"""nexa-script core: formats, pace by language, loading a script, timing it and numbering its lines. Shared by the
CLI (script.py) and the rules (script_lint.py)."""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nexa_review as R  # noqa: E402

# Words per minute by format (English): R1 measured pros at 157 to 197 (Kurzgesagt 157-167, Johnny Harris 158-171,
# Veritasium 185-190, Mark Rober 192-197); R2 puts ad voice-over at about 2.5 words a second (150).
FORMATS = {
    "youtube-long": {"medium": "video", "wpm": 160, "long": True},
    "explainer": {"medium": "video", "wpm": 160, "long": True},
    "documentary": {"medium": "video", "wpm": 150, "long": True},
    "tutorial": {"medium": "video", "wpm": 150, "long": True},
    "commentary": {"medium": "video", "wpm": 170, "long": True},
    "short": {"medium": "video", "wpm": 165, "long": False, "max_s": 180},
    "ad": {"medium": "video", "wpm": 150, "long": False, "ad": True},
    "talk": {"medium": "listen", "wpm": 140, "long": True},
    "podcast": {"medium": "listen", "wpm": 155, "long": True},
    "blog": {"medium": "read", "wpm": None, "long": True},
}
ALIASES = {"reel": "short", "tiktok": "short", "shorts": "short", "ugc-ad": "ad", "vsl": "ad", "article": "blog",
           "newsletter": "blog", "video-essay": "youtube-long"}
# Pace by language relative to English: Hindi creators measured at 173 to 252 wpm (median about 205) on the 14
# reference videos; Bangla has no measured sample yet, so nexa-speech's presets (125 to 140 for an explainer) set it.
LANG_FACTOR = {"en": 1.0, "hi": 1.25, "bn": 0.84, "banglish": 0.9}
# Truth modes (R3 R12, V5 H10): who may be quoted and what may be reconstructed
MODES = ("nonfiction", "personal", "testimonial", "case_study", "ad", "fiction")


def die(message, code=2):
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    sys.exit(code)


def emit(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"cannot read {path}: {e}")


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt_of(name):
    name = (name or "youtube-long").lower()
    name = ALIASES.get(name, name)
    if name not in FORMATS:
        die(f"unknown format {name!r}: one of {', '.join(sorted(FORMATS))} (or {', '.join(sorted(ALIASES))})")
    return name


def lang_of(text, given=None):
    if given:
        return given
    if re.search(r"[ঀ-৿]", text or ""):
        return "bn"
    if re.search(r"[ऀ-ॿ]", text or ""):
        return "hi"
    return "en"


def words(text):
    return re.findall(r"[\wঀ-৿ऀ-ॿ'’%$৳₹.-]+", text or "")


def sentences(text):
    return R.split_sentences(text or "")


def wpm_for(fmt, lang, meta_wpm=None):
    if meta_wpm:
        return float(meta_wpm)
    base = FORMATS[fmt]["wpm"]
    return None if base is None else round(base * LANG_FACTOR.get(lang, 1.0))


def mmss(sec):
    sec = int(round(sec or 0))
    return f"{sec // 60}:{sec % 60:02d}"


def loop_question(value):
    """A loop in the ledger is a question string, or {"question": ..., "cross_video": true} for a loop that is
    declared to run into the next video."""
    return value.get("question", "") if isinstance(value, dict) else str(value or "")


def loop_is_cross_video(value):
    return isinstance(value, dict) and bool(value.get("cross_video"))


# --------------------------------------------------------------------------------------------------- loading

def load_script(path, fmt=None, lang=None):
    """A script.json, a narration .txt (paragraphs become beats) or a .md article. Returns a normalised dict."""
    p = Path(path)
    if not p.exists():
        die(f"{path} not found")
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        try:
            data = json.loads(raw)
        except ValueError as e:
            die(f"{path}: not valid JSON ({e})")
        if not isinstance(data, dict):
            die(f"{path}: a script.json is an object with meta and beats, not a {type(data).__name__}")
        if (data.get("schema") or "").split("/")[0] not in ("nexa.script", ""):
            die(f"{path}: schema {data.get('schema')} is not nexa.script")
        meta = dict(data.get("meta") or {})
        beats = data.get("beats") or []
        meta["format"] = fmt_of(fmt or meta.get("format"))
        meta["lang"] = lang or meta.get("lang") or lang_of(" ".join(b.get("narration", "") for b in beats))
        return {"kind": "json", "meta": meta, "beats": beats, "promise": data.get("promise") or {},
                "loops": data.get("loops") or {}, "cta": data.get("cta") or {}, "story": data.get("story") or {},
                "raw": data, "path": str(p)}
    f = fmt_of(fmt or ("blog" if p.suffix.lower() == ".md" else "youtube-long"))
    if f == "blog":
        return {"kind": "blog", "meta": {"format": "blog", "lang": lang or lang_of(raw)}, "text": raw,
                "beats": [], "path": str(p)}
    paras = [x.strip() for x in re.split(r"\n\s*\n", raw) if x.strip()]
    beats = [{"id": f"b{i + 1}", "narration": x} for i, x in enumerate(paras)]
    return {"kind": "text", "meta": {"format": f, "lang": lang or lang_of(raw)}, "beats": beats, "promise": {},
            "loops": {}, "cta": {}, "story": {}, "path": str(p)}


def timing(script, wpm_override=None):
    meta = script["meta"]
    wpm = wpm_for(meta["format"], meta["lang"], wpm_override or meta.get("wpm"))
    t = 0.0
    rows = []
    for b in script["beats"]:
        n = len(words(b.get("narration", "")))
        secs = (n / wpm * 60 if wpm else 0.0) + float(b.get("pause_s") or 0)
        rows.append({"beat": b.get("id"), "start": round(t, 1), "end": round(t + secs, 1), "words": n,
                     "seconds": round(secs, 1)})
        t += secs
    return {"wpm": wpm, "total_seconds": round(t, 1), "beats": rows}


def narration_lines(script):
    """Numbered lines L1..Ln for judges and the panel; each line keeps its beat id, its start second and, on the
    first line of a video beat, the picture and the on-screen text."""
    if script["kind"] == "blog":
        body = re.sub(r"^#+\s.*$", "", script["text"], flags=re.M)
        return R.number_lines(body)
    lines = R.number_lines([{"text": b.get("narration", ""), "beat": b.get("id")} for b in script["beats"]])
    wpm = wpm_for(script["meta"]["format"], script["meta"]["lang"], script["meta"].get("wpm"))
    if wpm:
        t = 0.0
        for ln in lines:
            ln["t"] = round(t, 1)
            t += len(words(ln["text"])) / wpm * 60
    beats = {b.get("id"): b for b in script["beats"]}
    seen = set()
    for ln in lines:
        b = beats.get(ln.get("beat"))
        if b is not None and ln["beat"] not in seen:
            seen.add(ln["beat"])
            for key in ("visual", "on_screen"):
                if (b.get(key) or "").strip():
                    ln[key] = b[key].strip()
    return lines


def text_of(script):
    return script["text"] if script["kind"] == "blog" else "\n".join(b.get("narration", "") for b in script["beats"])
