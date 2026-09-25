# Render safety for 3D in Remotion 4.0.528

What makes a Three.js scene render the same frame in every browser tab, and what breaks it. Most of this is read
from the installed sources (`@remotion/three` 4.0.528, `@react-three/fiber` 9.8.1, three 0.186) and measured in
test renders on 2026-09-26.

## How ThreeCanvas draws a frame while rendering

- `<ThreeCanvas>` wraps R3F's `<Canvas>`. While rendering it forces `frameloop="never"`: the scene is drawn only when
  someone calls `advance()`.
- On mount it holds a `delayRender` until R3F's `onCreated`, and there it calls `state.advance(performance.now())`
  once (before your own `onCreated` runs).
- On every later frame it opens a `delayRender` in a layout effect of the outer tree, and an internal
  `ManualFrameRenderer`, placed in the R3F tree before your children, calls `advance(performance.now())` in a
  passive effect (`useEffect`) and then releases that handle.
- React runs all layout effects of a commit before its passive effects, and passive effects in tree order. So:
  JSX props and `useLayoutEffect` changes are in the scene when the frame is drawn; a `useEffect` in your component
  runs after the draw.

## Measured: which ways of changing the scene reach the frame

A test scene moved four squares by 20 px per frame against a DOM line drawn at the true position, rendered as
stills at frames 0, 1, 2, 10, 11, 12, 40, 41, 59 in one parallel render:

| Method | Result |
|---|---|
| JSX prop (`position={[x, y, 0]}`) | exact in every frame |
| `InstancedMesh.setMatrixAt` in `useLayoutEffect` | exact in every frame |
| `InstancedMesh.setMatrixAt` in `useEffect` | wrong in every frame: the initial identity matrix, or a pose from an earlier frame of that tab |
| a mesh with a JSX `position`, moved through a ref in `useEffect` | wrong in every frame: it always showed the JSX prop's value; the effect's value was never drawn |

So "one frame late" understates it: with many tabs, most tabs draw only one or a few frames, and a `useEffect`
change is simply not in the picture. The same holds for camera moves done in `useEffect` (the official template
sets its camera that way, so the first frame each tab draws uses the default camera).

Rules that follow:
- Animate with JSX props computed from `useCurrentFrame()` wherever you can.
- Imperative per-frame work (instance matrices, buffer attributes, uniforms, `camera.lookAt`, clipping planes,
  `mixer.setTime`) goes in `useLayoutEffect`, with no dependency array or with the frame values as dependencies.
- Never animate with R3F's `useFrame`: its `delta` and `clock` depend on wall time. (A `useFrame` with priority 1
  that only draws, such as an EffectComposer, is fine: it runs inside `advance()` and reads no time.)

## Async work: hold, then redraw with advance()

- `invalidate()` returns immediately when `frameloop` is `'never'` (R3F source), so it does nothing in a render.
  After anything async lands in the scene, call `advance(performance.now())` (from `useThree`), then release your
  `delayRender`. In the Studio the loop runs, so `invalidate()` is enough there.
- Create the `delayRender` handle in a `useState` initializer (or `useDelayRender()` inside the canvas; the R3F tree
  sees Remotion's contexts because ThreeCanvas re-provides them and R3F v9 bridges the rest). Release it on unmount
  too, or a Sequence that ends early hangs the render.
- The kit's `useHoldUntil(ready, label)` does exactly this; `useRedraw()` is the advance-or-invalidate call.

| Asset | Safe pattern |
|---|---|
| Image texture | `TextureLoader.load` in an effect, set state, redraw, continue (`useImageTexture`). Tag colour maps `SRGBColorSpace`. |
| Canvas-drawn texture | wait for fonts, draw once in `useMemo`, redraw, continue (`useCanvasTexture`). |
| Web fonts for canvas text or tracing | see the font trap below. |
| glTF / GLB | `GLTFLoader.load` (textures are parsed before `onLoad`), set state, redraw (`useModel`). |
| Video frames | `@remotion/media` `<Video headless onVideoFrame>`: draw into a canvas texture, set `needsUpdate`, `advance()` inside the callback (`useVideoFrameTexture`). |
| Suspense loaders (drei's `useGLTF`) | ThreeCanvas's Suspense fallback holds a `delayRender`, so they are render-safe, but they fetch at render time; prefer local files. |

## The font trap (4.0.528)

`@remotion/google-fonts` fetches the font file, builds a `FontFace`, waits for it to load, and only then adds it to
`document.fonts`. Until that moment `document.fonts.load('800 100px "Inter"', text)` finds no matching face and
resolves at once, and `document.fonts.check()` returns true for names it does not know. A canvas drawn or traced
right after mount then uses a fallback font. Measured: a 3D title in Baloo Da 2 came out in a system sans.

Fix: wait for the loader's own promise. Calling the same `loadFont()` again with the same weights and subsets
reuses the requests in flight and returns `waitUntilDone()`. The kit does this in `useFontsReady(fonts, text,
themeFontRefs(theme))`. Also note the registered family name can differ from the font's name (digits are spelled
out: "Baloo Da Two", "VTThreeTwoThree"); always use the name the loader returns (the theme's `t.type.*` stacks do).

## Depth precision and thin layers

- A screen plane a millimetre in front of a phone's glass, or a label on a card, fights in the depth buffer when the
  near plane is tiny. On Apple GPUs (ANGLE over Metal) the fight shows as flickering square blocks, not stripes.
- Keep `near` proportional to the camera distance (the kit uses 3% of it, `far` 40 times it), leave real gaps
  between layers (about 0.1% of the object size) and add `polygonOffset` (factor and units -1 to -4) on the upper
  layers.

## GL flags, concurrency, memory

| Situation | Flag |
|---|---|
| Mac or desktop with a GPU | `--gl=angle` (`Config.setChromiumOpenGlRenderer('angle')` for CLI and Studio) |
| Linux server with a GPU | `--gl=angle-egl` (Chrome for Testing, see the cloud GPU guide) |
| No GPU, Lambda, Cloud Run | `--gl=swangle` (software: slow; test a still first) |
| GitHub Actions | no GPU: `swangle` |
| Node SSR (`renderMedia`, `renderStill`, `renderFrames`, `getCompositions`, Lambda, Vercel) | `chromiumOptions: {gl: 'angle'}`; the config file does not apply |
| Remotion 5 | ANGLE by default with a SwiftShader fallback; no flag needed |

- The default `null` renderer gives an empty or black canvas in v4 renders.
- Each ThreeCanvas is one WebGL context; Chrome drops the oldest when about 16 are alive on a page. Keep to a few
  per frame; mount scenes in Sequences so they unmount when done.
- `angle` leaks memory on very long renders: split long 3D renders into frame ranges.
- Normal concurrency is fine for light scenes (all kit demos: about 2 to 5 s for 12 stills). Consider
  `--concurrency=1` only for WebGL-heavy scenes that crash with "Target closed" or lose their context.

## Randomness and simulation

- Seed everything: `random('x-' + i)` from `remotion`, or `@remotion/noise` for smooth motion. Never
  `Math.random()`.
- Positions must be pure functions of the frame. For drifting particles: start position plus velocity times time,
  wrapped into the field with a modulo, plus seeded noise. No accumulated state, no physics steps.
- Physics you cannot write in closed form (a falling pile, cloth): bake it offline to data and index it by frame.
- Animated glTF: `mixer.setTime(frame / fps)` in `useLayoutEffect`, never `mixer.update(delta)`.

## Colour pipeline

- R3F v9 sets `ColorManagement.enabled = true`, sRGB output and ACES Filmic tone mapping unless you pass `flat` /
  `linear` or set `toneMapping` / `outputColorSpace` in the `gl` props (explicit `gl` props win over the shorthands
  in 9.8.1, applied after the renderer is created).
- Hex colours given to materials are sRGB and converted to linear. For exact brand colours on flat faces use
  `meshBasicMaterial toneMapped={false}`.
- Custom `ShaderMaterial`: pass linear colours and end the fragment shader with `#include <tonemapping_fragment>`
  and `#include <colorspace_fragment>`. Writing sRGB directly looks right until a post pass renders to a linear
  target, then it is converted twice and washes out.
- Colour textures: `texture.colorSpace = SRGBColorSpace` (data maps such as normal or roughness stay linear).

## Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Black or empty canvas in the render, fine in the Studio | no GL in headless Chrome | `--gl=angle` (or `swangle`); SSR `chromiumOptions.gl` |
| Objects jump or show the wrong pose in some frames | changes made in `useEffect` or `useFrame` | JSX props or `useLayoutEffect` |
| First frame of each tab has the wrong camera | camera set in `useEffect` | set it in `useLayoutEffect` (kit: `Scene3D`, `CameraPath`) |
| Texture or model missing in some frames | loaded without `delayRender`, or no redraw after load | hold the render and `advance()` after it lands |
| Video texture a frame behind | `invalidate()` in `onVideoFrame` | `advance(performance.now())` while rendering |
| 3D or canvas text in the wrong font | faces not yet in `document.fonts` | wait for the loader's `waitUntilDone()` (`useFontsReady` with kit refs) |
| Square blocks flickering on a screen or label | depth fight on a tile GPU | larger near plane, real gaps, `polygonOffset` |
| Metal renders black | no environment map | `StudioEnvironment` (Scene3D mounts it) |
| Colours washed out after adding Bloom | shader writes sRGB directly | linear colours plus the tone-mapping and colour-space chunks |
| "Error: div is not part of the THREE namespace" or similar | a `<Sequence>` (or any DOM element) inside the canvas | `<Sequence layout="none">`; keep DOM outside ThreeCanvas |
| Points look half the size in the Studio | `gl_PointSize` ignores the pixel ratio | multiply by `gl.getPixelRatio()` |
| Holes in letters filled, or an M/N folded | wrong winding, or a negative bevel offset | outlines clockwise, holes counter-clockwise; erode before extruding (kit's `traceText`) |
| `WebGL context lost` | too many contexts or memory pressure | fewer canvases, lower concurrency, split the render |
