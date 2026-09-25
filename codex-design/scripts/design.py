#!/usr/bin/env python3
"""codex-design: render Claude-written HTML/CSS designs to exact-size PNG/JPG/WebP/PDF with the installed Chrome
(DevTools protocol over a pipe, stdlib only), check them (clipped or off-canvas text, safe zones, real contrast over
images, missing fonts, upscaled or broken images, file size), and slice carousels.

Run `design.py doctor` first. Every command prints JSON on stdout; logs go to stderr.
"""
from __future__ import annotations

import argparse
import atexit
import base64
import contextlib
import functools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
from html import escape as html_escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True  # no __pycache__ inside the skill folder
import copyrules  # noqa: E402  (copy that reads human: references/copy.md)

SKILL_VERSION = "2026.09.25.1"
SKILL_DIR = Path(__file__).resolve().parent.parent
PRESETS_FILE = SKILL_DIR / "scripts" / "presets.json"


def _venv_dir() -> Path:
    """The skill venv for this Python: compiled packages (Pillow, uharfbuzz) only load in the minor version that
    built them, so a different python3 gets its own .venv-3.X next to the first one instead of a broken import."""
    base = SKILL_DIR / ".venv"
    try:
        cfg = (base / "pyvenv.cfg").read_text(encoding="utf-8")
        m = re.search(r"^version(?:_info)?\s*=\s*(\d+)\.(\d+)", cfg, re.M)
        if m and (int(m.group(1)), int(m.group(2))) != sys.version_info[:2]:
            return SKILL_DIR / f".venv-{sys.version_info[0]}.{sys.version_info[1]}"
    except OSError:
        pass
    return base


VENV_DIR = _venv_dir()
MAX_RASTER_PX = 400_000_000  # largest raster written (a 850x2000 mm roll-up at 300 dpi is 237 MP); PDF has no limit
CACHE = Path(os.environ.get("CODEX_DESIGN_CACHE") or Path.home() / ".cache" / "codex-design")
IMAGEGEN = Path(os.environ.get("CODEX_IMAGEGEN_SCRIPT") or
                Path.home() / ".claude" / "skills" / "codex-imagegen" / "scripts" / "codex_image.py")
CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
CHROME_NAMES = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "chrome"]
# Templates link the kit and the sample brand as https://codex-design.invalid/<path under templates/>; the renderer
# answers those requests from the skill folder (no network; .invalid never resolves). `kit` copies them for delivery.
KIT_HOST = "https://codex-design.invalid/"
KIT_ROOT = SKILL_DIR / "templates"
MIME = {".css": "text/css", ".js": "application/javascript", ".svg": "image/svg+xml", ".woff2": "font/woff2",
        ".woff": "font/woff", ".ttf": "font/ttf", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".json": "application/json"}
PX_PER_MM = 96 / 25.4
# IPTC DigitalSourceType for a design that composites generated visuals with typeset text, logos and vectors:
# "compositeSynthetic" = a mix of several elements, at least one of which is generative AI (IPTC, 2024-10-23).
# (compositeWithTrainedAlgorithmicMedia is for a real photo changed by generative fill; raw AI images keep
# trainedAlgorithmicMedia from codex-imagegen.)
COMPOSITE_TERM = "compositeSynthetic"
COMPOSITE_XMP = ('<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                 '<rdf:Description xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/" '
                 'Iptc4xmpExt:DigitalSourceType="http://cv.iptc.org/newscodes/digitalsourcetype/'
                 f'{COMPOSITE_TERM}"/></rdf:RDF></x:xmpmeta>')


def log(msg: str) -> None:
    print(f"[codex-design {time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"codex-design: {msg}", file=sys.stderr)
    sys.exit(code)


_TMP = {"lock": threading.Lock()}


def tmp_dir(prefix: str = "codex-design-") -> str:
    """Every temporary folder lives under one run root that is removed at exit (CODEX_DESIGN_KEEP_TMP=1 keeps it)."""
    with _TMP["lock"]:
        if "root" not in _TMP:
            _TMP["root"] = tempfile.mkdtemp(prefix="codex-design-run-")
            Path(_TMP["root"], ".pid").write_text(str(os.getpid()), encoding="utf-8")  # `doctor --clean-tmp`
            if not os.environ.get("CODEX_DESIGN_KEEP_TMP"):
                atexit.register(shutil.rmtree, _TMP["root"], True)
    return tempfile.mkdtemp(prefix=prefix, dir=_TMP["root"])


def stale_runs() -> list:
    """Run folders left by runs that were killed (SIGKILL, a crash, power loss): their process is gone and they are
    over an hour old. A SIGTERM or Ctrl-C run cleans up after itself."""
    out = []
    base = Path(tempfile.gettempdir())
    for d in base.glob("codex-design-run-*"):
        if d.is_symlink() or not d.is_dir() or d.parent != base or str(d) == _TMP.get("root"):
            continue
        try:
            age = time.time() - d.stat().st_mtime
        except OSError:
            continue
        if age < 3600:
            continue
        try:
            pid = int((d / ".pid").read_text(encoding="utf-8").strip())
        except (OSError, ValueError):
            pid = None
        if pid:
            try:
                os.kill(pid, 0)
                continue  # still running
            except ProcessLookupError:
                pass
            except PermissionError:
                continue
        elif age < 86400:  # a folder from before .pid files: only when a day old
            continue
        size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file() and not f.is_symlink())
        out.append({"path": str(d), "bytes": size, "hours": round(age / 3600, 1)})
    return out


# Every Codex session and codex-imagegen child runs in its own process group and is tracked here, so a stop signal
# (Ctrl-C, or SIGTERM when a background task is killed) ends them all at once. Before, a multi-run judge kept its
# sessions running, and spending plan quota, until they finished on their own.
_LIVE = {"procs": set(), "lock": threading.RLock(), "stop": False}  # RLock: a signal may land while it is held
POLL_S = 0.2  # how often a running child checks the stop flag and its timeout


class RunFailed(Exception):
    """A Codex session, a judge run or an image edit that gave no usable answer. The message says why, in one line."""


def _stop_group(proc, grace: float = 2.0) -> None:
    """SIGTERM the child's process group (a codex-imagegen child ends its own sessions on it), then SIGKILL whatever
    is left after `grace` seconds."""
    import signal
    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, None)):
        if proc.poll() is not None:
            return
        try:
            os.killpg(proc.pid, sig)
        except OSError:
            try:
                proc.kill()
            except OSError:
                pass
        try:
            proc.wait(timeout=wait)
            return
        except subprocess.TimeoutExpired:
            continue


def kill_live_sessions() -> int:
    """Stop every child session this run started and refuse new ones. Returns how many were still running."""
    _LIVE["stop"] = True
    with _LIVE["lock"]:
        procs = [p for p in _LIVE["procs"] if p.poll() is None]
    threads = [threading.Thread(target=_stop_group, args=(p, 3.0)) for p in procs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(procs)


def run_session(cmd: list, prompt: str | None, timeout: float | None, env: dict | None = None) -> dict:
    """Run a child (a Codex session, codex-imagegen or a judge) in its own process group, tracked in _LIVE, with its
    output in files so no pipe fills up. A timeout or a stop ends the whole group.
    -> {"stdout", "stderr", "returncode", "error": None, "stopped" or "timed out after N s"}"""
    res = {"stdout": "", "stderr": "", "returncode": None, "error": None}
    if _LIVE["stop"]:
        return dict(res, error="stopped")
    tmp = Path(tmp_dir("session-"))
    so, se = tmp / "stdout.txt", tmp / "stderr.txt"
    t0 = time.time()
    with open(so, "w", encoding="utf-8") as fo, open(se, "w", encoding="utf-8") as fe:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE if prompt is not None else subprocess.DEVNULL, stdout=fo,
                                stderr=fe, text=True, start_new_session=True, env=env)
        with _LIVE["lock"]:
            _LIVE["procs"].add(proc)
        try:
            if prompt is not None:
                try:
                    proc.stdin.write(prompt)
                    proc.stdin.close()
                except BrokenPipeError:
                    pass
            while True:
                try:
                    proc.wait(timeout=POLL_S)
                    break
                except subprocess.TimeoutExpired:
                    pass
                stop = "stopped" if _LIVE["stop"] else \
                    f"timed out after {timeout:g} s" if timeout and time.time() - t0 > timeout else None
                if stop:
                    _stop_group(proc, grace=3.0)
                    res["error"] = stop
                    break
        finally:
            with _LIVE["lock"]:
                _LIVE["procs"].discard(proc)
            if proc.poll() is None:  # an exception (a stop signal) got here first
                _stop_group(proc, grace=3.0)
    if res["error"] is None and _LIVE["stop"] and proc.returncode != 0:
        res["error"] = "stopped"  # ended by kill_live_sessions() from another thread
    res["returncode"] = proc.returncode
    res["stdout"] = so.read_text(encoding="utf-8", errors="replace")
    res["stderr"] = se.read_text(encoding="utf-8", errors="replace")
    return res


def child_budget(timeout: float) -> float:
    """How long to wait for a child that runs Codex sessions of `timeout` seconds and retries a failed one once
    (codex-imagegen, a judge): both sessions, plus two minutes to start and save. The child's own timeout ends a hung
    session first, so the outer one only catches a child that is stuck itself."""
    return 2 * timeout + 120


def one_line(text: str, limit: int = 300) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()[:limit]


def codex_error(res: dict) -> str:
    """Why a child session gave no answer, in one line: the stop or timeout, else an error event in Codex's --json
    stream, else the last line it wrote to stderr, else the end of its output."""
    if res.get("error"):
        return res["error"]
    for line in reversed((res.get("stdout") or "").splitlines()):
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        err = ev.get("error")
        if isinstance(err, str) and err.strip():
            return one_line(err)
        for part in (err, ev.get("msg"), ev):
            if isinstance(part, dict) and part.get("message") and (
                    part is err or re.search(r"error|fail", str(part.get("type") or ""), re.I)):
                return one_line(part["message"])
    lines = [x for x in (res.get("stderr") or "").splitlines() if x.strip()]
    if lines:
        return one_line(lines[-1])
    tail = (res.get("stdout") or "").strip().splitlines()
    return one_line(tail[-1]) if tail else f"no output (exit {res.get('returncode')})"


def need_pillow():
    """Pillow from the system, else from this skill's venv (`doctor --setup`), else from codex-imagegen's venv."""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        add_venv_paths(IMAGEGEN.parent.parent / ".venv")
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            die("this command needs Pillow; run once: python3 ~/.claude/skills/codex-design/scripts/design.py "
                "doctor --setup")
    from PIL import Image
    if Image.MAX_IMAGE_PIXELS and Image.MAX_IMAGE_PIXELS < MAX_RASTER_PX:
        Image.MAX_IMAGE_PIXELS = MAX_RASTER_PX  # our own captures of big print canvases are not decompression bombs
    return Image


def add_venv_paths(*extra: Path) -> None:
    """Make the skill venv's packages importable: only the site-packages built for the running Python."""
    ver = f"python{sys.version_info[0]}.{sys.version_info[1]}"
    for venv in (VENV_DIR,) + extra:
        sp = venv / "lib" / ver / "site-packages"
        if sp.is_dir() and str(sp) not in sys.path:
            sys.path.append(str(sp))


# ----------------------------------------------------------------------------- presets
_PRESETS: dict = {}


_PRESET_FILES: list = []  # --preset-file, after CODEX_DESIGN_PRESETS: a client's or project's verified specs
_RETIRED: dict = {}


def load_preset_file(path) -> list:
    """A preset file: a list of presets, or {"presets": [...], "retired": [...]}. Each preset needs id, w and h; a
    source and a verified date are expected (a spec without a source is a guess)."""
    f = Path(path).expanduser()
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read the preset file {f}: {e}")
    rows = data.get("presets", []) if isinstance(data, dict) else data
    if not isinstance(rows, list):
        die(f"{f}: \"presets\" must be a list")
    for i, r in enumerate(rows, 1):
        if not isinstance(r, dict) or not all(r.get(k) for k in ("id", "w", "h")):
            die(f"{f}: preset {i} needs at least \"id\", \"w\" and \"h\"")
        if not r.get("source"):
            log(f"{f.name}: preset {r['id']} has no source; say where its numbers come from")
    if isinstance(data, dict):
        for r in data.get("retired") or []:
            _RETIRED[r["id"]] = r
    return rows


def presets() -> dict:
    if not _PRESETS:
        try:
            data = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            die(f"cannot read {PRESETS_FILE}: {e}")
        _PRESETS.update({p["id"]: p for p in data["presets"]})
        for r in data.get("retired") or []:
            _RETIRED[r["id"]] = r
        extra = [x for x in os.environ.get("CODEX_DESIGN_PRESETS", "").split(os.pathsep) if x] + _PRESET_FILES
        for f in extra:  # later files win: a project can correct a skill preset by giving the same id
            for r in load_preset_file(f):
                _PRESETS[r["id"]] = dict(r, origin=str(Path(f).expanduser()))
    return _PRESETS


def retired() -> dict:
    presets()
    return _RETIRED


def _words_of(r: dict) -> str:
    return " ".join(str(x) for x in [r.get("id"), r.get("label"), r.get("platform"), r.get("group"),
                                     " ".join(r.get("aliases") or []), r.get("notes")] if x).lower()


def _preset_vocab() -> set:
    words = set()
    for r in list(presets().values()) + list(retired().values()):
        words.update(re.findall(r"[\w\u0980-\u09FF]+", _words_of(r)))
    return words


def find_presets(query: str) -> list:
    """Presets matching words people use ("pinterest pin", "ebook cover", "fb cover photo", "biye card"), best first,
    with retired formats and what replaces them. A word that starts no word in the catalogue is read as a close
    spelling ("pintarest", "thumbnil", "youtute", "squrae", "bilboard"), and every result then says so in "read_as"
    (a correctly spelt word the catalogue lacks can land on a different word: the caller shows the reading)."""
    import difflib
    words = [w for w in re.findall(r"[\w\u0980-\u09FF]+", query.lower()) if w not in ("design", "size", "the", "a")]
    if not words:
        return []
    vocab, read_as = _preset_vocab(), {}
    for i, w in enumerate(words):
        if len(w) >= 4 and not any(v.startswith(w) for v in vocab):
            close = difflib.get_close_matches(w, vocab, n=1, cutoff=0.8)
            if close:
                read_as[w] = words[i] = close[0]
    out = []
    for r in list(presets().values()) + [dict(v, retired=True) for v in retired().values()]:
        idl, label = str(r.get("id", "")).lower(), f"{r.get('label', '')} {' '.join(r.get('aliases') or [])}".lower()
        text = _words_of(r)
        phrase = " ".join(words)
        score, hit = 0, 0
        if any(phrase == a.lower() for a in r.get("aliases") or []):
            score += 8  # the exact words people use for it ("pinterest pin", "fb cover photo")
        elif phrase in label:
            score += 4
        for w in words:  # words match at a word start: "ebook" is not found inside "facebook"
            start = re.compile(rf"(?<![\w\u0980-\u09FF]){re.escape(w)}")
            if any(part.startswith(w) for part in idl.split("-")):
                score, hit = score + 3, hit + 1
            elif start.search(label):
                score, hit = score + 2, hit + 1
            elif start.search(text):
                score, hit = score + 1, hit + 1
        if hit and hit >= max(1, (len(words) + 1) // 2):
            out.append((hit, score, r))
    out.sort(key=lambda t: (-t[0], -t[1], len(str(t[2].get("id"))), str(t[2].get("id"))))
    return [dict(r, read_as=read_as) if read_as else r for _, _, r in out]


def nearest_presets(w: float, h: float, print_job: bool, n: int = 6) -> list:
    """Presets with the closest aspect ratio (and size) to an unknown canvas: the place to borrow a safe zone, a
    viewing width and a pattern from."""
    import math
    rows = []
    for r in presets().values():
        c = resolve_canvas(r["id"], None)
        if bool(c["print"]) != bool(print_job):
            continue
        tw, th = c["trim_px"]
        d = abs(math.log((tw / th) / (w / h)))
        rows.append((d, abs(math.log(tw / w)), r["id"], round(tw / th, 3)))
    rows.sort()
    return [{"id": i, "ratio": ratio, "ratio_off_pct": round((math.exp(d) - 1) * 100, 1)} for d, _, i, ratio in rows[:n]]


def parse_len(v, unit_default: str = "px") -> float:
    """'1080', '1080px', '210mm', '8.5in', '3mm' -> CSS px."""
    m = re.fullmatch(r"\s*([0-9]*\.?[0-9]+)\s*(px|mm|in|cm|pt)?\s*", str(v))
    if not m:
        die(f"bad length: {v!r}")
    n, unit = float(m.group(1)), m.group(2) or unit_default
    return n * {"px": 1, "mm": PX_PER_MM, "cm": PX_PER_MM * 10, "in": 96, "pt": 96 / 72}[unit]


SIZE_RX = re.compile(r"\s*([0-9.]+(?:px|mm|in|cm)?)\s*[xX×]\s*([0-9.]+(?:px|mm|in|cm)?)\s*")  # 1080x1350, 210mmx297mm


def resolve_canvas(preset: str | None, size: str | None, bleed: str | None = None) -> dict:
    """The canvas in CSS px plus what the checks need: safe insets, minimum text size, byte limit, print info."""
    if preset:
        p = presets().get(preset)
        if not p:
            if preset in retired():
                r = retired()[preset]
                die(f"{r.get('label', preset)} was retired ({r.get('retired', 'date unknown')}): "
                    f"{r.get('notes', '')} Use {', '.join(r.get('use') or []) or 'another format'}")
            near = [x["id"] for x in find_presets(preset.replace("-", " "))[:4]]
            die(f"unknown preset {preset!r}" + (f"; did you mean {', '.join(near)}?" if near else "") +
                " (`design.py presets --find WORDS`, or --size WxH with --safe and --view-width)")
        c = dict(p)
    elif size:
        m = re.fullmatch(r"\s*([0-9.]+(?:px|mm|in|cm)?)\s*[xX×]\s*([0-9.]+(?:px|mm|in|cm)?)\s*", size)
        if not m:
            die(f"bad --size {size!r}; use 1080x1350, 210mmx297mm or 8.5inx11in")
        c = {"id": "custom", "w": m.group(1), "h": m.group(2)}
    else:
        die("give --preset or --size")
    w, h = parse_len(c["w"]), parse_len(c["h"])
    print_job = c.get("print") or any(str(c[k]).endswith(("mm", "in", "cm")) for k in ("w", "h"))
    b = parse_len(bleed if bleed is not None else c.get("bleed", "0")) if print_job else 0.0
    c.update({"w_px": w + 2 * b, "h_px": h + 2 * b, "trim_px": [w, h], "bleed_px": b, "print": bool(print_job)})
    safe = c.get("safe") or [0, 0, 0, 0]  # top, right, bottom, left in canvas px (print: mm inside the trim)
    if print_job:
        safe = [parse_len(s, "mm") + b for s in (c.get("safe_mm") or [5, 5, 5, 5])]
    c["safe_px"] = [float(s) for s in safe]
    # folded print (brochures): fold x positions per side, measured from the left trim edge
    c["folds_px"] = [[b + parse_len(f, "mm") for f in side] for side in c.get("folds_mm") or []]
    set_distance_floor(c)
    return c


def distance_ppi(c: dict) -> float:
    """Print resolution a viewer can tell apart, at the file's own scale: 240 ppi in hand (or the preset's own lower
    figure: posters and roll-ups 150); from a distance, 87.3 / metres on the real object (1 arcminute of normal acuity,
    the same 3438 constant as AVIXA DISCAS), never under 10 (billboards print at 12.5 to 45); a scaled artwork file (a
    bulletin supplied at 1/2 in = 1 ft, file_scale 24) needs that times its scale, at most 240. The floor sits on the
    real object on purpose, so on a 1:24 billboard file it decides: 240 ppi on the file is 10 ppi on the board, a
    little under Lamar's 300 ppi file (12.5 on the board)."""
    d = float(c.get("view_distance_m") or 0)
    if d > 0.4:
        return min(240.0, max(10.0, min(240.0, 87.3 / d)) * float(c.get("file_scale") or 1))
    return min(240.0, float(c.get("ppi") or 240))  # in hand, or the printer's own lower figure (posters: 150)


def set_distance_floor(c: dict) -> None:
    """Text seen from a distance gets its floor from the distance, not from a phone width. Signs read on foot (posters,
    banners, wayfinding, menus): ADA 2010 §703.5.5, capitals 16 mm up to 1.83 m plus 10.5 mm per metre beyond. Signs
    read in passing from a road (billboards, bus sides, roadside screens; `legibility_index`): USSC and MUTCD, capitals
    = distance / legibility index (30 on average: 2.78 mm per metre). Screens in a room (menu boards, signage):
    AVIXA DISCAS basic decision making, character height = farthest viewer / 200; screens need their height in
    metres. A scaled artwork file (`file_scale`) gets the floor divided by its scale. Font size = cap height / 0.7
    (common sans faces)."""
    d = float(c.get("view_distance_m") or 0)
    if d <= 0:
        return
    li, scale = float(c.get("legibility_index") or 0), float(c.get("file_scale") or 1)
    screen_h = float(c.get("screen_height_m") or 0)
    if li and (c["print"] or screen_h):
        cap_mm = d * 83.33 / li
        why = f"capitals {cap_mm:.0f} mm for {d:g} m at legibility index {li:g} (USSC, MUTCD)"
        floor = (cap_mm / scale * PX_PER_MM if c["print"] else cap_mm / 1000 / screen_h * c["trim_px"][1]) / 0.7
    elif c["print"]:
        cap_mm = 16 + 10.5 * max(0.0, d - 1.83)
        floor = cap_mm / scale / 0.7 * PX_PER_MM
        why = f"capitals {cap_mm:.0f} mm for {d:g} m (ADA 703.5.5)"
    elif screen_h:
        floor = (d / 200) / screen_h * c["trim_px"][1] / 0.7
        why = f"characters {d / 200 * 1000:.0f} mm tall for {d:g} m on a {screen_h:g} m high screen (DISCAS)"
    else:
        return
    if c["print"] and scale != 1:
        why += f", on a file at 1:{scale:g} of the real size"
    if floor > float(c.get("min_text_px") or 0):
        c["min_text_px"] = round(floor, 1)
        c["distance_floor"] = why


def apply_spec(c: dict, args) -> dict:
    """--safe, --keepout, --view-width and --min-text refine any canvas. A custom size without them gets stated
    defaults, never silent ones: a 5 % safe margin, a phone viewing width of 390 px and an 11 px text floor there
    (screens); a note when print has no bleed. They are listed in the report's canvas.assumed."""
    assumed = []
    tw, th = c["trim_px"]
    short = min(tw, th)
    custom = c.get("id") == "custom"
    if getattr(args, "file_scale", None):
        if float(args.file_scale) < 1:
            die("--file-scale is how many times bigger the real object is than the file (24 for 1/2 in = 1 ft)")
        c["file_scale"] = float(args.file_scale)
    if getattr(args, "legibility_index", None):
        c["legibility_index"] = float(args.legibility_index)
    if any(getattr(args, k, None) for k in ("view_distance", "screen_height", "file_scale", "legibility_index")):
        if getattr(args, "view_distance", None):
            c["view_distance_m"] = float(args.view_distance)
        if getattr(args, "screen_height", None):
            c["screen_height_m"] = float(args.screen_height)
        set_distance_floor(c)
    if getattr(args, "safe", None):
        vals = [v.strip() for v in str(args.safe).split(",") if v.strip()]
        if len(vals) == 1:
            vals *= 4
        if len(vals) != 4:
            die("--safe takes one value or four (top,right,bottom,left): px, mm for print, or a share like 5%")
        c["safe_px"] = [(float(v[:-1]) / 100 * short if v.endswith("%") else
                         parse_len(v, "mm" if c["print"] else "px")) + c["bleed_px"] for v in vals]
    elif custom and not c["print"]:
        m = round(0.05 * short)
        c["safe_px"] = [float(m)] * 4
        assumed.append(f"a safe margin of 5 % of the short side ({m} px)")
    if getattr(args, "keepout", None):
        zones = []
        for k in args.keepout:
            try:
                z = [float(x) for x in k.split(",")]
            except ValueError:
                z = []
            if len(z) != 4 or z[2] <= z[0] or z[3] <= z[1]:
                die(f"--keepout {k!r}: give x0,y0,x1,y1 in canvas px (the area the platform's UI covers)")
            zones.append(z)
        c["keepout"] = zones
    distant = getattr(args, "view_distance", None) or c.get("view_distance_m")
    if getattr(args, "view_width", None):
        c["view_width_px"] = float(args.view_width)
    elif custom and not c["print"] and not distant:  # a screen across a room is not a phone
        c["view_width_px"] = 390.0
        assumed.append("a phone viewing width of 390 px (dense scripts and logos are checked at that size)")
    if getattr(args, "min_text", None):
        c["min_text_px"] = float(args.min_text)
    elif custom and not c["print"] and not c.get("distance_floor") and c.get("view_width_px"):
        c["min_text_px"] = round(11 * tw / c["view_width_px"], 1)
        c.setdefault("large_text_px", round(24 * tw / c["view_width_px"], 1))
        assumed.append(f"a text floor of 11 px at that width ({c['min_text_px']:g} px on the canvas)")
    if custom and c["print"] and not c["bleed_px"]:
        assumed.append("no bleed: printers usually need 3 mm (0.125 in); add --bleed 3mm unless the printer says "
                       "otherwise")
    c["assumed"] = assumed
    return c


# ----------------------------------------------------------------------------- chrome over the devtools pipe
def chrome_bin() -> str:
    env = os.environ.get("CODEX_DESIGN_CHROME")
    if env:
        if Path(env).expanduser().is_file():
            return str(Path(env).expanduser())
        if shutil.which(env):
            return shutil.which(env)
        die(f"CODEX_DESIGN_CHROME points at {env}, which does not exist; fix it or unset it")
    for cand in CHROME_PATHS:
        p = Path(cand).expanduser()
        if p.exists():
            return str(p)
    for n in CHROME_NAMES:
        w = shutil.which(n)
        if w:
            return w
    die("Google Chrome (or Chromium/Edge) not found; install it or set CODEX_DESIGN_CHROME")


class Chrome:
    """One headless Chrome with a throwaway profile, driven over --remote-debugging-pipe (fd 3 in, fd 4 out).
    Offline unless allow_net: every http(s) and WebSocket request, loopback included, goes to a proxy that does not
    exist, so a design renders the same everywhere and cannot send anything anywhere. Kit links
    (https://codex-design.invalid/) are answered from the skill folder before they reach the network."""

    def __init__(self, allow_net: bool = False):
        import fcntl
        r1, self._w = os.pipe()
        self._r, w2 = os.pipe()
        cr = fcntl.fcntl(r1, fcntl.F_DUPFD_CLOEXEC, 10)
        cw = fcntl.fcntl(w2, fcntl.F_DUPFD_CLOEXEC, 10)
        os.close(r1)
        os.close(w2)

        def wire():
            os.dup2(cr, 3)
            os.dup2(cw, 4)
        args = [chrome_bin(), "--headless", "--remote-debugging-pipe", f"--user-data-dir={tmp_dir('chrome-')}",
                "--use-mock-keychain", "--password-store=basic", "--no-first-run", "--no-default-browser-check",
                "--disable-extensions", "--disable-sync", "--disable-background-networking",
                "--disable-component-update", "--disable-default-apps", "--mute-audio", "--hide-scrollbars",
                "--allow-file-access-from-files", "--force-color-profile=srgb"] + \
            ([] if allow_net else ["--proxy-server=http://127.0.0.1:9", "--proxy-bypass-list=<-loopback>"]) + \
            ["about:blank"]
        self.allow_net = allow_net
        self.proc = subprocess.Popen(args, preexec_fn=wire, close_fds=False, stdin=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.close(cr)
        os.close(cw)
        self._buf = b""
        self._id = 0
        self._aux = 10 ** 6  # ids of fire-and-forget replies (kit requests), never awaited
        self._events: list = []

    def _dispatch(self, m: dict) -> bool:
        """Answer paused kit requests (https://codex-design.invalid/...) from the skill folder."""
        if m.get("method") != "Fetch.requestPaused":
            return False
        p = m["params"]
        rel = p["request"]["url"][len(KIT_HOST):].split("?")[0].split("#")[0]
        f = (KIT_ROOT / rel).resolve()
        ok = f.is_file() and KIT_ROOT.resolve() in f.parents
        body = f.read_bytes() if ok else b"not found"
        self._aux += 1
        msg = {"id": self._aux, "method": "Fetch.fulfillRequest", "sessionId": m.get("sessionId"),
               "params": {"requestId": p["requestId"], "responseCode": 200 if ok else 404,
                          "responseHeaders": [{"name": "Content-Type",
                                               "value": MIME.get(f.suffix.lower(), "application/octet-stream")},
                                              {"name": "Access-Control-Allow-Origin", "value": "*"}],
                          "body": base64.b64encode(body).decode()}}
        os.write(self._w, json.dumps(msg).encode() + b"\0")
        return True

    def _msg(self, deadline: float) -> dict:
        import select
        while b"\0" not in self._buf:
            left = deadline - time.time()
            if left <= 0 or not select.select([self._r], [], [], left)[0]:
                raise TimeoutError("Chrome did not answer in time")
            chunk = os.read(self._r, 1 << 20)
            if not chunk:
                code = self.proc.poll()
                raise RuntimeError("Chrome quit" + (f" (exit {code})" if code is not None else "") +
                                   f": {chrome_bin()} may be broken or not a Chrome build; set CODEX_DESIGN_CHROME")
            self._buf += chunk
        raw, _, self._buf = self._buf.partition(b"\0")
        return json.loads(raw)

    def send(self, method: str, params: dict | None = None, session: str | None = None, timeout: float = 60):
        self._id += 1
        msg = {"id": self._id, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        os.write(self._w, json.dumps(msg).encode() + b"\0")
        deadline = time.time() + timeout
        while True:
            m = self._msg(deadline)
            if m.get("id") == self._id:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error'].get('message')}")
                return m.get("result", {})
            if not self._dispatch(m) and not (m.get("id", 0) > 10 ** 6):
                self._events.append(m)

    def wait(self, event: str, session: str, timeout: float = 30) -> dict:
        for i, e in enumerate(self._events):
            if e.get("method") == event and e.get("sessionId") == session:
                return self._events.pop(i)
        deadline = time.time() + timeout
        while True:
            e = self._msg(deadline)
            if e.get("method") == event and e.get("sessionId") == session:
                return e
            if not self._dispatch(e) and not (e.get("id", 0) > 10 ** 6):
                self._events.append(e)

    def evaluate(self, session: str, expr: str, timeout: float = 30):
        r = self.send("Runtime.evaluate", {"expression": expr, "awaitPromise": True, "returnByValue": True},
                      session=session, timeout=timeout)
        if "exceptionDetails" in r:
            raise RuntimeError("page script failed: " + json.dumps(r["exceptionDetails"])[:400])
        return r.get("result", {}).get("value")

    def network_log(self, session: str, drop: bool = True) -> dict:
        """What the page asked for (Network events of this session): failed or refused requests as
        [(url, reason)], and requests still waiting. With drop the events are removed, so a pack of many canvases
        does not pile them up."""
        urls, done, failed, keep = {}, set(), [], []
        for e in self._events:
            m = e.get("method", "")
            if e.get("sessionId") != session or not m.startswith("Network."):
                keep.append(e)
                continue
            p = e.get("params") or {}
            rid = p.get("requestId")
            if m == "Network.requestWillBeSent":
                urls[rid] = (p.get("request") or {}).get("url", "")
            elif m == "Network.loadingFinished":
                done.add(rid)
            elif m == "Network.loadingFailed":
                done.add(rid)
                if not p.get("canceled"):
                    err = p.get("errorText") or p.get("blockedReason") or "failed"
                    if "FILE_NOT_FOUND" in err:
                        err = "the file is not there (check the path and its case)"
                    elif "PROXY" in err or "TUNNEL" in err:
                        err = "blocked: renders are offline (download fonts with `design.py fonts`, keep images in " \
                              "the project, or pass --allow-net)"
                    failed.append((urls.get(rid, "?"), err))
            elif m == "Network.responseReceived":
                r = p.get("response") or {}
                if int(r.get("status") or 200) >= 400:
                    failed.append((r.get("url", urls.get(rid, "?")), f"HTTP {r.get('status')}"))
        if drop:
            self._events = keep
        pending = [u for rid, u in urls.items() if rid not in done and not u.startswith("data:")]
        return {"failed": failed, "pending": pending}

    def version(self) -> str:
        if not hasattr(self, "_version"):
            try:
                self._version = self.send("Browser.getVersion", timeout=10).get("product", "")
            except Exception:
                self._version = ""
        return self._version

    def close(self) -> None:
        try:
            self.send("Browser.close", timeout=5)
        except Exception:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        for fd in (self._r, self._w):
            try:
                os.close(fd)
            except OSError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


# ----------------------------------------------------------------------------- page checks (run inside Chrome)
QA_JS = r"""
(async () => {
  const W = innerWidth, H = innerHeight, S = window.__CD || {safe: [0, 0, 0, 0]};
  const [st, sr, sb, sl] = S.safe;
  const one = document.createElement('canvas'); one.width = one.height = 1;
  const oc = one.getContext('2d', {willReadFrequently: true});
  const rgba = c => { oc.clearRect(0, 0, 1, 1); oc.fillStyle = '#000'; oc.fillStyle = c; oc.fillRect(0, 0, 1, 1);
    const d = oc.getImageData(0, 0, 1, 1).data; return [d[0], d[1], d[2], +(d[3] / 255).toFixed(3)]; };
  const mc = document.createElement('canvas').getContext('2d');
  const probe = 'mmmmmmmmmmlliWW@#1';
  const GENERIC = /^(serif|sans-serif|monospace|cursive|fantasy|system-ui|ui-[a-z-]+|emoji|math|fangsong)$/i;
  const unq = s => s.replace(/^["']|["']$/g, '');
  const faces = {};
  for (const f of document.fonts) (faces[unq(f.family)] = faces[unq(f.family)] || []).push(f);
  // web fonts: the element's own face (weight, style, the characters it shows) must be loaded;
  // system fonts: measured against the generic fallbacks at the same weight
  const hasFont = (f, w, st, text) => {
    if (GENERIC.test(f)) return true;
    if (faces[f]) return !faces[f].every(x => x.status === 'error') &&
      document.fonts.check(`${st} ${w} 16px "${f}"`, text || 'a');
    return ['monospace', 'serif', 'sans-serif'].some(g => {
      mc.font = `${st} ${w} 72px ${g}`; const a = mc.measureText(probe).width;
      mc.font = `${st} ${w} 72px "${f}", ${g}`; return Math.abs(mc.measureText(probe).width - a) > 0.01; });
  };
  const SCRIPTS = {bengali: /[ঀ-৿]/, devanagari: /[ऀ-ॿ]/, arabic: /[؀-ۿݐ-ݿ]/,
    hebrew: /[֐-׿]/, thai: /[฀-๿]/, cyrillic: /[Ѐ-ӿ]/, greek: /[Ͱ-Ͽ]/,
    cjk: /[぀-ヿ㐀-鿿가-힯]/};
  const covers = (face, cp) => (face.unicodeRange || 'U+0-10FFFF').split(',').some(r => {
    const m = r.trim().replace(/^U\+/i, '').split('-');
    const a = parseInt(m[0].replace(/\?/g, '0'), 16), b = m[1] ? parseInt(m[1], 16) : parseInt(m[0].replace(/\?/g, 'F'), 16);
    return cp >= a && cp <= b; });
  // a script the primary web font does not cover is drawn by some system font instead (mixed look)
  const fallbackScripts = (f, text) => !faces[f] ? [] : Object.entries(SCRIPTS).filter(([k, rx]) => {
    const m = text.match(rx); return m && !faces[f].some(x => covers(x, m[0].codePointAt(0))); }).map(([k]) => k);
  // does an element paint at a point it is hit at? SVG shapes are only hit where painted; replaced elements paint
  // their box; HTML boxes paint with a background, border, shadow or a pseudo-element layer
  const alpha = c => { const m = /rgba?\(([^)]+)\)/.exec(c || ''); if (!m) return c && c !== 'transparent' ? 1 : 0;
    const v = m[1].split(/[ ,/]+/).filter(Boolean); return v.length > 3 ? parseFloat(v[3]) : 1; };
  const boxPaints = st => alpha(st.backgroundColor) > 0.02 || st.backgroundImage !== 'none' || st.boxShadow !== 'none' ||
    ['Top', 'Right', 'Bottom', 'Left'].some(k => parseFloat(st['border' + k + 'Width']) > 0 && alpha(st['border' + k + 'Color']) > 0.02) ||
    (st.backdropFilter && st.backdropFilter !== 'none');
  const paints = e => {
    if (e instanceof SVGElement) return !(e instanceof SVGSVGElement);
    if (/^(IMG|CANVAS|VIDEO|IFRAME|OBJECT|EMBED)$/.test(e.tagName)) return true;
    const st = getComputedStyle(e);
    if (+st.opacity < 0.05 || st.visibility !== 'visible') return false;
    if (boxPaints(st)) return true;
    return ['::before', '::after'].some(pe => { const ps = getComputedStyle(e, pe);
      return ps.content !== 'none' && ps.content !== 'normal' && boxPaints(ps); });
  };
  const selector = el => el.id ? '#' + el.id : el.tagName.toLowerCase() +
    (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const els = new Set();
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = tw.nextNode(); n; n = tw.nextNode())
    if (n.nodeValue.trim() && n.parentElement) els.add(n.parentElement);
  const items = [], fams = {};
  // the weights each @font-face family really has: a weight it lacks is drawn from the nearest face (font-synthesis
  // is off), so the page says 600 while the reader sees 700, and the brand's weights are not the ones asked for
  const faceW = {};
  for (const f of document.fonts) {
    const [a, b = a] = String(f.weight).split(/\s+/).map(Number);
    (faceW[f.family.replace(/^["']|["']$/g, '')] ||= []).push([a, b]);
  }
  for (const el of els) {
    if (el.closest('[data-qa-ignore],script,style,noscript,title,template')) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility !== 'visible' || cs.display === 'none') continue;
    let op = 1; for (let a = el; a; a = a.parentElement) op *= +getComputedStyle(a).opacity;
    if (op < 0.05) continue;
    let l = 1e9, t = 1e9, r = -1e9, b = -1e9, text = '';
    const lineBoxes = {};
    for (const c of el.childNodes) if (c.nodeType === 3 && c.nodeValue.trim()) {
      text += c.nodeValue + ' ';
      const rg = document.createRange(); rg.selectNodeContents(c);
      for (const q of rg.getClientRects()) { if (q.width * q.height === 0) continue;
        l = Math.min(l, q.left); t = Math.min(t, q.top); r = Math.max(r, q.right); b = Math.max(b, q.bottom);
        const k = Math.round(q.top / 4); const lb = lineBoxes[k] || (lineBoxes[k] = [1e9, -1e9]);
        lb[0] = Math.min(lb[0], q.left); lb[1] = Math.max(lb[1], q.right); }
    }
    if (r < l) continue;
    const lineKeys = Object.keys(lineBoxes).map(Number).sort((a, b2) => a - b2);
    const widths = lineKeys.map(k => lineBoxes[k][1] - lineBoxes[k][0]);
    // each line's own box (for contrast: a ragged block's union box would include the ground beside short lines),
    // and its ink band: the line box is the font's content area, the letters sit inside it at the font's real
    // ascent and descent for this text (canvas metrics), which matters for tall scripts like Bengali
    mc.font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const tm = mc.measureText(text.trim() || 'x');
    const fAsc = tm.fontBoundingBoxAscent, inkUp = tm.actualBoundingBoxAscent, inkDown = tm.actualBoundingBoxDescent;
    const lineRects = [], inkRects = [];
    for (const c of el.childNodes) if (c.nodeType === 3 && c.nodeValue.trim()) {
      const rg = document.createRange(); rg.selectNodeContents(c);
      for (const q of rg.getClientRects()) if (q.width * q.height > 0 && lineRects.length < 24) {
        lineRects.push([q.left, q.top, q.right, q.bottom].map(v => Math.round(v)));
        const base = q.top + (isFinite(fAsc) && fAsc > 0 ? fAsc : q.height * 0.8);
        inkRects.push([q.left, base - inkUp, q.right, base + inkDown].map(v => Math.round(v)));
      }
    }
    const lastFrac = widths.length > 1 ? widths[widths.length - 1] / Math.max(...widths) : 1;
    const fam = cs.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    fams[fam] = (fams[fam] || 0) + 1;
    const issues = [];
    const wantW = parseInt(cs.fontWeight, 10) || 400, haveW = faceW[fam];
    if (haveW && haveW.length && !haveW.some(([a, b]) => wantW >= a && wantW <= b))
      issues.push('weight-missing:' + wantW + ':' + [...new Set(haveW.map(([a, b]) => a === b ? a : a + '-' + b))].sort().join('/'));
    // box overflow is an HTML notion: SVG text is positioned, and its cuts show up in the canvas and clip checks
    let blk = el; while (blk.parentElement && getComputedStyle(blk).display.startsWith('inline')) blk = blk.parentElement;
    const bcs = getComputedStyle(blk);
    if (!(el instanceof SVGElement)) {
      if (blk.clientWidth > 0 && blk.scrollWidth > blk.clientWidth + 1)
        issues.push(bcs.overflowX === 'visible' ? 'spills-x' : 'clipped-x');
      if (blk.clientHeight > 0 && blk.scrollHeight > blk.clientHeight + 1 && bcs.overflowY !== 'visible') issues.push('clipped-y');
    }
    for (let a = el.parentElement; a && a !== document.documentElement; a = a.parentElement) {
      const acs = getComputedStyle(a);
      if (acs.overflowX === 'visible' && acs.overflowY === 'visible') continue;
      const ar = a.getBoundingClientRect();
      if (l < ar.left - 1 || r > ar.right + 1 || t < ar.top - 1 || b > ar.bottom + 1) { issues.push('clipped-by-' + selector(a)); break; }
    }
    if (el.closest('[data-fit-failed]')) issues.push('fit-failed');
    // a compound broken at its hyphen across two lines ("36-" / "hour")
    for (const c of el.childNodes) if (c.nodeType === 3) {
      const v = c.nodeValue;
      for (let i = 1; i < v.length - 1; i++) {
        if (!/[-\u2010\u2013]/.test(v[i]) || !/\w/.test(v[i - 1]) || !/\w/.test(v[i + 1])) continue;
        if (v[i] === '\u2013' && !(/\d/.test(v[i - 1]) && /\d/.test(v[i + 1]))) continue;  // en dash: number ranges
        const a = document.createRange(), z = document.createRange();
        a.setStart(c, i); a.setEnd(c, i + 1); z.setStart(c, i + 1); z.setEnd(c, i + 2);
        const qa = a.getBoundingClientRect(), qz = z.getBoundingClientRect();
        if (qz.top > qa.top + qa.height * 0.5) {
          let s0 = i, s1 = i;
          while (s0 > 0 && !/\s/.test(v[s0 - 1])) s0--;
          while (s1 < v.length - 1 && !/\s/.test(v[s1 + 1])) s1++;
          issues.push('hyphen-break:' + v.slice(s0, s1 + 1)); break; }
      }
    }
    // cut and safe-zone checks use the measured ink (the inline box includes the font's ascent/descent, which
    // pokes past the letters; without ink metrics allow a fraction of the size instead).
    // Carousels (slides side by side) and documents (pages stacked) are checked against their own canvas.
    const fs = parseFloat(cs.fontSize);
    const hasInk = inkRects.length > 0;
    const cut = hasInk ? 2 : 0.12 * fs, soft = hasInk ? 0.05 * fs + 2 : 0.3 * fs;
    const [il, itp, ir, ib] = hasInk ? [Math.min(...inkRects.map(q => q[0])), Math.min(...inkRects.map(q => q[1])),
      Math.max(...inkRects.map(q => q[2])), Math.max(...inkRects.map(q => q[3]))] : [l, t, r, b];
    const cw = W / (S.slides || 1), chh = H / (S.pages || 1);
    const kx = Math.min((S.slides || 1) - 1, Math.max(0, Math.floor((il + ir) / 2 / cw)));
    const ky = Math.min((S.pages || 1) - 1, Math.max(0, Math.floor((itp + ib) / 2 / chh)));
    const L = il - kx * cw, R = ir - kx * cw, T = itp - ky * chh, B = ib - ky * chh;
    if (L < -cut || T < -cut || R > cw + cut || B > chh + cut) issues.push('off-canvas');
    else if (L < sl - soft || T < st - soft || R > cw - sr + soft || B > chh - sb + soft) issues.push('outside-safe');
    const fb = fallbackScripts(fam, text);
    if (fb.length) issues.push('script-fallback:' + fb.join('+'));
    // text hidden under another element (a product cut-out, a shape, a scrim placed above it)
    // probe every ~0.18 em along each line at 40 % and 60 % height: two neighbouring hits = part of a letter hidden.
    // Only elements that paint count: transparent layout boxes stacked above the text (a .safe grid) do not.
    const covering = (x, y) => {
      // the topmost hit first: elementsFromPoint misses text that overflows its own box, elementFromPoint does not
      const top = document.elementFromPoint(x, y);
      if (!top || top === el || el.contains(top) || top.contains(el)) return null;
      for (const e of document.elementsFromPoint(x, y)) {
        if (e === el || el.contains(e) || e.contains(el)) return null;
        if (paints(e)) return e;
      }
      return null;
    };
    let hid = 0, worst = 0, probes = 0, coverer = null;
    const step = Math.max(4, parseFloat(cs.fontSize) * 0.18);
    for (const q of (() => { const rg = document.createRange(); rg.selectNodeContents(el); return [...rg.getClientRects()]; })()) {
      if (q.width < 2 || q.height < 2) continue;
      for (const fy of [0.4, 0.6]) {
        let run = 0;
        for (let x = q.left + step / 2; x < q.right; x += step) {
          const y = q.top + q.height * fy;
          if (x < 0 || y < 0 || x >= W || y >= H) continue;
          probes++;
          const cov = covering(x, y);
          if (cov) { hid++; run++; worst = Math.max(worst, run); coverer = coverer || selector(cov); }
          else run = 0;
        }
      }
    }
    if (worst >= 2) issues.push('covered:' + Math.round(100 * hid / probes) + ':' + coverer);
    const fill = el instanceof SVGElement ? cs.fill :
      (cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color ? cs.webkitTextFillColor : cs.color);
    const lh = cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight) / fs;
    const ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) / fs;
    const tag = el.tagName.toLowerCase();
    const script = Object.entries(SCRIPTS).filter(([k, rx]) => rx.test(text)).map(([k]) => k)[0] ||
      (/[A-Za-z]/.test(text) ? 'latin' : 'other');
    items.push({text: text.trim().replace(/\s+/g, ' ').slice(0, 200), sel: selector(el), tag, font: fam,
      font_missing: !hasFont(fam, cs.fontWeight, cs.fontStyle, text.trim()), size: +fs.toFixed(1), weight: cs.fontWeight,
      line_height: cs.lineHeight, lh_ratio: lh === null ? null : +lh.toFixed(2), ls_em: +ls.toFixed(3),
      lines: widths.length, last_line_frac: +lastFrac.toFixed(2), script,
      lang: (el.closest('[lang]') || document.documentElement).lang || null,
      upper: cs.textTransform === 'uppercase',
      color: rgba(fill), clip_text: cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text',
      effects: cs.textShadow !== 'none' || parseFloat(cs.webkitTextStrokeWidth || '0') > 0,
      opacity: +op.toFixed(2), box: [l, t, r, b].map(v => Math.round(v)), line_rects: lineRects,
      ink_rects: inkRects, issues,
      // text that is not copy: marked data-allow, or part of a logo lockup typeset in HTML
      allowed: !!el.closest('[data-allow], [data-logo], .logo, .wordmark, .logo-mark, .brandmark'),
      // the whole line or paragraph it belongs to: "The <em>36-hour</em> loaf" is one approved string
      block_text: (blk.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 400)});
  }
  const DPR = devicePixelRatio, imgs = [];
  const scaleOf = (fit, rw, rh, nw, nh) => fit === 'contain' ? Math.min(rw / nw, rh / nh) :
    fit === 'fill' || fit === '100% 100%' ? Math.max(rw / nw, rh / nh) : Math.max(rw / nw, rh / nh);
  for (const im of document.images) {
    const q = im.getBoundingClientRect();
    if (q.width * q.height === 0 || getComputedStyle(im).visibility !== 'visible') continue;
    const src = im.currentSrc || im.src;
    if (!im.complete || im.naturalWidth === 0) { imgs.push({src, broken: true}); continue; }
    const s = scaleOf(getComputedStyle(im).objectFit, q.width, q.height, im.naturalWidth, im.naturalHeight) * DPR;
    imgs.push({src, natural: [im.naturalWidth, im.naturalHeight], shown: [Math.round(q.width), Math.round(q.height)],
      upscale: +s.toFixed(2)});
  }
  const bgs = [];
  for (const el of document.querySelectorAll('*')) {
    const bi = getComputedStyle(el).backgroundImage;
    if (!bi || bi === 'none') continue;
    for (const m of bi.matchAll(/url\("?([^")]+)"?\)/g)) bgs.push([el, m[1]]);
  }
  for (const [el, src] of bgs) {
    const q = el.getBoundingClientRect(); if (q.width * q.height === 0) continue;
    const im = new Image(); im.src = src;
    try { await im.decode(); } catch (e) { imgs.push({src, broken: true, background: true}); continue; }
    const size = getComputedStyle(el).backgroundSize.split(',')[0].trim();
    const s = scaleOf(size === 'contain' ? 'contain' : 'cover', q.width, q.height, im.naturalWidth, im.naturalHeight) * DPR;
    imgs.push({src, natural: [im.naturalWidth, im.naturalHeight], shown: [Math.round(q.width), Math.round(q.height)],
      upscale: +s.toFixed(2), background: true});
  }
  // logos (data-logo, .logo, .wordmark, .logo-mark, .brandmark, or an <img> whose file or alt says logo): their
  // clear space is checked against text and graphics
  const logos = [];
  for (const el of document.querySelectorAll('[data-logo], .logo, .wordmark, .logo-mark, .brandmark, img')) {
    if (el.tagName === 'IMG' && !el.matches('[data-logo], .logo, .wordmark, .logo-mark, .brandmark') &&
        !/logo|wordmark|brandmark/i.test((el.currentSrc || el.src || '') + ' ' + (el.alt || ''))) continue;
    if (el.closest('[data-qa-ignore]') || [...logos].some(x => x.el.contains(el))) continue;
    const q = el.getBoundingClientRect(), cs = getComputedStyle(el);
    if (q.width * q.height === 0 || cs.visibility !== 'visible') continue;
    // a filter that recolours the logo (invert, hue-rotate...) instead of the supplied variant; shadows are fine
    const recolour = (cs.filter || 'none').replace(/drop-shadow\((?:[^()]|\([^()]*\))*\)/g, '').trim();
    logos.push({el, sel: selector(el), box: [q.left, q.top, q.right, q.bottom].map(v => Math.round(v)),
      filter: recolour && recolour !== 'none' ? recolour : null});
  }
  const cover = items.reduce((a, i) => a + (i.box[2] - i.box[0]) * (i.box[3] - i.box[1]), 0) / (W * H);
  return JSON.stringify({W, H, dpr: DPR, safe: S.safe, slides: S.slides || 1, pages: S.pages || 1, items, images: imgs, families: fams,
    logos: logos.map(({sel, box, filter}) => ({sel, box, filter})),
    brand: document.body.dataset.brand || (document.querySelector('link[href$="brand.css"]') || {}).href || null,
    text_coverage: +cover.toFixed(3), lang: document.documentElement.lang || null});
})()
"""
HIDE_TEXT_JS = r"""(() => { const s = document.createElement('style'); s.id = '__cd_hide';
  s.textContent = '*{color:transparent!important;-webkit-text-fill-color:transparent!important;' +
    'text-decoration-color:transparent!important;caret-color:transparent!important}' +
    'svg text,svg tspan,svg textPath{fill:transparent!important;stroke:transparent!important}';
  document.head.appendChild(s); return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(1)))); })()"""
SETTLE_JS = ("document.fonts.ready.then(() => Promise.all([...document.images].map(i => i.complete ? 0 : "
             "i.decode().catch(() => 0)))).then(() => window.__cdReady).then(() => document.fonts.ready)"
             ".then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(1)))))")


# ----------------------------------------------------------------------------- contrast from pixels
def _lum_lut():
    out = []
    for v in range(256):
        c = v / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return out


_LUT = _lum_lut()


def rel_lum(r: int, g: int, b: int) -> float:
    return 0.2126 * _LUT[r] + 0.7152 * _LUT[g] + 0.0722 * _LUT[b]


def contrast_ratio(l1: float, l2: float) -> float:
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def _ratio_ranks(lt: float, colours: list, *ranks: int) -> list:
    """Contrast ratios of a text luminance against pixels given as [(count, (r, g, b))], at the given ranks (from 0):
    the values a sorted list of every pixel's ratio has at those indexes, worked out once per colour."""
    import bisect
    tally = {}
    for n, rgb in colours:
        ratio = contrast_ratio(lt, rel_lum(*rgb))
        tally[ratio] = tally.get(ratio, 0) + n
    ratios, upto, seen = sorted(tally), [], 0
    for ratio in ratios:
        seen += tally[ratio]
        upto.append(seen)  # pixels with this ratio or a lower one
    return [ratios[bisect.bisect_right(upto, k)] for k in ranks]


def text_contrast(bg, box, color, rects: list | None = None, size: float = 0.0) -> dict | None:
    """Contrast of a text colour against the real pixels behind its glyphs (text hidden), line by line and inside
    the ink band (the font's content area reaches ~0.18 em above and below the letters): the 10th percentile is what
    the weakest tenth of the text sits on. Pixels are counted per colour (a flat ground is one colour, not thousands
    of pixels); the percentiles are the ones every pixel sorted one by one gives."""
    regs, parts = [], []
    pad = 0.18 * size
    step = max(40, 1.5 * size)  # word-sized pieces of each line: one word on a dark patch is not averaged away
    for rb in (rects or [box]):
        x0, y0, x1, y1 = [int(round(v)) for v in rb]
        if y1 - y0 > 2 * pad + 4:
            y0, y1 = int(round(y0 + pad)), int(round(y1 - pad))
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(bg.width, x1), min(bg.height, y1)
        if x1 - x0 < 2 or y1 - y0 < 2:
            continue
        reg = bg.crop((x0, y0, x1, y1)).convert("RGB")
        n = max(1, round((x1 - x0) / step))
        for k in range(n):
            a0, a1 = round(k * reg.width / n), round((k + 1) * reg.width / n)
            if a1 - a0 < 2:
                continue
            piece = reg.crop((a0, 0, a1, reg.height))
            piece.thumbnail((32, 32))
            parts.append(piece.getcolors(piece.width * piece.height))
        reg.thumbnail((140, 140))
        regs.append(reg)
    total = sum(reg.width * reg.height for reg in regs)
    if total < 4:
        return None
    r, g, b, a = color
    if a < 1:  # semi-transparent text sits on the median background
        px = [p for reg in regs for p in reg.getdata()]
        med = sorted(px, key=lambda p: rel_lum(*p))[len(px) // 2]
        r, g, b = (round(a * c + (1 - a) * m) for c, m in zip((r, g, b), med))
    lt = rel_lum(r, g, b)
    p10, median = _ratio_ranks(lt, [x for reg in regs for x in reg.getcolors(reg.width * reg.height)],
                               total // 10, total // 2)
    worst = min((_ratio_ranks(lt, part, sum(n for n, _ in part) // 2)[0] for part in parts if part), default=None)
    return {"p10": round(p10, 2), "median": round(median, 2),
            "worst_part": round(worst, 2) if worst is not None else None}


def text_ground(bg, rects: list, size: float) -> dict | None:
    """How clean the ground under the letters is (text hidden, inside the ink band): the share of the main colour
    and of pixels far from it. On a flat ground, far pixels are a line, a shape or a colour edge running behind the
    text, which contrast alone misses when it touches only a few letters."""
    pad = 0.18 * size
    worst = None
    for rb in rects:  # line by line: a stroke through one line of a long headline is diluted by the others
        x0, y0, x1, y1 = [int(round(v)) for v in rb]
        if y1 - y0 > 2 * pad + 4:
            y0, y1 = int(round(y0 + pad)), int(round(y1 - pad))
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(bg.width, x1), min(bg.height, y1)
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        reg = bg.crop((x0, y0, x1, y1))
        if reg.width * reg.height > 120_000:  # big display lines: half resolution is plenty
            reg = reg.resize((max(4, reg.width // 2), max(4, reg.height // 2)))
        total = reg.width * reg.height
        hist = {col: n for n, col in reg.point(lambda v: v & 0xF0).getcolors(1 << 16) or []}
        if total < 64 or not hist:
            continue
        dom = max(hist, key=hist.get)
        far = sum(n for col, n in hist.items() if sum((a - b) ** 2 for a, b in zip(col, dom)) > 56 ** 2)
        g = {"main": round(hist[dom] / total, 3), "far": round(far / total, 4)}
        if g["main"] >= 0.55 and (worst is None or g["far"] > worst["far"]):
            worst = g
    return worst


def text_busy(bg, rects: list, size: float) -> dict | None:
    """Edge energy behind each word-sized piece of each line (text hidden): a piece far busier than the rest of its
    line is a word running onto a shelf, a post, a face or other detail, even where contrast holds."""
    from PIL import ImageFilter, ImageStat
    step = max(40, 1.5 * size)
    pieces = []
    for rb in rects:
        x0, y0, x1, y1 = [int(round(v)) for v in rb]
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(bg.width, x1), min(bg.height, y1)
        if x1 - x0 < 8 or y1 - y0 < 6:
            continue
        g = bg.crop((x0, y0, x1, y1)).convert("L").filter(ImageFilter.FIND_EDGES)
        g = g.crop((1, 1, g.width - 1, g.height - 1))
        n = max(1, round(g.width / step))
        for k in range(n):
            a0, a1 = round(k * g.width / n), round((k + 1) * g.width / n)
            if a1 - a0 >= 4:
                pieces.append(ImageStat.Stat(g.crop((a0, 0, a1, g.height))).mean[0])
    if len(pieces) < 3:
        return None
    srt = sorted(pieces)
    return {"median": round(srt[len(srt) // 2], 1), "max": round(srt[-1], 1)}


def ring_ground(bg, box: list, gap: float) -> dict | None:
    """The ground in the clear-space ring around a box (a logo): its main colour share and the share far from it."""
    l, t, r, b = box
    strips = [(l - gap, t - gap, r + gap, t), (l - gap, b, r + gap, b + gap), (l - gap, t, l, b), (r, t, r + gap, b)]
    hist, total = {}, 0
    for x0, y0, x1, y1 in strips:
        x0, y0, x1, y1 = max(0, round(x0)), max(0, round(y0)), min(bg.width, round(x1)), min(bg.height, round(y1))
        if x1 - x0 < 2 or y1 - y0 < 2:
            continue
        reg = bg.crop((x0, y0, x1, y1))
        for n, col in reg.point(lambda v: v & 0xF0).getcolors(1 << 16) or []:
            hist[col] = hist.get(col, 0) + n
        total += reg.width * reg.height
    if total < 64 or not hist:
        return None
    dom = max(hist, key=hist.get)
    far = sum(n for col, n in hist.items() if sum((a - b) ** 2 for a, b in zip(col, dom)) > 56 ** 2)
    return {"main": round(hist[dom] / total, 3), "far": round(far / total, 4)}


# ----------------------------------------------------------------------------- render
def _preset_css(c: dict, slides: int = 1) -> str:
    import math
    # Chrome paints boxes on whole CSS px (an A5 page of 816.38 px paints 816), so print canvases are laid out at the
    # next whole pixel: the fraction lands in the bleed and the exact trim is cut from the render afterwards
    w, h = (math.ceil(c["w_px"] - 1e-6), math.ceil(c["h_px"] - 1e-6)) if c["print"] else (c["w_px"], c["h_px"])
    extra = ""
    for k, v in (c.get("css_vars") or {}).items():  # a preset's own measurements: a book wrap's spine, a dieline's panels
        if not re.fullmatch(r"--[a-z0-9-]+", str(k)) or not re.fullmatch(r"[-0-9A-Za-z.%#(), ]+", str(v)):
            die(f"preset {c.get('id')}: css_vars {k!r}: {v!r} is not a plain CSS variable and value")
        extra += f";{k}:{v}"
    # the text floor, so a pattern can keep its smallest line above it: font-size: max(…, var(--min-text)); labels,
    # dates and captions keep above --label-min (fine print may sit at --min-text); --view-scale is how much the
    # platform shrinks the canvas on a phone (0 in print), so a brand's minimum logo size in px can be kept at any
    # preset: width: max(…, var(--mark-min)) with the brand.css variables
    floor = f";--min-text:{float(c['min_text_px']):.2f}px" if c.get("min_text_px") else ""
    if c.get("min_text_px"):
        floor += f";--label-min:{label_floor(c):.2f}px"
    view_w = float(c.get("view_width_px") or 0)
    floor += f";--view-scale:{w / view_w:.4f}" if view_w and not c["print"] else ";--view-scale:0"
    return (f"--canvas-w:{w:.2f}px;--canvas-h:{h:.2f}px;--slides:{slides};--bleed:{c['bleed_px']:.2f}px;"
            f"--safe-top:{c['safe_px'][0]:.2f}px;--safe-right:{c['safe_px'][1]:.2f}px;"
            f"--safe-bottom:{c['safe_px'][2]:.2f}px;--safe-left:{c['safe_px'][3]:.2f}px" + floor + extra)


VISION_SIMS = ("deuteranopia", "protanopia", "tritanopia", "achromatopsia", "blurredVision", "reducedContrast")
MAX_TILE = 4096  # device px per capture side: big canvases are captured in tiles (Chrome paints smaller ones reliably)
MAX_CSS_AREA = 8192 * 8192  # CSS px of one page: at 10000x10000 Chrome paints nothing, even into a small capture


def capture(ch: Chrome, s: str, w_css: int, h_css: int, scale: float, fast: bool = True) -> bytes:
    """A PNG of the page's canvas; canvases larger than a tile (20-slide carousels, big posters at 300 dpi) are
    captured in tiles and stitched. Chrome now and then returns a big tile before it has painted it (a white
    8000 px square in an 8100 px page, 1 run in 4): every tile is compared with a small capture of the whole page,
    captured again when it does not match, and the run stops rather than write a file with a blank patch.
    fast: the PNG is only decoded again (the delivered file is re-saved by save_image), so Chrome compresses it
    for speed (optimizeForSpeed: the same pixels, 3 to 4 times faster, a larger stream); False keeps Chrome's
    smaller PNG for bytes written as they are (the vision simulations)."""
    def shot(x, y, w, h, k=1.0, beyond=True):
        p = {"format": "png", "clip": {"x": x, "y": y, "width": w, "height": h, "scale": k},
             "captureBeyondViewport": beyond}
        if fast:
            p["optimizeForSpeed"] = True
        return base64.b64decode(ch.send("Page.captureScreenshot", p, session=s, timeout=180)["data"])
    if w_css * scale <= MAX_TILE and h_css * scale <= MAX_TILE:
        return shot(0, 0, w_css, h_css, beyond=False)
    Image = need_pillow()
    from PIL import ImageChops, ImageStat
    import io
    k_ref = min(1.0, 1024 / (max(w_css, h_css) * scale))  # a reference of about 1024 px on its long side
    ref = Image.open(io.BytesIO(shot(0, 0, w_css, h_css, k_ref))).convert("RGB")
    rk = ref.width / w_css  # reference px per CSS px
    step = max(1, int(MAX_TILE // scale))
    full = Image.new("RGBA", (round(w_css * scale), round(h_css * scale)))
    for y0 in range(0, h_css, step):
        for x0 in range(0, w_css, step):
            w, h = min(step, w_css - x0), min(step, h_css - y0)
            box = (round(x0 * rk), round(y0 * rk), max(round(x0 * rk) + 1, round((x0 + w) * rk)),
                   max(round(y0 * rk) + 1, round((y0 + h) * rk)))
            want = ref.crop(box)
            for attempt in range(4):
                with Image.open(io.BytesIO(shot(x0, y0, w, h))) as tile:
                    tile = tile.convert("RGBA")
                got = tile.convert("RGB").resize(want.size, Image.BILINEAR)
                if ImageStat.Stat(ImageChops.difference(got, want).convert("L")).mean[0] < 24:
                    break
                ch.evaluate(s, "new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
                time.sleep(0.3 * (attempt + 1))
            else:
                die(f"Chrome kept returning an unpainted tile at {x0},{y0} ({w}x{h} CSS px) of this "
                    f"{w_css}x{h_css} page; render it smaller with a higher --scale, or as a .pdf")
            full.paste(tile, (round(x0 * scale), round(y0 * scale)))
    buf = io.BytesIO()
    full.save(buf, "PNG", **({"compress_level": 1} if fast else {}))
    return buf.getvalue()


def render_page(ch: Chrome, html: Path, c: dict, scale: float, transparent: bool, want_png: bool, want_pdf: bool,
                qa: bool, slides: int = 1, pages: int = 1, simulate: list | None = None, timeout: float = 60) -> dict:
    """Load one HTML file at the canvas size and return its PNG bytes, PDF bytes, a text-hidden background PNG
    (for contrast) and the page's own check results. Print canvases round up to whole CSS px; the raster is cropped
    to its exact size afterwards."""
    import math
    w_css, h_css = (math.ceil(c["w_px"] - 1e-6) * slides, math.ceil(c["h_px"] - 1e-6) * pages) if c["print"] else \
        (round(c["w_px"]) * slides, round(c["h_px"]) * pages)
    if w_css * h_css > MAX_CSS_AREA:
        die(f"the page is {w_css}x{h_css} CSS px ({w_css * h_css / 1e6:.0f} MP); above 8192x8192 Chrome paints "
            f"parts of it blank. Design at a smaller size and raise --scale (the same pixels), use a print preset "
            f"(mm sizes stay small in CSS px) or render fewer slides at a time")
    tid = ch.send("Target.createTarget", {"url": "about:blank"})["targetId"]
    s = None
    try:  # from here on the target is closed whatever fails, even the attach
        s = ch.send("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        ch.send("Page.enable", session=s)
        ch.send("Network.enable", session=s)
        ch.send("Emulation.setDeviceMetricsOverride", {"width": w_css, "height": h_css, "deviceScaleFactor": scale,
                                                        "mobile": False}, session=s)
        if transparent:
            ch.send("Emulation.setDefaultBackgroundColorOverride", {"color": {"r": 0, "g": 0, "b": 0, "a": 0}},
                    session=s)
        info = {"safe": c["safe_px"], "preset": c.get("id"), "slides": slides, "pages": pages}
        boot = (f"window.__CD={json.dumps(info)};document.addEventListener('DOMContentLoaded',()=>{{"
                f"const d=document.documentElement;d.dataset.preset={json.dumps(str(c.get('id')))};"
                f"d.style.cssText+=';{_preset_css(c, slides)};--pages:{pages}';}});")
        ch.send("Page.addScriptToEvaluateOnNewDocument", {"source": boot}, session=s)
        ch.send("Fetch.enable", {"patterns": [{"urlPattern": KIT_HOST + "*", "requestStage": "Request"}]}, session=s)
        ch.send("Page.navigate", {"url": html.resolve().as_uri()}, session=s)
        try:
            ch.wait("Page.loadEventFired", s, timeout=timeout)
        except TimeoutError:
            waiting = ch.network_log(s)["pending"]
            die(f"{html.name} did not finish loading in {timeout:g}s: " +
                (f"still waiting for {', '.join(u[-90:] for u in waiting[:3])}" if waiting else
                 "a script on the page is busy (an endless loop?)") + "; fix the page or raise --timeout")
        try:
            ch.evaluate(s, SETTLE_JS, timeout=timeout)
        except TimeoutError:
            die(f"{html.name} loaded but did not settle in {timeout:g}s: web fonts or images still loading, or "
                f"window.__cdReady never resolved; fix the page or raise --timeout")
        out = {"png": None, "pdf": None, "bg": None, "qa": None,
               "page_blocks": ch.evaluate(s, "document.querySelectorAll('.page').length")}
        if want_png:
            out["png"] = capture(ch, s, w_css, h_css, scale)
            # documents: each .page captured alone at the top of the viewport. Chrome snaps stacked pages at
            # fractional heights (A5 = 816.38 px) a device pixel early, which would leak one page into the next.
            if pages > 1 and ch.evaluate(s, "document.querySelectorAll('.page').length") == pages:
                show = ("(k => { document.querySelectorAll('.page').forEach((p, i) => p.style.display = "
                        "k < 0 || i === k ? '' : 'none'); return new Promise(r => requestAnimationFrame(() => "
                        "requestAnimationFrame(() => r(1)))); })")
                out["png_pages"] = []
                for k in range(pages):
                    ch.evaluate(s, f"{show}({k})")
                    out["png_pages"].append(capture(ch, s, w_css, h_css // pages, scale))
                ch.evaluate(s, f"{show}(-1)")
        if simulate:  # how the design reads with colour-vision deficiencies, in grey, and blurred (squint test)
            out["sims"] = {}
            for kind in simulate:
                if kind not in VISION_SIMS:
                    die(f"--simulate: unknown {kind!r}; choose from {', '.join(VISION_SIMS)}")
                ch.send("Emulation.setEmulatedVisionDeficiency", {"type": kind}, session=s)
                out["sims"][kind] = capture(ch, s, w_css, h_css, scale, fast=False)  # written as captured
            ch.send("Emulation.setEmulatedVisionDeficiency", {"type": "none"}, session=s)
        if want_pdf:
            # Chrome rounds paper sizes to 1/100 in, so print 1 mm larger and crop the boxes exactly afterwards
            pw, ph = (c["w_px"] + PX_PER_MM) / 96, (c["h_px"] + PX_PER_MM) / 96
            ch.evaluate(s, "(()=>{const s=document.createElement('style');s.textContent='@page{size:"
                           f"{pw * 25.4:.4f}mm {ph * 25.4:.4f}mm;margin:0}}';document.head.appendChild(s);"
                           "return 1})()")
            out["pdf"] = base64.b64decode(ch.send("Page.printToPDF", {
                "printBackground": True, "preferCSSPageSize": True, "displayHeaderFooter": False,
                "paperWidth": pw, "paperHeight": ph, "marginTop": 0, "marginBottom": 0, "marginLeft": 0,
                "marginRight": 0}, session=s, timeout=120)["data"])
        if qa:
            out["qa"] = json.loads(ch.evaluate(s, QA_JS, timeout=60))
            ch.evaluate(s, HIDE_TEXT_JS)
            ch.send("Emulation.setDeviceMetricsOverride", {"width": w_css, "height": h_css, "deviceScaleFactor": 1,
                                                            "mobile": False}, session=s)
            out["bg"] = capture(ch, s, w_css, h_css, 1)
        out["failed_loads"] = ch.network_log(s)["failed"]
        return out
    finally:
        try:
            ch.send("Target.closeTarget", {"targetId": tid}, timeout=10)
        except Exception:
            pass
        if s:
            ch.network_log(s)  # drop this page's leftover events


PLACEHOLDER_RX = re.compile(r"\b(lorem|ipsum|dolor sit|todo|tbd|placeholder|sample text|your (?:text|logo|headline|"
                            r"name|brand|title) here)\b|\[(?:insert|add|your)[^\]]*\]|\bx{3,}\b", re.I)
SLOP_RX = re.compile(r"\b(game[- ]chang\w*|revolutionar\w*|world[- ]class|cutting[- ]edge|seamlessly|elevate|"
                     r"unleash|next[- ]gen\w*|harness the power|in today'?s (?:fast|competitive|digital)|unlock (?:your|the)"
                     r" (?:full )?potential|to the next level|look no further|best[- ]in[- ]class)\b", re.I)
SOLEMN_WORDS = re.compile(r"\b(happy|congratulations?|congrats|celebrat\w*|mubarak|joyeux|feliz|felices|cheers)\b|"
                          r"শুভ|快乐|!|[\U0001F389\U0001F38A\U0001F973\U0001F386\U0001F387✨]", re.I)
FAST_WORDS = re.compile(r"\b(happy|congratulations?|celebrat\w*)\b", re.I)
COMMERCE_WORDS = re.compile(r"\d+\s?%|[$€£৳₹¥]\s?\d|\d\s?(?:tk|taka|usd|eur|bdt|inr)\b|\b(?:sale|offers?|discount|"
                            r"buy|shop now|order now|promo|coupon|voucher|deal|free shipping|limited time|"
                            r"\d+\s*off)\b", re.I)
DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")
QUOTES = {ord("“"): '"', ord("”"): '"', ord("„"): '"', ord("‘"): "'", ord("’"): "'"}


DENSE_SCRIPTS = ("bengali", "devanagari", "arabic")


def dash_issues(text: str, script: str = "") -> list:
    """Dashes readers take as the mark of AI-written copy, as [(severity, message)]. The rule lives in
    copyrules.dashes, so copy and rendered text are judged the same way."""
    return [(f["severity"], f"{f['message']}; {f['suggest']}") for f in copyrules.dashes(text, script)]


def norm_text(s: str) -> str:
    """NFC, one dash, one quote style, single spaces: how copy and rendered text are compared."""
    import unicodedata
    s = unicodedata.normalize("NFC", s).translate(DASHES).translate(QUOTES)
    return re.sub(r"\s+", " ", s.replace(" ", " ")).strip()


def load_copy(path) -> list:
    """copy.json: a list of strings, {role: text}, or {"locale": "BD", "platform": ..., "strings": [{"role", "text",
    "lang", "must_exact", "on_image"}]}."""
    try:
        data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read the copy file {path}: {e}")
    if isinstance(data, dict) and "strings" in data:
        data = data["strings"]
    elif isinstance(data, dict):
        data = [{"role": k, "text": v} for k, v in data.items() if isinstance(v, str)]
    if not isinstance(data, list):
        die(f"{path}: \"strings\" must be a list of strings or {{\"role\": ..., \"text\": ...}} objects, not "
            f"{type(data).__name__}")
    out = []
    for i, x in enumerate(data, 1):
        if isinstance(x, str):
            if x.strip():
                out.append({"role": "", "text": x, "must_exact": True})
        elif isinstance(x, dict):
            if not isinstance(x.get("text"), str):
                die(f"{path}: string {i} ({x.get('role') or 'no role'}) needs \"text\" as a string")
            if x["text"].strip():
                out.append(dict({"must_exact": True}, **x))
        else:
            die(f"{path}: string {i} is {type(x).__name__}; give a string or a {{\"role\", \"text\"}} object")
    if not out:
        die(f"{path} has no copy strings")
    return out


def copy_meta(path) -> dict:
    """The deck-wide fields of copy.json ("locale", "platform"), when it has them."""
    try:
        data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: data[k] for k in ("locale", "platform") if isinstance(data, dict) and isinstance(data.get(k), str)}


# Copy that never appears on the image: captions, alt text, the YouTube title, hashtags, notes. The deck keeps it
# (copylint and copyjudge read it); the render, judge, pairwise and OCR checks skip it.
OFF_IMAGE_ROLES = re.compile(r"^(?:caption|post_text|body_long|alt|alt_text|video_title|yt_title|youtube_title|"
                             r"hashtags?|first_comment)(?:[_-]?\d+)?$", re.I)  # anything else: on_image: false


def on_image(s: dict) -> bool:
    if "on_image" in s:
        return bool(s["on_image"])
    return not OFF_IMAGE_ROLES.match(str(s.get("role") or ""))


def image_copy(copy: list | None) -> list | None:
    """Only the strings that are set on the design."""
    return None if copy is None else [s for s in copy if on_image(s)]


@functools.lru_cache(maxsize=32)
def brand_minimums(uri: str | None) -> dict:
    """The brand's own minimum logo sizes from brand.json `min_size` ("24 px / 6 mm", "96 px wide / 25 mm"): px at
    the size people see a screen design, mm in print. Found from the brand file the design links (its brand.css sits
    next to brand.json); empty when there is none."""
    if not uri:
        return {}
    if uri.startswith(KIT_HOST):
        path = KIT_ROOT / uri[len(KIT_HOST):]
    elif uri.startswith("file://"):
        path = Path(urllib.parse.unquote(urllib.parse.urlparse(uri).path))
    else:
        return {}
    if path.suffix == ".css":
        path = path.with_name("brand.json")
    try:
        ms = json.loads(path.read_text(encoding="utf-8")).get("min_size") or {}
    except (OSError, ValueError, AttributeError):
        return {}
    out = {}
    for k in ("mark", "wordmark"):
        v = str(ms.get(k) or "") if isinstance(ms, dict) else ""
        for unit in ("px", "mm"):
            m = re.search(rf"(\d+(?:\.\d+)?)\s*{unit}", v)
            if m:
                out[f"{k}_{unit}"] = float(m.group(1))
    return out


# fine print may sit at the preset's floor; labels, dates and captions need about 13 % more on a canvas the platform
# shrinks (craft.md: 30 and 34 px on a 1080 post; the judges fail a 30-32 px date line the plain floor lets through).
# A unit seen at its own size (a web banner, an ad) keeps its floor.


def label_floor(c: dict) -> float:
    """The smallest size for labels, dates and captions on this preset."""
    base, view_w = float(c.get("min_text_px") or 0), float(c.get("view_width_px") or 0)
    shrunk = view_w and not c.get("print") and c["w_px"] / view_w > 1.2
    return base * 34 / 30 if shrunk else base



LEGAL_SEL = re.compile(r"legal|terms|fine|disclaim|credit|copyright|small-?print|foot-?note|source", re.I)
LEGAL_TEXT = re.compile(r"^\s*(?:\*|©|terms|t&cs?\b|offer (?:valid|ends)|conditions|valid until|see (?:terms|site))", re.I)


def review(qa: dict, bg_png: bytes | None, c: dict, copy: list | None = None, slides: int = 1,
           occasion: str | None = None, locale: str = "") -> dict:
    """Turn the page's raw measurements into errors and warnings a designer would act on. Checks the design judge
    fails a design for (safe zones, platform UI, dense script at viewing size, logo size and ground, contrast,
    unapproved text) are errors, so a render with errors is fixed before anyone spends a judge run on it (R6)."""
    errors, warnings = [], []
    copy = image_copy(copy)
    if occasion in ("solemn", "fast"):  # memorial and fast days: no greeting words, no selling
        for it in qa["items"]:
            words = SOLEMN_WORDS if occasion == "solemn" else FAST_WORDS
            m = words.search(it["text"])
            if m:
                errors.append(f"'{m.group(0)}' on a {occasion} day ('{it['text'][:50]}'): use the day's official name "
                              f"and a tribute or customary wish, no exclamation marks")
            m = COMMERCE_WORDS.search(it["text"]) if occasion == "solemn" else None
            if m:
                errors.append(f"selling on a solemn day ('{m.group(0)}' in '{it['text'][:50]}'): no prices, offers, "
                              f"CTAs or products; make any offer a separate creative on another day")
    min_px = float(c.get("min_text_px") or 0)
    large_px = float(c.get("large_text_px") or 48)
    canvas_w = qa["W"] / max(1, slides)
    pages = int(qa.get("pages") or 1)
    bg = None
    if bg_png:
        Image = need_pillow()
        import io
        bg = Image.open(io.BytesIO(bg_png)).convert("RGB")
    default_face = [it for it in qa["items"] if (it.get("font") or "").strip().lower() in ("times", "times new roman")]
    if default_face:
        # Times is the browser's default: a page whose font variables did not load looks like this, and nothing
        # else flags it because Times is installed
        warnings.append(f"{len(default_face)} text item{'' if len(default_face) == 1 else 's'} in Times, the browser's "
                        f"default ('{default_face[0]['text'][:30]}'): the page's fonts did not load; keep the pattern's "
                        f"stylesheet links and set --font-display and --font-text on :root")
    for i, it in enumerate(qa["items"]):
        tag = f"text {i + 1} '{it['text'][:40]}' ({it['sel']})"
        for iss in it["issues"]:
            if iss.startswith("clipped") or iss == "off-canvas":
                errors.append(f"{tag}: {iss.replace('-', ' ')}: the text is cut off")
            elif iss == "outside-safe":
                errors.append(f"{tag}: outside the safe zone ({c.get('id')}); platform UI or trimming covers it "
                              f"there")
            elif iss == "spills-x":
                warnings.append(f"{tag}: wider than its box (it spills out); give it room or reduce the size")
            elif iss == "fit-failed":
                errors.append(f"{tag}: does not fit its box even at the minimum data-fit size; shorten the copy "
                              f"or enlarge the box")
            elif iss.startswith("covered:"):
                _, pct, *who = iss.split(":", 2) + [""]
                errors.append(f"{tag}: about {pct} % of it is hidden under {who[0] or 'another element'}; move that "
                              f"element, put the text above it (z-index) or let it overlap only a non-letter area")
            elif iss.startswith("hyphen-break:"):
                word = iss.split(":", 1)[1]
                if re.search(r"\d[-–]\d", word):  # a range (7:00–14:00, 2025–26) never splits, at any size
                    warnings.append(f"{tag}: the range '{word}' is split across two lines; keep it together "
                                    f"(white-space: nowrap on it, or a shorter line)")
                elif it["size"] >= large_px * 0.8:  # display type; long body text may break at hyphens
                    warnings.append(f"{tag}: the line breaks inside '{word}' at its hyphen; keep the "
                                    f"compound together (a non-breaking hyphen ‑ or white-space: nowrap)")
            elif iss.startswith("weight-missing:"):
                _, want, have = iss.split(":", 2)
                warnings.append(f"{tag}: weight {want} is not a face of '{it['font']}' (it has {have.replace('/', ', ')}), "
                                f"so the browser draws the nearest one; set a weight the family has (the brand's)")
            elif iss.startswith("script-fallback:"):
                warnings.append(f"{tag}: '{it['font']}' has no {iss.split(':', 1)[1]} glyphs, so a system font draws "
                                f"them; put a matching font first for that text (e.g. a --font-bengali variable)")
        if it["font_missing"]:
            errors.append(f"{tag}: font '{it['font']}' is not available; the browser used a fallback")
        if min_px and it["size"] < min_px:
            warnings.append(f"{tag}: {it['size']}px is below the {min_px:g}px minimum for {c.get('id')}" +
                            (f" ({c['distance_floor']})" if c.get("distance_floor") else ""))
        elif min_px and it["size"] < label_floor(c) - 0.05 and not LEGAL_SEL.search(it["sel"] or "") \
                and not LEGAL_TEXT.search(it["text"]):
            warnings.append(f"{tag}: {it['size']}px is under the {label_floor(c):.0f}px floor for labels, dates "
                            f"and captions on {c.get('id')} ({min_px:g}px is for fine print only: mark that "
                            f"class=\"legal\")")
        # Bengali, Devanagari and Arabic letters are denser than Latin at the same px size: the art-director judge
        # failed Bengali supporting text at 26-30 px on 1080-1200 px canvases that passed the Latin floor (Sutokotha,
        # 2026-09-24). Such text needs about 12 px at the size people see it.
        view_px = float(c.get("view_width_px") or 0)
        if view_px and not c["print"] and it.get("script") in ("bengali", "devanagari", "arabic"):
            seen = it["size"] * view_px / canvas_w
            if seen < 12:
                errors.append(f"{tag}: {it['script']} text at {it['size']}px is {seen:.1f} px at viewing size "
                                f"({view_px:.0f} px wide); dense scripts need about 12 px there, so set it at ≥ "
                                f"{-(-12 * canvas_w // view_px):.0f}px")
        big = it["size"] >= large_px * 0.8
        # display type (headlines) for leading: by its size on the canvas on screen; from 18 pt in print (panels and
        # pages are read at arm's length whatever the sheet size)
        disp = it["size"] >= (large_px if c["print"] else 0.045 * canvas_w) or \
            it.get("tag") in ("h1", "h2")  # marked as headlines (serif display faces are often weight 400)
        wt = int(it["weight"]) if str(it["weight"]).isdigit() else 400
        if PLACEHOLDER_RX.search(it["text"]):
            errors.append(f"{tag}: placeholder text left in the design")
        if it.get("script") in ("bengali", "devanagari", "arabic") and abs(it.get("ls_em") or 0) > 0.001:
            warnings.append(f"{tag}: letter-spacing on {it['script']} text breaks conjuncts and joins; set "
                            f"letter-spacing: normal for it")
        if it.get("lines", 1) >= 2:
            need = (1.25 if disp else 1.45) if it.get("script") in ("bengali", "devanagari", "arabic") else \
                (0.85 if disp else 1.1 if it["size"] >= (16 if c["print"] else 0.035 * canvas_w) else 1.25)
            if it.get("lh_ratio") is None:
                warnings.append(f"{tag}: line-height is 'normal' (the font's default, anything from 1.0 to 2.4); "
                                f"set it explicitly")
            elif it["lh_ratio"] < need:
                warnings.append(f"{tag}: line-height {it['lh_ratio']} is tight for {it.get('script')} "
                                f"{'display' if disp else 'body'} text (use ≥ {need})")
            if disp and it.get("last_line_frac", 1) < 0.25:
                warnings.append(f"{tag}: the headline ends with a very short last line (a runt); rebalance the "
                                f"break (text-wrap: balance) or edit the copy")
            elif not disp and it.get("lines") == 2 and it.get("last_line_frac", 1) < 0.2:
                warnings.append(f"{tag}: a two-line text ends with one short word on its own line; rebalance it "
                                f"(text-wrap: balance), widen the box or break it where the sense breaks")
        if (it.get("ls_em") or 0) < -0.045:
            warnings.append(f"{tag}: tracking {it['ls_em']}em is tighter than -0.04em; letters start to collide")
        if wt < 400 and it["size"] < large_px:
            warnings.append(f"{tag}: weight {wt} at {it['size']}px is too thin to read at display size")
        t_raw = it["text"]
        if '"' in t_raw or re.search(r"(?<=[A-Za-z])'(?=[A-Za-z])", t_raw):
            warnings.append(f"{tag}: straight quotes or apostrophes; typeset them as “ ” and ’")
        if "..." in t_raw:
            warnings.append(f"{tag}: use the ellipsis character … instead of three dots")
        for sev_d, msg in dash_issues(t_raw, it.get("script") or ""):
            (errors if sev_d == "error" else warnings).append(f"{tag}: {msg}")
        sev = "error" if any(x.startswith(("clipped", "covered")) or x in ("off-canvas", "fit-failed")
                             for x in it["issues"]) or it["font_missing"] else ("warning" if it["issues"] or (min_px and it["size"] < min_px) else "ok")
        if bg is not None and not it["clip_text"]:
            ct = text_contrast(bg, it["box"], it["color"], it.get("ink_rects") or it.get("line_rects"),
                               0.0 if it.get("ink_rects") else it["size"])
            if ct:
                bold = str(it["weight"]).isdigit() and int(it["weight"]) >= 600
                large = it["size"] >= float(c.get("large_text_px") or 48) * (0.8 if bold else 1)
                need = 3.0 if large else 4.5
                it["contrast"] = dict(ct, needs=need)
                if ct["p10"] < need:
                    errors.append(f"{tag}: contrast {ct['p10']}:1 over its background (needs {need}:1); add a "
                                  f"scrim, move it to a calmer area or change the colour")
                    sev = "error"
                elif ct.get("worst_part") is not None and ct["worst_part"] < need:
                    # the text as a whole reads, but a word of it sits on a darker or busier patch
                    hard = ct["worst_part"] < need * 0.66
                    (errors if hard else warnings).append(
                        f"{tag}: part of it sits on a patch where contrast drops to {ct['worst_part']}:1 (needs "
                        f"{need}:1): a word runs onto a busier or darker area; keep every word on the calm ground, "
                        f"narrow the box or extend the scrim")
                    sev = "error" if hard else ("warning" if sev == "ok" else sev)
            bz = None if it.get("effects") else text_busy(bg, it.get("ink_rects") or it.get("line_rects") or [it["box"]],
                                                          it["size"])
            if bz:
                it["busy"] = bz
            if bz and bz["max"] >= 10 and bz["max"] >= 2.5 * max(bz["median"], 2):  # calibrated on real plates
                warnings.append(f"{tag}: one word of it runs onto a detailed part of the image (edges {bz['max']:g} there "
                                f"against {bz['median']:g} behind the rest); keep the text on the calm area or narrow its "
                                f"box")
                sev = "warning" if sev == "ok" else sev
            gr = None if it.get("effects") else text_ground(bg, it.get("ink_rects") or it.get("line_rects") or [it["box"]],
                                                            0.0 if it.get("ink_rects") else it["size"])
            if gr and gr["main"] >= 0.55 and gr["far"] >= 0.003:
                it["ground"] = gr
                warnings.append(f"{tag}: a line, shape or colour edge runs behind the letters ({gr['far'] * 100:.1f} % "
                                f"of the text area differs sharply from its ground); move the text or the graphic so "
                                f"every letter sits on one clean ground (fine for a deliberate highlight or underline)")
                sev = "warning" if sev == "ok" else sev
        if c["print"]:  # prepress: how small text survives four printing plates
            r0, g0, b0 = it["color"][:3]
            if it["size"] < 16 and max(r0, g0, b0) <= 60 and (r0, g0, b0) != (0, 0, 0):
                warnings.append(f"{tag}: small near-black text ({it['size'] * 0.75:.1f} pt, rgb {r0},{g0},{b0}) prints "
                                f"as four-colour black and blurs when the plates shift; set it to #000 so the "
                                f"printer's RIP prints it in black only")
            if it["size"] < 12 and rel_lum(r0, g0, b0) > 0.5 and wt < 600 and \
                    (it.get("contrast") or {}).get("median", 0) >= 2:
                warnings.append(f"{tag}: small reversed text ({it['size'] * 0.75:.1f} pt, weight {wt}) fills in on "
                                f"press; use ≥ 9 pt and a medium or bold weight for light text on colour")
        it["severity"] = sev
    items = qa["items"]
    # text that collides with other text
    def ink(it):  # where the letters are: measured per line by the page, else ~0.18 em inside the content area
        if it.get("ink_rects"):
            rs = it["ink_rects"]
            return [min(q[0] for q in rs), min(q[1] for q in rs), max(q[2] for q in rs), max(q[3] for q in rs)]
        l, t, r, b = it["box"]
        pad = 0.18 * it["size"]
        return [l, t + pad, r, max(t + pad, b - pad)]
    def overlap(ra, rb):  # the larger share of the smaller of two boxes that the other covers
        ix, iy = min(ra[2], rb[2]) - max(ra[0], rb[0]), min(ra[3], rb[3]) - max(ra[1], rb[1])
        if ix <= 0 or iy <= 0:
            return 0.0
        return ix * iy / (min((ra[2] - ra[0]) * (ra[3] - ra[1]), (rb[2] - rb[0]) * (rb[3] - rb[1])) or 1)
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i].get("clip_text") or items[j].get("clip_text") or overlap(ink(items[i]), ink(items[j])) <= 0.08:
                continue
            # line by line: a headline's own words and a span inside it share one union box without touching
            ra, rb = items[i].get("ink_rects") or [ink(items[i])], items[j].get("ink_rects") or [ink(items[j])]
            if max(overlap(x, y) for x in ra for y in rb) > 0.08:
                warnings.append(f"text {i + 1} '{items[i]['text'][:30]}' overlaps text {j + 1} "
                                f"'{items[j]['text'][:30]}'")
    # platform UI inside the canvas (duration badge, profile photo): text and logos stay out of it, and the photo's
    # subject should not sit under it either (the LinkedIn avatar covered the weaver on Sutokotha's banner)
    def meets(a, zone):
        return min(a[2], zone[2]) > max(a[0], zone[0]) and min(a[3], zone[3]) > max(a[1], zone[1])
    whys = c.get("keepout_why") or []
    for zi, zone in enumerate(c.get("keepout") or []):
        why = whys[zi] if zi < len(whys) and whys[zi] else "platform UI (badge, avatar) covers it there"
        for i, it in enumerate(items):
            if meets(ink(it), zone):
                errors.append(f"text {i + 1} '{it['text'][:30]}' is inside a keep-out zone of {c.get('id')} "
                              f"{[round(v) for v in zone]}: {why}")
        for lg in qa.get("logos") or []:
            if meets(lg["box"], zone):
                errors.append(f"the logo ({lg['sel']}) is inside a keep-out zone of {c.get('id')} "
                              f"{[round(v) for v in zone]}: {why}")
        if bg is not None:
            from PIL import ImageFilter, ImageStat
            x0, y0 = max(0, round(zone[0])), max(0, round(zone[1]))
            x1, y1 = min(bg.width, round(zone[2])), min(bg.height, round(zone[3]))
            if x1 - x0 > 8 and y1 - y0 > 8:
                e = bg.crop((x0, y0, x1, y1)).convert("L").filter(ImageFilter.FIND_EDGES)
                energy = ImageStat.Stat(e.crop((1, 1, e.width - 1, e.height - 1))).mean[0]
                if energy >= 14:
                    warnings.append(f"the image is detailed under the keep-out zone {[round(v) for v in zone]} (edges "
                                    f"{energy:.0f}): {why}, so part of the picture is covered or lost there; if that "
                                    f"is the subject, reframe the photo")
    # logos must still read at the size people see the design (a thumbnail is ~168-360 px wide on a phone)
    view_w = float(c.get("view_width_px") or 0)
    bmin = brand_minimums(qa.get("brand"))
    for lg in qa.get("logos") or []:
        l, t, r, b = lg["box"]
        wide = (r - l) >= 2 * (b - t)  # a wordmark reads by its width (brand minimums) or height; a mark by its side
        kind, size = ("wordmark", r - l) if wide else ("mark", min(r - l, b - t))
        need = bmin.get(f"{kind}_mm" if c["print"] else f"{kind}_px")
        if need and (c["print"] or view_w):  # the brand's own minimum: px at viewing size, mm in print
            have = size / PX_PER_MM if c["print"] else size * view_w / canvas_w
            if have < need - 0.5:  # the page reports whole pixels
                unit = "mm" if c["print"] else f"px at viewing size ({view_w:.0f} px wide)"
                grow = need * PX_PER_MM if c["print"] else need * canvas_w / view_w
                errors.append(f"the {kind} ({lg['sel']}) is {have:.0f} {unit}, under the brand's minimum of "
                              f"{need:g} {'mm' if c['print'] else 'px'}{' wide' if wide else ''}: set it to ≥ "
                              f"{grow:.0f} px {'wide' if wide else 'on its smaller side'} here")
            continue
        if view_w and not c["print"]:
            floor = 10 if wide else 16
            seen = min(r - l, b - t) * view_w / canvas_w
            if seen < floor:
                errors.append(f"the logo ({lg['sel']}) is {seen:.0f} px at viewing size ({view_w:.0f} px wide): "
                                f"too small to recognise; enlarge it to ≥ {floor * canvas_w / view_w:.0f} px or leave "
                                f"it out and let the platform's avatar carry the brand")
    # folds: text keeps 4 mm from every fold (it cracks or sinks into the fold); side k of a --pages N render uses
    # the folds of side k (outside, inside)
    if c.get("folds_px"):
        page_h = qa["H"] / pages
        for i, it in enumerate(items):
            k = min(pages - 1, int((it["box"][1] + it["box"][3]) / 2 // page_h))
            for fx in c["folds_px"][min(k, len(c["folds_px"]) - 1)]:
                a = ink(it)
                gap_mm = float(c.get("fold_gap_mm") or 4)  # 4 mm at a brochure fold; a book spine's own margin
                gap = gap_mm * PX_PER_MM
                if a[0] < fx + gap and a[2] > fx - gap:
                    where = "crosses" if a[0] < fx < a[2] else f"is within {gap_mm:g} mm of"
                    warnings.append(f"text {i + 1} '{it['text'][:30]}' {where} the fold at "
                                    f"{(fx - c['bleed_px']) / PX_PER_MM:.1f} mm (side {k + 1}); keep it inside its panel")
    # a colour change right on a fold: folds and spines drift (KDP and IngramSpark allow 1/16 in), so a sliver of
    # the wrong colour shows on the spine or on the next panel
    if bg is not None and c.get("folds_px"):
        from PIL import ImageStat
        page_h, near, far = qa["H"] / pages, 0.5 * PX_PER_MM, 3 * PX_PER_MM
        for k in range(pages):
            y0, y1 = round(k * page_h + c["bleed_px"]), round((k + 1) * page_h - c["bleed_px"])
            for fx in c["folds_px"][min(k, len(c["folds_px"]) - 1)]:
                a = bg.crop((max(0, round(fx - far)), y0, round(fx - near), y1))
                b = bg.crop((round(fx + near), y0, min(bg.width, round(fx + far)), y1))
                if min(a.width, b.width, a.height) < 1:
                    continue
                ma, mb = ImageStat.Stat(a).mean, ImageStat.Stat(b).mean
                if sum((p - q) ** 2 for p, q in zip(ma, mb)) ** 0.5 > 60:
                    warnings.append(f"the colour changes right at the fold at {(fx - c['bleed_px']) / PX_PER_MM:.1f} mm "
                                    f"(side {k + 1}): folds and spines drift up to 1.6 mm, so a sliver of the wrong "
                                    f"colour can show; carry one colour across the fold, or move the change at least "
                                    f"3 mm onto a panel")
    # logo clear space: half the logo's height (its smaller side) kept free of text and graphics on every side
    for lg in qa.get("logos") or []:
        l, t, r, b = lg["box"]
        gap = 0.5 * min(r - l, b - t)
        for i, it in enumerate(items):
            a = ink(it)
            if a[0] >= l - 1 and a[2] <= r + 1 and a[1] >= t - 1 and a[3] <= b + 1:
                continue  # text that is part of the logo (an HTML lockup)
            if min(a[2], r + gap) > max(a[0], l - gap) and min(a[3], b + gap) > max(a[1], t - gap):
                warnings.append(f"text {i + 1} '{it['text'][:30]}' is inside the clear space of the logo "
                                f"({lg['sel']}); keep half the logo's height free around it")
        rg = ring_ground(bg, lg["box"], gap) if bg is not None else None
        if rg and rg["main"] >= 0.55 and rg["far"] >= 0.01:
            warnings.append(f"a graphic or colour edge runs into the clear space of the logo ({lg['sel']}, "
                            f"{rg['far'] * 100:.0f} % of it); move the graphic or the logo")
        elif bg is not None:  # on a photo: the logo needs a calm patch, not the subject's detail
            from PIL import ImageFilter, ImageStat
            tot, area = 0.0, 0
            for sx0, sy0, sx1, sy1 in ((l - gap, t - gap, r + gap, t), (l - gap, b, r + gap, b + gap),
                                       (l - gap, t, l, b), (r, t, r + gap, b)):  # the ring only, not the logo itself
                sx0, sy0, sx1, sy1 = max(0, round(sx0)), max(0, round(sy0)), min(bg.width, round(sx1)), min(bg.height, round(sy1))
                if sx1 - sx0 < 4 or sy1 - sy0 < 4:
                    continue
                e = bg.crop((sx0, sy0, sx1, sy1)).convert("L").filter(ImageFilter.FIND_EDGES)
                e = e.crop((1, 1, e.width - 1, e.height - 1))
                tot += ImageStat.Stat(e).mean[0] * e.width * e.height
                area += e.width * e.height
            if area:
                energy = tot / area
                lg["busy"] = round(energy, 1)
                if energy >= 12:
                    errors.append(f"the logo ({lg['sel']}) sits on a detailed part of the image (edges {energy:.0f}); "
                                  f"move it to a calm area, onto a solid band, or use a plate behind it")
        if lg.get("filter"):
            warnings.append(f"the logo ({lg['sel']}) is recoloured with a CSS filter ({lg['filter'][:60]}); use the "
                            f"brand's supplied variant (reversed or one-colour file) instead")
    # carousel seams: nothing written across or right next to the cut between slides
    if slides > 1:
        sw = qa["W"] / slides
        for i, it in enumerate(items):
            for k in range(1, slides):
                x = k * sw
                if it["box"][0] < x + 40 and it["box"][2] > x - 40:
                    warnings.append(f"text {i + 1} '{it['text'][:30]}' crosses or touches the seam between slides "
                                    f"{k} and {k + 1}; keep text ≥ 40 px from every cut")
    # hierarchy: few sizes, clearly different steps. Carousels are judged slide by slide and documents page by page
    # (the set may use a few more sizes); folded sheets and book wraps panel by panel on every side, because each panel
    # is read on its own (a spine on the shelf, a front in a store), so their size steps are compared within a panel
    sizes = sorted({round(it["size"]) for it in items})
    steps = list(zip(sizes, sizes[1:]))
    folds_px = c.get("folds_px") or [] if slides == 1 else []
    frames = []  # (label, x0, y0, x1, y1)
    if slides > 1:
        sw = qa["W"] / slides
        frames = [(f"slide {k + 1}", k * sw, 0.0, (k + 1) * sw, float(qa["H"])) for k in range(slides)]
    else:
        ph = qa["H"] / pages
        for k in range(pages):
            side = sorted(folds_px[min(k, len(folds_px) - 1)]) if folds_px else []
            edges = [0.0, *side, float(qa["W"])]
            for j in range(len(edges) - 1):
                label = ", ".join(x for x in (f"page {k + 1}" if pages > 1 else "", f"panel {j + 1}" if side else "")
                                  if x)
                frames.append((label, edges[j], k * ph, edges[j + 1], (k + 1) * ph))
    if len(frames) > 1:
        if folds_px:
            steps = []
        for label, x0, y0, x1, y1 in frames:
            per = sorted({round(it["size"]) for it in items if x0 <= (it["box"][0] + it["box"][2]) / 2 < x1 and
                          y0 <= (it["box"][1] + it["box"][3]) / 2 < y1})
            if len(per) > 5:
                warnings.append(f"{label} uses {len(per)} text sizes ({', '.join(map(str, per))} px); keep 3–4")
            if folds_px:
                steps += zip(per, per[1:])
        if len(sizes) > 7:
            word = "panels" if folds_px else "slides" if slides > 1 else "pages"
            warnings.append(f"the {word} use {len(sizes)} text sizes in total; keep one type scale across them")
    elif len(sizes) > 5:
        warnings.append(f"{len(sizes)} different text sizes ({', '.join(map(str, sizes))} px); a clear hierarchy "
                        f"uses 3–4")
    for a, b in steps:
        if b / a < 1.12:
            warnings.append(f"text sizes {a} and {b} px are too close to read as different levels; make the step "
                            f"≥ 1.25 or use one size")
    # generic marketing phrases in copy that is ours, not the client's approved copy
    approved = [norm_text(s["text"]).casefold() for s in (copy or [])]
    for i, it in enumerate(items):
        m = SLOP_RX.search(it["text"])
        if m and not any(norm_text(it["text"]).casefold() in a for a in approved):
            warnings.append(f"text {i + 1}: '{m.group(0)}' is generic marketing language that reads as template/AI "
                            f"copy; say something specific")
        # bookish, translated or West Bengal wording in Bengali that is ours (copylint checks the deck earlier)
        if it.get("script") == "bengali" and not any(norm_text(it["text"]).casefold() in a for a in approved):
            for f in copyrules.lint_string(it["text"], "", locale):
                if f["code"] in ("bn-formal", "bn-pattern", "bn-locale"):
                    warnings.append(f"text {i + 1} '{it['text'][:30]}': {f['message']}; {f['suggest']}")
    # the approved copy, exactly once, and nothing else written
    copy_report = None
    if copy:
        corpus = " ".join(norm_text(it["text"]) for it in items)
        blocks = " | ".join(dict.fromkeys(norm_text(it.get("block_text") or "") for it in items))
        missing, dup, case = [], [], []
        for s in copy:
            t = norm_text(s["text"])
            n = corpus.count(t) or (1 if t in blocks else 0)  # a string split over inline elements counts once
            if n == 0:
                (case if t.casefold() in (corpus + " | " + blocks).casefold() else missing).append(t)
            elif n > 1 and s.get("must_exact", True) and not s.get("repeat"):
                dup.append(t)

        def leftover(t):
            rem = norm_text(t).casefold()
            for a in sorted(approved, key=len, reverse=True):
                rem = rem.replace(a, " ")
            return re.sub(r"[\W_]+", "", rem)
        extra = []
        for it in items:
            if it.get("allowed") or not leftover(it["text"]) or \
                    any(norm_text(it["text"]).casefold() in a for a in approved) or \
                    (it.get("block_text") and not leftover(it["block_text"])):
                continue
            extra.append(it["text"][:80])
        for t in missing:
            errors.append(f"approved copy missing or altered: '{t[:80]}'")
        for t in case:
            warnings.append(f"approved copy differs in letter case: '{t[:80]}' (type the copy as approved; use "
                            f"text-transform for caps)")
        for t in dup:
            warnings.append(f"approved copy appears more than once: '{t[:80]}'")
        for t in extra:
            errors.append(f"text that is not in the approved copy: '{t}' (add it to copy.json, or mark a fixed "
                          f"element such as a slide counter data-allow)")
        copy_report = {"strings": len(copy), "missing": missing, "case_only": case, "duplicated": dup, "extra": extra}
    fams = [f for f in qa["families"] if not re.match(r"^(serif|sans-serif|monospace|system-ui)$", f)]
    if len(fams) > 3:
        warnings.append(f"{len(fams)} font families ({', '.join(fams)}); professional sets use 1–2 (3 at most)")
    for im in qa["images"]:
        vector = re.search(r"\.svg(?:[?#]|$)|^data:image/svg", im.get("src", ""), re.I)
        if im.get("broken"):
            errors.append(f"image did not load: {short_url(im.get('src', ''))}")
        elif vector or not im.get("upscale"):
            continue
        elif c["print"]:  # effective resolution on paper
            ppi = 96 * float(qa.get("dpr") or 1) / im["upscale"]
            want = distance_ppi(c)
            if ppi < want:
                seen = f"at {c['view_distance_m']:g} m" if c.get("view_distance_m") else "in hand"
                (errors if ppi < want * 0.625 else warnings).append(
                    f"image prints at {ppi:.0f} ppi ({want:.0f} wanted {seen}): {im['src'][-80:]}; use a larger "
                    f"file, show it smaller, or regenerate/upscale it for print")
        elif im["upscale"] > 1.25:
            warnings.append(f"image shown {im['upscale']}x larger than its pixels (soft/blurry): {im['src'][-80:]}")
    out = {"ok": not errors, "errors": errors, "warnings": warnings, "sizes_px": sizes}
    if copy_report:
        out["copy"] = copy_report
    return out


def draw_overlay(png: bytes, qa: dict, c: dict, out: Path, scale: float) -> None:
    """A review copy: safe zone in cyan, text boxes green (fine), amber (warning) or red (error)."""
    Image = need_pillow()
    from PIL import ImageDraw
    import io
    im = Image.open(io.BytesIO(png)).convert("RGB")
    d = ImageDraw.Draw(im)
    k = im.width / qa["W"]
    t, r, b, l = c["safe_px"]
    nx, ny = qa.get("slides") or 1, qa.get("pages") or 1
    cw, chh = im.width / nx, im.height / ny  # one frame per slide or page
    for ix in range(nx):
        for iy in range(ny):
            x0, y0 = ix * cw, iy * chh
            if any(c["safe_px"]):
                d.rectangle([x0 + l * k, y0 + t * k, x0 + cw - r * k, y0 + chh - b * k], outline=(0, 200, 255),
                            width=max(2, int(3 * k)))
            if c.get("bleed_px"):
                bp = c["bleed_px"] * k
                d.rectangle([x0 + bp, y0 + bp, x0 + cw - bp, y0 + chh - bp], outline=(255, 0, 255),
                            width=max(1, int(2 * k)))
    for iy, side in enumerate((c.get("folds_px") or [])[:ny]):  # folds, dashed
        for fx in side:
            for y in range(int(iy * chh), int((iy + 1) * chh), int(24 * k) or 1):
                d.line([fx * k, y, fx * k, min((iy + 1) * chh, y + 12 * k)], fill=(255, 0, 255), width=max(1, int(2 * k)))
    for zone in c.get("keepout") or []:  # platform UI (badge, avatar)
        d.rectangle([v * k for v in zone], outline=(230, 30, 30), width=max(2, int(3 * k)))
        d.line([zone[0] * k, zone[1] * k, zone[2] * k, zone[3] * k], fill=(230, 30, 30), width=max(1, int(2 * k)))
    for i, it in enumerate(qa["items"]):
        col = {"error": (230, 30, 30), "warning": (255, 170, 0)}.get(it.get("severity"), (40, 200, 90))
        x0, y0, x1, y1 = [v * k for v in it["box"]]
        d.rectangle([x0, y0, x1, y1], outline=col, width=max(2, int(2 * k)))
        d.text((x0 + 3, max(0, y0 - 14 * k)), str(i + 1), fill=col)
    im.save(out)


_ICC: dict = {}


def srgb_icc():
    """An sRGB ICC profile, embedded in every raster so colour-managed apps and printers read the colours right."""
    if "v" not in _ICC:
        try:
            from PIL import ImageCms
            _ICC["v"] = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        except Exception:
            _ICC["v"] = None
    return _ICC["v"]


_SAVE_LOCK = threading.Lock()
_ENCODER: dict = {}


def encoder():
    """Worker threads that write images: Pillow's encoders release the GIL, so the files of one render encode side
    by side while its checks run (a 1080x1350 photo takes about 0.7 s as a compress-level-9 PNG)."""
    with _SAVE_LOCK:
        if "pool" not in _ENCODER:
            from concurrent.futures import ThreadPoolExecutor
            _ENCODER["pool"] = ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2),
                                                  thread_name_prefix="codex-design-encode")
    return _ENCODER["pool"]


def save_image(png, out: Path, fmt: str, quality: int, max_bytes: int | None, tag_composite: bool,
               dpi: float | None = None, size: tuple | None = None) -> dict:
    """Chrome's PNG (bytes, or the image already decoded) re-saved through Pillow with an sRGB profile: PNG, or
    JPG/WebP where a byte limit lowers the quality until it fits. Print rasters are cropped to their exact pixel size
    and carry their dpi. Safe to run in several threads at once (encoder())."""
    out.parent.mkdir(parents=True, exist_ok=True)
    Image = need_pillow()
    from PIL import ImageFile
    import io
    im = Image.open(io.BytesIO(png)) if isinstance(png, bytes) else png
    if size and im.size != tuple(size):
        im = im.crop((0, 0, min(size[0], im.width), min(size[1], im.height)))
    with _SAVE_LOCK:  # only ever raised, so a save running beside this one keeps the room it asked for
        ImageFile.MAXBLOCK = max(ImageFile.MAXBLOCK, im.width * im.height * 4)  # progressive JPEG of grainy images
    extra = {"dpi": (dpi, dpi)} if dpi else {}
    if srgb_icc():
        extra["icc_profile"] = srgb_icc()
    if tag_composite:
        if fmt == "png":
            from PIL import PngImagePlugin
            info = PngImagePlugin.PngInfo()
            info.add_itxt("XML:com.adobe.xmp", COMPOSITE_XMP)
            extra["pnginfo"] = info
        else:
            extra["xmp"] = COMPOSITE_XMP.encode("utf-8")
    if fmt == "png":
        buf = io.BytesIO()
        # level 6: the same pixels as optimize=True (PNG is lossless) about 12 times faster, in files about 8 % larger
        im.save(buf, "PNG", compress_level=6, **extra)
        write_atomic(out, buf.getvalue())
        return {"path": str(out), "bytes": buf.tell(), "size": list(im.size)}
    rgb = im.convert("RGB") if fmt == "jpg" else im
    q = quality
    while True:
        buf = io.BytesIO()
        if fmt == "jpg":
            rgb.save(buf, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q >= 90 else 2, **extra)
        else:
            rgb.save(buf, "WEBP", quality=q, method=6, **extra)
        size = buf.tell()
        if not max_bytes or size <= max_bytes or q <= 50:
            write_atomic(out, buf.getvalue())
            return {"path": str(out), "bytes": size, "quality": q, "over_limit": bool(max_bytes and size > max_bytes)}
        q -= 5


def uses_generated_images(html: Path, qa: dict | None) -> bool:
    """True when a visual in the design declares it is AI-generated (C2PA, IPTC tag or codex-imagegen sidecar)."""
    srcs = [i["src"] for i in (qa or {}).get("images", []) if i.get("src", "").startswith("file:")]
    if not srcs:
        return False
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("codex_image", IMAGEGEN)
        ci = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ci)
        ai = ci.ai_source
    except Exception:
        def ai(p):
            try:
                head = Path(p).read_bytes()[:8_000_000]
            except OSError:
                return False
            return b"trainedAlgorithmicMedia" in head or b"caBX" in head or b"c2pa" in head
    from urllib.parse import unquote, urlparse
    return any(ai(unquote(urlparse(s).path)) for s in srcs)


def fix_pdf_boxes(data: bytes, c: dict) -> tuple:
    """Crop Chrome's slightly larger pages to the exact canvas (top-left anchored) and set the BleedBox and TrimBox
    printers read. Without pypdf the PDF keeps Chrome's rounded page size."""
    try:
        from pypdf import PdfReader, PdfWriter
        from pypdf.generic import RectangleObject
    except ImportError:
        add_venv_paths()
        try:
            from pypdf import PdfReader, PdfWriter
            from pypdf.generic import RectangleObject
        except ImportError:
            return data, "Chrome page size (rounded to 1/100 in), no TrimBox: run `doctor --setup` for exact boxes"
    import io
    w, h, b = c["w_px"] * 0.75, c["h_px"] * 0.75, c["bleed_px"] * 0.75
    rd, wr = PdfReader(io.BytesIO(data)), PdfWriter()
    for page in rd.pages:
        top = float(page.mediabox.top)
        box = RectangleObject([0, top - h, w, top])
        page.mediabox = box
        page.cropbox = box
        page.bleedbox = box
        page.trimbox = RectangleObject([b, top - h + b, w - b, top - b]) if b else box
        wr.add_page(page)
    wr.add_metadata({"/Creator": "codex-design", "/Producer": "Chrome + pypdf"})
    buf = io.BytesIO()
    wr.write(buf)
    return buf.getvalue(), (f"exact {w / 72 * 25.4:.1f}x{h / 72 * 25.4:.1f} mm" +
                            (f", TrimBox inset {b / 72 * 25.4:.1f} mm bleed" if b else ""))


GENERIC_CMYK = Path("/System/Library/ColorSync/Profiles/Generic CMYK Profile.icc")


def cmyk_pdf(shots: list, c: dict, out: Path, profile: str, scale: float) -> dict:
    """A raster CMYK PDF for printers that refuse RGB: the 300 ppi render converted from sRGB to the press profile
    (relative colorimetric + black point compensation) by LittleCMS, one page per canvas, with exact boxes. Text is
    pixels here and black text becomes four-colour black, so the RGB vector PDF stays the master."""
    Image = need_pillow()
    from PIL import ImageCms
    import io
    path = GENERIC_CMYK if profile in (None, "", "generic") else Path(profile).expanduser()
    if not path.exists():
        die(f"--cmyk: ICC profile not found: {path} (get the printer's profile, e.g. FOGRA51/PSO Coated v3 from "
            f"eci.org or GRACoL2013 from idealliance, or use 'generic')")
    intent = getattr(getattr(ImageCms, "Intent", None), "RELATIVE_COLORIMETRIC", 1)
    bpc = getattr(getattr(ImageCms, "Flags", None), "BLACKPOINTCOMPENSATION", 0x2000)
    xf = ImageCms.buildTransform(ImageCms.createProfile("sRGB"), ImageCms.getOpenProfile(str(path)), "RGB", "CMYK",
                                 renderingIntent=intent, flags=bpc)
    w, h = round(c["w_px"] * scale), round(c["h_px"] * scale)
    frames = []
    for shot in shots:  # one PNG per page, cropped to the exact print size
        im = Image.open(io.BytesIO(shot)).convert("RGB")
        frames.append(ImageCms.applyTransform(im.crop((0, 0, min(w, im.width), min(h, im.height))), xf))
    buf = io.BytesIO()
    frames[0].save(buf, "PDF", save_all=True, append_images=frames[1:], resolution=96 * scale, quality=95)
    data, note = fix_pdf_boxes(buf.getvalue(), c)
    write_atomic(out, data)
    name = ImageCms.getProfileDescription(ImageCms.getOpenProfile(str(path))).strip()
    return {"path": str(out), "bytes": len(data), "pages": len(frames), "pdf_boxes": note,
            "colour": f"CMYK raster {96 * scale:.0f} ppi, {name}",
            "note": "for printers that require CMYK; text is rasterised and black is four-colour, so send the RGB "
                    "vector PDF unless the printer asks for this"}


def pdf_fonts(pdf: Path) -> dict | None:
    """Poppler's pdffonts: every font in a print PDF must be embedded, and as real TrueType. Chrome's PDF backend
    (Skia) falls back to Type 3 glyph procedures for variable, CFF-outlined or restricted fonts, blurred text-shadows
    and faux bold: it still prints, but preflight flags it and text extraction suffers (pdffonts says "emb yes")."""
    exe = shutil.which("pdffonts")
    if not exe:
        return None
    r = subprocess.run([exe, str(pdf)], capture_output=True, text=True, timeout=60)
    fonts = []
    for line in r.stdout.splitlines()[2:]:
        tok = line.split()
        if len(tok) < 8:  # name, type (1-3 words), encoding, emb, sub, uni, object, generation
            continue
        fonts.append({"name": tok[0], "type": " ".join(tok[1:-6]), "embedded": tok[-5] == "yes"})
    return {"count": len(fonts), "types": sorted({f["type"] for f in fonts}),
            "not_embedded": [f["name"] for f in fonts if not f["embedded"]],
            "type3": sorted({re.sub(r"^[A-Z]{6}\+", "", f["name"]) for f in fonts if f["type"] == "Type 3"})}


def page_shots(page: dict, c: dict, pages: int, scale: float) -> list:
    """One PNG per page: the separate .page captures, else slices of the stacked capture."""
    if page.get("png_pages"):
        return page["png_pages"]
    if pages <= 1:
        return [page["png"]]
    Image = need_pillow()
    import io
    full = Image.open(io.BytesIO(page["png"]))
    ph, shots = c["h_px"] * scale, []
    for k in range(pages):
        buf = io.BytesIO()
        full.crop((0, round(k * ph), full.width, min(full.height, round(k * ph + ph)))).save(buf, "PNG")
        shots.append(buf.getvalue())
    return shots


def write_atomic(path: Path, data) -> None:
    """Write through a temporary file in the same folder, then rename it into place: a crash or a reader never
    sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.part")
    tmp.write_bytes(data.encode("utf-8") if isinstance(data, str) else data)
    os.replace(tmp, path)


def file_sha256(path) -> str | None:
    import hashlib
    try:
        with open(path, "rb") as f:
            return hashlib.file_digest(f, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else \
                hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


@contextlib.contextmanager
def output_lock(out: Path):
    """One writer per output name: two runs writing the same files at once leave a mixed set (one design's PNG,
    the other's report)."""
    import fcntl
    import hashlib
    d = CACHE / "locks"
    d.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(str(out.expanduser().resolve().with_suffix("")).encode("utf-8")).hexdigest()[:20]
    with open(d / f"{key}.lock", "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            die(f"another codex-design run is writing {out.name} in {out.parent} right now; wait for it or choose "
                f"another --out")
        yield


def short_url(url: str, html: Path | None = None) -> str:
    """A failed request as a designer reads it: the path relative to the design (or the file name), else the URL."""
    if url.startswith("file:"):
        from urllib.parse import unquote, urlparse
        f = Path(unquote(urlparse(url).path)).resolve()
        if html is None:
            return f.name
        try:
            rel = os.path.relpath(f, html.resolve().parent)
        except ValueError:
            return str(f)
        return rel if rel.count("..") <= 2 else str(f)
    return url if len(url) <= 100 else url[:97] + "..."


def plate_notes(qa: dict | None) -> list:
    """What the image judge said about the photo plates this design uses (codex-imagegen's <name>.meta.json next to
    each file): a rejected candidate, or defects it flagged. Both came back later as design failures (R6)."""
    from urllib.parse import unquote, urlparse
    notes, seen = [], set()
    for im in (qa or {}).get("images") or []:
        src = im.get("src", "")
        if not src.startswith("file:"):
            continue
        f = Path(unquote(urlparse(src).path))
        base = re.sub(r"-(?:c\d+|raw)$", "", f.stem)
        meta = next((m for m in (f.with_name(f.stem + ".meta.json"), f.with_name(base + ".meta.json")) if m.exists()),
                    None)
        if not meta or meta in seen:
            continue
        seen.add(meta)
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        kept = m.get("output_path")
        if str(f) in (m.get("rejected") or []) or (kept and Path(kept).name != f.name and f.stem != base):
            notes.append(f"the plate {f.name} is a candidate the image judge rejected ({meta.name}); use the kept "
                         f"file {Path(kept).name if kept else base + f.suffix}")
        j = m.get("judge") or {}
        bad = [d for d in j.get("defects") or [] if d.get("severity") in ("critical", "major")]
        if bad or j.get("computed_verdict") == "FAIL":
            notes.append(f"the plate {f.name} was judged {j.get('computed_verdict', '?')}: " +
                         "; ".join(f"{d.get('what', '')} ({d.get('where', '')})" for d in bad[:3]))
    return notes


def produce(ch: Chrome, html: Path, c: dict, out: Path, scale: float | None = None, transparent: bool = False,
            slides: int = 1, qa: bool = True, overlay: bool = False, quality: int = 90, max_bytes: int | None = None,
            preview: bool = False, pages: int = 1, copy: list | None = None, simulate: list | None = None,
            occasion: str | None = None, cmyk: str | None = None, locale: str = "", timeout: float = 60,
            wait: bool = True):
    """Render one design to one canvas: the files, provenance tag, checks and a review overlay. `slides` lays N
    canvases side by side (carousel), `pages` stacks N canvases (a document printed page by page), `cmyk` adds a
    raster CMYK PDF next to a print PDF. A PDF's --preview is written as <out>.preview.png. wait=False returns a
    Future of the report as soon as Chrome and the checks are done with the page: its images are encoded and
    written, and its report finished, in the background while the caller renders the next canvas (pack)."""
    fmt = out.suffix.lower().lstrip(".").replace("jpeg", "jpg")
    if fmt not in ("png", "jpg", "webp", "pdf"):
        die("--out must end in .png, .jpg, .webp or .pdf")
    slides, pages = max(1, slides or 1), max(1, pages or 1)
    if slides > 1 and pages > 1:
        die("use --slides (side by side) or --pages (stacked), not both")
    # a preset for a product that prints only the art (a t-shirt, a sticker) renders on a transparent ground; a JPG
    # cannot hold transparency, so it keeps the page's own background
    transparent = transparent or (bool(c.get("transparent")) and fmt in ("png", "webp"))
    raster_pdf = fmt == "pdf" and slides > 1  # a carousel PDF (LinkedIn document) is one page per slide
    if cmyk and not (fmt == "pdf" and c["print"] and not raster_pdf):
        die("--cmyk works with a print preset (or a mm/in size) and a .pdf output")
    scale = scale or (300 / 96 if c["print"] and (fmt != "pdf" or cmyk) else 1)
    want_png = fmt != "pdf" or preview or raster_pdf or bool(cmyk)
    raster_px = c["w_px"] * c["h_px"] * slides * pages * (scale if not raster_pdf else max(scale, 1)) ** 2
    if want_png and raster_px > MAX_RASTER_PX:
        die(f"the raster would be {raster_px / 1e6:.0f} MP (the limit is {MAX_RASTER_PX / 1e6:.0f} MP); write a "
            f".pdf (vector, any size) or lower --scale")
    with contextlib.ExitStack() as stack:
        stack.enter_context(output_lock(out))
        finish = _produce(ch, html, c, out, fmt, scale, transparent, slides, pages, raster_pdf, want_png, qa, overlay,
                          quality, max_bytes, preview, copy, simulate, occasion, cmyk, locale, timeout)
        if wait:
            return finish()
        held = stack.pop_all()  # the lock stays taken until the files are written

    def done():
        with held:
            return finish()
    return finisher().submit(done)


def finisher():
    """The thread that completes renders made with produce(wait=False); it waits on encoder() jobs, so it has its
    own pool."""
    with _SAVE_LOCK:
        if "finish" not in _ENCODER:
            from concurrent.futures import ThreadPoolExecutor
            _ENCODER["finish"] = ThreadPoolExecutor(max_workers=1, thread_name_prefix="codex-design-finish")
    return _ENCODER["finish"]


def _produce(ch, html, c, out, fmt, scale, transparent, slides, pages, raster_pdf, want_png, qa, overlay, quality,
             max_bytes, preview, copy, simulate, occasion, cmyk, locale, timeout):
    """Chrome's work and the checks, in the caller's thread; returns finish(), which waits for the image files and
    writes the report (it no longer touches Chrome, so it may run in another thread)."""
    t0 = time.time()
    page = render_page(ch, html, c, scale if not raster_pdf else max(scale, 1), transparent,
                       want_png=want_png, want_pdf=fmt == "pdf" and not raster_pdf,
                       qa=qa, slides=slides, pages=pages, simulate=simulate, timeout=timeout)
    rep = {"html": str(html), "canvas": {"id": c.get("id"), "w": round(c["w_px"]), "h": round(c["h_px"]),
                                         "slides": slides, "pages": pages, "scale": round(scale, 4),
                                         "bleed_px": round(c["bleed_px"], 2)}, "outputs": []}
    if c.get("assumed"):
        rep["canvas"]["assumed"] = c["assumed"]
    info = page["qa"]
    tag = uses_generated_images(html, info)
    out.parent.mkdir(parents=True, exist_ok=True)
    max_bytes = max_bytes or c.get("max_bytes")
    extra_err, extra_warn = [], []
    blocks = int(page.get("page_blocks") or 0)
    if pages == 1 and blocks > 1:
        extra_err.append(f"the document has {blocks} .page blocks but was rendered as one canvas: render it with "
                         f"--pages {blocks} (the clipping errors below come from that)")
    failed = page.get("failed_loads") or []
    for url, why in failed:
        extra_err.append(f"failed to load {short_url(url, html)}: {why}")
    extra_warn += plate_notes(info)
    if c.get("assumed"):
        extra_warn.append("custom size, so the checks assumed " + "; ".join(c["assumed"]) + ". Give the platform's "
                          "numbers with --safe, --keepout and --view-width, or a preset (references/formats.md)")
    if page["pdf"] is not None:
        data, note = fix_pdf_boxes(page["pdf"], c)
        write_atomic(out, data)
        try:
            n_pages = len(re.findall(rb"/Type\s*/Page(?!s)", data))
        except Exception:
            n_pages = None
        fonts = pdf_fonts(out)
        rep["outputs"].append({"path": str(out), "bytes": len(data), "pdf_boxes": note, "pages": n_pages,
                               "fonts": fonts})
        if pages > 1 and n_pages and n_pages != pages:
            extra_warn.append(f"the PDF has {n_pages} pages, expected {pages}: give every .page a fixed size and "
                              f"break-after: page")
        if fonts and fonts["not_embedded"]:
            extra_warn.append(f"fonts not embedded in the PDF: {', '.join(fonts['not_embedded'])}")
        if fonts and fonts["type3"] and c["print"]:
            extra_warn.append(f"Type 3 fonts in a print PDF ({', '.join(fonts['type3'][:4])}): Chrome converts "
                              f"variable, CFF/OTF-outlined or restricted fonts (and blurred text-shadows, faux bold) to "
                              f"Type 3, which preflight flags; use static TrueType web fonts (`design.py fonts`) and no "
                              f"blurred shadows on print text")
        if cmyk:
            rep["outputs"].append(cmyk_pdf(page_shots(page, c, pages, scale), c, out.with_name(out.stem + ".cmyk.pdf"),
                                           cmyk, scale))
    jobs = []  # (place in rep["outputs"], future): images encode in worker threads while the checks below run

    def save_later(*a, **k):
        need_pillow()
        srgb_icc()  # one profile for every file of the run, made before the threads start
        rep["outputs"].append(None)
        jobs.append((len(rep["outputs"]) - 1, encoder().submit(save_image, *a, **k)))
    if page["png"] is not None and (fmt != "pdf" or preview or raster_pdf):  # a raster made only for --cmyk stays in memory
        img_fmt = fmt if fmt != "pdf" else "png"
        if pages > 1:
            exact = (round(c["w_px"] * scale), round(c["h_px"] * scale))
            for k, shot in enumerate(page_shots(page, c, pages, scale)):
                p = out.with_name(f"{out.stem}-p{k + 1:02d}.{img_fmt}")
                save_later(shot, p, img_fmt, quality, max_bytes, tag, dpi=round(96 * scale, 2) if c["print"] else None,
                           size=exact if c["print"] else None)
            stale = [q.name for k in range(pages + 1, 100)
                     for q in [out.with_name(f"{out.stem}-p{k:02d}.{img_fmt}")] if q.exists()]
            if stale:
                extra_warn.append(f"files from an earlier render with more pages are still here (not deleted): "
                                  f"{', '.join(stale[:6])}")
        elif slides > 1:
            Image = need_pillow()
            import io
            full = Image.open(io.BytesIO(page["png"]))
            sw = full.width // slides
            frames = []
            for k in range(slides):
                part = full.crop((k * sw, 0, (k + 1) * sw, full.height))
                if raster_pdf:
                    frames.append(part.convert("RGB"))
                    continue
                save_later(part, out.with_name(f"{out.stem}-{k + 1:02d}.{img_fmt}"), img_fmt, quality, max_bytes, tag)
            if raster_pdf:
                buf = io.BytesIO()
                frames[0].save(buf, "PDF", save_all=True, append_images=frames[1:], resolution=72 * scale)
                write_atomic(out, buf.getvalue())
                rep["outputs"].append({"path": str(out), "bytes": out.stat().st_size, "pages": slides})
            else:
                stale = [q.name for k in range(slides + 1, 100)
                         for q in [out.with_name(f"{out.stem}-{k:02d}.{img_fmt}")] if q.exists()]
                if stale:
                    extra_warn.append(f"files from an earlier render with more slides are still here (not deleted): "
                                      f"{', '.join(stale[:6])}")
            strip = out.with_name(f"{out.stem}-strip.jpg")
            prev = full.convert("RGB")
            prev.thumbnail((2400, 2400))
            buf = io.BytesIO()
            prev.save(buf, "JPEG", quality=85)
            write_atomic(strip, buf.getvalue())
            rep["preview_strip"] = str(strip)
        else:
            target = out if fmt != "pdf" else out.with_name(out.stem + ".preview.png")
            exact = (round(c["w_px"] * scale), round(c["h_px"] * scale)) if c["print"] else None
            save_later(page["png"], target, img_fmt, quality, max_bytes, tag,
                       dpi=round(96 * scale, 2) if c["print"] else None, size=exact)
    if tag:
        rep["provenance"] = (f"{COMPOSITE_TERM} (contains generated visuals). Platforms strip metadata: when the AI "
                             f"imagery is photorealistic and the audience includes the EU, add a visible label.")
    for kind, png in (page.get("sims") or {}).items():
        p = out.with_name(f"{out.stem}.sim-{kind}.png")
        write_atomic(p, png)
        rep.setdefault("simulations", []).append(str(p))
    verdict = review(info, page["bg"], c, copy, slides, occasion, locale) if info else None
    if info:
        said = {f"image did not load: {short_url(u)}" for u, _ in failed}  # the load error already names the cause
        verdict["errors"] = extra_err + [e for e in verdict["errors"] if e not in said]
        verdict["warnings"] += extra_warn
        verdict["ok"] = not verdict["errors"]
        rep["checks"] = verdict
        rep["text"] = [{k: it[k] for k in ("text", "font", "size", "weight", "box", "severity") if k in it} |
                       ({"contrast": it["contrast"]["p10"]} if it.get("contrast") else {}) for it in info["items"]]
        rep["images"] = info["images"]
        rep["fonts"] = info["families"]
        rep["text_coverage"] = info["text_coverage"]
    elif extra_err or extra_warn:
        rep["errors"], rep["warnings"] = extra_err, extra_warn
    chrome = ch.version()  # rendering changes between Chrome releases: keep the version with the files

    def finish():
        for i, job in jobs:  # the files are written before anything reports on them
            rep["outputs"][i] = job.result()
        if info:
            files = [o["path"] for o in rep["outputs"]] + ([rep["preview_strip"]] if rep.get("preview_strip") else [])
            spec = {k: c.get(k) for k in ("label", "source", "confidence", "verified", "origin", "view_width_px",
                                          "thumb_width_px", "file_scale") if c.get(k)}
            source = {"html": str(html.resolve()), "html_sha256": file_sha256(html), "preset": c.get("id"),
                      "canvas": rep["canvas"], "locale": locale or None, "generated_visuals": bool(tag),
                      "spec": spec or None, "assumed": c.get("assumed") or None,
                      "distance_floor": c.get("distance_floor"),
                      "outputs": [{"path": f, "sha256": file_sha256(f)} for f in files],
                      "rendered_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "skill_version": SKILL_VERSION,
                      "chrome": chrome}
            qa_path = out.with_name(out.stem + ".qa.json")
            write_atomic(qa_path, json.dumps(dict(info, checks=verdict, source=source), indent=2, ensure_ascii=False))
            rep["qa_json"] = str(qa_path)
            if overlay and page["png"] is not None:
                ov = out.with_name(out.stem + ".overlay.png")
                part = ov.with_name(f".{ov.name}.{os.getpid()}.part.png")
                draw_overlay(page["png"], info, c, part, scale)
                os.replace(part, ov)
                rep["overlay"] = str(ov)
        rep["chrome"] = chrome
        rep["ms"] = int((time.time() - t0) * 1000)
        return rep
    return finish


def norm_locale(loc: str | None) -> str:
    """A market as a two-letter country code (BD, IN, US): copy rules change with it (Bangladesh vs West Bengal)."""
    loc = (loc or "").strip()
    if loc and not re.fullmatch(r"[A-Za-z]{2}", loc):
        die(f"--locale takes a two-letter country code such as BD, IN, US or GB, not {loc!r}")
    return loc.upper()


def design_html(arg: str) -> Path:
    html = Path(arg).expanduser()
    if not html.exists():
        die(f"not found: {html}")
    if html.is_dir():
        die(f"{html} is a folder; give the design's .html file")
    return html


def cmd_render(args) -> None:
    html = design_html(args.html)
    if args.preset and args.size:
        die("give --preset or --size, not both")
    c = apply_spec(resolve_canvas(args.preset, args.size, args.bleed), args)
    if args.size and not c["print"]:  # a preset of that size also sets the safe zone the layout may rely on
        same = [k for k, v in presets().items() if (v.get("w"), v.get("h")) == (round(c["w_px"]), round(c["h_px"]))]
        if same:
            log(f"--size {args.size}: presets of this size carry a platform's safe zone: {', '.join(same[:5])}")
    if args.out:
        out = Path(args.out).expanduser()
    elif SKILL_DIR in html.resolve().parents:  # a template rendered as is: never write into the skill folder
        out = Path.cwd() / (html.stem + ".png")
        log(f"no --out: writing {out}")
    else:
        out = html.with_suffix(".png")
    copy = load_copy(args.copy) if args.copy else None
    locale = norm_locale(args.locale or (copy_meta(args.copy).get("locale") if args.copy else ""))
    sims = [s.strip() for s in args.simulate.split(",")] if args.simulate else None
    with Chrome(allow_net=args.allow_net) as ch:
        rep = produce(ch, html, c, out, args.scale, args.transparent, args.slides or 1, not args.no_qa, args.overlay,
                      args.quality, args.max_bytes, args.preview, args.pages or 1, copy, sims, args.occasion,
                      args.cmyk, locale, args.timeout)
    if copy:
        rep["copy_lint"] = render_copy_lint(copy, locale, copy_meta(args.copy).get("platform") or "")
    print(json.dumps(rep if getattr(args, "json", False) else render_summary(rep), indent=2, ensure_ascii=False))
    if args.strict and ((rep.get("checks") and not rep["checks"]["ok"]) or rep.get("errors")
                        or (rep.get("copy_lint") or {}).get("errors")):
        sys.exit(2)


def render_copy_lint(copy: list, locale: str, platform: str) -> dict:
    """copylint on the copy.json the render checked, so one command gives the picture's checks and the copy's: one
    step less for every draft. Notes stay in `copylint`; errors and warnings come here."""
    platform = platform.lower() if platform and platform.split("-")[0].lower() in copyrules.PLATFORM else ""
    strings = [{"role": s.get("role", ""), "text": s.get("text", ""), "lang": s.get("lang", "")} for s in copy]
    lint = copyrules.lint_deck(strings, locale, platform)
    found = [f"{f['severity']}: {it['role'] or '-'}: {f['message']} -> {f['suggest']}"
             for it in lint["items"] for f in it["findings"] if f["severity"] != "note"] + \
            [f"{f['severity']}: (deck) {f['message']} -> {f['suggest']}" for f in lint["deck"] if f["severity"] != "note"]
    return {"errors": lint["errors"], "warnings": lint["warnings"], "found": found[:15]}


def render_summary(rep: dict) -> dict:
    """A render report without its per-item detail (every text item and image: 27 KB for a 10-page brand book). The
    detail stays in <out>.qa.json, and render --json prints it."""
    return {k: v for k, v in rep.items() if k not in ("text", "images")}


def cmd_pack(args) -> None:
    """One responsive HTML rendered on several canvases (feed, square, story, cover...) in one Chrome session."""
    html = design_html(args.html)
    ids = [p.strip() for p in args.presets.split(",") if p.strip()]
    for p in ids:
        resolve_canvas(p, None)  # an unknown or retired preset stops here, with the nearest names or its replacement
    out_dir = Path(args.out_dir).expanduser()
    copy = load_copy(args.copy) if args.copy else None
    locale = norm_locale(args.locale or (copy_meta(args.copy).get("locale") if args.copy else ""))
    sims = [x.strip() for x in args.simulate.split(",")] if args.simulate else None
    pending = []  # each canvas's files are encoded while Chrome renders the next one
    with Chrome(allow_net=args.allow_net) as ch:
        for p in ids:
            c = resolve_canvas(p, None, None)
            pending.append(produce(ch, html, c, out_dir / f"{args.name or html.stem}-{p}.{args.format}", args.scale,
                                   qa=not args.no_qa, overlay=args.overlay, quality=args.quality, copy=copy,
                                   occasion=args.occasion, simulate=sims, locale=locale, timeout=args.timeout,
                                   wait=False))
    reps = [f.result() for f in pending]
    files = [o["path"] for r in reps for o in r["outputs"] if not o["path"].endswith(".pdf")]
    sheet = out_dir / f"{args.name or html.stem}-pack-sheet.jpg"
    if files:
        make_sheet(files, sheet, cell=420)
    designs = [{"preset": r["canvas"]["id"], "outputs": [o["path"] for o in r["outputs"]],
                "ok": r.get("checks", {}).get("ok", not r.get("errors")),
                "errors": r.get("checks", {}).get("errors", r.get("errors")),
                "warnings": r.get("checks", {}).get("warnings", r.get("warnings"))} for r in reps]
    print(json.dumps({"designs": designs, "sheet": str(sheet) if files else None}, indent=2, ensure_ascii=False))
    if args.strict and not all(d["ok"] for d in designs):
        sys.exit(2)


def make_sheet(files: list, out: Path, cell: int = 480, cols: int | None = None, label: bool = True) -> Path:
    """Contact sheet: every image fitted into a cell with its file name, for side-by-side review."""
    Image = need_pillow()
    from PIL import ImageDraw
    import math
    ims = []
    for f in files:
        with Image.open(f) as im:
            t = im.convert("RGB")
            t.thumbnail((cell, cell))
            ims.append((Path(f).name, t))
    cols = cols or min(len(ims), max(1, math.ceil(math.sqrt(len(ims)))))
    rows = math.ceil(len(ims) / cols)
    pad, lab = 16, (22 if label else 0)
    sheet = Image.new("RGB", (cols * (cell + pad) + pad, rows * (cell + pad + lab) + pad), (236, 236, 232))
    d = ImageDraw.Draw(sheet)
    for i, (name, t) in enumerate(ims):
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + pad + lab)
        sheet.paste(t, (x + (cell - t.width) // 2, y + (cell - t.height) // 2))
        if label:
            d.text((x, y + cell + 4), name[:60], fill=(40, 40, 40))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out, "JPEG", quality=88)
    return out


DERIVED_RX = re.compile(r"\.(?:overlay|preview|sim-[\w-]+)\.png$|-(?:strip|sheet|pack-sheet)\.jpg$|\.part(?:\.png)?$",
                        re.I)


def cmd_sheet(args) -> None:
    files = []
    for s in args.src:
        p = Path(s).expanduser()
        if not p.exists():
            die(f"not found: {p}")
        # a folder: its designs, not the renderer's side files (overlays, strips, simulations, earlier sheets)
        files += sorted(q for q in p.iterdir() if q.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and
                        not DERIVED_RX.search(q.name) and not q.name.startswith(".")) if p.is_dir() else [p]
    if not files:
        die("no images to put on the sheet")
    out = make_sheet([str(f) for f in files], Path(args.out).expanduser(), args.cell, args.cols)
    print(json.dumps({"sheet": str(out), "images": len(files)}, indent=2))


def cmd_qr(args) -> None:
    """A QR code as SVG (scales for print) or PNG; quiet zone of 4 modules; logo overlays need error level H."""
    try:
        import segno
    except ImportError:
        add_venv_paths()
        try:
            import segno
        except ImportError:
            die("QR codes need segno; run `design.py doctor --setup` once")
    q = segno.make(args.data, error=args.error, micro=False)
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    kw = {"border": args.border, "dark": args.dark, "light": None if args.light == "none" else args.light}
    modules = q.symbol_size(border=args.border)[0]
    if out.suffix.lower() == ".svg":
        q.save(str(out), kind="svg", scale=1, xmldecl=False, svgclass=None, lineclass=None, **kw)
        svg = out.read_text(encoding="utf-8")
        if "viewBox" not in svg:  # without it the code does not scale when shown larger than 1 px per module
            out.write_text(svg.replace("<svg ", f'<svg viewBox="0 0 {modules} {modules}" '
                                       f'shape-rendering="crispEdges" ', 1), encoding="utf-8")
    else:
        q.save(str(out), scale=args.scale, **kw)
    print(json.dumps({"qr": str(out), "version": q.version, "error": q.error, "modules_with_quiet_zone": modules,
                      "min_print_mm": round(max(20, modules * 0.4), 1),
                      "note": "print at least ~2 cm wide (0.4 mm per module) and test-scan it before printing"},
                     indent=2))


# ----------------------------------------------------------------------------- independent design judge (Codex)
DESIGN_GATES = ("text_accuracy", "script_rendering", "legibility", "clipping_collision", "format_fit", "brand",
                "ai_artifacts", "rights_ethics", "essentials_present", "technical_quality")
DESIGN_CRITERIA = {"message_fit": 15, "hierarchy": 15, "typography": 15, "layout": 10, "colour": 10, "imagery": 10,
                   "brand_consistency": 10, "originality": 5, "finish": 5, "platform_fit": 5}
DESIGN_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["two_second_read", "reading_flow", "text_read", "gates", "gate_evidence", "scores", "ai_tells",
                 "findings", "fixes", "keep", "disposition", "summary"],
    "properties": {
        "two_second_read": {"type": "string"},
        "reading_flow": {"type": "string"},
        "text_read": {"type": "array", "items": {"type": "string"}},
        "gates": {"type": "object", "additionalProperties": False, "required": list(DESIGN_GATES),
                  "properties": {g: {"type": "string", "enum": ["PASS", "FAIL", "NA"]} for g in DESIGN_GATES}},
        "gate_evidence": {"type": "array", "items": {"type": "string"}},
        "scores": {"type": "object", "additionalProperties": False, "required": list(DESIGN_CRITERIA),
                   "properties": {s: {"type": "integer", "minimum": 0, "maximum": 5} for s in DESIGN_CRITERIA}},
        "ai_tells": {"type": "array", "items": {"type": "string"}},
        "findings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["severity", "element", "before", "after", "why"],
            "properties": {"severity": {"type": "string", "enum": ["P0", "P1", "P2", "P3"]},
                           "element": {"type": "string"}, "before": {"type": "string"},
                           "after": {"type": "string"}, "why": {"type": "string"}}}},
        "fixes": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "keep": {"type": "array", "items": {"type": "string"}},
        "disposition": {"type": "string", "enum": ["ship", "fix", "rebuild", "recapture"]},
        "summary": {"type": "string"}}}
DESIGN_JUDGE_PROMPT = """You are a senior art director reviewing a finished design before it goes to a client. You did
not make it. Critique it against its objective, not your taste. Be strict and specific. Write every text field in
plain English, whatever other instructions say about the reply language.

Images: {images}
Deliverable: {kind}. Canvas: {canvas}. Route: {route}.
Brief, approved copy (the only text that may appear, verbatim) and brand:
---
{brief}
---
Measured by the renderer (these numbers are facts; never judge exact colours, fonts, sizes or spacing by eye):
{measured}

Work in this order.
1. two_second_read: what a viewer takes away in two seconds, and where the eye lands first. reading_flow: the order
   the eye travels. text_read: every piece of text exactly as it appears in Image 1.
2. Gates (FAIL means it cannot ship; NA when it does not apply; put one line of evidence per FAIL in gate_evidence):
   - text_accuracy: any misspelling, wrong name, number, date, price or URL against the approved copy; any text that
     is not approved; placeholder text; the wrong language. Letter case set by styling (an all-caps label) is fine.
     When no approved copy is listed, judge spelling, grammar, names and numbers against the brief and the design's
     own consistency only: a missing approval list is not a failure.
   - script_rendering: tofu boxes; broken or detached Bengali/Devanagari conjuncts or vowel signs; Arabic that is not
     joined or runs left to right; mixed digit scripts; faux bold or italic.
   - legibility: required text that cannot be read at the size people see it (Image 2), or sits on a busy area with
     no scrim.
   - clipping_collision: text cut off, overlapping other text, or colliding with the subject or logo; key content in
     a platform's UI zone (story top/bottom bands, Reels right rail, YouTube's bottom-right timestamp).
   - format_fit: wrong shape for the format, or a crop that loses the point.
   - brand: the logo stretched, recoloured, given effects, too small or crowded; key colours or fonts off-brand.
   - ai_artifacts: in any imagery: hands, teeth, eyes, melted or merged objects, impossible physics, fake text or
     gibberish marks, watermarks.
   - rights_ethics: third-party logos or trademarks, identifiable real people who were not supplied, invented claims,
     prices, reviews, awards or badges, fake interfaces, culturally offensive or careless use of symbols, flags,
     religious or national imagery, a celebratory tone on a day of mourning.
   - essentials_present: anything the brief requires (CTA, logo, date, time, venue, handle, disclaimer) is missing.
   - technical_quality: visible pixelation, blur on the key subject, banding, JPEG blocks, halos on cut-outs.
3. Scores 0-5 (0 broken, 1 amateur, 2 below professional, 3 competent professional, 4 strong senior work,
   5 exceptional): message_fit (one clear message, right tone, a CTA where needed), hierarchy (unmistakable entry
   point, 2-3 levels, survives the squint image), typography (purposeful faces, leading and tracking right for size
   and script, balanced breaks, real punctuation), layout (one grid, consistent margins and spacing, intentional
   balance, white space used), colour (disciplined palette, comfortable contrast, no default gradients), imagery
   (credible, specific, well integrated with the type; 3 if there is none), brand_consistency (recognisable even
   without the logo), originality (a specific idea; a competitor's logo would not fit it; no template or AI tells),
   finish (radii, strokes, alignment, kerning, no near-misses), platform_fit (reads at display size, crop-safe).
4. ai_tells: every tell of generic AI or template graphics you can see (glossy default gradients, purple-to-blue,
   sparkles, blobs and orbs, plastic 3D icons, stock-smooth people, everything centred, effects stacked, emoji
   clutter, fake badges or logos, decoration with no job, reflex fonts used without a reason).
5. findings: each concrete problem as severity (P0 blocks shipping, P1 major, P2 minor, P3 polish), element (what
   and where), before, after (the exact change, in numbers where possible: "subhead 64 -> 48 px", "scrim 45% over
   the bottom 40%"), why. fixes: at most 5, in fix order concept -> hierarchy -> layout -> type -> colour -> polish.
   keep: what works and must not be broken by the fixes.
6. disposition: ship (ready), fix (small changes), rebuild (the layout or type system needs redoing), recapture (the
   imagery or concept must be replaced).
"""


def _judge_verdict(data: dict) -> tuple:
    sc = data["scores"]
    weighted = sum(sc[k] * w for k, w in DESIGN_CRITERIA.items()) / sum(DESIGN_CRITERIA.values())
    core = [sc["message_fit"], sc["hierarchy"], sc["typography"]]
    if any(v == "FAIL" for v in data["gates"].values()) or min(sc.values()) <= 1 or \
            any(f["severity"] == "P0" for f in data["findings"]):
        return "FAIL", weighted
    if weighted < 3.5 or min(sc.values()) == 2 or min(core) < 3:
        return "REVISE", weighted
    if weighted >= 4.2 and min(core) >= 4:
        return "PASS_SENIOR", weighted
    return "PASS", weighted


def text_diff(copy: list, read: list, allow: list | None = None) -> dict:
    """Approved strings against what a reader saw: missing, extra and case-only differences (Latin only; readers
    are unreliable on Indic and Arabic scripts, which need a native reader). `allow` is text that may appear besides
    the copy, such as the brand name in the logo's wordmark."""
    latin = [s for s in copy if not re.search(r"[֐-ࣿऀ-෿]", s["text"])]
    got = norm_text(" ".join(read)).casefold()  # a reader lists a multi-line headline line by line
    missing = [s["text"] for s in latin if norm_text(s["text"]).casefold() not in got]
    approved = " | ".join(norm_text(s["text"]).casefold() for s in copy)
    ok_extra = {norm_text(a).translate(MARKS).casefold() for a in allow or [] if a.strip()}
    extra = [t for t in read if norm_text(t).casefold() and norm_text(t).casefold() not in approved and
             norm_text(t).translate(MARKS).casefold().strip(" .,") not in ok_extra]
    return {"missing": missing, "extra": extra, "checked": len(latin), "skipped_non_latin": len(copy) - len(latin)}


def judge_views(img: Path, kind: str, is_print: bool, tmp: Path, slides: int = 1, view_w: float | None = None,
                thumb_w: float | None = None) -> tuple:
    """Image 1 full size; Image 2 at the size people see it (the preset's viewing width when the render recorded one;
    a carousel strip: every slide at that size, side by side, since the strip scaled to one phone width makes each
    slide unreadably small); then the smallest listing size when the format has one (an e-book in search results);
    last, grey and blurred (squint test)."""
    Image = need_pillow()
    from PIL import ImageFilter
    views, lines = [img], ["Image 1 is the design at full size."]
    with Image.open(img) as im:
        rgb = im.convert("RGB")
    w, h = rgb.size
    small_w = None if is_print else round(view_w or (168 if re.search(r"thumb", kind, re.I) else 390))
    if small_w and slides > 1:
        sw = w / slides
        gap = 16
        cells = [rgb.crop((round(i * sw), 0, round((i + 1) * sw), h)).resize((small_w, round(h * small_w / sw)),
                                                                               Image.LANCZOS) for i in range(slides)]
        sheet = Image.new("RGB", (slides * small_w + (slides - 1) * gap, cells[0].height), (255, 255, 255))
        for i, cell in enumerate(cells):
            sheet.paste(cell, (i * (small_w + gap), 0))
        p = tmp / "viewing-size.png"
        sheet.save(p)
        views.append(p)
        lines.append(f"Image 2 shows the {slides} slides in order, each at about the size people see one slide "
                     f"({small_w} px wide), with white gaps where the cuts are; judge legibility and hierarchy slide "
                     f"by slide on it, and the continuity across the cuts on Image 1.")
    elif small_w and w > small_w * 1.4:
        sm = rgb.resize((small_w, round(h * small_w / w)), Image.LANCZOS)
        p = tmp / "viewing-size.png"
        sm.save(p)
        views.append(p)
        lines.append(f"Image 2 is the same design at about the size people see it ({small_w} px wide); judge "
                     f"legibility and hierarchy on it.")
    if thumb_w and not is_print and slides == 1 and w > thumb_w * 1.4 and thumb_w < (small_w or w) / 1.2:
        tw = round(thumb_w)
        p = tmp / "listing-size.png"
        rgb.resize((tw, round(h * tw / w)), Image.LANCZOS).save(p)
        views.append(p)
        lines.append(f"Image {len(views)} is the design at the smallest size it is listed at ({tw} px wide, as in "
                     f"search results): the title or main message and the main shape must still read there; small "
                     f"print need not.")
    sq = rgb.convert("L").filter(ImageFilter.GaussianBlur(max(2, w / 160)))
    sq.thumbnail((720, 720))
    p = tmp / "squint.png"
    sq.save(p)
    views.append(p)
    lines.append(f"Image {len(views)} is the design in grey and blurred (the squint test): the hierarchy must "
                 f"survive it.")
    return views, " ".join(lines)


def _model_json(raw: str, required: tuple, who: str) -> dict:
    """A model's structured answer, or RunFailed saying what is wrong with it: a killed or drifting session can leave
    half a file or miss a field the verdict needs."""
    try:
        data = json.loads(raw)
    except ValueError as e:
        raise RunFailed(f"{who} returned invalid JSON ({e}); the last output was: {one_line(raw[-300:])}")
    if not isinstance(data, dict):
        raise RunFailed(f"{who} returned {type(data).__name__}, not an object")
    missing = [k for k in required if k not in data]
    if missing:
        raise RunFailed(f"{who} answer lacks {', '.join(missing)}; rerun it (the schema was not honoured)")
    return data


def _load_model_json(path: Path, required: tuple, who: str) -> dict:
    """A model's structured answer from a file, or a clear stop."""
    try:
        return _model_json(path.read_text(encoding="utf-8", errors="replace"), required, who)
    except RunFailed as e:
        die(str(e))


def brand_brief(brand_json) -> str:
    """brand.json as the judge checks a design against it: the supplied logo files (a variant that is not supplied
    fails the brand gate), logo rules, colours, fonts and the motif with its colour."""
    try:
        b = json.loads(Path(brand_json).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read {brand_json}: {e}")
    rows = []
    name = re.sub(r"\s*\(.*\)\s*$", "", str(b.get("name") or "")).strip()
    if name:
        rows.append(f"Brand: {name}")
    if b.get("logo"):
        rows.append("Logo files supplied (only these exist; any other variant, a recoloured or redrawn logo is a "
                    "brand failure): " + ", ".join(f"{k} ({v})" for k, v in b["logo"].items()))
    for k in ("logo_use", "clear_space", "min_size", "proportions", "colors", "fonts", "motif", "numerals",
              "photography", "voice"):
        v = b.get(k)
        if v:
            rows.append(f"{k.replace('_', ' ').capitalize()}: " +
                        (v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)))
    return "\n".join(rows)


def _codex_json(ci, prompt: str, images: list, schema: dict, effort: str, timeout: int, who: str,
                required: tuple, retries: int = 1) -> dict:
    """One fresh read-only Codex session that answers in a JSON schema. A timeout, an empty answer or one that breaks
    the schema is retried once (1 run in 6 of the copy judge hung until its timeout, R5). Raises RunFailed with the
    reason when no attempt gave a usable answer; a stop signal ends it without a retry."""
    tmp = Path(tmp_dir("codex-"))
    sp = tmp / "schema.json"
    sp.write_text(json.dumps(schema), encoding="utf-8")
    err, problem = "", None
    for attempt in range(retries + 1):
        last = tmp / f"answer-{attempt}.json"
        cmd = [ci.codex_bin(), "exec"] + sum((["-i", str(x)] for x in images), []) + [
            "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "--json",
            "-c", f'model_reasoning_effort="{effort}"', "--output-schema", str(sp), "-o", str(last)] + \
            ci.LEAN_FLAGS + ["-"]
        res = run_session(cmd, prompt, timeout, env=ci.codex_env())
        if res["error"] == "stopped":
            raise RunFailed(f"{who}: stopped")
        problem = None
        if last.exists() and last.stat().st_size:
            try:
                return _model_json(last.read_text(encoding="utf-8", errors="replace"), required, who)
            except RunFailed as e:
                problem = str(e)
        err = problem or codex_error(res)
        if attempt < retries:
            log(f"{who}: {err[-160:]}; asking once more")
    raise RunFailed(err if problem else f"{who} returned nothing: {err}")


def judge_key(prompt: str, *parts) -> str:
    """What a judge verdict depends on: the prompt (brief, measurements, views, copy) and the file and settings."""
    import hashlib
    return hashlib.sha256(json.dumps([prompt, *parts], ensure_ascii=False).encode("utf-8")).hexdigest()


def cached_verdict(out: Path, key: str, fresh: bool, show=None) -> bool:
    """Print the earlier verdict and return True when `out` holds one for exactly this input: the same file, brief
    and settings cost a Codex session (1 to 3 minutes and plan quota) for nothing. --fresh asks again. `show` turns
    the report into what is printed (a short summary); without it the whole report is printed."""
    if fresh or not out.exists():
        return False
    try:
        data = json.loads(out.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if data.get("cache_key") != key:
        return False
    log(f"same input as the verdict of {data.get('judged_at', 'an earlier run')}: reusing it (--fresh asks again)")
    data = dict(data, cached=True)
    print(json.dumps(show(data) if show else data, indent=2, ensure_ascii=False))
    return True


def _runs(n: int, fn, who: str = "judge") -> tuple:
    """n independent judge sessions (up to 3 at a time) -> (answers in run order, failed runs). A failed run no longer
    throws the others away: one run must answer, and several need a majority of at least 2 (2 of 3, 3 of 5). Fewer
    stops with the reason each run gave."""
    import concurrent.futures as cf
    n = max(1, n)
    if n == 1:
        try:
            return [fn(0)], []
        except RunFailed as e:
            die(str(e))
    need = max(2, n // 2 + 1)
    good, failed = {}, []
    with cf.ThreadPoolExecutor(max_workers=min(n, 3)) as ex:
        futs = {ex.submit(fn, i): i for i in range(n)}
        for f in cf.as_completed(futs):
            try:
                good[futs[f]] = f.result()
            except RunFailed as e:
                failed.append({"run": futs[f] + 1, "error": str(e)})
    failed.sort(key=lambda x: x["run"])
    if len(good) < need:
        die(f"only {len(good)} of {n} {who} runs answered ({need} needed): " +
            "; ".join(dict.fromkeys(x["error"] for x in failed)))
    if failed:
        log(f"{who}: {len(failed)} of {n} runs failed ({failed[0]['error'][:120]}); the verdict uses the other "
            f"{len(good)}")
    return [good[i] for i in sorted(good)], failed


def _median(vals: list):
    v = sorted(vals)
    return v[(len(v) - 1) // 2]  # the lower median: an even count leans strict


def aggregate_design(runs: list) -> dict:
    """Several judge runs as one verdict: each criterion's median, a gate fails only when most runs fail it (one run
    failed a mark it had accepted before, R6), a P0 finding counts only when most runs raise one."""
    if len(runs) == 1:
        return runs[0]
    n, agg = len(runs), dict(runs[0])
    agg["scores"] = {k: _median([r["scores"][k] for r in runs]) for k in runs[0]["scores"]}
    gates, evidence = {}, []
    for g in runs[0]["gates"]:
        vals = [r["gates"].get(g, "NA") for r in runs]
        fails = vals.count("FAIL")
        gates[g] = "FAIL" if fails * 2 > n else max(("PASS", "NA"), key=vals.count)
        if fails:
            evidence.append(f"{g}: FAIL in {fails} of {n} runs")
    agg["gates"] = gates
    agg["gate_evidence"] = list(dict.fromkeys(evidence + [e for r in runs for e in r.get("gate_evidence", [])]))
    p0_runs = sum(any(f["severity"] == "P0" for f in r["findings"]) for r in runs)
    finds = []
    for r in runs:
        for f in r["findings"]:
            if f["severity"] == "P0" and p0_runs * 2 <= n:
                f = dict(f, severity="P1", why=f"{f['why']} (P0 in {p0_runs} of {n} runs)")
            finds.append(f)
    agg["findings"] = finds
    for k in ("ai_tells", "fixes", "keep"):
        agg[k] = list(dict.fromkeys(x for r in runs for x in r.get(k, [])))
    agg["fixes"] = agg["fixes"][:8]
    return agg


BRIEF_MAX = 9000  # characters of the brief the design judge reads; the approved copy and brand facts come in full


def judge_summary(data: dict, out: Path) -> dict:
    """What a caller needs to act on a design verdict. The whole report stays in the file (and --json prints it)."""
    s = {k: data[k] for k in ("verdict", "weighted", "scores", "disposition", "cached") if k in data}
    failed = [g for g, v in (data.get("gates") or {}).items() if v == "FAIL"]
    if failed:
        s["gates_failed"] = failed
        s["gate_evidence"] = (data.get("gate_evidence") or [])[:6]
    s["fixes"] = data.get("fixes") or []
    top = [f for f in data.get("findings") or [] if f.get("severity") in ("P0", "P1")]
    if top:
        s["findings"] = [f"{f['severity']} {f.get('element', '')}: {f.get('after', '')}" for f in top[:6]]
    diff = data.get("text_diff") or {}
    if diff.get("missing") or diff.get("extra"):
        s["text_diff"] = {"missing": diff.get("missing"), "extra": diff.get("extra")}
    for k in ("notes", "runs", "runs_failed", "seconds"):
        if data.get(k):
            s[k] = data[k]
    s["report"] = str(out)
    return s


def cmd_judge(args) -> None:
    """Independent review of a rendered design by fresh Codex sessions (vision); the verdict is computed here. The
    render's own errors come first: a design with errors in its .qa.json is not judged (the judge fails those)."""
    ci = _imagegen()
    if ci is None:
        die(f"the design judge uses codex-imagegen's Codex setup ({IMAGEGEN})")
    img = Path(args.image).expanduser()
    if not img.exists():
        die(f"not found: {img}")
    brief = (text_or_file(args.brief, "brief") or "(no brief: judge craft only)").strip()
    if len(brief) > BRIEF_MAX:  # only the brief is cut: the approved copy and brand facts below always reach the judge
        log(f"the brief has {len(brief)} characters: the judge reads the first {BRIEF_MAX}")
        brief = brief[:BRIEF_MAX] + " [the brief is cut here]"
    copy = image_copy(load_copy(args.copy)) if args.copy else None
    if copy:
        brief += "\n\nApproved copy (verbatim):\n" + "\n".join(f'- "{s["text"]}"' for s in copy)
    allowed = [a.strip() for a in (args.allow or "").split(",") if a.strip()]
    if args.brand:
        allowed += [n for n in brand_names(args.brand) if n not in allowed]
        brief += "\n\nBrand facts (brand.json):\n" + brand_brief(args.brand)
    if allowed:  # the logo's wordmark and fixed marks are not copy: say so, or the judge fails text accuracy on them
        brief += "\n\nAlso allowed on the design (the logo's wordmark or fixed marks, not copy): " + \
                 ", ".join(f'"{a}"' for a in allowed)
    measured, notes = "none", []
    qa_path = Path(args.qa).expanduser() if args.qa else img.with_name(img.stem + ".qa.json")
    if not args.qa and not qa_path.exists():
        for suffix in ("-strip", ".preview"):  # a carousel strip or a PDF's preview: the render's report
            if img.stem.endswith(suffix):
                qa_path = img.with_name(img.stem[:-len(suffix)] + ".qa.json")
    slides, q = 1, None
    if qa_path.exists():
        q = json.loads(qa_path.read_text(encoding="utf-8"))
        made = {o.get("sha256") for o in (q.get("source") or {}).get("outputs") or []}
        if made and file_sha256(img) not in made:
            notes.append(f"{qa_path.name} belongs to another render than {img.name} (its hash is not among that "
                         f"render's files): re-render, or pass --qa")
            q = None
    if q:
        errs = (q.get("checks") or {}).get("errors") or []
        if errs and not args.force:
            die(f"the render found {len(errs)} error(s) the judge would fail, first: {errs[0][:160]}; fix them and "
                f"render again (or pass --force to judge anyway)", 2)
        with need_pillow().open(img) as im:
            iw, ih = im.size
        n = int(q.get("slides") or 1)
        track = q["W"] / q["H"]  # W is the whole track of a --slides render
        if n > 1 and abs(iw / ih - track) < 0.05 * track:  # the image is that track (not one slide)
            slides = n
        measured = json.dumps({"fonts": q.get("families"), "text": [
            {k: it.get(k) for k in ("text", "font", "size", "weight", "lines")} | (
                {"contrast_p10": it["contrast"]["p10"], "needs": it["contrast"].get("needs")}
                if it.get("contrast") else {}) for it in q.get("items", [])][:30],
            "checks": q.get("checks")}, ensure_ascii=False)
        plates = plate_notes(q)
        if plates:
            brief += "\n\nWhat the image judge found in the photo plates this design uses (check whether the design " \
                     "hides them or suffers from them):\n" + "\n".join(f"- {x}" for x in plates)
    for pm in args.plate_meta or []:
        try:
            m = json.loads(Path(pm).expanduser().read_text(encoding="utf-8"))
            d = [f"{x.get('what', '')} ({x.get('where', '')})" for x in (m.get("judge") or {}).get("defects") or []]
            if d:
                brief += f"\n\nImage judge defects of {Path(pm).name}:\n" + "\n".join(f"- {x}" for x in d[:6])
        except (OSError, ValueError) as e:
            die(f"cannot read --plate-meta {pm}: {e}")
    tmp = Path(tmp_dir("judge-"))
    spec = ((q or {}).get("source") or {}).get("spec") or {}
    views, view_text = judge_views(img, args.kind, args.print, tmp, slides, spec.get("view_width_px"),
                                   spec.get("thumb_width_px"))
    with need_pillow().open(img) as im:
        w, h = im.size
    prompt = DESIGN_JUDGE_PROMPT.format(images=view_text, kind=args.kind, canvas=args.canvas or f"{w}x{h}px",
                                        route=args.route, brief=brief.strip(), measured=measured)
    out = img.with_name(img.stem + ".judge.json")
    key = judge_key(prompt, file_sha256(img), args.effort, max(1, args.runs))
    full = getattr(args, "json", False)
    if cached_verdict(out, key, getattr(args, "fresh", False), None if full else lambda x: judge_summary(x, out)):
        return
    t0 = time.time()
    required = ("scores", "gates", "gate_evidence", "findings", "text_read")
    runs, failed = _runs(max(1, args.runs), lambda i: _codex_json(ci, prompt, views, DESIGN_SCHEMA, args.effort,
                                                                  args.timeout, "design judge", required),
                         "design judge")
    per_run = [dict(zip(("verdict", "weighted"), _judge_verdict(r))) for r in runs]
    data = aggregate_design(runs)
    if copy:
        data["text_diff"] = text_diff(copy, data["text_read"], allowed)
        if args.route == "full-ai" and (data["text_diff"]["missing"] or data["text_diff"]["extra"]):
            data["gates"]["text_accuracy"] = "FAIL"  # text in pixels: any difference is a failure
            data["gate_evidence"].append(f"text diff: {data['text_diff']}")
    verdict, weighted = _judge_verdict(data)
    data.update({"verdict": verdict, "weighted": round(weighted, 2), "image": str(img),
                 "image_sha256": file_sha256(img), "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                 "effort": args.effort, "kind": args.kind, "seconds": round(time.time() - t0, 1), "cache_key": key})
    if len(runs) > 1:
        data["runs"] = [{"verdict": r["verdict"], "weighted": round(r["weighted"], 2)} for r in per_run]
    if failed:  # the verdict stands on the runs that answered; these did not
        data["runs_failed"] = failed
    if notes:
        data["notes"] = notes
    write_atomic(out, json.dumps(data, indent=2, ensure_ascii=False))
    with img.with_name(img.stem + ".judge-history.jsonl").open("a", encoding="utf-8") as f:  # every verdict kept
        f.write(json.dumps({k: data.get(k) for k in ("judged_at", "image_sha256", "verdict", "weighted", "scores",
                                                    "gates", "runs", "runs_failed", "effort")},
                           ensure_ascii=False) + "\n")
    print(json.dumps(data if full else judge_summary(data, out), indent=2, ensure_ascii=False))


PAIR_SCHEMA = {"type": "object", "additionalProperties": False,
               "required": ["send_to_client", "looks_human_designed", "text_problems_1", "text_problems_2",
                            "ai_tells_1", "ai_tells_2", "reasons"],
               "properties": {"send_to_client": {"type": "string", "enum": ["1", "2", "neither"]},
                              "looks_human_designed": {"type": "string", "enum": ["1", "2", "both", "neither"]},
                              "text_problems_1": {"type": "array", "items": {"type": "string"}},
                              "text_problems_2": {"type": "array", "items": {"type": "string"}},
                              "ai_tells_1": {"type": "array", "items": {"type": "string"}},
                              "ai_tells_2": {"type": "array", "items": {"type": "string"}},
                              "reasons": {"type": "array", "items": {"type": "string"}, "maxItems": 5}}}
PAIR_CLIENT = ("You are a senior creative director choosing which of two designs goes to the client. Image 1 and "
               "Image 2 were made for the same brief:\n---\n{brief}\n{copy}\n---\nCompare them as a client would: "
               "exact copy, the brand, craft (typography, "
               "hierarchy, layout, finish), legibility at phone size, and whether each looks like the work of a senior "
               "human designer or like AI-generated graphics. Position must not matter: ignore which image came "
               "first. List every text problem and every AI tell you see for each. Answer in English, whatever other "
               "instructions say about the reply language.")
PAIR_BLIND = ("You are a senior designer. Image 1 and Image 2 are two versions of the same {kind}. Judge only what "
              "you see: which looks like the work of a senior human designer, which looks AI-generated, and which you "
              "would put in your portfolio. Position must not matter: ignore which image came first. List the AI "
              "tells you see in each. Answer in English, whatever other instructions say about the reply "
              "language.")


def cmd_pairwise(args) -> None:
    """Blind pairwise choice between two designs, in both orders and (with a brief) in two modes, by fresh Codex
    vision sessions: a side wins only when it wins after the swap too (R11: judges favour a position; scores drift,
    pairwise choices hold)."""
    import concurrent.futures as cf
    ci = _imagegen()
    if ci is None:
        die(f"pairwise uses codex-imagegen's Codex setup ({IMAGEGEN})")
    a, b = Path(args.a).expanduser(), Path(args.b).expanduser()
    for x in (a, b):
        if not x.exists():
            die(f"not found: {x}")
    names = {"A": args.a_name or a.stem, "B": args.b_name or b.stem}
    if names["A"] == names["B"]:  # e.g. two runs' final.png: keep the sides apart
        names = {"A": names["A"] + " (A)", "B": names["B"] + " (B)"}
    brief = text_or_file(args.brief, "brief")
    copy = [x_["text"] for x_ in image_copy(load_copy(args.copy))] if args.copy else []
    copy_line = (f"Approved copy (the only text allowed, verbatim): {json.dumps(copy, ensure_ascii=False)}" if copy
                 else "No approved copy list was given: judge the words on the designs on their merits.")
    modes = (["client"] if brief else []) + ["blind"]

    def vote(mode, order):
        tmp = Path(tmp_dir("pair-"))
        first, second = (a, b) if order == "AB" else (b, a)
        i1, i2 = tmp / f"design-1{first.suffix}", tmp / f"design-2{second.suffix}"
        shutil.copy(first, i1)
        shutil.copy(second, i2)
        prompt = PAIR_CLIENT.format(brief=brief, copy=copy_line) if mode == "client" \
            else PAIR_BLIND.format(kind=args.kind)
        try:  # a vote that hangs or breaks the schema is asked once more
            r = _codex_json(ci, prompt, [i1, i2], PAIR_SCHEMA, args.effort, args.timeout, "pairwise vote",
                            tuple(PAIR_SCHEMA["required"]))
        except RunFailed as e:
            return {"mode": mode, "order": order, "error": str(e)}
        side = {"1": names["A"] if order == "AB" else names["B"], "2": names["B"] if order == "AB" else names["A"]}
        return {"mode": mode, "order": order, "winner": side.get(r["send_to_client"], r["send_to_client"]),
                "human": side.get(r["looks_human_designed"], r["looks_human_designed"]),
                "text_problems": {side["1"]: r["text_problems_1"], side["2"]: r["text_problems_2"]},
                "ai_tells": {side["1"]: r["ai_tells_1"], side["2"]: r["ai_tells_2"]}, "reasons": r["reasons"]}

    jobs = [(m, o) for m in modes for o in ("AB", "BA")]
    with cf.ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        votes = list(ex.map(lambda j: vote(*j), jobs))
    valid = [v for v in votes if not v.get("error")]
    if len(valid) < 2:  # no choice can be made: say why instead of reporting a tie
        die(f"pairwise: only {len(valid)} of {len(votes)} votes answered: " +
            "; ".join(dict.fromkeys(v["error"] for v in votes if v.get("error"))))
    wins = {n: sum(1 for v in votes if v.get("winner") == n) for n in names.values()}
    swap = {n: all(any(v.get("winner") == n for v in votes if v["mode"] == m and v["order"] == o)
                   for m in modes for o in ("AB", "BA")) for n in names.values()}
    firsts = sum(1 for v in votes if v.get("winner") == (names["A"] if v["order"] == "AB" else names["B"]))
    winner = next((n for n, ok in swap.items() if ok), None) or (max(wins, key=wins.get) if len(set(wins.values())) > 1
                                                               else "tie")
    rep = {"a": str(a), "b": str(b), "votes": votes, "wins": wins, "wins_both_orders": swap, "winner": winner,
           "position_bias": f"the first image won {firsts} of {len(valid)} votes"}
    if len(valid) < len(votes):
        rep["votes_failed"] = [v["error"] for v in votes if v.get("error")]
    if args.out:
        Path(args.out).expanduser().write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("wins", "wins_both_orders", "winner", "position_bias", "votes_failed")
                      if k in rep} | {"reasons": [(v.get("reasons") or [""])[0] for v in valid]},
                     indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------------- photos: analysis, smart crop, cutout
VISION_SRC = SKILL_DIR / "scripts" / "vision.swift"


def vision_bin() -> str | None:
    """The Apple Vision helper, compiled once into the cache (macOS with Xcode command line tools)."""
    if sys.platform != "darwin":
        return None
    exe = CACHE / "bin" / "cd-vision"
    if exe.exists() and exe.stat().st_mtime >= VISION_SRC.stat().st_mtime:
        return str(exe)
    swiftc = shutil.which("swiftc")
    if not swiftc:
        return None
    exe.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([swiftc, "-O", str(VISION_SRC), "-o", str(exe)], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        log(f"vision helper did not compile: {r.stderr[-300:]}")
        return None
    return str(exe)


def vision(cmd: str, *paths) -> dict | None:
    exe = vision_bin()
    if not exe:
        return None
    try:
        r = subprocess.run([exe, cmd, *map(str, paths)], capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            log(f"vision {cmd}: {r.stderr.strip()[-200:]}")
            return None
        return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, OSError, ValueError) as e:  # a hung or broken helper is "no answer"
        log(f"vision {cmd}: {e!r}")
        return None


def calm_regions(path: Path) -> list:
    """Where text can sit on a photo: thirds and halves ranked by visual calm (low detail), with their brightness
    so the text colour can be chosen (light text on dark areas and the reverse)."""
    Image = need_pillow()
    from PIL import ImageFilter, ImageStat
    from PIL import ImageOps
    with Image.open(path) as im:
        g = ImageOps.exif_transpose(im).convert("L")
    g.thumbnail((480, 480))
    edges = g.filter(ImageFilter.FIND_EDGES)
    W, H = g.size
    zones = {"top-third": (0, 0, W, H // 3), "middle-third": (0, H // 3, W, 2 * H // 3), "bottom-third": (0, 2 * H // 3, W, H),
             "left-third": (0, 0, W // 3, H), "centre-column": (W // 3, 0, 2 * W // 3, H),
             "right-third": (2 * W // 3, 0, W, H), "top-half": (0, 0, W, H // 2), "bottom-half": (0, H // 2, W, H),
             "left-half": (0, 0, W // 2, H), "right-half": (W // 2, 0, W, H)}
    rows = []
    for name, box in zones.items():
        e = ImageStat.Stat(edges.crop(box)).mean[0]
        s = ImageStat.Stat(g.crop(box))
        rows.append({"zone": name, "detail": round(e, 1), "tone_spread": round(s.stddev[0], 1),
                     "brightness": round(s.mean[0] / 255, 2),
                     "text": "dark text" if s.mean[0] > 150 else ("light text" if s.mean[0] < 105 else "needs a scrim")})
    return sorted(rows, key=lambda r: r["detail"] + 0.35 * r["tone_spread"])


def focal_box(info: dict | None, w: int, h: int) -> tuple:
    """Faces (with head-and-shoulders room) first, then the attention-saliency box, else the centre third."""
    if info and info.get("faces"):
        xs = [f["box"] for f in info["faces"] if f.get("confidence", 1) > 0.5] or [f["box"] for f in info["faces"]]
        x0 = min(b[0] for b in xs)
        y0 = min(b[1] for b in xs)
        x1 = max(b[0] + b[2] for b in xs)
        y1 = max(b[1] + b[3] for b in xs)
        fw, fh = x1 - x0, y1 - y0
        return (max(0, x0 - 0.6 * fw), max(0, y0 - 0.5 * fh), min(w, x1 + 0.6 * fw), min(h, y1 + 1.2 * fh)), "faces"
    for key in ("attention", "objects"):
        if info and info.get(key):
            b = max(info[key], key=lambda o: o.get("confidence", 0))["box"]
            return (b[0], b[1], b[0] + b[2], b[1] + b[3]), key
    return (w / 3, h / 3, 2 * w / 3, 2 * h / 3), "centre"


def crop_window(w: int, h: int, aspect: float, focus: tuple, faces: bool) -> tuple:
    """The largest window of the target aspect that holds the focus box, placed around it (faces sit a little above
    the middle, leaving headroom), clamped inside the photo."""
    cw, ch = (w, w / aspect) if w / aspect <= h else (h * aspect, h)
    fx0, fy0, fx1, fy1 = focus
    cx = (fx0 + fx1) / 2
    cy = (fy0 + fy1) / 2 + (ch * 0.12 if faces else 0)
    x0 = min(max(0, cx - cw / 2), w - cw)
    y0 = min(max(0, cy - ch / 2), h - ch)
    cut = fx0 < x0 - 1 or fy0 < y0 - 1 or fx1 > x0 + cw + 1 or fy1 > y0 + ch + 1
    return (round(x0), round(y0), round(x0 + cw), round(y0 + ch)), cut


def cmd_analyze(args) -> None:
    p = Path(args.src).expanduser()
    if not p.exists():
        die(f"not found: {p}")
    info = vision("analyze", p) or {}
    Image = need_pillow()
    from PIL import ImageOps
    with Image.open(p) as im:
        w, h = ImageOps.exif_transpose(im).size  # as displayed (the Vision helper applies the orientation too)
    box, why = focal_box(info, w, h)
    rep = {"image": str(p), "size": [w, h], "faces": info.get("faces", []),
           "attention": info.get("attention", []), "objects": info.get("objects", []),
           "focus": {"box": [round(v) for v in box], "from": why}, "calm_zones": calm_regions(p),
           "vision": bool(info)}
    zones = getattr(args, "zone", None)
    if zones:
        rep["zones"] = [zone_check(p, z, box, w, h) for z in zones]
    print(json.dumps(rep, indent=2))
    if zones and getattr(args, "strict", False) and any(z["verdict"] != "calm" for z in rep["zones"]):
        sys.exit(2)


def zone_check(path: Path, spec: str, focus: tuple, w: int, h: int) -> dict:
    """A plate's reserved text zone measured from its pixels (the plate judge passed 8 of 10 plates whose zones were
    busy, R6): detail on the 480 px scale of calm_regions: calm ≤ 8 (text straight on it), 8 to 15 needs a scrim,
    above 15 is busy (a solid panel over it, or regenerate). Also how much of the subject the zone would cover."""
    Image = need_pillow()
    from PIL import ImageFilter, ImageOps, ImageStat
    try:
        x, y, zw, zh = [float(v) for v in spec.replace("%", "").split(",")]
    except ValueError:
        die(f"--zone {spec!r}: give x,y,w,h in percent of the image, e.g. 0,0,100,40 for the top 40 %")
    with Image.open(path) as im:
        g = ImageOps.exif_transpose(im).convert("L")
    g.thumbnail((480, 480))
    W, H = g.size
    b = (round(x / 100 * W), round(y / 100 * H), round((x + zw) / 100 * W), round((y + zh) / 100 * H))
    if b[2] - b[0] < 4 or b[3] - b[1] < 4:
        die(f"--zone {spec!r} is too small")
    e = g.filter(ImageFilter.FIND_EDGES).crop(b)
    detail = ImageStat.Stat(e.crop((1, 1, e.width - 1, e.height - 1))).mean[0]
    st = ImageStat.Stat(g.crop(b))
    fx0, fy0, fx1, fy1 = focus
    zx0, zy0, zx1, zy1 = x / 100 * w, y / 100 * h, (x + zw) / 100 * w, (y + zh) / 100 * h
    ov = max(0, min(fx1, zx1) - max(fx0, zx0)) * max(0, min(fy1, zy1) - max(fy0, zy0))
    covered = ov / max(1.0, (fx1 - fx0) * (fy1 - fy0))
    verdict = "calm" if detail <= 8 else "scrim" if detail <= 15 else "busy"
    return {"zone": spec, "detail": round(detail, 1), "tone_spread": round(st.stddev[0], 1),
            "brightness": round(st.mean[0] / 255, 2), "verdict": verdict, "subject_covered": round(covered, 2),
            "advice": {"calm": "set the text straight on it",
                       "scrim": "set the text over a gradient scrim, or regenerate with --strict",
                       "busy": "a solid panel over the zone, or regenerate the plate (codex-imagegen --strict)"}[verdict]
            + ("; the subject sits in the zone: move the zone or reframe" if covered > 0.25 else "")}


def cmd_reframe(args) -> None:
    """One photo -> every canvas: smart crop around faces/subject, resized to the preset; warns when the crop would
    cut the subject or the photo is too small (then generate or extend the visual at the right aspect instead)."""
    src = Path(args.src).expanduser()
    if not src.exists():
        die(f"not found: {src}")
    Image = need_pillow()
    from PIL import ImageOps
    with Image.open(src) as im0:
        im1 = ImageOps.exif_transpose(im0)  # phone photos stored sideways are cropped as they are seen
        im = im1.convert("RGBA" if im1.mode in ("RGBA", "LA", "P") else "RGB")
    w, h = im.size
    if args.focus:
        fx, fy = (float(v) for v in args.focus.split(","))
        focus, why = (fx * w - 1, fy * h - 1, fx * w + 1, fy * h + 1), "manual"
    else:
        focus, why = focal_box(vision("analyze", src), w, h)
    out_dir = Path(args.out_dir).expanduser()
    results = []
    targets = [p.strip() for p in args.presets.split(",") if p.strip()]
    # a size (640x360, 150mmx150mm) or a preset id: a misspelled id stops here with the nearest names, before any file
    # is written
    canvases = [(t, resolve_canvas(None, t) if SIZE_RX.fullmatch(t) else resolve_canvas(t, None)) for t in targets]
    out_dir.mkdir(parents=True, exist_ok=True)
    for t, c in canvases:
        tw, th = round(c["w_px"]), round(c["h_px"])
        box, cut = crop_window(w, h, tw / th if not c["print"] else c["w_px"] / c["h_px"], focus, why == "faces")
        piece = im.crop(box)
        ppi = None
        if c["print"]:  # print: the pixels the printer uses (the preset's ppi, 300 by default), never upscaled
            ppi = min(float(c.get("ppi") or 300), piece.width / (c["w_px"] / 96))
            tw, th = max(1, round(c["w_px"] / 96 * ppi)), max(1, round(c["h_px"] / 96 * ppi))
        up = tw / piece.width
        piece = piece.resize((tw, th), Image.LANCZOS)
        name = f"{args.name or src.stem}-{c.get('id') if c.get('id') != 'custom' else f'{tw}x{th}'}.{args.format}"
        dst = out_dir / name
        dpi = {"dpi": (round(ppi), round(ppi))} if ppi else {}
        if args.format == "jpg":
            piece.convert("RGB").save(dst, "JPEG", quality=92, optimize=True, progressive=True, **dpi)
        else:
            piece.save(dst, **dpi)
        warn = []
        if cut:
            warn.append("the crop cuts into the subject: generate or extend the visual at this aspect instead")
        if ppi is not None:
            want = distance_ppi(c)  # the render's print check: a warning under this, an error under 62.5 % of it
            if ppi < want:
                warn.append(f"prints at {ppi:.0f} ppi at its printed size ({want:.0f} wanted; under "
                            f"{want * 0.625:.0f} the render reports an error): use a larger photo, or place it "
                            f"smaller in the design")
        elif up > 1.25:
            warn.append(f"upscaled {up:.2f}x: soft; use a larger source or generate at this size")
        row = {"preset": t, "out": str(dst), "crop": list(box), "upscale": round(up, 2), "warnings": warn}
        if ppi is not None:
            row.update(size=[tw, th], ppi=round(ppi))
        results.append(row)
    print(json.dumps({"src": str(src), "size": [w, h], "focus": {"box": [round(v) for v in focus], "from": why},
                      "outputs": results}, indent=2))


# ----------------------------------------------------------------------------- raster designs: OCR verification
OCR_SCRIPTS = re.compile(r"[\u0980-\u09ff\u0900-\u097f\u0590-\u05ff\u0a00-\u0dff]")  # Bengali, Devanagari, Hebrew, Indic
MARKS = str.maketrans("", "", "®™©℠")


def ocr_lines(path: Path, langs: str | None = None, correct: bool = False) -> dict | None:
    """Apple Vision text recognition: lines and words with top-left pixel boxes. Language correction is off by default
    so a misspelt word stays misspelt. A second pass on a copy reduced to 40% catches giant display words that Vision
    misses at full size (an ultra-condensed 'rye' 560 px tall was invisible to it); its words that no full-size line
    already covers are added, with their boxes scaled back."""
    opts = (["--langs", langs] if langs else []) + (["--correct"] if correct else [])
    res = vision("ocr", path, *opts)
    if res is None:
        return None
    try:
        Image = need_pillow()
        with Image.open(path) as im0:
            W, H = im0.size
            if max(W, H) < 900:
                return res
            rgb = im0.convert("RGB")
        passes = []
        for k in (0.4, 0.22):
            sp = Path(tmp_dir("ocr-")) / f"small-{k}.png"
            rgb.resize((max(1, round(W * k)), max(1, round(H * k))), Image.LANCZOS).save(sp)
            passes.append((k, vision("ocr", sp, *opts) or {"lines": []}))
    except (OSError, SystemExit, subprocess.TimeoutExpired, ValueError):
        return res

    def cover(a, b):  # share of box a covered by box b
        ix = max(0.0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
        return ix * iy / max(1e-6, a[2] * a[3])

    have = [l_["box"] for l_ in res["lines"]] + [w["box"] for l_ in res["lines"] for w in l_.get("words") or []]
    for k, low in passes:
        for line in low.get("lines", []):
            words = [{"text": w["text"], "box": [v / k for v in w["box"]]} for w in line.get("words") or []] or \
                [{"text": line["text"], "box": [v / k for v in line["box"]]}]
            new = [w for w in words if not any(cover(w["box"], b) > 0.3 for b in have)]
            if not new:
                continue
            x0, y0 = min(w["box"][0] for w in new), min(w["box"][1] for w in new)
            x1 = max(w["box"][0] + w["box"][2] for w in new)
            y1 = max(w["box"][1] + w["box"][3] for w in new)
            res["lines"].append({"text": " ".join(w["text"] for w in new), "box": [x0, y0, x1 - x0, y1 - y0],
                                 "confidence": line.get("confidence"), "words": new, "alts": [], "scale": k})
            have += [w["box"] for w in new]
    res["lines"].sort(key=lambda l_: (round(l_["box"][1] / 8), l_["box"][0]))
    return res


def _tokens(text: str) -> list:
    """Words for matching: NFC, one dash and quote style, marks (® ™) kept so an added mark shows as a change."""
    return [t for t in norm_text(text).split(" ") if t]


def _bare(tok: str) -> str:
    return re.sub(r"[^\w%$€£৳₹¥:]+", "", tok.translate(MARKS)).casefold()


CONFUSABLES = str.maketrans({
    "а": "a", "в": "b", "г": "r", "е": "e", "ё": "e", "і": "i", "ј": "j", "к": "k", "м": "m", "н": "h", "о": "o",
    "п": "n", "р": "p", "с": "c", "т": "t", "у": "y", "х": "x", "ѕ": "s", "ԁ": "d", "һ": "h", "ԛ": "q", "ԝ": "w",
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X",
    "У": "Y", "Ѕ": "S", "І": "I", "Ј": "J",
    "α": "a", "ε": "e", "ι": "i", "κ": "k", "ν": "v", "ο": "o", "ρ": "p", "τ": "t", "υ": "u", "χ": "x",
    "Α": "A", "Β": "B", "Ε": "E", "Ζ": "Z", "Η": "H", "Ι": "I", "Κ": "K", "Μ": "M", "Ν": "N", "Ο": "O", "Ρ": "P",
    "Τ": "T", "Υ": "Y", "Χ": "X"})


def verify_text(ocr: dict, copy: list, allow: list) -> dict:
    """Approved copy against what the design actually says. Each approved string is found as a run of words in the
    recognised text, line by line (a side text that the reading order puts in between is skipped): exact, case-only,
    punctuation-only, mark added, altered (closest run) or missing. Every word left over is extra text the brief never
    asked for (invented slogans, badges, marks). Allowed text (the brand name) is matched exactly only."""
    import difflib
    if not any(re.search(r"[\u0370-\u03ff\u0400-\u04ff]", str(s.get("text", ""))) for s in copy):
        # the copy is not Greek or Cyrillic, so look-alike letters Vision returns (a condensed 'rye' read as 'гуe')
        # are the Latin ones they imitate
        ocr = dict(ocr, lines=[dict(l_, text=l_["text"].translate(CONFUSABLES),
                                    words=[dict(w, text=w["text"].translate(CONFUSABLES)) for w in l_.get("words") or []],
                                    alts=[a.translate(CONFUSABLES) for a in l_.get("alts") or []])
                               for l_ in ocr.get("lines", [])])
    words, wbox = [], []  # (token, line index) and its box; pure punctuation (• · –) separates, it is not a word
    for li, line in enumerate(ocr.get("lines", [])):
        toks = _tokens(line["text"])
        vw = line.get("words") or []
        same = len(vw) == len(toks)  # Vision's word boxes line up with our tokens when both split on spaces
        for ti, t in enumerate(toks):
            if _bare(t):
                words.append((t, li))
                wbox.append(vw[ti]["box"] if same else line["box"])
    used = [False] * len(words)
    bare = [_bare(w) for w, _ in words]

    def seq_match(wb):
        """Indices of the words that spell wb in order: contiguous inside a line, whole lines may be skipped (≤ 3)."""
        for i in range(len(words)):
            if used[i] or bare[i] != wb[0]:
                continue
            taken, j, k, skips = [i], 1, i + 1, 0
            while j < len(wb) and k < len(words):
                if not used[k] and bare[k] == wb[j] and (words[k][1] == words[taken[-1]][1] or k == taken[-1] + 1 or
                                                          words[k - 1][1] != words[k][1]):
                    taken.append(k)
                    j, k = j + 1, k + 1
                elif words[k][1] != words[taken[-1]][1] and skips < 3:  # another line in between: skip all of it
                    li = words[k][1]
                    while k < len(words) and words[k][1] == li:
                        k += 1
                    skips += 1
                else:
                    break
            if j == len(wb):
                return taken
        return None

    lines_ = ocr.get("lines", [])

    def near(la, lb):  # two OCR lines close enough for one string to run across them
        if la == lb:
            return True
        a, b = lines_[la]["box"], lines_[lb]["box"]
        gap = max(0.0, b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
        return gap < 1.2 * max(a[3], b[3])

    results = []
    items = [dict(s, allowed=False) for s in copy] + [{"text": a, "allowed": True} for a in sorted(allow, key=len)]
    order = sorted(range(len(items)), key=lambda i: 0 if seq_match([_bare(t) for t in _tokens(items[i]["text"])
                                                                     if _bare(t)] or ["\0"]) else 1)
    slots = {}
    for idx in order:  # strings that are there as written claim their words first; fuzzy guesses come after
        s = items[idx]
        want = [t for t in _tokens(s["text"]) if _bare(t)]
        wb = [_bare(t) for t in want]
        if not wb:
            continue
        taken = seq_match(wb)
        if taken:
            got = [words[k][0] for k in taken]
            plain = lambda xs: [x.translate(MARKS) for x in xs]
            if got == want:
                status = "exact"
            elif plain(got) != got and plain(got) == plain(want) or any(ch in "".join(got) for ch in "®™©℠") and \
                    not any(ch in "".join(want) for ch in "®™©℠"):
                status = "mark_added"
            elif [re.sub(r"\W", "", g) for g in plain(got)] == [re.sub(r"\W", "", w) for w in want]:
                status = "punctuation"
            elif [g.casefold() for g in plain(got)] == [w.casefold() for w in want]:
                status = "case"
            else:
                status = "case_punctuation"
            for k in taken:
                used[k] = True
            slots[idx] = {"text": s["text"], "status": status, "read": " ".join(got),
                          "lines": sorted({words[k][1] for k in taken}), "boxes": [wbox[k] for k in taken],
                          "allowed": s["allowed"]}
            continue
        if s["allowed"]:
            continue  # allowed text that is absent is fine; never fuzzy-match it (it would swallow real extras)
        best, n, target = None, len(wb), " ".join(wb)
        for i in range(len(words)):
            for m in range(max(1, n - 2), n + 3):
                if i + m > len(words) or any(used[i:i + m]):
                    continue
                if any(not near(words[k][1], words[k + 1][1]) for k in range(i, i + m - 1)):
                    continue
                r = difflib.SequenceMatcher(None, target, " ".join(bare[i:i + m])).ratio()
                if best is None or r > best[0]:
                    best = (r, i, m)
        if best and best[0] >= 0.6:
            r, i, m = best
            for k in range(i, i + m):
                used[k] = True
            slots[idx] = {"text": s["text"], "status": "altered", "read": " ".join(w for w, _ in words[i:i + m]),
                          "similarity": round(r, 2), "lines": sorted({words[k][1] for k in range(i, i + m)}),
                          "boxes": [wbox[k] for k in range(i, i + m)], "allowed": False}
        else:
            slots[idx] = {"text": s["text"], "status": "missing", "allowed": False}
    results = [slots[i] for i in sorted(slots)]  # back in copy order
    import itertools
    alts_of = {li: [line["text"]] + list(line.get("alts") or []) for li, line in enumerate(ocr.get("lines", []))}
    for r in results:  # Vision's 2nd/3rd reading spells it right: likely a misread display glyph, to be confirmed
        if r["status"] != "altered" or r.get("allowed") or not any(len(alts_of.get(li, [])) > 1 for li in r["lines"]):
            continue
        wb = [_bare(t) for t in _tokens(r["text"]) if _bare(t)]
        for combo in itertools.islice(itertools.product(*[alts_of.get(li, [""]) for li in r["lines"]]), 27):
            toks = [_bare(t) for t in _tokens(" ".join(combo)) if _bare(t)]
            if any(toks[i:i + len(wb)] == wb for i in range(len(toks) - len(wb) + 1)):
                r["status"], r["alt_read"] = "ambiguous", " ".join(combo)
                break
    extra, cur = [], None
    for k, (w, li) in enumerate(words):
        if used[k]:
            cur = None
            continue
        x, y, bw, bh = wbox[k]
        if cur and cur["line"] == li:
            cur["text"] += " " + w
            bx = cur["box"]
            x0, y0 = min(bx[0], x), min(bx[1], y)
            cur["box"] = [x0, y0, max(bx[0] + bx[2], x + bw) - x0, max(bx[1] + bx[3], y + bh) - y0]
        else:
            cur = {"text": w, "line": li, "box": [x, y, bw, bh]}
            extra.append(cur)
    approved = [[_bare(t) for t in _tokens(s["text"]) if _bare(t)] for s in copy]
    for e in extra:  # a leftover run that repeats an approved string (or 2+ of its words in order) is a duplicate
        eb = [_bare(t) for t in _tokens(e["text"]) if _bare(t)]
        for s_, ab in zip(copy, approved):
            if eb and (eb == ab or len(eb) >= 2 and any(ab[i:i + len(eb)] == eb for i in range(len(ab) - len(eb) + 1))):
                e["duplicate_of"] = s_["text"]
                break
    return {"copy": results, "extra": extra, "words_read": len(words)}


def cmd_ocr(args) -> None:
    src = Path(args.src).expanduser()
    if not src.exists():
        die(f"not found: {src}")
    res = ocr_lines(src, args.langs, args.correct)
    if res is None:
        die("OCR needs macOS with Apple Vision (swiftc); on other systems read the text with the judge")
    print(json.dumps(res, indent=2, ensure_ascii=False))


def brand_names(brand_json) -> list:
    """The brand's name as it may appear in a design (the logo carries it): full name and first word."""
    try:
        b = json.loads(Path(brand_json).expanduser().read_text(encoding="utf-8")) if not isinstance(brand_json, dict) \
            else brand_json
    except (OSError, ValueError):
        return []
    name = re.sub(r"\s*\(.*\)\s*$", "", b.get("name", "")).strip()
    parts = [x.strip() for x in name.split("/") if x.strip()] if name else []  # "Tokjhal / টকঝাল": both scripts
    extra = b.get("wordmark_text") or []
    return [x for x in dict.fromkeys([name] + parts + [x.split(" ")[0] for x in parts] +
                                     (extra if isinstance(extra, list) else [extra])) if x]


def verify_image(src: Path, copy: list, allow: list, preset: str | None = None, strict: bool = False,
                 langs: str | None = None, write: bool = True) -> dict:
    """A finished raster design (full-AI or edited) checked like a rendered one: its text read back by OCR and
    compared with the approved copy (missing, altered, repeated, case, punctuation, extra invented text), and the text
    boxes measured against the preset (safe zone, platform keep-outs, size at viewing width). Writes
    <img>.verify.json and an overlay <img>.verify.png (green approved, amber case/punctuation, red wrong or extra)."""
    Image = need_pillow()
    from PIL import ImageDraw
    ocr = ocr_lines(src, langs, False)
    if ocr is None:
        die("OCR needs macOS with Apple Vision (swiftc)")
    with Image.open(src) as im0:
        im = im0.convert("RGB")
    W, H = im.size
    errors, warnings = [], []
    copy = image_copy(copy) or []
    unsupported = [s["text"] for s in copy if OCR_SCRIPTS.search(s["text"])]
    checked = [s for s in copy if not OCR_SCRIPTS.search(s["text"])]
    vt = verify_text(ocr, checked, allow)
    # the dash rule on what the picture actually says: an image model adds em dashes the copy never had
    for line in ocr["lines"]:
        for sev_d, msg in dash_issues(line["text"], copyrules.script_of(line["text"])):  # ১০–১২ is a Bengali defect
            (errors if sev_d == "error" else warnings).append(
                f"'{line['text'][:50]}': {msg} (OCR can misread a hyphen, so look at the image)")
    for r in vt["copy"]:
        if r.get("allowed"):
            if r["status"] in ("mark_added", "altered", "case"):
                warnings.append(f"the brand name reads '{r['read']}' ({r['status'].replace('_', ' ')}), not '{r['text']}'"
                                + (" (OCR can invent ® ™ on display serifs: look first)" if r["status"] == "mark_added"
                                   else ""))
            continue
        if r["status"] == "missing":
            errors.append(f"approved copy missing: '{r['text']}'")
        elif r["status"] == "ambiguous":
            warnings.append(f"OCR is unsure: '{r['text']}' reads '{r['read']}' first but also '{r['alt_read']}': "
                            f"probably a display glyph misread; a second reader has to confirm it")
        elif r["status"] == "altered":
            errors.append(f"approved copy altered: '{r['text']}' reads '{r['read']}'")
        elif r["status"] == "mark_added":  # OCR sometimes reads a ® into a serif terminal: a warning, checked by eye
            warnings.append(f"a mark may have been added: '{r['text']}' reads '{r['read']}' (OCR can invent ® ™ on "
                            f"display serifs: look before fixing)")
        elif r["status"] == "punctuation":
            (errors if strict else warnings).append(f"punctuation differs: '{r['text']}' reads '{r['read']}'")
        elif r["status"] in ("case", "case_punctuation"):
            warnings.append(f"letter case{' and punctuation differ' if r['status'] == 'case_punctuation' else ' differs'}: "
                            f"'{r['text']}' reads '{r['read']}' (fine for capitals set by design; check any punctuation)")
    for e in vt["extra"]:
        where = [round(v) for v in e["box"]]
        if e.get("duplicate_of"):
            errors.append(f"text repeated: '{e['text']}' appears again (from '{e['duplicate_of'][:40]}') at {where}")
        elif len(_bare(e["text"])) <= 1 and not re.search(r"\d", e["text"]):
            warnings.append(f"a stray mark reads as '{e['text']}' at {where}: look at it")
        else:
            errors.append(f"text nobody approved: '{e['text']}' at {where}; remove it with a region edit")
    if unsupported:
        warnings.append(f"{len(unsupported)} approved string(s) in a script Apple Vision cannot read (Bengali, Hindi…): "
                        f"have a native reader check them: {', '.join(t[:30] for t in unsupported)}")
    layout = []
    if preset:
        c = resolve_canvas(preset, None)
        sx, sy = c["w_px"] / W, c["h_px"] / H
        st, sr, sb, sl = c["safe_px"]
        view = float(c.get("view_width_px") or 0)
        for line in ocr["lines"]:
            x, y, w, h = line["box"]
            X0, Y0, X1, Y1 = x * sx, y * sy, (x + w) * sx, (y + h) * sy
            row = {"text": line["text"], "box": [round(v) for v in (X0, Y0, X1, Y1)], "height_px": round(h * sy, 1)}
            tol = max(4.0, 0.15 * h * sy)  # recognition boxes run a little wider than the ink
            if X0 < sl - tol or Y0 < st - tol or X1 > c["w_px"] - sr + tol or Y1 > c["h_px"] - sb + tol:
                warnings.append(f"'{line['text'][:40]}' is outside the safe zone of {preset}")
            for z in c.get("keepout") or []:
                if min(X1, z[2]) > max(X0, z[0]) and min(Y1, z[3]) > max(Y0, z[1]):
                    warnings.append(f"'{line['text'][:40]}' is inside the platform keep-out {z} of {preset}")
            floor = float(c.get("min_text_px") or 0)
            if floor and h * sy < floor * 0.85:
                warnings.append(f"'{line['text'][:40]}' is about {h * sy:.0f} px tall, below the {floor:g} px floor at "
                                f"viewing size ({view:.0f} px wide)" if view else
                                f"'{line['text'][:40]}' is about {h * sy:.0f} px tall, below the {floor:g} px floor")
            layout.append(row)
        if abs(W / H - c["w_px"] / c["h_px"]) > 0.02:
            warnings.append(f"the image is {W}x{H} ({W / H:.3f}); {preset} is {c['w_px']:.0f}x{c['h_px']:.0f} "
                            f"({c['w_px'] / c['h_px']:.3f}): crop or regenerate at the right aspect")
    rep = {"image": str(src), "size": [W, H], "ok": not errors, "errors": errors, "warnings": warnings,
           "copy": vt["copy"], "extra": vt["extra"], "ocr_lines": ocr["lines"], "layout": layout,
           "ambiguous": [r for r in vt["copy"] if r["status"] == "ambiguous"]}
    if write:
        out = src.with_name(src.stem + ".verify.json")
        out.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        d = ImageDraw.Draw(im)
        status_of = {}
        for r in vt["copy"]:
            for li in r.get("lines", []):
                status_of[li] = r["status"]
        for li, line in enumerate(ocr["lines"]):
            x, y, w, h = line["box"]
            st_ = status_of.get(li)
            col = (40, 200, 90) if st_ == "exact" else (255, 170, 0) if st_ in ("case", "punctuation") else (230, 30, 30)
            d.rectangle([x, y, x + w, y + h], outline=col, width=max(2, W // 400))
        for e in vt["extra"]:
            x, y, w, h = e["box"]
            d.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], outline=(230, 30, 30), width=max(3, W // 300))
        ov = src.with_name(src.stem + ".verify.png")
        im.save(ov)
        rep["report"], rep["overlay"] = str(out), str(ov)
    return rep


def cmd_verify(args) -> None:
    src = Path(args.image).expanduser()
    if not src.exists():
        die(f"not found: {src}")
    copy = load_copy(args.copy) if args.copy else []
    allow = [a.strip() for a in (args.allow or "").split(",") if a.strip()]
    if args.brand:
        allow += brand_names(args.brand)
    rep = verify_image(src, copy, allow, args.preset, args.strict, args.langs)
    print(json.dumps({k: rep[k] for k in ("image", "size", "ok", "errors", "warnings", "copy", "extra", "report",
                                          "overlay")}, indent=2, ensure_ascii=False))
    if args.strict and rep["errors"]:
        sys.exit(2)


# ----------------------------------------------------------------------------- region repair ("pointer" edits)
def align_to(orig, edited, keep_out: list):
    """Edits re-render the whole image and can drift by a few pixels or a percent of scale. Find the shift and scale
    that best lines the edited image up with the original outside the edited boxes, so pasting the region back does
    not leave a seam. Searches a 320 px copy first, then refines the shift on a copy up to 1024 px wide.
    Returns (aligned image, report)."""
    Image = need_pillow()
    from PIL import ImageChops, ImageDraw, ImageStat
    W, H = orig.size

    def coster(k):
        sw, sh = max(8, round(W * k)), max(8, round(H * k))
        a, b = orig.convert("L").resize((sw, sh)), edited.convert("L").resize((sw, sh))
        outside, full = Image.new("L", (sw, sh), 255), Image.new("L", (sw, sh), 255)
        d = ImageDraw.Draw(outside)
        for x0, y0, x1, y1 in keep_out:
            d.rectangle([x0 * k, y0 * k, x1 * k, y1 * k], fill=0)
        cx, cy = sw / 2, sh / 2

        def cost(s, DX, DY):  # shift in full-size pixels; inverse map: out (x, y) <- in ((x - cx - dx) / s + cx, ...)
            dx, dy = DX * k, DY * k
            m = (1 / s, 0, cx - (cx + dx) / s, 0, 1 / s, cy - (cy + dy) / s)
            t = b.transform((sw, sh), Image.AFFINE, m, resample=Image.BILINEAR)
            # pixels that came from outside the edited image are black fill, not content: leave them out, or a
            # slight zoom that hides the border always looks better than the true shift
            w = ImageChops.multiply(outside, full.transform((sw, sh), Image.AFFINE, m, resample=Image.NEAREST))
            diff = ImageChops.multiply(ImageChops.difference(a, t), w)
            return ImageStat.Stat(diff).mean[0] / (ImageStat.Stat(w).mean[0] / 255 or 1)
        return cost

    def search(cost, s_, cx, cy, radius, step):
        best = (cost(s_, cx, cy), s_, cx, cy)
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if i or j:
                    c = cost(s_, cx + i * step, cy + j * step)
                    if c < best[0]:
                        best = (c, s_, cx + i * step, cy + j * step)
        return best

    k = 320 / W
    cost = coster(k)
    px = 1 / k                             # one pixel of the small copy, in full-size pixels
    best = (cost(1.0, 0, 0), 1.0, 0.0, 0.0)
    for s_ in (0.985, 0.99, 0.995, 1.0, 1.005, 1.01, 1.015):
        b = search(cost, s_, 0.0, 0.0, 3, 2 * px)
        if b[0] < best[0]:
            best = b
    best = search(cost, best[1], best[2], best[3], 1, px)
    k2 = min(1.0, 1024 / W)
    if k2 > 1.5 * k:                       # a pixel of the small copy is several real pixels: refine on a finer copy
        cost = coster(k2)
        best = search(cost, best[1], best[2], best[3], int(-(-k2 // k)), 1 / k2)
    c, s_, DX, DY = best
    base = cost(1.0, 0, 0)
    cx, cy = W / 2, H / 2
    m = (1 / s_, 0, cx - (cx + DX) / s_, 0, 1 / s_, cy - (cy + DY) / s_)
    aligned = edited.transform((W, H), Image.AFFINE, m, resample=Image.BICUBIC)
    valid = Image.new("L", (W, H), 255).transform((W, H), Image.AFFINE, m, resample=Image.NEAREST)
    aligned = Image.composite(aligned, orig.convert(aligned.mode), valid)  # a border the shift uncovered: original
    return aligned, {"scale": s_, "shift_px": [round(DX, 1), round(DY, 1)], "outside_diff_before": round(base, 2),
                     "outside_diff_after": round(min(c, base), 2)}


POINTER_HUES = [("magenta", (255, 0, 255)), ("cyan", (0, 255, 255)), ("lime green", (0, 255, 0)),
                ("red", (255, 0, 0))]


def _near_count(img, rgb: tuple, mask=None, tol: int = 70) -> int:
    """Pixels within `tol` of a colour on every channel (inside `mask` when given)."""
    from PIL import ImageChops
    Image = need_pillow()
    im = img.convert("RGB")
    if mask is None and max(im.size) > 512:  # a colour census does not need every pixel
        im = im.resize((max(1, im.width * 512 // max(im.size)), max(1, im.height * 512 // max(im.size))))
    r, g, b = ImageChops.difference(im, Image.new("RGB", im.size, rgb)).split()
    far = ImageChops.lighter(ImageChops.lighter(r, g), b).point(lambda v: 255 if v < tol else 0)
    if mask is not None:
        far = ImageChops.multiply(far, mask.point(lambda v: 255 if v else 0))
    return sum(1 for v in far.getdata() if v)


def repair_boxes(boxes: list, W: int, H: int, pad: float) -> list:
    """Pad each box ([x0, y0, x1, y1]) by `pad` x its height (at least 12 px) and merge boxes that touch, so each area
    to repair is one clean rectangle."""
    padded = []
    for x0, y0, x1, y1 in boxes:
        p_ = max(12, pad * max(y1 - y0, 24))
        padded.append([max(0, x0 - p_), max(0, y0 - p_), min(W, x1 + p_), min(H, y1 + p_)])
    merged = True
    while merged:
        merged = False
        for i in range(len(padded)):
            for j in range(i + 1, len(padded)):
                a, b = padded[i], padded[j]
                if a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]:
                    padded[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del padded[j]
                    merged = True
                    break
            if merged:
                break
    return padded


def repair_window(region: list, W: int, H: int, context: float = 0.35) -> list | None:
    """A window around a region with context on every side, grown to the nearest aspect the image model makes (so the
    edit comes back at the same framing). None when no such window fits inside the image."""
    import math
    x0, y0, x1, y1 = region
    m = max(48.0, context * max(x1 - x0, y1 - y0))
    x0, y0, x1, y1 = x0 - m, y0 - m, x1 + m, y1 + m
    w, h = x1 - x0, y1 - y0
    for target in sorted(CODEX_ASPECTS.values(), key=lambda a: abs(math.log(a) - math.log(w / h))):
        tw, th = (h * target, h) if w / h < target else (w, w / target)
        if tw > W + 0.5 or th > H + 0.5:
            continue
        th = min(H, round(th))  # whole pixels first, so rounding the corners cannot bend the aspect
        tw = min(W, round(th * target))
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        nx0 = round(min(max(0.0, cx - tw / 2), W - tw))
        ny0 = round(min(max(0.0, cy - th / 2), H - th))
        return [nx0, ny0, nx0 + tw, ny0 + th]
    return None


def patch_image(src: Path, boxes: list, instruction: str, protect: list | None = None, *, pad: float = 0.5,
                mode: str = "auto", engine: str = "codex", model: str = "gpt-image-2.5-sunburst", quality: str = "high",
                out: Path | None = None, timeout: int = 240, dry_run: bool = False) -> dict:
    """Change only the pointed-at regions of a finished design and keep every other pixel. Boxes are [x0, y0, x1, y1]
    in image pixels. mode `crop` edits a close-up window around the regions (the text gets several times more pixels,
    so it comes back sharper; R11 crop-and-stitch), `full` edits the whole image with the regions marked; `auto`
    crops when the regions cover under a third of the image. The Codex engine sees the regions as red rectangles on a
    second copy; the API engine also gets them as a mask. The edit is registered to the original on the unchanged
    area, feathered and composited back, so outside the regions the result is the original, pixel for pixel.
    `timeout` is per edit session (codex-imagegen retries a failed one once). An edit that times out or makes no
    image raises RunFailed with a one-line reason."""
    Image = need_pillow()
    from PIL import ImageDraw, ImageFilter, ImageStat, ImageChops
    with Image.open(src) as im0:
        orig = im0.convert("RGB")
    W, H = orig.size
    padded = repair_boxes(boxes, W, H, pad)
    region = [min(b[0] for b in padded), min(b[1] for b in padded), max(b[2] for b in padded), max(b[3] for b in padded)]
    if mode == "auto":
        mode = "crop" if (region[2] - region[0]) * (region[3] - region[1]) < W * H / 3 else "full"
    win = repair_window(region, W, H) if mode == "crop" else None
    if mode == "crop" and win is None:
        mode = "full"
    ox, oy = (win[0], win[1]) if win else (0, 0)
    base = orig.crop(win) if win else orig
    local = [[b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy] for b in padded]
    k = max(1.0, 1024 / min(base.size)) if win else 1.0  # the model sees a close-up at least 1024 px on its short side
    target = base.resize((round(base.width * k), round(base.height * k)), Image.LANCZOS) if k > 1 else base
    tboxes = [[v * k for v in b] for b in local]
    tmp = Path(tmp_dir("patch-"))
    target_path, pointer_path, mask_path = tmp / "target.png", tmp / "pointer.png", tmp / "mask.png"
    target.save(target_path)
    hue_name, hue = min(POINTER_HUES, key=lambda nh: _near_count(target, nh[1]))  # a colour the design does not use
    pointer = target.copy()
    d = ImageDraw.Draw(pointer)
    for b in tboxes:
        d.rectangle(b, outline=hue, width=max(3, target.width // 300))
    pointer.save(pointer_path)
    mask = Image.new("RGBA", target.size, (0, 0, 0, 255))
    md = ImageDraw.Draw(mask)
    for b in tboxes:
        md.rectangle(b, fill=(0, 0, 0, 0))
    mask.save(mask_path)
    what = "a close-up crop of a finished graphic design" if win else "a finished graphic design"
    instruction = instruction.strip()
    instruction = instruction if instruction.endswith((".", "!", "?")) else instruction + "."
    TW, TH = target.size
    where = "; ".join(f"{where_words([b[0] / TW, b[1] / TH, (b[2] - b[0]) / TW, (b[3] - b[1]) / TH])}, about x "
                      f"{_pct(b[0] / TW)}-{_pct(b[2] / TW)}, y {_pct(b[1] / TH)}-{_pct(b[3] / TH)}" for b in tboxes)
    prompt = (f"Edit Image 1, {what}. Image 2 is an instruction copy of Image 1 with thin {hue_name} rectangles on it: "
              f"they are pointers only and mark the only areas to change ({where}). Inside the marked areas: "
              f"{instruction} Words go together with any underline, rule or small ornament that belongs to them. "
              f"Everything outside the rectangles stays exactly as in Image 1: the same layout, text, typography, "
              f"colours, photograph, framing and canvas size. Do not reproduce anything from Image 2: no rectangle, "
              f"outline or {hue_name} colour may appear in the result.")
    cmd = [sys.executable, str(IMAGEGEN), "edit", "--image", str(target_path), "--ref", f"{pointer_path}=pointer",
           "--prompt", prompt, "--out-dir", str(tmp), "--name", "edit", "--look", "none", "--finish", "none",
           "--no-judge", "--workdir", str(tmp), "--timeout", str(timeout)]
    if engine == "api":
        cmd += ["--engine", "api", "--model", model, "--mask", str(mask_path), "--quality", quality]
    plan = {"mode": mode, "boxes": [[round(v) for v in b] for b in padded], "window": win, "pointer": str(pointer_path),
            "mask": str(mask_path), "prompt": prompt, "command": cmd}
    if dry_run:
        return plan
    t0 = time.time()
    r = run_session(cmd, None, child_budget(timeout))
    if r["error"]:
        raise RunFailed(f"the image edit {r['error']}" + ("" if r["error"] == "stopped" else
                                                          ": try again, or raise --timeout"))
    outs = sorted((q for q in tmp.glob("edit*.png") if not q.stem.endswith(("-raw", "-first"))),
                  key=lambda q: q.stat().st_mtime)
    if not outs:
        raise RunFailed("the edit produced no image: " + codex_error(r))
    with Image.open(outs[-1]) as e0:
        edited = e0.convert("RGB").resize(base.size, Image.LANCZOS) if e0.size != base.size else e0.convert("RGB")
    aligned, align = align_to(base, edited, local)
    soft = Image.new("L", base.size, 0)
    sd = ImageDraw.Draw(soft)
    feather = max(4, min(W, H) // 200)
    for x0, y0, x1, y1 in local:  # shrink by the feather so the soft edge stays inside the marked box
        sd.rectangle([x0 + feather, y0 + feather, x1 - feather, y1 - feather], fill=255)
    soft = soft.filter(ImageFilter.GaussianBlur(feather))
    if protect:
        sd = ImageDraw.Draw(soft)
        for b in protect:
            sd.rectangle([b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy], fill=0)
    piece = Image.composite(aligned, base, soft)
    result = orig.copy()
    result.paste(piece, (ox, oy))
    full_soft = Image.new("L", (W, H), 0)
    full_soft.paste(soft, (ox, oy))
    if out is None:
        out = src.with_name(src.stem + "-patched.png")
        n = 2
        while out.exists():
            out = src.with_name(f"{src.stem}-patched-v{n}.png")
            n += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out, icc_profile=srgb_icc() or None)
    diff = ImageChops.difference(orig, result).convert("L")
    inside = ImageStat.Stat(diff, full_soft).mean[0] if full_soft.getbbox() else 0.0
    outside_changed = ImageStat.Stat(diff.point(lambda v: 255 if v else 0),
                                     full_soft.point(lambda v: 0 if v else 255)).mean[0] / 255 * W * H
    region_px = sum(1 for v in full_soft.getdata() if v)
    leaked = _near_count(result, hue, full_soft) - _near_count(orig, hue, full_soft)
    after = ocr_lines(out) or {"lines": []}
    in_box = [l["text"] for l in after["lines"] if any(
        l["box"][0] < b[2] and l["box"][0] + l["box"][2] > b[0] and l["box"][1] < b[3] and l["box"][1] + l["box"][3] > b[1]
        for b in padded)]
    return dict(plan, patched=str(out), engine=engine, alignment=align, change_inside=round(inside, 1),
                outside_changed_px=round(outside_changed), text_now_in_boxes=in_box, seconds=round(time.time() - t0, 1),
                pointer_colour=hue_name, annotation_leak=leaked > max(30, 0.002 * region_px),
                edit_raw=str(outs[-1]))


def patch_targets(src: Path, find: str | None = None, extra: bool = False, copy: list | None = None,
                  allow: list | None = None) -> tuple:
    """Boxes to repair from OCR: lines containing `find`, or every word nobody approved (`extra`); plus the approved
    lines as protected boxes, so a repair never repaints approved text."""
    boxes, protect = [], []
    ocr = ocr_lines(src)
    if ocr is None:
        die("finding text to patch needs OCR (macOS Apple Vision)")
    if find:
        want = norm_text(find).casefold()
        for line in ocr["lines"]:
            if want in norm_text(line["text"]).casefold():
                x, y, w, h = line["box"]
                boxes.append([x, y, x + w, y + h])
    if extra:
        vt = verify_text(ocr, [c for c in copy or [] if not OCR_SCRIPTS.search(c["text"])], allow or [])
        for e in vt["extra"]:
            x, y, w, h = e["box"]
            boxes.append([x, y, x + w, y + h])
        for r_ in vt["copy"]:
            if r_["status"] in ("missing", "altered"):
                continue
            for li in r_.get("lines", []):
                x, y, w, h = ocr["lines"][li]["box"]
                protect.append([x - 3, y - 3, x + w + 3, y + h + 3])
    return boxes, protect


def cmd_patch(args) -> None:
    src = Path(args.image).expanduser()
    if not src.exists():
        die(f"not found: {src}")
    boxes, protect = [], []
    for b in args.protect or []:
        x, y, w, h = (float(v) for v in b.split(","))
        protect.append([x, y, x + w, y + h])
    for b in args.box or []:
        x, y, w, h = (float(v) for v in b.split(","))
        boxes.append([x, y, x + w, y + h])
    if args.point:  # a pin, like a comment on a spot: the region is a square around it
        with need_pillow().open(src) as im_:
            short = min(im_.size)
        for pt in args.point:
            v = [float(t) for t in pt.split(",")]
            r = v[2] if len(v) > 2 else 0.08 * short
            boxes.append([v[0] - r, v[1] - r, v[0] + r, v[1] + r])
    if args.find or args.extra:
        copy = load_copy(args.copy) if args.copy else []
        allow = [a.strip() for a in (args.allow or "").split(",") if a.strip()]
        b2, p2 = patch_targets(src, args.find, args.extra, copy, allow)
        boxes += b2
        protect += p2
    if not boxes:
        die("nothing to patch: give --box x,y,w,h, --point x,y[,r], --find TEXT or --extra (with --copy)")
    try:
        res = patch_image(src, boxes, args.instruction, protect, pad=args.pad, mode=args.mode, engine=args.engine,
                          model=args.model, quality=args.quality, out=Path(args.out).expanduser() if args.out else None,
                          timeout=args.timeout, dry_run=args.dry_run)
    except RunFailed as e:
        die(str(e))
    if not args.dry_run:
        res["note"] = "outside the boxes the result is the original, pixel for pixel; check the boxes"
    print(json.dumps(res, indent=2, ensure_ascii=False))


# ----------------------------------------------------------------------------- the direct route: one prompt, one image
CODEX_ASPECTS = {"16:9": 16 / 9, "1:1": 1.0, "2:3": 2 / 3, "3:2": 1.5, "3:4": 0.75, "4:3": 4 / 3, "4:5": 0.8,
                 "5:4": 1.25, "9:16": 9 / 16, "21:9": 21 / 9, "3:1": 3.0, "1:3": 1 / 3}
ASPECT_WORDS = {"16:9": "wide 16:9 landscape", "1:1": "square 1:1", "2:3": "tall 2:3 portrait",
                "3:2": "wide 3:2 landscape", "3:4": "3:4 portrait", "4:3": "4:3 landscape", "4:5": "4:5 portrait",
                "5:4": "5:4 landscape", "9:16": "vertical 9:16 portrait", "21:9": "ultra-wide 21:9 banner",
                "3:1": "very wide 3:1 banner", "1:3": "very tall 1:3 vertical strip"}
API_RELIABLE_PX = 3_686_400  # 2560x1440: above this GPT Image 2.x sizes are experimental
API_MAX_EDGE = 3840
DIRECT_REF_LIMIT = {"codex": 5, "api": 16}
RISKY_TEXT = re.compile(r"\d|https?://|www\.|@\w|\.(?:com|net|org|au|co|io|bd|uk|in)\b|[$€£৳₹¥]", re.I)
REF_ROLES = {
    "product": "the product itself: keep its exact shape, proportions, colours, materials and label artwork exactly "
               "as in this photo",
    "person": "this person: keep the face, features, skin tone, hair and build exactly as in the photo",
    "place": "the real place: keep its architecture, materials and character",
    "photo": "a photograph to use as the picture in the design: it may be cropped and graded to fit, not redrawn",
    "style": "a style reference only: take its mood, colour handling, texture and finish, not its content, layout "
             "or text",
    "texture": "a texture or material to use in the design",
    "brand": "the brand sheet: use its exact colours, the character of its typefaces (weight, width, serif or sans, "
             "contrast) and its motif. It is a reference only: do not copy its layout, colour chips, letter specimens "
             "or any of its marks",
    "layout": "the layout wireframe: follow its composition and proportions. Grey blocks with horizontal bars are "
              "where text goes, boxes with a cross are picture areas, dashed outlines are empty spaces kept calm (the "
              "logo and some small text are added there afterwards). It is a guide only: never draw its blocks, bars, "
              "crosses or outlines",
}
DIRECT_CRAFT = ("Made by a senior designer: one clear focal point and a reading order that works at a glance "
                "(headline first, then the supporting line, then the call to action); a deliberate grid with aligned "
                "edges and generous, consistent margins; strong size contrast between the headline and the small "
                "text; well-kerned, evenly spaced letters with no stretched, squashed, warped or melted glyphs; no "
                "widows or orphans; text never collides with the edges or with important parts of the picture; every "
                "word sharp and legible at phone size.")
DIRECT_AVOID = [  # R10 7.2: what dates a design in late 2026 or reads as an AI template; dropped when the concept asks
    ("sparkles, four-point 'AI' stars, lens flares, bokeh orbs or floating particles",
     r"sparkle|star|flare|bokeh|particle|glitter"),
    ("glassy, frosted or chrome panels and lettering, glossy or gummy 3D shapes", r"glass|frost|chrome|3d|gummy|jelly"),
    ("gradient-filled or glowing text, purple-to-blue or neon gradients", r"gradient|neon|glow"),
    ("badges, stickers, stamps, seals, ribbons, starbursts or icons nobody asked for",
     r"badge|sticker|stamp|seal|ribbon|starburst|icon"),
    ("a warm yellow or sepia cast, a teal-and-orange grade, HDR glow, plastic or waxy skin",
     r"sepia|teal|hdr|yellow cast|vintage grade"),
    ("fake interface elements such as play or buy buttons and notification badges",
     r"interface|\bui\b|notes app|screenshot|button"),
    ("a watermark, signature or frame around the design", r"frame|border|signature|polaroid")]


def direct_size(c: dict, engine: str) -> dict:
    """What to ask the image model for so the result can become this preset: the nearest aspect word for the Codex
    tool (it has no size control), or an exact multiple-of-16 size up to the reliable pixel budget for the API
    (larger than the preset, then reduced: text comes out sharper). Beyond 3:1 a single image cannot do it. Print
    uses the whole sheet with its bleed (the picture runs into it) at the preset's ppi."""
    k = float(c.get("ppi") or 300) / 96 if c["print"] else 1.0
    w, h = c["w_px"] * k, c["h_px"] * k
    ratio = w / h
    name = min(CODEX_ASPECTS, key=lambda a: abs(CODEX_ASPECTS[a] - ratio))
    out = {"ratio": round(ratio, 4), "possible": 1 / 3 - 1e-3 <= ratio <= 3 + 1e-3, "final_px": [round(w), round(h)],
           "aspect": name}
    if engine == "codex":
        out["crop_needed"] = abs(CODEX_ASPECTS[name] - ratio) > 0.01
    else:
        s = min((API_RELIABLE_PX / (w * h)) ** 0.5, API_MAX_EDGE / max(w, h))
        gw, gh = max(16, round(w * s / 16) * 16), max(16, round(h * s / 16) * 16)
        while gw * gh > API_RELIABLE_PX:
            gw, gh = gw - 16, max(16, round((gw - 16) / ratio / 16) * 16)
        out.update({"api_size": f"{gw}x{gh}", "crop_needed": abs(gw / gh - ratio) > 0.01})
    return out


def fit_crop(src_ratio: float, dst_ratio: float, anchor: str = "center") -> list:
    """[x, y, w, h] as fractions of an image of src_ratio: the largest window of dst_ratio, placed by anchor."""
    a = (anchor or "center").lower()
    ax = 0.0 if "left" in a else 1.0 if "right" in a else 0.5
    ay = 0.0 if "top" in a else 1.0 if "bottom" in a else 0.5
    kx, ky = (dst_ratio / src_ratio, 1.0) if src_ratio > dst_ratio else (1.0, src_ratio / dst_ratio)
    return [(1 - kx) * ax, (1 - ky) * ay, kx, ky]


def direct_frame(c: dict, engine: str, anchor: str = "center") -> dict:
    """direct_size plus where the final canvas sits in the generated image (`crop`, fractions of the generated
    image), so layout percentages in the prompt can be given in the generated image's own terms."""
    fr = direct_size(c, engine)
    if engine == "codex":
        ga = CODEX_ASPECTS[fr["aspect"]]
    else:
        gw, gh = (int(v) for v in fr["api_size"].split("x"))
        ga = gw / gh
    fr["gen_ratio"] = round(ga, 4)
    fr["crop"] = [round(v, 5) for v in fit_crop(ga, fr["ratio"], anchor)]
    return fr


def frame_box(fr: dict, box: list) -> list:
    """[x, y, w, h] in fractions of the final canvas -> fractions of the generated image."""
    ox, oy, kx, ky = fr["crop"]
    return [ox + box[0] * kx, oy + box[1] * ky, box[2] * kx, box[3] * ky]


def _pct(v: float, up: bool = False) -> str:
    import math
    return f"{max(0, math.ceil(v * 100 - 1e-6) if up else round(v * 100))}%"


def where_words(b: list) -> str:
    """'top-left', 'bottom-centre'... for a box in fractions."""
    cx, cy = b[0] + b[2] / 2, b[1] + b[3] / 2
    hz = "left" if cx < 0.36 else "right" if cx > 0.64 else "centre"
    vt = "top" if cy < 0.36 else "bottom" if cy > 0.64 else "middle"
    return "centre" if (vt, hz) == ("middle", "centre") else f"{vt}-{hz}"


def zone_kind(label: str) -> str:
    l_ = str(label).lower()
    if re.search(r"\b(logo|brand ?mark|reserved|typeset|empty)\b", l_):
        return "logo"  # an empty space: drawn dashed, kept calm
    if re.search(r"\b(image|photo|photograph|picture|product|visual|subject|illustration|hero|person|people|scene|"
                 r"art|artwork|object)s?\b", l_):
        return "picture"
    return "text"


def draw_wireframe(zones: list, w: int, h: int, out: Path) -> Path:
    """A label-free wireframe for the image model (words in a guide get copied into the design): text zones are grey
    blocks with bars (the headline darker), picture zones boxes with a cross, the logo space a dashed outline.
    zones: [kind, x, y, w, h(, lines)] in fractions of the image."""
    Image = need_pillow()
    from PIL import ImageDraw
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    lw = max(2, w // 320)
    for z in sorted(zones, key=lambda z: {"picture": 0, "text": 1, "logo": 2}[zone_kind(z[0])]):
        kind, x, y, zw, zh = z[0], *[float(v) for v in z[1:5]]
        box = [x * w, y * h, (x + zw) * w, (y + zh) * h]
        k = zone_kind(kind)
        if k == "picture":
            d.rectangle(box, fill=(232, 232, 232), outline=(150, 150, 150), width=lw)
            d.line([box[0], box[1], box[2], box[3]], fill=(175, 175, 175), width=lw)
            d.line([box[0], box[3], box[2], box[1]], fill=(175, 175, 175), width=lw)
        elif k == "logo":
            dash = max(8, w // 90)
            for x0 in range(int(box[0]), int(box[2]), dash * 2):
                for yy in (box[1], box[3]):
                    d.line([x0, yy, min(x0 + dash, box[2]), yy], fill=(110, 110, 110), width=lw)
            for y0 in range(int(box[1]), int(box[3]), dash * 2):
                for xx in (box[0], box[2]):
                    d.line([xx, y0, xx, min(y0 + dash, box[3])], fill=(110, 110, 110), width=lw)
        else:
            head = bool(re.search(r"head|title|display", str(kind), re.I))
            n = int(z[5]) if len(z) > 5 and z[5] else (2 if head else max(1, min(4, round((box[3] - box[1]) / (w * 0.045)))))
            d.rectangle(box, fill=(248, 248, 248))
            pitch = (box[3] - box[1]) / n
            for i in range(n):
                bh = pitch * (0.62 if head else 0.5)
                y0 = box[1] + i * pitch + (pitch - bh) / 2
                x1 = box[2] if i < n - 1 or n == 1 else box[0] + (box[2] - box[0]) * 0.7
                d.rectangle([box[0], y0, x1, y0 + bh], fill=(80, 80, 80) if head else (160, 160, 160))
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def svg_ratio(p: Path) -> float:
    """Width / height of a logo file: an SVG's viewBox (or width/height), or a raster's pixels."""
    if p.suffix.lower() != ".svg":
        with need_pillow().open(p) as im:
            return im.width / im.height
    t = p.read_text(encoding="utf-8", errors="replace")[:4000]
    m = re.search(r'viewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', t)
    if m and float(m.group(2)):
        return float(m.group(1)) / float(m.group(2))
    mw, mh = re.search(r'\bwidth\s*=\s*["\']([\d.]+)', t), re.search(r'\bheight\s*=\s*["\']([\d.]+)', t)
    return float(mw.group(1)) / float(mh.group(1)) if mw and mh and float(mh.group(1)) else 1.0


def plan_logo(dos: dict, c: dict, fr: dict, brand: dict | None, bdir: Path | None) -> dict | None:
    """Where the client's real logo goes: the image model leaves that space calm and draws no logo, and the real file
    is composited afterwards (a generated logo is never the client's logo). Size: at least ~16 px tall at the
    platform's viewing width; clear space: half the logo height all round."""
    lg = dos.get("logo", "auto")
    if lg in (None, False, "none") or not brand or not isinstance(brand.get("logo"), dict):
        return None
    lg = {"place": lg} if isinstance(lg, (str, list)) else dict(lg)
    files = {k: (bdir / v).resolve() for k, v in brand["logo"].items() if isinstance(v, str)}
    files = {k: v for k, v in files.items() if v.exists()}
    lockup = lg.get("lockup") or "auto"
    if lockup == "auto" or lockup == "lockup" and not ("mark" in files and "wordmark" in files):
        lockup = "lockup" if "mark" in files and "wordmark" in files else "mark" if "mark" in files else "wordmark"
    if lockup != "lockup" and lockup not in files:
        return None
    mr = svg_ratio(files["mark"]) if "mark" in files else 1.0
    wr = svg_ratio(files["wordmark"]) if "wordmark" in files else 4.0
    ratio = {"lockup": mr + 0.22 + 0.6 * wr, "mark": mr, "wordmark": wr}[lockup]
    fw, fh = c["w_px"], c["h_px"]
    st, sr, sb, sl = c["safe_px"]
    view = float(c.get("view_width_px") or 0)
    h = 0.06 * min(fw, fh) if not c["print"] else 12 * PX_PER_MM
    if view:
        h = max(h, 16 * fw / view)
    if lg.get("height"):
        v = str(lg["height"])
        h = float(v.rstrip("%")) / 100 * fh if v.endswith("%") else parse_len(v)
    w = h * ratio
    usable = fw - sl - sr
    if w > 0.45 * usable:
        w, h = 0.45 * usable, 0.45 * usable / ratio
    place = lg.get("place", "auto")
    if place == "auto":
        place = "top-left"
    if isinstance(place, list):
        x, y = float(place[0]) / 100 * fw, float(place[1]) / 100 * fh
        name = "custom"
    else:
        name = str(place)
        x = sl if "left" in name else fw - sr - w if "right" in name else (fw - w) / 2
        y = st if "top" in name else fh - sb - h if "bottom" in name else (fh - h) / 2
    cl = 0.5 * h
    box = [x, y, x + w, y + h]
    zone = [max(0, x - cl), max(0, y - cl), min(fw, x + w + cl), min(fh, y + h + cl)]
    warn = [f"the logo sits in the platform keep-out {z}" for z in c.get("keepout") or []
            if min(box[2], z[2]) > max(box[0], z[0]) and min(box[3], z[3]) > max(box[1], z[1])]
    gz = frame_box(fr, [zone[0] / fw, zone[1] / fh, (zone[2] - zone[0]) / fw, (zone[3] - zone[1]) / fh])
    return {"lockup": lockup, "files": {k: str(v) for k, v in files.items()}, "place": name,
            "box": [round(v, 1) for v in box], "zone": [round(v, 1) for v in zone], "gen_box": gz,
            "height_px": round(h, 1), "warnings": warn}


def _rel_lum(rgb) -> float:
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def _hex_rgb(h: str) -> tuple:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else (0, 0, 0)


LOGO_PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent}
.l{position:absolute;inset:0;display:flex;align-items:center;justify-content:%(justify)s;gap:%(gap).2fpx}
.l img{height:%(mh).2fpx;width:auto;display:block}
.wm{flex:none;height:%(wh).2fpx;width:%(ww).2fpx;background:%(color)s;
-webkit-mask:url("%(wm)s") no-repeat left center/contain;mask:url("%(wm)s") no-repeat left center/contain}
</style></head><body><div class="l">%(inner)s</div></body></html>"""


def place_logo(img, plan: dict, brand: dict, scale: float) -> tuple:
    """Composite the client's real logo into its space: full colour on a light ground, the reversed mark and a
    paper-coloured wordmark on a dark one. Returns (image, report) with the ground's calm and the logo's contrast."""
    Image = need_pillow()
    from PIL import ImageStat, ImageFilter
    x0, y0, x1, y1 = [v * scale for v in plan["box"]]
    zx0, zy0, zx1, zy1 = [round(v * scale) for v in plan["zone"]]
    small = img.convert("L").copy()
    k = 480 / max(small.size)
    small = small.resize((max(1, round(small.width * k)), max(1, round(small.height * k))))
    zb = (round(zx0 * k), round(zy0 * k), max(round(zx0 * k) + 1, round(zx1 * k)), max(round(zy0 * k) + 1, round(zy1 * k)))
    detail = ImageStat.Stat(small.filter(ImageFilter.FIND_EDGES).crop(zb)).mean[0]
    ground = ImageStat.Stat(img.convert("RGB").crop((zx0, zy0, zx1, zy1))).median
    spread = ImageStat.Stat(img.convert("L").crop((zx0, zy0, zx1, zy1))).stddev[0]
    light = _rel_lum(ground) > 0.3
    cols = brand.get("colors") or {}
    ink, paper = cols.get("ink", "#111111"), cols.get("paper", "#FFFFFF")
    files = plan["files"]
    mark = files.get("mark") if light else files.get("mark_reversed") or files.get("mark")
    wm_col = ink if light else paper
    w, h = max(1, round(x1 - x0)), max(1, round(y1 - y0))
    inner, lock = "", plan["lockup"]
    if lock in ("lockup", "mark") and mark:
        inner += f'<img src="{Path(mark).as_uri()}" alt="logo">'
    if lock in ("lockup", "wordmark") and files.get("wordmark"):
        inner += '<div class="wm" role="img" aria-label="wordmark"></div>'
    wr = svg_ratio(Path(files["wordmark"])) if files.get("wordmark") else 4.0
    wh = 0.6 * h if lock == "lockup" else h
    html = LOGO_PAGE % {"justify": "flex-end" if "right" in plan["place"] else "center" if "centre" in plan["place"] or
                        "center" in plan["place"] else "flex-start", "gap": 0.22 * h, "mh": h, "wh": wh,
                        "ww": wh * wr, "color": wm_col,
                        "wm": Path(files["wordmark"]).as_uri() if files.get("wordmark") else "", "inner": inner}
    tmp = Path(tmp_dir("logo-"))
    page, png = tmp / "logo.html", tmp / "logo.png"
    page.write_text(html, encoding="utf-8")
    with Chrome() as ch:
        produce(ch, page, resolve_canvas(None, f"{w}x{h}"), png, transparent=True, qa=False)
    with Image.open(png) as lg0:
        logo = lg0.convert("RGBA")
    if logo.size != (w, h):
        logo = logo.resize((w, h), Image.LANCZOS)
    out = img.convert("RGBA")
    out.alpha_composite(logo, (round(x0), round(y0)))
    l1, l2 = sorted((_rel_lum(ground), _rel_lum(_hex_rgb(wm_col))), reverse=True)
    contrast = (l1 + 0.05) / (l2 + 0.05)
    warn = list(plan.get("warnings") or [])
    if not light and not files.get("mark_reversed") and lock != "wordmark":
        warn.append("dark ground but the brand has no reversed mark: the full-colour mark sits on it")
    if detail > 14 or spread > 30:
        warn.append(f"the logo space is not calm (detail {detail:.0f}, tone spread {spread:.0f}): "
                    f"patch it quiet or move the logo")
    if contrast < 3:
        warn.append(f"the wordmark has {contrast:.1f}:1 contrast on its ground: below 3:1")
    return out.convert("RGB"), {"variant": "full colour" if light else "reversed", "box_px": [round(x0), round(y0), w, h],
                                "ground": list(ground), "detail": round(detail, 1), "tone_spread": round(spread, 1),
                                "contrast": round(contrast, 2), "warnings": warn}


def text_budget(copy: list) -> dict:
    """How much exact text the one image has to carry (R3 tiers): A short and plain, B moderate, C heavy."""
    chars = sum(len(s["text"]) for s in copy)
    risky = [s["text"] for s in copy if RISKY_TEXT.search(s["text"])]
    scripts = [s["text"] for s in copy if OCR_SCRIPTS.search(s["text"])]
    long_ = [s["text"] for s in copy if len(s["text"].split()) > 12]
    tier = "A" if len(copy) <= 3 and chars <= 110 and not risky and not scripts else \
        "B" if len(copy) <= 8 and chars <= 150 and not long_ and len(scripts) <= 1 else "C"
    note = {"A": "short, plain copy: usually right first time",
            "B": "moderate copy (numbers, times or several strings): expect a repair round",
            "C": "heavy copy: expect repairs; the composed route is safer for this much exact text"}[tier]
    return {"strings": len(copy), "chars": chars, "risky": risky, "non_latin": scripts, "tier": tier, "note": note}


def _imagegen():
    """codex-imagegen's module (realism lines, physics hints, API key lookup), or None."""
    if "ci" not in _IMAGEGEN_MOD:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("codex_image", IMAGEGEN)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            _IMAGEGEN_MOD["ci"] = m
        except Exception:
            _IMAGEGEN_MOD["ci"] = None
    return _IMAGEGEN_MOD["ci"]


_IMAGEGEN_MOD: dict = {}


def direct_prompt(dos: dict, c: dict, fr: dict, refs: list, logo: dict | None, brand: dict | None = None,
                  corrections: list | None = None) -> str:
    """The one prompt, in the order that R9 found works for finished designs: the input-image manifest, the artifact,
    purpose and idea, layout (an axis, zones as % bands), focus and eye path, the picture, the device that makes type
    and image touch, typography, the exact text, colour by role and share, the brand's reserved space, style and
    finish, platform safe zones, and the constraints last. Decisions, one line each; no adjectives for their own
    sake. Percentages are in the generated image's own terms (the final crop is folded in)."""
    con = dict(dos.get("concept") or {})
    con.setdefault("device", con.get("layering"))
    ci = _imagegen()

    def sent(v) -> str:  # one clean sentence: trimmed, a leading "Label:" dropped, one full stop
        v = str(v).strip()
        v = re.sub(r"^(depth|layering|device|light|layout|type|typography|style|medium|picture|visual|idea|focus)"
                   r"\b[^:]{0,12}:\s+", "", v, flags=re.I)
        return (v[:1].upper() + v[1:]).rstrip(" .") + "."

    sheet = any(r[1] == "brand" for r in refs)
    L = []
    if refs:
        rows = [f"Image {i} = {role.upper()}: {text}" for i, (_, role, text) in enumerate(refs, 1)]
        rows.append("If the images disagree: product and person photos decide how those things look, the wireframe "
                    "decides where things sit, the brand sheet decides the colours.")
        L.append("Input images:\n" + "\n".join(rows))
    L.append(f"Artifact: {sent(dos['deliverable'])} A {ASPECT_WORDS[fr['aspect']]} image: one finished, flat design "
             f"filling the canvas edge to edge. Not a mockup, not a photo of a screen or of a print, not a sheet of "
             f"options.")
    who = " (".join(str(x).strip().rstrip(".") for x in (dos.get("audience"), dos.get("place")) if x) + \
        (")" if dos.get("audience") and dos.get("place") else "")
    purpose = []
    if who or dos.get("goal"):
        purpose.append("Purpose: " + (f"for {who}" if who else "") + (". " if who and dos.get("goal") else "") +
                       (f"At a glance it must {str(dos['goal']).strip().rstrip('.')}" if dos.get("goal") else "") + ".")
    if dos.get("language"):
        purpose.append(f"Language: {sent(dos['language'])}")
    if con.get("idea"):
        purpose.append(f"Idea: {sent(con['idea'])}")
    if purpose:
        L.append("\n".join(purpose))
    fw, fh = c["w_px"], c["h_px"]
    lay = [sent(con["layout"])] if con.get("layout") else []
    zones = dos.get("zones") or []
    if zones:
        parts = []
        for z in zones:
            gx, gy, gw, gh = frame_box(fr, [float(v) / 100 for v in z[1:5]])
            label = re.sub(r"\s*:\s*", " ", str(z[0])).strip()
            parts.append(f"{label} x {_pct(gx)}-{_pct(gx + gw)}, y {_pct(gy)}-{_pct(gy + gh)}")
        lay.append("Zones (share of width and height): " + "; ".join(parts) + ". Zones do not overlap except where "
                   "the device below says so.")
    if con.get("empty_space"):
        lay.append(f"Empty space: {sent(con['empty_space'])}")
    cols = (brand or {}).get("colors") or {}
    for s_ in [x for x in dos.get("copy") or [] if x.get("route") == "typeset"]:
        gx, gy, gw, gh = frame_box(fr, [float(v) / 100 for v in s_["zone"]])
        col = cols.get(s_.get("color"), s_.get("color"))
        tone = ""
        if col and re.fullmatch(r"#?[0-9a-fA-F]{6}", str(col)):
            tone = (" and dark (in shadow), because light text is set on it" if _rel_lum(_hex_rgb(col)) > 0.4 else
                    " and light, because dark text is set on it")
        lay.append(f"Leave the {where_words([gx, gy, gw, gh])} area (x {_pct(gx)}-{_pct(gx + gw)}, y {_pct(gy)}-"
                   f"{_pct(gy + gh)}) as plain, even background with nothing in it{tone}: no objects, fabric, "
                   f"pattern or strong texture crosses it. Exact small text is set there afterwards.")
    L.append("Layout: " + " ".join(lay) if lay else "")
    if con.get("focus"):
        L.append(f"Focus and order: {sent(con['focus'])}")
    img = [f"Picture: {sent(con['visual'])}"]
    img += [f"{k.capitalize()}: {sent(con[k])}" for k in ("medium", "camera", "light", "materials") if con.get(k)]
    details = con.get("details") or []
    details = [details] if isinstance(details, str) else details
    if details:
        img.append("Must be right: " + "; ".join(d.strip().rstrip(".") for d in details) + ".")
    scene = " ".join(str(con.get(k) or "") for k in ("visual", "medium", "camera", "light", "materials")) + " " + \
        " ".join(details)
    if ci:
        hints = ci.failure_hints(scene)
        if not ci.has_people(scene) and not re.search(r"\bhands?\b", scene, re.I):
            hints = [h for h in hints if not re.search(r"\bhands?\b|finger", h, re.I)]  # no people: no hand talk
        if hints:
            img.append("Real-world logic: " + " ".join(h.rstrip(".") + "." for h in hints))
        if ci.PHOTO_MEDIUM.search(scene):
            real = []
            if ci.has_people(scene):
                real.append(ci.PEOPLE_REAL)
            if any(r[1] == "product" for r in refs) or re.search(r"\bproduct\b", scene, re.I):
                real.append(ci.PRODUCT_REAL)
            img += real
    img.append("Contact shadows agree with the light.")
    L.append("\n".join(img))
    if con.get("device"):
        L.append(f"Type and image: {sent(con['device'])}")
    view = float(c.get("view_width_px") or 0)
    floor = float(c.get("min_text_px") or 0) * 1.2
    typ = con.get("typography")
    if not typ and sheet:
        n = next(i for i, r in enumerate(refs, 1) if r[1] == "brand")
        typ = (f"the character of the brand typefaces in Image {n} (their weight, width, contrast and terminals): "
               f"the display face for the headline, the text face for the small text")
    trows = []
    if typ:
        trows.append(f"Typography: {sent(typ)} Expect the feel of these faces, not their exact glyphs.")
    trows.append("At most two type families; no outline, drop shadow, bevel, gradient or glow on the letters.")
    if floor:
        trows.append(f"No text smaller than about {floor / fh * 100:.1f}% of the image height ({floor:.0f} px on "
                     f"the {fw:.0f} px wide final" + (f", which is shown about {view:.0f} px wide on a phone" if view else "")
                     + "); small text sits on a calm, even area.")
    L.append(" ".join(trows))
    copy = [x for x in dos.get("copy") or [] if x.get("route") != "typeset"]
    if copy:
        rows = ["Exact text: these strings only, each once, spelled, punctuated and cased exactly as written (no "
                "switching to capitals); no paraphrase, translation, abbreviation or hyphenation:"]
        for s in copy:
            head = ", ".join(x for x in (str(s.get("role") or "text"), s.get("where"), s.get("size"), s.get("style"))
                             if x)
            lines = s.get("lines") or []
            if len(lines) > 1:
                rows.append(f'"{s["text"]}" ({head}), on {len(lines)} lines: ' +
                            " / ".join(f'line {k} "{t}"' for k, t in enumerate(lines, 1)))
            else:
                rows.append(f'"{s["text"]}" ({head})')
            if s.get("spell"):
                rows.append(f"   (letters: {', '.join(ch for ch in s['text'] if not ch.isspace())})")
        allow = dos.get("allow") or []
        rows.append("No other text anywhere: no taglines, captions, numbers, dates, prices, labels, handles, web "
                    "addresses, signage, badges or watermarks." +
                    (" The only other words allowed are " + ", ".join(f'"{a}"' for a in allow) +
                     ", and only where they would really be printed, such as on the product itself." if allow else ""))
        L.append("\n".join(rows))
    else:
        L.append("No text anywhere: no words, letters, numbers, labels, signage or watermarks.")
    pal = con.get("palette") or (", ".join(f"{k} {v}" for k, v in list((brand or {}).get("colors", {}).items())[:5])
                                 if brand else "")
    if pal:
        if sheet:  # the swatches are in the sheet: codes in the text only invite printed labels
            pal = re.sub(r"\s*\(?#[0-9a-fA-F]{3,8}\)?", "", pal)
        L.append(f"Colour: {sent(pal)} Colour names and codes are guidance only: never print them.")
    brand_rows = []
    if logo:
        gx, gy, gw, gh = logo["gen_box"]
        brand_rows.append(f"Leave a plain, empty area at the {where_words(logo['gen_box'])} (x {_pct(gx)}-"
                          f"{_pct(gx + gw)}, y {_pct(gy)}-{_pct(gy + gh)}): calm background with nothing in it, "
                          f"because the client's real logo is added there afterwards. Draw no logo, emblem, monogram "
                          f"or brand name anywhere.")
    else:
        brand_rows.append("Draw no logo, emblem, monogram or brand name.")
    if con.get("brand_device"):
        brand_rows.append(f"Brand device: {sent(con['brand_device'])}")
    L.append("Brand: " + " ".join(brand_rows))
    sf = [sent(x) for x in (con.get("style"), con.get("finish")) if x]
    if sf:
        L.append("Style and finish: " + " ".join(sf) + " Flat colour areas stay clean.")
    st, sr, sb, sl = c["safe_px"]
    sx, sy, sw, sh = frame_box(fr, [sl / fw, st / fh, 1 - (sl + sr) / fw, 1 - (st + sb) / fh])
    buf = 0.025  # measured: type lands ~2-2.5% nearer the edge than asked, so aim inside the true safe area
    safe = [f"every word stays inside x {_pct(sx + buf, True)}-"
            f"{_pct(sx + sw - buf)} and y {_pct(sy + buf, True)}-{_pct(sy + sh - buf)} (the headline shrinks rather "
            f"than cross these margins); the picture itself runs to every edge"]
    for z in c.get("keepout") or []:
        gx, gy, gw, gh = frame_box(fr, [z[0] / fw, z[1] / fh, (z[2] - z[0]) / fw, (z[3] - z[1]) / fh])
        safe.append(f"the {where_words([gx, gy, gw, gh])} area (x {_pct(gx)}-{_pct(gx + gw)}, y {_pct(gy)}-"
                    f"{_pct(gy + gh)}) is calm background with no text or faces, because the platform covers it")
    ox, oy, kx, ky = fr["crop"]
    if kx < 0.995 or ky < 0.995:  # the model makes a wider (or taller) frame than the format: say what gets trimmed
        side, share = ("left and right", 1 - kx) if kx < 0.995 else ("top and bottom", 1 - ky)
        safe.append(f"the final format trims about {_pct(share / 2, True)} off the {side} of this image, so nothing "
                    f"that matters sits in those strips")
    L.append("Safe zones: " + "; ".join(safe) + ".")
    cons = " ".join(str(v) for v in con.values() if isinstance(v, str)).lower()
    own = list(con.get("avoid") or [])
    avoid = [a for a, rx in DIRECT_AVOID if not re.search(rx, cons)][:max(3, 7 - len(own))] + own  # R9: 3-8 items
    L.append("Constraints: one focal point and a clear reading order; aligned edges; no second focal object or extra "
             "props beyond what is described. Do not add: " + "; ".join(a.strip().rstrip(".") for a in avoid) + ".")
    if corrections:
        L.append("Corrections (the last attempt got these wrong; fix them): " + " ".join(corrections))
    return "\n\n".join(x for x in L if x)


LEDGER_KEYS = ("idea", "visual", "medium", "style", "palette", "layout", "typography", "layering")
_STOP = frozenset("a an and are as at be by for from in into is it its of on or over that the this to under with "
                  "while your our their one two three very more most like".split())


def concept_words(con: dict, keys=LEDGER_KEYS) -> set:
    t = " ".join(str(con.get(k) or "") for k in keys).lower()
    return {w for w in re.findall(r"[a-z][a-z-]{2,}", t) if w not in _STOP}


def dhash(path) -> str:
    """64-bit difference hash: near-identical layouts and pictures have a small Hamming distance."""
    Image = need_pillow()
    with Image.open(path) as im:
        g = im.convert("L").resize((9, 8), Image.LANCZOS)
    px = list(g.getdata())
    bits = "".join("1" if px[r * 9 + c] > px[r * 9 + c + 1] else "0" for r in range(8) for c in range(8))
    return f"{int(bits, 2):016x}"


def ledger_entries(p: Path) -> list:
    out = []
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


RECIPE_AXES = ("structure", "archetype", "focal", "device", "type_mode", "palette", "finish")


def _axis(v) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(v or "").lower()).strip()


def ledger_check(dos: dict, entries: list, image: Path | None = None) -> list:
    """No two designs alike (R9 4.4): against the same client's last 6 designs this recipe must differ on at least
    3 of its axes (structure, archetype, focal type, device, type mode, palette roles, finish), and not repeat the
    last design's archetype + focal pair; the concept's words, its style anchor and the finished image must not be
    close to an earlier design either."""
    con = dos.get("concept") or {}
    words, style = concept_words(con), concept_words(con, ("style",))
    h = dhash(image) if image else None
    warn = []
    rec = {k: _axis((dos.get("recipe") or {}).get(k)) for k in RECIPE_AXES}
    mine = [e for e in entries if e.get("id") != dos["id"] and
            (not dos.get("client") or not e.get("client") or e["client"] == dos["client"])]
    if any(rec.values()):
        for e in mine[-6:]:
            er = {k: _axis((e.get("recipe") or {}).get(k)) for k in RECIPE_AXES}
            diff = sum(1 for k in RECIPE_AXES if rec[k] and er[k] and rec[k] != er[k]) + \
                sum(1 for k in RECIPE_AXES if bool(rec[k]) != bool(er[k]))
            if diff < 3:
                warn.append(f"the recipe differs from '{e['id']}' on only {diff} axes (need 3 of: "
                            f"{', '.join(RECIPE_AXES)})")
        if mine:
            last = {k: _axis((mine[-1].get("recipe") or {}).get(k)) for k in ("archetype", "focal")}
            if rec["archetype"] and rec["focal"] and (rec["archetype"], rec["focal"]) == (last["archetype"], last["focal"]):
                warn.append(f"the same archetype and focal type as the last design '{mine[-1]['id']}'")
    elif not dos.get("recipe"):
        warn.append("no recipe in the dossier: name structure, archetype, focal, device, type_mode, palette and "
                    "finish so the ledger can keep every design different")
    for e in entries:
        if e.get("id") == dos["id"] or dos.get("client") and e.get("client") and e["client"] != dos["client"]:
            continue
        ew = set(e.get("words") or [])
        j = len(words & ew) / max(1, len(words | ew))
        if j >= 0.4:
            warn.append(f"concept close to '{e['id']}' ({j:.0%} of its idea, style and layout words are shared): "
                        f"change the idea, not just the wording")
        es = set(e.get("style_words") or [])
        if style and es and len(style & es) / max(1, len(style | es)) >= 0.6:
            warn.append(f"the same style anchor as '{e['id']}'")
        if h and e.get("dhash"):
            dist = bin(int(h, 16) ^ int(e["dhash"], 16)).count("1")
            if dist <= 10:
                warn.append(f"the finished image looks like '{e['id']}' (difference hash {dist}/64 apart)")
    return warn


def ledger_add(p: Path, dos: dict, image: Path, extra: dict) -> None:
    con = dos.get("concept") or {}
    entry = {"id": dos["id"], "client": dos.get("client"), "date": time.strftime("%Y-%m-%d"),
             "deliverable": dos.get("deliverable"), "preset": dos.get("preset"),
             **{k: con.get(k) for k in ("idea", "medium", "style", "palette", "layout")},
             "recipe": dos.get("recipe"), "words": sorted(concept_words(con)),
             "style_words": sorted(concept_words(con, ("style",))), "dhash": dhash(image), "image": str(image), **extra}
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def load_dossier(path: Path) -> dict:
    """The design dossier (the spec): brief, verified facts, the chosen concept, the frozen copy, zones, references
    and logo placement. It is the one source for the prompt, the verifier and the repairs."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read the dossier {path}: {e}")
    need = [k for k in ("deliverable",) if not d.get(k)] + ([] if d.get("preset") or d.get("size") else ["preset"])
    con = d.get("concept") or {}
    need += [f"concept.{k}" for k in ("idea", "visual") if not con.get(k)]
    if need:
        die("the dossier needs: " + ", ".join(need))
    copy = []
    for x in d.get("copy") or []:
        x = {"text": x} if isinstance(x, str) else dict(x)
        if str(x.get("text", "")).strip():
            copy.append(dict({"role": "text", "must_exact": True}, **x))
    labels = {str(z[0]).lower(): z for z in d.get("zones") or []}
    for s in copy:
        if s.get("lines") and norm_text(" ".join(s["lines"])) != norm_text(s["text"]):
            die(f"copy '{s['text']}': its lines {s['lines']} do not join back to the text")
        if s.get("route") == "typeset" and not s.get("zone"):
            z = labels.get(str(s.get("role") or "").lower())
            if not z:
                die(f"copy '{s['text'][:30]}' is typeset: give it a \"zone\": [x%, y%, w%, h%] (or a zones entry "
                    f"labelled '{s.get('role')}')")
            s["zone"] = [float(v) for v in z[1:5]]
    d["copy"] = copy
    d.setdefault("id", re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-") or "design")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,80}", d["id"]):
        die(f"dossier id {d['id']!r}: letters, digits, dot, dash and underscore only")
    d["_base"] = str(path.parent)
    return d


def _to_master(src: Path, ratio: float, anchor: str, out: Path) -> tuple:
    """The generated image cropped to the final aspect at full resolution (the master every later step works on).
    When the aspects differ, the window slides to where the text is (read by OCR) instead of blindly centring, so a
    headline set near the edge is not cut. Returns (path, info) with info["cut_text"] when no window can hold all of
    the text and the side where it runs out."""
    Image = need_pillow()
    with Image.open(src) as im0:
        im = im0.convert("RGB")
    W, H = im.size
    x, y, w, h = fit_crop(W / H, ratio, anchor)
    info = {"window": None, "cut_text": False}
    if abs(w - 1) > 1e-3 or abs(h - 1) > 1e-3:
        ocr = ocr_lines(src) or {"lines": []}
        horiz = abs(w - 1) > 1e-3
        spans = [((l_["box"][0], l_["box"][0] + l_["box"][2]) if horiz else (l_["box"][1], l_["box"][1] + l_["box"][3]))
                 for l_ in ocr["lines"] if len(_bare(l_["text"])) > 1]
        if spans:
            size = W if horiz else H
            t0 = max(0.0, min(a for a, _ in spans) / size)  # recognition boxes can poke past the image edge
            t1 = min(1.0, max(b for _, b in spans) / size)
            k = w if horiz else h
            lo, hi = max(0.0, t1 - k), min(1 - k, t0)  # window starts that hold every word
            base = x if horiz else y
            if lo <= hi + 1e-6:
                hi = max(hi, lo)
                pos = base if lo <= base <= hi and min(t0 - base, base + k - t1) >= 0.04 else (lo + hi) / 2
                info_v = vision("analyze", src) or {}  # then keep the main objects whole too, where the text allows
                objs = [o["box"] for o in info_v.get("objects") or [] if o.get("confidence", 0) > 0.3]
                if objs:
                    o0 = max(0.0, min((b[0] if horiz else b[1]) for b in objs) / size)
                    o1 = min(1.0, max((b[0] + b[2] if horiz else b[1] + b[3]) for b in objs) / size)
                    olo, ohi = max(lo, o1 - k), min(hi, o0)
                    if olo <= ohi:
                        pos = (olo + ohi) / 2
                        info["object_span"] = [round(o0 * 100, 1), round(o1 * 100, 1)]
            else:
                pos = min(max((t0 + t1 - k) / 2, 0.0), 1 - k)
                info["cut_text"] = "left and right" if horiz else "top and bottom"
            x, y = (pos, y) if horiz else (x, pos)
            info["text_span"] = [round(t0 * 100, 1), round(t1 * 100, 1)]
    box = (round(x * W), round(y * H), round((x + w) * W), round((y + h) * H))
    info["window"] = list(box)
    im = im.crop(box)
    im.save(out, icc_profile=srgb_icc() or None)
    return out, info


READ_PROMPT = ("Transcribe exactly the text visible in this image, line by line, character by character, in its own "
               "script, and spell every line letter by letter with hyphens between letters and spaces between words "
               "(for example C-a-f-e O-p-e-n). Do not correct spelling, do not guess hidden letters, do not translate, "
               "do not add anything. Write an unclear character as ?.")


def blind_read(img: Path, timeout: int = 300) -> list | None:
    """A second reader from another model family than Apple Vision (Codex vision), given only the pixels: no copy,
    no brief, so it cannot see what the text is supposed to say (R11: blind transcription). It also spells each line
    letter by letter, which makes it look at the glyphs instead of guessing the word. Returns the spelled lines,
    joined back into words."""
    ci = _imagegen()
    if ci is None:
        return None
    tmp = Path(tmp_dir("read-"))
    schema, last = tmp / "schema.json", tmp / "read.json"
    schema.write_text(json.dumps({"type": "object", "properties": {
        "lines": {"type": "array", "items": {"type": "string"}},
        "spelled": {"type": "array", "items": {"type": "string"}}}, "required": ["lines", "spelled"],
        "additionalProperties": False}), encoding="utf-8")
    cmd = [ci.codex_bin(), "exec", "-i", str(img), "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "--json",
           "-c", 'model_reasoning_effort="low"', "--output-schema", str(schema), "-o", str(last)] + ci.LEAN_FLAGS + ["-"]
    try:
        run_session(cmd, READ_PROMPT, timeout, env=ci.codex_env())
        data = json.loads(last.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    spelled = [" ".join(w.replace("-", "") for w in line.split(" ")) for line in data.get("spelled") or []]
    return spelled or data.get("lines")


def blind_reads(paths: list) -> list:
    """blind_read on several images side by side (up to 3 sessions at once), in the order given. The second reads of
    one candidate used to run one after another, each up to its timeout."""
    import concurrent.futures as cf
    if len(paths) <= 1:
        return [blind_read(p) for p in paths]
    _imagegen()  # load codex-imagegen once, before the threads
    with cf.ThreadPoolExecutor(max_workers=min(3, len(paths))) as ex:
        return list(ex.map(blind_read, paths))


def resolve_ambiguous(src: Path, rep: dict) -> dict:
    """Settle the strings Apple Vision may have misread: 'ambiguous' ones (a second Vision reading spells them right)
    and 'altered' ones within a letter or two of the approved text (display glyphs such as a soft-serif f read as t).
    A blind second reader looks at a close-up crop: if it reads the approved text, the string passes with a warning
    kept for the human check; if not, it is an 'altered' error. The reads run side by side. Returns the updated
    report."""
    import difflib
    Image = need_pillow()
    todo = [r for r in rep.get("copy", []) if not r.get("allowed") and (r["status"] == "ambiguous" or (
        r["status"] == "altered" and difflib.SequenceMatcher(None, norm_text(r["text"]).casefold(),
                                                            norm_text(r.get("read", "")).casefold()).ratio() >= 0.85))]
    rest = [r for r in rep.get("copy", []) if not r.get("allowed") and r["status"] in ("missing", "altered")
            and r not in todo]
    crops = []  # (string, close-up crop) for every string with boxes, read together with the whole image below
    if todo:
        with Image.open(src) as im0:
            im = im0.convert("RGB")
        for r in todo:
            bs = r.get("boxes") or []
            if not bs:
                continue
            x0, y0 = min(b[0] for b in bs), min(b[1] for b in bs)
            x1, y1 = max(b[0] + b[2] for b in bs), max(b[1] + b[3] for b in bs)
            m = 0.25 * (y1 - y0)
            crop = im.crop((max(0, round(x0 - m)), max(0, round(y0 - m)), min(im.width, round(x1 + m)),
                            min(im.height, round(y1 + m))))
            k = max(1.0, 900 / max(crop.size))
            crop = crop.resize((round(crop.width * k), round(crop.height * k)), Image.LANCZOS)
            cp = Path(tmp_dir("amb-")) / "crop.png"
            crop.save(cp)
            crops.append((r, cp))
    reads = blind_reads(([src] if rest else []) + [cp for _, cp in crops])
    if rest:  # Vision could not find these at all (giant, condensed or stylised display type): one whole-image read
        lines = reads.pop(0)
        got = [_bare(t) for t in _tokens(" ".join(lines or [])) if _bare(t)]
        for r in rest:
            want = [_bare(t) for t in _tokens(r["text"]) if _bare(t)]
            ok = bool(lines) and bool(want) and any(got[i:i + len(want)] == want
                                                    for i in range(len(got) - len(want) + 1))
            r["second_reader"] = {"read": " ".join(lines or [])[:300], "agrees": ok, "whole_image": True}
            if ok:
                rep["errors"] = [e for e in rep["errors"] if not e.startswith((f"approved copy altered: '{r['text']}'",
                                                                               f"approved copy missing: '{r['text']}'"))]
                rep["warnings"].append(f"'{r['text']}': Apple Vision could not read it (display type); a blind second "
                                       f"reader finds it exactly on the whole image (look at it once)")
                r["status"] = "confirmed"
        rep["ok"] = not rep["errors"]
    if not todo:
        return rep
    for (r, _), lines in zip(crops, reads):
        read = " ".join(lines or [])
        want = [_bare(t) for t in _tokens(r["text"]) if _bare(t)]
        got = [_bare(t) for t in _tokens(read) if _bare(t)]
        ok = bool(lines) and bool(want) and any(got[i:i + len(want)] == want for i in range(len(got) - len(want) + 1))
        r["second_reader"] = {"read": read, "agrees": ok}
        rep["warnings"] = [w for w in rep["warnings"] if not w.startswith(f"OCR is unsure: '{r['text']}'")]
        rep["errors"] = [e for e in rep["errors"] if not e.startswith(f"approved copy altered: '{r['text']}'")]
        if ok:
            r["status"] = "confirmed"
            rep["warnings"].append(f"'{r['text']}': Apple Vision read '{r['read']}', a blind second reader reads the "
                                   f"approved text (a display glyph; look at it once)")
        else:
            r["status"] = "altered"
            rep["errors"].append(f"approved copy altered: '{r['text']}' reads '{r['read']}' (second reader: "
                                 f"'{read or 'no answer'}')")
    rep["ok"] = not rep["errors"]
    return rep


def _rank(rep: dict) -> tuple:
    hard = sum(1 for e in rep["errors"] if "missing" in e or "altered" in e)
    return hard, len(rep["errors"]), len(rep["warnings"])


def direct_repair(path: Path, rep: dict, copy: list, allow: list, preset: str | None, args, work: Path) -> tuple:
    """Bounded repair rounds on the best candidate (R11: at most 3 regions a round, stop when a round gains
    nothing): words nobody approved are removed and the background rebuilt; altered strings are corrected in a
    close-up crop; approved words are protected. Missing text cannot be placed reliably by a region edit, so it is
    left to a regeneration."""
    history, best_path, best_rep = [], path, rep
    for rnd in range(1, args.repair_rounds + 1):
        if best_rep["ok"]:
            break
        good = []
        for r in best_rep["copy"]:
            if r["status"] not in ("missing", "altered"):
                good += [[b[0] - 3, b[1] - 3, b[0] + b[2] + 3, b[1] + b[3] + 3] for b in r.get("boxes", [])]
        jobs = []
        rm = [e for e in best_rep["extra"] if len(_bare(e["text"])) > 1 or re.search(r"\d", e["text"])]
        if rm:
            jobs.append(("remove", [[e["box"][0], e["box"][1], e["box"][0] + e["box"][2], e["box"][1] + e["box"][3]]
                                    for e in rm],
                         "remove every word, letter and number, and rebuild what was behind them: continue the "
                         "surrounding background, surfaces, texture, light and shadow seamlessly, as if the text had "
                         "never been there.", "auto", 0.5))
        with need_pillow().open(best_path) as im_:
            IW, IH = im_.size
        for r in [r for r in best_rep["copy"] if r["status"] == "altered" and not r.get("allowed")][:2]:
            bs = r.get("boxes") or []
            if not bs:
                continue
            if any(b[0] < 0.01 * IW or b[1] < 0.01 * IH or b[0] + b[2] > 0.99 * IW or b[1] + b[3] > 0.99 * IH
                   for b in bs):
                history.append({"round": rnd, "note": f"'{r['text']}' runs into the frame edge: a region edit would "
                                                      f"only repaint it there, so it is left to a regeneration"})
                continue
            box = [min(b[0] for b in bs), min(b[1] for b in bs), max(b[0] + b[2] for b in bs),
                   max(b[1] + b[3] for b in bs)]
            jobs.append(("correct", [box], f'the text must read exactly "{r["text"]}": the same spelling, '
                                           f'capitalisation and punctuation, in the same typeface, weight, size, colour, '
                                           f'alignment and position as the text there now. Correct only the wrong '
                                           f'letters.', "crop", 0.35))
        if not jobs:
            history.append({"round": rnd, "note": "only missing text is left: a region edit cannot place it"})
            break
        cur = best_path
        for kind, boxes, instr, mode, pad in jobs[:3]:
            prot = [g for g in good if not any(min(g[2], b[2]) > max(g[0], b[0]) and min(g[3], b[3]) > max(g[1], b[1])
                                               for b in boxes)] if kind == "correct" else good
            try:
                res = patch_image(cur, boxes, instr, prot, pad=pad, mode=mode, engine=args.engine_used,
                                  model=args.model, quality=args.quality, out=work / f"repair-r{rnd}-{kind}.png",
                                  timeout=args.timeout)
            except (RunFailed, SystemExit) as e:  # one failed edit fails this repair, not the whole run
                history.append({"round": rnd, "kind": kind, "error": f"edit failed ({e})"})
                continue
            history.append({"round": rnd, "kind": kind, "instruction": instr,
                            **{k: res.get(k) for k in ("mode", "boxes", "window", "patched", "alignment",
                                                       "change_inside", "outside_changed_px", "text_now_in_boxes",
                                                       "pointer_colour", "annotation_leak", "seconds")}})
            if res.get("annotation_leak"):
                history[-1]["note"] = "the pointer colour leaked into the edit: not used"
                continue
            cur = Path(res["patched"])
        if cur == best_path:
            break
        new = resolve_ambiguous(cur, verify_image(cur, copy, allow, preset))
        history.append({"round": rnd, "errors_after": new["errors"]})
        if _rank(new) < _rank(best_rep):
            best_path, best_rep = cur, new
        else:
            history.append({"round": rnd, "note": "no gain: stopped"})
            break
    return best_path, best_rep, history


def direct_brief(dos: dict) -> str:
    """The dossier as a plain brief for the judge (facts included, so the judge does not guess them)."""
    con = dos.get("concept") or {}
    rows = [f"Deliverable: {dos['deliverable']}", f"Canvas: {dos.get('preset') or dos.get('size')}"]
    rows += [f"{k.capitalize()}: {dos[k]}" for k in ("client", "audience", "place", "language", "goal") if dos.get(k)]
    rows += [f"Concept {k}: {con[k]}" for k in LEDGER_KEYS if con.get(k)]
    facts = [f"- {f.get('claim') or f.get('text')}: {f.get('value', '')} ({f.get('status', 'unverified')})"
             for f in dos.get("facts") or []]
    if facts:
        rows += ["Verified facts:"] + facts
    lg = dos.get("logo", "auto")
    if lg in (None, False, "none"):
        rows.append("No logo on this piece, by the brief's choice" + (
            " (YouTube shows the channel's name and avatar beside every thumbnail)" if "thumbnail" in
            str(dos.get("kind") or dos.get("deliverable") or "").lower() else "") + ": do not ask for one.")
    else:
        rows.append("The logo is the client's real file, composited after generation into the space the design "
                    "leaves for it.")
    return "\n".join(rows)


def cmd_direct(args) -> None:
    """One dossier -> one compiled prompt with its reference images -> K candidates -> OCR verification -> bounded
    region repairs -> the real logo composited -> final verification (-> judge) -> the finished file, a master and a
    report. Designs beyond 3:1, and ones that still fail after the repairs and retries, go to the composed route
    (exit code 3 or 4, with a text-free plate of the best attempt for it)."""
    Image = need_pillow()
    import hashlib
    import io
    t_start = time.time()
    dp = Path(args.dossier).expanduser().resolve()
    dos = load_dossier(dp)
    base = Path(dos["_base"])
    c = resolve_canvas(dos.get("preset"), dos.get("size"))
    ci = _imagegen()
    engine = args.engine or dos.get("engine") or "auto"
    if engine == "auto":
        engine = "api" if ci is not None and ci.get_api_key() else "codex"
    args.engine_used = engine
    anchor = dos.get("crop_anchor", "center")
    fr = direct_frame(c, engine, anchor)
    if not fr["possible"]:
        print(json.dumps({"route": "compose", "reason": f"{c.get('id')} is {fr['ratio']}:1, beyond the 1:3-3:1 range "
                          f"one generated image can have: render it as HTML with an AI plate (design.py render)"},
                         indent=2))
        sys.exit(3)
    facts = dos.get("facts") or []
    blockers = [f for f in facts if f.get("status") in ("refuted", "needs_client")]
    if blockers and not args.force:
        die("facts block this design (fix the copy or get the client's answer first): " +
            "; ".join(f"{f.get('claim') or f.get('text')} = {f.get('status')}" for f in blockers))
    dcopy = [{"role": x.get("role", ""), "text": x["text"], "lang": x.get("lang", "")}
             for x in dos.get("copy") or [] if isinstance(x, dict) and isinstance(x.get("text"), str)]
    if dcopy:  # the copy goes into pixels: an em dash or a bookish word there costs a whole generation to remove
        lint = copyrules.lint_deck(dcopy, norm_locale(dos.get("locale")), check_platform(dos.get("platform") or ""))
        bad = [f"{it['role'] or 'text'} '{it['text'][:40]}': {f['message']}" for it in lint["items"]
               for f in it["findings"] if f["severity"] == "error"] + \
            [f["message"] for f in lint["deck"] if f["severity"] == "error"]
        if bad and not args.force:
            die("the dossier's copy fails the copy lint; fix it before generating: " + "; ".join(bad[:5]), 2)
    run = Path(args.out_dir).expanduser().resolve() if args.out_dir else base / "direct" / dos["id"]
    (run / "refs").mkdir(parents=True, exist_ok=True)
    lock = run / ".direct.lock"
    if not args.plan:
        for _ in range(2):  # atomic create; a lock left by a run that died is taken over once
            try:
                fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                break
            except FileExistsError:
                try:
                    other = int(lock.read_text().strip() or "0")
                    os.kill(other, 0)  # still running: two runs in one folder would mix their candidates
                except (OSError, ValueError):
                    lock.unlink(missing_ok=True)  # stale
                    continue
                die(f"another direct run (pid {other}) is using {run}; wait for it, give --out-dir, or delete "
                    f"{lock.name} if no run is active")
        atexit.register(lambda: lock.unlink() if lock.exists() and lock.read_text().strip() == str(os.getpid())
                        else None)
    args.stamp = time.strftime("%H%M%S")  # every run's files get their own names: no stale candidate is picked up
    brand, bdir, bj = None, None, None
    if dos.get("brand"):
        bj = (base / dos["brand"]).resolve()
        if not bj.exists():
            die(f"brand file not found: {bj}")
        brand, bdir = json.loads(bj.read_text(encoding="utf-8")), bj.parent
    refs = []
    for r in dos.get("references") or []:
        pth = (base / r["path"]).resolve()
        if not pth.exists():
            die(f"reference not found: {pth}")
        role = r.get("role", "photo")
        if role == "person" and not r.get("consent"):
            die(f"{pth.name}: a person reference needs the client's consent to use that person's likeness "
                f"(set \"consent\": true on it in the dossier)")
        text = REF_ROLES.get(role, REF_ROLES["photo"]).rstrip(".") + "." + (f" {r['use'].strip()}" if r.get("use") else "")
        refs.append((pth, role, text))
    if brand and dos.get("brand_sheet", True):
        sheet = run / "refs" / "brand-sheet.png"
        if args.refresh or not sheet.exists():
            make_refsheet(bj, None, sheet, model=True)
        refs.append((sheet, "brand", REF_ROLES["brand"] + "."))
    logo = plan_logo(dos, c, fr, brand, bdir)
    ts_roles = {str(x.get("role") or "").lower() for x in dos["copy"] if x.get("route") == "typeset"}
    zones_all = [(["reserved"] + list(z[1:5]) if str(z[0]).lower() in ts_roles else list(z)) for z in dos.get("zones") or []]
    zones_all += [["reserved", *x["zone"]] for x in dos["copy"] if x.get("route") == "typeset" and
                  str(x.get("role") or "").lower() not in {str(z[0]).lower() for z in dos.get("zones") or []}]
    if zones_all:
        gz = [[z[0], *frame_box(fr, [float(v) / 100 for v in z[1:5]])] + list(z[5:6]) for z in zones_all]
        if logo and not any(zone_kind(z[0]) == "logo" for z in gz):
            gz.append(["logo", *logo["gen_box"]])
        long_side = 1024
        gw = long_side if fr["gen_ratio"] >= 1 else round(long_side * fr["gen_ratio"])
        gh = round(gw / fr["gen_ratio"])
        wire = draw_wireframe(gz, gw, gh, run / "refs" / "wireframe.png")
        refs.append((wire, "layout", REF_ROLES["layout"] + "."))
    order = ["product", "person", "place", "photo", "texture", "layout", "style", "brand"]
    refs.sort(key=lambda r: order.index(r[1]) if r[1] in order else len(order))  # fidelity-critical first (R8 3.6)
    if len(refs) > DIRECT_REF_LIMIT[engine]:
        die(f"{len(refs)} reference images; the {engine} engine takes at most {DIRECT_REF_LIMIT[engine]}: drop a style "
            f"reference, or set \"brand_sheet\": false and describe the palette in words")
    copy = [x for x in dos["copy"] if x.get("route") != "typeset"]  # what the image model has to draw
    typeset = [x for x in dos["copy"] if x.get("route") == "typeset"]  # what HTML sets over its result
    if typeset and not (bj and bj.with_name("brand.css").exists()):
        die("typeset copy needs the brand's fonts: give the dossier a brand and run `design.py brand --json` for it")
    allow_gen = list(dos.get("allow") or [])
    allow_final = list(dict.fromkeys(allow_gen + (brand_names(brand) if brand else [])))
    budget = text_budget(copy)
    lp = Path(args.ledger).expanduser() if args.ledger else base / "ledger.jsonl"
    entries = ledger_entries(lp)
    similar = ledger_check(dos, entries)
    prompt = direct_prompt(dos, c, fr, refs, logo, brand)
    (run / "prompt.txt").write_text(prompt, encoding="utf-8")
    (run / "copy.json").write_text(json.dumps(dos["copy"], indent=2, ensure_ascii=False), encoding="utf-8")
    (run / "brief.md").write_text(direct_brief(dos), encoding="utf-8")
    notes = []
    if not dos.get("proof"):
        notes.append("no proof slot: name the real thing this design shows (the client's photo, a named person, a "
                     "sourced number, a handmade mark); without it the design reads as generic (R10 3.5)")
    floor_pct = float(c.get("min_text_px") or 0) * 1.2 / c["h_px"] * 100
    for s_ in dos["copy"]:
        m_ = re.search(r"([\d.]+)\s*%\s*of the (?:image )?height", str(s_.get("size") or ""))
        if m_ and floor_pct and float(m_.group(1)) < floor_pct - 0.05:
            notes.append(f"'{s_['text'][:30]}' is asked at {m_.group(1)}% of the height, below the readable floor of "
                         f"{floor_pct:.1f}% for {c.get('id')} at its viewing size: raise it")
    for s_ in dos["copy"]:
        if s_.get("route") == "typeset":
            fl = float(c.get("min_text_px") or 12)
            need = max(len(t) for t in (s_.get("lines") or [s_["text"]])) * 0.6 * fl
            rows_ = 1 if s_.get("lines") else max(1, int(float(s_["zone"][3]) / 100 * c["h_px"] / (fl * 1.3)))
            have = float(s_["zone"][2]) / 100 * c["w_px"] * rows_
            if need > have * 1.05:
                notes.append(f"typeset '{s_['text'][:30]}' needs about {need / c['w_px'] * 100:.0f}% of the width at the "
                             f"readable size; its zone is {s_['zone'][2]}%: widen it, give it lines, or it will be "
                             f"widened towards its free side")
    trust = re.search(r"dental|dentist|clinic|medical|health|doctor|finance|bank|insur|legal|law firm|real estate|"
                      r"property|b2b|saas", " ".join(str(dos.get(k) or "") for k in ("deliverable", "client",
                                                                                     "industry")), re.I)
    scene_txt = " ".join(str((dos.get("concept") or {}).get(k) or "") for k in ("visual", "medium"))
    if trust and ci is not None and ci.PHOTO_MEDIUM.search(scene_txt) and ci.has_people(scene_txt) and \
            not any(r[1] == "person" for r in refs):
        notes.append("trust sector with photoreal people the model would invent: use the client's real people "
                     "(a person reference with consent) or an illustrated picture (R10 3.5)")
    st_, sr_, sb_, sl_ = c["safe_px"]
    gx_, gy_, gw_, gh_ = frame_box(fr, [sl_ / c["w_px"], st_ / c["h_px"], 1 - (sl_ + sr_) / c["w_px"],
                                        1 - (st_ + sb_) / c["h_px"]])
    plan_safe = {"x": [round((gx_ + 0.025) * 100, 1), round((gx_ + gw_ - 0.025) * 100, 1)],
                 "y": [round((gy_ + 0.025) * 100, 1), round((gy_ + gh_ - 0.025) * 100, 1)],
                 "note": "the prompt asks for text inside this box (the true safe area less 2.5%, since the model sets "
                         "type nearer the edge than asked); align the layout axis and zones with it"}
    plan = {"id": dos["id"], "engine": engine, "safe_area_pct": plan_safe, "model": args.model if engine == "api" else "gpt-image-2 (Codex tool)",
            "quality": args.quality if engine == "api" else "auto", "preset": c.get("id"), "frame": fr,
            "references": [{"image": i, "path": str(p), "role": role} for i, (p, role, _) in enumerate(refs, 1)],
            "logo": logo, "text_budget": budget, "typeset": [x["text"] for x in typeset],
            "similar_to_earlier": similar, "notes": notes,
            "estimated_facts": [f.get("claim") or f.get("text") for f in facts if f.get("status") == "estimated"],
            "prompt_file": str(run / "prompt.txt"), "prompt_chars": len(prompt),
            "prompt_sha1": hashlib.sha1(prompt.encode()).hexdigest()[:12]}
    (run / "plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.plan:
        print(json.dumps(dict(plan, prompt=prompt), indent=2, ensure_ascii=False))
        return
    if args.retypeset:  # the client changed small print (hours, price, address): set it again, keep the picture
        pic = run / f"{dos['id']}-picture.png"
        if not pic.exists():
            die(f"no kept picture at {pic}: --retypeset needs a finished run whose copy had typeset entries")
        if not typeset:
            die("the dossier has no typeset copy to set")
        final_out = Path(args.out).expanduser().resolve() if args.out else run / f"{dos['id']}.png"
        master_out = final_out.with_name(final_out.stem + "-master.png") if args.out else run / f"{dos['id']}-master.png"
        tr = typeset_overlay(pic, typeset, c, brand, bj, final_out, master_out)
        vr = verify_image(final_out, dos["copy"], allow_final, c.get("id"))
        vr = resolve_ambiguous(final_out, vr)
        print(json.dumps({"id": dos["id"], "route": "direct (retypeset)", "final": str(final_out),
                          "errors": vr["errors"] + [f"typeset: {e}" for e in tr["errors"]],
                          "warnings": vr["warnings"] + [f"typeset: {w}" for w in tr["warnings"]]},
                         indent=2, ensure_ascii=False))
        return
    blocking = [w for w in similar if not w.startswith("no recipe")]
    if blocking and not args.force:
        die("this concept repeats an earlier design (" + "; ".join(blocking) + "); change the idea, or pass --force")
    ctx = {"dos": dos, "c": c, "fr": fr, "refs": refs, "logo": logo, "brand": brand, "engine": engine, "run": run,
           "anchor": anchor, "copy": copy, "copy_all": dos["copy"], "typeset": typeset, "bj": bj,
           "allow_gen": allow_gen, "allow_final": allow_final}
    report = {"id": dos["id"], "dossier": str(dp), "plan": plan, "rounds": []}
    first = direct_round(ctx, args, 1, [])
    report["rounds"].append(first["record"])
    if not first.get("ok"):
        report.update(route="compose", reason=first["reason"])
        if not args.no_plate and first.get("fixed"):  # the attempt's composition without its text, for composing
            ocr = first["rep"]["ocr_lines"]
            boxes = [[l_["box"][0], l_["box"][1], l_["box"][0] + l_["box"][2], l_["box"][1] + l_["box"][3]] for l_ in ocr]
            if boxes:
                try:
                    pr = patch_image(first["fixed"], boxes, "remove every word, letter and number, and rebuild what was "
                                     "behind them seamlessly: continue the background, surfaces, texture, light and "
                                     "shadow.", None, mode="full", engine=engine, model=args.model,
                                     quality=args.quality, out=run / f"{dos['id']}-plate.png", timeout=args.timeout)
                    report["plate"] = pr["patched"]
                except (RunFailed, SystemExit) as e:
                    report["plate_error"] = str(e)
        rp = run / f"{dos['id']}.direct.json"
        rp.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps({"id": dos["id"], "route": "compose", "reason": report["reason"], "plate": report.get("plate"),
                          "best_attempt": str(first.get("fixed")), "report": str(rp)}, indent=2, ensure_ascii=False))
        sys.exit(4)
    best = first
    if args.judge:
        best["judge"] = direct_judge(best["final"], ctx, args)
        report["rounds"][-1]["judge"] = best["judge"]
        for n in range(2, 2 + max(0, args.revise)):
            j = best["judge"] or {}
            if j.get("verdict") not in ("REVISE", "FAIL") or not (j.get("fixes") or j.get("findings")):
                break
            skip = re.compile(r"\blogo|wordmark|brand ?mark|monogram|emblem|watermark", re.I)
            notes = [f.strip().rstrip(".") + "." for f in (j.get("fixes") or []) if not skip.search(f)][:5] or \
                [str(f.get("after", "")).strip() for f in (j.get("findings") or [])[:3] if not skip.search(
                    str(f.get("after", "")) + str(f.get("element", "")))]
            if not notes:
                break  # what is left is ours to fix (the logo is composited, never drawn): no regeneration
            log(f"direct: the judge says {j.get('verdict')} ({j.get('weighted')}): revision round {n} with its notes")
            nxt = direct_round(ctx, args, n, ["Art director's notes on the last version (keep its idea, copy and "
                                               "look; change only this, and add no logo, text or element the brief "
                                               "does not name): " + " ".join(notes)], tries=1)
            report["rounds"].append(nxt["record"])
            if not nxt.get("ok"):
                continue
            nxt["judge"] = direct_judge(nxt["final"], ctx, args)
            report["rounds"][-1]["judge"] = nxt["judge"]
            order = {"PASS_SENIOR": 3, "PASS": 2, "REVISE": 1, "FAIL": 0}
            key = lambda r: (order.get((r["judge"] or {}).get("verdict"), 0), (r["judge"] or {}).get("weighted") or 0)
            if key(nxt) > key(best):
                best = nxt
    final_out = Path(args.out).expanduser().resolve() if args.out else run / f"{dos['id']}{best['final'].suffix}"
    master_out = run / f"{dos['id']}-master.png"
    if best["final"] != final_out:
        shutil.copy2(best["final"], final_out)
    shutil.copy2(best["master"], master_out)
    if best.get("picture"):
        shutil.copy2(best["picture"], run / f"{dos['id']}-picture.png")
    report.update(route="direct", final=str(final_out), master=str(master_out), chosen_round=best["round"],
                  verify=best["final_rep"]["errors"], warnings=best["final_rep"]["warnings"] +
                  (best.get("logo_rep") or {}).get("warnings", []), logo=best.get("logo_rep"), judge=best.get("judge"),
                  effective_ppi=round(best["width"] / (c["w_px"] / 96), 1) if c["print"] else None)
    report["similar_to_earlier"] = ledger_check(dos, entries, best["master"])
    ledger_add(lp, dos, best["master"], {"engine": engine, "prompt_sha1": plan["prompt_sha1"], "route": "direct",
                                         "final": str(final_out)})
    report["seconds"] = round(time.time() - t_start, 1)
    rp = run / f"{dos['id']}.direct.json"
    rp.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    j = best.get("judge") or {}
    print(json.dumps({"id": dos["id"], "route": "direct", "final": str(final_out), "master": str(master_out),
                      "errors": best["final_rep"]["errors"], "warnings": report["warnings"],
                      "judge": j.get("verdict"), "judge_score": j.get("weighted"), "rounds": len(report["rounds"]),
                      "chosen_round": best["round"], "seconds": report["seconds"], "report": str(rp)},
                     indent=2, ensure_ascii=False))


def direct_round(ctx: dict, args, n: int, notes: list, tries: int | None = None) -> dict:
    """One round: up to `tries` attempts of K candidates (a retry carries the last attempt's text mistakes), the best
    candidate by verification, bounded repairs, then the real logo and the final files for this round."""
    import io
    Image = need_pillow()
    dos, c, fr, refs, run = ctx["dos"], ctx["c"], ctx["fr"], ctx["refs"], ctx["run"]
    attempts, corrections, best = [], [], None
    for attempt in range(1, (tries or args.tries) + 1):
        tag = f"{getattr(args, 'stamp', 'run')}-r{n}a{attempt}"
        ptext = direct_prompt(dos, c, fr, refs, ctx["logo"], ctx["brand"], notes + corrections)
        pfile = run / f"prompt-{tag}.txt"
        pfile.write_text(ptext, encoding="utf-8")
        gen = run / f"gen-{tag}"
        gen.mkdir(exist_ok=True)
        cmd = [sys.executable, str(IMAGEGEN), "generate", "--prompt-file", str(pfile), "--out-dir", str(gen),
               "--name", "cand", "--workdir", str(gen), "--look", "none", "--finish", "none", "--no-judge",
               "--raw-prompt", "--n", str(args.variants), "--timeout", str(args.timeout)]
        for p_, role, _ in refs:
            cmd += ["--ref", f"{p_}={role}"]
        if ctx["engine"] == "codex":
            cmd += ["--aspect", fr["aspect"], "--mode", "fast", "--prompt-writer", "compiled", "--no-auto-candidates",
                    "--log-dir", str(gen / "logs")]
        else:
            cmd += ["--engine", "api", "--model", args.model, "--quality", args.quality, "--api-size", fr["api_size"]]
        log(f"direct: round {n}, attempt {attempt}: {args.variants} candidate(s) on the {ctx['engine']} engine")
        t0 = time.time()
        r = run_session(cmd, None, child_budget(args.timeout))  # --timeout per session; codex-imagegen retries once
        outs = sorted(q for q in gen.glob("cand*.png") if not q.stem.endswith(("-raw", "-first")))
        rec = {"attempt": tag, "seconds": round(time.time() - t0, 1), "prompt": str(pfile), "candidates": []}
        if not outs:  # a failed or timed-out attempt costs this attempt, not the run
            rec["error"] = r["error"] or (r["stdout"] + r["stderr"])[-800:]
            attempts.append(rec)
            continue
        cut = False
        for q in outs:
            m, crop_info = _to_master(q, fr["ratio"], ctx["anchor"], run / f"{tag}-{q.stem}.png")
            rep = resolve_ambiguous(m, verify_image(m, ctx["copy"], ctx["allow_gen"], c.get("id")))
            if crop_info.get("cut_text"):
                cut = True
                rep["errors"].append(f"the text runs past the final format's {crop_info['cut_text']} edges "
                                     f"(text spans {crop_info['text_span'][0]}-{crop_info['text_span'][1]}% of the "
                                     f"generated image): it cannot be cropped to {c.get('id')} without cutting words")
                rep["ok"] = False
            rec["candidates"].append({"generated": str(q), "master": str(m), "crop": crop_info,
                                      "errors": rep["errors"], "warnings": rep["warnings"]})
            if best is None or _rank(rep) < best[0]:
                best = (_rank(rep), m, rep)
        attempts.append(rec)
        if best and best[0][0] == 0 and len(best[2]["errors"]) <= 3 * args.repair_rounds:
            break  # every approved string is there and spelled right: the rest is removable extras
        corrections = [f'"{x["text"]}" was {x["status"]}' + (f' (it read "{x["read"]}")' if x.get("read") else "") + "."
                       for x in best[2]["copy"] if x["status"] in ("missing", "altered")] if best else []
        corrections += [f'It added "{e["text"]}", which nobody asked for.' for e in (best[2]["extra"] if best else [])][:6]
        if cut:
            ox, oy, kx, ky = fr["crop"]
            a, b = (ox, ox + kx) if kx < 1 else (oy, oy + ky)
            corrections.append(f"The text ran into the strips the final format trims away: keep every word between "
                               f"{_pct(a + 0.03, True)} and {_pct(b - 0.03)} of the {'width' if kx < 1 else 'height'}.")
    record = {"round": n, "notes": notes, "attempts": attempts}
    if best is None:
        return {"ok": False, "reason": "no image was generated", "record": record}
    _, master, rep = best
    fixed, rep, repairs = direct_repair(master, rep, ctx["copy"], ctx["allow_gen"], c.get("id"), args, run)
    record.update(chosen=str(master), repairs=repairs)
    if not rep["ok"]:
        return {"ok": False, "fixed": fixed, "rep": rep, "record": record,
                "reason": "the text is still wrong after the repairs and retries: " + "; ".join(rep["errors"][:4])}
    with Image.open(fixed) as im0:
        im = im0.convert("RGB")
    logo_rep = None
    if ctx["logo"]:
        im, logo_rep = place_logo(im, ctx["logo"], ctx["brand"], im.width / c["w_px"])
    master_out = run / f"{dos['id']}-r{n}-master.png"
    ext = Path(args.out).suffix.lower() if args.out else ".png"
    fmt = ext.lstrip(".").replace("jpeg", "jpg") or "png"
    final_out = run / f"{dos['id']}-r{n}{ext or '.png'}"
    buf = io.BytesIO()
    im.save(buf, "PNG")
    save_image(buf.getvalue(), master_out, "png", 95, None, True)
    fw, fh = fr["final_px"]
    typeset_rep = None
    picture_out = None
    if ctx["typeset"]:  # exact small text set in HTML with the brand's fonts over the picture, checked by the renderer
        picture_out = run / f"{dos['id']}-r{n}-picture.png"  # kept, so the copy can change without a new picture
        shutil.copy2(master_out, picture_out)
        typeset_rep = typeset_overlay(picture_out, ctx["typeset"], c, ctx["brand"], ctx["bj"], final_out, master_out)
        saved = typeset_rep["final"]
    else:
        small = im.resize((fw, fh), Image.LANCZOS) if im.size != (fw, fh) else im
        buf = io.BytesIO()
        small.save(buf, "PNG")
        saved = save_image(buf.getvalue(), final_out, fmt, 90, c.get("max_bytes"), True,
                           dpi=float(c.get("ppi") or 300) if c["print"] else None)
    final_rep = verify_image(final_out if fmt == "png" else master_out, ctx["copy_all"], ctx["allow_final"],
                             c.get("id"))
    if typeset_rep:
        final_rep["errors"] += [f"typeset: {e}" for e in typeset_rep["errors"]]
        final_rep["warnings"] += [f"typeset: {w}" for w in typeset_rep["warnings"]]
        final_rep["ok"] = not final_rep["errors"]
    final_rep = resolve_ambiguous(final_out if fmt == "png" else master_out, final_rep)
    record.update(final=saved, logo=logo_rep, verify=final_rep["errors"], warnings=final_rep["warnings"])
    return {"ok": True, "round": n, "final": final_out, "master": master_out, "final_rep": final_rep,
            "logo_rep": logo_rep, "width": im.width, "record": record, "picture": picture_out}


def place_typeset(im, entries: list, c: dict) -> list:
    """Where each typeset string goes, as a designer would place it: its planned zone when the picture is calm there,
    otherwise the calmest nearby spot (shifted up to about half its size, inside the safe area) that keeps clear of
    the text already in the picture, the logo corner and the other strings. Returns the zones in final-canvas %."""
    from PIL import ImageFilter, ImageStat
    small = im.convert("L")
    k = 400 / max(small.size)
    small = small.resize((max(1, round(small.width * k)), max(1, round(small.height * k))))
    edges = small.filter(ImageFilter.FIND_EDGES)
    W, H = small.size
    st, sr, sb, sl = c["safe_px"]
    fw, fh = c["w_px"], c["h_px"]
    safe = (sl / fw * 100, st / fh * 100, 100 - sr / fw * 100, 100 - sb / fh * 100)
    ocr = ocr_lines_img(im)
    taken = [[b[0] / im.width * 100, b[1] / im.height * 100, (b[0] + b[2]) / im.width * 100,
              (b[1] + b[3]) / im.height * 100] for b in ocr]

    def busy(z):
        x0, y0, x1, y1 = z[0] / 100 * W, z[1] / 100 * H, (z[0] + z[2]) / 100 * W, (z[1] + z[3]) / 100 * H
        box = (max(0, round(x0)), max(0, round(y0)), min(W, max(round(x0) + 1, round(x1))),
               min(H, max(round(y0) + 1, round(y1))))
        return ImageStat.Stat(edges.crop(box)).mean[0] + 0.35 * ImageStat.Stat(small.crop(box)).stddev[0]

    def hits(z, boxes):
        return any(min(z[0] + z[2], b[2]) > max(z[0], b[0]) and min(z[1] + z[3], b[3]) > max(z[1], b[1])
                   for b in boxes)

    # one alignment axis: left-aligned strings snap to the left edge the picture's own type (the headline) uses
    lefts = sorted(b[0] / im.width * 100 for b in ocr if b[0] / im.width < 0.5 and b[3] / im.height > 0.03)
    axis = lefts[len(lefts) // 2] if lefts else None
    out = []
    for s_ in entries:
        z = [float(v) for v in s_["zone"]]
        if axis is not None and s_.get("align", "left") == "left" and abs(z[0] - axis) < 6:
            z[0] = axis
        z[2], z[3] = min(z[2], safe[2] - safe[0]), min(z[3], safe[3] - safe[1])  # no wider than the safe area
        z[0] = min(max(z[0], safe[0]), safe[2] - z[2])  # then inside it (shifted)
        z[1] = min(max(z[1], safe[1]), safe[3] - z[3])
        base = busy(z)
        best = (base, z)
        if base > 12:  # the planned spot is busy: look around it, and at wider, shorter boxes (fewer, longer lines)
            for sw, sh in ((1, 1), (1.25, 0.75), (1.5, 0.6)):
                for fx in (-0.5, -0.25, 0, 0.25, 0.5):
                    for fy in (-0.8, -0.4, 0, 0.4, 0.8):
                        cand = [z[0] + fx * z[2], z[1] + fy * z[3], z[2] * sw, z[3] * sh]
                        if cand[0] < safe[0] or cand[1] < safe[1] or cand[0] + cand[2] > safe[2] or \
                                cand[1] + cand[3] > safe[3] or hits(cand, taken):
                            continue
                        score = busy(cand) + 2 * (abs(fx) + abs(fy)) + 3 * (sw - 1)  # stay near the plan
                        if score < best[0] * 0.7:
                            best = (score, cand)
        out.append(best[1])
        taken.append([best[1][0], best[1][1], best[1][0] + best[1][2], best[1][1] + best[1][3]])
    return out


def ocr_lines_img(im) -> list:
    """Text boxes [x, y, w, h] already in a picture (to keep typeset strings off them)."""
    p_ = Path(tmp_dir("tsocr-")) / "pic.png"
    im.save(p_)
    res = vision("ocr", p_) or {"lines": []}
    return [l_["box"] for l_ in res.get("lines", []) if len(_bare(l_["text"])) > 1]


TYPESET_PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://codex-design.invalid/kit/cd-kit.css">
<link rel="stylesheet" href="{css}">
<script src="https://codex-design.invalid/kit/cd-kit.js"></script>
<style>
.cd-bg{{position:absolute;inset:0;background:url("{img}") center/100% 100% no-repeat}}
.cd-t{{position:absolute;margin:0;display:block;line-height:1.25;hyphens:none;z-index:2}}
.cd-t.v-center{{display:flex;flex-direction:column;justify-content:center}}
.cd-t.v-bottom{{display:flex;flex-direction:column;justify-content:flex-end}}
.cd-scrim{{position:absolute;pointer-events:none}}
</style></head><body>
<div class="cd-bg"></div>
{blocks}
<script>
// lines of one group (the same alignment by default) share one size: the smallest that fitted, so a two-line
// detail block does not read as two levels
window.__cdReady = (async () => {{
  await window.__cdReady;
  const groups = {{}};
  document.querySelectorAll('.cd-t[data-group]').forEach(el => (groups[el.dataset.group] ||= []).push(el));
  for (const els of Object.values(groups)) {{
    const size = Math.min(...els.map(el => parseFloat(getComputedStyle(el).fontSize)));
    els.forEach(el => el.style.fontSize = size + 'px');
  }}
  // small text in steps under 1.25x reads as muddled levels: one size for all of it
  const small = [...document.querySelectorAll('.cd-t[data-group]')];
  const sizes = small.map(el => parseFloat(getComputedStyle(el).fontSize));
  if (sizes.length > 1 && Math.max(...sizes) / Math.min(...sizes) < 1.25) {{
    const m = Math.min(...sizes);
    small.forEach(el => el.style.fontSize = m + 'px');
  }}
}})();
</script>
</body></html>"""


def typeset_overlay(img: Path, entries: list, c: dict, brand: dict, bj: Path, out: Path, master: Path) -> dict:
    """Set the typeset copy over the generated picture in HTML with the brand's real fonts, at exact positions and at
    least the preset's readable size (data-fit), colour chosen against the ground (ink on light, paper on dark), then
    render it at the preset's size with the renderer's checks (contrast on real pixels, fit, safe zone, copy) and
    again at the master's size. Bengali and other scripts get their own font and lang."""
    import html as H
    Image = need_pillow()
    from PIL import ImageStat
    with Image.open(img) as im0:
        im = im0.convert("RGB")
    cw, chh = c["w_px"], c["h_px"]
    cols = brand.get("colors") or {}
    ink, paper = cols.get("ink", "#111111"), cols.get("paper", "#FFFFFF")
    blocks, langs, meta = [], set(), []
    zones, moves = place_typeset(im, entries, c), []
    for s_, z in zip(entries, zones):
        if [round(v, 1) for v in z] != [round(float(v), 1) for v in s_["zone"]]:
            moves.append(f"'{s_['text'][:30]}' placed at {[round(v, 1) for v in z]} instead of {s_['zone']} (the "
                         f"picture's type axis, the safe area or calmer ground)")
    for s_, zone in zip(entries, zones):
        x, y, w, h = [float(v) / 100 for v in zone]
        X, Y, Wd, Hd = x * cw, y * chh, w * cw, h * chh
        lines = s_.get("lines") or [s_["text"]]
        role = str(s_.get("role") or "")
        bn = bool(re.search(r"[\u0980-\u09ff]", s_["text"]))
        dev = bool(re.search(r"[\u0900-\u097f]", s_["text"]))
        lang = "bn" if bn else "hi" if dev else ""
        langs.add(lang)
        family = ("var(--font-bengali, var(--font-text))" if bn else
                  "var(--font-display)" if s_.get("font") == "display" or re.search(r"head|title", role, re.I)
                  else "var(--font-text)")
        # the band the letters will occupy (the middle of the box), not the whole box: a shelf edge or a shadow at
        # its rim must not decide the colour; pick whichever of ink and paper contrasts more with that ground
        band = im.crop((round(x * im.width), round((y + h * 0.25) * im.height), round((x + w) * im.width),
                        round((y + h * 0.75) * im.height)))
        ground = ImageStat.Stat(band).median
        lum = 0.2126 * ground[0] + 0.7152 * ground[1] + 0.0722 * ground[2]
        cr = lambda hx: (max(_rel_lum(_hex_rgb(hx)), _rel_lum(ground)) + 0.05) / \
            (min(_rel_lum(_hex_rgb(hx)), _rel_lum(ground)) + 0.05)
        colour = s_.get("color")
        colour = cols.get(colour, colour) if colour else (ink if cr(ink) >= cr(paper) else paper)
        meta.append({"explicit": bool(s_.get("color")), "ground": _rel_lum(ground), "colour": colour,
                     "box": (X, Y, Wd, Hd), "scrim": bool(s_.get("scrim"))})
        floor = float(c.get("min_text_px") or 12)
        need = max(len(t) for t in lines) * 0.6 * floor  # rough width of the longest line at the readable size
        fit_lines = max(1, int(Hd / (floor * 1.3)))       # lines the box can hold at the readable size
        if need > Wd and len(lines) == 1 and fit_lines > 1:
            import math
            lines_allowed = min(fit_lines, math.ceil(need / Wd) + 1)  # wrap rather than shrink below the floor
        else:
            lines_allowed = len(lines)
        if need > Wd * lines_allowed:  # widen the box towards its free side, inside the safe area
            st_, sr_, sb_, sl_ = c["safe_px"]
            grow = need / lines_allowed - Wd
            al = s_.get("align", "left")
            if al == "right":
                X = max(sl_, X - grow)
            elif al == "center":
                X = max(sl_, X - grow / 2)
            Wd = min(cw - sr_ - X, Wd + grow)
        top = max(floor * 1.2, Hd / lines_allowed / 1.2)
        vcls = {"top": "", "bottom": "v-bottom"}.get(s_.get("valign", "center"), "v-center")
        weight = s_.get("weight") or (600 if re.search(r"cta|call to action|button", role, re.I) else 500)  # one group, one weight
        text = "<br>".join(H.escape(t) for t in lines)
        for em in s_.get("emphasis") or []:  # a stronger weight on part of the string; the words stay the same
            e_ = H.escape(em)
            if e_ in text:
                text = text.replace(e_, f'<b style="font-weight:{min(900, int(s_.get("weight") or 500) + 200)}">{e_}</b>', 1)
        scrim = ""
        if s_.get("scrim"):
            dark = lum > 140
            tint = "255,255,255" if dark else "0,0,0"
            scrim = (f'<div class="cd-scrim" style="left:{X - Hd * 0.6:.1f}px;top:{Y - Hd * 0.5:.1f}px;width:'
                     f'{Wd + Hd * 1.2:.1f}px;height:{Hd * 2:.1f}px;background:radial-gradient(closest-side,rgba({tint},'
                     f'0.55),rgba({tint},0))"></div>')
        group = s_.get("group") or ("" if re.search(r"head|title", role, re.I) else f"a-{s_.get('align', 'left')}")
        blocks.append(scrim + f'<div class="cd-t {vcls}"{" data-group=" + chr(34) + group + chr(34) if group else ""} data-fit="{floor:.0f},{top:.0f}" data-fit-lines="{lines_allowed}" '
                      f'{"lang=" + chr(34) + lang + chr(34) + " " if lang else ""}style="left:{X:.1f}px;top:{Y:.1f}px;'
                      f'width:{Wd:.1f}px;height:{Hd:.1f}px;text-align:{s_.get("align", "left")};'
                      f'color:{colour};font-family:{family};font-weight:{weight}">{text}</div>')
    css = bj.with_name("brand.css")
    page = Path(tmp_dir("typeset-")) / "page.html"
    page.write_text(TYPESET_PAGE.format(lang="en", css=css.as_uri(), img=img.as_uri(), blocks="\n".join(blocks)),
                    encoding="utf-8")
    copy = [{"text": x["text"]} for x in entries]
    with Chrome() as ch:
        rep = produce(ch, page, c, out, qa=True, copy=copy)
        def low_blocks(r):  # lines the renderer measured as low-contrast or sitting on busy detail
            msgs = [e for e in (r.get("checks") or {}).get("warnings", []) + (r.get("checks") or {}).get("errors", [])
                    if "contrast" in e or "detailed part" in e or "runs behind the letters" in e]
            return {i for i, x in enumerate(entries) if any(f"'{x['text'][:20]}" in e for e in msgs)}, len(msgs)

        def render(bl):
            page.write_text(TYPESET_PAGE.format(lang="en", css=css.as_uri(), img=img.as_uri(), blocks="\n".join(bl)),
                            encoding="utf-8")
            return produce(ch, page, c, out, qa=True, copy=copy)

        bad, n_bad = low_blocks(rep)
        if bad:  # 1) the other of ink and paper, where the dossier did not fix the colour
            flip = {ink: paper, paper: ink}
            trial = list(blocks)
            for i in bad:
                if not meta[i]["explicit"] and meta[i]["colour"] in flip:
                    trial[i] = trial[i].replace(f"color:{meta[i]['colour']};", f"color:{flip[meta[i]['colour']]};")
            if trial != blocks:
                rep2 = render(trial)
                bad2, n2 = low_blocks(rep2)
                if n2 < n_bad:
                    blocks, rep, bad, n_bad = trial, rep2, bad2, n2
                    for i in range(len(meta)):
                        m_ = re.search(r"color:(#[0-9a-fA-F]{3,8});", blocks[i])
                        meta[i]["colour"] = m_.group(1) if m_ else meta[i]["colour"]
        bad = {i for i in bad if not meta[i]["explicit"]}  # a colour the dossier chose is a design decision: report it
        if bad:  # 2) a soft scrim that pushes the ground away from the letters' tone
            trial = list(blocks)
            for i in bad:
                if meta[i]["scrim"]:  # it has its scrim already: a second one would only muddy it
                    continue
                X, Y, Wd, Hd = meta[i]["box"]  # the text box itself, not a scrim's inflated one
                text_l = _rel_lum(_hex_rgb(meta[i]["colour"])) if str(meta[i]["colour"]).startswith("#") else 0.5
                tint = "0,0,0" if text_l >= meta[i]["ground"] else "255,255,255"
                trial[i] = (f'<div class="cd-scrim" style="left:{X - Hd * 0.8:.1f}px;top:{Y - Hd * 0.6:.1f}px;width:'
                            f'{Wd + Hd * 1.6:.1f}px;height:{Hd * 2.2:.1f}px;background:radial-gradient(closest-side,'
                            f'rgba({tint},0.62),rgba({tint},0.35) 60%,rgba({tint},0))"></div>') + trial[i]
            rep2 = render(trial)
            if low_blocks(rep2)[1] < n_bad:
                blocks, rep = trial, rep2
                rep["scrim_added"] = True
            else:
                rep = render(blocks)
        big = produce(ch, page, c, master, scale=im.width / cw if not c["print"] else None, qa=False)
    chk = rep.get("checks") or {}
    # the typeset copy is only part of the design's text: "missing" or "extra" findings about the rest are not ours
    errs = [e for e in chk.get("errors", []) if not re.search(r"approved copy|not in the approved copy", e)]
    warns = [w for w in chk.get("warnings", []) if not re.search(r"approved copy|not in the approved copy", w)]
    if rep.get("scrim_added"):
        warns.append("a soft scrim was added behind small text whose ground was too busy or too close in tone: look "
                     "at it, and keep that zone calmer in the next concept")
    warns += moves
    return {"final": rep["outputs"][0], "master": big["outputs"][0], "errors": errs, "warnings": warns,
            "overlay": rep.get("overlay"), "qa": rep.get("qa_json")}


def direct_judge(final: Path, ctx: dict, args) -> dict:
    """The independent art-director review (design.py judge, full-AI rules) of one final file. The judge gets the
    run's per-session --timeout and this waits for its one retry as well; the whole report is read from
    <final>.judge.json, since the judge prints only a summary."""
    c, dos, run = ctx["c"], ctx["dos"], ctx["run"]
    fw, fh = ctx["fr"]["final_px"]
    jcmd = [sys.executable, str(Path(__file__).resolve()), "judge", "--image", str(final), "--brief",
            str(run / "brief.md"), "--copy", str(run / "copy.json"), "--route", "full-ai",
            "--kind", dos.get("kind") or c.get("label") or "social post",
            "--canvas", f"{c.get('label') or c.get('id')} {fw}x{fh}", "--timeout", str(args.timeout)] + \
        (["--print"] if c["print"] else [])
    if ctx["allow_final"]:
        jcmd += ["--allow", ",".join(ctx["allow_final"])]
    try:
        jr = run_session(jcmd, None, child_budget(args.timeout))
    except OSError as e:
        return {"error": f"the judge did not start ({e})"}
    if jr["error"]:
        return {"error": f"the judge did not answer ({jr['error']})"}
    try:
        data = json.loads(final.with_name(final.stem + ".judge.json").read_text(encoding="utf-8"))
        if jr["returncode"] == 0 and data.get("image_sha256") == file_sha256(final):
            return data
    except (OSError, ValueError):
        pass
    return {"error": codex_error(jr)}


# ----------------------------------------------------------------------------- references for the single-prompt route
def make_refsheet(bj: Path, css: Path | None, out: Path, model: bool = False) -> dict:
    """Render the brand sheet. model=True is the version the image model sees: colours, type character and motif
    only, with no logo (the real logo is composited afterwards, so the model must not draw one) and no words (labels,
    names and hex codes in a reference get copied into designs)."""
    css = css or bj.with_name("brand.css")
    if not css.exists():
        die(f"no brand.css next to {bj}: run `design.py brand --json {bj}` first")
    html = (KIT_ROOT / "ai" / "brand-sheet.html").read_text(encoding="utf-8")
    html = html.replace('<body data-brand="https://codex-design.invalid/sample-brand/brand.json">',
                        f'<body data-brand="{bj.as_uri()}"' + (' data-mode="model"' if model else "") + ">")
    html = html.replace('href="https://codex-design.invalid/sample-brand/brand.css"', f'href="{css.as_uri()}"')
    tmp = Path(tmp_dir("refsheet-")) / "sheet.html"
    tmp.write_text(html, encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    with Chrome() as ch:
        rep = produce(ch, tmp, resolve_canvas(None, "1536x1024"), out, qa=False)
    return {"sheet": rep["outputs"][0]["path"], "size": [1536, 1024], "for_model": model,
            "role": REF_ROLES["brand"] if model else "brand sheet for people: logo, colours, fonts and motif"}


def cmd_refsheet(args) -> None:
    """The brand on one 3:2 reference image (logo on light and dark, palette, type specimens in the real fonts, motif);
    --for-model makes the word-free, logo-free version the direct route attaches."""
    bj = Path(args.brand).expanduser().resolve()
    if not bj.exists():
        die(f"not found: {bj}")
    print(json.dumps(make_refsheet(bj, Path(args.css).expanduser().resolve() if args.css else None,
                                   Path(args.out).expanduser(), args.for_model), indent=2))


def draw_sketch(zones: list, w: int, h: int, safe: list, out: Path) -> Path:
    """A layout sketch: grey zones with labels on white, the safe area dotted. Zones are [label, x%, y%, w%, h%]."""
    Image = need_pillow()
    from PIL import ImageDraw, ImageFont
    im = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    size = max(18, w // 28)
    font = None
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/Library/Fonts/Arial.ttf"):
        try:
            font = ImageFont.truetype(f, size)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    st, sr, sb, sl = safe
    for x in range(int(sl), int(w - sr), 14):  # dotted safe area
        d.point([(x, st), (x, h - sb)], fill=(150, 150, 150))
    for y in range(int(st), int(h - sb), 14):
        d.point([(sl, y), (w - sr, y)], fill=(150, 150, 150))
    shades = [(222, 222, 222), (200, 200, 200), (235, 235, 235), (210, 210, 210)]
    for i, z in enumerate(zones):
        label, zx, zy, zw, zh = z[0], *[float(v) for v in z[1:5]]
        box = [zx / 100 * w, zy / 100 * h, (zx + zw) / 100 * w, (zy + zh) / 100 * h]
        d.rectangle(box, fill=shades[i % len(shades)], outline=(120, 120, 120), width=max(2, w // 400))
        f = font
        if hasattr(font, "font_variant"):  # the label fits its zone
            f = font.font_variant(size=max(10, min(size, int((box[3] - box[1]) * 0.6), int((box[2] - box[0]) / max(4, len(label)) * 1.6))))
        tb = d.textbbox((0, 0), label, font=f)
        tx = box[0] + (box[2] - box[0] - (tb[2] - tb[0])) / 2
        ty = box[1] + (box[3] - box[1] - (tb[3] - tb[1])) / 2
        d.text((tx, ty - tb[1]), label, fill=(90, 90, 90), font=f)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def cmd_sketch(args) -> None:
    c = resolve_canvas(args.preset, args.size)
    w, h = round(c["w_px"]), round(c["h_px"])
    if args.scale:
        k = args.scale
    else:
        k = min(1.0, 1024 / max(w, h))  # a sketch needs no more than ~1 MP
    zones = json.loads(Path(args.zones).expanduser().read_text(encoding="utf-8")) if Path(args.zones).expanduser().exists() \
        else json.loads(args.zones)
    out = draw_sketch(zones, round(w * k), round(h * k), [v * k for v in c["safe_px"]], Path(args.out).expanduser())
    print(json.dumps({"sketch": str(out), "canvas": [w, h], "zones": zones,
                      "role": "layout sketch: follow its zones and proportions; do not draw the boxes, labels or dots"},
                     indent=2, ensure_ascii=False))


def cmd_cutout(args) -> None:
    src, out = Path(args.src).expanduser(), Path(args.out).expanduser()
    if not src.exists():
        die(f"not found: {src}")
    out.parent.mkdir(parents=True, exist_ok=True)
    res = vision("cutout", src, out)
    if not res:
        die("local subject cutout needs macOS 14+ with swiftc; otherwise use codex_image.py cutout (flat backgrounds) "
            "or a transparent AI edit")
    print(json.dumps(res, indent=2))


# ----------------------------------------------------------------------------- fonts and brand tokens
FONT_API = "https://api.fontsource.org/v1/fonts"
FONT_CDN = "https://cdn.jsdelivr.net/fontsource/fonts"
SCRIPT_SUBSETS = {"bengali", "devanagari", "arabic", "hebrew", "cyrillic", "cyrillic-ext", "greek", "greek-ext",
                  "vietnamese", "thai", "tamil", "telugu", "gujarati", "gurmukhi", "kannada", "malayalam", "oriya",
                  "sinhala", "khmer", "lao", "myanmar", "georgian", "armenian", "ethiopic"}


def http_get(url: str, timeout: int = 40) -> bytes:
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": f"codex-design/{SKILL_VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def font_meta(family: str) -> dict:
    """Fontsource metadata (subsets, weights, styles, unicode ranges, licence), cached for 30 days."""
    from urllib.error import HTTPError
    from urllib.parse import quote
    fid = re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")
    cache = CACHE / "fonts" / fid / "meta.json"
    if cache.exists() and time.time() - cache.stat().st_mtime < 30 * 86400:
        return json.loads(cache.read_text(encoding="utf-8"))
    try:
        meta = json.loads(http_get(f"{FONT_API}/{fid}"))
    except HTTPError as e:
        if e.code != 404:
            raise
        hits = [h for h in json.loads(http_get(f"{FONT_API}?family={quote(family)}"))
                if h.get("family", "").lower() == family.lower()]
        if not hits:
            die(f"font family {family!r} not found on Fontsource (Google Fonts and other open fonts); "
                f"try `design.py fonts --search <words>`")
        meta = json.loads(http_get(f"{FONT_API}/{hits[0]['id']}"))
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(meta), encoding="utf-8")
    return meta


def parse_font_spec(spec: str) -> tuple:
    """'Inter:400,700,700i' -> ('Inter', [(400,'normal'), (700,'normal'), (700,'italic')]). A trailing '@110'
    ('Noto Sans Bengali:400,700@110') is a size-adjust percentage, read by font_size_adjust()."""
    fam, _, ws = spec.split("@")[0].partition(":")
    out = []
    for w in (ws or "400,700").split(","):
        w = w.strip().lower()
        if not w:
            continue
        ital = w.endswith("i")
        out.append((int(w.rstrip("i")), "italic" if ital else "normal"))
    return fam.strip(), out


def font_size_adjust(spec: str):
    """The '@110' of a font spec: scales a second script to its Latin partner (size-adjust: 110%)."""
    m = re.search(r"@\s*([0-9.]+)\s*%?\s*$", spec)
    return float(m.group(1)) if m else None


def install_fonts(specs: list, out_dir: Path, subsets: list | None = None) -> dict:
    """Download the woff2 files of each family/weight/subset into out_dir/<id>/ and write out_dir/fonts.css with
    unicode-range rules, so Latin and non-Latin files combine under one family name."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rules, lic, fams, files = [], [], [], 0
    for spec in specs:
        fam, variants = parse_font_spec(spec)
        adjust = font_size_adjust(spec)
        meta = font_meta(fam)
        subs = subsets or [s for s in meta["subsets"] if s in ("latin", "latin-ext") or s in SCRIPT_SUBSETS]
        subs = [s for s in subs if s in meta["subsets"]]
        if not subs:
            die(f"{meta['family']}: none of the subsets {subsets} exist (it has {meta['subsets'][:12]})")
        for w, st in variants:
            if w not in meta["weights"] or st not in meta["styles"]:
                die(f"{meta['family']} has weights {meta['weights']} and styles {meta['styles']}; {w} {st} is not one")
            for sub in subs:
                name = f"{sub}-{w}-{st}.woff2"
                cached = CACHE / "fonts" / meta["id"] / name
                if not cached.exists():
                    cached.parent.mkdir(parents=True, exist_ok=True)
                    cached.write_bytes(http_get(f"{FONT_CDN}/{meta['id']}@latest/{name}"))
                dst = out_dir / meta["id"] / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                if not dst.exists() or dst.stat().st_size != cached.stat().st_size:
                    shutil.copy2(cached, dst)
                files += 1
                rng = (meta.get("unicodeRange") or {}).get(sub)
                rules.append(f"@font-face{{font-family:'{meta['family']}';font-style:{st};font-weight:{w};"
                             f"font-display:block;src:url('{meta['id']}/{name}') format('woff2')"
                             + (f";unicode-range:{rng}" if rng else "")
                             + (f";size-adjust:{adjust:g}%" if adjust else "") + "}")
        fams.append({"family": meta["family"], "css": f"'{meta['family']}'", "weights": sorted({w for w, _ in variants}),
                     "subsets": subs, "category": meta.get("category"), "license": meta.get("license")})
        lic.append(f"- {meta['family']} · {meta.get('license')} · https://fontsource.org/fonts/{meta['id']}")
    (out_dir / "fonts.css").write_text("\n".join(rules) + "\n", encoding="utf-8")
    (out_dir / "FONT-LICENSES.md").write_text("# Fonts used\n\n" + "\n".join(lic) +
                                              "\n\nOFL fonts may be used commercially, embedded in PDFs and bundled; "
                                              "they may not be sold on their own.\n", encoding="utf-8")
    return {"css": str(out_dir / "fonts.css"), "families": fams, "files": files,
            "licenses": str(out_dir / "FONT-LICENSES.md")}


def cmd_fonts(args) -> None:
    if args.search:
        from urllib.parse import urlencode
        q = {k: v for k, v in (("subsets", args.subset), ("category", args.category)) if v}
        hits = json.loads(http_get(f"{FONT_API}?{urlencode(q)}" if q else FONT_API))
        words = [w.lower() for w in args.search.split()] if args.search != "*" else []
        rows = [{"family": h["family"], "category": h.get("category"), "weights": h.get("weights"),
                 "subsets": [s for s in h.get("subsets", []) if not s[:1].isdigit()][:8], "variable": h.get("variable"),
                 "license": h.get("license")} for h in hits
                if all(w in (h.get("family", "") + " " + h.get("category", "")).lower() for w in words)]
        print(json.dumps(rows[:60], indent=1, ensure_ascii=False))
        if len(rows) > 60:
            log(f"showing 60 of {len(rows)} families; add words to --search or use --subset/--category")
        return
    if not args.family:
        die("give --family 'Inter:400,700' (repeatable) or --search")
    subs = [s.strip() for s in args.subsets.split(",")] if args.subsets else None
    print(json.dumps(install_fonts(args.family, Path(args.out).expanduser(), subs), indent=2, ensure_ascii=False))


def need_shaping():
    """uharfbuzz + fontTools from the skill venv (`doctor --setup`)."""
    add_venv_paths()
    try:
        import uharfbuzz  # noqa: F401
        import fontTools  # noqa: F401
    except ImportError:
        die("outline needs uharfbuzz and fontTools; run `design.py doctor --setup` once")


def cmd_outline(args) -> None:
    """Text -> SVG outlines, shaped by HarfBuzz (kerning, ligatures, Bengali/Devanagari conjuncts and Arabic joining
    come out right): the way wordmarks and print logos are delivered, with no font dependency."""
    need_shaping()
    import uharfbuzz as hb
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    if args.font:
        path = Path(args.font).expanduser()
    else:
        meta = font_meta(args.family)
        sub = args.subset or ("bengali" if re.search(r"[ঀ-৿]", args.text) else
                              "devanagari" if re.search(r"[ऀ-ॿ]", args.text) else
                              "arabic" if re.search(r"[؀-ۿ]", args.text) else "latin")
        name = f"{sub}-{args.weight}-{'italic' if args.italic else 'normal'}.ttf"
        path = CACHE / "fonts" / meta["id"] / name
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(http_get(f"{FONT_CDN}/{meta['id']}@latest/{name}"))
    if not path.exists():
        die(f"font file not found: {path}")
    blob = hb.Blob.from_file_path(str(path))
    face = hb.Face(blob)
    font = hb.Font(face)
    upem = face.upem
    buf = hb.Buffer()
    buf.add_str(args.text)
    buf.guess_segment_properties()
    feats = {}
    for f in (args.features or "").split(","):
        f = f.strip()
        if f:
            feats[f.lstrip("+-")] = not f.startswith("-")
    hb.shape(font, buf, feats)
    k = args.size / upem
    track = args.tracking * upem
    svg_pen, bounds = SVGPathPen(None), BoundsPen(None)
    x = 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        t = (k, 0, 0, -k, (x + pos.x_offset) * k, -pos.y_offset * k)
        font.draw_glyph_with_pen(info.codepoint, TransformPen(svg_pen, t))
        font.draw_glyph_with_pen(info.codepoint, TransformPen(bounds, t))
        x += pos.x_advance + track
    if not bounds.bounds:
        die("nothing to draw: the font has no glyphs for this text (wrong subset?)")
    x0, y0, x1, y1 = bounds.bounds
    pad = args.size * 0.02
    vb = f"{x0 - pad:.2f} {y0 - pad:.2f} {x1 - x0 + 2 * pad:.2f} {y1 - y0 + 2 * pad:.2f}"
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{x1 - x0 + 2 * pad:.1f}" '
                   f'height="{y1 - y0 + 2 * pad:.1f}"><title>{html_escape(args.text)}</title>'
                   f'<path fill="{args.fill}" d="{svg_pen.getCommands()}"/></svg>\n', encoding="utf-8")
    print(json.dumps({"svg": str(out), "font": str(path), "glyphs": len(buf.glyph_infos),
                      "width": round(x1 - x0, 1), "height": round(y1 - y0, 1),
                      "note": "outlines: no font needed to display or print it; kern pairs by hand with --tracking "
                              "or by editing the paths"}, indent=2, ensure_ascii=False))


def cmd_brand(args) -> None:
    """brand.json -> fonts/ + brand.css (CSS variables for colours, fonts, radius, logo paths)."""
    src = Path(args.json).expanduser()
    try:
        b = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read {src}: {e}")
    out = Path(args.out).expanduser() if args.out else src.parent
    out.mkdir(parents=True, exist_ok=True)
    lines = []
    fonts = b.get("fonts") or {}
    res = None
    if fonts:
        res = install_fonts(list(fonts.values()), out / "fonts")
        lines.append('@import url("fonts/fonts.css");')
    fallback = {"serif": "Georgia, serif", "sans-serif": "system-ui, sans-serif", "display": "system-ui, sans-serif",
                "handwriting": "cursive", "monospace": "ui-monospace, monospace"}
    var = []
    for k, v in (b.get("colors") or {}).items():
        var.append(f"--{re.sub(r'[^a-z0-9-]+', '-', k.lower())}:{v}")
    for role, spec in fonts.items():
        fam = parse_font_spec(spec)[0]
        cat = next((f["category"] for f in (res or {}).get("families", []) if f["family"].lower() == fam.lower()),
                   "sans-serif")
        var.append(f"--font-{re.sub(r'[^a-z0-9-]+', '-', role.lower())}:'{fam}', {fallback.get(cat, 'sans-serif')}")
    if b.get("radius") is not None:
        var.append(f"--radius:{b['radius']}px")
    for k, v in (b.get("logo") or {}).items():
        p = Path(v)
        rel = os.path.relpath((src.parent / p).resolve() if not p.is_absolute() else p, out.resolve())
        var.append(f"--logo-{re.sub(r'[^a-z0-9-]+', '-', k.lower())}:url('{rel}')")
    # the brand's minimum logo sizes as sizes a pattern can use at any preset: px at viewing size on screens (the
    # renderer sets --view-scale), mm in print: width: max(…, var(--mark-min))
    ms = b.get("min_size") if isinstance(b.get("min_size"), dict) else {}
    for k in ("mark", "wordmark"):
        v = str(ms.get(k) or "")
        px, mm = re.search(r"(\d+(?:\.\d+)?)\s*px", v), re.search(r"(\d+(?:\.\d+)?)\s*mm", v)
        if px or mm:
            var.append(f"--{k}-min:max({mm.group(1) if mm else 0}mm, calc({px.group(1) if px else 0}px * 1.05 * "
                       f"var(--view-scale, 0)))")  # 5 % over: a measured logo is never a pixel short
    lines.append(":root{" + ";".join(var) + "}")
    (out / "brand.css").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"brand_css": str(out / "brand.css"), "variables": var, "fonts": res}, indent=2,
                     ensure_ascii=False))


def cmd_kit(args) -> None:
    """Copy the kit (and the sample brand) next to the designs so the HTML works outside the renderer, and rewrite
    the https://codex-design.invalid/ links of the given HTML files to those copies (for editable-source delivery)."""
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    copied = []
    for sub in ["kit"] + (["sample-brand"] if args.sample_brand else []):
        shutil.copytree(KIT_ROOT / sub, out / sub, dirs_exist_ok=True)
        copied.append(str(out / sub))
    rewritten = []
    for h in args.html or []:
        hp = Path(h).expanduser()
        text = hp.read_text(encoding="utf-8")
        rel = os.path.relpath(out.resolve(), hp.parent.resolve())
        new = text.replace(KIT_HOST, "" if rel == "." else rel.replace(os.sep, "/") + "/")
        if new != text:
            hp.write_text(new, encoding="utf-8")
            rewritten.append(str(hp))
    print(json.dumps({"copied": copied, "rewritten": rewritten}, indent=2))


PRESET_KEYS = ("id", "group", "label", "platform", "w", "h", "safe", "safe_mm", "keepout", "bleed", "view_width_px",
               "thumb_width_px", "min_text_px", "view_distance_m", "screen_height_m", "legibility_index", "file_scale",
               "transparent", "max_bytes", "aliases", "notes", "source", "verified", "origin")


def cmd_presets(args) -> None:
    """The canvas catalogue: all of it or one group, one preset in full (--id), a word search in names, aliases and
    notes (--find), or the presets nearest an unknown size by aspect ratio (--nearest WxH)."""
    if getattr(args, "id", None):
        c = presets().get(args.id)
        if not c:
            resolve_canvas(args.id, None)  # the retired-format or did-you-mean message
        print(json.dumps(c, indent=2, ensure_ascii=False))
        return
    if getattr(args, "find", None):
        hits = find_presets(args.find)
        if hits and hits[0].get("read_as"):
            log("read " + ", ".join(f"'{a}' as '{b}'" for a, b in hits[0]["read_as"].items()) +
                ": check the results match what you meant")
        rows = [({k: r[k] for k in PRESET_KEYS if k in r} | ({"retired": r.get("retired"), "use": r.get("use")}
                                                                if r.get("use") else {})) for r in hits[:12]]
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        if not rows:
            log(f"no preset matches {args.find!r}: find the platform's spec (references/formats.md), then render with "
                f"--size and --safe, or add it to a --preset-file")
        return
    if getattr(args, "nearest", None):
        m = re.fullmatch(r"\s*([0-9.]+(?:px|mm|in|cm)?)\s*[xX×]\s*([0-9.]+(?:px|mm|in|cm)?)\s*", args.nearest)
        if not m:
            die("--nearest takes a size such as 1500x3000 or 150mmx150mm")
        w, h = parse_len(m.group(1)), parse_len(m.group(2))
        printed = any(x.endswith(("mm", "in", "cm")) for x in m.groups())
        print(json.dumps({"size": args.nearest, "ratio": round(w / h, 3), "nearest": nearest_presets(w, h, printed)},
                         indent=2, ensure_ascii=False))
        return
    groups = sorted({str(p.get("group")) for p in presets().values()})
    if args.group and args.group not in groups:
        die(f"unknown --group {args.group!r}; groups: {', '.join(groups)}")
    rows = []
    for p in presets().values():
        if args.group and p.get("group") != args.group:
            continue
        rows.append({k: p[k] for k in ("id", "group", "label", "w", "h", "safe", "safe_mm", "bleed", "max_bytes",
                                       "min_text_px", "aliases", "notes", "origin") if k in p})
    if getattr(args, "json", False):
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    # one line each: the whole catalogue as JSON is 361 KB, far more than anyone reads to pick a size
    for p in rows:
        print(f"{p['id']:<32} {str(p['w']) + 'x' + str(p['h']):<16} {p.get('group', '')}")
    log(f"{len(rows)} presets. `presets --find WORDS` searches them, `--id ID` shows one in full, `--json` lists "
        f"every field")


SETUP_PACKAGES = ["pillow", "segno", "pypdf", "uharfbuzz", "fonttools"]


def cmd_doctor(args) -> None:
    """Everything a run needs, checked: `ready` means a test design rendered, saved through Pillow and measured.
    Optional parts (the judges, QR, PDF boxes, outlines, OCR) are listed with what they unlock."""
    if args.setup:
        if not (VENV_DIR / "bin" / "python").exists():
            subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        subprocess.run([str(VENV_DIR / "bin" / "python"), "-m", "pip", "install", "-q", "--upgrade"] +
                       SETUP_PACKAGES, check=True)
        log(f"venv ready at {VENV_DIR} ({', '.join(SETUP_PACKAGES)})")
    if args.clean_tmp:
        gone = []
        for d in stale_runs():
            shutil.rmtree(d["path"], ignore_errors=True)
            gone.append(d)
        log(f"removed {len(gone)} folder(s) of killed runs, {sum(d['bytes'] for d in gone) / 1e6:.1f} MB")
    rep = {"skill_version": SKILL_VERSION, "python": sys.version.split()[0], "venv": str(VENV_DIR)}
    missing = []
    if sys.version_info < (3, 9):
        rep["python"] += " (too old: 3.9 or newer)"
        missing.append("python")
    try:
        rep["chrome"] = chrome_bin()
        rep["chrome_version"] = subprocess.run([rep["chrome"], "--version"], capture_output=True, text=True,
                                               timeout=30).stdout.strip()
    except SystemExit:
        rep["chrome"] = "NOT FOUND (install Google Chrome or set CODEX_DESIGN_CHROME)"
        missing.append("chrome")
    try:
        need_pillow()
        import PIL
        rep["pillow"] = PIL.__version__
    except SystemExit:
        rep["pillow"] = "missing: run `doctor --setup`"
        missing.append("pillow")
    rep["presets"] = len(presets())
    optional = {}
    ci = _imagegen() if IMAGEGEN.exists() else None
    if ci is None:
        optional["codex_imagegen"] = f"missing ({IMAGEGEN}): AI plates, judge, copyjudge, pairwise and direct"
    else:
        rep["codex_imagegen"] = str(IMAGEGEN)
        bin_ = os.environ.get("CODEX_BIN") or shutil.which("codex")
        if not bin_:
            optional["codex"] = "Codex CLI not found: judge, copyjudge, pairwise, direct and AI plates need it"
        else:
            try:
                st = subprocess.run([bin_, "login", "status"], capture_output=True, text=True, timeout=30)
                line = (st.stdout + st.stderr).strip().splitlines()
                rep["codex"] = f"{ci.codex_version(bin_)}; {line[0] if line else 'login status unknown'}"
                if st.returncode != 0:
                    optional["codex_login"] = "not logged in: run `codex login` (the judges need it)"
            except (OSError, subprocess.TimeoutExpired):
                rep["codex"] = f"{bin_} (login status unknown)"
    add_venv_paths()
    for mod, use in (("segno", "qr"), ("pypdf", "exact print PDF boxes"), ("uharfbuzz", "outline (SVG wordmarks)"),
                     ("fontTools", "outline (SVG wordmarks)")):
        try:
            __import__(mod)
            rep[mod] = "ok"
        except ImportError:
            optional[mod] = f"missing: `doctor --setup` ({use})"
    rep["pdffonts"] = shutil.which("pdffonts") or "missing (brew install poppler): print PDFs skip the font check"
    vb = vision_bin()
    rep["vision"] = f"ok ({vb})" if vb else "unavailable (needs macOS + swiftc): analyze/reframe fall back to the " \
                                           "centre, ocr and verify do not run, cutout needs codex_image.py"
    if not vb:
        optional["vision"] = rep["vision"]
    rep["cache"] = str(CACHE)
    stale = stale_runs()
    if stale:
        rep["stale_temp"] = f"{len(stale)} folder(s) of killed runs, {sum(d['bytes'] for d in stale) / 1e6:.1f} MB: " \
                            f"`doctor --clean-tmp` removes them"
    if "chrome" not in missing:
        d = Path(tmp_dir("doctor-"))
        (d / "t.html").write_text("<html><body style='margin:0;background:#fff'><p id=t style='font:40px serif'>"
                                  "Ag অক্ষ</p></body></html>", encoding="utf-8")
        t0 = time.time()
        try:
            with Chrome() as ch:
                page = render_page(ch, d / "t.html", resolve_canvas(None, "400x200"), 1, False, True, False, True)
            saved = save_image(page["png"], d / "t.png", "png", 90, None, False)  # through Pillow, as renders are
            rep["render_test"] = f"pass ({time.time() - t0:.1f}s, {saved['bytes']} bytes, " \
                                 f"{len(page['qa']['items'])} text item)"
        except SystemExit as e:
            rep["render_test"] = f"FAIL: {e}"
        except Exception as e:
            rep["render_test"] = f"FAIL: {e!r}"
    rep["ready"] = not missing and str(rep.get("render_test", "")).startswith("pass")
    if optional:
        rep["optional_missing"] = optional
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    if not rep["ready"]:
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ copy
COPY_CRITERIA = {"naturalness": 20, "hook": 14, "clarity": 12, "specificity": 10, "register": 10, "locale": 10,
                 "cta": 8, "voice": 6, "emotion": 5, "no_ai_tells": 5}
COPY_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["reader", "first_read", "scores", "ai_tells", "strings", "hooks", "cta", "notes"],
    "properties": {
        "reader": {"type": "string"},
        "first_read": {"type": "string"},
        "scores": {"type": "object", "additionalProperties": False, "required": list(COPY_CRITERIA),
                   "properties": {k: {"type": "integer", "minimum": 0, "maximum": 5} for k in COPY_CRITERIA}},
        "ai_tells": {"type": "array", "items": {"type": "string"}},
        "strings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["role", "text", "natural", "problem", "rewrite"],
            "properties": {"role": {"type": "string"}, "text": {"type": "string"},
                           "natural": {"type": "integer", "minimum": 0, "maximum": 5},
                           "problem": {"type": "string"}, "rewrite": {"type": "string"}}}},
        "hooks": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "cta": {"type": "string"},
        "notes": {"type": "array", "items": {"type": "string"}, "maxItems": 5}}}
COPY_JUDGE_PROMPT = """You are a senior copywriter and a native reader. Read this copy the way {reader} would meet it on
{platform}, in the feed, on a phone, in two seconds. The copy is for:
---
{brief}
---
Goal of the piece: {goal}. Copy deck (role: text), in reading order:
{deck}
An automatic lint already found: {lint}

Judge only how the words land with that reader:
- First, fidelity: every fact, number, name, feeling and experience in the copy must come from the brief. A line
  that invents one (a customer, a quote, "we tasted it at dawn", a result) is a defect however human it sounds;
  score specificity and no_ai_tells 1 or lower for it and say so in the string's problem. Alt text (role alt, alt_1
  and on) describes the picture, which you do not see: its colours, objects and layout are not invented facts, so
  judge only its words there (plain, short, everyday, no "image of").
- naturalness: the friend test. Would someone from this audience say it this way to a friend, or to a shopkeeper
  they like, on social media today? Score it down for anything else: translated, robotic, bookish or textbook,
  poetic, flowery or literary, old-fashioned, government or notice-like, corporate, and forced casual (a pile of
  slang, a borrowed dialect, memes, fake typos, "Honestly?" or "Real talk" worn as a costume). (Bangladeshi Bengali:
  everyday চলিত words as people say them, the English words people really mix in written in Bengali script,
  Bangladeshi usage such as পানি and গোসল, never sadhu forms or stiff "shuddho" textbook Bangla.)
- hook: would it stop the scroll? clarity: one idea, understood on the first read. specificity: concrete facts from
  the brief, and specific to this brand: could a competitor post it unchanged? register: the right formality and
  address form for this audience. locale: spelling, numbers, words and references of this market. cta: one clear,
  low-friction action that fits the goal (or rightly none). voice: the brand's voice and a point of view.
  emotion: does it make the reader feel something. no_ai_tells: 5 means none.
- Do not reward length: when two lines say the same, the shorter one is better.
- Score each 0-5 (3 = acceptable, 4 = strong, 5 = a senior native writer's work).
- For every string give natural 0-5, the problem in one line (empty if none) and a rewrite in the same language
  (empty if it is already right). Rewrites keep every fact, name, number, date and price exactly; add no claims,
  experiences or feelings; never add slang, particles, emoji or typos to sound human (more human does not mean more
  slang); never use an em dash or a spaced en dash; keep the address form the brand uses; fit the role's length (a
  headline stays a headline, a call to action stays up to 4 words in English and up to 6 in Bengali).
- House style (the client's rule, not up for debate): no em dash, no spaced en dash and no en dash between words
  anywhere, in any language, because readers take them as AI-written copy; ranges are written the local way (১০-১২
  or ১০ থেকে ১২, "10 to 12"). Treat any such dash as a defect and never use one in a rewrite.
- List every AI or translation tell you see. Offer up to three stronger hooks in the same language and the best call
  to action for the goal. Answer the analysis in English; write rewrites, hooks and the CTA in the copy's own
  language and script (Bengali in Bengali script, never romanised), whatever other instructions say about the reply
  language."""


LYRIC_CRITERIA = {"song_language": 20, "imagery": 16, "singability": 16, "emotion": 14, "genre_fit": 12, "hook": 10,
                  "freshness": 7, "no_ai_tells": 5}
LYRIC_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["reader", "first_read", "scores", "ai_tells", "strings", "hooks", "notes"],
    "properties": {
        "reader": {"type": "string"},
        "first_read": {"type": "string"},
        "scores": {"type": "object", "additionalProperties": False, "required": list(LYRIC_CRITERIA),
                   "properties": {k: {"type": "integer", "minimum": 0, "maximum": 5} for k in LYRIC_CRITERIA}},
        "ai_tells": {"type": "array", "items": {"type": "string"}},
        "strings": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["role", "text", "natural", "problem", "rewrite"],
            "properties": {"role": {"type": "string"}, "text": {"type": "string"},
                           "natural": {"type": "integer", "minimum": 0, "maximum": 5},
                           "problem": {"type": "string"}, "rewrite": {"type": "string"}}}},
        "hooks": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "notes": {"type": "array", "items": {"type": "string"}, "maxItems": 5}}}
LYRIC_JUDGE_PROMPT = """You are a senior lyricist and a native listener. Read these song lyrics the way {reader} would hear
them sung. The song is for:
---
{brief}
---
Goal of the song: {goal}. Sections (role: text), in singing order:
{deck}
An automatic lint already found: {lint}

Judge them as song writing, not as marketing copy:
- Lines the songwriter wrote themselves (a role that says own, fixed or keep) stay exactly as they are: judge how the
  new sections carry them, and never rewrite them.
- song_language: does it sound like a real song of this genre and market? Poetic and literary words are allowed and
  often right. Everyday chat, phone-call talk, prose that does not sing, and ad or post phrasing are defects.
  (Bangladeshi songs: the words, images and references of today's Bangladeshi band, modern, film and indie songs and
  Bangladeshi usage such as পানি and গোসল; a line that sounds like Kolkata adhunik, a textbook poem or a chat message is
  a defect, unless the brief asks for that sound.)
- imagery: fresh, concrete pictures a listener can see (a place, a time of day, a small action), not stock images.
- singability: an even meter within paired lines (count the syllables), natural stress on the beat, open vowels on
  long notes, and rhyme or near rhyme where the genre expects it.
- emotion: the feeling builds from section to section towards the hook. genre_fit: the words, references and form
  of this genre and market. hook: one line people remember and sing back. freshness: no pile of stock song phrases
  (চাঁদের আলো, স্বপ্নের ডানায় and the like) or AI-song clichés. no_ai_tells: 5 means none.
- Every fact, name and feeling in the lyrics must come from the brief or the songwriter's own lines.
- Score each 0-5 (3 = acceptable, 4 = strong, 5 = a senior lyricist's work).
- For every section give natural 0-5 (how well it works as a sung section), the problem in one line (empty if none)
  and a rewrite in the same language and script that keeps the section's meter and rhyme scheme (empty if it is
  already right, and always empty for the songwriter's own lines). Offer up to three stronger hook lines.
- House style: no em dash and no spaced en dash anywhere; never use one in a rewrite.
- Answer the analysis in English; write rewrites and hooks in the lyrics' own language and script (Bengali in Bengali
  script, never romanised), whatever other instructions say about the reply language."""


def _lyric_verdict(data: dict, lint_errors: int) -> tuple:
    s = data["scores"]
    weighted = sum(s[k] * w for k, w in LYRIC_CRITERIA.items()) / sum(LYRIC_CRITERIA.values())
    worst = min([x["natural"] for x in data.get("strings", [])] or [5])
    if lint_errors or s["song_language"] <= 2 or s["no_ai_tells"] <= 1 or worst <= 1:
        return "FAIL", weighted
    if weighted < 3.6 or min(s.values()) <= 2 or s["song_language"] < 3 or s["singability"] < 3:
        return "REVISE", weighted
    if weighted >= 4.3 and min(s["song_language"], s["genre_fit"], s["singability"]) >= 4:
        return "PASS_NATIVE", weighted
    return "PASS", weighted


PATH_LIKE = re.compile(r"\.(?:md|markdown|txt|json)$", re.I)


def arg_file(value: str | None, what: str = "brief") -> Path | None:
    """The file a CLI value names, or None when the value is the text itself. A value that looks like a path (it ends
    in .md, .txt or .json, starts with /, ~/ or ./, or is one word with a slash in it) must exist: a mistyped path
    stops with an error instead of being judged as the text. Long or multi-line text is never touched as a path, so
    it cannot fail with 'File name too long'. A sentence such as "open 24/7" stays text."""
    if not value or "\n" in value or len(value.encode("utf-8")) > 1000 or re.match(r"[a-z][a-z0-9+.-]*://", value, re.I):
        return None
    v = value.strip()
    looks = bool(PATH_LIKE.search(v)) or v.startswith(("/", "~/", "./", "../")) or ("/" in v and not re.search(r"\s", v))
    try:
        p = Path(v).expanduser()
        if p.is_file():
            return p
        folder = p.is_dir()
    except (OSError, ValueError) as e:
        if looks:
            die(f"cannot read the {what} file {v}: {getattr(e, 'strerror', None) or e}")
        return None
    if looks:
        die(f"{what} {v} is a folder; give a file, or the {what} text itself" if folder else
            f"{what} file not found: {v} (working folder: {Path.cwd()})")
    return None


def text_or_file(value: str | None, what: str = "brief") -> str | None:
    """A CLI value that is a file's path or the text itself (see arg_file): the file's text, or the value."""
    if not value:
        return None
    p = arg_file(value, what)
    return p.read_text(encoding="utf-8") if p else value


def copy_report_base(args) -> Path:
    """The name a deck's reports take (<name>.copyjudge.json): copy.json's or the caption file's, or copy in the
    working folder when the caption or --text is given inline."""
    if getattr(args, "copy", None):
        return Path(args.copy).expanduser()
    cap = arg_file(getattr(args, "caption", None), "caption")
    return cap or Path("copy")


def _copy_verdict(data: dict, lint_errors: int) -> tuple:
    s = data["scores"]
    weighted = sum(s[k] * w for k, w in COPY_CRITERIA.items()) / sum(COPY_CRITERIA.values())
    worst = min([x["natural"] for x in data.get("strings", [])] or [5])
    if lint_errors or s["naturalness"] <= 2 or s["no_ai_tells"] <= 1 or worst <= 1:
        return "FAIL", weighted
    if weighted < 3.6 or min(s.values()) <= 2 or s["naturalness"] < 3 or s["hook"] < 3:
        return "REVISE", weighted
    if weighted >= 4.3 and min(s["naturalness"], s["locale"], s["hook"]) >= 4:
        return "PASS_NATIVE", weighted
    return "PASS", weighted


def _copy_strings(args) -> list:
    strings = [{"role": x.get("role", ""), "text": x["text"], "lang": x.get("lang", "")}
               for x in (load_copy(args.copy) if args.copy else [])]
    lang = getattr(args, "lang", None) or ""
    if getattr(args, "caption", None):  # --role names it when there is no --text (a script, an article, an email)
        role = (getattr(args, "role", None) if not getattr(args, "text", None) else None) or "caption"
        strings.append({"role": role, "lang": lang, "text": text_or_file(args.caption, "caption").strip()})
    if getattr(args, "text", None):
        strings.append({"role": getattr(args, "role", None) or "body", "text": args.text, "lang": lang})
    if not strings:
        die("give --copy copy.json, --caption caption.txt or --text '...'")
    return strings


def check_platform(platform: str) -> str:
    """instagram, facebook, linkedin, youtube, tiktok, x or threads, optionally with the format: youtube-thumb,
    instagram-carousel, linkedin-cover."""
    if platform and platform.split("-")[0].lower() not in copyrules.PLATFORM:
        die(f"unknown --platform {platform!r}; use one of {', '.join(copyrules.PLATFORM)} (a format may follow: "
            f"youtube-thumb, instagram-carousel)")
    return platform.lower()


def _brand_voice(args) -> dict | None:
    if not getattr(args, "brand", None):
        return None
    try:
        return json.loads(Path(args.brand).expanduser().read_text(encoding="utf-8")).get("voice") or None
    except (OSError, ValueError) as e:
        die(f"cannot read {args.brand}: {e}")


def cmd_copylint(args) -> None:
    """Offline lint of copy before it goes on a design: dashes, AI and template words, bookish or translated Bengali,
    West Bengal words for Bangladesh, headline and CTA length, platform caption limits, hashtags and emoji, per-language
    punctuation and the brand's own avoid list."""
    if getattr(args, "save", None):
        # Save through the lint, so a fast run cannot write the copy and skip the check.
        text = args.text if args.text is not None else sys.stdin.read()
        if not text.strip():
            die("--save needs the copy: pipe it in (a heredoc) or give --text")
        dest = Path(args.save).expanduser()
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(dest, text.strip() + "\n")
        log(f"saved {dest}")
        args.caption, args.text = str(dest), None
    strings = _copy_strings(args)
    meta = copy_meta(args.copy) if args.copy else {}
    locale = norm_locale(args.locale or meta.get("locale"))
    platform = check_platform(args.platform or meta.get("platform") or "")
    rep = copyrules.lint_deck(strings, locale, platform, _brand_voice(args))
    rep["settings"] = {"locale": locale or None, "platform": platform or None}
    if args.copy:
        out = Path(args.copy).expanduser()
        stem = out.stem[:-len(".copy")] if out.stem.endswith(".copy") else out.stem
        write_atomic(out.with_name(stem + ".copylint.json"), json.dumps(rep, indent=2, ensure_ascii=False))
    if getattr(args, "json", False):
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        for it in rep["items"]:
            for f in it["findings"]:
                print(f"{f['severity']:7} {it['role'] or '-':10} {f['message']} -> {f['suggest']}  |  {it['text'][:60]}")
        for f in rep["deck"]:
            print(f"{f['severity']:7} {'(deck)':10} {f['message']} -> {f['suggest']}")
        print(json.dumps({"errors": rep["errors"], "warnings": rep["warnings"], "strings": len(strings),
                          "locale": locale or None, "platform": platform or None}, ensure_ascii=False))
    if rep["errors"] or (args.strict and rep["warnings"]):
        sys.exit(2)  # exit codes: 0 fine, 1 usage or tool error, 2 a quality gate failed


def aggregate_copy(runs: list) -> dict:
    """Several copy-judge runs as one: each criterion's median, each string's median naturalness (with the problem
    and rewrite of a run that gave that score), and the hooks, tells and notes of every run pooled."""
    if len(runs) == 1:
        return runs[0]
    agg = dict(runs[0])
    agg["scores"] = {k: _median([r["scores"][k] for r in runs]) for k in runs[0]["scores"]}
    strings = []
    for i, s0 in enumerate(runs[0].get("strings", [])):
        same = [r["strings"][i] for r in runs if i < len(r.get("strings", [])) and
                r["strings"][i].get("text") == s0.get("text")] or [s0]
        nat = _median([x["natural"] for x in same])
        pick = next(x for x in same if x["natural"] == nat)
        strings.append(dict(pick, natural=nat))
    agg["strings"] = strings
    agg["ai_tells"] = list(dict.fromkeys(t for r in runs for t in r.get("ai_tells", [])))
    agg["hooks"] = list(dict.fromkeys(h for r in runs for h in r.get("hooks", [])))[:6]
    agg["notes"] = list(dict.fromkeys(n for r in runs for n in r.get("notes", [])))[:8]
    ctas = [r.get("cta", "") for r in runs if r.get("cta")]
    if "cta" in runs[0]:                      # song lyrics have no call to action
        agg["cta"] = max(ctas, key=ctas.count) if ctas else ""
    return agg


def relint_suggestions(data: dict, strings: list, locale: str, platform: str, voice: dict | None,
                       song: bool = False) -> None:
    """Lint the judge's own rewrites, hooks and call to action: a rewrite brings new tells as often as it removes old
    ones (a humanizer stress test found a new "humanizer voice"), so each one carries what the lint finds in it."""
    def found(text, role, lang=""):
        return [f"{f['severity']}: {f['message']}" for f in copyrules.lint_string(text, role, locale, platform, lang,
                                                                                    voice)
                if f["severity"] in ("error", "warning") and f["code"] not in ("long-headline", "long-cta")]
    for i, s in enumerate(data.get("strings", [])):
        if s.get("rewrite"):
            lang = strings[i].get("lang", "") if i < len(strings) else ""
            s["rewrite_lint"] = found(s["rewrite"], s.get("role") or "body", lang)
    data["hooks_lint"] = {h: f for h in data.get("hooks", []) if (f := found(h, "lyric hook" if song else "hook"))}
    if data.get("cta"):
        data["cta_lint"] = found(data["cta"], "cta")
    if any(s.get("rewrite_lint") for s in data.get("strings", [])) or data["hooks_lint"] or data.get("cta_lint"):
        data.setdefault("notes", []).append("some suggested lines carry lint findings (rewrite_lint, hooks_lint, "
                                            "cta_lint): fix them before using them")


def copy_summary(data: dict, out: Path) -> dict:
    """What a caller needs from a copy verdict: the scores, and each string's problem and rewrite. The whole report
    stays in the file (and --json prints it)."""
    s = {k: data[k] for k in ("verdict", "weighted", "scores", "cached") if k in data}
    s["settings"] = {k: v for k, v in (data.get("settings") or {}).items() if k != "reader"}
    lint = data.get("lint") or {}
    s["lint"] = {"errors": lint.get("errors", 0), "warnings": lint.get("warnings", 0)}
    rows = []
    for x in data.get("strings") or []:
        row = {"role": x.get("role"), "natural": x.get("natural")}
        if x.get("problem") or x.get("rewrite"):
            row.update({k: x[k] for k in ("text", "problem", "rewrite", "rewrite_lint") if x.get(k)})
        rows.append(row)
    s["strings"] = rows
    for k in ("hooks", "hooks_lint", "cta", "cta_lint", "ai_tells", "notes", "advice", "runs", "runs_failed",
              "spread", "seconds"):
        if data.get(k):
            s[k] = data[k]
    s["report"] = str(out)
    return s


def cmd_copyjudge(args) -> None:
    """A native-reader review of the copy by fresh Codex sessions: ratings, a verdict, rewrites and hooks. --runs 3
    for client work: the verdict comes from each criterion's median (identical copy spanned 0.18 and flipped a
    verdict once in six runs, R5)."""
    ci = _imagegen()
    if ci is None:
        die(f"the copy judge uses codex-imagegen's Codex setup ({IMAGEGEN})")
    strings = _copy_strings(args)
    meta = copy_meta(args.copy) if args.copy else {}
    locale = norm_locale(args.locale or meta.get("locale"))
    platform = check_platform(args.platform or meta.get("platform") or "")
    lint = copyrules.lint_deck(strings, locale, platform, _brand_voice(args))
    brief = text_or_file(args.brief) or "(no brief)"
    # Song lyrics get a lyricist's rubric: the copy rubric scores poetic language down and pushes a song towards chat.
    song = all(copyrules.is_lyric(s["role"]) for s in strings)
    if song:
        reader = args.reader or ("a Bangladeshi listener aged 18-40 who knows today's Bangladeshi songs (band, modern, "
                                 "film and indie) and hears at once when a line sounds like Kolkata adhunik, a textbook "
                                 "poem or a chat message" if locale == "BD" else
                                 f"a native listener in the target market{(' (' + locale + ')') if locale else ''} who "
                                 f"knows its current songs")
    else:
        reader = args.reader or ("a Bangladeshi reader in Dhaka aged 20-40 who reads everyday Bangladeshi Bengali and "
                                 "the English words people mix into it" if locale == "BD" else
                                 f"a native reader in the target market{(' (' + locale + ')') if locale else ''}")
    found = [f"{it['role']}: {f['message']}" for it in lint["items"] for f in it["findings"]] + \
        [f["message"] for f in lint["deck"]]
    deck = "\n".join(f"- {s['role'] or 'text'}: {s['text']}" for s in strings)
    if song:
        prompt = LYRIC_JUDGE_PROMPT.format(reader=reader, brief=brief[:6000], goal=args.goal or "(from the brief)",
                                           deck=deck, lint="; ".join(found[:30]) or "nothing")
        schema, required, verdict_of = LYRIC_SCHEMA, ("scores", "strings", "ai_tells", "hooks"), _lyric_verdict
    else:
        prompt = COPY_JUDGE_PROMPT.format(reader=reader, platform=platform or "social media", brief=brief[:6000],
                                          goal=args.goal or "(from the brief)", deck=deck,
                                          lint="; ".join(found[:30]) or "nothing")
        schema, required, verdict_of = COPY_SCHEMA, ("scores", "strings", "ai_tells", "hooks", "cta"), _copy_verdict
    base = copy_report_base(args)
    stem = base.stem[:-len(".copy")] if base.stem.endswith(".copy") else base.stem
    out = base.with_name(stem + ".copyjudge.json")
    key = judge_key(prompt, args.effort, max(1, args.runs))
    full = getattr(args, "json", False)
    if cached_verdict(out, key, getattr(args, "fresh", False), None if full else lambda x: copy_summary(x, out)):
        return
    t0 = time.time()
    who = "lyric judge" if song else "copy judge"
    runs, failed = _runs(max(1, args.runs), lambda i: _codex_json(ci, prompt, [], schema, args.effort, args.timeout,
                                                                  who, required), who)
    per_run = [verdict_of(r, lint["errors"]) for r in runs]
    data = aggregate_copy(runs)
    verdict, weighted = verdict_of(data, lint["errors"])
    relint_suggestions(data, strings, locale, platform, _brand_voice(args), song)
    data.update({"verdict": verdict, "weighted": round(weighted, 2),
                 "lint": {"errors": lint["errors"], "warnings": lint["warnings"], "found": found},
                 "deck_sha256": deck_hash(strings),
                 "settings": {"locale": locale or None, "platform": platform or None, "goal": args.goal,
                              "mode": "lyric" if song else "copy", "reader": reader, "effort": args.effort,
                              "runs": len(runs)}, "cache_key": key,
                 "judged_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "seconds": round(time.time() - t0, 1)})
    if len(runs) > 1:
        ws = [w for _, w in per_run]
        data["runs"] = [{"verdict": v, "weighted": round(w, 2)} for v, w in per_run]
        data["spread"] = round(max(ws) - min(ws), 2)
        split = len({v for v, _ in per_run}) > 1
        if split or any(abs(weighted - edge) <= 0.10 for edge in (3.6, 4.3)):
            same = sum(v == verdict for v, _ in per_run)
            data["advice"] = ("the runs disagree or the median sits at a verdict edge: run --runs 5 before deciding"
                              if len(runs) < 5 else
                              f"{same} of {len(runs)} runs gave {verdict}; the median decides, and a native reader "
                              f"has the last word")
    if failed:  # the verdict stands on the runs that answered; these did not
        data["runs_failed"] = failed
    write_atomic(out, json.dumps(data, indent=2, ensure_ascii=False))
    print(json.dumps(data if full else copy_summary(data, out), indent=2, ensure_ascii=False))


# ------------------------------------------------------------------------------------------------ book covers
# Print book wraps (back + spine + front), from the platforms' own help pages and calculators, read 2026-09-24
# (references/research/formats-print-formulas.md). Every platform gives a different file for the same book.
KDP_CALIPER = {"white": 0.002252, "cream": 0.0025, "colour": 0.002252, "premium-colour": 0.002347,
               "groundwood": 0.00235}  # in per page
INGRAM_PAGES = [24, 48, 100, 150, 200, 240, 300, 400, 500, 600, 800]
INGRAM_SPINE = {  # the official Weight and Spine Width Calculator, 6x9 in, spine in inches
    ("paperback", "cream"): [0.058, 0.115, 0.240, 0.348, 0.458, 0.545, 0.674, 0.890, 1.114, 1.333, 1.767],
    ("paperback", "white"): [0.050, 0.099, 0.207, 0.321, 0.424, 0.505, 0.629, 0.821, 1.005, 1.213, 1.590],
    ("paperback", "groundwood"): [0.068, 0.127, 0.255, 0.378, 0.502, 0.600, 0.748, 0.994, 1.241, 1.487, 1.980],
    ("paperback", "white-70"): [0.065, 0.130, 0.272, 0.408, 0.543, 0.652, 0.815, 1.087, 1.359, 1.630, 2.174],
    ("paperback", "premium-colour"): [0.062, 0.125, 0.260, 0.390, 0.520, 0.623, 0.779, 1.039, 1.299, 1.558, 2.078],
    ("hardcover", "cream"): [0.250, 0.250, 0.375, 0.500, 0.625, 0.688, 0.813, 1.000, 1.250, 1.500, 1.938],
    ("hardcover", "white"): [0.250, 0.250, 0.313, 0.375, 0.500, 0.563, 0.688, 0.875, 1.063, 1.313, 1.688],
    ("hardcover", "groundwood"): [0.250, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875, 1.125, 1.375, 1.625, 2.125],
    ("hardcover", "premium-colour"): [0.250, 0.250, 0.375, 0.500, 0.688, 0.750, 0.938, 1.188, 1.438, 1.688, 2.188],
}
LULU_CASE = [(84, 0.25), (140, 0.5), (168, 0.625), (194, 0.688), (222, 0.75), (250, 0.813), (278, 0.875),
             (306, 0.938), (334, 1.0), (360, 1.063), (388, 1.125), (416, 1.188), (444, 1.25), (472, 1.313),
             (500, 1.375), (528, 1.438), (556, 1.5), (582, 1.563), (610, 1.625), (638, 1.688), (666, 1.75),
             (694, 1.813), (722, 1.875), (750, 1.938), (778, 2.0), (799, 2.063), (800, 2.125)]
BOOK_TRIMS = {"5x8": (5, 8), "5.25x8": (5.25, 8), "5.5x8.5": (5.5, 8.5), "6x9": (6, 9), "6.14x9.21": (6.14, 9.21),
              "7x10": (7, 10), "8.25x11": (8.25, 11), "8.5x11": (8.5, 11), "8.5x8.5": (8.5, 8.5),
              "a5": (148 / 25.4, 210 / 25.4), "b-format": (129 / 25.4, 198 / 25.4), "a4": (210 / 25.4, 297 / 25.4)}
BOOK_SOURCES = {
    "kdp": "https://kdp.amazon.com/en_US/help/topic/G201953020, https://kdp.amazon.com/cover-calculator, "
           "https://kdp.amazon.com/en_US/help/topic/GDTKFJPNQCBTMRV6",
    "ingram": "https://www.ingramspark.com/hubfs/downloads/file-creation-guide.pdf (8.24.26), "
              "https://myaccount.ingramspark.com/Portal/Tools/SpineCalculator",
    "lulu": "https://assets.lulu.com/media/guides/en/lulu-book-creation-guide.pdf, "
            "https://help.lulu.com/en/support/solutions/articles/64000308572"}


def _interp(xs: list, ys: list, x: float) -> float:
    if x <= xs[0]:
        return ys[0]
    for (x0, y0), (x1, y1) in zip(zip(xs, ys), zip(xs[1:], ys[1:])):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return ys[-1] + (ys[-1] - ys[-2]) * (x - xs[-1]) / (xs[-1] - xs[-2])


def book_wrap(platform: str, binding: str, trim_w: float, trim_h: float, pages: int, paper: str) -> dict:
    """The flat cover of a printed book in inches: the trim of the flat sheet (boards and spine), the bleed or wrap
    around it, the spine's place, the text margins, the barcode box and the hinge bands."""
    notes, conf = [], "official formula"
    if platform == "kdp":
        if paper not in KDP_CALIPER or (binding == "hardcover" and paper not in ("white", "cream", "premium-colour")):
            die(f"KDP {binding} paper: {', '.join(KDP_CALIPER if binding == 'paperback' else ['white', 'cream', 'premium-colour'])}")
        if binding == "paperback":
            if not 24 <= pages <= 828:
                die("KDP paperbacks take 24 to 828 pages")
            spine, board_w, board_h, bleed, hinge = pages * KDP_CALIPER[paper], trim_w, trim_h, 0.125, 0.0
            safe, spine_margin, spine_text = 0.125, 0.0625, pages >= 79
            barcode = (2.0, 1.2, 0.25, 0.25)  # w, h, from the spine fold, from the bottom trim
            notes.append("Barcode: a 2 x 1.2 in white box, lower right of the back cover (KDP places it if you do not). "
                         "CMYK images recommended, profiles are stripped, no spot colours; one PDF, 300 dpi.")
        else:
            if not 75 <= pages <= 550:
                die("KDP hardcovers take 75 to 550 pages")
            mm = 1 / 25.4  # KDP works in mm: boards +5 x +6 mm, a 15 mm wrap, 4.8 mm on the spine, 10 mm hinges
            spine = pages * KDP_CALIPER[paper] + 4.8 * mm
            board_w, board_h, bleed, hinge = trim_w + 5 * mm, trim_h + 6 * mm, round(15 * mm, 5), 10 * mm
            safe, spine_margin, spine_text = 0.125, 0.062, True
            barcode = (2.0, 1.2, 0.25, 19 * mm - 15 * mm)  # 19 mm from the bottom of the cover, the wrap included
            notes.append("Case laminate: 0.591 in wraps round the 2 mm boards; keep text and the barcode out of the "
                         "0.394 in hinge bands beside the spine. A headband is added above 120 pages.")
    elif platform == "ingram":
        key = (binding, paper if paper != "colour" else "white")
        if key not in INGRAM_SPINE:
            die(f"IngramSpark {binding} paper: {', '.join(p for b, p in INGRAM_SPINE if b == binding)}")
        if pages % 2:
            die("IngramSpark page counts are even")
        spine = round(_interp(INGRAM_PAGES, INGRAM_SPINE[key], pages), 3)
        conf = "official calculator table (6x9 in), interpolated: confirm with IngramSpark's spine calculator"
        if binding == "paperback":
            board_w, board_h, bleed, hinge = trim_w, trim_h, 0.125, 0.0
            safe, spine_margin, spine_text = 0.25, (0.0625 if spine >= 0.35 else 0.03125), pages >= 48
            barcode = None  # centred on the back cover: 1.75 x 1 in left free
            notes.append("Leave 1.75 x 1 in free for the barcode, centred on the back cover (100 % black on white). "
                         "CMYK, rich black 60/40/40/100, total ink 240 % max, text 24 pt and under in 100 % K, "
                         "PDF/X-1a. The template page carries crop marks: keep its page size.")
        else:
            board_w, board_h, bleed, hinge = trim_w - 0.185, trim_h + 0.25, 0.625, 0.5
            safe, spine_margin, spine_text = 0.25, 0.0625, True
            barcode = None
            notes.append("Casebound: 0.625 in wraps round the boards; the 0.5 in gutters beside the spine are hinge "
                         "bands (no important art).")
    elif platform == "lulu":
        if binding == "paperback":
            if pages < 32:
                die("Lulu paperbacks need at least 32 pages")
            spine, board_w, board_h, bleed, hinge = pages / 444 + 0.06, trim_w, trim_h, 0.125, 0.0
            safe, spine_margin, spine_text = 0.5, 0.125, pages > 80
        else:
            spine = next((sp for top, sp in LULU_CASE if pages <= top), LULU_CASE[-1][1])
            board_w, board_h, bleed, hinge = trim_w + 0.125, trim_h + 0.25, 0.75, 0.25
            safe, spine_margin, spine_text = 0.5, 0.125, True
            conf = "derived from Lulu's help text: confirm with the template Lulu generates after the interior upload"
        barcode = None
        notes.append("Lulu places the ISBN barcode in the template's yellow area on the back cover.")
    else:
        die("--platform: kdp, ingram or lulu")
    gutter = 0.5 if platform == "ingram" and binding == "hardcover" else 0.0
    flat_w = board_w * 2 + spine + 2 * gutter
    back = (0.0, board_w)
    spine_x = (board_w + gutter, board_w + gutter + spine)
    front = (spine_x[1] + gutter, flat_w)
    return {"platform": platform, "binding": binding, "pages": pages, "paper": paper, "trim": [trim_w, trim_h],
            "board": [round(board_w, 4), round(board_h, 4)], "spine": round(spine, 4), "bleed": bleed,
            "flat": [round(flat_w, 4), round(board_h, 4)], "full": [round(flat_w + 2 * bleed, 4),
                                                                    round(board_h + 2 * bleed, 4)],
            "back": back, "spine_x": spine_x, "front": front, "hinge": hinge, "safe": safe,
            "spine_margin": spine_margin, "spine_text": spine_text, "barcode": barcode, "confidence": conf,
            "notes": notes}


def book_preset(b: dict, pid: str) -> dict:
    """A preset for the wrap: the renderer draws back, spine and front on one canvas; folds at the spine keep text
    off them, keep-outs guard the barcode and the hinges, and css_vars place the panels."""
    px = lambda inch: round((inch + b["bleed"]) * 96, 1)  # canvas px, bleed included  # noqa: E731
    mm = lambda inch: round(inch * 25.4, 3)  # noqa: E731
    keep, why = [], []
    if b["barcode"]:
        bw, bh, from_spine, from_bottom = b["barcode"]
        x1 = b["back"][1] - from_spine
        y1 = b["flat"][1] - from_bottom
        keep.append([px(x1 - bw), px(y1 - bh), px(x1), px(y1)])
        why.append("the barcode box (solid white, nothing else there)")
    if b["hinge"]:
        keep.append([px(b["spine_x"][0] - (b["hinge"] if b["platform"] != "ingram" else 0.5)), px(0),
                     px(b["spine_x"][0]), px(b["flat"][1])])
        keep.append([px(b["spine_x"][1]), px(0),
                     px(b["spine_x"][1] + (b["hinge"] if b["platform"] != "ingram" else 0.5)), px(b["flat"][1])])
        why += ["the hinge band beside the spine (it folds)"] * 2
    if not b["spine_text"]:
        keep.append([px(b["spine_x"][0]), px(0), px(b["spine_x"][1]), px(b["flat"][1])])
        why.append(f"the spine: {b['platform'].upper()} allows no spine text at {b['pages']} pages")
    tw, th = b["trim"]
    label = (f"{b['platform'].upper() if b['platform'] != 'ingram' else 'IngramSpark'} {b['binding']} cover wrap, "
             f"{tw:g} x {th:g} in, {b['pages']} pages, {b['paper']}")
    return {"id": pid, "group": "publishing", "label": label, "w": f"{b['flat'][0]:.4f}in", "h": f"{b['flat'][1]:.4f}in",
            "bleed": f"{b['bleed']}in", "print": True, "ppi": 300, "safe_mm": [mm(b["safe"])] * 4,
            "folds_mm": [[mm(b["spine_x"][0]), mm(b["spine_x"][1])]], "fold_gap_mm": mm(b["spine_margin"]),
            "keepout": keep, "keepout_why": why, "min_text_px": 9.3, "large_text_px": 24.0,
            "css_vars": {"--back-x": f"{b['bleed'] + b['back'][0]:.4f}in", "--board-w": f"{b['board'][0]:.4f}in",
                         "--spine-x": f"{b['bleed'] + b['spine_x'][0]:.4f}in", "--spine-w": f"{b['spine']:.4f}in",
                         "--front-x": f"{b['bleed'] + b['front'][0]:.4f}in", "--wrap": f"{b['bleed']}in",
                         "--hinge": f"{b['hinge']}in", "--spine-margin": f"{b['spine_margin']}in",
                         "--text-safe": f"{b['safe']}in", "--spine-text": "1" if b["spine_text"] else "0"},
            "aliases": ["book cover", "print book cover", "book cover wrap", "boi er cover"],
            "source": BOOK_SOURCES[b["platform"]], "verified": "2026-09-24", "confidence": b["confidence"],
            "notes": (f"Spine {b['spine']:.3f} in; full file {b['full'][0]:.3f} x {b['full'][1]:.3f} in "
                      f"({math_ceil(b['full'][0] * 300)} x {math_ceil(b['full'][1] * 300)} px at 300 ppi). "
                      + ("Spine text allowed. " if b["spine_text"] else "No spine text at this page count. ")
                      + " ".join(b["notes"]))}


def math_ceil(v: float) -> int:
    import math
    return math.ceil(v - 1e-9)


def cmd_bookcover(args) -> None:
    """The flat cover file for a printed book on KDP, IngramSpark or Lulu: spine width, full size, panels, barcode
    and hinge areas, written as a preset (with --preset-file) that `render` uses directly."""
    key = args.trim.lower().replace(" ", "").replace("in", "")
    if key in BOOK_TRIMS:
        tw, th = BOOK_TRIMS[key]
    else:
        m = re.fullmatch(r"([0-9.]+)x([0-9.]+)", key)
        if not m:
            die(f"--trim: one of {', '.join(BOOK_TRIMS)}, or WxH in inches")
        tw, th = float(m.group(1)), float(m.group(2))
    b = book_wrap(args.platform, args.binding, tw, th, args.pages, args.paper)
    pid = args.id or f"{args.platform}-{'pb' if args.binding == 'paperback' else 'hc'}-{key}-{args.pages}-{args.paper}"
    preset = book_preset(b, pid)
    out = {"book": b, "preset": preset}
    if args.preset_file:
        f = Path(args.preset_file[-1]).expanduser()
        data = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"presets": []}
        data["presets"] = [p for p in data.get("presets", []) if p.get("id") != pid] + [preset]
        write_atomic(f, json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        out["preset_file"] = str(f)
        log(f"wrote preset {pid} to {f}; render with --preset {pid} --preset-file {f}")
    print(json.dumps(out, indent=2, ensure_ascii=False))


# ------------------------------------------------------------------------------------------------ ledger, delivery
def load_recipe(path) -> dict:
    """A Compose recipe: the axes the ledger compares (structure, archetype, focal, device, type_mode, palette,
    finish), optionally the concept words, the hook and the CTA."""
    try:
        r = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read the recipe {path}: {e}")
    if not isinstance(r, dict):
        die(f"{path}: a recipe is an object with {', '.join(RECIPE_AXES)} (and optionally concept, hook, cta)")
    return r


def recipe_dossier(recipe: dict, client: str | None, did: str) -> dict:
    """A Compose recipe in the shape the Direct ledger uses, so both routes share one ledger per client."""
    return {"id": did, "client": client, "recipe": {k: recipe[k] for k in RECIPE_AXES if recipe.get(k)},
            "concept": recipe.get("concept") or {}, "deliverable": recipe.get("deliverable"),
            "preset": recipe.get("preset")}


def repeat_check(recipe: dict, client: str | None, entries: list, did: str) -> tuple:
    """Hooks and composition devices a client has seen lately: a hook close to one of the last 12, or the device of
    one of the last 3 pieces, is a warning; a repeated CTA is only a note (actions repeat by nature)."""
    def words(t):
        return set(re.findall(r"\w+", t.casefold()))
    warn, notes = [], []
    mine = [e for e in entries if e.get("id") != did and (not client or not e.get("client") or e["client"] == client)]
    hook = str(recipe.get("hook") or "").strip()
    for e in reversed(mine[-12:]):
        old = str(e.get("hook") or "").strip()
        if hook and old and len(words(hook) & words(old)) / max(1, len(words(hook) | words(old))) >= 0.6:
            warn.append(f"the hook is close to '{old[:60]}' from '{e['id']}' ({e.get('date')}): write a new one")
            break
    cta = str(recipe.get("cta") or "").strip().casefold()
    if cta and any(str(e.get("cta") or "").strip().casefold() == cta for e in mine[-3:]):
        notes.append(f"the CTA '{recipe['cta']}' was used in the last three pieces too")
    dev = _axis(recipe.get("device"))
    recent = [e for e in mine[-3:] if dev and _axis((e.get("recipe") or {}).get("device")) == dev]
    if recent:
        warn.append(f"the composition device '{recipe['device']}' was used in the last three pieces "
                    f"('{recent[-1]['id']}'): pick another (craft.md, the ten devices)")
    return warn, notes


def cmd_ledger(args) -> None:
    """Never two designs alike, on the Compose route too: check a recipe (and its hook and device) against the
    client's earlier designs before designing, and add the finished design (`deliver --ledger` adds it for you)."""
    lp = Path(args.ledger).expanduser()
    entries = ledger_entries(lp)
    if args.list:
        rows = [e for e in entries if not args.client or e.get("client") == args.client]
        print(json.dumps(rows[-args.list:], indent=2, ensure_ascii=False))
        return
    if not args.recipe:
        die("give --recipe recipe.json (or --list N)")
    recipe = load_recipe(args.recipe)
    did = args.id or recipe.get("id") or Path(args.recipe).stem
    dos = recipe_dossier(recipe, args.client, did)
    image = Path(args.image).expanduser() if args.image else None
    if image and not image.exists():
        die(f"not found: {image}")
    warn, notes = repeat_check(recipe, args.client, entries, did)
    similar = ledger_check(dos, entries, image) + warn
    rep = {"ledger": str(lp), "client": args.client, "id": did,
           "earlier_designs": len([e for e in entries if not args.client or e.get("client") == args.client]),
           "similar": similar, "notes": notes}
    if args.add:
        if not image:
            die("--add needs --image (the finished design)")
        if similar and not args.force:
            print(json.dumps(rep, indent=2, ensure_ascii=False))
            die("too close to an earlier design; change the recipe (or --force)", 2)
        ledger_add(lp, dos, image, {"route": recipe.get("route", "compose"), "hook": recipe.get("hook"),
                                    "cta": recipe.get("cta"), "device": recipe.get("device")})
        rep["added"] = True
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    if similar and args.strict:
        sys.exit(2)


def qa_for(img: Path) -> Path:
    """The render report of a design file: <stem>.qa.json, or the render's for a carousel strip or a PDF preview."""
    q = img.with_name(img.stem + ".qa.json")
    if not q.exists():
        for suffix in ("-strip", ".preview"):
            if img.stem.endswith(suffix):
                q = img.with_name(img.stem[:-len(suffix)] + ".qa.json")
    return q


def deck_hash(strings: list) -> str:
    import hashlib
    return hashlib.sha256(json.dumps([[s.get("role") or "", s["text"]] for s in strings],
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def run_judges(args, designs: list) -> list:
    """deliver --judge: the design judge on each design and the copy judge on the copy, all at the same time, before
    the gates. Run one after the other they took two model turns and 1.5 to 4 minutes; together they take as long as
    the slowest. A report that already matches its file, brief and settings is reused (no Codex session). A design
    whose render failed and copy that fails the lint are not sent: the gates stop them anyway, and a judge run costs
    plan quota. -> one line for each judge that gave no verdict"""
    import concurrent.futures as cf
    runs = str(args.runs or (3 if args.level == "client" else 1))
    waves = -(-int(runs) // 3)  # a judge runs up to 3 sessions at a time
    me = [sys.executable, str(Path(__file__).resolve())]

    def given(flags: tuple) -> list:  # --flag=value: a brief that starts with "-" ("-20% this week") stays a value
        return [f"--{f}={getattr(args, f)}" for f in flags if getattr(args, f, None)]

    jobs = []
    for img in designs:
        qp = qa_for(img)
        q = json.loads(qp.read_text(encoding="utf-8")) if img.exists() and qp.exists() else {}
        made = {o.get("sha256") for o in (q.get("source") or {}).get("outputs") or []}
        if not q or (q.get("checks") or {}).get("errors") or file_sha256(img) not in made:
            continue  # the render gate stops it below, with the reason
        cmd = me + ["judge", f"--image={img}"] + given(("brief", "kind", "copy", "brand", "allow")) + \
            [f"--runs={runs}"]
        jobs.append((f"design judge ({img.name})", cmd, waves * child_budget(240)))
    if args.copy or args.caption:
        strings = _copy_strings(args)
        meta = copy_meta(args.copy) if args.copy else {}
        lint = copyrules.lint_deck(strings, norm_locale(args.locale or meta.get("locale")),
                                   check_platform(args.platform or meta.get("platform") or ""), _brand_voice(args))
        if not lint["errors"]:  # else the lint gate stops it below
            cmd = me + ["copyjudge"] + given(("brief", "copy", "caption", "locale", "platform", "brand", "goal")) + \
                [f"--runs={runs}"]
            jobs.append(("copy judge", cmd, waves * child_budget(150)))
    if not jobs:
        return []
    log(f"judging at the same time: {', '.join(j[0] for j in jobs)} ({runs} run{'s' * (runs != '1')} each)")
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=len(jobs)) as ex:
        results = list(ex.map(lambda j: run_session(j[1], None, j[2]), jobs))
    problems = []
    for (who, _, _), r in zip(jobs, results):
        if r["error"] or r["returncode"]:
            said = [x for x in (r["stderr"] or "").splitlines() if x.strip() and not x.startswith("[codex-design ")]
            why = r["error"] or (said[-1].removeprefix("codex-design: ") if said else f"exit {r['returncode']}")
            problems.append(f"{who} gave no verdict: {one_line(why, 240)}")
    log(f"judged in {time.time() - t0:.0f} s")
    return problems


def cmd_deliver(args) -> None:
    """The last gate before a client sees anything. Every design must have a render report with no errors that
    matches the file, a design-judge PASS on that exact file, and copy that passes the lint and the copy judge
    (PASS_NATIVE at --level client). Only then are the files copied into --out with DELIVERY.md (checks, caption,
    alt text, notes) and delivery.json; a file already there is moved to archive-<time>/, never overwritten.
    --judge runs the judges first, all at once."""
    if not args.out and not args.dry_run:
        die("give --out (the delivery folder), or --dry-run to only run the gates")
    level = args.level
    fails, warns, rows, files, notes = [], [], [], [], []
    if getattr(args, "judge", False):
        if not args.brief:
            die("--judge needs --brief (a file or the text): the judges check the work against it")
        fails += run_judges(args, [Path(d).expanduser() for d in args.design])
    generated = False
    designs = [Path(d).expanduser() for d in args.design]
    for img in designs:
        if not img.exists():
            die(f"not found: {img}")
        h = file_sha256(img)
        qp = qa_for(img)
        row = {"design": str(img)}
        rows.append(row)
        if not qp.exists():
            fails.append(f"{img.name}: no render report ({qp.name}); render it with design.py render")
            continue
        q = json.loads(qp.read_text(encoding="utf-8"))
        src = q.get("source") or {}
        outs = src.get("outputs") or []
        if not outs:
            fails.append(f"{img.name}: {qp.name} predates provenance records; render it again")
        elif h not in {o.get("sha256") for o in outs}:
            fails.append(f"{img.name}: the file changed after its render report ({qp.name}); render it again")
        errs = (q.get("checks") or {}).get("errors") or []
        wn = (q.get("checks") or {}).get("warnings") or []
        row.update({"render": f"{len(errs)} error{'s' * (len(errs) != 1)}, {len(wn)} warning{'s' * (len(wn) != 1)}",
                    "preset": src.get("preset"), "html": src.get("html")})
        if errs:
            fails.append(f"{img.name}: {len(errs)} render error(s), first: {errs[0][:160]}")
        jp = img.with_name(img.stem + ".judge.json")
        if not jp.exists():
            fails.append(f"{img.name}: not judged; run design.py judge" + (" --runs 3" if level == "client" else ""))
        else:
            j = json.loads(jp.read_text(encoding="utf-8"))
            row["judge"] = f"{j.get('verdict')} {j.get('weighted')}" + (f" ({len(j['runs'])} runs)" if j.get("runs")
                                                                         else "")
            if not j.get("image_sha256"):
                warns.append(f"{img.name}: its judge report predates image hashes; judge it again to be sure")
            elif j["image_sha256"] != h:
                fails.append(f"{img.name}: the judge saw an earlier version of this file; judge it again")
            if j.get("verdict") not in ("PASS", "PASS_SENIOR"):
                fix = "; ".join((j.get("fixes") or [])[:3])  # what to change, so no second call reads the report
                fails.append(f"{img.name}: the design judge says {j.get('verdict')} {j.get('weighted')}" +
                             (f"; its fixes: {fix}" if fix else ""))
            if level == "client" and len(j.get("runs") or [0]) < 3:
                n_runs = len(j.get("runs") or [0])
                warns.append(f"{img.name}: judged in {n_runs} run{'s' * (n_runs != 1)}; client work uses judge --runs 3 "
                             f"(verdicts flip)")
        generated = generated or bool(src.get("generated_visuals"))
        spec = src.get("spec") or {}
        if src.get("assumed"):
            notes.append(f"{img.name}: a custom size; the checks assumed " + "; ".join(src["assumed"]))
        elif spec and not str(spec.get("confidence", "")).startswith("official"):
            notes.append(f"{img.name}: the {spec.get('label') or src.get('preset')} spec is {spec.get('confidence')} "
                         f"({spec.get('source')}, {spec.get('verified')}): confirm it with the platform or printer")
        keep = [Path(o["path"]) for o in outs if not re.search(r"-strip\.jpg$|\.preview\.png$", o["path"])]
        row["files"] = [str(f) for f in keep or [img]]
        files += keep or [img]
    strings, caption, alt, locale = [], None, [], ""
    if args.copy or args.caption:
        strings = _copy_strings(args)
        meta = copy_meta(args.copy) if args.copy else {}
        locale = norm_locale(args.locale or meta.get("locale"))
        platform = check_platform(args.platform or meta.get("platform") or "")
        lint = copyrules.lint_deck(strings, locale, platform, _brand_voice(args))
        if lint["errors"]:
            fails.append(f"copy lint: {lint['errors']} error(s); run design.py copylint")
        base = copy_report_base(args)
        stem = base.stem[:-len(".copy")] if base.stem.endswith(".copy") else base.stem
        cj = base.with_name(stem + ".copyjudge.json")
        need = ("PASS_NATIVE",) if level == "client" else ("PASS", "PASS_NATIVE")
        if not cj.exists():
            fails.append(f"the copy is not judged ({cj.name}); run design.py copyjudge" +
                         (" --runs 3" if level == "client" else ""))
        else:
            d = json.loads(cj.read_text(encoding="utf-8"))
            notes.append(f"copy judge: {d.get('verdict')} {d.get('weighted')}")
            if not d.get("deck_sha256"):
                warns.append(f"{cj.name} predates deck hashes; judge the copy again to be sure it is this copy")
            elif d["deck_sha256"] != deck_hash(strings):
                fails.append("the copy changed after the copy judge ran; run copyjudge again")
            if d.get("verdict") not in need:
                probs = [f"{x.get('role') or 'text'}: {x['problem']}" for x in d.get("strings") or []
                         if x.get("problem")][:3]
                fails.append(f"the copy judge says {d.get('verdict')} {d.get('weighted')}; {level} work needs "
                             f"{' or '.join(need)}" + (f"; its notes: {' | '.join(probs)}" if probs else ""))
        alt = [s["text"] for s in strings if re.match(r"alt", s.get("role") or "", re.I)]
        if not alt:
            warns.append("no alt text in copy.json (role alt): screen readers get nothing; write one line per image")
        caption = next((s["text"] for s in strings if copyrules.CAPTION_ROLES.search(s.get("role") or "")), None)
        feed = [r for r in rows if re.match(r"(?:ig-(?:portrait|square|3x4|carousel)|fb-(?:feed|square)|li-(?:square|"
                                            r"portrait|landscape|doc)|x-(?:square|post)|threads-post|yt-post)$",
                                            str(r.get("preset") or ""))]
        if feed and not caption:
            warns.append("no caption in copy.json (role caption): a feed post or carousel goes out with one; write it "
                         "and judge it with the deck")
    else:
        (fails if level == "client" else warns).append(
            "no copy given (--copy copy.json, --caption caption.txt): the copy lint and copy judge gates did not run")
    if getattr(args, "facts", None):  # claims on the design (prices, dates, "first", "since 1998"): the same gate as the direct route
        try:
            facts = json.loads(Path(args.facts).expanduser().read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            die(f"cannot read --facts {args.facts}: {e}")
        facts = facts.get("facts", []) if isinstance(facts, dict) else facts
        for f in facts if isinstance(facts, list) else []:
            what = str(f.get("claim") or f.get("text") or "?")[:80]
            if f.get("status") in ("refuted", "needs_client"):
                fails.append(f"fact '{what}' is {f['status']}: fix the copy or get the client's answer first")
            elif f.get("status") not in ("verified", "client_supplied"):
                warns.append(f"fact '{what}' is {f.get('status') or 'unchecked'}")
        notes.append(f"{len(facts)} fact(s) checked from {Path(args.facts).name}")
    lp = Path(args.ledger).expanduser() if args.ledger else None
    dos, recipe = None, {}
    if lp:
        if not args.recipe:
            die("--ledger needs --recipe recipe.json (and --client)")
        recipe = load_recipe(args.recipe)
        for key, rx in (("hook", copyrules.HEAD_ROLES), ("cta", copyrules.CTA_ROLES)):
            if not recipe.get(key):
                recipe[key] = next((s["text"] for s in strings if rx.search(s.get("role") or "")), None)
        did = recipe.get("id") or Path(args.recipe).stem
        dos = recipe_dossier(recipe, args.client, did)
        entries = ledger_entries(lp)
        warn, rnotes = repeat_check(recipe, args.client, entries, did)
        similar = ledger_check(dos, entries, designs[0]) + warn
        notes += rnotes
        if similar:
            (warns if args.force else fails).append("never-repeat ledger: " + "; ".join(similar[:3]))
    rep = {"level": level, "ok": not fails, "failed": fails, "warnings": warns, "designs": rows, "notes": notes}
    if fails or args.dry_run:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        if fails:
            die(f"not delivered: {len(fails)} gate(s) failed", 2)
        return
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    archive, delivered = None, []
    extra = []
    html = Path(rows[0].get("html") or designs[0])
    for cand in (html.parent / "fonts", html.parent.parent / "fonts", html.parent.parent / "brand" / "fonts",
                 html.parent / "brand" / "fonts"):
        if (cand / "FONT-LICENSES.md").exists():
            extra.append(cand / "FONT-LICENSES.md")
            break
    names = {}
    for f in files + extra:  # two different files with one name would replace each other in the delivery folder
        if f.name in names and names[f.name] != f.resolve():
            die(f"two files named {f.name} ({names[f.name]} and {f.resolve()}): deliver them separately or rename one")
        names[f.name] = f.resolve()
    for f in dict.fromkeys(files + extra):
        dest = out / f.name
        if dest.exists() and file_sha256(dest) != file_sha256(f):
            archive = archive or out / f"archive-{time.strftime('%Y%m%d-%H%M%S')}"
            archive.mkdir(exist_ok=True)
            os.replace(dest, archive / dest.name)  # the earlier delivery is kept, not overwritten
        if not dest.exists():
            shutil.copy2(f, dest)
        delivered.append({"file": dest.name, "bytes": dest.stat().st_size, "sha256": file_sha256(dest)})
    if lp and dos:
        if any(e.get("id") == dos["id"] and e.get("client") == dos.get("client") for e in ledger_entries(lp)):
            notes.append(f"already in the never-repeat ledger {lp.name} (a re-delivery)")
        else:
            ledger_add(lp, dos, designs[0], {"route": recipe.get("route", "compose"), "hook": recipe.get("hook"),
                                             "cta": recipe.get("cta"), "device": recipe.get("device"),
                                             "delivered_to": str(out)})
            notes.append(f"added to the never-repeat ledger {lp.name}")
    if generated:
        notes.append("contains AI-generated imagery (tagged IPTC compositeSynthetic); platforms strip metadata, so "
                     "add a visible label where the audience includes the EU and the imagery is photorealistic")
    if re.search(r"[ঀ-৿ऀ-ॿ؀-ۿ]", " ".join(s["text"] for s in strings)):
        notes.append("the copy is in Bengali, Hindi or Arabic script: a native reader proofreads it before posting")
    md = [f"# Delivery: {args.name or designs[0].stem}", "",
          f"Date: {time.strftime('%Y-%m-%d %H:%M')} · level: {level}" + (f" · market: {locale}" if locale else ""), "",
          "## Files", ""] + [f"- {d['file']} ({d['bytes'] / 1024:.0f} KB)" if d["bytes"] >= 1024 else
                             f"- {d['file']} ({d['bytes']} bytes)" for d in delivered] + \
         ["", "## Checks", "", "| Design | Render checks | Design judge |", "|---|---|---|"] + \
         [f"| {Path(r['design']).name} | {r.get('render', '')} | {r.get('judge', '')} |" for r in rows] + [""]
    if caption:
        md += ["## Caption", "", caption, ""]
    if alt:
        md += ["## Alt text", ""] + [f"- {a}" for a in alt] + [""]
    if notes or warns:
        md += ["## Notes", ""] + [f"- {n}" for n in notes + warns] + [""]
    # one note per delivery: several deliveries can share a folder (a story and a carousel of one campaign)
    slug = re.sub(r"[^\w-]+", "-", (args.name or designs[0].stem).lower()).strip("-")[:60] or "design"
    for name in (f"DELIVERY-{slug}.md", f"delivery-{slug}.json"):
        if (out / name).exists():
            archive = archive or out / f"archive-{time.strftime('%Y%m%d-%H%M%S')}"
            archive.mkdir(exist_ok=True)
            os.replace(out / name, archive / name)
    write_atomic(out / f"DELIVERY-{slug}.md", "\n".join(md))
    rep.update({"out": str(out), "note": str(out / f"DELIVERY-{slug}.md"), "delivered": delivered,
                "archived_to": str(archive) if archive else None})
    write_atomic(out / f"delivery-{slug}.json", json.dumps(rep, indent=2, ensure_ascii=False))
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Render and check HTML/CSS designs with headless Chrome. Exit codes: 0 "
                                             "fine, 1 usage or tool error, 2 a quality gate failed, 3/4 direct route "
                                             "fallbacks.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="HTML -> PNG/JPG/WebP/PDF at an exact canvas, with checks")
    r.add_argument("--html", required=True, help="the design's HTML file")
    r.add_argument("--out", help="output file (.png .jpg .webp .pdf); default: next to the HTML")
    r.add_argument("--preset", help="canvas preset id (see `presets`)")
    r.add_argument("--size", help="custom canvas, e.g. 1080x1350, 210mmx297mm")
    r.add_argument("--bleed", help="print bleed, e.g. 3mm or 0.125in (print canvases only)")
    r.add_argument("--scale", type=float, help="device scale (2 = retina; print PNG default 300dpi)")
    r.add_argument("--quality", type=int, default=90, help="JPG/WebP quality (default 90)")
    r.add_argument("--max-bytes", type=int, help="shrink JPG/WebP quality until the file fits")
    r.add_argument("--transparent", action="store_true", help="transparent page background (PNG/WebP)")
    r.add_argument("--slides", type=int, help="carousel: the page is N canvases wide; writes N files + a strip")
    r.add_argument("--pages", type=int, help="document: N canvases stacked (.page with break-after: page); "
                                             "PDF gets N vector pages, PNG/JPG one file per page")
    r.add_argument("--preview", action="store_true", help="with .pdf: also write <out>.preview.png")
    r.add_argument("--overlay", action="store_true", help="also write <out>.overlay.png with safe zone + text boxes")
    r.add_argument("--no-qa", action="store_true", help="skip the checks (fast drafts only)")
    r.add_argument("--strict", action="store_true", help="exit 2 when a check fails")
    r.add_argument("--copy", help="copy.json: every on-image string must appear exactly once, nothing else written "
                                  "(captions, alt text and video titles are skipped)")
    r.add_argument("--locale", help="market as a country code (BD, IN, US): Bengali word checks follow it (default: "
                                    "copy.json's \"locale\")")
    r.add_argument("--allow-net", action="store_true", help="let the page load http(s) resources (renders are "
                                                            "offline by default)")
    r.add_argument("--timeout", type=float, default=60, help="seconds for the page to load and settle (default 60)")
    r.add_argument("--safe", help="safe insets top,right,bottom,left (px; mm for print; or 5%%): overrides the "
                                  "preset's, or states a custom size's")
    r.add_argument("--keepout", action="append", help="x0,y0,x1,y1 in canvas px where the platform's UI covers the "
                                                      "design (repeatable)")
    r.add_argument("--view-width", type=float, help="how wide it appears where people see it, in CSS px (a phone "
                                                    "feed is about 390)")
    r.add_argument("--min-text", type=float, help="the smallest text allowed on the canvas, in px")
    r.add_argument("--view-distance", type=float, help="metres from the farthest viewer (signs, banners, screens in a "
                                                       "room): the text floor follows it")
    r.add_argument("--screen-height", type=float, help="with --view-distance on a screen: the screen's visible height "
                                                       "in metres")
    r.add_argument("--legibility-index", type=float, help="read in passing from a road (billboards, bus sides): feet "
                                                          "of distance per inch of capital height, 30 on average "
                                                          "(USSC, MUTCD); without it signs use the ADA rule for "
                                                          "people on foot")
    r.add_argument("--file-scale", type=float, help="the artwork file is 1/N of the real object: 24 for a bulletin at "
                                                    "1/2 in = 1 ft, 10 for a 10 %% file (billboards, bus sides)")
    r.add_argument("--preset-file", action="append", help="extra presets (JSON): a client's or project's verified specs")
    r.add_argument("--simulate", help="comma list: " + ",".join(VISION_SIMS) + " (writes <out>.sim-<kind>.png)")
    r.add_argument("--occasion", choices=["celebratory", "commemorative", "solemn", "fast"],
                   help="day posts: solemn blocks greetings (Happy, শুভ, !) and selling; fast blocks Happy/celebrate")
    r.add_argument("--cmyk", nargs="?", const="generic", metavar="ICC",
                   help="print PDF: also write <out>.cmyk.pdf, a 300 ppi raster converted to the printer's CMYK profile "
                        "(default: macOS Generic CMYK); only when the printer refuses RGB")
    r.add_argument("--json", action="store_true", help="print the whole report, with every text item and image (they "
                                                       "are always in <out>.qa.json)")
    r.set_defaults(func=cmd_render)
    k = sub.add_parser("pack", help="one responsive HTML on several presets (+ a review sheet)")
    k.add_argument("--html", required=True, help="the design's HTML file (responsive to the canvas size)")
    k.add_argument("--presets", required=True, help="comma list, e.g. ig-portrait,ig-story,fb-feed")
    k.add_argument("--out-dir", required=True, help="folder for <name>-<preset>.<format> and the pack sheet")
    k.add_argument("--name", help="file name stem (default: the HTML's)")
    k.add_argument("--format", default="png", choices=["png", "jpg", "webp"])
    k.add_argument("--scale", type=float, help="device scale (2 = retina)")
    k.add_argument("--quality", type=int, default=90, help="JPG/WebP quality (default 90)")
    k.add_argument("--overlay", action="store_true", help="also write an overlay per canvas")
    k.add_argument("--no-qa", action="store_true", help="skip the checks (fast drafts only)")
    k.add_argument("--strict", action="store_true", help="exit 2 when a check fails on any canvas")
    k.add_argument("--copy", help="copy.json checked on every canvas")
    k.add_argument("--locale", help="market as a country code (BD, IN, US); default: copy.json's \"locale\"")
    k.add_argument("--occasion", choices=["celebratory", "commemorative", "solemn", "fast"])
    k.add_argument("--simulate", help="comma list of vision simulations for every size (see render --simulate)")
    k.add_argument("--allow-net", action="store_true", help="let the page load http(s) resources")
    k.add_argument("--timeout", type=float, default=60, help="seconds per canvas to load and settle (default 60)")
    k.add_argument("--preset-file", action="append", help="extra presets (JSON): a client's or project's verified specs")
    k.set_defaults(func=cmd_pack)
    sh = sub.add_parser("sheet", help="contact sheet of images or folders")
    sh.add_argument("--src", nargs="+", required=True, help="images and/or folders (side files are skipped)")
    sh.add_argument("--out", required=True, help="the sheet, .jpg")
    sh.add_argument("--cell", type=int, default=480, help="cell size in px (default 480)")
    sh.add_argument("--cols", type=int, help="columns (default: a square-ish grid)")
    sh.set_defaults(func=cmd_sheet)
    q = sub.add_parser("qr", help="QR code as SVG or PNG")
    q.add_argument("--data", required=True)
    q.add_argument("--out", required=True, help=".svg (print/web) or .png")
    q.add_argument("--error", default="m", choices=["l", "m", "q", "h"], help="h when a logo covers the centre")
    q.add_argument("--border", type=int, default=4, help="quiet zone in modules (4 is the standard)")
    q.add_argument("--dark", default="#000000")
    q.add_argument("--light", default="#ffffff", help="'none' for transparent")
    q.add_argument("--scale", type=int, default=10, help="PNG pixels per module")
    q.set_defaults(func=cmd_qr)
    cl = sub.add_parser("copylint", help="offline lint of copy: dashes, AI words, bookish or translated Bengali, "
                                         "lengths, platform limits")
    cl.add_argument("--copy", help="copy.json")
    cl.add_argument("--caption", help="a caption or post text: a file, or the text itself")
    cl.add_argument("--text", help="one string")
    cl.add_argument("--role", help="the role of --text, or of --caption when there is no --text (headline, cta, body, "
                                   "caption, reply, script, voiceover, alt)")
    cl.add_argument("--lang", help="language of --text or --caption as a BCP 47 tag (es, fr, hi, ar, zh-TW, pt-PT ...): "
                                   "its punctuation and voice rules; a region part switches on that market's rules")
    cl.add_argument("--locale", help="e.g. BD (Bangladesh), IN, US (default: copy.json's \"locale\")")
    cl.add_argument("--platform", help="instagram, facebook, linkedin, youtube, tiktok, x, threads, whatsapp, email, "
                                       "web, sms, voiceover; a format may follow: youtube-thumb, instagram-carousel "
                                       "(default: copy.json's \"platform\")")
    cl.add_argument("--brand", help="brand.json: its voice.avoid and voice.prefer words, and voice.keep lines the lint "
                                    "leaves alone")
    cl.add_argument("--strict", action="store_true", help="exit 2 on warnings too")
    cl.add_argument("--json", action="store_true", help="print the whole report as JSON only")
    cl.add_argument("--save", metavar="FILE", help="save the copy (from --text, or piped in) to FILE, then lint that "
                                                    "file: one step that cannot skip the check")
    cl.set_defaults(func=cmd_copylint)
    cj = sub.add_parser("copyjudge", help="native-reader review of copy by a fresh Codex session: ratings, rewrites")
    cj.add_argument("--copy", help="copy.json")
    cj.add_argument("--caption", help="a caption or post text: a file, or the text itself")
    cj.add_argument("--text", help="one string")
    cj.add_argument("--role", help="the role of --text, or of --caption when there is no --text")
    cj.add_argument("--lang", help="language of --text or --caption as a BCP 47 tag")
    cj.add_argument("--brief", help="the brief: a file (a path must exist), or the brief's text itself")
    cj.add_argument("--locale", help="e.g. BD (default: copy.json's \"locale\")")
    cj.add_argument("--platform", help="as for copylint (default: copy.json's \"platform\")")
    cj.add_argument("--goal", help="register, buy, visit, save, share, comment, watch, awareness")
    cj.add_argument("--reader", help="who reads it (default from --locale)")
    cj.add_argument("--brand", help="brand.json: its voice, avoid list and keep lines")
    cj.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    cj.add_argument("--runs", type=int, default=1, help="independent judge runs; the verdict uses each criterion's "
                                                         "median (3 for client work)")
    cj.add_argument("--timeout", type=int, default=150, help="seconds per run (one takes about 40 s); a timed-out run "
                                                              "is retried once")
    cj.add_argument("--fresh", action="store_true", help="judge again even when the report already holds a verdict for "
                                                          "exactly this deck, brief and settings")
    cj.add_argument("--json", action="store_true", help="print the whole report (it is always saved as "
                                                        "<copy>.copyjudge.json)")
    cj.set_defaults(func=cmd_copyjudge)
    jd = sub.add_parser("judge", help="independent senior-art-director review of a rendered design (Codex vision)")
    jd.add_argument("--image", required=True)
    jd.add_argument("--brief", help="the brief: a file (a path must exist), or the brief's text itself")
    jd.add_argument("--kind", default="social post", help="e.g. social post, story, carousel slide, thumbnail, "
                                                          "banner, poster, flyer, brochure, infographic, logo")
    jd.add_argument("--canvas", help="e.g. 'Instagram 4:5 1080x1350, safe zone 60 px'")
    jd.add_argument("--qa", help="the renderer's .qa.json (default: next to the image)")
    jd.add_argument("--print", action="store_true", help="print piece: no phone-size preview")
    jd.add_argument("--copy", help="copy.json: the approved strings (diffed against what the judge reads)")
    jd.add_argument("--allow", help="comma list of text allowed besides the copy (the brand name in the logo)")
    jd.add_argument("--brand", help="brand.json: its names become allowed text, and its logo files, logo rules, "
                                    "colours and motif go into the brief")
    jd.add_argument("--plate-meta", action="append", help="a photo plate's .meta.json whose image-judge defects the "
                                                          "judge should know (found automatically next to the plate)")
    jd.add_argument("--force", action="store_true", help="judge even though the render report has errors")
    jd.add_argument("--route", default="hybrid", choices=["hybrid", "full-ai"],
                    help="full-ai: text is in the pixels, so any text difference fails the design")
    jd.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    jd.add_argument("--runs", type=int, default=1, help="independent judge runs: median scores, a gate fails when "
                                                         "most runs fail it (3 for client work)")
    jd.add_argument("--timeout", type=int, default=240, help="seconds per run (one takes about 50 s); a timed-out run "
                                                              "is retried once")
    jd.add_argument("--fresh", action="store_true", help="judge again even when <image>.judge.json already holds a "
                                                          "verdict for exactly this image, brief and settings")
    jd.add_argument("--json", action="store_true", help="print the whole report (it is always saved as "
                                                        "<image>.judge.json)")
    jd.set_defaults(func=cmd_judge)
    pw = sub.add_parser("pairwise", help="blind A/B choice in both orders (and modes): which design goes to the client")
    pw.add_argument("--a", required=True, help="first design image")
    pw.add_argument("--b", required=True, help="second design image")
    pw.add_argument("--a-name", help="label for A in the report")
    pw.add_argument("--b-name", help="label for B in the report")
    pw.add_argument("--brief", help="the brief (a file, or its text): adds the client-facing mode to the blind one")
    pw.add_argument("--copy", help="copy.json for the client-facing mode")
    pw.add_argument("--kind", default="social post")
    pw.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    pw.add_argument("--out", help="write every vote to this JSON file")
    pw.add_argument("--timeout", type=int, default=300, help="seconds per vote; a timed-out vote is asked once more")
    pw.set_defaults(func=cmd_pairwise)
    an = sub.add_parser("analyze", help="faces, subject, focus and calm zones for text on a photo")
    an.add_argument("--src", required=True, help="the photo or plate")
    an.add_argument("--zone", action="append", help="a reserved text zone as x,y,w,h in percent (repeatable): "
                                                    "calm, scrim or busy, and how much of the subject it covers")
    an.add_argument("--strict", action="store_true", help="exit 2 when a --zone is not calm")
    an.set_defaults(func=cmd_analyze)
    rf = sub.add_parser("reframe", help="smart-crop one photo to several presets/sizes around faces or the subject")
    rf.add_argument("--src", required=True)
    rf.add_argument("--presets", required=True, help="comma list of preset ids and/or WxH sizes")
    rf.add_argument("--out-dir", required=True)
    rf.add_argument("--name")
    rf.add_argument("--focus", help="manual focus as fractions 'x,y' (0-1), instead of face/saliency detection")
    rf.add_argument("--format", default="jpg", choices=["jpg", "png", "webp"])
    rf.add_argument("--preset-file", action="append", help="extra presets (JSON)")
    rf.set_defaults(func=cmd_reframe)
    oc = sub.add_parser("ocr", help="read the text in an image (Apple Vision): lines and words with boxes")
    oc.add_argument("--src", required=True)
    oc.add_argument("--langs", help="comma list, e.g. en-US,fr-FR (default: automatic)")
    oc.add_argument("--correct", action="store_true", help="language correction on (off by default, to catch typos)")
    oc.set_defaults(func=cmd_ocr)
    vf = sub.add_parser("verify", help="check a finished raster design: OCR copy diff, invented text, safe zones, sizes")
    vf.add_argument("--image", required=True)
    vf.add_argument("--copy", help="copy.json: the approved strings")
    vf.add_argument("--preset", help="the canvas it is for (safe zone, keep-outs, text floor)")
    vf.add_argument("--brand", help="brand.json: its name counts as allowed text (the wordmark)")
    vf.add_argument("--allow", help="comma list of other allowed text (e.g. a handle on a sign)")
    vf.add_argument("--langs", help="OCR languages (default automatic)")
    vf.add_argument("--strict", action="store_true", help="punctuation differences are errors; exit 2 on any error")
    vf.add_argument("--preset-file", action="append", help="extra presets (JSON)")
    vf.set_defaults(func=cmd_verify)
    pa = sub.add_parser("patch", help="edit only the pointed-at regions of a design and paste them back (pixel-safe)")
    pa.add_argument("--image", required=True)
    pa.add_argument("--instruction", required=True, help="what to do inside the boxes, e.g. \"remove the text; continue "
                                                          "the background\"")
    pa.add_argument("--box", action="append", help="x,y,w,h in image pixels (repeatable)")
    pa.add_argument("--point", action="append", help="x,y[,r]: a pin on the spot to change; the region is a square of "
                                                      "radius r px around it (default 8%% of the short side)")
    pa.add_argument("--find", help="locate the region by the text it shows (OCR)")
    pa.add_argument("--extra", action="store_true", help="every text line that is not approved copy (needs --copy)")
    pa.add_argument("--copy", help="copy.json for --extra")
    pa.add_argument("--allow", help="comma list of allowed text for --extra (the brand name)")
    pa.add_argument("--pad", type=float, default=0.5, help="padding around each box, as a share of its height")
    pa.add_argument("--protect", action="append", help="x,y,w,h never repainted (approved copy is protected "
                                                         "automatically with --extra)")
    pa.add_argument("--mode", default="auto", choices=["auto", "crop", "full"],
                    help="crop: edit a close-up window around the boxes (sharper text); full: the whole image with "
                         "the boxes marked; auto: crop when the boxes cover under a third of the image")
    pa.add_argument("--engine", default="codex", choices=["codex", "api"])
    pa.add_argument("--model", default="gpt-image-2.5-sunburst", help="api engine model")
    pa.add_argument("--quality", default="high", help="api engine quality")
    pa.add_argument("--out", help="output PNG (default <image>-patched.png)")
    pa.add_argument("--timeout", type=int, default=240, help="seconds per edit session (one takes about 50 s); "
                                                              "codex-imagegen retries a failed one once")
    pa.add_argument("--dry-run", action="store_true", help="show the boxes, pointer, mask and prompt only")
    pa.set_defaults(func=cmd_patch)
    rs = sub.add_parser("refsheet", help="the brand on one reference image (logo, colours, fonts, motif) for the AI route")
    rs.add_argument("--brand", required=True, help="brand/brand.json")
    rs.add_argument("--css", help="brand.css (default: next to brand.json)")
    rs.add_argument("--out", required=True, help=".png")
    rs.add_argument("--for-model", action="store_true", help="the image-model version: no logo, no words")
    rs.set_defaults(func=cmd_refsheet)
    dr = sub.add_parser("direct", help="the single-prompt route: dossier -> one compiled prompt + references -> "
                                       "candidates -> OCR verify -> region repairs -> real logo -> final file")
    dr.add_argument("--dossier", required=True, help="dossier JSON (brief, facts, concept, copy, zones, references, logo)")
    dr.add_argument("--plan", action="store_true", help="build the references and the prompt, check them, stop")
    dr.add_argument("--engine", choices=["auto", "codex", "api"], help="default: the dossier's, else auto (api when "
                                                                        "an OpenAI key is in the keychain)")
    dr.add_argument("--model", default="gpt-image-2.5-sunburst", help="api engine model")
    dr.add_argument("--quality", default="xhigh", choices=["low", "medium", "high", "xhigh", "max"],
                    help="api engine quality")
    dr.add_argument("--variants", type=int, default=2, help="candidates per attempt (the best one is kept)")
    dr.add_argument("--tries", type=int, default=2, help="attempts (a retry carries the last attempt's mistakes)")
    dr.add_argument("--repair-rounds", type=int, default=2, help="region-repair rounds on the chosen candidate")
    dr.add_argument("--judge", action="store_true", help="independent art-director review of the final file")
    dr.add_argument("--revise", type=int, default=1, help="with --judge: rounds that regenerate with the judge's notes "
                                                          "when it says REVISE or FAIL (the better version is kept)")
    dr.add_argument("--out", help="final file (.png/.jpg/.webp); default <run>/<id>.png")
    dr.add_argument("--out-dir", help="run folder (default <dossier dir>/direct/<id>)")
    dr.add_argument("--ledger", help="creative ledger (default <dossier dir>/ledger.jsonl)")
    dr.add_argument("--refresh", action="store_true", help="rebuild the brand sheet")
    dr.add_argument("--retypeset", action="store_true", help="set the typeset copy again over the kept picture (a "
                                                               "changed price, date or address): no generation")
    dr.add_argument("--no-plate", action="store_true", help="on failure, skip the text-free plate for composing")
    dr.add_argument("--force", action="store_true", help="go on despite blocking facts or a repeated concept")
    dr.add_argument("--timeout", type=int, default=240, help="seconds per Codex session: generation, edit or judge "
                                                              "(each takes about 50 s and is retried once)")
    dr.set_defaults(func=cmd_direct)
    sk = sub.add_parser("sketch", help="a layout sketch (labelled zones) for the AI route")
    sk.add_argument("--zones", required=True, help='JSON file or text: [["HEADLINE", x%%, y%%, w%%, h%%], ...]')
    sk.add_argument("--preset")
    sk.add_argument("--size")
    sk.add_argument("--scale", type=float)
    sk.add_argument("--out", required=True)
    sk.add_argument("--preset-file", action="append", help="extra presets (JSON)")
    sk.set_defaults(func=cmd_sketch)
    co = sub.add_parser("cutout", help="lift the subject(s) of a photo onto transparency (Apple Vision, local)")
    co.add_argument("--src", required=True)
    co.add_argument("--out", required=True, help=".png")
    co.set_defaults(func=cmd_cutout)
    fo = sub.add_parser("fonts", help="download open-licensed fonts (Fontsource/Google Fonts) + fonts.css")
    fo.add_argument("--family", action="append", help="'Inter:400,700' or 'Hind Siliguri:500,700' (repeatable)")
    fo.add_argument("--out", default="fonts", help="project folder for the files and fonts.css")
    fo.add_argument("--subsets", help="comma list (default: latin, latin-ext and every non-Latin script the font has)")
    fo.add_argument("--search", help="list families matching words ('*' for all), with --subset/--category filters")
    fo.add_argument("--subset", help="with --search: e.g. bengali, arabic, devanagari")
    fo.add_argument("--category", help="with --search: serif, sans-serif, display, handwriting, monospace")
    fo.set_defaults(func=cmd_fonts)
    ol = sub.add_parser("outline", help="text -> SVG outlines shaped by HarfBuzz (wordmarks, print logos)")
    ol.add_argument("--text", required=True)
    ol.add_argument("--out", required=True, help=".svg")
    src_font = ol.add_mutually_exclusive_group(required=True)
    src_font.add_argument("--font", help="a .ttf/.otf file (e.g. the client's licensed font)")
    src_font.add_argument("--family", help="or an open font family from Fontsource")
    ol.add_argument("--weight", type=int, default=700)
    ol.add_argument("--italic", action="store_true")
    ol.add_argument("--subset", help="latin, latin-ext, bengali... (guessed from the text)")
    ol.add_argument("--size", type=float, default=200, help="font size in px (the SVG scales anyway)")
    ol.add_argument("--tracking", type=float, default=0.0, help="letter-spacing in em, e.g. -0.01 (not for Indic/Arabic)")
    ol.add_argument("--features", help="OpenType features, e.g. 'ss01,-liga'")
    ol.add_argument("--fill", default="#111111")
    ol.set_defaults(func=cmd_outline)
    br = sub.add_parser("brand", help="brand.json -> brand.css variables + fonts")
    br.add_argument("--json", required=True)
    br.add_argument("--out", help="folder for brand.css and fonts/ (default: next to brand.json)")
    br.set_defaults(func=cmd_brand)
    kt = sub.add_parser("kit", help="copy the kit next to designs and point their links at it (editable source)")
    kt.add_argument("--out", required=True, help="folder that receives kit/ (and sample-brand/)")
    kt.add_argument("--html", nargs="*", help="HTML files whose https://codex-design.invalid/ links are rewritten")
    kt.add_argument("--sample-brand", action="store_true", help="also copy the sample brand")
    kt.set_defaults(func=cmd_kit)
    p = sub.add_parser("presets", help="the canvas catalogue: list, search (--find), one in full (--id), or the "
                                       "nearest to an unknown size (--nearest)")
    p.add_argument("--group", help="only this group (social, web, ads, ecommerce, print, document, ...)")
    p.add_argument("--find", help="words people use: 'pinterest pin', 'ebook cover', 'fb cover photo', 'biye card'")
    p.add_argument("--id", help="one preset in full, with its notes and source")
    p.add_argument("--nearest", help="an unknown size (1500x3000, 150mmx150mm): the presets closest in aspect ratio")
    p.add_argument("--preset-file", action="append", help="extra presets (JSON): a client's or project's verified specs")
    p.add_argument("--json", action="store_true", help="the list with every field as JSON (the default is one line per "
                                                       "preset: id, size, group)")
    p.set_defaults(func=cmd_presets)
    bk = sub.add_parser("bookcover", help="a printed book's flat cover (back, spine, front) for KDP, IngramSpark or "
                                          "Lulu: spine width, full size, barcode and hinge areas, as a preset")
    bk.add_argument("--platform", required=True, choices=["kdp", "ingram", "lulu"])
    bk.add_argument("--binding", default="paperback", choices=["paperback", "hardcover"])
    bk.add_argument("--trim", required=True, help="6x9, 5.5x8.5, 5x8, 7x10, a5, b-format, a4 ... or WxH in inches")
    bk.add_argument("--pages", type=int, required=True, help="interior page count")
    bk.add_argument("--paper", default="cream", help="white, cream, colour, premium-colour, groundwood (ingram: also "
                                                     "white-70)")
    bk.add_argument("--id", help="preset id (default: platform-binding-trim-pages-paper)")
    bk.add_argument("--preset-file", action="append", help="write the preset into this file (created if missing)")
    bk.set_defaults(func=cmd_bookcover)
    lg = sub.add_parser("ledger", help="never two designs alike: check a recipe (axes, device, hook) against the "
                                       "client's earlier designs, or add a finished one")
    lg.add_argument("--ledger", required=True, help="the client's ledger.jsonl (shared with the direct route)")
    lg.add_argument("--client", help="client name: only their designs are compared")
    lg.add_argument("--recipe", help="recipe.json: structure, archetype, focal, device, type_mode, palette, finish "
                                     "(+ concept, hook, cta)")
    lg.add_argument("--id", help="this design's id (default: the recipe's id or file name)")
    lg.add_argument("--image", help="the finished design (compared by look; needed with --add)")
    lg.add_argument("--add", action="store_true", help="record the design (refused when too close, unless --force)")
    lg.add_argument("--force", action="store_true")
    lg.add_argument("--strict", action="store_true", help="exit 2 when the recipe is too close to an earlier one")
    lg.add_argument("--list", type=int, help="print the last N entries")
    lg.set_defaults(func=cmd_ledger)
    dv = sub.add_parser("deliver", help="the final gate: render report, judge and copy checks must pass; then the "
                                        "files go to --out with DELIVERY.md")
    dv.add_argument("--design", action="append", required=True, help="a finished design file (repeatable; a "
                                                                    "carousel strip brings its slides)")
    dv.add_argument("--out", help="delivery folder (an existing file there is moved to archive-<time>/)")
    dv.add_argument("--copy", help="copy.json (lint and copy-judge gates)")
    dv.add_argument("--caption", help="the caption (a file, or its text), as given to copyjudge")
    dv.add_argument("--locale", help="default: copy.json's \"locale\"")
    dv.add_argument("--platform", help="default: copy.json's \"platform\"")
    dv.add_argument("--brand", help="brand.json: its voice words for the lint")
    dv.add_argument("--level", default="client", choices=["client", "draft"],
                    help="client (default): copy must be PASS_NATIVE; draft: PASS is enough")
    dv.add_argument("--judge", action="store_true", help="run the design judge on every design and the copy judge "
                                                         "first, all at the same time (a report that already matches "
                                                         "is reused); needs --brief")
    dv.add_argument("--brief", help="with --judge: the brief (a file, or its text)")
    dv.add_argument("--kind", default="social post", help="with --judge: what the design is (default: social post)")
    dv.add_argument("--allow", help="with --judge: the logo's wordmark or fixed marks, comma separated")
    dv.add_argument("--goal", help="with --judge: what the copy should make the reader do")
    dv.add_argument("--runs", type=int, help="with --judge: runs per judge (default 3 at client level, 1 at draft)")
    dv.add_argument("--facts", help="facts.json: [{\"claim\", \"status\": verified | client_supplied | unverified | "
                                    "refuted | needs_client}]; refuted or needs_client stops the delivery")
    dv.add_argument("--ledger", help="add the delivered design to this ledger (needs --recipe, --client)")
    dv.add_argument("--recipe", help="recipe.json for the ledger")
    dv.add_argument("--client", help="client name for the ledger")
    dv.add_argument("--name", help="title of DELIVERY.md (default: the first design's name)")
    dv.add_argument("--force", action="store_true", help="deliver although the ledger finds a close earlier design")
    dv.add_argument("--dry-run", action="store_true", help="run the gates, copy nothing")
    dv.set_defaults(func=cmd_deliver)
    d = sub.add_parser("doctor", help="check Chrome, Pillow, presets and a test render")
    d.add_argument("--setup", action="store_true", help="create the skill venv for this Python and install "
                                                         "Pillow, segno, pypdf, uharfbuzz and fontTools")
    d.add_argument("--clean-tmp", action="store_true", help="remove temp folders left by killed runs")
    d.set_defaults(func=cmd_doctor)
    return ap


def _explain(e: BaseException) -> str:
    """One line a person can act on, instead of a traceback."""
    import urllib.error
    if isinstance(e, urllib.error.HTTPError):
        return f"the server answered HTTP {e.code} for {e.url} (a font family, weight or subset that does not exist?)"
    if isinstance(e, urllib.error.URLError):
        return f"network error ({e.reason}): `fonts` and font downloads need the internet"
    if isinstance(e, TimeoutError):
        return f"{e}: a page script may be stuck, or Chrome is overloaded (raise --timeout)"
    if isinstance(e, RunFailed):
        return str(e)
    return f"{e.__class__.__name__}: {e}"


def main() -> None:
    import signal

    def stop(signum, frame):
        """Ctrl-C or a supervisor's TERM: end the running Codex sessions first (they would go on spending plan quota
        while the worker threads wait for them), then exit normally so atexit removes temp dirs and the Chrome
        profile."""
        n = kill_live_sessions()
        if n:
            log(f"stopping: ended {n} running session(s)")
        if signum == signal.SIGINT:
            raise KeyboardInterrupt
        sys.exit(128 + signum)
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, stop)
        except (ValueError, OSError):
            pass
    args = build_parser().parse_args()
    _PRESET_FILES.extend(getattr(args, "preset_file", None) or [])
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("codex-design: interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:  # noqa: BLE001  (every failure ends in one readable line; CODEX_DESIGN_DEBUG=1 for more)
        if os.environ.get("CODEX_DESIGN_DEBUG"):
            raise
        die(f"{args.cmd}: {_explain(e)} (CODEX_DESIGN_DEBUG=1 shows the traceback)")


if __name__ == "__main__":
    main()
