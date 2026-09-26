# What research hands to writers

The research folder is the shared memory (forgetting found information was the strongest predictor of failed research
tasks, R8 §3); `pack.json` is the one file nexa-script and nexa-copy read. Evidence: `research/R8-deep-research-methods.md`
§9 and §11.4.

## 1. The folder (`research.py new DIR --topic "..."`)

```
DIR/research/
  plan.md                 the question, sub-questions, perspectives, budget, stopping rule (filled first)
  sources.json            every source: id, url, title, publisher, date, kind, grade A to E, accessed
  ledger.json             every claim: id, text, source ids, the quote that states it, where, date, key, status
  notes/voice-bank.json   the audience's own words
  notes/story-bank.json   real people, cases and moments
  notes/competitors.json  what already exists, with hooks and results
  findings.md             the synthesis, written last, from ledger rows only
  budget.json             the session's shared WebSearch count
  pack.json               everything above, checked, for the writers
```

## 2. Claims (`ledger.json`)

`research.py source add DIR --url --title --publisher --date --kind --grade`, then
`research.py claim add DIR --text "one atomic fact" --source s1 [--source s2] --quote "the exact words" [--where
"page 4"] [--date] [--key]`, then `research.py verify DIR`. Statuses: `unverified` (added, or the source could not be
read), `verified` (the quote was found in the fetched text), `unsupported` (not found: fix or drop), and three set by
hand with `research.py claim set DIR c3 --status ... --note "..."`: `manual` (checked by a person, for a video quote
against its transcript or a page the tool cannot read), `conflicting` (sources disagree), `removed`.

`research.py check DIR --level final` fails when a claim has no source or quote, rests only on D or E sources, is a key
claim without an A source or two publishers, is unsupported, or when fewer than 90 % of the claims are verified.

## 3. The banks (`research.py note add DIR --bank ...`)

| Bank | Item fields | Fed by |
|---|---|---|
| voice | `text` (the words as written), `source`, `kind` (comment, review, question, search, dm, interview), `lang`, `likes`, `segment` | `youtube comments --bank`, reviews and forums read by hand |
| story | `text` (the story in one or two lines), `source`, `people`, `turn`, `claims` (claim ids), `mode` | the depth workers |
| competitors | `url`, `title`, `channel`, `hook` (the opening line), `angle`, `result` (views or another known outcome), `length_s`, `published`, `x_median_views`, `notes` | `youtube search --bank`, articles and ads read by hand |

Ids are assigned by the tool (v1, st1, k1); a voice item already in the bank is skipped. Usernames never go in.

## 4. `findings.md` (R8 §9)

```
# Research findings: <topic>   As of <date> | Tier <tier> | Market <country, language>
## Answer in five lines
## Key facts (each: the sentence [c3] and its confidence)
## Contested points (each side, the sources, why they differ)
## Story angles (3), the best evidence for each
## Audience words (the top phrases with counts)
## Gaps in existing content
## Do not say (failed verification)
## Say carefully (medium or low confidence)
## Open questions and what could not be verified
```

Every factual sentence carries its claim ids in brackets; `research.py audit DIR/research/findings.md --dir DIR --level
final` blocks delivery when one does not, or when a tagged claim is not verified.

## 5. The pack (`research.py pack DIR`, `nexa.research-pack/1`)

`topic`, `made_at`, `findings_md`, `sources`, `claims` (all but removed), `story_bank`, `voice_bank`, `competitors`,
and `check` (the gate result at the time of packing). nexa-script and nexa-copy read it:

- `script.py lint FILE --pack research/pack.json --level final` and `copywriter.py lint FILE --pack ... --level final`
  demand verified claims for every claim id the writer used.
- `panel build --evidence research/pack.json` grounds the personas in the voice bank.
- `copywriter.py hooks FILE --pack research/pack.json` puts the competitors' hooks beside the draft's.

## 6. The handoff to writers (R8 §11.4 G10)

Writers get only high and medium confidence claims, with wording guidance ("say it plainly", "attribute it", "give the
range"), plus the do-not-say list. A fact-check table for a finished draft: `line | claim | verdict (supported, partly,
unsupported, contradicted, outdated, unverifiable) | evidence (claim ids) | fix (suggested wording)`.

## 7. Quality gates (R8 §11.4)

| Gate | Pass |
|---|---|
| G1 Plan | `plan.md` filled before searching |
| G2 Coverage | each must-answer sub-question answered or logged as a gap |
| G3 Citations | 100 % of cited claims pass the quote or number match (the best products sit at 78 to 90 %: this is where we beat them) |
| G4 Independence | each key claim has an A source or two origins |
| G5 Recency | time-sensitive claims carry "as of" and a later-update search |
| G6 Balance | contested topics include the strongest counter-evidence |
| G7 Links | none dead; each archived |
| G8 Privacy and copyright | as in `protocol.md` §6 |
| G10 Handoff | writers get only high and medium claims, plus the do-not-say list |
