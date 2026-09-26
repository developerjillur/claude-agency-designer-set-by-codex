# Benchmark results

## 2026-09-26, run 1: a fast-path draft against a plain baseline (Facebook shop post, Bangla)

- **Brief:** a Dhaka seller of raw Sundarbans honey; eight facts given (April 2026 harvest, strained, never heated,
  can crystallize in the cold, ৳650, delivery ৳60 or ৳120, cash on delivery); the reader's objections "is it real or
  mixed with sugar?" and "why does raw honey crystallize?".
- **Baseline:** a fresh Claude subagent, no skill.
- **Skill:** the fast-path draft (facts only, the price and delivery terms, the honest limit; lint clean).
- **Judges:** codex, Gemini 3.8 Flash, Gemini 3.1 Pro, both orders.
- **Result: the baseline won 3 to 0.**
- **Why, in the judges' words:** the baseline opened on the reader's situation (tea, the children) and voiced their
  worry about sugar before answering it with the facts, admitting that a seller's word alone is no proof; the skill
  draft "reads merely as an impersonal list of specifications".
- **Changes made the same day:** `lint --brief` (objections answered, the reader's situation, the brief's action,
  must-avoid kept), a `brief` item first in every judge checklist, and a brief check in the fast path. Brief
  objections should be logged in the customer's own words and language, so the check can read them.

## 2026-09-26, run 2: the worry answered

- **What changed:** the reader's worry voiced first in their words ("চিনি মেশানো নয় তো?"), with the admission that a
  seller's word is no proof; the facts after it; the same price, delivery and payment lines.
- **Judges (3 x 2 runs):** the `brief` item now passes; only `scannable` failed (the order facts sat in running
  lines). The first-line and publishable scales went from 3 and 3 to 4 and 4.
- **Tournament against the same baseline: baseline 3, v2 0.**
- **Why, in the judges' words:** the baseline named both uses the brief gives (tea and the children) where v2 named
  only the children; it set the order facts in labelled lines, said what cash on delivery means for the buyer ("pay
  when the honey is in your hands") and gave two easy ways to order.

## 2026-09-26, run 3: round 2, on the tournament's reasons

- **What changed:** both uses in the first line; the order facts in labelled lines (পরিমাণ, দাম, ডেলিভারি, পেমেন্ট);
  cash on delivery explained; two ways to order.
- **Judges:** every item passed (4 and 4).
- **Tournament: baseline 2, v3 0, one judge split** (codex chose whichever it read first).
- **Why:** both Gemini judges found v3 "clipped" and "transactional" next to the baseline's spoken joins ("আরেকটা কথা
  আগেই বলে রাখি", "সোজাসুজি বলছি"); the brief asked for a warm, honest voice, and headline shorthand with a colon
  ("প্রথম প্রশ্ন: ...") read as brisk.
- **Stopped at the two-round limit.** The lessons went into `references/product.md` §6: open on every use the brief
  names, voice the worry, the order facts in labelled lines, two ways to order, warm means whole spoken sentences. Its
  old "strong" example was itself the losing spec-list style and was replaced.
- **What this says:** the drafts now pass every checklist item and still lose the head-to-head. A client final now
  plays a plain draft in the tournament (SKILL.md §5), and the reasons come back with the result.

## 2026-09-26, run 4: a holdout on a new brief

- **Why:** runs 2 and 3 tuned drafts to one brief; a holdout shows whether the lessons carry to a new one.
- **Brief:** a small Dhaka leather workshop; a hand-stitched cow-leather wallet; ten facts (Savar tannery, waxed
  thread, a free stitch repair for 6 months, ৳1,450, delivery, cash on delivery); the objections in the buyer's own
  Bangla ("আসল চামড়া তো, নাকি রেক্সিন?", "ছবির মতো আসবে তো?"); the action "order by inbox".
- **Both drafts by fresh sessions:** one given only the brief, one told to follow this skill's fast path (standard
  level, no judges). The skill draft opened on the buyer's two questions, set the order facts in labelled lines and
  passed `lint --level final` clean.
- **Tournament: plain 1, skill 0, two judges split.** Gemini 3.1 Pro chose the plain draft in both orders because it
  said who makes the wallet ("ঢাকায় আমাদের ছোট্ট ওয়ার্কশপে"); codex and Gemini 3.8 Flash split. One Flash reading
  called "ছবিতে সাইজ বোঝা কঠিন" a reason the brief never gave.
- **What this says:** close to parity on a brief the skill was not tuned on (run 1 was 0 to 3), not yet better. The
  maker lesson went into `references/product.md` §6.
