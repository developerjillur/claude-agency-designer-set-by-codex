# Claims, proof and the law (general information, not legal advice)

Route health, money, environmental and comparative claims to a human before they run. Evidence:
`research/R5-copywriting.md` §7, `R6-email-and-outbound.md` §7, `R7-product-copy.md` §5, and nexa-script's
`R2-shortform-and-ads.md` §6 for ad platforms.

## 1. Reviews, testimonials and endorsements

- **US, FTC rule on consumer reviews and testimonials** (16 CFR Part 465, effective 2024-10-21): bans fake reviews and
  testimonials, including AI-generated ones that misstate real experience; paying for reviews conditioned on
  sentiment; undisclosed insider reviews; company-run "independent" review sites; review suppression; buying or selling
  fake followers or views. Incentives for honest reviews stay legal if not tied to sentiment.
- **US, Endorsement Guides** (updated 2023): a testimonial with exceptional results needs proof that it is typical or a
  clear statement of what people generally get ("results not typical" alone is not enough); material connections are
  disclosed clearly and early in the post; platform disclosure tools may not suffice.
- **UK, DMCC Act 2024** (in force April 2025): bans fake reviews, concealed incentivised reviews and false review
  information, and commissioning them; the CMA can fine directly.
- **Never:** invent a review, a rating, a customer, a quote, a follower count or a "customers love it".

## 2. Substantiation and dark patterns

- **US:** hold a reasonable basis before the ad runs; "tests show" or "doctors recommend" needs exactly that level of
  evidence (the FTC's 1984 policy). The FTC's dark-patterns report (2022) names fake countdown timers and false
  limited-time claims as deceptive.
- **UK, CAP Code:** documentary evidence for objective claims before publishing (rule 3.7); do not mislead (3.1) or
  exaggerate (3.11); specific rules for "free" (3.23 to 3.26) and availability and limited-time claims (3.27 to 3.31).
- **Urgency and scarcity** only with a real date or stock count (the lint flags urgency without one).

## 3. Environmental claims

- **EU Directive 2024/825, applied from 2026-09-27:** bans generic environmental claims (eco-friendly, green, climate
  friendly, natural, biodegradable) without recognised excellent performance; climate-neutral claims based on offsets;
  uncertified sustainability labels; whole-product claims when only a part qualifies; presenting a legal requirement as
  a distinctive feature.
- **US:** the FTC Green Guides (2012; a review opened in 2022 with no revision posted) and California's Environmental
  Marketing Claims Act; Amazon requires evidence.
- **UK:** the Green Claims Code: truthful, clear, complete, fairly compared, life-cycle aware, substantiated.
- Write the scoped fact: "Bottle body: 50 % recycled PET (certificate in the brief); the cap is virgin plastic."

## 4. Health, beauty, supplements

- The FTC expects competent and reliable scientific evidence, generally randomised controlled human trials, for health
  benefit claims, judged on the net impression of names, images and text (2022 guidance).
- Claims decide whether a cosmetic is a drug: restoring hair growth, reducing cellulite, treating varicose veins,
  changing melanin, regenerating cells, antidandruff and antiperspirant are drug claims (FDA).
- US supplements: structure and function claims need substantiation, FDA notification within 30 days and the exact
  disclaimer (21 CFR 101.93: the product is "not intended to diagnose, treat, cure, or prevent any disease").
- Amazon bans disease claims (arthritis, cancer, COVID-19, depression, diabetes, flu, obesity and more),
  anti-bacterial, anti-fungal and anti-microbial claims, and restricts "FDA approved" and "FDA cleared".
- Ad platforms reject exaggerated results and miracle cures; Meta bans claims to cure conditions and requires 18+
  targeting for weight loss.

## 5. Origin, comparison, superlatives, guarantees

- An unqualified "Made in USA" means all or virtually all US content; Amazon requires an attestation and calls "Made in
  Italy" misleading for a product only assembled there; treat every origin claim, "Made in Bangladesh" included, the
  same way.
- The FTC accepts truthful comparative advertising, but marketplace fields forbid comparisons.
- "Best", "100 % pure" or "twice as effective" need objective proof; "money-back guarantee" commits to full refunds for
  any reason; material, filling, purity and technical claims (cashmere, down, thread count, drive capacity) need proof
  on request.

## 6. Ads: personal attributes and AI

- **Meta personal-attribute rule:** ads may not assert or imply race, religion, age, sexual orientation, gender
  identity, disability, health, financial vulnerability, voting status or criminal record: no questions about the
  viewer's condition ("Struggling with your weight?"), no "Meet other seniors". Describing the product, or "you" with no
  trait, is fine.
- **AI disclosure:** TikTok requires the AIGC label or a clear disclaimer on significantly AI-modified ads and bans fake
  public-figure endorsements; YouTube requires disclosure of realistic synthetic people, places or events; Meta labels
  AI and requires disclosure on political and social issue ads; the EU AI Act (Article 50) requires deepfakes to be
  disclosed from 2026-08-02.
- Do not lead with "AI" in consumer copy: naming artificial intelligence as the benefit lowered purchase intent, most
  for risky products.

## 7. Email and outbound

CAN-SPAM, GDPR, PECR and the mailbox rules are in `email.md` §3 and `outbound.md` §4: sender identity, postal address,
a working opt-out, no deceptive subjects, privacy information for EU and UK prospects.

## 8. Bangladesh

- **Consumer Rights Protection Act 2009, s.44:** deceiving buyers with false or untrue advertising is punishable by up
  to one year in prison, a fine up to Tk 2 lakh, or both.
- The Digital Commerce Operation Guidelines 2021 set disclosure duties (product details, price, delivery time, return
  and refund terms); the official text could not be read in our research, so treat the exact wording as unverified.
- No specific e-marketing or spam law was found (2024); outreach abroad follows the recipient's law.

## 9. How the lint helps

`copywriter.py lint` gates every claim-looking line (numbers, percentages, prices, superlatives, "free", guarantees,
reviews, "clinically", "FDA", awards) until it carries a claim id or `brief`; errors on disease and drug claims;
gates generic green claims and "made in" without evidence; warns on urgency without a date; errors on hidden prices in
Bangladeshi shop posts. A passing lint is not legal clearance: a human signs off regulated claims.
