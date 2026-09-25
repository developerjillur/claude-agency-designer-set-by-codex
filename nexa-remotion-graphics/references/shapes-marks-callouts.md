# Shapes, callouts and hand-drawn marks

## 1. @remotion/shapes (4.0.528)

Every shape comes as a component `<X />` and a maker `makeX()` returning `{path, width, height, transformOrigin,
instructions}`. The maker is plain data: combine it with any @remotion/paths function.

Component props (all shapes): any SVG `<path>` attribute except `d`, `width`, `height` (set `fill`: the default is
black), `style` (on the `<svg>`, merged with `overflow: visible`), `pathStyle` (on the `<path>`, with
`transform-box: fill-box`, so a rotation turns around the shape's centre), `debug` (draws Bezier handles), `effects`
and `pixelDensity` (GPU effects through HtmlInCanvas), and Sequence props (`from`, `durationInFrames`, `premountFor`
and others).

| Shape | Options (defaults) | Size | Notes |
|---|---|---|---|
| Rect / makeRect | `width`, `height`, `cornerRadius` 0, `edgeRoundness` null | w x h | radius like border-radius; edgeRoundness bulges the sides (squircle-like); not both |
| Circle / makeCircle | `radius` | 2r | starts at the top |
| Ellipse / makeEllipse | `rx`, `ry` | 2rx x 2ry | |
| Triangle / makeTriangle | `length`, `direction` ('right', 'left', 'up', 'down'), `cornerRadius`, `edgeRoundness` | equilateral | origin at the centroid |
| Star / makeStar | `points`, `innerRadius`, `outerRadius`, `cornerRadius`, `edgeRoundness` | 2 x outer | price badges: 12 points, inner 70, outer 90, corner 6 |
| Polygon / makePolygon | `points` (3 or more), `radius`, `cornerRadius`, `edgeRoundness` | 2r | |
| Pie / makePie | `radius`, `progress` (0..1), `closePath` true, `counterClockwise` false, `rotation` 0 (radians) | 2r | 12 o'clock, clockwise; `closePath: false` + stroke = progress ring |
| Arrow / makeArrow | `length` 300, `headWidth` 185, `headLength` 120, `shaftWidth` 80, `direction` 'right', `cornerRadius` 0 | length x headWidth | a filled block arrow; headWidth >= shaftWidth, headLength <= length |
| Callout / makeCallout | `width` 500, `height` 200, `pointerLength` 40, `pointerBaseWidth` 60, `pointerPosition` 0.5, `pointerDirection` 'down', `cornerRadius` 0, `edgeRoundness` null | body plus pointer | the body keeps width x height; the pointer adds its length on its side |
| Heart / makeHeart | `height`, `aspectRatio` 1.1, `bottomRoundnessAdjustment` 0, `depthAdjustment` 0 | height x aspect | 4.0.315 |
| Spark / makeSpark | `width`, `height`, `edgeRoundness` 1, `cornerRadius` 0 | w x h | a four-point sparkle |

Errors: `"cornerRadius" and "edgeRoundness" cannot be specified at the same time`, `"points" should be minimum 3`,
`"headWidth" must be greater than or equal to "shaftWidth"`, `"pointerPosition" must be a number between 0 and 1`,
`"width" must be a positive number`.

Uses: a progress ring (`<Pie closePath={false} fill="none" stroke strokeWidth progress={p}/>`), a donut slice by
slice (one Pie per slice with `rotation` = the sum before it), sparkles (`Spark` popping with an overshoot, rotated
15 to 45 degrees), badges (`Star`), a draw-on card border (`makeRect` path + `DrawnPath`), a mask reveal (a maker's
path as CSS `clip-path: path()`, centred with `centerPath` and sized to the frame diagonal).

## 2. Callouts

The kit's `Callout` measures its text after the fonts load, builds the bubble with `makeCallout` around it, puts the
pointer tip exactly on (x, y), keeps the bubble inside `bounds` (slides the pointer along the edge, flips the side
when there is no room), pops out of the tip (scale 0.55 -> 1 with an overshoot, 16 f) and shrinks back at the end of
its Sequence.

Craft:
- 32 px text (26 inside charts), 460 px wide at most, balanced wrapping; a bold `title` line and a plain line.
- Pointer 26 long and 34 wide; the tip a few px off the point it names (not covering it).
- Light themes: a surface bubble with a soft shadow; dark themes: the accent bubble with on-accent text.
- One callout at a time, each in its own Sequence, 2 to 4 s; stagger several by 20 frames.
- Grow from the pointer tip (`transform-origin` at the tip) so it reads as coming from the thing.

Making your own bubble: `makeCallout({width: textW + 2 * pad, height: textH + 2 * pad, pointerDirection: 'down',
pointerPosition: 0.2, cornerRadius: 20})`, text absolutely placed on the body (the body sits at y = pointerLength for
'up', x = pointerLength for 'left'), and the tip at `(pointerPosition * width, height + pointerLength)` for 'down'.
Keep `pointerPosition` at least `(cornerRadius + pointerBaseWidth / 2) / width` from each end so the pointer never
lands on a rounded corner.

## 3. Hand-drawn marks with perfect-freehand (kit `HandMark`, `Marked`, `HandStroke`)

perfect-freehand 1.2.3 turns a list of points (with optional pressure) into the outline polygon of an inked
stroke: `getStroke(points, options)` -> `[x, y][]`, filled as a path.

Options: `size` (diameter), `thinning` (how much pressure changes width: 0 even, 0.5 inky, negative thicker when
fast), `smoothing` (edge softness), `streamline` (how much the line lags and smooths the input), `easing` (pressure
curve), `simulatePressure` (from speed; off when you give pressure), `start` and `end` (`{taper, cap, easing}`:
taper length in px or true), `last` (true once the stroke is finished: closes the end cap properly).

How the kit draws a mark:
1. Ideal strokes per kind in a w x h box (an ellipse loop of about 383 degrees that starts inside and ends
   outside so the ends cross; a slightly bowed underline; a check as one stroke with two legs; an arrow as a shaft
   and two head strokes).
2. Points about 3 px apart along each stroke (an even pen speed), pushed along the normal by seeded simplex noise
   (`@remotion/noise`, wavelength about 90 px), less at the ends.
3. Pressure from the kit: it lands, stays with a little noise, lifts at the end.
4. Drawing progress p: strokes one after another with a short lift between them; the drawn part of a stroke is cut
   at the exact length with an interpolated last point (the tip moves smoothly between samples); `last` only when a
   stroke is complete.
5. The outline becomes an SVG path by joining edge midpoints with quadratic curves; filled with the mark colour.

Kinds and sizes: circle (pen 7), underline (8), double-underline (7), strike (8), check (11), cross (10), arrow (8),
box (6), highlight (flat ends, 80% of its height, highlight colour at 80%), scribble (6). `rough` scales the wobble
(0 is a ruler), `seed` picks a different hand-made variation, `boil` redraws every n frames after the mark is done
(3 to 5 frames for a sketch look; never in clean corporate styles).

Craft:
- The text lands first; the mark starts 6 to 10 frames later and takes 16 to 24 frames (circles and boxes 24).
- One mark per phrase, at most two per frame. Circles around numbers, underlines under claims, strikes on the old
  way, checks and crosses in lists, arrows from a label to a thing.
- Marker colour: the theme's second accent (red in Vox, amber in studio), highlights in the theme's highlight
  colour behind the text.
- `Marked` measures the phrase after the fonts load (so Bangla and any font are exact); the phrase must fit on one
  line.

## 4. @remotion/rough-notation (4.0.490), the alternative for text

Components: `Highlight` (behind the text), `Underline`, `StrikeThrough`, `CrossedOff`, `Box`, `Bracket`, `Circle` (on
top). They wrap inline text, measure it (holding the first render until a size is known) and draw seeded Rough.js
strokes revealed by `progress` (0..1, required; drive it with a clamped `interpolate`).

Props: `progress`, `color` (default `currentColor`: for Highlight always pass a translucent colour such as
`rgba(255, 221, 64, 0.72)` or it covers the text), `strokeWidth` (Box 7, most others 20), `iterations` (integer >=
1; Highlight and Box 2), `padding` (`{left, right, top, bottom}`; Underline only `top`), `seed` (1; change it every
4 frames for a boil), `roughness` (3 Highlight, 1.5 others), `maxRandomnessOffset` 5, `bowing` 1 (0 for a straight
marker), `disableMultiStroke` (effectively true inside the renderer: pass `false` for the doubled pencil look),
`rtl`, Circle's `box` ('around' scales the ellipse to enclose the box, 'inside' fits it) and curve options,
Bracket's `bracketLeft/Right/Top/Bottom`, and Sequence props.

Name clash: its `Circle` and `Box` collide with @remotion/shapes names; alias on import. The annotated text never
wraps (`white-space: pre`).

When to use which: rough-notation for a rough, sketchy, Rough.js look; the kit's marks for an inked marker look with
pressure and taper, Bangla-safe measuring, and marks that are not attached to text (`HandMark`, `HandStroke`).
