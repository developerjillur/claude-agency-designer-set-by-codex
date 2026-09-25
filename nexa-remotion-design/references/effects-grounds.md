# @remotion/effects for grounds (Remotion 4.0.528)

The GPU effects that make backgrounds and surface textures: what they do, their parameters and limits, cost, and
the traps. The fx sub-skill covers effects on footage (grades, glitch, keying); this file covers the ones that
draw or texture a ground. Checked against the installed 4.0.528 typings and the package source.

## 1. How effects run

- An effect is a per-frame pixel pass on a canvas-based component, passed as an ordered array to its `effects`
  prop. Hosts on 4.0.528: `<Solid>` and `<HtmlInCanvas>` (core), `<Img>`, `<CanvasImage>`, `<AnimatedImage>`,
  `<Video>` from `@remotion/media` (not `<OffthreadVideo>`), `@remotion/shapes` components (4.0.474+). A plain
  `<div>` cannot take effects.
- `<Solid width height color? pixelDensity? effects style? ...sequenceProps>` (4.0.464) is the generator surface: a
  1x1 canvas filled with `color` (transparent when omitted) stretched to `ceil(width * pixelDensity)` pixels. It
  renders a `<canvas>` with `style={{width, height, ...style}}`: position it yourself (the kit uses `position:
  absolute; left: 0; top: 0; display: block`). `pixelDensity` must be a positive finite number (Studio slider 1 to
  3); values below 1 render a smaller canvas that CSS scales up (softer, cheaper).
- Each factory call validates its params during React render; an invalid value throws and fails the render. Clamp
  every animated param (`interpolate(..., {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`, and
  `Math.min/Math.max` after springs).
- `<Solid>` wraps each chain run in `delayRender('Solid effect chain')` and calls `cancelRender` on errors. The chain
  re-runs only when the memoised params change: still params cost one pass per render tab; animated ones re-run
  every frame.
- Each component with WebGL effects owns two WebGL2 contexts (a ping-pong pair) plus its own texture uploads.
  Chrome keeps about 16 contexts alive: prefer one `<Solid>` carrying a stack over many small ones, and mount effect
  layers only while their Sequence is on screen. Never animate `width`, `height` or `pixelDensity` (the chain and its
  contexts are rebuilt); scale with CSS instead.
- Pixel params (`gridSize`, `lineWidth`, `thickness`, `spacing`, radii) are canvas pixels: multiply by `unit` for
  the frame size and by `pixelDensity` when you raise it.
- Import each effect from its subpath: `import {paper} from '@remotion/effects/paper'`. The package root exports
  only 11 effects (`checkerboard`, `pattern`, `tile`, `rings`, `starburst`, `lightLeak`, `gridlines`, `zigzag`,
  `linearGradient`, `linearGradientTint`, `cornerPin`).

## 2. WebGL in renders

- Everything except the 11 2D effects (`brightness`, `contrast`, `grayscale`, `hue`, `invert`, `saturation`, `tint`,
  `scale`, `uvTranslate`, `xyTranslate`, `tile`) is WebGL2 and needs GL in the render browser: `--gl=angle`, or
  `Config.setChromiumOpenGlRenderer('angle')` in remotion.config.ts (the kit sets it), or `chromiumOptions: {gl:
  'angle'}` in renderMedia/renderStill, or "OpenGL render backend: angle" in the Studio render dialog. Remotion 5
  enables it by default.
- Without GL: "Failed to acquire WebGL2 context for <effect>. Pass --gl=angle". The kit's `EffectGround` and `Paper`
  test `getContext('webgl2')` once per tab and draw a CSS ground instead of throwing.
- `--gl=swangle` (software, for machines without a GPU) works: the six effect grounds of DemoDesignEffects rendered
  in 29 s against 2 s with angle.
- "WebGL context was lost during canvas effect rendering": too many contexts or memory (Lambda); lower concurrency,
  raise memory, use fewer effect components at once, lower `pixelDensity`.

## 3. Generators and patterns (for grounds)

Replacing generators (put them first in a chain): `linearGradient`, `starburst`, `liquidContours`. Compositing ones
draw over the source (use a coloured `<Solid>` or a transparent one over other layers).

**liquidContours** (4.0.491, T1): `firstColor` #ff1a0a, `secondColor` #050505, `spacing` 62 (px of a band pair,
> 0), `scale` 300 (> 0), `complexity` 0 (0 to 1), `smoothness` 1 (0 to 1), `seed` 4, `offsetX` 13.4, `offsetY` 0,
`phase` 3.23. `phase` is in band cycles: adding exactly 1 returns the same image, so `phase = 3.23 + cycles * frame
/ durationInFrames` with an integer `cycles` loops seamlessly (the kit's `loop`). For a ground behind text, keep the
two colours close (the kit mixes 15% of the accent into the ground).

**waves** (4.0.471, T0) and the line family: `colors` (at least 2, cyclic, `'transparent'` allowed), `direction`
`'horizontal'`, `thickness` 40 (> 0), `gap` 0 (>= 0, transparent), `angle` 0, `offset` 0 (scrolls), `amplitude` 24
(>= 0), `wavelength` 160 (> 0), `phase` 0 (degrees here; `wave()` distortion uses radians), `maskToSourceAlpha`
(4.0.474). Seamless scroll: the pattern period is `thickness x colors.length`; move `offset` a whole number of
periods over the Sequence. `lines` (thickness, angle, offset), `zigzag` (like waves without phase), `rings`
(`center`, `thickness`, `offset`: expanding rings are on the anti-slop list), `checkerboard` (`cellSize` 80,
`angle`, `offsetX/Y`; 3 or more colours make diagonal bands). Their edges are hard and aliased: angles 0 or 90, or
`pixelDensity` 2 (the kit's default for waves), or `blur({radius: 1})` after.

**gridlines** (4.0.476, T0, anti-aliased): `gridSize` 64 (> 0), `lineWidth` 2 (>= 0), `lineColor` white,
`backgroundColor` transparent, `rotation`, `rotationX`, `rotationY` (degrees), `perspective` 0 (> 0 makes a 3D
plane; >= 0 validated), `offsetX`, `offsetY` (px), `maskToSourceAlpha`. Blueprint: a fine and a coarse grid with the
same offsets (the coarse size a multiple of the fine one). Floor: the plane passes through the canvas centre and
its horizon sits `perspective / tan(tilt)` px above it, so render the floor on its own `<Solid>` whose height puts
the horizon at the top edge (`perspective = (height / 2) x tan(tilt)`; the kit uses a 72 degree tilt on the lower
58% of the frame) and scroll `offsetY` towards the viewer. Lines fade near the horizon by themselves.

**contourLines** (4.0.476, T1, anti-aliased): `lineColor` white, `lineWidth` 1.5, `spacing` 36, `scale` 220 (all >
0), `complexity` 0.65, `smoothness` 0.55, `opacity` 1 (0 to 1), `seed` 0, `offsetX/Y`, `maskToSourceAlpha`.

**starburst** (4.0.500, T0): `rays` required (2 to 100), `colors` required (at least 2; alpha is dropped, so
transparent becomes black), `rotation` 0 (degrees, any), `smoothness` 0 (0 to 1; 0 is aliased, use 0.05 to 0.1),
`origin` [0.5, 0.5] (each 0 to 1, RangeError outside; measured from the top). Follow with `vignette({mode:
'alpha'})` to fade the rays out (the old `<Starburst vignette>` behaviour). The Rotating Starburst Element uses 28
rays turning 360 degrees over 2000 frames.

**linearGradient** (4.0.483, T0): `start` [0, 0.5], `end` [1, 0.5] (UV), `startColor`, `endColor`. sRGB, 8-bit:
add `noise({amount: 0.02})` after. `linearGradientTint` blends existing colours towards a two-stop gradient
(`amount` 0.5).

**paper** (4.0.486): see grounds-light-texture.md section 8. **burlap** (`amount` 0.55, `size` 5, `roughness`,
`seed`, `color`) and **flannel** (`amount`, `size` 96, `softness`, `baseColor`, `stripeColor`) are fabric grounds on
a `<Solid>`.

**halftoneLinearGradient** (4.0.469): `firstStopDotSize` 0, `secondStopDotSize` 40, `firstStopPosition` [0, 0.5],
`secondStopPosition` [1, 0.5], `gridSize` 24, `colorMode` solid, `dotColor` black, `maskToSourceAlpha`. Dot size by
position, a pop-art ground or a dot wipe. **dotGrid** (`dotSize` 16, `gridSize` 20, `invert`) keeps the source only
inside dots. **pattern** (`scale` 0.1, crops, gaps, `offsetU/V` to scroll, `rowOffset` + `rowOffsetEvery: 2` for
bricks) repeats a picture as wallpaper.

## 4. Texture and light passes

**noise** (4.0.469, T0): `amount` 0.15 (0 to 1), `seed` 0, `premultiply` false (true: grain follows brightness, like
film). Static until the seed changes: `seed: Math.floor(frame / 2.5)` for 12 plates a second at 30 fps. Put it last.

**vignette** (4.0.468, T0): `amount` 0.5, `radius` 0.65, `feather` 0.35, `roundness` 1 (all 0 to 1), `center`
[0.5, 0.5], `color` black, `mode` `color` (paints the colour into the edges, over transparent areas too) or `alpha`
(fades the edges to transparent).

**lightLeak** (4.0.500, T1): `seed` 0, `hueShift` 0 (0 to 360, throws outside; 0 yellow-orange, 120 green, 240
blue), `progress` 0.5 (reveals in the first half, retracts in the second). Normal alpha composite over the source:
on a transparent `<Solid>` it is an overlay. The deprecated `<LightLeak>` from `@remotion/light-leaks` (WebGL1, a
Sequence, accepts `style={{mixBlendMode: 'screen'}}`) still works on 4.0.528 and goes away in 5.0.

**glow** (4.0.468, T2: four passes): `radius` 20, `intensity` 1, `threshold` 0, `color` white; monochrome and
additive (neon lines on the floor ground). **shine** (4.0.468): `progress`, `angle` 30, `haloSigma` 200,
`coreSigma` 65, `haloIntensity` 0.3, `coreIntensity` 0.4; a sweep masked by alpha.

**blur** (radius required) and the progressive blurs (`radialProgressiveBlur` for a soft focus fall-off) are heavy
(two passes, up to 65 taps): avoid big blurs on full-frame grounds; draw soft shapes with gradients instead.

## 5. Order in a chain

Replacing generators first; then masks (`evolve`, `pixelDissolve`); then anything that reads alpha (`glow`,
`dropShadow`, `outline`); grade before stylise before texture (`paper`, `burlap`) before lens before `vignette`;
grain (`noise`) last. Group same-backend effects (a 2D effect between two WebGL ones costs two bridges, one of them
asynchronous).

## 6. Cost tiers (relative, from the shaders)

- T0, cheap: single pass, a few reads (gridlines, waves and the line family, starburst, linearGradient, noise,
  vignette, halftone, dotGrid).
- T1, moderate: procedural single passes (liquidContours, contourLines, burlap, lightLeak, pattern); paper is the
  heaviest single pass.
- T2, heavy: blur and progressive blurs, glow and dropShadow (four passes), zoomBlur and lightTrail (up to 64
  samples).
- CPU per frame: brightness, contrast, tile (pixel readback and a JavaScript loop).
- `pixelDensity` multiplies the pixel count by its square.

## 7. Errors and fixes

| Message | Cause | Fix |
|---|---|---|
| `Failed to acquire WebGL2 context for ... Pass --gl=angle` | no GL | `--gl=angle` (or swangle without a GPU) |
| `"progress" must be <= 1`, `"amount" must be <= 1` | unclamped interpolate or spring overshoot | clamp both ends |
| `"seed" must be <= 1000` (paper, roughenEdges) | seed driven by the frame | `seed: frame % 1000` or `frame * 0.1` clamped |
| `"hueShift" must be <= 360` | lightLeak hue animation | `(frame * 2) % 360` |
| `"rays" must be between 2 and 100`, `"colors" must be an array with at least 2 colors` | starburst | pass both |
| `"origin" must contain coordinates between 0 and 1` | starburst origin | clamp |
| `"thickness" must be ...` greater than 0, `"wavelength"` | line family | positive values |
| `"complexity"`, `"smoothness"` must be between 0 and 1 | liquid/contour lines | clamp |
| `WebGL context was lost ...` | context or memory pressure | fewer effect components, lower concurrency or pixelDensity |
| Stripes stair-step | hard edges on a leaned pattern | angle 0 or 90, pixelDensity 2, or a 1 px blur |
| Gradient bands after encoding | 8-bit pipeline | noise 0.02 to 0.04 last, CRF 18 or lower |
| Paper looks blue | default `colorFront` #9fadbc | pass near-white front and back colours from the sheet |
| A starburst ground is black where the palette had `transparent` | starburst drops alpha | use opaque colours, fade with `vignette({mode: 'alpha'})` |

## 8. Recipes (raw Remotion)

Blueprint:
```tsx
<Solid width={width} height={height} color="#0b2545" effects={[
  gridlines({gridSize: 24, lineWidth: 1, lineColor: 'rgba(255,255,255,0.12)'}),
  gridlines({gridSize: 120, lineWidth: 2, lineColor: 'rgba(255,255,255,0.3)'}),
]} />
```

A seamless liquid loop over the whole composition:
```tsx
<Solid width={width} height={height} color={bg} effects={[
  liquidContours({firstColor: bg, secondColor: tint, spacing: 110, scale: 520, phase: 3.23 + frame / durationInFrames}),
]} />
```

Sunburst with a fade:
```tsx
<Solid width={width} height={height} color={bg} pixelDensity={2} effects={[
  starburst({rays: 24, colors: [bg, tint], rotation: (frame / fps) * 4, smoothness: 0.08, origin: [0.5, 0.62]}),
  vignette({amount: 0.9, radius: 0.3, feather: 0.7, mode: 'alpha'}),
]} />
```
(pixel params are not used by starburst, so doubling the density only smooths the rays).

Notebook paper: `paper({amount: 0.38, contrast: 0.18, roughness: 0.18, fiber: 0.28, crumples: 0.1, folds: 0.12,
seed: 24, scale: 0.8, drops: 0})` then `gridlines({gridSize: 54, lineWidth: 3.4, lineColor: 'rgba(76, 101, 128,
0.16)'})` (the values the Notebook Paper Element uses; give `colorFront` and `colorBack` near white to avoid the blue
tint).
