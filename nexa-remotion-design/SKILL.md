---
name: nexa-remotion-design
description: "Visual design for Remotion videos: lit grounds (a light with a source, floor bands, spotlights), gradients and moving mesh backgrounds, film grain, vignette, paper and notebook textures, patterns and halftone, WebGL effect backgrounds (blueprint, liquid, waves, sunburst, contours, a synthwave floor), cards (solid, outline, glass, paper), pills, badges, shadows and elevation, scrims over pictures, frames, borders, app panels, layouts that adapt to 16:9, 9:16, 4:5 and 1:1 inside platform safe zones, colour contrast and OKLab mixing, and brand kits from one colour. Use it whenever a scene should look designed instead of flat, Banglish included ('background sundor koro', 'design ta professional koro', 'brand color diye video banao'). Part of the nexa-remotion family."
---

# Design for Remotion video

What a scene stands on and how it is arranged: grounds and light, texture, surfaces and depth, layout across frame
shapes and safe zones, colour and brand kits. Part of the nexa-remotion family (the director skill is
`nexa-remotion`; the kit lives in `~/.claude/skills/nexa-remotion/kit`, and a project made with `nrk.py new` imports
these parts from `./kit/design`). Motion, type, charts, UI devices and effects on footage are the sibling skills'.

## Fast path

1. **Direction.** Write one scene sentence ("a printed page on a desk", "a product under a lamp at night") and
   decide dark or light from it. Pick the theme from `nexa-remotion-styles`, or build the client's with
   `brandTheme({primary})`. Set the texture dial: grain and vignette come from the theme.
2. **Ground every beat.** Wrap each scene in a ground: `<Ground>` (lit, spot, band), `<Mesh>`, `<Gradient>`,
   `<Paper>`, `<EffectGround>` or a `<FullBleed>` picture. Never a flat colour behind small floating content, unless
   flat is the style (Swiss, brutalist). Adjacent beats use different composition systems.
3. **Lay out inside the safe area** with `Grid`, `Stack`, `Split`, `StatSplit`, `FullBleed`, `Center`; give per-shape
   values (`{wide: 3, tall: 1}`) and restack for 9:16 instead of cropping.
4. **Surfaces.** `Card`, `Pill`, `Badge`, `Panel`, `Frame`, `Border`; elevation 2 for cards, 4 for panels, one
   floating hero at 5; glass once per film and only over a moving ground.
5. **Colour.** One accent per frame; check text with `contrast()` and fix small accent text with
   `ensureContrast()`; tinted neutrals.
6. **Light and finish.** A `Spotlight` or `LightSweep` only on named beats; the grounds add the theme's vignette and
   grain (lower the grain `rate` on long uploads).
7. **Check.** `nrk.py stills PROJECT`, then full-size stills of dense frames and 1:1 crops of textures; render every
   delivered shape (9:16, 1:1, 4:5). Review with `references/taste-review.md`.

## Components (from `./kit/design`)

| Component | Use it for | Key props |
|---|---|---|
| `Ground` | the lit ground of any scene, with the finish on top | `kind` lit, spot, band, solid; `light`, `split`, `direction`, `drift`, `grain`, `vignette` |
| `Gradient` | a tinted wash, OKLab, dithered, drifting | `kind` linear, radial, conic; `colors`, `angle`, `center`, `drift`, `space` |
| `Mesh` | a soft moving colour field (launches, glass backdrops) | `colors`, `speed`, `wander`, `size`, `grain` |
| `EffectGround` | WebGL pattern grounds | `kind` blueprint, liquid, waves, starburst, contours, floor; `contrast`, `speed`, `loop` |
| `Paper` | paper sheets, Vox grid, notebook | `grid`, `rules`, `margin`, `fibers`, `boil`, `engine` webgl or css |
| `Grain`, `Vignette`, `Finish` | film texture over everything | `amount`, `rate` (12), `blend`; `amount`; the theme's pair |
| `Pattern` | grid, dots, crosses, stripes, rules, checker, halftone | `kind`, `size`, `weight`, `fade`, `drift` |
| `Spotlight`, `LightSweep` | point the eye; a specular pass on a beat | `at`/`to` or `rect`/`toRect`, `dim`; `at`, `duration`, `children` |
| `Card` | a surface for a group | `variant` solid, outline, glass, paper, tonal; `elevation`, `padding`, `tilt` |
| `Pill`, `Badge` | tags, states, numbers | `variant`, `color`, `size`, `dot`, `caps` |
| `Scrim`, `FullBleed` | legible text on pictures | `side`, `strength`; `src`, `focus`, `place`, `push` |
| `Frame`, `Border`, `Panel` | picture mounts, frame rules and corners, an app window without a device | `variant`, `caption`; `kind`, `inset`; `bar`, `title` |
| `Grid`, `Cell`, `Stack`, `Center`, `Split`, `StatSplit` | layout that adapts to wide, square, portrait and tall | responsive `columns`, `dir`, `ratio`, `gap`; `seam` hard; `value`, `label` |
| `Blob`, `BlobMask`, `Ring`, `Sparkle`, `Squiggle` | decoration with a job | `size`, `seed`, `speed`; `progress`, `delay` |
| `useLayout`, `pick` | the frame's shape and per-shape values | `shape`, `tall`, `pick({wide, tall})` |
| colour helpers | `mix`, `lighten`, `darken`, `oklch`, `contrast`, `readableOn`, `ensureContrast`, `brandTheme` | see `references/colour-brand.md` |
| tokens | `elevation(level, t, unit)`, `surfaceAt`, `hairline`, `tonal`, `SPACE` | see `references/surfaces-depth.md` |

## Craft rules

- **No vacuum.** Every frame stands on light with a source and a falloff, a band, a texture or depth. Sourceless
  glow is a defect; small text never sits in the bright core of a dark spot.
- **Light.** One direction per film (the kit's: from above, shadows fall down). The kit's lit ground lifts 65%
  towards white at the source and shades 0.055 OKLab lightness at the far corner on light themes; on dark themes a
  10% lift, blacks kept lifted.
- **Banding.** Every large gradient gets 2 to 4% still noise (the kit's default dither 0.035); measured on H.264 it
  breaks up the rings for about 130 KB a second.
- **Grain.** About 40 x `amount` levels of luma spread: 0.16 printed paper, 0.05 a whisper. 12 plates a second reads
  as film, every frame as sizzle. It is the most expensive thing to encode: 5 s at 1080p CRF 18 went from 0.9 MB
  (none) to 1.6 MB (still), 8.4 MB (3 Hz), 21.7 MB (12 Hz) and 53.6 MB (every frame) at 0.16. Long uploads: 3 to 6 Hz.
- **Vignette** weak: corners about 0.15 darker, in the ground's hue on light themes.
- **Frame shape.** Text and logos inside `safe` on every delivered shape; the tightest height is 1:1 (972 px of
  safe height). 9:16 keeps text in the band from 270 to 1248 px; pictures and grounds fill the rest.
- **Proportions.** A content box under 60% of the frame reads as a slide: one full-bleed moment per act. Premium
  frames about 40% negative space. One focal point winning on two of size, contrast, position, weight.
- **Type sizes at 1080.** Captions 56 px, auxiliary 32 px, pills 30, badges 28; headlines 96 to 140 on 16:9 and 90
  to 110 on 9:16; balance headline lines (`textWrap: 'balance'`).
- **Surfaces.** Elevation 2 cards, 4 panels, one level-5 hero. On dark themes lift the surface a step per level.
  Glass only over a moving ground, once per film (a backdrop blur costs every frame). No cards on cards.
- **Colour.** One accent with a budget; tinted neutrals (chroma about 0.01); mix in OKLab. Small text at 4.5:1
  minimum (aim for 7:1 on phones), large type 3:1. Accents under 4.5 on their ground (vox, playful, fresh, brutalist,
  data, dhaka) are fills and big type, not small text.
- **Decoration.** One or two shapes per frame, each with a job; a blob offset from its subject, not a halo behind
  it. Sweeps on named beats only (about three in 45 s).
- **Anti-slop check** after designing: default purple-blue gradients, three icon cards, cards on cards, gradient
  text, glass by default, glow on everything, emoji icons, eyebrows everywhere, 01 02 03 scaffolding, ring ripples,
  heartbeat pulses, divider bars, confetti, globe as tech, random particles, a headline over a moving full-bleed
  asset, the same formula twice in a row.

## Recipes

Imports for all of them: `import {SafeArea, ThemeProvider, useStage, useTheme} from './kit/core'`, `import {Animate}
from './kit/motion'`, `import {...} from './kit/design'`, and `Img`, `staticFile` from `remotion`.

A lit title scene (the ground adds the theme's finish):
```tsx
export const Title: React.FC = () => {
  const t = useTheme();
  const {unit} = useStage();
  return (
    <Ground>
      <Center>
        <Animate in="mask">
          <div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 120 * unit, color: t.colors.text}}>
            Make the first frame worth a pause.
          </div>
        </Animate>
      </Center>
    </Ground>
  );
};
```

A Vox collage beat on paper (`Paper` adds a still grain; the extra `Grain` boils it gently at 4 Hz):
```tsx
<ThemeProvider theme="vox">
  <Paper grid={106}>
    <SafeArea row justify="center" align="center" gap={70}>
      <Frame variant="polaroid" width={360} height={360} tilt={4} caption="Rangamati, May">
        <Img src={staticFile('trip.jpg')} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </Frame>
      <Card variant="paper" tilt={-2} width={520}>Rice doubled in ten years</Card>
    </SafeArea>
    <Grain rate={4} />
  </Paper>
</ThemeProvider>
```

A launch moment with its one glass surface:
```tsx
<ThemeProvider theme="midnight">
  <Mesh>
    <Center>
      <Card variant="glass" padding={[40, 56]}>
        <Pill dot>Live now</Pill>
        <div style={{fontSize: 72, fontWeight: 800}}>Version 4.0</div>
      </Card>
    </Center>
  </Mesh>
</ThemeProvider>
```

One stat beat for every frame shape (the number is measured in its font and fitted to the safe area):
```tsx
<Ground kind="spot">
  <StatSplit value="87%" label="of viewers start a video with the sound off" note="Source: the client's 2026 survey" />
</Ground>
```

Before and after on two grounds meeting at a seam (side by side on 16:9, stacked on 9:16):
```tsx
const Block: React.FC<{k: string; v: string; line: string}> = ({k, v, line}) => {
  const t = useTheme();
  const {unit} = useStage();
  return (
    <div>
      <div style={{fontSize: 30 * unit, letterSpacing: '0.08em', textTransform: 'uppercase'}}>{k}</div>
      <div style={{fontFamily: t.type.display, fontWeight: t.weights.display, fontSize: 280 * unit, lineHeight: 0.9}}>{v}</div>
      <div style={{fontSize: 42 * unit}}>{line}</div>
    </div>
  );
};
<Ground>
  <Split area="full" seam="hard">
    <Block k="Before" v="14" line="steps to publish a video" />
    <Block k="After" v="3" line="steps, and the rest is automatic" />
  </Split>
</Ground>
```

A client's brand from one colour:
```tsx
<ThemeProvider theme={brandTheme({primary: '#E4002B', base: 'corporate', fonts: {display: 'Manrope'}})}>
  <Video />
</ThemeProvider>
```

A spotlight moving from the first to the second of three cards laid out with `SafeArea row justify="space-between"`
(box mode; the rects come from the same layout numbers):
```tsx
const {safe, unit} = useStage();
const w = 460 * unit;
const h = 180 * unit;
const y = safe.y + (safe.h - h) / 2;
const box = (x: number) => ({x: x - 26 * unit, y: y - 26 * unit, w: w + 52 * unit, h: h + 52 * unit});
<Spotlight rect={box(safe.x)} toRect={box(safe.x + (safe.w - w) / 2)} moveAt={36} />
```

## Remotion 4.0.528 facts and traps

- `@remotion/effects` (all 74 effects on 4.0.528) run only on canvas hosts: `<Solid>` (4.0.464), `<HtmlInCanvas>`,
  `<Img>`, `<CanvasImage>`, `@remotion/media` `<Video>`, `@remotion/shapes` (4.0.474+). Import from subpaths
  (`@remotion/effects/paper`); the root exports only 11.
- WebGL2 effects need `--gl=angle` (nrk passes it; the kit's config sets it). Without GL they throw "Failed to acquire
  WebGL2 context"; the kit's `EffectGround` and `Paper` detect this and fall back to CSS. `--gl=swangle` works
  without a GPU about 15 times slower.
- Effect params are validated when the factory is called: clamp every animated value (`progress` 0 to 1, `seed` at
  most 1000 for paper, `hueShift` at most 360, `rays` 2 to 100, starburst `origin` 0 to 1).
- `<Solid>` holds a delayRender per chain run and re-runs only when params change; each effect component holds two
  WebGL2 contexts (Chrome keeps about 16): few effect grounds per frame, never animate its size or `pixelDensity`.
- The paper shader's default `colorFront` (#9fadbc) tints a sheet blue-grey and the lighting darkens it by about a
  fifth; the kit passes near-white tones and lifts the source.
- Line-family patterns (`lines`, `waves`, `zigzag`, `checkerboard`) have hard, aliased edges: angles 0 or 90,
  `pixelDensity` 2, or a 1 px blur. `starburst` drops alpha (`transparent` becomes black); fade it with
  `vignette({mode: 'alpha'})`. `liquidContours` phase is in band cycles: whole-number changes loop.
- CSS background images are not awaited by the renderer: decode a generated texture behind `delayRender` before the
  first frame (the kit's `useGrainUrl`), and use `<Img>` for pictures.
- Canvas drawing for grain and patterns happens in `useLayoutEffect` (before paint), from the frame only:
  deterministic in every tab.
- `@remotion/google-fonts` adds a font face to `document.fonts` only after it has loaded, so `document.fonts.ready`
  resolves too early; measure text after the face exists (`useTextEm`).
- `<Sequence width height>` overrides `useVideoConfig()` for its subtree: a way to lay out a 9:16 tile inside a
  16:9 frame (the kit's demos), or to show a vertical cut inside an explainer.
- `interpolateColors()` takes `oklch()`/`oklab()` since 4.0.439 and ignores easing; CSS gradients take `in oklab`.
- `backdrop-filter` and stacked large blurs slow renders a lot; a blur under about 0.8 px does nothing in Chromium.
  A full-width semi-transparent overlay that ghosts on Lambda (SwANGLE) was fixed with `willChange: 'opacity'` on
  the overlay; never put will-change on text.
- H.264 needs an opaque background (transparent frames flatten onto black without antialiasing); render with
  `--color-space=bt709`; CRF 14 to 18 and PNG or JPEG 100 frames when flat gradients or thin type matter.
- `@remotion/shapes`: set `fill` (the default is black), `style` goes to the svg and `pathStyle` to the path, do not
  combine `cornerRadius` and `edgeRoundness`; alias `Circle` and `Box` next to rough-notation. `premountFor` works on
  `<Solid>`, `AbsoluteFill` and `Interactive.*` from 4.0.528.
- The kit's `Blob` component shadows the DOM `Blob` in a file that imports it: alias it if that file needs both.

## References

- `references/kit-api.md`: every design component, helper and default on one page, and the demo list.
- `references/grounds-light-texture.md`: lit grounds, gradients, mesh, grain calibration and file-size tables,
  vignette, paper, patterns, spotlight and sweep, with raw Remotion versions.
- `references/effects-grounds.md`: `@remotion/effects` for backgrounds and textures: Solid, GL, every relevant
  effect's parameters and limits, costs, order, errors, recipes.
- `references/layout-safe-zones.md`: safe areas per platform, frame shapes and responsive props, composition
  systems, type sizes and measure, fitting text, grids, tiles of other shapes, layout transitions.
- `references/surfaces-depth.md`: elevation tokens, cards and glass, pills and badges, scrims, frames, borders,
  panels, decorative shapes and the shapes package.
- `references/colour-brand.md`: colour rules, the helpers, measured contrast of all 20 themes, pictures, brand kits,
  colour and encoding.
- `references/taste-review.md`: choosing a direction and grounds per style, composition rules, the anti-slop list,
  the contact-sheet review and the failure modes found while building the kit.
