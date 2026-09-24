"""The pattern library must render with no errors and no warnings on every preset it lists (templates/README.md).

Slow (about a minute: ~60 renders), so it runs only when asked:
    CODEX_DESIGN_PATTERNS=1 python3 -m unittest discover -s ~/.claude/skills/codex-design/tests
Run it after any change to the checks, the kit or a template.
"""
import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(os.environ.get("CODEX_DESIGN_SCRIPT") or Path(__file__).resolve().parent.parent / "scripts" / "design.py")
spec = importlib.util.spec_from_file_location("design_patterns", SCRIPT)
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
d.log = lambda *a, **k: None
T = SCRIPT.parent.parent / "templates"
FEED = ["ig-portrait", "ig-square", "ig-story", "fb-feed"]
# book wraps are computed, not catalogued: a paperback, a hardcover and a book too thin for spine text
WRAPS = {"kdp-pb-6x9-240-cream": ("kdp", "paperback", 6, 9, 240, "cream"),
         "kdp-hc-6x9-320-white": ("kdp", "hardcover", 6, 9, 320, "white"),
         "kdp-pb-6x9-60-white": ("kdp", "paperback", 6, 9, 60, "white")}
d.presets()
for _pid, _a in WRAPS.items():
    d._PRESETS[_pid] = d.book_preset(d.book_wrap(*_a), _pid)

# (template, presets, extra produce() arguments, output extension)
CASES = [
    ("patterns/post-photo.html", FEED, {}, "png"),
    ("patterns/post-type.html", FEED, {}, "png"),
    ("patterns/post-product.html", FEED + ["vertical-safe"], {}, "png"),
    ("patterns/card.html", FEED, {}, "png"),
    ("patterns/story.html", ["ig-story", "vertical-safe", "wa-status"], {}, "png"),
    ("patterns/day-post.html", FEED, {"occasion": "celebratory"}, "png"),
    ("patterns/day-solemn.html", ["ig-portrait", "ig-square", "ig-story"], {"occasion": "solemn"}, "png"),
    ("patterns/thumbnail.html", ["yt-thumbnail"], {}, "png"),
    ("patterns/carousel.html", ["ig-carousel"], {"slides": 5}, "png"),
    ("patterns/carousel.html", ["li-doc"], {"slides": 5}, "pdf"),
    ("patterns/cover.html", ["yt-banner", "fb-cover", "li-profile-cover", "li-company-cover", "x-header"], {}, "png"),
    ("patterns/ad-banner.html", ["iab-mrec", "iab-leaderboard", "iab-halfpage", "iab-skyscraper", "iab-mobile-banner",
                                 "iab-billboard", "gads-landscape", "gads-square"], {}, "png"),
    ("patterns/infographic.html", ["ig-portrait", "pin-standard", "ig-story", "li-square"], {}, "png"),
    ("patterns/pin.html", ["pin-standard"], {}, "png"),
    ("patterns/blog-featured.html", ["blog-featured", "og-image", "article-hero", "x-card"], {}, "png"),
    ("patterns/product-infographic.html", ["shop-square"], {}, "png"),
    ("patterns/square-cover.html", ["podcast-cover", "album-cover", "audiobook-cover", "yt-podcast-thumb"], {}, "png"),
    ("patterns/app-screenshot.html", ["appstore-iphone-69", "play-phone-screenshot"], {}, "png"),
    ("patterns/book-cover.html", ["ebook-master", "ebook-kobo", "ebook-bookbaby"], {}, "png"),
    ("patterns/book-cover.html", list(WRAPS), {}, "pdf"),
    ("patterns/certificate.html", ["certificate-a4-landscape", "certificate-letter-landscape"], {}, "pdf"),
    ("patterns/invitation.html", ["invite-5x7", "invite-a5"], {}, "pdf"),
    ("patterns/sign.html", ["banner-3x6ft", "banner-2x4ft", "pvc-banner-2000x1000", "pvc-banner-bd-4x6ft",
                            "billboard-us-bulletin", "billboard-uk-48sheet", "billboard-bd-20x10ft", "transit-bus-king"],
     {}, "pdf"),
    ("patterns/sign.html", ["signage-1080p", "signage-4k"], {}, "png"),
    ("patterns/poster.html", ["a3-poster", "a2-poster", "tabloid-poster", "poster-18x24"], {}, "pdf"),
    ("patterns/flyer.html", ["a5-flyer"], {"pages": 2}, "pdf"),
    ("patterns/brochure-trifold.html", ["trifold-a4"], {"pages": 2}, "pdf"),
    ("patterns/business-card.html", ["bc-eu", "bc-us", "bc-jp"], {"pages": 2}, "pdf"),
    ("brand/guidelines.html", ["deck-16x9"], {"pages": 10}, "pdf"),
]


@unittest.skipUnless(os.environ.get("CODEX_DESIGN_PATTERNS"), "set CODEX_DESIGN_PATTERNS=1 to render the pattern library")
class Patterns(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ch = d.Chrome()
        cls.tmp = Path(tempfile.mkdtemp())

    @classmethod
    def tearDownClass(cls):
        cls.ch.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_pattern_is_clean_on_its_presets(self):
        failures = []
        for tpl, presets, kw, ext in CASES:
            for preset in presets:
                rep = d.produce(self.ch, T / tpl, d.resolve_canvas(preset, None), self.tmp / f"{Path(tpl).stem}-{preset}.{ext}",
                                **kw)
                checks = rep.get("checks") or {}
                problems = checks.get("errors", []) + checks.get("warnings", [])
                if problems:
                    failures.append(f"{tpl} on {preset}: " + " | ".join(p[:140] for p in problems))
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
