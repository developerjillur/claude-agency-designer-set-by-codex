# Product titles and descriptions

Facts in, facts out: every spec, number, certification, award, origin or test traces to the brief; a gap becomes a
client question, never a guess. Evidence: `research/R7-product-copy.md` (official platform pages read 2026-09-26;
Baymard and NN/g on how shoppers read). Limits change often: `platforms.json` holds them with the date.

## 1. Key findings (R7 §1)

1. Amazon titles are now 75 characters (all product types except media), plus a 125-character "item highlights"
   field; guides saying 200 are stale.
2. The same title junk is banned everywhere: promo phrases, boasts ("best seller", "top rated"), all caps, symbols,
   prices, shipping and time words.
3. AI text carries duties: Google wants it flagged (`structured_title`, `structured_description`); Walmart makes
   sellers substantiate it and bans fabricated reviews.
4. Assistants read the page: Amazon's shopping assistant answers questions from detail-page data; Google's
   `question_and_answer` attribute targets AI Mode.
5. Facts beat fluff: every Baymard test user relied on descriptions, yet many found them bland; objective text tested
   27 % more usable than promotional text.
6. Missing specs lose sales: materials, labelled dimensions, exact compatibility, box contents; 83 % of desktop apparel
   sites lack enough sizing information.
7. Returns and fit are pre-purchase questions: 60 % look for the return policy on the product page; size and fit are
   what apparel shoppers most seek in reviews (48 %).
8. Claims carry the legal risk: health, eco, origin, comparison and guarantee wording needs evidence or removal.

## 2. Platforms (R7 §2)

| Platform (type) | Title | Short copy | Long description |
|---|---|---|---|
| Amazon (`amazon`) | 75; no `! $ ? _ { } ^ ¬ ¦`; a word at most twice | highlights 125; 3 to 5 bullets | paragraphs, no HTML but line breaks; search terms under 250 bytes |
| Google Merchant (`google-merchant`) | 150, about 70 seen | highlights 150 each (4 to 6 advised); up to 30 Q&A pairs of 1,000 | 5,000; key facts in the first 160 to 500 |
| Shopify (`shopify`) | SEO title 70, aim 60 | meta description about 160 | theme-dependent |
| eBay (`ebay`) | 80 | item specifics | the site's language, no symbols |
| Walmart (`walmart`) | 150 (50 to 75 advised) | 3 to 10 key features of 80 | one paragraph of 150+ words, no bullets or emoji |
| Etsy (`etsy`, unverified) | 140 | 13 tags of 20 | free text |
| Daraz (`daraz`, behind seller login) | unverified | highlights plus attributes | free text |

- **Amazon title order:** brand, flavour or style, product type, the key attribute, colour, size or pack count, model
  number. Numerals ("2-Pack"), abbreviated units, title case with small words lowercase. Size and colour go in child
  titles, never the parent.
- **Amazon bullets:** "Header: description" fragments with no end punctuation; spell out one to nine except in names,
  model numbers and measurements; a space between number and unit ("60 ml"); no brand stories, no subjective,
  comparative or unprovable claims; banned: emoji, placeholders (N/A, TBD), "eco-friendly", "anti-microbial",
  "anti-bacterial", "made from bamboo", guarantee phrases, company info, links, abbreviations (qty, pkg, w/, approx.).
- **Amazon search terms:** under 250 bytes; synonyms, abbreviations, spelling variants; no brand names, ASINs,
  temporary words (new, on sale) or subjective words (best, cheapest, amazing, popular); no common misspellings.
- **Everywhere on marketplaces:** no contact details, URLs, prices, availability, shipping offers, reviews, quotes or
  review requests in titles, bullets, descriptions or images. Google's own sample of an AI-generated title ("Stride &
  Conquer: ... Power Shoes") shows the pun-plus-colon pattern never to produce.
- **Daraz:** correct titles, images, category tags and attribute-based descriptions; variations instead of
  near-duplicate listings (April 2026); size charts to cut size-related returns.

## 3. What shoppers look for (R7 §3)

- Descriptions chunked by highlight (a header, an image, short text) are read more deeply than feature dumps.
- Materials or ingredients, labelled dimensions in two unit systems, exact compatibility down to the model number, box
  contents, explanations of icons shown in images.
- Group specs, lead with the key ones, one column.
- Sizes: conventional and numeric, cm and inches, conversions, how to measure, the model's measurements and size worn.
- The return policy on the product page; a community Q&A plus site FAQs work best.

## 4. Writing (R7 §4)

**Feature, benefit, outcome, proof, limit** (an insulated bottle): double-wall 18/8 stainless steel, vacuum sealed →
keeps drinks cold → ice still there at the end of a 10-hour shift → cold for 24 h in a 22 °C room (the maker's test) →
hand wash only. Outcomes and proofs are claims: without a test in the brief, stop at the benefit.

**Specs by category:**

| Category | State these | Answer these |
|---|---|---|
| Fashion | size range and system, fit, fabric %, weight or stretch, care, length, the model's size | Will it fit? See-through? Shrink? |
| Electronics | model number, exact compatibility, W, mAh or GB, version, battery life with test conditions, size, weight, box contents | Works with my device? How long? |
| Beauty | skin or hair type, actives with %, full ingredients, volume, fragrance status, texture, use | Will it irritate? What is in it? |
| Food | net weight, ingredients, allergens, origin, process, storage, shelf life | Fresh? Real? Safe for me? |
| Home | overall and part dimensions, material, weight limit, cleaning, assembly, set contents | Fits my space? Easy to clean? |
| B2B | part number, standard (DIN, ISO), grade, tolerances, pack quantity, documents | Meets spec? Paperwork? |

- **Keywords without stuffing:** the product type plus the one or two searched attributes inside the first 70
  characters; each primary keyword once per field; synonyms go to hidden fields (search terms, tags).
- **Voice by category:** fashion tactile but checkable; electronics numbers with conditions, no hype; beauty calm, no
  drug verbs (treat, cure, repair, heal), and who it is not for; food origin, process and taste through concrete
  comparisons, no health promises; home dimensions plus living-with details; B2B spec-sheet voice.
- **Sensory words point at something checkable:** "soft" becomes "brushed inside, 280 gsm fleece".
- **One honest limit** where relevant (care, a fit quirk, excluded models, what is not in the box).

## 5. Templates (R7 §8; brand "BrandCo" is a dummy)

| Category | Title | Characters |
|---|---|---|
| Apparel | BrandCo Women's Merino Wool Crew Neck Sweater, Navy, Medium | 59 |
| Electronics | BrandCo 65W USB-C Charger, 2-Port GaN Wall Adapter, White, BC-65C | 65 |
| Beauty | BrandCo Niacinamide 10% + Zinc 1% Serum, Fragrance-Free, 30 ml | 62 |
| Food | BrandCo Raw Khalisha Honey from the Sundarbans, Unheated, 500 g Jar | 67 |
| Home | BrandCo Stoneware Dinner Plates, 10.5 Inch, Matte Sand, Set of 4 | 64 |
| B2B | BrandCo M8 x 40 mm Hex Bolts, A2-70 Stainless Steel, DIN 933, 100 Pack | 70 |

**Bullet formulas:** "Battery: 7 hours per charge, 30 with the case, at 50% volume"; "Fits: iPhone 15 and 15 Pro;
not 15 Plus or Pro Max"; "Tested: holds 22 kg on the included anchors in brick"; "Includes: 2 plates, 4 screws, 1 hex
key; drill not included"; "Care: hand wash only; the matte glaze shows cutlery marks over time". One idea per bullet,
numbers with units, nothing repeated from the title.

**Long description:** the first 160 characters say what it is, who it is for and the deciding spec; 3 to 5 highlights
(a header plus one to three sentences); grouped specs; in the box and not in the box; care, use and one honest limit;
3 to 5 FAQs. On Walmart, one paragraph of 150+ words.

**Weak and strong:** Weak title (111 characters): "BEST Premium Wireless Earbuds Bluetooth Earbuds Headphones for
iPhone Android Sports Running Gym Perfect Gift!!" Strong (66): "BrandCo Wireless Earbuds, Bluetooth 5.3, 30-Hour Case,
IPX4, Black". Weak bullet: "PREMIUM SOUND: Elevate your listening experience, perfect for any occasion!" Strong:
"Sound: 10 mm drivers with app EQ" (plus a tested claim only if the brief holds the test). Weak beauty line:
"Clinically proven serum that repairs skin and boosts collagen." Strong: "10% niacinamide and 1% zinc in a
water-light gel for oily skin; fragrance-free; patch test first".

## 6. Bangladesh f-commerce (R7 §6; type `fb-shop` or `daraz`)

- Show the price with ৳ in the post; "দাম জানতে ইনবক্স করুন" hides what buyers need and clashes with the disclosure
  duties in the Digital Commerce guidelines (the lint errors on it).
- State the delivery charge inside and outside Dhaka, the delivery time, cash on delivery and the return window.
- Replace "১০০% অরিজিনাল" or "সেরা মানের" with checkable facts: origin, harvest or batch date, a warranty card, a size
  chart.
- Open on the buyer's own situation, with every use the brief names (tea and the children, not one of them), and
  voice their worry in their words before the facts answer it; admit what a seller's word cannot prove.
- Put the order facts in labelled lines, one per line (পরিমাণ, দাম, ডেলিভারি, পেমেন্ট): buyers scan for them. Say
  what cash on delivery means for them (হাতে পেয়ে দাম দেবেন).
- Give two easy ways to order: the inbox, or a comment with how many they want (when the brief's action allows both).
- Say who makes it when the brief says so (a small Dhaka workshop, a family farm, "we"): in the holdout the judge
  that chose a side named the maker's presence as the reason.
- Warm means spoken: whole sentences with the small joins people use when they talk (আরেকটা কথা আগেই বলে রাখি,
  সোজাসুজি বলছি), not headline shorthand with a colon ("প্রথম প্রশ্ন: ..."). Judges called the shorthand "clipped" and
  "transactional" when the brief asked for a warm, honest voice.
- In the 2026-09-26 benchmark a post that listed the facts in running lines lost 0 to 3 to one that did the above;
  the judges called the loser "an impersonal list of specifications".
- Everyday চলিত Bangla with the English words buyers use (size, cotton, charger); one digit system per post.
- False advertising is an offence in Bangladesh: up to one year in prison, a fine up to Tk 2 lakh, or both (Consumer
  Rights Protection Act 2009, s.44). Disease claims ("রোগ প্রতিরোধ ক্ষমতা বাড়ায়", "ডায়াবেটিসে উপকারী") never run.

Weak: "১০০% খাঁটি সুন্দরবনের মধু, সেরা মানের! রোগ প্রতিরোধ ক্ষমতা বাড়ায়, ডায়াবেটিসেও উপকারী। দাম জানতে ইনবক্স করুন!!"
Strong (a hand-stitched kantha; the facts are the example's own):

```
শীতে বাচ্চার গায়ে দেবেন, সোফায়ও বিছাবেন। প্রশ্ন একটাই: ছবির মতো আসবে তো?
হাতে সেলাই, তাই দুটো কাঁথা হুবহু এক হয় না, আর স্ক্রিনে রং একটু আলাদা দেখাতে পারে। বাকিটা নিচে লিখে দিলাম।

মাপ: ৬০ × ৯০ ইঞ্চি
কাপড়: সুতি, তিন পরত
ধোয়া: ঠান্ডা পানিতে, মেশিনেও চলে
দাম: ৳২,৪০০
ডেলিভারি: ঢাকার ভেতরে ৳৬০, বাইরে ৳১২০
পেমেন্ট: ক্যাশ অন ডেলিভারি, হাতে পেয়ে দাম দেবেন

নিতে চাইলে ইনবক্স করুন, অথবা কমেন্টে লিখুন কয়টা লাগবে।
```

## 7. Before publishing (R7 §9)

- Every field within its limit (bytes for Amazon search terms); the title opens with the brand and product type, the
  deciding attribute within 70 characters, variants only in child titles.
- No banned symbols, no word three times, no promo, boast, time or price words, no all caps.
- Numbers carry units, and test conditions where results vary.
- The category's top five questions answered; one honest limit where relevant.
- Every health, eco, origin, comparison, guarantee, certification or award claim has evidence in the brief, or it is
  gone.
- Facts identical across the title, bullets, description, attributes and images (the lint compares numbers and units).
- AI-generated Google text sent in the `structured_*` attributes.
