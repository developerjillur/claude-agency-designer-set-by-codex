# @remotion/svg-3d-engine (4.0.528): 3D-looking vectors without WebGL

An undocumented package (no docs page on 4.0.528; read from its source and types). It extrudes SVG paths into 3D
side walls and applies 4x4 matrices, then projects orthographically back to SVG path strings. Remotion uses it for
the extruded buttons and badges on its own website. It renders anywhere: no GL flag, no WebGL context, fast at any
concurrency. The kit's `Svg3D` wraps it with caps, lighting, sorting and perspective.

## Exports

| Export | What it does |
|---|---|
| `extrudeElement({points, depth, pressInDepth, sideColor, crispEdges, description?})` | `points` = `parsePath(d)` from `@remotion/paths`. Returns only the side walls as `FaceType[]`, running from z = +depth/2 to z = -depth/2 + pressInDepth. Curves are subdivided three times at t = 0.5 (each curve becomes 8) so walls follow them. |
| `extrudeAndTransformElement({...same, transformations})` | The same, with one matrix applied to every wall. |
| `transformPath({path, transformation})` | A 2D path string through a 4x4 matrix, projected to a 2D path string (x, y only). |
| `threeDIntoSvgPath(instructions)` | Serialises 3D instructions to an SVG `d` (drops z, no perspective). |
| `rotateX/Y/Z(radians)`, `translateX/Y/Z(n)`, `scaled(n or [x, y, z])`, `scaleX`, `scaleY` | 4x4 matrices, row-major, for column vectors. |
| `reduceMatrices([a, b, c])` | Combines so that `a` applies first, then `b`, then `c`. |
| `aroundCenterPoint({matrix, x, y, z})` | Applies a matrix about a pivot. |
| `interpolateMatrix4d(t, m1, m2)` | Element-wise blend (fine for small differences, not for large rotations). |
| `makeMatrix3dTransform(matrix)` | A CSS `matrix3d(...)` string: put HTML on a face. |
| Types | `FaceType = {color, points: ThreeDReducedInstruction[], centerPoint, crispEdges}`, `ThreeDReducedInstruction` (M, L, C, Q, Z with 4D points), `MatrixTransform4D`, `Vector4D`. |

## Conventions (CSS)

- SVG y points down; positive z comes toward the viewer; `rotateY(+a)` turns the right side away; `rotateX(+a)` tips
  the top away. Draw faces with a larger average z later.
- Projection is orthographic. Add perspective yourself: scale x and y by `f / (f - z)` per point (the kit does, with
  `f = 1800` px at 1080).

## Traps found in the source

- `centerPoint` of the walls is always `[0, 0, 0, 1]`: sorting by it does nothing. Compute each face's average z
  from its points.
- The walls of a path with several subpaths are generated as one run and can bridge from one subpath to the next:
  split with `getSubpaths()` and extrude each.
- No front or back faces: build them yourself (the path at z = +depth/2 and -depth/2 through the same matrix).
- `scalePath()` from `@remotion/paths` re-zeroes the path at its top-left corner: scale first, then centre with
  `translatePath` using the scaled bounding box.
- No lighting, no culling: compute a normal per wall (outward is best decided by an inside test next to the edge,
  which also handles holes), skip walls facing away (normal z < 0) and shade the rest by a light direction.
- The cap that faces the viewer is never covered by walls of the same solid: draw it last. Draw all subpaths' caps
  as one path with `fill-rule="evenodd"` so holes stay open.
- Adjacent walls leave hairline seams when anti-aliased: stroke each wall in its own fill colour (about 0.9 px).

## Raw recipe (what Svg3D does, in short)

```tsx
const M = reduceMatrices([rotateY(turn), rotateX(tilt)]); // spin in its own frame, then tilt in view space
const walls = getSubpaths(centredPath).flatMap((sub) =>
  extrudeElement({points: parsePath(sub), depth, pressInDepth: 0, sideColor, crispEdges: false}));
// per wall: transform points by M, normal from the edge, cull, shade, average z; sort by z
// then the caps: the front face (z = depth / 2) through M, drawn last with fill-rule evenodd
// content on the face: SVG transform matrix(M[0], M[4], M[1], M[5], o.x, o.y) with o = M * (0, 0, depth / 2, 1)
```

## When to use it

- Logos, badges, stickers, icons, simple shapes, big numbers from glyph paths: a 3D feel with no GPU and crisp
  vector edges at any scale, fine on Lambda.
- Turns up to about 60 degrees read well; deep, very concave shapes viewed at steep angles can mis-sort (painter's
  algorithm on walls).
- Not for text you have as a string (no shaping: use Text3D), textures, or real lighting and shadows (use WebGL).
