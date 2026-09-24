"""Offline tests for design.py (no network, no Codex). Render tests need Google Chrome and skip without it.

Run:  python3 -m unittest discover -s ~/.claude/skills/codex-design/tests -v
Set CODEX_DESIGN_SCRIPT=/path/to/design.py to test another copy.
"""
import argparse
import contextlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(os.environ.get("CODEX_DESIGN_SCRIPT") or Path(__file__).resolve().parent.parent / "scripts" / "design.py")
spec = importlib.util.spec_from_file_location("design", SCRIPT)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.log = lambda *a, **k: None

try:
    Image = d.need_pillow()
    HAVE_PIL = True
except SystemExit:
    HAVE_PIL = False
try:
    d.chrome_bin()
    HAVE_CHROME = True
except SystemExit:
    HAVE_CHROME = False
KIT = SCRIPT.parent.parent / "templates" / "kit"


def size_of(path) -> tuple:
    with Image.open(path) as im:
        return im.size


def page(body: str, style: str = "", head: str = "") -> str:
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>{head}<style>html,body{{margin:0}}"
            f"body{{width:var(--canvas-w);height:var(--canvas-h);overflow:hidden;background:#fff;position:relative}}"
            f"{style}</style></head><body>{body}</body></html>")


class Units(unittest.TestCase):
    def test_dashes_that_read_as_ai_copy(self):
        sev = lambda t, s="": [x[0] for x in d.dash_issues(t, s)]
        self.assertEqual(sev("Hand-built steel — ridden on dirt"), ["error"])
        self.assertEqual(sev("Open today -- all day"), ["error"])
        self.assertEqual(sev("Slowly – woven by hand"), ["error"])        # a spaced en dash used as a pause
        self.assertEqual(sev("Tuesday–Sunday"), ["warning"])              # write 'to'
        self.assertEqual(sev("10 – 12 December"), ["warning"])            # close up the range
        self.assertEqual(sev("Open 09:00–13:00, €34–38k"), [])            # ranges between numbers stay
        self.assertEqual(sev("১০–১২ ডিসেম্বর", "bengali"), ["warning"])     # ১০-১২ or ১০ থেকে ১২
        self.assertEqual(sev("state-of-the-art, well-made"), [])
        self.assertEqual(sev("Price - 450"), ["warning"])

    def test_copylint_catches_ai_and_translated_copy(self):
        cr = d.copyrules
        codes = lambda t, role="", loc="BD", plat="": [f["code"] for f in cr.lint_string(t, role, loc, plat)]
        self.assertIn("em-dash", codes("Elevate your mornings — taste it", "headline"))
        self.assertIn("ai-word", codes("Elevate your mornings", "headline"))
        self.assertIn("ai-pattern", codes("It's not just coffee, it's a ritual", "headline"))
        self.assertEqual(codes("Hand-built steel. Ridden on dirt.", "headline"), [])
        self.assertIn("bn-formal", codes("আমাদের পণ্য ক্রয় করুন", "body"))
        self.assertEqual(codes("আমাদের পণ্য ক্রয় করুন", "body").count("bn-formal"), 1)   # the phrase, not also 'ক্রয়'
        self.assertIn("bn-pattern", codes("সেবা প্রদান করা হয়ে থাকে", "body"))
        self.assertIn("bn-locale", codes("ঠান্ডা জল খান", "body"))                       # পানি in Bangladesh
        self.assertNotIn("bn-locale", codes("ঠান্ডা জল খান", "body", "IN"))
        self.assertIn("pause-dash", codes("সকাল ১১টা – রাত ৮টা", "time"))
        self.assertEqual(codes("অর্ডার করুন", "cta"), [])
        self.assertIn("long-cta", codes("Click here to learn more about our offer", "cta"))
        self.assertIn("long-headline", codes("One two three four five", "headline", "", "youtube-thumb"))
        cap = "নতুন কালেকশন\n" + " ".join(f"#tag{i}" for i in range(8))
        self.assertIn("hashtag-cap", [f["code"] for f in cr.lint_caption(cap, "instagram", "BD")])   # over the cap
        cap = "নতুন কালেকশন\n" + " ".join(f"#tag{i}" for i in range(4))
        self.assertIn("hashtags", [f["code"] for f in cr.lint_caption(cap, "instagram", "BD")])       # over native
        self.assertIn("greeting-open", [f["code"] for f in cr.lint_caption("প্রিয় গ্রাহক, অফার চলছে", "facebook", "BD")])
        self.assertIn("engagement-bait", [f["code"] for f in cr.lint_string("লাইক দিন ও শেয়ার করুন", "body")])
        both = cr.lint_deck([{"role": "title", "text": "I wove a Jamdani for 90 days"}, {"role": "thumb", "text": "90 days"}])
        self.assertIn("thumb-repeats-title", [f["code"] for f in both["deck"]])
        long_first = "ক" * 140 + "\nবাকিটা"
        self.assertIn("hook-cut", [f["code"] for f in cr.lint_caption(long_first, "instagram", "BD")])
        deck = cr.lint_deck([{"role": "cta", "text": "Book now"}, {"role": "cta_2", "text": "Call us"}])
        self.assertIn("many-ctas", [f["code"] for f in deck["deck"]])

    def test_copylint_bengali_for_bangladesh(self):
        cr = d.copyrules
        codes = lambda t, role="body", loc="BD": [f["code"] for f in cr.lint_string(t, role, loc)]
        self.assertIn("bn-pattern", codes("অর্ডার করিলেই পাইবেন ফ্রী ডেলিভারি"))             # sadhu + ফ্রী
        self.assertIn("bn-pattern", codes("পেমেন্ট প্রদানের মাধ্যমে ক্যাশব্যাক গ্রহণ করা যাবে"))  # a notice chain
        self.assertEqual(codes("অ্যাপে পেমেন্টের মাধ্যমে ক্যাশব্যাক"), [])                   # one মাধ্যমে is normal
        self.assertIn("bn-pattern", codes("বিস্তারিতঃ পেজে দেখুন"))                           # visarga as a colon
        self.assertEqual(codes("দুঃখিত, আজ বন্ধ"), [])                                        # a real visarga
        self.assertIn("bn-pattern", codes("এখন সব আউটলেটে পাওয়া যাচ্ছে."))                   # '.' for '।'
        self.assertIn("bn-pattern", codes("দাম জানতে ইনবক্স করুন"))                           # print the price
        self.assertIn("bn-formal", codes("এখন সব আউটলেটে উপলব্ধ"))                             # a calque
        self.assertIn("bn-pronouns", codes("আপনি আপনার ফোন থেকে আপনার অ্যাকাউন্টে লগ ইন করুন।"))
        self.assertIn("bn-latin", codes("New Collection এখন Online এ", "headline"))
        self.assertIn("bn-locale", codes("ঠান্ডা জলের বোতল"))                                  # with a case ending
        self.assertIn("bn-kin", codes("মাসির জন্য শাড়ি"))
        self.assertNotIn("bn-kin", codes("গেমিং পিসির দাম"))            # পিসি is also "PC"
        self.assertEqual(codes("মাসিক অফার, জলপাইয়ের আচার"), [])                              # no false matches
        self.assertEqual(codes("অ্যাপে পেমেন্ট করলেই ক্যাশব্যাক। অফার চলবে ৩০ সেপ্টেম্বর পর্যন্ত।"), [])
        deck = cr.lint_deck([{"role": "head", "text": "আপনি কি প্রস্তুত?"}, {"role": "cta", "text": "অর্ডার করো"}], "BD")
        self.assertIn("bn-honorific", [f["code"] for f in deck["deck"]])
        self.assertNotIn("emoji-first", [f["code"] for f in cr.lint_caption("🔥 আজ রাতের অফার", "facebook", "BD")])

    def test_copylint_edge_cases_found_in_review(self):
        cr = d.copyrules
        # every en dash is read, not only the first: a benign range, then an AI pause dash
        self.assertEqual([f["code"] for f in cr.dashes("Open 09:00–13:00, then wander back – whenever", "latin")],
                         ["pause-dash"])
        self.assertEqual(d.dash_issues("Open 09:00–13:00, then wander back – whenever")[0][0], "error")
        codes = lambda t: [f["code"] for f in cr.lint_string(t, "body", "BD")]
        self.assertEqual(codes("তার গলায় নতুন মুক্তাহার, একদম মানানসই"), [])            # তাহার inside a word
        self.assertIn("bn-pattern", codes("আমরা কাজটি করিয়াছি, তাহার ফল পাইবেন"))       # inflected sadhu forms
        self.assertIn("bn-formal", codes("ক্রয়ের পূর্বে দেখে নিন"))                        # a case ending on ক্রয়

    def test_model_answers_that_break_the_schema_stop_cleanly(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bad = tmp / "j.json"
            for raw in ("{not valid, cut off", "[1, 2]", json.dumps({"scores": {}})):
                bad.write_text(raw)
                with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                    d._load_model_json(bad, ("scores", "gates"), "design judge")
            bad.write_text(json.dumps({"scores": {}, "gates": {}}))
            self.assertEqual(d._load_model_json(bad, ("scores", "gates"), "design judge")["gates"], {})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_copylint_command_writes_its_report_and_exits_2_on_errors(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            c = tmp / "post.copy.json"
            c.write_text(json.dumps({"strings": [{"role": "headline", "text": "Fresh bread — daily"}]}))
            ns = argparse.Namespace(copy=str(c), caption=None, text=None, role=None, locale="", platform="",
                                    brand=None, strict=False, json=False)
            with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()):
                d.cmd_copylint(ns)
            self.assertEqual(cm.exception.code, 2)
            self.assertTrue((tmp / "post.copylint.json").exists())          # not post.copy.copylint.json
            c.write_text(json.dumps({"strings": [{"role": "headline", "text": "Fresh bread, daily"}]}))
            with contextlib.redirect_stdout(io.StringIO()):
                d.cmd_copylint(ns)                                          # clean copy: no exit
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_the_judges_own_suggestions_are_linted(self):
        data = {"strings": [{"role": "headline", "text": "x", "natural": 3, "problem": "",
                             "rewrite": "Elevate your mornings \u2014 with us"}],
                "hooks": ["Delve into our tapestry", "Fresh bread at 7"], "cta": "Click here", "notes": []}
        d.relint_suggestions(data, [{"role": "headline", "text": "x", "lang": ""}], "", "instagram", None)
        self.assertTrue(any(x.startswith("error") for x in data["strings"][0]["rewrite_lint"]))   # the dash
        self.assertEqual(list(data["hooks_lint"]), ["Delve into our tapestry"])
        self.assertTrue(data["cta_lint"])
        self.assertTrue(data["notes"])

    def test_copy_verdict_bands(self):
        good = {k: 4 for k in d.COPY_CRITERIA}
        ok = [{"natural": 4}]
        self.assertEqual(d._copy_verdict({"scores": dict(good, naturalness=5, hook=5, locale=5), "strings": ok}, 0)[0],
                         "PASS_NATIVE")
        self.assertEqual(d._copy_verdict({"scores": good, "strings": ok}, 0)[0], "PASS")
        self.assertEqual(d._copy_verdict({"scores": good, "strings": ok}, 1)[0], "FAIL")     # a lint error (em dash)
        self.assertEqual(d._copy_verdict({"scores": dict(good, naturalness=2), "strings": ok}, 0)[0], "FAIL")
        self.assertEqual(d._copy_verdict({"scores": dict(good, hook=2), "strings": ok}, 0)[0], "REVISE")
        self.assertEqual(d._copy_verdict({"scores": good, "strings": [{"natural": 1}]}, 0)[0], "FAIL")

    def test_lengths_and_canvases(self):
        self.assertAlmostEqual(d.parse_len("25.4mm"), 96, places=3)
        self.assertEqual(d.parse_len("2in"), 192)
        c = d.resolve_canvas(None, "1080x1350")
        self.assertEqual((c["w_px"], c["h_px"], c["print"]), (1080, 1350, False))
        p = d.resolve_canvas(None, "148mmx210mm", "3mm")
        self.assertTrue(p["print"])
        self.assertAlmostEqual(p["w_px"], d.parse_len("154mm"), places=3)
        self.assertAlmostEqual(p["safe_px"][0], d.parse_len("8mm"), places=3)  # 5 mm safe inside a 3 mm bleed
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.resolve_canvas(None, "big")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.resolve_canvas("no-such-preset", None)

    def test_every_preset_resolves(self):
        for pid in d.presets():
            c = d.resolve_canvas(pid, None)
            self.assertGreater(c["w_px"], 0, pid)
            self.assertEqual(len(c["safe_px"]), 4, pid)

    def test_contrast_math(self):
        self.assertAlmostEqual(d.contrast_ratio(d.rel_lum(0, 0, 0), d.rel_lum(255, 255, 255)), 21, places=1)
        self.assertAlmostEqual(d.contrast_ratio(0.5, 0.5), 1.0)
        if HAVE_PIL:
            bg = Image.new("RGB", (100, 40), (255, 255, 255))
            self.assertGreater(d.text_contrast(bg, [0, 0, 100, 40], [0, 0, 0, 1])["p10"], 20)
            self.assertLess(d.text_contrast(bg, [0, 0, 100, 40], [250, 250, 250, 1])["p10"], 1.1)

    def test_crop_window_keeps_the_focus_and_flags_cuts(self):
        box, cut = d.crop_window(1600, 900, 1.0, (700, 200, 900, 400), False)
        self.assertEqual((box[2] - box[0], box[3] - box[1]), (900, 900))
        self.assertTrue(box[0] <= 700 and box[2] >= 900 and not cut)
        box, cut = d.crop_window(1600, 900, 9 / 16, (100, 100, 1500, 500), False)
        self.assertTrue(cut)  # a wide group cannot fit a story crop
        box, _ = d.crop_window(1600, 900, 1.0, (1500, 100, 1590, 200), False)
        self.assertEqual(box[2], 1600)  # clamped inside the photo

    def test_font_specs(self):
        self.assertEqual(d.parse_font_spec("Inter:400,700i"), ("Inter", [(400, "normal"), (700, "italic")]))
        self.assertEqual(d.parse_font_spec("Hind Siliguri"), ("Hind Siliguri", [(400, "normal"), (700, "normal")]))

    def test_judge_verdict_bands(self):
        gates = {g: "PASS" for g in d.DESIGN_GATES}
        good = {k: 4 for k in d.DESIGN_CRITERIA}
        self.assertEqual(d._judge_verdict({"scores": dict(good, message_fit=5, hierarchy=5), "gates": gates,
                                           "findings": []})[0], "PASS_SENIOR")
        self.assertEqual(d._judge_verdict({"scores": dict(good, message_fit=5, hierarchy=5, typography=5, originality=3),
                                           "gates": gates, "findings": []})[0], "PASS_SENIOR")
        self.assertEqual(d._judge_verdict({"scores": dict(good, originality=3), "gates": gates, "findings": []})[0],
                         "PASS")  # weighted 3.95: strong, not senior
        self.assertEqual(d._judge_verdict({"scores": {k: 3 for k in good}, "gates": gates, "findings": []})[0], "REVISE")
        self.assertEqual(d._judge_verdict({"scores": dict(good, finish=2), "gates": gates, "findings": []})[0], "REVISE")
        self.assertEqual(d._judge_verdict({"scores": good, "gates": dict(gates, brand="FAIL"), "findings": []})[0], "FAIL")
        self.assertEqual(d._judge_verdict({"scores": good, "gates": gates, "findings": [{"severity": "P0"}]})[0], "FAIL")
        self.assertEqual(d._judge_verdict({"scores": dict(good, hierarchy=3), "gates": gates, "findings": []})[0], "PASS")

    def test_text_diff_and_copy_formats(self):
        copy = [{"text": "Book a visit"}, {"text": "Sat 11 Oct – 09:00"}, {"text": "শুভ নববর্ষ"}]
        r = d.text_diff(copy, ["BOOK A VISIT", "Sat 11 Oct - 09:00", "Free coffee"])
        self.assertEqual(r["missing"], [])
        self.assertEqual(r["extra"], ["Free coffee"])
        self.assertEqual(r["skipped_non_latin"], 1)
        tmp = Path(tempfile.mkdtemp())
        try:
            for data, n in ((["One", "Two", " "], 2), ({"headline": "One", "cta": "Two", "n": 3}, 2),
                            ({"strings": [{"role": "h", "text": "One", "lang": "en"}, {"text": ""}]}, 1)):
                (tmp / "c.json").write_text(json.dumps(data))
                got = d.load_copy(tmp / "c.json")
                self.assertEqual(len(got), n)
                self.assertTrue(all(s["must_exact"] for s in got))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    @unittest.skipUnless(HAVE_PIL, "Pillow not available")
    def test_ground_under_text_and_around_logos(self):
        bg = Image.new("RGB", (400, 100), (22, 78, 87))
        clean = d.text_ground(bg, [[10, 10, 390, 90]], 0)
        self.assertGreater(clean["main"], 0.95)
        self.assertEqual(clean["far"], 0)
        for x in range(200, 210):  # a light stroke through the line
            for y in range(0, 100):
                bg.putpixel((x, y), (224, 163, 58))
        crossed = d.text_ground(bg, [[10, 10, 390, 90]], 0)
        self.assertGreater(crossed["far"], 0.003)
        ring = d.ring_ground(bg, [150, 30, 190, 70], 20)
        self.assertGreater(ring["far"], 0.01)
        self.assertEqual(d.ring_ground(bg, [20, 30, 60, 70], 10)["far"], 0)

    def test_pdffonts_parser_flags_type3(self):
        out = ("name                                 type              encoding         emb sub uni object ID\n"
               "------------------------------------ ----------------- ---------------- --- --- --- ---------\n"
               "AAAAAA+Figtree-Bold                  CID TrueType      Identity-H       yes yes yes      9  0\n"
               "BAAAAA+Kohinoor-Regular              Type 3            Custom           yes yes yes     11  0\n"
               "Helvetica                            Type 1            Builtin          no  no  no      12  0\n")
        saved = (d.shutil.which, d.subprocess.run)
        d.shutil.which = lambda name: "/usr/bin/pdffonts"
        d.subprocess.run = lambda *a, **k: argparse.Namespace(stdout=out, stderr="", returncode=0)
        try:
            r = d.pdf_fonts(Path("x.pdf"))
        finally:
            d.shutil.which, d.subprocess.run = saved
        self.assertEqual(r["count"], 3)
        self.assertEqual(r["type3"], ["Kohinoor-Regular"])
        self.assertEqual(r["not_embedded"], ["Helvetica"])
        self.assertIn("CID TrueType", r["types"])

    def test_verify_text_finds_changes_and_invented_copy(self):
        ocr = {"lines": [{"text": "NORTHLOAF", "box": [0, 0, 10, 10]}, {"text": "Baked before", "box": [0, 20, 10, 10]},
                         {"text": "SOURDOUGH PEOPLE", "box": [50, 20, 10, 10]}, {"text": "sunrise.", "box": [0, 40, 10, 10]},
                         {"text": "OPEN DAILY 7:00-14:00", "box": [0, 60, 10, 10]}, {"text": "Good Bread Days", "box": [0, 80, 10, 10]},
                         {"text": "Brunswik Stret", "box": [0, 100, 10, 10]}]}
        copy = [{"text": "Baked before sunrise"}, {"text": "Open daily 7:00–14:00"}, {"text": "Brunswick Street"},
                {"text": "Book now"}]
        r = d.verify_text(ocr, copy, ["Northloaf"])
        status = {x["text"]: x["status"] for x in r["copy"]}
        self.assertEqual(status["Baked before sunrise"], "punctuation")   # found across a side text, full stop added
        self.assertEqual(status["Open daily 7:00–14:00"], "case")
        self.assertEqual(status["Brunswick Street"], "altered")
        self.assertEqual(status["Book now"], "missing")
        self.assertEqual(status["Northloaf"], "case")                     # the allowed brand name, in capitals
        self.assertEqual([e["text"] for e in r["extra"]], ["SOURDOUGH PEOPLE", "Good Bread Days"])

    def test_direct_sizes(self):
        c = d.resolve_canvas("ig-portrait", None)
        self.assertEqual(d.direct_size(c, "codex")["aspect"], "4:5")
        api = d.direct_size(c, "api")["api_size"]
        w, h = (int(v) for v in api.split("x"))
        self.assertTrue(w % 16 == 0 and h % 16 == 0 and w * h <= d.API_RELIABLE_PX and w > 1080)
        self.assertFalse(d.direct_size(d.resolve_canvas("li-company-cover", None), "api")["possible"])  # 5.9:1

    @unittest.skipUnless(HAVE_PIL, "Pillow not available")
    def test_patch_alignment_undoes_a_small_shift(self):
        from PIL import ImageDraw
        orig = Image.new("RGB", (640, 800), (240, 236, 228))
        dr = ImageDraw.Draw(orig)
        for i in range(0, 640, 40):
            dr.rectangle([i, (i * 3) % 700, i + 25, (i * 3) % 700 + 60], fill=(40 + i % 200, 80, 120))
        edited = Image.new("RGB", (640, 800), (240, 236, 228))
        edited.paste(orig, (6, -4))          # the edit came back shifted by (6, -4) px
        aligned, rep = d.align_to(orig, edited, [[100, 100, 200, 160]])
        self.assertEqual(rep["shift_px"], [-6.0, 4.0])
        self.assertLess(rep["outside_diff_after"], rep["outside_diff_before"])

    def test_direct_frame_maps_final_percent_into_the_generated_image(self):
        c = d.resolve_canvas("og-image", None)                       # 1200x630 (1.905) -> Codex 16:9 (1.778)
        fr = d.direct_frame(c, "codex")
        self.assertEqual(fr["aspect"], "16:9")
        ox, oy, kx, ky = fr["crop"]
        self.assertAlmostEqual(kx, 1.0)
        self.assertAlmostEqual(ky, (16 / 9) / (1200 / 630), places=4)  # a centred band of the height
        self.assertAlmostEqual(oy, (1 - ky) / 2, places=4)
        x, y, w, h = d.frame_box(fr, [0, 0, 1, 1])
        self.assertAlmostEqual(y, oy, places=4)
        self.assertAlmostEqual(h, ky, places=4)
        self.assertEqual(d.fit_crop(1.0, 0.5, "top")[:2], [0.25, 0.0])  # square -> 1:2 anchored at the top

    def test_where_words_and_zone_kinds(self):
        self.assertEqual(d.where_words([0.8, 0.02, 0.15, 0.1]), "top-right")
        self.assertEqual(d.where_words([0.4, 0.4, 0.2, 0.2]), "centre")
        self.assertEqual(d.zone_kind("picture: loaf"), "picture")
        self.assertEqual(d.zone_kind("logo"), "logo")
        self.assertEqual(d.zone_kind("headline"), "text")
        for text_zone in ("Start button", "Smart badge", "Chart", "Heart rate stat", "Department hours"):
            self.assertEqual(d.zone_kind(text_zone), "text", text_zone)  # whole words only

    def test_text_budget_tiers(self):
        self.assertEqual(d.text_budget([{"text": "Baked before sunrise"}])["tier"], "A")
        b = d.text_budget([{"text": "Open daily 7:00–14:00"}, {"text": "Brunswick Street"}])
        self.assertEqual(b["tier"], "B")
        self.assertEqual(b["risky"], ["Open daily 7:00–14:00"])
        self.assertEqual(d.text_budget([{"text": "word " * 14}] * 3)["tier"], "C")

    def _dossier(self, **extra):
        base = {"id": "t1", "client": "Acme", "deliverable": "Instagram post", "preset": "ig-portrait",
                "concept": {"idea": "a", "visual": "b", "palette": "deep green wall (#2F4F43), cream type"},
                "copy": [{"role": "headline", "text": "Baked before sunrise", "lines": ["Baked before", "sunrise"]}]}
        base.update(extra)
        return base

    def test_direct_prompt_contract(self):
        c = d.resolve_canvas("ig-portrait", None)
        fr = d.direct_frame(c, "codex")
        dos = self._dossier(zones=[["headline", 9, 12, 82, 29, 2]])
        logo = {"gen_box": [0.84, 0.02, 0.12, 0.1]}
        refs = [(Path("sheet.png"), "brand", "the brand sheet.")]
        pr = d.direct_prompt(dos, c, fr, refs, logo)
        self.assertTrue(pr.startswith("Input images:\nImage 1 = BRAND"))
        self.assertIn('line 1 "Baked before" / line 2 "sunrise"', pr)
        self.assertIn("No other text anywhere", pr)
        self.assertIn("real logo is added there afterwards", pr)
        self.assertNotIn("#2F4F43", pr)                      # swatches are in the sheet: no codes in the text
        self.assertIn("headline x 9%-91%, y 12%-41%", pr)
        self.assertIn("Safe zones: every word stays inside x 10%-91%", pr)
        self.assertIn("No text smaller than about 2.7% of the image height", pr)
        pr2 = d.direct_prompt(dos, c, fr, [], None, None, ['"sunrise" was altered.'])
        self.assertIn("Draw no logo", pr2)
        self.assertTrue(pr2.rstrip().endswith('"sunrise" was altered.'))

    def test_dossier_lines_must_join_back(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            bad = self._dossier(copy=[{"text": "Baked before sunrise", "lines": ["Baked", "sunrise"]}])
            (tmp / "d.json").write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(SystemExit):
                d.load_dossier(tmp / "d.json")
            (tmp / "d.json").write_text(json.dumps(self._dossier()), encoding="utf-8")
            self.assertEqual(d.load_dossier(tmp / "d.json")["copy"][0]["must_exact"], True)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_ledger_recipe_rules(self):
        rec = {"structure": "fusion", "archetype": "editorial cover", "focal": "product", "device": "behind",
               "type_mode": "revival serif", "palette": "green ground", "finish": "photo"}
        earlier = [{"id": "p1", "client": "Acme", "recipe": dict(rec, finish="risograph")}]
        warn = d.ledger_check(self._dossier(recipe=rec), earlier)
        self.assertTrue(any("only 1 axes" in w for w in warn))
        self.assertTrue(any("archetype and focal" in w for w in warn))
        fresh = dict(rec, structure="replacement", archetype="object field", focal="type", finish="risograph")
        self.assertEqual(d.ledger_check(self._dossier(recipe=fresh), earlier), [])
        other_client = [dict(earlier[0], client="Other")]
        self.assertEqual(d.ledger_check(self._dossier(recipe=rec), other_client), [])

    def test_repair_boxes_merge_and_window(self):
        boxes = d.repair_boxes([[100, 100, 200, 130], [205, 100, 300, 130], [600, 900, 700, 940]], 1080, 1350, 0.5)
        self.assertEqual(len(boxes), 2)                       # the two touching words became one region
        win = d.repair_window(boxes[0], 1080, 1350)
        w, h = win[2] - win[0], win[3] - win[1]
        self.assertTrue(any(abs(w / h - a) < 0.01 for a in d.CODEX_ASPECTS.values()))  # a ratio the model makes
        self.assertTrue(win[0] <= boxes[0][0] and win[2] >= boxes[0][2])

    @unittest.skipUnless(HAVE_PIL, "Pillow not available")
    def test_wireframe_has_no_words_and_the_pointer_colour_is_unused(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            out = d.draw_wireframe([["headline", 0.1, 0.1, 0.8, 0.2, 2], ["photo", 0.2, 0.4, 0.6, 0.4],
                                    ["logo", 0.8, 0.02, 0.12, 0.08]], 400, 500, tmp / "w.png")
            with Image.open(out) as im:
                self.assertEqual(im.getpixel((5, 495)), (255, 255, 255))
                self.assertLess(sum(im.getpixel((200, 80))), 300)     # a dark headline bar
                self.assertEqual(d._near_count(im, (255, 0, 255)), 0)  # no magenta: a safe pointer colour
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_verify_text_word_boxes_and_duplicates(self):
        ocr = {"lines": [{"text": "Baked before sunrise daily", "box": [0, 0, 400, 50],
                          "words": [{"text": "Baked", "box": [0, 0, 90, 50]}, {"text": "before", "box": [100, 0, 110, 50]},
                                    {"text": "sunrise", "box": [220, 0, 120, 50]}, {"text": "daily", "box": [350, 0, 50, 50]}]},
                         {"text": "Baked before sunrise", "box": [0, 100, 400, 50]}]}
        r = d.verify_text(ocr, [{"text": "Baked before sunrise"}], [])
        self.assertEqual(r["copy"][0]["boxes"][0], [0, 0, 90, 50])
        extra = {e["text"]: e for e in r["extra"]}
        self.assertEqual(extra["daily"]["box"], [350, 0, 50, 50])   # only the extra word, not the whole line
        self.assertEqual(extra["Baked before sunrise"]["duplicate_of"], "Baked before sunrise")
        self.assertNotIn("duplicate_of", extra["daily"])

    def test_latin_copy_reads_cyrillic_lookalikes_as_latin(self):
        ocr = {"lines": [{"text": "100%", "box": [0, 0, 100, 50]}, {"text": "гуe", "box": [0, 60, 100, 200]}]}
        r = d.verify_text(ocr, [{"text": "100% rye"}], [])
        self.assertEqual(r["copy"][0]["status"], "exact")
        ocr_ru = {"lines": [{"text": "гуe", "box": [0, 0, 100, 50]}]}
        r2 = d.verify_text(ocr_ru, [{"text": "Привет"}], [])      # Cyrillic copy: no mapping
        self.assertEqual([e["text"] for e in r2["extra"]], ["гуe"])

    def test_exact_strings_claim_their_words_before_fuzzy_ones(self):
        ocr = {"lines": [{"text": "100%", "box": [0, 0, 100, 50]},
                         {"text": "Dark, dense, sliced thin.", "box": [0, 900, 500, 40]}]}
        r = d.verify_text(ocr, [{"text": "100% rye"}, {"text": "Dark, dense, sliced thin."}], [])
        st = {x["text"]: x["status"] for x in r["copy"]}
        self.assertEqual(st["Dark, dense, sliced thin."], "exact")   # not robbed of "Dark," by the fuzzy match
        self.assertEqual(st["100% rye"], "altered")
        self.assertEqual([x["text"] for x in r["copy"]], ["100% rye", "Dark, dense, sliced thin."])  # copy order

    @unittest.skipUnless(HAVE_PIL, "Pillow not available")
    def test_sketch_draws_labelled_zones(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            out = d.draw_sketch([["HEADLINE", 10, 10, 80, 20], ["PHOTO", 20, 40, 70, 50]], 400, 500, [20, 20, 20, 20],
                                tmp / "s.png")
            with Image.open(out) as im:
                self.assertEqual(im.size, (400, 500))
                self.assertLess(im.convert("L").getpixel((200, 60)), 240)   # inside the headline zone
                self.assertEqual(im.convert("L").getpixel((5, 5)), 255)     # outside every zone
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_fold_positions_resolve(self):
        c = d.resolve_canvas("trifold-a4", None)
        self.assertEqual(len(c["folds_px"]), 2)
        self.assertAlmostEqual(c["folds_px"][0][0], d.parse_len("100mm"), places=3)  # 97 mm + 3 mm bleed


@unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
class Photos(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    @unittest.skipUnless(HAVE_PIL, "needs Pillow")
    def test_judge_shows_a_carousel_strip_slide_by_slide(self):
        strip = Image.new("RGB", (2400, 600), (240, 236, 228))  # a 5-slide strip, as render --slides 5 writes it
        src = self.tmp / "carousel-strip.jpg"
        strip.save(src)
        views, text = d.judge_views(src, "Instagram carousel", False, self.tmp, slides=5)
        with Image.open(views[1]) as v:
            self.assertEqual(v.size, (5 * 390 + 4 * 16, 488))     # every slide at phone width, not 78 px each
        self.assertIn("5 slides", text)
        views, text = d.judge_views(src, "Instagram carousel", False, self.tmp)
        with Image.open(views[1]) as v:
            self.assertEqual(v.width, 390)                      # a single design keeps one phone-width view

    def test_judge_sees_the_preset_viewing_and_listing_sizes(self):
        cover = Image.new("RGB", (1600, 2560), (22, 78, 87))   # an e-book cover: product page and search results
        src = self.tmp / "cover.png"
        cover.save(src)
        views, text = d.judge_views(src, "e-book cover", False, self.tmp, 1, 300, 94)
        self.assertEqual(len(views), 4)                          # full, product page, listing, squint
        with Image.open(views[1]) as v, Image.open(views[2]) as t:
            self.assertEqual((v.width, t.width), (300, 94))
        self.assertIn("94 px wide", text)

    @unittest.skipUnless(HAVE_PIL and sys.platform == "darwin" and d.vision_bin(), "needs Apple Vision")
    def test_typeset_zone_wider_than_the_safe_area_stays_inside_it(self):
        im = Image.new("RGB", (1080, 1350), (30, 30, 30))
        c = d.resolve_canvas("ig-portrait", None)
        z = d.place_typeset(im, [{"text": "x", "zone": [0, 90, 120, 6]}], c)[0]
        st, sr, sb, sl = c["safe_px"]
        self.assertGreaterEqual(z[0], sl / 1080 * 100 - 1e-6)
        self.assertLessEqual(z[0] + z[2], 100 - sr / 1080 * 100 + 1e-6)
        self.assertLessEqual(z[1] + z[3], 100 - sb / 1350 * 100 + 1e-6)

    @unittest.skipUnless(HAVE_PIL and sys.platform == "darwin" and d.vision_bin(), "needs Apple Vision")
    def test_master_crop_slides_to_keep_text_near_an_edge(self):
        from PIL import ImageDraw, ImageFont
        im = Image.new("RGB", (1800, 600), (234, 223, 203))
        f = None
        for cand in ("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"):
            try:
                f = ImageFont.truetype(cand, 70)
                break
            except OSError:
                continue
        ImageDraw.Draw(im).text((30, 260), "Sourdough", font=f, fill=(47, 79, 67))   # 1.7% from the left edge
        src = self.tmp / "wide.png"
        im.save(src)
        out, info = d._to_master(src, 2.7, "center", self.tmp / "m.png")
        self.assertFalse(info["cut_text"])
        self.assertLessEqual(info["window"][0], 30)                  # the window moved left to keep the S
        with Image.open(out) as m:
            self.assertAlmostEqual(m.width / m.height, 2.7, places=2)

    def test_calm_regions_rank_the_flat_area_first(self):
        import random
        im = Image.new("L", (300, 300), 200)
        rnd = random.Random(1)
        for x in range(300):
            for y in range(150, 300):
                im.putpixel((x, y), rnd.randint(0, 255))
        p = self.tmp / "p.png"
        im.save(p)
        zones = d.calm_regions(p)
        self.assertIn(zones[0]["zone"], ("top-third", "top-half"))
        self.assertEqual(zones[0]["text"], "dark text")

    def test_reframe_outputs_every_size_and_warns(self):
        p = self.tmp / "wide.jpg"
        Image.new("RGB", (1600, 900), (120, 140, 160)).save(p)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            d.cmd_reframe(argparse.Namespace(src=str(p), presets="ig-square,ig-story,640x360", out_dir=str(self.tmp / "o"),
                                             name=None, focus="0.5,0.5", format="jpg"))
        rep = json.loads(out.getvalue())
        sizes = {o["preset"]: size_of(o["out"]) for o in rep["outputs"]}
        self.assertEqual(sizes["ig-square"], (1080, 1080))
        self.assertEqual(sizes["640x360"], (640, 360))
        story = next(o for o in rep["outputs"] if o["preset"] == "ig-story")
        self.assertTrue(any("upscaled" in w for w in story["warnings"]))

    def test_reframe_and_analyze_follow_exif_orientation(self):
        shown = Image.new("RGB", (600, 400), (200, 200, 200))
        p = self.tmp / "sideways.jpg"
        exif = Image.Exif()
        exif[0x0112] = 6  # stored rotated: shown = stored turned 90 degrees clockwise
        shown.transpose(Image.Transpose.ROTATE_90).save(p, exif=exif)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            d.cmd_reframe(argparse.Namespace(src=str(p), presets="640x360", out_dir=str(self.tmp / "o"), name=None,
                                             focus="0.5,0.5", format="jpg"))
        rep = json.loads(out.getvalue())
        self.assertEqual(rep["size"], [600, 400])
        self.assertEqual(rep["outputs"][0]["crop"], [0, 31, 600, 369])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            d.cmd_analyze(argparse.Namespace(src=str(p)))
        self.assertEqual(json.loads(out.getvalue())["size"], [600, 400])

    def test_sheet(self):
        for i in range(3):
            Image.new("RGB", (200, 100 + 50 * i), (i * 80, 90, 90)).save(self.tmp / f"{i}.png")
        out = d.make_sheet([str(self.tmp / f"{i}.png") for i in range(3)], self.tmp / "s.jpg", cell=120)
        self.assertTrue(out.exists())

    def test_image_formats_and_byte_limit(self):
        buf = io.BytesIO()
        import random
        rnd = random.Random(2)
        im = Image.new("RGB", (600, 400))
        im.putdata([(rnd.randint(0, 255), rnd.randint(0, 255), rnd.randint(0, 255)) for _ in range(600 * 400)])
        im.save(buf, "PNG")
        r = d.save_image(buf.getvalue(), self.tmp / "a.jpg", "jpg", 95, 120_000, False)
        self.assertLessEqual(r["bytes"], 120_000)
        self.assertLess(r["quality"], 95)
        r = d.save_image(buf.getvalue(), self.tmp / "b.png", "png", 90, None, True)
        self.assertIn(b"compositeSynthetic", (self.tmp / "b.png").read_bytes())

    def test_brand_css_from_tokens(self):
        (self.tmp / "brand.json").write_text(json.dumps({"colors": {"Ink": "#111", "brand primary": "#0E7490"},
                                                         "radius": 12, "logo": {"mark": "logo-mark.svg"}}))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            d.cmd_brand(argparse.Namespace(json=str(self.tmp / "brand.json"), out=None))
        css = (self.tmp / "brand.css").read_text()
        self.assertIn("--ink:#111", css)
        self.assertIn("--brand-primary:#0E7490", css)
        self.assertIn("--radius:12px", css)
        self.assertIn("--logo-mark:url('logo-mark.svg')", css)

    def test_font_install_writes_unicode_ranges_and_licences(self):
        meta = {"id": "demo-sans", "family": "Demo Sans", "subsets": ["latin", "bengali", "cyrillic"],
                "weights": [400, 700], "styles": ["normal"], "category": "sans-serif", "license": "OFL-1.1",
                "unicodeRange": {"latin": "U+0000-00FF", "bengali": "U+0980-09FE", "cyrillic": "U+0400-045F"}}
        saved = (d.font_meta, d.http_get, d.CACHE)
        d.font_meta = lambda fam: meta
        d.http_get = lambda url, timeout=40: b"wOF2fake"
        d.CACHE = self.tmp / "cache"
        try:
            res = d.install_fonts(["Demo Sans:400,700"], self.tmp / "fonts", ["latin", "bengali"])
        finally:
            d.font_meta, d.http_get, d.CACHE = saved
        css = (self.tmp / "fonts" / "fonts.css").read_text()
        self.assertEqual(res["files"], 4)
        self.assertIn("unicode-range:U+0980-09FE", css)
        self.assertIn("font-weight:700", css)
        self.assertIn("OFL-1.1", (self.tmp / "fonts" / "FONT-LICENSES.md").read_text())
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.font_meta, d.http_get = (lambda fam: meta), (lambda url, timeout=40: b"x")
            try:
                d.install_fonts(["Demo Sans:900"], self.tmp / "f2")
            finally:
                d.font_meta, d.http_get, d.CACHE = saved


@unittest.skipUnless(HAVE_CHROME and HAVE_PIL, "needs Google Chrome and Pillow")
class Render(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ch = d.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.ch.close()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_html(self, html: str, size="600x400", out="o.png", **kw) -> dict:
        p = self.tmp / "d.html"
        p.write_text(html, encoding="utf-8")
        preset = kw.pop("preset", None)
        c = d.resolve_canvas(preset, None if preset else size, kw.pop("bleed", None))
        return d.produce(self.ch, p, c, self.tmp / out, **kw)

    def test_typeset_overlay_picks_the_contrasting_colour_and_fits(self):
        bj = KIT.parent / "sample-brand" / "brand.json"
        brand = json.loads(bj.read_text(encoding="utf-8"))
        bg = Image.new("RGB", (1080, 1350), (240, 236, 228))
        bg.paste((22, 40, 44), (0, 675, 1080, 1350))            # light top half, dark bottom half
        src = self.tmp / "bg.png"
        bg.save(src)
        c = d.resolve_canvas("ig-portrait", None)
        entries = [{"text": "Open daily 7:00–14:00", "zone": [8, 20, 84, 8], "align": "left"},
                   {"text": "Brunswick Street, Fitzroy", "zone": [8, 70, 84, 8], "align": "left"}]
        rep = d.typeset_overlay(src, entries, c, brand, bj, self.tmp / "final.png", self.tmp / "master.png")
        self.assertEqual(rep["errors"], [])
        with Image.open(self.tmp / "final.png") as im:
            self.assertEqual(im.size, (1080, 1350))
            top = im.convert("L").crop((86, 270, 994, 378))
            bottom = im.convert("L").crop((86, 945, 994, 1053))
            self.assertLess(min(top.getdata()), 80)        # dark ink letters on the light half
            self.assertGreater(max(bottom.getdata()), 200)  # light paper letters on the dark half

    def test_exact_size_and_clean_design(self):
        rep = self.run_html(page("<h1 style='position:absolute;left:40px;top:40px;margin:0;font:700 48px serif;"
                                 "color:#111'>Hello</h1>"))
        self.assertEqual(size_of(rep["outputs"][0]["path"]), (600, 400))
        self.assertTrue(rep["checks"]["ok"], rep["checks"])
        self.assertEqual(rep["text"][0]["text"], "Hello")
        self.assertGreater(rep["text"][0]["contrast"], 15)

    def test_cut_text_missing_font_and_low_contrast_are_errors(self):
        body = ("<div style='position:absolute;left:20px;top:20px;width:120px;overflow:hidden;white-space:nowrap;"
                "font:24px serif'>This sentence is clipped</div>"
                "<div style='position:absolute;left:520px;top:200px;font:40px serif;white-space:nowrap'>Off the edge</div>"
                "<div style='position:absolute;left:20px;top:300px;font:24px NoSuchFont123'>Ghost font</div>"
                "<div style='position:absolute;left:300px;top:40px;font:24px serif;color:#f2f2f2'>Faint</div>")
        rep = self.run_html(page(body))
        errs = " ".join(rep["checks"]["errors"])
        self.assertFalse(rep["checks"]["ok"])
        self.assertIn("clipped", errs)
        self.assertIn("off canvas", errs)
        self.assertIn("NoSuchFont123", errs)
        self.assertIn("contrast", errs)

    def test_safe_zone_small_text_and_fit(self):
        body = ("<div style='position:absolute;left:10px;top:10px;font:30px serif'>Corner</div>"
                "<h1 id=h data-fit='20,200' style='position:absolute;left:100px;top:600px;width:600px;height:260px;"
                "margin:0;font-family:serif;line-height:1.1'>A headline that must fit its box</h1>"
                "<p style='position:absolute;left:100px;top:1100px;font:16px serif;margin:0'>tiny print</p>")
        head = f"<script src='{(KIT / 'cd-kit.js').as_uri()}'></script>"
        rep = self.run_html(page(body, head=head), preset="ig-portrait")
        warns = " ".join(rep["checks"]["warnings"])
        self.assertIn("outside the safe zone", " ".join(rep["checks"]["errors"]))   # the judge fails it: an error
        self.assertIn("below the", warns)
        h = next(t for t in rep["text"] if t["text"].startswith("A headline"))
        self.assertLess(h["size"], 200)
        self.assertGreaterEqual(h["size"], 20)
        body = ("<h1 data-fit='90,120' style='position:absolute;left:0;top:0;width:200px;height:100px;margin:0;"
                "font-family:serif'>Far too many words for this very small box</h1>")
        rep = self.run_html(page(body, head=head), size="600x400", out="f.png")
        self.assertIn("does not fit", " ".join(rep["checks"]["errors"]))

    @unittest.skipUnless(sys.platform == "darwin", "uses a local macOS font")
    def test_script_fallback_is_flagged(self):
        style = "@font-face{font-family:LatinOnly;src:local('Helvetica');unicode-range:U+0000-00FF}"
        body = "<p style='position:absolute;left:20px;top:20px;font:30px LatinOnly;margin:0'>Hello বাংলা</p>"
        rep = self.run_html(page(body, style))
        self.assertIn("bengali", " ".join(rep["checks"]["warnings"]))

    def test_carousel_slides_and_pdf(self):
        body = ("<div style='display:flex;width:calc(var(--canvas-w)*var(--slides));height:100%'>" +
                "".join(f"<section style='flex:none;width:var(--canvas-w);height:100%;background:hsl({i * 90} 50% 50%)'>"
                        f"<h2 style='margin:40px;font:40px serif;color:#000'>Slide {i + 1}</h2></section>" for i in range(3)) +
                "</div>")
        html = page(body).replace("width:var(--canvas-w);height", "width:calc(var(--canvas-w)*var(--slides));height", 1)
        rep = self.run_html(html, size="400x500", out="c.png", slides=3)
        files = [o["path"] for o in rep["outputs"]]
        self.assertEqual(len(files), 3)
        self.assertEqual(size_of(files[1]), (400, 500))
        self.assertTrue(Path(rep["preview_strip"]).exists())
        rep = self.run_html(html, size="400x500", out="c.pdf", slides=3, qa=False)
        self.assertEqual(rep["outputs"][0]["pages"], 3)

    def test_print_pdf_boxes_and_300dpi_png(self):
        html = page("<div style='position:absolute;inset:0;background:#123'></div>")
        rep = self.run_html(html, size="148mmx210mm", out="f.pdf", bleed="3mm", qa=False)
        note = rep["outputs"][0]["pdf_boxes"]
        try:
            from pypdf import PdfReader
        except ImportError:
            self.assertIn("doctor --setup", note)
            return
        pg = PdfReader(rep["outputs"][0]["path"]).pages[0]
        mm = lambda v: float(v) / 72 * 25.4
        self.assertAlmostEqual(mm(pg.mediabox.width), 154, delta=0.05)
        self.assertAlmostEqual(mm(pg.trimbox.width), 148, delta=0.05)
        self.assertAlmostEqual(mm(pg.trimbox.height), 210, delta=0.05)
        rep = self.run_html(html, size="148mmx210mm", out="f.png", bleed="3mm", qa=False)
        self.assertEqual(size_of(rep["outputs"][0]["path"]), (1819, 2551))

    def test_transparent_png_and_provenance_tag(self):
        gen = self.tmp / "gen.png"
        from PIL import PngImagePlugin
        info = PngImagePlugin.PngInfo()
        info.add_itxt("XML:com.adobe.xmp", "<x>trainedAlgorithmicMedia</x>")
        Image.new("RGB", (300, 200), (200, 100, 50)).save(gen, pnginfo=info)
        client = self.tmp / "client.png"
        Image.new("RGB", (300, 200), (50, 100, 200)).save(client)
        rep = self.run_html(page(f"<img src='{gen.as_uri()}' style='width:300px'>"), out="g.png")
        self.assertIn("composite", rep.get("provenance", ""))
        self.assertIn(b"compositeSynthetic", Path(rep["outputs"][0]["path"]).read_bytes())
        rep = self.run_html(page(f"<img src='{client.as_uri()}' style='width:300px'>"), out="c.png")
        self.assertNotIn("provenance", rep)
        html = "<!doctype html><html><body style='margin:0;background:transparent'><div style='width:50px;height:50px;background:red'></div></body></html>"
        rep = self.run_html(html, out="t.png", transparent=True, qa=False)
        with Image.open(rep["outputs"][0]["path"]) as im0:
            im = im0.convert("RGBA")
        self.assertEqual(im.getpixel((300, 300))[3], 0)
        self.assertEqual(im.getpixel((10, 10))[3], 255)

    def test_copy_file_placeholders_and_typography_lint(self):
        (self.tmp / "copy.json").write_text(json.dumps({"headline": "Hello world", "cta": "Book a visit"}))
        body = ("<h1 style='position:absolute;left:40px;top:30px;margin:0;font:700 48px serif'>Hello world</h1>"
                "<p style='position:absolute;left:40px;top:120px;margin:0;font:20px serif'>Lorem ipsum dolor</p>"
                "<p style='position:absolute;left:40px;top:160px;margin:0;font:20px serif'>A game-changing \"offer\" - now...</p>"
                "<p style='position:absolute;left:300px;top:250px;margin:0;font:40px serif'>Big</p>"
                "<p style='position:absolute;left:400px;top:250px;margin:0;font:42px serif'>Near</p>")
        rep = self.run_html(page(body), copy=d.load_copy(self.tmp / "copy.json"))
        errs, warns = " ".join(rep["checks"]["errors"]), " ".join(rep["checks"]["warnings"])
        self.assertIn("approved copy missing or altered: 'Book a visit'", errs)
        self.assertIn("placeholder", errs)
        self.assertIn("not in the approved copy", errs)          # unapproved text is an error (R6)
        self.assertIn("generic marketing language", warns)
        self.assertIn("straight quotes", warns)
        self.assertIn("ellipsis", warns)
        self.assertIn("spaced hyphen reads as a dash", warns)
        self.assertIn("too close", warns)
        self.assertEqual(rep["checks"]["copy"]["missing"], ["Book a visit"])

    def test_runt_overlap_and_seam(self):
        body = ("<h1 style='position:absolute;left:40px;top:30px;width:300px;margin:0;font:700 60px/1.05 serif'>"
                "Aaaaaaa Bbbbbbbb C</h1>"
                "<p style='position:absolute;left:400px;top:40px;margin:0;font:30px serif'>First line here</p>"
                "<p style='position:absolute;left:410px;top:48px;margin:0;font:30px serif'>Second on top</p>")
        rep = self.run_html(page(body))
        warns = " ".join(rep["checks"]["warnings"])
        self.assertIn("runt", warns)
        self.assertIn("overlaps", warns)
        html = page("<p style='position:absolute;left:350px;top:100px;margin:0;font:30px serif;white-space:nowrap'>"
                    "Across the cut</p>").replace("width:var(--canvas-w);", "width:calc(var(--canvas-w)*var(--slides));", 1)
        rep = self.run_html(html, size="400x500", out="s.png", slides=2)
        self.assertIn("seam", " ".join(rep["checks"]["warnings"]))

    @unittest.skipUnless(sys.platform == "darwin", "uses a macOS Bengali font")
    def test_tracked_bengali_is_flagged(self):
        body = ("<p lang='bn' style='position:absolute;left:20px;top:20px;width:500px;margin:0;"
                "font:32px/1.1 \"Kohinoor Bangla\";letter-spacing:.1em'>বাংলা লেখা এখানে আছে এবং আরও একটি লাইন</p>")
        rep = self.run_html(page(body))
        warns = " ".join(rep["checks"]["warnings"])
        self.assertIn("breaks conjuncts", warns)
        self.assertIn("line-height", warns)

    def test_icc_profile_pdf_fonts_and_vision_simulation(self):
        body = "<h1 style='position:absolute;left:20px;top:20px;margin:0;font:700 40px serif;color:#c00'>Colour</h1>"
        rep = self.run_html(page(body), simulate=["achromatopsia"])
        with Image.open(rep["outputs"][0]["path"]) as im:
            self.assertTrue(im.info.get("icc_profile"))
        sim = rep["simulations"][0]
        with Image.open(sim) as im:
            r, g, b = im.convert("RGB").getpixel((5, 5))[:3]
            self.assertTrue(abs(r - g) < 4 and abs(g - b) < 4)
        rep = self.run_html(page(body), size="148mmx210mm", out="f.pdf", qa=False)
        fonts = rep["outputs"][0]["fonts"]
        if fonts is not None:
            self.assertGreaterEqual(fonts["count"], 1)
            self.assertEqual(fonts["not_embedded"], [])

    def test_upscaled_and_broken_images_are_reported(self):
        small = self.tmp / "small.png"
        Image.new("RGB", (100, 60), (90, 90, 90)).save(small)
        body = (f"<img src='{small.as_uri()}' style='width:500px;height:300px;object-fit:cover'>"
                f"<img src='{(self.tmp / 'missing.png').as_uri()}' style='width:50px;height:50px'>")
        rep = self.run_html(page(body))
        self.assertIn("larger than its pixels", " ".join(rep["checks"]["warnings"]))
        self.assertRegex(" ".join(rep["checks"]["errors"]), r"failed to load \S*missing\.png: the file is not there")

    def test_line_through_text_and_logo_clear_space(self):
        body = ("<div style='position:absolute;inset:0;background:#164E57'></div>"
                "<div style='position:absolute;left:300px;top:0;width:10px;height:400px;background:#E0A33A'></div>"
                "<h1 style='position:absolute;left:40px;top:60px;margin:0;font:700 60px/1 serif;color:#fff;"
                "white-space:nowrap'>Crossed headline</h1>"
                "<div class='logo' style='position:absolute;left:40px;top:250px;width:80px;height:80px;border-radius:50%;"
                "background:#F3F1EC'></div>"
                "<p style='position:absolute;left:130px;top:270px;margin:0;font:24px serif;color:#fff'>Too close</p>")
        warns = " ".join(self.run_html(page(body))["checks"]["warnings"])
        self.assertIn("runs behind the letters", warns)
        self.assertIn("clear space of the logo", warns)

    def test_transparent_boxes_do_not_hide_text_but_painted_ones_do(self):
        body = ("<p style='position:absolute;left:40px;top:40px;margin:0;font:40px serif'>Under a glass box</p>"
                "<div style='position:absolute;inset:0'></div>"
                "<p style='position:absolute;left:40px;top:200px;margin:0;font:40px serif'>Under a card</p>"
                "<div style='position:absolute;left:30px;top:190px;width:200px;height:80px;background:#eee'></div>")
        rep = self.run_html(page(body))
        errs = " ".join(rep["checks"]["errors"])
        self.assertNotIn("Under a glass", errs)
        self.assertIn("'Under a card' (p): about", errs)
        self.assertIn("hidden under div", errs)

    def test_an_em_dash_on_a_design_is_an_error(self):
        body = ("<p style='position:absolute;left:80px;top:300px;margin:0;font:600 60px/1.2 serif'>Fresh bread — daily</p>"
                "<p style='position:absolute;left:80px;top:500px;margin:0;font:600 60px/1.2 serif'>Open 09:00–13:00</p>")
        rep = self.run_html(page(body), preset="ig-portrait", out="dash.png")
        errs = " ".join(rep["checks"]["errors"])
        self.assertIn("em dash", errs)
        self.assertNotIn("09:00", errs)                  # a range between numbers stays

    def test_dense_scripts_need_twelve_px_at_viewing_size(self):
        body = ("<p lang='bn' style='position:absolute;left:80px;top:300px;margin:0;font:500 30px/1.6 serif'>"
                "সুতোকথা স্টুডিও, ধানমন্ডি</p>"
                "<p lang='bn' style='position:absolute;left:80px;top:500px;margin:0;font:500 40px/1.6 serif'>"
                "প্রবেশ বিনামূল্যে</p>"
                "<p style='position:absolute;left:80px;top:700px;margin:0;font:500 30px/1.6 serif'>Free entry</p>")
        rep = self.run_html(page(body), preset="ig-story", out="bn.png")
        dense = [w for w in rep["checks"]["errors"] if "dense scripts" in w]
        self.assertEqual(len(dense), 1, dense)           # the 30 px Bengali only: 40 px and Latin pass
        self.assertIn("সুতোকথা", dense[0])
        self.assertIn("≥ 34px", dense[0])                # 12 px at 390 of 1080

    def test_fit_counts_lines_not_rect_tops(self):
        head = f"<script src='{(KIT / 'cd-kit.js').as_uri()}'></script>"
        # block spans in a flex column (their boxes are shorter than the text) and a smaller unit on the same baseline
        body = ("<h1 data-fit='40,200' data-fit-lines='2' style='position:absolute;left:20px;top:20px;width:560px;"
                "height:360px;margin:0;display:flex;flex-direction:column;justify-content:flex-end;"
                "font:700 200px/0.86 serif'><span>Two words</span> <span>Here</span></h1>"
                "<h1 data-fit='40,200' data-fit-lines='1' style='position:absolute;left:20px;top:420px;width:560px;"
                "height:240px;margin:0;white-space:nowrap;font:700 200px/0.8 serif'>200<span style='font-size:.5em'>"
                "&nbsp;km</span></h1>")
        rep = self.run_html(page(body, head=head), size="600x700", out="l.png")
        self.assertNotIn("does not fit", " ".join(rep["checks"]["errors"]), rep["checks"])
        sizes = {t["text"]: t["size"] for t in rep["text"]}
        self.assertGreater(sizes["Two words"], 40)
        self.assertGreater(sizes["200"], 40)

    def test_bottom_aligned_fit_counts_upward_overflow(self):
        head = f"<script src='{(KIT / 'cd-kit.js').as_uri()}'></script>"
        body = ("<h1 data-fit='20,120' style='position:absolute;left:20px;top:100px;width:400px;height:150px;margin:0;"
                "display:flex;align-items:flex-end;font:700 120px/1 serif'>Three short lines here</h1>")
        rep = self.run_html(page(body, head=head))
        h = rep["text"][0]
        self.assertLessEqual(h["box"][1], 150 + 0.25 * h["size"])  # fitted: the first line stays near the box top
        self.assertGreaterEqual(h["box"][1], 100 - 0.25 * h["size"])
        self.assertTrue(rep["checks"]["ok"], rep["checks"])

    def test_pages_are_captured_one_by_one_without_leaks(self):
        style = ".page{position:relative;width:var(--canvas-w);height:var(--canvas-h);overflow:hidden;break-after:page}"
        body = ("<section class='page' style='background:#F3F1EC'><p style='margin:40px;font:20px serif'>Front</p></section>"
                "<section class='page' style='background:#164E57'><p style='margin:40px;font:20px serif;color:#fff'>"
                "Back</p></section>")
        html = page(body, style).replace("height:var(--canvas-h);overflow", "height:calc(var(--canvas-h)*2);overflow", 1)
        rep = self.run_html(html, size="148mmx210mm", out="f.png", bleed="3mm", pages=2)
        files = [o["path"] for o in rep["outputs"]]
        self.assertEqual(len(files), 2)
        for f, colour in zip(files, ((243, 241, 236), (22, 78, 87))):
            with Image.open(f) as im:
                self.assertEqual(im.size, (1819, 2551))
                rgb = im.convert("RGB")
                self.assertEqual(rgb.getpixel((900, 0))[:3], colour)
                self.assertEqual(rgb.getpixel((900, 2550))[:3], colour)  # no row of the other page at the edge

    def test_print_prepress_checks(self):
        small = self.tmp / "small.png"
        Image.new("RGB", (120, 80), (90, 120, 90)).save(small)
        body = ("<div style='position:absolute;inset:0;background:#fff'></div>"
                "<p style='position:absolute;left:40px;top:40px;margin:0;font:12px serif;color:#16191B'>Near-black small</p>"
                "<div style='position:absolute;left:40px;top:100px;width:300px;height:60px;background:#164E57'></div>"
                "<p style='position:absolute;left:50px;top:118px;margin:0;font:400 10px sans-serif;color:#fff'>Reversed tiny</p>"
                f"<img src='{small.as_uri()}' style='position:absolute;left:40px;top:200px;width:300px;height:200px'>")
        rep = self.run_html(page(body), size="148mmx210mm", out="p.pdf", bleed="3mm")
        errs, warns = " ".join(rep["checks"]["errors"]), " ".join(rep["checks"]["warnings"])
        self.assertIn("four-colour black", warns)
        self.assertIn("small reversed text", warns)
        self.assertIn("ppi", errs)  # 120 px over 300 css px ≈ 38 ppi on paper

    def test_folds_keepouts_and_the_solemn_lint(self):
        style = ".page{position:relative;width:var(--canvas-w);height:var(--canvas-h)}"
        body = ("<section class='page'><p style='position:absolute;left:350px;top:200px;margin:0;font:20px serif;"
                "white-space:nowrap'>Across the fold</p></section>"
                "<section class='page'><p style='margin:60px;font:20px serif'>Inside</p></section>")
        html = page(body, style).replace("height:var(--canvas-h);overflow", "height:calc(var(--canvas-h)*2);overflow", 1)
        rep = self.run_html(html, preset="trifold-a4", out="b.pdf", pages=2)
        self.assertIn("the fold at 97.0 mm (side 1)", " ".join(rep["checks"]["warnings"]))
        rep = self.run_html(page("<p style='position:absolute;left:1100px;top:600px;margin:0;font:60px serif'>12:34</p>"),
                            preset="yt-thumbnail")
        self.assertIn("keep-out zone", " ".join(rep["checks"]["errors"]))
        body = "<h1 style='position:absolute;left:40px;top:40px;margin:0;font:40px serif'>Happy Memorial Day! 20% off</h1>"
        errs = " ".join(self.run_html(page(body), occasion="solemn")["checks"]["errors"])
        self.assertIn("'Happy' on a solemn day", errs)
        self.assertIn("selling on a solemn day", errs)

    def test_cmyk_pdf(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("pypdf not installed (doctor --setup)")
        body = "<div style='position:absolute;inset:0;background:#164E57'></div>"
        rep = self.run_html(page(body), size="85mmx55mm", out="c.pdf", bleed="3mm", qa=False, cmyk="generic")
        cm = next(o for o in rep["outputs"] if o["path"].endswith(".cmyk.pdf"))
        self.assertIn("CMYK", cm["colour"])
        pg = PdfReader(cm["path"]).pages[0]
        self.assertAlmostEqual(float(pg.mediabox.width) / 72 * 25.4, 91, delta=0.1)
        self.assertAlmostEqual(float(pg.trimbox.width) / 72 * 25.4, 85, delta=0.1)
        xobj = pg["/Resources"]["/XObject"]
        self.assertTrue(any(xobj[k].get_object()["/ColorSpace"] == "/DeviceCMYK" for k in xobj))

    def test_kit_links_are_served_from_the_skill(self):
        head = ("<link rel='stylesheet' href='https://codex-design.invalid/kit/cd-kit.css'>"
                "<link rel='stylesheet' href='https://codex-design.invalid/sample-brand/brand.css'>")
        html = (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>{head}</head><body>"
                "<div class='safe'><h1 style='margin:0;font:800 60px/1 var(--font-display);color:var(--primary)'>"
                "Kit and brand</h1></div></body></html>")
        rep = self.run_html(html, preset="ig-square")
        h = rep["text"][0]
        self.assertEqual(h["font"], "Bricolage Grotesque")          # the brand's web font loaded through the kit host
        self.assertTrue(rep["checks"]["ok"], rep["checks"])
        self.assertGreaterEqual(h["box"][0], 59)                    # .safe from the kit put it inside the safe zone

    def test_word_on_a_dark_patch_hyphen_breaks_and_tiny_logos(self):
        body = ("<div style='position:absolute;left:420px;top:0;width:180px;height:400px;background:#3a2a20'></div>"
                "<p style='position:absolute;left:10px;top:40px;margin:0;font:24px serif;color:#111;white-space:nowrap'>"
                "a long calm line of words that ends on the dark</p>"
                "<h1 style='position:absolute;left:10px;top:140px;width:160px;margin:0;font:700 60px/1 serif'>The 36-hour loaf</h1>")
        warns = " ".join(self.run_html(page(body))["checks"]["warnings"] + self.run_html(page(body))["checks"]["errors"])
        self.assertIn("part of it sits on a patch", warns)
        self.assertIn("breaks inside '36-hour' at its hyphen", warns)
        tiny = f"<img class='logo' src='{(KIT.parent / 'sample-brand' / 'logo-mark.svg').as_uri()}' style='position:absolute;left:80px;top:80px;width:30px;height:30px'>"
        self.assertIn("too small to recognise", " ".join(self.run_html(page(tiny), preset="ig-portrait")["checks"]["errors"]))

    @unittest.skipUnless(sys.platform == "darwin", "uses a macOS CFF font")
    def test_type3_fonts_are_flagged_in_print(self):
        body = "<p style='position:absolute;left:40px;top:40px;margin:0;font:24px \"Kohinoor Bangla\"'>বাংলা</p>"
        rep = self.run_html(page(body), size="148mmx210mm", out="t.pdf", bleed="3mm")
        fonts = rep["outputs"][0]["fonts"]
        if fonts is None:
            self.skipTest("pdffonts (poppler) not installed")
        self.assertTrue(fonts["type3"])
        self.assertIn("Type 3 fonts in a print PDF", " ".join(rep["checks"]["warnings"]))


class Tools(unittest.TestCase):
    def test_qr_svg(self):
        try:
            import segno  # noqa: F401
        except ImportError:
            for sp in sorted(d.VENV_DIR.glob("lib/python*/site-packages")):
                sys.path.append(str(sp))
            try:
                import segno  # noqa: F401
            except ImportError:
                self.skipTest("segno not installed (doctor --setup)")
        tmp = Path(tempfile.mkdtemp())
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                d.cmd_qr(argparse.Namespace(data="https://example.com", out=str(tmp / "q.svg"), error="m", border=4,
                                            dark="#000000", light="#ffffff", scale=10))
            rep = json.loads(out.getvalue())
            svg = (tmp / "q.svg").read_text()
            self.assertTrue(svg.lstrip().startswith("<svg"))
            self.assertIn(f'viewBox="0 0 {rep["modules_with_quiet_zone"]} {rep["modules_with_quiet_zone"]}"', svg)
            self.assertGreaterEqual(rep["min_print_mm"], 20)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_kit_command_copies_and_rewrites_links(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "design").mkdir()
            h = tmp / "design" / "post.html"
            h.write_text("<link rel='stylesheet' href='https://codex-design.invalid/kit/cd-kit.css'>")
            with contextlib.redirect_stdout(io.StringIO()):
                d.cmd_kit(argparse.Namespace(out=str(tmp / "design"), html=[str(h)], sample_brand=False))
            self.assertTrue((tmp / "design" / "kit" / "cd-kit.css").exists())
            self.assertIn("href='kit/cd-kit.css'", h.read_text())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_every_pattern_names_its_presets(self):
        pats = SCRIPT.parent.parent / "templates" / "patterns"
        readme = (SCRIPT.parent.parent / "templates" / "README.md").read_text()
        for f in sorted(pats.glob("*.html")):
            self.assertIn(f"`{f.name}`", readme, f"{f.name} is missing from templates/README.md")
            self.assertIn("<!-- Pattern:", f.read_text(), f"{f.name} has no pattern note")



class Production(unittest.TestCase):
    """What the production-readiness review (2026-09-24) found: help on every Python, copy file shapes, judge
    aggregation, the never-repeat ledger and the delivery gate."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_every_command_help_formats(self):
        # a bare % in a help string crashed every command at start-up on Python 3.14 (argparse checks it there)
        ap = d.build_parser()
        subs = next(a for a in ap._actions if isinstance(a, argparse._SubParsersAction))
        self.assertIn("deliver", subs.choices)
        self.assertIn("ledger", subs.choices)
        for name, sp in subs.choices.items():
            self.assertTrue(sp.format_help(), name)

    def test_copy_lint_calibrated_on_real_bangladeshi_and_ai_copy(self):
        # measured 2026-09-24 on natural and robotic corpora (review r5): natural Bangladeshi copy stays quiet,
        # word-for-word calques and stock English lines are caught
        def flagged(text, role="body", locale="BD"):
            return [f["code"] for f in d.copyrules.lint_string(text, role, locale, "facebook")
                    if f["severity"] in ("warning", "error")]
        for text, role in (("ঈদের কেনাকাটা এবার ঘরে বসেই!", "headline"), ("শীঘ্রই আসছে", "headline"),
                           ("২৫% মূল্যছাড়", "headline"), ("সুস্বাদু আচার", "headline"), ("আজই সংগ্রহ করুন", "cta"),
                           ("অর্ডার করতে এখনই ইনবক্স করুন", "cta"), ("মোঃ রহিম, পাইলট", "body"),
                           ("গেমিং পিসি", "body"), ("বর্তমানে শুধু ঢাকার ভেতরে ডেলিভারি", "body")):
            self.assertEqual(flagged(text, role), [], text)
        for text in ("এটি শুধু একটি পোশাক নয়, এটি একটি অনুভূতি", "এখনই অন্বেষণ করুন", "স্বাদ নিন নতুন উচ্চতায়",
                     "বাড়ির আরাম থেকে অর্ডার করুন", "প্রতিটি মুহূর্ত উদযাপন করুন",
                     "আপনি আপনার ফোন থেকে আপনার অ্যাকাউন্টে লগ ইন করুন"):
            self.assertTrue(flagged(text), text)
        for text, role in (("Last chance: 30% off ends Sunday at midnight", "body"),
                           ("Our seamless leggings stay put", "body")):
            self.assertEqual(flagged(text, role, "US"), [], text)
        for text in ("Not Just Coffee. It's an Experience.", "Where Comfort Meets Style", "Crafted with love",
                     "A seamless experience, every step of the way", "Tag someone who needs this",
                     "Indulge in the perfect blend of flavours"):
            self.assertTrue(flagged(text, "body", "US"), text)
        self.assertEqual(d.copyrules.visible_len("ক্ষেত্রে"), 2)  # ক্ষে + ত্রে as read, not 8 code points

    def test_voice_rules_are_calibrated_in_every_language(self):
        # the 2026-09-24 voice research: natural lines in 20 languages get no finding at all, robotic ones are caught
        cal = json.loads((SCRIPT.parent.parent / "tests" / "data" / "voice_calibration.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cal), 20)
        for lang, v in cal.items():
            loc = "BD" if lang == "bn" else ""
            for line in v["natural"]:
                self.assertEqual(d.copyrules.lint_string(line, "body", loc, "", lang), [], f"{lang}: {line}")
            caught = sum(1 for line in v["robotic"] if d.copyrules.lint_string(line, "body", loc, "", lang))
            self.assertGreaterEqual(caught / len(v["robotic"]), 0.95, lang)
        rules = json.loads((SCRIPT.parent / "voice_rules.json").read_text(encoding="utf-8"))["rules"]
        self.assertEqual(len({r["id"] for r in rules}), len(rules))
        for r in rules:
            d.copyrules._rule_regex(r)                                   # every pattern compiles
            self.assertNotRegex(r["what"] + r["replacement"], "[\u2014]| \u2013 ", r["id"])

    def test_the_lint_reads_each_language_on_its_own_terms(self):
        cr = d.copyrules
        self.assertEqual(cr.script_of("Nike 新品上市"), "han")               # a brand name does not make it Latin
        self.assertEqual(cr.lang_of("sale mein sab kuch aur bhi sasta"), "hi")  # Hinglish
        self.assertEqual(cr.lang_of("Hai kak, yuk ke toko"), "en")          # Indonesian "hai" is not Hindi
        # one "!" may end a hook outside English; an English headline takes none
        self.assertFalse([f for f in cr.lint_string("Jom tapau!", "headline", lang="ms") if f["code"] == "exclamation"])
        self.assertTrue([f for f in cr.lint_string("Fresh bread!", "headline") if f["code"] == "exclamation"])
        self.assertTrue([f for f in cr.lint_string("新品！限时！", "body", lang="zh") if f["code"] == "exclamation"])
        long_zh = cr.lint_string("我们的新款夏季连衣裙现在全部都在门店和网店同时上市销售中", "headline", lang="zh")
        self.assertTrue([f for f in long_zh if f["code"] == "long-headline"])
        # the English lists stay out of other languages; each language has its own
        self.assertFalse([f for f in cr.lint_string("i-unlock mo na ang rewards", "body", lang="tl")
                          if f["code"] == "ai-word"])
        self.assertTrue([f for f in cr.lint_string("Sumérgete en el sabor", "body", lang="es")
                         if f["code"] == "es-voice"])
        # Bangla: a stack of literary praise, a pile of slang, Banglish in a headline, the translated enjoy as the ask
        codes = lambda t, role="body": {f["code"] for f in cr.lint_string(t, role, "BD")}
        self.assertIn("bn-poetic", codes("অপরূপ ও মনোমুগ্ধকর এক সন্ধ্যা"))
        self.assertNotIn("bn-poetic", codes("নান্দনিক ডিজাইনের নতুন শোরুম"))  # one word alone is ordinary Bangla
        self.assertIn("bn-slang-pile", codes("জোস অফার, প্যারা নাই, পুরাই চিল"))
        self.assertIn("banglish", codes("Ajke order korun, delivery free", "headline"))
        self.assertIn("bn-enjoy-cta", codes("উপভোগ করুন", "cta"))
        self.assertNotIn("cta-verb", codes("ঘুরে আসেন", "cta"))            # the spoken আসেন is an ask too
        # copy that is heard gets the voice checks, and only then
        spoken = cr.lint_caption("Tickets are $25 and the 2nd show starts at 8.", "voiceover", "", "en", None,
                                 "voiceover")
        self.assertTrue([f for f in spoken if f["code"] == "en-voice"])
        self.assertFalse([f for f in cr.lint_string("Tickets are $25 and the 2nd show starts at 8.", "body")
                          if f["code"] == "en-voice"])
        self.assertEqual(len(cr._words("रात 11 बजे तक ऑर्डर कीजिए")), 6)  # vowel signs stay inside words

    def test_every_humanizer_rule_passes_its_own_lines_and_keeps_to_its_market_and_role(self):
        cr = d.copyrules
        rules = json.loads((SCRIPT.parent / "voice_rules.json").read_text(encoding="utf-8"))["rules"]
        tested = [r for r in rules if r.get("bad")]
        self.assertGreater(len(tested), 300)
        for r in tested:
            rx, need = cr._rule_regex(r), r.get("min", 1)
            self.assertGreaterEqual(len(rx.findall(r["bad"])), need, f"{r['id']} misses its bad line")
            self.assertLess(len(rx.findall(r["good"])), need, f"{r['id']} flags its good line")
        codes = lambda t, role="body", loc="", lang="": [f["code"] for f in cr.lint_string(t, role, loc, "", lang)]
        # a variant's words are wrong only in the other market: Brazilian words in a Portugal post, mainland words
        # in a Taiwan post
        self.assertIn("pt-voice", codes("Ligue pelo celular e faça o cadastro.", loc="PT", lang="pt"))
        self.assertNotIn("pt-voice", codes("Ligue pelo celular e faça o cadastro.", loc="BR", lang="pt"))
        self.assertEqual(cr.regions("BD"), {"BD"})
        self.assertEqual(cr.regions("", "zh-TW"), {"TW"})
        # role scopes: Title Case only in headlines, how an image was made only in alt text (a caption may have to
        # disclose it)
        self.assertIn("pt-voice", codes("Negociações Estratégicas E Parcerias Globais", "headline", lang="pt"))
        self.assertNotIn("pt-voice", codes("Negociações Estratégicas E Parcerias Globais", lang="pt"))
        self.assertIn("en-voice", codes("AI-generated image of a latte on a table", "alt"))
        self.assertNotIn("en-voice", codes("AI-generated image of a latte on a table", "caption"))
        # rules every language shares: invisible characters and look-alike letters
        self.assertIn("mul-voice", codes("Cоffee is back"))                   # a Cyrillic о
        self.assertIn("mul-voice", codes("New​ menu today"))
        self.assertEqual(cr.lang_of("Наш новый продукт"), "ru")
        # untagged Latin lines: the language's own small words, not the English lists
        self.assertEqual(cr.lang_of("Bestellen Sie jetzt"), "de")
        self.assertEqual(cr.lang_of("Frete grátis até domingo, corre que é só até lá"), "pt")
        self.assertNotIn("cta-verb", codes("Pide tu cupón", "cta"))
        self.assertEqual(cr.lang_of("Ami ajke order korbo, apnar jonno"), "bn")  # Banglish
        # the brand's own signature line is not flagged
        self.assertIn("ai-word", codes("A tapestry of flavours"))
        self.assertNotIn("ai-word", [f["code"] for f in cr.lint_string("A tapestry of flavours", "body",
                                                                        voice={"keep": ["tapestry of flavours"]})])

    def test_a_weekday_that_does_not_match_its_date_is_caught(self):
        import datetime
        cr, today = d.copyrules, datetime.date(2026, 9, 24)
        self.assertTrue(cr.weekday_slips("Sat 11 Oct, 9 am", today))           # a Sunday in 2026, a Monday in 2027
        self.assertFalse(cr.weekday_slips("Sat 10 Oct, 9 am", today))
        self.assertFalse(cr.weekday_slips("Sunday, 8 November 2026", today))
        self.assertTrue(cr.weekday_slips("Fri 29 Feb", today))                 # no such date in either year
        self.assertIn("weekday-date", [f["code"] for f in cr.lint_string("Tastings on Sat 11 Oct 2026", "body")])

    def test_the_caption_checks_know_the_platform_and_the_reply(self):
        cr = d.copyrules
        codes = lambda t, plat="instagram", role="caption": [f["code"] for f in cr.lint_caption(t, plat, "", "en",
                                                                                                 None, role)]
        self.assertEqual(cr.x_length("Hi https://example.com/a/very/long/path 👍🏽"), 3 + 23 + 1 + 2)
        self.assertIn("too-long", codes("word " * 60, "x"))
        self.assertNotIn("too-long", codes("word " * 50, "x"))
        self.assertEqual(cr.sms_parts("a" * 160), 1)
        self.assertEqual(cr.sms_parts("অ" * 71), 2)                           # Bengali is 70 a part
        self.assertIn("markdown", codes("**New** menu today"))
        self.assertNotIn("markdown", codes("*New* menu today", "whatsapp"))
        self.assertIn("link-in-bio", codes("New menu. Link in bio.", "facebook"))
        self.assertNotIn("link-in-bio", codes("New menu. Link in bio."))
        # a reply: read in short lines, opened with a name, no fold
        reply = "Hi Sam, thanks for flagging it. We checked your order. It left today. It arrives Friday."
        self.assertIn("reply-block", codes(reply, "facebook", "reply"))
        self.assertNotIn("greeting-open", codes(reply, "facebook", "reply"))
        self.assertEqual(len(cr._sentences(reply)), 4)                     # "it." ends a sentence
        # the rhythm the em dash ban pushes into colons, and the unprompted contrast
        self.assertIn("colon-reveals", codes("The secret: love. The result: joy. Book a table."))
        self.assertIn("not-tails", codes("Real butter, not margarine. Baked daily, not frozen."))
        self.assertNotIn("colon-reveals", codes("Our hours: 9 to 5. Our address: 12 Lake Road."))
        rep = cr.lint_deck([{"role": "body", "text": "Fresh bread, fresh cakes, fresh coffee, fresh start."}])
        self.assertIn("keep the same word", next(f["suggest"] for f in rep["deck"] if f["code"] == "repeat"))
        # "no X, no Y" is English: repeating a word shared with Spanish must not switch the English checks off
        self.assertEqual(cr.lang_of("No filler, no fluff. Just seamlessly good coffee, every single day."), "en")
        # X counts any emoji as 2 (twitter-text v3): a keycap, a flag, a family
        for e in ("1\ufe0f\u20e3", "\U0001F1E7\U0001F1E9", "\U0001F468\u200d\U0001F469\u200d\U0001F467"):
            self.assertEqual(cr.x_length(e), 2)
        # long text without commas or spaces stays fast (two patterns were quadratic)
        import time
        t0 = time.time()
        cr.lint_caption("word " * 8000, "x", "", "en", None, "caption")
        cr.lint_caption(("sku-" * 400)[:2000], "x", "", "en", None, "caption")
        self.assertLess(time.time() - t0, 5)

    def test_the_preset_catalogue_is_well_formed(self):
        data = json.loads((SCRIPT.parent / "presets.json").read_text(encoding="utf-8"))
        self.assertNotIn("—", json.dumps(data, ensure_ascii=False))
        ids = [p["id"] for p in data["presets"]]
        self.assertEqual(len(ids), len(set(ids)), "duplicate preset ids")
        for p in data["presets"]:
            self.assertRegex(p["id"], r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")      # book-5.5x8.5: dots only in numbers
            self.assertNotRegex(p["id"], r"(?<![0-9])\.|\.(?![0-9])")
            for side in p.get("folds_mm") or []:
                self.assertIsInstance(side, list, f"{p['id']}: folds_mm is one list of positions per side")
            for k in ("group", "label", "w", "h", "source", "verified", "confidence"):
                self.assertTrue(p.get(k), f"{p['id']} lacks {k}")
            c = d.resolve_canvas(p["id"], None)
            tw, th = c["trim_px"]
            st, sr, sb, sl = c["safe_px"]
            self.assertTrue(st + sb < c["h_px"] and sl + sr < c["w_px"], f"{p['id']}: the safe zone leaves no room")
            for k in p.get("keepout") or []:
                self.assertTrue(0 <= k[0] < k[2] <= tw + 1 and 0 <= k[1] < k[3] <= th + 1, f"{p['id']}: keepout {k}")
            self.assertIsInstance(p.get("aliases", []), list)
            if not c["print"]:  # a screen is seen at a width, or from a distance on a screen of known height
                self.assertTrue(p.get("view_width_px") or p.get("group") in ("document", "print") or
                                (p.get("view_distance_m") and p.get("screen_height_m")), f"{p['id']}: no viewing width")
            if p.get("file_scale"):
                self.assertTrue(c["print"] and p["file_scale"] >= 1, f"{p['id']}: file_scale is for print files")
        for r in data.get("retired", []):
            self.assertTrue(r.get("use") and all(u in ids for u in r["use"]), f"retired {r['id']} points nowhere")
            self.assertTrue(r.get("retired") and r.get("source"), f"retired {r['id']} lacks a date or source")

    def test_book_wraps_match_the_platforms_worked_examples(self):
        b = d.book_wrap("kdp", "paperback", 6, 9, 240, "cream")      # KDP's own example: 12.85 x 9.25 in
        self.assertAlmostEqual(b["spine"], 0.6, places=4)
        self.assertEqual([round(x, 4) for x in b["full"]], [12.85, 9.25])
        self.assertTrue(b["spine_text"])
        hc = d.book_wrap("kdp", "hardcover", 6, 9, 240, "cream")
        self.assertEqual([round(x * 25.4, 2) for x in hc["full"]], [364.84, 264.6])
        self.assertEqual([round(x, 3) for x in d.book_wrap("ingram", "paperback", 6, 9, 240, "cream")["full"]],
                         [12.795, 9.25])
        self.assertEqual([round(x, 3) for x in d.book_wrap("ingram", "hardcover", 6, 9, 240, "cream")["full"]],
                         [14.568, 10.5])
        self.assertEqual([round(x, 4) for x in d.book_wrap("lulu", "paperback", 6, 9, 240, "cream")["full"]],
                         [12.8505, 9.25])
        thin = d.book_preset(d.book_wrap("kdp", "paperback", 6, 9, 60, "white"), "thin")
        self.assertEqual(thin["css_vars"]["--spine-text"], "0")  # the pattern hides its spine title
        self.assertTrue(any(w.startswith("the spine") for w in thin["keepout_why"]))

    def test_preset_search_matches_word_starts(self):
        ids = [r["id"] for r in d.find_presets("ebook")]
        self.assertEqual(ids[0], "ebook-master")
        self.assertFalse(any(i.startswith("fb-") for i in ids))  # "ebook" is not found inside "facebook"
        self.assertEqual(d.find_presets("biye card")[0]["id"], "invite-5x7")
        self.assertEqual(d.find_presets("visiting card")[0]["id"], "visiting-card-bd")
        self.assertEqual(d.find_presets("cover page")[0]["id"], "report-cover-a4")
        first = d.find_presets("youtube story")[0]
        self.assertTrue(first.get("retired") and "yt-shorts-frame" in first["use"])
        # people misspell: a word that starts nothing in the catalogue is read as its closest spelling
        for typo, want in (("pintarest design", ("pin-standard",)), ("blog post thumbnil", ("blog-featured",)),
                           ("squrae size banner", ("fb-square", "ig-square")),
                           ("bilboard bd", ("billboard-bd-20x10ft",)), ("instagarm post", ("ig-portrait",))):
            self.assertIn(d.find_presets(typo)[0]["id"], want, typo)
        self.assertTrue(d.find_presets("youtute story")[0].get("retired"))

    def test_unknown_formats_are_found_or_stated(self):
        ids = [r["id"] for r in d.find_presets("pinterest pin")]
        self.assertIn("pin-standard", ids[:3])
        near = d.nearest_presets(1080, 1350, False)
        self.assertEqual(near[0]["ratio_off_pct"], 0.0)                 # a 4:5 size finds the 4:5 presets
        self.assertTrue(all(not d.presets()[n["id"]].get("print") for n in near))
        printed = d.nearest_presets(d.parse_len("148mm"), d.parse_len("210mm"), True)
        self.assertTrue(all(d.presets()[n["id"]].get("print") for n in printed))
        # a custom size without a spec gets stated assumptions, never silent ones
        c = d.apply_spec(d.resolve_canvas(None, "1500x3000"), argparse.Namespace())
        self.assertEqual(c["safe_px"], [75.0] * 4)
        self.assertEqual(c["view_width_px"], 390.0)
        self.assertEqual(len(c["assumed"]), 3)
        c = d.apply_spec(d.resolve_canvas(None, "1500x3000"),
                         argparse.Namespace(safe="10%", view_width=600, keepout=["0,2700,1500,3000"], min_text=40))
        self.assertEqual(c["assumed"], [])
        self.assertEqual(c["safe_px"], [150.0] * 4)
        self.assertEqual(c["keepout"], [[0.0, 2700.0, 1500.0, 3000.0]])
        c = d.apply_spec(d.resolve_canvas(None, "150mmx150mm"), argparse.Namespace())
        self.assertTrue(any("bleed" in a for a in c["assumed"]))
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.apply_spec(d.resolve_canvas(None, "1500x3000"), argparse.Namespace(keepout=["10,10,5,5"]))

    def test_text_seen_from_a_distance_gets_its_floor_from_the_distance(self):
        # a banner read from 5 m: ADA 703.5.5 capitals 16 mm + 10.5 mm per metre beyond 1.83 m (49 mm), font = cap / 0.7
        c = d.apply_spec(d.resolve_canvas(None, "600mmx1800mm"), argparse.Namespace(view_distance=5))
        self.assertAlmostEqual(c["min_text_px"], (16 + 10.5 * 3.17) / 0.7 * d.PX_PER_MM, delta=0.2)
        self.assertAlmostEqual(d.distance_ppi(c), 17.46, delta=0.01)     # 87.3 / 5 m
        self.assertEqual(d.distance_ppi(d.resolve_canvas("a5-flyer", None)), 240.0)
        self.assertEqual(d.distance_ppi(d.resolve_canvas("rollup-800x2000", None)), 150.0)  # the printer's own figure
        # read in passing from a road: capitals = distance / legibility index (USSC, MUTCD), on a file at 1:24
        c = d.resolve_canvas("billboard-us-bulletin", None)
        self.assertAlmostEqual(c["min_text_px"], 152 * 83.33 / 30 / 24 / 0.7 * d.PX_PER_MM, delta=0.2)
        self.assertIn("legibility index 30", c["distance_floor"])
        self.assertEqual(d.distance_ppi(c), 240.0)                       # 10 ppi at full size, times 24
        c = d.apply_spec(d.resolve_canvas(None, "24inx7in"),
                         argparse.Namespace(view_distance=152, legibility_index=30, file_scale=24))
        self.assertAlmostEqual(c["min_text_px"], 95.0, delta=0.2)
        self.assertIn("1:24", c["distance_floor"])
        # a menu screen 0.68 m high read from 4 m: DISCAS characters 20 mm tall, and no phone assumptions
        c = d.apply_spec(d.resolve_canvas(None, "1920x1080"), argparse.Namespace(view_distance=4, screen_height=0.68))
        self.assertAlmostEqual(c["min_text_px"], 45.4, delta=0.1)
        self.assertIsNone(c.get("view_width_px"))
        self.assertIn("DISCAS", c["distance_floor"])

    def test_a_project_preset_file_and_retired_formats(self):
        f = self.tmp / "presets.json"
        f.write_text(json.dumps({"presets": [{"id": "client-kiosk", "group": "signage", "label": "Mall kiosk screen",
                                              "w": 1080, "h": 1920, "safe": [96, 60, 96, 60], "view_width_px": 540,
                                              "aliases": ["kiosk"], "source": "client spec sheet 2026-09",
                                              "verified": "2026-09-24"}],
                                 "retired": [{"id": "old-format", "label": "An old format", "retired": "2023-06-26",
                                              "use": ["pin-9x16"], "aliases": ["old thing"], "notes": "Gone."}]}))
        saved = (dict(d._PRESETS), dict(d._RETIRED), list(d._PRESET_FILES))
        try:
            d._PRESETS.clear()
            d._RETIRED.clear()
            d._PRESET_FILES[:] = [str(f)]
            self.assertEqual(d.presets()["client-kiosk"]["origin"], str(f))
            self.assertEqual(d.resolve_canvas("client-kiosk", None)["safe_px"], [96.0, 60.0, 96.0, 60.0])
            self.assertEqual(d.find_presets("kiosk")[0]["id"], "client-kiosk")
            err = io.StringIO()
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
                d.resolve_canvas("old-format", None)
            self.assertIn("pin-9x16", err.getvalue())
            err = io.StringIO()
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(err):
                d.resolve_canvas("pin-standrd", None)                    # a typo gets suggestions
            self.assertIn("did you mean", err.getvalue())
        finally:
            d._PRESETS.clear(); d._PRESETS.update(saved[0])
            d._RETIRED.clear(); d._RETIRED.update(saved[1])
            d._PRESET_FILES[:] = saved[2]

    def test_copy_file_shapes_are_checked(self):
        f = self.tmp / "c.json"
        for bad in ({"strings": "Order a bag"}, {"strings": [{"role": "headline", "text": 42}]}, [], {"strings": [7]}):
            f.write_text(json.dumps(bad))
            with self.assertRaises(SystemExit, msg=bad), contextlib.redirect_stderr(io.StringIO()):
                d.load_copy(f)
        f.write_text(json.dumps({"locale": "BD", "platform": "facebook", "strings": [{"role": "headline",
                                                                                    "text": "ঈদের অফার"}]}))
        self.assertEqual(d.load_copy(f)[0]["text"], "ঈদের অফার")
        self.assertEqual(d.copy_meta(f), {"locale": "BD", "platform": "facebook"})

    def test_off_image_roles_stay_off_the_design_checks(self):
        copy = [{"role": "headline", "text": "Fresh at 7"}, {"role": "caption", "text": "Long caption"},
                {"role": "alt", "text": "A loaf"}, {"role": "video_title", "text": "How we bake"},
                {"role": "hashtags", "text": "#bread"}, {"role": "note", "text": "x", "on_image": True}]
        self.assertEqual([s["role"] for s in d.image_copy(copy)], ["headline", "note"])
        self.assertIsNone(d.image_copy(None))

    def test_locale_and_platform_are_validated(self):
        self.assertEqual(d.norm_locale("bd"), "BD")
        self.assertEqual(d.check_platform("YouTube-thumb"), "youtube-thumb")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.norm_locale("Bangladesh")
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            d.check_platform("insta")

    def test_judge_runs_aggregate_by_median_and_majority(self):
        def run(scores, gate, p0=False):
            return {"scores": dict.fromkeys(d.DESIGN_CRITERIA, scores), "gates": dict.fromkeys(d.DESIGN_GATES, "PASS")
                    | {"legibility": gate}, "gate_evidence": [], "text_read": [], "ai_tells": [], "fixes": [],
                    "keep": [], "findings": [{"severity": "P0" if p0 else "P2", "element": "e", "before": "b",
                                              "after": "a", "why": "w"}]}
        agg = d.aggregate_design([run(4, "PASS"), run(3, "FAIL", p0=True), run(4, "PASS")])
        self.assertEqual(agg["gates"]["legibility"], "PASS")          # one FAIL of three does not fail the gate
        self.assertEqual(set(agg["scores"].values()), {4})
        self.assertNotIn("P0", [f["severity"] for f in agg["findings"]])
        self.assertEqual(d._judge_verdict(agg)[0], "PASS")
        agg = d.aggregate_design([run(4, "FAIL"), run(3, "FAIL"), run(4, "PASS")])
        self.assertEqual(agg["gates"]["legibility"], "FAIL")
        cruns = [{"scores": dict.fromkeys(d.COPY_CRITERIA, v), "strings": [{"role": "h", "text": "t", "natural": v,
                                                                          "problem": "", "rewrite": ""}],
                  "ai_tells": [], "hooks": [f"hook {v}"], "cta": "Order", "notes": []} for v in (4, 5, 4)]
        agg = d.aggregate_copy(cruns)
        self.assertEqual(agg["scores"]["hook"], 4)
        self.assertEqual(agg["strings"][0]["natural"], 4)
        self.assertEqual(sorted(agg["hooks"]), ["hook 4", "hook 5"])

    def test_output_lock_refuses_a_second_writer(self):
        out = self.tmp / "post.png"
        with d.output_lock(out):
            with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
                with d.output_lock(self.tmp / "post.jpg"):   # same stem: same side files (post.qa.json)
                    pass
        with d.output_lock(out):                             # released
            pass

    def test_write_atomic_leaves_no_part_files(self):
        f = self.tmp / "a" / "x.json"
        d.write_atomic(f, "{}")
        d.write_atomic(f, b"[]")
        self.assertEqual(f.read_text(), "[]")
        self.assertEqual([p.name for p in f.parent.iterdir()], ["x.json"])

    def test_plate_notes_catch_a_rejected_candidate(self):
        plate = self.tmp / "story.png"
        cand = self.tmp / "story-c2.png"
        for f in (plate, cand):
            f.write_bytes(b"x")
        (self.tmp / "story.meta.json").write_text(json.dumps({
            "output_path": str(plate), "rejected": [str(cand)],
            "judge": {"computed_verdict": "PASS_WITH_NOTES", "defects": [
                {"what": "busy sky band", "where": "top 20%", "severity": "major"}]}}))
        notes = d.plate_notes({"images": [{"src": cand.as_uri()}]})
        self.assertTrue(any("rejected" in n for n in notes), notes)
        self.assertTrue(any("busy sky band" in n for n in notes), notes)
        self.assertEqual([n for n in d.plate_notes({"images": [{"src": plate.as_uri()}]}) if "rejected" in n], [])

    def test_ledger_flags_a_repeated_device_and_hook(self):
        entries = [{"id": f"p{i}", "client": "tok", "date": "2026-09-2{i}", "hook": h, "cta": "অর্ডার করুন",
                    "recipe": {"structure": s, "archetype": "a", "focal": "f", "device": dev, "type_mode": "t",
                               "palette": "p", "finish": "x"}}
                   for i, (h, s, dev) in enumerate([("বৃষ্টির দিনে ফুচকা", "split", "horizon lock"),
                                                    ("ঝাল কম, স্বাদ বেশি", "stack", "unit grid"),
                                                    ("অফিস শেষে টক ঝাল", "grid", "data spine")])]
        recipe = {"structure": "diptych", "archetype": "b", "focal": "g", "device": "unit grid", "type_mode": "u",
                  "palette": "q", "finish": "y", "hook": "বৃষ্টির দিনে গরম ফুচকা", "cta": "অর্ডার করুন"}
        warn, notes = d.repeat_check(recipe, "tok", entries, "new")
        self.assertTrue(any("device" in w for w in warn), warn)
        self.assertTrue(any("hook" in w for w in warn), warn)
        self.assertTrue(any("CTA" in n for n in notes), notes)
        recipe.update(device="aperture", hook="নতুন কিছু বলুন আজ")
        self.assertEqual(d.repeat_check(recipe, "tok", entries, "new")[0], [])
        self.assertEqual(d.ledger_check(d.recipe_dossier(recipe, "tok", "new"), entries), [])


@unittest.skipUnless(HAVE_CHROME and HAVE_PIL, "needs Google Chrome and Pillow")
class RenderProduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ch = d.Chrome()

    @classmethod
    def tearDownClass(cls):
        cls.ch.close()

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_html(self, html: str, size="600x400", out="o.png", **kw) -> dict:
        p = self.tmp / "d.html"
        p.write_text(html, encoding="utf-8")
        c = d.resolve_canvas(kw.pop("preset", None), size if "preset" not in kw else None)
        return d.produce(self.ch, p, c, self.tmp / out, **kw)

    def test_merch_renders_on_a_transparent_ground_and_folds_are_read_per_panel(self):
        art = "<div style='position:absolute;left:40%;top:40%;width:20%;height:20%;background:#164e57'></div>"
        self.run_html(art, preset="cap-embroidery-printful", out="s.png")
        with Image.open(self.tmp / "s.png") as im:
            self.assertEqual(im.convert("RGBA").getpixel((3, 3))[3], 0)   # the preset asks for transparency
        self.run_html(art, preset="cap-embroidery-printful", out="s.jpg")  # a JPG keeps a solid ground
        d.presets()
        d._PRESETS["t-wrap"] = d.book_preset(d.book_wrap("kdp", "paperback", 6, 9, 240, "cream"), "t-wrap")
        try:
            ground = "<div style='position:absolute;inset:0;background:#164e57'></div>"
            back = ("<div style='position:absolute;top:0;bottom:0;left:0;width:var(--spine-x);"
                    "background:#16191b'></div>")
            rep = self.run_html(ground + back, preset="t-wrap", out="w.pdf", preview=True)
            self.assertTrue(any("colour changes right at the fold" in w for w in rep["checks"]["warnings"]))
            rep = self.run_html(ground, preset="t-wrap", out="w2.pdf", preview=True)
            self.assertFalse(any("fold" in w for w in rep["checks"]["warnings"]))
        finally:
            d._PRESETS.pop("t-wrap", None)
        # a folded sheet: 25 and 26 px on different panels are fine, on one panel they are too close
        apart = ("<p style='position:absolute;left:30mm;top:40mm;margin:0;font:25px sans-serif'>Left panel</p>"
                 "<p style='position:absolute;left:180mm;top:40mm;margin:0;font:26px sans-serif'>Right panel</p>")
        rep = self.run_html(apart, preset="bifold-a4", out="b.pdf", preview=True)
        self.assertFalse(any("too close" in w for w in rep["checks"]["warnings"]))
        together = apart.replace("left:180mm;top:40mm", "left:30mm;top:90mm")
        rep = self.run_html(together, preset="bifold-a4", out="b2.pdf", preview=True)
        self.assertTrue(any("too close" in w for w in rep["checks"]["warnings"]))
        # a two-sided tri-fold (--pages 2) is judged panel by panel on each side too
        page = ("<section class='page' style='position:relative;width:var(--canvas-w);height:var(--canvas-h);"
                "break-after:page'>{}</section>")
        flap = "<p style='position:absolute;left:30mm;top:40mm;margin:0;font:25px sans-serif'>Flap words</p>"
        cover = "<p style='position:absolute;left:230mm;top:40mm;margin:0;font:26px sans-serif'>Cover words</p>"
        rep = self.run_html(page.format(flap + cover) + page.format(""), preset="trifold-a4", out="t.pdf", pages=2,
                            preview=True)
        self.assertFalse(any("too close" in w for w in rep["checks"]["warnings"]), rep["checks"]["warnings"])
        same = cover.replace("left:230mm", "left:30mm;top:90mm").replace("top:40mm;", "")
        rep = self.run_html(page.format(flap + same) + page.format(""), preset="trifold-a4", out="t2.pdf", pages=2,
                            preview=True)
        self.assertTrue(any("too close" in w for w in rep["checks"]["warnings"]), rep["checks"]["warnings"])
        # data-fit="floor" never leaves a line under the canvas's floor, even when its CSS size is smaller
        kit = "<script src='https://codex-design.invalid/kit/cd-kit.js'></script>"
        fit = kit + ("<p data-fit='floor' style='position:absolute;left:1in;top:1in;width:18in;margin:0;"
                     "font:20px sans-serif'>Coffee roasted today</p>")
        rep = self.run_html(fit, preset="billboard-us-bulletin", out="f.pdf")
        floor = d.resolve_canvas("billboard-us-bulletin", None)["min_text_px"]
        self.assertGreaterEqual(min(rep["checks"]["sizes_px"]), floor - 1)

    def test_renders_are_offline_and_failed_loads_are_errors(self):
        body = ("<link rel='stylesheet' href='missing.css'>"
                "<img src='http://127.0.0.1:9/pixel.png' style='width:10px;height:10px'>"
                "<p style='margin:40px;font:30px serif'>Offline</p>")
        errs = " ".join(self.run_html(page(body))["checks"]["errors"])
        self.assertIn("failed to load missing.css", errs)
        self.assertIn("pixel.png", errs)                      # the network image never loads (and is named)

    def test_provenance_preview_name_and_stale_slides(self):
        rep = self.run_html(page("<p style='margin:40px;font:30px serif'>Hello</p>"))
        q = json.loads(Path(rep["qa_json"]).read_text())
        self.assertEqual(q["source"]["outputs"][0]["sha256"], d.file_sha256(self.tmp / "o.png"))
        self.assertEqual(q["source"]["skill_version"], d.SKILL_VERSION)
        self.run_html(page("<p style='margin:40px;font:30px serif'>Print</p>"), size="100mmx100mm", out="p.pdf",
                      preview=True)
        self.assertTrue((self.tmp / "p.preview.png").exists())
        self.assertFalse((self.tmp / "p.png").exists())       # a 300 dpi p.png of an earlier render stays safe
        (self.tmp / "c-04.png").write_bytes(b"old")
        rep = self.run_html(page("<p style='margin:40px;font:30px serif'>Slide</p>"), out="c.png", slides=3)
        self.assertIn("c-04.png", " ".join(rep["checks"]["warnings"]))
        self.assertTrue((self.tmp / "c-04.png").exists())      # reported, never deleted

    def test_copy_split_over_inline_elements_still_matches(self):
        # <h1>The <em>36-hour</em> loaf</h1> is one approved string (a false error on Northloaf's thumbnail)
        copy = [{"role": "headline", "text": "The 36-hour loaf"}, {"role": "note", "text": "the hard bit"}]
        rep = self.run_html(page("<h1 style='margin:40px;font:50px serif'>The <em>36-hour</em> loaf</h1>"
                                 "<p style='margin:40px;font:30px serif'>the hard bit</p>"), copy=copy)
        self.assertEqual(rep["checks"]["errors"], [])
        rep = self.run_html(page("<h1 style='margin:40px;font:50px serif'>The <em>12-hour</em> loaf</h1>"), copy=copy[:1])
        self.assertTrue(any("missing or altered" in e for e in rep["checks"]["errors"]))

    def test_verify_reads_dashes_in_the_pictures_own_script(self):
        img = self.tmp / "gen.png"
        Image.new("RGB", (400, 300), (240, 240, 240)).save(img)
        line = {"text": "অফার চলবে ১০–১২ তারিখ", "box": [20, 20, 300, 40], "words": [], "alts": []}
        saved = d.ocr_lines
        d.ocr_lines = lambda *a, **k: {"lines": [line]}
        try:
            rep = d.verify_image(img, [], [], write=False)
        finally:
            d.ocr_lines = saved
        self.assertTrue(any("১০-১২" in w for w in rep["warnings"]), rep["warnings"])   # an en dash range in Bengali

    @unittest.skipUnless(d.GENERIC_CMYK.exists(), "needs the macOS Generic CMYK profile")
    def test_cmyk_alone_writes_no_preview(self):
        self.run_html(page("<p style='margin:20mm;font:14pt serif'>Print</p>"), size="100mmx100mm", out="c.pdf",
                      cmyk="generic")
        self.assertTrue((self.tmp / "c.cmyk.pdf").exists())
        self.assertFalse((self.tmp / "c.preview.png").exists())

    def test_a_page_too_big_for_chrome_is_refused(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            self.run_html(page("<p>big</p>"), size="12000x12000")

    def test_multi_page_documents_rendered_as_one_canvas_get_a_hint(self):
        body = "<section class='page'>One</section><section class='page'>Two</section>"
        errs = self.run_html(page(body), size="100mmx100mm", out="doc.pdf")["checks"]["errors"]
        self.assertIn("--pages 2", errs[0])

    def test_a_judge_verdict_is_reused_for_the_same_input_only(self):
        out = self.tmp / "x.judge.json"
        key = d.judge_key("prompt", "sha", "high", 1)
        self.assertNotEqual(key, d.judge_key("prompt", "sha", "high", 3))     # more runs is a new question
        self.assertFalse(d.cached_verdict(out, key, False))                  # nothing judged yet
        out.write_text(json.dumps({"verdict": "PASS", "cache_key": key}))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
            self.assertTrue(d.cached_verdict(out, key, False))
        self.assertTrue(json.loads(buf.getvalue())["cached"])
        self.assertFalse(d.cached_verdict(out, key, True))                   # --fresh asks again
        self.assertFalse(d.cached_verdict(out, d.judge_key("a new brief", "sha", "high", 1), False))

    def test_judge_refuses_a_render_with_errors(self):
        rep = self.run_html(page("<p style='position:absolute;left:-40px;top:10px;font:30px serif;margin:0'>Cut off "
                                 "text</p>"))
        self.assertTrue(rep["checks"]["errors"])
        if d._imagegen() is None:
            self.skipTest("codex-imagegen is not installed")
        ns = argparse.Namespace(image=str(self.tmp / "o.png"), brief=None, copy=None, allow=None, brand=None,
                                plate_meta=None, force=False, qa=None, kind="social post", canvas=None, print=False,
                                route="hybrid", effort="low", runs=1, timeout=30)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stderr(io.StringIO()):
            d.cmd_judge(ns)                                    # stops before any Codex session starts
        self.assertEqual(cm.exception.code, 2)

    def test_deliver_ships_only_what_passed_every_gate(self):
        rep = self.run_html(page("<h1 style='margin:60px;font:60px serif'>Fresh at 7</h1>"), size="1080x1350",
                            out="post.png")
        self.assertEqual(rep["checks"]["errors"], [])
        img = self.tmp / "post.png"
        copy = self.tmp / "post.copy.json"
        strings = [{"role": "headline", "text": "Fresh at 7"}, {"role": "alt", "text": "A loaf on a bench"}]
        copy.write_text(json.dumps({"locale": "US", "strings": strings}))
        judge = {"verdict": "PASS", "weighted": 4.0, "image_sha256": d.file_sha256(img), "runs": [{}, {}, {}]}
        (self.tmp / "post.judge.json").write_text(json.dumps(judge))
        deck = d.deck_hash([{"role": s["role"], "text": s["text"]} for s in strings])
        cj = self.tmp / "post.copyjudge.json"
        cj.write_text(json.dumps({"verdict": "PASS", "weighted": 3.9, "deck_sha256": deck}))
        ns = argparse.Namespace(design=[str(img)], out=str(self.tmp / "final"), copy=str(copy), caption=None,
                                locale=None, platform=None, brand=None, level="client", ledger=None, recipe=None,
                                client=None, name=None, force=False, dry_run=False)
        with self.assertRaises(SystemExit) as cm, contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            d.cmd_deliver(ns)                                  # client work needs PASS_NATIVE copy
        self.assertEqual(cm.exception.code, 2)
        self.assertFalse((self.tmp / "final").exists())
        cj.write_text(json.dumps({"verdict": "PASS_NATIVE", "weighted": 4.4, "deck_sha256": deck}))
        with contextlib.redirect_stdout(io.StringIO()):
            d.cmd_deliver(ns)
        self.assertTrue((self.tmp / "final" / "post.png").exists())
        md = (self.tmp / "final" / "DELIVERY-post.md").read_text()
        self.assertIn("A loaf on a bench", md)
        self.assertNotIn("—", md)
        img.write_bytes(img.read_bytes() + b"\0")               # changed after the judge saw it
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            d.cmd_deliver(ns)


if __name__ == "__main__":
    unittest.main()
