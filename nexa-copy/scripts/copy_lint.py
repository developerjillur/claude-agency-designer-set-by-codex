"""nexa-copy rules: field limits per platform, claims and compliance, email and outbound mechanics, marketplace rules,
Bangladesh f-commerce, and the natural-text voice pass (codex-design copylint) on every field.

Findings name their research note: R5 conversion copywriting, R6 email and outbound, R7 product copy
(references/research/, 2026-09-26). Errors block delivery; warnings are fixed or argued with a reason; notes are
read. A gate is a warning in a draft and an error in a final.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nexa_review as R  # noqa: E402

PLATFORMS = HERE.parent / "references" / "platforms.json"
DESIGN = Path(os.environ.get("NEXA_DESIGN_PY", str(Path.home() / ".claude/skills/codex-design/scripts/design.py")))
EM, EN = chr(0x2014), chr(0x2013)

# ------------------------------------------------------------------------------------------------ word lists

# R5 §9 and R7 §7: praise that says nothing (the natural-text voice pass adds its own 932 rules on top)
PUFFERY = ["premium quality", "high-quality materials", "high quality", "perfect for any occasion", "perfect gift",
           "must-have", "must have", "next level", "next-level", "ultimate", "revolutionary", "revolutionize",
           "designed with you in mind", "crafted with care", "timeless", "effortless", "unleash", "boasts",
           "cutting-edge", "cutting edge", "world-class", "world class", "best-in-class", "supercharge", "empower",
           "tailored solutions", "state-of-the-art", "one-stop", "leverage", "streamline", "robust"]
OPENERS = ["introducing", "elevate your", "experience the", "discover the", "discover our", "say goodbye to",
           "look no further", "are you tired of", "ready to", "imagine a world", "picture this", "have you ever",
           "what if i told you", "in today's", "whether you're"]
# R6 §10: what buyers and clients read as a template
EMAIL_TELLS = ["i hope this email finds you well", "hope this finds you well", "hope you're doing well",
               "hope you are doing well", "i came across your", "just following up", "just checking in", "bumping this",
               "i wanted to reach out", "reaching out because", "sorry to bother you", "circling back", "touching base",
               "i'd love to hop on a call", "let me know if you're interested", "looking forward to hearing from you"]
# R6 6.1: a time or meeting ask on a first cold touch (Gong: specific times book 15 % cold against 37 % in active deals)
MEETING_ASK = re.compile(r"(\b\d{1,2}[- ]?(minute|min)\b.{0,20}\b(call|chat|meeting)|\b(book|schedule|hop on) a (call|meeting|"
                         r"demo)|\bnext (monday|tuesday|wednesday|thursday|friday)\b|calendly|\bmy calendar\b)", re.I)
PROPOSAL_TELLS = ["dear sir", "dear madam", "dear hiring manager", "i'm passionate about", "i am passionate about",
                  "i came across your job", "i have read your job", "i read your job post", "i am an expert",
                  "i'm an expert", "i am the perfect", "i'm the perfect"]
# claims that need a ledger row (R5 §7, §11.3; R7 §5)
CLAIM = re.compile(
    r"(\d[\d,.]*\s?(%|x\b|times\b)|[$€£৳₹]\s?\d|\b\d[\d,.]*\s?(taka|tk|rupees?|dollars?)\b|"
    r"(?<!\w)#1\b|\b(best|number one|no\.? ?1|leading|top[- ]rated|fastest|cheapest|lowest|most popular|award|certified|"
    r"clinically|dermatologist|doctor[- ]recommended|fda|proven|guarantee[ds]?|free|faster than|better than|"
    r"cheaper than|studies|study|research shows|reviews?|rated|stars?)\b|"
    r"টাকা|৳|সেরা|শতভাগ|১০০%|গ্যারান্টি|প্রমাণিত|ফ্রি|বিনামূল্যে)", re.I)
DISEASE = re.compile(
    r"\b(cure[sd]?|heals?|treats?|prevents?|reverses?)\b.{0,40}\b(diabetes|cancer|arthritis|covid|depression|obesity|"
    r"flu|infection|disease|hypertension|asthma)\b|\b(anti-?bacterial|anti-?microbial|anti-?fungal)\b|"
    r"ডায়াবেটিস|ক্যান্সার|রোগ প্রতিরোধ|রোগ সারায়|রোগ সারে|ওষুধের মতো", re.I)
ECO = re.compile(r"\b(eco-?friendly|environmentally friendly|ecologically friendly|climate[- ]friendly|"
                 r"climate[- ]neutral|carbon[- ]neutral|biodegradable|compostable|green product|planet[- ]friendly|"
                 r"sustainable|all[- ]natural|100% natural)\b|পরিবেশবান্ধব", re.I)
URGENCY = ["last chance", "ends soon", "ending soon", "only today", "today only", "limited time", "hurry",
           "while stocks last", "don't miss", "closing soon", "only a few left", "almost gone", "shesh shujog",
           "শেষ সুযোগ", "সীমিত সময়", "তাড়াতাড়ি করুন", "স্টক সীমিত", "আজই শেষ"]
MARKETPLACE_BANNED = ["best seller", "bestseller", "best-selling", "top rated", "top-rated", "hot item", "hot sale",
                      "free shipping", "on sale", "sale", "discount", "limited time", "cheap", "lowest price",
                      "#1", "number one", "premium quality", "clearance", "buy now", "order now", "savings",
                      "5 star", "five star", "guaranteed", "money-back"]
AMAZON_BULLET_BANNED = ["eco-friendly", "environmentally friendly", "ecologically friendly", "anti-microbial",
                        "antimicrobial", "anti-bacterial", "antibacterial", "made from bamboo", "contains bamboo",
                        "made from soy", "contains soy", "guarantee", "n/a", "tbd"]
AMAZON_SEARCH_BANNED = ["best", "cheapest", "amazing", "popular", "new", "on sale", "sale", "top"]
ABBREVIATIONS = re.compile(r"\b(qty|pkg|approx\.)|\bw/", re.I)
BD_HIDDEN_PRICE = ["দাম জানতে ইনবক্স", "ইনবক্সে দাম", "দাম জানতে মেসেজ", "প্রাইস জানতে ইনবক্স", "price in inbox",
                   "inbox for price", "dm for price", "dam jante inbox"]
BD_BOASTS = ["১০০% অরিজিনাল", "১০০% খাঁটি", "সেরা মানের", "100% original", "100% pure", "১০০% গ্যারান্টি"]
GENERIC_BUTTONS = ["learn more", "click here", "submit", "sign up", "get started", "read more", "click now"]
NOT_X_ITS_Y = re.compile(r"\b(it'?s |this is |that'?s )?not (just |only |about )?[^.,;!?]{1,40}[,;:] ?(it'?s|but|it is)"
                         r"\b", re.I)
TRIPLET = re.compile(r"\b([A-Za-z]{3,15}), ([A-Za-z]{3,15}),? and ([A-Za-z]{3,15})\b")
LINK = re.compile(r"(https?://\S+|www\.\S+|\b[\w-]+\.(com|net|org|io|co|bd|in|ai|app|me|ly)(/\S*)?\b)", re.I)
EMAIL_ADDR = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
PHONE = re.compile(r"(\+?\d[\d\s().-]{8,}\d)")
CONTACT_WORDS = re.compile(r"\b(whatsapp|skype|telegram|calendly|cal\.com|call me at|text me|my number|my email)\b", re.I)
MERGE_TAG = re.compile(r"(\{\{?\s*\w+\s*\}?\}|\[(first ?name|name|company|x|y|n|date|product|link)\]|\{first_name\})",
                       re.I)
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF]")
HASHTAG = re.compile(r"(?<![\w&])#\w+")
MENTION = re.compile(r"(?<![\w.])@\w+")
YOU = re.compile(r"\b(you|your|you're|yours)\b", re.I)
ME = re.compile(r"\b(i|i'm|i've|me|my|we|we're|our|us)\b", re.I)
STOP = {"a", "an", "and", "the", "for", "of", "with", "to", "in", "on", "or", "by", "at", "from", "&"}
ACRONYMS = {"USB", "LED", "LCD", "HDMI", "GSM", "SPF", "UV", "USA", "UK", "EU", "BPA", "PVC", "RAM", "SSD", "HD",
            "FHD", "UHD", "IPX", "DIN", "ISO", "AC", "DC", "LTE", "NFC", "CPU", "GPU", "OEM", "PDF", "SEO", "API",
            "B2B", "B2C", "CTA", "ROI", "FAQ", "BD", "DSLR", "LLC", "USD", "BDT", "COD", "SAAS"}


def words(text):
    return re.findall(r"[\wঀ-৿ऀ-ॿ'’%$৳₹.-]+", text or "")


def phrase_hits(text, phrases):
    """Phrases found as whole words (any script); a phrase inside a longer hit is reported once."""
    low = (text or "").lower()
    found = {}
    for p in phrases:
        key = p.lower()
        if (key.isascii() and re.search(r"(?<![\w])" + re.escape(key) + r"(?![\w])", low)) or \
                (not key.isascii() and key in low):
            found[key] = p
    out = []
    for key, p in sorted(found.items(), key=lambda kv: -len(kv[0])):
        if not any(key in longer.lower() for longer in out):
            out.append(p)
    return out


def load_platforms():
    return json.loads(PLATFORMS.read_text(encoding="utf-8"))


def x_length(text):
    """X counts a URL as 23 and an emoji or a CJK character as 2."""
    t = LINK.sub("x" * 23, text or "")
    return sum(2 if (EMOJI.match(ch) or "一" <= ch <= "鿿" or "぀" <= ch <= "ヿ") else 1 for ch in t)


def sms_parts(text):
    """GSM text: 160 characters, 153 a part when split; Bengali and other UCS-2 text: 70, 67 a part."""
    ucs = any(ord(ch) > 127 for ch in text or "")
    single, multi = (70, 67) if ucs else (160, 153)
    n = len(text or "")
    return 1 if n <= single else -(-n // multi)


def syllables(word):
    w = word.lower().strip(".,;:!?\"'")
    if not w:
        return 0
    groups = re.findall(r"[aeiouy]+", w)
    n = len(groups) - (1 if w.endswith("e") and len(groups) > 1 else 0)
    return max(1, n)


def grade(text):
    """Flesch-Kincaid grade for English text (None for other scripts or under 12 words)."""
    sents = [s for s in R.split_sentences(text or "") if s.strip()]
    ws = re.findall(r"[A-Za-z']+", text or "")
    if not sents or len(ws) < 12 or re.search(r"[ঀ-৿ऀ-ॿ]", text or ""):
        return None
    syl = sum(syllables(w) for w in ws)
    return round(0.39 * len(ws) / len(sents) + 11.8 * syl / len(ws) - 15.59, 1)


class Findings:
    def __init__(self, level):
        self.level = level
        self.errors, self.warnings, self.notes = [], [], []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def note(self, msg):
        self.notes.append(msg)

    def gate(self, msg):
        (self.errors if self.level == "final" else self.warnings).append(msg)


# ------------------------------------------------------------------------------------------------- loading

def load_copy(path, ctype=None, lang=None):
    """A copy.json (`nexa.copy/1`) or a plain text file (one field: the body or caption of `ctype`)."""
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".json":
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError(f"a copy.json is an object with meta and variants, not a {type(data).__name__}")
        meta = dict(data.get("meta") or {})
        if ctype:
            meta["type"] = ctype
        if lang:
            meta["lang"] = lang
        variants = data.get("variants") or [{"id": "A", "fields": data.get("fields") or []}]
        return {"meta": meta, "variants": variants, "test_plan": data.get("test_plan") or {}, "raw": data,
                "path": str(p)}
    platforms = load_platforms()["types"]
    t = ctype or "facebook"
    fields = platforms.get(t, {}).get("fields", {})
    role = "caption" if "caption" in fields else "body" if "body" in fields else next(iter(fields), "body")
    meta = {"type": t, "lang": lang or ("bn" if re.search(r"[ঀ-৿]", raw) else "en")}
    return {"meta": meta, "variants": [{"id": "A", "fields": [{"role": role, "text": raw.strip()}]}],
            "test_plan": {}, "path": str(p)}


def doc_text(doc, variant=None):
    """The copy as a reader meets it, field by field."""
    out = []
    for v in doc["variants"]:
        if variant and v.get("id") != variant:
            continue
        out += [x.get("text", "") for x in v.get("fields") or [] if x.get("role") not in ("search_terms", "tag")]
        if variant is None:
            break
    return "\n".join(t for t in out if t)


# ------------------------------------------------------------------------------------------------- checks

def check_field(f, spec, fld, ctx):
    text, tag = fld.get("text") or "", ctx["tag"]
    n_chars = x_length(text) if spec.get("x_counting") else len(text)
    n_words = len(words(text))
    if spec.get("max_chars") and n_chars > spec["max_chars"]:
        f.error(f"{tag}: {n_chars} characters; {spec['max_chars']} at most")
    if spec.get("min_chars") and 0 < n_chars < spec["min_chars"]:
        f.error(f"{tag}: {n_chars} characters; {spec['min_chars']} at least")
    rc = spec.get("rec_chars")
    if rc and text and not rc[0] <= n_chars <= rc[1]:
        f.warn(f"{tag}: {n_chars} characters; {rc[0]} to {rc[1]} recommended")
    if spec.get("max_words") and n_words > spec["max_words"]:
        f.error(f"{tag}: {n_words} words; {spec['max_words']} at most")
    if spec.get("min_words") and n_words < spec["min_words"]:
        f.warn(f"{tag}: {n_words} words; {spec['min_words']} at least")
    rw = spec.get("rec_words")
    if rw and text and not rw[0] <= n_words <= rw[1]:
        f.warn(f"{tag}: {n_words} words; {rw[0]} to {rw[1]} for this type")
    if spec.get("max_bytes") and len(text.encode("utf-8")) > spec["max_bytes"]:
        f.error(f"{tag}: {len(text.encode('utf-8'))} bytes; {spec['max_bytes']} at most")
    if spec.get("max_sentences") and len(R.split_sentences(text)) > spec["max_sentences"]:
        f.warn(f"{tag}: {len(R.split_sentences(text))} sentences; {spec['max_sentences']} at most")
    if spec.get("fold_chars") and len(text) > spec["fold_chars"]:
        f.note(f"{tag}: the fold is {spec['fold_chars']} characters; the sale must land in: "
               f"'{text[:spec['fold_chars']]}'")
    tags = HASHTAG.findall(text)
    if spec.get("no_hashtags") and tags:
        f.error(f"{tag}: hashtags are not allowed here")
    if spec.get("max_hashtags") is not None and len(tags) > spec["max_hashtags"]:
        f.warn(f"{tag}: {len(tags)} hashtags; {spec['max_hashtags']} at most (they label, they add no reach; R5 6.4)")
    if spec.get("no_mentions") and MENTION.search(text):
        f.error(f"{tag}: @ mentions are not allowed here")
    if spec.get("no_links") and LINK.search(text):
        f.error(f"{tag}: links are not allowed here")
    if spec.get("no_emoji") and EMOJI.search(text):
        f.error(f"{tag}: emoji are not allowed here")
    for ch in spec.get("banned_chars") or "":
        if ch in text:
            f.error(f"{tag}: the character '{ch}' is not allowed ({ctx['label']})")
    if spec.get("max_word_repeat"):
        counts = {}
        for w in re.findall(r"[\w'-]+", text.lower()):
            if w not in STOP:
                counts[w] = counts.get(w, 0) + 1
        over = [w for w, k in counts.items() if k > spec["max_word_repeat"]]
        if over:
            f.error(f"{tag}: '{over[0]}' appears more than {spec['max_word_repeat']} times (R7 2.2)")
    if spec.get("one_paragraph") and re.search(r"\n\s*\n|^\s*[-*•]", text, re.M):
        f.error(f"{tag}: one paragraph, no bullets (R7 2.7)")
    if spec.get("sms_parts"):
        parts = sms_parts(text)
        if parts > 1:
            f.note(f"{tag}: {parts} SMS parts (Bengali and other Unicode text fits 70 characters in one part)")


def check_words(f, text, tag, ctx):
    if EM in text or re.search(r"\s" + EN + r"\s", text):
        f.error(f"{tag}: an em dash or a spaced en dash")
    for p in phrase_hits(text, PUFFERY):
        f.warn(f"{tag}: empty praise ('{p}'): the fact instead (R5 9, R7 7)")
    first = (R.split_sentences(text) or [""])[0].lower()
    for p in OPENERS:
        if first.startswith(p):
            f.warn(f"{tag}: a template opener ('{p}'): start at the reader's moment (R5 9)")
            break
    if NOT_X_ITS_Y.search(text) and ctx["lang"] in ("en", "banglish"):
        f.warn(f"{tag}: a 'not X, it's Y' frame: say Y (R5 9)")
    m = TRIPLET.search(text)
    if m and ctx["family"] in ("ad", "post", "product", "landing"):
        f.note(f"{tag}: a list of three ('{m.group(0)}'): one specific beats three vague words (R5 9)")
    if text.count("!") > 1:
        f.warn(f"{tag}: {text.count('!')} exclamation marks; one at most (R5 11.3)")
    caps = [w for w in re.findall(r"\b[A-Z]{4,}\b", text) if w not in ACRONYMS]
    if caps:
        (f.error if ctx["family"] == "product" else f.warn)(f"{tag}: ALL CAPS ('{caps[0]}')")
    if MERGE_TAG.search(text):
        f.gate(f"{tag}: a merge tag or placeholder is still in the copy ('{MERGE_TAG.search(text).group(0)}')")
    for marker in ("NEEDS INPUT", "PROOF NEEDED"):
        if marker in text:
            f.gate(f"{tag}: a [{marker}] marker is still in the copy")


def check_claims(f, text, fld, tag, ctx):
    claims = fld.get("claims") or []
    m = CLAIM.search(text)
    if m and not claims:
        f.gate(f"{tag}: a claim with no ledger row ('{m.group(0).strip()}'): add its claim id, or 'brief' for a "
               "client fact (R5 7)")
    for cid in claims:
        if cid == "brief" or str(cid).startswith("brief:") or ctx["pack"] is None:
            continue
        x = ctx["claims"].get(cid)
        if not x:
            f.error(f"{tag}: claim {cid} is not in the research pack")
        elif x.get("status") not in ("verified", "manual"):
            f.gate(f"{tag}: claim {cid} is {x.get('status')}, not verified")
    m = DISEASE.search(text)
    if m and ctx["family"] in ("ad", "product", "post", "email", "landing"):
        f.error(f"{tag}: a disease or drug claim ('{m.group(0)}'): marketplaces and ad policies ban it; in Bangladesh "
                "false advertising is an offence (R7 5)")
    m = ECO.search(text)
    if m and not claims:
        f.gate(f"{tag}: a generic green claim ('{m.group(0)}'): banned in the EU from 2026-09-27 without proof; "
               "write the scoped fact (R5 7, R7 5)")
    if re.search(r"\bmade in\b", text, re.I) and not claims:
        f.gate(f"{tag}: an origin claim ('made in'): needs the attestation in the brief (R7 5)")
    for p in phrase_hits(text, URGENCY):
        if not re.search(r"[\d০-৯]", text) and not ctx["meta"].get("deadline"):
            f.warn(f"{tag}: urgency ('{p}') with no date or stock count: real deadlines only (R5 2.7)")


def check_email(f, fields, ctx):
    rules = ctx["rules"]
    body = " ".join(x.get("text", "") for x in fields if x.get("role") in ("body", "caption"))
    subject = next((x.get("text", "") for x in fields if x.get("role") == "subject"), "")
    everything = " ".join(x.get("text", "") for x in fields)
    tag = ctx["vtag"]
    if subject:
        if re.match(r"\s*(re|fwd?)\s*:", subject, re.I) and not ctx["meta"].get("is_reply"):
            f.error(f"{tag}: a fake 'Re:' or 'Fwd:' subject is deceptive (CAN-SPAM, Gmail; R6 7)")
        if "quick question" in subject.lower():
            f.warn(f"{tag}: 'Quick question' subjects underperform (Hunter: 2.5 % replies against 2.9 %; R6 2)")
        if ctx["family"] == "outbound" and (EMOJI.search(subject) or "!!" in subject):
            f.warn(f"{tag}: no emoji or '!!' in a B2B subject (R6 11)")
    if rules.get("needs_preview") and not any(x.get("role") == "preview" and x.get("text") for x in fields):
        f.gate(f"{tag}: no preview text: without it the client shows 'View in browser' (R6 2)")
    links = LINK.findall(body)
    if rules.get("no_links") and links:
        if ctx["type"] == "email-cold":
            f.error(f"{tag}: a link in a first cold touch: none in the first email, at most one later (R6 3)")
        else:
            f.error(f"{tag}: links are not allowed in a {ctx['label']} (R6 9)")
    if rules.get("max_links") is not None and len(links) > rules["max_links"]:
        f.warn(f"{tag}: {len(links)} links; {rules['max_links']} at most")
    lo_hi = rules.get("links")
    n_all = len(LINK.findall(everything))
    if lo_hi and not lo_hi[0] <= n_all <= lo_hi[1]:
        f.note(f"{tag}: {n_all} links; {lo_hi[0]} to {lo_hi[1]} did best (MailerLite; R6 3)")
    q = body.count("?")
    if rules.get("must_end_question") and q == 0:
        f.warn(f"{tag}: a cold email ends on a soft interest question ('Worth a look?'; R6 6.1)")
    if rules.get("max_questions") and q > rules["max_questions"]:
        f.warn(f"{tag}: {q} questions; {rules['max_questions']} at most")
    if rules.get("you_over_i"):
        core = " ".join(x for x in R.split_sentences(body) if not re.search(r"(reply ['\"]?(no|stop)|won'?t follow up|"
                                                                          r"unsubscribe|opt[- ]out)", x, re.I))
        you, me = len(YOU.findall(core)), len(ME.findall(core))
        if me > you + 1:
            f.note(f"{tag}: {me} I/we against {you} you/your: make the reader's world the subject (R6 11)")
    if ctx["type"] == "email-cold" and MEETING_ASK.search(body):
        f.warn(f"{tag}: a meeting or time ask on a first cold touch ('{MEETING_ASK.search(body).group(0)}'): ask for "
               "interest instead ('Worth a look?'; R6 6.1)")
    first = re.sub(r"^\s*(hi|hello|hey|dear)\s+[^,.!?\n]{1,30}[,!.]?\s*", "",
                   (R.split_sentences(body) or [""])[0], flags=re.I)
    if ctx["family"] == "outbound" and re.match(r"\s*(i\b|i'm\b|my name is)", first, re.I):
        f.warn(f"{tag}: the first sentence starts with the sender: open with the premise (R6 11)")
    for p in phrase_hits(everything, EMAIL_TELLS):
        f.warn(f"{tag}: a template phrase ('{p}'; R6 10)")
    low = everything.lower()
    footer = ctx["meta"].get("footer_by_tool")
    if rules.get("needs_unsubscribe") and "unsubscribe" not in low and not footer:
        f.gate(f"{tag}: no unsubscribe link (Gmail and Yahoo bulk rules, CAN-SPAM; R6 3, 7); set meta.footer_by_tool "
               "when the email tool adds it")
    if rules.get("needs_address") and not footer and not ctx["meta"].get("address") and \
            not re.search(r"\d+\s*,?\s*[\w .]*(road|street|st\.|avenue|ave|lane|house|suite|floor|po box|rd\.?)\b", low):
        f.gate(f"{tag}: no postal address (CAN-SPAM for commercial email; R6 7); set meta.address or "
               "meta.footer_by_tool")
    if rules.get("needs_optout") and not re.search(r"(reply ['\"]?(no|stop)|opt[- ]out|unsubscribe|won'?t follow up|"
                                                  r"not relevant\?|i'?ll stop)", low):
        f.gate(f"{tag}: no opt-out line ('Not relevant? Reply no and I won't follow up'; R6 7)")
    if (ctx["meta"].get("region") or "").upper() in ("EU", "UK") and ctx["family"] == "outbound" \
            and not re.search(r"(privacy|object|your data|delete your details)", low):
        f.gate(f"{tag}: EU and UK prospects get a privacy link and the right-to-object line in the first message "
               "(GDPR Art. 14, 21; R6 7)")


def check_outbound(f, fields, ctx):
    tag = ctx["vtag"]
    everything = " ".join(x.get("text", "") for x in fields)
    if ctx["rules"].get("no_contact_details"):
        if EMAIL_ADDR.search(everything) or PHONE.search(everything) or CONTACT_WORDS.search(everything):
            f.error(f"{tag}: contact details before a contract break Upwork's rules (R6 8)")
    if ctx["type"].startswith("proposal"):
        for p in phrase_hits(everything, PROPOSAL_TELLS):
            f.warn(f"{tag}: a proposal template phrase ('{p}'): open with the client's goal in their words (R6 8)")


def check_product(f, fields, ctx):
    tag, t = ctx["vtag"], ctx["type"]
    market = ctx["rules"].get("marketplace")
    by_role = {}
    for x in fields:
        by_role.setdefault(x.get("role"), []).append(x.get("text") or "")
    for role, texts in by_role.items():
        for text in texts:
            if market and role != "search_terms":
                for p in phrase_hits(text, MARKETPLACE_BANNED):
                    f.error(f"{tag} {role}: '{p}' is banned in marketplace fields (a promo, boast, price or time word; "
                            "R7 2)")
                if LINK.search(text) or EMAIL_ADDR.search(text) or PHONE.search(text):
                    f.error(f"{tag} {role}: no URLs, emails or phone numbers in marketplace fields (R7 2.2)")
                if re.search(r"[$€£৳₹]\s?\d", text) and role in ("title", "bullet", "highlights"):
                    f.error(f"{tag} {role}: no price in the title or bullets (R7 2)")
            if role == "title" and ":" in text and market:
                f.warn(f"{tag} title: a colon in a product title: Google's own AI-title sample shows the pun-plus-colon "
                       "pattern (R7 2.3)")
    if t == "amazon":
        for text in by_role.get("bullet", []):
            for p in phrase_hits(text, AMAZON_BULLET_BANNED):
                f.error(f"{tag} bullet: '{p}' is banned in Amazon bullets (R7 2.2)")
            if ABBREVIATIONS.search(text):
                f.warn(f"{tag} bullet: an abbreviation ('{ABBREVIATIONS.search(text).group(0)}'): spell it out")
            if not re.match(r"[^:]{2,40}:", text):
                f.note(f"{tag} bullet: Amazon's form is 'Header: description' ('{text[:40]}')")
            if text.rstrip().endswith("."):
                f.note(f"{tag} bullet: Amazon bullets are fragments without end punctuation")
        for text in by_role.get("search_terms", []):
            for p in phrase_hits(text, AMAZON_SEARCH_BANNED):
                f.error(f"{tag} search_terms: '{p}' is not allowed (subjective or temporary; R7 2.2)")
            brand = (ctx["meta"].get("brand") or "").lower()
            if brand and brand in text.lower():
                f.error(f"{tag} search_terms: no brand names in search terms (R7 2.2)")
    title = (by_role.get("title") or [""])[0]
    first_bullet = (by_role.get("bullet") or by_role.get("key_feature") or by_role.get("highlight") or [""])[0]
    if title and first_bullet and R.overlap(first_bullet, [title], n=3) > 0.5:
        f.warn(f"{tag}: the first bullet restates the title (R7 7)")
    seen = {}
    for texts in by_role.values():
        for text in texts:
            for num, unit in re.findall(r"(\d+(?:\.\d+)?)\s?(ml|l|g|kg|cm|mm|in|inch|w|mah|gb|tb|oz|lb)\b", text, re.I):
                seen.setdefault(unit.lower(), set()).add(num)
    mixed = [u for u, nums in seen.items() if len(nums) > 1]
    if mixed:
        f.note(f"{tag}: '{mixed[0]}' appears with {sorted(seen[mixed[0]])}: check the facts match across fields (R7 10)")


def check_bd_commerce(f, fields, ctx):
    tag = ctx["vtag"]
    text = " ".join(x.get("text", "") for x in fields)
    for p in phrase_hits(text, BD_HIDDEN_PRICE):
        f.error(f"{tag}: the price is hidden behind the inbox ('{p}'): show it with ৳ (disclosure duties; R7 6)")
    for p in phrase_hits(text, BD_BOASTS):
        f.warn(f"{tag}: '{p}' is a boast buyers cannot check: write the origin, batch date, warranty or size chart "
               "instead (R7 6)")
    if not re.search(r"(৳|টাকা|\btk\b|\btaka\b)\s?[\d০-৯]|[\d০-৯]\s?(৳|টাকা|\btk\b|\btaka\b)", text, re.I):
        f.warn(f"{tag}: no price shown (৳): buyers need it in the post (R7 6)")
    if not re.search(r"(ডেলিভারি|delivery|ক্যাশ অন|cash on delivery|\bcod\b)", text, re.I):
        f.note(f"{tag}: no delivery terms: the charge inside and outside Dhaka, the time, COD and returns (R7 6)")


def check_variants(f, doc, ctx):
    vs = doc["variants"]
    if ctx["family"] == "ad":
        if len(vs) < 3:
            (f.errors if f.level == "final" else f.notes).append(
                f"{len(vs)} variants: an ad ships 3 to 5 angles that differ in pain, desire or mechanism (R5 11.1 rule 3)")
        angles = [(v.get("angle") or "").strip().lower() for v in vs if (v.get("angle") or "").strip()]
        if len(set(angles)) < len(angles):
            f.warn("two variants share an angle: vary the pain, the desire or the mechanism, not the wording")
        texts = [" ".join(x.get("text", "") for x in v.get("fields") or []) for v in vs]
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                if texts[i] and texts[j] and R.overlap(texts[j], [texts[i]], n=3) > 0.4:
                    f.warn(f"variants {vs[i].get('id')} and {vs[j].get('id')} share most of their wording: that is one "
                           "angle twice (R5 5)")
        if f.level == "final" and not (doc.get("test_plan") or {}).get("hypothesis"):
            f.gate("no test plan: a hypothesis (angle A against angle B), the metric and the sample (copy.py sample; "
                   "R5 11.5)")


GENERIC = {"that", "this", "with", "from", "have", "your", "about", "another", "will", "what", "when", "they", "their",
           "there", "which", "into", "just", "really", "thing", "things", "people", "product", "more", "some", "than",
           "then", "them", "these", "those", "would", "could", "should", "been", "being", "does", "make", "made", "also",
           "only", "very", "much", "many", "most", "such", "like", "want", "wants", "know", "buy", "buys", "other",
           "brand", "order"}
BN_GENERIC = {"কি", "কী", "না", "তো", "এই", "আর", "ও", "যে", "কেন", "হয়", "করে", "থেকে", "একটা", "আমি", "আপনি",
              "তারা", "এটা", "সেটা", "কিন্তু", "তবে", "জন্য", "দিয়ে"}


def content_words(text):
    return [w for w in re.findall(r"[a-z]{4,}|[\u0980-\u09ff]{3,}", (text or "").lower())
            if w not in GENERIC and w not in BN_GENERIC]


def mentions(text, word):
    low = (text or "").lower()
    return word in low or (word.isascii() and len(word) > 6 and word[:6] in low)


def check_brief(f, doc, brief):
    """Every objection in the brief answered, the reader's situation touched, the brief's action asked for, its bans
    kept (the 2026-09-26 benchmark: a draft that read as a list of specifications lost 0 to 3 to one that voiced the
    reader's worry first)."""
    reader = brief.get("reader") or {}
    for v in doc["variants"]:
        tag = f"variant {v.get('id', '?')}"
        text = " ".join(x.get("text", "") for x in v.get("fields") or [])
        bangla = bool(re.search(r"[\u0980-\u09ff]", text))
        for obj in reader.get("objections") or []:
            words = content_words(obj)
            if not words:
                continue
            if bool(re.search(r"[\u0980-\u09ff]", obj)) != bangla:
                f.note(f"{tag}: the objection '{obj}' is in another language than the copy: check by eye that it is "
                       "answered, and log objections in the customer's own words")
                continue
            if not any(mentions(text, w) for w in words):
                f.warn(f"{tag}: the reader's objection '{obj}' is never answered: voice it in their words, then answer "
                       "it with the proof (R5 2.1, 4)")
        situation = " ".join(str(reader.get(k) or "") for k in ("who", "situation", "job"))
        sw = content_words(situation)
        if sw and bool(re.search(r"[\u0980-\u09ff]", situation)) == bangla and not any(mentions(text, w) for w in sw):
            f.note(f"{tag}: nothing of the reader's situation from the brief ('{situation.strip()[:60]}'): start at the "
                   "reader's moment (R5 9)")
        action = brief.get("action") or ""
        aw = content_words(action)
        if aw and bool(re.search(r"[\u0980-\u09ff]", action)) == bangla and not any(mentions(text, w) for w in aw):
            f.warn(f"{tag}: the brief's action ('{action}') is never asked for")
        for bad in brief.get("must_avoid") or []:
            if isinstance(bad, str) and 0 < len(bad.split()) <= 4 and bad.lower() in text.lower():
                f.error(f"{tag}: '{bad}' is on the brief's must-avoid list")


def lint_copy(doc, pack=None, level="draft", brief=None):
    platforms = load_platforms()["types"]
    meta = doc["meta"]
    t = meta.get("type")
    if t not in platforms:
        return {"ok": False, "errors": [f"unknown type {t!r}: one of {', '.join(sorted(platforms))}"], "warnings": [],
                "notes": [], "stats": {}}
    prof = platforms[t]
    f = Findings(level)
    ctx = {"type": t, "family": prof["family"], "label": prof["label"], "rules": prof.get("rules") or {},
           "meta": meta, "lang": meta.get("lang") or "en", "pack": pack,
           "claims": {c.get("id"): c for c in (pack or {}).get("claims", [])}}
    for v in doc["variants"]:
        fields = v.get("fields") or []
        ctx["vtag"] = f"variant {v.get('id', '?')}"
        counts = {}
        for fld in fields:
            role = fld.get("role")
            counts[role] = counts.get(role, 0) + 1
            spec = prof["fields"].get(role)
            ctx["tag"] = f"{ctx['vtag']} {role}" + (f" {counts[role]}" if counts[role] > 1 else "")
            if spec is None:
                f.warn(f"{ctx['tag']}: '{role}' is not a field of {t} ({', '.join(prof['fields'])})")
                spec = {}
            text = fld.get("text") or ""
            if not text.strip():
                f.warn(f"{ctx['tag']}: empty")
                continue
            check_field(f, spec, fld, ctx)
            if role not in ("search_terms", "tag"):
                check_words(f, text, ctx["tag"], ctx)
                check_claims(f, text, fld, ctx["tag"], ctx)
            if role in ("button", "cta") and ctx["family"] in ("landing", "email") and \
                    text.strip().lower().rstrip(".!") in GENERIC_BUTTONS:
                f.note(f"{ctx['tag']}: a generic button ('{text}'): name the result the reader gets (R5 3)")
        for role, spec in prof["fields"].items():
            k = counts.get(role, 0)
            if spec.get("min_count") and k < spec["min_count"]:
                f.warn(f"{ctx['vtag']}: {k} {role} fields; {spec['min_count']} at least")
            if spec.get("max_count") and k > spec["max_count"]:
                f.error(f"{ctx['vtag']}: {k} {role} fields; {spec['max_count']} at most")
            if spec.get("one_at_most") and k:
                short = [x for x in fields if x.get("role") == role and len(x.get("text") or "") <= spec["one_at_most"]]
                if not short:
                    f.warn(f"{ctx['vtag']}: at least one {role} of {spec['one_at_most']} characters or fewer (R5 6.1)")
        if ctx["family"] in ("email", "outbound"):
            check_email(f, fields, ctx)
            check_outbound(f, fields, ctx)
        if ctx["family"] == "product":
            check_product(f, fields, ctx)
        if ctx["rules"].get("bd_commerce"):
            check_bd_commerce(f, fields, ctx)
        body = " ".join(x.get("text", "") for x in fields if x.get("role") not in ("search_terms", "tag"))
        g = grade(body)
        target = ctx["rules"].get("grade")
        if g is not None and target and g > target[1] + 1:
            f.warn(f"{ctx['vtag']}: reading grade {g}; {target[0]} to {target[1]} for this type (R5 3, R6 6.1)")
        if ctx["rules"].get("one_cta"):
            ctas = {(x.get("text") or "").strip().lower() for x in fields if x.get("role") in ("cta", "button")}
            if len(ctas) > 1:
                f.warn(f"{ctx['vtag']}: {len(ctas)} different calls to action: one primary action (R5 11.1)")
    check_variants(f, doc, ctx)
    if brief:
        check_brief(f, doc, brief)
    stats = {"type": t, "family": ctx["family"], "variants": len(doc["variants"]), "lang": ctx["lang"],
             "fields": sum(len(v.get("fields") or []) for v in doc["variants"])}
    return {"ok": not f.errors, "errors": f.errors, "warnings": f.warnings, "notes": f.notes, "stats": stats}


# --------------------------------------------------------------------------------------------- the voice pass

TYPE_PLATFORM = {"meta-feed": "facebook", "meta-stories": "instagram", "linkedin-ad": "linkedin",
                 "tiktok-ad": "tiktok", "youtube-shorts-ad": "youtube", "instagram": "instagram",
                 "facebook": "facebook", "linkedin": "linkedin", "x": "x", "threads": "threads", "tiktok": "tiktok",
                 "youtube": "youtube", "linkedin-note": "linkedin", "linkedin-dm": "linkedin", "whatsapp": "whatsapp",
                 "sms": "sms", "fb-shop": "facebook"}
FAMILY_PLATFORM = {"email": "email", "outbound": "email", "product": "web", "landing": "web", "ad": "web",
                   "post": "facebook", "message": "whatsapp"}
ROLE_MAP = {"headline": "headline", "title": "headline", "h1": "headline", "long_headline": "headline",
            "subject": "headline", "seo_title": "headline", "display_name": "headline", "business_name": "headline",
            "path": "headline", "cta": "cta", "button": "cta", "caption": "caption", "primary": "caption",
            "intro": "caption", "ad_text": "caption"}


def voice_pass(doc):
    """natural-text's lint on every field, through codex-design copylint (932 rules, 24 languages)."""
    if not DESIGN.exists():
        return {"ran": False, "why": f"{DESIGN} not found (install codex-design)"}
    meta = doc["meta"]
    t = meta.get("type")
    fam = load_platforms()["types"].get(t, {}).get("family")
    platform = meta.get("platform") or TYPE_PLATFORM.get(t) or FAMILY_PLATFORM.get(fam) or "web"
    lang = meta.get("lang") or "en"
    locale = meta.get("locale") or ("BD" if lang in ("bn", "banglish") else "")
    errors, warnings, notes = [], [], []
    ran = False
    for v in doc["variants"]:     # one call per variant: deck checks (repeats, calls to action) stay inside a variant
        strings, where = [], []
        for fld in v.get("fields") or []:
            role = fld.get("role")
            if role in ("search_terms", "tag") or not (fld.get("text") or "").strip():
                continue
            if role == "cta" and fam == "ad":
                continue          # ad buttons come from the platform's fixed menu (Learn More, Shop Now)
            mapped = "body" if (fam == "product" and role == "title") else ROLE_MAP.get(role, "body")
            strings.append({"role": mapped, "text": fld["text"]})
            where.append(f"variant {v.get('id', '?')} {role}")
        if not strings:
            continue
        payload = {"platform": platform, "strings": strings}
        if locale:
            payload["locale"] = locale
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False)
            tmp = fh.name
        cmd = [sys.executable, str(DESIGN), "copylint", "--copy", tmp, "--json"]
        if lang not in ("en", "banglish"):
            cmd += ["--lang", lang]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            return {"ran": False, "why": "copylint timed out after 300 s"}
        finally:
            os.unlink(tmp)
        try:
            rep = json.loads(proc.stdout)
        except ValueError:
            return {"ran": False, "why": (proc.stderr or proc.stdout)[:300]}
        ran = True
        for item, label in zip(rep.get("items", []), where):
            for x in item.get("findings", []):
                msg = f"voice: {label}: {x.get('message')}" + (f" (try: {x['suggest']})" if x.get("suggest") else "")
                {"error": errors, "warning": warnings}.get(x.get("severity"), notes).append(msg)
        for x in rep.get("deck", []):
            notes.append(f"voice: variant {v.get('id', '?')}: {x.get('message') if isinstance(x, dict) else x}")
    if not ran:
        return {"ran": False, "why": "no text"}
    return {"ran": True, "errors": errors, "warnings": warnings, "notes": notes}
