# Kit conventions

Rules for every component in `src/kit/`. They keep renders deterministic, keep scenes working in every format,
and keep the kit one consistent library. Remotion is pinned at 4.0.528: check an API against the installed types
(`node_modules/<package>/dist/**/*.d.ts`) before using it, because the docs describe 4.0.529 and later.

## Layout of the kit

- `src/kit/<module>/`: one folder per module with an `index.ts` that exports its public parts, and a `README.md`
  that documents every component (what it is for, its props, a short example, its gotchas).
- `src/demos/<module>.tsx`: exports `demos: DemoDef[]`, one composition per component or feature, ids
  `Demo<Module><Thing>` (for example `DemoTypeCounter`). Demos use real-looking content, never lorem ipsum.
- A module imports only `../core`, `../motion` and npm packages. Never another module: modules are built and
  tested on their own (`nrk.py demos --module NAME` copies only core, motion and that module).
- Heavy modules (`three`, `maps`) are imported by path (`./kit/maps`), not from `src/kit/index.ts`.

## Determinism (a render opens many tabs and renders frames out of order)

- Every visible value is a pure function of `useCurrentFrame()` (and props). No `Math.random()`, `Date.now()`,
  timers, `requestAnimationFrame`, CSS transitions or CSS animations, and no state that builds up across frames.
- Randomness: `rand(seed)`, `randBetween`, `shuffle` from core (seeded), or `wiggle()` from motion (noise; use
  one seed with different lanes).
- Clamp every `interpolate()` at both ends (the kit's `ramp` and `track` do). Effect parameters from
  `@remotion/effects` are validated at render time: an unclamped value outside the allowed range fails the render.
- Anything loaded asynchronously (fonts, data, images drawn to canvas) holds the render with `delayRender` /
  `continueRender` (or `useDelayRender`), created in a `useState` initializer, never in the render body.
- `premountFor` on Sequences that hold media or heavy content (the v5 default is not active on 4.0.528).

## WebGL budget (measured on 4.0.528)

- Chrome allows 16 WebGL contexts per render tab and every component with WebGL effects holds 2: keep at most 8
  effect hosts on screen at once (10 fail with "WebGL context was lost").
- Never put `HtmlInCanvas` in a scene that sits next to a shader transition: the render hangs until the delayRender
  timeout. The fx module's `Scenes` detects it and its looks switch to their CSS engine.
- A scene that entered with a CSS transition plays a following shader transition as a hard cut; `Scenes` splits the
  scene to avoid it.
- `useEffect` changes inside a `ThreeCanvas` never show in their frame: set per-frame values as JSX props or in
  `useLayoutEffect`.

## Time

- Frames everywhere. Components take `delay` (frames from the start of their Sequence) and `duration`.
- Temporary things (labels, callouts, lower thirds, toasts) have an entrance and an exit; the exit ends on the
  last frame of the enclosing Sequence by default (`useVideoConfig().durationInFrames` inside a Sequence is the
  Sequence's length).
- Theme timings are written for 30 fps: scale them with `at30(frames, fps)`.
- Motion rules: arrivals ease out, departures ease in and are faster, moves on screen ease in-out, linear only for
  clocks. Hold settled text still while it is read (at least `readingFrames(text, fps)`). One focal move at a time.

## Size, colour, type

- Sizes are px at a 1080 px short side, multiplied by `unit` from `useStage()` (1 at 1080p and 1080x1920, 2 at
  4K). Never hard-code 1920 or 1080: read `width`, `height` and `safe` from `useStage()`.
- Text and key graphics stay inside `safe` (the platform safe area).
- Colours and fonts come from `useTheme()`: `t.colors.*` and the resolved stacks `t.type.display|body|mono|serif|
  hand|bangla` (they already include a Bangla fallback). A prop may override a colour.
- Load extra fonts only through core's `loadKitFont` or `fontStack` (explicit weights). A font name in CSS
  alone loads nothing and renders a fallback.
- Numbers that change use `fontVariantNumeric: 'tabular-nums'`. Big text scales with `scale`, never by animating
  `fontSize`. Put `textRendering: 'geometricPrecision'` on animated text. No `will-change` on text.
- Bangla must work: test every text component with Bangla (`বাংলা`) as well as English. Do not split Bangla into
  single characters (conjuncts and vowel signs break); split by words, or by grapheme with `Intl.Segmenter`.

## Code style

- TypeScript strict, React function components, props typed with `type` (not `interface`), sensible defaults for
  every prop so `<Thing />` renders something reasonable.
- Prefer the individual CSS `translate`, `scale` and `rotate` properties over `transform` strings (Studio can edit
  them), and inline `interpolate()` keyframes in scene code.
- Comments explain why, briefly. No em dash characters anywhere (use a comma, a colon or brackets).
- Do not copy code or text from the official Remotion skills or docs (they are under the Remotion licence): write
  it yourself. Small API usage patterns are fine.

## Checking a module

1. `npx tsc --noEmit -p .` is clean (nrk runs it).
2. `python3 ../scripts/nrk.py demos --module NAME` renders every demo to a labelled contact sheet.
3. Look at every sheet (and a full-size still of anything detailed): entrance, hold and exit frames, text inside
   the safe area, no clipping, no overlap, Bangla shaped correctly, nothing left half-visible on the last frame.
