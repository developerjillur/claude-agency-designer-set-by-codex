"""Offline tests for codex_image.py (no Codex calls, no image generation).

Run:  python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests -v
Set CODEX_IMAGE_SCRIPT=/path/to/codex_image.py to test another copy.
"""
import argparse
import contextlib
import importlib.util
import io
import sys
import itertools
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(os.environ.get("CODEX_IMAGE_SCRIPT") or Path(__file__).resolve().parent.parent / "scripts" /
              "codex_image.py")
spec = importlib.util.spec_from_file_location("codex_image", SCRIPT)
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)
ci.log = lambda *a, **k: None

try:
    Image = ci.need_pillow()
    HAVE_PIL = True
except SystemExit:
    HAVE_PIL = False


def args_ns(**kw):
    base = dict(no_judge=False, fix_rounds=None, judge_effort=None, max_parallel=10, gen_effort="low", timeout=600,
                judge_workers=4, threshold=4, judge_model=None, concurrency=4, candidates=1, auto_candidates=True,
                prompt_writer="compiled", prompt_effort="medium", strict=False, early_exit=True, max_images=None)
    base.update(kw)
    return ci.fast_args(argparse.Namespace(**base))


def judge_result(verdict, gates=None, fix="fix it", mode="regenerate", total=None):
    return {"computed_verdict": verdict, "score_total": total or {"PASS": 23, "PASS_WITH_NOTES": 21}.get(verdict, 15),
            "scores": {"realism": 4}, "gates": gates or {}, "fix_mode": mode if verdict == "FAIL" else "none",
            "fix_instruction": fix if verdict == "FAIL" else ""}


class PromptAndPolicy(unittest.TestCase):
    def test_hints_and_style_detection(self):
        prompt, hints = ci.compile_prompt("Intent: product photo of a glass jar of honey, sun from the left", "1:1")
        self.assertIn("Format: square 1:1 format.", prompt)
        self.assertTrue(any("refracts" in h for h in hints))
        self.assertIn("unretouched real photograph", prompt)
        self.assertTrue(ci.is_non_photo("Intent: flat vector infographic for a blog"))
        self.assertFalse(ci.is_non_photo("Intent: product photo\nConstraints: not a 3D render, no logos"))

    def test_image_kind_separates_photos_styled_art_and_designs(self):
        k = ci.image_kind
        self.assertEqual(k("Intent: background photo for an Instagram post"), "photo")
        self.assertEqual(k('Intent: event poster for a jazz night, headline "Blue Hour"'), "design")
        self.assertEqual(k('Intent: poster with a photo of a runner, headline "Run the city"'), "design")
        self.assertEqual(k("Intent: YouTube thumbnail for a baking video"), "photo")  # no words to lay out
        self.assertEqual(k('Intent: text-free background plate for a YouTube thumbnail; three words "Bake it right" are '
                           'typeset later'), "photo")
        self.assertEqual(k("Intent: text-free plate for a poster\nStyle: flat vector illustration"), "styled")
        self.assertEqual(k("Intent: flat vector illustration of a bicycle"), "styled")
        self.assertEqual(k("Intent: Instagram post photo of a latte"), "photo")  # no quoted text: still a photo
        p, _ = ci.compile_prompt('Intent: Instagram post for a bakery launch\nText: "Now open"', "4:5")
        self.assertIn("finished graphic design", p)
        self.assertNotIn("An unretouched real photograph", p)
        p, _ = ci.compile_prompt("Intent: background photo for an Instagram post, calm space at the top", "4:5")
        self.assertIn("An unretouched real photograph", p)
        p, _ = ci.compile_prompt('Intent: poster with a photo of one runner mid-stride, headline "Run"', "2:3")
        self.assertTrue(any("skin" in h.lower() or "people" in h.lower() for h in ci.compile_prompt(
            'Intent: poster with a photo of one runner mid-stride, headline "Run"', "2:3")[1]))

    def test_tilt_and_upside_down_detection(self):
        self.assertEqual(ci.brief_risks("milk leaves the tilted pitcher's spout into the cup"), [])
        self.assertIn("tilted liquid container", ci.brief_risks("the barista tilts the cup 15 degrees"))
        self.assertEqual(ci.brief_risks("the pond reflects the house upside down"), [])
        self.assertIn("upside-down object resting on contact points",
                      ci.brief_risks("one bicycle turned upside down resting on its saddle"))

    def test_lint(self):
        warn = ci.lint_brief("A woman pours water from a kolshi (water pitcher), her right hand under it.", "3:2")
        text = " ".join(warn)
        self.assertIn("Grip & load", text)
        self.assertIn("pitcher, jug or jar", text)
        self.assertIn("frame position", text)
        self.assertEqual([w for w in ci.lint_brief("Intent: a quiet beach at dawn, sun from the left", "16:9")
                          if not w.startswith("risk")], [])

    def test_verdict_policy(self):
        G = {k: "PASS" for k in ("instruction_following", "text_exact", "physics", "hand_object", "anatomy",
                                 "no_unrequested_elements")}

        def J(g=None, **sc):
            s = {"realism": 4, "artifacts": 4, "physics_plausibility": 4, "composition": 4, "brief_fidelity": 4}
            s.update(sc)
            return {"gates": dict(G, **(g or {})), "scores": s, "defects": []}
        self.assertEqual(ci.verdict_of(J(), 4), "PASS")
        self.assertEqual(ci.verdict_of(J({"instruction_following": "FAIL"}, brief_fidelity=3), 4), "PASS_WITH_NOTES")
        self.assertEqual(ci.verdict_of(J(brief_fidelity=2), 4), "FAIL")
        self.assertEqual(ci.verdict_of(J({"physics": "FAIL"}), 4), "FAIL")
        self.assertEqual(ci.verdict_of(J(realism=3), 4), "FAIL")
        ci.STRICT["on"] = True
        try:
            self.assertEqual(ci.verdict_of(J({"instruction_following": "FAIL"}), 4), "FAIL")
        finally:
            ci.STRICT["on"] = False
        self.assertGreater(ci.judge_rank(judge_result("PASS_WITH_NOTES")),
                           ci.judge_rank(judge_result("FAIL", total=24)))

    def test_style_block(self):
        b = ci.style_block({"palette": ["#0ea5e9", "#f8fafc"], "light": "soft daylight"})
        self.assertIn("Style lock", b)
        self.assertIn("#0ea5e9, #f8fafc", b)
        self.assertEqual(ci.style_block(None), "")
        # inline style text longer than a file name is read as text, not looked up as a path (it crashed with
        # "File name too long" at 255 bytes)
        long_style = "Sample photos for a small coffee roastery, unretouched camera photos in real light. " * 4
        self.assertIn("small coffee roastery", ci.style_block(long_style))


class Pipeline(unittest.TestCase):
    def test_raw_prompt_reaches_the_codex_tool_verbatim(self):
        """codex-design's direct route compiles its own prompt: with --raw-prompt the fast compiled writer must not
        add the format, place, look or physics layers."""
        seen = {}

        def fake_parallel(tasks, workdir, args, kind="generate"):
            seen["prompt"] = tasks[0]["prompt"]
            return {"results": {t["id"]: {"ok": False, "src": None, "ms": None, "err": "x"} for t in tasks},
                    "sessions": []}

        args = argparse.Namespace(prompt_writer="compiled", raw_prompt=True)
        brief = 'Format: a 4:5 portrait image. A poster with the headline "Baked before sunrise".'
        with mock.patch.object(ci, "generate_parallel", fake_parallel):
            ci.gen_candidates({"aspect": "4:5", "hints": []}, "job", brief, 1, [], args, Path("."), "generate")
        self.assertEqual(seen["prompt"], brief)
        args.raw_prompt = False
        with mock.patch.object(ci, "generate_parallel", fake_parallel):
            ci.gen_candidates({"aspect": "4:5", "hints": []}, "job", brief, 1, [], args, Path("."), "generate")
        self.assertNotEqual(seen["prompt"], brief)  # the compiled layers are back

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src = self.tmp / "src.png"
        if HAVE_PIL:
            Image.new("RGB", (64, 48), (200, 120, 90)).save(self.src)
        else:
            self.src.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 64)
        self.counter = itertools.count()
        self.saved = (ci.codex_parallel_images, ci.run_judge, ci.job_pipeline)
        ci.BUDGET.used = 0

    def tearDown(self):
        ci.codex_parallel_images, ci.run_judge, ci.job_pipeline = self.saved
        ci.BUDGET.limit, ci.BUDGET.used = None, 0
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_gen(self, delays=None):
        def gen(tasks, workdir, effort, timeout, kind="generate", cancel=None):
            res = {}
            for t in tasks:
                d = (delays or {}).get(t["id"][-2:], 0)
                t0 = time.time()
                cancelled = False
                while time.time() - t0 < d:
                    if cancel is not None and cancel.is_set():
                        cancelled = True
                        break
                    time.sleep(0.02)
                if cancelled:
                    res[t["id"]] = {"ok": False, "src": None, "ms": None, "err": "cancelled"}
                    continue
                p = self.tmp / f"gen-{next(self.counter)}.png"
                shutil.copy2(self.src, p)
                res[t["id"]] = {"ok": True, "src": str(p), "ms": 10, "err": None}
            return {"results": res, "wall_s": 0.1, "thread_id": None, "session_total_ms": 1, "tokens": None}
        return gen

    def run_jobs(self, jobs, verdicts, delays=None, **kw):
        ci.codex_parallel_images = self.fake_gen(delays)
        ci.run_judge = lambda img, brief, threshold=4, model=None, effort="high", timeout=420, checklist=None, \
            job=None, **k: verdicts(job)
        return ci.fast_pipeline(jobs, args_ns(**kw), self.tmp, self.tmp / "out")

    def test_early_exit_cancels_slow_candidate(self):
        t0 = time.time()
        rep = self.run_jobs([{"name": "risky", "brief": "The barista tilts the cup while pouring", "aspect": "3:2"}],
                            lambda job: judge_result("PASS"), delays={"c1": 0.05, "c2": 5})
        self.assertLess(time.time() - t0, 3)
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "PASS")
        self.assertTrue(im["path"].endswith("risky.png"))
        self.assertIsNotNone(im.get("early_exit"))

    def test_model_limit_skips_fix(self):
        rep = self.run_jobs([{"name": "hard", "brief": "The barista tilts the cup while pouring", "aspect": "3:2"}],
                            lambda job: judge_result("FAIL", {"physics": "FAIL"}))
        im = rep["images"][0]
        self.assertEqual(im["model_limit"], ["physics"])
        self.assertEqual(len(im["rounds"]), 2)

    def test_fix_round_and_rename(self):
        rep = self.run_jobs([{"name": "plain", "brief": "A green coconut on a cart.", "aspect": "3:2"}],
                            lambda job: judge_result("FAIL") if job == "plain" else judge_result("PASS"))
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "PASS")
        self.assertTrue(im["path"].endswith("plain.png"))
        self.assertTrue((self.tmp / "out" / "plain-first.png").exists())

    def test_existing_file_is_never_touched(self):
        (self.tmp / "out").mkdir()
        old = self.tmp / "out" / "a.png"
        old.write_bytes(b"old")
        rep = self.run_jobs([{"name": "a", "brief": "A cup on a table.", "aspect": "1:1"}],
                            lambda job: judge_result("PASS"))
        self.assertEqual(old.read_bytes(), b"old")
        self.assertNotEqual(Path(rep["images"][0]["path"]).name, "a.png")

    def test_crash_isolation(self):
        real = ci.job_pipeline

        def jp(j, *a):
            if j["name"] == "boom":
                raise RuntimeError("exploded")
            return real(j, *a)
        ci.job_pipeline = jp
        rep = self.run_jobs([{"name": "ok", "brief": "A cup on a table.", "aspect": "1:1"},
                             {"name": "boom", "brief": "x", "aspect": "1:1"}], lambda job: judge_result("PASS"))
        by = {i["name"]: i for i in rep["images"]}
        self.assertEqual(by["ok"]["verdict"], "PASS")
        self.assertIn("exploded", by["boom"]["error"])

    def test_budget_caps_generations(self):
        rep = self.run_jobs([{"name": "b1", "brief": "A cup.", "aspect": "1:1"},
                             {"name": "b2", "brief": "A mug.", "aspect": "1:1"}], lambda job: judge_result("PASS"),
                            max_images=1)
        self.assertEqual(sum(1 for i in rep["images"] if i.get("path")), 1)

    def test_run_cancellable_kills_group(self):
        ev = threading.Event()
        threading.Timer(0.5, ev.set).start()
        t0 = time.time()
        _, err = ci.run_cancellable(["/bin/sh", "-c", "sleep 20 & sleep 20"], "", 60, self.tmp, ev)
        self.assertEqual(err, "cancelled")
        self.assertLess(time.time() - t0, 5)


@unittest.skipUnless(HAVE_PIL, "Pillow missing: run doctor --setup")
class WebAssets(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_export_variants_manifest_markup(self):
        src = self.tmp / "hero.png"
        Image.new("RGB", (1600, 900), (30, 120, 200)).save(src)
        out = self.tmp / "public" / "images"
        e = ci.web_export(src, out, alt='Clinic "reception"', eager=True)
        widths = sorted({v["width"] for v in e["variants"]})
        self.assertEqual(widths[-1], 1600)
        self.assertNotIn(1920, widths)
        self.assertIn('type="image/avif"', e["html"])
        self.assertIn('fetchpriority="high"', e["html"])
        self.assertIn("&quot;reception&quot;", e["html"])
        self.assertTrue(e["variants"][0]["url"].startswith("/images/"))
        manifest = json.loads(ci.update_manifest(out, [e]).read_text())
        self.assertTrue(manifest["hero"]["blurDataURL"].startswith("data:"))

    def test_alpha_export_and_clean(self):
        im = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        im.paste((250, 250, 250, 252), (100, 100, 300, 300))
        src = self.tmp / "icon.png"
        im.save(src)
        e = ci.web_export(src, self.tmp / "out", widths=[200], formats=("webp", "jpg"))
        self.assertTrue(e["alpha"])
        self.assertTrue(any(v["format"] == "png" for v in e["variants"]))
        self.assertEqual(ci.alpha_clean(im).getchannel("A").getextrema(), (0, 255))

    def test_refine_alpha_and_grey_view(self):
        im = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        for x in range(30, 90):
            for y in range(30, 90):
                im.putpixel((x, y), (250, 250, 250, 253))
        p = self.tmp / "asset.png"
        im.save(p)
        raw = ci.refine_alpha(p)
        self.assertTrue(raw and Path(raw).exists())
        with Image.open(p) as out:
            a = out.getchannel("A")
            self.assertEqual(a.getpixel((60, 60)), 255)
            self.assertEqual(a.getpixel((5, 5)), 0)
        with Image.open(ci.judge_view(p)) as v:
            self.assertEqual(v.mode, "RGB")
            self.assertEqual(v.getpixel((5, 5)), (128, 128, 128))

    def test_favicons_and_og(self):
        logo = self.tmp / "logo.png"
        Image.new("RGBA", (300, 200), (14, 165, 233, 255)).save(logo)
        res = ci.make_favicons(logo, self.tmp / "public", "Smile Dental", theme="#0ea5e9")
        for fn in ("favicon.ico", "apple-touch-icon.png", "android-chrome-512x512.png", "site.webmanifest"):
            self.assertTrue(Path(res["files"][fn]).exists(), fn)
        self.assertIn('rel="manifest"', res["html"])
        bg = self.tmp / "bg.png"
        Image.new("RGB", (1536, 1024), (40, 90, 140)).save(bg)
        og = ci.make_og(bg, "Gentle dental care for the whole family", self.tmp / "og.png", "Open six days a week",
                        logo, accent="#0ea5e9")
        with Image.open(og) as im:
            self.assertEqual(im.size, (1200, 630))

    @unittest.skipUnless(shutil.which("rsvg-convert") or shutil.which("qlmanage"), "no SVG rasterizer")
    def test_svg_rasterize_fills_canvas_with_alpha(self):
        svg = self.tmp / "mark.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
                       '<rect width="64" height="64" rx="16" fill="#0E7490"/><circle cx="32" cy="32" r="10" '
                       'fill="#ffffff"/></svg>')
        png = ci.rasterize_svg(svg, 512, self.tmp / "mark.png")
        with Image.open(png) as im:
            im = im.convert("RGBA")
            self.assertGreaterEqual(min(im.size), 400)
            self.assertEqual(im.getpixel((1, 1))[3], 0)
            self.assertEqual(im.getpixel((im.width // 2, im.height // 2))[:3], (255, 255, 255))
            self.assertEqual(im.getpixel((im.width // 2, im.height // 5))[3], 255)

    def test_cutout_keeps_interior_white(self):
        im = Image.new("RGB", (200, 200), (255, 255, 255))
        for x in range(60, 140):
            for y in range(60, 140):
                im.putpixel((x, y), (255, 255, 255) if 90 < x < 110 and 90 < y < 110 else (40, 40, 40))
        src = self.tmp / "obj.png"
        im.save(src)
        res = ci.cutout(src, self.tmp / "obj-cutout.png", feather=0)
        a = Image.open(res["out"]).getchannel("A")
        self.assertEqual(a.getpixel((5, 5)), 0)
        self.assertEqual(a.getpixel((100, 100)), 255)
        self.assertEqual(a.getpixel((70, 70)), 255)

    def test_audit_flags_problems(self):
        root = self.tmp / "site"
        (root / "public" / "img").mkdir(parents=True)
        Image.new("RGB", (3000, 2000), (1, 2, 3)).save(root / "public" / "img" / "hero.png")
        (root / "index.html").write_text('<img src="/img/hero.png">\n<img src="https://via.placeholder.com/300" '
                                         'alt="x" width="3" height="3">\n<img src="/img/missing.jpg" alt="m">')
        rep = ci.audit_site(root)
        kinds = set(rep["issue_counts"])
        for k in ("missing-alt", "no-dimensions", "placeholder-url", "oversized", "broken-ref?"):
            self.assertIn(k, kinds)


class Locale(unittest.TestCase):
    """Global by default, local from context: the place engine and project locale detection."""

    def test_global_default_when_the_brief_names_no_place(self):
        prompt, hints = ci.compile_prompt("Intent: website hero photo for a family dental clinic\n"
                                          "Subject: exactly one dentist talking with exactly one adult patient", "3:2")
        self.assertEqual(hints[:2], [ci.GLOBAL_SETTING, ci.GLOBAL_PEOPLE])
        self.assertIn("internationally neutral", prompt)

    def test_named_locale_line_becomes_place_rule_and_traffic_facts(self):
        brief = "Intent: street photo\nScene: a busy street corner with one bus, taxis and shops\nLocale: London, UK"
        prompt, hints = ci.compile_prompt(brief, "3:2")
        self.assertNotIn("Locale:", prompt)
        self.assertTrue(hints[0].startswith("Place and people: London, UK."))
        self.assertIn("present-day population", hints[0])
        self.assertTrue(any("traffic keeps to the left" in h and "wheel on the right" in h for h in hints))
        self.assertNotIn(ci.GLOBAL_SETTING, hints)

    def test_place_named_inside_the_brief_is_used(self):
        _, hints = ci.compile_prompt("Intent: travel photo\nScene: a street in Tokyo at dusk with taxis and shops", "3:2")
        self.assertTrue(any(h.startswith("Japan: traffic keeps to the left") for h in hints))
        self.assertTrue(any("Japanese script" in h for h in hints))
        self.assertNotIn(ci.GLOBAL_SETTING, hints)
        _, hints = ci.compile_prompt("Intent: street photo\nScene: a street in New York with yellow taxis", "3:2")
        self.assertTrue(any(h.startswith("United States: traffic keeps to the right") for h in hints))

    def test_objects_and_icons_get_no_place_rule(self):
        _, hints = ci.compile_prompt("Intent: app icon\nSubject: one clay tooth, isolated\nStyle: soft 3D icon", "1:1")
        self.assertFalse(any(h.startswith(("Place", "People")) for h in hints))
        _, info = ci.place_context("Intent: interior photo\nScene: a dental clinic reception\nSubject: no people")
        self.assertEqual(info["hints"], [ci.GLOBAL_SETTING])  # "no people" is not a cast
        lock = ci.style_block({"people": "relaxed expressions", "locale": "global"})
        _, info = ci.place_context("Intent: interior photo\nScene: a clinic reception\nSubject: no people\n" + lock)
        self.assertEqual(info["hints"], [ci.GLOBAL_SETTING])  # the style lock's "people" key adds no cast
        _, hints = ci.compile_prompt("Intent: hero photo\nSubject: one dentist with one patient\n"
                                     "Constraints: no text, signage or logos\nLocale: Tokyo, Japan", "4:3")
        self.assertFalse(any("signs use" in h for h in hints))  # "no signage" adds no signage fact

    def test_culture_markers_and_false_friends(self):
        _, info = ci.place_context("Intent: photo\nSubject: one woman carrying a kolshi on her hip in a village")
        self.assertEqual(info["mode"], "brief")  # the object names the culture: no neutral rule
        _, info = ci.place_context("Intent: cafe photo\nSubject: one barista pouring from a French press in a cafe\n"
                                   "Camera: Dutch angle")
        self.assertEqual(info["mode"], "global")  # French press / Dutch angle are not places
        self.assertEqual(ci.find_places("a nice cafe in paris"), [])  # running-text names must be capitalized

    def test_brief_place_beats_project_locale_and_lint_warns(self):
        brief = "Intent: travel photo\nScene: a tourist on a street in Tokyo\nLocale: Austin, Texas, USA"
        _, info = ci.place_context(brief)
        self.assertEqual((info["mode"], info["country"]), ("brief", "JP"))
        self.assertTrue(any("names its own place" in w for w in ci.lint_brief(brief, "3:2")))
        self.assertTrue(any("'local'" in w for w in ci.lint_brief("Intent: photo\nSubject: locals at a market", "3:2")))

    def test_locale_precedence_job_then_style_lock_then_global(self):
        style = ci.style_block({"mood": "calm", "locale": "Munich, Germany"})
        base = "Intent: clinic photo\nSubject: one dentist with one patient"
        _, info = ci.place_context(ci.with_locale(base, "Lagos, Nigeria") + "\n" + style)
        self.assertEqual((info["mode"], info["country"]), ("named", "NG"))
        _, info = ci.place_context(base + "\n" + style)
        self.assertEqual((info["mode"], info["country"]), ("named", "DE"))
        _, info = ci.place_context(ci.with_locale(base, "global"))
        self.assertEqual(info["mode"], "global")
        self.assertEqual(ci.with_locale(base + "\nLocale: Oslo, Norway", "Lagos"), base + "\nLocale: Oslo, Norway")

    def test_southern_hemisphere_season(self):
        _, hints = ci.compile_prompt("Intent: photo\nScene: a family Christmas lunch in a garden in Sydney", "3:2")
        self.assertTrue(any("southern hemisphere" in h for h in hints))

    def test_codex_runs_get_a_neutral_timezone(self):
        if os.environ.get("CODEX_IMAGEGEN_TZ") is None:
            self.assertEqual(ci.codex_env()["TZ"], "UTC")

    def test_auto_cast_rotates_only_global_people_jobs(self):
        lock = ci.style_block({"people": "relaxed expressions", "locale": "global"})
        jobs = [{"name": "hero", "brief": "Intent: hero\nSubject: one dentist in a white coat with one patient\n" + lock},
                {"name": "kids", "brief": "Intent: card\nSubject: one dentist showing one child how to brush\n" + lock},
                {"name": "room", "brief": "Intent: interior\nScene: a clinic reception\nSubject: no people\n" + lock},
                {"name": "told", "brief": "Intent: card\nSubject: one Black woman dentist with one patient\n" + lock},
                {"name": "tokyo", "brief": "Intent: card\nSubject: one dentist in Tokyo with one patient\n" + lock},
                {"name": "off", "cast": False, "brief": "Intent: card\nSubject: one nurse with one patient\n" + lock}]
        self.assertEqual(ci.auto_cast(jobs), 2)
        self.assertEqual([j.get("cast_auto") for j in jobs], ["African", "East Asian", None, None, None, None])
        self.assertIn("Cast (auto, global set): the main person is of African descent", jobs[0]["brief"])
        self.assertNotIn("Cast (auto", ci.judge_brief(jobs[0]["brief"]))  # the judge never grades appearance
        _, info = ci.place_context(jobs[1]["brief"])  # "East Asian" in the casting line is not a place
        self.assertEqual(info["mode"], "global")
        self.assertIn(ci.GLOBAL_SETTING, info["hints"])
        self.assertEqual(ci.auto_cast(jobs), 0)  # idempotent
        one = [{"name": "solo", "brief": "Intent: hero\nSubject: one dentist with one patient"}]
        self.assertEqual(ci.auto_cast(one), 0)  # a single image is not a set

    def test_brand_safe_signage_hint(self):
        _, hints = ci.compile_prompt("Intent: street photo\nScene: a street corner in London with shops", "3:2")
        self.assertIn(ci.BRAND_HINT, hints)
        _, hints = ci.compile_prompt("Intent: portrait\nSubject: one barista\nConstraints: no signage", "3:2")
        self.assertNotIn(ci.BRAND_HINT, hints)

    def test_capture_profile_is_picked_from_the_intent(self):
        pick = lambda b: ci.pick_look(b)[0]
        self.assertEqual(pick("Intent: user-generated review photo\nSubject: one woman holding a bottle"), "phone")
        self.assertEqual(pick("Intent: product photo for an online shop\nSubject: one mug on a counter"), "product")
        self.assertEqual(pick("Intent: interior photo for a rental listing\nSubject: no people"), "interior")
        self.assertEqual(pick("Intent: interior photo\nSubject: one family on the sofa"), "editorial")  # people
        self.assertEqual(pick("Intent: environmental portrait\nCamera: 50mm lens feel"), "portrait")
        self.assertIn("50mm lens", ci.pick_look("Intent: environmental portrait\nCamera: 50mm lens feel")[1])
        self.assertEqual(pick("Intent: lifestyle photo\nSubject: two friends cooking"), "editorial")
        self.assertEqual(pick("Intent: photo\nCamera: shot on a Leica M6 with Portra 400"), "brief")
        self.assertEqual(pick(ci.with_look("Intent: lifestyle photo\nSubject: one cook", "film")), "film")
        self.assertEqual(pick("Intent: lifestyle photo\nSubject: one cook\n" + ci.style_block({"look": "phone"})),
                         "phone")
        self.assertEqual(ci.pick_look(ci.with_look("Intent: photo\nSubject: one cook", "none")), ("none", ""))

    def test_realism_checks_and_capture_line_in_the_prompt(self):
        prompt, hints = ci.compile_prompt("Intent: lifestyle photo\nScene: a kitchen\nSubject: one man cooking", "3:2")
        self.assertIn("Capture: documentary photograph", prompt)
        self.assertIn(ci.PEOPLE_REAL, hints)
        self.assertIn(ci.SCENE_REAL, hints)
        self.assertNotIn("Look:", ci.compile_prompt(ci.with_look("Intent: photo\nSubject: one cook", "film"))[0])
        _, hints = ci.compile_prompt("Intent: product photo for an online shop\nSubject: one ceramic mug", "1:1")
        self.assertEqual([h for h in hints if h in (ci.PEOPLE_REAL, ci.SCENE_REAL, ci.PRODUCT_REAL)], [ci.PRODUCT_REAL])
        _, hints = ci.compile_prompt("Intent: portrait\nScene: a fishing harbour\nSubject: one old fisherman", "4:5")
        self.assertIn(ci.PEOPLE_REAL, hints)  # occupations count as people
        prompt, hints = ci.compile_prompt("Intent: flat vector illustration of a family\nStyle: flat design", "1:1")
        self.assertNotIn("Capture:", prompt)
        self.assertNotIn(ci.PEOPLE_REAL, hints)

    def test_text_objects_lint_and_night_hint(self):
        warn = ci.lint_brief("Intent: street food photo\nScene: a stall with a menu board too blurry to read\n"
                             "Constraints: no readable text", "3:2")
        self.assertTrue(any("text-bearing objects" in w for w in warn))
        self.assertFalse(any("text-bearing objects" in w for w in
                             ci.lint_brief("Intent: photo\nScene: a kitchen\nConstraints: no text, signage or logos",
                                           "3:2")))
        _, hints = ci.compile_prompt("Intent: photo\nScene: a taco stall at night in Mexico City", "3:2")
        self.assertTrue(any(h.startswith("At night the frame is mostly dark") for h in hints))

    def test_no_text_briefs_do_not_invite_signs_or_screen_text(self):
        brief = ("Intent: street food photo\nScene: a taco stall on a Mexico City sidewalk at night, a street lamp\n"
                 "Constraints: no readable text, no logos")
        _, hints = ci.compile_prompt(brief, "3:2")
        self.assertFalse(any("public street and traffic signs use" in h for h in hints))
        self.assertTrue(any(h.startswith("Any signs, menus, price boards or labels") for h in hints))
        _, hints = ci.compile_prompt("Intent: office photo\nScene: a laptop on a desk\nSubject: one designer\n"
                                     "Constraints: no text or logos", "3:2")
        self.assertTrue(any(h.startswith("Screens are seen at an angle") for h in hints))
        _, hints = ci.compile_prompt("Intent: photo\nScene: a kitchen with a wall clock\nSubject: one cook", "3:2")
        self.assertTrue(any("10:10" in h for h in hints))

    def test_style_lock_and_judge_guard_against_stock_polish(self):
        self.assertIn("small natural accents", ci.style_block({"palette": ["#0E7490 teal"]}))
        self.assertIn("ai_tells", ci.JUDGE_SCHEMA["required"])
        self.assertIn("reads as stock photography", ci.JUDGE_PROMPT)

    def test_detect_uk_site_and_ignore_dotfiles(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "index.html").write_text(
                '<html lang="en-GB"><head><link rel="canonical" href="https://www.brightsmile.co.uk/">'
                '<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans" rel="stylesheet"></head>'
                '<body>Call +44 20 7946 0000. Check-up £45. 12 Harley Street, London W1G 9PF</body></html>',
                encoding="utf-8")
            (d / ".env").write_text("SUPPORT=+880 1711 000000\nPRICE=৳ 1500\n", encoding="utf-8")
            (d / "styles.css").write_text("body { font-family: Verdana, Geneva, sans-serif; }", encoding="utf-8")
            rep = ci.detect_locale(d)
            self.assertEqual(rep["country"], "GB")
            self.assertEqual(rep["suggested"], "London, United Kingdom")
            flagged = {c for s in rep["signals"] for c in s["countries"]}
            self.assertEqual(flagged, {"GB"})  # nothing from .env, the font URL or the stylesheet

    def test_detect_bd_global_and_multi_market(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "index.html").write_text('<html lang="bn"><body>Hotline +880 1711-000000 · Scaling ৳ 1,500 · '
                                          'Road 5, Dhanmondi, Dhaka</body></html>', encoding="utf-8")
            rep = ci.detect_locale(d)
            self.assertEqual((rep["country"], rep["suggested"]), ("BD", "Dhaka, Bangladesh"))
            self.assertEqual(rep["facts"]["traffic"], "keeps to the left")
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "index.html").write_text('<html lang="en"><body>Book online. Plans from $49.</body></html>',
                                          encoding="utf-8")
            self.assertEqual(ci.detect_locale(d)["suggested"], "global")
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "index.html").write_text('<html lang="en"><head><link rel="alternate" hreflang="en-US" href="/us">'
                                          '<link rel="alternate" hreflang="de-DE" href="/de"></head></html>',
                                          encoding="utf-8")
            self.assertEqual(ci.detect_locale(d)["multi_locale"], ["de-DE", "en-US"])

    def test_detect_from_request_text_and_nanp_phone(self):
        rep = ci.detect_locale(None, "Build a website for a family dental clinic in Austin, Texas")
        self.assertEqual((rep["country"], rep["suggested"]), ("US", "Austin, Texas, United States"))
        self.assertEqual(ci.detect_locale(None, "Call us: +1 416 555 0199, +1 647 555 0101")["country"], "CA")



@unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
class Finish(unittest.TestCase):
    """Photographic finish: cast correction, protected highlights, grain, raw copy, defaults."""

    def _warm(self, d):
        im = Image.new("RGB", (600, 400), (150, 110, 80))  # orange midtones
        im.paste((255, 255, 255), (0, 0, 120, 80))  # a clipped white lamp
        p = Path(d) / "warm.png"
        im.save(p)
        return p

    def test_finish_in_place_reduces_cast_and_keeps_raw(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._warm(d)
            info = ci.finish_image(p, "natural")
            self.assertTrue((Path(d) / "warm-raw.png").exists())
            self.assertLess(info["cast_after"], info["cast_before"] - 15)
            out = Image.open(p).convert("RGB")
            r, g, b = out.getpixel((10, 10))
            self.assertLessEqual(max(r, g, b) - min(r, g, b), 6)  # the clipped white stays neutral, not cyan
            mean = sum(ci.need_pillow().open(p).convert("L").getdata()) / (600 * 400)
            mean0 = sum(Image.open(Path(d) / "warm-raw.png").convert("L").getdata()) / (600 * 400)
            self.assertLess(abs(mean - mean0), 6)

    def test_warm_scene_keeps_mood_and_out_dir_copy(self):
        with tempfile.TemporaryDirectory() as d:
            p = self._warm(d)
            od = Path(d) / "out"
            od.mkdir()
            warm = ci.finish_image(p, "natural", dst=od / "warm.png", warm_scene=True)
            full = ci.finish_image(p, "natural", dst=od / "full.png")
            self.assertGreater(warm["cast_after"], full["cast_after"])
            self.assertFalse((Path(d) / "warm-raw.png").exists())  # dst given: the source is untouched

    def test_finish_tags_generated_sources_only_and_marks_the_finish(self):
        with tempfile.TemporaryDirectory() as d:
            gen = Path(d) / "gen.png"
            Image.new("RGB", (400, 300), (150, 110, 80)).save(gen, **ci.provenance_kwargs(gen))  # a generated file
            client = self._warm(d)  # no provenance: stands for a client's own photo
            for p in (gen, client):
                ci.finish_image(p, "natural")
            with Image.open(gen) as im:
                self.assertIn("trainedAlgorithmicMedia", im.info.get("XML:com.adobe.xmp", ""))
                self.assertEqual(im.info.get(ci.FINISH_MARK), "natural")
            with Image.open(client) as im:
                self.assertNotIn("XML:com.adobe.xmp", im.info)  # never mislabel a real photo as AI
                self.assertEqual(im.info.get(ci.FINISH_MARK), "natural")
            self.assertTrue(ci.is_finished(gen))
            self.assertEqual(ci.with_finish_default({"look": "editorial", "target": str(gen)}), "none")
            self.assertIn("xmp", ci.provenance_kwargs(Path(d) / "a.webp"))

    def test_finish_defaults_follow_the_look(self):
        f = ci.with_finish_default
        self.assertEqual(f({"look": "editorial"}), "natural")
        self.assertEqual(f({"look": "phone"}), "phone")
        self.assertEqual(f({"look": "product"}), "clean")
        self.assertEqual(f({"look": "portrait"}), "portrait")
        self.assertEqual(f({"look": "-"}), "none")
        self.assertEqual(f({"look": "editorial", "transparent": True}), "none")
        self.assertEqual(f({"look": "editorial", "finish": "none"}), "none")
        self.assertEqual(f({"look": "editorial", "finish": "film"}), "film")


class Production(unittest.TestCase):
    """Production paths: the batch CLI, failures that must not lose work, provenance, recovery, degradation."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.src = self.tmp / "src.png"
        if HAVE_PIL:
            Image.new("RGB", (64, 48), (200, 120, 90)).save(self.src)
        else:
            self.src.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\0" * 64)
        self.counter = itertools.count()
        self.saved = (ci.codex_parallel_images, ci.run_judge, ci.finish_image, ci.codex_bin, ci.codex_version,
                      ci.cmd_generate_or_edit, ci.CODEX_HOME, ci.LOCALE_FILE, ci.engine_codex)
        self.log_dir, self.fail_dir = ci.TELEMETRY.get("log_dir"), ci.TELEMETRY.get("fail_dir")
        ci.BUDGET.used = 0

    def tearDown(self):
        ci.TELEMETRY["log_dir"], ci.TELEMETRY["fail_dir"] = self.log_dir, self.fail_dir
        (ci.codex_parallel_images, ci.run_judge, ci.finish_image, ci.codex_bin, ci.codex_version,
         ci.cmd_generate_or_edit, ci.CODEX_HOME, ci.LOCALE_FILE, ci.engine_codex) = self.saved
        ci._LOC.clear()
        ci.BUDGET.limit, ci.BUDGET.used = None, 0
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake(self, verdicts=lambda job: judge_result("PASS"), fail_ids=()):
        gen = Pipeline.fake_gen(self)

        def g(tasks, *a, **k):
            out = gen([t for t in tasks if not t["id"].startswith(tuple(fail_ids) or ("\0",))], *a, **k)
            for t in tasks:
                if fail_ids and t["id"].startswith(tuple(fail_ids)):
                    out["results"][t["id"]] = {"ok": False, "src": None, "ms": None, "err": "content policy"}
            return out
        ci.codex_parallel_images = g
        ci.run_judge = lambda img, brief, threshold=4, model=None, effort="high", timeout=420, checklist=None, \
            job=None, **k: verdicts(job)
        ci.codex_bin, ci.codex_version = (lambda: "codex"), (lambda b: "codex-cli test")
        ci.finish_image = lambda *a, **k: {"cast_before": 0, "cast_after": 0}

    def cli(self, *argv):
        old = sys.argv
        sys.argv = ["codex_image.py", *argv]
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                ci.main()
            return out.getvalue()
        finally:
            sys.argv = old

    def test_finish_error_keeps_the_judged_image(self):
        self.fake()

        def boom(*a, **k):
            raise ValueError("corrupt")
        ci.finish_image = boom
        rep = ci.fast_pipeline([{"name": "ok", "brief": "Intent: lifestyle photo\nSubject: one cook in a kitchen",
                                 "aspect": "3:2"}], args_ns(), self.tmp, self.tmp / "out")
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "PASS")
        self.assertTrue(Path(im["path"]).exists())
        self.assertIn("corrupt", json.loads(Path(im["meta"]).read_text())["finish"]["error"])

    def test_finish_runs_once_on_the_final_file_and_detects_warm_light(self):
        self.fake()
        calls = []
        ci.finish_image = lambda p, prof, dst=None, warm_scene=False, **k: calls.append(
            (Path(p).name, prof, warm_scene)) or {"cast_before": 0, "cast_after": 0}
        ci.fast_pipeline([{"name": "dinner", "aspect": "3:2", "brief": "Intent: lifestyle photo\nScene: a candle-lit "
                           "dinner table\nSubject: two friends talking"},
                          {"name": "icon", "aspect": "1:1", "brief": "Intent: app icon\nStyle: flat vector illustration "
                           "of a cup"}], args_ns(), self.tmp, self.tmp / "out")
        self.assertEqual(calls, [("dinner.png", "natural", True)])  # vector art gets no photographic finish

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_web_variants_declare_ai_only_for_generated_sources(self):
        gen = self.tmp / "gen.png"
        Image.new("RGBA", (300, 300), (10, 120, 90, 200)).save(gen, **ci.provenance_kwargs(gen))
        ci.web_export(gen, self.tmp / "web", widths=[160], formats=("png", "webp"))
        outs = [o for o in (self.tmp / "web").iterdir() if o.suffix in (".png", ".webp")]
        self.assertTrue(outs)
        for o in outs:
            self.assertIn(b"trainedAlgorithmicMedia", o.read_bytes(), o.name)
        client = self.tmp / "client.png"
        Image.new("RGB", (300, 300), (1, 2, 3)).save(client)
        ci.web_export(client, self.tmp / "web2", widths=[160], formats=("png",))
        self.assertFalse(any(b"trainedAlgorithmicMedia" in o.read_bytes() for o in (self.tmp / "web2").glob("*.png")))

    def test_batch_cli_precedence_style_opt_out_and_only(self):
        self.fake()
        jf = self.tmp / "jobs.json"
        jf.write_text(json.dumps({"locale": "Lagos, Nigeria", "look": "phone", "style": {"mood": "calm"}, "jobs": [
            {"name": "a", "aspect": "3:2", "brief": "Intent: card photo\nSubject: one cook at work"},
            {"name": "b", "aspect": "3:2", "look": "product", "style": False,
             "brief": "Intent: card photo\nSubject: one cook at work\nLocale: Oslo, Norway"}]}), encoding="utf-8")
        self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o1"), "--workdir", str(self.tmp))
        a = json.loads((self.tmp / "o1" / "a.meta.json").read_text())
        b = json.loads((self.tmp / "o1" / "b.meta.json").read_text())
        self.assertIn("Locale: Lagos, Nigeria", a["brief"])
        self.assertIn("calm", a["brief"])
        self.assertEqual(a["look"], "phone")
        self.assertIn("Oslo", b["brief"])
        self.assertNotIn("Lagos", b["brief"])
        self.assertNotIn("calm", b["brief"])
        self.assertEqual(b["look"], "product")
        self.cli("batch", "--jobs", str(jf), "--only", "b", "--out-dir", str(self.tmp / "o2"), "--workdir",
                 str(self.tmp))
        self.assertTrue((self.tmp / "o2" / "b.meta.json").exists())
        self.assertFalse((self.tmp / "o2" / "a.meta.json").exists())

    def test_batch_cli_rejects_bad_json_duplicates_and_unknown_only(self):
        self.fake()
        jf = self.tmp / "j.json"
        for content, extra in (("not json", ()),
                               (json.dumps([{"name": "a", "brief": "x"}, {"name": "a", "brief": "y"}]), ()),
                               (json.dumps([{"name": "a", "brief": "x"}]), ("--only", "zzz")),
                               (json.dumps([{"brief": "no name"}]), ())):
            jf.write_text(content, encoding="utf-8")
            with self.assertRaises(SystemExit):
                self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"), *extra)

    def test_generate_and_edit_cli_wiring(self):
        seen = []
        ci.cmd_generate_or_edit = lambda a: seen.append(vars(a).copy())
        self.cli("generate", "--prompt", "hi", "--look", "film", "--finish", "none", "--locale", "Tokyo, Japan")
        self.cli("edit", "--image", "x.png", "--prompt", "hi")
        self.assertEqual((seen[0]["look"], seen[0]["finish"], seen[0]["locale"], seen[0]["image"]),
                         ("film", "none", "Tokyo, Japan", None))
        self.assertEqual(seen[1]["image"], "x.png")
        for bad in (("--n", "9"), ("--look", "cinematic"), ("--finish", "sepia")):
            with self.assertRaises(SystemExit):
                self.cli("generate", "--prompt", "hi", *bad)

    def test_codex_output_recovery_from_generated_images(self):
        home = self.tmp / "codexhome"
        ci.CODEX_HOME = home
        gdir = home / "generated_images" / "abc_id"
        gdir.mkdir(parents=True)
        (gdir / "old.png").write_bytes(b"old")
        (gdir / "new.png").write_bytes(b"new")
        os.utime(gdir / "old.png", (1, 1))
        want = self.tmp / "out" / "want.png"
        found, missing = ci.collect_codex_outputs([want], {"report": {"images": []}, "res": {"thread_id": "abc/id"}},
                                                  self.tmp)
        self.assertEqual(missing, [])
        self.assertEqual(want.read_bytes(), b"new")
        self.assertEqual(found[0][1]["qa"]["issues"], ["recovered: no QA report"])
        _, missing = ci.collect_codex_outputs([self.tmp / "out" / "other.png"],
                                              {"report": {"images": []}, "res": {"thread_id": None}}, self.tmp)
        self.assertEqual(len(missing), 1)

    def test_budget_exhausted_during_fix_keeps_the_best_so_far(self):
        self.fake(verdicts=lambda job: judge_result("FAIL"))
        rep = ci.fast_pipeline([{"name": "one", "brief": "A green coconut on a cart.", "aspect": "3:2"}],
                               args_ns(max_images=1), self.tmp, self.tmp / "out")
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "FAIL")
        self.assertTrue(Path(im["path"]).exists())
        self.assertEqual(len(im["rounds"]), 1)

    def test_one_job_without_an_image_does_not_break_the_batch(self):
        self.fake(fail_ids=("nope",))
        rep = ci.fast_pipeline([{"name": "ok", "brief": "A green coconut on a cart.", "aspect": "3:2"},
                                {"name": "nope", "brief": "A red kite in a blue sky.", "aspect": "3:2"}],
                               args_ns(), self.tmp, self.tmp / "out")
        by = {i["name"]: i for i in rep["images"]}
        self.assertEqual(by["ok"]["verdict"], "PASS")
        self.assertIsNone(by["nope"].get("path"))
        self.assertTrue(by["nope"].get("error"))

    def test_missing_locales_file_degrades_to_no_places(self):
        ci._LOC.clear()
        ci.LOCALE_FILE = self.tmp / "missing.json"
        self.assertEqual(ci.find_places("Paris and Tokyo"), [])
        _, info = ci.place_context("Intent: photo\nScene: a street in Tokyo with taxis")
        self.assertIn(info["mode"], ("global", "none"))

    def test_detect_locale_schema_org_og_locale_and_ambiguity(self):
        d = self.tmp / "site"
        d.mkdir()
        (d / "index.html").write_text(
            '<html><head><meta property="og:locale" content="de_DE"><script type="application/ld+json">'
            '{"@type": "Dentist", "address": {"addressCountry": "DE", "addressLocality": "Munich"}}</script>'
            '</head></html>', encoding="utf-8")
        rep = ci.detect_locale(d)
        self.assertEqual(rep["country"], "DE")
        self.assertIn("Munich", rep["suggested"])
        self.assertTrue(any(s["kind"] == "schema" for s in rep["signals"]))
        amb = ci.detect_locale(None, "Offices in London (+44 20 7946 0000) and San Francisco (+1 415 555 0100)")
        self.assertTrue(amb["ambiguous"])
        self.assertIn("confirm", amb["note"])

    def test_lint_flags_hype_crowds_ethics_and_missing_aspect(self):
        self.assertTrue(any("AI look" in w for w in ci.lint_brief("An 8k hyperrealistic masterpiece of a cafe", "3:2")))
        self.assertTrue(any("crowds fail" in w for w in ci.lint_brief("A busy market with dozens of people", "3:2")))
        self.assertTrue(any(w.startswith("ethics") for w in
                            ci.lint_brief("A before and after smile makeover for a testimonial", "3:2")))
        self.assertTrue(any("no --aspect" in w for w in ci.lint_brief("A quiet beach at dawn", None)))

    def test_image_budget_clamps(self):
        b = ci.ImageBudget(5)
        self.assertEqual([b.take(3), b.take(3), b.take(1)], [3, 2, 0])
        self.assertEqual(ci.ImageBudget().take(7), 7)

    def test_report_lists_failures_with_a_rerun_command(self):
        rep = {"created": "t", "timing": {"total_s": 1, "slowest_job_s": 1, "median_job_s": 1}, "passed": 1,
               "first_pass": 1, "jobs_file": "/p/jobs.json", "out_dir": "/p/out",
               "images": [{"name": "good", "verdict": "PASS", "rounds": []},
                          {"name": "bad", "verdict": "FAIL", "rounds": [], "defects": ["readable menu text"],
                           "remaining_fix": "remove the menu board"}]}
        md = ci.fast_report_md(rep)
        self.assertIn("Next steps for failed images", md)
        self.assertIn("readable menu text", md)
        self.assertIn("--only bad", md)
        self.assertNotIn("--only good", md)

    def test_agent_mode_gets_the_compiled_layers_and_the_finish(self):
        self.fake()
        seen, finished = {}, []

        def fake_engine(args, brief, outputs, refs, target, workdir):
            seen["brief"] = brief
            outputs[0].parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.src, outputs[0])
            return {"res": {"ok": True, "thread_id": None}, "codex_version": "t", "effort": "low", "codex_model": "m",
                    "prompt": brief, "report": {"images": [{"output_path": str(outputs[0]), "source_path": "",
                                                            "final_prompt": "p", "attempts": 1, "qa": {"pass": True}}]}}
        ci.engine_codex = fake_engine
        ci.finish_image = lambda p, prof, dst=None, warm_scene=False, **k: finished.append((Path(p).name, prof)) or \
            {"cast_before": 0, "cast_after": 0}
        self.cli("generate", "--mode", "agent", "--prompt", "Intent: lifestyle photo\nSubject: one cook in a kitchen",
                 "--aspect", "3:2", "--name", "cook", "--workdir", str(self.tmp), "--out-dir", str(self.tmp / "o"))
        self.assertIn("Capture:", seen["brief"])
        self.assertEqual(finished, [("cook.png", "natural")])
        self.assertIn("finish", json.loads((self.tmp / "o" / "cook.meta.json").read_text()))

    def test_unsafe_names_and_unknown_aspects_are_rejected(self):
        for bad in ("../x", "/etc/cron.d/evil", "a/b", "", ".hidden", "a" * 120):
            with self.assertRaises(SystemExit):
                with contextlib.redirect_stderr(io.StringIO()):
                    ci.check_name(bad)
        self.assertEqual(ci.check_name("hero-v2_final.1"), "hero-v2_final.1")
        self.fake()
        jf = self.tmp / "j.json"
        for jobs in ([{"name": "../escape", "brief": "x"}], [{"name": "a", "brief": "x", "aspect": "16:10"}]):
            jf.write_text(json.dumps(jobs), encoding="utf-8")
            with self.assertRaises(SystemExit):
                self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"))
        self.assertFalse((self.tmp / "escape").exists())

    def test_batch_dry_run_generates_nothing(self):
        self.fake()
        calls = []
        ci.codex_parallel_images = lambda *a, **k: calls.append(1)
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps({"locale": "global", "jobs": [
            {"name": "a", "aspect": "3:2", "brief": "Intent: interior photo for a rental listing\nSubject: no people"},
            {"name": "b", "aspect": "1:1", "brief": "Intent: flat vector icon of a cup\nStyle: flat design"}]}))
        out = json.loads(self.cli("batch", "--jobs", str(jf), "--dry-run", "--out-dir", str(self.tmp / "o")))
        by = {r["name"]: r for r in out["jobs"]}
        self.assertEqual((by["a"]["look"], by["a"]["finish"]), ("interior", "clean"))
        self.assertEqual((by["b"]["look"], by["b"]["finish"]), ("-", "none"))
        self.assertIn("Capture:", Path(by["a"]["prompt"]).read_text(encoding="utf-8"))  # the prompt is in a file
        self.assertEqual(calls, [])

    def test_batch_dry_run_stays_small_and_names_the_prompt_files(self):
        self.fake()
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps({"style": {"palette": ["#0ea5e9"], "mood": "calm, honest, daylight"}, "jobs": [
            {"name": f"img{i}", "aspect": "3:2", "brief": "Intent: website photo for a family dental clinic\n"
             f"Scene: room {i}, a hygienist explains an X-ray to one patient\nCamera: eye level, 35mm\n"
             "Light: overcast window light mixing with ceiling LEDs\nConstraints: no readable text, no logos"}
            for i in range(10)]}), encoding="utf-8")
        text = self.cli("batch", "--jobs", str(jf), "--dry-run", "--out-dir", str(self.tmp / "o"))
        self.assertLess(len(text), 8000)  # was about 60 KB for ten jobs: every compiled prompt on stdout
        rows = json.loads(text)["jobs"]
        self.assertEqual(set(rows[0]), {"name", "lint", "risks", "place", "look", "finish", "checks", "prompt"})
        self.assertTrue(all(Path(r["prompt"]).read_text(encoding="utf-8").startswith("Format:") for r in rows))

    def test_leftover_marks_get_a_local_edit_not_a_model_limit(self):
        seq = {"n": 0}

        def verdicts(job):
            seq["n"] += 1
            if seq["n"] <= 2:  # both first candidates: a tiny logo on a shoe
                return judge_result("FAIL", {"text_exact": "FAIL"}, fix="remove the logo", mode="edit")
            return judge_result("PASS")
        self.fake(verdicts=verdicts)
        rep = ci.fast_pipeline([{"name": "run", "aspect": "3:2", "candidates": 2,
                                 "brief": "Intent: photo\nSubject: one runner on a track"}], args_ns(), self.tmp,
                               self.tmp / "out")
        im = rep["images"][0]
        self.assertIsNone(im.get("model_limit"))
        self.assertEqual(im["verdict"], "PASS")
        self.assertEqual([m for _, m, _, _ in im["rounds"]][-1], "edit")

    def test_one_bonus_edit_after_the_configured_rounds(self):
        seq = {"n": 0}

        def verdicts(job):
            seq["n"] += 1
            if seq["n"] == 1:
                return judge_result("FAIL", {"physics": "FAIL"}, fix="fix the pour", mode="regenerate")
            if seq["n"] == 2:
                return judge_result("FAIL", {"no_unrequested_elements": "FAIL"}, fix="remove the mark", mode="edit")
            return judge_result("PASS")
        self.fake(verdicts=verdicts)
        rep = ci.fast_pipeline([{"name": "cup", "aspect": "3:2", "candidates": 1,
                                 "brief": "Intent: photo\nSubject: one cup of tea on a table"}],
                               args_ns(fix_rounds=1), self.tmp, self.tmp / "out")
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "PASS")
        self.assertEqual([m for _, m, _, _ in im["rounds"]], ["initial", "regenerate", "edit"])

    def test_style_lock_medium_prop_phones_and_candidate_cost(self):
        lock = ci.style_block({"style": "flat vector illustration, soft pastel palette"})
        self.assertTrue(ci.is_non_photo("Intent: service card image\nSubject: a tooth\n" + lock))
        self.assertEqual(ci.pick_look("Intent: website photo of a home office\nScene: a smartphone face down on "
                                      "the desk")[0], "editorial")
        look, cap = ci.pick_look("Intent: UGC selfie for a review\nCamera: 50mm lens feel")
        self.assertEqual(look, "phone")
        self.assertIn("24mm", cap)  # a phone has no 50mm prime; the brief's focal length is not forced onto it
        j = {"brief": "Intent: lifestyle photo\nScene: a kitchen\nSubject: one man cooking dinner for his family"}
        j["prompt"], j["hints"] = ci.compile_prompt(j["brief"], "3:2")
        j["n_checks"] = len(ci.failure_hints(ci.place_context(j["brief"])[0]))
        j["risks"] = []
        self.assertEqual(ci._job_candidates(j, args_ns()), 1)  # place/realism checks do not double the cost

    def test_edit_prompts_keep_the_frame(self):
        prompt, _ = ci.compile_prompt("Intent: edit\nSubject: change only the mug colour to blue", "3:2", edit=True)
        self.assertNotIn("Capture:", prompt)
        self.assertIn("keep the framing, composition", prompt)
        self.assertNotIn("subject a little off centre", prompt)

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_audit_counts_srcset_and_skips_generated_masters(self):
        site = self.tmp / "site"
        (site / "img").mkdir(parents=True)
        for n in ("hero-480.webp", "hero-768.webp", "hero-480.jpg"):
            Image.new("RGB", (40, 30), (1, 2, 3)).save(site / "img" / n)
        (site / "gen").mkdir()
        Image.new("RGB", (40, 30)).save(site / "gen" / "hero.png")
        (site / "gen" / "hero.meta.json").write_text("{}")
        Image.new("RGB", (40, 30)).save(site / "gen" / "hero-c1.png")
        (site / "index.html").write_text('<picture><source type="image/webp" srcset="img/hero-480.webp 480w, '
                                         'img/hero-768.webp 768w"><img src="img/hero-480.jpg" alt="Hero" width="40" '
                                         'height="30"></picture>', encoding="utf-8")
        rep = ci.audit_site(site)
        self.assertEqual(rep["issue_counts"].get("unreferenced", 0), 0)
        self.assertEqual(rep["images"], 3)  # the generated master and its candidate are not site images

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_manifest_has_no_local_paths_and_derivatives_stay_tagged(self):
        gen = self.tmp / "gen.png"
        Image.new("RGB", (600, 400), (90, 120, 150)).save(gen, **ci.provenance_kwargs(gen))
        out = self.tmp / "public" / "images"
        e = ci.web_export(gen, out, widths=[480], formats=("webp",))
        ci.update_manifest(out, [e])
        text = (out / "assets.json").read_text()
        self.assertNotIn(str(self.tmp), text)
        self.assertNotIn("/private/", text)
        e2 = ci.web_export(gen, out, widths=[480], formats=("webp",), name="custom", url_prefix="/img")
        ci.update_manifest(out, [e2])
        self.assertIn('"url": "/img/custom-480.webp"', (out / "assets.json").read_text())  # URLs stay intact
        ci.fit_to_size(gen, 300, 300)
        self.assertIn(b"trainedAlgorithmicMedia", gen.read_bytes())
        legacy = {"name": "old", "source": "/abs/old.png", "variants": [{"path": str(out / "old-480.webp"), "url": "/images/old-480.webp"}]}
        (out / "assets.json").write_text(json.dumps({"old": legacy}))
        ci.update_manifest(out, [])  # entries written by an older version are cleaned too
        self.assertNotIn(str(self.tmp), (out / "assets.json").read_text())
        alpha = self.tmp / "alpha.png"
        im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        im.paste((200, 50, 50, 252), (50, 50, 150, 150))
        im.save(alpha, **ci.provenance_kwargs(alpha))
        ci.refine_alpha(alpha)
        self.assertIn(b"trainedAlgorithmicMedia", alpha.read_bytes())  # refined transparent assets stay declared
        dark = self.tmp / "dark.png"
        Image.new("RGB", (200, 150), (0, 0, 0)).save(dark)
        self.assertEqual(ci.midtone_cast(Image.open(dark)), 0.0)
        ci.finish_image(dark, "natural")  # an all-dark frame no longer breaks the finish

    def test_agent_mode_transparent_and_style_lock(self):
        self.fake()
        seen, refined = {}, []

        def fake_engine(args, brief, outputs, refs, target, workdir):
            seen["brief"] = brief
            outputs[0].parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.src, outputs[0])
            return {"res": {"ok": True, "thread_id": None}, "codex_version": "t", "effort": "low", "codex_model": "m",
                    "prompt": brief, "report": {"images": [{"output_path": str(outputs[0]), "source_path": "",
                                                            "final_prompt": "p", "attempts": 1, "qa": {"pass": True}}]}}
        ci.engine_codex = fake_engine
        saved = ci.refine_alpha
        ci.refine_alpha = lambda p: refined.append(Path(p).name)
        try:
            self.cli("generate", "--mode", "agent", "--transparent", "--style", "calm, pastel", "--prompt",
                     "Intent: spot illustration of a tooth\nStyle: soft clay 3D", "--aspect", "1:1", "--name", "tooth",
                     "--workdir", str(self.tmp), "--out-dir", str(self.tmp / "o"))
        finally:
            ci.refine_alpha = saved
        self.assertIn("transparent background", seen["brief"])
        self.assertIn("Style lock", seen["brief"])
        self.assertEqual(refined, ["tooth.png"])

    def test_style_lock_does_not_trigger_lint_and_possessives_are_not_people(self):
        lock = ci.style_block({"palette": ["#0E7490 teal"], "people": "busy with the task", "avoid": "text or logos"})
        self.assertEqual(ci.lint_brief("Intent: interior photo\nScene: a reception\nSubject: no people\n" + lock, "16:9"),
                         [])
        brief = ("Intent: interior photo of the clinic reception\nScene: a desk with a cardigan over the receptionist's "
                 "chair\nSubject: no people")
        self.assertFalse(ci.has_people(brief))
        self.assertEqual(ci.pick_look(brief)[0], "interior")
        self.assertTrue(ci.has_people("Intent: photo\nSubject: one receptionist answering the phone"))

    def test_cmd_locale_needs_input(self):
        with self.assertRaises(SystemExit):
            with contextlib.redirect_stderr(io.StringIO()):
                ci.cmd_locale(argparse.Namespace(root=None, text=None, out=None))

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_sidecar_declares_outputs_that_lost_their_metadata(self):
        gen = self.tmp / "gen"
        gen.mkdir()
        spot = gen / "spot.png"
        im = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
        im.paste((40, 120, 90, 255), (30, 30, 90, 90))
        im.save(spot)  # an older refine re-saved it without the C2PA manifest or the IPTC tag
        client = gen / "spot.jpg"
        Image.new("RGB", (120, 120), (90, 80, 70)).save(client)
        self.assertFalse(ci.ai_source(spot))
        (gen / "spot.meta.json").write_text(json.dumps({"output_path": str(spot)}), encoding="utf-8")
        self.assertTrue(ci.ai_source(spot))
        self.assertFalse(ci.ai_source(client))  # same stem, but the sidecar names another file
        e = ci.web_export(spot, self.tmp / "public", widths=[64], formats=("webp", "jpg"))
        self.assertEqual(sorted(v["format"] for v in e["variants"]), ["png", "webp"])
        for v in e["variants"]:
            self.assertIn(b"trainedAlgorithmicMedia", (self.tmp / "public" / Path(v["path"]).name).read_bytes())
        for name in ("spot-raw.png", "spot-c2.png", "spot-fix1.png", "spot-regen1-v2.png", "spot-v3.png"):
            self.assertTrue(ci.is_generated_file(gen / name), name)
        self.assertFalse(ci.is_generated_file(gen / "team-v2.png"))

    def test_missing_pillow_stops_image_commands_but_not_the_audit(self):
        site = self.tmp / "site"
        site.mkdir()
        shutil.copy2(self.src, site / "hero.png")
        (site / "index.html").write_text('<img src="hero.png" alt="Hero">', encoding="utf-8")
        with mock.patch.dict(sys.modules, {"PIL": None}), mock.patch.object(ci, "VENV_DIR", self.tmp / "no-venv"), \
                contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                ci.need_pillow()
            rep = ci.audit_site(site)  # the inventory still works, without pixel sizes
        self.assertEqual(rep["images"], 1)

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_finish_and_audit_cli_wrappers(self):
        photo = self.tmp / "photo.png"
        Image.new("RGB", (320, 240), (150, 120, 100)).save(photo)
        before = photo.read_bytes()
        res = json.loads(self.cli("finish", "--src", str(photo), "--profile", "phone", "--out-dir",
                                  str(self.tmp / "fin")))
        self.assertEqual(photo.read_bytes(), before)  # --out-dir leaves the original alone
        done = Path(res[0]["path"])
        self.assertEqual(done.parent.name, "fin")
        self.assertNotIn(b"trainedAlgorithmicMedia", done.read_bytes())  # a client photo is never declared as AI
        with self.assertRaises(SystemExit):
            self.cli("finish", "--src", str(self.tmp / "missing.png"))
        site = self.tmp / "site"
        site.mkdir()
        shutil.copy2(photo, site / "team.png")
        (site / "index.html").write_text('<img src="team.png">', encoding="utf-8")
        brief = json.loads(self.cli("audit", "--root", str(site), "--out", str(self.tmp / "audit.json")))
        self.assertEqual(brief["images"], 1)
        self.assertIn("missing-alt", brief["issue_counts"])
        self.assertIn("inventory", json.loads((self.tmp / "audit.json").read_text(encoding="utf-8")))

    def test_doctor_without_codex_and_the_readiness_rule(self):
        ns = argparse.Namespace(setup=False, smoke=False, image_smoke=False)
        ci.codex_bin = lambda: ci.die("codex CLI not found")
        out = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            ci.cmd_doctor(ns)
        self.assertEqual(json.loads(out.getvalue())["codex"], "NOT FOUND")
        ci.codex_bin, ci.codex_version = (lambda: "codex"), (lambda b: "codex-cli test")
        for login, ready in (("Logged in using ChatGPT", True), ("Not logged in", False)):
            def fake_run(cmd, *a, _login=login, **k):
                text = {"login": _login, "features": "image_generation  stable  true"}.get(
                    cmd[1] if len(cmd) > 1 else "", "")
                return subprocess.CompletedProcess(cmd, 0, text, "")
            out = io.StringIO()
            with mock.patch.object(ci.subprocess, "run", fake_run), contextlib.redirect_stdout(out):
                ci.cmd_doctor(ns)
            rep = json.loads(out.getvalue())
            self.assertIs(rep["ready_for_codex_engine"], ready)
            self.assertEqual(rep["skill_version"], ci.SKILL_VERSION)

    def test_output_planning_and_reference_roles(self):
        out = self.tmp / "o"
        out.mkdir()
        (out / "cup-1.png").write_bytes(b"x")
        planned = ci.plan_outputs(argparse.Namespace(n=3, out=None, out_dir=str(out), name="cup"), "a cup", self.tmp)
        self.assertEqual([p.name for p in planned], ["cup-1-v2.png", "cup-2.png", "cup-3.png"])  # never overwrites
        self.assertEqual((out / "cup-1.png").read_bytes(), b"x")
        one = ci.plan_outputs(argparse.Namespace(n=1, out="art/hero.jpg", out_dir=None, name=None), "b", self.tmp)
        self.assertEqual(one, [self.tmp / "art" / "hero.png"])
        refs = ci.parse_refs([f"{self.src}=style reference", str(self.src)])
        self.assertEqual([role for _, role in refs], ["style reference", "reference"])
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            ci.parse_refs([str(self.tmp / "missing.png")])

    def test_api_engine_dry_run_uses_the_compiled_prompt(self):
        ns = argparse.Namespace(tier="draft", model="auto", quality=None, api_size=None, aspect="3:2",
                                raw_prompt=False, mask=None, dry_run=True)
        brief = "Intent: website hero photo for a bakery\nSubject: exactly one baker shaping dough"

        def run(**kw):
            for k, v in kw.items():
                setattr(ns, k, v)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertIsNone(ci.engine_api(ns, brief, [self.tmp / "a.png"], [], None, self.tmp))
            return json.loads(out.getvalue())
        rep = run()
        self.assertEqual(rep["endpoint"], "images/generations")
        self.assertEqual(rep["model_chain"], ["gpt-image-2.5-flare", "gpt-image-2"])
        self.assertEqual(rep["payload"]["size"], ci.ASPECTS["3:2"][1])
        self.assertIn("exactly one baker shaping dough", rep["payload"]["prompt"])
        self.assertNotEqual(rep["payload"]["prompt"], brief)  # place, look and realism layers are added
        self.assertEqual(run(raw_prompt=True)["payload"]["prompt"], brief)
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            run(api_size="1000x1000")  # not a multiple of 16

    def test_bad_size_refs_candidates_and_style_stop_before_any_session(self):
        self.fake()
        calls = []
        ci.codex_parallel_images = lambda *a, **k: calls.append(1)
        jf = self.tmp / "j.json"
        for i in range(6):
            shutil.copy2(self.src, self.tmp / f"r{i}.png")
        base = {"name": "a", "aspect": "1:1", "brief": "Intent: product photo\nSubject: one mug"}
        for bad in ({"size": "1200 x 630"}, {"size": "1920X1080"}, {"candidates": "two"}, {"candidates": 9},
                    {"refs": ["missing.png"]}, {"target": "missing.png"},
                    {"refs": [f"r{i}.png" for i in range(6)]}):  # the image tool takes at most 5 inputs
            jf.write_text(json.dumps([dict(base, **bad)]), encoding="utf-8")
            with self.assertRaises(SystemExit, msg=str(bad)):
                self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"), "--workdir", str(self.tmp))
        jf.write_text(json.dumps({"style": "brand/style.json", "jobs": [base]}), encoding="utf-8")
        with self.assertRaises(SystemExit):  # a style file that is missing is not used as the style text
            self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"), "--workdir", str(self.tmp))
        for bad in (("--size", "1920X1080"), ("--candidates", "7"), ("--style", "brand/missing.json")):
            with self.assertRaises(SystemExit):
                self.cli("generate", "--prompt", "Intent: product photo\nSubject: one mug", "--aspect", "1:1",
                         "--out-dir", str(self.tmp / "g"), "--workdir", str(self.tmp), *bad)
        self.assertEqual(calls, [])  # nothing reached Codex
        jf.write_text(json.dumps([dict(base, refs=["r0.png"], size="1200x630", candidates=2)]), encoding="utf-8")
        self.fake()
        self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "ok"), "--workdir", str(self.tmp))
        self.assertTrue((self.tmp / "ok" / "a.meta.json").exists())  # good values still run

    def test_each_job_writes_its_meta_and_a_progress_line_as_it_ends(self):
        self.fake()
        out, seen = self.tmp / "out", {}
        gen = ci.codex_parallel_images

        def slow_gen(tasks, *a, **k):
            if tasks[0]["id"].startswith("slow"):  # wait until the quick job is done, then look at the disk
                t0 = time.time()
                while not (out / "quick.meta.json").exists() and time.time() - t0 < 5:
                    time.sleep(0.02)
                seen["meta"] = (out / "quick.meta.json").exists()
                seen["progress"] = (out / "progress.jsonl").read_text(encoding="utf-8")
            return gen(tasks, *a, **k)
        ci.codex_parallel_images = slow_gen
        ci.fast_pipeline([{"name": "quick", "aspect": "1:1", "brief": "Intent: product photo\nSubject: one mug"},
                          {"name": "slow", "aspect": "1:1", "brief": "Intent: product photo\nSubject: one jar"}],
                         args_ns(), self.tmp, out, progress=out / "progress.jsonl")
        self.assertTrue(seen["meta"])  # written while the other job was still running
        self.assertEqual(json.loads(seen["progress"].splitlines()[0])["name"], "quick")
        lines = [json.loads(l) for l in (out / "progress.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(l["name"], l["verdict"]) for l in lines], [("quick", "PASS"), ("slow", "PASS")])

    def test_report_is_written_when_the_run_is_cut_short(self):
        self.fake()
        real = ci.job_pipeline
        out = self.tmp / "o"

        def jp(j, *a):
            if j["name"] == "b":  # the run is interrupted after job a has finished
                t0 = time.time()
                while not (out / "a.meta.json").exists() and time.time() - t0 < 5:
                    time.sleep(0.02)
                raise KeyboardInterrupt
            return real(j, *a)
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps([{"name": n, "aspect": "1:1", "brief": f"Intent: product photo\nSubject: one {n}"}
                                  for n in ("a", "b")]), encoding="utf-8")
        with mock.patch.object(ci, "job_pipeline", jp), self.assertRaises(KeyboardInterrupt):
            self.cli("batch", "--jobs", str(jf), "--out-dir", str(out))
        rep = json.loads((out / "batch-report.json").read_text(encoding="utf-8"))
        self.assertEqual([i["name"] for i in rep["images"]], ["a"])
        self.assertEqual(rep["unfinished"], ["b"])
        self.assertIn('"a"', (out / "batch-progress.jsonl").read_text(encoding="utf-8"))

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_one_export_error_keeps_the_other_exports_and_the_report(self):
        self.fake()
        real = ci.web_export

        def flaky(src, *a, **k):
            if Path(src).stem == "b":
                raise OSError("encoder error")
            return real(src, *a, **k)
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps([{"name": n, "aspect": "1:1", "brief": f"Intent: product photo\nSubject: one {n}"}
                                  for n in ("a", "b")]), encoding="utf-8")
        with mock.patch.object(ci, "web_export", flaky):
            out = json.loads(self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"), "--export-dir",
                                      str(self.tmp / "web")))
        self.assertEqual(out["export_errors"], ["b"])
        self.assertIn("a", json.loads((self.tmp / "web" / "assets.json").read_text(encoding="utf-8")))
        rep = json.loads((self.tmp / "o" / "batch-report.json").read_text(encoding="utf-8"))
        self.assertIn("encoder error", {i["name"]: i for i in rep["images"]}["b"]["export_error"])

    def test_resume_keeps_passed_jobs_and_runs_only_the_rest(self):
        self.fake(verdicts=lambda job: judge_result("FAIL") if str(job).startswith("b") else judge_result("PASS"))
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps([{"name": n, "aspect": "1:1", "brief": f"Intent: product photo\nSubject: one {n}"}
                                  for n in ("a", "b")]), encoding="utf-8")
        out = self.tmp / "o"
        self.cli("batch", "--jobs", str(jf), "--out-dir", str(out))
        calls = []
        gen = ci.codex_parallel_images
        ci.codex_parallel_images = lambda tasks, *a, **k: calls.append(tasks[0]["id"]) or gen(tasks, *a, **k)
        res = json.loads(self.cli("batch", "--jobs", str(jf), "--out-dir", str(out), "--resume"))
        self.assertTrue(calls and all(c.startswith("b") for c in calls))  # a passed before: it is not made again
        self.assertFalse((out / "a-v2.png").exists())
        self.assertEqual([n for n, _ in res["images"]][0], "a.png")
        rep = json.loads((out / "batch-report.json").read_text(encoding="utf-8"))
        self.assertTrue({i["name"]: i for i in rep["images"]}["a"]["resumed"])
        with self.assertRaises(SystemExit):  # resume needs the folder of the run it continues
            self.cli("batch", "--jobs", str(jf), "--resume")

    @unittest.skipUnless(HAVE_PIL, "Pillow not available (run doctor --setup)")
    def test_rejudge_judges_the_existing_image_again_and_exports_on_pass(self):
        self.fake(verdicts=lambda job: {"computed_verdict": "ERROR", "error": "judge timed out after 150s"}
                  if str(job).startswith("cup") else judge_result("PASS"))
        jf = self.tmp / "j.json"
        jf.write_text(json.dumps({"style": {"mood": "calm"}, "jobs": [
            {"name": n, "aspect": "1:1", "brief": f"Intent: product photo\nSubject: one {n} on a table"}
            for n in ("cup", "mug")]}), encoding="utf-8")
        out, web = self.tmp / "o", self.tmp / "web"
        self.cli("batch", "--jobs", str(jf), "--out-dir", str(out), "--export-dir", str(web))
        md = (out / "batch-report.md").read_text(encoding="utf-8")
        self.assertIn("### ERROR: the judge failed, not the image", md)
        self.assertIn(f'--only cup --out-dir "{out}" --rejudge', md)
        self.assertNotIn("cup", json.loads((web / "assets.json").read_text(encoding="utf-8")))  # unjudged: not exported
        calls, seen = [], {}
        ci.codex_parallel_images = lambda *a, **k: calls.append(1)

        def judge(img, brief, threshold=4, model=None, effort="high", timeout=0, checklist=None, job=None, **k):
            seen.update(brief=brief, checklist=checklist, effort=effort)
            return judge_result("PASS")
        ci.run_judge = judge
        res = json.loads(self.cli("batch", "--jobs", str(jf), "--only", "cup", "--rejudge", "--out-dir", str(out),
                                  "--export-dir", str(web)))
        self.assertEqual(calls, [])  # no new image
        self.assertEqual(res["images"], [["cup.png", "PASS"]])
        meta = json.loads((out / "cup.meta.json").read_text(encoding="utf-8"))
        self.assertEqual((meta["judge"]["computed_verdict"], meta["rounds"][-1]["mode"]), ("PASS", "rejudge"))
        self.assertEqual((seen["brief"], seen["checklist"]), (meta["brief"], meta["prompt_time_checks"]))
        self.assertIn("calm", seen["brief"])  # the same brief the first judge saw, style lock included
        self.assertEqual(seen["effort"], "medium")
        self.assertIn("cup", json.loads((web / "assets.json").read_text(encoding="utf-8")))  # exported on pass

    def test_judge_command_checks_paths_first_runs_at_once_and_prints_every_result(self):
        imgs = []
        for n in ("a", "b", "c"):
            p = self.tmp / f"{n}.png"
            shutil.copy2(self.src, p)
            imgs += ["--image", str(p)]
        seen = []

        def judge(img, brief, threshold=4, model=None, effort="high", timeout=0, checklist=None, job=None, **k):
            seen.append((effort, timeout))
            time.sleep(0.4)
            if Path(img).stem == "b":
                raise RuntimeError("judge crashed")
            return judge_result("PASS")
        ci.run_judge = judge
        t0 = time.time()
        out = json.loads(self.cli("judge", *imgs, "--prompt", "a cup on a table", "--timeout", "90"))
        self.assertLess(time.time() - t0, 1.0)  # three judges at once, not one after another
        self.assertEqual([r["computed_verdict"] for r in out], ["PASS", "ERROR", "PASS"])  # every result printed
        self.assertEqual(set(seen), {("medium", 90)})
        seen.clear()
        with self.assertRaises(SystemExit):
            self.cli("judge", *imgs, "--image", str(self.tmp / "typo.png"), "--prompt", "a cup")
        self.assertEqual(seen, [])  # a bad path stops the command before any judge runs

    def test_report_tells_a_judge_error_from_a_rejected_image(self):
        rep = {"created": "t", "timing": {"total_s": 9}, "passed": 0, "first_pass": 0, "jobs_file": "/p/jobs.json",
               "out_dir": "/p/out",
               "images": [{"name": "bad", "path": "/p/out/bad.png", "verdict": "FAIL", "defects": ["a stray logo"]},
                          {"name": "cup", "path": "/p/out/cup.png", "verdict": "ERROR",
                           "judge_error": "judge timed out after 150s"},
                          {"name": "gone", "path": None, "error": "timed out after 480s (events: /p/out/logs/x)"},
                          {"name": "ok", "path": "/p/out/ok.png", "verdict": "PASS", "export_error": "OSError: disk"}]}
        md = ci.fast_report_md(rep)
        fail, err = md.split("### FAIL")[1].split("###")[0], md.split("### ERROR")[1].split("###")[0]
        self.assertIn("--only bad ", fail)
        self.assertNotIn("--rejudge", fail)  # rejected: make a new image
        self.assertIn('--only cup --out-dir "/p/out" --rejudge', err)  # unjudged: judge again, no new image
        self.assertIn("not judged (judge timed out after 150s)", err)
        self.assertIn("### No image", md)
        self.assertIn("events: /p/out/logs/x", md)
        self.assertIn("**ok**: OSError: disk", md)

    def test_jobs_file_paths_resolve_next_to_the_jobs_file_and_a_job_style_wins(self):
        self.fake()
        seen = {}
        gen = ci.codex_parallel_images
        ci.codex_parallel_images = lambda tasks, *a, **k: seen.update({tasks[0]["id"]: tasks[0].get("refs")}) or \
            gen(tasks, *a, **k)
        site = self.tmp / "site"
        (site / "brand").mkdir(parents=True)
        shutil.copy2(self.src, site / "brand" / "logo.png")
        (site / "brand" / "style.json").write_text(json.dumps({"mood": "calm clinic daylight"}), encoding="utf-8")
        (site / "brand" / "alt.txt").write_text("Watercolour illustration, loose ink lines.", encoding="utf-8")
        jf = site / "brand" / "jobs.json"
        for style in ("style.json", "brand/style.json"):  # next to the jobs file, or from the project root
            jf.write_text(json.dumps({"style": style, "jobs": [
                {"name": "a", "aspect": "1:1", "refs": ["logo.png"], "brief": "Intent: product photo\nSubject: one mug"},
                {"name": "b", "aspect": "1:1", "style": "alt.txt", "brief": "Intent: spot illustration of a mug"},
                {"name": "c", "aspect": "1:1", "style": False, "brief": "Intent: product photo\nSubject: one jar"}]}),
                encoding="utf-8")
            out = self.tmp / f"o-{style.replace('/', '-')}"
            self.cli("batch", "--jobs", str(jf), "--out-dir", str(out), "--workdir", str(site))
            brief = {n: json.loads((out / f"{n}.meta.json").read_text(encoding="utf-8"))["brief"] for n in "abc"}
            self.assertIn("calm clinic daylight", brief["a"])
            self.assertIn("Watercolour", brief["b"])  # the job's own style replaces the shared one
            self.assertNotIn("calm clinic daylight", brief["b"])
            self.assertNotIn("Style lock", brief["c"])
            self.assertEqual(seen["a-c1"], [str((site / "brand" / "logo.png").resolve())])

    def test_empty_and_file_name_briefs_are_caught(self):
        (self.tmp / "empty.txt").write_text("  \n", encoding="utf-8")
        ns = lambda **kw: argparse.Namespace(**dict({"prompt": None, "prompt_file": None}, **kw))
        for bad in (ns(prompt_file=str(self.tmp / "empty.txt")), ns(prompt_file=str(self.tmp / "missing.txt")),
                    ns(prompt_file="Intent: a mug on a table. Subject: one mug."), ns(prompt="   ")):
            with self.assertRaises(SystemExit, msg=str(bad)):
                ci.read_brief(bad)
        with mock.patch.object(sys, "stdin", io.StringIO("")), self.assertRaises(SystemExit):
            ci.read_brief(ns(prompt_file="-"))  # a lost heredoc no longer starts a generation
        logs = []
        with mock.patch.object(ci, "log", logs.append):
            self.assertEqual(ci.read_brief(ns(prompt="brief.txt")), "brief.txt")
            self.assertEqual(ci.read_brief(ns(prompt="Intent: product photo\nSubject: one mug")),
                             "Intent: product photo\nSubject: one mug")
        self.assertEqual(len(logs), 1)
        self.assertIn("--prompt-file", logs[0])  # the warning says how to read a file
        self.fake()
        jf = self.tmp / "j.json"
        for brief in ("   ", ["Intent: a list", "is not text"]):
            jf.write_text(json.dumps([{"name": "a", "brief": brief}]), encoding="utf-8")
            with self.assertRaises(SystemExit):
                self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "o"))

    def test_missing_files_and_bad_values_give_one_line_errors(self):
        logs = []
        runs = (("audit", "--root", str(self.tmp / "no-such-site")),
                ("og", "--bg", str(self.tmp / "missing.png"), "--title", "Hi", "--out", str(self.tmp / "og.png")),
                ("favicon", "--src", str(self.tmp / "missing.png"), "--out", str(self.tmp / "pub")),
                ("cutout", "--src", str(self.tmp / "missing.png")),
                ("export", "--src", str(self.src), "--out", str(self.tmp / "w"), "--widths", "480px"),
                ("export", "--src", str(self.src), "--out", str(self.tmp / "w"), "--alt-json", str(self.tmp / "no.json")))
        with mock.patch.object(ci, "log", logs.append):
            for argv in runs:
                logs.clear()
                with self.assertRaises(SystemExit, msg=argv[0]):  # not a traceback
                    self.cli(*argv)
                self.assertEqual(len(logs), 1, argv)
                self.assertTrue(logs[0].startswith("ERROR: ") and "\n" not in logs[0], logs[0])


class SpeedAndReliability(unittest.TestCase):
    """Early results from the rollout, overlapping judges, judge retry, stop signals, atomic writes, API retry."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (ci.CODEX_HOME, ci.codex_bin, ci.run_judge, ci.codex_parallel_images, ci.JUDGE_RETRY_WAIT,
                      ci.run_group, ci.api_call, ci.get_api_key)
        ci.BUDGET.used = 0

    def tearDown(self):
        (ci.CODEX_HOME, ci.codex_bin, ci.run_judge, ci.codex_parallel_images, ci.JUDGE_RETRY_WAIT, ci.run_group,
         ci.api_call, ci.get_api_key) = self.saved
        ci._LIVE["stop"] = False
        ci.BUDGET.limit, ci.BUDGET.used = None, 0
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_codex(self, body: str) -> str:
        p = self.tmp / "codex"
        p.write_text("#!/bin/sh\n" + body, encoding="utf-8")
        p.chmod(0o755)
        return str(p)

    def test_batch_result_is_taken_from_the_rollout_without_waiting_for_the_reply(self):
        """The agent's closing echo of the JSON line (5.5 s median in real sessions) is not waited for."""
        home = self.tmp / "home"
        ci.CODEX_HOME = home
        day = home / "sessions" / "2026" / "09" / "24"
        day.mkdir(parents=True)
        img = self.tmp / "gen.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        line = json.dumps({"total_ms": 5, "results": [{"ok": True, "id": "job-c1", "ms": 5, "path": str(img)}]})
        rollout = {"type": "response_item", "payload": {"type": "custom_tool_call_output", "output": [
            {"type": "input_text", "text": "Script completed"}, {"type": "input_text", "text": line}]}}
        (self.tmp / "rollout-line.json").write_text(json.dumps(rollout), encoding="utf-8")
        ci.codex_bin = lambda: self.fake_codex(
            'echo \'{"type": "thread.started", "thread_id": "tid-1"}\'\n'
            f'cat "{self.tmp / "rollout-line.json"}" > "{day}/rollout-2026-09-24T00-00-00-tid-1.jsonl"\n'
            f'echo >> "{day}/rollout-2026-09-24T00-00-00-tid-1.jsonl"\n'
            'sleep 30\n')  # the agent would now spend seconds repeating the JSON line
        t0 = time.time()
        res = ci.codex_parallel_images([{"id": "job-c1", "prompt": "p"}], self.tmp, "low", 60)
        self.assertLess(time.time() - t0, 10)
        self.assertTrue(res["results"]["job-c1"]["ok"])
        self.assertEqual(ci._LIVE["procs"], set())  # the session's process group is gone

    def test_stop_ends_running_sessions_and_refuses_new_ones(self):
        out = {}
        th = threading.Thread(target=lambda: out.update(ci.run_group(["/bin/sh", "-c", "sleep 30 & sleep 30"], "",
                                                                     60, self.tmp)))
        th.start()
        time.sleep(0.5)
        t0 = time.time()
        self.assertEqual(ci.kill_live_sessions(), 1)
        th.join(10)
        self.assertLess(time.time() - t0, 5)
        self.assertEqual(out["error"], "stopped")
        self.assertEqual(ci.run_group(["/bin/sh", "-c", "sleep 30"], "", 60, self.tmp)["error"], "stopped")

    def test_judge_gets_one_more_session_after_an_error(self):
        calls = []

        def fake_run_group(cmd, prompt, timeout, tmp, cancel=None, ready=None, env=None):
            calls.append(1)
            if len(calls) == 2:  # the retry answers; the first session died without an answer
                Path(cmd[cmd.index("-o") + 1]).write_text(json.dumps({
                    "gates": {g: "PASS" for g in ("instruction_following", "text_exact", "physics", "hand_object",
                                                  "anatomy", "no_unrequested_elements")},
                    "scores": {"realism": 5, "artifacts": 5, "physics_plausibility": 5, "composition": 5,
                               "brief_fidelity": 5}, "defects": []}))
            return {"stdout": "stream disconnected" if len(calls) == 1 else "", "stderr": "", "returncode": 0,
                    "error": None, "early": None}
        ci.run_group, ci.JUDGE_RETRY_WAIT = fake_run_group, 0
        ci.codex_bin = lambda: "codex"
        j = ci.run_judge(self.tmp / "x.png", "a cup")
        self.assertEqual((j["computed_verdict"], len(calls)), ("PASS", 2))
        rep = {"created": "t", "timing": {"total_s": 1}, "passed": 0, "first_pass": 0,
               "images": [{"name": "cup", "verdict": "ERROR", "rounds": [], "judge_error": "judge timed out"}]}
        self.assertIn("not judged (judge timed out)", ci.fast_report_md(rep))  # an unjudged image is listed

    def test_the_judge_starts_in_its_own_empty_folder(self):
        """2026-09-25: a judge that started in the project folder read the files there (a design's HTML, notes)."""
        seen = {}

        def fake_run_group(cmd, prompt, timeout, tmp, cancel=None, ready=None, env=None):
            seen.update(cmd=cmd, prompt=prompt, tmp=tmp)
            Path(cmd[cmd.index("-o") + 1]).write_text(json.dumps({
                "gates": {g: "PASS" for g in ("instruction_following", "text_exact", "physics", "hand_object",
                                              "anatomy", "no_unrequested_elements")},
                "scores": {"realism": 5, "artifacts": 5, "physics_plausibility": 5, "composition": 5,
                           "brief_fidelity": 5}, "defects": []}))
            return {"stdout": "", "stderr": "", "returncode": 0, "error": None, "early": None}
        ci.run_group, ci.JUDGE_RETRY_WAIT = fake_run_group, 0
        ci.codex_bin = lambda: "codex"
        ci.run_judge(self.tmp / "x.png", "a cup")
        self.assertEqual(Path(seen["cmd"][seen["cmd"].index("-C") + 1]), Path(seen["tmp"]))
        self.assertTrue(seen["prompt"].startswith("Use only this message and the attached image."))

    def test_early_exit_judges_candidates_while_others_are_judged(self):
        spans, lock = {}, threading.Lock()
        src = self.tmp / "src.png"
        src.write_bytes(b"\x89PNG\r\n\x1a\n")

        def gen(tasks, workdir, effort, timeout, kind="generate", cancel=None):
            t = tasks[0]
            time.sleep({"c1": 0.05, "c2": 0.25}[t["id"][-2:]])
            p = self.tmp / f"{t['id']}.png"
            shutil.copy2(src, p)
            return {"results": {t["id"]: {"ok": True, "src": str(p), "ms": 1, "err": None}}, "wall_s": 0.1,
                    "thread_id": None, "session_total_ms": 1, "tokens": None}

        def judge(img, brief, threshold=4, model=None, effort="high", timeout=420, checklist=None, job=None, **k):
            with lock:
                spans[job] = [time.time(), None]
            cancel = k.get("cancel")
            slow = job.endswith("c2")  # c2 is judged slowly and must be cancelled once c1 passes
            if cancel is not None and cancel.wait(1.5 if slow else 0.6):
                return {"computed_verdict": "CANCELLED"}
            spans[job][1] = time.time()
            return judge_result("PASS" if job == "risky" else "FAIL")
        ci.codex_parallel_images, ci.run_judge = gen, judge
        t0 = time.time()
        rep = ci.fast_pipeline([{"name": "risky", "brief": "The barista tilts the cup while pouring", "aspect": "3:2"}],
                               args_ns(), self.tmp, self.tmp / "out")
        im = rep["images"][0]
        self.assertEqual(im["verdict"], "PASS")
        self.assertLess(spans["risky-c2"][0], spans["risky"][1])  # c2's judge started while c1 was being judged
        self.assertLess(time.time() - t0, 1.4)  # c1 passed: c2's slow judge was cancelled, not waited for
        self.assertIsNotNone(im.get("early_exit"))

    def test_atomic_write_replaces_without_leftovers(self):
        p = self.tmp / "assets.json"
        p.write_text("old")
        ci.write_atomic(p, '{"a": 1}')
        self.assertEqual(json.loads(p.read_text()), {"a": 1})
        self.assertEqual([x.name for x in self.tmp.iterdir()], ["assets.json"])

    def test_api_retries_a_server_error_on_the_same_model(self):
        self.assertEqual(ci.retry_after({"retry-after": "1.5"}, 10), 1.5)
        self.assertEqual(ci.retry_after({"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}, 7), 7)
        self.assertEqual(ci.retry_after({}, 5), 5)
        seen = []

        def fake_api(path, payload, key, timeout):
            seen.append(payload["model"])
            if len(seen) == 1:
                return 503, {"error": {"code": "server_error", "message": "busy"}}, {"retry-after": "0"}
            return 200, {"data": [{"b64_json": "iVBORw0KGgo="}]}, {}
        ci.api_call, ci.get_api_key = fake_api, (lambda: "k")
        ns = argparse.Namespace(tier="final", model=None, quality=None, api_size=None, aspect="3:2", raw_prompt=True,
                                mask=None, dry_run=False, timeout=5)
        res = ci.engine_api(ns, "a cup", [self.tmp / "a.png"], [], None, self.tmp)
        self.assertEqual(seen, ["gpt-image-2.5-sunburst", "gpt-image-2.5-sunburst"])  # no silent downgrade
        self.assertEqual(res["model"], "gpt-image-2.5-sunburst")


class Docs(unittest.TestCase):
    """The docs Claude reads first: SKILL.md stays short and says how to run things; master.md's contents point at the
    real lines (they go stale when master.md is edited); cli.md covers the flags added for failures and resumes."""
    ROOT = SCRIPT.parent.parent

    def test_docs_point_to_real_lines_and_stay_short(self):
        skill = (self.ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLess(len(skill), 13500)  # loaded on every use
        for must in ("run_in_background", "--rejudge", "--resume", "batch-report.md", "about 90 s", "about 40 s"):
            self.assertIn(must, skill)
        lines = (self.ROOT / "references" / "master.md").read_text(encoding="utf-8").split("\n")
        toc = [l for l in lines[:40] if re.match(r"\d+\. .*\(line \d+", l)]
        self.assertEqual(len(toc), 20)
        for entry in toc:
            sec = entry.split(".")[0]
            first = int(re.search(r"\(line (\d+)", entry).group(1))
            self.assertTrue(lines[first - 1].startswith(f"## {sec}. "), entry)
            for sub, n in re.findall(r"(\d+\.\d+\w*) [^,;)]*? line (\d+)", entry):
                self.assertTrue(lines[int(n) - 1].startswith(f"### {sub} "), (entry, sub))
        cli = (self.ROOT / "references" / "cli.md").read_text(encoding="utf-8")
        for flag in ("--resume", "--rejudge", "--judge-timeout", "## `judge`", "WIDTHxHEIGHT", "3 = stopped"):
            self.assertIn(flag, cli)
        for text in (skill, cli):
            self.assertNotIn("\u2014", text)  # no em dash
            self.assertNotIn(" \u2013 ", text)  # no spaced en dash


class FailingSessions(unittest.TestCase):
    """Stuck or failing Codex sessions: time limits, no long retries, Codex's own error, a stop on a usage limit,
    kept event logs. The Codex CLI is a small shell script here; the real one is never called."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.saved = (ci.codex_bin, ci.codex_parallel_images, ci.run_judge, ci.codex_version, ci.finish_image,
                      ci.TELEMETRY["log_dir"], ci.TELEMETRY["fail_dir"], ci.CODEX_HOME)
        ci.CODEX_HOME = self.tmp / "codex-home"  # rollout lookups never touch the real ~/.codex
        ci.BUDGET.used = 0

    def tearDown(self):
        (ci.codex_bin, ci.codex_parallel_images, ci.run_judge, ci.codex_version, ci.finish_image,
         ci.TELEMETRY["log_dir"], ci.TELEMETRY["fail_dir"], ci.CODEX_HOME) = self.saved
        ci._LIVE["stop"], ci._LIVE["fatal"] = False, None
        ci.BUDGET.limit, ci.BUDGET.used = None, 0
        shutil.rmtree(self.tmp, ignore_errors=True)

    def fake_codex(self, body: str) -> str:
        p = self.tmp / "codex"
        p.write_text("#!/bin/sh\ncat > /dev/null\n" + body, encoding="utf-8")
        p.chmod(0o755)
        return str(p)

    def cli(self, *argv):
        old = sys.argv
        sys.argv = ["codex_image.py", *argv]
        code = 0
        try:
            with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
                ci.main()
        except SystemExit as e:
            code = e.code
        finally:
            sys.argv = old
        return code, out.getvalue()

    def test_session_time_limits_default_to_the_measured_ones(self):
        self.assertEqual((ci.GEN_TIMEOUT, ci.JUDGE_TIMEOUT), (480, 150))
        self.assertEqual(ci.fast_args(argparse.Namespace(timeout=None)).timeout, ci.GEN_TIMEOUT)
        self.assertEqual(ci.fast_args(argparse.Namespace(timeout=900)).timeout, 900)  # the flag still wins
        seen = []
        ci.run_judge = lambda img, brief, threshold=4, model=None, effort="high", timeout=0, checklist=None, \
            job=None, **k: seen.append(timeout) or judge_result("PASS")
        ci.judge_parallel([("a", "x.png", "b", None)], args_ns())
        ci.judge_parallel([("a", "x.png", "b", None)], args_ns(judge_timeout=60))
        self.assertEqual(seen, [ci.JUDGE_TIMEOUT, 60])
        got = []
        with mock.patch.object(ci, "cmd_generate_or_edit", lambda a: got.append((a.timeout, a.judge_timeout))):
            self.cli("generate", "--prompt", "a cup")
            self.cli("generate", "--prompt", "a cup", "--timeout", "900", "--judge-timeout", "200")
        self.assertEqual(got, [(None, ci.JUDGE_TIMEOUT), (900, 200)])  # None becomes 480 (fast) or 900 (agent)

    def test_no_second_full_length_try_after_a_timeout(self):
        calls = []

        def gen(err):
            def g(tasks, workdir, effort, timeout, kind="generate", cancel=None):
                calls.append(kind)
                return {"results": {t["id"]: {"ok": False, "src": None, "ms": None, "err": err} for t in tasks},
                        "wall_s": 0.1, "thread_id": None, "session_total_ms": None, "tokens": None}
            return g
        task = [{"id": "cup-c1", "prompt": "p"}]
        for err, sessions in (("timed out after 480s (events: x)", 1), ("You've hit your usage limit.", 1),
                              ("no result from the Codex session", 2)):  # only a quick failure is retried
            calls.clear()
            ci.codex_parallel_images = gen(err)
            ci.generate_parallel(task, self.tmp, args_ns(), "generate")
            self.assertEqual(len(calls), sessions, err)
        for err, sessions in (("timed out after 480s", 2), ("no result from the Codex session", 3)):
            calls.clear()  # two candidates with early exit: the plain retry runs only after quick failures
            ci.codex_parallel_images = gen(err)
            ci.run_judge = lambda *a, **k: judge_result("PASS")
            rep = ci.fast_pipeline([{"name": "risky", "brief": "The barista tilts the cup while pouring",
                                     "aspect": "3:2"}], args_ns(), self.tmp, self.tmp / f"out{sessions}")
            self.assertEqual(len(calls), sessions, err)
            self.assertIn(err, rep["images"][0]["error"])
            self.assertEqual(rep["images"][0]["error"].count(err), 1)  # the same reason is not repeated per candidate

    def test_codex_error_text_reaches_the_result_and_the_events_are_kept(self):
        ci.codex_bin = lambda: self.fake_codex(
            'echo \'{"type": "thread.started", "thread_id": "tid-9"}\'\n'
            'echo \'{"type": "turn.failed", "error": {"message": "stream error: the model is overloaded"}}\'\n'
            'echo "Error: turn failed" >&2\nexit 1\n')
        ci.TELEMETRY["log_dir"], ci.TELEMETRY["fail_dir"] = None, str(self.tmp / "out" / "logs")
        res = ci.codex_parallel_images([{"id": "mug-c1", "prompt": "p"}], self.tmp, "low", 30)
        err = res["results"]["mug-c1"]["err"]
        self.assertTrue(err.startswith("stream error: the model is overloaded"), err)
        kept = Path(err.split("(events: ")[1].rstrip(")"))
        self.assertTrue(kept.exists())
        self.assertIn("overloaded", kept.read_text())
        self.assertTrue(kept.with_name(kept.name.replace(".events.jsonl", ".stderr.txt")).exists())
        self.assertTrue(ci.retry_worth(err))  # an overloaded model is worth one more quick try
        ci.codex_bin = lambda: self.fake_codex("sleep 30\n")
        t0 = time.time()
        res = ci.codex_parallel_images([{"id": "mug-c1", "prompt": "p"}], self.tmp, "low", 1)
        self.assertLess(time.time() - t0, 10)
        self.assertTrue(res["results"]["mug-c1"]["err"].startswith("timed out after 1s (events: "))
        self.assertFalse(ci.retry_worth(res["results"]["mug-c1"]["err"]))

    def test_a_usage_limit_stops_the_whole_run_with_codexs_words(self):
        calls = self.tmp / "calls"
        ci.codex_bin = lambda: self.fake_codex(
            f'echo x >> "{calls}"\n'
            f'if mkdir "{self.tmp / "first"}" 2>/dev/null; then\n'
            '  echo \'{"type": "error", "message": "You have hit your usage limit. Try again in 2 hours."}\'\n'
            '  exit 1\nfi\nsleep 30\n')  # the first session hits the limit; the others would hang
        ci.codex_version = lambda b: "codex-cli test"
        jf = self.tmp / "jobs.json"
        jf.write_text(json.dumps([{"name": n, "aspect": "1:1", "brief": f"Intent: product photo\nSubject: one {n}"}
                                  for n in ("mug", "cup", "jar")]), encoding="utf-8")
        t0 = time.time()
        code, out = self.cli("batch", "--jobs", str(jf), "--out-dir", str(self.tmp / "out"))
        self.assertLess(time.time() - t0, 15)  # the hanging sessions were stopped, not waited for
        self.assertEqual(code, 3)
        rep = json.loads(out)
        self.assertIn("usage limit", rep["stopped"])
        # one session per job at most, and no retries after the stop; a slow machine may stop before the third starts
        self.assertIn(len(calls.read_text().split()), (1, 2, 3))
        self.assertIn("usage limit", (self.tmp / "out" / "batch-report.json").read_text())


if __name__ == "__main__":
    unittest.main()
