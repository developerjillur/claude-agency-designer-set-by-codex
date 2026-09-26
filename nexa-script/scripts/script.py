#!/usr/bin/env python3
"""nexa-script: the tools behind the script skill. Claude writes; this measures, checks, times, renders and runs the
review loop (judges from other model families and a simulated audience panel).

  script.py doctor
  script.py new DIR --format youtube-long|short|ad|talk|blog --lang en|bn|hi|banglish [--title T] [--target SECONDS]
  script.py lint FILE [--brief brief.json] [--pack research/pack.json] [--voice] [--level draft|final] [--json]
  script.py timing FILE [--wpm N]
  script.py render FILE [--out DIR]            script.md (A/V table, loop ledger), roadmap.md, narration.txt
  script.py judge FILE --brief brief.json [--past past.json] [--runs 2] [--roster codex,gemini:MODEL,...]
  script.py understand FILE --brief brief.json   retell and first-time-learner tests
  script.py panel build DIR --brief brief.json [--evidence voice-bank.json] [--n 100]
  script.py panel validate --panel panel.json --items past.json   5 to 10 past pieces with real results
  script.py panel run FILE --panel panel.json [--hooks hooks.json] [--judge judge.json]
  script.py prefer OLD NEW --panel panel.json
  script.py tournament V1 V2 [V3 ...] --brief brief.json   the best version, not the last
  script.py baselines --brief brief.json [--n 3]
  script.py guard OLD NEW [--baselines baselines.json] [--keep review.json] [--rewrite]
  script.py decide --round N [--lint lint.json] [--judge judge.json] [--review review.json] [--prefer P] [--guard G]

FILE is a script.json (schema nexa.script/1), or plain narration (.txt), or a markdown article (.md, format blog).
Research notes behind every rule: R1 (YouTube long-form), R2 (short-form and ads), R3 (storytelling), R4 (blog),
R10 (judges and panels) and V1 to V6 (the reference videos), 2026-09-26.
"""
import argparse
import itertools
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nexa_llm  # noqa: E402
import nexa_review as R  # noqa: E402
from script_core import (ALIASES, FORMATS, LANG_FACTOR, MODES, die, emit, fmt_of, lang_of, load_json,  # noqa: E402,F401
                         load_script, loop_question, mmss, narration_lines, save_json, sentences, text_of, timing,
                         words, wpm_for)
from script_lint import (DESIGN, PAUSE_MARK, QUOTE_RE, ROLES, WORDS, classify, lex, lint_blog,  # noqa: E402,F401
                         lint_script, phrase_hits, voice_pass)

SKILL_VERSION = "2026.09.26.1"
CHECKLISTS = HERE.parent / "references" / "checklists.json"


# ------------------------------------------------------------------------------------------------------ lint

def cmd_lint(args):
    script = load_script(args.file, args.format, args.lang)
    pack = load_json(args.pack) if args.pack else None
    level = "final" if args.level == "final" else "draft"
    brief = load_json(args.brief) if args.brief else None
    res = lint_blog(script, level, args.keyword) if script["kind"] == "blog" else \
        lint_script(script, pack, level, brief)
    if args.voice:
        v = voice_pass(script)
        res["voice"] = v
        if v.get("ran"):
            res["errors"] += [f"voice: {e}" for e in v["errors"]]
            res["warnings"] += [f"voice: {w}" for w in v["warnings"]]
            res["ok"] = not res["errors"]
        else:
            res["notes"].append(f"voice: natural-text's pass did not run ({v.get('why')}): the words are unchecked")
    if args.json:
        emit(res)
    else:
        for kind in ("errors", "warnings", "notes"):
            for item in res[kind]:
                print(f"{kind[:-1]:7s} {item}")
        print(json.dumps({"ok": res["ok"], "errors": len(res["errors"]), "warnings": len(res["warnings"]),
                          **{k: res["stats"].get(k) for k in ("format", "lang", "wpm", "seconds", "words")}},
                         ensure_ascii=False))
    sys.exit(0 if res["ok"] else 1)


def cmd_timing(args):
    script = load_script(args.file, args.format, args.lang)
    emit(timing(script, args.wpm))


# ------------------------------------------------------------------------------------------------------ render

def cell(s):
    return (s or "").replace("|", "/").replace("\n", " ")


def spoken(text):
    """What a voice reads: stage marks such as [beat] and [pause] come out."""
    return re.sub(r"\s{2,}", " ", PAUSE_MARK.sub("", text or "")).strip()


def cmd_render(args):
    script = load_script(args.file)
    if script["kind"] != "json":
        die("render needs a script.json")
    out = Path(args.out or Path(args.file).parent)
    out.mkdir(parents=True, exist_ok=True)
    T = timing(script)
    meta, promise, beats = script["meta"], script["promise"], script["beats"]
    has_sound = any((b.get("sound") or "").strip() for b in beats)
    md = [f"# {meta.get('title') or 'Script'}", "",
          f"Format {meta['format']}, language {meta['lang']}, {T['wpm']} wpm, about {mmss(T['total_seconds'])}.", ""]
    if promise:
        md += ["## Promise", ""]
        for k in ("promise", "first_line", "first_visual", "tension", "payoff_at"):
            if promise.get(k):
                md.append(f"- **{k.replace('_', ' ')}:** {promise[k]}")
        for k in ("titles", "thumbnails"):
            if promise.get(k):
                md.append(f"- **{k}:** " + " | ".join(promise[k]))
        hooks = [h for h in promise.get("hook_variants") or [] if (h.get("spoken") or h.get("visual") or "").strip()]
        if len(hooks) > 1:
            md += ["", "| Hook | Type | First frame | Spoken | Caption |", "|---|---|---|---|---|"]
            for i, h in enumerate(hooks, 1):
                md.append(f"| H{i} | {cell(h.get('type'))} | {cell(h.get('visual'))} | {cell(h.get('spoken'))} | "
                          f"{cell(h.get('caption'))} |")
        md.append("")
    head = "| Time | Narration | Visual | On screen |" + (" Sound |" if has_sound else "")
    md += ["## Script", "", head, "|---|---|---|---|" + ("---|" if has_sound else "")]
    for b, tb in zip(beats, T["beats"]):
        row = f"| {mmss(tb['start'])} | {cell(b.get('narration'))} | {cell(b.get('visual'))} | {cell(b.get('on_screen'))} |"
        md.append(row + (f" {cell(b.get('sound'))} |" if has_sound else ""))
    if script["loops"]:
        md += ["", "## Loop ledger", "", "| Loop | Question | Opened | Closed |", "|---|---|---|---|"]
        for lid, q in script["loops"].items():
            op = next((b.get("id") for b in beats if lid in (b.get("loops_open") or [])), "")
            cl = next((b.get("id") for b in beats if lid in (b.get("loops_close") or [])), "")
            md.append(f"| {lid} | {cell(loop_question(q))} | {op} | {cl} |")
    claims = sorted({c for b in beats for c in (b.get("claims") or [])})
    if claims:
        md += ["", "## Sources", "", "Claim ids used: " + ", ".join(claims) + " (see research/pack.json)."]
    (out / "script.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (out / "narration.txt").write_text("\n\n".join(spoken(b.get("narration", "")) for b in beats) + "\n",
                                       encoding="utf-8")
    # V2 (YASH): an on-camera creator talks from a roadmap, not a read-out script
    sections, order = {}, []
    for b in beats:
        name = b.get("section") or b.get("id")
        if name not in sections:
            sections[name] = []
            order.append(name)
        sections[name].append(b)
    first = (sentences(spoken(beats[0].get("narration", ""))) or [""])[0] if beats else ""
    last = (sentences(spoken(beats[-1].get("narration", ""))) or [""])[-1] if beats else ""
    road = [f"# Roadmap: {meta.get('title') or 'script'}", "",
            "Say it in your own words from this card; the full script is in script.md.", "",
            f"**Hook line:** {first}", "", "**Structure:**", ""]
    for name in order:
        gist = spoken(" ".join(b.get("narration", "") for b in sections[name]))
        road.append(f"1. {name}: {(sentences(gist) or [''])[0][:160]}")
    facts = [s for b in beats if b.get("claims") for s in sentences(spoken(b.get("narration", "")))
             if re.search(r"\d", s)]
    if facts:
        road += ["", "**Facts to get exactly right:**", ""] + [f"- {s}" for s in facts[:12]]
    road += ["", f"**Close line:** {last}", ""]
    (out / "roadmap.md").write_text("\n".join(road), encoding="utf-8")
    emit({"ok": True, "script_md": str(out / "script.md"), "roadmap": str(out / "roadmap.md"),
          "narration": str(out / "narration.txt"), "seconds": T["total_seconds"]})


# --------------------------------------------------------------------------------------------------------- new

# Beat maps (R3 3.1 T1 to T4, R1 6, V3 ST1 and ST2), with the story roles the lint checks (V3 SR4)
SKELETONS = {
    "short": [("hook", "The most surprising moment or the contradiction, shown first; the promise by 3 s", ["hook"]),
              ("context", "Only what the viewer needs to see the gap (setup by 5 s)", ["identity"]),
              ("but", "The first complication: PP1, by about a third of the runtime", ["conflict", "pp1"]),
              ("so", "What it forces", ["choice"]),
              ("but", "A second turn, a small twist", ["conflict"]),
              ("payoff", "Answers the hook exactly: the change", ["change"]),
              ("loop", "A last line that closes the hook's loop; the value is shown, not stated", ["value"])],
    "ad": [("hook", "A person and a want, in the first frame; the product cue by 3 to 5 s", ["hook"]),
           ("problem", "The problem, specific", ["conflict"]),
           ("proof", "The product doing the job, a provable detail", ["pp1", "choice"]),
           ("result", "A specific result", ["change", "value"]),
           ("cta", "Verb, object, reason to act now; spoken and shown", ["cta"])],
    "youtube-long": [
        ("cold-open", "In medias res: the question in one sentence and the stakes (0 to 5 %)", ["hook"]),
        ("belief", "The common belief or normal world, what can be lost and gained, then the anomaly (5 to 20 %)",
         ["identity", "stakes_loss", "stakes_gain"]),
        ("investigate-1", "PP1 and the investigation; a BUT turn; end on a re-hook (10 to 35 %)", ["pp1", "conflict"]),
        ("investigate-2", "A second BUT turn; end on a re-hook", ["conflict"]),
        ("reversal", "The midpoint turn that reframes the question (40 to 55 %)", ["surprise"]),
        ("complication", "The best counter-argument, the cost (50 to 75 %)", ["conflict", "choice"]),
        ("low-point", "PP2: the favourite explanation fails or the stakes land (75 to 85 %)", ["pp2"]),
        ("answer", "The answer and what it means for the viewer (85 to 97 %)", ["change", "value"]),
        ("callback", "Back to the cold open; one CTA to the next video", ["cta"])],
    "talk": [("story-a", "Open story A at its peak", ["hook"]), ("what-is", "What is", ["identity"]),
             ("what-could-be", "What could be", ["stakes_gain", "stakes_loss"]),
             ("story-b", "Story B, with evidence", ["pp1", "conflict"]),
             ("core", "The core idea and the one moment to remember", ["key_moment", "pp2"]),
             ("close-b", "Close story B", ["change"]),
             ("close-a", "Close story A; the new normal and the ask", ["value", "cta"])],
}


def cmd_new(args):
    d = Path(args.dir).expanduser()
    if (d / "script.json").exists() or (d / "article.md").exists():
        die(f"{d} already holds a draft (never overwritten)")
    d.mkdir(parents=True, exist_ok=True)
    fmt = fmt_of(args.format)
    brief = {"schema": "nexa.brief/1", "client": "", "channel_or_brand": "", "topic": args.title or "",
             "goal": "", "platform": "", "format": fmt, "target_seconds": args.target, "lang": args.lang,
             "locale": "BD" if args.lang in ("bn", "banglish") else "", "mode": "nonfiction",
             "audience": {"who": "", "knows": "", "wants": "", "objections": []}, "voice": "",
             "facts_given": [], "must_include": [], "must_avoid": [], "level": "draft"}
    if not (d / "brief.json").exists():
        save_json(d / "brief.json", brief)
    if fmt == "blog":
        (d / "article.md").write_text("# Title (60 characters or fewer)\n\nAnswer first, in the first 100 words.\n",
                                      encoding="utf-8")
        emit({"ok": True, "files": [str(d / "brief.json"), str(d / "article.md")]})
        return
    kind = ("short" if fmt == "short" else "ad" if FORMATS[fmt].get("ad") else
            "talk" if FORMATS[fmt]["medium"] == "listen" else "youtube-long")
    beats = [{"id": f"b{i + 1}", "section": name, "purpose": hint, "roles": roles, "narration": "", "visual": "",
              "visual_type": "", "on_screen": "", "sound": "", "emotion": "", "loops_open": [], "loops_close": [],
              "claims": [], "tension": {"q": 0, "s": 0, "u": 0, "p": 0}}
             for i, (name, hint, roles) in enumerate(SKELETONS[kind])]
    is_ad = bool(FORMATS[fmt].get("ad"))
    meta = {"title": args.title or "", "format": fmt, "lang": args.lang, "target_seconds": args.target, "wpm": None,
            "mode": "ad" if is_ad else "nonfiction"}
    if is_ad:
        meta.update({"brand": "", "paid": False})
    if fmt == "short" or is_ad:
        meta["captions"] = True
    hook = {"type": "", "visual": "", "spoken": "", "caption": ""}
    script = {"schema": "nexa.script/1", "meta": meta,
              "promise": {"promise": "", "titles": [], "thumbnails": [], "first_line": "", "first_visual": "",
                          "tension": "", "payoff_at": "",
                          "hook_variants": [dict(hook) for _ in range(5 if is_ad else 1)]},
              "loops": {}, "story": {"mode": meta["mode"], "key_moment": "", "key_line": "", "reconstructed": []},
              "beats": beats, "cta": {"text": "", "beat": ""}, "sources": "research/pack.json"}
    save_json(d / "script.json", script)
    emit({"ok": True, "files": [str(d / "brief.json"), str(d / "script.json")], "beats": len(beats)})


# ------------------------------------------------------------------------------------------------ review loop

def checklist_for(fmt):
    data = load_json(CHECKLISTS)
    name = data.get("aliases", {}).get(fmt, fmt)
    if name not in data["formats"]:
        name = "youtube-long" if FORMATS.get(fmt, {}).get("medium") == "video" else "blog"
    return data["formats"][name]


def roster(value):
    return tuple(x.strip() for x in value.split(",") if x.strip()) if value else R.DEFAULT_ROSTER


def review_brief(brief, script):
    """The brief as judges and personas get it: plus how the video carries words for a muted viewer."""
    meta = script.get("meta") or {}
    if FORMATS[meta.get("format", "youtube-long")]["medium"] == "video" and meta.get("captions"):
        brief = dict(brief, captions="the narration is burned in as on-screen captions, so a muted viewer reads it")
    return brief


def cmd_judge(args):
    script = load_script(args.file)
    brief = review_brief(load_json(args.brief), script)
    cl = checklist_for(script["meta"]["format"])
    lines = narration_lines(script)
    past = load_json(args.past) if args.past else None
    res = R.judge(brief, lines, cl["items"], roster=roster(args.roster), runs=args.runs, past=past,
                  effort=args.effort, fresh=args.fresh)
    res["hard_fails_to_check"] = cl.get("hard_fails", [])
    res["lines"] = lines
    out = Path(args.out or Path(args.file).with_name("judge.json"))
    save_json(out, res)
    fails = [c for c in res["criteria"] if c["state"] == "fail"]
    unstable = [c["id"] for c in res["criteria"] if c["state"] == "unstable"]
    emit({"ok": not fails, "saved": str(out), "runs_ok": res["runs_ok"], "runs_total": res["runs_total"],
          "fail": [{"id": c["id"], "lines": c["lines"], "problems": c["problems"][:2]} for c in fails],
          "unstable": unstable, "scales": {k: v["median"] for k, v in res["scales"].items()},
          "best_lines": res["best_lines"]})


RETELL_SCHEMA = {"type": "object", "properties": {
    "retell": {"type": "array", "items": {"type": "string"}},
    "question": {"type": "string"}, "answer": {"type": "string"}, "turn": {"type": "string"},
    "change": {"type": "string"}, "explain_like_new": {"type": "string"},
    "unclear": {"type": "array", "items": {"type": "string"}}}}
MAP_SCHEMA = {"type": "object", "properties": {
    "covered": {"type": "array", "items": {"type": "string"}},
    "missing_key_lines": {"type": "array", "items": {"type": "object", "properties": {
        "line": {"type": "string"}, "why_it_matters": {"type": "string"}}}},
    "order_changed": {"type": "boolean"}, "order_note": {"type": "string"},
    "question_matches_promise": {"type": "boolean"}, "mechanism_explained": {"type": "boolean"},
    "note": {"type": "string"}}}


def cmd_understand(args):
    """V2's two machine judges and V5's summary test: a fresh reader retells the piece to a friend and explains it as
    a first-time learner; a second reader maps that retelling onto the numbered lines. Beats that drop out or change
    order point at an unclear structure; a mechanism the learner cannot explain points at a missing comparison."""
    script = load_script(args.file)
    brief = review_brief(load_json(args.brief), script)
    plain = spoken(text_of(script))
    lines = narration_lines(script)
    first = nexa_llm.call_json(
        nexa_llm.ONLY_THIS + "Read this once, the way a viewer meets it, then put it away.\n\n" + plain + "\n\n"
        "Now: retell it to a friend in five short sentences, in order; say the one question it answers and the answer; "
        "the turn (where things changed direction) and what changed from start to end; explain the main idea as "
        "someone learning it for the first time, in two or three sentences, using the piece's own comparison if it has "
        "one; list anything that was unclear on a single read.",
        RETELL_SCHEMA, engine=args.engine, effort="medium", fresh=args.fresh, who="understand-retell")
    if not first.get("ok"):
        die(f"the retell call failed: {first.get('error')}")
    retold = first["data"]
    second = nexa_llm.call_json(
        nexa_llm.ONLY_THIS + "A reader retold a script after one read. Compare the retelling with the script.\n\n"
        f"THE BRIEF\n{json.dumps(brief, ensure_ascii=False)}\n\nTHE SCRIPT (numbered lines)\n{R.render_lines(lines)}"
        f"\n\nTHE RETELLING\n{json.dumps(retold, ensure_ascii=False, indent=1)}\n\n"
        "List the line ids the retelling covers; the key lines it lost (a turn, a stake, a payoff, a number that "
        "matters), each with why it matters; whether the order of events changed; whether the question it names "
        "matches the brief's promise; whether the learner's explanation gets the mechanism right.",
        MAP_SCHEMA, engine=args.engine, effort="medium", fresh=args.fresh, who="understand-map")
    mapped = second.get("data") or {}
    res = {"schema": "nexa.understand/1", "retell": retold, "map": mapped,
           "ok": bool(second.get("ok")) and not mapped.get("missing_key_lines") and not mapped.get("order_changed")
           and mapped.get("question_matches_promise", True) and mapped.get("mechanism_explained", True),
           "engines": [first.get("engine"), second.get("engine")]}
    save_json(Path(args.file).with_name("understand.json"), res)
    emit(res)


def cmd_panel(args):
    if args.what == "build":
        brief = load_json(args.brief)
        ev = []
        if args.evidence:
            data = load_json(args.evidence)
            # a voice bank ({"items": [...]}), a research pack ({"voice_bank": [...]}) or a plain list
            items = (data.get("items") or data.get("voice_bank") or []) if isinstance(data, dict) else data
            for i, it in enumerate(items):
                text = (it.get("quote") or it.get("text")) if isinstance(it, dict) else str(it)
                if text:
                    ev.append({"id": (it.get("id") if isinstance(it, dict) else None) or f"v{i + 1}", "text": text,
                               "source": it.get("source") if isinstance(it, dict) else None})
        panel = R.build_panel(brief, ev, n=args.n, engine=args.engine, fresh=args.fresh)
        out = Path(args.dir).expanduser() / "panel.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        save_json(out, panel)
        emit({"ok": bool(panel["personas"]), "saved": str(out), "personas": len(panel["personas"]),
              "grounded_in": panel["evidence_count"], "grounded_cards": panel["grounded_cards"],
              "errors": panel["errors"][:3], "label": R.SYNTHETIC})
        return
    if args.what == "validate":
        panel = load_json(args.panel)
        data = load_json(args.items)
        items = data.get("items", []) if isinstance(data, dict) else data
        res = R.validate_panel(panel, items, fresh=args.fresh)
        if "spearman" in res:
            panel["validation"] = {"spearman": res["spearman"], "ok": res["ok"], "threshold": res["threshold"],
                                   "items": len(res["items"]), "source": str(args.items)}
            save_json(args.panel, panel)
        emit(res)
        sys.exit(0 if res["ok"] else 1)
    script = load_script(args.file)
    panel = load_json(args.panel)
    panel = dict(panel, brief=review_brief(panel.get("brief") or {}, script))
    lines = narration_lines(script)
    hooks = load_json(args.hooks) if args.hooks else None
    spec = FORMATS[script["meta"]["format"]]
    run = R.run_panel(panel, lines, medium=spec["medium"], hooks=hooks, intent=bool(spec.get("ad")),
                      fresh=args.fresh)
    judge = load_json(args.judge) if args.judge else None
    review = R.aggregate(panel, run, lines, judge_result=judge, hooks=hooks)
    base = Path(args.file).with_name
    save_json(base("panel-run.json"), run)
    save_json(base("review.json"), dict(review, lines=lines))
    emit({"ok": True, "saved": [str(base("panel-run.json")), str(base("review.json"))], "label": R.SYNTHETIC,
          "personas": review["personas"], "finished": review["finished"], "spikes": review["spikes"],
          "fixes": [{"line": f["line"], "tag": f["tag"], "support": f["support"], "quotes": f["quotes"][:2]}
                    for f in review["fixes"]], "keep": review["keep"], "noise": review["noise"],
          "act_on_panel": review["act_on_panel"], "validated": review["validated"],
          "comments": review["comments"][:10]})


def file_text(path):
    return spoken(text_of(load_script(path)))


def cmd_prefer(args):
    panel = load_json(args.panel)
    emit(R.panel_prefer(panel, file_text(args.old), file_text(args.new), fresh=args.fresh))


def cmd_tournament(args):
    """R10 5.4: ship the best version, not the last. Every pair is judged in both orders by the roster; a member's
    vote counts only when both orders agree."""
    if len(args.versions) < 2:
        die("a tournament needs two versions or more")
    brief = load_json(args.brief)
    texts = {p: file_text(p) for p in args.versions}
    wins = {p: 0 for p in args.versions}
    games = []
    for a, b in itertools.combinations(args.versions, 2):
        res = R.pairwise(brief, texts[a], texts[b], roster=roster(args.roster), effort=args.effort, fresh=args.fresh)
        wins[a] += res["tally"]["A"]
        wins[b] += res["tally"]["B"]
        games.append({"a": a, "b": b, "tally": res["tally"],
                      "winner": a if res["a_wins"] else b if res["b_wins"] else None,
                      "reasons": R.pair_reasons(res)})
    ranking = sorted(args.versions, key=lambda p: -wins[p])
    emit({"schema": "nexa.tournament/1", "ranking": [{"version": p, "wins": wins[p]} for p in ranking],
          "best": ranking[0] if wins[ranking[0]] > (wins[ranking[1]] if len(ranking) > 1 else -1) else None,
          "games": games, "note": "a tie at the top goes to a blind human read (R10 5.4)"})


def cmd_baselines(args):
    brief = load_json(args.brief)
    versions = R.generic_baselines(brief, n=args.n, fresh=args.fresh)
    out = Path(args.out or Path(args.brief).with_name("baselines.json"))
    save_json(out, {"schema": "nexa.baselines/1", "versions": versions})
    plain = []
    for i, text in enumerate(versions, 1):     # each plain draft as a file, ready to play in the tournament
        f = out.with_name(f"plain-{i}.txt")
        f.write_text(str(text).strip() + "\n", encoding="utf-8")
        plain.append(str(f))
    emit({"ok": bool(versions), "saved": str(out), "versions": len(versions), "plain": plain})


def cmd_guard(args):
    old_s, new_s = load_script(args.old), load_script(args.new)
    base = load_json(args.baselines).get("versions") if args.baselines else None
    keep = load_json(args.keep).get("keep") if args.keep else None
    res = R.blandness(spoken(text_of(old_s)), spoken(text_of(new_s)), baselines=base, budget=args.budget,
                      keep_lines=keep, old_lines=narration_lines(old_s), new_lines=narration_lines(new_s),
                      rewrite=args.rewrite)
    emit(res)
    sys.exit(0 if res["ok"] else 1)


def cmd_decide(args):
    lint = load_json(args.lint) if args.lint else {"ok": True}
    emit(R.decide(args.round, bool(lint.get("ok", True)), load_json(args.judge) if args.judge else None,
                  load_json(args.review) if args.review else None,
                  prefer=load_json(args.prefer) if args.prefer else None,
                  guard=load_json(args.guard) if args.guard else None, cap=args.cap))


def cmd_doctor(_args):
    emit({"ok": True, "skill_version": SKILL_VERSION, "engines": nexa_llm.engines_status(),
          "voice_lint": str(DESIGN) if DESIGN.exists() else "missing: install codex-design (natural-text's lint)",
          "checklists": str(CHECKLISTS), "formats": sorted(FORMATS), "aliases": ALIASES, "modes": list(MODES),
          "roles": list(ROLES)})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="script.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    p = sub.add_parser("new")
    p.add_argument("dir")
    p.add_argument("--format", required=True)
    p.add_argument("--lang", default="en")
    p.add_argument("--title")
    p.add_argument("--target", type=int)
    for name in ("lint", "timing"):
        q = sub.add_parser(name)
        q.add_argument("file")
        q.add_argument("--format")
        q.add_argument("--lang")
        if name == "lint":
            q.add_argument("--pack")
            q.add_argument("--voice", action="store_true", help="also run natural-text's lint (codex-design copylint)")
            q.add_argument("--level", default="draft", choices=["draft", "standard", "final"])
            q.add_argument("--json", action="store_true")
            q.add_argument("--keyword", help="blog: the primary query (at most two subheads carry it)")
            q.add_argument("--brief", help="brief.json: its objections answered, its goal's ask said, its bans kept")
        else:
            q.add_argument("--wpm", type=float)
    r = sub.add_parser("render")
    r.add_argument("file")
    r.add_argument("--out")
    j = sub.add_parser("judge")
    j.add_argument("file")
    j.add_argument("--brief", required=True)
    j.add_argument("--past")
    j.add_argument("--runs", type=int, default=2)
    j.add_argument("--roster")
    j.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    j.add_argument("--fresh", action="store_true")
    j.add_argument("--out")
    u = sub.add_parser("understand")
    u.add_argument("file")
    u.add_argument("--brief", required=True)
    u.add_argument("--engine", default="auto", choices=["auto", "codex", "gemini"])
    u.add_argument("--fresh", action="store_true")
    pn = sub.add_parser("panel")
    psub = pn.add_subparsers(dest="what", required=True)
    pb = psub.add_parser("build")
    pb.add_argument("dir")
    pb.add_argument("--brief", required=True)
    pb.add_argument("--evidence")
    pb.add_argument("--n", type=int, default=100)
    pb.add_argument("--engine", default="auto", choices=["auto", "codex", "gemini"])
    pb.add_argument("--fresh", action="store_true")
    pv = psub.add_parser("validate")
    pv.add_argument("--panel", required=True)
    pv.add_argument("--items", required=True, help="past pieces: [{id, text, actual}] (5 to 10, actual = real result)")
    pv.add_argument("--fresh", action="store_true")
    pr = psub.add_parser("run")
    pr.add_argument("file")
    pr.add_argument("--panel", required=True)
    pr.add_argument("--hooks")
    pr.add_argument("--judge")
    pr.add_argument("--fresh", action="store_true")
    pf = sub.add_parser("prefer")
    pf.add_argument("old")
    pf.add_argument("new")
    pf.add_argument("--panel", required=True)
    pf.add_argument("--fresh", action="store_true")
    tn = sub.add_parser("tournament")
    tn.add_argument("versions", nargs="+")
    tn.add_argument("--brief", required=True)
    tn.add_argument("--roster")
    tn.add_argument("--effort", default="medium", choices=["low", "medium", "high"])
    tn.add_argument("--fresh", action="store_true")
    bl = sub.add_parser("baselines")
    bl.add_argument("--brief", required=True)
    bl.add_argument("--n", type=int, default=3)
    bl.add_argument("--out")
    bl.add_argument("--fresh", action="store_true")
    g = sub.add_parser("guard")
    g.add_argument("old")
    g.add_argument("new")
    g.add_argument("--baselines")
    g.add_argument("--keep", help="a review.json (its keep list)")
    g.add_argument("--budget", type=float, default=0.25)
    g.add_argument("--rewrite", action="store_true",
                   help="a new draft after a hard failure: no edit budget or keep list, the other checks stay")
    d = sub.add_parser("decide")
    d.add_argument("--round", type=int, required=True)
    d.add_argument("--lint")
    d.add_argument("--judge")
    d.add_argument("--review")
    d.add_argument("--prefer")
    d.add_argument("--guard")
    d.add_argument("--cap", type=int, default=2)
    args = ap.parse_args(argv)
    {"doctor": cmd_doctor, "new": cmd_new, "lint": cmd_lint, "timing": cmd_timing, "render": cmd_render,
     "judge": cmd_judge, "understand": cmd_understand, "panel": cmd_panel, "prefer": cmd_prefer,
     "tournament": cmd_tournament, "baselines": cmd_baselines, "guard": cmd_guard, "decide": cmd_decide}[args.cmd](args)


if __name__ == "__main__":
    main()
