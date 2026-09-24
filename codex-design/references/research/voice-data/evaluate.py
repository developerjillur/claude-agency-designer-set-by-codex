"""python3 evaluate.py : check scripts/voice_rules.json after a rebuild: the calibration lines (natural lines get no
finding, robotic ones are caught), each rule's own bad and good lines, and, when the corpora are given, how often each
rule fires on real brand copy. The 2026-09-24 run used 1,671 Bluesky brand posts (casual-src/bsky_brand_corpus.json)
and 308 Bangladeshi Meta ads (bn-src/adlib_brands*.json); they are third-party texts and are not kept here, so pass
their folder as VOICE_CORPUS to repeat that part."""
import collections
import importlib.util
import json
import os
import sys
from pathlib import Path

HERE = Path(os.environ.get("VOICE_CORPUS") or Path(__file__).resolve().parent)
SKILL = Path.home() / ".claude/skills/codex-design"
spec = importlib.util.spec_from_file_location("cr", SKILL / "scripts/copyrules.py")
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

rules = json.loads((SKILL / "scripts/voice_rules.json").read_text(encoding="utf-8"))["rules"]
cal = json.loads((SKILL / "tests/data/voice_calibration.json").read_text(encoding="utf-8"))

print("== calibration")
bad_nat = 0
for lang, v in cal.items():
    loc = "BD" if lang == "bn" else ""
    for line in v["natural"]:
        f = cr.lint_string(line, "body", loc, "", lang)
        if f:
            bad_nat += 1
            print("  NATURAL FLAGGED", lang, line[:80], [(x["code"], x["message"][:60]) for x in f])
    caught = sum(1 for line in v["robotic"] if cr.lint_string(line, "body", loc, "", lang))
    if caught / len(v["robotic"]) < 0.95:
        print("  LOW RECALL", lang, caught, len(v["robotic"]))
print("  natural lines flagged:", bad_nat)

print("== each rule on its own bad and good lines")
fails = 0
for r in rules:
    if "bad" not in r:
        continue
    rx = cr._rule_regex(r)
    nb = len(rx.findall(r["bad"]))
    ng = len(rx.findall(r["good"])) if r.get("good") else 0
    need = r.get("min", 1)
    if nb < need or ng >= need:
        fails += 1
        print("  FAIL", r["id"], "bad hits", nb, "good hits", ng, "need", need, "|", r["bad"][:60], "|", r["good"][:60])
print("  rule self-test failures:", fails)

if not (HERE / "casual-src/bsky_brand_corpus.json").exists():
    sys.exit(0)  # no corpora: the calibration and the rules' own lines are the check
print("== English brand posts")
posts = json.loads((HERE / "casual-src/bsky_brand_corpus.json").read_text(encoding="utf-8"))
texts = [p["text"] for p in posts if p.get("text")]
hits = collections.Counter()
examples = {}
en_rules = [(cr._rule_regex(r), r) for r in rules if r["lang"] in ("en", "mul") and r.get("scope", "") in ("", "casual")]
for t in texts:
    for rx, r in en_rules:
        n = len(rx.findall(t))
        if n >= r.get("min", 1):
            hits[r["id"]] += 1
            examples.setdefault(r["id"], t[:140].replace("\n", " / "))
print(f"  {len(texts)} posts; rules that fire at all: {len(hits)}")
for rid, n in hits.most_common(40):
    r = next(x for x in rules if x["id"] == rid)
    print(f"  {n:4d} {rid} {r['level']:7s} {r['what'][:60]!r} | e.g. {examples[rid]!r}")
codes = collections.Counter()
per_post = 0
for t in texts:
    fs = [f for f in cr.lint_caption(t, "x", "", "", None, "caption") if f["severity"] in ("warning", "error")]
    per_post += bool(fs)
    for f in fs:
        codes[f["code"]] += 1
print("  posts with any warning or error (full lint, platform x):", per_post, f"({per_post / len(texts):.1%})")
print("  by code:", codes.most_common(25))

print("== Bangladeshi brand ads")
ads = []
for fn in ("bn-src/adlib_brands.json", "bn-src/adlib_brands2.json"):
    for brand, v in json.loads((HERE / fn).read_text(encoding="utf-8")).items():
        ads += [c["body"] for c in v.get("brand_cards", []) if c.get("body")]
ads = list(dict.fromkeys(ads))
bn_rules = [(cr._rule_regex(r), r) for r in rules if r["lang"] in ("bn", "mul") and r.get("scope", "") in ("", "casual")]
hits = collections.Counter()
examples = {}
for t in ads:
    for rx, r in bn_rules:
        if len(rx.findall(t)) >= r.get("min", 1):
            hits[r["id"]] += 1
            examples.setdefault(r["id"], t[:120].replace("\n", " / "))
print(f"  {len(ads)} ads; rules that fire at all: {len(hits)}")
for rid, n in hits.most_common(30):
    r = next(x for x in rules if x["id"] == rid)
    print(f"  {n:4d} {rid} {r['level']:7s} {r['what'][:60]!r} | e.g. {examples[rid]!r}")
