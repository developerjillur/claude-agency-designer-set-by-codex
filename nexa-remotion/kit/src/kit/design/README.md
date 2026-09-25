# design: grounds, textures, surfaces, layout and colour

Everything a scene stands on and is arranged with: lit grounds, gradients and a moving mesh, grain, vignette,
paper, patterns, WebGL effect grounds, a spotlight and a light sweep; cards, pills, badges, scrims, frames, a
border and an app panel; layout helpers that adapt to 16:9, 1:1, 4:5 and 9:16; decorative shapes; colour helpers
and brand kits. Every part reads the theme (`useTheme()`), sizes itself with `unit` and stays inside `safe`.

```tsx
import {Ground, Card, Grid, Pill} from './kit/design'; // or from './kit' once the kit index exports design
```

Demos: `nrk.py demos --module design` (Grounds, GroundsTall, Gradients, Mesh, Effects, Textures, Paper, Grain,
Patterns, Cards, Elevation, Surfaces, More, Layouts in 16:9, 9:16, 1:1 and 4:5, Shapes, Color).

Units: every size prop is px at a 1080 px short side (the component multiplies by `unit`). Colours default to the
theme's; any prop colour takes any CSS colour.

---

## Grounds

### Ground

The theme's ground as a lit surface. `<Ground>{scene}</Ground>` is a complete stage: the ground, then the scene,
then the theme's vignette and grain over everything (the finish).

| Prop | Default | Notes |
|---|---|---|
| `kind` | `'lit'` | `lit`: light from a source above the frame with a falloff; `spot`: a pool behind the subject; `band`: a two-tone floor or column; `solid`: flat (for Swiss, brutalist) |
| `color` | `t.colors.bg` | the ground |
| `color2` | `t.colors.bg2` | the band; if bg2 is too close to bg, a visible step lighter or darker is used |
| `light` | lit `[0.3, -0.25]`, spot `[0.5, 0.42]` | the source in frame fractions; may be outside 0..1 |
| `intensity` | `1` | 0 to 2 |
| `split` | `0.64` | band seam position |
| `direction` | `'horizontal'` | band: `horizontal` is a floor, `vertical` a column |
| `seam` | `'soft'` | `hard` or `soft` |
| `drift` | `0.05` | how far the light travels over the Sequence (fraction of the frame) |
| `grain`, `vignette` | theme | a number, or `false` to switch off |
| `dither` | `true` | a still 0.03 noise when the theme has no grain, so the light does not band in H.264 |

```tsx
<Ground kind="band" split={0.7}>
  <SafeArea>
    <Title />
  </SafeArea>
</Ground>
```

Gotchas: light themes get a white light and a soft shade towards the far corner; dark themes get a cool lift tinted
by the text and accent colours. Text parked in the brightest point of a dark `spot` loses contrast: keep the spot
behind the subject, not behind small text.

### Finish

The theme's vignette and grain as the top layers: grounds add it; use it alone on custom scenes (last child).
Props: `grain` and `vignette` (number or `false`), `dither` (a still noise amount when grain is 0).

```tsx
<AbsoluteFill>
  <MyCustomBackground />
  <Content />
  <Finish />
</AbsoluteFill>
```

### Gradient

Linear, radial or conic colour, interpolated in OKLab (`in oklab`), dithered, optionally drifting.

| Prop | Default | Notes |
|---|---|---|
| `kind` | `'linear'` | `linear`, `radial`, `conic` |
| `colors` | a tinted wash from the theme | at least 2 |
| `stops` | even | 0 to 1 per colour |
| `angle` | linear 135, conic 0 | degrees |
| `center` | radial `[0.5, 0.42]`, conic `[0.5, 1.1]` | the conic default is a fan rising from below the frame, so its pinch point is not behind the text |
| `drift` | `0` | degrees a second (linear, conic); radial: the centre orbits |
| `space` | `'oklab'` | `oklab`, `oklch`, `srgb` |
| `dither` | `0.035` | still noise against banding |

```tsx
<Gradient colors={['#FF6B6B', '#2E86AB']} angle={90}>
  <Content />
</Gradient>
```

Gotchas: sRGB interpolation between far hues dips to grey in the middle (see DemoDesignGradients). Keep the dither
on: without it, wide dark gradients show rings after H.264 encoding (measured, see the skill's references).

### Mesh

A soft moving colour field: 3 to 5 radial blobs whose centres and sizes drift on seeded noise, drawn as CSS
gradients with a gaussian-like falloff (no blur filter), with grain.

| Prop | Default | Notes |
|---|---|---|
| `colors` | from the theme's accents softened into the ground | 2 to 5 |
| `base` | `t.colors.bg` | under the blobs |
| `speed` | `1` | a full wander takes about 12 s; 0 is still |
| `wander` | `0.16` | travel, fraction of the frame |
| `size` | `1` | blob size multiplier |
| `seed` | `'mesh'` | |
| `grain` | theme, at least 0.05 | moving gradients band without grain |

```tsx
<Mesh>
  <Center>
    <Card variant="glass">Version 4.0</Card>
  </Center>
</Mesh>
```

Gotchas: the anti-slop list names "purple and blue gradients by default"; the mesh takes the theme's accents, so
choose the theme first. A mesh is the right ground for glass cards: glass needs a busy, moving backdrop.

### EffectGround

Moving pattern grounds drawn by `@remotion/effects` on a `<Solid>` (WebGL2), coloured from the theme, every
parameter clamped to its valid range.

| `kind` | Effect stack | Default contrast |
|---|---|---|
| `blueprint` | two `gridlines` (24 and 120 px) panning | 0.5 |
| `liquid` | `liquidContours`, phase in band cycles | 0.15 |
| `waves` | `waves`, scrolling | 0.14 |
| `starburst` | `starburst` (24 rays) + `vignette` in alpha mode | 0.14 |
| `contours` | `contourLines` drifting east | 0.5 |
| `floor` | a perspective `gridlines` plane under a sky gradient, `glow` on the lines | 0.8 |

Props: `colors` (`[ground, pattern]`), `contrast` (0 to 1), `speed` (default 1), `scale`, `seed`, `loop` (liquid and
waves move a whole number of cycles over the Sequence so it loops), `pixelDensity` (default 2 for waves and
starburst, whose edges are hard; 1 otherwise), `grain`, `vignette`, `children`.

```tsx
<EffectGround kind="liquid" loop>
  <Copy />
</EffectGround>
```

Gotchas: needs `--gl=angle` in renders (nrk passes it; `Config.setChromiumOpenGlRenderer('angle')` in the kit's
remotion.config.ts). Without WebGL2 it warns once and draws a lit `Ground` instead of failing the render. With
`--gl=swangle` (no GPU) it works about 15 times slower. Each `EffectGround` holds two WebGL2 contexts: keep a few
per frame, not dozens (Chrome drops the oldest contexts past about 16). Animated params re-run the shader every
frame; still params run once per tab.

---

## Texture and light

### Grain

Film grain: a seeded 256 px noise tile made once per tab, drawn onto a full-frame canvas at a new random offset
(and flip) 12 times a second.

| Prop | Default | Notes |
|---|---|---|
| `amount` | `t.texture.grain` | about `40 x amount` levels of luma spread on mid-grey: 0.16 printed paper, 0.05 a whisper |
| `rate` | `12` | plates a second; each plate is held a whole number of frames; `0` = still |
| `size` | `1.25` | px at 1080 per grain |
| `blend` | `'auto'` (= `signed`) | `signed`: white and black specks with alpha, visible on every tone, lifts blacks slightly; `overlay` / `soft-light`: keep pure white and black clean but vanish there |
| `seed` | `'grain'` | |

```tsx
<AbsoluteFill>
  <Scene />
  <Grain amount={0.1} rate={6} />
</AbsoluteFill>
```

Gotchas: grain is the most expensive thing to encode. Measured on 5 s of 1080p30 at CRF 18 (vox ground): no grain
0.9 MB, still 0.16: 1.6 MB, 0.16 at 3 Hz: 8.4 MB, 6 Hz: 14.5 MB, 12 Hz: 21.7 MB, every frame: 53.6 MB; 0.06 at 12 Hz:
11.5 MB, 0.03 at 12 Hz: 5.4 MB. Use `rate={6}` or `3` on long uploads, and never per-frame grain.

`grainTile(kind)`, `grainUrl(kind)` and `useGrainUrl(kind)` give the tile as a canvas, a CSS `url()` and a CSS
`url()` that holds the render until it is decoded (use the hook for backgrounds shown on frame 0).

### Vignette

Darkened corners in the ground's own hue (black on dark themes). Corners get half the amount as darkness, with eased
stops (no visible ring). Props: `amount` (theme), `color`, `center` (`[0.5, 0.46]`), `size` (1).

```tsx
<Vignette amount={0.3} />
```

Gotchas: weak is right (corner alpha about 0.15 for the vox theme). A visible vignette reads as an Instagram filter.

### Paper

A sheet of paper as the ground: the `@remotion/effects` paper shader on a `<Solid>`, with a CSS fallback, an
optional grid or ruled lines, a still printed grain and the soft falloff of a lit sheet.

| Prop | Default | Notes |
|---|---|---|
| `color` | light themes `bg`, dark themes `surface` | the shader darkens a flat sheet; the source is lifted to keep this colour |
| `amount` | `0.5` | texture strength |
| `fibers`, `crumples`, `folds`, `roughness` | 0.2, 0.1, 0.05, 0.22 | fibres 0.4 and up read as craft paper, folds above 0.3 as crumpled |
| `scale` | `0.8` | 0.01 to 4 |
| `seed` | `6` | 0 to 1000 |
| `boil` | `0` | re-seed every N frames (stop-motion paper); still is cheapest |
| `grid` | `false` | cell px at 1080 (the Vox look: 106) |
| `rules`, `margin` | `false` | notebook lines and a margin colour |
| `lineColor`, `lineWeight` | text at 8%, 1.7 | |
| `engine` | `'auto'` | `webgl` (shader), `css` (mottling from the grain tile), auto picks webgl when WebGL2 exists |
| `grain` | theme, at least 0.06 | still |
| `light` | `1` | lit-sheet falloff |

```tsx
<Paper grid={106}>
  <VoxBeat />
</Paper>
```

Gotchas: the shader's default front colour is a blue-grey that tints the sheet; the kit passes near-white tones
derived from `color` instead. Both engines were matched to the same mean tone (see DemoDesignPaper). Paper's grain is
still (the tooth of the sheet) and its lit-sheet falloff replaces the theme's vignette; for the filmed-collage boil
add `<Grain rate={3} />` as the last layer.

### Spotlight

Veils everything except one place, and can travel to a second one. The veil is the ground's own colour, so a light
theme fades the rest back instead of turning it grey; a dark theme darkens it.

| Prop | Default | Notes |
|---|---|---|
| `at`, `to` | `[0.5, 0.45]` | a round spot's centre (frame fractions) and where it travels |
| `radius` | `300` | px at 1080 |
| `rect`, `toRect` | | a rounded box instead (px in the frame): `{x, y, w, h}` |
| `corner` | theme radius | the box's corner radius |
| `moveAt`, `moveFrames` | `30`, by distance | ease in-out |
| `feather` | 0.6 (round) / 40 px (box) | soft edge |
| `dim` | `0.62` | veil strength |
| `color` | `t.colors.bg` | the veil |
| `glow` | dark 0.18, light 0 | light inside a round spot |
| `delay`, `fade`, `exit` | 0, theme entrance, true | fades out by the end of the Sequence |

```tsx
<Spotlight rect={{x: 80, y: 420, w: 520, h: 240}} toRect={{x: 700, y: 420, w: 520, h: 240}} moveAt={36} />
```

Gotchas: place it after the content. Box mode is a huge spread box-shadow around an empty box; its rect is in stage
px, so compute it from the same layout numbers you used to place the element.

### LightSweep

One specular pass of light across a card, a logo plate or the frame. The band is a straight gradient leaned with
`skewX`, so its edges stay clean. Props: `at` (8), `duration` (28 at 30 fps), `angle` (-18), `width` (0.3 of the
box), `intensity` (0.6), `color` (white), `blend` (soft-light light / screen dark), `radius` (theme), `children`.

```tsx
<LightSweep at={20}>
  <Card>Annual plan $96</Card>
</LightSweep>
```

Gotchas: a named beat, not decoration: two or three in a 45 s film. Only the band is clipped to the box, so the
wrapped card keeps its shadow. On pure white a sweep is invisible (as in life); use it on mid and dark surfaces.

### Pattern

A repeating pattern between the ground and the content.

| `kind` | Drawn with | Default size / weight |
|---|---|---|
| `grid` | CSS gradients | 80 / 1.5 |
| `dots` | CSS radial gradient | 32 / 5 (diameter) |
| `cross` | canvas | 96 / 2 |
| `stripes` | repeating linear gradient with 1 px ramps | 28 / 10 |
| `rules` | CSS gradient | 56 / 1.5 |
| `checker` | repeating conic gradient | 64 |
| `halftone` | canvas, dot size follows `fade` | 26 / 0.9 (largest dot, share of the cell) |

Props: `size`, `weight`, `color` (text at a low alpha, stronger on dark themes), `opacity`, `angle` (stripes 45,
halftone 20), `fade` (`none`, `center`, `edges`, `top`, `bottom`, `left`, `right`), `drift` (`[x, y]` px a second).

```tsx
<Ground>
  <Pattern kind="grid" fade="center" />
  <Content />
</Ground>
```

Gotchas: cells are centred on the frame. Keep patterns quiet behind text (the defaults are 5 to 16% alpha); a
halftone reads best in a corner or along an edge, not under the headline.

---

## Surfaces

### elevation(), surfaceAt(), hairline(), tonal(), SPACE, space()

`elevation(level, theme, unit)` is a two-layer box-shadow (a tight key and a soft ambient), lit from above, levels
0 to 5, tinted with the ground's hue on light themes and black and stronger on dark ones. `surfaceAt(level, t)`
lightens the surface a step per level on dark themes (shadows barely show there). `hairline(t)` is a 1 px border
colour. `tonal(t, color?)` tints the ground towards a colour. `SPACE` is 8, 16, 24, 40, 64, 96, 144.

```tsx
<div style={{boxShadow: elevation(3, t, unit), background: surfaceAt(3, t)}} />
```

### Card

| Prop | Default | Notes |
|---|---|---|
| `variant` | `'solid'` | `solid`, `outline`, `glass`, `paper`, `tonal` |
| `elevation` | solid 2, paper 2, glass 3, others 0 | |
| `radius` | theme | px at 1080 |
| `padding` | `44` | or `[vertical, horizontal]` |
| `width`, `height` | auto | numbers are px at 1080 |
| `color` | | the surface (tonal: the tint) |
| `blur` | `28` | glass backdrop blur |
| `tilt` | `0` | degrees, pinned paper cut-outs |

```tsx
<Card variant="paper" tilt={-2}>
  <h3>Notes</h3>
</Card>
```

Gotchas: glass is a backdrop blur every frame (slow: a community render ran 4x slower with stacked big blurs)
and it only reads over a busy, moving ground; on a flat ground it is a pale card. Cards on cards and three identical
icon cards in a row are on the anti-slop list. Paper cards carry a grain texture under their content (they are
isolated, so absolutely positioned children still sit relative to the card).

### Pill and Badge

Rounded labels. `Pill`: `variant` (`soft` default, `solid`, `outline`, `glass`), `color` (accent), `size` (30, the
smallest that reads on a phone), `caps`, `dot` (true or a colour), `icon`. `Badge`: the same props, solid by default,
bolder, squarer, tabular figures, size 28.

```tsx
<Pill dot color={t.colors.positive}>Shipped</Pill>
<Badge variant="soft">+24%</Badge>
```

Gotchas: soft and outline text is pushed to 4.5:1 contrast with `ensureContrast()`. On a photo or a hard-seam part,
the backdrop is not the theme's ground: `FullBleed` and `Split` wrap their content in `OnTone`, and chips read it
(`useOnDark()`); wrap your own content in `<OnTone dark>` when you put chips on a dark picture.

### Scrim

A legibility gradient over a picture, behind text, with eased stops (no visible start line). Props: `side`
(`bottom`, `top`, `left`, `right`, `center`, `full`), `size` (0.62), `strength` (0.72), `color` (black; the theme's
bg for a light scrim).

```tsx
<AbsoluteFill>
  <Img src={staticFile('photo.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
  <Scrim side="left" size={0.7} />
</AbsoluteFill>
```

### Frame

A finished frame around a picture: `variant` `mat` (white mat and shadow), `polaroid` (a thick bottom with a
handwritten `caption` in the theme's hand font), `line` (a hairline, rounded), `bare`. Props: `width`, `height`
(the picture, 720 x 480), `mat`, `color`, `radius`, `elevation` (3), `tilt`, `caption`.

```tsx
<Frame variant="polaroid" width={360} height={360} tilt={4} caption="Rangamati, May">
  <Img src={staticFile('trip.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
</Frame>
```

### Border

A decorative border for the whole frame, drawn on: `kind` `rule`, `double` (luxury and editorial), `corners`
(viewfinder marks), `brackets` (thicker, round caps, accent). Props: `inset` (`'safe'`: 60% of the smaller safe
margin, or px), `color`, `weight` (2, brackets 5), `length` (64), `delay`, `duration` (24 at 30 fps; 0 = drawn).

```tsx
<Border kind="double" />
<Border kind="corners" inset={80} color={t.colors.accent} delay={10} />
```

### Panel

An app window without a device: a surface, a slim top strip (`bar`: `dots`, `title`, `none`) and a clipped content
area. Props: `width` (1100), `height` (680), `title`, `tone` (`auto`, `light`, `dark`), `elevation` (4), `radius`
(theme, at most 22), `padding` (0: screenshots fill it). Text inside is left-aligned whatever wraps it.

```tsx
<Panel title="Roadmap" width={1180} height={640}>
  <Img src={staticFile('app.png')} style={{width: '100%'}} />
</Panel>
```

---

## Layout (16:9, 1:1, 4:5, 9:16)

### useLayout(), pick(), shapeOf(), Responsive

`useLayout()` returns `{shape, wide, tall, pick, safe, width, height, unit}`. Shapes: `wide` (aspect 1.3 and up),
`square` (0.9 to 1.3), `portrait` (0.68 to 0.9, 4:5), `tall` (below, 9:16). A `Responsive<T>` prop takes one value or
one per shape; a missing shape uses the nearest given one by aspect.

```tsx
const {pick, tall} = useLayout();
const size = pick({wide: 120, square: 104, tall: 96});
```

### Grid and Cell

Columns and gutters. Props: `columns` (`{wide: 3, square: 2, portrait: 2, tall: 1}`), `rows` (shares the height,
with `fill`), `gap` (`{wide: 32, tall: 24}`), `rowGap`, `align` (stretch), `fill` (position on the area), `area`
(`safe`). `Cell`: `span`, `rowSpan` (responsive).

```tsx
<Grid columns={{wide: 3, square: 3, portrait: 1, tall: 1}} gap={{wide: 36, tall: 24}}>
  <PlanCard />
  <PlanCard />
  <PlanCard />
</Grid>
```

Gotchas: the kit does not shrink content to fit: check the stacked height on tall frames (three stacked cards
overflowed a 1:1 safe area in testing, three columns fit). In a `SafeArea` (a column with `align="start"`), Grid
takes the full width by itself.

### Stack

A row or column with one gap: `dir` (responsive, default column), `gap` (24), `align`, `justify` (`between`,
`around` too), `wrap`, `fill`, `area`.

```tsx
<Stack dir={{wide: 'row', tall: 'column'}} gap={24} align="center">
  <Pill>Design</Pill>
  <Pill>Motion</Pill>
</Stack>
```

### Center

Content centred in the safe area with a readable measure and optical centring (lifted 3% of the height), headlines
balanced over their lines (`text-wrap: balance`). Props: `area`, `maxWidth` (`{wide: 0.72, square: 0.86, portrait:
0.9, tall: 0.96}` of the area width), `optical` (true), `align` (center), `gap` (28).

```tsx
<Center>
  <h1>Make the first frame worth a pause.</h1>
</Center>
```

### Split

Two parts side by side on wide and square frames, stacked on portrait and tall ones. `area="full"` with
`seam="hard"` makes two grounds meet at the seam (the seam divides the safe area, so both parts get the same room).
Props: `ratio` (0.5), `dir`, `gap` (72), `area` (`safe`), `seam` (`none`, `line`, `hard`), `grounds` (bg and
accent), `align`, `justify` (per part), `children` (exactly two).

```tsx
<Split area="full" seam="hard">
  <Before />
  <After />
</Split>
```

Gotchas: on the accent part the text colour is the theme's `onAccent` only if it reaches 4.5:1 there, else the
more readable of onAccent and the text colour (the fresh theme's white on green is 2.9:1, so it gets dark text).

### StatSplit

One big number and its meaning. The number is measured in its loaded font and sized to its box (the render waits),
so "87%" never runs out of the frame in any shape. Props: `value`, `sample` (the widest text a counter will show),
`label`, `note`, `color` (accent), `ratio` (`{wide: 0.58, square: 0.56, portrait: 0.5, tall: 0.46}`), `size` (fixed
size, skips measuring), `align` (bottom).

```tsx
<StatSplit value="87%" label="of viewers start with the sound off" note="Source: our 2026 survey" />
```

Gotchas: "hero metric" layouts are on the anti-slop list when used as filler; one per film, for the number that
carries the story. Pass `sample` when `value` is an animated counter, or the size is only estimated.

### FullBleed

A picture edge to edge with text on a scrim, laid out per shape (bottom-left on wide, bottom-centred on tall), with
a slow push-in. Props: `src` or `background`, `focus` (the point kept in frame when the crop changes), `push`
(0.04), `place` (responsive), `scrim` (`auto` from the text's side, a side, or false), `strength` (0.72),
`maxWidth` (`{wide: 0.56, square: 0.84, portrait: 0.92, tall: 1}`), `tone` (`light`: white text on a dark scrim),
`area` (`safe`: a whole frame, text in the safe area; `box`: a picture inside a card or grid cell, text kept inside
that box with `pad`, 44).

```tsx
<FullBleed src={staticFile('hills.jpg')} focus={[0.66, 0.5]}>
  <h1>Into the hills</h1>
  <p>A weekend on foot, 42 km</p>
</FullBleed>
```

Gotchas: "headline over a full-bleed motion asset" is on the anti-slop list: use a still or slow picture under text,
and set `focus` so the subject survives the 9:16 crop. Inside a card, pass `area="box"`: the default places text by
the frame's safe area, which is outside a small box (seen in testing: the caption vanished from a bento card).

---

## Shapes

### blobPath(), Blob, BlobMask

`blobPath({width, height?, points = 7, wobble = 0.16, seed, time})` returns a closed smooth path (points on a
circle pushed by 3D noise, joined with Catmull-Rom curves), always inside its box. `Blob` draws it (`size` 520,
`height`, `color` (accent softened), `gradient`, `outline`, `points`, `wobble`, `seed`, `speed` 0.25, `delay`, `grow`
(theme entrance), `opacity`, `children` centred). `BlobMask` clips a picture to a slowly moving blob (`width` 560,
`height` 640, `wobble` 0.12, `speed` 0.2).

```tsx
<div style={{position: 'relative', width: 720, height: 780}}>
  <Blob size={600} style={{position: 'absolute', left: 150, top: 150}} />
  <BlobMask width={520} height={600} style={{position: 'absolute', left: 80, top: 70}}>
    <Img src={staticFile('photo.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
  </BlobMask>
</div>
```

Gotchas: offset the blob from the subject rather than centring it behind (a concentric blob reads as a halo). The
name `Blob` shadows the DOM `Blob` in a file that imports it: `import {Blob as Shape}` if that file also uses the
DOM one.

### Ring, Sparkle, Squiggle

`Ring`: a circle that draws on around something (`size` 360, `weight` 6, `color`, `progress` or `delay` +
`duration` 30, `start` -90, `dashed` for round dots revealed through a drawing mask, `children` centred).
`Sparkle`: a four-point star (`makeSpark` from @remotion/shapes) that pops in with overshoot (`size` 64, `color`,
`delay`, `rotate`, `twinkle`). `Squiggle`: a hand-drawn wave that draws itself under a word (`width` 420,
`amplitude` 12, `waves` 5, `weight` 7, `color`, `delay`, `duration` 18, `seed`).

```tsx
<Ring size={210} delay={20}><Big>42</Big></Ring>
<Squiggle width={430} delay={16} />
<Sparkle size={64} delay={24} />
```

Gotchas: decoration is rationed: one or two pieces per frame, each with a job (framing a number, marking a payoff).

---

## Colour

| Function | What it does |
|---|---|
| `parseColor(c)` | any CSS colour (hex, rgb, hsl, oklch, oklab, names) to sRGB 0..1 |
| `toHex(c)`, `withAlpha(c, a)` | hex (with alpha when needed), rgba() |
| `mix(a, b, t)` | mix in OKLab (clean midpoints) |
| `lighten(c, d)`, `darken(c, d)`, `saturate(c, k)` | OKLab lightness steps (0.05 is visible), chroma scale |
| `oklch(l, c, h, alpha?)`, `toOklch(c)` | build and read OKLCH (out-of-gamut chroma is reduced) |
| `luminance(c)`, `contrast(fg, bg)` | WCAG relative luminance and ratio (1 to 21) |
| `isReadable(fg, bg, 'AA' or 'AAA', large?)` | 4.5 / 3 (large) or 7 / 4.5 |
| `readableOn(bg, light?, dark?)` | the better text colour |
| `ensureContrast(fg, bg, min = 4.5)` | the colour moved in lightness, hue kept, until it reads |
| `isDark(c)`, `shadowTint(ground)` | a ground that wants light text; a shadow colour in the ground's hue |

```tsx
const label = ensureContrast(t.colors.accent2, t.colors.bg, 4.5);
const ink = readableOn(photoAverage, '#FFFFFF', t.colors.text);
```

### brandTheme()

A full `ThemeSpec` from one or two brand colours: grounds and greys tinted by the brand hue (a whisper: chroma at
most 0.008 light, 0.016 dark), the brand colour kept exact as the accent, `onAccent` chosen for contrast, a second
accent about 160 degrees round the wheel unless given, fonts and motion from a base theme.

```tsx
<ThemeProvider theme={brandTheme({primary: '#E4002B', base: 'corporate', fonts: {display: 'Manrope'}})}>
  <Video />
</ThemeProvider>
```

Options: `primary`, `secondary`, `dark`, `base` (studio or midnight), `neutral` (`tinted` or `pure`), `fonts`,
`radius`, `name`, `grain`, `vignette`. Gotchas: a very light brand colour (yellow) stays the fill; text in that
colour on a light ground is pushed darker by the components that use `ensureContrast()`.

### useTextEm(), estimateEm()

`useTextEm(text, {fontFamily, fontWeight, letterSpacing?, textTransform?})` measures a string's width in em in the
page once its font face has loaded (the kit's Google fonts are added to `document.fonts` only when loaded), holding
the render meanwhile; cached per tab. `estimateEm(text, digitEm)` is the quick guess before that.

---

## Module-wide gotchas

- Everything is a pure function of the frame. Grain, patterns and halftone draw on canvases in layout effects
  (before paint); the grain tile and paper texture are decoded behind `delayRender` once per tab.
- WebGL parts (`EffectGround`, `Paper` with the shader) need `--gl=angle`; they fall back to CSS without WebGL2.
- The finish (grain) goes over everything; put scene-wide overlays (spotlight, sweep) before `Finish` or inside a
  ground's children.
- Demos place several themes and frame shapes in one frame with a `<Sequence width height>`: inside it
  `useVideoConfig()` (and so `useStage()`) reports that size, so each tile lays out as a real frame.

Assets in `public/design/` were made here, in code: `landscape.jpg` (mountains at dawn) and `dusk.jpg` (mountains under
a moon), layered noise ridges rendered as Remotion stills. Nothing was downloaded.
