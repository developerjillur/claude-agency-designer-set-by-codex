#!/usr/bin/env python3
"""nexa-video-creator: edit real footage and make finished videos for every platform, with Remotion as the renderer.

The job, in order (each step writes files into the job folder and can be run again):

  nvc.py new JOB --target youtube [--title T] [--lang en]     make a job folder
  nvc.py add JOB FILE... [--role camera|screen|broll|image|voice|music|dialogue|segment|logo]
  nvc.py ingest JOB             probe, classify, H.264 proxies, audio, best microphone, face position
  nvc.py sync JOB               offset and drift of every other recording against the dialogue
  nvc.py clean JOB              dialogue clean-up (nexa-sound), delay removed and checked
  nvc.py transcribe JOB         word timings on the master clock (whisper.cpp, Gemini or agy), edges measured
  nvc.py brief JOB              edit-brief.md: the transcript with word ids, fillers, retakes, numbers, rules
  (Claude writes plan.json, the edit, grounded to word ids and quotes)
  nvc.py compile JOB            verify the plan and build the edit decision list (frames, captions, cues)
  nvc.py audio JOB              dialogue cut sample-accurately, music fitted, effects placed, mixed to the platform
  nvc.py stills JOB             key frames on one contact sheet (seconds)
  nvc.py render JOB             the video (Remotion 4.0.528)
  nvc.py qa JOB [--review]      measured QA (agy-watch-video) and the plan's own checks
  nvc.py deliver JOB            final files: video, subtitles, chapters, credits, disclosure notes, report

  nvc.py segment broll|hf ...   render a remotion-broll scene or a HyperFrames composition and add it as media
  nvc.py cutout JOB PICTURE...  cut the subject out for Vox beats: people halftone with a marker stroke, objects in colour
  nvc.py key JOB CLIP...        a clip shot on black (fire, smoke, sparks) or green made transparent for Vox beats
  nvc.py doctor [--setup]       what this machine has; --setup builds the Python environment and the renderer
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gemini_api  # noqa: E402
import nvc_plan as P  # noqa: E402
import pixabay_api as X  # noqa: E402

SKILL_VERSION = "2026.09.26.1"
REMOTION_VERSION = "4.0.528"
SKILL_DIR = HERE.parent
TEMPLATE = SKILL_DIR / "template"
PRESETS_FILE = HERE / "presets.json"
VENV_DIR = SKILL_DIR / ".venv"
NVC_HOME = Path(os.environ.get("NVC_HOME") or (Path.home() / ".nexa-video-creator"))
RENDERER = Path(os.environ.get("NVC_RENDERER") or (NVC_HOME / "renderer"))
BIN = NVC_HOME / "bin"
SKILLS = Path(os.environ.get("CLAUDE_SKILLS_DIR") or (Path.home() / ".claude" / "skills"))
SOUND = SKILLS / "nexa-sound" / "scripts" / "sound.py"
SPEECH = SKILLS / "nexa-speech" / "scripts" / "speech.py"
WATCH = SKILLS / "agy-watch-video" / "scripts" / "watch_video.py"
BROLL = SKILLS / "remotion-broll" / "scripts" / "broll.py"
T7 = Path("/Volumes/T7 Shield")
ROLES = ("camera", "screen", "broll", "image", "voice", "music", "dialogue", "segment", "logo")
ROLE_KIND = {"camera": "camera", "screen": "screen_recording", "broll": "broll", "image": "image", "voice": "voice",
             "music": "music", "dialogue": "audio_dialogue", "segment": "segment", "logo": "image"}
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic")
WHISPER_MODEL_NAMES = ("ggml-large-v3-turbo-q8_0.bin", "ggml-large-v3-turbo-q5_0.bin", "ggml-large-v3-turbo.bin",
                       "ggml-large-v3.bin", "ggml-medium.bin", "ggml-small.bin", "ggml-base.en.bin")


class NvcError(Exception):
    pass


def die(msg, code=1):
    print("nvc: " + str(msg), file=sys.stderr)
    sys.exit(code)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def run(cmd, cwd=None, timeout=3600, env=None, check=False, input_bytes=None):
    """Run a command (argument list, never a shell) and capture its output as text."""
    cmd = [str(c) for c in cmd]
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, timeout=timeout, env=env,
                              input=input_bytes, capture_output=True)
    except FileNotFoundError:
        raise NvcError("not installed: " + cmd[0])
    except subprocess.TimeoutExpired:
        raise NvcError("timed out after %d s: %s" % (timeout, " ".join(cmd[:3])))
    proc.stdout = proc.stdout.decode("utf-8", "replace") if isinstance(proc.stdout, bytes) else proc.stdout
    proc.stderr = proc.stderr.decode("utf-8", "replace") if isinstance(proc.stderr, bytes) else proc.stderr
    if check and proc.returncode:
        raise NvcError("%s failed: %s" % (cmd[0], (proc.stderr or proc.stdout).strip()[-900:]))
    return proc


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return default


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
        handle.write("\n")
    os.replace(tmp, path)


def slug(text, fallback="clip"):
    text = re.sub(r"[^A-Za-z0-9]+", "-", str(text)).strip("-").lower()
    return text[:40] or fallback


def emit(data, as_json):
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- presets and jobs

def presets():
    return read_json(PRESETS_FILE)


def target_preset(name):
    data = presets()
    if name not in data["targets"]:
        raise NvcError("unknown target %s; use one of %s" % (name, ", ".join(data["targets"])))
    preset = dict(data["targets"][name])
    preset["name"] = name
    return preset


def job_dir(path):
    d = Path(path).expanduser().resolve()
    if not (d / "job.json").exists():
        raise NvcError("%s is not a job folder (no job.json); start one with: nvc.py new %s" % (d, path))
    return d


def load_job(d):
    return read_json(d / "job.json")


def save_job(d, job):
    job["updated"] = now()
    write_json(d / "job.json", job)


def mark(job, step, **info):
    job.setdefault("steps", {})[step] = dict(info, at=now())


# ---------------------------------------------------------------- tools

def venv_python():
    for name in ("bin/python3", "bin/python"):
        p = VENV_DIR / name
        if p.exists():
            return str(p)
    return None


def numpy_python():
    """A Python that has numpy: the skill venv, or this interpreter when it already has numpy."""
    py = venv_python()
    if py:
        return py
    try:
        import numpy  # noqa: F401
        return sys.executable
    except ImportError:
        return None


def ffmpeg_filters():
    try:
        out = run(["ffmpeg", "-hide_banner", "-filters"], timeout=30).stdout
    except NvcError:
        return set()
    names = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 3 and re.match(r"^[TSC.|]{2,3}$", parts[0]):
            names.add(parts[1])
    return names


def whisper_model():
    env = os.environ.get("NVC_WHISPER_MODEL")
    if env and Path(env).exists():
        return env
    roots = [NVC_HOME / "models", T7 / "nexa-video-creator" / "models", Path("/opt/homebrew/share/whisper-cpp"),
             Path.home() / ".cache" / "whisper"]
    local_share = Path.home() / ".local" / "share"
    if local_share.exists():
        for child in sorted(local_share.iterdir()):
            if (child / "models").is_dir():
                roots.append(child / "models")
    for name in WHISPER_MODEL_NAMES:
        for root in roots:
            candidate = root / name
            if candidate.exists():
                return str(candidate)
    return None


def compile_swift(name):
    """Build a Swift helper once into ~/.nexa-video-creator/bin (Apple frameworks only, nothing downloaded)."""
    src = HERE / (name + ".swift")
    out = BIN / name
    if out.exists() and out.stat().st_mtime >= src.stat().st_mtime:
        return str(out)
    if not shutil.which("swiftc"):
        return None
    BIN.mkdir(parents=True, exist_ok=True)
    r = run(["swiftc", "-O", src, "-o", out], timeout=600)
    return str(out) if r.returncode == 0 and out.exists() else None


def node_version():
    try:
        out = run(["node", "--version"], timeout=20).stdout.strip()
    except NvcError:
        return None
    m = re.match(r"v(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else None


# ---------------------------------------------------------------- probing

def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path], timeout=120)
    if r.returncode:
        raise NvcError("ffprobe could not read %s: %s" % (path, r.stderr.strip()[-300:]))
    data = json.loads(r.stdout or "{}")
    streams = data.get("streams") or []
    fmt = data.get("format") or {}
    video = next((s for s in streams if s.get("codec_type") == "video"
                  and not (s.get("disposition") or {}).get("attached_pic")), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    info = {"container": fmt.get("format_name"), "duration": float(fmt.get("duration") or 0) or None,
            "size_bytes": int(fmt.get("size") or 0), "hasVideo": bool(video), "hasAudio": bool(audio),
            "tags": {k: v for k, v in (fmt.get("tags") or {}).items()
                     if k.startswith(("com.apple", "com.android", "encoder", "creation_time"))}}
    if video:
        w, h = int(video.get("width") or 0), int(video.get("height") or 0)
        rotation = 0
        for side in video.get("side_data_list") or []:
            if "rotation" in side:
                rotation = int(float(side["rotation"]))
        if rotation % 180:
            w, h = h, w

        def rate(text):
            try:
                a, b = str(text).split("/")
                return float(a) / float(b) if float(b) else 0.0
            except (ValueError, ZeroDivisionError):
                return 0.0

        r_fps, avg_fps = rate(video.get("r_frame_rate")), rate(video.get("avg_frame_rate"))
        transfer = video.get("color_transfer") or ""
        info.update({"width": w, "height": h, "rotation": rotation, "codec": video.get("codec_name"),
                     "pix_fmt": video.get("pix_fmt"), "fps": round(avg_fps or r_fps, 3), "r_fps": round(r_fps, 3),
                     "vfr": bool(r_fps and avg_fps and abs(r_fps - avg_fps) / r_fps > 0.01),
                     "color": {"space": video.get("color_space"), "primaries": video.get("color_primaries"),
                               "transfer": transfer},
                     "hdr": transfer in ("arib-std-b67", "smpte2084"),
                     "alpha": ((video.get("tags") or {}).get("alpha_mode") == "1"
                               or (video.get("tags") or {}).get("ALPHA_MODE") == "1"
                               or "a" in str(video.get("pix_fmt") or "").replace("yuva", "a").split("p")[0][-1:])})
        if not info.get("duration") and video.get("duration"):
            info["duration"] = float(video["duration"])
    if audio:
        info.update({"audioCodec": audio.get("codec_name"), "sampleRate": int(audio.get("sample_rate") or 0),
                     "channels": int(audio.get("channels") or 0)})
    return info


def classify(path, info, role=None):
    """What a file is. A role given by the user wins; otherwise file facts and a few cheap rules decide, with the
    evidence kept so the editor can see why."""
    if role:
        return ROLE_KIND.get(role, role), {"by": "role"}
    ext = Path(path).suffix.lower()
    name = Path(path).name.lower()
    if ext in IMAGE_EXT:
        return "image", {"by": "extension"}
    if not info.get("hasVideo"):
        return ("audio_dialogue" if info.get("duration", 0) > 15 else "sfx"), {"by": "audio only"}
    ev = {"by": "rules", "fps": info.get("fps"), "size": [info.get("width"), info.get("height")]}
    if re.search(r"screen ?record|screenshot|obs|loom|cap[-_ ]|capture|screencast|desktop", name):
        return "screen_recording", dict(ev, name="looks like a screen recorder's file name")
    if any(k.startswith("com.apple.quicktime.make") or k.startswith("com.android") for k in info.get("tags", {})):
        return "camera", dict(ev, tags="phone or camera maker tags")
    w, h = info.get("width") or 0, info.get("height") or 0
    if (w, h) in ((2880, 1800), (2560, 1600), (3024, 1964), (3456, 2234), (1440, 900), (1680, 1050), (2560, 1440)):
        return "screen_recording", dict(ev, size_hint="a Mac display size")
    return "camera", dict(ev, note="no screen signs; treated as camera footage (use --role to change)")


# ---------------------------------------------------------------- new, add

def cmd_new(args):
    d = Path(args.job).expanduser().resolve()
    if (d / "job.json").exists():
        raise NvcError("%s already has a job; use it, or pick another folder" % d)
    target_preset(args.target)
    for sub in ("media/originals", "media/proxies", "media/audio", "analysis", "out", "final", "audio"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    job = {"schema": "nvc-job/1", "skill_version": SKILL_VERSION, "id": slug(args.id or d.name, "job"),
           "title": args.title or d.name, "target": args.target, "targets": [args.target],
           "language": args.lang, "fps": args.fps or target_preset(args.target).get("fps") or 30,
           "created": now(), "sources": {}, "dialogue": None, "steps": {}}
    if args.brand:
        job["theme"] = read_json(args.brand, {}) if str(args.brand).endswith(".json") else {"accent": args.brand}
    save_job(d, job)
    note = ""
    if not str(d).startswith(str(T7)) and T7.exists():
        note = " (the T7 is mounted: long footage and renders are better kept there)"
    print("job %s at %s, target %s%s" % (job["id"], d, args.target, note))
    print("next: nvc.py add %s FILE... --role camera|screen|broll|image|voice|music" % args.job)


def cmd_add(args):
    d = job_dir(args.job)
    job = load_job(d)
    added = []
    for f in args.files:
        src = Path(f).expanduser().resolve()
        if not src.exists():
            raise NvcError("no such file: %s" % src)
        base = slug(args.id if (args.id and len(args.files) == 1) else src.stem, "clip")
        sid, n = base, 2
        while sid in job["sources"] and job["sources"][sid].get("original") != str(src):
            sid, n = "%s%d" % (base, n), n + 1
        link = d / "media" / "originals" / (sid + src.suffix.lower())
        if link.is_symlink() or link.exists():
            if link.resolve() != src:
                raise NvcError("%s already links to another file" % link)
        else:
            os.symlink(src, link)
        info = probe(src) if src.suffix.lower() not in IMAGE_EXT else probe_image(src)
        kind, evidence = classify(src, info, args.role)
        job["sources"][sid] = {"id": sid, "role": args.role, "kind": kind, "original": str(src),
                               "link": str(link.relative_to(d)), "probe": info, "evidence": evidence,
                               "duration": info.get("duration"), "width": info.get("width"),
                               "height": info.get("height"), "hasAudio": info.get("hasAudio", False),
                               "hasVideo": info.get("hasVideo", False), "alpha": info.get("alpha", False)}
        if args.role == "dialogue" or (args.role == "voice" and not job.get("dialogue")):
            job["dialogue"] = sid
        if args.role == "voice":
            imported = import_speech_words(d, src, sid, job.get("language"))
            if imported:
                added.append("%d words imported from nexa-speech" % imported)
        added.append("%s (%s, %s)" % (sid, kind, fmt_dur(info.get("duration"))))
    save_job(d, job)
    print("added: " + "; ".join(added))
    print("next: nvc.py ingest %s" % args.job)


def import_speech_words(d, vo_path, sid, job_language=None):
    """A nexa-speech voice-over comes with its own word timings (words.json next to vo_48k.wav): use them as the
    transcript, so a faceless edit needs no transcription. The language is the main voice profile's (the manifest
    keeps it per profile, "bn-BD"), else the job's."""
    words_file = vo_path.parent / "words.json"
    data = read_json(words_file)
    if not isinstance(data, list) or not data or "start" not in data[0]:
        return 0
    words = []
    for i, w in enumerate(data):
        text = str(w.get("w") or w.get("text") or "").strip()
        if text:
            words.append({"id": "w%04d" % (len(words) + 1), "text": text, "start": round(float(w["start"]), 3),
                          "end": round(float(w["end"]), 3)})
    manifest = read_json(vo_path.parent / "vo.manifest.json") or {}
    profile = (manifest.get("profiles") or {}).get(manifest.get("main_profile")) or {}
    lang = str(manifest.get("language") or profile.get("language") or job_language or "en").split("-")[0].lower()
    write_json(d / "analysis" / "words.json", {"schema": "nvc-words/1", "source": sid,
                                               "language": lang,
                                               "engine": "nexa-speech", "snapping": "script timings from nexa-speech",
                                               "created": now(), "words": words})
    (d / "analysis" / "transcript.txt").write_text("\n".join(P.pack_transcript(words)) + "\n", encoding="utf-8")
    return len(words)


def probe_image(path):
    info = {"hasVideo": False, "hasAudio": False, "duration": None, "image": True}
    try:
        r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                 "-of", "json", path], timeout=60)
        s = (json.loads(r.stdout or "{}").get("streams") or [{}])[0]
        info.update({"width": s.get("width"), "height": s.get("height")})
    except (NvcError, ValueError):
        pass
    return info


def fmt_dur(sec):
    if not sec:
        return "still"
    sec = float(sec)
    return "%d:%04.1f" % (sec // 60, sec % 60)


# ---------------------------------------------------------------- ingest

def proxy_size(src, preset, kind):
    """Scale a source down only as far as the output still has headroom: 2x for screen recordings (zooms), 1.25x
    for cameras (punch-ins). A landscape camera in a vertical edit keeps its full height for the crop."""
    w, h = src.get("width") or 0, src.get("height") or 0
    if not w or not h:
        return None
    k = max(preset["width"] / float(w), preset["height"] / float(h))
    factor = 2.0 if kind in P.SCREEN_KINDS else 1.25
    scale = min(1.0, k * factor)
    if scale >= 0.98:
        return None
    nw, nh = int(round(w * scale / 2) * 2), int(round(h * scale / 2) * 2)
    return nw, nh


def make_proxy(d, src, preset, fps, force=False):
    out = d / "media" / "proxies" / (src["id"] + ".mp4")
    if out.exists() and not force:
        return out
    info = src["probe"]
    vf = ["fps=%s" % fps]
    size = proxy_size(src, preset, src["kind"])
    if size:
        vf.append("scale=%d:%d:flags=lanczos" % size)
    vf.append("scale=out_color_matrix=bt709:out_range=tv")
    vf.append("setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv")
    vf.append("format=yuv420p")
    cmd = ["ffmpeg", "-y", "-v", "error", "-nostdin", "-i", d / src["link"], "-map", "0:v:0"]
    if src.get("hasAudio"):
        cmd += ["-map", "0:a:0"]
    cmd += ["-vf", ",".join(vf), "-fps_mode", "cfr", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
            "-g", str(int(fps)), "-bf", "2", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"]
    if src.get("hasAudio"):
        cmd += ["-af", "aresample=48000:async=1:first_pts=0", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-movflags", "+faststart", out]
    t0 = time.time()
    run(cmd, timeout=6 * 3600, check=True)
    src["proxy_seconds"] = round(time.time() - t0, 1)
    if info.get("hdr"):
        src.setdefault("notes", []).append("HDR source: the proxy is not tone-mapped, colours may look flat. "
                                           "Ask for SDR recordings, or tone-map with Remotion's ffmpeg (research 02)")
    return out


def extract_audio(d, src, force=False):
    out = d / "media" / "audio" / (src["id"] + ".wav")
    if out.exists() and not force:
        return out
    run(["ffmpeg", "-y", "-v", "error", "-nostdin", "-i", d / src["link"], "-map", "0:a:0", "-ac", "1", "-ar",
         "48000", "-c:a", "pcm_s24le", out], timeout=3600, check=True)
    return out


def dsp(cmd, *files):
    py = numpy_python()
    if not py:
        raise NvcError("numpy is missing: run `nvc.py doctor --setup` once (it builds the skill's Python environment)")
    r = run([py, HERE / "nvc_dsp.py", cmd] + list(files), timeout=3600)
    if r.returncode:
        raise NvcError("nvc_dsp %s failed: %s" % (cmd, r.stderr.strip()[-600:]))
    return json.loads(r.stdout or "null")


def face_position(d, src):
    """Median face centre from Apple Vision samples (2 a second), or the frame centre."""
    tool = compile_swift("facetrack")
    if not tool:
        return None
    out = d / "analysis" / (src["id"] + ".faces.json")
    r = run([tool, d / "media" / "proxies" / (src["id"] + ".mp4"), "2"], timeout=1800)
    if r.returncode:
        return None
    data = json.loads(r.stdout or "{}")
    write_json(out, data)
    xs, ys, sizes = [], [], []
    for sample in data.get("samples") or []:
        faces = sample.get("faces") or []
        if faces:
            f = max(faces, key=lambda b: b["w"] * b["h"])
            xs.append(f["x"] + f["w"] / 2)
            ys.append(f["y"] + f["h"] / 2)
            sizes.append(f["w"] * f["h"])
    if not xs:
        return {"x": 0.5, "y": 0.42, "found": 0, "track": str(out.relative_to(d))}
    xs.sort()
    ys.sort()
    share = len(xs) / max(1, len(data.get("samples") or []))
    return {"x": round(xs[len(xs) // 2], 3), "y": round(ys[len(ys) // 2], 3), "found": round(share, 2),
            "area": round(sorted(sizes)[len(sizes) // 2], 4), "track": str(out.relative_to(d))}


def cmd_ingest(args):
    d = job_dir(args.job)
    job = load_job(d)
    preset = target_preset(job["target"])
    fps = job.get("fps") or 30
    if not job["sources"]:
        raise NvcError("no media yet: nvc.py add %s FILE..." % args.job)
    t0 = time.time()
    rows = []
    for sid, src in job["sources"].items():
        kind = src["kind"]
        if src.get("probe", {}).get("image") or kind == "image":
            src["image"] = src["link"]
            rows.append("%s: image %sx%s" % (sid, src.get("width"), src.get("height")))
            continue
        if src.get("hasVideo"):
            if src.get("alpha") and src["link"].endswith((".webm", ".mov")):
                src["proxy"] = src["link"]
                rows.append("%s: %s with alpha, used as it is" % (sid, kind))
            else:
                make_proxy(d, src, preset, fps, force=args.force)
                src["proxy"] = "media/proxies/%s.mp4" % sid
                vfr = " (VFR fixed to %d fps)" % fps if src["probe"].get("vfr") else ""
                rows.append("%s: %s %sx%s %s%s" % (sid, kind, src.get("width"), src.get("height"),
                                                    fmt_dur(src.get("duration")), vfr))
        if src.get("hasAudio"):
            extract_audio(d, src, force=args.force)
            src["audio"] = "media/audio/%s.wav" % sid
        if kind in P.CAMERA_KINDS and src.get("hasVideo") and not args.no_faces:
            face = face_position(d, src)
            if face:
                src["face"] = face
    speakers = [sid for sid, s in job["sources"].items() if s.get("audio") and s["kind"] not in ("music", "sfx")]
    music = [sid for sid, s in job["sources"].items() if s.get("audio") and s["kind"] == "music"]
    if job.get("dialogue") and job["dialogue"] in job["sources"]:
        reason = ("set by role" if job["sources"][job["dialogue"]].get("role") in ("dialogue", "voice")
                  else "kept from the last ingest")
    elif not speakers and music:
        job["dialogue"] = music[0]
        reason = "no speech: the music track is the master clock (time the segments and overlays in seconds)"
    elif speakers:
        scores = {}
        for sid in speakers:
            lv = dsp("levels", d / job["sources"][sid]["audio"]) if numpy_python() else {}
            job["sources"][sid]["levels"] = lv
            if lv and lv.get("snr_db") is not None:
                scores[sid] = lv["snr_db"] + 30 * lv.get("hf_share", 0) - min(20, lv.get("clipped", 0) / 50.0) \
                    + (10 if lv.get("speech_share", 0) > 0.2 else -20)
            else:
                scores[sid] = 0
        job["dialogue"] = max(scores, key=lambda k: scores[k])
        reason = "best microphone by measured SNR and bandwidth: " + ", ".join(
            "%s %.1f" % (k, v) for k, v in sorted(scores.items(), key=lambda kv: -kv[1]))
    else:
        reason = "no source has sound"
    mark(job, "ingest", seconds=round(time.time() - t0, 1), dialogue=job.get("dialogue"), reason=reason)
    save_job(d, job)
    for row in rows:
        print(row)
    print("dialogue (master clock): %s (%s)" % (job.get("dialogue"), reason))
    others = [s for s in speakers if s != job.get("dialogue")]
    step = "sync" if others else ("brief" if (d / "analysis" / "words.json").exists() else "transcribe")
    print("next: nvc.py %s %s" % (step, args.job))


# ---------------------------------------------------------------- sync

def cmd_sync(args):
    d = job_dir(args.job)
    job = load_job(d)
    master = job.get("dialogue")
    if not master:
        raise NvcError("no dialogue source yet: run nvc.py ingest first")
    manual = {}
    for item in args.set or []:
        key, _, value = item.partition("=")
        manual[key.strip()] = float(value)
    results = {}
    for sid, src in job["sources"].items():
        if sid == master or src["kind"] in ("image", "music", "sfx", "segment", "broll"):
            continue
        if sid in manual:
            src["sync"] = {"reference": master, "offset_s": manual[sid], "drift_ppm": None, "confidence": "manual",
                           "segments": [{"t_ref_from": 0, "t_ref_to": 1e12, "offset_s": manual[sid],
                                         "drift_ppm": None}]}
            results[sid] = "manual offset %+.3f s" % manual[sid]
            continue
        if not src.get("audio"):
            results[sid] = "no sound to sync by: give the offset with --set %s=SECONDS" % sid
            continue
        py = numpy_python()
        if not py:
            raise NvcError("numpy is missing: run `nvc.py doctor --setup` once")
        t0 = time.time()
        r = run([py, HERE / "nvc_sync.py", d / job["sources"][master]["audio"], d / src["audio"], "--json"],
                timeout=3600)
        if r.returncode not in (0, 3):
            raise NvcError("sync failed for %s: %s" % (sid, r.stderr.strip()[-500:]))
        res = json.loads(r.stdout)
        res.pop("windows", None)
        res["reference"] = master
        res["seconds"] = round(time.time() - t0, 2)
        src["sync"] = res
        steps = (", %d steps" % len(res["steps"])) if res.get("steps") else ""
        drift = (", drift %+.1f ppm" % res["drift_ppm"]) if res.get("drift_ppm") is not None else ""
        results[sid] = "%+.4f s%s%s, confidence %s (%.1f s)" % (res["offset_s"], drift, steps, res["confidence"],
                                                                 res["seconds"])
        if res["confidence"] == "low":
            results[sid] += ": these may not be the same event; check, or set it by hand with --set"
    mark(job, "sync", results=results)
    save_job(d, job)
    for sid, text in results.items():
        print("%s against %s: %s" % (sid, master, text))
    print("next: nvc.py clean %s (optional), then nvc.py transcribe %s" % (args.job, args.job))


# ---------------------------------------------------------------- clean

def cmd_clean(args):
    d = job_dir(args.job)
    job = load_job(d)
    master = job.get("dialogue")
    if not master:
        raise NvcError("no dialogue source yet: run nvc.py ingest first")
    if not SOUND.exists():
        raise NvcError("nexa-sound is not installed (%s); the edit works without clean-up" % SOUND)
    src = job["sources"][master]
    out = d / "media" / "audio" / (master + ".clean.wav")
    cmd = [sys.executable, SOUND, "clean", d / src["audio"], "--out", out, "--json"]
    if args.isolate:
        cmd.append("--isolate")
    if args.hum:
        cmd += ["--hum", str(args.hum)]
    r = run(cmd, timeout=3600)
    if r.returncode:
        raise NvcError("clean-up failed: " + (r.stderr or r.stdout).strip()[-600:])
    info = json.loads(r.stdout or "{}")
    job["dialogue_clean"] = str(out.relative_to(d))
    mark(job, "clean", report=info)
    save_job(d, job)
    print("clean dialogue: %s" % out)
    print("next: nvc.py transcribe %s" % args.job)


# ---------------------------------------------------------------- transcription

def dialogue_audio(d, job):
    rel = job.get("dialogue_clean") or job["sources"][job["dialogue"]].get("audio")
    if not rel:
        raise NvcError("the dialogue source has no audio file: run nvc.py ingest")
    return d / rel


DTW_PRESETS = (("large-v3-turbo", "large.v3.turbo"), ("large-v3", "large.v3"), ("large-v2", "large.v2"),
               ("large-v1", "large.v1"), ("medium.en", "medium.en"), ("medium", "medium"), ("small.en", "small.en"),
               ("small", "small"), ("base.en", "base.en"), ("base", "base"), ("tiny.en", "tiny.en"), ("tiny", "tiny"))


WHISPER_TOKEN_P = []   # the token probabilities of the last whisper run, for whisper_doubt()


def pick_transcriber(lang, has_key, whisper_ready):
    """The auto engine, by the house rule (2026-09-26): Gemini 3.5 Transcribe for every language but English (on a
    22 s Bangla voice-over whisper garbled correct words all through and a real slip was lost among its errors;
    Gemini's clean transcript showed it); English starts on whisper when it is installed and moves to Gemini when
    the result looks unsure (whisper_doubt). agy (Gemini through agy-watch-video) when there is no key."""
    if (lang or "").lower().startswith("en") and whisper_ready:
        return "whisper"
    return "gemini" if has_key else "agy"


def whisper_doubt(words, probs):
    """Why an English whisper transcript should not be trusted, or None. The house rule (2026-09-26): transcripts come
    from Gemini 3.5 Transcribe for every language but English; English may use whisper, and moves to Gemini as soon as
    the whisper result looks unsure. Signals: low token confidence, a phrase repeated in a loop (whisper's
    hallucination on music and silence), and letters outside the Latin script in an English transcript."""
    if not words:
        return "no words"
    if probs:
        mean_p = sum(probs) / len(probs)
        low = sum(1 for x in probs if x < 0.5) / len(probs)
        if mean_p < 0.70:
            return "low confidence (mean token probability %.2f)" % mean_p
        if low > 0.15:
            return "low confidence (%d%% of tokens under 0.5)" % round(low * 100)
    texts = [re.sub(r"[^\w']+", "", w["text"].lower()) for w in words]
    for n in (3, 4, 5, 6):
        for i in range(0, max(0, len(texts) - 3 * n + 1)):
            gram = texts[i:i + n]
            if all(gram) and texts[i + n:i + 2 * n] == gram and texts[i + 2 * n:i + 3 * n] == gram:
                return "a phrase repeated in a loop (%s)" % " ".join(gram)
    letters = "".join(w["text"] for w in words)
    alpha = [ch for ch in letters if ch.isalpha()]
    foreign = [ch for ch in alpha if not ("a" <= ch.lower() <= "z")]
    if alpha and len(foreign) / len(alpha) > 0.02:
        return "letters outside the Latin script in an English transcript"
    return None


def whisper_words(wav16, lang, model, tmpdir):
    """Words from whisper.cpp tokens. With a known model, DTW token times are used (-dtw, and -nfa because flash
    attention silently turns DTW off in whisper.cpp 1.8). Measured on the test pair (2026-09-25): the plain segment
    offsets put a word 1.5 s late, inside a pause; the DTW times matched the measured speech."""
    out_base = tmpdir / "whisper"
    del WHISPER_TOKEN_P[:]
    cmd = ["whisper-cli", "-m", model, "-f", wav16, "-ojf", "-of", out_base, "-nfa", "-np",
           "-t", str(max(4, (os.cpu_count() or 8) // 2))]
    name = Path(model).name
    preset = next((p for key, p in DTW_PRESETS if key in name), None)
    if preset:
        cmd += ["-dtw", preset]
    if lang and lang != "auto":
        cmd += ["-l", lang.split("-")[0]]
    r = run(cmd, timeout=6 * 3600)
    if r.returncode:
        raise NvcError("whisper-cli failed: " + r.stderr.strip()[-600:])
    data = json.loads((tmpdir / "whisper.json").read_bytes().decode("latin-1"))
    raw = []
    for seg in data.get("transcription") or []:
        for tok in seg.get("tokens") or []:
            text = tok.get("text", "")
            if not text or text.startswith("[_") or text.startswith("<|"):
                continue
            t_dtw = tok.get("t_dtw", -1)
            t = t_dtw / 100.0 if isinstance(t_dtw, (int, float)) and t_dtw >= 0 else tok["offsets"]["from"] / 1000.0
            raw.append((text.encode("latin-1"), t, tok["offsets"]["to"] / 1000.0))
            if isinstance(tok.get("p"), (int, float)):
                WHISPER_TOKEN_P.append(float(tok["p"]))
    words, cur = [], None
    for data_bytes, t, t_end in raw:
        if cur is None or data_bytes[:1] == b" ":
            if cur:
                words.append(cur)
            cur = {"bytes": [data_bytes], "start": t, "last": t, "end_off": t_end}
        else:
            cur["bytes"].append(data_bytes)
            cur["last"] = t
            cur["end_off"] = t_end
    if cur:
        words.append(cur)
    out = []
    for k, w in enumerate(words):
        text = b"".join(w["bytes"]).decode("utf-8", "replace").strip()
        if not text:
            continue
        nxt = words[k + 1]["start"] if k + 1 < len(words) else None
        guess = max(0.25, 0.065 * len(text))
        end = max(w["last"] + 0.1, w["start"] + guess) if preset else w["end_off"]
        if nxt is not None:
            end = min(end, nxt)
        out.append({"text": text, "start": round(w["start"], 3), "end": round(max(end, w["start"] + 0.05), 3)})
    return out


def agy_sentences(path, lang):
    if not WATCH.exists():
        raise NvcError("agy-watch-video is not installed")
    cmd = [sys.executable, WATCH, "transcribe", path, "--json"]
    if lang and lang != "auto":
        cmd += ["--lang", lang.split("-")[0]]
    r = run(cmd, timeout=6 * 3600)
    if r.returncode:
        raise NvcError("agy transcribe failed: " + (r.stderr or r.stdout).strip()[-600:])
    data = json.loads(r.stdout or "{}")
    return data.get("segments") or data.get("sentences") or []


def spread_words(sentences):
    """Sentence timings to word timings: each word gets a share of its sentence by visible characters."""
    words = []
    for s in sentences:
        text = str(s.get("text") or "").strip()
        start = float(s.get("start") or 0)
        end = float(s.get("end") or (start + max(1.0, len(text) / 15.0)))
        toks = [t for t in text.split() if t]
        if not toks:
            continue
        weights = [max(1, P.graphemes(t)) for t in toks]
        total = float(sum(weights))
        t = start
        for tok, wgt in zip(toks, weights):
            dur = (end - start) * wgt / total
            words.append({"text": tok, "start": round(t, 3), "end": round(t + dur * 0.92, 3)})
            t += dur
    return words


BN_DIGIT_MAP = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bangla_digits(words):
    """Counts, prices and times in Bengali digits inside Bangla speech, as the house rule for Bangla copy asks:
    Gemini writes "10" and "500" where the speaker said দশ and পাঁচশো. A number after a Latin word stays in Latin
    digits (a model name such as iPhone 15), and so does one with no Bangla word beside it."""
    def bangla(i):
        return 0 <= i < len(words) and re.search(r"[ঀ-৿]", words[i]["text"] or "")

    def latin(i):
        return 0 <= i < len(words) and re.search(r"[A-Za-z]", words[i]["text"] or "")

    out = []
    for i, w in enumerate(words):
        text = w["text"] or ""
        if (re.search(r"[0-9]", text) and not re.search(r"[A-Za-z]", text) and not latin(i - 1)
                and (bangla(i - 1) or bangla(i + 1))):
            w = dict(w, text=text.translate(BN_DIGIT_MAP))
        out.append(w)
    return out


def cmd_transcribe(args):
    d = job_dir(args.job)
    job = load_job(d)
    if not job.get("dialogue"):
        raise NvcError("no dialogue source yet: run nvc.py ingest first")
    lang = args.lang or job.get("language") or "en"
    engine = args.engine
    has_key = bool(gemini_api.key_sources())
    model = args.model or whisper_model()
    bn = lang.startswith("bn")
    doubt = None
    if engine == "auto":
        engine = pick_transcriber(lang, has_key, bool(model and shutil.which("whisper-cli")))
    audio = dialogue_audio(d, job)
    tmp = d / "analysis" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    wav16 = tmp / "dialogue16k.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav16],
        timeout=3600, check=True)
    t0 = time.time()
    cost = 0.0
    if engine == "whisper":
        if not model:
            raise NvcError("no whisper model found: set NVC_WHISPER_MODEL to a ggml-large-v3-turbo file (see "
                           "`nvc.py doctor`), or use --engine gemini")
        raw_words = whisper_words(wav16, lang, model, tmp)
        doubt = whisper_doubt(raw_words, list(WHISPER_TOKEN_P))
        if doubt and args.engine == "auto" and has_key:
            log("whisper looked unsure (%s): transcribing with Gemini 3.5 Transcribe instead" % doubt)
            engine = "gemini"
        elif doubt:
            log("whisper looked unsure (%s); run with --engine gemini to check it" % doubt)
    if engine == "gemini":
        minutes = (job["sources"][job["dialogue"]].get("duration") or 0) / 60.0
        cost = round(minutes * 0.005, 3)
        log("Gemini 3.5 Transcribe: about $%.3f for %.1f min" % (cost, minutes))
        mp3 = tmp / "dialogue.mp3"
        run(["ffmpeg", "-y", "-v", "error", "-i", wav16, "-c:a", "libmp3lame", "-b:a", "64k", mp3], timeout=3600,
            check=True)
        try:
            codes = [{"bn": "bn-BD", "en": "en-US"}.get(lang, lang)] if lang not in ("auto", "mixed") else None
            res = gemini_api.transcribe(str(mp3), language_codes=codes, words=True)
        except gemini_api.GeminiError as err:
            raise NvcError("Gemini transcription failed (%s): %s" % (err.kind, err))
        raw_words = [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in res["words"]
                     if w.get("start") is not None]
        if not raw_words and res.get("text"):
            raise NvcError("Gemini returned text without word timings; try --engine agy or whisper")
        append_ledger(d, {"command": "transcribe", "model": "gemini-3.5-transcribe", "minutes": round(minutes, 2),
                          "est_usd": cost, "key": res["info"].get("key")})
    elif engine == "agy":
        raw_words = spread_words(agy_sentences(str(audio), lang))
    elif engine != "whisper":
        raise NvcError("unknown engine " + engine)
    if not raw_words:
        raise NvcError("no words came back: is there speech in %s?" % audio)
    raw_words.sort(key=lambda w: w["start"])
    if bn:
        raw_words = bangla_digits(raw_words)
    snapped = raw_words
    note = "edges from the engine"
    if numpy_python():
        tmpw = tmp / "raw_words.json"
        write_json(tmpw, raw_words)
        try:
            snapped = dsp("snap", audio, tmpw)
            note = "edges snapped to measured speech"
        except NvcError as err:
            note = "edges from the engine (snapping failed: %s)" % err
    words = []
    for i, w in enumerate(snapped):
        item = {"id": "w%04d" % (i + 1), "text": w["text"], "start": round(float(w["start"]), 3),
                "end": round(float(w["end"]), 3)}
        if w.get("pause_after") is not None:
            item["pause_after"] = w["pause_after"]
        words.append(item)
    data = {"schema": "nvc-words/1", "source": job["dialogue"], "language": lang, "engine": engine,
            "snapping": note, "created": now(), "words": words}
    if doubt:
        data["whisper_doubt"] = doubt
    write_json(d / "analysis" / "words.json", data)
    (d / "analysis" / "transcript.txt").write_text("\n".join(P.pack_transcript(words)) + "\n", encoding="utf-8")
    mark(job, "transcribe", engine=engine, words=len(words), seconds=round(time.time() - t0, 1), est_usd=cost)
    save_job(d, job)
    print("%d words (%s, %s) in %.1f s" % (len(words), engine, note, time.time() - t0))
    print("next: nvc.py brief %s" % args.job)


def append_ledger(d, entry):
    entry = dict(entry, time=now())
    with open(d / "ledger.jsonl", "a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_words(d):
    data = read_json(d / "analysis" / "words.json")
    if not data:
        raise NvcError("no transcript yet: run nvc.py transcribe (or import words with --words)")
    return data["words"], data


# ---------------------------------------------------------------- brief

BRIEF_EXAMPLE = {
    "schema": "nvc-plan/1", "target": "youtube", "title": "How I sync a screen recording with my camera",
    "segments": [
        {"words": ["w0001", "w0012"], "quote": "<the exact words of w0001..w0012>", "beat": "hook",
         "layout": "camFull"},
        {"words": ["w0013", "w0090"], "quote": "<exact words>", "beat": "step 1", "layout": "screenPip",
         "pip": {"corner": "br", "shape": "circle"}}],
    "remove": [{"words": ["w0031", "w0036"], "quote": "<the restart to drop>", "kind": "retake"}],
    "overlays": [
        {"type": "hook", "at": "start", "props": {"text": "Sync in 10 seconds"}},
        {"type": "stat", "words": ["w0040", "w0047"], "quote": "<words that say the number>",
         "props": {"value": "62%", "label": "leave in the first 3 seconds", "source": "YouTube Analytics"}},
        {"type": "broll", "words": ["w0050", "w0053"], "quote": "<words>", "source": "broll1", "in": 2.0},
        {"type": "cta", "at": "end", "seconds": 4, "props": {"text": "Subscribe for part 2"}}],
    "zooms": [{"words": ["w0060", "w0064"], "quote": "<words>", "layer": "screen", "x": 0.72, "y": 0.18,
               "scale": 1.8}],
    "chapters": [{"words": ["w0001", "w0004"], "quote": "<words>", "title": "Why it drifts"}],
    "captions": {"style": "word", "emphasis": ["w0044"]},
    "music": {"source": "music1"},
    "sfx": [{"at": "word:w0044", "name": "impact"}],
}


def cmd_brief(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    preset = target_preset(target)
    words, meta = load_words(d)
    lang = meta.get("language") or job.get("language")
    fillers = P.find_fillers(words)
    retakes = P.find_retakes(words)
    numbers = P.find_numbers(words)
    speech_s = sum(w["end"] - w["start"] for w in words)
    long_pauses = [(words[i]["id"], words[i]["end"], words[i + 1]["start"] - words[i]["end"])
                   for i in range(len(words) - 1) if words[i + 1]["start"] - words[i]["end"] >= 1.0]
    lines = ["# Edit brief: %s" % job.get("title"), "",
             "Job `%s`, target **%s** (%dx%d, %d fps). Language: %s. Transcript: %d words, %s of speech, engine %s "
             "(%s)." % (job["id"], preset["label"], preset["width"], preset["height"], job.get("fps") or 30, lang,
                        len(words), fmt_dur(speech_s), meta.get("engine"), meta.get("snapping")), "",
             "## Material", ""]
    for sid, s in job["sources"].items():
        bits = [s["kind"], fmt_dur(s.get("duration"))]
        if s.get("width"):
            bits.append("%sx%s" % (s.get("width"), s.get("height")))
        if sid == job.get("dialogue"):
            bits.append("DIALOGUE (master clock)")
        if s.get("sync"):
            bits.append("synced %+.3f s (%s)" % (s["sync"].get("offset_s", 0), s["sync"].get("confidence")))
        if s.get("face"):
            bits.append("face at x %.2f y %.2f" % (s["face"]["x"], s["face"]["y"]))
        lines.append("- `%s`: %s" % (sid, ", ".join(str(b) for b in bits)))
    cap = preset.get("captions") or {}
    sil = preset.get("silence") or {}
    lines += ["", "## Rules for this target", "",
              "- Hook: frame 0 shows the subject and the first word starts by %.1f s (open on the strongest line, not a "
              "greeting); say or show the promise by %.0f s; a text hook of 3 to 7 words from frame 0 "
              "(`\"at\": \"start\"`) holds at least 0.35 s a word plus 0.5 s." % (preset["hook"]["first_word_s"],
                                                                                 preset["hook"]["promise_s"]),
              "- Pauses over %d ms are trimmed to %d ms automatically; keep a deliberate pause after a punchline with "
              "`holds`. Filled pauses (um, uh, উম) bounded by silence are cut automatically."
              % (sil.get("trim_above_ms", 550), sil.get("target_ms", 300)),
              "- Pacing: something on screen changes every %.1f to %.1f s (median); nothing static for over %.0f s "
              "(punch-in, layout change, b-roll, graphic, zoom)." % (preset["pacing"]["median_gap_s"][0],
                                                                     preset["pacing"]["median_gap_s"][1],
                                                                     preset["pacing"]["max_static_s"]),
              "- Captions: %s style%s. Emphasise one word per phrase at most (`captions.emphasis`)."
              % (cap.get("style"), "" if cap.get("burn") else " as a subtitle file (set captions.burn to burn in)"),
              "- B-roll 1.5 to 6 s, starting on the word it shows; stay on the face for emotion and credibility.",
              "- Every number on screen must be in the grounded quote (else it is flagged for review); every line "
              "on screen goes through natural-text first.",
              "- Layouts: camFull, screenFull, screenPip, split, stack (9:16), brollFull, voiceOnly. Vertical "
              "targets turn screenPip and split into stack.",
              "- Overlays: hook{text}, keyword{text}, stat{value,label,source?}, list{items[],title?}, "
              "compare{left,right,title?}, quote{text,by?}, chapter{title}, lowerThird{name,role?}, "
              "callout{label?}+box, redact+box, broll|image|segment+source(+in), cta{text,sub?}, label{text,corner?}.",
              "- Designed full-frame scenes (references/plan.md, Scenes): kinetic{text|lines,highlight?}, "
              "step{n,title}, bigStat{value,label?,title?,series?}, bars{rows[{label,value,text?}],title?,note?}, "
              "versus{left,right}, recap{items[]}, endCard{text,button?}, photo+source{label?}. Over a camera the "
              "speaker stays in a round picture. A faceless video is carried by them: a scene every 3 to 8 s.",
              "- Transitions (into a segment): cut (default), zoom, whip, dip, flash, slide, sweep. Use them "
              "sparingly; scenes come in with their own (enter: slide, slideUp, sweep, pop, fade, cut).",
              ""]
    if preset["width"] > preset["height"]:
        lines[-1:-1] = [
            "- Long-form: chapters (00:00 first, 3 or more, each 10 s or longer, one per step in tutorials); re-engage "
            "near 3:00 and 6:00; never signal the end before the payoff; a clean pause where a mid-roll can go in "
            "videos of 8 minutes or more; keep the last 5 to 20 s free for end-screen elements."]
    else:
        lines[-1:-1] = [
            "- Short-form: one idea, 20 to 60 s; a re-hook near the middle; end on a loop into the first frame or a "
            "call to action of 2 s or less; text and captions inside the safe zone (x %d to %d, y %d to %d)."
            % (preset["safe"]["x"], preset["safe"]["x"] + preset["safe"]["w"], preset["safe"]["y"],
               preset["safe"]["y"] + preset["safe"]["h"])]
    if max(0, len(fillers)):
        lines += ["## Found automatically", ""]
        fp = [f for f in fillers if f["kind"] == "filled_pause"]
        dm = [f for f in fillers if f["kind"] == "discourse_marker"]
        if fp:
            lines.append("- Filled pauses: " + ", ".join("%s \"%s\" %.2f s%s" % (f["id"], f["text"], f["t"],
                                                                                 "" if f["bounded"] else " (inside a phrase: cut by hand if needed)")
                                                         for f in fp[:60]))
        if dm:
            lines.append("- Discourse markers (keep unless empty): " + ", ".join("%s \"%s\"" % (f["id"], f["text"])
                                                                                 for f in dm[:60]))
    if retakes:
        lines.append("- Possible retakes (keep one): " + "; ".join(
            "\"%s\" at %s (%.1f s) and %s (%.1f s)" % (r["phrase"], r["first"], r["t_first"], r["again"], r["t_again"])
            for r in retakes[:30]))
    if numbers:
        lines.append("- Numbers said (stat card candidates): " + ", ".join("%s \"%s\"" % (n["id"], n["text"])
                                                                           for n in numbers[:40]))
    if long_pauses:
        lines.append("- Pauses of 1 s or more: " + ", ".join("after %s at %.1f s (%.1f s)" % (i, t, g)
                                                             for i, t, g in long_pauses[:40]))
    if SOUND.exists():
        lines.append("- Sound effects (nexa-sound): whoosh, whoosh-short, swipe, swoosh-down, pop, bubble, click, "
                     "tick, key, typing, ding, chime, notify, success, error, riser, downlifter, impact, boom, "
                     "sub-drop, glitch, shutter, sparkle.")
    style = args.style or job.get("style")
    if style == "vox":
        if job.get("style") != "vox":
            job["style"] = "vox"
            save_job(d, job)
        lines += [""] + P.V.brief_lines(words, job, preset, lang)
    lines += ["", "## Transcript (word ids, master-clock seconds)", ""] + P.pack_transcript(words)
    lines += ["", "## Write the plan", "",
              "Save it as `plan.json` (or `plan.%s.json` for another target) in the job folder, then run "
              "`nvc.py compile %s`. Quotes must be the exact words of the span. Example:" % (target, args.job), "",
              "```json", json.dumps(BRIEF_EXAMPLE, ensure_ascii=False, indent=1), "```", ""]
    out = d / ("edit-brief.md" if target == job["target"] else "edit-brief.%s.md" % target)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote %s (%d transcript lines, %d filler candidates, %d possible retakes)"
          % (out, len(P.pack_transcript(words)), len(fillers), len(retakes)))


# ---------------------------------------------------------------- compile

def plan_path(d, target, given=None):
    if given:
        return Path(given).expanduser().resolve()
    for name in ("plan.%s.json" % target, "plan.json"):
        if (d / name).exists():
            return d / name
    raise NvcError("no plan yet: write %s/plan.json (see edit-brief.md)" % d)


def out_dir(d, target):
    p = d / "out" / target
    p.mkdir(parents=True, exist_ok=True)
    return p


def cmd_compile(args):
    d = job_dir(args.job)
    job = load_job(d)
    pp = plan_path(d, args.target or job["target"], args.plan)
    plan = read_json(pp)
    if plan is None:
        raise NvcError("%s is not valid JSON" % pp)
    target = args.target or plan.get("target") or job["target"]
    preset = target_preset(target)
    if (d / "analysis" / "words.json").exists():
        words, meta = load_words(d)
    else:
        words = []
        log("no transcript: every segment and overlay must be timed in seconds (from, to, at)")
    data = presets()
    result = P.compile_plan(plan, words, job, preset, data["overlays"], data["sfx_defaults"], fps=job.get("fps"))
    rep = result["report"]
    od = out_dir(d, target)
    write_json(od / "report.json", rep)
    if not rep["ok"]:
        print("the plan has %d error(s); nothing was written:" % len(rep["errors"]))
        for e in rep["errors"]:
            print("  x " + e)
        for w in rep["warnings"]:
            print("  ! " + w)
        sys.exit(1)
    edl = result["edl"]
    edl["base"] = "jobs/%s/" % job["id"]
    old = read_json(od / "edl.json") or {}
    if old.get("audio") and Path(d / old["audio"]).exists() and old.get("durationInFrames") == edl["durationInFrames"]:
        edl["audio"] = old["audio"]
    write_json(od / "edl.json", edl)
    write_json(od / "pieces.json", result["pieces"])
    write_json(od / "speech.json", {"spans": result["speech"]})
    write_json(od / "sfx_cues.json", [{k: v for k, v in c.items() if v is not None} for c in result["sfx"]])
    write_json(od / "words.out.json", result["mapped_words"])
    (od / "captions.srt").write_text(P.srt(result["cues"]), encoding="utf-8")
    (od / "captions.vtt").write_text(P.vtt(result["cues"]), encoding="utf-8")
    if result["chapters"]:
        (od / "chapters.txt").write_text(P.chapters_txt(result["chapters"]), encoding="utf-8")
    (od / "edl.md").write_text(P.edl_report_md(result, job, preset), encoding="utf-8")
    mark(job, "compile:" + target, duration=round(result["duration"], 3), clips=len(edl["clips"]),
         overlays=len(edl["overlays"]), warnings=len(rep["warnings"]), review=len(rep["review"]))
    save_job(d, job)
    print("edit: %s, %d clips, %d overlays, %d zooms, %d caption pages, %d sound cues -> %s"
          % (fmt_dur(result["duration"]), len(edl["clips"]), len(edl["overlays"]), len(edl["zooms"]),
             len(edl["captions"]["pages"]) or len(result["cues"]), len(result["sfx"]), od / "edl.json"))
    for w in rep["warnings"]:
        print("  ! " + w)
    for w in rep["review"]:
        print("  ? " + w)
    print("next: nvc.py audio %s%s" % (args.job, "" if target == job["target"] else " --target " + target))


# ---------------------------------------------------------------- audio

def premix_dialogue(d, job, pieces, fps, out):
    """Cut the dialogue on the same frame grid as the picture: every piece is exactly its frame count long, with
    30 ms fades at each cut so no click is heard."""
    src = dialogue_audio(d, job)
    parts, labels = [], []
    for n, p in enumerate(pieces):
        start = p["masterIn"]
        length = p["frames"] / float(fps)
        fade = min(0.03, length / 4)
        parts.append("[0:a]atrim=start=%.6f:duration=%.6f,asetpts=PTS-STARTPTS,apad=whole_dur=%.6f,"
                     "afade=t=in:st=0:d=%.4f,afade=t=out:st=%.6f:d=%.4f[p%d]"
                     % (start, length, length, fade, max(0.0, length - fade), fade, n))
        labels.append("[p%d]" % n)
    graph = ";\n".join(parts) + ";\n" + "".join(labels) + "concat=n=%d:v=0:a=1[out]" % len(labels)
    script = out.with_suffix(".filter.txt")
    script.write_text(graph, encoding="utf-8")
    run(["ffmpeg", "-y", "-v", "error", "-nostdin", "-i", src, filter_file_option(), script, "-map", "[out]",
         "-ac", "1", "-ar", "48000", "-c:a", "pcm_s24le", out], timeout=6 * 3600, check=True)
    return out


def filter_file_option():
    """How this ffmpeg reads a filter graph from a file: `-/filter_complex FILE` from ffmpeg 7 on (newer builds
    removed `-filter_complex_script`, which was deprecated in 7.0), the old option before that."""
    try:
        first = run(["ffmpeg", "-version"], timeout=30).stdout.splitlines()[0]
    except (NvcError, IndexError):
        return "-/filter_complex"
    m = re.search(r"version n?(\d+)\.", first)
    return "-filter_complex_script" if m and int(m.group(1)) < 7 else "-/filter_complex"


def audio_duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], timeout=60)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
            timeout=3600)
    text = r.stderr
    out = {}
    for key, pat in (("I", r"I:\s+(-?[\d.]+) LUFS"), ("LRA", r"LRA:\s+([\d.]+) LU"), ("TP", r"Peak:\s+(-?[\d.]+) dBFS")):
        found = re.findall(pat, text)
        if found:
            out[key] = float(found[-1])
    return out


def simple_master(src, out, target_i, target_tp):
    """Fallback when nexa-sound is missing: two-pass linear loudnorm with the output pinned to 48 kHz."""
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af",
             "loudnorm=I=%s:TP=%s:LRA=11:print_format=json" % (target_i, target_tp), "-f", "null", "-"], timeout=3600)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", r.stderr, re.S)
    if not m:
        raise NvcError("loudness measurement failed")
    j = json.loads(m.group(0))
    af = ("loudnorm=I=%s:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:"
          "linear=true:print_format=json" % (target_i, target_tp, j["input_i"], j["input_tp"], j["input_lra"],
                                             j["input_thresh"], j["target_offset"]))
    r = run(["ffmpeg", "-y", "-hide_banner", "-nostats", "-i", src, "-af", af, "-ar", "48000", "-ac", "2", "-c:a",
             "pcm_s24le", out], timeout=3600, check=True)
    m = re.search(r"\"normalization_type\"\s*:\s*\"(\w+)\"", r.stderr)
    return m.group(1) if m else None


def sound_cmd(args_list, timeout=6 * 3600):
    r = run([sys.executable, SOUND] + args_list + ["--json"], timeout=timeout)
    if r.returncode:
        raise NvcError("nexa-sound %s failed: %s" % (args_list[0], (r.stderr or r.stdout).strip()[-800:]))
    try:
        return json.loads(r.stdout or "{}")
    except ValueError:
        return {"output": r.stdout.strip()[-400:]}


def cmd_audio(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    preset = target_preset(target)
    od = out_dir(d, target)
    edl = read_json(od / "edl.json")
    pieces = read_json(od / "pieces.json")
    if not edl or not pieces:
        raise NvcError("compile the plan first: nvc.py compile %s" % args.job)
    plan = read_json(plan_path(d, target)) or {}
    fps = edl["fps"]
    duration = edl["durationInFrames"] / float(fps)
    ad = d / "audio" / target
    ad.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    dialogue = premix_dialogue(d, job, pieces, fps, ad / "dialogue.wav")
    got = audio_duration(dialogue) or 0
    if abs(got - duration) > 0.02:
        raise NvcError("the dialogue cut is %.3f s, the picture %.3f s: they must match" % (got, duration))
    report = {"dialogue": str(dialogue.relative_to(d)), "duration_s": round(duration, 3)}
    music = None
    mplan = plan.get("music") or {}
    if args.music:
        mplan = {"file": args.music}
    if args.no_music:
        mplan = {}
    if mplan and not SOUND.exists():
        raise NvcError("music needs nexa-sound (not installed at %s); run with --no-music to skip" % SOUND)
    if mplan:
        track = None
        if mplan.get("source"):
            src = job["sources"].get(mplan["source"])
            if not src:
                raise NvcError("music source %s is not in the job" % mplan["source"])
            track = d / src["link"]
        elif mplan.get("file"):
            track = Path(mplan["file"]).expanduser().resolve()
        elif mplan.get("generate"):
            brief_args = ["brief", "--duration", "%.2f" % duration, "--mood", mplan.get("mood") or "corporate",
                          "--out", ad / "music-brief.json", "--cuts", od / "music_cuts.json",
                          "--speech", od / "speech.json"]
            write_json(od / "music_cuts.json", music_cuts(edl))
            sound_cmd(brief_args)
            kind = str(mplan["generate"])
            how = {"draft": ["--draft", "1"], "final": ["--final"], "realtime": ["--realtime"]}.get(kind)
            if not how:
                raise NvcError("music.generate must be draft, final or realtime")
            gen = sound_cmd(["generate", ad / "music-brief.json", "--out", ad / "music", "--budget", str(args.budget),
                             "--project", d] + how)
            takes = [t for t in (gen.get("takes") or []) if t.get("ok") and t.get("file")]
            track = Path(takes[0]["file"]) if takes else None
            if not track or not track.exists():
                raise NvcError("nexa-sound generate gave no file: %s" % json.dumps(gen)[:400])
        if track:
            write_json(od / "music_cuts.json", music_cuts(edl))
            sound_cmd(["fit", track, "--target", "%.3f" % duration, "--cuts", od / "music_cuts.json",
                       "--out", ad / "music.wav"])
            music = ad / "music.wav"
            report["music"] = {"from": str(track), "fitted": str(music.relative_to(d))}
    sfx = None
    cues = read_json(od / "sfx_cues.json") or []
    if cues and not args.no_sfx and SOUND.exists():
        sound_cmd(["sfx", "place", od / "sfx_cues.json", "--duration", "%.3f" % duration, "--out", ad / "sfx.wav",
                   "--fps", str(fps), "--project", d])
        sfx = ad / "sfx.wav"
        report["sfx"] = {"cues": len(cues), "file": str(sfx.relative_to(d))}
    mix = ad / "mix.wav"
    loud = preset["loudness"]
    if SOUND.exists():
        mix_args = ["mix", "--dialogue", dialogue, "--speech", od / "speech.json", "--platform",
                    loud.get("sound_platform") or "youtube", "--out", mix]
        if music:
            mix_args += ["--music", music]
        if sfx:
            mix_args += ["--sfx", sfx]
        report["mix"] = sound_cmd(mix_args)
    else:
        norm = simple_master(dialogue, mix, loud["I"], loud["TP"])
        report["mix"] = {"note": "nexa-sound is not installed: dialogue only, loudness-normalised",
                         "normalization": norm}
    report["measured"] = loudness(mix)
    got = audio_duration(mix) or 0
    if abs(got - duration) > 0.05:
        report.setdefault("warnings", []).append("mix is %.3f s, picture %.3f s" % (got, duration))
    edl["audio"] = str(mix.relative_to(d))
    write_json(od / "edl.json", edl)
    report["seconds"] = round(time.time() - t0, 1)
    write_json(ad / "audio.json", report)
    mark(job, "audio:" + target, **{k: report[k] for k in ("measured", "seconds") if k in report})
    save_job(d, job)
    m = report["measured"]
    print("audio: %s, %.1f LUFS, true peak %.1f dBTP%s%s (%.1f s)" % (
        mix, m.get("I", float("nan")), m.get("TP", float("nan")), ", music" if music else "",
        ", %d sound effects" % len(cues) if sfx else "", report["seconds"]))
    print("next: nvc.py stills %s, then nvc.py render %s" % (args.job, args.job))


def music_cuts(edl):
    fps = float(edl["fps"])
    cuts = []
    last_layout = None
    for c in edl["clips"]:
        if c["layout"] != last_layout or c["transitionIn"]["type"] != "cut":
            cuts.append({"t": round(c["from"] / fps, 3), "weight": 2 if c["transitionIn"]["type"] != "cut" else 1,
                         "label": c["layout"]})
        last_layout = c["layout"]
    for o in edl["overlays"]:
        if o["type"] in ("hook", "stat", "cta", "chapter", "quote", "kinetic", "step", "bigStat", "bars", "versus",
                         "recap", "endCard", "photo"):
            cuts.append({"t": round(o["from"] / fps, 3),
                         "weight": 3 if o["type"] in ("stat", "cta", "step", "bigStat", "endCard") else 2,
                         "label": o["type"]})
    return sorted(cuts, key=lambda c: c["t"])


# ---------------------------------------------------------------- renderer

def template_hash():
    h = hashlib.sha256()
    for p in sorted(TEMPLATE.rglob("*")):
        if p.is_file() and "node_modules" not in p.parts:
            h.update(str(p.relative_to(TEMPLATE)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]


def ensure_renderer(link_modules=None, install=False):
    """The shared Remotion project: the template's files, and node_modules linked from an installed project of the
    same Remotion version (or installed with npm when asked)."""
    RENDERER.mkdir(parents=True, exist_ok=True)
    stamp = RENDERER / ".template-hash"
    want = template_hash()
    if not stamp.exists() or stamp.read_text().strip() != want:
        for p in sorted(TEMPLATE.rglob("*")):
            if not p.is_file() or "node_modules" in p.parts:
                continue
            dest = RENDERER / p.relative_to(TEMPLATE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        stamp.write_text(want)
    mods = RENDERER / "node_modules"
    if link_modules:
        src = Path(link_modules).expanduser().resolve()
        src = src if src.name == "node_modules" else src / "node_modules"
        have = (read_json(src / "remotion" / "package.json") or {}).get("version")
        if have != REMOTION_VERSION:
            raise NvcError("%s has Remotion %s; the renderer needs %s" % (src, have, REMOTION_VERSION))
        if mods.is_symlink():
            mods.unlink()
        if mods.exists():
            raise NvcError("%s exists and is not a link; move it away first" % mods)
        os.symlink(src, mods)
    if not mods.exists():
        if not install:
            raise NvcError("the renderer has no node_modules. Run `nvc.py doctor --setup --link-modules PATH` with an "
                           "installed Remotion %s project (remotion-broll's kit works), or `nvc.py doctor --setup "
                           "--npm` to install (downloads about 600 MB)" % REMOTION_VERSION)
        r = run(["npm", "install", "--no-audit", "--no-fund"], cwd=RENDERER, timeout=3600)
        if r.returncode:
            raise NvcError("npm install failed: " + r.stderr.strip()[-600:])
    (RENDERER / "public" / "jobs").mkdir(parents=True, exist_ok=True)
    return RENDERER


def link_job(d, job):
    link = RENDERER / "public" / "jobs" / job["id"]
    if link.is_symlink():
        if link.resolve() == d:
            return link
        link.unlink()
    elif link.exists():
        raise NvcError("%s exists and is not a link" % link)
    os.symlink(d, link)
    return link


def render_env():
    env = dict(os.environ)
    if T7.exists() and os.access(str(T7), os.W_OK):
        tmp = T7 / "nexa-video-creator" / "tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        env["TMPDIR"] = str(tmp) + "/"
    return env


def props_for(d, job, target):
    od = out_dir(d, target)
    edl = read_json(od / "edl.json")
    if not edl:
        raise NvcError("compile first: nvc.py compile %s" % d)
    edl["base"] = "jobs/%s/" % job["id"]
    props = od / "props.json"
    write_json(props, edl)
    return edl, props


def cmd_stills(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    ensure_renderer()
    link_job(d, job)
    edl, props = props_for(d, job, target)
    n = edl["durationInFrames"]
    frames = set()
    if args.frames:
        frames = {min(n - 1, max(0, int(x))) for x in args.frames.split(",") if x.strip()}
    else:
        fps = edl["fps"]
        frames.add(min(n - 1, int(0.5 * fps)))
        for o in edl["overlays"]:
            if o["type"] == "vox":
                # a vox beat is looked at as each picture lands, and once everything is in
                els = sorted((o.get("props") or {}).get("elements") or [], key=lambda e: e["at"])
                picks = els if len(els) <= 3 else [els[0], els[len(els) // 2], els[-1]]
                for e in picks:
                    frames.add(min(n - 1, o["from"] + min(o["durationInFrames"] - 1, e["at"] + 24)))
                continue
            # a designed scene is looked at once its parts have landed; other graphics 0.8 s in
            t_ = (o.get("props") or {}).get("t") or {}
            at = (t_.get("click", 0) + 12) if o["type"] == "endCard" and t_.get("click") else \
                (t_["land"] + 8 if t_.get("land") else int(0.7 * o["durationInFrames"])) if o["type"] in P.SCENE_TYPES \
                else int(0.8 * fps)
            frames.add(min(n - 1, o["from"] + min(o["durationInFrames"] - 1, at)))
        for c in edl["clips"]:
            frames.add(min(n - 1, c["from"] + min(c["durationInFrames"] - 1, 6)))
        for z in edl["zooms"]:
            frames.add(min(n - 1, z["from"] + z["durationInFrames"] // 2))
        frames = set(sorted(frames)[:24]) if len(frames) > 24 else frames
        if len(frames) < 8:
            frames |= {min(n - 1, int((i + 0.5) * n / 8)) for i in range(8)}
    frames = sorted(frames)
    outdir = out_dir(d, target) / "stills"
    outdir.mkdir(parents=True, exist_ok=True)
    for old in outdir.glob("element-*.png"):
        old.unlink()
    t0 = time.time()
    r = run(["npx", "remotion", "render", "Edit", outdir, "--props=%s" % props, "--frames=%s" % ",".join(map(str, frames)),
             "--image-format=png", "--gl=angle", "--log=error"], cwd=RENDERER, timeout=1800, env=render_env())
    if r.returncode:
        raise NvcError("stills failed: " + (r.stderr or r.stdout).strip()[-900:])
    sheet = out_dir(d, target) / "stills.png"
    cols = 4 if len(frames) > 9 else 3
    rows = -(-len(frames) // cols)
    tw = 480 if edl["width"] >= edl["height"] else 270
    th = int(round(tw * edl["height"] / float(edl["width"])))
    run(["ffmpeg", "-y", "-v", "error", "-pattern_type", "glob", "-i", str(outdir / "*.png"), "-vf",
         "scale=%d:%d,tile=%dx%d:padding=6:color=white" % (tw, th, cols, rows), "-frames:v", "1", sheet], timeout=300)
    print(json.dumps({"frames": frames, "seconds_at": [round(f / float(edl["fps"]), 2) for f in frames],
                      "sheet": str(sheet), "folder": str(outdir), "took_s": round(time.time() - t0, 1)}, indent=1))


def cmd_render(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    preset = target_preset(target)
    ensure_renderer()
    link_job(d, job)
    edl, props = props_for(d, job, target)
    if not edl.get("audio"):
        log("note: no mixed audio yet (nvc.py audio); the render is silent")
    od = out_dir(d, target)
    out = Path(args.out).expanduser().resolve() if args.out else od / ("%s-%s%s.mp4" % (job["id"], target,
                                                                                          "-draft" if args.draft else ""))
    cmd = ["npx", "remotion", "render", "Edit", out, "--props=%s" % props, "--gl=angle",
           "--concurrency=%d" % int(preset.get("render", {}).get("concurrency") or 6), "--jpeg-quality=90",
           "--media-cache-size-in-bytes=4294967296", "--color-space=bt709", "--log=error"]
    if args.draft:
        cmd += ["--scale=0.5", "--crf=28"]
    else:
        cmd += ["--crf=%d" % int(preset.get("render", {}).get("crf") or 18)]
    t0 = time.time()
    r = run(cmd, cwd=RENDERER, timeout=12 * 3600, env=render_env())
    if r.returncode:
        raise NvcError("render failed: " + (r.stderr or r.stdout).strip()[-1200:])
    took = time.time() - t0
    info = probe(out)
    loud = loudness(out) if info.get("hasAudio") else {}
    rep = {"video": str(out), "render_s": round(took, 1), "duration_s": info.get("duration"),
           "size_mb": round(info.get("size_bytes", 0) / 1e6, 1), "loudness": loud,
           "speed": "%.2f s of render per s of video" % (took / max(0.1, info.get("duration") or 1))}
    write_json(od / "render.json", rep)
    mark(job, "render:" + target, **{k: rep[k] for k in ("render_s", "duration_s", "size_mb")})
    save_job(d, job)
    print(json.dumps(rep, indent=1))
    print("next: nvc.py qa %s%s" % (args.job, "" if target == job["target"] else " --target " + target))


# ---------------------------------------------------------------- QA and delivery

def cmd_qa(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    preset = target_preset(target)
    od = out_dir(d, target)
    rend = read_json(od / "render.json")
    if not rend:
        raise NvcError("render first: nvc.py render %s" % args.job)
    video = rend["video"]
    edl = read_json(od / "edl.json")
    checks = []

    def check(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    want = edl["durationInFrames"] / float(edl["fps"])
    got = rend.get("duration_s") or 0
    check("length", abs(got - want) < 0.1, "%.2f s rendered, %.2f s planned" % (got, want))
    loud = rend.get("loudness") or {}
    tgt = preset["loudness"]
    if loud:
        check("loudness", abs(loud.get("I", 0) - tgt["I"]) <= 1.0, "%.1f LUFS (target %.0f +-1)" % (loud.get("I", 0),
                                                                                                    tgt["I"]))
        check("true peak", loud.get("TP", 0) <= tgt["TP"] + 0.5, "%.1f dBTP (target %.1f or lower; AAC adds a "
                                                                  "little)" % (loud.get("TP", 0), tgt["TP"]))
    else:
        check("sound", False, "the video has no audio track")
    rep_plan = read_json(od / "report.json") or {}
    check("plan review items", not rep_plan.get("review"), "%d item(s) to confirm: %s" % (
        len(rep_plan.get("review") or []), "; ".join(rep_plan.get("review") or [])[:300]))
    measured = None
    if WATCH.exists():
        r = run([sys.executable, WATCH, "qa", video, "--platform", preset.get("qa_platform") or "generic"],
                timeout=1800)
        try:
            measured = json.loads(r.stdout)
            check("agy-watch-video qa", measured.get("ok", False), "; ".join(
                str(f) for f in (measured.get("flags") or [])[:8]) or "clean")
        except ValueError:
            check("agy-watch-video qa", False, "no answer: " + r.stderr.strip()[-300:])
    review = None
    if args.review and WATCH.exists():
        expect = od / "expect.txt"
        lines = []
        for o in edl["overlays"]:
            text = P._overlay_text({"props": o["props"]})
            if text and o["type"] not in ("broll", "image", "segment", "redact"):
                lines.append(text)
        expect.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cmd = [sys.executable, WATCH, "watch", video, "--goal", "promo", "--platform", preset.get("qa_platform") or
               "generic"]
        if lines:
            cmd += ["--expect", expect]
        r = run(cmd, timeout=3600)
        review = r.stdout[-6000:] if r.returncode == 0 else ("review failed: " + r.stderr[-400:])
    result = {"video": video, "target": target, "ok": all(c["ok"] for c in checks), "checks": checks,
              "agy_qa": measured, "review": review}
    write_json(od / "qa.json", result)
    for c in checks:
        print("%s %s: %s" % ("ok " if c["ok"] else "FIX", c["check"], c["detail"]))
    if review:
        print("\n" + review[-3000:])
    print("next: nvc.py deliver %s" % args.job if result["ok"] else "fix the items above, then render again")


def cmd_deliver(args):
    d = job_dir(args.job)
    job = load_job(d)
    target = args.target or job["target"]
    preset = target_preset(target)
    od = out_dir(d, target)
    rend = read_json(od / "render.json")
    if not rend:
        raise NvcError("render first")
    qa = read_json(od / "qa.json") or {}
    if not qa.get("ok") and not args.force:
        raise NvcError("QA has open items (nvc.py qa %s); fix them or deliver with --force" % args.job)
    fd = d / "final"
    fd.mkdir(exist_ok=True)
    name = slug(job.get("title") or job["id"]) + "-" + target
    video = fd / (name + ".mp4")
    shutil.copy2(rend["video"], video)
    files = [video.name]
    for ext in ("srt", "vtt"):
        src = od / ("captions." + ext)
        if src.exists():
            shutil.copy2(src, fd / ("%s.%s" % (name, ext)))
            files.append("%s.%s" % (name, ext))
    if (od / "chapters.txt").exists():
        shutil.copy2(od / "chapters.txt", fd / (name + ".chapters.txt"))
        files.append(name + ".chapters.txt")
    edl = read_json(od / "edl.json") or {}
    try:
        plan = read_json(plan_path(d, target)) or {}
    except NvcError:
        plan = {}
    notes = disclosure_notes(d, job, edl, plan)
    (fd / (name + ".notes.md")).write_text(notes, encoding="utf-8")
    files.append(name + ".notes.md")
    if SOUND.exists() and (d / "audio" / target).exists():
        r = run([sys.executable, SOUND, "credits"] + credit_roots(d, target)
                + ["--out", fd / (name + ".CREDITS.txt"), "--strict"], timeout=300)
        if (fd / (name + ".CREDITS.txt")).exists():
            files.append(name + ".CREDITS.txt")
        if r.returncode != 0 and not args.allow_noncommercial:
            raise NvcError("the sound has ElevenLabs items made on a free or unknown plan (see %s): they are not for "
                           "client delivery. Make them again on a paid plan, or deliver an internal test with "
                           "--allow-noncommercial" % (fd / (name + ".CREDITS.txt")))
    report = ["# Delivery: %s (%s)" % (job.get("title"), preset["label"]), "",
              "- Video: %s, %s, %.1f MB, rendered in %.0f s" % (video.name, fmt_dur(rend.get("duration_s")),
                                                               rend.get("size_mb", 0), rend.get("render_s", 0)),
              "- Loudness: %s" % json.dumps(rend.get("loudness")), "- QA: %s" % ("passed" if qa.get("ok") else
                                                                                "delivered with open items"), ""]
    for c in qa.get("checks") or []:
        report.append("  - %s %s: %s" % ("ok" if c["ok"] else "open", c["check"], c["detail"]))
    report += ["", "Files: " + ", ".join(files), ""]
    edl_md = od / "edl.md"
    if edl_md.exists():
        report += ["", edl_md.read_text(encoding="utf-8")]
    (fd / (name + ".report.md")).write_text("\n".join(report), encoding="utf-8")
    files.append(name + ".report.md")
    mark(job, "deliver:" + target, files=files)
    save_job(d, job)
    print("delivered to %s:" % fd)
    for f in files:
        print("  " + f)


def sidecars(root):
    """Every small JSON under root (audio and media provenance)."""
    out = []
    for p in root.rglob("*.json") if root.exists() else []:
        try:
            if p.stat().st_size < 2000000:
                j = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(j, dict):
                    out.append(j)
        except (OSError, ValueError):
            continue
    return out


def credit_roots(d, target):
    """The folders whose sound goes into a target's video: its mix folder, and the cleaned dialogue it was made from
    (voice isolation may have been ElevenLabs')."""
    roots = [d / "audio" / target]
    if (d / "media" / "audio").exists():
        roots.append(d / "media" / "audio")
    return roots


def used_sources(edl):
    """The source ids a compiled edit shows: clip placements, overlays, and the pictures in vox beats and scenes."""
    used = set()
    for c in edl.get("clips") or []:
        for key in ("cam", "screen", "broll"):
            if isinstance(c.get(key), dict) and c[key].get("source"):
                used.add(c[key]["source"])
    for o in edl.get("overlays") or []:
        p = o.get("props") or {}
        if p.get("source"):
            used.add(p["source"])
        for el in p.get("elements") or []:
            if isinstance(el, dict) and el.get("source"):
                used.add(el["source"])
        for ref in [p.get("left"), p.get("right")] + list(p.get("items") or []):
            if isinstance(ref, dict) and ref.get("source"):
                used.add(ref["source"])
    return used


PIXABAY_FILE = re.compile(r"pixabay-(\d+)")


def stock_used(job, edl):
    """The stock records of the files the edit shows, following cut-outs and keyed clips back to their stock file.
    Without an edit (an older job) every stock pick counts."""
    stock = job.get("stock") or {}
    if not edl:
        return stock
    ids = set()
    for sid in used_sources(edl):
        src = (job.get("sources") or {}).get(sid) or {}
        derived = src.get("cutout") or src.get("keyed") or {}
        if derived.get("stock_id"):
            ids.add(str(derived["stock_id"]))
        for text in (src.get("original"), derived.get("from"), src.get("link")):
            m = PIXABAY_FILE.search(str(text or ""))
            if m:
                ids.add(m.group(1))
        origin = (job.get("sources") or {}).get(derived.get("from")) if derived.get("from") else None
        if origin:
            m = PIXABAY_FILE.search(str(origin.get("original") or ""))
            if m:
                ids.add(m.group(1))
    return {k: v for k, v in stock.items() if str(k) in ids}


def facts_lines(plan):
    """Every fact the plan gave for a number or a page on screen, with its source: the record a client checks."""
    out = []
    for ov in plan.get("overlays") or []:
        for f in ov.get("facts") or []:
            if not isinstance(f, dict) or not str(f.get("text") or "").strip():
                continue
            where = f.get("url") or f.get("source") or f.get("origin")
            out.append("- %s (%s)" % (str(f["text"]).strip(), where))
    return out


def disclosure_notes(d, job, edl=None, plan=None):
    lines = ["# Notes for the upload", ""]
    voice = [s for s in job["sources"].values() if s.get("kind") == "voice"]
    audio = sidecars(d / "audio")
    tracks = [j for j in audio if j.get("schema") == "nexa-sound/track-1"]
    lyria = any((j.get("provider") or {}).get("api") != "elevenlabs" for j in tracks)
    eleven_music = any((j.get("provider") or {}).get("api") == "elevenlabs" for j in tracks)
    eleven_any = eleven_music or any(j.get("schema") in ("nexa-sound/elevenlabs-1", "nexa-sound/ambience-1")
                                     for j in audio)
    if voice:
        lines.append("- The voice-over is synthetic (text-to-speech). YouTube asks for the \"altered or "
                     "synthetic content\" label when a voice could be taken for a real person; Meta labels realistic "
                     "AI audio; TikTok needs a label only when it imitates a real person's voice.")
    if lyria:
        lines.append("- Music generated with Google Lyria carries Google's SynthID watermark, is not exclusive, and "
                     "must not be registered with Content ID. Background music alone does not need YouTube's "
                     "synthetic-content label.")
    if eleven_any:
        lines.append("- ElevenLabs music or sound carries ElevenLabs' inaudible watermark and is not exclusive: never "
                     "register it with Content ID. Eleven Music on self-serve plans covers online video, not film, "
                     "TV, radio or games; see CREDITS.txt for the plan it was made on.")
    stock = stock_used(job, edl or {})
    if stock:
        lines.append("- Stock from Pixabay (Pixabay Content License; no credit needed): %s. Keep these records: if "
                     "a claim ever comes up, the file is taken out of the video." % "; ".join(
                         "%s by %s" % (v.get("page_url"), v.get("user")) for v in stock.values()))
        if any(v.get("ai_generated") for v in stock.values()):
            lines.append("- Some stock was marked AI-made on Pixabay: disclose it where the platform asks for "
                         "realistic AI imagery.")
    cut = [s for s in (job.get("sources") or {}).values() if s.get("cutout") and s.get("id") in used_sources(edl or {})]
    if cut:
        lines.append("- Cut-outs were made on this Mac with Apple Vision (a mask of the subject, then halftone and a "
                     "marker stroke): an edit of the stock picture, nothing generated.")
    facts = facts_lines(plan or {})
    if facts:
        lines += ["", "## Facts on screen and their sources", ""] + facts
    lines.append("")
    lines.append("- Keep the original recordings and the job folder: they are the proof of what was filmed.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- stock media (Pixabay)

STOCK_TYPES = {"video": ("video", "film"), "animation": ("video", "animation"), "photo": ("image", "photo"),
               "illustration": ("image", "illustration"), "vector": ("image", "vector")}
PIXABAY_LICENCE = {"name": "Pixabay Content License", "url": "https://pixabay.com/service/license-summary/",
                   "terms": "https://pixabay.com/service/terms/", "attribution_required": False,
                   "notes": ["free for commercial use and to edit; no credit needed (\"by X via Pixabay\" is optional)",
                             "never sell or hand over the file as it is, alone or as stock; not in a trademark or logo",
                             "no visible logo or brand used to promote a product, and nothing that implies endorsement",
                             "recognisable people: not in health, dating, drug, adult or political contexts; Pixabay "
                             "has no model releases",
                             "no political use",
                             "do not feed the file to AI tools (img2img, outpainting, AI upscaling, training): "
                             "Pixabay's October 2025 IP guidance",
                             "if a claim comes up, stop using the file and delete it: this record says where it went"]}
STOCK_WEIGHTS = {"subject": 0.30, "action": 0.15, "setting": 0.10, "people_market": 0.15, "quality": 0.15,
                 "framing": 0.15}
STOCK_HARD_GATES = ("watermark", "burned_text", "logo_or_brand", "nsfw_or_gore", "wrong_place")
STOCK_JUDGE_SCHEMA = {"type": "array", "items": {"type": "object", "properties": {
    "i": {"type": "integer"}, "subject": {"type": "integer"}, "action": {"type": "integer"},
    "setting": {"type": "integer"}, "people_market": {"type": "integer", "nullable": True},
    "quality": {"type": "integer"}, "framing": {"type": "integer"},
    "gates": {"type": "object", "properties": {g: {"type": "boolean"} for g in (
        "watermark", "burned_text", "logo_or_brand", "nsfw_or_gore", "ai_look", "identifiable_person",
        "sensitive_context", "wrong_place")}},
    "seen": {"type": "string"}}, "required": ["i", "subject", "quality", "framing", "gates"]}}


def frame_size(job):
    preset = target_preset(job.get("target") or "youtube")
    return int(preset["width"]), int(preset["height"])


def stock_dir(d, query):
    folder = d / "media" / "stock" / slug(query, "stock")
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def stock_sheet(items, out, cell=(480, 270)):
    """The candidates on one numbered contact sheet (sheet.swift draws the numbers and captions)."""
    spec = out.with_suffix(".spec.json")
    write_json(spec, {"out": str(out), "cols": 4, "cell_w": cell[0], "cell_h": cell[1],
                      "items": [{"file": it.get("thumb") or "", "label": str(it["n"]), "caption": it["caption"]}
                                for it in items]})
    tool = compile_swift("sheet")
    if tool:
        r = run([tool, spec], timeout=120)
        if r.returncode == 0 and out.exists():
            return out
    files = [it.get("thumb") for it in items]      # no labels without swiftc: numbered in reading order
    if not any(files):
        return None
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for f in files:          # a missing preview stays a grey cell, so every cell keeps its number's place
        cmd += ["-i", f] if f else ["-f", "lavfi", "-i", "color=c=gray:s=%dx%d:d=1" % cell]
    graph = "".join("[%d:v]scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2[v%d];"
                    % (i, cell[0], cell[1], cell[0], cell[1], i) for i in range(len(files)))
    cols = 4
    layout = "|".join("%d_%d" % ((i % cols) * cell[0], (i // cols) * cell[1]) for i in range(len(files)))
    graph += "".join("[v%d]" % i for i in range(len(files))) + "xstack=inputs=%d:layout=%s:fill=gray[out]" % (
        len(files), layout) if len(files) > 1 else "[v0]null[out]"
    run(cmd + ["-filter_complex", graph, "-map", "[out]", "-frames:v", "1", out], timeout=120, check=True)
    return out


def stock_caption(it):
    size = "%sx%s" % (it.get("download_w"), it.get("download_h"))
    bits = [it["kind"], size]
    if it.get("duration"):
        bits.append("%d s" % round(it["duration"]))
    bits.append("fills the frame" if it["fills_frame"] else "card only")
    if it.get("ai_generated"):
        bits.append("AI-made")
    return "  ".join(bits) + "  " + ", ".join(it.get("tags") or [])[:60]


def cmd_stock(args):
    d = job_dir(args.job)
    job = load_job(d)
    if args.pick:
        return stock_pick(d, job, args)
    if not args.query:
        raise NvcError("give a search, for example: nvc.py stock JOB \"laptop typing\" --type video")
    api, sub = STOCK_TYPES[args.type]
    W, H = frame_size(job)
    orient = args.orientation
    if orient == "auto":
        orient = "horizontal" if W > H else ("vertical" if H > W else "all")
    params = {"per_page": max(3, min(200, args.n * 3)), "safesearch": True, "order": args.order,
              "lang": args.lang or None, "page": 1}
    if api == "image":
        params.update({"image_type": sub, "orientation": orient, "editors_choice": True if args.editors_choice else None})
    else:
        params["video_type"] = sub
        if orient == "vertical":
            params["min_height"] = H          # a 4K landscape clip still fills a 9:16 frame when cropped
        elif orient == "horizontal":
            params["min_width"] = W
    queries = [args.query] + [q for q in (args.also or []) if q and q != args.query]
    hits, seen, total = [], set(), 0
    for q in queries:
        try:
            found = X.search(api, q, **params)
        except X.PixabayError as err:
            raise NvcError("Pixabay: %s" % err)
        total += found.get("totalHits") or 0
        for hit in found.get("hits") or []:
            if hit.get("id") not in seen:
                seen.add(hit.get("id"))
                hit["_query"] = q
                hits.append(hit)
    folder = stock_dir(d, args.query)
    items, skipped = [], {"low quality": 0, "AI-made": 0, "too short": 0}
    for hit in hits:
        it = X.normalize(api, hit)
        if hit.get("isLowQuality"):
            skipped["low quality"] += 1
            continue
        if args.no_ai and hit.get("isAiGenerated"):
            skipped["AI-made"] += 1
            continue
        if api == "video" and args.min_seconds and (it.get("duration") or 0) < args.min_seconds:
            skipped["too short"] += 1
            continue
        it.update({"ai_generated": bool(hit.get("isAiGenerated")), "g_rated": bool(hit.get("isGRated")),
                   "fills_frame": X.covers(it, W, H), "type": args.type, "query": hit.get("_query")})
        items.append(it)
    items.sort(key=lambda it: not it["fills_frame"])        # stable: Pixabay's relevance order inside each group
    items = items[:args.n]
    thumbs = folder / "thumbs"
    thumbs.mkdir(exist_ok=True)
    for i, it in enumerate(items, 1):
        it["n"] = i
        url = it.get("thumbnail_url") or it.get("preview_url")
        dest = thumbs / ("%s.jpg" % it["id"])
        if url and not dest.exists():
            try:
                X.download(url, str(dest), max_bytes=20 * 1024 ** 2, timeout=120)
            except X.PixabayError as err:
                log("no preview for %s: %s" % (it["id"], err))
        it["thumb"] = str(dest) if dest.exists() else None
        it["caption"] = stock_caption(it)
    sheet = stock_sheet(items, folder / "sheet.png") if items else None
    judged = None
    if args.judge and sheet:
        judged = stock_judge(sheet, items, args, W, H)
    data = {"schema": "nvc-stock-search/1", "query": args.query, "also": queries[1:], "type": args.type,
            "frame": [W, H], "orientation": orient, "searched": now(), "total": total, "skipped": skipped,
            "sheet": str(sheet) if sheet else None, "items": items, "judge": judged, "licence": PIXABAY_LICENCE}
    write_json(folder / "candidates.json", data)
    if judged and args.auto_pick and judged.get("best"):
        args.pick = str(judged["best"])
        stock_pick(d, load_job(d), args)
        return
    if args.json:
        emit(data, True)
        return
    print("stock: %d Pixabay %s for %r (%s%s); %s" % (
        len(items), args.type + ("s" if len(items) != 1 else ""), args.query, orient,
        ", skipped " + ", ".join("%d %s" % (v, k) for k, v in skipped.items() if v) if any(skipped.values()) else "",
        ("sheet: %s" % sheet) if sheet else "no sheet"))
    for it in items:
        v = it.get("verdict")
        print(" %2d  #%-9s %s%s" % (it["n"], it["id"], it["caption"],
                                   ("   judge: %s %.2f (%s)" % (v["verdict"], v["score"], v.get("seen") or "")
                                    if v else "")))
    if judged:
        print("judge: %s" % (("best #%s (%.2f)" % (judged["best"], judged["best_score"])) if judged.get("best")
                             else "no candidate reached %.2f with subject 4 or more: search another way or make it"
                             % STOCK_ACCEPT.get(args.use, 0.75)))
    if items:
        print("look at the sheet, then: nvc.py stock %s --pick ID [--id NAME]" % args.job)
    print("nothing fits? make it instead: codex-imagegen for a still (text prompt only, never a Pixabay file as the "
          "reference), remotion-broll for an explainer scene")
    print("results from Pixabay (pixabay.com); the Pixabay Content License applies")


STOCK_ACCEPT = {"ad": 0.75, "broll": 0.70, "background": 0.65}   # to tune on the first 50 real slots


def stock_verdict(c, real_only=False, ad=False, accept=0.75):
    """(verdict, score) from one judged candidate: the weighted rubric, the hard gates, the thresholds."""
    used = {k: w for k, w in STOCK_WEIGHTS.items() if c.get(k) is not None}
    score = sum(float(c[k]) * w for k, w in used.items()) / (5.0 * sum(used.values())) if used else 0.0
    g = c.get("gates") or {}
    if any(g.get(k) for k in STOCK_HARD_GATES) or (real_only and g.get("ai_look")) \
            or (g.get("identifiable_person") and g.get("sensitive_context")):
        return "reject", score
    if score >= accept and (c.get("subject") or 0) >= 4 and (c.get("quality") or 0) >= 3 \
            and (c.get("framing") or 0) >= 3:
        return ("human" if ad and g.get("identifiable_person") else "accept"), score
    return ("near" if score >= accept - 0.15 else "reject"), score


def stock_judge(sheet, items, args, W, H):
    """Gemini 3.8 Flash looks at the numbered sheet and scores every candidate against the slot (subject, action,
    setting, people and market, quality, framing) with hard gates for watermarks, burned-in text, logos, unsafe
    content and the wrong place. About a cent a sheet."""
    import base64
    if not gemini_api.keys():
        log("no Gemini key: look at the sheet yourself instead of --judge")
        return None
    slot = args.slot or args.query
    aspect = "%d:%d" % (W // math.gcd(W, H), H // math.gcd(W, H))
    prompt = ("You check stock candidates for one slot of a client video. Judge only what you can see.\n"
              "SLOT: %s\nUSE: %s\nMARKET: %s\n"
              "The sheet shows %d candidates, each with its number in a red badge; the final frame is %s.\n"
              "Return one object per candidate: i (its number), subject, action, setting, people_market (null when no "
              "people are visible), quality, framing (0 to 5 each: 5 = exactly the slot, 3 = usable but generic, "
              "1 = wrong), gates (watermark, burned_text, logo_or_brand, nsfw_or_gore, ai_look, identifiable_person, "
              "sensitive_context, wrong_place: true or false; if unsure, true) and seen (at most 15 words: what is "
              "really in the frame). people_market: do the people, dress, signs and buildings fit the market? "
              "wrong_place applies only when a market is named."
              % (slot, args.use, args.market or "none named", len(items), aspect))
    data = base64.b64encode(Path(sheet).read_bytes()).decode("ascii")
    body = {"model": "gemini-3.8-flash", "store": False, "response_format": STOCK_JUDGE_SCHEMA,
            "input": [{"type": "text", "text": prompt}, {"type": "image", "mime_type": "image/png", "data": data}]}
    try:
        resp, info = gemini_api.interactions(body, timeout=300)
    except gemini_api.GeminiError as err:
        log("the stock judge failed (%s): look at the sheet yourself" % err.kind)
        return None
    text = "".join(gemini_api.text_parts(resp)).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        rows = json.loads(text)
    except ValueError:
        log("the stock judge did not answer in JSON: look at the sheet yourself")
        return None
    by_n = {it["n"]: it for it in items}
    best, best_score = None, 0.0
    for c in rows if isinstance(rows, list) else []:
        it = by_n.get(c.get("i"))
        if not it:
            continue
        verdict, score = stock_verdict(c, real_only=args.no_ai, ad=args.use == "ad",
                                       accept=STOCK_ACCEPT.get(args.use, 0.75))
        it["verdict"] = {"verdict": verdict, "score": round(score, 3), "seen": c.get("seen"), "raw": c}
        if verdict == "accept" and it.get("fills_frame") and score > best_score:
            best, best_score = it["id"], score
    return {"model": "gemini-3.8-flash", "key_source": info.get("key"), "usage": gemini_api.usage(resp),
            "best": best, "best_score": round(best_score, 3), "slot": slot, "market": args.market}


def stock_find(d, pick):
    for cand in sorted((d / "media" / "stock").glob("*/candidates.json"), key=lambda p: p.stat().st_mtime,
                       reverse=True):
        data = read_json(cand) or {}
        for it in data.get("items") or []:
            if str(it.get("id")) == str(pick) or ("n%s" % it.get("n")) == str(pick):
                return it, data
    return None, None


def stock_pick(d, job, args):
    it, search = stock_find(d, args.pick)
    if it is None:
        raise NvcError("#%s is not in this job's stock searches; search first (nvc.py stock JOB \"words\")" % args.pick)
    api = STOCK_TYPES[it.get("type") or "video"][0]
    url = it.get("download_url")
    if not url:
        raise NvcError("#%s has no download link" % it["id"])
    ext = ".mp4" if api == "video" else (os.path.splitext(url.split("?")[0])[1].lower() or ".jpg")
    dest = d / "media" / "stock" / ("pixabay-%s%s" % (it["id"], ext))
    if not dest.exists():
        log("downloading Pixabay #%s (%s)" % (it["id"], "%.1f MB" % (it["download_size"] / 1e6)
                                              if it.get("download_size") else it.get("download_field")))
        try:
            X.download(url, str(dest))
        except X.PixabayError as err:
            raise NvcError("Pixabay: %s" % err)
    digest = hashlib.sha256(dest.read_bytes()).hexdigest()
    side = {"schema": "nvc-stock/1", "source": "pixabay", "id": it["id"], "type": it.get("type"),
            "page_url": it.get("page_url"), "user": it.get("user"), "user_id": it.get("user_id"),
            "tags": it.get("tags"), "query": (search or {}).get("query"), "width": it.get("download_w"),
            "height": it.get("download_h"), "duration": it.get("duration"), "rendition": it.get("download_field"),
            "ai_generated": it.get("ai_generated"), "fills_frame": it.get("fills_frame"),
            "downloaded": now(), "sha256": digest, "licence": PIXABAY_LICENCE}
    write_json(dest.with_name(dest.name + ".json"), side)
    role = "broll" if api == "video" else "image"
    cmd_add(argparse.Namespace(job=str(d), files=[str(dest)], role=role, id=args.id or "px-%s" % it["id"]))
    job = load_job(d)
    job.setdefault("stock", {})[str(it["id"])] = {k: side[k] for k in ("source", "page_url", "user", "type",
                                                                           "ai_generated", "sha256")}
    save_job(d, job)
    if not it.get("fills_frame"):
        print("note: %sx%s does not fill the %s frame without enlarging; use it as a card (fit box) or pick another"
              % (it.get("download_w"), it.get("download_h"), "x".join(str(v) for v in frame_size(job))))


# ---------------------------------------------------------------- cut-outs for Vox beats

def cmd_cutout(args):
    """Cut the subject out of pictures (Apple Vision, on this Mac) and style them for a Vox-style collage. A person
    becomes black and white halftone with the red-orange marker stroke behind, anything else keeps its colour; a
    soft shadow is baked in. Each cut-out is added to the job as a picture with transparency, with a note of where it
    came from (a stock picture's licence travels with it)."""
    d = job_dir(args.job)
    job = load_job(d)
    tool = compile_swift("cutout")
    if not tool:
        raise NvcError("cutting out needs swiftc (xcode-select --install) and macOS 14 or newer")
    outdir = d / "media" / "cutouts"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for n, f in enumerate(args.pictures):
        src_id = None
        if f in job["sources"]:
            src_id = f
            srec = job["sources"][f]
            path = Path(srec.get("original") or (d / srec["link"]))
        else:
            path = Path(f).expanduser().resolve()
        if not path.exists():
            raise NvcError("no such picture or source id: %s" % f)
        if path.suffix.lower() not in IMAGE_EXT:
            raise NvcError("%s is not a picture (cut a still out of a clip first: nvc.py frames, or ffmpeg)" % path.name)
        sid = slug(args.id if (args.id and len(args.pictures) == 1) else (src_id or path.stem) + "-cut", "cutout")
        out = outdir / (sid + ".png")
        cmd = [tool, path, out, "--style", args.style, "--stroke", args.stroke, "--shadow", args.shadow]
        if args.stroke_width:
            cmd += ["--stroke-width", str(args.stroke_width)]
        if args.offset:
            cmd += ["--offset", args.offset]
        if args.no_lift:
            cmd.append("--no-lift")
        if args.largest:
            cmd.append("--largest")
        r = run(cmd, timeout=600)
        if r.returncode:
            raise NvcError("cutout %s: %s" % (path.name, (r.stderr or r.stdout).strip()[-400:]))
        info = json.loads(r.stdout.strip().splitlines()[-1])
        # where it came from: a stock picture's record (and licence) travels with the cut-out
        origin = read_json(Path(str(path) + ".json")) or {}
        side = {"schema": "nvc-cutout/1", "from": src_id or str(path), "made": now(),
                "tool": "Apple Vision foreground mask and Core Image, on this Mac (a cut-out, nothing generated)",
                "style": info["style"], "stroke": info["stroke"], "shadow": info["shadow"], "people": info["people"],
                "width": info["width"], "height": info["height"]}
        if origin.get("licence"):
            side.update({"licence": origin["licence"], "source": origin.get("source"), "page_url": origin.get("page_url"),
                         "user": origin.get("user"), "stock_id": origin.get("id")})
        write_json(out.with_name(out.name + ".json"), side)
        rel = str(out.relative_to(d))
        job["sources"][sid] = {"id": sid, "role": "image", "kind": "cutout", "original": str(out), "link": rel,
                               "image": rel, "probe": {"image": True, "width": info["width"],
                                                       "height": info["height"]},
                               "evidence": "cut out by nvc.py cutout from %s" % (src_id or path.name),
                               "duration": None, "width": info["width"], "height": info["height"],
                               "hasAudio": False, "hasVideo": False, "alpha": True, "people": info["people"],
                               "cutout": side}
        if origin.get("licence") and info["people"]:
            rows.append("%s: note: a recognisable person from stock: Pixabay allows no political, health, dating, "
                        "drug or adult use of people (no model releases)" % sid)
        rows.append("%s: %s%s, %dx%d, %s" % (sid, info["style"], " + marker stroke" if info["stroke"] != "none" else "",
                                            info["width"], info["height"],
                                            "%d person(s)" % info["people"] if info["people"] else "no people"))
    save_job(d, job)
    for row in rows:
        print(row)
    print("next: use them in a vox beat (\"kind\": \"cutout\", \"source\": ID); references/plan.md, Vox beats")


KEY_MAX_S = 20.0


def key_filter(on, width):
    """ffmpeg filters that make a clip's background transparent. On black, the brightness becomes the alpha and the
    colour is un-premultiplied, so flames and sparks stay bright on light paper (a screen blend washes them out
    there); on green, a chroma key with the green spill taken out."""
    scale = "scale='min(%d,iw)':-2" % width
    if on == "green":
        return "%s,chromakey=color=0x00FF00:similarity=0.16:blend=0.08,despill=type=green,format=yuva420p" % scale
    m = "max(max(r(X,Y),g(X,Y)),b(X,Y))"
    un = "if(gt({m},0),{c}(X,Y)*255/{m},0)"
    return ("%s,format=rgba,geq=r='%s':g='%s':b='%s':a='clip((%s-18)*1.25,0,255)',format=yuva420p"
            % (scale, un.format(m=m, c="r"), un.format(m=m, c="g"), un.format(m=m, c="b"), m))


def backdrop_of(path):
    """black or green: what a clip was shot on, from the average colour of its frame's edges."""
    try:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.5", "-i", str(path), "-frames:v", "1", "-vf",
                              "scale=64:36,crop=64:6:0:0,scale=1:1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, timeout=120).stdout or b""
    except (OSError, subprocess.TimeoutExpired):
        raw = b""
    if len(raw) < 3:
        return "black"
    red, green, blue = raw[0], raw[1], raw[2]
    return "green" if green > 90 and green > red * 1.4 and green > blue * 1.4 else "black"


def cmd_key(args):
    """Make clips shot on black (fire, smoke, sparks, light) or on a green screen transparent: a VP9 WebM with
    alpha that a Vox beat lays over the paper as it is. Each becomes a source of the job with a note of where it
    came from (a stock clip's licence travels with it)."""
    d = job_dir(args.job)
    job = load_job(d)
    outdir = d / "media" / "keyed"
    outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for f in args.clips:
        src_id = f if f in job["sources"] else None
        if src_id:
            srec = job["sources"][f]
            path = Path(srec.get("original") or (d / srec["link"]))
        else:
            path = Path(f).expanduser().resolve()
        if not path.exists():
            raise NvcError("no such clip or source id: %s" % f)
        sid = slug(args.id if (args.id and len(args.clips) == 1) else (src_id or path.stem) + "-key", "keyed")
        out = outdir / (sid + ".webm")
        on = args.on if args.on != "auto" else backdrop_of(str(path))
        start = float(args.start or 0)
        length = float(args.seconds or KEY_MAX_S)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "%.3f" % start, "-t", "%.3f" % length, "-i", path, "-vf",
               key_filter(on, int(args.max)), "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-crf", "32", "-b:v", "0",
               "-auto-alt-ref", "0", "-row-mt", "1", "-an", out]
        t0 = time.time()
        r = run(cmd, timeout=3600)
        if r.returncode or not out.exists():
            raise NvcError("keying %s failed: %s" % (path.name, (r.stderr or "").strip()[-400:]))
        info = probe(out)
        origin = read_json(Path(str(path) + ".json")) or {}
        side = {"schema": "nvc-keyed/1", "from": src_id or str(path), "made": now(), "on": on,
                "tool": "ffmpeg %s key on this Mac" % ("luma (brightness as alpha)" if on == "black" else "chroma"),
                "start_s": start, "seconds": info.get("duration")}
        if origin.get("licence"):
            side.update({"licence": origin["licence"], "source": origin.get("source"), "page_url": origin.get("page_url"),
                         "user": origin.get("user"), "stock_id": origin.get("id")})
        write_json(out.with_name(out.name + ".json"), side)
        rel = str(out.relative_to(d))
        job["sources"][sid] = {"id": sid, "role": "broll", "kind": "broll", "original": str(out), "link": rel,
                               "proxy": rel, "probe": info, "evidence": "keyed by nvc.py key from %s" % (src_id or path.name),
                               "duration": info.get("duration"), "width": info.get("width"), "height": info.get("height"),
                               "hasAudio": False, "hasVideo": True, "alpha": True, "keyed": side}
        rows.append("%s: keyed on %s, %sx%s, %s, %.1f s to key" % (sid, on, info.get("width"), info.get("height"),
                                                                  fmt_dur(info.get("duration")), time.time() - t0))
    save_job(d, job)
    for row in rows:
        print(row)
    print("next: use them in a vox beat (\"kind\": \"clip\", \"source\": ID, no blend needed)")


# ---------------------------------------------------------------- segments from other engines

def cmd_segment(args):
    d = job_dir(args.job)
    job = load_job(d)
    preset = target_preset(job["target"])
    seg_dir = d / "media" / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    sid = slug(args.id or ("%s-%s" % (args.engine, Path(args.project).name)))
    if args.engine == "broll":
        if not BROLL.exists():
            raise NvcError("remotion-broll is not installed")
        out = seg_dir / (sid + ".mp4")
        r = run([sys.executable, BROLL, "render", args.project, "--comp", args.comp or "BrollMinute", "--out", out,
                 "--no-qa"], timeout=3600)
        if r.returncode:
            raise NvcError("remotion-broll render failed: " + (r.stderr or r.stdout).strip()[-600:])
    else:
        hf = shutil.which("hyperframes") or str(Path.home() / ".local" / "bin" / "hyperframes")
        if not Path(hf).exists():
            raise NvcError("the hyperframes CLI is not installed")
        out = seg_dir / (sid + (".webm" if args.alpha else ".mp4"))
        env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", HYPERFRAMES_SKIP_SKILLS="1")
        cmd = [hf, "render", args.project, "--fps", str(job.get("fps") or 30), "--output", out]
        if args.alpha:
            cmd += ["--format", "webm"]
        r = run(cmd, timeout=3600, env=env)
        if r.returncode:
            raise NvcError("hyperframes render failed: " + (r.stderr or r.stdout).strip()[-600:])
    info = probe(out)
    if info.get("width") and (info["width"], info["height"]) != (preset["width"], preset["height"]) and args.engine == "hf":
        log("note: the segment is %dx%d, the edit %dx%d; it will be fitted" % (info["width"], info["height"],
                                                                                preset["width"], preset["height"]))
    if args.alpha and not info.get("alpha"):
        log("note: no alpha channel was found in %s (VP9 alpha is expected)" % out)
    job["sources"][sid] = {"id": sid, "role": "segment", "kind": "segment", "original": str(out),
                           "link": str(out.relative_to(d)), "probe": info, "duration": info.get("duration"),
                           "width": info.get("width"), "height": info.get("height"), "hasAudio": info.get("hasAudio"),
                           "hasVideo": True, "alpha": info.get("alpha", False),
                           "evidence": {"by": "segment", "engine": args.engine, "project": str(args.project)}}
    save_job(d, job)
    print("segment %s: %s, %s. Run nvc.py ingest %s, then place it with an overlay of type segment."
          % (sid, out, fmt_dur(info.get("duration")), args.job))


# ---------------------------------------------------------------- status, doctor

def cmd_status(args):
    d = job_dir(args.job)
    job = load_job(d)
    print("job %s (%s), target %s, dialogue %s" % (job["id"], job.get("title"), job["target"], job.get("dialogue")))
    for sid, s in job["sources"].items():
        print("  %-12s %-16s %s%s" % (sid, s["kind"], fmt_dur(s.get("duration")),
                                      "  proxy" if s.get("proxy") else ""))
    for step, info in (job.get("steps") or {}).items():
        print("  done: %-16s %s" % (step, info.get("at")))
    order = ["ingest", "sync", "transcribe", "compile:" + job["target"], "audio:" + job["target"],
             "render:" + job["target"], "deliver:" + job["target"]]
    for step in order:
        if step not in (job.get("steps") or {}):
            print("next: %s" % step.split(":")[0])
            break


def cmd_doctor(args):
    rows = []

    def row(name, ok, detail=""):
        rows.append((name, ok, detail))

    row("ffmpeg", bool(shutil.which("ffmpeg")), "")
    filters = ffmpeg_filters()
    need = ["loudnorm", "ebur128", "silencedetect", "atrim", "afade", "concat", "setparams", "tile"]
    missing = [f for f in need if f not in filters]
    row("ffmpeg filters", not missing, "missing: " + ", ".join(missing) if missing else "all present")
    nv = node_version()
    row("node", bool(nv and nv >= (22, 6)), "v%d.%d" % nv if nv else "not found (Remotion needs Node 22.6 or newer)")
    if args.setup and not venv_python():
        log("building the skill's Python environment (numpy) in %s" % VENV_DIR)
        run([sys.executable, "-m", "venv", VENV_DIR], timeout=600, check=True)
        run([venv_python(), "-m", "pip", "install", "--quiet", "numpy"], timeout=1800, check=True)
    row("numpy (sync, snapping)", bool(numpy_python()), venv_python() or "run doctor --setup")
    model = whisper_model()
    row("whisper-cli", bool(shutil.which("whisper-cli")), "brew install whisper-cpp")
    row("whisper model", bool(model), model or "set NVC_WHISPER_MODEL to a ggml-large-v3-turbo model file")
    row("swiftc (face positions)", bool(shutil.which("swiftc")), "xcode-select --install")
    row("Gemini key (Bangla transcripts)", bool(gemini_api.key_sources()),
        ", ".join(gemini_api.key_sources()) or "none; see nexa-speech doctor")
    for name, path in (("nexa-sound", SOUND), ("nexa-speech", SPEECH), ("agy-watch-video", WATCH),
                       ("remotion-broll", BROLL)):
        row(name, path.exists(), str(path) if path.exists() else "not installed")
    if args.setup:
        try:
            ensure_renderer(args.link_modules, install=args.npm)
        except NvcError as err:
            row("renderer", False, str(err))
    mods = RENDERER / "node_modules"
    have = (read_json(mods / "remotion" / "package.json") or {}).get("version") if mods.exists() else None
    row("renderer", have == REMOTION_VERSION, "%s (Remotion %s)" % (RENDERER, have) if have else
        "not set up: nvc.py doctor --setup --link-modules PATH")
    row("T7 Shield", T7.exists(), "mounted: renders use it for temp files" if T7.exists() else "not mounted")
    usage = shutil.disk_usage(str(Path.home()))
    row("free disk", usage.free > 20e9, "%.0f GB free on the internal disk" % (usage.free / 1e9))
    width = max(len(r[0]) for r in rows)
    fixes = {"whisper-cli": "brew install whisper-cpp", "swiftc (face positions)": "xcode-select --install"}
    for name, ok, detail in rows:
        if ok and detail == fixes.get(name):
            detail = ""
        print("%s %s %s" % ("ok  " if ok else "MISS", name.ljust(width), detail))
    if args.json:
        print(json.dumps([{"check": n, "ok": o, "detail": t} for n, o, t in rows], indent=1))


# ---------------------------------------------------------------- CLI

def build_parser():
    p = argparse.ArgumentParser(prog="nvc.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=SKILL_VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    targets = list(presets()["targets"])

    s = sub.add_parser("new", help="make a job folder")
    s.add_argument("job")
    s.add_argument("--target", default="youtube", choices=targets)
    s.add_argument("--title")
    s.add_argument("--id")
    s.add_argument("--lang", default="en", help="spoken language: en, bn, or auto for mixed Bangla and English")
    s.add_argument("--fps", type=int, help="output frame rate (default 30)")
    s.add_argument("--brand", help="an accent colour (#RRGGBB) or a theme JSON file")

    s = sub.add_parser("add", help="add media files (linked, never modified)")
    s.add_argument("job")
    s.add_argument("files", nargs="+")
    s.add_argument("--role", choices=ROLES)
    s.add_argument("--id", help="name for a single file")

    s = sub.add_parser("ingest", help="probe, classify, proxies, audio, best microphone, face position")
    s.add_argument("job")
    s.add_argument("--force", action="store_true", help="rebuild proxies and audio")
    s.add_argument("--no-faces", action="store_true")

    s = sub.add_parser("sync", help="offset and drift of every recording against the dialogue")
    s.add_argument("job")
    s.add_argument("--set", action="append", help="SOURCE=SECONDS: set an offset by hand (source time minus master)")

    s = sub.add_parser("clean", help="dialogue clean-up with nexa-sound")
    s.add_argument("job")
    s.add_argument("--isolate", action="store_true", help="Apple voice isolation first")
    s.add_argument("--hum", type=int, choices=(50, 60))

    s = sub.add_parser("transcribe", help="word timings on the master clock")
    s.add_argument("job")
    s.add_argument("--engine", default="auto", choices=("auto", "whisper", "gemini", "agy"))
    s.add_argument("--lang")
    s.add_argument("--model", help="a whisper.cpp ggml model file")

    s = sub.add_parser("brief", help="edit-brief.md for writing the plan")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--style", choices=("vox",), help="vox: add the Vox look, its rules and a beat storyboard")

    s = sub.add_parser("compile", help="verify the plan and build the edit")
    s.add_argument("job")
    s.add_argument("--plan")
    s.add_argument("--target", choices=targets)

    s = sub.add_parser("audio", help="cut, music, effects and the mix")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--music", help="a music file to fit under the edit (overrides the plan)")
    s.add_argument("--no-music", action="store_true")
    s.add_argument("--no-sfx", action="store_true")
    s.add_argument("--budget", type=float, default=1.0, help="most USD to spend on generated music")

    s = sub.add_parser("stills", help="key frames on one contact sheet")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--frames", help="comma-separated frame numbers")

    s = sub.add_parser("render", help="render the video")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--draft", action="store_true", help="half size, fast")
    s.add_argument("--out")

    s = sub.add_parser("qa", help="measured QA and the plan's checks")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--review", action="store_true", help="also the Gemini review with the on-screen lines expected")

    s = sub.add_parser("deliver", help="final files and the delivery report")
    s.add_argument("job")
    s.add_argument("--target", choices=targets)
    s.add_argument("--force", action="store_true", help="deliver even with open QA items")
    s.add_argument("--allow-noncommercial", action="store_true",
                   help="an internal test: deliver even with free-plan ElevenLabs sound in it")

    s = sub.add_parser("segment", help="render a remotion-broll scene or a HyperFrames composition into the job")
    s.add_argument("engine", choices=("broll", "hf"))
    s.add_argument("project", help="the remotion-broll project folder or the HyperFrames project folder")
    s.add_argument("--job", required=True)
    s.add_argument("--comp", help="remotion-broll composition id (default BrollMinute)")
    s.add_argument("--alpha", action="store_true", help="HyperFrames: render VP9 WebM with alpha for an overlay")
    s.add_argument("--id")

    s = sub.add_parser("stock", help="search Pixabay for b-roll and pictures, then pick one into the job")
    s.add_argument("job")
    s.add_argument("query", nargs="?", help="what to find, in English keywords (Pixabay's tags are English)")
    s.add_argument("--type", default="video", choices=sorted(STOCK_TYPES))
    s.add_argument("--n", type=int, default=12, help="candidates on the sheet (default 12)")
    s.add_argument("--orientation", default="auto", choices=("auto", "horizontal", "vertical", "all"))
    s.add_argument("--min-seconds", type=float, help="videos at least this long")
    s.add_argument("--order", default="popular", choices=("popular", "latest"))
    s.add_argument("--lang", help="the query's language code (Pixabay's default is en)")
    s.add_argument("--editors-choice", action="store_true", help="pictures Pixabay's editors picked")
    s.add_argument("--no-ai", action="store_true", help="leave out AI-made stock")
    s.add_argument("--also", action="append", help="another wording of the same need (repeatable; 3 in all is "
                                                     "a good search)")
    s.add_argument("--judge", action="store_true", help="Gemini scores every candidate on the sheet (about a cent)")
    s.add_argument("--slot", help="for the judge: what the shot must show, in a sentence (default: the query)")
    s.add_argument("--use", default="broll", choices=("broll", "ad", "background"), help="for the judge")
    s.add_argument("--market", help="for the judge: the client's market when people or places must fit it")
    s.add_argument("--auto-pick", action="store_true", help="with --judge: add the best accepted candidate")
    s.add_argument("--pick", help="download this Pixabay id (from the sheet) and add it to the job")
    s.add_argument("--id", help="the source id to add it as (default px-ID)")
    s.add_argument("--json", action="store_true")

    s = sub.add_parser("cutout", help="cut subjects out of pictures for Vox beats (halftone people, marker stroke)")
    s.add_argument("job")
    s.add_argument("pictures", nargs="+", help="picture files, or ids of pictures already in the job")
    s.add_argument("--style", default="auto", choices=("auto", "color", "bw", "halftone"),
                   help="auto: people halftone, everything else in colour")
    s.add_argument("--stroke", default="auto", help="auto (the marker red for people), none, or a colour #RRGGBB")
    s.add_argument("--stroke-width", type=float, help="px (default 1.4%% of the subject's longer side)")
    s.add_argument("--offset", help="the stroke's offset DX,DY in px, y down (default up and to the left)")
    s.add_argument("--shadow", default="soft", choices=("soft", "none"))
    s.add_argument("--no-lift", action="store_true", help="the picture is a cut-out already (has transparency)")
    s.add_argument("--largest", action="store_true", help="keep only the biggest subject (one of two trucks)")
    s.add_argument("--id")

    s = sub.add_parser("key", help="make clips shot on black or green transparent for Vox beats")
    s.add_argument("job")
    s.add_argument("clips", nargs="+", help="clip files, or ids of clips already in the job")
    s.add_argument("--on", default="auto", choices=("auto", "black", "green"), help="what the clip was shot on")
    s.add_argument("--start", type=float, help="seconds into the clip to start (default 0)")
    s.add_argument("--seconds", type=float, help="how much to key (default %d s)" % KEY_MAX_S)
    s.add_argument("--max", type=int, default=1280, help="the longest side in px (default 1280)")
    s.add_argument("--id")

    s = sub.add_parser("status", help="what is done and what is next")
    s.add_argument("job")

    s = sub.add_parser("doctor", help="check the machine; --setup builds what is missing")
    s.add_argument("--setup", action="store_true")
    s.add_argument("--link-modules", help="an installed Remotion %s project or its node_modules" % REMOTION_VERSION)
    s.add_argument("--npm", action="store_true", help="install the renderer's packages with npm")
    s.add_argument("--json", action="store_true")
    return p


COMMANDS = {"new": cmd_new, "add": cmd_add, "ingest": cmd_ingest, "sync": cmd_sync, "clean": cmd_clean,
            "transcribe": cmd_transcribe, "brief": cmd_brief, "compile": cmd_compile, "audio": cmd_audio,
            "stills": cmd_stills, "render": cmd_render, "qa": cmd_qa, "deliver": cmd_deliver,
            "segment": cmd_segment, "stock": cmd_stock, "cutout": cmd_cutout, "key": cmd_key, "status": cmd_status,
            "doctor": cmd_doctor}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        COMMANDS[args.cmd](args)
    except NvcError as err:
        die(err)
    except gemini_api.GeminiError as err:
        die("%s (%s)" % (err, err.kind))


if __name__ == "__main__":
    main()
