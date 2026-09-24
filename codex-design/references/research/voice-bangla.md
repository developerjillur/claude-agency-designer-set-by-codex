# Natural Bangla voice for Bangladesh: research note, 24 September 2026

How Bangladeshi brands and ordinary readers write Bengali and Banglish for social media in 2024 to 2026, which
poetic, bookish and translated words give AI copy away, and how to lint for them without flagging what real brands
write. Every source was read on 2026-09-24. This note brings only what is new against `references/copy.md` §3 and
`scripts/copyrules.py`; the machine-readable candidates are in `bangla-casual.json` next to this file.

## 1. Method and corpora

| Corpus | Size | What it is |
|---|---|---|
| Brand YouTube titles | 580 Bengali-script titles | the latest 45 videos and 45 Shorts of 15 channels (bKash, Pathao, foodpanda, Chaldal, Grameenphone, Robi, Banglalink, 10 Minute School, Shikho, Aarong, Yellow, Bata, Rokomari, Sheba.xyz, Daraz), 2024 to 2026, pulled with yt-dlp; upload dates checked for every title quoted here |
| Brand ads | 144 Bengali ads | active Meta ads of bKash, Robi, Grameenphone, Nagad, Pathao, Shwapno, foodpanda and Daraz (Meta Ad Library, Bangladesh, active ads), mostly started July to September 2026 |
| Market sample | 1,457 ad texts | every active Bangladeshi ad the Ad Library returned for 163 probe words and phrases. It is biased toward those words, so it over-represents stiff and poetic copy; use it for "who writes this", not for base rates |
| Prothom Alo headlines | about 200 terms | exact-phrase search of Prothom Alo headlines through its public search API, as the newspaper benchmark for each word |
| Human vs ChatGPT pairs | 3,322 + 3,322 passages | Bangla news and textbook passages, each with a ChatGPT paraphrase (MehemudAzad/Bangla-AI-Generated-text-detection on GitHub): the only corpus that measures AI Bangla directly. Formal register, so it tests translation habits, not casual voice |
| Readers and research | 11 new sources | articles, fact-checks and 2026 papers on AI and machine-translated Bangla (§12) |

Limits:
- Facebook, Instagram and TikTok posts need a login, so brand voice comes from YouTube titles, Meta ads and the
  newspaper.
- The Ad Library rate-limited the probes after about 180 queries for roughly an hour. A slower batch afterwards
  collected 102 ads of Banglalink, Shikho, PRAN, Walton and Kacchi Bhai; they were kept out of the tuning and used as
  a hold-out check (§14). Aarong, Yellow and Bata come from YouTube titles only.
- The Ad Library's Bengali matching is loose for short words: it returned 1,100, 150 and 210 ads for জোস, খাইসি and
  করতেসি, yet none of the 20 ads retrieved for each contains the word. Counts in this note are used only when the
  word was found in the ad text ("n of 12 retrieved contain it").
- Bengali text is compared after NFC normalisation (য় and ড় have two encodings). Write every new list entry in NFC,
  as `copyrules.py` already does, or it will silently miss.

## 2. Key findings

1. **Big-brand copy is plain and factual.** Median sentence 9 words (p75 15, p90 20; 13 % above 18) across 431
   sentences in the 144 brand ads. The casual work is done by the emphatic -ই (in 58 % of ads) and the inclusive -ও
   (35 %), not by particles: তো, কিন্তু, নাকি, একটু and তাই না together appear in 10 of 144 ads and 27 of 580
   titles, never more than two in one text. Reaction words (উফ, আহা, ইশ) appear in 1 of 580 titles and 0 ads.
2. **Stacked literary praise is the poetic AI tell; single words are not.** Prothom Alo headlines use নান্দনিক 180
   times, মুগ্ধতা 136, অপরূপ 79. Two or more such words in one text: 0 of 724 brand texts, 69 of 1,457 market ads
   (small fashion pages, resorts, food shops). A cluster rule catches the pattern without touching brand copy; on
   102 hold-out ads of five more brands, the whole new rule set raised 0 warnings.
3. **Real brands write several clichés a lint would like to ban.** Robi, Nagad, Banglalink, Toffee and GP write
   উপভোগ করুন; Robi and Arogga write তাহলে আর দেরি কেন; Robi, Pathao, bKash and 10 Minute School write দেরি না
   করে; Shwapno writes নিকটস্থ; Rokomari writes অর্জন করুন; Pureit writes পান করুন; GP writes শুধুমাত্র and
   জার্নি. None of these can be a warning (§15).
4. **Some brands now publish AI-flavoured copy.** Chaldal's 2025 Shorts pair natural lines with lines that the
   current lint flags (the "not just X" calque and প্রতিটি মুহূর্ত); RFL and HATIL posts in 2026 use em dashes and
   stacked praise. A brand sighting is therefore weak evidence of naturalness; the newspaper count and the plain
   brands (bKash, Nagad, GP, Robi, Pathao, Shwapno) carry more weight.
5. **The em dash split is stark.** 3 % of the 144 brand ads and 3 % of the 580 brand titles contain an em dash; 31 %
   of the 1,457 market ads do (and 15 % an en dash). The market sample is word-biased, but the gap is large.
6. **Dhaka speech spellings are absent from ad text.** করতেসি, খাইসি, হইসে and the like appear in 0 of 2,181 ad
   texts and brand titles; Prothom Alo prints them only inside quotes. Brands go only as far as the colloquial
   আপনি imperative (আসেন, থাকেন) and one slang word per line.
7. **Measured AI Bangla has its own fingerprints** (§6.1). Against 3,322 human passages, their ChatGPT paraphrases
   use এবং 3.9 times as often and ও and আর 0.4 times, এটি 5 times, দ্বারা 12.6 times, কোনও 10.6 times, গিয়েছে 9
   times, and put যে after বলেছেন 58 times (the human side: 0). Prothom Alo headlines write কোনো, গেছে and এটা.
8. **Readers and researchers describe the same tells** (§12): literal idioms, English sentence order, needless
   English words, the long dash, stock phrases (পরিলক্ষিত হয়, উপসংহারে বলা যায়), numbered scaffolding, too much
   আপনি, and আপনি and তুমি mixed in one text.

## 3. How Bangladeshi brands write, 2025 to 2026

### 3.1 Sentence shapes that recur

| Shape | Example (brand, date) | Notes |
|---|---|---|
| Question hook, then the answer | "বাসার বিল দিতে বাইরে কেন যাবেন?" (Nagad ad, 9 Sep 2026) | 17 % of brand ads and 21 % of brand titles contain a question |
| Rhetorical exclamation plus particle | "কেনাকাটায় অফার পেতে কার না ভালো লাগে! তাই তো মনমতো কেনাকাটায় পেমেন্ট মানেই বিকাশ!" (bKash ad, 16 Sep 2026) | the কার না ... লাগে! frame is native and hard to translate |
| X তো আছেই | "ডায়াপার শেষ? চিন্তা কিসের, চালডাল তো আছেই!" (Chaldal Short, 13 Oct 2025) | also foodpanda (Short, 15 Dec 2024) and Vim (ad, 7 Sep 2026); a reliable native formula |
| X মানেই Y | পেমেন্ট মানেই বিকাশ (bKash, 2026); উৎসব মানেই স্টাইল (Bata) | Prothom Alo headlines use মানেই 429 times |
| [action] করলেই [reward] | 21 of 580 titles, bKash the most | already in copy.md §3.7 |
| Verb or news verb first | থাকছে, চলছে, চলে এলো, আসছে | "আসছে সাফ, প্রস্তুত বাংলাদেশ। পারবে তুমিও।" (Robi, 20 Aug 2026) |
| Two rhyming halves | স্পিনে না পেসে, ম্যাচ ঘোরাবে কীসে? (Robi Bowler Hunt title, 15 Sep 2026); ঈদ লাগছে মনে, বিকাশ পেমেন্ট সবখানে (bKash, 1 May 2026) | festive and contest copy |
| Wordplay on one word | Red Cow plays on গাঢ় (a thick taste, a closer bond; ad, 27 Aug 2026); Nagad sets বিরতি against অবিরাম (ad, 7 Sep 2026); GP asks why Wi-Fi should need a তার (wire) at all (ad, 2 Feb 2026) | |
| An everyday observation | "কিছু জিনিস মনে রাখতে হয় না, এমনিতেই মনে থেকে যায়।" (GP ad, 9 Sep 2026) | leads into a fact (a memorable number) |
| Humour from family and daily life | দুলাভাই buying on credit (bKash, 10 Aug 2026); ড্রাইভার গায়েব? (Sheba.xyz, 27 Jan 2025) | kin terms and small daily annoyances, never mockery |

### 3.2 Particles, emphasis and reactions: how many is natural

| Marker | Brand ads (144) | Brand titles (580) | Guidance |
|---|---|---|---|
| Emphatic -ই (আজই, সহজেই, ঘরে বসেই, আছেই) | 58 % of ads, 2.7 per 100 words | 23 % of titles | the main casual marker; one or two per line is normal |
| Inclusive -ও (আপনিও, নেটও চলবে, কথাও চলবে) | 35 %, 1.5 per 100 words | common | natural in parallel halves |
| তো, কিন্তু, নাকি, একটু, তাই না, আর কী, ব্যস | 7 % of ads, never more than 2 in one | 4.7 %, never more than 2 | one per line at most, one or two per caption; three or more in 30 words reads as imitation speech (lint K7) |
| Reactions: উফ, আহা, ইশ, আরে, বাহ | 0 | 1 title | one per piece, at the start, only when a person is speaking or thinking: "ইশ, যদি একটু আগে শুরু করাতাম।" (10 Minute School ad, 25 Aug 2026) |
| Exclamation mark | 56 % of ads (the house rule still allows one per line) | 39 % | |
| Emoji | 26 % of ads, about 4 in each ad that uses them | 12 % | the house rule stays: 0 to 1 on the image, up to 3 in a caption |

The takeaway for writers and for `copyjudge`: a flat Bengali line is fixed with -ই, -ও, a question or a verb-first
order far more often than with a particle. Particles are seasoning.

### 3.3 English inside Bengali: how much and how

- 71 % of brand ads and 50 % of Bengali brand titles contain at least one Latin-script word, but most are brand,
  product and app names (My Robi, Pathao Pay, FDR, GPStar) and CTA buttons.
- **Bengali-script loans are the norm for common words:** নো টেনশন (Nagad, 7 Sep 2026), টেনশন ফ্রি (bKash Short,
  31 Aug 2026), লাইফ আরেকটু ইজি (Nagad, 7 Sep 2026), এক্সপেরিয়েন্স (GP), আনলক করুন (Banglalink), জার্নি (GP ad,
  10 Aug 2026; Prothom Alo headlines use জার্নি 57 times).
- **Latin-script English words in a Bengali sentence are a youth and telecom habit:** Pathao writes Safe থাকি,
  Safe রাখি (28 Jun 2026) and "Relax-এ travel করুন with Pathao Car Intercity!" (1 Mar 2026); Robi writes
  "ব্যালেন্স gone? Royal Enfield জেতার chance এখনও ON!" (ad, 1 Sep 2026); Banglalink capitalises VOLUME, ME TIME,
  PRODUCTIVE. Fintech, grocery and retail stay mostly in Bengali script. The existing `bn-latin` note (three or
  more Latin words) is right as a note, not a warning.
- **English-only posts** are the premium fashion pattern already in copy.md (Aarong, Yellow, Bata's English
  lines); foodpanda also runs English-only brand lines ("Make life delicious").
- **What readers object to is needless English**, not loanwords (Bigganchinta, §12). Mainstream English slang is in
  brand copy too: bKash wrote flex করার মতো দারুণ একটা স্মার্টফোন (ad, 25 Aug 2026).

### 3.4 How casual they get, and where they stop

- Casual stops at one slang word per line: প্যারাহীন (Chaldal Short, 11 Jul 2025; 10 Minute School, 20 Apr 2025),
  ফাটাফাটি (Domex ad, 7 Sep 2026), চিল (foodpanda, 31 Aug 2025), সাবধানের মাইর নাই (GP video title, 12 May 2026).
- It stops at the colloquial আপনি imperative: "Credit Card নিয়ে নিশ্চই অনেক প্রশ্ন? আসেন বুঝাই, কারণ বুঝলে
  সোজা!" (bKash Short, 7 Sep 2026); মার্চেন্ট থাকেন নিশ্চিন্তে (Pathao Courier ad, 30 Jul 2026).
- Dhaka phonetic spellings (করতেসি, খাইসি) never appear in ad text (§2). Shikho's রাগ করলা ? (Short, 19 May 2026)
  is the furthest a brand title in the sample goes.
- Solemn and safety content drops the casual register completely: bKash's fraud warning (ad, 3 Sep 2026) and
  Shwapno's dengue information (ad, 21 Sep 2026) are standard, formal আপনি.
- Poetic language is kept for festival greetings and brand films: "বছরের প্রথম বৃষ্টির ছোঁয়ায় প্রশান্ত হোক মন।"
  (Banglalink Short, 2 Mar 2026); Robi's regional ads weave a thread metaphor (6 Sep 2026). Offer posts from the
  same brands stay plain.

### 3.5 Brand by brand

| Brand | Address | Voice in the sample |
|---|---|---|
| bKash | আপনি; colloquial আপনি in explainers; তুমি once in a football debate (কমেন্টে জানাও!, 4 Jun 2026) | question hooks, কারণ বুঝলে সোজা tagline, মানেই formula, family humour, Bengali-script loans; spells দারুণ right, but wrote নিশ্চই |
| Nagad | আপনি | short problem-solution lines, নো টেনশন, wordplay (রিচার্জে বিরতি নয়, অবিরাম বিনোদন!, ad 7 Sep 2026), উপভোগ করুন once per ad |
| Pathao | আপনি; English and Latin code-mixing | Safe থাকি, Safe রাখি; the courier arm uses থাকেন; English-only ride ads |
| foodpanda | তুমি (Bengali), English lines | foodpanda করো ডিলের স্বাদে চিল করো। (31 Aug 2025); নতুন এসেছেন? (ads 2026) |
| Chaldal | আপনি | natural (তো আছেই, মিস করা যায় নাকি?) next to AI-flavoured lines (em dashes, শুধু পণ্য নয়) |
| Shwapno | আপনি | কিন্তু used well (ইলিশপ্রেমীরা, সময় কিন্তু ফুরিয়ে আসছে, 21 Sep 2026), full terms lines (স্টক থাকা সাপেক্ষে, শর্ত প্রযোজ্য), writes দারুন |
| Grameenphone | আপনি; তুমি for youth; many English titles | observations, puns, ১ নম্বর claims, colloquial থাকেন, one em dash in a phone ad |
| Robi | আপনি; তুমি for Bowler Hunt and #ParbeTumio | rhyme, Latin English words, clichés (তাহলে আর দেরি কেন, নেক্সট লেভেলে) |
| Banglalink | আপনি; classic তুমি slogan শুনতে কি পাও? | seasonal poetic greetings and brand films (even a শুধু ... নয় line about the internet as a keeper of memories, ad 31 Aug 2026), capitalised English words, দুশ্চিন্তা আর নয়! openers, আপনি যেখানে, বাংলালিংক সেখানে |
| 10 Minute School | তুমি for students, আপনি for parents | English-heavy titles, প্যারাহীন, Latin "Vai" in a title |
| Shikho | তুমি | জেনে নাও, মাথায় রাখো, কল করো 16780 (phone numbers in Latin digits), আসলেই, একদম, colloquial রাগ করলা, স্বপ্নের কলেজ; misspells মুহূর্ত as মুহুর্ত |
| Aarong, Yellow | English | English-only titles; copy.md already covers them |
| Bata | English; Bengali for festivals | উৎসবে ভালোবাসায় ঈদ মানে বাটা; ভাগ ব্যাকটেরিয়া ভাগ (7 Feb 2024) talks to germs in the তুই imperative |
| PRAN (PRAN UP, Toast, Junior, Layer) | pronoun-free, playful; তুমি in #SmartKichuKhao | "প্রাণ আপ ছাড়া আর কী!" (PRAN UP ad, 16 Sep 2026); PRAN Toast calls itself the tea-time দোস্ত (ads, 7 Sep 2026); PRAN Layer wrote প্রতিটি মুহূর্ত twice in one line (3 Sep 2026), which the existing calque check flags |
| Walton | আপনি; formal CSR | ফ্রিজ একটাই ওয়ালটন; যত বেশি স্টার, তত বেশি সেভিংস! (18 Sep 2026); Walton Computer wrote সুবর্ণ সুযোগ and !!!; Walton Cables stacks নির্ভরতা, নিশ্চিন্ততা and ছোঁয়া with a long dash; Walton Plaza wrote শুধুমাত্র আপনার নিকটবর্তী ওয়ালটন প্লাজায় and প্রানবন্ত (Sep 2026) |
| Rokomari | আপনি | question titles for its talk show; ads use সমাহার, উপভোগ করুন, অর্জন করুন and an em dash |
| Sheba.xyz | আপনি | short service lines, ড্রাইভার গায়েব?, several !!! |
| Kacchi Bhai | pronoun-free and আপনি; English for Pathao Food promos | branch ads on 23 and 24 Sep 2026: a question hook with sensory detail ("দুপুরে আজ একটু খুলনার স্বাদ হলে কেমন হয়?"), আজই শেষ দিন with the old and new price, ঠিকানাঃ with a visarga |
| Small F-commerce pages | আপনি | the market sample: ঢাকার বাহিরে delivery lines, em dashes, stacked praise, তাহলে আর দেরি কেন, করে তুলুন আরও |

## 4. Register ladder for Bangladesh

| Rung | Forms | Who uses it, and when | Evidence |
|---|---|---|---|
| **তুই-chat** | তুই, তোর; কর, খা, ভাগ; করিস, খাবি | Never to address a customer. Only inside quoted dialogue between friends, in memes, in drama and film promos, or when a brand talks to a thing (Bata tells bacteria to run: ভাগ ব্যাকটেরিয়া ভাগ, 7 Feb 2024) | 0 তুই verbs in 144 brand ads and 580 titles. The one brand use found is a quoted line between friends: "দোস্ত, তোর ফোন দিয়ে একটা ছবি তুলে দে না!" (bKash ad, 25 Aug 2026), which the ad then answers in আপনি. Prothom Alo prints তুই only inside quotes (‘ওয়াও! তুই কখন আসলি?’, headline, 20 Sep 2026). BanglaSocialBench (2026) found LLMs avoid তুই even where it is the natural choice in dialogue |
| **তুমি-casual** | তুমি, তোমার; করো, নাও, জানাও, দেখো, রাখো | School and college students (Shikho, 10 Minute School student content, Panjeree), youth contests and slogans (Robi Bowler Hunt, #ParbeTumio; Banglalink's শুনতে কি পাও?), food delivery lines for the young (foodpanda) | "আর জানাও, স্পিনে না পেসে, ম্যাচ ঘোরাবে কীসে?" (Robi ad, 19 Sep 2026); 18 of 580 titles, mostly Shikho |
| **আপনি-warm** | আপনি with colloquial forms: আসেন, থাকেন, দেখেন, করেন; plus question hooks, -ই, one particle | Explainers, reminders and offers from fintech, telecom and delivery brands when they want to sound like a helpful person | bKash Short (7 Sep 2026) আসেন বুঝাই; Pathao Courier ad (30 Jul 2026) থাকেন নিশ্চিন্তে; GP ad (31 Aug 2026) "ঘরে-বাইরে যেখানেই থাকেন"; Prothom Alo headlines quote ministers and witnesses using আসেন in speech (Sep 2026). 2 of 144 brand ads use the -েন imperative, never mixed with -ুন in the same ad |
| **আপনি-formal** | আপনি with -ুন imperatives, full standard verbs, no slang, complete sentences | Fraud and security alerts, health information, loans, insurance, terms, service notices | bKash fraud alert (ad, 3 Sep 2026: বিভ্রান্ত হবেন না ... কল কেটে দিন); Shwapno dengue information (ad, 21 Sep 2026); UCB SME and MetLife ads (2025 to 2026) |
| Pronoun-free | থাকছে ২০% ছাড়, এক ক্লিকে বাজার শেষ | The most common shape in titles; sidesteps the choice | most brand titles carry no pronoun |

Rules that follow from the data:
- One rung per piece. The existing check catches আপনি with a তুমি verb. Within আপনি, the -েন and -ুন imperatives
  were never mixed inside one ad in the sample; keep them apart.
- **Fix for the existing CTA check:** `BN_CTA_END` accepts ুন, িন, ান, ো, াও, ও but not the colloquial -েন
  (থাকেন, আসেন, দেখেন, নেন). A CTA such as "চলে আসেন" gets a false "no action verb" note today. Accept -েন in CTA
  roles; the address-form check still guards consistency.
- Research agrees that LLMs overuse আপনি (BanglaSocialBench, 2026) and switch between আপনি and তুমি inside one text
  (BLADE, 2026); both are already covered by the judge prompt and the honorific check.

## 5. Poetic and literary words: calibrated

Counts: Prothom Alo headlines ("PA"); active Bangladeshi ads the Ad Library returned ("Ads", with how many of the 12
retrieved actually contain the word); who uses it. Verdict: **cluster** means the word counts toward the new
stacked-praise warning (two or more in one line, three in a caption) and is never flagged alone.

| Word or phrase | PA | Ads (in text) | Who uses it | Verdict |
|---|---|---|---|---|
| স্বপ্নের ডানায় | 0 | 1 (0) | nobody in the sample | **warning** |
| হৃদয়ের গভীর থেকে | 0 | 7 (4 of 6) | a political page, a beauty shop | **warning** (medium risk: personal greetings) |
| হৃদয় ছুঁয়ে / মন ছুঁয়ে যাবে | 1 / 2 | 38 (11) / 130 (3) | gift, book, travel pages; PA uses the past form in reviews | note, promise form only |
| রাঙিয়ে দিন / তুলুন | 0 / 0 | 2 (2) / 33 (11) | small fashion and gift shops; HATIL wrote রাঙিয়ে তুলুক | note |
| ছুঁয়ে যাক | 0 | 7 (3) | furniture, a school, a craft shop; PA used it in an Eid wish in 2018 | not flagged |
| ডানা মেলে | 10 | 8 (4) | PA uses it for real wings and ambitions | not flagged |
| অপরূপ | 79 | 220 (5) | resorts, tourism | cluster |
| মনোমুগ্ধকর | 34 | 710 | small shops (a honey page, melamine, kurtis) | cluster |
| মনোরম | 32 | 710 (4) | resorts | cluster |
| নয়নাভিরাম | 3 | 19 (7) | tour operators, resorts | cluster |
| নান্দনিক | 180 | 1,600 (9) | HATIL, RFL Building Hub, Crystal Melamine | cluster |
| অনবদ্য | 54 | 170 (4) | Walton Computer, Crystal Melamine | cluster |
| অনন্য | 830 | 4,000 (6) | Ispahani Mirzapore Tea, Polar, Red Cow | cluster (never alone) |
| অসামান্য, অভূতপূর্ব, অবিস্মরণীয় | 40, 45, 9 | 28, 65, 68 | gift shops; Rokomari Islamic Books (অভূতপূর্ব সাড়া); buffets | cluster |
| অপার, অফুরন্ত, অবারিত, অনাবিল | 87, 22, 9, 8 | 300, 210, 14, 130 | resorts; Tapmad (মাত্র ১০ টাকায় অফুরন্ত আনন্দ) | cluster |
| স্নিগ্ধ, স্নিগ্ধতা, মাধুর্য, মুগ্ধতা | 104, 28, 7, 136 | 540, 140, 28, 94 | HATIL, fashion pages | cluster |
| শিহরণ, চিরন্তন, কালজয়ী | 17, 58, 4 | 14 (0), 180, 98 | book shops, fashion | cluster |
| আভিজাত্য, রাজকীয় | 34, 20 | 1,700 (10), 3,400 (9) | RFL Building Hub, fashion, a ghee brand | cluster |
| স্বর্গীয়, জাদুকরী, মোহনীয়, মায়াবী | 3, 28, 5, 8 | 62, 860, 50 (10), 430 | LUX writes মোহনীয়; RFL Best Buy writes মায়াবী | cluster |
| প্রশান্তি, মেলবন্ধন | 64, 118 | 1,400, 820 | religious and health pages; matrimony; Rokomari | cluster |
| রোমাঞ্চকর | 188 | 270 (11) | PRAN Junior, RFL Best Buy; sports news | not flagged |
| কোমলতা | 4 | 220 (10) | literal: fabrics, baby care | not flagged |
| সমাহার | 77 | 500 | Rokomari, Walton Refrigerator | not flagged |
| এক ছাদের নিচে, হাতের মুঠোয় | 79, 6 | 780 (10), 1,300 (7) | Praava Health; Chaldal | not flagged |
| স্বপ্নের ঠিকানা | 7 | 430 | real-estate developers (a genre phrase) | not flagged |
| নতুন দিগন্ত, নতুন অধ্যায়, নতুন মাত্রা | 73, 7, 87 | 98, 300, n/a | foodpanda partner ads; HATIL Bashundhara | not flagged (news idioms) |
| উষ্ণতা, পরশ, আবেশ, শাশ্বত, সৌরভ, অমৃত | 131, 60, 11, 28, 344, 27 | | also literal words or personal names (আবেশ খান, সৌরভ) | kept out of the cluster |
| ভালোবাসার ছোঁয়া, যত্নের ছোঁয়া, প্রকৃতির ছোঁয়া | 0, 0, 1 | 130 (8), 77 (10), 190 (7) | RFL Gas Stove, Ribana, Farm Fresh | not flagged; ছোঁয়া is also literal |

Why a cluster and not a list: brands and the newspaper use each word, so a single-word rule flags real copy; the
stack is what brand copy never does (0 of 724 texts) and what generated and puffery copy does often.

## 6. Stock AI Bangla phrases and sentence patterns (new)

| Pattern | Example | Level | Evidence in one line |
|---|---|---|---|
| "In today's busy world" opener | আজকের এই ব্যস্ত জীবনে ..., দ্রুতগতির এই পৃথিবীতে ... | warning | PA 0; 11 of 12 ads retrieved for it are small shops; Chaldal's mid-line কর্মব্যস্ত জীবনে is not matched |
| উত্তেজিত for "excited" | আমরা ভীষণ উত্তেজিত ... | warning | in BD news উত্তেজিত means agitated (উত্তেজিত জনতা, PA 30 Mar 2023) |
| Announcement formula | আনন্দের সাথে জানাচ্ছি | warning | PA 0; 8 of 12 retrieved ads; the Bangla form of launch hype |
| "You deserve it" | সেরাটাই আপনার প্রাপ্য, আপনার কফি সেরাটাই ডিজার্ভ করে | warning | 12 of 20 ads retrieved for প্রাপ্য and 10 of 20 for ডিজার্ভ use it this way (small shops, 2025 to 2026); first-person quotes (এটা আমি ডিজার্ভ করি) and আপনার প্রাপ্য টাকা (a refund) are not matched |
| Essay closer | উপসংহারে বলা যায়, পরিশেষে বলা যায় | warning | named by AnswerPointBD (9 Dec 2025) |
| Report verb | পরিলক্ষিত হয় | warning | PA 1 (a party statement) |
| "We are proud / thrilled" | আমরা গর্বিত, আমরা আনন্দিত | note | PA uses them only in quotes |
| "Welcome to the world of X" | খাবারের জগতে স্বাগতম | note | ফুডপ্যান্ডায় স্বাগতম (foodpanda) is fine and not matched |
| Essay importance | অপরিহার্য অংশ, গুরুত্বপূর্ণ ভূমিকা পালন করে | note | normal in news |
| Assertion | নিঃসন্দেহে | note | PA 14, all quotes |
| English order "make X more Y" | ... কে করে তুলুন আরও সুন্দর | note | 530 and 740 ads; common, so a note |
| "In every bite / sip / drop" | প্রতিটি কামড়ে, প্রতিটি চুমুকে, প্রতিটি ফোঁটায় | note | 16 of 20 ads retrieved for প্রতিটি কামড়ে use it (Naturo, Bisk Club, Jun to Sep 2026); Chaldal Shorts (2025) and a Walton pump ad (Sep 2026) write প্রতিটি ফোঁটায় |
| "Take it to the next level" | নিয়ে যান নেক্সট লেভেলে | note | Robi (ad, 10 Aug 2026), so never a warning |
| "Unlock a world of" | আনলক করুন ... দুনিয়া | note | Robi (ad, 31 Aug 2026); Toffee says it plainly |
| "Stay connected" | সংযুক্ত থাকুন | note | telecoms write কানেক্টেড থাকুন |
| Coaching clichés | স্বপ্নকে বাস্তবে রূপ দিন, সাফল্যের চাবিকাঠি | note | coaching and job-prep pages (Panjeree, Apr 2026) |
| "Feel the difference" | অনুভব করুন | note | supplement and apparel pages |
| "Treat yourself" | নিজেকে দিন স্মার্ট লুক | note | 19 of 20 retrieved ads (gyms, apparel, gadgets); PA 0 |
| "We believe" | আমরা বিশ্বাস করি | note | 14 of 20 retrieved ads (investment and hotel pages); GP used it once (10 Sep 2026) |
| "An amazing experience" | অসাধারণ অভিজ্ঞতা, অনবদ্য অভিজ্ঞতা | note | extends the existing অনন্য অভিজ্ঞতা check |
| Numbered scaffolding | প্রথমত ... দ্বিতীয়ত | note | named by Bangla Samagra (16 May 2026) |

Tested and not turned into rules: a simple এবং density rule (two in a sentence fired on 3.5 % of brand ads and
2.7 % of market ads, so it separated nothing; the stricter H7 below does), এক অনন্য (PA 50 headlines), নতুন মাত্রা
(PA 87), bracketed English glosses (a Robi pack lists এসএমএস (Outgoing), a legitimate spec).

### 6.1 Measured on human passages and their ChatGPT paraphrases

Counts per 3,322 passages each (similar word totals: 142,109 human, 149,168 paraphrased). The human side is formal
news and textbook prose, so these are translation habits, not casual-voice habits.

| Marker | Human | ChatGPT | Newspaper and brands | Candidate |
|---|---|---|---|---|
| এবং | 910 | 3,763 (3.9 times per word) | brand titles use ও 5 times as often as এবং | H7 note: 3 or more এবং and no ও or আর (21 human vs 281 paraphrases; 1 of 144 brand ads) |
| ও, আর (and) | 1,962, 322 | 871, 140 (0.4 times) | | (the other half of H7) |
| এটি | 103 | 544 (5 times) | PA: এটা 1,142 vs এটি 382 headlines | H5 note: এটি twice or more (7 vs 78; 0 brand texts) |
| একটা | 115 | 6 | a casual line uses টা freely (§16 natural lines) | judge only |
| দ্বারা | 16 | 211 (12.6 times) | PA 43 (science, quotes) | H4 note (16 vs 183 passages; 0 brand texts) |
| কোনও | 9 | 100 (10.6 times) | PA: কোনো 4,641 vs কোনও 2 | H1 warning |
| গিয়েছে | 6 | 57 (9 times) | PA: গেছে 4,867 vs 2; গেছেন 1,998 vs গিয়েছেন 0 | H2 warning (BD locale) |
| বলেছেন যে and other reporting verbs + যে | 0 | 58 (113 passages) | PA: 1 headline, a 2016 quote | H3 warning |
| X করতে সাহায্য করে | 16 | 108 (6.4 times) | 46 market ads, mostly supplements | H6 note |
| প্রদান, অত্যন্ত | 55, 34 | 228, 155 (4 times) | | already in `BN_FORMAL`: the existing list is confirmed |
| যেগুলি | 2 | 26 | | already covered by the -গুলি note |
| আরম্ভ | 0 | 16 passages | | the new আরম্ভ warning |

All voice candidates together (leaving out the punctuation and spelling checks): 31 human passages get a warning and
131 any finding; 288 paraphrases get a warning and 817 any finding. On news prose the new rules fire six times as
often on machine text as on human text.

## 7. Formal to everyday: new swaps

| Formal | Everyday | Level | PA | Ads (in text) | Note |
|---|---|---|---|---|---|
| উপলব্ধি করুন | বুঝবেন, টের পাবেন | warning | 0 | 19 (5) | |
| ভোজন করুন | খান, খেয়ে দেখুন | warning | 0 | 0 | ভোজনরসিক (foodie) is fine and not matched |
| উপস্থিত হোন | চলে আসুন | warning | 0 | 0 | invitations use উপস্থিত থাকার অনুরোধ, not matched |
| অবস্থান করুন | থাকুন | warning | 0 | 1 | |
| নিম্নোক্ত | নিচের | warning | 0 | 140 (7) | MetLife, Truck Lagbe; the list already has নিম্নলিখিত |
| সত্বর | তাড়াতাড়ি, শিগগির | warning | 1 | 19 (0) | |
| তথাপি | তবুও | warning | 0 | 13 (0) | |
| অত্র | এই | warning | 0 | 64 (2) | notice register |
| আরম্ভ | শুরু | warning | 4 | 120 (0) | শুভারম্ভ (grand opening) is not matched |
| গৃহ, গৃহে | ঘর, বাসা, বাড়ি | warning | 8 | 16 (0) | compounds গৃহসজ্জা, গৃহিণী are not matched |
| তৈরিকৃত, and -কৃত on English loans (ডিজাইনকৃত) | তৈরি, ডিজাইন করা | warning | 0 | 87 (10) | |
| উপকৃত হোন | (say the benefit) | warning | | | the imperative only; উপকৃত হয়েছি is natural |
| বাহিরে | বাইরে | note | ঢাকার বাহিরে 0 vs বাইরে 192 | 1,800 vs 4,800 | a spelling note; F-commerce writes it often |
| বাছাইকৃত | বাছাই করা | note | 3 | 990 (11) | |
| লাভ করুন | পান, পেয়ে যান | note | 0 | 67 (4) | লাভ also means profit |
| হালনাগাদ | আপডেট | note | 251 | 130 (4) | a government and news word |
| আহার | খাবার, খাওয়া | note | 26 | 97 (3) | |
| টাকার ঊর্ধ্বে | টাকার বেশি | note | | | idiomatic ঊর্ধ্বে (সবকিছুর ঊর্ধ্বে) is not matched |
| প্রতিবছরের ন্যায় | প্রতিবছরের মতো | note | 0 | 7 (3) | Walton dealer pages |
| দ্বারা (any use) | দিয়ে, or the active voice | note | 43 | 730 for দ্বারা তৈরি (4) | measured AI marker, §6.1 (H4) |
| গ্রহণ করে, করতে, করলে | নিয়ে, নিতে, নিলে | note | 29 (news) | | extends the existing গ্রহণ করুন; অংশ গ্রহণ is not matched |
| অত্যাবশ্যক | খুব দরকারি | note | 15 | | named by AnswerPointBD |

Calibrated keeps (do not add): উপভোগ করুন (brands, see §15), সাশ্রয় করুন (bKash), পান করুন (Pureit: নিরাপদ পানি
পান করুন, Aug 2026), নিকটস্থ (Shwapno, 21 Sep 2026), নিকটবর্তী (Walton Plaza, 13 Sep 2026), অর্জন করুন
(Rokomari, 12 Aug 2026), প্রচেষ্টা (PA 146; Walton CSR), প্রত্যাশা (PA 717), যথাযথ (PA 292), শ্রেষ্ঠ (PA 359),
উত্তম (PA 224), অধিক (Shwapno: ১০০১ টিরও অধিক আউটলেট), কর্তৃক (BCSIR কর্তৃক পরীক্ষিত is a legal claim),
স্বল্প খরচে, সম্পূর্ণ ফ্রি, নিশ্চিত করুন, অবস্থিত, অচিরেই, নূতন (names and institutions such as নূতন বিদ্যুৎ).

## 8. Sadhu forms the current pattern misses

The sadhu regex in `copyrules.py` lists a few stems (করি-, হই-, পাই-, দিয়াছ, গিয়াছ ...). Five additions
cover the rest with no hit in 2,181 real ad texts and brand titles:
- `(?:ি|ই)য়াছ`: every sadhu perfect (দেখিয়াছেন, খাইয়াছি, বলিয়াছে). No চলিত word contains it.
- `(?<![দনজ])িতেছ`: the sadhu continuous (চলিতেছে, করিতেছি). দিতেছি and নিতেছি are Dhaka speech, and জিতেছে (has
  won) is চলিত, so all three are excluded (the জ case surfaced in sports news in the human test set).
- কেহ, কাহার, কাহারও, কাহাকে: sadhu pronouns not in the list.
- বলিল, বলিলেন, কহিল, কহিলেন, এক্ষণে: the words most typical of sadhu in the SadhuCholito-BN corpus (42,734
  sentences). হস্তে is also typical, but কঠোর হস্তে দমন is a live news idiom, so it stays out.
- যদ্যপি, নচেৎ, কিঞ্চিৎ, কুত্রাপি: literary function words from the Bengali Wikipedia সাধু ভাষা tables (যদিও,
  নইলে, একটু or কিছু, কোথাও).
- Do not flag দিবেন, নিবেন, দিয়েন: they are Bangladeshi colloquial, not sadhu, and very common in F-commerce (the Ad
  Library returned 11,000 ads for দিবেন; 7 of the 20 retrieved use it, as in "মিলিয়ে নিবেন তারপর টাকা দিবেন", Classic Shopping ad, 12 Aug 2025). A generic
  -িবে pattern would catch them; the patterns above do not.

## 9. Dhaka speech and slang in writing

- **Where it works:** quoted dialogue, memes, a youth brand that talks this way, one word per line. Prothom Alo
  itself runs slang in lifestyle and entertainment headlines ("মাথা নষ্ট অ্যাকশন, এই সিনেমা না দেখলে মিস করবেন",
  4 Aug 2026; "মানুষ অফিস নিয়ে এত প্যারা খায় কেন, বুঝি না", 4 Oct 2025).
- **Where it looks fake:** in fintech, banks, health and notices; when three or more slang words pile up; when
  Dhaka phonetic spelling (করতেসেন) sits next to formal honorifics (সম্মানিত গ্রাহক).
- **Never:** ক্ষ্যাত (mocks rural or lower-class people: SentNoB comments use it for eating habits and speech,
  natok titles set গ্রামের ক্ষ্যাত against the city), আবাল and ফকিন্নি (abuse). খ্যাত (famous) is a different word:
  Prothom Alo headlines use it 22 times, always meaning famous, and বিখ্যাত and কুখ্যাত contain it, so the lint
  matches only the whole words ক্ষ্যাত, আবাল, ফকিন্নি.
- **Kolkata forms in Bangladeshi copy:** হেব্বি (Dhaka: জোস), চাপ নিও না (Dhaka: টেনশন নিয়ো না, প্যারা নাই).
  copy.md §3.4 names them; the lint does not check them yet (candidates K4, K5).
- Meanings from use (Daraz reviews, mean star rating of reviews containing the word; overall 4.54): জোস 4.93,
  অস্থির 4.94 and ফাটাফাটি 4.94 are praise; পুরাই 2.79 (most often followed by ফালতু) and হুদাই 2.10 lean
  negative; কড়া is mostly literal (strong tea); প্যারা alone is rare. Slang is a small share of praise words: about
  270 hits for জোস, অস্থির and ফাটাফাটি against about 3,000 for অসাধারণ and দারুণ. House spelling: জোস (99 to 27
  over জোশ on Daraz); Pathao used both within ten days in February 2022.
- Brand slang lines found by the Banglish pass: জোস ডিলে কিস্তিমাৎ! (Pathao, 12 Feb 2022), ওয়ার্ল্ডকাপ
  এক্সপেরিয়েন্স হবে সেই লেভেলে (Nagad, 21 Sep 2023), ইন্টারনেটের প্যারা instant শেষ। (Airtel, now Cirkle, 1 Dec 2024).
  One viewer called the Airtel ad "REALLY cringe"; another turned Nagad's phrase into সেই লেভেলের চিটিং.
- 0 of 4,547 titles from 12 brand channels contain a -সি or -সে verb. In Bengali-script Daraz reviews even
  colloquial writers use ছ: হয়েছে 81.4 %, হইছে 14.7 %, হইসে 1.3 %. The স spelling is a romanised habit (hoise).
- Lint candidates: K1 (Dhaka phonetic spelling, warning, skip quoted dialogue), K2 (three or more slang words,
  warning), K3 (ক্ষ্যাত, আবাল, ফকিন্নি: warning), K4 and K5 (Kolkata forms), K6 (two or more reaction words, note),
  K7 (three or more particles in 30 words, note), GZ (English Gen Z slang such as rizz or bruh in Bengali copy,
  note). Not flagged: মফিজ and কামলা (a common name and a literal word for day labour in Prothom Alo headlines).

## 10. Banglish (romanised Bangla)

**Where Bangladeshis write it.**
- Comments, forums and reviews. BanglaTLit's 245,727 samples are mostly TrickBD forum comments plus Facebook,
  YouTube and blog sentiment sets. In a 205,660-review sample of Daraz reviews (BanglishRev, collected 2024) the
  split is 57.4 % English, 26.0 % Bengali script, 13.1 % Banglish and 2.8 % mixed. Bengali script rose from 12.4 %
  (2018) to 33.1 % (early 2024) while Banglish held at 11 to 16 %.
- Seller replies in the same sample: 63.0 % English, 25.7 % Bengali script, 8.3 % mixed, only 2.6 % Banglish.
- The F-commerce buyer's stock question is "Price koto?" (a 2026 seller tutorial is built on it; koto appears 4,081
  times in BanglaTLit).
- Brands use it for campaign names, song titles and hashtags, usually beside Bengali script: GP's স্বপ্ন যাবে বাড়ি
  with "Shopno Jabe Bari" (2025), Banglalink's "Internet Jokhon Hoye Uthe Sritir Thikana" (6 Aug 2026), Daraz's
  "Shobai Ekhon Phone e?" (31 Oct 2023), foodpanda's "Khela hobe" (5 Oct 2023), Robi's #ParbeTumio and Domex's
  #NaakDiyeDekhun (ads, Sep 2026), 10 Minute School's "Dana Vai" (1 Mar 2026). The offer copy itself stays in
  Bengali script.
- Prices: 0 of 182 brand YouTube titles that state a price write it in Banglish (140 Bengali script, 42 English).

**Spellings people actually use** (BanglaTLit, 3.31M tokens / BnSentMix, 20,015 comments / Daraz Latin-only
reviews, 146,295):

| Bangla | Most common | Other variants and shares |
|---|---|---|
| ভালো | valo 86 / 68 / 69 % | vlo 8 to 14 %, bhalo 3 to 11 %, balo 2 to 4 % |
| ভাই | vai 65 / 52 / 62 % | bhai 12 to 19 %, vaiya 9 to 17 % |
| কিছু | kichu 67 / 42 / 42 % | kisu 19 to 38 %, kicu 10 to 17 % |
| আছে | ache 51 / 36 / 36 % | ase 38 to 52 % (also means আসে), ace 11 to 16 % |
| হয়েছে | hoise 15 / 46 / 38 % | hoyeche 18 to 49 %, hoiche or hoice 24 to 29 % |
| অনেক | onek 58 / 49 % | onk 35 to 42 % |
| না, কি | na 92 to 97 %, ki 99.6 % or more | naa and kee are rare |
| নেই | nai 74 to 85 % | nei |
| please, thanks | plz (55 to 68 % in comments), tnx | dhonnobad 1 to 9 % |

Vowel dropping is normal (amr, kmn, kno); digits for syllables (2mi, gr8) have almost disappeared; digits appear
as numbers with classifiers (1ta, 2ta). There is no agreed standard: commenters on a 2022 tutorial argued over how
to spell বন্ধু.

**When it is wrong.**
- Official records and notices: the Bengali Language Implementation Act 1987 (section 3) requires Bangla in
  government records and correspondence; that it rules out romanised Bangla is an inference, not in the text.
- Broadcast and formal speech: besides the 2012 High Court order, the state minister for information told FM
  stations in January 2018 to drop Banglish (The Daily Star, 30 Jan 2018); a 2026 satire video mocking a Banglish
  speech in parliament drew 211k views and approving comments.
- Findability: Banglish-dominant Daraz users got the worst recommendations, 46.8 % below Bengali-script users,
  because spelling variants split the vocabulary (arXiv 2606.16387, 15 Jun 2026).
- Headlines, prices and terms: copy.md §3.3 already says never; candidate B1 now detects romanised Bangla (a note,
  raised to a warning in headline, CTA, price and terms roles). It fires on 0 of 1,187 brand titles with Latin text.

**Replying in Banglish** (a youth brand answering a commenter in kind): use the majority spellings (valo, vai,
kichu, ache, hoise, onek, na, ki, nai, plz), prefer inbox or message to DM (BanglaTLit: inbox 559, dm 2), pair any
romanised campaign name with Bengali script, and never put a price or a condition only in Banglish. Candidate B2
notes naa, kee, 2mi and gr8.

## 11. Punctuation and spelling slips in 2026 brand copy

| Slip | Seen in | Candidate |
|---|---|---|
| নিশ্চই for নিশ্চয়ই | bKash Short, 7 Sep 2026 | X3, warning |
| দারুন for দারুণ | Robi ad (4 Aug 2026), Shwapno ad (21 Sep 2026); PA prints দারুণ 517 times, দারুন 9 | X3, warning |
| মুহুর্ত for মুহূর্ত | Shikho YouTube (19 Apr 2026) | X3, warning |
| প্রানবন্ত for প্রাণবন্ত | Walton Plaza ad, 10 Sep 2026 | X3, warning |
| -ী on loans: ডেলিভারী, গ্যারান্টী, দেরী, তৈরী | F-commerce ads | X3, warning (Bangla Academy 2012 rule) |
| U+09F7 (৷, currency numerator four) used as the দাঁড়ি | Red Cow ad, 27 Aug 2026 | X6, warning: screen readers and search read it as a number |
| a space before । | foodpanda ad (13 May 2026), Robi, GP; 8 of 144 brand ads | X1, note; skip titles that use " । " as a separator |
| no space after । | Banglalink Short (14 Apr 2026), bKash Short (13 Aug 2026) | X2, note |
| greeting openers beyond প্রিয় গ্রাহক | Retina coaching ad (18 Aug 2026) opens প্রিয় শিক্ষার্থীরা | X4, warning (extends the existing check) |

## 12. What readers and researchers say about AI and machine-translated Bangla

New since copy.md (which cites Prothom Alo, Niropekho and Bigganchinta 2025 on the dash and on AI Bengali being
grammatical but absent from everyday talk):

| Source (date) | What it says |
|---|---|
| Bangla Samagra, "এআই নাকি মানুষের লেখা - চিনবেন কীভাবে?" (16 May 2026), summarising Kabir Alamgir's year-long comparison for Deshkal News | The richest Bangla-specific list: recurring "coding words" of AI analysis prose (অশনি সংকেত, পালাবদল, সন্ধিক্ষণ, বহুমাত্রিক, সমীকরণ, নতুন বাস্তবতা, টানাপোড়েন), numbered scaffolding (প্রথমত, দ্বিতীয়ত), English glosses in brackets after Bangla terms, curly quotes and the long dash, repeated sentence frames, literal calques (an English "dark chapter" rendered word for word instead of কালো অধ্যায়). It adds that detectors are unreliable for Bangla |
| Bigganchinta, Riton Khan, "বাংলা ভাষায় কৃত্রিম বুদ্ধিমত্তা" (29 Aug 2026; also on Prothom Alo) | Answers are vague even when spelled right; literal translation distorts idioms; models know only standard urban Bangla. "কোথাও আবার বাংলা বাক্যের মধ্যে অপ্রয়োজনীয় ইংরেজি শব্দ ঢুকে যাচ্ছে।" Ordinary mixing is fine; needless English is the complaint |
| The Daily Star, "Bangla in the age of algorithms" (21 Feb 2026) | A Dhaka University Bangla professor calls AI language mechanical and easy to spot in assignments; an LLM researcher says chatbots fall back on 10 to 20 response patterns and push English sentence structure onto Bangla |
| Prothom Alo opinion on the Class 7 science book (20 Jan 2023) | Passages copied and machine-translated line by line made a simple lesson hard to read: the benchmark case of translated Bangla in public life |
| Prothom Alo, "চ্যাটজিপিটি কি বাংলায় কবিতা লিখতে পারে" (4 May 2023) | ChatGPT's Bangla poem was far rawer than its English one for the same prompt |
| AnswerPointBD, "Bangla AI Text Humanizer" (9 Dec 2025; a commercial tool page) | Readers dislike hard sadhu forms and needlessly complex words; stock AI phrases include অত্যাবশ্যক, পরিলক্ষিত হয় and উপসংহারে বলা যায়. The page itself uses the long dash and ends with পরিশেষে বলা যায় |
| FactWatch and Rumor Scanner fact-checks (Feb to Aug 2026) | AI videos give themselves away by a mechanical or robotic voice, lips out of sync, one voice reused for different people, and a voice that shifts mid-clip |
| BLADE, arXiv 2605.22487 (United International University, May 2026) | Untuned models wrote formal Bangla application letters with blocks in the wrong order and switched between আপনি and তুমি in one letter; expert fluency 2.40 of 5 |
| BanglaSocialBench, arXiv 2603.15949 (Jahangirnagar, RUET, BUET; Apr 2026) | 12 LLMs overuse আপনি where তুমি or তুই is natural, especially an elder talking to a younger person, and pick kinship terms from the wrong community (a student bargaining with a rickshaw puller says মামা) |
| Bangla idioms, arXiv 2609.03410 (3 Sep 2026) | Native raters scored the best models about 1.4 of 2 on idiom paraphrase; overly literal renderings were the common failure |
| TigerLLM, ACL 2025 | Many Bangla models sound translated because their instruction data is English data run through Google Translate |

What readers say sounds natural: plain সহজ-সরল words rather than sadhu or needlessly complex ones; everyday
Bangla-English mixing, the spoken and social-media register and regional variation; pronouns that fit the
relationship; real idioms; personal experience and a recognisable voice. Memes about "ChatGPT-er Bangla" could not
be verified: Facebook and Reddit need a login and the search budget ran out.

How this maps to the lint: needless English (the existing `bn-latin` note), the long dash (existing), stock phrases
and scaffolding (new ESS, PRL, ATB, SCF), analysis-prose words (left to the judge: they are normal in Prothom Alo
features, e.g. বহুমাত্রিক 75 headlines), and register (existing honorific check; judge).

## 13. Resources

No official list of bookish-to-everyday swaps exists: the Ministry of Public Administration's সরকারি কাজে ব্যবহারিক
বাংলা (2015, 75 pages) is only the Bangla Academy spelling rules plus a right/wrong spelling list, and Prothom Alo's
ভাষারীতি is a printed book with no online excerpt. So the lint's word lists have to be built, and these are the
best inputs found (licences matter if a list ships with the skill):

| Resource | What is in it | Use for the lint | Licence |
|---|---|---|---|
| Prothom Alo, প্রথম আলো ভাষারীতি (Prothoma, 2009; 21st printing 2025) | the house style book: wrong words and usages, a write/do-not-write list | buy it and hand-code rules; the newspaper's search API (§1) gives usage counts meanwhile | copyright |
| Bangla Academy, প্রমিত বাংলা বানানের নিয়ম (2012 rules; 2015 reprint scanned on archive.org) | spelling (কী/কি, ও-কার, ি in non-tatsama words) | already behind copy.md §3.6; add কোনও and the -ী loans (H1, X3) | none stated |
| Bengali Wikipedia, সাধু ভাষা | a 17-row pronoun, noun and indeclinable table (about 51 pairs) and about 60 verb forms by tense | the cleanest seed list of sadhu to চলিত pairs (D1 to D5 use it) | CC BY-SA |
| Sadhu2Colito (GitHub, themasudur; ICCIT 2019) | 20 verb-root groups, 53 suffix rules (িয়াছে to েছে, ইতেছে to চ্ছে) and 16 exception pairs | port the suffix rules into regexes, internal use only | none |
| SadhuCholito-BN (GitHub, 2026) | 42,734 sentences from scanned books, labelled sadhu or চলিত | the words most typical of sadhu (বলিল, করিয়া, কেহ, এক্ষণে); labels are noisy (character names leak) | research only |
| BanglaBlend (Mendeley, Data in Brief 2024) | 7,350 sentences, half sadhu | train a sadhu/চলিত classifier | CC BY 4.0 |
| Bangla AI-generated text detection (GitHub, MehemudAzad) | 3,322 passages each with a ChatGPT paraphrase | the only direct measure of AI Bangla (§6.1; H1 to H7) | none |
| BanglaSocialBench (Hugging Face, 2026) | 1,719 items on address forms and kinship terms | test the judge prompt on আপনি, তুমি and তুই | CC BY 4.0 |
| SentNoB and NC-SentNoB (Hugging Face) | Bangladeshi social-media comments; NC-SentNoB labels local words, mixed language and spelling errors | slang meanings and insults (K3) | CC BY-ND, CC BY-SA |
| BanglaTLit, BnSentMix, BanglishRev | romanised and code-mixed comments and Daraz reviews | Banglish spellings and shares (§10; B1, B2) | MIT (BanglaTLit); see each card |
| Wiktionary via kaikki.org (updated 20 Sep 2026) | 11,227 Bengali entries tagged tatsama (1,062), Persian (1,085), English (541), literary, poetic, archaic, Bangladesh | 308 candidate tatsama to everyday pairs, noisy; filter by frequency | CC BY-SA |
| FrequencyWords (OpenSubtitles 2018, top 50k) | word frequencies | rank suggestions: কাজ 5,250 vs কার্য 8, শুধু 5,035 vs কেবল 713, মানে 2,483 vs অর্থাৎ 46 | CC BY-SA |
| Prothom Alo article dumps on Hugging Face (about 409k and 438k articles) | newspaper text | newspaper word frequency, internal only | the text is Prothom Alo's |
| Chakraborty, Nayeem and Ahmad (AAAI 2021), BengaliReadability | 618 NCTB textbooks, 96k sentences labelled simple or complex, a conjunct counter, 3,396 easy words | conjunct count and word length as a proxy for tatsama density; the easy-word list measures familiarity (it contains প্রদান and গ্রহণ), not register | MIT |
| Sinha et al. (COLING 2012) | Bangla readability score = -5.23 + 1.43 x average word length + 0.01 x polysyllabic words | a cheap readability number for body copy | paper |

Traps:
- Unicode: FrequencyWords mixes the precomposed য় (158,850 tokens) with য plus nukta (15,247). Normalise to NFC
  before any lookup (§1).
- The csebuetnlp normaliser is CC BY-NC-SA and cannot go into a commercial tool.
- Kinship and greeting words depend on the audience (Hindu and Muslim usage tables on English Wikipedia): never
  auto-replace them; copy.md keeps them as notes.
- No BBC Bangla style guide is public; the Anandabazar style book is useful only for contrast.

## 14. Calibration results

The 75 candidates in `bangla-casual.json` were run on every corpus. "Warning" counts texts with at least one
new warning; "any" counts texts with any new finding (note or warning).

| Corpus | Texts | New warning | Any new finding |
|---|---|---|---|
| Natural calibration lines (§16) | 50 | 0 | 0 |
| Earlier natural set (the 24 September copy.md study) | 47 | 0 | 0 |
| Brand ads, 2026 (8 brands) | 144 | 2 (1.4 %), both the দারুন misspelling | 15 (10 %), mostly the space-before-। note |
| Brand YouTube titles (15 brands) | 580 | 6 (1.0 %), all misspellings (নিশ্চই, মুহুর্ত) | 24 (4 %) |
| **Hold-out brand ads** (Banglalink, Shikho, PRAN, Walton, Kacchi Bhai; collected after the rules were fixed) | 102 | **0** | 6 (6 %): five space-before-। notes, one প্রতিটি ফোঁটায় |
| Market sample (word-biased) | 1,457 | 112 (7.7 %) | 416 (29 %) |
| Human news and textbook passages, voice rules only | 3,322 | 31 (0.9 %) | 131 (3.9 %) |
| The same passages paraphrased by ChatGPT, voice rules only | 3,322 | 288 (8.7 %) | 817 (24.6 %) |
| Robotic calibration lines (§16) | 50 | 28 (56 %) | 47 (94 %) |

With the existing lint: the robotic lines go from 8 of 50 with a warning (existing rules alone) to 32 of 50
(existing plus new), and 49 of 50 get at least one finding; the natural lines stay at 0 findings. The one robotic
line with no finding (এক অনন্য ও অসাধারণ অফার) is left to the judge, because the newspaper writes এক অনন্য 50
times. "Voice rules only" leaves out the punctuation and spelling checks (X1, X2, X3, X6), which fire on scraping
artefacts in the passage set.

Brand texts that trigger a new rule, all as notes except misspellings: Robi's আনলক করুন ... দুনিয়া and নিয়ে যান
নেক্সট লেভেলে, GP's আমরা বিশ্বাস করি (OneAI launch), Pathao Commerce's three এবং, a Shwapno Mela product page's
X করতে সাহায্য করে, Chaldal's প্রতিটি ফোঁটায় and প্রতিটি চুমুক, Walton's প্রতিটি ফোঁটায়, and the space-before-। slip.

**Candidate index.** The IDs used in this note, in the order of `bangla-casual.json` (the JSON has no ID field;
word and phrase entries match whole words with the usual case endings, as `BN_FORMAL` does):

| ID | Kind | Level | False-positive risk | Matches |
|---|---|---|---|---|
| P5 | structure | warning | low | stacked praise words (30-word set), 2 in a line or 3 in a caption |
| P1 | phrase | warning | low | স্বপ্নের ডানায় |
| P2 | phrase | warning | medium | হৃদয়ের গভীর থেকে |
| P3 | regex | note | medium | হৃদয় / মন ছুঁয়ে যাবে, যাক, দেবে |
| P4 | regex | note | medium | রাঙিয়ে দিন, তুলুন |
| S1 | regex | warning | low | "In today's busy world" opener |
| S2 | regex | warning | low | উত্তেজিত in the brand's voice |
| S3 | regex | warning | medium | আনন্দের সাথে জানাচ্ছি |
| S4 | regex | note | medium | আমরা গর্বিত, আনন্দিত |
| S5 | regex | note | low | জগতে স্বাগতম |
| S6 | regex | warning | low | you deserve it (প্রাপ্য, ডিজার্ভ) |
| S7 | regex | note | medium | অপরিহার্য অংশ, গুরুত্বপূর্ণ ভূমিকা |
| S8 | word | note | medium | নিঃসন্দেহে |
| S9 | regex | note | medium | করে তুলুন আরও |
| S10 | regex | note | medium | প্রতিটি কামড়ে, চুমুকে, ফোঁটায় |
| S11 | regex | note | medium | নেক্সট লেভেলে নিয়ে যান |
| S12 | regex | note | medium | আনলক করুন ... দুনিয়া |
| S13 | phrase | note | medium | সংযুক্ত থাকুন |
| S14 | regex | note | medium | স্বপ্নকে বাস্তবে রূপ দিন, সাফল্যের চাবিকাঠি |
| S17 | phrase | note | medium | অনুভব করুন |
| S48 | regex | note | medium | অসাধারণ, অনবদ্য অভিজ্ঞতা |
| S18 | phrase | note | medium | নিজেকে দিন |
| S19 | phrase | note | medium | আমরা বিশ্বাস করি |
| ESS | regex | warning | low | উপসংহারে বলা যায়, পরিশেষে বলা যায় |
| PRL | word | warning | low | পরিলক্ষিত |
| ATB | word | note | medium | অত্যাবশ্যক |
| SCF | structure | note | low | প্রথমত and দ্বিতীয়ত |
| F:উপলব্ধি করুন | phrase | warning | low | উপলব্ধি করুন |
| F:ভোজন করুন | phrase | warning | low | ভোজন করুন |
| F:উপস্থিত হোন | phrase | warning | low | উপস্থিত হোন |
| F:অবস্থান করুন | phrase | warning | low | অবস্থান করুন |
| F:নিম্নোক্ত | word | warning | low | নিম্নোক্ত |
| F:সত্বর | word | warning | low | সত্বর |
| F:তথাপি | word | warning | low | তথাপি |
| F:অত্র | word | warning | low | অত্র |
| F:আরম্ভ | word | warning | low | আরম্ভ |
| F:গৃহ | word | warning | low | গৃহ |
| F:তৈরিকৃত | word | warning | low | তৈরিকৃত |
| F:উপকৃত হোন | phrase | warning | low | উপকৃত হোন |
| F:বাহিরে | word | note | low | বাহিরে |
| F:বাছাইকৃত | word | note | medium | বাছাইকৃত |
| F:লাভ করুন | phrase | note | medium | লাভ করুন |
| F:হালনাগাদ | word | note | medium | হালনাগাদ |
| F:আহার | word | note | medium | আহার |
| F:UR | regex | note | low | টাকার ঊর্ধ্বে |
| F:NY | regex | note | medium | genitive + ন্যায় |
| F:GR | regex | note | medium | গ্রহণ করে, করতে, করলে |
| F:KRT | regex | warning | low | -কৃত on English loans |
| H1 | word | warning | low | কোনও |
| H2 | regex | warning | low | গিয়েছে, গিয়েছি, গিয়েছেন |
| H3 | regex | warning | low | reporting verb + যে (বলেছেন যে) |
| H4 | word | note | medium | দ্বারা |
| H5 | structure | note | low | এটি twice or more |
| H6 | regex | note | medium | X করতে সাহায্য করে |
| H7 | structure | note | medium | 3 or more এবং and no ও or আর |
| D1 | regex | warning | low | sadhu perfect (ি|ই)য়াছ |
| D2 | regex | warning | low | sadhu continuous িতেছ |
| D3 | regex | warning | low | কেহ, কাহার ... |
| D4 | regex | warning | low | বলিল, কহিল, এক্ষণে |
| D5 | regex | warning | low | যদ্যপি, নচেৎ, কিঞ্চিৎ, কুত্রাপি |
| K1 | regex | warning | low | Dhaka phonetic spelling (করতেসি, খাইসি) |
| K2 | structure | warning | low | three or more slang words |
| K3 | regex | warning | low | ক্ষ্যাত, আবাল, ফকিন্নি |
| K4 | word | warning | medium | হেব্বি |
| K5 | regex | note | low | চাপ নিও না |
| K6 | structure | note | low | two or more reaction words |
| K7 | structure | note | low | three or more particles in 30 words |
| B1 | structure | note | low | romanised Bangla detector |
| B2 | regex | note | low | naa, kee, 2mi, gr8 |
| GZ | structure | note | medium | rizz, bruh, skibidi in Bengali copy |
| X1 | regex | note | medium | space before । |
| X2 | regex | note | low | no space after । |
| X3 | regex | warning | low | misspellings (নিশ্চই, দারুন, মুহুর্ত, প্রানবন্ত, -ী on loans) |
| X6 | regex | warning | low | U+09F7 used as । |
| X4 | regex | warning | medium | greeting openers (প্রিয় শিক্ষার্থীরা ...) |

## 15. Keep, fix, or do not add

**Do not flag (real brands write it):**
- উপভোগ করুন once per piece: Nagad (7 and 10 Sep 2026), Robi, Banglalink (9 Sep 2026), Toffee, GP (13 Sep
  2026), Rokomari. The copy.md rule "at most once, never as the CTA" is right, but copyrules does not check it yet:
  implement it as a count (two or more in one piece: note) and a CTA-role warning.
- তাহলে আর দেরি কেন (Robi ad, 15 Sep 2026; Arogga), দেরি না করে (Robi 19 Jul 2026, Pathao, bKash, 10 Minute
  School): stale but human; leave them to the judge.
- জার্নি in Bengali script (GP ad, 10 Aug 2026; Pathao; PA 57 headlines): do not extend the যাত্রা rule to it.
- শুধুমাত্র (GP ad, 10 Sep 2026; Walton Plaza), সাথে (brands 35 times against সঙ্গে once in the ads), আরো (bKash,
  Pathao), নো টেনশন, টেনশন ফ্রি, হাতের মুঠোয়, এক ছাদের নিচে, স্বপ্নের ঠিকানা, মানেই, তো আছেই.
- অর্থাৎ (GP ad, 7 Apr 2026: অর্থাৎ প্রতি মাসের বিল ...), কেবল (PA 530 headlines), কার্য (কার্য দিবস, a job title),
  সহস্র and প্রাতে (song and programme titles), দিবেন and নিবেন (F-commerce everyday), মফিজ (a common name), খ্যাত
  (famous), flex (bKash, Aug 2026), দোস্ত (PRAN Toast's tea-time friend, Sep 2026).

**Fixes to existing checks:**
- Accept the colloquial -েন imperative in `BN_CTA_END` (§4).
- The engagement-bait rule fires on GP's nomination post "ট্যাগ করুন আপনার এলাকার ফুটবল স্টারকে!" (1 Jul 2026).
  Keep it (platforms demote tag requests either way), but the judge can pass a tag that nominates a named role.
- The visarga-colon warning fires on a bKash offer ad (Jul 2026). That is correct by Bangla Academy style; keep it.
- The `প্রতিটি মুহূর্ত` calque fires on Chaldal Shorts (2025): consistent with finding 4 in §2.
- Store every new list entry in NFC (§1).
- `BN_FORMAL` already holds প্রদান and অত্যন্ত; the human and ChatGPT pairs confirm both (4 times as frequent in the
  paraphrases), so keep them as warnings.

## 16. Calibration lines

Written for this study in the register of the brands above; not quotes. Each natural line passes the existing lint
and every new candidate with no finding at all.

**50 natural lines** (varied registers and sectors; line 39 uses one slang word, and lines 44 to 49 carry words that
real brands use and a careless lint would flag: নান্দনিক alone, সমাহার, এক ছাদের নিচে, হাতের মুঠোয়, শুভারম্ভ, প্রাইসে, দিবেন, আসেন):

1. বৃষ্টি নামলেই খিচুড়ির কথা মনে পড়ে? আজ রাত ১১টা পর্যন্ত খিচুড়ি কম্বো ৳২৪৯।
2. বাজার শেষ মাত্র এক ক্লিকে, ডেলিভারি পৌঁছে যাবে এক ঘণ্টায়।
3. মাসের শেষে টাকা টানাটানি? অ্যাপে বিল দিলেই ৳২০ ক্যাশব্যাক।
4. অফিস থেকে ফিরে রান্নার মুড নেই? থাক, আজ আমরাই রাঁধছি।
5. ঈদের পাঞ্জাবি কেনা বাকি? ৩০ রোজা পর্যন্ত সব পাঞ্জাবিতে ২০% ছাড়।
6. নতুন সিমে ৩০ দিন মেয়াদের ২০ জিবি, দাম মাত্র ২৯৮ টাকা।
7. সকালের নাস্তায় পরোটা আর ডিম ভাজি, অর্ডার করলে ২০ মিনিটেই হাজির।
8. পরীক্ষার আগের রাতে সব গুলিয়ে যাচ্ছে? এক ক্লাসেই পুরো সিলেবাস রিভিশন করে নাও।
9. জ্যামে বসে বসে বিরক্ত? বাইক ডাকুন, অফিসে পৌঁছান সময়মতো।
10. ইলিশের মৌসুম কিন্তু শেষের দিকে, পদ্মার ইলিশ কেজি ১,৪৫০ টাকা।
11. চুলায় ভাত বসিয়ে দিন, মাছ আর সবজি আমরা পৌঁছে দিচ্ছি।
12. গরমে ঘেমে একাকার? সুতি টি-শার্ট তিনটা মাত্র ৯৯০ টাকায়।
13. টাকা পাঠাতে এখন আর লাইনে দাঁড়াতে হবে না, অ্যাপেই সেন্ড মানি করুন।
14. ছুটির দিনে বাসায় বসে বোর? বাচ্চাদের নিয়ে চলে আসুন, প্লে জোন খোলা সকাল ১০টা থেকে।
15. প্রথম অর্ডারে ৫০% ছাড়, সর্বোচ্চ ১৫০ টাকা। কোড: FIRST50
16. সাইজ নিয়ে টেনশন নেই, না মিললে ৭ দিনের মধ্যে বদলে নিন।
17. মিরপুরে নতুন আউটলেট খুলছে শুক্রবার, প্রথম ১০০ জনের জন্য থাকছে ফ্রি কফি।
18. ফোনের চার্জ ১০%? পাওয়ার ব্যাংক ১০,০০০ mAh, দাম ১,২৫০ টাকা।
19. বিয়ের দাওয়াত আছে? শাড়ির সাথে মিলিয়ে গয়না বেছে নিন, দোকান খোলা রাত ৯টা পর্যন্ত।
20. বাবার জন্য কিছু কিনবেন ভাবছেন? আরামের স্যান্ডেল এখন ১,৪৯০ টাকায়।
21. রেজিস্ট্রেশনের শেষ দিন ৩০ সেপ্টেম্বর, ফি ৫০০ টাকা। লিংক কমেন্টে।
22. রং আর সাইজ ছবিতেই আছে, পছন্দ হলে ইনবক্সে কোডটা লিখে পাঠান।
23. চা ছাড়া আড্ডা জমে না, তাই প্রতি অর্ডারে এক প্যাক চা ফ্রি।
24. গ্যাস, বিদ্যুৎ আর পানির বিল, সব এক অ্যাপে। দিতে লাগে এক মিনিট।
25. কলেজ শুরুর আগে ইংরেজিটা একটু ঝালিয়ে নাও, ক্লাস শুরু ৫ অক্টোবর।
26. ঝাল কতটা চান? অর্ডারের সময় নোটে লিখে দিন।
27. এই শীতে কম্বল কেনার আগে একবার আমাদের কালেকশনটা দেখে যান।
28. লোডশেডিংয়েও ওয়াইফাই চলবে, রাউটারে ৪ ঘণ্টার ব্যাকআপ।
29. আপনার এলাকায় ডেলিভারি হয় কি না, কমেন্টে থানার নাম লিখুন।
30. ভর্তি চলছে! ক্লাস ৬ থেকে ১০, ব্যাচে সর্বোচ্চ ২০ জন।
31. ব্যাগ গোছানো শেষ? কক্সবাজারের বাসের টিকিট এখন অ্যাপেই, সিট দেখে বুক করুন।
32. বাচ্চার টিফিনে আর কী দেবেন ভাবছেন? চিকেন নাগেটস ৫০০ গ্রাম ৩২০ টাকা।
33. জ্যাম যতই থাকুক, খাবার গরম থাকবে। থার্মাল ব্যাগে ডেলিভারি।
34. আজ বিকেল ৫টায় লাইভে আসছি, নতুন কালেকশনের সব ড্রেস দেখাব।
35. ১০ বছরের পুরোনো ফ্রিজ? এক্সচেঞ্জ করলেই নতুনটায় ৮,০০০ টাকা পর্যন্ত ছাড়।
36. হাতে বোনা জামদানি, একেকটা শাড়ি বুনতে লাগে তিন মাস।
37. সিম হারিয়েছেন? নম্বর ঠিক রেখে নতুন সিম তুলুন যেকোনো কাস্টমার কেয়ার থেকে।
38. পূজার ছুটিতে বাড়ি যাচ্ছেন? বাসার ইন্টারনেট প্যাকটা পজ করে রাখুন, টাকা কাটবে না।
39. প্যারা নাই, সাবস্ক্রিপশন বাতিল করা যায় যেকোনো দিন।
40. মা বলেন, বাজারে পচা টমেটো গছিয়ে দেয়। আমরা প্রতিটা টমেটো হাতে বেছে পাঠাই।
41. দুপুরে কী খাবেন, এখনও ঠিক হয়নি? আজকের স্পেশাল কাচ্চি, ফুল প্লেট ৩৫০ টাকা।
42. ফ্রিল্যান্সিং শিখতে চাও? প্রথম ক্লাসটা ফ্রি, বসে দেখো তারপর ঠিক করো।
43. বসুন্ধরায় নতুন ফ্ল্যাট, ১,২৫০ বর্গফুট, হস্তান্তর ডিসেম্বরে।
44. নান্দনিক ডিজাইনের সোফা সেট, সাথে ৩ বছরের ওয়ারেন্টি।
45. হাজার বইয়ের সমাহার এক ছাদের নিচে, মেলা চলবে ২৮ তারিখ পর্যন্ত।
46. সব সেবা এখন হাতের মুঠোয়, অ্যাপটা নামিয়ে নিন ফ্রিতে।
47. শুভারম্ভ উপলক্ষে আজ সব আইটেমে ১০% ছাড়, চলে আসুন ধানমন্ডি ২৭-এ।
48. বেস্ট প্রাইসে জুতা, টাকা দিবেন ডেলিভারির সময়।
49. আসেন বুঝাই, ক্রেডিট কার্ডের বিল না দিলে সুদ কীভাবে বাড়ে।
50. অফারটা কিন্তু রবিবার রাত ১২টায় শেষ, পরে বললে পাব না!

**50 robotic lines** (1 to 10 poetic, 11 to 26 translated templates, 27 to 38 bookish, notice or sadhu, 39 to 44
forced or wrong-register casual, 45 and 46 Banglish, 47 to 50 other translation habits). With the existing and the
new rules, 32 get a warning and 49 at least a note; line 47 is left to the judge:

1. স্বপ্নের ডানায় ভর করে আপনার প্রতিটি মুহূর্ত হয়ে উঠুক অনন্য ও অবিস্মরণীয়।
2. হৃদয়ের গভীর থেকে জানাই আন্তরিক শুভেচ্ছা ও অফুরন্ত ভালোবাসা।
3. মনোমুগ্ধকর নকশা আর স্নিগ্ধ রঙের অপরূপ মেলবন্ধনে তৈরি আমাদের নতুন কালেকশন।
4. প্রকৃতির অপার সৌন্দর্যের মাঝে পান এক অনাবিল প্রশান্তি।
5. প্রতিটি চুমুকে ছড়িয়ে পড়ুক স্বর্গীয় স্বাদের জাদুকরী আবেশ।
6. আভিজাত্য আর আধুনিকতার অনবদ্য সমন্বয়ে সাজিয়ে তুলুন আপনার স্বপ্নের ঘর।
7. চিরন্তন ঐতিহ্যের ছোঁয়ায় রাঙিয়ে তুলুন আপনার উৎসবের প্রতিটি দিন।
8. এই ঈদে খুশির রঙে রাঙিয়ে দিন আপনার প্রিয়জনের মন।
9. মায়াবী রাতের স্নিগ্ধতায় হারিয়ে যান এক শিহরণ জাগানো আয়োজনে।
10. নয়নাভিরাম সৌন্দর্য আর মনোরম পরিবেশে আপনার ছুটি হয়ে উঠুক স্মরণীয়।
11. আজকের এই ব্যস্ত জীবনে সুস্থ থাকা সবার জন্যই জরুরি।
12. দ্রুতগতির এই পৃথিবীতে সময় বাঁচানোই এখন সবচেয়ে বড় চ্যালেঞ্জ।
13. আমরা ভীষণ উত্তেজিত আমাদের নতুন অ্যাপ আপনাদের সামনে আনতে পেরে।
14. আমরা আনন্দের সাথে জানাচ্ছি যে আমাদের নতুন শাখা চালু হতে যাচ্ছে।
15. সুস্বাদু খাবারের জগতে আপনাকে স্বাগতম।
16. কারণ সেরাটাই আপনার প্রাপ্য।
17. আপনার রান্নাঘরকে করে তুলুন আরও আধুনিক ও স্মার্ট।
18. ত্বকের যত্নে এটি একটি অপরিহার্য অংশ, যা আপনাকে দেবে উজ্জ্বল ত্বক।
19. সুস্থ জীবনের জন্য সকালের হাঁটা গুরুত্বপূর্ণ ভূমিকা পালন করে।
20. নিঃসন্দেহে এটি হতে চলেছে আপনার সেরা সিদ্ধান্ত।
21. প্রতিটি কামড়ে অনুভব করুন খাঁটি স্বাদের জাদু।
22. আপনার ব্যবসাকে নিয়ে যান নেক্সট লেভেলে।
23. আনলক করুন বিনোদনের এক নতুন দুনিয়া।
24. আমাদের সাথে সংযুক্ত থাকুন, নতুন আপডেট পেতে পেজটি ফলো করুন।
25. স্বপ্নকে বাস্তবে রূপ দিন, কারণ সাফল্যের চাবিকাঠি এখন আপনার হাতে।
26. এটি শুধুমাত্র একটি ব্যাগ নয়, এটি আপনার ব্যক্তিত্বের প্রতিচ্ছবি।
27. অদ্যই আপনার নিকটস্থ শাখায় উপস্থিত হোন।
28. নিম্নোক্ত নিয়ম মেনে আবেদন সম্পন্ন করুন।
29. সত্বর যোগাযোগ করুন, অন্যথায় অফারটি বাতিল বলিয়া গণ্য হইবে।
30. উক্ত পণ্যটি গৃহে বসিয়া ক্রয় করা যাইবে।
31. আমাদের রেস্তোরাঁয় আসুন এবং ঐতিহ্যবাহী খাবার ভোজন করুন।
32. তথাপি আপনার সন্তুষ্টিই আমাদের মূল লক্ষ্য।
33. বাছাইকৃত সুতা দ্বারা তৈরিকৃত এই পাঞ্জাবি আপনাকে দেবে আরাম।
34. ৫০০ টাকার ঊর্ধ্বে অর্ডারে গৃহে পৌঁছে দেওয়া হবে।
35. পণ্য হাতে পাইয়া মূল্য পরিশোধ করিবেন।
36. আমরা আপনাদের সেবায় নিরলসভাবে কাজ করিয়া যাইতেছি।
37. আমাদের সেবা নিয়ে উপকৃত হোন এবং অন্যদেরও জানান।
38. উপলব্ধি করুন আরামের এক নতুন মাত্রা।
39. ভাই জোস অফার, প্যারা নাই চিল, সেই লেভেলের ডিল, পুরাই আগুন!
40. উফ, আহা, ইশ, এমন অফার আর কোথায় পাবেন বলুন তো?
41. তো আজকে কিন্তু একটু অফারটা দেখেই যান না, তাই না?
42. সম্মানিত গ্রাহক, আপনার কিস্তি জমা দিতে দেরি করতেসেন কেন?
43. ক্ষ্যাত লোকেরা এই ড্রেস পরে না, তুমি তো স্মার্ট!
44. হেব্বি অফার চলছে, একদম চাপ নিও না!
45. Offer sesh hobar age order korun, dam matro 499 taka!
46. Apnar pochonder product ekhon pacchen 20% discount e!
47. আমরা আমাদের প্রিয় গ্রাহকদের জন্য নিয়ে এসেছি এক অনন্য ও অসাধারণ অফার।
48. অফারটি গ্রহণ করে আপনার দিনটিকে করে তুলুন আরও আনন্দময় এবং স্মরণীয়।
49. প্রিয় বন্ধুরা, আমাদের নতুন কালেকশন এখন বাজারে।
50. আজই সংগ্রহ করুন এবং উপভোগ করুন এক অসাধারণ অভিজ্ঞতা এবং অতুলনীয় মান।

## 17. Sources (all read 2026-09-24)

**Brand YouTube titles** (upload dates from yt-dlp):
- bKash, 2026-09-07, Credit Card explainer Short (আসেন বুঝাই; নিশ্চই): https://www.youtube.com/watch?v=34GG2VfCvkY
- bKash, 2026-08-31, BTEB fee Short (টেনশন ফ্রি): https://www.youtube.com/watch?v=Nq9EmewsZ4Y
- bKash, 2026-08-13, Debit or Credit Short (no space after ।): https://www.youtube.com/watch?v=eWTQADS6nqM
- bKash, 2026-08-10, দুলাভাই buying on credit: https://www.youtube.com/watch?v=Ebm1nHSksBo
- bKash, 2026-06-04, football debate (তুমি: কমেন্টে জানাও): https://www.youtube.com/watch?v=Sr5lBKsCjF0
- bKash, 2026-05-01, Eid rhyme: https://www.youtube.com/watch?v=e-Pf023WtUg
- Grameenphone, 2026-07-01, football-star nomination (ট্যাগ করুন): https://www.youtube.com/watch?v=pGe3b0EHqH0
- Grameenphone, 2026-05-12, সাবধানের মাইর নাই: https://www.youtube.com/watch?v=3f-oUxrQkEI
- Robi, 2026-09-15, Bowler Hunt 2026: https://www.youtube.com/watch?v=IJaSNkbbngY
- Robi, 2026-08-20, আসছে সাফ, পারবে তুমিও: https://www.youtube.com/watch?v=_BA0rO2tQPU
- Banglalink, 2026-08-06, Internet Jokhon Hoye Uthe Sritir Thikana: https://www.youtube.com/watch?v=PH5M0STM8wU
- Banglalink, 2026-05-27, আপনি যেখানে, বাংলালিংক সেখানে: https://www.youtube.com/watch?v=kb3Zhcap2lY
- Banglalink, 2026-04-14, Pohela Boishakh greeting: https://www.youtube.com/watch?v=53Ql0J84MdI
- Banglalink, 2026-03-02, first-rain greeting: https://www.youtube.com/watch?v=WIu80sZtPGc
- Banglalink, 2025-03-29, শুনতে কি পাও?: https://www.youtube.com/watch?v=IC-bPRgaJP0
- Pathao, 2026-06-28, Safe থাকি, Safe রাখি: https://www.youtube.com/watch?v=fIVPfa-GaqU
- Pathao, 2026-03-01, Relax-এ travel করুন: https://www.youtube.com/watch?v=gvQiIAt0kt8
- Pathao, 2022-02-12, জোস ডিলে কিস্তিমাৎ! (and Gxz2vWOB78A, 2022-02-03, জোশ): https://www.youtube.com/watch?v=ku6kVv5UZKc
- Shikho, 2026-05-19, রাগ করলা ?: https://www.youtube.com/watch?v=2-i_s0T4GTg
- Shikho, 2026-04-19, শেষ মুহুর্তের চারটি উপদেশ: https://www.youtube.com/watch?v=-2FzDZdHLC8
- 10 Minute School, 2026-03-01, Dana Vai: https://www.youtube.com/watch?v=knayJHLoU5E
- 10 Minute School, 2025-04-20, প্যারাহীন IELTS Speaking Test: https://www.youtube.com/watch?v=6z6yPVptGjY
- Chaldal, 2026-01-05, কর্মব্যস্ত জীবনে: https://www.youtube.com/watch?v=gQajKkgB99c
- Chaldal, 2025-11-17, প্রতিটি ফোঁটায়: https://www.youtube.com/watch?v=eTe4ZKWaKVc
- Chaldal, 2025-11-07, শুধু পণ্য নয় (AI-flavoured): https://www.youtube.com/watch?v=fXf41CO-eaw
- Chaldal, 2025-10-13, চালডাল তো আছেই: https://www.youtube.com/watch?v=27VpJ6WGnwM
- Chaldal, 2025-07-11, প্রতিদিন হোক প্যারাহীন: https://www.youtube.com/watch?v=iyyt7nwsx2o
- Chaldal, 2025-06-28, প্রতিটি চুমুক: https://www.youtube.com/watch?v=fpK9b7XgV8s
- foodpanda, 2025-08-31, ডিলের স্বাদে চিল করো: https://www.youtube.com/watch?v=u-12zeo83dQ
- foodpanda, 2024-12-15, foodpanda তো আছেই: https://www.youtube.com/watch?v=s33Uq_aOMb4
- foodpanda, 2023-10-05, Khela hobe: https://www.youtube.com/watch?v=kg1KdU4mCXM
- Nagad, 2023-09-21, সেই লেভেলে: https://www.youtube.com/watch?v=shKpIcE6UvA
- Airtel (now Cirkle), 2024-12-01, ইন্টারনেটের প্যারা: https://www.youtube.com/watch?v=TsHJjdihrUg
- Daraz, 2023-10-31, Shobai Ekhon Phone e?: https://www.youtube.com/watch?v=Et1nE_WMkd8
- Sheba.xyz, 2025-01-27, ড্রাইভার গায়েব?: https://www.youtube.com/watch?v=k1dWf3iFihU
- Bata, 2024-02-07, ভাগ ব্যাকটেরিয়া ভাগ: https://www.youtube.com/watch?v=Miic9Sau1iQ

**Meta Ad Library, Bangladesh, active ads** (https://www.facebook.com/ads/library/, keyword and advertiser search;
dates are the ads' start dates): bKash Limited (16 Sep, 3 Sep, 27 Aug, 16 Jul 2026; Amar bKash 24 Aug 2026), Nagad
(7, 9 and 10 Sep 2026; Nagad Islamic 16 Sep 2026), Pathao Courier (30 Jul 2026), Grameenphone (2 Feb, 10 Aug, 31
Aug, 7, 9, 10 and 13 Sep 2026), Robi (19 Jul, 2, 4 and 10 Aug, 31 Aug, 1, 6, 15 and 19 Sep 2026), Banglalink
Digital (9 Sep 2026), Shwapno (20 and 21 Sep 2026), foodpanda (13 May 2026; partner BD 29 Jun 2026; riders 18 Sep
2026), Toffee (2 Sep 2026), PRAN UP (16 Sep 2026), PRAN Junior (14 Sep 2026), Vim Bangladesh (7 Sep 2026), Domex
Bangladesh (7 Sep 2026), 10 Minute School (25 Aug 2026), Red Cow (27 Aug 2026), Ispahani Mirzapore Tea (7 Sep
2026), Polar Ice Cream (5 Sep 2026), HATIL (14 Feb 2026; HATIL Bashundhara 21 Jul 2026), RFL Building Hub (6 Sep
2026), RFL Best Buy (13 Sep 2026), Walton Plaza (10 and 13 Sep 2026), Walton Computer (7 Sep 2026), Walton dealer
pages (22 Sep 2026), Rokomari.com (12 Aug and 6 Sep 2026), Pureit Bangladesh (Aug 2026), Praava Health (Feb 2026),
Retina (18 Aug 2026), Panjeree (29 Apr and 7 Jul 2026), Naturo (27 Jun 2026), Arogga (Mar 2026), UCB SME (16 Sep
2026), MetLife Bangladesh (9 Nov 2025), Tapmad (11 Aug 2026), Shosti Food (6 Aug 2026), Crystal Melamine (12 Jul
2026), Ruposi Bangla Tourism (3 Jun 2026).

**Prothom Alo headlines** (search API https://www.prothomalo.com/api/v1/search, exact phrase; counts in §5 to §9):
- 2026-09-20: ‘ওয়াও! তুই কখন আসলি?’ (তুই inside a quote), https://www.prothomalo.com/bangladesh/district/bbiwiy7u9p
- 2026-09-03: a minister quoted with হারপিকটা নিয়ে আসেন (colloquial আপনি), https://www.prothomalo.com/bangladesh/district/sj9oqsc5jz
- 2026-08-25: ‘মধু হই হই’ খ্যাত জাহিদ (খ্যাত = famous), https://www.prothomalo.com/video/entertainment/8f1667oudw
- 2026-08-04: মাথা নষ্ট অ্যাকশন (slang in an entertainment headline), https://www.prothomalo.com/entertainment/world-cinema/rcg7wvgoy4
- 2026-06-20: সালিসে উত্তেজিত এমপি (উত্তেজিত = agitated), https://www.prothomalo.com/bangladesh/district/rysjdxdg3y
- 2026-05-23: ডিজার্ভ in a first-person quote, https://www.prothomalo.com/video/entertainment/qjzklwlmjq
- 2025-10-04: মানুষ অফিস নিয়ে এত প্যারা খায় কেন (fun section), https://www.prothomalo.com/fun/03mn1camk5
- 2025-07-06: মন ছুঁয়ে গেল (review), https://www.prothomalo.com/entertainment/bollywood/ybnqazbeo8
- 2024-05-14: ডিজার্ভ in a first-person quote, https://www.prothomalo.com/sports/cricket/68fa0v5122
- 2023-03-30: উত্তেজিত জনতা, https://www.prothomalo.com/world/pakistan/oh7a2gmizf
- 2022-05-09: খাইসি inside a quoted remark, https://www.prothomalo.com/video/bangladesh/পেঁয়াজ-ছাড়া-তরকারি-খাইসি-এখন-তেল-ছাড়া-খাই
- 2018-06-09: ছুঁয়ে যাক in an Eid wish, https://www.prothomalo.com/ঈদের-স্বর্গীয়-আনন্দ-সবাইকে-ছুঁয়ে-যাক

**Readers, researchers and reporting:**
- Bangla Samagra, 16 May 2026: https://banglasamagra.com/news/how-to-understand-ai-content
- Bigganchinta, Riton Khan, 29 Aug 2026: https://www.bigganchinta.com/technology/si8etx5umu
- The Daily Star, "Bangla in the age of algorithms", 21 Feb 2026: https://www.thedailystar.net/slow-reads/slow-reads-special/news/bangla-the-age-algorithms-4110631
- Prothom Alo opinion, Nadim Mahmud, 20 Jan 2023: https://www.prothomalo.com/opinion/column/29mmae1mty
- Prothom Alo, Mostofa Tanim, 4 May 2023: https://www.prothomalo.com/onnoalo/treatise/96s5rj5zmz
- AnswerPointBD, 9 Dec 2025: https://answerpointbd.com/bangla-ai-text-humanizer/
- FactWatch, 18 May 2026: https://www.fact-watch.org/azhari_deepfake/ ; Rumor Scanner, 13 Aug 2026: https://rumorscanner.com/fact-check/mahfuz-anam-said-raw-prevent-bangladesh-from-joining-the-mecca-pact-ai-video/214970
- BLADE, arXiv 2605.22487 (May 2026): https://arxiv.org/abs/2605.22487
- BanglaSocialBench, arXiv 2603.15949 (Apr 2026): https://arxiv.org/abs/2603.15949
- Bangla idioms and LLMs, arXiv 2609.03410 (3 Sep 2026): https://arxiv.org/abs/2609.03410
- TigerLLM, ACL 2025: https://aclanthology.org/2025.acl-short.69.pdf
- The Daily Star, Badiuzzaman Bay, 30 Jan 2018: https://www.thedailystar.net/opinion/perspective/banglish-ban-and-our-dangerous-obsession-force-1527367
- Bengali Language Implementation Act 1987, section 3: http://bdlaws.minlaw.gov.bd/act-705/section-29350.html

**Banglish and colloquial datasets:**
- BanglaTLit (EMNLP Findings 2024): https://huggingface.co/datasets/aplycaebous/BanglaTLit ; https://aclanthology.org/2024.findings-emnlp.859.pdf
- BnSentMix (2025): https://huggingface.co/datasets/aplycaebous/BnSentMix
- BanglishRev (Daraz reviews, collected 2024): https://huggingface.co/datasets/BanglishRev/bangla-english-and-code-mixed-ecommerce-review-dataset ; https://arxiv.org/abs/2412.13161
- SentNoB (EMNLP Findings 2021): https://huggingface.co/datasets/khondoker/SentNoB
- Bari, Adnan and Sadeq, arXiv 2606.16387 (15 Jun 2026): https://arxiv.org/abs/2606.16387
- YouTube: Rtv News Gen Z explainer https://www.youtube.com/watch?v=XQDHTEMtq0w ; Prothom Alo Gen Z explainer https://www.youtube.com/watch?v=t3AXeD5s8lg ; Ujan TV satire (2026-06-17) https://www.youtube.com/watch?v=CXXHS4iXlYM ; seller tutorial (2026-08-20) https://www.youtube.com/watch?v=DnZnwhnMq6c ; natok titles https://www.youtube.com/watch?v=J-o9j4OAP7c and https://www.youtube.com/watch?v=SIPLqJReqc8
