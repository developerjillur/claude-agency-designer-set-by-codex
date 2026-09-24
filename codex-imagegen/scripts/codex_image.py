#!/usr/bin/env python3
"""codex-imagegen: production image generation and editing through the local Codex CLI.

Engines
  codex (default)  Drives `codex exec` with Codex's built-in image_gen tool. Uses the ChatGPT login
                   stored by `codex login` (no OpenAI API key, no approval prompts). Codex picks the
                   image model server-side (the client currently requests gpt-image-2).
  api   (optional) OpenAI Images API with explicit routing: gpt-image-2.5-sunburst / -flare, falling
                   back to gpt-image-2. Needs OPENAI_API_KEY (env var, or macOS Keychain item
                   "OPENAI_API_KEY"). Never used unless selected or --engine auto finds a key.

Subcommands: generate, edit, batch, judge, compare, export, favicon, og, cutout, audit, doctor.  Stdlib only (Python 3.9+); Pillow is optional for --size.
"""
from __future__ import annotations

import argparse
import atexit
import base64
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")
APP_BUNDLED_CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
FALLBACK_CODEX_MODEL = os.environ.get("CODEX_IMAGEGEN_FALLBACK_MODEL", "gpt-5.5")
REASONING_SUMMARY = os.environ.get("CODEX_IMAGEGEN_REASONING_SUMMARY", "detailed")  # "none" disables
# Automated sessions do not need memories, chronicle, apps or browser/computer use: switching them off cut Codex start-up
# from 14.5 s to 9.1 s (-5k context tokens) and keeps hundreds of image jobs out of the user's Codex memory.
LEAN_FLAGS = [] if os.environ.get("CODEX_IMAGEGEN_FULL_FEATURES") else [
    "-c", "features.memories=false", "-c", "memories.generate_memories=false", "-c", "memories.use_memories=false",
    "-c", "features.chronicle=false", "-c", "features.apps=false", "-c", "features.browser_use=false",
    "-c", "features.computer_use=false", "-c", "features.in_app_browser=false"]
# Extra flags for every automated session, to A/B what image and judge sessions do not need (MCP servers, the notify
# hook, plugins), e.g. CODEX_IMAGEGEN_EXTRA_FLAGS='-c mcp_servers.motion.enabled=false -c notify=[]'. Real sessions
# spend ~3.1 s (median) in Codex start-up before the model is called; measure with `doctor --image-smoke`.
LEAN_FLAGS = LEAN_FLAGS + shlex.split(os.environ.get("CODEX_IMAGEGEN_EXTRA_FLAGS", ""))
API_BASE = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
SKILL_VERSION = "2026.09.24.1"  # bump on every behaviour change; `doctor` reports it
CODEX_TZ = os.environ.get("CODEX_IMAGEGEN_TZ", "UTC")  # Codex tells the model the machine timezone; "system" keeps it
# Session time limits. Real fast-mode image sessions took 87 s median, 246 s p90 and 488 s at most; real judges took
# 38 s median, 53 s p90 and 104 s at most. Agent mode and the API engine keep the older, longer limit.
GEN_TIMEOUT = 480
AGENT_TIMEOUT = 900
JUDGE_TIMEOUT = 150


_TMP = {"lock": threading.Lock()}


def tmp_dir(prefix: str = "codex-imagegen-") -> str:
    """Every temp folder of one run lives under one root that is removed at exit (CODEX_IMAGEGEN_KEEP_TMP=1 keeps it
    for debugging); Codex event streams worth keeping go to --log-dir instead."""
    with _TMP["lock"]:
        if "root" not in _TMP:
            _TMP["root"] = tempfile.mkdtemp(prefix="codex-imagegen-run-")
            if not os.environ.get("CODEX_IMAGEGEN_KEEP_TMP"):
                atexit.register(shutil.rmtree, _TMP["root"], True)
    return tempfile.mkdtemp(prefix=prefix, dir=_TMP["root"])


SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,99}")


def check_name(name, what: str = "job name") -> str:
    """Names become file and folder names: letters, digits, dot, dash, underscore; no paths, no '..'."""
    if not isinstance(name, str) or not SAFE_NAME.fullmatch(name) or ".." in name:
        die(f"invalid {what} {name!r}: use letters, digits, '.', '-' or '_' (no slashes or '..')")
    return name


def codex_env() -> dict:
    """Environment for Codex runs: a neutral timezone, so the developer's location never localizes an image."""
    return dict(os.environ) if CODEX_TZ.lower() in ("", "system") else dict(os.environ, TZ=CODEX_TZ)


def write_atomic(path, text: str) -> Path:
    """Write text through a temp file in the same folder + os.replace: an interrupted run never leaves half a JSON
    file (a truncated assets.json used to break every later export)."""
    path = Path(path)
    tmp = path.with_name(f".{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        try:
            tmp.unlink()
        except OSError:
            pass
        raise
    return path


# Every Codex session (and agent-mode child run) lives in its own process group, so the terminal's Ctrl-C never
# reaches it. They are tracked here: a stop signal ends them all at once instead of leaving them running (and
# spending plan quota) for up to --timeout while Python waits for its worker threads.
_LIVE = {"procs": set(), "lock": threading.RLock(), "stop": False, "fatal": None}  # RLock: a signal may land while held
POLL_S = 0.2  # how often a running session checks cancel / stop / an early result
# Codex errors that every later session would hit too: the plan's usage limit or a lost login. The run stops at once.
FATAL_RX = re.compile(r"usage limit|hit your limit|quota|not logged in|(please|need to) (log|sign) ?in|codex login|"
                      r"unauthori[sz]ed|(authentication|auth) (failed|required|error)|"
                      r"token (has )?(expired|been revoked)|(access|refresh) token\b.{0,40}\b(expired|invalid|revoked)",
                      re.I)


def _stop_group(proc, grace: float = 2.0) -> None:
    """SIGTERM the process group, then SIGKILL whatever is left after `grace` seconds."""
    for sig, wait in ((signal.SIGTERM, grace), (signal.SIGKILL, None)):
        if proc.poll() is not None:
            return
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError, OSError):
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
    """Stop every session this run started and refuse new ones. Returns how many were still running."""
    _LIVE["stop"] = True
    with _LIVE["lock"]:
        procs = [p for p in _LIVE["procs"] if p.poll() is None]
    # 3 s grace: an agent-mode child CLI first ends its own Codex sessions (2 s grace each) when it gets SIGTERM
    threads = [threading.Thread(target=_stop_group, args=(p, 3.0)) for p in procs]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return len(procs)


def fatal_error(text) -> bool:
    """True for a Codex error that no retry can fix: the plan's usage limit or a lost login."""
    return bool(text) and bool(FATAL_RX.search(str(text)))


def stop_run(reason: str) -> None:
    """End the whole run at once, keeping Codex's own words as the reason: every other session would fail the same
    way, so none of them should keep waiting or spending quota."""
    with _LIVE["lock"]:
        first = not _LIVE["fatal"]
        if first:
            _LIVE["fatal"] = str(reason)[:500]
    if first:
        log(f"STOPPING the run. Codex said: {_LIVE['fatal']}")
        kill_live_sessions()


def install_stop_handlers() -> None:
    """Ctrl-C, SIGTERM (a killed background task) or SIGHUP stop the running Codex sessions first, then exit."""
    def stop(signum, frame):
        n = kill_live_sessions()
        if n:
            log(f"stopping: ended {n} running Codex session(s)")
        if signum == signal.SIGINT:
            raise KeyboardInterrupt
        raise SystemExit(128 + signum)
    for s in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGHUP", None)):
        if s is not None:
            try:
                signal.signal(s, stop)
            except (ValueError, OSError):  # not the main thread
                pass


def run_group(cmd: list, prompt, timeout, tmp: Path, cancel=None, ready=None, env=None) -> dict:
    """Run a command in its own process group with stdout/stderr in files (no pipe deadlock), tracked in _LIVE.
    The timeout, a set `cancel` event or a stop signal end the whole group. `ready()` is polled while it runs: a
    non-empty return value is the session's finished result (only the agent's closing message is left), so the
    group is stopped and the value comes back as "early".
    -> {"stdout", "stderr", "returncode", "error" (None, "cancelled", "stopped" or "timed out after Ns"), "early"}"""
    res = {"stdout": "", "stderr": "", "returncode": None, "error": None, "early": None}
    if _LIVE["stop"]:
        return dict(res, error="stopped")
    t0 = time.time()
    so, se = tmp / "stdout.jsonl", tmp / "stderr.txt"
    with open(so, "w", encoding="utf-8") as fo, open(se, "w", encoding="utf-8") as fe:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE if prompt is not None else subprocess.DEVNULL, stdout=fo,
                                stderr=fe, text=True, start_new_session=True, env=codex_env() if env is None else env)
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
                stop = "stopped" if _LIVE["stop"] else "cancelled" if cancel is not None and cancel.is_set() else (
                    f"timed out after {timeout}s" if timeout and time.time() - t0 > timeout else None)
                if stop is None and ready is not None:
                    try:
                        res["early"] = ready() or None
                    except Exception:  # an early-result probe must never break the run
                        res["early"] = None
                if stop or res["early"]:
                    # a stop gives a child CLI time to end its own sessions; cancel/timeout end fast
                    _stop_group(proc, grace=3.0 if stop == "stopped" else 0.5 if stop else 2.0)
                    res["error"] = stop
                    break
        finally:
            with _LIVE["lock"]:
                _LIVE["procs"].discard(proc)
    if res["error"] is None and not res["early"] and _LIVE["stop"] and proc.returncode != 0:
        res["error"] = "stopped"  # ended by kill_live_sessions() from another thread
    res["returncode"] = proc.returncode
    res["stdout"] = so.read_text(encoding="utf-8", errors="replace")
    res["stderr"] = se.read_text(encoding="utf-8", errors="replace")
    return res

# aspect -> (phrase written into Codex prompts, valid API generation size)
ASPECTS = {
    "1:1": ("square 1:1 format", "1024x1024"),
    "3:2": ("wide 3:2 landscape", "1536x1024"),
    "2:3": ("tall 2:3 portrait", "1024x1536"),
    "4:3": ("4:3 landscape", "1600x1200"),
    "3:4": ("3:4 portrait", "1200x1600"),
    "4:5": ("4:5 portrait", "1088x1360"),
    "5:4": ("5:4 landscape", "1360x1088"),
    "16:9": ("wide 16:9 landscape", "1920x1088"),
    "9:16": ("vertical 9:16 portrait", "1088x1920"),
    "21:9": ("ultra-wide 21:9 banner", "2800x1200"),
    "3:1": ("very wide 3:1 panoramic banner", "3072x1024"),
    "1:3": ("very tall 1:3 vertical strip", "1024x3072"),
}
TIERS = {"draft": ("gpt-image-2.5-flare", "medium"), "final": ("gpt-image-2.5-sunburst", "high"),
         "premium": ("gpt-image-2.5-sunburst", "xhigh")}
Q_ORDER = ["low", "medium", "high", "xhigh", "max"]

CRAFT_RULES = """PROMPT CRAFT (think it through carefully before every tool call)
1. Normalize the brief into labeled lines, omitting empty ones: Intent / Scene / Subject (exact counts, pose, gaze, scale) / Action mechanics (only if something moves: source -> path -> target) / Object anatomy (for anything held or used: handles, spouts, necks, bases; write "no handle" when there is none) / Grip & load (which hand touches which part, grip type, where the weight is supported, visible strain) / Camera (medium, shot size, angle, lens feel, depth of field) / Light (ONE motivated source: direction, quality, color cast; plus practicals if present) / Materials & texture (scaled to camera distance) / Color & mood / Text (verbatim, exact count, font style, placement) / Constraints (must keep + exclusions) / Output (aspect and orientation, negative space, background).
2. Specificity: a detailed brief is only normalized; a generic brief gets only framing, intended-use polish, layout and plausible scene concreteness. Never add people, props, brands, slogans, claims, prices or readable text the brief does not imply.
3. Photoreal briefs: state the medium once ("photorealistic", "real photograph" or "phone photo"); describe capture conditions (device or lens feel, angle, handheld or tripod); one motivated light; texture at the right scale; 1-3 specific imperfections, each with a location and a cause; exact counts of people and objects. Delete hype words (8K, masterpiece, ultra-detailed, hyperrealistic, flawless, perfect skin, sharp focus, Unreal/Octane). Avoid "cinematic", "golden" and "vintage" unless the brief asks for that look. At most 5 prominent faces.
4. Non-photo briefs (illustration, UI, infographic, logo, poster, 3D): keep the requested style; quote exact text with count and typography; keep diagram labels verbatim and never invent data or numbers.
5. The tool has no size parameter: always write the aspect ratio and orientation into the prompt.
6. Write every image prompt in English. Hands and held objects: refer to each hand by its frame position (the hand on the viewer's left/right, the hand nearer the camera) and name anatomical left/right only when it matters. Give heavy objects poses the model renders reliably: close to the body, resting on the hip, a surface or a table edge, both hands visible with clear roles (one bears the weight under the center of mass, one steers). Never call a handle-less water pot (for example a South Asian kolshi) a pitcher, jug or jar (those words bring a handle); describe what an object IS before any "no X" and keep negations to one short line, because a "no X" can prime X.
7. Place and people: keep the place the brief or its Locale line names. When none is named, keep the setting internationally neutral and give people natural, varied appearances; never localize from the user's language, timezone or earlier examples."""

PHYSICS_RULES = """REAL-WORLD LOGIC (apply to every image and spell out the parts that matter in the prompt)
- Gravity and support: nothing floats unintentionally; objects rest on surfaces with contact shadows; weight compresses soft materials.
- Liquids: they leave a container only over a tilted rim or through a spout, at its lowest point, as a connected stream that ends inside the target; liquid surfaces stay level with the horizon; splashes rise from the impact point.
- Light: one consistent light logic; every shadow falls away from its source with consistent direction and length; catchlights match the source; mixed color temperatures stay plausible.
- Reflections and refraction: mirrors, water and glass show the actual scene, correctly inverted and aligned.
- Motion: steam, smoke, hair and fabric follow one wind or motion direction; motion blur only on moving things.
- Mechanics and anatomy: tools touch what they act on; chains, wheels, hinges, cables and ropes connect end to end; hands have five fingers with natural grips; bodies keep plausible proportions and balance.
- Hand-object affordance: hands touch only parts that exist on the real object and are meant to be held; handles appear only where the object really has one; a handle-less pot or jar is cradled by its body and base, never gripped at the neck as if the neck were a handle; fingers wrap around surfaces and never pass through them; tools are held the way they are used.
- Load and balance: heavy or full objects are supported under their center of mass; the load-bearing hand shows the weight (fingers spread and pressing into the surface, wrist extended, forearm tension, elbow bent, body leaning back to counterbalance); two hands share heavy loads, one bearing weight and one steering; light objects use precision grips.
- Cultural handling: objects are held and used the way people in the named place actually do it; with no place named, use the internationally common form. A handle-less water pot (for example a South Asian kolshi: round belly, short neck, rolled rim, no handle, no spout) is carried on the hip with its neck in the crook of the arm, or on the head on a cloth ring, and poured with a palm or forearm under its belly while the other hand only steers at the rim; a very heavy one is tipped while resting on the floor, a ring or the hip. Chopsticks rest together in one hand; in many South Asian, Middle Eastern and African cultures food is eaten and things are handed over with the right hand. Hot vessels (kettle bodies, woks, karahi, handle-less cooking pots) are touched only by their handles, a cloth or tongs. A bodna (South Asian toilet-water pot with a side handle and spout) never serves drinking water.
- Scale and perspective: things shrink with distance; architectural verticals stay straight unless intended; one consistent horizon.
- Place, time and culture: clothing, vehicles, traffic side, signage script, architecture, food and customs fit the place and period named in the brief or its Locale line; never mix regions or eras. With no place named, keep the setting internationally neutral and people's appearances varied.
- Materials: skin has pores and tonal variation; fabric folds at joints; metal shows anisotropic highlights and scratches; glass shows refraction and dark edge lines; food shows moisture and irregular cuts."""

QA_RULES = """SELF-QA (after every generation; inspect the returned image at detail level)
- Gates (any failure means retry): instruction following; exact text if requested (check every character); physics trace (every pour, splash, reflection, shadow and support has a correct source -> path -> target); hand-object (trace each hand: the part it touches really exists on the object and is meant to be held, no phantom handles or added spouts, the grip suits the weight, its role is clear; then count each hand's fingers one by one; and trace each heavy object's load: something under its center of mass with visible load cues, held close to the body); anatomy (hands, fingers, limbs); no unrequested elements, text or logos.
- Scores 0-5: realism (style fidelity for non-photo work), artifacts, physics_plausibility, composition. If unsure between two scores, choose the lower one.
- If a gate fails or any score is below 4 and attempts remain (max {attempts} generations per deliverable), make ONE targeted fix: regenerate with the prompt plus one corrective sentence, or edit the last image (num_last_images_to_include=1) with "change only <X>; keep everything else exactly the same". Keep the best attempt."""

SAVE_RULES = """SAVING
- Copy (never move) each final PNG from $CODEX_HOME/generated_images/... to its deliverable path; create missing folders; never overwrite an existing file (append -v2, -v3 instead).
- Do not create or modify any other files. Never use scripts/image_gen.py, never ask for an API key, never ask for confirmation.

FINAL ANSWER
Return ONLY the JSON object required by the output schema: one entry per delivered image; output_path = the file you actually wrote; source_path = the original under $CODEX_HOME/generated_images; final_prompt = the exact prompt of the kept attempt; attempts = generations used for it."""


OUTPUT_SCHEMA = {
    "type": "object", "additionalProperties": False, "required": ["images", "notes"],
    "properties": {
        "images": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["output_path", "source_path", "final_prompt", "attempts", "qa"],
            "properties": {
                "output_path": {"type": "string"}, "source_path": {"type": "string"},
                "final_prompt": {"type": "string"}, "attempts": {"type": "integer"},
                "qa": {"type": "object", "additionalProperties": False,
                       "required": ["pass", "realism", "artifacts", "physics_plausibility", "composition", "issues"],
                       "properties": {"pass": {"type": "boolean"}, "realism": {"type": "integer"},
                                      "artifacts": {"type": "integer"},
                                      "physics_plausibility": {"type": "integer"},
                                      "composition": {"type": "integer"},
                                      "issues": {"type": "array", "items": {"type": "string"}}}}}}},
        "notes": {"type": "string"}}}


def log(msg: str) -> None:
    print(f"[codex-imagegen {time.strftime('%H:%M:%S')}] {msg}", file=sys.stderr, flush=True)


def die(msg: str, code: int = 1) -> None:
    log(f"ERROR: {msg}")
    err = SystemExit(code)
    err.message = msg  # a batch job that dies reports this instead of ending the whole batch
    raise err


# ----------------------------------------------------------------------------- helpers
def slugify(text: str, words: int = 6) -> str:
    toks = re.findall(r"[a-z0-9]+", text.lower())[:words]
    return "-".join(toks)[:60] or "image"


def unique_path(p: Path) -> Path:
    if not p.exists():
        return p
    i = 2
    while True:
        cand = p.with_name(f"{p.stem}-v{i}{p.suffix}")
        if not cand.exists():
            return cand
        i += 1


def parse_size(s: str) -> tuple:
    m = re.fullmatch(r"(\d+)x(\d+)", s or "")
    if not m:
        die(f"size must look like 1920x1080, got {s!r}")
    return int(m.group(1)), int(m.group(2))


def check_size(size, what: str) -> None:
    """Refuse a malformed size before any Codex session (it used to end the whole run after the images were made)."""
    m = re.fullmatch(r"(\d+)x(\d+)", str(size))
    if not m or int(m.group(1)) < 1 or int(m.group(2)) < 1:
        die(f"{what}: size must be WIDTHxHEIGHT in pixels with a lowercase x and no spaces, like 1920x1080 "
            f"(got {size!r})")


def check_candidates(value, what: str) -> None:
    """Candidates per image: a whole number from 1 to 4, or not set."""
    if value is None:
        return
    if isinstance(value, bool) or not str(value).strip().isdigit() or not 1 <= int(value) <= 4:
        die(f"{what}: candidates must be a whole number from 1 to 4 (got {value!r})")


def find_input(value, bases=()):
    """A file named on the command line or in a jobs file. Absolute and ~ paths are taken as given; a relative path
    is looked up in each base folder in turn, then in the current folder. None when it is nowhere."""
    p = Path(str(value)).expanduser()
    for q in ([p] if p.is_absolute() else [Path(b) / p for b in bases] + [Path.cwd() / p]):
        try:
            if q.exists():
                return q.resolve()
        except OSError:  # text longer than a file name is not a path
            return None
    return None


def valid_api_size(w: int, h: int) -> bool:
    return (max(w, h) <= 3840 and w % 16 == 0 and h % 16 == 0 and max(w, h) / min(w, h) <= 3
            and 655_360 <= w * h <= 8_294_400)


def png_info(p: Path) -> dict:
    data = p.read_bytes()
    info = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "c2pa": b"c2pa" in data}
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        info["width"] = int.from_bytes(data[16:20], "big")
        info["height"] = int.from_bytes(data[20:24], "big")
    return info


def fit_to_size(src: Path, w: int, h: int) -> Path:
    """Center-crop to the target aspect and resize to exactly w x h. Keeps a -raw copy."""
    raw = unique_path(src.with_name(f"{src.stem}-raw{src.suffix}"))
    shutil.copy2(src, raw)
    try:
        need_pillow()
        from PIL import Image, ImageOps  # type: ignore
        with Image.open(raw) as im:
            ImageOps.fit(im, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)).save(
                src, **(provenance_kwargs(src) if ai_source(raw) else {}))
        return raw
    except (ImportError, SystemExit):
        pass
    except Exception as e:  # an unreadable image keeps its native size instead of failing the job
        log(f"WARNING: --size crop failed ({e!r}); trying sips")
    if shutil.which("sips"):
        info = png_info(raw)
        sw, sh = info.get("width"), info.get("height")
        if sw and sh:
            r = w / h
            cw, ch = (round(sh * r), sh) if sw / sh > r else (sw, round(sw / r))
            try:
                subprocess.run(["sips", "--cropToHeightWidth", str(ch), str(cw), str(raw), "--out", str(src)],
                               capture_output=True, check=True)
                subprocess.run(["sips", "-z", str(h), str(w), str(src)], capture_output=True, check=True)
                return raw
            except (OSError, subprocess.CalledProcessError) as e:
                log(f"WARNING: sips crop failed ({e})")
    log("WARNING: --size needs Pillow (pip install pillow) or macOS sips; left the image at its native size")
    return raw


def codex_bin() -> str:
    cand = os.environ.get("CODEX_BIN") or shutil.which("codex")
    if cand:
        return cand
    if APP_BUNDLED_CODEX.exists():
        return str(APP_BUNDLED_CODEX)
    die("Codex CLI not found. Install it (references/server-setup.md) or set CODEX_BIN.")
    return ""


def codex_version(bin_: str) -> str:
    try:
        return subprocess.run([bin_, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:
        return "unknown"


def get_api_key():
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    if sys.platform == "darwin" and shutil.which("security"):
        r = subprocess.run(["security", "find-generic-password", "-s", "OPENAI_API_KEY", "-w"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    return None


# ----------------------------------------------------------------------------- job setup
def looks_like_file_name(text: str) -> bool:
    """A one-line text that is a file name (brief.txt) or an existing file, not a brief."""
    t = (text or "").strip()
    if not t or "\n" in t or len(t) > 250:
        return False
    p = find_input(t)
    return bool(re.fullmatch(r"\S+\.(txt|md|json)", t, re.I)) or (p is not None and p.is_file())


def read_brief(args) -> str:
    """The brief from --prompt, --prompt-file FILE or --prompt-file - (stdin). An empty brief stops the run."""
    if args.prompt_file and args.prompt is not None:
        log("WARNING: both --prompt and --prompt-file given; the file is used")
    if args.prompt_file == "-":
        brief = sys.stdin.read().strip()
        if not brief:
            die("the brief is empty: nothing came in on stdin (check the heredoc)")
        return brief
    if args.prompt_file:
        p = find_input(args.prompt_file)
        if p is None or not p.is_file():
            die(f"brief file not found: {args.prompt_file} (to pass the brief as text, use --prompt)")
        brief = p.read_text(encoding="utf-8").strip()
        if not brief:
            die(f"the brief is empty: {p}")
        return brief
    if args.prompt is not None:
        if not args.prompt.strip():
            die("the brief is empty")
        if looks_like_file_name(args.prompt):
            log(f"WARNING: --prompt looks like a file name ({args.prompt.strip()}); it is used as the brief text. "
                f"To read the brief from a file, use --prompt-file")
        return args.prompt.strip()
    die("give --prompt or --prompt-file")
    return ""


def parse_refs(items, bases=()) -> list:
    """--ref PATH[=ROLE] values -> [(path, role)]. Relative paths are looked up in `bases`, then the current folder."""
    refs = []
    for it in items or []:
        whole = find_input(it, bases)  # a file name that itself contains "=" is a path with no role
        path, _, role = (it, "", "") if whole is not None and whole.is_file() else it.partition("=")
        p = find_input(path, bases)
        if p is None or not p.is_file():
            die(f"reference image not found: {Path(path).expanduser()}")
        refs.append((p, role.strip() or "reference"))
    return refs


def plan_outputs(args, brief: str, workdir: Path) -> list:
    n = args.n
    if args.out:
        base = Path(args.out).expanduser()
        base = base if base.is_absolute() else workdir / base
        if base.suffix.lower() != ".png":
            base = base.with_suffix(".png")
    else:
        out_dir = Path(args.out_dir).expanduser() if args.out_dir else workdir / "output" / "imagegen"
        out_dir = out_dir if out_dir.is_absolute() else workdir / out_dir
        base = out_dir / f"{args.name or slugify(brief)}.png"
    names = [base] if n == 1 else [base.with_name(f"{base.stem}-{i}{base.suffix}") for i in range(1, n + 1)]
    planned, taken = [], set()
    for p in names:
        q = unique_path(p)
        while q in taken:
            q = unique_path(q.with_name(q.stem + "x" + q.suffix))
        taken.add(q)
        planned.append(q)
    return planned


def director_prompt(mode: str, brief: str, outputs: list, aspect: str, refs: list, target, attempts: int,
                    qa: bool, explore: bool) -> str:
    L = ["$imagegen You are a senior art director, photographer and retoucher producing production-grade images. "
         "Work autonomously: never ask questions, never ask for confirmation, never ask for an API key. "
         "Use ONLY the built-in image_gen tool (default built-in mode).", "", "JOB",
         f"- Mode: {mode}", f"- Deliverables ({len(outputs)}):"]
    L += [f"  {i}. {o}" for i, o in enumerate(outputs, 1)]
    if len(outputs) > 1:
        L.append("- Make one separate image_gen call per deliverable." + (
            " They are variants of ONE brief: give each a clearly different direction (camera angle, framing or "
            "light), never near-duplicates." if explore else ""))
    if aspect:
        L.append(f"- Aspect and orientation to write into every prompt: {aspect}")
    if target is not None:
        L.append(f"- EDIT TARGET (Image 1): {target} - pass it first in referenced_image_paths.")
    if refs:
        L.append("- Reference images (pass them in referenced_image_paths after any edit target, max 5 in total; "
                 "state in the prompt what to take from each and what not to take):")
        L += [f"  - {p} = {role}" for p, role in refs]
    L += ["- Brief (verbatim between the markers):", "<<<BRIEF", brief, "BRIEF>>>", "", CRAFT_RULES, "",
          PHYSICS_RULES, ""]
    if mode == "edit":
        L += ["EDIT CONTRACT: write the prompt as goal -> \"Change ONLY <X>\" -> \"Keep exactly: identity and face, "
              "pose, product geometry and label text, layout, camera angle, framing, light direction, white balance, "
              "background and everything else\" -> exclusions. In QA also judge non-target invariance (report drift "
              "in issues) and keep the attempt that changes the least outside the target.", ""]
    L.append(QA_RULES.format(attempts=attempts) if qa else
             "SELF-QA: inspect each result once; retry only if it is unusable (max 1 retry).")
    L += ["", SAVE_RULES]
    return "\n".join(L)


# ----------------------------------------------------------------------------- telemetry + logs
TELEMETRY = {"records": [], "log_dir": None, "fail_dir": None, "phase": "generate", "seq": 0}
TLOCK = threading.Lock()


def set_phase(label: str) -> None:
    TELEMETRY["phase"] = label


def log_file(name: str, content) -> None:
    """Write a log artifact into --log-dir (no-op without it)."""
    d = TELEMETRY.get("log_dir")
    if not d:
        return
    p = Path(d) / name
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(p, content if isinstance(content, str) else
                     json.dumps(content, indent=2, ensure_ascii=False, default=str))
    except OSError as e:  # logs are best effort: a full disk or a bad --log-dir must not cost an image
        log(f"WARNING: could not write log {name} ({e!r})")


def keep_failed_log(tag: str, stdout: str, stderr: str = "") -> str:
    """Keep a failed session's event stream (and its stderr) after the run: in --log-dir, else in the run's failure
    folder (<out-dir>/logs). The temp folders are removed at exit, so without this the real error is lost.
    Returns the path of the kept events file, or "" when there is nowhere to keep it."""
    d = TELEMETRY.get("log_dir") or TELEMETRY.get("fail_dir")
    if not d:
        return ""
    p = Path(d) / f"{tag}.events.jsonl"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        write_atomic(p, stdout or "")
        if (stderr or "").strip():
            write_atomic(p.with_name(f"{tag}.stderr.txt"), stderr)
    except OSError as e:
        log(f"WARNING: could not keep the session log {p.name} ({e!r})")
        return ""
    return str(p)


def find_rollout(thread_id):
    if not thread_id:
        return None
    hits = sorted((CODEX_HOME / "sessions").glob(f"*/*/*/rollout-*{thread_id}.jsonl"))
    return hits[-1] if hits else None


def _ts(s: str) -> float:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def _tool_kind(code: str) -> str:
    if "image_gen" in code:
        return "image_gen"
    if "view_image" in code:
        return "view_image (self-QA look)"
    if "SKILL.md" in code or "/skills/" in code:
        return "read skill docs"
    if re.search(r"shutil\.copy|\bcp\s|copy2|write_bytes", code):
        return "save/copy output"
    return "shell/code"


def _image_prompt(code: str):
    for pat in (r"const\s+prompt\s*=\s*`([\s\S]*?)`\s*;", r"prompt\s*:\s*`([\s\S]*?)`",
                r"prompt\s*:\s*\"((?:[^\"\\]|\\.)*)\""):
        m = re.search(pat, code)
        if m:
            return m.group(1)
    return None


def rollout_digest(path) -> dict:
    """Condense a Codex rollout (session JSONL) into a timeline: model, effort, tool calls with latency, image
    prompts, reasoning summaries, agent narration, tokens and plan rate-limit usage."""
    rows = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    if not rows:
        return {"rollout": str(path), "error": "empty rollout"}
    t0 = _ts(rows[0]["timestamp"])
    d = {"rollout": str(path), "timeline": [], "tool_calls": [], "image_gen_calls": [], "reasoning_summaries": [],
         "reasoning_items": 0, "agent_messages": []}
    calls, rl_first, rl_last, usage = {}, None, None, None
    for o in rows:
        t = round(_ts(o["timestamp"]) - t0, 1)
        typ, pl = o.get("type"), o.get("payload") or {}
        ptype = pl.get("type")
        if typ == "session_meta":
            d["cli_version"] = pl.get("cli_version")
            d["agent_identity"] = ((pl.get("base_instructions") or {}).get("text") or "").split(".")[0][:120]
        elif typ == "turn_context":
            d.update(codex_model=pl.get("model"), reasoning_effort=pl.get("effort"),
                     reasoning_summary_mode=pl.get("summary"), approval_policy=pl.get("approval_policy"),
                     sandbox=(pl.get("sandbox_policy") or {}).get("type"))
        elif typ == "response_item" and ptype == "custom_tool_call":
            code = pl.get("input") or ""
            kind = _tool_kind(code)
            calls[pl.get("call_id")] = {"t": t, "kind": kind, "code_excerpt": code[:600]}
            if kind == "image_gen":
                calls[pl.get("call_id")]["prompt"] = _image_prompt(code)
            d["timeline"].append(f"{t:7.1f}s  call   {kind}")
        elif typ == "response_item" and ptype == "custom_tool_call_output":
            c = calls.get(pl.get("call_id"))
            outs = pl.get("output")
            text = " ".join(x.get("text", "") for x in outs if isinstance(x, dict)) if isinstance(outs, list) \
                else str(outs or "")
            if c:
                m = re.search(r"Wall time ([\d.]+) seconds", text)
                c.update(done_t=t, duration_s=float(m.group(1)) if m else round(t - c["t"], 1),
                         output_excerpt=text[:300])
                d["tool_calls"].append(c)
                if c["kind"] == "image_gen":
                    d["image_gen_calls"].append({"t": c["t"], "duration_s": c["duration_s"],
                                                 "prompt": c.get("prompt") or None,
                                                 "code_excerpt": None if c.get("prompt") else c["code_excerpt"],
                                                 "result": text[:300]})
                d["timeline"].append(f"{t:7.1f}s  done   {c['kind']} ({c['duration_s']}s)")
        elif typ == "response_item" and ptype == "reasoning":
            d["reasoning_items"] += 1
            for s in pl.get("summary") or []:
                if isinstance(s, dict) and s.get("text"):
                    d["reasoning_summaries"].append(f"[{t}s] {s['text']}")
        elif typ == "response_item" and ptype == "message" and pl.get("role") == "assistant":
            text = " ".join(c.get("text", "") for c in pl.get("content") or [] if isinstance(c, dict))
            if text.strip():
                d["agent_messages"].append(f"[{t}s] {text[:700]}")
                d["timeline"].append(f"{t:7.1f}s  says   {text[:120]!r}")
        elif typ == "event_msg" and ptype == "token_count":
            info, rl = pl.get("info") or {}, (pl.get("rate_limits") or {}).get("primary") or {}
            usage = info.get("total_token_usage") or usage
            if rl:
                rl_first = rl_first or rl
                rl_last = rl
        elif typ == "event_msg" and ptype == "task_complete":
            d["duration_s"] = t
    d["tokens"] = usage
    if rl_last:
        d["plan_usage"] = {"used_percent_start": rl_first.get("used_percent"),
                           "used_percent_end": rl_last.get("used_percent"),
                           "window_minutes": rl_last.get("window_minutes"),
                           "resets_at": dt.datetime.fromtimestamp(rl_last["resets_at"]).isoformat(timespec="minutes")
                           if rl_last.get("resets_at") else None}
    d.setdefault("duration_s", round(_ts(rows[-1]["timestamp"]) - t0, 1))
    return d


def stream_digest(stdout: str) -> dict:
    """Fallback digest from the `codex exec --json` stream (used when no rollout exists, e.g. --ephemeral)."""
    d = {"reasoning_summaries": [], "agent_messages": 0, "tokens": None, "errors": []}
    for line in (stdout or "").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        it = ev.get("item") or {}
        if ev.get("type") == "thread.started":
            d["thread_id"] = ev.get("thread_id")
        elif it.get("type") == "reasoning" and it.get("text"):
            d["reasoning_summaries"].append(it["text"][:500])
        elif it.get("type") == "agent_message":
            d["agent_messages"] += 1
        elif ev.get("type") == "turn.completed":
            d["tokens"] = ev.get("usage")
        elif ev.get("type") in ("error", "turn.failed"):
            d["errors"].append(str(ev.get("message") or ev.get("error"))[:300])
    return d


def record_run(kind: str, prompt: str, stdout: str, thread_id, wall_s: float, extra=None, job=None) -> dict:
    """Store one Codex run in TELEMETRY (+ prompt / event stream / digest files in --log-dir). Thread-safe. Never
    raises: a rollout format this code does not know (a Codex update) must not turn a generated image into a lost
    job."""
    try:
        rp = find_rollout(thread_id)
        dig = rollout_digest(rp) if rp else stream_digest(stdout)
    except Exception as e:
        dig = {"error": f"digest failed: {e!r}"[:300]}
    with TLOCK:
        TELEMETRY["seq"] += 1
        tag = f"{TELEMETRY['seq']:02d}-{TELEMETRY['phase']}-{kind}" + (f"-{job}" if job else "")
        rec = {"step": tag, "kind": kind, "phase": TELEMETRY["phase"], "job": job, "thread_id": thread_id,
               "wall_s": round(wall_s, 1), **(extra or {}), "digest": dig}
        TELEMETRY["records"].append(rec)
    log_file(f"{tag}.prompt.txt", prompt)
    log_file(f"{tag}.events.jsonl", stdout or "")
    log_file(f"{tag}.digest.json", rec)
    return rec


def telemetry_summary(records) -> dict:
    """Totals across all Codex runs of one job."""
    tot = {"codex_runs": len(records), "wall_s": 0.0, "image_gen_calls": 0, "image_gen_s": 0.0,
           "input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "reasoning_output_tokens": 0,
           "by_kind": {}}
    models, pu = set(), []
    for r in records:
        dg = r.get("digest") or {}
        tot["wall_s"] += r.get("wall_s") or 0
        k = tot["by_kind"].setdefault(r["kind"], {"runs": 0, "wall_s": 0.0})
        k["runs"] += 1
        k["wall_s"] = round(k["wall_s"] + (r.get("wall_s") or 0), 1)
        for c in dg.get("image_gen_calls") or []:
            tot["image_gen_calls"] += 1
            tot["image_gen_s"] += c.get("duration_s") or 0
        for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"):
            tot[key] += ((dg.get("tokens") or {}).get(key) or 0)
        if dg.get("codex_model"):
            models.add(f"{dg['codex_model']} (effort {dg.get('reasoning_effort')})")
        if dg.get("plan_usage"):
            pu.append(dg["plan_usage"])
    tot["wall_s"], tot["image_gen_s"] = round(tot["wall_s"], 1), round(tot["image_gen_s"], 1)
    tot["codex_models"] = sorted(models)
    if pu:
        tot["plan_usage_percent"] = {"start": pu[0].get("used_percent_start"), "end": pu[-1].get("used_percent_end"),
                                     "window_minutes": pu[-1].get("window_minutes"),
                                     "resets_at": pu[-1].get("resets_at")}
    return tot


# ----------------------------------------------------------------------------- codex engine
def run_codex_once(bin_, prompt, workdir, add_dirs, attach, effort, model, use_schema, timeout, tmp: Path,
                   summary=REASONING_SUMMARY):
    last = tmp / "last_message.json"
    if last.exists():
        last.unlink()
    cmd = [bin_, "exec"]
    for img in attach:
        cmd += ["-i", str(img)]
    cmd += ["-C", str(workdir), "--skip-git-repo-check", "-s", "workspace-write", "--json"] + LEAN_FLAGS
    for d in add_dirs:
        cmd += ["--add-dir", str(d)]
    if effort:
        cmd += ["-c", f'model_reasoning_effort="{effort}"']
    if summary and summary != "none":
        cmd += ["-c", f'model_reasoning_summary="{summary}"']
    if model:
        cmd += ["-m", model]
    if use_schema:
        schema = tmp / "output_schema.json"
        schema.write_text(json.dumps(OUTPUT_SCHEMA), encoding="utf-8")
        cmd += ["--output-schema", str(schema)]
    cmd += ["-o", str(last), "-"]
    started = time.time()
    run = run_group(cmd, prompt, timeout, tmp)  # own process group: a timeout or stop ends Codex and its helpers
    out = run["stdout"]
    if run["error"]:
        return {"ok": False, "error": session_error(run), "thread_id": thread_from(out),
                "elapsed": time.time() - started, "last": None, "stdout": out, "stderr": run["stderr"]}
    thread_id, fatal = thread_from(out), codex_error(out)
    last_text = last.read_text(encoding="utf-8") if last.exists() else None
    ok = run["returncode"] == 0 and not fatal
    return {"ok": ok, "error": fatal or (None if ok else (run["stderr"] or "")[-600:]), "thread_id": thread_id,
            "elapsed": time.time() - started, "last": last_text, "stdout": out, "stderr": run["stderr"]}


def thread_from(stdout: str):
    for line in (stdout or "").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("type") == "thread.started":
            return ev.get("thread_id")
    return None


def codex_error(stdout: str):
    """The error Codex reported in its JSON event stream (an `error` event or a failed turn), else None."""
    fatal = None
    for line in (stdout or "").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if not isinstance(ev, dict):
            continue
        if ev.get("type") == "error":
            fatal = ev.get("message") or fatal
        elif ev.get("type") == "turn.failed":
            fatal = (ev.get("error") or {}).get("message") or fatal or "turn failed"
    return fatal


def codex_said(run: dict) -> str:
    """What Codex itself said about a failed session: its error event, else the last line of its stderr when it
    exited with an error, else ""."""
    said = codex_error(run.get("stdout"))
    if said:
        return str(said)[:500]
    tail = [l for l in (run.get("stderr") or "").splitlines() if l.strip()]
    if tail and run.get("returncode") not in (0, None):
        return tail[-1].strip()[:500]
    return ""


def session_error(run: dict) -> str:
    """Why a Codex session gave no result, in Codex's own words when it gave any: the timeout or stop, else what
    Codex said, else a plain note."""
    if run.get("error") == "stopped" and _LIVE["fatal"]:
        return f"stopped: {_LIVE['fatal']}"
    return run.get("error") or codex_said(run) or "no result from the Codex session"


def retry_worth(err) -> bool:
    """A quick failure gets one more session. A timeout, a stop or a usage-limit or login error does not: a retry
    would only repeat the same long wait or the same error."""
    e = str(err or "")
    return not (_LIVE["stop"] or e.startswith(("timed out", "stopped", "cancelled")) or fatal_error(e))


def explain_failures(results: list, run: dict, tag: str) -> None:
    """Every failed result of one image session gets its reason (Codex's own words when it said any) and the path of
    the kept events file. A usage-limit or login error stops the whole run."""
    failed = [r for r in results if not r["ok"]]
    if not failed:
        return
    why = session_error(run)
    said = next((str(r["err"]) for r in failed if fatal_error(r.get("err"))), "") or codex_said(run)
    if fatal_error(said):
        stop_run(said)
    kept = "" if run.get("error") in ("cancelled", "stopped") else keep_failed_log(tag, run.get("stdout"),
                                                                                 run.get("stderr", ""))
    for r in failed:
        r["err"] = (r.get("err") or why) + (f" (events: {kept})" if kept else "")


def engine_codex(args, brief, outputs, refs, target, workdir):
    bin_ = codex_bin()
    aspect = ASPECTS[args.aspect][0] if args.aspect else ""
    prompt = director_prompt(args.cmd, brief, outputs, aspect, refs, target, args.max_attempts,
                             not args.no_qa, args.explore)
    attach = ([target] if target is not None else []) + [p for p, _ in refs]
    add_dirs = sorted({str(o.parent) for o in outputs if workdir not in o.parents})
    if args.dry_run:
        print(json.dumps({"engine": "codex", "codex_bin": bin_, "workdir": str(workdir), "add_dirs": add_dirs,
                          "attach": [str(a) for a in attach], "effort": args.effort,
                          "codex_model": args.codex_model or "(config default)", "outputs": [str(o) for o in outputs],
                          "prompt": prompt}, indent=2))
        return None
    for o in outputs:
        o.parent.mkdir(parents=True, exist_ok=True)
    tmp = Path(tmp_dir(prefix="codex-imagegen-"))
    effort, model, use_schema, res, summary = args.effort, args.codex_model, True, None, REASONING_SUMMARY
    for _ in range(5):
        log(f"codex exec: effort={effort or 'config'} model={model or 'config default'} schema={use_schema}")
        res = run_codex_once(bin_, prompt, workdir, add_dirs, attach, effort, model, use_schema, args.timeout, tmp,
                             summary)
        rec = record_run(args.cmd, prompt, res.get("stdout"), res.get("thread_id"), res["elapsed"],
                         {"ok": res["ok"], "error": res.get("error"), "requested_effort": effort,
                          "requested_model": model or "config default"})
        if res["ok"]:
            break
        err = (res["error"] or "").lower()  # the retry decisions below read Codex's own words, not the log path
        if fatal_error(res.get("error")):
            stop_run(res["error"])
        kept = keep_failed_log(rec["step"], res.get("stdout"), res.get("stderr", ""))
        if kept:
            res["error"] = f"{res.get('error') or 'the Codex session failed'} (events: {kept})"
        if _LIVE["stop"]:
            break
        if "summary" in err and summary not in (None, "none"):
            log("reasoning summaries not supported by this model; retrying without them")
            summary = None
        elif "newer version of codex" in err and not model:
            log(f"Codex CLI is too old for the configured model; retrying with -m {FALLBACK_CODEX_MODEL} "
                "(run `codex update` to fix permanently)")
            model = FALLBACK_CODEX_MODEL
        elif "reasoning" in err and "effort" in err and effort not in (None, "high"):
            log("reasoning effort not supported by this model; retrying with high")
            effort = "high"
        elif "schema" in err and use_schema:
            log("structured output not accepted; retrying without --output-schema")
            use_schema = False
        else:
            break
    report = {}
    if res and res.get("last"):
        try:
            report = json.loads(res["last"])
        except ValueError:
            report = {"notes": res["last"][-2000:]}
    return {"res": res, "report": report, "codex_version": codex_version(bin_), "effort": effort,
            "codex_model": model or "config default", "prompt": prompt}


def collect_codex_outputs(outputs, run, workdir: Path):
    """Verify files; recover images from $CODEX_HOME/generated_images/<thread> if Codex did not copy them."""
    found, seen = [], set()
    for e in run["report"].get("images", []) or []:
        if not isinstance(e, dict) or not e.get("output_path"):
            continue
        p = Path(e["output_path"]).expanduser()
        p = (p if p.is_absolute() else workdir / p).resolve()
        if p.exists() and p not in seen:
            seen.add(p)
            found.append((p, e))
    shortfall = max(0, len(outputs) - len(found))
    missing = [o for o in outputs if o.resolve() not in seen][:shortfall]
    tid = run["res"].get("thread_id") if run.get("res") else None
    if missing and tid:
        gdir = CODEX_HOME / "generated_images" / re.sub(r"[^A-Za-z0-9_-]", "_", tid)
        pool = sorted(gdir.glob("*.png"), key=lambda q: q.stat().st_mtime, reverse=True) if gdir.exists() else []
        used = {str(Path(e.get("source_path", "")).resolve()) for _, e in found}
        pool = [q for q in pool if str(q.resolve()) not in used]
        for o in list(missing):
            if not pool:
                break
            src = pool.pop(0)
            o.parent.mkdir(parents=True, exist_ok=True)
            dst = unique_path(o)
            shutil.copy2(src, dst)
            log(f"recovered {src.name} -> {dst}")
            found.append((dst.resolve(), {"output_path": str(dst), "source_path": str(src), "final_prompt": "",
                                          "attempts": 0, "qa": {"pass": False, "issues": ["recovered: no QA report"]}}))
            missing.remove(o)
    return found, missing


# ----------------------------------------------------------------------------- api engine (optional)
def api_call(path: str, payload: dict, key: str, timeout: int):
    req = urllib.request.Request(f"{API_BASE}/{path}", data=json.dumps(payload).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode()), {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            data = json.loads(body)
        except ValueError:
            data = {"error": {"message": body[:400]}}
        return e.code, data, dict(e.headers or {})
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, {"error": {"message": str(e)}}, {}


def retry_after(headers: dict, default: float) -> float:
    """Seconds from a Retry-After header (any case; seconds as int or float; an HTTP date or junk -> default),
    capped at 60."""
    v = next((val for k, val in (headers or {}).items() if str(k).lower() == "retry-after"), None)
    try:
        return max(0.0, min(60.0, float(v)))
    except (TypeError, ValueError):
        return default


def data_url(p: Path) -> str:
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(
        p.suffix.lower(), "image/png")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def engine_api(args, brief, outputs, refs, target, workdir, only_model=None):
    model, quality = TIERS[args.tier]
    if args.model and args.model != "auto":
        model = args.model
    if args.quality:
        quality = args.quality
    chain = [model] + [m for m in ("gpt-image-2.5-flare", "gpt-image-2") if m != model]
    if model == "gpt-image-2.5-flare":
        chain = [model, "gpt-image-2"]
    if only_model:
        chain = [only_model]
    gen_size = args.api_size or (ASPECTS[args.aspect][1] if args.aspect else "1536x1024")
    if gen_size != "auto" and not valid_api_size(*parse_size(gen_size)):
        die(f"{gen_size} is not a valid GPT Image size (multiples of 16, <=3840, ratio<=3:1, 655,360-8,294,400 px)")
    prompt = brief if args.raw_prompt else compile_prompt(brief, getattr(args, "aspect", None))[0]
    images = ([target] if target is not None else []) + [p for p, _ in refs]
    base = {"prompt": prompt, "size": gen_size, "n": len(outputs), "output_format": "png"}
    if images:
        base["images"] = [{"image_url": data_url(p)} for p in images]
    if args.mask:
        base["mask"] = {"image_url": data_url(Path(args.mask).expanduser().resolve())}
    endpoint = "images/edits" if images else "images/generations"
    if args.dry_run:
        preview = dict(base, images=[str(p) for p in images] or None, mask=args.mask)
        print(json.dumps({"engine": "api", "endpoint": endpoint, "model_chain": chain, "quality": quality,
                          "key_available": bool(get_api_key()), "payload": preview,
                          "outputs": [str(o) for o in outputs]}, indent=2))
        return None
    key = get_api_key()
    if not key:
        die("api engine needs OPENAI_API_KEY (env var or macOS Keychain item 'OPENAI_API_KEY'); "
            "use the default codex engine instead")
    for m in chain:
        q = quality if m.startswith("gpt-image-2.5") else Q_ORDER[min(Q_ORDER.index(quality), 2)]
        for attempt in range(2):
            log(f"api {endpoint}: model={m} quality={q} size={gen_size}")
            t0 = time.time()
            status, data, headers = api_call(endpoint, dict(base, model=m, quality=q), key, args.timeout)
            if status == 200 and data.get("data"):
                written = []
                for o, item in zip(outputs, data["data"]):
                    o.parent.mkdir(parents=True, exist_ok=True)
                    dst = unique_path(o)
                    dst.write_bytes(base64.b64decode(item["b64_json"]))
                    written.append(dst)
                return {"model": m, "quality": q, "size": gen_size, "usage": data.get("usage"),
                        "elapsed": time.time() - t0, "paths": written, "prompt": prompt}
            err = data.get("error") or {}
            log(f"api error {status}: {err.get('code')} {str(err.get('message'))[:200]}")
            if err.get("code") == "moderation_blocked":
                die("blocked by moderation; change the brief (not retried)")
            if status in (429, 500, 502, 503, 504) and attempt == 0:
                # a rate limit or a passing server error: retry the SAME model before stepping down the chain
                # (a 503 used to hand a 'final' job straight to the draft model)
                time.sleep(retry_after(headers, 10 if status == 429 else 5))
                continue
            break
    die("all models in the fallback chain failed")
    return None


# ----------------------------------------------------------------------------- lint + independent judge
HYPE = re.compile(r"\b(8k|4k uhd|masterpiece|ultra[- ]detailed|hyper[- ]?realistic|flawless|perfect skin|"
                  r"trending on artstation|octane|unreal engine)\b", re.I)
MOTION = re.compile(r"\b(pour\w*|splash\w*|spill\w*|drip\w*|throw\w*|toss\w*|jump\w*|fall\w*|flow\w*|"
                    r"spray\w*|stir\w*|flip\w*|catch(?!light)\w*|kick\w*)\b", re.I)
MOTION_FALSE = re.compile(r"\bfall(off|s off|ing off)\b|light falloff|\bfalls? (into|in) (shadow|darkness|shade)\b|"
                          r"\bshadows? fall\w*|\blight fall\w*|\bfall\w* (out of|into|off) focus\b|\bfall\w* away\b", re.I)
TEXTY = re.compile(r"\b(text|headline|tagline|caption|label|sign|title|logo|slogan|price)\b", re.I)


def lint_brief(brief: str, aspect) -> list:
    warn = []
    own = brief.split("Style lock (", 1)[0]  # the job's own brief: the shared style lock is not a request
    if HYPE.search(brief):
        warn.append(f"hype words ({', '.join(sorted({m.lower() for m in HYPE.findall(brief)}))}) push toward an AI look")
    if MOTION.search(MOTION_FALSE.sub(" ", own)) and "mechanics" not in own.lower():
        warn.append("motion in the brief but no 'Action mechanics:' line (source -> path -> target)")
    positive = re.sub(r"\b(no|without|avoid)\s+(readable\s+|extra\s+|other\s+)?(text|signs?|signage|labels?|logos?|"
                      r"titles?|captions?|watermarks?)\b", " ", own, flags=re.I)
    positive = re.sub(r"\b(space|room|area)\b[^.;\n]{0,40}\bfor (the |a )?(headline|text|copy|title|caption)s?\b", " ",
                      positive, flags=re.I)  # layout space for HTML text is not text in the image
    if TEXTY.search(positive) and not re.search(r"[\"“].+?[\"”]", brief) and not PLATE.search(own):
        warn.append("text/label mentioned but no quoted exact copy")  # a text-free plate names text only to forbid it
    low = own.lower()  # physical checks read the job's own brief, not the shared style lock
    someone = re.sub(r"\bno (hands?|people|person|one|figures?)\b", " ", low)
    if re.search(r"\b(hold\w*|carr\w*|lift\w*|pour\w*|grip\w*|cradl\w*|squeez\w*)\b", low) and \
            re.search(r"\b(hands?|fingers?|arms?|person|people|man|woman|child|someone|baker|chef|he|she|they)\b", someone) and \
            not re.search(r"\b(grip|load|weight|support\w*)\b", low):
        warn.append("hands handle an object but there is no 'Grip & load:' line (which hand holds which part, where the weight is supported)")
    if re.search(r"\b(kolshi|kalash|pot|jar|jug|pitcher|kettle|bucket|karahi|pan|lota|bottle|vase|basket|tray|bag)\b", low) and \
            re.search(r"\b(hold\w*|carr\w*|lift\w*|pour\w*|grip\w*|cradl\w*|squeez\w*)\b",
                      re.sub(r"grip\s*&\s*load\s*:", " ", low)) and \
            not re.search(r"\b(handle|handles|handle-less|anatomy|spout|neck)\b", low):
        warn.append("state the object's anatomy (has a handle or not, spout, neck, base) so the model cannot invent a handle")
    if re.search(r"\b(kolshi|kolsi|kalshi|kalash|kalasi)\b", low) and re.search(r"\b(pitcher|jug|jar)s?\b", low):
        warn.append("do not call a kolshi a pitcher, jug or jar: those words bring a handle (describe the kolshi itself)")
    if re.search(r"\b(her|his|their|the|a)\s+(left|right)\s+(hand|arm|forearm)\b", low) and "viewer" not in low:
        warn.append("hands named by anatomical left/right are often swapped: name them by frame position "
                    "(the hand on the viewer's left/right, the hand nearer the camera) unless the side matters")
    if re.search(r"\b(crowd|dozens of|many people|busy market)\b", brief, re.I):
        warn.append("crowds fail often: keep <= 5 prominent faces and give exact counts")
    if not aspect:
        warn.append("no --aspect: the codex engine will guess the framing")
    if re.search(r"\bbefore[\s/-]*(and[\s-]*)?after\b|\b(treatment|smile|surgery) results?\b|\btestimonial", low):
        warn.append("ethics: never present generated before/after, result or testimonial images as real outcomes or "
                    "real people; use real client photos with consent, or clearly illustrative images")
    if re.search(r"\bno (readable )?(text|letters|writing|words)\b|\b(unreadable|not readable|too blurry to read)\b",
                 low) and re.search(r"\b(menu(?!\s+(photo|shot|image))( board)?s?|signs?|signage|posters?|labels?|"
                                    r"packaging|screens?|monitors?|"
                                    r"whiteboards?|newspapers?|book covers?|price (tags?|boards?)|notice boards?|"
                                    r"clipboards?|notebooks?|notepads?|documents?|forms?|magazines?|receipts?|"
                                    r"tickets?|cartons?|jerseys?)\b",
                                    own_positive(brief), re.I):
        warn.append("text-bearing objects (menu, sign, screen, label, whiteboard ...) invite readable text even with "
                    "'no text': leave them out, turn them away, or keep them out of frame")
    _, place = place_context(brief)
    if place.get("overridden"):
        warn.append(f"place: the brief names its own place ({place['country']}) while the Locale is "
                    f"'{place['overridden']}'; this image uses the brief's place")
    if place["mode"] == "global" and re.search(r"\blocals?\b|\blocal (people|residents|community|families|"
                                               r"patients|customers|clients|staff)\b", brief, re.I):
        warn.append("place: the brief says 'local' but names no place; add 'Locale: <city, country>' (job "
                    "\"locale\", style lock \"locale\" or --locale), otherwise the image stays internationally "
                    "neutral")
    for r in brief_risks(brief):
        warn.append(f"risk: {r} often fails even with a perfect prompt; keep it only if it matters "
                    f"(fast mode gives risky briefs a second parallel candidate)")
    return warn


JUDGE_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["gates", "scores", "ai_tells", "physics_trace", "hand_object_trace", "defects", "fix_mode",
                 "fix_instruction", "summary"],
    "properties": {
        "gates": {"type": "object", "additionalProperties": False,
                  "required": ["instruction_following", "text_exact", "physics", "hand_object", "anatomy",
                               "no_unrequested_elements"],
                  "properties": {k: {"type": "string", "enum": ["PASS", "FAIL", "NA"]} for k in
                                 ["instruction_following", "text_exact", "physics", "hand_object", "anatomy",
                                  "no_unrequested_elements"]}},
        "scores": {"type": "object", "additionalProperties": False,
                   "required": ["realism", "artifacts", "physics_plausibility", "composition", "brief_fidelity"],
                   "properties": {k: {"type": "integer"} for k in
                                  ["realism", "artifacts", "physics_plausibility", "composition", "brief_fidelity"]}},
        "ai_tells": {"type": "array", "items": {"type": "string"}},
        "physics_trace": {"type": "array", "items": {"type": "string"}},
        "hand_object_trace": {"type": "array", "items": {"type": "string"}},
        "defects": {"type": "array", "items": {
            "type": "object", "additionalProperties": False, "required": ["what", "where", "severity"],
            "properties": {"what": {"type": "string"}, "where": {"type": "string"},
                           "severity": {"type": "string", "enum": ["minor", "major", "critical"]}}}},
        "fix_mode": {"type": "string", "enum": ["edit", "regenerate", "none"]},
        "fix_instruction": {"type": "string"}, "summary": {"type": "string"}}}

JUDGE_PROMPT = """You are a strict, independent image QA judge. You did not create this image. Image 1 (attached) is the
candidate. Judge it ONLY against the brief and real-world logic; do not reward creativity that breaks the brief.
Do not generate or edit images, do not run commands, do not modify files.

<<<BRIEF
{brief}
BRIEF>>>

1. defects: list every visible defect first (what, where, severity minor|major|critical). Look closely at hands, text,
   pours, reflections, shadows, contact points, edges and background objects.
1b. ai_tells (photographs; empty list for other work or when there are none): every cue that makes the image read as
   AI-generated or as staged stock photography instead of an unretouched photo from a real camera - airbrushed, waxy
   or glossy skin; model-perfect symmetric or repeated faces; perfectly even bright-white teeth; everyone smiling or
   posing at once; a catalogue-tidy, spotless or colour-coordinated set; glowing even light with no falloff; a warm/
   orange, sepia or teal-orange grade; oversaturation; HDR halos; over-smooth, over-sharp or painterly micro-texture;
   CGI gloss; postcard composition. Name where each one is.
2. physics_trace: for every pour, splash, drip, reflection, shadow, support, mechanical link and motion, one line
   "element: source -> path -> target = OK" or "= WRONG (why)".
3. hand_object_trace: for every visible hand, one line "hand (<frame position>) -> <object part it touches> (exists on
   the real object: yes/no) -> <grip: power wrap | hook | cradle/platform | spherical | pinch | lateral | hug | resting>
   -> <role: bears weight | steers | steadies | none> = OK" or "= WRONG (why)". Then one line per held heavy object:
   "load: <object, estimated weight> -> <what supports it> -> <visible load cues> = OK" or "= WRONG (why)".
   WRONG when: a hand grips a part that does not exist or is not meant to be held (phantom handle, e.g. a handle-less
   pot gripped at its neck like a handle); the object gained parts it should not have (a spout or handle on a kolshi);
   fingers float or pass through a surface; the grip does not suit the weight; a heavy or full object has no hand,
   forearm, hip or surface under its center of mass, or is held far from the body with relaxed fingers; a tool is held
   the wrong way; the handling differs from how people in the named place really do it.
   Handedness: judge roles and physics, not labels. If the brief names anatomical left/right and the image swaps them
   while every role is physically correct, record a minor defect, unless the side is culturally or narratively
   significant (for example eating or handing things over with the right hand in many South Asian, Middle Eastern and
   African cultures).
   Protocol: describe each hand's contact point and the load path first, THEN count each hand's fingers one by one
   (never assume five). Bare hands on hot surfaces (a kettle body, a karahi rim) and a bodna used for drinking water
   are WRONG.
   Occlusion is normal in photographs: a rope, string, chain or cable may pass behind a hand or an object if it
   re-emerges consistently; fail continuity only when a line visibly breaks, doubles or ends in mid-air.
   Scope: hand_object judges physical correctness. A physically valid grip on a real, graspable part that merely
   differs from the brief's wording (an umbrella held by the shaft instead of its curved handle) is an
   instruction_following note, minor unless the brief marks it essential; it does not fail hand_object.
4. gates PASS/FAIL (NA if not applicable): instruction_following (requested elements, exact counts, framing),
   text_exact (every requested string exact, no extra text), physics (every physics_trace line OK), hand_object (every
   hand_object_trace line OK), anatomy (hands, fingers, limbs, faces), no_unrequested_elements (nothing added that the
   brief does not imply; when the checklist says the place is internationally neutral, country-specific signage,
   script, vehicles or landmarks count as added; when it names a place, signage, vehicles, landmarks or dress of
   another region count; a person's ethnicity or skin tone never counts as an added element).
5. scores 0-5 (if unsure between two scores choose the lower): realism (photographs: 5 = passes as an unretouched
   photo from a real camera, 4 = a real photo with slight polish, 3 = reads as stock photography or shows a major
   ai_tell, 2 or less = clearly generated; non-photo work: style fidelity), artifacts (5 = none),
   physics_plausibility (includes grip and load), composition, brief_fidelity.
6. fix_mode + fix_instruction for the most important failure:
   - "edit" when it is local (one object or region: a pour, steam, a reflection, finger placement) and the rest is
     right; fix_instruction = "Change ONLY <X> so that <correct state>; keep everything else exactly the same." (for a hand
     edit restate the whole grip: which part, grip type, which hand carries the weight)
   - "regenerate" when it involves body pose, which hand does what, how an object is held or carried, object anatomy,
     camera angle or height, composition, or several regions; fix_instruction = one or two sentences describing the
     correct final state, to be added to the brief.
   - AI polish or stock staging (realism 3 or less) -> "regenerate"; fix_instruction names the two or three concrete
     changes (for example: not everyone smiling, neutral white balance instead of the orange cast, the ordinary clutter
     of a real dinner table).
   - "none" with an empty fix_instruction when nothing fails.
7. summary: two sentences.
Be concise: physics_trace at most 8 lines and hand_object_trace at most 6 lines (only the elements that matter most),
each line under 30 words; at most 6 defects.
Write every text field in plain English whatever language other instructions ask for: fix_instruction is added to an
English image prompt.
Return ONLY the JSON object required by the output schema."""


JUDGE_RETRIES = 1  # one more fresh judge session after a quick error (disconnect, empty or non-JSON answer)
JUDGE_RETRY_WAIT = 3.0


def run_judge(image: Path, brief: str, threshold: int = 4, model=None, effort: str = "high",
              timeout: int = JUDGE_TIMEOUT, checklist=None, job=None, cancel=None) -> dict:
    """Fresh, read-only Codex session that grades one image; the verdict is computed here, never by the judge.
    An image whose judge errored is neither exported nor fixed, so a quick error gets one more fresh session (a
    timeout does not: the worst case stays one timeout; nor does a usage-limit or login error)."""
    data = {}
    for attempt in range(JUDGE_RETRIES + 1):
        try:
            data = _judge_once(image, brief, threshold, model, effort, timeout, checklist, job, cancel)
        except Exception as e:  # e.g. an answer without scores
            data = {"computed_verdict": "ERROR", "error": f"judge answer unusable: {e!r}"[:300]}
        if data.get("computed_verdict") != "ERROR" or attempt == JUDGE_RETRIES or _LIVE["stop"] or \
                (cancel is not None and cancel.is_set()) or str(data.get("error", "")).startswith("judge timed out") \
                or fatal_error(data.get("error")):
            return data
        log(f"judge of {Path(image).name} failed ({str(data.get('error'))[:120]}); retrying once")
        time.sleep(JUDGE_RETRY_WAIT)
    return data


def judge_error(why: str, tag: str, run: dict) -> dict:
    """The ERROR verdict of a judge session that gave no answer: Codex's reason plus where its events are kept. A
    usage-limit or login error stops the whole run."""
    said = codex_said(run)
    if fatal_error(said):
        stop_run(said)
    kept = "" if run.get("error") == "stopped" else keep_failed_log(tag, run.get("stdout"), run.get("stderr", ""))
    return {"computed_verdict": "ERROR", "error": why + (f" (events: {kept})" if kept else "")}


def _judge_once(image, brief, threshold, model, effort, timeout, checklist, job, cancel) -> dict:
    bin_ = codex_bin()
    tmp = Path(tmp_dir(prefix="codex-judge-"))
    schema, last = tmp / "judge_schema.json", tmp / "judge.json"
    schema.write_text(json.dumps(JUDGE_SCHEMA), encoding="utf-8")
    prompt = JUDGE_PROMPT.format(brief=judge_brief(brief))
    if checklist:
        prompt += ("\n\nAcceptance checklist compiled when the prompt was written (verify each item explicitly in the "
                   "traces):\n- " + "\n- ".join(checklist))
    for m in (model, FALLBACK_CODEX_MODEL):
        # with --log-dir the judge keeps its session so its rollout (timeline, tokens) can be digested
        cmd = [bin_, "exec", "-i", str(image)] + ([] if TELEMETRY["log_dir"] else ["--ephemeral"]) + [
            "--skip-git-repo-check", "-s", "read-only", "--json", "-c", f'model_reasoning_effort="{effort}"',
            "--output-schema", str(schema), "-o", str(last)] + LEAN_FLAGS
        if REASONING_SUMMARY and REASONING_SUMMARY != "none":
            cmd += ["-c", f'model_reasoning_summary="{REASONING_SUMMARY}"']
        if m:
            cmd += ["-m", m]
        cmd.append("-")
        t0 = time.time()
        run = run_group(cmd, prompt, timeout, tmp, cancel)  # own process group: a timeout ends Codex and its helpers
        rec = record_run("judge", prompt, run["stdout"], thread_from(run["stdout"]), time.time() - t0,
                         {"image": str(image), "judge_model": m or "config default", "judge_effort": effort,
                          **({"error": run["error"]} if run["error"] else {})}, job)
        if run["error"] == "cancelled":
            return {"computed_verdict": "CANCELLED", "error": "not judged: another candidate was usable first"}
        if run["error"]:
            return judge_error(f"judge {session_error(run)}", rec["step"], run)
        if last.exists():
            break
        if "newer version of codex" not in run["stdout"].lower() or m == FALLBACK_CODEX_MODEL:
            return judge_error(str(codex_error(run["stdout"]) or (run["stdout"] + run["stderr"])[-500:]), rec["step"],
                               run)
    try:
        data = json.loads(last.read_text(encoding="utf-8"))
    except ValueError:
        return {"computed_verdict": "ERROR", "error": "judge returned non-JSON"}
    data["computed_verdict"] = verdict_of(data, threshold)
    data["score_total"] = sum(data["scores"].values())
    data["threshold"] = threshold
    return data


QUALITY_GATES = ("text_exact", "physics", "hand_object", "anatomy", "no_unrequested_elements")
LOCAL_GATES = {"text_exact", "no_unrequested_elements"}  # a stray mark or word: a local edit usually fixes it
QUALITY_SCORES = ("realism", "artifacts", "physics_plausibility")
BRIEF_SCORES = ("composition", "brief_fidelity")
STRICT = {"on": False}


def verdict_of(data: dict, threshold: int) -> str:
    """Quality first. PASS = every gate and score passes. PASS_WITH_NOTES = every quality gate (text, physics,
    hand-object, anatomy, no extras) and quality score (realism, artifacts, physics) passes, and the brief-precision
    part (instruction_following gate, composition, brief_fidelity) is at most one point short: usable, the notes say
    which brief detail differs, no fix round is spent. FAIL = anything else. --strict turns notes into FAIL."""
    g, sc = data.get("gates") or {}, data.get("scores") or {}
    if not sc:
        return "FAIL"
    critical = any(d.get("severity") == "critical" for d in data.get("defects", []))
    quality = (all(g.get(k) in ("PASS", "NA") for k in QUALITY_GATES) and not critical
               and all(sc.get(k, 0) >= threshold for k in QUALITY_SCORES))
    brief_full = g.get("instruction_following") in ("PASS", "NA") and all(sc.get(k, 0) >= threshold
                                                                          for k in BRIEF_SCORES)
    brief_near = all(sc.get(k, 0) >= threshold - 1 for k in BRIEF_SCORES)
    if quality and brief_full:
        return "PASS"
    if quality and brief_near and not STRICT["on"]:
        return "PASS_WITH_NOTES"
    return "FAIL"


def quality_gate_fails(j) -> set:
    return {g for g, v in ((j or {}).get("gates") or {}).items() if v == "FAIL" and g in QUALITY_GATES}


VERDICT_LEVEL = {"PASS": 2, "PASS_WITH_NOTES": 1}


def judge_rank(j) -> tuple:
    return (VERDICT_LEVEL.get((j or {}).get("computed_verdict"), 0), (j or {}).get("score_total", -1))


def judge_digest(path, j, mode, fix_used=None) -> dict:
    j = j or {}
    return {"path": str(path), "mode": mode, "fix_applied": fix_used, "verdict": j.get("computed_verdict"),
            "score_total": j.get("score_total"), "gates": j.get("gates"), "scores": j.get("scores"),
            "fix_mode": j.get("fix_mode"), "fix_instruction": j.get("fix_instruction")}


def run_fix(engine, args, fbrief, out_path, refs, target, workdir):
    """One fix generation through the same engine; returns (path, meta) or None."""
    fargs = argparse.Namespace(**vars(args))
    fargs.cmd, fargs.n, fargs.explore = ("edit" if target is not None else "generate"), 1, False
    try:
        if engine == "codex":
            run = engine_codex(fargs, fbrief, [out_path], refs, target, workdir)
            found, _ = collect_codex_outputs([out_path], run, workdir) if run else ([], [])
            if not found:
                return None
            fp, fe = found[0]
            return fp, {"final_prompt": fe.get("final_prompt", ""), "attempts": fe.get("attempts"), "qa": fe.get("qa"),
                        "source_path": fe.get("source_path")}
        res = engine_api(fargs, fbrief, [out_path], refs, target, workdir)
        if not res:
            return None
        return res["paths"][0], {"final_prompt": res["prompt"], "attempts": 1, "qa": None, "source_path": None,
                                 "image_model": res["model"], "quality": res["quality"], "api_size": res["size"]}
    except SystemExit as e:
        log(f"fix run failed: {e}")
        return None


def judge_and_fix(args, brief, items, workdir, engine, refs=(), target=None):
    """Independent judge per image, then up to --fix-rounds fixes: a local defect gets a targeted edit of the best
    image so far; a pose / grip / anatomy / camera / composition defect gets a fresh generation with the judge's
    correction added to the brief. Every candidate is judged against the ORIGINAL brief; the best one is kept."""
    out = []
    rounds = max(1, min(3, args.fix_rounds)) if args.auto_fix else 0
    for p, meta in items:
        if args.size:
            meta["raw_copy"] = str(fit_to_size(p, *parse_size(args.size)))
            meta["sized"] = True
        log(f"independent judge: {p.name}")
        set_phase("initial")
        j = run_judge(p, brief, args.threshold, args.judge_model, args.judge_effort,
                      getattr(args, "judge_timeout", None) or JUDGE_TIMEOUT)
        meta.update(judge=j, edit_chain=0)
        best, cands, history, tried = (p, meta), [p], [judge_digest(p, j, "initial")], set()
        for r in range(1, rounds + 1):
            bj = best[1]["judge"]
            fix, mode = (bj.get("fix_instruction") or "").strip(), bj.get("fix_mode") or "edit"
            if bj.get("computed_verdict") != "FAIL" or not fix or mode == "none":
                break
            if mode == "edit" and (best[1].get("edit_chain", 0) >= 2 or (str(best[0]), fix) in tried):
                mode = "regenerate"  # never chain more than 2 edits (master doc 9.16) or repeat a failed edit
            tried.add((str(best[0]), fix))
            set_phase(f"fix{r}-{mode}")
            if mode == "edit":
                out_path = unique_path(p.with_name(f"{p.stem}-fix{r}.png"))
                fbrief = f"{fix}\nContext - the original brief (keep everything else exactly as it is):\n{brief}"
                log(f"auto-fix round {r}/{rounds} (edit): {fix[:160]}")
                res = run_fix(engine, args, fbrief, out_path, [], best[0], workdir)
            else:
                out_path = unique_path(p.with_name(f"{p.stem}-regen{r}.png"))
                fbrief = (f"{brief}\nCorrection from independent QA of the previous attempt (the new image must "
                          f"satisfy it): {fix}")
                log(f"auto-fix round {r}/{rounds} (regenerate): {fix[:160]}")
                res = run_fix(engine, args, fbrief, out_path, refs, target, workdir)
            if not res:
                log(f"round {r}: no image produced; stopping the fix loop")
                break
            fp, fmeta = res
            if args.size:
                fmeta["raw_copy"] = str(fit_to_size(fp, *parse_size(args.size)))
                fmeta["sized"] = True
            fj = run_judge(fp, brief, args.threshold, args.judge_model, args.judge_effort,
                           getattr(args, "judge_timeout", None) or JUDGE_TIMEOUT)
            fmeta = dict(meta, **fmeta, judge=fj, fix_of=str(best[0]), fix_mode=mode, fix_instruction=fix,
                         edit_chain=best[1].get("edit_chain", 0) + 1 if mode == "edit" else 0)
            cands.append(fp)
            history.append(judge_digest(fp, fj, mode, fix))
            if judge_rank(fj) > judge_rank(bj):
                best = (fp, fmeta)
        bp, bm = best
        bm = dict(bm, rounds=history, rejected=[str(c) for c in cands if c != bp])
        out.append((bp, bm))
    return out


# ----------------------------------------------------------------------------- fast pipeline
# Speed design (measured 2026-09-23): in the agent mode ~60% of every Codex run is agent overhead (reading the imagegen
# skill, xhigh prompt rewriting, self-QA retries, copying). The fast pipeline compiles the final prompt here (brief +
# prompt-time judge knowledge), runs ALL images of a job list concurrently inside ONE low-effort Codex session
# (Promise.allSettled over the built-in image_gen tool), judges every image in parallel fresh sessions, and spends a
# fix round only on quality failures.

FAILURE_HINTS = [  # prompt-time judge knowledge: trigger -> the check the judge will apply later
    (r"\b(tilt\w*|tipp\w*)\s+(the\s+|a\s+|her\s+|his\s+)?(cup|glass|bowl|mug|bucket)\b|"
     r"\b(cup|glass|bowl|mug|bucket)\b[^.;\n]{0,40}\b(tilt\w*|tipped)\b",
     "Liquid inside any tilted container stays level with the horizon: its surface sits closer to the rim on the "
     "lower side and farther from the rim on the higher side."),
    (r"\bpour\w*", "A pour leaves only from the spout tip or the lowest point of the rim as one continuous stream and "
                   "lands inside the target; nothing leaks from a side or bottom."),
    (r"\b(reflect\w*|mirror\w*|puddle\w*|wet (floor|ground|road|street|asphalt|slate|stone|steps?))\b",
     "Reflections on water or wet ground sit directly below their objects and lights, flipped vertically with the "
     "same left-right order; reflected text reads upside down, never mirrored left-right."),
    (r"\bupside[- ]down\b", "Anything upside down rests stably on its real contact points (an upside-down bicycle "
                            "stands on its saddle and BOTH handlebar grips, all touching the ground)."),
    (r"\b(wrench|spanner|screwdriver|pliers|hammer|knife|blade|scissors|boti)\b",
     "Tools engage their target the way they work: a wrench fits the nut (open jaws on two opposite flats or a ring "
     "end around it), a blade's edge faces what it cuts, a screwdriver tip sits in the screw head."),
    (r"\b(rope|string|thread|chain|cable|wire|leash|kite)\b",
     "Every rope, string, chain or cable is one continuous line from end to end with no breaks or extra strands, "
     "taut or sagging according to the forces on it; where it passes behind a hand or an object it re-emerges in "
     "line."),
    (r"\b(wind|breeze|flag|kite|smoke|steam|windy)\b",
     "One wind direction for everything moving in the air: smoke, steam, hair, fabric, flags and kite tails all "
     "move the same way."),
    (r"\brain\w*\b", "Rain falls as fine streaks in one direction; splashes and ripples appear only where drops hit "
                     "water or ground."),
    (r"\b(motion blur|moving|pedal\w*|running|speeding)\b",
     "Motion blur only on moving parts and along their direction of travel; everything static stays sharp."),
    (r"\b(glass|bottle|jar|lens)\b", "Transparent glass refracts and bends what is behind it and shows dark edge "
                                     "lines; liquid surfaces inside stay flat and level."),
    (r"\b(portrait|face|skin|elderly|wrinkle\w*)\b",
     "Natural skin with visible pores, fine lines and uneven tone, no smoothing; each eye has one catchlight from "
     "the single light source, on the same side of both irises (the side facing the light)."),
    (r"[\"“][^\"”]{1,120}[\"”]", "Every quoted text is rendered exactly once and spelled exactly as given; no other "
                                 "text anywhere."),
    (r"\b(hands?|holding|holds?|grip\w*|carr\w*|lift\w*|pinch\w*)\b",
     "Each visible hand has five fingers; a hand touches only real parts of an object; heavy things rest on a hand, "
     "forearm, hip or surface under their center of mass."),
    (r"\b(sun|sunlight|window|daylight|lamp|bulb|softbox|tube light)\b",
     "Every shadow falls away from the named light with consistent direction and length; objects touching a "
     "surface cast contact shadows."),
    (r"\brickshaw\b", "A cycle rickshaw has exactly three wheels: one front wheel under the puller and "
                      "two rear wheels under the passenger seat."),
    (r"\b(fuchka|panipuri|puris?)\b", "Puris waiting in the basket are whole and uncracked; only the one being filled "
                                      "has a hole."),
    (r"\b(latte art|heart[- ]shaped|rosetta|microfoam)\b",
     "Latte art forms only when the pitcher spout is low, almost touching the crema, as the pattern is drawn; the "
     "stream is short and the foam lands on the surface."),
    (r"\b(kolshi|kolsi|kalshi|kalash)\b",
     "A kolshi has a round belly, a short neck and a rolled rim, no handle and no spout; it rests on the hip, the "
     "head or a palm under its belly and is never gripped at the neck like a handle."),
    (r"\b(kettle|karahi|wok|frying pan)\b", "Hot vessels are touched only by their handles, a cloth or tongs, never by "
                                            "bare hands on the hot body."),
    (r"\b(dentist|dental|hygienist|orthodont\w*|tooth|teeth)\b",
     "Clinical accuracy: gloves and a mask whenever hands are near a patient's mouth; the patient wears a bib and "
     "protective glasses during treatment; a real dental chair with overhead light, instrument tray and suction; "
     "natural tooth anatomy and smiles (no uniform piano-key teeth); a bright hygienic room; no blood."),
    (r"\b(doctor|nurse|surgeon|hospital|clinic|patient|physician)\b",
     "Medical accuracy: correct protective equipment for the task (gloves, mask), realistic equipment used the right "
     "way, hygienic surfaces, calm and respectful patient interaction, nothing graphic."),
]
BRAND_HINT = ("Shop signs, storefronts and billboards show invented, generic names instead of real chains or brands "
              "(ordinary vehicle makers' badges are fine).")
FAILURE_HINTS.append((r"(?is)(?=.*\bno (readable )?(text|writing|letters)\b)(?=.*\b(streets?|stalls?|shops?|market|"
                       r"sidewalk|storefronts?|caf[eé]s?|restaurants?|bars?|kiosks?)\b)",
                       "Any signs, menus, price boards or labels in the scene are turned away, out of frame or too "
                       "blurred to read."))
FAILURE_HINTS.append((r"(?is)(?=.*\bno (readable )?(text|writing|logos?)\b)(?=.*\b(monitors?|screens?|laptops?|"
                       r"computers?|tablets?|displays?)\b)",
                       "Screens are seen at an angle or show only pictures, with no interface text; equipment carries no "
                       "maker's marks or logos."))
FAILURE_HINTS.append((r"(?is)(?=.*\bno (readable )?(text|writing|logos?|brand)\b)(?=.*\b(gym|sports?|runners?|"
                       r"trainers|sneakers|jerseys?|kit|equipment|clipboards?|notebooks?|papers?|magazines?|books?|"
                       r"bags?|uniforms?|scrubs|machines?)\b)",
                       "Clothing, shoes, bags, equipment, papers and magazines are plain: no brand logos, maker's marks "
                       "or printed words (blank sheets, turned away or out of focus)."))
FAILURE_HINTS.append((r"\b(clocks?|wristwatch|watch face)\b",
                      "Any clock shows an ordinary, random time, not the advertising 10:10."))
FAILURE_HINTS.append((r"\b(night|at dusk|after dark|nighttime|evening street)\b",
                      "At night the frame is mostly dark: only lit areas hold detail, shadows fall close to black with "
                      "some noise, bright bulbs clip; no lifted, HDR-looking shadows."))
FAILURE_HINTS.append((r"\b(shops?|stores?|storefronts?|shopfronts?|streets?|market|caf[eé]s?|restaurants?|"
                      r"billboards?|mall|signs?|signage)\b", BRAND_HINT))
MAX_HINTS = 10
COMPACT_RULES = ("An unretouched real photograph: neutral white balance, true-to-life colour and contrast, exposure "
                 "set for the subject (bright windows or sky may clip, shadows may go dark), texture at the right "
                 "scale for the distance (not etched or over-sharpened), the depth of field a real lens gives, "
                 "framing chosen in the moment (subject "
                 "a little off centre, something cut by the frame edge). Honest rather than perfect: no airbrushing, "
                 "beauty filter, HDR look, cinematic or teal-orange grade, oversaturation or CGI gloss, no watermark. "
                 "Real-world logic everywhere: nothing floats, one consistent light, exact counts, nothing added that "
                 "the brief does not ask for.")
COMPACT_RULES_STYLED = ("Keep exactly the requested style and medium. Logic everywhere: consistent light and "
                        "perspective, exact counts, labels only where asked, nothing added that the brief does not ask "
                        "for, no watermark.")
DESIGN_RULES = ("A finished graphic design laid out by a senior human designer: the exact text in quotes, spelled "
                "exactly, each string once and nothing else written (no extra words, letters, numbers, logos, badges "
                "or watermark); one clear focal point and reading order (headline, supporting line, call to action); "
                "a consistent grid with generous margins and aligned edges; one or two type families with a clear "
                "size contrast; a restrained palette; any photograph in it looks like a real, unretouched photo; no "
                "fake interface, random sparkles, blobs, lens flares, glossy gradients or decorative clutter.")
# ----------------------------------------------------------------------------- natural look (anti "AI look")
# Measured 2026-09-23 (10-brief realism benchmark): what reads as "AI" is mostly stock-photo polish - everyone smiling
# at once, catalogue-tidy colour-coordinated sets, glowing even light, a warm/orange grade - more than skin. Every
# photo therefore gets a concrete capture profile (a real camera or phone, lens and settings; picked from the intent
# unless the brief names its own camera) plus people / scene / product realism checks that the judge verifies.
LOOK_LINE = re.compile(r"^[ \t]*-?[ \t]*look[ \t]*:[ \t]*(.+?)[ \t]*$", re.I | re.M)
LOOKS = {
    "editorial": ("documentary photograph taken handheld on a full-frame camera with a {focal} lens at about f/2.8, "
                  "available light only: focus on the subject, the background a little softer but still readable, "
                  "an unretouched raw conversion with neutral white balance and natural contrast"),
    "portrait": ("portrait on a full-frame camera with a {focal} lens at about f/2, the light the brief describes: "
                 "focus on the eyes, background soft but recognisable, unretouched, real skin texture everywhere"),
    "phone": ("casual photo taken on an iPhone main camera ({focal} equivalent) with the default camera app, handheld, "
              "no portrait mode: deep depth of field with a sharp, recognisable background, phone HDR tone mapping, "
              "mild phone sharpening, faint noise in darker areas, framing a little off level"),
    "phone-flash": ("phone snapshot with the built-in flash on: hard frontal flash, bright foreground, quick falloff "
                    "into a dark background, specular shine on skin and glossy surfaces, casual framing"),
    "film": ("35mm film photograph on Kodak Portra 400 with a {focal} lens: natural film grain and colour, soft "
             "contrast, true skin tones, a slightly imperfect exposure"),
    "product": ("product photograph on a full-frame camera with a {focal} lens at f/8 on a tripod, the light the "
                "brief describes: real material texture with tiny true imperfections, honest reflections of the "
                "room, only the props the brief names"),
    "interior": ("interior photograph on a full-frame camera with a {focal} tilt-shift lens on a tripod at f/8, "
                 "verticals straight, available light only, windows a little brighter than the room, shadows in the "
                 "corners"),
}
LOOK_FOCAL = {"editorial": "35mm", "portrait": "85mm", "phone": "24mm", "film": "35mm", "product": "100mm macro",
              "interior": "24mm"}
LOOK_RULES = [  # first match wins; interior/product only when no people are in the shot
    ("phone-flash", r"\b(direct flash|on-camera flash|flash (photo|snapshot)|built-in flash)\b"),
    ("phone", r"\b(ugc|user[- ]generated|selfie|phone photo|smartphone|mobile photo|instagram|tiktok|social post|"
              r"snapshot)\b"),
    ("film", r"\b(35mm film|film photo\w*|analog(ue)? photo\w*|film stock|disposable camera)\b"),
    ("product", r"\b(product (photo|shot|image)|packshot|e-?commerce|online (shop|store)|catalog(ue)? (photo|shot))\b"),
    ("interior", r"\b(interior (photo|shot)|real estate|rental listing|listing photo|architectur\w+ photo\w*)\b"),
    ("portrait", r"\b(portrait|headshot|close-up of (a|an|the|his|her|their) face)\b"),
]
CAMERA_NAMED = re.compile(r"\b(iphone|pixel \d|galaxy s\d+|canon|nikon|sony (a|alpha)\s?\d|fujifilm|fuji x|leica|"
                          r"hasselblad|lumix|olympus|ricoh|gopro|polaroid|disposable camera|portra|ektar|tri-x|hp5|"
                          r"cinestill|kodak gold|superia)\b", re.I)
FOCAL_RX = re.compile(r"\b(\d{2,3})\s?mm\b", re.I)
PEOPLE_REAL = ("People look real and unretouched: visible skin texture (pores, fine lines, faint redness, uneven tone), "
               "natural facial asymmetry, real teeth with slight shade and alignment differences, a few loose hairs; "
               "skin mostly matte with natural shine only on the nose and forehead; one or two people act while the "
               "others simply listen or wait, expressions in between (listening, mid-word, thinking), not everyone "
               "smiling or looking the same way; everyday clothes with small creases.")
SCENE_REAL = ("The place looks real and in use: one or two ordinary things left where someone just used them, at "
              "the edges or partly hidden rather than arranged for the camera, nothing colour-sorted or evenly spaced, "
              "not every typical prop on show, light wear on surfaces, everyday objects plain or unbranded with labels "
              "turned away, colours as they really are (brand colours only as small accents), light falling off into "
              "darker corners; an ordinary spot rather than a postcard view (no famous landmark unless the brief "
              "names one); a caught moment, not a staged stock shot.")
PRODUCT_REAL = ("The product looks photographed, not rendered: real material texture, tiny true imperfections (dust, "
                "pinholes, faint fingerprints), honest reflections of the room, a real contact shadow.")
NON_PHOTO = re.compile(r"\b(illustration|illustrated|vector|flat design|diagram|logo|icon|cartoon|comic|3d render|3d|"
                       r"isometric|watercolou?r|painting|painted|sketch|line art|pixel art|sprite|clay|claymation|"
                       r"low[- ]poly|collage|paper[- ]cut)\b", re.I)  # a drawn, painted or rendered medium
PHOTO_MEDIUM = re.compile(r"\b(photo|photos|photograph\w*|snapshot|shot on)\b", re.I)
DESIGN_KIND = re.compile(r"\b(poster|infographic|ui|mockup|graphic design|layout|social[- ]media (?:post|graphic)|"
                         r"(?:instagram|facebook|linkedin|twitter|tiktok|pinterest|youtube|whatsapp) "
                         r"(?:post|story|cover|banner|thumbnail|carousel|ad)|story (?:design|graphic)|carousel|"
                         r"thumbnail|banner|flyer|leaflet|brochure|typographic|lettering|greeting card|info ?card|"
                         r"quote card|ad creative|menu design|packaging|label design|business card|invitation|"
                         r"certificate|cover design)\b", re.I)  # a finished layout that carries text
QUOTED = re.compile(r"[\"“][^\"”\n]{2,}[\"”]")
EXPLORE_DIRECTIONS = ["eye-level three-quarter view", "higher angle looking down at the action",
                      "closer framing with shallower depth of field", "wider framing that shows more of the place"]

PAR_JS = r"""// @exec: {"yield_time_ms": __YIELD__, "max_output_tokens": 8000}
const f = await tools.exec_command({cmd: "cat '__JOBS__'", max_output_tokens: 120000});
const o = typeof f === "string" ? JSON.parse(f) : f;
const jobs = JSON.parse(o.output);
__VIEW_REFS__const t0 = Date.now();
const res = await Promise.allSettled(jobs.map(async j => {
  const s = Date.now();
  const v = await tools.image_gen__imagegen(__ARGS__);
  generatedImage(v);
  const h = String((v && v.output_hint) || "");
  const m = h.match(/ as (\/\S+?\.png)/);
  return {id: j.id, ms: Date.now() - s, path: m ? m[1] : null, note: m ? "" : h.slice(0, 300)};
}));
text(JSON.stringify({total_ms: Date.now() - t0, results: res.map((x, i) => x.status === "fulfilled" ? Object.assign({ok: true}, x.value) : {ok: false, id: jobs[i].id, err: String(x.reason).slice(0, 400)})}));
"""
PAR_VIEW_REFS = """for (const j of jobs) for (const r of (j.refs || [])) await tools.view_image({path: r});
"""
PAR_TASK = """Batch image job. Run the JavaScript below with your exec tool in one single call, exactly as written. It \
already follows the image tool rules: it inspects every reference image with view_image before editing, and it \
displays every generated image with generatedImage. The prompts are final and pre-approved by the art director: do \
not rewrite them, do not generate anything else, do not read other files. When the call finishes, reply with only \
the JSON line it printed.

```js
{code}
```"""


LITE_JS = r"""// @exec: {"yield_time_ms": __YIELD__, "max_output_tokens": 8000}
const P = `PROMPT_HERE`;
__VIEW_REFS__const t0 = Date.now();
const res = await Promise.allSettled(Array.from({length: __K__}, async (_, i) => {
  const s = Date.now();
  const v = await tools.image_gen__imagegen(__ARGS__);
  generatedImage(v);
  const h = String((v && v.output_hint) || "");
  const m = h.match(/ as (\/\S+?\.png)/);
  return {id: "__ID__-c" + (i + 1), ms: Date.now() - s, path: m ? m[1] : null, note: m ? "" : h.slice(0, 300)};
}));
text(JSON.stringify({total_ms: Date.now() - t0, prompt: P, results: res.map((x, i) => x.status === "fulfilled" ? Object.assign({ok: true}, x.value) : {ok: false, id: "__ID__-c" + (i + 1), err: String(x.reason).slice(0, 400)})}));
"""
LITE_TASK = """You are the art director and prompt engineer for one image job. Work fast and autonomously: do not read \
any files or skills, do not ask questions, do not explain.

1. Write the final prompt for the image model from the brief below. Use labeled lines (Intent, Scene, Subject, \
Object anatomy, Grip & load, Action mechanics, Camera, Light, Materials & texture, Color & mood, Text, Constraints, \
Output), at most 250 words. Keep every specific of the brief. Turn every check listed after the brief into a \
concrete visual statement. State exact counts and one consistent light logic, and name the only light sources. \
Unless text is requested, write "no text, letters, signage or logos anywhere". Never add people, light sources, \
props or effects the brief does not ask for. Describe what things ARE before any exclusion, and keep exclusions to \
one short Constraints line. Write the prompt in English. __EDIT_NOTE__
2. Run the JavaScript below with your exec tool in ONE call, with PROMPT_HERE replaced by your prompt (keep the \
backticks; escape any backtick or dollar-brace inside your prompt). It already follows the image tool rules: it \
inspects reference images with view_image before editing and shows every result with generatedImage.
3. Reply with only the JSON line it printed.

```js
{code}
```

<<<BRIEF
{brief}
BRIEF>>>
Checks the independent judge will apply to the result (make each one visibly true):
{checks}
Format: {fmt}"""


def codex_lite_job(job_id: str, brief: str, hints: list, aspect, k: int, refs: list, args, kind: str = "generate",
                   edit: bool = False) -> dict:
    """ONE Codex session per job: the art director writes the final prompt (with the judge's checks in view) and
    generates k candidates concurrently. No skill reading, no self-QA retries, no copying: the script does the rest."""
    bin_ = codex_bin()
    tmp = Path(tmp_dir(prefix="codex-lite-"))
    refs = [str(r) for r in refs or []]
    code = (LITE_JS.replace("__YIELD__", str(max(60, args.timeout - 30) * 1000)).replace("__K__", str(k))
            .replace("__ID__", job_id)
            .replace("__VIEW_REFS__", "".join(f"await tools.view_image({{path: {json.dumps(r)}}});\n" for r in refs))
            .replace("__ARGS__", "{prompt: P" + (f", referenced_image_paths: {json.dumps(refs)}" if refs else "") + "}"))
    prompt = (LITE_TASK.replace("{code}", code).replace("{brief}", brief.strip())
              .replace("{checks}", "\n".join(f"- {h}" for h in hints) or "- (none beyond the brief)")
              .replace("{fmt}", ASPECTS[aspect][0] if aspect else "as the brief implies")
              .replace("__EDIT_NOTE__", "This is an EDIT of reference Image 1: write the prompt as 'Change ONLY <X> "
                                        "...; keep everything else exactly the same' and describe the full final "
                                        "image." if edit else ""))
    last = tmp / "last.txt"
    cmd = [bin_, "exec", "--skip-git-repo-check", "-s", "read-only", "--json", "-C", str(Path.cwd()),
           "-c", f'model_reasoning_effort="{args.prompt_effort}"'] + LEAN_FLAGS + ["-o", str(last), "-"]
    t0 = time.time()
    run = run_group(cmd, prompt, args.timeout, tmp, ready=batch_watch(tmp, [f"{job_id}-c{i + 1}" for i in range(k)]))
    out, err = run["stdout"], run["error"]
    wall = time.time() - t0
    tid = thread_from(out)
    rec = record_run(kind, prompt, out, tid, wall, {"tasks": [job_id], "k": k, "error": err,
                                                    "early_result": bool(run["early"])}, job_id)
    parsed = run["early"] or _parse_par_result(last.read_text(encoding="utf-8") if last.exists() else "")
    if not parsed:
        for line in out.splitlines():
            try:
                it = (json.loads(line).get("item") or {})
            except ValueError:
                continue
            if it.get("type") == "agent_message":
                parsed = _parse_par_result(it.get("text", "")) or parsed
    if not parsed and tid:
        parsed = _rollout_result(tid)
    results = []
    for r in (parsed or {}).get("results", []):
        src = Path(r["path"]) if r.get("ok") and r.get("path") else None
        results.append({"ok": bool(src and src.exists()), "src": str(src) if src else None, "ms": r.get("ms"),
                        "err": r.get("err") or r.get("note")})
    answered = bool(results)
    if not answered:  # no result line: every candidate failed for the session's own reason
        results = [{"ok": False, "src": None, "ms": None, "err": None} for _ in range(k)]
    explain_failures(results, run, rec["step"])
    return {"results": results, "prompt": (parsed or {}).get("prompt"), "wall_s": round(wall, 1), "thread_id": tid,
            "error": None if answered else results[0]["err"], "tokens": (rec.get("digest") or {}).get("tokens")}


# ----------------------------------------------------------------------------- place, culture and people
# Global by default, local from context. Without a place the image model paints a US-looking street and cast, and
# earlier briefs leaked the requester's own region; neither is the client's audience. A job's place comes from
# (1) a "Locale:" line (job "locale", jobs-file "locale", --locale, or the style lock's "locale"), (2) a place the
# brief itself names, else (3) an internationally neutral setting with varied people. A known country adds its
# real-world logic (traffic side, signage script, southern-hemisphere seasons) to the prompt-time checks, so the
# judge verifies it too. The requester's chat language, timezone or nationality is never a signal.
LOCALE_FILE = Path(__file__).with_name("locales.json")
GLOBAL_LOCALES = {"global", "international", "worldwide", "neutral", "any", "none", "unspecified", "auto"}
LOCALE_LINE = re.compile(r"^[ \t]*-?[ \t]*locale[ \t]*:[ \t]*(.+?)[ \t]*$", re.I | re.M)
PEOPLE_RX = re.compile(r"\b(people|persons?|m[ae]n|wom[ae]n|child(ren)?|kids?|boys?|girls?|bab(y|ies)|famil(y|ies)|"
                       r"adults?|seniors?|teen\w*|patients?|dentists?|doctors?|nurses?|hygienists?|staff|team|"
                       r"customers?|clients?|guests?|students?|teachers?|workers?|chefs?|waiters?|vendors?|drivers?|"
                       r"crowd|pedestrians?|couples?|mothers?|fathers?|parents?|receptionists?|owners?|colleagues?|"
                       r"athletes?|fisherm[ae]n|farmers?|mechanics?|baristas?|cooks?|bakers?|artists?|musicians?|"
                       r"craftsm[ae]n|builders?|carpenters?|tailors?|sellers?|shopkeepers?|merchants?|traders?|"
                       r"monks?|priests?|soldiers?|officers?|guards?|pilots?|surfers?|runners?|cyclists?|riders?|"
                       r"dancers?|singers?|grandm\w+|grandp\w+|grandparents?|toddlers?|infants?|elderly|retirees?|"
                       r"residents?|locals?|tourists?|travell?ers?|hikers?|shoppers?|diners?|passengers?|commuters?|"
                       r"entrepreneurs?|founders?|engineers?|designers?|scientists?|technicians?|therapists?|"
                       r"pharmacists?|surgeons?|midwi(fe|ves)|caregivers?|volunteers?|coaches?|trainers?|taqueros?)\b",
                       re.I)
SETTING_RX = re.compile(r"\b(street|city|town|village|market|neighbou?rhood|shop|store|restaurant|caf[eé]|office|home|"
                        r"house|apartment|school|hospital|clinic|hotel|reception|lobby|kitchen|living room|bedroom|"
                        r"park|beach|downtown|skyline|interior|exterior|landscape|harbou?r|port|pier|dock|boats?|"
                        r"farm|field|forest|mountains?|river|lake|garden|yard|balcony|rooftop|workshop|garage|"
                        r"factory|warehouse|studio|gym|classroom|library|church|temple|mosque|station|airport|"
                        r"playground|stall|salon|bar|pub|bakery|pharmacy|lab(oratory)?|construction site)\b", re.I)
VEHICLE_RX = re.compile(r"\b(cars?|taxis?|cabs?|bus|buses|traffic|roads?|highway|motor(bike|cycle)s?|scooters?|"
                        r"trucks?|vans?|vehicles?|driv(e|es|er|ers|ing)|parked|parking|crosswalk|intersection|trams?|"
                        r"rickshaws?|tuk[- ]?tuks?)\b", re.I)
SIGN_RX = re.compile(r"\b(signs?|signage|shopfronts?|storefronts?|shops?|stores?|streets?|market|billboards?|station|"
                     r"bus stop|downtown)\b", re.I)
SEASON_RX = re.compile(r"\b(christmas|new year|december|january|february|june|july|august|summer|winter|autumn|"
                       r"snow\w*|holiday season)\b", re.I)
GLOBAL_SETTING = ("Place: no country is named, so the setting stays internationally neutral: a contemporary place that "
                  "could be in many countries, with no country-specific signage, script, vehicles, money, landmarks "
                  "or traditional dress.")
GLOBAL_PEOPLE = ("People not described in the brief have natural, varied appearances (an international cast), not one "
                 "region's look by default.")
GLOBAL_TRAFFIC = "All vehicles keep to the same side of the road, and steering wheels sit on the matching side."
NO_TEXT_RX = re.compile(r"\bno (readable )?(text|writing|letters|words)\b|\bnot readable\b", re.I)
# One image cannot see the rest of its set, so "varied people" alone converges on one look across a batch
# (measured 2026-09-23). Global batches therefore rotate the main person's background per job; the judge never
# sees this line, because appearance is never a quality defect.
GLOBAL_CAST = ["African", "East Asian", "European", "Latin American", "South Asian", "Middle Eastern",
               "Southeast Asian"]
AUTO_CAST_LINE = re.compile(r"^Cast \(auto, global set\):.*$\n?", re.M)
CAST_DESCRIBED = re.compile(r"\b(descent|heritage|ethnicit\w*|skin tone|complexion|(black|white|brown|asian|"
                            r"african|european|latin[oa]|hispanic|arab|caucasian|indigenous)[- ](m[ae]n|wom[ae]n|"
                            r"person|people|child(ren)?|kids?|boys?|girls?|teens?|adults?|patients?|dentists?|"
                            r"doctors?|nurses?|family|couple))\b", re.I)
_LOC = {}
_LOC_LOCK = threading.Lock()


def locales() -> dict:
    """locales.json compiled once: the country table and one longest-first regex over every place name."""
    with _LOC_LOCK:
        return _locales_locked()


def _locales_locked() -> dict:
    if _LOC:
        return _LOC
    try:
        data = json.loads(LOCALE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    names = {}
    for c in data.get("countries", []):
        for kind in ("aliases", "cities", "regions", "demonyms"):
            for a in c.get(kind, []):
                names.setdefault(a.lower(), (c["code"], kind))
    for a in data.get("world_regions", []):
        names.setdefault(a.lower(), (None, "world"))
    for a, code in (data.get("markers") or {}).items():
        names.setdefault(a.lower(), (code, "marker"))
    for a in data.get("ignore", []):
        names[a.lower()] = (None, "ignore")
    alts = sorted(names, key=len, reverse=True)
    _LOC.update(countries=data.get("countries", []), by_code={c["code"]: c for c in data.get("countries", [])},
                names=names, rx=re.compile(r"(?<![\w.])(" + "|".join(map(re.escape, alts)) + r")(?!\w)", re.I)
                if alts else None)
    return _LOC


def find_places(text: str, require_cap: bool = True) -> list:
    """Countries, cities, regions, demonyms, world regions and culture markers in text -> [{code, kind, name}].
    Names must be capitalized in running text ("Nice"/"nice" traps); markers (kimono, kolshi) match in any case."""
    L = locales()
    if not text or not L.get("rx"):
        return []
    out = []
    for m in L["rx"].finditer(text):
        code, kind = L["names"].get(m.group(1).lower(), (None, "ignore"))
        if kind == "ignore" or (require_cap and kind != "marker" and not m.group(1)[0].isupper()):
            continue
        out.append({"code": code, "kind": kind, "name": m.group(1)})
    return out


def locale_facts(code, text: str, no_text: bool = False) -> list:
    """Real-world logic a country implies for this brief: traffic side, public signage script, seasons."""
    c = locales().get("by_code", {}).get(code)
    if not c:
        return []
    out = []
    if VEHICLE_RX.search(text):
        wheel = "right" if c["drive"] == "left" else "left"
        out.append(f"{c['name']}: traffic keeps to the {c['drive']}; cars have the steering wheel on the {wheel}.")
    if SIGN_RX.search(text) and not no_text:  # never invite signs into a no-text brief
        out.append(f"{c['name']}: public street and traffic signs use {c['script']}.")
    if c.get("south") and SEASON_RX.search(text):
        out.append(f"{c['name']} is in the southern hemisphere: December to February is summer, June to August is "
                   "winter.")
    return out


NO_PEOPLE_RX = re.compile(r"\b(no people|no one|nobody|without people|empty of people|unoccupied)\b", re.I)


def has_people(text: str) -> bool:
    """People appear in the frame: a people word that is not negated and not a possessive ('the receptionist's
    chair'), and no explicit 'no people'."""
    if NO_PEOPLE_RX.search(text):
        return False
    return bool(PEOPLE_RX.search(re.sub(r"\b\w+['’]s\b", " ", own_positive(text))))


def own_positive(text: str) -> str:
    """The job's own brief without negated phrases ("no signage" is not signage) and without the shared style lock
    (its "people" key must not put people or streets into every image)."""
    pos = re.sub(r"\b(no|not|never|avoid|without)\b[^.;\n]*", " ", text, flags=re.I)
    return AUTO_CAST_LINE.sub("", pos.split("Style lock (", 1)[0])


def place_context(brief: str):
    """-> (brief without Locale lines, {mode: named|brief|global|none, locale, country, hints[, overridden]})."""
    from collections import Counter
    m = LOCALE_LINE.search(brief)
    explicit = m.group(1).strip() if m else ""
    body = re.sub(r"\n{3,}", "\n\n", LOCALE_LINE.sub("", brief)).strip() if m else brief.strip()
    info = {"mode": "none", "locale": None, "country": None, "hints": []}
    pos = own_positive(body)
    places = find_places(AUTO_CAST_LINE.sub("", body))  # the set's casting line is not a place
    codes = [p["code"] for p in places if p["code"] and p["kind"] != "marker"]
    top = Counter(codes).most_common(1)[0][0] if codes else None
    if explicit and explicit.lower() not in GLOBAL_LOCALES:
        code = next((p["code"] for p in find_places(explicit, require_cap=False) if p["code"]), None)
        if top and top != code:  # the image names its own place: it wins over the project locale
            info.update(mode="brief", country=top, overridden=explicit)
        else:
            info.update(mode="named", locale=explicit, country=code)
            info["hints"].append(f"Place and people: {explicit}. Architecture, interiors, vehicles, public signage, clothing "
                                 "and food fit this place today, and the cast reflects its real present-day "
                                 "population (often diverse), unless the brief says otherwise.")
    elif places:
        info.update(mode="brief", country=top)
    elif SETTING_RX.search(pos) or has_people(body):
        info["mode"] = "global"
        info["hints"].append(GLOBAL_SETTING)
        if has_people(body):
            info["hints"].append(GLOBAL_PEOPLE)
        if VEHICLE_RX.search(pos):
            info["hints"].append(GLOBAL_TRAFFIC)
    if info["country"]:
        info["hints"] += locale_facts(info["country"], pos, no_text=bool(NO_TEXT_RX.search(body)))
    return body, info


def with_locale(brief: str, locale) -> str:
    """Add 'Locale: X' unless the brief already has one (job > jobs file > --locale > style lock)."""
    if not locale or LOCALE_LINE.search(brief):
        return brief
    return f"{brief.rstrip()}\nLocale: {locale}"


def auto_cast(jobs: list) -> int:
    """Global sets with two or more jobs showing people: give each such job a different main-person background, so
    the set reads as international instead of one repeated look. Skips jobs with a place, jobs whose brief already
    describes appearance, and jobs with "cast": false. Returns the number of jobs cast."""
    todo = []
    for j in jobs:
        if j.get("cast") is False or AUTO_CAST_LINE.search(j["brief"]):
            continue
        body, info = place_context(j["brief"])
        own = own_positive(body)
        if info["mode"] == "global" and has_people(body) and not CAST_DESCRIBED.search(own):
            todo.append(j)
    if len(todo) < 2:
        return 0
    for i, j in enumerate(todo):
        who = GLOBAL_CAST[i % len(GLOBAL_CAST)]
        j["brief"] = (f"{j['brief'].rstrip()}\nCast (auto, global set): the main person is of {who} descent; anyone "
                      "else has a different background.")
        j["cast_auto"] = who
    return len(todo)


def judge_brief(brief: str) -> str:
    """What the judge sees: the brief without the automatic casting line (appearance is never a defect)."""
    return AUTO_CAST_LINE.sub("", brief).strip()


def with_look(brief: str, look) -> str:
    """Add 'Look: X' unless the brief already has one (job > jobs file > --look > style lock)."""
    if not look or LOOK_LINE.search(brief):
        return brief
    return f"{brief.rstrip()}\nLook: {look}"


def pick_look(body: str):
    """-> (look, "Capture: ..." line). A Look line wins; else a camera the brief names keeps the brief in charge;
    else the intent picks a profile (default editorial). The focal length the brief gives is kept."""
    m = LOOK_LINE.search(body)
    want = m.group(1).strip().lower() if m else "auto"
    own = own_positive(LOOK_LINE.sub("", body))
    if want == "none":
        return "none", ""
    if want not in LOOKS:
        if CAMERA_NAMED.search(own):
            return "brief", ""
        people = has_people(own)
        # the intent and camera lines decide ("a smartphone face down on the desk" is a prop, not a phone photo)
        decide = "\n".join(l for l in own.splitlines()
                           if re.match(r"\s*(intent|camera|style|medium|output)\s*:", l, re.I)) or own
        want = next((n for n, rx in LOOK_RULES
                     if re.search(rx, decide, re.I) and not (n in ("interior", "product") and people)), "editorial")
    fm = FOCAL_RX.search(own)
    focal = f"{fm.group(1)}mm" if fm and want not in ("phone", "phone-flash") else LOOK_FOCAL.get(want, "35mm")
    return want, "Capture: " + LOOKS[want].format(focal=focal) + "."


def place_label(p) -> str:
    if not p or p.get("mode") in (None, "none"):
        return "-"
    if p["mode"] == "named":
        return p.get("locale") or "-"
    if p["mode"] == "brief":
        return f"named in brief ({p.get('country') or 'culture'})"
    return f"global, cast: {p['cast']}" if p.get("cast") else "global"


EDIT_RULES = ("Edit, do not re-imagine: keep the framing, composition, people, objects, light and colour of Image 1 "
              "exactly as they are except for the change the brief asks for; an unretouched real photograph, no "
              "watermark.")


def failure_hints(body: str) -> list:
    """The physics/logic failure-library checks a brief triggers (at most MAX_HINTS)."""
    hints = []
    for rx, h in FAILURE_HINTS:
        if rx == r"\bupside[- ]down\b":
            hit = upside_down_object(body)
        elif h is BRAND_HINT:
            hit = re.search(rx, own_positive(body), re.I)
        else:
            hit = re.search(rx, body, re.I)
        if hit and h not in hints:
            hints.append(h)
    return hints[:MAX_HINTS]


def compile_prompt(brief: str, aspect=None, edit: bool = False) -> tuple:
    """Final image prompt = format + brief + the checks the judge will apply (prompt-time judge): place first
    (Locale / a place the brief names / the global default), then the physics and logic failure library."""
    body, place = place_context(brief)
    kind = image_kind(body)
    photo = kind == "photo"
    look, capture = pick_look(body) if photo and not edit else ("none", "")
    body = re.sub(r"\n{3,}", "\n\n", LOOK_LINE.sub("", body)).strip()
    own = own_positive(body)
    real = []
    if photo and look == "product":
        real.append(PRODUCT_REAL)
    elif photo:
        if has_people(body):
            real.append(PEOPLE_REAL)
        if SETTING_RX.search(own) or has_people(body):
            real.append(SCENE_REAL)
    elif kind == "design" and PHOTO_MEDIUM.search(own) and has_people(body):
        real.append(PEOPLE_REAL)  # the people photo inside a designed post still has to look real
    hints = place["hints"] + real + failure_hints(body)
    parts = ([f"Format: {ASPECTS[aspect][0]}."] if aspect else []) + [body] + ([capture] if capture else [])
    if hints:
        parts.append("Physics and logic checks (must all hold):\n- " + "\n- ".join(hints))
    parts.append(EDIT_RULES if edit and kind in ("photo", "design") else COMPACT_RULES if photo else
                 DESIGN_RULES if kind == "design" else COMPACT_RULES_STYLED)
    return "\n".join(parts), hints


PLATE = re.compile(r"\b(text-free|text free|background plate|plate for|no text|typography is added later|"
                   r"typeset later|type is added later)\b", re.I)


def image_kind(brief: str) -> str:
    """'photo', 'styled' (illustration, 3D, painting...) or 'design' (a finished layout with text: post, poster,
    thumbnail, flyer...), read from the Intent/Style/Medium/Output lines (or the whole brief), ignoring negations.
    A design needs quoted text to lay out: 'YouTube thumbnail for a baking video' with no words is an image, and a
    text-free plate for a design (codex-design adds the type) is never a design. When both a photo and a design
    deliverable are named, the first one wins: 'background photo for a poster' stays a photo; 'poster with a photo
    of a runner, headline "Run"' is a design."""
    lines = [l for l in brief.splitlines()
             if re.match(r"\s*-?\s*(intent|style|medium|output)\s*:", l, re.I)] or [brief]
    text_ = re.sub(r"\b(no|not|never|avoid|without)\b[^.;,\n]*", " ", " ".join(lines), flags=re.I)
    d, p = DESIGN_KIND.search(text_), PHOTO_MEDIUM.search(text_)
    if d and QUOTED.search(brief) and not PLATE.search(brief) and (not p or d.start() < p.start()):
        return "design"
    if NON_PHOTO.search(text_):
        return "styled"
    return "photo"


def is_non_photo(brief: str) -> bool:
    return image_kind(brief) != "photo"


def _parse_par_result(text_: str):
    for cand in re.findall(r"\{.*\}", text_ or "", re.S):
        try:
            d = json.loads(cand)
        except ValueError:
            continue
        if isinstance(d, dict) and "results" in d:
            return d
    return None


def _rollout_result(tid):
    """The batch call's JSON line from the session rollout (when the agent never repeated it), else None."""
    parsed = None
    try:
        rp = find_rollout(tid)
        if not rp:
            return None
        for line in Path(rp).read_text(encoding="utf-8", errors="replace").splitlines():
            if '"total_ms' in line:
                try:
                    pl = json.loads(line).get("payload") or {}
                except ValueError:
                    continue
                for itm in pl.get("output") or []:
                    if isinstance(itm, dict):
                        parsed = _parse_par_result(itm.get("text", "")) or parsed
    except (OSError, AttributeError, TypeError) as e:
        log(f"WARNING: could not read the session rollout ({e!r})")
    return parsed


def run_cancellable(cmd: list, prompt: str, timeout: int, tmp: Path, cancel=None) -> tuple:
    """run_group() for callers that only need (stdout, error or None)."""
    res = run_group(cmd, prompt, timeout, tmp, cancel)
    return res["stdout"], res["error"]


class BatchResultWatch:
    """Early result of a batch-image session. The batch call's JSON line lands in the session rollout the moment
    the call returns; after that the agent only repeats it as its final answer, which took 5.5 s median (p90 8.5 s)
    over 328 real sessions. Each poll reads only the bytes added since the last one; anything unexpected simply
    means "not yet", and the normal end of the session still applies. CODEX_IMAGEGEN_WAIT_FOR_REPLY=1 turns it off."""

    def __init__(self, stdout_path: Path, ids):
        self.stdout_path, self.ids = Path(stdout_path), {i for i in ids}
        self.tid = self.path = None
        self.pos, self.buf = 0, b""

    def __call__(self):
        if self.tid is None:
            self.tid = thread_from(self.stdout_path.read_text(encoding="utf-8", errors="replace"))
            if self.tid is None:
                return None
        if self.path is None:
            self.path = find_rollout(self.tid)
            if self.path is None:
                return None
        with open(self.path, "rb") as fh:
            fh.seek(self.pos)
            chunk = fh.read()
        self.pos += len(chunk)
        lines = (self.buf + chunk).split(b"\n")
        self.buf = lines.pop()  # a line still being written waits for the next poll
        for line in lines:
            if b'"total_ms' not in line or b"call_output" not in line:
                continue
            try:
                outs = (json.loads(line).get("payload") or {}).get("output")
            except ValueError:
                continue
            texts = [x.get("text", "") for x in outs if isinstance(x, dict)] if isinstance(outs, list) else [str(outs)]
            for t in texts:
                parsed = _parse_par_result(t)
                got = {r.get("id") for r in (parsed or {}).get("results") or [] if isinstance(r, dict)}
                if parsed and self.ids <= got:
                    return parsed
        return None


def batch_watch(tmp: Path, ids):
    return None if os.environ.get("CODEX_IMAGEGEN_WAIT_FOR_REPLY") else BatchResultWatch(tmp / "stdout.jsonl", ids)


def codex_parallel_images(tasks: list, workdir: Path, effort: str, timeout: int, kind: str = "generate",
                          cancel=None) -> dict:
    """Generate every task concurrently inside ONE Codex session. tasks: [{"id", "prompt", "refs"}].
    Returns {id: {"ok", "src", "ms", "err"}} plus session stats."""
    bin_ = codex_bin()
    tmp = Path(tmp_dir(prefix="codex-par-"))
    jobs_file = tmp / "jobs.json"
    jobs_file.write_text(json.dumps([{"id": t["id"], "prompt": t["prompt"], "refs": [str(r) for r in t.get("refs") or []]}
                                     for t in tasks], ensure_ascii=False), encoding="utf-8")
    has_refs = any(t.get("refs") for t in tasks)
    code = (PAR_JS.replace("__JOBS__", str(jobs_file)).replace("__YIELD__", str(max(60, timeout - 30) * 1000))
            .replace("__VIEW_REFS__", PAR_VIEW_REFS if has_refs else "")
            .replace("__ARGS__", "Object.assign({prompt: j.prompt}, (j.refs && j.refs.length) ? "
                                 "{referenced_image_paths: j.refs} : {})" if has_refs else "{prompt: j.prompt}"))
    prompt = PAR_TASK.replace("{code}", code)
    last = tmp / "last.txt"
    cmd = [bin_, "exec", "--skip-git-repo-check", "-s", "read-only", "--json", "-C", str(workdir),
           "-c", f'model_reasoning_effort="{effort}"'] + LEAN_FLAGS + ["-o", str(last), "-"]
    t0 = time.time()
    run = run_group(cmd, prompt, timeout, tmp, cancel, ready=batch_watch(tmp, [t["id"] for t in tasks]))
    out, err = run["stdout"], run["error"]
    wall = time.time() - t0
    tid = thread_from(out)
    rec = record_run(kind, prompt, out, tid, wall, {"tasks": [t["id"] for t in tasks], "error": err,
                                                    "early_result": bool(run["early"])})
    parsed = run["early"] or _parse_par_result(last.read_text(encoding="utf-8") if last.exists() else "")
    if not parsed:
        for line in out.splitlines():
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            it = ev.get("item") or {}
            if it.get("type") == "agent_message":
                parsed = _parse_par_result(it.get("text", "")) or parsed
    if not parsed:
        parsed = _rollout_result(tid)
    results = {}
    for r in (parsed or {}).get("results", []):
        src = Path(r["path"]) if r.get("ok") and r.get("path") else None
        results[r.get("id")] = {"ok": bool(src and src.exists()), "src": str(src) if src else None,
                                "ms": r.get("ms"), "err": r.get("err") or r.get("note")}
    for t in tasks:  # no result line for a task: it failed for the session's own reason
        results.setdefault(t["id"], {"ok": False, "src": None, "ms": None, "err": None})
    explain_failures([results[t["id"]] for t in tasks], run, rec["step"])
    return {"results": results, "wall_s": round(wall, 1), "thread_id": tid, "session_total_ms": (parsed or {}).get(
        "total_ms"), "tokens": (rec.get("digest") or {}).get("tokens")}


def generate_parallel(tasks: list, workdir: Path, args, kind: str = "generate") -> dict:
    """Chunk tasks into sessions of --max-parallel, run the sessions concurrently, retry quick failures once (never a
    timeout, a stop or a usage-limit or login error)."""
    import concurrent.futures as cf
    size = max(1, args.max_parallel)
    chunks = [tasks[i:i + size] for i in range(0, len(tasks), size)]
    merged, sessions = {}, []
    with cf.ThreadPoolExecutor(max_workers=len(chunks)) as ex:
        for res in ex.map(lambda ch: codex_parallel_images(ch, workdir, args.gen_effort, args.timeout, kind), chunks):
            merged.update(res["results"])
            sessions.append({k: v for k, v in res.items() if k != "results"})
    failed = [t for t in tasks if not merged[t["id"]]["ok"] and retry_worth(merged[t["id"]].get("err"))]
    if failed:
        log(f"{len(failed)} image(s) failed ({', '.join(t['id'] for t in failed)}); retrying once")
        res = codex_parallel_images(failed, workdir, args.gen_effort, args.timeout, kind + "-retry")
        for t in failed:
            if res["results"][t["id"]]["ok"]:
                merged[t["id"]] = dict(res["results"][t["id"]], retried=True)
        sessions.append({k: v for k, v in res.items() if k != "results"})
    return {"results": merged, "sessions": sessions}


def judge_parallel(entries: list, args, cancel=None) -> dict:
    """entries: [(job_id, image_path, brief, checklist)] -> {job_id: judge dict}; one fresh Codex session each.
    A set `cancel` event ends judges still running (another candidate was usable first)."""
    import concurrent.futures as cf
    if not entries:
        return {}
    out, kw = {}, ({"cancel": cancel} if cancel is not None else {})
    timeout = getattr(args, "judge_timeout", None) or JUDGE_TIMEOUT
    with cf.ThreadPoolExecutor(max_workers=max(1, min(getattr(args, "judge_workers", 10), len(entries)))) as ex:
        futs = {ex.submit(run_judge, Path(img), brief, args.threshold, args.judge_model, args.judge_effort, timeout,
                          checklist, jid, **kw): jid for jid, img, brief, checklist in entries}
        for fu in cf.as_completed(futs):
            try:
                out[futs[fu]] = fu.result()
            except Exception as e:  # a judge crash must not lose the batch
                out[futs[fu]] = {"computed_verdict": "ERROR", "error": str(e)[:300]}
    return out


FINISHES = {  # photographic finish applied once to the chosen image (after judging); the original stays as -raw
    # wb: share of the midtone colour cast removed; grain: noise sigma (8-bit levels) at 1536 px; size: grain size in
    # px at 1536 px; chroma: share of colour noise; vignette: edge darkening; halation: red glow around highlights;
    # lift: black lift in levels
    # Ranges from photo tools (2026-09-23 research): grain 0.02-0.04 std at mid-grey (5-10 levels), grain size about
    # long edge / 2500 px, soften 0.3-0.5 px before film grain, vignette -0.2 to -0.4 EV, none on portraits/products.
    "clean": {"wb": 0.6, "grain": 0.0, "size": 1.0, "chroma": 0.0, "vignette": 0.0, "halation": 0.0, "lift": 0,
              "soften": 0.0, "sat": 1.0},
    "natural": {"wb": 0.6, "grain": 4.0, "size": 1.0, "chroma": 0.0, "vignette": 0.08, "halation": 0.0, "lift": 2,
                "soften": 0.3, "sat": 0.97},
    "portrait": {"wb": 0.6, "grain": 0.0, "size": 1.0, "chroma": 0.0, "vignette": 0.04, "halation": 0.0, "lift": 0,
                 "soften": 0.0, "sat": 0.98},
    "phone": {"wb": 0.35, "grain": 3.5, "size": 1.0, "chroma": 0.3, "vignette": 0.02, "halation": 0.0, "lift": 0,
              "soften": 0.0, "sat": 1.0},
    "film": {"wb": 0.3, "grain": 8.0, "size": 1.4, "chroma": 0.0, "vignette": 0.12, "halation": 0.10, "lift": 5,
             "soften": 0.4, "sat": 0.97},
}
LOOK_FINISH = {"editorial": "natural", "portrait": "portrait", "brief": "natural", "phone": "phone",
               "phone-flash": "phone", "film": "film", "product": "clean", "interior": "clean"}
WARM_LIGHT = re.compile(r"\b(tungsten|candle\w*|bulbs?|lamps?|lanterns?|fire\w*|sunset|sunrise|golden hour|dusk|"
                        r"fairy lights|neon|string lights|pendant)\b", re.I)


def midtone_cast(im) -> float:
    """Mean R - B over midtones (a warm/orange cast is positive)."""
    from PIL import ImageStat
    small = im.convert("RGB").copy()
    small.thumbnail((512, 512))
    mask = small.convert("L").point(lambda v: 255 if 60 <= v <= 200 else 0)
    if not mask.getbbox():  # no midtones at all (a night frame or a white packshot)
        return 0.0
    r, _, b = ImageStat.Stat(small, mask).mean
    return round(r - b, 1)


def finish_image(src: Path, profile: str = "natural", dst=None, warm_scene: bool = False, **over) -> dict:
    """Photographic finish: partial white balance on the midtone cast, black lift, halation, vignette and luminance
    grain scaled to the image size. Writes dst (default: in place, keeping the untouched original as -raw)."""
    Image = need_pillow()
    from PIL import ImageChops, ImageFilter, ImageStat
    prm = dict(FINISHES[profile], **{k: v for k, v in over.items() if v is not None})
    if warm_scene:
        prm["wb"] = min(prm["wb"], 0.35)  # keep the mood of a lamp-lit or sunset scene, only trim the overcast
    generated = ai_source(src)  # only generated files are declared AI-generated; a client's photo stays untagged
    with Image.open(src) as im0:
        im0.load()
        alpha = im0.convert("RGBA").getchannel("A") if "A" in im0.getbands() or "transparency" in im0.info else None
        im = im0.convert("RGB")
    w, h = im.size
    k = max(w, h) / 1536
    before = midtone_cast(im)
    L = im.convert("L")
    gains = [1.0, 1.0, 1.0]
    if prm["wb"]:
        # shades-of-grey (p=6) over near-neutral, unclipped pixels: grey-world is fooled by big coloured areas
        sat = im.convert("HSV").getchannel("S").point(lambda v: 255 if v < 102 else 0)
        mask = ImageChops.multiply(sat, L.point(lambda v: 255 if 12 <= v <= 248 else 0))
        if ImageStat.Stat(mask).mean[0] < 0.05 * 255:
            mask = L.point(lambda v: 255 if 12 <= v <= 248 else 0)
        hist = im.histogram(mask)
        est = []
        for c in range(3):
            hc = hist[c * 256:(c + 1) * 256]
            n = sum(hc) or 1
            est.append((sum(cnt * (i / 255) ** 6 for i, cnt in enumerate(hc)) / n) ** (1 / 6) or 1e-6)
        luma = [0.299, 0.587, 0.114]
        y = sum(w * e for w, e in zip(luma, est))
        gains = [max(1 / 1.2, min(1.2, y / e)) ** prm["wb"] for e in est]
        norm = y / max(1e-6, sum(w * g * e for w, g, e in zip(luma, gains, est)))  # keep brightness
        gains = [g * norm for g in gains]
        if max(abs(g - 1) for g in gains) < 0.02:  # no real cast: leave the colour alone
            gains = [1.0, 1.0, 1.0]
        # full gain up to level 190, fading to none at 255, so clipped whites stay neutral instead of turning cyan
        im = im.point([min(255, int(round(i * (1 + (g - 1) * min(1.0, max(0.0, (255 - i) / 65))))))
                       for g in gains for i in range(256)])
    if prm["lift"]:
        lift = prm["lift"]
        im = im.point([int(lift + i * (255 - lift) / 255) for _ in range(3) for i in range(256)])
    if prm["halation"]:
        hi = im.convert("L").point(lambda v: 0 if v < 215 else min(255, (v - 215) * 6))
        glow = hi.filter(ImageFilter.GaussianBlur(radius=max(3.0, max(w, h) * 0.006)))
        a = prm["halation"]
        red = Image.merge("RGB", (glow.point(lambda v: int(v * a)), glow.point(lambda v: int(v * a * 0.3)),
                                  Image.new("L", im.size, 0)))
        im = ImageChops.screen(im, red)
    if prm["vignette"]:
        g = Image.radial_gradient("L").resize(im.size, Image.BICUBIC)
        vig = g.point(lambda v: int(255 * (1 - prm["vignette"] * (v / 255) ** 2)))
        im = Image.merge("RGB", [ImageChops.multiply(b, vig) for b in im.split()])
    if prm.get("sat", 1.0) != 1.0:  # the fakes that fool people look realistic but not professional (Roca 2025)
        from PIL import ImageEnhance
        im = ImageEnhance.Color(im).enhance(prm["sat"])
    if prm.get("soften"):
        im = im.filter(ImageFilter.GaussianBlur(radius=prm["soften"] * k))  # film cannot resolve finer than its grain
    if prm["grain"]:
        size = max(1.0, prm["size"] * k)
        gw, gh = max(1, int(w / size)), max(1, int(h / size))
        # midtone bias 0.8: grain fades in bright flat areas (walls, skies) where it reads as a filter
        weight = im.convert("L").point(lambda v: int(255 * (0.2 + 0.8 * 4 * (v / 255) * (1 - v / 255))))
        flat = Image.new("L", (w, h), 128)
        mono = Image.effect_noise((gw, gh), prm["grain"]).resize((w, h), Image.BICUBIC)
        if size < 1.3:
            mono = mono.filter(ImageFilter.GaussianBlur(radius=0.35)).point(lambda v: int(128 + (v - 128) * 1.6))
        bands = []
        for i, b in enumerate(im.split()):
            n = mono
            if prm["chroma"]:
                own = Image.effect_noise((gw, gh), prm["grain"]).resize((w, h), Image.BICUBIC)
                n = Image.blend(mono, own, prm["chroma"])
            bands.append(ImageChops.add(b, Image.composite(n, flat, weight), 1.0, -128))
        im = Image.merge("RGB", bands)
    if alpha is not None:
        im.putalpha(alpha)
    src = Path(src)
    if dst is None:
        raw = unique_path(src.with_name(f"{src.stem}-raw{src.suffix}"))
        shutil.copy2(src, raw)
        dst = src
    im.save(dst, **finish_save_kwargs(dst, generated, profile))
    return {"profile": profile, "params": prm, "wb_gains": [round(g, 3) for g in gains], "cast_before": before,
            "cast_after": midtone_cast(im), "path": str(dst)}


AI_SOURCE_XMP = ('<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
                 '<rdf:Description xmlns:Iptc4xmpExt="http://iptc.org/std/Iptc4xmpExt/2008-02-29/" '
                 'Iptc4xmpExt:DigitalSourceType="http://cv.iptc.org/newscodes/digitalsourcetype/'
                 'trainedAlgorithmicMedia"/></rdf:RDF></x:xmpmeta>')


GEN_SUFFIX = re.compile(r"-(?:(?:raw|c\d+|first|fix\d+|regen\d+)(?:-v\d+)?|v\d+)$")  # masters, candidates, re-runs


def own_sidecar(path):
    """The .meta.json the skill wrote for exactly this output (its output_path names this file), else None."""
    p = Path(path)
    m = p.with_name(f"{p.stem}.meta.json")
    try:
        rec = json.loads(m.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return m if isinstance(rec, dict) and Path(str(rec.get("output_path") or "")).name == p.name else None


def is_generated_file(p: Path) -> bool:
    """A job output, its -raw master, a candidate or a re-run attempt: each sits next to its job's .meta.json."""
    return any(p.with_name(f"{s}.meta.json").exists() for s in {p.stem, GEN_SUFFIX.sub("", p.stem)})


def ai_source(path) -> bool:
    """True when the file declares it is generated (a C2PA manifest, caBX / c2pa, or our IPTC source type) or the
    skill's own .meta.json names it, so an output whose metadata a re-save lost is still declared on export."""
    try:
        with open(path, "rb") as fh:
            head = fh.read(8_000_000)
    except OSError:
        return False
    return b"trainedAlgorithmicMedia" in head or b"caBX" in head or b"c2pa" in head or own_sidecar(path) is not None


def provenance_kwargs(dst) -> dict:
    """Re-saving drops the C2PA manifest, so every derivative says in IPTC metadata that it is AI-generated
    (DigitalSourceType trainedAlgorithmicMedia); the -raw.png master keeps the signed C2PA manifest."""
    ext = Path(dst).suffix.lower()
    if ext == ".png":
        from PIL import PngImagePlugin
        info = PngImagePlugin.PngInfo()
        info.add_itxt("XML:com.adobe.xmp", AI_SOURCE_XMP)
        return {"pnginfo": info}
    if ext in (".jpg", ".jpeg", ".webp", ".avif"):
        return {"xmp": AI_SOURCE_XMP.encode("utf-8")}
    return {}


FINISH_MARK = "codex-imagegen-finish"


def finish_save_kwargs(dst, generated: bool, profile: str) -> dict:
    """PNG gets a finish marker (so an edit of a finished file is not finished twice) plus the AI source tag when
    the source was generated; other formats get the tag only."""
    if Path(dst).suffix.lower() == ".png":
        from PIL import PngImagePlugin
        info = PngImagePlugin.PngInfo()
        info.add_text(FINISH_MARK, profile)
        if generated:
            info.add_itxt("XML:com.adobe.xmp", AI_SOURCE_XMP)
        return {"pnginfo": info}
    return provenance_kwargs(dst) if generated else {}


def is_finished(path) -> bool:
    try:
        from PIL import Image  # type: ignore
        need_pillow()
        with Image.open(path) as im:
            return FINISH_MARK in im.info
    except BaseException:
        return False


def with_finish_default(j: dict) -> str:
    """The finish for one job: its own "finish", else the one its look implies (photos only, never transparent)."""
    f = (j.get("finish") or "auto").lower()
    if f == "auto" and j.get("target") and is_finished(j["target"]):
        return "none"  # editing a finished image: finishing again would double the grain and vignette
    if f == "auto":
        f = "none" if j.get("transparent") or j.get("look") in (None, "-", "none") else LOOK_FINISH.get(j["look"], "natural")
    return f if f in FINISHES else "none"


def place_output(src: str, dest: Path, size, transparent: bool = False) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dst = unique_path(dest)
    shutil.copy2(src, dst)
    if size:
        fit_to_size(dst, *parse_size(size))
    if transparent:
        try:
            refine_alpha(dst)
        except SystemExit:
            log("Pillow missing: transparent edges left unrefined (run doctor --setup)")
        except Exception as e:  # keep the generated file as it is
            log(f"WARNING: transparent edge refine failed for {dst.name} ({e!r}); left as generated")
    return dst


RISK_PATTERNS = [  # configurations that failed repeatedly in the 2026-09-23 benchmark (model limits, not prompt gaps)
    ("tilted liquid container", r"\b(tilt\w*|tipp\w*)\s+(the\s+|a\s+|her\s+|his\s+)?(cup|glass|bowl|mug|bucket)\b|"
                                r"\b(cup|glass|bowl|mug|bucket)\b[^.;\n]{0,40}\b(tilt\w*|tipped)\b"),
    ("upside-down object resting on contact points", None),
    ("tool engaging a fastener", r"\b(wrench|spanner|screwdriver|pliers)\b"),
    ("rope or string continuity through a hand", r"\b(kite|string|rope|thread)\b[\s\S]{0,400}\b(hand|fingers?|pinch\w*)\b"),
    ("catchlights in close-up eyes", r"\bcatchlights?\b"),
    ("three or more exact text strings", r"(?:[\"“][^\"”]{1,120}[\"”][\s\S]*?){3,}"),
]


def upside_down_object(brief: str) -> bool:
    """'upside down' that describes an object, not a reflection ('the pond reflects the house upside down')."""
    return any(re.search(r"\bupside[- ]down\b", c, re.I) and not re.search(r"\b(reflect\w*|mirror\w*)", c, re.I)
               for c in re.split(r"[.;\n]", brief))


def brief_risks(brief: str) -> list:
    return [name for name, rx in RISK_PATTERNS
            if (upside_down_object(brief) if rx is None else re.search(rx, brief, re.I))]


COMPLEX_CHECKS = 6  # briefs that trigger this many prompt-time checks failed most often in the benchmark


def _job_candidates(j, args) -> int:
    if j.get("candidates"):
        return max(1, min(4, int(j["candidates"])))
    complex_ = bool(j["risks"]) or j.get("n_checks", len(j["hints"])) >= COMPLEX_CHECKS  # place/realism checks don't count
    return max(args.candidates, 2 if (args.auto_candidates and complex_) else 1)


def _judge_many(cands: list, j, args, cancel=None):
    todo = [c for c in cands if "judge" not in c]
    if not (args.judge and todo):
        return
    def view(c):
        if not j.get("transparent"):
            return c["path"]
        try:
            return str(judge_view(Path(c["path"])))
        except Exception as e:  # judge the file itself rather than lose the job
            log(f"{Path(c['path']).name}: grey judge view failed ({e!r}); judging the file as is")
            return c["path"]
    res = judge_parallel([(Path(c["path"]).stem, view(c), j["brief"], j["hints"]) for c in todo], args, cancel)
    for c in todo:
        c["judge"] = res.get(Path(c["path"]).stem)


def gen_candidates(j: dict, job_id: str, brief: str, k: int, refs: list, args, workdir: Path, kind: str,
                   edit: bool = False) -> tuple:
    """-> (list of {"ok","src","ms","err","prompt"}, sessions). prompt_writer codex = art-director session (default),
    compiled = the script's compiled prompt verbatim (fastest)."""
    if args.prompt_writer == "codex":
        sessions, out = [], []
        for attempt in range(2):
            res = codex_lite_job(job_id, brief, j["hints"], j.get("aspect"), k, refs, args, kind, edit)
            sessions.append({kk: v for kk, v in res.items() if kk != "results"})
            out = [dict(r, prompt=res.get("prompt") or brief) for r in res["results"]]
            why = res.get("error") or next((r.get("err") for r in out if r.get("err")), None) or "no result"
            if any(r["ok"] for r in out) or attempt or not retry_worth(why):
                break
            log(f"{job_id}: no image from the Codex session ({why}); retrying once")
        return out, sessions
    prompt = brief if getattr(args, "raw_prompt", False) else \
        compile_prompt(brief, j.get("aspect"), edit=edit or bool(j.get("target")))[0]
    tasks = [{"id": f"{job_id}-c{i + 1}", "prompt": prompt, "refs": refs} for i in range(k)]
    gen = generate_parallel(tasks, workdir, args, kind)
    return [dict(gen["results"][t["id"]], prompt=prompt) for t in tasks], gen["sessions"]


def job_pipeline(j: dict, args, workdir: Path, out_dir: Path) -> dict:
    """One job end to end: k candidates in one Codex session -> parallel judges -> fix rounds -> best kept."""
    t0 = time.time()
    name, k = j["name"], BUDGET.take(_job_candidates(j, args))
    kind = "edit" if j.get("target") else "generate"
    if k == 0:
        j.update(error="image budget (--max-images) exhausted before this job", candidates_out=[])
        return j
    cands, results = [], []
    j["sessions"] = []
    if k >= 2 and args.prompt_writer == "compiled" and args.judge and getattr(args, "early_exit", True):
        # every candidate in its own session; each is judged the moment it lands, while the others still generate or
        # are being judged; the first usable verdict cancels the sessions and judges still running
        import concurrent.futures as cf
        prompt = j["brief"] if getattr(args, "raw_prompt", False) else \
            compile_prompt(j["brief"], j.get("aspect"), edit=bool(j.get("target")))[0]
        cancel = threading.Event()
        with cf.ThreadPoolExecutor(max_workers=2 * k) as ex:
            pending = {ex.submit(codex_parallel_images, [{"id": f"{name}-c{i + 1}", "prompt": prompt,
                                                          "refs": j["refs_all"]}], workdir, args.gen_effort,
                                 args.timeout, kind, cancel): None for i in range(k)}  # value: None = generation
            while pending:
                done, _ = cf.wait(pending, return_when=cf.FIRST_COMPLETED)
                for fu in done:
                    c = pending.pop(fu)
                    if c is not None:  # a judge finished
                        fu.result()
                        if (c.get("judge") or {}).get("computed_verdict") in VERDICT_LEVEL and not cancel.is_set():
                            cancel.set()  # usable image found: stop the slower candidates and their judges
                            j["early_exit"] = f"{Path(c['path']).name} {c['judge']['computed_verdict']}"
                            log(f"{name}: {j['early_exit']} - cancelling the other candidate session(s)")
                        continue
                    res = fu.result()
                    j["sessions"].append({kk: v for kk, v in res.items() if kk != "results"})
                    r = next(iter(res["results"].values()))
                    results.append(r)
                    if not r["ok"] or cancel.is_set():
                        continue
                    dst = place_output(r["src"], out_dir / (f"{name}.png" if not cands else
                                                            f"{name}-c{len(cands) + 1}.png"),
                                       j.get("size"), bool(j.get("transparent")))
                    c = {"path": str(dst), "mode": f"candidate{len(cands) + 1}", "src": r["src"],
                         "gen_ms": r.get("ms"), "prompt": prompt}
                    cands.append(c)
                    j.setdefault("t_generated", round(time.time() - t0, 1))
                    pending[ex.submit(_judge_many, [c], j, args, cancel)] = c
        if not cands and results and all(retry_worth(r.get("err")) for r in results):
            # every session failed quickly: one plain retry (never after a timeout, a stop or a usage-limit error)
            log(f"{name}: no image from {len(results)} session(s); retrying once")
            res = codex_parallel_images([{"id": f"{name}-c1", "prompt": prompt, "refs": j["refs_all"]}], workdir,
                                        args.gen_effort, args.timeout, kind + "-retry")
            j["sessions"].append({kk: v for kk, v in res.items() if kk != "results"})
            results = [dict(r, prompt=prompt) for r in res["results"].values()]
    else:
        results, sessions = gen_candidates(j, name, j["brief"], k, j["refs_all"], args, workdir, kind,
                                           bool(j.get("target")))
        j["sessions"] = list(sessions)
    if not cands:
        for i, r in enumerate(results):
            if r["ok"]:
                dst = place_output(r["src"], out_dir / (f"{name}.png" if not cands else f"{name}-c{i + 1}.png"),
                                   j.get("size"), bool(j.get("transparent")))
                cands.append({"path": str(dst), "mode": "initial" if k == 1 else f"candidate{i + 1}", "src": r["src"],
                              "gen_ms": r.get("ms"), "prompt": r.get("prompt")})
        j["t_generated"] = round(time.time() - t0, 1)
    if not cands:
        j["error"] = "; ".join(dict.fromkeys(str(r.get("err")) for r in results)) or "no image produced"
        j["candidates_out"] = []
        return j
    _judge_many(cands, j, args)
    j["t_judged"] = round(time.time() - t0, 1)
    first_best = max(cands, key=lambda c: judge_rank(c.get("judge")))
    j["first_pass"] = (first_best.get("judge") or {}).get("computed_verdict")
    rounds = max(0, min(3, args.fix_rounds)) if args.judge else 0
    best0 = (max(cands, key=lambda c: judge_rank(c.get("judge"))).get("judge") or {})
    local_fix = best0.get("fix_mode") == "edit" and set(quality_gate_fails(best0)) <= LOCAL_GATES
    if len(cands) >= 2 and all((c.get("judge") or {}).get("computed_verdict") == "FAIL" for c in cands) \
            and all(quality_gate_fails(c.get("judge")) for c in cands) and not local_fix:
        # every candidate broke a hard quality rule: in the 2026-09-23 benchmarks such fixes succeeded 0 times, while
        # score/style/brief failures were fixed 3 of 3 times -> skip the round, report the rules instead
        j["model_limit"] = sorted(set().union(*[quality_gate_fails(c.get("judge")) for c in cands]))
        log(f"{name}: all {len(cands)} candidates break {', '.join(j['model_limit'])}; skipping the fix round "
            f"(likely a model limit: simplify that part of the brief)")
        rounds = 0
    bonus = 1 if args.judge else 0  # one extra local edit for a leftover mark or stray text
    r = 0
    while True:
        r += 1
        best = max(reversed(cands), key=lambda c: judge_rank(c.get("judge")))
        jd = best.get("judge") or {}
        fix = (jd.get("fix_instruction") or "").strip()
        if jd.get("computed_verdict") != "FAIL" or not fix:
            break
        if r > rounds:
            if not (bonus and jd.get("fix_mode") == "edit" and set(quality_gate_fails(jd)) <= LOCAL_GATES):
                break
            bonus = 0
            log(f"{name}: one extra local edit for a small remaining defect")
        mode = jd.get("fix_mode") if jd.get("fix_mode") in ("edit", "regenerate") else "regenerate"
        if mode == "edit":
            fbrief = (f"Edit Image 1 (the reference). {fix}\nKeep its composition, people, objects, light and "
                      f"everything not named above exactly the same.\nOriginal brief for context:\n{j['brief']}")
            refs = [best["path"]] + list(j.get("refs") or [])
        else:
            fbrief = f"{j['brief']}\nCorrection from independent QA of the previous attempt (must hold): {fix}"
            refs = j["refs_all"]
        if BUDGET.take(1) == 0:
            log(f"{name}: image budget exhausted; no fix round")
            break
        log(f"{name}: fix round {r} ({mode}): {fix[:120]}")
        fres, fsess = gen_candidates(j, f"{name}-fix{r}", fbrief, 1, refs, args, workdir, "fix", mode == "edit")
        j["sessions"] += fsess
        res = next((x for x in fres if x["ok"]), None)
        if not res:
            break
        dst = place_output(res["src"], out_dir / f"{name}-{'fix' if mode == 'edit' else 'regen'}{r}.png",
                           j.get("size"), bool(j.get("transparent")))
        c = {"path": str(dst), "mode": mode, "src": res["src"], "gen_ms": res.get("ms"), "prompt": res.get("prompt"),
             "fix_instruction": fix}
        cands.append(c)
        _judge_many([c], j, args)
    best = max(cands, key=lambda c: judge_rank(c.get("judge")))
    final = out_dir / f"{name}.png"
    first = next((c for c in cands if Path(c["path"]) == final), None)
    if first is not None and first is not best:  # the deliverable is <name>.png; files from earlier runs are untouched
        alt = unique_path(out_dir / f"{name}-c1.png" if first["mode"].startswith("candidate") else
                          out_dir / f"{name}-first.png")
        final.rename(alt)
        first["path"] = str(alt)
        Path(best["path"]).rename(final)
        best["path"] = str(final)
    fin = with_finish_default(j)
    if fin != "none" and Path(best["path"]).exists():
        try:
            warm = bool(WARM_LIGHT.search(own_positive(place_context(j["brief"])[0])))
            j["finish_info"] = finish_image(Path(best["path"]), fin, warm_scene=warm)
            log(f"{name}: finish {fin} (cast {j['finish_info']['cast_before']} -> {j['finish_info']['cast_after']})")
        except SystemExit:
            log(f"{name}: Pillow missing, no finish (run doctor --setup)")
        except Exception as e:  # a finishing problem must never cost the judged image
            j["finish_info"] = {"error": repr(e)}
            log(f"{name}: finish skipped ({e!r}); the unfinished image is kept")
    j["candidates_out"], j["best"] = cands, best
    j["t_total"] = round(time.time() - t0, 1)
    return j


def fast_pipeline(jobs: list, args, workdir: Path, out_dir: Path, rep=None, progress=None) -> dict:
    """jobs: [{"name", "brief", "aspect"?, "size"?, "refs"?, "target"?, "candidates"?}] -> report dict.
    Every job runs its own pipeline concurrently, so one slow image never holds up the others. Each job writes its
    <name>.meta.json (and a line in `progress`) the moment it ends, and `rep` (when given) holds the rows finished so
    far, so a run that is cut short still keeps and reports every finished job."""
    import concurrent.futures as cf
    t0 = time.time()
    rep = {} if rep is None else rep
    rep.update(mode="fast", images=[])
    set_phase("run")
    for j in jobs:
        if j.get("transparent") and not re.search(r"transparent background", j["brief"], re.I):
            j["brief"] += ("\nOutput: fully transparent background (PNG alpha); the subject isolated with clean edges; "
                           "no backdrop, floor, frame or shadow plane.")
        j["prompt"], j["hints"] = compile_prompt(j["brief"], j.get("aspect"), edit=bool(j.get("target")))
        j["n_checks"] = len(failure_hints(place_context(j["brief"])[0]))
        j["place"] = {k: v for k, v in place_context(j["brief"])[1].items() if k != "hints"}
        j["look"] = pick_look(place_context(j["brief"])[0])[0] if not is_non_photo(j["brief"]) else "-"
        if j.get("cast_auto"):
            j["place"]["cast"] = j["cast_auto"]
        if j.get("transparent"):
            j["hints"] = j["hints"] + ["Transparent asset: it is judged on a neutral grey backdrop that is not part of the "
                                       "image; the subject is fully isolated with clean anti-aliased edges and no light "
                                       "or dark fringe, halo or stray pixels."]
        j["lint"] = lint_brief(j["brief"], j.get("aspect"))
        j["risks"] = brief_risks(j["brief"])
        j["refs_all"] = ([j["target"]] if j.get("target") else []) + list(j.get("refs") or [])
        log_file(f"prompts/{j['name']}.txt", j["prompt"])
    out_dir.mkdir(parents=True, exist_ok=True)
    log(f"fast: {len(jobs)} job(s) in parallel; candidates per job: "
        + ", ".join(f"{j['name']}={_job_candidates(j, args)}" for j in jobs))
    rows, lock = {}, threading.Lock()

    def safe(jj):
        try:
            jj = job_pipeline(jj, args, workdir, out_dir)
        except (Exception, SystemExit) as e:  # one broken job must not lose the rest of the batch
            why = getattr(e, "message", None) or repr(e)
            log(f"{jj['name']}: job failed: {why}")
            jj.update(error=f"job failed: {why}", candidates_out=[])
        try:
            row = job_row(jj)  # its meta.json is written now, not after the whole batch
        except Exception as e:
            row = {"name": jj["name"], "path": None, "error": f"could not write the job's meta.json: {e!r}"}
        with lock:
            rows[jj["name"]] = row
            rep["images"] = [rows[x["name"]] for x in jobs if x["name"] in rows]
        note_progress(progress, row)
        return jj

    with cf.ThreadPoolExecutor(max_workers=max(1, min(args.concurrency, len(jobs)))) as ex:
        done = list(ex.map(safe, jobs))
    images = rep["images"]
    totals = [i["timing_s"]["total"] for i in images if i.get("timing_s")]
    timing = {"total_s": round(time.time() - t0, 1), "slowest_job_s": max(totals) if totals else None,
              "median_job_s": sorted(totals)[len(totals) // 2] if totals else None}
    rep.update(timing=timing, sessions=[s for j in done for s in (j.get("sessions") or [])],
               passed=sum(1 for i in images if i.get("verdict") in VERDICT_LEVEL),
               first_pass=sum(1 for i in images if i.get("first_pass") in VERDICT_LEVEL))
    if _LIVE["fatal"]:
        rep["stopped"] = _LIVE["fatal"]
    return rep


def job_row(j: dict) -> dict:
    """The report row of one finished job. Writes the job's <name>.meta.json next to its image first."""
    cands = j.get("candidates_out") or []
    if not cands:
        return {"name": j["name"], "path": None, "error": j.get("error")}
    best = j["best"]
    jd = best.get("judge") or {}
    info = png_info(Path(best["path"]))
    rounds = [{"path": c["path"], "mode": c["mode"], "gen_ms": c.get("gen_ms"),
               "verdict": (c.get("judge") or {}).get("computed_verdict"),
               "score_total": (c.get("judge") or {}).get("score_total"),
               "scores": (c.get("judge") or {}).get("scores"), "gates": (c.get("judge") or {}).get("gates"),
               "fix_instruction": c.get("fix_instruction")} for c in cands]
    meta = {"created": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "engine": "codex-fast",
            "name": j["name"], "brief": j["brief"], "aspect": j.get("aspect"), "lint": j["lint"],
            "risks": j["risks"], "place": j.get("place"), "look": j.get("look"), "finish": j.get("finish_info"),
            "prompt_time_checks": j["hints"],
            "final_prompt": best["prompt"],
            "output_path": best["path"], "source_path": best["src"],
            "image_model": "codex built-in image_gen (client requests gpt-image-2)", "judge": jd,
            "first_pass": j.get("first_pass"), "transparent": bool(j.get("transparent")),
            "rounds": rounds, "rejected": [c["path"] for c in cands if c is not best],
            "timing_s": {"generated": j.get("t_generated"), "judged": j.get("t_judged"), "total": j.get("t_total")},
            "sessions": j.get("sessions"), "model_limit": j.get("model_limit"), "early_exit": j.get("early_exit"),
            **info}
    mp = Path(best["path"]).with_name(f"{Path(best['path']).stem}.meta.json")
    write_atomic(mp, json.dumps(meta, indent=2, ensure_ascii=False, default=str))
    return {"name": j["name"], "path": best["path"], "width": info.get("width"),
            "height": info.get("height"), "verdict": jd.get("computed_verdict"), "scores": jd.get("scores"),
            "first_pass": j.get("first_pass"), "risks": j["risks"], "place": j.get("place"),
            "look": j.get("look"),
            "rounds": [(Path(c["path"]).name, c["mode"], (c.get("judge") or {}).get("computed_verdict"),
                        (c.get("judge") or {}).get("score_total")) for c in cands],
            "gen_s": round(max((c.get("gen_ms") or 0) for c in cands[:1]) / 1000, 1),
            "timing_s": {"generated": j.get("t_generated"), "judged": j.get("t_judged"),
                         "total": j.get("t_total")},
            "remaining_fix": jd.get("fix_instruction"), "model_limit": j.get("model_limit"),
            "judge_error": jd.get("error") if jd.get("computed_verdict") == "ERROR" else None,
            "defects": [d.get("what", "") for d in (jd.get("defects") or [])[:2]],
            "early_exit": j.get("early_exit"),
            "meta": str(mp), "lint": j["lint"]}


def latest_meta(name: str, out_dir: Path):
    """The newest meta.json that out_dir holds for job `name` and whose image still exists: (path, meta) or None."""
    best = None
    for mp in Path(out_dir).glob(f"{name}*.meta.json"):
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(meta, dict) or meta.get("name") != name or \
                not Path(str(meta.get("output_path") or "")).is_file():
            continue
        if best is None or mp.stat().st_mtime_ns > best[0].stat().st_mtime_ns:
            best = (mp, meta)
    return best


def row_from_meta(meta: dict, mp: Path) -> dict:
    """A report row rebuilt from a job's meta.json (for --resume and --rejudge)."""
    jd = meta.get("judge") or {}
    rounds = meta.get("rounds") or []
    first = [r.get("verdict") for r in rounds if str(r.get("mode") or "").startswith(("initial", "candidate"))]
    return {"name": meta.get("name"), "path": meta.get("output_path"), "width": meta.get("width"),
            "height": meta.get("height"), "verdict": jd.get("computed_verdict"), "scores": jd.get("scores"),
            "first_pass": meta.get("first_pass") or max(first, key=lambda v: VERDICT_LEVEL.get(v, 0), default=None),
            "risks": meta.get("risks") or [], "place": meta.get("place"), "look": meta.get("look"),
            "rounds": [(Path(str(r.get("path"))).name, r.get("mode"), r.get("verdict"), r.get("score_total"))
                       for r in rounds],
            "gen_s": round((rounds[0].get("gen_ms") or 0) / 1000, 1) if rounds else None,
            "timing_s": meta.get("timing_s") or {}, "remaining_fix": jd.get("fix_instruction"),
            "model_limit": meta.get("model_limit"),
            "judge_error": jd.get("error") if jd.get("computed_verdict") == "ERROR" else None,
            "defects": [d.get("what", "") for d in (jd.get("defects") or [])[:2]],
            "early_exit": meta.get("early_exit"), "meta": str(mp), "lint": meta.get("lint") or []}


def rejudge_jobs(jobs: list, args, out_dir: Path, rep: dict) -> dict:
    """Judge again the images a batch already made (after a judge that timed out or failed), all at once, from each
    job's newest meta.json: the same brief and checks, no new image. Each meta.json gets the new verdict."""
    t0 = time.time()
    set_phase("rejudge")
    found, rows = {}, {}
    for j in jobs:
        m = latest_meta(j["name"], out_dir)
        if m:
            found[j["name"]] = m
        else:
            rows[j["name"]] = {"name": j["name"], "path": None,
                               "error": f"nothing to re-judge: no image with a meta.json for this job in {out_dir}"}
    entries = []
    for name, (mp, meta) in found.items():
        img = Path(meta["output_path"])
        if meta.get("transparent"):  # judged on grey, as in the first run
            try:
                img = judge_view(img)
            except Exception as e:
                log(f"{img.name}: grey judge view failed ({e!r}); judging the file as is")
        entries.append((name, str(img), meta.get("brief") or "", meta.get("prompt_time_checks") or []))
    log(f"re-judging {len(entries)} image(s) at once")
    verdicts = judge_parallel(entries, args)
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for name, (mp, meta) in found.items():
        jd = verdicts.get(name) or {"computed_verdict": "ERROR", "error": "no verdict"}
        meta["judge"], meta["rejudged"] = jd, now
        meta.setdefault("rounds", []).append({"path": meta["output_path"], "mode": "rejudge", "gen_ms": None,
                                              "verdict": jd.get("computed_verdict"),
                                              "score_total": jd.get("score_total"), "scores": jd.get("scores"),
                                              "gates": jd.get("gates"), "fix_instruction": jd.get("fix_instruction")})
        write_atomic(mp, json.dumps(meta, indent=2, ensure_ascii=False, default=str))
        rows[name] = dict(row_from_meta(meta, mp), rejudged=True)
        note_progress(None, rows[name])
    rep["images"] = [rows[j["name"]] for j in jobs if j["name"] in rows]
    rep["timing"] = {"total_s": round(time.time() - t0, 1), "slowest_job_s": None, "median_job_s": None}
    return rep


def order_rows(rows: list, jobs: list) -> list:
    """Report rows in the jobs file's order, one per job."""
    pos = {j["name"]: i for i, j in enumerate(jobs)}
    by = {r["name"]: r for r in rows}
    return [by[n] for n in sorted(by, key=lambda n: pos.get(n, len(pos)))]


PROGRESS_LOCK = threading.Lock()


def note_progress(path, row: dict) -> None:
    """Log a finished job and add one JSON line to `path` (<out>/batch-progress.jsonl), so a long batch can be
    checked while it runs."""
    log(f"done: {row['name']} {row.get('verdict') or row.get('error') or 'no verdict'}"
        + (f" ({row['path']})" if row.get("path") else ""))
    if not path:
        return
    line = json.dumps({"time": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "name": row["name"],
                       "verdict": row.get("verdict"), "path": row.get("path"), "meta": row.get("meta"),
                       "error": row.get("error")}, ensure_ascii=False)
    try:
        with PROGRESS_LOCK, open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as e:
        log(f"WARNING: could not write {Path(path).name} ({e!r})")


def fast_report_md(rep: dict) -> str:
    t, imgs = rep.get("timing") or {}, rep.get("images") or []
    L = [f"# Fast batch report · {rep.get('created', '')}", ""]
    if rep.get("stopped"):
        L += [f"**Stopped.** Codex said: {rep['stopped']}", "",
              "Every later session would fail the same way, so the run stopped at once. Fix that first (a usage "
              "limit: wait until the plan resets; a login error: run `codex login`), then continue with `--resume`.",
              ""]
    L += [f"- Images: {len(imgs)} · passed (PASS or PASS_WITH_NOTES): {rep.get('passed')} · first-pass: "
          f"{rep.get('first_pass')}",
          f"- Wall time: **{t.get('total_s')} s** for the whole batch (slowest job {t.get('slowest_job_s')} s, median "
          f"job {t.get('median_job_s')} s); jobs run concurrently"]
    if rep.get("unfinished"):
        L.append(f"- Not finished (the run was cut short): {', '.join(rep['unfinished'])}. Rerun the same command with "
                 f"`--resume`: it keeps the images that passed and makes only the rest.")
    L += ["", "| Image | Verdict | First pass | Scores R/A/P/C/B | Candidates / rounds | Risks | Place | Look | Job s |",
          "|---|---|---|---|---|---|---|---|---|"]
    for im in imgs:
        sc = im.get("scores") or {}
        s = "/".join(str(sc.get(k, "-")) for k in ("realism", "artifacts", "physics_plausibility", "composition",
                                                   "brief_fidelity"))
        rounds = " → ".join(f"{m}:{v}" for _, m, v, _ in im.get("rounds") or [])
        verdict = (im.get("verdict") or ("-" if im.get("path") else "no image")) + \
            (" (kept from an earlier run)" if im.get("resumed") else " (re-judged)" if im.get("rejudged") else "")
        L.append(f"| {im['name']} | {verdict} | {im.get('first_pass')} | {s} | "
                 f"{rounds or '-'} | {', '.join(im.get('risks') or []) or '-'} | {place_label(im.get('place'))} | {im.get('look') or '-'} | "
                 f"{(im.get('timing_s') or {}).get('total', '-')} |")
    rejected = [im for im in imgs if im.get("verdict") == "FAIL"]
    unjudged = [im for im in imgs if im.get("verdict") == "ERROR"]  # an image exists; only its judge failed
    no_image = [im for im in imgs if not im.get("path") and not im.get("verdict")]
    export_errors = [im for im in imgs if im.get("export_error")]

    def rerun(group, extra=""):
        return (f"`python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py batch --jobs \"{rep['jobs_file']}\" "
                f"--only {','.join(im['name'] for im in group)} --out-dir \"{rep.get('out_dir', '')}\"{extra}`")
    if rejected or unjudged or no_image or export_errors:
        L += ["", "## Next steps for failed images"]
    if rejected:
        L += ["", "### FAIL: the judge rejected the image. Make a new one.", "",
              "Failed images are not exported. Simplify each brief as the judge says (text-bearing objects, colour-"
              "matched sets and model limits are the usual causes), then rerun only those jobs. Export an image "
              "anyway only if you accept it (`export --src <name>.png`).", ""]
        for im in rejected:
            L.append(f"- **{im['name']}**: {'; '.join(im.get('defects') or []) or 'see meta'}"
                     + (f" Fix: {im['remaining_fix']}" if im.get("remaining_fix") else "")
                     + (f" Model limit: {im['model_limit']}." if im.get("model_limit") else ""))
        if rep.get("jobs_file"):
            L += ["", f"Rerun (new images): {rerun(rejected)}"]
    if unjudged:
        L += ["", "### ERROR: the judge failed, not the image. Judge it again.", "",
              "These images exist but were never judged, so they were not exported. No new image is needed.", ""]
        L += [f"- **{im['name']}**: not judged ({im.get('judge_error') or 'no verdict'})" for im in unjudged]
        if rep.get("jobs_file"):
            L += ["", f"Re-judge (no new image): {rerun(unjudged, ' --rejudge')} (add `--export-dir <dir>` to export "
                      f"the ones that pass)"]
    if no_image:
        L += ["", "### No image: the Codex session failed.", "",
              "Read each error (and its events log), fix the cause, then make these again.", ""]
        L += [f"- **{im['name']}**: {im.get('error') or 'no image produced'}" for im in no_image]
        if rep.get("jobs_file"):
            L += ["", f"Rerun: {rerun(no_image)}"]
    if export_errors:
        L += ["", "### Export failed (the image itself is fine).", ""]
        L += [f"- **{im['name']}**: {im['export_error']}. Export it again with `export --src \"{im['path']}\" --out "
              f"<dir>`." for im in export_errors]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- web + brand asset tools
# Everything a website needs around generation: responsive AVIF/WebP/JPEG exports with <picture> markup, favicons +
# web manifest, social (OG) cards with guaranteed text, alpha cleanup and flat-background cutouts, and an audit of an
# existing site's images. Pillow comes from the system or from the skill's own venv (`doctor --setup`).
SKILL_DIR = Path(__file__).resolve().parent.parent
VENV_DIR = SKILL_DIR / ".venv"
WEB_WIDTHS = [480, 768, 1024, 1440, 1920]
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg", ".ico", ".bmp", ".tif", ".tiff"}
CODE_EXT = {".html", ".htm", ".jsx", ".tsx", ".js", ".ts", ".vue", ".svelte", ".astro", ".css", ".scss", ".sass",
            ".less", ".md", ".mdx", ".php", ".liquid", ".njk", ".hbs", ".ejs", ".twig", ".erb"}
SKIP_DIRS = {"node_modules", ".git", ".next", "dist", "build", ".nuxt", ".output", ".svelte-kit", "vendor", ".venv",
             "venv", "__pycache__", ".cache", "coverage", ".turbo", ".vercel"}
FONT_CANDIDATES = {
    "bold": ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
             "C:/Windows/Fonts/arialbd.ttf"],
    "regular": ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/dejavu/DejaVuSans.ttf",
                "C:/Windows/Fonts/arial.ttf"]}


def need_pillow():
    """Pillow from the system, else from the skill's venv (created by `doctor --setup`)."""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        for sp in sorted(VENV_DIR.glob("lib/python*/site-packages")):
            if str(sp) not in sys.path:
                sys.path.append(str(sp))
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            die("this command needs Pillow; run once: python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py "
                "doctor --setup")
    from PIL import Image
    return Image


def alpha_clean(im, lo: int = 8, hi: int = 240):
    """Generated cutouts come back with subject alpha 250-254 (faint see-through, grey fringes): snap near-opaque
    to 255 and near-transparent to 0, keep the soft edge in between."""
    if im.mode != "RGBA":
        return im
    a = im.getchannel("A").point(lambda v: 0 if v <= lo else (255 if v >= hi else v))
    im = im.copy()
    im.putalpha(a)
    return im


def refine_alpha(p: Path):
    """Clean a generated transparent PNG in place (1 px choke removes the light matte rim, light blur keeps the
    anti-aliasing, then alpha_clean); the untouched original, with its C2PA manifest, stays as <name>-raw.png."""
    Image = need_pillow()
    from PIL import ImageFilter
    with Image.open(p) as im0:
        if im0.mode != "RGBA" or im0.getchannel("A").getextrema()[0] >= 250:
            return None
        im = im0.copy()
    raw = unique_path(p.with_name(f"{p.stem}-raw{p.suffix}"))
    shutil.copy2(p, raw)
    a = im.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    im.putalpha(a)
    alpha_clean(im).save(p, "PNG", optimize=True, **(provenance_kwargs(p) if ai_source(raw) else {}))
    return raw


def judge_view(p: Path) -> Path:
    """Transparent assets are judged composited on neutral grey, where light or dark fringes show up."""
    try:
        Image = need_pillow()
    except SystemExit:
        return p
    with Image.open(p) as im:
        if im.mode != "RGBA":
            return p
        bg = Image.new("RGBA", im.size, (128, 128, 128, 255))
        bg.alpha_composite(im.convert("RGBA"))
    out = Path(tmp_dir(prefix="judge-view-")) / f"{p.stem}-on-grey.png"
    bg.convert("RGB").save(out)
    return out


def _public_url(path: Path, url_prefix) -> str:
    if url_prefix is not None:
        return url_prefix.rstrip("/") + "/" + path.name
    parts = path.resolve().parts
    for anchor in ("public", "static", "www"):
        if anchor in parts:
            return "/" + "/".join(parts[parts.index(anchor) + 1:])
    return path.name


def web_export(src: Path, out_dir: Path, widths=None, formats=("avif", "webp", "jpg"), quality: int = 80,
               alt: str = "", name=None, url_prefix=None, sizes: str = "100vw", eager: bool = False) -> dict:
    """Responsive variants (never upscaled) + blur placeholder + dominant color + <picture> markup."""
    Image = need_pillow()
    from PIL import ImageOps
    import io
    with Image.open(src) as im0:  # closed right away: exports run in parallel over many files
        im = ImageOps.exif_transpose(im0)
        alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        im = alpha_clean(im.convert("RGBA")) if alpha else im.convert("RGB")
    tag = {"xmp": AI_SOURCE_XMP.encode("utf-8")} if ai_source(src) else {}  # only generated sources, never client photos
    W, H = im.size
    name = name or src.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    wl = widths or WEB_WIDTHS
    ws = sorted({w for w in wl if w < W} | {min(W, max(wl))})
    sized = {w: im if w == W else im.resize((w, round(H * w / W)), Image.Resampling.LANCZOS) for w in ws}

    def encode_width(w):  # one thread per width: an Image object is never saved from two threads at once
        h, r, out = round(H * w / W), sized[w], []
        for fmt in formats:
            ext = {"jpeg": "jpg"}.get(fmt.lower(), fmt.lower())
            if ext == "jpg" and alpha:
                ext = "png"
            p = out_dir / f"{name}-{w}.{ext}"
            if ext == "avif":
                r.save(p, "AVIF", quality=max(30, quality - 20), **tag)
            elif ext == "webp":
                r.save(p, "WEBP", quality=quality, method=6, **tag)
            elif ext == "jpg":
                r.convert("RGB").save(p, "JPEG", quality=quality, optimize=True, progressive=True, **tag)
            else:
                r.save(p, "PNG", optimize=True, **(provenance_kwargs(p) if tag else {}))
            out.append({"width": w, "height": h, "format": ext, "path": str(p), "url": _public_url(p, url_prefix),
                        "bytes": p.stat().st_size})
        return out
    # the encoders release the GIL; WebP with alpha at method 6 takes ~2 s per width, so widths run in parallel
    # (same settings and bytes as one after another; a transparent asset 8.3 s -> ~2.5 s)
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=max(1, len(ws))) as ex:
        variants = [v for vs in ex.map(encode_width, ws) for v in vs]
    tiny = im.convert("RGB").resize((16, max(1, round(16 * H / W))), Image.Resampling.BILINEAR)
    buf = io.BytesIO()
    tiny.save(buf, "WEBP", quality=40)
    blur = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    color = "#%02x%02x%02x" % im.convert("RGB").resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))[:3]

    def srcset(fmt):
        return ", ".join(f"{v['url']} {v['width']}w" for v in variants if v["format"] == fmt)
    fallback_fmt = "png" if alpha else ("jpg" if any(f in ("jpg", "jpeg") for f in formats) else variants[-1]["format"])
    fb = [v for v in variants if v["format"] == fallback_fmt] or variants
    default = next((v for v in fb if v["width"] >= min(1024, W)), fb[-1])
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    lines = ["<picture>"]
    for fmt, mime in (("avif", "image/avif"), ("webp", "image/webp")):
        if any(v["format"] == fmt for v in variants):
            lines.append(f'  <source type="{mime}" srcset="{srcset(fmt)}" sizes="{sizes}">')
    lines.append(f'  <img src="{default["url"]}" srcset="{srcset(fallback_fmt)}" sizes="{sizes}" width="{W}" '
                 f'height="{H}" alt="{alt.replace(chr(34), "&quot;")}" {load} decoding="async">')
    lines.append("</picture>")
    return {"name": name, "source": str(src), "width": W, "height": H, "alpha": alpha, "alt": alt,
            "variants": variants, "blurDataURL": blur, "dominantColor": color, "html": "\n".join(lines),
            "bytes_total": sum(v["bytes"] for v in variants)}


def portable_entry(e: dict, out_dir: Path) -> dict:
    """assets.json ships with the site: file paths relative to its folder (or bare names), URLs untouched."""
    base = str(Path(out_dir).resolve())

    def local(v):
        if not (isinstance(v, str) and os.path.isabs(v)):
            return v
        rp = str(Path(v).resolve())
        return os.path.relpath(rp, base) if rp.startswith(base + os.sep) else Path(v).name

    e = dict(e)
    for k in ("path", "source"):
        if k in e:
            e[k] = local(e[k])
    e["variants"] = [dict(v, path=local(v.get("path"))) if isinstance(v, dict) else v for v in e.get("variants") or []]
    if e.get("source"):
        e["source"] = Path(e["source"]).name
    return e


def update_manifest(out_dir: Path, entries: list) -> Path:
    mp = out_dir / "assets.json"
    data = json.loads(mp.read_text(encoding="utf-8")) if mp.exists() else {}
    for e in entries:
        data[e["name"]] = e
    data = {k: portable_entry(v, out_dir) if isinstance(v, dict) else v for k, v in data.items()}  # old entries too
    write_atomic(mp, json.dumps(data, indent=2, ensure_ascii=False))
    return mp


def rasterize_svg(svg: Path, size: int, out: Path) -> Path:
    """SVG -> PNG with whatever the machine has: rsvg-convert, cairosvg, or macOS Quick Look."""
    if shutil.which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(out), str(svg)], check=True)
        return out
    try:
        import cairosvg  # type: ignore
        cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=size, output_height=size)
        return out
    except ImportError:
        pass
    if shutil.which("qlmanage"):
        # Quick Look draws the SVG at its intrinsic width/height on a white canvas: enlarge the intrinsic size first,
        # then trim the canvas and turn the border-connected white back into transparency.
        tmp = Path(tmp_dir(prefix="svg-"))
        text = svg.read_text(encoding="utf-8")
        vb = re.search(r'viewBox\s*=\s*"\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', text)
        vw, vh = (float(vb.group(1)), float(vb.group(2))) if vb else (1.0, 1.0)
        tw, th = (size, round(size * vh / vw)) if vw >= vh else (round(size * vw / vh), size)
        tag = re.search(r"<svg\b[^>]*>", text).group(0)
        new_tag = re.sub(r'\s(width|height)\s*=\s*"[^"]*"', "", tag).replace("<svg", f'<svg width="{tw}" height="{th}"', 1)
        big = tmp / svg.name
        big.write_text(text.replace(tag, new_tag, 1), encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", str(tmp), str(big)], capture_output=True)
        got = next(tmp.glob("*.png"), None)
        if got:
            Image = need_pillow()
            from PIL import ImageChops
            im = Image.open(got).convert("RGB")
            bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
            if bbox:
                im.crop(bbox).save(got)
            cutout(got, out, tolerance=12, feather=0.6, key="#ffffff")
            return out
    die("cannot rasterize SVG here: install rsvg-convert (librsvg) or pass a PNG logo")
    return out


def make_favicons(src: Path, out_dir: Path, name: str = "", bg=None, theme: str = "#ffffff") -> dict:
    Image = need_pillow()
    out_dir.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".svg":
        shutil.copy2(src, out_dir / "favicon.svg")
        src = rasterize_svg(src, 1024, Path(tmp_dir(prefix="fav-")) / "logo.png")
    im = Image.open(src).convert("RGBA")
    side = max(im.size)
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    files = {}
    solid = bg or theme

    def fit(sz, pad=0.0, fill=None):
        canvas = Image.new("RGBA", (sz, sz), fill or (0, 0, 0, 0))
        inner = max(1, round(sz * (1 - 2 * pad)))
        canvas.alpha_composite(sq.resize((inner, inner), Image.Resampling.LANCZOS), ((sz - inner) // 2,
                                                                                    (sz - inner) // 2))
        return canvas
    for sz in (16, 32):
        p = out_dir / f"favicon-{sz}x{sz}.png"
        fit(sz).save(p)
        files[p.name] = str(p)
    fit(48).save(out_dir / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    fit(180, 0.1, solid).convert("RGB").save(out_dir / "apple-touch-icon.png")
    for sz in (192, 512):
        fit(sz).save(out_dir / f"android-chrome-{sz}x{sz}.png")
    fit(512, 0.12, solid).save(out_dir / "maskable-icon-512x512.png")
    for fn in ("favicon.ico", "apple-touch-icon.png", "android-chrome-192x192.png", "android-chrome-512x512.png",
               "maskable-icon-512x512.png"):
        files[fn] = str(out_dir / fn)
    manifest = {"name": name or "Website", "short_name": (name or "Website")[:12], "theme_color": theme,
                "background_color": solid, "display": "standalone",
                "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"},
                          {"src": "/maskable-icon-512x512.png", "sizes": "512x512", "type": "image/png",
                           "purpose": "maskable"}]}
    (out_dir / "site.webmanifest").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    files["site.webmanifest"] = str(out_dir / "site.webmanifest")
    html = "\n".join((['<link rel="icon" href="/favicon.svg" type="image/svg+xml">']
                      if (out_dir / "favicon.svg").exists() else []) + [
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="manifest" href="/site.webmanifest">',
        f'<meta name="theme-color" content="{theme}">'])
    return {"files": files, "html": html}


def _font(kind: str, size: int, path=None):
    from PIL import ImageFont
    for cand in ([path] if path else []) + FONT_CANDIDATES[kind]:
        if cand and Path(cand).exists():
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


def _wrap(draw, text: str, font, max_w: int) -> list:
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def make_og(bg: Path, title: str, out: Path, subtitle: str = "", logo=None, size=(1200, 630), font=None,
            font_regular=None, text_color: str = "#ffffff", accent=None) -> Path:
    """Social card: cover-cropped background + legibility gradient + exact title/subtitle + optional logo.
    Latin text only (no complex-script shaping); for Bangla or other scripts render the card as HTML instead."""
    Image = need_pillow()
    from PIL import ImageDraw, ImageOps
    W, H = size
    base = ImageOps.fit(Image.open(bg).convert("RGB"), (W, H), Image.Resampling.LANCZOS).convert("RGBA")
    grad = Image.new("L", (W, 1))
    for x in range(W):
        grad.putpixel((x, 0), int(215 * max(0.0, 1 - x / (W * 0.72))))
    shade = Image.new("RGBA", (W, H), (8, 12, 20, 255))
    shade.putalpha(grad.resize((W, H)))
    base.alpha_composite(shade)
    d = ImageDraw.Draw(base)
    pad, max_w, size_t = 72, int(W * 0.58), 76
    while True:
        ft = _font("bold", size_t, font)
        lines = _wrap(d, title, ft, max_w)
        if len(lines) <= 3 or size_t <= 40:
            break
        size_t -= 4
    fs = _font("regular", max(26, size_t // 2), font_regular)
    sub = _wrap(d, subtitle, fs, max_w) if subtitle else []
    lh_t, lh_s = int(size_t * 1.15), int(fs.size * 1.3) if hasattr(fs, "size") else 34
    block = len(lines) * lh_t + (18 + len(sub) * lh_s if sub else 0)
    y = (H - block) // 2 + (30 if logo else 0)
    if accent:
        d.rectangle([pad, y - 22, pad + 90, y - 14], fill=accent)
    for ln in lines:
        d.text((pad, y), ln, font=ft, fill=text_color)
        y += lh_t
    y += 18
    for ln in sub:
        d.text((pad, y), ln, font=fs, fill=text_color)
        y += lh_s
    if logo:
        lp = Path(logo)
        if lp.suffix.lower() == ".svg":
            lp = rasterize_svg(lp, 512, Path(tmp_dir(prefix="oglogo-")) / "logo.png")
        lg = Image.open(lp).convert("RGBA")
        lh = 64
        lg = lg.resize((max(1, round(lg.width * lh / lg.height)), lh), Image.Resampling.LANCZOS)
        base.alpha_composite(lg, (pad, pad - 16))
    out.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(out, "PNG" if out.suffix.lower() == ".png" else "JPEG", quality=90)
    return out


def cutout(src: Path, out: Path, tolerance: int = 40, feather: float = 1.2, key=None) -> dict:
    """Remove a flat studio/key background connected to the image border (interior areas of the same color, like
    white teeth on a white background, are kept). For new assets prefer generating with a transparent background."""
    Image = need_pillow()
    from PIL import ImageChops, ImageDraw, ImageFilter
    src_im = Image.open(src)
    if src_im.mode == "RGBA" and src_im.getchannel("A").getextrema()[0] < 250:
        out.parent.mkdir(parents=True, exist_ok=True)
        alpha_clean(src_im).save(out, "PNG", optimize=True)
        return {"out": str(out), "background": "native alpha (cleaned)", "transparent_share": None}
    im = src_im.convert("RGB")
    W, H = im.size
    if key:
        bgc = tuple(int(key.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    else:
        border = [im.getpixel((x, y)) for x in range(0, W, max(1, W // 64)) for y in (0, H - 1)] + \
                 [im.getpixel((x, y)) for y in range(0, H, max(1, H // 64)) for x in (0, W - 1)]
        bgc = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))
    diff = ImageChops.difference(im, Image.new("RGB", (W, H), bgc))
    r, g, b = diff.split()
    dist = ImageChops.lighter(ImageChops.lighter(r, g), b)
    bg_like = dist.point(lambda v: 255 if v <= tolerance else 0)
    seeds = [(x, y) for x in range(0, W, max(1, W // 16)) for y in (0, H - 1)] + \
            [(x, y) for y in range(0, H, max(1, H // 16)) for x in (0, W - 1)] + [(W - 1, H - 1)]
    for seed in seeds:
        if bg_like.getpixel(seed) == 255:
            ImageDraw.floodfill(bg_like, seed, 128)
    alpha = bg_like.point(lambda v: 0 if v == 128 else 255)
    if feather:
        alpha = alpha.filter(ImageFilter.GaussianBlur(feather))
    rgba = im.convert("RGBA")
    rgba.putalpha(alpha)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out, "PNG", optimize=True)
    hist = alpha.histogram()
    return {"out": str(out), "background": "#%02x%02x%02x" % bgc, "transparent_share": round(sum(hist[:8]) / (W * H),
                                                                                             3)}


LOCALE_TEXT_EXT = (CODE_EXT - {".css", ".scss", ".sass", ".less"}) | {".json", ".yml", ".yaml", ".toml", ".txt", ".xml",
                                                                   ".webmanifest"}  # stylesheets: font names only
SHORT_LINK_HOSTS = {"youtu.be", "lnkd.in", "dlvr.it", "spoti.fi", "redd.it", "ift.tt", "amzn.to", "wa.me", "t.me",
                    "bit.ly", "goo.gl", "fb.me", "instagr.am", "linktr.ee", "ow.ly", "buff.ly", "t.co", "g.co"}
SIGNAL_CAP = {"request": 12, "schema": 6, "locality": 4, "phone": 9, "postcode": 9, "domain": 6, "email": 4, "og": 3,
              "lang": 3, "currency": 4, "name": 6, "link": 2}
CA_AREA = {"204", "226", "236", "249", "250", "263", "289", "306", "343", "354", "365", "367", "368", "382", "403",
           "416", "418", "428", "431", "437", "438", "450", "468", "474", "506", "514", "519", "548", "579", "581",
           "584", "587", "604", "613", "639", "647", "672", "683", "705", "709", "742", "753", "778", "780", "782",
           "807", "819", "825", "867", "873", "879", "902", "905"}
POSTCODES = [(re.compile(r"(?<![#\w])[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}\b"), "GB", "UK postcode"),
             (re.compile(r"\b(A[KLRZ]|C[AOT]|D[CE]|FL|GA|HI|I[ADLN]|K[SY]|LA|M[ADEINOST]|N[CDEHJMVY]|O[HKR]|PA|RI|"
                         r"S[CD]|T[NX]|UT|V[AT]|W[AIVY]),? \d{5}(?:-\d{4})?\b"), "US", "US state + ZIP"),
             (re.compile(r"(?<![#\w])[ABCEGHJ-NPRSTVXY]\d[ABCEGHJ-NPRSTV-Z] \d[ABCEGHJ-NPRSTV-Z]\d\b"), "CA",
              "Canadian postcode"),
             (re.compile(r"\b(NSW|VIC|QLD|WA|SA|TAS|ACT|NT) \d{4}\b"), "AU", "Australian state + postcode")]


def _locale_files(root: Path, limit: int = 4000):
    n = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            low = fn.lower()
            if fn.startswith(".") or low.endswith((".lock", "-lock.json", "lock.yaml", ".min.js", ".map")):
                continue  # dotfiles (.env) can hold secrets; lock files and bundles are noise
            p = Path(dp) / fn
            if p.suffix.lower() not in LOCALE_TEXT_EXT and fn != "CNAME":
                continue
            try:
                if p.stat().st_size > 2_000_000:
                    continue
                yield p, p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            n += 1
            if n >= limit:
                return


def detect_locale(root=None, text=None) -> dict:
    """Where is this project's audience? Scores schema.org address, phone codes, postcodes, currency, the site's own
    domain and emails, <html lang>/og:locale and place names (capped per signal type). The requester's chat language,
    timezone or nationality are never signals. Weak or no evidence -> "global"."""
    L = locales()
    by_code = L.get("by_code", {})
    phone_map, cur_map, tld_map, lang_map = {}, {}, {}, {}
    for c in L.get("countries", []):
        for v in c.get("phone", []):
            phone_map.setdefault(v, []).append(c["code"])
        for v in c.get("currency", []):
            cur_map.setdefault(v, []).append(c["code"])
        for v in c.get("tld", []):
            tld_map[v] = c["code"]
        for v in c.get("lang", []):
            lang_map.setdefault(v, []).append(c["code"])
    cur_rx = [(t, codes, re.compile((r"(?<![A-Za-z])" if t[0].isalpha() else "") + re.escape(t) + r"\.?\s?\d|\d\s?"
                                    + re.escape(t) + (r"(?![A-Za-z])" if t[-1].isalpha() else "")))
              for t, codes in cur_map.items()]
    raw, signals, cities, multi, seen = {}, {}, {}, set(), set()

    def add(codes, w, kind, why):
        codes = [c for c in codes if c in by_code]
        if not codes:
            return
        for c in codes:
            raw[(c, kind)] = raw.get((c, kind), 0) + w / len(codes)
        sig = signals.setdefault((why, tuple(codes)), {"signal": why, "countries": codes, "kind": kind, "count": 0})
        sig["count"] += 1

    def city(code, name, w=1, kind="cities"):
        cities.setdefault((code, kind), {})
        cities[(code, kind)][name] = cities[(code, kind)].get(name, 0) + w

    def host(h, w, kind, why):
        h = (h or "").lower().strip(".")
        if not h or h in SHORT_LINK_HOSTS or (kind, h) in seen:
            return
        seen.add((kind, h))
        tld = h.rsplit(".", 1)[-1]
        if tld in tld_map:
            add([tld_map[tld]], w, kind, f"{why} {h}")

    def scan(t, request=False):
        for tag in re.findall(r"<html\b[^>]*>", t, re.I):
            lm = re.search(r"\blang\s*=\s*[\"']([A-Za-z]{2,3})(?:[-_]([A-Za-z]{2}))?", tag)
            if lm and lm.group(2):
                add([lm.group(2).upper()], 3, "lang", f"html lang {lm.group(1)}-{lm.group(2).upper()}")
            elif lm and lm.group(1).lower() in lang_map:
                add(lang_map[lm.group(1).lower()], 1, "lang", f"html lang {lm.group(1)}")
        for a, b in re.findall(r"og:locale[\"'][^>]{0,80}?content\s*=\s*[\"']([a-z]{2,3})[_-]([A-Za-z]{2})", t, re.I) + \
                re.findall(r"content\s*=\s*[\"']([a-z]{2,3})[_-]([A-Za-z]{2})[\"'][^>]{0,80}?og:locale\b", t, re.I):
            add([b.upper()], 3, "og", f"og:locale {a}_{b.upper()}")
        for a, b in re.findall(r"hreflang\s*=\s*[\"']([a-z]{2,3})[-_]([A-Za-z]{2})[\"']", t, re.I):
            multi.add(f"{a.lower()}-{b.upper()}")
        for block in re.findall(r"\blocales\s*:\s*\[([^\]]{0,400})\]", t):
            for a, b in re.findall(r"[\"']([a-z]{2,3})[-_]([A-Za-z]{2})[\"']", block):
                multi.add(f"{a.lower()}-{b.upper()}")
        for v in re.findall(r"[\"']addressCountry[\"']\s*:\s*[\"']([^\"']{2,40})[\"']", t):
            code = v.upper() if v.upper() in by_code else next(
                (p["code"] for p in find_places(v, require_cap=False) if p["code"] and p["kind"] == "aliases"), None)
            if code:
                add([code], 5, "schema", f"schema.org addressCountry {v}")
        for v in re.findall(r"[\"']addressLocality[\"']\s*:\s*[\"']([^\"']{2,60})[\"']", t):
            for p in find_places(v, require_cap=False):
                if p["code"] and p["kind"] in ("cities", "regions"):
                    add([p["code"]], 2, "locality", f"schema.org addressLocality {v}")
                    city(p["code"], p["name"], 2, p["kind"])
        for num in re.findall(r"\+\s?\(?(\d[\d\s().-]{6,18}\d)", t):
            digits = re.sub(r"\D", "", num)
            if not 8 <= len(digits) <= 15 or ("phone", digits) in seen:
                continue
            seen.add(("phone", digits))
            if digits[0] == "1":
                codes = ["CA"] if digits[1:4] in CA_AREA else ["JM"] if digits[1:4] in ("876", "658") else ["US"]
            else:
                codes = next((phone_map[digits[:k]] for k in (3, 2) if digits[:k] in phone_map), None) or \
                    phone_map.get(digits[:1])
            if codes:
                add(codes, 3, "phone", f"phone +{digits[:3]}...")
        for tok, codes, rx in cur_rx:
            n = len(rx.findall(t))
            if n:
                add(codes, min(n, 4), "currency", f"currency {tok} x{n}")
        for pat in (r"rel\s*=\s*[\"']canonical[\"'][^>]*href\s*=\s*[\"']https?://([^/\"'>\s:]+)",
                    r"href\s*=\s*[\"']https?://([^/\"'>\s:]+)[^>]*rel\s*=\s*[\"']canonical",
                    r"og:url[\"'][^>]*content\s*=\s*[\"']https?://([^/\"'>\s:]+)",
                    r"\b(?:metadataBase|siteUrl|site_url|homepage|baseURL|baseUrl|site)\b[\"']?\s*[:=]\s*"
                    r"(?:new URL\()?[\"']https?://([^/\"'>\s:]+)"):
            for h in re.findall(pat, t, re.I):
                host(h, 4, "domain", "site domain")
        for h in re.findall(r"[\w.+-]+@([a-z0-9-]+(?:\.[a-z0-9-]+)+)", t, re.I):
            host(h, 2, "email", "email domain")
        for h in re.findall(r"https?://([a-z0-9-]+(?:\.[a-z0-9-]+)+)", t, re.I):
            host(h, 0.5, "link", "link")
        for rx, code, why in POSTCODES:
            n = len(rx.findall(t))
            if n:
                add([code], 3 * min(n, 3), "postcode", f"{why} x{n}")
        for p in find_places(t):
            if not p["code"] or p["kind"] == "marker":
                continue
            w = 4 if request else (1.5 if p["kind"] in ("cities", "regions") else 1)
            add([p["code"]], w, "request" if request else "name", f"{'request' if request else 'text'}: {p['name']}")
            if p["kind"] in ("cities", "regions"):
                city(p["code"], p["name"], 3 if request else 1, p["kind"])

    if root is not None:
        for p, t in _locale_files(Path(root)):
            if p.name == "CNAME":
                host(t.strip().split()[0] if t.strip() else "", 4, "domain", "CNAME")
            else:
                scan(t)
    if text:
        scan(text, request=True)
    score = {}
    for (c, kind), v in raw.items():
        score[c] = score.get(c, 0) + min(v, SIGNAL_CAP.get(kind, 4))
    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    total = sum(score.values()) or 1
    rep = {"suggested": "global", "country": None, "confidence": 0.0, "ambiguous": False,
           "candidates": [{"code": c, "country": by_code[c]["name"], "score": round(v, 1)} for c, v in ranked[:5]],
           "multi_locale": sorted(multi),
           "signals": sorted(signals.values(), key=lambda g: -g["count"])[:30]}
    if ranked and ranked[0][1] >= 3:
        code, top = ranked[0]
        c = by_code[code]
        best = [max(cities.get((code, k), {}).items(), key=lambda kv: kv[1], default=(None, 0))[0]
                for k in ("cities", "regions")]
        rep.update(suggested=", ".join(x for x in best + [c["name"]] if x), country=code,
                   confidence=round(top / total, 2), ambiguous=len(ranked) > 1 and ranked[1][1] >= 0.7 * top,
                   facts={"traffic": f"keeps to the {c['drive']}", "signage": c["script"],
                          **({"seasons": "southern hemisphere"} if c.get("south") else {})})
    if len(multi) > 1:
        rep["note"] = ("several markets (hreflang/i18n): a global cast for shared images, and a Locale per market "
                       "page where pages differ")
    elif rep["suggested"] == "global":
        rep["note"] = "no reliable place signal: keep the images internationally neutral (Locale: global)"
    elif rep["ambiguous"]:
        rep["note"] = "two places score close: confirm with the client, or keep shared images global"
    else:
        rep["note"] = f'put "locale": "{rep["suggested"]}" in the style lock or jobs file'
    return rep


def audit_site(root: Path) -> dict:
    """Inventory every image and image reference in a web project and flag the usual problems."""
    Image = None
    try:
        Image = need_pillow()
    except SystemExit:
        pass
    images, refs = {}, []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in fns:
            p = Path(dp) / fn
            ext = p.suffix.lower()
            if ext in IMG_EXT and is_generated_file(p):
                continue  # generated masters, candidates and re-run attempts, not site images
            if ext in IMG_EXT:
                info = {"path": str(p.relative_to(root)), "format": ext.lstrip("."), "bytes": p.stat().st_size}
                if Image and ext not in (".svg", ".ico"):
                    try:
                        with Image.open(p) as im:
                            info.update(width=im.width, height=im.height, mode=im.mode)
                    except Exception:
                        info["unreadable"] = True
                images[p.name] = info
            elif ext in CODE_EXT and p.stat().st_size < 2_000_000:
                text = p.read_text(encoding="utf-8", errors="ignore")
                for m in re.finditer(r"<(img|Image)\b[^>]*>", text, re.I | re.S):
                    tag = m.group(0)
                    src = re.search(r"""\bsrc\s*=\s*[{"']*([^"'}\s>]+)""", tag)
                    altm = re.search(r"""\balt\s*=\s*[{"']*([^"'}]*)""", tag)
                    refs.append({"file": str(p.relative_to(root)), "line": text.count("\n", 0, m.start()) + 1,
                                 "tag": m.group(1), "src": src.group(1) if src else None,
                                 "alt": altm.group(1) if altm else None, "has_alt": bool(altm),
                                 "has_size": bool(re.search(r"\bwidth\s*=", tag) and re.search(r"\bheight\s*=", tag))
                                 or (m.group(1) == "Image" and "fill" in tag),
                                 "lazy": "loading" in tag or m.group(1) == "Image"})
                for m in re.finditer(r"""\bsrcset\s*=\s*["']([^"']+)["']""", text, re.I):
                    for part in m.group(1).split(","):
                        u = part.strip().split(" ")[0]
                        if u:
                            refs.append({"file": str(p.relative_to(root)), "line": text.count("\n", 0, m.start()) + 1,
                                         "tag": "srcset", "src": u, "has_alt": None, "has_size": None, "lazy": None})
                for m in re.finditer(r"url\(\s*['\"]?([^)'\"]+\.(?:png|jpe?g|webp|avif|gif|svg))", text, re.I):
                    refs.append({"file": str(p.relative_to(root)), "line": text.count("\n", 0, m.start()) + 1,
                                 "tag": "css-url", "src": m.group(1), "has_alt": None, "has_size": None, "lazy": None})
    issues = []
    referenced = {Path(r["src"]).name for r in refs if r.get("src")}
    for name, info in images.items():
        fmt, b = info["format"], info["bytes"]
        if fmt in ("png", "jpg", "jpeg") and b > 300_000:
            issues.append(("heavy", info["path"], f"{b // 1024} KB {fmt}; export AVIF/WebP variants"))
        if info.get("width", 0) > 2560:
            issues.append(("oversized", info["path"], f"{info['width']}px wide; serve responsive widths"))
        if re.search(r"(shutterstock|istock|gettyimages|dreamstime|depositphotos|adobestock|placeholder|lorem|"
                      r"dummy|sample|stock)", name, re.I):
            issues.append(("stock/placeholder", info["path"], "looks like a stock or placeholder image"))
        if name not in referenced and fmt != "ico" and not name.startswith(("favicon", "apple-touch", "android-chrome",
                                                                            "maskable")):
            issues.append(("unreferenced", info["path"], "not referenced in code (may be dynamic)"))
    for r in refs:
        loc = f"{r['file']}:{r['line']}"
        if r["tag"] not in ("css-url", "srcset"):
            if not r["has_alt"]:
                issues.append(("missing-alt", loc, r.get("src") or "?"))
            if not r["has_size"]:
                issues.append(("no-dimensions", loc, "add width/height to prevent layout shift"))
        src = r.get("src") or ""
        if re.search(r"(via\.placeholder|placehold|picsum|unsplash\.it|dummyimage|lorempixel)", src, re.I):
            issues.append(("placeholder-url", loc, src))
        elif src and not src.startswith(("http", "data:", "{", "$", "/_next", "@")) and "${" not in src \
                and Path(src).name not in images:
            issues.append(("broken-ref?", loc, src))
    counts = {}
    for k, _, _ in issues:
        counts[k] = counts.get(k, 0) + 1
    loc = detect_locale(root)
    return {"root": str(root), "images": len(images), "references": len(refs), "issue_counts": counts,
            "locale": {k: loc.get(k) for k in ("suggested", "country", "confidence", "ambiguous", "multi_locale",
                                               "note")},
            "issues": [{"type": k, "where": w, "detail": d} for k, w, d in issues],
            "inventory": sorted(images.values(), key=lambda i: -i["bytes"])[:200], "refs": refs[:500]}


STYLE_FILE = re.compile(r"[^\n]*\.(json|txt|md|ya?ml)", re.I)  # a style value that names a file, not a style


def style_block(style, bases=()) -> str:
    """Shared style lock (brand DNA) appended to every brief of a set so all images match. A string is a file when
    one exists (relative paths are looked up in `bases`, then the current folder), else the style text itself; a
    value that looks like a file name but is not found stops the run instead of becoming the style text."""
    if not style:
        return ""
    if isinstance(style, str):
        p = find_input(style.strip(), bases) if len(style) < 400 and "\n" not in style else None
        if p is not None and p.is_file():
            style = p.read_text(encoding="utf-8")
            try:
                style = json.loads(style)
            except ValueError:
                pass
        elif STYLE_FILE.fullmatch(style.strip()):
            die(f"style file not found: {style.strip()} (relative paths are looked up next to the jobs file, in "
                f"--workdir and in the current folder)")
    if isinstance(style, dict):
        label = {"palette": "palette (for graphics; in photos only one small object in these colours)"}
        style = "\n".join(f"- {label.get(k, k.replace('_', ' '))}: "
                          f"{', '.join(map(str, v)) if isinstance(v, list) else v}" for k, v in style.items() if v)
    return ("Style lock (identical across every image of this project; keep it exactly; in photographs brand colours "
            "appear only as small natural accents, never as a colour-matched set):\n" + str(style).strip())


class ImageBudget:
    """Caps the number of image generations of one run (candidates + fixes); thread-safe."""

    def __init__(self, limit=None):
        self.limit, self.used, self.lock = limit, 0, threading.Lock()

    def take(self, n: int) -> int:
        with self.lock:
            if self.limit is None:
                self.used += n
                return n
            n = max(0, min(n, self.limit - self.used))
            self.used += n
            return n


BUDGET = ImageBudget()


# ----------------------------------------------------------------------------- commands
def cmd_judge(args) -> None:
    """Judge existing images against one brief, all at once. Every path is checked before any judge starts, and
    every result is printed, also when one judge fails."""
    brief = read_brief(args)
    imgs = [Path(i).expanduser().resolve() for i in args.image]
    missing = [str(p) for p in imgs if not p.is_file()]
    if missing:
        die("image not found: " + ", ".join(missing))
    TELEMETRY["fail_dir"] = str(Path.cwd() / "output" / "imagegen" / "logs")  # a failed judge's events are kept here
    log(f"judging {len(imgs)} image(s) at once")
    res = judge_parallel([(str(i), str(p), brief, None) for i, p in enumerate(imgs)],
                         argparse.Namespace(threshold=args.threshold, judge_model=args.judge_model,
                                            judge_effort=args.judge_effort, judge_timeout=args.timeout,
                                            judge_workers=len(imgs)))
    out = [{"image": str(p), **(res.get(str(i)) or {"computed_verdict": "ERROR", "error": "no verdict"})}
           for i, p in enumerate(imgs)]
    print(json.dumps(out if len(out) > 1 else out[0], indent=2, ensure_ascii=False))
    if _LIVE["fatal"]:
        raise SystemExit(3)


def cmd_compare(args) -> None:
    """Same brief on several API models (no fallback), each judged independently."""
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else Path.cwd().resolve()
    brief = read_brief(args)
    for w in lint_brief(brief, args.aspect):
        log(f"lint: {w}")
    if not args.dry_run and not get_api_key():
        die("compare uses the API engine and needs OPENAI_API_KEY. On macOS store it once in your own terminal with: "
            "security add-generic-password -a \"$USER\" -s OPENAI_API_KEY -w")
    out_dir = Path(args.out_dir).expanduser() if args.out_dir else workdir / "output" / "imagegen" / "compare"
    out_dir = out_dir if out_dir.is_absolute() else workdir / out_dir
    name = args.name or slugify(brief)
    rows = []
    for m in [x.strip() for x in args.models.split(",") if x.strip()]:
        res = engine_api(args, brief, [unique_path(out_dir / f"{name}-{m}.png")], [], None, workdir, only_model=m)
        if res is None:
            continue
        p = res["paths"][0]
        u = res.get("usage") or {}
        det = u.get("input_tokens_details") or {}
        cost = (u.get("output_tokens", 0) * 30 + det.get("text_tokens", 0) * 5 + det.get("image_tokens", 0) * 8) / 1e6
        row = {"model": m, "path": str(p), "seconds": round(res["elapsed"], 1), "quality": res["quality"],
               "size": res["size"], "usage": u, "est_cost_usd": round(cost, 4), **png_info(p)}
        if not args.no_judge:
            row["judge"] = run_judge(p, brief, args.threshold, args.judge_model, args.judge_effort)
        rows.append(row)
    if rows:
        best = max(rows, key=lambda r: judge_rank(r.get("judge")))
        print(json.dumps({"brief": brief, "results": rows, "best": best["model"]}, indent=2, ensure_ascii=False))


def export_many(calls: list, keep_going: bool = False) -> list:
    """web_export(*a, **kw) for every (a, kw) in calls, in parallel, results in call order (Pillow's encoders
    release the GIL; 3 photos + 1 transparent asset: 10.6 s -> 3.1 s, byte-identical files). Files with the same
    export name run one after another, as before, so two exports never write the same file at once. With
    keep_going, an image that fails gives {"error": ...} and the others are still exported."""
    import concurrent.futures as cf

    def one(c):
        try:
            return web_export(*c[0], **c[1])
        except Exception as e:
            if not keep_going:
                raise
            return {"error": f"{type(e).__name__}: {e}"}
    names = [kw.get("name") or Path(a[0]).stem for a, kw in calls]
    workers = min(len(calls), os.cpu_count() or 4, 8)
    if workers < 2 or len(set(names)) != len(names):
        return [one(c) for c in calls]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(one, calls))


def export_results(rep: dict, jobs: list, export_dir: Path, args) -> list:
    """Web-export every usable final image (PASS / PASS_WITH_NOTES, or all with --export-all). An image that fails
    to export gets "export_error" in its row; the others are exported."""
    by_name = {j["name"]: j for j in jobs}
    todo, calls = [], []
    for im in rep["images"]:
        if not im.get("path") or (im.get("verdict") not in VERDICT_LEVEL and not getattr(args, "export_all", False)):
            continue
        j = by_name.get(im["name"], {})
        todo.append(im)
        calls.append(((Path(im["path"]), export_dir), dict(
            widths=j.get("widths"), alt=j.get("alt", ""), name=j.get("export_name") or im["name"],
            sizes=j.get("sizes", "100vw"), eager=bool(j.get("eager")), url_prefix=getattr(args, "url_prefix", None))))
    entries = []
    for im, e in zip(todo, export_many(calls, keep_going=True)):
        if e.get("error"):
            im["export_error"] = e["error"]
            log(f"{im['name']}: export failed ({e['error']}); the image itself is kept")
            continue
        im["export"] = {"html": e["html"], "variants": len(e["variants"]), "bytes_total": e["bytes_total"]}
        entries.append(e)
    if entries:
        rep["assets_manifest"] = str(update_manifest(export_dir, entries))
        log(f"exported {len(entries)} image(s) to {export_dir} (assets.json has srcset/<picture> markup)")
    return entries


def fast_args(args):
    """Normalize flags for the fast pipeline (judge on unless --no-judge; one fix round unless given)."""
    args.judge = not getattr(args, "no_judge", False)
    if getattr(args, "timeout", None) is None:
        args.timeout = GEN_TIMEOUT
    STRICT["on"] = bool(getattr(args, "strict", False))
    if getattr(args, "fix_rounds", None) is None:
        args.fix_rounds = 1
    if getattr(args, "judge_effort", None) is None:
        args.judge_effort = "medium"
    BUDGET.limit = getattr(args, "max_images", None)
    return args


def write_fast_outputs(rep: dict, out_dir: Path, print_summary: bool = True) -> None:
    rep["created"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    recs = TELEMETRY["records"]
    rep["telemetry"] = telemetry_summary(recs)
    if TELEMETRY.get("log_dir"):
        rep["log_dir"] = TELEMETRY["log_dir"]
        log_file("telemetry.json", {"totals": rep["telemetry"], "records": recs})
        lines = []
        for r in recs:
            dg = r.get("digest") or {}
            lines.append(f"=== {r['step']}  wall {r['wall_s']}s  model {dg.get('codex_model')} "
                         f"effort {dg.get('reasoning_effort')}  thread {r.get('thread_id')}")
            lines += dg.get("timeline") or []
            lines += [f"  thinking: {x}" for x in dg.get("reasoning_summaries") or []]
        log_file("run.log", "\n".join(lines) + "\n")
    if print_summary:
        print(json.dumps(rep, indent=2, ensure_ascii=False, default=str))


def finish_batch_report(rep: dict, jobs: list, args, out_dir: Path) -> None:
    """Write batch-report.json and batch-report.md with whatever the run finished, also when it was cut short (a
    stop, a crash): jobs that never ended are listed as unfinished."""
    images = rep.setdefault("images", [])
    done = {i["name"] for i in images}
    unfinished = [j["name"] for j in jobs if j["name"] not in done]
    if unfinished:
        rep["unfinished"] = unfinished
    rep.setdefault("timing", {"total_s": None, "slowest_job_s": None, "median_job_s": None})
    rep["passed"] = sum(1 for i in images if i.get("verdict") in VERDICT_LEVEL)
    rep["first_pass"] = sum(1 for i in images if i.get("first_pass") in VERDICT_LEVEL)
    if _LIVE["fatal"]:
        rep["stopped"] = _LIVE["fatal"]
    try:
        rep["codex_version"] = codex_version(codex_bin())
    except SystemExit:
        rep["codex_version"] = "not found"
    rep["jobs_file"], rep["out_dir"] = str(Path(args.jobs).expanduser().resolve()), str(out_dir)
    write_fast_outputs(rep, out_dir, print_summary=False)
    write_atomic(out_dir / "batch-report.json", json.dumps(rep, indent=2, ensure_ascii=False, default=str))
    write_atomic(out_dir / "batch-report.md", fast_report_md(rep))


def print_batch_summary(rep: dict, out_dir: Path) -> None:
    """The short stdout of a batch: where the report is, the timing, and one [file, verdict] pair per job."""
    extra = {k: rep[k] for k in ("stopped", "unfinished") if rep.get(k)}
    errs = [i["name"] for i in rep["images"] if i.get("export_error")]
    if errs:
        extra["export_errors"] = errs
    print(json.dumps({"out_dir": str(out_dir), "report": str(out_dir / "batch-report.md"), "timing": rep["timing"],
                      "passed": rep["passed"], "first_pass": rep["first_pass"],
                      "images": [(Path(i["path"]).name if i.get("path") else None, i.get("verdict"))
                                 for i in rep["images"]], **extra}, indent=2, ensure_ascii=False))


def cmd_generate_fast(args, workdir: Path, brief: str, refs, target) -> None:
    fast_args(args)
    if args.out:
        base = Path(args.out).expanduser()
        base = base if base.is_absolute() else workdir / base
        out_dir, name = base.parent, base.stem
    else:
        out_dir = Path(args.out_dir).expanduser() if args.out_dir else workdir / "output" / "imagegen"
        out_dir = out_dir if out_dir.is_absolute() else workdir / out_dir
        name = check_name(args.name) if args.name else slugify(brief)
    if args.log_dir and not args.dry_run:
        ld = Path(args.log_dir).expanduser()
        TELEMETRY["log_dir"] = str(ld if ld.is_absolute() else workdir / ld)
    if not args.dry_run:
        TELEMETRY["fail_dir"] = str(out_dir / "logs")  # a failed session's events are kept here
    jobs = []
    for i in range(args.n):
        b = brief if not args.explore or args.n == 1 else \
            f"{brief}\nVariant direction: {EXPLORE_DIRECTIONS[i % len(EXPLORE_DIRECTIONS)]}."
        if getattr(args, "style", None):
            b = f"{b}\n{style_block(args.style, [Path.cwd(), workdir])}"
        jobs.append({"name": name if args.n == 1 else f"{name}-{i + 1}", "brief": b, "aspect": args.aspect,
                     "size": args.size, "refs": [str(r) for r, _ in refs], "target": str(target) if target else None,
                     "transparent": getattr(args, "transparent", False), "alt": getattr(args, "alt", "") or "",
                     "finish": getattr(args, "finish", None),
                     "eager": getattr(args, "eager", False)})
    if args.dry_run:
        for j in jobs:
            j["prompt"], j["hints"] = compile_prompt(j["brief"], j.get("aspect"))
            j["lint"] = lint_brief(j["brief"], j.get("aspect"))
        print(json.dumps({"mode": "fast", "out_dir": str(out_dir), "jobs": jobs}, indent=2, ensure_ascii=False))
        return
    for j in jobs:
        for w in lint_brief(j["brief"], j.get("aspect")):
            log(f"lint ({j['name']}): {w}")
    rep = fast_pipeline(jobs, args, workdir, out_dir)
    if getattr(args, "export_dir", None):
        ed = Path(args.export_dir).expanduser()
        export_results(rep, jobs, ed if ed.is_absolute() else workdir / ed, args)
    write_fast_outputs(rep, out_dir)
    if _LIVE["fatal"]:
        raise SystemExit(3)
    if not any(i.get("path") for i in rep["images"]):
        raise SystemExit(2)


def edit_target(args, bases):
    """The `edit --image` file (None for generate); a missing file stops the run before any Codex session."""
    if args.cmd != "edit":
        return None
    p = find_input(args.image, bases)
    if p is None or not p.is_file():
        die(f"edit target not found: {Path(args.image).expanduser()}")
    return p


def cmd_generate_or_edit(args) -> None:
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else Path.cwd().resolve()
    brief = with_look(with_locale(read_brief(args), getattr(args, "locale", None)), getattr(args, "look", None))
    if args.timeout is None:
        args.timeout = GEN_TIMEOUT if args.mode == "fast" and args.engine != "api" else AGENT_TIMEOUT
    if args.size:  # checked before any Codex session
        check_size(args.size, "--size")
    check_candidates(getattr(args, "candidates", None), "--candidates")
    bases = [Path.cwd(), workdir]  # relative input paths: the current folder first, then --workdir
    if args.mode == "fast" and args.engine != "api":
        refs = parse_refs(args.ref, bases)
        target = edit_target(args, bases)
        if len(refs) + (1 if target else 0) > 5:
            die("Codex's image tool accepts at most 5 input images (edit target + references)")
        return cmd_generate_fast(args, workdir, brief, refs, target)
    if args.fix_rounds is None:
        args.fix_rounds = 2
    if args.judge_effort is None:
        args.judge_effort = "high"
    if getattr(args, "style", None):
        brief = f"{brief}\n{style_block(args.style, bases)}"
    if getattr(args, "transparent", False) and not re.search(r"transparent background", brief, re.I):
        brief += ("\nOutput: fully transparent background (PNG alpha); the subject isolated with clean edges; no "
                  "backdrop, floor, frame or shadow plane.")
    refs = parse_refs(args.ref, bases)
    target = edit_target(args, bases)
    if len(refs) + (1 if target else 0) > 5 and args.engine != "api":
        die("Codex's image tool accepts at most 5 input images (edit target + references)")
    outputs = plan_outputs(args, brief, workdir)
    lint = lint_brief(brief, args.aspect)
    for w in lint:
        log(f"lint: {w}")
    if getattr(args, "log_dir", None) and not args.dry_run:
        ld = Path(args.log_dir).expanduser()
        TELEMETRY["log_dir"] = str(ld if ld.is_absolute() else workdir / ld)
        log_file("brief.txt", brief)
        log_file("lint.json", lint)
        log_file("args.json", {k: v for k, v in vars(args).items() if k not in ("prompt", "func")})
    if not args.dry_run:
        TELEMETRY["fail_dir"] = str(outputs[0].parent / "logs")  # a failed session's events are kept here
    set_phase("initial")
    engine = args.engine
    if engine == "auto":
        engine = "api" if (args.model or "").startswith("gpt-image-2.5") and get_api_key() else "codex"
    if engine == "codex" and args.model and args.model not in ("auto", "codex"):
        log(f"NOTE: the codex engine cannot select {args.model}; Codex chooses the image model server-side. "
            "Use --engine api for explicit model routing.")
    if engine == "codex" and args.mask:
        log("NOTE: Codex's built-in tool has no mask input; the mask is ignored (use --engine api for masks)")
    t0 = time.time()
    summary = {"engine": engine, "brief": brief, "lint": lint, "images": []}
    if engine == "codex":
        # the art director gets the same place, capture and realism layers as fast mode; the judge keeps the brief
        run = engine_codex(args, compile_prompt(brief, args.aspect, edit=target is not None)[0], outputs, refs,
                           target, workdir)
        if run is None:
            return
        found, missing = collect_codex_outputs(outputs, run, workdir)
        summary.update({"codex_version": run["codex_version"], "codex_model": run["codex_model"],
                        "reasoning_effort": run["effort"], "thread_id": run["res"].get("thread_id"),
                        "codex_error": None if run["res"].get("ok") else run["res"].get("error"),
                        "notes": run["report"].get("notes", ""),
                        "missing": [str(m) for m in missing]})
        items = [(p, {"final_prompt": e.get("final_prompt", ""), "attempts": e.get("attempts"), "qa": e.get("qa"),
                      "source_path": e.get("source_path"),
                      "image_model": "codex built-in image_gen (client requests gpt-image-2; server may route newer)"})
                 for p, e in found]
    else:
        res = engine_api(args, brief, outputs, refs, target, workdir)
        if res is None:
            return
        summary.update({"usage": res["usage"]})
        items = [(p, {"final_prompt": res["prompt"], "attempts": 1, "qa": None, "source_path": None,
                      "image_model": res["model"], "quality": res["quality"], "api_size": res["size"]})
                 for p in res["paths"]]
    if (args.judge or args.auto_fix) and not args.dry_run:
        items = judge_and_fix(args, brief, items, workdir, engine, refs, target)
    body = place_context(brief)[0]
    look = pick_look(body)[0] if not is_non_photo(brief) else "-"
    fin = with_finish_default({"look": look, "finish": getattr(args, "finish", None),
                               "transparent": getattr(args, "transparent", False),
                               "target": str(target) if target else None})
    for p, meta in items:
        raw = None
        if args.size and not meta.get("sized"):
            w, h = parse_size(args.size)
            raw = fit_to_size(p, w, h)
        if getattr(args, "transparent", False) and not args.dry_run:
            try:
                refine_alpha(p)
            except BaseException as e:  # keep the generated file
                log(f"transparent edge refine skipped ({e!r})")
        if fin != "none" and not args.dry_run:
            try:
                meta["finish"] = finish_image(p, fin, warm_scene=bool(WARM_LIGHT.search(own_positive(body))))
            except SystemExit:
                meta["finish"] = {"error": "Pillow missing (run doctor --setup)"}
            except Exception as e:  # never lose the image over its finish
                meta["finish"] = {"error": repr(e)}
        info = png_info(p)
        record = {"created": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "engine": engine,
                  "brief": brief, "output_path": str(p), "raw_copy": str(raw) if raw else None, **meta, **info,
                  "telemetry": TELEMETRY["records"]}
        if engine == "codex":
            record.update({"codex_version": summary.get("codex_version"), "codex_model": summary.get("codex_model"),
                           "reasoning_effort": summary.get("reasoning_effort"), "thread_id": summary.get("thread_id")})
        meta_path = p.with_name(f"{p.stem}.meta.json")
        write_atomic(meta_path, json.dumps(record, indent=2, ensure_ascii=False))
        summary["images"].append({"path": str(p), "width": info.get("width"), "height": info.get("height"),
                                  "qa": meta.get("qa"), "image_model": meta.get("image_model"),
                                  "judge_verdict": (meta.get("judge") or {}).get("computed_verdict"),
                                  "judge_scores": (meta.get("judge") or {}).get("scores"),
                                  "judge_fix": (meta.get("judge") or {}).get("fix_instruction"),
                                  "judge_rounds": [{"path": Path(r["path"]).name, "mode": r["mode"],
                                                    "verdict": r["verdict"], "score_total": r["score_total"]}
                                                   for r in meta.get("rounds", [])],
                                  "rejected_candidates": meta.get("rejected", []), "meta": str(meta_path)})
    summary["elapsed_s"] = round(time.time() - t0, 1)
    recs = TELEMETRY["records"]
    summary["telemetry"] = {"totals": telemetry_summary(recs), "steps": [
        {"step": r["step"], "wall_s": r["wall_s"], "ok": r.get("ok", True),
         "codex_model": (r.get("digest") or {}).get("codex_model"),
         "effort": (r.get("digest") or {}).get("reasoning_effort"),
         "image_gen_s": [c.get("duration_s") for c in (r.get("digest") or {}).get("image_gen_calls") or []],
         "tokens": (r.get("digest") or {}).get("tokens"),
         "reasoning_summaries": len((r.get("digest") or {}).get("reasoning_summaries") or [])} for r in recs]}
    if TELEMETRY.get("log_dir"):
        summary["log_dir"] = TELEMETRY["log_dir"]
        log_file("telemetry.json", {"totals": summary["telemetry"]["totals"], "records": recs})
        lines = []
        for r in recs:
            dg = r.get("digest") or {}
            lines.append(f"=== {r['step']}  wall {r['wall_s']}s  model {dg.get('codex_model')} "
                         f"effort {dg.get('reasoning_effort')}  thread {r.get('thread_id')}")
            lines += dg.get("timeline") or []
            lines += [f"  thinking: {x}" for x in dg.get("reasoning_summaries") or []]
        log_file("run.log", "\n".join(lines) + "\n")
        log_file("summary.json", summary)
    if _LIVE["fatal"]:
        summary["stopped"] = _LIVE["fatal"]
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if _LIVE["fatal"]:
        raise SystemExit(3)
    if not summary["images"]:
        raise SystemExit(2)


def cmd_batch(args) -> None:
    """Run generate jobs in parallel subprocesses; every job logs into <out>/logs/<name>/; writes batch-report.json
    and batch-report.md (timings, Codex models, image-tool latency, tokens, plan usage, judge verdicts, rounds)."""
    import concurrent.futures as cf
    import threading
    workdir = Path(args.workdir).expanduser().resolve() if args.workdir else Path.cwd().resolve()
    if args.timeout is None:
        args.timeout = GEN_TIMEOUT if args.mode == "fast" else AGENT_TIMEOUT
    for flag in ("resume", "rejudge"):
        if getattr(args, flag, False) and (args.mode != "fast" or not args.out_dir):
            die(f"--{flag} needs fast mode and the --out-dir of the run it continues")
    try:
        spec = json.loads(Path(args.jobs).expanduser().read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read the jobs file {args.jobs}: {e}")
    jobs = spec.get("jobs") if isinstance(spec, dict) else spec
    if not isinstance(jobs, list) or not all(isinstance(j, dict) and j.get("name") and isinstance(j.get("brief"), str)
                                             and j["brief"].strip() for j in jobs):
        die("the jobs file must be a list of jobs (or {\"jobs\": [...]}) and every job needs a name and a brief "
            "(non-empty text)")
    # relative paths in the jobs file (style, refs, target): next to the jobs file, then --workdir, then here
    bases = list(dict.fromkeys([Path(args.jobs).expanduser().resolve().parent, workdir]))
    check_candidates(getattr(args, "candidates", None), "--candidates")
    for j in jobs:  # everything is checked here, before any Codex session
        check_name(j["name"])
        what = f"job {j['name']}"
        if j.get("export_name"):
            check_name(j["export_name"], "export_name")
        if j.get("aspect") and j["aspect"] not in ASPECTS:
            die(f"{what}: unknown aspect {j['aspect']!r}; use one of {', '.join(ASPECTS)}")
        if j.get("size"):
            check_size(j["size"], what)
        check_candidates(j.get("candidates"), what)
        inputs = 0
        for key, label in (("refs", "reference image"), ("target", "edit target")):
            if j.get(key):
                vals = j[key] if isinstance(j[key], list) else [j[key]]
                found = [find_input(v, bases) for v in vals]
                for v, p in zip(vals, found):
                    if p is None or not p.is_file():
                        die(f"{what}: {label} not found: {v}")
                j[key] = [str(p) for p in found] if key == "refs" else str(found[0])
                inputs += len(found)
        if inputs > 5:
            die(f"{what}: Codex's image tool accepts at most 5 input images (edit target + references), got {inputs}")
        if looks_like_file_name(j["brief"]):
            log(f"WARNING: {what}: the brief looks like a file name ({j['brief'].strip()}); it is used as the brief "
                f"text. Put the brief itself in the jobs file")
    shared_locale = (spec.get("locale") if isinstance(spec, dict) else None) or getattr(args, "locale", None)
    shared_look = (spec.get("look") if isinstance(spec, dict) else None) or getattr(args, "look", None)
    shared_finish = (spec.get("finish") if isinstance(spec, dict) else None) or getattr(args, "finish", None)
    for j in jobs:
        if shared_finish and not j.get("finish"):
            j["finish"] = shared_finish
    for j in jobs:
        j["brief"] = with_look(with_locale(j["brief"], j.get("locale") or shared_locale), j.get("look") or shared_look)
    shared_style = (spec.get("style") if isinstance(spec, dict) else None) or getattr(args, "style", None)
    block = style_block(shared_style, bases) if shared_style else ""
    for j in jobs:  # a job's own "style" (file, text or object) replaces the shared lock; "style": false skips it
        own = j.get("style")
        if own is False:
            continue
        b = style_block(own, bases) if own not in (None, True, "") else block
        if b:
            j["brief"] = f"{j['brief'].rstrip()}\n{b}"
    if getattr(args, "auto_cast", True):
        n_cast = auto_cast(jobs)
        if n_cast:
            log(f"global set: rotated the main person's background across {n_cast} job(s) with people")
    names = [j["name"] for j in jobs]
    if len(set(names)) != len(names):
        die("job names must be unique")
    if getattr(args, "only", None):
        want = [n.strip() for n in args.only.split(",") if n.strip()]
        unknown = sorted(set(want) - set(names))
        if unknown:
            die(f"--only: no such job(s): {', '.join(unknown)}")
        jobs = [j for j in jobs if j["name"] in want]
    out_dir = Path(args.out_dir).expanduser() if args.out_dir else \
        workdir / "output" / "imagegen" / f"batch-{dt.datetime.now():%Y%m%d-%H%M}"
    out_dir = out_dir if out_dir.is_absolute() else workdir / out_dir
    (out_dir / "logs").mkdir(parents=True, exist_ok=True)
    if getattr(args, "dry_run", False):  # compact: the full prompts go to files, not to stdout
        pdir = out_dir / "prompts"
        pdir.mkdir(parents=True, exist_ok=True)
        rows = []
        for j in jobs:
            edit = bool(j.get("target"))
            prompt, hints = compile_prompt(j["brief"], j.get("aspect"), edit=edit)
            body, place = place_context(j["brief"])
            look = pick_look(body)[0] if not is_non_photo(j["brief"]) else "-"
            pf = pdir / f"{j['name']}.txt"
            write_atomic(pf, prompt + "\n")
            rows.append({"name": j["name"], "lint": lint_brief(j["brief"], j.get("aspect")),
                         "risks": brief_risks(j["brief"]), "place": place_label(place),
                         "look": look if not edit else "-", "finish": with_finish_default(dict(j, look=look)),
                         "checks": len(hints), "prompt": str(pf)})
        print(json.dumps({"out_dir": str(out_dir), "prompts": str(pdir), "jobs": rows}, indent=2, ensure_ascii=False))
        return
    if args.mode == "fast":
        fast_args(args)
        TELEMETRY["log_dir"] = str(out_dir / "logs")
        if getattr(args, "rejudge", False):  # judge the existing images again; nothing is generated
            rep = {"mode": "fast", "images": []}
            try:
                rejudge_jobs(jobs, args, out_dir, rep)
                if getattr(args, "export_dir", None):
                    ed = Path(args.export_dir).expanduser()
                    export_results(rep, jobs, ed if ed.is_absolute() else workdir / ed, args)
            finally:
                finish_batch_report(rep, jobs, args, out_dir)
            print_batch_summary(rep, out_dir)
            if _LIVE["fatal"]:
                raise SystemExit(3)
            return
        resumed, left = [], jobs
        if getattr(args, "resume", False):  # jobs that already passed in this --out-dir are kept, not made again
            found = {j["name"]: latest_meta(j["name"], out_dir) for j in jobs}
            resumed = [dict(row_from_meta(found[j["name"]][1], found[j["name"]][0]), resumed=True) for j in jobs
                       if found[j["name"]] and (found[j["name"]][1].get("judge") or {}).get("computed_verdict")
                       in VERDICT_LEVEL]
            kept = {r["name"] for r in resumed}
            left = [j for j in jobs if j["name"] not in kept]
            log(f"--resume: {len(resumed)} job(s) already passed and are kept; {len(left)} to run")
        for j in left:
            for w in lint_brief(j["brief"], j.get("aspect")):
                log(f"lint ({j['name']}): {w}")
        progress = out_dir / "batch-progress.jsonl"
        write_atomic(progress, "")
        rep = {"mode": "fast", "images": []}
        try:
            if left:
                fast_pipeline(left, args, workdir, out_dir, rep=rep, progress=progress)
            rep["images"] = order_rows(resumed + rep["images"], jobs)
            if getattr(args, "export_dir", None):
                ed = Path(args.export_dir).expanduser()
                export_results(rep, jobs, ed if ed.is_absolute() else workdir / ed, args)
        finally:  # the report is written even when the run is cut short, with every job that finished
            rep["images"] = order_rows(resumed + [i for i in rep.get("images") or [] if not i.get("resumed")], jobs)
            finish_batch_report(rep, jobs, args, out_dir)
        print_batch_summary(rep, out_dir)
        if _LIVE["fatal"]:
            raise SystemExit(3)
        return
    if args.fix_rounds is None:
        args.fix_rounds = 2
    if args.judge_effort is None:
        args.judge_effort = "high"
    common = ["--mode", "agent", "--effort", args.effort, "--max-attempts", str(args.max_attempts),
              "--timeout", str(args.timeout), "--judge-timeout", str(args.judge_timeout),
              "--threshold", str(args.threshold), "--judge-effort", args.judge_effort]
    common += (["--judge"] if args.judge else []) + (["--auto-fix", "--fix-rounds", str(args.fix_rounds)]
                                                       if args.auto_fix else [])
    common += (["--judge-model", args.judge_model] if args.judge_model else []) + \
              (["--codex-model", args.codex_model] if args.codex_model else [])
    rows, lock, t_batch = [], threading.Lock(), time.time()

    def run(i, job):
        # stagger the first starts 3 s apart; a job that waited for a free slot starts at once (it used to sleep
        # 3 s x its index AFTER getting the slot: jobs 4-10 of a --concurrency 3 batch idled 9-27 s each)
        time.sleep(max(0.0, t_batch + 3 * i - time.time()))
        jl = out_dir / "logs" / job["name"]
        jl.mkdir(parents=True, exist_ok=True)
        (jl / "brief.txt").write_text(job["brief"].strip() + "\n", encoding="utf-8")
        cmd = [sys.executable, str(Path(__file__).resolve()), "generate", "--prompt-file", str(jl / "brief.txt"),
               "--name", job["name"], "--out-dir", str(out_dir), "--workdir", str(workdir), "--log-dir", str(jl)]
        cmd += (["--aspect", job["aspect"]] if job.get("aspect") else []) + \
               (["--size", job["size"]] if job.get("size") else []) + \
               (["--finish", job["finish"]] if job.get("finish") else []) + \
               (["--transparent"] if job.get("transparent") else []) + common + list(job.get("args") or [])
        started = dt.datetime.now().astimezone()
        log(f"batch: start {job['name']}")
        # tracked process group: a stop signal ends the child, which ends its own Codex sessions
        proc = run_group(cmd, None, None, Path(tmp_dir(prefix="batch-job-")), env=dict(os.environ))
        wall = (dt.datetime.now().astimezone() - started).total_seconds()
        (jl / "stderr.log").write_text(proc["stderr"], encoding="utf-8")
        try:
            summ = json.loads(proc["stdout"][proc["stdout"].index("{"):]) if "{" in proc["stdout"] else {}
        except ValueError:
            summ = {"unparsed_stdout": proc["stdout"][-2000:]}
        row = {"index": i + 1, "name": job["name"], "aspect": job.get("aspect"), "brief": job["brief"].strip(),
               "started": started.isoformat(timespec="seconds"), "wall_s": round(wall, 1),
               "returncode": proc["returncode"], "log_dir": str(jl), "command": cmd, "summary": summ}
        log(f"batch: done {job['name']} rc={proc['returncode']} {wall:.0f}s "
            f"verdict={[im.get('judge_verdict') for im in summ.get('images', [])]}")
        with lock:
            rows.append(row)
            write_atomic(out_dir / "batch-progress.json",
                         json.dumps(sorted(rows, key=lambda r: r["index"]), indent=2, ensure_ascii=False))
        return row

    with cf.ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as ex:
        list(ex.map(lambda ij: run(*ij), enumerate(jobs)))
    rows.sort(key=lambda r: r["index"])
    report = {"created": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "workdir": str(workdir),
              "out_dir": str(out_dir), "concurrency": args.concurrency, "common_args": common,
              "batch_wall_s": round(time.time() - t_batch, 1), "codex_version": codex_version(codex_bin()),
              "jobs": rows}
    write_atomic(out_dir / "batch-report.json", json.dumps(report, indent=2, ensure_ascii=False))
    write_atomic(out_dir / "batch-report.md", batch_markdown(report))
    print(json.dumps({"out_dir": str(out_dir), "report_md": str(out_dir / "batch-report.md"),
                      "batch_wall_s": report["batch_wall_s"],
                      "results": [{"name": r["name"], "rc": r["returncode"], "wall_s": r["wall_s"],
                                   "images": [(Path(im["path"]).name, im.get("judge_verdict"))
                                              for im in r["summary"].get("images", [])]} for r in rows]},
                     indent=2, ensure_ascii=False))


def batch_markdown(rep: dict) -> str:
    L = [f"# Batch report · {rep['created']}", "",
         f"- Output: `{rep['out_dir']}`", f"- Codex CLI: {rep['codex_version']}; concurrency {rep['concurrency']}; "
         f"batch wall time {rep['batch_wall_s']} s", f"- Common flags: `{' '.join(rep['common_args'])}`", "",
         "| # | Job | Kept image | Verdict | Scores R/A/P/C/B | Rounds | Wall s | Image-tool s | Codex runs | "
         "Tokens in / out / reasoning | Codex model |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rep["jobs"]:
        s = r["summary"] or {}
        tt = (s.get("telemetry") or {}).get("totals") or {}
        for im in s.get("images") or [{}]:
            sc = im.get("judge_scores") or {}
            scores = "/".join(str(sc.get(k, "-")) for k in
                              ("realism", "artifacts", "physics_plausibility", "composition", "brief_fidelity"))
            rounds = " → ".join(f"{x['mode']}:{x['verdict']}" for x in im.get("judge_rounds") or [])
            L.append(f"| {r['index']} | {r['name']} | {Path(im['path']).name if im.get('path') else 'none'} | "
                     f"{im.get('judge_verdict') or ('rc ' + str(r['returncode']))} | {scores} | {rounds or 'none'} | "
                     f"{r['wall_s']} | {tt.get('image_gen_s', '-')} ({tt.get('image_gen_calls', 0)} calls) | "
                     f"{tt.get('codex_runs', '-')} | {tt.get('input_tokens', 0):,} / {tt.get('output_tokens', 0):,} / "
                     f"{tt.get('reasoning_output_tokens', 0):,} | {', '.join(tt.get('codex_models') or []) or '-'} |")
    L.append("")
    for r in rep["jobs"]:
        s = r["summary"] or {}
        L += [f"## {r['index']}. {r['name']}", "", "```text", r["brief"], "```", ""]
        if s.get("lint"):
            L.append("Lint: " + "; ".join(s["lint"]))
        for st in (s.get("telemetry") or {}).get("steps") or []:
            L.append(f"- `{st['step']}` {st['wall_s']} s · {st.get('codex_model')} ({st.get('effort')}) · "
                     f"image tool {st.get('image_gen_s') or '-'} s · reasoning summaries {st.get('reasoning_summaries')}")
        for im in s.get("images") or []:
            L.append(f"- Kept: `{im.get('path')}` ({im.get('width')}×{im.get('height')}) · verdict "
                     f"**{im.get('judge_verdict')}** · rejected: {[Path(x).name for x in im.get('rejected_candidates') or []]}")
            if im.get("judge_fix"):
                L.append(f"- Judge's remaining fix: {im['judge_fix']}")
        L += [f"- Logs: `{r['log_dir']}` (run.log, telemetry.json, per-step prompt/events/digest)", ""]
    return "\n".join(L) + "\n"


def _paths(items) -> list:
    out = []
    for it in items:
        q = Path(it).expanduser()
        out += sorted(x for x in q.rglob("*") if x.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")) \
            if q.is_dir() else [q]
    return out


def cmd_export(args) -> None:
    alts = json.loads(Path(args.alt_json).read_text(encoding="utf-8")) if args.alt_json else {}
    widths = [int(w) for w in args.widths.split(",")] if args.widths else None
    formats = tuple(f.strip() for f in args.formats.split(","))
    out_dir = Path(args.out).expanduser()
    srcs = _paths(args.src)
    for src in srcs:
        if not src.exists():
            die(f"not found: {src}")
    entries = export_many([((src, out_dir, widths, formats, args.quality, alts.get(src.stem, args.alt or ""), None,
                             args.url_prefix, args.sizes, args.eager), {}) for src in srcs])
    for src, e in zip(srcs, entries):
        log(f"exported {src.name}: {len(e['variants'])} files, {e['bytes_total'] // 1024} KB")
    mp = update_manifest(out_dir, entries)
    print(json.dumps({"manifest": str(mp), "images": [{"name": e["name"], "html": e["html"],
                                                       "bytes_total": e["bytes_total"]} for e in entries]},
                     indent=2, ensure_ascii=False))


def cmd_favicon(args) -> None:
    res = make_favicons(Path(args.src).expanduser(), Path(args.out).expanduser(), args.name, args.bg, args.theme)
    print(json.dumps(res, indent=2))


def cmd_og(args) -> None:
    w, h = parse_size(args.size)
    out = make_og(Path(args.bg).expanduser(), args.title, Path(args.out).expanduser(), args.subtitle or "",
                  args.logo, (w, h), args.font, args.font_regular, args.color, args.accent)
    print(json.dumps({"og_image": str(out), "html": f'<meta property="og:image" content="/{Path(out).name}">\n'
                                                   f'<meta property="og:image:width" content="{w}">\n'
                                                   f'<meta property="og:image:height" content="{h}">\n'
                                                   '<meta name="twitter:card" content="summary_large_image">'},
                     indent=2))


def cmd_cutout(args) -> None:
    res = [cutout(p, (Path(args.out).expanduser() / f"{p.stem}-cutout.png") if args.out else
                  p.with_name(f"{p.stem}-cutout.png"), args.tolerance, args.feather, args.key) for p in _paths(args.src)]
    print(json.dumps(res, indent=2))


def cmd_audit(args) -> None:
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():  # a typo used to give a clean report with 0 images and a "global" place
        die(f"not a folder: {root}")
    rep = audit_site(root)
    if args.out:
        Path(args.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    brief = {k: rep[k] for k in ("root", "images", "references", "issue_counts", "locale")}
    brief["top_issues"] = rep["issues"][:40]
    brief["largest_images"] = rep["inventory"][:10]
    print(json.dumps(brief, indent=2, ensure_ascii=False))


def cmd_finish(args) -> None:
    out = []
    for src in args.src:
        sp = Path(src).expanduser().resolve()
        if not sp.exists():
            die(f"not found: {sp}")
        dst = None
        if args.out_dir:
            od = Path(args.out_dir).expanduser()
            od.mkdir(parents=True, exist_ok=True)
            dst = unique_path(od / sp.name)
        out.append(finish_image(sp, args.profile, dst=dst, warm_scene=args.warm, wb=args.wb, grain=args.grain,
                                vignette=args.vignette))
    print(json.dumps(out, indent=2))


def cmd_locale(args) -> None:
    root = Path(args.root).expanduser().resolve() if args.root else None
    if root is not None and not root.is_dir():
        die(f"not a folder: {root}")
    if root is None and not args.text:
        die("give --root and/or --text")
    rep = detect_locale(root, args.text)
    if args.out:
        Path(args.out).write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rep, indent=2, ensure_ascii=False))


def cmd_doctor(args) -> None:
    if getattr(args, "setup", False):
        if not (VENV_DIR / "bin" / "python").exists():
            subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        subprocess.run([str(VENV_DIR / "bin" / "python"), "-m", "pip", "install", "-q", "--upgrade", "pillow"],
                       check=True)
        log(f"skill venv ready at {VENV_DIR} (Pillow for export, favicon, og, cutout, audit, --size)")
    rep = {"python": sys.version.split()[0], "codex_home": str(CODEX_HOME)}
    try:
        bin_ = codex_bin()
    except SystemExit:
        print(json.dumps(dict(rep, codex="NOT FOUND"), indent=2))
        raise
    rep["codex_bin"] = bin_
    rep["codex_version"] = codex_version(bin_)
    st = subprocess.run([bin_, "login", "status"], capture_output=True, text=True)
    rep["login"] = (st.stdout + st.stderr).strip().splitlines()[-1] if (st.stdout + st.stderr).strip() else "unknown"
    feats = subprocess.run([bin_, "features", "list"], capture_output=True, text=True).stdout
    rep["image_generation_feature"] = next((" ".join(l.split()[1:]) for l in feats.splitlines()
                                            if l.startswith("image_generation ")), "unknown")
    try:
        need_pillow()
        import PIL  # type: ignore
        from PIL import features  # type: ignore
        rep["pillow"] = f"{PIL.__version__} (webp {features.check('webp')}, avif {features.check('avif')})"
    except SystemExit:
        rep["pillow"] = "missing: run `doctor --setup` (needed by export, favicon, og, cutout, --size on Linux)"
    rep["sips"] = bool(shutil.which("sips"))
    try:
        import cairosvg  # type: ignore  # noqa: F401
        cairo = True
    except Exception:
        cairo = False
    rep["svg_rasterizer"] = next((n for n in ("rsvg-convert", "qlmanage") if shutil.which(n)), None) or \
        ("cairosvg" if cairo else "none: pass a PNG mark to favicon, or install librsvg")
    rep["api_engine_key"] = "present" if get_api_key() else "absent (codex engine still works)"
    rep["skill_version"] = SKILL_VERSION
    n_loc = len(locales().get("countries", []))
    rep["locales"] = f"{n_loc} countries" if n_loc else "MISSING scripts/locales.json: place rules and locale detection off"
    rep["codex_tz"] = CODEX_TZ
    agents = CODEX_HOME / "AGENTS.md"
    if agents.exists():
        lang = re.search(r"(?im)^\s*(reply|respond|answer|write)\s+in\s+([A-Za-z]+)", agents.read_text(errors="ignore"))
        rep["codex_agents_md"] = (f"asks for replies in {lang.group(2)}; judge fields and prompts are forced to English"
                                  if lang else "present")
    if args.smoke:
        t0 = time.time()
        r = subprocess.run([bin_, "exec", "--ephemeral", "--skip-git-repo-check", "-s", "read-only",
                            "Reply with exactly: OK"], capture_output=True, text=True, timeout=300, env=codex_env())
        rep["smoke_test"] = ("pass" if "OK" in r.stdout else f"FAIL: {(r.stdout + r.stderr)[-300:]}") + \
                            f" ({time.time() - t0:.0f}s)"
    if getattr(args, "image_smoke", False):
        # the real image path: code mode + the built-in image tool + the generated file with its C2PA manifest
        t0 = time.time()
        tmp = Path(tmp_dir(prefix="codex-smoke-"))
        res = codex_parallel_images([{"id": "smoke", "prompt": "Format: square 1:1 format.\nA plain white ceramic cup "
                                      "on a grey table in soft window light. A real photograph, no text."}],
                                    tmp, "low", 420)
        r = (res.get("results") or {}).get("smoke") or {}
        rep["image_smoke_test"] = (f"pass ({time.time() - t0:.0f}s, C2PA {'yes' if ai_source(r['src']) else 'NO'}): "
                                   f"{r['src']}" if r.get("ok") else f"FAIL: {r.get('err') or 'no image returned'}")
    ok = "chatgpt" in rep["login"].lower() and "true" in rep["image_generation_feature"]
    rep["ready_for_codex_engine"] = ok
    print(json.dumps(rep, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser(description="Image generation/editing through the local Codex CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("generate", "edit"):
        p = sub.add_parser(name)
        p.add_argument("--prompt")
        p.add_argument("--prompt-file")
        if name == "edit":
            p.add_argument("--image", required=True, help="edit target (local file)")
            p.add_argument("--mask", help="PNG mask, alpha 0 = edit (api engine only)")
        else:
            p.set_defaults(image=None, mask=None)
        p.add_argument("--ref", action="append", help="reference image, optionally PATH=ROLE (repeatable)")
        p.add_argument("--out", help="output PNG path (relative to --workdir)")
        p.add_argument("--out-dir", help="output folder (default <workdir>/output/imagegen)")
        p.add_argument("--name", help="file name stem (default: slug of the brief)")
        p.add_argument("--n", type=int, default=1, choices=range(1, 5), metavar="1-4")
        p.add_argument("--explore", action="store_true", help="make the n variants clearly different directions")
        p.add_argument("--aspect", choices=sorted(ASPECTS), help="aspect ratio written into the prompt")
        p.add_argument("--size", help="exact final WxH (center crop + resize after generation)")
        p.add_argument("--engine", choices=["codex", "api", "auto"], default="codex")
        p.add_argument("--model", help="api engine: gpt-image-2.5-sunburst | gpt-image-2.5-flare | gpt-image-2")
        p.add_argument("--tier", choices=sorted(TIERS), default="final", help="api engine model/quality preset")
        p.add_argument("--quality", choices=Q_ORDER, help="api engine quality override")
        p.add_argument("--api-size", help="api engine generation size (default from --aspect)")
        p.add_argument("--raw-prompt", action="store_true", help="send the brief as written, without the compiled format/place/look/realism/physics "
                            "layers (api engine, and the codex engine with the compiled prompt writer); the brief "
                            "then has to state the aspect itself")
        p.add_argument("--effort", default=os.environ.get("CODEX_IMAGEGEN_EFFORT", "xhigh"),
                       help="Codex reasoning effort (extended thinking default: xhigh)")
        p.add_argument("--codex-model", help="Codex agent model override (-m)")
        p.add_argument("--max-attempts", type=int, default=2, help="generations per deliverable incl. retries")
        p.add_argument("--no-qa", action="store_true", help="skip the Codex self-QA/retry loop")
        p.add_argument("--timeout", type=int, default=None,
                       help=f"seconds per Codex image session (fast default {GEN_TIMEOUT}; agent mode and the API "
                            f"engine {AGENT_TIMEOUT})")
        p.add_argument("--judge-timeout", type=int, default=JUDGE_TIMEOUT, help="seconds per judge session")
        p.add_argument("--workdir", help="project root Codex may write in (default: current directory)")
        p.add_argument("--dry-run", action="store_true", help="print the plan/prompt without generating")
        p.add_argument("--judge", action="store_true", help="grade each image in a fresh, independent Codex session")
        p.add_argument("--auto-fix", action="store_true",
                       help="judge, then fix failures (edit for local defects, regenerate for pose/grip/composition)")
        p.add_argument("--fix-rounds", type=int, default=None,
                       help="fix rounds (fast default 1, agent default 2; max 3; 0 = judge only)")
        p.add_argument("--mode", choices=["fast", "agent"], default=os.environ.get("CODEX_IMAGEGEN_MODE", "fast"),
                       help="fast: compiled prompt, parallel generation + parallel judge (default); agent: Codex "
                            "art-director session with self-QA (slower)")
        p.add_argument("--no-judge", action="store_true", help="fast mode: skip the independent judge")
        p.add_argument("--no-early-exit", dest="early_exit", action="store_false",
                       help="fast mode: wait for every candidate even after one passes")
        p.add_argument("--style", help="style lock / brand DNA (text, .txt/.md or .json file) appended to the brief")
        p.add_argument("--locale", help='where the image is set: "City, Country" or "global" (default: a place the '
                                        'brief names, else internationally neutral)')
        p.add_argument("--look", choices=sorted(LOOKS) + ["auto", "none"], help="capture profile for photos (default auto: picked from the intent; none = no capture line)")
        p.add_argument("--transparent", action="store_true", help="isolated subject on a transparent background")
        p.add_argument("--finish", choices=sorted(FINISHES) + ["auto", "none"], default=None,
                       help="photographic finish after judging (default auto: from the look; the original stays as -raw)")
        p.add_argument("--export-dir", help="also export web variants (AVIF/WebP/JPEG + <picture> markup) here")
        p.add_argument("--alt", help="alt text for the exported image")
        p.add_argument("--eager", action="store_true", help="export markup for an above-the-fold (hero) image")
        p.add_argument("--url-prefix", help="public URL prefix for exported files (default: path after public/)")
        p.add_argument("--export-all", action="store_true", help="export even images whose verdict is FAIL")
        p.add_argument("--max-images", type=int, help="cap on image generations in this run (candidates + fixes)")
        p.add_argument("--strict", action="store_true",
                       help="brief precision counts like quality: PASS_WITH_NOTES becomes FAIL (client specs)")
        p.add_argument("--gen-effort", default="low", help="fast/compiled: reasoning effort of the generation session")
        p.add_argument("--prompt-writer", choices=["codex", "compiled"], default="compiled",
                       help="fast mode: compiled = brief + prompt-time checks verbatim (default, fastest); codex = an "
                            "art-director session rewrites the prompt first (for short or generic briefs)")
        p.add_argument("--prompt-effort", default="medium", help="fast mode: reasoning effort of the art director")
        p.add_argument("--max-parallel", type=int, default=10, help="fast mode: images per Codex session")
        p.add_argument("--judge-workers", type=int, default=10, help="fast mode: judges running at once")
        p.add_argument("--threshold", type=int, default=4, help="judge: minimum score per metric (0-5)")
        p.add_argument("--judge-model", help="judge: Codex model override (use a different model for diversity)")
        p.add_argument("--judge-effort", default=None, help="judge reasoning effort (fast default medium, agent high)")
        p.add_argument("--concurrency", type=int, default=10, help="fast mode: jobs/variants running at once")
        p.add_argument("--candidates", type=int, default=1, help="fast mode: parallel candidates per image (1-4)")
        p.add_argument("--no-auto-candidates", dest="auto_candidates", action="store_false",
                       help="fast mode: do not give risky briefs a second parallel candidate")
        p.add_argument("--log-dir", help="write prompts, Codex event streams, rollout digests, run.log and "
                                         "telemetry.json into this folder")
        p.set_defaults(func=cmd_generate_or_edit)
    j = sub.add_parser("judge", help="independent QA verdict for existing image(s), judged at once")
    j.add_argument("--image", action="append", required=True, help="image to judge (repeat for more)")
    j.add_argument("--prompt")
    j.add_argument("--prompt-file")
    j.add_argument("--threshold", type=int, default=4)
    j.add_argument("--judge-model")
    j.add_argument("--judge-effort", default="medium", help="medium (default) or high: same pass/fail, high is slower")
    j.add_argument("--timeout", type=int, default=JUDGE_TIMEOUT, help="seconds per judge session")
    j.set_defaults(func=cmd_judge)
    c = sub.add_parser("compare", help="same brief on several API models, each judged (needs OPENAI_API_KEY)")
    c.add_argument("--prompt")
    c.add_argument("--prompt-file")
    c.add_argument("--models", default="gpt-image-2,gpt-image-2.5-flare,gpt-image-2.5-sunburst",
                   help="comma list; gpt-image-2 is the baseline (the model Codex itself uses)")
    c.add_argument("--aspect", choices=sorted(ASPECTS))
    c.add_argument("--api-size")
    c.add_argument("--quality", choices=Q_ORDER, default="high")
    c.add_argument("--raw-prompt", action="store_true")
    c.add_argument("--name")
    c.add_argument("--out-dir")
    c.add_argument("--workdir")
    c.add_argument("--timeout", type=int, default=600)
    c.add_argument("--no-judge", action="store_true")
    c.add_argument("--threshold", type=int, default=4)
    c.add_argument("--judge-model")
    c.add_argument("--judge-effort", default="high")
    c.add_argument("--dry-run", action="store_true")
    c.set_defaults(func=cmd_compare, tier="final", model=None, mask=None)
    b = sub.add_parser("batch", help="run many generate jobs from a JSON file with bounded concurrency + report")
    b.add_argument("--jobs", required=True, help='JSON list: [{"name", "brief", "aspect", "size"?, "args"?: [...]}]')
    b.add_argument("--only", help="comma-separated job names to run (rerun failures; casting stays as in the full set)")
    b.add_argument("--resume", action="store_true",
                   help="fast mode: keep the jobs whose image and meta.json in --out-dir already passed (PASS or "
                        "PASS_WITH_NOTES) and run only the others")
    b.add_argument("--rejudge", action="store_true",
                   help="fast mode: judge the images already in --out-dir again from their meta.json (after a judge "
                        "ERROR); no new image is made; add --export-dir to export the ones that pass")
    b.add_argument("--concurrency", type=int, default=10, help="fast: jobs at once (agent mode: use 3)")
    b.add_argument("--dry-run", action="store_true", help="print every job's compiled prompt, checks, lint, place, look and finish; generate nothing")
    b.add_argument("--out-dir", help="default <workdir>/output/imagegen/batch-<timestamp>")
    b.add_argument("--workdir")
    b.add_argument("--judge", action="store_true")
    b.add_argument("--auto-fix", action="store_true")
    b.add_argument("--fix-rounds", type=int, default=None, help="fast default 1, agent default 2")
    b.add_argument("--mode", choices=["fast", "agent"], default=os.environ.get("CODEX_IMAGEGEN_MODE", "fast"))
    b.add_argument("--no-judge", action="store_true")
    b.add_argument("--no-early-exit", dest="early_exit", action="store_false")
    b.add_argument("--style", help="style lock / brand DNA shared by every job (or put \"style\" in the jobs file)")
    b.add_argument("--locale", help='default place for every job ("City, Country" or "global"); job or jobs-file '
                                    '"locale" wins')
    b.add_argument("--look", choices=sorted(LOOKS) + ["auto", "none"], help="default capture profile for every photo job; job or jobs-file \"look\" wins")
    b.add_argument("--no-auto-cast", dest="auto_cast", action="store_false",
                   help="global sets: do not rotate the main person's background across jobs")
    b.add_argument("--finish", choices=sorted(FINISHES) + ["auto", "none"], default=None,
                   help="default finish for every job; job or jobs-file \"finish\" wins")
    b.add_argument("--export-dir", help="export web variants of every usable image here (uses job alt/eager/widths)")
    b.add_argument("--url-prefix")
    b.add_argument("--export-all", action="store_true")
    b.add_argument("--max-images", type=int, help="cap on image generations in this run (candidates + fixes)")
    b.add_argument("--strict", action="store_true")
    b.add_argument("--gen-effort", default="low")
    b.add_argument("--prompt-writer", choices=["codex", "compiled"], default="compiled")
    b.add_argument("--prompt-effort", default="medium")
    b.add_argument("--max-parallel", type=int, default=10)
    b.add_argument("--judge-workers", type=int, default=10)
    b.add_argument("--max-attempts", type=int, default=2)
    b.add_argument("--effort", default=os.environ.get("CODEX_IMAGEGEN_EFFORT", "xhigh"))
    b.add_argument("--threshold", type=int, default=4)
    b.add_argument("--judge-effort", default=None, help="fast default medium, agent default high")
    b.add_argument("--judge-model")
    b.add_argument("--codex-model")
    b.add_argument("--candidates", type=int, default=1)
    b.add_argument("--no-auto-candidates", dest="auto_candidates", action="store_false")
    b.add_argument("--timeout", type=int, default=None,
                   help=f"seconds per Codex image session (fast default {GEN_TIMEOUT}, agent mode {AGENT_TIMEOUT})")
    b.add_argument("--judge-timeout", type=int, default=JUDGE_TIMEOUT, help="seconds per judge session")
    b.set_defaults(func=cmd_batch)
    x = sub.add_parser("export", help="web-ready responsive variants + <picture> markup + assets.json")
    x.add_argument("--src", nargs="+", required=True, help="image files or folders")
    x.add_argument("--out", required=True, help="output folder (e.g. public/images/home)")
    x.add_argument("--widths", help="comma list, default 480,768,1024,1440,1920 (never upscaled)")
    x.add_argument("--formats", default="avif,webp,jpg")
    x.add_argument("--quality", type=int, default=80)
    x.add_argument("--alt", help="alt text (single image)")
    x.add_argument("--alt-json", help='{"<file stem>": "alt text", ...}')
    x.add_argument("--sizes", default="100vw", help="the <img sizes> attribute")
    x.add_argument("--eager", action="store_true", help="above-the-fold image: eager + fetchpriority=high")
    x.add_argument("--url-prefix")
    x.set_defaults(func=cmd_export)
    f = sub.add_parser("favicon", help="favicon.ico + PNG sizes + apple/android/maskable icons + site.webmanifest")
    f.add_argument("--src", required=True, help="square logo mark (PNG, or SVG if an SVG rasterizer exists)")
    f.add_argument("--out", required=True, help="usually the site's public/ folder")
    f.add_argument("--name", default="")
    f.add_argument("--theme", default="#ffffff")
    f.add_argument("--bg", help="solid background for apple-touch and maskable icons (default = theme)")
    f.set_defaults(func=cmd_favicon)
    o = sub.add_parser("og", help="social card with guaranteed text over a generated background")
    o.add_argument("--bg", required=True)
    o.add_argument("--title", required=True)
    o.add_argument("--subtitle")
    o.add_argument("--logo")
    o.add_argument("--out", required=True)
    o.add_argument("--size", default="1200x630")
    o.add_argument("--font", help="bold .ttf/.otf (brand font)")
    o.add_argument("--font-regular")
    o.add_argument("--color", default="#ffffff")
    o.add_argument("--accent", help="accent bar color, e.g. #0ea5e9")
    o.set_defaults(func=cmd_og)
    ct = sub.add_parser("cutout", help="transparent PNG from a flat-background image (or clean native alpha)")
    ct.add_argument("--src", nargs="+", required=True)
    ct.add_argument("--out")
    ct.add_argument("--tolerance", type=int, default=40)
    ct.add_argument("--feather", type=float, default=1.2)
    ct.add_argument("--key", help="background color to remove, e.g. #ffffff (default: sampled from the border)")
    ct.set_defaults(func=cmd_cutout)
    au = sub.add_parser("audit", help="inventory and issues of every image in an existing web project")
    au.add_argument("--root", required=True)
    au.add_argument("--out", help="write the full JSON report here")
    au.set_defaults(func=cmd_audit)
    fn = sub.add_parser("finish", help="photographic finish: white balance on the colour cast, grain, vignette, "
                                       "halation (in place keeps the original as -raw)")
    fn.add_argument("--src", action="append", required=True)
    fn.add_argument("--profile", choices=sorted(FINISHES), default="natural")
    fn.add_argument("--out-dir", help="write finished copies here instead of finishing in place")
    fn.add_argument("--warm", action="store_true", help="lamp-lit or sunset scene: only trim the cast")
    fn.add_argument("--wb", type=float, help="override: share of the colour cast removed (0-1)")
    fn.add_argument("--grain", type=float, help="override: grain strength (8-bit levels at 1536 px)")
    fn.add_argument("--vignette", type=float, help="override: edge darkening (0-0.3)")
    fn.set_defaults(func=cmd_finish)
    lc = sub.add_parser("locale", help="detect a project's audience location (address, phone, currency, domain, "
                                       "language, place names) -> the Locale for its image briefs")
    lc.add_argument("--root", help="project folder to scan")
    lc.add_argument("--text", help="also read this text: the client's request, an address, a brief")
    lc.add_argument("--out", help="write the full JSON here")
    lc.set_defaults(func=cmd_locale)
    d = sub.add_parser("doctor")
    d.add_argument("--smoke", action="store_true", help="also run a tiny codex exec round-trip")
    d.add_argument("--image-smoke", action="store_true",
                   help="also generate one small image through the real pipeline (run after every codex update)")
    d.add_argument("--setup", action="store_true", help="create the skill venv with Pillow (export/favicon/og/cutout)")
    d.set_defaults(func=cmd_doctor)
    args = ap.parse_args()
    install_stop_handlers()
    try:
        args.func(args)
    except (OSError, ValueError) as e:  # a missing file or a bad value: one clear line instead of a traceback
        die(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
