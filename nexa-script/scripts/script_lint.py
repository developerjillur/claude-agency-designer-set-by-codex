"""nexa-script rules: the lint for scripts (script.json, narration .txt) and articles (.md).

Every finding names the research note it comes from: R1 YouTube long-form, R2 short-form and ads, R3 storytelling,
R4 blog, V1 to V6 the reference videos (skill-lab, 2026-09-26). Errors block delivery, warnings are fixed or argued
with a reason, notes are read. A gate is a warning in a draft and an error in a final.
"""
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nexa_review as R  # noqa: E402
from script_core import (FORMATS, LANG_FACTOR, MODES, loop_is_cross_video, loop_question, mmss,  # noqa: E402
                         sentences, text_of, timing, words)

EM, EN = chr(0x2014), chr(0x2013)
DESIGN = Path(os.environ.get("NEXA_DESIGN_PY", str(Path.home() / ".claude/skills/codex-design/scripts/design.py")))

WORDS = {
    "but": {
        "en": ["but", "however", "yet", "except", "instead", "actually", "turns out", "until", "though", "still",
               "only", "and yet"],
        "bn": ["কিন্তু", "অথচ", "তবে", "আসলে", "বরং", "যদিও", "তবুও", "তবু"],
        "hi": ["लेकिन", "पर", "मगर", "असल में", "बल्कि", "फिर भी", "हालांकि", "हालाँकि"],
        "banglish": ["kintu", "asole", "tobe", "othocho", "boroncho", "jodio"],
    },
    "therefore": {
        "en": ["so", "therefore", "that's why", "which means", "because of that", "as a result", "this is why",
               "that means", "which is why", "and so"],
        "bn": ["তাই", "ফলে", "সেজন্য", "এজন্য", "এর মানে", "তার মানে", "সেই কারণে", "এ কারণে"],
        "hi": ["तो", "इसलिए", "इसी वजह से", "मतलब", "इसका मतलब", "इस कारण"],
        "banglish": ["tai", "fole", "er mane", "tar mane", "sejonno", "ejonno"],
    },
    "andthen": {
        "en": ["and then", "then", "next", "also", "another", "plus", "after that", "additionally", "moreover",
               "furthermore", "secondly", "thirdly", "finally"],
        "bn": ["এরপর", "তারপর", "আরেকটা", "এছাড়া", "এছাড়াও", "পরের", "দ্বিতীয়ত", "তৃতীয়ত"],
        "hi": ["फिर", "इसके बाद", "एक और", "इसके अलावा", "दूसरा", "तीसरा"],
        "banglish": ["tarpor", "erpor", "arekta", "echara"],
    },
    "preamble": {
        "en": ["hi guys", "hey guys", "hello everyone", "hey everyone", "welcome back", "welcome to", "in today's video",
               "in this video", "today we're going to", "today i'm going to", "before we start", "before we begin",
               "don't forget to", "let's dive in", "without further ado", "what's up guys", "hello friends"],
        "bn": ["আসসালামু আলাইকুম", "হ্যালো বন্ধুরা", "সবাইকে স্বাগতম", "আজকের ভিডিওতে", "কেমন আছেন সবাই",
               "স্বাগতম আমাদের", "আজকে আমরা কথা বলব"],
        "hi": ["नमस्कार दोस्तों", "हेलो दोस्तों", "आज की वीडियो में", "आज के वीडियो में", "स्वागत है",
               "क्या हाल है दोस्तों", "नमस्ते दोस्तों"],
        "banglish": ["assalamu alaikum", "hello bondhura", "ajker video te", "sobai ke shagotom"],
    },
    "ending": {
        "en": ["in conclusion", "to sum up", "to wrap up", "that's it for today", "before we end", "in summary",
               "to conclude", "that's all for", "let's recap", "to recap"],
        "bn": ["শেষ করার আগে", "সব মিলিয়ে", "আজ এই পর্যন্তই", "সংক্ষেপে বলি", "শেষে বলি"],
        "hi": ["अंत में", "आज के लिए बस इतना", "निष्कर्ष", "संक्षेप में"],
        "banglish": ["shesh korar age", "aj ei porjonto"],
    },
    "moral": {
        "en": ["the lesson", "the moral", "remember,", "at the end of the day", "always remember", "never forget",
               "the takeaway", "what this teaches us", "the real lesson", "believe in yourself", "never give up",
               "follow your dreams", "anything is possible", "hard work pays off"],
        "bn": ["শিক্ষা হলো", "শিক্ষাটা হলো", "মনে রাখবেন", "মনে রাখবে", "দিনশেষে", "দিন শেষে"],
        "hi": ["सीख यह है", "याद रखिए", "याद रखो", "सबक यह है"],
        "banglish": ["mone rakhben", "shikkha holo", "din sheshe"],
    },
    "cta": {
        "en": ["subscribe", "like this video", "hit the bell", "comment below", "link in bio", "click the link",
               "sign up", "buy now", "shop now", "download", "order now", "book a", "get yours", "try it", "tap"],
        "bn": ["সাবস্ক্রাইব", "লাইক দিন", "কমেন্ট করুন", "অর্ডার করুন", "কিনুন", "ইনবক্স করুন", "লিংকে", "বুক করুন"],
        "hi": ["सब्सक्राइब", "लाइक करें", "कमेंट करें", "ऑर्डर करें", "खरीदें", "लिंक पर"],
        "banglish": ["subscribe", "order korun", "inbox korun", "kinun"],
    },
    # V2 E13: an ending that hands the payoff to the viewer's imagination
    "vague_payoff": {
        "en": ["and you know the rest", "the rest is history", "you know how it goes", "and the rest, as they say",
               "you can guess the rest"],
        "bn": ["বাকিটা তো জানোই", "বাকিটা তো জানেনই", "বাকিটা ইতিহাস", "বাকিটা আপনারা জানেন", "বাকিটা তো বুঝতেই পারছেন"],
        "hi": ["आगे तो तुम्हें पता ही है", "बाकी तो इतिहास है", "आगे आप जानते ही हैं", "बाकी आप समझ ही गए होंगे"],
        "banglish": ["baki ta to jano", "bakita to janen", "baki ta itihash"],
    },
    # V3 SL15: a loop with nothing behind it
    "fake_loop": {
        "en": ["stay till the end", "watch till the end", "watch until the end", "stick around till the end",
               "stay until the end", "secret at the end", "bonus at the end", "wait for it", "keep watching to find out",
               "don't skip"],
        "bn": ["শেষ পর্যন্ত দেখুন", "শেষ পর্যন্ত থাকুন", "শেষ পর্যন্ত দেখবেন", "শেষে একটা বোনাস", "শেষে একটা সিক্রেট",
               "স্কিপ করবেন না"],
        "hi": ["अंत तक देखें", "आखिर तक देखना", "आखिर तक बने रहें", "अंत में एक बोनस", "स्किप मत करना"],
        "banglish": ["shesh porjonto dekhun", "skip korben na"],
    },
    "sponsor": {
        "en": ["sponsored by", "this video is sponsored", "brought to you by", "today's sponsor", "use code",
               "promo code", "use my code", "link in the description"],
        "bn": ["স্পন্সর", "প্রোমো কোড", "ডিসক্রিপশনে লিংক", "ডেসক্রিপশনে লিংক"],
        "hi": ["स्पॉन्सर", "प्रोमो कोड", "डिस्क्रिप्शन में लिंक"],
        "banglish": ["sponsor", "promo code"],
    },
    # V3 SL12: a label in place of a picture of the scale
    "abstract": {
        "en": ["huge", "a lot of", "very popular", "massive", "tons of", "so many", "very poor", "very rich",
               "enormous", "countless", "incredibly"],
        "bn": ["বিশাল", "অনেক বেশি", "খুবই জনপ্রিয়", "প্রচুর", "অসংখ্য", "ব্যাপক"],
        "hi": ["बहुत बड़ा", "बहुत सारे", "बहुत ज़्यादा", "बहुत पॉपुलर", "अनगिनत", "ढेर सारे"],
        "banglish": ["onek beshi", "bishal", "prochur"],
    },
    # V5 HL4: a feeling named at the peak (English uses EMOTION_EN)
    "emotion_label": {
        "en": [],
        "bn": ["নার্ভাস ছিলাম", "খুব খুশি হলাম", "খুশি হলাম", "লজ্জা পেলাম", "ভয় পেয়ে গেলাম", "ভয় পেলাম",
               "মন খারাপ হয়ে গেল", "রাগ হলো", "অবাক হলাম", "হতাশ হলাম", "খুব টেনশনে ছিলাম"],
        "hi": ["घबरा गया", "घबरा गई", "डर गया", "डर गई", "बहुत खुश था", "बहुत खुश थी", "शर्म आई", "गुस्सा आया",
               "हैरान रह गया", "हैरान रह गई"],
        "banglish": ["nervous chilam", "khushi holam", "bhoy pelam", "mon kharap hoye gelo"],
    },
    # V5 HL5: speech reported instead of heard (English uses REPORTED_EN)
    "reported": {
        "en": [],
        "bn": ["বলল যে", "বললেন যে", "জানাল যে", "জানালেন যে", "জিজ্ঞেস করল যে", "জিজ্ঞেস করলেন যে"],
        "hi": ["ने कहा कि", "ने बताया कि", "ने पूछा कि"],
        "banglish": ["bollo je", "janalo je"],
    },
    # V5 HL6: a thought frame
    "thought": {
        "en": ["i thought", "i'm like", "i was like", "in my head", "i'm thinking", "i was thinking",
               "i think to myself", "i said to myself"],
        "bn": ["মনে মনে ভাবছি", "মনে মনে ভাবলাম", "মাথায় একটাই কথা", "ভাবছি", "ভাবলাম"],
        "hi": ["मन में सोचा", "मैंने सोचा", "सोच रहा था", "सोच रही थी"],
        "banglish": ["mone mone vabchi", "vablam"],
    },
    # V5 HL7: report words inside a spoken line
    "formal_quote": {
        "en": ["represents", "opportunity", "inadequate", "execution", "dissatisfied", "regarding", "furthermore",
               "utilize", "commence", "henceforth", "in order to"],
        "bn": ["প্রদান", "গ্রহণ করুন", "পরিলক্ষিত", "অবগত", "সুতরাং", "বিধায়"],
        "hi": ["अतः", "प्रदान", "उपरोक्त", "कृपया ध्यान दें"],
        "banglish": [],
    },
    # V6-L1: empty hedges where the script should commit (the hook, an instruction, the CTA)
    "hedge": {
        "en": ["maybe", "might", "perhaps", "possibly", "probably", "kind of", "sort of", "i think", "i guess",
               "hopefully", "try to"],
        "bn": ["হয়তো", "সম্ভবত", "মনে হয়", "হতে পারে"],
        "hi": ["शायद", "मुझे लगता है", "हो सकता है"],
        "banglish": ["hoyto", "sombhoboto", "mone hoy"],
    },
    # V4-L02 and T10: openers that announce instead of breaking a belief
    "weak_opener": {
        "en": ["here are", "you must learn", "some day you'll need", "someday you'll need", "today i'll teach you",
               "today i will teach you", "in this video i will", "in this video i'll", "let me tell you a story"],
        "bn": ["আজকে আপনাদের শেখাবো", "আজকে আমি দেখাবো", "আজকে জানবো", "চলুন শুরু করা যাক"],
        "hi": ["आज मैं आपको सिखाऊंगा", "आज हम सीखेंगे", "चलिए शुरू करते हैं"],
        "banglish": ["ajke apnader shekhabo", "cholun shuru kora jak"],
    },
    # R2 and natural-text: urgency needs a real date or count
    "urgency": {
        "en": ["last chance", "only today", "limited time", "hurry", "closing soon", "while stocks last", "ends soon",
               "don't miss out"],
        "bn": ["সীমিত সময়", "শেষ সুযোগ", "তাড়াতাড়ি করুন", "আজই শেষ", "মিস করবেন না"],
        "hi": ["सीमित समय", "आखिरी मौका", "जल्दी करें"],
        "banglish": ["shimito shomoy", "shesh shujog"],
    },
    # V2 E10: talking to the viewer (English uses YOU_EN)
    "you": {
        "en": [],
        "bn": ["আপনি", "আপনার", "আপনাকে", "আপনারা", "তুমি", "তোমার", "তোমাকে", "তোমরা", "তুই", "তোর"],
        "hi": ["आप", "आपके", "आपको", "आपका", "आपकी", "तुम", "तुम्हारा", "तुम्हें", "तुम्हारी"],
        "banglish": ["apni", "apnar", "apnake", "tumi", "tomar"],
    },
}
# Every language: claims that have no source (R3 2.9); a script that uses them fails
POP_SCIENCE = ["22 times more memorable", "22x more memorable", "goldfish", "8-second attention", "8 second attention",
               "eight-second attention", "dopamine hit", "dopamine rush", "oxytocin", "গোল্ডফিশ", "২২ গুণ বেশি মনে"]
# V6-L12: pop-science words that need a source or go (a warning; the claims above are errors)
POP_SCIENCE_WARN = ["dopamine", "cortisol", "subconscious", "hypnotic", "cheat code", "hack your brain",
                    "rewire your brain", "brain is wired", "twice as motivated", "ডোপামিন", "সাবকনশাস"]
# V6-L4: the "not X, it's Y" frame, once a script at most
NOT_X_ITS_Y = re.compile(r"\b(it'?s |this is |that'?s )?not (just |only |about )?[^.,;!?]{1,40}[,;:] ?(it'?s|but|it is)"
                         r"\b", re.I)
AI_PHRASES = ["let's dive in", "dive deep into", "delve", "tapestry", "a testament to", "in a world where",
              "little did", "game-changer", "game changer", "unlock the", "buckle up", "digital landscape",
              "ever-evolving", "fast-paced world", "it's important to note", "navigate the complexities",
              "look no further", "whether you're a", "seamless", "elevate your", "pivotal", "underscore",
              "stay tuned", "the result?", "here's the thing:"]
SOURCE_NEEDED = re.compile(
    r"(\d[\d,.]*\s?%|[$€£৳₹]\s?\d|\d[\d,.]*\s?(?:million|billion|crore|lakh|কোটি|লাখ|करोड़|लाख|"
    r"taka|tk\b|টাকা|rupees?|रुपये|रुपए|dollars?|euros?|pounds?)|[০-৯][০-৯,.]*\s?(?:%|শতাংশ|টাকা|কোটি|লাখ)|"
    r"\b(?:study|studies|research|survey|scientists|according to|data shows|experts|proven|science says|"
    r"scientifically)\b|গবেষণা|সমীক্ষা|জরিপ|"
    r"অনুযায়ী|अध्ययन|रिसर्च|सर्वे|के अनुसार)", re.I)
RISK_WORDS = ["cure", "cures", "heal", "heals", "guaranteed", "guarantee", "#1", "number one", "clinically proven",
              "risk-free", "risk free", "instant results", "overnight", "100% safe", "no side effects",
              "গ্যারান্টি", "শতভাগ নিশ্চিত", "রাতারাতি"]
ATTRIBUTE = re.compile(
    r"\b(are you|do you have|do you suffer|your)\b.{0,40}\b(diabetes|diabetic|depression|depressed|debt|overweight|"
    r"obese|fat|bald|balding|acne|anxiety|single|divorced|pregnant|disabled|gay|lesbian|religion|muslim|hindu|"
    r"christian|credit score|bankrupt)\b", re.I)
QUICK_MONEY = re.compile(r"(earn|make)\s+[$€£৳₹]?\s?\d[\d,.]*\s*(k|,000)?\s*(in|per|a)\s+"
                         r"(\d+\s+)?(day|days|week|weeks|hour)", re.I)
# V5 HL13: improvement claims that need a measurement behind them
IMPROVEMENT = re.compile(r"((improv|boost|increas|grow|doubl|tripl)\w*\b.{0,40}?\bby\s+\d+(\.\d+)?\s?%|"
                         r"\b\d+(\.\d+)?\s?%\s+(better|faster|more|higher|cheaper)\b|\btop\s?1\s?%|"
                         r"\bbetter than 99\s?%|\b\d+x\s+(better|faster|more|higher|cheaper)\b)", re.I)
EMOTION_EN = re.compile(
    r"\b(i|we|he|she|they)\s+(was|were|felt|feel|am|is|are|got|became)\s+(so\s+|very\s+|really\s+|extremely\s+|"
    r"totally\s+)?(nervous|scared|afraid|happy|sad|angry|excited|anxious|shocked|surprised|embarrassed|ashamed|"
    r"upset|terrified|thrilled|devastated|furious|relieved|proud|jealous|overwhelmed|heartbroken)\b", re.I)
REPORTED_EN = re.compile(r"\b(told (me|him|her|us|them) that|said that|asked (me|him|her|us) (whether|if)|"
                         r"explained that|was very upset with)\b", re.I)
YOU_EN = re.compile(r"\b(you|your|you're|yours|yourself)\b", re.I)
QUOTE_RE = re.compile(r"[\"“]([^\"“”]{2,400})[\"”]")
PAUSE_MARK = re.compile(r"\[(beat|pause)\]", re.I)
# V3 SL18: Hindi carried into Bangla
HINDI_IN_BANGLISH = ["lekin", "matlab", "bahut", "kyunki", "sirf", "nahi hai", "accha hai"]
HINDI_IN_BANGLA_SCRIPT = ["লেকিন", "মতলব", "বহুত"]
TALKING_HEAD = ("talking head", "a-roll", "a roll", "face to camera", "to camera", "on camera")
ROLES = ("hook", "identity", "setup", "conflict", "choice", "pp1", "pp2", "change", "value", "marker", "stakes_loss",
         "stakes_gain", "surprise", "bridge", "sponsor", "cta", "key_moment")
DIGITS = re.compile(r"[0-9০-৯०-९]")


# ------------------------------------------------------------------------------------------------------ helpers

def phrase_hits(text, phrases):
    """The phrases found in the text; a phrase inside a longer one that was found (মনে রাখবে in মনে রাখবেন) is
    reported once, as the longer one."""
    low = (text or "").lower()
    hits = sorted({p.lower(): p for p in phrases if p.lower() in low}.items(), key=lambda kv: -len(kv[0]))
    out = []
    for key, p in hits:
        if not any(key in longer.lower() for longer in out):
            out.append(p)
    return out


def word_hits(text, phrases):
    """Like phrase_hits, but whole words only (for Latin-script words such as 'lekin' or 'huge')."""
    low = (text or "").lower()
    return [p for p in phrases if re.search(r"(?<![\w])" + re.escape(p.lower()) + r"(?![\w])", low)]


def lex(kind, lang, english=True):
    """A word list in the script's language, plus the English one (scripts mix English in), without repeats."""
    out = list(WORDS[kind].get(lang, []))
    if english or lang == "banglish":
        out += [w for w in WORDS[kind]["en"] if w not in out]
    return out


def starts_with(sentence, phrases):
    s = re.sub(r"^[\s\"'“‘(\[]+", "", (sentence or "").lower())
    for p in sorted(phrases, key=len, reverse=True):
        if s.startswith(p.lower()) and (len(s) == len(p) or not s[len(p)].isalpha()):
            return p
    return None


def classify(sentence, lang):
    for kind in ("but", "therefore", "andthen"):
        if starts_with(sentence, lex(kind, lang, english=lang in ("en", "banglish"))):
            return kind
    return None


def count_you(text, lang):
    if lang == "en":
        return len(YOU_EN.findall(text or ""))
    vocab = set(WORDS["you"].get(lang, []))
    return sum(1 for w in words(text) if w.lower() in vocab)


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
        """A warning in a draft, an error in a final."""
        (self.errors if self.level == "final" else self.warnings).append(msg)


class Ctx:
    """Everything the checks read, computed once."""

    def __init__(self, script, pack):
        self.script, self.pack = script, pack
        self.meta, self.beats = script["meta"], script["beats"]
        self.fmt, self.lang = self.meta["format"], self.meta["lang"]
        self.spec = FORMATS[self.fmt]
        self.json = script["kind"] == "json"
        self.T = timing(script)
        self.wpm, self.total = self.T["wpm"], self.T["total_seconds"]
        self.text = " ".join(b.get("narration", "") for b in self.beats)
        # sentences with their beat and start second
        self.rows = []
        for i, (b, tb) in enumerate(zip(self.beats, self.T["beats"])):
            t = tb["start"]
            for s in sentences(b.get("narration", "")):
                self.rows.append({"text": s, "beat": i, "t": t})
                t += len(words(s)) / self.wpm * 60 if self.wpm else 0
        self.sents = [r["text"] for r in self.rows]
        self.kinds = [None] + [classify(s, self.lang) for s in self.sents[1:]]
        self.minutes = self.total / 60 if self.total else len(words(self.text)) / 160
        self.mode = (script.get("story") or {}).get("mode") or self.meta.get("mode") or ""
        self.stats = {}
        self.opened, self.closed = {}, {}

    def roles(self, i):
        return set(self.beats[i].get("roles") or [])

    def start(self, i):
        return self.T["beats"][i]["start"]


# ------------------------------------------------------------------------------------------------------ checks

def check_words(c, f):
    text = c.text
    if EM in text or re.search(r"\s" + EN + r"\s", text):
        f.error("an em dash or a spaced en dash: use a comma, a colon, a full stop or brackets")
    for p in phrase_hits(text, POP_SCIENCE):
        f.error(f"pop-science claim with no source ('{p}'): cut it (R3 2.9)")
    for p in phrase_hits(text, AI_PHRASES):
        f.warn(f"machine tell: '{p}'")
    for p in word_hits(text, POP_SCIENCE_WARN) if c.lang in ("en", "banglish") else phrase_hits(text, POP_SCIENCE_WARN):
        if not any(p in x.lower() for x in phrase_hits(text, POP_SCIENCE)):
            f.warn(f"a pop-science word ('{p}'): source it or cut it (V6-L12)")
    frames = NOT_X_ITS_Y.findall(text) if c.lang in ("en", "banglish") else []
    if len(frames) > 1:
        f.warn(f"{len(frames)} 'not X, it's Y' frames: one a script at most (V6-L4, natural-text)")
    for s_ in c.sents:
        for p in phrase_hits(s_, lex("urgency", c.lang)):
            if not DIGITS.search(s_):
                f.warn(f"urgency with no date or count ('{p}'): give the real deadline or cut it (R2 4.5)")
    for p in phrase_hits(text, lex("vague_payoff", c.lang)):
        f.error(f"a vague payoff ('{p}'): show the result instead of handing it to the viewer (V2 E13)")
    for p in phrase_hits(text, lex("fake_loop", c.lang)):
        f.warn(f"a fake-loop phrase ('{p}'): name the real payoff and pay it, or cut the line (V3 SL15)")
    for b in c.beats:
        nar = b.get("narration", "")
        m = IMPROVEMENT.search(nar)
        if m and not b.get("claims"):
            f.gate(f"{b.get('id')}: an improvement claim with no measurement behind it ('{m.group(0)}'; V5 HL13)")
        labels = word_hits(nar, lex("abstract", c.lang)) if c.lang in ("en", "banglish") else \
            phrase_hits(nar, lex("abstract", c.lang, english=False))
        if labels and not DIGITS.search(nar):
            f.warn(f"{b.get('id')}: '{labels[0]}' with no number or concrete detail: show the scale against "
                   "something the viewer knows (V3 SR12)")
    if c.lang == "bn":
        # the danda and double danda (U+0964, U+0965) sit in the Devanagari block but belong to Bangla too
        if re.search(r"[\u0900-\u0963\u0966-\u097f]", text):
            f.error("Devanagari text inside a Bangla script (V3 SL18)")
        for p in phrase_hits(text, HINDI_IN_BANGLA_SCRIPT):
            f.warn(f"a Hindi word in Bangla script ('{p}'; V3 SL18)")
    if c.lang in ("bn", "hi"):
        narr = QUOTE_RE.sub(" ", text)
        polite = {"bn": ("আপনি", "আপনার", "আপনাকে", "আপনারা"), "hi": ("आप", "आपके", "आपको", "आपका", "आपकी")}[c.lang]
        close = {"bn": ("তুমি", "তোমার", "তোমাকে", "তোমরা"), "hi": ("तुम", "तुम्हारा", "तुम्हें", "तुम्हारी")}[c.lang]
        toks = [w.strip("\u0964\u0965,.?!") for w in words(narr)]
        if any(t in polite for t in toks) and any(t in close for t in toks):
            f.warn("the narration mixes the polite and the familiar you: keep one address form (V4-L27)")
    if c.lang == "banglish":
        for p in word_hits(text, HINDI_IN_BANGLISH):
            f.warn(f"a Hindi word in a Banglish script ('{p}'; V3 SL18)")


def check_opening(c, f):
    first = c.sents[0]
    pre = starts_with(first, lex("preamble", c.lang))
    if pre:
        f.error(f"the first line opens with a greeting or preamble ('{pre}'): open on the hook, greet later if at "
                "all (R1 9.1, V2 E1)")
    weak = starts_with(first, lex("weak_opener", c.lang))
    if weak and not pre:
        f.warn(f"the first line announces instead of hooking ('{weak}'): break a belief, show the result or open "
               "a gap (V4-L02)")
    # thought narration ("you might think...") voices the viewer's belief before breaking it: not a hedge (V6-L1)
    hook_text = re.sub(r"(you might (think|be wondering)|you'?d think|you probably think|আপনি হয়তো ভাবছেন|"
                       r"হয়তো ভাবছেন|आप सोच रहे होंगे)", " ", " ".join(c.sents[:2]), flags=re.I)
    hedges = word_hits(hook_text, lex("hedge", c.lang)) if c.lang in ("en", "banglish") else \
        phrase_hits(hook_text, lex("hedge", c.lang, english=False))
    if hedges and "?" not in hook_text:
        f.warn(f"a hedge in the hook ('{hedges[0]}'): commit where the evidence is firm (V6-L1)")
    n_first = len(words(first))
    if c.fmt in ("short", "ad"):
        if n_first > 12:
            f.warn(f"the first sentence is {n_first} words; a short's hook line is 12 or fewer (V2 E2)")
        b1 = c.beats[0] if c.beats else {}
        if c.json and not (b1.get("visual") or "").strip():
            f.error("beat 1 has no visual: the first frame needs an action (R2)")
        ov = b1.get("on_screen") or ""
        if ov and len(words(ov)) > 7:
            f.warn(f"beat 1 overlay has {len(words(ov))} words; 7 or fewer (R2)")
        contrast = starts_with(first, lex("but", c.lang)) or phrase_hits(f" {first.lower()} ",
                                                                          [" but ", " yet ", " except "])
        if not DIGITS.search(first) and not contrast and "?" not in first:
            f.note("the hook line has no number, time, contrast or question: check that it makes a specific promise "
                   "(V3 SL14)")
    elif c.spec["long"]:
        if n_first > 20:
            f.warn(f"the first sentence is {n_first} words; 20 or fewer (V2 E2)")
        opening = " ".join(c.sents[:6])
        first20 = [r for r in c.rows if r["t"] < 20] or c.rows[:1]
        has_turn = any(k in ("but", "therefore") for k, r in zip(c.kinds, c.rows) if r["t"] < 20) or \
            any("?" in r["text"] for r in first20) or \
            bool(phrase_hits(" " + " ".join(r["text"] for r in first20).lower() + " ",
                             [f" {w} " for w in lex("but", c.lang)]))
        if not has_turn:
            f.warn("no turn (but, except, yet) or question in the first 20 seconds (R1 9.1, V1 SC-01)")
        if not DIGITS.search(opening) and not re.search(r"\b[A-Z][a-z]{2,}", " ".join(opening.split()[1:])):
            f.note("the opening has no number or name: check that it is specific enough")
        early = " ".join(r["text"] for r in c.rows if r["t"] < 30)
        for p in phrase_hits(early, lex("cta", c.lang)):
            f.warn(f"a call to action ('{p}') in the first 30 seconds: move it to the end (R1 9.1)")
    if not c.spec.get("ad") and c.total:
        early = " ".join(r["text"] for r in c.rows if r["t"] < 0.2 * c.total)
        for p in phrase_hits(early, lex("sponsor", c.lang)):
            f.warn(f"a sponsor or plug ('{p}') in the first 20 % of the runtime: place it after the first payoff "
                   "(V2 E15, R1 4)")


def check_engine(c, f):
    counted = [k for k in c.kinds if k]
    andthen = sum(1 for k in counted if k == "andthen")
    turns = sum(1 for k in counted if k in ("but", "therefore"))
    c.stats.update({"but_or_therefore": turns, "and_then": andthen})
    if counted and andthen / len(counted) > 1 / 3:
        f.warn(f"{andthen} of {len(counted)} marked transitions are and-then: rewrite them as but or therefore "
               "(R3 C1)")
    for i in range(2, len(c.kinds)):
        if c.kinds[i] == "andthen" and c.kinds[i - 1] == "andthen":
            f.warn(f"two and-then openers in a row: '{c.sents[i - 1][:40]}' / '{c.sents[i][:40]}' (V2 E6)")
            break
    if c.spec["long"] and c.minutes >= 2 and turns / max(c.minutes, 1) < 1:
        f.warn(f"{turns} but or therefore turns in {c.minutes:.1f} minutes: fewer than one a minute (R1 4)")
    # the longest stretch with nothing that pulls the viewer on: a question, a turn, a new loop or a new section
    if c.wpm and c.total >= 20:
        events = [0.0]
        for r, k in zip(c.rows, c.kinds):
            if "?" in r["text"] or k in ("but", "therefore"):
                events.append(r["t"])
        for i, b in enumerate(c.beats):
            if b.get("loops_open") or (i and b.get("section") and b.get("section") != c.beats[i - 1].get("section")):
                events.append(c.start(i))
        events = sorted(set(events)) + [c.total]
        gap, at = max(((b - a), a) for a, b in zip(events, events[1:]))
        c.stats["longest_gap_s"] = round(gap, 1)
        limit = 60 if c.spec["long"] else 12
        if gap > limit:
            f.warn(f"{mmss(at)} to {mmss(at + gap)}: {gap:.0f} s with no question, turn or new loop ({limit} s at "
                   "most; R1 4, V2 E5, V3 SL5)")
    questions = sum(1 for s in c.sents if "?" in s)
    if c.minutes >= 1:
        qpm = questions / c.minutes
        c.stats["questions_per_min"] = round(qpm, 1)
        if qpm > 3:
            f.note(f"{qpm:.1f} questions a minute: over 3 turns into a quiz (V3 SL11)")
    if c.spec["long"] and c.spec["medium"] in ("video", "listen") and c.minutes >= 2:
        ypm = count_you(c.text, c.lang) / c.minutes
        c.stats["you_per_min"] = round(ypm, 1)
        if ypm < 3:
            f.note(f"{ypm:.1f} direct addresses a minute: the references talk to the viewer 3.5 to 8 times a minute "
                   "(V2 E10)")


def check_loops(c, f):
    opened, closed, order = {}, {}, []
    for i, b in enumerate(c.beats):
        for lid in b.get("loops_open") or []:
            opened.setdefault(lid, i)
            order.append(lid)
        for lid in b.get("loops_close") or []:
            if lid not in opened:
                f.error(f"{b.get('id')}: loop {lid} is closed before it is opened")
            closed[lid] = i
    for lid in opened:
        if lid not in closed:
            value = c.script["loops"].get(lid)
            if loop_is_cross_video(value):
                f.note(f"loop {lid} is declared to run into the next video: say so on screen or in the CTA")
            else:
                f.error(f"loop {lid} ({loop_question(value)}) is opened and never paid off (R3 R4)")
    for lid in c.script["loops"]:
        if lid not in opened:
            f.warn(f"loop {lid} is in the ledger but no beat opens it (loops_open)")
    if len(order) > 1 and order[0] in closed and closed[order[0]] < max(closed.values()):
        f.warn(f"the main loop {order[0]} closes before the others: close it last (R3 C2)")
    if order and order[0] in closed and c.spec["long"] and c.total:
        tail = c.total - c.T["beats"][closed[order[0]]]["end"]
        limit = max(10.0, min(30.0, 0.05 * c.total))
        if tail > limit:
            f.warn(f"{tail:.0f} s after the main payoff; {limit:.0f} s at most: pay off, close short, then the CTA "
                   "(V4-L22)")
    if not opened:
        f.note("no loops marked (loops_open / loops_close): the loop ledger cannot be checked")
    c.opened, c.closed = opened, closed


def check_tension(c, f):
    tens = [b.get("tension") for b in c.beats]
    if not (tens and all(isinstance(t, dict) and any(t.values()) for t in tens)):
        f.note("no tension scores on the beats (q, s, u, p): the tension map is skipped")
        return
    beats, T, fmt = c.beats, c.T, c.fmt
    tvals = [(t.get("q", 0) + t.get("s", 0) + t.get("u", 0)) for t in tens]
    pvals = [t.get("p", 0) for t in tens]
    run = 0
    for i, tv in enumerate(tvals):
        run = run + 1 if tv < 4 else 0
        limit = 2 if fmt in ("short", "ad") else max(2, int(45 / max(T["beats"][i]["seconds"] or 15, 1)))
        if run > limit:
            f.warn(f"{beats[i].get('id')}: a flat zone (tension under 4 for {run} beats; R3 6.1)")
            run = 0
    for i, pv in enumerate(pvals):
        if pv >= 2 and not any(tv >= 5 for tv in tvals[:i]):
            f.warn(f"{beats[i].get('id')}: an orphan payoff: nothing built tension before it (R3 6.1)")
    run, start = 0, 0
    for i, (tv, pv) in enumerate(zip(tvals, pvals)):
        if tv >= 6 and pv < 2:
            start = i if run == 0 else start
            run += 1
        else:
            run = 0
        span = T["beats"][i]["end"] - T["beats"][start]["start"]
        if run and (run > 3 if fmt in ("short", "ad") else span > 90):
            f.warn(f"{beats[start].get('id')} to {beats[i].get('id')}: unpaid tension (high for {run} beats with "
                   "no payoff): pay off a smaller loop (R3 6.1)")
            run = 0
    for i in range(len(beats) - 1):
        sec, nxt = beats[i].get("section"), beats[i + 1].get("section")
        if sec and nxt and sec != nxt and tens[i].get("q", 0) < 2 and i < len(beats) - 2:
            f.warn(f"{beats[i].get('id')}: the section '{sec}' ends with no open question (q under 2): end it on a "
                   "re-hook (R3 6.1)")
    if c.spec["long"] and c.total:
        stakes = [T["beats"][i]["start"] for i, t in enumerate(tens) if t.get("s", 0) >= 2]
        if not stakes or min(stakes) > c.total / 2:
            f.warn("no concrete stakes (s of 2 or more) before the midpoint (R3 R5)")
        surprises = sum(1 for p in pvals if p >= 2)
        need = max(1, math.ceil(c.minutes / 3))
        if surprises < need:
            f.warn(f"{surprises} payoffs or surprises; a {c.minutes:.0f}-minute script needs {need} (one every 2 to 3 "
                   "minutes; R3 6.2)")
        if len(tvals) >= 4:
            peak = max(range(len(tvals)), key=lambda i: tvals[i])
            if T["beats"][peak]["start"] < 0.5 * c.total:
                f.note("the tension peak sits in the first half: the highest tension belongs just before the biggest "
                       "payoff, around 75 to 90 % of the runtime (R3 6.1)")


def check_roles(c, f):
    """The story skeleton (V3): hook, conflict, change and value; PP1 early, PP2 late; the stakes pair early."""
    tagged = [i for i in range(len(c.beats)) if c.roles(i)]
    if not tagged:
        return
    unknown = sorted({r for i in tagged for r in c.roles(i)} - set(ROLES))
    if unknown:
        f.warn(f"unknown roles {', '.join(unknown)}: use {', '.join(ROLES)}")
    have = {r for i in tagged for r in c.roles(i)}
    missing = [r for r in ("hook", "conflict", "change", "value") if r not in have]
    if missing:
        f.warn(f"the skeleton lacks {', '.join(missing)} (hook, conflict, change and value are required; V3 SR4)")
    total = c.total or 1

    def where(role):
        return [i for i in tagged if role in c.roles(i)]

    pp1, pp2 = where("pp1"), where("pp2")
    if not pp1:
        f.warn("no PP1: name the one event that flips the before state (V3 SR1)")
    else:
        i = pp1[0]
        pos = c.start(i) / total
        if i == 0:
            f.warn("PP1 is the first beat: the viewer must know what it changes first (V3 3.1)")
        if c.spec["long"] and c.total > 180 and not 0.05 <= pos <= 0.30:
            f.warn(f"PP1 lands at {pos:.0%} of the runtime; 10 to 25 % (V3 SL2)")
        if not c.spec["long"] and pos > 0.40:
            f.warn(f"PP1 lands at {pos:.0%}; a short needs it by about a third (V3 ST2)")
        hook_end = max((c.T["beats"][j]["end"] for j in where("hook")), default=0.0)
        setup = c.start(i) - hook_end
        # V3 ST2: the minimum setup by 5 s in a short (SR3's 3 s is marked "ours, calibrate"); 10 % of long-form
        limit = 0.10 * total if c.spec["long"] else 5.0
        if setup > limit + 0.5:
            f.warn(f"{setup:.0f} s of setup before PP1; {limit:.0f} s at most (V3 SR3)")
    if c.spec["long"] and c.total > 180:
        if not pp2:
            f.warn("no PP2: a script over 3 minutes needs a second turn at 75 to 85 % (V3 SR2)")
        else:
            pos = c.start(pp2[0]) / total
            if not 0.70 <= pos <= 0.90:
                f.warn(f"PP2 lands at {pos:.0%} of the runtime; 75 to 85 % (V3 SL2)")
    if "stakes_loss" in have or "stakes_gain" in have or c.spec["long"]:
        early = [i for i in tagged if c.start(i) <= 0.2 * total]
        roles_early = {r for i in early for r in c.roles(i)}
        for role, what in (("stakes_loss", "what can be lost"), ("stakes_gain", "what the viewer gains")):
            if role not in roles_early:
                f.warn(f"no {role} beat in the first 20 %: say {what}, concretely (V3 SL9)")
    for i in where("sponsor"):
        inside = any(c.opened.get(lid, 99999) < i < c.closed.get(lid, -1) for lid in c.opened)
        if not inside:
            f.warn(f"{c.beats[i].get('id')}: the sponsor beat sits outside every open loop: place it after a loop "
                   "opens and before it pays off (V3 SR15)")


def check_sections(c, f):
    starts = [i for i in range(1, len(c.beats)) if c.beats[i].get("section") and
              c.beats[i].get("section") != c.beats[i - 1].get("section")]
    if len(starts) >= 3:
        bridged = 0
        for i in starts:
            first = (sentences(c.beats[i].get("narration", "")) or [""])[0]
            if "?" in first or starts_with(first, lex("but", c.lang)):
                bridged += 1
        if bridged / len(starts) < 0.8:
            f.note(f"{bridged} of {len(starts)} sections open on a question or a but: bridge each section with the "
                   "viewer's next question (V3 SR7)")
    emos = [(b.get("emotion") or "").strip().lower() for b in c.beats]
    if sum(1 for e in emos if e) >= 3:
        for i in range(2, len(emos)):
            if emos[i] and emos[i] == emos[i - 1] == emos[i - 2]:
                f.warn(f"{c.beats[i].get('id')}: three beats in a row with the emotion '{emos[i]}': let it rise and "
                       "fall (V2 E11)")
                break
        if c.minutes >= 3 and len({e for e in emos if e}) < 3:
            f.note("fewer than 3 different emotions across the script (V2 E11)")
    start = None
    for i, b in enumerate(c.beats):
        vt = (b.get("visual_type") or "").lower()
        if vt and any(k in vt for k in TALKING_HEAD):
            start = i if start is None else start
            run = c.T["beats"][i]["end"] - c.start(start)
            if c.spec["long"] and run > 20:
                f.note(f"{c.beats[start].get('id')} to {b.get('id')}: {run:.0f} s of talking head: plan an insert "
                       "(V3 SL13)")
                start = None
        else:
            start = None


def check_video(c, f):
    if c.spec["medium"] != "video" or not c.json:
        return
    missing = [b.get("id") for b in c.beats if not (b.get("visual") or "").strip()]
    generic = [b.get("id") for b in c.beats if re.fullmatch(r"\s*(b-?roll|stock footage|footage)\s*\.?\s*",
                                                           (b.get("visual") or ""), re.I)]
    if missing:
        f.warn(f"beats with no visual: {', '.join(missing[:12])} (R1 5.3)")
    if generic:
        f.warn(f"generic visual notes ('b-roll'): {', '.join(generic[:12])} (R1 8)")
    for b, tb in zip(c.beats, c.T["beats"]):
        ov = b.get("on_screen") or ""
        if ov and tb["seconds"] and len(ov) / tb["seconds"] > 20:
            f.warn(f"{b.get('id')}: on-screen text at {len(ov) / tb['seconds']:.0f} characters a second; 20 at most "
                   "(R2 4.3)")
    if c.fmt in ("short", "ad"):
        with_text = sum(1 for b in c.beats if (b.get("on_screen") or "").strip())
        if not c.meta.get("captions") and with_text < len(c.beats) / 2:
            f.warn(f"{with_text} of {len(c.beats)} beats carry on-screen text and captions are off: a muted viewer "
                   "loses the story (set meta.captions for burned captions, or put text on screen; R2 4.3)")


def check_claims(c, f):
    if not c.json:
        for s in c.sents:
            if SOURCE_NEEDED.search(s):
                f.warn(f"a factual line to source: '{s[:70]}'")
                break
        return
    claim_ids = {x.get("id"): x for x in (c.pack or {}).get("claims", [])}
    for b in c.beats:
        nar = b.get("narration", "")
        m = SOURCE_NEEDED.search(nar)
        if m and not b.get("claims"):
            f.gate(f"{b.get('id')}: a factual line with no claim id ('{m.group(0)}'; R1 9.1, V1 SC-10)")
        for cid in b.get("claims") or []:
            if cid == "brief" or str(cid).startswith("brief:"):
                continue    # a fact the client gave in the brief (facts_given)
            if c.pack is not None:
                x = claim_ids.get(cid)
                if not x:
                    f.error(f"{b.get('id')}: claim {cid} is not in the research pack")
                elif x.get("status") not in ("verified", "manual"):
                    f.gate(f"{b.get('id')}: claim {cid} is {x.get('status')}, not verified")


def check_story(c, f):
    """Scene craft (V5): the key moment is rendered, not reported; quotes sound like people; the key line is staged;
    nothing is reconstructed in nonfiction."""
    story = c.script.get("story") or {}
    mode = c.mode
    if mode and mode not in MODES:
        f.warn(f"unknown story mode '{mode}': one of {', '.join(MODES)}")
    ids = {b.get("id"): i for i, b in enumerate(c.beats)}
    km = story.get("key_moment")
    key_beats = [ids[km]] if km in ids else [i for i in range(len(c.beats)) if "key_moment" in c.roles(i)]
    for i in key_beats:
        nar = c.beats[i].get("narration", "")
        labels = EMOTION_EN.findall(nar) if c.lang == "en" else phrase_hits(nar, lex("emotion_label", c.lang, False))
        if labels:
            f.warn(f"{c.beats[i].get('id')}: a feeling named inside the key moment: show it with a thought, a line or "
                   "a body cue, and name it afterwards if at all (V5 HL4)")
        rep = REPORTED_EN.search(nar) if c.lang == "en" else phrase_hits(nar, lex("reported", c.lang, False))
        if rep:
            f.warn(f"{c.beats[i].get('id')}: reported speech in the key moment: give the exact words (V5 HL5)")
        if not QUOTE_RE.search(nar) and not phrase_hits(nar, lex("thought", c.lang)):
            if mode in ("nonfiction", "testimonial", "case_study", "ad"):
                f.note(f"{c.beats[i].get('id')}: the key moment has no spoken line or thought: use the person's real "
                       "words if the research holds them, never invented ones (V5 HL6, H10)")
            else:
                f.warn(f"{c.beats[i].get('id')}: the key moment has no spoken line or thought (V5 HL6)")
    for b in c.beats:
        for q in QUOTE_RE.findall(b.get("narration", "")):
            for s in sentences(q):
                if len(words(s)) > 15:
                    f.warn(f"{b.get('id')}: a quoted sentence of {len(words(s))} words: people speak in short "
                           f"lines (V5 HL7): '{s[:50]}'")
                    break
            formal = word_hits(q, lex("formal_quote", c.lang)) if c.lang in ("en", "banglish") else \
                phrase_hits(q, lex("formal_quote", c.lang, False))
            if formal:
                f.warn(f"{b.get('id')}: report words inside a spoken line ('{formal[0]}'; V5 HL7)")
            if mode in ("nonfiction", "testimonial", "case_study", "ad") and not b.get("claims"):
                f.gate(f"{b.get('id')}: a quote in {mode} mode with no ledger source or approval: quote real, "
                       "approved words only (V5 H10, R3 R12)")
    if mode == "personal":
        quoted = [q for b in c.beats for q in QUOTE_RE.findall(b.get("narration", ""))]
        if quoted and not story.get("reconstructed"):
            f.note("a personal story with quoted lines: list the reconstructed ones in story.reconstructed and get "
                   "the teller's approval (V5 H10)")
    key_line = (story.get("key_line") or "").strip()
    if key_line:
        at = next((i for i, b in enumerate(c.beats) if key_line in b.get("narration", "")), None)
        if at is None:
            f.warn("story.key_line is not in the narration")
        else:
            b = c.beats[at]
            after = b.get("narration", "").split(key_line, 1)[1]
            nxt = c.beats[at + 1] if at + 1 < len(c.beats) else {}
            paused = PAUSE_MARK.search(after[:40]) or float(b.get("pause_s") or 0) >= 0.5 or \
                (not after.strip() and float(nxt.get("pause_s") or 0) >= 0.5)
            if not paused:
                f.warn("the key line has no pause after it: mark [beat] or give its beat a pause_s of 0.7 to 1.2 "
                       "(V5 H7)")


def check_ending(c, f):
    sents = c.sents
    last = " ".join(sents[-2:])
    for p in phrase_hits(last, lex("moral", c.lang)):
        f.warn(f"a stated moral at the end ('{p}'): show the change, end on the payoff (R3 R10)")
    if c.spec["long"] and len(sents) > 10:
        body = " ".join(sents[:int(len(sents) * 0.85)])
        for p in phrase_hits(body, lex("ending", c.lang)):
            f.warn(f"an ending signal before the end ('{p}'): never announce the end (R1 4)")
    everything = c.text + " " + " ".join((b.get("on_screen") or "") + " " + (b.get("visual") or "") for b in c.beats)
    for marker in ("PROOF NEEDED", "NEEDS INPUT"):
        if marker in everything:
            f.gate(f"a [{marker}] marker is still in the script")
    if c.meta.get("paid"):
        cut = max(c.total * 0.3 if c.total else 0, 5)
        early = " ".join((b.get("narration", "") + " " + (b.get("on_screen") or ""))
                         for b, tb in zip(c.beats, c.T["beats"]) if tb["start"] <= cut).lower()
        if not re.search(r"(#ad\b|\bad\b|paid partnership|sponsored|in partnership with|বিজ্ঞাপন|স্পন্সর|পেইড|"
                         r"प्रायोजित|विज्ञापन)", early):
            f.gate("a paid creator with no disclosure early in the video, spoken and on screen (R2 6.4)")
    if not c.spec.get("ad"):
        return
    ctas = phrase_hits(" ".join(sents[-3:]), lex("cta", c.lang))
    if not ctas and not (c.script.get("cta") or {}).get("text"):
        f.error("no call to action at the end: a verb, an object and a reason, spoken and shown (R2 4.5)")
    for p in phrase_hits(c.text, RISK_WORDS):
        f.warn(f"risk word '{p}': needs proof or goes (ad policy, R2 6)")
    m = ATTRIBUTE.search(c.text)
    if m:
        f.error(f"a personal-attribute callout ('{m.group(0)}'): ad policy forbids it (R2 6.2)")
    m = QUICK_MONEY.search(c.text)
    if m:
        f.error(f"a quick-money claim ('{m.group(0)}'; R2 6.1)")


def check_ad_pack(c, f):
    hooks = [h for h in (c.script.get("promise") or {}).get("hook_variants") or []
             if (h.get("spoken") or h.get("visual") or "").strip()]
    if c.spec.get("ad") or len(hooks) > 1:
        kinds = {(h.get("type") or "").strip().lower() for h in hooks if (h.get("type") or "").strip()}
        frames = {(h.get("visual") or "").strip().lower() for h in hooks if (h.get("visual") or "").strip()}
        if c.spec.get("ad") and len(hooks) < 5:
            (f.errors if f.level == "final" else f.notes).append(
                f"{len(hooks)} hook variants: an ad ships 5 hooks of at least 4 types on one body (R2 8 rule 7)")
        if len(hooks) >= 3 and len(kinds) < min(4, len(hooks) - 1):
            f.warn(f"the hook variants use {len(kinds)} hook types: vary the type (result first, question, proof "
                   "shot, mistake, in medias res...), not the wording (R2 2)")
        if len(hooks) >= 3 and len(frames) < 3:
            f.warn("fewer than 3 different first frames across the hook variants (R2 8)")
    brand = (c.meta.get("brand") or "").strip().lower()
    if c.spec.get("ad") and brand:
        early = [b for b, tb in zip(c.beats, c.T["beats"]) if tb["start"] < 5]
        seen = any(brand in " ".join([b.get("narration", ""), b.get("visual", ""), b.get("on_screen", "")]).lower()
                   for b in early)
        if not seen:
            f.warn(f"the product or brand ('{c.meta.get('brand')}') is not shown or said in the first 5 s, as part of "
                   "the action, not a logo slate (R2 1.4)")


def check_rhythm(c, f):
    lens = [len(words(s)) for s in c.sents]
    if c.fmt in ("short", "ad"):
        cap = 18 if c.lang in ("en", "banglish") else 15
        for s, n in zip(c.sents, lens):
            if n > cap:
                f.warn(f"a spoken sentence of {n} words (over {cap}): '{s[:60]}' (R2 8)")
        max_wps = 3.0 * LANG_FACTOR.get(c.lang, 1.0)
        for b in c.beats:
            planned = b.get("seconds")
            n = len(words(b.get("narration", "")))
            if planned and n / float(planned) > max_wps:
                f.warn(f"{b.get('id')}: {n} words in {planned} s ({n / float(planned):.1f} a second; {max_wps:.1f} at "
                       "most; R2 4.1)")
    else:
        for s, n in zip(c.sents, lens):
            if n > 30:
                f.warn(f"a sentence of {n} words: split it for the ear (30 at most; V2 E9): '{s[:60]}'")
        long_cut = 20 if c.lang in ("bn", "hi") else 25
        over = sum(1 for n in lens if n > long_cut)
        if lens and over / len(lens) > 0.10:
            f.warn(f"{over} of {len(lens)} sentences over {long_cut} words: split them for the ear (R1 5.2)")
    short_n = sum(1 for n in lens if n <= 8)
    if len(lens) >= 10 and short_n / len(lens) < 0.15:
        f.note("few short sentences (8 words or fewer): add some for rhythm (R1 9.2)")
    med = R.median(lens)
    if c.spec["long"] and c.lang == "en" and len(lens) >= 10 and not 9 <= med <= 16:
        f.note(f"median sentence length {med} words; pros sit at 9 to 16 for the ear (R1 9.2)")
    # 14 reference creators measured 0.54 to 1.01 (sd over mean of sentence length) and no 12-sentence stretch
    # under 0.25; an even rhythm is a machine tell
    rh = R.rhythm(c.text)
    cv = rh["sd"] / rh["mean"] if rh["mean"] else 0.0
    if rh["sentences"] >= 8 and cv < 0.25:
        f.warn(f"monotone rhythm (sentence length varies {cv:.2f} of the mean; creators measured 0.54 and up): vary "
               "long and short")
    spec_density = R.specificity(c.text)
    if spec_density < 1.0 and c.lang == "en" and c.spec["long"]:
        f.warn(f"specificity {spec_density} details per 100 words: add numbers, names, places (R1 9.2)")
    c.stats.update({"median_sentence": med, "rhythm_cv": round(cv, 2), "specificity": spec_density})


def check_length(c, f):
    target = c.meta.get("target_seconds")
    if target and c.total:
        off = (c.total - target) / target
        if abs(off) > 0.25:
            f.error(f"runtime {c.total:.0f} s against a target of {target} s ({off:+.0%})")
        elif abs(off) > 0.10:
            f.warn(f"runtime {c.total:.0f} s against a target of {target} s ({off:+.0%})")
    if c.spec.get("max_s") and c.total > c.spec["max_s"]:
        f.error(f"runtime {c.total:.0f} s is over the {c.spec['max_s']} s limit for {c.fmt}")


# words too common to show that an objection or a goal was addressed
GENERIC = {"that", "this", "with", "from", "have", "your", "about", "another", "will", "what", "when", "they", "their",
           "there", "which", "into", "just", "really", "video", "videos", "thing", "things", "people", "product", "more",
           "some", "than", "then", "them", "these", "those", "would", "could", "should", "been", "being", "does",
           "make", "made", "also", "only", "very", "much", "many", "most", "such", "like", "want", "wants", "know",
           "knows", "watch", "end", "channel", "brand", "other"}
BN_GENERIC = {"কি", "কী", "না", "তো", "এই", "আর", "ও", "যে", "কেন", "হয়", "করে", "থেকে", "একটা", "আমি", "আপনি",
              "তারা", "এটা", "সেটা", "কিন্তু", "তবে", "জন্য", "দিয়ে"}
GOAL_CTA = {"follow": ["follow", "ফলো"], "subscribe": ["subscribe", "সাবস্ক্রাইব"],
            "order": ["order", "অর্ডার", "inbox", "ইনবক্স"], "buy": ["buy", "shop", "কিনুন", "কিনতে"],
            "comment": ["comment", "কমেন্ট"], "share": ["share", "শেয়ার"], "sign": ["sign up", "join"],
            "visit": ["visit", "link", "লিংক"], "call": ["call", "ফোন"]}


def content_words(text):
    out = []
    for w in re.findall(r"[a-z]{4,}|[\u0980-\u09ff]{3,}", (text or "").lower()):
        if w not in GENERIC and w not in BN_GENERIC:
            out.append(w)
    return out


def mentions(text, word):
    low = (text or "").lower()
    return word in low or (word.isascii() and len(word) > 6 and word[:6] in low)


def check_brief(c, f, brief):
    """The brief's audience objections are answered, its goal gets its call to action, nothing it bans slips in
    (the 2026-09-26 benchmark: a draft that skipped the brief's objection and its follow ask lost 0 to 3)."""
    aud = brief.get("audience") or {}
    text = c.text
    bangla = bool(re.search(r"[\u0980-\u09ff]", text))
    for obj in aud.get("objections") or []:
        words = content_words(obj)
        if not words:
            continue
        if bool(re.search(r"[\u0980-\u09ff]", obj)) != bangla:
            f.note(f"the objection '{obj}' is in another language than the script: check by eye that it is answered, "
                   "and write objections in the audience's own words")
            continue
        if not any(mentions(text, w) for w in words):
            f.warn(f"the audience's objection '{obj}' is never answered: voice it in their words, then answer it "
                   "(R5 4, V6-R7)")
    goal = (brief.get("goal") or "").lower()
    if c.spec["medium"] in ("video", "listen"):
        for key, verbs in GOAL_CTA.items():
            if key in goal and not any(v in text.lower() for v in verbs):
                f.warn(f"the brief's goal asks for '{key}' but the narration never says it: say the ask as well as "
                       "showing it (R2 4.5)")
    for bad in brief.get("must_avoid") or []:
        if isinstance(bad, str) and 0 < len(bad.split()) <= 4 and bad.lower() in text.lower():
            f.error(f"'{bad}' is on the brief's must-avoid list")


def lint_script(script, pack=None, level="draft", brief=None):
    c = Ctx(script, pack)
    f = Findings(level)
    if not c.sents:
        return {"ok": False, "errors": ["no narration"], "warnings": [], "notes": [], "stats": {}}
    c.stats = {"format": c.fmt, "lang": c.lang, "wpm": c.wpm, "seconds": c.total, "words": len(words(c.text)),
               "sentences": len(c.sents), "beats": len(c.beats), "mode": c.mode or None}
    check_words(c, f)
    check_opening(c, f)
    check_engine(c, f)
    if c.json:
        check_loops(c, f)
        check_tension(c, f)
        check_roles(c, f)
        check_sections(c, f)
        check_story(c, f)
        check_ad_pack(c, f)
    check_video(c, f)
    check_claims(c, f)
    check_ending(c, f)
    check_rhythm(c, f)
    check_length(c, f)
    if brief:
        check_brief(c, f, brief)
    return {"ok": not f.errors, "errors": f.errors, "warnings": f.warnings, "notes": f.notes, "stats": c.stats,
            "timing": c.T["beats"]}


# ------------------------------------------------------------------------------------------------------- blog

AFFILIATE = re.compile(r"\]\((https?://[^)]*(amzn\.to|[?&]tag=|[?&]ref=|affiliate|/aff/|go\.skimresources|"
                       r"shareasale|impact\.com|awin1)[^)]*)\)", re.I)
DISCLOSURE = re.compile(r"(affiliate|commission|we earn|i earn|paid link|sponsored|partner link|কমিশন|অ্যাফিলিয়েট)",
                        re.I)


def lint_blog(script, level="draft", keyword=None):
    text = script["text"]
    lang = script["meta"]["lang"]
    f = Findings(level)
    title = next((m.group(1).strip() for m in re.finditer(r"^#\s+(.+)$", text, re.M)), "")
    if not title:
        f.warn("no title (a line starting with '# ')")
    elif len(title) > 70:
        f.error(f"title is {len(title)} characters; 70 at most (aim for 60; R4 5.2)")
    elif len(title) > 60:
        f.warn(f"title is {len(title)} characters; aim for 60 or fewer (R4 5.2)")
    if EM in text or re.search(r"\s" + EN + r"\s", text):
        f.error("an em dash or a spaced en dash")
    for p in phrase_hits(text, AI_PHRASES + ["in today's", "in conclusion", "it's important to note"]):
        f.warn(f"machine tell: '{p}'")
    for p in phrase_hits(text, POP_SCIENCE):
        f.error(f"pop-science claim ('{p}')")
    if re.search(r"\[(?:click here|here|read more|this article)\]\(", text, re.I):
        f.error("an anchor text like 'click here' or 'read more': say where the link goes (R4 5.5)")
    if "NEEDS INPUT" in text or "PROOF NEEDED" in text:
        f.gate("a [NEEDS INPUT] or [PROOF NEEDED] marker is still in the draft: get the input or cut the line")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text)
             if p.strip() and not p.strip().startswith(("#", "|", "-", "*", ">"))]
    for p in paras:
        n = len(sentences(p))
        if n > 6:
            f.error(f"a paragraph of {n} sentences: 1 to 4 (R4 5.4): '{p[:50]}'")
        elif n > 4:
            f.warn(f"a paragraph of {n} sentences: 1 to 4 (R4 5.4): '{p[:50]}'")
        if SOURCE_NEEDED.search(p) and not re.search(r"\]\(https?://|https?://", p):
            f.error(f"a figure or study with no link in its paragraph: '{p[:60]}' (R4 6.1)")
    for p in re.split(r"\n\s*\n", text):
        if AFFILIATE.search(p) and not DISCLOSURE.search(p):
            f.error("an affiliate link with no disclosure next to it (R4 7, FTC)")
    if re.search(r"\bnot only\b.{1,80}\bbut also\b", text, re.I):
        f.warn("'not only ... but also': say the stronger half (R4 10.3)")
    if keyword:
        heads = [h for h in re.findall(r"^#{2,6}\s+(.+)$", text, re.M) if keyword.lower() in h.lower()]
        if len(heads) > 2:
            f.error(f"the keyword '{keyword}' is in {len(heads)} subheads; two at most (R4 10.1)")
    body = re.sub(r"^#+\s.*$", "", text, flags=re.M)
    sents = sentences(body)
    lens = [len(words(s)) for s in sents]
    if lens and sum(1 for n in lens if n > 25) / len(lens) > 0.15:
        f.warn("over 15 % of sentences are longer than 25 words (R4 5.4)")
    if lens and sum(lens) / len(lens) > 20:
        f.note(f"average sentence {sum(lens) / len(lens):.0f} words; under 20 reads easier (R4 10.1)")
    first100 = " ".join(words(body)[:100])
    f.note(f"check by eye: the answer is in the first 100 words ('{first100[:120]}...')")
    stats = {"format": "blog", "lang": lang, "title_chars": len(title), "words": len(words(body)),
             "sentences": len(sents), "paragraphs": len(paras), "specificity": R.specificity(body)}
    return {"ok": not f.errors, "errors": f.errors, "warnings": f.warnings, "notes": f.notes, "stats": stats}


def voice_pass(script):
    """natural-text's lint on the words (codex-design copylint): its findings join the script's."""
    if not DESIGN.exists():
        return {"ran": False, "why": f"{DESIGN} not found (install codex-design)"}
    lang = script["meta"]["lang"]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
        fh.write(text_of(script))
        tmp = fh.name
    role = "body" if script["kind"] == "blog" else "voiceover"
    cmd = [sys.executable, str(DESIGN), "copylint", "--caption", tmp, "--role", role,
           "--lang", "bn" if lang == "banglish" else lang]
    if lang in ("bn", "banglish"):
        cmd += ["--locale", "BD"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return {"ran": False, "why": "copylint timed out after 300 s"}
    finally:
        os.unlink(tmp)
    # copylint's exit codes: 0 fine, 2 a quality gate failed (it ran and found errors), 1 a usage or tool error;
    # a 1, anything else, or no summary line means it did not run
    if proc.returncode not in (0, 2) or '"errors"' not in proc.stdout:
        return {"ran": False, "why": (proc.stderr or proc.stdout or f"exit {proc.returncode}")[-300:]}
    findings = [ln.strip() for ln in proc.stdout.splitlines() if ln.startswith(("error", "warning", "note"))]

    def of(kind):         # the message without its severity word: the caller files it under errors or warnings
        return [x.split(None, 1)[1] if " " in x else x for x in findings if x.startswith(kind)]
    return {"ran": True, "findings": findings, "errors": of("error"), "warnings": of("warning")}
