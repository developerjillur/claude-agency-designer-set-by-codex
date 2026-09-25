"""Offline tests for remotion-broll: the kit is whole, its scenes take their words from one file, and broll.py starts a
project without touching anything else. No npm, no render: those run by hand (see SKILL.md).

Run: python3 -m unittest discover -s ~/.claude/skills/remotion-broll/tests
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT / "template"
sys.path.insert(0, str(KIT / "scripts"))
import broll  # noqa: E402


def node_reads_typescript() -> bool:
    node = shutil.which("node")
    if not node:
        return False
    r = subprocess.run([node, "--experimental-strip-types", "--no-warnings", "-e", "0"], capture_output=True)
    return r.returncode == 0


class TemplateTests(unittest.TestCase):
    def test_the_kit_is_whole_and_holds_no_build_output(self):
        for f in ("package.json", "package-lock.json", "remotion.config.ts", "tsconfig.json", "src/Root.tsx",
                  "src/copy.ts", "src/theme.ts", "src/components/draw.tsx", "src/components/Guitarist.tsx",
                  "src/components/Runner.tsx", "public/presenter-pip.png", "public/creator-cutout.png"):
            self.assertTrue((TEMPLATE / f).exists(), f)
        for f in ("node_modules", "out", ".git", ".ecc"):
            self.assertFalse((TEMPLATE / f).exists(), f)

    def test_remotion_packages_share_one_pinned_version(self):
        pkg = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))
        rem = {k: v for k, v in {**pkg["dependencies"], **pkg["devDependencies"]}.items()
               if k == "remotion" or k.startswith("@remotion/")}
        self.assertGreater(len(rem), 5)
        self.assertEqual(len(set(rem.values())), 1, rem)
        self.assertRegex(next(iter(rem.values())), r"^\d+\.\d+\.\d+$")   # exact, so npm ci gives every project the same

    def test_the_pictures_are_small_stand_ins(self):
        """The session's AI presenter stays out of the public kit: the scenes load plain stand-ins until a project
        adds its own (references/asset-briefs.json)."""
        pics = sorted(p.name for p in (TEMPLATE / "public").iterdir() if p.suffix.lower() in (".png", ".jpg", ".webp"))
        self.assertEqual(pics, ["creator-cutout.png", "presenter-pip.png"])
        for p in pics:
            self.assertLess((TEMPLATE / "public" / p).stat().st_size, 60_000, p)

    def test_scenes_take_their_words_from_copy_ts(self):
        """A new product changes src/copy.ts, not fourteen scene files."""
        copy = (TEMPLATE / "src" / "copy.ts").read_text(encoding="utf-8")
        words = re.findall(r'"([A-Za-z][^"\n]{3,})"', copy)
        self.assertIn("Just for fun", words)
        for f in (TEMPLATE / "src").rglob("*.tsx"):
            text = f.read_text(encoding="utf-8")
            for w in words:  # a composition's id or a sequence's name is not on screen
                shown = re.search(rf'(?<!id=)(?<!name=)"{re.escape(w)}"', text) or re.search(rf">\s*{re.escape(w)}\s*<", text)
                self.assertFalse(shown, f"{f.name} still spells out {w!r}")

    def test_the_charts_compute_from_growth(self):
        stat = (TEMPLATE / "src" / "scenes" / "StatScene.tsx").read_text(encoding="utf-8")
        self.assertFalse("1.01" in stat, "StatScene still has 1.01 written in")
        self.assertIn("GROWTH.rate", stat)
        bars = (TEMPLATE / "src" / "scenes2" / "StatBarsScene.tsx").read_text(encoding="utf-8")
        self.assertNotIn("Math.pow(1.01", bars)


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="broll-test-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def new(self, *extra) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(KIT / "scripts" / "broll.py"), "new", *map(str, extra)],
                              capture_output=True, text=True)

    def test_new_copies_the_kit_and_never_overwrites(self):
        dest = self.tmp / "promo"
        r = self.new(dest, "--no-install")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((dest / "src" / "copy.ts").exists())
        self.assertFalse((dest / "node_modules").exists())
        r = self.new(dest, "--no-install")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not empty", r.stderr)

    def test_linked_modules_must_be_the_kits_remotion(self):
        other = self.tmp / "old" / "node_modules" / "remotion"
        other.mkdir(parents=True)
        (other / "package.json").write_text(json.dumps({"version": "4.0.1"}))
        r = self.new(self.tmp / "p", "--link-modules", self.tmp / "old")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("the kit needs", r.stderr)

    def test_composition_lengths_are_read_from_root(self):
        root = (TEMPLATE / "src" / "Root.tsx").read_text(encoding="utf-8")
        self.assertEqual(broll.comp_frames(root, "BrollMinute"), 1800)
        self.assertEqual(broll.comp_frames(root, "BrollDemo"), 300)
        self.assertIsNone(broll.comp_frames(root, "Nope"))

    def test_copy_lines_give_each_line_on_screen_a_role(self):
        lines = broll.copy_lines({"caption": {"first": ["If", "your"], "firstKey": ["your"]},
                                  "steps": [["Practice a little", "every day"]], "end": {"button": "Subscribe"},
                                  "bars": {"periods": [{"label": "1 week", "days": 7}]}, "recap": ["Share"]})
        self.assertIn({"role": "headline", "text": "If your"}, lines)
        self.assertIn({"role": "headline", "text": "Practice a little every day"}, lines)
        self.assertIn({"role": "cta", "text": "Subscribe"}, lines)
        self.assertIn({"role": "label", "text": "1 week"}, lines)
        self.assertIn({"role": "label", "text": "Share"}, lines)
        self.assertNotIn("your", [x["text"] for x in lines])     # the underlined word is part of its line

    @unittest.skipUnless(node_reads_typescript(), "needs Node 22.6 or newer")
    def test_the_real_copy_file_reads_as_lines(self):
        dest = self.tmp / "p"
        self.assertEqual(self.new(dest, "--no-install").returncode, 0)
        copy = broll.read_copy(dest)
        texts = [x["text"] for x in broll.copy_lines(copy)]
        self.assertIn("Get 1% better every day", texts)
        self.assertIn("Pick one skill and start today.", texts)


if __name__ == "__main__":
    unittest.main()
