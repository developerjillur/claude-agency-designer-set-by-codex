"""python3 build_voice_rules.py : merge the research lint candidates into codex-design's scripts/voice_rules.json,
and the calibration lines into tests/data/voice_calibration.json. Then run evaluate.py.

Inputs (whichever exist, next to this script): languages-casual.json, bangla-casual.json, casual-craft-en.json,
humanizer-skills.json. Each candidate: {lang, kind, match, replacement, level, why, evidence, false_positive_risk},
and in humanizer-skills.json also bad_example and good_example.
- every pattern must compile with the lint's own rules (copyrules._rule_regex);
- no em dash or spaced en dash in any text field but the pattern;
- a candidate whose literal is already in the hand-written lists (AI_WORDS_EN, BN_FORMAL ...) is skipped;
- duplicates (same lang and pattern) keep the first; a humanizer rule written in prose (its pattern misses its own
  bad example) is left to code or the judge;
- regional tags become a language plus markets (TAGS), and OVERRIDES holds the changes the calibration run made.
Prints what it kept and skipped. `python3 build_voice_rules.py a.json b.json` builds from those files only.
"""
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = Path.home() / ".claude/skills/codex-design"
spec = importlib.util.spec_from_file_location("copyrules", SKILL / "scripts/copyrules.py")
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

SOURCES = {"languages-casual.json": "voice-languages.md", "bangla-casual.json": "voice-bangla.md",
           "casual-craft-en.json": "voice-casual-en.md", "humanizer-skills.json": "voice-humanizer-skills.md"}
DASH = re.compile("[—―⸺⸻]|--| – ")
KNOWN = {w.lower() for w in list(cr.AI_WORDS_EN) + list(cr.AI_WORDS_EN_SOFT) + list(cr.BN_FORMAL)
         + list(cr.BN_WB_FOR_BD) + list(cr.BN_KIN_NOTE)}


def candidates(data):
    return data if isinstance(data, list) else data.get("lint_candidates", [])


LATAM = ["419", "MX", "AR", "CO", "CL", "PE", "VE", "EC", "GT", "CU", "BO", "DO", "HN", "PY", "SV", "NI", "CR", "PA",
         "UY", "PR", "US"]
# humanizer-skills.json tags: a regional tag becomes the language plus the markets the rule is for. pt-BR and zh-CN
# rules are general AI tells, so they run for every market; pt-PT, zh-TW, es-419, ar-EG and Levantine rules flag the
# other variant's words, so they run only when the copy is for that market.
TAGS = {"bn-bd": ("bn", None), "zh-cn": ("zh", None), "zh-tw": ("zh", ["TW"]), "pt-br": ("pt", None),
        "pt-pt": ("pt", ["PT"]), "es-419": ("es", LATAM), "ar-eg": ("ar", ["EG"]), "apc": ("ar", ["LB", "SY", "JO", "PS"])}
IN_PYTHON = re.compile(r"^platform x:|link in \(\?:my \|our \|the \)\?bio")  # written as code in lint_caption
DUPLICATE = {25: "inflected tier-1 verbs: copyrules.INFLECT_EN", 40: "utilize and in order to: en voice rules",
             44: "rest assured, peace of mind: en voice rules", 103: "the busy-life opener: bn voice rules"}


# Calibrated after the merge (eval/evaluate.py: calibration lines, each rule's own lines, 1,671 Bluesky brand posts,
# 308 Bangladeshi Meta ads). Keyed by language and the start of the pattern.
OVERRIDES = [
    ("de", r"(?i)\bnicht nur\b", {"min": 3, "bad": "Nicht nur schnell, sondern auch günstig. Nicht nur frisch, sondern "
                                   "auch regional. Nicht nur lecker, sondern auch gesund."}),
    # "twice on a page is style, in every paragraph a signal"
    ("de", r"(?<![\d.,])\d+\.\d{1,2}", {"match": r"(?<![\d.,])\d+\.\d{2}(?![\d.])\s?(?:€|EUR\b|Euro\b)|€\d"}),
    # Swiss prices (4.50 Fr.) and the Austrian "€ 9,90" are right; the tell is a US decimal point next to the euro
    ("en", r"(?im)(?:^|(?<=[.!?]\s))(?:(?:let me be", {"min": 2, "level": "note", "bad": "Real talk: our first batch "
                                                       "cracked. Honestly? We learned a lot."}),  # one "Honestly?" is a person
    ("en", r"(?i)\b(?:what sets (?:us|it|them", {"sub": ("|deep[- ]dive", "")}),  # "gameplay deep dive" is plain
    ("en", r"\b(?:what nobody tells you about", {"level": "note"}),  # fine when a truly little-known fact follows
    ("ar", r"(?:^|\s)(?:تم|تمت|يتم|سيتم)", {"bad": "تم تجهيز طلبك. سيتم توصيله خلال ساعتين"}),  # fine once
    ("en", r"(?:[^,.!?;]+,){3,}", {"match": r"(?:[^,.!?;]{1,60},){3,}[^,.!?;]{0,80}\b(?:and|or)\b"}),  # bounded: the
    # open run was quadratic on long text without commas
    ("bn", r"[ঀ-৿]\s+।", {"drop": True}),  # the same as the earlier "space before the দাঁড়ি" note
    ("bn", r"[A-Za-z0-9]\s(?:এর|তে|কে)", {"level": "note", "what": "a space between a Latin word and its Bengali "
                                           "ending (Daraz এর); Bangla Academy style joins them: Daraz-এর"}),
]


# What a reader of the lint sees: the problem, not how the research compared it with the lint.
CLEAN = [
    (r"^The skill bans greeting openers but the lint knows only English and Bengali ones; these are the ", "Greeting "
     "openers in their "),
    (r";?\s*the (?:global rule bans greeting openers and the )?lint (?:only knew|knows only|had no|cannot know)[^;]*", ""),
    (r"^'X doesn't just A, it Bs' escapes the current rule.*", "'X doesn't just A, it Bs'"),
    (r"^extends the self-answered-question pattern \([^)]*\) to ", "a question the copy answers itself: "),
    (r"^Brazilian repos call 'Não é X, é Y' the number-one tell", "'Não é X, é Y', the tell Brazilian writers name first"),
    (r"^empty superlatives: .*", "empty superlatives with no proof behind them"),
    (r"^Box-drawing rule used as a dash slips past the em-dash check", "a box-drawing line used as a dash"),
    (r"\s*\((?:the current rule needs a digit|'Hot take:' is already linted)\)", ""),
    (r"\s*(?:that|which) (?:the current [\w -]+?|copyrules' [\w -]+?) (?:misses|miss)\b:?", ""),
    (r"\s*that the current list (\([^)]*\)) misses", r" \1"),
    (r"\s*that the current [\w -]+? misses:.*", ""),
    (r"\s*that (?:BAIT_RX and the _EN bait pattern|copyrules only checks in English)(?: miss)?", ""),
    (r"\s*(?:missing from|not in|beyond) (?:the current|copyrules'?|the copyrules|AI_WORDS_EN|the pt or pt-BR)"
     r"(?: [\w'-]+)*?(?: list| pattern| entries| rule)?(?=[:;(]|$| \()", ""),
    (r"\s*beyond copyrules' .*", ""),
    (r"\s*(?:;\s*)?not yet in the spelling pattern.*", ""),
    (r";\s*(?:not in the current list|only 'boasts' is linted today)", ""),
    (r"\s*not in the current list", ""),
    (r"\s*(?:that|which) copyrules does not list", ""),
    (r"which the repo calls ", ""),
    (r"\s*missing from copyrules", ""),
    (r"\s*it lists only a few stems", ""),
    (r";\s*the current lint only catches it[^;]*", ""),
    (r"\s*not in the current chatbot list.*", ""),
    (r"\s*\(utilize stays[^)]*\)?", ""),
    (r"\s*\(scope: [^)]*\)", ""),
]


def _clean(what):
    for pat, rep in CLEAN:
        what = re.sub(pat, rep, what)
    return re.sub(r"\s{2,}", " ", what).strip(" ;,")


def _override(rule):
    for lang, start, change in OVERRIDES:
        if rule["lang"] == lang and rule["match"].startswith(start):
            if change.get("drop"):
                return None
            rule = dict(rule)
            if "sub" in change:
                rule["match"] = rule["match"].replace(*change["sub"])
            rule.update({k: v for k, v in change.items() if k not in ("sub", "drop")})
    return rule


def _compiled(r):
    rx = r["match"]
    flags = 0
    for ch in r.get("flags", "i"):
        flags |= {"i": re.I, "m": re.M}[ch]
    return re.compile(rx, flags) if r.get("kind") in ("regex", "structure") else cr._rule_regex(r)


def main():
    rules, seen, skipped, calib = [], set(), [], {}
    counters = {}
    only = set(sys.argv[1:])  # build from these files only (a research run still in progress stays out)
    for fn, note in SOURCES.items():
        if only and fn not in only:
            continue
        f = HERE / fn
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        humanizer = fn == "humanizer-skills.json"
        for idx, c in enumerate(candidates(data)):
            c = {k: unicodedata.normalize("NFC", v) if isinstance(v, str) else v for k, v in c.items()}
            tag = str(c.get("lang", "")).lower().strip()
            lang, region = TAGS.get(tag, (tag, None)) if humanizer else (tag, None)
            match = c.get("match", "")
            key = (lang, match)
            why = str(c.get("why", "")).strip()
            if not lang or not match or c.get("level") not in ("error", "warning", "note"):
                skipped.append((fn, lang, match, "incomplete"))
                continue
            if key in seen:
                first = next((r for r in rules if (r["lang"], r["match"]) == key), None)
                if first and region and first.get("region"):  # the same rule for another market (سوف: Egypt, Levant)
                    first["region"] = sorted(set(first["region"]) | set(region))
                    continue
                skipped.append((fn, lang, match, "duplicate"))
                continue
            if humanizer and idx in DUPLICATE:
                skipped.append((fn, lang, match[:40], "already linted: " + DUPLICATE[idx]))
                continue
            if humanizer and IN_PYTHON.search(match):
                skipped.append((fn, lang, match[:40], "written as code in copyrules.lint_caption"))
                continue
            if not humanizer and c.get("kind") == "structure" and (lang == "bn" or re.search(
                    r">=|count\(|count_distinct|\bin one\b|inside a string", match)):
                skipped.append((fn, lang, match[:40], "a counted structure: written as code in copyrules.py"))
                continue
            if c.get("kind") in ("word", "phrase") and match.lower() in KNOWN:
                skipped.append((fn, lang, match, "already in the hand-written lists"))
                continue
            if any(DASH.search(str(c.get(k, ""))) for k in ("replacement", "why", "evidence")):
                skipped.append((fn, lang, match, "a dash in its text"))
                continue
            rule = {"lang": lang, "kind": c.get("kind", "regex"), "match": match}
            if humanizer:  # tested by its author with MULTILINE, plus IGNORECASE for English only
                rule["flags"] = "im" if lang == "en" else "m"
            try:
                rx = _compiled(rule)
            except re.error as e:
                skipped.append((fn, lang, match, f"regex error {e}"))
                continue
            bad, good = c.get("bad_example", ""), c.get("good_example", "")
            if humanizer and bad and not rx.search(bad):
                skipped.append((fn, lang, match[:50], "a rule written in prose: code or judge, not a regex"))
                continue
            seen.add(key)
            counters[lang] = counters.get(lang, 0) + 1
            why = re.sub(r"^Named in copy\.md, not yet linted: ", "", why)
            why = re.sub(r" the copy\.md greeting regex misses \([^)]*\)", "", why)
            why = re.sub(r" the copy\.md ('[^']+') regex misses", r" of \1", why)
            what = "; ".join(x for x in why.split(". ")[0].rstrip(".").split("; ")
                             if not re.search(r"lint_spoken|copyrules|copy\.md|§|escapes the current|slips past", x))
            what = re.sub(r"\s*\((?:headline roles only|\d\+ in one[^)]*)\)", "", what)
            rep = re.sub(r"^add to AI_WORDS_EN_SOFT[^;]*;\s*", "", c.get("replacement", ""))
            rule.update({"id": f"{lang}-{counters[lang]:03d}", "replacement": rep,
                         "level": c["level"], "what": _clean(what or why.split(". ")[0])[:140], "why": why,
                         "evidence": c.get("evidence", ""), "risk": c.get("false_positive_risk", ""),
                         "source_notes": f"references/research/{note}"})
            rule = {k: rule[k] for k in ("id", "lang", "kind", "match", "flags", "replacement", "level", "what", "why",
                                         "evidence", "risk", "source_notes") if k in rule}
            if re.search(r"lint_spoken|text-to-speech|\bTTS\b|in a script|read oddly|read aloud|voice ?over|for the ear",
                         why, re.I):
                rule["scope"] = "spoken"  # only for copy that is heard (a voiceover platform or a script role)
            elif re.search(r"headline roles? only|run on headline roles|Title Case", why, re.I):
                rule["scope"] = "headline"
            elif re.search(r"apply to alt", why, re.I):
                rule["scope"] = "alt"
            elif re.search(r"skip legal lines", why, re.I):
                rule["scope"] = "casual"
            m = re.search(r"\b(?:at\s+)?([23])\+\s+in one", why)
            if m:
                rule["min"] = int(m.group(1))
            elif re.search(r"one use is fine|the tell is frequency|fine once|fine alone", why):
                rule["min"] = 2  # the research says so itself: once is a person, the repeat is the template
            if region:
                rule["region"] = region
            if "cog(?:e|er" in match:
                rule["region"] = ["419", "MX", "AR", "UY", "PY", "BO"]
            if bad:
                rule["bad"], rule["good"] = bad, good
            rule = _override(rule)
            if rule is None:
                counters[lang] -= 1  # the ids stay contiguous
                skipped.append((fn, lang, match[:40], "dropped after calibration"))
                continue
            rules.append(rule)
        cal = data.get("calibration", {}) if isinstance(data, dict) else {}
        if cal and ("natural" in cal or "robotic" in cal):  # one language per file (en, bn)
            lang = candidates(data)[0]["lang"] if candidates(data) else "und"
            cal = {lang: cal}
        for lang, v in cal.items():
            dst = calib.setdefault(lang, {"natural": [], "robotic": []})
            dst["natural"] += [unicodedata.normalize("NFC", x) for x in v.get("natural", []) if isinstance(x, str)]
            dst["robotic"] += [unicodedata.normalize("NFC", x) for x in v.get("robotic", []) if isinstance(x, str)]
    out = {"version": "2026-09-24",
           "note": "Voice rules from the 2026-09-24 research (natural, casual, native copy in 24 languages, plus mul "
                   "rules for every language). Each rule: a regex (regex, structure) or a literal (word, phrase) "
                   "matched with its script's boundary; flags i (default) or m, im; scope spoken, headline, alt or "
                   "casual limits it to those roles; min is the number of matches it needs; region lists the markets "
                   "it is for; bad and good are the author's test lines. copyrules.lint_voice applies a language's "
                   "rules to lines in that language. Calibration lines are in tests/data/voice_calibration.json.",
           "rules": rules}
    (SKILL / "scripts/voice_rules.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    (SKILL / "tests/data").mkdir(exist_ok=True)
    (SKILL / "tests/data/voice_calibration.json").write_text(json.dumps(calib, indent=1, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
    print(f"kept {len(rules)} rules: " + ", ".join(f"{k} {v}" for k, v in sorted(counters.items())))
    print(f"skipped {len(skipped)}")
    for x in skipped:
        print("  ", x)
    print("calibration:", {k: (len(v["natural"]), len(v["robotic"])) for k, v in calib.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
