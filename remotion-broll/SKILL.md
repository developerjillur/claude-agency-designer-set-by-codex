---
name: remotion-broll
description: "Explainer-video B-roll made in Remotion from a ready kit: code-drawn 2D caricature characters (a strumming guitarist and a runner, both rigged), a split screen, a round presenter picture-in-picture, a video-editor timeline, a growth stat card and a bar chart that compute from one rate, kinetic captions with hand-drawn underlines, step cards, a habit streak, an upload scene, a Day 1 against Day 365 split, a finish line with confetti, recap cards and a subscribe end card, at 1920x1080 and 30 fps with sound effects. Use it whenever a request asks for animated B-roll, motion graphics, 2D caricature or explainer animation for a YouTube, course, product or talking-head video, Banglish asks included ('remotion diye video banao', 'explainer animation banao', 'b-roll lagbe'). Start from the kit, change one copy file and the theme, check, render a minute in about 45 s, and review it with agy-watch-video."
---

# Remotion B-roll

A kit made from a real session (2026-09-25): the first 10 s of this style took 52 minutes from nothing (install,
pictures, character rigs, review); the next 50 s from the same rigs took 22.6 minutes. The kit starts every new video
at the second speed. Command prefix: `python3 ~/.claude/skills/remotion-broll/scripts/broll.py`.

## Fast path (do exactly this)

1. **Start:** `broll.py new ~/path/to/project`: the kit is copied and `npm ci` runs (about a minute the first time,
   quick after that from the npm cache). `--link-modules OTHER_KIT_PROJECT` reuses an installed kit's `node_modules`
   at once (the same Remotion version is checked).
2. **Make it this product's:** every word on screen is in `src/copy.ts`, the charts' numbers in its `GROWTH`, the
   font and colours in `src/theme.ts`, scene lengths in `src/Part2.tsx` and `src/BrollDemo.tsx`. Write the words with
   the natural-copy skill: short lines, the audience's own words, no invented claims.
3. **Check:** `broll.py check DIR`: the typecheck, then every line on screen through codex-design's copy lint (it
   writes `copy/onscreen.json`). Fix every error and warning.
4. **Look once:** `broll.py stills DIR`: 16 frames across the minute and one contact sheet in about 5 s. Read the
   sheet, fix, and look again only where something changed.
5. **Render:** `broll.py render DIR`: the minute in about 45 s, then the measured QA (ffmpeg, 2 s).
6. **Client final:** `broll.py review DIR out/BrollMinute.mp4`: the Gemini review (agy-watch-video, `--goal motion`,
   every copy line checked on screen), about 5 minutes. Act on findings the frames confirm.

Open the Studio with `npm run dev` in the project to scrub the timeline; each scene is also its own composition.

## What the kit holds

| Composition | Length | What it shows |
|---|---|---|
| `BrollDemo` | 10 s | split screen (guitarist and runner, label chips), creator with camera and icons, round presenter PiP, timeline editor UI, growth stat card, kinetic caption |
| `Part2` | 50 s | the caption continues, three step cards each with its scene (habit streak, share and upload, feedback edit), compounding bars, Day 1 against Day 365, finish line with confetti, recap cards, subscribe end card |
| `BrollMinute` | 60 s | both, one after the other |

Every scene is listed with its copy keys and length in `references/scenes.md`. The guitarist and the runner are drawn
in code (`components/draw.tsx`: chains of points bent by angles over time), so they move for any length and in any
colour. The creator cutout and the presenter are pictures in `public/`: the kit ships plain stand-ins.

## Make it yours

- **Words:** `src/copy.ts` only. Keep a line to one idea and one or two lines on screen at a time, each for at least
  a second. `GROWTH` (rate and days) drives the stat card and the bars; keep the stat title and the bar chart's note
  in step with it. The bar chart has exactly four periods (its animation times four bars).
- **Look:** `src/theme.ts`: the font (`@remotion/google-fonts`), `INK` (the characters' outline) and `COLORS`.
- **Timing:** in `src/Part2.tsx` each scene's `durationInFrames` (30 = one second) and the `AT` offsets that place
  the sound effects and the PiP. Fit the scenes to the voice-over, not the other way round.
- **Pictures:** `public/presenter-pip.png` (square; the presenter's real still or footage is best) and
  `public/creator-cutout.png` (square, transparent). To make them: codex-imagegen `batch` with the two briefs in
  `references/asset-briefs.json` (both in about 1.6 minutes). A realistic AI person must be labelled where the
  platform requires it; never pass one off as a real customer or expert.
- **Sound:** the kit carries only sound effects (`@remotion/sfx`). Add the voice-over and music with `<Audio>`
  (`@remotion/media`); until then the QA's "audio is silent" note is expected. Common practice for YouTube is about
  -14 to -16 LUFS integrated.

## Craft rules that came out of the reviews

- A hold longer than about 0.7 s reads as a frozen frame in motion graphics: give it a slow push-in (scale 1 to 1.04).
- A fade between two bright scenes reads as an exposure drop: slide or wipe instead.
- Check drawing order at contact moments on stills (the finish tape and poles sat in front of the runner's arm once).
- Small bars that grow in the same frames as big ones are not seen growing: stagger their start.
- Counters and growing charts pass through in-between values: judge the settled frame.
- Keep text clear of the top-left and bottom-right corners, where YouTube's player shows the title and the time.
- Colour is BT.709 (`remotion.config.ts`), what YouTube expects for SDR.
- Remotion moves what is drawn in code and can pop, sway, breathe and push in on a picture. It cannot turn a
  picture's head, move its hands or lip-sync: for acting shots use real footage or an image-to-video model (Wan 2.2),
  and keep Remotion for everything drawn.

## Time, measured on this machine (2026-09-25)

| Step | Time |
|---|---|
| `new` with `--link-modules` | under a second |
| `check` | about 3 s |
| `stills` (16 frames and a sheet) | about 5 s |
| `render` of 60 s | 45 s, plus 2 s of QA |
| `review` (Gemini) | about 5 minutes (a 10 s clip: 289 s) |

Most of a session's time goes into the model writing scene code and into the review, not the render: reuse scenes,
and write new ones only where the story needs them.

## Licence

Remotion is free for individuals and for companies of up to three people; larger teams need a company licence
(remotion.pro/license). The fonts come from Google Fonts (OFL).

## Files

- `scripts/broll.py`: new, check, stills, render, review. `scripts/placeholders.py`: remakes the stand-in pictures.
- `template/`: the Remotion project (Remotion 4.0.528, React 19). `references/scenes.md`: every scene and component.
  `references/asset-briefs.json`: the codex-imagegen briefs for the two pictures. `tests/`: offline tests
  (`python3 -m unittest discover -s ~/.claude/skills/remotion-broll/tests`).
