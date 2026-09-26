---
name: nexa-copy
description: "Writes conversion copy like a senior direct-response copywriter: paid ads (Meta, Google Search and Performance Max, TikTok, LinkedIn, YouTube), social media posts and captions, landing pages, email (welcome, abandoned cart, promo, newsletter), cold outbound and follow-ups, Upwork proposals, LinkedIn notes and DMs, product titles, bullets and short and long descriptions (Amazon, Google Merchant, Shopify, eBay, Walmart, Etsy, Daraz, Facebook shop posts), in English, Bangla, Banglish and more. It researches the customer's own words first (nexa-research), picks the reader's awareness and the angle, writes 3 to 5 distinct angles, then checks every field against the platform's current limits, every claim against the research pack and the law, and every word against natural-text, and runs a review loop: judges from other model families, a 100-persona panel grounded in real comments, pairwise preference and an A/B test plan with the right sample size. Use it for any selling or outreach copy ('ad copy likho', 'product description banao', 'cold email likho', 'Upwork proposal'). Not for video scripts or articles (nexa-script) or a single casual caption or reply (natural-text)."
allowed-tools: Bash(python3 ~/.claude/skills/nexa-copy/scripts/copywriter.py:*), Bash(python3 ~/.claude/skills/nexa-research/scripts/research.py:*), Bash(python3 ~/.claude/skills/codex-design/scripts/design.py:*), Read, Write, Edit
---

# nexa-copy

Claude is the copywriter: the research, the angle, the words and every judgement are Claude's. The tool holds each
platform's field limits as dated data, gates claims against the research pack and the law, runs natural-text's 932
voice rules on every field, and runs the review loop with judges from other model families and a simulated audience.
Command prefix: `python3 ~/.claude/skills/nexa-copy/scripts/copywriter.py`.

## Fast path (every piece: do exactly this)

1. **Start the folder:** `copywriter.py new DIR --type TYPE --lang en|bn|banglish [--brand B]` (`copywriter.py types`
   lists the 37 types). Fill `DIR/brief.json`: the product, the reader (who, situation, the job, objections), their
   awareness, the offer, the one action, `facts_given`, `proof`, `voc` (real customer phrases), the voice, the deadline
   (only a real one), the region.
2. **Find the customer's words:** when the brief has no real customer phrases, run nexa-research for reviews,
   comments, forums and competitor copy (`research.py new DIR --topic "..."`), and log the phrases in the voice bank.
   Never invent one.
3. **Pick the angle** (`references/craft.md` §2 to §4): the awareness level sets the first line; the most frequent,
   most intense, provable pain or desire sets the angle. Ads get 3 to 5 angles that differ in pain, desire or
   mechanism.
4. **Write `DIR/copy.json`:** each variant's fields in the platform's order; every field with a claim lists its claim
   ids (or `brief`). Mark what the client must supply with `[NEEDS INPUT: ...]`.
5. **Check it against the brief, then gate it.** Read the brief again: the reader's worry voiced in their words and
   answered with the proof, their situation in the opening, the brief's action asked for, nothing added that the brief
   or the research does not hold. Then `copywriter.py lint DIR/copy.json --brief DIR/brief.json --pack
   DIR/research/pack.json` (natural-text's voice pass runs by default). Fix every error and warning, or keep a warning
   only with a one-line reason. (In the 2026-09-26 benchmark a draft that read as a list of specifications lost 0 to 3
   to one that voiced the reader's worry first.)
6. **Render and show:** `copywriter.py render DIR/copy.json` writes `copy.md` with every field's count against its
   limit. Offer the review loop in one line.

**Client level** (anything published under a client's name, a paid campaign, or the user asks for the best): after the
gate, run §5 (judges per variant, the panel, preference, a tournament of the variants) and ship with a test plan
(§6).

## 1. The rules that make copy convert

1. No draft without a brief: product, reader, job, awareness, offer, placement, the one action, the claim ledger and
   customer phrases, or a visible "no research" flag that keeps the output a draft (R5 §11.1).
2. Angles before words: 3 to 5 angles that differ in pain, desire or mechanism, never synonyms.
3. The first line is the headline and must sell alone inside the placement's fold.
4. Every factual claim maps to a ledger row. Never invent numbers, reviews, customers, awards, certifications, stock
   levels or deadlines.
5. One reader, one idea, one action per piece.
6. Plain words: consumer copy at grade 5 to 7; B2B may use its readers' trade terms in short sentences; cold email at
   grade 3 to 6.
7. Persuasion levers only on true facts; urgency only with a real date or stock count.
8. Platform limits and disclosures are hard gates; limits are re-read at job time (`platforms.json` carries the date).
9. The words come from natural-text: the audience's own register, no AI tells, no em dashes.

## 2. By job

| Job | Types | Read |
|---|---|---|
| Paid ads | `meta-feed`, `meta-stories`, `google-rsa`, `google-pmax`, `google-demandgen`, `tiktok-ad`, `linkedin-ad`, `youtube-shorts-ad` | `references/ads-and-social.md` §1 to §4; video ads and UGC scripts with nexa-script |
| Organic posts and captions | `facebook`, `instagram`, `linkedin`, `x`, `threads`, `tiktok`, `youtube` | `references/ads-and-social.md` §5; natural-text |
| Landing pages | `landing` | `references/craft.md` §7, `ads-and-social.md` §3 |
| Lifecycle and marketing email | `email-welcome`, `email-cart`, `email-promo`, `email-newsletter` | `references/email.md` |
| Cold outbound, proposals, LinkedIn | `email-cold`, `email-followup`, `email-breakup`, `proposal`, `proposal-plan`, `linkedin-note`, `linkedin-dm` | `references/outbound.md` |
| Product listings | `amazon`, `google-merchant`, `shopify`, `ebay`, `walmart`, `etsy`, `daraz`, `fb-shop` | `references/product.md` |
| Messages | `whatsapp`, `sms` | natural-text |

## 3. The copy file (`nexa.copy/1`)

```json
{"schema": "nexa.copy/1",
 "meta": {"type": "meta-feed", "lang": "bn", "locale": "BD", "brand": "", "awareness": "problem", "mode": "ad",
          "region": "", "deadline": "", "address": "", "footer_by_tool": false, "is_reply": false},
 "variants": [{"id": "A", "angle": "pain: receipts on Sunday night", "awareness": "problem",
               "fields": [{"role": "primary", "text": "...", "claims": ["c2"]},
                          {"role": "headline", "text": "...", "claims": []},
                          {"role": "cta", "text": "Learn More"}]}],
 "test_plan": {"hypothesis": "", "metric": "", "sample": ""}}
```

Roles per type come from `platforms.json` (`copywriter.py types`); repeat a role for multiple headlines or bullets.
`claims` holds claim ids from `research/pack.json`, or `brief` for a client-given fact. `footer_by_tool` says the email
tool adds the unsubscribe link and address; `region` EU or UK adds the GDPR checks.

## 4. What the lint checks

- **Limits** per field: characters (X counts a URL as 23), words, bytes (Amazon search terms), counts per role, the
  fold, hashtags, mentions, links, emoji, banned characters, repeated words, one-paragraph fields, SMS parts.
- **Claims:** numbers, prices, superlatives, "free", guarantees, reviews, "clinically", "FDA", awards need a ledger row;
  disease and drug claims fail; generic green claims and "made in" need evidence; urgency needs a date.
- **Email and outbound:** fake "Re:" subjects, "Quick question", preview text, link counts, a meeting ask on a first
  touch, an interest question, template phrases, the sender opening the email, unsubscribe, postal address, opt-out,
  the EU privacy line, contact details in Upwork proposals.
- **Products:** marketplace-banned words, prices, links and phone numbers; Amazon bullet and search-term rules; a colon
  in a title; the first bullet restating the title; numbers that disagree across fields.
- **Bangladesh f-commerce:** the price hidden behind the inbox, boasts buyers cannot check, a missing price or delivery
  terms.
- **Packs:** fewer than 3 angles, two variants on one angle or with the same wording, no test plan in a final.
- **Words:** puffery, template openers, "not X, it's Y", lists of three, exclamation marks, all caps, merge tags and
  markers; then natural-text's voice pass per variant (its findings start with `voice:`).

## 5. The review loop (client level)

| Step | Command |
|---|---|
| Gate | `copywriter.py lint FILE --pack research/pack.json --level final` |
| Judges per variant (3 judges x 2 runs) | `copywriter.py judge FILE --brief brief.json --variant A` |
| Panel, once per client and product | `copywriter.py panel build DIR --brief brief.json --evidence research/pack.json --n 100` |
| Validate the panel (past pieces with real results) | `copywriter.py panel validate --panel panel.json --items past.json` |
| The feed-stop lineup | `copywriter.py hooks FILE --pack research/pack.json` |
| Panel reaction | `copywriter.py panel run FILE --panel panel.json --variant A --hooks hooks.json --judge judge-A.json` |
| Revise (Claude) | fix-list lines and neighbours, 25 % of tokens at most, keep-list lines frozen |
| New against old | `copywriter.py prefer OLD NEW --panel panel.json --variant A` |
| Guard against blandness | `copywriter.py guard OLD NEW --variant A --keep review-A.json` |
| Decide | `copywriter.py decide --round N --judge ... --review ... --prefer ... --guard ...` |
| The best angle | `copywriter.py tournament FILE --brief brief.json` |
| Against a plain draft (the bar) | `copywriter.py tournament plain.json FILE --brief brief.json` (a plain draft from `baselines` or a fresh session given only the brief; each judge's reasons come back from both orders) |

The protocol, thresholds and what never to do are in `~/.claude/skills/nexa-script/references/review.md` (the same
engine): two rounds at most; accept a revision only on 61 of 100 paired preferences in each model family, no broken
gate and a clean guard; the panel's fixes count only after validation on past results; every panel number is
synthetic and directional. Real A/B tests decide paid copy; the panel only ranks what goes into the test.

## 6. Test plans (paid copy)

Every ad pack ships `test_plan`: the hypothesis (angle A against angle B), what varies, the primary metric, the sample
and a stop rule written before launch. `copywriter.py sample --baseline 0.03 --lift 0.2` gives the visitors and
conversions per variant (13,914 visitors and 417 conversions for a 3 % baseline and +20 %). Test big levers first:
the angle, the offer, the hook, the proof type, the format, then the CTA and length (`references/ads-and-social.md`
§4).

## 7. Honesty (non-negotiable)

- No invented reviews, ratings, customers, quotes, results, awards, stock levels or deadlines; no AI personas presented
  as real people (FTC 2024 rule, UK DMCC Act).
- No disease, cure, guaranteed-result or quick-money claims; no personal-attribute callouts in ads; no generic green
  claims without proof (EU from 2026-09-27); paid endorsements disclosed early.
- Outreach premises come from the brief or research only; never a detail about the reader you do not have.
- A passing lint is not legal clearance: a human signs off health, money, environmental and comparative claims
  (`references/compliance.md`).
- Never an em dash or a spaced en dash.

## 8. References

- `references/craft.md`: awareness and sophistication, research and the voice of the customer, angles, frameworks,
  the classics and modern conversion writing, proof and specificity, AI tells, weak and strong examples.
- `references/ads-and-social.md`: the fold, what each ad platform advises, output templates, testing and sample
  sizes, organic posts and what the large datasets say.
- `references/email.md`: numbers after Apple's privacy change, subjects and previews, deliverability, lifecycle
  templates, newsletters and promotions, budgets.
- `references/outbound.md`: cold email data and structure, follow-ups, the law for outreach, Upwork proposals,
  LinkedIn, budgets.
- `references/product.md`: platform rules, what shoppers look for, writing by category, templates, Bangladesh
  f-commerce, the pre-publish checklist.
- `references/compliance.md`: reviews and endorsements, substantiation, green claims, health and beauty, origin and
  guarantees, ad policies and AI disclosure, Bangladesh.
- `references/platforms.json`: every type's fields and limits (verified 2026-09-26; update with the date).
- `references/checklists.json`: the judges' yes-or-no items and hard fails per family.
- `references/research/`: R5 conversion copywriting, R6 email and outbound, R7 product copy (2026-09-26): the evidence
  behind every rule.

## The family

natural-text writes every word (the voice backbone); nexa-research finds and verifies facts and the customer's own
words; nexa-script writes video scripts and articles; nexa-copy writes selling and outreach copy. They share one
review engine (`nexa_review.py`) and one model layer (`nexa_llm.py`), copied byte for byte and checked by the tests.
