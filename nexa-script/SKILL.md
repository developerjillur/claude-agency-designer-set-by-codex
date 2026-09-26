---
name: nexa-script
description: "Writes complete, production-ready scripts and articles like a senior head writer: YouTube long-form (explainers, documentaries, video essays, tutorials, commentary, list videos, story vlogs), Shorts, Reels and TikToks, video ads and UGC briefs, talks and podcasts, blog posts and newsletters, in English, Bangla, Banglish, Hindi and more. It works like a channel team: studies the channel and its audience, picks the topic, researches every fact through nexa-research, finds the story (a caused change, a turning point, real stakes), builds the hook with the title and thumbnail, drafts an A/V script with loops, tension and visuals, then runs a review loop: an offline lint of research-based rules, judges from other model families, a 100-persona audience panel grounded in real comments, retell tests and fix-and-rescore rounds. Use it whenever someone wants a script, a hook, narration for a video, or a blog post or article ('script likho', 'youtube video script', 'reels script banao', 'blog likhe dao'). Not for single captions, posts or replies (natural-text) or for ads copy, emails and product text (nexa-copy)."
allowed-tools: Bash(python3 ~/.claude/skills/nexa-script/scripts/script.py:*), Bash(python3 ~/.claude/skills/nexa-research/scripts/research.py:*), Bash(python3 ~/.claude/skills/codex-design/scripts/design.py:*), Read, Write, Edit
---

# nexa-script

Claude is the head writer: the channel study, the topic, the story, the words and every judgement are Claude's. The
tool measures and checks (timing by language, about a hundred lint checks from the research, the loop ledger, the tension map,
claims against the research pack), renders the A/V script, and runs the review loop with judges from other model
families and a simulated audience. Command prefix: `python3 ~/.claude/skills/nexa-script/scripts/script.py`.

## Fast path (every script: do exactly this)

1. **Start the folder:** `script.py new DIR --format FORMAT --lang en|bn|banglish|hi --target SECONDS --title "..."`.
   Fill `DIR/brief.json`: the channel or brand, the audience (who, what they know, what they want, their
   objections), the goal, the platform, `facts_given`, `must_include`, `must_avoid`, `mode` (nonfiction by default).
   Ask one question only when a must-have is missing.
2. **Research every fact** with nexa-research (`research.py new DIR --topic "..."`, then its fast path) unless the brief
   gives every fact the script needs. Pack it: `research.py pack DIR/research`.
3. **Find the story and the promise** before a word of script: the five story questions, the change line and PP1
   (`references/story.md` §1), then the promise contract with 3 titles and 3 thumbnail ideas
   (`references/hooks.md` §1).
4. **Draft in `DIR/script.json`** on the format's beat map (`references/formats.md`): per beat the narration, the
   picture, the on-screen text, roles, loops opened and closed, claim ids, and a tension score.
5. **Check it against the brief, then gate it.** Read the brief again: every audience objection answered in their
   words, the goal's call to action said aloud (and shown), and nothing added that the brief or the research does not
   hold (a prop, a place, a time, a motive, a number). Then `script.py lint DIR/script.json --brief DIR/brief.json
   --pack DIR/research/pack.json --voice`. Fix every error and warning, or keep a warning only with a reason you can
   say in one line. Read the notes. (In the 2026-09-26 benchmark a draft that skipped the brief's objection, left the
   follow ask on screen only and added a sign the brief never mentioned lost 0 to 3 to a plain draft that did not.)
6. **Render and show:** `script.py render DIR/script.json` writes `script.md` (the A/V table, the loop ledger, the
   sources), `roadmap.md` (for on-camera creators) and `narration.txt` (for a voice). Offer the review loop in one
   line.

**Client level** (a client's script, anything published under a client's name, a flagship video, or the user asks
for the best): after the gate, run the loop in §6 (judges, understanding, the panel, revision, preference, guard,
decision; two rounds at most) and deliver the best version with a short review summary. Articles follow
`references/blog.md` with the same gate and judges.

## 1. Understand the channel before the topic

A script is written for one channel and one audience. Before choosing a topic, learn (from the user, the brief and
nexa-research):

- **Mission and objective:** what the channel or brand is for, what this video must do (views, subscribers, leads,
  sales, trust), and for whom.
- **Content type, category and niche:** the formats that work there, the tone, the length.
- **The audience:** country, language mix, age, what they already know, what they complain about and ask, in their
  own words (the voice bank: comments on the channel and on competitors).
- **What performs:** the channel's outliers (videos far above and below its own average), their packaging, and,
  when the user can share them, retention graphs and the "typical retention" line. Judge against the channel's own
  numbers, never against internet benchmarks (`references/retention.md` §1).
- **Competitors:** who already covers the topic, their hooks, angles and lengths, and the questions left in their
  comments.

Write what you learn into `brief.json`. In Bangladesh the audience is Facebook first; the market comes from the
client, never from the writer's language or location (`references/south-asia.md`).

## 2. Pick the topic

- **A topic signal:** a trend, a "wow" (a surprising link or contrast), a demand the audience keeps repeating, or a
  proven angle (V2).
- **Core, Casual, New:** would core fans, casual viewers and new viewers each want it (Galloway, R1 §2.2)? Familiar
  plus unexpected; about 80 % proven formats, 20 % experiments.
- **The glance test:** can you draw the thumbnail and say the promise in one line today? If not, the idea is not
  ready.
- **The gap:** what none of the existing videos answered (from the competitors' comments).
- Write the one-line wow and the gap into the brief.

## 3. Research (nexa-research)

Every factual line carries a claim id from the research pack or `brief` for a client-given fact; `lint --level final`
blocks unverified claims. The order of work, the three depth modes (sequence, breadth, chain), counter-evidence for
the twist and how the pack feeds hooks, stories and the panel: `references/research-to-script.md`. When the research
is thin, say so and narrow the promise; never fill a gap with a plausible invention.

## 4. The story and the hook

- **Story** (`references/story.md`): a caused change chained by but and therefore; the skeleton Hook, Identity,
  Conflict, Choice, Change, Value; PP1 at 10 to 25 % (never beat 1), a midpoint turn at 40 to 55 %, PP2 at 75 to 85 %;
  concrete, true stakes in the first 20 %; a loop ledger where every loop closes and the main one closes last; one
  zoomed scene at the turn (place, action, the exact words or thought, the key line staged with a pause); an ending
  on shown change with no stated moral.
- **Hook** (`references/hooks.md`): the package, the first frame, the first line and the overlay make one promise;
  the opening confirms it and gives more than the title by 0:30; formulas (break + stakes + gap, the belief break,
  the collision line, the anchor opener); every hook literally true to the body. Ads ship 5 hooks of at least 4 types.
- **Retention** (`references/retention.md`): a question, turn or new loop at least every 60 s in long-form and 12 s
  in a short; re-hooks at every section; a texture change every 20 to 45 s; sponsors inside an open loop, after the
  first payoff.
- **The ear** (`references/ear.md`): one idea per sentence, varied rhythm, numbers the way people say them, commit
  where the evidence is firm, talk to one viewer, voice their real doubts.

## 5. Draft

- Take the beat map for the format (`references/formats.md` §2 to §5); `new` has already written it with the roles.
- Write narration and picture together (the A/V script): a concrete, shootable visual every 1 to 3 sentences, every
  number with an on-screen form, captions burned in for shorts and ads (`meta.captions`).
- Words come from natural-text: casual, specific, in the audience's own words; `lint --voice` runs its checks.
- Fill `tension` (q, s, u, p, 0 to 3 each) per beat for anything over a minute, `roles` for the skeleton, `emotion`
  tags for the wave, `story.key_moment` and `story.key_line` for the scene.
- Mark what you cannot know: `[NEEDS INPUT: ...]` or `[PROOF NEEDED]`. A final cannot ship with one left.

## 6. The review loop (client level)

| Step | Command |
|---|---|
| Gate | `script.py lint FILE --pack research/pack.json --voice --level final` |
| Judges (3 judges x 2 runs, other families) | `script.py judge FILE --brief brief.json` |
| Understanding (retell, first-time learner) | `script.py understand FILE --brief brief.json` |
| Panel, once per client and format | `script.py panel build DIR --brief brief.json --evidence research/pack.json --n 100` |
| Validate the panel (past pieces with real results) | `script.py panel validate --panel panel.json --items past.json` |
| Panel reaction | `script.py panel run FILE --panel panel.json --judge judge.json [--hooks hooks.json]` |
| Revise (Claude) | fix only fix-list lines and neighbours, 25 % of tokens at most, keep-list lines frozen |
| Preference (new vs old) | `script.py prefer OLD NEW --panel panel.json` |
| Guard against blandness | `script.py guard OLD NEW --keep review.json --baselines baselines.json` (`--rewrite` after a hard failure) |
| Decide | `script.py decide --round N --lint lint.json --judge judge.json --review review.json --prefer p.json --guard g.json` |
| Best version, against a plain draft | `script.py tournament plain.txt V1 V2 --brief brief.json` (a plain draft from `baselines` or a fresh session given only the brief) |

The plain draft is the bar: a checklist finds faults, but only a head-to-head read finds the better piece (in the
2026-09-26 benchmark drafts that passed every checklist item still lost to plain ones). The tournament keeps each
judge's reasons from both orders; read them before the next round, and if the plain draft still wins, say so.

Rules (R10, `references/review.md`): two revision rounds, three for flagships; accept a revision only when it wins at
least 61 of 100 paired preferences in each model family, breaks no gate and passes the guard; the panel's fixes count
only after it has been validated on past results (Spearman 0.4 or more) and when its noise probe agrees; name each
problem and choose the fix yourself; ship the best version, not the last. Every panel number is labelled synthetic
and directional, never reported as a forecast.

A judge run takes about 30 s (6 runs across codex and two Gemini models); a 10-persona panel about 20 s; run long
steps in the background and keep working.

## 7. Deliver

- `script.md` (the A/V script with the promise, the hook variants, the loop ledger and the claim ids), `roadmap.md`
  (on camera), `narration.txt` (voice), the title and thumbnail options, the source list for the description.
- For client work, a short review note: the lint result, the judges' fails fixed, what the panel flagged and what
  changed, the best-version pick, and what still needs the client (every `[NEEDS INPUT]` resolved).
- Next skills: nexa-speech for the voice, nexa-video-creator or nexa-remotion for the edit, codex-design for the
  thumbnail, agy-watch-video to check the finished video (captions against speech, pacing).

## 8. Honesty (non-negotiable)

- No invented facts, numbers, quotes, people, customers, reviews, events or experiences in factual work; composites
  and reconstructions are labelled; `story.mode` says what the piece may contain (`references/story.md` §11).
- No pop science (22 times more memorable, goldfish attention, oxytocin, dopamine hits, "your brain is wired").
- No hooks the body does not pay, no fake loops, no fake urgency, no improvement percentages without a measurement.
- Ads: no personal-attribute callouts, no cure, guaranteed-result or quick-money claims; paid creators disclose early;
  licensed music; realistic synthetic people or events carry the platform's AI label.
- Never an em dash or a spaced en dash, in any language.

## 9. Commands

| Command | Does |
|---|---|
| `doctor` | engines (codex, Gemini), the voice lint, formats, modes, roles |
| `new DIR --format F --lang L --target S` | brief.json and script.json on the format's beat map (never overwrites) |
| `lint FILE [--pack P] [--voice] [--level final] [--keyword K] [--json]` | the offline rules (exit 1 on an error) |
| `timing FILE [--wpm N]` | seconds per beat at the language's pace |
| `render FILE [--out DIR]` | script.md, roadmap.md, narration.txt |
| `judge`, `understand`, `panel build / validate / run`, `prefer`, `baselines`, `guard`, `decide`, `tournament` | the review loop (§6) |

`FILE` is a `script.json` (`nexa.script/1`, fields in `references/formats.md` §7), a narration `.txt` (paragraphs
become beats) or a markdown article `.md`. Set `NEXA_LLM_FAKE=1` for offline dry runs of the model steps.

## 10. References

- `references/hooks.md`: the promise contract, the three layers, formulas, weak and strong openers, hook packs,
  titles and thumbnails, Bangla hook lines.
- `references/story.md`: finding the story, but and therefore, the skeleton and PP1/PP2, stakes, loops and bridges,
  the tension map, scenes (PAST), emotion, devices, endings, truth modes, AI tells.
- `references/formats.md`: pace and word budgets, beat maps for every format, ads and UGC briefs, the A/V script, the
  roadmap, chapters, the script file.
- `references/retention.md`: what platforms measure, the retention architecture, measured reference values, learning
  from the graph.
- `references/ear.md`: writing for the ear, rhythm, numbers, commitment, delivery and the retell test.
- `references/blog.md`: articles: intent, information gain, answer first, titles, structure, sourcing, conversion.
- `references/research-to-script.md`: the pack, claims on beats, from research to story.
- `references/review.md`: judges, the panel, reading the review, revising, accepting and stopping.
- `references/south-asia.md`: Bangla, Banglish and Hindi scripts for Bangladesh and India.
- `references/checklists.json`: the judges' yes-or-no items and hard fails per format.
- `references/research/`: the research behind every rule (R1 YouTube long-form, R2 short-form and ads, R3
  storytelling, R4 blog, R10 judges and panels, V2 to V6 the reference videos, 2026-09-26). They are evidence, not
  rules.

## The family

natural-text writes every word (the voice backbone); nexa-research finds and verifies every fact; nexa-script builds
scripts and articles; nexa-copy writes ads, emails, outbound and product copy. They share one review engine
(`nexa_review.py`) and one model layer (`nexa_llm.py`), copied byte for byte and checked by the tests.
