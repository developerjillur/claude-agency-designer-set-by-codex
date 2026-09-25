"""Gemini API access shared by the nexa skills (nexa-speech, nexa-sound, nexa-video-creator).

Standard library only, Python 3.9 or newer. Each skill keeps an identical copy in its own scripts folder, so every
skill installs on its own; a repository test keeps the copies the same.

Keys
- Read from the environment: GEMINI_API_KEY, then GEMINI_API_KEY_1, GEMINI_API_KEY_2 and so on. When none is set, the
  macOS keychain is asked for a generic password whose service name is GEMINI_API_KEY.
- A key is never printed, logged, written to a file or put in a URL, and every error message is scrubbed of keys
  before anyone sees it.
- More than one key is for failover only (a revoked key, a project without billing). Google counts rate limits per
  project and its terms forbid working around them, so a quota error waits on the same key and never moves on.

Test hooks (environment): NEXA_GEMINI_BASE_URL points the calls at a fake server, NEXA_GEMINI_SLEEP_SCALE scales
every wait (0 in tests), NEXA_NO_KEYCHAIN=1 skips the keychain.
"""
import base64
import io
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave

API_VERSION = "v1beta"
KEYCHAIN_SERVICE = "GEMINI_API_KEY"
INLINE_AUDIO_LIMIT = 14 * 1024 * 1024  # raw bytes; base64 adds a third and a request must stay under 20 MB

MISSING_KEY_HELP = (
    "No Gemini API key found. Set GEMINI_API_KEY in your shell (GEMINI_API_KEY_1, _2 and so on add failover keys), "
    "or store it once in the macOS keychain; `security` asks for the key at a prompt, so it stays out of your shell "
    "history:\n"
    "  security add-generic-password -a \"$USER\" -s GEMINI_API_KEY -w\n"
    "Use a key from a Google Cloud project with billing turned on: on the free tier Google may use what you send "
    "to improve its products, and some models (Lyria 3.5) have no free tier at all."
)


def base_url():
    return os.environ.get("NEXA_GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")


class GeminiError(Exception):
    """A failed call. `kind` is one of: no_key, auth, billing, quota_day, quota_minute, bad_request, safety, server,
    network, timeout, empty."""

    def __init__(self, kind, message, status=None, retry_after=None):
        super().__init__(message)
        self.kind = kind
        self.status = status
        self.retry_after = retry_after

    def as_dict(self):
        return {"kind": self.kind, "status": self.status, "message": str(self)}


# ---------------------------------------------------------------- keys

_KEY_CACHE = None


def _keychain(service):
    if sys.platform != "darwin" or os.environ.get("NEXA_NO_KEYCHAIN"):
        return None
    try:
        out = subprocess.run(["security", "find-generic-password", "-s", service, "-w"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    value = out.stdout.strip()
    return value if out.returncode == 0 and value else None


def keys(refresh=False):
    """[(source, key)] in failover order. The source names are safe to show; the keys are not."""
    global _KEY_CACHE
    if _KEY_CACHE is not None and not refresh:
        return list(_KEY_CACHE)
    found = []
    main = os.environ.get("GEMINI_API_KEY", "").strip()
    if main:
        found.append(("GEMINI_API_KEY", main))
    for i in range(1, 51):
        name = "GEMINI_API_KEY_%d" % i
        value = os.environ.get(name, "").strip()
        if value:
            found.append((name, value))
    if not found:
        value = _keychain(KEYCHAIN_SERVICE)
        if value:
            found.append(("keychain:" + KEYCHAIN_SERVICE, value))
    seen, unique = set(), []
    for name, value in found:
        if value not in seen:
            seen.add(value)
            unique.append((name, value))
    _KEY_CACHE = unique
    return list(unique)


def key_sources():
    """Where the keys come from, for doctor output: names only, never values."""
    return [name for name, _ in keys()]


def scrub(text, pairs=None):
    """Remove every known key, and anything shaped like a Google API key, from text meant for people."""
    text = str(text)
    for _, value in (pairs if pairs is not None else (_KEY_CACHE or [])):
        if value:
            text = text.replace(value, "***")
    return re.sub(r"AIza[0-9A-Za-z_\-]{20,}", "***", text)


# ---------------------------------------------------------------- HTTP

_REFUSED = set()  # key sources refused (auth or billing) in this process; tried again only when none is left


def _sleep(seconds):
    try:
        scale = float(os.environ.get("NEXA_GEMINI_SLEEP_SCALE", "1"))
    except ValueError:
        scale = 1.0
    if seconds > 0 and scale > 0:
        time.sleep(seconds * scale)


def _short(text, limit=600):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit] + "..."


def classify(status, body):
    """Sort an HTTP error into a kind that decides what happens next."""
    low = (body or "").lower()
    if status == 401 or "api_key_invalid" in low or "api key not valid" in low or "api key expired" in low:
        return "auth"
    if status == 403:
        if "billing" in low or "free tier" in low or "free_tier" in low:
            return "billing"
        return "auth"
    if status == 429:
        if "free_tier" in low or "limit: 0" in low or "billing" in low:
            return "billing"
        if "perday" in low or "per day" in low or "per_day" in low:
            return "quota_day"
        return "quota_minute"
    if status == 400:
        if "billing" in low or "free tier" in low or "not available on the free" in low:
            return "billing"
        if any(word in low for word in ("safety", "blocked", "prohibited", "recitation", "copyright", "harmful")):
            return "safety"
        return "bad_request"
    if status == 408 or (status is not None and status >= 500):
        return "server"
    return "bad_request"


def _retry_after(body, headers):
    match = re.search(r'"retryDelay"\s*:\s*"(\d+(?:\.\d+)?)s"', body or "")
    if match:
        return float(match.group(1))
    value = headers.get("Retry-After") if headers is not None else None
    try:
        return float(value) if value else None
    except (TypeError, ValueError):
        return None


def _open(url, method, data, headers, timeout):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers


def request(method, path, body=None, timeout=600, headers=None, raw=None, max_waits=3):
    """Call the Gemini API and return (parsed JSON, info).

    info = {"key": the key's source name, "seconds": wall time, "attempts": calls made, "headers": response headers}.
    Auth and billing errors move on to the next key. A per-minute quota error or a server error waits on the same key
    (the server's retryDelay, or 15, 30 and 60 s) and tries again, at most `max_waits` times. A timeout is never
    retried, because the model may still be working and a second call would be paid again. Everything else raises
    GeminiError at once: a bad request, a safety block and a daily quota only get worse when repeated.
    """
    pairs = keys()
    if not pairs:
        raise GeminiError("no_key", MISSING_KEY_HELP)
    url = path if path.startswith("http") else base_url() + path
    data = raw if raw is not None else (json.dumps(body).encode("utf-8") if body is not None else None)
    started = time.time()
    attempts = 0
    last = None
    usable = [pair for pair in pairs if pair[0] not in _REFUSED] or pairs
    for name, value in usable:
        waits = 0
        while True:
            attempts += 1
            hdrs = {"x-goog-api-key": value}
            if raw is None and body is not None:
                hdrs["Content-Type"] = "application/json"
            hdrs.update(headers or {})
            try:
                payload, resp_headers = _open(url, method, data, hdrs, timeout)
            except urllib.error.HTTPError as err:
                text = err.read().decode("utf-8", "replace")
                kind = classify(err.code, text)
                last = GeminiError(kind, scrub("HTTP %d from %s: %s" % (err.code, path.split("?")[0], _short(text)),
                                               pairs),
                                   status=err.code, retry_after=_retry_after(text, err.headers))
                if kind in ("auth", "billing"):
                    _REFUSED.add(name)
                    break
                if kind in ("quota_minute", "server") and waits < max_waits:
                    _sleep(last.retry_after if last.retry_after else 15 * (2 ** waits))
                    waits += 1
                    continue
                raise last
            except socket.timeout:
                raise GeminiError("timeout", "no answer from %s within %d s" % (path.split("?")[0], timeout))
            except urllib.error.URLError as err:
                if isinstance(err.reason, socket.timeout):
                    raise GeminiError("timeout", "no answer from %s within %d s" % (path.split("?")[0], timeout))
                last = GeminiError("network", scrub("network error calling %s: %s" % (path.split("?")[0], err.reason),
                                                    pairs))
                if waits < max_waits:
                    _sleep(10 * (waits + 1))
                    waits += 1
                    continue
                raise last
            text = payload.decode("utf-8", "replace") if payload else ""
            try:
                parsed = json.loads(text) if text.strip() else {}
            except ValueError:
                raise GeminiError("server", "the answer from %s was not JSON: %s" % (path.split("?")[0], _short(text)))
            return parsed, {"key": name, "seconds": round(time.time() - started, 2), "attempts": attempts,
                            "headers": dict(resp_headers.items()) if resp_headers is not None else {}}
    raise last if last is not None else GeminiError("auth", "no key was accepted")


def interactions(body, timeout=600):
    """POST /v1beta/interactions: speech, music and transcription all use it."""
    return request("POST", "/%s/interactions" % API_VERSION, body, timeout=timeout)


def list_models(timeout=60):
    """Model ids the key's project can see (a free call)."""
    names, token = [], None
    for _ in range(20):
        path = "/%s/models?pageSize=1000" % API_VERSION + ("&pageToken=" + token if token else "")
        resp, _ = request("GET", path, timeout=timeout)
        for model in resp.get("models") or []:
            name = str(model.get("name") or "")
            names.append(name.split("/", 1)[1] if name.startswith("models/") else name)
        token = resp.get("nextPageToken")
        if not token:
            break
    return names


# ---------------------------------------------------------------- responses

def _steps(resp):
    steps = resp.get("steps")
    if isinstance(steps, list):
        return [s for s in steps if isinstance(s, dict) and s.get("type") != "user_input"]
    outputs = resp.get("outputs")
    if isinstance(outputs, list):
        return [{"type": "model_output", "content": outputs}]
    candidates = resp.get("candidates")
    if isinstance(candidates, list) and candidates:
        parts = ((candidates[0] or {}).get("content") or {}).get("parts") or []
        content = []
        for part in parts:
            inline = part.get("inlineData") or part.get("inline_data")
            if inline:
                content.append({"type": "audio", "data": inline.get("data"),
                                "mime_type": inline.get("mimeType") or inline.get("mime_type")})
            elif "text" in part:
                content.append({"type": "text", "text": part.get("text")})
        return [{"type": "model_output", "content": content}]
    return []


def blocks(resp, kind):
    """Every output content block of one type ("audio", "text"), in order."""
    found = []
    for step in _steps(resp):
        for block in step.get("content") or []:
            if isinstance(block, dict) and block.get("type") == kind:
                found.append(block)
    return found


def _rate_from_mime(mime):
    match = re.search(r"rate=(\d+)", mime or "")
    return int(match.group(1)) if match else None


def audio_parts(resp):
    """[{"bytes", "mime_type", "sample_rate", "channels"}] for every audio block."""
    parts = []
    for block in blocks(resp, "audio"):
        data = block.get("data")
        if not data:
            continue
        mime = str(block.get("mime_type") or block.get("mimeType") or "")
        parts.append({"bytes": base64.b64decode(data), "mime_type": mime,
                      "sample_rate": block.get("sample_rate") or _rate_from_mime(mime),
                      "channels": block.get("channels")})
    return parts


def text_parts(resp):
    return [str(block.get("text")) for block in blocks(resp, "text") if block.get("text")]


def parse_offset(value):
    """'1.250s' -> 1.25 (also takes numbers and {'seconds', 'nanos'})."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return float(value.get("seconds") or 0) + float(value.get("nanos") or 0) / 1e9
    text = str(value).strip()
    if text.endswith("s"):
        text = text[:-1]
    try:
        return float(text)
    except ValueError:
        return None


def word_infos(resp):
    """Word timings from a transcription: [{"text", "start", "end", "speaker"}]."""
    words = []
    for block in blocks(resp, "text"):
        for note in block.get("annotations") or []:
            if isinstance(note, dict) and note.get("type") == "word_info":
                words.append({"text": note.get("text") or "", "start": parse_offset(note.get("start_offset")),
                              "end": parse_offset(note.get("end_offset")), "speaker": note.get("speaker")})
    return words


def status(resp):
    """What the server says about how the answer ended: {"status", "finish_reason"} (either may be None)."""
    finish = None
    candidates = resp.get("candidates")
    if isinstance(candidates, list) and candidates:
        finish = (candidates[0] or {}).get("finishReason")
    for step in _steps(resp):
        finish = step.get("finish_reason") or step.get("finishReason") or finish
    return {"status": resp.get("status"), "finish_reason": finish}


def usage(resp):
    return resp.get("usage") or resp.get("usageMetadata") or {}


# ---------------------------------------------------------------- audio files

def is_riff(data):
    return data[:4] == b"RIFF" and data[8:12] == b"WAVE"


def audio_extension(data, mime=""):
    mime = (mime or "").lower()
    if is_riff(data):
        return ".wav"
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2") or "mp3" in mime or "mpeg" in mime:
        return ".mp3"
    if data[:4] == b"OggS" or "ogg" in mime:
        return ".ogg"
    return ".pcm"


def pcm_to_wav(pcm, rate=24000, channels=1, width=2):
    """Wrap raw little-endian PCM in a WAV header. Gemini's audio/L16 is little-endian, whatever the name says."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as out:
        out.setnchannels(channels)
        out.setsampwidth(width)
        out.setframerate(rate)
        out.writeframes(pcm)
    return buf.getvalue()


def save_audio(part, stem, default_rate=24000, default_channels=1):
    """Write one audio part next to `stem` and return the path. A WAV (RIFF) answer is written as it came, never
    wrapped again (a WAV inside a WAV clicks and reports the wrong length); raw PCM gets a header; MP3 and Ogg stay
    as they are."""
    data = part["bytes"]
    ext = audio_extension(data, part.get("mime_type"))
    if ext == ".pcm":
        data = pcm_to_wav(data, int(part.get("sample_rate") or default_rate),
                          int(part.get("channels") or default_channels))
        ext = ".wav"
    path = stem + ext
    with open(path, "wb") as handle:
        handle.write(data)
    return path


MIME_BY_EXT = {".wav": "audio/wav", ".mp3": "audio/mp3", ".m4a": "audio/mp4", ".aac": "audio/aac",
               ".flac": "audio/flac", ".ogg": "audio/ogg", ".opus": "audio/ogg", ".aiff": "audio/aiff",
               ".mp4": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm"}


def mime_for(path):
    return MIME_BY_EXT.get(os.path.splitext(path)[1].lower(), "application/octet-stream")


# ---------------------------------------------------------------- files and transcription

def upload_file(path, mime_type=None, display_name=None, timeout=900):
    """Upload through the Files API (resumable, two calls) and return the file resource ({"name", "uri", ...}).
    Files expire on Google's side after 48 hours; delete_file() removes one sooner."""
    mime_type = mime_type or mime_for(path)
    size = os.path.getsize(path)
    pairs = keys()
    if not pairs:
        raise GeminiError("no_key", MISSING_KEY_HELP)
    start_url = base_url() + "/upload/%s/files" % API_VERSION
    meta = json.dumps({"file": {"display_name": display_name or os.path.basename(path)}}).encode("utf-8")
    last = None
    for name, value in pairs:
        try:
            _, resp_headers = _open(start_url, "POST", meta, {
                "x-goog-api-key": value, "Content-Type": "application/json",
                "X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                "X-Goog-Upload-Header-Content-Length": str(size),
                "X-Goog-Upload-Header-Content-Type": mime_type}, 60)
        except urllib.error.HTTPError as err:
            text = err.read().decode("utf-8", "replace")
            last = GeminiError(classify(err.code, text), scrub("upload start failed: HTTP %d %s" % (err.code,
                                                                                               _short(text)), pairs),
                               status=err.code)
            if last.kind in ("auth", "billing"):
                continue
            raise last
        except (urllib.error.URLError, socket.timeout) as err:
            raise GeminiError("network", scrub("upload start failed: %s" % err, pairs))
        upload_url = None
        for header, header_value in resp_headers.items():
            if header.lower() == "x-goog-upload-url":
                upload_url = header_value
        if not upload_url:
            raise GeminiError("server", "the Files API gave no upload URL")
        with open(path, "rb") as handle:
            data = handle.read()
        try:
            payload, _ = _open(upload_url, "POST", data, {
                "Content-Length": str(size), "X-Goog-Upload-Offset": "0",
                "X-Goog-Upload-Command": "upload, finalize"}, timeout)
        except urllib.error.HTTPError as err:
            text = err.read().decode("utf-8", "replace")
            raise GeminiError(classify(err.code, text), scrub("upload failed: HTTP %d %s" % (err.code, _short(text)),
                                                              pairs), status=err.code)
        except (urllib.error.URLError, socket.timeout) as err:
            raise GeminiError("network", scrub("upload failed: %s" % err, pairs))
        resource = json.loads(payload.decode("utf-8")).get("file") or {}
        for _ in range(60):
            if resource.get("state") in (None, "ACTIVE"):
                return resource
            if resource.get("state") == "FAILED":
                raise GeminiError("server", "the Files API could not process %s" % os.path.basename(path))
            _sleep(2)
            resource, _ = request("GET", "/%s/%s" % (API_VERSION, resource["name"]), timeout=60)
        raise GeminiError("timeout", "the uploaded file never became ACTIVE")
    raise last if last is not None else GeminiError("auth", "no key was accepted")


def delete_file(name):
    try:
        request("DELETE", "/%s/%s" % (API_VERSION, name), timeout=60, max_waits=0)
    except GeminiError:
        pass


def transcribe(path, language_codes=None, words=True, speakers=False, mode="verbatim", vocabulary=None,
               model="gemini-3.5-transcribe", timeout=900):
    """Transcribe an audio or video file with Gemini 3.5 Transcribe.

    Returns {"text", "words": [{"text", "start", "end", "speaker"}], "usage", "info"}. Word timings and speaker
    labels work up to 30 minutes a call (1 hour without them); custom vocabulary cannot be combined with either, so it
    is dropped when they are asked for. Leave `language_codes` empty for code-switched speech (Bangla with English):
    the model then detects and switches languages by itself. Small files go inline; larger ones, or a model that
    refuses inline audio, go through the Files API, and the uploaded copy is deleted afterwards.
    """
    config = {"mode": {"type": mode}}
    if words:
        config["mode"]["timestamp_granularities"] = ["word"]
    if speakers:
        config["mode"]["diarization_mode"] = "speaker"
    if language_codes:
        config["language_codes"] = list(language_codes)
    if vocabulary and not (words or speakers):
        config["custom_vocabulary"] = list(vocabulary)[:1000]
    mime = mime_for(path)

    def call(block):
        body = {"model": model, "input": [block], "store": False,
                "generation_config": {"transcription_config": config}}
        return interactions(body, timeout=timeout)

    uploaded = None
    try:
        if os.path.getsize(path) <= INLINE_AUDIO_LIMIT:
            with open(path, "rb") as handle:
                block = {"type": "audio", "mime_type": mime, "data": base64.b64encode(handle.read()).decode("ascii")}
            try:
                resp, info = call(block)
            except GeminiError as err:
                if err.kind != "bad_request":
                    raise
                uploaded = upload_file(path, mime)
                resp, info = call({"type": "audio", "mime_type": mime, "uri": uploaded["uri"]})
        else:
            uploaded = upload_file(path, mime)
            resp, info = call({"type": "audio", "mime_type": mime, "uri": uploaded["uri"]})
    finally:
        if uploaded and uploaded.get("name"):
            delete_file(uploaded["name"])
    return {"text": "".join(text_parts(resp)), "words": word_infos(resp), "usage": usage(resp), "info": info,
            "status": status(resp)}
