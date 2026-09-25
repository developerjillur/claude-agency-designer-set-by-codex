# D5: Effects, light leaks, starburst, motion blur, noise, canvas, Skia, canvas capture, animation-utils

Knowledge file for the skill authors. Target runtime: Remotion 4.0.528 (React 19). Everything below was checked against
the docs mirror and the package sources; where the two disagree, the source wins and the difference is called out.

---

## 1. Scope and coverage

**Assigned docs read fully: 105 of 105** (listed in `kb/D5-effects-canvas.coverage.txt`):

- `mirror/docs/effects/*`: 75 pages (the `@remotion/effects` API page plus 74 effect pages).
- `mirror/docs/light-leaks/*` (3), `starburst/*` (3), `motion-blur/*` (5), `noise/*` (3), `canvas/*` (11),
  `skia/*` (2), `canvas-capture/installation.md` (1), `animation-utils/*` (2).

**Source read (163 files listed in coverage):**

- `repo/packages/effects/src` (138 TS files): for every one of the 74 effects I read the schema, the `resolve()` defaults,
  the validation function, the fragment shader and the `apply()` call (backend, pass count, sampler setup). The shared
  helpers (`color-utils.ts`, `validate-effect-param.ts`, `uv-coordinate.ts`, `gaussian-blur-shader.ts`,
  `color-correction-shader-utils.ts`, `progressive-pixelate-runtime.ts`, `lut/parse-cube-lut.ts`) were read fully.
  Runtime boilerplate (compile/link/VAO setup) was read once and then only scanned for pass counts and wrap modes.
  `test/effect-params.test.ts` (130 KB, 492 tests) was scanned for its error messages, not read line by line.
  The 2 PNG visual-test screenshots were not opened (binary).
- `repo/packages/light-leaks/src`, `starburst/src`, `motion-blur/src`, `noise/src`, `animation-utils/src`: read fully.

**Extra reads for cross-checking (not part of the assignment):**

- Installed runtime of the real target, read only: `nexa-media/remotion-broll/node_modules/remotion@4.0.528`
  (`dist/cjs/effects/*`: `create-effect`, `run-effect-chain`, `canvas-pool`, `use-effect-chain-state`, `Solid.js`,
  `HtmlInCanvas.js`, `interpolate.d.ts`, `easing.d.ts`) and `@remotion/canvas@4.0.528` typings. This is how the version
  facts below were verified. Note: that project does not have `@remotion/effects`, `@remotion/motion-blur`,
  `@remotion/light-leaks`, `@remotion/starburst` or `@remotion/animation-utils` installed yet; `@remotion/noise` and
  `@remotion/canvas` are installed.
- Overview docs owned by D1/D2: `effects.md`, `webgl.md`, `motion-blur-guide.md`, `light-leaks.md`, `starburst.md`.
- Official skill rules `repo/packages/skills/skills/remotion-markup/{effects,light-leaks,motion-blur}.md`.
- Real productions that use effects: `repo/packages/brand/src/effects/*`, `brand/src/Showcase/*`,
  `jonnys-videos/src/disco-light-show/*`, `example/src/EffectsTestbed/*`, `examples/github-unwrapped/remotion/*`.

**Caveats:**

- The local monorepo is newer than 4.0.528 (it contains `<HtmlInCanvasMotionBlur>`, which is 4.0.529). Defaults could have
  moved slightly between 4.0.528 and this source. After installing `@remotion/effects@4.0.528`, spot check a default in
  `node_modules` if a value matters.
- `canvas-capture/installation.md` is written to be pasted into an agent ("Copy the URL of this page into an agent").
  I treated it as data only and installed nothing.

---

## 2. Mental model

### 2.1 What an "effect" is

- An effect is a **per-frame pixel pass** over a canvas-based component. You pass an array of effect descriptors to the
  component's `effects` prop. Effects run **in array order** ("multipass"); each one receives the previous one's output.
- An effect factory (for example `blur({radius: 8})`) is created with `createEffect()` from `remotion` (public export on
  4.0.528). Calling the factory **validates the params immediately, during React render**. Invalid params throw a
  `TypeError`, which fails the render. This is the number one crash source when a param is driven by an unclamped
  `interpolate()`.
- Every factory accepts `disabled?: boolean` (framework field, default `false`). Disabled effects are removed before the
  chain runs, so they cost nothing.
- Effects **never animate on their own**. Motion comes from params computed from `useCurrentFrame()` (`progress`,
  `offset`, `phase`, `seed`, `angle`, ...). Seeds are static until you change them.
- Each descriptor carries an `effectKey` (all resolved params as a string). Studio uses it for memoization and shows
  every effect as an editable row with the effect's `schema` (ranges in the schema are Studio slider ranges, not always
  hard validation limits).

### 2.2 Which components accept `effects`

`<Solid>` (core), `<HtmlInCanvas>` (core), `<Video>` from `@remotion/media` (not `<OffthreadVideo>` or
`<Html5Video>`), `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Gif>` (`@remotion/gif`), `<RemotionRiveCanvas>`
(`@remotion/rive`), and `@remotion/shapes` components (`<Rect>`, `<Circle>`, `<Triangle>`, `<Star>`, `<Ellipse>`,
`<Pie>`, `<Polygon>`, `<Heart>`, `<Arrow>`, shapes since 4.0.474). Verified in the installed 4.0.528 typings for Solid,
HtmlInCanvas, Img, CanvasImage, AnimatedImage, `@remotion/media` Video and shapes (gif and rive are not installed there).

- `<Solid width height color? pixelDensity? effects>` is the **generator surface**: its source is a 1x1 canvas filled with
  `color` (or left transparent when `color` is omitted) and stretched to `ceil(width * pixelDensity)` pixels. Use it for
  backgrounds (`starburst`, `liquidContours`, `gridlines`, `linearGradient`, `flannel`) and for overlays (`lightLeak` on a
  transparent Solid composites over whatever is behind it).
- `<HtmlInCanvas width height pixelDensity? effects>` is how you put effects on **arbitrary DOM** (text, SVG, cards).
  Preview needs Chrome 148+ with `chrome://flags/#canvas-draw-element` enabled (4.0.528 error text says exactly this);
  rendering needs no flag. Nested `<HtmlInCanvas>` is unsupported.

### 2.3 Backends

- **2D canvas (11 effects):** `brightness`, `contrast`, `grayscale`, `hue`, `invert`, `saturation`, `tint`, `scale`,
  `uvTranslate`, `xyTranslate`, `tile`. Of these, `hue`/`saturation`/`grayscale`/`invert` use `ctx.filter` (cheap),
  `tint`/`scale`/`translate` use `drawImage`/`fillRect` (cheap), while `brightness`, `contrast` and `tile` read pixels back
  with `getImageData` and loop in JavaScript every frame (expensive).
- **WebGL2 (the other 63 effects)**, including `exposure`, `levels`, `shadowsHighlights`, `vibrance`, `whiteBalance`,
  `colorCorrection` and `lut`, whose doc pages only show a compatibility table and do **not** say "uses a WebGL2
  backend". The source is unambiguous: they are WebGL2 and need GL enabled in renders.
- On Remotion 4.x renders, WebGL must be enabled: `npx remotion render --gl=angle`, or
  `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts`, or `chromiumOptions: {gl: 'angle'}` for SSR APIs,
  or "OpenGL render backend = angle" in the Studio render dialog. (Remotion 5 enables it automatically.)

### 2.4 How the chain runs (read from the 4.0.528 runtime)

- Each component owns one **effect chain state** with a canvas pool. The pool lazily allocates **two canvases per backend**
  (ping-pong pair) at the component's pixel size. So a component with any WebGL effect holds 2 WebGL2 contexts; a
  component with 2D effects holds 2 more 2D canvases. Every WebGL effect compiles its program once per target canvas and
  caches it.
- Consecutive effects with the same backend form a "run". Crossing backends costs a bridge: 2D to WebGL uploads the canvas
  directly; WebGL to 2D goes through `createImageBitmap` (async). Grouping same-backend effects reduces bridges.
- Each WebGL effect uploads its input with `texImage2D` (8-bit RGBA, premultiplied) every time it runs. There is no float
  pipeline between effects, so heavy grading stacks can band.
- If the component's pixel width/height changes, the whole chain state (and its GL contexts) is destroyed and rebuilt.
- `<Solid>` wraps each chain run in `delayRender('Solid effect chain')` and calls `cancelRender(err)` on failure, so renders
  wait for the effects and fail loudly on errors. The chain only re-runs when the memoized params change.
- If a WebGL context is lost, the next effect throws: "WebGL context was lost during canvas effect rendering ... Try
  reducing concurrency or increasing the Lambda function memory."

### 2.5 Three output behaviors (decide layering from this)

1. **Modify, keep alpha:** color ops, `noise`, `scanlines`, `burlap`, `paper`, `emboss`, `flannel`, `thermalVision`,
   `duotone`, `tvSignalOff`, `whiteNoise`, `shine`, `linearGradientTint`, `lut`. Transparent pixels stay transparent.
2. **Composite a generated pattern over the source:** `lines`, `rings`, `waves`, `zigzag`, `checkerboard`, `gridlines`,
   `contourLines`, `halftoneLinearGradient` (solid mode), `lightLeak`, `vignette` (color mode), `glow`, `lightTrail`,
   `dropShadow`, `outline`. Most have `maskToSourceAlpha` to keep the pattern inside the source silhouette.
3. **Replace the source:** `linearGradient`, `starburst`, `liquidContours` (source ignored entirely), `halftone` (dots only,
   transparent between dots), `halftoneLinearGradient` in `colorMode: 'source'`, `dotGrid` (source only inside/outside
   dots), `pixelDissolve`/`evolve`/`venetianBlinds` (mask the source). Put replacing generators first in the chain.

### 2.6 Coordinates and units (a frequent source of bugs)

- UV tuples are `[u, v]` with `[0, 0]` = top-left, `[1, 1]` = bottom-right (converted internally for most effects).
  Many accept values outside 0..1 (Studio range `-1..2`), but some validate strictly: `noiseDisplacement.center`
  (0..1), `skew.origin` (0..1), `starburst.origin` (0..1), `pattern.origin` (0..1).
- Pixel params (`radius`, `gridSize`, `thickness`, `dotSize`, `amount` of `chromaticAberration`, ...) are in **canvas
  pixels**, which are CSS pixels times `pixelDensity`. Doubling `pixelDensity` halves the apparent size of every pixel
  param, so scale them with it.
- Angles are degrees everywhere **except** `wave().phase` (radians) and `fisheye().fieldOfView` (radians, 0..PI).
  `waves().phase` is degrees. `liquidContours().phase` is in band cycles (1.0 = one full cycle, loops seamlessly).

### 2.7 Defaults that are NOT a no-op

- **Visible change with no arguments:** `grayscale()` (amount 1), `invert()` (amount 1), `skew()` (x = 20 degrees),
  `barrelDistortion()` (0.25), `chromaticAberration()` (8 px), `fisheye()` (2.5 rad), `wave()` (amplitude 60),
  `mirror()` (mirrors at 0.5), `tile()`, `glow()`, `dropShadow()`, `vignette()` (0.5), `noise()` (0.15),
  `whiteNoise()` (full replace), `tvSignalOff()` (full), `thermalVision()` (full), `paper()` (amount 1), `burlap()`,
  `emboss()`, `flannel()`, `shrinkwrap()`, `roughenEdges()`, `speckle()`, `scanlines()`, `pixelate()`, `dotGrid()`,
  `halftone()`, `linearProgressivePixelate()`/`radialProgressivePixelate()` (end block 40), the progressive blurs
  (end blur 50), `zoomBlur()` (40), every pattern generator, and every progress effect (`evolve`, `venetianBlinds`,
  `pixelDissolve`, `shine`, `lightLeak`, `tear` all default to progress 0.5).
- **Identity with no arguments:** `brightness()`, `contrast()`, `saturation()`, `hue()`, `exposure()`, `levels()`,
  `shadowsHighlights()`, `whiteBalance()`, `vibrance()`, `colorCorrection()`, `cornerPin()`, `uvTranslate()`,
  `xyTranslate()`.
- **Cannot be called without arguments (required params):** `blur` (`radius`), `scale` (`scale`), `tint` (`color`),
  `starburst` (`rays`, `colors`), `noiseDisplacement` (`center`, `radius`), `regionBlur` (`topLeft`, `bottomRight`),
  `lut` (`content`).

### 2.8 The rest of this area in one line each

- `@remotion/light-leaks` (`<LightLeak>`, 4.0.415) and `@remotion/starburst` (`<Starburst>`, 4.0.435): **deprecated**,
  still work on 4.0.528, will not be published from 5.0. Their effect versions moved into `@remotion/effects` (4.0.500).
- `@remotion/motion-blur`: `<CameraMotionBlur>` and `<Trail>` (3.2.39, usable now); `<HtmlInCanvasMotionBlur>` is
  **4.0.529, not available on 4.0.528**.
- `@remotion/noise`: deterministic simplex `noise2D/3D/4D(seed, ...)` in -1..1 for procedural motion (CPU, React side).
- `@remotion/canvas` (4.0.527, experimental): a toolkit for building **editor UIs** around `<Player>` (selection,
  hover, timeline store). Not a drawing API. Parts are 4.0.529 only.
- `@remotion/skia`: React Native Skia inside Remotion (`enableSkia()` webpack override + `<SkiaCanvas>`); WebGL based.
- Canvas Capture: an Apple Silicon only Chrome extension for recording web pages with HTML-in-canvas. User-side tool.
- `@remotion/animation-utils`: `interpolateStyles()` (keyframe whole style objects) and `makeTransform()` helpers.

---

## 3. API digest

### 3.1 Package, imports, custom effects

```bash
npx remotion add @remotion/effects   # installs the version matching the project's remotion
```

- Import each effect from its **subpath**: `@remotion/effects/<slug>`, where slug is the kebab-case name
  (`@remotion/effects/radial-progressive-blur`). Exceptions: `uvTranslate` and `xyTranslate` both come from
  `@remotion/effects/translate`.
- The package root entry (`src/index.ts`) re-exports only 11 effects (`checkerboard`, `pattern`, `tile`, `rings`,
  `starburst`, `lightLeak`, `gridlines`, `zigzag`, `linearGradient`, `linearGradientTint`, `cornerPin`) plus
  `starburstEffectSchema` and `lightLeakEffectSchema`. The official skill's example `import {brightness} from
  "@remotion/effects"` does not match the source; always use subpaths.
- Custom effects: `createEffect<P, S>({type, label, documentationLink, backend: '2d'|'webgl2'|'webgpu', calculateKey,
  setup(target), apply({source, target, state, params, width, height, gpuDevice, flipSourceY}), cleanup(state), schema,
  validateParams})` from `remotion`. Rules from the source: put every resolved param in `calculateKey`; validate in
  `validateParams` (runs at factory call); in WebGL `apply` set `UNPACK_FLIP_Y_WEBGL` to `flipSourceY`; get the context with
  `{premultipliedAlpha: true, alpha: true, preserveDrawingBuffer: true}`; reset 2D context state (`filter`,
  `globalAlpha`, `globalCompositeOperation`) after drawing. `webgpu` is a backend option; the device is a cached singleton.
  Working samples: `repo/packages/example/src/EffectsTestbed/sample-posterize-2d.ts`, `sample-rgb-shift-webgl.ts`,
  `palette-map.ts`, and `repo/packages/brand/src/effects/metallic-swirl-effect.ts`.

Minimal usage shape:

```tsx
import {Video} from '@remotion/media';
import {colorCorrection} from '@remotion/effects/color-correction';
import {noise} from '@remotion/effects/noise';

<Video src={src} effects={[
  colorCorrection({exposure: 0.2, contrast: 1.1, temperature: 0.1}),
  noise({amount: 0.05, seed: frame}),
]} />
```

Cost legend used below (relative, from reading the shaders, not measured):
**T0** trivial single pass, 1 to 8 texture reads. **T1** single pass with procedural noise or tens of reads.
**T2** multi-pass or up to about 100 reads per pixel. **CPU** pixel readback plus a JavaScript loop every frame.

### 3.2 Color and tone

**brightness()** `brightness` · 4.0.466 · 2D (CPU loop) · CPU
- `amount = 0` (-1..1). Adds `round(amount*255)` to R, G and B.
- Look: flat lift or crush, washes out blacks. Not photographic; prefer `exposure()` for footage.
- Gotcha: `getImageData` + loop every frame at full resolution. Not alpha aware (works on premultiplied data).

**contrast()** `contrast` · 4.0.467 · 2D (CPU loop) · CPU
- `amount = 1` (>= 0). `0` = flat mid gray, `>1` more contrast. Pivot is 128.
- Order matters with brightness (not commutative). Prefer `colorCorrection({contrast, pivot})` (GPU, has a pivot).

**exposure()** `exposure` · 4.0.508 · WebGL2 · T0
- `stops = 0` (-5..5, throws outside). Multiplies light in linear space: +1 doubles.
- Look: natural brighten/darken that keeps tonal relationships.

**levels()** `levels` · 4.0.508 · WebGL2 · T0
- `blackPoint = 0`, `whitePoint = 1` (both 0..1, black must be < white or it throws), `gamma = 1` (0.01..10; >1 brightens
  midtones). Remaps unpremultiplied sRGB input then applies gamma.
- Look: punchier blacks and whites, midtone lift. It cannot raise the output black (for faded film blacks use
  `colorCorrection({blacks: +x})` or a LUT).

**shadowsHighlights()** `shadows-highlights` · 4.0.508 · WebGL2 · T0
- `shadows = 0`, `highlights = 0` (-1..1, up to +/- 1 stop). Smooth luminance weights, applied as linear gain, no halos.
- Look: lift shadows, recover highlights, HDR-lite.

**whiteBalance()** `white-balance` · 4.0.508 · WebGL2 · T0
- `temperature = 0` (-1 cool .. +1 warm), `tint = 0` (-1 green .. +1 magenta). Channel gains up to about 0.3 stops,
  normalized to keep luminance.

**vibrance()** `vibrance` · 4.0.508 · WebGL2 · T0
- `amount = 0` (-1..1; -1 = grayscale). Boosts muted colors more than saturated ones; grays untouched.

**saturation()** `saturation` · 4.0.466 · 2D (`ctx.filter: saturate()`) · T0
- `amount = 1` (>= 0; 0 gray, >1 more).

**hue()** `hue` · 4.0.466 · 2D (`ctx.filter: hue-rotate()`) · T0
- `degrees = 0`. Any finite number.

**grayscale()** `grayscale` · 4.0.466 · 2D (`ctx.filter`) · T0
- `amount = 1` (0..1). Default is full black and white.

**invert()** `invert` · 4.0.466 · 2D (`ctx.filter`) · T0
- `amount = 1` (0..1). Negative, x-ray looks.

**tint()** `tint` · 4.0.466 · 2D (source-atop fill) · T0
- `color` **required** (any CSS color), `amount = 0.5` (0..1). Paints a flat color over opaque pixels only.

**colorCorrection()** `color-correction` · 4.0.509 · WebGL2 · T0
- `exposure = 0` (-5..5), `contrast = 1` (>= 0), `pivot = 0.5` (0..1), `shadows = 0`, `highlights = 0`, `whites = 0`,
  `blacks = 0`, `temperature = 0`, `tint = 0`, `vibrance = 0` (all -1..1), `saturation = 1` (>= 0).
- Fixed internal order: exposure, white balance, tonal regions (shadows/highlights, then whites/blacks), contrast,
  saturation, vibrance. One pass, no intermediate 8-bit round trips, so it looks cleaner than chaining 6 effects.
- The default grade tool. Identity when called with no args.

**lut()** `lut` · 4.0.526 · WebGL2 · T0
- `content` **required**: full text of a 3D `.cube` file. Supported: `LUT_3D_SIZE` 2..256, `TITLE`, `DOMAIN_MIN`,
  `DOMAIN_MAX`, blank lines, `#` comments. 1D LUTs and any other directive (for example `LUT_3D_INPUT_RANGE`) throw.
  Row count must equal size cubed. Uploaded as a float 3D texture with trilinear lookup.
- Parsed LUTs are cached (LRU of 4 contents); switching among more than 4 LUTs re-parses. 33-point LUTs are the sweet spot.

**duotone()** `duotone` · 4.0.468 · WebGL2 · T0
- `darkColor = '#000000'`, `lightColor = '#ffffff'`, `threshold = 0.5` (0..1).
- **Hard threshold**, not a gradient map: each pixel becomes exactly one of the two colors (BT.601 luminance). Looks like
  1-bit print, stencil, risograph single pass. For the smooth "Spotify duotone" use `thermalVision` with 2 colors.

**thermalVision()** `thermal-vision` · 4.0.479 · WebGL2 · T0
- `amount = 1` (0..1), `palette` (>= 2 CSS colors; default dark blue, blue, cyan, green, yellow, orange, red, white).
- The palette is a linearly filtered 1D texture, so this is a **true gradient map**. Two colors = smooth duotone, three
  = tritone, default = heat cam.

**linearGradientTint()** `linear-gradient-tint` · 4.0.483 · WebGL2 · T0
- `start = [0, 0.5]`, `end = [1, 0.5]` (UV), `startColor = '#000000'`, `endColor = '#ffffff'`, `amount = 0.5` (0..1).
  Blends existing RGB toward a two-stop gradient; alpha kept; clamps outside the stops.

**colorKey()** `color-key` · 4.0.472 · WebGL2 · T0
- `keyColor = '#00ff00'`, `similarity = 0.18`, `smoothness = 0.08`, `spillSuppression = 0.25` (all 0..1).
- RGB distance keying (normalized by sqrt 3) with a smoothstep band `similarity +/- smoothness`; spill suppression caps
  the dominant key channel at the average of the other two. Typical good values from real use: similarity 0.19 to 0.45,
  spillSuppression up to 0.9.

### 3.3 Blur and focus

**blur()** `blur` · 4.0.465 · WebGL2 · T2 (2 passes)
- `radius` **required** (finite px; <= 0 passes through), `horizontal = true`, `vertical = true` (one axis off =
  directional blur). Separable Gaussian, sigma = radius / 3, 9 to 65 taps per pass (stride grows past radius 64).
  Edges clamp (no dark border).

**linearProgressiveBlur()** `linear-progressive-blur` · 4.0.472 · WebGL2 · T2
- `start = [0, 0.5]`, `end = [1, 0.5]`, `startBlur = 0`, `endBlur = 50` (px, negatives clamped). Radius interpolates
  along the line, clamped outside. Tilt shift, gradual focus fall-off.

**radialProgressiveBlur()** `radial-progressive-blur` · 4.0.483 · WebGL2 · T2
- `center = [0.5, 0.5]`, `width = 1`, `height = 1` (full ellipse size in UV), `rotation = 0`, `start = 0` (0..1 along the
  ellipse), `startBlur = 0`, `endBlur = 50`. Spotlight focus, depth of field. Most used blur in Remotion's own videos.

**regionBlur()** `region-blur` · 4.0.507 · WebGL2 · T2
- `topLeft`, `bottomRight` **required** UV tuples (top-left must be above and left of bottom-right), `blurRadius = 40`,
  `feather = 0` (px), `roundness = 0` (0 rectangle .. 1 circle/pill). For faces, plates, documents. Make the region large
  enough that detail stays inside the fully blurred part.

**zoomBlur()** `zoom-blur` · 4.0.480 · WebGL2 · T2 (samples)
- `amount = 40` (px; streak length scales with distance from center), `center = [0.5, 0.5]`, `samples = 24` (integer
  1..64). Radial speed zoom, impact punch-ins. Animate `amount` down to 0.

### 3.4 Distortion and geometry

**barrelDistortion()** `barrel-distortion` · 4.0.466 · WebGL2 · T0
- `amount = 0.25` (0..1). Geometric bulge only; corners become transparent. CRT screen curvature.

**chromaticAberration()** `chromatic-aberration` · 4.0.467 · WebGL2 · T0
- `amount = 8` (px, >= 0), `angle = 0` (degrees; 0 horizontal, 90 vertical). Red sampled at -offset, blue at +offset,
  alpha from the center sample. RGB split, lens fringe, glitch.

**fisheye()** `fisheye` · 4.0.470 · WebGL2 · T0
- `fieldOfView = 2.5` (radians, 0..PI, 0 disables), `center = [0.5, 0.5]`, `radius = 1` (1 = full height; outside is
  untouched), `zoom = 1` (> 0). Samples outside the source become transparent. Action cam, peephole, bulge.

**wave()** `wave` · 4.0.465 · WebGL2 · T0
- `phase = 0` (**radians**), `direction = 'horizontal'` (phase along X, pixels move vertically) or `'vertical'`,
  `amplitude = 60` (px), `wavelength = 240` (px, > 0). Chain two for both axes. Edges clamp, so the border pixels smear;
  overscan with `scale()` first or keep amplitude small. Flag wave, heat haze, underwater.

**noiseDisplacement()** `noise-displacement` · 4.0.474 · WebGL2 · T2 (inside the circle)
- `center` **required** (UV, each 0..1), `radius` **required** (0 < r <= 1, relative to the shorter side),
  `strength = 36` (px), `seed = 0`, `grainSize = 8` (px), `passes = 6` (integer 1..12), `blur = 0` (px),
  `feather = 0.25` (fraction of radius), `biasDirection = 0` (degrees), `biasAmount = 0` (>= 0).
- Local smeared/glass distortion in a soft circle. Animate `seed` for boiling, `biasAmount` for directional smear.

**cornerPin()** `corner-pin` · 4.0.482 · WebGL2 · T0
- `topLeft = [0, 0]`, `topRight = [1, 0]`, `bottomRight = [1, 1]`, `bottomLeft = [0, 1]` (UV, Studio range -1..2).
  Projective (homography) map of the source rectangle into the quad; outside is transparent; clipped to the canvas.
  Screen replacement, billboard, phone mockup, 3D card tilt.

**skew()** `skew` · 4.0.491 · WebGL2 · T0
- `x = 20`, `y = 0` (degrees, strictly between -89 and 89), `origin = [0.5, 0.5]` (0..1). Uncovered areas transparent.

**mirror()** `mirror` · 4.0.466 · WebGL2 · T0
- `direction = 'horizontal'` (left/right) or `'vertical'`, `position = 0.5` (0..1), `invert = false` (mirror the other
  half). Chain horizontal + vertical for 4-way symmetry (kaleidoscope-lite).

**scale()** `scale` · 4.0.466 · 2D · T0
- `scale` **required in the type** (docs say default 1; calling `scale()` with no value throws), must be > 0;
  `horizontal = true`, `vertical = true`. Scales around the canvas center, clipped to the canvas. Use before `tile()`,
  or to overscan before `wave()`.

**uvTranslate()** / **xyTranslate()** `translate` · 4.0.467 · 2D · T0
- `uvTranslate({u = 0, v = 0})` (1 = full width/height), `xyTranslate({x = 0, y = 0})` (px). Content moved out is clipped.

**tile()** `tile` · 4.0.513 · 2D (CPU bounds scan) · CPU
- `horizontal = true`, `vertical = true`. Finds the non-transparent bounds and repeats them, mirroring every other copy so
  edges match (seamless texture). Place `scale({scale: 0.25})` before it.

**pattern()** `pattern` · 4.0.477 · WebGL2 · T1
- `scale = 0.1` (> 0), `cropLeft/Top/Right/Bottom = 0` (px, negatives extend), `gapX = 0`, `gapY = 0` (px; docs say
  >= 0 but the source does not validate, and negative gaps overlap tiles in real use), `offsetU = 0`, `offsetV = 0`
  (animate to scroll), `rowOffset = 0` (px per row), `rowOffsetEvery = 0` (integer >= 0; 0 = accumulate forever),
  `columnOffset = 0`, `columnOffsetEvery = 0`, `origin = [0, 0]` (0..1), `wrap = true`.
- Wallpaper, logo walls, contact sheets, brick layouts (`rowOffset: w/2, rowOffsetEvery: 2`).

**tear()** `tear` · 4.0.523 · WebGL2 (192-row mesh, drawn twice) · T0
- `progress = 0.5` (>= 0; 1 reaches the far edge; above 1 the halves keep separating), `angle = 0` (rip direction; 0 top
  to bottom, 90 left to right), `rotation = 20` (0..90, outward rotation of each piece), `jaggedness = 20` (px zigzag;
  capped at 45% of the width). Paper rip transition.

### 3.5 Print, halftone, pixel, signal

**halftone()** `halftone` · 4.0.467 · WebGL2 · T0
- `shape = 'circle'` | `'square'` | `'line'`, `dotSize = 20` (>= 1), `dotSpacing = dotSize` (>= 1), `rotation = 0`,
  `offsetX = 0`, `offsetY = 0`, `sampling = 'bilinear'` | `'nearest'`, `colorMode = 'solid'` | `'source'`,
  `dotColor = 'red'` (solid only; passing it with `'source'` throws; the old name `color` throws "renamed to dotColor"),
  `invert = false` (true: bright and transparent areas get big dots).
- Output is **only the dots**; between dots is transparent. Transparent source counts as white (no dots). Put a paper
  colored layer behind it for print looks.

**halftoneLinearGradient()** `halftone-linear-gradient` · 4.0.469 · WebGL2 · T0
- `firstStopDotSize = 0`, `secondStopDotSize = 40` (px), `firstStopPosition = [0, 0.5]`, `secondStopPosition = [1, 0.5]`
  (UV, -1..2), `gridSize = 24`, `colorMode = 'solid'`, `dotColor = 'black'`, `maskToSourceAlpha = false` (4.0.474).
- Dot size depends on position, not luminance. Solid mode composites dots over the source; source mode outputs dots only.
  Dot wipes, gradient overlays, pop-art backgrounds.

**dotGrid()** `dot-grid` · 4.0.469 · WebGL2 · T0
- `dotSize = 16` (>= 0), `gridSize = 20` (> 0), `invert = false`. Source visible only inside dots (or only outside with
  `invert`). Grid centered on the canvas. LED wall, perforated mask.

**pixelate()** `pixelate` · 4.0.479 · WebGL2 · T0
- `blockSize = 20` (>= 1). Samples one texel per block (no averaging), so moving footage shimmers; blur first for a
  steadier mosaic.

**linearProgressivePixelate()** `linear-progressive-pixelate` · 4.0.490 · WebGL2 · T0
- `start = [0, 0.5]`, `end = [1, 0.5]`, `startBlockSize = 1`, `endBlockSize = 40` (>= 1). Cross-fades between
  power-of-two grids so block edges stay aligned while the size changes.

**radialProgressivePixelate()** `radial-progressive-pixelate` · 4.0.490 · WebGL2 · T0
- `center = [0.5, 0.5]`, `width = 1`, `height = 1`, `rotation = 0`, `start = 0`, `startBlockSize = 1`,
  `endBlockSize = 40`. Swap the sizes to pixelate the center and keep the outside clear (pixelated face).

**scanlines()** `scanlines` · 4.0.469 · WebGL2 · T0
- `amount = 0.15` (0..1), `spacing = 4` (> 0 px), `thickness = 1` (>= 0, clamped to spacing), `offset = 0` (animate to
  roll), `premultiply = false` (true: effect follows source brightness, subtler). Horizontal only, zero-mean signal
  (lines brighter, gaps darker).

**noise()** `noise` · 4.0.469 · WebGL2 · T0
- `amount = 0.15` (0..1), `seed = 0`, `premultiply = false` (true: grain scales with brightness, film-like). Per-pixel
  static grain until you change `seed`. Use `seed: frame` for moving grain.

**whiteNoise()** `white-noise` · 4.0.470 · WebGL2 · T0
- `amount = 1` (0..1, blend toward random gray), `seed = 0`. TV static, snow, signal loss. Uses a sin-based hash.

**speckle()** `speckle` · 4.0.469 · WebGL2 · T0
- `density = 0.08` (0..1), `size = 4` (>= 0 px), `randomness = 1` (0..1). Small **alpha holes** (what is behind shows
  through). No `seed` param: the layout is fixed; changing `size` changes the cell grid and so reshuffles the holes.

**tvSignalOff()** `tv-signal-off` · 4.0.476 · WebGL2 · T0
- `amount = 1` (0..1). Blends to a color-bars test pattern inside the source alpha.

**outline()** `outline` · 4.0.515 · WebGL2 (+ CPU when simplifying) · T2
- `width = 8` (>= 0 px), `edgeSimplification = 0` (px tolerance; > 0 extracts and simplifies the alpha contour on the CPU
  every frame, making polygonal outlines), `color = white`, `opacity = 1`, `outlineOnly = false` (true: filled silhouette
  mask in the outline color).
- Binary alpha test (any alpha above 0.5/255 counts), 32 directions x 3 rings of samples, so outlines are hard edged.
  Clipped at the canvas edge: leave transparent margin. Place after `colorKey()` for sticker cutouts.

**roughenEdges()** `roughen-edges` · 4.0.487 · WebGL2 · T1
- `amount = 1` (0..1), `border = 26.5` (0..200 px), `scale = 0.07` (0.01..4), `seed = 231.2` (0..1000; throws above).
  Displaces pixels near alpha edges only, so it does nothing on fully opaque full-frame sources. Torn paper, stamp edges.

### 3.6 Texture and material

**paper()** `paper` · 4.0.486 · WebGL2 · T1 (heavy single pass)
- `amount = 1`, `colorFront = '#9fadbc'`, `colorBack = '#ffffff'`, `contrast = 0.3`, `roughness = 0.4`, `fiber = 0.3`,
  `fiberSize = 0.2` (0.01..1), `crumples = 0.3`, `crumpleSize = 0.35` (0.01..1), `folds = 0.65`, `foldCount = 5`
  (0..15), `drops = 0.2`, `fade = 0`, `seed = 6` (0..1000), `scale = 0.6` (0.01..4). Unit params are 0..1.
- Grain, fibers, crumples, folds and speckles; slightly displaces the source. Adapted from Paper Shaders (Apache-2.0).
  A new `seed` re-uploads a 256x256 noise texture.

**burlap()** `burlap` · 4.0.478 · WebGL2 · T1
- `amount = 0.55`, `size = 5` (> 0 px), `roughness = 0.7`, `seed = 0`, `color = '#000000'` (alpha = fiber strength).
  Woven sack texture that keeps source colors.

**flannel()** `flannel` · 4.0.491 · WebGL2 · T0
- `amount = 0.7`, `size = 96` (> 0 px per plaid repeat), `softness = 0.18`, `baseColor = '#c92f3d'`,
  `stripeColor = '#241015'` (alpha = stripe coverage). Plaid is shaded by source luminance; meant for a `<Solid>`.

**shrinkwrap()** `shrinkwrap` · 4.0.479 · WebGL2 · T1
- `amount = 1`, `displacement = 5` (>= 0 px), `highlightIntensity = 0.75` (>= 0), `wrinkleDensity = 0.42`,
  `edgeTension = 0.45`, `phase = 0` (animate for drifting wrinkles), `seed = 0`. Glossy plastic wrap on labels, stickers.

**emboss()** `emboss` · 4.0.479 · WebGL2 · T1
- `amount = 0.7`, `size = 26` (> 0 px cell), `lineWidth = 7` (> 0), `depth = 0.75`, `angle = 0`, `lightAngle = 135`,
  `offset = 0` (animate to scroll).
- **Procedural raised-dash relief** (tread plate / quilted pattern) shaded over the source. It is not a classic
  "emboss the image edges" filter.

### 3.7 Pattern generators and backgrounds

The line family (`lines`, `rings`, `waves`, `zigzag`, `checkerboard`) shares: `colors = ['#dff4ff', '#7cc6ff']` (>= 2 CSS
colors, cyclic, `'transparent'` allowed, not keyframable in Studio), `gap = 0` (transparent band), `maskToSourceAlpha =
false` (4.0.474; checkerboard since its release). Stripes are composited over the source with **hard, non-antialiased
edges**, so rotated stripes stair-step; keep angles at 0/90 or add `blur({radius: 1})` after.

- **lines()** `lines` · 4.0.470 · T0: `direction = 'horizontal'`, `thickness = 40` (> 0), `angle = 0`, `offset = 0`.
- **rings()** `rings` · 4.0.471 · T0: `center = [0.5, 0.5]`, `thickness = 40`, `offset = 0` (animate to expand).
- **waves()** `waves` · 4.0.471 · T0: `direction`, `thickness = 40`, `angle = 0`, `offset = 0`, `amplitude = 24`,
  `wavelength = 160` (> 0), `phase = 0` (**degrees**, moves the wave shape without scrolling bands).
- **zigzag()** `zigzag` · 4.0.471 · T0: like waves with triangular turns, `amplitude = 40`, `wavelength = 160`, no phase.
- **checkerboard()** `checkerboard` · 4.0.480 · T0: `cellSize = 80` (> 0), `angle = 0`, `offsetX = 0`, `offsetY = 0`.
  With 3+ colors it makes diagonal color bands rather than a checker.

**gridlines()** `gridlines` · 4.0.476 · WebGL2 · T0
- `gridSize = 64` (> 0), `lineWidth = 2` (>= 0 screen px), `lineColor = '#ffffff'`, `backgroundColor = 'transparent'`,
  `rotation = 0`, `rotationX = 0`, `rotationY = 0` (degrees), `perspective = 0` (px; > 0 = 3D plane), `offsetX = 0`,
  `offsetY = 0`, `maskToSourceAlpha = false`. Anti-aliased, fades lines near the horizon. Blueprint, UI guides,
  synthwave floor.

**contourLines()** `contour-lines` · 4.0.476 · WebGL2 · T1
- `lineColor = '#ffffff'`, `lineWidth = 1.5`, `spacing = 36`, `scale = 220` (all > 0), `complexity = 0.65`,
  `smoothness = 0.55`, `seed = 0`, `offsetX = 0`, `offsetY = 0`, `opacity = 1`, `maskToSourceAlpha = false`.
  Anti-aliased topographic linework over the source.

**liquidContours()** `liquid-contours` · 4.0.491 · WebGL2 · T1
- `firstColor = '#ff1a0a'`, `secondColor = '#050505'`, `spacing = 62`, `scale = 300` (> 0), `complexity = 0`,
  `smoothness = 1`, `seed = 4`, `offsetX = 13.4`, `offsetY = 0`, `phase = 3.23`. Replaces the source with flowing two-color
  bands. `phase` is in band cycles: adding exactly 1.0 returns the same image, so it loops perfectly.

**linearGradient()** `linear-gradient` · 4.0.483 · WebGL2 · T0
- `start = [0, 0.5]`, `end = [1, 0.5]`, `startColor = '#000000'`, `endColor = '#ffffff'`. Replaces the source; colors with
  alpha let lower layers show through. Interpolated in sRGB, 8-bit (add a touch of `noise` to dither banding).

**starburst()** `starburst` · 4.0.500 · WebGL2 · T0
- `rays` **required** (2..100), `colors` **required** (>= 2; alpha is dropped, so `'transparent'` becomes black),
  `rotation = 0` (degrees), `smoothness = 0` (0..1, 0 = hard aliased edges), `origin = [0.5, 0.5]` (0..1, RangeError
  outside). Fully opaque, replaces the source. Aspect corrected rays.

### 3.8 Light, glow, shadow

**glow()** `glow` · 4.0.468 · WebGL2 · T2 (4 passes)
- `radius = 20` (>= 0 px), `intensity = 1` (>= 0), `threshold = 0` (0..1 luminance), `color = white`.
- The halo is **monochrome** (`color`, not the source colors) and **added** on top (clamped). Neon, bloom on highlights,
  emissive UI. Raise `threshold` on footage to glow only highlights.

**dropShadow()** `drop-shadow` · 4.0.469 · WebGL2 · T2 (4 passes)
- `radius = 12` (>= 0), `offsetX = 8`, `offsetY = 8` (px), `opacity = 0.5` (0..1), `color = black`. Shadow from the alpha,
  drawn behind; clipped at the canvas edge (leave margin inside the component).

**lightTrail()** `light-trail` · 4.0.476 · WebGL2 · T2 (samples)
- `direction = 180` (degrees), `distance = 80` (>= 0 px), `intensity = 1` (>= 0), `decay = 0.9` (0..1),
  `threshold = 0` (0..1), `samples = 32` (integer 1..64), `color = white`. Additive, monochrome.
- A pixel contributes by max(alpha, luminance), so **every opaque pixel contributes at full strength regardless of
  threshold**. Use it on alpha-isolated subjects (logo PNG, text in `<HtmlInCanvas>`), not on full-frame video.

**shine()** `shine` · 4.0.468 · WebGL2 · T0
- `progress = 0.5` (0..1, band enters at 0, leaves at 1), `angle = 30` (0 moves right, 90 up), `haloSigma = 200`,
  `coreSigma = 65` (> 0 px), `haloIntensity = 0.3`, `coreIntensity = 0.4` (0..1). White sweep masked by alpha.

**lightLeak()** `light-leak` · 4.0.500 · WebGL2 · T1
- `seed = 0`, `hueShift = 0` (0..360; throws outside; 0 yellow-orange, 120 green, 240 blue), `progress = 0.5` (0..1).
  Reveals during the first half, retracts during the second. Composited with normal alpha over the source (not screen).

**vignette()** `vignette` · 4.0.468 · WebGL2 · T0
- `amount = 0.5`, `radius = 0.65`, `feather = 0.35` (0 = hard), `roundness = 1` (0 rectangular .. 1 elliptical), all
  0..1; `center = [0.5, 0.5]` (any finite); `color = '#000000'`; `mode = 'color'` (paints color into edges, including over
  transparent areas) or `'alpha'` (fades edges to transparent). Computed in UV so it follows the frame's aspect.

### 3.9 Reveals and transitions

**evolve()** `evolve` · 4.0.470 · WebGL2 · T0
- `progress = 0.5` (0 hidden .. 1 revealed, 0..1 validated), `direction = 'left'` | `'right'` | `'top'` | `'bottom'` (the
  side it reveals from), `feather = 0.1` (0..1; the soft band sits ahead of the edge). Wipes and build-ons.

**venetianBlinds()** `venetian-blinds` · 4.0.485 · WebGL2 · T0
- `progress = 0.5` (0..1), `direction = 'vertical'` (vertical slats across X) or `'horizontal'`, `slats = 12` (integer
  >= 1). Each slat opens from its center; hard edges.

**pixelDissolve()** `pixel-dissolve` · 4.0.471 · WebGL2 · T0
- `progress = 0.5` (**0 = fully visible, 1 = fully gone**), `columns = 10`, `rows = 10` (integers >= 1), `seed = 0`,
  `feather = 0.15` (0..1). Opposite direction from evolve: for a dissolve-in pass `1 - t`.

`tear()` (3.4) and `lightLeak()` (3.8) also work as transitions.

### 3.10 `@remotion/light-leaks` (deprecated, available since 4.0.415)

- `<LightLeak durationInFrames? seed? hueShift? ...SequenceProps>`: a `<Sequence>` (all Sequence props except `children`
  and `layout`) that renders a **WebGL1** transparent canvas the size of the composition. It reveals during the first half
  of `durationInFrames` (defaults to the parent duration) and retracts in the second. `seed` finite, `hueShift` 0..360
  (RangeError). Accepts `style`, so `mixBlendMode: 'screen'` works; it overlays any DOM, unlike the effect, which needs a
  canvas-based host. `supportsEffects: false`.
- `lightLeak()` from `@remotion/light-leaks` (4.0.468) is a re-export of `@remotion/effects/light-leak`.
- Migration: use `lightLeak()` from `@remotion/effects/light-leak` on a `<Solid>` (4.0.500+). The component will not move.

### 3.11 `@remotion/starburst` (deprecated, available since 4.0.435)

- `<Starburst rays colors rotation? smoothness? vignette? originOffsetX? originOffsetY? ...SequenceProps>`: WebGL1 canvas
  in a Sequence. `rays` 2..100, `colors` >= 2, `rotation = 0`, `smoothness = 0` (0..1), `vignette = 1` (1 = opaque, 0 =
  fully transparent, between = circular fade), `originOffsetX/Y = 0` (-1..1 per docs; the shader adds them raw to the
  0.5 center, so +/-0.5 already reaches an edge; verify visually).
- `starburst()` from `@remotion/starburst` (4.0.468) re-exports the effect. The effect has no `vignette`: pair it with
  `vignette({mode: 'alpha'})` to get the old fade.

### 3.12 `@remotion/motion-blur`

**`<CameraMotionBlur shutterAngle? samples?>`** (3.2.39): `shutterAngle = 180` (0..360), `samples = 10` (integer >= 0;
recommended 5 to 10). Renders `samples` copies of the children, each `<Freeze>`d at a fractional frame between the current
frame and the next, stacked with `mix-blend-mode: plus-lighter` and `filter: opacity(1/N)` in an isolated layer. Near
frame 0 it reduces samples. Costs N times the children's render; 8-bit per-layer opacity darkens and bands colors
("destructive to colors", keep samples low). Children must be absolutely positioned (`<AbsoluteFill>`). Not supported by
the default client-side renderer (mix-blend-mode).

**`<Trail layers lagInFrames trailOpacity>`** (3.2.39, formerly `<MotionBlur>`, `trailOpacity` formerly
`blurOpacity`): all three props required. `layers` integer >= 0, `lagInFrames` any number (fractional OK; echo k is
frozen at `frame - lagInFrames * k`), `trailOpacity` = the peak echo opacity (the nearest echo gets
`trailOpacity * (1 - 1/layers)`, fading linearly to 0 for the oldest). Renders the `layers` echoes behind plus the live
children on top. Stylized echo, not a camera blur. Early frames freeze children at negative frames.

**`<HtmlInCanvasMotionBlur width height samples? shutterAngle? from? durationInFrames? trimBefore? playbackRate?>`**
(**4.0.529, not in 4.0.528**, experimental): samples default 8 (1..64), shutter centered on the frame, averaged with
`lighter` compositing in a canvas; needs HTML-in-canvas for preview; no nesting of HTML-in-canvas.

**Common mistake (all three):** they override the time context of their children. `useCurrentFrame()` must be called
inside a child component rendered within the wrapper; a frame read outside and passed down produces no blur.

### 3.13 `@remotion/noise`

- `noise2D(seed, x, y)`, `noise3D(seed, x, y, z)`, `noise4D(seed, x, y, z, w)` return -1..1 simplex noise, deterministic
  for the same seed and coordinates. `seed` is a string or number. Uses `simplex-noise` with Remotion's `random(seed)`.
- Each seed builds a permutation table once; the cache keeps about 10 seeds per dimension (FIFO). Many distinct seeds per
  frame thrash the cache: use one seed and put the index in a coordinate, for example `noise2D('float', frame / 100, i)`.
- Works everywhere (browser, Node, Lambda, client rendering). The pages carry no "available from" tag (long-standing
  package, fine on 4.0.528). Values vary smoothly: divide `frame` by 10 for jitter, by 100 for slow drift.

### 3.14 `@remotion/canvas` (experimental editor toolkit, 4.0.527)

- `<Canvas controller showOutlines? resolveSequenceNodePathInfo? ...PlayerProps>`: a `<Player>` that registers its timeline
  tracks into a controller and can draw hover/selection outlines (`showOutlines`, default false; Shift = range,
  Cmd/Ctrl = toggle, Escape or empty click clears). Forwards its ref to the Player.
- `createCanvasController()` / `useCanvasController()`: on **4.0.528** the controller is `{timeline, selection, hover}`
  only (verified in the installed typings). `timeline` is an external store of `TimelineTrackData[]`
  (`subscribe`/`getSnapshot`, use with `useSyncExternalStore`).
- `createCanvasSelectionController()` (`select(item, {shiftKey, toggleKey}, allItems)`, `setSelectedItems`,
  `setSnapshot`, `clear`), `createCanvasHoverController()` (`setHoveredSequence`, `clear('canvas'|'timeline'|null)`),
  `useCanvasSelection(controller.selection)`, `useCanvasHover(controller.hover)`,
  `useCanvasSequenceHover(hover, nodePathInfo, 'timeline'|'canvas')` (returns `{hovered, onPointerEnter,
  onPointerLeave}`), `getCanvasSelectionItemKey(item)` (opaque identity string), `getCanvasSequenceNodePathInfo(track)`.
- Return shapes: `useCanvasSelection` gives `{selectedItems, anchor}` (items are a union with `type`: `'sequence'` plus
  property, effect, keyframe, easing segment and guide variants); `useCanvasHover` gives `{key, nodePathKey, source}` or
  `null`; `getCanvasSequenceNodePathInfo` gives `{sequenceSubscriptionKey, auxiliaryKeys, index,
  numberOfSequencesWithThisNodePath, supportsEffects}`, falling back to the mounted sequence id (not stable across
  remounts) when no source identity is registered.
- **4.0.529 only (not usable on 4.0.528):** `track.sequence.controls`, `controller.setSequenceNodePaths()`,
  `controller.overrides.set/clear` (preview prop values without editing source), `getCanvasSequenceSourceLocation()`
  (needs `createBrowserBundler` with `enableFastRefresh`).
- Relevance to video making: low. It is for building Studio-like editors. Do not confuse with canvas drawing.

### 3.15 `@remotion/skia`

- `enableSkia(webpackConfig)` from `@remotion/skia/enable`, used as
  `Config.overrideWebpackConfig((c) => enableSkia(c))` in `remotion.config.ts` (spread other changes reducer-style). Runs
  at bundle time. (Before 3.3.39 the method was `Config.Bundling.overrideWebpackConfig`.)
- `<SkiaCanvas width height ...RNSkiaCanvasProps>` wraps React Native Skia's `<Canvas>` with Remotion contexts; put
  `@shopify/react-native-skia` elements inside. Uses WebGL, so enable `--gl=angle` on 4.x renders. Full setup page is
  `/docs/skia` (D2).

### 3.16 Canvas Capture

- A Chrome extension (Apple Silicon Macs only) for recording a web page through the HTML-in-canvas API. Install =
  clone `remotion-dev/canvas-capture` to `~/Applications/...`, run its script to install Chrome for Testing
  150.0.7842.0 (r1631007), which gets no security updates, enable "Canvas Draw Element" in `chrome://flags`, load the
  extension unpacked. A skill may describe it; it must not install it for the user without explicit consent.

### 3.17 `@remotion/animation-utils`

No "available from" tags on these pages (long-standing package); per-segment easing arrays and `posterize` depend on
the core `interpolate()` of the installed version, and both exist in 4.0.528.

**`interpolateStyles(input, inputRange, outputStylesRange, options?)`** returns a React style object.
- `inputRange`: >= 2 strictly increasing finite numbers; `outputStylesRange`: same length, style objects.
- `options`: same keys as `interpolate()`: `easing` (function or per-segment array), `extrapolateLeft/Right`
  (**default `'extend'`**, so pass `'clamp'` for opacity and friends), `posterize` (floor the input to a step). All
  available on 4.0.528.
- Behavior (from source): only keys present in the segment's **start** style are output; a key missing in the end style
  holds its start value; a key that exists only in the end style is dropped. Numbers keep numbers. Strings are split into
  tokens; units must match unless one side is 0; function values (`translateX(...) scale(...)`) must have the same
  functions in the same order; colors (hex, named, rgb/rgba, hsl/hsla, oklch/oklab/lab/lch/hwb) go through
  `interpolateColors`, which **ignores easing** (linear).
- Throws: "must be of the same type", "must have the same structure", "units ... must match", "Non-animatable values".
  Numbers must be written like `0.5` (not `.5` or `+5px`). Space-separated arguments inside a function
  (`drop-shadow(0 0 10px #fff)`) cannot be interpolated; top-level space-separated values (`box-shadow`, `padding`) can.

```tsx
const style = interpolateStyles(frame, [0, 20, 40], [
  {opacity: 0, transform: makeTransform([translateY(40), scale(0.9)])},
  {opacity: 1, transform: makeTransform([translateY(0), scale(1)])},
  {opacity: 0, transform: makeTransform([translateY(-40), scale(1.05)])},
], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.bezier(0.2, 0, 0, 1)});
```

**`makeTransform(transforms: string[])`** joins helper outputs with spaces. Helpers (validate finite numbers, throw on bad
signatures): `matrix(a,b,c,d,tx,ty)`, `matrix3d(16 numbers)`, `perspective(n, unit='px' | '100px')`,
`rotate/rotateX/rotateY/rotateZ(n, unit='deg' | '1rad')`, `rotate3d(x, y, z, angle, unit?)`, `scale(x, y=x)` (outputs
`scale(x, y)`), `scale3d`, `scaleX/Y/Z`, `skew(a)` (both axes), `skew(ax, ay)`, `skew(a, 'rad')`,
`skew(ax, ux, ay, uy)`, `skewX/skewY(n, unit?)`, `translate(10)`, `translate(10, 20)`, `translate(10, '%')`,
`translate(0, '%', 10, '%')`, `translate('10px', '30%')`, `translate3d(x, y, z)` (numbers get px) or the 6-arg form,
`translateX/Y/Z(n, unit='px' | '12rem')`. Doc typos: `rotateX(1, 'rad')` returns `rotateX(1rad)` (page says 45rad),
`translate('10px', '30%')` returns `translate(10px, 30%)` (page says 20%); the tests confirm the source behavior.

---

## 4. Recipes

All snippets assume `const frame = useCurrentFrame();` and `{width, height, durationInFrames} = useVideoConfig()`.
`clamp` means `{extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}`. Keep `interpolate()` calls inline inside the
effect call so Studio can keyframe them.

### 4.1 Look to effects decision table

| Look | Core stack (in order) | Notes |
|---|---|---|
| Cinematic grade | `colorCorrection` then `vignette` then `noise(premultiply)` | One grade pass beats chaining. |
| Film print / vintage | `colorCorrection` (blacks above 0, contrast and saturation below 1, temperature above 0), `noise({seed: frame})`, `vignette`, occasional `lightLeak` | Or a `.cube` via `lut()`. See 4.3. |
| 8mm/16mm dust | above + `speckle` over a light backdrop | Speckle holes show the layer behind. |
| VHS / CRT | `chromaticAberration`, `scanlines(offset: frame)`, `noise`, `barrelDistortion`, `vignette` | Barrel after scanlines curves them. |
| Glitch hit | spike `chromaticAberration.amount`, flip `angle` every 2 frames, `xyTranslate` jitter, short `pixelate` or `whiteNoise` burst | Few frames only. |
| TV off / no signal | `tvSignalOff`, `whiteNoise`, CSS scaleY collapse | See 4.9. |
| Neon / bloom | `glow({threshold, color})` (+ `lightTrail` for motion) | Glow is monochrome. |
| Halftone comic | `halftone({colorMode: 'source'})` or solid dots over a paper `<Solid>` | Halftone drops the source. |
| Newspaper | `grayscale`, `halftone({dotColor: '#111'})` over off-white + `paper` | |
| Risograph 2-color | `thermalVision({palette: [ink, paper]})` + `noise` + tiny `chromaticAberration` | Smooth gradient map. |
| Hard stencil duotone | `duotone({darkColor, lightColor, threshold})` | 1-bit look. |
| Paper cutout / collage | alpha subject: `roughenEdges`, `dropShadow`; background `<Solid>` + `paper` | |
| Fabric | `<Solid>` + `burlap` or `flannel` | |
| Plastic sticker | `shrinkwrap({phase: frame * 0.05})` + `shine` sweep | |
| Thermal cam | `thermalVision()` + `scanlines` + `noise` | |
| Blueprint / tech | `<Solid>` + two `gridlines` (fine and coarse) | |
| Synthwave | `gridlines({rotationX: -68, perspective: 900, offsetY: frame*k})` + `glow`; `starburst` or `linearGradient` sky | |
| Retro sunburst | `<Solid>` + `starburst({rotation: frame*0.5})` + `vignette` + `noise` | |
| Topographic | `<Solid>` + `contourLines({offsetX: frame*0.3})` | |
| Liquid bands loop | `liquidContours({phase: base + frame/durationInFrames})` | Integer phase change = seamless loop. |
| Tilt shift | `radialProgressiveBlur` wide flat ellipse or two `linearProgressiveBlur`, + `saturation(1.3)` | |
| Rack focus | animate `blur.radius` on background vs foreground layers | |
| Anonymize | `regionBlur` with tuple-interpolated corners, or `radialProgressivePixelate` with swapped sizes | |
| Greenscreen | `colorKey`, then `outline`, then `dropShadow` | Order matters. |
| Screen replacement | `cornerPin` on `<HtmlInCanvas pixelDensity={2}>` or `<Video>` | |
| Speed / impact | `zoomBlur({amount: 80 to 0})`, `lightTrail` on isolated logos | |
| Lens | `fisheye`, `barrelDistortion` | |
| Wallpaper | `pattern` (brick with `rowOffsetEvery: 2`), `tile` after `scale` | |
| Symmetry | `mirror` horizontal + `mirror` vertical | |

### 4.2 Cinematic grade with living grain

```tsx
<Video src={src} effects={[
  colorCorrection({exposure: 0.1, contrast: 1.12, shadows: 0.15, highlights: -0.2,
    temperature: 0.1, saturation: 0.92, vibrance: 0.15}),
  vignette({amount: 0.35, radius: 0.7, feather: 0.45}),
  noise({amount: 0.05, seed: frame, premultiply: true}),
]} />
```
Grain last so it is not blurred or graded. `premultiply: true` keeps shadows clean like real film.

### 4.3 Vintage film print

`colorCorrection({blacks: 0.6, contrast: 0.9, saturation: 0.75, temperature: 0.25, tint: 0.05})`, then
`noise({amount: 0.1, seed: frame})`, then `vignette({amount: 0.55, radius: 0.6, feather: 0.5, color: '#1a0f05'})`.
For dust: put the footage over a warm off-white `<AbsoluteFill>` and add `speckle({density: 0.02, size: 3 +
(frame % 3) * 0.4})` (changing `size` reshuffles the holes, giving flicker). Punctuate cuts with a `lightLeak` overlay.

### 4.4 CRT / VHS

```tsx
<HtmlInCanvas width={width} height={height} effects={[
  chromaticAberration({amount: 3 + Math.abs(Math.sin(frame * 2.7)) * 3}),
  scanlines({amount: 0.3, spacing: 5, thickness: 2, offset: frame * 3, premultiply: true}),
  noise({amount: 0.12, seed: frame}),
  barrelDistortion({amount: 0.12}),
  vignette({amount: 0.5, radius: 0.6, feather: 0.4}),
]}>{children}</HtmlInCanvas>
```
Wrapping the whole scene in one `<HtmlInCanvas>` gives a "master" look with one pair of GL contexts
(pattern from `jonnys-videos/.../MasterWithEffect.tsx`).

### 4.5 Glitch burst (frames g0..g0+8)

- `chromaticAberration({amount: interpolate(frame, [g0, g0+2, g0+8], [0, 30, 0], clamp), angle: frame % 4 < 2 ? 0 : 180})`
- `xyTranslate({x: noise2D('glx', frame, 0) * 20})` and `pixelate({blockSize: frame % 3 === 0 ? 12 : 1})`
- Optional `whiteNoise({amount: 0.15, seed: frame})`. Remove the effects outside the burst (or use `disabled`).

### 4.6 Neon title and speed logo

```tsx
<HtmlInCanvas width={width} height={height} pixelDensity={2} effects={[
  glow({radius: 24, intensity: 1.6, threshold: 0.2, color: '#00e5ff'}),
]}>{/* white or light-colored text on transparent */}</HtmlInCanvas>
```
Speed logo (transparent PNG): `lightTrail({direction: 180, distance: 120, intensity: 1.6, decay: 0.9, color:
'#ffb000'})`, then `glow`, then `chromaticAberration` (the docs' suggested trio). Scale px params by `pixelDensity`.

### 4.7 Print looks

- Comic dots in the source colors: `halftone({shape: 'circle', dotSize: 12, dotSpacing: 12, rotation: 15, colorMode:
  'source'})` with a cream `<Solid color="#f6ecd6">` plus `paper()` underneath.
- Newspaper: `grayscale()`, `halftone({dotSize: 8, dotColor: '#161616', rotation: 45})` over off-white.
- Gradient-map duotone (smooth): `thermalVision({palette: ['#1b1f3b', '#ff7a59']})`; tritone: 3 colors.
- Stencil duotone: `duotone({darkColor: '#101820', lightColor: '#f2aa4c', threshold: 0.45})`.
- Dot wipe: animate `halftoneLinearGradient` stops or dot sizes with `progress`.

### 4.8 Reveals and transitions

- Wipe: `evolve({progress: interpolate(frame, [0, 30], [0, 1], clamp), direction: 'left', feather: 0.18})`.
- Blinds: `venetianBlinds({progress: ..., direction: 'vertical', slats: 14})`.
- Dissolve in: `pixelDissolve({progress: 1 - t, columns: 16, rows: 9, feather: 0.2})` (progress 1 = gone).
- Paper rip out: `tear({progress: interpolate(frame, [0, 45], [0, 1.6], {extrapolateLeft: 'clamp'}), rotation: 20,
  jaggedness: 24})` (above 1 the halves fly apart).
- Light leak over a cut (4.0.500+):

```tsx
<TransitionSeries.Overlay durationInFrames={30}>
  <Solid width={width} height={height} effects={[lightLeak({seed: 3, hueShift: 30,
    progress: interpolate(frame, [0, durationInFrames - 1], [0, 1], clamp)})]} />
</TransitionSeries.Overlay>
```
Inside the Overlay, `useVideoConfig().durationInFrames` is the overlay's length. The transparent `<Solid>` makes it an
overlay. For additive/screen light on arbitrary DOM, the deprecated `<LightLeak>` with `style={{mixBlendMode:
'screen'}}` also works on 4.0.528.

### 4.9 TV power-off outro (from `MasterWithEffect.tsx`)

Ramp `scanlines.amount` 0 to 0.58, spike `chromaticAberration.amount` with a per-frame sine flicker and alternating angle,
`noise({seed: frame})`, then collapse the wrapper with CSS `scale: "1 0.012"` followed by `"0 0.012"` while a radial white
glow `<AbsoluteFill>` flashes and shrinks. End with a black frame.

### 4.10 Backgrounds

- Sunburst: `<Solid width height effects={[starburst({rays: 24, colors: ['#ffcc00', '#ff9900'], rotation: frame *
  0.4, smoothness: 0.05}), vignette({amount: 0.4}), noise({amount: 0.03})]} />`.
- Synthwave floor: dark `<Solid>` + `gridlines({gridSize: 72, lineWidth: 3, lineColor: '#ff4fd8', rotationX: -68,
  perspective: 900, offsetY: frame * 4})` + `glow({radius: 16, color: '#ff4fd8'})`.
- Blueprint: `<Solid color="#0b2545">` + `gridlines({gridSize: 24, lineWidth: 1, lineColor: 'rgba(255,255,255,0.12)'})`
  + `gridlines({gridSize: 120, lineWidth: 2, lineColor: 'rgba(255,255,255,0.3)'})`.
- Grid with a mask edge: a transparent `<Solid color="rgba(24,24,24,0)">` + `gridlines(...)` + `evolve({direction:
  'bottom', progress: 0.86, feather: 0})` + `scale({scale: 1.4})` (from `brand/src/effects/Goal.tsx`).
- Topographic: `contourLines({lineColor: 'rgba(255,255,255,0.35)', spacing: 28, scale: 260, offsetX: frame * 0.3})`.
- Seamless liquid loop over the whole comp: `liquidContours({phase: 3.23 + frame / durationInFrames})`.
- Gradient: `linearGradient({start: [0, 0], end: [1, 1], startColor, endColor})` then `noise({amount: 0.02})` to dither.
- Rings pulse: `rings({colors: ['#9fd6ff', 'transparent'], thickness: 40, offset: frame * 2})` (with `transparent` in the
  palette the source shows between rings).

### 4.11 Greenscreen sticker

```tsx
<Video src={src} effects={[
  colorKey({keyColor: '#00ff00', similarity: 0.4, smoothness: 0.05, spillSuppression: 0.8}),
  outline({width: 12, color: '#ffffff'}),
  dropShadow({radius: 20, offsetX: 0, offsetY: 12, opacity: 0.4}),
]} />
```

### 4.12 Screen replacement / billboard

Render the screen content in `<HtmlInCanvas width={2400} height={700} pixelDensity={2} effects={[cornerPin({topLeft:
[0.15, 0.17], topRight: [0.63, 0.21], bottomRight: [0.63, 0.76], bottomLeft: [0.15, 0.73]})]}>` over the photo, then
position it with CSS `scale`/`translate` (`brand/src/effects/experiments/BillboardForeground.tsx`). Animate corners
with tuple `interpolate()` (4.0.528 supports tuple output ranges).

### 4.13 Anonymization

`regionBlur({topLeft: interpolate(frame, [0, 60], [[0.30, 0.20], [0.42, 0.22]], clamp), bottomRight:
interpolate(frame, [0, 60], [[0.50, 0.55], [0.62, 0.57]], clamp), blurRadius: 60, feather: 8, roundness: 1})`.
Pixelated variant: `radialProgressivePixelate({center, width: 0.2, height: 0.3, start: 0.85, startBlockSize: 24,
endBlockSize: 1})`. Keep `topLeft` strictly above/left of `bottomRight` on every frame.

### 4.14 Focus and depth

- Tilt shift: `radialProgressiveBlur({center: [0.5, 0.55], width: 2.2, height: 0.5, start: 0.35, endBlur: 30})` +
  `saturation({amount: 1.3})`.
- Newsprint scan (from `brand/src/effects/NewsHeadline.tsx`): `noise({amount: 0.39, premultiply: true})`, two
  `linearProgressiveBlur` with diagonal stops, `vignette({radius: 0.84, amount: 0.46, color: '#030013'})`.

### 4.15 Procedural motion with `@remotion/noise`

- Camera shake: `translate: ${noise2D('shake', frame / 10, 0) * 10 * k}px ${noise2D('shake', frame / 10, 5) *
  10 * k}px`, rotation `noise2D('shake', frame / 10, 9) * 0.02 * k` rad.
- Idle float: `noise2D('float', frame / 100, i) * 10` px per element i (one seed, index in a coordinate).
- Flicker: `opacity: 0.7 + ((noise2D('flicker', frame / 15, i) + 1) / 2) * 0.3`.
- Drive effect params too: `noiseDisplacement({seed: Math.floor(frame / 2), ...})`,
  `chromaticAberration({amount: 4 + noise2D('ca', frame / 8, 0) * 3})`.

### 4.16 Motion blur on 4.0.528

- Realistic: wrap the moving part in `<CameraMotionBlur shutterAngle={180} samples={6}>` with `useCurrentFrame()` inside
  a child component. Check colors on a still; drop to 4 to 6 samples if banding shows.
- Stylized echo: `<Trail layers={6} lagInFrames={0.5} trailOpacity={0.6}>`.
- Cheap directional smear on a single element moving along X (or Y): `blur({radius: speedPx * 0.3, vertical: false})`,
  with `speedPx` = the per-frame distance computed from the same `interpolate()` that moves it. Axis-aligned motion only
  (blur has no angle), canvas-based element required. This is our own recipe, not from the docs.
- `<HtmlInCanvasMotionBlur>` needs 4.0.529+: only after an upgrade.

### 4.17 LUT from a file

```tsx
const [cube, setCube] = useState<string | null>(null);
const [handle] = useState(() => delayRender('Load LUT'));
useEffect(() => { fetch(staticFile('grade.cube')).then((r) => r.text())
  .then((t) => { setCube(t); continueRender(handle); }); }, [handle]);
<Video src={src} effects={cube ? [lut({content: cube})] : []} />
```
Or fetch it in `calculateMetadata()` and pass the text as a prop. Default Remotion webpack does not import `.cube` as
text without a config change.

---

## 5. Performance and render stability

**Cost ranking** (relative, from shader reading; measure on a still before a long render):

- Cheap: `ctx.filter` effects (`hue`, `saturation`, `grayscale`, `invert`), `tint`, `scale`, `translate`, and every T0
  WebGL effect (single pass, few reads).
- Moderate: procedural single passes (`burlap`, `emboss`, `contourLines`, `liquidContours`, `shrinkwrap`,
  `roughenEdges`, `lightLeak`, `pattern`), `paper` (heaviest single pass).
- Heavy: `blur`, `linearProgressiveBlur`, `radialProgressiveBlur` (2 passes, up to 65 taps each), `regionBlur` (3 passes),
  `glow` and `dropShadow` (4 passes each), `zoomBlur` and `lightTrail` (up to 64 samples), `noiseDisplacement` (up to
  108 reads inside its circle), `outline` (96 reads per pixel).
- CPU per frame: `brightness`, `contrast` (full-frame `getImageData` + JS loop), `tile` (readback + bounds scan),
  `outline({edgeSimplification > 0})` (contour extraction). Replace brightness/contrast with `exposure`/`levels`/
  `colorCorrection` on video.
- `pixelDensity` multiplies pixel count quadratically (2 = 4x shader work and 4x larger texture uploads per effect).

**Structural costs:**

- Each component with WebGL effects owns 2 WebGL2 contexts plus its own texture uploads. Browsers cap live WebGL contexts
  (Chrome drops the oldest when about 16 are alive); dozens of effect-bearing components mounted at once risk context
  loss. Prefer one wrapper (`<HtmlInCanvas>` or one `<Solid>`) carrying a shared stack over the same effect on many
  small components, and premount/unmount effect layers with `<Sequence>` so they are not all alive at once. (The context
  cap is general browser knowledge, not stated in the docs; see open questions.)
- Keep effect components at a constant pixel size. Changing `width`/`height`/`pixelDensity` rebuilds the chain and its
  GL contexts. Animate size with CSS `scale`/`translate` on the component instead.
- Group same-backend effects: a 2D effect between two WebGL effects forces two bridges (one of them async
  `createImageBitmap`).
- Static params cost nothing after the first frame on `<Solid>` (the chain re-runs only when params change). Animated
  params re-run the whole chain every frame.

**Determinism:**

- All effects are pure functions of params and source pixels; the procedural ones hash with the seed and pixel
  coordinates. Parallel chunked rendering is safe as long as params derive from `frame` only.
- `whiteNoise` uses a `sin()`-based hash, whose low bits can differ between GPU backends/drivers. Preview and render, or
  local and Lambda, may show different static; within one render it is stable. The other procedural effects use
  `fract()`-based hashes, which are more portable.
- `<Solid>` holds a `delayRender` until the chain finishes and cancels the render on errors. `<LightLeak>` and
  `<Starburst>` hold a `delayRender` until GL init and call `cancelRender` if WebGL is missing.

**Quality:**

- 8-bit RGBA between effects, sRGB interpolation for gradients. Heavy grades, big blurs and wide gradients band. Use one
  `colorCorrection` instead of several color effects, and finish with `noise({amount: 0.02 to 0.04})` to dither.
- Stripe/ray patterns (`lines`, `rings`, `waves`, `zigzag`, `checkerboard`, `starburst` with `smoothness: 0`,
  `venetianBlinds`, `outline`) have aliased edges. Use `smoothness > 0` for starburst, angles of 0/90 for stripes, or a
  1 px blur after.
- `pixelate` point-samples: moving video shimmers; blur slightly first.
- `wave`, `blur` clamp at edges (smear border pixels); `barrelDistortion`, `fisheye`, `cornerPin`, `skew`, `scale`,
  `translate`, `tear` leave transparent areas: put a background behind or overscan.
- Motion blur components: `<CameraMotionBlur>` and `<Trail>` render N copies of the subtree (CPU and memory scale with N);
  `<Freeze>` at fractional frames means children must tolerate non-integer frames (index lookups, video seeking).

**Lambda / servers:** WebGL on Lambda needs the GL flag and enough memory. On "WebGL context was lost" lower concurrency
or raise memory; test with a still render first.

---

## 6. Errors and fixes

| Symptom / message | Cause | Fix |
|---|---|---|
| `Failed to acquire WebGL2 context for <effect>. Pass --gl=angle ...` | GL disabled in the render browser | `--gl=angle`, `Config.setChromiumOpenGlRenderer('angle')`, `chromiumOptions: {gl: 'angle'}`, or Studio render setting "OpenGL render backend: angle". |
| `WebGL context was lost during canvas effect rendering ...` | Memory or context pressure (Lambda, many components) | Reduce concurrency, raise memory, fewer simultaneous WebGL effect components, lower `pixelDensity`. |
| `"progress" must be <= 1` (or `>= 0`, `"amount" must be <= 1`, ...) at render | Unclamped `interpolate()` or spring overshoot fed into a validated param | Always `extrapolateLeft/Right: 'clamp'`; clamp spring-eased values with `Math.min/Math.max`. |
| `"radius" must be a finite number`, `"scale" must be a finite number`, `"color" must be a non-empty string`, `"rays" must be a finite number`, `"center" must be a [number, number] tuple`, `"content" must be a non-empty string` | Required params missing: `blur.radius`, `scale.scale`, `tint.color`, `starburst.rays/colors`, `noiseDisplacement.center/radius`, `regionBlur.topLeft/bottomRight`, `lut.content` | Pass them explicitly. |
| `"color" has been renamed to "dotColor"` | Old halftone API | Use `dotColor`. |
| `"dotColor" can only be set when "colorMode" is "solid"` | Both passed | Drop `dotColor` in source mode. |
| `"topLeft" must be above and to the left of "bottomRight"` | regionBlur box inverted on some frame | Keep x1 < x2 and y1 < y2 throughout the animation. |
| `"blackPoint" must be less than "whitePoint"` | levels | Keep a gap. |
| `"seed" must be <= 1000` | `paper`/`roughenEdges` seed driven by frame | `seed: frame % 1000` or `frame * 0.1`. |
| `"hueShift" must be <= 360` | `lightLeak` hue animation | `hueShift: (frame * 2) % 360`. |
| `"samples" must be <= 64`, `"passes" must be <= 12`, `"x" must be ... less than 89` | limits | Clamp. |
| `Invalid LUT content ...: 1D LUTs are not supported` / `unsupported directive` / `expected N color rows` | LUT file format | Export a 3D `.cube`; strip other directives; check `LUT_3D_SIZE`. |
| `HTML in Canvas is not supported ...` | Preview browser lacks the API | Chrome 148+ with `chrome://flags/#canvas-draw-element`; or use CSS alternatives for DOM. |
| Motion blur has no visible effect | `useCurrentFrame()` called outside the blur wrapper | Move the animation into a child component rendered inside it. |
| `import {brightness} from '@remotion/effects'` is undefined | Root entry exports only 11 effects | Import from `@remotion/effects/brightness`. |
| Light trail smears the entire frame | Opaque pixels always contribute | Apply to an alpha-isolated subject. |
| Halftone shows only dots on transparency | Halftone replaces the source | Add a background layer or use `halftoneLinearGradient` solid mode. |
| Duotone looks posterized | It is a hard threshold | Use `thermalVision` with a 2-color palette. |
| Outline or shadow cut off at edges | Clipped to the component canvas | Leave transparent margin, enlarge the canvas. |
| `interpolateStyles`: "must have the same structure" / "units ... must match" | Mismatched transforms or units | Same functions in the same order; same units or 0. |
| `skew() supports only the following signatures` / `translate() supports only ...` | Wrong helper arguments | Use documented overloads. |

---

## 7. What our skills must teach

**Version gate (Remotion 4.0.528):**
- All 74 effects are usable (newest: `lut` 4.0.526, `tear` 4.0.523, `outline` 4.0.515, `tile` 4.0.513). Effects on
  `@remotion/shapes` need 4.0.474+. `maskToSourceAlpha` on `lines`/`rings`/`waves`/`zigzag`/`halftoneLinearGradient`
  needs 4.0.474+.
- Not available: `<HtmlInCanvasMotionBlur>` (4.0.529), Canvas `overrides`, `setSequenceNodePaths`,
  `sequence.controls`, `getCanvasSequenceSourceLocation` (4.0.529).
- Install with `npx remotion add @remotion/effects` so the version matches `remotion` exactly.

**Setup checklist before using any effect:**
1. Is the host canvas-based (`Solid`, `HtmlInCanvas`, `@remotion/media` `Video`, `Img`, `CanvasImage`, `AnimatedImage`,
   `Gif`, Rive canvas, shapes)? If not, wrap in `<HtmlInCanvas>` or use CSS.
2. Any WebGL2 effect (everything except the 11 2D ones)? Set `Config.setChromiumOpenGlRenderer('angle')` and render a
   still to verify.
3. Import from the subpath; pass required params.
4. Every animated param clamped to its valid range.
5. Pixel params scaled by `pixelDensity`.
6. Order the array deliberately (below).

**Ordering rules:**
- Generators that replace the source (`linearGradient`, `starburst`, `liquidContours`) first.
- Keying and masking (`colorKey`, `evolve`, `pixelDissolve`) before anything that reads alpha (`outline`, `dropShadow`,
  `glow`, `roughenEdges`, `lightTrail`).
- Grade (`colorCorrection`/`lut`) before stylize (halftone, duotone, thermal), before texture (`paper`, `burlap`,
  `scanlines`), before lens (`barrelDistortion`, `fisheye`), before `vignette`, with grain (`noise`) last.
- `scale()` before `tile()`; `scale()` before `wave()` to hide edge smear.
- Brightness then contrast if you must use them (not commutative); better: one `colorCorrection`.

**Defaults and units the agent must remember:**
- Non-identity defaults listed in 2.7 (notably `skew()` = 20 degrees, `grayscale()`/`invert()` = full).
- `wave.phase` radians, `waves.phase` degrees, `fisheye.fieldOfView` radians, `liquidContours.phase` cycles.
- `pixelDissolve` progress is "gone-ness"; `evolve`/`venetianBlinds` progress is "revealed-ness"; `tear` progress may
  exceed 1.
- `duotone` = hard threshold; `thermalVision` = smooth gradient map.
- `glow`/`lightTrail` are single-color and additive; `lightLeak` composites normally.
- `halftone` and `dotGrid` remove the source outside dots.

**Animation discipline:**
- Effects are static: drive `progress`, `offset`, `phase`, `seed`, `angle` from `frame`. Grain wants `seed: frame`;
  pattern scroll wants `offset: frame * k`; loops want phase changes of whole cycles over the loop length.
- Keep `interpolate()` inline inside the effect call (Studio can then edit keyframes).
- Use tuple `interpolate()` for UV params (`center`, `start`, `end`, corners).
- Use `disabled` rather than conditionally changing the array shape when toggling an effect across a timeline (keeps
  the memoized definitions stable).

**Performance defaults:**
- Default to T0 effects; allow at most one or two T2 effects per layer in a 1080p comp unless a still render shows
  headroom.
- Avoid `brightness`/`contrast`/`tile` on full-frame video; avoid `outline.edgeSimplification` in long renders.
- One master `<HtmlInCanvas>` for scene-wide looks instead of per-element copies; mount effect layers only while visible.
- Never animate an effect component's `width`/`height`/`pixelDensity`.
- `@remotion/noise`: one seed per purpose, index in the coordinate.
- Motion blur: `<CameraMotionBlur>` samples 5 to 8 by default; verify color on a still.

**Deprecation policy:**
- New code uses `lightLeak()` and `starburst()` from `@remotion/effects` on `<Solid>`. `<LightLeak>`/`<Starburst>` are
  acceptable on 4.0.528 when their extras are needed (`mixBlendMode` overlay on DOM, starburst `vignette` fade), with a
  note that they disappear in 5.0.

**Safety:**
- Do not install Canvas Capture or Chrome for Testing on the user's behalf; describe the steps and let the user decide.

---

## 8. Best examples to learn from

- `repo/packages/jonnys-videos/src/disco-light-show/MasterWithEffect.tsx`: whole-video CRT power-off with scanlines,
  flickering chromatic aberration, per-frame grain and CSS collapse. The best glitch/outro reference.
- `repo/packages/jonnys-videos/src/disco-light-show/DiscoBallBg.tsx`: layered `<Solid>` generators (rings + wave + blur +
  noise), `pattern` + `chromaticAberration` on looping video, tuple `interpolate` with `posterize` for stepped motion.
- `repo/packages/brand/src/effects/Goal.tsx`: sports title card: gridlines floor masked by `evolve`, spring-eased
  `fisheye`/`glow` params, `halftoneLinearGradient` text texture, custom effect in the same chain.
- `repo/packages/brand/src/effects/NewsHeadline.tsx`: newsprint scan look (premultiplied noise, two progressive blurs,
  tinted vignette) on an `<HtmlInCanvas>` group.
- `repo/packages/brand/src/effects/experiments/BillboardForeground.tsx`: screen replacement with `cornerPin` and
  `pixelDensity={2}`.
- `repo/packages/brand/src/effects/EffectsAnnouncement.tsx`: greenscreen compositing (`colorKey` tuned values) over a
  `burlap` background.
- `repo/packages/brand/src/effects/experiments/LightTrailRemotionText.tsx`: animated `pattern` row offset and scroll.
- `repo/packages/brand/src/effects/metallic-swirl-effect.ts` and `MetallicSwirl.tsx`: a production custom WebGL effect.
- `repo/packages/example/src/EffectsTestbed/sample-posterize-2d.ts`, `sample-rgb-shift-webgl.ts`, `palette-map.ts`:
  minimal custom effect templates (2D and WebGL2).
- `repo/packages/brand/src/Showcase/MotionBlurSlideIn.tsx`: `<HtmlInCanvasMotionBlur>` usage (4.0.529+ only).
- `examples/github-unwrapped/remotion/StarsGiven/index.tsx`, `Opening/TakeOff.tsx`, `TopLanguages/FloatingOctocat.tsx`:
  `noise2D` camera shake, take-off rumble, idle float.
- `mirror/docs/light-leaks.md` (D1): the `<TransitionSeries.Overlay>` light-leak pattern.
- `repo/packages/effects/src/color-correction-shader-utils.ts`: the exact color math for exposure, white balance,
  shadows/highlights and vibrance (useful to predict results).

---

## 9. Open questions

1. `zoomBlur().center` is passed to the shader without the top-left UV conversion that most effects apply; a center of
   `[0.5, 0.2]` may land 20% from the bottom. Same question for `mirror({direction: 'vertical', position})` and the
   vertical layout of `tvSignalOff` bars. Verify in Studio; if mirrored, use `1 - y`.
2. How many simultaneously mounted WebGL effect components the headless render browser tolerates before context loss
   (browser cap is general knowledge; Remotion docs are silent). Worth a benchmark with our typical scenes.
3. Real per-effect cost at 1080p and 4K on the Mac Studio and on Lambda (only relative tiers are known).
4. Whether `ctx.filter` based 2D effects (`hue`, `saturation`, `grayscale`, `invert`) render in Safari for the Player
   (their pages have no compatibility table).
5. The package root export map is not in the local repo; the source index suggests `import {x} from '@remotion/effects'`
   works for only 11 effects. Confirm against the installed `package.json` after `npx remotion add @remotion/effects`.
6. Defaults in 4.0.528 versus this newer source: confirm a couple (for example `speckle`, `outline`) in `node_modules`
   once installed.
7. `<Starburst originOffsetX/Y>` range: docs say -1..1 maps to the edges, the shader suggests +/-0.5 already reaches
   them and that +Y may move up. Needs a visual check if the deprecated component is used.
8. `whiteNoise` uses a `sin()` hash; do local and Lambda renders match closely enough for split renders stitched from
   different machines?
9. `lut()` with `.cube` files from common tools: which extra directives appear in practice (DaVinci, Premiere) and would
   need stripping before use?
