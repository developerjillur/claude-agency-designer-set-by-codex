# Evals for nexa-copy

Two kinds, as R9 recommends for every skill we ship (`nexa-script/references/research/` and the skill-lab notes).

## 1. Trigger evals (`triggers.json`)

Twenty queries: ten that should load nexa-copy and ten that should route to another skill. Run each in a fresh Claude Code
session at the user's usual effort setting and record which skill loaded. Target: 18 of 20 or better. Re-run after any
change to the description or to a sibling skill's description.

## 2. Benchmark: baseline against the skill, blind

1. Take a brief from `briefs/` (only the facts the piece may use), or write a new one there.
2. **Baseline:** a fresh session writes the piece from the brief alone, told not to load any skill.
3. **Skill:** a second fresh session writes it following nexa-copy's fast path (and its client level for finals).
   Use a fresh session, not the one that tuned the skill: a writer who has read earlier judges' reasons is no test.
4. **Judge:** the tool's `tournament` command runs both orders with judges from other model families (codex,
   Gemini 3.8 Flash, Gemini 3.1 Pro); a judge's vote counts only when both orders agree, and each judge's reasons
   come back from both orders.
5. Also lint both with the skill's own lint and count errors and warnings.
6. After tuning on one brief, run a brief the skill was not tuned on (a holdout) before claiming anything.

Target: the skill wins at least 80 % of counted votes across the benchmark set, with no hard fail. Record every run in
`results.md` with the date, the models and the raw tallies; never report a win the tallies do not show.
