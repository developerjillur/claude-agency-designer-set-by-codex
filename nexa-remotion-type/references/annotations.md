# Emphasis on words: marker sweeps and hand-drawn annotations

Two families. A **marker sweep** is a clean, flat bar behind the words (editorial, product, data). A **hand-drawn
annotation** is a rough stroke from `@remotion/rough-notation` (explainers, whiteboard, notebook, social). Use one
emphasis per sentence, after the text has landed (6 to 8 frames later), and stagger several by 10 to 20 frames.

## 1. Marker sweeps (the kit's `Marker`)

Technique: one `linear-gradient` background on the **inline** element, `background-repeat: no-repeat`, growing
`background-size: p% h`. With `box-decoration-break: slice` (the default), an inline box broken over several lines
is laid out as one long strip, so the percentage fills the first line, then continues on the next: the sweep follows
the text in reading order across wraps. With `clone` every line would fill at once.

| Shape | Height | Position | Look |
|---|---|---|---|
| `marker` | 0.5 em | 86 % down | a highlighter over the lower half |
| `block` | the line | centre | a selection |
| `underline` | 0.085 em | 96 % | a thin rule |
| `strike` | 0.085 em | 58 % | a strike line |

- The background is painted behind the text of the same element, so an opaque colour is fine on light grounds (dark
  text stays on top). On dark grounds use the highlight at 30 to 40 % alpha (the kit does), or light text turns
  unreadable on a bright bar.
- Horizontal padding (0.08 em) with an equal negative margin lets the bar bleed past the first and last letter
  without moving the text.
- Exit: wipe it away toward the end (`backgroundPosition: 100%` with a shrinking size) at the Sequence end.
- 18 frames with an in-out curve reads as a hand sweep; 10 frames as a snap.

**Block with repainted text** (the kit's `KineticTitle emphasisStyle="block"`, and `marker` on dark themes): a bar
covering the whole line box grows behind one word; a second copy of the word in the ground colour sits on top,
clipped with `clip-path: inset(-40% (1 - p)% -40% q%)` to the bar's extent. Letters change colour exactly at the bar's
edge, so white text on an acid-yellow bar is never unreadable. When the word leaves, the bar clears from the left.

## 2. `@remotion/rough-notation` (4.0.490)

Components: `Highlight` (drawn behind the text), `Underline`, `StrikeThrough`, `CrossedOff`, `Box`, `Bracket`,
`Circle` (drawn on top). Import with aliases: `Circle` and `Box` clash with other names
(`import {Circle as RoughCircle} from '@remotion/rough-notation'`).

Common props: `children`, `progress` (0 to 1, required; drive it with a clamped `interpolate`), `style` (on the text
span, which is forced to `display: inline-block; position: relative; white-space: pre`), `disabled`, `seed` (1),
`color` (`currentColor`), `roughness` (3 for Highlight, 1.5 for the rest), `maxRandomnessOffset` (5), `bowing` (1),
`disableMultiStroke`, `preserveVertices` (false), and Sequence props (`from`, `durationInFrames`, `trimBefore`,
`playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`; premount props from 4.0.528).

| Component | Stroke width | Iterations | Other |
|---|---|---|---|
| Highlight | line height plus top and bottom padding | 2 | `padding`, `rtl` |
| Underline | 20 | 2 | `padding.top` moves it down, `rtl` |
| StrikeThrough | 20 | 1 | `rtl` |
| CrossedOff | 20 | 1 per diagonal | `rtl` |
| Box | 7 | 2 | `padding` |
| Bracket | 20 | n/a | `padding`, `bracketLeft` (false), `bracketRight` (true), `bracketTop`, `bracketBottom` |
| Circle | 20 | 2 (each with seed + i) | `padding`, `box` (`around` scales the ellipse by the square root of 2 to enclose the box; `inside` fits the padded box), `curveFitting` 0.95, `curveTightness` 0, `curveStepCount` 9 |

Behaviour and traps (source-verified):
- Strokes draw one after another: with n paths, path i draws while `progress * n - i` goes 0 to 1 (two iterations:
  the first stroke in the first half). Highlight, underline, strike and cross alternate direction per stroke.
- **Default colour `currentColor`**: a Highlight in the text colour hides the text. Always pass a translucent colour
  (about `rgba(255, 221, 64, 0.62)` on white).
- **Single stroke by default**: every type is built with `disableMultiStroke: true` whatever the docs say; pass
  `disableMultiStroke={false}` for the doubled pencil line.
- The annotated text never wraps: annotate short phrases, or one component per word (a multi-word highlighter: word i
  covers `[i/n, (i+1)/n]` of one phrase progress, each with its own seed).
- It measures its span (`offsetLeft/Top/Width/Height`, a ResizeObserver) and holds the first render until a size is
  known; hidden or empty children can stall until the delayRender timeout. Measure after the fonts load (the kit
  mounts the annotation only then).
- The component wraps itself in a `<Sequence layout="none" from={from}>`: before `from` the **text itself** is not
  rendered. Drive `progress` instead of using `from` when the text must show before the mark.
- Strokes are recomputed every frame in a layout effect; keep a few per frame.

Looks (from Remotion's own element values):
- Text marker: highlight `rgba(255, 236, 79, 0.62)`, roughness 2.3, maxRandomnessOffset 10, bowing 0, 20 px side
  padding, 25 frames with a spring ease.
- Circle marker: stroke 12, roughness 1.8, padding 10, `box="inside"`, 43 frames, progress and seed posterized every 4
  frames for a hand-drawn, boiling line.
- Strike: stroke 14, red, 15 frames. Crossed off: 10 iterations, roughness 2, stroke 6 for an angry scribble.
- Boiling line: after the stroke has drawn, `seed = 1 + Math.floor(frame / 4)` (a new shape every 4 frames at 30 fps;
  faster than every 3 looks noisy).

## 3. The kit's `Annotate`

Defaults in em of the annotated text (read from the page), so marks fit 40 px labels and 200 px headlines alike:
circle stroke 0.07 em, highlight padding 0.14 em, underline 0.075 em, box 0.055 em, strike 0.08 em, cross 0.07 em,
bracket 0.075 em. A circle's padding is computed from the text's box so the ellipse encloses the corners of the words
(an inscribed ellipse cuts through the first and last letters), and circles, boxes and brackets take a margin so they
do not run into the next word. Colours: translucent highlight (62 %, 40 % on dark), accent for marks, the theme's
negative colour for strike and cross. `multiStroke` true, `boil` optional, `role` = the font to wait for.

```tsx
Most teams lose <Annotate kind="circle" delay={34} role="serif">four hours</Annotate> every week.
<Annotate kind="highlight" delay={60} role="body" boil>new pricing</Annotate>
```

## 4. Choosing

| Want | Use |
|---|---|
| a phrase in running text, possibly wrapping | `Marker` |
| one word in a big title | `KineticTitle` emphasis (`punch`, `marker`, `block`) |
| a number or short phrase, playful or explainer | `Annotate kind="circle"` |
| correction ("was 1 hour, now 15 minutes") | `Annotate kind="strike"` or `"cross"` on the old value, then the new value |
| a notebook or whiteboard look | `Annotate` with `boil`, a hand font (`role="hand"`) |
| a label on a chart or screenshot | `Annotate kind="box"` or `"bracket"` |
