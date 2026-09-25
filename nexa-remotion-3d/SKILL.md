---
name: nexa-remotion-3d
description: "3D in Remotion videos with the nexa-remotion kit: product turntables and hero shots, 3D phone and payment-card mock-ups with an image, a drawn app or a video on the screen, extruded 3D titles in any web font (Bangla included), particle backgrounds (dust, bokeh, stars, embers, snow, confetti), keyframed camera moves and orbits, floating UI cards with parallax, glTF models with frame-driven animation, bloom, 3D bar charts and 3D-looking SVG solids without WebGL. Use it for any 3D, depth or product-render request in a Remotion video, Banglish included ('3D logo banao', 'product ta ghurao', '3D text animation koro'). Part of the nexa-remotion family."
---

# 3D for Remotion

Three.js scenes for Remotion 4.0.528 through `@remotion/three`, React Three Fiber 9.8.1 and three 0.186, built as
kit components that are deterministic in parallel renders and look designed by default. Part of the nexa-remotion
family: the director skill is `nexa-remotion`, the kit lives in `~/.claude/skills/nexa-remotion/kit`, and a project
made with `nrk.py new` imports these parts from `./kit/three` (by path: the module is heavy and is not re-exported
from `./kit`). Every render of a 3D scene needs `--gl=angle` (nrk passes it).

## Fast path

1. Pick the job: product hero (`ProductSpin` + `Phone3D`, `Card3D` or `Model`), 3D title (`Text3D`), background
   (`Particles`), UI story (`FloatingCards` + `CameraPath`), data (bars from `RoundedBox` + `CameraPath`), logo or
   badge without WebGL (`Svg3D`).
2. Wrap WebGL parts in `<Scene3D>` with a camera preset and a light rig that fit the theme: `hero` + `studio` on
   light themes, `dramatic` on dark ones, `soft` for UI, `flat` for charts. Put 2D copy (the kit's `Animate`,
   `Stagger`, `SafeArea`) after the Scene3D so it sits on top, inside the safe area.
3. Aim the camera, not the object: `camera={{preset: 'hero', target: [-2, 0, 0]}}` puts the product in the right
   half and leaves the left for copy; in 9:16 stack copy at the top and the product below.
4. One move per shot: a gentle product turn (40 to 60 degrees), or a camera orbit, or a title reveal, then hold.
5. Render stills: `nrk.py stills PROJECT --every 0.5`, then one full frame with `nrk.py still PROJECT --frame N`
   and look at it: blank canvas (GL flag), fallback fonts, depth flicker, clipped edges, text outside the safe area.
6. Final render with the project's preset; long 3D renders: split into frame ranges (`angle` leaks memory).

## Components (from `./kit/three`)

| Component | Use it for | Key props |
|---|---|---|
| `Scene3D` | the stage: sized canvas, camera, lights, reflections, tone mapping, CSS background | `camera` (preset or `{preset, azimuth, elevation, zoom, fov, target, roll}`), `lights`, `environment`, `background`, `toneMapping`, `shadows`, `fog`, `width`/`height` |
| `CameraPath` | keyframed camera moves and orbits | `keys: [{at, orbit: {azimuth, elevation}, dolly, shift, position, target, fov, roll}]` (`dolly` and `shift` work in every format), `ease`, `mode` (`keys`, `glide`), `handheld` |
| `Turntable` | turn and bob any 3D child with an entrance and an exit | `from`, `to`, `ease`, `tilt`, `float`, `enter` (`rise`, `drop`, `pop`, `spin`), `out` |
| `ProductSpin` | product hero turn with a breathing contact shadow | Turntable props + `floor`, `shadow` |
| `Phone3D` | modern phone mock-up | `screen` (image), `video`, `ui` (drawn app), `color`, `finish`, `height` |
| `Card3D` | payment or membership card, printed both sides | `front`, `back`, `brand`, `number`, `name`, `expiry`, `color`, `color2`, `finish` |
| `Text3D` | extruded 3D title in any loaded font, Bangla included | `text`, `size`, `depth`, `bevel`, `look` (`duo`, `solid`, `metal`, `glossy`), `in` (`rise`, `flip`, `drop`, `extrude`, `wipe`), `out`, `stagger` |
| `Particles` | seeded background fields | `kind` (`dust`, `bokeh`, `stars`, `embers`, `snow`, `confetti`), `count`, `opacity`, `speed`, `fadeIn` |
| `FloatingCards` | stat or image cards in depth with parallax | `cards` (`title`, `value`, `caption`, `chart`, `src`), `layout`, `enter`, `out` |
| `Model` | a glTF / GLB, fitted, with a frame-driven clip | `src`, `height`/`size`, `anchor`, `clip`, `offset`, `loop` |
| `VideoPlane`, `useVideoFrameTexture` | video on any 3D surface | `src`, `width`, `height`, `radius` |
| `RoundedBox`, `Floor`, `ContactShadow` | bars and tiles; a ground with shadows and a fading grid; a soft blob shadow | sizes in world units |
| `Bloom` | glow on highlights and emissive parts | `strength`, `radius`, `threshold` |
| `Svg3D` | extruded lit vector solids in plain SVG (no WebGL) | `shape` or `path`, `size`, `depth`, `color`, `turnFrom`/`turnTo`, `children` (content on the face) |
| hooks | building your own parts safely | `useScene3D`, `useHoldUntil`, `useRedraw`, `useFontsReady`, `useImageTexture`, `useCanvasTexture`, `traceText` |

The module README (`kit/src/kit/three/README.md`) lists every prop and default.

## Craft rules

- **Units.** One world unit is 200 px at a 1080 short side; Scene3D fixes the camera so this holds in every format.
  Size in px at 1080 and convert with `useScene3D().px()`. A phone 3.2 to 3.3 units tall in 16:9, 4.6 in 9:16.
- **Camera.** Long lenses (28 to 35 degrees) for products and type, 45 degrees for depth and particles. Hero angle:
  azimuth 20 to 30, elevation 8 to 15. One camera move per shot, 60 to 150 frames, ease in-out; 4 to 8 px of
  handheld drift on long holds; no roll on products.
- **Light.** Always an environment for metal and gloss. Studio rig on light grounds (key about 2.3, rim 1.7, fill
  0.55), dramatic on dark (hard side key 3.4, accent rim 3.2, fill 0.12). Ground objects with `ContactShadow`, or
  real shadows with a high key so they stay short.
- **Colour.** Neutral tone mapping keeps brand colours; exact colours (UI, screens, type faces) on unlit materials
  with `toneMapped={false}`. Backgrounds are CSS behind a transparent canvas.
- **Motion.** Products rise in over 30 to 40 frames and turn slowly; titles reveal once (18 to 26 frames a part,
  10 to 16 frames spread) and hold still while read; move the camera, not the letters, during a hold. Exits 12 to
  18 frames, ease in, ending on the last frame.
- **Type.** 3D type for one hero word, number or logo word; supporting copy stays 2D. Depth 0.15 to 0.3 em, bevel
  0.01 to 0.03 em, viewed within about 25 degrees of straight on.
- **Particles.** Behind type keep them quiet: dust opacity 0.6, bokeh alpha 0.05 to 0.16. Confetti for one
  celebratory beat, not a whole video.
- **Budget.** A few WebGL canvases at most per frame (about 16 contexts per page is the hard limit), under 200 k
  triangles, Bloom only on hero shots.

## Recipes

Product hero with copy (16:9):
```tsx
<AbsoluteFill>
  <Scene3D camera={{preset: 'hero', target: [-2.1, 0, 0]}} lights={t.dark ? 'dramatic' : 'studio'}>
    <ProductSpin from={-34} to={20} delay={4} floor={-2.05}>
      <Phone3D screen={staticFile('app.png')} height={3.3} />
    </ProductSpin>
  </Scene3D>
  <SafeArea justify="center" style={{width: '44%'}}>{/* eyebrow, headline, one line */}</SafeArea>
</AbsoluteFill>
```

3D title with a camera drift and dust:
```tsx
<Scene3D camera={{preset: 'front', elevation: 6}}>
  <CameraPath keys={[{at: 0, orbit: {azimuth: -9, elevation: 7}}, {at: 119, orbit: {azimuth: 9, elevation: 4}}]} ease={curves.sine} />
  <Particles kind="dust" count={320} opacity={0.7} />
  <Text3D text="Launch Day" size={200} in="rise" out="sink" delay={6} position={[0, 0.35, 0]} />
</Scene3D>
```

Chrome launch title on a dark theme: `<Text3D text="Nexa Pro" look="metal" in="extrude" depth={0.3} bevel={0.03}
/>` with `lights="dramatic"`, `<Particles kind="bokeh" opacity={0.4} />` and `<Bloom strength={0.45}
threshold={0.82} />`.

Bangla: `<Text3D text="নতুন শুরু" size={210} in="flip" />` in the `dhaka` theme: shaped by the browser, staggered
by joined clusters.

Floating dashboard cards with parallax:
```tsx
<Scene3D camera="front" lights="soft">
  <CameraPath keys={[{at: 0, orbit: {azimuth: -4}, dolly: 1.06, shift: [-0.45, 0.18]}, {at: 179, orbit: {azimuth: 4}, dolly: 0.95, shift: [0.45, -0.1]}]} mode="glide" />
  <FloatingCards delay={4} out="fly" cards={[{title: 'Monthly revenue', value: '$48.2k', caption: '+12.4%', chart: [12, 14, 13, 17, 21, 24]}]} />
</Scene3D>
```

A model with its animation played once: `<Model src={staticFile('bottle.glb')} height={2.7} offset={-1.6}
loop={false} />` inside `ProductSpin`, with `Scene3D shadows` and `<Floor grid={false} />`.

No-WebGL badge: `<Svg3D shape="badge" size={320} depth={50}><text ...>NEW</text></Svg3D>` (works on Lambda and in
any concurrency).

## Remotion 4.0.528 facts and traps

- `<ThreeCanvas>` needs `width` and `height`. Since 4.0.528 it takes Sequence timing and premount props itself
  (`showInTimeline` defaults to false). Any `<Sequence>` inside it needs `layout="none"`.
- While rendering, frameloop is forced to `'never'` and the frame is drawn in a passive effect that runs before
  your components' effects. Measured: changes made in `useEffect` never reach the frame (an instanced mesh showed
  its initial matrix in every frame). Animate with JSX props or `useLayoutEffect`; never with R3F's `useFrame`.
- After async work lands (texture, model, font, video frame) call `advance(performance.now())`; `invalidate()` does
  nothing while rendering. The official template's `invalidate()` in `onVideoFrame` and camera set in `useEffect`
  are the patterns to avoid.
- `@remotion/google-fonts` adds a face to `document.fonts` only after it loads, so `document.fonts.load()` can
  resolve before the font exists and a canvas draws a fallback. Wait for the loader's `waitUntilDone()` (the kit's
  `useFontsReady` with `themeFontRefs`). Family names may spell digits out ("Baloo Da Two").
- three 0.186 has no typeface fonts in npm and `TTFLoader` imports from a CDN: the kit traces web fonts instead.
- `ExtrudeGeometry` triangulates caps on the inset contour: a negative `bevelOffset` folds acute letters (M, N);
  it only repairs hole winding when it reverses the outline.
- R3F 9 defaults to sRGB output and ACES tone mapping; explicit `gl` props win. The `camera` prop applies once.
- Tiny near planes make thin layers fight; on ANGLE over Metal it shows as flickering blocks. Scale near/far with
  distance and add polygon offset.
- `useVideoTexture` and `useOffthreadVideoTexture` are deprecated: `@remotion/media` `<Video headless
  onVideoFrame>` into a CanvasTexture.
- `--gl=angle` locally, `angle-egl` on Linux GPUs, `swangle` without a GPU (Lambda, CI); SSR APIs need
  `chromiumOptions: {gl: 'angle'}`. Remotion 5 picks automatically; 4.0.528 does not.
- `ThreeWebGPUCanvas` (4.0.503, `@remotion/three/webgpu`) is experimental; use it only for TSL or compute.

## References

- `references/render-safety.md`: how ThreeCanvas draws a frame, the measured lag experiment, async assets, the font
  trap, depth precision, GL flags, colour pipeline, errors and fixes.
- `references/remotion-three-api.md`: ThreeCanvas, ThreeWebGPUCanvas, the deprecated texture hooks, R3F 9.8.1 and
  three 0.186 facts, version gates.
- `references/scene-craft.md`: units and framing, camera language, light rigs, material values, colour and tone,
  3D type, timing tables, composition with 2D, performance budget.
- `references/text-3d.md`: why and how the kit traces fonts, looks, reveals, sizing, limits, the TextGeometry route.
- `references/svg-3d-engine.md`: the undocumented package's API, its traps, and the raw recipe behind Svg3D.
- `references/recipes.md`: raw R3F in Remotion: cameras, instancing, shaders, glTF, video, bloom, orthographic,
  split screens, transparent overlays, Sequences, data scenes, WebGPU, Spline.
