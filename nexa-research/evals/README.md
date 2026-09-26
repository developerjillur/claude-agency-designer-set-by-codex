# Evals for nexa-research

Two kinds, as R9 recommends for every skill we ship (`nexa-script/references/research/` and the skill-lab notes).

## 1. Trigger evals (`triggers.json`)

Twenty queries: ten that should load nexa-research and ten that should route to another skill. Run each in a fresh Claude Code
session at the user's usual effort setting and record which skill loaded. Target: 18 of 20 or better. Re-run after any
change to the description or to a sibling skill's description.

## 2. Benchmark: baseline against the skill, blind

1. Write a brief (`brief.json`) with only the facts the piece may use.
2. **Baseline:** a fresh Claude subagent writes the piece from the brief alone, told not to load any skill.
3. **Skill:** Claude writes the same piece following nexa-research's fast path (and its client level for finals).
4. **Judge:** the tool's `tournament` command runs both orders with judges from other model families (codex,
   Gemini 3.8 Flash, Gemini 3.1 Pro); a judge's vote counts only when both orders agree.
5. Also lint both with the skill's own lint and count errors and warnings.

Target: the skill wins at least 80 % of counted votes across the benchmark set, with no hard fail. Record every run in
`results.md` with the date, the models and the raw tallies; never report a win the tallies do not show.
