#!/usr/bin/env python3
"""nexa-copy: the tools behind the copy skill. Claude researches and writes; this checks every field against its
platform, the claims against the research pack and the words against natural-text, and runs the review loop (judges
from other model families, a simulated audience panel, pairwise preference) plus the test-plan arithmetic.

  copywriter.py doctor
  copywriter.py types                               every copy type, its fields and limits
  copywriter.py new DIR --type TYPE --lang en|bn|banglish [--variants 3] [--brand B]
  copywriter.py lint FILE [--brief brief.json] [--pack research/pack.json] [--level draft|final] [--no-voice] [--json]
  copywriter.py render FILE [--out DIR]             copy.md: every field with its count against the limit
  copywriter.py judge FILE --brief brief.json [--variant A] [--runs 2] [--roster codex,gemini:MODEL]
  copywriter.py panel build DIR --brief brief.json [--evidence research/pack.json] [--n 100]
  copywriter.py panel validate --panel panel.json --items past.json
  copywriter.py panel run FILE --panel panel.json [--variant A] [--hooks hooks.json] [--judge judge.json]
  copywriter.py hooks FILE [--pack research/pack.json]   the variants' openers beside real competitor openers
  copywriter.py prefer OLD NEW --panel panel.json [--variant A]
  copywriter.py tournament FILE [FILE2 ...] --brief brief.json   the best variant or version, both orders
  copywriter.py baselines --brief brief.json | guard OLD NEW | decide --round N ...
  copywriter.py sample --baseline 0.03 --lift 0.2 [--alpha 0.05] [--power 0.8]

FILE is a copy.json (`nexa.copy/1`) or a text file (one field of --type). Research notes behind the rules: R5
conversion copywriting, R6 email and outbound, R7 product copy, R10 judges and panels (references/research/).
"""
import argparse
import itertools
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nexa_llm  # noqa: E402
import nexa_review as R  # noqa: E402
from copy_lint import DESIGN, doc_text, lint_copy, load_platforms, voice_pass  # noqa: E402
from copy_lint import load_copy as read_copy  # noqa: E402

SKILL_VERSION = "2026.09.26.1"
CHECKLISTS = HERE.parent / "references" / "checklists.json"


def load_copy(path, ctype=None, lang=None):
    try:
        return read_copy(path, ctype, lang)
    except (OSError, ValueError) as e:
        die(f"cannot read {path}: {e}")


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


def profile(doc):
    types = load_platforms()["types"]
    t = doc["meta"].get("type")
    if t not in types:
        die(f"unknown type {t!r}: run `copywriter.py types`")
    return types[t]


def copy_lines(doc, variant=None):
    """Numbered lines for judges and personas: the fields of one variant in reading order, each with its role."""
    vs = doc["variants"]
    v = next((x for x in vs if x.get("id") == variant), None) if variant else vs[0]
    if v is None:
        die(f"no variant {variant!r} (have {', '.join(str(x.get('id')) for x in vs)})")
    units = [{"text": f.get("text", ""), "beat": v.get("id"), "role": f.get("role")} for f in v.get("fields") or []
             if f.get("role") not in ("search_terms", "tag") and (f.get("text") or "").strip()]
    return R.number_lines(units), v


def review_brief(brief, doc):
    """The brief as judges and personas get it: plus the placement, its family and the reader's awareness."""
    prof = profile(doc)
    extra = {"placement": prof["label"], "family": prof["family"]}
    if doc["meta"].get("awareness"):
        extra["awareness"] = doc["meta"]["awareness"]
    return dict(brief, **extra)


# ------------------------------------------------------------------------------------------------------ lint

def cmd_lint(args):
    doc = load_copy(args.file, args.type, args.lang)
    pack = load_json(args.pack) if args.pack else None
    level = "final" if args.level == "final" else "draft"
    res = lint_copy(doc, pack, level, load_json(args.brief) if args.brief else None)
    if not args.no_voice:
        v = voice_pass(doc)
        res["voice"] = {"ran": v.get("ran"), "why": v.get("why")}
        if v.get("ran"):
            res["errors"] += v["errors"]
            res["warnings"] += v["warnings"]
            res["notes"] += v["notes"]
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
                          **res["stats"]}, ensure_ascii=False))
    sys.exit(0 if res["ok"] else 1)


def cmd_types(_args):
    data = load_platforms()
    emit({"verified_on": data["verified_on"],
          "types": {t: {"family": p["family"], "label": p["label"], "fields": p["fields"]}
                    for t, p in data["types"].items()}})


# ------------------------------------------------------------------------------------------------------ new

def cmd_new(args):
    d = Path(args.dir).expanduser()
    if (d / "copy.json").exists():
        die(f"{d} already holds a draft (never overwritten)")
    types = load_platforms()["types"]
    if args.type not in types:
        die(f"unknown type {args.type!r}: run `copywriter.py types`")
    prof = types[args.type]
    d.mkdir(parents=True, exist_ok=True)
    locale = "BD" if args.lang in ("bn", "banglish") else ""
    brief = {"schema": "nexa.copy-brief/1", "client": "", "brand": args.brand or "", "product": "",
             "reader": {"who": "", "situation": "", "job": "", "objections": []},
             "awareness": "problem", "sophistication": "", "offer": "", "placement": prof["label"],
             "action": "", "facts_given": [], "proof": [], "voc": [], "voice": "", "must_avoid": [],
             "deadline": "", "region": "", "lang": args.lang, "locale": locale}
    if not (d / "brief.json").exists():
        save_json(d / "brief.json", brief)
    fields = []
    for role, spec in prof["fields"].items():
        fields += [{"role": role, "text": "", "claims": []} for _ in range(max(1, spec.get("min_count", 1)))]
    if args.variants is not None and not 1 <= args.variants <= 10:
        die("--variants is 1 to 10")
    n = args.variants or (3 if prof["family"] == "ad" else 1)
    doc = {"schema": "nexa.copy/1",
           "meta": {"type": args.type, "lang": args.lang, "locale": locale, "brand": args.brand or "",
                    "awareness": "problem", "mode": "ad" if prof["family"] == "ad" else "nonfiction"},
           "variants": [{"id": chr(65 + i), "angle": "", "awareness": "", "fields": [dict(f) for f in fields]}
                        for i in range(n)],
           "test_plan": {"hypothesis": "", "metric": "", "sample": ""} if prof["family"] == "ad" else {}}
    save_json(d / "copy.json", doc)
    emit({"ok": True, "files": [str(d / "brief.json"), str(d / "copy.json")], "type": args.type,
          "fields": list(prof["fields"]), "variants": n})


# ---------------------------------------------------------------------------------------------------- render

def cmd_render(args):
    doc = load_copy(args.file)
    prof = profile(doc)
    out = Path(args.out or Path(args.file).parent)
    out.mkdir(parents=True, exist_ok=True)
    md = [f"# {prof['label']}", "", f"Type `{doc['meta'].get('type')}`, language {doc['meta'].get('lang', 'en')}; "
          f"limits as read on {load_platforms()['verified_on']}.", ""]
    for v in doc["variants"]:
        md += [f"## Variant {v.get('id')}" + (f": {v['angle']}" if v.get("angle") else ""), "",
               "| Field | Copy | Count | Limit |", "|---|---|---|---|"]
        for f in v.get("fields") or []:
            spec = prof["fields"].get(f.get("role"), {})
            text = (f.get("text") or "").replace("|", "/").replace("\n", " ")
            limit = spec.get("max_chars") or (spec.get("rec_chars") or [None, None])[1] or \
                (f"{spec['rec_words'][0]} to {spec['rec_words'][1]} words" if spec.get("rec_words") else "")
            md.append(f"| {f.get('role')} | {text} | {len(f.get('text') or '')} | {limit or ''} |")
        md.append("")
    tp = doc.get("test_plan") or {}
    if any(tp.values()):
        md += ["## Test plan", ""] + [f"- **{k}:** {v}" for k, v in tp.items() if v] + [""]
    (out / "copy.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    emit({"ok": True, "copy_md": str(out / "copy.md"), "variants": len(doc["variants"])})


# ------------------------------------------------------------------------------------------------ review loop

def checklist_for(doc):
    data = load_json(CHECKLISTS)
    fam = profile(doc)["family"]
    return data["formats"].get(fam) or data["formats"]["post"]


def roster(value):
    return tuple(x.strip() for x in value.split(",") if x.strip()) if value else R.DEFAULT_ROSTER


def cmd_judge(args):
    doc = load_copy(args.file)
    brief = review_brief(load_json(args.brief), doc)
    cl = checklist_for(doc)
    lines, v = copy_lines(doc, args.variant)
    if len(doc["variants"]) > 1:
        brief = dict(brief, other_variants=[doc_text(doc, x.get("id")) for x in doc["variants"] if x is not v][:4])
    res = R.judge(brief, lines, cl["items"], roster=roster(args.roster), runs=args.runs, effort=args.effort,
                  fresh=args.fresh)
    res["hard_fails_to_check"] = cl.get("hard_fails", [])
    res["lines"] = lines
    res["variant"] = v.get("id")
    out = Path(args.out or Path(args.file).with_name(f"judge-{v.get('id')}.json"))
    save_json(out, res)
    fails = [c for c in res["criteria"] if c["state"] == "fail"]
    emit({"ok": not fails, "saved": str(out), "variant": v.get("id"), "runs_ok": res["runs_ok"],
          "runs_total": res["runs_total"],
          "fail": [{"id": c["id"], "lines": c["lines"], "problems": c["problems"][:2]} for c in fails],
          "unstable": [c["id"] for c in res["criteria"] if c["state"] == "unstable"],
          "scales": {k: x["median"] for k, x in res["scales"].items()}, "best_lines": res["best_lines"]})


def evidence_from(path):
    data = load_json(path)
    items = (data.get("items") or data.get("voice_bank") or []) if isinstance(data, dict) else data
    ev = []
    for i, it in enumerate(items):
        text = (it.get("quote") or it.get("text")) if isinstance(it, dict) else str(it)
        if text:
            ev.append({"id": (it.get("id") if isinstance(it, dict) else None) or f"v{i + 1}", "text": text,
                       "source": it.get("source") if isinstance(it, dict) else None})
    return ev


def cmd_panel(args):
    if args.what == "build":
        panel = R.build_panel(load_json(args.brief), evidence_from(args.evidence) if args.evidence else [],
                              n=args.n, engine=args.engine, fresh=args.fresh)
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
        res = R.validate_panel(panel, data.get("items", []) if isinstance(data, dict) else data, fresh=args.fresh)
        if "spearman" in res:
            panel["validation"] = {"spearman": res["spearman"], "ok": res["ok"], "threshold": res["threshold"],
                                   "items": len(res["items"]), "source": str(args.items)}
            save_json(args.panel, panel)
        emit(res)
        sys.exit(0 if res["ok"] else 1)
    doc = load_copy(args.file)
    panel = load_json(args.panel)
    panel = dict(panel, brief=review_brief(panel.get("brief") or {}, doc))
    lines, v = copy_lines(doc, args.variant)
    hooks = load_json(args.hooks) if args.hooks else None
    fam = profile(doc)["family"]
    run = R.run_panel(panel, lines, medium="read", hooks=hooks,
                      intent=fam in ("ad", "email", "outbound", "product", "landing"), fresh=args.fresh)
    judge = load_json(args.judge) if args.judge else None
    review = R.aggregate(panel, run, lines, judge_result=judge, hooks=hooks)
    base = Path(args.file).with_name
    save_json(base(f"panel-run-{v.get('id')}.json"), run)
    save_json(base(f"review-{v.get('id')}.json"), dict(review, lines=lines))
    emit({"ok": True, "variant": v.get("id"), "label": R.SYNTHETIC, "personas": review["personas"],
          "finished": review["finished"], "actions": review["actions"],
          "fixes": [{"line": f["line"], "tag": f["tag"], "support": f["support"], "quotes": f["quotes"][:2]}
                    for f in review["fixes"]], "keep": review["keep"], "hook": review["hook"],
          "noise": review["noise"], "act_on_panel": review["act_on_panel"], "validated": review["validated"],
          "comments": review["comments"][:10]})


def cmd_hooks(args):
    """The feed-stop lineup (R10 T1): each variant's opening line as a draft hook beside real competitor openers from
    the research pack (competitors with a `hook` and a known `result`)."""
    doc = load_copy(args.file)
    hooks = []
    for v in doc["variants"]:
        lines, _ = copy_lines(doc, v.get("id"))
        if lines:
            hooks.append({"id": f"H{v.get('id')}", "text": lines[0]["text"], "draft": True})
    if args.pack:
        for i, c in enumerate((load_json(args.pack).get("competitors") or [])[:8], 1):
            if c.get("hook"):
                hooks.append({"id": f"R{i}", "text": c["hook"], "result": c.get("result") or c.get("views")})
    out = Path(args.out or Path(args.file).with_name("hooks.json"))
    save_json(out, hooks)
    emit({"ok": True, "saved": str(out), "draft": sum(1 for h in hooks if h.get("draft")),
          "real": sum(1 for h in hooks if not h.get("draft")),
          "note": "6 to 8 real openers with known results make the stop rates comparable (R10 5.2)"})


def cmd_prefer(args):
    panel = load_json(args.panel)
    old, new = load_copy(args.old), load_copy(args.new)
    emit(R.panel_prefer(panel, doc_text(old, args.variant), doc_text(new, args.variant), fresh=args.fresh))


def cmd_tournament(args):
    """R10 5.4: the best version, not the last. With one file, its variants play each other; with several files,
    the files do (their first variant, or --variant)."""
    brief = load_json(args.brief)
    if len(args.files) == 1:
        doc = load_copy(args.files[0])
        brief = review_brief(brief, doc)
        entries = {str(v.get("id")): doc_text(doc, v.get("id")) for v in doc["variants"]}
    else:
        entries = {p: doc_text(load_copy(p), args.variant) for p in args.files}
    if len(entries) < 2:
        die("a tournament needs two entries or more")
    wins = {k: 0 for k in entries}
    games = []
    for a, b in itertools.combinations(entries, 2):
        res = R.pairwise(brief, entries[a], entries[b], roster=roster(args.roster), effort=args.effort,
                         fresh=args.fresh, question="Which would the reader in the brief rather act on, and which "
                                                     "serves the brief better and more honestly?")
        wins[a] += res["tally"]["A"]
        wins[b] += res["tally"]["B"]
        games.append({"a": a, "b": b, "tally": res["tally"],
                      "winner": a if res["a_wins"] else b if res["b_wins"] else None,
                      "reasons": R.pair_reasons(res)})
    ranking = sorted(entries, key=lambda k: -wins[k])
    best = ranking[0] if wins[ranking[0]] > wins[ranking[1]] else None
    emit({"schema": "nexa.tournament/1", "ranking": [{"entry": k, "wins": wins[k]} for k in ranking], "best": best,
          "games": games, "note": "a tie at the top goes to a blind human read; real tests decide paid copy"})


def cmd_baselines(args):
    versions = R.generic_baselines(load_json(args.brief), n=args.n, fresh=args.fresh)
    out = Path(args.out or Path(args.brief).with_name("baselines.json"))
    save_json(out, {"schema": "nexa.baselines/1", "versions": versions})
    plain = []
    for i, text in enumerate(versions, 1):     # each plain draft as a file, ready to play in the tournament
        f = out.with_name(f"plain-{i}.txt")
        f.write_text(str(text).strip() + "\n", encoding="utf-8")
        plain.append(str(f))
    emit({"ok": bool(versions), "saved": str(out), "versions": len(versions), "plain": plain})


def cmd_guard(args):
    old, new = load_copy(args.old), load_copy(args.new)
    base = load_json(args.baselines).get("versions") if args.baselines else None
    keep = load_json(args.keep).get("keep") if args.keep else None
    old_lines, _ = copy_lines(old, args.variant)
    new_lines, _ = copy_lines(new, args.variant)
    res = R.blandness(doc_text(old, args.variant), doc_text(new, args.variant), baselines=base, budget=args.budget,
                      keep_lines=keep, old_lines=old_lines, new_lines=new_lines, rewrite=args.rewrite)
    emit(res)
    sys.exit(0 if res["ok"] else 1)


def cmd_decide(args):
    lint = load_json(args.lint) if args.lint else {"ok": True}
    emit(R.decide(args.round, bool(lint.get("ok", True)), load_json(args.judge) if args.judge else None,
                  load_json(args.review) if args.review else None,
                  prefer=load_json(args.prefer) if args.prefer else None,
                  guard=load_json(args.guard) if args.guard else None, cap=args.cap))


# ----------------------------------------------------------------------------------------------- test plans

def norm_ppf(p):
    """The inverse of the standard normal distribution (Acklam's rational approximation, error under 1.2e-9)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02,
         -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01,
         -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00,
         4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    lo, hi = 0.02425, 1 - 0.02425
    if p < lo:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p > hi:
        return -norm_ppf(1 - p)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)


def sample_size(baseline, lift, alpha=0.05, power=0.80):
    """Visitors per variant to detect a relative lift in a conversion rate: the standard two-proportion formula,
    two-sided (R5 §8: a 5 % baseline and +20 % give 8,158 visitors)."""
    p1, p2 = baseline, baseline * (1 + lift)
    za, zb = norm_ppf(1 - alpha / 2), norm_ppf(power)
    pbar = (p1 + p2) / 2
    n = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / (p2 - p1) ** 2
    return math.ceil(n)


def cmd_sample(args):
    if not 0 < args.baseline < 1 or args.lift <= 0:
        die("--baseline is a rate between 0 and 1 (0.03 for 3 %); --lift a relative lift above 0 (0.2 for +20 %)")
    if not 0 < args.alpha < 1 or not 0 < args.power < 1:
        die("--alpha and --power are between 0 and 1 (0.05 and 0.8 are the usual values)")
    if args.baseline * (1 + args.lift) >= 1:
        die("the baseline and the lift give a rate of 100 % or more")
    n = sample_size(args.baseline, args.lift, args.alpha, args.power)
    emit({"visitors_per_variant": n, "conversions_per_variant": round(n * args.baseline),
          "baseline": args.baseline, "lift": args.lift, "alpha": args.alpha, "power": args.power,
          "rules": ["fix the sample before launch; peeking turned a 5 % false-positive rate into 26.1 % (Evan Miller)",
                    "run whole weeks, one primary metric, check the lift holds downstream (qualified leads, revenue)",
                    "small accounts test bold differences (angle, offer), not synonyms"]})


def cmd_doctor(_args):
    data = load_platforms()
    emit({"ok": True, "skill_version": SKILL_VERSION, "engines": nexa_llm.engines_status(),
          "voice_lint": str(DESIGN) if DESIGN.exists() else "missing: install codex-design (natural-text's lint)",
          "platforms_verified_on": data["verified_on"], "types": len(data["types"]), "checklists": str(CHECKLISTS)})


def main(argv=None):
    ap = argparse.ArgumentParser(prog="copywriter.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    sub.add_parser("types")
    p = sub.add_parser("new")
    p.add_argument("dir")
    p.add_argument("--type", required=True)
    p.add_argument("--lang", default="en")
    p.add_argument("--variants", type=int)
    p.add_argument("--brand")
    q = sub.add_parser("lint")
    q.add_argument("file")
    q.add_argument("--type")
    q.add_argument("--lang")
    q.add_argument("--pack")
    q.add_argument("--level", default="draft", choices=["draft", "standard", "final"])
    q.add_argument("--no-voice", action="store_true", help="skip natural-text's lint (codex-design copylint)")
    q.add_argument("--brief", help="brief.json: its objections answered, the reader's situation, its action, its bans")
    q.add_argument("--json", action="store_true")
    r = sub.add_parser("render")
    r.add_argument("file")
    r.add_argument("--out")
    j = sub.add_parser("judge")
    j.add_argument("file")
    j.add_argument("--brief", required=True)
    j.add_argument("--variant")
    j.add_argument("--runs", type=int, default=2)
    j.add_argument("--roster")
    j.add_argument("--effort", default="high", choices=["low", "medium", "high"])
    j.add_argument("--fresh", action="store_true")
    j.add_argument("--out")
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
    pv.add_argument("--items", required=True)
    pv.add_argument("--fresh", action="store_true")
    pr = psub.add_parser("run")
    pr.add_argument("file")
    pr.add_argument("--panel", required=True)
    pr.add_argument("--variant")
    pr.add_argument("--hooks")
    pr.add_argument("--judge")
    pr.add_argument("--fresh", action="store_true")
    hk = sub.add_parser("hooks")
    hk.add_argument("file")
    hk.add_argument("--pack")
    hk.add_argument("--out")
    pf = sub.add_parser("prefer")
    pf.add_argument("old")
    pf.add_argument("new")
    pf.add_argument("--panel", required=True)
    pf.add_argument("--variant")
    pf.add_argument("--fresh", action="store_true")
    tn = sub.add_parser("tournament")
    tn.add_argument("files", nargs="+")
    tn.add_argument("--brief", required=True)
    tn.add_argument("--variant")
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
    g.add_argument("--variant")
    g.add_argument("--baselines")
    g.add_argument("--keep")
    g.add_argument("--budget", type=float, default=0.25)
    g.add_argument("--rewrite", action="store_true")
    d = sub.add_parser("decide")
    d.add_argument("--round", type=int, required=True)
    d.add_argument("--lint")
    d.add_argument("--judge")
    d.add_argument("--review")
    d.add_argument("--prefer")
    d.add_argument("--guard")
    d.add_argument("--cap", type=int, default=2)
    s = sub.add_parser("sample")
    s.add_argument("--baseline", type=float, required=True)
    s.add_argument("--lift", type=float, required=True)
    s.add_argument("--alpha", type=float, default=0.05)
    s.add_argument("--power", type=float, default=0.80)
    args = ap.parse_args(argv)
    {"doctor": cmd_doctor, "types": cmd_types, "new": cmd_new, "lint": cmd_lint, "render": cmd_render,
     "judge": cmd_judge, "panel": cmd_panel, "hooks": cmd_hooks, "prefer": cmd_prefer, "tournament": cmd_tournament,
     "baselines": cmd_baselines, "guard": cmd_guard, "decide": cmd_decide, "sample": cmd_sample}[args.cmd](args)


if __name__ == "__main__":
    main()
