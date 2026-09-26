# Benchmark results

## 2026-09-26, run 1: a fast-path draft against a plain baseline (Instagram Reel, 35 s, English)

- **Brief:** a Dhaka street-food channel; why a one-oven bakery sells out by 9 a.m.; five facts given; the audience's
  objection "another hype video"; the goal "watch to the end and follow".
- **Baseline:** a fresh Claude subagent, no skill, narration only.
- **Skill:** the fast-path draft (beats, loops, tension, roles; lint clean but for a runtime warning).
- **Judges:** codex, Gemini 3.8 Flash, Gemini 3.1 Pro, both orders, narration only.
- **Result: the baseline won 3 to 0** (every judge agreed in both orders).
- **Why, in the judges' words:** the baseline answered the audience's "hype" objection and asked for the follow aloud;
  the skill draft left the follow ask on screen only, ignored the objection and added a detail the brief never gave
  (a sign flipping at 9).
- **Changes made the same day:** `lint --brief` (objections answered, the goal's ask said aloud, must-avoid kept), a
  `brief` item first in every judge checklist, and a brief check in the fast path before the gate.

## 2026-09-26, run 2: the judges' fix list, as a rewrite

- **Why a rewrite:** the run 1 draft showed moments nobody filmed (a sign flipped at 9:02, a golden loaf beside the
  pale one). An invented event shown as real is a hard fail, so v2 was a new draft checked with `guard --rewrite`.
- **What changed:** the follow ask said aloud; the objection voiced and answered ("If that sounds like another hype
  video, count the loaves"); every picture limited to what can be filmed on the day, or shown as text.
- **Judges (3 x 2 runs):** the run 1 draft failed the `brief` item; v2 passed every item (the first-line and
  publishable scales went from 4 and 3 to 4 and 4).
- **Tournament against the same baseline: baseline 2, v2 0, one judge split** (codex chose whichever draft it read
  first).
- **Why, in the judges' words:** the baseline opened on the scene with both times (the 7 a.m. line, sold out by 9),
  while v2 left the line to the end; codex called "this bakery turns people away" a claim the facts do not make.

## 2026-09-26, run 3: round 2, on the tournament's reasons

- **What changed:** the hook became the scene ("The line starts at 7 a.m. By 9, this bakery is sold out."); the close
  named the choice ("200 good loaves beat 400 pale ones"); the ask called back the objection ("Follow for the numbers
  behind the next Dhaka food spot"). natural-text's voice pass caught a "follow for more" on the way.
- **Judges:** every item passed (4 and 4).
- **Tournament: baseline 2, v3 1.** Codex chose v3 in both orders: it "makes the bakery's one-oven limit the story"
  and does not give the owner "an unverified motive". Both Gemini judges chose the baseline for its ask, "Follow for
  the story behind the food, not the hype": the audience wants "the story behind a food spot", and v3 offered them
  numbers.
- **Stopped at the two-round limit.** The lessons went into `references/hooks.md` (the scene the facts give beats an
  interpretation of it) and `references/formats.md` (the ask names what the audience wants, in the brief's words).
- **Fixed on the way:** the tournament now returns each judge's reasons from both orders (a loss with no reasons
  cannot be fixed); the guard no longer counts "7," and "7." as two details, or a number said once instead of twice
  as a lost one; `baselines` writes each plain draft as a file for the tournament.
- **What this says:** a checklist finds faults, a head-to-head read finds the better piece. Drafts that pass every
  item can still lose to a plain draft, so a client final now plays a plain draft (SKILL.md §6).

## 2026-09-26, run 4: a holdout on a new brief

- **Why:** runs 2 and 3 tuned drafts to one brief; a holdout shows whether the lessons carry to a new one.
- **Brief:** a Chattogram channel; a port tea stall that still charges 10 taka; six facts; two objections ("10 taka
  tea must taste like water", "the price has probably gone up by now"); the goal "save it for the next trip".
- **Both drafts by fresh sessions:** one given only the brief, one told to follow this skill's fast path (standard
  level, no judges). The skill draft passed `lint --level final --voice` clean at 32.1 s; the plain draft drew two
  warnings (13 s with no turn, an unsourced number) that a reader would not notice.
- **Tournament: 0 to 0, all three judges split.** Each judge preferred whichever draft it read second, in both orders:
  the two drafts are equal to these judges. Run 1 was 0 to 3.
- **What this says:** the updated skill now writes as well as a plain draft on a brief it was not tuned on; it does not
  yet write better. The judges' order bias is strong, which is why a vote counts only when both orders agree.
