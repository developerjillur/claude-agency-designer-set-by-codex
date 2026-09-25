"""Copy that reads human: the lint behind `design.py copylint` and the rendered-text checks.

Pure Python, no dependencies. The word lists and patterns come from the research in references/copy.md (AI-writing
tells, natural Bangladeshi Bengali, hooks and calls to action). Every finding carries a plain suggestion; the lint
never rewrites copy by itself (a person, or `copyjudge`, chooses the words).

A finding is a dict: {"severity": "error" | "warning" | "note", "code": str, "message": str, "suggest": str}.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

BN = "ঀ-৿"                     # Bengali block
NOT_BN_BEFORE = f"(?<![{BN}])"
NOT_BN_AFTER = f"(?![{BN}])"
EMOJI_RX = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
HASHTAG_RX = re.compile(r"(?<![\w#])#[\wঀ-৿_]+")

# ------------------------------------------------------------------------------------------------ platforms
# Characters shown before the feed cuts a caption ("… more"), and the counts that stay native. Sources and dates
# are in references/copy.md; the numbers move, so check them there before a campaign.
PLATFORM = {
    # preview_chars: the caption shown before "more" on a phone; hashtags: (native low, hard or native high)
    "instagram": {"preview_chars": 125, "hashtags": (0, 3), "hashtag_cap": 5, "emoji_max": 3},   # cap 5 since Dec 2025
    "facebook": {"preview_chars": 80, "hashtags": (0, 2), "emoji_max": 3},                      # "See more" ≈ 80
    "linkedin": {"preview_chars": 140, "hashtags": (0, 3), "emoji_max": 2},                     # 210 desktop, 140 mobile
    "youtube": {"title_chars": 60, "hashtags": (0, 3), "emoji_max": 1},                          # ≈ 60 in search
    "tiktok": {"preview_chars": 90, "hashtags": (3, 5), "hashtag_cap": 5, "emoji_max": 3},       # cap 5 (Aug 2025)
    "x": {"max_chars": 280, "hashtags": (0, 1), "emoji_max": 2},
    "threads": {"max_chars": 500, "hashtags": (0, 1), "emoji_max": 2},
    # beyond the feed: the same voice rules, without feed limits
    "whatsapp": {"hashtags": (0, 0), "emoji_max": 3},
    "email": {"preview_chars": 90, "hashtags": (0, 0), "emoji_max": 1},     # the preheader shows about 90
    "web": {"hashtags": (0, 0), "emoji_max": 1},
    "sms": {"max_chars": 160, "hashtags": (0, 0), "emoji_max": 1},          # 70 per part in Bengali (Unicode)
    "voiceover": {"hashtags": (0, 0), "emoji_max": 0, "spoken": True},      # reels, ads, explainers: read aloud
    "print": {"hashtags": (0, 1), "emoji_max": 0},                          # posters, flyers, cards, signs, packs
}
SPOKEN_ROLES = re.compile(r"script|voice|narrat|\bvo\b|spoken|read_aloud", re.I)

# ------------------------------------------------------------------------------------------------ English
# Tier 1: one sighting is a tell (Wikipedia "Signs of AI writing" lists and corpus studies: Kobak 2024, Juzek & Ward
# 2024, the Washington Post 2025; repos humanizer, stop-slop, unslop, SlopMonster). Literal uses (robust steel) are
# fine; the lint cannot tell, so it warns and a person decides.
AI_WORDS_EN = {
    "delve": "look at, dig into", "delves": "looks at", "underscores": "shows", "underscore": "show",
    "showcasing": "showing", "showcases": "shows", "testament": "proof, sign", "tapestry": "mix, range",
    "boasts": "has", "garner": "get, win", "pivotal": "key, turning", "groundbreaking": "new, first",
    "meticulous": "careful", "meticulously": "carefully", "interplay": "mix", "bolster": "back, strengthen",
    "realm": "field, area", "multifaceted": "varied", "unveil": "show, launch", "unveils": "shows, launches",
    "revolutionize": "change", "revolutionary": "new, first", "elevate": "improve, lift", "unlock": "get, open",
    "unleash": "release, use", "embark": "start", "game-changer": "(name the change)",
    "game-changing": "(name the change)", "cutting-edge": "new, latest", "transformative": "(name the result)",
    "nestled": "sits, is", "in the heart of": "in, central", "breathtaking": "(describe it)",
    "diverse array": "range", "ever-evolving": "changing", "paramount": "most important",
    "supercharge": "speed up", "seamlessly": "easily", "leverage": "use",
    "harness": "use", "synergy": "(say what works together)", "holistic": "whole", "next-gen": "new",
    "world-class": "(name the proof)", "best-in-class": "(name the proof)", "rich heritage": "long history",
    "look no further": "(cut it)", "in today's fast-paced world": "(cut it)", "unlock your potential": "(say the result)",
    "take it to the next level": "(say the result)", "hidden gem": "(say what is special)",
    "must-visit": "(say why)", "a feast for the senses": "(describe one sense)",
    # Reinhart et al. 2025 (PNAS), Juzek and Ward 2024, Liang et al. 2024: tens of times the human rate
    "camaraderie": "team spirit, friendship", "palpable": "(say what people felt)", "commendable": "good (say why)",
    "intricacies": "details",
}
# Tier 2: common words that become a tell in a cluster (two or more in one piece).
AI_WORDS_EN_SOFT = {
    "crucial": "important", "vibrant": "lively, busy", "robust": "strong", "foster": "build",
    "enhance": "improve", "intricate": "detailed", "enduring": "lasting", "valuable": "useful",
    "additionally": "also", "moreover": "also", "comprehensive": "full", "streamline": "simplify",
    "journey": "process, trip", "landscape": "market, field", "navigate": "handle", "renowned": "known for",
    "profound": "deep", "nuanced": "subtle", "empower": "let, help", "curated": "chosen", "resonate": "appeal",
    "bustling": "busy", "emphasizing": "saying", "highlighting": "showing", "discover": "(the real verb)",
    "experience": "(the real verb)", "elevated": "better", "effortless": "easy", "innovative": "new",
    "seamless": "smooth, easy",  # literal in product names (seamless leggings): a tell only in a cluster
    "amidst": "among, during", "solace": "comfort", "unravel": "figure out", "fleeting": "short",
    "unspoken": "(say it)", "grapple": "deal with", "ignite": "start, spark", "cacophony": "noise",
    "surpassing": "beating", "comprehending": "understanding", "advancements": "improvements", "aligns with": "fits",
}
_EN = [
    # (regex, what it is, the fix, severity)
    (r"(?:\bnot|n't)\s+(?:just|only|merely|simply)\b[^!?]{0,80}?(?:\b(?:but|it'?s|it is)\b)",
     "the 'not just X, it's Y' turn", "say the one true thing plainly", "warning"),
    (r"\bmore than (?:a|an|just a|just an|just) [\w-]+,\s+(?:it'?s|it is)\b", "'more than X, it's Y'",
     "say what it is", "warning"),
    (r"\bwhere [\w-]+ meets [\w-]+", "'where X meets Y'", "say what it is", "warning"),
    (r"\b(?:the )?perfect (?:blend|balance|harmony|mix) of\b", "'the perfect blend of'", "name the two things and "
     "why they work", "warning"),
    (r"\b(?:step|dive|escape) into (?:a|the) world of\b|\ba world of (?:flavou?rs?|luxury|comfort|possibilit)",
     "'a world of'", "name the thing", "warning"),
    (r"\blike never before\b", "'like never before'", "say what is new", "warning"),
    (r"\b(?:tells?|telling) (?:a|its|your) (?:own )?story\b", "'tells a story'", "tell the story in one fact",
     "warning"),
    (r"\b(?:crafted|made|designed|baked) with (?:love|passion|care)\b", "'made with love'", "say how it is made",
     "warning"),
    (r"\b(?:start|begin) your journey\b|\byour journey (?:to|with)\b", "'your journey'", "say the first step",
     "warning"),
    (r"\byou deserve (?:it|this|the best)\b|\bdeserves? the best\b", "'you deserve it'", "give the reason", "warning"),
    (r"\bevery step of the way\b|\bcommitted to (?:delivering|providing|excellence)\b|\bwe'?ve got you covered\b",
     "a corporate stock phrase", "say what you do", "warning"),
    (r"\b(?:indulge in|redefines?|treat yourself to)\b", "a hype verb", "say what it is", "warning"),
    (r"\bseamless (?:experience|integration|transition|blend|journey|solution)s?\b", "'a seamless experience'",
     "say what is easy about it", "warning"),
    (r"\bNot (?:a |an |the )?[\w-]+\.\s+Not (?:a |an |the )?[\w-]+\.", "a negative countdown ('Not X. Not Y.')",
     "say what it is", "warning"),
    (r"\bwhether you'?re\b[^.!?]{0,60}\bor\b", "'Whether you're X or Y'", "name one reader", "warning"),
    (r"\b(?:The|Your) (?:result|answer|secret|catch|best part|kicker|twist)\?", "a question the copy answers itself",
     "state the fact", "warning"),
    (r"\b(?:here'?s the thing|here'?s why|here'?s what|let'?s dive in|let'?s break (?:it|this) down|without further "
     r"ado|buckle up|in conclusion|it'?s worth noting|let'?s be honest|the truth is)\b", "sign-posting",
     "cut it and start with the point", "warning"),
    (r"\b(?:in today'?s (?:fast-paced|digital|modern|competitive|ever-changing)|in a world where)\b",
     "an 'In today's world' opener", "start with the reader's problem or the fact", "warning"),
    (r"\b(?:marks? a (?:pivotal|significant|major|new) (?:moment|milestone|shift|chapter)|stands? as a testament|"
     r"plays? a (?:pivotal|crucial|vital|key) role)\b", "inflated significance", "say what happened", "warning"),
    (r",\s+(?:ensuring|highlighting|reflecting|showcasing|emphasizing|fostering|underscoring|contributing to|"
     r"solidifying|cementing|paving the way)\b", "a trailing '-ing' clause", "make it a sentence with a plain verb, "
                                                                          "or cut it", "warning"),
    (r"\b(?:let that sink in|game\. changer|think about it\.|and that'?s the point)\b", "a punchline closer",
     "end on the last concrete fact", "warning"),
    (r"\bfrom [\w-]+ to [\w-]+(?: to [\w-]+)?,\s+(?:we|our|this|it)\b", "a false range ('From X to Y, we…')",
     "name the one thing", "warning"),
    (r"\b(?:may potentially|could possibly|might perhaps|arguably perhaps)\b", "stacked hedges", "one hedge or none",
     "warning"),
    (r"\b(?:experts (?:agree|say)|studies (?:show|suggest)|research (?:shows|suggests)|as seen on)\b",
     "borrowed authority", "name the source, or cut the claim", "warning"),
    (r"\b(?:the future (?:looks|is) bright|continues to thrive|the possibilities are endless|and so much more|"
     r"the rest is history)\b", "a stock ending", "end on the last fact", "warning"),
    (r"\b(?:look no further|say goodbye to|that'?s where we come in|imagine a (?:world|life|day)|more than just|"
     r"you deserve the best)\b", "a stock ad construction", "say what the product does", "warning"),
    (r"\?\s+Meet\b", "'[Problem]? Meet [solution].'", "say what it does", "warning"),
    (r"\b(?:big news|exciting news|(?:we'?re|we are) (?:thrilled|excited|delighted|proud) to (?:announce|share|"
     r"introduce|unveil))\b", "launch hype", "lead with the news itself", "warning"),
    (r"\b(?:drop (?:a|an|your) [^.!?]{0,20} in the comments|hot take:|tag (?:a friend|someone|the \w+) who|"
     r"smash that|who'?s with me)", "engagement bait", "ask a real question, or none", "warning"),
    (r"\b(?:act now|don'?t miss out|hurry|limited time only|while stocks last|last chance)\b",
     "urgency without a fact", "give the real date or quantity (until 30 Sept, 40 left)", "warning"),
    (r"\b(?:i hope this helps|here'?s (?:a|the|your) (?:caption|post|headline|tagline)|certainly!|as an ai|great "
     r"question)\b|oaicite|contentreference|utm_source=chatgpt", "a chatbot leftover", "delete it", "error"),
    (r"\b\d[\d,.]*\+?\s*(?:k\s+)?(?:happy|satisfied|trusted|loyal)?\s*(?:customers|clients|users|members|homeowners)\b",
     "a customer count", "use it only with a source in the brief, or mark it as a placeholder", "note"),
    (r"→", "an arrow in running copy", "write 'to' or 'then'", "note"),
    # the tidy, self-announcing shape (SlopShape, Madler 2026: structure alone separates AI posts at 98 F1)
    (r"\b(?:in this (?:post|article|guide|thread|carousel|video)|we(?:'ll| will) (?:cover|explore|walk you through|"
     r"dive into|break down)|here'?s what you'?ll (?:learn|get))\b", "a roadmap line (the post announces itself)",
     "start with the first real point", "warning"),
    (r"(?:^|[.!?]\s+|\n)(?:in short|in summary|to sum up|ultimately|the bottom line|at the end of the day)\b",
     "a closer that restates the point", "end on the last new fact or the one ask", "warning"),
    (r"\b(?:gone are the days|the old way of)\b", "an old-against-new frame", "say what it does now", "note"),
    (r"\b(?:costing you|every day you wait|before it'?s too late|make or break)\b", "escalated stakes",
     "state the real cost once, with its number", "note"),
    (r"\bAI[- ]powered\b|\bartificial intelligence\b", "'AI' as the selling point",
     "lead with what it does for the buyer; the word lowers trust in consumer copy (WSU 2024), most in finance, "
     "health and costly products", "note"),
]
AI_PATTERNS_EN = [(re.compile(rx, re.I), what, fix, sev) for rx, what, fix, sev in _EN]
# verbs whose other forms run just as high in model text (Kobak et al. data, 2024: bolstered, garnered, showcased,
# delved, leveraging, unveiled at 2.4 to 12.3 times their expected rate); words with a common literal sense (unlock,
# harness) stay exact
INFLECT_EN = {"delve", "bolster", "garner", "showcase", "unveil", "underscore", "embark", "revolutionize", "supercharge",
              "boast", "elevate", "leverage", "delves", "unveils", "boasts", "showcasing", "underscores"}


def _inflected(w: str) -> str:
    """A regex for the word and, for the verbs above, its -s, -d, -ed and -ing forms."""
    base = re.sub(r"(?:s|ing)$", "", w) if w in ("delves", "unveils", "boasts", "underscores", "showcasing") else w
    if base not in INFLECT_EN:
        return re.escape(w)
    stem = base[:-1] if base.endswith("e") else base
    return re.escape(stem) + ("(?:e|es|ed|ing)" if base.endswith("e") else "(?:s|ed|ing)?")


GENERIC_CTA_EN = re.compile(r"^\s*(?:get started|learn more|click here|submit|find out more|read more|discover more|"
                            r"see more|explore now|check it out)\s*[.!]?\s*$", re.I)

# ------------------------------------------------------------------------------------------------ Bengali (BD)
# formal, old or translated -> the everyday Bangladeshi word (research: brand posts 2024-26, the Bangla Academy, Prothom
# Alo, Niropekho and Bigganchinta on AI Bengali; copy.md §3). Standard ad phrases stay: শর্ত প্রযোজ্য, সীমিত সময়ের অফার.
BN_FORMAL = {
    "ক্রয় করুন": "কিনুন", "ক্রয়": "কেনা", "বিক্রয়": "বিক্রি", "প্রদান করুন": "দিন", "প্রদান": "দেওয়া",
    "গ্রহণ করুন": "নিন", "প্রেরণ করুন": "পাঠান", "প্রাপ্ত হবেন": "পাবেন", "অবগত হোন": "জেনে নিন", "অবগত": "জানা",
    "অবহিত করা যাচ্ছে": "জানিয়ে রাখি", "পরিদর্শন করুন": "ঘুরে আসুন", "নিবন্ধন": "রেজিস্ট্রেশন",
    "অংশগ্রহণ করুন": "যোগ দিন", "নির্বাচন করুন": "বেছে নিন", "সংগ্রহ করুন": "নিয়ে নিন", "আস্বাদন করুন": "চেখে দেখুন",
    "পরিধান করুন": "পরুন", "মতামত প্রদান করুন": "মতামত জানান", "যোগাযোগ স্থাপন করুন": "ইনবক্স করুন / কল করুন",
    "সহায়তা": "সাহায্য", "সম্পন্ন": "শেষ", "প্রারম্ভ": "শুরু", "সূচনা": "শুরু", "সমাপ্তি": "শেষ", "অত্যন্ত": "খুব",
    "অদ্য": "আজ", "আগামীকল্য": "কাল", "অবিলম্বে": "এখনই", "তৎক্ষণাৎ": "সঙ্গে সঙ্গে", "শীঘ্রই": "শিগগিরই",
    "সর্বদা": "সবসময়", "পুনরায়": "আবার", "বর্তমানে": "এখন", "পরবর্তীতে": "পরে", "অতঃপর": "তারপর",
    "নিমিত্তে": "জন্য", "উদ্দেশ্যে": "জন্য", "ব্যতীত": "ছাড়া", "সহিত": "সঙ্গে", "উক্ত": "এই", "নিম্নলিখিত": "নিচের",
    "উপরোক্ত": "ওপরের", "সুবিধার্থে": "সুবিধার জন্য", "অনুগ্রহপূর্বক": "দয়া করে (বা বাদ দিন)", 
    "মূল্যহ্রাস": "ছাড়", "স্বল্পমূল্যে": "কম দামে", "সাশ্রয়ী মূল্যে": "কম দামে", "প্রয়োজনীয়": "দরকারি",
    "পর্যাপ্ত": "যথেষ্ট", "সুসংবাদ": "সুখবর", "উপলব্ধ": "পাওয়া যাচ্ছে", "গ্রাহকবৃন্দ": "গ্রাহকেরা",
    "বাসস্থান": "বাসা", "প্রতীক্ষা করুন": "আসছে…", "অবলোকন": "দেখা",
    "তদুপরি": "তার ওপর", "অধিকন্তু": "এ ছাড়া", "পরিশেষে": "শেষে", "এতদ্বারা": "(বাদ দিন)", "প্রস্তুতকৃত": "বানানো",
    "হস্তনির্মিত": "হাতে বানানো", "যুগান্তকারী": "(প্রমাণটা বলুন)", "বিপ্লবী": "(কী বদলায়, সেটা বলুন)",
    "উন্নীত করুন": "(ফলটা বলুন)", "অভিজ্ঞতা নিন": "(কাজটা বলুন: চেখে দেখুন, ঘুরে যান)", "সুবর্ণ সুযোগ": "সুযোগ",
    "অতুলনীয়": "(প্রমাণটা বলুন)", "অনন্য অভিজ্ঞতা": "(কী আলাদা, সেটা বলুন)",
    "আপনি কি কখনো ভেবে দেখেছেন": "(সরাসরি কথাটা বলুন)",
}
# Standard words that are only stiffer than everyday speech: a note, not a warning. Bangladeshi brands and papers use
# them (bKash বর্তমানে, Easy Fashion আজই সংগ্রহ করুন, Prothom Alo আর্থিক সহায়তা, জন্ম নিবন্ধন is the legal term);
# measured on natural and robotic corpora, 2026-09-24. সুস্বাদু, মূল্যছাড় and দ্রুততম left the list for the same reason.
BN_FORMAL_SOFT = {"সহায়তা", "বর্তমানে", "প্রয়োজনীয়", "সংগ্রহ করুন", "শীঘ্রই", "সম্পন্ন", "নিবন্ধন", "পর্যাপ্ত",
                  "অংশগ্রহণ করুন", "নির্বাচন করুন", "উদ্দেশ্যে", "বিক্রয়", "বিপ্লবী", "সুবর্ণ সুযোগ", "সাশ্রয়ী মূল্যে",
                  "স্বল্পমূল্যে", "সূচনা", "সুসংবাদ"}
# English marketing lines translated word for word: what an LLM or a translation tool writes, not a Dhaka page.
BN_CALQUES = [(re.compile(rx), what) for rx, what in (
    (NOT_BN_BEFORE + "(?:শুধু|শুধুমাত্র|কেবল) (?:একটি|একটা) [^,।!?]{1,25} নয়", "a calque of 'not just X, it's Y'"),
    (NOT_BN_BEFORE + "(?:আবিষ্কার|অন্বেষণ) করুন", "a calque of 'discover / explore'"),
    ("নতুন উচ্চতায়", "a calque of 'to new heights'"),
    ("নিখুঁত (?:সমন্বয়|মিশ্রণ|মেলবন্ধন)", "a calque of 'the perfect blend'"),
    ("আরাম থেকে", "a calque of 'from the comfort of your home'"),
    ("প্রতিটি মুহূর্ত", "a calque of 'every moment'"),
    (NOT_BN_BEFORE + "এখানে আছ(?:ে|ি)" + NOT_BN_AFTER, "a calque of 'we're here to help'"),
    (NOT_BN_BEFORE + "(?:উদযাপন|উদ্‌যাপন) করুন", "a calque of 'celebrate' as a call to action"),
    (NOT_BN_BEFORE + "দাবি করুন", "a calque of 'claim your X'"),
    ("প্রতিশ্রুতিবদ্ধ", "a calque of 'committed to' (corporate)"),
    ("(?:অবিস্মরণীয়|স্বাদের|আপনার|এক) যাত্রা", "'journey' as a metaphor"),
    ("গল্প (?:বলুক|বলে)" + NOT_BN_AFTER, "a calque of 'tells a story'"),
    ("^\\s*(?:ফলাফল|রহস্য|উত্তর|সমাধান)\\?", "a question the copy answers itself ('The result?')"),
)]
VISARGA_ABBR = re.compile("(?:মোঃ|মোসাঃ|ডাঃ|বিঃদ্রঃ|দ্রঃ|লিঃ|প্রাঃ|কোঃ)")
SADHU_EXCEPT = re.compile("পাইলট|পাইলস|আসিয়ান")
BN_PATTERNS = [
    (re.compile(NOT_BN_BEFORE + "(?:করি(?:য়া|তে|বে|ল)|হই(?:য়া|তে|বে|ল)|দিয়াছ|লইয়া|গিয়াছ|আসিয়া|পাই(?:বে|য়া|ল)|যাহা|"
                "তাহা|ইহা|উহা)" + f"[{BN}]*" + NOT_BN_AFTER),
     "sadhu form (mixed with চলিত it is গুরুচণ্ডালী)", "চলিত রূপ: হবে, হয়ে, করে, করতে, পাবেন, যা, তা"),
    (re.compile(NOT_BN_BEFORE + "(?:প্রদানের মাধ্যমে|গ্রহণ করা যাবে|করা হয়ে থাকে|করা হইয়া থাকে|প্রদান করা হবে|"
                "প্রদান করা হচ্ছে)" + NOT_BN_AFTER),
     "a passive or noun-chain notice", "কাজটা সক্রিয়ভাবে বলুন: পেমেন্ট করলেই ক্যাশব্যাক"),
    (re.compile("আপনার [^ ]+কে উন্নত করুন|আপনার যাত্রা শুরু করুন|যাত্রা শুরু হোক|আপনার অভিজ্ঞতাকে"),
     "a translated marketing cliché", "কাজটা সরাসরি বলুন"),
    (re.compile("দাম জানতে ইনবক্স|দাম জানতে মেসেজ|মূল্য জানতে ইনবক্স"),
     "the price hidden behind the inbox (buyers dislike it; Bangladesh's Digital Commerce Guideline 2021 §3.1.2 asks "
     "for clear prices)", "দামটা লিখে দিন: ৳১,২৯০"),
    # found by the copy judge in every run of a fast-path post (2026-09-25): "৮৫০ টাকা প্রতি কেজি" reads translated
    (re.compile(f"(?:[০-৯0-9][০-৯0-9,.]*\\s*টাকা|৳\\s*[০-৯0-9][০-৯0-9,.]*)\\s+প্রতি\\s*(?:কেজি|পিস|লিটার|গ্রাম|ডজন|"
                f"হালি|বক্স|প্যাকেট|প্লেট|কাপ|জন|রাত|মাস|ঘণ্টা|দিন|সপ্তাহ|বছর|সেট|কপি|ইউনিট|মিটার|গজ|টিকিট|"
                f"টি|টা)[{BN}]*"),
     "the price before প্রতি and its unit is English word order ('850 taka per kg')",
     "the unit first, the way shops say it: প্রতি কেজি ৮৫০ টাকা, or কেজি ৮৫০ টাকা"),
    (re.compile(f"[{BN}]{{2,}}ঃ(?=\\s|$)"), "a visarga (ঃ) used as a colon (বিস্তারিতঃ)", "কোলন লিখুন: বিস্তারিত:"),
    (re.compile(f"[{BN}]{{3,}}\\.(?=\\s|$)"), "an English full stop at the end of a Bengali sentence",
     "দাঁড়ি (।) লিখুন; '.' শুধু সংক্ষেপে (ড., লি.)"),
    (re.compile("ফ্রী|সরকারী|জানুয়ারী|ফেব্রুয়ারী|শ্রেণী|এখনি(?![ং])"),
     "a spelling the Bangla Academy changed", "ফ্রি, সরকারি, জানুয়ারি, ফেব্রুয়ারি, শ্রেণি, এখনই"),
]
# Bangladesh vs West Bengal (and Hindu-household usage): a warning for words most Bangladeshi readers do not use in
# brand copy; kinship words are notes, because Bangladeshi Hindu families use them too.
BN_WB_FOR_BD = {"জল": "পানি", "স্নান": "গোসল", "নিমন্ত্রণ": "দাওয়াত", "নেমন্তন্ন": "দাওয়াত", "জলখাবার": "নাস্তা",
                "নুন": "লবণ", "লঙ্কা": "মরিচ", "পরিষেবা": "সেবা", "ইদ": "ঈদ"}
BN_KIN_NOTE = {"মাসি": "খালা", "কাকা": "চাচা", "বউদি": "ভাবি", "ঠাকুমা": "দাদি", "দিদিমা": "নানি",
               "আশীর্বাদ": "দোয়া"}
BN_TUMI_VERBS = re.compile(f"{NOT_BN_BEFORE}(?:করো|দেখো|নাও|দাও|চলো|এসো|যাও|খাও|জানো|রাখো|পড়ো|শোনো){NOT_BN_AFTER}")
BN_APNI = re.compile(f"{NOT_BN_BEFORE}(?:আপনি|আপনার|আপনাকে|আপনারা){NOT_BN_AFTER}")
BN_CTA_END = re.compile("(?:ুন|িন|ান|েন|ো|াও|ও)[।!]?\\s*$")  # করুন, নিন, যান, করো, নাও, and the spoken আসেন, থাকেন
# Measured 2026-09-24 on 724 brand texts, 1,457 Bangladeshi ads and 3,322 news passages with their ChatGPT
# paraphrases (references/research/voice-bangla.md): each poetic word alone is ordinary written Bangla, a stack of them
# is the tell; particles, reactions and slang read spoken one at a time and fake when piled up.
BN_PRAISE = ["অপরূপ", "মনোমুগ্ধকর", "মনোরম", "নয়নাভিরাম", "নান্দনিক", "অনবদ্য", "অনন্য", "অসামান্য", "অভূতপূর্ব",
             "অবিস্মরণীয়", "অপার", "অফুরন্ত", "অবারিত", "অনাবিল", "স্নিগ্ধ", "মাধুর্য", "মুগ্ধতা", "শিহরণ", "চিরন্তন",
             "কালজয়ী", "আভিজাত্য", "রাজকীয়", "স্বর্গীয়", "জাদুকরী", "মোহনীয়", "মায়াবী", "প্রশান্তি", "মেলবন্ধন"]
BN_SLANG = ["জোস", "প্যারা", "চিল", "অস্থির", "জটিল", "সেই লেভেলের", "মাথা নষ্ট", "পুরাই", "কড়া", "ফাটাফাটি",
            "ঝাক্কাস", "ব্রো", "মামা", "ক্রাশ", "আগুন", "হুদাই", "সেইরকম", "সেইরাম", "ঝাকানাকা", "খাইছে রে"]
BN_REACTIONS = ["উফ", "উফফ", "আহা", "ইশ", "ইশশ", "ওহো", "আরে", "বাহ", "ওয়াও", "হায় হায়"]
BN_PARTICLES = re.compile(NOT_BN_BEFORE + "(?:তো|কিন্তু|একটু|নাকি|ব্যস|তাই না|আর কী)" + NOT_BN_AFTER +
                          "|" + NOT_BN_BEFORE + "না\\?")
ROMAN_BN_STRONG = {"korun", "koren", "korte", "korben", "korbo", "kinun", "kinte", "hobe", "hoyeche", "hoise", "hoiche",
                   "ache", "achhe", "ekhon", "ekhoni", "ajke", "aajke", "valo", "bhalo", "onek", "kichu", "kisu", "keno",
                   "kemon", "koto", "apnar", "tomar", "amader", "jonno", "theke", "sathe", "shathe", "lagbe", "paben",
                   "pacchen", "pachen", "thakbe", "shudhu", "sudhu", "matro", "sesh", "shesh", "hobar", "pochonder",
                   "pochondo", "dekhun", "dekhen", "janun", "janaben", "bolun", "vaiya", "bhaiya", "apu", "dam", "taka",
                   "vlo", "kicu", "chilo", "cilo", "hoice", "dise", "paisi", "paici", "pelam", "onk", "kmn"}
ROMAN_BN_WEAK = {"ami", "apni", "tumi", "vai", "bhai", "ki", "na", "nai", "nei", "ar", "e", "te", "ta", "ti", "din",
                 "nin", "age", "pore", "kal", "aj", "ebar", "diye", "niye", "kore", "dite", "nite"}


def _bn_count(words: list, text: str) -> list:
    """The distinct words of the list present in the text as whole words, case endings allowed."""
    return [w for w in words if re.search(NOT_BN_BEFORE + re.escape(w) + "(?:তা)?" + BN_SUFFIX_PLAIN + NOT_BN_AFTER,
                                          text)]


def roman_bangla(text: str) -> bool:
    """Bangla written in Latin letters (Banglish)."""
    toks = {t.lower() for t in re.findall(r"[A-Za-z]+", text)}
    strong = toks & ROMAN_BN_STRONG
    return len(strong) >= 2 or (len(strong) == 1 and len(toks & ROMAN_BN_WEAK) >= 2)


EN_CTA_VERBS = {"book", "buy", "get", "shop", "order", "register", "join", "save", "share", "watch", "read", "try",
                "start", "see", "visit", "download", "sign", "call", "message", "reserve", "claim", "apply", "learn",
                "come", "taste", "listen", "follow", "comment", "tell", "grab", "pick", "subscribe", "rsvp", "text",
                "email", "send", "find", "compare", "check", "ask", "vote", "enter", "donate", "meet", "plan", "stop",
                "drop", "pop", "swing", "bring", "make", "switch", "choose", "upgrade", "cook", "build", "shop",
                "scan"}

BAIT_RX = re.compile(r"\b(?:like and share|like,? comment,? (?:and )?share|share (?:this|it) with everyone|tag (?:your|a) "
                     r"friends?|smash (?:that|the) like)\b|লাইক(?:,)? (?:দিন|কমেন্ট)|শেয়ার করুন সবাইকে|সবাইকে শেয়ার|"
                     r"ট্যাগ করুন|লাইক ও শেয়ার|লাইক দিয়ে", re.I)
GREETING_OPEN_RX = re.compile(r"^\s*(?:hi|hello|hey)(?: everyone| guys| all)?\b|^\s*(?:dear (?:customers?|valued)|"
                              r"প্রিয় গ্রাহক|সম্মানিত গ্রাহক|প্রিয় ক্রেতা|আসসালামু আলাইকুম|নমস্কার সবাইকে)", re.I)
HEAD_ROLES = re.compile(r"head|title|hook|big|num|kicker", re.I)
CTA_ROLES = re.compile(r"cta|button|action", re.I)
CAPTION_ROLES = re.compile(r"caption|post_text|body_long", re.I)
ALT_ROLES = re.compile(r"\balt\b|alt[_-]?text|image[_-]?caption|figcaption", re.I)
REPLY_ROLES = re.compile(r"reply|comment|\bdm\b|message", re.I)
CASUAL_ROLES = re.compile(r"caption|post|body|reply|comment|\bdm\b|message|chat", re.I)
FORMAL_ROLES = re.compile(r"terms|legal|safety|notice|disclaimer|instruction", re.I)
# Songs and poems: an even meter, a refrain, repeated openings, literary words and "আহা" are the craft there, not tells.
LYRIC_ROLES = re.compile(r"(?<![a-z])(?:lyrics?|songs?|verses?|chorus|refrain|mukhra|antara|sanchari|abhog|bridge|poem|"
                         r"poetry|jingle|ghazal|rap)(?![a-z])", re.I)
# Checks written for posts and ads that are wrong for lyrics, and checks that become advice only (a note).
LYRIC_SKIP = {"flat-rhythm", "staccato", "same-openers", "long-sentence", "bn-poetic", "bn-reactions", "quote",
              "all-positive", "no-speaker", "triads", "emoji-on-image", "exclamation", "question-headline",
              "long-headline", "long-cta", "cta-verb", "generic-cta", "colon-reveal", "colon-reveals", "bn-essay",
              "engagement-bait", "all-caps"}
LYRIC_SOFT = {"bn-formal", "bn-formal-soft", "bn-pattern", "ai-word", "ai-cluster", "bn-latin", "banglish",
              "bn-slang-pile", "not-tails", "bn-particles", "bn-ebong", "bn-eti"}


def is_lyric(role: str) -> bool:
    return bool(LYRIC_ROLES.search(role or ""))


def script_of(text: str) -> str:
    """The script a line is written in. A brand name in Latin letters does not change it: a Chinese, Japanese,
    Korean, Thai or Tamil line with one Latin word is still that script."""
    bn = len(re.findall(f"[{BN}]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    if bn and bn >= latin:
        return "bengali"
    for script, rx in (("devanagari", "[ऀ-ॿ]"), ("arabic", "[؀-ۿݐ-ݿﭐ-﷿ﹰ-﻿]"), ("kana", "[぀-ヿ]"),
                       ("han", "[一-鿿㐀-䶿]"), ("hangul", "[가-힯ᄀ-ᇿ㄰-㆏]"), ("thai", "[฀-๿]"),
                       ("tamil", "[஀-௿]")):
        if re.search(rx, text):
            return script
    # Cyrillic and Hebrew by majority: one look-alike Cyrillic letter in an English word keeps the line Latin
    for script, rx in (("cyrillic", "[Ѐ-ӿ]"), ("hebrew", "[֐-׿]")):
        n = len(re.findall(rx, text))
        if n and n >= latin:
            return script
    return "latin" if latin else "other"


# ------------------------------------------------------------------------------------------------ other languages
# The research rules for 18 languages (and the newer English and Bengali ones) live in voice_rules.json: each is a
# regex, or a word or phrase matched with the boundary its script needs. A line is checked against its language's
# rules: the copy.json "lang" tag first, then the script (a Latin line with Roman Hindi in it is Hinglish).
SCRIPT_LANG = {"bengali": "bn", "devanagari": "hi", "arabic": "ar", "kana": "ja", "han": "zh", "hangul": "ko",
               "thai": "th", "tamil": "ta", "cyrillic": "ru", "hebrew": "he"}
ROMAN_HI = re.compile(r"\b(?:karo|karein|kijiye|mein|aur|toh|bhi|nahi|nahin|kya|aap|hain|abhi)\b", re.I)
# Latin-script languages told apart by their commonest small words, so an untagged Spanish or Taglish line does not
# get the English lists. Words two languages share count for both; a tie is left undecided.
LATIN_STOP = {
    "en": "the and to of for on with is are you your we our it this that at by from not no now just get new all can",
    "es": "el los las del y en una por para con es tu te su al lo como más pero ya este esta hoy aquí que de no un",
    "pt": "o os as do da dos das e em uma para com não é você seu sua no na mais mas já hoje aqui pra que de um",
    "fr": "le les des du et est une pour avec pas vous votre nous sur au aux ce cette plus mais en de que un la",
    "de": "der die das und ist nicht mit für auf ein eine den dem sie du ich wir zu von im bei auch noch jetzt",
    "it": "il gli di del e un una per con non è sono ti tuo tua ci più ma oggi qui che la lo",
    "id": "yang dan di ke dari ini itu untuk dengan tidak ada kamu kami nggak gak aja banget udah sudah juga nih dong",
    "ms": "yang dan di ke dari ini itu untuk dengan tidak ada anda kami tak nak je dah lah korang jom kat",
    "tl": "ang ng mga sa na at ay ka mo ko po lang naman pa kasi talaga din rin",
    "tr": "ve bir bu için ile çok daha mı mi ne var yok gibi sen siz da de",
    "fi": "ja on ei se että oli ovat mutta kun jos tai myös nyt sinun meidän",
}
LATIN_STOP = {k: set(v.split()) for k, v in LATIN_STOP.items()}
# matched on the lowercased text, without IGNORECASE: Python folds ı and i together under it
VI_MARKS = re.compile("[ơưđạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]")
NON_EN_LATIN = re.compile("[ñ¿¡áéíóúãõçàèìòùâêîôûäöüßışğåøæœ]")


def latin_lang(text: str) -> str:
    """The language of an untagged Latin-script line: vi by its tone marks, else the language whose small words it
    uses most (two or more, and more than English), else "und" when it has non-English letters and no English words,
    else English."""
    low = text.lower()
    if len(VI_MARKS.findall(low)) >= 2:
        return "vi"
    toks = {t.lower() for t in re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", text)}  # distinct: "no X, no Y" is one
    score = {k: len(toks & v) for k, v in LATIN_STOP.items()}
    en = score.pop("en")
    best = max(score.values())
    top = [k for k, v in score.items() if v == best]
    if best >= 2 and best > en:
        return top[0] if len(top) == 1 else "und"
    if not en and NON_EN_LATIN.search(low):
        return "und"
    return "en"
_BLOCKS = {"deva": "ऀ-ॣॱ-ॿ꣠-ꣿ", "arab": "ؐ-ؚؠ-ٟٮ-ۓە-ۜ۟-۪ۨ-ۯۺ-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿",
           "taml": "஀-௥", "beng": "ঀ-৿"}
_VOICE: dict | None = None


def lang_of(text: str, lang: str = "", script: str = "") -> str:
    """A two-letter language code for the rules: the tag if given, else the script's usual language; for Latin text,
    Hinglish when two Roman Hindi words appear, Bangla for Banglish, else the language its small words show
    (latin_lang), English by default."""
    code = (lang or "").lower().replace("_", "-").split("-")[0]
    if code:
        return code
    script = script or script_of(text)
    if script in SCRIPT_LANG:
        return SCRIPT_LANG[script]
    if script == "latin":
        if len(set(w.lower() for w in ROMAN_HI.findall(text))) >= 2:
            return "hi"
        return "bn" if roman_bangla(text) else latin_lang(text)
    return ""


def _rule_regex(r: dict):
    """Compile one voice rule. regex and structure: a Python pattern with the rule's flags (case-insensitive by
    default). word and phrase: the literal,
    with a boundary that depends on its script (Hangul stays open on the right, where particles attach; Thai and
    CJK have no word boundary at all)."""
    m = unicodedata.normalize("NFC", r.get("match", ""))
    fl = 0
    for ch in r.get("flags", "i"):  # "i" by default; the humanizer rules were tested with "m" ("im" in English)
        fl |= {"i": re.I, "m": re.M}.get(ch, 0)
    if r.get("kind") in ("regex", "structure"):
        return re.compile(m, fl)
    lit, sc = re.escape(m), script_of(m)
    if sc in ("thai", "han", "kana"):
        return re.compile(lit, fl)
    if sc == "hangul":
        return re.compile("(?<![가-힯])" + lit, fl)
    block = {"devanagari": "deva", "arabic": "arab", "tamil": "taml", "bengali": "beng"}.get(sc)
    if block:
        rng = _BLOCKS[block]
        ending = BN_SUFFIX if block == "beng" else ""  # গৃহে, পরিলক্ষিত হয়: Bengali words take case endings
        return re.compile(f"(?<![{rng}]){lit}{ending}(?![{rng}])", fl)
    return re.compile(r"(?<![\w\u0300-\u036f])" + lit + r"(?![\w\u0300-\u036f])", fl)


def _voice_data() -> dict:
    """{lang: [rule]} as voice_rules.json lists them, loaded once."""
    global _VOICE
    if _VOICE is None:
        data = {}
        path = Path(__file__).with_name("voice_rules.json")
        if path.exists():
            for r in json.loads(path.read_text(encoding="utf-8")).get("rules", []):
                data.setdefault(r["lang"], []).append(r)
        _VOICE = data
    return _VOICE


_VOICE_RX: dict = {}


def voice_of(code: str) -> list:
    """[(compiled, rule)] of one language code, compiled the first time that language is linted: a deck in one or
    two languages does not wait for the patterns of the other 20-odd (0.17 s for all of them)."""
    if code not in _VOICE_RX:
        _VOICE_RX[code] = [(_rule_regex(r), r) for r in _voice_data().get(code, [])]
    return _VOICE_RX[code]


def voice_rules() -> dict:
    """{lang: [(compiled, rule)]} from voice_rules.json, every language compiled."""
    return {code: voice_of(code) for code in _voice_data()}


def _variants(code: str, text: str) -> tuple:
    """The text as the rules should see it: Turkish lowercasing (İ to i, I to ı, which Python does not fold) and
    Arabic-script text without tatweel and short vowels, alongside the text itself."""
    t = unicodedata.normalize("NFC", text)
    if code == "tr":
        return t, t.replace("İ", "i").replace("I", "ı").lower()
    if code in ("ar", "ur"):
        return t, re.sub("[\u064B-\u065F\u0670\u0640]", "", t)
    return (t,)


def regions(locale: str = "", lang: str = "") -> set:
    """The markets a piece is for, from --locale (BD, pt-BR, es-419) and the region part of the lang tag (zh-TW)."""
    out = set()
    loc = (locale or "").strip().replace("_", "-")
    if re.fullmatch(r"[A-Za-z]{2}|\d{3}", loc):
        out.add(loc.upper())
    for tag in (loc, (lang or "").strip().replace("_", "-")):
        out |= {p.upper() for p in tag.split("-")[1:] if re.fullmatch(r"[A-Za-z]{2}|\d{3}", p)}
    return out


def _in_scope(rule_scope: str, scope: str, role: str) -> bool:
    """spoken rules run only for copy that is heard; headline, alt and casual rules only for those roles."""
    if scope == "spoken" or rule_scope == "spoken":
        return rule_scope == scope
    return {"": True, "headline": bool(HEAD_ROLES.search(role or "")), "alt": bool(ALT_ROLES.search(role or "")),
            "casual": bool(CASUAL_ROLES.search(role or "")) and not FORMAL_ROLES.search(role or "")
            }.get(rule_scope, False)


def lint_voice(text: str, codes, scope: str = "", role: str = "", locale: str = "", lang: str = "") -> list:
    """The research rules of each language code that match the text, plus the "mul" rules every language shares.
    scope "spoken" runs the rules for copy that is heard (currency signs, ordinals, homographs a voice misreads)
    instead of the general ones. A rule with a region runs only for those markets (pt-PT words in a Portugal post);
    a rule with a min needs that many matches (a Xiaohongshu buzzword is fine once, a tell at two)."""
    out, seen, spans = [], set(), []
    markets = regions(locale, lang)
    for code in list(codes) + (["mul"] if "mul" not in codes and scope != "spoken" else []):
        variants = _variants(code, text)
        for rx, r in voice_of(code):
            if r.get("id") in seen or not _in_scope(r.get("scope", ""), scope, role):
                continue
            if r.get("region") and not markets & set(r["region"]):
                continue
            if r.get("min"):
                if max(len(rx.findall(v)) for v in variants) < r["min"]:
                    continue
            else:
                hit = next(((i, m) for i, v in enumerate(variants) for m in [rx.search(v)] if m), None)
                if not hit:
                    continue
                i, m = hit
                a, b = m.span()
                # two research sources often name the same tell ("No es solo X, es Y"): one finding per span
                if b > a and any(j == i and min(b, y) - max(a, x) >= 0.5 * min(b - a, y - x) for j, x, y in spans):
                    continue
                spans.append((i, a, b))
            seen.add(r.get("id"))
            out.append(_f(r["level"], f"{code}-voice", r.get("what") or r["why"].split(". ")[0][:120],
                          r.get("replacement", "")))
    return out


def has_bengali(text: str) -> bool:
    """Bengali checks run on any string with Bengali in it, mixed lines included."""
    return len(re.findall(f"[{BN}]", text)) >= 2


BN_SUFFIX = "(?:র|এর|ের|কে|দের|রা|ও|ই|ে|য়|েই)?"
BN_SUFFIX_PLAIN = BN_SUFFIX


def _f(sev, code, message, suggest=""):
    return {"severity": sev, "code": code, "message": message, "suggest": suggest}


# Scarcity claimed without the fact behind it ("it may sell out on day one"): a model's favourite closer in Bengali.
BN_URGENCY = re.compile(unicodedata.normalize("NFC", r"(?:শেষ হয়ে|ফুরিয়ে) (?:যেতে পারে|যাবে|যাচ্ছে)|স্টক সীমিত|"
                                                     r"সীমিত স্টক|সীমিত সময়ের (?:জন্য|অফার)"))
BN_HAS_FACT = re.compile(unicodedata.normalize("NFC", r"পর্যন্ত|শেষ দিন|[০-৯0-9]+\s*(?:টি|টা|পিস|জন|সেট|কেজি)?\s*"
                                                      r"(?:বাকি|আছে)"))
HAS_FACT = re.compile(r"\b(?:until|till|ends?|by|before)\b[^.!?]{0,25}\b(?:mon|tue|wed|thu|fri|sat|sun|today|tonight|"
                      r"midnight|noon|\d)|\b\d+\s+(?:left|seats|spots|places|units|bags|tickets)\b", re.I)
VIRAMA = "\u09CD\u094D"


def visible_len(text: str) -> int:
    """Characters as a reader counts them: a Bengali or Devanagari letter with its vowel signs and conjuncts (ক্ষে) is
    one, not four code points. Platforms cut captions by what they show."""
    n, after_virama = 0, False
    for ch in unicodedata.normalize("NFC", text):
        cat = unicodedata.category(ch)
        if ch in VIRAMA:
            after_virama = True
            continue
        if cat in ("Mn", "Mc", "Me", "Cf") or after_virama:
            after_virama = False
            continue
        n += 1
    return n


def dashes(text: str, script: str) -> list:
    """Dashes readers take as the mark of AI-written copy; the one rule for copy and for rendered text (design.py
    calls it). Every en dash is classified, and each kind of finding is reported once."""
    out, seen = [], set()

    def add(f):
        if f["code"] not in seen:
            seen.add(f["code"])
            out.append(f)
    if re.search("[\u2014\u2015\u2E3A\u2E3B]|(?<!-)--(?!-)", text):
        add(_f("error", "em-dash", "an em dash (— or --): readers take it as the mark of AI-written copy",
               "rewrite with a comma, a colon, a full stop or brackets"))
    for m in re.finditer("\u2013", text):
        left, right = text[:m.start()], text[m.end():]
        a, b = left.rstrip()[-1:], right.lstrip()[:1]
        spaced = left[-1:].isspace() or right[:1].isspace()
        if a.isdigit() and b.isdigit():
            if script in ("bengali", "devanagari", "arabic"):
                add(_f("warning", "range-dash", "an en dash in a range",
                       "write it as local readers do: ১০-১২ or ১০ থেকে ১২"))
            elif spaced:
                add(_f("warning", "range-dash", "a spaced en dash in a range", "close it up (10–12) or write 'to'"))
        elif spaced:
            add(_f("error", "pause-dash", "a spaced en dash ( – ): as a pause, or between words and times, readers "
                                          "take it as the AI dash",
                   "লিখুন: সকাল ১১টা থেকে রাত ৮টা; বাক্য ভাঙতে কমা বা দাঁড়ি" if script == "bengali"
                   else "rewrite with a comma, a colon or a full stop ('to' for a range)"))
        else:
            add(_f("warning", "word-dash", "an en dash between words", "write 'to' or the local word"))
    if re.search(r"\S - \S", text):
        add(_f("warning", "spaced-hyphen", "a spaced hyphen reads as a dash",
               "rewrite with a comma, a colon or a full stop, or write 'to' for a range"))
    return out


WORD_MARKS = "\u0900-\u0DFF\u0E00-\u0E7F\u064B-\u065F\u0670\u0591-\u05C7\u0300-\u036F"  # Indic, Thai, Arabic, Hebrew


def _words(text: str) -> list:
    return re.findall(rf"[\w{BN}{WORD_MARKS}'’-]+", text)


ABBR_END = re.compile(r"(?:\b[A-Za-z]|\b(?:etc|vs|approx|incl|min|max|Dr|Mr|Mrs|Ms|Sr|Sra|Jr|St|Nr|Tel|e\.g|i\.e))\.$",
                      re.I)  # initials and a. m. (one letter), and the usual abbreviations; "it." ends a sentence


def _sentences(text: str) -> list:
    """Sentences, without breaking at abbreviations (a. m., p.m., Dr., etc.)."""
    out = []
    for part in re.split(r"(?<=[.!?।])\s+", text.strip()):
        if out and ABBR_END.search(out[-1]):
            out[-1] += " " + part
        elif part:
            out.append(part)
    return out


# A colon reveal: a short set-up, then the payoff ("The secret: love.", "Here's the thing: it works."). A label with
# a figure after it ("Our hours: 9 to 5") is not one.
COLON_REVEAL_EN = re.compile(r"(?:^|(?<=[.!?])\s+)((?:the|our|my|your|here['’]s|one|this|that|what)\b[^:\n.!?]{0,40}):"
                             r"[ \t]+(?![\d৳$€£₹])[^\n:]{1,80}?[.!?](?=\s|$)", re.I | re.M)
LABEL_EN = re.compile(r"\b(?:hours|address|location|venue|date|dates|time|times|price|prices|menu|sizes?|colou?rs|offer|"
                      r"deadline|contact|phone|email|website|link|code|ingredients|details|terms|schedule|line-?up|"
                      r"speakers|tickets|dress code|rules|prize|prizes|order|delivery)\b", re.I)
NOT_TAIL_EN = re.compile(r",\s+not\s+(?!only\b|just\b|to\b|that\b|because\b|even\b)[\w'’-]+", re.I)


def keep_masked(text: str, voice: dict | None) -> str:
    """brand.json voice.keep: the brand's signature lines (a tagline, a catchphrase) that the lint must not flag.
    Each is replaced by as many placeholder words, so lengths and rhythm stay as written."""
    for k in (voice or {}).get("keep", []) or []:
        k = (k or "").strip()
        if k:
            text = re.sub(re.escape(k), lambda m: " ".join("0" for _ in m.group(0).split()), text, flags=re.I)
    return text


MONTHS_EN = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov",
                                          "dec"), 1)}
WEEKDAY_DATE = re.compile(r"\b(mon|tue|wed|thu|fri|sat|sun)[a-z]*\.?,?\s+(\d{1,2})(?:st|nd|rd|th)?\s+"
                          r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?(?:,?\s+(\d{4}))?", re.I)


def weekday_slips(text: str, today=None) -> list:
    """'Sat 11 Oct' where 11 October is not a Saturday: in the year given, or, with no year, in this year and the next
    (a date people will read soon). A wrong weekday sends people on the wrong day."""
    import datetime
    today = today or datetime.date.today()
    names = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    out = []
    for m in WEEKDAY_DATE.finditer(text):
        wd = ("mon", "tue", "wed", "thu", "fri", "sat", "sun").index(m.group(1).lower())
        day, month = int(m.group(2)), MONTHS_EN[m.group(3).lower()[:3]]
        years = [int(m.group(4))] if m.group(4) else [today.year, today.year + 1]
        real = []
        for y in years:
            try:
                real.append((y, datetime.date(y, month, day).weekday()))
            except ValueError:
                real.append((y, None))
        if all(w != wd for _, w in real):
            said = "; ".join(f"{day} {m.group(3)[:3].title()} {y} is " + (f"a {names[w]}" if w is not None else "no date")
                             for y, w in real)
            out.append(_f("warning", "weekday-date", f"'{m.group(0)}': {said}", "check the date and the weekday together"))
    return out


def lint_string(text: str, role: str = "", locale: str = "", platform: str = "", lang: str = "",
                voice: dict | None = None) -> list:
    """Findings for one piece of copy. role: the copy.json role (headline, cta, caption, body, reply, alt …); lang: a
    BCP 47 tag for the language's punctuation and voice rules (its region part, like --locale, switches on a market's
    rules); voice: brand.json 'voice' (its avoid list, preferred words and keep lines)."""
    text = unicodedata.normalize("NFC", text)
    lex = lexicon(text, voice)
    text = keep_masked(text, voice)  # the brand's own signature lines are not flagged
    script = script_of(text)
    code = lang_of(text, lang, script)
    english = script == "latin" and code == "en"   # the English lists are for English, not Taglish or Spanish
    out = dashes(text, script) + punctuation(text, lang) + lex + weekday_slips(text)
    low = text.lower()
    if english:
        spans = set()
        for w, rep in AI_WORDS_EN.items():
            m = re.search(rf"(?<![\w-]){_inflected(w)}(?![\w-])", low)
            if m and m.span() not in spans:  # delve and delves both see "delved": report it once
                spans.add(m.span())
                out.append(_f("warning", "ai-word", f"'{w}' is a well-known AI or template word", rep))
        soft = [w for w in AI_WORDS_EN_SOFT if re.search(rf"(?<![\w-]){re.escape(w)}(?![\w-])", low)]
        if len(soft) >= 2:
            out.append(_f("warning", "ai-cluster", "a cluster of common AI words: " + ", ".join(soft),
                          "; ".join(f"{w} → {AI_WORDS_EN_SOFT[w]}" for w in soft)))
        for rx, what, rep, sev in AI_PATTERNS_EN:
            if rx.search(text):
                if what == "urgency without a fact" and HAS_FACT.search(text):
                    continue  # "30% off ends Sunday at midnight" states its fact
                out.append(_f(sev, "chatbot-leftover" if sev == "error" else "ai-pattern", what, rep))
        if CTA_ROLES.search(role or "") and GENERIC_CTA_EN.search(text):
            out.append(_f("warning", "generic-cta", f"'{text.strip()}' does not say what happens",
                          "name the action and the thing: Book a tasting, Get the menu"))
        if HEAD_ROLES.search(role or "") and re.match(r"^[A-Z][^:]{2,40}:\s+\S", text):
            out.append(_f("note", "colon-reveal", "a colon reveal in a headline ('The best part: …')",
                          "write the payoff as the headline"))
        elif sum(not LABEL_EN.search(m.group(1)) for m in COLON_REVEAL_EN.finditer(text)) >= 2:
            # the em dash ban moves the same punchy aside into colons (displacement)
            out.append(_f("note", "colon-reveals", "two or more colon reveals ('The fix is simple: stop.')",
                          "say it straight: keep one at most"))
        if len(NOT_TAIL_EN.findall(text)) >= 2:
            out.append(_f("note", "not-tails", "two or more ', not X' tails ('Real butter, not margarine.')",
                          "say what it is; drop the contrast nobody asked for"))
    if has_bengali(text):
        rest = text.replace("শীঘ্রই আসছে", " ")  # longest phrase first; a matched span is not matched again
        for w in sorted(BN_FORMAL, key=len, reverse=True):
            rx = re.compile(NOT_BN_BEFORE + re.escape(w) + BN_SUFFIX + NOT_BN_AFTER)
            if rx.search(rest):
                if w in BN_FORMAL_SOFT:
                    out.append(_f("note", "bn-formal-soft", f"'{w}' is standard but stiffer than everyday speech",
                                  BN_FORMAL[w]))
                else:
                    out.append(_f("warning", "bn-formal", f"'{w}' sounds bookish or translated", BN_FORMAL[w]))
                rest = rx.sub(" ", rest)
        for rx, what, rep in BN_PATTERNS:
            target = SADHU_EXCEPT.sub(" ", text) if what.startswith("sadhu") else \
                VISARGA_ABBR.sub(" ", text) if what.startswith("a visarga") else text
            if rx.search(target):
                out.append(_f("warning", "bn-pattern", what, rep))
        if BN_URGENCY.search(text) and not BN_HAS_FACT.search(text):
            out.append(_f("warning", "bn-urgency", "scarcity or a deadline claimed without the fact (a closing date, a "
                                                   "count)", "give the real date or quantity (শুক্রবার পর্যন্ত, আর ৪০টা "
                                                             "বাকি), or leave it out"))
        if VISARGA_ABBR.search(text):
            out.append(_f("note", "bn-abbr", "an abbreviation with a visarga (মোঃ, ডাঃ)",
                          "common, and fine; Bangla Academy style is মো., ডা."))
        for rx, what in BN_CALQUES:
            if rx.search(text):
                out.append(_f("warning", "bn-calque", what, "say the concrete thing the way a Dhaka page would"))
        if locale.upper() == "BD":
            for w, rep in BN_WB_FOR_BD.items():
                if re.search(NOT_BN_BEFORE + re.escape(w) + BN_SUFFIX + NOT_BN_AFTER, text):
                    out.append(_f("warning", "bn-locale", f"'{w}': most Bangladeshi readers say '{rep}' (keep it for "
                                                          f"a West Bengal or Hindu-household context)", rep))
            for w, rep in BN_KIN_NOTE.items():
                if re.search(NOT_BN_BEFORE + re.escape(w) + BN_SUFFIX + NOT_BN_AFTER, text):
                    out.append(_f("note", "bn-kin", f"'{w}': many Bangladeshi readers say '{rep}'; choose for the "
                                                    f"audience", rep))
            if re.search(f"[{BN}]গুলি(?:র|কে|তে)?{NOT_BN_AFTER}", text):
                out.append(_f("note", "bn-locale", "-গুলি: Bangladeshi copy writes -গুলো", "-গুলো"))
        for sentence in re.split(r"(?<=[।!?])\s+", text):
            if len(BN_APNI.findall(sentence)) >= 3:
                out.append(_f("warning", "bn-pronouns", "আপনি / আপনার three times in one sentence (a translation habit)",
                              "drop the pronouns the verb already carries: ফোন থেকে অ্যাকাউন্টে লগ ইন করুন"))
                break
        praise = _bn_count(BN_PRAISE, text)
        if len(praise) >= (3 if CAPTION_ROLES.search(role or "") else 2):
            out.append(_f("warning", "bn-poetic", "stacked literary praise: " + ", ".join(praise),
                          "keep the one word that is literally true; say the concrete thing (the fabric, the view, "
                          "the price, the time)"))
        slang = _bn_count(BN_SLANG, text)
        if len(slang) >= 3:
            out.append(_f("warning", "bn-slang-pile", "a pile of slang: " + ", ".join(slang),
                          "one slang word at most; brands that sound young still use one"))
        if len(_bn_count(BN_REACTIONS, text)) >= 2:
            out.append(_f("note", "bn-reactions", "stacked reaction words (উফ, আহা, ইশ …)",
                          "one reaction at the start, from someone speaking or thinking"))
        toks = re.findall(rf"[\w{BN}?]+", text)
        for i in range(max(1, len(toks) - 29)):
            if len(BN_PARTICLES.findall(" ".join(toks[i:i + 30]))) >= 3:
                out.append(_f("note", "bn-particles", "three or more particles close together (তো, কিন্তু, একটু …)",
                              "one particle per line sounds spoken; a stack sounds like an imitation of speech"))
                break
        if re.search(r"(?i)\b(?:rizz|skibidi|bruh|pookie|delulu)\b", text):
            out.append(_f("note", "bn-genz", "English Gen Z slang inside Bengali copy",
                          "say it in plain Bangla, or leave it out"))
        n_ebong = len(re.findall(NOT_BN_BEFORE + "এবং" + NOT_BN_AFTER, text))
        if n_ebong >= 3 and not re.search(NOT_BN_BEFORE + "(?:ও|আর)" + NOT_BN_AFTER, text):
            out.append(_f("note", "bn-ebong", f"এবং {n_ebong} times and never ও or আর (a translated rhythm)",
                          "join with আর or ও, or a comma"))
        if len(re.findall(NOT_BN_BEFORE + "এটি" + BN_SUFFIX + NOT_BN_AFTER, text)) >= 2:
            out.append(_f("note", "bn-eti", "এটি again and again (a translation habit)",
                          "এটা, or name the thing again, or drop the pronoun"))
        if re.search("প্রথমত", text) and re.search("দ্বিতীয়ত", text):
            out.append(_f("note", "bn-essay", "প্রথমত … দ্বিতীয়ত: essay scaffolding in a post", "one point per line"))
        if CTA_ROLES.search(role or "") and re.search("উপভোগ করুন", text):
            out.append(_f("warning", "bn-enjoy-cta", "উপভোগ করুন as the call to action (the translated 'enjoy')",
                          "the real action: অর্ডার করুন, চেখে দেখুন, দেখে নিন"))
        latin = [w for w in re.findall(r"(?<![\w.@/#])[A-Za-z][a-z]+(?![\w.@/])", text)]
        if len(latin) >= 2 and HEAD_ROLES.search(role or "") or len(latin) >= 3:
            out.append(_f("note", "bn-latin", f"English words in Latin script inside Bengali: {', '.join(latin[:4])}",
                          "write loanwords in Bengali script (অফার, ডেলিভারি); keep brand names, URLs and codes "
                          "in Latin; at most one punchy Latin word on a consumer graphic"))
    if script == "latin" and roman_bangla(text):
        firm = HEAD_ROLES.search(role or "") or CTA_ROLES.search(role or "") or re.search(r"price|terms|legal", role or "",
                                                                                        re.I)
        out.append(_f("warning" if firm else "note", "banglish", "Bangla in Latin letters (Banglish)",
                      "write it in Bengali script; keep Banglish for replies, comments and the captions of youth "
                      "brands that talk that way, never for headlines, prices or terms"))
    n_excl = text.count("!") + text.count("！")
    if n_excl > 1 or (n_excl and HEAD_ROLES.search(role or "") and english):
        # a hook in most markets may end in one "!" (ঈদের কেনাকাটা এবার ঘরে বসেই!, Jom tapau!, 신메뉴 출시!); English
        # headlines take none
        out.append(_f("warning", "exclamation", "exclamation marks read as shouting or ad-speak",
                      "let the words carry it; one at most" + (", never in an English headline" if english else "")))
    if not CAPTION_ROLES.search(role or "") and len(EMOJI_RX.findall(text)) > 1:
        out.append(_f("warning", "emoji-on-image", f"{len(EMOJI_RX.findall(text))} emoji in one string on the design",
                      "one at most on the image; captions carry the rest"))
    caps = [w for w in re.findall(r"\b[A-Z]{4,}\b", text) if w not in ("RSVP", "FAQ", "HTML")]
    if len(caps) >= 2:
        out.append(_f("note", "all-caps", "several words in capitals", "set caps with CSS, not in the copy"))
    if BAIT_RX.search(text):
        out.append(_f("warning", "engagement-bait", "asking for likes, shares or tags (platforms demote it, and "
                                                    "asking for likes lowered likes in a 2025 study)",
                      "ask a real question, or for a save or a send with a reason"))
    words = _words(text)
    # Bengali drops the pronoun ("ফুচকা হবে?" speaks to the reader) and Bangladeshi brands open with questions, so the
    # note is for Latin headlines only
    if english and HEAD_ROLES.search(role or "") and text.strip().endswith("?") and \
            not re.search(r"\byou", text, re.I):
        out.append(_f("note", "question-headline", "a headline as a general question", "statements usually pull "
                      "more; keep a question only if it is specific and speaks to the reader"))
    if HEAD_ROLES.search(role or "") and script in ("han", "kana"):
        # no spaces between words: count characters (about two per English word)
        n = visible_len(re.sub(r"[\s、。！？，：「」『』・]", "", text))
        limit = 8 if re.search("thumb", platform or "", re.I) else 12 if re.search("carousel|cover", platform or "",
                                                                                      re.I) else 16
        if n > limit:
            out.append(_f("note", "long-headline", f"{n} characters in a headline (about {limit} read at a glance)",
                          "cut to the one idea"))
    elif HEAD_ROLES.search(role or ""):
        limit = 4 if re.search("thumb", platform or "", re.I) else 6 if re.search("carousel|cover", platform or "",
                                                                                     re.I) else 8
        if len(words) > limit:
            out.append(_f("warning", "long-headline", f"{len(words)} words in a headline (≤ {limit} reads at a "
                                                         f"glance)", "cut to the one idea"))
    if CTA_ROLES.search(role or "") and script in ("han", "kana"):
        n = visible_len(re.sub(r"[\s、。！？，]", "", text))
        if n > 8:
            out.append(_f("note", "long-cta", f"a {n}-character call to action", "about 4 to 8 characters: 立即预订, "
                                                                                "今すぐ予約"))
    elif CTA_ROLES.search(role or ""):
        cap = 6 if script == "bengali" else 4  # অর্ডার করুন is two words where English has one
        if len(words) > cap:
            out.append(_f("warning", "long-cta", f"a {len(words)}-word call to action", f"≤ {cap} words, the action "
                                                                                       f"first" if script != "bengali"
                          else f"≤ {cap} words, ending in the action (অর্ডার করুন)"))
        first = words[0].lower() if words else ""
        if english and first and first not in EN_CTA_VERBS:
            out.append(_f("note", "cta-verb", f"the call to action starts with '{words[0]}'",
                          "start with the action (Book, Order, Save, Watch)"))
        if script == "bengali" and not BN_CTA_END.search(text.strip()):
            out.append(_f("note", "cta-verb", "the call to action does not end in an action verb",
                          "শেষে ক্রিয়া: করুন, দেখুন, নিন, আসুন"))
    sentences = _sentences(text)
    lens = [len(_words(x)) for x in sentences]
    run = 0
    for n in lens:
        run = run + 1 if n <= 3 else 0
        if run >= 3:
            out.append(_f("note", "staccato", "three or more very short sentences in a row ('Real dough. Real fire. "
                                              "Real fast.')", "one fragment can land; a run of them reads as a formula"))
            break
    if len(lens) >= 6:
        mean = sum(lens) / len(lens)
        cv = (sum((n - mean) ** 2 for n in lens) / len(lens)) ** 0.5 / mean if mean else 0
        # an even rhythm is normal in short X posts and threads (it scored above the median there)
        if cv < 0.45 and (platform or "").split("-")[0].lower() not in ("x", "threads"):
            out.append(_f("note", "flat-rhythm", f"sentences of nearly the same length (variation {cv:.2f})",
                          "mix short and long sentences, the way people write"))
        firsts = [(_words(x) or [''])[0].lower() for x in sentences]
        if len(set(firsts)) / len(firsts) < 0.55:
            out.append(_f("note", "same-openers", "many sentences start with the same word", "vary the openings"))
    if english and len(words) >= 60:
        pos = len(re.findall(r"\b(?:amazing|incredible|perfect|love|loved|thrilled|excited|delighted|awesome|fantastic|"
                             r"stunning|wonderful|unforgettable|best)\b", low))
        friction = re.search(r"\b(?:but|however|problem|mistake|hard|costly|late|annoying|though|wrong|tired|messy|"
                             r"stuck|honestly)\b", low)
        if pos >= 4 and not friction:
            out.append(_f("note", "all-positive", "all praise and no friction", "name the problem, the trade-off or the "
                                                                              "annoying part people know is real"))
        if not re.search(r"\b(?:i|we|my|our|us|i'm|we're|i've|we've|i'd|we'd)\b", low) and \
                len(re.findall(r"\byour?\b", low)) >= 4:
            out.append(_f("note", "no-speaker", "no one is talking: all 'you', never 'I' or 'we'",
                          "let the brand or the person speak where it is true (we bake at 5, I tried it)"))
    if re.search(r"[“\"][^”\"]{8,}[”\"]", text):
        if re.search(r"\b(?:Emily|Sarah)\b", text):
            out.append(_f("warning", "default-name", "a quote from 'Emily' or 'Sarah', the names models default to",
                          "only real, approved quotes, in the person's own words"))
        else:
            out.append(_f("note", "quote", "a quote or testimonial", "use it only if it is real and approved: invented "
                                                                     "reviews and testimonials are illegal (FTC 2024, "
                                                                     "UK DMCC 2025)"))
    if english and len(re.findall(r"\b[\w-]+,\s+[\w-]+,?\s+and\s+[\w-]+\b", text)) >= 2:
        out.append(_f("note", "triads", "two or more lists of three", "keep the list that matters, as two or four"))
    if not CAPTION_ROLES.search(role or ""):
        for sentence in _sentences(text):
            n = len(_words(sentence))
            if n > (18 if script == "bengali" else 22):
                out.append(_f("note", "long-sentence", f"a {n}-word sentence", "split it; one idea per sentence"))
                break
    codes = [code] + (["bn"] if code != "bn" and has_bengali(text) else [])
    out += lint_voice(text, [c for c in codes if c], "", role, locale, lang)
    if is_lyric(role):
        # The voice rules and the lists were calibrated on posts and ads: in a song they are advice, not a verdict.
        # Hard errors stay: dashes, chatbot leftovers, calques, West Bengal words in a Bangladeshi song.
        out = [f for f in out if f["code"] not in LYRIC_SKIP]
        for f in out:
            if f["severity"] != "note" and (f["code"] in LYRIC_SOFT or f["code"].endswith("-voice")):
                f["severity"] = "note"
    return out


def lint_spoken(text: str, lang: str = "", locale: str = "") -> list:
    """Copy that is heard, not read (a reel's voiceover, an ad read, an explainer): the listener cannot see symbols,
    brackets or links, and cannot re-read a long sentence."""
    out = []
    if re.search(r"[&/%#@*<>\[\]{}()|~^_=+]", re.sub(r"\d+/\d+", "", text)):
        out.append(_f("warning", "spoken-symbol", "symbols or brackets in copy that is read aloud",
                      "write what the voice says: 'and', 'percent', 'taka'; say the aside as its own sentence"))
    if re.search(r"https?://|www\.|\.(?:com|net|org|bd|xyz)\b", text, re.I):
        out.append(_f("warning", "spoken-link", "a web address in copy that is read aloud",
                      "say it the way people say it ('tidewater dot com'), or say where to tap"))
    if EMOJI_RX.search(text):
        out.append(_f("warning", "spoken-emoji", "emoji in copy that is read aloud", "cut them; a voice cannot say them"))
    abbr = [w for w in re.findall(r"\b[A-Z]{2,}\b", text) if w not in ("OK", "TV", "AI")]
    if abbr:
        out.append(_f("note", "spoken-abbr", f"abbreviations a voice may spell or misread: {', '.join(abbr[:4])}",
                      "write them the way they are said, or the full words"))
    if "৳" in text:
        out.append(_f("note", "spoken-taka", "the ৳ sign in copy that is read aloud", "write ১,৫০০ টাকা"))
    for sentence in _sentences(text):
        n = len(_words(sentence))
        if n > 16:
            out.append(_f("note", "spoken-long", f"a {n}-word sentence for the ear",
                          "one idea per breath: split it (about 8 to 14 words)"))
            break
    code = lang_of(text, lang)
    return out + lint_voice(text, [code] if code else [], "spoken", locale=locale, lang=lang)


URL_RX = re.compile(r"https?://\S+|(?<![@\w.])(?:www\.)?[a-z0-9-]{1,63}(?:\.[a-z0-9-]{1,63}){0,8}\.(?:com|net|org|io|co|"
                    r"ai|app|bd|in|uk|us|info|me|shop|store|xyz|dev|ly|gl|gg|tv|link|site|online)\b(?:/\S*)?", re.I)
# twitter-text v3 (emojiParsingEnabled) weighs every emoji as 2, whatever its code points: a skin tone, a flag, a
# keycap, a tag flag or a ZWJ family is one emoji
EMOJI_CLUSTER = re.compile("[\\U0001F1E6-\\U0001F1FF]{2}|[0-9#*]\\uFE0F?\\u20E3|\\U0001F3F4[\\U000E0020-\\U000E007F]+|"
                           "[\\U0001F000-\\U0001FAFF\\u2600-\\u27BF][\\uFE0F\\U0001F3FB-\\U0001F3FF]*"
                           "(?:\\u200D[\\U0001F000-\\U0001FAFF\\u2600-\\u27BF][\\uFE0F\\U0001F3FB-\\U0001F3FF]*)*")
MARKDOWN_RX = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__|\[[^\]\n]+\]\((?:https?://|www\.)[^)\s]+\)|^#{1,6}\s+\S|^```", re.M)
THREAD_MARK = "^\\s*(?:\\d{1,2}/|\\(\\d{1,2}/\\d{1,2}\\))(?=\\s)|\U0001F9F5"  # 1/ or (1/5), not 3/4 cup or 12/25
GSM7 = set("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿"
           "abcdefghijklmnopqrstuvwxyzäöñüà")
GSM7_EXT = set("^{}\\[~]|€")


def x_length(text: str) -> int:
    """The length X counts: a link is 23, an emoji 2, CJK and most scripts past U+10FF 2, the rest 1 (Bengali and
    Devanagari included)."""
    t = EMOJI_CLUSTER.sub("xx", URL_RX.sub("x" * 23, unicodedata.normalize("NFC", text)))
    return sum(1 if cp <= 0x10FF or 0x2000 <= cp <= 0x200D or 0x2010 <= cp <= 0x201F or 0x2032 <= cp <= 0x2037 else 2
               for cp in map(ord, t))


def sms_parts(text: str) -> int:
    """SMS parts: 160 characters in the GSM alphabet (153 a part when split), 70 otherwise (67), as with Bengali
    or an emoji."""
    if all(c in GSM7 or c in GSM7_EXT for c in text):
        n = len(text) + sum(c in GSM7_EXT for c in text)
        return 1 if n <= 160 else -(-n // 153)
    n = len(text.encode("utf-16-le")) // 2
    return 1 if n <= 70 else -(-n // 67)


def platform_checks(text: str, platform: str, role: str = "") -> list:
    """What the platform does to the text: X and Threads refuse a long post, SMS splits it, feeds show markdown as
    raw symbols, 'link in bio' belongs where posts cannot carry a link, thread numbering belongs on X, and a reply
    is read in short lines."""
    out = []
    if platform == "x" and x_length(text) > 280:
        out.append(_f("error", "too-long", f"{x_length(text)} of 280 characters as X counts them (a link is 23, an "
                                           f"emoji 2)", "cut it to 280, or make it a thread"))
    if platform == "threads" and len(text) > 500:
        out.append(_f("error", "too-long", f"{len(text)} of 500 characters", "cut it to 500"))
    if platform == "sms" and sms_parts(text) > 1:
        out.append(_f("warning", "sms-parts", f"{sms_parts(text)} SMS parts (160 characters a part in plain Latin "
                                              f"text, 70 with Bengali or an emoji)", "cut it to one part"))
    md = MARKDOWN_RX.search(text)
    if md and platform not in ("whatsapp", "email", "web"):
        out.append(_f("warning", "markdown", f"markdown ('{md.group(0)[:20]}') that {platform or 'a feed'} shows as "
                                             f"raw symbols", "plain text: line breaks, and a word in capitals for "
                                                             "emphasis if the brand does that"))
    if platform in ("x", "linkedin", "facebook", "threads") and re.search(r"\blink in (?:my |our |the )?bio\b", text,
                                                                          re.I):
        out.append(_f("warning", "link-in-bio", f"'link in bio' on {platform}, where the post can carry the link",
                      "put the link in the post"))
    if platform in ("instagram", "linkedin", "facebook") and re.search(THREAD_MARK, text, re.M):
        out.append(_f("warning", "thread-numbering", f"thread numbering (1/, 🧵) on {platform}",
                      "one post; a carousel carries the steps"))
    if REPLY_ROLES.search(role or "") and "\n" not in text.strip():
        n_sent = len(_sentences(text))
        if n_sent >= 4 and len(_words(text)) < 150:
            out.append(_f("note", "reply-block", f"a {n_sent}-sentence reply in one block",
                          "break it into short lines: the answer first, then what happens next"))
    return out


def lint_caption(text: str, platform: str = "instagram", locale: str = "", lang: str = "",
                 voice: dict | None = None, role: str = "caption") -> list:
    """Checks for a caption, a post body or any longer text, on top of lint_string; spoken copy (a voiceover
    platform or a script role) gets the checks for the ear instead of the feed's."""
    out = lint_string(text, role or "caption", locale, platform, lang, voice)
    p = PLATFORM.get((platform or "").split("-")[0].lower(), {})
    if p.get("spoken") or SPOKEN_ROLES.search(role or ""):
        return out + lint_spoken(text, lang, locale)
    out += platform_checks(text, (platform or "").split("-")[0].lower(), role)
    post = not REPLY_ROLES.search(role or "")  # a reply opens with the person's name and has no fold to protect
    first = text.strip().split("\n", 1)[0]
    n_first = visible_len(first)
    if post and p.get("preview_chars") and n_first > p["preview_chars"]:
        out.append(_f("warning", "hook-cut", f"the first line is {n_first} characters; {platform} shows about "
                                                f"{p['preview_chars']} before 'more'",
                      f"put the hook in the first {p['preview_chars']}"))
    if post and GREETING_OPEN_RX.search(text):
        out.append(_f("warning", "greeting-open", "the caption opens with a greeting", "open with the payoff; the "
                                                                                      "greeting costs the fold"))
    if post and re.match(r"\s*(?:#|[\U0001F300-\U0001FAFF\u2600-\u27BF])", text) and (locale or "").upper() != "BD":
        out.append(_f("note", "emoji-first", "the caption starts with an emoji or a hashtag", "start with words"))
    tags = HASHTAG_RX.findall(text)
    hi = p.get("hashtags", (0, 5))[1]
    cap = p.get("hashtag_cap")
    if cap and len(tags) > cap:
        out.append(_f("error", "hashtag-cap", f"{len(tags)} hashtags; {platform} accepts {cap}", f"≤ {cap}"))
    elif len(tags) > hi:
        out.append(_f("warning", "hashtags", f"{len(tags)} hashtags; {hi} or fewer read native on {platform}",
                      "keep the few that name the topic or the brand"))
    emo = EMOJI_RX.findall(text)
    if p.get("emoji_max") is not None and len(emo) > p["emoji_max"]:
        out.append(_f("warning", "emoji", f"{len(emo)} emoji", f"≤ {p['emoji_max']} on {platform}; one per idea"))
    bullets = re.findall(r"^\s*[\U0001F300-\U0001FAFF✅✨\U0001F525\U0001F449]\s", text, re.M)
    if len(bullets) >= 3:
        out.append(_f("warning", "emoji-bullets", "emoji used as bullets on three or more lines",
                      "plain line breaks read more human"))
    return out


# What a 2026 model writes by default is not purple prose but launch templates: each is fine once, and brands use
# them, but 12 of 72 model captions stacked two or more against 0 of 1,658 brand posts (voice-casual-en.md §7).
LAUNCH_TEMPLATES = [re.compile(rx, re.I | re.M) for rx in (
    r"\b(?:is|are)\s+(?:finally\s+)?here\b|\bhas\s+(?:finally\s+)?arrived\b|\bjust\s+(?:landed|dropped)\b",
    r"\b(?:meet|say\s+hello\s+to|introducing)\s+(?:our|the|your)\b",
    r"\b(?:discover|explore)\s+(?:our|the\s+new)\b",
    r"\ba\s+(?:quieter|softer|slower|calmer|gentler)\s+(?:moment|finish|morning|pace|way)\b",
    r"\bentered\s+the\s+(?:\w+\s+)?chat\b|^\s*\w+\s+called[,.]|\bcue\s+the\b|\bfinally,\s+a\s+(?:way|place|reason)\s+to\b|"
    r"\bjust\s+got\s+(?:easier|better)\b",
    r"^\s*(?:new|same)\s+[\w'’]+,\s+(?:new|same)\s+\w+",
    r"\bthe\s+warmth\s+of\b|\b\w+\s+meets\s+\w+\.",
    r"\b(?:is|are)\s+calling\b",
    r"\byour\s+\w+(?:\s+\w+)?\s+(?:has\s+been\s+waiting|noticed|is\s+jealous)\b",
)]
SOLEMN_RX = re.compile(r"\b(?:condolences?|thoughts\s+are\s+with|hearts\s+go\s+out|rest\s+in\s+peace|victims|in\s+memory\s+of|"
                       r"affected\s+by\s+the\s+(?:floods?|fires?|earthquake|cyclone|storm)|anniversary\s+of\s+the\s+"
                       r"(?:attack|tragedy))\b", re.I)
SELLING_RX = re.compile(r"\d+\s?%\s?off|\bsale\b|\buse\s+code\b|\b(?:order|shop|buy)\s+now\b|\bfree\s+delivery\b", re.I)
BAD_NEWS_RX = re.compile(r"\b(?:outage|app\s+is\s+down|is\s+down|delayed|cancell?ed|price\s+(?:rise|increase)|breach|recall|"
                         r"layoffs?)\b", re.I)
JOKE_RX = re.compile(r"\b(?:lol|lmao|oops|our\s+bad|plot\s+twist|touch\s+grass)\b|[😂🤣💀😅]", re.I)


def lint_deck(strings: list, locale: str = "", platform: str = "", voice: dict | None = None) -> dict:
    """strings: [{"role", "text", "lang"?}]. Returns {"items": [...], "deck": [...], "errors": n, "warnings": n}."""
    items = []
    for s in strings:
        role, text, lang = s.get("role", ""), s.get("text", ""), s.get("lang", "")
        long_form = CAPTION_ROLES.search(role or "") or SPOKEN_ROLES.search(role or "")
        found = lint_caption(text, platform, locale, lang, voice, role) if long_form else \
            lint_string(text, role, locale, platform, lang, voice)
        items.append({"role": role, "text": text, "findings": found})
    deck = []
    song = bool(strings) and all(is_lyric(s.get("role", "")) for s in strings)
    words = [] if song else [w.lower() for s in strings for w in _words(s.get("text", "")) if len(w) > 3]
    for w in sorted(set(words)):          # a song repeats its refrain on purpose
        if words.count(w) >= 3:
            deck.append(_f("note", "repeat", f"'{w}' appears {words.count(w)} times",
                           "cut it, or keep the same word: rotating synonyms reads machine-made"))
    if sum(s.get("text", "").count("!") for s in strings) > 2:
        deck.append(_f("warning", "exclamation", "more than two exclamation marks in the piece", "one at most"))
    joined = " ".join(s.get("text", "") for s in strings)
    if BN_APNI.search(joined) and BN_TUMI_VERBS.search(joined):
        deck.append(_f("warning", "bn-honorific", "আপনি and তুমি verb forms in one piece (আপনি … করো)",
                       "one address form throughout: আপনি with করুন, তুমি with করো"))
    title = next((s["text"] for s in strings if re.search(r"^(?:video_)?title$", s.get("role", ""), re.I)), "")
    thumb = " ".join(s["text"] for s in strings if re.search(r"thumb", s.get("role", ""), re.I))
    if title and thumb:
        stop = {"the", "a", "an", "and", "to", "of", "in", "for", "on", "with", "is", "এর", "ও", "আর", "একটি", "এই"}
        shared = {w.lower() for w in _words(title)} & {w.lower() for w in _words(thumb)} - stop
        shared = {w for w in shared if len(w) > 2}
        if shared:
            deck.append(_f("warning", "thumb-repeats-title", "the thumbnail text repeats the title: " +
                           ", ".join(sorted(shared)), "the thumbnail adds what the title lacks, in 2-4 words"))
    templates = [rx.pattern[:30] for rx in LAUNCH_TEMPLATES if rx.search(joined)]
    if len(templates) >= 2:
        deck.append(_f("warning", "launch-templates", f"{len(templates)} launch templates in one piece ('is here', "
                                                      f"'Meet our', 'Discover our' …)", "rewrite one of them around a fact"))
    if SOLEMN_RX.search(joined) and SELLING_RX.search(joined):
        deck.append(_f("warning", "grief-sells", "a message of grief or tragedy with an offer in it",
                       "split them: a quiet message now, no offer; sell another day"))
    if BAD_NEWS_RX.search(joined) and JOKE_RX.search(joined):
        deck.append(_f("warning", "joke-on-bad-news", "a joke or a laughing emoji on bad news (an outage, a delay, a price "
                                                      "rise)", "plain: one apology, what happened, what you're doing, "
                                                              "when it's fixed"))
    replies = [re.sub(r"@\w+|\b[A-Z][a-z]+\b", "", x.get("text", "")).lower().strip() for x in strings
               if re.search("reply|comment", x.get("role", ""), re.I)]
    if any(replies.count(r) >= 3 for r in set(replies) if r):
        deck.append(_f("note", "copy-paste-replies", "the same reply three times", "answer each person; vary the words"))
    if len(re.findall("উপভোগ করুন", joined)) >= 2:
        deck.append(_f("note", "bn-enjoy", "উপভোগ করুন more than once in the piece (the translated 'enjoy')",
                       "once at most, never as the call to action"))
    ctas = [s for s in strings if CTA_ROLES.search(s.get("role", ""))]
    if len(ctas) > 1:
        deck.append(_f("warning", "many-ctas", f"{len(ctas)} calls to action", "one per piece"))
    allf = [f for it in items for f in it["findings"]] + deck
    return {"items": items, "deck": deck, "errors": sum(f["severity"] == "error" for f in allf),
            "warnings": sum(f["severity"] == "warning" for f in allf)}


# ------------------------------------------------------------------------------------------------ languages
MATH_ALNUM = re.compile("[\U0001D400-\U0001D7FF]")   # 𝗯𝗼𝗹𝗱 / 𝘪𝘵𝘢𝘭𝘪𝘤 "fonts" made of maths symbols


def punctuation(text: str, lang: str = "") -> list:
    """Per-language punctuation that marks a translation or a copy-paste from English."""
    out = []
    lang = (lang or "").lower()
    if MATH_ALNUM.search(text):
        out.append(_f("warning", "unicode-bold", "letters from the Unicode maths block (𝗯𝗼𝗹𝗱, 𝘪𝘵𝘢𝘭𝘪𝘤)",
                      "screen readers spell them out or skip them; use plain letters"))
    if lang.startswith("es"):
        if "?" in text and "¿" not in text:
            out.append(_f("warning", "es-question", "a Spanish question without ¿", "open it with ¿"))
        if "!" in text and "¡" not in text:
            out.append(_f("warning", "es-exclaim", "a Spanish exclamation without ¡", "open it with ¡"))
    if lang.startswith("fr") and not lang.startswith("fr-ca"):
        if re.search(r"[^\s  ][;!?]", text):
            out.append(_f("note", "fr-spacing", "no space before ; ! or ?", "a narrow no-break space (U+202F) before "
                                                                           "; ! ?, a no-break space before :"))
        if re.search(r'"[^"]+"', text):
            out.append(_f("note", "fr-quotes", "English quotes in French", "« guillemets » with narrow spaces"))
    if lang.startswith(("zh", "ja")) and re.search(r"[぀-ヿ一-鿿][,.!?:;]", text):
        out.append(_f("note", "cjk-halfwidth", "half-width punctuation after CJK text", "full-width ，。！？：；"))
    if lang.startswith("de") and re.search(r'"[^"]+"', text):
        out.append(_f("note", "de-quotes", "English quotes in German", "„so“"))
    return out


def lexicon(text: str, brand_voice: dict | None) -> list:
    """The brand's own words: voice.avoid (never) and voice.prefer ({'use this': 'instead of that'})."""
    out = []
    if not brand_voice:
        return out
    low = text.lower()
    for w in brand_voice.get("avoid", []) or []:
        if w and w.lower() in low:
            out.append(_f("warning", "brand-avoid", f"'{w}' is on the brand's avoid list", "use the brand's words"))
    for use, instead in (brand_voice.get("prefer") or {}).items():
        for x in ([instead] if isinstance(instead, str) else instead):
            if x and x.lower() in low:
                out.append(_f("note", "brand-prefer", f"the brand says '{use}', not '{x}'", use))
    return out
