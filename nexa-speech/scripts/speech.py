#!/usr/bin/env python3
"""nexa-speech: voice-overs and character voices with Gemini text-to-speech, with one voice and one delivery from the
first second of a video to the last.

  speech.py doctor [--live]                           keys (names only), ffmpeg and its filters, the cache
  speech.py voices [--gender f|m] [--find WORD]        the 30 prebuilt voices (--library: Google's voice library)
  speech.py presets                                   the 15 presets
  speech.py profile new NAME --preset ID | show NAME | list
  speech.py design --desc TEXT --gender G --lang L --out DIR, then: design keep VOICE_ID --profile NAME
  speech.py audition --voices A,B,C --text FILE --profile NAME --out DIR
  speech.py plan SCRIPT --profile NAME [--out DIR]     free dry run: chunks, seconds, requests, tokens, USD
  speech.py render SCRIPT --profile NAME --out DIR     synthesise what is not cached, gates, one re-roll, ledger
  speech.py pick DIR CHUNK TAKE                        choose a take by hand
  speech.py say "TEXT" --profile NAME --out FILE       one line, cached and mastered
  speech.py qa DIR [--asr]                            run the gates again, write qa.json
  speech.py master DIR                                vo_48k.wav and vo.manifest.json
  speech.py align DIR [--engine auto|gemini|elevenlabs|pauses]   words.json, sentences.json, vo.srt, vo.vtt
  speech.py fit DIR --scenes FILE [--ad] [--apply]     fit scenes to target lengths
  speech.py cost [DIR] [--minutes 10] [--model M]      an estimate, or the actual numbers from ledger.jsonl

render, say, design, audition, voices --library, qa --asr, align --engine gemini and doctor --live reach the Gemini
API, align --engine elevenlabs reaches ElevenLabs; everything else is offline and free. Every command prints a short
summary, or one JSON object with --json.
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import datetime as dt
import difflib
import hashlib
import io
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import threading
import time
import unicodedata
import wave
from array import array
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemini_api as G  # noqa: E402  (shared by the nexa skills: never edit it here)
import elevenlabs_api as EL  # noqa: E402  (shared by the nexa skills: never edit it here)

SKILL_VERSION = "2026.09.25.5"
PRICES_AS_OF = "2026-09-25"
ANALYSIS_VERSION = "2026.09.25.1"   # bump when what analyse_audio() returns changes
SCRIPTS = Path(__file__).resolve().parent

# ------------------------------------------------------------------------------------------------ models and money

DEFAULT_MODEL = "gemini-3.8-flash-tts"
# USD per 1M tokens, dated: (last day the price holds, or None for "from then on", price). Source: the Gemini API
# pricing page, fetched 2026-09-25.
MODELS = {
    "gemini-3.8-flash-tts": {"family": "speech_metadata", "status": "GA",
                             "audio": [("2026-12-31", 9.00), (None, 18.00)],
                             "text": [("2026-12-31", 0.50), (None, 1.00)]},
    "gemini-3.8-flash-lite-tts": {"family": "speech_metadata", "status": "GA",
                                  "audio": [("2026-12-31", 6.00), (None, 12.00)],
                                  "text": [("2026-12-31", 0.50), (None, 1.00)]},
    "gemini-3.1-flash-tts-preview": {"family": "director_text", "status": "legacy preview",
                                     "audio": [(None, 20.00)], "text": [(None, 1.00)]},
    "gemini-2.5-flash-preview-tts": {"family": "director_text", "status": "legacy preview",
                                     "audio": [(None, 10.00)], "text": [(None, 0.50)]},
    "gemini-2.5-pro-preview-tts": {"family": "director_text", "status": "legacy preview",
                                   "audio": [(None, 20.00)], "text": [(None, 1.00)]},
}
AUDIO_TOKENS_PER_S = 32          # audio output tokens per second of speech (usage on the live API, 2026-09-25)
TEXT_CHARS_PER_TOKEN = 3.0       # a rough count for the text input line, which is under 1% of the bill
BATCH_FACTOR = 0.5               # batch and flex cost half (shown for reference; this tool renders interactively)
BILL_FACTOR = 1.2                # a public test (2026-09-23) was billed 1.5x the arithmetic at 25 tokens a second;
                                 # 32 a second (measured) explains 1.28x of that, so about 1.2x is left
RETAKE_FACTOR = 1.4              # typical extra takes
TRANSCRIBE_MODEL = "gemini-3.5-transcribe"
TRANSCRIBE_USD_PER_MIN = 0.003 + 0.002   # audio in plus text out, per minute of audio
DESIGN_SAMPLE_S = 10.0           # voice design has no separate price in the research: estimated as 10 s of audio
DEFAULT_BUDGET = 1.00
MAX_PARALLEL = 3
TTS_TIMEOUT = 300
SAFETY_REASONS = {"SAFETY", "RECITATION", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "LANGUAGE"}
OK_REASONS = {"", "STOP", "FINISH_REASON_STOP", "COMPLETED", "END_TURN"}
OK_STATUS = {"", "COMPLETED", "SUCCEEDED", "DONE"}
STOP_KINDS = {"no_key", "auth", "billing", "quota_day", "quota_minute", "bad_request"}

# ------------------------------------------------------------------------------------------------ profile defaults

PROFILE_SCHEMA = "nexa-speech/profile-1"
DIRECTOR_HEAD = "Synthesize speech for the performance defined below. Speak ONLY the lines under #### TRANSCRIPT."
DEFAULT_TAGS = ["<short pause>", "<long pause>", "<breath>"]
KNOWN_TAGS = {
    "breath", "heavy breath", "exhales", "sigh", "sighs", "laugh", "laughter", "chuckle", "chuckles", "giggle", "gasp",
    "cough", "throat-clearing", "tsk", "phew", "pff", "yawn", "sob", "cry", "whimper", "shout", "scream", "shriek",
    "groan", "growl", "grunt", "hiss", "moan", "pant", "snort", "snicker", "sneeze", "cheer", "cackle", "argh", "grr",
    "whispers", "whispering", "short pause", "long pause"}
DEFAULT_GAPS = {"sentence": 320, "paragraph": 750, "scene": 1100, "min": 180, "max": 900}
DEFAULT_CHUNK = {"max_s": 45, "target_s": [12, 35], "max_words": 110, "max_chars_bn": 1488}
DEFAULT_LOUDNESS = {"stem_I": -16.0, "TP": -1.5, "LRA": 11.0}
DEFAULT_POST = {"highpass_hz": 70, "deess": 0, "room_tone": "pink", "room_tone_dbfs": -65.0}
DEFAULT_TAKES = {"default": 1, "hero": 3, "max_auto_reroll": 1}
BN_MAX_WORDS = 124               # Bangla ceiling per request, measured in an earlier production pipeline
PAUSE_SHARE = 0.10               # starting guess: share of a chunk spent in pauses of 150 ms or more
GATE2_WINDOW = (0.80, 1.25)      # voiced time against the words at the measured pace
GATE2_WINDOW_PRESET = (0.65, 1.50)   # against a preset's guess: on the live API (2026-09-25) 3.8 Flash TTS spoke
                                     # 2 to 39 % faster than the presets in English and Bangla, and every chunk
                                     # was complete; whole missing sentences still fall under 0.65
INNER_PAUSE_S = 0.35             # estimate of the pause between two sentences inside one request
TAG_SECONDS = {"short pause": 0.25, "long pause": 1.0}
OTHER_TAG_S = 0.4
LEAD_S, TAIL_S, FADE_IN_S, FADE_OUT_S = 0.060, 0.150, 0.008, 0.040
CANVAS_RATE = 24000
RESAMPLE_48K = "aresample=48000:filter_size=64:phase_shift=10:cutoff=0.97"
FRAGMENT_WORDS = 6
EXPIRY_WARN_DAYS = 30
CENTROID_SD_FLOOR = 0.05         # drift: the centroid spread is taken as at least 5% of the mean

REQUIRED_FILTERS = ("silencedetect", "ebur128", "astats", "aspectralstats", "asetnsamples", "ametadata", "loudnorm",
                    "alimiter", "acompressor", "highpass", "equalizer", "aresample", "afade", "atrim", "asetpts",
                    "volume", "amix", "anoisesrc", "atempo", "aformat")

_LOCK = threading.Lock()
_FILE_LOCK = threading.Lock()


class ToolError(RuntimeError):
    """A local step failed (ffmpeg, a file, a bad input): shown to the user as it is."""


# ------------------------------------------------------------------------------------------------ basics

def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def log(msg: str) -> None:
    with _LOCK:
        print(f"[nexa-speech {time.strftime('%H:%M:%S')}] {G.scrub(msg)}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"nexa-speech: {G.scrub(msg)}", file=sys.stderr)
    sys.exit(code)


def emit(args, obj: dict, lines: list, code: int = 0) -> None:
    """The command's answer: one JSON object with --json, else the short plain summary. `code` is the exit code."""
    if getattr(args, "json", False):
        print(G.scrub(json.dumps(obj, ensure_ascii=False, indent=1)))
    else:
        print(G.scrub("\n".join(str(x) for x in lines)))
    sys.stdout.flush()
    if code:
        sys.exit(code)


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return dt.date.today().isoformat()


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha16(obj) -> str:
    text = obj if isinstance(obj, str) else canon(obj)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()[:16]


def read_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except ValueError as err:
        raise ToolError(f"{path} is not valid JSON ({err})")


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


def append_jsonl(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _FILE_LOCK:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list:
    out = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        continue
    except FileNotFoundError:
        pass
    return out


def own_file(path: Path, schema_prefix: str) -> bool:
    """True when `path` is missing or is a JSON file this tool wrote (so it may be replaced)."""
    if not path.exists():
        return True
    try:
        data = read_json(path)
    except ToolError:
        return False
    return isinstance(data, dict) and str(data.get("schema", "")).startswith(schema_prefix)


def link_or_copy(src: Path, dst: Path) -> None:
    """A hard link when both sit on one disk, else a copy. Never replaces a file that is already there."""
    if dst.exists():
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def home() -> Path:
    return Path(os.environ.get("NEXA_SPEECH_HOME") or (Path.home() / ".nexa-speech")).expanduser()


def cache_dir() -> Path:
    return home() / "cache"


def fmt_s(sec) -> str:
    if sec is None:
        return "?"
    sec = float(sec)
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


def usd(x) -> str:
    return f"${x:.3f}" if x < 10 else f"${x:.2f}"


def median(xs):
    xs = [x for x in xs if isinstance(x, (int, float)) and not math.isnan(x)]
    return statistics.median(xs) if xs else None


def rnd(x, n=3):
    return None if x is None else round(float(x), n)


# ------------------------------------------------------------------------------------------------ ffmpeg

_FILTERS = None


def ffmpeg_bin() -> str:
    path = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if not path:
        die("ffmpeg is missing: install it (macOS: brew install ffmpeg), then run this again")
    return path


def run_cmd(cmd: list, timeout: float = 900, check: bool = True, binary: bool = False):
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, timeout=timeout, stdin=subprocess.DEVNULL,
                           **({} if binary else {"text": True, "errors": "replace"}))
    except subprocess.TimeoutExpired:
        raise ToolError(f"{Path(str(cmd[0])).name} timed out after {timeout:.0f} s")
    except FileNotFoundError:
        raise ToolError(f"not found: {cmd[0]}")
    if check and r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace") if binary else (r.stderr or r.stdout or "")
        raise ToolError(f"{Path(str(cmd[0])).name} failed: {err.strip()[-800:]}")
    return r


def ff(args: list, timeout: float = 900, check: bool = True, binary: bool = False):
    return run_cmd([ffmpeg_bin(), "-hide_banner", "-nostdin", "-nostats", *args], timeout, check, binary)


def ffmpeg_filters() -> set:
    global _FILTERS
    if _FILTERS is None:
        r = run_cmd([ffmpeg_bin(), "-hide_banner", "-filters"], 60, check=False)
        names = set()
        for line in (r.stdout or "").splitlines():
            parts = line.split()
            if len(parts) >= 3 and re.fullmatch(r"[TSCA.|]{2,4}", parts[0]):
                names.add(parts[1])
        _FILTERS = names
    return _FILTERS


def need_filters(extra: tuple = ()) -> None:
    missing = [f for f in (*REQUIRED_FILTERS, *extra) if f not in ffmpeg_filters()]
    if missing:
        die(f"this ffmpeg lacks the filters {', '.join(missing)}: install a full build (macOS: brew install ffmpeg)")


def read_wav(path: Path) -> tuple:
    """(sample rate, 16-bit mono samples as array('h')). Anything but 16-bit mono PCM goes through ffmpeg at 24 kHz."""
    try:
        with wave.open(str(path), "rb") as w:
            if w.getsampwidth() == 2 and w.getnchannels() == 1 and w.getcomptype() == "NONE":
                data = w.readframes(w.getnframes())
                a = array("h")
                a.frombytes(data[: len(data) // 2 * 2])
                if sys.byteorder == "big":
                    a.byteswap()
                return w.getframerate(), a
    except (wave.Error, EOFError):
        pass
    r = ff(["-v", "error", "-i", path, "-ac", "1", "-ar", "24000", "-f", "s16le", "-acodec", "pcm_s16le", "-"],
           binary=True)
    a = array("h")
    a.frombytes(r.stdout[: len(r.stdout) // 2 * 2])
    if sys.byteorder == "big":
        a.byteswap()
    return 24000, a


def read_f32(path: Path) -> array:
    a = array("f")
    with open(path, "rb") as fh:
        data = fh.read()
    a.frombytes(data[: len(data) // 4 * 4])
    if sys.byteorder == "big":
        a.byteswap()
    return a


def write_f32(path: Path, a: array) -> None:
    b = array("f", a)
    if sys.byteorder == "big":
        b.byteswap()
    with open(path, "wb") as fh:
        fh.write(b.tobytes())


def probe_duration(path: Path):
    r = run_cmd([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                 "default=nw=1:nk=1", str(path)], 60, check=False)
    try:
        return float((r.stdout or "").strip())
    except ValueError:
        return None


def loudness(path_args: list) -> dict:
    """ebur128 of an input (true peak on): {"I", "LRA", "TP"}."""
    r = ff(["-v", "info", *path_args, "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"], check=False)
    err = r.stderr or ""
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else err

    def grab(rx):
        m = re.search(rx, summ)
        if not m:
            return None
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return {"I": grab(r"I:\s*(-?[0-9.]+|-inf)\s*LUFS"), "LRA": grab(r"LRA:\s*(-?[0-9.]+)\s*LU"),
            "TP": grab(r"Peak:\s*(-?[0-9.]+|-inf)\s*dBFS")}


def silences(path_args: list, noise_db: float, min_s: float) -> list:
    """Pauses in an input: [(start, end)] from ffmpeg silencedetect."""
    r = ff(["-v", "info", *path_args, "-af", f"silencedetect=noise={noise_db:.1f}dB:d={min_s}", "-f", "null", "-"],
           check=False)
    err = r.stderr or ""
    starts = [float(x) for x in re.findall(r"silence_start:\s*(-?[0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", err)]
    out = []
    for i, s in enumerate(starts):
        e = ends[i] if i < len(ends) else None
        out.append((max(0.0, s), e))
    return out


# ------------------------------------------------------------------------------------------------ data files

_DATA = {}


def data(name: str) -> dict:
    if name not in _DATA:
        path = SCRIPTS / name
        got = read_json(path)
        if not got:
            die(f"{path} is missing: reinstall the skill")
        _DATA[name] = got
    return _DATA[name]


def prebuilt_voice(name: str):
    for v in data("voices.json")["voices"]:
        if v["name"].lower() == (name or "").lower():
            return v
    return None


def preset_by_id(pid: str):
    for p in data("presets.json")["presets"]:
        if p["id"] == pid:
            return p
    return None


# ------------------------------------------------------------------------------------------------ prices

def price_per_m(model: str, kind: str, day: str = None) -> float:
    table = MODELS[model][kind]
    day = day or today()
    for until, value in table:
        if until is None or day <= until:
            return value
    return table[-1][1]


def text_tokens(text: str) -> int:
    return int(math.ceil(len(text or "") / TEXT_CHARS_PER_TOKEN))


def tts_usd(model: str, audio_s: float, tokens_in: int, day: str = None) -> float:
    return (audio_s * AUDIO_TOKENS_PER_S / 1e6 * price_per_m(model, "audio", day)
            + tokens_in / 1e6 * price_per_m(model, "text", day))


def asr_usd(seconds: float) -> float:
    return seconds / 60.0 * TRANSCRIBE_USD_PER_MIN


# ------------------------------------------------------------------------------------------------ profiles

NAME_RX = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class ProfileError(Exception):
    pass


def profiles_dir(args) -> Path:
    given = getattr(args, "profiles", None)
    return Path(given).expanduser().resolve() if given else home() / "profiles"


def voice_key(voice: dict) -> str:
    """How the voice enters the cache key: a prebuilt name, or id@expire_time for a designed or replicated voice."""
    vid = str((voice or {}).get("id") or "")
    if (voice or {}).get("type") in ("designed", "replicated") and voice.get("expire_time"):
        return f"{vid}@{voice['expire_time']}"
    return vid


def lexicon_file(p: dict, pdir: Path):
    name = p.get("lexicon")
    if not name:
        return None
    path = Path(str(name)).expanduser()
    return path if path.is_absolute() else (pdir / path)


def identity(p: dict, pdir: Path) -> dict:
    lex = lexicon_file(p, pdir)
    lex_sha = (file_sha(lex) if lex.exists() else "missing") if lex else None
    return {"model": p.get("model"), "voice": voice_key(p.get("voice") or {}), "style": p.get("style") or "",
            "modes": p.get("modes") or {}, "lexicon": lex_sha, "prompt_family": p.get("prompt_family"),
            "send_language_code": bool(p.get("send_language_code"))}


def _merge_defaults(p: dict) -> dict:
    for key, default in (("gaps_ms", DEFAULT_GAPS), ("chunk", DEFAULT_CHUNK), ("loudness", DEFAULT_LOUDNESS),
                         ("post", DEFAULT_POST), ("takes", DEFAULT_TAKES)):
        merged = dict(default)
        merged.update(p.get(key) or {})
        p[key] = merged
    p.setdefault("modes", {})
    p.setdefault("tags_allowed", list(DEFAULT_TAGS))
    p.setdefault("numbers", "words")
    p.setdefault("send_language_code", False)
    p.setdefault("language", "en-US")
    p.setdefault("style", "")
    p.setdefault("engine", "gemini-api")
    wpm = {"target": 150, "min": 140, "max": 160, "measured_wps": None}
    wpm.update(p.get("wpm") or {})
    p["wpm"] = wpm
    return p


def new_profile(name: str, preset: dict, pdir: Path, voice: str = None, style: str = None, model: str = None,
                lang: str = None, modes: dict = None, lexicon: str = None) -> dict:
    model = model or DEFAULT_MODEL
    family = MODELS[model]["family"]
    if style is None:
        style = preset["style"]
        if family == "director_text" and preset.get("director_accent"):
            style = f"{style}. {preset['director_accent']}"
    vid, vtype = preset["voice"], "prebuilt"
    if voice:
        pv = prebuilt_voice(voice)
        if pv:
            vid = pv["name"]
        elif voice.startswith("voicekey_"):
            vid, vtype = voice, "replicated"
        elif re.search(r"[_/0-9]", voice):
            vid, vtype = voice, "library"     # a library or designed id; `design keep` records a designed one
        else:
            raise ProfileError(f"unknown voice {voice}: pick one of `voices`, an id from `voices --library`, or a "
                               "designed voice (design, then design keep)")
    wmin, wmax = preset["wpm"]
    now = now_iso()
    all_modes = dict(preset.get("modes") or {})
    all_modes.update(modes or {})
    p = {"schema": PROFILE_SCHEMA, "name": name, "version": 1, "preset": preset["id"], "engine": "gemini-api",
         "model": model, "prompt_family": family,
         "voice": {"id": vid, "type": vtype, "expire_time": None, "sample": None},
         "language": lang or preset["language"], "send_language_code": False, "style": style, "modes": all_modes,
         "tags_allowed": list(DEFAULT_TAGS),
         "wpm": {"target": int(round((wmin + wmax) / 2)), "min": wmin, "max": wmax, "measured_wps": None},
         "gaps_ms": dict(DEFAULT_GAPS), "chunk": json.loads(json.dumps(DEFAULT_CHUNK)), "numbers": "words",
         "lexicon": lexicon, "loudness": dict(DEFAULT_LOUDNESS), "post": dict(DEFAULT_POST),
         "takes": dict(DEFAULT_TAKES), "precise": bool(preset.get("precise")),
         "design_prompt": preset.get("design_prompt"), "created": now, "updated": now,
         "history": [{"version": 1, "time": now, "change": f"created from preset {preset['id']}"}]}
    p["identity"] = identity(p, pdir)
    return p


def validate_profile(p: dict) -> None:
    model = p.get("model")
    if model not in MODELS:
        raise ProfileError(f"profile {p.get('name')}: unknown model {model}; known: {', '.join(MODELS)}")
    family = MODELS[model]["family"]
    if p.get("prompt_family") != family:
        raise ProfileError(f"profile {p.get('name')}: {model} needs prompt_family {family}, "
                           f"not {p.get('prompt_family')}")
    if not (p.get("voice") or {}).get("id"):
        raise ProfileError(f"profile {p.get('name')}: no voice id")
    if p.get("numbers") not in ("words", "keep"):
        raise ProfileError(f"profile {p.get('name')}: numbers must be words or keep")
    for tag in p.get("tags_allowed") or []:
        if not re.fullmatch(r"<[a-z][a-z \-]*>", str(tag)):
            raise ProfileError(f"profile {p.get('name')}: tags_allowed entries look like <short pause>, not {tag}")


def save_profile(p: dict, pdir: Path, change: str = None) -> dict:
    """Write a profile; a change to model, voice, style, modes or lexicon bumps its version (that changes cache keys
    through the text and style anyway; the version is what the manifest shows)."""
    ident = identity(p, pdir)
    old = p.get("identity")
    if old is not None and old != ident:
        changed = [k for k in ident if old.get(k) != ident[k]]
        p["version"] = int(p.get("version") or 1) + 1
        p.setdefault("history", []).append({"version": p["version"], "time": now_iso(),
                                            "change": change or ("changed: " + ", ".join(changed))})
        log(f"profile {p['name']}: {', '.join(changed)} changed, now version {p['version']}")
    p["identity"] = ident
    p["updated"] = now_iso()
    write_json(pdir / f"{p['name']}.json", p)
    return p


def load_profile(name: str, pdir: Path) -> dict:
    if not NAME_RX.match(name or ""):
        raise ProfileError(f"{name!r} is not a profile name (letters, digits, dot, dash, underscore)")
    path = pdir / f"{name}.json"
    if not path.exists():
        raise ProfileError(f"no profile {name} in {pdir}; make one with: profile new {name} --preset ID")
    try:
        p = read_json(path)
    except ToolError as err:
        raise ProfileError(str(err))
    if not isinstance(p, dict) or p.get("schema") != PROFILE_SCHEMA:
        raise ProfileError(f"{path} is not a nexa-speech profile")
    p["name"] = name
    _merge_defaults(p)
    validate_profile(p)
    if p.get("identity") != identity(p, pdir):
        save_profile(p, pdir, None if p.get("identity") else "identity recorded")
    return p


def voice_days_left(p: dict):
    exp = (p.get("voice") or {}).get("expire_time")
    if not exp:
        return None
    try:
        when = dt.datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=dt.timezone.utc)
    return (when - dt.datetime.now(dt.timezone.utc)).total_seconds() / 86400.0


def load_lexicon(p: dict, pdir: Path) -> list:
    path = lexicon_file(p, pdir)
    if not path:
        return []
    if not path.exists():
        raise ProfileError(f"profile {p['name']}: lexicon {path} is missing")
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" not in line:
            raise ProfileError(f"{path}:{n}: a lexicon line is display<TAB>spoken")
        display, spoken = line.split("\t", 1)
        display, spoken = nfc(display.strip()), nfc(spoken.strip())
        if display and spoken:
            out.append((display, spoken))
    return out


# ------------------------------------------------------------------------------------------------ text: basics

BN_LETTER_RX = re.compile(r"[\u0985-\u09B9\u09CE\u09DC-\u09DF]")
BN_DIGITS = "\u09e6\u09e7\u09e8\u09e9\u09ea\u09eb\u09ec\u09ed\u09ee\u09ef"
DIGIT_FOLD = str.maketrans(BN_DIGITS, "0123456789")
INVISIBLE_RX = re.compile("[\u200b\u200e\u200f\u202a-\u202e\u2060\u2066-\u2069\ufeff]")
TAG_RX = re.compile(r"<([a-z][a-z \-]{0,30})>")
INLINE_RX = re.compile(r"\{([^{}|]*)\|([^{}]*)\}|\{([^{}|]+)\}")
VIRAMA = "\u09cd"


def is_bn(text: str) -> bool:
    return bool(BN_LETTER_RX.search(text or ""))


def _bn_consonant(ch: str) -> bool:
    return "\u0995" <= ch <= "\u09b9" or ch in "\u09ce\u09dc\u09dd\u09df"


def graphemes(text: str) -> int:
    """User-perceived characters: combining marks, joiners and virama conjuncts join the one before (close to the
    Unicode rules for Bengali, without a library)."""
    n, prev = 0, ""
    for ch in text or "":
        joins = (unicodedata.category(ch) in ("Mn", "Mc", "Me") or ch in "\u200c\u200d"
                 or (prev == VIRAMA and _bn_consonant(ch)))
        if not joins:
            n += 1
        prev = ch
    return n


def clean_text(text: str) -> str:
    return INVISIBLE_RX.sub("", nfc(text.replace("\r\n", "\n").replace("\r", "\n")))


# ------------------------------------------------------------------------------------------------ numbers: English

EN_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
           "seventeen eighteen nineteen").split()
EN_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
EN_SCALES = [(10 ** 12, "trillion"), (10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")]
EN_ORD = {"one": "first", "two": "second", "three": "third", "five": "fifth", "eight": "eighth", "nine": "ninth",
          "twelve": "twelfth"}
CURRENCY = {"$": ("dollar", "dollars", "cent", "cents"), "\u00a3": ("pound", "pounds", "penny", "pence"),
            "\u20ac": ("euro", "euros", "cent", "cents"), "\u09f3": ("taka", "taka", "poisha", "poisha")}
SCALE_ABBR = {"k": "thousand", "m": "million", "bn": "billion"}


def en_int(n: int) -> str:
    if n < 0:
        return "minus " + en_int(-n)
    if n < 20:
        return EN_ONES[n]
    if n < 100:
        return EN_TENS[n // 10] + ("-" + EN_ONES[n % 10] if n % 10 else "")
    if n < 1000:
        return EN_ONES[n // 100] + " hundred" + (" " + en_int(n % 100) if n % 100 else "")
    for size, name in EN_SCALES:
        if n >= size:
            head, rest = divmod(n, size)
            return en_int(head) + " " + name + (" " + en_int(rest) if rest else "")
    return str(n)


def en_digits(s: str) -> str:
    return " ".join(EN_ONES[int(c)] for c in s if c.isdigit())


def en_ordinal(n: int) -> str:
    words = en_int(n)
    m = re.match(r"^(.*?)([a-z]+)$", words)
    head, last = m.group(1), m.group(2)
    if last in EN_ORD:
        last = EN_ORD[last]
    elif last.endswith("y"):
        last = last[:-1] + "ieth"
    else:
        last += "th"
    return head + last


def en_year(n: int) -> str:
    """1971 nineteen seventy-one, 2005 two thousand five, 2026 twenty twenty-six, 1900 nineteen hundred."""
    if 2000 <= n <= 2009:
        return "two thousand" + (" " + EN_ONES[n - 2000] if n > 2000 else "")
    hi, lo = divmod(n, 100)
    if lo == 0:
        return en_int(hi) + " hundred"
    if lo < 10:
        return en_int(hi) + " oh " + EN_ONES[lo]
    return en_int(hi) + " " + en_int(lo)


def en_num_text(s: str) -> str:
    """'1,250,000' -> words; '3.5' three point five; '007' zero zero seven."""
    s = s.replace(",", "")
    whole, _, frac = s.partition(".")
    if len(whole) > 1 and whole.startswith("0") and not frac:
        return en_digits(whole)
    if len(whole) > 15:
        return en_digits(whole) + (" point " + en_digits(frac) if frac else "")
    words = en_int(int(whole or "0"))
    return words + (" point " + en_digits(frac) if frac else "")


def _plural(words: str) -> str:
    head, _, last = words.rpartition(" ")
    last = last[:-1] + "ies" if last.endswith("y") else last + ("es" if last.endswith(("x", "s")) else "s")
    return (head + " " if head else "") + last


def en_money(sym: str, amount: str, scale: str = None) -> str:
    one, many, sub_one, sub_many = CURRENCY[sym]
    num = amount.replace(",", "")
    if scale:
        return f"{en_num_text(num)} {scale} {many}"
    if "." in num:
        whole, frac = num.split(".", 1)
        if len(frac) == 2:
            iv, fv = int(whole or "0"), int(frac)
            parts = []
            if iv:
                parts.append(f"{en_int(iv)} {one if iv == 1 else many}")
            if fv:
                parts.append(f"{en_int(fv)} {sub_one if fv == 1 else sub_many}")
            return " ".join(parts) if parts else f"zero {many}"
        return f"{en_num_text(num)} {many}"
    iv = int(num or "0")
    return f"{en_int(iv)} {one if iv == 1 else many}"


EN_NUM = r"\d(?:\d|,(?=\d))*(?:\.\d+)?"
EN_RX = re.compile(
    r"(?P<money>(?<![\w.])(?P<cur>[$\u00a3\u20ac\u09f3])\s?(?P<amt>" + EN_NUM + r")"
    r"(?:\s(?P<scale>thousand|million|billion|trillion)\b|(?P<abbr>k|m|bn)\b)?)"
    r"|(?P<pct>(?<![\w.])(?P<pnum>-?" + EN_NUM + r")\s?%)"
    r"|(?P<time>(?<![\w:.])(?P<hh>[01]?\d|2[0-3]):(?P<mm>[0-5]\d)(?![\d:])(?:\s?(?P<ampm>[ap])\.?\s?m\b\.?)?)"
    r"|(?P<ord>(?<![\w.])(?P<onum>\d{1,9})(?:st|nd|rd|th)\b)"
    r"|(?P<dec>(?<![\w.,])(?P<decade>1[1-9]\d0|20\d0)s\b)"
    r"|(?P<range>(?<![\w.,])(?P<ra>\d{1,4})\s?\u2013\s?(?P<rb>\d{1,4})(?![\w]|[.,]\d))"
    r"|(?P<year>(?<![\w.,\-])(?P<y>1[1-9]\d\d|20\d\d)(?![\w]|[.,]\d))"
    r"|(?P<neg>(?<![\w.\-])-(?P<nnum>" + EN_NUM + r")(?![\w]|\.\d))"
    r"|(?P<num>(?<![\w.])(?P<n>" + EN_NUM + r")(?![\w]|\.\d))",
    re.I)


def _en_range_side(s: str) -> str:
    n = int(s)
    return en_year(n) if 1100 <= n <= 2099 and len(s) == 4 else en_int(n)


def en_number_match(m) -> str:
    g = m.groupdict()
    if g["money"]:
        scale = g["scale"] or SCALE_ABBR.get((g["abbr"] or "").lower())
        return en_money(g["cur"], g["amt"], scale.lower() if scale else None)
    if g["pct"]:
        neg = g["pnum"].startswith("-")
        return ("minus " if neg else "") + en_num_text(g["pnum"].lstrip("-")) + " percent"
    if g["time"]:
        hh, mm = int(g["hh"]), int(g["mm"])
        words = en_int(hh) + (" o'clock" if mm == 0 else (" oh " + EN_ONES[mm] if mm < 10 else " " + en_int(mm)))
        if g["ampm"]:
            words += " a.m." if g["ampm"].lower() == "a" else " p.m."
        return words
    if g["ord"]:
        return en_ordinal(int(g["onum"]))
    if g["dec"]:
        return _plural(en_year(int(g["decade"])))
    if g["range"]:
        return _en_range_side(g["ra"]) + " to " + _en_range_side(g["rb"])
    if g["year"]:
        return en_year(int(g["y"]))
    if g["neg"]:
        return "minus " + en_num_text(g["nnum"])
    return en_num_text(g["n"])


# ------------------------------------------------------------------------------------------------ numbers: Bangla

# Bangla words for 0 to 99, exactly as given in the build spec (a native reader checks this list before release).
BN_0_99 = nfc(
    "শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয় "  # 0 to 9
    "দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ "  # 10 to 19
    "বিশ একুশ বাইশ তেইশ চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ ঊনত্রিশ "  # 20 to 29
    "ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ ঊনচল্লিশ "  # 30 to 39
    "চল্লিশ একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ ঊনপঞ্চাশ "  # 40 to 49
    "পঞ্চাশ একান্ন বাহান্ন তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন ঊনষাট "  # 50 to 59
    "ষাট একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি আটষট্টি ঊনসত্তর "  # 60 to 69
    "সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর ঊনআশি "  # 70 to 79
    "আশি একাশি বিরাশি তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি আটাশি ঊননব্বই "  # 80 to 89
    "নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই সাতানব্বই আটানব্বই নিরানব্বই"  # 90 to 99
).split()
BN_HUNDRED = nfc("শো")
BN_TAKA, BN_PERCENT, BN_POINT = nfc("টাকা"), nfc("শতাংশ"), nfc("দশমিক")
BN_THOUSAND, BN_LAKH, BN_CRORE = nfc("হাজার"), nfc("লাখ"), nfc("কোটি")
BN_OCLOCK, BN_MINUTE = nfc("টা"), nfc("মিনিট")
BN_ORDINALS = {1: (nfc("ম"), nfc("প্রথম")), 2: (nfc("য়"), nfc("দ্বিতীয়")), 3: (nfc("য়"), nfc("তৃতীয়")),
               4: (nfc("র্থ"), nfc("চতুর্থ")), 5: (nfc("ম"), nfc("পঞ্চম")), 6: (nfc("ষ্ঠ"), nfc("ষষ্ঠ")),
               7: (nfc("ম"), nfc("সপ্তম")), 8: (nfc("ম"), nfc("অষ্টম")), 9: (nfc("ম"), nfc("নবম")),
               10: (nfc("ম"), nfc("দশম"))}
BN_ABBREV_SPOKEN = {nfc("খ্রি."): nfc("খ্রিস্টাব্দ"), nfc("হি."): nfc("হিজরি")}


def bn_int(n: int) -> str:
    """Bangla words with the lakh and crore system: 150000 এক লাখ পঞ্চাশ হাজার."""
    if n < 100:
        return BN_0_99[n]
    parts = []
    crore, rest = divmod(n, 10 ** 7)
    if crore:
        parts.append(bn_int(crore) + " " + BN_CRORE)
    lakh, rest = divmod(rest, 10 ** 5)
    if lakh:
        parts.append(BN_0_99[lakh] + " " + BN_LAKH)
    thousand, rest = divmod(rest, 1000)
    if thousand:
        parts.append(BN_0_99[thousand] + " " + BN_THOUSAND)
    hundred, rest = divmod(rest, 100)
    if hundred:
        parts.append(BN_0_99[hundred] + BN_HUNDRED)
    if rest:
        parts.append(BN_0_99[rest])
    return " ".join(parts)


def bn_year(n: int) -> str:
    """1971 before সাল: উনিশশো একাত্তর."""
    hi, lo = divmod(n, 100)
    return BN_0_99[hi] + BN_HUNDRED + ((" " + BN_0_99[lo]) if lo else "")


def bn_digits(s: str) -> str:
    return " ".join(BN_0_99[int(c)] for c in s if c.isdigit())


def bn_num_text(s: str) -> str:
    s = s.translate(DIGIT_FOLD).replace(",", "")
    whole, _, frac = s.partition(".")
    if len(whole) > 1 and whole.startswith("0") and not frac:
        return bn_digits(whole)
    if len(whole) > 15:
        return bn_digits(whole)
    words = bn_int(int(whole or "0"))
    return words + ((" " + BN_POINT + " " + bn_digits(frac)) if frac else "")


BN_D = "[0-9\u09e6-\u09ef]"
BN_NUM = BN_D + r"(?:" + BN_D + r"|,(?=" + BN_D + r"))*(?:\." + BN_D + r"+)?"
BN_RX = re.compile(nfc(
    r"(?P<taka1>(?:\u09f3|Tk\.?)\s?(?P<t1>" + BN_NUM + r"))"
    r"|(?P<taka2>(?<!" + BN_D + r")(?P<t2>" + BN_NUM + r")\s?\u09f3)"
    r"|(?P<pct>(?<!" + BN_D + r")(?P<pnum>" + BN_NUM + r")\s?%)"
    r"|(?P<time>(?<!" + BN_D + r")(?P<hh>" + BN_D + r"{1,2}):(?P<mm>" + BN_D + r"{2})(?!" + BN_D + r"))"
    r"|(?P<ord>(?<!" + BN_D + r")(?P<onum>10|\u09e7\u09e6|" + BN_D + r")(?P<osuf>ম|য়|র্থ|ষ্ঠ))"
    r"|(?P<year>(?<!" + BN_D + r")(?P<y>" + BN_D + r"{4})(?=\s?(?:সাল|খ্রিস্টাব্দ)))"
    r"|(?P<num>(?<!" + BN_D + r")(?P<n>" + BN_NUM + r")(?![A-Za-z]))"))


def bn_number_match(m) -> str:
    g = m.groupdict()
    if g["taka1"] or g["taka2"]:
        return bn_num_text(g["t1"] or g["t2"]) + " " + BN_TAKA
    if g["pct"]:
        return bn_num_text(g["pnum"]) + " " + BN_PERCENT
    if g["time"]:
        hh, mm = int(g["hh"].translate(DIGIT_FOLD)), int(g["mm"].translate(DIGIT_FOLD))
        return BN_0_99[hh] + BN_OCLOCK + ((" " + BN_0_99[mm] + " " + BN_MINUTE) if mm else "")
    if g["ord"]:
        n = int(g["onum"].translate(DIGIT_FOLD))
        suffix, word = BN_ORDINALS.get(n, ("", ""))
        if suffix and nfc(g["osuf"]) == suffix:
            return word
        return bn_int(n) + g["osuf"]
    if g["year"]:
        n = int(g["y"].translate(DIGIT_FOLD))
        return bn_year(n) if 1100 <= n <= 1999 else bn_int(n)
    return bn_num_text(g["n"])


# ------------------------------------------------------------------------------------------------ text: segments

def seg(display: str, spoken: str, kind: str = "text") -> dict:
    return {"d": display, "s": spoken, "k": kind}


def replace_in_text(segs: list, rx, fn, kind: str) -> list:
    """Replace matches of `rx` inside the plain-text segments with fixed segments: fn(match) -> (display, spoken), or
    None to leave that match as it is. Fixed segments are never touched again."""
    out = []
    for sg in segs:
        if sg["k"] != "text":
            out.append(sg)
            continue
        text, pos = sg["d"], 0
        for m in rx.finditer(text):
            got = fn(m)
            if got is None:
                continue
            if m.start() > pos:
                out.append(seg(text[pos:m.start()], text[pos:m.start()]))
            out.append(seg(got[0], got[1], kind))
            pos = m.end()
        if pos < len(text):
            out.append(seg(text[pos:], text[pos:]))
    return out


def lexicon_rx(lexicon: list):
    """Two whole-word patterns: all-caps entries (acronyms) match case-sensitively, the rest ignore case."""
    if not lexicon:
        return None, None, {}
    word = r"[\w\u0980-\u09ff]"
    table = {}
    cs, ci = [], []
    for display, spoken in sorted(lexicon, key=lambda x: -len(x[0])):
        table[display] = spoken
        table.setdefault(display.lower(), spoken)
        (cs if display.isupper() else ci).append(re.escape(display))

    def build(items, flags):
        if not items:
            return None
        return re.compile(r"(?<!" + word + r")(?:" + "|".join(items) + r")(?!" + word + r")", flags)
    return build(cs, 0), build(ci, re.I), table


def normalise(raw: str, family: str, lexicon: list, numbers: str, lex_rx=None) -> dict:
    """One sentence -> {"segs", "display", "spoken", "tags", "terms"}: what the captions show and what the voice
    says, kept side by side."""
    segs = [seg(raw, raw)]
    tags = []

    def tag_fn(m):
        name = m.group(1).strip()
        tags.append(name)
        return ("", f"<{name}>" if family == "speech_metadata" else f"[{name}]")
    segs = replace_in_text(segs, TAG_RX, tag_fn, "tag")

    def inline_fn(m):
        if m.group(3) is not None:
            return (m.group(3), m.group(3))
        return (m.group(1), m.group(2))
    segs = replace_in_text(segs, INLINE_RX, inline_fn, "inline")
    terms = []
    cs_rx, ci_rx, table = lex_rx if lex_rx is not None else lexicon_rx(lexicon)

    def lex_fn(m):
        spoken = table.get(m.group(0)) or table.get(m.group(0).lower())
        if spoken is None:
            return None
        terms.append([m.group(0), spoken])
        return (m.group(0), spoken)
    if cs_rx is not None:
        segs = replace_in_text(segs, cs_rx, lex_fn, "lexicon")
    if ci_rx is not None:
        segs = replace_in_text(segs, ci_rx, lex_fn, "lexicon")
    bn = is_bn(raw)
    if bn:
        for short, full in BN_ABBREV_SPOKEN.items():
            segs = replace_in_text(segs, re.compile(re.escape(short)), lambda m, f=full: (m.group(0), f), "abbrev")
    if numbers == "words":
        if bn:
            segs = replace_in_text(segs, BN_RX, lambda m: (m.group(0), bn_number_match(m)), "number")
        else:
            segs = replace_in_text(segs, re.compile(BN_NUM.replace("0-9", "")), lambda m: (m.group(0), bn_num_text(
                m.group(0))) if re.search("[\u09e6-\u09ef]", m.group(0)) else None, "number")
            segs = replace_in_text(segs, EN_RX, lambda m: (m.group(0), en_number_match(m)), "number")
    display = " ".join("".join(s["d"] for s in segs).split())
    spoken = " ".join("".join(s["s"] for s in segs).split())
    return {"segs": segs, "display": display, "spoken": spoken, "tags": tags, "terms": terms}


PUNCT_ONLY_RX = re.compile(r"^[\W_]+$")


def word_map(segs: list) -> list:
    """Display words with the spoken text each one stands for: [{"w", "sp"}]. Captions show `w`; timing weighs `sp`."""
    words = []
    cur_d, cur_s = "", ""

    def push():
        nonlocal cur_d, cur_s
        if cur_d.strip() or cur_s.strip():
            words.append({"w": cur_d.strip(), "sp": " ".join(cur_s.split())})
        cur_d, cur_s = "", ""
    for sg in segs:
        if sg["k"] == "tag":
            continue
        if sg["k"] == "text":
            for ch in sg["d"]:
                if ch.isspace():
                    push()
                else:
                    cur_d += ch
                    cur_s += ch
            continue
        dwords = sg["d"].split()
        swords = sg["s"].split()
        if not dwords:
            cur_s += " " + sg["s"] + " "
            continue
        if len(dwords) == 1:
            cur_d += dwords[0]
            cur_s += sg["s"].strip()
            continue
        per = max(1, int(math.ceil(len(swords) / len(dwords))))
        for i, dw in enumerate(dwords):
            part = swords[i * per:(i + 1) * per] if i < len(dwords) - 1 else swords[i * per:]
            cur_d += dw
            cur_s += " " + " ".join(part) + " "
            if i < len(dwords) - 1:
                push()
    push()
    merged = []
    for w in words:
        if not w["w"]:
            if merged:
                merged[-1]["sp"] = (merged[-1]["sp"] + " " + w["sp"]).strip()
            continue
        if merged and PUNCT_ONLY_RX.match(w["w"]):
            merged[-1]["w"] += " " + w["w"]
            merged[-1]["sp"] = (merged[-1]["sp"] + " " + w["sp"]).strip()
            continue
        merged.append(w)
    return merged


def spoken_words(text: str) -> list:
    """The words the voice says (tags and bare punctuation are not words)."""
    text = TAG_RX.sub(" ", text or "")
    text = re.sub(r"\[[a-z][a-z \-]*\]", " ", text)
    return [w for w in text.split() if re.search(r"[\w\u0980-\u09ff]", w)]


# ------------------------------------------------------------------------------------------------ text: warnings

ENGLISH_OK = set("""video videos youtube facebook google gmail app apps online offline internet website websites web
email mobile phone smartphone laptop computer software hardware editing editor content creator channel subscribe like
share comment comments link links post posts reel reels story stories live ok okay ai tiktok instagram whatsapp
messenger wifi wi-fi bluetooth camera photo photos selfie design designer marketing digital brand logo business startup
office meeting team project update download upload login account profile page group iphone android windows mac excel
powerpoint zoom bkash nagad rocket daraz pathao foodpanda netflix spotify cloud server data code coding developer
freelancing freelancer fiverr upwork linkedin twitter pdf usb shop order delivery offer sale discount""".split())
URL_RX = re.compile(r"(?:https?://|www\.)\S+|\b[\w-]+\.(?:com|org|net|io|co|ai|app|dev|bd|in|uk|me|info|xyz|tv)"
                    r"(?:/\S*)?\b", re.I)
EMAIL_RX = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
SYMBOL_RX = re.compile(r"[&/#@+=]")
SQUARE_RX = re.compile(r"\[[^\]]{1,40}\]")
DIGIT_RX = re.compile(r"[0-9\u09e6-\u09ef]")
LATIN_WORD_RX = re.compile(r"[A-Za-z][A-Za-z'\u2019\-]*")
SCREEN_WORDS = [nfc(x) for x in (
    "see below", "see above", "shown below", "shown above", "listed below", "listed above", "the list below",
    "the list above", "this list", "the table below", "the table above", "নিচে দেখুন", "উপরে দেখুন",
    "নিচের তালিকা", "উপরের তালিকা", "এই তালিকা", "নিচের সারণি", "উপরের সারণি")]


def text_warnings(spoken: str, family: str, lexicon: list, numbers: str, bn: bool = None) -> list:
    """What a voice would read oddly: [{"kind", "text", "hint"}]. plan prints them; render refuses them without
    --force. `bn`: the sentence as written is Bangla (a lexicon can put Bengali letters into an English line)."""
    out = []
    body = TAG_RX.sub(" ", spoken)
    if family == "director_text":
        body = re.sub(r"\[[a-z][a-z \-]*\]", " ", body)
    for m in EMAIL_RX.finditer(body):
        out.append({"kind": "email", "text": m.group(0), "hint": "write the address as it is said"})
    body_nomail = EMAIL_RX.sub(" ", body)
    for m in URL_RX.finditer(body_nomail):
        out.append({"kind": "url", "text": m.group(0), "hint": "write the address as it is said, or show it on screen"})
    rest = URL_RX.sub(" ", body_nomail)
    for m in SYMBOL_RX.finditer(rest):
        out.append({"kind": "symbol", "text": m.group(0), "hint": "write the word the voice should say"})
    if family == "speech_metadata":
        for m in SQUARE_RX.finditer(rest):
            out.append({"kind": "square_brackets", "text": m.group(0),
                        "hint": "3.8 reads square brackets aloud: use a mode (@mode) or an angle-bracket tag"})
    if numbers == "words":
        for m in re.finditer(r"\S*" + DIGIT_RX.pattern + r"\S*", rest):
            out.append({"kind": "digits", "text": m.group(0),
                        "hint": "digits left in the spoken text: write it as it is said, or add it to the lexicon"})
    if (is_bn(spoken) if bn is None else bn):
        lex_words = set()
        for d, s in lexicon:
            lex_words.update(w.lower() for w in LATIN_WORD_RX.findall(d + " " + s))
        for m in LATIN_WORD_RX.finditer(rest):
            w = m.group(0)
            if w.lower().strip("'-") in ENGLISH_OK or w.lower() in lex_words:
                continue
            hint = ("an acronym in Latin letters inside Bangla: write it as said (for example এআই) or add it to the "
                    "lexicon") if w.isupper() and len(w) <= 6 else (
                "Latin letters inside Bangla are read with an English accent: write Bangla in Bengali script, or "
                "add the word to the lexicon")
            out.append({"kind": "latin_in_bangla", "text": w, "hint": hint})
    low = nfc(body.lower())
    for phrase in SCREEN_WORDS:
        if phrase in low:
            out.append({"kind": "screen_words", "text": phrase,
                        "hint": "a listener cannot see the page: say what it is instead"})
    return out


# ------------------------------------------------------------------------------------------------ script parsing

ABBREV = {"mr", "mrs", "ms", "dr", "prof", "sr", "jr", "st", "vs", "etc", "e.g", "i.e", "inc", "ltd", "co", "no",
          "approx", "fig", "mt", "ft", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "sept", "oct", "nov",
          "dec", "dept", "u.s", "u.k", "a.m", "p.m", "cf", "al", "min", "max", "nos", "ave",
          nfc("খ্রি"), nfc("হি"), nfc("ড"), nfc("ডা"), nfc("মো"), nfc("পৃ")}
TERMINATORS = ".!?\u0964\u0965\u2026"
CLOSERS = "\"')]}\u201d\u2019\u00bb"


def split_sentences(line: str) -> list:
    """One script line -> sentences. Ends: . ! ? danda, double danda, ellipsis, and the line end. Never inside a
    {display|spoken} pair or a tag, on a decimal, an abbreviation, initials or a web address."""
    out, start, i, n = [], 0, 0, len(line)
    while i < n:
        ch = line[i]
        if ch == "{":
            j = line.find("}", i)
            if j > 0:
                i = j + 1
                continue
        if ch == "<":
            m = TAG_RX.match(line, i)
            if m:
                i = m.end()
                continue
        if ch not in TERMINATORS:
            i += 1
            continue
        j = i + 1
        while j < n and line[j] in TERMINATORS:
            j += 1
        while j < n and line[j] in CLOSERS:
            j += 1
        if j >= n:
            break
        if not line[j].isspace():
            i = j
            continue
        k = j
        while k < n and line[k].isspace():
            k += 1
        nxt = line[k] if k < n else ""
        run = line[i:j].rstrip(CLOSERS)
        ws = line.rfind(" ", 0, i) + 1
        token = line[ws:i].lower().lstrip("([\"'\u201c\u2018")
        if run == ".":
            if token in ABBREV or re.fullmatch(r"[a-z]", token) or re.fullmatch(r"(?:[a-z]\.)+[a-z]", token):
                i = j
                continue
            if nxt.isascii() and nxt.islower():
                i = j
                continue
        if run in ("...", "\u2026") and nxt.isascii() and nxt.islower():
            i = j
            continue
        out.append(line[start:j].strip())
        start = i = k
    rest = line[start:].strip()
    if rest:
        out.append(rest)
    return [s for s in out if s]


SPEAKER_RX = re.compile(r"^([^\s:@#/][^:]{0,40}?):\s+(.+)$")


def parse_script(text: str) -> dict:
    """Script text -> {"cast", "scenes", "units", "tail_pause", "errors", "warnings"}. Units are sentences with their
    scene, paragraph, profile, speaker, mode and markers."""
    lines = clean_text(text).split("\n")
    cast, scenes, units, errors, warnings = {}, [], [], [], []
    cur_profile, cur_mode, pending_takes, pending_pause = None, None, None, 0.0
    para, para_open, turn, turn_speaker, seen = 0, False, 0, None, False

    def ensure_scene():
        if not scenes:
            scenes.append({"id": "s1", "title": ""})

    for ln, raw_line in enumerate(lines, 1):
        s = raw_line.strip()
        if not s:
            if para_open:
                para += 1
                para_open = False
            turn_speaker = None
            continue
        if s.startswith("//"):
            continue
        if re.match(r"^#{1,6}(\s|$)", s):
            scenes.append({"id": f"s{len(scenes) + 1}", "title": s.lstrip("#").strip()})
            if para_open:
                para += 1
                para_open = False
            turn_speaker = None
            continue
        if s.startswith("@"):
            m = re.match(r"^@([A-Za-z]+)\s*(.*)$", s)
            name, arg = (m.group(1).lower(), m.group(2).strip()) if m else ("", "")
            if name == "cast":
                if seen:
                    errors.append({"line": ln, "error": "@cast goes at the top, before the first spoken line"})
                    continue
                for pair in [x.strip() for x in arg.split(",") if x.strip()]:
                    if "=" not in pair:
                        errors.append({"line": ln, "error": f"@cast wants Name=profile pairs, not {pair!r}"})
                        continue
                    who, prof = [x.strip() for x in pair.split("=", 1)]
                    if not who or not NAME_RX.match(prof):
                        errors.append({"line": ln, "error": f"@cast: bad pair {pair!r}"})
                        continue
                    cast[who] = prof
            elif name == "profile":
                if not NAME_RX.match(arg):
                    errors.append({"line": ln, "error": f"@profile wants a profile name, not {arg!r}"})
                else:
                    cur_profile = arg
            elif name == "mode":
                if not arg:
                    errors.append({"line": ln, "error": "@mode wants a mode name, or off"})
                else:
                    cur_mode = None if arg.lower() == "off" else arg
            elif name == "takes":
                if not arg:
                    pending_takes = "hero"
                elif re.fullmatch(r"\d+", arg) and 1 <= int(arg) <= 5:
                    pending_takes = int(arg)
                else:
                    errors.append({"line": ln, "error": "@takes wants a number from 1 to 5"})
            elif name == "pause":
                try:
                    sec = float(arg)
                except ValueError:
                    sec = -1
                if not 0.05 <= sec <= 30:
                    errors.append({"line": ln, "error": "@pause wants seconds from 0.05 to 30, for example @pause 1.2"})
                else:
                    pending_pause += sec
            else:
                errors.append({"line": ln, "error": f"unknown directive {s.split()[0]}; known: @cast @profile @mode "
                                                    "@takes @pause"})
            continue
        speaker = None
        body = s
        m = SPEAKER_RX.match(s)
        if cast and m and m.group(1).strip() in cast:
            speaker = m.group(1).strip()
            body = m.group(2).strip()
            turn += 1
            turn_speaker = speaker
        else:
            if cast and m and re.fullmatch(r"[A-Z\u0985-\u09b9][\w .'\u0980-\u09ff-]{0,30}", m.group(1).strip()):
                warnings.append({"line": ln, "kind": "speaker",
                                 "text": m.group(1).strip(), "hint": "looks like a speaker but is not in @cast: "
                                                                     "it is read as narration"})
            if turn_speaker and para_open:
                speaker = turn_speaker
        ensure_scene()
        seen = True
        para_open = True
        for i, sent in enumerate(split_sentences(body)):
            units.append({"line": ln, "scene": scenes[-1]["id"], "para": para, "profile": cur_profile,
                          "speaker": speaker, "turn": turn if speaker else None, "mode": cur_mode, "raw": sent,
                          "takes": pending_takes if i == 0 else None,
                          "pause_before": round(pending_pause, 3) if i == 0 else 0.0})
            if i == 0:
                pending_takes, pending_pause = None, 0.0
    if not units:
        errors.append({"line": 0, "error": "the script has no spoken lines"})
    return {"cast": cast, "scenes": scenes, "units": units, "tail_pause": round(pending_pause, 3),
            "errors": errors, "warnings": warnings}


# ------------------------------------------------------------------------------------------------ chunking

def articulation_wps(p: dict, calib: dict = None) -> tuple:
    """Words per voiced second for estimates and the duration gate: this project's calibration, the profile's
    measured value, or the preset's words per minute less the pause share (a starting guess)."""
    c = (calib or {}).get(p["name"]) or {}
    if c.get("measured_wps"):
        return float(c["measured_wps"]), "calibration.json"
    if (p.get("wpm") or {}).get("measured_wps"):
        return float(p["wpm"]["measured_wps"]), "profile"
    return float(p["wpm"]["target"]) / 60.0 / (1.0 - PAUSE_SHARE), "preset words per minute (not calibrated yet)"


def tag_seconds(tags: list) -> float:
    return sum(TAG_SECONDS.get(t, OTHER_TAG_S) for t in tags)


def chunk_cost(est: float, lo: float, hi: float, target: float = None) -> float:
    cost = 1.0
    if est < lo:
        cost += 0.05 * (lo - est) ** 2
    if est > hi:
        cost += 0.2 * (est - hi) ** 2
    mid = target if target is not None else (lo + hi) / 2.0
    cost += (0.05 if target is not None else 0.002) * (est - mid) ** 2
    return cost


def partition(sents: list, lim: dict, precise: bool, target: float = None) -> list:
    """Split one run of sentences (one scene, speaker, mode and paragraph) into chunks: few requests, 12 to 35 s where
    possible, never over the limits, no lone fragment. Returns [(i, j)] index ranges."""
    n = len(sents)
    lo, hi = lim["target_s"]
    best = [math.inf] * (n + 1)
    back = [0] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for i in range(max(0, j - 4), j):
            group = sents[i:j]
            k = j - i
            if precise and k > 1 and not (k == 2 and any(s["fragment"] for s in group)):
                continue
            words = sum(s["n_words"] for s in group)
            est = sum(s["est_s"] for s in group) + INNER_PAUSE_S * (k - 1)
            chars = sum(s["chars"] for s in group)
            if k > 1 and (est > lim["max_s"] or words > lim["max_words"] or
                          (group[0]["bn"] and (words > BN_MAX_WORDS or chars > lim["max_chars_bn"]))):
                continue
            c = chunk_cost(est, lo, hi, target)
            if k == 1 and group[0]["fragment"] and n > 1:
                c += 50.0
            if best[i] + c < best[j]:
                best[j] = best[i] + c
                back[j] = i
    ranges, j = [], n
    while j > 0:
        i = back[j]
        ranges.append((i, j))
        j = i
    return list(reversed(ranges))


def build_plan(script_text: str, main_name, pdir: Path, precise=None, source: str = None, calib: dict = None) -> dict:
    """Parse, normalise and chunk a script. Free: no call is made. Returns the plan (errors and warnings inside)."""
    parsed = parse_script(script_text)
    errors = list(parsed["errors"])
    warnings = list(parsed["warnings"])
    notes = []
    names = [main_name] if main_name else []
    names += [u["profile"] for u in parsed["units"] if u["profile"]]
    names += list(parsed["cast"].values())
    if not main_name:
        first = next((u["profile"] for u in parsed["units"] if u["profile"]), None)
        main_name = first or (list(parsed["cast"].values())[0] if parsed["cast"] else None)
    if not main_name:
        raise ProfileError("no profile: pass --profile NAME (or use @profile or @cast in the script)")
    profiles, lexicons = {}, {}
    for name in dict.fromkeys(n for n in names if n):
        profiles[name] = load_profile(name, pdir)
        lexicons[name] = load_lexicon(profiles[name], pdir)
    main = profiles[main_name]
    if precise is None:
        precise = bool(main.get("precise"))
    lex_cache = {name: lexicon_rx(lex) for name, lex in lexicons.items()}
    sents = []
    for u in parsed["units"]:
        pname = parsed["cast"].get(u["speaker"]) if u["speaker"] else None
        pname = pname or u["profile"] or main_name
        p = profiles[pname]
        mode_style = None
        if u["mode"]:
            if u["mode"] not in p["modes"]:
                errors.append({"line": u["line"], "error": f"mode {u['mode']} is not in profile {pname} (modes: "
                                                           f"{', '.join(p['modes']) or 'none'})"})
            else:
                mode_style = p["modes"][u["mode"]]
        nm = normalise(u["raw"], p["prompt_family"], lexicons[pname], p["numbers"], lex_cache[pname])
        allowed = {t.strip("<>").strip() for t in p.get("tags_allowed") or []}
        for t in nm["tags"]:
            if t not in allowed:
                errors.append({"line": u["line"], "error": f"tag <{t}> is not in profile {pname}'s tags_allowed "
                                                           f"({', '.join(sorted(allowed)) or 'none'})"})
        for w in text_warnings(nm["spoken"], p["prompt_family"], lexicons[pname], p["numbers"], is_bn(u["raw"])):
            w["line"] = u["line"]
            warnings.append(w)
        words = spoken_words(nm["spoken"])
        wps, _ = articulation_wps(p, calib)
        bn = is_bn(nm["spoken"])
        est = len(words) / wps + tag_seconds(nm["tags"]) if words else tag_seconds(nm["tags"])
        sents.append({"u": u, "profile": pname, "style": mode_style, "nm": nm, "n_words": len(words),
                      "chars": len(nm["spoken"]), "graphemes": graphemes(nm["spoken"]), "bn": bn,
                      "est_s": est, "fragment": len(words) < FRAGMENT_WORDS})
    # runs: same scene, paragraph, profile, speaker, turn and mode; a pause or a takes marker starts a new run
    runs = []
    for s in sents:
        u = s["u"]
        keyv = (u["scene"], u["para"], s["profile"], u["speaker"], u["turn"], u["mode"])
        if runs and runs[-1]["key"] == keyv and not u["pause_before"] and u["takes"] is None:
            runs[-1]["sents"].append(s)
        else:
            runs.append({"key": keyv, "sents": [s]})
    chunks = []
    for r in runs:
        p = profiles[r["sents"][0]["profile"]]
        lim = p["chunk"]
        for s in r["sents"]:
            if s["est_s"] > lim["max_s"] or s["n_words"] > lim["max_words"] or (
                    s["bn"] and (s["n_words"] > BN_MAX_WORDS or s["chars"] > lim["max_chars_bn"])):
                errors.append({"line": s["u"]["line"], "error": f"one sentence is too long for one request "
                                                                f"({s['n_words']} words, about {s['est_s']:.0f} s): "
                                                                "split it"})
        r["ranges"] = partition(r["sents"], lim, precise)
    # keep narration chunk lengths inside a scene within 2x: one more pass that pulls runs toward the scene median.
    # Dialogue turns, @takes lines and lines that stand alone are short by design and do not count.
    by_scene = {}
    for r in runs:
        if r["sents"][0]["u"]["speaker"] is None and r["sents"][0]["u"]["takes"] is None:
            by_scene.setdefault(r["key"][0], []).append(r)
    for scene_id, scene_runs in by_scene.items():
        def ests(rs):
            out = []
            for r in rs:
                for i, j in r["ranges"]:
                    g = r["sents"][i:j]
                    if not (len(g) == 1 and g[0]["fragment"] and len(r["sents"]) == 1):
                        out.append(sum(x["est_s"] for x in g) + INNER_PAUSE_S * (len(g) - 1))
            return out
        e = ests(scene_runs)
        if len(e) >= 2 and max(e) > 2 * min(e):
            target = statistics.median(e)
            for r in scene_runs:
                p = profiles[r["sents"][0]["profile"]]
                r["ranges"] = partition(r["sents"], p["chunk"], precise, target)
            e = ests(scene_runs)
            if len(e) >= 2 and max(e) > 2 * min(e):
                notes.append({"scene": scene_id, "note": f"chunk lengths in scene {scene_id} run from {min(e):.1f} s "
                                                         f"to {max(e):.1f} s (more than 2x); pace can drift with "
                                                         "length: merge the short paragraph into its neighbour or "
                                                         "split the long one"})
    gaps = main["gaps_ms"]
    for r in runs:
        for (i, j) in r["ranges"]:
            g = r["sents"][i:j]
            first = g[0]
            p = profiles[first["profile"]]
            u = first["u"]
            standalone = len(g) == 1 and first["fragment"] and (len(r["sents"]) == 1)
            mode_style = first["style"]
            if standalone and not u["mode"]:
                style = ""
            else:
                style = mode_style if mode_style is not None else (p.get("style") or "")
            takes = int(p["takes"]["default"])
            hero = False
            if (i == 0) and u["takes"] is not None:
                hero = True
                takes = int(p["takes"]["hero"]) if u["takes"] == "hero" else int(u["takes"])
            if standalone:
                takes = max(takes, 2)
            spoken = " ".join(x["nm"]["spoken"] for x in g)
            display = " ".join(x["nm"]["display"] for x in g)
            tags = [t for x in g for t in x["nm"]["tags"]]
            terms = []
            for x in g:
                for t in x["nm"]["terms"]:
                    if t not in terms:
                        terms.append(t)
            est = sum(x["est_s"] for x in g) + INNER_PAUSE_S * (len(g) - 1)
            ch = {"id": f"c{len(chunks) + 1:03d}", "scene": u["scene"], "para": u["para"], "profile": first["profile"],
                  "speaker": u["speaker"], "mode": u["mode"], "style": style, "standalone": standalone, "hero": hero,
                  "takes": takes,
                  "sentences": [{"display": x["nm"]["display"], "spoken": x["nm"]["spoken"],
                                 "words": word_map(x["nm"]["segs"]), "n_words": x["n_words"],
                                 "graphemes": x["graphemes"], "line": x["u"]["line"]} for x in g],
                  "display": display, "spoken": spoken, "request_text": spoken,
                  "n_words": sum(x["n_words"] for x in g), "chars": len(spoken), "est_s": round(est, 2),
                  "tags": tags, "lexicon_terms": terms, "model": p["model"], "family": p["prompt_family"],
                  "voice": p["voice"]["id"], "voice_type": p["voice"].get("type", "prebuilt"),
                  "voice_key": voice_key(p["voice"]), "language": p["language"],
                  "send_language_code": bool(p.get("send_language_code")), "pause_before": u["pause_before"]}
            ch["base_key"] = sha16(key_fields(ch))
            chunks.append(ch)
    lead = 0.0
    for idx, ch in enumerate(chunks):
        nxt = chunks[idx + 1] if idx + 1 < len(chunks) else None
        if idx == 0 and ch["pause_before"]:
            lead = ch["pause_before"]
        if nxt is None:
            tail = parsed["tail_pause"]
            ch["gap_after"] = {"kind": "pause", "s": tail} if tail else {"kind": "end", "s": 0.0}
        elif nxt["pause_before"]:
            ch["gap_after"] = {"kind": "pause", "s": nxt["pause_before"]}
        elif nxt["scene"] != ch["scene"]:
            ch["gap_after"] = {"kind": "scene", "s": gaps["scene"] / 1000.0}
        elif nxt["para"] != ch["para"]:
            ch["gap_after"] = {"kind": "paragraph", "s": gaps["paragraph"] / 1000.0}
        else:
            ch["gap_after"] = {"kind": "sentence", "s": gaps["sentence"] / 1000.0}
    for ch in chunks:
        ch.pop("pause_before", None)
    for p in profiles.values():
        days = voice_days_left(p)
        if days is not None and days < EXPIRY_WARN_DAYS:
            notes.append({"profile": p["name"], "note": (
                f"profile {p['name']}: the designed voice {p['voice']['id']} expired {-days:.0f} days ago; cached "
                "chunks still work, new ones need a new voice") if days < 0 else (
                f"profile {p['name']}: the designed voice {p['voice']['id']} expires in {days:.0f} days; masters are "
                "kept, but new chunks after that need a new voice")})
    plan = {"schema": "nexa-speech/plan-1", "skill_version": SKILL_VERSION, "created": now_iso(),
            "script": source, "script_sha": sha16(clean_text(script_text)), "main_profile": main_name,
            "precise": bool(precise), "cast": parsed["cast"], "profiles": profiles,
            "lexicons": {k: [list(x) for x in v] for k, v in lexicons.items()},
            "scenes": parsed["scenes"], "lead_pause_s": lead, "chunks": chunks, "errors": errors,
            "warnings": warnings, "notes": notes}
    plan["totals"] = plan_totals(plan)
    return plan


def key_fields(ch: dict) -> dict:
    return {"engine": "gemini-api", "endpoint": "interactions", "model": ch["model"], "voice": ch["voice_key"],
            "language": ch["language"], "style": ch["style"], "prompt_family": ch["family"],
            "text": ch["request_text"], "format": "audio/l16@24000",
            "send_language_code": bool(ch.get("send_language_code"))}


def take_key(ch: dict, take: int) -> str:
    fields = key_fields(ch)
    fields["take"] = int(take)
    return sha16(fields)


def take_cost(ch: dict, day: str = None) -> float:
    tokens = text_tokens(ch["request_text"]) + text_tokens(ch["style"]) + (40 if ch["family"] == "director_text"
                                                                         else 0)
    return tts_usd(ch["model"], ch["est_s"], tokens, day)


def plan_totals(plan: dict) -> dict:
    chunks = plan["chunks"]
    speech = sum(c["est_s"] for c in chunks)
    gaps = sum(c["gap_after"]["s"] for c in chunks)
    paid = list({c["base_key"]: c for c in chunks}.values())     # the same words twice are paid for once
    requests = sum(c["takes"] for c in paid)
    audio_s = sum(c["est_s"] * c["takes"] for c in paid)
    tokens_in = sum((text_tokens(c["request_text"]) + text_tokens(c["style"])) * c["takes"] for c in paid)
    by_model = {}
    for c in paid:
        m = by_model.setdefault(c["model"], {"requests": 0, "audio_s": 0.0, "usd": 0.0, "usd_after_2027": 0.0})
        m["requests"] += c["takes"]
        m["audio_s"] += c["est_s"] * c["takes"]
        m["usd"] += take_cost(c) * c["takes"]
        m["usd_after_2027"] += take_cost(c, "2027-01-01") * c["takes"]
    interactive = sum(m["usd"] for m in by_model.values())
    return {"chunks": len(chunks), "scenes": len(plan["scenes"]), "requests": requests,
            "speech_s": round(speech, 1), "total_s": round(plan["lead_pause_s"] + speech + gaps, 1),
            "audio_tokens": int(round(audio_s * AUDIO_TOKENS_PER_S)), "text_tokens": tokens_in,
            "usd": {"interactive": round(interactive, 4), "batch_or_flex": round(interactive * BATCH_FACTOR, 4),
                    "interactive_from_2027": round(sum(m["usd_after_2027"] for m in by_model.values()), 4),
                    "likely_bill": round(interactive * BILL_FACTOR, 4)},
            "by_model": {k: {"requests": v["requests"], "audio_s": round(v["audio_s"], 1), "usd": round(v["usd"], 4)}
                         for k, v in by_model.items()},
            "prices_as_of": PRICES_AS_OF}


# ------------------------------------------------------------------------------------------------ requests

def request_body(ch: dict) -> dict:
    """The exact request for one chunk. 3.8: the transcript in `text`, the style in speech_metadata (never in the
    text). 3.1 and 2.5: one string with the director block. No temperature, ever."""
    sc = {"voice": ch["voice"]}
    if ch.get("send_language_code"):
        sc["language"] = ch["language"]
    if ch["family"] == "speech_metadata":
        item = {"type": "text", "text": ch["request_text"]}
        if ch["style"]:
            item["annotations"] = [{"type": "speech_metadata", "style": ch["style"]}]
        return {"model": ch["model"], "store": False, "input": [item],
                "response_format": {"type": "audio", "mime_type": "audio/l16", "sample_rate": 24000},
                "generation_config": {"speech_config": [sc]}}
    text = DIRECTOR_HEAD
    if ch["style"]:
        text += "\n### PERFORMANCE\n" + ch["style"]
    text += "\n#### TRANSCRIPT\n" + ch["request_text"]
    return {"model": ch["model"], "store": False, "input": text, "response_format": {"type": "audio"},
            "generation_config": {"speech_config": [sc]}}


def finish_class(st: dict, has_audio: bool) -> str:
    reason = str(st.get("finish_reason") or "").upper()
    status = str(st.get("status") or "").upper()
    if reason in SAFETY_REASONS:
        return "blocked"
    if status in ("FAILED", "CANCELLED", "CANCELED"):
        return "failed"
    if reason not in OK_REASONS or status not in OK_STATUS:
        return "truncated"
    if not has_audio:
        return "empty"
    return "ok"


def explain(err) -> str:
    """What happened, in plain words, and what the user can do. Nothing here is retried in a loop."""
    kind = getattr(err, "kind", "")
    if kind == "no_key":
        return G.MISSING_KEY_HELP
    if kind == "billing":
        return ("The key's Google Cloud project needs billing turned on (or this model has no free tier). Turn it "
                "on, then run the same command again: finished chunks are cached.")
    if kind == "auth":
        return "The key was refused (invalid, expired or restricted). Check it in AI Studio."
    if kind == "quota_day":
        return ("The daily request quota for this model is used up. Wait until midnight Pacific time, or render with "
                "another model (a new model is a new voice: render the whole project on it). Finished chunks are "
                "cached.")
    if kind == "quota_minute":
        return ("The per-minute quota was hit and the waits did not clear it. Try again in a minute; finished chunks "
                "are cached.")
    if kind == "safety":
        return ("The service refused this line. Rephrase or shorten it, or try the other voice once; it is never "
                f"retried automatically. ({err})")
    if kind == "bad_request":
        return f"The request was rejected: {err}"
    if kind == "timeout":
        return ("No answer in time. It was not retried, because the call may still be billed. Run again later; "
                "finished chunks are cached.")
    if kind in ("server", "network", "empty"):
        return f"The service did not answer properly ({err}). Run the same command again later; nothing is paid twice."
    return str(err)


def pcm_frames(part: dict) -> tuple:
    """(frames, rate) of one audio part: a RIFF WAV is opened as such, anything else is raw 16-bit PCM."""
    data = part["bytes"]
    if G.is_riff(data):
        with wave.open(io.BytesIO(data), "rb") as w:
            return w.readframes(w.getnframes()), w.getframerate()
    return data, int(part.get("sample_rate") or 24000)


def save_master(parts: list, key: str) -> Path:
    """The paid audio in the cache as <key>.wav, written once: a RIFF answer as it came (never wrapped twice), raw
    PCM with a header; several parts are joined."""
    cdir = cache_dir()
    cdir.mkdir(parents=True, exist_ok=True)
    final = cdir / f"{key}.wav"
    tmp_stem = str(cdir / f".{key}.{os.getpid()}.{threading.get_ident()}")
    if len(parts) == 1:
        path = Path(G.save_audio(parts[0], tmp_stem))
        if path.suffix != ".wav":
            keep = cdir / f"{key}{path.suffix}"
            os.replace(path, keep)
            ff(["-v", "error", "-y", "-i", keep, "-ac", "1", "-ar", "24000", "-c:a", "pcm_s16le", final])
            return final
        os.replace(path, final)
        return final
    frames, rate = b"", 24000
    for part in parts:
        f, rate = pcm_frames(part)
        frames += f
    with open(tmp_stem + ".wav", "wb") as fh:
        fh.write(G.pcm_to_wav(frames, rate))
    os.replace(tmp_stem + ".wav", final)
    return final


def nested_riff(path: Path) -> bool:
    try:
        with wave.open(str(path), "rb") as w:
            return w.readframes(2)[:4] == b"RIFF"
    except (wave.Error, EOFError):
        return False


def ledger(project: Path, entry: dict) -> None:
    append_jsonl(project / "ledger.jsonl", entry)


def synth_take(ch: dict, take: int, project: Path, command: str, ledger_dir: Path = None) -> dict:
    """One paid call: the master in the cache and the project, its sidecar, and one ledger line (in `ledger_dir`,
    else the project). Raises GeminiError for errors the user has to see (quota, billing, safety and so on)."""
    ledger_dir = ledger_dir or project
    key = take_key(ch, take)
    body = request_body(ch)
    est = take_cost(ch)
    t0 = time.time()
    base = {"time": now_iso(), "command": command, "project": str(project), "chunk": ch.get("id"), "take": take,
            "master_key": key, "model": ch["model"], "voice": ch["voice"],
            "units": {"audio_s_est": ch["est_s"], "audio_tokens_est": int(round(ch["est_s"] * AUDIO_TOKENS_PER_S)),
                      "text_tokens_est": text_tokens(ch["request_text"]) + text_tokens(ch["style"])}}
    try:
        resp, info = G.interactions(body, timeout=TTS_TIMEOUT)
    except G.GeminiError as err:
        ledger(ledger_dir, dict(base, est_usd=0.0, key_source=None, result="error:" + err.kind,
                                message=G.scrub(str(err))[:300], seconds=round(time.time() - t0, 2)))
        raise
    parts = G.audio_parts(resp)
    st = G.status(resp)
    fc = finish_class(st, bool(parts))
    rec = {"take": take, "key": key, "finish": st.get("finish_reason"), "status": st.get("status"),
           "finish_class": fc, "riff": bool(parts) and G.is_riff(parts[0]["bytes"]), "source": "api",
           "created": now_iso(), "usage": G.usage(resp), "key_source": info.get("key")}
    # the paid call goes into the ledger before any file is written: a save that fails must not hide it
    ledger(ledger_dir, dict(base, est_usd=round(est, 6), key_source=info.get("key"), usage=rec["usage"],
                            status=st.get("status"), finish=st.get("finish_reason"), result=fc,
                            attempts=info.get("attempts"), seconds=round(time.time() - t0, 2)))
    if parts:
        path = save_master(parts, key)
        rec["nested_riff"] = nested_riff(path)
        side = {"schema": "nexa-speech/master-1", "key": key, "skill_version": SKILL_VERSION, "created": rec["created"],
                "engine": "gemini-api", "endpoint": "interactions", "model": ch["model"], "voice": ch["voice"],
                "voice_key": ch["voice_key"], "language": ch["language"], "style": ch["style"],
                "prompt_family": ch["family"], "text": ch["request_text"], "take": take, "format": "audio/l16@24000",
                "request": body, "finish": rec["finish"], "status": rec["status"], "finish_class": fc,
                "riff": rec["riff"], "usage": rec["usage"], "key_source": info.get("key"), "est_usd": round(est, 6),
                "seconds": round(time.time() - t0, 2)}
        write_json(cache_dir() / f"{key}.json", side)
        link_or_copy(path, project / "masters" / f"{key}.wav")
        write_json(project / "masters" / f"{key}.json", side)     # the project carries its own provenance
        rec["file"] = f"masters/{key}.wav"
    return rec


def cached_take(ch: dict, take: int, project: Path):
    """A take that exists already (global cache or this project's masters), put in both places. None if unpaid."""
    key = take_key(ch, take)
    cpath = cache_dir() / f"{key}.wav"
    ppath = project / "masters" / f"{key}.wav"
    if not cpath.exists() and not ppath.exists():
        return None
    if cpath.exists():
        link_or_copy(cpath, ppath)
    else:
        cache_dir().mkdir(parents=True, exist_ok=True)
        link_or_copy(ppath, cpath)
    cside, pside = cache_dir() / f"{key}.json", project / "masters" / f"{key}.json"
    side = read_json(cside) or read_json(pside) or {}
    if side and not cside.exists():
        write_json(cside, side)
    if side and not pside.exists():
        write_json(pside, side)
    return {"take": take, "key": key, "finish": side.get("finish"), "status": side.get("status"),
            "finish_class": side.get("finish_class") or "ok", "riff": side.get("riff"), "source": "cache",
            "created": side.get("created"), "usage": side.get("usage"), "key_source": side.get("key_source"),
            "nested_riff": nested_riff(ppath), "file": f"masters/{key}.wav"}


def run_jobs(jobs: list, project: Path, command: str, ledger_dir: Path = None) -> tuple:
    """Paid calls for [(chunk, take)], at most three at a time. Returns (records {(base, take): rec}, failures
    [{chunk, take, kind, message}], the error that stopped the run or None). Nothing is retried here: the waits for
    per-minute limits and server errors live in gemini_api."""
    stop = threading.Event()
    stopped = []
    recs, fails = {}, []

    def work(job):
        ch, take = job
        if stop.is_set():
            return job, None, None
        try:
            log(f"{ch.get('id', '?')} take {take}: calling {ch['model']} ({ch['est_s']:.0f} s of speech)")
            return job, synth_take(ch, take, project, command, ledger_dir), None
        except G.GeminiError as err:
            if err.kind in STOP_KINDS:
                stop.set()
                stopped.append(err)
            return job, None, err
    with cf.ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        for (ch, take), rec, err in pool.map(work, jobs):
            if rec is not None:
                recs[(ch["base_key"], take)] = rec
            elif err is not None:
                fails.append({"chunk": ch.get("id"), "take": take, "kind": err.kind, "message": explain(err)})
    return recs, fails, (stopped[0] if stopped else None)


# ------------------------------------------------------------------------------------------------ audio analysis

def _parse_meta(text: str) -> list:
    frames, cur = [], None
    for line in text.splitlines():
        if line.startswith("frame:"):
            m = re.search(r"pts_time:([0-9.eE+-]+)", line)
            cur = {"t": float(m.group(1)) if m else 0.0, "rms": -120.0, "peak": -120.0, "cen": 0.0, "flat": 0.0}
            frames.append(cur)
        elif cur is not None and "=" in line:
            k, v = line.split("=", 1)
            try:
                val = float(v)
            except ValueError:
                val = -120.0
            if math.isinf(val) or math.isnan(val):
                val = -120.0
            if k.endswith("RMS_level"):
                cur["rms"] = val
            elif k.endswith("Peak_level"):
                cur["peak"] = val
            elif k.endswith("centroid"):
                cur["cen"] = val
            elif k.endswith("flatness"):
                cur["flat"] = val
    return frames


def analyse_audio(path: Path) -> dict:
    """What the gates and the master need to know about one take, from one ffmpeg pass (10 ms frames of RMS,
    spectral centroid and flatness, ebur128, astats) and a look at the samples."""
    rate, smp = read_wav(path)
    n = len(smp)
    dur = n / float(rate) if rate else 0.0
    if n == 0:
        return {"version": ANALYSIS_VERSION, "empty": True, "duration_s": 0.0}
    win = max(32, rate // 100)
    af = (f"asetnsamples=n={win}:p=0,astats=metadata=1:reset=1:measure_perchannel=none:"
          f"measure_overall=RMS_level+Peak_level,aspectralstats=win_size={win}:overlap=0:measure=centroid+flatness,"
          "ametadata=mode=print:file=-,ebur128=peak=true:framelog=quiet,"
          "astats=measure_perchannel=none:measure_overall=Peak_level+Peak_count+RMS_level")
    r = ff(["-v", "info", "-i", path, "-af", af, "-f", "null", "-"], check=False)
    frames = _parse_meta(r.stdout or "")
    err = r.stderr or ""
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else ""

    def grab(rx, text):
        m = re.findall(rx, text)
        if not m:
            return None
        try:
            v = float(m[-1])
        except ValueError:
            return None
        return None if math.isinf(v) else v
    li = grab(r"I:\s*(-?[0-9.]+)\s*LUFS", summ)
    if li is not None and li <= -69.9:
        li = None
    peak_db = grab(r"Peak level dB:\s*(-?[0-9.]+|-inf)", err)
    peak_count = grab(r"Peak count:\s*([0-9.]+)", err)
    thr = max(-50.0, min(-35.0, (li - 25.0) if li is not None else -45.0))
    amp = 32768.0 * 10 ** (thr / 20.0)
    fdur = win / float(rate)
    p5 = max((abs(x) for x in smp[: int(0.005 * rate)]), default=0)
    p50 = max((abs(x) for x in smp[int(0.005 * rate): int(0.055 * rate)]), default=0)
    click = p5 > 0.03 * 32768 and p5 > 4 * max(p50, 1)
    skip = 0.025 if click else 0.0
    sound = [f["rms"] > thr for f in frames]
    first_i = next((i for i, f in enumerate(frames) if sound[i] and f["t"] >= skip), None)
    if first_i is None:
        return {"version": ANALYSIS_VERSION, "empty": True, "duration_s": round(dur, 4), "rate": rate,
                "loudness_i": li, "click": click}
    lo = max(int(skip * rate), int((frames[first_i]["t"] - fdur) * rate))
    hi = min(n, int((frames[first_i]["t"] + fdur) * rate))
    first = next((k for k in range(lo, hi) if abs(smp[k]) > amp), int(frames[first_i]["t"] * rate)) / float(rate)
    tail = [f for f in frames if f["t"] >= dur - 0.3]
    live = [f for f in tail if f["rms"] > -70]
    noise_tail, flat_tail = False, None
    if len(tail) >= 10 and len(live) >= 0.8 * len(tail):
        level = 10 * math.log10(sum(10 ** (f["rms"] / 10.0) for f in live) / len(live))
        flat_tail = statistics.median(f["flat"] for f in live)
        noise_tail = level > -50 and flat_tail >= 0.4
    if noise_tail:
        i = len(frames) - 1
        while i > first_i and (frames[i]["rms"] <= -70 or (frames[i]["flat"] >= 0.3 and frames[i]["rms"] < thr + 20)):
            i -= 1
        last = min(dur, frames[i]["t"] + fdur)
    else:
        last_i = max(i for i in range(len(frames)) if sound[i])
        hi = min(n, int((frames[last_i]["t"] + fdur) * rate))
        lo = max(0, int(frames[last_i]["t"] * rate) - 1)
        k = next((k for k in range(hi - 1, lo, -1) if abs(smp[k]) > amp), hi - 1)
        last = min(dur, (k + 1) / float(rate))
    last = max(last, first + 0.01)
    quiet, run_start = [], None
    for f, s in zip(frames, sound):
        inside = first <= f["t"] < last
        if inside and not s:
            run_start = f["t"] if run_start is None else run_start
        else:
            if run_start is not None and f["t"] - run_start >= 0.15:
                quiet.append([round(run_start, 3), round(f["t"], 3)])
            run_start = None
    voiced = max(0.0, (last - first) - sum(b - a for a, b in quiet))
    cents = [f["cen"] for f, s in zip(frames, sound) if s and first <= f["t"] < last and f["cen"] > 1.0]
    clipped = peak_db is not None and peak_db >= -0.1 and (peak_count or 0) >= 3
    return {"version": ANALYSIS_VERSION, "empty": False, "rate": rate, "duration_s": round(dur, 4),
            "first_sound": round(first, 4), "last_sound": round(last, 4), "lead_s": round(first, 4),
            "voiced_s": round(voiced, 3), "pauses": quiet, "loudness_i": li, "threshold_db": round(thr, 1),
            "centroid_hz": round(sum(cents) / len(cents), 1) if cents else None, "click": click,
            "noise_tail": noise_tail, "tail_flatness": rnd(flat_tail), "peak_db": peak_db,
            "peak_count": peak_count, "clipped": clipped}


def analysis_for(project: Path, key: str) -> dict:
    """The analysis of one master, cached in the project (derived data, rebuilt freely)."""
    apath = project / "analysis" / f"{key}.json"
    got = read_json(apath)
    if isinstance(got, dict) and got.get("version") == ANALYSIS_VERSION:
        return got
    m = analyse_audio(project / "masters" / f"{key}.wav")
    write_json(apath, m)
    return m


# ------------------------------------------------------------------------------------------------ gates

RE_ROLLABLE = {"truncated", "empty", "duration", "asr", "drift"}


def references(plan: dict, state: dict, metrics: dict, calib: dict) -> dict:
    """What each take is measured against, per profile: the speaking rate (the median of this project's chunks once
    there are 3, else calibration.json, the profile, or the preset's pace) and, with 5 or more chunks, the drift
    medians."""
    groups = {}
    for ch in plan["chunks"]:
        entry = state["chunks"].get(ch["base_key"]) or {}
        take = entry.get("chosen") or (min(int(t) for t in entry.get("takes", {})) if entry.get("takes") else None)
        if take is None:
            continue
        rec = entry["takes"].get(str(take)) or {}
        m = metrics.get(rec.get("key"))
        if not m or m.get("empty") or rec.get("finish_class") not in ("ok", None):
            continue
        groups.setdefault(ch["profile"], []).append((ch, m))
    out = {}
    for name, p in plan["profiles"].items():
        items = groups.get(name, [])
        rates = [ch["n_words"] / m["voiced_s"] for ch, m in items if ch["n_words"] >= 4 and m["voiced_s"] >= 0.8]
        if len(rates) >= 3:
            wps, source = statistics.median(rates), f"this project (median of {len(rates)} chunks)"
        else:
            wps, source = articulation_wps(p, calib)
        ref = {"wps": wps, "wps_source": source, "drift": None, "calibrated": not source.startswith("preset")}
        long_items = [(ch, m) for ch, m in items if m["voiced_s"] >= 3.0 and ch["n_words"] >= 4]
        if len(long_items) >= 5:
            r = [ch["n_words"] / m["voiced_s"] for ch, m in long_items]
            li = [m["loudness_i"] for ch, m in long_items if m["loudness_i"] is not None]
            cen = [m["centroid_hz"] for ch, m in long_items if m["centroid_hz"]]
            ref["drift"] = {"n": len(long_items), "rate": statistics.median(r),
                            "loudness": statistics.median(li) if li else None,
                            "centroid_mean": statistics.mean(cen) if len(cen) >= 2 else None,
                            "centroid_sd": statistics.pstdev(cen) if len(cen) >= 2 else None}
        out[name] = ref
    return out


def evaluate(ch: dict, rec: dict, m: dict, ref: dict, asr: dict = None) -> dict:
    """The per-take gates. Fails (gates 1, 2, 4, 5) earn one automatic re-roll; flags (gates 3 and 6) are fixed in
    master or listed for a listen. Returns {"result", "fails", "flags", "gates", "score", "reroll"}."""
    fails, flags, gates, why = [], [], {}, set()
    fc = rec.get("finish_class") or "ok"
    if not m or m.get("empty"):
        fails.append("gate 1: no audio")
        why.add("empty")
        gates["1"] = "fail"
    elif fc in ("truncated", "failed"):
        fails.append(f"gate 1: finish {rec.get('finish') or rec.get('status')} (the audio may be cut short; it is "
                     "billed all the same)")
        why.add("truncated")
        gates["1"] = "fail"
    elif fc == "blocked":
        fails.append(f"gate 1: refused ({rec.get('finish')}): rephrase the line")
        gates["1"] = "fail"
    elif rec.get("nested_riff"):
        fails.append("gate 1: a WAV inside a WAV")
        gates["1"] = "fail"
    else:
        gates["1"] = "pass"
    score = 1000.0 * len(fails)
    ratio = rate_dev = loud_dev = cen_z = None
    if m and not m.get("empty"):
        if ch["n_words"] >= 4 and m["voiced_s"] >= 0.8:
            expected = ch["n_words"] / ref["wps"]
            ratio = m["voiced_s"] / expected
            lo, hi = GATE2_WINDOW if ref.get("calibrated", True) else GATE2_WINDOW_PRESET
            if ratio < lo or ratio > hi:
                fails.append(f"gate 2: duration ratio {ratio:.2f} (voiced {m['voiced_s']:.1f} s against about "
                             f"{expected:.1f} s expected; {lo:.2f} to {hi:.2f} passes"
                             + ("" if ref.get("calibrated", True) else " until the voice's pace is measured") + ")")
                why.add("duration")
                gates["2"] = "fail"
            else:
                gates["2"] = "pass"
            score += abs(ratio - 1.0) * 10
        else:
            gates["2"] = "skip (too short to measure)"
        g3 = []
        if m["lead_s"] < 0.02:
            g3.append("lead-in under 20 ms (padded in master)")
        if m["click"]:
            g3.append("click at the start (trimmed in master)")
        if m["noise_tail"]:
            g3.append("noise after the last word (trimmed in master)")
        flags += ["gate 3: " + x for x in g3]
        gates["3"] = "flag" if g3 else "pass"
        score += 0.5 * len(g3)
        d = ref.get("drift")
        if d and m["voiced_s"] >= 3.0 and ch["n_words"] >= 4:
            g5 = []
            rate_dev = (ch["n_words"] / m["voiced_s"]) / d["rate"] - 1.0
            if abs(rate_dev) > 0.12:
                g5.append(f"speaking rate {rate_dev * 100:+.0f}% from the project median (12% allowed)")
            if d["loudness"] is not None and m["loudness_i"] is not None:
                loud_dev = m["loudness_i"] - d["loudness"]
                if abs(loud_dev) > 4:
                    g5.append(f"loudness {loud_dev:+.1f} LU from the median (4 allowed)")
            if d["centroid_mean"] and m["centroid_hz"]:
                # the spread has a floor of 5% of the mean: near-identical chunks must not turn a few hertz into
                # "2 SD"
                sd = max(d["centroid_sd"] or 0.0, CENTROID_SD_FLOOR * d["centroid_mean"])
                cen_z = (m["centroid_hz"] - d["centroid_mean"]) / sd
                if abs(cen_z) > 2:
                    g5.append(f"spectral centroid {cen_z:+.1f} SD from the project mean (2 allowed)")
            if g5:
                fails += ["gate 5: " + x for x in g5]
                why.add("drift")
            gates["5"] = "fail" if g5 else "pass"
            score += abs(rate_dev) * 10 + (abs(loud_dev) / 2 if loud_dev is not None else 0) + (
                abs(cen_z) * 0.5 if cen_z is not None else 0)
        else:
            gates["5"] = "skip (needs 5 chunks of 3 s or more)"
        if m["clipped"]:
            flags.append("gate 6: clipping (peak count at full scale)")
            gates["6"] = "flag"
            score += 5
        else:
            gates["6"] = "pass"
    if asr is not None:
        if asr.get("fails"):
            fails += ["gate 4: " + x for x in asr["fails"]]
            why.add("asr")
            gates["4"] = "fail"
        else:
            gates["4"] = "pass"
        score += (asr.get("error_rate") or 0) * 20
    else:
        gates["4"] = "skip (run with --asr)"
    score += 100.0 * len([f for f in fails if not f.startswith("gate 1")])
    result = "fail" if fails else ("flag" if flags else "pass")
    return {"result": result, "fails": fails, "flags": flags, "gates": gates, "score": round(score, 3),
            "reroll": bool(why & RE_ROLLABLE) and fc != "blocked",
            "measures": {"ratio": rnd(ratio), "rate_dev": rnd(rate_dev), "loudness_dev": rnd(loud_dev),
                         "centroid_z": rnd(cen_z), "wps_ref": rnd(ref["wps"]), "wps_source": ref["wps_source"],
                         "gate2_window": list(GATE2_WINDOW if ref.get("calibrated", True) else GATE2_WINDOW_PRESET)}}


# ------------------------------------------------------------------------------------------------ ASR check (gate 4)

def norm_tokens(text: str, bn: bool) -> list:
    """Lower case, punctuation stripped, Bengali digits folded, numbers spelled out, hyphens split."""
    text = nfc(text or "")
    text = TAG_RX.sub(" ", text)
    if bn:
        text = BN_RX.sub(lambda m: bn_number_match(m), text)
    else:
        text = EN_RX.sub(lambda m: en_number_match(m), text)
    text = text.translate(DIGIT_FOLD).lower().replace("-", " ")
    text = "".join(ch if (ch.isalnum() or unicodedata.category(ch).startswith("M") or ch.isspace()) else " "
                   for ch in text)
    return text.split()


def edit_distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, y in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y))
        prev = cur
    return prev[-1]


def asr_check(ch: dict, transcript: str) -> dict:
    """Gate 4 from a transcript: WER (English, 3%) or CER (Bangla, 5%), words missing or extra at the end,
    direction words heard, lexicon terms not heard."""
    bn = is_bn(ch["spoken"])
    ref = norm_tokens(ch["spoken"], bn)
    hyp = norm_tokens(transcript, bn)
    fails = []
    if bn:
        a, b = list("".join(ref)), list("".join(hyp))
        rate = edit_distance(a, b) / max(1, len(a))
        if rate > 0.05:
            fails.append(f"character error rate {rate * 100:.1f}% (5% allowed)")
    else:
        rate = edit_distance(ref, hyp) / max(1, len(ref))
        if rate > 0.03:
            fails.append(f"word error rate {rate * 100:.1f}% (3% allowed)")
    sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
    blocks = [bk for bk in sm.get_matching_blocks() if bk.size]
    if blocks:
        last = blocks[-1]
        missing = len(ref) - (last.a + last.size)
        extra = len(hyp) - (last.b + last.size)
        if missing > 0:
            fails.append(f"{missing} word(s) missing at the end: {' '.join(ref[-missing:])}")
        if extra > 0:
            fails.append(f"{extra} extra word(s) at the end: {' '.join(hyp[-extra:])}")
    elif ref:
        fails.append("nothing of the script was heard")
    leak_words = set()
    for w in re.findall(r"[a-z]{4,}", (ch["style"] or "").lower()):
        leak_words.add(w)
    for t in ch.get("tags") or []:
        leak_words.update(t.split())
    leak_words.update({"style", "transcript", "performance", "synthesize", "narration", "director"})
    leak_words -= set(ref)
    heard = sorted(w for w in leak_words if w in hyp)
    if heard:
        fails.append("direction words spoken: " + ", ".join(heard))
    compact_h = re.sub(r"[\W_]+", "", " ".join(hyp))
    for display, spoken in ch.get("lexicon_terms") or []:
        forms = [re.sub(r"[\W_]+", "", " ".join(norm_tokens(x, bn))) for x in (spoken, display)]
        if not any(f and f in compact_h for f in forms):
            fails.append(f"lexicon term not heard: {display} ({spoken})")
    return {"fails": fails, "error_rate": round(rate, 4), "metric": "cer" if bn else "wer"}


def transcribe_cached(path: Path, key: str, bangla: bool, lang: str, project: Path, command: str,
                      label: str) -> dict:
    """gemini-3.5-transcribe of one file, cached next to the master (paid once), logged in the ledger. Bangla is
    sent without a language code: the model then follows code-switched English by itself."""
    side = cache_dir() / f"{key}.asr.json"
    got = read_json(side)
    if isinstance(got, dict) and got.get("model") == TRANSCRIBE_MODEL:
        return got
    dur = probe_duration(path) or 0.0
    codes = None if bangla or not lang else [lang]
    t0 = time.time()
    try:
        res = G.transcribe(str(path), language_codes=codes, words=True, model=TRANSCRIBE_MODEL)
    except G.GeminiError as err:
        ledger(project, {"time": now_iso(), "command": command, "chunk": label, "model": TRANSCRIBE_MODEL,
                         "units": {"audio_s": round(dur, 2)}, "est_usd": 0.0, "key_source": None,
                         "result": "error:" + err.kind, "message": G.scrub(str(err))[:300]})
        raise
    out = {"model": TRANSCRIBE_MODEL, "text": res["text"], "words": res["words"], "usage": res.get("usage"),
           "created": now_iso()}
    ledger(project, {"time": now_iso(), "command": command, "chunk": label, "model": TRANSCRIBE_MODEL,
                     "units": {"audio_s": round(dur, 2)}, "est_usd": round(asr_usd(dur), 6),
                     "key_source": (res.get("info") or {}).get("key"), "usage": res.get("usage"), "result": "ok",
                     "seconds": round(time.time() - t0, 2)})
    write_json(side, out)
    return out


# ------------------------------------------------------------------------------------------------ project state

def load_state(project: Path) -> dict:
    st = read_json(project / "takes.json")
    if not isinstance(st, dict) or st.get("schema") != "nexa-speech/takes-1":
        st = {"schema": "nexa-speech/takes-1", "chunks": {}}
    return st


def save_state(project: Path, st: dict) -> None:
    st["updated"] = now_iso()
    write_json(project / "takes.json", st)


def load_plan(project: Path) -> dict:
    plan = read_json(project / "plan.json")
    if not isinstance(plan, dict) or plan.get("schema") != "nexa-speech/plan-1":
        die(f"{project} has no plan.json from nexa-speech: run render first")
    return plan


def calibration(project: Path) -> dict:
    got = read_json(project / "calibration.json", {}) or {}
    return got.get("profiles", {}) if isinstance(got, dict) else {}


def write_plan_file(project: Path, plan: dict) -> Path:
    path = project / "plan.json"
    if not own_file(path, "nexa-speech/plan"):
        die(f"{path} exists and was not written by nexa-speech: pick another folder (nothing was changed)")
    write_json(path, plan)
    return path


# ------------------------------------------------------------------------------------------------ render

def gather(plan: dict, state: dict, project: Path) -> dict:
    """Every take this project has for its chunks (from the cache or earlier runs), analysed. {key: metrics}."""
    todo = []
    for ch in plan["chunks"]:
        entry = state["chunks"].setdefault(ch["base_key"], {"takes": {}})
        entry["id"] = ch["id"]
        for t in list(entry["takes"]):
            rec = entry["takes"][t]
            # the master and its sidecar in both places (a project moved to another machine refills the cache)
            if cached_take(ch, int(t), project) is None:
                log(f"{ch['id']} take {t}: its master is gone from the project and the cache; dropped")
                del entry["takes"][t]
        known = max([int(x) for x in entry["takes"]] or [0])
        for t in range(1, 13):
            if str(t) in entry["takes"]:
                continue
            rec = cached_take(ch, t, project)
            if rec is None:
                if t > known:
                    break
                continue
            entry["takes"][str(t)] = rec
            known = max(known, t)
        for rec in entry["takes"].values():
            todo.append(rec["key"])
    metrics = {}
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        for key, m in zip(todo, pool.map(lambda k: analysis_for(project, k), todo)):
            metrics[key] = m
    return metrics


def choose(ch: dict, entry: dict, metrics: dict, refs: dict, asr: dict = None) -> dict:
    """Evaluate every take of a chunk and pick one: a hand pick stays; otherwise the best gate score."""
    evals = {}
    for t, rec in entry["takes"].items():
        evals[t] = evaluate(ch, rec, metrics.get(rec["key"]), refs[ch["profile"]],
                            (asr or {}).get(rec["key"]))
    if not evals:
        return {}
    if entry.get("chosen_by") == "pick" and str(entry.get("chosen")) in evals:
        best = str(entry["chosen"])
    else:
        best = min(evals, key=lambda t: (evals[t]["score"], int(t)))
        entry["chosen"] = int(best)
        entry["chosen_by"] = ("best of %d takes" % len(evals)) if len(evals) > 1 else "gates"
    entry["result"] = evals[best]["result"]
    entry["fails"] = evals[best]["fails"]
    entry["flags"] = evals[best]["flags"]
    entry["gates"] = evals[best]["gates"]
    entry["measures"] = evals[best]["measures"]
    entry["score"] = evals[best]["score"]
    return evals


def render_project(plan: dict, project: Path, command: str, budget: float, min_takes: int = 0, only: set = None,
                   asr: bool = False, ledger_dir: Path = None) -> dict:
    """Synthesise what is not cached, run the gates, one automatic re-roll per chunk, the ledger. Returns a summary.

    A chunk is decided once it has been through the gates with its re-roll; a later render never re-rolls it again
    by itself (so a second render of the same script makes no call), only `--takes N` or `--only` asks for more."""
    project.mkdir(parents=True, exist_ok=True)
    (project / "masters").mkdir(exist_ok=True)
    state = load_state(project)
    calib = calibration(project)
    chunks = [c for c in plan["chunks"] if not only or c["id"] in only]
    gather(plan, state, project)
    jobs, queued = [], set()
    for ch in chunks:
        entry = state["chunks"][ch["base_key"]]
        for t in range(1, max(ch["takes"], min_takes or 0) + 1):
            # the same words twice in a script share one key: one call serves both chunks
            if str(t) not in entry["takes"] and (ch["base_key"], t) not in queued:
                queued.add((ch["base_key"], t))
                jobs.append((ch, t))
    est = sum(take_cost(ch) for ch, _ in jobs)
    if asr:
        est += sum(asr_usd(ch["est_s"]) * max(ch["takes"], min_takes or 0) for ch in chunks)
    if est > budget + 1e-9:
        raise BudgetError(est, budget, len(jobs))
    if jobs:
        for name, p in plan["profiles"].items():
            days = voice_days_left(p)
            if days is not None and days < 0 and any(ch["profile"] == name for ch, _ in jobs):
                raise ToolError(f"profile {name}: the designed voice {p['voice']['id']} expired; cached chunks still "
                                "work, but new ones need a new voice (design, then design keep)")
            if days is not None and days < EXPIRY_WARN_DAYS:
                log(f"profile {name}: the designed voice expires in {days:.0f} days")
    recs, fails, stopped = run_jobs(jobs, project, command, ledger_dir) if jobs else ({}, [], None)
    fails += keep_takes(state, recs, chunks)
    calls = len(recs)
    spent = sum(take_cost(ch) for ch, t in jobs if (ch["base_key"], t) in recs)
    save_state(project, state)
    metrics = gather(plan, state, project)
    asr_results = (run_asr(plan, state, project, command, chunks, max_take=min_takes or 0)
                   if asr and stopped is None else {})
    refs = references(plan, state, metrics, calib)
    rerolls, reroll_notes, allowed = [], [], []
    for ch in chunks:
        entry = state["chunks"][ch["base_key"]]
        if not entry["takes"]:
            continue
        evals = choose(ch, entry, metrics, refs, asr_results)
        best = evals[str(entry["chosen"])]
        if (best["result"] == "fail" and best["reroll"] and not entry.get("decided") and not entry.get("auto_reroll")
                and entry.get("chosen_by") != "pick"
                and int(plan["profiles"][ch["profile"]]["takes"]["max_auto_reroll"]) >= 1
                and ch["base_key"] not in {c["base_key"] for c, _, _ in rerolls}):
            rerolls.append((ch, max(int(t) for t in entry["takes"]) + 1, best["fails"]))
    if rerolls and stopped is None:
        for ch, t, why in rerolls:
            cost = take_cost(ch)
            if spent + cost > budget + 1e-9:
                reroll_notes.append({"chunk": ch["id"], "note": f"re-roll skipped: the budget (${budget:.2f}) is "
                                                                "used up"})
                continue
            spent += cost
            allowed.append((ch, t))
            log(f"{ch['id']}: re-roll (take {t}) because {why[0]}")
        rr, rfails, rstop = run_jobs(allowed, project, command, ledger_dir) if allowed else ({}, [], None)
        fails += rfails
        stopped = stopped or rstop
        for rec in rr.values():
            rec["reroll"] = True
        fails += keep_takes(state, rr, chunks)
        calls += len(rr)
        spent -= sum(take_cost(ch) for ch, t in allowed if (ch["base_key"], t) not in rr)
        metrics = gather(plan, state, project)
        if asr and stopped is None:
            asr_results.update(run_asr(plan, state, project, command, [ch for ch, _ in allowed]))
        for ch, t in allowed:
            entry = state["chunks"][ch["base_key"]]
            entry["auto_reroll"] = True
            choose(ch, entry, metrics, refs, asr_results)
    skipped = {n["chunk"] for n in reroll_notes}
    for ch in chunks:
        entry = state["chunks"][ch["base_key"]]
        if entry["takes"] and ch["id"] not in skipped and stopped is None:
            entry["decided"] = True
    save_state(project, state)
    update_calibration(project, plan, state, metrics)
    write_qa(project, plan, state, metrics, refs, asr_results)
    missing = [c["id"] for c in plan["chunks"] if not state["chunks"][c["base_key"]]["takes"]]
    flagged = [c["id"] for c in chunks if state["chunks"][c["base_key"]].get("result") == "fail"]
    # how many takes each flagged chunk has: --takes N asks for N in all, so a new take needs more than this
    have = {c["id"]: len(state["chunks"][c["base_key"]]["takes"]) for c in chunks if c["id"] in flagged}
    return {"chunks": len(plan["chunks"]), "rendered": len(chunks), "calls": calls, "est_usd": round(spent, 5),
            "flagged_takes": have,
            "rerolls": [{"chunk": ch["id"], "take": t, "why": why[0]} for ch, t, why in rerolls
                        if (ch, t) in allowed],
            "reroll_notes": reroll_notes, "failures": fails, "stopped": explain(stopped) if stopped else None,
            "stop_kind": stopped.kind if stopped else None, "missing": missing, "flagged": flagged,
            "budget": budget}


def keep_takes(state: dict, recs: dict, chunks: list) -> list:
    """Store the takes that brought audio; an answer without audio (a refusal, an empty answer) is reported instead
    and never stored, so the next render asks again (once)."""
    ids = {c["base_key"]: c["id"] for c in chunks}
    fails = []
    for (base, t), rec in recs.items():
        if rec.get("file"):
            state["chunks"][base]["takes"][str(t)] = rec
            continue
        why = rec.get("finish") or rec.get("status") or "no reason given"
        msg = (f"refused ({why}): rephrase or shorten the line, or try the other voice once; it is never retried "
               "automatically") if rec.get("finish_class") == "blocked" else (
            f"no audio came back ({why}); the answer is logged in the ledger; run render again to ask once more")
        fails.append({"chunk": ids.get(base), "take": t, "kind": rec.get("finish_class"), "message": msg})
    return fails


class BudgetError(Exception):
    def __init__(self, est, budget, calls):
        shown = f"{budget:.2f}" if budget >= 0.01 else f"{budget:g}"
        super().__init__(f"the estimate ${est:.4f} for {calls} call(s) is over the budget ${shown}: raise it "
                         f"with --budget {math.ceil(est * 100) / 100:.2f} (nothing was called)")
        self.est, self.budget, self.calls = est, budget, calls


def run_asr(plan: dict, state: dict, project: Path, command: str, chunks: list, chosen_only: bool = False,
            max_take: int = None) -> dict:
    """Transcribe takes (every take, or only the chosen one) that have no transcript yet, in parallel;
    {master_key: asr_check result}. Bangla goes without a language code, so code-switched English is kept."""
    todo = []
    for ch in chunks:
        entry = state["chunks"].get(ch["base_key"]) or {}
        recs = list(entry.get("takes", {}).values())
        if max_take is not None:
            limit = max(ch["takes"], max_take)
            recs = [r for t, r in entry.get("takes", {}).items() if int(t) <= limit]
        if chosen_only and entry.get("chosen"):
            recs = [entry["takes"][str(entry["chosen"])]]
        for rec in recs:
            if (project / "masters" / f"{rec['key']}.wav").exists():
                todo.append((ch, rec))

    def one(item):
        ch, rec = item
        tr = transcribe_cached(project / "masters" / f"{rec['key']}.wav", rec["key"], is_bn(ch["spoken"]),
                               ch["language"], project, command, ch["id"])
        res = asr_check(ch, tr["text"])
        res["transcript"] = tr["text"]
        return rec["key"], res
    out = {}
    with cf.ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        for key, res in pool.map(one, todo):
            out[key] = res
    return out


def update_calibration(project: Path, plan: dict, state: dict, metrics: dict) -> None:
    by = {}
    for ch in plan["chunks"]:
        entry = state["chunks"].get(ch["base_key"]) or {}
        if entry.get("result") not in ("pass", "flag") or not entry.get("chosen"):
            continue
        m = metrics.get((entry["takes"].get(str(entry["chosen"])) or {}).get("key"))
        if m and not m.get("empty") and ch["n_words"] >= 4 and m["voiced_s"] >= 0.8:
            by.setdefault(ch["profile"], []).append(ch["n_words"] / m["voiced_s"])
    cal = read_json(project / "calibration.json", {}) or {}
    profs = cal.get("profiles", {}) if isinstance(cal, dict) else {}
    changed = False
    for name, rates in by.items():
        if len(rates) >= 3:
            profs[name] = {"measured_wps": round(statistics.median(rates), 3), "chunks": len(rates),
                           "updated": now_iso()}
            changed = True
    if changed:
        write_json(project / "calibration.json", {"schema": "nexa-speech/calibration-1", "profiles": profs})


def write_qa(project: Path, plan: dict, state: dict, metrics: dict, refs: dict, asr_results: dict) -> dict:
    rows = []
    for ch in plan["chunks"]:
        entry = state["chunks"].get(ch["base_key"]) or {}
        if not entry.get("takes"):
            rows.append({"chunk": ch["id"], "take": None, "result": "missing", "fails": ["no take yet"], "flags": []})
            continue
        rec = entry["takes"].get(str(entry.get("chosen"))) or {}
        m = metrics.get(rec.get("key")) or {}
        row = {"chunk": ch["id"], "scene": ch["scene"], "profile": ch["profile"], "take": entry.get("chosen"),
               "takes": len(entry["takes"]), "chosen_by": entry.get("chosen_by"), "master_key": rec.get("key"),
               "result": entry.get("result"), "fails": entry.get("fails", []), "flags": entry.get("flags", []),
               "gates": entry.get("gates", {}), "measures": entry.get("measures", {}),
               "words": ch["n_words"], "voiced_s": m.get("voiced_s"), "duration_s": m.get("duration_s"),
               "loudness_i": m.get("loudness_i"), "centroid_hz": m.get("centroid_hz")}
        if rec.get("key") in asr_results:
            row["transcript"] = asr_results[rec["key"]].get("transcript")
        rows.append(row)
    qa = {"schema": "nexa-speech/qa-1", "skill_version": SKILL_VERSION, "created": now_iso(),
          "references": refs, "speaker_similarity": "not measured: it needs a speaker-embedding model; listen instead",
          "chunks": rows,
          "summary": {k: sum(1 for r in rows if r["result"] == k) for k in ("pass", "flag", "fail", "missing")}}
    write_json(project / "qa.json", qa)
    return qa


def qa_lines(qa: dict) -> list:
    lines = [f"{'chunk':6} {'take':>4} {'words':>5} {'voiced':>7} {'ratio':>5} {'LUFS':>6} {'rate':>5}  result"]
    for r in qa["chunks"]:
        ms = r.get("measures") or {}
        rate = ms.get("rate_dev")
        lines.append(f"{r['chunk']:6} {str(r.get('take') or '-'):>4} {str(r.get('words') or '-'):>5} "
                     f"{(str(r.get('voiced_s')) + 's') if r.get('voiced_s') is not None else '-':>7} "
                     f"{ms.get('ratio') if ms.get('ratio') is not None else '-':>5} "
                     f"{r.get('loudness_i') if r.get('loudness_i') is not None else '-':>6} "
                     f"{(('%+.0f%%' % (rate * 100)) if rate is not None else '-'):>5}  {r['result']}"
                     + ("  " + "; ".join(r.get("fails", []) + r.get("flags", [])) if r.get("fails") or r.get("flags")
                        else ""))
    s = qa["summary"]
    lines.append(f"{s['pass']} pass, {s['flag']} flagged, {s['fail']} failing, {s['missing']} missing")
    return lines


# ------------------------------------------------------------------------------------------------ master

def process_chunk(src: Path, m: dict, gain_db: float, tempo: float, out: Path) -> dict:
    """Trim to 60 ms before the first sound and 150 ms after the last, stretch, fade, gain; raw float at 24 kHz.
    Returns where the first and last sound sit in the processed samples."""
    start = max(0.025 if m.get("click") else 0.0, m["first_sound"] - LEAD_S)   # a click at the start is cut off
    end = min(m["duration_s"], m["last_sound"] + TAIL_S)
    length = (end - start) / tempo
    chain = [f"atrim=start={start:.5f}:end={end:.5f}", "asetpts=PTS-STARTPTS"]
    if abs(tempo - 1.0) > 1e-4:
        chain.append(f"atempo={tempo:.5f}")
    chain += [f"afade=t=in:st=0:d={FADE_IN_S}", f"afade=t=out:st={max(0.0, length - FADE_OUT_S):.5f}:d={FADE_OUT_S}",
              f"volume={gain_db:.3f}dB"]
    ff(["-v", "error", "-y", "-i", src, "-af", ",".join(chain), "-ar", str(CANVAS_RATE), "-ac", "1", "-f", "f32le",
        "-c:a", "pcm_f32le", out])
    a = read_f32(out)
    thr = 10 ** ((m.get("threshold_db") or -45.0) / 20.0) * 10 ** (gain_db / 20.0)
    exp_first = int(round((m["first_sound"] - start) / tempo * CANVAS_RATE))
    exp_last = int(round((m["last_sound"] - start) / tempo * CANVAS_RATE))
    win = int(0.03 * CANVAS_RATE)
    lo, hi = max(0, exp_first - win), min(len(a), exp_first + win)
    first = next((k for k in range(lo, hi) if abs(a[k]) > thr), min(max(exp_first, 0), max(0, len(a) - 1)))
    lo, hi = max(0, exp_last - win), min(len(a), exp_last + win)
    last = next((k for k in range(hi - 1, lo - 1, -1) if abs(a[k]) > thr), min(max(exp_last, 0), max(0, len(a) - 1)))
    last = max(last, first + 1)
    return {"samples": len(a), "first": first, "last": last}


_PINK_RMS = {}


def pink_rms_db(highpass_hz: int) -> float:
    """The RMS level of ffmpeg's pink noise at amplitude 1 after the chain's high-pass (measured once per cut-off):
    the room tone then sits at room_tone_dbfs after the clean-up, not 3 dB under it."""
    if highpass_hz not in _PINK_RMS:
        r = ff(["-v", "info", "-f", "lavfi", "-i", "anoisesrc=color=pink:r=24000:a=1:seed=7:d=5", "-af",
                f"highpass=f={highpass_hz},astats=measure_perchannel=none:measure_overall=RMS_level", "-f", "null",
                "-"], check=False)
        m = re.findall(r"RMS level dB:\s*(-?[0-9.]+)", r.stderr or "")
        _PINK_RMS[highpass_hz] = float(m[-1]) if m else -17.0
    return _PINK_RMS[highpass_hz]


def file_rms_db(path: Path, highpass_hz: int):
    r = ff(["-v", "info", "-i", path, "-af", f"highpass=f={highpass_hz},astats=measure_perchannel=none:"
                                             "measure_overall=RMS_level", "-f", "null", "-"], check=False)
    m = re.findall(r"RMS level dB:\s*(-?[0-9.]+)", r.stderr or "")
    return float(m[-1]) if m else None


def pre_chain(post: dict) -> str:
    parts = [f"highpass=f={int(post.get('highpass_hz') or 70)}", "equalizer=f=250:t=q:w=1:g=-1.5"]
    if float(post.get("deess") or 0) > 0:
        parts.append(f"deesser=i={min(1.0, float(post['deess'])):.2f}")
    parts.append("acompressor=threshold=-20dB:ratio=2:attack=10:release=150")
    return ",".join(parts)


def build_pre(canvas: Path, seconds: float, post: dict, out: Path, work: Path) -> dict:
    """The joined voice with its room tone under it and the gentle clean-up chain, as raw float at 24 kHz."""
    tone = post.get("room_tone") or "pink"
    target = float(post.get("room_tone_dbfs") or -65.0)
    inp = ["-f", "f32le", "-ar", str(CANVAS_RATE), "-ac", "1", "-i", canvas]
    chain = pre_chain(post)
    info = {"room_tone": tone, "room_tone_dbfs": target}
    if tone == "none":
        ff(["-v", "error", "-y", *inp, "-af", chain, "-f", "f32le", "-c:a", "pcm_f32le", out])
        return info
    hp = int(post.get("highpass_hz") or 70)
    if tone == "pink":
        gain = target - pink_rms_db(hp)
        src = ["-f", "lavfi", "-i", f"anoisesrc=color=pink:r={CANVAS_RATE}:a=1:seed=7:d={seconds + 1:.3f}"]
    else:
        path = Path(str(tone)).expanduser()
        if not path.exists():
            raise ToolError(f"room tone file {path} is missing (post.room_tone in the profile)")
        rms = file_rms_db(path, hp)
        gain = target - (rms if rms is not None else target)
        src = ["-stream_loop", "-1", "-i", path]
        info["file"] = str(path)
    graph = (f"[1:a]aformat=sample_fmts=flt:sample_rates={CANVAS_RATE}:channel_layouts=mono,volume={gain:.2f}dB[rt];"
             f"[0:a][rt]amix=inputs=2:normalize=0:duration=first[mix];[mix]{chain}[out]")
    ff(["-v", "error", "-y", *inp, *src, "-filter_complex", graph, "-map", "[out]", "-f", "f32le", "-c:a",
        "pcm_f32le", out])
    return info


def _loudnorm_json(stderr: str) -> dict:
    found = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr or "")
    if not found:
        raise ToolError("loudnorm printed no measurement")
    return json.loads(found[-1])


def finish_loudness(pre: Path, rate: int, target: dict, out: Path) -> dict:
    """Two-pass loudnorm in linear mode to the target; a limiter first when the gain would push the true peak over;
    pass 2's report must say linear (else the ceiling goes down and it runs again); resample to 48 kHz, 24-bit;
    verified with ebur128. Raises ToolError rather than ship a dynamic-mode result."""
    I, TP = float(target["stem_I"]), float(target["TP"])
    lra = float(target["LRA"])
    inp = ["-f", "f32le", "-ar", str(rate), "-ac", "1", "-i", pre]
    limit_db, tp_goal, i_goal = None, TP, I
    history = []
    for attempt in range(8):
        lim = (f"alimiter=limit={10 ** (limit_db / 20.0):.6f}:level=disabled:latency=1:attack=5:release=50,"
               if limit_db is not None else "")
        r = ff(["-v", "info", *inp, "-af", f"{lim}loudnorm=I={i_goal:.2f}:TP={tp_goal:.2f}:LRA={lra:.1f}:"
                                            "print_format=json", "-f", "null", "-"], check=False)
        m1 = _loudnorm_json(r.stderr)
        mi, mtp, mlra = float(m1["input_i"]), float(m1["input_tp"]), float(m1["input_lra"])
        if mi <= -69.0:
            raise ToolError("the voice-over is silent: nothing to normalise")
        gain = i_goal - mi
        if mtp + gain > tp_goal - 0.2:
            # limiter first: a sample-peak ceiling before the gain, with room for the true-peak overshoot; lower it
            # further when the last ceiling was not enough
            ceiling = tp_goal - gain - 0.8
            if limit_db is not None:
                ceiling = min(ceiling, limit_db - 0.5)
            if limit_db is not None and limit_db <= -24.0:
                raise ToolError("the peaks cannot be brought under the true-peak target: lower loudness.stem_I")
            limit_db = max(-24.0, ceiling)
            history.append({"attempt": attempt + 1, "limiter_db": round(limit_db, 2), "why": "peak over the target"})
            continue
        use_lra = max(lra, min(50.0, mlra + 0.1))
        ln = (f"loudnorm=I={i_goal:.2f}:TP={tp_goal:.2f}:LRA={use_lra:.1f}:measured_I={m1['input_i']}:"
              f"measured_TP={m1['input_tp']}:measured_LRA={m1['input_lra']}:measured_thresh={m1['input_thresh']}:"
              f"offset={m1['target_offset']}:linear=true:print_format=json")
        r2 = ff(["-v", "info", "-y", *inp, "-af", f"{lim}{ln},{RESAMPLE_48K}", "-ar", "48000", "-c:a", "pcm_s24le",
                 out], check=False)
        if r2.returncode != 0:
            raise ToolError(f"ffmpeg failed in the loudness pass: {(r2.stderr or '')[-500:]}")
        m2 = _loudnorm_json(r2.stderr)
        if m2.get("normalization_type") != "linear":
            limit_db = (limit_db if limit_db is not None else tp_goal - gain - 0.8) - 1.0
            history.append({"attempt": attempt + 1, "limiter_db": round(limit_db, 2), "why": "pass 2 was dynamic"})
            continue
        v = loudness(["-i", str(out)])
        if v["TP"] is not None and v["TP"] > TP:
            tp_goal -= (v["TP"] - TP) + 0.1
            history.append({"attempt": attempt + 1, "why": f"true peak {v['TP']} over {TP}"})
            continue
        if v["I"] is not None and abs(v["I"] - I) > 0.5:
            i_goal += I - v["I"]
            history.append({"attempt": attempt + 1, "why": f"integrated {v['I']} off {I}"})
            continue
        return {"I": v["I"], "TP": v["TP"], "LRA": v["LRA"], "normalization": "linear", "target": dict(target),
                "limiter_db": rnd(limit_db, 2), "loudnorm_lra": use_lra, "input_lra": mlra, "passes": attempt + 1,
                "history": history}
    raise ToolError("loudness could not be finished in linear mode after 8 tries (nothing shipped as dynamic): "
                    "lower loudness.stem_I or the peaks, then run master again")


def master_project(project: Path, overrides: dict = None) -> dict:
    """The finished voice-over: every chunk's chosen take trimmed, gain-matched and placed with exact gaps over one
    room tone, then the finishing chain; vo_48k.wav and vo.manifest.json."""
    need_filters()
    plan = load_plan(project)
    state = load_state(project)
    main = plan["profiles"][plan["main_profile"]]
    if overrides is None:
        fit_file = read_json(project / "fit.json")
        if isinstance(fit_file, dict) and fit_file.get("script_sha") == plan.get("script_sha"):
            overrides = fit_file
    overrides = overrides or {}
    chosen = []
    for ch in plan["chunks"]:
        entry = state["chunks"].get(ch["base_key"]) or {}
        if not entry.get("chosen") or str(entry["chosen"]) not in entry.get("takes", {}):
            raise ToolError(f"{ch['id']} has no take yet: run render first")
        rec = entry["takes"][str(entry["chosen"])]
        m = analysis_for(project, rec["key"])
        if m.get("empty"):
            raise ToolError(f"{ch['id']} take {entry['chosen']} holds no sound: pick another take or re-render it")
        chosen.append((ch, entry, rec, m))
    loud = [m["loudness_i"] for _, _, _, m in chosen if m.get("loudness_i") is not None]
    med = statistics.median(loud) if loud else None
    work = project / "work"
    (work / "chunks").mkdir(parents=True, exist_ok=True)
    tempos = (overrides.get("tempo") or {})
    gap_over = (overrides.get("gaps") or {})

    def proc(item):
        ch, entry, rec, m = item
        gain = 0.0 if med is None or m.get("loudness_i") is None else max(-12.0, min(12.0, med - m["loudness_i"]))
        tempo = float(tempos.get(ch["scene"], 1.0))
        out = work / "chunks" / f"{ch['id']}-{rec['key']}.f32"
        info = process_chunk(project / "masters" / f"{rec['key']}.wav", m, gain, tempo, out)
        info.update({"path": out, "gain_db": round(gain, 2), "tempo": tempo})
        return info
    with cf.ThreadPoolExecutor(max_workers=4) as pool:
        procs = list(pool.map(proc, chosen))
    rate = CANVAS_RATE
    pos = int(round((plan.get("lead_pause_s") or 0.0) * rate + LEAD_S * rate))
    placed = []
    for (ch, entry, rec, m), pr in zip(chosen, procs):
        start = pos - pr["first"]
        if start < 0:
            pos -= start
            start = 0
        first_abs = start + pr["first"]
        last_abs = start + pr["last"]
        gap = float(gap_over.get(ch["id"], ch["gap_after"]["s"]))
        placed.append((ch, entry, rec, m, pr, start, first_abs, last_abs, gap))
        pos = last_abs + int(round(gap * rate))
    end_pos = max(p[5] + p[4]["samples"] for p in placed)
    total = max(end_pos, placed[-1][7] + int(round((placed[-1][8] + 0.5) * rate)))
    canvas = array("f", bytes(4 * total))
    prev_end = 0
    for ch, entry, rec, m, pr, start, first_abs, last_abs, gap in placed:
        a = read_f32(pr["path"])
        n = min(len(a), total - start)
        overlap = max(0, min(prev_end, start + n) - start)   # a short gap: this lead-in lies on the last tail
        for k in range(overlap):
            canvas[start + k] += a[k]
        if n > overlap:
            canvas[start + overlap:start + n] = a[overlap:n]
        prev_end = max(prev_end, start + n)
    canvas_path = work / "canvas.f32"
    write_f32(canvas_path, canvas)
    del canvas
    pre = work / "pre.f32"
    tone = build_pre(canvas_path, total / float(rate), main["post"], pre, work)
    out = project / "vo_48k.wav"
    fin = finish_loudness(pre, rate, main["loudness"], out)
    manifest = build_manifest(project, plan, placed, fin, tone, overrides, out)
    write_json(project / "vo.manifest.json", manifest)
    # the raw float files this run wrote are only steps on the way (about 100 MB for 10 minutes): remove them
    for path in [canvas_path, pre] + [pr["path"] for pr in procs]:
        try:
            Path(path).unlink()
        except OSError:
            pass
    return manifest


def match_boundaries(start: float, end: float, weights: list, pauses: list) -> list:
    """Split [start, end] into len(weights) parts at pauses: each boundary goes to the pause nearest its expected
    place (longer pauses preferred), in order; a boundary with no pause near it stays at the expected place."""
    k = len(weights)
    if k <= 1:
        return [(start, end)]
    inner = [(a, b) for a, b in pauses if b is not None and a > start + 0.03 and b < end - 0.03]
    total = float(sum(weights)) or 1.0
    exp, acc = [], 0.0
    for w in weights[:-1]:
        acc += w
        exp.append(start + (end - start) * acc / total)
    reach = max(1.5, 0.4 * (end - start))
    nb, npz = len(exp), len(inner)
    INF = math.inf
    cost = [[INF] * (npz + 1) for _ in range(nb + 1)]
    back = [[None] * (npz + 1) for _ in range(nb + 1)]
    for j in range(npz + 1):
        cost[0][j] = 0.0
    for i in range(1, nb + 1):
        for j in range(npz + 1):
            best, arg = cost[i - 1][j] + 2.0, (i - 1, j, None)   # no pause for this boundary: only when none is near
            if j > 0 and cost[i][j - 1] < best:
                best, arg = cost[i][j - 1], (i, j - 1, "skip")
            if j > 0:
                a, b = inner[j - 1]
                mid = (a + b) / 2
                if abs(mid - exp[i - 1]) <= reach and cost[i - 1][j - 1] < INF:
                    c = cost[i - 1][j - 1] + abs(mid - exp[i - 1]) - 0.3 * min(b - a, 1.0)
                    if c < best:
                        best, arg = c, (i - 1, j - 1, j - 1)
            cost[i][j], back[i][j] = best, arg
    picks = [None] * nb
    i, j = nb, npz
    while i > 0:
        pi, pj, what = back[i][j]
        if what == "skip":
            i, j = pi, pj
            continue
        if what is not None:
            picks[i - 1] = inner[what]
        i, j = pi, pj
    parts, cur = [], start
    for bi in range(nb):
        if picks[bi]:
            a, b = picks[bi]
            parts.append((cur, a))
            cur = b
        else:
            parts.append((cur, exp[bi]))
            cur = exp[bi]
    parts.append((cur, end))
    return parts


def sentence_weight(s: dict) -> float:
    """How long a sentence should take, relatively: its letters plus an allowance of 4 for each word."""
    text = TAG_RX.sub("", s["spoken"])
    return float(max(1, graphemes(re.sub(r"[\W_]+", "", text)) + 4 * len(spoken_words(text))))


def build_manifest(project: Path, plan: dict, placed: list, fin: dict, tone: dict, overrides: dict,
                   out: Path) -> dict:
    rate = CANVAS_RATE
    target_i = float(plan["profiles"][plan["main_profile"]]["loudness"]["stem_I"])
    pauses = silences(["-i", str(out)], target_i - 20.0, 0.15)
    chunks_out, sentences_out = [], []
    for ch, entry, rec, m, pr, start, first_abs, last_abs, gap in placed:
        c0, c1 = first_abs / float(rate), last_abs / float(rate)
        chunks_out.append({"id": ch["id"], "scene": ch["scene"], "profile": ch["profile"], "speaker": ch["speaker"],
                           "mode": ch["mode"], "display": ch["display"], "spoken": ch["spoken"],
                           "start": round(c0, 3), "end": round(c1, 3), "master": f"masters/{rec['key']}.wav",
                           "take": entry["chosen"], "gap_after": {"kind": ch["gap_after"]["kind"], "s": round(gap, 3)},
                           "gain_db": pr["gain_db"], "tempo": pr["tempo"]})
        parts = match_boundaries(c0, c1, [sentence_weight(s) for s in ch["sentences"]], pauses)
        for s, (a, b) in zip(ch["sentences"], parts):
            sentences_out.append({"scene": ch["scene"], "chunk": ch["id"], "text": s["display"], "start": round(a, 3),
                                  "end": round(b, 3)})
    scenes = []
    for sc in plan["scenes"]:
        cs = [c for c in chunks_out if c["scene"] == sc["id"]]
        if cs:
            scenes.append({"id": sc["id"], "title": sc["title"], "start": cs[0]["start"], "end": cs[-1]["end"]})
    entries = [e for e in read_jsonl(project / "ledger.jsonl") if e.get("est_usd")]
    profiles = {n: {"model": p["model"], "voice": p["voice"]["id"], "voice_type": p["voice"].get("type"),
                    "style": p["style"], "version": p["version"], "language": p["language"]}
                for n, p in plan["profiles"].items()}
    dur = probe_duration(out)
    return {"schema": "nexa-speech/manifest-1", "skill_version": SKILL_VERSION, "created": now_iso(),
            "file": "vo_48k.wav", "sample_rate": 48000, "duration_s": rnd(dur),
            "loudness": {"I": fin["I"], "TP": fin["TP"], "LRA": fin["LRA"], "normalization": fin["normalization"],
                         "target": fin["target"], "limiter_db": fin["limiter_db"], "passes": fin["passes"]},
            "post": {"chain": pre_chain(plan["profiles"][plan["main_profile"]]["post"]), "room_tone": tone,
                     "trim": {"lead_s": LEAD_S, "tail_s": TAIL_S, "fade_in_s": FADE_IN_S, "fade_out_s": FADE_OUT_S},
                     "resample": RESAMPLE_48K, "format": "pcm_s24le"},
            "profiles": profiles, "main_profile": plan["main_profile"], "script": plan.get("script"),
            "script_sha": plan.get("script_sha"), "scenes": scenes, "chunks": chunks_out,
            "sentences": sentences_out, "fit": {k: v for k, v in overrides.items() if k in ("tempo", "gaps")} or None,
            "qa": {"flagged": [c["id"] for c, e, *_ in placed if e.get("result") == "fail"]},
            "cost": {"est_usd": round(sum(e["est_usd"] for e in entries), 5), "calls": len(entries),
                     "ledger": "ledger.jsonl", "prices_as_of": PRICES_AS_OF},
            "versions": {"skill": SKILL_VERSION, "ffmpeg": ffmpeg_version()}}


_FFV = None


def ffmpeg_version() -> str:
    global _FFV
    if _FFV is None:
        r = run_cmd([ffmpeg_bin(), "-hide_banner", "-version"], 30, check=False)
        m = re.search(r"ffmpeg version (\S+)", r.stdout or "")
        _FFV = m.group(1) if m else "unknown"
    return _FFV


# ------------------------------------------------------------------------------------------------ align and captions

def word_weight(w: dict) -> float:
    return graphemes(re.sub(r"[\W_]+", "", w["sp"] or w["w"])) + 2.0


def spread_words(s0: float, s1: float, words: list, pauses: list) -> list:
    """Word times inside one sentence: spread by the spoken length over the voiced time, and nudged to a pause within
    150 ms."""
    inner = [(a, b) for a, b in pauses if b is not None and a >= s0 and b <= s1]
    segs, cur = [], s0
    for a, b in inner:
        if a > cur:
            segs.append((cur, a))
        cur = max(cur, b)
    if s1 > cur:
        segs.append((cur, s1))
    voiced = sum(b - a for a, b in segs) or (s1 - s0) or 0.001

    def at(v):
        for a, b in segs:
            if v <= (b - a) + 1e-9:
                return a + v
            v -= (b - a)
        return s1
    weights = [word_weight(w) for w in words]
    total = sum(weights) or 1.0
    bounds, acc = [], 0.0
    for wt in weights[:-1]:
        acc += wt
        bounds.append(at(voiced * acc / total))
    starts, ends = [s0], []
    for p in bounds:
        e, s = p, p
        for a, b in inner:
            if a - 0.15 <= p <= b + 0.15:
                e, s = a, b
                break
        ends.append(e)
        starts.append(s)
    ends.append(s1)
    return [(round(a, 3), round(max(b, a + 0.01), 3)) for a, b in zip(starts, ends)]


def manifest_sentences(plan: dict, manifest: dict) -> list:
    """[(index, manifest sentence, plan sentence)]: the manifest lists each chunk's sentences in plan order."""
    by_chunk = {c["id"]: c for c in plan["chunks"]}
    seen, out = {}, []
    for idx, s in enumerate(manifest["sentences"]):
        ch = by_chunk.get(s["chunk"])
        k = seen.get(s["chunk"], 0)
        seen[s["chunk"]] = k + 1
        if ch is None or k >= len(ch["sentences"]):
            raise ToolError("vo.manifest.json does not match plan.json: run master again")
        out.append((idx, s, ch["sentences"][k]))
    return out


def align_pauses(project: Path, plan: dict, manifest: dict) -> tuple:
    target_i = float(plan["profiles"][plan["main_profile"]]["loudness"]["stem_I"])
    pauses = silences(["-i", str(project / "vo_48k.wav")], target_i - 20.0, 0.15)
    words_out, sents_out = [], []
    for idx, s, sent in manifest_sentences(plan, manifest):
        times = spread_words(s["start"], s["end"], sent["words"], pauses)
        for w, (a, b) in zip(sent["words"], times):
            words_out.append({"w": w["w"], "start": a, "end": b, "sentence": idx, "chunk": s["chunk"],
                              "scene": s["scene"]})
        sents_out.append({"index": idx, "scene": s["scene"], "chunk": s["chunk"], "text": s["text"],
                          "start": s["start"], "end": s["end"]})
    return words_out, sents_out, {"engine": "pauses", "pauses_found": len(pauses)}


def script_tokens(plan: dict, manifest: dict) -> list:
    """The spoken script as normalised tokens, each knowing its sentence, word and display form."""
    script = []
    for idx, s, sent in manifest_sentences(plan, manifest):
        for wi, w in enumerate(sent["words"]):
            toks = norm_tokens(w["sp"] or w["w"], is_bn(w["sp"] or w["w"])) or [""]
            for t in toks:
                script.append({"tok": t, "sent": idx, "wi": wi, "word": w, "s": s})
    return script


def words_from_tokens(script: list, manifest: dict) -> tuple:
    """(words, sentences) once the script tokens carry times: unmatched tokens are placed between their neighbours
    in the same sentence, the display words are carried over, and each sentence spans its words."""
    for i, x in enumerate(script):
        if "t" in x:
            continue
        prev_t = next((script[j]["t"][1] for j in range(i - 1, -1, -1) if "t" in script[j]
                       and script[j]["sent"] == x["sent"]), x["s"]["start"])
        nj = next((j for j in range(i + 1, len(script)) if "t" in script[j] and script[j]["sent"] == x["sent"]), None)
        next_t = script[nj]["t"][0] if nj is not None else x["s"]["end"]
        gap_count = (nj if nj is not None else len(script)) - i
        span = max(0.0, next_t - prev_t) / max(1, gap_count)
        x["t"] = (prev_t, prev_t + span)
        x["interp"] = True
    words_out, sents_out = [], []
    groups = {}
    for x in script:
        groups.setdefault((x["sent"], x["wi"]), []).append(x)
    for (si, wi), xs in sorted(groups.items()):
        a = min(x["t"][0] for x in xs)
        b = max(x["t"][1] for x in xs)
        s = xs[0]["s"]
        words_out.append({"w": xs[0]["word"]["w"], "start": round(a, 3), "end": round(max(b, a + 0.01), 3),
                          "sentence": si, "chunk": s["chunk"], "scene": s["scene"]})
    for idx, s in enumerate(manifest["sentences"]):
        ws = [w for w in words_out if w["sentence"] == idx]
        a = ws[0]["start"] if ws else s["start"]
        b = ws[-1]["end"] if ws else s["end"]
        sents_out.append({"index": idx, "scene": s["scene"], "chunk": s["chunk"], "text": s["text"], "start": a,
                          "end": b})
    return words_out, sents_out


def asr_proxy(project: Path) -> Path:
    proxy = project / "work" / "asr_16k.wav"
    proxy.parent.mkdir(parents=True, exist_ok=True)
    ff(["-v", "error", "-y", "-i", project / "vo_48k.wav", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", proxy])
    return proxy


def align_gemini(project: Path, plan: dict, manifest: dict, budget: float) -> tuple:
    """One transcription of the whole voice-over (word timestamps), the ASR words matched to the script words with
    difflib, the display text carried over, unmatched words placed between their neighbours."""
    dur = manifest.get("duration_s") or probe_duration(project / "vo_48k.wav") or 0.0
    est = asr_usd(dur)
    if est > budget + 1e-9:
        raise BudgetError(est, budget, 1)
    proxy = asr_proxy(project)
    bn = any(is_bn(c["spoken"]) for c in plan["chunks"])
    lang = plan["profiles"][plan["main_profile"]]["language"]
    tr = transcribe_cached(proxy, "vo-" + file_sha(proxy), bn, lang, project, "align", "vo_48k.wav")
    asr_words = [w for w in tr.get("words") or [] if w.get("start") is not None]
    script = script_tokens(plan, manifest)
    matched, close = place_tokens(script, heard_tokens(asr_words, bn))
    words_out, sents_out = words_from_tokens(script, manifest)
    return words_out, sents_out, {"engine": "gemini", "model": TRANSCRIBE_MODEL, "asr_words": len(asr_words),
                                  "script_tokens": len(script), "matched": matched, "close": close,
                                  "matched_share": round((matched + close) / max(1, len(script)), 3),
                                  "est_usd": round(est, 5)}


EL_FA_USD_PER_HOUR = 0.22       # ElevenLabs forced alignment, billed at the Scribe rate (pricing/api, 2026-09-25)


def align_eleven(project: Path, plan: dict, manifest: dict, budget: float) -> tuple:
    """ElevenLabs forced alignment: the spoken script goes up with the audio and every word comes back timed, with
    a per-word loss (high where the voice did not say what the script says). No recogniser guesses, so nothing
    needs matching back except the display forms. ElevenLabs lists the Multilingual v2 languages for it; Bengali
    is not among them, so Bangla is tried and checked, never assumed."""
    dur = manifest.get("duration_s") or probe_duration(project / "vo_48k.wav") or 0.0
    est = dur / 3600.0 * EL_FA_USD_PER_HOUR
    if est > budget + 1e-9:
        raise BudgetError(est, budget, 1)
    proxy = asr_proxy(project)
    script = script_tokens(plan, manifest)
    spoken = " ".join(w["sp"] or w["w"] for _, _, sent in manifest_sentences(plan, manifest) for w in sent["words"])
    t0 = time.time()
    try:
        fa, info = EL.forced_alignment(str(proxy), spoken)
    except EL.ElevenError as err:
        ledger(project, {"time": now_iso(), "command": "align", "model": "elevenlabs-forced-alignment",
                         "est_usd": 0.0, "result": "error:" + err.kind, "message": EL.scrub(str(err))[:300]})
        raise
    ledger(project, {"time": now_iso(), "command": "align", "model": "elevenlabs-forced-alignment",
                     "est_usd": round(est, 5), "key_source": info.get("key"), "result": "ok",
                     "response": EL.cost_headers(info), "seconds": round(time.time() - t0, 2)})
    words = [w for w in (fa.get("words") or []) if isinstance(w, dict) and str(w.get("text") or "").strip()
             and isinstance(w.get("start"), (int, float)) and isinstance(w.get("end"), (int, float))]
    bn = any(is_bn(c["spoken"]) for c in plan["chunks"])
    hyp = []
    for w in words:
        for t in norm_tokens(w["text"], is_bn(w["text"]) or bn) or []:
            hyp.append({"tok": t, "start": float(w["start"]), "end": float(w["end"]), "loss": w.get("loss")})
    matched, close = place_tokens(script, hyp)
    words_out, sents_out = words_from_tokens(script, manifest)
    losses = sorted(float(w["loss"]) for w in words if isinstance(w.get("loss"), (int, float)))
    med = losses[len(losses) // 2] if losses else None
    # a starting rule, to calibrate on the first real files: 4x the median and 0.2 above it
    suspect = [w["text"] for w in words if med is not None and isinstance(w.get("loss"), (int, float))
               and w["loss"] >= max(4 * med, med + 0.2)][:20]
    return words_out, sents_out, {"engine": "elevenlabs", "model": "forced-alignment", "fa_words": len(words),
                                  "script_tokens": len(script), "matched": matched, "close": close,
                                  "matched_share": round((matched + close) / max(1, len(script)), 3),
                                  "loss": fa.get("loss"), "median_word_loss": med, "suspect_words": suspect,
                                  "est_usd": round(est, 5)}


def heard_tokens(asr_words: list, bn: bool) -> list:
    """The recognised words as normalised tokens with their times. Digits are read in the language around them:
    Gemini writes "10" inside Bangla speech that said দশ, and "15" after "iPhone" is fifteen."""
    hyp = []
    texts = [w.get("text") or "" for w in asr_words]
    for i, w in enumerate(asr_words):
        bn_w = is_bn(texts[i]) or (bn and not re.search(r"[A-Za-z]", texts[i]) and any(
            is_bn(texts[j]) for j in (i - 1, i + 1) if 0 <= j < len(texts)))
        for t in norm_tokens(texts[i], bn_w) or []:
            hyp.append({"tok": t, "start": w["start"], "end": w["end"] if w.get("end") is not None else w["start"]})
    return hyp


def place_tokens(script: list, hyp: list) -> tuple:
    """Give each script token ("tok") the time ("t") of the heard token it matches. Returns (exact matches,
    close ones: joined, split or spelled differently); tokens left without "t" are placed by the caller."""
    a_keys = [match_key(x["tok"]) for x in script]
    b_keys = [match_key(x["tok"]) for x in hyp]
    matched = close = 0
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(a=a_keys, b=b_keys, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(a2 - a1):
                script[a1 + k]["t"] = (hyp[b1 + k]["start"], hyp[b1 + k]["end"])
                matched += 1
        elif tag == "replace":
            close += fill_replaced(script[a1:a2], hyp[b1:b2], a_keys[a1:a2], b_keys[b1:b2])
    return matched, close


BN_SPELLING_FOLD = str.maketrans({"\u09c0": "\u09bf", "\u09c2": "\u09c1"})   # ী as ি, ূ as ু


def match_key(tok: str) -> str:
    """A token as the aligner compares it: the Bangla spellings that the script and the ASR often write
    differently are folded (কীভাবে and কিভাবে, দেখাবো and দেখাব)."""
    key = tok.translate(BN_SPELLING_FOLD)
    return key[:-1] if len(key) > 2 and key.endswith("\u09cb") else key


def _share_span(xs: list, start: float, end: float) -> None:
    lens = [max(1, len(x["tok"])) for x in xs]
    t, total = start, float(sum(lens))
    for x, n in zip(xs, lens):
        d = (end - start) * n / total
        x["t"] = (t, t + d)
        t += d


def fill_replaced(xs: list, hs: list, ak: list, bk: list) -> int:
    """Script tokens and heard tokens that differ between two matched stretches. Words joined or split
    differently (আসসালামু আলাইকুম heard as আসসালামুআলাইকুম) take the heard time, shared by length; where both
    sides have the same number of tokens left, alike words (60 % of their letters) pair one to one. Returns the
    number of script tokens placed; the rest are placed between their neighbours."""
    placed = i = j = 0
    while i < len(xs) and j < len(hs):
        a, b, ii, jj = ak[i], bk[j], i + 1, j + 1
        while a != b:
            if len(a) < len(b) and ii < len(xs) and b.startswith(a):
                a, ii = a + ak[ii], ii + 1
            elif len(b) < len(a) and jj < len(hs) and a.startswith(b):
                b, jj = b + bk[jj], jj + 1
            else:
                break
        if a == b:
            _share_span(xs[i:ii], hs[j]["start"], hs[jj - 1]["end"])
            placed, i, j = placed + (ii - i), ii, jj
        elif len(xs) - i == len(hs) - j and difflib.SequenceMatcher(a=ak[i], b=bk[j]).ratio() >= 0.6:
            xs[i]["t"] = (hs[j]["start"], hs[j]["end"])
            placed, i, j = placed + 1, i + 1, j + 1
        else:
            break
    return placed


BREAK_AFTER = tuple(",;:.!?\u0964\u0965\u2026)") + ("\u2014", "\u2013")


def _fits(words: list, max_chars: int, max_lines: int) -> bool:
    return split_lines(words, max_chars, max_lines) is not None


def split_lines(words: list, max_chars: int = 42, max_lines: int = 2):
    """Break one cue's words into at most two lines of at most 42 graphemes, balanced, preferring a break after
    punctuation. None when they do not fit."""
    text = " ".join(w["w"] for w in words)
    if graphemes(text) <= max_chars:
        return [text]
    if max_lines < 2:
        return None
    best = None
    for i in range(1, len(words)):
        a = " ".join(w["w"] for w in words[:i])
        b = " ".join(w["w"] for w in words[i:])
        ga, gb = graphemes(a), graphemes(b)
        if ga > max_chars or gb > max_chars:
            continue
        cost = abs(ga - gb) - (8 if a.endswith(BREAK_AFTER) else 0)
        if best is None or cost < best[0]:
            best = (cost, [a, b])
    return best[1] if best else None


def split_sentence(ws: list, max_chars: int, max_lines: int, max_s: float) -> list:
    """One sentence's timed words as cue groups: the fewest groups that fit (2 lines of 42 graphemes, 7 s), then
    even lengths, breaks after punctuation preferred, no one-word group left hanging."""
    def fits(j, i):
        g = ws[j:i]
        if i - j == 1:
            return True
        return g[-1]["end"] - g[0]["start"] <= max_s and _fits(g, max_chars, max_lines)
    n = len(ws)
    if fits(0, n):
        return [ws]
    count = [math.inf] * (n + 1)
    count[0] = 0
    for i in range(1, n + 1):
        for j in range(i - 1, -1, -1):
            if not fits(j, i):
                break
            count[i] = min(count[i], count[j] + 1)
    k = int(count[n])
    lengths = [graphemes(w["w"]) + 1 for w in ws]
    ideal = sum(lengths) / float(k)
    best = [[math.inf] * (n + 1) for _ in range(k + 1)]
    back = [[0] * (n + 1) for _ in range(k + 1)]
    best[0][0] = 0.0
    for g in range(1, k + 1):
        for i in range(1, n + 1):
            for j in range(i - 1, -1, -1):
                if not fits(j, i):
                    break
                if best[g - 1][j] == math.inf:
                    continue
                c = (sum(lengths[j:i]) - ideal) ** 2
                if i < n and ws[i - 1]["w"].endswith(BREAK_AFTER):
                    c -= 0.5 * ideal ** 2 * 0.25
                if i - j == 1:
                    c += ideal ** 2
                if best[g - 1][j] + c < best[g][i]:
                    best[g][i] = best[g - 1][j] + c
                    back[g][i] = j
    out, i = [], n
    for g in range(k, 0, -1):
        j = back[g][i]
        out.append(ws[j:i])
        i = j
    return list(reversed(out))


def build_cues(words: list, max_chars: int = 42, max_lines: int = 2, min_s: float = 1.0, max_s: float = 7.0,
               max_cps: float = 20.0) -> list:
    """Subtitle cues from timed words: at most 2 lines of 42 graphemes, 1 to 7 s, about 20 characters a second at
    most where the gaps allow, breaks at punctuation, never across sentences."""
    groups = []
    by_sent = {}
    for w in words:
        by_sent.setdefault(w["sentence"], []).append(w)
    for si in sorted(by_sent):
        groups += split_sentence(by_sent[si], max_chars, max_lines, max_s)
    cues = []
    for g in groups:
        lines = split_lines(g, max_chars, max_lines) or [" ".join(w["w"] for w in g)]
        cues.append({"start": g[0]["start"], "end": g[-1]["end"], "lines": lines,
                     "chars": sum(graphemes(x) for x in lines)})
    for i, c in enumerate(cues):
        nxt = cues[i + 1]["start"] - 0.08 if i + 1 < len(cues) else c["start"] + max_s
        want = max(c["end"], c["start"] + min_s, c["start"] + c["chars"] / max_cps)
        c["end"] = round(max(c["end"], min(want, nxt, c["start"] + max_s)), 3)
        if i + 1 < len(cues) and c["end"] > cues[i + 1]["start"] - 0.08:
            limit = cues[i + 1]["start"] - 0.08
            # the next cue wins: this one ends 80 ms before it, or halfway between the two starts when they are closer
            c["end"] = round(limit if limit > c["start"] + 0.02 else (c["start"] + cues[i + 1]["start"]) / 2, 3)
        c["cps"] = round(c["chars"] / max(0.01, c["end"] - c["start"]), 1)
    for c in cues:
        fixed = []
        for line in c["lines"]:
            if fixed and line[:1] in "\u0964\u0965,.;:!?":
                fixed[-1] += line[:1]
                line = line[1:].lstrip()
            if line:
                fixed.append(line)
        c["lines"] = fixed
    return cues


def srt_ts(sec: float, sep: str = ",") -> str:
    ms = int(round(max(0.0, float(sec)) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d}{sep}{ms:03d}"


def write_captions(project: Path, cues: list) -> tuple:
    srt = "".join(f"{i}\n{srt_ts(c['start'])} --> {srt_ts(c['end'])}\n" + "\n".join(c["lines"]) + "\n\n"
                  for i, c in enumerate(cues, 1))
    vtt = "WEBVTT\n\n" + "".join(f"{srt_ts(c['start'], '.')} --> {srt_ts(c['end'], '.')}\n" + "\n".join(c["lines"])
                                 + "\n\n" for c in cues)
    (project / "vo.srt").write_text(srt, encoding="utf-8")
    (project / "vo.vtt").write_text(vtt, encoding="utf-8")
    return project / "vo.srt", project / "vo.vtt"


# ------------------------------------------------------------------------------------------------ fit

def fit_plan(manifest: dict, plan: dict, targets: dict, ad: bool) -> dict:
    """Per scene: change the gaps first (180 to 900 ms), then one atempo factor (0.94 to 1.06, or 0.90 to 1.10 for
    ads; neighbours at most 3% apart), else say how much to cut or add."""
    main = plan["profiles"][plan["main_profile"]]
    gmin, gmax = main["gaps_ms"]["min"] / 1000.0, main["gaps_ms"]["max"] / 1000.0
    lo, hi = (0.90, 1.10) if ad else (0.94, 1.06)
    chunks = manifest["chunks"]
    wps = articulation_wps(main)[0]
    rows = []
    for sc in manifest["scenes"]:
        cs = [c for c in chunks if c["scene"] == sc["id"]]
        speech = sum(c["end"] - c["start"] for c in cs)
        gaps_all = sum(c["gap_after"]["s"] for c in cs if c is not chunks[-1])
        current = speech + gaps_all
        row = {"scene": sc["id"], "title": sc.get("title"), "current_s": round(current, 3)}
        if sc["id"] not in targets:
            row.update({"target_s": None, "new_s": round(current, 3), "tempo": 1.0, "gaps": {}, "residual_s": 0.0,
                        "advice": "no target given"})
            rows.append(row)
            continue
        target = float(targets[sc["id"]])
        adj = [c for c in cs[:-1] if c["gap_after"]["kind"] in ("sentence", "paragraph")]
        delta = target - current
        old_gaps = {c["id"]: c["gap_after"]["s"] for c in adj}
        new_gaps = dict(old_gaps)
        remaining = delta
        for _ in range(6):
            free = [cid for cid, g in new_gaps.items() if (remaining > 0 and g < gmax - 1e-6) or
                    (remaining < 0 and g > gmin + 1e-6)]
            if not free or abs(remaining) < 0.005:
                break
            step = remaining / len(free)
            for cid in free:
                g = new_gaps[cid]
                ng = min(gmax, max(gmin, g + step))
                remaining -= ng - g
                new_gaps[cid] = ng
        want = 1.0
        if abs(remaining) >= 0.005 and speech > 0:
            want = speech / max(0.1, speech + remaining)
        tempo = min(hi, max(lo, want))
        row.update({"target_s": target,
                    "gaps": {k: round(v, 3) for k, v in new_gaps.items() if abs(v - old_gaps[k]) > 1e-4},
                    "gap_change_s": round(delta - remaining, 3), "tempo_wanted": round(want, 4),
                    "tempo": round(tempo, 4), "speech_s": round(speech, 3),
                    "remaining_before_tempo": round(remaining, 3)})
        rows.append(row)
    # neighbouring scenes never more than 3% apart: a scene without a target stays at 1.0, so its neighbour moves
    for _ in range(len(rows) + 2):
        moved = False
        for i in range(1, len(rows)):
            a, b = rows[i - 1], rows[i]
            if abs(b["tempo"] - a["tempo"]) <= 0.03 + 1e-9:
                continue
            fix, other = (b, a) if b.get("target_s") is not None else (a, b)
            if fix.get("target_s") is None:
                continue
            fix["tempo"] = round(other["tempo"] + (0.03 if fix["tempo"] > other["tempo"] else -0.03), 4)
            fix["neighbour_limited"] = True
            moved = True
        if not moved:
            break
    for r in rows:
        if r.get("target_s") is None:
            continue
        new_speech = r["speech_s"] / r["tempo"]
        new_len = new_speech + (r["current_s"] - r["speech_s"]) + r["gap_change_s"]
        residual = r["target_s"] - new_len
        r["new_s"] = round(new_len, 3)
        r["residual_s"] = round(residual, 3)
        if abs(residual) < 0.05:
            r["advice"] = "fits" if (r["tempo"] == 1.0 and not r["gaps"]) else "fits with the changes above"
        elif residual < 0:
            r["advice"] = (f"re-render with a pace style or cut the script: {-residual:.1f} s too long, about "
                           f"{int(math.ceil(-residual * wps))} words to cut")
        else:
            r["advice"] = (f"{residual:.1f} s short: add about {int(math.ceil(residual * wps))} words, or re-render "
                           "with a slower pace style")
    return {"scenes": rows, "range": [lo, hi], "gap_range_s": [gmin, gmax]}


# ------------------------------------------------------------------------------------------------ commands: offline

def cmd_voices(args) -> None:
    if args.library:
        return voices_library(args)
    rows = data("voices.json")["voices"]
    if args.gender:
        g = {"f": "female", "m": "male"}.get(args.gender[0].lower())
        rows = [v for v in rows if v["gender"] == g]
    if args.find:
        f = args.find.lower()
        rows = [v for v in rows if f in v["name"].lower() or f in v["character"].lower()]
    lines = [f"{v['name']:14} {v['gender']:7} {v['character']}" for v in rows]
    lines.append(f"{len(rows)} voices. {data('voices.json')['note']}")
    emit(args, {"ok": True, "voices": rows, "note": data("voices.json")["note"]}, lines)


def voices_library(args) -> None:
    params = {"page_size": "100"}
    if args.lang:
        params["language_code"] = args.lang
    if args.gender:
        params["gender"] = {"f": "female", "m": "male"}.get(args.gender[0].lower(), args.gender)
    if args.search or args.find:
        params["search"] = args.search or args.find
    found, token = [], None
    for _ in range(10):
        q = dict(params)
        if token:
            q["page_token"] = token
        path = "/v1beta/voices?" + "&".join(f"{k}={urllib_quote(v)}" for k, v in q.items())
        try:
            resp, _ = G.request("GET", path, timeout=60)
        except G.GeminiError as err:
            die(explain(err))
        found += resp.get("voices") or []
        token = resp.get("next_page_token") or resp.get("nextPageToken")
        if not token:
            break
    lines = [f"{v.get('id', ''):28} {v.get('display_name', v.get('displayName', '')):22} "
             f"{v.get('language_code', v.get('languageCode', '')):7} {v.get('gender', ''):7} "
             f"{v.get('accent', '') or ''} {v.get('description', '') or ''}".rstrip() for v in found]
    lines.append(f"{len(found)} library voices (3.8 only; use an id with `profile new NAME --preset ID --voice ID`)")
    emit(args, {"ok": True, "voices": found, "filters": params}, lines)


def urllib_quote(v: str) -> str:
    import urllib.parse
    return urllib.parse.quote(str(v), safe="")


def cmd_presets(args) -> None:
    rows = data("presets.json")["presets"]
    lines = [f"{p['id']:22} {p['voice']:13} {p['language']:6} {p['wpm'][0]}-{p['wpm'][1]} wpm  {p['use']}"
             for p in rows]
    lines.append(data("presets.json")["note"])
    emit(args, {"ok": True, "presets": rows, "note": data("presets.json")["note"],
                "bangla_accent": data("presets.json")["bangla_accent"]}, lines)


def cmd_profile(args) -> None:
    pdir = profiles_dir(args)
    action = args.action
    if action == "list":
        rows = []
        for path in sorted(pdir.glob("*.json")) if pdir.exists() else []:
            try:
                p = load_profile(path.stem, pdir)
            except ProfileError:
                continue
            rows.append({"name": p["name"], "version": p["version"], "model": p["model"], "voice": p["voice"]["id"],
                         "language": p["language"], "preset": p.get("preset"), "days_left": rnd(voice_days_left(p), 1)})
        lines = [f"{r['name']:20} v{r['version']:<3} {r['model']:28} {r['voice']:16} {r['language']}" for r in rows]
        lines.append(f"{len(rows)} profiles in {pdir}")
        return emit(args, {"ok": True, "folder": str(pdir), "profiles": rows}, lines)
    if not args.name:
        die(f"profile {action} wants a NAME")
    if action == "show":
        try:
            p = load_profile(args.name, pdir)
        except ProfileError as err:
            die(str(err))
        lines = [f"{p['name']} version {p['version']} ({pdir / (p['name'] + '.json')})",
                 f"model {p['model']} ({p['prompt_family']}), voice {p['voice']['id']} ({p['voice'].get('type')}), "
                 f"language {p['language']}",
                 f"style: {p['style'] or '(empty)'}",
                 "modes: " + (", ".join(f"{k} = {v}" for k, v in p["modes"].items()) or "none"),
                 f"pace {p['wpm']['target']} wpm (measured {p['wpm'].get('measured_wps') or 'not yet'}), gaps "
                 f"{p['gaps_ms']['sentence']}/{p['gaps_ms']['paragraph']}/{p['gaps_ms']['scene']} ms, loudness "
                 f"{p['loudness']['stem_I']} LUFS / {p['loudness']['TP']} dBTP"]
        if p.get("design_prompt") and p["voice"].get("type") == "prebuilt" and p["prompt_family"] == "speech_metadata":
            lines.append(f"voice design prompt for this preset: {p['design_prompt']}")
        days = voice_days_left(p)
        if days is not None:
            lines.append(f"designed voice: {days:.0f} days left")
        return emit(args, {"ok": True, "profile": p, "file": str(pdir / (p["name"] + ".json"))}, lines)
    if action == "new":
        if not NAME_RX.match(args.name):
            die(f"{args.name!r} is not a profile name (letters, digits, dot, dash, underscore)")
        if not args.preset:
            die("profile new wants --preset ID (see `presets`)")
        preset = preset_by_id(args.preset)
        if not preset:
            die(f"unknown preset {args.preset}; see `presets`")
        if args.model and args.model not in MODELS:
            die(f"unknown model {args.model}; known: {', '.join(MODELS)}")
        path = pdir / f"{args.name}.json"
        if path.exists():
            die(f"{path} exists: pick another name, or edit that file (its version goes up by itself)")
        modes = {}
        for item in args.mode or []:
            if "=" not in item:
                die(f"--mode wants NAME=STYLE, not {item!r}")
            k, v = item.split("=", 1)
            modes[k.strip()] = v.strip()
        try:
            p = new_profile(args.name, preset, pdir, voice=args.voice, style=args.style, model=args.model,
                            lang=args.lang, modes=modes, lexicon=args.lexicon)
            validate_profile(p)
        except ProfileError as err:
            die(str(err))
        pdir.mkdir(parents=True, exist_ok=True)
        write_json(path, p)
        lines = [f"made profile {p['name']} (version 1): {p['model']}, voice {p['voice']['id']}, {p['language']}",
                 f"style: {p['style']}", f"file: {path}"]
        if preset.get("design_prompt") and p["prompt_family"] == "speech_metadata" and not args.voice:
            lines.append("For a Dhaka accent on 3.8, design a voice once: design --desc \"" + preset["design_prompt"]
                         + "\" --gender " + preset["gender"] + " --lang bn-BD --takes 3 --out DIR, then design keep ID "
                         f"--profile {p['name']}")
        return emit(args, {"ok": True, "profile": p, "file": str(path)}, lines)
    die(f"unknown profile action {action}: new, show or list")


def cmd_plan(args) -> None:
    script = Path(args.script).expanduser().resolve()
    if not script.exists():
        die(f"{script} is missing")
    out = Path(args.out).expanduser().resolve() if args.out else script.parent
    try:
        plan = build_plan(script.read_text(encoding="utf-8"), args.profile, profiles_dir(args),
                          True if args.precise else None, str(script), calibration(out))
    except (ProfileError, ToolError) as err:
        die(str(err))
    out.mkdir(parents=True, exist_ok=True)
    path = write_plan_file(out, plan)
    lines = plan_lines(plan)
    lines.append(f"wrote {path}")
    emit(args, {"ok": not plan["errors"], "plan": str(path), "totals": plan["totals"], "errors": plan["errors"],
                "warnings": plan["warnings"], "notes": plan["notes"],
                "chunks": [{k: c[k] for k in ("id", "scene", "profile", "speaker", "mode", "n_words", "est_s", "takes",
                                              "standalone", "hero", "gap_after", "display", "spoken")}
                           for c in plan["chunks"]]}, lines, 1 if plan["errors"] else 0)


def plan_lines(plan: dict) -> list:
    t = plan["totals"]
    speakers = {c["speaker"] for c in plan["chunks"] if c["speaker"]}
    lines = [f"{'chunk':6} {'scene':5} {'who':18} {'words':>5} {'secs':>5} {'takes':>5}  text"]
    for c in plan["chunks"]:
        who = c["speaker"] or c["profile"]
        if c["mode"]:
            who += "/" + c["mode"]
        text = c["display"] if len(c["display"]) <= 48 else c["display"][:47] + "..."
        lines.append(f"{c['id']:6} {c['scene']:5} {who[:18]:18} {c['n_words']:>5} {c['est_s']:>5.1f} {c['takes']:>5}  "
                     f"{text}" + ("  (stands alone)" if c["standalone"] else "") + ("  (hero)" if c["hero"] else ""))
    lines.append(f"{t['chunks']} chunks in {t['scenes']} scenes" + (f", {len(speakers)} speakers" if speakers else "")
                 + f"; about {fmt_s(t['speech_s'])} of speech, {fmt_s(t['total_s'])} with the gaps")
    lines.append(f"{t['requests']} requests, about {t['audio_tokens']:,} audio tokens and {t['text_tokens']:,} text "
                 "tokens")
    u = t["usd"]
    lines.append(f"cost: about {usd(u['interactive'])} interactive, {usd(u['batch_or_flex'])} batch or flex (for "
                 f"reference), {usd(u['interactive_from_2027'])} from 2027-01-01; real bills have run about "
                 f"{BILL_FACTOR}x the arithmetic (prices as of {PRICES_AS_OF})")
    for e in plan["errors"]:
        lines.append(f"ERROR line {e['line']}: {e['error']}")
    for w in plan["warnings"]:
        lines.append(f"warning line {w.get('line')}: {w['kind']} {w.get('text', '')!r}: {w['hint']}")
    for n in plan["notes"]:
        lines.append(f"note: {n['note']}")
    return lines


def cmd_pick(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    plan = load_plan(project)
    state = load_state(project)
    ch = next((c for c in plan["chunks"] if c["id"] == args.chunk), None)
    if not ch:
        die(f"no chunk {args.chunk} in {project / 'plan.json'}")
    entry = state["chunks"].get(ch["base_key"]) or {}
    if str(args.take) not in entry.get("takes", {}):
        die(f"{args.chunk} has no take {args.take}; it has: {', '.join(sorted(entry.get('takes', {}))) or 'none'}")
    entry["chosen"] = int(args.take)
    entry["chosen_by"] = "pick"
    save_state(project, state)
    emit(args, {"ok": True, "chunk": args.chunk, "take": int(args.take)},
         [f"{args.chunk}: take {args.take} chosen by hand; run master again"])


def cmd_qa(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    need_filters()
    plan = load_plan(project)
    state = load_state(project)
    metrics = gather(plan, state, project)
    asr_results = {}
    if args.asr:
        est = sum(asr_usd(c["est_s"]) for c in plan["chunks"])
        if est > args.budget + 1e-9:
            die(str(BudgetError(est, args.budget, len(plan["chunks"]))))
        try:
            asr_results = run_asr(plan, state, project, "qa", plan["chunks"], chosen_only=True)
        except G.GeminiError as err:
            die(explain(err))
    refs = references(plan, state, metrics, calibration(project))
    for ch in plan["chunks"]:
        entry = state["chunks"].get(ch["base_key"]) or {}
        if entry.get("takes"):
            choose(ch, entry, metrics, refs, asr_results)
    save_state(project, state)
    qa = write_qa(project, plan, state, metrics, refs, asr_results)
    lines = qa_lines(qa) + [f"wrote {project / 'qa.json'}"]
    emit(args, {"ok": True, "qa": str(project / "qa.json"), "summary": qa["summary"], "chunks": qa["chunks"]}, lines)


def cmd_master(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    t0 = time.time()
    try:
        man = master_project(project)
    except ToolError as err:
        die(str(err))
    lines = master_lines(project, man, time.time() - t0)
    emit(args, {"ok": True, "file": str(project / "vo_48k.wav"), "manifest": str(project / "vo.manifest.json"),
                "duration_s": man["duration_s"], "loudness": man["loudness"], "chunks": len(man["chunks"]),
                "flagged": man["qa"]["flagged"], "seconds": round(time.time() - t0, 1)}, lines)


def master_lines(project: Path, man: dict, secs: float) -> list:
    ld = man["loudness"]
    lines = [f"master: {project / 'vo_48k.wav'} ({fmt_s(man['duration_s'])}, 48 kHz 24-bit), "
             f"{len(man['chunks'])} chunks, {len(man['sentences'])} sentences",
             f"loudness {ld['I']} LUFS, true peak {ld['TP']} dBTP, LRA {ld['LRA']} LU ({ld['normalization']}"
             + (f", limiter at {ld['limiter_db']} dBFS" if ld.get("limiter_db") is not None else "") + ")",
             f"manifest: {project / 'vo.manifest.json'} ({secs:.1f} s)"]
    if man["qa"]["flagged"]:
        lines.append("flagged chunks (listen, pick another take or re-render): " + ", ".join(man["qa"]["flagged"]))
    if man.get("fit"):
        lines.append("fit.json applied (scene tempo and gaps)")
    return lines


def cmd_align(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    plan = load_plan(project)
    man = read_json(project / "vo.manifest.json")
    if not isinstance(man, dict) or man.get("schema") != "nexa-speech/manifest-1":
        die(f"{project} has no vo.manifest.json: run master first")
    engine = args.engine
    if engine == "auto":
        engine = "gemini" if G.keys() else "pauses"
    try:
        if engine == "gemini":
            words, sents, info = align_gemini(project, plan, man, args.budget)
        elif engine == "elevenlabs":
            words, sents, info = align_eleven(project, plan, man, args.budget)
        else:
            words, sents, info = align_pauses(project, plan, man)
    except G.GeminiError as err:
        die(explain(err))
    except EL.ElevenError as err:
        die("ElevenLabs forced alignment: %s" % EL.scrub(str(err)))
    except BudgetError as err:
        die(str(err))
    cues = build_cues(words)
    write_json(project / "words.json", words)
    write_json(project / "sentences.json", sents)
    srt, vtt = write_captions(project, cues)
    fast = [i + 1 for i, c in enumerate(cues) if c["cps"] > 20.5]
    write_json(project / "align.json", {
        "schema": "nexa-speech/align-1", "skill_version": SKILL_VERSION, "created": now_iso(), "engine": engine,
        "info": info, "source": "vo_48k.wav", "manifest_created": man.get("created"),
        "captions": {"max_chars": 42, "max_lines": 2, "min_s": 1.0, "max_s": 7.0, "max_cps": 20.0,
                     "cues": len(cues), "fast_cues": fast},
        "files": ["words.json", "sentences.json", "vo.srt", "vo.vtt"]})
    lines = [f"align ({engine}): {len(words)} words, {len(sents)} sentences, {len(cues)} caption cues",
             f"wrote {project / 'words.json'}, sentences.json, {srt.name}, {vtt.name}"]
    if fast:
        lines.append(f"cues over 20 characters a second (fast speech, no room to hold them longer): {fast[:12]}")
    if info.get("matched_share") is not None:
        share = info["matched_share"]
        lines.append(f"ASR matched {share * 100:.0f}% of the script tokens"
                     + (f" ({info['close']} of them joined, split or spelled differently)" if info.get("close") else "")
                     + ("; the rest are placed between their neighbours" if share < 1.0 else ""))
    emit(args, {"ok": True, "engine": engine, "info": info, "words": str(project / "words.json"),
                "sentences": str(project / "sentences.json"), "srt": str(srt), "vtt": str(vtt), "cues": len(cues),
                "fast_cues": fast}, lines)


def cmd_fit(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    plan = load_plan(project)
    man = read_json(project / "vo.manifest.json")
    if not isinstance(man, dict) or man.get("schema") != "nexa-speech/manifest-1":
        die(f"{project} has no vo.manifest.json: run master first")
    scenes = read_json(Path(args.scenes).expanduser())
    if not isinstance(scenes, list):
        die("--scenes wants a JSON list like [{\"scene\": \"s1\", \"target_s\": 12.0}]")
    targets = {}
    for s in scenes:
        if not isinstance(s, dict) or "scene" not in s or "target_s" not in s:
            die("each scene entry needs scene and target_s")
        targets[str(s["scene"])] = float(s["target_s"])
    unknown = [k for k in targets if k not in {x["id"] for x in man["scenes"]}]
    if unknown:
        die(f"unknown scene(s) {', '.join(unknown)}; the manifest has {', '.join(x['id'] for x in man['scenes'])}")
    fp = fit_plan(man, plan, targets, args.ad)
    lines = [f"{'scene':6} {'now':>7} {'target':>7} {'new':>7} {'tempo':>6}  advice"]
    for r in fp["scenes"]:
        lines.append(f"{r['scene']:6} {r['current_s']:>7.2f} {('%.2f' % r['target_s']) if r['target_s'] else '-':>7} "
                     f"{r['new_s']:>7.2f} {r['tempo']:>6.3f}  {r['advice']}"
                     + (f" (gaps changed: {len(r['gaps'])})" if r.get("gaps") else ""))
    result = {"ok": True, "plan": fp, "applied": False}
    if args.apply:
        stamp = time.strftime("%Y%m%d-%H%M%S")
        kept, backups = [], []
        for name in ("vo_48k.wav", "vo.manifest.json"):
            src = project / name
            if src.exists():
                dst = project / f"{src.stem}.before-fit-{stamp}{src.suffix}"
                shutil.copy2(src, dst)
                backups.append((src, dst))
                kept.append(dst.name)
        gaps, tempo = {}, {}
        for r in fp["scenes"]:
            gaps.update(r.get("gaps") or {})
            if r["tempo"] != 1.0:
                tempo[r["scene"]] = r["tempo"]
        fit_doc = {"schema": "nexa-speech/fit-1", "created": now_iso(), "script_sha": plan.get("script_sha"),
                   "targets": targets, "ad": bool(args.ad), "tempo": tempo, "gaps": gaps, "plan": fp}
        write_json(project / "fit.json", fit_doc)
        try:
            man2 = master_project(project, fit_doc)
        except ToolError as err:
            for src, dst in backups:
                shutil.copy2(dst, src)
            die(f"{err} (the master and manifest from before the fit are back in place)")
        for name in ("words.json", "sentences.json", "vo.srt", "vo.vtt"):
            src = project / name
            if src.exists():
                dst = project / f"{src.stem}.before-fit-{stamp}{src.suffix}"
                os.replace(src, dst)
                kept.append(dst.name)
        result.update({"applied": True, "kept": kept, "fit": str(project / "fit.json"),
                       "duration_s": man2["duration_s"]})
        lines.append(f"applied: new vo_48k.wav and vo.manifest.json; the old ones are kept as {', '.join(kept)}; "
                     "run align again for new captions")
    else:
        lines.append("nothing changed; --apply writes the new master and manifest (the old ones are kept)")
    emit(args, result, lines)


def cmd_cost(args) -> None:
    if args.dir:
        return cost_actual(args)
    minutes = float(args.minutes)
    secs = minutes * 60.0
    models = [args.model] if args.model else list(MODELS)
    rows = []
    for m in models:
        if m not in MODELS:
            die(f"unknown model {m}; known: {', '.join(MODELS)}")
        base = tts_usd(m, secs, text_tokens("x" * int(secs * 15)))
        rows.append({"model": m, "status": MODELS[m]["status"], "audio_tokens": int(secs * AUDIO_TOKENS_PER_S),
                     "interactive": round(base, 4), "batch_or_flex": round(base * BATCH_FACTOR, 4),
                     "interactive_from_2027": round(tts_usd(m, secs, text_tokens("x" * int(secs * 15)), "2027-01-01"),
                                                    4),
                     "with_retakes": round(base * RETAKE_FACTOR, 4),
                     "word_timings": round(asr_usd(secs), 4),
                     "likely_bill": round((base * RETAKE_FACTOR + asr_usd(secs)) * BILL_FACTOR, 4)})
    lines = [f"{minutes:g} minutes of finished voice-over ({int(secs * AUDIO_TOKENS_PER_S):,} audio tokens at "
             f"{AUDIO_TOKENS_PER_S} a second; prices as of {PRICES_AS_OF}):",
             f"{'model':30} {'interactive':>11} {'batch/flex':>10} {'from 2027':>9} {'x1.4 takes':>10} "
             f"{'+timings':>8} {'likely':>8}"]
    for r in rows:
        lines.append(f"{r['model']:30} {usd(r['interactive']):>11} {usd(r['batch_or_flex']):>10} "
                     f"{usd(r['interactive_from_2027']):>9} {usd(r['with_retakes']):>10} {usd(r['word_timings']):>8} "
                     f"{usd(r['likely_bill']):>8}")
    lines.append(f"'likely' = (x1.4 takes + word timings) x {BILL_FACTOR}: real bills have run about {BILL_FACTOR}x "
                 "the token arithmetic; ledger.jsonl records every call's usage so you can check")
    emit(args, {"ok": True, "minutes": minutes, "rows": rows, "prices_as_of": PRICES_AS_OF}, lines)


def _pacific_day(iso: str) -> str:
    try:
        when = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return "?"
    try:
        from zoneinfo import ZoneInfo
        return when.astimezone(ZoneInfo("America/Los_Angeles")).date().isoformat()
    except Exception:
        return (when - dt.timedelta(hours=8)).date().isoformat()


def usage_usd(model: str, usage: dict, when: str):
    """Dollars from a response's usage block, when it carries token counts (field names vary by API)."""
    if not isinstance(usage, dict) or model not in MODELS:
        return None
    out_tok = None
    for k in ("total_output_tokens", "output_tokens", "candidatesTokenCount", "candidates_token_count"):
        if isinstance(usage.get(k), (int, float)):
            out_tok = usage[k]
            break
    in_tok = 0
    for k in ("total_input_tokens", "input_tokens", "promptTokenCount", "prompt_token_count"):
        if isinstance(usage.get(k), (int, float)):
            in_tok = usage[k]
            break
    if out_tok is None:
        return None
    day = (when or "")[:10] or None
    return out_tok / 1e6 * price_per_m(model, "audio", day) + in_tok / 1e6 * price_per_m(model, "text", day)


def cost_actual(args) -> None:
    project = Path(args.dir).expanduser().resolve()
    entries = read_jsonl(project / "ledger.jsonl")
    by_model, by_day = {}, {}
    total_est, total_usage, usage_n = 0.0, 0.0, 0
    for e in entries:
        m = by_model.setdefault(e.get("model") or "?", {"calls": 0, "errors": 0, "est_usd": 0.0, "usage_usd": 0.0,
                                                          "usage_calls": 0})
        m["calls"] += 1
        if str(e.get("result", "")).startswith("error"):
            m["errors"] += 1
        m["est_usd"] += e.get("est_usd") or 0.0
        total_est += e.get("est_usd") or 0.0
        u = usage_usd(e.get("model"), e.get("usage"), e.get("time"))
        if u is not None:
            m["usage_usd"] += u
            m["usage_calls"] += 1
            total_usage += u
            usage_n += 1
        day = _pacific_day(e.get("time") or "")
        by_day.setdefault(day, {}).setdefault(e.get("model") or "?", 0)
        by_day[day][e.get("model") or "?"] += 1
    plan = read_json(project / "plan.json") or {}
    lines = [f"{project / 'ledger.jsonl'}: {len(entries)} calls, estimated {usd(total_est)}"
             + (f", {usd(total_usage)} from the usage the API reported on {usage_n} calls" if usage_n else "")]
    for name, m in by_model.items():
        lines.append(f"  {name:30} {m['calls']:>4} calls ({m['errors']} errors), est {usd(m['est_usd'])}"
                     + (f", usage {usd(m['usage_usd'])}" if m["usage_calls"] else ""))
    for day, ms in sorted(by_day.items()):
        lines.append(f"  requests on {day} (Pacific): " + ", ".join(f"{k} {v}" for k, v in ms.items()))
    if plan.get("totals"):
        lines.append(f"the plan estimated {usd(plan['totals']['usd']['interactive'])} for one take of each chunk")
    emit(args, {"ok": True, "ledger": str(project / "ledger.jsonl"), "calls": len(entries),
                "est_usd": round(total_est, 5), "usage_usd": round(total_usage, 5) if usage_n else None,
                "by_model": by_model, "requests_by_day": by_day}, lines)


# ------------------------------------------------------------------------------------------------ commands: API

def cmd_doctor(args) -> None:
    rep = {"skill_version": SKILL_VERSION, "prices_as_of": PRICES_AS_OF}
    rep["keys"] = G.key_sources()
    ffb = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    rep["ffmpeg"] = ffb
    if ffb:
        have = ffmpeg_filters()
        rep["ffmpeg_version"] = ffmpeg_version()
        rep["filters"] = {f: (f in have) for f in (*REQUIRED_FILTERS, "deesser")}
    cdir = cache_dir()
    wavs = list(cdir.glob("*.wav")) if cdir.exists() else []
    rep["cache"] = {"folder": str(cdir), "masters": len(wavs),
                    "mb": round(sum(p.stat().st_size for p in wavs) / 1e6, 1)}
    pdir = profiles_dir(args)
    expiring = []
    for path in sorted(pdir.glob("*.json")) if pdir.exists() else []:
        try:
            p = load_profile(path.stem, pdir)
        except ProfileError:
            continue
        days = voice_days_left(p)
        if days is not None and days < EXPIRY_WARN_DAYS:
            expiring.append({"profile": p["name"], "voice": p["voice"]["id"], "days_left": round(days, 1)})
    rep["profiles_folder"] = str(pdir)
    rep["voices_expiring"] = expiring
    lines = [f"nexa-speech {SKILL_VERSION} (prices as of {PRICES_AS_OF})",
             "keys: " + (", ".join(rep["keys"]) if rep["keys"] else "none (render, say, design and --asr need one)"),
             f"ffmpeg: {ffb or 'missing (brew install ffmpeg)'}" + (f" {rep.get('ffmpeg_version')}" if ffb else "")]
    if ffb:
        missing = [f for f, ok in rep["filters"].items() if not ok and f != "deesser"]
        lines.append("filters: " + ("all present" if not missing else "MISSING " + ", ".join(missing))
                     + ("" if rep["filters"].get("deesser") else " (deesser missing: post.deess must stay 0)"))
    lines.append(f"cache: {cdir} ({len(wavs)} masters, {rep['cache']['mb']} MB; never deleted by this tool)")
    for e in expiring:
        lines.append(f"voice expiring: profile {e['profile']} voice {e['voice']} in {e['days_left']:.0f} days")
    ready = bool(ffb) and all(v for k, v in (rep.get("filters") or {}).items() if k != "deesser")
    if args.live:
        if not rep["keys"]:
            die(G.MISSING_KEY_HELP)
        try:
            names = G.list_models()
        except G.GeminiError as err:
            die(explain(err))
        rep["live"] = {"models_seen": len(names), "tts": sorted(n for n in names if "tts" in n),
                       "transcribe": sorted(n for n in names if "transcribe" in n),
                       "ours": {m: (m in names) for m in (*MODELS, TRANSCRIBE_MODEL)}}
        lines.append("live: the key's project sees " + ", ".join(f"{m} {'yes' if ok else 'NO'}"
                                                                 for m, ok in rep["live"]["ours"].items()))
    rep["ready"] = ready
    rep["ok"] = ready
    emit(args, rep, lines, 0 if ready else 1)


def design_parse(resp: dict) -> dict:
    v = resp.get("voice") if isinstance(resp.get("voice"), dict) else resp
    vid = str(v.get("id") or v.get("name") or resp.get("id") or "")
    vid = vid.split("/")[-1]
    expire = v.get("expire_time") or v.get("expireTime") or resp.get("expire_time") or resp.get("expireTime")
    sample = v.get("sample_audio") or v.get("sampleAudio") or resp.get("sample_audio") or resp.get("sampleAudio")
    data_b64, mime = None, "audio/wav"
    if isinstance(sample, dict):
        data_b64 = sample.get("data")
        mime = sample.get("mime_type") or sample.get("mimeType") or mime
    elif isinstance(sample, str):
        data_b64 = sample
    return {"id": vid, "expire_time": expire, "sample_b64": data_b64, "mime": mime,
            "display_name": v.get("display_name") or v.get("displayName")}


def cmd_design(args) -> None:
    rest = args.rest or []
    if rest and rest[0] == "keep":
        return design_keep(args, rest[1] if len(rest) > 1 else None)
    if rest:
        die("design takes --desc ... (or: design keep VOICE_ID --profile NAME)")
    if not args.desc or not args.out:
        die("design wants --desc \"...\" and --out DIR")
    model = args.model or DEFAULT_MODEL
    if model not in MODELS or MODELS[model]["family"] != "speech_metadata":
        die("voice design is a 3.8 feature: use gemini-3.8-flash-tts or gemini-3.8-flash-lite-tts")
    takes = max(1, min(5, int(args.takes)))
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    est = takes * tts_usd(model, DESIGN_SAMPLE_S, text_tokens(args.desc))
    if est > args.budget + 1e-9:
        die(str(BudgetError(est, args.budget, takes)))
    name = args.name or "designed"
    results = []
    for i in range(1, takes + 1):
        body = {"store": True, "voice": {"model": model, "type": "prompted", "display_name": f"{name}-{i}",
                                         "gender": args.gender, "language_code": args.lang,
                                         "prompted": {"input": args.desc}}}
        t0 = time.time()
        try:
            resp, info = G.request("POST", "/v1beta/voices", body, timeout=TTS_TIMEOUT)
        except G.GeminiError as err:
            ledger(out, {"time": now_iso(), "command": "design", "model": model, "units": {"takes": 1},
                         "est_usd": 0.0, "result": "error:" + err.kind, "message": G.scrub(str(err))[:300]})
            if results:
                break
            die(explain(err))
        got = design_parse(resp)
        sample = None
        if got["sample_b64"]:
            stem = str(out / f"design-{i}-{got['id'] or 'voice'}")
            sample = G.save_audio({"bytes": base64.b64decode(got["sample_b64"]), "mime_type": got["mime"],
                                   "sample_rate": 24000}, stem)
        rec = {"id": got["id"], "expire_time": got["expire_time"], "model": model, "desc": args.desc,
               "gender": args.gender, "language": args.lang, "display_name": got["display_name"] or f"{name}-{i}",
               "sample": sample, "created": now_iso(), "key_source": info.get("key")}
        results.append(rec)
        append_jsonl(home() / "designs.jsonl", rec)
        ledger(out, {"time": now_iso(), "command": "design", "model": model, "units": {"takes": 1,
                                                                                      "audio_s_est": DESIGN_SAMPLE_S},
                     "est_usd": round(est / takes, 6), "key_source": info.get("key"), "result": "ok",
                     "voice": got["id"], "seconds": round(time.time() - t0, 2)})
    write_json(out / "design.json", {"schema": "nexa-speech/design-1", "created": now_iso(), "model": model,
                                     "desc": args.desc, "gender": args.gender, "language": args.lang,
                                     "voices": results, "note": "voice design is untested against the real API"})
    lines = [f"{len(results)} designed voice(s) in {out}:"]
    for r in results:
        lines.append(f"  {r['id']}  expires {r['expire_time'] or 'unknown'}  sample {r['sample'] or 'none'}")
    lines.append("listen to the samples, then: design keep VOICE_ID --profile NAME (every design call gives a new "
                 "voice, even with the same words; stored voices count toward the project's 200)")
    emit(args, {"ok": bool(results), "voices": results, "design": str(out / "design.json")}, lines,
         0 if results else 1)


def design_keep(args, vid) -> None:
    if not vid or not args.profile:
        die("design keep wants VOICE_ID and --profile NAME")
    recs = []
    if args.out and (Path(args.out).expanduser() / "design.json").exists():
        recs += (read_json(Path(args.out).expanduser() / "design.json") or {}).get("voices", [])
    recs += read_jsonl(home() / "designs.jsonl")
    rec = next((r for r in reversed(recs) if r.get("id") == vid), None)
    if not rec:
        die(f"no designed voice {vid} in {home() / 'designs.jsonl'}: run design first (or pass --out with its folder)")
    pdir = profiles_dir(args)
    try:
        p = load_profile(args.profile, pdir)
    except ProfileError as err:
        die(str(err))
    notes = []
    if rec.get("model") and rec["model"] != p["model"]:
        notes.append(f"model changed from {p['model']} to {rec['model']} (a designed voice belongs to its model)")
        p["model"] = rec["model"]
        p["prompt_family"] = MODELS[rec["model"]]["family"]
    p["voice"] = {"id": vid, "type": "designed", "expire_time": rec.get("expire_time"), "sample": rec.get("sample")}
    save_profile(p, pdir, f"voice pinned to designed voice {vid}")
    days = voice_days_left(p)
    lines = [f"profile {p['name']} now uses {vid} (version {p['version']})"] + notes
    if days is not None:
        lines.append(f"it expires in {days:.0f} days ({rec.get('expire_time')}); doctor and render warn 30 days ahead")
    else:
        lines.append("no expiry time came back: check the voice in AI Studio")
    emit(args, {"ok": True, "profile": p["name"], "version": p["version"], "voice": p["voice"], "notes": notes}, lines)


def cmd_audition(args) -> None:
    need_filters()
    pdir = profiles_dir(args)
    try:
        p = load_profile(args.profile, pdir)
    except ProfileError as err:
        die(str(err))
    text = clean_text(Path(args.text).expanduser().read_text(encoding="utf-8")).strip()
    if not text:
        die(f"{args.text} is empty")
    voices = [v.strip() for v in args.voices.split(",") if v.strip()]
    if not voices:
        die("--voices wants names like Charon,Iapetus")
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    lex = load_lexicon(p, pdir)
    nm = normalise(" ".join(text.split()), p["prompt_family"], lex, p["numbers"])
    words = spoken_words(nm["spoken"])
    wps, _ = articulation_wps(p)
    est_s = len(words) / wps + tag_seconds(nm["tags"])
    if est_s > 15.5:
        die(f"the audition text runs about {est_s:.0f} s: keep it to 15 s or less (about {int(15 * wps)} words)")
    chunks = []
    for v in voices:
        pv = prebuilt_voice(v)
        vid = pv["name"] if pv else v
        vtype = "prebuilt" if pv else ("designed" if v.startswith("voice_") else "library")
        voice = {"id": vid, "type": vtype, "expire_time": None}
        ch = {"id": f"a-{vid}", "model": p["model"], "family": p["prompt_family"], "voice": vid, "voice_type": vtype,
              "voice_key": voice_key(voice), "language": p["language"], "send_language_code": p["send_language_code"],
              "style": p["style"], "request_text": nm["spoken"], "spoken": nm["spoken"], "display": nm["display"],
              "est_s": round(est_s, 2), "n_words": len(words), "tags": nm["tags"], "lexicon_terms": nm["terms"],
              "profile": p["name"], "takes": 1}
        ch["base_key"] = sha16(key_fields(ch))
        chunks.append(ch)
    todo = [(ch, 1) for ch in chunks if cached_take(ch, 1, out) is None]
    est = sum(take_cost(ch) for ch, _ in todo)
    log(f"audition: {len(voices)} voices, {len(todo)} new call(s), about {usd(est)}")
    if est > args.budget + 1e-9:
        die(str(BudgetError(est, args.budget, len(todo))))
    recs, fails, stopped = run_jobs(todo, out, "audition") if todo else ({}, [], None)
    if stopped is not None:
        die(explain(stopped))
    files, silence = [], None
    for ch in chunks:
        rec = recs.get((ch["base_key"], 1)) or cached_take(ch, 1, out)
        if not rec:
            continue
        m = analyse_audio(out / "masters" / f"{rec['key']}.wav")
        if m.get("empty"):
            continue
        tmp = out / "work" / f"{ch['voice']}.f32"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        process_chunk(out / "masters" / f"{rec['key']}.wav", m, 0.0, 1.0, tmp)
        dst = out / f"audition-{re.sub(r'[^A-Za-z0-9_.-]+', '_', ch['voice'])}.wav"
        fin = finish_loudness(tmp, CANVAS_RATE, p["loudness"], dst)
        files.append({"voice": ch["voice"], "file": str(dst), "master_key": rec["key"],
                      "duration_s": rnd(probe_duration(dst)), "loudness": fin["I"], "source": rec["source"]})
    if files:
        lst = out / "work" / "all.txt"
        silence = out / "work" / "gap.wav"
        ff(["-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", "1", "-c:a", "pcm_s24le",
            silence])
        lst.write_text("".join(f"file '{Path(f['file']).as_posix()}'\nfile '{silence.as_posix()}'\n" for f in files),
                       encoding="utf-8")
        ff(["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c:a", "pcm_s24le",
            out / "audition-all.wav"])
    doc = {"schema": "nexa-speech/audition-1", "created": now_iso(), "profile": p["name"], "model": p["model"],
           "style": p["style"], "text": nm["display"], "spoken": nm["spoken"], "est_usd": round(est, 5),
           "files": files, "all": str(out / "audition-all.wav") if files else None, "failures": fails}
    write_json(out / "audition.json", doc)
    lines = [f"audition: {len(files)} of {len(voices)} voices in {out} (about {usd(est)} for new calls)"]
    for f in files:
        lines.append(f"  {f['voice']:16} {f['file']} ({f['duration_s']} s, {f['source']})")
    for f in fails:
        lines.append(f"  {f['chunk']}: {f['message']}")
    if files:
        lines.append(f"all in one file, 1 s apart, in this order: {out / 'audition-all.wav'}")
    emit(args, dict(doc, ok=bool(files)), lines, 0 if files else 1)


def render_summary_lines(project: Path, plan: dict, res: dict) -> list:
    lines = [f"render: {res['rendered']} of {res['chunks']} chunks; {res['calls']} paid call(s), about "
             f"{usd(res['est_usd'])} (budget {usd(res['budget'])}); ledger {project / 'ledger.jsonl'}"]
    for r in res["rerolls"]:
        lines.append(f"re-roll {r['chunk']} take {r['take']}: {r['why']}")
    for n in res["reroll_notes"]:
        lines.append(f"{n['chunk']}: {n['note']}")
    for f in res["failures"]:
        if not (res["stopped"] and f["kind"] == res["stop_kind"]):
            lines.append(f"{f['chunk']} take {f['take']}: {f['message']}")
    if res["stopped"]:
        lines.append("stopped: " + res["stopped"])
    if res["missing"]:
        lines.append("missing (no audio yet): " + ", ".join(res["missing"]))
    if res["flagged"]:
        have = res.get("flagged_takes") or {}
        lines.append("still failing after the re-roll (listen; `pick DIR CHUNK TAKE`, or render --only ID --takes N, "
                     "where N counts the takes already made): "
                     + ", ".join("%s (%d take%s; --takes %d for 2 more)" % (c, have.get(c, 1), "" if have.get(c, 1) == 1
                                                                          else "s", have.get(c, 1) + 2)
                                 for c in res["flagged"]))
    return lines


def cmd_render(args) -> None:
    script = Path(args.script).expanduser().resolve()
    if not script.exists():
        die(f"{script} is missing")
    project = Path(args.out).expanduser().resolve()
    project.mkdir(parents=True, exist_ok=True)
    need_filters()
    try:
        plan = build_plan(script.read_text(encoding="utf-8"), args.profile, profiles_dir(args),
                          True if args.precise else None, str(script), calibration(project))
    except (ProfileError, ToolError) as err:
        die(str(err))
    write_plan_file(project, plan)
    if plan["errors"]:
        emit(args, {"ok": False, "errors": plan["errors"]}, plan_lines(plan) + ["fix the errors above (nothing was "
                                                                               "called)"], 1)
    if plan["warnings"] and not args.force:
        emit(args, {"ok": False, "warnings": plan["warnings"]},
             plan_lines(plan) + ["render refuses warnings: fix them, or pass --force (nothing was called)"], 1)
    only = {x.strip() for x in (args.only or "").split(",") if x.strip()} or None
    if only:
        unknown = only - {c["id"] for c in plan["chunks"]}
        if unknown:
            die(f"unknown chunk(s) {', '.join(sorted(unknown))}")
    t0 = time.time()
    try:
        res = render_project(plan, project, "render", args.budget, args.takes or 0, only, args.asr)
    except BudgetError as err:
        die(str(err))
    except ToolError as err:
        die(str(err))
    except G.GeminiError as err:
        die(explain(err))
    qa = read_json(project / "qa.json") or {"chunks": [], "summary": {}}
    lines = render_summary_lines(project, plan, res) + qa_lines(qa)
    bad = bool(res["missing"]) or bool(res["stopped"])
    lines.append(f"({time.time() - t0:.1f} s) " + (
        "run render again once the problem above is solved: finished chunks are cached" if bad else
        f"next: python3 {Path(__file__).resolve()} master {project}"))
    emit(args, dict(res, ok=not bad, qa=str(project / "qa.json"), seconds=round(time.time() - t0, 1)), lines,
         1 if bad else 0)


def cmd_say(args) -> None:
    need_filters()
    out = Path(args.out).expanduser().resolve()
    if out.suffix.lower() != ".wav":
        die("--out wants a .wav file")
    side = out.with_suffix(".json")
    if out.exists() and not (side.exists() and own_file(side, "nexa-speech/say")):
        die(f"{out} exists and was not made by say: pick another name (nothing was changed)")
    text = clean_text(args.text).strip()
    if not text:
        die("say wants some text")
    pdir = profiles_dir(args)
    try:
        p = load_profile(args.profile, pdir)
    except ProfileError as err:
        die(str(err))
    script = "\n".join(line.strip() for line in text.split("\n") if line.strip() and not line.strip().startswith(
        ("@", "#", "//")))
    work = home() / "say" / sha16({"text": script, "profile": p["name"], "identity": p.get("identity")})
    try:
        plan = build_plan(script, p["name"], pdir, None, "say", calibration(work))
    except (ProfileError, ToolError) as err:
        die(str(err))
    if plan["errors"]:
        emit(args, {"ok": False, "errors": plan["errors"]}, plan_lines(plan), 1)
    if plan["warnings"] and not args.force:
        emit(args, {"ok": False, "warnings": plan["warnings"]},
             plan_lines(plan) + ["say refuses warnings: fix them, or pass --force"], 1)
    work.mkdir(parents=True, exist_ok=True)
    write_plan_file(work, plan)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        res = render_project(plan, work, "say", args.budget, ledger_dir=out.parent)
        if res["missing"]:
            emit(args, dict(res, ok=False), render_summary_lines(out.parent, plan, res), 1)
        man = master_project(work)
    except BudgetError as err:
        die(str(err))
    except ToolError as err:
        die(str(err))
    except G.GeminiError as err:
        die(explain(err))
    shutil.copy2(work / "vo_48k.wav", out)
    doc = dict(man, schema="nexa-speech/say-1", file=out.name, work=str(work), text=text,
               cost={"est_usd": res["est_usd"], "calls": res["calls"], "ledger": str(out.parent / "ledger.jsonl"),
                     "prices_as_of": PRICES_AS_OF})
    write_json(side, doc)
    lines = [f"say: {out} ({fmt_s(man['duration_s'])}, {man['loudness']['I']} LUFS, {man['loudness']['TP']} dBTP); "
             f"{res['calls']} paid call(s), about {usd(res['est_usd'])}"
             + (" (all from the cache)" if not res["calls"] else ""), f"sidecar: {side}"]
    if res["flagged"]:
        lines.append("the take still fails a gate after its re-roll: listen before you use it")
    emit(args, {"ok": True, "file": str(out), "sidecar": str(side), "calls": res["calls"], "est_usd": res["est_usd"],
                "duration_s": man["duration_s"], "loudness": man["loudness"], "flagged": res["flagged"]}, lines)


# ------------------------------------------------------------------------------------------------ CLI

def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="print one JSON object instead of the summary")
    prof = argparse.ArgumentParser(add_help=False)
    prof.add_argument("--profiles", help="the profiles folder (default ~/.nexa-speech/profiles)")
    money = argparse.ArgumentParser(add_help=False)
    money.add_argument("--budget", type=float, default=DEFAULT_BUDGET,
                       help=f"refuse work whose estimate is higher (USD, default {DEFAULT_BUDGET:.2f})")
    ap = argparse.ArgumentParser(description="Gemini text-to-speech voice-overs with one consistent voice.",
                                 parents=[common])
    ap.add_argument("--version", action="version", version=SKILL_VERSION)
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("doctor", parents=[common, prof], help="keys (names only), ffmpeg, filters, the cache")
    d.add_argument("--live", action="store_true", help="also list the models the key's project sees (free)")
    d.set_defaults(func=cmd_doctor)

    v = sub.add_parser("voices", parents=[common], help="the 30 prebuilt voices, or the voice library (--library)")
    v.add_argument("--gender", help="f or m")
    v.add_argument("--find", help="a word in the name or character")
    v.add_argument("--library", action="store_true", help="search Google's voice library (3.8, live)")
    v.add_argument("--lang", help="library: language code, for example bn-BD")
    v.add_argument("--search", help="library: free-text search")
    v.set_defaults(func=cmd_voices)

    p = sub.add_parser("presets", parents=[common], help="the 15 presets")
    p.set_defaults(func=cmd_presets)

    pr = sub.add_parser("profile", parents=[common, prof], help="profile new NAME --preset ID | show NAME | list")
    pr.add_argument("action", choices=("new", "show", "list"))
    pr.add_argument("name", nargs="?")
    pr.add_argument("--preset")
    pr.add_argument("--voice", help="a prebuilt voice name, or a voice_... id")
    pr.add_argument("--style", help="the delivery style, sent byte for byte")
    pr.add_argument("--model", help=f"default {DEFAULT_MODEL}")
    pr.add_argument("--lang", help="language code, for example bn-BD or en-GB")
    pr.add_argument("--mode", action="append", help="a delivery mode NAME=STYLE (repeatable)")
    pr.add_argument("--lexicon", help="a TSV of display<TAB>spoken (path relative to the profiles folder)")
    pr.set_defaults(func=cmd_profile)

    ds = sub.add_parser("design", parents=[common, prof, money], help="3.8 voice design; design keep ID --profile N")
    ds.add_argument("rest", nargs="*", help="keep VOICE_ID")
    ds.add_argument("--desc", help="1 or 2 sentences: age, gender, timbre, texture, accent")
    ds.add_argument("--gender", default="male")
    ds.add_argument("--lang", default="bn-BD")
    ds.add_argument("--takes", type=int, default=3)
    ds.add_argument("--model", help=f"default {DEFAULT_MODEL}")
    ds.add_argument("--name", help="display name prefix")
    ds.add_argument("--out", help="folder for the samples and design.json")
    ds.add_argument("--profile", help="design keep: the profile to pin the voice to")
    ds.set_defaults(func=cmd_design)

    au = sub.add_parser("audition", parents=[common, prof, money], help="one short text in several voices")
    au.add_argument("--voices", required=True)
    au.add_argument("--text", required=True, help="a text file, 15 s of speech or less")
    au.add_argument("--profile", required=True)
    au.add_argument("--out", required=True)
    au.set_defaults(func=cmd_audition)

    pl = sub.add_parser("plan", parents=[common, prof], help="free dry run of a script")
    pl.add_argument("script")
    pl.add_argument("--profile")
    pl.add_argument("--out", help="where plan.json goes (default: the script's folder)")
    pl.add_argument("--precise", action="store_true", help="one sentence per chunk (ads, tutorials)")
    pl.set_defaults(func=cmd_plan)

    rn = sub.add_parser("render", parents=[common, prof, money], help="synthesise, gate, re-roll once, ledger")
    rn.add_argument("script")
    rn.add_argument("--profile")
    rn.add_argument("--out", required=True)
    rn.add_argument("--takes", type=int, help="at least this many takes of every chunk (best by gate score)")
    rn.add_argument("--only", help="chunk ids, for example c003,c007")
    rn.add_argument("--force", action="store_true", help="render in spite of plan warnings")
    rn.add_argument("--precise", action="store_true", help="one sentence per chunk (ads, tutorials)")
    rn.add_argument("--asr", action="store_true", help="also run gate 4 (transcription, paid, about $0.005 a minute)")
    rn.set_defaults(func=cmd_render)

    pk = sub.add_parser("pick", parents=[common], help="choose a take by hand")
    pk.add_argument("dir")
    pk.add_argument("chunk")
    pk.add_argument("take", type=int)
    pk.set_defaults(func=cmd_pick)

    sy = sub.add_parser("say", parents=[common, prof, money], help="one line, cached and mastered")
    sy.add_argument("text")
    sy.add_argument("--profile", required=True)
    sy.add_argument("--out", required=True, help="a .wav file")
    sy.add_argument("--force", action="store_true")
    sy.set_defaults(func=cmd_say)

    q = sub.add_parser("qa", parents=[common, money], help="run the gates again")
    q.add_argument("dir")
    q.add_argument("--asr", action="store_true", help="gate 4: transcribe every chosen take (paid, small)")
    q.set_defaults(func=cmd_qa)

    m = sub.add_parser("master", parents=[common], help="vo_48k.wav and vo.manifest.json")
    m.add_argument("dir")
    m.set_defaults(func=cmd_master)

    al = sub.add_parser("align", parents=[common, money], help="words.json, sentences.json, vo.srt, vo.vtt")
    al.add_argument("dir")
    al.add_argument("--engine", choices=("auto", "gemini", "elevenlabs", "pauses"), default="auto",
                    help="gemini: Gemini 3.5 Transcribe; elevenlabs: forced alignment of the known script")
    al.set_defaults(func=cmd_align)

    ft = sub.add_parser("fit", parents=[common], help="fit scenes to target lengths")
    ft.add_argument("dir")
    ft.add_argument("--scenes", required=True)
    ft.add_argument("--ad", action="store_true", help="allow 0.90 to 1.10 tempo")
    ft.add_argument("--apply", action="store_true")
    ft.set_defaults(func=cmd_fit)

    c = sub.add_parser("cost", parents=[common], help="an estimate, or the actual numbers of a project")
    c.add_argument("dir", nargs="?")
    c.add_argument("--minutes", type=float, default=10.0)
    c.add_argument("--model")
    c.set_defaults(func=cmd_cost)
    return ap


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except ToolError as err:
        die(str(err))
    except ProfileError as err:
        die(str(err))
    except KeyboardInterrupt:
        die("interrupted; finished chunks are cached", 130)


if __name__ == "__main__":
    main()
