# Colour and brand kits

Colour for video that is watched small, compressed and often without sound: a budget for the accent, tinted
neutrals, perceptual mixing, contrast you can measure, and brand kits built from one or two colours.

## 1. Rules

- One accent with a budget: it marks the one thing per frame that matters (a number, a word, a button, a line).
  A second accent only for a second data series or a contrast; no third hue except semantic states (positive,
  negative).
- Tinted neutrals: grounds and greys carry a whisper of the brand or the scene's hue (chroma about 0.005 to 0.015 in
  OKLCH). Pure #808080 greys look dead next to colour; pure black grounds look like a hole (lift blacks).
- Mix and animate colours perceptually: OKLab or OKLCH, never plain sRGB between distant hues (red to green
  through sRGB is brown; through OKLab it stays clean).
- Decide dark or light from a scene sentence; do not default silently to dark.
- Anti-slop: purple and blue gradients by default, gradient text, glow on everything, neon on everything.

## 2. The kit's helpers

| Helper | Use |
|---|---|
| `mix(a, b, t)` | an OKLab mix (`mix(bg, accent, 0.14)` is a soft tint of the ground) |
| `lighten(c, d)`, `darken(c, d)` | move OKLab lightness; 0.05 is a visible step, 0.02 a subtle one |
| `saturate(c, k)` | scale chroma (0 is grey) |
| `oklch(l, c, h)`, `toOklch(c)` | build and read OKLCH; out-of-gamut chroma is reduced, lightness and hue kept |
| `withAlpha(c, a)`, `toHex(c)`, `parseColor(c)` | conversions (parse takes hex, rgb, hsl, oklch, oklab and names) |
| `contrast(fg, bg)`, `luminance(c)` | WCAG 2 ratio (1 to 21) and relative luminance; a translucent colour is laid over the ground first |
| `isReadable(fg, bg, level, large)` | AA: 4.5 body, 3 large; AAA: 7 and 4.5 |
| `readableOn(bg, light, dark)` | the better of two text colours on a fill |
| `ensureContrast(fg, bg, min)` | the same hue moved in lightness until it reads |
| `isDark(c)` | luminance under 0.18: wants light text |
| `shadowTint(ground)` | a very dark colour in the ground's hue for shadows |
| `brandTheme(opts)` | a full theme from brand colours |

In Remotion itself: `interpolateColors(frame, [0, 30], ['oklch(0.7 0.15 250)', 'oklch(0.7 0.15 30)'])` interpolates
through OKLab/OKLCH strings since 4.0.439 (it ignores easing: ease the input instead). CSS gradients take `in
oklab` or `in oklch` (Chrome 111+, which Remotion's headless shell is): `linear-gradient(90deg in oklab, a, b)`.
Per-frame `color-mix(in oklab, a x%, b)` also works in styles.

## 3. Contrast on video

WCAG ratios are the floor, not the target: video is watched on phones, in sunlight, after two compressions, and
H.264 at yuv420p stores colour at half resolution, so small coloured text on a coloured ground blurs first. Aim for
7:1 for small text, 4.5:1 for 32 to 40 px text, 3:1 only for type above about 60 px and for graphics.

The kit's themes, measured with `contrast()`:

| Theme | Dark | Ground | Accent | Text on ground | Muted on ground | Accent on ground | onAccent on accent | Accent2 on ground |
|---|---|---|---|---|---|---|---|---|
| studio | no | #F5F6F7 | #2563EB | 16.4 | 4.5 | 4.8 | 5.2 | 2.0 |
| midnight | yes | #0B0D12 | #5B8CFF | 17.8 | 7.6 | 6.1 | 6.1 | 11.0 |
| keynote | yes | #0A0A0B | #2997FF | 18.2 | 5.5 | 6.6 | 3.0 | 9.6 |
| keynoteLight | no | #FBFBFD | #0071E3 | 16.3 | 4.9 | 4.5 | 4.7 | 2.1 |
| vox | no | #D9D7D1 | #FF8900 | 12.0 | 4.8 | 1.7 | 7.2 | 2.9 |
| editorial | no | #FFFFFF | #D7263D | 18.9 | 5.3 | 5.0 | 5.0 | 8.7 |
| kinetic | yes | #0A0A0A | #E8FF3A | 19.8 | 7.8 | 17.7 | 17.7 | 5.6 |
| swiss | no | #FFFFFF | #E30613 | 19.8 | 5.0 | 4.9 | 4.9 | 19.8 |
| neon | yes | #07091A | #00E5FF | 17.5 | 7.2 | 12.8 | 12.8 | 6.2 |
| retro | yes | #1A0F2E | #FF5E8A | 15.5 | 8.8 | 6.3 | 6.3 | 11.4 |
| corporate | no | #F4F6F9 | #0E7C86 | 16.0 | 5.0 | 4.6 | 4.9 | 7.7 |
| playful | no | #DFF4FF | #FF6B6B | 12.7 | 5.9 | 2.4 | 2.8 | 1.4 |
| whiteboard | no | #FFFFFF | #1E5AFF | 17.4 | 7.5 | 5.3 | 5.3 | 4.4 |
| luxury | yes | #0C0B0A | #C9A45C | 16.9 | 7.2 | 8.4 | 8.4 | 4.0 |
| data | no | #FFFFFF | #E4572E | 18.7 | 5.3 | 3.7 | 3.7 | 4.1 |
| trailer | yes | #050505 | #E0B354 | 18.2 | 5.9 | 10.4 | 10.4 | 3.1 |
| terminal | yes | #0D1117 | #3FB950 | 16.0 | 6.2 | 7.4 | 7.4 | 7.5 |
| brutalist | no | #F2F2F2 | #FF4F00 | 18.8 | 8.7 | 2.9 | 6.4 | 5.6 |
| dhaka | yes | #0E3B2E | #F42A41 | 11.1 | 6.9 | 3.1 | 4.0 | 7.7 |
| fresh | no | #FFFFFF | #00B37E | 17.2 | 6.1 | 2.7 | 2.7 | 2.6 |

Read it before using a colour as text:
- Accents under 4.5 on their ground (vox orange 1.7, playful coral 2.4, fresh green 2.7, brutalist orange 2.9, dhaka
  red 3.1, data orange 3.7) are fills, markers and big type, not small text. For small accent-coloured text use
  `ensureContrast(accent, bg, 4.5)`; the kit's soft and outline pills do this.
- `onAccent` under 4.5 (keynote 3.0, playful 2.8, fresh 2.7): fine on big buttons, not on small labels. The kit's
  solid chips and hard-seam splits fall back to the more readable of onAccent and the theme's dark colour.
- `muted` is at or just above 4.5 on light themes: keep muted text 32 px or larger.
- Accent2 on light grounds is often under 3 (studio amber 2.0): a fill or chart colour, not text.

## 4. Colour on pictures

- Text on a photo gets a scrim from its side (`Scrim`, `FullBleed`); check contrast against the brightest area
  under the text.
- Pick the text colour from the picture region, not the whole picture: `readableOn(regionColour, '#FFFFFF',
  t.colors.text)`.
- Grade pictures towards the palette (warm or cool) with one `colorCorrection()` pass rather than stacking colour
  effects (fx sub-skill).

## 5. Brand kits

`brandTheme({primary, secondary?, dark?, base?, neutral?, fonts?, radius?, name?, grain?, vignette?})` returns a
`ThemeSpec`:

- `accent` is the brand colour exactly; `onAccent` is whichever of white and the theme's text colour reads better
  on it.
- `accent2` is the secondary brand colour, or a counterpart 160 degrees round the OKLCH wheel with similar
  lightness (clamped 0.55 to 0.8) and chroma (0.09 to 0.17).
- Light grounds: bg L 0.975, bg2 0.995, surface white, text 0.21, muted 0.5, faint 0.84, line 0.915, all in the brand's
  hue with a whisper of chroma (at most 0.008, `neutral: 'pure'` for none). Dark grounds: bg 0.17, bg2 0.21, surface
  0.235, text 0.97, muted 0.73, faint 0.42, line 0.31 (chroma at most 0.016).
- `highlight` (marker sweeps) is a light version of accent2.
- Fonts, weights, motion and radius come from `base` (studio or midnight by default): pick the base whose motion
  character fits the brand (corporate for calm, fresh for springy, editorial for masked serif reveals).

```tsx
const brand = brandTheme({primary: '#E4002B', secondary: '#1A1A1A', base: 'corporate', fonts: {display: 'Manrope'}});
<ThemeProvider theme={brand}>...</ThemeProvider>
```

For full control, `makeTheme(base, {colors: {...}, fonts: {...}, radius, motion, texture})` from core replaces any
part of a named theme. A brand kit is usually colours and fonts; keep the base's motion unless the brand has a
motion guide.

Checks for a brand kit (render DemoDesignColor with the brand): accent on ground, onAccent on accent, text on
surface; light brand colours (yellow, lime) stay fills with dark text on them; saturated brand colours as large
fields vibrate on screens and in H.264 (keep them for fills under about 40% of the frame, or tint them into the
ground).

## 6. Theme dials that are colour

`texture.grain` and `texture.vignette` (see grounds-light-texture.md), `dark`, the `highlight` for marker sweeps,
`positive` and `negative` for states. Charts take accent and accent2 as series one and two, greys for the rest,
one highlighted bar in the accent (graphics sub-skill).

## 7. Encoding and colour space

- Render with `--color-space=bt709` (the kit's config and nrk presets do) so colours match players.
- yuv420p halves colour resolution: thin coloured lines and small coloured text soften; `--scale=2` or PNG frames
  for type-heavy masters.
- Give every composition an opaque background for H.264 (transparent frames are flattened onto black without
  antialiasing).
