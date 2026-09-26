# The craft: awareness, research, angles, frameworks, proof

Copy cannot create desire; it channels desire that already exists toward a product (Schwartz). Everything below serves
that: find the desire in the customer's own words, match the reader's awareness, make one specific, provable promise,
ask for one action. Evidence: `research/R5-copywriting.md` (the classics re-read, modern conversion writers, the data
on plain copy, the legal side), with examples written for that file.

## 1. The ten findings that matter most (R5 §1)

1. The reader's awareness decides the first line; the market's sophistication decides the claim.
2. The best lines are found in customers' own words, not invented.
3. Specific claims are believed; generalities and superlatives are discounted.
4. The opening does most of the selling: the headline, the first line before "more", the first three seconds.
5. Plain, objective copy beats promotional copy in usability and conversion data.
6. The real limit is the visible fold, not the field maximum.
7. Proof is regulated: fake or AI-invented reviews, hidden incentives and fake countdowns carry US and UK penalties,
   and the EU bans generic green claims from 2026-09-27.
8. Reviews lift sales, but perfect scores look fake: purchase likelihood peaks at 4.0 to 4.7 stars.
9. Most ideas lose in tests, and small accounts can only detect big differences.
10. Hype and AI tells cost trust; naming "artificial intelligence" as the benefit even lowered purchase intent.

## 2. Awareness and sophistication (Schwartz, R5 §2.1)

| Awareness | Reader state | The first line must | Frameworks | Proof load | Typical placement |
|---|---|---|---|---|---|
| Unaware | does not see the problem | open with a story, a surprising fact or an identity; never lead with the product | story, BAB, curiosity tied to self-interest | light early, strong at the end | cold video feeds |
| Problem aware | feels the pain, knows no fix | name the pain in their words, then show it is solvable | PAS, BAB, AIDA | medium | Meta feed, LinkedIn, organic |
| Solution aware | knows fixes exist, has not chosen | show your mechanism and why other routes fall short | 4Ps, QUEST, AIDA | high: comparisons, demos | non-brand search, landing pages |
| Product aware | knows you, not convinced | answer the main objection with proof | FAB, 4Ps heavy on proof, objection FAQ | highest: reviews, guarantees, data | retargeting, pricing pages |
| Most aware | ready, waiting for the deal | lead with the offer and the terms | offer first | price, terms, deadline | email, brand search, promos |

**Sophistication**, how many similar claims the market has heard: stage 1, state the claim simply; 2, enlarge it; 3,
introduce a mechanism (how it works); 4, improve the mechanism (faster, easier); 5, identification (the reader buys who
they become). Crowded categories sit at 3 to 5, so "better, faster" alone fails and a named mechanism or hard proof is
needed. Set `meta.awareness` in `copy.json`; the judges check the first line against it.

## 3. Research before writing (R5 §4)

1. **The job:** the progress a person wants in a specific circumstance, with functional, social and emotional sides.
2. **The four forces:** the push of the current situation, the pull of the new solution, anxiety about the new, the
   habit of the present. Weak copy only adds pull; strong copy also names the push and shrinks anxiety and habit
   (setup time, risk, switching cost).
3. **Voice of customer**, in order of value: customer and lost-deal interviews; reviews of you, competitors and
   adjacent products (Amazon, Daraz, G2, Trustpilot, app stores, Google Maps); Reddit, Facebook groups and niche
   forums; support tickets, sales calls, cancellation reasons; post-purchase polls. nexa-research collects them into
   the voice bank.
4. **Log one row per verbatim quote:** the quote, its source link, the segment, the awareness, the type (pain, desired
   outcome, trigger, alternative, objection, anxiety, result), intensity 1 to 3, how often it recurs, the proof we hold.
5. **Interview prompts** (switch-interview style): When did you first look for something like this, and what happened
   that day? What were you using before, and what made it stop being good enough? What else did you consider? What
   nearly stopped you? What did you expect, and what happened? How would you describe it to a friend?
6. **Objection checklist:** price or value; will it work for me; effort to switch; trust in the company; risk and
   refunds; compatibility; I can do it myself; timing.
7. **Pick the angle:** the most frequent and most intense pain or desire that you can prove.

Review mining works: Copyhackers' review-mined rehab headline ("If you think you need rehab, you do") won 400 % more
clicks than the control (a single case). Design Academy asked each sign-up "what is your biggest frustration with
design?" and wrote its copy from the answers (Harry Dry). Quote nobody without permission; use their words, never their
identity.

## 4. Angles before words

An angle is a different pain, desire or mechanism, never a synonym of the same one. Paid work ships 3 to 5 angles
(`variants` with an `angle` each); the lint flags two variants on one angle or with mostly the same wording. Caples
saw one mail-order ad sell 19.5 times as much as another in the same space for the same product: the difference was
the appeal (R5 §2.4). Test the angle before the wording.

## 5. Frameworks as fill-in templates (R5 §5)

Frameworks order ideas; they do not create them (hierarchy-of-effects models have little empirical support for a
fixed sequence). Use them as checklists.

- **AIDA:** attention (the reader's situation in one line), interest (the fact that makes it real), desire (the outcome
  in concrete terms, plus proof), action (one CTA and what happens next).
- **PAS:** problem (the pain in their words), agitate (the specific cost of leaving it; facts, not fear), solution
  (product, how it works, proof).
- **BAB:** before (their day now), after (the same day solved), bridge (how the product gets them there).
- **4Ps:** picture (a scene), promise (a specific outcome), prove (data, testimonial, demo), push (the CTA; urgency
  only if true).
- **FAB:** feature (what it is), advantage (why it beats the alternative), benefit (what the reader gets).
- **QUEST:** qualify (who it is for and not for), understand (show you know their situation), educate (the mechanism),
  stimulate (outcomes and proof), transition (to the offer).
- **PASTOR:** problem, amplify, story, transformation or testimony, offer, response.
- **One reader, one idea, one action:** write to one named reader; build the piece on one idea you can state in a
  sentence without "and"; ask for one action.

## 6. What the classics still teach (R5 §2)

- **Hopkins, specificity:** a definite figure implies a test; superlatives make readers discount everything. His
  brewer described filtered air, bottles washed four times and 1,018 yeast experiments while rivals said "pure": the
  pre-emptive claim, being first to explain a process everyone uses. Today specifics need visible proof beside them.
- **Ogilvy, the headline:** most people read the headline, few the body. Today the headline is the first line before
  "See more", the first three seconds of a video, headline 1 of a search ad and the thumbnail text.
- **Caples, test the appeal:** self-interest or news beats curiosity alone; long headlines that say something beat
  short ones that say nothing; "Do you make these mistakes in English?" beat a headline about fearing mistakes.
- **Sugarman, the slippery slide:** every element exists to get the next sentence read.
- **Halbert, the starving crowd:** a market that already wants it beats better copy; under broad targeting a precise
  callout ("for landlords with 1 to 5 units") does part of the targeting.
- **Cialdini, honest levers only:**

| Lever | Honest use | Refuse |
|---|---|---|
| Reciprocity | a real free tool, sample or guide | "free" that hides a paid commitment |
| Commitment | a small first step (quiz, free plan) | pre-ticked boxes, trick consent |
| Social proof | real counts, reviews, named customers | fake or bought reviews, fake followers |
| Authority | real credentials, test data | "experts recommend" with no evidence |
| Liking | a real founder voice, real similarity | fake personas, hidden paid endorsers |
| Scarcity | real stock and real deadlines | timers that reset, a false "2 left" |
| Unity | a shared identity that is true | a manufactured tribe |

A lever may only amplify a fact the reader could verify, and the copy must survive the reader learning everything
behind it.

## 7. Modern conversion writing (R5 §3)

- **Wiebe (Copyhackers):** research first; mine reviews of products your prospects already buy; a message map of
  product facts, persona, motivators, problems and conversion factors; keep master lists of sticky customer phrases.
- **Harry Dry:** cut hard; write the way you talk; open with the fact, not an adjective; write to one reader and name
  them; the button names the result, never a generic "sign up"; use customers' words. Useful judge questions: can I
  visualise it, can I falsify it, could nobody else say it?
- **April Dunford, positioning:** competitive alternatives, unique attributes, the value they enable, best-fit
  customers, market category. Every claim is compared with the reader's alternative (a spreadsheet, an agency, doing
  nothing): name it.
- **Julian Shapiro, landing pages:** purchase rate = desire minus (labour plus confusion). The header says what you
  sell, not a slogan; the subheader says how it works and why the claim is believable; each feature block pairs a blunt
  value header with an objection-handling paragraph and an image; the CTA continues the hero's promise.
- **Plain copy wins in the data:** concise, scannable and objective web text tested 124 % more usable than promotional
  text (NN/g 1997); landing pages at a 5th to 7th grade reading level converted at 11.1 % against 5.3 % for
  professional-level pages (Unbounce 2024, 41,000 pages; correlation). Length follows questions: a page made about 20
  times longer around four researched objections lifted conversion 30 % (Conversion Rate Experts).

## 8. Proof and specificity (R5 §7)

**The specificity ladder:** level 0, vague ("fast payroll"); 1, specific ("payroll in 10 minutes"); 2, verifiable
("median run time 9 minutes across 2,140 payrolls in June 2026"); 3, attributed (a named owner, business and quote).
Push every key claim to level 1, and to 2 or 3 when the claim ledger allows. State the unit, the period, the base (n)
and the source, and put the proof next to the claim. Odd, precise figures read as measured.

**Reviews:** showing five reviews raised purchase likelihood 270 % against none (190 % for cheaper products, 380 % for
pricier ones); likelihood peaked at 4.0 to 4.7 stars and fell toward 5.0; verified-buyer badges added 15 % (Spiegel
Research Center 2017). Show real rating distributions; never hide the negatives; never invent one.

**Claim ledger:** one row per factual claim with its type (number, comparison, superlative, testimonial, review
statistic, free, guarantee, urgency, health, money, environmental), the evidence link and date, the scope (market,
period, n), the disclosure needed, who approved it and when to recheck. In nexa-copy every field that carries a claim
lists its claim ids (from the research pack) or `brief` for a client-given fact; the lint gates the rest.

## 9. AI tells and their fix (R5 §9)

| Tell | Fix |
|---|---|
| a vague benefit ("Boost your productivity") | the task, the time, the number |
| puffery (elevate, unlock, seamless, revolutionize, game-changer, cutting-edge, supercharge, empower) | the fact instead |
| AI vocabulary (delve, tapestry, testament, vibrant, pivotal, crucial, foster, enhance, showcase, underscore) | everyday words |
| copula dodging ("serves as", "stands as", "boasts") | is, has |
| "It's not just X, it's Y" | say Y |
| rule of three ("fast, simple and powerful") | one specific |
| em dashes, emoji bullets, bold everywhere, Title Case | plain lines |
| fake urgency or scarcity | a real date or stock count |
| AI as the benefit ("AI-powered invoicing") | lead with the outcome |
| an unscoped superlative ("the best", "#1", "world-class") | scope and source it, or cut it |
| template openers ("In today's fast-paced world", "Are you tired of", "Imagine a world", "Whether you're X or Y") | start at the reader's moment |

The swap test: a line that still works with a competitor's name in it gets rewritten. The natural-text voice pass
(`copywriter.py lint`, on by default) runs 932 tested rules in 24 languages on every field.

## 10. Weak and strong (R5 §10; numbers are placeholders for ledger facts, brands fictional)

- **Meta feed, problem aware.** Weak: "Elevate your business finances with our seamless AI-powered bookkeeping
  platform. Unlock growth today!" Strong primary text: "Still doing receipts on Sunday night? Snap each one as you pay.
  Tallybook files it under the right tax category for you." Headline: "Tax-ready books, no Sundays".
- **Google RSA, solution aware** (query: invoice software for freelancers). Weak headlines: "Best Invoicing Software",
  "Innovative Solutions", "Click Here Now". Strong: "Freelance Invoicing Software", "Get Paid 9 Days Faster", "Free for
  Your First 5 Clients", "Auto Reminders for Late Payers", "4.8 Stars From 2,300 Reviews".
- **LinkedIn, B2B.** Weak: "In today's fast-paced business landscape, leveraging cutting-edge solutions is crucial."
  Strong: "Your month-end close takes 9 days because approvals live in email. See how 40 finance teams got it to 4."
- **TikTok or Reels, unaware.** Weak: "Hey guys, today I want to talk about something really exciting." Strong: text
  "My sink smelled for 6 months. It was this." Voice: "It wasn't the drain. It was the overflow hole." Product on
  screen by second 3.
- **Landing hero, solution aware.** Weak: "Revolutionize the way you work." Strong H1: "Scheduling for clinics that are
  done with no-shows"; subhead: "Patients confirm by text, rebook in two taps, and your waitlist fills cancelled slots
  on its own. Clinics on Bookwell cut no-shows from 18 % to 7 % in 90 days." Button: "Start filling cancelled slots".
- **Instagram, coffee roaster.** Weak: "Elevate your mornings with our premium artisanal coffee! Rich, bold,
  unforgettable." Strong: "Roasted Tuesday, at your door Thursday. This week's Ethiopia tastes like blueberry jam,
  honestly. Kenya or Colombia next? You pick."
