#!/usr/bin/env python3
"""nexa-remotion kit: make, preview, render and check Remotion videos built from the kit (standard library only).

  nrk.py doctor [--link-modules PATH]                 node, ffmpeg, the shared Remotion 4.0.528 modules and extras
  nrk.py setup                                        install the kit's modules once (npm, pinned) into ~/.nexa-remotion
  nrk.py new PROJECT [--format youtube] [--fps 30] [--seconds 20] [--title T]
                                                      a project from the kit: its library, a starter, linked modules
  nrk.py stills PROJECT [--comp Main] [--frames 0,45,90 | --every 1.5] [--scale 0.5]
                                                      frames of a composition on one labelled contact sheet
  nrk.py still PROJECT --frame 42 [--comp Main]       one full-size PNG (a thumbnail, a close look)
  nrk.py render PROJECT [--comp Main] [--preset web|draft|master|alpha|webm-alpha|gif] [--out FILE]
  nrk.py qa PROJECT [--platform youtube]              measured checks of the last render (agy-watch-video qa)
  nrk.py demos [--module NAME] [--only TEXT]          the kit's demos typechecked and rendered to stills
  nrk.py sync PROJECT                                 the project's copy of the kit library brought up to date

A project is a normal Remotion project: `npx remotion studio` opens it, and everything the kit gives it lives in
`src/kit/`, a copy the project owns. The modules are shared (one install of Remotion 4.0.528 and the extra packages
for every project), linked as `node_modules`.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
KIT = SKILL_DIR / "kit"
KIT_VERSION = "2026.09.26.1"
REMOTION_VERSION = "4.0.528"
NRK_HOME = Path(os.environ.get("NRK_HOME") or (Path.home() / ".nexa-remotion"))
CONFIG = NRK_HOME / "config.json"
GL = os.environ.get("NRK_GL", "angle")          # swangle on a machine without a GPU
MARK = ".nrk-owned"                              # a folder nrk made itself, and so may clear
BASE_MODULES = ["core", "motion"]                # every kit module may import these two, and nothing else
# kit/public folders that components load at run time (key clicks, UI sounds); the rest of kit/public is demo media
RUNTIME_PUBLIC = ["type", "ui"]
WATCH = Path.home() / ".claude" / "skills" / "agy-watch-video" / "scripts" / "watch_video.py"
WATCH_PY = Path.home() / ".claude" / "skills" / "agy-watch-video" / ".venv" / "bin" / "python3"

# What a kit project imports. Every Remotion package must be exactly REMOTION_VERSION.
REQUIRED = ["remotion", "@remotion/cli", "@remotion/media", "@remotion/media-utils", "@remotion/google-fonts",
            "@remotion/transitions", "@remotion/paths", "@remotion/shapes", "@remotion/noise",
            "@remotion/layout-utils", "@remotion/rough-notation", "@remotion/effects", "@remotion/light-leaks",
            "@remotion/starburst", "@remotion/motion-blur", "@remotion/three", "@remotion/lottie",
            "@remotion/captions", "@remotion/sfx", "@remotion/rounded-text-box", "three", "@react-three/fiber",
            "lottie-web", "d3-geo", "d3-scale", "d3-shape", "topojson-client", "world-atlas", "perfect-freehand",
            "react", "react-dom", "typescript"]

# Frame sizes and the safe area where text may go ([x, y, w, h]); the same numbers as nexa-video-creator's
# presets, so a kit scene drops into an nvc edit unchanged.
FORMATS = {
    "youtube": {"width": 1920, "height": 1080, "safe": [96, 54, 1728, 972], "platform": "youtube"},
    "4k": {"width": 3840, "height": 2160, "safe": [192, 108, 3456, 1944], "platform": "youtube"},
    "shorts": {"width": 1080, "height": 1920, "safe": [65, 270, 875, 978], "platform": "shorts"},
    "reels": {"width": 1080, "height": 1920, "safe": [65, 270, 875, 978], "platform": "reels"},
    "tiktok": {"width": 1080, "height": 1920, "safe": [65, 270, 875, 978], "platform": "tiktok"},
    "story": {"width": 1080, "height": 1920, "safe": [65, 270, 950, 978], "platform": "reels"},
    "feed": {"width": 1080, "height": 1350, "safe": [54, 68, 972, 1215], "platform": "facebook"},
    "square": {"width": 1080, "height": 1080, "safe": [54, 54, 972, 972], "platform": "generic"},
}

# Render presets: what each is for and the flags it adds (the GL flag is added to every render).
PRESETS = {
    "web": {"why": "delivery for YouTube and social: H.264, CRF 18, BT.709, AAC 320k", "ext": ".mp4", "args": [
        "--codec=h264", "--crf=18", "--pixel-format=yuv420p", "--color-space=bt709", "--image-format=jpeg",
        "--jpeg-quality=95", "--audio-codec=aac", "--audio-bitrate=320k"]},
    "upload": {"why": "the file to upload to YouTube or Vimeo: H.264 CRF 12, so flat colour, thin lines and small type survive "
               "the platform's re-encode (flat graphics at CRF 18 came out near 2 Mbps; YouTube asks about 8 for 1080p)",
               "ext": ".mp4", "args": [
        "--codec=h264", "--crf=12", "--pixel-format=yuv420p", "--color-space=bt709", "--image-format=jpeg",
        "--jpeg-quality=100", "--audio-codec=aac", "--audio-bitrate=320k"]},
    "draft": {"why": "a fast look: half size, CRF 28", "ext": ".mp4", "args": [
        "--codec=h264", "--crf=28", "--scale=0.5", "--color-space=bt709", "--image-format=jpeg",
        "--jpeg-quality=80"]},
    "master": {"why": "a master for another editor: ProRes 422 HQ from PNG frames", "ext": ".mov", "args": [
        "--codec=prores", "--prores-profile=hq", "--image-format=png", "--color-space=bt709"]},
    "alpha": {"why": "a transparent overlay for an editor: ProRes 4444 with alpha", "ext": ".mov", "args": [
        "--codec=prores", "--prores-profile=4444", "--pixel-format=yuva444p10le", "--image-format=png"]},
    "webm-alpha": {"why": "a transparent overlay for the web or another Remotion project: VP9 with alpha",
                   "ext": ".webm", "args": ["--codec=vp9", "--pixel-format=yuva420p", "--image-format=png"]},
    "gif": {"why": "a GIF: every second frame, no sound", "ext": ".gif", "args": [
        "--codec=gif", "--every-nth-frame=2"]},
}


class NrkError(Exception):
    pass


def log(msg):
    print("[nrk %s] %s" % (time.strftime("%H:%M:%S"), msg), file=sys.stderr)


def run(cmd, cwd=None, timeout=3600):
    cmd = [str(c) for c in cmd]
    try:
        p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, timeout=timeout, capture_output=True)
    except FileNotFoundError:
        raise NrkError("not installed: " + cmd[0])
    except subprocess.TimeoutExpired:
        raise NrkError("timed out after %d s: %s" % (timeout, " ".join(cmd[:4])))
    p.stdout = p.stdout.decode("utf-8", "replace")
    p.stderr = p.stderr.decode("utf-8", "replace")
    return p


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def clock(seconds):
    return "%d:%04.1f" % (seconds // 60, seconds % 60)


# ---------------------------------------------------------------- the shared modules

def package_version(modules, name):
    return (read_json(Path(modules) / name / "package.json") or {}).get("version")


def modules_report(modules):
    """({package: version or None}, [problems]) for every package a kit project needs."""
    found = {name: package_version(modules, name) for name in REQUIRED}
    problems = []
    for name, ver in found.items():
        if ver is None:
            problems.append("%s is missing" % name)
        elif (name == "remotion" or name.startswith("@remotion/")) and ver != REMOTION_VERSION:
            problems.append("%s is %s; every Remotion package must be %s" % (name, ver, REMOTION_VERSION))
    return found, problems


def as_modules(path):
    p = Path(path).expanduser()
    return p if p.name == "node_modules" else p / "node_modules"


def find_modules():
    """The shared node_modules: NRK_MODULES, then the saved path, then the one `setup` installs."""
    candidates = [os.environ.get("NRK_MODULES"), (read_json(CONFIG) or {}).get("modules"), NRK_HOME / "modules"]
    for c in candidates:
        if not c:
            continue
        p = as_modules(c)
        if (p / "remotion" / "package.json").exists():
            return p.resolve()
    return None


def link_modules(project):
    mods = find_modules()
    if not mods:
        raise NrkError("no shared modules: run `nrk.py setup` (installs them), or `nrk.py doctor --link-modules "
                       "PATH` with an installed Remotion %s project" % REMOTION_VERSION)
    link = Path(project) / "node_modules"
    if link.is_symlink():
        if link.resolve() == mods:
            return link
        link.unlink()
    elif link.exists():
        return link              # the project has its own install: leave it alone
    os.symlink(mods, link)
    return link


# ---------------------------------------------------------------- projects

def project_dir(path, must_exist=True):
    d = Path(path).expanduser().resolve()
    if must_exist and not (d / "project.json").exists():
        raise NrkError("%s is not a kit project (no project.json): make one with `nrk.py new %s`" % (d, path))
    return d


def kit_modules():
    return sorted(p.name for p in (KIT / "src" / "kit").iterdir() if p.is_dir())


def copy_tree(src, dest):
    if dest.exists():
        raise NrkError("%s already exists" % dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns(".DS_Store", "*.tmp"))


def copy_runtime_public(project):
    """The sounds and files kit components load at run time, into the project's public/ (never over its own)."""
    copied = []
    for name in RUNTIME_PUBLIC:
        src = KIT / "public" / name
        if not src.is_dir():
            continue
        for f in src.rglob("*"):
            if f.is_file() and f.name != ".DS_Store":
                dest = Path(project) / "public" / name / f.relative_to(src)
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dest)
                    copied.append(str(dest.relative_to(project)))
    return copied


def cmd_new(args):
    d = project_dir(args.project, must_exist=False)
    if (d / "project.json").exists():
        raise NrkError("%s is a kit project already; use it or pick another folder" % d)
    if d.exists() and any(d.iterdir()):
        raise NrkError("%s exists and is not empty; pick a new folder" % d)
    fmt = FORMATS[args.format]
    d.mkdir(parents=True, exist_ok=True)
    for name in ("package.json", "tsconfig.json", "remotion.config.ts"):
        shutil.copy2(KIT / name, d / name)
    pkg = read_json(d / "package.json")
    pkg["name"] = re.sub(r"[^a-z0-9-]+", "-", d.name.lower()).strip("-") or "video"
    write_json(d / "package.json", pkg)
    (d / ".gitignore").write_text("node_modules\nout\n", encoding="utf-8")
    for sub in ("src", "public", "out"):
        (d / sub).mkdir(exist_ok=True)
    copy_tree(KIT / "src" / "kit", d / "src" / "kit")
    copy_runtime_public(d)
    frames = int(round(float(args.seconds) * args.fps))
    shutil.copy2(KIT / "src" / "index.ts", d / "src" / "index.ts")
    root = (KIT / "starter" / "Root.tsx").read_text(encoding="utf-8")
    for key, val in (("__WIDTH__", fmt["width"]), ("__HEIGHT__", fmt["height"]), ("__FPS__", args.fps),
                     ("__FRAMES__", frames)):
        root = root.replace(key, str(val))
    (d / "src" / "Root.tsx").write_text(root, encoding="utf-8")
    shutil.copy2(KIT / "starter" / "Main.tsx", d / "src" / "Main.tsx")
    meta = {"schema": "nrk-project/1", "title": args.title or d.name, "format": args.format,
            "width": fmt["width"], "height": fmt["height"], "safe": fmt["safe"], "fps": args.fps,
            "seconds": float(args.seconds), "frames": frames, "kit_version": KIT_VERSION, "created": now()}
    write_json(d / "project.json", meta)
    link_modules(d)
    print("project %s: %s %dx%d, %d fps, %.1f s (%d frames)" % (d, args.format, fmt["width"], fmt["height"],
                                                               args.fps, float(args.seconds), frames))
    print("next: write the video in src/Main.tsx with the kit (src/kit), then `nrk.py stills %s`" % args.project)


def cmd_sync(args):
    d = project_dir(args.project)
    lib = d / "src" / "kit"
    if lib.exists():
        keep = d / "src" / ("kit.before-sync-" + time.strftime("%Y%m%d-%H%M%S"))
        shutil.move(str(lib), str(keep))
        print("kept the old library at %s (any edits the project made are there)" % keep)
    copy_tree(KIT / "src" / "kit", lib)
    added = copy_runtime_public(d)
    if added:
        print("added %d runtime file(s) to public/" % len(added))
    meta = read_json(d / "project.json")
    meta["kit_version"] = KIT_VERSION
    write_json(d / "project.json", meta)
    print("library updated to kit %s" % KIT_VERSION)


# ---------------------------------------------------------------- stills, render, qa

def remotion(project, argv, timeout=3600):
    link_modules(project)
    r = run(["npx", "remotion"] + argv, cwd=project, timeout=timeout)
    if r.returncode:
        raise NrkError("remotion %s failed: %s" % (argv[0], (r.stderr or r.stdout).strip()[-2000:]))
    return r


def parse_compositions(text):
    """{id: (durationInFrames, fps, width, height)} from the table `remotion compositions` prints. A one-frame
    composition is listed as `Id  1920x1080  Still`, without fps or length."""
    comps = {}
    for line in text.splitlines():
        m = re.match(r"^(\S+)\s+(?:(\d+(?:\.\d+)?)\s+)?(\d+)x(\d+)\s+(?:(\d+)\s+\(|Still\b)", line.strip())
        if m:
            fps = float(m.group(2)) if m.group(2) else 30.0
            frames = int(m.group(5)) if m.group(5) else 1
            comps[m.group(1)] = (frames, fps, int(m.group(3)), int(m.group(4)))
    return comps


def list_compositions(project):
    # the table is printed at the info log level: --log=error hides it
    r = remotion(project, ["compositions", "src/index.ts"], timeout=900)
    return parse_compositions(r.stdout)


def pick_frames(frames, fps, every=None, given=None):
    """The frames to look at: the given ones, or one every `every` s (default: about 12), always the last."""
    if given:
        return sorted({max(0, min(frames - 1, int(x))) for x in str(given).split(",") if x.strip()})
    step = max(1, int(round((every or max(0.5, frames / fps / 12.0)) * fps)))
    out = list(range(0, frames, step))
    if frames - 1 not in out:
        out.append(frames - 1)
    return out


SHEET_PY = r'''
import sys, json
from PIL import Image, ImageDraw
spec = json.loads(sys.argv[1])
imgs = [Image.open(p).convert("RGB") for p in spec["images"]]
w = spec["width"]; h = int(round(w * imgs[0].height / imgs[0].width)); cols = spec["cols"]
rows = -(-len(imgs) // cols)
strip = 20  # the label sits under each frame, never over it (a label on the frame hides the safe-area corner)
sheet = Image.new("RGB", (cols * (w + 6) + 6, rows * (h + strip + 6) + 6), "white")
d = ImageDraw.Draw(sheet)
for i, (im, t) in enumerate(zip(imgs, spec["labels"])):
    x, y = 6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + strip + 6)
    sheet.paste(im.resize((w, h)), (x, y))
    if spec.get("safe"):
        k = w / im.width
        sx, sy, sw, sh = spec["safe"]
        d.rectangle([x + sx * k, y + sy * k, x + (sx + sw) * k, y + (sy + sh) * k], outline=(255, 0, 90), width=2)
    d.rectangle([x, y + h, x + w, y + h + strip], fill="black")
    d.text((x + 5, y + h + 4), t, fill="white")
sheet.save(spec["out"], quality=90)
'''


def contact_sheet(images, labels, out, safe=None):
    """One image of every frame with its label (Pillow from agy-watch-video's venv; plain ffmpeg tiles without).
    With `safe` ([x, y, w, h] in source px) each frame carries the safe-area box."""
    portrait = False
    cols = 4 if len(images) > 9 else 3
    width = 480
    probe = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                 "-of", "csv=p=0", images[0]])
    if probe.returncode == 0 and "," in probe.stdout:
        w, h = [int(x) for x in probe.stdout.strip().split(",")[:2]]
        portrait = h > w
    if portrait:
        cols, width = (6 if len(images) > 10 else 4), 270
    if WATCH_PY.exists():
        spec = {"images": [str(p) for p in images], "labels": labels, "out": str(out), "width": width, "cols": cols,
                "safe": safe}
        if run([WATCH_PY, "-c", SHEET_PY, json.dumps(spec)], timeout=600).returncode == 0:
            return out
    rows = -(-len(images) // cols)
    r = run(["ffmpeg", "-y", "-v", "error", "-pattern_type", "glob", "-i", str(Path(images[0]).parent / "*.jpeg"),
             "-vf", "scale=%d:-1,tile=%dx%d:padding=6:color=white" % (width, cols, rows), "-frames:v", "1", out])
    if r.returncode:
        raise NrkError("contact sheet failed: " + r.stderr[-400:])
    return out


def safe_box(d, width, height):
    """The safe area of a project's format ([x, y, w, h]), or of the first format with this frame size."""
    fmt = FORMATS.get((read_json(d / "project.json") or {}).get("format"))
    if fmt and (fmt["width"], fmt["height"]) == (width, height):
        return fmt["safe"]
    return next((f["safe"] for f in FORMATS.values() if (f["width"], f["height"]) == (width, height)), None)


def render_stills(d, comp, frames_given=None, every=None, scale=None, comps=None, guides=False):
    comps = comps or list_compositions(d)
    if comp not in comps:
        raise NrkError("no composition %s in %s (there are: %s)" % (comp, d, ", ".join(sorted(comps)) or "none"))
    frames, fps = comps[comp][0], comps[comp][1]
    picks = pick_frames(frames, fps, every, frames_given)
    outdir = d / "out" / "stills" / comp
    outdir.mkdir(parents=True, exist_ok=True)
    for p in outdir.glob("*.jpeg"):
        p.unlink()                    # the stills this command wrote last time
    # relative: Remotion rejects an image-sequence folder whose path has a dot anywhere (".nexa-remotion")
    argv = ["render", "src/index.ts", comp, os.path.relpath(outdir, d), "--sequence",
            "--frames=" + ",".join(map(str, picks)),
            "--image-format=jpeg", "--jpeg-quality=88", "--gl=" + GL, "--log=error"]
    if scale:
        argv.append("--scale=%s" % scale)
    t0 = time.time()
    remotion(d, argv)
    images = sorted(outdir.glob("*.jpeg"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
    if not images:
        raise NrkError("the render wrote no stills into %s" % outdir)
    labels = ["%s  f%d" % (clock(f / fps), f) for f in picks][:len(images)]
    safe = None
    if guides:
        probe = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                     "-of", "csv=p=0", images[0]])
        if probe.returncode == 0 and "," in probe.stdout:
            w, h = [int(x) for x in probe.stdout.strip().split(",")[:2]]
            box = safe_box(d, int(round(w / (scale or 1))), int(round(h / (scale or 1))))
            safe = [v * (scale or 1) for v in box] if box else None
    sheet = contact_sheet(images, labels, d / "out" / ("%s-stills.jpg" % comp), safe)
    return {"comp": comp, "frames": picks, "sheet": str(sheet), "folder": str(outdir),
            "took_s": round(time.time() - t0, 1)}


def cmd_stills(args):
    d = project_dir(args.project)
    print(json.dumps(render_stills(d, args.comp, args.frames, args.every, args.scale, guides=args.guides), indent=1))


def cmd_still(args):
    d = project_dir(args.project)
    out = d / "out" / ("%s-%d.png" % (args.comp, args.frame))
    remotion(d, ["still", "src/index.ts", args.comp, str(out), "--frame=%d" % args.frame, "--image-format=png",
                 "--gl=" + GL, "--log=error"])
    print(json.dumps({"still": str(out)}, indent=1))


def cmd_render(args):
    d = project_dir(args.project)
    preset = PRESETS[args.preset]
    out = Path(args.out).expanduser().resolve() if args.out else \
        d / "out" / ("%s-%s%s" % (d.name, args.comp.lower(), preset["ext"]))
    argv = ["render", "src/index.ts", args.comp, str(out)] + preset["args"] + ["--gl=" + GL, "--log=error"]
    if args.concurrency:
        argv.append("--concurrency=%d" % args.concurrency)
    t0 = time.time()
    remotion(d, argv, timeout=6 * 3600)
    took = time.time() - t0
    meta = read_json(d / "project.json")
    meta.setdefault("renders", []).append({"file": str(out), "preset": args.preset, "comp": args.comp,
                                           "seconds": round(took, 1), "at": now()})
    write_json(d / "project.json", meta)
    print(json.dumps({"video": str(out), "preset": args.preset, "render_s": round(took, 1),
                      "size_mb": round(out.stat().st_size / 1e6, 1) if out.exists() else None}, indent=1))
    print("next: nrk.py qa %s" % args.project)


def cmd_qa(args):
    d = project_dir(args.project)
    meta = read_json(d / "project.json")
    renders = [r for r in meta.get("renders") or [] if Path(r["file"]).exists()]
    if not renders:
        raise NrkError("render first: nrk.py render %s" % args.project)
    video = renders[-1]["file"]
    platform = args.platform or FORMATS.get(meta.get("format"), {}).get("platform", "generic")
    if not WATCH.exists():
        raise NrkError("agy-watch-video is not installed (its qa measures the render)")
    r = run([sys.executable, WATCH, "qa", video, "--platform", platform], timeout=1800)
    sys.stdout.write(r.stdout[-8000:])
    if r.returncode:
        raise NrkError("qa failed: " + r.stderr[-600:])


# ---------------------------------------------------------------- the kit's own check

ONE_MODULE_ROOT = """import React from 'react';
import {Composition} from 'remotion';
import {demos} from './demos/%s';

export const RemotionRoot: React.FC = () => (
\t<>
\t\t{demos.map((d) => (
\t\t\t<Composition
\t\t\t\tkey={d.id}
\t\t\t\tid={d.id}
\t\t\t\tcomponent={d.component}
\t\t\t\twidth={d.width ?? 1920}
\t\t\t\theight={d.height ?? 1080}
\t\t\t\tfps={d.fps ?? 30}
\t\t\t\tdurationInFrames={d.durationInFrames}
\t\t\t/>
\t\t))}
\t</>
);
"""


def check_dir(name):
    """NRK_HOME/kit-check/NAME, a folder only nrk writes to; its src and stills are made fresh each time."""
    work = NRK_HOME / "kit-check" / name
    if work.exists() and not (work / MARK).exists():
        raise NrkError("%s exists but nrk did not make it; move it away first" % work)
    # src and public are copied fresh each time; out keeps every demo's last sheet (each demo clears its own stills)
    for sub in ("src", "public"):
        p = work / sub
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p)
    work.mkdir(parents=True, exist_ok=True)
    (work / MARK).write_text("made by nrk.py demos; nrk clears src and public here\n", encoding="utf-8")
    return work


def build_check(module=None):
    work = check_dir(module or "all")
    for name in ("package.json", "tsconfig.json", "remotion.config.ts"):
        shutil.copy2(KIT / name, work / name)
    if (KIT / "public").is_dir():
        copy_tree(KIT / "public", work / "public")
    if module is None:
        copy_tree(KIT / "src", work / "src")
    else:
        if module not in kit_modules():
            raise NrkError("no kit module %s (there are: %s)" % (module, ", ".join(kit_modules())))
        if not (KIT / "src" / "demos" / (module + ".tsx")).exists():
            raise NrkError("module %s has no demos file (src/demos/%s.tsx)" % (module, module))
        for m in dict.fromkeys(BASE_MODULES + [module]):
            copy_tree(KIT / "src" / "kit" / m, work / "src" / "kit" / m)
        (work / "src" / "demos").mkdir(parents=True)
        shutil.copy2(KIT / "src" / "demos" / (module + ".tsx"), work / "src" / "demos" / (module + ".tsx"))
        shutil.copy2(KIT / "src" / "index.ts", work / "src" / "index.ts")
        (work / "src" / "Root.tsx").write_text(ONE_MODULE_ROOT % module, encoding="utf-8")
    write_json(work / "project.json", {"schema": "nrk-project/1", "title": "kit check " + (module or "all"),
                                       "format": "youtube", "kit_version": KIT_VERSION, "created": now()})
    link_modules(work)
    return work


def cmd_demos(args):
    """Typecheck the kit (or one module with core and motion) and render every demo to a contact sheet."""
    work = build_check(args.module)
    tsc = run(["npx", "tsc", "--noEmit", "-p", "."], cwd=work, timeout=900)
    if tsc.returncode:
        raise NrkError("the kit does not typecheck:\n" + (tsc.stdout + tsc.stderr)[-4000:])
    comps = list_compositions(work)
    ids = sorted(comps)
    if args.only:
        ids = [i for i in ids if args.only.lower() in i.lower()]
    if not ids:
        raise NrkError("no demos matched")
    results = []
    for comp in ids:
        try:
            r = render_stills(work, comp, every=args.every, scale=args.scale, comps=comps)
            results.append({"demo": comp, "ok": True, "sheet": r["sheet"], "took_s": r["took_s"]})
        except NrkError as err:
            results.append({"demo": comp, "ok": False, "error": str(err)[-600:]})
    print(json.dumps({"module": args.module or "all", "demos": results, "folder": str(work / "out")}, indent=1))
    failed = [r["demo"] for r in results if not r["ok"]]
    if failed:
        raise NrkError("%d demo(s) failed: %s" % (len(failed), ", ".join(failed)))


# ---------------------------------------------------------------- doctor, setup

def cmd_doctor(args):
    if args.link_modules:
        p = as_modules(args.link_modules).resolve()
        if not (p / "remotion" / "package.json").exists():
            raise NrkError("%s has no Remotion install" % p)
        cfg = read_json(CONFIG) or {}
        cfg["modules"] = str(p)
        write_json(CONFIG, cfg)
        print("shared modules: %s" % p)
    rows = []  # (name, ok, what was found, how to fix, needed)
    ver = run(["node", "--version"]).stdout.strip() if shutil.which("node") else ""
    rows.append(("node 18 or newer", bool(re.match(r"v(1[89]|[2-9]\d)", ver)), ver, "brew install node", True))
    ff = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
    rows.append(("ffmpeg and ffprobe", ff, shutil.which("ffmpeg") or "", "brew install ffmpeg", True))
    mods = find_modules()
    rows.append(("shared modules", bool(mods), str(mods or ""), "nrk.py setup", True))
    if mods:
        found, problems = modules_report(mods)
        rows.append(("Remotion %s and the kit's packages" % REMOTION_VERSION, not problems,
                     "%d packages" % len(found), "; ".join(problems) + " (nrk.py setup)", True))
    rows.append(("agy-watch-video (for qa)", WATCH.exists(), "", "install the agency skills", False))
    rows.append(("labelled contact sheets (Pillow)", WATCH_PY.exists(), "", "agy-watch-video doctor --setup", False))
    for name, ok, found, fix, _ in rows:
        print("%s %-44s %s" % ("ok  " if ok else "FIX ", name, found if ok else fix))
    if not all(ok for _, ok, _, _, needed in rows if needed):
        sys.exit(1)


def cmd_setup(args):
    target = NRK_HOME / "modules"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT / "package.json", target / "package.json")
    log("npm install into %s (about 700 MB, a few minutes)" % target)
    r = run(["npm", "install", "--no-audit", "--no-fund"], cwd=target, timeout=3600)
    if r.returncode:
        raise NrkError("npm install failed: " + (r.stderr or r.stdout)[-1500:])
    cfg = read_json(CONFIG) or {}
    cfg["modules"] = str(target / "node_modules")
    write_json(CONFIG, cfg)
    print("shared modules: %s" % (target / "node_modules"))


# ---------------------------------------------------------------- main

def build_parser():
    p = argparse.ArgumentParser(prog="nrk.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version="nexa-remotion kit " + KIT_VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("doctor", help="check the machine; --link-modules sets the shared modules")
    s.add_argument("--link-modules", help="an installed Remotion %s project or its node_modules" % REMOTION_VERSION)
    sub.add_parser("setup", help="install the kit's modules into ~/.nexa-remotion/modules")
    s = sub.add_parser("new", help="a project from the kit")
    s.add_argument("project")
    s.add_argument("--format", default="youtube", choices=sorted(FORMATS))
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--seconds", type=float, default=20)
    s.add_argument("--title")
    s = sub.add_parser("stills", help="frames on a labelled contact sheet")
    s.add_argument("project")
    s.add_argument("--comp", default="Main")
    s.add_argument("--frames", help="comma-separated frame numbers")
    s.add_argument("--every", type=float, help="seconds between frames (default: about 12 over the length)")
    s.add_argument("--scale", type=float)
    s.add_argument("--guides", action="store_true", help="draw the format's safe area on every frame of the sheet")
    s = sub.add_parser("still", help="one full-size PNG")
    s.add_argument("project")
    s.add_argument("--frame", type=int, required=True)
    s.add_argument("--comp", default="Main")
    s = sub.add_parser("render", help="render a composition")
    s.add_argument("project")
    s.add_argument("--comp", default="Main")
    s.add_argument("--preset", default="web", choices=sorted(PRESETS))
    s.add_argument("--out")
    s.add_argument("--concurrency", type=int)
    s = sub.add_parser("qa", help="measured checks of the last render")
    s.add_argument("project")
    s.add_argument("--platform")
    s = sub.add_parser("demos", help="typecheck the kit and render its demos to stills")
    s.add_argument("--module", help="one module (with core and motion) instead of the whole kit")
    s.add_argument("--only", help="only demos whose id contains this")
    s.add_argument("--every", type=float, default=0.5)
    s.add_argument("--scale", type=float, default=0.5)
    s = sub.add_parser("sync", help="update a project's copy of the kit library")
    s.add_argument("project")
    return p


COMMANDS = {"doctor": cmd_doctor, "setup": cmd_setup, "new": cmd_new, "stills": cmd_stills, "still": cmd_still,
            "render": cmd_render, "qa": cmd_qa, "demos": cmd_demos, "sync": cmd_sync}


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        COMMANDS[args.cmd](args)
    except NrkError as err:
        print("nrk: %s" % err, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
