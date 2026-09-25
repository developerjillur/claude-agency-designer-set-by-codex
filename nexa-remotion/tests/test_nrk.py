"""Offline tests for nrk.py and the kit's shape (no Remotion render, no network)."""
import argparse
import importlib.util
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
REPO = SKILL.parent
spec = importlib.util.spec_from_file_location("nrk", SKILL / "scripts" / "nrk.py")
nrk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nrk)

TABLE = """
The following compositions are available:

DemoCoreThemes                 1920x1080      Still
Main                   30      1920x1080      600 (20.00 sec)
Shorts                 60      1080x1920      900 (15.00 sec)
"""


def fake_modules(root, version="4.0.528", skip=(), wrong=()):
    mods = Path(root) / "node_modules"
    for name in nrk.REQUIRED:
        if name in skip:
            continue
        d = mods / name
        d.mkdir(parents=True, exist_ok=True)
        v = "4.0.527" if name in wrong else (version if name == "remotion" or name.startswith("@remotion/") else "1.0.0")
        (d / "package.json").write_text(json.dumps({"name": name, "version": v}))
    return mods


class Parsing(unittest.TestCase):
    def test_compositions_table(self):
        comps = nrk.parse_compositions(TABLE)
        self.assertEqual(comps["Main"], (600, 30.0, 1920, 1080))
        self.assertEqual(comps["Shorts"], (900, 60.0, 1080, 1920))
        self.assertEqual(comps["DemoCoreThemes"], (1, 30.0, 1920, 1080))

    def test_pick_frames_given(self):
        self.assertEqual(nrk.pick_frames(100, 30, given="90,0,500,45,45"), [0, 45, 90, 99])

    def test_pick_frames_every_keeps_last(self):
        picks = nrk.pick_frames(90, 30, every=1)
        self.assertEqual(picks, [0, 30, 60, 89])

    def test_pick_frames_default_about_twelve(self):
        picks = nrk.pick_frames(1800, 30)
        self.assertTrue(10 <= len(picks) <= 14, picks)
        self.assertEqual(picks[-1], 1799)

    def test_one_frame(self):
        self.assertEqual(nrk.pick_frames(1, 30, every=0.5), [0])


class Presets(unittest.TestCase):
    def test_web_is_bt709_crf18(self):
        args = nrk.PRESETS["web"]["args"]
        self.assertIn("--color-space=bt709", args)
        self.assertIn("--crf=18", args)
        self.assertIn("--codec=h264", args)

    def test_alpha_presets(self):
        self.assertIn("--pixel-format=yuva444p10le", nrk.PRESETS["alpha"]["args"])
        self.assertIn("--image-format=png", nrk.PRESETS["alpha"]["args"])
        self.assertIn("--prores-profile=4444", nrk.PRESETS["alpha"]["args"])
        self.assertIn("--pixel-format=yuva420p", nrk.PRESETS["webm-alpha"]["args"])
        self.assertIn("--codec=vp9", nrk.PRESETS["webm-alpha"]["args"])

    def test_upload_is_high_quality_h264(self):
        a = nrk.PRESETS["upload"]["args"]
        self.assertIn("--crf=12", a)
        self.assertIn("--color-space=bt709", a)
        self.assertEqual(nrk.PRESETS["upload"]["ext"], ".mp4")

    def test_safe_box_for_guides(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.assertEqual(nrk.safe_box(d, 1920, 1080), nrk.FORMATS["youtube"]["safe"])
            (d / "project.json").write_text(json.dumps({"format": "story"}))
            self.assertEqual(nrk.safe_box(d, 1080, 1920), nrk.FORMATS["story"]["safe"])
            self.assertIsNone(nrk.safe_box(d, 640, 480))

    def test_every_preset_has_extension(self):
        for name, p in nrk.PRESETS.items():
            self.assertTrue(p["ext"].startswith("."), name)


class KitShape(unittest.TestCase):
    def test_formats_match_kit(self):
        text = (SKILL / "kit" / "src" / "kit" / "core" / "format.tsx").read_text()
        for name, f in nrk.FORMATS.items():
            key = "'4k'" if name == "4k" else name
            m = re.search(r"%s: \{width: (\d+), height: (\d+), safe: \{x: (\d+), y: (\d+), w: (\d+), h: (\d+)\}" % re.escape(key), text)
            self.assertIsNotNone(m, name)
            self.assertEqual([int(g) for g in m.groups()], [f["width"], f["height"]] + f["safe"], name)

    def test_twenty_themes(self):
        text = (SKILL / "kit" / "src" / "kit" / "core" / "themes.ts").read_text()
        self.assertEqual(len(re.findall(r"^\t\tname: '", text, re.M)), 20)

    def test_theme_fonts_exist(self):
        fonts = (SKILL / "kit" / "src" / "kit" / "core" / "fonts.ts").read_text()
        keys = set(re.findall(r"^\t(\w+): font\(", fonts, re.M))
        themes = (SKILL / "kit" / "src" / "kit" / "core" / "themes.ts").read_text()
        used = set(re.findall(r"(?:display|body|mono|bangla|serif|hand): '(\w+)'", themes))
        self.assertTrue(used, "no fonts found in themes")
        self.assertEqual(used - keys, set())

    def test_required_are_in_kit_package(self):
        pkg = json.loads((SKILL / "kit" / "package.json").read_text())
        deps = {**pkg["dependencies"], **pkg["devDependencies"]}
        for name in nrk.REQUIRED:
            self.assertIn(name, deps, name)
        for name, ver in deps.items():
            if name == "remotion" or name.startswith("@remotion/"):
                self.assertEqual(ver, nrk.REMOTION_VERSION, name)


class Modules(unittest.TestCase):
    def test_report_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            found, problems = nrk.modules_report(fake_modules(tmp))
            self.assertEqual(problems, [])
            self.assertEqual(len(found), len(nrk.REQUIRED))

    def test_report_problems(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, problems = nrk.modules_report(fake_modules(tmp, skip=("three",), wrong=("@remotion/effects",)))
            joined = " ".join(problems)
            self.assertIn("three is missing", joined)
            self.assertIn("@remotion/effects is 4.0.527", joined)


class Projects(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.mods = fake_modules(self.root / "shared")
        self.env = mock.patch.dict(os.environ, {"NRK_MODULES": str(self.mods)})
        self.env.start()
        self.home = mock.patch.object(nrk, "NRK_HOME", self.root / "home")
        self.home.start()

    def tearDown(self):
        self.env.stop()
        self.home.stop()
        self.tmp.cleanup()

    def new(self, name="promo", fmt="shorts", seconds=15):
        args = argparse.Namespace(project=str(self.root / name), format=fmt, fps=30, seconds=seconds, title="Promo")
        nrk.cmd_new(args)
        return self.root / name

    def test_new_project(self):
        d = self.new()
        meta = json.loads((d / "project.json").read_text())
        self.assertEqual((meta["width"], meta["height"], meta["frames"]), (1080, 1920, 450))
        self.assertEqual(meta["safe"], [65, 270, 875, 978])
        root = (d / "src" / "Root.tsx").read_text()
        self.assertIn("width={1080}", root)
        self.assertIn("durationInFrames={450}", root)
        self.assertNotIn("__", root)
        self.assertTrue((d / "src" / "kit" / "core" / "index.ts").exists())
        self.assertTrue((d / "src" / "kit" / "motion" / "index.ts").exists())
        self.assertTrue((d / "node_modules").is_symlink())
        self.assertEqual((d / "node_modules").resolve(), self.mods.resolve())
        self.assertIn("src/kit", "\n".join(str(p.relative_to(d)) for p in d.rglob("index.ts")))
        for name in nrk.RUNTIME_PUBLIC:
            src = nrk.KIT / "public" / name
            if src.is_dir():
                want = sorted(f.relative_to(src) for f in src.rglob("*") if f.is_file() and f.name != ".DS_Store")
                got = sorted(f.relative_to(d / "public" / name) for f in (d / "public" / name).rglob("*") if f.is_file())
                self.assertEqual(got, want, name)
        self.assertFalse((d / "public" / "edit").exists(), "demo media must not be copied into projects")

    def test_new_refuses_non_empty(self):
        d = self.root / "busy"
        d.mkdir()
        (d / "notes.txt").write_text("keep me")
        with self.assertRaises(nrk.NrkError):
            nrk.cmd_new(argparse.Namespace(project=str(d), format="youtube", fps=30, seconds=10, title=None))
        self.assertEqual((d / "notes.txt").read_text(), "keep me")

    def test_sync_keeps_old_copy(self):
        d = self.new()
        marker = d / "src" / "kit" / "core" / "mine.ts"
        marker.write_text("// an edit the project made")
        nrk.cmd_sync(argparse.Namespace(project=str(d)))
        kept = list((d / "src").glob("kit.before-sync-*"))
        self.assertEqual(len(kept), 1)
        self.assertTrue((kept[0] / "core" / "mine.ts").exists())
        self.assertFalse(marker.exists())

    def test_check_dir_refuses_foreign_folder(self):
        foreign = self.root / "home" / "kit-check" / "type"
        foreign.mkdir(parents=True)
        (foreign / "src").mkdir()
        (foreign / "src" / "precious.txt").write_text("not ours")
        with self.assertRaises(nrk.NrkError):
            nrk.check_dir("type")
        self.assertTrue((foreign / "src" / "precious.txt").exists())

    def test_check_dir_clears_its_own(self):
        work = nrk.check_dir("motion")
        (work / "src").mkdir()
        (work / "src" / "old.tsx").write_text("old")
        again = nrk.check_dir("motion")
        self.assertEqual(again, work)
        self.assertFalse((work / "src" / "old.tsx").exists())


EM, SPACED_EN = chr(0x2014), " %s " % chr(0x2013)


class Family(unittest.TestCase):
    def family(self):
        return sorted(p for p in REPO.iterdir() if p.is_dir() and p.name.startswith("nexa-remotion"))

    def test_no_em_dash(self):
        bad = []
        for d in self.family():
            for p in d.rglob("*"):
                if p.is_file() and p.suffix in {".md", ".ts", ".tsx", ".py", ".json"} and "node_modules" not in p.parts:
                    text = p.read_text(encoding="utf-8", errors="ignore")
                    if EM in text or SPACED_EN in text:
                        bad.append(str(p.relative_to(REPO)))
        self.assertEqual(bad, [])

    def test_skill_frontmatter(self):
        for d in self.family():
            skill = d / "SKILL.md"
            if not skill.exists():
                continue
            text = skill.read_text()
            m = re.match(r"---\nname: (.+)\ndescription: \"(.+)\"\n---\n", text)
            self.assertIsNotNone(m, d.name)
            self.assertEqual(m.group(1), d.name)
            self.assertLessEqual(len(m.group(2)), 1024, d.name)


if __name__ == "__main__":
    unittest.main()
