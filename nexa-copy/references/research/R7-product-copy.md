# R7: Product titles and descriptions that rank and convert (2024 to 2026)

Research date: 2026-09-26. Scope: titles, short copy (bullets, highlights, key features), long descriptions and feed fields on Amazon, Google Merchant Center, Shopify, Etsy, eBay, Walmart, Daraz and Lazada/Shopee. Bracketed numbers point to the source list. **[unverified]** marks items not confirmed on a primary page in this run (seller login or bot protection). Most platform pages carry no update stamp: treat every limit as "true on 2026-09-26" and re-read at job time.

## 1. Key findings

1. **Amazon titles are now 75 characters** (all types except media), plus a 125-character "item highlights" field [1][2]; the January 2025 symbol and repetition rules still apply [11]. Guides saying 200 are stale; one tracker dates enforcement to 27 July 2026 [13, unverified].
2. **The same title junk is banned everywhere**: promo phrases, boasts ("best seller", "top rated"), all caps, symbols, prices, shipping and time words [1][16][29].
3. **AI text carries duties**: Google wants it flagged in `structured_title` / `structured_description` [16][17]; Walmart makes sellers substantiate it and bans fabricated reviews [29].
4. **Assistants read the page**: Amazon's Alexa for Shopping (Rufus merged in) answers questions from detail-page data [10]; Google's `question_and_answer` attribute targets AI Mode [20].
5. **Facts beat fluff**: every Baymard test user relied on descriptions, yet many found them bland [39]; objective text tested 27% more usable than promotional text [45].
6. **Missing specs lose sales**: materials, labelled dimensions, exact compatibility, box contents [38]; 83% of desktop apparel sites lack enough sizing information [41].
7. **Returns and fit are pre-purchase questions**: 60% look for the return policy on the product page [37]; size and fit are what apparel shoppers most seek in reviews (48%) [42].
8. **Claims carry the legal risk**: health, eco, origin, comparison and guarantee wording needs evidence or removal; the EU ban on generic green claims applies from 27 September 2026 [52][53].

## 2. Platform rules

### 2.1 Limits at a glance

| Platform | Title | Short copy | Long description | Hidden keywords |
|---|---|---|---|---|
| Amazon (all stores except SA, EG, TR, AE; media exempt) | 75 chars; no `! $ ? _ { } ^ ¬ ¦`; a word max twice [1][11] | Item highlights 125 chars [2]; min 3 bullets, up to 5, limits per product type [3][6] (2024 rule: 10 to 255 [12]) | Paragraphs, no HTML except line breaks [2]; 2,000 chars [13, unverified] | Under 250 bytes; spaces and punctuation not counted [5][7] |
| Google Merchant Center | 150; about the first 70 are seen [16] | Highlights 2 to 100, 150 chars each, 4 to 6 advised [18]; Q&A up to 30 pairs, 1,000 chars each [19] | 5,000; key facts in first 160 to 500 [17] | None; keyword lists banned [18] |
| Shopify (own site) | SEO title 70, aim for 60 [21] | Meta description about 160 [21] | Theme-dependent | n/a |
| eBay | 80 [25] | Item specifics [26] | Site language, no symbols [27] | n/a |
| Walmart (US) | Max 150 [29]; 50 to 75 advised [31] | Key features 3 to 10, 80 chars each [29] | One paragraph, 150+ words, no bullets [29] | n/a |
| Etsy | 140 [unverified]; `% : & +` once each [23] | 13 tags of 20 chars [unverified] | Free text | Tags |
| Daraz, Lazada, Shopee | Behind seller login [unverified] | Highlights plus attributes [32] | Free text | n/a |

### 2.2 Amazon

**Title** [1][2][11]: brand, flavor or style, product type, key attribute, color, size or pack count, model number. Numerals ("2-Pack"), abbreviated units, title case with small words lowercase, standard letters only; no "Hot Item" or "Best seller", no all caps, no "FSA/HSA eligible". Size and color go in child titles, never the parent. With brand "generic", no brand in the title. Non-compliant titles may be auto-corrected or dropped from search [1] (rewritten by AI, per [13], unverified).

**Item highlights** [1][2]: 125 characters of comma-separated phrases shown under the title. Keep the most important variant attributes in the title; move the rest here.

**Bullets** [3]: "Header: description" (Amazon's example: "Cotton fabric: Made from 100% cotton for softness and breathability"); fragments, no end punctuation, semicolons inside; spell out one to nine except in names, model numbers and measurements; a space between number and unit ("60 ml"); no brand stories; minimal overlap with title and description; no subjective, performance or comparative claims unless verifiable on packaging; no unsupported awards or survey results; no competitor comparisons. Banned: ™ ® € … † ‡ ¢ £ ¥ © ± ~ â, emojis, placeholders (N/A, TBD), ASINs, "eco-friendly", "environmentally friendly", "ecologically friendly", "anti-microbial", "anti-bacterial", "made from" or "contains" bamboo or soy, guarantee phrases, company info and links, repeats, all caps, abbreviations (qty, pkg, w/, approx.), and fabric, care or origin (they have their own fields).

**Description and page rules** [2][6]: paragraphs on use, benefits, specs and applications. Not allowed in titles, bullets, descriptions or images: contact details, URLs, price, availability, condition, shipping offers, reviews, quotes, testimonials, review requests or dated information. Amazon may ignore description and bullet text for retrieval when it looks irrelevant or manipulative [6].

**A+** [4]: awards need year and awarding body and must be under 2 years old; "certified", "tested", "proven" and similar need the body or study and year; "eco-friendly", "biodegradable", "compostable" banned, "recyclable" needs a note; no "#1 rated", "top-rated", "best-selling", satisfaction guarantees, disease claims, warranty or return text, shipping, price or promo words ("affordable", "free", "buy now"), or "new" outside the brand story; charts compare only the brand's own products or categories (LED vs halogen); at most four quotes, from known publications or public figures, with author and date; photorealistic AI-generated people must be tagged.

**Search terms** [5][6][7]: under 250 bytes; synonyms, abbreviations, lowercase, no repeats or articles, singular or plural (not both), spelling variants but **not** common misspellings (many guides still advise them). Banned: any brand name, ASINs, profanity, temporary words (new, on sale), subjective words (best, cheapest, amazing, popular).

**Machine readers**: Alexa for Shopping answers questions such as dimensions or washability from the detail page [10]; Amazon's COSMO graph links products to audiences, functions and places of use (slip-resistant shoes for pregnant shoppers) [14]. Most early testers of Amazon's 2023 listing generator used its text directly [15]: review gates matter.

### 2.3 Google Merchant Center

Titles [16]: key details first, brand when it differentiates, variant details (color, size, flavor) in the title and in attributes; no promo text (price, sale, shipping, dates, company name), no caps for emphasis, no gimmicky characters. Google may rewrite titles from the landing page; if both `title` and `structured_title` arrive, it uses `title`. Descriptions [17]: consistent with the feed, no links, no comparisons with other products. `product_highlight` carries benefits and `product_detail` verifiable specs; neither may list keywords or repeat other fields [18]. `question_and_answer` is meant for conversational surfaces such as AI Mode and bans prices, dates and keywords [19][20].

Warning sample: Google's own example of an AI-generated title is "Stride & Conquer: Original Google Men's Blue & Orange Power Shoes (Size 8)" [16]. A pun, a colon and "Power" wrapped around a plain product: the pattern our skill must never produce.

### 2.4 Shopify (own site)

SEO titles up to 60 characters (70 allowed) with the main keyword early, meta descriptions about 160, keywords inside readable sentences [21]. Shopify's 2026 guide: write to one buyer, lead with benefits, swap clichés like "high quality" for specifics, prove superlatives, use sensory words and social proof, keep it scannable [22]. Own sites may show reviews, guarantees and return summaries that marketplace fields ban.

### 2.5 Etsy

The API allows letters, numbers, punctuation and ™ © ® in titles, with `%`, `:`, `&` and `+` once each [23]. The 140-character title, 13 tags of 20 characters, and Etsy's 2023 to 2025 push toward short readable titles with tags and attributes carrying variants are **[unverified]**: Etsy's help center blocks automated readers [24].

### 2.6 eBay

"Use all 80 characters and focus on relevant keywords"; eBay's sample titles run brand, model, capacity, color, lock status, grade [25]. Condition must match across title, description and item specifics; symbols become words ("Copyright", not ©); descriptions use the site's language; "Made in USA" claims must meet FTC rules [27]. No unrelated keywords, no comparisons with other products, no keywords with question marks (leave unknowns out), "fits" or "compatible with" before a compatible brand, one product per listing [28]. New in 2026: standardized apparel and footwear sizes from June; listings with missing or unclear size or condition may be hidden from August [26].

### 2.7 Walmart Marketplace

Title [29]: max 150, proper capitalization, key values ("5 in", "4 count"); banned: all caps, `~ ! * $`, promo claims (free shipping, hot sale, top rated, premium quality, best-selling, clearance, savings, low price), retailer names, stock status, URLs, non-English words, years unless standard for the type, repeats. Description: one paragraph of 150+ words, no bullets or emojis, no "Amazon exclusive", no authenticity claims without approval. Key features: 3 to 10, most important first, 80 characters max. AI text must match the delivered product, limitations included, and the seller must substantiate it. One or two primary keywords, once per field [30]. Canada: 50 to 75 characters, ordered brand, item name, model, style, key attribute, pack count, size [31].

### 2.8 Daraz, Lazada, Shopee

Daraz University stresses correct titles, images, category tags and descriptions built on attributes and highlights [32]; offers an AI title tool fed by product details and search trends (Jan 2026) [33]; forces variations instead of near-duplicate listings and bans reusing titles, descriptions or images for a second listing (Apr 2026) [34]; adds size charts to cut size-related returns (Apr 2026) [35]; and ties images to local cultural rules (Jul 2026) [36]. Field limits for all three platforms sit behind seller login **[unverified]**.

## 3. What shoppers look for

- **Descriptions decide.** Every Baymard test user relied on the description at some point; "feature dumps" got skipped, and descriptions chunked by highlight (header, image, short text) drew deeper reading; 78% of sites lacked them (2018) [39].
- **Gaps cause abandonment and returns.** 10% of large sites lacked consistently detailed descriptions (2021). Users sought materials or ingredients (50% of beauty shoppers needed ingredients), labelled dimensions in two unit systems, exact compatibility down to model number, box contents, and explanations of icons shown in images [38].
- **Specs must scan.** 50% of sites had hard-to-scan spec sheets: group specs, lead with key specs (3% did), use one column (2018) [40].
- **Size.** 42% of users judge size from images [37]. 83% of desktop and 87% of mobile apparel sites lack sufficient sizing information; supply conventional and numeric sizes, cm and inches, conversions, how to measure, and the model's measurements and size worn (2022) [41]. Size accuracy and fit top what apparel shoppers seek in reviews (48%, 2026) [42].
- **Returns.** 60% look for the policy on the product page, 44% of sites neither show nor link it, and 15% of shoppers abandoned an order over a poor policy [37]. US returns were projected at $890 billion, 16.9% of 2024 sales [47].
- **Questions.** 40% of test users used community Q&A when present; site FAQs plus community Q&A worked best (2017) [43].
- **Style.** NN/g asks for pages that are "complete, but not wordy or fluffy", gist first, jargon explained, same facts across variants (2019) [44]. Its 1997 test found concise, scannable and objective text 58%, 47% and 27% more usable than promotional copy, 124% combined [45]. In service conversations, one standard deviation more concrete wording went with about 30% higher spending [46]: a different setting, the same direction.

**Bullets or paragraphs?** The field decides (Amazon bullets [3], Walmart one paragraph [29], Google split fields [18][19]); research favors labelled chunks over walls of text [39][40][45]. Where a paragraph is forced, write one topic sentence per idea, facts first.

## 4. Writing craft

### 4.1 Feature, benefit, outcome, proof, limit

| Step | Example (insulated bottle) |
|---|---|
| Feature | Double-wall 18/8 stainless steel, vacuum sealed |
| Benefit | Keeps drinks cold |
| Outcome | Ice still there at the end of a 10-hour shift |
| Proof | Cold for 24 h in a 22°C room (maker's test) |
| Limit | Hand wash only; not dishwasher safe |

Outcomes and proofs are claims: without a test in the brief, stop at the benefit [8][29].

### 4.2 Specs people search and ask for

| Category | State these | Questions to answer |
|---|---|---|
| Fashion | Size range and system, fit, fabric %, weight or stretch, care, length or rise, model's size worn | Will it fit? See-through? Shrink? |
| Electronics | Model number, exact compatibility, W, mAh or GB, standard or version, battery life with test conditions, size, weight, box contents | Works with my device? How long? |
| Beauty | Skin or hair type, actives with %, full ingredients, volume, fragrance status, texture, use | Will it irritate? What is in it? |
| Food | Net weight, ingredients, allergens, origin, process, storage, shelf life | Fresh? Real? Safe for me? |
| Home | Overall and part dimensions, material, weight limit, cleaning, assembly, set contents | Fits my space? Easy to clean? |
| B2B | Part number, standard (DIN, ISO), grade, tolerances, pack quantity, documents | Meets spec? Paperwork? |

Basis: Baymard [38][41], eBay item specifics [25], Amazon title order [1]; the per-category lists are editorial.

### 4.3 Keywords without stuffing

- Product type plus the one or two searched attributes inside the first 70 characters: about what Google shows [16] and nearly all Amazon allows (75) [1].
- Each primary keyword once per field [30]; synonyms and alternate names go to hidden fields (Amazon generic keywords, Etsy tags), never visible copy [5].
- Write the phrase buyers say ("wireless earbuds"), then describe. Stuffed text may not be indexed [6] and can hurt ranking [31].

### 4.4 Voice by category (editorial)

- **Fashion**: tactile but checkable (fabric weight, stretch, lining), fit facts, occasions only when specific.
- **Electronics**: numbers with conditions, compatibility lists, no hype.
- **Beauty**: calm look-and-feel language, no drug verbs (treat, cure, repair, heal), say who it is not for.
- **Food**: origin, process, taste through concrete comparisons, storage, no health promises.
- **Home**: dimensions plus living-with details (cleaning, how it ages).
- **B2B**: spec-sheet voice, standards and documents, few adjectives.

### 4.5 Sensory language

A sensory word must point at something checkable on arrival: "soft" becomes "brushed inside, 280 gsm fleece"; "crisp" becomes "percale weave". Shopify recommends sensory words [22], NN/g measured promotional style as less usable [45], and A+ bans boasts [4]: sensory detail yes, decorative adjectives and metaphors no.

### 4.6 Limits, FAQs, social proof

- **Limits**: one honest boundary per listing where relevant (care, fit quirk, excluded models, what is not in the box); Walmart expects limitations to match the product [29].
- **FAQs**: answer the category's top five questions; send them as Google `question_and_answer` [19][20]; on own sites pair FAQs with community Q&A [43].
- **Social proof**: marketplaces ban reviews, quotes and testimonials in titles, bullets, descriptions and images [2]; A+ allows up to four sourced quotes and awards under two years old [4]. Since 21 October 2024 the FTC rule bans fake or AI-generated reviews and undisclosed insider reviews [57][58]. Never invent ratings, counts or "customers love it".

## 5. Compliance

**Health, beauty, supplements.** The FTC's December 2022 guidance expects competent and reliable scientific evidence, generally randomized controlled human trials, for health benefit claims, judged on the net impression of names, images and text [48]. Claims decide whether a cosmetic is a drug: restoring hair growth, reducing cellulite, treating varicose veins, changing melanin, regenerating cells, antidandruff and antiperspirant are drug claims [49]. Supplement structure/function claims need substantiation, FDA notification within 30 days, and a disclaimer that FDA has not evaluated the claim and the product is "not intended to diagnose, treat, cure, or prevent any disease" (exact text: 21 CFR 101.93) [50]. Amazon bans disease claims (its list includes arthritis, cancer, COVID-19, depression, diabetes, flu, obesity), anti-bacterial, anti-fungal and anti-microbial claims, and restricts "FDA approved" or "FDA cleared" [8].

**Environmental.** Amazon requires evidence and points to the FTC Green Guides and California's Environmental Marketing Claims Act [8][9]. The Green Guides date from 2012; a review opened in December 2022 and no revision is posted [51]. EU Directive 2024/825 applies from 27 September 2026 [53] and bans generic claims such as "environmentally friendly", "natural", "biodegradable", "climate neutral" or "eco" without proof, offset-based neutrality claims, labels outside certification schemes and unfounded durability claims [52]. The UK Green Claims Code wants claims truthful, clear, complete, fairly compared, life-cycle aware and substantiated [54]. Write scoped facts: "Bottle body: 50% recycled PET (certificate in brief); cap is virgin plastic."

**Made-in claims.** Unqualified "Made in USA" means all or virtually all US content; qualified forms and "Assembled in USA" have their own tests; the 2021 labeling rule reaches online promotion [55]. Amazon requires an attestation and calls "Made in Italy" misleading for a product only assembled there [8][9]; eBay demands proof [27]. Treat every origin claim, "Made in Bangladesh" included, the same way (editorial).

**Comparisons, superlatives, guarantees.** The FTC accepts truthful comparative advertising [56], but marketplace fields forbid it [3][4][17][18][28][29]. "Best", "100% pure" or "twice as effective" need objective proof [8]. "Money-back guarantee" commits to full refunds for any reason; material, filling, purity and technical claims (cashmere, down, 100% natural, thread count, drive capacity) need proof on request [9].

**Bangladesh.** Deceiving buyers with false or untrue advertising is punishable by up to one year in prison, a fine up to Tk 2 lakh, or both (Consumer Rights Protection Act 2009, s.44) [59]. The Ministry of Commerce's Digital Commerce Operation Guidelines 2021 set disclosure duties (product details, price, delivery time, return and refund terms) **[unverified: official text unreachable in this run]**.

## 6. Bangla and Bangladeshi commerce

Verified: the Daraz policies in 2.8 and s.44 above. Practice notes (editorial, **[unverified]**):

- Show the price with ৳ in the post; "দাম জানতে ইনবক্স করুন" hides what buyers need and clashes with disclosure duties.
- State delivery charge inside and outside Dhaka, delivery time, cash on delivery and the return window.
- Replace "১০০% অরিজিনাল" or "সেরা মানের" with checkable facts: origin, harvest or batch date, warranty card, size chart.
- Write everyday চলিত Bangla, keep the English words buyers use (size, cotton, charger), and use one digit system per post.

## 7. Failures and AI tells

Grounded in NN/g's "marketese" penalty [45], Baymard's "bland" finding [39], Shopify's cliché warning [22], Walmart's AI rules [29] and Google's AI title sample [16]; the phrase list is editorial.

- **Openers**: Introducing, Elevate your, Experience the, Discover, Say goodbye to, Look no further.
- **Empty praise**: premium quality, high-quality materials, perfect for any occasion, perfect gift, must-have, game-changer, next level, ultimate, revolutionary, designed with you in mind, crafted with care, timeless, seamless, effortless, unleash, boasts.
- **Shapes**: "Whether you're X or Y", "not just X, it's Y", rhetorical questions, three-adjective stacks, pun-plus-colon titles, emoji bullets, ALL CAPS headers, em dashes.
- **Repetition**: the title restated as bullet one and sentence one [3].
- **Stuffing**: synonym chains, every phone model listed, repeated keywords [1][28][31].
- **Invention**: tests, certifications, ratings or awards not in the brief [29][57].
- **Leftovers**: placeholders (N/A, TBD) [3]; AI refusal messages published as Amazon product names, widely reported in January 2024 **[unverified in this run]**.
- **Vague audience**: "for men and women of all ages".

## 8. Templates

### 8.1 Titles (dummy brand "BrandCo"; counts include spaces)

| Category | Template | Example | Chars |
|---|---|---|---|
| Apparel (Amazon child) | Brand + department + material + type, color, size | BrandCo Women's Merino Wool Crew Neck Sweater, Navy, Medium | 59 |
| Electronics | Brand + key spec + type, attribute, color, model | BrandCo 65W USB-C Charger, 2-Port GaN Wall Adapter, White, BC-65C | 65 |
| Beauty | Brand + actives with % + type, attribute, size | BrandCo Niacinamide 10% + Zinc 1% Serum, Fragrance-Free, 30 ml | 62 |
| Food | Brand + process + variety + origin, attribute, net weight | BrandCo Raw Khalisha Honey from the Sundarbans, Unheated, 500 g Jar | 67 |
| Home | Brand + material + type, size, color, set count | BrandCo Stoneware Dinner Plates, 10.5 Inch, Matte Sand, Set of 4 | 64 |
| B2B | Brand + size + type, grade, standard, pack | BrandCo M8 x 40 mm Hex Bolts, A2-70 Stainless Steel, DIN 933, 100 Pack | 70 |
| eBay used phone | Brand + model + capacity + color + lock + grade + battery + model no. | Apple iPhone 13 128GB Midnight Unlocked Good Condition Battery 88% A2482 | 72 |
| Etsy | Personalization + material + type, detail, size | Personalized Walnut Cutting Board, Engraved Family Name, 12 x 8 Inch | 68 |

For Google, extend the Amazon title with the next most-searched attributes up to 150 characters, keeping the decisive words in the first 70 [16].

### 8.2 Bullet formulas

1. **Label: fact, so outcome**: "Battery: 7 hours per charge, 30 with the case, at 50% volume"
2. **Fit or compatibility**: "Fits: iPhone 15 and 15 Pro; not 15 Plus or Pro Max"
3. **Proof first**: "Tested: holds 22 kg on the included anchors in brick"
4. **In the box**: "Includes: 2 plates, 4 screws, 1 hex key; drill not included"
5. **Care and limits**: "Care: hand wash only; the matte glaze shows cutlery marks over time"

One idea per bullet, numbers with units, nothing repeated from the title, within the field limit.

### 8.3 Long description skeleton

1. First 160 characters: what it is, who it is for, the deciding spec [17].
2. Three to five highlights: header plus one to three sentences [39].
3. Grouped specs: dimensions and weight, materials, compatibility, power [40].
4. In the box, and not in the box [38].
5. Care, use and one honest limit.
6. Three to five FAQs [43].

On Walmart, merge steps 1 to 5 into one paragraph of 150+ words [29].

### 8.4 Weak vs strong (written for this report)

- **Amazon title.** Weak (111 chars): "BEST Premium Wireless Earbuds Bluetooth Earbuds Headphones for iPhone Android Sports Running Gym Perfect Gift!!" Strong (66): "BrandCo Wireless Earbuds, Bluetooth 5.3, 30-Hour Case, IPX4, Black"; item highlights: "Active noise canceling, 6 mics, USB-C and Qi charging, 4.6 g per earbud".
- **Bullet.** Weak: "PREMIUM SOUND: Elevate your listening experience, perfect for any occasion!" Strong: "Sound: 10 mm drivers with app EQ; bass stays clean at full volume in our tests" (only if the brief holds that test).
- **Apparel fit.** Weak: "Perfect fit for every body." Strong: "Fit: relaxed through the chest; model is 178 cm and wears M; between sizes, size down".
- **Beauty.** Weak: "Clinically proven serum that repairs skin and boosts collagen." Strong: "10% niacinamide and 1% zinc in a water-light gel for oily skin; fragrance-free; patch test first".
- **Home.** Weak: "Elevate your dining with stunning, timeless plates perfect for any occasion." Strong: "Stoneware, 26.7 cm (10.5 in) across. Dishwasher and microwave safe; not for the oven. The matte glaze shows cutlery marks; baking-soda paste lifts most."
- **Bangla Facebook post.** Weak: "১০০% খাঁটি সুন্দরবনের মধু, সেরা মানের! রোগ প্রতিরোধ ক্ষমতা বাড়ায়, ডায়াবেটিসেও উপকারী। দাম জানতে ইনবক্স করুন!!" Strong: "সুন্দরবনের খলিশা ফুলের কাঁচা মধু, ৫০০ গ্রাম কাচের বয়ামে। এপ্রিলে সংগ্রহ করা, ছেঁকে নেওয়া, জ্বাল দেওয়া হয়নি। ঠান্ডায় দানা বাঁধতে পারে, কাঁচা মধুতে এটা স্বাভাবিক; বয়ামটা কুসুম গরম পানিতে রাখলে আবার তরল হয়। দাম ৳৬৫০। ঢাকার ভেতরে ডেলিভারি ৳৬০, বাইরে ৳১২০, ক্যাশ অন ডেলিভারি।" The weak one makes an unprovable purity claim and a disease claim (s.44 risk) and hides the price.

## 9. Pre-publish checklist

- [ ] Platform profile loaded; every field within its limit (bytes for Amazon keywords).
- [ ] Title opens with brand and product type; decisive attribute within 70 characters; variants only in child titles.
- [ ] No banned symbols, no word three times, no promo, boast, time or price words, no all caps.
- [ ] Numbers carry units, and test conditions where results vary.
- [ ] Top five category questions answered; one honest limit where relevant.
- [ ] Every health, eco, origin, comparison, guarantee, certification or award claim has evidence in the brief, or is gone.
- [ ] No reviews, ratings, URLs, phone numbers, shipping or dates in marketplace fields.
- [ ] Facts identical across title, bullets, description, attributes and images.
- [ ] AI-tell scan clean; no em or en dashes; generated Google text sent as `structured_*` [16][17].
- [ ] Bangla: price shown, delivery and return terms stated, everyday language.

## 10. Implications for our skill

**Rules**

1. Load a platform profile first; one version per channel. Store limits and banned lists as data with a "verified on" date: Amazon rewrote its title rules twice in two years (January 2025, then the 75-character cap) [1][11].
2. Facts in, facts out: every spec, number, certification, award, origin or test traces to the brief; gaps become client questions, never guesses [29][57].
3. Title = identity plus decisive attribute in the platform's order [1][16][31]; overflow goes to item highlights, tags or hidden keywords.
4. Bullets follow 8.2, descriptions follow 8.3, gist first [3][17][44].
5. A claims gate (section 5) rewrites or blocks risky wording before any style pass.
6. Voice follows 4.4; Bangla follows section 6 and house style.

**Automatic checks (copylint-style)**

- Length per field (characters; bytes for Amazon keywords, 249 max).
- Banned characters per platform; emoji and all-caps detectors.
- Amazon title word counter (max 2, ignoring articles, prepositions, conjunctions).
- Word lists: promo, boast, time-sensitive, retailer and competitor names, URL, phone, email.
- Claim triggers: disease terms, drug verbs, "FDA approved", "clinically proven", eco generics, "Made in", guarantee, certified, #1, award; each hit needs an evidence field.
- AI-tell phrases (section 7) and shapes (pun-plus-colon title, "Whether you're", rhetorical questions).
- Overlap: n-gram similarity between title, first bullet and first sentence.
- Consistency: numbers and units extracted from all fields must match.

**Judge criteria (1 to 5 each; any hard fail blocks delivery)**

| Criterion | Pass looks like | Hard fail |
|---|---|---|
| Compliance | Within limits; no banned words or symbols | Any platform or legal violation |
| Truth | Every claim traceable to the brief | Invented spec, review, award or test |
| Findability | Product type and decisive attribute early; searched phrases once | Stuffing, or product type missing |
| Sufficiency | Answers the category's top five questions | Fit, size or compatibility missing where relevant |
| Specificity | Most sentences carry a checkable detail | Mostly adjectives |
| Honesty | A real limit where relevant | Hides a known limit |
| Voice | Fits category and audience; reads like a person | Two or more AI tells |
| Scannability | Labelled chunks, grouped specs | Wall of text where structure is allowed |

## Sources

Entries without a date come from pages that show none; all pages except [24] were read on 2026-09-26.

1. Amazon Seller Central, "Product title requirements and guidelines", https://sellercentral.amazon.com/help/hub/reference/external/GYTR6SYGFA5E3EQC.
2. Amazon Seller Central, "Product detail page rules", https://sellercentral.amazon.com/help/hub/reference/external/G200390640.
3. Amazon Seller Central, "Product bullet point requirements", https://sellercentral.amazon.com/help/hub/reference/external/GX5L8BF8GLMML6CX.
4. Amazon Seller Central, "A+ content guidelines", https://sellercentral.amazon.com/help/hub/reference/external/GGW8U76SSNTRTBX7.
5. Amazon Seller Central, "Use search terms effectively", https://sellercentral.amazon.com/help/hub/reference/external/G23501.
6. Amazon Seller Central, "Optimize your product discoverability", https://sellercentral.amazon.com/help/hub/reference/external/G10471.
7. Amazon Seller Central, "Keyword attributes explained", https://sellercentral.amazon.com/help/hub/reference/external/GF2C2L6RCFZGWBXC.
8. Amazon Seller Central, "Misleading and prohibited claims", https://sellercentral.amazon.com/help/hub/reference/external/G202024200.
9. Amazon Seller Central, "General Listing Restrictions", https://sellercentral.amazon.com/gp/help/external/G201707070.
10. Amazon Seller Central, "Alexa for shopping", https://sellercentral.amazon.com/help/hub/reference/external/GYYH9SLHSTHKT3CZ.
11. Amazon Seller Forums, "New product title requirements effective January 21, 2025", https://sellercentral.amazon.com/seller-forums/discussions/t/b2b15728-0d43-453e-974f-59eb63f73059, posted before 8 Jan 2025.
12. eComEngine, "Stay Compliant: Amazon's Updated Bullet Point Guidelines", https://www.ecomengine.com/blog/amazon-bullet-point-guidelines, 5 Sep 2024 (secondary).
13. Keywords.am, "Amazon Character Limits 2026: The Complete Technical Reference", https://keywords.am/blog/amazon-character-limits/, updated 4 Aug 2026 (secondary).
14. Amazon Science, "Building commonsense knowledge graphs to aid product recommendation", https://www.amazon.science/blog/building-commonsense-knowledge-graphs-to-aid-product-recommendation, 10 May 2024.
15. About Amazon, "Amazon launches generative AI to help sellers write product descriptions", https://www.aboutamazon.com/news/small-business/amazon-sellers-generative-ai-tool, 13 Sep 2023.
16. Google Merchant Center Help, "Title [title]", https://support.google.com/merchants/answer/6324415.
17. Google Merchant Center Help, "Description [description]", https://support.google.com/merchants/answer/6324468.
18. Google Merchant Center Help, "Product highlight [product_highlight]", https://support.google.com/merchants/answer/9216100.
19. Google Merchant Center Help, "Product data specification", https://support.google.com/merchants/answer/7052112.
20. Google Merchant Center Help, "Question and answer [question_and_answer]", https://support.google.com/merchants/answer/17085211.
21. Shopify Help Center, "Adding keywords" (SEO), https://help.shopify.com/en/manual/promoting-marketing/seo/adding-keywords.
22. Shopify Blog, Lizzie Davey, "How to Write a Product Description That Sells (2026)", https://www.shopify.com/blog/8211159-9-simple-ways-to-write-product-descriptions-that-sell, 30 Jan 2026.
23. Etsy Open API v3, "createDraftListing", https://developers.etsy.com/documentation/reference/#operation/createDraftListing.
24. Etsy Help Center, listing and search help, https://help.etsy.com/hc/en-us/articles/360000343508, not readable (bot challenge).
25. eBay Seller Center, "Listing best practices", https://www.ebay.com/sellercenter/listings/listing-best-practices.
26. eBay Help, "Creating a listing", https://www.ebay.com/help/selling/listings/creating-managing-listings/creating-listing?id=4105.
27. eBay Help, "Item description policy", https://www.ebay.com/help/policies/listing-policies/item-description-policy?id=4372.
28. eBay Help, "Search manipulation policy", https://www.ebay.com/help/policies/listing-policies/search-browse-manipulation-policy?id=4243.
29. Walmart Marketplace Learn, "Product detail page: overview", https://marketplacelearn.walmart.com/guides/Item%20setup/Item%20content,%20imagery,%20and%20media/Product-Detail-Page:-overview.
30. Walmart Marketplace Learn, "Product detail page: Keyword optimization", https://marketplacelearn.walmart.com/guides/Item%20setup/Item%20content,%20imagery,%20and%20media/Product-detail-page:-Keyword-optimization.
31. Walmart Marketplace Learn (Canada), "Avoid keyword stuffing", https://marketplacelearn.walmart.com/ca/guides/Item%20setup/Item%20content,%20imagery,%20and%20media/avoid-keyword-stuffing.
32. Daraz University, "Improve your Product Content Quality", https://university.daraz.com.bd/course/learn?id=39939&type=video, 28 Feb 2024.
33. Daraz University, "AI Product Titles", https://university.daraz.com.bd/course/learn?id=46371&type=article, 6 Jan 2026.
34. Daraz University, "Duplicate Products Policy", https://university.daraz.com.bd/course/learn?id=46924&type=lms, 1 Apr 2026.
35. Daraz University, "Guide To Size Chart Feature", https://university.daraz.com.bd/course/learn?id=46946&type=article, 16 Apr 2026.
36. Daraz University, "Product Image Policy", https://university.daraz.com.bd/course/learn?id=47452&type=lms, 13 Jul 2026.
37. Baymard Institute, Edward Scott, "Product Page UX 2026: 10 Pitfalls and Best Practices", https://baymard.com/research-articles/current-state-ecommerce-product-page-ux, updated 18 Mar 2026.
38. Baymard Institute, Alex Krzyminski, "10% of E-Commerce Sites Have Product Descriptions That Are Insufficient for Users' Needs", https://baymard.com/research-articles/product-descriptions, 9 Mar 2021.
39. Baymard Institute, Edward Scott, "Structuring Product Page Descriptions by 'Highlights' Increases User Engagement (Yet 78% of Sites Don't)", https://baymard.com/research-articles/structure-descriptions-by-highlights, 24 Apr 2018.
40. Baymard Institute, Edward Scott, "Product Spec Sheets: 4 Ways to Make Spec Sheets More Scannable for Users (50% of Sites Get It Wrong)", https://baymard.com/research-articles/spec-sheet-scannability, 27 Mar 2018.
41. Baymard Institute, Edward Scott, "83% of Apparel Sites Don't Provide Sufficient Sizing Information: 10 Best Practices on Sizing", https://baymard.com/research-articles/apparel-size-information, 6 Jul 2022.
42. Baymard Institute, Niel Gan, "Apparel & Accessories Quantitative UX: 3 High-Level Takeaways from 40+ Charts", https://baymard.com/research-articles/apparel-and-accessories-quantitative-ux-insights-2026, 12 Jun 2026.
43. Baymard Institute, "Product Page UX: Provide Both Site-Authored FAQs and Community-Driven Q&As (70% Get it Wrong)", https://baymard.com/research-articles/product-page-faq-and-qa, 4 Jul 2017.
44. Nielsen Norman Group, Katie Sherwin, "UX Guidelines for Ecommerce Product Pages", https://www.nngroup.com/articles/ecommerce-product-pages/, 24 Nov 2019.
45. Nielsen Norman Group, John Morkes and Jakob Nielsen, "Concise, SCANNABLE, and Objective: How to Write for the Web", https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/, 1 Jan 1997.
46. Grant Packard and Jonah Berger, "How Concrete Language Shapes Customer Satisfaction", Journal of Consumer Research 47(5), https://academic.oup.com/jcr/article/47/5/787/5873526, Feb 2021.
47. National Retail Federation, "NRF and Happy Returns Report: 2024 Retail Returns to Total $890 Billion", https://nrf.com/media-center/press-releases/nrf-and-happy-returns-report-2024-retail-returns-total-890-billion, 5 Dec 2024.
48. US FTC, "Health Products Compliance Guidance", https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance, Dec 2022.
49. US FDA, "Is It a Cosmetic, a Drug, or Both? (Or Is It Soap?)", https://www.fda.gov/cosmetics/cosmetics-laws-regulations/it-cosmetic-drug-or-both-or-it-soap, 11 Sep 2024.
50. US FDA, "Structure/Function Claims", https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/structurefunction-claims, 28 Mar 2024 (regulation: 21 CFR 101.93).
51. US FTC, "Green Guides", https://www.ftc.gov/news-events/topics/truth-advertising/green-guides.
52. European Parliament, "MEPs adopt new law banning greenwashing and misleading product information", https://www.europarl.europa.eu/news/en/press-room/20240112IPR16772/meps-adopt-new-law-banning-greenwashing-and-misleading-product-information, 17 Jan 2024.
53. European Commission, "Sustainable consumption", https://commission.europa.eu/live-work-travel-eu/consumer-rights-and-complaints/sustainable-consumption_en.
54. UK CMA, "Making environmental claims on goods and services" (Green Claims Code), https://www.gov.uk/government/publications/green-claims-code-making-environmental-claims/environmental-claims-on-goods-and-services, 20 Sep 2021.
55. US FTC, "Complying with the Made in USA Standard", https://www.ftc.gov/business-guidance/resources/complying-made-usa-standard, Jul 2024.
56. US FTC, "Statement of Policy Regarding Comparative Advertising", https://www.ftc.gov/legal-library/browse/statement-policy-regarding-comparative-advertising, 13 Aug 1979.
57. US FTC, "Federal Trade Commission Announces Final Rule Banning Fake Reviews and Testimonials", https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials, 14 Aug 2024.
58. US FTC, "Consumer Reviews and Testimonials Rule: Questions and Answers", https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers, Nov 2024.
59. Government of Bangladesh, Consumer Rights Protection Act 2009 (Act 26 of 2009), section 44, http://bdlaws.minlaw.gov.bd/act-1014/section-39152.html, 6 Apr 2009.
