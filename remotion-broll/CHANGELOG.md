# Changelog: remotion-broll

The version is `SKILL_VERSION` in `scripts/broll.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/remotion-broll/tests`, and render the minute once by hand
(`broll.py new`, `stills`, `render`).

## 2026.09.25.1 · the kit

Made from a real session (2026-09-25, "Remotion 2D caricature animation setup"): the first 10 s of explainer B-roll
took 52 minutes from nothing, the next 50 s from the same rigs 22.6 minutes. The kit starts every new video from the
rigs and scenes.

- **The template:** the session's Remotion 4.0.528 project, 15 scenes and 8 components: code-drawn guitarist and runner
  rigs, split screen, creator with camera, timeline editor, growth stat card, kinetic captions, step cards, habit
  streak, upload, feedback edit, bar chart, Day 1 against Day 365, finish line, recap cards, subscribe end card, with
  sound effects; 1920x1080, 30 fps, BT.709.
- **One copy file:** every word on screen moved from 14 scene files into `src/copy.ts`, and the stat card and bar chart
  now compute from `GROWTH` (rate, days), with the stat axis and ticks sized to the final value.
- **No AI people in the public kit:** the session's AI presenter and creator pictures are replaced by plain drawn
  stand-ins (`scripts/placeholders.py`); `references/asset-briefs.json` holds the codex-imagegen briefs that made them.
- **`scripts/broll.py`:** `new` (copy and install, or link an installed kit's modules of the same Remotion version;
  never overwrites), `check` (typecheck, then every line on screen through codex-design's copy lint), `stills` (16
  frames and one contact sheet in about 5 s), `render` (timed, with agy-watch-video's measured QA), `review` (the
  Gemini review with every copy line checked on screen).
- **Measured on the kit:** 16 stills in 5 s, the minute in 45 s, the QA in 2 s; the copy lint passes all 32 lines.
- **Tests:** 10 offline tests.
