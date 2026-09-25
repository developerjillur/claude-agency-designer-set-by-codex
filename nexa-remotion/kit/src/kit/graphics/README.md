# graphics: charts, diagrams, paths, icons and hand-drawn marks

Data visualisation and drawn graphics for Remotion 4.0.528. Every component reads the theme (`useTheme()`), sizes
itself in px at a 1080 px short side (`unit` from `useStage()`), stays inside the safe area, and is a pure function of
the frame. Import from `./kit/graphics` in a project (from `../kit/graphics` inside the kit).

Shared timing props (most components): `delay` (frames from the start of the enclosing Sequence), `duration`
(frames of the main build), `ease` (a kit curve), and the exit props `exit` (`'none' | 'fade' | 'shrink' |
'undraw'`), `outDuration`, `outAt`. An exit ends on the last frame of the enclosing Sequence unless `outAt` says
otherwise. Charts default to `exit: 'none'` (cut on a settled frame); `Callout` exits by default (it is temporary).
Give other temporary annotations an exit too when they leave before the cut: `Arrow`, `HandMark` and `DrawPath`
take `exit="fade"` or `exit="undraw"` (put them in a Sequence of their own).

Chart rules built in: bars always start at zero, values are labelled on the marks (no legends), one highlight at a
time in the accent with everything else grey, tabular digits, numbers formatted by the kit (not `Intl`), text
laid out from estimates or measured after fonts load, never from a guess that changes between render tabs.

---

## Chart scene

### ChartFrame
A titled chart scene inside the safe area: title, optional subtitle, the chart in the space left, a source line at
the bottom. Charts inside take their size and start frame from it. The header is measured after fonts load, so the
chart gets exactly the room left.

| Prop | Default | |
|---|---|---|
| `title`, `subtitle`, `source` | none | `source` keeps numbers honest: say where they come from ('Example data' for made-up numbers) |
| `align` | `'left'` | `'center'` for symmetric diagrams |
| `titleSize` | 64 (58 in 9:16) | px at 1080 |
| `delay` | 0 | title entrance; the chart inside starts about 10 frames later |
| `exit` | `'none'` | `'fade'` fades the whole scene out at the end |

```tsx
<ChartFrame title="Referrals brought in the most customers" subtitle="New customers by channel, 2025" source="Company CRM, Jan to Dec 2025">
  <BarChart data={data} format={{compact: true}} highlight="Referral" highlightAt={96} />
</ChartFrame>
```
Gotchas: one chart per frame. The title wraps with `text-wrap: balance`; keep it to one sentence that states the
finding ("Referrals brought in the most"), not the topic ("Customer channels").

### Chart size without a frame
A chart outside `ChartFrame` takes `width`/`height` props (px at 1080) or defaults to the safe width and 74% of the
safe height. It renders as a block: put it in `SafeArea` or position it yourself.

---

## Charts

Bad values never break a chart: a value that is not a finite number (NaN, Infinity, an invalid date) is left
out by `BarChart`, `LineChart` and `Sparkline` (the others keep their places), and counts as 0 in `Donut`, `BarRace`
and `Comparison`. Check the data anyway: a missing bar is still a wrong chart.

### BarChart
Vertical or horizontal bars growing from a zero baseline in reading order, values on the bars, nice ticks from
d3-scale, negative values, one highlight.

| Prop | Default | |
|---|---|---|
| `data` | required | `{label, value, color?}[]` |
| `orientation` | `'vertical'` | `'horizontal'` for rankings, long labels, 9:16 |
| `highlight` | none | index, label or a list: accent; the rest grey |
| `highlightAt` | none | frame when the others turn grey (all start in the accent); none: grey from the start |
| `format` | `{}` | `ValueFormat` or a function (see Numbers) |
| `values` | `'land'` | `'land'` (label rises as its bar lands), `'count'` (rides the tip and counts), `'none'` |
| `valuePosition` | `'outside'` | `'inside'` puts it in the bar end when it fits (text colour picked for contrast) |
| `axis` | vertical: on; horizontal: off | gridlines and tick labels |
| `ticks` | 4 | about how many |
| `max`, `min` | from data | pin the range to compare charts; zero is always included |
| `axisLabel` | none | what the numbers are ('USD millions') |
| `sort` | `'none'` | `'desc'`, `'asc'` |
| `duration`, `stagger` | 24 f, theme stagger | per bar, between bars (at 30 fps, scaled) |
| `ease` | theme arrival curve | `curves.outBack` for a playful overshoot |
| `color`, `neutral`, `negativeColor` | accent, theme grey, theme negative | |
| `labelSize`, `valueSize` | from bar count | px at 1080 |
| `barRadius`, `gap`, `maxBar` | theme radius (at most 12), 0.32, 190 / 76 | |
| `exit` | `'none'` | `'fade'`, `'shrink'` (bars sink back, last in first out) |

```tsx
<BarChart orientation="horizontal" sort="desc" data={cities} values="count" highlight="Dhaka" />
<BarChart data={quarters} format={{prefix: '$', suffix: 'M', decimals: 1}} axisLabel="USD millions" />
```
Gotchas: tick labels drop forced decimals (`$1M`, not `$1.0M`) and show zero as `0`. Negative bars are red unless a
highlight is set. Labels wrap to two lines under vertical bars; very long labels belong in a horizontal chart.

### LineChart
Series that draw on left to right (dash technique, per series), an area wash, dots that pop as the line reaches
them, direct labels at the line ends, callouts that open when the line arrives, x values that are categories,
numbers or dates (true spacing for uneven dates).

| Prop | Default | |
|---|---|---|
| `series` or `data` | required | `{name?, points: {x, y}[], color?, dashed?, area?}[]`, or one series' points |
| `curve` | `'smooth'` | monotone (never overshoots the data), `'linear'`, `'step'` |
| `area` | on for one series | a gradient wash under the line |
| `dots` | `'all'` for 12 points or fewer, else `'end'` | `'none'` |
| `zero` | `true` | `false` for prices, temperatures, anything whose shape matters more than size |
| `yTicks`, `xTicks` | 4, 6 | |
| `format`, `xFormat` | `{}`, auto | dates format in UTC ('Jun 14', 'Mar 2026', '2026') |
| `yLabel`, `xLabel` | none | axis captions |
| `endLabel` | one series: `'value'`, several: `'name'` | `'both'`, `'none'`; labels are nudged apart |
| `callouts` | `[]` | `{series?, x, title?, text?, side?}`: opens when the line reaches x |
| `highlight` | none | series index kept in the accent, the rest grey and thinner |
| `duration`, `stagger` | 66 f, 16 f | per series |
| `ease` | `curves.inOut` | |
| `lineWidth`, `tickSize`, `labelSize` | 6, 22, 28 | |
| `exit` | `'none'` | `'undraw'` erases the lines from the start, `'fade'` |

```tsx
<LineChart
  data={readings.map((r) => ({x: new Date(Date.UTC(2026, 5, r.day)), y: r.level}))}
  format={{decimals: 1}} yLabel="metres" curve="linear"
  callouts={[{x: new Date(Date.UTC(2026, 5, 15)), title: 'Peak', text: '5.2 m on 15 June'}]}
/>
```
Gotchas: build dates with `Date.UTC` (formatting and ticks are UTC, so every render machine agrees). A dashed series
(targets, forecasts) is revealed by a moving clip instead of a dash draw. A series with one point shows its dot
and end label only. Callouts whose x is not in the data are skipped. Keep to 4 series or fewer.

### Donut and Pie
Slices sweep clockwise from 12 o'clock; each label arrives as the sweep passes its slice; the centre counts up a total.

| Prop | Default | |
|---|---|---|
| `data` | required | `{label, value, color?}[]` (negative values count as 0) |
| `thickness` | 0.34 (Donut), 1 (Pie) | share of the radius |
| `labels` | `'outside'` | leader lines out along the slice middle; `'inside'` (percent in the slice), `'none'` |
| `show` | `'percent'` | `'value'`, `'both'` |
| `center` | Donut: `'total'`; Pie: none | `{value, label, format}` or `'none'` |
| `centerLabel` | `'Total'` | |
| `highlight` | none | index or label: pulled out, in the accent; the rest in stepped greys |
| `radius` | fits the box and labels | px at 1080 (set it to match two charts) |
| `padAngle`, `cornerRadius`, `startAngle` | 1.2 deg, 6, 0 | |
| `duration`, `ease` | 48 f, in-out | |
| `exit` | `'none'` | `'shrink'` or `'undraw'` sweeps back, `'fade'` |

```tsx
<Donut data={week} highlight="Focused work" format={{suffix: ' h'}} centerLabel="hours" />
<Pie data={budget} labels="inside" radius={230} />
```
Gotchas: five or six slices at most; merge the rest into 'Other'. Percent labels use 1 decimal under 10%. When every
value is 0 the donut shows an empty grey track and a total of 0 (never a made-up share).

### BarRace
The bar chart race: values move between snapshots, bars re-sort as they pass, rank changes glide (a rank averaged
over the last few frames, a pure function of the frame), the scale follows the leader from zero, the period label
sits large in the corner.

| Prop | Default | |
|---|---|---|
| `snapshots` | required | `{label, values: {name: number}}[]` in time order |
| `top` | 8 | bars shown (12 at most) |
| `step`, `hold` | 45 f, 10 f | frames per snapshot, rest at each snapshot |
| `smoothing` | 8 f | frames a rank change takes |
| `highlight`, `colors`, `format`, `periodLabel` | none, palette, `{}`, `true` | |

```tsx
<BarRace snapshots={years} highlight="Lumen" format={{suffix: 'M'}} />
// composition length: barRaceFrames(years.length, 45, 10, delay)
```
Gotchas: in-between values keep the snapshots' decimals. A race shows sizes, so negative values count as 0. With
fewer names than `top` the rows fill the box. Labels can touch for a few frames while two bars swap places. Give each
snapshot at least 1.5 s; a race is read, not watched.

### Sparkline
A small trend line without axes that draws on, with a wash and a dot on the latest value.
Props: `data` (numbers), `width` 280, `height` 80, `color` accent, `area` true, `dot` true, `strokeWidth` 4, `zero`
false, timing (`delay`, `duration` 40 f, `ease`).
```tsx
<Sparkline data={[6.1, 6.8, 6.4, 7.9, 8.8, 9.6, 12.5]} width={420} height={90} delay={20} />
```

### Stat
One big number that counts up (or rolls like an odometer), a caption, and a change pill.

| Prop | Default | |
|---|---|---|
| `value`, `from` | required, 0 | |
| `format`, `prefix`, `suffix` | `{}` | prefix/suffix are shorthands for the format |
| `label` | none | caption under the number |
| `delta`, `deltaFormat`, `deltaLabel`, `lowerIsBetter` | none, `+12.4%` style, none, false | the pill's colour follows good or bad news |
| `size` | 180 | px at 1080 |
| `mode` | `'count'` | `'roll'` (each digit rolls, right-hand digits spin more), `'none'` |
| `duration`, `ease` | 42 f, out-cubic | |
| `align`, `color` | `'left'`, text | |

```tsx
<Stat value={12480} label="new customers this month" delta={18.2} deltaLabel="vs May" />
<Stat value={1234567} format={{grouping: 'south-asian', digits: 'bengali', prefix: '৳'}} label="মোট বিক্রি" mode="roll" />
```
Gotchas: the final number's width is reserved (the count never shifts the layout). If the in-between values would
be read as facts (years, prices), use `mode="none"` or `'roll'`.

### ProgressRing and ProgressBar
A share filling from zero with the number counting in step.
ProgressRing: `value` (0 to 1, or with `max`), `size` 300, `thickness` 9% of size, `label` (`'percent'`, `'value'`,
`'none'` or a node), `sublabel`, `color`, `track`, `format`, timing (42 f, out-cubic).
ProgressBar: `value`, `max`, `width` 760, `thickness` 22, `label`, `showValue` (`'percent'`, `'value'`, `'none'`),
`segments` (steps of a process), `color`, `track`, timing.
```tsx
<ProgressRing value={0.72} sublabel="of the goal" />
<ProgressBar value={3} max={5} segments={5} label="Step 3 of 5: shipping" showValue="none" />
```

### Comparison
A against B. `'bars'`: two big numbers with bars on one shared scale from zero (side by side, stacked in 9:16);
`'share'`: one bar split into the two parts of a whole, each part counting as the wipe crosses it.
Props: `a`, `b` (`{label, value, color?, note?}`), `format`, `mode` `'bars'`, `winner` `'auto'` (the larger, or the
smaller with `lowerIsBetter`), `vs` `'vs'`, `layout` `'auto'`, `width`/`height`, `numberSize`, timing.
```tsx
<Comparison a={{label: 'Old checkout', value: 94}} b={{label: 'New checkout', value: 38}} format={{suffix: ' s'}} lowerIsBetter />
```

---

## Diagrams

### Timeline
A line that draws through time; each event arrives when the line reaches it. Horizontal (events alternate above and
below when close) or vertical (default in 9:16). Even spacing, or true to time when every event has `at` (when an
`at` is missing, or every event shares one date, the events are spaced evenly).
Props: `events` (`{label, title, text?, at?}`), `orientation` `'auto'`, `highlight`, `spacing`, `alternate` (auto),
`arrow` true, `duration` (20 f per event, at least 50), `ease` in-out, `lineWidth` 5, `titleSize` 36 (44 vertical),
`labelSize` 28 (30), `textSize` 26 (30).
```tsx
<Timeline events={[{label: '2019', title: 'Founded', at: 2019}, {label: '2026', title: '1M users', at: 2026}]} highlight={1} />
```

### FlowDiagram
Boxes and connectors choreographed as a flow: a node arrives, its connector draws to the next node, that node
arrives when the connector gets there. Nodes by `col`/`row` (fractions allowed), by `x`/`y` (share of the box), or
laid out in layers from the edges.

| Prop | Default | |
|---|---|---|
| `nodes` | required | `{id, label, sub?, icon?, col?, row?, x?, y?, tone?}`; `tone: 'accent'` is a solid box (one at most), `'outline'` a ruled one |
| `edges` | required | `{from, to, label?, dashed?}` |
| `direction` | `'auto'` | `'right'`, `'down'` (auto: down in 9:16) |
| `route` | `'curve'` | `'elbow'` (right angles with rounded corners), `'straight'`; back edges run round outside the nodes between their ends |
| `highlight` | `[]` | node ids ringed in the accent; an edge between two highlighted nodes turns accent |
| `pulse` | false | dots keep travelling along drawn connectors |
| `nodeWidth`, `nodeHeight`, `labelSize` | from the grid, 30 | |
| `nodeDuration`, `edgeDuration`, `stagger` | 14, 18, 8 f | |

```tsx
<FlowDiagram
  nodes={[{id: 'a', label: 'Order', icon: 'cart'}, {id: 'b', label: 'Payment', icon: 'money'}, {id: 'c', label: 'Delivered', icon: 'home', tone: 'accent'}]}
  edges={[{from: 'a', to: 'b'}, {from: 'b', to: 'c', label: 'paid'}]}
  highlight={['a', 'b', 'c']}
/>
```

### OrgChart
A tree from parent links, top down, elbow connectors: leaves spread evenly, each parent centred over its children.
Props: `people` (`{id, label, sub?, parent?, icon?, tone?}`) plus FlowDiagram's sizing, highlight and timing props.

---

## Paths

### SvgLayer
A full-frame `<svg>` whose coordinates are frame pixels. Put DrawnPath, ArrowPath, PathFollow, MorphPath and
HandStroke inside it to lay drawings over a scene. Stroke widths inside are frame px: multiply by `unit`.

### DrawnPath and DrawPath
Draw any SVG path on. Every subpath gets its own dash, so multi-part drawings draw correctly.
DrawnPath (inside an `<svg>`): `d`, timing (`progress` or `delay`/`duration` 30 f/`ease` in-out), `mode`
(`'sequence'` a pen, one subpath after another by length; `'together'`; `'stagger'`), `reverse`, `stroke` (text),
`strokeWidth` 4, `linecap`/`linejoin` round, `dash` (a dash pattern: drawn by cutting the path), `fill` (fades in
from `fillFrom` 0.75 of the stroke), `fillOpacity`, `opacity`, exit `'undraw'`/`'fade'`.
DrawPath: the same as a sized block; `viewBox` (default: the path's box plus stroke room), `width`/`height` in px at
1080, `style` to position it.
```tsx
<DrawPath d={logoOutline} width={600} strokeWidth={6} stroke={t.colors.text} fill={t.colors.accent} duration={50} />
```
Gotchas: nothing renders at progress 0 (a round cap would leave a dot) and the stroke is solid at 1 (no seam).
Use `dash` for dotted routes; a dash pattern cannot also be the draw-on dash.

### PathFollow
An object riding a path, turned to the direction of travel (the heading is measured across a short window, so
corners turn smoothly and the end never returns null). Inside an `<svg>`.
Props: `d`, timing (ease in-out), `rotate` true, `angleOffset` (90 when the artwork points up), `trail` (`'none'`,
`'solid'`, `'dashed'`), `trailColor`, `trailWidth`, `trailDash`, `scaleIn`/`scaleOut` (share of the trip), children
drawn around (0, 0) pointing right. An empty `d` renders nothing (the path helpers return 0 or the origin for it).
```tsx
<SvgLayer>
  <PathFollow d={route} delay={20} duration={90} trail="dashed" scaleIn={0.06}>
    <path d="M26 0L-14 -16L-8 0L-14 16Z" fill={t.colors.accent} />
  </PathFollow>
</SvgLayer>
```

### MorphPath and Morph
Shapes that morph through a list, each held then morphed into the next, with the fill colour moving along.
Props: `paths`, `colors` (one per shape) or `fill`, `stroke`, `strokeWidth`, `mode` (`'points'` default: resampled
outlines lined up, morphs any closed shapes; `'native'`: @remotion/paths `interpolatePath`), `frames` (the frame each
shape is fully shown) or `delay`/`hold` 18 f/`move` 24 f, `ease` in-out. Morph adds `viewBox`, `width`, `height`.
Helpers: `morphAt(frame, frames, paths, ease, mode)` (the 4.0.528 stand-in for `interpolatePaths`, which is
4.0.529), `morphBetween(a, b, t, mode)`, `morphSchedule(n, delay, hold, move)`.
```tsx
<MorphPath paths={[circlePath(0, 0, 96), starPath(0, 0, 5, 116, 50)]} colors={[t.colors.accent, t.colors.accent2]} delay={20} />
```
Gotchas: 'points' mode pairs subpaths when both shapes have the same count; otherwise it falls back to
`interpolatePath`. The exact source strings are shown at rest (no resampling artefacts on held frames).

### ArrowPath and Arrow
A straight or bent arrow that draws on, with an open or filled head that rides the tip and turns with it.
ArrowPath (inside an `<svg>`): `from`, `to` (or `d`), `bend` (0 straight, 0.2 to 0.35 a friendly arc, negative the
other way), `head` `'open'`, `tail` `'none'`, `headSize` 4.5 x stroke, `headAngle` 30, `gap` (stay clear of both
ends), `color`, `strokeWidth` 5, `dash`, timing (22 f, out-cubic), exit `'undraw'`/`'fade'`.
Arrow: the same over the whole frame; `from`/`to` in frame pixels, sizes in px at 1080 (`strokeWidth` 6).
```tsx
<Arrow from={[width * 0.2, height * 0.8]} to={[target.x, target.y]} bend={-0.3} gap={16} head="filled" />
```

### Path helpers (paths.ts)
`pathLength(d)` cached; `subpathsOf(d)`; `pointOnPath(d, len)` (clamped, never null); `pathPose(d, t)`
({x, y, angle}); `dashFor(len, p)`; `subProgress(lengths, p, mode)`; `vertexLengths(d)`; `resamplePath(d, n)`;
`circlePath`, `roundedRectPath`, `starPath`, `polyPath`, `smoothPath(points, tension, closed)` (Catmull-Rom through
the points), `bendPath(a, b, bend)`.

---

## Hand-drawn marks (perfect-freehand)

### HandMark
A mark in a box of its own: `'circle'` (a loop with crossing ends), `'underline'`, `'double-underline'`, `'strike'`,
`'check'`, `'cross'`, `'arrow'` (with `direction`), `'box'`, `'highlight'` (a flat marker swipe), `'scribble'`.
Props: `kind`, `width` 320, `height` (200 for shapes, 160 arrows, 40 lines), `color` (accent2; highlight uses the
theme highlight), `size` (pen width), `rough` 1 (wobble; 0 a steady hand), `seed` (a different hand-made variation),
`boil` (redraw every n frames once drawn: 3 to 5 is a cartoon boil), `direction`, timing (16 to 24 f, in-out), exit.
```tsx
<HandMark kind="check" width={150} height={130} delay={30} style={{position: 'absolute', left: 900, top: 400}} />
```

### Marked
Words with a mark around, under, through or behind them, measured after fonts load:
`<Marked kind="circle">42%</Marked>`. Kinds: circle, underline, double-underline, strike, box, highlight (drawn behind
the text), cross, scribble. Props: `kind` `'underline'`, `pad`, and HandMark's colour, pen and timing props.
Gotchas: one short phrase on one line (the wrapper does not wrap). Works with Bangla (the box is measured, never
split into letters).

### HandStroke
Any point list drawn with a pen inside an `<svg>` (a signature, a sketched route): `points`, `size` 8, `thinning`,
`taper`, `flat`, `rough`, `seed`, `color`, timing. Helpers: `handStrokes(kind, w, h, seed)` and `penPaths(strokes,
p, style)` build the geometry for custom marks.

---

## Callout
A speech-bubble label built with `makeCallout` around its measured text. The pointer tip lands exactly on (`x`, `y`)
in px of the positioned parent (frame px on a full-frame layer); the bubble stays inside `bounds` (default the safe
area) by sliding the pointer along its edge and flipping sides when there is no room.
Props: `x`, `y`, `side` `'top'` (`'bottom'`, `'left'`, `'right'`, `'auto'`), `title`, `text` or children,
`maxWidth` 460, `fontSize` 32, `tone` (surface on light themes, accent on dark; `'ink'`), `fill`, `color`,
`pointerLength` 26, `pointerWidth` 34, `radius`, `bounds`, `delay`, `shadow`, `align`, exit `'shrink'` (at the end
of its Sequence).
```tsx
<Sequence from={40} durationInFrames={90} layout="none">
  <Callout x={point.x} y={point.y} side="right" title="Live balance" text="Updates the second money moves" />
</Sequence>
```
Gotchas: the text is measured after the fonts load (the render waits), and the bubble is drawn to the widest
line while the text keeps its natural, balanced wrapping (re-flowing it into a narrower box would break it
differently). Put each callout in its own Sequence so its exit lands where you want it.

---

## Icons
49 stroke icons drawn for this kit on a 24 grid (2 px strokes, round caps), each made of strokes that draw on in a
hand's order: check, x, arrow-right, arrow-left, arrow-up, arrow-down, trend, play, pause, star, heart, bolt, globe,
chart-up, chart-down, chart-bar, user, users, lock, bell, cart, clock, pin, mail, phone, search, plus, minus, home,
settings, camera, cloud, code, file, money, trophy, rocket, leaf, shield, spark, calendar, chat, bulb, target, eye,
download, link, flag, gift.

### Icon
Props: `name`, `size` 96 (px at 1080), `color` (text), `strokeWidth` 2 (on the 24 grid), `draw` true, `mode`
`'sequence'`, timing (26 f), exit (`'undraw'` erases it).
### IconBadge
An icon in a tinted disc or tile that pops, then draws: `name`, `size` 120, `shape` `'circle'`/`'tile'`, `tint`
(accent), `solid` (a filled disc with the on-accent icon), plus Icon's props.
```tsx
<IconBadge name="rocket" size={140} delay={10} />
```
`ICONS[name]` is the path data (24 grid) for your own SVGs; `ICON_NAMES` lists them.

---

## Numbers (numbers.ts)
`formatValue(value, ValueFormat)`: `decimals` (default: the value's own, up to 3), `prefix`, `suffix`, `compact`
(1.2K, 3.4M; with south-asian grouping 1.2L, 3.4Cr), `units`, `grouping` (`'intl'` 1,234,567; `'south-asian'`
12,34,567; `'none'`), `separator`, `point`, `digits` (`'latin'`, `'bengali'` ০-৯, `'devanagari'`), `sign`
(`'always'` for deltas), `minus` (default U+2212). `tickFormat(format)` for axes, `countValue(from, to, p, decimals)`
for counters, `decimalsFor`, `localDigits`, `formatChartDate(date, style)` (UTC).

## Colours (color.ts)
`mixColor(a, b, t)`, `withOpacity(c, a)`, `contrastRatio(a, b)`, `textColorOn(fill)`, `gridOf(theme)`,
`neutralOf(theme)`, `seriesColors(theme, n, highlight?)`.

## Building your own chart
`useChartBox(width, height, delay)` (size and start from a ChartFrame or the safe area), `ChartRoot` (a sized box
with an SVG in the same px-at-1080 coordinates behind HTML labels), `ChartLabel` (an HTML label at chart
coordinates with an anchor), `useChartType()` (tick, label and value text styles), `estimateLabelWidth`,
`breakLabelLines`, `useGraphicExit`, `frameAtProgress(target, start, duration, ease)` (when an eased build reaches a
point: time a dot to the moment a line reaches it), `GRAPHIC_TIMING` / `buildFrames(key, fps)` (house lengths),
`useMeasuredSize(ref, label, {lines})` (a text box's size, and with `lines` its widest line; it holds the render
until Remotion's font handles are gone, then re-measures every frame).

Measuring gotcha (4.0.528): `@remotion/google-fonts` fetches a font file first and adds the loaded FontFace to
`document.fonts` only afterwards, so `document.fonts.ready` can resolve before a kit font exists and a first frame
would measure the fallback font. `useMeasuredSize` also waits until no pending `delayRender` handle is a font load.
Use it (or `loadFont(...).waitUntilDone()`) for any text you measure yourself.

## Demos
`src/demos/graphics.tsx`: DemoGraphicsBars, BarsHorizontal, BarsNegative, Bangla, Race, Line, LineUneven,
LineStep, Donut, Stats, Progress, Compare, Flow, FlowGrid, Org, Timeline, Vertical (1080 x 1920 bars),
VerticalTimeline (1080 x 1920), Paths, Hand, MarksVariants, Icons, Callout, BarsInside. Run
`nrk.py demos --module graphics`.
