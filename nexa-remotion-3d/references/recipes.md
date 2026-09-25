# Recipes: raw React Three Fiber in Remotion, when the kit has no component

Every recipe follows render-safety.md: values from `useCurrentFrame()`, per-frame imperative work in
`useLayoutEffect`, async work held with `delayRender` and redrawn with `advance()`.

## 1. A minimal correct scene without the kit

```tsx
import {ThreeCanvas} from '@remotion/three';
import {useCurrentFrame, useVideoConfig, interpolate, Easing} from 'remotion';
import * as THREE from 'three';

export const Spin: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const turn = interpolate(frame, [0, 4 * fps], [0, Math.PI * 2], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return (
    <ThreeCanvas width={width} height={height} camera={{fov: 30, position: [0, 0, 10]}}
      gl={{toneMapping: THREE.NeutralToneMapping}}>
      <hemisphereLight args={['#ffffff', '#444444', 0.6]} />
      <directionalLight position={[-5, 7, 6]} intensity={2.3} />
      <mesh rotation={[0.3, turn, 0]}>
        <torusKnotGeometry args={[1, 0.32, 200, 32]} />
        <meshPhysicalMaterial color="#2563eb" roughness={0.25} clearcoat={1} />
      </mesh>
    </ThreeCanvas>
  );
};
```

## 2. Moving the camera by hand

```tsx
const Cam: React.FC<{x: number; y: number; z: number}> = ({x, y, z}) => {
  const camera = useThree((s) => s.camera);
  useLayoutEffect(() => {
    camera.position.set(x, y, z);
    camera.lookAt(0, 0, 0);
    camera.updateMatrixWorld();
  }, [camera, x, y, z]);
  return null;
};
```

## 3. Thousands of instances

```tsx
const Field: React.FC<{n: number}> = ({n}) => {
  const frame = useCurrentFrame();
  const ref = useRef<THREE.InstancedMesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  useLayoutEffect(() => {
    const m = ref.current!;
    for (let i = 0; i < n; i++) {
      const t = frame / 30;
      dummy.position.set(random(`x${i}`) * 10 - 5, ((random(`y${i}`) * 10 + t * 0.3) % 10) - 5, random(`z${i}`) * -8);
      dummy.rotation.set(t + i, t * 0.7 + i, 0);
      dummy.updateMatrix();
      m.setMatrixAt(i, dummy.matrix);
    }
    m.instanceMatrix.needsUpdate = true;
  });
  return (
    <instancedMesh ref={ref} args={[undefined, undefined, n]} frustumCulled={false}>
      <boxGeometry args={[0.08, 0.08, 0.08]} />
      <meshStandardMaterial color="#e2e8f0" />
    </instancedMesh>
  );
};
```

## 4. Shader uniforms from the frame

```tsx
const mat = useMemo(() => new THREE.ShaderMaterial({uniforms: {uTime: {value: 0}}, vertexShader, fragmentShader}), []);
useLayoutEffect(() => { mat.uniforms.uTime.value = frame / fps; });
```
End custom fragment shaders with `#include <tonemapping_fragment>` and `#include <colorspace_fragment>` and pass
linear colours. Anything procedural (noise, hash) must be a function of `uTime` and position only.

## 5. A glTF model

Use the kit's `Model` (load, fit, anchor, frame-driven clip). Raw version: `GLTFLoader().load(staticFile('x.glb'))`
in an effect, state, `useHoldUntil`, `<primitive object={clone}>`, and `mixer.setTime(frame / fps)` in
`useLayoutEffect`. Compressed files:
```ts
const draco = new DRACOLoader().setDecoderPath(staticFile('draco/')); // copy node_modules/three/examples/jsm/libs/draco/*
const loader = new GLTFLoader().setDRACOLoader(draco).setMeshoptDecoder(MeshoptDecoder);
```
Convert client files to GLB (Blender export, or `gltf-transform` offline), keep them under about 10 MB, and bake
anything the brief needs to change (colours, labels) as separate materials you can override in code.

## 6. Video on a surface

```tsx
const {texture, onVideoFrame} = useVideoFrameTexture(1280, 720);
return (<>
  <Video src={staticFile('clip.mp4')} headless muted onVideoFrame={onVideoFrame} />
  <mesh><planeGeometry args={[3.2, 1.8]} /><meshBasicMaterial map={texture} toneMapped={false} /></mesh>
</>);
```
Put the audio as a separate `<Audio>` outside the canvas.

## 7. Bloom and other post passes

Use the kit's `Bloom`. Raw: build `EffectComposer(gl)` with `RenderPass`, `UnrealBloomPass`, `OutputPass`, size it
from `useThree().size` and the pixel ratio, and draw it with `useFrame(() => composer.render(), 1)`. Stateless passes
only (bloom, FXAA, vignette-style shader passes); no `AfterimagePass`, no temporal AA. Note the OutputPass tone-maps
everything, including `toneMapped={false}` materials.

## 8. Orthographic, flat-shaded "2.5D" scenes

`<ThreeCanvas orthographic camera={{zoom: 100, position: [0, 0, 50], near: 0.1, far: 1000}}>`: `zoom` is px per
world unit, so layout maps to pixels (useful for isometric illustrations: rotate a group by `[Math.atan(1 /
Math.sqrt(2)), Math.PI / 4, 0]`). Unlit `meshBasicMaterial` plus `lineSegments` of `EdgesGeometry` gives a clean
technical look.

## 9. Split screens and insets

Kit: `<Scene3D width={W / 2} height={H}>` inside a positioned div. Raw: give ThreeCanvas the box size and wrap it in
an absolutely positioned div. Each canvas is a WebGL context: two or three are fine.

## 10. Transparent 3D overlays for an editor

`<Scene3D background="transparent">` (or a ThreeCanvas without a CSS background), render with ProRes 4444
(`--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png`) or VP9 with `yuva420p`.
The canvas keeps alpha (R3F clears with alpha 0; premultiplied alpha composites correctly).

## 11. A 3D scene inside a longer video

```tsx
<Sequence from={90} durationInFrames={150} premountFor={30}>
  <Scene3D>...</Scene3D>
</Sequence>
```
Premount so WebGL starts before the cut in the Studio (renders wait anyway). Inside the scene, `useVideoConfig()`
and the kit's `useStage()` give the Sequence's length, so exits end on its last frame.

## 12. Data-driven 3D (bars, towers, maps of points)

Map values to heights once (`useMemo`), grow each bar with a clamped eased progress from the frame (`scale` y from
0.001 to 1 about its base), label with Text3D or 2D overlays, and move the camera with CameraPath orbit keys. Keep
labels 30 to 50 px at 1080 and within about 25 degrees of facing the camera. The kit demo `DemoThreeCamera` is a
complete example.

## 13. WebGPU and TSL

Only when you need node materials or compute: `ThreeWebGPUCanvas` from `@remotion/three/webgpu` (4.0.503,
experimental), no `gl` prop, TSL from `three/tsl`, `extend()` the `three/webgpu` namespace for JSX node materials,
render with `--gl=angle`. The same determinism rules apply; test a still first.

## 14. Spline scenes

Spline's "Code (Experimental)" React Three Fiber export plus `@splinetool/r3f-spline` goes inside a ThreeCanvas;
drive its objects and camera from the frame as above. Remotion marks the tutorial as possibly out of date; loading
from Spline's URL fetches at render time, so export and keep the scene file local.
