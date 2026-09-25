#!/usr/bin/env python3
"""remotion-broll: start, check, preview and render explainer B-roll from the kit (Remotion 4, 1920x1080, 30 fps).

  broll.py new DIR [--link-modules PATH] [--no-install]    copy the kit into DIR and install it
  broll.py check DIR [--locale US]                         typecheck, then lint every word on screen
  broll.py stills DIR [--comp BrollMinute] [--frames ...]  still frames and one contact sheet to look at
  broll.py render DIR [--comp BrollMinute] [--out FILE]    render, time it, and run the measured QA
  broll.py review DIR VIDEO                                the Gemini review for a client final

Measured on the kit (2026-09-25, Mac Studio): 16 stills of the minute in 5 s, the 60 s render in 45 s, the QA in 2 s,
the Gemini review in about 5 minutes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKILL_VERSION = "2026.09.25.1"
KIT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "template"
SKILLS = Path(os.environ.get("CLAUDE_SKILLS_DIR") or Path.home() / ".claude" / "skills")
DESIGN = SKILLS / "codex-design" / "scripts" / "design.py"
WATCH = SKILLS / "agy-watch-video" / "scripts" / "watch_video.py"
IGNORE = shutil.ignore_patterns("node_modules", "out", ".DS_Store", "*.log")

# roles for the copy lint: what each line of copy.ts is on screen
ROLES = {"stat.title": "headline", "stat.result": "key_fact", "caption.first": "headline", "caption.next": "headline",
         "steps": "headline", "bars.title": "headline", "end.words": "headline", "end.button": "cta"}
JOINED = {"first", "next", "words", "title"}   # word lists shown as one line
SKIPPED = {"firstKey", "nextKey"}              # the words that get an underline, already in their line


def log(msg: str) -> None:
    print(f"[remotion-broll {time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"remotion-broll: {msg}", file=sys.stderr)
    sys.exit(code)


def run(cmd: list, cwd: Path, timeout: float = 1800) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], cwd=str(cwd), capture_output=True, text=True, timeout=timeout)


def project(path: str) -> Path:
    d = Path(path).expanduser().resolve()
    if not (d / "src" / "Root.tsx").exists():
        die(f"{d} is not a kit project (no src/Root.tsx); start one with: broll.py new {path}")
    return d


def kit_remotion_version() -> str:
    return json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))["dependencies"]["remotion"]


def cmd_new(args) -> None:
    """A new project from the kit. The folder must be new or empty: nothing is overwritten."""
    dest = Path(args.dir).expanduser().resolve()
    if dest.exists() and any(dest.iterdir()):
        die(f"{dest} is not empty; pick a new folder (nothing was changed)")
    t0 = time.time()
    shutil.copytree(TEMPLATE, dest, ignore=IGNORE, dirs_exist_ok=True)
    log(f"copied the kit to {dest}")
    if args.link_modules:
        mods = Path(args.link_modules).expanduser().resolve()
        mods = mods if mods.name == "node_modules" else mods / "node_modules"
        pkg = mods / "remotion" / "package.json"
        if not pkg.exists():
            die(f"no Remotion in {mods}; install instead (leave out --link-modules)")
        have, want = json.loads(pkg.read_text(encoding="utf-8")).get("version"), kit_remotion_version()
        if have != want:
            die(f"{mods} has Remotion {have}, the kit needs {want}; install instead (leave out --link-modules)")
        os.symlink(mods, dest / "node_modules")
        log(f"linked node_modules from {mods} (Remotion {have})")
    elif not args.no_install:
        if not shutil.which("npm"):
            die("npm was not found: install Node.js 22.6 or newer, then run npm ci in the project")
        log("npm ci (about a minute the first time; the npm cache makes the next ones quick)")
        r = run(["npm", "ci", "--prefer-offline", "--no-audit", "--no-fund"], dest)
        if r.returncode:
            die(f"npm ci failed: {(r.stderr or r.stdout).strip()[-600:]}")
    print(json.dumps({"ok": True, "project": str(dest), "seconds": round(time.time() - t0, 1), "next": [
        "edit src/copy.ts (every word on screen) and src/theme.ts (fonts, colours)",
        "set scene lengths in src/Part2.tsx and src/BrollDemo.tsx to the voice-over",
        f"python3 {Path(__file__).resolve()} check {dest}",
        f"python3 {Path(__file__).resolve()} stills {dest}",
        f"python3 {Path(__file__).resolve()} render {dest}"]}, indent=2))


def copy_lines(copy: dict) -> list:
    """copy.ts as the lines a viewer reads, each with a role for the copy lint."""
    out: list = []

    def walk(node, path: str, key: str) -> None:
        if key in SKIPPED:
            return
        role = ROLES.get(path) or ROLES.get(path.split(".")[0]) or "label"
        if isinstance(node, str):
            out.append({"role": role, "text": node})
        elif isinstance(node, list) and node and all(isinstance(x, str) for x in node) and key in JOINED:
            out.append({"role": role, "text": " ".join(node)})
        elif isinstance(node, list):
            for x in node:
                if isinstance(x, list) and all(isinstance(y, str) for y in x):
                    out.append({"role": role, "text": " ".join(x)})
                elif isinstance(x, dict) and "label" in x:
                    out.append({"role": role, "text": x["label"]})
                elif isinstance(x, str):
                    out.append({"role": role, "text": x})
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else k, k)
    walk(copy, "", "")
    return out


def read_copy(d: Path) -> dict | None:
    """COPY from src/copy.ts, through Node's TypeScript support (Node 22.6 or newer); None when Node cannot."""
    node = shutil.which("node")
    if not node:
        return None
    js = ('import(process.argv[1]).then(m => console.log(JSON.stringify(m.COPY)))'
          '.catch(e => { console.error(e.message); process.exit(1); })')
    r = run([node, "--experimental-strip-types", "--no-warnings", "--input-type=module", "-e", js,
             (d / "src" / "copy.ts").as_uri()], d, timeout=60)
    if r.returncode:
        log(f"could not read src/copy.ts with node ({(r.stderr or '').strip()[-200:]})")
        return None
    return json.loads(r.stdout)


def cmd_check(args) -> None:
    """The typecheck, then every word on screen through the copy lint (codex-design's copylint)."""
    d = project(args.dir)
    rep: dict = {}
    r = run(["npx", "tsc", "--noEmit"], d, timeout=300)
    rep["typecheck"] = "ok" if r.returncode == 0 else (r.stdout or r.stderr).strip()[-1500:]
    copy = read_copy(d)
    if copy is None:
        rep["copy_lint"] = "skipped: Node 22.6 or newer reads src/copy.ts; lint copy/onscreen.json by hand"
    else:
        deck = {"locale": args.locale, "platform": "youtube", "strings": copy_lines(copy)}
        path = d / "copy" / "onscreen.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(deck, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        if DESIGN.exists():
            lint = run([sys.executable, DESIGN, "copylint", "--copy", path], d, timeout=120)
            tail = [x for x in (lint.stdout or "").splitlines() if x.strip()]
            rep["copy_lint"] = {"file": str(path), "exit": lint.returncode, "findings": tail[:-1][:20],
                                "summary": json.loads(tail[-1]) if tail and tail[-1].startswith("{") else None}
        else:
            rep["copy_lint"] = f"wrote {path}; codex-design is not installed, so it was not linted"
    ok = rep["typecheck"] == "ok" and not (isinstance(rep["copy_lint"], dict) and rep["copy_lint"]["exit"] == 2)
    print(json.dumps(dict(ok=ok, **rep), indent=2, ensure_ascii=False))
    if not ok:
        sys.exit(2)


def comp_frames(root: str, comp: str) -> int | None:
    """durationInFrames of a composition in Root.tsx."""
    for block in re.findall(r"<Composition\b.*?/>", root, re.S):
        if re.search(rf'\bid="{re.escape(comp)}"', block):
            m = re.search(r"durationInFrames=\{(\d+)\}", block)
            return int(m.group(1)) if m else None
    return None


def cmd_stills(args) -> None:
    """Still frames across a composition, tiled into one sheet: one look at the whole piece in about 5 s."""
    d = project(args.dir)
    if args.frames:
        frames = [int(x) for x in args.frames.split(",") if x.strip()]
    else:
        n = comp_frames((d / "src" / "Root.tsx").read_text(encoding="utf-8"), args.comp)
        if not n:
            die(f"no composition {args.comp} in src/Root.tsx")
        frames = sorted({min(n - 1, int((i + 0.5) * n / 16)) for i in range(16)})
    out = d / "out" / f"stills-{args.comp}"
    for old in out.glob("element-*.png"):  # the stills this command wrote before; nothing else is touched
        old.unlink()
    t0 = time.time()
    r = run(["npx", "remotion", "render", args.comp, out, f"--frames={','.join(map(str, frames))}",
             "--image-format=png", "--log=error"], d, timeout=900)
    if r.returncode:
        die(f"stills failed: {(r.stderr or r.stdout).strip()[-800:]}")
    sheet = d / "out" / f"stills-{args.comp}.png"
    if shutil.which("ffmpeg"):
        cols = 4 if len(frames) > 9 else 3
        rows = -(-len(frames) // cols)
        s = run(["ffmpeg", "-y", "-loglevel", "error", "-pattern_type", "glob", "-i", str(out / "*.png"), "-vf",
                 f"scale=480:270,tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", sheet], d)
        if s.returncode:
            sheet = None
    print(json.dumps({"ok": True, "frames": frames, "folder": str(out), "sheet": str(sheet) if sheet else None,
                      "seconds": round(time.time() - t0, 1)}, indent=2))


def cmd_render(args) -> None:
    """Render one composition, time it, and run agy-watch-video's measured QA (ffmpeg only, about 2 s)."""
    d = project(args.dir)
    out = Path(args.out) if args.out else Path("out") / f"{args.comp}.mp4"
    t0 = time.time()
    r = run(["npx", "remotion", "render", args.comp, out, "--log=error"], d, timeout=3600)
    if r.returncode:
        die(f"render failed: {(r.stderr or r.stdout).strip()[-800:]}")
    rep = {"ok": True, "video": str((d / out).resolve()), "render_seconds": round(time.time() - t0, 1)}
    if WATCH.exists() and not args.no_qa:
        q = run([sys.executable, WATCH, "qa", d / out, "--platform", "youtube"], d, timeout=600)
        try:
            qa = json.loads(q.stdout)
            rep["qa"] = {"ok": qa.get("ok"), "flags": qa.get("flags"),
                         "reading": "For motion graphics, brightness jumps at scene changes and silent stretches "
                                    "without a voice-over are expected; a freeze over 0.7 s wants a slow push-in."}
        except ValueError:
            rep["qa"] = f"the QA did not answer: {(q.stderr or '').strip()[-300:]}"
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def cmd_review(args) -> None:
    """The Gemini review of a render for a client final: the motion goal, every line of copy checked on screen."""
    d = project(args.dir)
    if not WATCH.exists():
        die(f"agy-watch-video is not installed ({WATCH})")
    video = Path(args.video).expanduser().resolve()
    lines = []
    deck = d / "copy" / "onscreen.json"
    if deck.exists():
        lines = [s["text"] for s in json.loads(deck.read_text(encoding="utf-8")).get("strings", [])]
    cmd = [sys.executable, WATCH, "watch", video, "--goal", "motion", "--platform", "youtube", "--focus",
           "Do all scenes animate cleanly (characters, UI, charts, transitions), is any shape glitched, cut off or "
           "overlapping wrongly, and is every on-screen text spelled right and readable?"]
    if lines:
        expect = d / "out" / "expect.txt"
        expect.parent.mkdir(parents=True, exist_ok=True)
        expect.write_text("\n".join(lines) + "\n", encoding="utf-8")
        cmd += ["--expect", expect]
    log("Gemini review of the render (about 5 minutes)")
    r = subprocess.run([str(c) for c in cmd], cwd=str(d), text=True, timeout=3600)
    sys.exit(r.returncode)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Explainer B-roll from the remotion-broll kit.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new", help="copy the kit into a new folder and install it")
    n.add_argument("dir")
    n.add_argument("--link-modules", help="use this project's node_modules (same Remotion version) instead of npm ci")
    n.add_argument("--no-install", action="store_true", help="copy only")
    n.set_defaults(func=cmd_new)
    c = sub.add_parser("check", help="typecheck, then lint every word on screen")
    c.add_argument("dir")
    c.add_argument("--locale", default="US", help="the market of the copy (default US)")
    c.set_defaults(func=cmd_check)
    s = sub.add_parser("stills", help="still frames and a contact sheet")
    s.add_argument("dir")
    s.add_argument("--comp", default="BrollMinute")
    s.add_argument("--frames", help="comma-separated frame numbers (default: 16 across the composition)")
    s.set_defaults(func=cmd_stills)
    r = sub.add_parser("render", help="render, time it and run the measured QA")
    r.add_argument("dir")
    r.add_argument("--comp", default="BrollMinute")
    r.add_argument("--out", help="output file (default out/COMP.mp4)")
    r.add_argument("--no-qa", action="store_true")
    r.set_defaults(func=cmd_render)
    v = sub.add_parser("review", help="the Gemini review for a client final (agy-watch-video)")
    v.add_argument("dir")
    v.add_argument("video")
    v.set_defaults(func=cmd_review)
    return ap


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
