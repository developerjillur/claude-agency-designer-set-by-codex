# From research to script

nexa-research finds, reads, verifies and packs; nexa-script turns the pack into a story. A script never states a
fact the pack or the brief does not hold. Evidence: `~/.claude/skills/nexa-research/references/research/`
(`R8-deep-research-methods.md`, `V1-method-videos-part1.md`), `research/R1-youtube-longform.md` §7.

## 1. What the pack holds

`research.py pack DIR` writes `research/pack.json` (`nexa.research-pack/1`):

| Part | Holds | The script uses it for |
|---|---|---|
| `claims` | every claim with its source ids, the quote that states it, `status` (verified, manual, unsupported, removed) and `key` | the claim ids on beats; `lint --pack --level final` demands verified claims |
| `sources` | url, publisher, date, grade A to E | the source sheet in the description; which claims can carry weight |
| `story_bank` | real people, cases and moments with their sources | the character, the turn, the scene (never invented) |
| `voice_bank` | real audience words: comments, reviews, questions, search terms | hooks in the audience's words, thought narration, panel grounding |
| `competitors` | the videos or pages already covering the topic: angle, hook, length, results | the gap, the angle, the feed-stop lineup |
| `findings_md` | the synthesis: what is known, contested and unknown | the outline, the counterpoint, the "as of" dates |

## 2. The order of work

1. **Classify** the piece: a What (news), a Why (explainer) or a How-to (tutorial) (V1). The class sets the research
   mode and the outline.
2. **Demand and coverage** (R1 §7, V1): what the audience asks (comments on outliers, People Also Ask, search
   suggestions in English, Bangla script and Banglish), what competitors already made, and a one-line gap.
3. **Question grid:** who, what, when, where, why, how, plus impact and what next; each answer chained into the next
   question; every question premise-checked (V1). AI may draft the grid; answers come only from sources opened and
   read.
4. **Depth, three modes** (V1): **sequence** (dated events, a timeline), **breadth** (parallel factors ranked by
   evidence), **chain** (why after why, each link sourced, to a documented point zero, or labelled a hypothesis). What
   videos need sequence; Why videos need all three.
5. **Counter-evidence:** the strongest opposing case and its best sources. It powers the midpoint twist and keeps the
   piece fair (V1.3).
6. **Primary material,** cheapest first: official statistics, documents, expert interviews, on-ground interviews.
7. **Freeze the ledger:** `research.py check DIR --level final` must pass before the final script.

## 3. Claims on beats

- Every beat with a number, a money figure, a study, "according to" or "experts" carries `claims`; the lint gates it
  (a warning in a draft, an error in a final).
- `brief` (or `brief:fact-3`) marks a fact the client gave in `facts_given`.
- A claim marked `key` needs grade A or two independent publishers (`research.py check`).
- Say it as strongly as its evidence: firm when verified, one plain caveat when contested, cut when unsupported
  (V6-R6). Numbers get their unit, date, place and definition; "as of" dates for anything that changes.
- Show key evidence on screen (a highlighted headline or document) and list the sources in the description: in
  high-trust explainer markets visible sources and published corrections are part of the product (Dhruv Rathee's
  research documents, R1 §2.10).

## 4. From the pack to the story

- **Find the story in the research** (`story.md` §1): the story bank gives the character and the turn; the ledger
  gives the stakes; the counter-evidence gives the midpoint; the findings give the reveal. Look for the "there's more
  going on" layer (Johnny Harris, R1 §2.6).
- **Hooks from the voice bank:** the viewer's own questions and words make the strongest hooks and thought-narration
  lines (V2 hook 1; V6-R7). Quote nobody without a source; paraphrase the pattern, not the person.
- **Angle from the competitors:** read their hooks, lengths, angles and the questions left in their comments; the
  gap is what none of them answered.
- **Panel from the voice bank:** `script.py panel build DIR --brief brief.json --evidence research/pack.json` grounds
  every persona card in real audience texts (R10 §2.3).
- **Feed-stop lineup from the competitors:** 6 to 8 real hooks with known results beside the draft hooks
  (`hooks.md` §6).

## 5. When the research is thin

- Say so, and ask for the missing input: a `[NEEDS INPUT: ...]` or `[PROOF NEEDED]` marker in the draft, never a
  plausible invention. The lint blocks a final with a marker left in it.
- Narrow the promise to what the evidence supports, or turn the gap into the story ("nobody has measured this; here
  is what we could find").
- Never fill a gap with pop science, a round number, a composite presented as a real person, or an AI answer whose
  source you did not open.
