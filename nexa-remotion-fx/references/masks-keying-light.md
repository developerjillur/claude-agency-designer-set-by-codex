# Masks, keying, blending and light

## Masks

Everything here is synchronous CSS on the DOM, so every frame is complete when it is captured (an image used as a
mask could still be loading).

| Technique | How | Good for | Limits |
|---|---|---|---|
| `clip-path: path('...')` | an SVG path string, from `@remotion/shapes` `makeX()` or `@remotion/paths` | shapes growing from a point, logo reveals | hard edge; the path is in element pixels |
| `clip-path: inset() / circle() / polygon()` | CSS shapes | wipes, iris, diagonal reveals | hard edge |
| `mask-image` gradients | `linear-gradient`, `radial-gradient`, `repeating-linear-gradient` (`-webkit-` too) | soft wipes, fades to an edge, blinds, soft circles | combine several with `mask-composite` (intersect) |
| SVG `<clipPath>` holding `<text>` | `clip-path: url(#id)` on the fill | words filled with a picture or video | ids must be unique: `useId()` |
| `mask-image: url(file)` | a PNG or SVG in `public/` | complex art masks (the transitions-video example masks a TransitionSeries with a word PNG) | loads asynchronously: prefer inline paths |
| Effects | `evolve`, `pixelDissolve`, `venetianBlinds`, `halftoneLinearGradient` on an effects host | pixel-level reveals | WebGL; counts toward the context limit |

Building paths: `makeCircle({radius})`, `makeRect({width, height, cornerRadius})` (or `edgeRoundness`, never both),
`makeStar({points, innerRadius, outerRadius, cornerRadius})`, `makePolygon({points, radius})`, `makeHeart({height})`,
`makeTriangle({length, direction})`, `makeCallout`, `makePie({radius, progress})`, `makeArrow`, `makeSpark` return
`{path, width, height, transformOrigin, instructions}`; `translatePath`, `scalePath` (scales around the top-left),
`centerPath(d, {x, y})` (4.0.486), `getBoundingBox(d)` place them. The kit adds `shapePath({shape, cx, cy, size,
aspect, radius, points, inner, rotate})`, `coverSize()` (the size that covers the frame from a point) and
`rotatePath()`.

Reveal sizes: to cover the frame from (cx, cy) a circle needs a radius of the distance to the farthest corner; a star
needs that divided by its inner-radius ratio; a rect needs the larger of the half height and the half width divided
by its aspect.

The kit's components: `ShapeMask` (growing shape, optional `ring` edge line, `spin`, soft edge on circles), `WipeMask`
(linear from 8 sides or any angle, radial, split, blinds; soft `feather`), `GradientMask` (fade to an edge, all edges,
radial, invert), `TextMask` (see below). All take `progress` or `delay`/`duration`/`exit`; exits end on the last frame
of the Sequence.

### Text filled with a picture or video

- The kit's `TextMask` renders real SVG `<text>` inside a `<clipPath>`: the browser shapes it, so Bangla conjuncts and
  vowel signs are right, and nothing is split into letters.
- It waits for its fonts (`document.fonts.load` under `delayRender`) and fits the longest line to `fit` of the safe
  width (measured with a canvas at 100 px), capped by `maxSize`. Lines come from '\n'.
- Fill with `src` (image or video by extension), `gradient`, or any children (a `<Video>`, a TransitionSeries of
  colour fields, a starburst). `fillZoom` pushes the fill slowly inside the letters.
- An outline is drawn under the fill at twice the width, so the overlapping contours inside variable-font glyphs
  never show as lines through the letters.
- Heavy, wide faces (weights 800 to 900) show the fill best; keep 2 to 6 letters a line for a hero word.

## Keying

`colorKey({keyColor, similarity, smoothness, spillSuppression})` (4.0.472, WebGL2): each pixel's RGB distance to the
key colour (normalised) inside `similarity` becomes transparent, a smoothstep band of `smoothness` around it gives a
soft edge, and spill suppression caps the dominant key channel at the average of the other two.

Tuning order:

1. Sample the real screen colour from the footage (a studio green is about #1fbf4f to #00b140, never #00ff00).
2. Raise `similarity` until the screen is gone everywhere (0.2 to 0.45); stop before the subject gets holes.
3. `smoothness` 0.05 to 0.1 for the edge; hair and motion blur want the upper end.
4. `spill` 0.5 to 0.9 removes the green fringe and green bounce on skin.
5. A garbage matte (the kit's `matte` crop, or a clip-path) removes rigs, floor, shadows and anything the key cannot:
   do it before an outline, which draws around every leftover speck.
6. Then `outline` (sticker edge) and `dropShadow` (grounding), both reading the keyed alpha; leave transparent
   margin inside the host or they clip at its edge.
7. Grade the subject toward the plate: temperature, contrast, black level; add a soft contact shadow; a faint light
   wrap (the plate's colour blurred onto the subject's edge) sells the composite.

`ChromaKey` does 1 to 6 on a `<Video>` from `@remotion/media` or an `<Img>`; `keyEffects(opts, unit)` returns the
chain for your own host.

## Blend modes instead of keys

Footage shot on black (sparks, flares, smoke, dust, fire, light leaks, bokeh) is additive light: lay it over the
scene with `mix-blend-mode: screen` (or `plus-lighter`, or `lighten` to keep only brighter pixels). Keying black
instead cuts hard edges into soft light and throws away the glow (DemoFxKey shows both). Footage or art on white
(ink, paper textures, line drawings, shadows) uses `multiply`. Grain and texture plates use `overlay` or `soft-light`.

- Crush the noise floor first: "black" footage is dark grey with noise, which screen turns into a veil. The kit's
  `BlendVideo` puts `levels({blackPoint: crush})` on the clip before blending (`crush` 0.04 to 0.1); for multiply it
  pushes near-white to white.
- A blend mode mixes with what is behind it inside the same stacking context. A parent with `isolation: isolate`,
  `opacity` below 1, `filter`, `transform` in 3D or `clip-path` starts a new context and the layer blends with
  nothing: put the clip, opacity or transform on the blended element itself.
- In Remotion blend modes on overlays work normally (one DOM); the "renders white" trap belongs to per-track
  compositors, not to Remotion.

## Light leaks

- Effect: `lightLeak({seed, hueShift, progress})` (4.0.500) on a transparent `<Solid width height>` over the scene:
  it grows over progress 0 to 0.5 (full cover at 0.5) and retracts from 0.5 to 1 with a second pattern. `hueShift`
  0..360 (throws outside: wrap it), `seed` any number (each gives a different shape).
- Hue map measured on renders: 0 warm yellow-orange, 30 coral, 60 rose, 90 magenta, 135 violet, 180 blue, 210 cyan,
  240 teal, 280 green, 320 lime. The kit's `LEAK_HUES` names these.
- Composite: the effect draws with normal alpha; put the Solid in `mix-blend-mode: screen` to add light instead
  (the kit's `LightLeak` does, at 0.85 opacity).
- Over a cut (it hides the switch): `<TransitionSeries.Overlay durationInFrames={30 to 40}>` or the kit's
  `tr.leak()`; as a transition that changes the scenes under its peak: `tr.lightLeakCross()`.
- Over a title: a full leak covers the frame at its middle. Use the kit's `peak` (0.5 to 0.7): it swells to that
  coverage and falls back the same way.
- Deprecated: `<LightLeak>` from `@remotion/light-leaks` (4.0.415, WebGL1, a Sequence the size of the composition,
  takes `style` so `mixBlendMode: 'screen'` works, `hueShift` 0..360). Still works on 4.0.528, removed in 5.0.
- A light-leak video over a cut works too (screen blend, the hard switch at the brightest moment, playbackRate
  stretched to the transition).

## Starburst

- Effect: `starburst({rays, colors, rotation, smoothness, origin})` (4.0.500) replaces the source: use it on a
  `<Solid>`. `rays` 2..100, `colors` at least 2 (alpha dropped), `origin` 0..1 (throws outside), `smoothness` 0 is
  aliased: use 0.03 to 0.05. Rotation any number (the kit wraps it). No vignette parameter: add `vignette()` (or
  `vignette({mode: 'alpha'})` for the old fade-out) and 2 percent `noise` against banding.
- Deprecated `<Starburst>` from `@remotion/starburst` (4.0.435, WebGL1) had `vignette` and `originOffsetX/Y`; removed
  in 5.0.
- Retro sunburst: 24 to 28 rays, two close tints of one colour (the kit defaults to the theme accent and an accent 14
  percent lighter), 4 to 8 degrees a second, vignette 0.35.

## Shine and tear

- `shine({progress, angle, haloSigma, coreSigma, haloIntensity, coreIntensity})` (4.0.468): a white band masked by
  the host's alpha. On `HtmlInCanvas` around a logo or product cut-out (the Shine Element scales the content to 0.75
  first so the band has room), progress 0 to 1 over about 44 frames, eased in-out. The kit's `Shine` does this
  (canvas) or a soft-light CSS band clipped to a box (css). Box shadows inside the canvas are clipped: keep them
  outside.
- `tear({progress, angle, rotation, jaggedness})` (4.0.523): paper rip; progress 0 intact, 1 reaches the far edge,
  above 1 the halves keep flying apart (animate 0 to 1.2 to 1.6 for an exit). Jaggedness 20 to 24, rotation 15 to 20,
  over 10 to 30 frames with a damping-200 spring. Put a ground behind: the gap is transparent.

## Motion blur on fast moves

- `<CameraMotionBlur shutterAngle={180} samples={5 to 8}>` from `@remotion/motion-blur` renders the children at
  sub-frame times and averages them (children must read `useCurrentFrame()` inside and fill an AbsoluteFill); it
  costs samples times the render and darkens colours with many samples.
- `<Trail layers lagInFrames trailOpacity>` gives echo copies (a stylised streak).
- For one direction, a directional blur from the speed is cheaper: SVG `feGaussianBlur stdDeviation="sd 0"` (the kit's
  `whipPan` does this), or `blur({radius, vertical: false})` on an effects host.
