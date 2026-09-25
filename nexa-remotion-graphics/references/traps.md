# Traps, errors, determinism, performance, version gates

## 1. Errors and fixes

| Symptom or message | Cause | Fix |
|---|---|---|
| `Cannot destructure property 'x' of null` after `getPointAtLength` | a length past the end returns null on 4.0.528 (even by floating error) | `pointOnPath` / `pathPose`, or clamp to `getLength(d)` and check for null |
| `A length of X was passed to getInstructionIndexAtLength()` | length past the end | clamp |
| `Malformed path data` | a bad `d`, often a missing `M` or a CSS `path("...")` string with quotes | check with `parsePath(d)`; strip quotes |
| `No path provided` | an empty `d` reached `getLength`, `getBoundingBox` or `getPointAtLength` (for example `smoothPath([])`) | the kit's helpers and `PathFollow`, `DrawPath`, `Morph` treat an empty `d` as nothing to draw; guard your own calls with `d.trim()` |
| `Malformed path data` with `NaN` in the string, or a chart with every bar or slice missing | one NaN value made the shared domain or a running sum NaN (`Math.min`/`Math.max` spread it, and `NaN === NaN` is false, so equal-ends guards miss it) | filter with `Number.isFinite` before scales and sums (the kit's charts do) |
| `interpolatePaths is not a function` / not exported | 4.0.529 API | `morphAt(frame, frames, paths, ease)` from the kit |
| Morph twists, crosses or turns inside out | different start points or winding | kit `mode="points"` (aligns rotation and winding), or reorder the source path |
| A dot at the start of a line before it draws | a round cap on a zero-length dash | do not render at progress 0 (the kit hides it) |
| Every part of an icon draws at the same time | one dash over several subpaths (Chrome restarts dashes per subpath) | `DrawnPath` (a dash per subpath) with `mode="sequence"` |
| A dashed line does not draw on | the draw-on dash replaces the dash pattern | cut it (`dash` prop / `cutPath`) or reveal with a clip |
| `"cornerRadius" and "edgeRoundness" cannot be specified at the same time` | both passed to a shape | pick one |
| `"pointerPosition" must be a number between 0 and 1` | callout pointer out of range | clamp; keep clear of rounded corners |
| Chart labels in the wrong place in some frames | text measured before the font loaded (the layout-utils cache keeps it) | do not measure charts; the kit estimates their layout |
| A callout bubble or a circled word is sized for a narrower font on the first frame of a render (a still is all first frame) | `@remotion/google-fonts` fetches the file, then adds the FontFace to `document.fonts` only once loaded: `document.fonts.ready` resolves before the font exists, and a width change inside a capped box fires no ResizeObserver | wait until no pending `delayRender` handle is a font load (the kit's `useMeasuredSize` does), or await `loadFont(...).waitUntilDone()`; re-measure every frame in a layout effect |
| A wrapped bubble shows empty space beside its lines | a wrapped box keeps its maximum width | measure the widest line (text-node client rects) and draw the bubble to it; never re-flow the text into the narrower box (`text-wrap: balance` breaks differently there, and measuring the constrained box feeds back) |
| Render hangs at a callout or a marked word | a measuring hook never released its handle (the element never mounted) | keep the measured node mounted (the kit renders it hidden first) |
| Dates one day off on another machine | local-time scales and `new Date('2026-06-15')` parsing | `Date.UTC(...)`, `scaleUtc`, `formatChartDate` (UTC) |
| Numbers print differently on another machine | `toLocaleString` / `Intl` depend on locale data | `formatValue` |
| Digits jiggle while counting | proportional digits | `fontVariantNumeric: 'tabular-nums'` (kit default) |
| A counter flickers through extra decimals | interpolated floats formatted raw | `countValue(from, to, p, decimals)` |
| Gridlines look heavy on Swiss or brutalist themes | full-ink line colour | `gridOf(theme)` (kit default) |
| d3 chart flickers or labels double up | d3 appending to the DOM in effects | compute with d3-scale/d3-shape, render with React |
| `Could not find a declaration file for module 'd3-format'` | no @types for d3-format in the kit | do not import d3-format; use `formatValue` or `scale.tickFormat()` |

## 2. Determinism (render tabs render frames out of order)

- Every value comes from the frame and props: no `Math.random`, `Date.now`, timers, `requestAnimationFrame` loops,
  CSS transitions or animations, or state that builds up across frames.
- Randomness: `rand(seed)` from core, `noise2D(seed, x, y)` from @remotion/noise (the hand marks' wobble), a mark's
  `seed`.
- A glide that looks like memory (the bar race's rank) is recomputed from earlier frames' values each frame.
- Measuring (callouts, marked words, chart titles) happens once per mount after fonts load, inside `delayRender`, and
  gives the same size in every tab.
- SVG ids (gradients, clips) come from `useId()`, never a counter or random.

## 3. Performance

- Cache path parsing: `pathLength`, `subpathsOf`, `resamplePath` are cached; `getPointAtLength` in a loop per frame
  is the usual slow spot.
- The line chart solves each dot's arrival frame and x position once (cached), not every frame.
- perfect-freehand on a few hundred points per mark per frame is cheap; boiling marks recompute geometry every
  `boil` frames only.
- The bar race sorts names `smoothing` times per frame: fine for 30 names, keep `smoothing` under 12.
- Many charts on screen at once multiply the work; one chart per scene is also the better design.

## 4. Version gates (relative to 4.0.528)

Available: @remotion/paths (all but `interpolatePaths`), `centerPath` 4.0.486, `getInstructionIndexAtLength` 4.0.84,
@remotion/shapes with `effects`, `pathStyle`, `debug` and Sequence props, `Heart` 4.0.315, @remotion/rough-notation
4.0.490 (premount props 4.0.528), `Easing.spring()` 4.0.476, easing arrays per segment 4.0.462, `posterize` 4.0.470,
`output: 'perceptual-scale'` 4.0.490 (on `interpolate`), `useDelayRender()` 4.0.342, `interpolateColors`.
Not available: `interpolatePaths` (4.0.529). v5 changes to expect: `getPointAtLength` null past the end (already so).

Packages the module uses (all pinned in the kit): `@remotion/paths`, `@remotion/shapes`, `@remotion/noise`,
`d3-scale` 4.0.2, `d3-shape` 3.2.0, `perfect-freehand` 1.2.3.

## 5. Pre-render checklist for a graphics scene

1. Typecheck and stills: `nrk.py stills PROJECT`; a full-size still of the settled frame.
2. The title's claim matches the numbers; source line present; bars from zero.
3. One highlight; it lands on its word; the build finishes before the voice moves on.
4. Labels: none overlapping, none outside the safe area, Bangla shaped (no broken conjuncts), digits tabular.
5. Last frame: nothing half-visible (exits finish on the last frame of their Sequence, or the chart holds whole).
6. Two themes if the piece is a template (light and dark): gridlines, greys and callout colours still read.
