"""Pixabay API access shared by the nexa skills (stock photos, illustrations, vectors and videos).

Standard library only, Python 3.9 or newer. Each skill that uses it keeps an identical copy; a repository test keeps
the copies the same.

Keys
- Read from the environment (PIXABAY_API_KEY); when it is not set, the macOS keychain is asked for a generic password
  whose service name is PIXABAY_API_KEY.
- Pixabay takes the key as a URL parameter, so a URL is never shown, logged or stored with it: every message goes
  through scrub(), and the cache is keyed by the query without the key.

Pixabay's API rules, followed here
- Cache requests for 24 hours: answers are kept on disk and reused for a day.
- At most 100 requests a minute by default: the X-RateLimit headers are read, and a 429 waits for the reset.
- Download before use: preview and web-format links are temporary and must not be embedded; download() saves files.
- Show where results come from whenever search results are shown to people: every normalised hit keeps its Pixabay
  page and author, and the caller lists them.

Test hooks (environment): NEXA_PIXABAY_BASE_URL points the calls at a fake server, NEXA_PIXABAY_CACHE moves the
cache, NEXA_PIXABAY_SLEEP_SCALE scales every wait (0 in tests), NEXA_NO_KEYCHAIN=1 skips the keychain.
"""
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

KEYCHAIN_SERVICE = "PIXABAY_API_KEY"
CACHE_S = 24 * 3600
MISSING_KEY_HELP = (
    "No Pixabay API key found. Get one free at https://pixabay.com/api/docs/ (signed in), then set PIXABAY_API_KEY "
    "in your shell or store it once in the macOS keychain:\n"
    "  security add-generic-password -a \"$USER\" -s PIXABAY_API_KEY -w"
)
IMAGE_TYPES = ("photo", "illustration", "vector")
VIDEO_TYPES = ("film", "animation")
CATEGORIES = ("backgrounds", "fashion", "nature", "science", "education", "feelings", "health", "people", "religion",
              "places", "animals", "industry", "computer", "food", "sports", "transportation", "travel", "buildings",
              "business", "music")


def base_url():
    return os.environ.get("NEXA_PIXABAY_BASE_URL", "https://pixabay.com").rstrip("/")


class PixabayError(Exception):
    """A failed call. `kind` is one of: no_key, auth, rate, bad_request, server, network, timeout, download."""

    def __init__(self, kind, message, status=None):
        super().__init__(message)
        self.kind = kind
        self.status = status


# ---------------------------------------------------------------- keys

_KEY = None


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


def key(refresh=False):
    """(source name, key) or (None, None)."""
    global _KEY
    if _KEY is not None and not refresh:
        return _KEY
    value = os.environ.get("PIXABAY_API_KEY", "").strip()
    if value:
        _KEY = ("PIXABAY_API_KEY", value)
    else:
        value = _keychain(KEYCHAIN_SERVICE)
        _KEY = ("keychain:" + KEYCHAIN_SERVICE, value) if value else (None, None)
    return _KEY


def key_sources():
    name, _ = key()
    return [name] if name else []


def scrub(text):
    """Remove the key (and any key=... parameter) from text meant for people."""
    text = str(text)
    _, value = _KEY or (None, None)
    if value:
        text = text.replace(value, "***")
    return re.sub(r"([?&]key=)[^&\s\"']+", r"\1***", text)


# ---------------------------------------------------------------- cache

def cache_dir():
    root = os.environ.get("NEXA_PIXABAY_CACHE") or os.path.join(os.path.expanduser("~"), ".nexa-video-creator",
                                                                  "pixabay-cache")
    os.makedirs(root, exist_ok=True)
    return root


def _cache_path(endpoint, params):
    blob = json.dumps({"endpoint": endpoint, "params": params}, sort_keys=True)
    return os.path.join(cache_dir(), hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24] + ".json")


def _cache_get(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError):
        return None
    if time.time() - float(data.get("saved") or 0) > CACHE_S:
        return None
    return data.get("answer")


def _cache_put(path, params, answer):
    tmp = path + ".tmp%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump({"saved": time.time(), "query": params, "answer": answer}, handle)
    os.replace(tmp, path)


# ---------------------------------------------------------------- HTTP

def _sleep(seconds):
    try:
        scale = float(os.environ.get("NEXA_PIXABAY_SLEEP_SCALE", "1"))
    except ValueError:
        scale = 1.0
    if seconds > 0 and scale > 0:
        time.sleep(seconds * scale)


def _get(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "nexa-skills/1 (+https://github.com/developerjillur)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), dict(resp.headers.items())


def _classify(status, text):
    low = (text or "").lower()
    if "api key" in low or "api_key" in low or status in (401, 403):
        return "auth"
    if status == 429:
        return "rate"
    if status is not None and status >= 500:
        return "server"
    return "bad_request"


def search(kind, q, timeout=60, **params):
    """Search Pixabay. kind: "image" (photos, illustrations, vectors) or "video". Returns {"total", "totalHits",
    "hits": [raw hits], "cached": bool, "rate": {"limit", "remaining", "reset"} or None}.

    params are Pixabay's own (image_type, video_type, orientation, category, min_width, min_height, colors,
    editors_choice, safesearch, order, page, per_page, lang, id); None values are left out."""
    name, value = key()
    if not value:
        raise PixabayError("no_key", MISSING_KEY_HELP)
    if kind not in ("image", "video"):
        raise ValueError("kind must be image or video")
    q = " ".join(str(q or "").split())
    if len(q) > 100:
        raise PixabayError("bad_request", "the query is longer than Pixabay's 100 characters: %r" % q[:120])
    clean = {k: v for k, v in params.items() if v is not None}
    for k, v in list(clean.items()):
        if isinstance(v, bool):
            clean[k] = "true" if v else "false"
    clean["q"] = q
    endpoint = "/api/" if kind == "image" else "/api/videos/"
    cpath = _cache_path(endpoint, clean)
    hit = _cache_get(cpath)
    if hit is not None:
        return dict(hit, cached=True, rate=None)
    url = base_url() + endpoint + "?" + urllib.parse.urlencode(dict(clean, key=value))
    for attempt in range(3):
        try:
            raw, headers = _get(url, timeout)
        except urllib.error.HTTPError as err:
            text = err.read().decode("utf-8", "replace")[:300]
            kind_err = _classify(err.code, text)
            if kind_err == "rate" and attempt < 2:
                reset = err.headers.get("X-RateLimit-Reset") if err.headers is not None else None
                try:
                    wait = min(65.0, max(1.0, float(reset)))
                except (TypeError, ValueError):
                    wait = 30.0
                _sleep(wait)
                continue
            if kind_err == "server" and attempt < 2:
                _sleep(5 * (attempt + 1))
                continue
            raise PixabayError(kind_err, scrub("HTTP %d from Pixabay %s: %s" % (err.code, endpoint, " ".join(
                text.split()))), status=err.code)
        except socket.timeout:
            raise PixabayError("timeout", "no answer from Pixabay within %d s" % timeout)
        except urllib.error.URLError as err:
            if attempt < 2:
                _sleep(5 * (attempt + 1))
                continue
            raise PixabayError("network", scrub("network error calling Pixabay: %s" % err.reason))
        try:
            answer = json.loads(raw.decode("utf-8"))
        except ValueError:
            raise PixabayError("server", "Pixabay's answer was not JSON")
        _cache_put(cpath, clean, answer)
        rate = {k: headers.get("X-RateLimit-" + k.capitalize()) for k in ("limit", "remaining", "reset")}
        return dict(answer, cached=False, rate=rate)
    raise PixabayError("rate", "Pixabay kept answering 429 (too many requests); wait a minute")


# ---------------------------------------------------------------- hits

def _tags(hit):
    return [t.strip() for t in str(hit.get("tags") or "").split(",") if t.strip()]


def normalize(kind, hit):
    """One hit in the toolkit's own shape: the best file to download, its size, the preview, the page and author (for
    credits), and the tags."""
    base = {"id": hit.get("id"), "page_url": hit.get("pageURL"), "user": hit.get("user"),
            "user_id": hit.get("user_id"), "tags": _tags(hit), "views": hit.get("views"),
            "downloads": hit.get("downloads"), "likes": hit.get("likes"), "source": "pixabay"}
    if kind == "image":
        best = next((f for f in ("imageURL", "fullHDURL", "largeImageURL") if hit.get(f)), None)
        w, h = hit.get("imageWidth") or 0, hit.get("imageHeight") or 0
        if best == "largeImageURL" and w and h:          # scaled to at most 1280 px on the long side
            s = min(1.0, 1280.0 / max(w, h))
            dw, dh = int(round(w * s)), int(round(h * s))
        elif best == "fullHDURL" and w and h:
            s = min(1.0, 1920.0 / max(w, h))
            dw, dh = int(round(w * s)), int(round(h * s))
        else:
            dw, dh = w, h
        if hit.get("vectorURL"):
            base["vector_url"] = hit.get("vectorURL")
        base.update({"kind": hit.get("type") or "photo", "original_w": w, "original_h": h,
                     "download_url": hit.get(best) if best else None, "download_field": best,
                     "download_w": dw, "download_h": dh,
                     "preview_url": hit.get("webformatURL") or hit.get("previewURL"),
                     "preview_w": hit.get("webformatWidth") or hit.get("previewWidth"),
                     "preview_h": hit.get("webformatHeight") or hit.get("previewHeight")})
        return base
    vids = hit.get("videos") or {}
    renditions = {}
    for name in ("large", "medium", "small", "tiny"):
        r = vids.get(name) or {}
        if r.get("url"):
            renditions[name] = {"url": r.get("url"), "width": r.get("width") or 0, "height": r.get("height") or 0,
                                "size": r.get("size") or 0, "thumbnail": r.get("thumbnail")}
    order = sorted(renditions.items(), key=lambda kv: -(kv[1]["width"] * kv[1]["height"]))
    best_name, best = order[0] if order else (None, {})
    small = renditions.get("tiny") or renditions.get("small") or best
    thumb = next((r.get("thumbnail") for _, r in order if r.get("thumbnail")), None)
    base.update({"kind": hit.get("type") or "film", "duration": hit.get("duration"),
                 "download_url": best.get("url"), "download_field": best_name,
                 "download_w": best.get("width"), "download_h": best.get("height"), "download_size": best.get("size"),
                 "preview_url": small.get("url"), "preview_w": small.get("width"), "preview_h": small.get("height"),
                 "thumbnail_url": thumb, "renditions": renditions})
    return base


def covers(item, frame_w, frame_h, scale=1.0):
    """True when the download fills a frame of frame_w x frame_h at `scale` without enlarging past 100 %."""
    w, h = item.get("download_w") or 0, item.get("download_h") or 0
    if not w or not h:
        return False
    need = max(frame_w * scale / float(w), frame_h * scale / float(h))
    return need <= 1.0


# ---------------------------------------------------------------- downloads

def download(url, dest, max_bytes=2 * 1024 ** 3, timeout=600):
    """Save a Pixabay file (image or video rendition) to dest, atomically. Returns dest."""
    if not url:
        raise PixabayError("download", "no download link")
    tmp = dest + ".part%d" % os.getpid()
    req = urllib.request.Request(url, headers={"User-Agent": "nexa-skills/1 (+https://github.com/developerjillur)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp, open(tmp, "wb") as out:
            got = 0
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                got += len(chunk)
                if got > max_bytes:
                    raise PixabayError("download", "the file is larger than %d MB" % (max_bytes // 1024 ** 2))
                out.write(chunk)
    except urllib.error.HTTPError as err:
        _remove(tmp)
        raise PixabayError("download", scrub("HTTP %d downloading %s" % (err.code, url.split("?")[0])),
                           status=err.code)
    except (urllib.error.URLError, socket.timeout, OSError) as err:
        _remove(tmp)
        raise PixabayError("download", scrub("download failed: %s" % err))
    except PixabayError:
        _remove(tmp)
        raise
    os.replace(tmp, dest)
    return dest


def _remove(path):
    try:
        os.remove(path)
    except OSError:
        pass
