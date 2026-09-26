# Copy that reads human

Readers drop copy that reads machine-made in the first line, in any language: the em dash, the "not just X, it's Y"
turn, the textbook word where a person would use an everyday one, the translated sentence, the greeting that wastes
the fold. This file is the writing half of the design:
- house rules;
- the tells and their fixes, in English, Bangladeshi Bengali and twelve other languages;
- hooks, calls to action, captions and platform limits;
- how `copylint` and `copyjudge` rate the copy before it goes on a design.

For the voice itself (learning the audience's own words, the register ladder, casual that is not fake casual, replies,
scripts for the ear, 18 more languages) use the `natural-text` skill: it writes, and this file and the lint check.

Research behind it (24 September 2026): four research passes covered
- AI-writing studies and humanizer repositories (`references/research/copy-ai-tells.md`);
- natural Bangladeshi Bengali in 2024 to 2026 brand posts (the findings and sources are in §3);
- hooks, CTAs and platform data (`references/research/copy-hooks-ctas-platforms.md`);
- transcreation (`references/research/copy-transcreation.md`).

A second pass the same day (the voice research) measured natural, casual copy against AI copy in English, Bangla and
18 more languages and read 89 humanizer and anti-slop projects: `references/research/voice-*.md`. Its 932 tested rules
in 24 languages are in `scripts/voice_rules.json`, and `copylint --lang` picks a language's rules (§9).

The same day a study ran `copylint` over natural and robotic lines in Bengali and English, and the lint was tuned to
catch the robotic lines without flagging what Bangladeshi brands and newspapers really write (§3.1 and §3.2). Sources
are listed at the end of each section and at the end of the file.

## 1. House rules (every piece, every language)

1. **No em dash, in any language.** Never write an em dash or a double hyphen, and never a spaced en dash as a
   pause, on a design or in a caption. Readers now take them as the mark of AI-written copy. Rewrite the sentence with
   a comma, a colon, a full stop or brackets.
   - No language is an exception (§4, rule 11).
   - Neither is the brief or the client's own copy: propose the dash-free line and ship it once the client approves
     (`craft.md` §2).
   - Between words, write "to" (Tuesday to Sunday).
   - Between numbers, write "to", a hyphen, or in Latin text a closed-up en dash (10–12, 09:00–13:00).
   - Bengali and other dense scripts write ranges the local way: ১০-১২, ১০ থেকে ১২, সকাল ১১টা থেকে রাত ৮টা.
   - `checks` and `copylint` treat the em dash and the spaced en dash as errors.
2. **Write the way the reader talks and writes on social media today, in their market.**
   - The register, address form, loanwords, spelling and numbers are the market's. §3–4 cover them.
   - The requester's language and location are not the market's.
3. **One reader, one idea, one action.**
   - Name one person you are writing for. Every sentence carries one idea.
   - Each piece has at most one call to action, or rightly none.
4. **Specific beats impressive.**
   - Use a number, a name, a place, a time or a concrete detail from the client's facts, never a superlative.
   - Never invent a fact to make the line specific.
5. **Short and active.**
   - Short sentences (Latin ≤ 22 words, Bengali ≤ 18 words).
   - Verbs over nouns: "we weave", not "weaving is carried out".
   - Concrete nouns over abstractions.
6. **No AI or template tells.**
   - None of the §2 vocabulary or structures in English.
   - None of the §3 bookish, translated or sadhu forms in Bengali.
   - For other languages, the §4 translation tells.
7. **Hook first.**
   - The first words the reader meets must earn the second look (§5): the headline, frame 1, the cover slide, and
     the first line of the caption.
   - Exclamation marks: an English headline takes none. A Bengali hook may end in one, as Bangladeshi hooks often
     do (§3.6). Never more than one in a line.
8. **The call to action is a verb and a benefit, read in one glance.**
   - On the design: 2 to 4 words in Latin script (3 is the sweet spot), and at most 6 in Bengali, where a verb such
     as অর্ডার করুন takes two words. `copylint` warns above 4 and 6.
   - The detail (the time, the price, the deadline) goes on its own line beside it (§6).
   - Match it to the goal (§6).
   - Urgency only with a fact: a date, a time or a count.
9. **Every social design ships with its caption** (§7):
   - the hook in the first line, before the platform cuts it;
   - short lines;
   - hashtags within the platform's native range (§7);
   - alt text.
   - **Emoji, the one rule for this skill:** 0 or 1 in the text on the image, up to 3 in a caption, never as bullets.
     `copylint` warns above 1 on an image and above 3 in a caption. Other sections point here.
10. **Read it aloud as the reader.**
    - If a friend would not say it that way in a message, rewrite it.
    - If it could be any brand's line, make it this brand's.
11. **More human does not mean more slang.** Never add slang, particles, emoji, typos or feelings to make a line sound
    human, and never invent an experience ("we tasted it at dawn"). Adding casual words did not hide AI text from
    expert readers (Russell et al.), and humanizer rewrites leave their own fingerprint. Keep only the voice the
    brief or the brand gives, and never pass client copy through a third-party humanizer tool: they strip hyphens,
    break ranges such as ১০-১২ and invent facts (Pangram).

## 2. English: the tells and the fixes

One tell can be chance; a cluster is the strongest sign (Wikipedia, "Signs of AI writing"). `copylint` flags the
tells marked (lint) and the structures in §2.2; the rest are for the writer and `copyjudge`. Fix every error and every
cluster, and keep a single soft word only when it is literally true (robust steel).

### 2.1 Punctuation

| Tell | Why it reads as AI | Fix |
|---|---|---|
| Em dash, double hyphen, spaced en dash (lint, error) | Models use about 9–11 per 1,000 words against about 3 in human essays (Freeburg 2026); readers now spot it | a comma, a colon, a full stop, brackets, or a new sentence. An explicit ban brings Claude's rate to zero |
| Colon reveal ("The best part: it learns.") (lint: in headlines, and two or more in body copy) | a model rhythm; banning the em dash moves the same aside into colons | write the payoff as the sentence |
| Emoji bullets (✅ 🔹 🚀 at the start of lines) (lint) | ✅ appears at 11× the human rate (Washington Post, 2025) | plain line breaks; emoji within the §1 rule, never as bullets |
| Arrows (→) in running copy (lint) | a list habit | "to", "then" |
| More than one "!" (lint) | ad-speak | a full stop; one "!" per piece at most, and none in an English headline |
| Ellipsis as a transition | filler | a full stop |
| Semicolons in ads and social copy | essay register | two sentences |
| 𝗕𝗼𝗹𝗱 or 𝘪𝘵𝘢𝘭𝘪𝘤 Unicode letters (lint) | screen readers skip or spell them | plain letters; emphasis on the design, not in the caption |

### 2.2 Structures (before → after)

`copylint` catches every "Before" example below except a single rule of three (it notes two or more lists of three
in one piece); the staccato run is a note.

| Tell | Before | After |
|---|---|---|
| "Not just X, it's Y" (the loudest tell), also split by a full stop | Not just a roof. It's peace of mind. | A written scope and a fixed price before anyone climbs a ladder. |
| "More than X, it's Y" and "Where X meets Y" | More than a café, it's a feeling. · Where craft meets comfort. | Forty seats, one long table, open till 11. |
| Negative countdown | Not a bug. Not a feature. A design flaw. | It's a design flaw. |
| Rule of three | Trusted, reliable and built to last. | Six nails per shingle, every shingle. |
| "Whether you're X or Y" | Whether you're a beginner or a pro… | Built for your first 10K. |
| A question it answers itself | The result? Faster shipping. | Orders ship the same day. |
| Sign-posting | Here's the thing: our bread is fresh. | Baked at 5 a.m. |
| "In today's…" opener | In today's fast-paced world, you need speed. | Delivered in two hours. |
| Inflated significance | The launch marks a pivotal moment for the company. | The launch is the company's first paid product. |
| Trailing "-ing" clause | adds file search, highlighting our commitment to workflows | adds file search, so you find old drafts without leaving the editor |
| Avoiding "is" and "has" | The café boasts 40 seats. | The café has 40 seats. |
| Punchline closer | Let that sink in. | (end on the last fact) |
| Staccato run | Real dough. Real fire. Real fast. | Out of the oven in 90 seconds. |
| False range | From innovation to implementation, we… | (name the two real things) |
| Stacked hedges | It may potentially help. | It may help. |
| Borrowed authority | Experts agree… | (name the source, or cut) |
| Stock ending | The future looks bright. | (end on the last fact) |
| Chatbot leftover | Here's a caption: … | (delete; `copylint` fails it) |
| The rest of the contrast family | It's not about the coffee, it's about the people. · The problem isn't X. It's Y. · X isn't the problem. Y is. · No fuss, no queues, just coffee. · It doesn't just hydrate, it transforms. | say the positive claim once: We open at 7 so regulars get a coffee before work. |
| ", not X" tails (a note at two) | Real butter, not margarine. Baked daily, not frozen. | Real butter, baked every morning. |
| Candour as a costume (a note at two) | Real talk: … Honestly? … · Pro tip: · PSA: | say it; one "Honestly?" before something true is a person |
| Social formulas (lint) | Meet X, your new favorite · Think X meets Y · Thank me later · *chef's kiss* · (yes, really) · What do you think? as the last line · "so this one hits" in a reply | the fact, and a real question or none |

Rhythm: people mix short and long sentences. Six or more sentences of nearly the same length, many sentences that
open with the same word, or two lists of three in one piece read as generated (`copylint` notes them).

### 2.3 Vocabulary

**Tier 1, flag on one sighting:**

| Word or phrase | Plain replacement |
|---|---|
| delve | look at |
| underscores | shows |
| showcasing | showing |
| a testament to | proof of |
| tapestry | mix |
| boasts | has |
| garner | get |
| pivotal | key |
| groundbreaking | new, first |
| meticulous | careful |
| interplay | mix |
| bolster | back |
| realm | field |
| multifaceted | varied |
| unveil | show, launch |
| revolutionize | change |
| elevate | improve |
| unlock / unleash | get, use |
| embark | start |
| game-changer | name the change |
| cutting-edge | new |
| transformative | name the result |
| nestled / in the heart of | in |
| breathtaking | describe it |
| diverse array | range |
| ever-evolving | changing |
| paramount | most important |
| supercharge | speed up |
| leverage / harness | use |
| synergy | say what works together |
| holistic | whole |
| world-class / best-in-class | name the proof |
| rich heritage | long history |
| hidden gem / must-visit | say what is special |

**Tier 2, flag when two or more appear in one piece:**

| Word | Plain replacement |
|---|---|
| crucial | important |
| vibrant | lively |
| robust | strong |
| foster | build |
| enhance | improve |
| intricate | detailed |
| valuable | useful |
| additionally, moreover | also |
| comprehensive | full |
| streamline | simplify |
| journey | the real process |
| landscape | market |
| navigate | handle |
| renowned | known for |
| empower | let |
| curated | chosen |
| resonate | appeal |
| discover, experience | the real verb |
| innovative | new |
| effortless | easy |
| seamless | smooth, easy. Literal use is fine (seamless leggings, a seamless carousel); "a seamless experience" (or integration, transition, journey) is still flagged on sight |

The lists move with every model generation (in 2025 ChatGPT used "core" five times as often as a year earlier). Add
what you see to the lists in `scripts/copyrules.py`.

### 2.4 Ads and marketing

| Tell | Fix |
|---|---|
| Hype verb + "your X" (unlock your potential, elevate your mornings) (lint) | say what the product does |
| Empty superlatives (most trusted, award-winning, world-class) | name the proof, or cut it |
| Invented proof ("Loved by 10,000+ customers") (lint, a note) | a real number with its source in the brief, or a marked placeholder |
| Stock constructions: Look no further · Say goodbye to · That's where we come in · Imagine a… · More than just · "[Problem]? Meet [solution]." (lint) | say what it does |
| Stock marketing phrases: perfect blend of · a world of · like never before · tells a story · crafted (or made) with love or passion · your journey · you deserve it · every step of the way · committed to delivering · we've got you covered · indulge in · redefine · treat yourself to (lint) | say the concrete thing: what it is, what it costs, when it is ready |
| Launch hype ("Big news! We're thrilled to announce") (lint) | lead with the news: "New: Smart Templates. 14-day free trial." |
| Engagement bait (tag a friend, tag someone, like and share, drop a 🔥 in the comments) (lint) | platforms demote it; ask a real question, or none (§6) |
| Urgency without a fact (Act now, Don't miss out, Hurry) (lint) | the real date or quantity: "until 30 Sept", "40 left". Urgency that states a fact passes: "30% off ends Sunday at midnight" |
| Generic buttons (Learn more, Click here, Submit, Get started) (lint) | the action and the thing: "Book a tasting", "Get the menu". "Get started" only when nothing more specific fits (§6) |
| Tourism puffery (nestled, hidden gem, a feast for the senses) (lint) | the place plus one concrete detail |

**Portability test:** if the line would work unchanged for any other brand, cut it or make it this brand's
(no-ai-slop).

## 3. Bengali for Bangladesh

Readers in Bangladesh scroll in everyday চলিত Bengali, mixed with the English words they really use. Copy that reads
like a textbook, a government notice, a Kolkata paper or a machine translation loses them in the first line. Prothom
Alo (2025) calls AI Bengali grammatical but absent from everyday talk. `copylint` carries these rules and the voice
research's (`references/research/voice-bangla.md`, `natural-text/references/bangla.md`). One Bengali natural-writing
skill exists on GitHub (opuu/bangla-writer, MIT, August 2026, not yet evaluated by its own rubric); its tested checks
are in the lint.

### 3.1 The tells of robotic or translated Bengali

| Tell | ✗ | ✓ |
|---|---|---|
| Literal idioms and marketing clichés (lint) | আপনার অভিজ্ঞতাকে উন্নীত করুন | কেনাকাটা এবার আরও সহজ |
| Tatsama words, notice register (lint) | অদ্যই ক্রয় করুন | আজই কিনুন |
| The translated "enjoy": উপভোগ করুন | আকর্ষণীয় মূল্যছাড় উপভোগ করুন | আকর্ষণীয় মূল্যছাড় চলছে · দামে দারুণ ছাড় |
| Sadhu forms, or sadhu mixed with চলিত (গুরুচণ্ডালী) (lint) | অর্ডার করিলেই পাইবেন ফ্রি ডেলিভারি | অর্ডার করলেই ফ্রি ডেলিভারি |
| Passive and noun chains (lint) | পেমেন্ট প্রদানের মাধ্যমে ক্যাশব্যাক গ্রহণ করা যাবে | অ্যাপে পেমেন্ট করলেই ক্যাশব্যাক |
| Notice passive (lint) | ২৪ ঘণ্টায় ডেলিভারি সম্পন্ন করা হয়ে থাকে | ২৪ ঘণ্টার মধ্যেই ডেলিভারি |
| A translated English sentence ("We are offering…") | আমরা অফার করছি ২০% ছাড় সব পণ্যে | সব পণ্যে ২০% ছাড় · থাকছে ২০% ছাড় |
| Pronouns in every slot (lint: a warning at three আপনি or আপনার in one sentence) | আপনি আপনার ফোন থেকে আপনার অ্যাকাউন্টে লগ ইন করুন | ফোন থেকে অ্যাকাউন্টে লগ ইন করুন |
| Flat statement where a spoken particle would do real work | অফার শীঘ্রই শেষ হবে | অফারটা কিন্তু বেশিদিন থাকছে না (one particle where it works; never a quota of them) |
| Honorific mismatch (lint) | আপনি আজই অর্ডার করো | আজই অর্ডার করুন (আপনি) · আজই অর্ডার করো (তুমি) |
| English punctuation and AI rhythm (lint) | অফার [em dash] শুধু আজ. | অফার শুধু আজ! |
| Kolkata or Hindi calques (lint) | এখন সব আউটলেটে উপলব্ধ | এখন সব আউটলেটে পাওয়া যাচ্ছে |
| Stock openers and hype words (lint) | আপনি কি কখনো ভেবে দেখেছেন…, যুগান্তকারী | say it straight, give the proof |
| "Not just X" calque (lint) | শুধু একটি শাড়ি নয়, একটি গল্প | ৯০ দিন ধরে হাতে বোনা শাড়ি |
| Discover, explore, claim (lint) | নতুন কালেকশন আবিষ্কার করুন · অন্বেষণ করুন · আপনার অফার দাবি করুন | নতুন কালেকশন দেখে নিন · অফারটা নিয়ে নিন |
| "Celebrate" as the call to action (lint). ঈদ উদযাপন as a noun is fine | প্রতিটি মুহূর্ত উদযাপন করুন | ঈদের দিনটা কাটুক আপনজনের সঙ্গে |
| English ad images (lint): new heights, the perfect blend, the comfort of your home, every moment, tells a story | স্বাদকে নিয়ে যান নতুন উচ্চতায় · ঐতিহ্য আর আধুনিকতার নিখুঁত সমন্বয় · বাড়ির আরাম থেকে কেনাকাটা করুন · প্রতিটি মুহূর্ত · প্রতিটি শাড়ি গল্প বলে | ঘরে বসেই কেনাকাটা, ডেলিভারি ২৪ ঘণ্টায় |
| Corporate lines (lint): we're here for you, committed to | আমরা এখানে আছি আপনার পাশে · সেরা সেবা দিতে প্রতিশ্রুতিবদ্ধ | হটলাইন খোলা রাত ১২টা পর্যন্ত |
| যাত্রা as a metaphor (lint) | শুরু হোক আপনার স্বাদের যাত্রা | আজ থেকে মেনুতে নতুন ৫টা আইটেম |
| A question the copy answers itself (lint) | ফলাফল? মচমচে ফুচকা। | অর্ডার পেলেই ফুচকা ভাজি, তাই মচমচে। |
| The -গুলি plural (lint, a note) | পণ্যগুলি এখন পাওয়া যাচ্ছে | পণ্যগুলো এখন পাওয়া যাচ্ছে |

Rows marked (lint) are `copylint` checks; the others are for the writer and `copyjudge`.
- **Word order and slogans with no fact in them are left to the judge.** Bangladeshi ads often put the verb first
  ("থাকছে ২০% ছাড়"), so a word-order rule would flag good copy. The lint does not check word order.
- **One মাধ্যমে in a caption is normal** (Pathao uses it); a chain of them is the tell.
- **Repeated pronouns:** two আপনি or আপনার in a sentence can be fine; three in one sentence is a warning.

### 3.2 Formal → everyday

Standard ad phrases stay: শর্ত প্রযোজ্য, সীমিত সময়ের অফার. উপভোগ করুন is the translated "enjoy": use it at most
once in a post, and never as the call to action.

**Warned:** clear bookish or translated words. `copylint` gives a warning and the everyday word.

| Formal | Everyday | Formal | Everyday |
|---|---|---|---|
| ক্রয় করুন | কিনুন | অত্যন্ত | খুব |
| প্রদান করুন | দিন | গ্রহণ করুন | নিন |
| প্রেরণ করুন | পাঠান | প্রাপ্ত হবেন | পাবেন |
| অবগত হোন | জেনে নিন | অবহিত করা যাচ্ছে যে | জানিয়ে রাখি |
| পরিদর্শন করুন | ঘুরে আসুন / ভিজিট করুন | আস্বাদন করুন | চেখে দেখুন |
| পরিধান করুন | পরুন | মতামত প্রদান করুন | মতামত জানান |
| যোগাযোগ স্থাপন করুন | ইনবক্স করুন / কল করুন | সমাপ্তি | শেষ |
| প্রারম্ভ | শুরু | অদ্য | আজ |
| অবিলম্বে / তৎক্ষণাৎ | এখনই / সঙ্গে সঙ্গে | সর্বদা | সবসময় |
| পুনরায় | আবার | পরবর্তীতে | পরে |
| নিমিত্তে | জন্য | ব্যতীত | ছাড়া |
| সহিত | সঙ্গে | উক্ত | এই |
| নিম্নলিখিত / উপরোক্ত | নিচের / ওপরের | অনুগ্রহপূর্বক | দয়া করে, or drop it |
| মূল্যহ্রাস | ছাড় / ডিসকাউন্ট | উপলব্ধ | পাওয়া যাচ্ছে |
| গ্রাহকবৃন্দ | গ্রাহকেরা / আপনারা | বাসস্থান | বাসা |
| হস্তনির্মিত | হাতে বানানো / হাতে বোনা | | |

**Noted:** standard Bengali, right in some senses, but stiffer than everyday ad copy. `copylint` adds a note, not a
warning; keep the word where its sense needs it.

| Word | Everyday in ad copy | Where it is right |
|---|---|---|
| সংগ্রহ করুন | নিয়ে নিন | fashion drops: an Easy Fashion post ends "আজই সংগ্রহ করুন" |
| শীঘ্রই | শিগগিরই (Prothom Alo's style) | "শীঘ্রই আসছে" is fine |
| বর্তমানে | এখন | bKash uses it |
| সহায়তা | সাহায্য (Robi's support page) | "আর্থিক সহায়তা" (Prothom Alo) |
| প্রয়োজনীয় | দরকারি | notices, instructions |
| সম্পন্ন | শেষ | forms, confirmations |
| নিবন্ধন | রেজিস্ট্রেশন | জন্ম নিবন্ধন, the legal term |
| পর্যাপ্ত | যথেষ্ট | reports |
| অংশগ্রহণ করুন | যোগ দিন | formal event notices |
| নির্বাচন করুন | বেছে নিন | app strings |
| উদ্দেশ্যে | জন্য | formal notices |
| বিক্রয় | বিক্রি | "বিক্রয় প্রতিনিধি", a job title |

The same calibration also notes, rather than warns on, সূচনা (শুরু), সুসংবাদ (সুখবর), স্বল্পমূল্যে and সাশ্রয়ী মূল্যে
(কম দামে), and the hype words বিপ্লবী and সুবর্ণ সুযোগ, which the judge weighs in context.

**Not flagged:** সুস্বাদু, মূল্যছাড় and দ্রুততম are normal in Bangladeshi ads and news. Daraz titles its Eid page
"আকর্ষণীয় মূল্যছাড়", The Daily Star Bangla writes সুস্বাদু, and Prothom Alo writes দ্রুততম.

The lists in `scripts/copyrules.py` hold every word. Add to them as you find more.

### 3.3 Code-mixing

1. **The grammar stays Bengali.**
   - The commonest mixed pattern in Bangladeshi social media is an English verb stem with a Bengali auxiliary (34 % of
     120,000 tokens, Sweet et al. 2025): অর্ডার করুন, ট্যাগ করো, never আদেশ প্রদান করুন.
   - English nouns take Bengali case endings.
2. **Script.**
   - Loanwords go in Bengali script.
   - Brand, app and product names, promo codes, URLs and USSD codes stay in Latin script.
   - A Latin word takes its case ending after a hyphen: Daraz-এ, মিরপুর ১০-এ.
3. **At most one punchy English word in Latin script** in a Bengali line on a consumer graphic, as Robi does with "No"
   or "Tension". `copylint` notes more.
4. **Banglish (romanised Bengali):**
   - fine in replies, comments and the captions of youth brands that talk that way;
   - never in headlines, prices or terms;
   - Bangladesh's High Court barred it from broadcast media in 2012.
5. **English-only posts** suit premium lifestyle brands (Aarong and Yellow posted in English). Aarong switches to
   Bengali with আপনি for community stories.
6. **Borrow only the English word people actually use.** Many readers dislike mixing for its own sake.

Loanwords that read as normal:

| Group | Words |
|---|---|
| Offers | অফার, ডিসকাউন্ট, ক্যাশব্যাক, প্রোমো কোড, ভাউচার, কম্বো, বোনাস, স্পেশাল, ধামাকা |
| Orders | অর্ডার, ডেলিভারি, ক্যাশ অন ডেলিভারি, ফ্রি |
| Products | কালেকশন, সাইজ, প্যাক, ডাটা |
| Places | আউটলেট, রেস্টুরেন্ট |
| Digital | অ্যাপ, ডাউনলোড, লিংক, ইনবক্স, মেসেজ, কমেন্ট, শেয়ার, ট্যাগ, লাইভ, অ্যাকাউন্ট, পেমেন্ট, রিচার্জ, হটলাইন |
| Events | রেজিস্ট্রেশন, ইভেন্ট, ক্যাম্পেইন |
| Everyday | টেনশন |

### 3.4 Bangladesh, not West Bengal

| Bangladesh | West Bengal | Bangladesh | West Bengal |
|---|---|---|---|
| পানি | জল | গোসল | স্নান |
| দাওয়াত | নিমন্ত্রণ / নেমন্তন্ন | নাস্তা | জলখাবার |
| লবণ | নুন | মরিচ | লঙ্কা |
| সেবা | পরিষেবা | ঈদ | ইদ |
| খালা | মাসি | ফুপু | পিসি |
| চাচা | কাকা | আপা / আপু | দিদি |
| ভাইয়া | দাদা (দাদা means grandfather in Bangladesh) | ভাবি | বউদি |
| দাদি / নানি | ঠাকুমা / দিদিমা | দোয়া | আশীর্বাদ |
| ৳ | ₹ | হলো, হতো | হল, হত |

- `copylint --locale BD` warns on the everyday words (জল, স্নান, নিমন্ত্রণ …) and adds a note on kinship words.
  Bangladeshi Hindu families use মাসি, পিসি, কাকা and জল, so choose for the audience. A Puja post uses পূজা and শারদীয়.
- Youth slang: Dhaka says জোস and প্যারা; Kolkata says হেবি and চাপ.

### 3.5 Address forms

- **আপনি:** fintech, banks, e-commerce, delivery, groceries, health, property, B2B, government and customer care
  (bKash, Nagad, Pathao, Daraz, Chaldal, Shwapno, Robi).
- **Telecom:** আপনি by default; তুমি for youth, student and gaming packs (Banglalink, GP).
- **তুমি:** snacks, soft drinks, streetwear, youth events, gaming, and school and college edtech.
- **তুই:** only inside quoted dialogue between friends, or in meme formats.
- **Pronoun-free lines** sidestep the choice: প্রথম অর্ডারে ডেলিভারি ফ্রি!
- **One form per piece.** `copylint` flags আপনি … করো.

| | আপনি | তুমি | তুই |
|---|---|---|---|
| do! | করুন | করো | কর |
| will do | করবেন | করবে | করবি |
| you get | পাচ্ছেন | পাচ্ছ | পাচ্ছিস |
| don't miss | মিস করবেন না | মিস কোরো না | মিস করিস না |
| your | আপনার | তোমার | তোর |

### 3.6 Punctuation, numbers, spelling

- **Sentence ends and marks:**
  - । ends a statement. "." is only for abbreviations (ড., লি.) and is checked.
  - One "!" per line, with no space before it. A hook or headline may end in one "!", as Bangladeshi hooks often
    do, and `copylint` accepts it. Two in a line, or more than two in a piece, get a warning.
  - Write a colon ":", never a visarga (ঃ) as a colon ("বিস্তারিতঃ" is a common error; checked).
  - Abbreviations with a visarga (মোঃ, ডাঃ, বিঃদ্রঃ, লিঃ) are common and not an error, so the lint gives only a
    note. The Bangla Academy style is মো., ডা., লি. (its spelling rulebook writes মো. and ড.): prefer it when the
    brand does.
- **Dashes:**
  - The NCTB textbook teaches the ড্যাশ, so it is real Bengali.
  - But Prothom Alo, Niropekho and Bigganchinta (2025) flag misused em dashes as the AI tell, and none of the latest
    posts on 12 Bangladeshi brand pages used one.
  - Rule: none on graphics and captions. Use a comma, a new sentence, a line break or "…".
- **Hyphens:** for compounds (লাল-সবুজ) and for case endings on numbers and Latin names (২০২৬-এর, Daraz-এ).
- **Digits:**
  - Bengali digits (০–৯) for prices, dates, times, percentages and counts.
  - Latin digits for USSD and promo codes, URLs and model names.
  - One digit script per piece otherwise.
- **Money:** ৳১৯৯ with no space, or ১৯৯ টাকা (টাকায়), which reads more natural in ads; never both in one piece.
  Print the price. "দাম জানতে ইনবক্স" annoys
  buyers, and Bangladesh's Digital Commerce Guideline 2021 (§3.1.2) asks for clear prices (checked).
- **Ranges and times:**
  - A plain hyphen for dates (২৩-৩০ সেপ্টেম্বর).
  - থেকে inside sentences.
  - "up to" is ৫০% পর্যন্ত ছাড়.
  - Times read সকাল ১০টা থেকে রাত ৯টা পর্যন্ত: the part of the day comes first, টা is attached, and there is no
    AM/PM.
- **Spelling, following the Bangla Academy (2012 rules):**
  - Non-tatsama words take only ি and ু: সরকারি, জানুয়ারি, ফ্রি (not ফ্রী).
  - শ্রেণি.
  - ঈদ: the Academy returned to ঈদ in March 2025.
  - কী for "what" or "how" (কী দারুণ!, কীভাবে); কি only in yes/no questions (তুমি কি যাবে?).
  - ও-কার: ভালো, মতো, কোনো, হলো (মত means "opinion").
  - কেন means "why"; কেনো means "buy!".
  - এখনই, আজই, আজও.
  - করি না but করিনি.
  - রং but রঙিন.
  - The common slips (ফ্রী, সরকারী, জানুয়ারী, শ্রেণী, এখনি) are checked.

### 3.7 Hooks, CTAs and captions that feel native

- **First line:**
  - the offer number or a relatable question, in 4 to 8 words (6 or fewer on a cover), often ending in one ! or ?;
  - or a place name, or a news verb (চলে এলো, থাকছে).
  - Never a greeting: প্রিয় গ্রাহক belongs in customer-care replies, not in captions (checked).
- **Formulas Bangladeshi brands use:**
  - [কাজ] করলেই [পুরস্কার];
  - মাত্র ৳…;
  - [কাজ] মানেই [ব্র্যান্ড];
  - two parallel or rhyming halves;
  - a pun on the brand name;
  - a question, then its answer;
  - a customer's quote in “ ”.
- **Humour** is light and daily: cravings, rain, traffic, load-shedding, exams.
- **Festivals** (Eid, Pohela Boishakh and Victory Day get the most interaction): a greeting, a one-line wish, then a
  soft offer. Solemn days follow `occasions.md`.
- **CTAs** (at most 6 words in Bengali, §1):
  - এখনই অর্ডার করুন;
  - অফারটি নিন;
  - আজই ঘুরে আসুন;
  - অর্ডার করতে ইনবক্স করুন;
  - ডায়াল করুন *…#.
  - লিংকে ক্লিক করুন and বিস্তারিত জানতে পড়ুন are the generic ones, like "Learn more": use them only when nothing
    more specific fits.
  - Put the detail into the ask: "ঝাল কতটা চান? ইনবক্সে লিখুন".
  - Never লাইক দিন, শেয়ার করুন সবাইকে or ট্যাগ করুন (bait, checked).
- **Emoji and hashtags:**
  - Bangladeshi brands often open the hook with an emoji (🔥 🛍 📢). That is local practice, so `copylint` accepts an
    emoji first for BD. How many follows the one emoji rule in §1.
  - 0 to 3 hashtags at the end, in Latin script or in Bengali with underscores (#খেলা_হবে_নগদে).

Lines in natural Bangladeshi Bengali (samples of the register; a native reader signs off real copy):
- ঈদের কেনাকাটা এবার ঘরে বসেই! ৳১,৫০০-এর বেশি অর্ডারে ডেলিভারি ফ্রি।
- বৃষ্টির দিনে খিচুড়ি না হলে চলে? আজ রাত ১০টা পর্যন্ত সব কম্বোতে ২০% ছাড়।
- অফিস থেকে ফিরে আবার রান্না? থাক, অর্ডার করুন, খাবার পৌঁছে যাবে ৩০ মিনিটে।
- অ্যাপে প্রথম পেমেন্টেই ৳৫০ ক্যাশব্যাক। অফার চলবে ৩০ সেপ্টেম্বর পর্যন্ত।
- নতুন আউটলেট এখন মিরপুর ১০-এ! উদ্বোধনের সপ্তাহে সব পণ্যে ১৫% ছাড়।
- পূজার নতুন কালেকশন চলে এসেছে। শোরুম খোলা সকাল ১০টা থেকে রাত ৯টা পর্যন্ত।
- দাম আর সাইজ ছবিতেই দেওয়া আছে, অর্ডার করতে ইনবক্স করুন।
- রেজিস্ট্রেশন চলছে! সিট সীমিত, ফি ৳৫০০। লিংক কমেন্টে।

Sources for §3:
- Wikipedia: Bengali language; Banglish
- the Bangla Academy's standard spelling rules (2012) and its 2025 notice on ঈদ
- Pabitra Sarkar, Inscript (2024), on West Bengal and Bangladesh spelling
- Sweet et al. (2025, arXiv 2512.13487)
- ULAB (2020), code-switching in ad posters
- Prothom Alo, Niropekho and Bigganchinta (2025) on AI-written Bengali
- The Daily Star Bangla on machine translation
- Bangla Tribune (2018) on FM radio language
- TBS (2023)
- 1idea (2025)
- the Tor Project's forum on Bengali address forms
- the latest public posts, 24 September 2026, of Aarong, Yellow, Pathao, Foodpanda BD, bKash, Grameenphone,
  Banglalink, Robi, Daraz, Nagad, Chaldal and Shwapno

## 4. Other languages: transcreate, never translate

The voice craft for these languages and six more (Nepali, Filipino, Korean, Thai, Vietnamese, and each variant) is in
`natural-text/references/languages.md`: the English moves calqued in every language, translated structure, the
spoken particles natural copy has, template lines, address and code-mixing, swaps and tells. `copylint --lang <code>`
runs each language's rules (Russian, Italian, Finnish and Hebrew have rules too).

1. **Start from the brief, not the English text.**
   - Say the intent, the audience, the feeling and the action.
   - List what is fixed: the brand, the claim, the price, the legal lines.
   - List what may change.
2. **Route by stakes.**
   - Translate specs and legal lines. Localise body copy.
   - Transcreate headlines, hooks and CTAs.
   - Write natively when the idea does not travel.
3. **Give options.** Two or three versions of each key line, each with a back-translation and one line of rationale.
4. **Target the locale, not the language.** Treat each as its own market: es-ES / es-MX / es-AR, pt-BR / pt-PT,
   zh-CN / zh-TW / zh-HK, id / ms, and Gulf / Egyptian / Maghrebi Arabic.
5. **Register first.**
   - Fix the address form, the dialect, the script and how much English mixes in, before drafting.
   - Keep them the same in posts, ads and replies.
6. **Keep the idea; swap the vehicle.**
   - Idioms, puns, references and proof get local equivalents.
   - Check names for local meanings. *Percuma* means "free" in Malay but "useless" in Indonesian.
7. **Review on the render,** not in a spreadsheet. Gender, line breaks and length only show there.
8. **Localise the formats:**
   - currency, number separators, dates, the clock and the digits;
   - currency signs the local way: $20 and £20 with no space (en-US, en-GB); 20 € with a no-break space (de, fr, es,
     it); ₹500 (India); ৳৫০০, or ৫০০ টাকা, which reads more natural in Bangladeshi ads (§3.6). `craft.md` §2 says
     the same;
   - German and French run up to 30 % longer, so re-compose the layout rather than shrink the type.
9. **Machine-translation tells:**
   - English word order and sentence length;
   - calques;
   - "you / your" in every line;
   - mixed or wrong formality;
   - textbook register on social media;
   - words from the wrong variant;
   - English punctuation;
   - lost wordplay.
10. **AI tells survive translation.** Watch for:
    - a calqued "not X, it's Y" (*No es solo X, es Y*);
    - triads and slogan fragments;
    - colon rhythm;
    - English Title Case in Spanish, French or Portuguese headlines.
11. **Dashes: no pause dash in any language, on a design or in a caption.**
    - No language is an exception: not the German spaced dash, the Spanish raya, the Portuguese travessão, the
      Chinese double dash (破折号) or the Japanese dash. In Brazil the travessão is now called a ChatGPT sign.
    - Russian uses a dash as grammar between two nouns (Москва [dash] столица). Rebuild the sentence instead: a verb
      (Кофе обжариваем каждую неделю), a colon, or two sentences.
    - Chinese and Japanese: a full-width colon (：), a comma (，in Chinese, 、in Japanese) or a new line.
    - Other languages: a comma, a colon, a full stop or brackets, as in English (§1).
    - Number ranges: a hyphen, "to" or the local word (Bengali ১০-১২ or ১০ থেকে ১২).

| Language | Register on social | Address | Locale notes | Punctuation |
|---|---|---|---|---|
| Hindi | Hinglish. Online, 58 % prefer Roman script (75 % of Gen Z); pure Hindi reads as official. | आप (कीजिए) by default; तुम (करो) only for youth brands; never switch | not pan-India; ₹1,00,000; nukta in loanwords (फ़्री) | । full stop, “ ” |
| Arabic | dialect for social, because MSA sounds stiff; Gulf, Egyptian and Maghrebi copy are separate | verbs are gendered, so use a plural (اطلبوا) or no verb, and match the picture | Maghreb uses Western digits; mirror the layout for RTL; bidi-isolate Latin text | ، ؛ ؟ and « » |
| Spanish | warm and direct | ES tú, vosotros; MX tú, ustedes; AR vos (*pedí*); CO usted in commerce | ordenador / computadora, móvil / celular | ¿ ¡ (checked); sentence case; commas or brackets for an aside, never the raya |
| Portuguese | BR informal and expressive; PT reserved | BR você; PT tu or no pronoun | frete (BR) / portes (PT); R$ 49,90 | “ ” BR, « » PT; never the travessão |
| French | vous by default; tu for youth, sport and fashion | one form everywhere | fr-CA: fin de semaine; 49,90 € (no-break space); 20 h | « » with narrow spaces; a narrow no-break space before ; ! ? (checked) |
| German | du on consumer social; Sie for finance, health and B2B | du in lowercase in ads | Switzerland: ss and « »; texts run about 30 % longer | „ “; no dash as a pause: a comma, a colon or a full stop |
| Indonesian / Malay | id casual (ya, yuk) with English mixed in; ms formal for corporate | id kamu (-mu), Anda for banks; ms anda | Rp 49.000 | “ ”; no dash as a pause |
| Urdu | Roman Urdu with English online; Urdu script for mass audiences | آپ (کریں) | fix one Roman spelling list per brand; Nastaliq, RTL | ۔ ، ؟ |
| Tamil | spoken Tamil or Tanglish on social; written Tamil reads like a notice | நீங்க (-ங்க) | Tamil Nadu, Sri Lanka, Singapore and Malaysia differ | . , “ ” |
| Chinese | short and platform-native | 你 for consumer brands; 您 for service and premium | zh-CN, zh-TW and zh-HK are separate versions; never auto-convert | full-width ，。！？ (checked); “ ” CN, 「」 TW and HK; no 破折号: ：，or a new line |
| Japanese | catch lines without keigo; body and CTA in です・ます | no あなた; ご注文, お届け | 1,980円; 9月24日(木) | 「」 、。 no spaces; 〜 for ranges; no dash as a pause: ：、or a new line |
| Turkish | natural idiom over literal accuracy | siz by default; sen for youth apps; never mix | casing i → İ (`lang="tr"`); 12'ye | “ ” |

A native reader signs off every language this skill cannot read itself.

## 5. Hooks

The rules:
- Put the topic in the first line or the first two seconds. On-screen text gets about one second.
- No greeting and no setup.
- A number, a name or a date beats an adjective. Give just enough: too vague and too literal both lose.
- Loss words pull more than positive ones (news headlines: +2.3 % CTR per negative word, −1.0 % per positive word).
- Statements beat questions in titles. Keep a question only when it is specific and speaks to the reader.
- In video, the picture, the spoken line and the on-screen text are three different hooks, and they never repeat each
  other.

Every example is 6 words or fewer, the most a cover carries (§8); thumbnail text is shorter still (below).

| Pattern | Example | Best fit |
|---|---|---|
| Specific result | "We cut onboarding to 3 days." | LinkedIn, carousel |
| Cost confession | "One missing clause cost me $18k." | Reels, LinkedIn |
| Mistakes | "5 pricing mistakes eating your margin" | carousel, YouTube |
| Curiosity gap, topic named | "The setting behind our 3x saves" | YouTube, Reels |
| Negative command | "Stop posting daily. Post twice." | LinkedIn, X |
| Unpopular opinion | "Your logo isn't the problem." | LinkedIn |
| Hyper-specific POV | "POV: 3 pm, coffee number four." | TikTok, Reels |
| Before / after | "March vs now. One change." | Reels, ads |
| Time collapse | "5-hour proposals now take 20 minutes." | Reels, ads |
| Proof first | "212 leads in 30 days." (the dashboard on the next frame) | ads, LinkedIn |
| List + favourite | "7 caption edits. Try number 4." | carousel |
| Callout | "Photographers under $2k, this is yours." | ads, feeds |
| Verbatim audience question | "'Why does posting feel awful?'" | Reels, stories |
| Head-to-head | "Carousels vs Reels, 90 days." | YouTube, LinkedIn |
| Experiment | "Daily Reels for 60 days. Results." | YouTube, TikTok |
| Insider truth | "Your first 30 Reels should flop." | Reels |

Patterns, not labels: the literal "Unpopular opinion:" label, "What nobody tells you about…" and the same pattern
opening most posts read as templates (the lint notes them; the ledger in §12 counts repeats). Use the pattern when
the post then gives something that really is little known or really disputed, and let the first line say it.
| Steal this | "Steal this four-line follow-up." | carousel, LinkedIn |
| Objection flip | "Camera-shy? Try the faceless version." | Reels, ads |
| Real deadline | "Grid crop changed today. Fix covers." | stories, X |
| Cold open | "…then the client wanted a refund." | TikTok, Reels |
| Surprising fact | "The motif isn't drawn on cloth." (Sutokotha: জামদানির নকশা কাপড়ে আঁকা হয় না) | carousel, post |
| Value promise | "Check your price in 30 seconds." | Reels ads |

Hooks by format:
- **Thumbnail text:**
  - 2–4 words that add what the title lacks, sharing no word with it (`copylint` compares `title` and `thumb`).
  - Legibility drops beyond 5–6 words.
- **Carousel cover:**
  - ≤ 6 words, legible at grid size, with an exact count when there is one.
  - Slide 2 is a second cover, because Instagram re-serves unswiped carousels from slide 2.
- **Story frame 1:**
  - a face or a hand doing something;
  - 3–7 frames, with the ask on frame 4;
  - text out of the top 14 % and the bottom 35 % in ads.
- **Caption line 1:**
  - the payoff, inside the fold (§7);
  - never a greeting or a hashtag first, and no emoji first except where that is local practice (Bangladesh, §3.7).
- **LinkedIn:** the first 140 characters carry the whole point (the mobile fold).

Write three hooks from three different patterns, then keep the one a stranger understands in two seconds.

## 6. Calls to action

1. Write the verb and what the reader gets: "Book a tasting". The qualifier (Saturday 10 am, the price, the
   deadline) goes on its own line beside the button, as the key fact (`craft.md` §4), so the button stays within the
   §1 limit.
   - Never "Submit", "Learn more" or "Click here".
2. Test first person ("Start my free trial"). Lower effort usually wins: in one test "Get started" beat "Book a
   demo". But "Get started" names no action, so it is the generic fallback, used only when nothing more specific
   fits. Prefer the specific low-effort ask: "Start my free trial", "See the menu".
3. One ask per piece:
   - on a carousel, the last slide;
   - on a story, frame 4;
   - in a video, the voice and the on-screen text together.
4. On Instagram, ask for saves or sends with a reason, never for likes.
   - A save CTA gave +92 % saves and a comment CTA +203 % comments.
   - Asking for likes lowered likes by 4.9 %.
   - The reason is the point: a bare "Save this for later." or "Thank me later" is a closer any post could carry,
     and the lint warns on it. "Save this for your next launch" is fine.
   - A closing question that fits any post ("What do you think?", "Thoughts?") gets a warning; ask the one question
     only this post can ask.
5. **No bait.** Meta demotes posts that ask for likes, shares, comments, tags or votes for their own sake: "tag a
   friend", "comment YES", "share if you agree", "comment 1, 2 or 3". A save or a send with a real reason (rule 4) is
   not bait, and asking for help, advice or recommendations is exempt.
6. **Urgency only when it is true,** stated as a fact: "30% off ends Sunday at midnight". Fake urgency is a dark
   pattern (FTC).
7. **No CTA** on mood or pure-reach pieces, on replies, and on sensitive posts.

The first five rows go on the design, within the §1 limit (4 words in Latin script, 6 in Bengali), with the time or
place on its own line beside them. The last three are caption asks, which need a reason and can run longer.

| Goal | English | Bangladeshi Bengali |
|---|---|---|
| Buy | Order yours | অর্ডার করুন · আজই অর্ডার করুন · ইনবক্সে অর্ডার করুন |
| Register | Save my seat | রেজিস্ট্রেশন করুন · আসন নিশ্চিত করুন |
| Visit | See the menu | চলে আসুন · দেখতে আসুন · ঘুরে যান |
| Watch | Watch part 2 | কমেন্টের লিংকে পুরোটা দেখুন |
| DM | Message us "menu" | "মেনু" লিখে ইনবক্স করুন |
| Save (caption) | Save this for your next launch | পরে কাজে লাগবে, সেভ করে রাখুন |
| Share (caption) | Send this to whoever runs your ads | যার কাজে লাগবে, তাকে পাঠিয়ে দিন |
| Comment (caption) | What would you fix first? | আপনি হলে কোনটা আগে ঠিক করতেন? |

## 7. Captions and platform limits

A caption goes in this order:
1. The hook, inside the fold.
2. Two to six short paragraphs, with blank lines between them.
3. One ask.
4. Hashtags, or none.

Aim for 5th–7th grade words. Pages written at that level convert at 11.1 %, against 5.3 % for professional-level copy.
Write search phrases as plain sentences, because Instagram search reads captions. End with one specific question to
get comments (+37 %).

| Platform | Before "more" | Hashtags | Emoji (the count follows §1) | Notes |
|---|---|---|---|---|
| Instagram | ~125 characters | 0–3, capped at 5 since December 2025 | light | carousels take 20 items, 4:5; the grid is portrait |
| Facebook | ~80 characters | 0–2 | light | predicts scroll-past; demotes bait and reposts |
| LinkedIn | ~140 mobile, ~210 desktop | 0–3, at the end | light | posts of 1,301–2,500 characters get more engagement; document posts lead engagement |
| YouTube | title ≈ 60 characters visible (≈ 40 on mobile home) | 1–3 | sparing | title, thumbnail and the first 30 s work as one package |
| TikTok | ~90 characters | 3–5, capped at 5 | the most at home here, still within §1 | 90 % of ad recall forms in the first 6 s |
| X / Threads | 280 / 500 characters | 0–1 / 1 topic tag | minimal | X bans hashtags in ads |

Alt text:
- Describe the scene, then repeat any text on the image word for word.
- Limits: X 1,000 characters, LinkedIn 1,000, TikTok 300.
- Every carousel slide gets its own alt text.

`copylint --platform` checks:
- the fold (the length of the first line);
- the hashtag count and cap;
- emoji and emoji bullets;
- greeting openers;
- bait;
- the length X counts (a link is 23 characters, an emoji 2, CJK 2: over 280 is an error) and Threads' 500;
- SMS parts (160 characters a part in plain Latin text, 70 with Bengali or an emoji);
- markdown (**bold**, [text](link), # headings) that feeds show as raw symbols; WhatsApp, email and web are exempt;
- "link in bio" on X, LinkedIn, Facebook and Threads, where the post can carry the link;
- thread numbering (1/, 🧵) on Instagram, LinkedIn and Facebook.
Replies (`--role reply`) skip the fold and greeting checks (a reply opens with the person's name) and get a note when
four or more sentences arrive as one block. Even rhythm is not noted on X and Threads, where short even posts do well.

## 8. Attention and vibe on the design

- **Design for a glance.**
  - People recall feed content after 0.25 s, and mobile attention averages about 1.7 s.
  - Use one focal point, at most three type sizes, and let only the headline, the subject and the CTA survive the
    squint test.
- **Faces help in some niches and not in others.**
  - 69 % of breakout thumbnails had a face filling ¼ to ⅓ of the frame, but across 300k videos faces were neutral
    overall.
  - A face looking at the product pulls the eye to it.
- **On-image text:** ≤ 6 words on covers and thumbnails. Detail goes in the caption.
- **Native beats polished.**
  - Instagram's head calls the polished feed dead.
  - Native, creator-style Reels ads cost 5 % less per result and convert 11 % better.
  - Choose candid photos and real places (`craft.md` §6, codex-imagegen's natural look).
- **Social vibe is local.** Use the market's references, humour, festivals, weather and slang, never a generic global
  "lifestyle".

## 9. The copy loop: write, lint, rate, fix

1. **Voice first.**
   - Fix the voice in three words it is, and three it is not.
   - Choose the address form: আপনি / তুমি; tú / usted; du / Sie.
   - Pick the loanword policy for the market.
2. **Write three hooks, then choose one.**
   - Write three options, each from a different pattern (§5).
   - Keep the one a stranger understands in two seconds and would stop for.
3. **Write the deck in `copy.json`** (role, text), in reading order, with the caption as a `caption` role.
   - Give the key fact (the time, the deadline, the price, the qualifying purchase) its own entry with
     `"role": "key_fact"`. Never a role name with "action" or "cta" in it: the lint reads those as the call to action
     and applies the CTA word limit.
4. **`copylint --copy copy.json --locale BD --platform instagram`**
   - Zero errors: no em dash, no pause dash, no chatbot leftover, no post over the platform's limit.
   - Fix the warnings, or keep one with a stated reason (the client's own wording, a legal phrase, a fixed term).
   - Give the language when it is not in the copy.json `lang` field: `--lang es`, `--lang zh-TW`, `--lang pt-PT`. An
     untagged line is read by its script, and a Latin line by its small words (English when unsure). The market
     (`--locale PT`, or the region in `--lang`) switches on the rules that are only for it: Brazilian words in a
     Portugal post, mainland words in a Taiwan post, Spain's vosotros in Latin America, standard Arabic in an
     Egyptian or Levantine post.
   - `--caption` takes `--role` too: caption (the default), body, reply, script or voiceover (checked for the ear),
     alt (alt text: never how the image was made). `--platform` also takes whatsapp, email, web, sms and voiceover.
   - In a long caption, fix every error and every cluster; a single note is a question to ask, not a verdict (zero
     tolerance rejected 31 % of human documents in one project's test).
5. **`copyjudge --copy copy.json --brief brief.md --locale BD --platform instagram --goal register`**
   - A fresh Codex session reads the deck as the named reader.
   - It scores ten criteria, gives a natural rating for every string and a rewrite, up to three stronger hooks and the
     best call to action.
   - The verdict:
     - **FAIL**: any lint error, naturalness ≤ 2, heavy AI tells, or a string rated ≤ 1.
     - **REVISE**: weighted < 3.6, any criterion ≤ 2, or naturalness or hook below 3.
     - **PASS**: weighted ≥ 3.6.
     - **PASS_NATIVE**: weighted ≥ 4.3 with naturalness, locale and hook ≥ 4. This is the target for client and hero
       work.
   - **The judge varies from run to run.** Read one score as a range, not a point:
     - Drafts: one run. A difference under 0.2 between two versions is noise, not progress.
     - Client and hero work: `--runs 3`. The tool takes the median of each criterion and recomputes the verdict from
       the medians.
     - When the runs disagree on the verdict, or the median sits within 0.10 of 3.6 or 4.3, go to five runs
       (`--runs 5`) and use their median. The report lists each run and the spread, and its `advice` says when.
     - Pool the suggested hooks and rewrites from every run before choosing.
   - The judge scores fidelity to the brief before how human a line sounds: blind judges reward invented
     experience ("we tasted it at dawn"), so an invented detail is a defect, not a strength. It does not reward
     length.
   - Its rewrites, hooks and call to action come back linted (`rewrite_lint`, `hooks_lint`, `cta_lint`): a rewrite
     can bring new tells while removing old ones.
   - The judge is a different model family from the writer (Codex reads what Claude wrote), which avoids a judge
     preferring its own family's style (Panickssery et al., NeurIPS 2024).
6. **Take the rewrites that are better, not all of them,** from whichever run offered them. The judge can be wrong
   about local usage.
   - Run a deletion test on every word a rewrite adds (does the line lose anything without it?) and a reversion test
     on every word it replaces (was the original word already right?).
   - Example: it called অধরা সাংস্কৃতিক ঐতিহ্য a translation tell, but it is the standard Bangladeshi term for
     UNESCO's Intangible Cultural Heritage (bn.wikipedia, the Bangladesh UNESCO National Commission).
   - Check a judge's rewrite of a disputed local term against a local source: a national newspaper, a government
     site or the local Wikipedia.
   - For social copy, still prefer the plainer phrase (ইউনেস্কোর স্বীকৃতি).
7. **Design with the approved deck** (`--copy`; add `--locale BD` for Bangladeshi copy). The render checks catch any
   dash or wording that slipped in later.
8. **A native reader has the last word on non-Latin copy.** Neither the lint nor any number of judge runs replaces
   them.

Measured on 24 September 2026. All copy is Bengali; the Tokjhal designs were judged by `judge`.

| Piece | Before | After | What changed |
|---|---|---|---|
| Sutokotha carousel | FAIL 3.46 | **PASS_NATIVE 4.55** | the cover "একটি জামদানি যেভাবে জন্মায়" became "জামদানির নকশা কাপড়ে আঁকা হয় না"; "হাতে হাতে বোনা" became "হাতে বোনা হয়"; range dashes became ১০-১২; hook 3 → 5, locale 3 → 5, AI tells 3 → 5 |
| Sutokotha story | FAIL 4.0 | PASS 4.26 | the spaced en dash between সকাল ১১টা and রাত ৮টা became থেকে; বিক্রয় became বিক্রি; "প্রবেশ বিনামূল্যে" became "বিনামূল্যে দেখতে আসুন"; CTA 2 → 3 |
| Tokjhal post and caption | PASS 4.01 | PASS 4.29, then 4.25 with hook 4 on the forecast version | the filler "আজকের সন্ধ্যা এমনই হোক" was cut; "কম, মাঝারি না ডাবল" became "…না বেশি"; the price names the product |
| Tokjhal story | PASS 3.9 | PASS 4.46 | see the note below the table |
| Tokjhal post design | REVISE 3.45 (originality 2) | PASS 3.85 | the awning, card and photo template gave way to a weather-widget idea, "ঢাকা · আজ সন্ধ্যা / ১০০% / ফুচকার সম্ভাবনা" |

On the Tokjhal story, the plain question "ফুচকা খাবেন?" fell to REVISE (hook 2, emotion 2). Putting the rain back in, as
"বৃষ্টির সন্ধ্যায় ফুচকা খাবেন?", gave the best score of the run.

Lessons:
- **Context carries a hook.** Cut the moment (the rain) and the emotion goes with it.
- **An offer-first hook helps an order goal.**
- **A layout that would fit any competitor loses on originality even with good copy.** The swap-the-logo test applies
  to layouts too.
- **The blind pairwise between the two Tokjhal posts was a tie with a strong position bias** (the first image won 0 of
  4 votes). When the judges split, run both variants live and let the platform decide (§12).

## 10. Frameworks, one line each

- **AIDA:** a full ad or carousel arc: attention, interest, desire, action.
- **PAS:** problem, agitate, solve. For short ads and captions aimed at people who already feel the pain.
- **BAB:** before, after, bridge. For transformation posts and before/after graphics.
- **4U:** useful, urgent, unique, ultra-specific. Score every headline and cover against it.
- **FAB:** feature, advantage, benefit. For product cards and bullets.
- **"So what?" three times:** the third answer is the benefit to lead with.
- **Rule of One:** one idea, emotion, story, benefit and response per piece.
- **Specificity over superlatives** (Claude Hopkins): named details beat claims.
- **Voice of customer:** lift phrases from the client's reviews, comments and DMs. One mined headline got 400 % more
  clicks.
- **ABCD (video):** attract, brand, connect, direct.
- **The four hook killers:** delay, confusion, irrelevance, disinterest. Audit every opener against them.

## 11. Brand voice in `brand.json`

Voice is constant; tone shifts with the context. Build the voice from 5–20 real posts and replies by the client; real
posts outrank website copy. When they split into two voices, say so; never average them into mush.

```json
"voice": {
  "is": ["warm", "patient", "exact"], "is_not": ["hype", "sentimental", "exclamation marks"],
  "axes": {"formal_casual": 3, "serious_playful": 2, "plain_poetic": 3, "reserved_bold": 2},
  "address": {"bn-BD": "আপনি", "en": "you", "es-MX": "tú"},
  "code_mixing": "bn-BD: the English words people really use, in Bengali script (অর্ডার, ডেলিভারি, অফার)",
  "numerals": "Bengali digits in Bengali copy",
  "avoid": ["premium", "luxury", "প্রিয় গ্রাহক"],
  "prefer": {"বিক্রি": "বিক্রয়", "হাতে বোনা": "হস্তনির্মিত"},
  "keep": ["হাতের ছোঁয়া, সুতোর কথা"],
  "we_always": ["name the weaver", "give the price in taka"],
  "we_never": ["fake urgency", "poverty talk"],
  "tone": {"launch": "confident, specific", "festival": "warm, short", "solemn": "quiet, no selling",
           "reply": "helpful, first name"}
}
```

`copylint --brand brand.json` flags every `avoid` word and every word that has a `prefer` alternative, and never
flags a `keep` line: the brand's own tagline, catchphrase or slang (জোস, if the brand really talks that way) that a
rewrite must not "correct". The judge reads the voice from the brief.

## 12. Variants, series and the copy ledger

- **A/B variants:**
  - Each variant tests one hypothesis and changes one variable: the hook pattern, the CTA, the image or the offer.
  - Name them after what changed: `post-hook-cost`, `post-hook-result`.
  - Use `pairwise` to choose before launch. Once live, the platform's results outrank any judge's vote. YouTube's
    Test & Compare runs 3 thumbnails and picks on watch-time share.
- **Content pillars:**
  - Set 3–5 per client, for example craft, people, product, offers and community.
  - Each post carries one pillar and one real claim.
  - Adapt the format to each platform; never post identical copy everywhere.
- **Series:**
  - A series has a fixed name, a fixed layout and a fixed slot for what changes.
  - The hook and the CTA still change every time.
- **Copy ledger:**
  - `design.py ledger` keeps each client's designs with their hook, CTA and composition device (`deliver --ledger`
    adds a finished design; flags in `cli.md`).
  - It warns when a new hook is close to one of the client's last 12 and notes a CTA line used in the last three
    pieces.
  - Never reuse a hook pattern twice in a row, and vary the CTA line from post to post.
- **Trends:** check the format, the audio and the meme on the day of the job, and write down four things: fit with
  the brand, rights, expiry, and no link to a tragedy.

## 13. Accessibility

- **Alt text on every image and every carousel slide:** the scene, then the on-image text word for word. Decorative
  images get an empty alt.
- **No 𝗯𝗼𝗹𝗱 Unicode letters** in captions or names. `copylint` flags them.
- **Video:** captions and subtitles, and CTAs that are both said and shown.
- **Contrast:** measured on real pixels (`checks`). Text sizes for dense scripts follow `fonts.md` §3.
- **Hashtags:** CamelCase for multi-word tags (#DhakaStreetFood), so screen readers can say them.

## Sources

The research notes behind this file are in `references/research/` (`copy-ai-tells.md`, `copy-hooks-ctas-platforms.md`,
`copy-transcreation.md`; the folder's README lists them all).

**AI tells:**
- Wikipedia: Signs of AI writing
- Freeburg 2026 (arXiv 2603.27006, em-dash rates)
- Kobak 2024 (arXiv 2406.07016)
- Reinhart 2024 (arXiv 2410.16107)
- Russell 2025 (arXiv 2501.15654)
- The Washington Post on ChatGPT's tells (2025)
- TechCrunch on OpenAI's em-dash fix (2025)
- McGill OSS on LLM dashes
- repos: blader/humanizer, hardikpandya/stop-slop, petergyang/no-ai-slop, theclaymethod/unslop (MIT),
  ItsssssJack/SlopMonster, sam-paech/antislop-sampler, jalaalrd/anti-ai-slop-writing

**Hooks, CTAs and platforms:**
- Instagram and Meta:
  - Instagram ranking explained
  - Instagram's hashtag limit (Social Media Today, December 2025)
  - Meta's content-distribution guidelines on engagement bait
  - Meta ads guides
- LinkedIn Engineering on dwell time
- Buffer on the LinkedIn algorithm
- YouTube Help (thumbnails, hashtags, Test & Compare)
- vidIQ on thumbnails
- Search Engine Journal on faces in thumbnails
- Metricool Instagram study 2026
- Hootsuite on post lengths
- AuthoredUp on LinkedIn's limit
- Socialinsider benchmarks
- Unbounce on CTAs and its conversion benchmark
- The FTC's "Bringing Dark Patterns to Light"
- NN/g on visual hierarchy
- WCAG 2.2 on contrast
- Stanford GSB on question titles
- repos: coreyhaines31/marketingskills, Jakeschincariol/instagram-agent-skill, artemnovitckii/content-skills

**Transcreation:**
- Smartling, Phrase, Translated (Arabic dialects), GTE Localize
- arXiv 2503.04369
- Milestone Localization on Hinglish
- Dawn on Roman Urdu
- Ulatus on Spanish
- Duden (du/Sie)
- CNN Brasil on the travessão
- MQM error typology
