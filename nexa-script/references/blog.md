# Blog posts and articles

Articles are read, not heard: the reader scans, decides in seconds and leaves if the answer is not there. Evidence:
`research/R4-blog-writing.md` (Google's primary guidance to 2026-09, Nielsen Norman Group reading studies, editorial
practice).

## 1. What the evidence says (R4 §1)

1. Google's bar is non-commodity content: first-hand, expert or original material beyond common knowledge.
2. Scaled content abuse is judged by purpose and value, not the tool: mass AI pages and a page per query phrasing are
   spam.
3. The public rater guidelines (2025-09-11) rate copied or AI-paraphrased low-effort content Lowest, fake AI author
   profiles deceptive and filler before the answer Low.
4. AI summaries cut clicks (8 % against 15 % in one study; position-one CTR down 58 % in another); being cited
   softens the loss.
5. Readers scan: 20 to 28 % of the words on an average visit; the first 10 seconds decide; heading-led scanning works
   best.
6. FAQ rich results stopped showing on 2026-05-07; structured data is optional for AI features.
7. AI tells are fixed with substance (experience, sourced numbers, named examples, a position), not synonym swaps.
8. Conversion works when the product does a real step, the offer fits the post and disclosures sit by the link.

## 2. Workflow (R4 §9.1)

1. The reader, their task or decision, and what they already know.
2. Read the results page (nexa-research): the intent (Know, Do, Website, Visit), the 3 Cs (content type, format,
   angle), the features, the AI Overview and its sources, forums and video. Note what every top result says
   (consensus) and what none says (the gap).
3. Choose the **gain**: original data, a first-hand test, expert input, a worked example, a decision framework or a
   defensible position. It must fit in one sentence.
4. Gather evidence first: dated primary sources, screenshots, measurements, approved quotes, product steps.
5. Fill the brief (below); outline with claim-style H2s in reader-priority order.
6. Draft answer-first, one idea per paragraph; edit in five passes; fact-check each claim with SIFT (Stop,
   Investigate the source, Find better coverage, Trace to the original).
7. Package: title, meta description, slug, alt text, internal links, Article markup, author box, disclosures.
8. After publishing: Search Console queries and AI impressions, engaged time, conversions; update when facts change,
   not to look fresh.

**Brief** (R4 §10.2): topic, primary query, secondary questions (People Also Ask, forums, fan-out); the reader (who,
situation, knowledge, job to be done); intent and the 3 Cs; consensus and gap; the gain and its source; evidence with
dates and `[NEEDS INPUT: ...]` markers for what the client must supply; the H2 outline; visuals; internal links;
business potential 0 to 3 with the CTA type and place; voice and style guide; author and reviewer; a YMYL flag.

## 3. Rules (R4 §10.1)

1. Intent before outline; justify any deviation from the results page's format.
2. The gain is mandatory. If inputs are missing, ask or insert `[NEEDS INPUT: ...]`. Never invent experiences,
   numbers, quotes, customers, authors or photos. The lint blocks a final with a marker still in it.
3. The answer or payoff in the first 100 words; no scene-setting filler.
4. Every statistic has a named source, a link and a date; primary preferred; vendor data labelled; never "studies
   show". The lint fails a figure with no link in its paragraph.
5. Titles: specific and honest; aim for 60 characters or fewer, 70 at most (Google rewrote 99.9 % of titles over 70
   characters in Zyppy's study of 80,959; 51 to 60 had the lowest rewrite rate); H1 consistent with the title.
6. Headings descriptive, front-loaded, readable alone; the main keyword in the title, H1 and intro, and in at most two
   subheads (`lint --keyword`).
7. Paragraphs of 1 to 4 sentences; average sentence under 20 words; split sentences over 25; reading grade 6 to 8 for
   general readers, 10 to 12 for experts.
8. Lists for parallel items, tables for comparisons, callouts for key numbers; bold sparingly; no word-count targets.
9. Descriptive anchors (never "click here"); informative images with descriptive alt text.
10. Article or BlogPosting markup with the real author and dates; no FAQ rich-result promises; no llms.txt work for
    Google.
11. The CTA fits the intent; the product appears only where it performs a step; three CTAs at most; the affiliate
    disclosure next to the link; no fake urgency.
12. A real human byline from the client; disclose AI help where readers would expect it; never an AI byline or an
    invented persona; YMYL topics need a named expert author or reviewer.
13. Change `dateModified` only for substantive edits; a year in the title only for year-specific content.
14. The client's style guide, else AP for blogs; plain words, active voice; close with a next action, never a recap.

## 4. Outline (how-to or explainer, R4 §9.2)

```
Title: [specific outcome or answer] for [reader or constraint]      (50 to 60 characters)
Summary (1 to 2 sentences): the answer, plus what makes this page different (tested, data, experience)
Intro (40 to 100 words): the answer first, one proof line, what is inside
H2 The answer or core method (steps or a decision rule)
   H3 each step with evidence (a screenshot, a number, an example)
H2 What happened when we tried it (first-hand data, surprises, mistakes)
H2 Options compared (table: option, best for, cost, drawback, verdict)
H2 When not to do this (edge cases, risks)
H2 Common mistakes (symptom, cause, fix)          [an in-context CTA where the product does a step]
H2 FAQ (only real questions, 2 to 4 sentence answers)
Close: the next action or decision rule; 2 to 3 related links with descriptive anchors
Author box, disclosures, sources with dates
```

Variants: "best X" lists add the test method, the criteria and a first-hand reason per pick; comparisons lead with a
verdict table; essays run thesis, argument, counter-argument; data studies lead with the finding, then method and
limits. Story shapes from `story.md` still apply to features and essays: an ABT lede, one case told as a nested loop,
a turn where the obvious answer fails, a resolution, a close on a concrete image (R3 T5).

## 5. Five editing passes (R4 §6.3)

1. **Structure:** the right answer, the right format, a clear thesis; cut sections that do not serve it.
2. **Evidence:** every claim sourced or experienced; remove unsupported superlatives.
3. **Line:** shorter sentences, specifics over abstractions, active voice, only hedges that carry meaning.
4. **Copy:** the style guide, names, numbers, links, heading consistency.
5. **Skim test:** read only the title, headings, first sentences and bold text; the argument still comes through.

## 6. Weak and strong (R4 §9.4, illustrative)

| | Weak | Strong |
|---|---|---|
| Title | The Ultimate Guide to Email Marketing in 2026: Everything You Need to Know | Welcome Emails: The 5-Email Sequence We Kept After Testing 9 |
| Intro | In today's fast-paced digital landscape, email remains a crucial tool. In this article we will delve into... | Send the first welcome email within five minutes, keep it under 120 words and ask one question. Below are the five emails we kept after testing nine on 4,200 trial users. |
| Heading | Unlocking the Power of Segmentation | Segment by signup source before job title |
| Evidence | Experts agree subject lines matter. | The plain subject line ("Your login link") beat the clever one on three of four sends. |
| Close | In conclusion, welcome emails are essential for success. | This week, move email one to the five-minute mark and cut it to one ask. Check activation after 14 days. |
| Anchor | click here | our send-time test across 12 newsletters |

## 7. AI tells and the editor's fix (R4 §8)

| Tell | Fix |
|---|---|
| A stock opener ("In today's digital landscape") | open with the answer, a number or a real scene |
| Fluffy headings ("Unlocking the power of X") | state the claim or the question answered |
| The keyword in every heading and paragraph | title, H1 and intro once, then natural language |
| No first-hand detail | add a test, a measurement, a screenshot, a cost or a mistake |
| "Experts say", "studies show" | name, link and date the source |
| AI vocabulary (delve, pivotal, testament, underscore, tapestry), "not just X but Y", triplets | plain verbs, varied rhythm |
| Trailing "-ing" analysis ("highlighting the importance of") | state the concrete consequence |
| A conclusion that restates the post | end with a next action or a decision rule |
| An invented experience or AI author persona | use real inputs or say what was not tested |

## 8. The judge (checklist `blog`)

The judge asks, as yes or no with evidence: intent and answer-first; an information gain the top results lack;
concrete first-hand detail and every statistic sourced; headings that tell the story; a specific human voice;
honest title, dates, byline and disclosures; a next step that feels like help; audience fit. Hard fails: a fabricated
fact, figure, quote, persona or experience; an unsourced statistic; a misleading title; an undisclosed affiliate
relationship; an em dash or spaced en dash.
