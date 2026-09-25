# Charts in video: rules, forms, the kit's charts, and building your own

A chart in a video is read once, at the speed of the voice, with no hover and no second look. So it must say one
thing, build in the order it is read, label itself, and hold still long enough to be read. Everything below serves
that.

## 1. Honesty rules (and why)

| Rule | Why | Kit |
|---|---|---|
| Bars start at zero | a bar's length is read as its value; a cut axis turns 10% into "three times" | `BarChart`, `BarRace`, `Comparison` always include 0 |
| Same scale for things compared | two charts side by side are read as one scale | pass the same `max` |
| Lines may skip zero only when the shape is the point (prices, temperature) and the axis shows it | a line's slope is read, not its height | `LineChart zero={false}` |
| Area and radius: size by area | a circle twice as wide looks four times as big | `scaleSqrt` for bubble radius |
| No 3D, no perspective on data | depth distorts length and angle | never |
| Title states the finding, and the data supports it | viewers remember the title | check the words ("nearly half" at 48%) |
| Say the source | trust; and made-up numbers must say 'Example data' | `ChartFrame source` |
| Counting numbers show in-between values | 1996, 1997 read as facts | `Stat mode="none"` or `'roll'` for years, prices |
| Round for reading, keep the source's precision | 1,234,567.89 is unreadable in 2 s | `format={{compact: true}}` |

## 2. Which chart

| Question the scene answers | Form | Kit | Notes |
|---|---|---|---|
| Which is biggest? ranking | horizontal bars, sorted | `BarChart orientation="horizontal" sort="desc"` | long labels fit; best in 9:16 |
| How do a few categories compare? | vertical bars | `BarChart` | 3 to 8 bars |
| Gains and losses | bars around zero | `BarChart` (negatives in the negative colour) | label below negative bars |
| How did it change over time? | line | `LineChart` | 12 points per series, 4 series at most |
| How did a total change, few periods | vertical bars | `BarChart` | 3 to 6 periods |
| Share of a whole (2 parts) | split bar, ring | `Comparison mode="share"`, `ProgressRing` | never a 2-slice pie |
| Share of a whole (3 to 6 parts) | donut with highlight | `Donut` | merge small ones into Other |
| One number | big number | `Stat` (+ `delta`, `Sparkline`) | |
| Before and after, A and B | two numbers with bars | `Comparison` | `lowerIsBetter` for time, cost |
| Ranks over time | bar race | `BarRace` | 8 to 10 bars, 1.5 s per step |
| Progress toward a goal | ring or bar | `ProgressRing`, `ProgressBar segments` | |
| Composition over time | stacked bars or areas | build with d3 `stack` (section 6) | 4 layers at most |
| Two measures per item | scatter | build with `ChartRoot` (section 6) | label the few that matter |
| Two categories x values | grouped bars | build (section 6) | 2 or 3 groups |
| Density over a grid | heatmap | build: rects with a sequential colour | label the extreme cells |
| Steps, pipelines | flow | `FlowDiagram` | see diagrams.md |
| Dates | timeline | `Timeline` with `at` | |

## 3. Anatomy and sizes (px at 1080 short side)

| Part | 16:9 | 9:16 | Notes |
|---|---|---|---|
| Title | 58 to 64, display face | 52 to 58 | one sentence, the finding |
| Subtitle | half the title | same | what is measured and the unit |
| Value labels | 36 to 44 bold | 36 | on the marks |
| Category labels | 26 to 30 | 28 to 30 | under vertical bars, left of horizontal |
| Ticks, axis captions | 22 | 24 | muted |
| Source | 22 | 22 | bottom-left, muted |
| Bars | at most 190 wide (vertical), 76 tall (horizontal) | 76 to 88 | the kit caps them |
| Lines | 5 to 7 stroke | 6 | dots 1.05 x stroke radius |
| Gridlines | 2 px, `gridOf(theme)` | | softer than any data mark |
| Baseline | 3 px, text colour at 85% | | drawn first |

Colour: the highlight takes the accent, the rest `neutralOf(theme)`. Several series: `seriesColors(theme, n)` (the
two accents, then tints, then greys). Positive and negative: the theme's `positive` and `negative`. Text on a
coloured fill: `textColorOn(fill)`.

## 4. The kit's charts, how they build

### BarChart
Order: gridlines fade and the baseline draws (14 f) -> each bar grows from zero (24 f, theme curve) with a stagger
in reading order (left to right, top to bottom) -> its category label rises with it -> its value label lands as it
settles (`values="land"`), or rides the tip counting (`values="count"`) -> at `highlightAt`, the others turn grey
(12 f). Exit `'shrink'` sinks bars last in first out.

Layout it does for you: tick label width is estimated from the formatted ticks; value headroom above the tallest
bar; two-line category labels when a label is wider than its band; label column for horizontal bars sized to the
longest label (12% to 36% of the width); negative bars get room below.

Choices: `valuePosition="inside"` for long bars in a clean look (it falls back outside when the label would not
fit); `axis` on for vertical (readers compare to gridlines), off for horizontal (values are on every bar);
`sort="desc"` for rankings; `max` to share a scale.

### LineChart
Order: gridlines, zero line -> series draw left to right one after another (66 f, `stagger` 16 f) with a moving head
dot -> dots pop when the line reaches them (the frame is solved with `frameAtProgress`) -> the area wash follows the
head (a clip at the head's x) -> end labels arrive when each line finishes -> callouts open 2 f after the line
reaches their x.

X values: strings are categories (evenly spaced, every nth label shown when crowded), numbers are a linear scale,
Dates are a UTC time scale with true spacing (uneven readings keep their gaps). Y: `zero` true by default; the
domain is made nice; ticks drop forced decimals.

Choices: `curve="smooth"` is monotone (it never overshoots the data between points); use `'linear'` for few,
irregular readings and `'step'` for values that jump (prices per plan, rates). `highlight` greys and thins the
others. `dashed: true` on a series for targets and forecasts (revealed by a clip).

### Donut and Pie
Order: a single sweep from 12 o'clock clockwise (48 f, in-out) -> each label (name over value, with a leader out
along the slice middle and across) arrives as the sweep passes its slice -> the centre counts the total -> the
highlighted slice pulls out with a small overshoot. Labels on each side are pushed apart so they never overlap.

### BarRace
Values ease between snapshots (hold 10 f, move 35 f); ranks are sorted each frame and averaged over the last 8
frames, so bars glide past each other; the bigger value is drawn on top; the scale follows the leader from zero;
bars leaving the top N fade as they slide out; the snapshot label sits large and faint in the corner. In-between
values keep the snapshots' decimals. A race shows sizes, so negative values count as 0; with fewer names than `top`
the rows fill the box. Length: `barRaceFrames(snapshots, step, hold, delay)`.

### Stat, Sparkline, ProgressRing, ProgressBar, Comparison
Counts use `countValue` so every step shows the final value's decimals (no flicker of extra digits) and reserve the
final width (an invisible copy of the final number sits in the same grid cell). The odometer (`mode="roll"`) rolls
each digit column to its digit, right-hand columns spinning more, with a slight vertical blur while fast.

## 5. Number formatting (`formatValue`)

```ts
formatValue(1234567)                                        // 1,234,567
formatValue(1234567, {compact: true})                       // 1.2M
formatValue(0.4, {suffix: '%', decimals: 1})                // 0.4%
formatValue(-1.2, {prefix: '$', suffix: 'M', decimals: 1})  // −$1.2M (true minus sign)
formatValue(12.4, {suffix: '%', sign: 'always'})            // +12.4%
formatValue(1234567, {grouping: 'south-asian'})             // 12,34,567
formatValue(1234567, {grouping: 'south-asian', compact: true}) // 12.3L
formatValue(25000000, {grouping: 'south-asian', compact: true}) // 2.5Cr
formatValue(1234567, {grouping: 'south-asian', digits: 'bengali', prefix: '৳'}) // ৳১২,৩৪,৫৬৭
```
- Decimals: default is the value's own (up to 3); compact values get 1 decimal under 100 and trailing zeros are
  trimmed (1K, not 1.0K; 999,600 becomes 1M, not 1000K).
- Currency before the number, units after with a space for words (`' kg'`, `' h'`), none for `%`, `K`, `M`.
- Bangla digits come from the Bangla fallback font of the theme stack (Anek Bangla by default), which is wider than
  Latin digits: give Bangla numbers about 10% more room or a smaller size.
- `tickFormat(format)` for axes (decimals per tick, zero as `0`); `formatChartDate(date, 'month-year' |
  'month-day' | 'year' | 'month')` in UTC.
- Why not `Intl.NumberFormat`: it depends on the browser's ICU data and locale; the kit's formatter prints the same
  characters on every machine.

## 6. Building a custom chart with the kit's blocks

The pattern every kit chart uses:
1. `const {width: W, height: H, delay} = useChartBox(props.width, props.height, props.delay);` (size and start from a
   ChartFrame, or the safe area)
2. Scales from `d3-scale` over the plot area (leave margins for labels, estimated with `estimateLabelWidth`).
3. Geometry as SVG elements in px-at-1080 coordinates; text as `ChartLabel` (HTML, wraps, shapes Bangla).
4. Progress per element from `ramp(frame, start, duration, ease)`; staggers in reading order.
5. `<ChartRoot width={W} height={H} svg={svgNodes}>{labels}</ChartRoot>`.

Stacked bars (composition over time):
```tsx
import {stack} from 'd3-shape';
import {scaleBand, scaleLinear} from 'd3-scale';
const StackedBars: React.FC<{rows: {period: string; a: number; b: number; c: number}[]}> = ({rows}) => {
  const frame = useCurrentFrame();
  const t = useTheme();
  const {unit} = useStage();
  const {width: W, height: H, delay} = useChartBox();
  const keys = ['a', 'b', 'c'] as const;
  const layers = stack<(typeof rows)[number]>().keys(keys)(rows);
  const x = scaleBand<string>().domain(rows.map((r) => r.period)).range([60, W - 20]).paddingInner(0.3);
  const y = scaleLinear().domain([0, Math.max(...rows.map((r) => r.a + r.b + r.c))]).nice().range([H - 60, 20]);
  const colors = seriesColors(t, keys.length);
  const svg = layers.flatMap((layer, li) =>
    layer.map((d, i) => {
      const p = ramp(frame, delay + i * 5 + li * 8, 20, curves.out); // bottom layer first, then up
      const y0 = y(d[0]);
      const y1 = y0 + (y(d[1]) - y0) * p;
      return <rect key={`${li}-${i}`} x={x(rows[i].period)} width={x.bandwidth()} y={Math.min(y0, y1)} height={Math.abs(y1 - y0)} fill={colors[li]} />;
    }),
  );
  return <ChartRoot width={W} height={H} svg={svg}>{rows.map((r) => (
    <ChartLabel key={r.period} x={(x(r.period) ?? 0) + x.bandwidth() / 2} y={H - 44} anchor="top" style={{fontFamily: t.type.body, fontSize: 26 * unit, color: t.colors.text}}>{r.period}</ChartLabel>
  ))}</ChartRoot>;
};
```
Label the top segment's total above each stack; label layers once, at the right end (direct labels).

Scatter: `scaleLinear` for both axes (`.nice()`), `scaleSqrt` for a size, dots pop in x order (`ramp` from `delay
+ rank * 2`), label only the 3 to 5 points the voice names, with `Callout` or a `ChartLabel` beside the dot.

Grouped bars: an outer `scaleBand` for the category and an inner `scaleBand().domain(groups).range([0,
outer.bandwidth()])` for the group; one colour per group from `seriesColors`, direct labels on the first category
only.

Heatmap: `scaleBand` for rows and columns, a sequential colour by `mixColor(t.colors.bg2, t.colors.accent, value /
max)`; cells fade in along a diagonal (`delay + (row + col) * 2`); label the maximum cell.

Animating between two datasets (the same chart, new numbers): interpolate each value from old to new with one
`ramp` and redraw; for bars keep the order fixed, for rankings interpolate ranks as `BarRace` does; for lines
interpolate y per point (both series need the same x values).

## 7. d3-scale in one page (v4, pure functions)

| Scale | Build | Use | Notes |
|---|---|---|---|
| `scaleLinear()` | `.domain([min, max]).range([px0, px1])` | values | `.nice(n)` rounds the ends; `.ticks(n)` about n round ticks; `.tickFormat(n, spec)` d3-format; `.invert(px)`; `.clamp(true)` |
| `scaleBand<T>()` | `.domain(keys).range([a, b])` | bars | `.paddingInner(0.3)` space between, `.paddingOuter(0.15)` at the ends, `.align(0.5)`; `.bandwidth()`, `.step()` |
| `scalePoint<T>()` | same | categories on a line | `.padding(0.5)` half a step at the ends |
| `scaleUtc()` | `.domain([d0, d1])` | dates | `.ticks(n)` picks day, week, month or year steps; stays in UTC |
| `scaleTime()` | same | dates in the machine's local zone | avoid in renders: a different zone moves the ticks |
| `scaleLog()` | `.domain([1, 1e6])` | orders of magnitude | domain must not include 0 |
| `scaleSqrt()` | `.domain([0, max]).range([0, rMax])` | circle radius for area | |
| `scaleOrdinal()` | `.domain(keys).range(colors)` | colours by key | |

`nice()` changes the domain; call `ticks()` after it. Ticks from a nice linear scale always include the domain ends.

## 8. d3-shape in one page (v3, pure functions)

- `line<T>().x(fx).y(fy).curve(curve)(data)` returns a path string (or null for no data); `.defined(fn)` breaks the
  line at gaps.
- `area<T>().x(fx).y0(baseline).y1(fy).curve(curve)(data)`.
- `arc().innerRadius(r0).outerRadius(r1).startAngle(a0).endAngle(a1).padAngle(p).cornerRadius(c)(datum)`: angles in
  radians, 0 at 12 o'clock, clockwise; the path is centred on (0, 0): translate it. `.centroid()` for a label spot.
- `pie<T>().value(fn).sort(null)(data)` gives start and end angles per datum (`sort(null)` keeps your order).
- `stack<T>().keys(keys).order(stackOrderNone).offset(stackOffsetNone)(rows)`: layers of `[y0, y1]` per row.
- Curves: `curveMonotoneX` (data: passes through every point, never overshoots), `curveLinear`, `curveStep`,
  `curveStepAfter`, `curveStepBefore`, `curveCatmullRom.alpha(0.5)` (smooth decorative lines through points),
  `curveBasis` (smooth but does NOT pass through the points: never for data), `curveNatural`, `curveBumpX`
  (connectors between columns).
- `linkHorizontal()` / `linkVertical()`: S-shaped connectors for trees.

## 9. Timing budgets (30 fps)

| Build | Frames | Curve |
|---|---|---|
| gridlines and baseline | 12 to 16 | out |
| one bar | 20 to 28 (taller bars can take 2 to 8 more) | theme arrival, or `outBack` for playful looks |
| bar stagger | 4 to 6 | |
| line series | 50 to 80 | in-out |
| dot pop | 8 to 12 | outBack |
| donut sweep | 40 to 55 | in-out |
| counter | 40 to 45 (90 for a hero number) | out-cubic or out-expo |
| highlight focus | 10 to 14 | |
| hold before the cut | 45+ (1.5 s), longer for many labels (`readingFrames`) | |

A chart scene is 4 s or more; the build takes no more than half of it.

## 10. 9:16

- Horizontal bars instead of vertical; 6 bars fill the safe box well.
- Vertical timelines; flow diagrams run down (`direction="auto"` does it).
- Keep everything in the safe box (x 65 to 940, y 270 to 1248 at 1080 x 1920); the bottom 670 px are for captions
  and platform buttons.
- Bigger type than 16:9 relative to the frame: labels 28 to 30, values 36 to 40, titles 52 to 58.

## 11. Chart scene checklist

1. The title is the finding and the data supports its words.
2. One highlight, in the accent, on the thing the voice names; everything else grey.
3. Values are on the marks; no legend unless several series cannot be labelled at their ends.
4. Bars from zero; shared scales where compared; source line present.
5. Build finishes within the first half of the scene; hold at least 1.5 s.
6. Full-size still of the last frame: no label overlap, nothing outside the safe area, Bangla shaped.
7. Tabular digits on anything that counts; numbers formatted for reading.
