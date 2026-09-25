# Fonts, measuring and laying out text (Remotion 4.0.528)

Text in a video is laid out once and then animated, so its lines, widths and sizes must be known before the first
frame and must match what the browser draws. That means: load the font, wait until it has really loaded, measure with
exactly the styles you render, and render the measured lines yourself.

## 1. Loading fonts

| Source | How | Notes |
|---|---|---|
| Google Fonts (kit) | the theme roles (`t.type.display` etc.) or core `loadKitFont(key, weights)` / `fontStack(key, weights)` | 45 families with their real weights; every stack ends in a Bangla font and a system fallback |
| Google Fonts (raw) | `loadFont(style, {weights: ['700'], subsets: ['latin']})` from `@remotion/google-fonts/<Name>` | returns `{fontFamily, fonts, unicodeRanges, waitUntilDone}`; one call per style; holds the render with `delayRender` (60 s) per weight and subset |
| Local files | `loadFont({family: 'Brand', url: staticFile('Brand-Bold.woff2'), weight: '700'})` from `@remotion/fonts` (4.0.165) | one call per file; `woff2` preferred; resolves when the FontFace is ready |
| Variable fonts | `loadVariableFont('normal', {subsets: ['latin']})` (4.0.525, variable families such as Inter) | returns `{fontFamily, axes}`; animate `fontWeight` between `axes.wght.min` and `max`; width changes with weight, so centre it or give it a box |

Rules:
- Always pass weights and subsets. A bare `loadFont()` in 4.0 loads every style, weight and subset (dozens of
  requests, a warning above 20, possible timeouts); v5 throws.
- A family name in CSS (`fontFamily: 'Inter'`) loads nothing: you get a fallback font and, worse, fallback
  measurements. CSS `@import` or `<link>` does not block rendering either.
- CJK subsets (`'chinese-simplified'` and so on) resolve to many numbered files; `ignoreTooManyRequestsWarning: true`
  only when that is intended.
- The Google Fonts loader adds a FontFace to `document.fonts` only after it has loaded, so `document.fonts.ready` or
  `document.fonts.load()` cannot tell you it is done. Use the loader's `waitUntilDone()`.

## 2. Waiting before measuring

The kit's `useTypeFontsReady(roles, extra)` returns false until the theme fonts of those roles (plus any extra kit fonts)
have loaded, and holds the render with a `delayRender` handle made in a `useState` initializer until then; the handle
is released in an effect after the ready state has rendered (and on unmount, for Studio scrubbing). Measure in a
`useMemo` keyed on `ready` and the text and style.

```tsx
const ready = useTypeFontsReady('display');
const style = typeStyle(t, unit, text, {size: 120}, 120);
const layout = useMemo(() => (ready ? layoutText(text, style, {maxWidth: 900 * unit, maxLines: 2}) : null), [ready, text]);
if (!layout) return null;
```

`<WaitForFonts roles={['display', 'body']}>` renders children only after the fonts, for your own measuring
components. Without the kit: keep the `loadFont()` results in one module, `await x.waitUntilDone()` in an effect,
set state, and `continueRender()` in a second effect once that state has rendered.

## 3. `@remotion/layout-utils`

| Function | Since | Input | Output |
|---|---|---|---|
| `measureText` | 4.0.50 | `text, fontFamily, fontSize, fontWeight?, letterSpacing?, fontVariantNumeric?, textTransform?, validateFontIsLoaded?, additionalStyles?` | `{width, height}` |
| `fitText` | 4.0.88 | `text, withinWidth, fontFamily, fontWeight?, letterSpacing?, ...` | `{fontSize}` for one line (cap it yourself) |
| `fitTextOnNLines` | 4.0.313 | `text, maxBoxWidth, maxLines, fontFamily, ..., maxFontSize? (2000)` | `{fontSize, lines}` |
| `fillTextBox` | 4.0.57 | `{maxBoxWidth, maxLines}` then `.add({text, fontFamily, fontSize, ...})` per word | `{exceedsBox, newLine}` |

How they work (source-verified):
- `measureText` appends a span (`display: inline-block; position: absolute; top: -10000px; white-space: pre`) to
  `document.body`, reads `getBoundingClientRect()` and removes it. Global CSS (resets, Tailwind preflight) applies to
  that span too. It throws `measureText() can only be called in a browser.` in Node (never call it in
  `calculateMetadata`).
- Results are cached for the page lifetime by text, family, weight, size, letter spacing, transform and
  `additionalStyles`, but **not** `fontVariantNumeric`, and never invalidated: a measurement taken with a fallback
  font stays wrong.
- `validateFontIsLoaded: true` measures a second time with the default font and throws when both boxes match, the
  computed families differ and the text has more than 4 distinct characters. Its default is false in 4.0 (true in v5):
  pass it explicitly.
- `fitText` measures at 100 px and scales linearly. Letter spacing in px does not scale: give it in em.
- `fitTextOnNLines` binary-searches the size between 0.1 and `maxFontSize` in 0.01 px steps, splitting the text on
  single spaces and filling lines greedily with `fillTextBox` (which trims leading spaces and reports `exceedsBox`
  when one word is wider than the box). Scripts without spaces are one word and only shrink.
- `fillTextBox` sums the widths of single words; kerning across a space is ignored (sub-pixel).

## 4. The kit's layout (balanced lines)

`layoutText(text | lines, style, {maxWidth, maxLines, balance = true, shrink = true, minSize})` measures every word once
at 100 px, then does the rest in arithmetic: greedy lines, then **balanced** lines (the narrowest width that keeps the
same line count, the way `text-wrap: balance` works), and, with `shrink`, a binary search for the biggest size that
fits `maxLines` without any word wider than the box. It returns every line with its words and their x offsets, the
size found, the space width and the line height, so components can place words absolutely (the caption pill) or
render explicit lines.

Which to use:

| Need | Use |
|---|---|
| Width of one string | `measureTextWidth` (kit) or `measureText` |
| Biggest size for one line | `FitText` or `fitText` capped with `Math.min` |
| Biggest size on N lines, lines returned | `FitText maxLines={n}` (greedy) or `layoutText` (balanced) |
| Headline lines that look set by hand | `layoutText` / `KineticTitle` (balanced) |
| Pages of words that fit a box | `fillTextBox` or `captionPages` + `layoutText` |
| A plate hugging ragged lines | `createRoundedTextBox` (section 7) |

## 5. Rendering what was measured

- One style object for both: the kit's `typeCss(style)` gives `fontFamily`, `fontWeight`, `fontSize`,
  `letterSpacing` (em), `lineHeight`, `textTransform`, `textRendering: geometricPrecision`, `fontKerning: normal`.
- Render each measured line as its own block with `white-space: pre`; never let the browser wrap measured text again.
- No `padding` or `border` on measured text (use `outline` for debug boxes); no `useCurrentScale()` multiplication.
- Debugging a mismatch: in Studio at 100 %, render a `display: inline-block; white-space: pre` div with the same
  text and styles next to the real node and compare their boxes and computed styles in DevTools. Usual causes:
  whitespace, CSS resets, padding or border, font not loaded, px tracking.

## 6. Baselines and scale

- Type grows with `scale`, never by animating `fontSize` (reflow and pixel snapping). Scale around the **baseline**:
  vertical judder under slow scale fell from 0.28 px (centre pivot) to 0.014 px (baseline pivot) in community
  measurements, and `textRendering: 'geometricPrecision'` cut glyph drift from 3.4 % to 0.2 %.
- The kit's `baselineRatio(family, weight, lineHeight)` reads the primary font's ascent and descent from canvas
  `TextMetrics` (`fontBoundingBoxAscent`/`Descent`) and returns where the baseline sits in a line box:
  `(halfLeading + ascent) / lineHeight`, with `halfLeading = (lineHeight - (ascent + descent)) / 2`. Use it as the y of
  `transformOrigin`.
- No `will-change` on text in renders (parallel tabs keep stale rasters and held text shimmers).
- Slow sub-pixel drifts of text look choppy: hold text still and move the camera or the ground instead.

## 7. `@remotion/rounded-text-box` (4.0.360)

`createRoundedTextBox({textMeasurements, textAlign, horizontalPadding, borderRadius})` returns `{d, boundingBox,
instructions}`: one outline around stacked lines of different widths, rounded outer corners and inverse-rounded inner
corners (the TikTok and Instagram plate).
- `textMeasurements`: one `{width, height}` per line, measured with the same line height you render (pass it through
  `additionalStyles: {lineHeight}` when using `measureText`). Lines stack with no gap.
- Corner radius is clamped to half of each line's height; inner corners follow half (left or right aligned) or a
  quarter (centred) of the width difference between neighbouring lines.
- Render: a relative box of `boundingBox.width` by `height`; an absolute `<svg viewBox={boundingBox.viewBox}
  style={{overflow: 'visible'}}>` with the path; then the lines, each with `paddingLeft/Right = horizontalPadding`
  and the same `textAlign`.
- House values: horizontal padding about 0.4 of the font size, radius about 0.35 of it, line height 1.3 to 1.4 (1.5
  for Bangla). Animate the plate with a spring scale from its centre, a clip wipe, or `evolvePath()` on the outline
  followed by the fill.

## 8. Tracking and leading (px at 1080)

| Text | Tracking | Leading |
|---|---|---|
| Display 160 px and up | theme display tracking (-0.03 to -0.045 em), never tighter than -0.05 | 0.98 |
| Display 100 to 160 | theme display tracking | 1.02 |
| Display 64 to 100 | 60 to 100 % of it | 1.08 |
| Body 32 to 56 | 0 | 1.3 to 1.4 |
| Caps labels under 48 | +0.06 to +0.12 em | 1.2 |
| Captions | 0 to -0.02 em | 1.14 (Bangla 1.42) |
| Any Bangla or other complex script | 0 | display at least 1.28, body 1.5 |

The kit's `trackingFor(theme, size, text, role, caps)` and `leadingFor(text, size, role)` apply this table.
