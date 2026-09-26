"""Offline tests for research.py: no network (http_get is replaced), a temp cache and temp research folders."""
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
TMP = tempfile.mkdtemp(prefix="nexa-research-test-")
os.environ["NEXA_CACHE"] = TMP
import research  # noqa: E402

PAGE = b"""<html><head><title>Plain title</title>
<meta property="og:title" content="The study page">
<meta name="author" content="A. Researcher">
<meta property="article:published_time" content="2024-05-02">
<script>var hidden = "people become immersed in a story";</script><style>p{color:red}</style></head>
<body><h1>Findings</h1><p>People become immersed in a story when they feel focused attention,
emotional engagement &amp; mental imagery.</p><p>Retention fell by 12% after the first minute.</p></body></html>"""


def run(*argv):
    out = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out):
        try:
            research.main(list(argv))
        except SystemExit as e:
            code = e.code or 0
    text = out.getvalue()
    return code, (json.loads(text) if text.strip() else None)


class QuoteTests(unittest.TestCase):
    def test_exact_after_normalizing(self):
        ok, how = research.quote_in_text("Retention fell by 12 % after the first minute",
                                         "Retention fell by 12% after the first minute.")
        self.assertFalse(ok)  # "12 %" and "12%" are different tokens: numbers must match as written
        ok, how = research.quote_in_text("retention fell by 12% after the first minute",
                                         "Retention fell by 12% after the first minute.")
        self.assertTrue(ok)
        self.assertEqual(how, "exact")

    def test_curly_quotes_and_entities(self):
        ok, _ = research.quote_in_text("the “best” story wins", 'The "best" story wins, they said.')
        self.assertTrue(ok)

    def test_close_match_needs_words_in_order(self):
        page = "people become deeply immersed in a story when they experience focused attention"
        ok, how = research.quote_in_text("people become immersed in a story when they experience focused attention",
                                         page)
        self.assertTrue(ok, how)
        ok, _ = research.quote_in_text("attention focused experience they when story a in immersed become people",
                                       page)
        self.assertFalse(ok)

    def test_short_quote_needs_exact(self):
        ok, how = research.quote_in_text("sales tripled", "sales nearly tripled last year")
        self.assertFalse(ok)
        self.assertIn("short", how)

    def test_fabricated_quote_is_not_found(self):
        ok, _ = research.quote_in_text("stories raise sales by three hundred percent", PAGE.decode())
        self.assertFalse(ok)


class PageTests(unittest.TestCase):
    def test_text_skips_scripts_and_reads_meta(self):
        text, info = research.html_to_text(PAGE.decode())
        self.assertIn("mental imagery", text)
        self.assertNotIn("var hidden", text)
        self.assertEqual(info["title"], "The study page")
        self.assertEqual(info["published"], "2024-05-02")
        self.assertEqual(info["author"], "A. Researcher")

    def test_youtube_ids(self):
        self.assertEqual(research.yt_id("https://www.youtube.com/watch?v=hNuAv-42jzY&t=3"), "hNuAv-42jzY")
        self.assertEqual(research.yt_id("https://youtu.be/UPkzsr8apq8"), "UPkzsr8apq8")
        self.assertEqual(research.yt_id("https://www.youtube.com/shorts/abcdefghijk"), "abcdefghijk")
        self.assertIsNone(research.yt_id("not a video"))

    def test_views_per_day(self):
        self.assertIsNone(research.views_per_day(None, "20240101"))
        self.assertGreater(research.views_per_day(1000, "20000101"), 0)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp(prefix="proj-", dir=TMP))
        self.real_get = research.http_get
        research.http_get = lambda url, **kw: (200, PAGE, url)
        code, out = run("new", str(self.dir), "--topic", "Immersion")
        self.assertEqual(code, 0)

    def tearDown(self):
        research.http_get = self.real_get

    def add_source(self, url, grade, publisher):
        code, out = run("source", "add", str(self.dir), "--url", url, "--title", "t", "--publisher", publisher,
                        "--date", "2024", "--kind", "study", "--grade", grade)
        self.assertEqual(code, 0, out)
        return out["id"]

    def test_new_never_overwrites(self):
        code, out = run("new", str(self.dir), "--topic", "Again")
        self.assertEqual(code, 2)
        self.assertIn("never overwritten", out["error"])

    def test_claim_needs_known_source(self):
        code, out = run("claim", "add", str(self.dir), "--text", "x", "--source", "s9", "--quote", "y")
        self.assertEqual(code, 2)
        self.assertIn("unknown source", out["error"])

    def test_verify_marks_real_and_fabricated_quotes(self):
        s1 = self.add_source("https://example.org/study", "A", "Journal")
        run("claim", "add", str(self.dir), "--text", "immersion", "--source", s1, "--quote",
            "people become immersed in a story when they feel focused attention")
        run("claim", "add", str(self.dir), "--text", "made up", "--source", s1, "--quote",
            "stories raise sales by three hundred percent")
        code, out = run("verify", str(self.dir), "--fresh")
        self.assertEqual(code, 0)
        status = {c["id"]: c["status"] for c in out["checked"]}
        self.assertEqual(status, {"c1": "verified", "c2": "unsupported"})
        code, out = run("check", str(self.dir), "--level", "final")
        self.assertEqual(code, 1)
        self.assertTrue(any("not found" in e for e in out["errors"]))

    def test_gates_on_grades_and_key_claims(self):
        blog = self.add_source("https://blog.example.com/post", "D", "Some blog")
        news = self.add_source("https://news.example.com/a", "B", "Daily News")
        run("claim", "add", str(self.dir), "--text", "only a blog", "--source", blog, "--quote", "abc def ghi jkl")
        run("claim", "add", str(self.dir), "--text", "key with one", "--source", news, "--quote", "abc def ghi jkl",
            "--key")
        code, out = run("check", str(self.dir), "--level", "draft")
        self.assertEqual(code, 1)
        joined = " ".join(out["errors"])
        self.assertIn("c1: only grade D", joined)
        self.assertIn("c2: key claim needs", joined)

    def test_key_claim_passes_with_two_publishers(self):
        a = self.add_source("https://news.example.com/a", "B", "Daily News")
        b = self.add_source("https://other.example.com/b", "B", "Other Paper")
        run("claim", "add", str(self.dir), "--text", "key", "--source", a, "--source", b, "--quote",
            "retention fell by 12% after the first minute", "--key")
        run("verify", str(self.dir), "--fresh")
        code, out = run("check", str(self.dir), "--level", "final")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["stats"]["verified"], 1)

    def test_pack_collects_notes(self):
        s = self.add_source("https://example.org/study", "A", "Journal")
        run("claim", "add", str(self.dir), "--text", "t", "--source", s, "--quote", "mental imagery")
        notes = self.dir / "research" / "notes" / "voice-bank.json"
        notes.write_text(json.dumps({"schema": "nexa.voice/1", "items": [{"quote": "I stop watching at the ad"}]}))
        code, out = run("pack", str(self.dir))
        self.assertEqual(code, 0)
        self.assertEqual(out["voice_items"], 1)
        pack = json.loads((self.dir / "research" / "pack.json").read_text())
        self.assertEqual(pack["schema"], "nexa.research-pack/1")
        self.assertEqual(len(pack["claims"]), 1)

    def test_fetch_reports_blocked_pages(self):
        research.http_get = lambda url, **kw: (403, b"no", url)
        page = research.fetch_page("https://blocked.example.com/x", fresh=True)
        self.assertFalse(page["ok"])
        self.assertIn("WebFetch", page["error"])

class BankTests(unittest.TestCase):
    def folder(self, name):
        d = Path(TMP) / name
        run("new", str(d), "--topic", "t")
        return d

    def test_note_add_assigns_ids_and_skips_repeats(self):
        d = self.folder("banks")
        code, out = run("note", "add", str(d), "--bank", "voice", "--text", "The oven is too small for my family",
                        "--source", "https://example.com/r/1", "--set", "kind=review")
        self.assertEqual(out["ids"], ["v1"])
        code, out = run("note", "add", str(d), "--bank", "voice", "--text", "the oven is too small for my family")
        self.assertEqual(out["added"], 0)
        code, out = run("note", "add", str(d), "--bank", "competitors", "--set", "url=https://youtu.be/x",
                        "--set", "hook=Cold tea again?", "--set", "result=2.1M views")
        self.assertEqual(out["ids"], ["k1"])
        code, out = run("note", "add", str(d), "--bank", "competitors", "--text", "no url")
        self.assertEqual(code, 2)
        data = json.loads((d / "research" / "notes" / "voice-bank.json").read_text(encoding="utf-8"))
        self.assertEqual(data["items"][0]["kind"], "review")
        code, out = run("pack", str(d))
        pack = json.loads((d / "research" / "pack.json").read_text(encoding="utf-8"))
        self.assertEqual(len(pack["voice_bank"]), 1)
        self.assertEqual(pack["competitors"][0]["hook"], "Cold tea again?")

    def test_youtube_comments_into_the_voice_bank(self):
        d = self.folder("yt")
        info = {"title": "Why tea goes cold", "view_count": 1000, "upload_date": "20260101", "comment_count": 4,
                "comments": [
                    {"text": "My tea is always cold by the time the meeting ends", "like_count": 40, "parent": "root"},
                    {"text": "ok", "like_count": 90, "parent": "root"},
                    {"text": "Same here, every single morning without fail", "like_count": 5, "parent": "abc"},
                    {"text": "Buy mine at https://spam.example now please", "like_count": 1, "parent": "root"},
                    {"text": "Thanks all for watching, more next week", "like_count": 3, "parent": "root",
                     "author_is_uploader": True}]}
        original = research.ytdlp

        def fake_ytdlp(args, timeout=300):
            out = Path(args[args.index("-o") + 1]).parent
            (out / "v.info.json").write_text(json.dumps(info), encoding="utf-8")

        research.ytdlp = fake_ytdlp
        try:
            code, out = run("youtube", "comments", "dQw4w9WgXcQ", "--bank", str(d))
        finally:
            research.ytdlp = original
        self.assertEqual(out["banked"]["added"], 1)      # the short one, the reply, the link and the uploader go
        data = json.loads((d / "research" / "notes" / "voice-bank.json").read_text(encoding="utf-8"))
        self.assertEqual(data["items"][0]["kind"], "comment")
        self.assertIn("dQw4w9WgXcQ", data["items"][0]["source"])


class AuditAndBudgetTests(unittest.TestCase):
    def test_audit_finds_untagged_facts(self):
        d = Path(TMP) / "audit"
        run("new", str(d), "--topic", "t")
        run("source", "add", str(d), "--url", "https://example.com/a", "--title", "A", "--publisher", "Pub",
            "--grade", "B", "--date", "2025-01-01")
        run("claim", "add", str(d), "--text", "Retention fell 12%", "--source", "s1", "--quote",
            "Retention fell by 12% after the first minute")
        brief = Path(TMP) / "audit-brief.md"
        brief.write_text("# Brief\n\nRetention fell by 12% after a minute [c1]. Most viewers leave early, a 2024 "
                         "survey found. People love stories.\n", encoding="utf-8")
        code, out = run("audit", str(brief), "--dir", str(d))
        self.assertEqual(code, 0)
        self.assertEqual(len(out["warnings"]), 1)          # the survey sentence has no tag; the opinion needs none
        code, out = run("audit", str(brief), "--dir", str(d), "--level", "final")
        self.assertEqual(code, 1)
        self.assertTrue(any("not verified: c1" in e for e in out["errors"]))
        brief.write_text("Sales rose 40% [c9].", encoding="utf-8")
        code, out = run("audit", str(brief), "--dir", str(d))
        self.assertTrue(any("unknown claim c9" in e for e in out["errors"]))

    def test_claim_set_by_hand(self):
        d = Path(TMP) / "claimset"
        run("new", str(d), "--topic", "t")
        run("source", "add", str(d), "--url", "https://youtu.be/dQw4w9WgXcQ", "--title", "V", "--publisher", "Ch",
            "--grade", "A", "--kind", "video")
        run("claim", "add", str(d), "--text", "He said it", "--source", "s1", "--quote", "we never gave up")
        code, out = run("claim", "set", str(d), "c1", "--status", "manual")
        self.assertEqual(code, 2)                          # a manual check needs a note
        code, out = run("claim", "set", str(d), "c1", "--status", "manual", "--note",
                        "matched at 3:12 in the agy-watch-video transcript")
        self.assertEqual(out["status"], "manual")
        code, out = run("check", str(d), "--level", "final")
        self.assertEqual(out["stats"]["verified"], 1)

    def test_budget_counts_and_advises(self):
        d = Path(TMP) / "budget"
        run("new", str(d), "--topic", "t")
        run("budget", str(d), "--add", "80", "--by", "agent-a", "--cap", "100")
        code, out = run("budget", str(d), "--add", "5", "--by", "agent-b")
        self.assertEqual(out["used"], 85)
        self.assertEqual(out["by"], {"agent-a": 80, "agent-b": 5})
        self.assertIn("75 %", out["advice"])


    def test_budget_cap_must_be_positive(self):
        d = Path(TMP) / "budget0"
        run("new", str(d), "--topic", "t")
        code, out = run("budget", str(d), "--cap", "0")
        self.assertEqual(code, 2)


class RetryAfterTests(unittest.TestCase):
    def test_seconds_dates_and_junk(self):
        self.assertEqual(research.retry_after("3", 5), 3.0)
        self.assertEqual(research.retry_after("99999", 5), 120.0)                  # the same cap as a date
        self.assertEqual(research.retry_after(None, 5), 5)
        self.assertEqual(research.retry_after("soon", 5), 5)
        self.assertEqual(research.retry_after("Wed, 21 Oct 2015 07:28:00 GMT", 5), 0.0)   # a date in the past

if __name__ == "__main__":
    unittest.main()
