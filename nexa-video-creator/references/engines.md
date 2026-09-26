# Engines: Remotion first, remotion-broll and HyperFrames as segments

Research 02 and 03 (2026-09-25) set these rules. Remotion 4.0.528 renders every edit; other engines make clips that
the edit places. The order to reach for, as the user asked (2026-09-25): the edit's own designed scenes first, then a
remotion-broll kit segment for drawn characters and acting, and HyperFrames only for what Remotion cannot do.

## Remotion (the master timeline)

- Footage uses `<Video>` from `@remotion/media` (frame-exact, the fast WebCodecs path). HEVC (every iPhone clip)
  cannot use that path while rendering and silently falls back to `<OffthreadVideo>`: 3x slower in the research
  render (60.5 s against about 20 s). So `ingest` makes H.264 proxies of everything first.
- Untagged or BT.601 sources render with a hue shift on macOS (pure red came out as #FF1800): proxies are tagged
  BT.709, and the output is BT.709.
- Timing props are frames at the composition frame rate (`trimBefore`, `durationInFrames`), whatever a skill note says.
- Sound: Remotion does not normalise loudness and applies volume per video frame with hard clipping. So all videos are
  muted and one mixed file (cut sample-accurately on the same frame grid by `audio`) plays under the whole edit.
- Render settings measured on the M4 Max: `--gl=angle` (faster, much less memory), concurrency 4 to 7, JPEG quality
  90, `--media-cache-size-in-bytes=4294967296` (Remotion reads macOS free memory as 73 to 214 MB and shrinks its cache
  otherwise), `TMPDIR` on the T7 for long or 4K renders. 1080p edits: about 50 to 60 s a minute; 9:16 60 to 70 s;
  4K 3 to 4 minutes a minute.
- HDR phone clips: tone-map in the proxy step with Remotion's own ffmpeg (`npx remotion ffmpeg`, it has zscale), or
  ask for SDR recordings. `ingest` warns when a source is HDR.

## The edit's own scenes (first choice for explainer graphics)

kinetic words, step cards, a big number with its curve, bar charts, a before and after split, recap cards, an end
card with a subscribe click, and photo cards (`references/plan.md`, Scenes). They are Remotion components in the
renderer (`template/src/scenes.tsx`) with the kit's craft built in (push-ins on holds, words rising out of a blur,
hand-drawn underlines, colour sweeps and slides between scenes, count-ups that land, sound on each moment), laid out
for 16:9 and 9:16 and for Bangla. They render with the edit itself: no project to set up, no extra render.

## remotion-broll (2D explainer animation)

The kit draws rigged 2D characters (a guitarist, a runner), a stat card and bar chart from one growth rate, step
cards, a timeline editor, a finish line and more (`remotion-broll/references/scenes.md`).

1. `broll.py new ~/videos/JOB-broll` (or reuse a kit project), change `src/copy.ts` with natural-text, `check`,
   `stills`.
2. `nvc.py segment broll ~/videos/JOB-broll --comp BrollDemo --job JOB` renders it into the job as a `segment`.
3. Place it: `{"type": "segment", "words": [...], "quote": "...", "source": "broll-jobbroll", "in": 0}`.
Each kit scene is also its own composition, so a single scene can be rendered on its own.

## HyperFrames (only where Remotion cannot do the job)

Kinetic titles, stat and chart hits and step cards are the edit's own scenes now. HyperFrames stays for what those
and the kit do not cover, such as a website capture tour or a logo sting a client already has in HTML: usually under
10 s, at most about 30 s. Never for the whole edit.

- Pin one CLI version per project (the global wrapper is 0.8.30, npm latest was 0.8.75 on 2026-09-25).
- Always run with `HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1 HYPERFRAMES_SKIP_SKILLS=1` (`init` rewrites
  `~/.claude/skills` otherwise); `nvc.py segment hf` sets them.
- Size and frame rate must equal the edit's (`data-width`, `data-height`, `data-fps`), and the duration a whole number
  of frames.
- Overlays over footage: `--alpha` renders VP9 WebM with alpha, placed as a `segment` overlay (the renderer uses
  `<OffthreadVideo transparent>`). Check that the alpha came through (`ffprobe ... alpha_mode`); a transparent first
  frame at a shard boundary means rendering again with one worker.
- Never let the hyperframes skill's own interview, storyboard or publish steps run inside a nexa job.

## Images and generated media

codex-imagegen makes stills (b-roll, product shots, backgrounds). Add them with `--role image` and place them as
`image` overlays (push, pull or pan motion) or `brollFull` segments. A realistic generated person is labelled where
the platform asks, and never passed off as a real customer.
