# Paths: drawing on, travelling along, morphing, warping (Remotion 4.0.528)

The SVG path pipeline: make a `d` string (a design tool, `@remotion/shapes` makers, the kit's builders, glyph
outlines) -> normalise and place it -> animate it (draw on, cut, follow, morph, warp) -> render it as a `<path>`, a
CSS `clip-path: path()` or an SVG `<clipPath>`.

## 1. @remotion/paths on 4.0.528 (pure functions, work in Node too)

| Function | Returns | Notes and traps |
|---|---|---|
| `getLength(d)` | number | parses the string every call: cache it (the kit's `pathLength` does) |
| `getPointAtLength(d, len)` | `{x, y}` or `null` | **null when len > total length, already on 4.0.528** (the docs say from v5). Floating error at the end is enough. Clamp and handle null, or use the kit's `pointOnPath` |
| `getTangentAtLength(d, len)` | unit `{x, y}` or `null` | same null rule; angle = `Math.atan2(y, x)`; at a corner the tangent jumps (the kit's `pathPose` measures across a short window instead) |
| `getInstructionIndexAtLength(d, len)` | `{index, lengthIntoInstruction}` | throws past the end |
| `evolvePath(p, d)` | `{strokeDasharray, strokeDashoffset}` | draw-on; at p = 0 it uses 1.5 x length to avoid a leftover dot; p > 1 starts erasing, p < 0 draws from the end; needs a stroke, and owns the dash array |
| `cutPath(d, len)` | string | the part from the start to len (reduced to M, L, C, Z); 0 gives only the M; past the end the whole path |
| `interpolatePath(t, a, b)` | string | morph of two paths; t 0 and 1 give the inputs verbatim; values outside 0..1 extrapolate; best with single closed subpaths of similar winding |
| `interpolatePaths(...)` | | **4.0.529: not on 4.0.528.** Use the kit's `morphAt` |
| `getBoundingBox(d)` | `{x1, y1, x2, y2, width, height, viewBox}` | includes curve extremes; `viewBox` is ready for `<svg>` |
| `resetPath(d)` | string | moves the box's top-left to 0,0 |
| `centerPath(d, {x, y}?)` | string | moves the box centre to a point (4.0.486) |
| `translatePath(d, x, y)` | string | |
| `scalePath(d, sx, sy)` | string | scales around the box's TOP-LEFT; for centre scaling centre at 0,0, scale, move back |
| `warpPath(d, fn, {interpolationThreshold?})` | string | subdivides then maps every point through `fn({x, y})`; output is large: memoise |
| `getSubpaths(d)` | string[] | splits at each M (relative m made absolute) |
| `reversePath(d)` | string | draws from the other end |
| `normalizePath(d)` | string | relative to absolute |
| `parsePath(d)`, `serializeInstructions(ins)`, `reduceInstructions(ins)` | | typed instructions; reduced gives only M, L, C, Z |
| `extendViewBox(vb, scale)` | string | usually `overflow: visible` on the svg is simpler |
| `PathInternals.debugPath(d)` | `{d, color}[]` | squares at every vertex, for debugging morphs |

Every function throws on malformed data (a missing M, a CSS `path("...")` string with quotes).

## 2. Drawing on: four techniques

| Technique | How | Good for | Watch |
|---|---|---|---|
| Dash per subpath (kit `DrawnPath`) | each subpath: `strokeDasharray = "drawn gap"`, hidden at 0, solid at 1 | icons, logos, illustrations with several parts, anything | nothing; lengths cached |
| `evolvePath(p, d)` | spread onto a `<path>` | one continuous stroke | one dash over several subpaths draws them all at once, because Chrome restarts the dash for every subpath; re-parses each frame |
| `pathLength={1}` + `strokeDasharray={1}` + `strokeDashoffset={1 - p}` | the browser scales the dash | quick one-offs without JS lengths | same subpath caveat; at p = 0 hide it (round caps leave a dot) |
| Cut (`cutPath(d, len * p)`) | render only the drawn part | dashed or dotted strokes (the dash pattern stays put) | re-cuts every frame |
| Clip reveal | a clip rect grows with the head | area fills, dashed series, text | reveals by x, not along the path |

Style: `strokeLinecap="round"`, `strokeLinejoin="round"`, in-out easing over 20 to 40 frames per stroke, 4 to 6 frames
between strokes; draw the outline first, then fade the fill in (a separate path, so the fill never waits for the
dash). For a logo: outline 30 to 45 f, fill 10 to 14 f after 75% of the outline, then the wordmark.

```tsx
<DrawPath d={logo} width={520} strokeWidth={5} stroke={t.colors.text} fill={t.colors.accent} mode="sequence" duration={45} />
<DrawnPath d={route} dash="2 16" strokeWidth={5} duration={60} />   // a dotted route that grows
```

Exits: `exit="undraw"` erases from the start (the stroke leaves the way it came); `reverse` draws each subpath from
its end.

## 3. Travelling along a path

```ts
const pose = pathPose(route, t);   // {x, y, angle}: clamped, never null, heading averaged across 4 units
<g transform={`translate(${pose.x} ${pose.y}) rotate(${pose.angle})`}>{plane}</g>
```
- `PathFollow` does this with a trail (`'solid'` dash, `'dashed'` cut) and scale in/out at the ends.
- Artwork points right (+x) at rest; `angleOffset={90}` for artwork that points up.
- Ease in-out for vehicles; linear for conveyor belts and data packets that loop.
- A packet that loops: `t = ((frame - start) % period) / period`, opacity `sin(pi * t)` so it fades at both ends
  (the flow diagram's `pulse`).
- Arcs between two points: `bendPath([x1, y1], [x2, y2], 0.3)` (a quadratic curve off the chord's middle); routes
  through several points: `smoothPath(points)` (Catmull-Rom through every point).
- Map routes: draw the route twice, a wide casing in the background colour under a narrower coloured line.

## 4. Morphing

- Two shapes: `interpolatePath(t, a, b)` (native) or the kit's `morphBetween(a, b, t, 'points')`.
- 'points' mode (kit default): both outlines are resampled to 240 points at equal spacing, the second is rotated
  (and reversed if its winding differs) to line up with the first, then points are blended. It morphs any two single
  closed outlines cleanly (circle to star to heart) without the twisting and crossing that mismatched start points
  cause. Shapes with the same number of subpaths are paired subpath by subpath; different counts fall back to
  `interpolatePath`.
- Several shapes on a timeline: `morphAt(frame, [0, 30, 60], [a, b, c], ease)`; repeat a shape on a later key to
  hold it. `MorphPath` adds a hold/move schedule and interpolates `colors` in step.
- At rest (t = 0 or 1) the exact source strings are shown, so held frames have no resampling artefacts.
- Letters and icons with holes (o, a, rings): morph them as separate subpaths, or cross-fade instead.
- Debug a bad morph by drawing `PathInternals.debugPath(d)` vertex markers over both shapes.

## 5. Placing and sizing

- The kit's builders: `circlePath(cx, cy, r)` (starts at 12 o'clock, clockwise), `roundedRectPath(x, y, w, h, r)`,
  `starPath(cx, cy, points, outer, inner)`, `polyPath(points, closed)`, `smoothPath(points, tension, closed)`,
  `bendPath(a, b, bend)`.
- `@remotion/shapes` makers give paths too (`makeCircle`, `makeRect`, `makeStar`, `makePolygon`, `makeHeart`,
  `makeTriangle`, `makeArrow`, `makeCallout`, `makePie`, `makeSpark`, `makeEllipse`): see shapes-marks-callouts.md.
- A path from a design tool: keep its viewBox, or `getBoundingBox(d).viewBox`; `DrawPath` computes one with room for
  the stroke.
- Mask a scene with a path: `clipPath: path("M...")` in CSS (no quotes inside the d), sized to the frame diagonal
  for reveals; prefer CSS clip-path over SVG `<clipPath id>` (ids collide; if you must, make them with `useId()`).

## 6. Warps and text as paths

- `warpPath(d, ({x, y}) => ({x, y: y + Math.sin(x / 40 + frame / 6) * 12}), {interpolationThreshold: 2})` for a flag
  wave; a bulge scales points by their distance from a centre. Output grows a lot: memoise static warps and keep
  thresholds 1 to 3.
- Text as outlines (draw-on lettering, warped words): opentype.js (not installed in the kit; add it only if needed)
  loads a font file from `public/` inside `delayRender`, `font.getPath(text, 0, size, size).toPathData(2)`, then
  `resetPath` and `getBoundingBox`. Use HTML text whenever no path operation is needed (sharper, shapes Bangla).
- Bangla lettering as paths is fragile (shaping happens in the font engine, not in opentype's simple path); draw
  Bangla with HTML text and mask or animate the box instead.

## 7. Arrows

- Line arrows (kit `Arrow`/`ArrowPath`): the shaft draws with a dash, the head rides the tip and turns with it,
  growing over the first stretch so the first frames never show a head without a line; a filled head's point sits at
  the tip and the shaft stops short so its round cap does not poke through; `gap` keeps both ends clear of what they
  connect; `tail` for two-way arrows; `dash` for a dotted shaft.
- Block arrows: `makeArrow({length, headWidth, headLength, shaftWidth, direction, cornerRadius})` from
  @remotion/shapes (headWidth must be at least shaftWidth, headLength at most length), revealed with
  `clip-path: inset(0 X% 0 0)` or scaled from its back end.
- Hand-drawn arrows: `HandMark kind="arrow" direction="up"`.

## 8. Performance

- Parse once: `pathLength`, `subpathsOf`, `resamplePath` and morph alignments are cached by string.
- `getPointAtLength` parses the path each call; a bisection (the kit's `lengthAtX`) is cached per point.
- `warpPath` and `interpolatePath` outputs: memoise on inputs, not per frame when static.
- A thousand paths per frame is fine; a thousand `getPointAtLength` calls per frame is not.
