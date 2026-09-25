# Performance, stability, errors and version gates

## GL setup

- Remotion 4 renders with no WebGL unless a GL backend is chosen: `--gl=angle` on the CLI,
  `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts` (the kit's config and nrk do both),
  `chromiumOptions: {gl: 'angle'}` in `renderMedia`/`renderStill`, or "OpenGL render backend: angle" in the Studio
  render dialog. `swangle` (software) on machines without a GPU, Lambda and Cloud Run (slower); `angle-egl` on Linux
  GPU servers. Remotion 5 turns GL on by itself.
- What needs it: the 63 WebGL2 effects (all but brightness, contrast, grayscale, hue, invert, saturation, tint,
  scale, the two translates and tile), every canvas look, the 12 shader transitions, `@remotion/three`, Skia.
- `<HtmlInCanvas>` itself needs the HTML-in-canvas API: present in the render browser of 4.0.528 (Chrome Headless
  Shell 149) without flags; in a normal Chrome only from 148 with `chrome://flags/#canvas-draw-element`.
  `HtmlInCanvas.isSupported()` (or `isHtmlInCanvasSupported()`) tells.
- Check a GL render with one still first: `nrk.py still PROJECT --comp X --frame N`; a blank or black canvas means
  no GL.

## The WebGL context limit (measured)

Chrome keeps 16 live WebGL contexts per page (one render tab = one page). Each effects host with any WebGL effect
holds a pair of canvases, so 2 contexts; a canvas look is one host; a shader transition instance holds 1; `glow`
adds a 2D canvas (does not count).

Measured on 4.0.528 with animated parameters: 8 hosts render; 10, 12, 16 and 24 fail with "WebGL context was lost
during canvas effect rendering". Static parameters can hide the problem on stills (a chain that does not re-run keeps
its last picture), so test with animation.

- Budget: at most 8 effect hosts mounted at the same time, counting both scenes during a transition.
- One host with five effects beats five hosts with one effect: put a look on the whole scene (`HtmlInCanvas`) or on
  the media element, not on every card.
- Grids of effect demos: page them with `<Sequence>`s; unmounted hosts' contexts are the oldest and are dropped
  first, which is harmless.
- Mount effect layers only while they are visible (Sequence `from` and `durationInFrames`).

## Cost tiers (per effect, relative)

- Cheap: the 2D filters (`hue`, `saturation`, `grayscale`, `invert`), `tint`, `scale`, translates, and every
  single-pass WebGL effect (colour, vignette, noise, scanlines, halftone, pixelate, chromatic aberration, wave,
  barrel, lightLeak, shine, tear).
- Moderate: procedural single passes (`paper` is the heaviest, `burlap`, `emboss`, `contourLines`,
  `liquidContours`, `shrinkwrap`, `roughenEdges`, `pattern`).
- Heavy: `blur` and the progressive blurs (2 passes, up to 65 taps), `regionBlur` (3 passes), `glow` and
  `dropShadow` (4 passes), `zoomBlur` and `lightTrail` (up to 64 samples), `noiseDisplacement`, `outline`.
- CPU every frame: `brightness`, `contrast` (read the whole frame back into JavaScript), `tile`, `outline` with
  `edgeSimplification`. Use `exposure`, `levels`, `colorCorrection` on video instead.
- `pixelDensity` multiplies the pixel count by its square (2 = 4 times the work and the uploads).
- CSS side: SVG filters (turbulence grain, RGB split, posterize) run on the CPU at full frame; `Bloom` and
  `SlicesCss` render their children several times; `backdrop-filter` and stacked large blurs are slow; a CSS blur
  under about 0.8 px does nothing.
- Static effect parameters cost nothing after the first frame on a `<Solid>` (the chain re-runs only when a
  parameter changes); animated parameters re-run the whole chain every frame.
- A transition renders both scenes: two heavy scenes overlap at double cost.

## Determinism

- Every effect is a pure function of its parameters and pixels; seeds are hashed with the pixel position. Drive
  seeds, offsets and progress from the frame and chunked parallel renders match.
- `whiteNoise` uses a sine hash whose low bits can differ between GPU drivers: local and Lambda renders of static may
  differ slightly (within one render it is stable).
- Randomness in React code: `random(seed)` (the kit's `r01`, `rand`) or `noise2D`; never `Math.random()` or time.
- Hosts hold `delayRender` until their chain has run (Solid, CanvasImage, HtmlInCanvas, shader presentations per
  paint) and cancel the render on errors, so a frame is never captured half-drawn.
- `<Freeze>` at fractional frames (motion blur) needs children that tolerate non-integer frames.

## Lambda and servers

WebGL on Lambda needs the GL flag (`swangle` by default there) and memory; "context lost" means lower concurrency or
more memory, and fewer simultaneous hosts. Long GPU renders with `angle` can leak memory: split them. A large CSS blur
inside HtmlInCanvas was reported to differ at chunk boundaries on Lambda: compare frames at chunk edges when it
matters.

## Errors and fixes

| Message or symptom | Cause | Fix |
|---|---|---|
| `Failed to acquire WebGL2 context for <effect>. Pass --gl=angle ...` | no GL backend | `--gl=angle` / config / `chromiumOptions`; `swangle` without a GPU |
| `WebGL context was lost during canvas effect rendering ...` | more than 8 effect hosts alive, or memory pressure | fewer hosts (one look on the scene), page grids with Sequences, lower concurrency, more memory |
| `"progress" must be <= 1` (or `>= 0`, `"amount" must be <= 1`, ...) | an unclamped interpolate or a spring overshoot fed an effect | clamp both ends; `Math.min(1, Math.max(0, v))`; the kit's `fx.*` clamp |
| `"radius" must be a finite number`, `"color" must be a non-empty string`, `"rays" must be a finite number`, `"center" must be a [number, number] tuple`, `"content" must be a non-empty string` | a required parameter missing | pass `blur.radius`, `tint.color`, `starburst.rays` and `colors`, `noiseDisplacement.center` and `radius`, `regionBlur` corners, `lut.content` |
| `"color" has been renamed to "dotColor"` | old halftone API | `dotColor` |
| `"dotColor" can only be set when "colorMode" is "solid"` | both given | drop `dotColor` in source mode |
| `"blackPoint" must be less than "whitePoint"` | levels crossed | keep a gap |
| `"topLeft" must be above and to the left of "bottomRight"` | regionBlur box inverted on some frame | keep x1 < x2 and y1 < y2 throughout |
| `"seed" must be <= 1000` | paper or roughenEdges seed driven by the frame | `seed: frame % 1000` or a slow step |
| `"hueShift" must be <= 360` | lightLeak hue animated | wrap `% 360` |
| `"samples" must be <= 64`, `"passes" must be <= 12`, `"x" must be ... less than 89` | limits | clamp |
| `Invalid LUT content ...` (1D LUT, unsupported directive, wrong row count) | LUT file | export a 3D `.cube`; `cleanCube()`; check `LUT_3D_SIZE` |
| `The "width" and "height" props must be numbers on <Img> when effects are passed` | `Img` with effects and CSS sizes | numeric `width`/`height`; `style.objectFit` sets the fit |
| `The ... prop cannot be used on <Img> when effects are passed` | `onLoad`, `alt`, `srcSet`, `ref`... on an Img with effects | remove them (it renders a canvas) |
| `HtmlInCanvas: width must be a positive integer` | fractional size | `Math.round` |
| `<HtmlInCanvas> components cannot be nested` | a canvas look inside a canvas look | css engine for the inner one, or merge the effects into one |
| `delayRender() "waiting for first paint after canvas resize" was called but not cleared after 28000ms` | an HtmlInCanvas inside a scene next to a shader transition | no HtmlInCanvas there (the kit's looks switch to css by themselves); or use CSS transitions around that scene |
| `HTML in Canvas is not supported ...` | preview browser without the API | Chrome 148+ with the canvas-draw-element flag; or a css engine; renders are fine |
| A shader transition plays as a hard cut | the scene entered with a CSS transition (4.0.528 captures nothing for the exiting shader) | split the scene (the kit's Scenes does), or use shader or CSS on both sides |
| `The duration of a <TransitionSeries.Sequence /> must not be shorter than the duration of the next/previous <TransitionSeries.Transition />` | scene shorter than a transition (springs without `durationInFrames` measure longer than expected) | lengthen the scene or shorten the timing; check `getDurationInFrames({fps})`; the kit's planScenes reports it first |
| `A <TransitionSeries.Transition /> component must not be followed by another ...` / overlay adjacency errors | two transitions or overlays in one slot | one per cut, a sequence between |
| `A <TransitionSeries.Overlay /> extends before frame 0 / beyond the previous or next sequence` | overlay longer than the room around the cut | shorter overlay or longer scenes; `offset` integer |
| `The <TransitionSeries /> component only accepts a list of ...` | a wrapper component, text or a plain Sequence inside | map `.Sequence` elements directly |
| TypeScript `Expected 1 arguments, but got 0` on `dissolve()`, `zoomInOut()`, `crosswarp()` | shader factories require an options object | `dissolve({})` |
| A spring transition snaps at the end | `durationRestThreshold` left at 0.005 | 0.001 |
| The old scene shows through a fade | incoming scene not opaque | give it a ground, or `shouldFadeOutExitingScene: true` |
| `cutProgress passed to pushCut() must be greater than 0 and less than 1`, `flashOpacity ... between 0 and 1` | pushCut options | valid values |
| `direction passed to blurSlide() must be one of ...`, `blur ... >= 0` | blurSlide options | valid values |
| Halftone shows only dots on a transparent frame | halftone replaces the source | a paper layer behind, or `halftoneLinearGradient` solid mode |
| Duotone looks posterised | Remotion's `duotone` is a hard threshold | `thermalVision({palette: [dark, light]})` (the kit's `fx.duotone`) |
| Light trail smears the whole frame | every opaque pixel contributes | use it on a cut-out with alpha |
| Outline or shadow cut off | clipped at the host's canvas edge | leave transparent margin, enlarge the host |
| Zoom blur centred in the wrong place vertically | raw `zoomBlur().center` counts y from the bottom | `[x, 1 - y]`, or the kit's `fx.zoomBlur` |
| A blend mode does nothing | the layer is in its own stacking context (isolation, opacity, filter, clip-path on a parent) | move those onto the blended element |
| Motion blur shows nothing | `useCurrentFrame()` read outside the blur wrapper | read it in a child inside |
| `import {brightness} from '@remotion/effects'` is undefined | the root exports 11 effects | subpath import |

## Version gates (relative to 4.0.528)

Available: all 74 effects (newest `lut` 4.0.526, `tear` 4.0.523, `outline` 4.0.515, `tile` 4.0.513; the grade effects
4.0.508 to 4.0.509; `lightLeak` and `starburst` effects 4.0.500; effects on shapes and `maskToSourceAlpha` 4.0.474),
`createEffect`, `Solid` (4.0.464), `HtmlInCanvas` (4.0.455), `Img` effects (4.0.469), TransitionSeries 4.0.59, Overlay
4.0.415, `useTransitionProgress` and `none` 4.0.177, `iris` 4.0.316, `pushCut` 4.0.500, shader presentations 4.0.456
to 4.0.467, `blurSlide` 4.0.523, `makeHtmlInCanvasPresentation` 4.0.456, `trimBefore` on TS.Sequence 4.0.497,
`@remotion/motion-blur` CameraMotionBlur and Trail.

Not available: `<HtmlInCanvasMotionBlur>` (4.0.529), `interpolatePaths` (4.0.529), Canvas editor overrides
(4.0.529). Deprecated but working: `@remotion/light-leaks` `<LightLeak>` and `@remotion/starburst` `<Starburst>`
(removed in 5.0). In v5: GL on by default, `layout="none"` on TransitionSeries throws, premount default changes.
Install packages with `npx remotion add <pkg>` so every `@remotion/*` version matches `remotion` exactly.
