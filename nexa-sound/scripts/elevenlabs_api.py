"""ElevenLabs API access shared by the nexa skills (nexa-sound, nexa-speech, nexa-video-creator).

Standard library only, Python 3.9 or newer. Each skill keeps an identical copy in its own scripts folder, so every
skill installs on its own; a repository test keeps the copies the same.

Keys
- Read from the environment: ELEVENLABS_API_KEY, then ELEVENLABS_API_KEY_1, _2 and so on. When none is set, the
  macOS keychain is asked for a generic password whose service name is ELEVENLABS_API_KEY.
- A key travels only in the xi-api-key header: never in a URL, a log line, a file or an error message.
- More than one key is for failover only (a revoked key). Credits and concurrency belong to the account, so a busy or
  exhausted account waits or stops; it never moves on to another key.

Test hooks (environment): NEXA_ELEVENLABS_BASE_URL points the calls at a fake server, NEXA_ELEVENLABS_SLEEP_SCALE
scales every wait (0 in tests), NEXA_NO_KEYCHAIN=1 skips the keychain.
"""
import json
import mimetypes
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

KEYCHAIN_SERVICE = "ELEVENLABS_API_KEY"

MISSING_KEY_HELP = (
    "No ElevenLabs API key found. Set ELEVENLABS_API_KEY in your shell, or store it once in the macOS keychain; "
    "`security` asks for the key at a prompt, so it stays out of your shell history:\n"
    "  security add-generic-password -a \"$USER\" -s ELEVENLABS_API_KEY -w\n"
    "Client work needs a paid plan: on the free plan ElevenLabs output is for non-commercial use with attribution."
)


def base_url():
    return os.environ.get("NEXA_ELEVENLABS_BASE_URL", "https://api.elevenlabs.io").rstrip("/")


class ElevenError(Exception):
    """A failed call. `kind` is one of: no_key, auth, permission, credits, busy, bad_request, blocked, too_large,
    server, network, timeout, empty, plan. `detail` is ElevenLabs' own status code when it sent one."""

    def __init__(self, kind, message, status=None, detail=None, retry_after=None):
        super().__init__(message)
        self.kind = kind
        self.status = status
        self.detail = detail
        self.retry_after = retry_after

    def as_dict(self):
        return {"kind": self.kind, "status": self.status, "detail": self.detail, "message": str(self)}


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
    main = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if main:
        found.append(("ELEVENLABS_API_KEY", main))
    for i in range(1, 21):
        name = "ELEVENLABS_API_KEY_%d" % i
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
    """Remove every known key, and anything shaped like an ElevenLabs key, from text meant for people."""
    text = str(text)
    for _, value in (pairs if pairs is not None else (_KEY_CACHE or [])):
        if value:
            text = text.replace(value, "***")
    return re.sub(r"\bsk_[0-9a-f]{32,}\b", "***", text)


# ---------------------------------------------------------------- HTTP

_REFUSED = set()


def _sleep(seconds):
    try:
        scale = float(os.environ.get("NEXA_ELEVENLABS_SLEEP_SCALE", "1"))
    except ValueError:
        scale = 1.0
    if seconds > 0 and scale > 0:
        time.sleep(seconds * scale)


def _short(text, limit=600):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit] + "..."


def _detail(body):
    """(status code word, message) from ElevenLabs' error JSON. Seen on the live API (2026-09-25):
    {"detail": {"status": "missing_permissions", "message": ...}}, {"detail": {"type": "validation_error", "code":
    "invalid_parameters", "status": "unsupported_target_language", "message", "request_id", "param"}} and FastAPI's
    {"detail": [{"loc": ["body", "audio"], "msg": "Field required"}]}."""
    try:
        data = json.loads(body or "{}")
    except ValueError:
        return None, body or ""
    det = data.get("detail") if isinstance(data, dict) else None
    if isinstance(det, dict):
        return det.get("status") or det.get("code") or det.get("type"), det.get("message") or json.dumps(det)
    if isinstance(det, list) and det:                    # FastAPI validation errors
        return "validation_error", "; ".join(
            ("%s: %s" % (".".join(str(x) for x in d.get("loc", [])[1:]), d.get("msg")) if d.get("loc") else
             str(d.get("msg", d))) if isinstance(d, dict) else str(d) for d in det)
    if isinstance(det, str):
        return None, det
    return None, body or ""


def classify(status, body):
    """Sort an HTTP error into a kind that decides what happens next."""
    code, message = _detail(body)
    code = (code or "").lower()
    low = (message or "").lower() + " " + code
    if code == "missing_permissions" or "missing the permission" in low:
        return "permission"        # a working key without this permission: turn it on in the key's settings
    if code in ("invalid_api_key", "missing_api_key", "api_key_not_found") or status == 401 and "key" in low \
            and "quota" not in low:
        return "auth"
    if code in ("quota_exceeded", "insufficient_credits", "credits_exhausted") or "quota" in low \
            or "credits" in low and ("exceed" in low or "insufficient" in low or "not enough" in low):
        return "credits"
    if code in ("too_many_concurrent_requests", "system_busy", "rate_limit_exceeded") or status == 429:
        return "busy"
    if code in ("payment_required", "subscription_required", "plan_limit", "feature_not_available",
                "watermark_not_allowed") or status == 402 or "upgrade" in low or "not available on your" in low \
            or "only available for" in low or "subscription" in low and status == 403:
        return "plan"
    if code in ("detected_unusual_activity", "content_policy_violation", "terms_of_service_violation") \
            or "policy" in low or "moderat" in low or "prohibited" in low or "blocked" in low:
        return "blocked"
    if status == 413 or "too large" in low or "file size" in low or "too long" in low:
        return "too_large"
    if status in (400, 404, 405, 409, 415, 422):
        return "bad_request"
    if status == 408 or (status is not None and status >= 500):
        return "server"
    if status == 403:
        return "auth"
    return "bad_request"


def _retry_after(headers):
    value = headers.get("Retry-After") if headers is not None else None
    try:
        return float(value) if value else None
    except (TypeError, ValueError):
        return None


def multipart(fields=None, files=None):
    """(body bytes, content type) for a multipart/form-data upload. files: {field: path or (filename, bytes, mime)}."""
    boundary = "----nexa%s" % uuid.uuid4().hex
    out = []
    for name, value in (fields or {}).items():
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        elif isinstance(value, bool):
            value = "true" if value else "false"
        out.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                    % (boundary, name, value)).encode("utf-8"))
    for name, item in (files or {}).items():
        if isinstance(item, (tuple, list)):
            filename, data, mime = item
        else:
            filename = os.path.basename(item)
            with open(item, "rb") as handle:
                data = handle.read()
            mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        out.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n"
                    % (boundary, name, filename.replace('"', ""), mime)).encode("utf-8"))
        out.append(data)
        out.append(b"\r\n")
    out.append(("--%s--\r\n" % boundary).encode("utf-8"))
    return b"".join(out), "multipart/form-data; boundary=" + boundary


def _open(url, method, data, headers, timeout):
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers


def request(method, path, body=None, query=None, fields=None, files=None, timeout=300, max_waits=3,
            accept="application/json"):
    """Call the ElevenLabs API and return (payload, info).

    payload is the parsed JSON when the answer is JSON, else the raw bytes (audio). info = {"key": the key's source
    name, "seconds", "attempts", "headers", "content_type"}. A refused key moves on to the next one. A busy account (too
    many concurrent requests, system busy, 429) or a server error waits on the same key (Retry-After, else 5, 15 and 45
    s) and tries again at most `max_waits` times. A timeout is never retried: the call may still be billed. Everything
    else raises ElevenError at once."""
    pairs = keys()
    if not pairs:
        raise ElevenError("no_key", MISSING_KEY_HELP)
    url = base_url() + path
    if query:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})
    if files or fields:
        data, ctype = multipart(fields, files)
    elif body is not None:
        data, ctype = json.dumps(body).encode("utf-8"), "application/json"
    else:
        data, ctype = None, None
    started = time.time()
    attempts, last = 0, None
    usable = [p for p in pairs if p[0] not in _REFUSED] or pairs
    for name, value in usable:
        waits = 0
        while True:
            attempts += 1
            hdrs = {"xi-api-key": value, "Accept": accept}
            if ctype:
                hdrs["Content-Type"] = ctype
            try:
                payload, resp_headers = _open(url, method, data, hdrs, timeout)
            except urllib.error.HTTPError as err:
                text = err.read().decode("utf-8", "replace")
                kind = classify(err.code, text)
                code, message = _detail(text)
                last = ElevenError(kind, scrub("HTTP %d from %s: %s" % (err.code, path.split("?")[0], _short(message)),
                                               pairs), status=err.code, detail=code,
                                   retry_after=_retry_after(err.headers))
                if kind == "auth":
                    _REFUSED.add(name)
                    break
                if kind in ("busy", "server") and waits < max_waits:
                    _sleep(last.retry_after if last.retry_after else 5 * (3 ** waits))
                    waits += 1
                    continue
                raise last
            except socket.timeout:
                raise ElevenError("timeout", "no answer from %s within %d s" % (path.split("?")[0], timeout))
            except urllib.error.URLError as err:
                if isinstance(err.reason, socket.timeout):
                    raise ElevenError("timeout", "no answer from %s within %d s" % (path.split("?")[0], timeout))
                last = ElevenError("network", scrub("network error calling %s: %s" % (path.split("?")[0], err.reason),
                                                    pairs))
                if waits < max_waits:
                    _sleep(5 * (waits + 1))
                    waits += 1
                    continue
                raise last
            headers = dict(resp_headers.items()) if resp_headers is not None else {}
            ctype_out = next((v for k, v in headers.items() if k.lower() == "content-type"), "")
            info = {"key": name, "seconds": round(time.time() - started, 2), "attempts": attempts,
                    "headers": headers, "content_type": ctype_out}
            if "json" in ctype_out.lower():
                try:
                    return json.loads(payload.decode("utf-8") or "{}"), info
                except ValueError:
                    raise ElevenError("server", "the answer from %s was not JSON" % path.split("?")[0])
            return payload, info
    raise last if last is not None else ElevenError("auth", "no key was accepted")


def header(info, name):
    """A response header by case-insensitive name, or None."""
    for k, v in (info.get("headers") or {}).items():
        if k.lower() == name.lower():
            return v
    return None


# ---------------------------------------------------------------- account

def subscription(timeout=60):
    """The account's plan and credits (a free call): {"tier", "credits_used", "credits_limit", "next_reset",
    "raw"}."""
    data, _ = request("GET", "/v1/user/subscription", timeout=timeout)
    data = data if isinstance(data, dict) else {}
    return {"tier": str(data.get("tier") or "").lower() or None,
            "credits_used": data.get("character_count"), "credits_limit": data.get("character_limit"),
            "next_reset": data.get("next_character_count_reset_unix"), "raw": data}


def paid_plan(sub):
    """True when the plan allows commercial use of the output (every plan except free)."""
    tier = (sub or {}).get("tier") or ""
    return bool(tier) and tier != "free"


def plan_status():
    """{"tier", "paid", "known", "credits_left", "note"}. Reading the plan needs the key's user_read permission; without
    it the plan is unknown, and output is treated as the free plan's (non-commercial) until the user says otherwise."""
    try:
        sub = subscription()
    except ElevenError as err:
        if err.kind == "permission":
            return {"tier": None, "paid": None, "known": False, "credits_left": None,
                    "note": "the key cannot read the plan (give the key User access in its permissions)"}
        raise
    used, limit = sub.get("credits_used"), sub.get("credits_limit")
    left = (limit - used) if isinstance(used, int) and isinstance(limit, int) else None
    return {"tier": sub.get("tier"), "paid": paid_plan(sub), "known": True, "credits_left": left, "note": None}


# ---------------------------------------------------------------- endpoints (fields checked on the live API, 2026-09-25)

SFX_MODELS = ("eleven_text_to_sound_v3", "eleven_text_to_sound_v2")
SFX_MIN_S, SFX_MAX_S = 0.5, 30.0
MUSIC_MIN_MS, MUSIC_MAX_MS = 3000, 600000
STT_MODELS = ("scribe_v2", "scribe_v1")
OUTPUT_FORMATS = ("mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128",
                  "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100",
                  "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96",
                  "opus_48000_128", "opus_48000_192")


def pcm_rate(output_format):
    """48000 for "pcm_48000", else None."""
    m = re.match(r"pcm_(\d+)$", output_format or "")
    return int(m.group(1)) if m else None


def sound_effect(text, duration=None, prompt_influence=None, loop=None, model_id=SFX_MODELS[0],
                 output_format="pcm_48000", timeout=300):
    """POST /v1/sound-generation. duration 0.5 to 30 s (None lets the model choose), prompt_influence 0 to 1, loop for
    a seamless loop, which only eleven_text_to_sound_v2 makes (so a loop always asks for v2). The answer's
    character-cost header says what it cost. Returns (audio bytes, info)."""
    if loop:
        model_id = "eleven_text_to_sound_v2"
    body = {"text": str(text)}
    if duration is not None:
        body["duration_seconds"] = round(max(SFX_MIN_S, min(SFX_MAX_S, float(duration))), 2)
    if prompt_influence is not None:
        body["prompt_influence"] = round(max(0.0, min(1.0, float(prompt_influence))), 2)
    if loop is not None:
        body["loop"] = bool(loop)
    if model_id:
        body["model_id"] = model_id
    return request("POST", "/v1/sound-generation", body=body, query={"output_format": output_format},
                   timeout=timeout, accept="*/*")


MUSIC_MODELS = ("music_v2_5", "music_v2")      # music_v1 is deprecated (OpenAPI, 2026-09-25)
MUSIC_MODES = ("track", "loop", "ambience", "video_to_music")
MUSIC_SECTION_MIN_MS, MUSIC_SECTION_MAX_MS = 3000, 120000
MUSIC_FORMATS_EXTRA = ("mp3_48000_128", "mp3_48000_192", "mp3_48000_240", "mp3_48000_320", "auto")


def music(prompt=None, composition_plan=None, length_ms=None, instrumental=True, model_id=None,
          output_format="pcm_48000", seed=None, respect_durations=None, c2pa=None, mode=None, timeout=900):
    """POST /v1/music: a prompt (with length_ms, 3 s to 10 min) or a composition plan
    {"positive_global_styles": [], "negative_global_styles": [], "sections": [{"section_name",
    "positive_local_styles": [], "negative_local_styles": [], "duration_ms": 3000 to 120000, "lines": []}]}.
    respect_durations keeps each section's length; c2pa signs the file with Content Credentials. Returns (audio
    bytes, info)."""
    body = {}
    if composition_plan is not None:
        body["composition_plan"] = composition_plan
        if respect_durations is not None:
            body["respect_sections_durations"] = bool(respect_durations)
    else:
        body["prompt"] = str(prompt or "")
        if length_ms is not None:
            body["music_length_ms"] = int(max(MUSIC_MIN_MS, min(MUSIC_MAX_MS, int(length_ms))))
        if instrumental is not None:
            body["force_instrumental"] = bool(instrumental)
        if mode:
            body["generation_mode"] = mode
    if model_id:
        body["model_id"] = model_id
    if seed is not None:
        body["seed"] = int(seed)
    if c2pa is not None and str(output_format).startswith("mp3"):     # C2PA signing applies to MP3 only
        body["sign_with_c2pa"] = bool(c2pa)
    return request("POST", "/v1/music", body=body, query={"output_format": output_format}, timeout=timeout,
                   accept="*/*")


def music_plan(prompt, length_ms, model_id=None, timeout=300):
    """POST /v1/music/plan: a composition plan (JSON) from a prompt, to edit before composing."""
    body = {"prompt": str(prompt), "music_length_ms": int(max(MUSIC_MIN_MS, min(MUSIC_MAX_MS, int(length_ms))))}
    if model_id:
        body["model_id"] = model_id
    plan, info = request("POST", "/v1/music/plan", body=body, timeout=timeout)
    return plan, info


def isolate(path, timeout=900):
    """POST /v1/audio-isolation (multipart field "audio"): the voice without the room. Returns (audio bytes, info)."""
    return request("POST", "/v1/audio-isolation", files={"audio": path}, timeout=timeout, accept="*/*")


def speech_to_text(path, model_id=STT_MODELS[0], language_code=None, diarize=False, num_speakers=None,
                   tag_audio_events=False, timestamps="word", timeout=1800):
    """POST /v1/speech-to-text (multipart field "file"): words with start and end in seconds."""
    fields = {"model_id": model_id, "timestamps_granularity": timestamps, "diarize": bool(diarize),
              "tag_audio_events": bool(tag_audio_events)}
    if language_code:
        fields["language_code"] = language_code
    if num_speakers:
        fields["num_speakers"] = int(num_speakers)
    return request("POST", "/v1/speech-to-text", fields=fields, files={"file": path}, timeout=timeout)


def forced_alignment(path, text, timeout=900):
    """POST /v1/forced-alignment (multipart fields "file" and "text"): the known script's words timed on the audio."""
    return request("POST", "/v1/forced-alignment", fields={"text": text}, files={"file": path}, timeout=timeout)


# ---------------------------------------------------------------- audio files

def audio_kind(data, output_format=""):
    """"wav", "mp3", "ogg" or "pcm" from the bytes, then the requested format."""
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if data[:3] == b"ID3" or data[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2", b"\xff\xe3"):
        return "mp3"
    if data[:4] == b"OggS":
        return "ogg"
    fmt = output_format or ""
    return "pcm" if fmt.startswith("pcm_") else ("mp3" if fmt.startswith("mp3_") else "bin")


def pcm_channels(n_bytes, rate, expect_s=None, content_type=""):
    """The channel count of raw 16-bit PCM: from the content type when it says so, else the count whose implied
    length is nearest the expected seconds, within 25 % (mono and stereo differ by 2x, so they never mix up; short
    effects come back a little short: 0.48 s for a 0.5 s click on the live API). None when it cannot be told."""
    m = re.search(r"channels=(\d+)", content_type or "")
    if m:
        return int(m.group(1))
    if expect_s and rate and float(expect_s) > 0:
        err = {c: abs(n_bytes / (2.0 * rate * c) - float(expect_s)) / float(expect_s) for c in (1, 2)}
        best = min(err, key=err.get)
        if err[best] <= 0.25:
            return best
    return None


def save_audio(data, stem, output_format, expect_s=None, info=None):
    """Write an answer next to `stem` and return (path, meta). Raw PCM gets a WAV header (16-bit, the requested
    rate, the channel count from the content type or the length); an MP3 or Ogg answer is written as it came."""
    import struct
    kind = audio_kind(data, output_format)
    meta = {"format": kind, "bytes": len(data)}
    if kind == "pcm":
        rate = pcm_rate(output_format) or 44100
        ctype = (info or {}).get("content_type") or ""
        ch = pcm_channels(len(data), rate, expect_s, ctype)
        if ch is None:
            raise ElevenError("empty", "cannot tell the channel count of %d bytes of %s PCM (expected %s s)"
                              % (len(data), output_format, expect_s))
        frames = len(data) // (2 * ch)
        data = data[:frames * 2 * ch]
        header = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt " + struct.pack(
            "<IHHIIHH", 16, 1, ch, rate, rate * ch * 2, ch * 2, 16) + b"data" + struct.pack("<I", len(data))
        data = header + data
        meta.update({"format": "wav", "from": output_format, "sample_rate": rate, "channels": ch,
                     "duration_s": round(frames / float(rate), 4)})
        path = stem + ".wav"
    else:
        path = stem + {"mp3": ".mp3", "ogg": ".ogg", "wav": ".wav"}.get(kind, ".bin")
    with open(path, "wb") as handle:
        handle.write(data)
    return path, meta


def cost_headers(info):
    """What ElevenLabs says about the call in its response headers: request id and any cost or credit counts."""
    out = {}
    for k, v in (info.get("headers") or {}).items():
        low = k.lower()
        if low in ("request-id", "x-request-id", "history-item-id", "song-id") or "cost" in low or "credit" in low \
                or "character" in low or "concurrent" in low:
            out[low] = v
    return out
