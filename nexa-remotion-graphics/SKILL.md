---
name: nexa-remotion-graphics
description: "Data visualisation and drawn graphics for Remotion videos: bar charts (vertical, horizontal, negative, highlighted), line and area charts with callouts and dates, donut and pie charts, bar chart races, big-number counters and odometers, progress rings and bars, A-versus-B comparisons, sparklines, timelines, flow diagrams and org charts, SVG paths that draw on, objects that follow a path, shape morphs, arrows, hand-drawn circles, underlines, checks and marker highlights, speech-bubble callouts and 49 animated stroke icons, all theme-aware and honest with numbers. Use it for any chart, graph, diagram, infographic, stat or annotation in a video, Banglish included ('chart animation banao', 'graph ta animate koro', 'number count up koro', 'arrow diye dekhao'). Part of the nexa-remotion family."
---

# Graphics for Remotion: charts, diagrams, paths, icons and marks

The kit's `graphics` module turns numbers and ideas into drawn, timed pictures: charts that build in reading order and
label their own values, diagrams whose connectors draw from one box to the next, paths and icons that draw
themselves on, and hand-made marks that point at what matters. Part of the nexa-remotion family (the director skill
is `nexa-remotion`; the kit lives in `~/.claude/skills/nexa-remotion/kit`, and a project made with `nrk.py new`
imports these parts from `./kit/graphics`).

## Fast path

1. **Find the one sentence.** A chart scene says one thing ("Referrals brought the most customers"). That sentence
   is the `ChartFrame` title; the data backs it. Check the sentence against the numbers (48% is "nearly half", not
   "more than half"). Numbers come from the brief or a named source; made-up numbers are labelled 'Example data'.
2. **Pick the form** (see the table in Craft rules): compare categories with `BarChart`, change over time with
   `LineChart`, parts of a whole with `Donut` (6 slices at most) or `Comparison mode="share"`, one number with `Stat`,
   ranks over time with `BarRace`, steps with `FlowDiagram` or `Timeline`.
3. **Write the scene**: `<ChartFrame title subtitle source>` around one chart, data as plain props, a `format` for
   the numbers, `highlight` on the one item the sentence is about. The frame gives the chart its size and start.
4. **Time it to the voice**: put the scene in a `Sequence` that starts on the word that introduces the data; set
   `highlightAt` (bars) or a `callouts` entry (lines) to land on the word that names the finding. Give a chart at
   least 4 s on screen, and hold the finished chart 1.5 s or more before the cut.
5. **Annotate if needed**: `Marked` circles or underlines a word, `Arrow` points from a label to a thing,
   `Callout` names a point. One annotation at a time.
6. **Check**: `nrk.py stills PROJECT` (look at the build and the last frame), then a full-size still of the
   settled chart: labels inside the safe area, nothing overlapping, the highlight obvious at a glance.

## Components (from `./kit/graphics`)

| Component | Use it for | Key props |
|---|---|---|
| `ChartFrame` | a titled chart scene in the safe area | `title`, `subtitle`, `source`, `align`, `delay`, `exit` |
| `BarChart` | comparing categories, rankings, gains and losses | `data`, `orientation`, `highlight`, `highlightAt`, `format`, `values`, `sort`, `axis`, `max` |
| `LineChart` | change over time, several series, uneven dates | `series`/`data`, `curve`, `area`, `callouts`, `highlight`, `zero`, `endLabel`, `yLabel` |
| `Donut`, `Pie` | parts of a whole | `data`, `highlight`, `labels`, `show`, `center`, `radius` |
| `BarRace` | ranks changing over years | `snapshots`, `top`, `step`, `highlight`; length from `barRaceFrames()` |
| `Stat` | one big number, a count-up or an odometer | `value`, `format`, `label`, `delta`, `mode`, `size` |
| `Sparkline` | a small trend beside a number | `data`, `width`, `height` |
| `ProgressRing`, `ProgressBar` | a share of a goal, steps of a process | `value`, `max`, `label`/`sublabel`, `segments` |
| `Comparison` | A against B, or a split of a whole | `a`, `b`, `mode`, `lowerIsBetter`, `format` |
| `Timeline` | events in order, even or true to time | `events` (`at` for true spacing), `orientation`, `highlight` |
| `FlowDiagram`, `OrgChart` | processes, pipelines, trees | `nodes`, `edges`, `route`, `highlight`, `pulse`; `people` |
| `DrawPath`, `DrawnPath`, `SvgLayer` | any SVG drawing that draws on | `d`, `mode`, `fill`, `dash`, timing |
| `PathFollow` | an object travelling a route | `d`, `trail`, `rotate`, `scaleIn` |
| `Morph`, `MorphPath` | one shape becoming another | `paths`, `colors`, `hold`, `move`, `mode` |
| `Arrow`, `ArrowPath` | pointing from here to there | `from`, `to`, `bend`, `head`, `tail`, `gap` |
| `HandMark`, `Marked`, `HandStroke` | hand-drawn circles, underlines, checks, crosses, arrows, highlights | `kind`, `color`, `seed`, `boil` |
| `Callout` | a bubble naming a point | `x`, `y`, `side`, `title`, `text` |
| `Icon`, `IconBadge` | 49 stroke icons that draw on | `name`, `size`, `color`, `delay` |

Helpers: `formatValue` (grouping, compact, Bangla digits), `seriesColors`, `pathPose`, `morphAt`, `smoothPath`,
`bendPath`, `circlePath`, `starPath`, `useChartBox`, `ChartRoot`, `ChartLabel` (build a custom chart). Full props and
defaults: `kit/src/kit/graphics/README.md`.

## Craft rules

**Honesty (never broken)**
- Bars start at zero, always (`BarChart` enforces it); a bar's length is its value. Lines may leave zero out
  (`zero={false}`) only when the shape is the point, and the axis says so.
- Same scale for things compared side by side: pass the same `max` to both charts.
- Label values on the marks, not in a legend. Round for reading (1.2M, 38%), keep the precision the source has.
- A count shows its in-between numbers as if they were facts: for years, prices or anything where 1996 and 1997
  mean something, use `mode="none"` or an odometer.
- Say where numbers come from (`source`). Invented numbers are marked 'Example data'.

**Which form**

| The sentence is about | Use | Not |
|---|---|---|
| which is biggest, a ranking | `BarChart` horizontal, `sort="desc"` | a pie |
| change over time | `LineChart` (a few points: vertical bars) | a donut |
| part of a whole, 2 parts | `Comparison mode="share"` or `ProgressRing` | a 2-slice pie |
| part of a whole, 3 to 6 parts | `Donut` with a highlight | 7+ slices (merge to Other) |
| one number | `Stat` (with `delta`, a `Sparkline`) | a chart with one bar |
| ranks moving over time | `BarRace` | twelve line series |
| a process, a pipeline | `FlowDiagram` | a bulleted list |
| dates and milestones | `Timeline` with `at` | even spacing when gaps matter |

**Colour and emphasis**
- One accent with a budget: the highlighted bar, slice, series or node. Everything else is the theme's grey
  (`neutralOf`). Without a highlight, use the accent for all bars of one series.
- `highlightAt` turns the others grey on the word of the finding: the chart builds in full colour, then focuses.
- Sequential or series colours come from `seriesColors(theme, n)`; never rainbow palettes.

**Type**
- Value labels 36 to 44 px bold, category labels 26 to 30 px, ticks 22 px (px at 1080). Tabular digits on every
  changing number (the kit sets it). Titles 58 to 64 px, one sentence.
- Bangla labels and Bangla digits work: `format={{digits: 'bengali', grouping: 'south-asian'}}` gives ১২,৩৪,৫৬৭.

**Timing (30 fps; scale with `at30`)**
- Axis and gridlines first (14 f), then bars 24 f each with a 4 to 6 f stagger in reading order; values land as
  bars settle. Total build for 5 bars about 1.5 s.
- A line draws in 50 to 80 f with an in-out curve; dots pop as it reaches them; callouts open 2 f after.
- Counters 40 to 45 f ease-out (fast then settling); donut sweeps 45 to 50 f.
- Connectors 18 f, nodes 14 f; the next node arrives when its connector gets there.
- Hold the settled chart at least 1.5 s (reading), 45 f for a single stat. A chart scene lasts 4 s or more.
- One focal move at a time: do not start the highlight while bars are still growing.

**Layout**
- Everything inside the safe area; `ChartFrame` does it. In 9:16, prefer horizontal bars and vertical timelines,
  keep content in the safe box (y 270 to 1248 on 1080 x 1920) and let the bottom stay clear for platform UI.
- Leave the chart room: 5 to 8 bars, 12 points per line, 6 slices, 8 to 10 race bars, 6 to 8 flow nodes per frame.

**Paths, marks and icons**
- Draw strokes with round caps over 20 to 40 f, in-out; a multi-part drawing draws in `'sequence'` like a pen.
- Hand marks: one per phrase, drawn 6 to 10 f after the text lands; circles 24 f, underlines 16 f. `boil` only in
  sketch styles.
- Arrows `gap` 12 to 20 px from what they point at, bend 0.2 to 0.35 for a friendly arc.
- Icons: 2 px on the 24 grid reads at 64 to 140 px; badges for lists and flow nodes.

## Recipes

**A finding in bars, focused on the word**
```tsx
// the voice says "referrals" at frame 240 and "the most" at frame 336
<Sequence from={240} durationInFrames={180}>
  <ChartFrame title="Referrals brought in the most new customers" subtitle="New customers by channel, 2025" source="Company CRM">
    <BarChart data={channels} format={{compact: true}} highlight="Referral" highlightAt={336 - 240} />
  </ChartFrame>
</Sequence>
```

**A line with a moment called out**
```tsx
<ChartFrame title="The new plan overtook the old one in June" subtitle="Monthly sign-ups" source="Example data">
  <LineChart series={[{name: 'Classic', points: classic}, {name: 'Plus', points: plus}]} highlight={1} dots="end"
    callouts={[{series: 1, x: 'Jun', title: 'June', text: 'Plus passes Classic'}]} />
</ChartFrame>
```

**Three numbers in a row (a stat slide)**
```tsx
<SafeArea justify="center">
  <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', width: '100%'}}>
    <Stat value={12480} label="new customers" delta={18.2} size={124} />
    <Stat value={4.2} format={{prefix: '$', suffix: 'M', decimals: 1}} label="revenue" mode="roll" delay={16} size={124} />
    <Stat value={98.2} suffix="%" label="uptime" delay={32} size={124} />
  </div>
</SafeArea>
```

**A route with a plane, over a map or illustration**
```tsx
const route = smoothPath([[300, 800], [700, 520], [1200, 640], [1600, 300]]);
<SvgLayer>
  <path d={route} fill="none" stroke={t.colors.faint} strokeWidth={4} strokeDasharray="2 14" strokeLinecap="round" />
  <PathFollow d={route} delay={10} duration={90} trail="solid" trailColor={t.colors.accent} scaleIn={0.06}>
    <path d="M26 0L-14 -16L-8 0L-14 16Z" fill={t.colors.accent} />
  </PathFollow>
</SvgLayer>
```

**Circle the number, then point at it**
```tsx
<div style={headline}>Sales grew <Marked kind="circle" delay={16}>42%</Marked> in one quarter</div>
<Sequence from={40} layout="none"><Arrow from={[1500, 820]} to={[1180, 300]} bend={0.3} gap={18} /></Sequence>
```

**A pipeline that flows**
```tsx
<ChartFrame title="What runs on every merge">
  <FlowDiagram nodes={steps} edges={links} route="elbow" highlight={['build', 'deploy']} pulse />
</ChartFrame>
```

## Remotion 4.0.528 facts and traps

- `getPointAtLength` and `getTangentAtLength` return `null` past the path's end on 4.0.528 (the docs say v5).
  Floating error at the very end is enough to crash a destructure: use `pointOnPath` / `pathPose` (clamped, never
  null) or clamp and check yourself.
- `interpolatePaths()` is 4.0.529: not available. Use `morphAt(frame, frames, paths, ease)` for multi-keyframe
  morphs; `interpolatePath(t, a, b)` exists for two shapes.
- `evolvePath(p, d)` re-parses the path each call and applies one dash to the whole path; Chrome restarts dash
  patterns per subpath, so a multi-part drawing drawn with one dash animates all parts at once. `DrawnPath` gives
  each subpath its own dash and caches lengths.
- A round cap on a zero-length dash draws a dot: hide a stroke at progress 0 (the kit does).
- `evolvePath` owns `strokeDasharray`, so a dashed line cannot also draw on by dash: cut it (`cutPath`, the kit's
  `dash` prop) or reveal it with a clip.
- `@remotion/shapes` makers: `makeCallout` defaults 500 x 200, pointer 40 long and 60 wide; `cornerRadius` and
  `edgeRoundness` cannot be combined; `makePie` starts at 12 o'clock, `closePath: false` gives an open arc.
- d3 in Remotion: use `d3-scale` and `d3-shape` as pure functions and render React SVG. Never let d3 mutate the DOM
  (the official d3 example does; it only works because it re-runs every frame). Use `scaleUtc` and `Date.UTC` for
  dates so every render machine agrees on the day.
- Measuring text: charts lay out from estimates, never from the DOM. `Callout`, `Marked` and `ChartFrame` measure
  inside a `delayRender`. `document.fonts.ready` is not enough on 4.0.528: `@remotion/google-fonts` fetches the file
  and adds the FontFace only when loaded, so `ready` can resolve before the font exists; the kit's
  `useMeasuredSize` also waits for Remotion's pending font handles and re-measures every frame.
- rough-notation (`@remotion/rough-notation`, 4.0.490) is the alternative for text annotations; its `Highlight`
  defaults to `currentColor` (covers the text) and `disableMultiStroke` is effectively on. The kit's `Marked` uses
  perfect-freehand instead: pressure-shaped strokes, seeded wobble, measured once the fonts load (Bangla-safe).
- Clamp every `interpolate()`; every chart value here is a pure function of the frame (the bar race's glide is an
  average over earlier frames' ranks, computed, not stored).

## References

- `references/charts.md`: chart design rules, every chart type step by step, d3-scale and d3-shape for custom
  charts, number formatting and Bangla numerals, timing budgets, 9:16 layouts.
- `references/paths.md`: @remotion/paths for 4.0.528 (every function with its traps), draw-on techniques compared,
  motion along a path, morphing, warps, text outlines.
- `references/shapes-marks-callouts.md`: @remotion/shapes makers and components, callouts, rough-notation,
  perfect-freehand options and hand-drawn craft.
- `references/diagrams.md`: flows, timelines, org charts and trees: layout, routing, choreography, recipes.
- `references/icons.md`: the 49 icons, design rules for stroke icons, adding your own, icon motion.
- `references/traps.md`: errors and fixes, determinism, performance, version gates, the pre-render checklist.
