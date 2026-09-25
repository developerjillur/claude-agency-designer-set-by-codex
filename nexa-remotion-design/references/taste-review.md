# Taste, choices and review

The decisions that make a frame look designed rather than generated, the anti-slop list to check against, and how
to review design on contact sheets. Use the list as a check after designing, never as the design itself:
prohibitions alone make every video the same.

## 1. Choosing the design of a film

Write three short directions for client work and keep one. Each direction sets these dials:

| Dial | Low | High |
|---|---|---|
| Ground | flat, deliberate (Swiss) | lit, textured, moving (mesh, paper, floor) |
| Density | one element per frame | many small things (UI, data) |
| Depth | flat colour planes | cards, shadows, parallax |
| Texture | none (clean product) | grain, paper, halftone (printed, filmed) |
| Colour | one accent on neutrals | many hues (playful, retro) |
| Type | quiet sans at moderate sizes | huge display type, one word per frame |

Then pick grounds and surfaces from the direction, not from habit:

| Brief or style | Ground | Surfaces | Texture |
|---|---|---|---|
| SaaS launch, app promo (dark) | `Mesh` or `Ground spot` | solid cards, one glass moment, panels | grain 0.03 |
| Clean explainer (light) | `Ground lit` or `band` | solid and tonal cards, pills | none, dither only |
| Keynote minimal | `Ground spot`, lots of black | almost none; type and one picture | none |
| Vox collage explainer | `Paper grid={106}` | paper cards tilted, frames, halftone people | grain 0.16 at 3 to 6 Hz |
| Editorial, magazine | `Ground` on white, rules | line frames, double borders, full-bleed pictures | grain 0.02 |
| Data journalism | white `Ground`, `contours` for maps | outline cards, direct labels | none |
| Kinetic promo | `Ground solid` black | none | grain 0.05 |
| Luxury, fashion | `Ground lit` warm black | double rule borders, mats | grain 0.06, vignette 0.5 |
| Trailer | `Ground` near black | none | grain 0.1, vignette 0.55, light leaks on cuts |
| Retro, sale, sports | `EffectGround starburst` or halftone | badges, bold pills | grain 0.12 |
| Neon, gaming, night | `EffectGround floor`, `Mesh` | glass pills, glow lines | grain 0.04 |
| Architecture, engineering | `EffectGround blueprint` | outline cards, cross patterns | none |
| Kids, playful explainer | `Ground` sky blue, `waves` | blobs, sparkles, rounded cards | none |
| Wellness, calm | `EffectGround liquid` (low contrast) or `Gradient` | tonal cards | dither |
| Bangla-first (dhaka) | `Ground band` green | cards with Bangla type | grain 0.04 |
| Brand work | `brandTheme()` then the style's ground | as the style | as the style |

## 2. Composition and taste rules

- No vacuum: every frame on a lit ground (radial light with a source, texture, horizon or parallax). Light
  interacts with form; sourceless glow is a defect; text parked in a glow core loses contrast.
- At least one full-bleed moment per act; a content box under 60% of the frame with dead margins on all sides reads
  as a slide. Premium frames keep about 40% negative space; headlines about 80%.
- One focal point: the hero wins on at least two of size, contrast, position and weight. Hierarchy: motion, size,
  contrast, saturation, position. Proximity: inside gaps clearly smaller than outside gaps.
- Adjacent beats use different composition systems (see layout-safe-zones.md); one palette, one type voice, one
  light language across the film.
- Frame 0 is the poster: open composed and legible (a ground and at least the main element), motion comes from
  inside it. No fade from black at the start.
- Colour: one accent with a budget, tinted neutrals, perceptual interpolation, an AA-safe darker accent for small
  text on light grounds.
- Texture is a per-direction dial, not a house style: "grain, grade and vignette on every scene" and "glow on the
  hero" are one school's habits.

## 3. The anti-slop list (check after designing)

Purple and blue gradients by default; three-column icon grids; cards on cards; gradient text; the hero-metric
template as filler; glassmorphism by default; glow on everything; emoji icons (they ignore the palette: draw glyphs
in SVG); eyebrow labels on every section; numbered 01, 02, 03 scaffolding; expanding ring ripples; rhythmic
heartbeat pulses; decorative divider bars; confetti endings; a globe or network as "tech"; random particles; a
headline over a full-bleed motion asset; the same visual formula in two adjacent beats; cream or sand default
backgrounds; invented UI and fake metrics.

## 4. Review on contact sheets

After `nrk.py stills PROJECT` (or `nrk.py demos` for kit work), read every sheet, then full-size stills of the
dense frames (`nrk.py still PROJECT --frame N`), and crops of textures at 1:1 or 2:1. For each held frame:

1. Ground: is there light with a source, or is flat a stated choice? Does the light agree with the shadows?
2. Focus: one focal point? Would a stranger say what the frame is about in two seconds?
3. Safe: all text and logos inside the safe outline on every delivered shape (render the 9:16, 1:1 and 4:5 cuts).
4. Size: captions 56 px or more, auxiliary 32 px or more at 1080; nothing scaled below the floor by a group scale.
5. Contrast: text on its actual backdrop (picture regions, accent fills) at least 4.5:1, big type 3:1; measure with
   `contrast()` when in doubt.
6. Fit: nothing overflowing (1:1 is the tightest height), no orphan word on a headline's last line.
7. Texture: grain visible in a full-size mid-tone crop but not in the sheet; no rings in dark gradients after
   encoding; paper not tinted blue.
8. Budget: one accent per frame, one or two decorative shapes, one glass moment per film, sweeps only on named beats.
9. Variety: the next beat uses a different composition system.
10. First and last frames: frame 0 composed; nothing half visible at a cut.

An agent that designed the frames cannot judge them reliably while its intent is in context: for client work,
give held frames plus the one-line brief to a fresh reviewer (the `remotion-reviewer` agent) and fix every high and
medium finding.

## 5. Failure modes seen while building the kit (and the fixes in it)

| Symptom | Cause | Fix now in the kit |
|---|---|---|
| Big number ran off a 4:5 frame | sized from a digit-width guess; % is 1.6 digits wide | StatSplit measures the text in the loaded font |
| Title cut off, cards past the safe area on 1:1 | three stacked cards do not fit 972 px | per-shape columns; check the stacked height |
| Grain invisible on white and black | overlay blending vanishes at the extremes | signed specks by default |
| 5 s clip grew from 0.9 to 21.7 MB | 0.16 grain re-seeded 12 times a second | rate and amount documented; 3 to 6 Hz for long uploads |
| Paper looked blue-grey and a fifth darker | the shader's default front colour and lighting | near-white tones from the sheet, source lifted |
| Glass pill grey on a dark photo | chip assumed the theme's light ground | OnTone context from FullBleed and Split |
| Spotlight turned a light frame muddy grey | a dark veil on a light theme | the veil is the ground's own colour |
| Card lost its shadow under a light sweep | the wrapper clipped its children | only the band is clipped |
| White caption on a green half failed contrast | theme onAccent 2.7:1 on that fill | onAccent only at 4.5:1, else the darker ink |
| Widow word on a centred headline | default wrapping | `textWrap: 'balance'` in Center and FullBleed |

## 6. Words for directions (to brief or to review)

Lit ground, source, falloff, pool, horizon, floor band, seam, hard seam, full bleed, scrim, mat, tooth, fibre,
grain boil, vignette, halation, tinted neutral, accent budget, tonal fill, elevation, key shadow, ambient shadow,
hairline, optical centre, measure, restack, safe area, title safe, negative space, focal point, composition system.
