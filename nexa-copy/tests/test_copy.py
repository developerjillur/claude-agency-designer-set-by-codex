"""Offline tests for nexa-copy: platform limits, claims and compliance, email and outbound mechanics, marketplace
rules, Bangladesh f-commerce, the test-plan arithmetic and the review commands (fake model answers, no network)."""
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
TMP = Path(tempfile.mkdtemp(prefix="nexa-copy-test-"))
os.environ["NEXA_CACHE"] = str(TMP / "cache")
import copy_lint as L  # noqa: E402
import copywriter as C  # noqa: E402


def doc(ctype, fields, variants=None, lang="en", **meta):
    vs = variants or [{"id": "A", "fields": fields}]
    return {"meta": dict({"type": ctype, "lang": lang}, **meta), "variants": vs, "test_plan": {}}


def lint(d, level="draft", pack=None):
    return L.lint_copy(d, pack, level)


def has(res, kind, needle):
    return any(needle in x for x in res[kind])


def write(name, data):
    p = TMP / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data, encoding="utf-8")
    return str(p)


def run(argv):
    out = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out):
        try:
            C.main(argv)
        except SystemExit as e:
            code = e.code or 0
    try:
        return code, json.loads(out.getvalue())
    except ValueError:
        return code, out.getvalue()


class Platforms(unittest.TestCase):
    def test_every_type_is_well_formed(self):
        data = L.load_platforms()
        self.assertEqual(data["verified_on"], "2026-09-26")
        for t, p in data["types"].items():
            self.assertIn(p["family"], ("ad", "post", "email", "outbound", "product", "landing", "message"), t)
            self.assertTrue(p["fields"], t)
        self.assertEqual(data["types"]["amazon"]["fields"]["title"]["max_chars"], 75)

    def test_sample_sizes_match_the_research_table(self):
        for base, lift, want in ((0.01, 0.1, 163095), (0.03, 0.2, 13914), (0.05, 0.2, 8158), (0.10, 0.5, 686)):
            self.assertEqual(C.sample_size(base, lift), want)


    def test_a_copy_file_that_is_not_an_object_stops_cleanly(self):
        code, out = run(["lint", write("list.json", "[1, 2]"), "--no-voice"])
        self.assertEqual(code, 2)
        self.assertIn("not a list", out["error"])

    def test_bad_numbers_stop_cleanly(self):
        code, out = run(["new", str(TMP / "zero"), "--type", "meta-feed", "--variants", "0"])
        self.assertEqual(code, 2)
        self.assertIn("--variants", out["error"])
        for flags in (["--power", "1.0"], ["--alpha", "0"], ["--baseline", "0.6", "--lift", "1.0"]):
            argv = ["sample", "--baseline", "0.03", "--lift", "0.2"] + flags
            code, out = run(argv)
            self.assertEqual(code, 2, flags)

class Ads(unittest.TestCase):
    def test_limits_claims_and_hype(self):
        res = lint(doc("meta-feed", [
            {"role": "primary", "text": "Elevate your finances with our platform. Unlock growth today!!"},
            {"role": "headline", "text": "The #1 Revolutionary Bookkeeping Platform For Everyone"}]))
        self.assertTrue(has(res, "errors", "40 at most"))
        self.assertTrue(has(res, "warnings", "'#1'"))
        self.assertTrue(has(res, "warnings", "template opener"))
        self.assertTrue(has(res, "warnings", "exclamation"))
        self.assertTrue(has(res, "warnings", "revolutionary"))

    def test_google_rsa_counts(self):
        res = lint(doc("google-rsa", [{"role": "headline", "text": "Freelance Invoicing Software"},
                                      {"role": "description", "text": "Send an invoice in 60 seconds.",
                                       "claims": ["brief"]}]))
        self.assertTrue(has(res, "warnings", "1 headline fields; 3 at least"))
        self.assertTrue(has(res, "warnings", "1 description fields; 2 at least"))

    def test_tiktok_ad_text_rules(self):
        res = lint(doc("tiktok-ad", [{"role": "ad_text", "text": "The 60-second fix #drain @brand www.fix.com \U0001F600",
                                      "claims": ["brief"]}]))
        for needle in ("hashtags", "@ mentions", "links", "emoji"):
            self.assertTrue(has(res, "errors", needle), needle)

    def test_variant_pack(self):
        one = [{"id": "A", "angle": "pain", "fields": [{"role": "primary", "text": "Receipts on Sunday night again."}]}]
        res = lint(doc("meta-feed", None, variants=one))
        self.assertTrue(has(res, "notes", "3 to 5 angles"))
        self.assertTrue(has(lint(doc("meta-feed", None, variants=one), "final"), "errors", "3 to 5 angles"))
        same = [{"id": k, "angle": "pain",
                 "fields": [{"role": "primary", "text": "Receipts on Sunday night, again and again."}]} for k in "ABC"]
        res = lint(doc("meta-feed", None, variants=same))
        self.assertTrue(has(res, "warnings", "share an angle"))
        self.assertTrue(has(res, "warnings", "share most of their wording"))
        final = lint(doc("meta-feed", None, variants=same), "final")
        self.assertTrue(has(final, "errors", "no test plan"))


class Claims(unittest.TestCase):
    def test_claims_need_a_ledger_row(self):
        d = doc("facebook", [{"role": "caption", "text": "Our tea is the best in Dhaka, 40% off."}])
        self.assertTrue(has(lint(d), "warnings", "claim with no ledger row"))
        self.assertTrue(has(lint(d, "final"), "errors", "claim with no ledger row"))
        d["variants"][0]["fields"][0]["claims"] = ["c1"]
        pack = {"claims": [{"id": "c1", "status": "unsupported"}]}
        self.assertTrue(has(lint(d, "final", pack), "errors", "c1 is unsupported"))
        pack["claims"][0]["status"] = "verified"
        self.assertFalse(has(lint(d, "final", pack), "errors", "c1"))

    def test_disease_green_origin_and_urgency(self):
        res = lint(doc("facebook", [{"role": "caption", "text": "This tea cures diabetes. Eco-friendly pack, made in "
                                                               "Sylhet. Hurry, last chance!"}]))
        self.assertTrue(has(res, "errors", "disease or drug claim"))
        self.assertTrue(has(res, "warnings", "generic green claim"))
        self.assertTrue(has(res, "warnings", "origin claim"))
        self.assertTrue(has(res, "warnings", "urgency"))
        res = lint(doc("facebook", [{"role": "caption", "text": "Last chance: the offer ends 30 September.",
                                     "claims": ["brief"]}]))
        self.assertFalse(has(res, "warnings", "urgency"))

    def test_merge_tags_and_markers(self):
        d = doc("email-promo", [{"role": "subject", "text": "Hi {first_name}, your code"},
                                {"role": "body", "text": "[NEEDS INPUT: offer]"}], footer_by_tool=True)
        final = lint(d, "final")
        self.assertTrue(has(final, "errors", "merge tag"))
        self.assertTrue(has(final, "errors", "NEEDS INPUT"))


class Email(unittest.TestCase):
    def test_cold_first_touch(self):
        res = lint(doc("email-cold", [
            {"role": "subject", "text": "Re: Quick question"},
            {"role": "body", "text": "Hi John, I hope this email finds you well. I run an agency. See https://x.com/work. "
                                     "Would you be free for a 30-minute call next Tuesday."}]))
        self.assertTrue(has(res, "errors", "fake 'Re:'"))
        self.assertTrue(has(res, "errors", "link in a first cold touch"))
        self.assertTrue(has(res, "warnings", "Quick question"))
        self.assertTrue(has(res, "warnings", "meeting or time ask"))
        self.assertTrue(has(res, "warnings", "soft interest question"))
        self.assertTrue(has(res, "warnings", "starts with the sender"))
        self.assertTrue(has(res, "warnings", "opt-out"))

    def test_strong_cold_email_passes(self):
        body = ("Hi Sara,\nOn my phone, the linen page shows two promo banners above the add-to-cart button, so buyers "
                "scroll before they can buy.\nWe moved the button up for Kora Home and their mobile conversion went "
                "from 1.9% to 2.6% in six weeks.\nWorth a 2-minute screen recording of what I'd change on yours?\n"
                "Jillur, Pixel Lane, Dhaka\nNot relevant? Reply no and I won't follow up.")
        res = lint(doc("email-cold", [{"role": "subject", "text": "Rivo mobile checkout"},
                                      {"role": "body", "text": body, "claims": ["brief"]}], address="Dhaka 1207"))
        self.assertTrue(res["ok"], res["errors"])
        self.assertEqual(res["warnings"], [])

    def test_marketing_email_needs_preview_and_footer(self):
        d = doc("email-welcome", [{"role": "subject", "text": "Your code is inside"},
                                  {"role": "body", "text": "Thanks for joining. " * 8}])
        res = lint(d, "final")
        self.assertTrue(has(res, "errors", "no preview text"))
        self.assertTrue(has(res, "errors", "no unsubscribe"))
        d["meta"]["footer_by_tool"] = True
        d["variants"][0]["fields"].append({"role": "preview", "text": "Plus the product most people start with"})
        res = lint(d, "final")
        self.assertFalse(has(res, "errors", "preview"))
        self.assertFalse(has(res, "errors", "unsubscribe"))

    def test_eu_prospects_need_a_privacy_line(self):
        d = doc("email-cold", [{"role": "body", "text": "Your checkout hides the button. Worth a look? Reply no and I "
                                                        "won't follow up."}], region="EU", address="x")
        self.assertTrue(has(lint(d), "warnings", "right-to-object"))


class Outbound(unittest.TestCase):
    def test_proposal_rules(self):
        res = lint(doc("proposal", [{"role": "body", "text": "Dear Sir, I'm passionate about design. I came across your "
                                                             "job posting. Email me at a@b.com or WhatsApp +880 1711 000000."}]))
        self.assertTrue(has(res, "errors", "contact details"))
        self.assertTrue(has(res, "warnings", "proposal template phrase"))

    def test_linkedin_note_limits(self):
        res = lint(doc("linkedin-note", [{"role": "body", "text": "Hi, connect? " + "x" * 300 + " https://a.com"}]))
        self.assertTrue(has(res, "errors", "300 at most"))
        self.assertTrue(has(res, "errors", "links are not allowed"))


class Products(unittest.TestCase):
    def test_amazon_weak_listing(self):
        res = lint(doc("amazon", [
            {"role": "title", "text": "BEST Premium Wireless Earbuds Bluetooth Earbuds Earbuds Headphones Perfect Gift!!"},
            {"role": "bullet", "text": "Eco-friendly case with anti-bacterial tips, approx. 5 g"},
            {"role": "search_terms", "text": "best earbuds brandco"}], brand="BrandCo"))
        errs = " | ".join(res["errors"])
        for needle in ("75 at most", "character '!'", "'earbuds' appears more than 2", "ALL CAPS",
                       "banned in Amazon bullets", "'best' is not allowed", "no brand names"):
            self.assertIn(needle, errs)
        self.assertTrue(has(res, "warnings", "abbreviation"))

    def test_amazon_strong_listing(self):
        res = lint(doc("amazon", [
            {"role": "title", "text": "BrandCo Wireless Earbuds, Bluetooth 5.3, 30-Hour Case, IPX4, Black",
             "claims": ["brief"]},
            {"role": "bullet", "text": "Battery: 7 hours per charge, 30 with the case, at 50% volume", "claims": ["brief"]},
            {"role": "bullet", "text": "Fits: iPhone 15 and 15 Pro; not 15 Plus or Pro Max", "claims": ["brief"]},
            {"role": "bullet", "text": "Includes: 2 earbuds, charging case, USB-C cable", "claims": ["brief"]}],
            brand="BrandCo"))
        self.assertTrue(res["ok"], res["errors"])

    def test_marketplace_bans_and_restated_title(self):
        res = lint(doc("ebay", [{"role": "title", "text": "Walnut Cutting Board Free Shipping Sale $20"},
                                {"role": "description", "text": "Walnut cutting board free shipping sale. Call 01711000000"}]))
        self.assertTrue(has(res, "errors", "'free shipping' is banned"))
        self.assertTrue(has(res, "errors", "no URLs, emails or phone numbers"))
        self.assertTrue(has(res, "errors", "no price in the title"))
        res = lint(doc("walmart", [{"role": "title", "text": "BrandCo Stoneware Plates, Set of 4", "claims": ["brief"]},
                                   {"role": "key_feature", "text": "BrandCo Stoneware Plates, Set of 4"},
                                   {"role": "description", "text": "- one\n- two"}]))
        self.assertTrue(has(res, "errors", "one paragraph"))
        self.assertTrue(has(res, "warnings", "restates the title"))

    def test_bangladesh_f_commerce(self):
        weak = lint(doc("fb-shop", [{"role": "caption", "text": "১০০% খাঁটি সুন্দরবনের মধু, সেরা মানের! রোগ প্রতিরোধ "
                                                                "ক্ষমতা বাড়ায়। দাম জানতে ইনবক্স করুন!!"}], lang="bn"))
        self.assertTrue(has(weak, "errors", "disease or drug claim"))
        self.assertTrue(has(weak, "errors", "hidden behind the inbox"))
        self.assertTrue(has(weak, "warnings", "boast buyers cannot check"))
        self.assertTrue(has(weak, "warnings", "no price shown"))
        strong = lint(doc("fb-shop", [{"role": "caption", "claims": ["brief"], "text":
                                       "সুন্দরবনের খলিশা ফুলের কাঁচা মধু, ৫০০ গ্রাম। দাম ৳৬৫০। ঢাকার ভেতরে ডেলিভারি ৳৬০, "
                                       "ক্যাশ অন ডেলিভারি।"}], lang="bn"))
        self.assertTrue(strong["ok"], strong["errors"])
        self.assertFalse(has(strong, "warnings", "price"))


class Counting(unittest.TestCase):
    def test_x_counts_links_as_23(self):
        self.assertEqual(L.x_length("see https://example.com/a/very/long/path/indeed"), 4 + 23)

    def test_sms_parts(self):
        self.assertEqual(L.sms_parts("a" * 160), 1)
        self.assertEqual(L.sms_parts("a" * 161), 2)
        self.assertEqual(L.sms_parts("ক" * 70), 1)
        self.assertEqual(L.sms_parts("ক" * 71), 2)

    def test_grade(self):
        self.assertLess(L.grade("Snap each receipt as you pay. We file it for you. Tax day is quiet now."), 4)
        self.assertGreater(L.grade("Leveraging comprehensive organizational infrastructure facilitates unprecedented "
                                   "operational optimization across multidimensional enterprise environments."), 14)
        self.assertIsNone(L.grade("আমি যাব। তুমি আসবে।"))


class Commands(unittest.TestCase):
    def test_new_render_and_never_overwrite(self):
        d = TMP / "proj"
        code, out = run(["new", str(d), "--type", "amazon", "--lang", "en", "--brand", "BrandCo"])
        self.assertEqual(code, 0)
        data = json.loads((d / "copy.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(1 for f in data["variants"][0]["fields"] if f["role"] == "bullet"), 3)
        self.assertEqual(run(["new", str(d), "--type", "amazon"])[0], 2)
        code, out = run(["new", str(TMP / "ads"), "--type", "meta-feed"])
        self.assertEqual(out["variants"], 3)
        code, out = run(["render", str(d / "copy.json")])
        self.assertTrue((d / "copy.md").exists())

    def test_lint_cli_without_voice(self):
        p = write("cli/caption.txt", "This tea cures diabetes.")
        code, out = run(["lint", p, "--type", "facebook", "--no-voice", "--json"])
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])

    def test_voice_pass_reports_a_missing_design_tool(self):
        old = L.DESIGN
        L.DESIGN = TMP / "missing-design.py"
        try:
            self.assertFalse(L.voice_pass(doc("facebook", [{"role": "caption", "text": "Hello"}]))["ran"])
        finally:
            L.DESIGN = old

    def test_review_commands_with_fake_models(self):
        os.environ["NEXA_LLM_FAKE"] = "1"
        try:
            brief = write("rv/brief.json", {"product": "tea", "reader": {"who": "office workers"}})
            fields = [{"role": "primary", "text": "Tea that stays hot through your 9 am call."},
                      {"role": "headline", "text": "Hot at 9, hot at 11"}]
            f = write("rv/copy.json", {"schema": "nexa.copy/1", "meta": {"type": "meta-feed", "lang": "en"},
                                       "variants": [{"id": "A", "angle": "time", "fields": fields},
                                                    {"id": "B", "angle": "taste", "fields": fields[:1]}]})
            code, out = run(["judge", f, "--brief", brief, "--runs", "1", "--roster", "codex,gemini:x"])
            self.assertEqual(out["variant"], "A")
            self.assertTrue((TMP / "rv" / "judge-A.json").exists())
            code, out = run(["panel", "build", str(TMP / "rv"), "--brief", brief, "--n", "10"])
            self.assertGreater(out["personas"], 0)
            code, out = run(["panel", "run", f, "--panel", str(TMP / "rv" / "panel.json"), "--variant", "B"])
            self.assertEqual(out["variant"], "B")
            pack = write("rv/pack.json", {"competitors": [{"hook": "Cold tea again?", "result": "2.1M views"}]})
            code, out = run(["hooks", f, "--pack", pack])
            self.assertEqual((out["draft"], out["real"]), (2, 1))
            code, out = run(["tournament", f, "--brief", brief, "--roster", "codex"])
            self.assertEqual(len(out["ranking"]), 2)
            code, out = run(["prefer", f, f, "--panel", str(TMP / "rv" / "panel.json")])
            self.assertIn("clears", out)
        finally:
            os.environ.pop("NEXA_LLM_FAKE", None)


class SharedModules(unittest.TestCase):
    def test_copies_match_nexa_script(self):
        other = SCRIPTS.parent.parent / "nexa-script" / "scripts"
        for module in ("nexa_llm.py", "nexa_review.py", "gemini_api.py"):
            if (other / module).exists():
                self.assertEqual((other / module).read_bytes(), (SCRIPTS / module).read_bytes(), module)


if __name__ == "__main__":
    unittest.main()
