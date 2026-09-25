"""Plan verification and compilation for nexa-video-creator (standard library only).

Claude writes the edit as a plan (nvc-plan/1) grounded to transcript word ids and verbatim quotes. This module checks
the plan against the transcript and the editing rules, then compiles it into a renderer-ready edit decision list
(nvc-edl/1): frame-exact clips, overlays, zooms, captions, chapters, sound-effect cues and the speech spans that
drive music ducking. It never invents a time: every time comes from measured word edges, and every cut lands on the
frame grid of the output.

Rules come from references/editing-rules.md (research 01 and 04, 2026-09-25): 50 ms kept before the first word and
80 ms after the last, no cut inside a pause under 150 ms, long pauses trimmed to the target's length, text on screen
for at least clamp(0.35 x words + 0.5, 0.83, 7) seconds, shown numbers must be in the grounded quote, and so on.
"""
import bisect
import difflib
import math
import re
import unicodedata

PLAN_SCHEMA = "nvc-plan/1"
EDL_SCHEMA = "nvc-edl/1"
PAD_BEFORE = 0.05
PAD_AFTER = 0.08
MIN_CUT_PAUSE = 0.15
LAYOUTS = ("camFull", "screenFull", "screenPip", "split", "stack", "brollFull", "voiceOnly")
TRANSITIONS = ("cut", "zoom", "whip", "dip", "flash")
CAMERA_KINDS = ("camera", "talking_head", "phone_clip")
SCREEN_KINDS = ("screen", "screen_recording", "screen_with_cam", "slides")
MEDIA_KINDS = ("broll", "b_roll", "image", "segment", "camera", "talking_head", "screen", "screen_recording", "logo")
FILLERS = {"um", "uh", "uhm", "umm", "er", "erm", "ah", "hmm", "mm", "mhm",
           "উম", "উমম", "আ", "অ্যাঁ", "হুম", "উঁ", "এ"}
DISCOURSE = {"like", "basically", "actually", "literally", "so", "right", "you know", "i mean",
             "মানে", "আসলে", "তো", "আচ্ছা", "ইয়ে", "আরকি", "বুঝলেন", "বুঝছেন", "বুঝলা", "তাই না", "ঠিক আছে"}
TEXT_PROPS = {"hook": ["text"], "keyword": ["text"], "stat": ["value", "label"], "list": ["items"],
              "compare": ["left", "right"], "quote": ["text"], "chapter": ["title"], "lowerThird": ["name"],
              "callout": [], "redact": [], "broll": [], "image": [], "segment": [], "cta": ["text"], "progress": []}
BN_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
NUMBER_WORDS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
                "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
                "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
                "thousand": 1000, "million": 1000000, "billion": 1000000000, "percent": None}


class Report:
    """Errors stop the compile; warnings and review items are shown to the editor and kept in the EDL."""

    def __init__(self):
        self.errors, self.warnings, self.review, self.decisions = [], [], [], []

    def error(self, where, msg):
        self.errors.append("%s: %s" % (where, msg))

    def warn(self, where, msg):
        self.warnings.append("%s: %s" % (where, msg))

    def ask(self, where, msg):
        self.review.append("%s: %s" % (where, msg))

    def as_dict(self):
        return {"ok": not self.errors, "errors": self.errors, "warnings": self.warnings, "review": self.review,
                "decisions": self.decisions}


# ---------------------------------------------------------------- text helpers

def is_bengali(text):
    return any("ঀ" <= ch <= "৿" for ch in text or "")


def graphemes(text):
    """Visible characters: combining marks, the virama and joiners do not count (Bengali conjuncts)."""
    count = 0
    for ch in text or "":
        if unicodedata.category(ch) in ("Mn", "Mc", "Me") or ch in ("্", "‌", "‍"):
            continue
        count += 1
    return count


def norm_text(text):
    """Lower case, Bengali digits folded, punctuation and symbols dropped, spaces collapsed (for quote checks)."""
    text = unicodedata.normalize("NFC", str(text or "")).translate(BN_DIGITS).lower()
    kept = []
    for ch in text:
        cat = unicodedata.category(ch)
        kept.append(" " if cat[0] in ("P", "S", "Z") and ch not in ("%",) else ch)
    return " ".join("".join(kept).split())


def word_count(text):
    return len([t for t in re.split(r"\s+", str(text or "").strip()) if t])


def reading_time(text, lang=None):
    """Seconds a line must stay on screen: clamp(0.35 x words + 0.5, 0.83, 7), and never under characters / cps
    (20 for English, 22 for Bangla)."""
    text = str(text or "")
    base = min(max(0.35 * word_count(text) + 0.5, 0.83), 7.0)
    cps = 22.0 if (lang or "").startswith("bn") or is_bengali(text) else 20.0
    return max(base, graphemes(text) / cps)


BN_NUMBER_WORDS = (
    "শূন্য এক দুই তিন চার পাঁচ ছয় সাত আট নয় দশ এগারো বারো তেরো চৌদ্দ পনেরো ষোলো সতেরো আঠারো উনিশ বিশ একুশ বাইশ তেইশ "
    "চব্বিশ পঁচিশ ছাব্বিশ সাতাশ আটাশ ঊনত্রিশ ত্রিশ একত্রিশ বত্রিশ তেত্রিশ চৌত্রিশ পঁয়ত্রিশ ছত্রিশ সাঁইত্রিশ আটত্রিশ ঊনচল্লিশ "
    "চল্লিশ একচল্লিশ বিয়াল্লিশ তেতাল্লিশ চুয়াল্লিশ পঁয়তাল্লিশ ছেচল্লিশ সাতচল্লিশ আটচল্লিশ ঊনপঞ্চাশ পঞ্চাশ একান্ন বাহান্ন "
    "তিপ্পান্ন চুয়ান্ন পঞ্চান্ন ছাপ্পান্ন সাতান্ন আটান্ন ঊনষাট ষাট একষট্টি বাষট্টি তেষট্টি চৌষট্টি পঁয়ষট্টি ছেষট্টি সাতষট্টি "
    "আটষট্টি ঊনসত্তর সত্তর একাত্তর বাহাত্তর তিয়াত্তর চুয়াত্তর পঁচাত্তর ছিয়াত্তর সাতাত্তর আটাত্তর ঊনআশি আশি একাশি বিরাশি "
    "তিরাশি চুরাশি পঁচাশি ছিয়াশি সাতাশি আটাশি ঊননব্বই নব্বই একানব্বই বিরানব্বই তিরানব্বই চুরানব্বই পঁচানব্বই ছিয়ানব্বই "
    "সাতানব্বই আটানব্বই নিরানব্বই").split()
BN_NUMBERS = {w: float(i) for i, w in enumerate(BN_NUMBER_WORDS)}
BN_NUMBERS.update({"একশো": 100.0, "একশ": 100.0, "দুইশো": 200.0, "দুশো": 200.0, "তিনশো": 300.0, "চারশো": 400.0,
                   "পাঁচশো": 500.0, "ছয়শো": 600.0, "সাতশো": 700.0, "আটশো": 800.0, "নয়শো": 900.0})
BN_SCALES = {"শো": 100, "শত": 100, "হাজার": 1000, "লাখ": 100000, "লক্ষ": 100000, "কোটি": 10000000}
BN_SUFFIXES = ("টি", "টা", "জন", "খানা", "েই", "ই", "ের", "র", "ে")


def _bn_number_value(token):
    for cand in [token] + [token[:-len(s)] for s in BN_SUFFIXES if token.endswith(s) and len(token) > len(s) + 1]:
        if cand in BN_NUMBERS:
            return BN_NUMBERS[cand]
    return None


def numbers_in(text):
    """Numbers a line states, as floats: digits in either script, English number words, and Bangla number words
    (0 to 99, the hundreds, and হাজার, লাখ, কোটি)."""
    raw_text = str(text or "")
    found = set()
    total = current = 0.0
    seen = False
    for token in re.findall(r"[ঀ-৿]+", raw_text):
        value = _bn_number_value(token)
        if value is not None:
            current += value
            seen = True
        elif token in BN_SCALES and seen:
            scale = BN_SCALES[token]
            if scale == 100:
                current = max(current, 1) * 100
            else:
                total += max(current, 1) * scale
                current = 0.0
        elif seen:
            found.add(total + current)
            total = current = 0.0
            seen = False
    if seen:
        found.add(total + current)
    text = raw_text.translate(BN_DIGITS).lower()
    for match in re.finditer(r"\d+(?:[.,]\d+)*", text):
        raw = match.group(0)
        compact = raw.replace(",", "")
        try:
            found.add(float(compact))
        except ValueError:
            pass
    total, current, seen = 0, 0, False
    for token in re.findall(r"[a-z]+", text):
        if token in NUMBER_WORDS and NUMBER_WORDS[token] is not None:
            value = NUMBER_WORDS[token]
            seen = True
            if value == 100:
                current = max(current, 1) * 100
            elif value >= 1000:
                total += max(current, 1) * value
                current = 0
            else:
                current += value
        elif seen:
            found.add(float(total + current))
            total, current, seen = 0, 0, False
    if seen:
        found.add(float(total + current))
    return found


LABEL_WORDS = r"(?:step|part|story|chapter|episode|tip|day|lesson|level|round|phase|no\.?|#|ধাপ|পর্ব|অধ্যায়|দিন|টিপ|লেসন)"


def label_numbers(text):
    """Numbers that only count things on screen ("Step 2", "Part 3", "পর্ব ২"): labels, not claims, so the
    said-numbers check leaves them alone."""
    found = set()
    for m in re.finditer(LABEL_WORDS + r"\s*([0-9\u09e6-\u09ef]{1,2})\b", str(text or "").lower()):
        try:
            found.add(float(m.group(1).translate(BN_DIGITS)))
        except ValueError:
            pass
    return found


def ends_sentence(text):
    return bool(re.search(r"[.!?।॥…]['\")\]]*$", str(text or "").strip()))


def is_filler(word_text):
    return norm_text(word_text) in FILLERS


# ---------------------------------------------------------------- words and grounding

def index_words(words):
    return {w["id"]: i for i, w in enumerate(words)}


def span_text(words, i0, i1):
    return " ".join(str(words[k].get("text", "")).strip() for k in range(i0, i1 + 1))


def resolve_span(item, words, idx, rep, where, need_quote=True):
    """(first index, last index) for an item's `words`, or None with an error. The quote must match the span."""
    ids = item.get("words")
    if not isinstance(ids, (list, tuple)) or len(ids) != 2:
        rep.error(where, "needs \"words\": [first_id, last_id]")
        return None
    first, last = ids
    if first not in idx or last not in idx:
        missing = [x for x in (first, last) if x not in idx]
        rep.error(where, "unknown word id %s" % ", ".join(str(m) for m in missing))
        return None
    i0, i1 = idx[first], idx[last]
    if i1 < i0:
        rep.error(where, "words run backwards (%s after %s)" % (first, last))
        return None
    quote = item.get("quote")
    actual = span_text(words, i0, i1)
    if quote is None:
        if need_quote:
            rep.error(where, "needs a verbatim \"quote\" of %s..%s: \"%s\"" % (first, last, _clip_text(actual)))
            return None
        return i0, i1
    if norm_text(quote) != norm_text(actual):
        ratio = difflib.SequenceMatcher(None, norm_text(quote), norm_text(actual)).ratio()
        rep.error(where, "quote does not match %s..%s (%.0f%% alike). The transcript says: \"%s\""
                  % (first, last, ratio * 100, _clip_text(actual)))
        return None
    return i0, i1


def _clip_text(text, limit=160):
    return text if len(text) <= limit else text[:limit] + "..."


# ---------------------------------------------------------------- transcript views for the brief

def pack_transcript(words, pause=0.5):
    """One line per phrase, broken at pauses of `pause` s or more and at sentence ends:
    `[w0012-w0021] 16.21-19.30  Sixty two percent of viewers leave.`"""
    lines, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        nxt = words[i + 1] if i + 1 < len(words) else None
        gap = (nxt["start"] - w["end"]) if nxt else 99
        if gap >= pause or ends_sentence(w.get("text", "")) or len(cur) >= 24:
            a, b = words[cur[0]], words[cur[-1]]
            lines.append("[%s-%s] %.2f-%.2f  %s%s" % (a["id"], b["id"], a["start"], b["end"],
                                                     span_text(words, cur[0], cur[-1]),
                                                     ("   (pause %.2f s)" % gap) if 0.7 <= gap < 99 else ""))
            cur = []
    return lines


def find_fillers(words):
    out = []
    for i, w in enumerate(words):
        text = norm_text(w.get("text", ""))
        prev_gap = w["start"] - words[i - 1]["end"] if i > 0 else 1.0
        next_gap = words[i + 1]["start"] - w["end"] if i + 1 < len(words) else 1.0
        if text in FILLERS:
            out.append({"id": w["id"], "text": w["text"], "kind": "filled_pause",
                        "bounded": prev_gap >= 0.1 or next_gap >= 0.1, "t": w["start"]})
        elif text in DISCOURSE:
            out.append({"id": w["id"], "text": w["text"], "kind": "discourse_marker", "bounded": False,
                        "t": w["start"]})
    return out


def find_retakes(words, window_s=10.0, n=3):
    """Phrases of n or more words said again within window_s: likely a restart; the editor keeps one."""
    toks = [norm_text(w.get("text", "")) for w in words]
    seen, out = {}, []
    for i in range(len(words) - n + 1):
        key = " ".join(toks[i:i + n])
        if not key.strip() or any(t in FILLERS for t in toks[i:i + n]):
            continue
        if key in seen:
            j = seen[key]
            if 0 < words[i]["start"] - words[j]["start"] <= window_s and i - j >= n:
                out.append({"first": words[j]["id"], "again": words[i]["id"], "phrase": key,
                            "t_first": words[j]["start"], "t_again": words[i]["start"]})
        seen[key] = i
    return out


def find_numbers(words):
    out = []
    for w in words:
        if numbers_in(w.get("text", "")):
            out.append({"id": w["id"], "text": w["text"], "t": w["start"]})
    return out


# ---------------------------------------------------------------- sources and sync

def other_time(sync, t_ref):
    """Where master time t_ref is found in a synced source (segments from nvc_sync.py)."""
    if not sync:
        return t_ref
    segs = sync.get("segments") or [{"t_ref_from": 0, "t_ref_to": 1e12, "offset_s": sync.get("offset_s", 0.0),
                                     "drift_ppm": sync.get("drift_ppm")}]
    best = min(segs, key=lambda s: 0 if s["t_ref_from"] <= t_ref <= s["t_ref_to"]
               else min(abs(t_ref - s["t_ref_from"]), abs(t_ref - s["t_ref_to"])))
    return best["offset_s"] + (1 + (best.get("drift_ppm") or 0) / 1e6) * t_ref


def source_time(job, source_id, t_master):
    if source_id == job.get("dialogue"):
        return t_master
    src = job["sources"][source_id]
    return other_time(src.get("sync"), t_master)


def ready(src):
    """A source the renderer can draw: it has a proxy (video) or is an image."""
    return bool(src.get("proxy") or src.get("image"))


def pick_sources(job):
    cams = [k for k, s in job["sources"].items() if (s.get("kind") in CAMERA_KINDS or s.get("role") == "camera")
            and s.get("hasVideo", True) and ready(s)]
    screens = [k for k, s in job["sources"].items()
               if (s.get("kind") in SCREEN_KINDS or s.get("role") == "screen") and ready(s)]
    return cams, screens


# ---------------------------------------------------------------- pieces (what is kept, in output order)

class Piece:
    def __init__(self, m_in, m_out, seg, words=None, timed=False):
        self.m_in, self.m_out, self.seg, self.timed = m_in, m_out, seg, timed
        self.words = words or []
        self.f_in = self.f_out = self.out_from = 0

    def frames(self):
        return self.f_out - self.f_in


def build_pieces(plan, words, idx, rep, trim_above, target_pause, dialogue_duration, auto_fillers=True):
    removed = set()
    for n, item in enumerate(plan.get("remove") or []):
        sp = resolve_span(item, words, idx, rep, "remove[%d]" % n)
        if sp:
            removed.update(range(sp[0], sp[1] + 1))
            rep.decisions.append({"kind": "cut_" + str(item.get("kind") or "other"), "words": item["words"],
                                  "quote": item.get("quote")})
    holds = {}
    for n, item in enumerate(plan.get("holds") or []):
        sp = resolve_span(item, words, idx, rep, "holds[%d]" % n)
        if sp:
            holds[sp[1]] = float(item.get("seconds") or 0.8)
    seg_spans = []
    for n, seg in enumerate(plan.get("segments") or []):
        where = "segments[%d]" % n
        if "words" in seg:
            sp = resolve_span(seg, words, idx, rep, where)
            seg_spans.append(sp)
        elif "from" in seg and "to" in seg:
            seg_spans.append(("timed", float(seg["from"]), float(seg["to"])))
        else:
            rep.error(where, "needs \"words\" (with a quote) or \"from\" and \"to\" seconds on the master clock")
            seg_spans.append(None)
    if auto_fillers and plan.get("auto_fillers", True):
        inside = set()
        for sp in seg_spans:
            if sp and sp[0] != "timed":
                inside.update(range(sp[0], sp[1] + 1))
        for i in sorted(inside):
            w = words[i]
            if i in removed or not is_filler(w.get("text", "")):
                continue
            prev_gap = w["start"] - words[i - 1]["end"] if i > 0 else 1.0
            next_gap = words[i + 1]["start"] - w["end"] if i + 1 < len(words) else 1.0
            if prev_gap >= 0.1 or next_gap >= 0.1:
                removed.add(i)
                rep.decisions.append({"kind": "cut_filler", "words": [w["id"], w["id"]], "quote": w["text"],
                                      "auto": True})
    pieces = []
    for si, sp in enumerate(seg_spans):
        if sp is None:
            continue
        if sp[0] == "timed":
            a, b = max(0.0, sp[1]), min(dialogue_duration, sp[2])
            if b - a < 0.1:
                rep.error("segments[%d]" % si, "the time range is empty or outside the recording")
                continue
            pieces.append(Piece(a, b, si, [i for i, w in enumerate(words) if a <= (w["start"] + w["end"]) / 2 <= b
                                          and i not in removed], timed=True))
            continue
        i0, i1 = sp
        kept = [i for i in range(i0, i1 + 1) if i not in removed]
        if not kept:
            rep.error("segments[%d]" % si, "every word of this segment is removed")
            continue
        runs, run = [], [kept[0]]
        for i in kept[1:]:
            if i == run[-1] + 1:
                run.append(i)
            else:
                runs.append(run)
                run = [i]
        runs.append(run)
        for run in runs:
            a, b = run[0], run[-1]
            start = words[a]["start"] - PAD_BEFORE
            if a > 0:
                start = max(start, words[a - 1]["end"] + 0.01)
            end = words[b]["end"] + max(PAD_AFTER, holds.get(b, 0.0))
            if b + 1 < len(words):
                end = min(end, words[b + 1]["start"] - 0.01)
            start, end = max(0.0, start), min(dialogue_duration, end)
            cur, cur_words = start, [a]
            for k in range(a, b):
                gap = words[k + 1]["start"] - words[k]["end"]
                limit, target = trim_above, target_pause
                if k in holds:
                    limit = target = max(holds[k], target_pause)
                if gap > limit and gap >= 2 * MIN_CUT_PAUSE:
                    keep_a = min(gap / 2, max(PAD_AFTER, target / 2))
                    keep_b = min(gap / 2, max(PAD_BEFORE, target / 2))
                    pieces.append(Piece(cur, words[k]["end"] + keep_a, si, cur_words))
                    cur, cur_words = words[k + 1]["start"] - keep_b, []
                cur_words.append(k + 1)
            pieces.append(Piece(cur, end, si, cur_words))
    return pieces, removed


def snap_pieces(pieces, fps, rep, min_frames=2):
    """Put every piece on the frame grid (start rounded down, end up, so no word loses a syllable) and lay the pieces
    end to end on the output timeline."""
    out, cursor = [], 0
    for n, p in enumerate(pieces):
        p.f_in = int(math.floor(p.m_in * fps + 1e-6))
        p.f_out = int(math.ceil(p.m_out * fps - 1e-6))
        if out and not p.timed:
            prev = out[-1]
            if prev.seg == p.seg and prev.f_out > p.f_in and prev.f_out - p.f_in <= 2:
                p.f_in = prev.f_out
        if p.f_out - p.f_in < min_frames:
            rep.warn("piece %d" % n, "shorter than %d frames after snapping; dropped" % min_frames)
            continue
        p.out_from = cursor
        cursor += p.frames()
        out.append(p)
    return out, cursor


# ---------------------------------------------------------------- word times on the output timeline

def map_words(pieces, words, removed, fps):
    """Each kept word's output start and end (seconds), per occurrence."""
    mapped = []
    for pi, p in enumerate(pieces):
        base = p.out_from / fps - p.f_in / fps
        lo, hi = p.f_in / fps, p.f_out / fps
        for i in p.words:
            if i in removed:
                continue
            w = words[i]
            mid = (w["start"] + w["end"]) / 2
            if not (lo - 0.02 <= mid <= hi + 0.02):
                continue
            s = max(w["start"], lo) + base
            e = min(w["end"], hi) + base
            mapped.append({"i": i, "id": w["id"], "text": w["text"], "start": round(s, 3), "end": round(max(e, s + 0.02), 3),
                           "piece": pi})
    mapped.sort(key=lambda m: m["start"])
    return mapped


def first_out(mapped_by_index, i):
    occ = mapped_by_index.get(i)
    return occ[0] if occ else None


# ---------------------------------------------------------------- captions

PUNCT_ONLY = re.compile(r"^[।॥.,!?;:…)\]'\"]+$")


def word_pages(mapped, max_words, max_chars, emphasis, gap_break=0.3):
    mapped = [dict(w) for w in mapped]
    pages, cur = [], []

    def flush():
        if cur:
            pages.append(list(cur))
            del cur[:]

    for w in mapped:
        text = str(w["text"]).strip()
        if PUNCT_ONLY.match(text):
            # a lone full stop or danda from the recogniser joins the word before it, never a page of its own
            target = cur[-1] if cur else (pages[-1][-1] if pages else None)
            if target is not None:
                target["text"] = str(target["text"]).rstrip() + text
                target["end"] = max(target["end"], w["end"])
            continue
        if cur:
            chars = sum(graphemes(x["text"].strip()) + 1 for x in cur) + graphemes(text)
            if (len(cur) >= max_words or chars > max_chars or w["start"] - cur[-1]["end"] > gap_break
                    or ends_sentence(cur[-1]["text"])):
                flush()
        cur.append(w)
    flush()
    out = []
    for n, page in enumerate(pages):
        start = page[0]["start"]
        end = page[-1]["end"] + 0.15
        if n + 1 < len(pages):
            nxt = pages[n + 1][0]["start"]
            end = nxt if nxt - page[-1]["end"] < 0.3 else min(end, nxt)
        tokens = []
        for k, w in enumerate(page):
            tokens.append({"text": (" " if k else "") + str(w["text"]).strip(), "fromMs": int(round(w["start"] * 1000)),
                           "toMs": int(round(w["end"] * 1000)), "emphasis": w["id"] in emphasis})
        out.append({"startMs": int(round(start * 1000)), "endMs": int(round(end * 1000)), "tokens": tokens})
    return out


def _split_lines(text, max_chars):
    if graphemes(text) <= max_chars:
        return [text]
    words = text.split(" ")
    best, best_score = None, None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        if b.startswith(("।", "॥", ")", "]")):
            continue
        over = max(graphemes(a) - max_chars, 0) + max(graphemes(b) - max_chars, 0)
        punct = 0 if re.search(r"[,;:.!?।]$", a) else 1
        score = (over, abs(graphemes(a) - graphemes(b)) / 10.0 + punct * 0.5 + (0.3 if graphemes(a) > graphemes(b) else 0))
        if best_score is None or score < best_score:
            best, best_score = [a, b], score
    return best or [text]


def sentence_cues(mapped, lang, max_chars=42, max_lines=2, fps=30):
    """Subtitle cues: at most 2 lines of 42 characters, 0.83 to 7 s, 20 (English) or 22 (Bangla) characters a second,
    a gap of at least 2 frames, breaks at punctuation, and never a line that starts with the danda."""
    cps = 22.0 if (lang or "").startswith("bn") else 20.0
    limit = max_chars * max_lines
    groups, cur = [], []
    for w in mapped:
        text = str(w["text"]).strip()
        if not text:
            continue
        if PUNCT_ONLY.match(text) and cur:
            cur[-1] = dict(cur[-1], text=cur[-1]["text"].rstrip() + text, end=w["end"])
            continue
        if cur:
            joined = " ".join(x["text"].strip() for x in cur) + " " + text
            if (graphemes(joined) > limit or w["start"] - cur[-1]["end"] > 0.7 or w["end"] - cur[0]["start"] > 7.0
                    or (ends_sentence(cur[-1]["text"]) and graphemes(joined) > max_chars * 0.6)):
                groups.append(cur)
                cur = []
        cur.append(w)
    if cur:
        groups.append(cur)
    cues = []
    min_gap = 2.0 / fps
    for n, g in enumerate(groups):
        text = " ".join(x["text"].strip() for x in g)
        start = g[0]["start"]
        end = max(g[-1]["end"] + 0.3, start + 0.83, start + graphemes(text) / cps)
        end = min(end, start + 7.0)
        end = max(end, g[-1]["end"])
        if n + 1 < len(groups):
            end = min(end, groups[n + 1][0]["start"] - min_gap)
        end = max(end, start + 0.05)
        cues.append({"start": round(start, 3), "end": round(end, 3), "lines": _split_lines(text, max_chars),
                     "text": text})
    return cues


def srt(cues):
    def ts(t):
        ms = int(round(t * 1000))
        return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    blocks = []
    for n, c in enumerate(cues, 1):
        blocks.append("%d\n%s --> %s\n%s\n" % (n, ts(c["start"]), ts(c["end"]), "\n".join(c["lines"])))
    return "\n".join(blocks)


def vtt(cues):
    def ts(t):
        ms = int(round(t * 1000))
        return "%02d:%02d:%02d.%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)
    return "WEBVTT\n\n" + "\n".join("%s --> %s\n%s\n" % (ts(c["start"]), ts(c["end"]), "\n".join(c["lines"]))
                                    for c in cues)


# ---------------------------------------------------------------- compile

def _frames(t, fps):
    return int(round(t * fps))


def _overlay_text(ov):
    props = ov.get("props") or {}
    parts = [str(props.get(k, "")) for k in ("text", "title", "value", "label", "name", "role", "left", "right",
                                            "source", "subtitle")]
    items = props.get("items") or []
    parts += [str(x) for x in items]
    return " ".join(p for p in parts if p).strip()


def compile_plan(plan, words, job, preset, overlay_rules, sfx_defaults=None, fps=None):
    """Check the plan and build the EDL. Returns a dict: edl, pieces, cues, speech, sfx, chapters, report."""
    rep = Report()
    if plan.get("schema") != PLAN_SCHEMA:
        rep.error("plan", "schema must be \"%s\"" % PLAN_SCHEMA)
    fps = int(fps or preset.get("fps") or job.get("fps") or 30)
    lang = plan.get("language") or job.get("language") or "en"
    idx = index_words(words)
    dialogue = job.get("dialogue")
    if not dialogue or dialogue not in job.get("sources", {}):
        rep.error("job", "no dialogue source: run `nvc.py ingest` (it picks the best microphone)")
        return {"report": rep.as_dict()}
    dsrc = job["sources"][dialogue]
    dialogue_duration = float(dsrc.get("duration") or 0) or (words[-1]["end"] + 1 if words else 0)
    silence = preset.get("silence") or {}
    trim_above = float(plan.get("trim_pauses_above_ms", silence.get("trim_above_ms", 550))) / 1000.0
    target_pause = float(plan.get("pause_target_ms", silence.get("target_ms", 300))) / 1000.0
    if not plan.get("segments"):
        rep.error("plan", "needs at least one segment")
        return {"report": rep.as_dict()}

    pieces, removed = build_pieces(plan, words, idx, rep, trim_above, target_pause, dialogue_duration)
    for a in range(len(pieces)):
        for b in range(a + 1, len(pieces)):
            pa, pb = pieces[a], pieces[b]
            if pa.seg != pb.seg and pa.m_in < pb.m_out - 0.05 and pb.m_in < pa.m_out - 0.05:
                rep.warn("segments[%d]" % pb.seg, "repeats %.2f-%.2f s of the recording already used by "
                         "segments[%d]; fine for a cold open, a mistake otherwise"
                         % (max(pa.m_in, pb.m_in), min(pa.m_out, pb.m_out), pa.seg))
    pieces, total_frames = snap_pieces(pieces, fps, rep)
    if rep.errors or not pieces:
        if not pieces and not rep.errors:
            rep.error("plan", "nothing is kept")
        return {"report": rep.as_dict()}
    duration = total_frames / fps

    cams, screens = pick_sources(job)
    segs = plan["segments"]
    layout_map = preset.get("layout_map") or {}
    pip_default = dict(preset.get("pip") or {})
    vertical = preset["height"] > preset["width"]
    default_layout = ("stack" if vertical else "screenPip") if (cams and screens) else (
        "camFull" if cams else ("screenFull" if screens else "voiceOnly"))

    punch_items = {}
    for n, item in enumerate(plan.get("punches") or []):
        sp = resolve_span(item, words, idx, rep, "punches[%d]" % n)
        if sp:
            punch_items[sp[0]] = float(item.get("scale") or 1.15)
    transitions = {}
    for n, item in enumerate(plan.get("transitions") or []):
        seg = item.get("segment")
        ttype = item.get("type", "zoom")
        if not isinstance(seg, int) or not (0 <= seg < len(segs)):
            rep.error("transitions[%d]" % n, "needs \"segment\": index of the segment it leads into")
        elif ttype not in TRANSITIONS:
            rep.error("transitions[%d]" % n, "type must be one of " + ", ".join(TRANSITIONS))
        else:
            transitions[seg] = {"type": ttype, "frames": int(item.get("frames") or (6 if ttype == "flash" else 9))}

    clips = []
    seg_piece_count = {}
    for n, p in enumerate(pieces):
        seg = segs[p.seg]
        layout = seg.get("layout") or default_layout
        if layout not in LAYOUTS:
            rep.error("segments[%d]" % p.seg, "layout must be one of " + ", ".join(LAYOUTS))
            layout = default_layout
        layout = layout_map.get(layout, layout)
        cam = seg.get("cam") or (cams[0] if cams else None)
        screen = seg.get("screen") or (screens[0] if screens else None)
        for role, sid in (("cam", seg.get("cam")), ("screen", seg.get("screen")), ("broll", seg.get("broll"))):
            if sid and sid in job["sources"] and not ready(job["sources"][sid]):
                rep.error("segments[%d]" % p.seg, "%s source %s has no proxy yet: run nvc.py ingest" % (role, sid))
        m_in = p.f_in / fps
        length = p.frames() / fps

        def place(src_id):
            if not src_id or src_id not in job["sources"]:
                return None
            src = job["sources"][src_id]
            t0 = source_time(job, src_id, m_in)
            dur = float(src.get("duration") or 0)
            if t0 < -0.04 or (dur and t0 + length > dur + 0.04):
                return None
            return {"source": src_id, "trimBefore": max(0, _frames(t0, fps))}

        need_cam = layout in ("camFull", "screenPip", "split", "stack")
        need_screen = layout in ("screenFull", "screenPip", "split", "stack")
        cam_place = place(cam) if need_cam else None
        screen_place = place(screen) if need_screen else None
        wanted = layout
        if need_cam and need_screen and (cam_place is None or screen_place is None):
            layout = "camFull" if cam_place else ("screenFull" if screen_place else "voiceOnly")
        elif need_cam and cam_place is None:
            layout = "screenFull" if place(screen) else "voiceOnly"
            screen_place = place(screen) if layout == "screenFull" else None
        elif need_screen and screen_place is None:
            layout = "camFull" if place(cam) else "voiceOnly"
            cam_place = place(cam) if layout == "camFull" else None
        if layout != wanted:
            rep.warn("clip c%03d" % (n + 1), "%s needs a source that does not cover %.2f-%.2f s; using %s"
                     % (wanted, m_in, m_in + length, layout))
        broll_place = None
        if layout == "brollFull":
            bid = seg.get("broll")
            if not bid or bid not in job["sources"]:
                rep.error("segments[%d]" % p.seg, "brollFull needs \"broll\": an ingested source id")
            else:
                broll_place = {"source": bid, "trimBefore": _frames(float(seg.get("in") or 0), fps)}
        k = seg_piece_count.get(p.seg, 0)
        seg_piece_count[p.seg] = k + 1
        punch = float(seg.get("punch") or 1.0)
        for wi in p.words:
            if wi in punch_items:
                punch = punch_items[wi]
        if punch == 1.0 and k % 2 == 1 and layout == "camFull" and seg.get("auto_punch", True) and cam_place:
            # a jump cut inside one segment reads as intended when the framing changes; the ceiling keeps the total
            # upscale of the source at or under 1.15 (a 4K source in a 1080p edit can go to 1.2, a landscape source
            # already blown up for a vertical frame gets no punch)
            src = job["sources"][cam_place["source"]]
            sw = float(src.get("width") or preset["width"])
            sh = float(src.get("height") or preset["height"])
            cover = max(preset["width"] / sw, preset["height"] / sh)
            ceiling = max(1.0, 1.15 / cover)
            if ceiling >= 1.08:
                punch = round(min(1.2, ceiling), 3)
        pip = dict(pip_default)
        pip.update(seg.get("pip") or {})
        clip = {"id": "c%03d" % (n + 1), "from": p.out_from, "durationInFrames": p.frames(), "layout": layout,
                "masterIn": round(m_in, 4), "masterOut": round(p.f_out / fps, 4), "segment": p.seg,
                "beat": seg.get("beat"), "punch": punch, "pip": pip, "cam": cam_place, "screen": screen_place,
                "broll": broll_place, "transitionIn": {"type": "cut", "frames": 0}}
        if k == 0 and p.seg in transitions and n > 0:
            clip["transitionIn"] = transitions[p.seg]
        clips.append(clip)

    mapped = map_words(pieces, words, removed, fps)
    by_index = {}
    for m in mapped:
        by_index.setdefault(m["i"], []).append(m)
    if not mapped:
        rep.warn("captions", "no spoken words are kept")

    rules = overlay_rules or {}
    overlays = []
    slot_busy = []
    for n, ov in enumerate(plan.get("overlays") or []):
        where = "overlays[%d] (%s)" % (n, ov.get("type"))
        otype = ov.get("type")
        rule = rules.get(otype)
        if not rule:
            rep.error(where, "unknown type; use one of " + ", ".join(sorted(rules)))
            continue
        props = dict(ov.get("props") or {})
        for key in TEXT_PROPS.get(otype, []):
            if props.get(key) in (None, "", []):
                rep.error(where, "props.%s is required" % key)
        start = end = None
        grounded_quote = None
        if "words" in ov:
            sp = resolve_span(ov, words, idx, rep, where)
            if not sp:
                continue
            grounded_quote = ov.get("quote")
            a = first_out(by_index, sp[0])
            b = None
            for i in range(sp[1], sp[0] - 1, -1):
                occ = by_index.get(i)
                if occ:
                    b = occ[0]
                    break
            if not a or not b:
                rep.error(where, "its words are not in the edit (removed or outside every segment)")
                continue
            lead = 0.0 if otype in ("broll", "image", "segment", "redact", "callout") else 0.12
            start = max(0.0, a["start"] - lead)
            end = b["end"] + (0.0 if otype in ("redact",) else 0.25)
        elif ov.get("at") == "start":
            start = 0.0
            end = float(ov.get("seconds") or rule["min_s"] + 1.0)
        elif ov.get("at") == "end":
            secs = float(ov.get("seconds") or max(rule["min_s"], 3.0))
            start, end = max(0.0, duration - secs), duration
        elif "from" in ov and "to" in ov:
            start, end = float(ov["from"]), float(ov["to"])
            rep.warn(where, "timed by seconds, not grounded to words")
        else:
            rep.error(where, "needs \"words\" and a quote, \"at\": \"start\"|\"end\", or \"from\" and \"to\"")
            continue
        text = _overlay_text(ov)
        need = max(float(rule.get("min_s") or 0), reading_time(text, lang) if text else 0.0)
        if otype in ("stat", "list", "compare"):
            need += 1.0
        if ov.get("seconds") and "words" in ov:
            end = start + float(ov["seconds"])
        if end - start < need:
            end = start + need
        if rule.get("max_s") and end - start > rule["max_s"]:
            if need > rule["max_s"]:
                rep.warn(where, "text needs %.1f s to read but this type stays at most %.1f s: shorten it"
                         % (need, rule["max_s"]))
            end = start + rule["max_s"]
        if end > duration:
            end = duration
            if end - start < need * 0.8:
                rep.warn(where, "runs past the end of the video; it gets only %.1f s" % max(0.0, end - start))
        if end <= start:
            rep.error(where, "has no time on screen")
            continue
        if otype in ("broll", "image", "segment"):
            sid = ov.get("source")
            if not sid or sid not in job["sources"]:
                rep.error(where, "needs \"source\": an ingested media id (nvc.py add JOB FILE --role broll)")
                continue
            if not ready(job["sources"][sid]):
                rep.error(where, "source %s has no proxy yet: run nvc.py ingest" % sid)
                continue
            props.setdefault("fit", ov.get("fit") or "full")
            props["source"] = sid
            props["trimBefore"] = _frames(float(ov.get("in") or 0), fps)
            src = job["sources"][sid]
            if otype == "broll" and src.get("duration") and float(ov.get("in") or 0) + (end - start) > float(src["duration"]) + 0.05:
                rep.warn(where, "the clip is shorter than its slot; it holds its last frame")
        if otype in ("callout", "redact"):
            box = ov.get("box")
            if not isinstance(box, dict) or not all(k in box for k in ("x", "y", "w", "h")):
                rep.error(where, "needs \"box\": {x, y, w, h} as fractions of the source frame")
                continue
            props["box"] = box
            props.setdefault("layer", ov.get("layer") or "screen")
        if text:
            shown = numbers_in(text) - label_numbers(text)
            # an overlay placed by time (a hook at the start) may show a number said later in the edit
            said = numbers_in(grounded_quote if grounded_quote else " ".join(m["text"] for m in mapped))
            origin = {str(f.get("origin")) for f in (ov.get("facts") or []) if isinstance(f, dict)}
            extra = sorted(x for x in shown if x not in said)
            if extra and not (origin & {"brief", "client", "web"}):
                rep.ask(where, "shows %s, which the speaker %s; confirm the source (add facts with origin brief, "
                        "client or web)" % (", ".join(("%g" % x) for x in extra),
                                            "did not say in the grounded words" if grounded_quote
                                            else "does not say anywhere in the edit"))
        slot = rule["slot"]
        f0, f1 = _frames(start, fps), _frames(end, fps)
        overlays.append({"id": "o%03d" % (n + 1), "type": otype, "from": f0, "durationInFrames": max(1, f1 - f0),
                         "props": props, "enter": ov.get("enter"), "exit": ov.get("exit"),
                         "sfx": ov.get("sfx", "default")})
        if slot not in ("redact", "screen", "bar"):
            slot_busy.append({"i": len(overlays) - 1, "slot": slot, "need": int(math.ceil(need * fps)),
                              "name": "overlays[%d]" % n})
        if ov.get("words"):
            rep.decisions.append({"kind": "graphic" if otype not in ("broll", "image", "segment") else "broll",
                                  "ref": overlays[-1]["id"], "words": ov["words"], "quote": grounded_quote})

    # two graphics in one slot: the earlier one ends where the next begins when it keeps its reading time that way
    # (graphics grounded on neighbouring words touch by design); otherwise the plan must change
    by_slot = {}
    for item in slot_busy:
        by_slot.setdefault(item["slot"], []).append(item)
    for slot, items in by_slot.items():
        items.sort(key=lambda it: overlays[it["i"]]["from"])
        for a, b in zip(items, items[1:]):
            oa, ob = overlays[a["i"]], overlays[b["i"]]
            if oa["from"] + oa["durationInFrames"] <= ob["from"]:
                continue
            room = ob["from"] - oa["from"]
            if room >= a["need"] and room >= 1:
                oa["durationInFrames"] = room
                rep.decisions.append({"kind": "trim_overlay", "ref": oa["id"], "why": "ends where %s begins" % ob["id"]})
            else:
                rep.error(b["name"], "overlaps %s in the %s slot (%.2f-%.2f s) and there is no room to shorten it: "
                          "move one, shorten its text or use another type" % (
                              a["name"], slot, oa["from"] / fps, (oa["from"] + oa["durationInFrames"]) / fps))

    zooms = []
    for n, z in enumerate(plan.get("zooms") or []):
        where = "zooms[%d]" % n
        sp = resolve_span(z, words, idx, rep, where)
        if not sp:
            continue
        a, b = first_out(by_index, sp[0]), None
        for i in range(sp[1], sp[0] - 1, -1):
            if by_index.get(i):
                b = by_index[i][0]
                break
        if not a or not b:
            rep.error(where, "its words are not in the edit")
            continue
        scale = float(z.get("scale") or 1.6)
        if not 1.0 < scale <= 3.0:
            rep.error(where, "scale must be above 1 and at most 3")
            continue
        start = max(0.0, a["start"] - 0.3)
        end = max(b["end"] + 0.4, start + 2.0 + 1.0)
        end = min(end, duration)
        zooms.append({"id": "z%03d" % (n + 1), "layer": z.get("layer") or "screen", "from": _frames(start, fps),
                      "durationInFrames": max(1, _frames(end - start, fps)), "x": float(z.get("x", 0.5)),
                      "y": float(z.get("y", 0.5)), "scale": scale, "ease": int(z.get("ease_frames") or 15)})
    zooms.sort(key=lambda z: z["from"])
    for layer in sorted({z["layer"] for z in zooms}):
        same = [z for z in zooms if z["layer"] == layer]
        for a, b in zip(same, same[1:]):
            if b["from"] < a["from"] + a["durationInFrames"]:
                rep.error(b["id"], "overlaps %s on the %s layer" % (a["id"], layer))

    cap = dict(preset.get("captions") or {})
    cap_plan = plan.get("captions") or {}
    style = cap_plan.get("style") or cap.get("style") or "word"
    emphasis = set(cap_plan.get("emphasis") or [])
    bn = str(lang).startswith("bn")
    pages = []
    if style == "word":
        max_chars = int(cap.get("max_chars") or 18) + (4 if bn else 0)
        per = int(cap.get("words_per_page") or 3)
        pages = word_pages(mapped, per if not bn else min(per, 2), max_chars, emphasis)
    subs = preset.get("subtitles") or {}
    cues = sentence_cues(mapped, lang, max_chars=int(subs.get("max_chars") or 42),
                         max_lines=int(subs.get("max_lines") or 2), fps=fps)
    burn_sentence = style == "sentence" and bool(cap_plan.get("burn", cap.get("burn")))
    captions = {"style": style if style in ("word", "sentence") else "none",
                "burn": style == "word" or burn_sentence, "fontPx": int(cap.get("font_px") or 64),
                "band": (preset.get("bands") or {}).get("captions"), "pages": pages,
                "cues": [{"startMs": int(c["start"] * 1000), "endMs": int(c["end"] * 1000), "lines": c["lines"]}
                         for c in cues] if burn_sentence else [],
                "case": "none" if bn else (cap_plan.get("case") or ("upper" if style == "word" else "none"))}
    if style == "none":
        captions["burn"] = False

    chapters = []
    for n, ch in enumerate(plan.get("chapters") or []):
        sp = resolve_span(ch, words, idx, rep, "chapters[%d]" % n)
        if not sp:
            continue
        a = first_out(by_index, sp[0])
        if not a:
            rep.error("chapters[%d]" % n, "its first word is not in the edit")
            continue
        chapters.append({"t": math.floor(a["start"]), "title": str(ch.get("title") or "").strip()})
    chapters.sort(key=lambda c: c["t"])
    if chapters:
        chapters[0]["t"] = 0
        if len(chapters) < 3:
            rep.warn("chapters", "YouTube shows chapters only with 3 or more")
        for a, b in zip(chapters, chapters[1:]):
            if b["t"] - a["t"] < 10:
                rep.warn("chapters", "\"%s\" is under 10 s; YouTube needs every chapter to be 10 s or longer"
                         % a["title"])
        if duration - chapters[-1]["t"] < 10:
            rep.warn("chapters", "the last chapter is under 10 s")

    speech = []
    for m in mapped:
        if speech and m["start"] - speech[-1][1] < 0.3:
            speech[-1][1] = max(speech[-1][1], m["end"])
        else:
            speech.append([m["start"], m["end"]])
    speech = [[round(a, 3), round(b, 3)] for a, b in speech]

    sfx = build_sfx(plan, overlays, clips, by_index, words, idx, rep, fps, preset, sfx_defaults or {})
    check_hook_and_pacing(clips, overlays, zooms, mapped, preset, duration, rep, fps)

    sources = {}
    for sid, s in job["sources"].items():
        if not s.get("proxy") and not s.get("image"):
            continue
        sources[sid] = {"src": s.get("proxy") or s.get("image"), "kind": s.get("kind"), "width": s.get("width"),
                        "height": s.get("height"), "alpha": bool(s.get("alpha")), "face": s.get("face"),
                        "duration": s.get("duration")}
    edl = {
        "schema": EDL_SCHEMA, "job": job.get("id"), "target": preset.get("name"), "title": plan.get("title")
        or job.get("title"), "language": lang, "width": preset["width"], "height": preset["height"], "fps": fps,
        "durationInFrames": total_frames, "safe": preset.get("safe"), "bands": preset.get("bands"),
        "theme": theme_for(plan, job, lang), "base": "", "audio": None, "sources": sources, "clips": clips,
        "overlays": overlays, "zooms": zooms, "captions": captions, "chapters": chapters,
        "progress": bool(plan.get("progress_bar")),
        "meta": {"warnings": rep.warnings, "review": rep.review},
    }
    return {"edl": edl, "pieces": [{"masterIn": round(p.f_in / fps, 6), "masterOut": round(p.f_out / fps, 6),
                                    "outFrom": p.out_from, "frames": p.frames()} for p in pieces],
            "cues": cues, "speech": speech, "sfx": sfx, "chapters": chapters, "mapped_words": mapped,
            "report": rep.as_dict(), "duration": duration}


def theme_for(plan, job, lang):
    theme = {"accent": "#FFD23F", "text": "#FFFFFF", "ink": "#0E1014", "bg": "#0E1014", "card": "#FFFFFF",
             "cardText": "#0E1014", "muted": "#9AA3B2", "danger": "#FF4D4D",
             "display": "Montserrat", "body": "Inter", "captions": "Montserrat", "radius": 28}
    if str(lang).startswith("bn"):
        theme.update({"display": "HindSiliguri", "body": "HindSiliguri", "captions": "HindSiliguri"})
    theme.update(job.get("theme") or {})
    theme.update(plan.get("theme") or {})
    return theme


def build_sfx(plan, overlays, clips, by_index, words, idx, rep, fps, preset, defaults):
    """Sound-effect cues on the output timeline: the plan's own cues plus one default per overlay and per
    transition. Default cues that crowd another cue are dropped (at most one prominent effect every 1 s in short
    videos and every 4 s in long ones)."""
    if plan.get("sfx") is False:
        return []
    vertical = preset["height"] > preset["width"]
    spacing = 1.0 if vertical else 4.0
    cues = []
    for n, item in enumerate(plan.get("sfx") or []):
        at = str(item.get("at") or "")
        t = None
        if at.startswith("overlay:"):
            key = at.split(":", 1)[1]
            ov = next((o for o in overlays if o["id"] == key or o["id"] == "o%03d" % (int(key) + 1 if key.isdigit() else -9)), None)
            t = ov["from"] / fps if ov else None
        elif at.startswith("word:"):
            wid = at.split(":", 1)[1]
            occ = by_index.get(idx.get(wid, -1))
            t = occ[0]["start"] if occ else None
        elif at.startswith("clip:"):
            key = at.split(":", 1)[1]
            c = next((c for c in clips if c["id"] == key or c["id"] == "c%03d" % (int(key) + 1 if key.isdigit() else -9)), None)
            t = c["from"] / fps if c else None
        elif at.startswith("time:"):
            t = float(at.split(":", 1)[1])
        if t is None:
            rep.error("sfx[%d]" % n, "\"at\" must be overlay:<id or index>, word:<id>, clip:<id> or time:<seconds>")
            continue
        cues.append({"t": round(t, 3), "name": item.get("name") or "whoosh", "gain_db": item.get("gain_db"),
                     "align": item.get("align") or _sfx_align(item.get("name")), "why": "plan", "explicit": True})
    for ov in overlays:
        name = ov.get("sfx")
        if name == "default":
            name = defaults.get(ov["type"])
        if not name or ov["type"] in ("redact", "progress"):
            continue
        cues.append({"t": round(ov["from"] / fps, 3), "name": name, "gain_db": None, "align": _sfx_align(name),
                     "why": "%s %s" % (ov["type"], ov["id"]), "explicit": False})
    for c in clips:
        if c["transitionIn"]["type"] in ("zoom", "whip", "flash"):
            cues.append({"t": round(c["from"] / fps, 3), "name": "whoosh-short" if c["transitionIn"]["type"] != "flash"
                         else "impact", "gain_db": None, "align": "peak", "why": "transition into " + c["id"],
                         "explicit": False})
    cues.sort(key=lambda c: (c["t"], not c["explicit"]))
    kept = []
    for c in cues:
        if not c["explicit"] and any(abs(c["t"] - k["t"]) < spacing for k in kept):
            continue
        kept.append(c)
    for c in kept:
        c.pop("explicit", None)
    return kept


def _sfx_align(name):
    name = str(name or "")
    if name.startswith(("riser", "downlifter")):
        return "end"
    if name.startswith(("whoosh", "swipe", "swoosh")):
        return "peak"
    return "attack"


def check_hook_and_pacing(clips, overlays, zooms, mapped, preset, duration, rep, fps):
    hook = preset.get("hook") or {}
    if mapped and mapped[0]["start"] > float(hook.get("first_word_s") or 0.5) + 0.01:
        rep.warn("hook", "the first word starts at %.2f s; start by %.1f s (trim the lead-in)"
                 % (mapped[0]["start"], float(hook.get("first_word_s") or 0.5)))
    if preset.get("max_s") and duration > preset["max_s"]:
        rep.error("length", "%.1f s is over this target's limit of %d s" % (duration, preset["max_s"]))
    events = {0.0, duration}
    for c in clips:
        events.add(c["from"] / fps)
    for o in overlays:
        events.add(o["from"] / fps)
        events.add((o["from"] + o["durationInFrames"]) / fps)
    for z in zooms:
        events.add(z["from"] / fps)
    ev = sorted(events)
    gaps = [(b - a, a, b) for a, b in zip(ev, ev[1:]) if b > a]
    pacing = preset.get("pacing") or {}
    max_static = float(pacing.get("max_static_s") or 15)
    for g, a, b in gaps:
        if g > max_static + 0.01:
            rep.warn("pacing", "nothing changes on screen from %.1f to %.1f s (%.1f s; aim for at most %.0f s): add a "
                     "punch-in, b-roll, a graphic or a zoom" % (a, b, g, max_static))
    if gaps:
        values = sorted(g for g, _, _ in gaps)
        median = values[len(values) // 2]
        lo, hi = (pacing.get("median_gap_s") or [0, 99])[:2]
        if median > hi * 1.5:
            rep.warn("pacing", "the median time between visual changes is %.1f s; this target reads best at %.1f to "
                     "%.1f s" % (median, lo, hi))


def edl_report_md(result, job, preset):
    """A human-readable edit report (edl.md) for the editor and the client."""
    edl = result["edl"]
    fps = edl["fps"]
    lines = ["# Edit report: %s" % (edl.get("title") or edl.get("job")), "",
             "Target: %s (%dx%d, %d fps). Length: %s. Clips: %d. Overlays: %d. Zooms: %d. Sound effects: %d." % (
                 preset.get("label"), edl["width"], edl["height"], fps, fmt_time(result["duration"]),
                 len(edl["clips"]), len(edl["overlays"]), len(edl["zooms"]), len(result["sfx"])), ""]
    rep = result["report"]
    if rep["warnings"]:
        lines += ["## Warnings", ""] + ["- " + w for w in rep["warnings"]] + [""]
    if rep["review"]:
        lines += ["## Check before delivery", ""] + ["- " + w for w in rep["review"]] + [""]
    lines += ["## Timeline", "", "| Output | Master | Layout | Beat |", "|---|---|---|---|"]
    for c in edl["clips"]:
        lines.append("| %s to %s | %.2f to %.2f | %s%s | %s |" % (
            fmt_time(c["from"] / fps), fmt_time((c["from"] + c["durationInFrames"]) / fps), c["masterIn"],
            c["masterOut"], c["layout"], (" x%.2f" % c["punch"]) if c["punch"] != 1 else "", c.get("beat") or ""))
    if edl["overlays"]:
        lines += ["", "## Overlays", "", "| Output | Type | Content |", "|---|---|---|"]
        for o in edl["overlays"]:
            lines.append("| %s to %s | %s | %s |" % (fmt_time(o["from"] / fps),
                                                    fmt_time((o["from"] + o["durationInFrames"]) / fps), o["type"],
                                                    _overlay_text({"props": o["props"]}).replace("|", "/")[:90]))
    if result["chapters"]:
        lines += ["", "## Chapters", ""] + ["%s %s" % (fmt_time(c["t"], chapters=True), c["title"])
                                          for c in result["chapters"]]
    return "\n".join(lines) + "\n"


def fmt_time(t, chapters=False):
    t = max(0.0, float(t))
    if chapters:
        s = int(t)
        return "%d:%02d:%02d" % (s // 3600, s // 60 % 60, s % 60) if s >= 3600 else "%02d:%02d" % (s // 60, s % 60)
    return "%d:%05.2f" % (int(t // 60), t % 60)


def chapters_txt(chapters):
    return "\n".join("%s %s" % (fmt_time(c["t"], chapters=True), c["title"]) for c in chapters) + "\n"


def active_index(starts, t):
    """Index of the last start at or before t (binary search), or -1."""
    return bisect.bisect_right(starts, t) - 1
