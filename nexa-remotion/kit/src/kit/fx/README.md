# fx: effects, looks, masks, keying, light and transitions

`import {...} from './kit/fx'` (a module of the nexa-remotion kit, Remotion 4.0.528). It imports only `../core`,
`../motion` and npm packages. Everything here is a pure function of the frame.

Before anything else:

- **WebGL in renders.** Every `@remotion/effects` effect except 11 cheap 2D ones, every canvas look and every shader
  transition needs a GL backend: `--gl=angle` (nrk passes it; `remotion.config.ts` sets it), `swangle` on a machine
  without a GPU. Without it the effect draws nothing or the render fails.
- **At most 8 effect hosts at once.** Chrome keeps 16 live WebGL contexts per render tab and every host with a WebGL
  effect (an `Img`/`Video`/`Solid`/`HtmlInCanvas` with `effects`, a canvas look) holds 2. Measured on this machine: 8
  hosts with animated effects render, 10 fail with "WebGL context was lost". Count both scenes of a transition.
  Put many effects on one host rather than one effect on many hosts, and page grids through Sequences.
- **HTML-in-canvas cannot nest.** A canvas look (`HtmlInCanvas`) inside another canvas look throws; inside a scene
  next to a shader transition it waits until the render times out. `<Scenes>` marks such scenes and the looks switch to
  their css engine by themselves (`engine="auto"`).
- **Preview.** Canvas looks and shader transitions preview only in Chrome 148+ with
  `chrome://flags/#canvas-draw-element`. With `engine="auto"` a look shows its css version where HTML-in-canvas is
  missing, so a plain-browser preview can differ from the render: pass `engine` explicitly when that matters.

Files: `effects.ts` (presets), `custom-effects.ts` (posterize, sliceShift), `css.tsx` (overlays), `looks.tsx`,
`glitch.ts`, `masks.tsx`, `keying.tsx`, `light.tsx`, `transitions.tsx`, `lut.ts`, `util.ts`.

---

## Effect presets: `fx`

Small wrappers around `@remotion/effects` (imported by subpath) with designed defaults and every parameter clamped
to its valid range, so an animated value can never fail the render. Pass the result in an `effects` array on `Img`,
`Video` from `@remotion/media`, `Solid`, `CanvasImage`, `HtmlInCanvas` or a `@remotion/shapes` shape. Effects run in
array order. Pixel values are canvas pixels of the host (multiply by `unit` from `useStage()` at 4K).

```tsx
const frame = useCurrentFrame();
const {fps, width, height} = useStage();
<Img src={staticFile('shot.jpg')} width={width} height={height} style={{objectFit: 'cover'}}
  effects={[fx.grade('cinematic'), fx.vignette(), fx.grain({frame, fps})]} />
```

| Preset | What it does | Defaults |
|---|---|---|
| `fx.colorCorrection(o)` | one-pass grade: exposure, contrast, pivot, shadows, highlights, whites, blacks, temperature, tint, saturation, vibrance | identity |
| `fx.grade(name, amount = 1)` | a named grade from `grades`, scaled toward identity by `amount` | `natural`, `cinematic`, `warmFilm`, `coolNight`, `bleach`, `punchy`, `mono` |
| `fx.exposure(stops)` | stops, -5 to 5 | 0 |
| `fx.levels({black, white, gamma})` | black below white (a 0.01 gap is kept), gamma 0.01 to 10 | 0, 1, 1 |
| `fx.lut(content)` | a 3D `.cube` LUT (text) | required |
| `fx.saturation(k)`, `fx.hue(deg)`, `fx.grayscale(k)` | cheap 2D canvas filters | 1, 0, 1 |
| `fx.grain({frame, fps, amount, hz, seed, premultiply})` | film grain re-seeded `hz` times a second | 0.06, 12 Hz, premultiply |
| `fx.noise({amount, seed})` | static noise; 0.02 to 0.04 dithers gradients | 0.03 |
| `fx.staticNoise({amount, seed})` | TV static toward grey | 0.25 |
| `fx.dust({density, size})` | transparent specks (show the layer behind) | 0.02, 3 |
| `fx.vignette({amount, radius, feather, roundness, color, mode, center})` | UV vignette | 0.35, 0.72, 0.5 |
| `fx.paper({amount, seed, front, back, folds, crumples, roughness, scale})` | paper texture over the source | 0.6, seed 6 |
| `fx.glow({radius, intensity, threshold, color})` | monochrome additive halo | 18, 0.9, 0.55, white |
| `fx.lightLeak({progress, seed, hue})` | leak over the source; hue wrapped into 0 to 360 | required progress |
| `fx.shine({progress, angle, width, intensity})` | white sweep masked by alpha | angle 30 |
| `fx.starburst({colors, rays, rotation, smoothness, origin})` | rays (replaces the source: use on a `Solid`) | 24 rays, 0.03 |
| `fx.chromaticAberration({amount, angle})` | RGB split in px | 3, 0 |
| `fx.scanlines({amount, spacing, thickness, offset, premultiply})` | horizontal lines; animate `offset` | 0.18, 4, 1.5 |
| `fx.barrel(amount)` | CRT curvature; corners go transparent | 0.12 |
| `fx.tvSignalOff(amount)` | colour bars blended in | 1 |
| `fx.pixelate(block)` | mosaic | 16 |
| `fx.wave({amplitude, wavelength, phase, direction})` | sine displacement, phase in radians | 10, 260 |
| `fx.jitter(x, y)` | moves the picture in px | 0, 0 |
| `fx.blur(radius, {horizontal, vertical})` | Gaussian; one axis = directional; 0 costs nothing | required |
| `fx.zoomBlur({amount, center, samples})` | radial speed blur; `center` is top-left UV (the preset flips the raw effect's bottom-up y) | 40, [0.5, 0.5], 24 |
| `fx.tiltShift({center, width, height, start, blur})` | sharp band, blurred above and below | [0.5, 0.55], 22 |
| `fx.focus({center, size, start, blur})` | sharp ellipse, soft outside | 0.9, 16 |
| `fx.halftone({size, spacing, angle, shape, ink, source, invert})` | dots only (put paper behind) | 10, 45 deg, ink `#161616` |
| `fx.duotone({dark, light})` / `fx.tritone({dark, mid, light})` | smooth gradient maps (thermalVision palette) | |
| `fx.stencil({dark, light, threshold})` | hard one-bit duotone | 0.5 |
| `fx.posterize(levels, amount)` | kit effect: colour levels per channel | 5 |
| `fx.colorKey({color, similarity, smoothness, spill})` | chroma key | `#00b140`, 0.3, 0.08, 0.6 |
| `fx.outline({width, color, opacity})`, `fx.dropShadow({blur, x, y, opacity, color})` | from the alpha | 10 white; 18, 0, 12, 0.35 |
| `fx.tear({progress, angle, rotation, jaggedness})` | paper rip, progress may pass 1 | 18, 22 |
| `fx.evolve({progress, direction, feather})` | soft wipe in (0 hidden, 1 shown) | left, 0.15 |
| `fx.pixelDissolve({progress, columns, rows, seed, feather})` | blocks vanish (0 shown, 1 GONE) | 16 x 9 |
| `fx.slices({amount, bands, density, seed, split})` | kit effect: glitch bands pushed sideways | 60, 24, 0.35 |

Gotchas: effects are static until a parameter changes (drive `progress`, `offset`, `seed`, `phase` from the frame);
`duotone` in Remotion is a hard threshold (the kit's `fx.duotone` is the smooth one, `fx.stencil` the hard one);
`halftone` and `dotGrid` output only dots; `lightLeak`, `glow` and `lightTrail` add light, they do not grade.

### Custom effects: `posterize`, `sliceShift`

Written with `createEffect()` from `remotion` (WebGL2, one pass). `posterize({levels = 5, amount = 1})`,
`sliceShift({amount = 60, bands = 24, density = 0.35, seed = 0, split = 0})`. Use them through `fx.posterize` and
`fx.slices`, or directly in any `effects` array.

### LUTs: `makeCubeLut`, `useLutFile`, `cleanCube`

```tsx
const TEAL = makeCubeLut((r, g, b) => [r * 0.96, g, b * 1.04], 17); // module level: built once
const cube = useLutFile('grades/client.cube'); // public/grades/client.cube, holds the render until loaded
<Video src={src} effects={cube ? [fx.lut(cube)] : [fx.lut(TEAL)]} />
```

`makeCubeLut(fn, size = 17, title)` builds a 3D `.cube` from a colour function. `useLutFile(file)` fetches a file from
`public/` (or a URL) with `delayRender`, strips what `lut()` rejects (`cleanCube`) and returns the text or null.
Gotchas: `lut()` accepts only 3D LUTs with TITLE, LUT_3D_SIZE, DOMAIN_MIN/MAX; it caches 4 contents, so do not switch
between more than 4 LUTs per frame; 17 or 33 points.

---

## CSS building blocks

Work in any browser and inside shader-transition scenes. Each is a full-frame layer unless noted.

| Component | Purpose | Props (defaults) |
|---|---|---|
| `Grain` | SVG turbulence grain re-seeded at `hz` | `amount` 0.35 (layer opacity), `size` 1, `hz` 12, `seed`, `blend` overlay |
| `VignetteOverlay` | radial darkening | `strength` 0.3 (corner opacity), `start` 0.55, `color`, `blend` |
| `ScanlineOverlay` | lines | `opacity` 0.22, `spacing` 4, `thickness` 1.6 (px at 1080), `roll` px per frame, `color`, `blend` multiply |
| `GrilleOverlay` | CRT aperture grille | `opacity` 0.14, `pitch` 3 |
| `RgbSplit` | red and blue channels offset (SVG filter) | `dx` 4, `dy` 0, children |
| `Bloom` | highlights blurred and screened (renders children twice) | `amount` 0.55, `radius` 26, `threshold` 0.5 |
| `PosterizeCss` | exact colour steps (SVG feComponentTransfer) | `levels` 5 |
| `DustOverlay` | seeded film dust and hairs | `amount` 1, `seed`, `hz` 12, `color` |
| `SlicesCss` + `makeSlices(seed, count, amount)` | glitch bands as clipped copies (renders children count + 1 times) | `slices` |

```tsx
<AbsoluteFill><Scene /><Grain amount={0.3} /><VignetteOverlay strength={0.25} /></AbsoluteFill>
```

Gotcha: SVG filters are CPU work at full frame; `Bloom` and `SlicesCss` multiply the render cost of their children.

---

## Looks

A whole treatment on children. Shared props (`LookBaseProps`): `engine` ('auto' | 'canvas' | 'css', default auto),
`strength` (1; 0 is off), `seed`, `width`/`height` (default the frame), `overlay` (layers drawn on top, untouched:
captions, logos, small type), `style`.

| Look | Canvas engine (WebGL on the pixels) | Look-specific props (defaults) |
|---|---|---|
| `FilmLook` | grade (lifted warm blacks, soft highlights), 12 Hz grain, weak vignette; gate weave and dust as DOM | `grain` 0.07, `grainHz` 12, `vignette` 0.3, `weave` 1.2 px, `flicker` 0.025, `warmth` 0.2, `fade` 0.14, `dust` 0.6 |
| `VhsLook` | smear, saturation, RGB split, line wobble, slices, tape noise; tracking band and OSD as DOM | `split` 3, `smear` 1.6, `noise` 0.07, `tracking` true, `osd`, `date` |
| `CrtLook` | glow, rolling scanlines, split, barrel curve, vignette; grille and glass as DOM | `curve` 0.08, `scanlines` 0.3, `mask` 0.12, `glow` 0.45, `flicker` 0.015 |
| `NewsprintLook` | levels lift, black and white, halftone ink on a paper `Solid` | `ink`, `paper`, `dot` 6, `angle` 45, `texture` 0.5, `lift` 0.5 |
| `NoirLook` | black and white, hard contrast, grain, heavy vignette | `contrast` 1.35, `grain` 0.07, `vignette` 0.5, `blinds` 0 |
| `DreamyLook` | lifted pastel grade, warm glow on highlights, soft edges, light haze | `bloom` 0.75, `haze` 0.25, `soften` 0.5, `warmth` 0.12 |
| `GlitchLook` | bursts: RGB split, slices, jitter, now and then blocks and static | `bursts` [{at, frames, strength}], or `every` 54, `length` 6, `chance` 0.85; `idle` 0 |
| `StopMotionLook` | poses held on twos, boil, optional posterize (css unless `levels`) | `step` 2, `levels` 0, `boil` 1.2 |

```tsx
<FilmLook overlay={<Captions />}>
  <MyScene />
</FilmLook>
<GlitchLook bursts={[{at: 42, frames: 6}, {at: 90, frames: 4, strength: 0.6}]}><Title /></GlitchLook>
<Look look="vhs"><MyScene /></Look>
```

For footage without the DOM parts: `lookEffects(name, {frame, fps, unit, strength, seed})` returns the effect stack
(`filmEffects`, `vhsEffects`, `crtEffects`, `newsprintEffects`, `noirEffects`, `dreamyEffects`, `glitchEffects` are
exported too). `glitchAt(frame, schedule)` gives `{intensity, local, seed}` for your own glitch-driven animation.
`LookShell` and `useLookEngine` are exported to build a new look the same way.

Gotchas: one canvas look over a whole scene is cheaper than effects on many elements; a canvas look inside another
canvas look throws (use css for the inner one); small type (under about 60 px) breaks up in halftone and glitch
slices, so pass it as `overlay`; `StopMotionLook` freezes its children with `<Freeze>`, so media inside stutters on
purpose; look timing (grain, bursts) follows the enclosing Sequence.

---

## Masks

| Component | Purpose | Props (defaults) |
|---|---|---|
| `ShapeMask` | children seen through a growing shape | `shape` 'circle' (rect, star, heart, triangle, polygon, `{path}`), `size` 'cover' or px at 1080, `at` [0.5, 0.5], `aspect`, `radius`, `points`, `inner`, `rotate`, `spin`, `feather` (circle only), `ring` (edge line, true = accent), timing |
| `TextMask` | big words filled with a picture, video, gradient or any children | `text` ('\n' breaks lines), `src`, `gradient`, children, `font`, `weight`, `size` or `fit` 0.9 of the safe width, `maxSize` 420, `lineHeight` 0.9, `tracking`, `caps`, `at`, `outline`, `fillZoom`, `background` |
| `GradientMask` | fades children toward an edge | `fade` 'bottom' (top, left, right, edges, radial), `size` 0.35, `angle`, `invert` |
| `WipeMask` | a hard or soft wipe reveal | `from` 'left' (8 names or degrees), `kind` 'linear' (radial, split, blinds), `feather` 80 px, `at`, `slats` 8, timing |

Timing props (ShapeMask, WipeMask): `progress` (0 to 1, drive it yourself) or `delay`, `duration` (about 0.8 s),
`ease` (in-out), `exit` (hide again, ending on the last frame of the Sequence), `outDuration`.

```tsx
<ShapeMask shape="star" spin={90} delay={6} exit><Photo /></ShapeMask>
<TextMask text="লেকের ধারে" src={staticFile('lake.mp4')} fillZoom={0.1} />
<GradientMask fade="bottom" size={0.5}><Photo /></GradientMask>
<WipeMask from="topLeft" feather={160} duration={24}><Scene /></WipeMask>
```

Helpers: `shapePath({shape, cx, cy, size, ...})` returns an SVG path for `clip-path: path()`; `coverSize()` the size
that covers the frame from a point; `rotatePath(d, deg, cx, cy)`.

Gotchas: masks use `clip-path` and `mask-image` on the DOM (no image files, so nothing loads late); `feather` works
on circles only (other shapes are hard edged: draw a `ring` instead); `TextMask` waits for its fonts and measures the
longest line, Bangla is shaped by the browser and never split; the outline is drawn under the fill so variable-font
contours do not show.

---

## Keying and blending

| Component | Purpose | Props (defaults) |
|---|---|---|
| `ChromaKey` | green or blue screen clip or photo, keyed on the GPU | `src`, `kind`, `color` '#00b140' (sample the real screen), `similarity` 0.3, `smoothness` 0.08, `spill` 0.6, `outline`, `shadow`, `matte` {top, right, bottom, left} garbage matte, `width`, `height`, `fit` contain, video props |
| `keyEffects(opts, unit)` | the chain in the order that works: key, outline, shadow | |
| `Blend` | any children blended onto what is behind | `mode` screen, `opacity` |
| `BlendVideo` | a clip shot on black (or white) blended, its floor cleaned first | `src`, `mode` screen, `opacity`, `crush` 0.06 (levels), `effects`, `fit` cover |

```tsx
<AbsoluteFill>
  <Background />
  <ChromaKey src={staticFile('presenter.mp4')} color="#1fbf4f" similarity={0.34} spill={0.7} shadow />
  <BlendVideo src={staticFile('sparks-on-black.mp4')} mode="screen" />
</AbsoluteFill>
```

Gotchas: key the colour of the actual screen (sample it), not `#00ff00`; raise similarity until the screen is gone,
then smoothness for the edge, then spill for the green fringe; outline and drop shadow read the keyed alpha, so they
come after the key and a garbage matte removes floor shadows first; for flares, smoke, sparks and light leaks shot
on black use `screen` (keying black kills the glow and leaves hard edges); for ink and line art on white use
`multiply`; a `mix-blend-mode` layer blends with what is behind it only within the same stacking context, so do not
wrap it in an element with its own `isolation`, `opacity` below 1 or `clip-path` (put the clip on the blended
element itself).

---

## Light

| Component | Purpose | Props (defaults) |
|---|---|---|
| `LightLeak` | a light leak over what is behind (effect version on a `Solid`) | `seed` 0, `hue` 'warm' or degrees (`LEAK_HUES`: warm 0, coral 30, rose 60, magenta 90, violet 135, blue 180, cyan 210, teal 240, green 280, lime 320), `opacity` 0.85, `blend` screen, `delay`, `duration` (rest of the Sequence), `reverse`, `peak` 1 |
| `Starburst` | rotating ray ground | `colors` (theme accent pair), `rays` 24, `speed` 6 deg/s, `rotation`, `origin`, `smoothness` 0.035, `vignette` 0.35, `grain` 0.025 |
| `Shine` | a light sweep across a logo, product or card | `delay`, `duration` (about 1.1 s), `repeat` (frames between sweeps), `angle` 30, `width`, `intensity`, `engine`, `radius` (css box), `boxWidth`, `boxHeight` |

```tsx
<LightLeak seed={3} hue="coral" peak={0.6} />        {/* a flare that never covers the frame */}
<Starburst rays={28} colors={['#ff5e8a', '#ff7aa0']} />
<Shine delay={20} boxWidth={520} boxHeight={220}><Badge /></Shine>
```

Gotchas: at `peak` 1 a leak covers the whole frame at its middle (right over a cut, wrong over a title you want
read); the leak shader's hue turns toward red first, so use the named hues; `Shine` canvas follows the alpha of the
children (put box shadows outside it, they are clipped at the canvas edge); the deprecated `@remotion/light-leaks`
and `@remotion/starburst` components are not used (they go away in 5.0).

---

## Transitions

`tr.*` returns an `FxTransition` recipe; `<Scenes>` turns a list into a `TransitionSeries`, checks the timing first
and throws a readable error (each scene at least as long as each neighbouring transition, overlays with room on both
sides). Frames are written for 30 fps and scaled.

```tsx
const scenes: SceneSpec[] = [
  {node: <Intro />, duration: 90, transition: tr.slide()},
  {node: <Chart />, duration: 120, transition: tr.blurSlide({sound: {src: staticFile('whoosh.m4a')}})},
  {node: <Outro />, duration: 90},
];
// in Root: durationInFrames={scenesLength(scenes, 30)}
<Scenes scenes={scenes} enter={tr.fade()} exit={tr.fade({out: true})} />
```

| Preset | Engine | Frames | Notes |
|---|---|---|---|
| `tr.fade({out})` | css | 15 | incoming fades in; `out: true` also fades the outgoing (transparent scenes, exits) |
| `tr.slide({direction, spring})` | css | 20 | spring, no overshoot, rest threshold 0.001 |
| `tr.wipe({direction})` | css | 20 | 8 directions |
| `tr.flip({direction, perspective})` | css | 26 | 3D card flip |
| `tr.clockWipe()`, `tr.iris()` | css | 26, 24 | frame size filled in by Scenes |
| `tr.pushCut({flash, flashOpacity})` | css | 11 | hard editorial cut; Scenes delays the next scene's content by 5 frames |
| `tr.choreo()` | css | 20 | no visual: animate with `useTransitionProgress()` |
| `tr.zoomThrough({depth, blur})` | css | 22 | kit: dolly through the old scene (scale = 1 / distance), the new one comes out of the blur |
| `tr.whipPan({direction, blur})` | css | 12 | kit: both scenes travel with directional motion blur; `direction` is where the picture moves |
| `tr.glitchCut({seed, intensity})` | css | 12 | kit: RGB split and slices peak on the cut |
| `tr.lightLeakCross({seed, hue, opacity})` | css | 36 | kit: the cut hides under a leak |
| `tr.blurDissolve({blur})` | css | 24 | kit: soft crossfade through blur |
| `tr.maskReveal({shape, at, feather, ring, angle})` | css | 26 | kit: shape from a point, or 'diagonal' led by an accent bar |
| `tr.blurSlide`, `tr.zoomBlur`, `tr.crossZoom`, `tr.filmBurn`, `tr.dissolve`, `tr.linearBlur`, `tr.dreamyZoom`, `tr.swap`, `tr.ripple`, `tr.crosswarp`, `tr.bookFlip`, `tr.zoomInOut` | shader | 18 to 32 | HTML-in-canvas + WebGL2; all render on 4.0.528 with `--gl=angle` |
| `tr.flash({color, opacity})`, `tr.leak({seed, hue})` | overlay | 10, 40 | on a hard cut, the edit keeps its length |
| `tr.cut({sound})` | cut | 0 | a hard cut that carries a sound |

Every preset takes `frames` and `sound: {src, volume = 0.6, lead}` (`lead` = frames before the cut the sound starts;
default: the start of the transition).

`SceneSpec`: `node`, `duration` (mounted frames, overlaps included), `transition` (into the next scene), `name`,
`premountFor` (preview only). `planScenes(scenes, fps, {enter, exit})` returns `{total, starts, durations, delays,
joints, problems, warnings}`; `scenesLength()` the total.

Gotchas: total = sum of scenes minus overlaps (plus the hidden pre-cut frames Scenes adds for pushCut, glitchCut and
lightLeakCross); on 4.0.528 a shader transition gets no picture of a scene that entered with a CSS transition, so
Scenes splits such a scene in two sequences (it must then hold both transitions: Scenes says so); scenes next to a
shader transition cannot hold an `HtmlInCanvas` (looks switch to css there; a canvas look throws); a canvas look
around a whole `Scenes` works only with CSS transitions inside; `enter` and `exit` take css or shader transitions,
not overlays; custom wrapper components around `TransitionSeries.Sequence` are not recognised by Remotion (Scenes
maps the list directly).

---

## Utilities

`FxNestContext` / `useFxNest()` (where HTML-in-canvas cannot run: the looks and Scenes set it; wrap content you put
inside your own `<HtmlInCanvas>` or shader presentation in `<FxNestContext.Provider value={{canvas: 'inside my
canvas'}}>` so looks there pick css), `stepSeed(frame, fps, hz)` (a seed that changes `hz` times a second),
`mixHex(a, b, t)`, `rgba(hex, alpha)`, `hex6(color)`.

## Demos (`src/demos/fx.tsx`)

DemoFxSampleArt (the test picture), DemoFxEffects (36 presets on one picture, 6 pages), DemoFxLooks (canvas),
DemoFxLooksCss, DemoFxLooksVertical (9:16), DemoFxGlitch, DemoFxMasks, DemoFxKey, DemoFxLightLeak, DemoFxLeakHues,
DemoFxTransitions (built-in CSS), DemoFxTransitionsKit (kit presentations, enter and exit, a sound),
DemoFxTransitionsMask (mask reveals and overlays), DemoFxTransitionsShaderA/B (all 12 shaders),
DemoFxTransitionsMixed (shader and CSS in one series), DemoFxTransitionsVertical (9:16).
Assets in `public/fx/` were made here: `landscape.jpg` (DemoFxSampleArt), `greenscreen.mp4` and
`leak-on-black.mp4` (ffmpeg `geq`), `warm-film.cube` (Python), `whoosh.m4a` (ffmpeg pink noise).
