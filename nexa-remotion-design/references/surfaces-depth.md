# Surfaces and depth

Cards, labels, scrims, frames, borders and panels: the things content sits on, and the shadows and light that give
them depth. Kit components first, raw CSS after.

## 1. One light, one depth system

- The kit's light comes from above the frame, so shadows fall straight down and grow with elevation. Keep one
  light direction for the whole film (the ground's light, the shadows and any sweep agree).
- Elevation levels 0 to 5 (`elevation(level, theme, unit)`), two layers each: a tight key shadow and a soft ambient
  one with a small negative spread. Values at 1080 (y offset, blur, alpha on light themes):

| Level | Key | Ambient | Use |
|---|---|---|---|
| 0 | none | none | flat, outline or tonal cards |
| 1 | 0 1 2, 0.13 | 0 3 8, 0.08 | chips, list rows |
| 2 | 0 2 5, 0.12 | 0 8 20, 0.11 | cards (default) |
| 3 | 0 3 8, 0.11 | 0 14 34, 0.14 | a highlighted card, pictures in frames |
| 4 | 0 5 12, 0.10 | 0 24 52, 0.18 | panels, modals |
| 5 | 0 8 18, 0.10 | 0 38 84, 0.24 | the one floating hero |

- On light grounds the shadow colour is the ground's own hue, very dark (`shadowTint(bg)`: warm paper gets warm
  shadows, never flat grey). On dark grounds shadows are black at 3.2 times the alpha (capped at 0.6 and 0.7) and
  still barely show, so higher surfaces are also lighter: `surfaceAt(level, t)` lifts the surface 0.012 OKLab
  lightness per level. Dark cards also get a 1 px top inner highlight (white at 5%).
- Subtle shadows vanish in compressed video: the kit's values were raised after the first renders because levels
  1 and 2 did not read at 1080p. Check the elevation demo at full size before trusting a shadow to separate things.
- Hairlines: text at 8% on light surfaces, white at 9% on dark ones (`hairline(t)`); Remotion's Elements use dark
  UI cards #15161a with a 1 px white 9% border, 26 px radius and a 0 18 40 black 26% shadow.

## 2. Cards

| Variant | Look | When |
|---|---|---|
| solid | surface, hairline, elevation 2 | most content |
| outline | 1.5 px border (text 18%), no fill | secondary items, alternatives |
| tonal | the ground tinted 10% (16% dark) towards a colour, no shadow | flat grouping, flat design looks |
| paper | warm off-white, printed tooth, a tight cut-paper shadow, optional tilt | collage, Vox, notes, scrapbook |
| glass | translucent tint, backdrop blur 28 px, saturate 1.35, bright top edge | only over a busy moving ground |

Glass: `backdrop-filter` is slow in renders (a community render ran four times slower with stacked large blurs for
an effect nobody could see) and it only reads over something busy: a `Mesh`, a moving picture. On a flat ground it
is a pale card. It is on the anti-slop list as a default; use it once, deliberately. Raw CSS:

```tsx
style={{
  background: 'linear-gradient(160deg, rgba(255,255,255,0.34) 0%, rgba(255,255,255,0) 48%), rgba(255,255,255,0.46)',
  backdropFilter: 'blur(28px) saturate(1.35)',
  border: '1px solid rgba(255,255,255,0.55)',
  boxShadow: `${shadow}, inset 0 1px 0 rgba(255,255,255,0.6)`,
}}
```

Cards on cards and a row of three identical icon cards are anti-slop. Give a card real content (a number, a name, a
state) and vary the treatment by role: one hero card (solid, elevation 3) among outline peers reads as a choice.

Text inside cards: the card sets `color` and `fontFamily` from the theme; padding 40 to 56 px at 1080 on 16:9, 30 to
40 on narrow frames; radius from the theme (0 for Swiss and brutalist, 24 to 28 for friendly looks).

## 3. Pills and badges

- Pill (a tag or state): 30 px text (the smallest that reads on a phone), 0.42em by 0.95em padding, fully round.
  Soft by default: the ground tinted 14% (24% dark) towards the colour, the text colour pushed to 4.5:1 with
  `ensureContrast()`. Solid: the colour filled, `onAccent` or the readable text colour on it. Outline: a 2 px border
  at 70%. Glass: white 55% (16% on dark) with a blur. A status dot (0.5em) in front for live states.
- Badge (a number or a flag: NEW, +24%, 4.9): 28 px, bolder (700+), tabular figures, small radius (at most 12).
- On a photo or another ground than the theme's, the chip does not know what is behind it: `FullBleed` and the
  hard-seam `Split` wrap their content in `OnTone`, and chips read it with `useOnDark()`; wrap your own content in
  `<OnTone dark>` over a dark picture. Measured before the fix: a glass pill on a dark scrim in a light theme came
  out grey with dark text.
- One or two chips per frame; eyebrow labels on every section are on the anti-slop list.

## 4. Scrims

A legibility gradient between a picture and its text. A two-stop linear gradient shows a line where it starts; the
kit uses ten stops on an eased curve `alpha(p) = strength x (1 - p)^2 x (1 + 2p)` over the first `size` (62%) of the
frame from the text's side, strongest 0.72 black. `center` puts a soft ellipse behind centred text; `full` is a
flat darkening (55 to 75%). For dark text on a picture use a light scrim (`color={t.colors.bg}`). Check contrast on
the brightest part of the picture under the text, not on the average.

Lambda trap: a full-width semi-transparent gradient overlay (a scrim, a vignette) showed stale horizontal strips on
Lambda with SwANGLE in one report; `willChange: 'opacity'` on the overlay fixed it there. Never put `will-change` on
text.

## 5. Frames for pictures

- Mat: white mat 18 px at 1080, radius up to 14, elevation 3: a print on a wall or a table.
- Polaroid: 22 px sides, 92 px bottom with a handwritten caption in the theme's hand font, radius 3, a small tilt
  (plus or minus 2 to 6 degrees; alternate the sign between neighbours).
- Line: a 1.5 px hairline around a rounded picture: interface screenshots, editorial.
- Pictures inside are `<Img>` (it waits for loading) at 100% with `objectFit: 'cover'` and an `objectPosition` that
  keeps the subject in the box.

## 6. Borders for the whole frame

An inset rule, a double rule (outer 2 px, inner 1 px, 10 px apart) for luxury and editorial title cards, corner
marks (viewfinder) for tech and documentary, brackets (5 px, round caps, accent) for callouts. Draw them on with
`pathLength={1}`, `strokeDasharray={1}` and `strokeDashoffset={1 - progress}` over about 24 frames with an ease
in-out; inset between the frame edge and the safe area (the kit uses 60% of the smaller safe margin).

## 7. Panels (an app without a device)

A surface with a 58 px strip (window dots, a centred title, or nothing), elevation 4, radius up to 22, content
clipped, text left-aligned whatever wraps it. Device frames (phones, laptops) and cursors are the ui sub-skill's.
Rebuild real UI from the product (real copy, real numbers) rather than inventing it; invented UI is one of the
loudest generated-video tells.

## 8. Decorative shapes, used with taste

- One organic blob behind a subject, offset from it (a concentric blob reads as a halo); a picture clipped to a
  calm blob (`BlobMask`, wobble 0.12); a ring drawn around a number; a sparkle on a payoff moment; a squiggle under
  one word. One or two per frame, each with a job.
- `@remotion/shapes` gives `Rect`, `Circle`, `Ellipse`, `Triangle`, `Star`, `Polygon`, `Pie`, `Arrow`, `Callout`,
  `Heart`, `Spark` and `make*()` path functions (`{path, width, height, transformOrigin, instructions}`). Set `fill`
  explicitly (the default is black; the Studio schema's blue only seeds the editor); `style` goes to the `<svg>`,
  `pathStyle` to the `<path>` (rotations about the centre); `cornerRadius` and `edgeRoundness` cannot be combined;
  `Circle` and `Box` clash with `@remotion/rough-notation` names (alias the import). Shapes accept `effects` on
  4.0.474+, rendered through `<HtmlInCanvas>` (the Studio preview needs a Chrome flag; do not nest HtmlInCanvas).
- Anti-slop: expanding ring ripples, heartbeat pulses, confetti endings, random particles, globe or network art as
  "tech", decorative divider bars.

## 9. Checks

- Separation: can you tell each card from the ground at full size, in the encoded file?
- One light direction; shadows agree with the ground's light.
- Chip text contrast at least 4.5:1 against its own fill; 3:1 for text above about 40 px.
- Glass only over a moving, busy ground, and at most once per film.
