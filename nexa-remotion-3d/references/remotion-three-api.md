# @remotion/three, React Three Fiber and three: the API as installed

Versions in the shared install: `remotion` and `@remotion/three` 4.0.528, `@react-three/fiber` 9.8.1, `three`
0.186.1 (REVISION 186), `@types/three` 0.186.0, React 19.2.3. Every Remotion package must be the same exact version.
Install in a fresh project with `npx remotion add @remotion/three` plus `three @react-three/fiber @types/three`.

## `<ThreeCanvas>` (from `@remotion/three`)

Props = R3F `<Canvas>` props + Remotion timing props + `width`, `height` (required, numbers in px).

| Prop | Notes |
|---|---|
| `width`, `height` | Required: the Studio scales the canvas with a CSS transform, which breaks R3F's own measuring. Use `useVideoConfig()` or the kit's `useStage()`. |
| `camera` | `{fov, near, far, position, zoom (orthographic)}`: applied once when the default camera is created. Later changes: set the camera yourself in `useLayoutEffect`. |
| `orthographic` | Orthographic default camera (`zoom` = px per unit). |
| `gl` | Renderer options and properties, e.g. `{antialias: true, alpha: true, toneMapping: THREE.NeutralToneMapping, toneMappingExposure: 1, outputColorSpace: THREE.SRGBColorSpace, localClippingEnabled: true, preserveDrawingBuffer: true}`. Memoise the object. |
| `shadows` | `true`, `'soft'` (PCF soft), `'basic'`, `'percentage'`, `'variance'`, or a shadow-map object. |
| `linear`, `flat`, `legacy` | Shorthands: linear output, no tone mapping, colour management off. Explicit `gl` props win in 9.8.1. |
| `dpr` | Default `[1, 2]` from `devicePixelRatio`: 1 in a render at scale 1, the `--scale` value when scaled, 2 in a Retina Studio. |
| `frameloop` | Ignored while rendering (forced to `'never'`); used in the Studio. |
| `onCreated` | Called after ThreeCanvas has already advanced once while rendering: do not set renderer state here that must be in frame 0; use `gl` props. |
| Timing (4.0.528) | `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name` (default `"<ThreeCanvas>"`), `showInTimeline` (default `false`) and premount props `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted`. ThreeCanvas is its own Sequence when you use them. |
| `style` | On R3F's wrapper div. |

Inside the canvas:
- Remotion hooks work (`useCurrentFrame`, `useVideoConfig`, `useDelayRender`, `useRemotionEnvironment`); R3F v9
  also bridges your own React contexts (theme providers) into the canvas.
- `<Sequence>` renders a `<div>`, which R3F cannot place: use `<Sequence layout="none">` inside the canvas. Same for
  `<Series>` (its default layout is already `'none'`) and any DOM component.
- `useThree()` gives `{gl, scene, camera, size, advance, invalidate, set, viewport}`.

## `<ThreeWebGPUCanvas>` (4.0.503, experimental in three)

`import {ThreeWebGPUCanvas} from '@remotion/three/webgpu'`. Same props as ThreeCanvas without `gl` (it creates
three's `WebGPURenderer`), timing props from 4.0.528. Needs three 0.167+, R3F 9+, React 19. Falls back to a WebGL 2
backend where WebGPU is missing. TSL node materials come from `three/tsl`; using them as JSX needs `extend()` with
the `three/webgpu` namespace. Render with `--gl=angle` on v4 or the canvas can be empty. Use it only when you need
TSL or WebGPU compute; the kit uses the WebGL canvas.

## Deprecated texture hooks

`useVideoTexture(videoRef)` (needs a hidden `<Html5Video>`, not frame-perfect) and `useOffthreadVideoTexture({src,
playbackRate, transparent, toneMapped, delayRenderTimeoutInMilliseconds, delayRenderRetries})` (render only, a new
texture every frame) are deprecated. Use `@remotion/media` `<Video src headless muted onVideoFrame>` into a
`CanvasTexture` and `advance()` in the callback (kit: `useVideoFrameTexture`, `VideoPlane`, `Phone3D video`).
`headless` exists since 4.0.387; `onVideoFrame(frame: CanvasImageSource, now?, metadata?)`.

## React Three Fiber 9.8.1 facts that matter here

- The renderer is created once; `configure()` then applies changed props. Explicit `gl` properties are applied with
  `applyProps` after the colour shorthands, so they win.
- Defaults: `ColorManagement.enabled = true`, `outputColorSpace = SRGBColorSpace`, `toneMapping =
  ACESFilmicToneMapping` (unless `flat`), antialias on, alpha on (transparent canvas, clear alpha 0).
- The default camera looks at the origin on creation; `camera` prop values are not re-applied later.
- `invalidate()` returns early when `frameloop` is `'never'`; `advance(timestamp)` runs `useFrame` subscribers and
  renders synchronously (unless a priority subscriber takes over rendering).
- `useFrame(cb, priority > 0)` takes over rendering (R3F skips its own `gl.render`): the hook for EffectComposer.
- Suspense inside the canvas bubbles to the outer tree, where ThreeCanvas's `SuspenseLoader` holds a
  `delayRender` until it resolves.
- JSX intrinsic elements (`<mesh>`, `<meshStandardMaterial>`) are typed through module augmentation when you
  import from `@react-three/fiber`; objects you build yourself go in as `geometry={geo}`, `material={mat}` or
  `<primitive object={obj} />`.
- Props are applied in the commit, before ThreeCanvas draws the frame: that is what makes prop animation exact.
  Never write the same property both as a JSX prop and imperatively: a prop can overwrite the imperative value.

## three 0.186 facts that matter here

- No `examples/fonts` folder in the npm package, so no typeface JSON to use with `TextGeometry`/`FontLoader`.
  `TTFLoader` imports opentype.js from a CDN URL inside its module: webpack cannot bundle it. The kit traces web
  fonts instead (see text-3d.md).
- Addons: `three/examples/jsm/...` (or `three/addons/...`): `RoundedBoxGeometry`, `TextGeometry`, `FontLoader`,
  `RoomEnvironment`, `GLTFLoader`, `DRACOLoader`, `KTX2Loader`, `SkeletonUtils`, `EffectComposer`, `RenderPass`,
  `UnrealBloomPass`, `OutputPass`, and decoders in `examples/jsm/libs/` (draco, basis, meshopt).
- Tone mappings: `NeutralToneMapping` (keeps base colours; best for brands), `AgXToneMapping` (soft filmic),
  `ACESFilmicToneMapping` (punchy, desaturates highlights), `NoToneMapping`.
- Physical light units: `DirectionalLight` 1 to 3.5 reads well; `HemisphereLight` 0.1 to 1.5 as fill;
  `scene.environmentIntensity` scales the environment (0.25 dramatic to 1 soft). Point and spot lights decay with
  distance squared and need much larger intensities.
- `ExtrudeGeometry` bevels outwards by `bevelSize` from the outline, and since r15x triangulates the caps on the
  contour inset by `bevelOffset`: a negative offset folds acute features. Outlines must be clockwise and holes
  counter-clockwise (it only fixes hole winding when it had to reverse the outline). Groups: 0 = caps, 1 = sides.
- `ShapeGeometry` UVs are in shape units: remap them to 0..1 before putting a texture on a shape (kit:
  `normalizeUvs`, `roundedPlaneGeometry`).
- Clipping planes are in world space; `renderer.localClippingEnabled = true` for material `clippingPlanes`.
- `Scene.environmentIntensity` and `environmentRotation` exist (r163+); `material.envMapIntensity` scales the
  scene environment per material.
- `InstancedMesh.setColorAt` creates `instanceColor` on first use; set it before the first draw.

## Related Remotion APIs

- `staticFile('three/model.glb')` for anything in `public/`; remote URLs as they are (CORS needed for textures,
  models loaded by fetch, and `@remotion/media`).
- `useDelayRender()` (4.0.342) inside components; label every handle; `delayRender(label, {timeoutInMilliseconds})`.
- `useRemotionEnvironment().isRendering` to branch between `advance()` and `invalidate()`.
- `usePixelDensity()` (4.0.472) for your own 2D canvases when rendering with `--scale`.
- `<Sequence premountFor={fps}>` around scenes that start mid-video (not automatic on 4.0.528).
- `@remotion/media` `<Video>` needs CORS for remote files and changes pitch with `playbackRate`.

## Version gates

| Feature | Since |
|---|---|
| ThreeCanvas timing and premount props | 4.0.528 |
| ThreeWebGPUCanvas | 4.0.503 |
| `useDelayRender`, `useRemotionEnvironment` | 4.0.342 |
| `<Video headless>` (`@remotion/media`) | 4.0.387 |
| `useOffthreadVideoTexture` | 4.0.83 (deprecated) |
| Remotion 5 automatic GL (not active on 4.0.528) | 5.0 |
