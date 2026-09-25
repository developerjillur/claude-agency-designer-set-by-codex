# 3D type

## Why the kit traces fonts instead of using TextGeometry

- `TextGeometry` needs a typeface JSON (made with facetype.js). three 0.186's npm package ships none (its
  `examples/fonts` folder is gone), and bundling 450 KB JSON files per weight is heavy.
- `TTFLoader` imports opentype.js from a CDN URL inside its module, which webpack cannot bundle, and it would fetch
  at render time anyway.
- `TextGeometry` places glyphs one by one without shaping, so Bangla conjuncts, vowel signs and reph break, and
  there is no kerning.
- The browser already shapes text correctly with the kit's web fonts. So `traceText` draws the text on a canvas with
  the loaded font and turns the coverage into outlines.

## The tracing pipeline (`traceText`)

1. Wait for the fonts (see render-safety.md: faces enter `document.fonts` only after they load on 4.0.528).
2. Measure each line (`measureText` ink boxes), size a canvas at `resolution` px per em (220 by default, shrunk to
   stay under about 8k px wide and 12 M pixels), draw the lines with `fillText`, honouring letter spacing
   (`ctx.letterSpacing`) and alignment.
3. Read the alpha channel (the anti-aliased coverage).
4. Erode it by the bevel size with a disk min-filter. The bevel will grow the outline back, so the final silhouette
   matches the font while the caps are triangulated on a clean contour. (Stroking the text with an eraser does not
   work: variable fonts keep overlapping contours, and the stroke cuts channels through the glyphs.)
5. Marching squares at the 50% level with interpolated edge points (sub-pixel accurate), saddle cells resolved by
   the cell average, segments linked into closed loops.
6. Douglas-Peucker simplification (about 0.25 px), tiny loops dropped.
7. Nesting by containment: a loop inside an even number of loops is an outline, inside an odd number a hole; each
   hole belongs to the smallest loop around it.
8. Winding set explicitly: outlines clockwise, holes counter-clockwise (ExtrudeGeometry only repairs holes when it
   reverses an outline itself).
9. World units: the ink box is centred at 0, 0; each outline becomes a part with its pivot at its centre x and its
   line's baseline, and `x01` (0 to 1 across the block) for staggering.

`ExtrudeGeometry` then extrudes each part with `bevelOffset: 0` and `bevelSize` = the erosion, translated so the
front face is at z = 0 and depth grows backwards (so an "extrude" reveal can scale z without moving the face).

## Parts and staggering

- Parts are connected outlines. Latin text gives one part per letter (the dot of an i is its own part at the same x,
  so it arrives with its stem). Bangla text gives joined clusters (the matra joins letters), so a stagger never
  breaks a conjunct or separates a vowel sign.
- Staggering by `x01` (plus the line index) reads left to right on every script.

## Looks

| Look | Face | Sides and bevel |
|---|---|---|
| `duo` (default) | `meshBasicMaterial`, exact colour (theme text), unlit | lit standard material in the accent |
| `solid` | exact colour | the face colour darkened to 62% |
| `metal` | physical, metalness 1, roughness 0.22, envMapIntensity 2.4 (silver on dark themes, gunmetal on light) | the same, darker |
| `glossy` | physical, roughness 0.18, clearcoat 1 | lit, darker |

A lit face is not exactly the brand colour (it depends on the light); use `duo` or `solid` when the colour matters.

## Reveals

| `in` | What happens | Built with |
|---|---|---|
| `rise` | parts rise from below their line's baseline, masked | a clipping plane per line at the baseline, moved to world space every frame |
| `flip` | parts stand up from lying flat, with a slight overshoot | rotation about the part's baseline, scale up in the first quarter |
| `drop` | parts fall in from above the frame and settle | a settle spring per part |
| `extrude` | the flat face wipes in left to right, then gains depth | a vertical clipping plane, then z scale |
| `wipe` | a left-to-right mask at full depth | a vertical clipping plane |
| `none` | on from the start | |

Exits (`out`): `sink` (back below the baseline), `flip`, `drop`, `wipe`, ending on the last frame of the Sequence.

## Sizing and fitting

- `size` is the em in px at 1080, like 2D type: 150 to 250 for a hero word, 30 to 50 for labels on a 3D chart.
- `maxWidth` (world units) scales long text down: default 96% of the safe width, so a long title never leaves the
  frame in 9:16.
- Multiple lines: `\n`, `lineHeight` in em, `align`.

## Limits and choices

- Very thin fonts (hairlines under about 0.04 em): use `bevel` 0.006 or 0, or the erosion eats the hairlines.
- Over about 300 px on screen, raise `resolution` to 320 for smoother curves (tracing time grows with the square).
- Per-letter colour: render separate Text3D elements, or post-process `traceText` output yourself.
- Emoji and colour fonts trace as silhouettes.
- If a client provides a typeface JSON, `TextGeometry` from `three/examples/jsm/geometries/TextGeometry.js` with
  `new FontLoader().parse(json)` works for Latin (no shaping): pass `{font, size, depth, bevelEnabled, bevelSize,
  bevelThickness, curveSegments: 8}` (`depth`, not the older `height`, and the default depth is 50: always set it).
- Without WebGL, extruded type in SVG is possible with `Svg3D` given glyph paths (from a font tool), but it cannot
  shape text: prefer Text3D.
