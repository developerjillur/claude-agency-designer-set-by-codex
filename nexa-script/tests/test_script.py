"""Offline tests for script.py: the lint rules, timing, new, render and the review commands (with fake model answers,
no network)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))
TMP = Path(tempfile.mkdtemp(prefix="nexa-script-test-"))
os.environ["NEXA_CACHE"] = str(TMP / "cache")
os.environ["NEXA_DESIGN_PY"] = str(TMP / "no-design.py")   # the voice pass is tested where codex-design exists
import script as S  # noqa: E402


def write(name, content):
    path = TMP / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False),
                    encoding="utf-8")
    return str(path)


def lint_text(text, fmt="short", lang=None, name="t.txt"):
    return S.lint_script(S.load_script(write(name, text), fmt, lang))


def run(argv):
    """Runs the CLI; returns (exit code, parsed JSON or the text)."""
    out = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out):
        try:
            S.main(argv)
        except SystemExit as e:
            code = e.code or 0
    text = out.getvalue()
    try:
        return code, json.loads(text)
    except ValueError:
        return code, text


def beat(bid, narration, visual="A hand turns the oven dial", **kw):
    return dict({"id": bid, "narration": narration, "visual": visual}, **kw)


def script_json(beats, fmt="explainer", lang="en", target=None, loops=None, cta=None):
    return {"schema": "nexa.script/1", "meta": {"title": "t", "format": fmt, "lang": lang, "target_seconds": target},
            "loops": loops or {}, "beats": beats, "cta": cta or {}}


GOOD_SHORT = ("This bakery turns people away every morning, on purpose.\n\nIt has one oven, and it bakes 200 loaves. "
              "But by 9 a.m. they are gone. So people started queueing at 7.\n\nBut last spring Mira doubled the batch. "
              "So the oven ran all night, and the bread came out pale.\n\nShe went back to 200. Now the queue starts "
              "at 6:30.")


class OpeningAndEngine(unittest.TestCase):
    def test_a_clean_short_passes(self):
        res = lint_text(GOOD_SHORT)
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual(res["warnings"], [])
        self.assertEqual(res["stats"]["and_then"], 0)
        self.assertGreaterEqual(res["stats"]["but_or_therefore"], 4)

    def test_greeting_first_is_an_error_in_english_and_bangla(self):
        res = lint_text("Hey guys, welcome back! Today the bakery.\n\nBut the oven broke.")
        self.assertTrue(any("greeting" in e for e in res["errors"]))
        res = lint_text("আসসালামু আলাইকুম, আজকের ভিডিওতে একটা বেকারি।\n\nকিন্তু ওভেন ভেঙে গেল।")
        self.assertEqual(res["stats"]["lang"], "bn")
        self.assertTrue(any("greeting" in e for e in res["errors"]))

    def test_and_then_chain_is_flagged(self):
        res = lint_text("The shop opened in 2019.\n\nAnd then it got busy. Then the bread sold out. Also the owner "
                        "smiled. Next, people came back.")
        self.assertTrue(any("and-then" in w for w in res["warnings"]))
        self.assertEqual(res["stats"]["and_then"], 4)

    def test_bangla_and_then_chain(self):
        res = lint_text("মিরপুরের দোকানটা ২০১৯ সালে খুলল।\n\nএরপর ভিড় বাড়ল। তারপর রুটি শেষ হলো। এছাড়া মালিক হাসলেন।")
        self.assertTrue(any("and-then" in w for w in res["warnings"]))

    def test_pop_science_and_dashes_are_errors(self):
        res = lint_text("Stories are 22 times more memorable than facts \u2014 so tell one.")
        self.assertTrue(any("pop-science" in e for e in res["errors"]))
        self.assertTrue(any("em dash" in e for e in res["errors"]))

    def test_a_moral_ending_is_reported_once(self):
        res = lint_text("মিরপুরের দোকানে ২০০টা রুটি হয়।\n\nকিন্তু ৯টায় শেষ।\n\nমনে রাখবেন, মান থাকলে সফলতা আসবেই।")
        morals = [w for w in res["warnings"] if "moral" in w]
        self.assertEqual(len(morals), 1, morals)

    def test_long_form_needs_a_turn_early_and_no_early_cta(self):
        flat = " ".join(["The city has many buses on many roads every single day."] * 12)
        res = lint_text("Subscribe to the channel for more. " + flat, fmt="explainer", name="long.txt")
        self.assertTrue(any("first 20 seconds" in w for w in res["warnings"]))
        self.assertTrue(any("call to action" in w for w in res["warnings"]))


class ShortsAndAds(unittest.TestCase):
    def test_beat_one_needs_a_visual_and_a_short_overlay(self):
        data = script_json([beat("b1", "This oven bakes 200 loaves.", visual="",
                                 on_screen="one oven two hundred loaves gone by nine every day"),
                            beat("b2", "But by 9 they are gone.")], fmt="short")
        res = S.lint_script(S.load_script(write("s.json", data)))
        self.assertTrue(any("beat 1 has no visual" in e for e in res["errors"]))
        self.assertTrue(any("overlay" in w for w in res["warnings"]))

    def test_ad_rules(self):
        data = script_json([beat("b1", "Are you overweight and tired of diets?"),
                            beat("b2", "This tea is guaranteed to work. Earn $500 a day from home.")], fmt="ad")
        res = S.lint_script(S.load_script(write("ad.json", data)))
        errs = " | ".join(res["errors"])
        self.assertIn("personal-attribute", errs)
        self.assertIn("quick-money", errs)
        self.assertIn("call to action", errs)
        self.assertTrue(any("guaranteed" in w for w in res["warnings"]))

    def test_long_spoken_sentence_and_fast_beat(self):
        data = script_json([beat("b1", "This oven bakes 200 loaves.", seconds=2),
                            beat("b2", "It is the only oven in the whole building and it has been running every "
                                       "single night since the owner bought it back in the spring of 2019.")],
                           fmt="short")
        res = S.lint_script(S.load_script(write("long-sentence.json", data)))
        self.assertTrue(any("spoken sentence of" in w for w in res["warnings"]))
        self.assertFalse(any("b1: 5 words in 2 s" in w for w in res["warnings"]))   # 2.5 a second is fine
        data["beats"][0]["seconds"] = 1
        res = S.lint_script(S.load_script(write("fast-beat.json", data)))
        self.assertTrue(any("b1: 5 words in 1 s" in w for w in res["warnings"]))

    def test_ad_hook_pack_brand_and_disclosure(self):
        data = script_json([beat("b1", "One swipe cleans a week of dog hair."),
                            beat("b2", "It is 30% off this week, order on the app.")], fmt="ad",
                           cta={"text": "order on the app"})
        data["meta"].update({"brand": "FurAway", "paid": True})
        data["promise"] = {"hook_variants": [{"type": "proof", "visual": "swipe on couch", "spoken": "One swipe."},
                                             {"type": "proof", "visual": "swipe on couch", "spoken": "Watch this."},
                                             {"type": "proof", "visual": "swipe on couch", "spoken": "Look."}]}
        path = write("ad-pack.json", data)
        draft = S.lint_script(S.load_script(path), None, "draft")
        self.assertTrue(any("hook types" in w for w in draft["warnings"]))
        self.assertTrue(any("first frames" in w for w in draft["warnings"]))
        self.assertTrue(any("5 hooks" in n for n in draft["notes"]))
        self.assertTrue(any("FurAway" in w for w in draft["warnings"]))
        self.assertTrue(any("no disclosure" in w for w in draft["warnings"]))
        final = S.lint_script(S.load_script(path), None, "final")
        self.assertTrue(any("5 hooks" in e for e in final["errors"]))
        self.assertTrue(any("no disclosure" in e for e in final["errors"]))
        data["beats"][0]["on_screen"] = "Paid partnership with FurAway"
        ok = S.lint_script(S.load_script(write("ad-pack2.json", data)), None, "final")
        self.assertFalse(any("disclosure" in e for e in ok["errors"]))
        self.assertFalse(any("FurAway" in w for w in ok["warnings"]))

    def test_sound_off_needs_text_or_captions(self):
        data = script_json([beat("b1", "This oven bakes 200 loaves.", on_screen="200 loaves"),
                            beat("b2", "But by 9 they are gone."), beat("b3", "So people queue at 7.")], fmt="short")
        res = S.lint_script(S.load_script(write("muted.json", data)))
        self.assertTrue(any("muted viewer" in w for w in res["warnings"]))
        data["meta"]["captions"] = True
        res = S.lint_script(S.load_script(write("muted2.json", data)))
        self.assertFalse(any("muted viewer" in w for w in res["warnings"]))

    def test_lines_carry_times_and_pictures(self):
        data = script_json([beat("b1", "One. Two.", on_screen="1 2"), beat("b2", "Three.")], fmt="short")
        lines = S.narration_lines(S.load_script(write("lines.json", data)))
        self.assertEqual([ln["id"] for ln in lines], ["L1", "L2", "L3"])
        self.assertEqual(lines[0]["t"], 0.0)
        self.assertIn("visual", lines[0])
        self.assertNotIn("visual", lines[1])       # the picture rides on the first line of its beat only
        self.assertIn("visual", lines[2])

    def test_markers_block_the_final(self):
        data = script_json([beat("b1", "Why does it sell out? [PROOF NEEDED]")], fmt="short")
        path = write("marker.json", data)
        self.assertTrue(any("PROOF NEEDED" in w for w in S.lint_script(S.load_script(path))["warnings"]))
        self.assertTrue(any("PROOF NEEDED" in e for e in S.lint_script(S.load_script(path), None, "final")["errors"]))

    def test_ad_with_a_cta_passes_that_rule(self):
        data = script_json([beat("b1", "Mira's oven bakes 200 loaves by 7 a.m."),
                            beat("b2", "Order before 9 on the app and it reaches you warm.")], fmt="ad",
                           cta={"text": "Order on the app", "beat": "b2"})
        res = S.lint_script(S.load_script(write("ad2.json", data)))
        self.assertFalse(any("call to action" in e for e in res["errors"]), res["errors"])


class LoopsTensionClaims(unittest.TestCase):
    def test_loop_ledger(self):
        beats = [beat("b1", "Why do the buses race?", loops_open=["Q1", "Q2"]),
                 beat("b2", "Because the driver rents the bus.", loops_close=["Q1"]),
                 beat("b3", "And the fare goes to him.", loops_close=["Q3"])]
        data = script_json(beats, loops={"Q1": "why race", "Q2": "who is paid", "Q3": "x", "Q4": "never opened"})
        res = S.lint_script(S.load_script(write("loops.json", data)))
        errs = " | ".join(res["errors"])
        self.assertIn("Q2", errs)                       # opened, never paid off
        self.assertIn("closed before it is opened", errs)   # Q3
        self.assertTrue(any("Q4" in w for w in res["warnings"]))

    def test_main_loop_should_close_last(self):
        beats = [beat("b1", "Why do the buses race?", loops_open=["Q1"]),
                 beat("b2", "And who gets the fare?", loops_open=["Q2"]),
                 beat("b3", "They race because of the rent.", loops_close=["Q1"]),
                 beat("b4", "The fare goes to the driver.", loops_close=["Q2"])]
        res = S.lint_script(S.load_script(write("main.json", script_json(beats, loops={"Q1": "a", "Q2": "b"}))))
        self.assertTrue(any("close it last" in w for w in res["warnings"]))

    def test_claims_against_the_pack(self):
        beats = [beat("b1", "According to a 2019 study, most buses run on daily rent.", claims=["c1"]),
                 beat("b2", "The rent is 3,500 taka a day."),
                 beat("b3", "The owner keeps 40% of it.", claims=["c9"])]
        path = write("claims.json", script_json(beats))
        pack = {"claims": [{"id": "c1", "status": "unsupported"}]}
        draft = S.lint_script(S.load_script(path), pack, "draft")
        self.assertTrue(any("c1 is unsupported" in w for w in draft["warnings"]))
        self.assertTrue(any("no claim id" in w for w in draft["warnings"]))
        self.assertTrue(any("c9 is not in the research pack" in e for e in draft["errors"]))
        final = S.lint_script(S.load_script(path), pack, "final")
        self.assertTrue(any("c1 is unsupported" in e for e in final["errors"]))
        self.assertTrue(any("no claim id" in e for e in final["errors"]))

    def test_tension_map(self):
        t = lambda q, s, u, p: {"q": q, "s": s, "u": u, "p": p}  # noqa: E731
        beats = [beat("b1", "It pays off already.", tension=t(1, 0, 0, 2)),
                 beat("b2", "Nothing happens here at all.", tension=t(1, 0, 0, 0)),
                 beat("b3", "Nothing again.", tension=t(1, 0, 0, 0)),
                 beat("b4", "Still nothing.", tension=t(1, 0, 0, 0))]
        res = S.lint_script(S.load_script(write("tension.json", script_json(beats, fmt="short"))))
        self.assertTrue(any("orphan payoff" in w for w in res["warnings"]))
        self.assertTrue(any("flat zone" in w for w in res["warnings"]))

    def test_unpaid_tension_and_section_ends(self):
        t = lambda q, s, u, p: {"q": q, "s": s, "u": u, "p": p}  # noqa: E731
        beats = [beat(f"b{i}", "But what happens next?", tension=t(3, 2, 2, 0), section="build") for i in range(1, 6)]
        beats[4]["tension"] = t(0, 2, 2, 0)            # the section ends with nothing open
        beats += [beat("b6", "So the oven ran all night.", tension=t(1, 1, 1, 3), section="payoff"),
                  beat("b7", "The queue is the product.", tension=t(0, 0, 0, 2), section="close"),
                  beat("b8", "Close on the shelf.", tension=t(0, 0, 0, 1), section="close")]
        res = S.lint_script(S.load_script(write("unpaid.json", script_json(beats, fmt="short"))))
        self.assertTrue(any("unpaid tension" in w for w in res["warnings"]), res["warnings"])
        self.assertTrue(any("section 'build' ends with no open question" in w for w in res["warnings"]))


class LoadingAndVoicePass(unittest.TestCase):
    def test_bad_json_roots_stop_cleanly(self):
        code, out = run(["timing", write("list-root.json", "[1, 2]")])
        self.assertEqual(code, 2)
        self.assertIn("not a list", out["error"])
        data = script_json([beat("b1", "The oven runs all night.")])
        data["schema"] = None                               # a null schema reads as no schema
        self.assertEqual(S.load_script(write("null-schema.json", data))["meta"]["format"], "explainer")

    def test_voice_pass_reports_a_copylint_that_did_not_run(self):
        import script_lint
        script = S.load_script(write("vp.txt", "The oven runs all night."), "short")
        old = script_lint.DESIGN
        try:
            # copylint's contract: 0 fine, 2 errors found (it ran), 1 a usage or tool error (it did not)
            script_lint.DESIGN = Path(write("tool-error.py", "import sys\nprint('file not found')\nsys.exit(1)\n"))
            self.assertFalse(script_lint.voice_pass(script)["ran"])
            script_lint.DESIGN = Path(write("ok.py", "print('warning voiceover  x')\nprint('{\"errors\": 0}')\n"))
            res = script_lint.voice_pass(script)
            self.assertTrue(res["ran"])
            self.assertEqual(res["warnings"], ["voiceover  x"])
            script_lint.DESIGN = Path(write("gate.py", "import sys\nprint('error   voiceover  an em dash')\n"
                                                       "print('{\"errors\": 1}')\nsys.exit(2)\n"))
            res = script_lint.voice_pass(script)
            self.assertTrue(res["ran"])                  # errors found is a run that failed its gate, not a skip
            self.assertEqual(res["errors"], ["voiceover  an em dash"])
        finally:
            script_lint.DESIGN = old


class TimingAndLength(unittest.TestCase):
    def test_pace_by_language(self):
        self.assertEqual(S.wpm_for("youtube-long", "en"), 160)
        self.assertEqual(S.wpm_for("youtube-long", "bn"), 134)
        self.assertEqual(S.wpm_for("youtube-long", "hi"), 200)
        self.assertEqual(S.wpm_for("short", "en", 180), 180.0)
        self.assertIsNone(S.wpm_for("blog", "en"))

    def test_timing_rows(self):
        data = script_json([beat("b1", " ".join(["word"] * 80)), beat("b2", " ".join(["word"] * 80), pause_s=1)],
                           fmt="youtube-long")
        t = S.timing(S.load_script(write("timing.json", data)))
        self.assertEqual(t["total_seconds"], 61.0)
        self.assertEqual(t["beats"][1]["start"], 30.0)

    def test_runtime_against_the_target(self):
        words = " ".join(["word"] * 160)   # 60 s at 160 wpm
        for target, kind in ((100, "errors"), (68, "warnings")):
            data = script_json([beat("b1", "Why? " + words)], target=target)
            res = S.lint_script(S.load_script(write(f"len{target}.json", data)))
            self.assertTrue(any("against a target" in x for x in res[kind]), (target, res))

    def test_a_long_stretch_with_no_turn(self):
        flat = " ".join(f"The road has {i} buses on it every day." for i in range(40))
        res = lint_text("Why do the buses race? But nobody asks. " + flat, fmt="explainer", name="stretch.txt")
        self.assertTrue(any("with no question, turn or new loop" in w for w in res["warnings"]), res["warnings"])

    def test_a_short_over_the_limit(self):
        res = lint_text(" ".join(["But the oven was hot."] * 110))
        self.assertTrue(any("over the 180 s limit" in e for e in res["errors"]))


class Blog(unittest.TestCase):
    def test_blog_rules(self):
        md = ("# The Complete and Ultimate Guide to Choosing the Best Rice Cooker for Your Family in 2026\n\n"
              "Studies show that 68% of families cook rice daily. A good cooker saves time. It saves power. It keeps "
              "rice warm. It is easy to clean. Many have timers. Some have steam trays.\n\n"
              "For more, [click here](https://example.com).\n\n[NEEDS INPUT: our test]\n")
        res = S.lint_blog(S.load_script(write("b.md", md)))
        errs = " | ".join(res["errors"])
        for needle in ("title is", "click here", "paragraph of 7", "no link"):
            self.assertIn(needle, errs)
        self.assertTrue(any("NEEDS INPUT" in w for w in res["warnings"]))          # a gate: a warning in a draft
        final = S.lint_blog(S.load_script(write("b.md", md)), "final")
        self.assertTrue(any("NEEDS INPUT" in e for e in final["errors"]))         # and an error in a final

    def test_affiliate_keyword_and_not_only(self):
        md = ("# Rice cookers\n\nBuy the [Walton cooker](https://amzn.to/abc123) today.\n\n"
              "## Rice cooker size\n\nText.\n\n## Rice cooker price\n\nText.\n\n## Rice cooker care\n\n"
              "It is not only cheap but also fast.\n")
        res = S.lint_blog(S.load_script(write("aff.md", md)), "draft", "rice cooker")
        errs = " | ".join(res["errors"])
        self.assertIn("affiliate link with no disclosure", errs)
        self.assertIn("in 3 subheads", errs)
        self.assertTrue(any("not only" in w for w in res["warnings"]))
        md2 = md.replace("today.", "today (affiliate link: we earn a commission).")
        res = S.lint_blog(S.load_script(write("aff2.md", md2)))
        self.assertFalse(any("affiliate" in e for e in res["errors"]))

    def test_a_clean_blog_passes(self):
        md = ("# Rice cooker size for a family of four\n\nA 1.8 litre cooker feeds four people, by the maker's chart "
              "at [Walton](https://waltonbd.com/rice-cooker).\n\n## Why size matters\n\nA small pot boils over. A big "
              "one burns a thin layer.\n")
        res = S.lint_blog(S.load_script(write("ok.md", md)))
        self.assertTrue(res["ok"], res["errors"])


class WordsAndStructure(unittest.TestCase):
    def test_vague_payoff_fake_loop_and_improvement_claims(self):
        res = lint_text("Stay till the end for the secret.\n\nShe opened the shop and the rest is history. "
                        "It boosted sales by 300%.", name="words.txt")
        self.assertTrue(any("vague payoff" in e for e in res["errors"]))
        self.assertTrue(any("fake-loop" in w for w in res["warnings"]))
        self.assertTrue(any("improvement claim" in w for w in res["warnings"]))

    def test_abstract_labels_need_a_number(self):
        res = lint_text("This shop is very popular.\n\nBut the oven is small.", name="abstract.txt")
        self.assertTrue(any("'very popular' with no number" in w for w in res["warnings"]))
        res = lint_text("This shop is very popular: 300 people queue daily.\n\nBut the oven is small.",
                        name="abstract2.txt")
        self.assertFalse(any("very popular" in w for w in res["warnings"]))

    def test_hindi_inside_bangla(self):
        res = lint_text("দোকানটা ছোট। लेकिन লাইন লম্বা।", fmt="short", lang="bn", name="leak.txt")
        self.assertTrue(any("Devanagari" in e for e in res["errors"]))
        # the danda sits in the Devanagari block but is Bangla punctuation too
        res = lint_text("দোকানটা ছোট। কিন্তু লাইন লম্বা॥", fmt="short", lang="bn", name="danda.txt")
        self.assertFalse(any("Devanagari" in e for e in res["errors"]))
        res = lint_text("Dokan ta choto, lekin line lomba.", fmt="short", lang="banglish", name="leak2.txt")
        self.assertTrue(any("Hindi word in a Banglish" in w for w in res["warnings"]))

    def test_hook_length_and_two_and_thens(self):
        res = lint_text("This small bakery in the old part of Dhaka turns away dozens of people every single morning."
                        "\n\nThen it opens. Then it sells out.", name="hooklen.txt")
        self.assertTrue(any("12 or fewer" in w for w in res["warnings"]))
        self.assertTrue(any("two and-then openers" in w for w in res["warnings"]))

    def test_sponsor_too_early(self):
        filler = " ".join(f"But the {i}th bus came late." for i in range(60))
        res = lint_text("Why do buses race? This video is sponsored by a bank. " + filler, fmt="explainer",
                        name="sponsor.txt")
        self.assertTrue(any("sponsor or plug" in w for w in res["warnings"]))

    def test_v6_words(self):
        res = lint_text("This gives you a dopamine boost.\n\nIt's not luck, it's the oven. It's not the flour, it's "
                        "the water. Hurry, last chance!", name="v6.txt")
        self.assertTrue(any("pop-science word ('dopamine')" in w for w in res["warnings"]))
        self.assertFalse(any("dopamine" in e for e in res["errors"]))
        self.assertTrue(any("'not X, it's Y' frames" in w for w in res["warnings"]))
        self.assertTrue(any("urgency with no date" in w for w in res["warnings"]))
        res = lint_text("Order by Sunday 25 May, last chance.\n\nBut the oven is small.", name="v6b.txt")
        self.assertFalse(any("urgency" in w for w in res["warnings"]))

    def test_weak_openers_and_hedges(self):
        res = lint_text("Here are 5 tips for better bread.\n\nBut the oven matters most.", name="weak.txt")
        self.assertTrue(any("announces instead of hooking" in w for w in res["warnings"]))
        res = lint_text("This might be the best bakery in Dhaka.\n\nBut it sells out by 9.", name="hedge.txt")
        self.assertTrue(any("hedge in the hook" in w for w in res["warnings"]))
        res = lint_text("You might think bakeries want more customers. But this one sends 50 away daily.",
                        name="hedge2.txt")
        self.assertFalse(any("hedge in the hook" in w for w in res["warnings"]))

    def test_address_form_mixing(self):
        res = lint_text("আপনি কি জানেন? তুমি যদি ৯টার পরে যাও, রুটি পাবে না।", fmt="short", lang="bn", name="addr.txt")
        self.assertTrue(any("address form" in w for w in res["warnings"]))
        res = lint_text('আপনি কি জানেন? মালিক বললেন, "তুমি পরে এসো।"', fmt="short", lang="bn", name="addr2.txt")
        self.assertFalse(any("address form" in w for w in res["warnings"]))   # a quoted line keeps its own voice

    def test_tail_after_the_main_payoff(self):
        pad = " ".join(["word"] * 80)        # 30 s a beat at 160 wpm
        beats = [beat("b1", "Why do buses race? " + pad, loops_open=["Q1"]), beat("b2", "But. " + pad),
                 beat("b3", "So. " + pad, loops_close=["Q1"]), beat("b4", "But. " + pad), beat("b5", "So. " + pad)]
        res = S.lint_script(S.load_script(write("tail.json", script_json(beats, loops={"Q1": "why"}))))
        self.assertTrue(any("after the main payoff" in w for w in res["warnings"]))

    def test_cross_video_loop_is_a_note(self):
        data = script_json([beat("b1", "Why do buses race?", loops_open=["Q1", "Q2"]),
                            beat("b2", "Because of rent.", loops_close=["Q1"])],
                           loops={"Q1": "why", "Q2": {"question": "who fixes it?", "cross_video": True}})
        res = S.lint_script(S.load_script(write("cross.json", data)))
        self.assertFalse(any("Q2" in e for e in res["errors"]), res["errors"])
        self.assertTrue(any("next video" in n for n in res["notes"]))


class RolesAndStory(unittest.TestCase):
    def long_beats(self, roles_per_beat):
        words_ = " ".join(["word"] * 40)       # 15 s a beat at 160 wpm
        return [beat(f"b{i + 1}", f"But why? {words_}", roles=r) for i, r in enumerate(roles_per_beat)]

    def test_skeleton_and_turning_points(self):
        roles = [["pp1", "hook"]] + [[] for _ in range(14)] + [["change"]]
        res = S.lint_script(S.load_script(write("roles.json", script_json(self.long_beats(roles)))))
        warns = " | ".join(res["warnings"])
        self.assertIn("lacks conflict, value", warns)
        self.assertIn("PP1 is the first beat", warns)
        self.assertIn("no PP2", warns)
        self.assertIn("no stakes_loss beat", warns)

    def test_well_placed_turning_points(self):
        roles = ([["hook", "stakes_loss", "stakes_gain"], ["identity"], ["pp1", "conflict"]] + [[]] * 9 +
                 [["pp2"], [], ["change", "value"], ["cta"]])
        res = S.lint_script(S.load_script(write("roles-ok.json", script_json(self.long_beats(roles)))))
        warns = " | ".join(res["warnings"])
        for needle in ("lacks", "PP1", "PP2", "stakes_"):
            self.assertNotIn(needle, warns)

    def test_sponsor_outside_loops(self):
        beats = [beat("b1", "Why do buses race?", roles=["hook"], loops_open=["Q1"]),
                 beat("b2", "Because of rent.", roles=["pp1", "conflict", "change", "value"], loops_close=["Q1"]),
                 beat("b3", "This part is brought to you by a bank.", roles=["sponsor"])]
        res = S.lint_script(S.load_script(write("sponsor.json", script_json(beats, fmt="short", loops={"Q1": "x"}))))
        self.assertTrue(any("sponsor beat sits outside" in w for w in res["warnings"]))

    def test_emotion_repeats(self):
        beats = [beat(f"b{i}", "But then it broke.", emotion="tense") for i in range(1, 5)]
        res = S.lint_script(S.load_script(write("emo.json", script_json(beats))))
        self.assertTrue(any("three beats in a row" in w for w in res["warnings"]))

    def test_key_moment_craft(self):
        beats = [beat("b1", "Last Thursday I'm third in line at the bank."),
                 beat("b2", "The clerk told me that my card was blocked. I was so nervous.", pause_s=0),
                 beat("b3", "Then I paid in cash.")]
        data = script_json(beats, fmt="short")
        data["story"] = {"mode": "personal", "key_moment": "b2"}
        res = S.lint_script(S.load_script(write("km.json", data)))
        warns = " | ".join(res["warnings"])
        self.assertIn("feeling named inside the key moment", warns)
        self.assertIn("reported speech", warns)
        self.assertIn("no spoken line or thought", warns)

    def test_quotes_and_truth_modes(self):
        beats = [beat("b1", 'The manager said: "We would like to utilize this opportunity regarding the '
                            'execution of our long-term strategic partnership framework today."')]
        data = script_json(beats, fmt="short")
        data["story"] = {"mode": "nonfiction"}
        res = S.lint_script(S.load_script(write("quote.json", data)))
        warns = " | ".join(res["warnings"])
        self.assertIn("quoted sentence of", warns)
        self.assertIn("report words inside a spoken line", warns)
        self.assertIn("a quote in nonfiction mode", warns)
        final = S.lint_script(S.load_script(write("quote.json", data)), None, "final")
        self.assertTrue(any("a quote in nonfiction mode" in e for e in final["errors"]))
        data["beats"][0]["claims"] = ["c1"]
        ok = S.lint_script(S.load_script(write("quote2.json", data)), {"claims": [{"id": "c1", "status": "verified"}]},
                           "final")
        self.assertFalse(any("nonfiction mode" in e for e in ok["errors"]))

    def test_key_line_needs_a_pause(self):
        beats = [beat("b1", "I walk in late. He looks up."), beat("b2", '"You are the coffee girl?" I smile.')]
        data = script_json(beats, fmt="short")
        data["story"] = {"mode": "personal", "key_line": '"You are the coffee girl?"'}
        res = S.lint_script(S.load_script(write("kl.json", data)))
        self.assertTrue(any("no pause after it" in w for w in res["warnings"]))
        data["beats"][1]["narration"] = '"You are the coffee girl?" [beat] I smile.'
        res = S.lint_script(S.load_script(write("kl2.json", data)))
        self.assertFalse(any("no pause after it" in w for w in res["warnings"]))


class Commands(unittest.TestCase):
    def test_new_never_overwrites(self):
        d = TMP / "proj-new"
        code, out = run(["new", str(d), "--format", "reel", "--lang", "bn", "--target", "45"])
        self.assertEqual(code, 0)
        data = json.loads((d / "script.json").read_text(encoding="utf-8"))
        self.assertEqual(data["meta"]["format"], "short")
        self.assertEqual(len(data["beats"]), len(S.SKELETONS["short"]))
        self.assertEqual(json.loads((d / "brief.json").read_text(encoding="utf-8"))["locale"], "BD")
        code, out = run(["new", str(d), "--format", "short"])
        self.assertEqual(code, 2)
        self.assertIn("never overwritten", out["error"])

    def test_render_writes_the_table_and_ledger(self):
        beats = [beat("b1", "Why do the buses race?", loops_open=["Q1"]),
                 beat("b2", "Because | the driver rents the bus.", loops_close=["Q1"])]
        path = write("render/script.json", script_json(beats, loops={"Q1": "why race"}))
        code, out = run(["render", path])
        self.assertEqual(code, 0)
        md = (TMP / "render" / "script.md").read_text(encoding="utf-8")
        self.assertIn("| 0:00 | Why do the buses race?", md)
        self.assertIn("Because / the driver", md)
        self.assertIn("| Q1 | why race | b1 | b2 |", md)
        self.assertTrue((TMP / "render" / "narration.txt").exists())

    def test_render_writes_a_roadmap_and_strips_marks(self):
        beats = [beat("b1", "By 9 the bakery is sold out. [beat] Every day.", section="hook", claims=["brief"]),
                 beat("b2", "It bakes 200 loaves in one oven.", section="why", claims=["brief"])]
        path = write("render2/script.json", script_json(beats))
        run(["render", path])
        road = (TMP / "render2" / "roadmap.md").read_text(encoding="utf-8")
        self.assertIn("**Hook line:** By 9 the bakery is sold out.", road)
        self.assertIn("It bakes 200 loaves in one oven.", road)          # a fact to get exactly right
        narration = (TMP / "render2" / "narration.txt").read_text(encoding="utf-8")
        self.assertNotIn("[beat]", narration)

    def test_understand_and_tournament_with_fake_models(self):
        os.environ["NEXA_LLM_FAKE"] = "1"
        try:
            brief = write("u/brief.json", {"topic": "bakery"})
            a = write("u/a.json", script_json([beat("b1", "This bakery turns people away.")], fmt="short"))
            b = write("u/b.json", script_json([beat("b1", "By 9 it is sold out.")], fmt="short"))
            code, out = run(["understand", a, "--brief", brief])
            self.assertIn("retell", out)
            self.assertTrue((TMP / "u" / "understand.json").exists())
            code, out = run(["tournament", a, b, "--brief", brief, "--roster", "codex"])
            self.assertEqual(len(out["ranking"]), 2)
            self.assertEqual(len(out["games"]), 1)
        finally:
            os.environ.pop("NEXA_LLM_FAKE", None)

    def test_lint_cli_exit_codes(self):
        good = write("cli/good.txt", GOOD_SHORT)
        self.assertEqual(run(["lint", good, "--format", "short"])[0], 0)
        bad = write("cli/bad.txt", "Hey guys, welcome back to the channel.\n\nThen we eat.")
        code, out = run(["lint", bad, "--format", "short", "--json"])
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])

    def test_review_commands_with_fake_models(self):
        os.environ["NEXA_LLM_FAKE"] = "1"
        try:
            d = TMP / "review"
            brief = write("review/brief.json", {"topic": "bakery", "format": "short", "lang": "en"})
            path = write("review/script.json", script_json([beat("b1", "This bakery turns people away."),
                                                            beat("b2", "But the queue is the product.")],
                                                           fmt="short"))
            code, out = run(["judge", path, "--brief", brief, "--runs", "1", "--roster", "codex,gemini:x"])
            self.assertTrue((d / "judge.json").exists(), out)
            self.assertEqual(out["runs_total"], 2)
            code, out = run(["panel", "build", str(d), "--brief", brief, "--n", "10"])
            self.assertGreater(out["personas"], 0)     # the fake model returns one card a batch
            self.assertTrue(any("asked for" in e for e in out["errors"]))
            code, out = run(["panel", "run", path, "--panel", str(d / "panel.json"), "--judge", str(d / "judge.json")])
            self.assertIn("synthetic", out["label"])
            self.assertTrue((d / "review.json").exists())
            code, out = run(["baselines", "--brief", brief, "--n", "2"])
            self.assertTrue((d / "baselines.json").exists())
            self.assertEqual(len(out["plain"]), out["versions"])
            for f in out["plain"]:                      # each plain draft is a file the tournament can take
                self.assertTrue(Path(f).read_text(encoding="utf-8").strip())
            new = write("review/script2.json", script_json([beat("b1", "This bakery turns people away."),
                                                            beat("b2", "But the queue is the product, by 7 a.m.")],
                                                           fmt="short"))
            code, out = run(["guard", path, new, "--keep", str(d / "review.json")])
            self.assertIn("edit_share", out)
            code, out = run(["prefer", path, new, "--panel", str(d / "panel.json")])
            self.assertIn("clears", out)
            code, out = run(["decide", "--round", "1", "--judge", str(d / "judge.json"), "--review",
                             str(d / "review.json")])
            self.assertIn("continue", out)
        finally:
            os.environ.pop("NEXA_LLM_FAKE", None)

    def test_checklists_cover_every_format(self):
        for fmt in S.FORMATS:
            items = S.checklist_for(fmt)["items"]
            self.assertGreaterEqual(len(items), 7, fmt)
            self.assertTrue(all(i["id"] and i["question"].endswith("?") or "Answer pass" in i["question"]
                                for i in items), fmt)


if __name__ == "__main__":
    unittest.main()
