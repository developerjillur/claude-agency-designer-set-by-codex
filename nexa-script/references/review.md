# The review loop: gates, judges, the audience panel and when to stop

Claude writes; other model families judge; a simulated audience reacts; code aggregates. Every number the panel
produces is labelled **synthetic, directional**: simulated personas, not people, never a forecast of real results.
Evidence and protocol: `research/R10-panels-judges-humanization.md` (sections 1 to 5, 97 sources). The shared engine
is `scripts/nexa_review.py` (identical copies in nexa-copy); the model layer is `scripts/nexa_llm.py`.

## 1. What each instrument is good for (R10 §0 to §3)

- **LLM judges** fit checklists and pairwise comparisons, not taste. Strong judges agree with human preferences in
  over 80 % of pairwise comparisons, about the rate at which humans agree with each other; with a rubric that
  describes every score level, correlation with human scores rose to about 0.9. Their biases are known: order,
  length, self-preference (a same-family writer and judge inflate scores) and a preference for AI-sounding text.
  Hence: binary items with evidence, several families, both orders, and never the writer's notes.
- **Persona panels** get the direction of effects right more often than their size; grounding them in real audience
  texts raised agreement (83 to 86 % against 74 %); they spread less than real people. Ask for behaviour (leave, keep
  watching, remember, comment), never a rating, and never read their numbers as predictions.
- LLMs predicted message effects well in survey experiments (r = .85) but only modestly in the field (r = .34); no
  validated text-only predictor of a script's retention curve exists.

## 2. The loop

| Step | Command | What it gives | Time (measured 2026-09-26) |
|---|---|---|---|
| Gates | `script.py lint FILE --pack research/pack.json --voice` | errors, warnings, notes (offline) | under a second, plus copylint |
| Judges | `script.py judge FILE --brief brief.json` | per checklist item: pass, fail or unstable (majority of 3 judges x 2 runs, shuffled item order); two 1-to-5 scales with IQR; best lines | about 30 s for 6 runs |
| Understanding | `script.py understand FILE --brief brief.json` | the retell and first-time-learner tests | about 30 s |
| Panel | `script.py panel run FILE --panel panel.json --judge judge.json` | survival, spikes, the fix list (5 at most), the keep list, the noise probe | about 20 s for 10 personas; 10 calls in parallel for 100 |
| Revision | Claude edits | fixes only on fix-list lines and their neighbours | |
| Preference | `script.py prefer OLD NEW --panel panel.json` | paired wins overall and per family against the binomial threshold | about 10 s for 10 personas |
| Guard | `script.py guard OLD NEW --keep review.json --baselines baselines.json` | edit budget, keep list, specificity, rhythm, generic-baseline overlap | offline |
| Decision | `script.py decide --round N --lint ... --judge ... --review ... --prefer ... --guard ...` | accept, continue or stop, with reasons | offline |
| Best version | `script.py tournament V1 V2 V3 --brief brief.json` | a both-orders pairwise ranking | about 30 s a pair |

Levels: a **draft** gets the lint only; a **standard** piece gets the lint and the judges; a **client final** or a
flagship gets the whole loop, with a validated panel when the channel has past results.

## 3. The panel

- **Build once per client and format** and reuse it across drafts so rounds stay comparable:
  `script.py panel build DIR --brief brief.json --evidence research/voice-bank.json --n 100`. Evidence = real audience
  texts (comments on the client's and competitors' posts, reviews, questions, search terms) from nexa-research's
  voice bank. Cards cite the evidence ids they rest on; invented ids are dropped and reported.
- **Segments** (default): core 30, newcomers 25, sceptics 15, price- or time-pressed 15, lapsed 10, adjacent 5.
  Replace them with the channel's real mix when analytics exist.
- **Validate before trusting:** `script.py panel validate --panel panel.json --items past.json` with 5 to 10 past
  pieces and their real results (`[{"id", "text", "actual"}]`). The panel must rank them with Spearman 0.4 or more;
  until then its fixes are hints and the judges and gates decide (R10 §5.2).
- **Tasks** (R10 §5.2): T1 feed stop (with `--hooks`), T2 where each person leaves and why (a reason tag: slow,
  confusing, salesy, irrelevant, repetitive, fake, other), T3 what they do after (like, comment, share, save, click,
  follow, reply, buy, nothing), the line they remember, the line that felt fake and the one that confused them, T4
  intent for ads, T5 pairwise preference (`prefer`).
- **Noise probe:** five personas are asked again in a new batch of the same model; if their leave points (by chunk:
  the hook, 0 to 15 s, 15 to 30 s, 30 to 60 s, the rest) disagree more than 30 % of the time, do not act on the panel
  this round (`act_on_panel: false`).
- **Muted viewers:** the judges and personas see each beat's picture and on-screen text with its first line, and a
  brief note when captions are burned in (`meta.captions`).

## 4. Reading `review.json`

- `finished` with a Wilson 95 % interval: at n = 100, p = 0.5 is about plus or minus 9.6 points.
- `survival` and `spikes`: a spike is a line where the hazard is at least twice the median and 5 or more personas
  leave.
- `fixes` (at most five): the line, the tag, the weighted support, the quotes, whether the judges failed the same
  lines. An issue enters only with 10 % support overall or 20 % in a priority segment, seen in both model families;
  the rest goes to `watch`.
- `comments`: up to 24 comments the personas would write, taken in turn from every segment so the biggest group does
  not drown the sceptics; read them as the audience's likely reactions, in their register.
- `keep`: lines remembered by 15 % or more, or named best by two judges. They are frozen next round. A line fans
  remember and sceptics call fake is `polarising`: a human decides.

## 5. Revising

- Name the problem, choose the fix yourself: wrong prescriptions and wrong locations caused most self-refine failures
  in the studies R10 reviewed. Never paste a judge's or persona's rewrite.
- **Revision** (the loop): at most 25 % of tokens change per round, only on fix-list lines and their neighbours;
  keep-list lines stay word for word.
- **Rewrite** (after a hard failure: invented facts, a broken promise, the wrong format): write a new draft, then
  `guard --rewrite` (no edit budget or keep list; specificity, rhythm and the baseline test still apply) and compare
  it with `prefer` as a fresh round 1.
- **Keep the writing alive** (R10 §5.5): judges favour familiar, AI-written and longer text, and loops reward-hack,
  so: specificity must not fall; lint findings must not rise; the rhythm stays in the creator's range; the draft must
  not move closer to what a generic model writes from the brief alone (`script.py baselines`); track love (share,
  save, remember) as well as hate. When a hook fails, write 5 hooks including unlikely ones and test them all.

## 6. Accepting and stopping (R10 §5.4)

- **Cap:** 2 revision rounds, 3 for flagship pieces. Gains come early and scores inflate with iteration.
- **Continue only if** a gate fails, a judge item fails by majority, or a fix has at least 20 % support in the core
  segment.
- **Accept a revision only if** it wins the paired panel comparison with at least 61 of 100 personas (39 of 60, 21
  of 30) in each model family, the judges' both-orders check does not prefer the old one, no gate breaks and the
  guard passes. Personas from one model are not independent, so 61 % is a floor.
- **Stop when** the gates pass and the latest pairwise result sits between 40 % and 60 %, at the cap, or on
  oscillation (a fixed issue returns, or one line tops the fix list twice).
- **The plain draft is the bar** (2026-09-26 benchmark): a client final plays a plain draft written from the brief
  alone (`script.py baselines`, or a fresh session given only the brief) in the tournament. The tournament keeps every
  judge's reason from both orders: read them before round 2, fix what they name, and if the plain draft still wins,
  say so in the delivery note with the reasons. In that benchmark the skill's drafts passed every checklist item yet
  lost the head-to-head: a checklist finds faults, a pairwise read finds the better piece.
- **Slow models:** every model call stops after `NEXA_LLM_TIMEOUT` seconds (240 by default) and is asked once more;
  a codex call that stalls while its MCP servers start is the usual cause (`NEXA_CODEX_EXTRA_FLAGS` passes extra
  flags to codex).
- **Ship the best version, not the last:** a both-orders tournament among the survivors, then a blind human read of
  the top two for client work.

## 7. What never to do

- Report a panel number as a prediction of views, retention, CTR or sales.
- Let a judge see the writer's notes, earlier scores, authorship or which version is newer.
- Judge Bangla quality on an English-only reading: judges inflate scores in non-Latin scripts; native-reader labels
  set the Bangla thresholds (R10 §7).
- Loop past the cap hoping for a higher score.
