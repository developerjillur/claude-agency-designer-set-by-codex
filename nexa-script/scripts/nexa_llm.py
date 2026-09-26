"""Model calls for the nexa writing family (nexa-research, nexa-script, nexa-copy): rubric judges, audience panels
and extraction, each in a fresh session outside the writer, answering in a JSON schema.

Standard library only, Python 3.9 or newer. Each skill keeps an identical copy in its own scripts folder, so every
skill installs on its own; the skills' tests keep the copies the same.

Engines
- codex: a fresh, read-only, ephemeral Codex CLI session in an empty folder that answers in a JSON schema (the
  codex-design judge pattern: a judge that can read the writer's notes judges the notes). Runs on the ChatGPT plan,
  no API key.
- gemini: the Gemini API through gemini_api.py (the family's shared module, byte for byte), with a JSON schema.
  Needs GEMINI_API_KEY in the environment or the macOS keychain; the key is never printed.
- auto: codex, then gemini when codex is missing or fails.

Every answer is cached by (engine, model, effort, prompt, schema) in ~/.cache/nexa-writing (NEXA_CACHE); fresh=True
asks again. A different model family from the writer is the point: a model grades its own family's text too kindly.

Test hooks (environment): NEXA_LLM_FAKE=1 answers every call with a minimal object built from the schema (no model,
no network); NEXA_LLM_FAKE_FILE=path.json answers from a file of {"who": answer} (or {"*": answer}).
"""
import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CACHE_VERSION = "1"
CACHE = Path(os.environ.get("NEXA_CACHE", str(Path.home() / ".cache" / "nexa-writing")))
APP_BUNDLED_CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
# Automated sessions need no memories, apps or browser use: the codex-imagegen measurements (start-up 14.5 s to
# 9.1 s) and it keeps judge sessions out of the user's Codex memory.
LEAN_FLAGS = [] if os.environ.get("NEXA_CODEX_FULL_FEATURES") else [
    "-c", "features.memories=false", "-c", "memories.generate_memories=false", "-c", "memories.use_memories=false",
    "-c", "features.chronicle=false", "-c", "features.apps=false", "-c", "features.browser_use=false",
    "-c", "features.computer_use=false", "-c", "features.in_app_browser=false"]
LEAN_FLAGS = LEAN_FLAGS + shlex.split(os.environ.get("NEXA_CODEX_EXTRA_FLAGS", ""))
GEMINI_MODEL = os.environ.get("NEXA_GEMINI_MODEL", "gemini-3.8-flash")
GEMINI_THINKING = os.environ.get("NEXA_GEMINI_THINKING", "medium")
# The user's own Codex instructions (~/.codex/AGENTS.md) ask for Banglish replies; a judge's notes must be in the
# language the calling tool reads, so every prompt states it (the prompt can still ask for another language per field).
ONLY_THIS = ("Use only this message. Do not open, list or search any files, do not browse, and do not run "
             "commands. Write every field of the answer in English unless this message names another language for "
             "that field.\n\n")
ENGINES = ("auto", "codex", "gemini")


def log(message):
    print(f"[nexa {time.strftime('%H:%M:%S')}] {message}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------------------------------------- schema

def strict_schema(schema):
    """OpenAI structured outputs need every object closed (additionalProperties false) with every property required;
    optional fields become nullable instead. Returns a copy; the input is not changed."""
    if isinstance(schema, list):
        return [strict_schema(s) for s in schema]
    if not isinstance(schema, dict):
        return schema
    out = {k: strict_schema(v) for k, v in schema.items()}
    if out.get("type") == "object" or "properties" in out:
        props = out.get("properties", {})
        out["additionalProperties"] = False
        out["required"] = list(props.keys())
    return out


def fake_from_schema(schema, who=""):
    """The smallest object that fits the schema (for offline tests): first enum value, minimum or 0, one item."""
    if not isinstance(schema, dict):
        return None
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), "null")
    if kind == "object" or "properties" in schema:
        return {k: fake_from_schema(v, who) for k, v in schema.get("properties", {}).items()}
    if kind == "array":
        n = max(1, int(schema.get("minItems", 1)))
        return [fake_from_schema(schema.get("items", {}), who) for _ in range(n)]
    if kind in ("integer", "number"):
        return schema.get("minimum", 0)
    if kind == "boolean":
        return False
    if kind == "string":
        return f"fake {who}".strip()
    return None


def json_from_text(text):
    """A JSON object from a model answer, with or without a fenced block around it."""
    text = (text or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if m:
        text = m.group(1).strip()
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except ValueError:
                return None
    return None


def check_required(data, required):
    missing = [k for k in required if not isinstance(data, dict) or k not in data]
    return missing


# ----------------------------------------------------------------------------------------------------------- cache

def cache_key(*parts):
    return hashlib.sha256(json.dumps([CACHE_VERSION, *parts], ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


def cache_get(key):
    path = CACHE / f"{key}.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def cache_put(key, result):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{key}.json"
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(dict(result, saved_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())),
                              ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


# ---------------------------------------------------------------------------------------------------------- codex

def codex_bin():
    cand = os.environ.get("CODEX_BIN") or shutil.which("codex")
    if cand:
        return cand
    return str(APP_BUNDLED_CODEX) if APP_BUNDLED_CODEX.exists() else ""


def codex_env():
    """A neutral timezone, so the developer's location never leaks into a verdict."""
    tz = os.environ.get("NEXA_CODEX_TZ", "UTC")
    return dict(os.environ) if tz.lower() in ("", "system") else dict(os.environ, TZ=tz)


def _codex(prompt, schema, effort, timeout, who):
    bin_ = codex_bin()
    if not bin_:
        return {"ok": False, "error": "Codex CLI not found (install it or set CODEX_BIN)"}
    tmp = Path(tempfile.mkdtemp(prefix="nexa-codex-"))
    try:
        sp = tmp / "schema.json"
        sp.write_text(json.dumps(strict_schema(schema)), encoding="utf-8")
        last = tmp / "answer.json"
        cmd = [bin_, "exec", "--ephemeral", "--skip-git-repo-check", "-s", "read-only", "--json", "-C", str(tmp),
               "-c", f'model_reasoning_effort="{effort}"', "--output-schema", str(sp), "-o", str(last)] + \
            LEAN_FLAGS + ["-"]
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, input=ONLY_THIS + prompt, capture_output=True, text=True, timeout=timeout,
                                  env=codex_env(), cwd=str(tmp))
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"{who}: Codex timed out after {timeout} s"}
        wall = round(time.time() - t0, 1)
        text = last.read_text(encoding="utf-8", errors="replace") if last.exists() else ""
        data = json_from_text(text)
        if not isinstance(data, dict):
            tail = (proc.stderr or proc.stdout or "")[-400:].strip()
            return {"ok": False, "error": f"{who}: Codex gave no JSON answer (exit {proc.returncode}): {tail}"}
        return {"ok": True, "data": data, "engine": "codex", "model": "codex", "seconds": wall}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------------------------- gemini

def _gemini_module():
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import gemini_api  # noqa: E402  (the family's shared module)
    return gemini_api


def gemini_available():
    try:
        return bool(_gemini_module().keys())
    except Exception:  # noqa: BLE001 (no module or an unreadable keychain means no Gemini)
        return False


def _gemini(prompt, schema, model, thinking, timeout, who):
    try:
        g = _gemini_module()
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{who}: gemini_api.py missing ({e})"}
    t0 = time.time()
    last_err = None
    for attempt in range(3):
        cfg = {}
        text = ONLY_THIS + prompt
        if attempt < 2:
            cfg["responseMimeType"] = "application/json"
            cfg["responseJsonSchema"] = schema
        else:
            text += "\n\nReply with only a JSON object that follows this JSON schema:\n" + json.dumps(schema)
        if attempt == 0 and thinking:
            cfg["thinkingConfig"] = {"thinkingLevel": thinking}
        body = {"contents": [{"role": "user", "parts": [{"text": text}]}], "generationConfig": cfg}
        try:
            resp, _info = g.request("POST", f"/v1beta/models/{model}:generateContent", body, timeout=int(timeout))
        except g.GeminiError as e:
            last_err = f"{who}: Gemini API {e.kind}: {e}"
            if e.kind == "bad_request" and attempt < 2:
                continue
            break
        data = json_from_text("".join(g.text_parts(resp)))
        if isinstance(data, dict):
            return {"ok": True, "data": data, "engine": "gemini", "model": model,
                    "seconds": round(time.time() - t0, 1), "usage": g.usage(resp)}
        last_err = f"{who}: {model} did not return the requested JSON"
    return {"ok": False, "error": last_err or f"{who}: Gemini API failed"}


# ----------------------------------------------------------------------------------------------------------- call

def _fake(schema, who):
    path = os.environ.get("NEXA_LLM_FAKE_FILE")
    if path:
        answers = json.loads(Path(path).read_text(encoding="utf-8"))
        data = answers.get(who, answers.get("*"))
        if data is not None:
            return {"ok": True, "data": data, "engine": "fake", "model": "fake", "seconds": 0.0}
    return {"ok": True, "data": fake_from_schema(schema, who), "engine": "fake", "model": "fake", "seconds": 0.0}


# A judge or panel call normally answers in 10 to 60 s; a session that hangs (an MCP server that will not start) must
# not hold a whole review for 15 minutes. codex-imagegen measured judges at 38 s median and 104 s at most.
CALL_TIMEOUT = int(os.environ.get("NEXA_LLM_TIMEOUT", "240"))


def call_json(prompt, schema, engine="auto", effort="medium", model=None, timeout=None, fresh=False, who="call",
              required=None, retries=1):
    """One fresh session answering `prompt` in `schema`. Returns {"ok", "data", "engine", "model", "seconds",
    "cached", "error"}. `required` lists keys the answer must have; a missing key or an empty answer is asked once
    more, then the other engine is tried (auto)."""
    timeout = timeout or CALL_TIMEOUT
    if engine not in ENGINES:
        raise ValueError(f"engine must be one of {ENGINES}")
    if os.environ.get("NEXA_LLM_FAKE") or os.environ.get("NEXA_LLM_FAKE_FILE"):
        return dict(_fake(schema, who), cached=False)
    required = list(required or schema.get("required") or schema.get("properties", {}).keys())
    order = ["codex", "gemini"] if engine == "auto" else [engine]
    errors = []
    for eng in order:
        mdl = model if (model and eng == "gemini") else (GEMINI_MODEL if eng == "gemini" else "codex")
        key = cache_key(eng, mdl, effort, prompt, schema)
        if not fresh:
            hit = cache_get(key)
            if hit and hit.get("ok"):
                return dict(hit, cached=True)
        if eng == "gemini" and not gemini_available():
            errors.append("gemini: no GEMINI_API_KEY")
            continue
        for attempt in range(retries + 1):
            res = (_codex(prompt, schema, effort, timeout, who) if eng == "codex" else
                   _gemini(prompt, schema, mdl, GEMINI_THINKING if effort != "low" else "low", timeout, who))
            if res.get("ok"):
                missing = check_required(res["data"], required)
                if not missing:
                    cache_put(key, res)
                    return dict(res, cached=False)
                res = {"ok": False, "error": f"{who}: answer missing {missing}"}
            errors.append(res["error"])
            if attempt < retries:
                log(f"{res['error'][-200:]}; asking once more")
    return {"ok": False, "data": None, "engine": engine, "model": model, "cached": False,
            "error": " | ".join(errors[-3:]) or f"{who}: no engine answered"}


def call_many(jobs, workers=6):
    """Run call_json for each job dict (the keyword arguments of call_json) in parallel; results keep the order."""
    if not jobs:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, len(jobs)))) as pool:
        futures = [pool.submit(call_json, **job) for job in jobs]
        return [f.result() for f in futures]


def engines_status():
    """What can run here: for `doctor` commands."""
    bin_ = codex_bin()
    return {"codex": bool(bin_), "codex_bin": bin_ or None, "gemini": gemini_available(),
            "fake": bool(os.environ.get("NEXA_LLM_FAKE") or os.environ.get("NEXA_LLM_FAKE_FILE")),
            "cache": str(CACHE)}
