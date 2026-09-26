"""The review engine of the nexa writing family (nexa-script, nexa-copy): rubric judges, version checks, a simulated
audience panel, the aggregator that turns reactions into at most five fixes, the acceptance and stopping rules, and
the blandness guard. Built on research note R10 (2026-09-26); the numbers below come from it.

Standard library only, Python 3.9 or newer. Identical copies in nexa-script and nexa-copy; tests keep them the same.

What the evidence allows, and so what this reports:
- Judges agree with people on checklists and pairwise calls, not on taste, and they favour longer, familiar and
  AI-written text. So: checklist items with quoted evidence, only two anchored 1 to 5 scales, judges from families
  other than the writer's (Codex/GPT and Gemini here; the writer is Claude), two runs each, majority votes, and a
  version check in both orders.
- A persona panel gets direction right, not magnitude. Every number it produces is "synthetic, directional": it finds
  where people would leave and ranks versions; it never predicts retention, CTR or conversion. Personas are simulations
  grounded in real audience texts, never "people" and never quoted as testimonials.
- Loops make writing blander. At most 2 revision rounds (3 for flagship pieces), an edit budget, a keep list, and a
  revision is accepted only when a paired panel prefers it by the binomial threshold (61 of 100) in both families.
"""
import json
import math
import random
import re
from collections import Counter, defaultdict

import nexa_llm

REASON_TAGS = ("slow", "confusing", "salesy", "irrelevant", "repetitive", "fake", "other")
ACTIONS = ("like", "comment", "share", "save", "click", "follow", "reply", "buy", "nothing")
SEVERITY = {"major": 3, "moderate": 2, "minor": 1}
DEFAULT_ROSTER = ("codex", "gemini:gemini-3.8-flash", "gemini:gemini-3.1-pro-preview")
SYNTHETIC = "synthetic, directional: simulated personas, not people; never a forecast of real results"
SCALES = {
    "stop_for_L1": "Would the target reader or viewer stop for the first line (L1) in their feed or inbox?",
    "publishable": "Is this publishable for this client, as it stands?",
}
SCALE_ANCHORS = ("1 = harms the brand; 2 = generic, reads as AI; 3 = publishable but forgettable; 4 = good, with one "
                 "line people would repeat; 5 = as good as the client's best past piece (when one is given)")


# ------------------------------------------------------------------------------------------------------- lines

# a full stop that does not end a sentence: titles and Latin shorthands (then the next word joins the line)
NOT_AN_END = re.compile(r"\b(?:Mr|Mrs|Ms|Dr|Prof|St|Sr|Jr|vs|approx|cf|e\.g|i\.e)\.$", re.I)


def split_sentences(text):
    """Sentences for English, Bangla and Hindi: split after . ! ? and the danda, keeping the mark. A title or
    shorthand (Dr., e.g.) and a full stop followed by a lower-case word (9 a.m. on Monday) do not split."""
    parts = re.split(r"(?<=[.!?।])\s+(?=\S)", (text or "").strip())
    out = []
    for p in (x.strip() for x in parts):
        if not p:
            continue
        if out and out[-1].endswith(".") and (NOT_AN_END.search(out[-1]) or p[0].islower() and p[0].isascii()):
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def number_lines(units):
    """units: a string (split into sentences) or a list of strings or of {"text", "beat"} dicts. Returns the lines
    [{"id": "L1", "text": ..., "beat": ...}] every judge and persona refers to."""
    items = []
    if isinstance(units, str):
        items = [{"text": s, "beat": None} for s in split_sentences(units)]
    else:
        for u in units:
            if isinstance(u, str):
                items += [{"text": s, "beat": None} for s in split_sentences(u)]
            else:
                extra = {"role": u["role"]} if u.get("role") else {}
                items += [dict({"text": s, "beat": u.get("beat")}, **extra) for s in split_sentences(u.get("text", ""))]
    return [dict(it, id=f"L{i + 1}") for i, it in enumerate(items)]


def render_lines(lines):
    """L1: text, with the field's role for copy (L1 (headline): ...) and, on the line where a video beat starts, the
    picture and the on-screen text in brackets."""
    out = []
    for ln in lines:
        extra = [f"picture: {ln['visual']}"] if ln.get("visual") else []
        extra += [f"on screen: {ln['on_screen']}"] if ln.get("on_screen") else []
        role = f" ({ln['role']})" if ln.get("role") else ""
        out.append(f"{ln['id']}{role}: {ln['text']}" + (f"   [{'; '.join(extra)}]" if extra else ""))
    return "\n".join(out)


def has_pictures(lines):
    return any(ln.get("visual") or ln.get("on_screen") for ln in lines)


PICTURE_NOTE = ("Square brackets after a line give what the viewer sees from that line on (picture) and the text "
                "shown on screen; they are part of the draft.")


def roster_engine(member):
    """"codex" or "gemini:<model>" into (engine, model)."""
    if ":" in member:
        eng, model = member.split(":", 1)
        return eng, model
    return member, None


def family(member):
    return roster_engine(member)[0]


# ----------------------------------------------------------------------------------------------------- statistics

def wilson(k, n, z=1.96):
    """95 % Wilson interval of a proportion (k of n) as (low, high)."""
    if n <= 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (round(max(0.0, centre - half), 3), round(min(1.0, centre + half), 3))


def binomial_threshold(n, alpha=0.05):
    """Smallest k with a two-sided exact binomial p-value under alpha for p = 0.5 (61 of 100, 39 of 60, 21 of 30)."""
    if n <= 0:
        return 1
    for k in range(n // 2, n + 1):
        tail = sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n
        if 2 * tail < alpha:
            return k
    return n


def median(values):
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def iqr(values):
    vals = sorted(v for v in values if v is not None)
    if len(vals) < 2:
        return 0.0
    q = lambda f: vals[min(len(vals) - 1, max(0, int(round(f * (len(vals) - 1)))))]  # noqa: E731
    return q(0.75) - q(0.25)


# ----------------------------------------------------------------------------------------------------------- judge

def line_ids(values):
    """The L-ids in whatever the models returned ("L5", "L5: the quote", "L2-L3"), unique, in line order."""
    found = {m for v in values for m in re.findall(r"\bL\d+\b", str(v))}
    return sorted(found, key=lambda x: int(x[1:]))


def judge_schema(checklist):
    return {"type": "object", "properties": {
        "criteria": {"type": "array", "items": {"type": "object", "properties": {
            "id": {"type": "string", "enum": [c["id"] for c in checklist]},
            "lines": {"type": "array", "items": {"type": "string"}},
            "evidence": {"type": "string"}, "reason": {"type": "string"},
            "verdict": {"type": "string", "enum": ["pass", "fail"]},
            "severity": {"type": "string", "enum": ["major", "moderate", "minor", "none"]},
            "problem": {"type": "string"}}}},
        "scales": {"type": "object", "properties": {
            k: {"type": "object", "properties": {"evidence": {"type": "string"},
                                                 "score": {"type": "integer", "minimum": 1, "maximum": 5}}}
            for k in SCALES}},
        "best_lines": {"type": "array", "items": {"type": "string"}},
        "tells": {"type": "array", "items": {"type": "object", "properties": {
            "line": {"type": "string"}, "pattern": {"type": "string"}}}},
    }}


def judge_prompt(brief, lines, checklist, past=None, seed=0):
    items = list(checklist)
    random.Random(seed).shuffle(items)
    crit = "\n".join(f"- {c['id']}: {c['question']}" for c in items)
    past_txt = ""
    if past:
        past_txt = "\n\nThe client's past pieces, with known results (the bar for a 5):\n" + "\n---\n".join(
            f"[{p.get('label', 'past')}] result: {p.get('result', 'unknown')}\n{p.get('text', '')}" for p in past)
    return (
        "You are a senior editor judging a draft for a client. You did not write it and you must not rewrite it. "
        "Length is not quality: a longer draft is not better. Judge what is on the page for this audience.\n\n"
        f"THE BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\n"
        f"THE DRAFT (numbered lines)" + (f" {PICTURE_NOTE}" if has_pictures(lines) else "") +
        f"\n{render_lines(lines)}{past_txt}\n\n"
        "THE CHECKLIST: for each item, quote the evidence lines first, give one or two sentences of reasoning, then "
        "the verdict (pass or fail). For a fail, give its severity (major, moderate, minor) and the problem as the "
        "reader would experience it, without prescribing a rewrite. For a pass, severity is none and problem is "
        f"empty.\n{crit}\n\n"
        "TWO SCALES, 1 to 5, evidence first: " + "; ".join(f"{k}: {v}" for k, v in SCALES.items()) +
        f". Anchors: {SCALE_ANCHORS}.\n\n"
        "Also list best_lines (up to three line ids worth keeping word for word) and tells (lines that read as "
        "machine-written, with the pattern: template, participial tail, stock phrase, summary line, uniform rhythm, "
        "not-X-but-Y, rule of three, named emotion, moral ending, preamble).")


def judge(brief, lines, checklist, roster=DEFAULT_ROSTER, runs=2, past=None, effort="high", fresh=False,
          workers=6):
    """Every roster member judges `runs` times with the checklist in a different order. Returns the aggregate:
    per criterion pass or fail by majority (a tie is 'unstable': a person decides), the scales' median and IQR
    (IQR above 1 marks a scale unreliable here), best lines named by two or more judges, tells, and each run."""
    jobs, meta = [], []
    for member in roster:
        eng, model = roster_engine(member)
        for r in range(runs):
            jobs.append({"prompt": judge_prompt(brief, lines, checklist, past, seed=r),
                         "schema": judge_schema(checklist), "engine": eng, "model": model, "effort": effort,
                         "fresh": fresh, "who": f"judge-{member}-run{r + 1}"})
            meta.append({"judge": member, "run": r + 1})
    results = nexa_llm.call_many(jobs, workers=workers)
    runs_out, votes, scales = [], defaultdict(list), defaultdict(list)
    best, tells = Counter(), []
    for m, res in zip(meta, results):
        if not res.get("ok"):
            runs_out.append(dict(m, ok=False, error=res.get("error")))
            continue
        d = res["data"]
        runs_out.append(dict(m, ok=True, engine=res.get("engine"), data=d))
        for c in d.get("criteria", []):
            votes[c.get("id")].append(dict(c, judge=m["judge"], run=m["run"]))
        for k, v in (d.get("scales") or {}).items():
            if isinstance(v, dict) and isinstance(v.get("score"), int):
                scales[k].append(v["score"])
        for ln in line_ids(d.get("best_lines") or []):
            best[ln] += 1
        tells += [dict(t, judge=m["judge"]) for t in d.get("tells") or []]
    criteria = []
    for c in checklist:
        # only real verdicts count: an answer with no verdict is neither a pass nor a fail
        vs = [v for v in votes.get(c["id"], []) if v.get("verdict") in ("pass", "fail")]
        fails = [v for v in vs if v.get("verdict") == "fail"]
        passes = len(vs) - len(fails)
        state = "no votes" if not vs else ("unstable" if len(fails) == passes else
                                           ("fail" if len(fails) > passes else "pass"))
        sev = Counter(v.get("severity") for v in fails).most_common(1)
        criteria.append({"id": c["id"], "question": c["question"], "state": state, "fail_votes": len(fails),
                         "votes": len(vs), "severity": sev[0][0] if sev else None,
                         "lines": line_ids(ln for v in fails for ln in (v.get("lines") or [])),
                         "evidence": [v.get("evidence") for v in fails][:3],
                         "problems": [v.get("problem") for v in fails if v.get("problem")][:3]})
    scale_out = {k: {"median": median(v), "iqr": iqr(v), "scores": v, "reliable": iqr(v) <= 1} for k, v in
                 scales.items()}
    ok_runs = sum(1 for r in runs_out if r.get("ok"))
    return {"schema": "nexa.judge/1", "runs_ok": ok_runs, "runs_total": len(jobs),
            "families": sorted({family(m) for m in roster}), "criteria": criteria, "scales": scale_out,
            "best_lines": [ln for ln, n in best.most_common() if n >= 2], "tells": tells, "runs": runs_out}


PAIR_SCHEMA = {"type": "object", "properties": {
    "winner": {"type": "string", "enum": ["A", "B", "tie"]}, "reason": {"type": "string"},
    "decisive_lines": {"type": "array", "items": {"type": "string"}}}}


def pair_prompt(brief, first, second, question):
    return (
        "Two drafts for the same brief, labelled A and B. They were written independently; the order means nothing "
        "and length is not quality. You did not write either one.\n\n"
        f"THE BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\nDRAFT A\n{first}\n\nDRAFT B\n{second}\n\n"
        f"QUESTION: {question} Answer A, B or tie, with one reason and the decisive lines.")


def pairwise(brief, text_a, text_b, question="Which draft would the target audience rather read or watch, and which "
             "serves the brief better?", roster=DEFAULT_ROSTER, effort="high", fresh=False):
    """Both orders for every roster member. A member's vote counts only when both orders agree; returns wins for A
    (the first text given) and B, ties and disagreements."""
    jobs, meta = [], []
    for member in roster:
        eng, model = roster_engine(member)
        for order in ("AB", "BA"):
            first, second = (text_a, text_b) if order == "AB" else (text_b, text_a)
            jobs.append({"prompt": pair_prompt(brief, first, second, question), "schema": PAIR_SCHEMA,
                         "engine": eng, "model": model, "effort": effort, "fresh": fresh,
                         "who": f"pair-{member}-{order}"})
            meta.append((member, order))
    results = nexa_llm.call_many(jobs)
    by_member = defaultdict(dict)
    for (member, order), res in zip(meta, results):
        if res.get("ok"):
            w = res["data"].get("winner")
            if order == "BA" and w in ("A", "B"):
                w = "B" if w == "A" else "A"  # map back to the caller's labels
            by_member[member][order] = {"winner": w, "reason": res["data"].get("reason")}
    tally = {"A": 0, "B": 0, "tie": 0, "split": 0, "failed": 0}
    detail = {}
    for member in roster:
        o = by_member.get(member, {})
        if len(o) < 2:
            tally["failed"] += 1
            detail[member] = "failed"
            continue
        a, b = o["AB"]["winner"], o["BA"]["winner"]
        verdict = a if a == b else "split"
        tally[verdict if verdict in tally else "split"] += 1
        detail[member] = {"verdict": verdict, "AB": o["AB"], "BA": o["BA"]}
    return {"schema": "nexa.pairwise/1", "tally": tally, "members": detail,
            "a_wins": tally["A"] > tally["B"] and tally["A"] > len(roster) / 2,
            "b_wins": tally["B"] > tally["A"] and tally["B"] > len(roster) / 2}


def pair_reasons(res):
    """Each judge's verdict and its reasons, what a loser has to fix. The reasons keep the judge's own labels: in
    `a_shown_first` "A" is the caller's A, in `b_shown_first` "A" is the caller's B."""
    out = {}
    for member, d in (res.get("members") or {}).items():
        if not isinstance(d, dict):
            out[member] = {"verdict": d}
            continue
        out[member] = {"verdict": d["verdict"],
                       "a_shown_first": (d.get("AB") or {}).get("reason") or "",
                       "b_shown_first": (d.get("BA") or {}).get("reason") or ""}
    return out


# ----------------------------------------------------------------------------------------------------------- panel

DEFAULT_SEGMENTS = [
    {"id": "core", "name": "core audience (already interested)", "weight": 0.30, "priority": True},
    {"id": "newcomer", "name": "newcomers who know little about it", "weight": 0.25, "priority": True},
    {"id": "sceptic", "name": "sceptics who distrust claims and ads", "weight": 0.15, "priority": False},
    {"id": "pressed", "name": "short of time or money", "weight": 0.15, "priority": False},
    {"id": "lapsed", "name": "lapsed or bored followers", "weight": 0.10, "priority": False},
    {"id": "adjacent", "name": "adjacent interests, might be won", "weight": 0.05, "priority": False},
]
PERSONA_SCHEMA = {"type": "object", "properties": {"personas": {"type": "array", "items": {"type": "object",
    "properties": {"id": {"type": "string"}, "segment": {"type": "string"}, "card": {"type": "string"},
                   "quote_ids": {"type": "array", "items": {"type": "string"}},
                   "context": {"type": "string"}}}}}}


def allocate(n, segments):
    """Persona counts per segment by weight, summing to n (largest remainder)."""
    total = sum(s["weight"] for s in segments) or 1.0
    raw = [(s["id"], n * s["weight"] / total) for s in segments]
    counts = {sid: int(v) for sid, v in raw}
    left = n - sum(counts.values())
    for sid, v in sorted(raw, key=lambda x: x[1] - int(x[1]), reverse=True)[:left]:
        counts[sid] += 1
    return counts


def build_panel(brief, evidence, n=100, segments=None, engine="auto", batch=20, seed=7, fresh=False, workers=4):
    """Persona cards grounded in real audience texts. `evidence`: [{"id", "text", "source"}] (comments, reviews, DMs,
    search terms; research pack voice bank). Each card cites the evidence ids it was built from; no invented
    biographies beyond what the evidence and the brief support."""
    segments = segments or DEFAULT_SEGMENTS
    counts = allocate(n, segments)
    rng = random.Random(seed)
    ev = list(evidence or [])
    jobs, plan = [], []
    pid = 1
    for seg in segments:
        k = counts.get(seg["id"], 0)
        while k > 0:
            m = min(batch, k)
            sample = rng.sample(ev, min(len(ev), 40)) if ev else []
            ids = [f"P{pid + i:03d}" for i in range(m)]
            prompt = (
                f"Write {m} audience persona cards for the segment '{seg['name']}' (segment id {seg['id']}), for "
                f"this brief:\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\n"
                "Ground every card in the real audience texts below: take their worries, words and habits from them "
                "and list the ids of the texts each card rests on in quote_ids. Do not invent a biography beyond what "
                "the texts and the brief support; demographics are context only. Each card is 120 to 200 words, "
                "first person, in the audience's own register (their language and mix of languages), and names the "
                "viewing or reading context (device, time, sound on or off) and what makes them skip or leave. Make "
                "the cards differ from each other: disagreement inside a segment is real.\n\n"
                f"Use these ids, in order: {', '.join(ids)}.\n\nREAL AUDIENCE TEXTS\n" +
                ("\n".join(f"[{e.get('id')}] {e.get('text')}" for e in sample) if sample else
                 "(none given: build from the brief only and say so in each card's first sentence)"))
            jobs.append({"prompt": prompt, "schema": PERSONA_SCHEMA, "engine": engine, "effort": "medium",
                         "fresh": fresh, "who": f"personas-{seg['id']}-{pid}"})
            plan.append((seg["id"], ids))
            pid += m
            k -= m
    results = nexa_llm.call_many(jobs, workers=workers)
    known = {e.get("id") for e in ev}
    personas, errors, invented = [], [], 0
    for (sid, ids), res in zip(plan, results):
        if not res.get("ok"):
            errors.append(res.get("error"))
            continue
        got = res["data"].get("personas") or []
        if len(got) < len(ids):
            errors.append(f"{sid}: asked for {len(ids)} personas, got {len(got)}")
        for want, p in zip(ids, got):
            qids = p.get("quote_ids") or []
            invented += sum(1 for q in qids if q not in known)
            personas.append({"id": want, "segment": sid, "card": p.get("card", ""),
                             "quote_ids": [q for q in qids if q in known], "context": p.get("context", "")})
    if invented:
        errors.append(f"{invented} quote ids named in the cards are not in the evidence (dropped)")
    return {"schema": "nexa.panel/1", "brief": brief, "segments": segments, "personas": personas,
            "evidence_count": len(ev), "grounded": bool(ev),
            "grounded_cards": sum(1 for p in personas if p["quote_ids"]), "errors": errors,
            "validation": {"spearman": None, "ok": False,
                           "note": "not validated against real results yet: `panel validate` ranks 5 to 10 past "
                                   "posts with known results (Spearman 0.4 or more before the panel's fixes count)"},
            "label": SYNTHETIC}


def reaction_schema(with_hooks, with_intent):
    props = {
        "persona_id": {"type": "string"},
        "t2": {"type": "object", "properties": {
            "left_at": {"type": "string"}, "reason_tag": {"type": "string", "enum": list(REASON_TAGS) + ["none"]},
            "why": {"type": "string"}}},
        "t3": {"type": "object", "properties": {
            "actions": {"type": "array", "items": {"type": "string", "enum": list(ACTIONS)}},
            "comment": {"type": "string"}, "remember": {"type": "string"}, "fake": {"type": "string"},
            "fake_why": {"type": "string"}, "confusing": {"type": "string"}, "confusing_why": {"type": "string"}}},
    }
    if with_hooks:
        props["t1"] = {"type": "object", "properties": {
            "stopped_for": {"type": "array", "items": {"type": "string"}}, "why": {"type": "string"}}}
    if with_intent:
        props["t4_text"] = {"type": "string"}
    return {"type": "object", "properties": {"reactions": {"type": "array", "items": {
        "type": "object", "properties": props}}}}


def panel_prompt(brief, lines, personas, medium, hooks=None, intent=False):
    cards = "\n\n".join(f"[{p['id']}] (segment {p['segment']}) {p['card']} Context: {p.get('context', '')}"
                        for p in personas)
    hook_txt = ""
    if hooks:
        hook_txt = ("\n\nT1 FEED STOP TEST: in their feed or inbox they see these openings (ids in brackets). Each "
                    "person picks up to two they would stop for (possibly none) and says why:\n" +
                    "\n".join(f"[{h['id']}] {h['text']}" for h in hooks))
    how = {"video": "as it plays, line by line, without skipping ahead", "read": "as they read it, top to bottom",
           "listen": "as they hear it, line by line"}[medium]
    return (
        f"You simulate {len(personas)} separate people, each described by a card. Each reacts alone, in character, "
        "from the card only; they do not see each other's answers. It is fine if most or none of them like it. "
        "Leaving early and finishing are both normal: each person does what their card says they would do, with no "
        "kindness and no harshness for its own sake.\n\n"
        f"THE BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\nTHE PEOPLE\n{cards}{hook_txt}\n\n"
        f"THE DRAFT (numbered lines; each person meets it {how})" +
        (f" {PICTURE_NOTE} A person watching with the sound off meets only the pictures and the on-screen text."
         if has_pictures(lines) else "") + f"\n{render_lines(lines)}\n\n"
        "For each person give: t2, the first line id where they would leave (\"end\" if they would finish), a reason "
        f"tag from {', '.join(REASON_TAGS)} (or none when they finish) and why, in their own words; t3, what they "
        f"would do after it ({', '.join(ACTIONS)}), the comment they would write in their own language and register "
        "(empty if none), the line id they would remember, the line id that felt fake and the line id that confused "
        "them, each with a short reason in their own words (fake_why, confusing_why; empty strings when none)" +
        ("; t4_text, what they would think or do next about the offer, in their "
                                             "own words" if intent else "") + ".")


def chunk_map(lines):
    """Line id to chunk, as in R10's staged watch: the hook (L1), 0 to 15 s, 15 to 30 s, 30 to 60 s, the rest, and
    "end" (finished). Lines carry their start second as "t" when the timing is known; otherwise the chunks split the
    lines by position."""
    out = {"end": 5}
    n = len(lines)
    for i, ln in enumerate(lines):
        if i == 0:
            out[ln["id"]] = 0
        elif ln.get("t") is not None:
            t = float(ln["t"])
            out[ln["id"]] = 1 if t < 15 else 2 if t < 30 else 3 if t < 60 else 4
        else:
            out[ln["id"]] = 1 + min(3, int(4 * i / max(n, 1)))
    return out


def run_panel(panel, lines, brief=None, medium="video", hooks=None, intent=False, families=("codex", "gemini"),
              batch=10, probe=5, seed=None, fresh=False, workers=8, effort="low"):
    """The panel reacts to one draft. Batches of `batch` personas are split across the model families; `probe`
    personas are asked twice (a noise probe: when their leave points disagree more than 30 % of the time, do not act
    on the panel). Returns the raw reactions and the probe result."""
    brief = brief or panel.get("brief") or {}
    personas = list(panel.get("personas") or [])
    rng = random.Random(seed)
    rng.shuffle(personas)
    groups = [personas[i:i + batch] for i in range(0, len(personas), batch)]
    probe_set = personas[:probe] if probe else []
    jobs, meta = [], []
    schema = reaction_schema(bool(hooks), intent)
    for gi, group in enumerate(groups):
        fam = families[gi % len(families)]
        eng, model = roster_engine(fam)
        jobs.append({"prompt": panel_prompt(brief, lines, group, medium, hooks, intent), "schema": schema,
                     "engine": eng, "model": model, "effort": effort, "fresh": fresh, "who": f"panel-{gi}-{eng}"})
        meta.append({"family": eng, "ids": [p["id"] for p in group], "probe": False})
    if probe_set:
        # the probe repeats personas of the first batch with the same family and model, in a new batch: it
        # measures run-to-run noise, not the difference between model families
        probe_set = groups[0][:probe]
        eng, model = roster_engine(families[0])
        jobs.append({"prompt": panel_prompt(brief, lines, probe_set, medium, hooks, intent),
                     "schema": schema, "engine": eng, "model": model, "effort": effort, "fresh": True,
                     "who": f"panel-probe-{eng}"})
        meta.append({"family": eng, "ids": [p["id"] for p in probe_set], "probe": True})
    results = nexa_llm.call_many(jobs, workers=workers)
    reactions, probe_answers, errors = [], {}, []
    for m, res in zip(meta, results):
        if not res.get("ok"):
            errors.append(res.get("error"))
            continue
        got = {r.get("persona_id"): r for r in (res["data"].get("reactions") or [])}
        for pid in m["ids"]:
            r = got.get(pid)
            if not r:
                continue
            r = dict(r, family=m["family"])
            if m["probe"]:
                probe_answers[pid] = r
            else:
                reactions.append(r)
    first = {r["persona_id"]: r for r in reactions}
    compared = [pid for pid in probe_answers if pid in first]
    chunk = chunk_map(lines)
    differ = sum(1 for pid in compared if chunk.get((probe_answers[pid].get("t2") or {}).get("left_at"), -1) !=
                 chunk.get((first[pid].get("t2") or {}).get("left_at"), -1))
    noise = {"compared": len(compared), "disagree": differ,
             "share": round(differ / len(compared), 2) if compared else None}
    noise["act_on_panel"] = noise["share"] is not None and noise["share"] <= 0.30
    by_id = {p["id"]: p for p in panel.get("personas") or []}
    for r in reactions:
        r["segment"] = (by_id.get(r.get("persona_id")) or {}).get("segment")
    return {"schema": "nexa.panel-run/1", "reactions": reactions, "noise": noise, "errors": errors,
            "probe": [dict(probe_answers[pid], first_left_at=(first[pid].get("t2") or {}).get("left_at"))
                      for pid in compared],
            "families": sorted({m["family"] for m in meta}), "label": SYNTHETIC}


# ------------------------------------------------------------------------------------------------------ aggregator

def _weights(panel):
    segs = {s["id"]: s for s in panel.get("segments") or DEFAULT_SEGMENTS}
    counts = Counter(p.get("segment") for p in panel.get("personas") or [])
    return {sid: (segs[sid]["weight"] / counts[sid]) if counts.get(sid) else 0.0 for sid in segs}, segs


def aggregate(panel, run, lines, judge_result=None, hooks=None, max_fixes=5):
    """Metrics, issues, the fix list (at most five), the keep list and the watch list, in code. Every number is
    labelled synthetic and directional."""
    reactions = run.get("reactions") or []
    n = len(reactions)
    ids = [ln["id"] for ln in lines]
    index = {lid: i for i, lid in enumerate(ids)}
    w, segs = _weights(panel)
    # survival and hazard over lines
    leave_at = []
    for r in reactions:
        t2 = r.get("t2") or {}
        pos = index.get(t2.get("left_at"), len(ids))
        leave_at.append(pos)
    survival, hazard = [], []
    alive = n
    for i in range(len(ids)):
        left = sum(1 for p in leave_at if p == i)
        prev = alive
        alive -= left
        survival.append(alive / n if n else 0.0)
        hazard.append((left / prev) if prev else 0.0)
    # the median over every line (most lines lose nobody): a spike is twice that and at least 5 people leaving
    med_h = median(hazard) or 0.0
    spikes = [{"line": ids[i], "left": sum(1 for p in leave_at if p == i), "hazard": round(hazard[i], 3)}
              for i in range(len(ids)) if hazard[i] >= 2 * med_h and sum(1 for p in leave_at if p == i) >= 5]
    finished = sum(1 for p in leave_at if p >= len(ids))
    # per-line shares
    def share(field):
        c = Counter((r.get("t3") or {}).get(field) for r in reactions)
        return {lid: {"count": c[lid], "ci": wilson(c[lid], n)} for lid in ids if c.get(lid)}
    remembered, fake, confusing = share("remember"), share("fake"), share("confusing")
    actions = Counter(a for r in reactions for a in (r.get("t3") or {}).get("actions") or [])
    # hook index
    hook = None
    if hooks:
        stops = Counter(h for r in reactions for h in ((r.get("t1") or {}).get("stopped_for") or [])[:2])
        draft_ids = [h["id"] for h in hooks if h.get("draft")]
        real = [stops.get(h["id"], 0) / n for h in hooks if not h.get("draft")] if n else []
        base = median(real)
        hook = {lid: {"stop_rate": round(stops.get(lid, 0) / n, 3) if n else 0.0,
                      "index": round((stops.get(lid, 0) / n) / base, 2) if n and base else None}
                for lid in draft_ids}
    # issues: panel flags and judge failures, clustered by line and tag
    clusters = defaultdict(lambda: {"support_w": 0.0, "count": 0, "families": set(), "segments": Counter(),
                                    "quotes": [], "tags": Counter()})
    for r in reactions:
        seg = r.get("segment")
        weight = w.get(seg, 1.0 / max(n, 1))
        t2 = r.get("t2") or {}
        if t2.get("left_at") in index:
            key = (t2["left_at"], t2.get("reason_tag") or "other")
            c = clusters[key]
            c["support_w"] += weight
            c["count"] += 1
            c["families"].add(r.get("family"))
            c["segments"][seg] += 1
            c["tags"][key[1]] += 1
            if t2.get("why") and len(c["quotes"]) < 2:
                c["quotes"].append(t2["why"])
        for field, tag in (("fake", "fake"), ("confusing", "confusing")):
            lid = (r.get("t3") or {}).get(field)
            if lid in index:
                c = clusters[(lid, tag)]
                c["support_w"] += weight
                c["count"] += 1
                c["families"].add(r.get("family"))
                c["segments"][seg] += 1
                c["tags"][tag] += 1
                why = (r.get("t3") or {}).get(f"{field}_why")
                if why and len(c["quotes"]) < 2:
                    c["quotes"].append(why)
    judge_fail_lines = set()
    judge_issues = []
    for crit in (judge_result or {}).get("criteria", []):
        if crit.get("state") == "fail":
            judge_fail_lines.update(crit.get("lines") or [])
            judge_issues.append(crit)
    total_w = sum(w.get(r.get("segment"), 0) for r in reactions) or 1.0
    priority_segs = {sid for sid, s in segs.items() if s.get("priority")}
    seg_n = Counter(r.get("segment") for r in reactions)
    issues = []
    for (lid, tag), c in clusters.items():
        support = c["support_w"] / total_w
        seg_support = max((c["segments"][s] / seg_n[s] for s in priority_segs if seg_n.get(s)), default=0.0)
        sev = 3 if tag in ("fake", "confusing") else 2
        prio = support * sev * (1.5 if lid in judge_fail_lines else 1.0)
        both = len(c["families"]) >= 2 or len(run.get("families") or []) < 2
        enters = (support >= 0.10 or seg_support >= 0.20) and both
        issues.append({"line": lid, "tag": tag, "support": round(support, 3), "count": c["count"],
                       "priority_segment_support": round(seg_support, 3), "families": sorted(f for f in c["families"] if f),
                       "judge_also_failed": lid in judge_fail_lines, "priority": round(prio, 4),
                       "quotes": c["quotes"], "enters_fix_list": enters})
    for crit in judge_issues:
        issues.append({"line": ",".join(crit.get("lines") or []) or None, "tag": f"judge:{crit['id']}",
                       "support": None, "count": crit.get("fail_votes"), "families": ["judges"],
                       "judge_also_failed": True, "priority": SEVERITY.get(crit.get("severity"), 1) * 0.2,
                       "quotes": crit.get("problems") or [], "evidence": crit.get("evidence"),
                       "enters_fix_list": True})
    issues.sort(key=lambda x: x["priority"], reverse=True)
    fixes = [i for i in issues if i["enters_fix_list"]][:max_fixes]
    watch = [i for i in issues if not i["enters_fix_list"]][:10]
    keep = sorted({lid for lid, v in remembered.items() if n and v["count"] / n >= 0.15} |
                  set((judge_result or {}).get("best_lines") or []))
    polarising = [lid for lid in keep if lid in fake]
    seg_finish = {sid: {"n": seg_n[sid], "finished": sum(1 for r, p in zip(reactions, leave_at)
                                                         if r.get("segment") == sid and p >= len(ids))}
                  for sid in seg_n}
    # the comments the personas would write, spread across segments so no single group speaks for the panel
    by_seg = defaultdict(list)
    for r in reactions:
        text = ((r.get("t3") or {}).get("comment") or "").strip()
        if text:
            by_seg[r.get("segment")].append({"persona": r.get("persona_id"), "segment": r.get("segment"),
                                             "family": r.get("family"), "comment": text})
    comments = []
    while any(by_seg.values()) and len(comments) < 24:
        for seg in list(by_seg):
            if by_seg[seg]:
                comments.append(by_seg[seg].pop(0))
    return {"schema": "nexa.review/1", "label": SYNTHETIC, "personas": n, "comments": comments,
            "finished": {"count": finished, "ci": wilson(finished, n)},
            "survival": [{"line": lid, "share": round(s, 3)} for lid, s in zip(ids, survival)],
            "spikes": spikes, "remembered": remembered, "fake": fake, "confusing": confusing,
            "actions": dict(actions), "hook": hook, "segments": seg_finish,
            "fixes": fixes, "watch": watch, "keep": keep, "polarising": polarising,
            "noise": run.get("noise"),
            "act_on_panel": bool((run.get("noise") or {}).get("act_on_panel", True)),
            "validated": bool((panel.get("validation") or {}).get("ok"))}


def ranks(values):
    """Ranks from 1, ties sharing their average rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def spearman(xs, ys):
    """Spearman's rank correlation (Pearson on the ranks, so ties are handled); None when a side is constant."""
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    sy = math.sqrt(sum((b - my) ** 2 for b in ry))
    if not sx or not sy:
        return None
    return round(sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (sx * sy), 3)


VALIDATE_SCHEMA = {"type": "object", "properties": {"answers": {"type": "array", "items": {"type": "object",
    "properties": {"persona_id": {"type": "string"}, "item": {"type": "string"},
                   "stop": {"type": "boolean"}, "finish": {"type": "boolean"}}}}}}


def validate_panel(panel, items, brief=None, families=("codex", "gemini"), batch=10, seed=13, threshold=0.4,
                   fresh=False, workers=8):
    """R10's gate: the panel ranks 5 to 10 past pieces with known results. items: [{"id", "text", "actual"}], where
    actual is the real result (views, average view duration, retention at 30 s, replies). Every persona says, for
    each piece under a neutral label, whether they would stop for it and whether they would finish it; the share
    who would do both ranks the pieces, and Spearman's rho against the real ranking must reach the threshold."""
    items = [it for it in items if (it.get("text") or "").strip() and it.get("actual") is not None]
    if not 5 <= len(items) <= 10:
        return {"ok": False, "error": f"validation needs 5 to 10 past pieces with a text and a result; got "
                                      f"{len(items)}", "label": SYNTHETIC}
    rng = random.Random(seed)
    personas = list(panel.get("personas") or [])
    rng.shuffle(personas)
    brief = brief or panel.get("brief") or {}
    jobs, plan = [], []
    for gi in range(0, len(personas), batch):
        group = personas[gi:gi + batch]
        order = list(range(len(items)))
        rng.shuffle(order)
        labels = {f"I{k + 1}": items[i]["id"] for k, i in enumerate(order)}
        shown = "\n\n".join(f"I{k + 1}:\n{items[i]['text'][:1500]}" for k, i in enumerate(order))
        cards = "\n\n".join(f"{p['id']} ({p.get('segment')}): {p.get('card')}" for p in group)
        prompt = (f"Each persona below meets these past pieces in their feed, one at a time, and reacts alone. It is "
                  f"fine if most or none of them appeal. For every persona and every piece, answer stop (would they "
                  f"stop for it or open it) and finish (would they watch or read to the end). Behaviour only, no "
                  f"ratings.\n\nTHE AUDIENCE BRIEF\n{json.dumps(brief, ensure_ascii=False)}\n\nPIECES\n{shown}"
                  f"\n\nPERSONAS\n{cards}")
        fam = families[(gi // batch) % len(families)]
        jobs.append({"prompt": prompt, "schema": VALIDATE_SCHEMA, "engine": fam, "effort": "low", "fresh": fresh,
                     "who": f"validate-{gi}-{fam}"})
        plan.append((labels, {p["id"] for p in group}))
    results = nexa_llm.call_many(jobs, workers=workers)
    both = Counter()
    seen = Counter()
    errors = []
    for (labels, members), res in zip(plan, results):
        if not res.get("ok"):
            errors.append(res.get("error"))
            continue
        for a in (res["data"].get("answers") or []):
            item_id = labels.get(a.get("item"))
            if item_id is None or a.get("persona_id") not in members:
                continue
            seen[item_id] += 1
            both[item_id] += 1 if (a.get("stop") and a.get("finish")) else 0
    scores = [both[it["id"]] / seen[it["id"]] if seen[it["id"]] else 0.0 for it in items]
    rho = spearman(scores, [float(it["actual"]) for it in items])
    return {"ok": rho is not None and rho >= threshold, "spearman": rho, "threshold": threshold,
            "items": [{"id": it["id"], "actual": it["actual"], "panel_share": round(sc, 3), "answers": seen[it["id"]]}
                      for it, sc in zip(items, scores)],
            "errors": errors, "label": SYNTHETIC}


# ------------------------------------------------------------------------------------------- versions and loops

PREF_SCHEMA = {"type": "object", "properties": {"choices": {"type": "array", "items": {"type": "object",
    "properties": {"persona_id": {"type": "string"}, "choice": {"type": "string", "enum": ["A", "B"]},
                   "reason": {"type": "string"}}}}}}


def panel_prefer(panel, text_old, text_new, brief=None, families=("codex", "gemini"), batch=10, seed=11,
                 fresh=False, workers=8):
    """T5: every persona sees both versions under neutral labels in a random order and picks one. Returns the new
    version's wins overall and per family, and whether it clears the binomial threshold in both families."""
    brief = brief or panel.get("brief") or {}
    personas = list(panel.get("personas") or [])
    rng = random.Random(seed)
    rng.shuffle(personas)
    jobs, meta = [], []
    for gi in range(0, len(personas), batch):
        group = personas[gi:gi + batch]
        flip = rng.random() < 0.5
        a, b = (text_new, text_old) if flip else (text_old, text_new)
        fam = families[(gi // batch) % len(families)]
        eng, model = roster_engine(fam)
        cards = "\n\n".join(f"[{p['id']}] (segment {p['segment']}) {p['card']}" for p in group)
        prompt = (f"You simulate {len(group)} separate people, each described by a card; each answers alone. Two "
                  "versions of the same piece, labelled A and B; the labels and order mean nothing and length is not "
                  f"quality.\n\nTHE BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}\n\nTHE PEOPLE\n{cards}"
                  f"\n\nVERSION A\n{a}\n\nVERSION B\n{b}\n\nFor each person: which one would they rather read or "
                  "watch (A or B), and the one reason, in their own words.")
        jobs.append({"prompt": prompt, "schema": PREF_SCHEMA, "engine": eng, "model": model, "effort": "low",
                     "fresh": fresh, "who": f"prefer-{gi}-{eng}"})
        meta.append({"family": eng, "ids": [p["id"] for p in group], "new_is": "A" if flip else "B"})
    results = nexa_llm.call_many(jobs, workers=workers)
    wins, total = Counter(), Counter()
    reasons = []
    for m, res in zip(meta, results):
        if not res.get("ok"):
            continue
        for ch in res["data"].get("choices") or []:
            if ch.get("persona_id") not in m["ids"]:
                continue
            total[m["family"]] += 1
            if ch.get("choice") == m["new_is"]:
                wins[m["family"]] += 1
                if len(reasons) < 6:
                    reasons.append(ch.get("reason"))
    n = sum(total.values())
    k = sum(wins.values())
    need = binomial_threshold(n)
    fam_ok = {f: wins[f] >= binomial_threshold(total[f]) for f in total}
    return {"schema": "nexa.prefer/1", "label": SYNTHETIC, "new_wins": k, "n": n, "threshold": need,
            "by_family": {f: {"wins": wins[f], "n": total[f], "threshold": binomial_threshold(total[f]),
                              "clears": fam_ok[f]} for f in total},
            "clears": n > 0 and k >= need and all(fam_ok.values()), "share": round(k / n, 3) if n else None,
            "ci": wilson(k, n), "reasons_for_new": reasons}


# ------------------------------------------------------------------------------------------- blandness guard

def tokens(text):
    return re.findall(r"\w+", (text or "").lower())


def edit_share(old, new):
    """Share of the new text's tokens that are not in the old text in order (a word-level diff, LCS based)."""
    a, b = tokens(old), tokens(new)
    if not b:
        return 0.0
    prev = [0] * (len(b) + 1)
    for x in a:
        cur = [0]
        for j, y in enumerate(b):
            cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
        prev = cur
    return round(1 - prev[-1] / len(b), 3)


def ngrams(text, n=4):
    t = tokens(text)
    return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


def overlap(text, others, n=4):
    """Highest share of the text's 4-grams found in any of the other texts (generic baselines)."""
    mine = ngrams(text, n)
    if not mine or not others:
        return 0.0
    return round(max(len(mine & ngrams(o, n)) / len(mine) for o in others), 3)


# a number keeps its inner separators (1,000, 3.5, 9:02) and a percent sign, never the comma or full stop after it
SPECIFIC = re.compile(r"(\d(?:[\d,.:]*\d)?%?|[০-৯]+|[०-९]+|\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b)")


def specific_tokens(text):
    """The concrete details themselves: numbers (any script) and capitalised names, not counting sentence starts."""
    first_words = {m.group(1) for m in re.finditer(r"(?:^|[.!?\u0964]\s+)([A-Z][a-z]+)", text or "")}
    return [m.group(0) for m in SPECIFIC.finditer(text or "") if m.group(0) not in first_words]


def specificity(text):
    """Concrete details per 100 words: numbers (Latin, Bangla and Devanagari digits) and capitalised names."""
    words = len(tokens(text))
    if not words:
        return 0.0
    first_words = {m.group(1) for m in re.finditer(r"(?:^|[.!?।]\s+)([A-Z][a-z]+)", text or "")}
    hits = [m.group(0) for m in SPECIFIC.finditer(text or "") if m.group(0) not in first_words]
    return round(100 * len(hits) / words, 2)


def rhythm(text):
    lens = [len(tokens(s)) for s in split_sentences(text)]
    if len(lens) < 2:
        return {"sentences": len(lens), "mean": float(lens[0]) if lens else 0.0, "sd": 0.0}
    m = sum(lens) / len(lens)
    sd = math.sqrt(sum((x - m) ** 2 for x in lens) / (len(lens) - 1))
    return {"sentences": len(lens), "mean": round(m, 1), "sd": round(sd, 1)}


def blandness(old, new, baselines=None, budget=0.25, keep_lines=None, old_lines=None, new_lines=None,
              rewrite=False):
    """The guard a revision must pass: within the edit budget, keep-list lines unchanged, specificity not lower,
    rhythm spread not flatter by more than a third, and no closer to the generic baselines than before. A rewrite
    (a new draft after a hard failure, R10 5.4) is not held to the edit budget or the keep list; the other checks
    stay."""
    problems, notes = [], []
    share = edit_share(old, new)
    if share > budget:
        (notes if rewrite else problems).append(f"edited {share:.0%} of the text; the budget is {budget:.0%}")
    if keep_lines and old_lines and new_lines and not rewrite:
        old_map = {ln["id"]: ln["text"] for ln in old_lines}
        new_texts = {ln["text"] for ln in new_lines}
        lost = [lid for lid in keep_lines if old_map.get(lid) and old_map[lid] not in new_texts]
        if lost:
            problems.append(f"keep-list lines changed or removed: {', '.join(lost)}")
    # R10 5.5: a revision must not lose concrete detail. Every number and name of the old text must survive, and the
    # density may not fall by more than a third (adding the reader's worry, which holds no number, dilutes it a
    # little; that is not blandness)
    s_old, s_new = specificity(old), specificity(new)
    # a detail is lost when it no longer appears at all; saying "9" once instead of twice loses nothing
    lost = sorted(set(specific_tokens(old)) - set(specific_tokens(new)))
    if lost:
        problems.append(f"concrete details removed: {', '.join(lost[:8])}")
    if s_old and s_new < s_old * 0.67:
        problems.append(f"specificity fell from {s_old} to {s_new} details per 100 words (over a third)")
    r_old, r_new = rhythm(old), rhythm(new)
    if r_old["sd"] and r_new["sd"] < r_old["sd"] * 0.67:
        problems.append(f"sentence rhythm flattened (sd {r_old['sd']} to {r_new['sd']})")
    o_old = overlap(old, baselines or [])
    o_new = overlap(new, baselines or [])
    if baselines and o_new > o_old + 0.02:
        problems.append(f"moved closer to the generic baselines (4-gram overlap {o_old} to {o_new})")
    return {"ok": not problems, "problems": problems, "notes": notes, "rewrite": rewrite, "edit_share": share,
            "specificity": [s_old, s_new],
            "rhythm": [r_old, r_new], "baseline_overlap": [o_old, o_new] if baselines else None}


BASELINE_SCHEMA = {"type": "object", "properties": {"versions": {"type": "array", "items": {"type": "string"}}}}


def generic_baselines(brief, n=3, engine="auto", fresh=False):
    """What a fresh model writes from the brief alone: the generic versions a draft must not drift towards."""
    res = nexa_llm.call_json(
        f"Write {n} different versions of this piece from the brief alone, the way a capable general assistant "
        f"would. Return them as plain text in versions.\n\nTHE BRIEF\n{json.dumps(brief, ensure_ascii=False, indent=1)}",
        BASELINE_SCHEMA, engine=engine, effort="low", fresh=fresh, who="generic-baselines")
    return (res.get("data") or {}).get("versions") or [] if res.get("ok") else []


def decide(round_no, gates_ok, judge_result, review, prefer=None, guard=None, cap=2):
    """The stopping and acceptance rules. Returns {"accept": bool or None, "continue": bool, "why": [...]}."""
    why = []
    accept = None
    if prefer is not None:
        accept = bool(prefer.get("clears")) and (guard is None or guard.get("ok")) and gates_ok
        if not prefer.get("clears"):
            why.append(f"panel preferred the new version {prefer.get('new_wins')} of {prefer.get('n')} times; "
                       f"it needs {prefer.get('threshold')} in every family")
        if guard is not None and not guard.get("ok"):
            why += [f"blandness guard: {p}" for p in guard["problems"]]
        if not gates_ok:
            why.append("a hard gate fails")
    majority_fail = [c["id"] for c in (judge_result or {}).get("criteria", []) if c.get("state") == "fail"]
    strong_fix = [f for f in (review or {}).get("fixes", []) if (f.get("priority_segment_support") or 0) >= 0.20]
    more = (not gates_ok) or bool(majority_fail) or bool(strong_fix)
    if round_no >= cap:
        more = False
        why.append(f"round cap reached ({cap}): ship the best version, not the last")
    if (review or {}).get("act_on_panel") is False:
        why.append("the panel's noise probe disagreed more than 30 %: do not act on the panel this round")
    if review and review.get("validated") is False:
        why.append("the panel is not validated against past results (Spearman 0.4 on 5 to 10 past posts): its "
                   "fixes are hints, the judges and the gates decide")
    if majority_fail:
        why.append(f"judge criteria failing by majority: {', '.join(majority_fail)}")
    return {"accept": accept, "continue": more, "why": why, "label": SYNTHETIC}
