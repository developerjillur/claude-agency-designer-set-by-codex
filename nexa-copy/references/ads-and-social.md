# Paid ads and organic posts

The field limits live in `platforms.json` (read 2026-09-26; `copywriter.py types` prints them). This file says what to
put in the fields. Evidence: `research/R5-copywriting.md` §6 and §8 to §11; video ads and UGC scripts are written with
nexa-script (`~/.claude/skills/nexa-script/references/formats.md` §3).

## 1. The fold does the selling

The real limit is the visible fold, not the field maximum (R5 §1):

| Placement | The fold |
|---|---|
| Meta feed primary text | the whole sale in the first 125 characters (Meta recommends 50 to 150; headline near 27) |
| Instagram caption | about 125 characters before "more" |
| LinkedIn | about 140 characters on mobile, 210 on desktop; ads: intro under 150, headline under 70 |
| Google Search | headline 1 and description 1 usually show; the others are not guaranteed |
| TikTok in-feed | up to 4 lines; the content proposition in the first 3 seconds of the video |
| YouTube | the title and the first description lines |

natural-text's Facebook rule is stricter (about 80 characters before "more"): write the hook so it lands in either.

## 2. What the platforms advise (R5 §6.3)

- **Google Search:** as many unique headlines and descriptions as you can, in varied lengths; keywords; prices,
  promotions or exclusives in the text; specific CTAs; pin only when a message must always show; at least two ads rated
  Good or Excellent per ad group. Google's own figures: Ad Strength from Poor to Excellent brings 15 % more clicks and
  conversions on average; a second RSA adds 6.6 % conversions, a third 3.7 %. Performance Max counts each Chinese,
  Japanese or Korean character as two.
- **YouTube:** the ABCD checklist (attention, branding, connection, direction): hook fast, brand early, one message,
  ask for the action in voice and text. Ads following it showed 30 % higher short-term sales likelihood and 17 % higher
  long-term brand contribution (Google and Kantar, 2021).
- **TikTok:** hook, body, close; 90 % of ad recall impact lands in the first six seconds; TikTok-first ads with native
  features and text overlays caught 74 % of viewers' attention; CTA cards lifted recall 45 % (TikTok's own studies).
  Non-Spark ad text takes no hashtags, @, links or emoji.
- **LinkedIn:** intro under 150 characters, headline under 70, legally required text in the intro. Only about 5 % of
  B2B buyers are in market at any time (B2B Institute with Ehrenberg-Bass), so most LinkedIn ads build memory for
  later rather than asking for a demo.
- **Meta:** feed primary text 50 to 150, headline near 27; distinct assets for distinct personas and use cases rather
  than small variations (Meta's creative diversification guidance, 2025).

## 3. Output templates (R5 §11.2)

- **Meta pack:** 3 angles, each with primary text (the sale complete in the first 125 characters), a headline up to 27
  (40 elsewhere), a description up to 30 and a CTA button from Meta's menu.
- **Google RSA:** 15 headlines (3 keyword or intent, 3 benefit, 3 proof, 2 offer, 2 objection, 2 CTA), 4
  descriptions, 2 paths; every headline must read well beside any other; pin only when required. Performance Max adds
  long headlines and one headline of 15 characters or fewer.
- **Short video (TikTok, Reels, Shorts):** a 0 to 3 second hook as on-screen text plus voice; the product on screen by
  second 3 to 6; proof or a demo; a CTA card. Script it with nexa-script (`format ad`).
- **Landing page:** H1 (what, for whom, outcome), subhead (how, why believable), a proof bar, 3 to 6 feature blocks
  (a value header plus an objection paragraph), an objection FAQ, risk reversal, one CTA repeated.
- **Organic post:** the hook inside the fold, one idea, one ask (a question or a CTA), a paid-partnership disclosure
  first.

## 4. Testing (R5 §8, §11.5)

What to test first, big levers first: (1) the angle or appeal; (2) the offer (trial, guarantee, bonus, price framing);
(3) the hook or headline; (4) the proof type (number, testimonial, demo); (5) the format (video, carousel, static);
(6) the CTA wording; (7) the length. Synonyms and button colours come last. Only about a third of ideas tested at
Microsoft improved their target metric; about 10 % of Google's experiments led to changes.

**Sample size per variant** (two-sided alpha 0.05, 80 % power; `copywriter.py sample --baseline 0.03 --lift 0.2`):

| Baseline rate | +10 % | +20 % | +30 % | +50 % |
|---|---|---|---|---|
| 1 % | 163,095 (1,631 conversions) | 42,693 (427) | 19,827 (198) | 7,750 (78) |
| 3 % | 53,211 (1,596) | 13,914 (417) | 6,455 (194) | 2,518 (76) |
| 5 % | 31,234 (1,562) | 8,158 (408) | 3,780 (189) | 1,471 (74) |
| 10 % | 14,751 (1,475) | 3,841 (384) | 1,774 (177) | 686 (69) |

Roughly 1,600 conversions per variant to see a 10 % lift, 400 for 20 %, 75 for 50 %. Small accounts test bold
differences, not tweaks. Fix the sample before launch: peeking and stopping at the first significant reading turned a
5 % false-positive rate into 26.1 % in Evan Miller's example. Run whole weeks, keep one primary metric, check the lift
holds downstream (qualified leads, revenue), and log the hypothesis, the variants, the result and the lesson.

Every paid deliverable ships a test plan in `copy.json`: the hypothesis (angle A against angle B), what varies, the
primary metric, the sample needed and a stop rule written before launch. The lint blocks a final ad pack without one.

## 5. Organic posts (R5 §6.2, §6.4)

| Platform | Maximum | Before "more" |
|---|---|---|
| Instagram | 2,200 characters; 5 hashtags per post or Reel since December 2025 | about 125 |
| LinkedIn | 3,000 | about 140 mobile, 210 desktop |
| X | 280 (a URL counts 23; emoji and CJK count 2) | the whole post |
| Threads | 500 | the whole post |
| TikTok | 4,000 | the first line or two |
| YouTube | title 100, description 5,000 | the title and first lines |
| Facebook | very long posts allowed | a few lines |

What the large datasets say (correlational; direction, not cause):

- Hashtags label content and add no reach (Instagram's Adam Mosseri). In Metricool's 2026 study of 24.4 million posts,
  posts with a hashtag averaged 31.7 % fewer views; questions got 36.7 % more comments and comment-focused CTAs 202.8 %
  more comments.
- Captions under 30 words had the highest engagement rate (Socialinsider, 9.1 million posts).
- Replying to comments went with higher engagement within the same account (Buffer, 52 million posts: Threads +42 %,
  LinkedIn +30 %, Instagram +21 %, Facebook +9.5 %, X +8 %); LinkedIn document carousels had a 21.77 % median
  engagement rate against 3.18 % for text posts; on X, text posts beat link posts.
- LinkedIn length: 1,301 to 2,500 characters engaged best in one 2026 dataset; others stress fewer, sharper posts.
  Fight for the first 140 characters and let length follow substance.

Words for every post come from natural-text (the audience's register, no AI tells); for a series, codex-design's
`ledger` keeps hooks and templates from repeating. Bangladesh is Facebook first; the post's market, currency and
places come from the client, never from the writer.
