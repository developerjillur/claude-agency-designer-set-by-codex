# The effects catalogue (`@remotion/effects`, Remotion 4.0.528)

All 74 effects, grouped by what they do. For each: subpath, since version, backend, parameters with defaults and
valid ranges, what it looks like, cost, and the trap. The kit wraps the common ones as `fx.*` presets with clamped
parameters (see the module README); use the raw factories for everything else.

## How effects work

- An effect factory (`blur({radius: 8})`) returns a descriptor; the host runs the list **in array order**, each effect
  reading the previous one's output. Hosts: `<Solid>`, `<Img>`, `<CanvasImage>`, `<HtmlInCanvas>`, `<Video>` from
  `@remotion/media`, `@remotion/shapes` components, `<Gif>`, `<AnimatedImage>`, `<RemotionRiveCanvas>`.
  `<OffthreadVideo>` and `<Html5Video>` take no effects.
- The factory **validates when you call it**, during React render. An out-of-range value throws a `TypeError` and
  fails the render: clamp every animated parameter (`extrapolateLeft/Right: 'clamp'`, `Math.min/max` around spring
  values). Every factory also takes `disabled: true`, which removes it before the chain runs (costs nothing and keeps
  the array shape stable).
- Effects never animate by themselves. Motion comes from parameters computed from `useCurrentFrame()`: `progress`,
  `offset`, `phase`, `seed`, `angle`, `rotation`. A `<Solid>` re-runs its chain only when a parameter changes.
- **Import from the subpath**: `import {noise} from '@remotion/effects/noise'`. The package root exports only
  `checkerboard`, `pattern`, `tile`, `rings`, `starburst`, `lightLeak`, `gridlines`, `zigzag`, `linearGradient`,
  `linearGradientTint`, `cornerPin`. `uvTranslate` and `xyTranslate` share `@remotion/effects/translate`.
- **Backends**: 11 effects are 2D canvas (`brightness`, `contrast`, `grayscale`, `hue`, `invert`, `saturation`,
  `tint`, `scale`, `uvTranslate`, `xyTranslate`, `tile`); the other 63 are WebGL2 and need a GL backend in renders
  (`--gl=angle`, or `swangle` without a GPU). `exposure`, `levels`, `colorCorrection`, `lut` and the other grade
  effects are WebGL2 too, although their doc pages do not say so.
- Each host keeps a pool of 2 canvases per backend. A host with any WebGL effect holds 2 WebGL2 contexts; Chrome keeps
  16 per tab: measured, 8 hosts with animated WebGL effects render and 10 fail ("WebGL context was lost"). Crossing
  from WebGL to 2D costs an async `createImageBitmap`: group effects by backend.
- Between effects the picture is 8-bit premultiplied RGBA: long grade chains and wide gradients band. One
  `colorCorrection` beats six chained colour effects.
- Changing a host's `width`, `height` or `pixelDensity` rebuilds its whole chain and contexts: animate size with CSS
  `scale` on the host instead.
- Units: UV tuples are `[u, v]` with `[0, 0]` top-left; pixel parameters are canvas pixels (CSS px times
  `pixelDensity`; doubling the density halves their apparent size). Angles are degrees except `wave().phase` and
  `fisheye().fieldOfView` (radians); `liquidContours().phase` is in cycles. Raw `zoomBlur().center` counts y from the
  bottom (measured); the kit's `fx.zoomBlur` flips it.

### Three output behaviours (decide the layering from this)

1. **Modify in place, keep alpha**: colour and tone effects, `noise`, `scanlines`, `burlap`, `paper`, `emboss`,
   `flannel`, `thermalVision`, `duotone`, `tvSignalOff`, `whiteNoise`, `shine`, `linearGradientTint`, `lut`.
2. **Draw a pattern or light over the source**: `lines`, `rings`, `waves`, `zigzag`, `checkerboard`, `gridlines`,
   `contourLines`, `halftoneLinearGradient` (solid mode), `lightLeak`, `vignette` (colour mode), `glow`,
   `lightTrail`, `dropShadow`, `outline`. Most take `maskToSourceAlpha` to stay inside the subject.
3. **Replace the source**: `linearGradient`, `starburst`, `liquidContours` (ignore it), `halftone` (dots only),
   `halftoneLinearGradient` in source mode, `dotGrid`, and the masks `pixelDissolve`, `evolve`, `venetianBlinds`.
   Put generators first in the chain.

### Defaults that are not a no-op

Visible with no arguments: `grayscale()`, `invert()` (full), `skew()` (20 degrees), `barrelDistortion()` (0.25),
`chromaticAberration()` (8 px), `fisheye()` (2.5 rad), `wave()` (60 px), `mirror()`, `tile()`, `glow()`,
`dropShadow()`, `vignette()` (0.5), `noise()` (0.15), `whiteNoise()` and `tvSignalOff()` and `thermalVision()`
(full), `paper()`, `burlap()`, `emboss()`, `flannel()`, `shrinkwrap()`, `roughenEdges()`, `speckle()`, `scanlines()`,
`pixelate()`, `dotGrid()`, `halftone()`, the progressive pixelates (block 40) and blurs (50 px), `zoomBlur()` (40),
every pattern, and every progress effect (`evolve`, `venetianBlinds`, `pixelDissolve`, `shine`, `lightLeak`, `tear`
default to progress 0.5). Identity with no arguments: `brightness`, `contrast`, `saturation`, `hue`, `exposure`,
`levels`, `shadowsHighlights`, `whiteBalance`, `vibrance`, `colorCorrection`, `cornerPin`, both translates.
Required parameters (calling without them throws): `blur` (radius), `scale` (scale), `tint` (color), `starburst`
(rays, colors), `noiseDisplacement` (center, radius), `regionBlur` (topLeft, bottomRight), `lut` (content).

Cost legend: **T0** one pass, a few texture reads; **T1** one pass with procedural noise; **T2** several passes or up
to about 100 reads a pixel; **CPU** pixels read back and looped in JavaScript every frame.

## Colour and tone

| Effect (subpath) | Since, backend, cost | Parameters (default, range) | Notes |
|---|---|---|---|
| `colorCorrection` (`color-correction`) | 4.0.509, WebGL2, T0 | `exposure` 0 (-5..5), `contrast` 1 (>= 0), `pivot` 0.5, `shadows`, `highlights`, `whites`, `blacks`, `temperature`, `tint`, `vibrance` 0 (-1..1), `saturation` 1 (>= 0) | the default grade: fixed internal order (exposure, white balance, tonal regions, contrast, saturation, vibrance) in one pass |
| `exposure` | 4.0.508, WebGL2, T0 | `stops` 0 (-5..5) | linear-light brighten or darken |
| `levels` | 4.0.508, WebGL2, T0 | `blackPoint` 0, `whitePoint` 1 (black < white or it throws), `gamma` 1 (0.01..10) | cannot raise the output black: faded blacks come from `colorCorrection({blacks})` or a LUT |
| `shadowsHighlights` (`shadows-highlights`) | 4.0.508, WebGL2, T0 | `shadows`, `highlights` 0 (-1..1, up to a stop) | smooth, no halos |
| `whiteBalance` (`white-balance`) | 4.0.508, WebGL2, T0 | `temperature` 0 (-1 cool..1 warm), `tint` 0 (-1 green..1 magenta) | keeps luminance |
| `vibrance` | 4.0.508, WebGL2, T0 | `amount` 0 (-1..1) | lifts muted colours more than saturated ones |
| `saturation` | 4.0.466, 2D filter, T0 | `amount` 1 (>= 0) | cheap |
| `hue` | 4.0.466, 2D filter, T0 | `degrees` 0 | |
| `grayscale` | 4.0.466, 2D filter, T0 | `amount` 1 (0..1) | full by default |
| `invert` | 4.0.466, 2D filter, T0 | `amount` 1 (0..1) | |
| `brightness` | 4.0.466, 2D, CPU | `amount` 0 (-1..1) | adds a flat value, washes blacks; prefer `exposure` |
| `contrast` | 4.0.467, 2D, CPU | `amount` 1 (>= 0) | pivot fixed at mid grey; prefer `colorCorrection` |
| `tint` | 4.0.466, 2D, T0 | `color` required, `amount` 0.5 | flat colour over opaque pixels |
| `lut` | 4.0.526, WebGL2, T0 | `content` required (a 3D `.cube` text) | sizes 2..256, TITLE, DOMAIN_MIN/MAX, comments; 1D LUTs and other directives throw; rows must equal size cubed; caches 4 contents |
| `duotone` | 4.0.468, WebGL2, T0 | `darkColor` black, `lightColor` white, `threshold` 0.5 | HARD threshold (1-bit stencil) |
| `thermalVision` (`thermal-vision`) | 4.0.479, WebGL2, T0 | `amount` 1, `palette` (>= 2 colours; default a heat ramp) | a true gradient map: 2 colours = smooth duotone, 3 = tritone |
| `linearGradientTint` (`linear-gradient-tint`) | 4.0.483, WebGL2, T0 | `start` [0, 0.5], `end` [1, 0.5], `startColor`, `endColor`, `amount` 0.5 | tints toward a two-stop gradient |
| `colorKey` (`color-key`) | 4.0.472, WebGL2, T0 | `keyColor` #00ff00, `similarity` 0.18, `smoothness` 0.08, `spillSuppression` 0.25 (all 0..1) | RGB distance key; good real values: similarity 0.2 to 0.45, spill up to 0.9 |

## Blur and focus

| Effect | Since, backend, cost | Parameters | Notes |
|---|---|---|---|
| `blur` | 4.0.465, WebGL2, T2 | `radius` required (<= 0 passes through), `horizontal` true, `vertical` true | separable Gaussian; one axis off = directional blur; edges clamp |
| `linearProgressiveBlur` (`linear-progressive-blur`) | 4.0.472, WebGL2, T2 | `start` [0, 0.5], `end` [1, 0.5], `startBlur` 0, `endBlur` 50 | gradual focus fall-off |
| `radialProgressiveBlur` (`radial-progressive-blur`) | 4.0.483, WebGL2, T2 | `center` [0.5, 0.5], `width` 1, `height` 1, `rotation` 0, `start` 0 (0..1), `startBlur` 0, `endBlur` 50 | spotlight focus and tilt shift (a wide flat ellipse) |
| `regionBlur` (`region-blur`) | 4.0.507, WebGL2, T2 | `topLeft`, `bottomRight` required (top-left above-left of bottom-right on every frame), `blurRadius` 40, `feather` 0, `roundness` 0 (0 box..1 pill) | anonymising faces, plates, documents |
| `zoomBlur` (`zoom-blur`) | 4.0.480, WebGL2, T2 | `amount` 40 px, `center` [0.5, 0.5] (y from the BOTTOM), `samples` 24 (1..64 integer) | speed punch-in; animate amount to 0 |

## Distortion and geometry

| Effect | Since, backend, cost | Parameters | Notes |
|---|---|---|---|
| `barrelDistortion` (`barrel-distortion`) | 4.0.466, WebGL2, T0 | `amount` 0.25 (0..1) | CRT glass; corners go transparent |
| `chromaticAberration` (`chromatic-aberration`) | 4.0.467, WebGL2, T0 | `amount` 8 px (>= 0), `angle` 0 | red one way, blue the other |
| `fisheye` | 4.0.470, WebGL2, T0 | `fieldOfView` 2.5 rad (0..PI), `center`, `radius` 1, `zoom` 1 | action cam, peephole; outside the source becomes transparent |
| `wave` | 4.0.465, WebGL2, T0 | `phase` 0 (radians), `direction` horizontal, `amplitude` 60 px, `wavelength` 240 px | edges smear: `scale()` first or keep it small; two for both axes |
| `noiseDisplacement` (`noise-displacement`) | 4.0.474, WebGL2, T2 | `center`, `radius` required (0..1), `strength` 36, `seed` 0, `grainSize` 8, `passes` 6 (1..12), `blur` 0, `feather` 0.25, `biasDirection` 0, `biasAmount` 0 | local glass or smear; animate seed to boil |
| `cornerPin` (`corner-pin`) | 4.0.482, WebGL2, T0 | `topLeft` [0,0], `topRight` [1,0], `bottomRight` [1,1], `bottomLeft` [0,1] | screen replacement, billboards; tuple interpolate for motion |
| `skew` | 4.0.491, WebGL2, T0 | `x` 20, `y` 0 (-89..89), `origin` [0.5, 0.5] | |
| `mirror` | 4.0.466, WebGL2, T0 | `direction` horizontal, `position` 0.5, `invert` false | two for 4-way symmetry |
| `scale` | 4.0.466, 2D, T0 | `scale` required (> 0), `horizontal`, `vertical` | overscan before `wave`, shrink before `tile` |
| `uvTranslate`, `xyTranslate` (`translate`) | 4.0.467, 2D, T0 | `u`, `v` (1 = full size); `x`, `y` px | content moved out is clipped |
| `tile` | 4.0.513, 2D, CPU | `horizontal`, `vertical` | repeats the opaque bounds, mirroring every other copy |
| `pattern` | 4.0.477, WebGL2, T1 | `scale` 0.1, crops, `gapX/Y`, `offsetU/V` (scroll), `rowOffset`, `rowOffsetEvery`, `columnOffset`, `columnOffsetEvery`, `origin`, `wrap` true | logo walls, brick layouts |
| `tear` | 4.0.523, WebGL2, T0 | `progress` 0.5 (>= 0; above 1 the halves keep moving), `angle` 0, `rotation` 20 (0..90), `jaggedness` 20 px | paper rip reveal or exit |

## Print, pixel and signal

| Effect | Since, backend, cost | Parameters | Notes |
|---|---|---|---|
| `halftone` | 4.0.467, WebGL2, T0 | `shape` circle (square, line), `dotSize` 20, `dotSpacing` = dotSize, `rotation` 0, `offsetX/Y`, `sampling` bilinear, `colorMode` solid (source), `dotColor` red (solid only), `invert` | outputs ONLY dots, transparent between; `color` was renamed `dotColor`; `dotColor` with source mode throws |
| `halftoneLinearGradient` (`halftone-linear-gradient`) | 4.0.469, WebGL2, T0 | `firstStopDotSize` 0, `secondStopDotSize` 40, stop positions, `gridSize` 24, `colorMode`, `dotColor` black, `maskToSourceAlpha` | dot size by position: dot wipes, pop-art grounds |
| `dotGrid` (`dot-grid`) | 4.0.469, WebGL2, T0 | `dotSize` 16, `gridSize` 20, `invert` | source only inside (or outside) the dots: LED wall |
| `pixelate` | 4.0.479, WebGL2, T0 | `blockSize` 20 (>= 1) | one sample per block: moving footage shimmers, blur a touch first |
| `linearProgressivePixelate`, `radialProgressivePixelate` | 4.0.490, WebGL2, T0 | like the progressive blurs with `startBlockSize` 1, `endBlockSize` 40 | swap the sizes to pixelate a face in the middle |
| `scanlines` | 4.0.469, WebGL2, T0 | `amount` 0.15, `spacing` 4, `thickness` 1 (clamped to spacing), `offset` (roll), `premultiply` false | lines brighter, gaps darker |
| `noise` | 4.0.469, WebGL2, T0 | `amount` 0.15, `seed` 0, `premultiply` false | static until the seed changes; premultiply scales it with brightness (film) |
| `whiteNoise` (`white-noise`) | 4.0.470, WebGL2, T0 | `amount` 1, `seed` 0 | TV static; its sin hash can differ between GPUs |
| `speckle` | 4.0.469, WebGL2, T0 | `density` 0.08, `size` 4, `randomness` 1 | transparent holes; no seed (change `size` to reshuffle) |
| `tvSignalOff` (`tv-signal-off`) | 4.0.476, WebGL2, T0 | `amount` 1 | colour bars inside the alpha |
| `outline` | 4.0.515, WebGL2 (+CPU when simplifying), T2 | `width` 8, `edgeSimplification` 0, `color` white, `opacity` 1, `outlineOnly` false | hard edged; clipped at the canvas edge: leave margin |
| `roughenEdges` (`roughen-edges`) | 4.0.487, WebGL2, T1 | `amount` 1, `border` 26.5 (0..200), `scale` 0.07, `seed` 231.2 (0..1000) | only near alpha edges: nothing on full-frame pictures |

## Texture and material

| Effect | Since, backend, cost | Parameters | Notes |
|---|---|---|---|
| `paper` | 4.0.486, WebGL2, T1 (heavy) | `amount` 1, `colorFront`, `colorBack`, `contrast`, `roughness`, `fiber`, `fiberSize`, `crumples`, `crumpleSize`, `folds`, `foldCount` (0..15), `drops`, `fade`, `seed` 6 (0..1000), `scale` 0.6 (0.01..4) | re-roll the seed on a slow step (every 30 frames) for a living texture |
| `burlap` | 4.0.478, WebGL2, T1 | `amount` 0.55, `size` 5, `roughness` 0.7, `seed`, `color` | woven sack |
| `flannel` | 4.0.491, WebGL2, T0 | `amount` 0.7, `size` 96, `softness` 0.18, `baseColor`, `stripeColor` | plaid on a Solid |
| `shrinkwrap` | 4.0.479, WebGL2, T1 | `amount` 1, `displacement` 5, `highlightIntensity` 0.75, `wrinkleDensity`, `edgeTension`, `phase`, `seed` | plastic wrap on stickers |
| `emboss` | 4.0.479, WebGL2, T1 | `amount` 0.7, `size` 26, `lineWidth` 7, `depth` 0.75, `angle`, `lightAngle` 135, `offset` | a raised dash relief pattern, not an edge emboss |

## Patterns and grounds (use on a `<Solid>`)

| Effect | Since | Parameters | Notes |
|---|---|---|---|
| `lines`, `rings`, `waves`, `zigzag`, `checkerboard` | 4.0.470 to 4.0.480 | `colors` ['#dff4ff', '#7cc6ff'] (cyclic, 'transparent' allowed), `gap`, `thickness` 40, `angle`, `offset` (scroll), waves/zigzag `amplitude`, `wavelength`, waves `phase` (degrees); checkerboard `cellSize` 80 | hard aliased edges: keep 0 or 90 degree angles or blur 1 px after; a seamless loop scrolls `offset` by a whole pattern period over the loop |
| `gridlines` | 4.0.476 | `gridSize` 64, `lineWidth` 2, `lineColor`, `backgroundColor`, `rotation`, `rotationX/Y`, `perspective` (> 0 = a 3D floor), `offsetX/Y`, `maskToSourceAlpha` | blueprint, synthwave floor (rotationX -68, perspective 900, offsetY by frame) |
| `contourLines` | 4.0.476 | `lineColor`, `lineWidth` 1.5, `spacing` 36, `scale` 220, `complexity`, `smoothness`, `seed`, `offsetX/Y`, `opacity` | topographic lines |
| `liquidContours` | 4.0.491 | `firstColor`, `secondColor`, `spacing` 62, `scale` 300, `complexity`, `smoothness`, `seed` 4, `offsetX`, `offsetY`, `phase` 3.23 (cycles) | replaces the source; +1.0 phase = the same picture (perfect loops) |
| `linearGradient` | 4.0.483 | `start`, `end`, `startColor`, `endColor` | replaces the source; 8-bit sRGB: add 2 percent noise |
| `starburst` | 4.0.500 | `rays` required (2..100), `colors` required (>= 2, alpha dropped), `rotation`, `smoothness` 0 (0..1), `origin` [0.5, 0.5] (0..1) | opaque; smoothness 0.03 to 0.05 against stair-steps |

## Light, glow and shadow

| Effect | Since, cost | Parameters | Notes |
|---|---|---|---|
| `glow` | 4.0.468, T2 | `radius` 20, `intensity` 1, `threshold` 0 (0..1), `color` white | one colour, added; raise threshold on footage |
| `dropShadow` (`drop-shadow`) | 4.0.469, T2 | `radius` 12, `offsetX` 8, `offsetY` 8, `opacity` 0.5, `color` | from the alpha, behind; clipped at the canvas edge |
| `lightTrail` (`light-trail`) | 4.0.476, T2 | `direction` 180, `distance` 80, `intensity` 1, `decay` 0.9, `threshold` 0, `samples` 32 (1..64), `color` | every opaque pixel contributes fully: use on cut-outs, not full frames |
| `shine` | 4.0.468, T0 | `progress` 0.5 (0..1), `angle` 30, `haloSigma` 200, `coreSigma` 65, `haloIntensity` 0.3, `coreIntensity` 0.4 | white sweep masked by alpha |
| `lightLeak` (`light-leak`) | 4.0.500, T1 | `seed` 0, `hueShift` 0 (0..360), `progress` 0.5 (0..1) | reveals to 0.5, retracts to 1, full cover at 0.5; normal alpha over the source |
| `vignette` | 4.0.468, T0 | `amount` 0.5, `radius` 0.65, `feather` 0.35, `roundness` 1, `center`, `color` black, `mode` color (alpha) | UV based, follows the aspect |

## Reveals

| Effect | Since | Parameters | Notes |
|---|---|---|---|
| `evolve` | 4.0.470 | `progress` 0.5 (0 hidden..1 shown), `direction` left (right, top, bottom), `feather` 0.1 | soft wipe |
| `venetianBlinds` (`venetian-blinds`) | 4.0.485 | `progress` 0.5, `direction` vertical, `slats` 12 | hard edges |
| `pixelDissolve` (`pixel-dissolve`) | 4.0.471 | `progress` 0.5 (0 shown..1 GONE), `columns` 10, `rows` 10, `seed`, `feather` 0.15 | the opposite direction of evolve |

`tear` and `lightLeak` also work as reveals.

## Order in a chain

Generators that replace the source, then keying and masking (`colorKey`, `evolve`, `pixelDissolve`), then grade
(`colorCorrection` or `lut`), stylise (`halftone`, `duotone`, `thermalVision`), texture (`paper`, `burlap`,
`scanlines`), lens (`barrelDistortion`, `fisheye`), `vignette`, and grain (`noise`) last. Alpha readers (`outline`,
`dropShadow`, `glow`, `roughenEdges`, `lightTrail`) come after whatever sets the alpha. `scale` before `tile` and
before `wave`. If brightness and contrast are used, brightness first (they do not commute).

## Writing your own effect: `createEffect`

`createEffect<P, S>({type, label, documentationLink, backend: '2d' | 'webgl2' | 'webgpu', calculateKey, setup,
apply, cleanup, schema, validateParams})` from `remotion` returns a factory like the built-ins. The kit's
`posterize` and `sliceShift` (`kit/fx/custom-effects.ts`) are complete WebGL2 examples. Rules:

- `calculateKey(params)` must include every resolved parameter (it drives memoisation; the framework adds
  `disabled`).
- `validateParams` runs when the factory is called: throw a readable error for bad input.
- `setup(target)` gets the context: for WebGL2 use `{premultipliedAlpha: true, alpha: true, preserveDrawingBuffer:
  true}`; compile the program and create the VAO, buffer and texture once.
- `apply({source, width, height, params, state, flipSourceY})`: set the viewport, bind the default framebuffer,
  upload the source with `UNPACK_FLIP_Y_WEBGL = flipSourceY` and `UNPACK_PREMULTIPLY_ALPHA_WEBGL = true`, draw. The
  texture is premultiplied: divide by alpha before colour maths and multiply back after.
- For 2D effects reset `filter`, `globalAlpha` and `globalCompositeOperation` after drawing.
- `cleanup(state)` deletes the GL objects. `schema: {}` is fine when Studio editing is not needed.

## Motion blur, noise and style interpolation (neighbours of the effects)

- `@remotion/motion-blur`: `<CameraMotionBlur shutterAngle={180} samples={6}>` (renders the children `samples` times
  at sub-frame times; children must read `useCurrentFrame()` themselves) and `<Trail layers lagInFrames
  trailOpacity>` (echo copies). `<HtmlInCanvasMotionBlur>` is 4.0.529, not in 4.0.528. The kit's `MotionBlur` (motion
  module) wraps CameraMotionBlur. A cheap directional smear on an effect host: `blur({radius: speedPx * 0.3,
  vertical: false})`.
- `@remotion/noise`: `noise2D/3D/4D(seed, ...)` in -1..1, deterministic; one seed per purpose with the index in a
  coordinate (the cache holds about 10 seeds). Drive effect parameters with it (`chromaticAberration({amount: 4 +
  noise2D('ca', frame / 8, 0) * 3})`).
- `@remotion/animation-utils`: `interpolateStyles(frame, range, styles, {extrapolateLeft: 'clamp', extrapolateRight:
  'clamp'})` keyframes whole style objects (default extrapolation is extend; colours interpolate linearly and ignore
  easing) and `makeTransform([...])` builds transform strings.
