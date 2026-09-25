# R2-team-videos: the Remotion team's own video code (craft, timing, patterns, APIs)

Research agent R2-team-videos, 2026-09-26. Material: the video code the Remotion team wrote for itself (brand and
marketing videos, the kitchen-sink example project, Jonny's videos, the website's Player demo), the packages
`@remotion/maptiler`, `@remotion/three`, `@remotion/svg-3d-engine`, `@remotion/timeline-utils`, `@remotion/design`, and
the core timing sources (`spring`, `measureSpring`, `Easing`, `interpolate`).

Path shorthands used everywhere below (all under `repo/packages/`):
`brand/` = `brand/src/`, `example/` = `example/src/`, `jonny/` = `jonnys-videos/src/`,
`promo/` = `promo-pages/src/components/`, `design/` = `design/src/`, `svg3d/` = `svg-3d-engine/src/`,
`three/` = `three/src/`, `timeline/` = `timeline-utils/src/`, `maptiler/` = `maptiler/src/`, `core/` = `core/src/`.
"f" means frames; fps is 30 unless stated. Line numbers refer to the 4.0.529 monorepo copy.

## 1. Scope and coverage

- Assignment: 905 files. Read in full: 900 text files (every file is listed in `kb/R2-team-videos.coverage.txt`,
  900 unique lines, checked against the file list: nothing missing, nothing extra). Skipped: 5 binary media files
  (`example/resources/framer-music.mp4`, `framer.mp4`, `framer-24fps.mp4`, `sound1.mp3`, `sound2.mp3`).
- Per area: example 396 (of 401), brand 216, promo-pages 145, jonnys-videos 44, timeline-utils 34, design 22,
  maptiler 21 (whole package incl. README, package.json, configs), svg-3d-engine 10, three 7, core timing 5
  (`core/spring/index.ts`, `measure-spring.ts`, `spring-utils.ts`, `core/easing.ts`, `core/interpolate.ts`).
- Method: 13 parallel chunk readers each read their files one by one and wrote dense notes (7,033 lines, kept in the
  session scratchpad); I read the five core timing files myself, re-implemented the spring solver to verify every
  spring number quoted here, and synthesised this file from all notes.
- Companion file: `kb/R2-team-videos.file-index.md` has one line per file read (all 900: what it shows, kind,
  techniques, learn value 0-3), for finding an example of any technique by grep.
- Data blobs that were read structurally and sampled (all code lines read): `example/3DSvgContent/index.tsx` (12 lines
  of embedded base64/SVG data up to 272 KB each), `example/AudioTesting/Base64.tsx` (one 62 KB base64 WAV line),
  `example/SwitzerlandMap/*.json` (Natural Earth GeoJSON rings), `brand/Skills2Gesture.tsx` (6,226 lines, about 96%
  per-frame keyframe arrays: shape learned, arrays skimmed), `example/InteractiveDivStressTest.tsx` (1,000 generated
  spans), `example/Lottie/LottieInitializationBugfix/index.tsx` (After Effects export).
- Not in the copy (so some semantics are inferred from call sites): the core sources of `Sequence`, `AbsoluteFill`,
  `Freeze`, `HtmlInCanvas`, `Solid`, `CanvasImage`, `Interactive` (only easing/interpolate/spring exist under
  `core/`); `@remotion/gsap`; `@remotion/mac-cursors`; `@remotion/media`.
- Version checks against the target project (`nexa-media/remotion-broll/node_modules`, remotion 4.0.528, read only):
  - Present in 4.0.528: `Interactive` (Div, Span, withSchema, about 35 tags), `Solid`, `CanvasImage`, `AnimatedImage`,
    `HtmlInCanvas`, `createEffect`, `Html5Audio`/`Html5Video`, `useDelayRender`, Sequence `width/height/crop*/controls/
    outlineRef/styleWhilePremounted`, every new `interpolate` option (string, tuple, discrete, `posterize`,
    `output: 'perceptual-scale'`, `outputType`, easing arrays) including 3D axis-angle rotate strings (the installed
    `interpolate.js` contains the axis-rotation parser), `Easing.spring` with `allowTail`/`durationRestThreshold`.
  - Installed 4.0.528 packages (as of 2026-09-26 00:00; effects, fonts, motion-blur, three, svg-3d-engine, light-leaks,
    gif, lottie, rive, starburst, rounded-text-box and animated-emoji were added during this session):
    animated-emoji, animation-utils, bundler, canvas, captions, cli, codemods, effects, fonts, gif, google-fonts,
    layout-utils, licensing, light-leaks, lottie, media, media-parser, media-utils, motion-blur, noise, paths, player,
    renderer, rive, rough-notation, rounded-text-box, sfx, shapes, starburst, streaming, studio*, svg-3d-engine,
    tailwind-v4, three, timeline-utils, transitions, web-renderer, zod-types.
  - NOT installed: `@remotion/mac-cursors` (used by every Studio close-up), `@remotion/maptiler` (4.0.529, README says
    internal), `@remotion/gsap`.
  - `@remotion/motion-blur` 4.0.528 exports only `CameraMotionBlur` and `Trail`: the team's `HtmlInCanvasMotionBlur`
    (brand/Showcase/MotionBlurSlideIn.tsx, example/HtmlInCanvas/motion-blur.tsx) is NEWER than 4.0.528.
  - `@remotion/effects` 4.0.528 subpaths include every effect the team uses (blur, burlap, chromatic-aberration,
    color-correction, color-key, corner-pin, drop-shadow, evolve, fisheye, glow, grayscale, gridlines, halftone,
    halftone-linear-gradient, hue, light-leak, linear-progressive-blur, noise, noise-displacement, paper, pattern,
    pixel-dissolve, radial-progressive-blur, rings, scale, scanlines, shine, starburst, tear, tint, translate,
    vignette, wave, waves, zigzag) plus many more (barrel-distortion, duotone, emboss, lut, mirror, pixelate,
    thermal-vision, tv-signal-off, zoom-blur, ...).
  - `@remotion/transitions` 4.0.528 presentations: blur-slide, book-flip, clock-wipe, cross-zoom, crosswarp, dissolve,
    dreamy-zoom, fade, film-burn, flip, iris, linear-blur, none, push-cut, ripple, slide, swap, wipe, zoom-blur,
    zoom-in-out.
- Freshness: remotion.media asset names in the close-ups are dated 2026-09-21 to 2026-09-23, so much of this code was
  written days before the 4.0.528/529 releases and shows the current, Studio-visual-editing authoring model.

## 2. Mental model

1. Every pixel is a pure function of the frame. The team never animates with state, timers, CSS transitions,
   `requestAnimationFrame` or wall clocks inside compositions (those only appear in website UI). Randomness is
   `random(seed)`; `random(null)` only for DOM ids. Loops are closed by frame math. This is what makes parallel,
   out-of-order rendering deterministic.
2. Two authoring eras live side by side, and our skills should write the NEW one:
   - Classic: `spring()` values mapped with `interpolate(progress, [0, 1], [a, b])` into `transform` strings, scenes
     in `AbsoluteFill` + `Sequence`, springs `{damping: 200}` with `delay` and `durationInFrames`.
   - Studio-era (4.0.46x to 4.0.52x, the newest brand, jonnys-videos and example files): animated values live directly
     in `style` of a `Sequence`/`AbsoluteFill`/`Interactive.*`/media element as CSS individual properties
     (`translate: 'Xpx Ypx'`, `rotate: 'Ndeg'` or `'x y z Ndeg'`, `scale`, `opacity`), each driven by ONE
     `interpolate(frame, keys, values, {easing: [one per segment], clamp both sides})`, scale keys carry
     `output: 'perceptual-scale'`, springs appear as `Easing.spring({damping: 200, mass: 1, stiffness: 100,
     allowTail: true, durationRestThreshold: 0.02, overshootClamping: false})`, stepped motion uses `posterize: 3`,
     every element has a `name`, timing edits (`from`, `durationInFrames`, `trimBefore`, `freeze`, `premountFor`,
     `playbackRate`) sit on the element itself, and effects come from an `effects={[...]}` array. This code is what
     the Studio's visual keyframe editor reads and writes (float noise like `1.0000000000280422` and `'-419.93606px
     93.283812px'` are drag results), so generated code in this form stays editable by the user.
3. Timing is made of three primitives: `spring()` (physics with a measurable natural duration), `interpolate()`
   (keyframes, now with strings, tuples, per-segment easing, posterize, perceptual scale) and `Easing` (including
   `Easing.spring`, which squeezes a spring into a keyframe segment). The single most important physical fact: Remotion
   solves any spring with damping ratio >= 1 as CRITICALLY damped, so `{damping: 20}`, `{damping: 200}` and
   `{damping: 2000}` (at default mass 1, stiffness 100) are the SAME 23-frame curve at 30 fps. Speed comes from
   `durationInFrames`, `mass` or `stiffness`, never from more damping.
4. Time is scoped by nesting. A child's frame is `(parentFrame - from) * playbackRate + trimBefore`; nested rates
   multiply; `durationInFrames` stays in PARENT frames; `useVideoConfig().durationInFrames` inside a Sequence is the
   Sequence's length. A frame captured in a parent (and used in a child's `style` or props) keeps the parent clock.
   Whether a component reads `useCurrentFrame()` itself or receives the frame as a prop decides which clock it follows;
   the team uses both deliberately (a ping-pong remap reaches nested components only as a prop).
5. Layers, not slides. Most newer videos are a flat list of absolutely positioned layers (`Sequence` with `width`,
   `height`, `style`, explicit `from`/`durationInFrames`), overlapping in time, source order = z order. Scene changes
   are keyframed pushes, flashes and overlays at least as often as `TransitionSeries`. A `Sequence width={1920}
   height={1080}` inside a vertical frame is a "sub-canvas" that can be moved and zoomed like a camera.
6. Scenes own their timing. Each scene file exports its `*_DURATION_IN_FRAMES` constant (and often registers its own
   `<Composition>`), the Root imports the constant, and a master composition reuses the same scene component. Beats
   inside a scene are named constants derived from each other so retiming ripples.
7. The team's visual language: GT Planar (brand font, stylistic set `ss03`), blue `#0b84f3`, red `#F43B00`/`#ff3232`,
   dark Studio UI `#1f2428`/`#181818`, "sticker 3D" (orthographic extrusion, black edges, 2-9 px black borders, flat
   offset shadows), glass panels on dark navy, hand-drawn sketch style for explainers, Arial Black captions with black
   strokes and hard drop shadows for short-form. Product videos are screen recordings on a tilted plane with fake depth
   of field and a re-drawn macOS cursor.
8. Heavy lifting runs outside the per-frame path: data and media metadata in `calculateMetadata` or under
   `delayRender`, fonts at module scope, DOM measurement once in `useLayoutEffect` under a delayRender handle,
   premounting media 0.5 to 1.5 s before it appears, and imperative renderers (maps, three.js, WebGPU) holding each
   frame with `delayRender` until they report idle.

## 3. API digest

Versions come from the docs mirror (`AvailableFrom`) where stated; "4.0.529 only" means seen in the monorepo copy but not in the installed 4.0.528.

### 3.1 Core timing primitives (read from `repo/packages/core/src/spring/*`, `easing.ts`, `interpolate.ts`)

#### `spring()`
Signature: `spring({frame, fps, config?, from = 0, to = 1, durationInFrames?, durationRestThreshold?, delay = 0, reverse = false}): number`.
- `config`: `{damping = 10, mass = 1, stiffness = 100, overshootClamping = false}`. An explicitly `undefined` field falls back to the default (source comment: otherwise the physics turn into NaN). `damping <= 0` throws.
- `durationInFrames` (since 3.0.27): time-stretches the natural curve so it lands exactly at that frame; after `delay + durationInFrames` the function returns exactly `to` (clean landing, no asymptotic 0.996).
- `durationRestThreshold` (since 3.0.27): the threshold used to measure the natural duration when stretching or reversing (default 0.005).
- `delay` (since 3.3.90): shifts the start; frames before the start return `from` (the frame is clamped to 0 internally). Fractional delays and frames are fine (team uses `delay: 28.2 + i`).
- `reverse` (since 3.3.92): plays the curve backwards over `[delay, delay + (durationInFrames ?? natural)]` (1 to 0). Team trick: a reversed DEFAULT (bouncy) spring gives an anticipation bulge before collapsing (brand/Brand/Logo.tsx).
- Order of operations in source: reverse, then delay, then stretch.
- `overshootClamping: true` clamps the value at `to`.
- Output mapping: `from`/`to` are applied with a plain linear interpolate of the 0..1 spring value.
- Solver facts that matter for craft (spring-utils.ts):
  - It steps frame by frame from frame 0 with `dt = min(frameDuration, 64 ms)`. Below 15.625 fps each step is capped at 64 ms, so springs play SLOWER in real time at low fps (damping 200 settles in 1.2 s at 10 fps versus 0.77 s at 30 fps). Relevant for 10 fps "stop-motion" compositions (the team's Skills2Hand runs at 10 fps).
  - It uses the underdamped formula only when zeta = damping / (2 * sqrt(stiffness * mass)) < 1, otherwise the CRITICALLY damped formula, which ignores damping beyond critical. With default mass 1 and stiffness 100, critical damping is 20, so `{damping: 20}`, `{damping: 200}` and `{damping: 2000}` are the same curve. To make motion heavier or slower without bounce, raise `mass` or lower `stiffness`, or use `durationInFrames`. This is the single most important spring fact in the team code.
  - Results are memoised per (frame, fps, config), so many calls per frame are cheap.

#### `measureSpring({fps, config?, threshold = 0.005}): number`
Returns the first frame at which |value - 1| < threshold and stays there for 20 more frames (guards against bouncy re-entry). `threshold` 0 returns Infinity, 1 returns 0; NaN, negative or non-finite thresholds throw. Team use: sync another animation to a spring's natural length, e.g. `durationInFrames: measureSpring({fps, config: {}})` (28 frames at 30 fps) so a width change ends exactly when a bouncy flip settles (brand/Compose/WhatIsRemotion.tsx:243-255).

#### Verified spring table (reimplementation of the core solver; frames at 30 fps, then 60 fps)
| config | zeta | 50% at | 90% at | overshoot | settle (0.005) | settle (0.02) |
|---|---|---|---|---|---|---|
| default `{damping 10, mass 1, stiffness 100}` | 0.50 | f4 / f8 | f7 / f13 | 16.3% at f11 / f22 | 28 / 56 | 25 / 49 |
| `{damping: 200}` (= any damping >= 20) | 10 | f6 / f11 | f12 / f24 | none | 23 / 45 | 18 / 36 |
| `{damping: 12}` | 0.60 | f5 | f8 | 9.5% at f12 | 28 | 18 |
| `{damping: 15}` | 0.75 | f5 | f9 | 2.8% at f14 | 22 | 18 |
| `{damping: 18, stiffness: 120}` | 0.82 | f5 | f9 | 1.1% at f15 | 20 | 11 |
| `{damping: 18, mass: 0.8, stiffness: 120}` | 0.92 | f4 | f9 | 0.1% | 15 | 13 |
| `{mass: 0.5}` | 0.71 | f4 | f6 | 4.2% at f9 | 15 | 13 |
| `{damping: 8, mass: 0.69, stiffness: 112}` | 0.46 | f3 | f5 | 19.9% at f8 | 28 | 20 |
| `{damping: 10, mass: 0.55, stiffness: 220}` | 0.45 | f2 | f4 | 19.7% at f5 | 18 | 13 |
| `{mass: 2, damping: 200}` | 7.07 | f8 | f17 | none | 32 | 25 |
| `{mass: 0.7, damping: 200}` | 11.95 | f5 | f10 | none | 19 | 15 |
| `{mass: 20, damping: 500}` | 5.59 | f23 | f53 | none | 100 | 79 |
| `{damping: 5, stiffness: 120}` | 0.23 | f4 | f5 | 47.8% at f9 | 64 | 47 |
| `{damping: 5, stiffness: 63}` | 0.31 | f5 | f7 | 35.0% at f13 | 65 | 43 |
| `{damping: 10, stiffness: 269}` | 0.30 | f3 | f4 | 36.6% at f6 | 32 | 21 |
Per-frame values of the house curve `{damping: 200}` at 30 fps: f1 .045, f2 .144, f3 .264, f4 .385, f5 .496, f6 .594, f8 .745, f10 .845, f12 .908, f15 .960, f18 .983, f20 .990, f23 .996.
Per-frame values of the default bouncy spring at 30 fps: f2 .174, f4 .521, f6 .849, f8 1.065, f11 1.163 (peak), f14 1.104, f18 1.002, f22 .973 (dip), f29 1.0.

#### `Easing` (class of static functions, from React Native's Easing)
- `step0` (n > 0 ? 1 : 0), `step1` (n >= 1 ? 1 : 0), `linear`, `quad` (t^2), `cubic` (t^3), `poly(n)`, `sin` (1 - cos(t*PI/2)), `circle` (clamped to [0,1]), `exp` (2^(10(t-1))), `elastic(bounciness = 1)`, `back(s = 1.70158)`, `bounce` (clamped), `bezier(x1, y1, x2, y2)`, `in(f)` (returns f), `out(f)` (1 - f(1 - t)), `inOut(f)`.
- GOTCHA: `Easing.ease` is `bezier(0.42, 0, 1, 1)`, i.e. CSS ease-IN, not CSS `ease` (0.25, 0.1, 0.25, 1). `Easing.in(Easing.ease)` is the same curve. For a CSS-like ease use `Easing.bezier(0.25, 0.1, 0.25, 1)`.
- `Easing.spring(config?)` (since 4.0.476; `allowTail` and `durationRestThreshold` since 4.0.483): turns a spring into an easing for `interpolate()`. Config: `damping`, `mass`, `stiffness`, `overshootClamping`, `durationRestThreshold`, `allowTail` (default false). Without `allowTail` it evaluates `spring({fps: 30, frame: t * 30, config, durationInFrames: 30})`, i.e. the natural curve squeezed into the segment, returns exactly 0 at t <= 0 and 1 at t >= 1. Underdamped configs overshoot INSIDE the segment (default config reaches 1.16 at 40% of the window). With `allowTail: true`, time is mapped onto `measureSpring({threshold: durationRestThreshold})`, the keyframe is reached at about 98% (threshold 0.02), and the function is tagged `remotionShouldExtendRight`: interpolate then treats a right clamp as extend for that segment and ADDS the unfinished remainder into later segments, so a spring hands off smoothly into the next segment (a spring move followed by a slow linear drift never visibly stops).
- Progress tables (value at 10%, 20% ... of the window):
  - `Easing.spring({damping: 200})`: .18 .45 .67 .81 .90 .94 .97 .985 .99 (then 1)
  - `Easing.spring({damping: 200, allowTail: true, durationRestThreshold: 0.02})` (the Studio default keyframe spring): .12 .34 .54 .69 .80 .87 .92 .95 .97, 0.98 at the key, tail continues
  - `Easing.spring({damping: 18})`: .12 .33 .54 .70 .82 .90 .95 .98 .99
  - `Easing.bezier(0.16, 1, 0.3, 1)` (expo-out, the team's favourite): .49 .75 .88 .94 .97 .99 1 1 1 (half the distance in the first 10% of the window)
  - `Easing.bezier(0.22, 1, 0.36, 1)` (quint-out): .40 .67 .83 .92 .96 .98 .99
  - `Easing.bezier(0.42, 0, 0.58, 1)` (ease-in-out): .02 .08 .19 .33 .50 .67 .81 .92 .98
  - `Easing.bezier(0, 0, 0.2, 1)` (decelerate): .30 .50 .65 .76 .84 .90 .95 .98 .995
  - `Easing.bezier(0.4, 0, 1, 1)` (accelerate): .02 .07 .14 .22 .33 .44 .56 .70 .84

#### `interpolate(input, inputRange, outputRange, options?)`
Options (all optional): `easing` (function, or since 4.0.462 an array with exactly `inputRange.length - 1` functions, one per segment), `extrapolateLeft` / `extrapolateRight` (`'extend'` default, `'clamp'`, `'identity'`, `'wrap'`), `output` (`'linear'` default or `'perceptual-scale'`, since 4.0.490), `outputType` (`'scale' | 'translate' | 'rotate' | 'transform-origin' | 'font-weight'`, since 4.0.526), `posterize` (positive number, since 4.0.470).
Output kinds (the return type follows the output range):
- numbers (classic);
- numeric tuples (since 4.0.473): `interpolate(f, [0, 30], [[0, 0], [100, 50]])` returns `[x, y]`, every tuple the same length;
- CSS individual-transform strings (since 4.0.472): scale (`'1'`, `'2 3'`, unitless), translate (`'0px 0px'`, `'-20% 0px'`, up to 3 components, any CSS length or %), rotate (`'90deg'`, rad, grad, turn), transform-origin keywords (`'left top'`, since 4.0.475; normalised to %). Units must match per axis, kinds cannot be mixed, missing axes default to CSS defaults (scale 1, translate and rotate 0). The 4.0.529 source also parses 3D axis-angle rotations (`'0.97 -0.21 -0.08 31deg'` or `'x 45deg'`) and interpolates the four numbers component-wise (not a slerp); the team's close-ups rely on this (verified present in the installed 4.0.528 `interpolate.js`);
- font weight: with `outputType: 'font-weight'`, numbers 1-1000 plus `'normal'` (400) and `'bold'` (700);
- discrete strings (since 4.0.509): any non-numeric strings (cursor names, `'auto'`) when EVERY segment easing is `Easing.step1`; the previous value holds until the next key. `extrapolate: 'identity'` is rejected for them.
Behaviour details:
- `inputRange` must be finite and strictly increasing, same length as `outputRange`. A single-element range returns its only output (since 4.0.469): the Studio writes `interpolate(frame, [7], [0.446])` for a property with one keyframe.
- Per segment the input is normalised to 0..1, eased, then mapped. A segment with equal endpoints returns the value without easing (clean holds).
- `posterize: n` floors the input to a multiple of n before everything else (`Math.floor(input / n) * n`): stepped "on threes" animation without touching the frame.
- `'wrap'` loops the input inside the range (`interpolate(1.5, [0, 1], [0, 2], {extrapolateRight: 'wrap'})` is 1).
- `output: 'perceptual-scale'` interpolates the signed area `sign(s) * s^2` and maps back with `sign(a) * sqrt(|a|)`, so a zoom from 0 to 2 is at 1.414 halfway (linear gives 1.0) and looks evenly paced; the Studio writes it on every scale keyframe (installed `absoluteFillSchema` marks `style.scale` with `defaultKeyframeOutput: 'perceptual-scale'`). Use it only for scale.
- Default extrapolation is `'extend'`: unclamped rotations keep spinning and opacity overshoots past 1. The team clamps both sides on almost every call.
- Common errors: "inputRange must be strictly monotonically increasing", "Non-numeric strings can only be interpolated using Easing.step1", "When easing is an array, it must have one entry per segment between keyframes", "posterize must be a positive finite number", "Cannot interpolate ... values with different units on axis N".

### 3.2 Other APIs as the team actually calls them (other KB files own the full references)

Timeline and layout
- `Sequence`: `from` (negative and fractional allowed), `durationInFrames` (fractional allowed; stays in parent frames),
  `name`, `layout="none"`, `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted`,
  `showInTimeline`, `hidden`, `trimBefore` (skips the child's first N frames: `from={27} trimBefore={27}` mounts at 27
  with inner time = outer time, an NLE head trim; two Sequences with equal `from - trimBefore` share one clock, used to
  split a layer), `playbackRate` (4.0.528; child frame = `(f - from) * rate + trimBefore`, nested rates multiply,
  child frames can be fractional), `freeze={n}` (children held at local frame n), `cropLeft/Right/Top/Bottom` (0..1,
  animatable), `width`/`height` (the child's canvas; `useVideoConfig()` inside reports them, so a standalone
  composition can be embedded unchanged), `style` (the Sequence is a positioned, sized, styled box: translate, scale,
  rotate, transformOrigin, opacity, borderRadius, overflow...; a childless styled Sequence can itself be the visual),
  `controls` + `outlineRef` (hand Studio its controls and the node to outline), `ref`.
- `AbsoluteFill` accepts the Sequence timing props since 4.0.501 (`from`, `durationInFrames`, `trimBefore`,
  `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`) and `premountFor`/`postmountFor`/`styleWhile*` since
  4.0.528; typed as `InteractiveBaseProps & InteractivePremountProps`. Team use: `<AbsoluteFill from={-449}
  playbackRate={2.3} style={{width, height, translate, rotate, scale}}>` for a trimmed, sped-up, tilted screen
  recording. `<AbsoluteFill from={775} durationInFrames={25} freeze={0} style={{opacity}}>` for a loop crossfade.
- Leaf elements are timeline items too: `name`, `from`, `durationInFrames`, `trimBefore` (and usually `premountFor`,
  `freeze`, `playbackRate`) are accepted by `Interactive.*`, `Solid`, `HtmlInCanvas`, `Img`, `AnimatedImage`,
  `CanvasImage`, `@remotion/media` `Video`/`Audio`, `Html5Video`, `Html5Audio`, `OffthreadVideo`, `RemotionRiveCanvas`,
  `@remotion/gif` `Gif`, `@remotion/shapes` components, `ThreeCanvas`, `LightLeak`, `MacOSCursor`, map components
  (`example/TrimBeforeSupportTest.tsx` is the one-page map). No wrapper Sequence is needed.
- `Series`/`Series.Sequence` (also `style`, `ref`, `trimBefore`, `premountFor`, `postmountFor`, `name`), `Loop
  {durationInFrames, times, name}`, `Freeze {frame, active: boolean | (f) => boolean}`, `Folder`, `Still`,
  `Composition` with `lazyComponent={() => import('./X')}` (default export), `schema`, `defaultProps`,
  `calculateMetadata` returning any of `durationInFrames, fps, width, height, props, defaultCodec, defaultOutName,
  defaultProResProfile, defaultPixelFormat, defaultVideoImageFormat` (width/height/fps/duration may be omitted on the
  Composition when calculateMetadata returns them).

Studio-editable elements (4.0.475+)
- `Interactive.Div/Span/Svg/Path/Rect/Circle/Ellipse/G/Line/Text/H1.../P/Button/Code/Section...`: normal element props
  plus `name` and the Sequence-like props above; each appears as a selectable, draggable layer. Studio-editable style
  keys: `transformOrigin`, `translate`, `scale`, `rotate`, `opacity`, `color`, plus text, background, border,
  borderRadius, crop and SVG paint schemas.
- Custom elements: `Interactive.withSchema({Component, componentName: '<MyElement>', schema, supportsEffects: false})`.
  Schema = `{...Interactive.baseSchema, ...Interactive.transformSchema, myField: {type: 'number', min, max, step,
  default, description, hiddenFromList: false, keyframable: false}} as const satisfies InteractivitySchema`. Field
  types seen: `number`, `color`, `text-content`, `asset` (`assetType: 'audio'`), `array` (`item`, `newItemDefault`,
  `minLength`, `maxLength`), `enum` (`variants`); preset groups `baseSchema`, `transformSchema`, `textSchema`,
  `backgroundSchema`, `borderSchema`, `borderRadiusSchema`, `captionsSchema`, `sequenceSchema`. The inner forwardRef
  component receives `controls` and must render `<Sequence layout="none" {...sequenceProps} controls={controls}
  name={name ?? 'My element'} outlineRef={outlineRef}>` and expose its root via `useImperativeHandle(ref, () =>
  outlineRef.current)`. Files named `*.element.tsx` are the team's element-library convention.

Canvas-backed components and effects
- `Solid` (4.0.464): `<Solid width height color style effects name from />` a canvas-painted rectangle; with effects it
  is a procedural generator (paper, burlap, rings, halftone gradient, light leak, starburst).
- `HtmlInCanvas` (4.0.455; `effects` 4.0.464; `premountFor` 4.0.528): draws its DOM children into a canvas. Props
  `width`, `height` (may change per frame), `style`, `effects`, `pixelDensity` (supersampling, cost x density^2),
  `onInit({canvas})` (once, may be async, returns cleanup), `onPaint({canvas, element, elementImage})` (2D:
  `ctx.reset(); const t = ctx.drawElementImage(elementImage, 0, 0); element.style.transform = t.toString()`; WebGL2:
  `gl.texElementImage2D(...)`; WebGPU: `device.queue.copyElementImageToTexture(...)`; an async onPaint holds the
  frame). Effects run after onPaint. Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element`;
  renders work out of the box; WebGL effects need `--gl=angle`; do not nest two HtmlInCanvas; cross-origin content
  paints blank unless CORS (`crossOrigin="anonymous"`).
- `CanvasImage` (4.0.466): `<CanvasImage src width height fit="cover" style effects name />` (CORS needed).
  `Img` and `AnimatedImage` also take `effects`; `Img pauseWhenLoading`, `crossOrigin`.
- `createEffect` (public in `remotion` since 4.0.479; the brand code still uses `Internals.createEffect`):
  `createEffect<Params, State>({type: 'com.example.fx', label, documentationLink, backend: '2d' | 'webgl2' | 'webgpu',
  calculateKey: (p) => string, setup: (target) => state, apply: ({source, target, width, height, params, state,
  flipSourceY}) => void, cleanup: (state) => void, schema, validateParams})`. 2D apply = drawImage + getImageData loop + putImageData (slow per pixel); WebGL2 apply = full-screen quad shader, honour `flipSourceY`, premultiplied alpha.
- `@remotion/effects/<name>` factories go in `effects={[...]}` (array order = processing order; every factory accepts
  `disabled`). Defaults and values seen in team code:
  `blur({radius})`; `tint({color, amount})` (amount default 0.5; `0.06` cyan unifies stock footage);
  `dropShadow({})` (radius 12, offsetX 8, offsetY 8, opacity 0.5, color #000; two white `radius 100` copies = glow);
  `burlap({size, roughness, color})` (amount 0.55, seed 0); `paper({amount, folds, colorFront, colorBack, contrast,
  roughness, fiber, crumples, seed, scale})`; `linearProgressiveBlur({start: [u, v], end: [u, v], startBlur = 0,
  endBlur = 50})` (defaults start [0, 0.5], end [1, 0.5]); `radialProgressiveBlur({center = [0.5, 0.5], width = 1,
  height = 1, rotation = 0, start = 0, startBlur = 0, endBlur = 50})`; `grayscale({})`; `colorCorrection({pivot,
  shadows, whites, blacks, temperature})`; `chromaticAberration({amount, angle})`; `pixelDissolve({progress, columns,
  rows, seed, feather})`; `evolve({progress, direction: 'left'|'right'|'bottom', feather})`; `colorKey({similarity,
  keyColor, spillSuppression, smoothness})` (the greenscreen demo passes only `similarity: 0.37`, so keyColor has a
  default); `translate({u, v})` (imported as uvTranslate); `hue({})`;
  `noise({amount, seed, premultiply})`; `shine({})`; `wave({phase, amplitude, wavelength})`; `waves({colors,
  thickness, angle})`; `rings({colors, center, thickness, gap})`; `scanlines({amount, spacing, thickness, offset,
  premultiply})`; `vignette({amount, radius, feather, roundness, color, mode: 'alpha', center})`; `gridlines({gridSize,
  lineWidth, lineColor, rotationX, perspective, offsetY})`; `pattern({scale, gapX, offsetU, offsetV, rowOffset})`;
  `starburst({rays, rotation, smoothness, colors, origin})`; `halftone({dotSize, dotSpacing, shape: 'circle'|'square'|
  'line', colorMode: 'solid'|'source', dotColor, invert})`; `halftoneLinearGradient({...})`; `fisheye({fieldOfView,
  center, radius, zoom})`; `glow({radius, intensity, color, threshold})`; `cornerPin({topLeft, topRight, bottomRight,
  bottomLeft})` (UV of the source); `zigzag({colors, direction, thickness, gap, angle, offset, amplitude,
  wavelength})`; `tear({angle, progress 0..2, rotation, jaggedness})`; `lightLeak({seed, hueShift, progress})`;
  `noiseDisplacement({center, radius, strength, seed, grainSize, passes, feather, biasDirection, biasAmount})`;
  `scale({scale, horizontal, vertical})`; `brightness({amount})`.

Media
- `@remotion/media` `Video`: `src` (https, staticFile, HLS `.m3u8`), `trimBefore`, `trimAfter` (exclusive), `from`,
  `durationInFrames` (fractional seen), `playbackRate`, `loop`, `muted`, `volume` (number or `(f) => number`, f is
  media-relative), `freeze`, `premountFor`, `name`, `style`, `objectFit`, `objectPosition`, `cropRight` (4.0.500, 0-1),
  `effects`, `debugOverlay`, `logLevel`, `showInTimeline`, `headless` + `onVideoFrame(frame: CanvasImageSource)`
  (decode without DOM, draw it yourself). `Audio`: `src`, `trimBefore`, `trimAfter`, `from`, `loop`, `volume`,
  `toneFrequency` (pitch), `playbackRate`, `hidden`, `showInTimeline`, `name`.
- Classic tags renamed: `Html5Video`, `Html5Audio` (`volume` up to 10 as gain, `loop`, `trimBefore/After`, legacy
  `startFrom/endAt`, `audioStreamIndex`, `pauseWhenBuffering`), `OffthreadVideo` (`pauseWhenBuffering`,
  `acceptableTimeShiftInSeconds`, `transparent`, `onVideoFrame`). The core `Audio` name still exists.
- ProRes with alpha in `@remotion/media`: call `registerProresDecoder()` from `@mediabunny/prores` in the entry file
  before `registerRoot` (brand/index.ts, jonny/index.ts). AC3: `registerAc3Decoder()/registerAc3Encoder()`.
- `@remotion/media-utils`: `useAudioData(src)`, `useWindowedAudioData({src, frame, fps, windowInSeconds})` ->
  `{audioData, dataOffsetInSeconds}`, `visualizeAudio({fps, frame, audioData, numberOfSamples, optimizeFor: 'speed',
  dataOffsetInSeconds})`, `visualizeAudioWaveform({..., windowInSeconds, channel})`, `getWaveformPortion({audioData,
  startTimeInSeconds, durationInSeconds, numberOfSamples, channel, normalize, outputRange: 'minus-one-to-one'})`,
  `createSmoothSvgPath({points})`, `audioBufferToDataUrl(buffer)`, `getVideoMetadata`.
- `@remotion/sfx`: 32 URL exports (whip, whoosh, pageTurn, uiSwitch, mouseClick, shutterModern, shutterOld, ding, bruh,
  vineBoom, windowsXpError, fah, spongebobFail, omgHellNah, priceIsRightFail, romanceMeme, boneCrack, animeWow, yippee,
  loadingLag, wilhelmScream, macQuack, skedaddle, snapchatNotification, nellyAhh, sanctuaryGuardianWhat, minecraftHurt,
  ohMyGodVine, illuminatiConfirmed, dramaticBoomer, triggered, recordScratch), usable as `src`.
- Metadata: `parseMedia({src, acknowledgeRemotionLicense: true, fields: {slowDurationInSeconds: true, dimensions:
  true}})`; mediabunny `new Input({formats: ALL_FORMATS, source: new UrlSource(src)})`, `computeDuration()`,
  `getPrimaryVideoTrack()`, `computePacketStats(50).averagePacketRate` snapped to 23.976/24/25/29.97/30/50/59.94/60.

Text, captions, paths, shapes, fonts
- `@remotion/captions`: `Caption {text (leading space), startMs, endMs, timestampMs, confidence, pageBreakAfter?}`,
  `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds})` -> pages `{startMs, durationMs, text,
  tokens [{text, fromMs, toMs}]}` (team uses 800 ms or 1100 ms).
- `@remotion/layout-utils`: `measureText({text, fontFamily, fontSize, fontWeight, letterSpacing, validateFontIsLoaded:
  true})`, `fitText({text, withinWidth, fontFamily, fontWeight, textTransform, validateFontIsLoaded})`,
  `fitTextOnNLines({text, maxLines, maxBoxWidth, maxFontSize, ...})` -> `{fontSize, lines}`, `fillTextBox({maxBoxWidth,
  maxLines}).add({text, ...})` -> `{newLine}`. `@remotion/rounded-text-box`: `createRoundedTextBox({textMeasurements,
  textAlign, horizontalPadding, borderRadius})` -> `{d, boundingBox}`.
- `@remotion/paths`: `evolvePath(progress, d)` -> `{strokeDasharray, strokeDashoffset}`, `getLength`,
  `getPointAtLength`, `getTangentAtLength`, `interpolatePath`, `reversePath`, `translatePath`, `resetPath`,
  `scalePath`, `warpPath`, `getBoundingBox`, `parsePath`, `reduceInstructions`, `serializeInstructions`, `extendViewBox`,
  `PathInternals.cutPath/debugPath`. `@remotion/shapes`: `makeRect/Circle/Triangle/Star/Polygon/Pie/Heart` and
  components `Rect`, `Triangle` (`edgeRoundness`), `Circle`, `Ellipse`, `Star`, `Arrow`, `Callout`, `Heart`, `Pie`,
  `Polygon`, `Spark` (accept effects and timeline props).
- Fonts: `@remotion/fonts` `loadFont({family, url: staticFile(...), weight, format})` at module scope;
  `@remotion/google-fonts/<Font>` `loadFont('normal', {subsets, weights})` -> `{fontFamily, waitUntilDone}`;
  `loadVariableFont('normal', {subsets})` -> `{axes, fontFamily}`; `ignoreTooManyRequestsWarning`.
- `@remotion/rough-notation`: `Highlight`, `Underline`, `Circle`, `Box`, `CrossedOff`, `StrikeThrough`, `Bracket`
  driven by `progress` 0..1 (+ color, strokeWidth, roughness, padding, iterations, bowing, maxRandomnessOffset).
- `@remotion/noise` `noise2D(seed, x, y)` in [-1, 1]. `@remotion/light-leaks` `<LightLeak seed hueShift durationInFrames>`
  (itself a Sequence; docs say replaced by the `lightLeak()` effect and dropped in 5.0). `@remotion/starburst`
  `<Starburst rays colors vignette rotation>`.

Transitions (`@remotion/transitions`)
- `TransitionSeries {from, name}` with `.Sequence {durationInFrames, trimBefore, premountFor, name, style}`,
  `.Transition {presentation, timing}` (no Transition between two Sequences = hard cut), `.Overlay {durationInFrames,
  offset}` (centred on a cut, consumes no time, cannot neighbour a Transition or another Overlay, must fit inside both
  neighbours). Timings: `linearTiming({durationInFrames, easing})`, `springTiming({config, durationInFrames,
  durationRestThreshold, reverse})` (default = bouncy default spring, about 28 f). Custom timing object:
  `{getDurationInFrames({fps}), getProgress({fps, frame})}`. Custom presentation: component receiving
  `{children, presentationDirection, presentationProgress, presentationDurationInFrames, passedProps}`.
  `useTransitionProgress()` -> `{entering, exiting, isInTransitionSeries}` inside scenes. Shader presentations
  (blur-slide, book-flip, cross-zoom, crosswarp, dissolve, dreamy-zoom, film-burn, linear-blur, ripple, swap, zoom-blur,
  zoom-in-out) render through HTML-in-canvas (`x({})`, `blurSlide()`), throw when unsupported. `pushCut({cutProgress,
  transformOrigin, outgoingScale, incomingStartScale, incomingEndScale, flashColor, flashOpacity, flashFrames})`.

Other packages seen
- `@remotion/mac-cursors` (4.0.513, not installed): `<MacOSCursor cursor="auto"|'default'|'pointer'|'text'|
  'ew-resize'|'col-resize'|'row-resize'|'ns-resize'|'custom' customCursor='url("data:...") 15 13, alias' style>`;
  hotspot at the component origin, 39 bundled cursors, unknown keywords draw the default arrow.
- `@remotion/gsap` (not installed, source not in the copy): `const scope = useGsapTimeline<HTMLDivElement>(({timeline,
  selector}) => {...})` then `<AbsoluteFill ref={scope}>`; timeline in seconds, seeked per frame, per Sequence local
  time, survives premount, primes start values so overlapping tweens are order-independent.
- `@remotion/lottie` `<Lottie animationData loop playbackRate direction assetsPath />`, `getLottieMetadata(data)`;
  `@remotion/gif` `<Gif fit loopBehavior="loop"|'pause-after-finish'|'unmount-after-finish' effects>`;
  `@remotion/rive` `<RemotionRiveCanvas src effects>`; `@remotion/animated-emoji`.
- `@remotion/player` `<Player component compositionWidth compositionHeight durationInFrames fps inputProps autoPlay
  loop controls clickToPlay initiallyMuted numberOfSharedAudioTags acknowledgeRemotionLicense />`, `PlayerRef` (toggle,
  play, pause, seekTo, getCurrentFrame, mute, unmute, isFullscreen) with events 'frameupdate', 'play', 'pause',
  'mutechange', 'fullscreenchange'; `@remotion/web-renderer` `renderMediaOnWeb({composition: {component,
  durationInFrames, fps, width, height, id, defaultProps}, inputProps, muted, scale, onProgress})` -> `{getBlob}`.
- `@remotion/studio`: `getStaticFiles()` (local-first assets), `visualControl(key, default, schema?)`, `seek`,
  `saveDefaultProps`, `writeStaticFile`, `StudioInternals.createComposition(...)` (internal). `watchStaticFile(name,
  cb)`. `window.remotion_initialFrame = 655` before `registerRoot` opens the Studio at a frame.
- Hooks: `useDelayRender()` -> `{delayRender(label, {timeoutInMilliseconds, retries}), continueRender, cancelRender}`,
  `useRemotionEnvironment()` -> `{isRendering, isClientSideRendering}`, `usePixelDensity()`, `useBufferState()
  .delayPlayback()` -> `{unblock()}`, `prefetch(src)` -> `{free()}`, `getInputProps()`, `random(seed)`.

### 3.3 `@remotion/maptiler` (package version 4.0.529 in the copy; deps `@maptiler/sdk` 4.0.2, `@turf/turf` 7.3.2)
Status: README says "internal package, no documentation"; ESM only; `publishConfig.access` is public but it is not
installed in the target `remotion-broll` project. Needs a MapTiler API key (team uses
`process.env.REMOTION_MAPTILER_KEY ?? null`). `MapViewport` imports `'@maptiler/sdk/style.css'` (the Remotion bundler
accepts CSS imports).
Exports: `MapViewport` (+ `MapViewportProps`, `MapViewportMapOptions`, `MapAdministrativeBorders`), `MapOverlay` and
its alias `MapMarker` (+ `MapOverlayProps`, `MapOverlayAnchor`), `MapSource`, `MapLayer`, `MapPoint`, `MapHeatmap`,
`MapPolygon` (+ `MapPolygonData`, `MapPolygonFeature`), `MapPolyline` (+ `MapPolylineData`, `MapPolylineFeature`),
`MapRegion` (+ `MapRegionFeature`), `MapRoute` (+ `MapRouteFeature`), `useMapTiler` (+ `MapTilerContextValue`).

Common to every component: they are timeline items. Each accepts `from`, `durationInFrames` (default Infinity),
`trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline` (false by default for MapSource and
MapLayer), `premountFor`, `postmountFor`, and `controls` (Studio). Internally each renders
`<Freeze frame={freezeFrame} active={isPremountingOrPostmounting}><Sequence layout="none" ...>`. MapViewport,
MapOverlay, MapRegion and MapRoute are Studio-editable (`Interactive.withSchema`, `supportsEffects: false`); none takes
`effects`. A scene is one `MapViewport` with children that have their own `from` (overlay children see LOCAL frames).

`<MapViewport>` props (defaults): `apiKey: string | null` (required; null shows a "MapTiler key needed" placeholder
and does not mount children); camera, all keyframable: `centerLongitude` 0, `centerLatitude` 0, `zoom` 4 (0..22),
`bearing` 0, `pitch` 0 (0..85), `paddingTop/Right/Bottom/Left` 0; look: `mapStyle` (`MapStyle.BASIC`), `backgroundColor`
`'#dfe7e2'`, `showLabels` true (false removes EVERY symbol layer, icons included), `administrativeBorders` `'all'` |
`'country-only'` | `'none'` (matches style layer ids containing "border" / "other border"), `language`, `projection`,
`terrain` false, `terrainExaggeration` 1; `mapOptions` (SDK options minus camera/container/style fields, read once at
creation), `onMapReady(map)` (after first load + idle), `children`. The map is created non-interactive with
`fadeDuration: 0` and `preserveDrawingBuffer: true`; MapTiler logo and attribution are kept.

`<MapOverlay>` / `<MapMarker>`: `latitude`, `longitude` (required), `anchor` `'center'` (9 anchors: top, bottom, left,
right, the four corners, center), `offsetX` 0, `offsetY` 0, `opacity` 1, `rotation` 0, `rotationAlignment`
`'viewport'` (`'map'` adds the map bearing), transform style props, `children`. Places a div at
`map.project([lng, lat]) + offset` with a percentage translate from the anchor, `pointerEvents: 'none'`.

`<MapRegion>`: `feature` (GeoJSON Polygon Feature with `properties {name, source}`), `id` (layer prefix), `fillColor`
(required; schema default `'#d52b1e'`), `fill` 0 (fill opacity), `glow` 0.72 (white blurred underlay: width 22, blur 8),
`progress` 1 (outline draw-on 0..1, outer ring only), `strokeColor` `'#8f1712'`, `strokeWidth` 9. Layers `${id}-fill`,
`${id}-outline-glow`, `${id}-outline`; paint transitions forced to 0.
`<MapRoute>`: LineString `feature`, `id`, `glow` 0.72, `progress` 1, `strokeColor` `'#006cff'`, `strokeWidth` 9.
`<MapPolyline>`: SDK polyline options + `data` (LineString/MultiLineString Feature, FeatureCollection or URL),
`progress` 1, `layerId` (required, unique), `sourceId` (default `${layerId}-source`); animatable per frame without
rebuild: lineBlur, lineColor, lineGapWidth, lineOpacity, lineWidth, outlineBlur, outlineColor, outlineOpacity,
outlineWidth. Reveal = turf `lineSliceAlong(line, 0, max(0.001, length * progress))` (constant geographic speed,
never empty). Async creation errors go to `cancelRender`.
`<MapPolygon>`: `data` (Feature, FeatureCollection or URL), `fillColor`, `fillOpacity`, outline options, `progress`
(when set the outline becomes an internal self-drawing MapPolyline, default white), `layerId`.
`<MapPoint>`: points, clusters, labels; animatable pointColor, pointOpacity, pointRadius, outline*, labelColor,
labelSize. `<MapHeatmap>`: `data`, `weight`, `colorRamp`, `zoomCompensation`, animatable `intensity`, `opacity`,
`radius`. `<MapSource id source>` and `<MapLayer layer beforeId>`: raw MapLibre sources and layers with diffed paint and
layout updates. `useMapTiler()` returns `{map, cameraRevision, styleRevision}` for custom overlays and layers.

Determinism (the part worth copying for ANY imperative WebGL library):
1. Initial load: `const [h] = useState(() => delayRender('Loading MapTiler map'))`, continue after `load` plus the first
   `idle`.
2. Every camera change: if any camera prop differs by more than 1e-7, `delayRender`, `map.once('idle', finish)`,
   `map.jumpTo({...})`, `triggerRepaint()`; cleanup unhooks and releases. `idle` fires only after all tiles are loaded and
   painted. Never `flyTo`/`easeTo` (their internal timers do not follow the frame): the frame-driven interpolate IS the
   animation.
3. No internal animation anywhere: `fadeDuration: 0`, `interactive: false`, paint `'*-transition': {delay: 0,
   duration: 0}`.
4. Every data or paint update goes through `delayMapRender` (delayRender + once idle + triggerRepaint, returns cleanup).
5. Premounting: DOM wrappers hide with opacity and freeze; WebGL layers cannot be hidden with CSS, so
   `useMapPremounting` sets `layout.visibility: 'none'` while `SequenceContext.premounting || postmounting`.
6. A JSON `structuralKey` of non-animatable options decides when to rebuild layers; primitive paint values go through
   `setPaintProperty` only.
Cost and gotchas: every frame with camera motion waits for tiles (network-bound renders; give maps `premountFor`);
zoom-stop arrays or expressions in animated props rebuild layers every frame; `mapStyle`/`showLabels`/borders changes
trigger a full `setStyle`; MapRegion and MapRoute probably do not re-add layers after a runtime style change; layer
ids must be unique per map; a working WebGL backend is required in headless Chrome.

### 3.4 `@remotion/three` (read from `repo/packages/three/src`; installed on the target: @remotion/three 4.0.528, three 0.186.1, @react-three/fiber 9.8.1)
Exports: `ThreeCanvas`, `ThreeCanvasProps`, deprecated `useVideoTexture`, `useOffthreadVideoTexture` (+ option types);
subpath `@remotion/three/webgpu`: `ThreeWebGPUCanvas`, `ThreeWebGPUCanvasProps`.
- `<ThreeCanvas width height {...R3F Canvas props}>`: `width` and `height` are REQUIRED positive INTEGERS (validated;
  `width * 0.5` on an odd width throws). It is also a timeline item: accepts `from`, `durationInFrames`, `trimBefore`,
  `playbackRate`, `freeze`, `hidden`, `name` (default `'<ThreeCanvas>'`), `showInTimeline` (default false),
  `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted` (no wrapper Sequence needed).
  While premounted it is frozen and hidden with opacity 0 (GL context and assets initialise early).
- Behaviour: delayRender until the canvas is created (released in `onCreated`, your `onCreated` still runs);
  `frameloop` is forced to `'never'` while rendering and the scene is advanced exactly once per Remotion frame under a
  per-frame delayRender; `resize` merged as `{offsetSize: true, ...resize}` and R3F auto `setSize` replaced, so the
  drawing buffer stays width x height regardless of preview zoom; any Suspense-based loader (useLoader, drei
  useTexture/useGLTF) is covered by an internal Suspense boundary whose fallback holds a delayRender.
- Rule: animate only from `useCurrentFrame()` inside the canvas (contexts are bridged). R3F `useFrame` delta and clock
  are wall-clock based and must not drive motion. Prefer `time = frame / fps` for fps-independent speeds.
- `ThreeWebGPUCanvas` (props = ThreeCanvasProps minus `gl`): async `WebGPURenderer` factory (`await renderer.init()`),
  one-time `compileAsync` + real `renderAsync` warm-up (compile alone does not prepare node bindings), and
  `device.queue.onSubmittedWorkDone()` before each frame is released.
- Deprecated texture hooks: `useVideoTexture(videoRef)` (preview; needs a hidden `<Video>` and
  requestVideoFrameCallback, returns null without it, throws in client-side rendering) and
  `useOffthreadVideoTexture({src, playbackRate = 1, transparent = false, toneMapped = true, delayRenderRetries?,
  delayRenderTimeoutInMilliseconds?})` (render only: throws outside rendering; fetches one frame image per frame from the
  local proxy). Classic switch: `isRendering ? useOffthreadVideoTexture : useVideoTexture`. Newer pattern in the team
  code (example/VideoTexture.tsx): `@remotion/media` `<Video src headless muted onVideoFrame>` drawing into an
  OffscreenCanvas + `CanvasTexture` (`needsUpdate = true`), and in render mode call `advance(performance.now())` again
  inside `onVideoFrame` because frame extraction is asynchronous.
- Lean GL for stills or 2D-heavy scenes: `gl={{alpha: false, antialias: false, stencil: false, depth: false}}`,
  `onCreated={(s) => s.gl.setClearColor('white')}`; `linear` prop to disable sRGB conversion of video colours;
  `meshBasicMaterial toneMapped={false}` for video planes.
- drei `<Html transform portal>` renders in a separate React root: wrap its content in
  `<Internals.RemotionContextProvider contexts={Internals.useRemotionContexts()}>` or `useCurrentFrame` breaks.

### 3.5 `@remotion/svg-3d-engine` (read from `repo/packages/svg-3d-engine/src`; same exports in installed 4.0.528)
Orthographic 3D for SVG and DOM, no WebGL. Exports: types `MatrixTransform4D` (16 numbers, ROW-major, column vectors),
`Vector4D` ([x, y, z, w]), `ThreeDReducedInstruction` (M/L/Z with point, C with cp1/cp2/point, Q with cp/point),
`FaceType` ({color, points, centerPoint, crispEdges}); functions:
- `translateX(x)`, `translateY(y)`, `translateZ(z)`, `scaled(n | [sx, sy, sz])`, `scaleX(x)`, `scaleY(y)` (use
  `scaled([1, 1, sz])` for z), `rotateX(rad)`, `rotateY(rad)`, `rotateZ(rad)` (Rodrigues matrices; in SVG screen space
  rotateZ(+a) turns clockwise).
- `reduceMatrices([A, B, C])` = C*B*A: the FIRST entry is applied FIRST (chronological, opposite of reading a CSS
  transform string); nulls are skipped. `aroundCenterPoint({matrix, x, y, z})` pivots.
- `interpolateMatrix4d(t, m1, m2)`: element-wise lerp, not clamped. Fine for small pose blends; for big rotations
  interpolate the angles and rebuild the matrix (element-wise lerp shrinks and shears mid-way).
- `makeMatrix3dTransform(m)`: CSS `matrix3d(...)` string (column-major) so the same math drives a DOM element. BUG in
  4.0.528 and 4.0.529: the string has no closing ')'; fine as the whole `transform` value, broken if you append more.
- `transformPath({path, transformation})`: 2D SVG path of a transformed flat path (z dropped).
- `threeDIntoSvgPath(instructions)`: prints x, y only (no perspective divide).
- `extrudeElement({depth, pressInDepth, sideColor, points, crispEdges, description?})` and
  `extrudeAndTransformElement({...same, transformations})`: `points` are @remotion/paths instructions (e.g.
  `parsePath(makeRect({width, height, cornerRadius}).path)`); the outline is subdivided 3 times (8 ribbons per segment)
  and only the SIDE ribbons are returned (outline at z = +depth/2, ribbons to z = -depth/2 + pressInDepth), all in one
  `sideColor`. No depth sorting and no front face: draw the front separately (HTML with `matrix3d` or
  `transformPath`) AFTER the sides. Valid only for moderate tilts (well under 90 degrees). Never add CSS `perspective`
  to a parent (it would affect the HTML front face but not the SVG sides).
- Team recipe (design/src/helpers/Outer.tsx, promo-pages 3DEngine/Outer.tsx): rest pose `rotateX(-PI/20)`; active
  pose `scaled(min(1 + 0.1 * depthFactor, (20 + width) / width))`, `rotateX(-PI/16)`, `rotateX(sin(a) / 4)`,
  `rotateY(-cos(a) / 4)`; blend with `interpolateMatrix4d(progress, rest, active)`; depth
  `interpolate(progress, [0, 1], [10, 20]) * depthFactor`; press `15 * depthFactor` into both `pressInDepth` and the
  face's translateZ; pivot `[translateX(-w/2), translateY(-h/2), T, translateX(w/2), translateY(h/2)]`; front face
  `[translateZ(-depth/2 + press), translateZ(1.1), T]`. For video, replace mouse inputs with springs.
- The brand package's `3DContext` (brand/src/3DContext, example/src/3DContext) builds a React scene graph on top:
  `<RotateX radians>`, `<RotateY>`, `<RotateZ>`, `<TranslateX|Y|Z px>`, `<Scale factor>` compose matrices through
  context (outermost applied first), `ExtrudeDiv` renders SVG walls + HTML front/back faces at z = -/+0.48 * depth with
  culling (back visible when m10 <= 0, top visible when m9 > 0), each wrapper a Studio-editable
  `Sequence layout="none"`. This is the team's "sticker 3D" look: orthographic, black extruded edges, 2-4 px black
  borders.

### 3.6 `@remotion/timeline-utils` (read from `repo/packages/timeline-utils/src`; installed 4.0.528 has the same list plus the `audio-waveform-worker` subpath)
Studio-oriented utilities (browser: WebCodecs, OffscreenCanvas, Worker; decoding via mediabunny). Useful for editor
UI mockups and exact Studio looks; for audio-reactive video visuals prefer `@remotion/media-utils`.
- Waveforms: `TARGET_SAMPLE_RATE = 100` (peaks per second); `loadWaveformPeaks(src | InputAudioTrack, signal, {onProgress?,
  progressIntervalInMs?, waveformSampleRate = 100})` -> `{peaks: Float32Array, averageVolume: number | null}` (peak = max
  |sample| over all channels per 10 ms window; averageVolume = mean-square dBFS; samples before t = 0 trimmed for edit
  lists and codec priming; results cached per rate and source; throws for live and UNIX-timestamp streams);
  `subscribeToWaveformPeaks({src, waveformSampleRate, onPeaks, onError})` (one shared module worker, cache, in-flight
  dedupe, main-thread fallback) returns an unsubscribe; `createWaveformPeakProcessor`, `emitWaveformProgress`;
  `drawBars({canvas, peaks, color, volume, width})` (one bar per pixel column, full scale = 80% of the height, clipped
  tips painted `#FF7F50`, volume a number or per-frame curve); `sliceWaveformPeaks({peaks, startFrom, durationInFrames,
  fps, playbackRate, waveformSampleRate})` (zero-padded outside the media), `sliceVisibleWaveformPeaks`,
  `getVisibleWaveformVolume`, `formatAverageAudioVolume`.
- Frames: `extractFrames({src, timestampsInSeconds (array or function of {track, container, durationInSeconds}),
  onVideoSample, signal?, repeatLastFrame = false})` shares the mediabunny Input with playback; the CALLER must
  `close()` every VideoSample. `renderFrameStripToCanvas({canvas, src, fromSeconds, toSeconds, width, frameHeight,
  devicePixelRatio, signal?})` draws a filmstrip whose slots are anchored to absolute media time (trims and splits never
  shift thumbnails) with progressive refinement from a global 10 MiB `VideoFrame` LRU (`frameDatabase`,
  `addFrameToCache`, `makeFrameDatabaseKey`); `resizeVideoFrame({frame, scale})`; `clampTimestampsToDuration`;
  strip math helpers (`WEBCODECS_TIMESCALE`, `calculateTimestampSlots`, `drawSlot`, ...).
- Loops: `getLoopDisplaySegments({displayDurationInFrames, displayOffsetInFrames, loopDurationInFrames})`,
  `getLoopDisplayWidth`, `shouldTileLoopDisplay`: computed per loop index (a float-accumulating version used to stall
  and exhaust memory; the regression test uses loop 99.999 frames).
- Determinism: pure math given the decoder; in a render, await these promises under delayRender before drawing.

### 3.7 `@remotion/design` (read from `repo/packages/design/src`)
The remotion.dev WEB component kit (Tailwind v4, Radix), not a video package: `Button` (`depth` default 1, `loading`,
`disabled`, `href` renders `<a>`, `asChild`; mouse-hover 3D extrusion via the Outer recipe above), `Card`, `Counter`
(`count`, `setCount`, `minCount`, `step`, `incrementStep`, max 9999999), `Input`, `Textarea`, `Link`, `InlineCode`,
`Select*` (Radix, content position `'popper'`), `Slider` (`value`, `onChange(number)`, `unfilledColor`, min 0, max 100),
`Spinner` (`size`, `duration`; wall-clock rAF, never use in a video), `Switch` (`active`, `onToggle`), `Tabs*`, icons
`CheckIcon`, `PlanePaperIcon`, `Triangle`. Tokens: `--font-brand` GTPlanar with `'ss03'`, `--color-brand #0b84f3`,
`--color-warn #ff3232`, neo-brutalist `border-2 border-b-4 border-black rounded-lg`. Transferable to video: the brand
tokens and the 3D button matrix recipe.

## 4. Recipes

### 4.1 Timing house style (how the team times and eases motion)

Curves the team actually uses (with where and why)

| name we give it | exact code | feel | used for |
|---|---|---|---|
| house spring (classic) | `spring({fps, frame, config: {damping: 200}})` (= damping 20, 100, 1000 at k 100, m 1) | no bounce, 50% at f5-6, 90% at f12, done at f23 (0.77 s) | almost every entrance, fade, slide, panel, logo letter, list row (brand, promo, example) |
| house spring, fitted | same + `durationInFrames: 3/10/12/15/20/25/30/34/40/90/115/300` (+ `delay`) | same shape, time-stretched to land exactly | chapter pops (10), list rows (12), card rows and stinger exits (15), callouts and badges (20), panel slides (30), slow 3D turn-in (115), 10 s glyph unroll (300) |
| Studio keyframe spring | `Easing.spring({damping: 200, mass: 1, stiffness: 100, allowTail: true, durationRestThreshold: 0.02, overshootClamping: false})` in an easing array | reaches 98% at the keyframe, last 2% settles into the next segment | every keyframed move in the Studio-era files (camera pans, pushes, pop scales, map zooms); 5-15 f segments in short-form, 20-150 f for cameras |
| expo-out | `Easing.bezier(0.16, 1, 0.3, 1)` | 49% done at 10% of the window, 94% at 40% | text and UI entrances (15-21 f), bar growth (34 f), panel expand (14 f), cursor moves, window pushes (40 f), countdown slam |
| quint-out | `Easing.bezier(0.22, 1, 0.36, 1)` | slightly softer launch | 1700 px slide-in under motion blur (18 f), rough-notation draws (22 f) |
| ease-in-out cubic | `Easing.bezier(0.65, 0, 0.35, 1)` or `Easing.inOut(Easing.cubic)` | symmetric | map camera push/pull and pans, avatar flips, drop highlights |
| CSS ease-in-out | `Easing.bezier(0.42, 0, 0.58, 1)` | symmetric, gentler | UI value drags (30 f), whip pans (25 f), hand-drawn circle |
| ease-out cubic | `Easing.out(Easing.cubic)` or `bezier(1/3, 1, 2/3, 1)` (Studio preset) | smooth decel | outline draw-ons (50 f), side panels in (1 s), goal slam (15 f) |
| accelerate out | `Easing.bezier(0.4, 0, 1, 1)`, `Easing.in(Easing.cubic)`, `bezier(0.7, 0, 0.84, 0)` (expo-in) | leaves fast | exits, explosions (18-21 f), panel out (1 s), closing fades (19 f) |
| decelerate in | `Easing.bezier(0, 0, 0.2, 1)` | lands soft | new tokens fading in after a code morph |
| overshoot out | `Easing.bezier(0.25, 0.25, 0.6884, 1.375)`, `Easing.out(Easing.back(1.8))`, `bezier(0.4681, 0.0594, 0.9171, 1.075)` | small overshoot | label reveal, drop landing, fork stab impact |
| bouncy accents | default `spring()` (16% overshoot, 28 f), `{damping: 15}` (2.8%), `{mass: 0.5}` (4%), `{mass: 0.7, damping: 12}` (4%), `{damping: 14, mass: 0.55, stiffness: 180}` (4%, 12 f), `{damping: 11, mass: 0.65, stiffness: 210}` in 10 f (20%), `{damping: 10, mass: 0.55, stiffness: 220}` (20%, 18 f), `{damping: 8, mass: 0.69, stiffness: 112, allowTail}` (20%), `{damping: 6, stiffness: 37}` squeezed into 9 f (17%) | visible bounce | ONE accent per element: card flips, coin flip, badge, map pin pop and swing, caption page pop, big-word pop, odometer roll, spin-in label |
| heavy / slow no-bounce | `{mass: 2, damping: 200}` (50% f8, done 32 f), `{mass: 3, damping: 200}` (39 f), `{mass: 20, damping: 500}` (100 f), `{damping: 30, stiffness: 40}` (36 f), `{damping: 1000, mass: 0.7, stiffness: 10}` (53 f) | calm, weighty | logo layer builds, zoom-blur grid, kinetic word wall, 3D phone entrance, squircle glide |
| linear | `Easing.linear` / no easing | constant | holds inside easing arrays, slow drifts, tilt drifts, Ken Burns, draw-ons in the sketch style, cursor tracks |

Spring facts (verified by re-implementing the solver): see the table in 3.1. The default spring overshoots 16% at
f11; `durationInFrames` never changes the shape, only the speed; frames before `delay` return `from`; below
15.6 fps springs slow down (64 ms step cap).

Durations (30 fps unless stated)
- Micro: button press 5 f down + 11 f up (scale 0.88); click squash 7 f (`[t-1, t+5]`, scale 0.9); icon pop 12 f
  (`[s, s+5, s+12] -> [0, 1.35, 1]`); word bump 1-2 f (+7%); caption pill glide 5 f; heart pulse 9 f.
- Entrances: 12-25 f (text 15-21 f expo-out; springs 20-23 f; short-form pops 5-11 f).
- UI moves and panel slides: 30-45 f (40 f is the standard window move; side panels exactly 1 s in, 1 s out).
- Camera moves: 22 f spring reframes; 40-52 f pans and pulls; 72-149 f slow pushes; dive into a screen 149 f at
  60 fps with a 29 f pull-out (exits are faster than entrances).
- Exits: 5-20 f, faster than the matching entrance; stinger exits = the last 15 f (`spring({frame: frame -
  durationInFrames + 15, durationInFrames: 15})`); cards exit in the last 20 f.
- Holds: fill the rest; data pieces settle by about 55% of the composition and hold (BarChart settles at f101 of 180).
- Scene lengths: short-form shots 1.6-2.2 s (47-66 f), inserts 1.2-7 s, UI inserts 5-8 s, Studio close-up shots
  0.9-1.67 s in the edit (standalone takes are longer handles), talking-head chapters 4-42 s (median 25 s).
- Transitions: shader transitions 24-30 f linear (the shader eases), fades 15 f, slides 22 f, springTiming about 28 f,
  pushCut 11 f, keyframed pushes 6-8 f, overlays 15-30 f centred on the cut.

Staggers
- 1 f: wordmark letters swinging on an arc; 2 f: kinetic letters, code tokens, end-card icons, concentric rings;
  3 f: gridlines, streamed LLM tokens; 3.75 f: bottom-up social rows (fractional delays are fine); 4 f: digit columns,
  word pops, collage sides; 5 f: list rows in a tier, end-card rows, 5-8 f drop-in collage; 7 f: second beat of a
  chapter pop; 8 f: bars, flying cards, step-card items (0/8/15/23); 10 f: logo layers, trending list items;
  12 f: sketch months, map pins; 67 f: conveyor items (loop / 4).
- Formula style: `delay = base + index * n`, two-level `row * 5 + item * 2`, bottom-up `delay = start + ((indexFromLast - 1) / 4) * (30 - 15)`, golden-angle direction for radial bursts.

Rhythm rules the team follows
- Beats overlap: the next element starts 2-4 f before the previous ends (maps, promos); nothing waits for a full stop.
- A 5 f breath between phases (logo draw ends f60, split starts f65).
- Entrance order: background/container first, text 3-7 f later, data after text, the emphasis callout last and landing
  with the last data item (BarChart: text 3-26, panel 12-31, grid 20-50, bars 35-101, badge 82-101).
- Big beat at 3 s: Skills 2.0 clips land their main event at f90 for 18-21 f.
- Stop-motion look: `posterize: 3` (10 updates/s) or `Math.floor(frame / 3) * 3`; the stock hand footage is animated
  on threes; a literal 10 fps composition for one clip.
- Sound on the beat: SFX start on the frame of the visual event (chime on the chapter-number pop, click per list row,
  whoosh with the light-leak flash at volume 0.1, prompt-appear on frame 0 of the insert).
- Speech sync: inserts start on the word's frame `round(startMs / 1000 * fps)` minus 0-2 f of lead; list rows appear on
  speech-cued absolute frames (gaps 75-100 f).
- Loops end on the first frame's state (explicitly engineered).

Reference beat sheets (copy these rhythms)
- Data card (`example/BarChart.tsx`, 180 f): eyebrow [3,20], title [5,26] +22 px rise, panel [12,31], gridlines
  [20+3i, 38+3i], bars `start = 35 + 8i`, 34 f growth with synced count-up, value labels [start+3, start+18], category labels [start+8, start+23],
  badge [82,101] spring pop, ambient glow 0.92 to 1.08 over the whole comp.
- Product promo (`example/ParseAndDownloadMedia`, 1000 f): 0-20 zoom settle 1.1 to 1; 20-40 "New" badge slides off;
  80-195 3D turn-in (spring, durationInFrames 115) then endless drift; 150-350 progress fill (ease-in); callouts at 185
  and 237 exactly when the fill passes them; 350 text roll to "Saved"; 420 curtain end card.
- Chapter panel (`brand/announcements/whats-new-in-remotion`): panel in 15-45 (out-cubic, presenter pushed 20% in
  sync), number pop at 30 (10 f spring) with chime, title rises 37-47, hold, panel out 150-180 (in-cubic).
- Map story (`example/SwitzerlandMap/SwitzerlandMap.tsx`, 240 f): push-in 0-72, creep 72-124, pan + pull-out 124-164
  (easeInOutCubic), outline draws 76-126, fill pops 122-154 ([0, 0.3, 0.24]), glow 142-154, second region 162-218,
  22 f hold.
- GSAP title card (`example/Gsap/Showcase.tsx`, 7 s): build 0-2.05 s (kicker, masked word rise with 0.1 s stagger, rule
  wipe, fanned cards back.out(1.45)), live hold with secondary motion 2-4.6 s, fast staggered exit (in-eases,
  0.035-0.06 s staggers) 4.65-5.3 s, full-frame wipe 5.0-5.7 s, end line lands 6.2 s, 24 f hold.
- Short-form music explainer (`jonny/disco-light-show/Composition.tsx`, 60 s vertical): a new layer every 2-4 s, each
  entering with a 6-8 f spring push or 5-11 f pop, exiting with a push, pendulum swing or 4 f fade; captions always on.
- Studio close-up montage (`brand/CloseUpsSeries.tsx`, 60 fps): 8 hard cuts of 54-100 f (mean 1.33 s), one feature and
  one gesture per shot, `trimBefore` into the action, `premountFor={30}`.

### 4.2 How the team structures compositions and scenes

Registries
- `example/Root.tsx`: 285 `<Composition>`, 19 `<Still>`, 50 `<Folder>` (max nesting 2), 24 components that register
  their own `<Composition>`, 50 compositions with `lazyComponent`. fps: 271 at 30, 7 at 60, 2 at 24, one at 24.87 on
  purpose. `brand/Root.tsx`: about 100 compositions in nested Folders (Logo, HomepageAssets, Showcases, VideoElements,
  Recorder, CloseUps, StudioAssets, SocialMediaAnnouncements > whats-new, effect-showcases, skills-2-0, webmcp,
  canvas-capture-announcement, effects). `jonny/Root.tsx`: Folders DiscoLightShow (27) and HowCanRemotionBeFree
  (+ Scenes). A second root can live in the same package (`brand/Brand/index.ts`, `brand/studio-code-handoff`).
- fps policy: 60 fps for screen-recording close-ups and device promos (recordings are 60 fps); 30 fps for logo, social,
  explainer and effect pieces; 25 fps for one ping-pong loop; 10 fps for a stop-motion hand clip.
- Canvas sizes seen: 1920x1080; 1080x1080; 1080x1920 (shorts, reels); 1080x1350 (4:5 effect showcases); 1280x720;
  1080x540 and 1080x500 banners (square design center-cropped with `marginTop: -(1080 - h) / 2`); 1200x630 OG cards;
  2048x720 and 3200x520 design sheets; odd sizes for inserts meant for an editor (1071x102 title strip, 1344x1700,
  1920x1920, 2358x2586, 1350x796, 640x360 Player demo).
- Stills are usually `<Composition durationInFrames={1}>` (logo exports, UI stills), sometimes `<Still>`.

Scene ownership
- A scene file exports `XPreview` (the scene) and `X = () => <Composition component={XPreview} .../>`; Root renders
  `<X />`; a master cut imports `XPreview` directly (brand close-ups). Or the scene exports `X_DURATION_IN_FRAMES` and
  Root imports it (jonnys-videos, brand effects, DesignSystems). Computed totals are exported too:
  `PUSH_CUT_DEMO_DURATION_IN_FRAMES = 90 + (90 + 5) - 11`.
- Inside a scene, beats are module constants derived from each other (`HALFTONE_ENABLE_FRAME = ROTATION_START +
  ROTATION_DURATION / 2 + 72`, `ACTION_DELAY` added to every beat), so one change ripples consistently.
- Scenes are also registered individually (Folder "Chapters" or "Scenes") so each can be previewed and edited alone,
  plus the combined master (MultiSceneSample 3 x 90 + combined 270; whats-new 11 chapters + master).

calculateMetadata patterns
- Duration from data: sum of trimmed takes from a silence table (whats-new, 8327 f), sum of edit sections (jump cuts),
  pages x frames per page from a fetched manifest with a fallback of 90 f (docs montage), audio length via mediabunny
  (LogoHorn), media duration/size/fps via parseMedia or mediabunny (Composition may omit width/height/fps/duration).
- Size from props: `({props}) => ({width: props.width, height: props.height})` so a UI mock renders at any size; reel
  variant returns 1080x1920 (+3 f); format enum `'widescreen' | 'instagram'` with a per-format layout table.
- Render defaults for alpha overlays: `{defaultCodec: 'prores', defaultProResProfile: '4444', defaultPixelFormat:
  'yuva444p10le', defaultVideoImageFormat: 'png'}`; `defaultOutName: 'whats-new-' + platform`; `defaultCodec: 'aac'`.
- Data injected into props (cursor JSON + media metadata with `Promise.all`), so components need no delayRender.
- Even dimensions: `Math.floor(width / 2) * 2`.

Three ways to cut scenes (all used)
1. `TransitionSeries` for overlapping transitions (shader or classic) and as a named series of hard cuts; total =
   from + sum(sequences) - sum(transitions); `TransitionSeries.Overlay` (light leak, white flash) centred on a hard cut
   adds nothing to the length. pushCut needs the incoming Sequence lengthened by the pre-cut frames and its content
   wrapped in `<Sequence from={5}>` so its frame 0 is the cut.
2. `Series` of `Series.Sequence` with `trimBefore` and `premountFor={30}` for montages and speed ramps.
3. A flat list of absolutely positioned `Sequence` layers with explicit `from`/`durationInFrames` (source order = z
   order) and keyframed pushes, pops, flashes and swings between them: the short-form and newest style. Same edit can be
   expressed all three ways (example/Issue8974TimelineInteractivity).

Layer and clock techniques
- Sequence as layer box: `<Sequence width={480} height={160} style={{position: 'absolute', translate, scale}}>`
  embeds a standalone composition (its `useVideoConfig` reports 480x160) and scales it; `<Sequence width={1920}
  height={1080}>` inside a 1080x1920 frame is a movable sub-canvas camera.
- `trimBefore` equal to `from` keeps a late-mounted child's clock equal to the master clock (captions synced to the
  master voiceover); equal `from - trimBefore` on two Sequences lets one layer be split (pass behind footage, then in
  front) without restarting its animation.
- Negative `from` starts a recording mid-way (`AbsoluteFill from={-455}`); a Sequence can run past the composition end.
- Frame as a prop: `<FolderTree frame={pingPongFrame} />` so a time remap (ping-pong, speed, freeze) reaches children.
- Where to read the frame: inside the retimed container (robust) or in the parent with pre-baked keys (fragile).
- `premountFor={30}` (0.5 s at 60 fps, 1 s at 30 fps) on every media Sequence that starts after 0; caption pages
  `premountFor={fps}`; OffthreadVideo cuts `1.5 * fps`; `postmountFor` for fast backward scrubbing.
- Every element gets a `name`; internal wrappers `showInTimeline={false}`.

Composition archetypes found (use as templates)
- Studio close-up: one continuous shot; `Solid` bg > `HtmlInCanvas` with progressive blur > tilted `AbsoluteFill` with
  `from`/`playbackRate` > `Video` + `MacOSCursor`.
- Talking-head announcement: master `TransitionSeries` of per-chapter compositions (each = one silence-trimmed take +
  overlays at local frames: chapter panel at 0.5 s, b-roll 3-5 s, callouts 2.5-5 s, one overlay every 4-10 s) with
  light-leak Overlays at two chapter changes.
- Caption-first vertical explainer: voiceover Audio + dark `Solid` + always-on caption band (`Sequence width={1080}
  height={360} style={{translate: '0px 780px'}}`) + short inserts (1.2-7.4 s) starting on their words, placed above
  the captions.
- Short-form music explainer: 24 flat layers over a procedural background, keyframed pushes every 2-4 s, captions
  band, global post effect via `HtmlInCanvas` around the whole master for the outro.
- Effect showcase (1080x1350): top 675 px preview + bottom 675 px mock inspector panel, scripted cursor, one action every
  48-54 f, derived beat constants, no Sequences.
- Interactive Player demo: page owns data and state, memoized `inputProps` to `<Player>`, same props exported with
  `renderMediaOnWeb`; interactive-only UI removed when `isRendering`.
- Loopable homepage asset: all timing absolute, last frame equals first (ping-pong, Freeze crossfade, orbit math).
- NLE insert elements (lower thirds, flying cards, prompt box, chapter pops, reference pills): 1.2-7 s, transparent
  background, alpha ProRes defaults, SFX on frame 0.

### 4.3 Recipes by goal (with the team's exact values)

#### a. Entrances, exits and cards
- Enter + hold + exit in ONE call (the idiom the team teaches inside its own Skills 2.0 video):
  `interpolate(frame, [0, 20, d - 20, d], [0, 200, 200, 0], {easing: Easing.spring({damping: 200})})` replaces
  `spring(...) - spring({delay: d - 20, durationInFrames: 20})`.
- Entry minus exit spring card (`brand/announcements/whats-new-in-remotion/LowerThird.tsx:25-68`):
  `p = spring(frame, {damping: 200}) - spring(frame - durationInFrames + 15, {damping: 200})`; translateY 400 to 0 px
  and rotateZ -0.03 PI to 0 (a -5.4 deg settle); UpperReference mirrors it from -400 px with +0.05 PI. White card,
  radius 18, padding 24px 44px, `boxShadow: '0 0 30px rgba(0, 0, 0, 0.1)'`.
- Full lifecycle title card (`brand/video-elements/UpperThird.tsx:20-44`): enter `scale(spring({config: {mass: 0.5}}))`
  (4% overshoot), idle float `noise2D('noisex', 0, frame / 160) * 50` px on x and y, exit in the last 20 f
  (`spring(frame - durationInFrames + 20, {damping: 200})` -> translateY -500 px, rotate -PI/20). Card top 90 right 90,
  padding 40, radius 25, title GT Planar 700 5em, subtitle 1.8em `#4290f5`.
- Flying cards (`brand/video-elements/FlyingCards.tsx:18-66`): posterized frame `Math.floor(f / 3) * 3`, `delay = i *
  8`, spring damping 200, translateX from `width + 200` (fully off-frame) to 0, scale 0.9 to 1; dark terminal cards
  `#292C34` monospace 52 px (`❯ git clone ...`) with shadow `'0 8px 32px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.2)'`.
- Reference pill (`brand/video-elements/lower-reference/index.tsx`): white pill (padding 40px 70px, radius 25, SF Pro
  70) with a YouTube or GitHub mark, springs 400 px in from the edge while rotateZ settles from 0.05 PI.
- Step card cascade (`brand/video-elements/step-guide.tsx:184-211`): asset 0 (scale 0.9 + 0.1p, opacity p), number
  badge 8 (`{damping: 15}` bounce on scale and opacity), title line 1 at 15, line 2 at 23 (translateY (1 - p) * 30,
  opacity p); layout swap prop `assetPosition: 'left' | 'right'`.
- Chapter pop (`brand/video-elements/numbered-chapter/index.tsx`, whats-new NumberedChapter): `jump1 = spring({frame,
  config: {damping: 200}, durationInFrames: 10})` scales a 120-200 px `#4290f5` number circle; `jump2` = same 7 f later
  lifts the circle 50 px and brings the title from +220 to +120 px with opacity; chime `<Audio from={30}
  volume={0.05}>` on the pop; done by f17 of a 36 f insert.
- Pop badge in a fixed window (`example/BarChart.tsx:286-316`): `scale: interpolate(frame, [82, 101], [0.86, 1],
  {easing: Easing.spring({damping: 18}), output: 'perceptual-scale', clamp})` + opacity on expo-out.
- Scale-through-zero swap (`brand/DesignSystems.tsx:19-67`): outgoing 1.3 to 0 with
  `Easing.out(Easing.spring({damping: 200, overshootClamping: true}))` (accelerates into nothing), incoming 0 to target
  with the plain spring easing, 1 f overlap, incoming opacity 0 to 1 over 3 f to hide tiny first frames.
- Accelerating fly-away (`brand/Compose/JumpThenDisappear.tsx:9-43`): speed `10 ** interpolate(f, [0, 120], [-1, 4])`
  (x10 every 24 f), integrate by summing, then `translateZ = interpolate(sum, [0, 30], [0, -1400])` unclamped: creeps,
  then rockets away (no bezier gives this).
- Pendulum exit (`jonny/disco-light-show/Composition.tsx`): move `transformOrigin` from `'50% 50%'` to `'50% 150%'`
  first, then rotate 0 to 60 deg with the keyframe spring over 15 f. Swing-in card: origin `'0% 0%'`, rotate -18 to 0
  deg while translating in 14 f, hold, swing out 9 f to -26.7 deg.
- Grow-then-snap (`jonny/disco-light-show/OneShot.tsx`): scale [0, 56, 59] -> [0, 0.786, 1] perceptual, opacity
  [56, 59] 1 to 0 (slow grow, instant pop away). Ghost echo: opacity [0, 8, 17, 26] -> [0, 0.1, 0.1, 0] + scale 1 to 2.5.
- Burn-away number (`brand/video-elements/money-burn.tsx`): Bangers 300 px gradient text (`linear-gradient(red,
  purple)` + `WebkitBackgroundClip: 'text'` + transparent fill), `filter: drop-shadow(0 20px 40px rgba(255,0,0,0.2))
  drop-shadow(0 20px 40px rgba(255,0,0,0.8)) blur(${p * 20}px)`, floats up 400 px and fades.
- Curtain end card (`example/ParseAndDownloadMedia/Covert.tsx:8-35`): `prog = (d) => spring({damping: 200, from: 1, to:
  0, delay: d})`; dark panel `top: prog(0) * 100 + '%'`, logo `marginTop: prog(4) * 1000 + 'px'` (4 f behind).
- End card with platform-filtered rows (`brand/announcements/whats-new-in-remotion/EndCard.tsx`): block rises
  `interpolate(frame, [56, 86], ['0px 200px', '0px 0px'], {easing: Easing.spring({damping: 200})})`; rows fade with
  15 f springs at delays 56/61/66 BOTTOM-UP; the viewer's own platform row is omitted (zod enum prop). Wrap it in a
  Sequence that starts when the panel appears (the team's copy animates off-screen, see section 6).

#### b. Text and typography
- Letter rise under a clip (`brand/Applications/KineticType.tsx:50-79`): each letter in an `overflow: hidden` box,
  inline-block span `translate: interpolate(frame, [6 + i * 2, 18 + i * 2], ['0px 80px', '0px 0px'], {easing:
  Easing.bezier(0.16, 1, 0.3, 1), clamp})`; global letter index continues across lines; 16 letters done in 1.6 s.
- Masked 3D word rise (`example/Gsap/Showcase.tsx:28-40, 188-203`): each word in an 82 px tall `overflow: hidden` row
  under `perspective: 900`, from `yPercent 130, rotateX -70deg, opacity 0` with `transformOrigin: '50% 100%'`, 0.9 s
  power4.out (use `Easing.bezier(0.16, 1, 0.3, 1)` without GSAP), 0.1 s stagger; title 76 px weight 900
  letterSpacing -0.055em. Kicker: 14 px bold caps whose `letterSpacing` collapses 0.7em to 0.24em while rising 24 px.
- Arc-swing wordmark (`brand/Brand/Recorder.tsx:234-270`): every letter is a full-canvas SVG so all share one pivot far
  outside the frame (`transformOrigin: '150% 50%'`); rotate -PI/2 to 0 with `spring({damping: 200, delay: 28.2 + i})`
  (1 f stagger); container `maskImage: 'linear-gradient(black 58%, transparent 74%)'` hides letters low on the arc.
- Kinetic word wall + zoom-through (`example/BetaText/index.tsx:24-131`): 17 rows of repeated outline words (one filled
  hero word per row) in a 10000 px nowrap row centred with `marginLeft: -(10000 - W) / 2`; rows slide 1000 px from
  alternating sides and words scale from 0 with `spring({damping: 30, stiffness: 40})`; exit at f70:
  `scale = interpolate(p2, [0, 0.4], [1, 10])` UNCLAMPED (21x by f89), background `mix(1 - p2, '#fff', brand)`, rows
  fade.
- Typewriter with fixed total duration (`brand/video-elements/Prompt.tsx:37-107`): `framesPerChar = (2 * fps) /
  text.length`, start at 0.5 s, `typed = min(len, floor(max(0, f - 0.5 * fps) / framesPerChar))`; block cursor 20x38
  with `opacity: interpolate(f % 16, [0, 8, 16], [1, 0, 1])` (period divisible by any posterize step you use); box
  height precomputed from characters per line so wrapping never jumps; status line fades 0.15 s after typing.
- Terminal "thinking" status (`brand/video-elements/Thinking.tsx`): glyph cycles `['·','✻','✽','✶','✳','✢']` every
  `Math.round(0.15 * fps)` f; one highlighted character sweeps every `Math.round(0.1 * fps)` f (`#D47556` base,
  `#E08468` highlight); a verb from a 56-word list plus an ellipsis.
- LLM streaming answer (`brand/HomepageAssets/CodingPrompt.tsx:195-211`, `brand/WebMCPPromo/MacBookScene.tsx`): split
  into sub-word tokens (`'Do'`, `'ne'`, `'.'`), each a 1 f opacity ramp, 3 f apart at 30 fps (1-2 f at 60 fps).
- Text shimmer: duplicate text in an absolutely positioned span with `color: 'transparent'`, gradient (transparent
  0-34%, `rgba(255,255,255,0.8)` 50%, transparent 66-100%), `backgroundClip/WebkitBackgroundClip: 'text'`,
  backgroundSize 200-220%, animate backgroundPosition (a 60 f loop, or one 75 f pass).
- Code typing (`brand/Compose/CodeFrame.tsx`): each syntax token `opacity: frame < delay ? 0 : 1`, delays every 2 f
  (15 tokens/s), 18 px inline-block tab spans, `whiteSpace: 'pre'`, Fira Code; GitHub-dark palette `#F87683`
  keywords, `#B392F0` names, `#79B8FF` components and numbers, `#9ECBFF` strings.
- Code morph, magic move (`brand/Skills2CodeChange.tsx:136-567`): tokenize with ordered regexes; weighted LCS (score
  1 for punctuation and operators, `before.length + after.length` for identifiers and keywords so names travel instead
  of brackets); render both versions in hidden `<pre>` (visibility hidden, width max-content, whiteSpace pre) with
  `data-token-index` spans; measure once in `useLayoutEffect` under one `useDelayRender` handle, dividing by
  `rect.width / offsetWidth` to undo preview scale; then removed tokens explode, matched tokens glide with
  `Easing.spring({damping: 200})` and `interpolateColors` on the raw frame, added tokens fade in with
  `bezier(0, 0, 0.2, 1)` after the moves. The codehike variant (`brand/announcements/whats-new-in-remotion/
  CodeTransition.tsx`): `getStartingSnapshot` + `calculateTransitions`, moves over 7 f, new tokens fade over the next
  7 f, block height glides, per-token style written each frame as `perspective(1000px) translate(x, y)`.
- Golden-angle explosion (`brand/Skills2CrazyContext.tsx:54-98`): per item `angle = i * PI * (3 - sqrt(5))`, distance
  2400 px (+ `(i % 8) * 90` jitter), spin `(i % 2 ? -720 : 720)` deg, progress on `bezier(0.4, 0, 1, 1)` over 18-21 f,
  stepped on threes; use individual `translate`/`rotate` so measured layout stays valid.
- Typewriter with follow-scroll: word tokens `/\S+\s*/g` each showing `text.slice(0, visible - token.start)`; layout
  effect `scroll = max(0, content.scrollHeight - viewport.clientHeight)`; content `translate: 0px -scroll`.
- Stretch and warp glyphs (`example/ScalePath.tsx`, `example/WarpText/index.tsx`): opentype.js `font.getPath(text, 0,
  150, 72).toPathData(2)` -> `resetPath` -> `scalePath(path, 1, sy)` or `warpPath(path, ({x, y}) => ...)` (ripple
  `sin(y / 4 + frame / 20) * 5`, Gaussian bulge) -> `getBoundingBox` for the viewBox; load the font ONCE under
  delayRender (both team files reload it every frame).
- Fit text: `Math.min(80, fitText({text, withinWidth: 600, fontFamily, fontWeight: 'bold', textTransform:
  'uppercase'}).fontSize)`; `fitTextOnNLines` returns `{fontSize, lines}`, render each line with `whiteSpace: 'pre'`.
  Big-word auto size: `fontSize = min(230, 920 / max(longestWord * 0.72, 1))` (0.72 = Arial Black glyph ratio).
- Typography habits: display type with negative tracking about -4% of the size (-3.2 at 61 px, -5 at 112 px, -9 at
  156 px), eyebrows uppercase with wide tracking (4.4 at 20 px, 8 at 30 px), heavy but not black weights (720-780)
  for UI titles, Arial Black 900 for short-form, `fontVariantNumeric: 'tabular-nums'` for changing numbers,
  `textWrap: 'balance'` for captions, `paintOrder: 'stroke fill'` with `WebkitTextStroke` so the stroke sits under the
  fill, container queries (`containerType: 'size'`, `fontSize: '40cqmin'`) so one scene renders at 1920x1080 and at a
  540x280 thumbnail.

#### c. Captions (all from real videos)
- Data shape: Whisper-style tokens `{text: ' word', startMs, endMs, timestampMs: midpoint, confidence}`; pages from
  `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 800 | 1100})`.
- Page Sequences that never overlap: `from = round(startMs / 1000 * fps)`, `durationInFrames = max(1,
  min(round(next.startMs / 1000 * fps), ceil(end / 1000 * fps)) - from)`, `premountFor={fps}`,
  `showInTimeline={false}`.
- Moving highlight pill (`example/moving-pill-captions.element.tsx:200-256`): measure every word span (offsetLeft/Top/
  Width/Height) in `useLayoutEffect` + ResizeObserver after `waitUntilDone()` of the font; one pill behind the text at
  `interpolate(fractionalIndex, [0..n-1], measured)` for left/top/width; `fractionalIndex = sum over words of
  spring({config: {damping: 100}, durationInFrames: 5, delay: wordStartFrame - 2.5})` (glide centred on the word
  start); pill `#0b84f3` radius 10, padding 12, height fontSize + 24; Montserrat 700 white with `WebkitTextStroke:
  fontSize / 7 px #000` + `paintOrder: 'stroke fill'`; fontSize = min(80, fit page in 800, fit each word).
- Big stacked words (`jonny/disco-light-show/AnimatedCaptionsBigWords.tsx:25-113`): words stacked in a column, each
  appears at its start frame (1 f opacity) with scale 0.2 to 1 in 10 f on `Easing.spring({damping: 11, mass: 0.65,
  stiffness: 210})`; active word `#ff3b1f`, others white; uppercase Arial Black 900, lineHeight 0.86, letterSpacing
  -0.055 * size, stroke `max(3, size * 0.018)` px black, sticker shadow `drop-shadow(0 14px 0 rgba(0,0,0,0.96))
  drop-shadow(0 30px 34px rgba(0,0,0,0.5))`.
- Pop pages (`example/CaptionsTester/AnimatedCaptions.tsx`): page enters with `spring({damping: 14, mass: 0.55,
  stiffness: 180})` (translateY 50 to 0, scale 0.82 to 1 from `'center bottom'`), fades in its last 5 f; active word
  `#6cf6ff` with a thicker stroke; Arial Black 76 px, letterSpacing -3.5, lineHeight 1.05.
- Word focus lens (`jonny/components/AnimatedCaptions.tsx:87-364`): all words `#d9d9d9`, the active one
  `interpolateColors` to white; the whole caption block in an `HtmlInCanvas` with `glow({intensity: 0.6, color:
  'gray', radius: 100})`, `fisheye({fieldOfView: 1.5, radius: 3, center, zoom: 0.8})`, `radialProgressiveBlur({center,
  width, height, start: 0.5, endBlur: 5})` whose centre glides to the active word within at most 6 f (spring then
  `Easing.spring` again); word boxes measured with getBoundingClientRect.
- Sentence-aware pagination (`jonny/components/paginate-captions.ts`): split at sentence ends or `pageBreakAfter`;
  pages per sentence = max(ceil(text width / (952 * 1.6)), ceil(duration / 2500 ms)); dynamic programming over line
  fill (penalise fill < 0.58 or > 0.94, two-line imbalance), page timing, and awkward breaks (+3.5 after "the/to/and/
  my", +2 awkward first word, -4 after comma, colon or dash). Worth porting as is.
- TikTok rounded box (`example/Title/FitTextOnNLines.tsx:25-97`, `example/TikTokTextbox`): `measureText` per line (same
  font size as rendered) -> `createRoundedTextBox({textMeasurements, textAlign, horizontalPadding: 30, borderRadius:
  20})` -> white `<path d>` behind the lines.
- Active-token box: active word background `#0983F1`, white text, radius 5; inactive words keep a 1 px transparent
  border so layout never shifts; plus a 1 f "bump" (`spring(delay t) - spring(delay t + 1)`, durationInFrames 3,
  scale 1 + bump * 0.1).
- Caption-first vertical explainer (`jonny/how-can-remotion-be-free/HowCanRemotionBeFree.tsx`): 1080x360 caption band
  at y 780 always on; inserts placed above it; photo inserts get a bottom darkening gradient `linear-gradient(180deg,
  rgba(0,0,0,0) 38%, rgba(0,0,0,0.08) 51%, rgba(0,0,0,0.52) 82%, rgba(0,0,0,0.68) 100%)`.
- Text behind the subject (`jonny/disco-light-show/DragIn.tsx`, `TextBehindVideoStack.tsx`): background video (subject
  removed), HTML text, foreground subject matte as a transparent webm, stacked in that order; explain it with an
  exploded view (layers 366 px apart collapsing over 26 f).

#### d. Numbers, charts and data
- Glass bar chart (`example/BarChart.tsx`): bg `radial-gradient(circle at 75% 12%, #202758 0%, #101632 34%, #080D1F
  72%)`; breathing glow 520 px `rgba(115,91,255,0.18)` `blur(90px)`; glass panel radius 34 `linear-gradient(145deg,
  rgba(255,255,255,0.08), rgba(255,255,255,0.025))`, border `1px solid rgba(255,255,255,0.11)`, shadow `0 28px 80px
  rgba(0,0,0,0.28)`, `backdropFilter: blur(16px)`; bars radius `'22px 22px 9px 9px'`, `linear-gradient(180deg, color,
  color + 'B8')`, inset highlight `0 1px 0 rgba(255,255,255,0.38)`, the winning bar also `0 0 34px color + '66'`;
  palette `#58D6FF #7C83FF #C879FF #FF6DAE #FFB45F`; count-up `Math.round(interpolate(frame, [start, end], [0, value],
  sameEasing))` so number and bar always agree; every element an `Interactive.Div` with a name.
- Odometer drum (`promo/homepage/Demo/DigitWheel.tsx:18-179`): 10 faces on a 120 px radius cylinder, face i at
  `index = i / 10 + rotation`, `translateZ(cos(index * -2PI) * 120) translateY(sin(index * 2PI) * -120)
  rotateX(index * 2PI rad)` with an inner counter-rotation, `backfaceVisibility: hidden`, container `perspective:
  5000` and `maskImage: linear-gradient(to bottom, transparent 0%, #000 28%, #000 80%, transparent 100%)`; roll
  springs `{mass: 0.7, damping: 12}` fitted to 25 f; digit d sits on face 9 - d.
- Summed-spring state timeline (`DigitWheel.tsx:30-99`): N states, N-1 sequential springs, their sum is a continuous
  state position; key any property per state with `interpolate(position, [0..N-1], values)` (leading-zero fade, width
  collapse, minus sign). Rolling unit conversion: pad both numbers to equal digits, one wheel per column
  `digits={[a, b, a]}`, column delay `i * 4`, unit letter wheel at `columns * 4 - 2` (`TemperatureNumber.tsx`).
- Progress callouts (`example/ParseAndDownloadMedia/FrontFace.tsx:29-75`): fill width on `Easing.in(Easing.ease)`
  [150, 350]; each marker is a 3 px line growing with a 20 f damping-200 spring, then its code label fades over 10 f;
  delay = the frame at which the eased fill reaches the marker (invert the easing), so every label looks caused by the
  bar. Status text roll (`TopFace.tsx`): two absolutely positioned lines at `top: offset%` and `offset + 100%` in an
  overflow-hidden box, offset 0 to -100 on a 20 f spring at the frame the fill completes.
- Rounded progress bar (`brand/HomepageAssets/RenderProgress/make-rounded-progress.ts`): split the corner beziers with
  de Casteljau so the fill keeps rounded caps at every value (kappa 0.5523). Progress ring: `makeCircle({radius: 10})`
  track + `makePie({progress, closePath: false, radius: 10})` arc, stroke 4, round caps.
- Hand-drawn chart (`jonny/how-can-remotion-be-free/FirstCustomerChart.tsx`): wobbly cubic strokes doubled with a
  fainter echo stroke offset 6 px; draw-on via `pathLength={1} strokeDasharray={1} strokeDashoffset={interpolate(f,
  [a, b], [1, 0])}` (no length measuring); per month 12 f stagger (underline [d, d+8], echo [d+3, d+11], value
  [d+2, d+8], label [d+5, d+11]); bar grows by animating a `<clipPath><rect y height>` over a static hatched bar on
  expo-out (22 f); emphasis circle + arrow draw on after; handwriting font stack; organic circles with
  `borderRadius: '51% 44% 53% 46%'`; static per-item rotations `[-1.1, 0.45, -0.35, 0.8, -0.65]` deg.
- Heatmap bloom on a map (`example/SwitzerlandMap/Heatmap.tsx`): radius 12 to 42 and intensity 0.2 to 1.4 over 45 f
  ease-out cubic; opacity [0, 30, 120, 150] -> [0, 0.85, 0.85, 0].
- Compact counters for UI mockups: 999, 1.2k, 12k, 1.5M (`promo/prompts/prompt-helpers.ts:3-8`).

#### e. Transitions and loops
- Shader transitions: `<TransitionSeries.Transition presentation={crossZoom({})} timing={linearTiming({durationInFrames:
  30})} />` between full-bleed scenes (docs demos: A 60 f, transition 30 f, B 60 f); a label revealed with the
  `evolve()` effect (in 0.09 to 0.83 over f-2..15 with `bezier(0.25, 0.25, 0.6884, 1.375)`, out 0.83 to 0.06 over
  f35-44) (`brand/Showcase/HtmlInCanvasAllEffects.tsx`). `linearBlur({intensity: 0.18})`. zoomBlur with
  `springTiming({durationInFrames: 40})` or `linearTiming({durationInFrames: 40, easing: Easing.bezier(0.36, 0.53, 0,
  1)})`.
- Iris / shape reveal (`example/Transitions/CustomTransition.tsx:26-81`): custom presentation clips the ENTERING scene
  with an SVG `clipPath` built from `makeStar({innerRadius: R * p, outerRadius: 2R * p, points: 5})`, R = half the
  frame diagonal, centred with `getBoundingBox` + `translatePath`; any `@remotion/shapes` maker works (circle, heart).
  Custom timing with a pause: progress = `spring(default) / 2 + spring({damping: 200}, delay 10 + measureSpring(
  default)) / 2`, duration = both natural lengths + 10.
- Sound on every transition (`example/Transitions/AudioTransition.tsx:8-33`): wrap a presentation so its component
  renders `<Audio src={whoosh} />` only when `presentationDirection === 'entering'`, then the original component.
- Flash on a hard cut (`example/TransitionSeriesOverlay/index.tsx`): `TransitionSeries.Overlay durationInFrames={20}`
  with white `opacity: interpolate(f, [0, d / 2, d], [0, 1, 0])` peaking exactly on the cut; or two stacked
  `LightLeak` seeds at opacity 0.7 + whoosh at volume 0.1 over 15 f (whats-new chapter changes). Without
  TransitionSeries: a full-frame white `Solid` with opacity keys [0, 4, 8] -> [0, 1, 0] (4 f up linear, 4 f down
  ease-out).
- Keyframed push between overlapping layers (short-form, `jonny/disco-light-show/Composition.tsx`): outgoing translate
  to about -1080 px, incoming from +1080 px (and captions from +1080), all with the same keyframe spring over the same
  6-8 f; park the next scene partly off the right edge 30 f early as a teaser ("peek-in").
- Push-cut (`example/Transitions/PushCutDemo.tsx`): `pushCut({cutProgress: 5 / 11, transformOrigin: '50% 58%'})` +
  `linearTiming({durationInFrames: 11})`: outgoing punches to 1.04 (in-quad), hard cut at 5/11, incoming 1.04 to 1.07
  (out-quad), warm flash `#f5f2ed` at 0.2 for 2 f; lengthen the incoming Sequence by 5 f and wrap its content in
  `<Sequence from={5}>`.
- Zoom-through: scale the whole frame 1 to 10+ with an unclamped interpolate on a spring or with
  `bezier(0.8, 0.22, 0.96, 0.65)` (1 to 70 over 50 f at 60 fps) while the centre fades to black or the background mixes
  to the brand colour (`example/BetaText`, `example/ReactSvg/index.tsx`).
- Diagonal triangle wipe (`brand/TriangularEntrance.tsx:14-58`): SVG `clipPath clipPathUnits="objectBoundingBox"`, in =
  `M 0 0 L 2p 0 L 0 2p Z`, out = `M 1 1 L 1-2p 1 L 1 1-2p Z` with p = 1 - progress; nest in and out for a stinger
  (in on the house spring, out on `spring(frame - durationInFrames + 15, durationInFrames: 15)`).
- Seamless loop by Freeze crossfade (`brand/HomepageAssets/Master.tsx:63-94`): `<Sequence from={end - 44}
  durationInFrames={44} style={{opacity: eased}}><Freeze frame={0}><Scene/></Freeze></Sequence>` with the opacity
  ramping over 24 f on `bezier(0.645, 0.045, 0.355, 1)`; or `<AbsoluteFill from={775} durationInFrames={25} freeze={0}
  style={{opacity}}>` (MacBookScene).
- Seamless ping-pong loop (`brand/DesignSystems.tsx:11-49`, `brand/HomepageAssets/Studio.tsx`): play forward N frames,
  `pp = f < N ? f : 2N - 2 - f`, and end the composition at the first mirrored frame whose state equals frame 0.
- Other closed loops: orbit `rotation = frame / duration * 2PI` with flip windows at fractions of the loop
  (ExpertsGraphic, 60 s); conveyor by modulo with 3 cycle copies and per-item local frames `frame - i * 67`
  (RenderProgress); carousel push with a symmetric return (`brand/Applications.tsx`: keys [0, 85, 95, 167, 179],
  easing `[linear, SPRING, linear, SPRING]`, 1240 px = frame width + 160 px margin).
- Rotation loops: use `[0, durationInFrames]` as input range, not `[0, durationInFrames - 1]`, or the loop frame
  duplicates (`example/CenteredSolid.tsx:26`).

#### f. Camera moves
- Sub-canvas camera (short-form): `<Sequence width={1920} height={1080} style={{position: 'absolute', translate,
  scale}}>` inside 1080x1920; translate keys [0, 91, 103, 127, 136, 172] with `[linear, SPRING, linear, linear,
  linear]` (3 s drift, 12 f spring jump, hold, 9 f move back) and scale keys [91, 103, 127, 136, 172, 179] -> [0.73,
  1.297, 1.297, 1.35, 1.35, 0.684] perceptual (punch-in, creep, 7 f zoom-out).
- Spring reframe then endless drift (`brand/Skills2Router.tsx:25-69`): translate keys [27, 49, 125, 301] with easing
  `[keyframeSpring(allowTail), Easing.linear, Easing.linear]` and scale [27, 49] 1.71 to 1.29 perceptual: a 22 f
  settle, then 13-15 px of drift over 76-176 f so the frame never freezes (allowTail blends the spring tail into the
  drift).
- Dive into a device screen (`brand/WebMCPPromo/MacBookScene.tsx:185-323`, 60 fps): keys [21, 170, 591, 620]:
  translate to `'-862.3px -292.5px'`, scale 1.26 to 6.02 perceptual, rotate `'0deg'` to `'0.945221 -0.227695 0.233905
  45.778028deg'`, all with keyframe-spring easing arrays; peripheral `radialProgressiveBlur` endBlur [88, 161, 591,
  620] -> [0, 16, 16, 0]; slow push-in (149 f), long hold, fast pull-out (29 f); freeze the app clip while the camera
  moves, then cut to the live clip trimmed earlier.
- Zoom then pan without bounds math (`brand/announcements/.../WebRendererDemo.tsx`): scale 1 to 1.5 on a 30 f spring,
  then spring `transformOrigin` from `50% 50%` to `100% 0%`: the view slides to a corner and never reveals an edge.
- Opening zoom settle: 1.1 to 1 over 20 f `Easing.out(Easing.ease)`, or 1.2 to 1 over 30 f at 60 fps; photo settle
  1.035 to 1 over the insert.
- Ken Burns b-roll: scale 1 to 1.05 (video) or 1 to 1.15 + translateY 0 to -15% (image) linearly over the whole
  3-5 s shot from `'top center'`, 6 f fade envelope.
- Slow tilt drift on a static screen shot: animate the axis-angle rotate string linearly over the shot (-1.29 deg over
  53 f); keeps a still UI alive.
- Perceptual zoom always: `interpolate(frame, [a, b], [s0, s1], {output: 'perceptual-scale'})` (0 to 2 is 1.414 at
  half time instead of 1.0).
- Map "fly-to": zoom out (spring), pan centre (spring or ease-in-out cubic), zoom in (`bezier(0.65, 0, 0.35, 1)`),
  optional `bearing`/`pitch`; give the lon and lat different easings for a subtly curved path; the route line and the
  camera land on the same frame.

#### g. Screen recordings and UI demos
- The Studio close-up recipe (`brand/CloseUp1-8.tsx`, `brand/PitchCorrection.tsx`, `brand/RenderOnWeb.tsx`):
  recording at its native pixel size (for example 3214x1690) in a box of that size; framed with `translate` (region),
  `scale` (0.67-2.01) and a 3D axis-angle `rotate` whose axis is dominated by X (the screen leans back like a
  tabletop, 23-58.5 deg, about 28 deg typical) plus small Y/Z for a diagonal skew; `transformOrigin` on the action;
  NO `perspective` (orthographic keeps text legible); depth sold by a static progressive blur ellipse centred on the
  UI being used (`radialProgressiveBlur` endBlur 10-32, or `linearProgressiveBlur` endBlur 12-25 with the end point
  off-canvas to cap it); `<Solid color="#1f2427">` behind; trim with a negative `from`, retime with
  `playbackRate` (2.3x to fast-forward a long drag, 0.7x to slow a quick interaction). Blur glued to the UI when the
  transform is on the `HtmlInCanvas`; blur fixed in frame space (the canvas is the lens) when the transform is on an
  inner AbsoluteFill (a frame-sized canvas is also 2.5-4x cheaper than a capture-sized one).
- Recorded cursor: record without the OS cursor, re-draw a vector `MacOSCursor` at 2-7x (3-5 on retina captures) with
  `style: {position: 'absolute', left: 0, top: 0, translate: interpolate(frame, sampleFrames, ['Xpx Ypx', ...]),
  scale: pressTrack}`; press = step to exactly 0.9x with `Easing.step1` (clicks 5-9 f at 60 fps, drags 30-312 f), hero
  clicks sprung over 3-5 f; cursor type is a `step1` string timeline (auto, default, pointer, text, ew-resize,
  col-resize, row-resize, ns-resize, custom); always emit a duplicate "hold" sample before motion resumes (152 of 155
  gaps in the team data do; the rest creep); park the cursor far off-canvas when it leaves; read the frame inside the
  retimed container.
- Procedural cursor (`brand/ShipCard.tsx:91-427`, `brand/effects/*Showcase.tsx`): ordered waypoints `{x, y, frame}`;
  moves on `bezier(0.16, 1, 0.3, 1)`; arrive 8 f before a click and stay 8 f after, arrive 12 f before a drag; resize
  cursor shows 8 f before the drag starts (hover state); drags on `bezier(0.42, 0, 0.58, 1)` over 30 f (a slower 72 f
  drag for the payoff); click = scale 0.9 on [t-1, t+5]; fade in 0-12, fade out over the last 12 f; one eased value
  drives the cursor x, the number in the field (`toFixed(2)` or `Math.round`) AND the real effect parameter ("truthful
  mockup").
- Humanized straight-line path (`brand/WebMCPPromo2.tsx:13-58`): `x = lerp + sin(PI p) * A + sin(2PI p) * sin(PI p) *
  B` with p on `bezier(0.22, 0.75, 0.28, 1)` (arrival 19 f) or `bezier(0.32, 0.05, 0.3, 1)` (exit 43 f); tiny A and B
  (0.35-7 px at 3x cursor scale).
- Arc approach: quadratic Bezier `(1-t)^2 P0 + 2(1-t)t P1 + t^2 P2` with t on `Easing.out(Easing.cubic)` over 46 f and
  rotation -18 to 0 deg so the cursor lands; click squash [52, 54, 60] -> [1, 0.82, 1] (`brand/effects/
  FxIconComposition.tsx`).
- Fake drag and drop (`jonny/disco-light-show/ForkDrop.tsx`): cursor and card share `bezier(0.33, 0, 0.2, 1)` to the
  drop point; card lands with `Easing.out(Easing.back(1.8))` on scale and a -5 to 2 to 0 deg rotation settle; drop-zone
  highlight opacity [24, 31, 42, 54] -> [0, 1, 1, 0].
- Mock inspector micro-motion (`brand/effects/EffectShowcaseScaffold.tsx:224-269`): section expand 14 f expo-out
  (height rows * rowH * p, content translateY (1 - p) * -18, arrow rotate p * 90), toggle icon pop [s, s+5, s+12] ->
  [0, 1.35, 1], preview crossfade 14 f, row highlight white at 15% fading 10 f before and after, keyframe diamond by
  step. Panel palette `#1f2428` bg, `#13161b` borders, `#dfe2e6` text, `#0b84f3` accent, `#2f363d` inputs.
- UI window choreography (`brand/video-elements/StudioCodeHandoff.tsx`): windows in an overflow-hidden screen push each
  other: `interpolate(frame, [60, 100, 140, 180], [6, 679, 679, 6], {easing: [EXPO, Easing.linear, EXPO]})`, moves 40 f,
  holds 40-60 f; a widening window drives the app's responsive progress on the same curve.
- App mockups: build at a reference size and fit (`scale = min(W / refW, H / refH)`, CSS `scale` from `'0 0'` with
  radius / scale, or multiply every px by scale for crisp text); every part an `Interactive.Div` with a name; pixel
  nudges matched against screenshots; all panels tell the same fictional work session. Mac chrome dots `#ff5f57
  #febc2e #28c840`; checkerboard `conic-gradient(#d1d5db 25%, transparent 0 50%, #d1d5db 0 75%, transparent 0)` 32 px.
- Frozen live preview inside a mock editor (`brand/video-elements/Studio.tsx:800-870`): `<Sequence durationInFrames
  freeze={n} width={compW} height={compH}>` in a div scaled by `min((cw - 16) / compW, (ch - 15) / compH)`.
- True responsive reflow (`brand/DesignSystemsResponsive.tsx`): 380 screenshots at every 2 px of width, index =
  `round(progress * 379)` from a 30 f `{damping: 18, stiffness: 120}` spring, centred with `left: 50%` + `translate:
  -50% 0`.
- Chat/agent beat (`brand/HomepageAssets/CodingPrompt.tsx`): send button `interpolate(f, [12, 17, 28], [0, 1, 0])` ->
  scale 1 - 0.12p; prompt bubble rises 322 px and scales 0.86 to 1 from `'100% 100%'` over 16 f (keyframe spring);
  "Thinking" [42, 54, 119, 131] opacity + shimmer loop 60 f; streamed answer tokens 3 f apart.
- Screen recordings as cards in short-form: radius 60, `boxShadow: '0px 0px 50px rgba(255,255,255,0.5)'`, 0.5-2x
  speed, `trimBefore`.

#### h. 3D
- CSS/SVG "sticker 3D" (`brand/3DContext/*`, `example/3DContext/*`, `design/helpers/Outer.tsx`, svg-3d-engine): see
  3.5. Frame-driven versions: coin flip `RotateY radians={(1 - spring({fps, frame, delay: 30})) * PI}` (default
  bouncy spring, overshoot 29 deg past flat) inside `Scale factor={3.94}`, face swap at 90 deg by culling;
  spin-in `Scale(jumpIn) > RotateX(-0.3 to 0, 15 f later) > RotateY(2PI to 0)` with 40 f damping-200 springs
  (`example/3DSvgContent/SpinEffect.tsx`); fixed isometric tilts RotateY -0.3 to -0.4, RotateX -0.35 to -0.6, RotateZ
  -0.06 to -0.5 rad for cards; 3D product pill turning in from edge-on (90 deg to 28.6 deg over 115 f) and then
  drifting.
- Flip with content swap at 90 deg: angle 0 to 90 then -90 to 0 with `Easing.inOut(Easing.cubic)` over 48 f, swap
  content at the midpoint (ExpertsGraphic, `perspective: 1400`).
- three.js product shot (`example/ThreeScene/Phone.tsx`): one `spring({config: {damping: 200, mass: 3}})` (39 f)
  drives scale 0 to 1, a full Y spin (-PI to PI) and a rise, plus a constant 6 PI rotation over 20 s; rounded phone
  body from `ExtrudeGeometry` with concentric corner radii; screen at z = thickness + 0.001 (no z-fighting); video
  texture with `repeat = 1 / size` on ShapeGeometry UVs and `toneMapped={false}`.
- Procedural 3D idle: rotation from `time = frame / fps` (0.4-1.1 rad/s), breathing scale `interpolate(sin(frame /
  10), [-1, 1], [0.8, 1.2])`; rim-light look ambient 0.4 + directional 2.5 + blue point `#4f9dff` on `#0b1020`.
- CSS perspective scenes: `perspective: 800-1400` on the parent + individual properties (`rotate: 'x 30deg'`, `scale:
  '1 1 2'`, `transformOrigin: '50% 50% 10px'`).

#### i. Shapes, paths and logos
- Stroke-drawn wordmark (`brand/animated-logo/*`): all glyphs in one shared SVG (`viewBox 0 0 2100 800`), stroke
  `currentColor` 46 (theme = CSS color); draw with `strokeDasharray = L`, `strokeDashoffset = L - L * p` (`getLength`)
  or `evolvePath(p, d)`; `reversePath` flips direction; letters phased by sub-ranges of one spring (i stem [0, 0.8],
  dot [0.8, 1] dropping 100 px; e crossbar [0.5, 1]; m right arch [0.1, 1]); fly-in smear on `o` letters drawn as
  rects `rx 63` so width can stretch `+ interpolate(p, [0, 0.5, 1], [0, 300, 0])`; a central stagger table (springs at
  0, 15, 24, 30, 35; one letter starts at -5 so it is half done at frame 0); SVG masks with `maskType: 'alpha'` cut
  letter openings; wordmark complete at about f58 (so 60 f banners).
- Living logo (`brand/Brand/Logo.tsx`): reversed DEFAULT spring = anticipation bulge then collapse; regrow on a damping
  200 spring; then breathe forever `sin((f - start) / 10) * 0.1`; rings offset by 1 f; spiral exit with stacked easings
  (spring -> inOut(ease) -> out(ease)), `x = sin(rot) * r`, `y = cos(rot) * r * 0.7`.
- Shape morph without path interpolation (`brand/Brand/TriangleToSquare.tsx`): `Triangle edgeRoundness` 0.707 to 0.414,
  swap to `Rect` at progress 0.5 with edgeRoundness 0.5523 (circle kappa) to 0.69; colour by `interpolateColors` of
  pre-mixed colours. Path morphs: `interpolatePath(p, a, b)`, `makePolygon({points: 15})` to `makeCircle`; progressive
  trace `PathInternals.cutPath(d, getLength(d) * p)`.
- Draw-on without measuring: `pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p}`; marching dashes
  `strokeDasharray '28 28'` with an animated dashoffset; clipPath rect width wipe.
- Object riding a path with a comet tail (`example/ReactSvg/Arc.tsx`): `getPointAtLength` + `getTangentAtLength`,
  triangle (p + 6n, p + 60t, p - 6n), n = (t.y, -t.x); one-becomes-three orbits rotated 30/90/-30 deg by one progress;
  orbit dash loop `strokeDasharray: 0.2L 0.8L`, `strokeDashoffset = L * ((frame / (20 * fps)) % 1)`.
- Ellipse draw-on: perimeter `L = 2PI sqrt((rx^2 + ry^2) / 2)`, stroke width L / 60, round caps.
- Figma-style selection box: 4 square handles (gap 24, handle 40, stroke 5, `#0d99ff`) with `vectorEffect:
  'non-scaling-stroke'`. Scale an SVG element about a point: `translate(x y) scale(s) translate(-x -y)`.
- Squircle icon: cubic handles at 0.67 r (a circle is 0.5523 r); concentric squircles at opacity 0.15 / 0.3 / 1.
- Brand mark: three nested rounded triangles (11:9:7 sizes, opacity 0.2 / 0.4 / 1 or tints `#0B84F3 #BBDDFC
  #E7F3FE`), built in outer-to-inner order with a 10 f stagger and `{mass: 2, damping: 200}` (calm, heavy).

#### j. Effects, backgrounds and post-processing
- Effect stacks with real values (array order = processing order):
  - Paper background: `<Solid color="#f5fafb" effects={[burlap({size: 10, roughness: 0, color: '#e9e9e9'})]} />` (Skills
    2.0), or `#f5f0e6` + `paper({amount: 0.38, contrast: 0.18, roughness: 0.18, fiber: 0.28, crumples: 0.1, folds:
    0.12, seed: 24, scale: 0.8})` + `gridlines({gridSize: 54, lineWidth: 1.25, lineColor: 'rgba(76,101,128,0.16)'})` +
    `vignette({amount: 0.3, radius: 0.72, feather: 0.38, color: '#2b2118'})`; boil the grain by posterizing its seed
    (`seed: interpolate(frame, [0, 120], [0, 1000], {posterize: 30})`) or per cut (`paper({seed: pageIndex})`).
  - Footage unification: `effects={[dropShadow({}), tint({color: '#1ec8ff', amount: 0.06})]}` on stock hand videos.
  - Grade for a family of assets: `grayscale({})` + `colorCorrection({pivot: 0, shadows: 1, whites: 0.26, blacks: -1,
    temperature: -1})` on an `HtmlInCanvas` (ExploreRemotion homepage wrappers).
  - Tilt-shift screenshot: two `linearProgressiveBlur` toward opposite corners + `noise` + `vignette`, slow push-in 1.54
    to 1.711 on `bezier(0, 0, 0.58, 1)` (`brand/effects/NewsHeadline.tsx`).
  - Chroma key: `colorKey({similarity: 0.19, keyColor: '#6ed860', spillSuppression: 0.91, smoothness: 0.01})` then
    `translate({u: 0.14, v: 0.22})` then `hue({})` on a green-screen `Video`; `colorKey({similarity: 0.45, keyColor:
    '#ffffff'})` removes a logo's white background.
  - Logo glow: two stacked `dropShadow({color: '#ffffff', radius: 100, offsetX: 0, offsetY: 0, opacity: 1})`.
  - Procedural background: `Solid` + `rings({colors, center, thickness, gap})` + `wave({phase})` + `blur({radius: 20})` + `noise({amount: 0.25})` at 10% opacity over `#1e1c1c`, parameters slowed with `posterize: 10`; a disco video tiled
    with `pattern({scale: 0.34, gapX: -13})` + rotating `chromaticAberration({amount: 100, angle})`.
  - Sports slam (`brand/effects/Goal.tsx`): halves slide together unskewing (skewX -22 and +22 to 0, gap 480 to 0) in 15 f
    out-cubic; `metallicSwirl` alpha-mask fill; `fisheye` driven by `Easing.spring({damping: 10, stiffness: 269})`;
    canvas scale 1 to 0.67 on `Easing.spring({damping: 5, stiffness: 63})` (35% overshoot); perspective floor
    `gridlines({rotationX: -4, perspective: 23, offsetY})` + `evolve({direction: 'bottom', progress: 0.86})`.
  - Glitch pulses: `chromaticAberration` amount [34, 45, 76] -> [0, 17, 0]; audio-driven amount and seeds quantised
    to every 4 f (`seed: Math.round(frame / 4)`, 7.5 fps stutter).
- Turning an effect "on" smoothly: effects are per-frame pure passes, so stack copies with cumulative chains and
  crossfade (layer k opacity = product of 14 f crossfades) (`brand/effects/StarburstEffectShowcase.tsx:979-1066`).
- CRT power-off outro (`jonny/disco-light-show/MasterWithEffect.tsx`): the whole master in an `HtmlInCanvas`; in the
  last 45 f ramp `scanlines` (amount to 0.58, spacing 5, thickness 2, offset frame * 3), `chromaticAberration` (to 34,
  times `0.35 + |sin(frame * 2.7)| * 0.65` flicker, angle flipping every 2 f) and `noise` (to 0.36, seed = frame); add a
  horizontal shake `sin(frame * 5.3) * 0..12 px`; collapse `scale` y to 0.012 in 5 f then x to 0 in 4 f; flash a
  radial white line; black for the final 20 f.
- CRT shader over live DOM (`example/HtmlInCanvas/compose-webgl-crt.tsx`): barrel `uv2 += uv2 * (abs(uv2.yx) /
  vec2(6, 4))^2`, chromatic offset 0.0015, scanlines `mix(0.85, 1.0, sin(uv.y * resY * 1.5 + t * 8) * 0.5 + 0.5)`,
  phosphor mask by `gl_FragCoord.x mod 3`, rolling bar, vignette `pow(uv.x (1 - uv.y) uv.y (1 - uv.x) * 18, 0.25)`,
  noise 0.04, `t = frame / fps`.
- Custom effects: 2D posterize and palette-map templates (`example/EffectsTestbed/sample-posterize-2d.ts`,
  `palette-map.ts`), WebGL2 RGB shift (`sample-rgb-shift-webgl.ts`: red sampled at +offset, blue at -offset), and the
  complete metallic swirl flow-field shader (`brand/effects/metallic-swirl-effect.ts`: schema, validation,
  `calculateKey`, `setup/apply/cleanup`, premultiplied alpha, blend vs alpha-mask modes, time = frame / fps).
- Motion blur: `HtmlInCanvasMotionBlur shutterAngle={360} samples={24}` over a 1700 px slide in 18 f (quint-out) is the
  team's title slam (4.0.529 only; on 4.0.528 use `CameraMotionBlur {samples, shutterAngle}` which multiplies render
  cost by the sample count).
- Heavy zoom-blur-in grid (`brand/Showcase/index.tsx`): scale 2 to 1, CSS blur 10 to 0 px, opacity 0 to 1 per element
  about its own centre (`transformBox: 'fill-box'`) on `{mass: 20, damping: 500}` springs.
- Frosted glass: `backdropFilter: blur(16px)` on a gradient panel; `blur(200px)` + white 50% for a frosted sheet.

#### k. Audio: sound design and audio-reactive visuals
- SFX timing: start the sound on the frame of the visual event (one `<Audio from={appearFrame}>` per list row at
  volume 0.8, chime at 0.05, whoosh at 0.1 under light leaks, prompt SFX at frame 0 of the insert); a showcase gives each
  sound its own `Series.Sequence` of `max(45, soundLength)` frames with a 64-bar waveform (from `getWaveformPortion`)
  that fills as the sound plays (bar i lit when progress >= (i + 1) / 64).
- Volume envelopes are callbacks in media time: `volume={(f) => interpolate(f, [0, 50, 100], [0, 1, 0], clamp)}`;
  fades `[0, 500] -> [1, 0]`; tremolo `(Math.sin(f / 4) + 1) / 2`; alternate music and dialogue by computing `muted`
  per frame from ranges.
- Bin mappings that work (`example/AudioVisualization/index.tsx`, 32 bins): bin 1 (bass) -> orb scale `1 +
  interpolate(v, [0.14, 1], [0, 0.6])` (0.14 = noise gate); bin 10 -> RGB-split distance 0-30 px; bin 31 (treble) ->
  background zoom; bins 4-31 (even, mirrored) -> a ring of 28 dots at radius `(300 + ln(avg3 * 600) * 6)` (average
  each bin with its neighbours; guard log(0)). With 128 bins: bass = mean(0-31) -> chromatic amount x400 and dissolve
  x7, highs = mean(96-127) -> angle (`brand/LogoHorn`).
- Chromatic RGB-split text: 3 tinted copies `rgba(255,0,0,0.3)`, `rgba(0,255,0,0.3)`, `rgba(0,0,255,0.3)` with 2 px blur
  offset by (-d, 2d), (3d, 3d), (-3d, 0) plus the real text at (0, d).
- Mirrored spectrum element (`example/mirrored-spectrum.element.tsx:67-126`): `useWindowedAudioData({windowInSeconds:
  10})`, `visualizeAudio({numberOfSamples: 256, optimizeFor: 'speed'})`, take ceil(bars / 2) bins and mirror
  `[...subset.slice(bars % 2).reverse(), ...subset]` so bass sits in the middle, height `max(4, min(300, 300 *
  sqrt(v) * 1.5))`, 65 bars, gap 8, radius 999.
- Oscilloscope (`example/oscilloscope.element.tsx:89-150`): `getWaveformPortion({numberOfSamples: 64, outputRange:
  'minus-one-to-one', normalize: false, durationInSeconds: 0.35, startTimeInSeconds: frame / fps - 0.175})` (window
  centred on the playhead) -> `createSmoothSvgPath` stroke `#55e6ff` width 6.
- Calm voice waveform: `visualizeAudioWaveform({windowInSeconds: 0.1, channel: 0})` posterized to every 3 f ->
  `createSmoothSvgPath`, stroke 10 round caps.
- Studio-accurate waveform (timeline-utils): peak = max |sample| per 10 ms, bars at 80% height, clipping in `#FF7F50`.
- Beat-locked re-randomisation: `iteration = floor(frame / 15)` (15 f = 120 BPM at 30 fps), seeds
  `random('x-' + i + '-' + iteration)`, linear drift inside the beat; rare big items via `interpolate(r, [0, 0.9,
  0.901, 1], [40, 40, 160, 160])`.
- Beat drop: a drum video at `playbackRate={0.8}` right after a countdown; countdown pages 20 f (scale 1.35 to 0.45
  expo-out perceptual, 3 f ease-in fade).
- Generated tones: `OfflineAudioContext` sine -> `audioBufferToDataUrl` -> `<Html5Audio src>`.

#### l. Video editing
- Jump cuts with one element (`example/JumpCuts.tsx:31-83`): sections `{trimBefore, trimAfter}`; per frame walk the
  sections summing lengths, the active one gives `trimBefore = section.trimAfter - summed`; keep ONE `OffthreadVideo`
  mounted; on the first frame of a section pass `acceptableTimeShiftInSeconds={0.000001}` to force an exact seek;
  append `#t=0,` to the src to stop the automatic media fragment; `calculateMetadata` sums the sections.
- NLE-style edit of one recording (`brand/WebMCPPromo2.tsx:67-96`): three `<Video>` with the same src: A `from={-31}
  durationInFrames={303}`, B `from={247} durationInFrames={135} trimBefore={530} freeze={36}` (a 2.25 s freeze of a
  result), C `from={380} durationInFrames={735} trimBefore={598}`; all `premountFor={30}`; later clips overlap earlier
  ones by 2-25 f so no gap frame appears.
- Speed ramp (`example/DifferentSegmentsAtDifferentSpeeds.tsx`): segments `{sourceLength, speed}` -> `Series.Sequence
  durationInFrames={sourceLength / speed}` holding `<Video trimBefore={sourceSoFar} playbackRate={speed}>`, total
  `Math.ceil(...)`, `premountFor={Math.round(1.5 * fps)}`. Container retime: `<AbsoluteFill playbackRate={2.3}>`.
- Freeze inserts with ripple (`example/FreezePortion/FreezePortion.tsx`): holds `{frame, durationInFrames}`; during a
  hold `<Freeze active frame={hold.frame}>`, otherwise shift the child Sequence `from` by the sum of previous holds.
  Variants: `<Freeze active={(f) => f >= 30} frame={30}>` (play then hold), `<Sequence freeze={20}>`.
- Talking head trimmed to speech (`brand/announcements/whats-new-in-remotion/Composition.tsx`): a SILENCES table
  `{leadingEnd, trailingStart}` per take (from ffmpeg silencedetect with a per-video loudness threshold); `<Video
  trimBefore={floor(leadingEnd * fps)} trimAfter={ceil(trailingStart * fps)}>`; `calculateMetadata` sums the same
  numbers, so timeline and trims never drift. B-roll = full-frame Sequence over the presenter (presenter audio
  continues, b-roll muted), 3-5 s, 6 f fades, slow Ken Burns; screen recordings at 2-3x.
- Side panel with presenter push (`SlideInOverlay.tsx:26-96`): `progress = in(out-cubic, 1 s) - out(in-cubic, 1 s)`;
  panel `left: 60%; width: 40%; translateX(interpolate(progress, [0, 1], [102, 0]) + '%')`; presenter
  `translateX(interpolate(progress, [0, 1], [0, -20]) + '%')` so the face stays in the free 60%; two panels ->
  `Math.max(p1, p2)`; content swap inside a persistent panel with sequential 8 f crossfades.
- Vertical reframe of landscape footage: native 1920x1080 box, `translate: '-420px 420px'` centres it in 1080x1920,
  `scale` 1.778 fills the height (1.8-2.0 in practice); or `objectFit: 'cover'` + `objectPosition` from crop fractions
  (`x = cropLeft / (cropLeft + cropRight) * 100`); or place the clip in the top half (`height: '50%'`) and keep the
  bottom for captions.
- Loops: `<Video trimBefore={197} trimAfter={268} loop>` loops a sub-range (trimAfter exclusive); render-safe
  OffthreadVideo loop = measure duration under delayRender, then `<Loop durationInFrames={floor(d * fps)}>`.
- Retimed clocks, the exact math (`example/SequencePlaybackRateLoops.tsx:88-93`): per level `local = (parentLocal -
  from) * rate + trimBefore`, a Video's own rate multiplies, and with `loop` the source frame is `trimBefore + ((local -
  videoFrom) * videoRate) % (trimAfter - trimBefore)`.
- Lottie re-timing by markers (`example/Lottie/ExplodingBird`): loop a segment with `<Loop times>`, then play the next
  marker range in `<Sequence from={segStart} durationInFrames={segLen}><Sequence from={-markerFrame / speed}><Lottie
  playbackRate={speed}>` (2x, 0.1x slow motion, 0.8x). Align a Lottie loop to a fixed composition loop with
  `playbackRate = Math.round(ratio) / ratio`, `ratio = compSeconds / lottieSeconds`.

#### m. Maps (`@remotion/maptiler`, see 3.3)
- Country highlight: `MapRegion` with a Natural Earth polygon, `progress` draws the outline (50 f ease-out cubic), `fill`
  pops to 0.3 and settles at 0.24, `glow` springs in; `fillColor '#1e46d5'` + `strokeColor '#8f1712'` or `'#ed2939'` +
  `'#981b27'`, strokeWidth 4.
- Route: `MapPolyline` `lineColor '#ff6700'`, `lineWidth 8`, white halo (`outline`, `outlineColor '#ffffff'`,
  `outlineOpacity 0.7`, `outlineWidth 7`, `outlineBlur 8`), `progress` synced to the camera pan; `bearing` so the route
  runs across the frame.
- Pins: `MapOverlay` + wrapper `translate: '-50% -100%'` so the tip is on the coordinate; pop scale [0, 9] with
  `Easing.spring({damping: 6, stiffness: 37, allowTail: true})` perceptual, swing rotate `'-116deg'` to `'0deg'` over
  21 f about `transformOrigin: '50% 100%'`, then shrink to 0.57 later; round photo with a 34 px white border in a blue
  teardrop.
- Clean base map: `showLabels={false}`, `administrativeBorders="none" | "country-only"`.

#### n. Hand-drawn and sketch explainer style (`jonny/how-can-remotion-be-free/*`)
- No springs: entrances expo-out, fades 5-9 f linear, strokes drawn linearly in 8-14 f, a 34 px rise in 12 f for the
  container; small static rotations per item; strokes doubled with a faint echo; organic circles; handwriting font
  stack "Noteworthy, 'Bradley Hand', 'Marker Felt', 'Comic Sans MS', cursive" (macOS fonts: bundle a real handwriting
  font for Linux renders); palette on `#161616`: cream `#f5f0dc`, labels `#c9c2ad`, blue `#6f98df`, accent `#ff674f`/
  `#ff563d`, bar fill `rgba(255,86,61,0.22)`.
- Fly-through prop over a photo: three keys (off-screen bottom-left, centre and largest at 1.06, off-screen top-right)
  with rotation continuing one way (-18 to 8 to 30 deg) and `bezier(0.22, 0.72, 0.24, 1)` per segment (it "presents
  itself" mid-frame), `drop-shadow(0 28px 24px rgba(0,0,0,0.46))`.
- Tier joke: the same logo drawn with 3/4/5 concentric outlines, rows 5 f apart, rings 2 f apart inside-out,
  `vectorEffect: 'non-scaling-stroke'`.

#### o. Colour and brand tokens seen
- Remotion: blue `#0b84f3` (darker `#0a77db #0970cf #085caa`, lighter `#2290f5 #2f96f6 #53a9f7`, older `#4290f5`),
  reds `#F43B00 #f02c00 #ff3232`, GT Planar 400/500/700/900 with `fontFeatureSettings: "'ss03' 1"`, neo-brutalist
  borders (2 px black + 4 px bottom border), flat offset shadows `'0 10px 0 rgba(5,5,5,0.08)'`, light bg `#f8fafc`,
  dark `#18191a`.
- Studio dark UI: `#1f2428` / `#1f2427` bg, `#181818`, `#2f363d` inputs, `#A6A7A9` text, `#15181B` timeline,
  `#0d69bd` sequence track, `#f02c00` playhead. VS Code dark `#131414` editor, `#181919` chrome. Codex dark `#171717`.
  Terminal box `#292C34`. Claude orange `#D47556` / `#E08468` / `#D97757`.
- Dark data dashboards: navy radial background + glass panels + pastel neon palette with hex-alpha tints (`B8`, `66`).
- Title-card palette (GSAP showcase): bg `#090A0F`, text `#F7F7F2`, lime `#B8FF5A`, violet `#7C5CFF`, pink `#FF5F8F`.
- Editorial scene: `#17122b` / `#082734` bg, `#f8f7f4` text, accent `#ffb35c` or `#7df6d0`, eyebrow 30 px 700
  letterSpacing 8, title 156 px 900 letterSpacing -9 lineHeight 0.9, a 620 px accent ring half off-frame.
- Colour mixing instead of opacity for overlapping shapes: `interpolateColors(p, [0, 1], [mix(bg, brand, a), mix(bg,
  red, a)])` (polished `mix`).

## 5. Performance and render stability

Determinism (what breaks parallel rendering, and the team's fixes)
- Only frame math drives pixels. No `Math.random()` (use `random('seed-' + i)`; `random(null)` only for SVG/DOM ids),
  no `Date.now()`/`performance.now()` values in visuals, no CSS transitions or keyframe animations, no
  `requestAnimationFrame` (the website's rAF tweens and the `@remotion/design` Spinner are UI-only), no R3F
  `useFrame` delta or clock, no drei materials that animate from their own clock (safe only in stills), no
  `map.flyTo`/`easeTo` (MapLibre timers), no state-based loops.
- Shaders and custom effects get `time = frame / fps` as a uniform; effect seeds are frame-derived
  (`noise({seed: frame})`, `seed: Math.round(frame / 4)`).
- Imperative renderers hold every frame until they are done: MapViewport (`delayRender` + `map.once('idle')` +
  `jumpTo` + `triggerRepaint()`, cleanup releases), ThreeCanvas (per-frame delayRender released after
  `advance()`; WebGPU also waits for `device.queue.onSubmittedWorkDone()`), async `HtmlInCanvas` `onPaint` (the frame
  waits for the promise), Suspense loaders (fallback holds a delayRender).
- Idempotent handles: `const [handle] = useState(() => delayRender('label'))` (one per mount), release once through a
  ref guard (safe under StrictMode double effects), `cancelRender(err)` on failure (or only when `isRendering`, so a
  failed fetch does not break the preview). Old style `useState(delayRender)` with globals still appears.
- Data and measurement: fetch data in `calculateMetadata` (duration, size, props) instead of in the component; measure
  DOM once in `useLayoutEffect` under a delayRender handle (code morph, pill captions) and divide by
  `rect.width / offsetWidth` to undo preview scaling; store measured regions with a deep-equality guard to avoid
  layout-effect loops.
- Fonts: `loadFont(...)` from `@remotion/fonts` or `@remotion/google-fonts` at module scope; before measuring text,
  `await waitUntilDone()` and use `validateFontIsLoaded: true`; never load fonts in `useEffect([frame])` (two team
  files do and can render blank frames); system fonts (macOS handwriting fonts) are machine dependent.
- Media: `premountFor` 30 f (0.5 s at 60 fps, 1 s at 30 fps) on every clip that starts after frame 0, `fps` for caption
  pages, `1.5 * fps` for OffthreadVideo cuts; one mounted video for jump cuts with forced exact seeks only at cut
  frames; `prefetch()` alternatives; `pauseWhenBuffering`/`pauseWhenLoading` for preview smoothness; local-first
  assets via `getStaticFiles()` with a CDN fallback; `crossOrigin="anonymous"` for anything drawn into a canvas.
- Fractions: fractional `from`, `durationInFrames`, `delay` and keyframes are accepted, but keep `TransitionSeries`
  durations integer (issue 4922: `3.000002` showed two scenes at once) and remember a half-frame keyframe never
  renders at integer frames.

Cost
- `HtmlInCanvas` costs pixels: canvases at capture size were 5.0 to 8.4 MP with a WebGL blur per frame; a frame-sized
  canvas with transformed content inside is 2.5-4x cheaper; `pixelDensity` multiplies cost by its square; nesting is not
  supported; WebGL effects in renders need a GPU-capable environment (`--gl=angle`); Studio preview needs Chrome 149+
  with the canvas-draw-element flag.
- Effects render even at opacity 0: mount stacked effect layers only while visible. Custom 2D effects loop over every
  pixel in JS (2 M pixels at 1080p): prefer WebGL2 for production; `calculateKey` lets identical params reuse output.
- Motion blur multiplies render cost by its sample count (`CameraMotionBlur samples 5` = about 5x).
- Inline keyframe arrays of hundreds of CSS strings are re-parsed on every call (about 5,400 string parses per frame
  in Skills2Gesture): hoist to module constants or prefer numeric tracks for machine-generated data.
- svg-3d-engine subdivides outlines 3 times (8 ribbons per segment, about 64 paths for a rounded rect); geometry is
  rebuilt every frame in the SVG-3D homepage assets (12 extruded buttons with glyph paths per frame): memoize the
  untransformed geometry when scenes get complex.
- Audio visuals: `useWindowedAudioData` (10-30 s windows) + `visualizeAudio({optimizeFor: 'speed'})` instead of loading
  whole files; waveform peaks decoded once in a shared worker and cached.
- `lazyComponent` per composition keeps the Studio bundle small (50 comps in the example Root).
- 10 fps compositions render a third of the frames; `posterize: 3` at 30 fps looks the same but renders every frame.
- Moving maps are network-bound (each frame waits for tiles); premount maps.
- Lambda payload limit 256 KB for input plus resolved props (example Root comment): compress one or pass URLs.
- Screen-recording and Player tips from the website code: alpha WebM for Chromium/Firefox + MP4 for Safari; stock
  footage for smooth multi-video playback prepared as 1080p H.264 High, 30 fps, about 5 Mbps, 60-frame GOP,
  faststart, no audio.

## 6. Errors and fixes

| Symptom or trap (where seen) | Cause | Fix |
|---|---|---|
| Spring with `damping: 200` feels exactly like `damping: 20`; raising damping does not slow it (everywhere) | solver treats every zeta >= 1 as critically damped | change `durationInFrames`, `mass` or `stiffness` |
| Springs run slow in a 10 fps composition | solver caps each step at 64 ms (below 15.6 fps) | expect about 1.56x longer at 10 fps or use `durationInFrames` |
| "Non-numeric strings can only be interpolated using Easing.step1" (cursor types, `'auto'`) | discrete strings need step easing on EVERY segment | `easing: keys.slice(1).map(() => Easing.step1)` or `easing: Easing.step1` |
| "When easing is an array, it must have one entry per segment" | array length != keys - 1 | one easing per gap |
| Cursor or layer creeps during a pause (brand close-ups) | linear interpolation across a gap without a hold sample | duplicate the sample on the frame before motion resumes, or step easing |
| Overlay out of sync after retiming a container (brand/RenderOnWeb.tsx) | keys computed on the parent clock | read `useCurrentFrame()` inside the retimed container (brand/PitchCorrection.tsx) |
| Cursor type 164 f late (brand/CloseUp5.tsx) | one track keyed on `frame`, others on `captureFrame` | one time base per layer |
| Last keyframes never show in a slowed Sequence (example/SequencePlaybackRateKeyframes.tsx) | `durationInFrames` is in parent frames | extend the duration by 1 / rate |
| Frame captured in a parent not retimed by the child's `playbackRate` | JSX nesting does not change a captured variable | animate inside a child component |
| End card animation already finished when it appears (brand whats-new EndCard) | keyed to absolute frames 56-86, panel shows at 502 | wrap in `<Sequence from={502}>` so its clock starts on appearance |
| Blank first frames (example/ScalePath.tsx, WarpText, brand Compose/Captions, CodeBRoll) | async font/JSON/highlighting in `useEffect` without delayRender | delayRender in a useState initializer or do it in calculateMetadata |
| Loop has a duplicate frame (example/CenteredSolid.tsx) | rotation `[0, 59] -> [360, 0]` over 60 f | input `[0, durationInFrames]` |
| Rotation keeps spinning, opacity exceeds 1 (example/EffectKeyframeE2e.tsx) | default extrapolation is `'extend'` | clamp both sides unless you want to keep accelerating |
| Scale goes negative late in a comp (brand NpmInitVideo) | `1.8 - frame / 300` crosses zero | clamp or interpolate with bounds |
| Caption highlight wrong at other fps (brand Compose/Captions.tsx) | hard-coded 30 instead of `fps` | always derive from `useVideoConfig().fps` |
| Two scenes visible at once in a TransitionSeries (issue 4922) | fractional durations | integer durations |
| Remotion adds a media fragment you did not want (JumpCuts) | automatic `#t=` from trim props | append `#t=0,` to the src |
| `Math.log(0)` = -Infinity in audio visuals | silent bins | floor the value before `Math.log` |
| Lottie loop does not align (promo Demo) | `playbackRate = ratio / ratio` (missing `Math.round`) | `Math.round(ratio) / ratio` |
| Shader transition factory throws (example HtmlInCanvas docs) | most need an options object | call `x({})` (`blurSlide()` excepted) |
| WebGL2 missing while rendering | headless GL backend | render with `--gl=angle` |
| No blur/effects in Studio preview (close-ups) | HtmlInCanvas needs Chrome 149+ flag in preview | renders are fine; enable the flag to preview |
| `makeMatrix3dTransform` breaks when you append transforms | returned string lacks the closing ')' (4.0.528 and 4.0.529) | append ')' in your own helper |
| `<ThreeCanvas>` throws "The "width" prop ... must be ..." | width/height must be positive integers | round computed sizes |
| `useOffthreadVideoTexture` throws in preview | render-only (deprecated) | branch on `useRemotionEnvironment().isRendering` or use `@remotion/media` `onVideoFrame` + CanvasTexture |
| three.js video texture one frame stale in renders (example/VideoTexture.tsx) | async frame extraction after the canvas advanced | call `advance(performance.now())` again inside `onVideoFrame` |
| drei `<Html>` content cannot read the frame | separate React root | wrap in `Internals.RemotionContextProvider` with `useRemotionContexts()` |
| WebGPU capture shows unfinished frame | `compileAsync` alone does not prepare bindings | one real `renderAsync` warm-up + queue wait (as `@remotion/three/webgpu` does) |
| Map renders show fading labels or mid-animation tiles | MapLibre internal animations | `fadeDuration: 0`, `jumpTo`, paint transitions 0, wait for `idle` (MapViewport does this) |
| Measured text wrong (TikTok box) | measured and rendered at different font sizes/paddings | same `fontSize`, `fontFamily`, padding in both |
| Font silently missing in render | family name mismatch ('GT Planar' vs 'GTPlanar'), class typo `fontbrand` | load and reference one exact family string |
| `perceptual-scale` on a translate string (Studio copy artefact) | option meant for scale | use it only for scale |
| Throwing or circular props in `calculateMetadata` break `getCompositions()` | metadata must be serialisable | return plain data; handle fetch errors with fallbacks |
| Class instances in props arrive as plain objects | props are serialised (even in Studio) | pass plain data; Dates and `staticFile()` paths survive |
| Error "Cannot use frame 500: Duration of composition is 300, therefore the highest frame that can be rendered is 299" | frame range beyond duration | clamp requested frames |
| Easing domain surprises when extrapolating | `Easing.circle`, `bounce`, `bezier` clamp t to [0, 1]; `linear`, `quad`, `cubic` extend | clamp interpolate or choose a curve that extends |
| Commercial icon paths copied into code (a Font Awesome Pro path in LicenseQuestionsGraphic.tsx) | licensing | draw our own or use MIT/CC icons |

## 7. What our skills must teach

Authoring style (default for 4.0.528)
- Write Studio-editable code: animate CSS individual properties (`translate`, `scale`, `rotate`, `opacity`,
  `transformOrigin`) directly in the `style` of a `Sequence`, `AbsoluteFill`, `Interactive.*` or media element; one
  `interpolate(frame, keys, values, {easing: [...], extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})` per
  property with literal arrays; `output: 'perceptual-scale'` on every scale; name every element; put `from`,
  `durationInFrames`, `trimBefore`, `freeze`, `premountFor`, `playbackRate` on the element itself; wrap reusable pieces
  with `Interactive.withSchema`. Avoid animated `transform` strings and animated `top/left` (not editable, and they
  compose badly with Studio edits); `transform` is fine for code-only 3D math.
- Read the frame once at the top of the component that owns the animation; pass remapped frames (ping-pong, freeze,
  speed) to children as props when the remap must reach them.
- Scenes own their timing: export `SCENE_DURATION_IN_FRAMES`, derive beat constants from each other, register each
  scene as its own composition inside a `Folder`, reuse the scene component in the master.

Timing defaults (decision table)
| need | default | alternatives |
|---|---|---|
| plain entrance (no bounce) | `spring({frame: frame - start, fps, config: {damping: 200}})` = 23 f at 30 fps | `durationInFrames: 10-20` to tighten; `{mass: 2}` (32 f) or `{mass: 3}` (39 f) for weight |
| keyframed move (Studio style) | `Easing.spring({damping: 200, mass: 1, stiffness: 100, allowTail: true, durationRestThreshold: 0.02, overshootClamping: false})` in the easing array | `Easing.bezier(0.16, 1, 0.3, 1)` for UI and text |
| text or UI element entrance | 15-21 f `Easing.bezier(0.16, 1, 0.3, 1)` with opacity + 12-80 px rise | letters 12 f each, 2 f stagger, under a clip |
| exit | 60-80% of the entrance length, accelerating (`bezier(0.4, 0, 1, 1)`, `Easing.in(Easing.cubic)`, expo-in `(0.7, 0, 0.84, 0)`) | exit spring on the last 15-20 f (`frame - durationInFrames + 15`) |
| camera pan/zoom | ease-in-out cubic `bezier(0.65, 0, 0.35, 1)` over 40-72 f, or the keyframe spring over 22-45 f | slow push over the whole shot (linear, perceptual) |
| UI drag or value scrub | `bezier(0.42, 0, 0.58, 1)` over 30 f; the same value drives cursor, text and effect | 72 f for the payoff drag |
| accent pop / bounce | ONE per element: default spring (16%), `{damping: 15}` (3%), `{mass: 0.5}` (4%), `Easing.spring({damping: 11, mass: 0.65, stiffness: 210})` in 10 f (20%) | pin pop `{damping: 6, stiffness: 37}` in 9 f + swing |
| stop-motion / handmade | `posterize: 3` (10 updates/s) on the driver interpolate | `Math.floor(frame / 3) * 3`; cursor blink periods divisible by 3 |
| stagger | letters 1-2 f, tokens 2-3 f, digit columns 4 f, cards/bars 8 f, list rows 10 f, pins 12 f | two levels `row * 5 + item * 2`; bottom-up rows |
| short-form scene change | keyframed push 6-8 f (spring) | white flash 8-14 f; pushCut 11 f; LightLeak overlay 15 f |
| long-form scene change | hard cut; `TransitionSeries.Overlay` flash on chapter changes | shader transition 24-30 f linear timing |
| loop | end on the frame-0 state: Freeze crossfade 24 f, ping-pong, or `frame / duration * 2PI` | never rely on state |
- Speed never comes from damping above critical (20 at defaults): use `durationInFrames`, `mass`, `stiffness`.
- Overlap beats by 2-4 f; leave a 5 f breath between phases; settle the main content by about 55% of the piece and
  hold; let the frame never freeze completely in long holds (slow drift, breathing glow, noise float).
- Time from seconds: `Math.round(seconds * fps)`; keep fps-independent code (`round(0.15 * fps)` for 150 ms cycles);
  choose 30 fps for motion graphics and social, 60 fps for screen recordings and UI demos.

Structure checklist
- [ ] Composition id, size, fps, duration registered in a Folder; duration constant exported by the scene.
- [ ] `calculateMetadata` for data-driven length/size/props (sum of trims, media length, manifest pages), with a
      fallback; alpha overlays default to ProRes 4444 `yuva444p10le` + PNG frames; even dimensions.
- [ ] Cut strategy chosen: TransitionSeries (overlapping transitions), Series (hard-cut montage), flat layers with
      keyframed pushes (short-form).
- [ ] `premountFor` on every media element that starts after 0; `name` on everything; internal wrappers hidden from the
      timeline.
- [ ] Captions: token data in the Caption shape; pages as non-overlapping Sequences with `premountFor={fps}`.
- [ ] Clock check: animations read the frame inside the retimed container; durations of slowed Sequences extended.

Render-stability checklist
- [ ] No `Math.random`, `Date.now`, rAF, CSS animations/transitions, R3F clock, map `flyTo`.
- [ ] Every async (fonts, JSON, highlighting, DOM measuring, media metadata, WebGL setup) is under a delayRender
      handle created once, released once, with `cancelRender` on error; or moved to `calculateMetadata`.
- [ ] Fonts loaded at module scope and awaited before `measureText`/`fitText`.
- [ ] Canvas-drawn assets are CORS-enabled; HtmlInCanvas renders use `--gl=angle` when WebGL is involved.
- [ ] Integer `TransitionSeries` durations and ThreeCanvas sizes; clamp interpolations unless extension is intended.
- [ ] Heavy per-frame work memoized (keyframe arrays, extruded geometry, parsed paths); effect layers mounted only while
      visible.

Version gates for 4.0.528 (tell the agent what exists)
- Safe: every `interpolate` feature (strings incl. axis-angle rotate, tuples, discrete step1 strings, easing arrays,
  `posterize`, `perceptual-scale`, `outputType`, `'wrap'`), `Easing.spring` with `allowTail`, `Sequence playbackRate`
  (4.0.528), AbsoluteFill timing props (4.0.501) and premount props (4.0.528), `HtmlInCanvas`, `Solid`, `CanvasImage`,
  `Interactive`, `createEffect`, `@remotion/effects` (installed), `@remotion/transitions` shader presentations and
  pushCut, `@remotion/media` Video `cropRight` and `effects`, `@remotion/three` (+ webgpu), `svg-3d-engine`,
  `timeline-utils`, `CameraMotionBlur`/`Trail`.
- Not available on the target: `HtmlInCanvasMotionBlur` (4.0.529 source only), `@remotion/mac-cursors` (install it or
  draw our own cursor SVG with a hotspot table as in `example/CanvasCapturePreview.tsx`), `@remotion/maptiler`
  (internal, needs a MapTiler key), `@remotion/gsap`.

Craft rules distilled from the team's best pieces
- Product demos: prefer a real screen recording on a tilted orthographic plane (about 28 deg, X-dominant axis), a
  static depth-of-field ellipse on the area of interest, a re-drawn cursor 2-5x larger than native with 0.9x click
  dips, trims with negative `from`, speed ramps (2.3x boring parts, 0.7x key moments), and cut the edit into
  0.9-1.7 s shots, one gesture each.
- When the UI is rebuilt in React: one eased value drives cursor position, displayed number and the real effect; the
  cursor arrives 8-12 f before acting; hover states appear 8 f before a drag.
- Data: animate the container first, text next, data last, callout last-landing; count-ups share the bar's window and
  easing; hold at least 40% of the runtime on the settled chart.
- Explainers: captions carry the video; inserts start on the spoken word and sit above the caption band; b-roll 3-5 s
  with 6 f fades and a slow Ken Burns; one overlay every 4-10 s; side panels push the presenter 20%.
- Short-form: something changes every 2-4 s; entrances 5-11 f pops or 6-8 f pushes; captions huge (Arial Black 900,
  black stroke, hard sticker shadow, active word coloured); flash cuts; a stop-motion posterize for handmade energy.
- Logos: stroke draw-ons with sub-range phasing, fly-in smears, anticipation (reversed spring), then a gentle breathing
  idle; stingers exit exactly in the last 15 f.
- 3D without WebGL: orthographic extrusion with black sides and HTML front faces, tilts under about 0.3 rad (always
  under 90 deg), flips with content swap at 90 deg; three.js when you need lighting, materials or video on surfaces.
- Effects: build looks from stacks (texture + grade + vignette), animate effect params with interpolate, quantise seeds
  for glitchy stutter, crossfade stacked copies to show an effect turning on.
- Sound: every visual event with an SFX gets it on the same frame, quietly (0.05-0.1 for chimes and whooshes).

## 8. Best examples to learn from

Complete videos (study the whole file)
- `brand/WebMCPPromo/MacBookScene.tsx`: the most modern promo: camera dive into a laptop screen, DOF ramp, chat sidebar,
  streamed answer, shimmer, loop variant, 60 fps keyframes with spring easing arrays.
- `example/ParseAndDownloadMedia/*`: best timing lesson: overlapping beats, callouts that fire as an eased progress bar
  passes them, text roll, curtain end card, 3D turn-in with endless drift.
- `brand/announcements/whats-new-in-remotion/*` (`Composition.tsx`, `Root.tsx`, `SlideInOverlay.tsx`,
  `NumberedChapter.tsx`, `LowerThird.tsx`, `Prompt.tsx`, `CodeTransition.tsx`): a 4:37 talking-head announcement:
  silence table, per-chapter compositions, side panels, chapter pops, b-roll units, code morphs, light-leak overlays.
- `jonny/disco-light-show/Composition.tsx` (+ `MasterWithEffect.tsx`, `AnimatedCaptionsBigWords.tsx`, `ForkDrop.tsx`,
  `DiscoBallBg.tsx`): 60 s vertical music explainer in the Studio keyframe style: 24 layers, keyframed pushes,
  sub-canvas camera, big-word captions, CRT outro.
- `jonny/how-can-remotion-be-free/*`: caption-first explainer with hand-drawn inserts placed on word timestamps.
- `brand/Compose/WhatIsRemotion.tsx`: multi-layer 3D explainer with synchronised springs (measureSpring sync,
  pass-through sums, late whip pan) that loops to its start.
- `brand/HomepageAssets/CodingPrompt.tsx` + `Map.tsx` + `Master.tsx`: prompt-to-result homepage loop with a Freeze
  crossfade.
- `example/Gsap/Showcase.tsx`: a fully art-directed 7 s title card (build, live hold, fast exit, wipe, end line).
- `example/BarChart.tsx`: the clearest statement of the current house style for data and UI.
- `brand/CloseUpsSeries.tsx` + `brand/CloseUp1.tsx`/`CloseUp2.tsx`/`CloseUp5.tsx`/`CloseUp8.tsx` +
  `brand/PitchCorrection.tsx`: the product close-up recipe and the montage edit.
- `brand/ShipCard.tsx` (+ `brand/effects/EffectShowcaseScaffold.tsx`, `CornerPinEffectShowcase.tsx`): procedural UI
  demo with a scripted cursor and truthful values.
- `example/SwitzerlandMap/SwitzerlandMap.tsx`, `ZurichToStuttgartMap.tsx`, `MapPin.tsx`: map storytelling.

Components and techniques
- `brand/Skills2CodeChange.tsx`, `brand/Skills2CrazyContext.tsx`: code morph and typewriter firehose with explosions.
- `brand/Skills2Router.tsx`, `brand/Skills2TableBangComp.tsx`: the modern keyframe idiom (easing arrays, allowTail,
  perceptual zoom, bouncy spin on threes) in under 100 lines each.
- `brand/Skills2Gesture.tsx`, `brand/Skills2TableBang.tsx`: layers driven by tracked per-frame data; depth swap through
  split Sequences.
- `brand/Applications.tsx` + `brand/Applications/KineticType.tsx`: spring push loop and the letter rise.
- `brand/Brand/Logo.tsx`, `brand/Brand/Recorder.tsx`, `brand/Brand/TriangleToSquare.tsx`, `brand/animated-logo/*`:
  logo craft (anticipation, morph, spiral exit, arc wordmark, stroke-drawn wordmark).
- `brand/video-elements/*` (`StudioCodeHandoff.tsx`, `Studio.tsx`, `Prompt.tsx`, `Thinking.tsx`, `UpperThird.tsx`,
  `step-guide.tsx`, `FlyingCards.tsx`, `TextEditor.tsx`): the NLE insert library and UI replicas.
- `brand/DesignSystems.tsx`, `brand/DesignSystemsResponsive.tsx`, `brand/DocsPagesShowcase.tsx`: ping-pong loop,
  responsive flipbook, seeded data-driven montage.
- `brand/HomepageAssets/LicenseQuestionsGraphic.tsx`, `RenderProgress.tsx` + `make-rounded-progress.ts`,
  `ExpertsGraphic.tsx`: micro-motion catalogue, seamless conveyor, orbit flip gallery.
- `example/moving-pill-captions.element.tsx`, `example/CaptionsTester/AnimatedCaptions.tsx`,
  `jonny/components/AnimatedCaptions.tsx` + `paginate-captions.ts`, `example/Title/FitTextOnNLines.tsx`: captions.
- `promo/homepage/Demo/DigitWheel.tsx` + `TemperatureNumber.tsx`: odometer and summed-spring state timeline;
  `promo/homepage/Demo/index.tsx` + `Comp.tsx` + `DemoRender.tsx`: Player + in-browser export.
- `example/MultiSceneSample/*`: the recommended Studio-editable authoring style in three tiny scenes.
- `example/Transitions/CustomTransition.tsx`, `PushCutDemo.tsx`, `AudioTransition.tsx`,
  `example/TransitionSeriesOverlay/index.tsx`: custom presentation and timing, push cut alignment, transition SFX,
  overlay rules.
- `example/SequencePlaybackRateKeyframes.tsx` + `SequencePlaybackRateLoops.tsx`: authoritative retiming semantics.
- `example/JumpCuts.tsx`, `example/DifferentSegmentsAtDifferentSpeeds.tsx`, `example/FreezePortion/FreezePortion.tsx`,
  `brand/WebMCPPromo2.tsx`: editing primitives.
- `example/AudioVisualization/index.tsx`, `example/mirrored-spectrum.element.tsx`, `example/oscilloscope.element.tsx`,
  `example/voice-visualization/VoiceVisualization.tsx`, `brand/LogoHorn/index.tsx`, `brand/Sfx/SfxShowcase.tsx`:
  audio.
- `example/HtmlInCanvas/compose-webgl-crt.tsx`, `minimal-docs-webgl.tsx`, `compose-webgpu.tsx`, `changing-size.tsx`,
  `example/EffectsTestbed/*`, `brand/effects/metallic-swirl-effect.ts`, `brand/effects/Goal.tsx`: effects and shaders.
- `example/ReactSvg/*`, `example/Paths/PathEvolve.tsx`, `example/RoughNotation/*`: logo build with orbit comets, path
  draw-ons, hand-drawn annotations.
- `brand/3DContext/*` + `brand/3DCheck/index.tsx`, `example/3DSvgContent/SpinEffect.tsx`, `design/helpers/Outer.tsx`,
  `svg3d/matrix.ts` + `extrude-element.ts`: CSS/SVG 3D; `example/ThreeScene/*`, `example/VideoTexture.tsx`,
  `three/ThreeCanvas.tsx`, `three/webgpu.tsx`: three.js done right.
- `maptiler/MapViewport.tsx` + `delay-map-render.ts` + `use-map-premounting.ts`: how to wrap any imperative WebGL
  library deterministically.

## 9. Open questions

- Semantics not verifiable in the copy (core sources absent): exact `Sequence freeze` behaviour inside a shifted child
  (StudioCodeHandoff freezes Scene11 at 655 through `from={-416}` in a 240 f comp: is the freeze frame clamped to the
  host range?); whether `useVideoConfig().durationInFrames` inside `<Sequence from={10}>` without a duration is the comp
  length or minus 10; whether an `AbsoluteFill` without `from` registers as a timeline item (the team passes
  `showInTimeline={false}`); whether `premountFor` counts parent or retimed frames inside a rated Sequence.
- How the per-frame cursor tracks and tracked-card keyframes were produced (a Studio recorder, a canvas-capture tool, a
  motion tracker?). The data looks machine-baked (1/64 px coordinates, 1e-13 float noise, 30 Hz pairs).
- `@remotion/mac-cursors`: does `style.scale` scale about the hotspot (the close-ups rely on it at 3-7x)? Do `'auto'`
  and `'default'` differ visually? Is `'resizewesteast'` a bundled asset name?
- `@remotion/gsap` internals (timeline duration vs Sequence, premount handling) are inferred from fixtures only.
- `HtmlInCanvas`: is `style` applied to the canvas, the capture wrapper or both; what is the default paint when
  `onPaint` is omitted; are other canvas components (a `Solid`) fully supported inside it (NewsHeadline nests one)?
- Effects: evaluation order is assumed first to last (all team code relies on it); `tint()` default amount when
  omitted; `tear()` behaviour for progress 1 to 2; does `@remotion/media` `Video` `effects` behave identically in
  preview and render (issue 7449 was a fast-refresh bug)?
- `@remotion/media` `Audio hidden`: mutes or only hides? Fractional `durationInFrames` on media (456.46, 1801.67):
  exact rounding?
- How the Studio discovers `*.element.tsx` files (element library, drag and drop from `StudioProtocolInternals.
  makeDragData`); what `supportsEffects: false` changes; how `keyframable: true` schema fields are keyframed.
- `@remotion/maptiler`: whether it will be published publicly (README says internal) and which `chromiumOptions.gl`
  renders it reliably on Lambda; whether MapRegion/MapRoute re-add layers after a runtime style change.
- `extractFrames` / `loadWaveformPeaks` inside a headless render (WebCodecs + OffscreenCanvas in Chrome Headless Shell).
- pushCut ends the incoming scene at 1.07 while the next frame renders at 1.0: a visible snap? (not verified visually).
- Visual confirmation still needed that the tilted close-up planes render without perspective in both preview and
  render (no `perspective` found in any ancestor).

## 10. The 30 best snippets to turn into our own components

Each entry: source (path:lines in the 4.0.529 copy) | proposed component | what it does | why it is worth owning.

1. `brand/Applications.tsx:31-71` (constant at :43-50) | `KEYFRAME_SPRING` + `PushLoop` | the Studio default keyframe
   easing, used in a two-panel push carousel keyed `[0, 85, 95, 167, 179]` with `[linear, SPRING, linear, SPRING]` |
   one shared easing token for all keyframed motion, and a loopable push that needs no TransitionSeries.
   ```tsx
   export const KEYFRAME_SPRING = Easing.spring({damping: 200, mass: 1, stiffness: 100,
     allowTail: true, durationRestThreshold: 0.02, overshootClamping: false});
   const x = interpolate(frame, [0, 85, 95, 167, 179],
     ['0px 0px', '0px 0px', '-1240px 0px', '-1240px 0px', '0px 0px'],
     {extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: [Easing.linear, KEYFRAME_SPRING, Easing.linear, KEYFRAME_SPRING]});
   ```
2. `example/MultiSceneSample/OpeningScene.tsx:28-37`, `FeatureScene.tsx:30-35`, `ClosingScene.tsx:28-36` | `RiseIn`,
   `ScaleIn`, `FadeEnvelope` | 20 f expo-out rise with a string translate; 24 f perceptual spring scale; one call for
   in (18 f expo-out), hold and out (19 f expo-in) | the smallest complete set of Studio-editable scene primitives.
   ```tsx
   opacity: interpolate(frame, [0, 18, 70, 89], [0, 1, 1, 0], {
     easing: [Easing.bezier(0.16, 1, 0.3, 1), Easing.linear, Easing.bezier(0.7, 0, 0.84, 0)],
     extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
   ```
3. `example/BarChart.tsx:24-316` | `GlassBarChart` (`StaggeredBar`, `CountUp`, `PopBadge`, `BreathingGlow`) | full data
   card with an exact entrance cascade, synced count-ups and a spring badge in a fixed window | the team's clearest
   house style, ready to parameterise for any metric.
4. `brand/announcements/whats-new-in-remotion/LowerThird.tsx:25-68` + `brand/video-elements/UpperThird.tsx:20-44` |
   `LowerThird` / `TitleCard` | entry-minus-exit spring with a tilt that settles; full enter / noise-float idle / exit
   lifecycle keyed to `durationInFrames` | the cleanest in-and-out pattern; works as an NLE insert.
   ```tsx
   const entry = spring({fps, frame, config: {damping: 200}});
   const exit = spring({fps, frame: frame - durationInFrames + 15, config: {damping: 200}});
   const p = entry - exit;
   const style = {translate: `0px ${interpolate(p, [0, 1], [400, 0])}px`,
     rotate: `${interpolate(p, [0, 1], [-0.03 * Math.PI, 0])}rad`};
   ```
5. `brand/announcements/whats-new-in-remotion/SlideInOverlay.tsx:26-96` + `Composition.tsx:24-55` + `Root.tsx:26-41` |
   `TalkingHeadKit` (`useSidePanelProgress`, `SidePanel`, silence-table trims) | 40% side panel with presenter push on
   one progress; takes trimmed to speech from data with matching calculateMetadata | the whole grammar of a
   talking-head announcement.
6. `brand/Applications/KineticType.tsx:50-79` | `LetterRise` | per-letter rise from under a clip line, 2 f stagger,
   expo-out, index continues across lines | typographic, cheap, works for any string.
7. `example/Gsap/Showcase.tsx:14-121, 188-203` | `MaskedWordRiseTitle` | kicker with tracking collapse, words hinging up
   out of masked rows (rotateX -70, yPercent 130), rule wipe, fanned cards, staggered exit, full-frame wipe to an end
   line | a complete title-card choreography; port the GSAP values to interpolate.
8. `brand/video-elements/Prompt.tsx:37-107` + `Thinking.tsx:12-48` + `brand/HomepageAssets/CodingPrompt.tsx:47-261` |
   `TerminalPrompt` + `AgentChatBeat` | fixed-duration typing, block cursor, spinner/shimmer status, send press, bubble
   rise, streamed tokens | the standard "AI agent does X" beat used across the brand.
9. `brand/Skills2CodeChange.tsx:136-567` + `brand/Skills2CrazyContext.tsx:29-98` | `CodeMorph` + `TextExplode` |
   tokenizer, weighted LCS, measured token layout under delayRender, explode/glide/fade choreography; golden-angle
   burst with parity spin | code on screen is common in dev videos; the measurement pattern is reusable for any
   text morph.
10. `example/moving-pill-captions.element.tsx:200-256` | `PillCaptions` | measured word boxes plus summed 5 f springs
    move a highlight pill word to word | exact fit for any font and wrap, as a Studio element.
    ```tsx
    const idx = page.tokens.reduce((acc, t, i) => i === 0 ? acc : acc + spring({
      frame: pageFrame, fps, config: {damping: 100}, durationInFrames: 5,
      delay: Math.max(0, ((t.fromMs - page.startMs) / 1000) * fps - 2.5)}), 0);
    const left = interpolate(idx, lefts.map((_, i) => i), lefts) - 12;
    ```
11. `jonny/disco-light-show/AnimatedCaptionsBigWords.tsx:25-113` | `BigWordCaptions` | stacked uppercase words popping
    in on their start frames, active word coloured, auto-fit size, sticker shadow | the short-form caption look.
12. `jonny/components/AnimatedCaptions.tsx:87-364` + `jonny/components/paginate-captions.ts:203-518` |
    `FocusCaptions` + `paginateCaptions` | lens (glow, fisheye, radial blur) gliding to the active word; sentence-aware
    DP pagination with awkward-break penalties | premium captions and far better page breaks than fixed windows.
13. `example/Title/FitTextOnNLines.tsx:25-97` (+ `example/TikTokTextbox/TikTokTextBox.tsx:44-118`) | `RoundedTextBox` |
    fits text to N lines and draws the TikTok-style rounded background per line | the exact platform look.
14. `promo/homepage/Demo/DigitWheel.tsx:18-179` + `TemperatureNumber.tsx:4-68` | `OdometerNumber` + `useStateTimeline` |
    3D rolling digit drum with masks and per-column stagger; N states driven by summed springs | numbers that feel
    mechanical; the state-timeline helper animates any multi-step morph.
15. `example/ParseAndDownloadMedia/FrontFace.tsx:29-75`, `TopFace.tsx:9-84`, `Covert.tsx:8-35` | `ProgressCallouts`,
    `TextRoll`, `CurtainEndCard` | callouts timed to where an eased progress bar is, status text rolling to a new line,
    panel-then-logo curtain | cause-and-effect storytelling for product features.
16. `jonny/how-can-remotion-be-free/FirstCustomerChart.tsx:22-55, 135-250` | `SketchChart` + `DrawOnStroke` | hand-drawn
    bar chart: wobbly doubled strokes drawn with `pathLength={1}`, per-item stagger, bar grown through an animated
    clipPath, circle and arrow emphasis | a dependency-free explainer style.
17. `brand/HomepageAssets/Master.tsx:63-94` + `brand/DesignSystems.tsx:11-67` | `SeamlessLoop` (`FreezeCrossfade`,
    `pingPong`, `ScaleThroughZeroSwap`) | guaranteed loops for any animation plus a clean hand-off between two brand
    assets | social loops and homepage assets.
    ```tsx
    <Sequence from={duration - 44} durationInFrames={44} style={{opacity: fadeToStart}}>
      <Freeze frame={0}><Scene {...props} /></Freeze>
    </Sequence>
    ```
18. `example/Transitions/CustomTransition.tsx:26-113` + `example/Transitions/AudioTransition.tsx:8-33` |
    `ShapeReveal` + `pausedTiming` + `withSound` | iris transition from any shape maker, a timing with a mid pause, and
    an SFX wrapper for any presentation | fills the gaps between built-in presentations.
19. `jonny/disco-light-show/Composition.tsx:211-369` (+ `BirthdayPartyCompilation.tsx:65-88`) | `KeyframedPush`,
    `FlashCut`, `PendulumExit` | multi-layer push on one spring in 6-8 f, white flash, transformOrigin-then-rotate
    exit | the short-form transition vocabulary without TransitionSeries.
20. `jonny/disco-light-show/MasterWithEffect.tsx:14-173` | `CrtPowerOff` | old-TV turn-off outro over any composition
    (scanlines, chromatic flicker, noise, shake, collapse to a line then a dot) | a signature ending in one wrapper.
21. `brand/CloseUp1.tsx:18-47` + `brand/CloseUp8.tsx:17-47` + `brand/PitchCorrection.tsx:704-732` +
    `brand/QuickSwitcher.tsx:30-137` | `ScreenCloseUp` + `RecordedCursor` | tilted orthographic screen plane with
    progressive-blur DOF, negative-from trim and speed ramp, plus a telemetry-driven vector cursor with 0.9x click
    dips | the Remotion product-video look in about 30 lines of props.
    ```tsx
    <HtmlInCanvas width={1920} height={1080} effects={[radialProgressiveBlur({center: [0.185, 0.716],
      width: 2.047, height: 1.784, endBlur: 15, rotation: -16.9})]}>
      <Solid width={1920} height={1080} color="#1f2427" style={{position: 'absolute'}} />
      <AbsoluteFill style={{width: 3102, height: 3030,
        translate: '-15.7px -1683.5px', scale: 0.725,
        rotate: '0.997177 -0.007592 -0.074696 53.392063deg', transformOrigin: '10.15% 86.1%'}}>
        {/* <Video/> + cursor; add from={-offset} playbackRate={r} to trim and retime */}
      </AbsoluteFill>
    </HtmlInCanvas>
    ```
22. `brand/ShipCard.tsx:230-427` + `brand/effects/EffectShowcaseScaffold.tsx:224-269` | `ScriptedCursor` +
    `InspectorMotion` | waypoint cursor with expo-out moves, ease-in-out drags, hover-before-press, click squash, fades;
    panel expand, icon pop and row highlight helpers; values synced to the rendered effect | believable hand-operated UI
    demos from React-built UIs.
23. `brand/WebMCPPromo/MacBookScene.tsx:185-323` + `brand/Skills2Router.tsx:25-69` | `CameraRig` (`DeviceDive`,
    `SpringReframe`) | keyframed translate + perceptual scale + axis-angle rotate with spring easing arrays and a DOF
    ramp; spring reframe that hands off into an endless drift | premium camera moves in plain CSS.
24. `brand/video-elements/StudioCodeHandoff.tsx:21-163` | `WindowPush` | app windows pushing each other inside a device
    screen with 4-key move/hold/move-back interpolates and easing arrays | UI explainer choreography.
25. `example/JumpCuts.tsx:31-83` + `example/DifferentSegmentsAtDifferentSpeeds.tsx:33-82` +
    `example/FreezePortion/FreezePortion.tsx:12-77` | `JumpCutVideo`, `SpeedRamp`, `FreezeInserts` | frame-exact editing
    primitives with correct seek, retime and ripple math | the basis of any automatic edit.
    ```tsx
    let summed = 0;
    for (const s of sections) {
      summed += s.trimAfter - s.trimBefore;
      if (summed > frame) return {trimBefore: s.trimAfter - summed,
        firstFrame: s.trimBefore - frame - (s.trimAfter - summed) === 0};
    }
    ```
26. `example/mirrored-spectrum.element.tsx:67-126` + `example/oscilloscope.element.tsx:89-150` +
    `example/AudioVisualization/index.tsx:53-251` | `SpectrumBars`, `Oscilloscope`, `RadialSpectrum`, `ChromaticText` |
    audio visualizers with sensible bin mappings, sqrt lift, mirroring, playhead-centred windows | podcast, music and
    voice visuals; the two element files double as `Interactive.withSchema` templates.
27. `example/SwitzerlandMap/SwitzerlandMap.tsx:17-101` + `ZurichToStuttgartMap.tsx:33-141` + `MapPin.tsx:30-72` |
    `MapStory` (`FlyTo`, `RegionReveal`, `RouteReveal`, `PinPop`) | complete map beat sheets with camera and route landing
    together | travel and location videos (needs `@remotion/maptiler` + a key, or reuse the timing with another map).
28. `brand/3DContext/transformation-context.tsx:74-178` + `Div3D.tsx:387-549` + `brand/3DCheck/index.tsx:13-24` +
    `design/helpers/Outer.tsx:37-119` + `example/3DSvgContent/SpinEffect.tsx:5-42` | `Sticker3D` (`Rotate*`/`Scale`
    context, `ExtrudeDiv`, `CoinFlip`, `SpinIn`, `Button3D`) | orthographic extrusion with HTML faces and culling, driven by
    springs | the brand's 3D look without WebGL, crisp at any resolution.
29. `brand/animated-logo/springs.ts` + `first-o.tsx` + `e.tsx` + `i.tsx` + `m.tsx` + `brand/Brand/Recorder.tsx:234-270` + `example/ReactSvg/Arc.tsx:6-68` | `StrokeLogo` kit | stroke draw-ons from one stagger table, sub-range phasing, fly-in
    smears, alpha masks, arc-swing wordmark, comet riding a path | logo reveals and stingers.
30. `example/EffectsTestbed/sample-posterize-2d.ts:42-95` + `sample-rgb-shift-webgl.ts:31-236` +
    `brand/effects/metallic-swirl-effect.ts:372-686` + `example/HtmlInCanvas/minimal-docs-webgl.tsx:79-186` |
    `createEffect` templates + `ShaderOverDom` | 2D and WebGL2 custom effects with schema, key, setup/apply/cleanup;
    WebGL2 onInit/onPaint scaffold over live DOM | any custom look (glitch, CRT, palette, swirl) as a composable effect.

Honourable mentions: `example/ThreeScene/Phone.tsx` + `Scene.tsx` (3D phone with render-safe video texture),
`example/VideoTexture.tsx` (video on a three.js plane via `onVideoFrame`), `brand/Compose/JumpThenDisappear.tsx`
(integrated-speed take-off), `brand/video-elements/FlyingCards.tsx` (posterized stagger),
`brand/HomepageAssets/RenderProgress/make-rounded-progress.ts` (rounded progress fill), `maptiler/delay-map-render.ts`
(wait-for-idle for any imperative renderer), `three/SuspenseLoader.tsx` (Suspense to delayRender),
`brand/DesignSystemsResponsive.tsx` (responsive flipbook), `promo/prompts/use-heart-animation.ts` (up-and-back pulse).
