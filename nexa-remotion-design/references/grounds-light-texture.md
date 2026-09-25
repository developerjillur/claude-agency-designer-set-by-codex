# Grounds, light and texture

What every frame stands on, how it is lit, and the surface texture that makes it read as a made thing rather than a
browser page. Kit components first, then the raw Remotion way for anything the kit does not cover.

## 1. The rule: no vacuum

A flat solid colour behind small floating content is the most common tell of generated video. Every frame sits on
a lit ground: a light with a source and a falloff, a band or floor that gives a horizon, a texture, or depth
(parallax). Light must behave like light:

- It comes from somewhere: a source above or beside the frame, or behind the subject. A glow with no source (a halo
  around text) is a defect.
- It falls off: brighter near the source, a shade towards the far side. One light direction per film; shadows fall
  away from it (the kit's elevation shadows fall straight down: light from above).
- Text parked in the brightest core of a light on a dark ground loses contrast. Put the pool behind the subject
  (a picture, a number, a product) and the small text in the quieter part.
- Flat can be a choice (Swiss, brutalist, some editorial looks): then the grid, the type and the rules carry the
  frame, and the flatness is deliberate across the whole film.

Decide dark or light from a written scene sentence ("a product on a desk at night", "a printed page on a table"),
never silently default to dark.

## 2. Kit grounds and when to use them

| Need | Kit | Notes |
|---|---|---|
| The default ground of any scene | `<Ground>` (lit) | light from `[0.3, -0.25]`, soft falloff, drifts 5% over the scene |
| Stage light behind a subject | `<Ground kind="spot">` | pool at `[0.5, 0.42]`; subject in it, small text outside it |
| Horizon or table-top | `<Ground kind="band" split={0.64..0.72}>` | floor band lit from the same source, contact shade at the seam |
| Column or sidebar | `<Ground kind="band" direction="vertical">` | a two-tone split without a hard layout seam |
| Deliberately flat | `<Ground kind="solid">` | still gets the theme's grain and vignette |
| A soft wash of the brand's hues | `<Gradient>` | OKLab, dithered; `drift` for slow life |
| A moving colour field (launch, product, glass) | `<Mesh>` | 3 to 5 blobs on noise, grain against banding |
| Tech, architecture, plans | `<EffectGround kind="blueprint">` | two gridlines, fine and coarse |
| Calm, organic, wellness, flow | `<EffectGround kind="liquid" loop>` | liquid contour bands, seamless loop |
| Kids, summer, playful | `<EffectGround kind="waves" loop>` | double density to smooth hard edges |
| Retro sale, opening, sports | `<EffectGround kind="starburst">` | rays fade out at the edges |
| Maps, data, outdoors, science | `<EffectGround kind="contours">` | topographic lines drifting |
| Night, synthwave, gaming | `<EffectGround kind="floor">` | perspective grid floor, horizon glow |
| Printed, Vox collage, notebook | `<Paper grid={106}>` / `<Paper rules={56} margin="#E4312B">` | shader paper or CSS paper |
| A photo or video under text | `<FullBleed src>` (layout) | scrim from the text's side |

Every ground takes `children` and puts the theme's finish (vignette and grain) over them. On a custom background
add `<Finish />` last.

Themes set the texture dials (`texture.grain`, `texture.vignette`): studio, keynote, swiss, corporate, data,
playful, fresh, terminal, brutalist 0 and 0; editorial 0.02 and 0; whiteboard 0.02 and 0; midnight 0.03 and 0.25;
neon 0.04 and 0.4; dhaka 0.04 and 0.2; kinetic 0.05 and 0; luxury 0.06 and 0.5; trailer 0.1 and 0.55; retro 0.12
and 0.45; vox 0.16 and 0.3.

## 3. Light on a ground, the numbers the kit uses

- Light themes: the light colour is the ground mixed 65% towards white; the far corner is the ground darkened by
  0.055 in OKLab lightness. Dark themes: the light is the ground mixed 10% towards the text colour tinted 30% by
  the accent; the far side darkens only 0.015 (keep blacks lifted).
- The ramp is drawn with 9 eased stops (smoothstep between stops). A two- or three-stop CSS gradient over a whole
  frame shows its stops as rings.
- Drift: the light moves 5% of the frame width over the scene with a sine curve. The movement is felt, not seen,
  and gives held shots life without moving what is being read.

Raw Remotion (no kit), the same idea:

```tsx
const frame = useCurrentFrame();
const {durationInFrames} = useVideoConfig();
const p = interpolate(frame, [0, durationInFrames], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
const x = 30 + 5 * (p - 0.5);
<AbsoluteFill style={{background: `radial-gradient(ellipse farthest-corner at ${x}% -25% in oklab, #fbfbfc 0%, #f5f6f7 42%, #e6e8ea 100%)`}} />
```

## 4. Gradients

- Interpolate in OKLab (`linear-gradient(135deg in oklab, ...)`): sRGB mixing between distant hues dips to a grey
  or brown middle (red to green is the worst). `interpolateColors()` accepts `oklch()` and `oklab()` strings since
  4.0.439; the kit's `mix()` mixes in OKLab in JavaScript.
- Keep at least two real colour stops and prefer tonal gradients (the ground to a tint of the accent) over two
  saturated hues. Purple to blue as a default is on the anti-slop list.
- Conic gradients have a pinch point at the centre: put the centre off the text (the kit's default fans up from
  below the frame).
- Banding: 8-bit H.264 turns a smooth dark gradient into visible rings. Measured on a keynote radial gradient at
  CRF 23: without dither the rings are obvious once the contrast is stretched; with a still 3.5% noise they break
  up. The dither cost 130 KB for a second of 1080p. Add 2 to 4% grain to every large gradient, avoid huge soft
  blurs, and render masters at CRF 14 to 18 (`--image-format=png` or `--jpeg-quality=100` when flat gradients
  matter).
- Slow life: rotate a linear or conic gradient 2 to 12 degrees a second, or orbit a radial centre. Faster reads as
  a screensaver.

## 5. Mesh (moving colour field)

The kit draws 3 to 5 CSS radial gradients (`circle R at x y in oklab`) with an eight-stop gaussian-like falloff
(1, 0.9, 0.72, 0.5, 0.3, 0.14, 0.04, 0), stacked over the ground. Centres wander on `noise2D(seed, t * 0.085 *
speed, lane)` by 16% of the frame; radii breathe 12%; anchors sit near the corners and the middle; radii are 42 to
62% of the long side. No CSS blur filter (slow, and blurs band). Grain at least 0.05, moving, because moving
gradients band more visibly than still ones.

Colours: light themes mix the ground 25 to 45% towards accent, accent2 and highlight, plus bg2; dark themes 30 to 55%.
A mesh is the one ground where glass cards read (they need a busy backdrop).

## 6. Grain

The kit's grain: a 256 px tile of the mean of three uniform draws per pixel (clusters like film grain), made once
per tab with a seeded generator (mulberry32), drawn on a full-frame canvas at a seeded random offset and flip per
plate, `size` 1.25 px at 1080 with smoothing. SVG `feTurbulence` cannot draw grain this fine and Chrome draws SVG
filters on the CPU.

Calibration (measured, luma standard deviation on flat patches, amount 0.16):

| Blend | #f4f4f4 | #d9d7d1 | #8a8a8a | #3a3a3a | #101010 | Mean shift |
|---|---|---|---|---|---|---|
| signed (default) | 6.6 | 6.4 | 6.0 | 6.2 | 6.6 | light -7, black +7 levels |
| overlay | 0.7 | 2.2 | 6.4 | 3.2 | 0.9 | none |
| soft-light | 0.5 | 1.7 | 3.5 | 3.4 | 1.7 | none |

So `amount` gives about 40 x amount levels of spread on a mid-grey in every mode; signed specks are the only mode
that shows on near-white and near-black (overlay grain vanishes there), and they lift blacks a little, which suits
film looks. Use `blend="overlay"` when pure whites must stay pure (UI on white).

Rate and file size (5 s of 1080p30, H.264 CRF 18, vox ground):

| Grain | File |
|---|---|
| none | 0.9 MB |
| 0.16 still | 1.6 MB |
| 0.16 at 3 Hz | 8.4 MB |
| 0.16 at 6 Hz | 14.5 MB |
| 0.16 at 12 Hz | 21.7 MB |
| 0.16 every frame (30 Hz) | 53.6 MB |
| 0.06 at 12 Hz | 11.5 MB |
| 0.03 at 12 Hz | 5.4 MB |

12 plates a second reads as film; every frame reads as electronic sizzle and multiplies the file. For long uploads
use 6 or 3 Hz (the Vox template in nexa-video-creator swaps six plates every 10 frames), or a still grain. The
community's rule of thumb: re-encode grainy masters with `-crf 19 -tune film`.

Raw Remotion alternatives: `noise({amount: 0.05, seed: Math.floor(frame / 2.5), premultiply: true})` from
`@remotion/effects/noise` on a canvas host (`<Solid>`, `<Video>` from @remotion/media, `<Img>`), last in the effect
chain. `premultiply: true` makes grain follow brightness like film.

## 7. Vignette

Weak: corner darkness about 0.15 for a "printed" look, up to 0.25 to 0.3 for trailers. The kit maps the theme's
`texture.vignette` to corner alpha = half of it, in the ground's own hue on light themes (a grey vignette on a warm
paper looks dirty), black on dark themes, centred slightly above the middle (0.46) like a lens, with eased stops.
The effect version is `vignette({amount, radius, feather, roundness, color, mode, center})` (all 0 to 1 except
center; `mode: 'alpha'` fades edges to transparent, useful to fade a pattern out).

## 8. Paper

The `@remotion/effects/paper` shader (4.0.486, WebGL2, the heaviest single pass, cheap when still because the chain
only re-runs when params change). Parameters: `amount` 1, `colorFront` #9fadbc, `colorBack` #ffffff, `contrast`
0.3, `roughness` 0.4, `fiber` 0.3, `fiberSize` 0.2 (0.01 to 1), `crumples` 0.3, `crumpleSize` 0.35 (0.01 to 1),
`folds` 0.65, `foldCount` 5 (0 to 15), `drops` 0.2, `fade` 0, `seed` 6 (0 to 1000, validated), `scale` 0.6 (0.01 to
4). What the source shows:

- The paper tone multiplies the sheet by a mix of `colorFront` and `colorBack` at 65%: the blue-grey default front
  colour tints any sheet blue. The kit passes `colorFront = mix(white, sheet, 0.55)`, `colorBack = white`.
- A flat sheet comes out about a fifth darker (lighting term plus a -0.1 shift at the default contrast). The kit
  lifts the source by `0.14 x amount` in OKLab lightness; measured mean 211 against a target of 217 on the vox
  ground (the rest is the grain's shift).
- Roughness is sampled per canvas pixel (`gl_FragCoord`), the rest in UV: at 4K the tooth is finer.
- Kit defaults for a fine sheet: amount 0.5, fibers 0.2, crumples 0.1, folds 0.05, roughness 0.22, scale 0.8,
  contrast 0.18. Fibers 0.4 and up read as craft paper; folds above 0.3 as a crumpled sheet.
- Stop-motion paper: re-seed every 8 to 30 frames (`boil`); the Remotion Paper Texture Element re-rolls every 30
  frames with `interpolate(frame, [0, 120], [0, 1000], {posterize: 30})`.

The CSS fallback (and the kit's `engine="css"`): the ground colour, two soft-light layers of the grain tile scaled
26x and 11x (mottling), a streak layer (the tile stretched 9x by 0.8x: horizontal fibres), a still printed grain
and a radial lit-sheet falloff. It matches the shader's mean tone and needs no WebGL.

Grid like the Vox look: two CSS linear gradients (one per axis), a 1.7 px line with 0.9 px soft edges at the
text colour's 8%, cells of about 106 px, centred on the frame (`offset = (width % cell) / 2`). Notebook: horizontal
rules every 56 px and a red margin line at 9% of the width.

## 9. Patterns

Quiet by default: grid lines 9%, dots 16%, crosses 28%, stripes 6%, rules 12%, checker 4.5% of the text colour, 1.5x
on dark themes. Fade them towards a side or the middle so text sits on a clean area (`fade="center"` keeps the
middle, `edges` clears it). Hard edges alias when leaned: the kit draws stripes with a one pixel ramp on each edge;
the effects' line family (`lines`, `waves`, `zigzag`, `checkerboard`) has hard, non-antialiased edges, so keep their
angles at 0 or 90 or draw at `pixelDensity` 2. Drift patterns slowly (10 to 20 px a second) or not at all.

Halftone (dot size by position, a print or comic look): the kit draws dots on a canvas on a rotated grid, radius
following the fade shape. The effects version is `halftoneLinearGradient({firstStopDotSize, secondStopDotSize,
firstStopPosition, secondStopPosition, gridSize, colorMode, dotColor, maskToSourceAlpha})`; `halftone()` turns the
source's luminance into dots and drops everything between them (put a paper layer behind).

## 10. Spotlight and light sweep

- Spotlight: veil the rest with the ground's own colour at about 60% (light themes fade back, dark themes darken),
  one element in focus, move to the next element on its cue with ease in-out. This is the staging principle "dim
  what already paid off". A box-shaped hole (a huge spread box-shadow around an empty box with a blur for the soft
  edge) fits UI better than a circle.
- Light sweep: a specular pass on a named beat (a price, a logo, a reveal), two or three in 45 s. Lean a straight
  gradient band with `skewX` (the edges stay clean), 26 to 30 frames at 30 fps with a sine curve, `screen` on dark
  surfaces, `soft-light` on mid tones; invisible on pure white, as in life. The effects version `shine({progress,
  angle, haloSigma, coreSigma, haloIntensity, coreIntensity})` needs a canvas host and, for DOM, `<HtmlInCanvas>`
  (preview needs a Chrome flag).
- Light leaks over a cut belong to the fx family (`lightLeak()` from `@remotion/effects/light-leak` on a transparent
  `<Solid>` inside `<TransitionSeries.Overlay>`), not to the ground.

## 11. Checks on the contact sheet

- Is there a light with a source on every frame (or is flat a stated choice)?
- Does text sit outside the brightest part of a dark spot?
- Is the grain visible at full size in a mid-tone crop (not just on the sheet)? Is the rate right for the length?
- Stretch the contrast of a dark gradient frame (`ffmpeg -vf colorlevels=rimax=0.16:gimax=0.16:bimax=0.16`) on the
  encoded file: rings mean more dither or grain.
- Paper: the sheet should not look blue-grey or darker than the brand ground.
