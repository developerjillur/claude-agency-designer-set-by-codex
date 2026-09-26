# Verifying: sources, claims, confidence

A fact enters a script or copy only after its quote or number was matched in the raw text of a source graded for the
claim. Evidence: `research/R8-deep-research-methods.md` §6 and §10, `research/V1-method-videos-part1.md` (research
checks RC-01 to RC-15).

## 1. How professionals check (R8 §6.1)

- **SIFT** (Mike Caulfield): Stop; Investigate the source; Find better coverage; Trace claims, quotes and media to the
  original context.
- **Lateral reading:** in a study of 45 skilled users, historians and students read vertically and were fooled by logos
  and domain names; fact-checkers left the site, opened new tabs to learn who was behind it, and reached better
  conclusions in a fraction of the time. Judge a site by what others say about it, not by its own pages or its domain.
- **PolitiFact:** the burden of proof is on the speaker; ratings use what was known when the claim was made.
- **Full Fact:** where is it from, what is missing, how does it make you feel.

## 2. The source grades (the tool's A to E, mapped to R8's ladder)

| Grade | Holds (R8 tier) | Use |
|---|---|---|
| **A** primary | law, court filing, official statistics, company filing, original dataset, peer-reviewed paper (retraction-checked), the person's own words on record, a full recording (T1) | cite for facts |
| **B** edited secondary | systematic reviews, intergovernmental reports, agency explainers, reputable news with a corrections policy (T2, T3) | cite; follow to A for key numbers |
| **C** credible trade or expert | trade press, expert sources that cite their evidence; company material attributed as such (T3, T4) | cite with attribution ("the company says") |
| **D** community and opinion | blogs, forums, social posts, reviews, YouTube comments, marketing pages (T4, T5) | the audience's words and leads only, never a fact on its own |
| **E** unverifiable | anonymous pages, content farms, unsourced AI pages, dead links with no archive (T6) | never cite; at most a lead to the origin |

Grade the source and the claim separately: a good source can carry a weak claim (the Admiralty code). The tool's
`check` fails a claim that rests only on D or E sources, and a **key** claim (`claim add --key`, one the piece stands
on) that has neither an A source nor two independent publishers.

## 3. Independence and origin

Two outlets repeating one wire story are one source; apparent confirmation from a single origin is circular reporting.
"Two independent sources" means two origins. Cite the original publisher, never a syndicated copy (the Tow Center found
AI tools citing Yahoo and AOL copies).

## 4. Confidence (R8 §6.3)

- **High:** a grade A source, or two independent B or C sources agree, with no credible dispute. The copy states it
  plainly.
- **Medium:** one reliable secondary source, or sources agree with small differences. The copy attributes it.
- **Low:** a single weak or indirect source, or conflicting evidence. The copy leaves it out or frames it as a claim.
- **Unverified:** not traced. Never used.

For probabilities, the IPCC words: virtually certain 99 to 100 %, very likely 90 to 100 %, likely 66 to 100 %, about as
likely as not 33 to 66 %, unlikely 0 to 33 %. Keep confidence (the evidence) separate from probability (the event).

## 5. Conflicts and dates (R8 §6.5, §6.6)

1. Check that both sources measure the same thing (definition, place, period, method, unit).
2. Prefer the primary and the latest revision; look for corrections.
3. Check independence and incentives.
4. If the conflict is real, give the range, attribute each side, explain the difference. Never average.
5. Mark the claim `conflicting`: the text must say so or drop it.

Record the event, data period, publication, last-update and retrieval dates; write "as of" in the copy for anything
that changes; search again for newer material before stopping (stale facts were a top AI error in the EBU study).

## 6. Per-claim steps (R8 §6.7)

1. Split into atomic claims (one fact each).
2. Find the origin.
3. Fetch the raw text (`research.py fetch URL`), not a summary.
4. Match the quote or number after normalizing whitespace, quote marks and escapes (`research.py verify DIR`: exact,
   then a 90 % in-order match; a fabricated quote comes back unsupported).
5. Read laterally on the publisher and the author.
6. Seek independent confirmation.
7. Record the dates.
8. Grade the source, the claim and the confidence.
9. Archive the page (`research.py wayback URL`).
10. Log it, failures included.

## 7. The research checks (V1 RC-01 to RC-15)

| Check | Pass |
|---|---|
| Grid coverage | every W, plus impact and what next, has a question or an explicit "not relevant" |
| Premise | no question assumes something unverified or false |
| Claim-source match | every claim has an excerpt from its source that states it |
| Corroboration | numbers, accusations and causal claims have two independent sources or a primary document |
| Origin | aggregator and news citations are traced to the original report or data |
| Forums and AI | Reddit, Quora, Facebook or X posts and AI answers are never the only source for a fact |
| High-risk topics | medicine, science, finance, law, elections and politics, religion, communal and cross-border topics have a primary or expert source plus a second source |
| Numbers | each has the unit, date, place, definition and source; conversions recomputed |
| Red-flag words | "scientifically proven", "biggest", "first", "only", "everyone", round percentages: each needs a qualifier and a source, or is cut |
| Chronology | the timeline is in order; key actors and turning points are present |
| Chains | every link of a why-chain is sourced; a speculative end is labelled a hypothesis |
| Breadth | at least three parallel factors, ranked by evidence |
| Recency | time-sensitive facts carry an "as of" date |
| Counterview | contested topics have the strongest opposing case with sources |
| Stakes | "why this matters to a viewer in [country]" is answered with evidence |

## 8. What AI research gets wrong (R8 §3), and the check that catches it

| Failure | Check |
|---|---|
| unsupported citations | `verify`: the quote must be in the source's raw text |
| broken links, syndicated copies | fetch every URL in the run; cite the original publisher; archive |
| confident wrongness | confidence levels; "not found" is an answer |
| shallow sources (content farms over primary sources) | the grades; `check` fails D and E only claims |
| outdated facts | dates on every source; the recency search before stopping |
| altered quotes | exact matching; no stitched fragments |
| one-sidedness | the counter-evidence search in every sub-question |
| forgetting what was found | every finding goes to the ledger or a bank as it is found |
