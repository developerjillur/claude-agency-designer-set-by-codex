#!/usr/bin/env python3
"""nexa-sound: music, sound effects, dialogue clean-up, ducking, platform mixing, QC and licence notes for videos.

  sound.py doctor [--live]                                  tools, filters, key sources (names only), helpers
  sound.py moods                                            the 12 mood templates
  sound.py brief --duration S --mood ID [--cuts F] [--speech F] [--bpm N] [--key K] [--vocals] --out brief.json
  sound.py generate BRIEF --out DIR (--draft N | --final | --realtime) [--images A,B] [--budget USD]
  sound.py fit TRACK --target S [--cuts F] [--bpm N] --out FILE
  sound.py loop TRACK --bars 8 --out FILE [--preview]
  sound.py sfx list | make NAME --out FILE | place CUES --duration S --out FILE | fetch QUERY --source S --out DIR
  sound.py clean IN --out FILE [--isolate] [--nr 12] [--hum 50|60] [--deess 0.4]
  sound.py duck --music F (--speech F | --voice F) --out FILE [--duck -14]
  sound.py mix [--dialogue F] [--voice F] [--music F] [--sfx F] [--speech F] --platform P --out FILE
  sound.py qc FILE [--brief F] [--kind music|sfx|mix] [--listen]
  sound.py library [--mood M] [--bpm 100-110] [--min S] [--max S]
  sound.py credits DIR --out CREDITS.txt
  sound.py cost [DIR]

Every command prints a short summary; --json prints one JSON object on stdout instead. Errors go to stderr and exit 1;
a failed QC exits 2. Every flag and file format: references/cli.md.
"""
import argparse
import atexit
import base64
import concurrent.futures
import datetime
import hashlib
import json
import math
import operator
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from array import array

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import beats as BT  # noqa: E402
import elevenlabs_api as EL  # noqa: E402
import gemini_api as G  # noqa: E402
import sfx_synth as SX  # noqa: E402

SKILL_VERSION = "2026.09.25.4"
SR = 48000
HQ_RESAMPLE = "aresample=48000:filter_size=64:phase_shift=10:cutoff=0.97"

MODEL_FINAL = "lyria-3.5"
MODEL_DRAFT = "lyria-3-clip-preview"
MODEL_RT = "lyria-realtime-exp"
MODEL_JUDGE = "gemini-3.8-flash"
# USD per call. Lyria prices from Google's pricing page (2026-09-25). The judge and ElevenLabs are estimates.
# ElevenLabs API list prices (pricing/api, 2026-09-25): music $0.15 a minute, sound effects $0.12 a minute billed
# per clip (the per-clip minimum is not published, so a clip is budgeted at $0.02).
PRICES = {MODEL_FINAL: 0.08, MODEL_DRAFT: 0.04, MODEL_RT: 0.0, MODEL_JUDGE: 0.01, "elevenlabs-sfx": 0.02,
          "elevenlabs-music-min": 0.15}
STAGES = {MODEL_FINAL: "GA", MODEL_DRAFT: "preview", MODEL_RT: "experimental"}
# Both Lyria models answer in MP3 only (44.1 kHz stereo, 192 kbps, with a C2PA manifest in the ID3 tag): on
# 2026-09-25 the live API refused response_format audio/wav and audio/l16 for lyria-3.5 ("Audio MIME type AUDIO_WAV
# is not supported for models/lyria-3.5"), so no format is asked for.

PLATFORMS = {"youtube": (-14.0, -1.0), "reels": (-14.0, -1.0), "tiktok": (-14.0, -1.0), "facebook": (-14.0, -1.0),
             "web": (-14.0, -1.0), "podcast": (-16.0, -1.0), "broadcast": (-23.0, -1.0)}
REF_DIALOGUE_LUFS = -20.0      # the dialogue anchor: speech stems are set here before the mix, SFX are authored to it
DUCK = {"lead": 0.25, "fall": 0.20, "tail": 0.15, "rise": 0.60, "bridge": 0.8}

SCALE_BY_MAJOR_PC = {0: "C_MAJOR_A_MINOR", 1: "D_FLAT_MAJOR_B_FLAT_MINOR", 2: "D_MAJOR_B_MINOR",
                     3: "E_FLAT_MAJOR_C_MINOR", 4: "E_MAJOR_D_FLAT_MINOR", 5: "F_MAJOR_D_MINOR",
                     6: "G_FLAT_MAJOR_E_FLAT_MINOR", 7: "G_MAJOR_E_MINOR", 8: "A_FLAT_MAJOR_F_MINOR",
                     9: "A_MAJOR_G_FLAT_MINOR", 10: "B_FLAT_MAJOR_G_MINOR", 11: "B_MAJOR_A_FLAT_MINOR"}
SCALES = sorted(SCALE_BY_MAJOR_PC.values()) + ["SCALE_UNSPECIFIED"]

LICENCE_LYRIA = {
    "source": "Google Lyria via the Gemini API (paid tier)",
    "terms": ["https://ai.google.dev/gemini-api/terms", "https://policies.google.com/terms/generative-ai/use-policy"],
    "ownership": "Google claims no ownership; similar output may be generated for others; not exclusive.",
    "indemnity": "None (Lyria is not on Google Cloud's indemnified list).",
    "content_id": "Do not register.",
    "synthid": "SynthID watermark embedded by Google in all Lyria output. Do not remove or alter.",
    "attribution_required": False,
}
LICENCE_SYNTH = {"name": "nexa-sound synthesiser", "licence": "made from scratch by the skill's own code; no samples, "
                 "no third-party rights; free to use in any work", "attribution": None}
LICENCE_PIXABAY = {"name": "Pixabay Content License", "url": "https://pixabay.com/service/license-summary/",
                   "note": "used in place from the media-use skill's folder: fine inside a video; never copy the file "
                           "into a deliverable's source folder or share it on its own"}
MEDIA_USE_SFX = os.path.join("~", ".claude", "skills", "media-use", "audio", "assets", "sfx")

FILTERS_USED = ["aresample", "acrossfade", "atrim", "afade", "apad", "adelay", "amix", "amultiply", "pan", "volume",
                "loudnorm", "alimiter", "ebur128", "astats", "silencedetect", "afftdn", "anlmdn", "adeclick",
                "adeclip", "highpass", "lowpass", "equalizer", "deesser", "acompressor", "atempo", "asetnsamples",
                "ametadata", "asetpts", "aformat", "asplit"]


# ================================================================ basics

def die(msg, code=1):
    print("nexa-sound: %s" % msg, file=sys.stderr)
    sys.exit(code)


def log(msg):
    print("[nexa-sound %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr, flush=True)


def home():
    return os.path.expanduser(os.environ.get("NEXA_SOUND_HOME") or os.path.join("~", ".nexa-sound"))


def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def rnd(v, n=3):
    return None if v is None else round(float(v), n)


def emit(args, result, lines):
    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False))
    else:
        print("\n".join(line for line in lines if line is not None))


def read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        die("%s does not exist" % path)
    except ValueError as err:
        die("%s is not valid JSON: %s" % (path, err))


def try_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def write_json(path, obj):
    d = os.path.dirname(os.path.abspath(path))
    os.makedirs(d, exist_ok=True)
    tmp = path + ".tmp-%d" % os.getpid()
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


_APPEND_LOCK = threading.Lock()


def append_jsonl(path, obj):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with _APPEND_LOCK:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(obj, ensure_ascii=False) + "\n")


def read_jsonl(path):
    out = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fmt_mmss(s):
    s = max(0, int(round(s)))
    return "%d:%02d" % (s // 60, s % 60)


def fmt_num(v):
    return str(int(v)) if float(v) == int(v) else ("%.1f" % v)


def stem_of(path):
    return os.path.splitext(os.path.abspath(path))[0]


def report_path(out, kind):
    """<out without extension>.json, unless a JSON of another kind (a track sidecar) already sits there."""
    p = stem_of(out) + ".json"
    old = try_json(p) if os.path.exists(p) else None
    if old is not None and (not isinstance(old, dict) or old.get("schema") != "nexa-sound/%s-1" % kind):
        p = stem_of(out) + ".%s.json" % kind
    return p


def check_out(out, inputs):
    """Refuse to write over an input or over a protected original."""
    o = os.path.abspath(out)
    for i in inputs:
        if i and os.path.abspath(i) == o:
            die("the output %s is also an input; pick another name (originals are never overwritten)" % out)
    if os.path.exists(o) and not os.access(o, os.W_OK):
        die("%s is read-only (a protected original?); pick another name" % out)
    os.makedirs(os.path.dirname(o) or ".", exist_ok=True)


class Work(object):
    """A temporary folder for intermediate files, removed afterwards."""

    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix="nexa-sound-")
        return self

    def path(self, name):
        return os.path.join(self.dir, name)

    def __exit__(self, *exc):
        shutil.rmtree(self.dir, ignore_errors=True)
        return False


# ================================================================ ffmpeg

def need(tool):
    p = shutil.which(os.environ.get(tool.upper()) or tool)
    if not p:
        die("%s was not found. Install it with: brew install ffmpeg" % tool)
    return p


def run_ff(args, input_bytes=None, timeout=3600, what="ffmpeg"):
    """Run ffmpeg with an argument list; stderr text back, or die with its last lines."""
    cmd = [need("ffmpeg"), "-hide_banner", "-nostdin"] + [str(a) for a in args]
    try:
        r = subprocess.run(cmd, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    except subprocess.TimeoutExpired:
        die("%s took longer than %d s and was stopped" % (what, timeout))
    err = r.stderr.decode("utf-8", "replace")
    if r.returncode != 0:
        missing = re.search(r"No such filter: '([^']+)'", err)
        if missing:
            die("this ffmpeg has no '%s' filter, which %s needs. Install a full build (brew install ffmpeg) and run "
                "sound.py doctor" % (missing.group(1), what))
        tail = " | ".join(line.strip() for line in err.strip().splitlines()[-4:])
        die("%s failed: %s" % (what, tail[-700:]))
    return err, r.stdout


_ENCODERS = None


def has_encoder(name):
    global _ENCODERS
    if _ENCODERS is None:
        try:
            _ENCODERS = subprocess.run([need("ffmpeg"), "-hide_banner", "-encoders"], capture_output=True,
                                       text=True).stdout
        except OSError:
            _ENCODERS = ""
    return (" %s " % name) in _ENCODERS


def ffmpeg_filters():
    try:
        out = subprocess.run([need("ffmpeg"), "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    except OSError:
        return set()
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and re.match(r"^[TSC.|]{2,3}$", parts[0]):
            names.add(parts[1])
    return names


def probe(path):
    if not os.path.exists(path):
        die("%s does not exist" % path)
    cmd = [need("ffprobe"), "-v", "error", "-select_streams", "a:0", "-show_entries",
           "stream=codec_name,sample_rate,channels,bits_per_raw_sample,bits_per_sample,sample_fmt,duration_ts,"
           "time_base,duration:format=duration,format_name", "-of", "json", path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffprobe could not read %s: %s" % (path, r.stderr.strip()[-300:]))
    j = json.loads(r.stdout or "{}")
    streams = j.get("streams") or []
    if not streams:
        die("%s has no audio stream" % path)
    s, f = streams[0], j.get("format") or {}
    rate = int(s.get("sample_rate") or 0)
    dur = None
    if s.get("codec_name", "").startswith("pcm") and s.get("duration_ts") and rate:
        dur = int(s["duration_ts"]) / float(rate)
    if dur is None:
        dur = float(s.get("duration") or f.get("duration") or 0.0)
    bits = int(s.get("bits_per_raw_sample") or s.get("bits_per_sample") or 0) or None
    return {"codec": s.get("codec_name"), "sample_rate": rate, "channels": int(s.get("channels") or 0),
            "bits": bits, "sample_fmt": s.get("sample_fmt"), "duration_s": round(dur, 4),
            "format": f.get("format_name")}


def to_wav(src, dst, channels=2, codec="pcm_s24le", pre=None, post=None, pad_s=None):
    """Any audio to 48 kHz WAV with the high-quality resampler; mono becomes dual mono (never a -3 dB pan law)."""
    info = probe(src)
    af = []
    if pre:
        af.append(pre)
    if channels == 2 and info["channels"] == 1:
        af.append("pan=stereo|c0=c0|c1=c0")
    elif channels == 2 and info["channels"] > 2:
        af.append("aformat=channel_layouts=stereo")
    elif channels == 1 and info["channels"] != 1:
        af.append("pan=mono|c0=0.5*c0+0.5*c1" if info["channels"] == 2 else "aformat=channel_layouts=mono")
    af.append(HQ_RESAMPLE)
    if pad_s:
        af.append("apad=pad_dur=%.3f" % pad_s)
    if post:
        af.append(post)
    run_ff(["-y", "-v", "error", "-i", src, "-af", ",".join(af), "-ar", SR, "-c:a", codec, dst])
    return info


def decode_f32(path, rate=SR, channels=2, af=None, start=None, dur=None):
    """Interleaved float samples. A mono source asked for as stereo becomes dual mono through pan, never through
    -ac 2 (ffmpeg's default upmix lowers each channel by 3 dB)."""
    if channels == 2:
        src_ch = probe(path)["channels"]
        if src_ch == 1:
            af = "pan=stereo|c0=c0|c1=c0" + ("," + af if af else "")
        elif src_ch > 2:
            af = "aformat=channel_layouts=stereo" + ("," + af if af else "")
    args = ["-v", "error"]
    if start is not None:
        args += ["-ss", "%.6f" % start]
    if dur is not None:
        args += ["-t", "%.6f" % dur]
    args += ["-i", path, "-map", "0:a:0"]
    if af:
        args += ["-af", af]
    args += ["-ac", channels, "-ar", rate, "-f", "f32le", "-"]
    _, out = run_ff(args, what="decoding %s" % os.path.basename(path))
    a = array("f")
    a.frombytes(out[: len(out) // 4 * 4])
    if sys.byteorder == "big":
        a.byteswap()
    return a


def write_f32(samples, path, rate=SR, channels=2, codec="pcm_s24le"):
    a = samples if isinstance(samples, array) else array("f", samples)
    if sys.byteorder == "big":
        a = array("f", a)
        a.byteswap()
    run_ff(["-y", "-v", "error", "-f", "f32le", "-ar", rate, "-ac", channels, "-i", "-", "-c:a", codec, path],
           input_bytes=a.tobytes(), what="writing %s" % os.path.basename(path))


def loudness(path, af=None, dualmono=False):
    """EBU R 128 integrated loudness, range and true peak (ebur128 with peak=true)."""
    flt = "ebur128=peak=true" + (":dualmono=true" if dualmono else "")
    err, _ = run_ff(["-nostats", "-v", "info", "-i", path, "-map", "0:a:0", "-af",
                     (af + "," if af else "") + flt, "-f", "null", "-"], what="loudness")
    summ = err[err.rfind("Summary:"):] if "Summary:" in err else ""

    def grab(rx):
        m = re.search(rx, summ)
        if not m or m.group(1) in ("-inf", "inf", "nan"):
            return None
        return float(m.group(1))
    i = grab(r"I:\s*(-?[0-9.]+|-inf)\s*LUFS")
    return {"I": None if i is None or i <= -69.9 else i, "LRA": grab(r"LRA:\s*(-?[0-9.]+)\s*LU"),
            "TP": grab(r"Peak:\s*(-?[0-9.]+|-inf)\s*dBFS"), "thresh": grab(r"Threshold:\s*(-?[0-9.]+)\s*LUFS")}


def momentary(path, af=None):
    """Momentary loudness (400 ms window) every 100 ms: [(window end in s, LUFS)]; silent frames are None."""
    chain = (af + "," if af else "") + ("aresample=48000,asetnsamples=n=4800:p=0,ebur128=metadata=1,"
                                        "ametadata=mode=print:key=lavfi.r128.M:file=-")
    err, out = run_ff(["-nostats", "-v", "error", "-i", path, "-map", "0:a:0", "-af", chain, "-f", "null", "-"],
                      what="momentary loudness")
    text = out.decode("utf-8", "replace") + "\n" + err
    series, t = [], None
    for line in text.splitlines():
        m = re.search(r"pts_time:\s*(-?[0-9.]+)", line)
        if m:
            t = float(m.group(1))
            continue
        m = re.search(r"lavfi\.r128\.M=(-?[0-9.]+|-?inf)", line)
        if m and t is not None:
            v = m.group(1)
            val = None if "inf" in v else float(v)
            series.append((round(t + 0.1, 3), None if val is None or val <= -69.0 else val))
            t = None
    return series


def power_mean(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return None
    return 10.0 * math.log10(sum(10 ** (v / 10.0) for v in vals) / len(vals))


def astats(path, af=None):
    err, _ = run_ff(["-nostats", "-v", "info", "-i", path, "-map", "0:a:0", "-af",
                     (af + "," if af else "") + "astats=measure_perchannel=none", "-f", "null", "-"],
                    what="astats")
    overall = err[err.rfind("Overall"):] if "Overall" in err else err

    def grab(name):
        m = re.search(re.escape(name) + r":\s*(-?[0-9.]+|-?inf)", overall)
        if not m or "inf" in m.group(1):
            return None
        return float(m.group(1))
    return {"dc_offset": grab("DC offset"), "peak_db": grab("Peak level dB"), "rms_db": grab("RMS level dB"),
            "flat_factor": grab("Flat factor"), "peak_count": grab("Peak count"),
            "samples": grab("Number of samples")}


def silences(path, noise_db=-50.0, min_d=0.75, af=None):
    err, _ = run_ff(["-nostats", "-v", "info", "-i", path, "-map", "0:a:0", "-af",
                     (af + "," if af else "") + "silencedetect=noise=%gdB:d=%g" % (noise_db, min_d), "-f", "null",
                     "-"], what="silencedetect")
    starts = [max(0.0, float(x)) for x in re.findall(r"silence_start:\s*(-?[0-9.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", err)]
    dur = probe(path)["duration_s"]
    return [[round(s, 3), round(ends[i] if i < len(ends) else dur, 3)] for i, s in enumerate(starts)]


# ================================================================ money, keys, errors

def ledger_file(start_dir, project=None):
    """The project's ledger.jsonl: --project, else the nearest one in the folder or up to two levels above it,
    else a new one in the folder."""
    if project:
        return os.path.join(os.path.abspath(project), "ledger.jsonl")
    d = os.path.abspath(start_dir)
    for _ in range(3):
        p = os.path.join(d, "ledger.jsonl")
        if os.path.exists(p):
            return p
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return os.path.join(os.path.abspath(start_dir), "ledger.jsonl")


def ledger_add(path, command, model, units, est_usd, key_source, status, **extra):
    entry = {"time": now_iso(), "skill": "nexa-sound", "command": command, "model": model, "units": units,
             "est_usd": round(est_usd, 4), "key_source": key_source, "status": status}
    entry.update({k: v for k, v in extra.items() if v is not None})
    append_jsonl(path, entry)


def guard(est, budget, what):
    if est > budget + 1e-9:
        die("%s would cost about $%.2f, over the budget of $%.2f for this run. Pass --budget %.2f (or more) to go "
            "ahead." % (what, est, budget, est))


def gemini_message(err):
    k = err.kind
    msg = str(err)
    if k == "no_key":
        return G.MISSING_KEY_HELP
    if k == "auth":
        return "the Gemini API key was refused (%s). Check or replace the key." % msg
    if k == "billing":
        return ("the key's Google Cloud project needs billing turned on (Lyria 3.5 and Lyria 3 Clip have no free "
                "tier).")
    if k == "quota_day":
        return ("the project's daily quota is used up. Wait until midnight Pacific time, or use another model "
                "(drafts run on lyria-3-clip-preview).")
    if k == "quota_minute":
        return "the per-minute quota was still exceeded after waiting and retrying. Try again in a minute."
    if k == "safety":
        return ("Google's safety filter blocked the prompt. Rephrase the brief (no artist, band, song, album or "
                "lyric references) and build it again; nexa-sound never retries a blocked prompt.")
    if k == "bad_request":
        return "Google rejected the request: %s" % msg
    if k == "timeout":
        return ("no answer within the time limit. The model may still have finished and billed the call: check the "
                "ledger before trying again. (%s)" % msg)
    if k == "server":
        return "Google's server kept failing after retries: %s" % msg
    if k == "network":
        return "network error: %s" % msg
    return msg


def secret_values():
    """Every key value this process knows (environment and the shared module's cache), for scrubbing text."""
    vals = [v for k, v in os.environ.items()
            if v and (k.startswith("GEMINI_API_KEY") or k.startswith("ELEVENLABS_API_KEY") or k == "FREESOUND_API_KEY")]
    vals += [v for _, v in (getattr(G, "_KEY_CACHE", None) or []) if v]
    vals += [v for _, v in (getattr(EL, "_KEY_CACHE", None) or []) if v]
    if _FREESOUND_KEY:
        vals.append(_FREESOUND_KEY)
    return vals


_FREESOUND_KEY = None


def freesound_key():
    """FREESOUND_API_KEY from the environment, else the macOS keychain item of that name."""
    global _FREESOUND_KEY
    if _FREESOUND_KEY is None:
        _FREESOUND_KEY = os.environ.get("FREESOUND_API_KEY", "").strip() or EL._keychain("FREESOUND_API_KEY") or ""
    return _FREESOUND_KEY or None


def scrub(text):
    text = G.scrub(text)
    for v in secret_values():
        text = text.replace(v, "***")
    return text


# ================================================================ moods, keys, briefs

def load_moods():
    with open(os.path.join(HERE, "moods.json"), "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {m["id"]: m for m in data["moods"]}


NOTE_PC = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "f": 5, "f#": 6, "gb": 6, "g": 7,
           "g#": 8, "ab": 8, "a": 9, "a#": 10, "bb": 10, "b": 11}
PC_NAME = {0: "C", 1: "Db", 2: "D", 3: "Eb", 4: "E", 5: "F", 6: "F#", 7: "G", 8: "Ab", 9: "A", 10: "Bb", 11: "B"}


def parse_key(text):
    """'C major', 'A minor', 'F#m', 'Bb' -> (pitch class, 'major' or 'minor', 'C major')."""
    t = str(text).strip().replace("\u266f", "#").replace("\u266d", "b")
    m = re.match(r"^([A-Ga-g])\s*(#|b|sharp|flat)?\s*(major|minor|maj|min|m)?$", t, re.I)
    if not m:
        raise ValueError("key %r is not like 'C major', 'A minor' or 'F# minor'" % text)
    acc = (m.group(2) or "").lower()
    acc = "#" if acc in ("#", "sharp") else ("b" if acc in ("b", "flat") else "")
    pc = NOTE_PC[m.group(1).lower() + acc]
    mode_raw = (m.group(3) or "major")
    mode = "minor" if mode_raw.lower() in ("minor", "min") or mode_raw == "m" else "major"
    return pc, mode, "%s %s" % (PC_NAME[pc], mode)


def scale_for_key(text):
    pc, mode, _ = parse_key(text)
    major_pc = pc if mode == "major" else (pc + 3) % 12
    return SCALE_BY_MAJOR_PC[major_pc]


def read_cuts(path):
    """Cuts from a list ([{t, weight, label}] or [seconds]) or an EDL {"cuts": [...], "speech": [...]}.
    Returns (cuts, speech spans or None, duration or None)."""
    data = read_json(path)
    speech, duration = None, None
    if isinstance(data, dict):
        speech = spans_from(data) if any(k in data for k in ("speech", "spans", "words")) else None
        duration = data.get("duration_s") or data.get("duration")
        data = data.get("cuts") or []
    cuts = []
    for c in data if isinstance(data, list) else []:
        if isinstance(c, (int, float)):
            cuts.append({"t": float(c), "weight": 1.0, "label": ""})
        elif isinstance(c, dict) and c.get("t") is not None:
            cuts.append({"t": float(c["t"]), "weight": float(c.get("weight", 1.0) or 1.0),
                         "label": str(c.get("label") or "")})
    cuts.sort(key=lambda c: c["t"])
    return cuts, speech, (float(duration) if duration else None)


def merge_spans(spans, gap=0.0):
    out = []
    for s, e in sorted((float(a), float(b)) for a, b in spans if b > a):
        if out and s - out[-1][1] <= gap:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [[round(a, 3), round(b, 3)] for a, b in out]


def spans_from(data):
    """Speech spans from [[s, e]], [{start, end}], nexa-speech words.json [{w, start, end}], or a dict with
    "spans", "speech" or "words"."""
    if isinstance(data, dict):
        for k in ("spans", "speech"):
            if k in data:
                return spans_from(data[k])
        if "words" in data:
            return spans_from(data["words"])
        return []
    if not isinstance(data, list):
        return []
    spans, words = [], False
    for item in data:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            spans.append((float(item[0]), float(item[1])))
        elif isinstance(item, dict) and item.get("start") is not None and item.get("end") is not None:
            spans.append((float(item["start"]), float(item["end"])))
            words = words or any(k in item for k in ("w", "word", "text"))
    return merge_spans(spans, gap=0.3 if words else 0.0)


def read_speech(path):
    return spans_from(read_json(path))


KINDS = [
    ("reveal", ("reveal", "launch", "product", "drop", "hero", "unveil", "logo"), 7,
     "lift: fuller drums and a bright lead layer"),
    ("cta", ("cta", "call to action", "buy", "shop", "order", "subscribe", "sign up", "signup", "download",
             "contact", "offer"), 7, "confident and full, heading for the ending"),
    ("end", ("end", "outro", "endcard", "end card", "credits", "closing"), 4, "resolve toward the final chord"),
    ("intro", ("intro", "hook", "open", "opening", "title", "start"), 4, "set the mood with the main motif"),
    ("tension", ("problem", "pain", "tension", "before", "issue", "struggle"), 3,
     "sparser and darker, holding tension"),
    ("build", ("build", "rise", "climb", "montage", "demo", "feature", "features", "steps", "how"), 5,
     "building: add rhythm and movement"),
    ("story", ("testimonial", "quote", "story", "review", "people", "team"), 3, "warm and gentle"),
]


CANON_LABEL = {"reveal": "Reveal", "cta": "Call to action", "end": "Outro", "intro": "Intro", "tension": "Tension",
               "build": "Build", "story": "Story"}


def _kind_of(label):
    low = label.lower()
    for kind, words, intensity, change in KINDS:
        if any(re.search(r"\b%s\b" % re.escape(w), low) for w in words):
            return kind, intensity, change
    return None, None, None


def _clean_label(label):
    text = re.sub(r"[\"'\u2018\u2019\u201c\u201d\u00ab\u00bb\[\]]", "", label or "").strip()
    text = " ".join(text.split()[:4])
    return text[:1].upper() + text[1:] if text else ""


def build_sections(duration, cuts, speech, min_len=3.0, max_sections=8):
    """Sections between cuts with a label, what changes and an intensity (05 section 7.3)."""
    inner = [dict(c) for c in cuts if 0.5 < c["t"] < duration - 0.5]
    while True:
        bounds = [0.0] + [c["t"] for c in inner] + [duration]
        short = [i for i in range(len(bounds) - 1) if bounds[i + 1] - bounds[i] < min_len]
        if not short and len(inner) + 1 <= max_sections:
            break
        if not inner:
            break
        if short:
            i = short[0]
            # drop the weaker of the cuts that bound this short section
            cand = [j for j in (i - 1, i) if 0 <= j < len(inner)]
        else:
            cand = list(range(len(inner)))
        j = min(cand, key=lambda k: (inner[k]["weight"], -inner[k]["t"]))
        inner.pop(j)
    bounds = [0.0] + [c["t"] for c in inner] + [duration]
    sections = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        cut = inner[i - 1] if i > 0 else None
        raw = _clean_label(cut["label"]) if cut else ""
        kind, intensity, change = _kind_of(raw) if raw else (None, None, None)
        covered = sum(max(0.0, min(b, e) - max(a, s)) for s, e in (speech or []))
        share = covered / (b - a) if b > a else 0.0
        narrated = share >= 0.5
        if kind is None:
            if i == 0:
                kind, intensity, change = "intro", 4, "set the mood with the main motif"
            elif i == len(bounds) - 2 and b - a >= 3.0:
                kind, intensity, change = "end", 4, "resolve toward the final chord"
            else:
                w = cut["weight"] if cut else 1.0
                kind, change = "section", "a gentle change of texture"
                intensity = 7 if w >= 2.0 else (6 if w >= 1.5 else 5)
        if narrated:
            if kind in ("reveal", "cta"):
                intensity = 6
            else:
                intensity = 2 if share > 0.8 else 3
                change = "sparse and supportive under the voice-over, simple chords, no lead melody"
        # the prompt gets a plain label for the section's role, never the edit list's own words (they can hold
        # brand or product names, which Lyria prompts must not carry)
        label = CANON_LABEL.get(kind) or "Section %d" % (i + 1)
        sections.append({"start": round(a, 2), "end": round(b, 2), "label": label, "cut_label": raw or None,
                         "kind": kind,
                         "change": change, "intensity": int(intensity), "narrated": narrated,
                         "speech_share": round(share, 2)})
    return sections


def section_line(s):
    change = s["change"][:1].upper() + s["change"][1:]
    return "[%s - %s] %s: %s. Intensity: %d/10" % (fmt_mmss(s["start"]), fmt_mmss(s["end"]), s["label"],
                                                     change.rstrip("."), s["intensity"])


BLOCK_PATTERNS = [
    (r"\bin the (?:style|vein|manner) of\b", "in the style of"),
    (r"\b(?:a la|\u00e0 la)\s+[a-z]", "a la"),
    (r"\bcover (?:of|version)\b", "cover of"),
    (r"\bremix of\b", "remix of"),
    (r"\btribute to\b", "tribute to"),
    (r"\bsound-?alike\b", "soundalike"),
    (r"\bfeat\.|\bft\.|\bfeaturing\b", "featuring"),
    (r"\b(?:rabindra ?sangeet|nazrul (?:geeti|sangeet)|lalon(?: geeti)?|tagore)\b",
     "a genre named after a person (describe it instead: for example an early 20th century Bengali art-song feel "
     "with harmonium, esraj and tabla)"),
]
LIKE_OK = {"a", "an", "the", "this", "that", "it", "when", "in", "on", "at", "to", "we", "you", "they", "i", "he",
           "she", "us", "them", "our", "your", "their", "its", "his", "her", "my", "one", "some", "any", "these",
           "those", "rain", "wind", "water", "waves"}


# "like", then up to three small words ("a", "the", "young", "early"...), then the word that may be a name
LIKE_RX = re.compile(r"\b(?i:like)\s+(?:(?i:a|an|the|some|young|old|early|late|modern|classic|vintage|new)\s+){0,3}"
                     r"([A-Za-z][\w'&.-]*)")


def name_problems(text, quotes=True, lyric=False):
    """Why a prompt would name an artist, band, song or album (05 sections 1.9 and 3.2); [] when it is clean."""
    found = []
    low = text.lower()
    for rx, why in BLOCK_PATTERNS:
        if re.search(rx, low):
            found.append(why)
    for m in LIKE_RX.finditer(text):
        if lyric and re.search(r"(^\s*|[\n.!?]\s*)$", text[:m.start()]):
            continue
        word = m.group(1).rstrip(".,;:!?")
        if word[:1].isupper() and word.lower() not in LIKE_OK:
            found.append("like %s" % word)
    if not quotes:
        return found
    quote = "\"\u201c\u201d\u00ab\u00bb"
    for m in re.finditer("[%s]([^%s]{2,80})[%s]" % (quote, quote, quote), text):
        found.append('quoted title "%s"' % m.group(1).strip())
    for m in re.finditer(r"(?:^|[\s(])[\u2018']([^'\u2018\u2019\n]{2,60})[\u2019'](?=[\s).,;:!?]|$)", text):
        found.append("quoted title '%s'" % m.group(1).strip())
    return found


def render_template(tpl, dur_prompt, bpm, key, drop, section_lines):
    text = tpl.replace("{DUR}", str(dur_prompt)).replace("{BPM}", fmt_num(bpm)).replace("{KEY}", key)
    text = text.replace("{DROP}", fmt_num(drop))
    block = ("\n" + "\n".join(section_lines) + "\n") if section_lines else " "
    text = text.replace(" {SECTIONS} ", block).replace("{SECTIONS}", block.strip())
    return re.sub(r"[ \t]+", " ", text).strip()


def cmd_moods(args):
    moods = load_moods()
    rows = []
    for m in moods.values():
        rows.append({"id": m["id"], "name": m["name"], "use_for": m["use_for"], "bpm": m["bpm"], "key": m["key"],
                     "ending": m["ending"], "variants": sorted((m.get("variants") or {}).keys()),
                     "template": m["template"]})
    lines = ["%-14s %-34s %4s  %-9s %s" % ("id", "name", "bpm", "key", "use for")]
    lines += ["%-14s %-34s %4s  %-9s %s" % (r["id"], r["name"], r["bpm"], r["key"], r["use_for"]) for r in rows]
    emit(args, {"ok": True, "moods": rows}, lines)


def cmd_brief(args):
    moods = load_moods()
    if args.mood not in moods:
        die("no mood %r; pick one of: %s" % (args.mood, ", ".join(moods)))
    mood = dict(moods[args.mood])
    if args.variant:
        var = (mood.get("variants") or {}).get(args.variant)
        if not var:
            die("mood %s has no variant %r" % (args.mood, args.variant))
        mood.update(var)
    if not 3.0 <= args.duration <= 600.0:
        die("--duration must be between 3 and 600 seconds")
    cuts, edl_speech, _ = read_cuts(args.cuts) if args.cuts else ([], None, None)
    speech = read_speech(args.speech) if args.speech else (edl_speech or [])
    bpm = float(args.bpm or mood["bpm"])
    if not 60 <= bpm <= 200:
        die("--bpm must be between 60 and 200 (the range Lyria RealTime and the beat grid use)")
    try:
        key = parse_key(args.key or mood["key"])[2]
        scale = scale_for_key(key)
    except ValueError as err:
        die(str(err))
    D = float(args.duration)
    sections = build_sections(D, cuts, speech)
    drop = max(cuts, key=lambda c: (c["weight"], -c["t"]))["t"] if cuts else round(D * 0.4)
    dur_prompt = int(math.ceil(D + 2.0))
    lines = [section_line(s) for s in sections] if cuts or speech else []
    prompt = render_template(mood["template"], dur_prompt, bpm, key, round(drop), lines)
    notes = (args.notes or "").strip()
    if args.vocals:
        prompt = re.sub(r"\s*\bInstrumental\.\s*$", "", prompt)
        prompt = re.sub(r"\binstrumental\s+", "", prompt, flags=re.I)
        prompt = prompt + " With lead vocals." + ("\n" + notes if notes else "")
    else:
        if notes:
            prompt = re.sub(r"\s*\bInstrumental\.\s*$", "", prompt) + " " + notes.rstrip(".") + "."
        if not prompt.endswith("Instrumental."):
            prompt = prompt.rstrip() + " Instrumental."
    # lyrics the user wrote (under a "Lyrics:" header) get only the strong checks: a sung line may well start with
    # "Like" and a capital, which is no reference to an artist
    m = re.search(r"(?i)\blyrics:", prompt)
    head, lyrics = (prompt[:m.start()], prompt[m.end():]) if m else (prompt, "")
    if lyrics.strip() and not args.vocals:
        die("brief refused: a Lyrics: section needs --vocals (an instrumental brief has no lyrics)")
    problems = name_problems(head) + (name_problems(lyrics, quotes=False, lyric=True) if lyrics else [])
    if problems:
        die("brief refused: the prompt names or quotes an artist, band, song or album (%s). Lyria blocks these "
            "and Google's terms forbid asking for an artist's voice or a real song. Describe the sound instead: "
            "genre and era, instruments, tempo, key and mood (references/music-craft.md). A flagged word that is "
            "not a name can be written in lower case." % "; ".join(problems))
    rt = mood.get("realtime") or {}
    automation = []
    for s in sections[1:]:
        automation.append({"t": s["start"], "density": round(min(1.0, 0.25 + 0.06 * s["intensity"]), 2),
                           "brightness": round(min(1.0, 0.4 + 0.04 * s["intensity"]), 2),
                           "mute_drums": s["intensity"] <= 2})
    brief = {
        "schema": "nexa-sound/brief-1", "skill_version": SKILL_VERSION, "created": now_iso(),
        "mood": mood["id"], "variant": args.variant, "mood_name": mood["name"],
        "duration_s": round(D, 3), "prompt_duration_s": dur_prompt, "bpm": bpm, "key": key, "scale": scale,
        "vocals": bool(args.vocals), "notes": notes or None, "ending": mood["ending"], "drop_s": round(drop, 2),
        "sections": sections, "cuts": cuts, "speech": speech,
        "cuts_file": os.path.abspath(args.cuts) if args.cuts else None,
        "speech_file": os.path.abspath(args.speech) if args.speech else None,
        "prompt": prompt,
        "realtime": {"weighted_prompts": rt.get("prompts") or [], "derived": bool(rt.get("derived")),
                     "config": {"bpm": int(round(bpm)), "scale": scale, "density": rt.get("density", 0.45),
                                "brightness": rt.get("brightness", 0.55), "guidance": 4.0,
                                "mute_drums": bool(sections and sections[0]["intensity"] <= 2)},
                     "automation": automation},
        "checks": {"names": "ok"},
    }
    write_json(args.out, brief)
    out_lines = ["brief: %s (%s), %s s video, prompt asks for %d s at %s BPM, %s, %s" % (
        mood["id"], mood["name"], fmt_num(D), dur_prompt, fmt_num(bpm), key,
        "with vocals" if args.vocals else "instrumental"),
        "sections: %d%s" % (len(sections), "" if lines else " (not written into the prompt: no cuts or speech given)"),
        "written: %s" % args.out]
    emit(args, {"ok": True, "brief": os.path.abspath(args.out), "prompt": prompt, "sections": sections,
                "bpm": bpm, "key": key, "prompt_duration_s": dur_prompt}, out_lines)


def read_brief(path):
    b = read_json(path)
    if not isinstance(b, dict) or b.get("schema") != "nexa-sound/brief-1":
        die("%s is not a nexa-sound brief (make one with: sound.py brief ...)" % path)
    b["_path"] = os.path.abspath(path)
    return b


# ================================================================ generate

TIMED = re.compile(r"^\s*\[(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)?\]\s*(.*)$")
SECTION_TAG = re.compile(r"\[\[([^\]]+)\]\]")
NOT_LYRICS = {"instrumental", "intro", "outro", "verse", "chorus", "bridge", "break", "solo", "interlude", "drop",
              "build", "end", "ending", "silence", "music", "no", "vocals", "hook", "pre", "post", "section", "fade",
              "out", "in", "instrumental.", "breakdown", "riser"}


def timed_lines(texts):
    out = []
    for text in texts:
        for line in str(text).splitlines():
            m = TIMED.match(line)
            if m:
                out.append({"start": float(m.group(1)), "end": float(m.group(2)) if m.group(2) else None,
                            "text": m.group(3).strip()})
    return out


def lyric_like(text):
    t = re.sub(r"\[[^\]]*\]", " ", text)
    words = [w for w in re.findall(r"[^\W\d_]{2,}", t.lower())]
    return any(w not in NOT_LYRICS for w in words)


def section_tags(texts):
    return [m for text in texts for m in SECTION_TAG.findall(str(text))]


def has_c2pa(data):
    """A C2PA manifest where Google puts it: a GEOB frame of type application/c2pa in the MP3's ID3 tag, or a C2PA or
    JUMBF chunk in a WAV. Only those regions are searched, never the audio itself."""
    if data[:3] == b"ID3" and len(data) >= 10:
        size = ((data[6] & 0x7F) << 21) | ((data[7] & 0x7F) << 14) | ((data[8] & 0x7F) << 7) | (data[9] & 0x7F)
        return b"application/c2pa" in data[10:10 + size].lower() or b"c2pa" in data[10:10 + size].lower()
    if data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        i = 12
        while i + 8 <= len(data):
            cid = data[i:i + 4].lower()
            if cid in (b"c2pa", b"jumb"):
                return True
            size = int.from_bytes(data[i + 4:i + 8], "little")
            i += 8 + size + (size & 1)
    return False


def next_ids(out_dir, mood, n):
    """Ids for n new takes, each reserved at once by a lock file created exclusively. Two runs in the same minute
    and folder (a draft and a final side by side, two terminals) would otherwise pick the same name before either
    had saved, and the second paid take could not be written. release_id removes the lock when the take is done."""
    base = "ns_%s_%s" % (datetime.datetime.now().strftime("%Y-%m-%d_%H%M"), re.sub(r"[^a-z0-9]+", "-", mood))
    ids, k = [], 0
    letters = "abcdefghijklmnopqrstuvwxyz"
    while len(ids) < n:
        tid = base + "_" + (letters[k] if k < 26 else "z%d" % k)
        k += 1
        if any(f.startswith(tid + "_orig") or f == tid + ".json" for f in os.listdir(out_dir)):
            continue
        try:
            fd = os.open(id_lock(out_dir, tid), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            continue
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.close(fd)
        ids.append(tid)
    return ids


def id_lock(out_dir, tid):
    return os.path.join(out_dir, "." + tid + ".lock")


def release_id(out_dir, tid):
    try:
        os.remove(id_lock(out_dir, tid))
    except OSError:
        pass


def image_blocks(spec, work):
    blocks, meta = [], []
    for p in [x.strip() for x in (spec or "").split(",") if x.strip()]:
        if not os.path.exists(p):
            die("image %s does not exist" % p)
        ext = os.path.splitext(p)[1].lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(ext)
        src = p
        if mime is None or os.path.getsize(p) > 1500000:
            src = work.path("img%d.jpg" % len(blocks))
            run_ff(["-y", "-v", "error", "-i", p, "-vf", "scale='min(1280,iw)':-2", "-q:v", "3", src],
                   what="shrinking %s" % os.path.basename(p))
            mime = "image/jpeg"
        with open(src, "rb") as fh:
            data = fh.read()
        blocks.append({"type": "image", "mime_type": mime, "data": base64.b64encode(data).decode("ascii")})
        meta.append({"file": os.path.abspath(p), "sha256": sha256(p), "mime_type": mime, "sent_bytes": len(data)})
    if len(blocks) > 10:
        die("Lyria takes at most 10 images")
    return blocks, meta


def library_path():
    return os.path.join(home(), "library.jsonl")


def library_add(entry):
    append_jsonl(library_path(), entry)


def library_entries():
    latest = {}
    for e in read_jsonl(library_path()):
        if e.get("id"):
            prev = latest.get(e["id"], {})
            prev.update({k: v for k, v in e.items() if v is not None})
            latest[e["id"]] = prev
    return list(latest.values())


def analyse_track(path, bpm_hint, beats_out=None):
    ana = {}
    lo = loudness(path)
    ana.update({"lufs_i": rnd(lo["I"], 1), "true_peak_dbtp": rnd(lo["TP"], 1), "lra_lu": rnd(lo["LRA"], 1)})
    try:
        g = BT.analyze(path, bpm_hint)
        ana.update({"bpm": g["bpm"], "bar_s": g["bar_s"], "first_downbeat_s": g["first_downbeat_s"],
                    "beat_confidence": g["confidence"]})
        if beats_out:
            write_json(beats_out, g)
            ana["downbeats_file"] = os.path.abspath(beats_out)
    except BT.BeatError as err:
        ana["beat_error"] = str(err)
    return ana


def brief_summary(brief):
    return {"file": brief.get("_path"), "mood": brief.get("mood"), "variant": brief.get("variant"),
            "bpm": brief.get("bpm"), "key": brief.get("key"), "vocals": brief.get("vocals"),
            "duration_s": brief.get("duration_s"), "ending": brief.get("ending"),
            "sections": brief.get("sections")}


def run_take(brief, body, model, out_dir, tid, ledger, project, images_meta):
    result = None
    try:
        result = _run_take(brief, body, model, out_dir, tid, ledger, project, images_meta)
        return result
    finally:
        release_id(out_dir, tid)
        if result and result.get("id") != tid:
            release_id(out_dir, result["id"])


def output_block_s():
    try:
        return float(os.environ.get("NEXA_SOUND_OUTPUT_BLOCK_S", "8"))
    except ValueError:
        return 8.0


def lyria_call(body, model, ledger, tid):
    """(response, info, blocked tracks) for one take.

    A track Google blocks after making it (seconds of generation, then "Request blocked for an unspecified
    policy reason": Lyria screens its output, for likeness to existing music among other things) is made once
    more, because a new take usually passes: on 2026-09-25 the same prompt passed at 17:26, was blocked at 17:33
    and passed again at 17:34. The blocked take is a 400 answer and is logged at $0. A prompt blocked at once is
    never retried: it would be blocked again."""
    blocked = 0
    while True:
        started = time.time()
        try:
            resp, info = G.interactions(body, timeout=600)
            return resp, info, blocked
        except G.GeminiError as err:
            if err.kind == "safety" and blocked == 0 and time.time() - started >= output_block_s():
                blocked += 1
                ledger_add(ledger, "generate", model, 1, 0.0, None, "blocked", id=tid, error_kind="safety",
                           note="blocked after %.0f s of generation; made once more" % (time.time() - started))
                log("%s: Google blocked the finished track (%s); making it once more" % (tid, scrub(str(err))[:120]))
                continue
            err.output_blocked = blocked + (1 if err.kind == "safety" and time.time() - started >= output_block_s()
                                            else 0)
            raise


def _run_take(brief, body, model, out_dir, tid, ledger, project, images_meta):
    t0 = time.time()
    try:
        resp, info, blocked = lyria_call(body, model, ledger, tid)
    except G.GeminiError as err:
        ledger_add(ledger, "generate", model, 1, PRICES[model] if err.kind == "timeout" else 0.0, None,
                   "failed", id=tid, error_kind=err.kind)
        message = gemini_message(err)
        if err.kind == "safety" and getattr(err, "output_blocked", 0):
            message = ("Google blocked the finished track %d time(s) (\"an unspecified policy reason\", raised after "
                       "generation: Lyria screens its output). Run it again later, or change the brief's instruments "
                       "or tempo a little." % err.output_blocked)
        return {"id": tid, "ok": False, "error_kind": err.kind, "error": scrub(message)}
    latency = round(time.time() - t0, 1)
    parts = G.audio_parts(resp)
    texts = G.text_parts(resp)
    if not parts:
        ledger_add(ledger, "generate", model, 1, PRICES[model], info.get("key"), "empty", id=tid)
        return {"id": tid, "ok": False, "error_kind": "empty",
                "error": "the answer had no audio (the output may have been filtered). Text parts: %s" % (
                    scrub(" | ".join(texts))[:300] or "none")}
    part = parts[-1]
    ext = G.audio_extension(part["bytes"], part.get("mime_type"))
    if os.path.exists(os.path.join(out_dir, tid + "_orig" + (".wav" if ext == ".pcm" else ext))):
        tid = next_ids(out_dir, brief.get("mood") or "track", 1)[0]   # never over another take's original
    # the paid call goes into the ledger before the file is written: a save that fails must not hide it
    ledger_add(ledger, "generate", model, 1, PRICES[model], info.get("key"), "ok", id=tid)
    path = G.save_audio(part, os.path.join(out_dir, tid + "_orig"), default_rate=48000, default_channels=2)
    with open(path, "rb") as fh:
        raw = fh.read()
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    timed = timed_lines(texts)
    lyric = [t for t in timed if lyric_like(t["text"])]
    vocals_suspected = bool(lyric) and not brief.get("vocals")
    side_path = os.path.join(out_dir, tid + ".json")
    sidecar = {
        "schema": "nexa-sound/track-1", "id": tid, "created_at": now_iso(),
        "tool": {"skill": "nexa-sound", "version": SKILL_VERSION},
        "provider": {"api": "gemini-api", "endpoint": "POST /v1beta/interactions", "model": model,
                     "stage": STAGES.get(model), "interaction_id": resp.get("id"), "store": False,
                     "key_var_used": info.get("key")},
        "request": {"prompt": brief["prompt"], "lyrics": None, "images": images_meta,
                    "response_format": None,
                    "realtime": None, "seed": None, "requested_duration_s": brief.get("prompt_duration_s"),
                    "brief": brief_summary(brief)},
        "response": {"text_parts": texts, "timed_lines": timed, "section_labels": section_tags(texts),
                     "vocals_suspected": vocals_suspected, "filtered": False, "blocked_before": blocked or None,
                     "latency_s": latency,
                     "cost_usd_est": PRICES[model], "status": G.status(resp), "usage": G.usage(resp) or None},
        "original": {"file": os.path.abspath(path), "sha256": hashlib.sha256(raw).hexdigest(),
                     "format": os.path.splitext(path)[1].lstrip("."), "bytes": len(raw),
                     "c2pa_manifest_present": has_c2pa(raw), "read_only": True,
                     "synthid": LICENCE_LYRIA["synthid"]},
        "analysis": {}, "fit": None, "qc": None, "licence": dict(LICENCE_LYRIA),
        "usage": {"project": os.path.abspath(project) if project else None, "video_edl": brief.get("cuts_file"),
                  "approved_by": None},
    }
    write_json(side_path, sidecar)             # the provenance is on disk before any analysis can fail
    try:
        pr = probe(path)
        sidecar["original"].update({"sample_rate": pr["sample_rate"], "channels": pr["channels"],
                                    "duration_s": pr["duration_s"]})
        sidecar["analysis"] = analyse_track(path, brief.get("bpm"), os.path.join(out_dir, tid + ".beats.json"))
        ana = sidecar["analysis"]
        qc = measured_checks(path, "music", brief_summary(brief), sidecar,
                             lo={"I": ana.get("lufs_i"), "TP": ana.get("true_peak_dbtp"), "LRA": ana.get("lra_lu")})
        sidecar["qc"] = qc_summary(qc, None, brief_summary(brief), "music")
    except (Exception, SystemExit) as err:     # keep the paid-for take even when a measurement fails
        sidecar["qc"] = {"passed": False, "failed": ["analysis"], "warnings": [], "error": scrub(str(err))}
        pr = {"duration_s": sidecar["original"].get("duration_s")}
    write_json(side_path, sidecar)
    library_add({"id": tid, "mood": brief.get("mood"), "bpm": sidecar["analysis"].get("bpm") or brief.get("bpm"),
                 "bpm_requested": brief.get("bpm"), "key": brief.get("key"), "duration_s": pr["duration_s"],
                 "file": os.path.abspath(path), "sidecar": os.path.abspath(side_path), "model": model,
                 "vocals": brief.get("vocals"), "qc_passed": sidecar["qc"]["passed"],
                 "qc_failed": sidecar["qc"]["failed"], "created": now_iso()})
    return {"id": tid, "ok": True, "file": os.path.abspath(path), "sidecar": os.path.abspath(side_path),
            "format": sidecar["original"]["format"], "duration_s": pr["duration_s"],
            "bpm": sidecar["analysis"].get("bpm"), "qc_passed": sidecar["qc"]["passed"],
            "qc_failed": sidecar["qc"]["failed"], "vocals_suspected": vocals_suspected, "latency_s": latency}


def pick_engine(args):
    """elevenlabs or lyria. A Lyria mode (--draft, --final, --realtime) means Lyria; --engine says it outright;
    otherwise ElevenLabs when its key is here and the plan allows client work, else a Lyria final."""
    lyria_mode = bool(args.draft or args.final or args.realtime)
    if args.engine == "elevenlabs":
        if lyria_mode:
            die("--draft, --final and --realtime are Lyria modes; ElevenLabs takes --takes N")
        return "elevenlabs"
    if args.engine == "lyria" or lyria_mode:
        if not lyria_mode:
            args.final = True
        return "lyria"
    if EL.keys():
        plan = eleven_plan()
        if plan.get("paid") is True:
            return "elevenlabs"
        log("ElevenLabs is here but %s; making a Lyria final instead (--engine elevenlabs to try it anyway)"
            % ("the plan is free" if plan.get("paid") is False else "its plan is unknown"))
    args.final = True
    return "lyria"


def cmd_generate(args):
    brief = read_brief(args.brief)
    engine = pick_engine(args)
    os.makedirs(args.out, exist_ok=True)
    ledger = ledger_file(args.out, args.project)
    if engine == "elevenlabs":
        return generate_eleven(args, brief, ledger)
    modes = [bool(args.draft), bool(args.final), bool(args.realtime)]
    if sum(modes) != 1:
        die("choose one of --draft N, --final or --realtime")
    if args.realtime:
        return generate_realtime(args, brief, ledger)
    model = MODEL_DRAFT if args.draft else MODEL_FINAL
    takes = int(args.draft or args.takes or 1)
    if not 1 <= takes <= (10 if args.draft else 3):
        die("--draft takes 1 to 10 takes, --final 1 to 3")
    est = PRICES[model] * takes
    guard(est, args.budget, "%d %s call%s" % (takes, model, "s" if takes > 1 else ""))
    if not G.keys():
        die(G.MISSING_KEY_HELP)
    if args.draft and brief.get("duration_s", 30) > 30:
        log("drafts on %s are always 30 s long: they are for choosing a style, then --final makes the length"
            % MODEL_DRAFT)
    with Work() as work:
        imgs, imgs_meta = image_blocks(args.images, work)
        prompt = brief["prompt"]
        body = {"model": model, "input": ([{"type": "text", "text": prompt}] + imgs) if imgs else prompt,
                "store": False}
        ids = next_ids(args.out, brief.get("mood") or "track", takes)
        log("%d call%s to %s (about $%.2f)" % (takes, "s" if takes > 1 else "", model, est))
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, takes)) as pool:
            futs = [pool.submit(run_take, brief, body, model, args.out, tid, ledger, args.project, imgs_meta)
                    for tid in ids]
            results = [f.result() for f in futs]
    ok = [r for r in results if r["ok"]]
    lines = []
    for r in results:
        if r["ok"]:
            lines.append("%s: %s, %.1f s, %s BPM, QC %s%s" % (
                r["id"], r["format"], r["duration_s"], r.get("bpm"), "passed" if r["qc_passed"] else
                "failed (%s)" % ", ".join(r["qc_failed"]), ", VOCALS in an instrumental" if r["vocals_suspected"]
                else ""))
        else:
            lines.append("%s: failed: %s" % (r["id"], r["error"]))
    lines.append("cost: about $%.2f (%d of %d calls returned audio); ledger %s" % (
        PRICES[model] * len(ok), len(ok), takes, ledger))
    emit(args, {"ok": bool(ok), "model": model, "takes": results, "est_usd": round(est, 2), "ledger": ledger},
         lines)
    if not ok:
        sys.exit(1)


def venv_python(create):
    override = os.environ.get("NEXA_SOUND_VENV_PYTHON")
    if override:
        return override
    venv = os.path.join(home(), "venv")
    py = os.path.join(venv, "bin", "python")
    if os.path.exists(py):
        chk = subprocess.run([py, "-c", "import google.genai"], capture_output=True)
        if chk.returncode == 0:
            return py
    if not create:
        return None
    uv = shutil.which("uv")
    if not uv:
        die("Lyria RealTime needs its own Python 3.12 environment, made with uv. Install uv first "
            "(brew install uv), then run this again.")
    log("first use of Lyria RealTime: creating %s with uv (Python 3.12) and installing google-genai>=2.9. This "
        "downloads the package (and Python 3.12 if uv has none), once." % venv)
    r = subprocess.run([uv, "venv", "--python", "3.12", venv], capture_output=True, text=True)
    if r.returncode != 0:
        die("uv could not create the environment: %s" % r.stderr.strip()[-400:])
    r = subprocess.run([uv, "pip", "install", "--python", py, "google-genai>=2.9"], capture_output=True, text=True)
    if r.returncode != 0:
        die("installing google-genai failed: %s" % r.stderr.strip()[-400:])
    return py


def generate_realtime(args, brief, ledger):
    rt = brief.get("realtime") or {}
    prompts = rt.get("weighted_prompts") or []
    if not prompts:
        die("the brief has no RealTime prompts")
    config = dict(rt.get("config") or {})
    if args.seed is not None:
        config["seed"] = int(args.seed)
    seconds = float(brief["duration_s"]) + 3.0
    if seconds > 540:
        die("a RealTime session stops at about 10 minutes; record at most 9 minutes (or loop a shorter bed)")
    if not G.keys():
        die(G.MISSING_KEY_HELP)
    py = venv_python(create=True)
    tid = next_ids(args.out, brief.get("mood") or "bed", 1)[0]
    atexit.register(release_id, args.out, tid)     # also after die(): one recording per run
    orig = os.path.join(args.out, tid + "_orig.wav")
    with Work() as work:
        cfg_path = work.path("realtime.json")
        write_json(cfg_path, {"weighted_prompts": prompts, "config": config, "automation": rt.get("automation") or [],
                              "seconds": seconds, "preroll": 8.0, "api_version": "v1beta"})
        log("recording %.0f s of Lyria RealTime (real time: about %.0f s plus setup)" % (seconds, seconds + 11))
        t0 = time.time()
        r = subprocess.run([py, os.path.join(HERE, "realtime.py"), "--config", cfg_path, "--out", orig, "--json"],
                           capture_output=True, text=True, timeout=int((seconds + 11) * 2 + 180))
    if r.returncode != 0:
        ledger_add(ledger, "generate", MODEL_RT, 1, 0.0, None, "failed", id=tid)
        die("Lyria RealTime failed: %s" % scrub((r.stderr or r.stdout).strip()[-600:]))
    try:
        res = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        die("the RealTime recorder gave no result: %s" % scrub(r.stdout[-300:]))
    os.chmod(orig, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    pr = probe(orig)
    sidecar = {
        "schema": "nexa-sound/track-1", "id": tid, "created_at": now_iso(),
        "tool": {"skill": "nexa-sound", "version": SKILL_VERSION},
        "provider": {"api": "gemini-api", "endpoint": "WebSocket BidiGenerateMusic", "model": MODEL_RT,
                     "stage": "experimental", "interaction_id": None, "store": None,
                     "key_var_used": res.get("key_source")},
        "request": {"prompt": None, "lyrics": None, "images": [], "response_format": None,
                    "realtime": {"weighted_prompts": prompts, "config": config,
                                 "automation": rt.get("automation") or [], "preroll_s": res.get("preroll_s"),
                                 "recorded_s": res.get("recorded_s"), "session_count": 1,
                                 "api_version": res.get("api_version")},
                    "seed": config.get("seed"), "requested_duration_s": seconds, "brief": brief_summary(brief)},
        "response": {"text_parts": [], "timed_lines": [], "filtered_prompts": res.get("filtered_prompts") or [],
                     "filtered": bool(res.get("filtered_prompts")), "latency_s": round(time.time() - t0, 1),
                     "cost_usd_est": 0.0, "chunks": res.get("chunks")},
        "original": {"file": os.path.abspath(orig), "sha256": sha256(orig), "format": "wav",
                     "bytes": os.path.getsize(orig), "sample_rate": pr["sample_rate"], "channels": pr["channels"],
                     "duration_s": pr["duration_s"], "c2pa_manifest_present": False, "read_only": True,
                     "synthid": LICENCE_LYRIA["synthid"]},
        "analysis": analyse_track(orig, brief.get("bpm"), os.path.join(args.out, tid + ".beats.json")),
        "fit": None, "qc": None,
        "licence": dict(LICENCE_LYRIA, source="Google Lyria RealTime (experimental) via the Gemini API",
                        note="experimental and free for now; on an unpaid key Google's unpaid-service terms apply "
                             "(what you send may be used to improve its products)"),
        "usage": {"project": os.path.abspath(args.project) if args.project else None,
                  "video_edl": brief.get("cuts_file"), "approved_by": None},
    }
    qc = measured_checks(orig, "music", brief_summary(brief), sidecar)
    sidecar["qc"] = qc_summary(qc, None, brief_summary(brief), "music")
    side_path = os.path.join(args.out, tid + ".json")
    write_json(side_path, sidecar)
    ledger_add(ledger, "generate", MODEL_RT, 1, 0.0, res.get("key_source"), "ok", id=tid,
               seconds=res.get("recorded_s"))
    library_add({"id": tid, "mood": brief.get("mood"), "bpm": sidecar["analysis"].get("bpm") or brief.get("bpm"),
                 "bpm_requested": brief.get("bpm"), "key": brief.get("key"), "duration_s": pr["duration_s"],
                 "file": os.path.abspath(orig), "sidecar": os.path.abspath(side_path), "model": MODEL_RT,
                 "vocals": False, "qc_passed": sidecar["qc"]["passed"], "created": now_iso()})
    result = {"ok": True, "model": MODEL_RT, "takes": [{"id": tid, "ok": True, "file": os.path.abspath(orig),
                                                         "sidecar": os.path.abspath(side_path), "format": "wav",
                                                         "duration_s": pr["duration_s"],
                                                         "bpm": sidecar["analysis"].get("bpm"),
                                                         "qc_passed": sidecar["qc"]["passed"],
                                                         "qc_failed": sidecar["qc"]["failed"]}],
              "filtered_prompts": res.get("filtered_prompts") or [], "est_usd": 0.0, "ledger": ledger}
    lines = ["%s: RealTime bed, %.1f s, %s BPM, QC %s" % (
        tid, pr["duration_s"], sidecar["analysis"].get("bpm"), "passed" if sidecar["qc"]["passed"] else
        "failed (%s)" % ", ".join(sidecar["qc"]["failed"])),
             "a RealTime bed is cut from a live stream, so its end is abrupt until fit ends it on a downbeat"
             if "ending" in sidecar["qc"]["failed"] else None,
             "filtered prompts: %s" % (", ".join(res.get("filtered_prompts")) if res.get("filtered_prompts")
                                       else "none"),
             "cost: $0.00 (experimental model, free for now)"]
    emit(args, result, lines)


# ================================================================ ElevenLabs music

ENDING_WORDS = {"ring_out": "end on a clean final chord that rings out naturally to silence",
                "final_hit": "one final hit, then a short tail ringing out to silence",
                "fade": "fade out gently to silence at the very end",
                "cut": "end with a clean, tight stop", "cut_to_silence": "end with a clean, tight stop"}
NO_VOICE = ["vocals", "singing", "choir", "spoken words", "lyrics", "vocal chops"]
ENDING_MS = {"ring_out": 4000, "final_hit": 3000, "fade": 4000, "cut": 3000, "cut_to_silence": 3000}


def composition_plan(brief, model=None):
    """The brief as an ElevenLabs composition plan: the mood's styles for the whole track, one section per brief
    section at its exact length (split at 120 s, the longest section ElevenLabs takes), sparse where the voice-over
    talks, the mood's ending in the last section, and no voices unless the brief asks for them. music_v2 and
    music_v2_5 take {"chunks": [{"text": "[Section]", "duration_ms", "positive_styles", "negative_styles",
    "context_adherence"}]} (the first chunk's styles set the tone); music_v1 took global styles and sections."""
    model = model or EL.MUSIC_MODELS[0]
    mood = load_moods().get(brief.get("mood")) or {}
    weighted = sorted(((w, p) for p, w in ((mood.get("realtime") or {}).get("prompts") or [])), reverse=True)
    pos = [p for _, p in weighted][:5]
    if brief.get("bpm"):
        pos.append("%g BPM" % float(brief["bpm"]))
    if brief.get("key"):
        pos.append(str(brief["key"]))
    narrated = any(sec.get("narrated") for sec in brief.get("sections") or [])
    if narrated:
        pos.append("background music under a voice-over")
    neg = [] if brief.get("vocals") else list(NO_VOICE)
    sections = []
    for sec in brief.get("sections") or []:
        total = int(round((float(sec["end"]) - float(sec["start"])) * 1000))
        parts = max(1, int(math.ceil(total / float(EL.MUSIC_SECTION_MAX_MS))))
        for k in range(parts):
            dur = total // parts + (1 if k < total % parts else 0)
            local = [str(sec.get("change") or sec.get("label") or "").strip(), "intensity %d of 10" % int(
                sec.get("intensity") or 5)]
            local_neg = []
            if sec.get("narrated"):
                local += ["sparse arrangement that leaves room for the voice"]
                local_neg += ["busy lead melody", "loud drum fills"]
            sections.append({"section_name": (sec.get("label") or "Section") + ("" if parts == 1 else " %d" % (k + 1)),
                             "positive_local_styles": [x for x in local if x], "negative_local_styles": local_neg,
                             "duration_ms": dur, "lines": []})
    if not sections:
        total = int(round(float(brief.get("duration_s") or 30) * 1000))
        sections = [{"section_name": "Track", "positive_local_styles": [], "negative_local_styles": [],
                     "duration_ms": total, "lines": []}]
    short = [x for x in sections if x["duration_ms"] < EL.MUSIC_SECTION_MIN_MS]
    for x in short:                           # a section under 3 s joins its neighbour
        i = sections.index(x)
        j = i - 1 if i > 0 else i + 1
        if 0 <= j < len(sections) and x in sections:
            sections[j]["duration_ms"] += x["duration_ms"]
            sections.remove(x)
    ending = ENDING_WORDS.get(brief.get("ending") or mood.get("ending") or "")
    if ending:
        sections[-1]["positive_local_styles"].append(ending)
    if model == "music_v1":
        return {"positive_global_styles": pos, "negative_global_styles": neg, "sections": sections}
    # the ending gets its own chunk: styled only at the end of a chunk, music_v2_5 cut off at the length
    # (judged "abrupt_cut" on the live test, 2026-09-25); a chunk of its own lets it land
    last = sections[-1]
    tail_ms = ENDING_MS.get(brief.get("ending") or mood.get("ending") or "", 0)
    if ending and tail_ms and last["duration_ms"] >= tail_ms + EL.MUSIC_SECTION_MIN_MS:
        last["duration_ms"] -= tail_ms
        last["positive_local_styles"] = [x for x in last["positive_local_styles"] if x != ending]
        sections.append({"section_name": "Ending", "positive_local_styles": [ending, "clear resolution"],
                         "negative_local_styles": ["fade in", "new melody", "abrupt cut"],
                         "duration_ms": tail_ms, "lines": []})
    chunks = []
    for i, sec in enumerate(sections):
        styles = (pos if i == 0 else pos[:2]) + sec["positive_local_styles"]
        text = "[%s]%s" % (sec["section_name"], "" if brief.get("vocals") else " {instrumental}")
        chunks.append({"text": text, "duration_ms": sec["duration_ms"], "positive_styles": styles[:50],
                       "negative_styles": (neg + sec["negative_local_styles"])[:50], "context_adherence": "high"})
    return {"chunks": chunks[:30]}


def plan_parts(plan):
    return plan.get("chunks") or plan.get("sections") or []


def plan_length_s(plan):
    return sum(x["duration_ms"] for x in plan_parts(plan)) / 1000.0


def generate_eleven(args, brief, ledger):
    if not EL.keys():
        die(EL.MISSING_KEY_HELP)
    takes = int(args.takes or 1)
    if not 1 <= takes <= 3:
        die("--takes is 1 to 3 on ElevenLabs")
    model = args.model or EL.MUSIC_MODELS[0]
    plan = composition_plan(brief, model)
    length = plan_length_s(plan)
    est = PRICES["elevenlabs-music-min"] * length / 60.0 * takes
    guard(est, args.budget, "%d ElevenLabs music take%s of %.0f s" % (takes, "s" if takes > 1 else "", length))
    acct = eleven_plan()
    lic = eleven_licence(acct)
    if lic["commercial"] is not True:
        log("ElevenLabs plan: %s. %s" % (acct.get("tier") or "unknown", lic["note"]))
    ids = next_ids(args.out, brief.get("mood") or "track", takes)
    log("%d ElevenLabs music take%s (%s, %.1f s, %d section%s)" % (
        takes, "s" if takes > 1 else "", model, length, len(plan_parts(plan)),
        "s" if len(plan_parts(plan)) > 1 else ""))

    def one(tid):
        try:
            return _eleven_take(args, brief, plan, length, model, tid, ledger, lic, acct)
        finally:
            release_id(args.out, tid)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, takes)) as pool:
        results = list(pool.map(one, ids))
    ok = [r for r in results if r["ok"]]
    lines = []
    for r in results:
        if r["ok"]:
            lines.append("%s: %s, %.1f s (asked %.1f s), %s BPM, QC %s%s" % (
                r["id"], r["format"], r["duration_s"], length, r.get("bpm"),
                "passed" if r["qc_passed"] else "failed (%s)" % ", ".join(r["qc_failed"]),
                "" if lic["commercial"] else "; NOT for client work (%s)" % lic["source"]))
        else:
            lines.append("%s: failed: %s" % (r["id"], r["error"]))
    lines.append("ledger %s" % ledger)
    emit(args, {"ok": bool(ok), "engine": "elevenlabs", "model": model, "takes": results, "plan": plan,
                "licence": lic, "ledger": ledger}, lines)
    if not ok:
        sys.exit(1)


def _eleven_take(args, brief, plan, length, model, tid, ledger, lic, acct):
    t0 = time.time()
    try:
        data, info, fmt = eleven_call(EL.music, "pcm_48000", steps=("mp3_48000_320", "mp3_44100_192",
                                                                 "mp3_44100_128"),
                                      composition_plan=plan, model_id=model, respect_durations=True, c2pa=True,
                                      seed=getattr(args, "seed", None))
    except EL.ElevenError as err:
        ledger_add(ledger, "generate", "elevenlabs-" + model, 1, 0.0, None, "failed", id=tid, error_kind=err.kind)
        return {"id": tid, "ok": False, "error_kind": err.kind, "error": scrub(str(err))}
    latency = round(time.time() - t0, 1)
    ledger_add(ledger, "generate", "elevenlabs-" + model, 1, PRICES["elevenlabs-music-min"] * length / 60.0,
               info.get("key"), "ok", id=tid, seconds=round(length, 2), response=EL.cost_headers(info) or None,
               commercial=lic["commercial"])
    try:
        path, meta = EL.save_audio(data, os.path.join(args.out, tid + "_orig"), fmt, expect_s=length, info=info)
    except EL.ElevenError as err:
        rescue = os.path.join(args.out, tid + "_orig.pcm")
        with open(rescue, "wb") as fh:
            fh.write(data)
        return {"id": tid, "ok": False, "error_kind": "format", "error": "%s; the raw answer is kept in %s" % (
            scrub(str(err)), rescue)}
    os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    with open(path, "rb") as fh:
        raw = fh.read()
    side_path = os.path.join(args.out, tid + ".json")
    sidecar = {
        "schema": "nexa-sound/track-1", "id": tid, "created_at": now_iso(),
        "tool": {"skill": "nexa-sound", "version": SKILL_VERSION},
        "provider": {"api": "elevenlabs", "endpoint": "POST /v1/music", "model": model, "stage": None,
                     "key_var_used": info.get("key"), "plan": acct.get("tier"), "response": EL.cost_headers(info)},
        "request": {"prompt": None, "composition_plan": plan, "respect_sections_durations": True,
                    "c2pa": fmt.startswith("mp3"),
                    "output_format": fmt, "seed": getattr(args, "seed", None), "requested_duration_s": length,
                    "brief": brief_summary(brief)},
        "response": {"text_parts": [], "timed_lines": [], "vocals_suspected": False, "latency_s": latency},
        "original": {"file": os.path.abspath(path), "sha256": hashlib.sha256(raw).hexdigest(),
                     "format": meta.get("format"), "bytes": len(raw), "c2pa_manifest_present": has_c2pa(raw),
                     "read_only": True, "sample_rate": meta.get("sample_rate"), "channels": meta.get("channels")},
        "analysis": {}, "fit": None, "qc": None, "licence": lic,
        "usage": {"project": os.path.abspath(args.project) if args.project else None,
                  "video_edl": brief.get("cuts_file"), "approved_by": None},
    }
    write_json(side_path, sidecar)
    try:
        pr = probe(path)
        sidecar["original"]["duration_s"] = pr["duration_s"]
        sidecar["analysis"] = analyse_track(path, brief.get("bpm"), os.path.join(args.out, tid + ".beats.json"))
        ana = sidecar["analysis"]
        qc = measured_checks(path, "music", brief_summary(brief), sidecar,
                             lo={"I": ana.get("lufs_i"), "TP": ana.get("true_peak_dbtp"), "LRA": ana.get("lra_lu")})
        sidecar["qc"] = qc_summary(qc, None, brief_summary(brief), "music")
    except (Exception, SystemExit) as err:
        sidecar["qc"] = {"passed": False, "failed": ["analysis"], "warnings": [], "error": scrub(str(err))}
        pr = {"duration_s": sidecar["original"].get("duration_s")}
    write_json(side_path, sidecar)
    library_add({"id": tid, "mood": brief.get("mood"), "bpm": sidecar["analysis"].get("bpm") or brief.get("bpm"),
                 "bpm_requested": brief.get("bpm"), "key": brief.get("key"), "duration_s": pr["duration_s"],
                 "file": os.path.abspath(path), "sidecar": os.path.abspath(side_path), "model": "elevenlabs-" + model,
                 "vocals": brief.get("vocals"), "qc_passed": sidecar["qc"]["passed"],
                 "qc_failed": sidecar["qc"]["failed"], "commercial": lic["commercial"], "created": now_iso()})
    return {"id": tid, "ok": True, "file": os.path.abspath(path), "sidecar": os.path.abspath(side_path),
            "format": sidecar["original"]["format"], "duration_s": pr["duration_s"],
            "bpm": sidecar["analysis"].get("bpm"), "qc_passed": sidecar["qc"]["passed"],
            "qc_failed": sidecar["qc"]["failed"], "latency_s": latency, "commercial": lic["commercial"]}


# ================================================================ ambience beds

def seam_report(path, piece_s, n_loops, rate=16000):
    """How audible the loop's joins are: at each join, the level change between the 20 ms windows either side
    against the 95th percentile of such changes elsewhere, and the sample jump against the median sample step."""
    x = decode_f32(path, rate=rate, channels=1)
    n = len(x)
    win = int(0.02 * rate)
    if n < 4 * win:
        return {"joins": 0}

    def level(a, b):
        seg = x[max(0, a):min(n, b)]
        return 10 * math.log10(sum(v * v for v in seg) / max(1, len(seg)) + 1e-12)
    jumps = []
    for i in range(win, n - win, win):
        jumps.append(abs(level(i, i + win) - level(i - win, i)))
    jumps.sort()
    p95 = jumps[int(0.95 * (len(jumps) - 1))] if jumps else 0.0
    steps = sorted(abs(x[i] - x[i - 1]) for i in range(1, n, max(1, n // 20000)))
    med = steps[len(steps) // 2] if steps else 0.0
    joins = []
    for k in range(1, n_loops):
        i = int(round(k * piece_s * rate))
        if win <= i < n - win:
            joins.append({"at_s": round(i / float(rate), 3), "level_jump_db": round(abs(level(i, i + win) -
                                                                                        level(i - win, i)), 2),
                          "sample_jump_x_median": round(abs(x[i] - x[i - 1]) / max(med, 1e-9), 1)})
    worst = max((j["level_jump_db"] for j in joins), default=0.0)
    return {"joins": len(joins), "worst_level_jump_db": round(worst, 2), "p95_level_jump_db": round(p95, 2),
            "audible": bool(joins) and worst > max(3.0, 1.5 * p95), "detail": joins[:12]}


def cmd_ambience(args):
    """An ambience or room-tone bed of exact length from one ElevenLabs loop: made once as a seamless loop (up to 30
    s), then repeated sample-exactly to the length, with a fade at each end."""
    out = os.path.abspath(args.out)
    folder = os.path.dirname(out) or "."
    os.makedirs(folder, exist_ok=True)
    check_out(out, [])
    ledger = ledger_file(folder, args.project)
    if not EL.keys():
        die(EL.MISSING_KEY_HELP)
    piece = max(4.0, min(EL.SFX_MAX_S, float(args.piece or min(EL.SFX_MAX_S, args.duration))))
    guard(PRICES["elevenlabs-sfx"], args.budget, "one ElevenLabs loop")
    try:
        r = elevenlabs_fetch(args.text, os.path.join(folder, "ambience_parts"), piece, loop=True,
                             influence=args.influence, model=args.model)
    except ServiceError as err:
        ledger_service_error(ledger, "ambience", "elevenlabs-sfx", PRICES["elevenlabs-sfx"], err)
        die("ElevenLabs: %s" % err)
    ledger_add(ledger, "ambience", "elevenlabs-sfx", 1, PRICES["elevenlabs-sfx"], r.get("key_source"), "ok",
               detail=args.text[:80], commercial=r.get("commercial"), response=r.get("response") or None)
    with Work() as work:
        loop_wav = work.path("loop.wav")
        to_wav(r["file"], loop_wav, channels=2, codec="pcm_f32le")
        got = probe(loop_wav)["duration_s"]
        loops = int(math.ceil(args.duration / max(0.5, got)))
        N = int(round(args.duration * SR))
        fade_in, fade_out = min(args.fade_in, args.duration / 4), min(args.fade_out, args.duration / 4)
        af = "atrim=end_sample=%d,asetpts=PTS-STARTPTS" % N
        if fade_in > 0:
            af += ",afade=t=in:st=0:d=%.3f:curve=hsin" % fade_in
        if fade_out > 0:
            af += ",afade=t=out:st=%.3f:d=%.3f:curve=hsin" % (args.duration - fade_out, fade_out)
        run_ff(["-y", "-v", "error", "-stream_loop", str(max(0, loops - 1)), "-i", loop_wav, "-af", af,
                "-ar", SR, "-c:a", "pcm_s24le", out], what="tiling the loop")
    seams = seam_report(out, got, loops)
    lo = loudness(out)
    side = {"schema": "nexa-sound/ambience-1", "skill_version": SKILL_VERSION, "created": now_iso(),
            "file": out, "text": args.text, "duration_s": probe(out)["duration_s"], "loop_s": got, "loops": loops,
            "fade_in_s": fade_in, "fade_out_s": fade_out, "seams": seams,
            "loudness": {"I": lo["I"], "TP": lo["TP"], "LRA": lo["LRA"]}, "source": r,
            "licence": r.get("licence"), "commercial": r.get("commercial"), "sha256": sha256(out)}
    write_json(stem_of(out) + ".json", side)
    lines = ["ambience: %s (%.2f s from a %.2f s loop x %d, %s LUFS)" % (out, side["duration_s"], got, loops,
                                                                           lo["I"]),
             "joins: %d, worst level jump %.1f dB (elsewhere 95%% under %.1f dB)%s" % (
                 seams.get("joins", 0), seams.get("worst_level_jump_db", 0.0), seams.get("p95_level_jump_db", 0.0),
                 ": AUDIBLE, make it again or use a longer --piece" if seams.get("audible") else ""),
             "licence: %s%s" % (r.get("licence"), "" if r.get("commercial") else " (NOT for client work)")]
    emit(args, dict(side, ok=True), lines)


# ================================================================ track metadata

def track_meta(path):
    """(sidecar, sidecar path, fit or loop report) for an original or a fitted file, when nexa-sound made it."""
    s = stem_of(path)
    side = side_path = rep = None
    cands = ([s[:-5] + ".json"] if s.endswith("_orig") else []) + [s + ".json", s + ".fit.json", s + ".loop.json"]
    for p in cands:
        j = try_json(p) if os.path.exists(p) else None
        if not isinstance(j, dict):
            continue
        if j.get("schema") == "nexa-sound/track-1" and side is None:
            side, side_path = j, p
        elif j.get("schema") in ("nexa-sound/fit-1", "nexa-sound/loop-1") and rep is None:
            rep = j
    if rep is not None and side is None and rep.get("source_sidecar") and os.path.exists(rep["source_sidecar"]):
        j = try_json(rep["source_sidecar"])
        if isinstance(j, dict) and j.get("schema") == "nexa-sound/track-1":
            side, side_path = j, rep["source_sidecar"]
    return side, side_path, rep


# ================================================================ bar features, fitting and loops

def band_features(path, beat_times, end_s):
    """Per beat: log energy (dB) in three bands (under 250 Hz, 250 Hz to 2 kHz, over 2 kHz), from ffmpeg-filtered
    decodes. A bar is four of these, so bars can be compared for a seamless edit."""
    bands = [("low", "lowpass=f=250,lowpass=f=250", 8000),
             ("mid", "highpass=f=250,highpass=f=250,lowpass=f=2000,lowpass=f=2000", 8000),
             ("high", "highpass=f=2000,highpass=f=2000", 16000)]
    edges = list(beat_times) + [end_s]
    mul = operator.mul
    feats = [[0.0, 0.0, 0.0] for _ in beat_times]
    for bi, (_, af, rate) in enumerate(bands):
        x = decode_f32(path, rate=rate, channels=1, af=af)
        for k in range(len(beat_times)):
            a, b = int(edges[k] * rate), int(edges[k + 1] * rate)
            seg = x[max(0, a):max(a + 1, min(len(x), b))]
            ms = sum(map(mul, seg, seg)) / max(1, len(seg))
            feats[k][bi] = max(-90.0, 10.0 * math.log10(ms + 1e-12))
    return feats


def bar_vectors(grid, feats):
    """One 12-number vector per bar (4 beats x 3 bands), keyed by the bar's index among the downbeats."""
    beats = grid["beats"]
    first = beats.index(grid["downbeats"][0]) if grid["downbeats"] else 0
    per = grid.get("beats_per_bar", 4)
    bars = []
    for i in range(len(grid["downbeats"])):
        k = first + i * per
        if k + per <= len(feats):
            bars.append([v for b in feats[k:k + per] for v in b])
    return bars


def bar_dist(bars, i, j):
    if i < 0 or j < 0 or i >= len(bars) or j >= len(bars):
        return 99.0
    a, b = bars[i], bars[j]
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / len(a))


def find_cut(bars, m, n_keep_end=2):
    """Best a for removing bars a .. a+m-1: bar a+m must sound like bar a (what would have followed bar a-1)."""
    best = None
    for a in range(1, len(bars) - m - n_keep_end + 1):
        d = bar_dist(bars, a, a + m) + 0.5 * bar_dist(bars, a - 1, a + m - 1)
        if best is None or d < best[1]:
            best = (a, d)
    return best


def steadiness(bars, a, k):
    levels = [sum(bars[i]) / len(bars[i]) for i in range(a, min(len(bars), a + k))]
    if len(levels) < 2:
        return 0.0
    mean = sum(levels) / len(levels)
    return math.sqrt(sum((v - mean) ** 2 for v in levels) / len(levels))


def find_loop(bars, k, rem=0, n_keep_end=2):
    """Best start bar L0 for a k-bar loop (and a rem-bar extra loop from the same start): steady inside, and the bars
    it jumps back from sound like bar L0."""
    best = None
    for L0 in range(1, len(bars) - k - n_keep_end + 1):
        d = bar_dist(bars, L0, L0 + k) + 0.5 * bar_dist(bars, L0 - 1, L0 + k - 1) + 0.3 * steadiness(bars, L0, k)
        if rem:
            d += bar_dist(bars, L0, L0 + rem)
        if best is None or d < best[1]:
            best = (L0, d)
    return best


def cut_score(cuts, grid_first, bar, length, offset, tempo=1.0):
    """Weighted cuts within 80 ms of a downbeat once the music start moves by `offset` s (positive: the head is
    skipped; negative: the music starts later)."""
    period = bar / tempo
    first = (grid_first - offset) / tempo if offset >= 0 else grid_first / tempo - offset
    hits, soft, detail = 0.0, 0.0, []
    for c in cuts:
        if c["t"] < 0 or c["t"] > length:
            continue
        k = round((c["t"] - first) / period)
        dist = abs(c["t"] - (first + k * period))
        hits += c["weight"] if dist <= 0.08 else 0.0
        soft += c["weight"] * math.exp(-(dist / 0.04) ** 2)
        detail.append({"t": c["t"], "weight": c["weight"], "error_ms": round(1000 * (c["t"] - first - k * period), 1),
                       "on_downbeat": dist <= 0.08})
    return hits, soft, detail


def offset_search(cuts, grid_first, bar, length, tempo=1.0):
    """The start offset (within 2 s either way) that puts the most weighted cuts on downbeats. The start stays put
    unless moving it lands more cuts, or brings them clearly closer (10 % of the total weight on the soft score)."""
    hits0, soft0, _ = cut_score(cuts, grid_first, bar, length, 0.0, tempo)
    total = sum(c["weight"] for c in cuts) or 1.0
    best = None
    for i in range(-200, 201):
        o = i / 100.0
        hits, soft, _ = cut_score(cuts, grid_first, bar, length, o, tempo)
        key = (round(hits, 6), soft - (0.15 if o < 0 else 0.0) - 0.02 * abs(o))
        if best is None or key > best[0]:
            best = (key, o)
    (hits, soft), o = best
    if hits <= hits0 + 1e-9 and soft < soft0 + 0.1 * total:
        return 0.0
    return o


def tail_info(path, grid, dur):
    """How the source ends: the last real hit (a beat whose onset is at least half the typical beat onset), how much
    ring-out follows it, whether the very end is quiet, and whether it stops abruptly."""
    x = BT.decode(path)
    onset = BT.onset_strength(BT.frame_log_energy(x))
    strength = []
    for t in grid["beats"]:
        i = int(t * BT.FPS)
        strength.append(max(onset[max(0, i - 3):i + 4] or [0.0]))
    ranked = sorted(strength)
    med = ranked[len(ranked) // 2] if ranked else 0.0
    hits = [t for t, v in zip(grid["beats"], strength) if v >= 0.5 * med and t <= dur - 0.25]
    last_hit = max(hits) if hits else 0.0
    y = decode_f32(path, rate=16000, channels=1, start=max(0.0, dur - 2.5))
    n = len(y)

    def rms_db(seg):
        if not seg:
            return -120.0
        return 10 * math.log10(sum(v * v for v in seg) / len(seg) + 1e-12)
    last50 = rms_db(y[max(0, n - 800):])
    before = rms_db(y[max(0, n - 32800):max(0, n - 800)])
    abrupt = last50 > -35.0 and last50 > before - 6.0
    return {"last_hit_s": round(last_hit, 3), "ring_room_s": round(dur - (last_hit + 0.5), 3),
            "last50_dbfs": round(last50, 1), "before_dbfs": round(before, 1), "abrupt": abrupt,
            "ends_quiet": last50 <= -45.0}


def lead_in(path):
    for s, e in silences(path, -50.0, 0.05)[:1]:
        if s <= 0.01:
            return e
    return 0.0


def plan_fit(L, T, grid, bars, cuts, tail, lead, ending=None):
    """The edit plan: segments of the source (joined by one-beat equal-power crossfades at bar lines), plus how the
    last fraction of a bar is absorbed. Everything it decides is written to fit.json."""
    bar, beat = grid["bar_s"], grid["period_s"]
    downs = grid["downbeats"]
    notes = []
    o = offset_search(cuts, grid["first_downbeat_s"], bar, T) if cuts else 0.0
    skip = max(o, 0.0)
    delay = max(-o, 0.0)
    base = L - skip + delay

    def residual_options(pre_len, ends_quiet, ring_room, can_skip):
        """Ways to absorb what whole bars cannot (under one bar), cheapest first. Costs are editing judgement:
        trimming a ring-out or skipping silence is nearly free; padding after a quiet ending, a small tempo change
        and skipping into the intro cost more; a plain fade-out is the last resort."""
        r = pre_len - T
        opts = []
        if abs(r) <= 0.02:
            return [(0.0, {"kind": "exact"})]
        if r > 0:
            if can_skip and lead - skip > 0.02:
                s_ = min(r, lead - skip)
                if abs(r - s_) <= 0.02:
                    opts.append((0.0, {"kind": "skip_lead_in", "s": round(s_, 4)}))
            if ring_room >= r + 1.0 and not tail["abrupt"]:
                opts.append((1.0 + 0.5 * r, {"kind": "trim_tail", "s": round(r, 4),
                                             "fade_s": round(min(1.5, ring_room - r), 3)}))
            if r / T <= 0.03:
                # a tempo change slides every downbeat away from the cuts it was lined up with
                opts.append((2.0 + 60.0 * r / T + (4.0 if cuts else 0.0),
                             {"kind": "atempo", "factor": round(pre_len / T, 6)}))
            if can_skip:
                opts.append((2.5 + r, {"kind": "head_skip", "s": round(r, 4), "fade_in_s": round(min(0.25, r), 3)}))
            opts.append((6.0, {"kind": "fade_end"}))
        else:
            s_ = -r
            if ends_quiet and s_ <= 1.5:
                opts.append((1.0 + 1.5 * s_, {"kind": "pad_tail", "s": round(s_, 4)}))
            if s_ / T <= 0.03:
                opts.append((2.0 + 60.0 * s_ / T + (4.0 if cuts else 0.0),
                             {"kind": "atempo", "factor": round(pre_len / T, 6)}))
            if s_ <= 3.0:
                opts.append((4.0 + s_, {"kind": "pad_tail", "s": round(s_, 4),
                                        "note": "the music ends %.1f s before the video" % s_}))
        return sorted(opts, key=lambda x: x[0])

    def phrase_penalty(bars_changed):
        """Removing or adding a number of bars that is not a multiple of 4 (or 2) can break the chord cycle, which
        the energy features cannot hear; prefer phrase-sized edits."""
        return (0.0 if bars_changed % 4 == 0 else 1.5) + (0.0 if bars_changed % 2 == 0 else 0.75)

    candidates = []
    E = base - T
    ring_room = tail["ring_room_s"]
    can_skip = not cuts
    if tail["abrupt"] and E > 0.02:
        candidates.append((6.0, {"segments": [[skip, L]], "edits": [], "residual": {"kind": "fade_end"}}))
        notes.append("the source ends abruptly, so the fit ends on a downbeat with a fade instead of keeping it")
    elif E > 0.02:
        mid = E / bar
        for m in range(max(0, int(mid) - 1), int(math.ceil(mid)) + 2):
            if m == 0:
                for cost, res in residual_options(base, tail["ends_quiet"], ring_room, can_skip)[:1]:
                    candidates.append((cost, {"segments": [[skip, L]], "edits": [], "residual": res}))
                continue
            found = find_cut(bars, m)
            if found is None:
                continue
            a, d = found
            if d > 3.0:
                notes.append("no pair of bars %d apart sounds alike (best %.1f dB apart)" % (m, d))
                continue
            cut_from, cut_to = downs[a], downs[a + m]
            if cut_from < skip + beat:
                continue
            pre = base - (cut_to - cut_from)
            for cost, res in residual_options(pre, tail["ends_quiet"], ring_room, can_skip)[:1]:
                candidates.append((cost + 0.2 * d + phrase_penalty(m), {
                    "segments": [[skip, cut_from], [cut_to, L]], "residual": res,
                    "edits": [{"op": "cut_middle", "from_s": round(cut_from, 4), "to_s": round(cut_to, 4),
                               "bars": m, "similarity_db": round(d, 2), "xfade_s": round(beat, 4)}]}))
        if not candidates:
            candidates.append((6.0, {"segments": [[skip, L]], "edits": [], "residual": {"kind": "fade_end"}}))
    elif E < -0.02:
        X = -E
        mid = X / bar
        n_bars_ok = len(bars) - 3
        if tail["abrupt"]:
            # keep nothing of an abrupt ending: loop past the target and end on a downbeat with a fade
            mid = (X + 1.0) / bar
            notes.append("the source ends abruptly, so the fit loops past the target and fades out on a downbeat")
        for N in range(max(1, int(mid) - 1), int(math.ceil(mid)) + 2):
            if n_bars_ok < 1:
                break
            if N % 4 == 0:
                k = 16 if N % 16 == 0 else (8 if N % 8 == 0 else 4)
            else:
                k = N if N <= 16 else 16
            k = min(k, n_bars_ok)
            reps, rem = N // k, N % k
            found = find_loop(bars, k, rem)
            if found is None:
                continue
            L0, d = found
            A, B1 = downs[L0], downs[L0 + k]
            segs = [[skip, B1]] + [[A, B1] for _ in range(reps - 1)]
            if rem:
                segs.append([A, downs[L0 + rem]])
            segs.append([A, L])
            pre = base + (downs[L0 + k] - downs[L0]) * reps + ((downs[L0 + rem] - downs[L0]) if rem else 0.0)
            joins = reps + (1 if rem else 0)
            options = residual_options(pre, tail["ends_quiet"], ring_room, can_skip)[:1]
            if tail["abrupt"]:
                options = [(6.0, {"kind": "fade_end"})] if pre >= T + 1.0 else []
            for cost, res in options:
                candidates.append((cost + 0.2 * d + 0.2 * (joins - 1) + phrase_penalty(N), {
                    "segments": segs, "residual": res,
                    "edits": [{"op": "loop", "from_s": round(A, 4), "to_s": round(B1, 4), "bars": k,
                               "repeats": reps, "extra_bars": rem, "similarity_db": round(d, 2),
                               "xfade_s": round(beat, 4)}]}))
        if not candidates:
            candidates.append((9.0, {"segments": [[skip, L]], "edits": [],
                                     "residual": {"kind": "pad_tail", "s": round(X, 4),
                                                  "note": "too few bars to loop; the music ends early"}}))
    else:
        candidates.append((0.0, {"segments": [[skip, L]], "edits": [], "residual": {"kind": "exact"}}))
    candidates.sort(key=lambda c: c[0])
    cost, plan = candidates[0]
    considered = [{"cost": round(c, 2), "edits": [dict((k, v) for k, v in e.items() if k in ("op", "bars",
                                                                                              "repeats", "extra_bars"))
                                                  for e in p["edits"]], "residual": p["residual"]["kind"]}
                  for c, p in candidates[:4]]
    xfade = beat
    if grid.get("confidence", 1.0) < 0.5:
        # a weak grid (little percussion) may put bar lines off the music's own: smear each join over a bar
        xfade = min(bar, 2.0)
        notes.append("the beat grid is weak (confidence %.2f), so joins use %.2f s crossfades" % (
            grid.get("confidence", 0.0), xfade))
    plan.update({"skip_s": round(skip, 4), "delay_s": round(delay, 4), "offset_s": round(o, 3), "notes": notes,
                 "xfade_s": round(xfade, 4), "tempo": 1.0, "cost": round(cost, 3), "considered": considered})
    res = plan["residual"]
    if res["kind"] == "atempo":
        plan["tempo"] = res["factor"]
    if res["kind"] == "skip_lead_in" or res["kind"] == "head_skip":
        plan["segments"][0][0] = round(plan["segments"][0][0] + res["s"], 4)
    # starting inside the music (a head skip or a cut offset) gets a short fade-in, so the first sample cannot click
    plan["fade_in_s"] = res.get("fade_in_s") or (0.02 if skip > lead + 0.01 else 0.0)
    if res["kind"] == "fade_end":
        pre_len = sum(b - a for a, b in plan["segments"]) + delay
        out_downs = output_downbeats(plan, downs)
        hits = [d for d in out_downs if d <= T - 0.3]
        if ending == "final_hit" and hits and T - max(hits) <= bar + 0.01:
            # a track built to end on a hit: let the last downbeat hit sound, fade 0.3 s after it, then silence
            res.update({"fade_from_s": round(max(hits), 4), "fade_s": 0.3, "style": "0.3 s after the final hit"})
        else:
            # the last downbeat that leaves a 1 to 3 s fade ending on the target
            cands = [d for d in out_downs if T - 3.0 <= d <= T - 1.0]
            if cands:
                start = max(cands)
                res.update({"fade_from_s": round(start, 4), "fade_s": round(T - start, 4), "style": "fade out"})
            else:
                res.update({"fade_from_s": round(max(0.0, T - 2.0), 4), "fade_s": round(min(2.0, T), 4),
                            "style": "fade out"})
        res["pre_length_s"] = round(pre_len, 3)
    return plan


def output_downbeats(plan, downs):
    out, t = [], plan.get("delay_s", 0.0)
    tempo = plan.get("tempo", 1.0)
    for a, b in plan["segments"]:
        for d in downs:
            if a - 1e-6 <= d < b - 1e-6:
                out.append(round((t + d - a) / tempo if tempo != 1.0 else t + d - a, 4))
        t += b - a
    return out


def render_plan(master, plan, out, T):
    """One ffmpeg graph: sample-exact atrim segments, acrossfade (qsin, one beat) at every join, fades, atempo,
    head delay, then exactly round(T * 48000) samples."""
    segs = plan["segments"]
    x = int(round(plan["xfade_s"] * SR))
    n = len(segs)
    g = []
    if n > 1:
        g.append("[0:a]asplit=%d%s" % (n, "".join("[i%d]" % i for i in range(n))))
    else:
        g.append("[0:a]anull[i0]")
    for i, (a, b) in enumerate(segs):
        sa = int(round(a * SR))
        sb = int(round(b * SR)) + (x if i < n - 1 else 0)
        g.append("[i%d]atrim=start_sample=%d:end_sample=%d,asetpts=PTS-STARTPTS[t%d]" % (i, sa, sb, i))
    cur = "t0"
    for i in range(1, n):
        g.append("[%s][t%d]acrossfade=ns=%d:c1=qsin:c2=qsin[j%d]" % (cur, i, x, i))
        cur = "j%d" % i
    post = []
    res = plan["residual"]
    if plan.get("fade_in_s"):
        post.append("afade=t=in:st=0:d=%.4f:curve=hsin" % plan["fade_in_s"])
    if plan.get("tempo", 1.0) != 1.0:
        post.append("atempo=%.6f" % plan["tempo"])
    N = int(round(T * SR))
    if res["kind"] == "trim_tail":
        pre_len = sum(b - a for a, b in segs) + plan["delay_s"]
        end = pre_len - res["s"] - plan["delay_s"]
        post.append("atrim=end_sample=%d" % int(round(end * SR)))
        post.append("afade=t=out:st=%.4f:d=%.4f:curve=qua" % (end - res["fade_s"], res["fade_s"]))
    if res["kind"] == "fade_end":
        st = res["fade_from_s"] - plan["delay_s"]
        post.append("afade=t=out:st=%.4f:d=%.4f:curve=qua" % (max(0.0, st), res["fade_s"]))
    if plan["delay_s"] > 0:
        post.append("adelay=delays=%dS:all=1" % int(round(plan["delay_s"] * SR)))
    post.append("apad=whole_len=%d,atrim=end_sample=%d" % (N, N))
    g.append("[%s]%s[out]" % (cur, ",".join(post)))
    run_ff(["-y", "-v", "error", "-i", master, "-filter_complex", ";".join(g), "-map", "[out]", "-ar", SR,
            "-c:a", "pcm_s24le", out], what="rendering the fit")


def describe_op(op):
    """One fit operation in an editor's words, for the summary."""
    k = op.get("op")
    if k == "offset":
        return ("skip the first %.2f s" % op["skip_head_s"]) if op["skip_head_s"] else (
            "start the music %.2f s late" % op["delay_s"])
    if k == "cut_middle":
        return "cut %d bar%s (%.2f s to %.2f s), %.2f s crossfade" % (op["bars"], "" if op["bars"] == 1 else "s",
                                                                      op["from_s"], op["to_s"], op["xfade_s"])
    if k == "loop":
        extra = (" plus %d bar%s" % (op["extra_bars"], "" if op["extra_bars"] == 1 else "s")) if op.get(
            "extra_bars") else ""
        times = "" if op["repeats"] == 1 else "s"
        return "loop %d bars (%.2f s to %.2f s) %d time%s%s, %.2f s crossfades" % (
            op["bars"], op["from_s"], op["to_s"], op["repeats"], times, extra, op["xfade_s"])
    if k == "pad_tail":
        return "%.2f s of silence after the ending%s" % (op["s"], (" (" + op["note"] + ")") if op.get("note") else "")
    if k == "trim_tail":
        return "end %.2f s earlier inside the ring-out, %.2f s fade" % (op["s"], op["fade_s"])
    if k == "atempo":
        return "tempo %+.1f %%" % (100.0 * (op["factor"] - 1.0))
    if k in ("head_skip", "skip_lead_in"):
        return "skip %.2f s at the start%s" % (op["s"], " (silence)" if k == "skip_lead_in" else "")
    if k == "fade_end":
        return "end with a %.2f s fade from the downbeat at %.2f s" % (op["fade_s"], op["fade_from_s"])
    return k


def prepare_master(src, work):
    """The working copy that fit and loop cut: 48 kHz stereo in 32-bit float, through a 5 Hz high-pass, with a
    gain that leaves 1 dB of headroom when the peaks need it. Lyria MP3s decode with peaks up to +0.8 dBFS, which a
    24-bit copy would clip, and carry a 0.5 to 0.7 % DC offset, which clicks at every cut."""
    master = work.path("master48k.wav")
    info = to_wav(src, master, channels=2, codec="pcm_f32le", pre="highpass=f=5")
    peak = astats(master)["peak_db"]
    if peak is not None and peak > -1.0:
        quieter = work.path("master48k_headroom.wav")
        run_ff(["-y", "-v", "error", "-i", master, "-af", "volume=%.3fdB" % (-1.0 - peak), "-c:a", "pcm_f32le",
                quieter], what="making headroom")
        master = quieter
        info = dict(info, headroom_gain_db=round(-1.0 - peak, 2))
    return master, info


def cmd_fit(args):
    src = args.track
    check_out(args.out, [src])
    if args.target < 2.0:
        die("--target must be at least 2 s")
    side, side_path, _ = track_meta(src)
    brief = (side or {}).get("request", {}).get("brief") or {}
    if args.brief:
        brief = brief_summary(read_brief(args.brief))
    bpm = args.bpm or brief.get("bpm")
    cuts = read_cuts(args.cuts)[0] if args.cuts else []
    t0 = time.time()
    with Work() as work:
        master, info = prepare_master(src, work)
        L = probe(master)["duration_s"]
        try:
            grid = BT.analyze(master, bpm)
        except BT.BeatError as err:
            die("no beat grid for %s: %s" % (src, err))
        feats = band_features(master, grid["beats"], L)
        bars = bar_vectors(grid, feats)
        tail = tail_info(master, grid, L)
        lead = lead_in(master)
        plan = plan_fit(L, args.target, grid, bars, cuts, tail, lead, brief.get("ending"))
        trial = work.path("fit_out.wav")
        render_plan(master, plan, trial, args.target)
        got = probe(trial)["duration_s"]
        if abs(got - args.target) > 0.05:
            die("the fit came out %.3f s long for a %.3f s target (over 50 ms off); nothing was written; report "
                "this" % (got, args.target))
        shutil.move(trial, args.out)
    out_downs = [d for d in output_downbeats(plan, grid["downbeats"]) if d <= args.target]
    score = None
    if cuts:
        hb, sb, _ = cut_score(cuts, grid["first_downbeat_s"], grid["bar_s"], args.target, 0.0)
        ha, sa, detail = cut_score(cuts, grid["first_downbeat_s"], grid["bar_s"], args.target, plan["offset_s"],
                                   plan["tempo"])
        score = {"offset_s": plan["offset_s"], "weighted_hits_before": round(hb, 3),
                 "weighted_hits_after": round(ha, 3), "soft_before": round(sb, 3), "soft_after": round(sa, 3),
                 "cuts": detail}
    ops = [{"op": "resample", "to_hz": SR, "bits": 24, "from_hz": info["sample_rate"],
            "filter": HQ_RESAMPLE}, {"op": "dc_block", "filter": "highpass=f=5"}]
    if info.get("headroom_gain_db") is not None:
        ops.append({"op": "gain", "db": info["headroom_gain_db"], "reason": "1 dB of headroom (the source peaked "
                    "above -1 dBFS)"})
    if plan["skip_s"] > 0 or plan["delay_s"] > 0:
        ops.append({"op": "offset", "s": plan["offset_s"], "skip_head_s": plan["skip_s"],
                    "delay_s": plan["delay_s"], "reason": "hits on cuts" if cuts else "length"})
    ops += plan["edits"]
    res = plan["residual"]
    if res["kind"] != "exact":
        op = dict(res)
        op["op"] = op.pop("kind")
        ops.append(op)
    report = {
        "schema": "nexa-sound/fit-1", "skill_version": SKILL_VERSION, "created": now_iso(),
        "source": os.path.abspath(src), "source_sha256": sha256(src),
        "source_sidecar": side_path,
        "file": os.path.abspath(args.out), "target_s": args.target, "result_s": got, "source_s": L,
        "bpm": grid["bpm"], "bar_s": grid["bar_s"], "beat_confidence": grid["confidence"],
        "segments": plan["segments"], "crossfade": {"curve": "qsin (equal power)", "s": plan["xfade_s"]},
        "tempo_factor": plan["tempo"], "ops": ops, "notes": plan["notes"], "considered": plan["considered"],
        "hits_on_cuts": score,
        "downbeats_out": out_downs, "tail": tail, "seconds": round(time.time() - t0, 2),
    }
    rp = report_path(args.out, "fit")
    write_json(rp, report)
    if side_path and os.path.exists(side_path):
        sc = try_json(side_path) or {}
        old = sc.get("fit") if isinstance(sc.get("fit"), dict) else None
        earlier = list((old or {}).get("earlier") or [])
        if old and old.get("file"):
            earlier.append({k: v for k, v in old.items() if k != "earlier"})
        sc["fit"] = {"target_s": args.target, "ops": ops, "start_offset_s": plan["offset_s"],
                     "file": os.path.abspath(args.out), "report": rp, "earlier": earlier}
        write_json(side_path, sc)
    lines = ["fit: %s -> %s, %.3f s (target %.3f s), %.2f BPM" % (os.path.basename(src), args.out, got,
                                                                   args.target, grid["bpm"])]
    for op in ops[1:]:
        lines.append("  %s" % describe_op(op))
    if score:
        lines.append("hits on cuts: %.1f weighted before, %.1f after (offset %+.2f s)" % (
            score["weighted_hits_before"], score["weighted_hits_after"], plan["offset_s"]))
    lines.append("report: %s" % rp)
    emit(args, dict(report, ok=True, report=rp), lines)


def cmd_loop(args):
    src = args.track
    check_out(args.out, [src])
    side, side_path, _ = track_meta(src)
    bpm = args.bpm or ((side or {}).get("request", {}).get("brief") or {}).get("bpm")
    k = int(args.bars)
    if k < 1 or k > 64:
        die("--bars must be 1 to 64")
    with Work() as work:
        master, info = prepare_master(src, work)
        L = probe(master)["duration_s"]
        try:
            grid = BT.analyze(master, bpm)
        except BT.BeatError as err:
            die("no beat grid for %s: %s" % (src, err))
        feats = band_features(master, grid["beats"], L)
        bars = bar_vectors(grid, feats)
        downs = grid["downbeats"]
        if len(downs) < k + 2:
            die("the track has %d whole bars; a %d-bar loop needs at least %d" % (len(downs) - 1, k, k + 2))
        found = find_loop(bars, k, 0, n_keep_end=1) or (0, 0.0)
        L0, d = found
        A, B1 = downs[L0], downs[L0 + k]
        x = int(round(grid["period_s"] * SR))
        N = int(round((B1 - A) * SR))
        seg = decode_f32(master, start=A, dur=(N + x) / float(SR) + 0.01)
        if len(seg) < 2 * (N + x):
            die("the loop runs past the end of the track")
        loop = array("f", seg[:2 * N])
        sin, cos, half_pi = math.sin, math.cos, math.pi / 2
        for i in range(x):
            g = (i + 0.5) / x
            gi, go = sin(half_pi * g), cos(half_pi * g)
            for c in (0, 1):
                loop[2 * i + c] = seg[2 * i + c] * gi + seg[2 * (N + i) + c] * go
        write_f32(loop, args.out)
        preview = None
        if args.preview:
            preview = stem_of(args.out) + ".preview.wav"
            write_f32(loop * 3, preview)
    join = join_check(loop, N, seg)
    report = {"schema": "nexa-sound/loop-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "source": os.path.abspath(src), "source_sha256": sha256(src), "file": os.path.abspath(args.out),
              "bars": k, "bpm": grid["bpm"], "bar_s": grid["bar_s"], "from_s": A, "to_s": B1,
              "length_samples": N, "length_s": round(N / float(SR), 6),
              "crossfade": {"curve": "qsin (equal power)", "s": round(x / float(SR), 4),
                            "how": "the bar after the loop fades into its first beat, so the end runs straight "
                                   "into the start"},
              "similarity_db": round(d, 2), "join": join, "preview": preview,
              "source_sidecar": side_path}
    rp = report_path(args.out, "loop")
    write_json(rp, report)
    lines = ["loop: %d bars (%.3f s) from %.2f s to %.2f s of %s, %.2f BPM" % (k, N / float(SR), A, B1,
                                                                               os.path.basename(src), grid["bpm"]),
             "join: %+.2f dB against the source's own flow, sample step %.2f times the source's own" % (
                 join["continuation_db"], join["sample_step_vs_source"]),
             "written: %s%s" % (args.out, (" and %s (3 repeats)" % preview) if preview else ""),
             "report: %s" % rp]
    emit(args, dict(report, ok=True, report=rp), lines)


def join_check(loop, N, seg):
    """How the wrap sounds: the loop's first 50 ms against the source's own continuation after the loop's last bar
    (0 dB means the wrap flows like the original), and the sample step across the wrap against the same step in the
    source (1.0 means the wrap is exactly as smooth as the original; a click shows as a much larger step)."""
    w = int(0.05 * SR)

    def rms(s):
        return math.sqrt(sum(v * v for v in s) / max(1, len(s))) or 1e-9
    start = loop[:2 * w]
    cont = seg[2 * N:2 * (N + w)]
    step = max(abs(loop[2 * (N - 1) + c] - loop[c]) for c in (0, 1))
    own = max(abs(seg[2 * (N - 1) + c] - seg[2 * N + c]) for c in (0, 1)) + 1e-9
    return {"continuation_db": round(20 * math.log10(rms(start) / rms(cont)), 2),
            "sample_step_vs_source": round(step / own, 2)}


# ================================================================ sound effects

def fps_lead(fps):
    return round(1.5 / float(fps), 4)


def sfx_dirs():
    return [d for d in os.environ.get("NEXA_SFX_DIRS", "").split(os.pathsep) if d.strip()]


def media_use_dir():
    return os.path.expanduser(os.environ.get("NEXA_MEDIA_USE_SFX") or MEDIA_USE_SFX)


AUDIO_EXT = (".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aif", ".aiff", ".opus")


def library_index(folder):
    """{key: {file, description, licence, ...}} for a folder: its manifest.json (media-use format) and its files."""
    idx = {}
    man = try_json(os.path.join(folder, "manifest.json")) if os.path.isdir(folder) else None
    folder_licence = None
    if isinstance(man, dict):
        folder_licence = man.get("_licence") or man.get("licence")
        for key, v in man.items():
            if key.startswith("_") or not isinstance(v, dict) or not v.get("file"):
                continue
            idx[SX.slug(key)] = dict(v, file=os.path.join(folder, v["file"]), key=key)
    if os.path.isdir(folder):
        for f in sorted(os.listdir(folder)):
            if f.lower().endswith(AUDIO_EXT):
                k = SX.slug(os.path.splitext(f)[0])
                idx.setdefault(k, {"file": os.path.join(folder, f), "key": k})
    for v in idx.values():
        v.setdefault("licence", folder_licence)
    return idx


def match_key(idx, name, query):
    for cand in [name, query]:
        if cand:
            s = SX.slug(cand)
            if s in idx:
                return idx[s]
    words = [w for w in SX.slug(query or name or "").split("-") if len(w) > 2]
    if words:
        scored = []
        for k, v in idx.items():
            hay = (k + " " + str(v.get("description") or "")).lower()
            hit = sum(1 for w in words if w in hay)
            if hit == len(words):
                scored.append((len(k), k))
        if scored:
            return idx[min(scored)[1]]
    return None


class ServiceError(Exception):
    """A source that gave nothing usable. `billed` is set when the service answered (and charged) but the answer
    could not be used; the raw answer is then kept on disk and the ledger records the cost."""

    def __init__(self, kind, message, billed=False, key=None):
        super().__init__(message)
        self.kind = kind
        self.billed = billed
        self.key = key


def ledger_service_error(ledger, command, model, est, err, **extra):
    """The ledger line for a failed call: the estimate when the service charged for it, else $0."""
    billed = bool(getattr(err, "billed", False))
    ledger_add(ledger, command, model, 1, est if billed else 0.0, getattr(err, "key", None),
               "unsaved" if billed else "failed", error_kind=err.kind, **extra)


def http(method, url, headers=None, body=None, timeout=120):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    hdrs = dict(headers or {})
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read(), dict(resp.headers.items())
    except urllib.error.HTTPError as err:
        text = err.read().decode("utf-8", "replace")[:400]
        kind = {401: "auth", 403: "auth", 429: "quota", 402: "billing"}.get(err.code, "bad_request" if err.code < 500
                                                                              else "server")
        raise ServiceError(kind, scrub("HTTP %d from %s: %s" % (err.code, url.split("?")[0], text)))
    except (urllib.error.URLError, OSError) as err:
        raise ServiceError("network", scrub("network error calling %s: %s" % (url.split("?")[0], err)))


def freesound_base():
    return os.environ.get("NEXA_FREESOUND_BASE_URL", "https://freesound.org").rstrip("/")


def elevenlabs_base():
    return os.environ.get("NEXA_ELEVENLABS_BASE_URL", "https://api.elevenlabs.io").rstrip("/")


def freesound_fetch(query, out_dir, allow_cc_by=False, max_dur=30.0):
    """Search Freesound for CC0 (or, when allowed, CC-BY) effects and download the best match's preview."""
    key = freesound_key()
    if not key:
        raise ServiceError("no_key", "no Freesound key: set FREESOUND_API_KEY or store it in the keychain "
                                     "(security add-generic-password -a \"$USER\" -s FREESOUND_API_KEY -w)")
    lic = 'license:"Creative Commons 0"'
    if allow_cc_by:
        lic = '(license:"Creative Commons 0" OR license:"Attribution")'
    # /apiv2/search/ replaced /apiv2/search/text/ (deprecated November 2025)
    params = {"query": query, "filter": "%s duration:[0 TO %d]" % (lic, int(max_dur)), "page_size": 10,
              "sort": "score", "fields": "id,name,username,license,previews,duration,url,tags,is_explicit,"
                                         "single_event,loopable,loudness"}
    raw, _ = http("GET", freesound_base() + "/apiv2/search/?" + urllib.parse.urlencode(params),
                  headers={"Authorization": "Token " + key}, timeout=60)
    results = (json.loads(raw.decode("utf-8")) or {}).get("results") or []
    for r in results:
        if r.get("is_explicit"):
            continue
        lic_url = str(r.get("license") or "").lower()
        if "-nc" in lic_url or "noncommercial" in lic_url or "sampling" in lic_url:
            continue
        cc0 = "publicdomain/zero" in lic_url or lic_url.strip() in ("creative commons 0", "cc0")
        ccby = "/licenses/by/" in lic_url or lic_url.strip() == "attribution"
        if not (cc0 or (allow_cc_by and ccby)):
            continue
        prev = (r.get("previews") or {}).get("preview-hq-mp3") or (r.get("previews") or {}).get("preview-lq-mp3")
        if not prev:
            continue
        data, _ = http("GET", prev, timeout=120)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "freesound_%s.mp3" % r.get("id"))
        with open(path, "wb") as fh:
            fh.write(data)
        credit = None
        if not cc0:
            credit = '"%s" by %s (freesound.org/s/%s), licensed under CC BY' % (r.get("name"), r.get("username"),
                                                                              r.get("id"))
        return {"file": os.path.abspath(path), "source": "freesound",
                "source_url": r.get("url") or "https://freesound.org/s/%s/" % r.get("id"),
                "freesound_id": r.get("id"), "title": r.get("name"), "author": r.get("username"),
                "licence": "CC0" if cc0 else "CC BY", "licence_url": r.get("license"),
                "attribution": credit, "quality": "preview (about 128 kbps MP3); the original file needs OAuth2"}
    raise ServiceError("empty", "no %s result on Freesound for %r" % ("CC0 or CC BY" if allow_cc_by else "CC0", query))


_EL_PLAN = None


def eleven_plan():
    """The ElevenLabs plan for this run (read once): {"tier", "paid", "known", "credits_left", "note"}."""
    global _EL_PLAN
    if _EL_PLAN is None:
        try:
            _EL_PLAN = EL.plan_status()
        except EL.ElevenError as err:
            _EL_PLAN = {"tier": None, "paid": None, "known": False, "credits_left": None, "note": scrub(str(err))}
    return _EL_PLAN


def eleven_licence(plan):
    """What a client may do with ElevenLabs output from this account."""
    base = {"terms": ["https://elevenlabs.io/terms-of-use"], "content_id": "Do not register.",
            "attribution_required": False}
    if plan.get("paid") is True:
        return dict(base, source="ElevenLabs (%s plan)" % plan.get("tier"), commercial=True,
                    note="made on a paid plan: commercial use in client work is allowed, mixed into the video "
                         "(never delivered as separate sound files)")
    if plan.get("paid") is False:
        return dict(base, source="ElevenLabs (free plan)", commercial=False, attribution_required=True,
                    note="made on the free plan: non-commercial use only, with elevenlabs.io in the title; for "
                         "evaluation, not for client delivery")
    return dict(base, source="ElevenLabs (plan unknown)", commercial=None,
                note="the key cannot read the plan (turn on User access for the key); confirm a paid plan before "
                     "client delivery")


def eleven_call(fn, output_format, steps=("mp3_44100_192", "mp3_44100_128"), **kw):
    """Run an ElevenLabs call, stepping down the output format when the plan refuses it (PCM, then the MP3s in
    `steps`). Returns (data, info, format used)."""
    order = [output_format] + [f for f in steps if f != output_format]
    last = None
    for fmt in order:
        try:
            data, info = fn(output_format=fmt, **kw)
            return data, info, fmt
        except EL.ElevenError as err:
            last = err
            low = str(err).lower()
            if err.kind in ("plan", "bad_request") and re.search(r"\boutput[_ ]format\b|\bformat\b|\btier\b|"
                                                                 r"\bsubscription\b|\bplan\b", low):
                log("ElevenLabs refused %s (%s); trying %s" % (fmt, err.detail or err.kind,
                                                              order[order.index(fmt) + 1] if fmt != order[-1] else
                                                              "nothing else"))
                continue
            raise
    raise last


def elevenlabs_fetch(query, out_dir, duration=None, loop=False, influence=None, model=None):
    """One effect from ElevenLabs (text to sound effects), saved as it came plus a sidecar with the plan and the
    licence. PCM at 48 kHz when the length is known (the channel count is read from it), else 192 kbps MP3."""
    if not EL.keys():
        raise ServiceError("no_key", EL.MISSING_KEY_HELP)
    plan = eleven_plan()
    dur = float(duration) if duration else None
    model = "eleven_text_to_sound_v2" if loop else (model or EL.SFX_MODELS[0])   # only v2 makes loops
    fmt = "pcm_48000" if dur else "mp3_44100_192"
    try:
        data, info, fmt = eleven_call(EL.sound_effect, fmt, text=query, duration=dur, prompt_influence=influence,
                                      loop=loop or None, model_id=model)
    except EL.ElevenError as err:
        raise ServiceError(err.kind, scrub(str(err)))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, "elevenlabs_%s" % hashlib.sha256(
        ("%s|%s|%s|%s|%s" % (query, dur, loop, influence, time.time())).encode("utf-8")).hexdigest()[:10])
    try:
        path, meta = EL.save_audio(data, stem, fmt, expect_s=dur, info=info)
    except EL.ElevenError as err:
        rescue = stem + ".raw"
        with open(rescue, "wb") as fh:
            fh.write(data)
        raise ServiceError("unsaved", "%s; the paid answer is kept in %s" % (scrub(str(err)), rescue), billed=True,
                           key=info.get("key"))
    lic = eleven_licence(plan)
    side = {"schema": "nexa-sound/elevenlabs-1", "provider": "elevenlabs", "endpoint": "POST /v1/sound-generation",
            "model": model, "prompt": query, "duration_s": dur, "loop": bool(loop), "prompt_influence": influence,
            "output_format": fmt, "audio": meta, "response": EL.cost_headers(info), "key_source": info.get("key"),
            "plan": {"tier": plan.get("tier"), "known": plan.get("known")}, "licence": lic, "created": now_iso(),
            "sha256": sha256(path)}
    write_json(path + ".json", side)
    return {"file": os.path.abspath(path), "source": "elevenlabs", "model": model, "prompt": query,
            "plan": plan.get("tier"), "licence": lic["source"], "licence_url": lic["terms"][0],
            "commercial": lic["commercial"], "licence_note": lic["note"],
            "attribution": "elevenlabs.io (in the title)" if lic.get("attribution_required") else None,
            "key_source": info.get("key"), "output_format": fmt, "response": EL.cost_headers(info),
            "loop": bool(loop)}


def sound_points(path, known=None):
    """Attack, loudest-10-ms and end times plus the max momentary loudness of an effect file."""
    if known and all(k in known for k in ("attack_s", "peak_s")):
        pts = dict(known)
    else:
        a = decode_f32(path, channels=2)
        L, R = list(a[0::2]), list(a[1::2])
        pts = SX.measure(L, R)
    mono = probe(path)["channels"] == 1
    series = momentary(path, af=("pan=stereo|c0=c0|c1=c0," if mono else "") + "apad=pad_dur=0.5")
    vals = [v for _, v in series if v is not None]
    pts["m_max_lufs"] = round(max(vals), 2) if vals else None
    return pts


class Resolver(object):
    ORDER = ["file", "synth", "library", "media-use", "freesound", "elevenlabs"]

    def __init__(self, files_dir, offline, budget, ledger):
        self.files_dir = files_dir
        self.offline = offline
        self.budget = budget
        self.spent = 0.0
        self.ledger = ledger
        self.counts = {}
        self._lib = None
        self._mu = None
        self.notes = []

    def resolve(self, cue, index):
        order = [cue["source"]] if cue.get("source") else self.ORDER
        why = []
        for src in order:
            fn = getattr(self, "_" + src.replace("-", "_"), None)
            if fn is None:
                why.append("unknown source %s" % src)
                continue
            try:
                r = fn(cue, index)
            except ServiceError as err:
                why.append("%s: %s" % (src, err))
                continue
            if r:
                return r, why
        return None, why

    def _file(self, cue, index):
        f = cue.get("file")
        if not f:
            return None
        if not os.path.exists(f):
            raise ServiceError("missing", "%s does not exist" % f)
        side = try_json(stem_of(f) + ".json") or {}
        lic = side.get("licence") if isinstance(side, dict) else None
        return {"file": os.path.abspath(f), "source": "file",
                "licence": lic or cue.get("licence") or "supplied by the user (their licence)",
                "known": (side.get("measured") if isinstance(side, dict) else None)}

    def _synth(self, cue, index):
        name = SX.resolve_name(cue.get("name") or "") or SX.resolve_name(cue.get("query") or "")
        if not name:
            return None
        seed = cue.get("seed")
        if seed is None:
            self.counts[name] = self.counts.get(name, 0) + 1
            seed = self.counts[name]
        parts = [name, "s%d" % int(seed)]
        for k, tag in (("dur", "d"), ("pitch", "p"), ("brightness", "b")):
            if cue.get(k) is not None:
                parts.append("%s%s" % (tag, fmt_num(float(cue[k]))))
        os.makedirs(self.files_dir, exist_ok=True)
        path = os.path.join(self.files_dir, "_".join(parts) + ".wav")
        entry = SX.make(name, path, cue.get("dur"), int(seed), cue.get("pitch"), cue.get("brightness"))
        return {"file": os.path.abspath(path), "source": "synth", "preset": name, "params": entry["params"],
                "licence": LICENCE_SYNTH["licence"], "known": entry["measured"],
                "default_gain_db": entry["gain_db"], "default_align": entry["align"]}

    def _library(self, cue, index):
        if self._lib is None:
            self._lib = [(d, library_index(d)) for d in sfx_dirs()]
        for d, idx in self._lib:
            hit = match_key(idx, cue.get("name"), cue.get("query"))
            if hit:
                return {"file": os.path.abspath(hit["file"]), "source": "library", "library": d,
                        "licence": hit.get("licence") or "your own library (licence not recorded: confirm it)",
                        "attribution": hit.get("attribution")}
        return None

    def _media_use(self, cue, index):
        if self._mu is None:
            d = media_use_dir()
            self._mu = library_index(d) if os.path.isdir(d) else {}
        hit = match_key(self._mu, cue.get("name"), cue.get("query"))
        if not hit:
            return None
        return {"file": os.path.abspath(hit["file"]), "source": "media-use", "licence": LICENCE_PIXABAY["name"],
                "licence_url": LICENCE_PIXABAY["url"], "note": LICENCE_PIXABAY["note"]}

    def _freesound(self, cue, index):
        if self.offline or not freesound_key():
            return None
        return freesound_fetch(cue.get("query") or cue.get("name"), self.files_dir,
                               allow_cc_by=bool(cue.get("allow_cc_by")))

    def _elevenlabs(self, cue, index):
        if self.offline or not EL.keys():
            return None
        est = PRICES["elevenlabs-sfx"]
        if self.spent + est > self.budget + 1e-9:
            raise ServiceError("budget", "the budget of $%.2f is spent (an ElevenLabs effect is about $%.2f)"
                               % (self.budget, est))
        try:
            r = elevenlabs_fetch(cue.get("query") or cue.get("name"), self.files_dir, cue.get("dur"),
                                 loop=bool(cue.get("loop")), influence=cue.get("influence"))
        except ServiceError as err:
            if err.kind not in ("no_key",):
                ledger_service_error(self.ledger, "sfx", "elevenlabs-sfx", est, err)
                if err.billed:
                    self.spent += est
            raise
        self.spent += est
        ledger_add(self.ledger, "sfx", "elevenlabs-sfx", 1, est, r.get("key_source"), "ok", detail=r["prompt"][:80],
                   commercial=r.get("commercial"), response=r.get("response") or None)
        return r


def read_cues(path):
    data = read_json(path)
    if isinstance(data, dict):
        data = data.get("cues") or []
    if not isinstance(data, list):
        die("%s: cues must be a list like [{\"t\": 3.2, \"name\": \"whoosh\"}]" % path)
    cues = []
    for i, c in enumerate(data):
        if not isinstance(c, dict) or c.get("t") is None or not (c.get("name") or c.get("query") or c.get("file")):
            die("cue %d needs t and one of name, query or file" % i)
        if c.get("align") and c["align"] not in ("attack", "peak", "end"):
            die("cue %d: align is attack, peak or end" % i)
        cues.append(dict(c, t=float(c["t"])))
    return cues


def cmd_sfx_list(args):
    rows = [SX.info(n) for n in SX.PRESETS]
    mu = media_use_dir()
    sources = {"synth": len(rows), "library_dirs": sfx_dirs(), "media_use": mu if os.path.isdir(mu) else None,
               "freesound": bool(freesound_key()), "elevenlabs": bool(EL.keys())}
    lines = ["%-13s %5s  %-6s %5s  %s" % ("preset", "dur", "align", "gain", "description")]
    for r in rows:
        lines.append("%-13s %5s  %-6s %5s  %s" % (r["name"], fmt_num(r["dur"]), r["align"], fmt_num(r["gain_db"]),
                                                 r["description"]))
    lines.append("sources: synth; %d library folder(s); media-use %s; Freesound %s; ElevenLabs %s" % (
        len(sources["library_dirs"]), "found" if sources["media_use"] else "not found",
        "on" if sources["freesound"] else "off (no Freesound key)",
        "on" if sources["elevenlabs"] else "off (no ElevenLabs key)"))
    emit(args, {"ok": True, "presets": rows, "sources": sources}, lines)


def sfx_sidecar(path, entry):
    pts = sound_points(path, entry["measured"])
    lo = loudness(path, af="apad=pad_dur=0.5")
    side = {"schema": "nexa-sound/sfx-1", "skill_version": SKILL_VERSION, "created": now_iso(),
            "file": os.path.abspath(path), "sha256": sha256(path), "preset": entry["params"]["preset"],
            "description": entry["description"], "params": entry["params"], "format": entry["format"],
            "measured": dict(entry["measured"], m_max_lufs=pts.get("m_max_lufs"), true_peak_dbtp=lo["TP"]),
            "placement": {"align": entry["align"], "gain_db": entry["gain_db"],
                          "lead_s": fps_lead(30) if entry["align"] == "peak" else 0.0},
            "licence": LICENCE_SYNTH["licence"], "source": "synth", "synth_version": entry["synth_version"]}
    return side


def cmd_sfx_make(args):
    if args.name == "all":
        os.makedirs(args.out, exist_ok=True)
        manifest = {"_licence": LICENCE_SYNTH["licence"], "_made_by": "nexa-sound %s" % SKILL_VERSION}
        rows = []
        for name in SX.PRESETS:
            path = os.path.join(args.out, name + ".wav")
            entry = SX.make(name, path, None, args.seed)
            side = sfx_sidecar(path, entry)
            write_json(stem_of(path) + ".json", side)
            manifest[name] = {"file": name + ".wav", "duration": entry["measured"]["duration_s"],
                              "description": entry["description"], "align": entry["align"],
                              "gain_db": entry["gain_db"], "attack_s": entry["measured"]["attack_s"],
                              "peak_s": entry["measured"]["peak_s"], "licence": LICENCE_SYNTH["licence"]}
            rows.append({"name": name, "file": os.path.abspath(path), "measured": side["measured"]})
        write_json(os.path.join(args.out, "manifest.json"), manifest)
        emit(args, {"ok": True, "folder": os.path.abspath(args.out), "files": rows},
             ["made %d effects in %s (manifest.json lists them; add the folder to NEXA_SFX_DIRS to reuse it)" % (
                 len(rows), args.out)])
        return
    name = SX.resolve_name(args.name)
    if not name:
        die("no preset %r; see: sound.py sfx list" % args.name)
    check_out(args.out, [])
    try:
        entry = SX.make(name, args.out, args.dur, args.seed, args.pitch, args.brightness)
    except ValueError as err:
        die(str(err))
    side = sfx_sidecar(args.out, entry)
    rp = report_path(args.out, "sfx")
    write_json(rp, side)
    m = side["measured"]
    emit(args, dict(side, ok=True, report=rp), [
        "%s: %s, %.3f s, peak %.1f dBFS (true peak %s dBTP), attack %.1f ms, loudest at %.3f s, DC %.5f, "
        "tail %.0f dBFS" % (name, args.out, m["duration_s"], m["peak_dbfs"], m.get("true_peak_dbtp"),
                            1000 * m["attack_s"], m["peak_s"], m["dc_offset"], m["tail_rms_dbfs"]),
        "place it: align %s, gain %s dB against the dialogue" % (entry["align"], fmt_num(entry["gain_db"])),
        "report: %s" % rp])


def cmd_sfx_place(args):
    cues = read_cues(args.cues)
    D = float(args.duration)
    if D <= 0:
        die("--duration must be positive")
    check_out(args.out, [args.cues])
    out_dir = os.path.dirname(os.path.abspath(args.out))
    files_dir = stem_of(args.out) + "_files"
    ledger = ledger_file(out_dir, args.project)
    res = Resolver(files_dir, args.offline, args.budget, ledger)
    placed, skipped = [], []
    measured = {}
    N = int(round(D * SR))
    inputs, graph = [], []
    for i, cue in enumerate(cues):
        r, why = res.resolve(cue, i)
        if not r:
            skipped.append({"index": i, "t": cue["t"], "name": cue.get("name") or cue.get("query") or cue.get("file"),
                            "reason": "; ".join(why) or "nothing matched (no preset, library, media-use or online "
                                                        "source)"})
            continue
        preset = SX.resolve_name(cue.get("name") or cue.get("query") or "")
        pinfo = SX.info(preset) if preset else {}
        align = cue.get("align") or r.get("default_align") or pinfo.get("align") or "attack"
        gain = cue.get("gain_db")
        if gain is None:
            gain = r.get("default_gain_db", pinfo.get("gain_db", -12.0))
        if r["file"] not in measured:
            measured[r["file"]] = sound_points(r["file"], r.get("known"))
        pts = measured[r["file"]]
        lead = float(cue.get("lead_s", fps_lead(args.fps) if align == "peak" else 0.0))
        if align == "attack":
            ref = pts["attack_s"]
        elif align == "peak":
            ref = pts["peak_s"]
        else:
            ref = pts.get("climax_s") or pts["peak_s"]
        start = cue["t"] - ref - lead
        m_max = pts.get("m_max_lufs")
        applied = (REF_DIALOGUE_LUFS + gain - m_max) if m_max is not None else gain
        s0 = int(round(start * SR))
        head = max(0, -s0)
        if s0 >= N:
            skipped.append({"index": i, "t": cue["t"], "name": cue.get("name") or cue.get("query"),
                            "reason": "starts after the end of the video"})
            continue
        k = len(inputs)
        inputs.append(r["file"])
        ch = probe(r["file"])["channels"]
        f = []
        if ch == 1:
            f.append("pan=stereo|c0=c0|c1=c0")
        elif ch > 2:
            f.append("aformat=channel_layouts=stereo")
        f.append("aresample=48000")
        if head:
            f.append("atrim=start_sample=%d,asetpts=PTS-STARTPTS" % head)
            f.append("afade=t=in:st=0:d=0.005")
        f.append("volume=%.4fdB" % applied)
        if s0 > 0:
            f.append("adelay=delays=%dS:all=1" % s0)
        graph.append("[%d:a]%s[c%d]" % (k, ",".join(f), k))
        length = pts["duration_s"]
        placed.append({"index": i, "t": cue["t"], "name": cue.get("name") or cue.get("query"),
                       "resolved": {kk: vv for kk, vv in r.items() if kk not in ("known",)},
                       "align": align, "lead_s": lead, "ref_s": round(ref, 5), "start_s": round(start, 5),
                       "gain_db": gain, "applied_gain_db": round(applied, 2), "m_max_lufs": m_max,
                       "trimmed_head_s": round(head / float(SR), 4),
                       "trimmed_tail_s": round(max(0.0, start + length - D), 4)})
    if inputs:
        mix_in = "".join("[c%d]" % k for k in range(len(inputs)))
        if len(inputs) > 1:
            graph.append("%samix=inputs=%d:normalize=0:duration=longest,apad=whole_len=%d,atrim=end_sample=%d,"
                         "afade=t=out:st=%.4f:d=0.01[out]" % (mix_in, len(inputs), N, N, max(0.0, D - 0.01)))
        else:
            graph.append("%sapad=whole_len=%d,atrim=end_sample=%d,afade=t=out:st=%.4f:d=0.01[out]" % (
                mix_in, N, N, max(0.0, D - 0.01)))
        args_ff = ["-y", "-v", "error"]
        for f in inputs:
            args_ff += ["-i", f]
        args_ff += ["-filter_complex", ";".join(graph), "-map", "[out]", "-ar", SR, "-ac", 2, "-c:a", "pcm_s24le",
                    args.out]
        run_ff(args_ff, what="placing the effects")
    else:
        run_ff(["-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", "%.6f" % D, "-c:a",
                "pcm_s24le", args.out], what="writing a silent stem")
    licences = sorted({p["resolved"].get("licence") for p in placed if p["resolved"].get("licence")})
    cues_path = stem_of(args.out) + "_cues.json"
    report = {"schema": "nexa-sound/sfx-cues-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "stem": os.path.abspath(args.out), "duration_s": D, "sample_rate": SR,
              "reference_dialogue_lufs": REF_DIALOGUE_LUFS, "fps": args.fps,
              "level_rule": "each effect's loudest 400 ms (momentary loudness) sits gain_db against a dialogue "
                            "anchor of -20 LUFS; mix moves the whole stem with the real dialogue level",
              "cues": placed, "skipped": skipped, "licences": licences,
              "cost": {"est_usd": round(res.spent, 2)}}
    write_json(cues_path, report)
    lines = ["sfx stem: %s, %.2f s, %d effect%s placed, %d skipped" % (args.out, D, len(placed),
                                                                     "" if len(placed) == 1 else "s", len(skipped))]
    for p in placed:
        lines.append("  %6.3f s  %-14s %-9s align %-6s start %7.3f s  %+.1f dB" % (
            p["t"], (p["name"] or "")[:14], p["resolved"]["source"], p["align"], p["start_s"], p["applied_gain_db"]))
    for s in skipped:
        lines.append("  skipped %s at %.2f s: %s" % (s["name"], s["t"], s["reason"]))
    lines.append("cues: %s" % cues_path)
    emit(args, dict(report, ok=True, cues_file=cues_path), lines)


def cmd_sfx_fetch(args):
    os.makedirs(args.out, exist_ok=True)
    ledger = ledger_file(args.out, args.project)
    try:
        if args.source == "freesound":
            r = freesound_fetch(args.query, args.out, allow_cc_by=args.allow_cc_by)
        else:
            if not EL.keys():
                die(EL.MISSING_KEY_HELP)
            guard(PRICES["elevenlabs-sfx"], args.budget, "one ElevenLabs sound effect")
            try:
                r = elevenlabs_fetch(args.query, args.out, args.dur, loop=args.loop, influence=args.influence,
                                     model=args.model)
            except ServiceError as err:
                if err.kind not in ("no_key",):
                    ledger_service_error(ledger, "sfx fetch", "elevenlabs-sfx", PRICES["elevenlabs-sfx"], err)
                raise
            ledger_add(ledger, "sfx fetch", "elevenlabs-sfx", 1, PRICES["elevenlabs-sfx"], r.get("key_source"),
                       "ok", detail=args.query[:80], commercial=r.get("commercial"), response=r.get("response") or None)
    except ServiceError as err:
        die("%s: %s" % (args.source, err))
    wav = stem_of(r["file"]) + ".wav"
    if os.path.abspath(wav) == os.path.abspath(r["file"]):     # the answer is already a WAV: keep it as it came
        wav = stem_of(r["file"]) + "_48k.wav"
    to_wav(r["file"], wav, channels=2)
    pts = sound_points(wav)
    side = dict(r, schema="nexa-sound/sfx-1", skill_version=SKILL_VERSION, created=now_iso(),
                file=os.path.abspath(wav), original=r["file"], sha256=sha256(wav), measured=pts, query=args.query)
    write_json(stem_of(wav) + ".json", side)
    man_path = os.path.join(args.out, "manifest.json")
    man = try_json(man_path) or {}
    key = SX.slug(args.query) or os.path.basename(stem_of(wav))
    man[key] = {"file": os.path.basename(wav), "duration": pts["duration_s"], "description": args.query,
                "licence": r["licence"], "attribution": r.get("attribution"), "source": r["source"],
                "source_url": r.get("source_url")}
    write_json(man_path, man)
    emit(args, dict(side, ok=True), ["%s: %s (%s, %.2f s)%s" % (
        r["source"], wav, r["licence"], pts["duration_s"],
        ("; credit line: %s" % r["attribution"]) if r.get("attribution") else ""),
        "manifest: %s (add the folder to NEXA_SFX_DIRS to reuse it)" % man_path])


# ================================================================ dialogue clean-up

KNOWN_DELAY_MS = {"afftdn": 25.0, "anlmdn": 8.0, "isolate": 56.3}


def envelope_ms(path, af="highpass=f=100,lowpass=f=4000"):
    """1 ms RMS envelope of the speech band (16 kHz decode)."""
    x = decode_f32(path, rate=16000, channels=1, af=af)
    mul = operator.mul
    return [math.sqrt(sum(map(mul, x[i:i + 16], x[i:i + 16])) / 16.0) for i in range(0, len(x) - 15, 16)]


def xcorr_offset_ms(a, b, max_ms=150):
    """Lag (ms) that best lines b up with a: positive when b is late. Coarse at 10 ms, then 1 ms, then parabolic."""
    n = min(len(a), len(b))
    if n < 200:
        return None, 0.0
    a, b = a[:n], b[:n]
    ma, mb = sum(a) / n, sum(b) / n
    a = [v - ma for v in a]
    b = [v - mb for v in b]
    mul = operator.mul

    def corr(x, y, lag):
        if lag >= 0:
            return sum(map(mul, x[:len(x) - lag], y[lag:]))
        return sum(map(mul, x[-lag:], y[:len(y) + lag]))
    a10 = [sum(a[i:i + 10]) for i in range(0, n - 9, 10)]
    b10 = [sum(b[i:i + 10]) for i in range(0, n - 9, 10)]
    lags = range(-max_ms // 10, max_ms // 10 + 1)
    coarse = max(lags, key=lambda k: corr(a10, b10, k)) * 10
    fine = list(range(coarse - 15, coarse + 16))
    vals = [corr(a, b, k) for k in fine]
    i = max(range(len(vals)), key=vals.__getitem__)
    lag = float(fine[i])
    if 0 < i < len(vals) - 1:
        den = vals[i - 1] - 2 * vals[i] + vals[i + 1]
        if den != 0:
            lag += 0.5 * (vals[i - 1] - vals[i + 1]) / den
    energy = math.sqrt(sum(map(mul, a, a)) * sum(map(mul, b, b))) or 1e-12
    return lag, vals[i] / energy


def noise_floor(path):
    """dBFS of the quietest 1 s without speech: the twenty quietest 50 ms blocks (they need not touch, since dialogue
    rarely pauses for a whole second), after a high-pass at 80 Hz; and where the quietest block is. Blocks of digital
    silence are skipped."""
    x = decode_f32(path, rate=16000, channels=1, af="highpass=f=80:poles=2")
    mul = operator.mul
    blk = 800
    e = [(sum(map(mul, x[i:i + blk], x[i:i + blk])) / blk, i) for i in range(0, len(x) - blk + 1, blk)]
    e = [v for v in e if v[0] > 1e-13] or [(1e-13, 0)]
    e.sort()
    low = e[:20]
    return 10 * math.log10(sum(v for v, _ in low) / len(low) + 1e-13), round(low[0][1] / 16000.0, 2)


def isolate_bin():
    return os.path.join(home(), "bin", "voice-isolate")


def build_isolate():
    """Compile scripts/voice_isolate.swift once (swiftc, no downloads). Returns the binary or None with a reason."""
    override = os.environ.get("NEXA_SOUND_ISOLATE_BIN")
    if override:
        return (override, None) if os.path.exists(override) else (None, "NEXA_SOUND_ISOLATE_BIN points nowhere")
    src = os.path.join(HERE, "voice_isolate.swift")
    out = isolate_bin()
    if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
        return out, None
    swiftc = shutil.which("swiftc")
    if not swiftc or sys.platform != "darwin":
        return None, "Apple voice isolation needs macOS and swiftc (xcode-select --install)"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    log("compiling Apple's voice isolation helper once (swiftc, about 20 s)")
    r = subprocess.run([swiftc, "-O", src, "-o", out], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        return None, "swiftc failed: %s" % r.stderr.strip()[-300:]
    return out, None


def run_isolate(src48, work, n_samples):
    binp, why = build_isolate()
    if not binp:
        return None, why
    f32 = work.path("iso_in.wav")
    run_ff(["-y", "-v", "error", "-i", src48, "-af", "apad=pad_dur=0.2", "-c:a", "pcm_f32le", f32])
    caf = work.path("iso_out.caf")
    try:
        r = subprocess.run([binp, f32, caf, "100"], capture_output=True, text=True, timeout=1800)
    except (OSError, subprocess.TimeoutExpired) as err:
        return None, "voice isolation did not run: %s" % err
    if r.returncode != 0 or not os.path.exists(caf):
        return None, "voice isolation failed: %s" % (r.stderr or r.stdout).strip()[-300:]
    out = work.path("iso.wav")
    d = int(round(KNOWN_DELAY_MS["isolate"] / 1000.0 * SR))
    run_ff(["-y", "-v", "error", "-i", caf, "-af", "atrim=start_sample=%d,asetpts=PTS-STARTPTS,atrim=end_sample=%d,"
            "apad=whole_len=%d" % (d, n_samples, n_samples), "-c:a", "pcm_f32le", out])
    return out, None


EL_ISOLATE_USD_MIN = 0.12      # ElevenLabs voice isolator, API list price (pricing/api, 2026-09-25)


def run_isolate_eleven(src48, work, n_samples, channels, ledger, keep):
    """ElevenLabs' voice isolator: the file goes up as 16-bit WAV and comes back as MP3, which is decoded to the
    working rate and length; the clean-up's own sync check then measures and removes what delay is left. On a live
    test with cafe chatter at 5 dB SNR it left the least noise and sounded the most natural of the three ways
    (judge: clarity 9, noise left 1, natural 8; Apple 7, 2, 5)."""
    if not EL.keys():
        return None, "no ElevenLabs key", None
    up = work.path("iso_up.wav")
    run_ff(["-y", "-v", "error", "-i", src48, "-c:a", "pcm_s16le", up], what="the isolator's upload")
    secs = n_samples / float(SR)
    try:
        data, info = EL.isolate(up)
    except EL.ElevenError as err:
        ledger_add(ledger, "clean --isolate", "elevenlabs-isolate", 1, 0.0, None, "failed", error_kind=err.kind)
        return None, "ElevenLabs voice isolator: %s" % scrub(str(err)), None
    lic = eleven_licence(eleven_plan())
    ledger_add(ledger, "clean --isolate", "elevenlabs-isolate", 1, EL_ISOLATE_USD_MIN * secs / 60.0, info.get("key"),
               "ok", seconds=round(secs, 2), response=EL.cost_headers(info) or None, commercial=lic["commercial"])
    # the paid answer goes next to the output first: a later step that fails must not take it with the work folder
    got = stem_of(keep) + ".mp3"
    with open(got, "wb") as fh:
        fh.write(data)
    extra = {"engine": "elevenlabs", "licence": lic["source"], "commercial": lic["commercial"],
             "response": EL.cost_headers(info), "answer": os.path.abspath(got)}
    try:
        dec = work.path("iso_dec.wav")
        to_wav(got, dec, channels=channels, codec="pcm_f32le")
        out = work.path("iso.wav")
        run_ff(["-y", "-v", "error", "-i", dec, "-af", "atrim=end_sample=%d,apad=whole_len=%d" % (n_samples, n_samples),
                "-c:a", "pcm_f32le", out], what="the isolated voice")
    except (Exception, SystemExit) as err:
        return None, "ElevenLabs answered but its audio could not be read (%s); the paid answer is kept in %s" % (
            scrub(str(err))[:200], got), extra
    return out, None, extra


def cmd_clean(args):
    src = args.input
    check_out(args.out, [src])
    info = probe(src)
    ch = 1 if info["channels"] == 1 else 2
    t0 = time.time()
    notes = []
    with Work() as work:
        base = work.path("in48.wav")
        to_wav(src, base, channels=ch, codec="pcm_f32le")
        N = int(round(probe(base)["duration_s"] * SR))
        st = astats(base)
        clipped = (st["peak_db"] is not None and st["peak_db"] >= -0.1
                   and ((st["peak_count"] or 0) >= 20 or (st["flat_factor"] or 0) > 0))
        stage_in = base
        isolated, iso_engine, iso_info = False, None, None
        if args.isolate:
            iso_engine = args.isolate
            if iso_engine == "auto":
                iso_engine = "elevenlabs" if EL.keys() and eleven_plan().get("paid") is True else "apple"
            if iso_engine == "elevenlabs":
                iso, why, iso_info = run_isolate_eleven(base, work, N, ch, ledger_file(
                    os.path.dirname(os.path.abspath(args.out)) or ".", None), stem_of(args.out) + ".isolated")
            else:
                iso, why = run_isolate(base, work, N)
            if iso:
                stage_in, isolated = iso, True
            else:
                notes.append("voice isolation skipped: %s (the rest of the chain ran)" % why)
        nf_in, nf_at = noise_floor(stage_in)
        nf = max(-80.0, min(-20.0, round(nf_in, 1)))
        chain = []
        if clipped:
            chain += ["adeclick", "adeclip"]
            notes.append("many full-scale peaks: adeclick and adeclip ran first")
        chain.append("highpass=f=80:poles=2")
        delay_ms = 0.0
        if args.denoiser == "afftdn":
            chain.append("afftdn=nr=%g:nf=%g:tn=1" % (args.nr, nf))
            delay_ms += KNOWN_DELAY_MS["afftdn"]
        elif args.denoiser == "anlmdn":
            chain.append("anlmdn=s=0.0005:p=0.002:r=0.006:m=15")
            delay_ms += KNOWN_DELAY_MS["anlmdn"]
        if args.hum:
            for h in range(1, 5):
                chain.append("equalizer=f=%d:t=q:w=8:g=-30" % (args.hum * h))
        chain += ["equalizer=f=250:t=q:w=1.0:g=-2", "equalizer=f=4000:t=q:w=1.0:g=2"]
        if args.deess:
            chain.append("deesser=i=%g:m=0.5:f=0.5" % args.deess)
        chain.append("acompressor=threshold=-20dB:ratio=3:attack=8:release=120:knee=4:makeup=2dB")

        def render(extra_ms):
            d = int(round((delay_ms + extra_ms) / 1000.0 * SR))
            post = ["atrim=start_sample=%d" % d if d >= 0 else "adelay=delays=%dS:all=1" % (-d),
                    "asetpts=PTS-STARTPTS", "atrim=end_sample=%d" % N, "apad=whole_len=%d" % N]
            out = work.path("clean_f32.wav")
            run_ff(["-y", "-v", "error", "-i", stage_in, "-af", "apad=pad_dur=0.25," + ",".join(chain + post),
                    "-c:a", "pcm_f32le", out], what="the clean-up chain")
            return out
        extra = 0.0
        cleaned = render(extra)
        ref_env = envelope_ms(base)
        off, strength = xcorr_offset_ms(ref_env, envelope_ms(cleaned))
        first_off = off
        if off is not None and 1.0 < abs(off) <= 100.0 and strength > 0.3:
            extra = off
            cleaned = render(extra)
            off, strength = xcorr_offset_ms(ref_env, envelope_ms(cleaned))
            notes.append("measured %.1f ms of extra delay and removed it" % first_off)
        if off is None or abs(off) > 2.0:
            die("the cleaned file is not in sync with the input (offset %s ms, over 2 ms); nothing was written" % (
                "unknown" if off is None else "%.1f" % off))
        run_ff(["-y", "-v", "error", "-i", cleaned, "-c:a", "pcm_s24le", "-ar", SR, args.out])
    nf_out, _ = noise_floor(args.out)
    nf_src, _ = noise_floor(src)
    report = {"schema": "nexa-sound/clean-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "source": os.path.abspath(src), "source_sha256": sha256(src), "file": os.path.abspath(args.out),
              "format": {"sample_rate": SR, "codec": "pcm_s24le", "channels": ch},
              "chain": chain, "denoiser": args.denoiser, "nr": args.nr, "nf_used_db": nf, "hum": args.hum,
              "deess": args.deess, "isolate": dict({"asked": bool(args.isolate), "ran": isolated, "engine": iso_engine},
                                                   **(iso_info or {})),
              "noise_floor_db": {"before": round(nf_src, 1), "after": round(nf_out, 1), "measured_at_s": nf_at},
              "delay": {"removed_ms": round(delay_ms + extra + (KNOWN_DELAY_MS["isolate"]
                                                                 if isolated and iso_engine == "apple" else 0.0), 2),
                        "known_ms": delay_ms, "extra_measured_ms": round(extra, 2),
                        "sync_offset_ms": round(off, 2), "sync_ok": abs(off) <= 2.0,
                        "method": "cross-correlation of 1 ms speech-band envelopes, input against output"},
              "clipping_repair": clipped, "loudness": "not set here (mix sets it)", "notes": notes,
              "seconds": round(time.time() - t0, 2)}
    rp = report_path(args.out, "clean")
    write_json(rp, report)
    emit(args, dict(report, ok=True, report=rp), [
        "clean: %s -> %s (48 kHz, 24-bit)" % (src, args.out),
        "noise floor %.1f -> %.1f dBFS; in sync (offset %+.2f ms after removing %.1f ms of delay)" % (
            nf_src, nf_out, off, report["delay"]["removed_ms"])] + ["note: %s" % n for n in notes] +
         ["report: %s" % rp])


# ================================================================ ducking

def duck_keyframes(spans, duck_db=-14.0, lead=0.25, fall=0.20, tail=0.15, rise=0.60, bridge=0.8):
    """Piecewise-linear (seconds, dB) keyframes, the same shape as the research's duck_env.py: down by duck_db under
    speech, the fall starting lead + fall before a phrase, the rise starting tail after it, pauses shorter than
    bridge held down. One change: when a pause is too short for the rise to finish before the next fall, the two
    meet in a V instead of jumping (duck_env.py stepped from 0 to the duck level in one sample there)."""
    merged = []
    for s, e in sorted((float(a), float(b)) for a, b in spans):
        if merged and s - merged[-1][1] < bridge:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    kf = [[0.0, 0.0]]
    prev_rise = None
    for s, e in merged:
        fs, fe = s - lead - fall, s - lead
        rs, re_ = e + tail, e + tail + rise
        if prev_rise is None:
            if fs < 0.0:                        # no room for the whole fall: the music starts already down
                kf = [[0.0, duck_db]]
            else:
                kf.append([fs, 0.0])
                kf.append([fe, duck_db])
        elif fs >= prev_rise[1] - 1e-9:
            kf.append([fs, 0.0])
            kf.append([fe, duck_db])
        else:
            prs, pre = prev_rise
            t_x = (rise * fall + fall * prs + rise * fs) / (fall + rise)
            if t_x <= prs:
                kf.pop()                    # the fall starts before the rise does: stay down
            else:
                g_x = duck_db * (t_x - fs) / fall
                kf[-1] = [round(t_x, 4), min(0.0, g_x)]
                kf.append([max(fe, t_x), duck_db])
        kf.append([rs, duck_db])
        kf.append([re_, 0.0])
        prev_rise = (rs, re_)
    out = []
    for t, g in kf:
        t = round(max(0.0, t), 4)
        if out and abs(out[-1][0] - t) < 1e-9:
            out[-1] = [t, round(g, 2)]
        else:
            out.append([t, round(g, 2)])
    return out


def gain_at(kf, t):
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, g0), (t1, g1) in zip(kf, kf[1:]):
        if t0 <= t <= t1:
            return g0 if t1 == t0 else g0 + (g1 - g0) * (t - t0) / (t1 - t0)
    return kf[-1][1]


def write_gain_track(kf, seconds, path):
    """The envelope as linear gain, 1,000 values a second, in a mono float WAV (ffmpeg upsamples it)."""
    n = int(math.ceil(seconds * 1000)) + 2
    vals = array("f", [10 ** (gain_at(kf, i / 1000.0) / 20.0) for i in range(n)])
    write_f32(vals, path, rate=1000, channels=1, codec="pcm_f32le")


def apply_gain_track(music, gain_wav, out, n_samples, codec="pcm_s24le"):
    ch = probe(music)["channels"]
    up = "pan=stereo|c0=c0|c1=c0," if ch == 1 else ""
    g = ("[0:a]%s%s[m];[1:a]aresample=48000,pan=stereo|c0=c0|c1=c0[g];[m][g]amultiply,apad=whole_len=%d,"
         "atrim=end_sample=%d[out]" % (up, HQ_RESAMPLE, n_samples, n_samples))
    run_ff(["-y", "-v", "error", "-i", music, "-i", gain_wav, "-filter_complex", g, "-map", "[out]", "-ar", SR,
            "-c:a", codec, out], what="applying the duck envelope")


def spans_from_voice(paths, work):
    """Speech spans from silencedetect (-35 dB, 0.35 s) on the voice stems, summed."""
    if len(paths) == 1:
        v = paths[0]
    else:
        v = work.path("voices.wav")
        g = "".join("[%d:a]" % i for i in range(len(paths))) + "amix=inputs=%d:normalize=0:duration=longest[o]" % len(
            paths)
        a = ["-y", "-v", "error"]
        for p in paths:
            a += ["-i", p]
        run_ff(a + ["-filter_complex", g, "-map", "[o]", "-c:a", "pcm_f32le", v])
    dur = probe(v)["duration_s"]
    lo = loudness(v)
    thr = -35.0
    if lo["I"] is not None and lo["I"] < -30.0:
        thr = round(lo["I"] - 12.0, 1)
    sil = silences(v, thr, 0.35)
    spans, t = [], 0.0
    for s, e in sil:
        if s - t >= 0.1:
            spans.append([round(t, 3), round(s, 3)])
        t = e
    if dur - t >= 0.1:
        spans.append([round(t, 3), round(dur, 3)])
    return spans, thr


def cmd_duck(args):
    music = args.music
    check_out(args.out, [music, args.voice, args.speech])
    t0 = time.time()
    with Work() as work:
        if args.speech:
            spans, source = read_speech(args.speech), "speech file %s" % os.path.basename(args.speech)
        elif args.voice:
            spans, thr = spans_from_voice([args.voice], work)
            source = "silencedetect (%.0f dB, 0.35 s) on %s" % (thr, os.path.basename(args.voice))
        else:
            die("give --speech FILE or --voice FILE")
        D = probe(music)["duration_s"]
        N = int(round(D * SR))
        kf = duck_keyframes(spans, args.duck)
        gw = work.path("gain1k.wav")
        write_gain_track(kf, D, gw)
        apply_gain_track(music, gw, args.out, N)
    kf_path = stem_of(args.out) + ".keyframes.json"
    write_json(kf_path, kf)
    report = {"schema": "nexa-sound/duck-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "music": os.path.abspath(music), "file": os.path.abspath(args.out), "depth_db": args.duck,
              "params": DUCK, "spans": spans, "spans_source": source, "keyframes": kf, "keyframes_file": kf_path,
              "how": "gain envelope at 1 kHz, upsampled by ffmpeg, upmixed with pan=stereo|c0=c0|c1=c0 and applied "
                     "with amultiply", "remotion": "volume={(f) => 10 ** (interpolate(f, kf.map(k => k[0] * fps), "
                                                   "kf.map(k => k[1])) / 20)}",
              "seconds": round(time.time() - t0, 2)}
    rp = report_path(args.out, "duck")
    write_json(rp, report)
    emit(args, dict(report, ok=True, report=rp), [
        "duck: %s -> %s, %d speech span%s (%s), %d keyframes, %.0f dB under speech" % (
            os.path.basename(music), args.out, len(spans), "" if len(spans) == 1 else "s", source, len(kf), args.duck),
        "keyframes: %s" % kf_path, "report: %s" % rp])


# ================================================================ mix and master

def master_bus(src, out, target_i, target_tp, work):
    """The finishing rule (04 section 7.4): a 4x-oversampled limiter only when the peaks need it, then two-pass
    loudnorm with linear=true; pass 2's JSON must say linear, otherwise the ceiling drops and it runs again."""
    m0 = loudness(src)
    if m0["I"] is None:
        die("the mix is silent; nothing to master")
    attempts = []
    extra, margin = 0.5, 0.3
    trial = work.path("master_try.wav")   # a try that falls back to dynamic mode never reaches `out`
    for _ in range(6):
        g = target_i - m0["I"]
        need_lim = (m0["TP"] if m0["TP"] is not None else -99.0) + g > target_tp - margin
        if need_lim:
            ceiling = target_tp - margin
            pre = work.path("pre.wav")
            run_ff(["-y", "-v", "error", "-i", src, "-af",
                    "volume=%.3fdB,aresample=192000,alimiter=limit=%.6f:attack=1:release=60:level=disabled,"
                    "aresample=48000" % (g + extra, 10 ** (ceiling / 20.0)), "-c:a", "pcm_f32le", pre],
                   what="the master limiter")
        else:
            ceiling, pre = None, src
        err, _ = run_ff(["-nostats", "-v", "info", "-i", pre, "-af",
                         "loudnorm=I=%g:TP=%g:LRA=11:print_format=json" % (target_i, target_tp), "-f", "null", "-"],
                        what="loudnorm pass 1")
        p1 = parse_loudnorm(err)
        if need_lim and float(p1["input_i"]) < target_i - 0.05:
            extra += target_i - float(p1["input_i"]) + 0.3
            attempts.append({"ceiling_dbfs": ceiling, "pre_gain_db": round(g + extra, 2), "result": "too quiet "
                             "after limiting; more gain before the limiter"})
            continue
        if float(p1.get("input_lra") or 0.0) <= 0.0:
            gain = target_i - float(p1["input_i"])
            run_ff(["-y", "-v", "error", "-i", pre, "-af", "volume=%.4fdB" % gain, "-ar", SR, "-c:a", "pcm_s24le",
                    trial], what="the static gain")
            got = loudness(trial)
            fine = (got["I"] is not None and abs(got["I"] - target_i) <= 0.3
                    and (got["TP"] if got["TP"] is not None else -99.0) <= target_tp + 0.05)
            attempts.append({"limiter": need_lim, "ceiling_dbfs": ceiling, "method": "static gain",
                             "gain_db": round(gain, 2), "pass1": p1, "result": got})
            if fine:
                shutil.move(trial, out)
                return {"attempts": attempts, "limiter": need_lim, "ceiling_dbfs": ceiling,
                        "normalization": "linear", "method": "static gain (loudnorm keeps linear mode only for a "
                        "loudness range above 0, and this one measured 0)", "input": m0}
            margin += 1.0
            continue
        lra = min(50.0, max(11.0, float(p1["input_lra"]) + 1.0))
        ask = target_i
        for _pass in range(2):
            # loudnorm's own meter and ebur128 can differ by a few tenths of a LU: verify with ebur128 and, when it
            # is off by more than 0.1 LU, ask loudnorm once more for the corrected level (still one linear gain)
            err, _ = run_ff(["-y", "-nostats", "-v", "info", "-i", pre, "-af",
                             "loudnorm=I=%g:TP=%g:LRA=%g:measured_I=%s:measured_TP=%s:measured_LRA=%s:"
                             "measured_thresh=%s:offset=%s:linear=true:print_format=json" % (
                                 ask, target_tp, lra, p1["input_i"], p1["input_tp"], p1["input_lra"],
                                 p1["input_thresh"], p1["target_offset"]), "-ar", SR, "-c:a", "pcm_s24le", trial],
                            what="loudnorm pass 2")
            p2 = parse_loudnorm(err)
            got = loudness(trial) if p2.get("normalization_type") == "linear" else None
            if got is None or got["I"] is None or abs(got["I"] - target_i) <= 0.1:
                break
            nxt = ask + (target_i - got["I"])
            if (got["TP"] if got["TP"] is not None else -99.0) + (nxt - ask) > target_tp - 0.05:
                break
            ask = nxt
        attempts.append({"limiter": need_lim, "ceiling_dbfs": ceiling, "pre_gain_db": round(g + extra, 2)
                         if need_lim else 0.0, "pass1": p1, "pass2": p2, "asked_i": round(ask, 2)})
        if p2.get("normalization_type") == "linear":
            shutil.move(trial, out)
            return {"attempts": attempts, "limiter": need_lim, "ceiling_dbfs": ceiling,
                    "normalization": "linear", "input": m0}
        margin += 1.0
    die("the master could not stay linear (loudnorm kept falling back to dynamic mode after %d tries); nothing was "
        "written to %s. The mix has unusual peaks: check it, lower the music or the effects, and run mix again"
        % (len(attempts), out))


def parse_loudnorm(err):
    i = err.rfind("{")
    j = err.rfind("}")
    if i < 0 or j < i:
        die("loudnorm printed no JSON")
    return json.loads(err[i:j + 1])


def sections_report(series, spans, music_active, D):
    """Loudness of dialogue-only stretches, music-only stretches and the end card, from momentary loudness."""
    def inside(t, lo, hi):
        return lo <= t - 0.4 and t <= hi
    speech_vals, music_vals, end_vals = [], [], []
    last_end = max([e for _, e in spans] or [0.0])
    for t, m in series:
        if any(inside(t, s, e) for s, e in spans):
            speech_vals.append(m)
        elif spans and all(t - 0.4 >= e + 0.8 or t <= s - 0.8 for s, e in spans) and music_active(t):
            music_vals.append(m)
        if spans and t - 0.4 >= last_end + 0.8:
            end_vals.append(m)
    end_len = D - (last_end + 0.8)
    return {"dialogue_lufs": rnd(power_mean(speech_vals), 1), "music_only_lufs": rnd(power_mean(music_vals), 1),
            "end_card_lufs": rnd(power_mean(end_vals), 1) if end_len >= 1.5 else None,
            "end_card_from_s": round(last_end + 0.8, 2) if end_len >= 1.5 else None}


def section_warnings(sec):
    out = []
    d, m, e = sec.get("dialogue_lufs"), sec.get("music_only_lufs"), sec.get("end_card_lufs")
    if m is not None and d is not None and m > d + 3.0:
        out.append("music-only stretches are %.1f LU louder than the dialogue (more than 3)" % (m - d))
    if e is not None and d is not None and e < d - 15.0:
        out.append("the end card sits %.1f LU under the dialogue (more than 15)" % (d - e))
    return out


def cmd_mix(args):
    if args.platform not in PLATFORMS:
        die("--platform is one of %s" % ", ".join(PLATFORMS))
    target_i, target_tp = PLATFORMS[args.platform]
    ins = {k: getattr(args, k) for k in ("dialogue", "voice", "music", "sfx", "ambience") if getattr(args, k)}
    if not ins:
        die("give at least one of --dialogue, --voice, --music, --sfx, --ambience")
    check_out(args.out, list(ins.values()) + [args.speech])
    t0 = time.time()
    warnings, stems = [], {}
    stems_dir = stem_of(args.out) + "_stems"
    os.makedirs(stems_dir, exist_ok=True)
    lengths = {k: probe(p)["duration_s"] for k, p in ins.items()}
    speech_len = max([lengths[k] for k in ("dialogue", "voice") if k in lengths] or [0.0])
    D = args.duration or speech_len or max(lengths.values())
    if args.duration and speech_len and abs(args.duration - speech_len) > 0.05:
        warnings.append("--duration %.3f s differs from the speech (%.3f s): the mix %s" % (
            args.duration, speech_len, "cuts the speech short" if args.duration < speech_len else
            "runs on after the speech"))
    for k, length in sorted(lengths.items()):
        if k not in ("dialogue", "voice") and abs(length - D) > 0.05:
            warnings.append("%s is %.3f s and the mix %.3f s: it is %s" % (
                k, length, D, "cut at the end" if length > D else "padded with silence"))
    N = int(round(D * SR))
    with Work() as work:
        speech_paths = []
        for k in ("dialogue", "voice"):
            if k not in ins:
                continue
            raw = work.path(k + "_48k.wav")
            info = to_wav(ins[k], raw, channels=2, codec="pcm_f32le")
            lo = loudness(raw)
            if lo["I"] is None:
                warnings.append("%s is silent; left out" % k)
                continue
            g = REF_DIALOGUE_LUFS - lo["I"]
            st = os.path.join(stems_dir, k + ".wav")
            run_ff(["-y", "-v", "error", "-i", raw, "-af", "volume=%.4fdB,apad=whole_len=%d,atrim=end_sample=%d" % (
                g, N, N), "-c:a", "pcm_s24le", st])
            stems[k] = {"source": os.path.abspath(ins[k]), "file": st, "gain_db": round(g, 2),
                        "measured_lufs": lo["I"], "set_to_lufs": REF_DIALOGUE_LUFS,
                        "mono_as_dual_mono": info["channels"] == 1}
            speech_paths.append(st)
        spans, span_source = [], None
        if args.speech:
            spans, span_source = read_speech(args.speech), "speech file"
        elif speech_paths:
            spans, thr = spans_from_voice(speech_paths, work)
            span_source = "silencedetect (%.0f dB, 0.35 s) on the speech stems" % thr
        kf = None
        music_env = None
        if "music" in ins:
            raw = work.path("music_48k.wav")
            to_wav(ins["music"], raw, channels=2, codec="pcm_f32le")
            ducked = work.path("music_ducked.wav")
            if spans:
                kf = duck_keyframes(spans, args.duck)
                gw = work.path("gain1k.wav")
                write_gain_track(kf, D, gw)
                apply_gain_track(raw, gw, ducked, N, codec="pcm_f32le")
            else:
                run_ff(["-y", "-v", "error", "-i", raw, "-af", "apad=whole_len=%d,atrim=end_sample=%d" % (N, N),
                        "-c:a", "pcm_f32le", ducked])
            series = momentary(ducked)
            if spans:
                under = [m for t, m in series if any(s <= t - 0.4 and t <= e for s, e in spans)]
                m_sp = power_mean(under)
                if m_sp is None:
                    m_sp = (loudness(ducked)["I"] or -30.0)
                gm = (REF_DIALOGUE_LUFS - args.music_under) - m_sp
                how = "under speech it sits %s dB below the dialogue anchor" % fmt_num(args.music_under)
            else:
                mi = loudness(ducked)["I"]
                gm = (REF_DIALOGUE_LUFS - 2.0) - (mi if mi is not None else -30.0)
                how = "no speech: music set 2 dB under the -20 LUFS anchor"
            st = os.path.join(stems_dir, "music.wav")
            run_ff(["-y", "-v", "error", "-i", ducked, "-af", "volume=%.4fdB" % gm, "-c:a", "pcm_s24le", st])
            active = {round(t, 1) for t, m in series if m is not None}
            music_env = lambda t: round(t, 1) in active  # noqa: E731
            stems["music"] = {"source": os.path.abspath(ins["music"]), "file": st, "gain_db": round(gm, 2),
                              "ducked": bool(spans), "rule": how}
        if "sfx" in ins:
            raw = work.path("sfx_48k.wav")
            to_wav(ins["sfx"], raw, channels=2, codec="pcm_f32le")
            cues = try_json(stem_of(ins["sfx"]) + "_cues.json") or {}
            ref = cues.get("reference_dialogue_lufs", REF_DIALOGUE_LUFS) if isinstance(cues, dict) else \
                REF_DIALOGUE_LUFS
            gs = REF_DIALOGUE_LUFS - ref
            st = os.path.join(stems_dir, "sfx.wav")
            run_ff(["-y", "-v", "error", "-i", raw, "-af", "volume=%.4fdB,apad=whole_len=%d,atrim=end_sample=%d" % (
                gs, N, N), "-c:a", "pcm_s24le", st])
            stems["sfx"] = {"source": os.path.abspath(ins["sfx"]), "file": st, "gain_db": round(gs, 2),
                            "rule": "authored against a -20 LUFS dialogue anchor (sfx_cues.json)" if cues else
                            "no sfx_cues.json: used at unity"}
        if "ambience" in ins:
            # room tone and ambience stay steady (never ducked): a bed that dips under every line gives the
            # edit away; it sits --ambience-under dB under the dialogue anchor
            raw = work.path("ambience_48k.wav")
            to_wav(ins["ambience"], raw, channels=2, codec="pcm_f32le")
            ai = loudness(raw)["I"]
            if ai is None:
                warnings.append("ambience is silent; left out")
            else:
                ga = (REF_DIALOGUE_LUFS - args.ambience_under) - ai
                st = os.path.join(stems_dir, "ambience.wav")
                run_ff(["-y", "-v", "error", "-i", raw, "-af", "volume=%.4fdB,apad=whole_len=%d,atrim=end_sample=%d"
                        % (ga, N, N), "-c:a", "pcm_s24le", st])
                stems["ambience"] = {"source": os.path.abspath(ins["ambience"]), "file": st, "gain_db": round(ga, 2),
                                     "rule": "steady, %s dB under the dialogue anchor" % fmt_num(args.ambience_under)}
        order = [k for k in ("dialogue", "voice", "music", "sfx", "ambience") if k in stems]
        summed = work.path("sum.wav")
        a = ["-y", "-v", "error"]
        for k in order:
            a += ["-i", stems[k]["file"]]
        g = "".join("[%d:a]" % i for i in range(len(order)))
        g += ("amix=inputs=%d:normalize=0:duration=longest," % len(order) if len(order) > 1 else "anull,")
        g += "apad=whole_len=%d,atrim=end_sample=%d[o]" % (N, N)
        run_ff(a + ["-filter_complex", g, "-map", "[o]", "-c:a", "pcm_f32le", summed], what="summing the stems")
        mb = master_bus(summed, args.out, target_i, target_tp, work)
    final = loudness(args.out)
    series = momentary(args.out)
    sec = sections_report(series, spans, music_env or (lambda t: False), D)
    warnings += section_warnings(sec)
    if final["I"] is None or abs(final["I"] - target_i) > 0.5:
        warnings.append("integrated loudness %s LUFS is more than 0.5 LU from the %s target" % (final["I"], target_i))
    if final["TP"] is not None and final["TP"] > target_tp + 0.05:
        warnings.append("true peak %.2f dBTP is over the %s dBTP target" % (final["TP"], target_tp))
    report = {"schema": "nexa-sound/mix-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "file": os.path.abspath(args.out), "platform": args.platform,
              "target": {"I": target_i, "TP": target_tp},
              "measured": {"I": final["I"], "TP": final["TP"], "LRA": final["LRA"]},
              "normalization": mb["normalization"], "master": {k: v for k, v in mb.items() if k != "normalization"},
              "format": {"sample_rate": SR, "codec": "pcm_s24le", "channels": 2}, "duration_s": D,
              "stems": stems, "speech": {"spans": spans, "source": span_source},
              "duck": {"keyframes": kf, "depth_db": args.duck if kf else None, "params": DUCK if kf else None},
              "sections": sec, "warnings": warnings, "seconds": round(time.time() - t0, 2)}
    rp = report_path(args.out, "mix")
    write_json(rp, report)
    emit(args, dict(report, ok=True, report=rp), [
        "mix: %s for %s: %s LUFS, %s dBTP, LRA %s (target %s LUFS, %s dBTP), %s" % (
            args.out, args.platform, final["I"], final["TP"], final["LRA"], target_i, target_tp, mb["normalization"]),
        "stems: %s (%s)" % (", ".join("%s %+.1f dB" % (k, stems[k]["gain_db"]) for k in order), stems_dir),
        "sections: dialogue %s, music only %s, end card %s LUFS" % (sec["dialogue_lufs"], sec["music_only_lufs"],
                                                                   sec["end_card_lufs"])] +
         ["warning: %s" % w for w in warnings] + ["report: %s" % rp])


# ================================================================ QC

def max_full_scale_run(path, peak_db=None):
    """The longest run of consecutive samples at |x| >= 0.999, on either channel (scanned only when the peak is
    that high)."""
    if peak_db is not None and peak_db < 20 * math.log10(0.999):
        return 0
    a = decode_f32(path, rate=probe(path)["sample_rate"] or SR, channels=2)
    best = 0
    for c in (0, 1):
        run = 0
        for v in a[c::2]:
            if v >= 0.999 or v <= -0.999:
                run += 1
                if run > best:
                    best = run
            else:
                run = 0
    return best


def check(checks, cid, ok, value, threshold, detail, severity="fail"):
    checks.append({"id": cid, "ok": bool(ok), "severity": severity, "value": value, "threshold": threshold,
                   "detail": detail})


def measured_checks(path, kind, brief=None, sidecar=None, fit=None, mix=None, target=None, lo=None):
    """The measured checks for music, effects and mixes: format, clipping, loudness, silences, ending, tempo, DC,
    mono fold-down and, for music, vocals in an instrumental."""
    brief = brief or {}
    checks = []
    pr = probe(path)
    dur = pr["duration_s"]
    lo = lo or loudness(path)
    st = astats(path)
    if kind == "sfx":
        check(checks, "format", pr["channels"] == 2 and pr["sample_rate"] == SR, "%d ch, %d Hz" % (
            pr["channels"], pr["sample_rate"]), "stereo, 48 kHz", "effects are delivered as 48 kHz stereo")
    elif kind == "mix":
        check(checks, "format", pr["channels"] == 2 and pr["sample_rate"] == SR and (pr["bits"] or 24) >= 24,
              "%d ch, %d Hz, %s-bit" % (pr["channels"], pr["sample_rate"], pr["bits"]), "stereo, 48 kHz, 24-bit",
              "the master format")
    else:
        check(checks, "format", pr["channels"] == 2 and pr["sample_rate"] >= 44100, "%d ch, %d Hz" % (
            pr["channels"], pr["sample_rate"]), "stereo, 44.1 kHz or more", "not stereo fails")
    if target is None and fit:
        target = fit.get("target_s")
    if target is not None:
        check(checks, "duration", abs(dur - target) <= 0.05, round(dur, 3), "%.3f s +-50 ms" % target,
              "length against the target")
    run = max_full_scale_run(path, st["peak_db"])
    flat = st["flat_factor"] or 0.0
    check(checks, "clipping", run <= 10 and flat < 20.0, {"full_scale_run": run, "flat_factor_db": rnd(flat, 1)},
          "10 consecutive full-scale samples; flat tops of 10 samples or more at the peak level (flat factor 20 dB)",
          "hard clipping, including audio that clipped and was turned down afterwards")
    if kind == "mix":
        tgt = (mix or {}).get("target") or {}
        if tgt:
            check(checks, "loudness", lo["I"] is not None and abs(lo["I"] - tgt["I"]) <= 1.0, lo["I"],
                  "%s LUFS +-1 LU" % tgt["I"], "integrated loudness after mastering")
            check(checks, "true_peak", lo["TP"] is not None and lo["TP"] <= tgt["TP"] + 0.1, lo["TP"],
                  "%s dBTP" % tgt["TP"], "true peak after mastering")
        if mix:
            check(checks, "normalization", mix.get("normalization") == "linear", mix.get("normalization"), "linear",
                  "loudnorm must not fall back to dynamic mode")
            for w in mix.get("warnings") or []:
                check(checks, "mix_warning", False, w, None, "from mix.json", severity="warn")
    else:
        bed = any(s.get("narrated") for s in brief.get("sections") or [])
        check(checks, "loudness_range", lo["LRA"] is None or lo["LRA"] <= 8.0 or kind == "sfx", lo["LRA"], "8 LU",
              "loudness range for a bed under speech", severity="fail" if bed and kind == "music" else "warn")
    dc = abs(st["dc_offset"] or 0.0)
    original = bool(sidecar) and os.path.abspath(path) == os.path.abspath(
        ((sidecar or {}).get("original") or {}).get("file") or "")
    if original and dc <= 0.02:     # Lyria takes carry 0.5 to 0.7 %; fit and loop take it out, the original stays
        check(checks, "dc_offset", dc <= 0.005, round(dc, 6), "0.5 %",
              "mean of all samples; fit and loop remove it (5 Hz high-pass)", severity="warn")
    else:
        check(checks, "dc_offset", dc <= 0.005, round(dc, 6), "0.5 %", "mean of all samples")
    if kind in ("music", "mix"):
        fold = loudness(path, af="pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1")
        drop = (lo["I"] - fold["I"]) if lo["I"] is not None and fold["I"] is not None else None
        check(checks, "mono_fold_down", drop is None or drop <= 3.0, rnd(drop, 2), "3 LU",
              "loudness lost when L and R are summed")
        sil = [s for s in silences(path, -50.0, 0.75) if s[0] > 0.3 and s[1] < dur - 0.5]
        check(checks, "silence_inside", not sil, sil, "none", "silences of 0.75 s or more inside the body",
              severity="fail" if kind == "music" else "warn")
        li = lead_in(path)
        check(checks, "lead_in", li <= 0.3, round(li, 3), "0.3 s", "silence before the music starts (fit trims it)",
              severity="warn")
    if kind == "music":
        x = decode_f32(path, rate=16000, channels=1, start=max(0.0, dur - 2.5))
        n = len(x)

        def rdb(seg):
            return 10 * math.log10(sum(v * v for v in seg) / len(seg) + 1e-12) if seg else -120.0
        last50, before = rdb(x[max(0, n - 800):]), rdb(x[max(0, n - 32800):max(0, n - 800)])
        abrupt = last50 > -35.0 and last50 > before - 6.0
        check(checks, "ending", not abrupt, {"last_50ms_dbfs": round(last50, 1), "before_dbfs": round(before, 1)},
              "not above -35 dBFS without decay", "an abrupt ending needs fit (fade or ring-out)")
        want = brief.get("bpm")
        if want:
            if fit and fit.get("tempo_factor"):
                want = want * fit["tempo_factor"]
            try:
                g = BT.analyze(path, want)
                got = g["bpm"]
                ratios = [got / want, got * 2 / want, got / 2 / want]
                err = min(abs(r - 1.0) for r in ratios)
                check(checks, "tempo", err <= 0.04, got, "%.1f BPM +-4 %% (half and double allowed)" % want,
                      "measured tempo against the brief")
            except BT.BeatError as e:
                check(checks, "tempo", False, None, want, "no beat grid: %s" % e, severity="warn")
        if not brief.get("vocals"):
            timed = ((sidecar or {}).get("response") or {}).get("timed_lines") or []
            lyric = [t for t in timed if lyric_like(t.get("text", ""))]
            check(checks, "vocals", not lyric, [t["text"] for t in lyric][:5], "no timed lyric lines",
                  "timed lyric lines in the model's text mean the take has vocals")
    if kind == "sfx":
        a = decode_f32(path, channels=2)
        L, R = list(a[0::2]), list(a[1::2])
        m = SX.measure(L, R)
        check(checks, "peak", m["peak_dbfs"] <= -0.5, m["peak_dbfs"], "-0.5 dBFS", "sample peak")
        check(checks, "tail", m["tail_rms_dbfs"] <= -50.0, m["tail_rms_dbfs"], "-50 dBFS", "the last 20 ms decay "
              "to silence")
        check(checks, "attack", m["attack_s"] <= 0.3 or (brief.get("align") == "end"), m["attack_s"], "0.3 s",
              "the effect starts promptly", severity="warn")
    return {"checks": checks, "loudness": lo, "astats": st, "probe": pr}


def qc_summary(q, judge, brief, kind):
    failed = [c["id"] for c in q["checks"] if not c["ok"] and c["severity"] == "fail"]
    warned = [c["id"] for c in q["checks"] if not c["ok"] and c["severity"] == "warn"]
    passed = not failed
    rule = "all measured checks pass"
    if judge is not None and kind == "music":
        rule = "measured checks pass, vocals_present false for an instrumental, fit_to_brief >= 7, ending not abrupt"
        if not brief.get("vocals") and judge.get("vocals_present"):
            failed.append("judge_vocals")
        if (judge.get("fit_to_brief_1_10") or 0) < 7:
            failed.append("judge_fit_to_brief")
        if judge.get("ending") == "abrupt_cut":
            failed.append("judge_ending")
        passed = not failed
    return {"passed": passed, "failed": failed, "warnings": warned, "listened": judge is not None,
            "vocals_present": (judge or {}).get("vocals_present"), "ending": (judge or {}).get("ending"),
            "fit_to_brief": (judge or {}).get("fit_to_brief_1_10"), "problems": (judge or {}).get("problems"),
            "pass_rule": rule, "checked": now_iso()}


JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "genre": {"type": "string"}, "mood": {"type": "string"}, "tempo_feel": {"type": "string"},
        "instruments": {"type": "array", "items": {"type": "string"}},
        "vocals_present": {"type": "boolean"},
        "vocal_spans": {"type": "array", "items": {"type": "string"}},
        "sections": {"type": "array", "items": {"type": "object", "properties": {
            "start": {"type": "string"}, "end": {"type": "string"}, "label": {"type": "string"},
            "energy_1_10": {"type": "integer"}}}},
        "ending": {"type": "string", "enum": ["ring_out", "fade", "final_hit", "abrupt_cut"]},
        "fit_to_brief_1_10": {"type": "integer"},
        "problems": {"type": "array", "items": {"type": "string"}},
    },
}


def listen(path, brief, sidecar, budget, ledger, work):
    est = PRICES[MODEL_JUDGE]
    guard(est, budget, "the listening check")
    if not G.keys():
        die(G.MISSING_KEY_HELP + "\nWithout a key, run agy-watch-video's transcribe or ask on the file for a free "
            "listening check.")
    if has_encoder("libmp3lame"):
        clip, mime = work.path("judge.mp3"), "audio/mp3"
        run_ff(["-y", "-v", "error", "-i", path, "-ac", 1, "-b:a", "64k", clip], what="the judge's MP3")
    else:                                       # no MP3 encoder in this ffmpeg: 16 kHz mono WAV is small enough too
        clip, mime = work.path("judge.wav"), "audio/wav"
        run_ff(["-y", "-v", "error", "-i", path, "-ac", 1, "-ar", 16000, "-c:a", "pcm_s16le", clip],
               what="the judge's WAV")
    with open(clip, "rb") as fh:
        data = fh.read()
    if len(data) > G.INLINE_AUDIO_LIMIT:
        die("the file is too long for an inline listening check")
    prompt_bits = ["You are a music supervisor for video. Listen to the track and report in the JSON schema."]
    if brief:
        secs = "; ".join("%s to %s %s (intensity %s/10)" % (fmt_mmss(s["start"]), fmt_mmss(s["end"]), s["label"],
                                                             s["intensity"]) for s in brief.get("sections") or [])
        prompt_bits.append("Brief: mood %s, %s BPM, %s, %s; intended ending: %s; target length %s s.%s" % (
            brief.get("mood"), brief.get("bpm"), brief.get("key"),
            "vocals allowed" if brief.get("vocals") else "instrumental (any sung or spoken words are a problem)",
            brief.get("ending"), brief.get("duration_s"), (" Sections: " + secs + ".") if secs else ""))
        req = ((sidecar or {}).get("request") or {}).get("prompt")
        if req:
            prompt_bits.append("The prompt the track was made from: %s" % req)
    prompt_bits.append("Judge only what you hear. Do not judge fidelity, loudness or stereo width.")
    body = {"model": MODEL_JUDGE, "input": [{"type": "text", "text": "\n".join(prompt_bits)},
                                            {"type": "audio", "mime_type": mime,
                                             "data": base64.b64encode(data).decode("ascii")}],
            "response_format": JUDGE_SCHEMA, "store": False}
    try:
        resp, info = G.interactions(body, timeout=300)
    except G.GeminiError as err:
        ledger_add(ledger, "qc --listen", MODEL_JUDGE, 1, 0.0, None, "failed", error_kind=err.kind)
        die(scrub(gemini_message(err)))
    ledger_add(ledger, "qc --listen", MODEL_JUDGE, 1, est, info.get("key"), "ok")
    text = "".join(G.text_parts(resp)).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        verdict = json.loads(text)
    except ValueError:
        die("the listening judge did not return JSON: %s" % scrub(text[:200]))
    verdict["_model"] = MODEL_JUDGE
    verdict["_key_source"] = info.get("key")
    return verdict


def cmd_qc(args):
    path = args.file
    if not os.path.exists(path):
        die("%s does not exist" % path)
    side, side_path, rep = track_meta(path)
    own = None
    for p in (stem_of(path) + ".json", stem_of(path) + ".mix.json", stem_of(path) + ".sfx.json"):
        j = try_json(p) if os.path.exists(p) else None
        if isinstance(j, dict) and j.get("schema") in ("nexa-sound/mix-1", "nexa-sound/sfx-1"):
            own = j
            break
    kind = args.kind or {"nexa-sound/mix-1": "mix", "nexa-sound/sfx-1": "sfx"}.get((own or {}).get("schema"),
                                                                                   "music")
    mix = own if kind == "mix" and (own or {}).get("schema") == "nexa-sound/mix-1" else None
    fit = rep if isinstance(rep, dict) and rep.get("schema") == "nexa-sound/fit-1" else None
    brief = brief_summary(read_brief(args.brief)) if args.brief else (((side or {}).get("request") or {}).get("brief")
                                                                      or {})
    if kind == "sfx" and isinstance(own, dict):
        brief = dict(brief, align=(own.get("placement") or {}).get("align"))
    t0 = time.time()
    q = measured_checks(path, kind, brief, side, fit, mix, args.target)
    judge = None
    ledger = ledger_file(os.path.dirname(os.path.abspath(path)), args.project)
    if args.listen:
        with Work() as work:
            judge = listen(path, brief, side, args.budget, ledger, work)
    summary = qc_summary(q, judge, brief, kind)
    report = {"schema": "nexa-sound/qc-1", "skill_version": SKILL_VERSION, "created": now_iso(),
              "file": os.path.abspath(path), "kind": kind, "passed": summary["passed"], "summary": summary,
              "checks": q["checks"], "loudness": q["loudness"], "judge": judge,
              "seconds": round(time.time() - t0, 2)}
    qp = stem_of(path) + ".qc.json"
    write_json(qp, report)
    if side and side_path and (side.get("original") or {}).get("file") and \
            os.path.abspath(side["original"]["file"]) == os.path.abspath(path):
        side["qc"] = summary
        write_json(side_path, side)
        library_add({"id": side["id"], "qc_passed": summary["passed"], "qc_listened": summary["listened"]})
    lines = ["qc (%s): %s %s" % (kind, path, "PASSED" if summary["passed"] else "FAILED")]
    for c in q["checks"]:
        if not c["ok"]:
            lines.append("  %s %s: %s (limit %s): %s" % ("FAIL" if c["severity"] == "fail" else "warn", c["id"],
                                                         c["value"], c["threshold"], c["detail"]))
    if judge:
        lines.append("  judge: vocals %s, fit to brief %s/10, ending %s%s" % (
            judge.get("vocals_present"), judge.get("fit_to_brief_1_10"), judge.get("ending"),
            ("; problems: " + "; ".join(judge.get("problems") or [])) if judge.get("problems") else ""))
    elif kind == "music":
        lines.append("  not listened to: add --listen (Gemini, about $0.01), or run agy-watch-video on the file for "
                     "a free listening check")
    lines.append("report: %s" % qp)
    emit(args, dict(report, ok=True, report=qp), lines)
    if not summary["passed"]:
        sys.exit(2)


# ================================================================ library, credits, cost, doctor

def cmd_library(args):
    rows = library_entries()
    if args.mood:
        rows = [r for r in rows if r.get("mood") == args.mood]
    if args.bpm:
        m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*$", args.bpm)
        if not m:
            die("--bpm is a number or a range like 100-110")
        lo_b = float(m.group(1))
        hi_b = float(m.group(2)) if m.group(2) else lo_b
        if not m.group(2):
            lo_b, hi_b = lo_b - 3, hi_b + 3
        rows = [r for r in rows if r.get("bpm") is not None and lo_b <= float(r["bpm"]) <= hi_b]
    if args.min is not None:
        rows = [r for r in rows if (r.get("duration_s") or 0) >= args.min]
    if args.max is not None:
        rows = [r for r in rows if (r.get("duration_s") or 0) <= args.max]
    if args.passed:
        rows = [r for r in rows if r.get("qc_passed")]
    for r in rows:
        r["exists"] = bool(r.get("file")) and os.path.exists(r["file"])
    rows.sort(key=lambda r: (not r.get("qc_passed"), not r["exists"], str(r.get("created") or "")), reverse=False)
    lines = ["%d track%s in %s" % (len(rows), "" if len(rows) == 1 else "s", library_path())]
    for r in rows:
        lines.append("  %-38s %-13s %6s BPM %6.1f s  QC %-6s %s%s" % (
            r["id"], r.get("mood") or "", r.get("bpm"), r.get("duration_s") or 0,
            "passed" if r.get("qc_passed") else ("failed" if r.get("qc_passed") is False else "?"),
            r.get("file"), "" if r["exists"] else "  (missing)"))
    emit(args, {"ok": True, "library": library_path(), "tracks": rows}, lines)


ELEVEN_NOTES = [
    "ElevenLabs output is usable commercially only when made on a paid plan while subscribed; free-plan output is "
    "for evaluation (non-commercial, with elevenlabs.io in the title).",
    "Eleven Music on self-serve plans covers online video (YouTube, social, ads online), not film, TV, radio or "
    "games; Free to Pro plans are for individuals, a company needs Scale or Business. Clients in firearms, "
    "tobacco, prescription drugs, adult content, religious organisations or political campaigns may not use it.",
    "It is not exclusive: do not register it with Content ID. ElevenLabs adds an inaudible watermark; nobody "
    "tries to remove it.",
    "ElevenLabs sound effects go to the client mixed into the video, never as separate files or a library; "
    "turn off sharing on the Sound Effects page if the effects should not be offered to other users.",
]

CREDITS_NOTES = [
    "You may use this music in commercial videos, including client work. Google claims no ownership of Lyria output.",
    "It is not exclusive: Google can make similar music for others. Do not register it with Content ID, sell it as "
    "exclusive stock, or promise a client exclusivity.",
    "Pure AI music is probably not protected by copyright in the US, so a copycat may be hard to stop. Your own "
    "lyrics and real editing work count as human authorship.",
    "Every Lyria track carries Google's invisible SynthID watermark, and the original MP3s carry a C2PA credential. "
    "The untouched originals are kept, and nobody tries to remove either. Do not present the music as made only by "
    "people in order to deceive.",
    "Google offers no copyright indemnity for Lyria through the Gemini API. If a client needs indemnity, Google Vids "
    "(Workspace) is the indemnified route.",
    "No prompt named an artist, band, song or album, and no real song lyrics were used.",
    "Sound effects come from the skill's own synthesiser or from CC0 sources (no credit needed) unless listed below "
    "with a credit line. Non-commercial (NC) sounds and non-commercial AI models are never used.",
    "YouTube: background AI music does not need the 'altered or synthetic' label by itself; that label is for "
    "realistic depictions of real people, places or events.",
]


def cmd_credits(args):
    roots = args.dir if isinstance(args.dir, list) else [args.dir]
    for root in roots:
        if not os.path.isdir(root):
            die("%s is not a folder" % root)
    tracks, sfx, fetched, fits, beds, cleans = [], [], [], [], [], []
    walked = []
    for root in roots:
        walked += list(os.walk(root))
    for d, _, files in walked:
        for f in sorted(files):
            if not f.endswith(".json"):
                continue
            j = try_json(os.path.join(d, f))
            if not isinstance(j, dict):
                continue
            s = j.get("schema")
            if s == "nexa-sound/track-1":
                tracks.append(j)
            elif s == "nexa-sound/sfx-cues-1":
                sfx.append(j)
            elif s == "nexa-sound/sfx-1" and j.get("source") in ("freesound", "elevenlabs"):
                fetched.append(j)
            elif s == "nexa-sound/fit-1":
                fits.append(j)
            elif s == "nexa-sound/ambience-1":
                beds.append(j)
            elif s == "nexa-sound/clean-1" and (j.get("isolate") or {}).get("engine") == "elevenlabs" \
                    and (j.get("isolate") or {}).get("ran"):
                cleans.append(j)
    blocked = []
    for t in tracks:
        if ((t.get("provider") or {}).get("api") == "elevenlabs"
                and (t.get("licence") or {}).get("commercial") is not True):
            blocked.append("music %s" % t.get("id"))
    for f in fetched:
        if f.get("source") == "elevenlabs" and f.get("commercial") is not True:
            blocked.append("effect %s" % os.path.basename(f.get("file") or ""))
    for b in beds:
        if b.get("commercial") is not True:
            blocked.append("ambience %s" % os.path.basename(b.get("file") or ""))
    for c in cleans:
        if (c.get("isolate") or {}).get("commercial") is not True:
            blocked.append("voice isolation %s" % os.path.basename(c.get("file") or ""))
    for s_ in sfx:
        for c in s_.get("cues") or []:
            r = c.get("resolved") or {}
            if r.get("source") == "elevenlabs" and r.get("commercial") is not True:
                blocked.append("effect cue %s" % (r.get("prompt") or r.get("file")))
    lines = ["Music and sound: licence and provenance notes", "Prepared with nexa-sound %s on %s." % (
        SKILL_VERSION, datetime.date.today().isoformat()), ""]
    if blocked:
        lines += ["STATUS: NOT FOR CLIENT DELIVERY. %d item(s) come from a free or unknown ElevenLabs plan, whose "
                  "output is for evaluation only: %s. Make them again on a paid plan, or replace them." % (
                      len(blocked), "; ".join(blocked[:12])), ""]
    else:
        lines += ["STATUS: every item below may be used in client work under the notes that follow.", ""]
    lines.append("MUSIC")
    if not tracks:
        lines.append("- none")
    for t in tracks:
        p, o = t.get("provider") or {}, t.get("original") or {}
        b = (t.get("request") or {}).get("brief") or {}
        used = [f for f in fits if f.get("source") == o.get("file")]
        if p.get("api") == "elevenlabs":
            lines.append("- %s: made with ElevenLabs Music (%s, %s) on %s from a written brief (%s, %s BPM, %s)."
                         % (t.get("id"), p.get("model"), (t.get("licence") or {}).get("source"),
                            str(t.get("created_at"))[:10], b.get("mood"), fmt_num(b.get("bpm") or 0),
                            "with vocals" if b.get("vocals") else "instrumental"))
        else:
            lines.append("- %s: made with Google Lyria (%s, %s, Gemini API) on %s from a written brief (%s, %s BPM, "
                         "%s)." % (t.get("id"), p.get("model"), p.get("stage"), str(t.get("created_at"))[:10],
                                   b.get("mood"), fmt_num(b.get("bpm") or 0), "with vocals" if b.get("vocals")
                                   else "instrumental"))
        lines.append("  Original kept untouched: %s (sha256 %s)." % (os.path.basename(o.get("file") or ""),
                                                                     o.get("sha256")))
        for f in used:
            lines.append("  Edited to %.2f s for the video (%s); the edit is a new file." % (
                f.get("target_s"), ", ".join(op["op"] for op in f.get("ops") or [])))
        if not used:
            lines.append("  Not edited for this video (a draft or an unused take).")
    lines.append("")
    lines.append("WHAT THIS MEANS")
    lyria = [t for t in tracks if (t.get("provider") or {}).get("api") != "elevenlabs"]
    eleven = len(tracks) - len(lyria) + len(beds) + sum(1 for f in fetched if f.get("source") == "elevenlabs")
    for n in (CREDITS_NOTES if lyria or not tracks else CREDITS_NOTES[-3:]):  # the effects and labelling notes
        lines.append("- " + n)
    if eleven:
        for n in ELEVEN_NOTES:
            lines.append("- " + n)
    if beds:
        lines.append("")
        lines.append("AMBIENCE")
        for b in beds:
            lines.append("- %s: %s (%.1f s from a %.1f s loop). Licence: %s." % (
                os.path.basename(b.get("file") or ""), b.get("text"), b.get("duration_s") or 0,
                b.get("loop_s") or 0, ((b.get("source") or {}).get("licence")) or "ElevenLabs"))
    lines.append("")
    lines.append("SOUND EFFECTS")
    groups, credit_lines = {}, []
    for s_ in sfx:
        for c in s_.get("cues") or []:
            r = c.get("resolved") or {}
            name = r.get("preset") or r.get("title") or os.path.basename(r.get("file") or "")
            if r.get("source") == "freesound":
                name = '"%s" by %s (%s)' % (r.get("title"), r.get("author"), r.get("source_url"))
            g = groups.setdefault((r.get("source"), r.get("licence")), {})
            g[name] = g.get(name, 0) + 1
            if r.get("attribution"):
                credit_lines.append(r["attribution"])
    for f in fetched:
        name = os.path.basename(f.get("file") or "")
        if f.get("source") == "freesound":
            name = '"%s" by %s (%s)' % (f.get("title"), f.get("author"), f.get("source_url"))
        groups.setdefault((f.get("source"), f.get("licence")), {}).setdefault(name, 0)
        if f.get("attribution"):
            credit_lines.append(f["attribution"])
    if not groups:
        lines.append("- none")
    what = {"synth": "Made by nexa-sound's own synthesiser", "media-use": "From the media-use library (Pixabay)",
            "freesound": "From Freesound", "elevenlabs": "Generated with ElevenLabs Sound Effects",
            "library": "From your own library", "file": "Supplied files"}
    for (src, lic), names in sorted(groups.items(), key=lambda kv: str(kv[0])):
        listed = ", ".join("%s%s" % (n, (" (x%d)" % k) if k > 1 else "") for n, k in sorted(names.items()))
        lines.append("- %s: %s. Licence: %s." % (what.get(src, src), listed, lic))
    if credit_lines:
        lines.append("")
        lines.append("CREDIT LINES TO PASTE (CC BY)")
        for c in sorted(set(credit_lines)):
            lines.append("- " + c)
    text = "\n".join(lines) + "\n"
    check_out(args.out, [])
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(text)
    emit(args, {"ok": not (blocked and args.strict), "file": os.path.abspath(args.out), "tracks": len(tracks),
                "sfx_stems": len(sfx), "credit_lines": sorted(set(credit_lines)), "blocked": blocked},
         ["credits: %s (%d track%s, %d effect stem%s)" % (args.out, len(tracks), "" if len(tracks) == 1 else "s",
                                                          len(sfx), "" if len(sfx) == 1 else "s")]
         + (["NOT FOR CLIENT DELIVERY: %s" % "; ".join(blocked[:6])] if blocked else []))
    if blocked and args.strict:
        sys.exit(1)


def cmd_cost(args):
    plan = {}
    for k, model in (("draft", MODEL_DRAFT), ("final", MODEL_FINAL), ("listen", MODEL_JUDGE),
                     ("elevenlabs", "elevenlabs-sfx")):
        n = getattr(args, k)
        if n:
            plan[model] = {"calls": n, "est_usd": round(PRICES[model] * n, 2)}
    result = {"ok": True, "prices": PRICES}
    lines = []
    if plan:
        total = sum(v["est_usd"] for v in plan.values())
        result["estimate"] = {"items": plan, "total_usd": round(total, 2)}
        lines.append("estimate: $%.2f (%s)" % (total, ", ".join("%d x %s" % (v["calls"], k) for k, v in plan.items())))
    path = args.dir
    if path:
        lp = path if path.endswith(".jsonl") else ledger_file(path)
        rows = read_jsonl(lp)
        by = {}
        for r in rows:
            k = (r.get("model"), r.get("status"))
            b = by.setdefault(k, {"calls": 0, "est_usd": 0.0})
            b["calls"] += 1
            b["est_usd"] += float(r.get("est_usd") or 0.0)
        spent = sum(v["est_usd"] for (m, s), v in by.items() if s in ("ok", "empty", "unsaved"))
        result["ledger"] = {"file": lp, "entries": len(rows), "spent_usd": round(spent, 4),
                            "by": [{"model": m, "status": s, "calls": v["calls"], "est_usd": round(v["est_usd"], 4)}
                                   for (m, s), v in sorted(by.items(), key=lambda kv: str(kv[0]))]}
        lines.append("ledger %s: %d entries, about $%.2f spent" % (lp, len(rows), spent))
        for b in result["ledger"]["by"]:
            lines.append("  %-22s %-7s %3d call%s  $%.2f" % (b["model"], b["status"], b["calls"],
                                                            "" if b["calls"] == 1 else "s", b["est_usd"]))
    if not lines:
        lines.append("prices: " + ", ".join("%s $%.2f" % (k, v) for k, v in PRICES.items()))
    emit(args, result, lines)


def cmd_doctor(args):
    rep = {"skill_version": SKILL_VERSION}
    ff, fp = shutil.which("ffmpeg"), shutil.which("ffprobe")
    rep["ffmpeg"] = ff
    rep["ffprobe"] = fp
    have = ffmpeg_filters() if ff else set()
    rep["filters_missing"] = [f for f in FILTERS_USED if f not in have]
    enc = subprocess.run([ff, "-hide_banner", "-encoders"], capture_output=True, text=True).stdout if ff else ""
    rep["mp3_encoder"] = "libmp3lame" in enc
    rep["key_sources"] = G.key_sources()
    rep["freesound_key"] = bool(freesound_key())
    rep["elevenlabs_keys"] = EL.key_sources()
    rep["elevenlabs_key"] = bool(rep["elevenlabs_keys"])
    rep["uv"] = shutil.which("uv")
    py = os.path.join(home(), "venv", "bin", "python")
    rep["realtime_venv"] = py if os.path.exists(py) else None
    rep["swiftc"] = shutil.which("swiftc")
    rep["voice_isolate_helper"] = isolate_bin() if os.path.exists(isolate_bin()) else None
    mu = media_use_dir()
    rep["media_use_sfx"] = {"folder": mu, "files": len(library_index(mu))} if os.path.isdir(mu) else None
    rep["sfx_dirs"] = [{"folder": d, "files": len(library_index(d)), "exists": os.path.isdir(d)} for d in sfx_dirs()]
    rep["library"] = {"file": library_path(), "tracks": len(library_entries())}
    rep["ready"] = bool(ff and fp and not rep["filters_missing"])
    if args.live:
        try:
            names = G.list_models()
            want = [MODEL_FINAL, MODEL_DRAFT, MODEL_RT, MODEL_JUDGE]
            rep["live"] = {m: (m in names) for m in want}
            write_json(os.path.join(home(), "capabilities.json"), {
                "schema": "nexa-sound/capabilities-1", "checked": now_iso(), "models": rep["live"],
                "key_sources": rep["key_sources"]})
        except G.GeminiError as err:
            rep["live"] = {"error": scrub(gemini_message(err))}
        if rep["elevenlabs_key"]:
            plan = eleven_plan()
            rep["elevenlabs_plan"] = {k: plan.get(k) for k in ("tier", "paid", "known", "credits_left", "note")}
    lines = ["nexa-sound %s: %s" % (SKILL_VERSION, "ready" if rep["ready"] else "NOT ready"),
             "ffmpeg: %s%s" % (ff or "missing", (", missing filters: " + ", ".join(rep["filters_missing"]))
                               if rep["filters_missing"] else ", all filters present"),
             "Gemini key sources: %s" % (", ".join(rep["key_sources"]) or "none (drafts, finals and --listen need "
                                         "one; everything else works without)"),
             "Freesound key: %s; ElevenLabs key sources: %s" % ("yes" if rep["freesound_key"] else "no",
                                                                ", ".join(rep["elevenlabs_keys"]) or "none"),
             "RealTime: uv %s, venv %s" % ("found" if rep["uv"] else "missing", rep["realtime_venv"] or
                                           "not made yet (generate --realtime makes it on first use)"),
             "voice isolation: swiftc %s, helper %s" % ("found" if rep["swiftc"] else "missing",
                                                        rep["voice_isolate_helper"] or "compiled on first use"),
             "media-use effects: %s" % ("%d files" % rep["media_use_sfx"]["files"] if rep["media_use_sfx"] else
                                        "not installed"),
             "NEXA_SFX_DIRS: %s" % (", ".join("%s (%d)" % (d["folder"], d["files"]) for d in rep["sfx_dirs"]) or
                                    "none"),
             "library: %d track%s" % (rep["library"]["tracks"], "" if rep["library"]["tracks"] == 1 else "s")]
    if "live" in rep:
        lines.append("live: %s" % json.dumps(rep["live"]))
    if rep.get("elevenlabs_plan"):
        pl = rep["elevenlabs_plan"]
        lines.append("ElevenLabs plan: %s%s%s" % (
            pl["tier"] or "unknown", (", %s credits left" % pl["credits_left"]) if pl.get("credits_left") is not None
            else "", "; output is for client work" if pl.get("paid") else "; output is NOT for client work (%s)"
            % (pl.get("note") or "free plan")))
    emit(args, dict(rep, ok=rep["ready"]), lines)
    if not rep["ready"]:
        sys.exit(1)


# ================================================================ arguments

def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="print one JSON object instead of the summary")
    ap = argparse.ArgumentParser(description="nexa-sound: music, effects, clean-up, ducking, mixing and QC for "
                                             "videos. Details: references/cli.md.")
    ap.add_argument("--version", action="version", version="nexa-sound " + SKILL_VERSION)
    sub = ap.add_subparsers(dest="cmd")
    sub.required = True

    p = sub.add_parser("doctor", parents=[common], help="check tools, filters, keys (names only), helpers")
    p.add_argument("--live", action="store_true", help="also list the Lyria models the key's project sees (free)")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("moods", parents=[common], help="the 12 mood templates")
    p.set_defaults(func=cmd_moods)

    p = sub.add_parser("brief", parents=[common], help="build the Lyria prompt from the cuts and speech")
    p.add_argument("--duration", type=float, required=True, help="video length in seconds")
    p.add_argument("--mood", required=True)
    p.add_argument("--variant", help="a mood variant (bangla-folk: calm)")
    p.add_argument("--cuts", help="cuts JSON: [{t, weight, label}] or an EDL with cuts and speech")
    p.add_argument("--speech", help="speech spans: [[s, e]], nexa-speech words.json or {\"spans\": [...]}")
    p.add_argument("--bpm", type=float)
    p.add_argument("--key", help="for example 'C major' or 'A minor'")
    p.add_argument("--vocals", action="store_true", help="allow vocals (the prompt no longer ends 'Instrumental.')")
    p.add_argument("--notes", help="extra words for the prompt (no artist or song names)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_brief)

    p = sub.add_parser("generate", parents=[common], help="make music with ElevenLabs or Lyria")
    p.add_argument("brief")
    p.add_argument("--out", required=True, help="folder for originals and sidecars")
    p.add_argument("--engine", choices=["auto", "elevenlabs", "lyria"], default="auto",
                   help="auto: ElevenLabs on a paid plan, else a Lyria final")
    p.add_argument("--model", choices=list(EL.MUSIC_MODELS), help="ElevenLabs music model")
    p.add_argument("--draft", type=int, help="N drafts on lyria-3-clip-preview (30 s MP3, $0.04 each)")
    p.add_argument("--final", action="store_true", help="a final on lyria-3.5 (MP3, $0.08)")
    p.add_argument("--takes", type=int, default=1, help="finals to make (1 to 3)")
    p.add_argument("--realtime", action="store_true", help="an exact-length bed on lyria-realtime-exp (free for now)")
    p.add_argument("--seed", type=int, help="RealTime or ElevenLabs seed")
    p.add_argument("--images", help="up to 10 images (comma-separated) that steer the mood")
    p.add_argument("--budget", type=float, default=1.00, help="refuse a run whose estimate is higher (USD, 1.00)")
    p.add_argument("--project", help="the folder whose ledger.jsonl records the cost")
    p.set_defaults(func=cmd_generate)

    p = sub.add_parser("ambience", parents=[common], help="an ambience or room-tone bed of exact length "
                                                        "(ElevenLabs loop)")
    p.add_argument("text", help="what it sounds like: 'quiet office room tone, distant keyboard'")
    p.add_argument("--duration", type=float, required=True, help="length in seconds")
    p.add_argument("--out", required=True)
    p.add_argument("--piece", type=float, help="the loop's length, 4 to 30 s (default: up to 30 s)")
    p.add_argument("--influence", type=float, help="prompt influence, 0 to 1")
    p.add_argument("--model", choices=list(EL.SFX_MODELS))
    p.add_argument("--fade-in", type=float, default=1.0)
    p.add_argument("--fade-out", type=float, default=1.5)
    p.add_argument("--budget", type=float, default=1.00)
    p.add_argument("--project")
    p.set_defaults(func=cmd_ambience)

    p = sub.add_parser("fit", parents=[common], help="fit a track to the picture's length")
    p.add_argument("track")
    p.add_argument("--target", type=float, required=True, help="length in seconds")
    p.add_argument("--cuts", help="cuts JSON: hits on cuts (the start moves up to 2 s)")
    p.add_argument("--bpm", type=float, help="the tempo asked for (from the sidecar when there is one)")
    p.add_argument("--brief", help="the brief, when the track has no sidecar")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_fit)

    p = sub.add_parser("loop", parents=[common], help="a seamless loop of whole bars")
    p.add_argument("track")
    p.add_argument("--bars", type=int, default=8)
    p.add_argument("--bpm", type=float)
    p.add_argument("--out", required=True)
    p.add_argument("--preview", action="store_true", help="also write 3 repeats to check the join")
    p.set_defaults(func=cmd_loop)

    p = sub.add_parser("sfx", help="sound effects: list, make, place, fetch")
    ss = p.add_subparsers(dest="sfx_cmd")
    ss.required = True
    q = ss.add_parser("list", parents=[common], help="the synthesiser's presets and the sources in use")
    q.set_defaults(func=cmd_sfx_list)
    q = ss.add_parser("make", parents=[common], help="render one preset (or all) to 48 kHz 24-bit WAV")
    q.add_argument("name", help="a preset name, or 'all' with --out FOLDER")
    q.add_argument("--dur", type=float)
    q.add_argument("--seed", type=int, default=1)
    q.add_argument("--pitch", type=float)
    q.add_argument("--brightness", type=float)
    q.add_argument("--out", required=True)
    q.set_defaults(func=cmd_sfx_make)
    q = ss.add_parser("place", parents=[common], help="place cues on a stem the length of the video")
    q.add_argument("cues")
    q.add_argument("--duration", type=float, required=True)
    q.add_argument("--out", required=True)
    q.add_argument("--fps", type=float, default=30.0, help="frame rate for the default whoosh lead (1.5 frames)")
    q.add_argument("--offline", action="store_true", help="never use Freesound or ElevenLabs")
    q.add_argument("--budget", type=float, default=1.00)
    q.add_argument("--project")
    q.set_defaults(func=cmd_sfx_place)
    q = ss.add_parser("fetch", parents=[common], help="fetch one effect from Freesound (CC0) or ElevenLabs")
    q.add_argument("query")
    q.add_argument("--source", choices=["freesound", "elevenlabs"], required=True)
    q.add_argument("--out", required=True, help="folder")
    q.add_argument("--dur", type=float, help="ElevenLabs length, 0.5 to 30 s (without it the model chooses)")
    q.add_argument("--loop", action="store_true", help="ElevenLabs: a seamless loop (ambience, a bed)")
    q.add_argument("--influence", type=float, help="ElevenLabs prompt influence, 0 (free) to 1 (literal)")
    q.add_argument("--model", choices=list(EL.SFX_MODELS), help="ElevenLabs model (default %s)" % EL.SFX_MODELS[0])
    q.add_argument("--allow-cc-by", action="store_true", help="Freesound: also CC BY (a credit line is then needed)")
    q.add_argument("--budget", type=float, default=1.00)
    q.add_argument("--project")
    q.set_defaults(func=cmd_sfx_fetch)

    p = sub.add_parser("clean", parents=[common], help="dialogue clean-up, proved in sync")
    p.add_argument("input")
    p.add_argument("--out", required=True)
    p.add_argument("--isolate", nargs="?", const="auto", choices=["auto", "elevenlabs", "apple"],
                   help="voice isolation first: elevenlabs (best on the live test), apple (on the Mac, free), or "
                        "auto (ElevenLabs on a paid plan, else Apple)")
    p.add_argument("--denoiser", choices=["afftdn", "anlmdn", "none"], default="afftdn")
    p.add_argument("--nr", type=float, default=12.0, help="afftdn noise reduction in dB (10 to 15 is natural)")
    p.add_argument("--hum", type=int, choices=[50, 60], help="notch the mains hum and 3 harmonics")
    p.add_argument("--deess", type=float, help="de-ess intensity 0 to 1 (off unless given)")
    p.set_defaults(func=cmd_clean)

    p = sub.add_parser("duck", parents=[common], help="duck music under speech with a gain envelope")
    p.add_argument("--music", required=True)
    p.add_argument("--speech", help="speech spans file")
    p.add_argument("--voice", help="a voice stem (spans from silencedetect)")
    p.add_argument("--duck", type=float, default=-14.0, help="dB under speech (-14)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_duck)

    p = sub.add_parser("mix", parents=[common], help="mix the stems and master to a platform's loudness")
    p.add_argument("--dialogue")
    p.add_argument("--voice")
    p.add_argument("--music")
    p.add_argument("--sfx")
    p.add_argument("--ambience", help="a room tone or ambience bed (from `ambience`): steady, never ducked")
    p.add_argument("--speech", help="speech spans file (else found in the speech stems)")
    p.add_argument("--platform", required=True, help=", ".join(PLATFORMS))
    p.add_argument("--duck", type=float, default=-14.0)
    p.add_argument("--music-under", type=float, default=20.0, help="dB the music sits under speech (18 to 25)")
    p.add_argument("--ambience-under", type=float, default=24.0,
                   help="dB the ambience sits under the dialogue anchor (20 to 30)")
    p.add_argument("--duration", type=float, help="length in seconds (default: the dialogue or voice, else the "
                   "longest input; give the video length when music runs on after the last word)")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_mix)

    p = sub.add_parser("qc", parents=[common], help="measured checks, optional listening judge")
    p.add_argument("file")
    p.add_argument("--brief")
    p.add_argument("--kind", choices=["music", "sfx", "mix"])
    p.add_argument("--target", type=float, help="expected length in seconds")
    p.add_argument("--listen", action="store_true", help="Gemini listening judge (about $0.01)")
    p.add_argument("--budget", type=float, default=1.00)
    p.add_argument("--project")
    p.set_defaults(func=cmd_qc)

    p = sub.add_parser("library", parents=[common], help="search kept tracks before paying for new ones")
    p.add_argument("--mood")
    p.add_argument("--bpm", help="100-110, or one number (+-3)")
    p.add_argument("--min", type=float)
    p.add_argument("--max", type=float)
    p.add_argument("--passed", action="store_true", help="only tracks that passed QC")
    p.set_defaults(func=cmd_library)

    p = sub.add_parser("credits", parents=[common], help="licence and provenance note from the sidecars")
    p.add_argument("dir", nargs="+", help="one or more folders to read (a job's mix folder and its clean dialogue)")
    p.add_argument("--out", required=True)
    p.add_argument("--strict", action="store_true", help="exit 1 when anything is not for client delivery")
    p.set_defaults(func=cmd_credits)

    p = sub.add_parser("cost", parents=[common], help="estimate a plan, or read a ledger")
    p.add_argument("dir", nargs="?", help="a project folder (its ledger.jsonl) or a ledger file")
    p.add_argument("--draft", type=int)
    p.add_argument("--final", type=int)
    p.add_argument("--listen", type=int)
    p.add_argument("--elevenlabs", type=int)
    p.set_defaults(func=cmd_cost)
    return ap


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except KeyboardInterrupt:
        die("interrupted", 130)


if __name__ == "__main__":
    main()
