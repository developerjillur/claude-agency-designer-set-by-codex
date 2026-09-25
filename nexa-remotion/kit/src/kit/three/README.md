# three: 3D for the kit

3D scenes for Remotion 4.0.528 on `@remotion/three` 4.0.528, React Three Fiber 9.8.1 and three 0.186: product
turntables, device mock-ups, extruded 3D type (any web font, Bangla included), particles, camera moves, floating UI
cards, glTF models, video on 3D screens, bloom, and 3D-looking vector solids in plain SVG.

Import by path (the module is heavy): `import {Scene3D, Text3D} from './kit/three'`. Render with `--gl=angle`
(nrk does; the kit's `remotion.config.ts` sets it for the CLI and the Studio; SSR code must pass
`chromiumOptions: {gl: 'angle'}`, and `swangle` on a machine without a GPU).

## The rules every part follows (and your own 3D code must follow)

- Every value comes from `useCurrentFrame()`. Never R3F's `useFrame()` for animation, no clocks, no simulation.
- Per-frame changes are JSX props or `useLayoutEffect`. While rendering, ThreeCanvas draws each frame from a passive
  effect that runs before yours, so a change made in `useEffect` never reaches that frame (measured: an instanced
  mesh updated in `useEffect` showed its initial matrix in every frame; a mesh moved through a ref in `useEffect`
  always showed its JSX prop's value). Props and layout effects were exact in every frame.
- Async results (images, fonts, traced text, models, video frames) hold the render with `delayRender` and redraw
  with `advance(performance.now())` once they are in the scene (`useHoldUntil`, `useRedraw`). `invalidate()` does
  nothing while rendering (frameloop is `'never'`).
- Only local or procedural assets: the studio reflections are three's `RoomEnvironment` (no HDR download), fonts are
  the kit's, models and videos come from `public/` via `staticFile()`.
- Sizes: one world unit is 200 px at a 1080 px short side. `Scene3D` puts the camera so the frame's short side is
  5.4 units at the target in every format, and `useScene3D().px(n)` turns "px at 1080" into world units.

## Scene3D

The stage: a `ThreeCanvas` sized from the stage (or `width`/`height`), a camera preset, a light rig, a procedural
studio environment, sRGB output with tone mapping, and a CSS background from the theme behind a transparent canvas.
Re-provides the theme inside the canvas.

| Prop | Default | Notes |
|---|---|---|
| `camera` | `'front'` | Preset name or `{preset, azimuth, elevation, zoom, fov, target, roll}` (degrees; `zoom` multiplies the distance). Presets: `front`, `hero` (24, 12), `low` (14, -10), `top` (0, 55), `side` (62, 6), `close` (zoom 0.7), `wide` (fov 45, zoom 1.35). |
| `lights` | `'studio'` | `studio`, `soft`, `dramatic`, `flat` or `'none'` (see LightRig). |
| `environment` | the rig's (0.8, 1, 0.28, 0.55) | Reflection intensity from the procedural room, or `false`. |
| `background` | `'studio'` | `'studio'` (soft radial sweep in the theme's ground), `'spot'` (tighter), `'theme'` (flat), `'transparent'` (alpha output), or any CSS background. |
| `toneMapping` | `'neutral'` | `'neutral'` keeps brand colours close to their hex, `'aces'`, `'agx'`, `'none'`. |
| `exposure` | `1` | |
| `shadows` | `false` | Soft shadow maps from the key light; pair with `Floor` and meshes with `castShadow`. |
| `fog` | `false` | `true` or `{near, far, color}`: depth fog in the ground colour. |
| `width`, `height` | the frame | px, for split screens and insets (a custom size gets 5% margins). |

```tsx
<Scene3D camera={{preset: 'hero', target: [-2, 0, 0]}} lights="studio">
  <ProductSpin><Phone3D screen={staticFile('screen.png')} /></ProductSpin>
</Scene3D>
```

`useScene3D()` returns `{theme, dark, width, height, pose, distance, visible: {w, h}, safe: {left, right, top,
bottom, w, h}, px}`: the base camera and the frame and safe area in world units on the target plane. Also exported:
`CAMERA_PRESETS`, `cameraPose(spec, w, h)`, `applyCameraPose(camera, pose)`, `sceneBackground(bg, theme)`.

Gotchas: put a `target` off-centre (`[-2, 0, 0]`) to place a product in the right half with 2D copy on the left,
rather than moving the product sideways (it keeps the perspective symmetric). The near and far planes follow the
camera distance; do not hand-set a tiny `near` (thin layers start to fight). Everything inside is R3F: any
`<Sequence>` inside the canvas needs `layout="none"`. To start a 3D scene mid-video, wrap it in
`<Sequence from={..} durationInFrames={..} premountFor={30}>` so WebGL starts before the cut in the Studio.

## LightRig and StudioEnvironment

Scene3D mounts both; use them directly in a raw `ThreeCanvas`.

- `LightRig` `{rig = 'studio', intensity = 1, accent, shadows = false}`: `studio` (warm key upper left, soft
  hemisphere fill, rim from behind), `soft` (low contrast, wraps UI and playful scenes), `dramatic` (hard side key,
  little fill, accent-tinted rim: dark themes, launches, trailers), `flat` (even light for charts and diagrams).
- `StudioEnvironment` `{intensity = 1, rotation = 0}`: three's `RoomEnvironment` pre-filtered with PMREM, set as
  `scene.environment`. Metals render black without an environment.

## CameraPath

Keyframed camera moves inside a Scene3D.

| Prop | Default | Notes |
|---|---|---|
| `keys` | | `{at, position?, orbit?: {azimuth, elevation, distance}, dolly?, shift?: [right, up], target?, fov?, roll?}`; missing values carry over. `dolly` is the orbit distance as a multiple of the base distance and `shift` slides camera and target in the image plane (world units): both keep a move the same in 16:9 and 9:16, where absolute positions do not. |
| `ease` | `curves.inOut` | One curve or one per segment (`'keys'`), one curve for the pass (`'glide'`). |
| `mode` | `'keys'` | `'keys'`: eased per segment, settles on every key. `'glide'`: one eased pass through a smooth spline. |
| `handheld` | `0` | px at 1080 of seeded drift (4 to 10 feels alive). |
| `handheldFreq`, `seed` | `0.35`, `'camera'` | |

```tsx
<CameraPath keys={[
  {at: 0, orbit: {azimuth: -10, elevation: 8}},
  {at: 90, orbit: {azimuth: 30, elevation: 22, distance: 9}},
  {at: 150, target: [0, 1, 0]},
]} handheld={4} />
```

Gotchas: orbit keys swing in arcs around the target (interpolated in angles); position keys travel in straight
lines, or a spline in `'glide'`. Absolute positions and orbit distances are tuned to one format (the base distance
is 10.1 units in 16:9 at 30 degrees and 17.9 in 9:16): prefer `dolly` and `shift` for moves that must work in both. Two keys on one frame: the later wins. `cameraPathPose(frame, keys, basePose)` gives
the pose without mounting anything.

## Turntable, ProductSpin, ContactShadow

- `Turntable`: turns children about Y with an eased move plus a bob, entrance and exit. `{from = -30, to = 330,
  delay = 0, duration (to the end), ease = curves.inOut, tilt = 0, float = 10 (px), floatPeriod = 3.4 (s),
  enter = 'rise' | 'drop' | 'pop' | 'spin' | 'none', enterDuration, out = 'none' | 'sink' | 'lift' | 'shrink',
  outDuration, position, scale}`. `ease={curves.linear}` for a constant spin.
- `ProductSpin`: Turntable tuned for a product hero (`from = -28, to = 28, enter = 'rise', float = 12`) with a
  contact shadow that fades in as the product arrives and breathes with the bob. `{floor, shadow = 2.2 | false}`.
- `ContactShadow`: a soft blob on the floor, no shadow maps. `{width = 2.4, depth = 45% of width, opacity (0.6 dark,
  0.34 light), color = '#000', lift = 0, ...mesh}`.

```tsx
<ProductSpin from={-34} to={20} floor={-2.05}>
  <Phone3D height={3.3} />
</ProductSpin>
```

Gotchas: `rise` starts below the frame, so the first frames are empty by design. Keep the turn gentle for a hero
(40 to 60 degrees over the shot); a full turn reads as a spec showcase.

## Floor

A ground that never shows an edge: a transparent shadow catcher (needs `Scene3D shadows`) and a grid that fades out.
`{y = 0, grid = 1 (world units, or false), gridColor, gridOpacity, fade = 7 (radius), shadowOpacity (0.5 dark,
0.2 light), size = 60}`.

```tsx
<Scene3D shadows camera="hero"><Floor grid={0.75} fade={6.5} y={-1.2} />...</Scene3D>
```

## RoundedBox and the rounded shapes

`RoundedBox` `{width = 1, height = 1, depth = 1, radius = 0.18, bevel, bevelSegments = 4, color = '#d7dbe2',
roughness = 0.45, metalness = 0.05, material, ...mesh}`: an extruded rounded rectangle with rounded edges (bars,
tiles, devices). Helpers: `roundedRectShape(w, h, r)`, `roundedPlaneGeometry(w, h, r)` (0..1 UVs for textures),
`roundedBoxGeometry(w, h, d, r, bevel)` (front face at z = +d/2, groups 0 caps and 1 sides), `normalizeUvs(geo)`.

```tsx
<RoundedBox width={0.9} height={h} depth={0.9} radius={0.12} position={[0, h / 2, 0]} color={t.colors.accent} />
```

## Phone3D and Card3D

- `Phone3D` `{screen (image), video (muted, looped), ui = 'app' | 'none', screenColor, color (graphite on light
  themes, silver on dark), finish = 'titanium' | 'gloss' | 'matte', height = 3.2, glare = true, children, ...group}`:
  rounded body, black glass, screen, island, buttons and a camera bump on the back. Without `screen` or `video` it
  shows a drawn app screen in the theme's colours and fonts.
- `Card3D` `{front, back (images), width = 3.2, finish = 'gloss', brand, number, name, expiry, color, color2}`: an
  ISO-proportioned payment or membership card with drawn faces (chip, contactless mark, number, name) when no images
  are given.

```tsx
<Turntable from={-24} to={336} tilt={-8}><Card3D brand="nexa" name="SAM CARTER" /></Turntable>
<Phone3D video={staticFile('three/screen.mp4')} height={4.6} />
```

Gotchas: screens are cropped to cover (keep important UI away from the edges). Decal layers sit on the glass with
real gaps and polygon offset; do not add your own planes at the same depth. Images need CORS when remote.

## Text3D

Extruded, bevelled type in the theme's display font (or any loaded CSS stack), with staggered reveals.

| Prop | Default | Notes |
|---|---|---|
| `text` | | `\n` for lines. |
| `size` | `150` | Font size (the em) in px at 1080. |
| `depth`, `bevel` | `0.22`, `0.016` | In em. `bevel: 0` for sharp edges. |
| `font`, `weight`, `italic`, `tracking`, `caps` | the theme's display | `tracking` in em. |
| `lineHeight`, `align` | `1.05`, `'center'` | |
| `maxWidth` | 96% of the safe width | World units; longer text scales down to fit. |
| `color`, `sideColor` | text colour, accent | Face and side/bevel colours. |
| `look` | `'duo'` | `duo` (exact unlit face, lit accent sides), `solid`, `metal` (chrome, silver on dark themes), `glossy`. |
| `in` | `'rise'` | `rise` (masked rise from the baseline), `flip` (stands up from lying flat), `drop` (falls in with a settle), `extrude` (wipes in flat, then gains depth), `wipe`, `none`. |
| `out` | `'none'` | `sink`, `flip`, `drop`, `wipe`, `none`; ends on the last frame of the Sequence. |
| `delay`, `duration`, `stagger` | `0`, 22, 14 (at 30 fps) | `stagger` = frames from the first part to the last, left to right, line by line. |
| `outDuration`, `outAt`, `ease`, `resolution` | 16, auto, per style, `220` | `resolution` = canvas px per em while tracing. |

```tsx
<Text3D text="Launch Day" size={200} in="rise" out="sink" delay={6} position={[0, 0.35, 0]} />
<Text3D text="নতুন শুরু" size={210} in="flip" />
<Text3D text="Nexa Pro" look="metal" in="extrude" depth={0.3} bevel={0.03} />
```

How it works: three 0.186 ships no typeface fonts and `TextGeometry` cannot shape Bangla, so `traceText` draws the
text on a canvas with the loaded font (the browser shapes it), erodes the coverage by the bevel size, traces the
50% contour with marching squares, simplifies it, nests holes, and extrudes it; the bevel grows the outline back to
the font's true silhouette. Parts are connected outlines, so a Latin word staggers by letter and a Bangla word by
its joined clusters, never breaking conjuncts.

Gotchas: fonts are waited for through the kit's loaders (`useFontsReady` with `themeFontRefs`), because on 4.0.528
Google Fonts faces enter `document.fonts` only after they load. Very thin display fonts want `bevel` 0.006 or 0.
Large type above about 300 px: raise `resolution` to 320. The `rise` and `wipe` reveals use clipping planes (Scene3D
enables local clipping; in a raw ThreeCanvas set `gl={{localClippingEnabled: true}}`).

## Particles

A seeded particle field, every position a pure function of the frame (drift, wrap-around, noise wobble).

| Prop | Default | Notes |
|---|---|---|
| `kind` | `'dust'` | `dust`, `bokeh` (large soft discs with a lens rim), `stars`, `embers` (rising sparks), `snow`, `confetti` (instanced tumbling paper, lit). |
| `count` | per kind (700, 34, 1400, 320, 700, 260) | |
| `colors` | from the theme | |
| `speed`, `size`, `opacity` | `1`, `1`, `1` | |
| `near`, `far` | `2.5`, `-9` | World z range; the camera sits at +z looking at 0. |
| `spread` | `1.1` | 1 = exactly the frame at every depth. |
| `fadeIn`, `seed` | `0`, `'particles'` | |

```tsx
<Particles kind="bokeh" fadeIn={24} />
<Particles kind="dust" count={320} opacity={0.7} />
```

Gotchas: glowing kinds add light on dark themes and blend normally on light ones. With `Bloom` on, additive
particles blend in linear light and read brighter: halve their opacity. Points are sized in world units and scale
with the pixel ratio, so the Studio and the render match.

## FloatingCards

UI cards floating at different depths; real parallax when the camera moves.

| Prop | Default | Notes |
|---|---|---|
| `cards` | five of `SAMPLE_CARDS` | `{title, value, caption, chart: number[], up, accent, src (image), color, width = 420, height = 300 (px), x, y (px from centre), z (world), turn (deg)}`. |
| `layout` | `'scatter'` | `scatter`, `row`, `fan`. |
| `enter`, `out` | `'fly'`, `'none'` | `fly` (from depth with a fade), `rise`; `out: 'fly'` flies them past the camera. |
| `delay`, `stagger`, `enterDuration`, `outDuration` | `0`, 6, 30, 18 (at 30 fps) | |
| `float`, `radius`, `shadow`, `seed` | `14` px, theme radius (min 16), `true`, `'cards'` | |

```tsx
<Scene3D lights="soft">
  <CameraPath keys={[{at: 0, orbit: {azimuth: -4}, dolly: 1.06, shift: [-0.45, 0.18]}, {at: 179, orbit: {azimuth: 4}, dolly: 0.95, shift: [0.45, -0.1]}]} mode="glide" />
  <FloatingCards delay={4} out="fly" />
</Scene3D>
```

Gotchas: cards are flat, unlit (exact UI colours) and transparent while fading; keep them apart in depth so sorting
never flips. Stat cards are drawn with the theme's fonts at twice their pixel size.

## Model and useModel

A glTF / GLB from `public/` loaded with three's `GLTFLoader` under `delayRender`, cloned (skinned meshes too),
fitted and anchored, with a clip driven by the frame (`mixer.setTime`).

| Prop | Default | Notes |
|---|---|---|
| `src` | | `staticFile('model.glb')` or a CORS URL. |
| `height` / `size` | | Fit to a height, or the largest side, in world units. |
| `anchor` | `'bottom'` | `bottom` (stands on y = 0), `center`, `none`. |
| `clip` | `0` | Name or index; `false` for the rest pose. |
| `time` / `speed` / `offset` / `loop` | frame / fps, `1`, `0`, `true` | `offset={-1.6} loop={false}` plays once, 1.6 s in. |
| `castShadow`, `receiveShadow`, `envIntensity` | `true`, `true`, file's | |

```tsx
<ProductSpin from={-20} to={25} float={0} floor={-0.01}>
  <Model src={staticFile('three/bottle.glb')} height={2.7} offset={-1.6} loop={false} />
</ProductSpin>
```

Gotchas: Draco or KTX2 compressed files need `DRACOLoader`/`KTX2Loader` with decoder files copied from
`node_modules/three/examples/jsm/libs/` into `public/` (never a CDN); Meshopt works with `MeshoptDecoder` from the
same folder. `kit/public/three/bottle.glb` is a small generated test asset (a lathe bottle with an "Open" clip);
`wallpaper.jpg` and `screen.mp4` (a drifting gradient) were made here in code too. Nothing was downloaded.

## VideoPlane and useVideoFrameTexture

Video on 3D surfaces with `@remotion/media`'s `<Video headless onVideoFrame>`: frames are drawn into a canvas
texture and the scene is redrawn with `advance()` while rendering.

- `useVideoFrameTexture(width = 1080, height = 1920, fit = 'cover')` returns `{texture, onVideoFrame}`; render
  `<Video src headless muted onVideoFrame={onVideoFrame} />` inside the canvas and use `texture` as a map with
  `toneMapped={false}`.
- `VideoPlane` `{src, width = 3.2, height = 1.8, radius = 0.12, loop = true, trimBefore, playbackRate, density = 400
  (texture px per unit)}`: a rounded screen in space. `Phone3D video` uses the same hook.

Gotchas: muted by design (lay audio with `<Audio>`). `@remotion/media` needs CORS for remote files.

## Bloom

`{strength = 0.7, radius = 0.4, threshold = 0.8}`: `UnrealBloomPass` through three's EffectComposer, drawn from a
priority-1 `useFrame` (a render takeover that runs inside `advance()` and uses no time). Verified frame-accurate and
the canvas stays transparent over the CSS background. While it is on, the OutputPass tone-maps everything, so
`toneMapped={false}` faces and screens are tone-mapped too. Do not add stateful passes (afterimage, TAA).

## Svg3D

An extruded, lit vector solid in plain SVG, no WebGL: side walls from `@remotion/svg-3d-engine`'s `extrudeElement`,
plus our caps, hole-aware normals, back-face culling, depth sorting, perspective, lighting and content on the face.

| Prop | Default | Notes |
|---|---|---|
| `path` / `shape` | `'star'` | Any SVG path, or `star`, `heart`, `badge`, `hexagon`, `rect`, `circle`, `triangle`. |
| `size`, `depth` | `360`, `70` | px at 1080. |
| `color`, `sideColor` | accent, 72% of it | |
| `rotateX`, `rotateY`, `rotateZ` | `-12`, `0`, `0` | Degrees, CSS conventions. |
| `turnFrom`, `turnTo`, `delay`, `duration`, `ease` | `-30`, `30`, `0`, to the end, in-out | An eased turn about the shape's own axis. |
| `enter`, `enterDuration` | `'pop'` | `pop`, `flip`, `none`. |
| `float`, `light`, `perspective` | `8`, `[-0.45, -0.7, 0.55]`, `1800` | `perspective: 0` for orthographic. |
| `x`, `y` | `0`, `0` | px at 1080 from the frame centre. |
| `children` | | SVG on the front face, in the face's own coordinates (centred), e.g. a `<text>` label. |

```tsx
<Svg3D shape="badge" size={320} depth={50} color={t.colors.accent}>
  <text textAnchor="middle" dominantBaseline="central" fill={t.colors.onAccent} style={{fontFamily: t.type.display, fontSize: 64}}>NEW</text>
</Svg3D>
```

Gotchas: best for convex or gently concave logos and badges; painter's sorting of walls is approximate on deep,
very concave shapes seen at steep angles (keep turns within about 60 degrees). `svg3dShapePath(shape, size)` gives
the preset paths.

## Hooks and helpers

- `useRedraw()`: redraw now (`advance` while rendering, `invalidate` in the Studio).
- `useHoldUntil(ready, label)`: hold the render from mount until `ready`, then redraw and continue.
- `useFontsReady(fonts, text, kit)`, `waitForKitFont(ref)`, `themeFontRefs(theme, which)`: wait for fonts before
  drawing or tracing text.
- `useImageTexture(src, aspect, fit)`, `useCanvasTexture({width, height, draw, key, fonts, text, kit})`,
  `fitTexture`, `roundRectPath`, `blobTexture`.
- `traceText(options)`: text to three Shapes with holes (see Text3D).
- Drawings: `drawAppScreen`, `drawCardFront`, `drawCardBack`, `drawStatCard`, `drawingFonts`.
- Units and colour: `PX_PER_UNIT` (200), `SHORT_SIDE_UNITS` (5.4), `deg`, `orbitPoint`, `lerp3`, `mix`, `shade`,
  `withAlpha`, `luminance`.

## Performance

All demos render at normal concurrency (about 2 to 5 s for 12 stills each on the Mac Studio with `--gl=angle`); none
needs `--concurrency=1`. Each Scene3D is one WebGL context: keep to a few per frame (browsers drop the oldest past
about 16). Text3D traces once per tab (tens of ms); `angle` leaks memory on very long renders, so split them.
