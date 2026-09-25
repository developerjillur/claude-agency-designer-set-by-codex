"""Vox-style beats for nexa-video-creator (standard library only).

A vox overlay is one composition on the locked paper ground, grounded to a stretch of narration. Its elements
(cutouts, clips, photo cards, headlines, labels, tags, speech bubbles, a newspaper page, a chart card, a typewriter
line, hand-drawn marks, icons, a source line) each come in on a spoken word and may leave on another. This module
turns the plan's element list into what the renderer reads (template/src/vox.tsx):

- every time a frame from the beat's start, taken from measured word edges after every trim;
- every place a point on the frame, from a named slot for this frame's shape (landscape and vertical differ);
- sizes that fit (lines balanced, pictures sized from their own shape);
- the sound cues the beat's movement lands on (a rise, a pop, a counter landing, a key for every typed word);
- the checks a careful editor makes: every word time real, text inside the safe area and clear of other text,
  enough time to read, not too much on screen at once, every shown number said or sourced (nvc_plan does that
  from vox_text), a newspaper that does not put words in a real outlet's mouth.

prepare() runs inside compile_plan's overlay loop (the beat's words are known, its length is not final yet): it checks
the elements and resolves each time to seconds on the output timeline. bake() runs after every trim and gap-closing:
it turns those seconds into frames from the beat's final start, sets the exits (a beat joined to the next vox beat
runs VOX_EXIT frames under it while its elements leave), and adds the sound cues and layout checks.
"""
import json
import re

VOX_EXIT = 12
KINDS = ("cutout", "card", "clip", "headline", "label", "credit", "icon", "tag", "bubble", "newspaper", "chart",
         "typewriter", "scribble")
TEXT_KINDS = ("headline", "label", "credit", "tag", "bubble", "typewriter")
LAYERS = ("back", "mid", "fore", "text")
ENTERS = ("rise", "pop", "slideLeft", "slideRight", "drop", "wipe", "fade", "none")
EXITS = ("drop", "fade", "pop", "slideLeft", "slideRight", "rise", "cut")
ICONS = ("barrel", "up", "down", "pin", "coin", "dollar", "taka", "warning", "check", "cross")
SHAPES = ("circle", "underline", "arrow", "cross", "box")
TIME_FIELDS = ("at", "out", "land", "markAt", "drawAt", "drawEnd")

# (x, y, anchor) as shares of the frame: landscape and square first, vertical second. Vertical keeps text in the top
# half (captions sit near the middle of a short) and stands pictures on the bottom edge.
SLOTS = {
    "center": ((0.50, 0.50, "center"), (0.50, 0.34, "center")),
    "left": ((0.29, 0.50, "center"), (0.50, 0.26, "center")),
    "right": ((0.71, 0.50, "center"), (0.50, 0.43, "center")),
    "top": ((0.50, 0.19, "center"), (0.50, 0.18, "center")),
    "bottom": ((0.50, 0.80, "center"), (0.50, 0.46, "center")),
    "top-left": ((0.27, 0.24, "center"), (0.31, 0.22, "center")),
    "top-right": ((0.73, 0.24, "center"), (0.69, 0.22, "center")),
    "bottom-left": ((0.27, 0.74, "center"), (0.31, 0.44, "center")),
    "bottom-right": ((0.73, 0.74, "center"), (0.69, 0.44, "center")),
    "sky": ((0.50, 0.32, "center"), (0.50, 0.26, "center")),
    "stage": ((0.50, 1.00, "bottom"), (0.50, 1.00, "bottom")),
    "stage-left": ((0.30, 1.00, "bottom"), (0.32, 1.00, "bottom")),
    "stage-right": ((0.70, 1.00, "bottom"), (0.68, 1.00, "bottom")),
    "far-left": ((0.15, 1.00, "bottom"), (0.18, 1.00, "bottom")),
    "far-right": ((0.85, 1.00, "bottom"), (0.82, 1.00, "bottom")),
    "floor": ((0.50, 1.00, "bottom"), (0.50, 1.00, "bottom")),
}
DEFAULT_SLOT = {"cutout": "stage", "card": "center", "clip": "floor", "headline": "top", "label": "bottom",
                "credit": "credit", "icon": "center", "tag": "top-right", "bubble": "top-left", "newspaper": "center",
                "chart": "center", "typewriter": "text-left", "scribble": "center"}
DEFAULT_LAYER = {"cutout": "mid", "card": "mid", "clip": "back", "headline": "text", "label": "text", "credit": "text",
                 "icon": "fore", "tag": "text", "bubble": "text", "newspaper": "mid", "chart": "mid",
                 "typewriter": "text", "scribble": "text"}
DEFAULT_ENTER = {"card": "pop", "clip": "fade", "headline": "wipe", "label": "fade", "credit": "fade", "icon": "pop",
                 "tag": "pop", "bubble": "pop", "newspaper": "rise", "chart": "rise", "typewriter": "none",
                 "scribble": "none"}
# landscape, vertical (share of the frame width)
DEFAULT_W = {"card": (0.34, 0.72), "clip": (1.0, 1.0), "headline": (0.80, 0.88), "newspaper": (0.62, 0.92),
             "chart": (0.56, 0.92), "typewriter": (0.84, 0.86), "scribble": (0.2, 0.4)}
# a grounded cut-out's height (share of the frame) by layer: landscape, vertical
CUTOUT_H = {"back": (0.9, 0.46), "mid": (0.8, 0.4), "fore": (0.5, 0.26), "text": (0.5, 0.26)}
# text sizes in px on a 1080-short-side frame: landscape, vertical
DEFAULT_SIZE = {"headline": (104, 96), "tag": (128, 118), "bubble": (66, 64), "label": (46, 50), "typewriter": (58, 50),
                "credit": (18, 22), "icon": (90, 110)}
# letters per line before a line is broken again: landscape, vertical
LINE_CHARS = {"headline": (20, 13), "bubble": (12, 11), "typewriter": (44, 24), "newspaper": (26, 22)}
MAX_LINES = {"headline": 2, "bubble": 3, "typewriter": 3, "newspaper": 3}
# how much of a letter's size one letter takes, for the layout estimates (heavy caps, comic, typewriter, sans)
PER_CHAR = {"headline": 0.70, "bubble": 0.47, "typewriter": 0.62, "label": 0.55, "tag": 0.64, "credit": 0.62}
SOUND = {"rise": "swipe", "pop": "pop", "slideLeft": "whoosh-short", "slideRight": "whoosh-short", "drop": "swoosh-down",
         "wipe": "whoosh-short", "fade": None, "none": None}
KIND_SOUND = {"bubble": "bubble", "newspaper": "whoosh", "chart": "whoosh-short", "scribble": "swipe", "label": None,
              "credit": None, "clip": None}
MAX_AT_ONCE = 7
# Effects barely heard and only on the main motion (research/vox 02, 5.3): a few dB under nexa-sound's own levels.
CUE_GAIN = {"pop": -18, "swipe": -17, "whoosh-short": -15, "whoosh": -15, "bubble": -17, "ding": -16, "key": -25,
            "impact": -9, "swoosh-down": -16, "click": -22, "shutter": -18}
# A reveal bound to a word lands 2 to 4 frames before it (research/vox 02, 4.7): frames at 30 fps from the start of
# each entrance to its word, when the plan gives the bare word id.
LEAD_IN = {"rise": 13, "pop": 8, "slideLeft": 13, "slideRight": 13, "drop": 11, "wipe": 9, "fade": 9, "none": 3}
LEAD = {"land": 2, "markAt": 4, "marks": 4, "callout": 8, "moves": 12, "drawAt": 4}
QUIET_S = 5.0          # inside a beat, something new every 2 to 4 s; over this is a hold with nothing new
EXIT_OF = {"cut": "cut", "drop": "drop", "fade": "fade", "slide": "slideLeft", "pop": "pop", "leak": "cut",
           "sweep": "cut"}

WORD_TIME = re.compile(r"^(w\d+)(\.end)?\s*(?:([+-])\s*(\d+(?:\.\d+)?))?$")
BARE = re.compile(r"^w\d+$")


def _norm(w):
    return re.sub(r"[^\w%$€£¥৳]+", "", str(w).lower(), flags=re.UNICODE)


def _lines(el, key="lines", fallback="text"):
    v = el.get(key)
    if v in (None, "", []):
        v = el.get(fallback)
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)] if v not in (None, "") else []


def elements_of(ov):
    els = ov.get("elements")
    if els is None:
        els = (ov.get("props") or {}).get("elements")
    return els if isinstance(els, list) else []


def vox_text(ov):
    """Every word a vox beat puts on screen, for the number check and the review's expected lines. The source line
    is left out (it names the source, it is not a claim)."""
    parts = []
    for el in elements_of(ov):
        if not isinstance(el, dict):
            continue
        kind = el.get("kind")
        if kind in ("headline", "bubble", "typewriter"):
            parts += _lines(el)
        elif kind == "label":
            parts.append(str(el.get("text") or ""))
        elif kind == "tag":
            parts += [str(el.get("value") or ""), str(el.get("unit") or "")]
        elif kind == "newspaper":
            parts += _lines(el, "headline", "title") + [str(el.get("deck") or "")]
        elif kind == "chart":
            parts.append(str(el.get("title") or ""))
            call = el.get("callout") or {}
            parts += _lines(call) if isinstance(call, dict) else []
        elif kind == "card":
            parts.append(str(el.get("caption") or ""))
    return " ".join(p for p in parts if p.strip()).strip()


class Ctx:
    """What prepare() needs from compile_plan: the words, where they landed on the output, the frame and the job."""

    def __init__(self, words, idx, by_index, fps, preset, job, lang, balance_lines, graphemes, reading_time):
        self.words, self.idx, self.by_index, self.fps = words, idx, by_index, fps
        self.preset, self.job, self.lang = preset, job, lang
        self.W, self.H = preset["width"], preset["height"]
        self.vertical = self.H > self.W
        self.safe = preset.get("safe") or {"x": 0, "y": 0, "w": self.W, "h": self.H}
        self.balance_lines, self.graphemes, self.reading_time = balance_lines, graphemes, reading_time


def _pick(pair, vertical):
    return pair[1] if vertical else pair[0]


def _bengali(text):
    return any("ঀ" <= ch <= "৿" for ch in text or "")


def resolve_time(v, ctx, span, rep, where):
    """Seconds on the output timeline for one time field: a word id ("w0012"), its end ("w0012.end"), either with an
    offset in seconds ("w0012+0.3"), a number of seconds from the beat's start, or "start" / "end"."""
    start, end = span
    if v is None:
        return None
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return start + float(v)
    s = str(v).strip()
    if s == "start":
        return start
    if s == "end":
        return end
    m = WORD_TIME.match(s)
    if not m:
        rep.error(where, "time \"%s\" must be a word id (w0012), w0012.end, w0012+0.3, seconds from the beat's start, "
                         "\"start\" or \"end\"" % s)
        return None
    wid, at_end, sign, off = m.groups()
    if wid not in ctx.idx:
        rep.error(where, "unknown word id %s" % wid)
        return None
    occ = ctx.by_index.get(ctx.idx[wid]) or []
    near = [o for o in occ if start - 1.0 <= o["start"] <= end + 1.0]
    if not near:
        rep.error(where, "%s (\"%s\") is not spoken inside this beat (%.2f-%.2f s)"
                  % (wid, ctx.words[ctx.idx[wid]].get("text"), start, end))
        return None
    t = near[0]["end"] if at_end else near[0]["start"]
    if off:
        t += float(off) * (1 if sign == "+" else -1)
    return t


def _src_aspect(ctx, sid):
    s = (ctx.job.get("sources") or {}).get(sid) or {}
    w, h = s.get("width"), s.get("height")
    return (float(w) / float(h)) if w and h else 1.0


def prepare(ov, props, span, ctx, rep, where):
    """Check a vox overlay's elements and resolve their times to output seconds. Returns the props to keep (with the
    working list under "_vox"), or None when the beat cannot be built."""
    els = elements_of(ov)
    if not els:
        rep.error(where, "needs \"elements\": the pictures and words of this beat (references/plan.md, Vox beats)")
        return None
    vertical = ctx.vertical
    sourced = any(isinstance(f, dict) and str(f.get("origin")) in ("brief", "client", "web", "formula")
                  for f in (ov.get("facts") or []))
    out = []
    ids = set()
    for n, raw in enumerate(els):
        w = "%s elements[%d]" % (where, n)
        if not isinstance(raw, dict):
            rep.error(w, "must be an object")
            continue
        el = dict(raw)
        kind = el.get("kind")
        if kind not in KINDS:
            rep.error(w, "kind must be one of " + ", ".join(KINDS))
            continue
        el["id"] = str(el.get("id") or "e%d" % (n + 1))
        if el["id"] in ids:
            rep.error(w, "id %s is used twice in this beat" % el["id"])
            continue
        ids.add(el["id"])
        w = "%s %s (%s)" % (where, el["id"], kind)
        if el.get("layer") and el["layer"] not in LAYERS:
            rep.error(w, "layer must be one of " + ", ".join(LAYERS))
        if el.get("enter") and el["enter"] not in ENTERS:
            rep.error(w, "enter must be one of " + ", ".join(ENTERS))
        if el.get("exit") and el["exit"] not in EXITS:
            rep.error(w, "exit must be one of " + ", ".join(EXITS))
        if not _content_ok(el, kind, ctx, rep, w, sourced):
            continue
        _place(el, kind, ctx, rep, w)
        t = {}
        bare = set()
        for key in TIME_FIELDS:
            if el.get(key) is not None:
                t[key] = resolve_time(el[key], ctx, span, rep, w)
                if BARE.match(str(el[key])):
                    bare.add(key)
        if isinstance(el.get("callout"), dict) and el["callout"].get("at") is not None:
            t["callout"] = resolve_time(el["callout"]["at"], ctx, span, rep, w)
            if BARE.match(str(el["callout"]["at"])):
                bare.add("callout")
        if isinstance(el.get("marks"), list):
            t["marks"] = [resolve_time(m.get("at"), ctx, span, rep, w) if isinstance(m, dict) else None
                          for m in el["marks"]]
            if any(isinstance(m, dict) and BARE.match(str(m.get("at"))) for m in el["marks"]):
                bare.add("marks")
        if isinstance(el.get("moves"), list):
            t["moves"] = []
            moves = []
            for m in el["moves"]:
                m = dict(m) if isinstance(m, dict) else None
                if not m or m.get("at") is None:
                    rep.error(w, "every move needs \"at\" (a word id) and where to go (slot, or x and y)")
                    continue
                if m.get("slot"):
                    if m["slot"] not in SLOTS:
                        rep.error(w, "move slot must be one of " + ", ".join(SLOTS))
                        continue
                    x, y, _ = _pick(SLOTS[m["slot"]], vertical)
                    m.setdefault("x", x)
                    m.setdefault("y", y)
                moves.append(m)
                t["moves"].append(resolve_time(m["at"], ctx, span, rep, w))
                if BARE.match(str(m["at"])):
                    bare.add("moves")
            el["moves"] = moves
        if kind == "typewriter":
            t["times"] = _typewriter_times(el, ctx, span, t.get("at"))
            if t["times"] is None:
                rep.warn(w, "its words are not the spoken words in order, so it types them evenly; to type in sync, "
                            "use the words as they are said")
        t["bare"] = sorted(bare)
        el["_t"] = t
        out.append(el)
    for el in out:
        if el.get("follow") and el["follow"] not in ids:
            rep.error("%s %s" % (where, el["id"]), "follow names %s, which is not an element of this beat"
                      % el["follow"])
            el.pop("follow")
    p = dict(props)
    p.pop("elements", None)
    p["_vox"] = out
    p["push"] = float(ov.get("push", props.get("push", 0.035)))
    return p


def _content_ok(el, kind, ctx, rep, w, sourced):
    vertical = ctx.vertical
    if kind in ("cutout", "card", "clip"):
        sid = el.get("source")
        src = (ctx.job.get("sources") or {}).get(sid) if sid else None
        if not src:
            rep.error(w, "needs \"source\": a picture or clip in the job (nvc.py cutout for a cut-out, nvc.py add, "
                         "nvc.py stock)")
            return False
        if not (src.get("image") or src.get("proxy")):
            rep.error(w, "source %s is not ready: run nvc.py ingest" % sid)
            return False
        if kind == "cutout" and not src.get("alpha"):
            rep.warn(w, "source %s has no transparency, so it shows as a rectangle: cut it out with nvc.py cutout" % sid)
    if kind in ("headline", "bubble", "typewriter"):
        lines = _lines(el)
        if not lines:
            rep.error(w, "needs \"text\" or \"lines\"")
            return False
        limit = _pick(LINE_CHARS[kind], vertical)
        text = " ".join(lines)
        if _bengali(text):
            limit = max(8, int(limit * 0.8))
        if max(ctx.graphemes(x) for x in lines) > 1.25 * limit or len(lines) > MAX_LINES[kind]:
            el["lines"] = ctx.balance_lines(text, limit, MAX_LINES[kind])
        else:
            el["lines"] = lines
        el.pop("text", None)
        if len(el["lines"]) > MAX_LINES[kind] or max(ctx.graphemes(x) for x in el["lines"]) > 1.4 * limit:
            rep.warn(w, "%d letters is a lot for a %s on this frame; shorten it" % (ctx.graphemes(text), kind))
    if kind == "label" and not str(el.get("text") or "").strip():
        rep.error(w, "needs \"text\"")
        return False
    if kind == "credit" and not str(el.get("text") or "").strip():
        rep.error(w, "needs \"text\" (the source, like \"Source: World Bank, 2025\")")
        return False
    if kind == "tag":
        if str(el.get("value") or "").strip() == "":
            rep.error(w, "needs \"value\" (\"$116\", \"৫০০ টাকা\")")
            return False
        if el.get("from") is not None:
            try:
                el["from"] = float(str(el["from"]).replace(",", ""))
            except ValueError:
                rep.error(w, "from must be the number the counter starts at")
                el.pop("from")
    if kind == "icon" and str(el.get("icon") or el.get("name") or "") not in ICONS:
        rep.error(w, "icon must be one of " + ", ".join(ICONS))
        return False
    if kind == "scribble" and str(el.get("shape") or "circle") not in SHAPES:
        rep.error(w, "shape must be one of " + ", ".join(SHAPES))
        return False
    if kind == "newspaper":
        head = _lines(el, "headline", "title")
        if not head or not str(el.get("masthead") or "").strip():
            rep.error(w, "needs \"masthead\" and \"headline\"")
            return False
        limit = _pick(LINE_CHARS["newspaper"], vertical)
        text = " ".join(head)
        if max(ctx.graphemes(x) for x in head) > 1.25 * limit or len(head) > MAX_LINES["newspaper"]:
            head = ctx.balance_lines(text, limit, MAX_LINES["newspaper"])
        el["headline"] = head
        el.pop("title", None)
        words = [_norm(x) for x in " ".join(head).split()]
        for m in el.get("marks") or []:
            want = [_norm(x) for x in str((m or {}).get("text") or "").split()]
            if not want or not any(words[i:i + len(want)] == want for i in range(len(words))):
                rep.error(w, "mark \"%s\" is not in the headline" % (m or {}).get("text"))
        rep.ask(w, "a newspaper page: its masthead \"%s\" must be made up, or the headline must be quoted from that "
                   "paper with its source in facts; never put words in a real outlet's mouth" % el.get("masthead"))
    if kind == "chart":
        series = el.get("series")
        good = isinstance(series, list) and 1 <= len(series) <= 3
        clean = []
        if good:
            for s in series:
                vals = s.get("values") if isinstance(s, dict) else None
                try:
                    vals = [float(str(v).replace(",", "")) for v in vals]
                except (TypeError, ValueError):
                    vals = None
                if not vals or len(vals) < 2:
                    good = False
                    break
                clean.append(dict(s, values=vals))
        if not good:
            rep.error(w, "series needs 1 to 3 lines, each {\"name\"?: ..., \"values\": 2 or more numbers}")
            return False
        el["series"] = clean
        xs = el.get("xLabels")
        if xs is not None and (not isinstance(xs, list) or len(xs) != max(len(s["values"]) for s in clean)):
            rep.warn(w, "xLabels should have one label per value")
        if not sourced:
            rep.ask(w, "the chart plots %d values; confirm where they come from (facts with origin brief, client, web "
                       "or formula on this beat)" % sum(len(s["values"]) for s in clean))
    return True


def _place(el, kind, ctx, rep, w):
    """x, y, anchor and width from the slot (or the element's own), for this frame's shape."""
    vertical = ctx.vertical
    W, H, safe = ctx.W, ctx.H, ctx.safe
    slot = el.get("slot") or DEFAULT_SLOT[kind]
    if el.get("x") is None or el.get("y") is None:
        if slot == "credit":
            x, y, anchor = safe["x"] / float(W), (safe["y"] + safe["h"]) / float(H) - (0.03 if not vertical else 0.02), \
                "bottom-left"
        elif slot == "text-left":
            x, y, anchor = safe["x"] / float(W) + (0.03 if not vertical else 0.02), 0.44 if not vertical else 0.3, "left"
        elif slot in SLOTS:
            x, y, anchor = _pick(SLOTS[slot], vertical)
        else:
            rep.error(w, "slot must be one of " + ", ".join(sorted(SLOTS)) + " (or give x and y)")
            x, y, anchor = _pick(SLOTS["center"], vertical)
        if el.get("x") is None:
            el["x"] = x
        if el.get("y") is None:
            # a picture standing on the bottom edge sits a little under it, so its cut-off bottom never shows (a
            # foreground band more: a ragged lower edge would let the people behind it show through)
            sink = {"fore": 0.08, "text": 0.08}.get(el.get("layer") or DEFAULT_LAYER[kind], 0.04)
            el["y"] = y + (sink if kind == "cutout" and anchor == "bottom" and y >= 0.99 else 0)
        el.setdefault("anchor", anchor)
    el.setdefault("anchor", "center")
    el.setdefault("layer", DEFAULT_LAYER[kind])
    grounded = str(el["anchor"]).startswith("bottom") and float(el["y"]) >= 0.95
    if kind == "cutout":
        el.setdefault("enter", "rise" if grounded else "pop")
        if "w" not in el:
            # sized by height: a foreground band (a building, a desk) hides the lower half of the people standing
            # behind it, who stand tall; things floating in the middle are smaller
            aspect = _src_aspect(ctx, el.get("source"))
            if el.get("h") is not None:
                h = float(el["h"])
            elif grounded:
                h = _pick(CUTOUT_H[el["layer"]], vertical)
                if el["layer"] == "fore":
                    # a foreground band spans the frame: wide enough to hide the people behind it, never taller than
                    # about two thirds of the frame
                    h = max(h, min(0.62 if not vertical else 0.3, (0.62 if not vertical else 0.9) * W / (H * aspect)))
            else:
                h = 0.3 if vertical else 0.46
            el["w"] = round(min(0.98 if vertical else 0.92, h * H * aspect / W), 3)
        el.pop("h", None)
        # the cut-out carries its own baked shadow (nvc.py cutout); "soft" or "ground" adds one in the renderer
        el.setdefault("shadow", "none")
    else:
        el.setdefault("enter", DEFAULT_ENTER[kind])
    if kind in DEFAULT_W and "w" not in el:
        el["w"] = _pick(DEFAULT_W[kind], vertical)
    if kind == "clip" and "h" not in el and slot == "floor":
        el["h"] = 0.3 if not vertical else 0.22
    if kind in DEFAULT_SIZE and "size" not in el:
        el["size"] = _pick(DEFAULT_SIZE[kind], vertical)
    if kind == "bubble" and "rotate" not in el:
        el["rotate"] = -6 if float(el["x"]) < 0.5 else 5
    el.pop("slot", None)


def _typewriter_times(el, ctx, span, at):
    """The spoken second of every typed word, when the line is the narration's own words in order."""
    typed = [_norm(x) for x in " ".join(_lines(el)).split() if _norm(x)]
    if not typed:
        return None
    start, end = span
    spoken = []
    for i in range(len(ctx.words)):
        for o in ctx.by_index.get(i) or []:
            if start - 0.5 <= o["start"] <= end + 0.5:
                spoken.append((_norm(ctx.words[i].get("text")), o["start"]))
    spoken.sort(key=lambda x: x[1])
    keys = [s[0] for s in spoken]
    for i in range(len(keys) - len(typed) + 1):
        if keys[i:i + len(typed)] == typed and (at is None or spoken[i][1] >= at - 0.6):
            return [s[1] for s in spoken[i:i + len(typed)]]
    return None


# ---------------------------------------------------------------- bake: frames, exits, sound, layout checks

def bake(o, joined_next, fps, ctx, rep, lang):
    """Turn a prepared beat into renderer props on its final length (after every trim)."""
    p = o["props"]
    els = p.pop("_vox", [])
    f0, dur = o["from"], o["durationInFrames"]
    last_at = 0

    k30 = fps / 30.0

    def fr(t, lo=0, hi=None, lead=0):
        if t is None:
            return None
        v = int(round(t * fps)) - f0 - int(round(lead * k30))
        return max(lo, min(dur if hi is None else hi, v))

    # a beat's exit when it hands the paper to the next beat: its elements drop, fade, slide or shrink away under the
    # next beat's first frames; a cut (the default) needs no tail
    beat_exit = EXIT_OF.get(o.get("exit") or "cut") if joined_next else None
    cues = []
    baked = []
    for n, el in enumerate(els):
        t = el.pop("_t", {})
        bare = set(t.get("bare") or [])
        w = "%s %s (%s)" % (o["id"], el["id"], el["kind"])
        at = fr(t.get("at"), 0, dur - 1, LEAD_IN.get(el.get("enter") or "pop", 8) if "at" in bare else 0)
        if at is None:
            # no word given: in after the element before it (the first one right on the cut)
            at = min(dur - 1, (last_at + 8) if n else 0)
        last_at = at
        el["at"] = at
        for key in ("land", "markAt", "drawAt", "drawEnd"):
            if t.get(key) is not None:
                el[key] = fr(t[key], lead=LEAD.get(key, 0) if key in bare else 0)
        if t.get("out") is not None:
            el["out"] = max(at + 1, fr(t["out"]))
            # leaving while the rest stays: off by the nearest side edge (where its moves took it), not through the
            # other pictures
            last_x = next((float(m["x"]) for m in reversed(el.get("moves") or []) if "x" in m), float(el["x"]))
            el.setdefault("exit", "slideLeft" if last_x < 0.5 else "slideRight")
        elif joined_next:
            # the next beat takes over the paper: a cut by default (the reference cuts between most beats), or the
            # beat's exit played under the next beat's first frames
            el["out"] = dur
            el.setdefault("exit", beat_exit or "cut")
        elif o.get("exit") == "drop":
            el["out"] = dur - VOX_EXIT          # everything falls away, then the cut
            el.setdefault("exit", "drop")
        else:
            el["out"] = None                    # stays to the cut (or under a light leak)
        if isinstance(el.get("callout"), dict):
            el["callout"] = dict(el["callout"])
            if t.get("callout") is not None:
                el["callout"]["at"] = fr(t["callout"], lead=LEAD["callout"] if "callout" in bare else 0)
        if isinstance(el.get("marks"), list):
            times = t.get("marks") or [None] * len(el["marks"])
            el["marks"] = [dict(m, at=fr(ts, lead=LEAD["marks"] if "marks" in bare else 0) if ts is not None
                                else at + 12) for m, ts in zip(el["marks"], times) if isinstance(m, dict)]
        if isinstance(el.get("moves"), list):
            moves = []
            for m, ts in zip(el["moves"], t.get("moves") or []):
                if ts is None:
                    continue
                mv = {k: m[k] for k in ("x", "y", "scale", "rotate", "frames") if k in m}
                mv["at"] = fr(ts, lead=LEAD["moves"] if "moves" in bare else 0)
                moves.append(mv)
            el["moves"] = sorted(moves, key=lambda m: m["at"])
        if el["kind"] == "typewriter":
            times = t.get("times")
            words = " ".join(el["lines"]).split()
            if times and len(times) == len(words):
                el["times"] = [fr(x) for x in times]
                el["at"] = el["times"][0]
            else:
                step = max(4, int(round(0.28 * fps)))
                el["times"] = [el["at"] + i * step for i in range(len(words))]
        if el["kind"] == "tag" and el.get("land") is None:
            el["land"] = min(dur, el["at"] + int(round(1.5 * fps)))
        if el["kind"] == "chart":
            if el.get("drawAt") is None:
                el["drawAt"] = el["at"] + 8
            if el.get("drawEnd") is None:
                el["drawEnd"] = min(dur, el["drawAt"] + int(round(1.8 * fps)))
        if el["kind"] == "headline" and el.get("count") and el.get("land") is None:
            el["land"] = min(dur, el["at"] + int(round(1.2 * fps)))
        shown_for = (el["out"] if el.get("out") is not None else dur) - el["at"]
        if el["kind"] in TEXT_KINDS and el["kind"] != "credit":
            text = _element_text(el)
            need = ctx.reading_time(text, lang) if text else 0
            if el["kind"] == "typewriter":
                need = 0.8 + (el["times"][-1] - el["at"]) / float(fps)
            if shown_for < need * fps * 0.9:
                rep.warn(w, "on screen %.1f s; its words need about %.1f s to read: bring it in earlier or keep it "
                            "longer" % (shown_for / float(fps), need))
        cues += _cues(el, fps)
        baked.append(el)
    _check_layout(o, baked, ctx, rep, dur)
    _check_rhythm(o, baked, ctx, rep, dur, fps)
    p["elements"] = baked
    p["tail"] = VOX_EXIT if joined_next and any(e.get("out") == dur and e.get("exit") != "cut" for e in baked) else 0
    if any(e["kind"] == "typewriter" for e in baked) and "hideCaptions" not in p:
        # the typed line is on screen already: captions would say it twice
        p["hideCaptions"] = True
    cues.sort(key=lambda c: c["at"])
    kept = []
    gap = max(3, int(round(0.2 * fps)))
    for c in cues:
        if c["at"] >= dur + p["tail"]:
            continue
        # two cues within a fifth of a second blur into one; a typewriter's keys are small and all stay
        if c["name"] != "key" and any(abs(c["at"] - k["at"]) < gap and k["name"] != "key" for k in kept):
            continue
        kept.append(c)
    for c in kept:
        c["gain_db"] = CUE_GAIN.get(c["name"])
    p["cues"] = kept
    return p


def _check_rhythm(o, els, ctx, rep, dur, fps):
    """Something new every few seconds inside a beat, and no full sentence on screen that the voice is saying."""
    moments = sorted({0, dur} | {e["at"] for e in els} | {m["at"] for e in els for m in e.get("moves") or []}
                     | {m["at"] for e in els for m in e.get("marks") or []}
                     | {e[k] for e in els for k in ("land", "markAt") if e.get(k) is not None}
                     | {e["callout"]["at"] for e in els if isinstance(e.get("callout"), dict)
                        and e["callout"].get("at") is not None})
    for a, b in zip(moments, moments[1:]):
        if (b - a) / float(fps) > QUIET_S and not any(e["kind"] in ("typewriter", "chart", "clip") and
                                                      e["at"] <= a < (e.get("out") or dur) for e in els):
            rep.warn(o["id"], "nothing new on screen for %.1f s (%.1f to %.1f s into the beat): add a mark, a label, a "
                     "move or the next picture on a word in between" % ((b - a) / float(fps), a / float(fps),
                                                                         b / float(fps)))
            break
    spoken = set()
    for i in range(len(ctx.words)):
        for occ in ctx.by_index.get(i) or []:
            if o["from"] / float(fps) - 0.5 <= occ["start"] <= (o["from"] + dur) / float(fps) + 0.5:
                spoken.add(_norm(ctx.words[i].get("text")))
    for e in els:
        if e["kind"] in ("headline", "label", "bubble"):
            ws = [_norm(x) for x in _element_text(e).split() if _norm(x)]
            if len(ws) >= 7 and sum(1 for x in ws if x in spoken) >= 0.85 * len(ws):
                rep.warn("%s %s" % (o["id"], e["id"]), "a full sentence on screen repeats the voice: show the key "
                         "words or the number (the typewriter is the one place for a spoken line)")


def _element_text(el):
    kind = el["kind"]
    if kind in ("headline", "bubble", "typewriter"):
        return " ".join(el.get("lines") or [])
    if kind == "tag":
        return "%s %s" % (el.get("value") or "", el.get("unit") or "")
    return str(el.get("text") or "")


def _cues(el, fps):
    if el.get("sfx") is False:
        return []
    kind, at = el["kind"], el["at"]
    if isinstance(el.get("sfx"), str):
        return [{"at": at, "name": el["sfx"]}]
    if kind == "typewriter":
        return [{"at": t, "name": "key"} for t in el.get("times") or []]
    out = []
    name = KIND_SOUND[kind] if kind in KIND_SOUND else SOUND.get(el.get("enter") or "pop")
    if kind == "cutout" and el.get("enter") == "rise" and float(el.get("w") or 0) >= 0.5:
        name = "whoosh-short"      # a building coming up is bigger than a flick
    if name:
        out.append({"at": at, "name": name})
    if kind == "tag" and el.get("land") is not None:
        out.append({"at": el["land"], "name": "ding"})
    if kind == "headline" and el.get("count") and el.get("land") is not None:
        out.append({"at": el["land"], "name": "impact"})
    if kind == "chart" and isinstance(el.get("callout"), dict) and el["callout"].get("at") is not None:
        out.append({"at": el["callout"]["at"], "name": "pop"})
    for m in el.get("marks") or []:
        out.append({"at": m["at"], "name": "swipe"})
    return out


def _box(el, ctx):
    """An estimate of a text element's box on the frame, in px: (left, top, right, bottom)."""
    W, H = ctx.W, ctx.H
    u = min(W, H) / 1080.0
    kind = el["kind"]
    size = float(el.get("size") or 50) * u
    per = PER_CHAR.get(kind, 0.6)
    g = ctx.graphemes
    if kind in ("headline", "bubble", "typewriter"):
        lines = el.get("lines") or [""]
        w_ = max(g(x) for x in lines) * per * size
        if kind == "headline":
            cap = float(el.get("w") or 0.8) * W
            if w_ > cap:
                size *= cap / w_
                w_ = cap
        h_ = len(lines) * size * (1.62 if kind == "typewriter" else 1.05)
        if kind == "bubble":
            w_, h_ = w_ * 1.44 + 60 * u, h_ * 1.44 + 52 * u
    elif kind == "tag":
        w_ = g(str(el.get("value") or "")) * per * size + (size * 0.75 if el.get("icon") not in (None, "none") else 0)
        h_ = size * (1.45 if el.get("unit") else 1.05)
    else:
        w_ = g(str(el.get("text") or "")) * per * size
        h_ = size * 1.25
    ax, ay = {"bottom": (-0.5, -1), "top": (-0.5, 0), "center": (-0.5, -0.5), "left": (0, -0.5), "right": (-1, -0.5),
              "bottom-left": (0, -1), "bottom-right": (-1, -1), "top-left": (0, 0), "top-right": (-1, 0)}.get(
        el.get("anchor") or "center", (-0.5, -0.5))
    x, y = float(el["x"]) * W, float(el["y"]) * H
    left, top = x + ax * w_, y + ay * h_
    return left, top, left + w_, top + h_


def _nudge(b, safe):
    """How far to move a box (dx, dy in px) so it sits inside the safe area, or None when it is bigger than it."""
    x0, y0, x1, y1 = safe["x"], safe["y"], safe["x"] + safe["w"], safe["y"] + safe["h"]
    if b[2] - b[0] > x1 - x0 or b[3] - b[1] > y1 - y0:
        return None
    dx = (x0 - b[0]) if b[0] < x0 else (x1 - b[2]) if b[2] > x1 else 0
    dy = (y0 - b[1]) if b[1] < y0 else (y1 - b[3]) if b[3] > y1 else 0
    return dx, dy


def _follow_points(target, fps, dur, W, H):
    """Where a followed element's point is at the start and the end of its drift (share of the frame)."""
    x, y = float(target["x"]), float(target["y"])
    d = target.get("drift") or {}
    secs = max(0.0, (dur - target["at"]) / float(fps))
    return [(x, y), (x + float(d.get("x") or 0) * secs, y + float(d.get("y") or 0) * secs)]


def _check_layout(o, els, ctx, rep, dur):
    safe = ctx.safe
    W, H = ctx.W, ctx.H
    byid = {e["id"]: e for e in els}
    boxes = {}
    for el in els:
        if el["kind"] not in TEXT_KINDS:
            continue
        where = "%s %s (%s)" % (o["id"], el["id"], el["kind"])
        if el.get("follow") and el["follow"] in byid:
            # a tag riding on a moving picture: keep it inside at both ends of the ride
            pts = _follow_points(byid[el["follow"]], ctx.fps, dur, W, H)
            moves = []
            for px, py in pts:
                probe = dict(el, x=px + float(el.get("dx") or 0), y=py + float(el.get("dy") or 0))
                moves.append(_nudge(_box(probe, ctx), safe))
            if any(m is None for m in moves):
                rep.warn(where, "is bigger than the safe area: shorten it")
                continue
            mx = max((m[0] for m in moves), key=abs)
            my = max((m[1] for m in moves), key=abs)
            if mx or my:
                el["dx"] = round(float(el.get("dx") or 0) + mx / W, 4)
                el["dy"] = round(float(el.get("dy") or 0) + my / H, 4)
                rep.decisions.append({"kind": "vox_nudge", "ref": "%s %s" % (o["id"], el["id"]),
                                      "why": "kept inside the safe area as it follows %s" % el["follow"]})
            continue
        b = _box(el, ctx)
        m = _nudge(b, safe)
        if m is None:
            rep.warn(where, "is bigger than the safe area (%.0f x %.0f px): shorten it" % (b[2] - b[0], b[3] - b[1]))
        elif m != (0, 0):
            el["x"] = round(float(el["x"]) + m[0] / W, 4)
            el["y"] = round(float(el["y"]) + m[1] / H, 4)
            b = _box(el, ctx)
            rep.decisions.append({"kind": "vox_nudge", "ref": "%s %s" % (o["id"], el["id"]),
                                  "why": "moved %+.0f, %+.0f px to stay inside the safe area" % m})
        boxes[el["id"]] = b

    def live(e):
        return e["at"], (e["out"] if e.get("out") is not None else dur)
    for i, a in enumerate(els):
        for b in els[i + 1:]:
            if a["id"] not in boxes or b["id"] not in boxes:
                continue
            (a0, a1), (b0, b1) = live(a), live(b)
            if a1 <= b0 or b1 <= a0:
                continue
            A, B = boxes[a["id"]], boxes[b["id"]]
            if min(A[2], B[2]) - max(A[0], B[0]) > 8 and min(A[3], B[3]) - max(A[1], B[1]) > 8:
                rep.warn("%s %s" % (o["id"], a["id"]), "its text overlaps %s's while both are on screen: give one "
                         "another slot" % b["id"])
    for el in els:
        now = [e for e in els if e["at"] <= el["at"] < live(e)[1]]
        if len(now) > MAX_AT_ONCE:
            rep.warn("%s %s" % (o["id"], el["id"]), "%d elements are on screen at once; a viewer follows 3 to 5"
                     % len(now))
            break


# ---------------------------------------------------------------- the storyboard for the brief

def storyboard(words, lang="en"):
    """The narration as beats for a vox plan: sentences (clauses, when a sentence runs long) grouped into beats of
    about 3 to 9 s, each with its word ids, times and text. One beat is one composition on the paper."""
    units, cur = [], []
    for w in words:
        cur.append(w)
        text = str(w.get("text") or "")
        long_enough = cur and (w["end"] - cur[0]["start"]) >= 6.0
        if re.search(r"[.!?।॥…]['\")\]]*$", text) or (long_enough and re.search(r"[,;:–]$", text)):
            units.append(cur)
            cur = []
    if cur:
        units.append(cur)
    beats, acc = [], []
    for u in units:
        if acc and (u[-1]["end"] - acc[0]["start"] > 9.0 or acc[-1]["end"] - acc[0]["start"] >= 3.0):
            beats.append(acc)
            acc = []
        acc = acc + u
    if acc:
        if beats and acc[-1]["end"] - acc[0]["start"] < 2.0:
            beats[-1] = beats[-1] + acc
        else:
            beats.append(acc)
    rows = []
    for b in beats:
        rows.append({"first": b[0]["id"], "last": b[-1]["id"], "start": b[0]["start"], "end": b[-1]["end"],
                     "text": " ".join(str(w.get("text") or "") for w in b)})
    return rows


def brief_lines(words, job, preset, lang="en"):
    """The Vox part of edit-brief.md: the look, the rules, the pictures in the job, the element kinds and the
    storyboard, so the plan can be written with no guesswork."""
    vertical = preset["height"] > preset["width"]
    src = job.get("sources") or {}
    cut = [(k, v) for k, v in src.items() if v.get("kind") == "cutout"]
    keyed = [(k, v) for k, v in src.items() if v.get("keyed")]
    other = [(k, v) for k, v in src.items() if k not in dict(cut) and k not in dict(keyed)
             and (v.get("image") or v.get("proxy")) and v.get("kind") not in ("voice", "music")]
    out = ["## Vox beats (the explainer look)", "",
           "One locked paper ground for the whole run: warm grey paper, a faint grid, grain. Each beat is one "
           "composition on it, grounded to its words, and a cut between beats (the default) swaps the pictures while "
           "the paper stays, so the video reads as one continuous shot. Layers from the back: `back`, `mid` "
           "(people: black and white halftone with the red marker stroke), `fore` (a colour foreground band, a "
           "building or a desk, that hides the people's lower halves), `text` (headlines, labels, tags, bubbles).",
           "",
           "- One anchor picture per beat, then one new thing at a time, about a second apart, each on the word it "
           "shows (a bare word id makes it land just before the word).",
           "- Something new every 2 to 4 s inside a beat (a label, a mark, a move, the next picture): the compiler "
           "warns after 5 s with nothing new.",
           "- Key words and numbers on screen, never the sentence being said (the typewriter is the one place for a "
           "spoken line, as a closer). Every number on screen is said, or sourced in the beat's facts.",
           "- Pictures come from the job: `nvc.py stock JOB \"words\" --type photo`, `nvc.py cutout JOB ID` (people "
           "become halftone with the marker stroke, objects stay in colour), `nvc.py key JOB ID` for fire, smoke or "
           "sparks shot on black, or a green screen. Never a real person's face made by AI; stock people never in "
           "political, health, dating, drug or adult contexts (Pixabay).",
           "- A newspaper gets a made-up masthead, unless the headline is quoted from that paper with its source.",
           "- Beat exits: `cut` (default), `drop`, `fade`, `slide`, `pop` (played under the next beat), `leak` (warm "
           "light over the cut, for the way out to a camera or the end).",
           "- `progress_bar: \"bottom\"` draws the explainer's thick orange bar.",
           "",
           "Elements (`elements` of a `vox` overlay; times are word ids, `w0012.end`, `w0012+0.3`, seconds from the "
           "beat's start, `start` or `end`; places are a `slot` or `x`/`y` shares of the frame):",
           "",
           "- `cutout{source, slot?, layer?, h?|w?, enter?, drift?{x,y}, moves?[], shadow?: none|soft|ground}`",
           "- `clip{source, slot? (floor: a band along the bottom), h?, feather?{top,...}, blend?}`",
           "- `card{source, caption?, bw?}`: a photo as a print",
           "- `headline{text|lines, highlight?, mark?, markAt?, count?, land?}`",
           "- `label{text, caps?, box?, size?}`, `credit{text}` (the source line, bottom left)",
           "- `tag{value, from?, unit?, icon?, land?, follow?, dx?, dy?}`: a price or number that counts and lands on "
           "its word; `follow` rides on a moving picture",
           "- `bubble{text|lines, highlight?, tail?}`: comic speech bubble near a speaker",
           "- `newspaper{masthead, headline, marks?[{text, at}], deck?, byline?, section?, left?[], right?[], body?}`",
           "- `chart{title, series[{name?, values[]}], xLabels?, yPrefix?, ySuffix?, drawAt?, drawEnd?, "
           "callout?{text[], at, index?}, note?}` (plus facts)",
           "- `typewriter{text|lines}`: typed word by word as it is said",
           "- `scribble{shape: circle|underline|arrow|cross|box, w?, h?}`, `icon{icon}`",
           "- All: `id`, `at`, `out?`, `enter?` (rise, pop, slideLeft, slideRight, drop, wipe, fade, none), `exit?`, "
           "`moves?[{at, x?, y?, slot?, scale?, rotate?}]`, `layer?`, `anchor?`, `rotate?`, `float?`, `sfx?`",
           "- Slots: %s (vertical frames keep text in the top half and stand pictures on the bottom edge)."
           % ", ".join(sorted(SLOTS)),
           ""]
    out += ["Pictures and clips in this job:", ""]
    if not (cut or keyed or other):
        out.append("- none yet: search stock, then cut out and key")
    for k, v in cut:
        c = v.get("cutout") or {}
        out.append("- `%s`: cut-out, %s%s, %sx%s%s" % (
            k, c.get("style", "?"), " + marker stroke" if c.get("stroke") not in (None, "none") else "",
            v.get("width"), v.get("height"), ", %d person(s)" % v["people"] if v.get("people") else ""))
    for k, v in keyed:
        out.append("- `%s`: keyed clip (transparent), %sx%s, %s s" % (k, v.get("width"), v.get("height"),
                                                                   round(float(v.get("duration") or 0), 1)))
    for k, v in other[:30]:
        out.append("- `%s`: %s, %sx%s%s" % (k, v.get("kind"), v.get("width"), v.get("height"),
                                            ", %s s" % round(float(v["duration"]), 1) if v.get("duration") else ""))
    out += ["", "Storyboard (suggested beats; merge or split as the pictures need):", "",
            "| Beat | Words | Time | Line | Anchor picture | Then, on which words | Facts |",
            "|---|---|---|---|---|---|---|"]
    for i, r in enumerate(storyboard(words, lang)):
        out.append("| %d | %s-%s | %.1f-%.1f s | %s |  |  |  |" % (i + 1, r["first"], r["last"], r["start"], r["end"],
                                                                 r["text"].replace("|", "/")))
    out += ["", "Example beat:", "", "```json", json.dumps(VOX_EXAMPLE, ensure_ascii=False, indent=1), "```", ""]
    return out


VOX_EXAMPLE = {"type": "vox", "words": ["w0034", "w0040"], "quote": "Oil prices skyrocketed to $116 a barrel,",
               "exit": "cut",
               "elements": [
                   {"id": "sea", "kind": "clip", "source": "sea", "slot": "floor", "layer": "fore",
                    "feather": {"top": 0.3}, "at": "start"},
                   {"id": "ship", "kind": "cutout", "source": "tanker-cut", "x": 0.36, "y": 0.86, "anchor": "bottom",
                    "w": 0.62, "enter": "slideRight", "drift": {"x": 0.008}, "at": "start"},
                   {"id": "price", "kind": "tag", "value": "$116", "from": 25, "unit": "per barrel", "icon": "barrel",
                    "at": "w0034", "land": "w0038", "follow": "ship", "dx": 0.3, "dy": -0.5},
                   {"id": "src", "kind": "credit", "text": "Source: EIA, 2026", "at": "w0038"}]}

