# Bangla and Banglish for Bangladesh: মুখের ভাষা, not বইয়ের ভাষা

How Bangladeshi brands and readers really write in 2024 to 2026, and how to write like them: casual, easy words,
চলিত as people speak it, the English words they really mix in. Never বইয়ের ভাষা, কবিতার ভাষা, সাধু ভাষা, a stiff
"শুদ্ধ" notice register, or a machine translation.

Research of 24 September 2026 (`~/.claude/skills/codex-design/references/research/voice-bangla.md`), measured on:
580 Bengali YouTube titles of 15 brands, 144 active 2026 Meta ads of 8 big brands, 1,457 other Bangladeshi ads,
Prothom Alo headline counts for about 200 words, and 3,322 Bangla news and textbook passages each paired with a
ChatGPT paraphrase (the only direct measure of AI Bangla). The base rules (formal to everyday, calques, Bangladesh
and West Bengal words, address forms, spelling, digits) stay in `codex-design/references/copy.md` §3; this file adds
what the new research found.

## 1. How Bangladeshi brands really write

**Big-brand copy is plain and factual.** Median sentence 9 words (p90 20) across 431 sentences of brand ads. The
casual feel comes from the emphatic -ই (in 58 % of ads: আজই, সহজেই, ঘরে বসেই, আছেই) and the inclusive -ও (35 %:
আপনিও, নেটও চলবে), not from particles. তো, কিন্তু, নাকি, একটু, তাই না together appear in 10 of 144 ads and never
more than two in one text; reaction words (উফ, আহা, ইশ) in 1 of 580 titles and 0 ads.

Fix a flat Bengali line with -ই, -ও, a question or a verb-first order far more often than with a particle. Particles
are seasoning.

Shapes that recur:

| Shape | Example |
|---|---|
| Question hook, then the answer | বাসার বিল দিতে বাইরে কেন যাবেন? (Nagad, 2026) |
| Rhetorical exclamation with a particle | কেনাকাটায় অফার পেতে কার না ভালো লাগে! (bKash, 2026) |
| X তো আছেই | ডায়াপার শেষ? চিন্তা কিসের, চালডাল তো আছেই! (Chaldal, 2025) |
| X মানেই Y | পেমেন্ট মানেই বিকাশ; উৎসব মানেই স্টাইল (Prothom Alo headlines use মানেই 429 times) |
| [কাজ] করলেই [পুরস্কার] | অ্যাপে বিল দিলেই ৳২০ ক্যাশব্যাক |
| Verb or news verb first | থাকছে, চলছে, চলে এলো, আসছে |
| Two rhyming halves | festive and contest copy |
| Wordplay on one word | Nagad set বিরতি against অবিরাম; GP asked why Wi-Fi needs a তার |
| An everyday observation leading to a fact | কিছু জিনিস মনে রাখতে হয় না, এমনিতেই মনে থেকে যায়। (GP) |
| Humour from family and daily life | দুলাভাই buying on credit; ড্রাইভার গায়েব? (kin and small annoyances, never mockery) |

English inside Bengali:
- Loanwords go in Bengali script: নো টেনশন, টেনশন ফ্রি, লাইফ আরেকটু ইজি, এক্সপেরিয়েন্স, জার্নি, আনলক করুন.
- Latin-script English words inside a Bengali sentence are a youth and telecom habit (Safe থাকি, Safe রাখি;
  ব্যালেন্স gone?); fintech, grocery and retail stay in Bengali script. Brand, app and product names, codes and URLs
  stay Latin.
- What readers object to is **needless** English, not loanwords.

How casual they get, and where they stop:
- One slang word per line at most (প্যারাহীন, ফাটাফাটি, চিল).
- The colloquial আপনি imperative is as far as big brands go: "আসেন বুঝাই, কারণ বুঝলে সোজা!" (bKash);
  "থাকেন নিশ্চিন্তে" (Pathao Courier).
- Dhaka phonetic spellings (করতেসি, খাইসি) appear in 0 of 2,181 ad texts and titles.
- Fraud warnings, health and safety drop the casual register completely: standard, formal আপনি.
- Poetic language is kept for festival greetings and brand films; offer posts from the same brands stay plain.

## 2. The register ladder

| Rung | Forms | Who, and when |
|---|---|---|
| তুই-chat | তুই, তোর; কর, খা; করিস | never to address a customer; only inside quoted dialogue between friends, memes, drama promos, or a brand talking to a thing (ভাগ ব্যাকটেরিয়া ভাগ) |
| তুমি-casual | তুমি, তোমার; করো, নাও, জানাও | school and college students, youth contests and slogans, some food delivery lines |
| আপনি-warm (the default) | আপনি with colloquial forms: আসেন, থাকেন, দেখেন; question hooks, -ই, one particle | explainers, reminders and offers from fintech, telecom, delivery and retail |
| আপনি-formal | আপনি with -ুন imperatives, full standard verbs, no slang | fraud and security alerts, health, loans, insurance, terms, service notices |
| Pronoun-free | থাকছে ২০% ছাড়, এক ক্লিকে বাজার শেষ | the commonest shape in titles; it sidesteps the choice |

Rules: one rung per piece; never আপনি with a তুমি verb (the lint checks it); within আপনি, keep the -েন and -ুন
imperatives apart; models overuse আপনি where তুমি or তুই is natural in dialogue, and switch between them inside one
text: the judge watches both.

## 3. Poetic and literary words: the stack is the tell

Each literary praise word alone is ordinary written Bangla: Prothom Alo headlines use নান্দনিক 180 times, মুগ্ধতা
136, অপরূপ 79. But two or more in one line appear in 0 of 724 big-brand texts, and often in generated and puffery
copy (small fashion pages, resorts, food shops). So the lint flags the stack, not the word: two or more in a line,
three in a caption (`bn-poetic`).

The stack words: অপরূপ, মনোমুগ্ধকর, মনোরম, নয়নাভিরাম, নান্দনিক, অনবদ্য, অনন্য, অসামান্য, অভূতপূর্ব,
অবিস্মরণীয়, অপার, অফুরন্ত, অবারিত, অনাবিল, স্নিগ্ধ, মাধুর্য, মুগ্ধতা, শিহরণ, চিরন্তন, কালজয়ী, আভিজাত্য,
রাজকীয়, স্বর্গীয়, জাদুকরী, মোহনীয়, মায়াবী, প্রশান্তি, মেলবন্ধন.

Flagged on sight: স্বপ্নের ডানায় (no brand uses it), হৃদয়ের গভীর থেকে (the stock opener of generated greetings).
Noted: হৃদয় বা মন ছুঁয়ে যাবে (the promise form), রাঙিয়ে দিন or তুলুন as a call to action.

Not flagged, because real brands and the newspaper use them: ছুঁয়ে যাক, ডানা মেলে, রোমাঞ্চকর, কোমলতা, সমাহার,
এক ছাদের নিচে, হাতের মুঠোয়, স্বপ্নের ঠিকানা (real estate), নতুন দিগন্ত, নতুন অধ্যায়, ভালোবাসার ছোঁয়া.

The test from `SKILL.md` holds: could a reader check, taste or count it? "মনোমুগ্ধকর নকশা আর স্নিগ্ধ রঙের অপরূপ
মেলবন্ধন" becomes "হাতে বোনা জামদানি, একেকটা শাড়ি বুনতে লাগে তিন মাস।"

## 4. Stock AI Bangla phrases and measured AI habits

| Pattern | Example | Level |
|---|---|---|
| "In today's busy world" opener | আজকের এই ব্যস্ত জীবনে..., দ্রুতগতির এই পৃথিবীতে... | warning |
| উত্তেজিত for "excited" (in Bangladesh it means agitated: উত্তেজিত জনতা) | আমরা ভীষণ উত্তেজিত... | warning |
| The announcement formula | আনন্দের সাথে জানাচ্ছি | warning |
| "You deserve it" | সেরাটাই আপনার প্রাপ্য, ...ডিজার্ভ করে | warning |
| Essay closers and report verbs | উপসংহারে বলা যায়, পরিশেষে বলা যায়, পরিলক্ষিত হয় | warning |
| "We are proud or thrilled" | আমরা গর্বিত, আমরা আনন্দিত | note |
| "Welcome to the world of X" | খাবারের জগতে স্বাগতম (ফুডপ্যান্ডায় স্বাগতম is fine) | note |
| Essay importance | অপরিহার্য অংশ, গুরুত্বপূর্ণ ভূমিকা পালন করে | note |
| English order "make X more Y" | ...কে করে তুলুন আরও সুন্দর | note |
| "In every bite, sip, drop" | প্রতিটি কামড়ে, চুমুকে, ফোঁটায় | note |
| "Next level", "unlock a world of" | নিয়ে যান নেক্সট লেভেলে; আনলক করুন... দুনিয়া | note (Robi writes them, so never a warning) |
| Coaching cliches | স্বপ্নকে বাস্তবে রূপ দিন, সাফল্যের চাবিকাঠি | note |
| "Feel", "treat yourself", "we believe" | অনুভব করুন, নিজেকে দিন, আমরা বিশ্বাস করি | note |
| "An amazing experience" | অসাধারণ অভিজ্ঞতা, অনবদ্য অভিজ্ঞতা | note |
| Numbered scaffolding | প্রথমত... দ্বিতীয়ত | note |

Measured on 3,322 human passages against their ChatGPT paraphrases (formal prose, so these are translation habits):

| Marker | ChatGPT against human | What people write |
|---|---|---|
| এবং | 3.9 times as often; ও and আর 0.4 times | আর, ও, a comma (brand titles use ও five times as often as এবং) |
| এটি | 5 times | এটা (Prothom Alo headlines: 1,142 to 382), the noun again, or nothing |
| দ্বারা | 12.6 times | দিয়ে, or the active voice |
| কোনও | 10.6 times | কোনো (Prothom Alo: 4,641 to 2) |
| গিয়েছে | 9 times | গেছে (Prothom Alo: 4,867 to 2) |
| বলেছেন যে | 58 against 0 | বলেছেন, then the quote |
| X করতে সাহায্য করে | 6.4 times | say the effect |

On news prose, the new rules fire six times as often on the machine text as on the human text; on 102 hold-out ads of
five more brands they raised no warning.

## 5. Formal to everyday: new swaps

| Formal | Everyday | Level |
|---|---|---|
| উপলব্ধি করুন | বুঝবেন, টের পাবেন | warning |
| ভোজন করুন | খান, খেয়ে দেখুন (ভোজনরসিক is fine) | warning |
| উপস্থিত হোন | চলে আসুন | warning |
| অবস্থান করুন | থাকুন | warning |
| নিম্নোক্ত | নিচের | warning |
| সত্বর | তাড়াতাড়ি, শিগগির | warning |
| তথাপি | তবুও | warning |
| অত্র | এই | warning |
| আরম্ভ | শুরু (শুভারম্ভ is fine) | warning |
| গৃহ, গৃহে | ঘর, বাসা, বাড়ি (গৃহসজ্জা, গৃহিণী are fine) | warning |
| তৈরিকৃত, -কৃত on English loans (ডিজাইনকৃত) | তৈরি, ডিজাইন করা | warning |
| উপকৃত হোন | (say the benefit) | warning |
| বাহিরে | বাইরে | note |
| বাছাইকৃত | বাছাই করা | note |
| লাভ করুন | পান, পেয়ে যান | note |
| হালনাগাদ | আপডেট | note |
| আহার | খাবার | note |
| টাকার ঊর্ধ্বে | টাকার বেশি | note |
| প্রতিবছরের ন্যায় | প্রতিবছরের মতো | note |
| গ্রহণ করে, করতে, করলে | নিয়ে, নিতে, নিলে | note |
| অত্যাবশ্যক | খুব দরকারি | note |

Keep (brands and the newspaper use them): উপভোগ করুন once in a piece and never as the call to action (Nagad, Robi,
Banglalink, GP use it), তাহলে আর দেরি কেন and দেরি না করে (stale but human: the judge decides), জার্নি, শুধুমাত্র,
সাথে, আরো, নো টেনশন, হাতের মুঠোয়, মানেই, তো আছেই, অর্থাৎ, কেবল, দিবেন and নিবেন (everyday F-commerce), সাশ্রয়
করুন, পান করুন (Pureit), নিকটস্থ, অর্জন করুন, প্রচেষ্টা, প্রত্যাশা, অধিক, কর্তৃক in a legal claim, খ্যাত (famous).

## 6. Sadhu forms

The lint already flags the common sadhu stems. The research added: every sadhu perfect in -িয়াছ or -ইয়াছ (দেখিয়াছেন,
খাইয়াছি); the sadhu continuous -িতেছ (চলিতেছে; দিতেছি and নিতেছি are Dhaka speech and জিতেছে is চলিত, so they
pass); কেহ, কাহার, কাহাকে; বলিল, কহিল, এক্ষণে; যদ্যপি, নচেৎ, কিঞ্চিৎ, কুত্রাপি. Do not flag দিবেন, নিবেন, দিয়েন:
they are Bangladeshi colloquial, not sadhu.

## 7. Dhaka speech and slang

- **Works:** quoted dialogue, memes, a youth brand that talks this way, one word per line. Even Prothom Alo runs slang
  in lifestyle headlines.
- **Looks fake:** in fintech, banks, health and notices; three or more slang words in a line (`bn-slang-pile`);
  Dhaka phonetic spelling next to formal honorifics (সম্মানিত গ্রাহক... করতেসেন).
- **Never:** ক্ষ্যাত (mocks rural and poorer people), আবাল, ফকিন্নি.
- **Kolkata forms in Bangladeshi copy:** হেব্বি (Dhaka says জোস), চাপ নিও না (Dhaka: টেনশন নিয়ো না, প্যারা নাই).
- **What the words mean in reviews:** জোস, অস্থির, ফাটাফাটি are praise; পুরাই (often before ফালতু) and হুদাই lean
  negative. House spelling: জোস.
- One viewer called a telecom's slang-stuffed ad "REALLY cringe": one word lands, a pile does not.
- English Gen Z slang (rizz, bruh, skibidi) inside Bengali copy reads as trying too hard (`bn-genz`).

## 8. Banglish (romanised Bangla)

- **Where it lives:** comments, forums and reviews (13 % of 205,660 Daraz reviews; seller replies only 2.6 %). The
  buyer's stock question is "Price koto?".
- **Brands use it for names, songs and hashtags,** beside Bengali script: "Shopno Jabe Bari", #ParbeTumio,
  "Khela hobe". The offer itself stays in Bengali script; 0 of 182 brand titles with a price wrote it in Banglish.
- **Never** for headlines, prices, terms, official notices or broadcast (a 2012 High Court order; a 2018 instruction
  to FM stations). It also hurts findability: Banglish users got the worst recommendations on Daraz.
- **Replying in Banglish** to someone who wrote that way: the majority spellings (valo, vai, kichu, ache, hoise, onek,
  na, ki, nai, plz), "inbox" rather than DM, and never a price or condition only in Banglish.
- The lint notes Banglish in a Latin line and warns in a headline, call to action, price or terms (`banglish`).

## 9. Spelling and punctuation slips seen in 2026 brand copy

নিশ্চই for নিশ্চয়ই; দারুন for দারুণ; মুহুর্ত for মুহূর্ত; প্রানবন্ত for প্রাণবন্ত; -ী on loans (ডেলিভারী,
গ্যারান্টী, দেরী, তৈরী); the character ৷ (a currency sign) used as the দাঁড়ি; a space before । or none after it;
greeting openers such as প্রিয় শিক্ষার্থীরা that cost the fold. Normalise Bengali text to NFC before any word check
(য় and ড় have two encodings).

## 10. What readers and researchers say

- AI Bangla is "mechanical" and easy to spot (a Dhaka University Bangla professor, 2026); chatbots fall back on 10
  to 20 response patterns and push English sentence structure onto Bangla.
- The tells readers name: literal idioms, English sentence order, needless English words, the long dash, stock
  phrases (পরিলক্ষিত হয়, উপসংহারে বলা যায়), numbered scaffolding, too much আপনি, আপনি and তুমি mixed.
- What reads natural to them: plain সহজ-সরল words, everyday mixing, pronouns that fit the relationship, real idioms,
  personal experience and a recognisable voice.
- After the 2026 election's flood of AI "ordinary people", fake vox pops and staged customers cost trust fast. Use
  only real, approved voices.

## 11. Lines to calibrate your ear

Natural (written in the register of Bangladeshi brands; not quotes):
- বৃষ্টি নামলেই খিচুড়ির কথা মনে পড়ে? আজ রাত ১১টা পর্যন্ত খিচুড়ি কম্বো ৳২৪৯।
- মাসের শেষে টাকা টানাটানি? অ্যাপে বিল দিলেই ৳২০ ক্যাশব্যাক।
- অফিস থেকে ফিরে রান্নার মুড নেই? থাক, আজ আমরাই রাঁধছি।
- ইলিশের মৌসুম কিন্তু শেষের দিকে, পদ্মার ইলিশ কেজি ১,৪৫০ টাকা।
- সাইজ নিয়ে টেনশন নেই, না মিললে ৭ দিনের মধ্যে বদলে নিন।
- ঝাল কতটা চান? অর্ডারের সময় নোটে লিখে দিন।
- লোডশেডিংয়েও ওয়াইফাই চলবে, রাউটারে ৪ ঘণ্টার ব্যাকআপ।
- মা বলেন, বাজারে পচা টমেটো গছিয়ে দেয়। আমরা প্রতিটা টমেটো হাতে বেছে পাঠাই।
- ফ্রিল্যান্সিং শিখতে চাও? প্রথম ক্লাসটা ফ্রি, বসে দেখো তারপর ঠিক করো।
- আসেন বুঝাই, ক্রেডিট কার্ডের বিল না দিলে সুদ কীভাবে বাড়ে।
- অফারটা কিন্তু রবিবার রাত ১২টায় শেষ, পরে বললে পাব না!

Robotic (poetic, translated, bookish, sadhu, forced casual, Banglish):
- স্বপ্নের ডানায় ভর করে আপনার প্রতিটি মুহূর্ত হয়ে উঠুক অনন্য ও অবিস্মরণীয়।
- মনোমুগ্ধকর নকশা আর স্নিগ্ধ রঙের অপরূপ মেলবন্ধনে তৈরি আমাদের নতুন কালেকশন।
- আজকের এই ব্যস্ত জীবনে সুস্থ থাকা সবার জন্যই জরুরি।
- আমরা আনন্দের সাথে জানাচ্ছি যে আমাদের নতুন শাখা চালু হতে যাচ্ছে।
- এটি শুধুমাত্র একটি ব্যাগ নয়, এটি আপনার ব্যক্তিত্বের প্রতিচ্ছবি।
- অদ্যই আপনার নিকটস্থ শাখায় উপস্থিত হোন।
- পণ্য হাতে পাইয়া মূল্য পরিশোধ করিবেন।
- বাছাইকৃত সুতা দ্বারা তৈরিকৃত এই পাঞ্জাবি আপনাকে দেবে আরাম।
- ভাই জোস অফার, প্যারা নাই চিল, সেই লেভেলের ডিল, পুরাই আগুন!
- Offer sesh hobar age order korun, dam matro 499 taka!
- অফারটি গ্রহণ করে আপনার দিনটিকে করে তুলুন আরও আনন্দময় এবং স্মরণীয়।

## 12. What the lint checks for Bangla

`copylint --locale BD` runs, on any line with Bengali in it: formal and bookish words (`bn-formal`), sadhu forms and
notice passives (`bn-pattern`), calques (`bn-calque`), West Bengal words (`bn-locale`), repeated আপনি, mixed
address forms, Latin words in Bengali, the stacked-praise rule (`bn-poetic`), slang piles (`bn-slang-pile`), stacked
reactions and particles, এবং with no ও or আর (`bn-ebong`), repeated এটি, essay scaffolding, উপভোগ করুন as the call to
action or twice in a piece, English Gen Z slang, Banglish, and the 92 research rules for Bangla in
`scripts/voice_rules.json` (`bn-voice`): the 66 from this study and 26 from the humanizer projects (among them
opuu/bangla-writer's checks: উল্লেখ্য যে, এটি মনে রাখা গুরুত্বপূর্ণ যে, অনুগ্রহ করে on every line, অভূতপূর্ব and
বৈপ্লবিক, and, as notes because real brand ads do them too, Daraz এর without the hyphen, a space before the দাঁড়ি
and Western grouping of lakh figures). On the 50 natural and 50 robotic calibration lines: 0 findings on the natural
ones, 49 robotic ones caught. A Banglish line is read as Bangla, so the English word lists never run on it; it gets
the Banglish note (a warning on headlines, calls to action, prices and terms).
