# D1-core-a: Remotion core docs, part A (fundamentals, animation, composition, timing, core APIs)

Agent: D1-core-a. Material: `assign-D1-core-a.txt` (131 pages of `mirror/docs/`, root section, `2-0-migration.md` through `measuring.md`).
Target runtime: Remotion 4.0.528 + React 19 on this machine. Docs mirror tracks 4.0.529.

---

## 1. Scope and coverage

- Read fully: 131 of 131 assigned pages. Every path is listed in `kb/D1-core-a.coverage.txt` (diffed against the assignment: identical, no duplicates).
- Could not read: nothing. Notes on page types:
  - Index pages whose real content is a `<TableOfContents />` of subpages (so the subpage APIs are NOT in this file): `animation-utils.md`, `animated-emoji.md`, `api.md`, `bundler.md`, `canvas-capture.md`, `captions.md`, `gif.md`, `gsap.md`, `layout-utils.md`, `legal.md`, `license.md`, `mac-cursors.md`, `elevenlabs.md`, `fonts-api.md`, `lottie.md`, `install-whisper-cpp.md` (function list), `canvas.md`/`codemods.md`/`browser-bundler.md` (partial API lists). Other agents own those subpages (`<Gif>`, layout-utils functions, gsap APIs, animation-utils, captions API, etc.).
  - HTML-converted pages with type noise (content extracted fine): `cli.md`, `fonts-api.md`, `google-fonts.md`, `lottie.md`.
  - Legal/business pages read for completeness, low value for skills: `dpa.md`, `dpia.md`, `acknowledgements.md`, `investors.md`, `lovable-for-motion-graphics.md`, `ask-in-public.md`, `get-help.md`, `contributing.md`, `accessibility.md` (product a11y, not animation).
- Several topics the lead asked for live in the other half of the alphabet (D2): `spring()`, `<Sequence>`, `<Series>`, `<Still>`, `staticFile()`, `random()`, `useCurrentFrame()`, `useVideoConfig()`, schemas/Zod, `registerRoot()`, `useDelayRender()`, `useCurrentScale()`. I cover them only as far as my pages use or specify them, and flag gaps in section 9.
- Verified against the installed package (read only) `nexa-media/remotion-broll/node_modules/remotion` = 4.0.528 and `@remotion/renderer`, `@remotion/cli`:
  - `interpolate()` validation messages (strictly increasing input range, string rules, step1 rule).
  - `interpolateColors()` always clamps and blends in sRGB (8-bit rounded channels, alpha to 3 decimals).
  - `Easing.spring` exists (normalized to a 30-frame spring at 30 fps); `Easing.back` default `s = 1.70158`; `Easing.elastic` default `bounciness = 1`.
  - `measureSpring` default `threshold = 0.005`.
  - `delayRender` default timeout 30000 ms, error fires 2000 ms earlier (hence "28000ms" in messages).
  - `ENABLE_V5_BREAKING_CHANGES = false`: none of the 5.0 defaults (auto premount, bt709, angle GL, etc.) are active in 4.0.528.
  - Color space: valid values `"default" | "bt601" | "bt709" | "bt2020-ncl"`, default `"default"` (bt601-like). `Config.setColorSpace()` exists in `@remotion/cli` 4.0.528 typings even though the config doc page does not list it.
  - `@remotion/effects` is NOT installed in `remotion-broll` (would need `npx remotion add @remotion/effects`).
- Also read (outside the assignment, for recipes only, not in coverage): `examples/timing-functions/src/{TimeRemapping,remap-speed,CameraApproach}.tsx`, `examples/css-animation-play-state/src/Composition.tsx`.

---

## 2. Mental model

1. **A Remotion video is a pure function: (frame, props) -> picture.** Rendering opens several headless Chrome tabs (concurrency), each renders arbitrary frames, possibly out of order, with no shared state. Anything driven by wall clock time (CSS transitions/animations, `setTimeout`, `requestAnimationFrame`, GSAP/Lottie tickers, `Date.now()`, `Math.random()`) desynchronizes across tabs and flickers. Everything visual must be computed from `useCurrentFrame()` plus props plus static data (flickering.md).
2. **Time is in frames.** `seconds = frames / fps`. A composition of `durationInFrames = N` has frames `0 .. N-1` (so "last frame" is `N - 1`; light-leaks and maps pages interpolate over `[0, durationInFrames - 1]`). CLI `--frames=S-E` is inclusive (`E - S + 1` frames).
3. **Two layers of code:**
   - Registration (the Root, called via `registerRoot()` in the entry point): `<Composition>`, `<Still>`, `<Folder>`. Metadata = `id, width, height, fps, durationInFrames, defaultProps, schema, calculateMetadata`.
   - Frame rendering (the component): hooks + JSX, evaluated per frame.
   `calculateMetadata()` bridges them: it runs once per render (in its own tab during `selectComposition()`), can fetch data, change duration/size/fps, transform props and set per-composition render defaults.
4. **Props pipeline:** `defaultProps` (or Studio edits) -> merged with input props (`--props`, `inputProps`) -> optionally transformed by `calculateMetadata` -> received by the component. Must be JSON-serializable (plus `Date`, `Map`, `Set`, `staticFile()` values). `type` not `interface`. `getInputProps()` returns only the raw input props (non-typed), and is `{}` in the Player.
5. **Time transformation components** nest and cascade: `<Sequence>` offsets/trims time, `<Series>` stacks, `<Loop>` repeats (nested loops cascade), `<Freeze>` holds (`useCurrentFrame()` returns the frozen frame inside), and since 4.0.501/4.0.465 many primitives (`<AbsoluteFill>`, `<Img>`, `Interactive.*`, `<CanvasImage>`, `<AnimatedImage>`) accept Sequence timing props directly (`from`, `durationInFrames`, ...).
6. **Animation primitives are just math on a driver value:** `interpolate()` maps any number (frame, spring output, progress) through keyframes, optional easing, extrapolation and output mapping; `spring()` produces a 0 -> 1 physical progress; `Easing.*` reshapes 0..1 progress; values can be added/subtracted (enter minus exit); `interpolateColors()` does colors; `measureSpring()` tells how many frames a spring needs.
7. **Readiness protocol:** a frame is only captured when no `delayRender()` handle is pending. Remotion's asset components (`<Img>`, `<Video>`, `<Audio>`, `<IFrame>`, `<Gif>`, `<AnimatedImage>`, `<CanvasImage>`, `<Html5Video>`, `<Html5Audio>`, `<OffthreadVideo>`) create and clear handles automatically; your own async work must do it (`useDelayRender()` + `useState` initializer). Default timeout 30 s. In Studio/Player `delayRender` is a no-op; use `useBufferState().delayPlayback()` for preview buffering.
8. **Assets live in `public/`, referenced via `staticFile()`**; the bundle is a snapshot (files added after `bundle()` are invisible unless you write into the bundle's public folder via SSR). No `fs`, no absolute paths in components.
9. **Layering = DOM order.** Later siblings paint on top; `<AbsoluteFill>` is the layer primitive; `z-index` is rarely needed.
10. **Canvas pipeline (new, 4.0.455+):** canvas-based components (`<Solid>`, `<HtmlInCanvas>`, `<Video>` from `@remotion/media`, `<Img effects>`, `<CanvasImage>`, `<AnimatedImage>`, `<Gif>`, Rive, `@remotion/shapes`) take an `effects` array (applied in order); custom effects via `createEffect()` (2d, webgl2, webgpu).
11. **Studio editability (4.0.475+):** `Interactive.*` elements and `Interactive.withSchema()` components expose timeline controls and keyframes; the Studio rewrites source code (via `@remotion/codemods`). Code stays editable only if values are inline literals, keyframes are hardcoded `interpolate()` arrays, and transforms use the individual CSS properties `translate`, `scale`, `rotate`, `opacity`.
12. **Environments differ:** Studio (preview + editing), Player (embedded, allows function props), server render (headless Chrome + FFmpeg, CLI/Node/Lambda/Vercel/Cloud Run), client-side render (`@remotion/web-renderer`, WebCodecs, subset of HTML). Check with `getRemotionEnvironment()` / `useRemotionEnvironment()`.
13. **Version landscape:** installed 4.0.528; docs at 4.0.529; 5.0 is planned with breaking default changes that are NOT active on 4.0.528. Write explicit values so code behaves identically on both (see 7.8).

---

## 3. API digest

Format per entry: what, signature, options (default), return, version, gotchas, example.

### 3.1 Animation and timing helpers

#### `interpolate()` (from `remotion`)
- Maps an input value through keyframes: `interpolate(input, inputRange, outputRange, options?)`.
- `inputRange`: numbers, strictly monotonically increasing, finite, same length as `outputRange`. Single-value ranges allowed from 4.0.469 (always returns that value).
- `outputRange` may be:
  - numbers;
  - CSS strings (4.0.472): `scale` (unitless, `'1'`, `'2 3'`), `translate` (length/percent, `'0px 0px'`, `'100px 50px'`), `rotate` (`deg|rad|grad|turn`), `transform-origin` (keywords `left|center|right|top|bottom` from 4.0.475, normalized to %; optional third component must be a length). Up to 3 components; all values same type; units must match per component; missing components default to scale `1`, translate/rotate `0`, origin `50% 50% 0`;
  - numeric tuples (4.0.473), e.g. `[[0, 0.5], [1, 0.5]]`, all same length;
  - arbitrary non-numeric strings only with `easing: Easing.step1` in every segment (4.0.509), e.g. cursor names.
- Options:
  - `extrapolateLeft` / `extrapolateRight`: `'extend'` (default) | `'clamp'` | `'wrap'` | `'identity'`. `interpolate(1.5,[0,1],[0,2])` gives extend 3, clamp 2, identity 1.5, wrap 1. `'identity'` is not allowed for non-numeric strings.
  - `easing`: a function `(t) => t` (default linear) applied to the normalized progress inside the active segment, or (4.0.462) an array with one easing per segment (`length = inputRange.length - 1`; empty array for a single keyframe).
  - `output` (4.0.490): `'linear'` (default, additive) | `'perceptual-scale'` (maps values to signed area `sign(v)*v^2`, interpolates, maps back with sqrt; `[0,1]` at 0.5 gives `Math.sqrt(0.5)`). Easing still controls time; `output` controls value distribution.
  - `outputType` (4.0.526): `'scale' | 'translate' | 'rotate' | 'transform-origin' | 'font-weight'`. Validates strings; font-weight keywords (`normal`, `bold`) only accepted with `'font-weight'` (numbers 1..1000).
  - `posterize` (4.0.470): positive number `n`; quantizes the input so values update every `n` frames (frames 0,1,2 use frame 0's value).
- Types exported since 3.3.77: `ExtrapolateType`, `InterpolateOptions`, `InterpolateOutputType`.
- Gotchas:
  - Without clamping, values keep growing past the last keyframe (scale 2 at frame 40 for `[0,20] -> [0,1]`). Clamp one-shot animations on both sides.
  - Keyframes computed from duration (`[0, 20, durationInFrames - 20, durationInFrames]`) throw "inputRange must be strictly monotonically increasing" when the composition is shorter than the fades. Guard short durations.
  - Driver does not have to be time: `interpolate(springValue, [0,1], [0,200])` is the idiomatic way to map a spring to pixels.
  - Studio keyframing writes hardcoded `interpolate()` arrays; keep your own keyframes literal if the Studio should edit them.

```tsx
const frame = useCurrentFrame();
const {durationInFrames} = useVideoConfig();
const opacity = interpolate(frame, [0, 20, durationInFrames - 20, durationInFrames - 1], [0, 1, 1, 0], {
  extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  easing: [Easing.out(Easing.cubic), Easing.linear, Easing.in(Easing.cubic)],
});
const scale = interpolate(frame, [0, 30], [0.6, 1], {extrapolateRight: 'clamp', output: 'perceptual-scale'});
const translate = interpolate(frame, [0, 30], ['0px 40px', '0px 0px'], {extrapolateRight: 'clamp'});
// <div style={{opacity, scale, translate}} />
```

#### `Easing` (from `remotion`)
- Same API as React Native's Easing. Use as `interpolate(..., {easing})` or `interpolateColors(..., {easing})`.
- Functions (take `t` in 0..1): `linear`, `ease` (cubic-bezier .42,0,1,1), `quad`, `cubic`, `sin`, `circle`, `exp`, `bounce`, `step0` (1 for any positive t), `step1` (1 when t >= 1; hold keyframes).
- Factories: `poly(n)` (n=4 quart, 5 quint), `elastic(bounciness = 1)` (0 = no overshoot, N>1 overshoots about N times), `back(s = 1.70158)` (pulls back before moving), `bezier(x1, y1, x2, y2)` (same as CSS `cubic-bezier`), `spring(config?)` (4.0.476).
- Modifiers: `Easing.in(f)` runs f forwards (ease-in), `Easing.out(f)` runs it backwards (ease-out), `Easing.inOut(f)` symmetric.
- `Easing.spring({damping = 10, mass = 1, stiffness = 100, overshootClamping = false, durationRestThreshold, allowTail = false})`: a spring normalized to interpolation progress (measured as if it took 30 frames), so it needs no `frame`/`fps`. `durationRestThreshold` (4.0.483): how close to the end the spring gets within the segment (lower = settles closer). `allowTail` (4.0.483): lets the spring keep settling after the segment ends, so in multi-keyframe interpolations the previous tail overlaps the next segment.

```tsx
const translate = interpolate(frame, [0, 30, 60], ['0px 1000px', '0px 0px', '1000px 0px'], {
  easing: [
    Easing.spring({allowTail: true, damping: 200, durationRestThreshold: 0.03}),
    Easing.spring({allowTail: true, damping: 200, durationRestThreshold: 0.03}),
  ],
});
```

#### `interpolateColors()` (2.0.3)
- `interpolateColors(input, inputRange, outputRange: string[], options?) => 'rgba(r, g, b, a)'`.
- Accepts CSS names, hex, `rgb/rgba`, `hsl/hsla`, and (4.0.439) `oklch`, `oklab`, `lab`, `lch`, `hwb` with optional `/ alpha`.
- Options: `easing` (4.0.475; function or per-segment array), `posterize` (4.0.470). Single-color ranges from 4.0.469.
- Verified in 4.0.528 source: every color is converted to sRGB first, channels are interpolated linearly in sRGB, always clamped on both sides (no extrapolation option), RGB rounded to integers, alpha to 3 decimals.
- Gotcha: passing `oklch()` colors does NOT give perceptual (OKLCH) blending; mid tones between saturated complementary hues get muddy/grey. Add an explicit middle color stop.

```tsx
const bg = interpolateColors(frame, [0, 30, 60], ['#0b84ff', '#7c3aed', '#ff2d55'], {
  easing: [Easing.inOut(Easing.quad), Easing.inOut(Easing.quad)],
});
```

#### `spring()` as used in my pages (full reference is on the D2 spring page)
- `spring({frame, fps, config?, delay?, durationInFrames?})` returns progress from 0 to 1 (default: slight overshoot, "the text jumps in").
- `config`: `damping`, `mass`, `stiffness`, `overshootClamping` (defaults per the Easing.spring page: 10, 1, 100, false). `config: {damping: 200}` gives a smooth no-bounce settle.
- `delay`: frames to wait; `durationInFrames`: stretch the spring to an exact length (animation-math uses `durationInFrames: 20, delay: durationInFrames - 20` for an exit).
- Idioms: `spring({fps, frame: frame - 10})` delays by 10 frames; subtract an exit spring from an enter spring; map with `interpolate(spring, [0,1], [a,b])`.

#### `measureSpring()` (2.0.8)
- `measureSpring({fps, config?, threshold = 0.005}) => frames` until the spring stays within `threshold` of the target (0.01 = within 1%). Lower threshold = longer duration.
- `measureSpring({fps: 30, config: {damping: 200}})` returns `23`.
- `from` / `to` options are deprecated (no effect, removed in 5.0). Do not pass them.
- Use it to schedule the next beat or to size a `<Sequence>` exactly to a spring.

#### Animation math (animation-math.md)
- Springs and interpolations are numbers: add, subtract, multiply.
- Enter and exit: `scale = enter - exit` where `exit` is a spring with `delay: durationInFrames - 20` and `durationInFrames: 20`.

```tsx
const {fps, durationInFrames} = useVideoConfig();
const enter = spring({fps, frame, config: {damping: 200}});
const exit = spring({fps, frame, config: {damping: 200}, durationInFrames: 20, delay: durationInFrames - 20});
const scale = enter - exit;
```

### 3.2 Structure and timing components

#### `<Composition>`
- Registers a renderable video in the Root (inside a fragment of the component passed to `registerRoot()`).
- Props: `id` (letters, numbers, `-` only), `fps`, `durationInFrames`, `width`, `height`, `component` XOR `lazyComponent` (a function returning a dynamic import; needs a default export; uses Suspense; reduces Studio startup; disabled under Bun runtime), `defaultProps?`, `calculateMetadata?`, `schema?` (top-level `z.object()` validating props and driving Studio controls).
- `defaultProps`: required if the component takes props (since 4.0). Only JSON-serializable values plus `Date`, `Map`, `Set`, `staticFile()`; functions and class instances are lost when rendering (the Player allows function props). Huge objects are slow. Type props with `type`, not `interface` (interfaces fail `Record<string, unknown>`).
- From 4.0.516 the Studio infers controls from `defaultProps` when there is no schema.
- Not usable in the Player or client-side rendering (they take the component directly).

#### `calculateMetadata()` (4.0.0) / `CalculateMetadataFunction<Props>`
- Arguments: `props` (resolved: defaults + input props), `defaultProps`, `abortSignal`, `compositionId` (4.0.98), `isRendering` (4.0.342).
- Return (all optional, JSON-serializable): `props` (same shape/type as input), `durationInFrames`, `width`, `height`, `fps`, `defaultCodec`, `defaultOutName` (4.0.268), `defaultVideoImageFormat` (`'png'|'jpeg'|'none'`, 4.0.316), `defaultPixelFormat` (`yuv420p|yuva420p|yuv422p|yuv444p|yuv420p10le|yuv422p10le|yuv444p10le|yuva444p10le`, 4.0.316), `defaultProResProfile` (`4444-xq|4444|hq|standard|light|proxy`, 4.0.367), `defaultSampleRate` (Hz, 4.0.448).
- May be async; wrapped in a `delayRender` (30 s default timeout). Runs once per render regardless of concurrency, in a separate tab during `selectComposition()`. Re-runs whenever props change in the Studio (use `abortSignal` and debouncing).
- Priority: returned fields override `<Composition>` props; CLI overrides (`--width`, `--height`, `--fps`, `--duration`) override `calculateMetadata`; `--scale` is applied last. `defaultCodec` beats the config file but loses to an explicit render option.
- Not supported by the Player (call the function yourself and pass results).

```tsx
export const calcMeta: CalculateMetadataFunction<Props> = async ({props, abortSignal}) => {
  const res = await fetch(`https://example.com/api/${props.id}`, {signal: abortSignal});
  const data = await res.json();
  return {props: {...props, data}, durationInFrames: Math.ceil(data.seconds * 30), fps: 30};
};
```

#### `<Folder>` (3.0.1)
- Groups compositions in the Studio sidebar only. `name`: `a-z A-Z 0-9 -`. Nestable. No render behavior.

#### `<AbsoluteFill>`
- A `<div>` with `position: absolute; top/left/right/bottom: 0; width/height: 100%; display: flex; flexDirection: column`.
- Inherited Sequence props (4.0.501): `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`. From 4.0.528: `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted`.
- `ref` (HTMLDivElement) since 3.2.13; all div props forwarded.
- Tailwind (4.0.249): conflicting utility classes like `flex-row` disable the matching inline style, so `className="flex flex-row"` works.

```tsx
<AbsoluteFill name="Title" from={30} durationInFrames={90}>visible frames 30..119</AbsoluteFill>
```

#### Layers (layers.md)
- Fixed canvas size makes `position: absolute` normal. Stack `<AbsoluteFill>`s; the lower in the tree, the higher in the stack. Avoid `z-index` in most cases.

#### `<Loop>` (2.5.0)
- Props: `durationInFrames` (one iteration), `times` (default `Infinity`), `layout` (`'absolute-fill'` default | `'none'`), `style` (3.3.4; not allowed with `layout="none"`), `name`, `playbackRate` (4.0.528; speed inside each iteration, constant across frames; iteration still lasts `durationInFrames` in the parent), inherited premount props (4.0.528; need `layout="absolute-fill"`; postmount needs finite `times`).
- Nested loops cascade.
- `Loop.useLoop()` (4.0.142): `null` outside a loop, else `{durationInFrames, iteration}` (iteration starts at 0). Use it to vary each repetition deterministically.

```tsx
<Loop durationInFrames={50} times={3} name="Pulse"><Pulse /></Loop>
const loop = Loop.useLoop(); // {durationInFrames: 50, iteration: 1}
```

#### `<Freeze>` (2.2.0)
- Children see `useCurrentFrame() === frame` regardless of Sequences; videos pause, audio renders muted.
- Props: `frame`, `active` (4.0.127; `boolean` or `(f) => boolean` per current frame).
- For new code prefer `<Sequence freeze={30}>` (editable in the Studio).

#### Entry point, Root, brownfield layout
- Entry point = file calling `registerRoot(RemotionRoot)`; Root returns `<Composition>`s. Brownfield: `remotion/Composition.tsx`, `remotion/Root.tsx`, `remotion/index.ts`; `npx remotion studio remotion/index.ts`; `npx remotion render remotion/index.ts MyComp out.mp4`.
- Gotcha: tsconfig `paths` without a prefix can make `import ... from "remotion"` resolve to your `remotion/` folder.

### 3.3 Props, schemas and Studio interactivity

#### Props resolution and `getInputProps()` (2.0)
- Pass input props with `--props='{"hello":"world"}'` or `--props=./props.json` (studio and render), or `inputProps` in Node/Lambda APIs.
- `getInputProps()` returns the raw input props anywhere (non-typed). Returns `{}` in the Player, client-side rendering, Node. Prefer typed component props or `calculateMetadata`.
- Since 4.0: `renderMedia({composition: {...composition, props}})` props are what the component gets; `inputProps` is what `getInputProps()` returns. Get `composition` from `selectComposition({serveUrl, id, inputProps})`.
- Input props must be an object (wrap arrays). Warning if props > 10 MB (4.0 alpha log).

#### Inferring controls from `defaultProps` (4.0.516)
| Value | Control |
|---|---|
| string | text |
| CSS color string | color picker (needs `@remotion/zod-types`; key contains `color` and value valid, or unambiguous `#`, `rgb()`, `hsl()`, `oklch()`) |
| `staticFile()` value | asset picker |
| number | number |
| boolean | checkbox |
| `Date` | date/time |
| plain object | nested controls |
| non-empty array | array editor if all items match the first item's type |
- Not editable: `null`, `undefined`, empty arrays, mixed arrays, class instances; a key named `type` is a non-editable literal (discriminator).
- Define a Zod `schema` when you need validation, enums, unions, optional/nullable, `.min/.max/.step`, descriptions, `zTextarea()`, `zMatrix()`, `zColor()` (from `@remotion/zod-types`; `z` is no longer exported by `remotion` since 4.0, install `zod`).

#### `Interactive` (4.0.475)
- Elements the Studio can select, drag and keyframe: `Interactive.Div` etc. HTML: `A, Article, Aside, Button, Code, Div, Em, Footer, H1..H6, Header, Label, Li, Main, Nav, Ol, P, Pre, Section, Small, Span, Strong, Ul`. SVG: `Circle, Ellipse, G, Line, Path, Rect, Svg, Text` (controls for `stroke`, `strokeWidth`, and `fill` where paintable).
- Inherited: `durationInFrames, from, trimBefore, playbackRate, freeze, hidden, name, showInTimeline`; premount props from 4.0.528; `cropLeft/Right/Top/Bottom` (ratios 0..1) from 4.0.506; `ref`.
- Schema fragments: `baseSchema` (4.0.479), `transformSchema` (4.0.479: `style.transformOrigin, style.translate, style.scale, style.rotate, style.opacity`), `cropSchema` (4.0.500), `textSchema` (4.0.481: color, fontFamily (4.0.486), fontSize, lineHeight, fontWeight, fontStyle, textAlign, letterSpacing), `backgroundSchema` (4.0.497, `backgroundColor` longhand), `borderSchema` (4.0.497, longhands), `borderRadiusSchema` (4.0.501), `svgPaintSchema` / `svgStrokeSchema` (4.0.499; `color` 4.0.507), `premountSchema` (4.0.479), `sequenceSchema` (4.0.479), `captionsSchema` (4.0.500).
- Editability rules: keep values inline in JSX, hardcoded `interpolate()` keyframe arrays, use `translate`, `scale`, `rotate`, `opacity` style props directly; avoid animated `top`/`left` and `transform` strings.

#### `Interactive.withSchema()` (4.0.479)
- `Interactive.withSchema({Component, componentName, schema, supportsEffects})` returns a component with the public props; the inner component receives `controls` and must forward it to the `<Sequence>` that represents it (and `outlineRef` if `layout="none"`).
- Rendering, Player and read-only Studio use original props; editable Studio merges timeline overrides.
- Always spread `Interactive.baseSchema` into the schema.

```tsx
const circleSchema = {...Interactive.baseSchema, radius: {type: 'number', min: 1, step: 1, default: 80, description: 'Radius', hiddenFromList: false}, ...Interactive.transformSchema} as const satisfies InteractivitySchema;
export const Circle = Interactive.withSchema({Component: CircleInner, componentName: '<Circle>', schema: circleSchema, supportsEffects: false});
```

#### `InteractivitySchema` (4.0.479)
- Plain data, not Zod (Zod is for `<Composition>` props). Keys may use dot notation (`style.opacity`).
- Field types: `number`, `boolean`, `color`, `asset` (`assetType: 'audio'|'video'|'image'`, 4.0.521), `font-family` (4.0.485; choosing a Google Font inserts the matching `loadFont()` call), `enum` (`variants` map to nested schemas), `array` (`item`, `newItemDefault`, `minLength`, `maxLength`), `remotion-captions` (4.0.500), `rotation-css` (`"15deg"`), `rotation-degrees` (number), `translate` (`"10px 20px"`), `transform-origin`, `scale`, `uv-coordinate` (`[x, y]` 0..1 with optional `visual` line/ellipse helpers), `hidden`.
- Common props: `type`, `default` (use `undefined` for required effect params), `description`, `keyframable` (default true for number, boolean, rotation, translate, transform-origin, scale, uv-coordinate, color; false for array, font-family; enum hold keyframes via `keyframable: true` from 4.0.509 using `Easing.step1`), `defaultKeyframeOutput` (4.0.490: `'linear'` | `'perceptual-scale'` for scale fields), `min`, `max`, `step`, `integer` (4.0.528), `hiddenFromList` (numbers).

### 3.4 Async and render control

#### `delayRender()`, `continueRender()`, `cancelRender()`, `useDelayRender()`
- `delayRender(label?, {timeoutInMilliseconds?, retries?}) => handle`; `continueRender(handle)`; `cancelRender(errorOrString)`.
- Preferred: `const {delayRender, continueRender, cancelRender} = useDelayRender();` + `const [handle] = useState(() => delayRender('label'))`. Future-proof for client-side rendering: the compatibility tables say the global `delayRender()` must be replaced by `useDelayRender()` in client-side rendering (the continueRender page says "Use useContinueRender()"); global imports are marked "discouraged".
- No effect in Studio/Player (use `useBufferState().delayPlayback()` there, or both together).
- Timeout: must clear within 30 s by default (effective message shows 28000 ms). Change globally with `Config.setDelayRenderTimeoutInMilliseconds()` / `--timeout`, or per call `timeoutInMilliseconds` (4.0.140).
- `retries` (4.0.140, default 0): on timeout the whole tab closes and the frame is retried.
- Label (2.6.13) appears in the timeout error; always label.
- Multiple handles allowed; render blocks while any is pending.
- `cancelRender` (3.3.44) stops the render without retries, accepts `Error` (best stack) or string, and throws (code after it does not run). From 4.0.374 it also cancels all pending `delayRender` calls. In `renderMediaOnWeb()`/`renderStillOnWeb()` wrap it in `try/catch` (otherwise unhandled).
- Components exposing `delayRenderTimeoutInMilliseconds` / `delayRenderRetries` props: `<Img>`, `<Video>`, `<Audio>`, `<Html5Audio>`, `<Html5Video>`, `<IFrame>`, `<CanvasImage>`.
- Bugs to avoid: `delayRender()` at module top level (blocks other compositions and the composition list); calling `delayRender()` in the component body (new handle every React render).

```tsx
const {delayRender, continueRender, cancelRender} = useDelayRender();
const [handle] = useState(() => delayRender('Fetching data'));
useEffect(() => {
  fetch(url).then((r) => r.json()).then((d) => { setData(d); continueRender(handle); })
    .catch((err) => cancelRender(err));
}, []);
```

#### `getRemotionEnvironment()` (4.0.25)
- Returns `{isStudio, isRendering, isPlayer, isReadOnlyStudio (4.0.238), isClientSideRendering (4.0.344)}`; all false in plain Node. Prefer the `useRemotionEnvironment()` hook (future-proof). Also available as `isRendering` inside `calculateMetadata`.

#### `<Artifact>` (4.0.176) and emitting artifacts
- `<Artifact filename content downloadBehavior? />` emits an extra file during render. Render it on ONE frame only (`frame === 0 ? <Artifact/> : null`); filenames must be unique (duplicates throw); forward slashes; must match `/^([0-9a-zA-Z-!_.*'()/:&$@=;+,?]+)/g`.
- `content`: `string` | `Uint8Array` (not faster) | `Artifact.Thumbnail` (4.0.290; emits the current frame's image, format decided by `imageFormat`, extension ignored).
- `downloadBehavior` (4.0.296, serverless only): `{type: 'play-in-browser'}` | `{type: 'download', fileName: string | null}`.
- Destinations: CLI/Studio `out/[composition-id]/[filename]`; `renderMedia/renderStill/renderFrames` `onArtifact({filename, content, frame})`; `renderMediaOnWeb/renderStillOnWeb` `onArtifact`; Lambda S3 `renders/[render-id]/artifacts/[filename]` (via `getRenderProgress().artifacts` or `renderStillOnLambda().artifacts`); Cloud Run: not supported. Player/Studio preview: no-op.

### 3.5 Assets, images and media

#### Asset rules (assets.md, getstaticfiles.md)
- Put files in `public/`, reference with `staticFile('logo.png')`. Since 4.0.0 `staticFile()` URI-encodes the name (`my-image#portrait.png` becomes `my-image%23portrait.png`): never encode manually.
- Image sequences: `<Img src={staticFile(`/frame${frame}.png`)} />`.
- CSS: `import './style.css'`. Tailwind/SASS need bundler overrides.
- `import logo from './logo.png'` works for png/svg/jpg/jpeg/webp/gif/bmp, webm/mov/mp4, mp3/wav/aac/m4a, woff/woff2/otf/ttf/eot; max 2 GB; dynamic `require()` is unreliable; prefer `staticFile()`.
- No `fs`, no absolute paths; enumerate with `getStaticFiles()` (3.3.26; moving to `@remotion/studio`): returns `[{name, src, sizeInBytes, lastModified}]` (first 10000 files; before 4.0.64, 1000); only in Studio and during rendering (empty array elsewhere); pass `src` (or `staticFile(name)`), never the bare `name`.
- Always use Remotion components: `<Img>`/`<Gif>` instead of `<img>`, Next `<Image>`, or CSS `background-image`; `<Video>` (`@remotion/media`), `<OffthreadVideo>`, `<Html5Video>` instead of `<video>`; `<Audio>`/`<Html5Audio>` instead of `<audio>`; `<IFrame>` instead of `<iframe>`. They wait for load and sync to the timeline.

#### `<Img>`
- `src` (local via `staticFile` or remote). `effects` (4.0.469): non-empty array renders through `<CanvasImage>` (a `<canvas>`); then `ref, srcSet, sizes, loading, decoding, fetchPriority, useMap, onLoad, onError, onImageFrame, alt` are unsupported and `style.objectFit` (`fill|contain|cover`) controls drawing.
- `cropLeft/Right/Top/Bottom` (4.0.500), `onError` (after retries; you must unmount or change `src`, else timeout), `onImageError` (4.0.526; works in both modes), `crossOrigin` (4.0.526), `maxRetries` (3.3.82, default 2, backoff 1 s, 2 s, 4 s), `pauseWhenLoading` (4.0.111; default false in v4, true in v5), `premountFor/postmountFor/styleWhilePremounted/styleWhilePostmounted` (4.0.497), `delayRenderTimeoutInMilliseconds`, `delayRenderRetries` (4.0.140), inherited `from, durationInFrames, name, showInTimeline, hidden` (4.0.465) and `trimBefore` (4.0.482).
- Since 4.0, an unloadable image with no retries left calls `cancelRender` unless `onError` is handled. Max 2^29 pixels (Chrome limit). Not for GIFs (use `@remotion/gif`).

#### `<CanvasImage>` (4.0.466)
- Static image drawn to a `<canvas>` so `effects` can apply. Remote images need CORS.
- Props: `src`, `effects`, `width`/`height` (default decoded size), `fit` (`'fill'` default | `'contain'` | `'cover'`), `className`, `id`, `style`, `crossOrigin` (4.0.526, default `'anonymous'`), `crop*` (4.0.500), premount props (4.0.495), `onError` (default calls `cancelRender`), `pauseWhenLoading` (4.0.467, default false), `maxRetries` (4.0.467, default 2), `delayRenderRetries`, `delayRenderTimeoutInMilliseconds` (4.0.467), inherited `from, durationInFrames, trimBefore (4.0.482), name, showInTimeline, hidden`; `ref` is `HTMLCanvasElement`.

#### `<AnimatedImage>` (4.0.246)
- Animated GIF/APNG/AVIF/WebP synced to the timeline via `ImageDecoder` (Chrome and Firefox; not Safari). Remote needs CORS.
- Props: `src`, `effects` (4.0.464), `width`, `height`, `fit` (`fill` default), `style` (no width/height), `crop*` (4.0.500), premount props (4.0.497), `loopBehavior` (`'loop'` default | `'pause-after-finish'` | `'clear-after-finish'`), `playbackRate` (default 1), `requestInit` (4.0.471; `signal` ignored), `ref` (canvas), inherited `from, durationInFrames, trimBefore (4.0.482), name, showInTimeline, hidden`. No `onLoad`.

#### `<IFrame>`
- Like `<iframe>`, wrapped in `delayRender` until loaded. The embedded site should not animate on its own. `delayRenderTimeoutInMilliseconds`, `delayRenderRetries` (4.0.140). Not supported in client-side rendering.

#### `<Html5Video>` (formerly `<Video>` from `remotion`)
- Legacy; for new code prefer `<Video>` from `@remotion/media`. Not supported in client-side rendering. All native `<video>` props except `autoplay`, `controls`.
- Props: `src`, `trimBefore`/`trimAfter` (4.0.319, frames at composition fps; `startFrom`/`endAt` deprecated and cannot be mixed), `style`, `volume` (number or `(f) => number`), `loopVolumeCurveBehavior` (4.0.142, `'repeat'` default | `'extend'`), `name` (4.0.71), `playbackRate` (2.2.0; preview throws outside 0.0625..16; reverse unsupported), `preservePitch` (4.0.463, preview only), `muted`, `loop` (3.2.29; without loop the last frame stays), `acceptableTimeShiftInSeconds` (3.2.42, default 0.45), `toneFrequency` (4.0.47, 0.01..2, render only), `audioStreamIndex` (4.0.340, render only), `onError` (from 3.3.89 no throw if passed), `pauseWhenBuffering` (4.0.100; v4 false, v5 true), `showInTimeline` (4.0.122), `delayRender*` (4.0.140), `onAutoPlayError` (4.0.187), `onVideoFrame` (4.0.472), `crossOrigin` (4.0.190; `'anonymous'` default if `onVideoFrame`), `useWebAudioApi` (4.0.306; volume > 1 and iOS volume; needs CORS; on Safari not with `playbackRate`). `allowAmplificationDuringRender` deprecated (4.0.279).
- Add `muted` to silent clips: Remotion then skips downloading the file for audio extraction.

#### `<Html5Audio>` (formerly `<Audio>` from `remotion`)
- Legacy; prefer `<Audio>` from `@remotion/media`. Not in client-side rendering.
- Props: `src`, `volume` (0..1 unless `useWebAudioApi`), `loopVolumeCurveBehavior` (4.0.142), `trimBefore`/`trimAfter` (4.0.319), `playbackRate` (2.2.0), `preservePitch` (4.0.463), `muted` (2.0.0; may change per frame), `name` (4.0.71), `loop` (3.2.29), `toneFrequency` (4.0.47), `audioStreamIndex` (4.0.340), `acceptableTimeShiftInSeconds` (3.2.42), `pauseWhenBuffering` (4.0.111), `showInTimeline` (4.0.122), `delayRender*` (4.0.140), `useWebAudioApi` (4.0.306), `onError` (4.0.326), `crossOrigin`.
- Volume values are linear amplitude scalars (dB = `20 * log10(volume)`).

#### HLS (4.0.454)
- `<Video src="...m3u8">` from `@remotion/media` plays VOD HLS via Mediabunny, in all browsers and during rendering; picks the highest-quality variant automatically; live streams rejected.

#### `@remotion/media-utils`
- `getAudioData(src, {sampleRate?, requestInit?})` returns `{channelWaveforms: Float32Array[], sampleRate, durationInSeconds, numberOfChannels, resultId, isRemote}`. `sampleRate` (4.0.121) default 48000 (before: device-dependent, non-deterministic). `requestInit` (4.0.458). Needs CORS for remote. Throws for files without audio. Memoized by `src` (reload page to clear). Use `useAudioData()` to get delayRender handling.
- `getWaveformPortion({audioData, startTimeInSeconds, durationInSeconds, numberOfSamples, channel = 0, outputRange = 'zero-to-one' | 'minus-one-to-one', normalize = true (4.0.280)})` returns `[{index, amplitude}]`. For frequency bands use `visualizeAudio()`.
- `audioBufferToDataUrl(audioBuffer)` (2.5.7): base64 data URL from an `AudioBuffer` for `<Audio src>`.
- `getImageDimensions(src)` (4.0.143): `{width, height}`, memoized.
- Deprecated: `getAudioDurationInSeconds()` and `getVideoMetadata()` (duration may be `Infinity`; fails on H.265 Linux). Use Mediabunny `getMediaMetadata()` instead.

#### Fonts
- `@remotion/google-fonts` (3.2.40): `import {loadFont} from '@remotion/google-fonts/Inter'`; `loadFont(style?, {weights?, subsets?, document?, ignoreTooManyRequestsWarning?})` returns `{fontFamily, fonts, unicodeRanges, waitUntilDone}`. On 4.x calling it without options loads every style, weight and subset (many requests, possible delayRender timeouts). In 5.0 weights and subsets are required. Also `getInfo()`, `getAvailableFonts()` (about 1400 fonts; `{fontFamily, importName, load}`), `loadVariableFont()`, `loadFontFromInfo()`, `loadVariableFontFromInfo()`. Use `import * as Montserrat from ...` to avoid name clashes. Font picker requires ESM import (CJS throws) and `@remotion/google-fonts` >= 3.3.64.
- `@remotion/fonts` (4.0.164): `loadFont({family, url: staticFile('Inter-Regular.woff2'), weight: '500'})` returns a promise.
- CSS `@import url(https://fonts.googleapis.com/...)` is auto-awaited since 2.2.
- Manual: `new FontFace(name, url(...))` + `delayRender` + `document.fonts.add`.
- Web renderer: fonts inside SVG `<text>` handled via an internal registry from 4.0.525.
- Multi-font projects: one `fonts.ts` exporting `waitForFonts = () => Promise.all([a.waitUntilDone(), b.waitUntilDone()])`; gate text measurement (layout-utils) behind fonts ready (HOC pattern).

#### Lottie, After Effects, Figma
- After Effects: Bodymovin export JSON -> `public/` -> fetch with `staticFile()` inside `delayRender` -> `<Lottie animationData>` from `@remotion/lottie` (+ `lottie-web`). Match composition size/duration to the AE comp (`getLottieMetadata()`). Lottie seeks with `goToAndStop()`; some expressions are not deterministic (can flicker).
- Figma (4.0.495): Copy as SVG then paste into the Studio (most reliable), or paste layers directly (not images), or convert SVG to JSX (SVGR playground) for code.

### 3.6 Effects and canvas visuals

#### Effects (4.0.464)
- Supported: `<Solid>`, `<HtmlInCanvas>`, `<Video>` (`@remotion/media`), `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Gif>`, `<RemotionRiveCanvas>`, `@remotion/shapes` components (4.0.474).
- `effects={[blur({radius: 40})]}`; multiple effects apply in array order; editable in the Studio timeline; every factory accepts `disabled`.
- Imports are per effect: `@remotion/effects/blur`, `/color-correction`, `/lut`, `/color-key`, `/light-leak`, etc.
- `colorCorrection({exposure, contrast, temperature, vibrance, ...})`; single effects `brightness()`, `contrast()`, `saturation()`; `lut({content: cubeFileString})` for `.cube` 3D LUTs (drop `.cube` files into `public/` to preview in the Assets panel). Order: `colorCorrection()` before `lut()`.
- `colorKey({similarity: 0.45})` for greenscreen (WebGL2).
- `lightLeak({seed, hueShift = 0, progress})` (4.0.500, WebGL2): reveals in the first half of `progress`, retracts in the second; `hueShift` 0 yellow/orange, 120 green, 240 blue. Replaces the old `@remotion/light-leaks` package (dropped in 5.0).

#### `createEffect()` (4.0.479)
- `createEffect<Params, State>({type (reverse DNS id), label, documentationLink | null, backend: '2d'|'webgl2'|'webgpu', calculateKey(params), setup(), apply({source, target, state, params, width, height, gpuDevice, flipSourceY}), cleanup(state), schema: InteractivitySchema, validateParams(params)})` returns an `EffectFactory`.
- `disabled` control is added automatically; adjacent effects are grouped by backend while rendering; WebGL/WebGPU need a working `--gl` backend.

#### `<HtmlInCanvas>` (4.0.455)
- Draws live DOM into a canvas for post-processing (2D, WebGL, WebGPU). `<HtmlInCanvas width height onPaint={({canvas, element, elementImage}) => ...} onInit?>`; `ctx.drawElementImage(elementImage, x, y)` returns a transform to apply to `element.style.transform`.
- Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element` enabled (`HtmlInCanvas.isSupported()`); rendering works out of the box (Remotion ships a custom Chrome with the flag) locally, Lambda, Vercel, SSR. WebGL shaders need `--gl=angle` (or `swangle` without GPU). Nesting throws: merge effects in one `onPaint`. Transitions: `zoomBlur()` presentation and custom HTML-in-canvas presentations. Using the raw browser API means you handle `delayRender`.

### 3.7 Rendering, encoding and configuration

#### `remotion.config.ts` (`import {Config} from '@remotion/cli/config'`)
Applies to CLI and Studio only, never to SSR Node APIs (`bundle()`, `renderMedia()`); CLI flags beat config values. Old nested format (`Config.Bundling.*`) deprecated since 3.3.39. The file runs as CommonJS: import ESM inside an async `overrideWebpackConfig` (4.0.117). Custom path via `--config`.

| Setter | Since | Default / values |
|---|---|---|
| `overrideBundlerConfig(fn(config, {bundler}))` | 4.0.498 | shared Webpack+Rspack, runs first |
| `overrideWebpackConfig(fn)` / `overrideRspackConfig(fn)` | 1.1.0 / 4.0.498 | reducer style, curry multiple |
| `setRspack(true)` (alias `setExperimentalRspackEnabled`, 4.0.426) | 4.0.502 | Webpack default |
| `setCachingEnabled` | 2.0.0 | bundle cache |
| `setStudioPort` / `setRendererPort` | 4.0.61 | free port (`setPort` deprecated) |
| `setPublicDir` / `setBundleOutDir` / `setEntryPoint` | 3.2.13 / 4.0.426 / 3.2.40 | |
| `setLogLevel` | 2.0.1 | `error`, `warn`, `info` (default), `verbose` |
| `setConcurrency` | | tip: `os.cpus().length` |
| `setVideoImageFormat` | 4.0.0 | `jpeg` (default), `png` (transparency), `none` |
| `setStillImageFormat` | 4.0.0 | `png` (default), `jpeg`, `pdf`, `webp` |
| `setJpegQuality` | (renamed from `setQuality` in 4.0) | 80 |
| `setScale` | 2.6.7 | 1 |
| `setCodec` | 1.4.0 | `h264` (default), `h265`, `vp8`, `vp9`, `av1`, `prores` (2.1.6), `mp3`/`wav`/`aac` (2.0); GIF output is covered on the separate render-as-gif page (distributed-rendering.md treats GIF as a codec) |
| `setAudioCodec` | | depends on codec; `pcm-16` = uncompressed |
| `setProResProfile` | 2.1.6 | `4444-xq`, `4444`, `hq`, `standard`, `light`, `proxy` |
| `setX264Preset` | doc says "4.2.2" (typo) | `medium` default; `superfast`..`placebo` |
| `setCrf` | 1.4.0 | see CRF table |
| `setVideoBitrate` / `setAudioBitrate` | 3.2.32 | e.g. `'1M'`, `'128K'`; incompatible with crf |
| `setEncodingBufferSize` / `setEncodingMaxRate` | 4.0.78 | e.g. `'10000k'`, `'5000k'` |
| `setGopSize` | 4.0.466 | |
| `setPixelFormat` | | e.g. `yuv420p`, `yuv444p`, `yuva444p10le` |
| `setColorSpace` | present in 4.0.528 typings | `default` (bt601-like), `bt601`, `bt709`, `bt2020-ncl` |
| `setMuted` / `setEnforceAudioTrack` | 3.2.1 | false |
| `setSampleRate` / `setPreviewSampleRate` | 4.0.448 / 4.0.470 | |
| `setForSeamlessAacConcatenation` / `setPreferLosslessAudio` | 4.0.123 | |
| `setFrameRange` | 2.0.0 | `90`, `[0, 20]`, `[100, null]` (4.0.421), `[[0,100],[150,200]]` (4.0.502) |
| `setEveryNthFrame`, `setNumberOfGifLoops`, `setImageSequence` (1.4.0), `setImageSequencePattern` | | |
| `setOutputLocation` | 3.1.6 | `out/{composition}.{container}` |
| `setOverwriteOutput` | | true (since 2.0) |
| `overrideWidth/Height` / `overrideFps/Duration` | 3.2.40 / 4.0.424 | |
| `setDisallowParallelEncoding` | 4.0.315 | false (true = less memory, slower) |
| `setDelayRenderTimeoutInMilliseconds` | 2.6.3 | 30000 |
| `setChromiumOpenGlRenderer` | | see GL table |
| `setChromiumDisableWebSecurity` / `IgnoreCertificateErrors` / `HeadlessMode` | 2.6.5 | |
| `setChromiumDarkMode` | 4.0.381 | |
| `setChromiumMultiProcessOnLinux` | 4.0.42 | recommended in Docker |
| `setChromeMode` | 4.0.248 | `'chrome-for-testing'` for headed |
| `setBrowserExecutable` | 1.5.0 | |
| `setHardwareAcceleration` | 4.0.228 | `disabled` (default), `if-possible`, `required` |
| `setBinariesDirectory` | 4.0.120 | |
| `overrideFfmpegCommand(({type, args}) => args)` | 3.2.22 | discouraged; `pre-stitcher`/`stitcher`; not on Lambda |
| `setDotEnvLocation` | | `.env` |
| `setNumberOfSharedAudioTags` / `setBufferStateDelayInMilliseconds` | 3.3.2 / 4.0.111 | buffer UI delay 300 ms |
| `setMaxTimelineTracks` | 2.1.10 | from 4.0.514 all tracks, virtualized |
| Studio: `setKeyboardShortcutsEnabled` (3.2.11), `setKeyboardShortcuts` (4.0.523), `setInteractivityEnabled` (4.0.487), `setDefaultEditor` (4.0.503), `setDefaultCodingAgent` (4.0.506: `codex`, `cursor`, `copilot`, `claude-code`), `setAllowHtmlInCanvasEnabled` (4.0.447), `setShouldOpenBrowser` (3.3.19), `setWebpackPollingInMilliseconds` (3.3.11), `setAskAIEnabled` (4.0.407), `setForceNewStudioEnabled` (4.0.421), `setIPv4` (4.0.125), `setEnableCrossSiteIsolation` (4.0.306), `setBeepOnFinish` (4.0.84), `addElementLibrary` (4.0.517), `setExperimentalKeepAudioContextAlive` (4.0.508), `setAudioLatencyHint` (4.0.303) | | |
| Lambda/cloud: `setLambdaInsights` (4.0.115), `setDeleteAfter` (4.0.32), `setEnableFolderExpiry` (4.0.32), `setEnableCancellation` (4.0.515), `setPublicLicenseKey` (4.0.398) | | |
| Benchmark: `setBenchmarkRuns`, `setBenchmarkConcurrencies` (4.0.430) | | |

#### Codecs and quality (encoding.md)
| Codec | Ext | Size | Speed | Browser support | HW accel |
|---|---|---|---|---|---|
| h264 (default) | .mp4 .mov .mkv | medium | very fast | very good | macOS, Linux, Windows NVIDIA |
| h265 | .mp4 .hevc | medium | fast | very poor | macOS, Linux, Windows NVIDIA |
| vp8 | .webm | small | slow | okay | no |
| vp9 | .webm | very small | very slow | okay | no |
| av1 | .mp4 .webm .mkv | very small | very slow | okay | no (not on Lambda, not Linux ARM64 GNU) |
| prores | .mov | large | fast | none | macOS |

CRF (lower = better; +6 roughly halves size): h264 1..51 default 18; h265 0..51 default 23; vp8 4..63 default 9; vp9 0..63 default 28; av1 0..63 default 30. Choose the highest CRF that still looks good. Bitrate options are an alternative (incompatible with crf). Audio-only: codec `mp3`, `wav`, `aac` (quality settings ignored). ProRes default audio is `pcm-16` since 4.0 (was aac). GIFs have no audio and no crf. File extension picks the default codec; container derives from extension. Audio codec flag since 3.3.42.

#### Hardware-accelerated encoding (4.0.228)
- macOS VideoToolbox: ProRes (4.0.228), H.264/H.265 (4.0.236). Linux/Windows NVENC (4.0.484; NVIDIA GPU, driver 525+, bundled FFmpeg on x64 only; H.264/H.265 only).
- `hardwareAcceleration: 'disabled' | 'if-possible' | 'required'` (`--hardware-acceleration`, Studio Advanced tab, config). Not on Lambda/Cloud Run.
- No crf with HW encoders; files are larger by default: use `--video-bitrate` (8M is close to software H.264 Full HD size). Verbose log shows `Encoder: h264_videotoolbox, hardware accelerated: true` style lines.

#### OpenGL backend `--gl` (gl-options.md, gpu.md)
| Value | Notes |
|---|---|
| `null` | 4.0 local default, Chrome decides (often GPU disabled headless) |
| `angle` | 5.0 default; best on desktop with WebGL/WebGPU/Three.js; known memory leaks on long renders (split them); fails on GitHub Actions (no GPU) in 4.0 |
| `angle-egl` | 4.0.52; Linux cloud GPU |
| `egl`, `swiftshader` | |
| `vulkan` | 4.0.41 |
| `swangle` | default on Lambda and Cloud Run; recommended without GPU (slow) |
- GPU-accelerated content: WebGL (Three, Skia, P5, Mapbox), video decoding, `box-shadow`, `text-shadow`, linear/radial gradients, `filter: blur()`/`drop-shadow()`, `transform`, many 2D canvas operations. Headless Chrome disables the GPU unless `--gl` is set. Lambda has no GPU. Most renders do not get faster with a GPU.

#### Chromium flags (2.6.5+)
- `chromiumOptions.disableWebSecurity` / `--disable-web-security` (disables CORS; adds `--user-data-dir`), `ignoreCertificateErrors`, `headless: false` (needs `chromeMode: 'chrome-for-testing'` or a desktop `browserExecutable`; no headed mode on Lambda/Cloud Run/Vercel), `gl`, `userAgent` (3.3.83), `darkMode` (4.0.381), `enableMultiProcessOnLinux` (4.0.42).

#### Environment variables (2.1.2)
- CLI: only `REMOTION_`-prefixed variables reach the bundle (`REMOTION_MY_VAR=x npm run dev`, read `process.env.REMOTION_MY_VAR`). `.env` in the Remotion root is read by the CLI, also `.env.local` from 4.0.110 (`--log=verbose` shows which). Node APIs do not read `.env`: pass `envVariables: {...}` to `renderMedia()`/`renderMediaOnLambda()`/`renderMediaOnVercel()`.

#### `bundle()` (`@remotion/bundler`) and bundler overrides
- `bundle({entryPoint (absolute), onProgress(0..100), webpackOverride, bundlerOverride (4.0.498), rspackOverride (4.0.498), outDir, enableCaching, publicPath (default './' from 4.0.497, earlier '/'), rootDir (3.1.6), publicDir (3.2.13), onPublicDirCopyProgress (3.3.3), onSymlinkDetected (3.3.3), ignoreRegisterRootWarning (3.3.46), rspack (default false), askAIEnabled, keyboardShortcutsEnabled})` returns the output directory.
- Call once per source change, never per video; cannot run inside a serverless function. It does not read `remotion.config.ts`: share override functions via a module imported in both places. Legacy positional signature removed in 5.0.
- Rspack (4.0.426 experimental; will become the default and eventually the only bundler): `Config.setRspack(true)`, `--rspack`, `bundle({rspack: true})`. Webpack and Rspack plugins are not interchangeable.
- Snippets documented: MDX, PostCSS, SVGR, GLSL (then delete `node_modules/.cache`), async WebAssembly (shared override), sync WebAssembly (Webpack only, use `lazyComponent`), `jsxImportSource` (esbuild loader for Webpack; `builtin:swc-loader` for Rspack), Tailwind via `@remotion/tailwind-v4`, SCSS via `@remotion/enable-scss`, legacy Babel via `@remotion/babel-loader` `replaceLoadersWithBabel()` (default transpilers: esbuild-loader for Webpack, SWC for Rspack).

#### CLI (`npx remotion ...`)
- Commands: `studio`, `render`, `still`, `compositions`, `lambda`, `bundle`, `browser` (`browser ensure`), `cloudrun`, `benchmark`, `skills`, `versions`, `upgrade`, `add`, `gpu`, `ffmpeg`, `ffprobe`, `help`. Bun runtime: `remotionb` (4.0.118). Deno (unsupported): `remotiond` (with `--allow-env --allow-read --allow-write --allow-net --allow-run --allow-sys`).
- FFmpeg is bundled since 4.0 (no install; `ffmpegExecutable` options removed). At the 4.0 launch the bundled binaries (6.0 line) only understood H.264, H.265, VP8, VP9 and ProRes; AV1 was added later (encoding.md) but is missing on Lambda and Linux ARM64 GNU. Use `npx remotion ffmpeg` / `npx remotion ffprobe` for probing.
- New project: `npx create-video@latest --yes --blank my-video` (Tailwind + blank + Agent Skills), `npx remotion skills add`, `npm run dev`.
- System requirements (docs): Node or Bun minimums, macOS 15+, Linux glibc 2.35+, Alpine and nixOS unsupported.

#### Distributed rendering (combine chunks yourself)
- `selectComposition()` once; equal frames per chunk except the last; same options for every chunk; same `inputProps`; `frameRange` per chunk (0-based, inclusive to `durationInFrames - 1`); `compositionStart` = first frame of the overall range; `numberOfGifLoops: null`; `enforceAudioTrack: true`; codec `h264-ts` for h264/GIF chunks; if >= 4 frames per chunk and audio codec not aac: `audioCodec: 'pcm-16'`, `forSeamlessAacConcatenation: false`, else keep codec and `forSeamlessAacConcatenation: true`; `separateAudioTo`. Then `combineChunks({videoFiles, audioFiles, outputLocation, codec: 'h264', framesPerChunk, fps, compositionDurationInFrames, frameRange?, preferLossless?, audioCodec?, audioBitrate?, numberOfGifLoops?, everyNthFrame?})`. Lambda already implements all of this and is recommended.

#### Docker
- Base `node:22-bookworm-slim`; apt install `libnss3 libdbus-1-3 libatk1.0-0 libgbm-dev libasound2 libxrandr2 libxkbcommon-dev libxfixes3 libxcomposite1 libxdamage1 libatk-bridge2.0-0 libpango-1.0-0 libcairo2 libcups2`; copy `package.json`, lockfiles, `tsconfig.json`, `remotion.config.*`, `src`, `public`; install deps; `RUN npx remotion browser ensure`; render with `chromiumOptions: {enableMultiProcessOnLinux: true}`. Emoji: `fonts-noto-color-emoji`; CJK: `fonts-noto-cjk`. Give CPUs: `--cpus=16 --cpuset-cpus=0-15`. Do not use Alpine (Rust part >10 s slower to start, Chrome versions not pinnable). Packages deliberately unpinned.

#### Client-side rendering (`@remotion/web-renderer`, stable 4.0.491)
- `renderMediaOnWeb({composition: {component, durationInFrames, fps, width, height, calculateMetadata: null, id}, inputProps})` returns `{getBlob}`; `renderStillOnWeb`. WebCodecs via Mediabunny, no bundling, subset of HTML supported. Chrome 94+, Firefox 130+, Safari 26+. Always sends telemetry (use a license key or `"free-license"`). Studio "Render in browser" from 4.0.491. `<Html5Video>`, `<Html5Audio>`, `<IFrame>` not supported; transparent ProRes not possible client-side.

#### Cloud options (compare-ssr.md, lambda.md, cloudrun.md)
- Lambda: recommended default; distributed, fastest; videos under ~80 min Full HD (15 min AWS timeout); 10 GB storage so output about 5 GB (~2 h Full HD); 1000 concurrent lambdas per region default; no GPU; no AV1; webhooks, cost estimation, PHP/Go/Python/Ruby clients.
- Vercel Sandbox: simplest for Vercel users; functions up to 800 s, use `detached: true` + `getRenderProgress()` for longer.
- Cloud Run: Alpha, not actively developed; 32 GB RAM, 8 vCPU, 60 min; no artifacts.
- Own Node server: cheapest compute, you handle queueing, spikes, progress, logging, provisioning.
- Azure Container Apps and Cloudflare Containers: community/demo guides only.

#### HDR
- Chrome renders in sRGB (SDR). HDR sources are tone mapped: `<Video>`/`<Html5Video>` by the browser (`--gl=angle` gave much better colors on macOS), `<OffthreadVideo>` via FFmpeg `zscale` (disable with `toneMapped={false}`). Do not output HDR: `--color-space=bt2020-ncl` only tags the file and looks overexposed.

### 3.8 Tooling and integrations (brief)
- `@remotion/codemods` (4.0.527, draft): in-memory source edits. `CodemodProject {rootDir, files}`; `getJsxNodes()`, `getJsxNodeProps({keys: ['style.opacity']})` (static vs keyframes vs computed), `updateJsxNodeProps()`, `applyCodemodChanges()` (checks `previousContents`; supports undo/redo by swapping), `nodePathRemappings`, effect references; registration edits for `Composition`, `Still`, `Folder` (4.0.528 node editing APIs).
- `@remotion/canvas` (4.0.527, experimental): `<Canvas controller showOutlines component ...>` preview + layer list; `useCanvasController`, `useCanvasSelection`, `useCanvasSequenceHover`, `getCanvasSequenceNodePathInfo`, `controller.overrides` for drag previews. `<Sequence layout="none">` has no outline.
- `@remotion/browser-bundler` (4.0.527, draft, Chrome only): compile a virtual project in the browser (`createBrowserBundler().bundle({project})`, `loadBrowserBundle`, `getBrowserComposition` runs calculateMetadata and merges props); requires COOP/COEP headers and `crossOriginIsolated`; npm deps via esm.sh; no `public/`/`staticFile()`; trusted code only (`Function` eval, needs `'unsafe-eval'`). The static-files `workerUrl` setup is 4.0.529 (NOT in 4.0.528).
- ESLint: `@remotion/eslint-config-flat` for ESLint 9 (`config` or `makeConfig({remotionDir})`); `@remotion/eslint-config` legacy (ESLint 7.15..8 on Remotion 4); `@remotion/eslint-plugin` (`remotion.flatPlugin` or `plugin:@remotion/recommended`).
- Electron: render in the main process over IPC; bundle during packaging (never `bundle()` at packaged runtime); `binariesDirectory` pointing into `app.asar.unpacked`; `ensureBrowser()` early or package the browser (`REMOTION_ELECTRON_PACKAGE_BROWSER=true`, not for universal macOS builds); match Linux compositor (gnu vs musl).
- Angular: React wrapper component with `createRoot`, `tsconfig` `"jsx": "react"`, Player inside.
- Timeline editors: `Item`/`Track` types -> tracks of `<Sequence key={item.id} from durationInFrames>` inside `<AbsoluteFill>`; pass `tracks` as memoized `inputProps` to the `<Player>`. Paid: Editor Starter, Timeline component (remotion.pro), React Video Editor, DesignCombo.
- OpenTimelineIO export: Remotion publishes a full agent skill (`remotion-opentimeline`) in `export-opentimeline.md` (see recipes 4.12).
- Maps: MapLibre GL + Turf (see recipe 4.10). GSAP: `@remotion/gsap` (4.0.517) builds a paused timeline seeked to the frame (install `gsap`). `@remotion/mac-cursors` (4.0.513). `@remotion/animated-emoji` (4.0.187, CC BY 4.0 emoji). `@remotion/install-whisper-cpp` (4.0.115: `installWhisperCpp({to, version: '1.5.5'})`, `downloadWhisperModel({model: 'medium.en', folder})`, `transcribe({..., tokenLevelTimestamps: true})` on 16 kHz WAV, `toCaptions()`). `@remotion/elevenlabs` (4.0.443) converts ElevenLabs STT to `Caption[]`.
- Measuring DOM: `rect = el.getBoundingClientRect()` is affected by the preview `scale()`: divide by `useCurrentScale()` (4.0.111). Before 4.0.103 first-effect measurements could be 0.
- `@remotion/licensing` (4.0.237): pass `licenseKey` to `renderMedia/renderStill/renderMediaOnLambda/renderStillOnLambda/renderMediaOnVercel`; voluntary below 5.0 except web-renderer (always sends); telemetry never blocks a render.
- Detect a Remotion video: metadata `comment=Made with Remotion 4.0.x` (`ffprobe`), `window.remotion_imported` in DevTools.

### 3.9 Migration landmarks that affect code written today
- 2.0: sequences were 1 frame too long in 1.x (fixed); `inputProps` naming; overwrite default.
- 3.0: `renderFrames/renderStill` take `composition` (with `id`), `serveUrl` replaces `webpackBundle`; errors reject.
- 4.0: config import `@remotion/cli/config` and flattened options; `setVideoImageFormat`/`setStillImageFormat`; `quality` -> `jpegQuality`; FFmpeg bundled; `logLevel: 'verbose'`; `<Img>`/`<Html5Audio>` cancel the render on load failure; `staticFile()` encodes; `defaultProps` required; props must be `type`; `TComposition` needs a schema generic (`AnyComposition` for generic); `composition.props` vs `inputProps`; ProRes pcm audio; `<MotionBlur>` -> `<Trail>`; `getParts` -> `getSubpaths`; `parallelism` -> `concurrency`; `onSlowestFrames` in the return value; `z` no longer exported by `remotion`.
- 5.0 (planned, not active on 4.0.528): Sequences auto-premount `fps` frames (opt out `premountFor={0}`); `bt709` default color space; `angle` GL default; `selectComposition()`/`getCompositions()` require `inputProps`; options-object `bundle()`/`getCompositions()`; `visualizeAudio` `optimizeFor: 'speed'` default; `TransitionSeries` drops `layout="none"`; `measureSpring` drops `from/to`; path sampling returns `null` past the end; Lambda `overwrite: true`, `x264Preset: 'veryfast'`, `diskSizeInMb: 10240`, client APIs from `@remotion/lambda/client`; Cloud Run `maxInstances` 5; google-fonts weights+subsets required; `validateFontIsLoaded` default true; Player `numberOfSharedAudioTags` 0; `pauseWhenBuffering`/`pauseWhenLoading` default true; `@remotion/light-leaks`, `@remotion/starburst` -> `@remotion/effects`; `@remotion/media-parser`, `@remotion/webcodecs` -> Mediabunny; `getVideoMetadata()` removed from renderer; telemetry mandatory for company licenses.

---

## 4. Recipes

### 4.1 Core motion patterns
- **Fade in (clamped):** `interpolate(frame, [0, 20], [0, 1], {extrapolateRight: 'clamp'})`.
- **Fade in and out with shaped edges:** 4-keyframe interpolate with per-segment easing (3.1 example). Guard: only build `[0, a, N-1-b, N-1]` when `N - 1 - b > a`.
- **Pop in with spring:** `const s = spring({fps, frame}); scale: s` (default overshoot = lively). For calm UI: `config: {damping: 200}`.
- **Enter + exit in one value:** `enter - exit` (3.1 animation math).
- **Map spring to any property:** `const x = interpolate(spring({fps, frame}), [0, 1], [0, 200])`.
- **Delay / stagger:** `spring({fps, frame: frame - delay})` or `spring({..., delay})`; per item `frame - i * 5`. Dataset example: logo scale spring delayed 10 frames, title slides `translateY` 10 -> 0 over frames 20..30, subtitle opacity 0 -> 1 over 30..40 (clamped). This is a clean staggered title reveal.
- **Exact-length spring:** pass `durationInFrames` to `spring()`; or measure with `measureSpring({fps, config})` to size the Sequence (damping 200 at 30 fps = 23 frames).
- **Scale that looks linear:** `output: 'perceptual-scale'` (visible area grows linearly).
- **Transform strings:** interpolate `scale: '1' -> '2 3'`, `translate: '0px 0px' -> '100px 50px'`, `rotate: '0deg' -> '90deg'`, `transformOrigin: 'left top' -> 'right bottom'`; apply as separate style properties (also the Studio-editable way).
- **Spring-shaped keyframes:** `easing: Easing.spring({damping: 200, durationRestThreshold: 0.03})`; chain segments with `allowTail: true` so motion overlaps smoothly (3.1 example).
- **Hold / discrete switches:** `interpolate(frame, [0, 100], ['default', 'ne-resize'], {easing: Easing.step1})`.
- **Stop-motion / "on twos" feel:** `posterize: 2` or `3` on `interpolate`/`interpolateColors`.
- **Color shift:** `interpolateColors(frame, [0, 60], ['black', 'white'], {easing: Easing.in(Easing.quad)})`; add a mid stop for saturated hue changes (sRGB blending).
- **Camera push-in (perspective-like):** interpolate a distance 1 -> tiny value and render `scale(1 / distance)` (examples/timing-functions CameraApproach): accelerates naturally as it approaches.
- **Speed ramp / time remapping:** accumulate speed per frame and feed the result to `interpolate` (deterministic because it recomputes from 0 each frame):

```tsx
const remapSpeed = (frame: number, speed: (f: number) => number) => {
  let passed = 0;
  for (let i = 0; i <= frame; i++) passed += speed(i);
  return passed;
};
const accelerated = remapSpeed(frame, (f) => 10 ** interpolate(f, [0, 60], [-1, 4]));
const y = interpolate(accelerated, [0, 60], [0, -200]);
```

- **Reusing CSS @keyframes deterministically:** pause the CSS animation and scrub it with a negative delay driven by the frame (examples/css-animation-play-state):

```tsx
const progress = interpolate(frame, [0, fps * 1], [0, 1], {extrapolateRight: 'clamp'});
<div className={styles.box} style={{animationPlayState: 'paused', animationDelay: `${progress * -1}s`}} />
```

### 4.2 Structure and timing
- **Layer stack:** background `<AbsoluteFill>` first, overlays later; time-limit a layer with `<AbsoluteFill from={60} durationInFrames={40}>` (4.0.501+).
- **Repeating motif:** `<Loop durationInFrames={50} times={3}>`; vary per repetition with `Loop.useLoop().iteration` (e.g. color index or deterministic offset).
- **Freeze frame / hold:** `<Sequence freeze={30}>` (preferred) or `<Freeze frame={30} active={(f) => f < 30}>`.
- **Speed up a looped child:** `<Loop durationInFrames={60} playbackRate={2}>` (4.0.528).
- **Organize many variants:** `<Folder name="Social">` with one `<Composition>` per aspect ratio.

### 4.3 Data-driven and dynamic videos
- **Duration from a media file:** `calculateMetadata` + Mediabunny: `new Input({formats: ALL_FORMATS, source: new UrlSource(src)})`, `computeDuration()`, `getPrimaryVideoTrack()`, `computeFrameRateMetrics().bestGuessFrameRate` (only if `probedPacketCount >= 2`); `durationInFrames: Math.floor(seconds * fps)`.
- **API data into props:** fetch in `calculateMetadata` (runs once, not per tab), type props with a nullable `data` field and throw in the component if `null`; pass `abortSignal`; debounce in Studio with a `waitForNoInput(signal, 750)` helper that skips waiting when `getRemotionEnvironment().isRendering`.
- **Batch render a dataset:** `bundle()` once, then for each entry `selectComposition({serveUrl, id, inputProps: entry})` and `renderMedia({composition, serveUrl, codec: 'h264', outputLocation: `out/${entry.name}.mp4`, inputProps: entry})`. Render sequentially (one render already uses the whole machine). CSV: convert to JSON first.
- **Per-composition render defaults:** return `defaultCodec`, `defaultOutName`, `defaultPixelFormat`, `defaultVideoImageFormat`, `defaultProResProfile`, `defaultSampleRate` from `calculateMetadata`.

### 4.4 Audio
- **Volume fade:** `volume={(f) => interpolate(f, [0, 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}` (`f` is relative to the media's start).
- **Trim:** `trimBefore={60} trimAfter={120}` at 30 fps plays source seconds 2..4 (2 s). Do not mix with deprecated `startFrom/endAt`.
- **Looping music bed with fade curve per loop:** `loop` + `loopVolumeCurveBehavior="repeat"` (or `"extend"` for one continuous curve).
- **Pitch:** `toneFrequency` (render only, 0.01..2); `playbackRate` preserves pitch in renders.
- **Multi-language track:** `audioStreamIndex={1}` (render only).
- **Silent B-roll:** add `muted` to videos without useful audio (faster renders, fewer FFmpeg inputs).
- **Generated tone/sound design:** `OfflineAudioContext` -> `startRendering()` -> `audioBufferToDataUrl()` -> `<Audio src={dataUrl}>` with `delayRender` around generation.
- **Waveform bars:** `getAudioData(staticFile('music.mp3'))` (or `useAudioData`) then `getWaveformPortion({audioData, startTimeInSeconds: frame / fps, durationInSeconds: 1, numberOfSamples: 32})` and map `amplitude` to bar heights.

### 4.5 Images, video and compositing
- **Image sequence playback:** `staticFile(`/frame${frame}.png`)` (exported from After Effects/Rotato).
- **Animated GIF/WebP/APNG with timeline sync:** `<AnimatedImage src loopBehavior="pause-after-finish" playbackRate={0.5} />` (Chrome/Firefox); `<Gif>` for Safari-compatible GIF.
- **Heavy asset appearing mid-video:** premount it: `premountFor={fps}` on `<Img>`/`<CanvasImage>`/`<AnimatedImage>`/`<AbsoluteFill>`/Sequence so decoding happens before it is visible (not automatic on 4.0.528).
- **Greenscreen:** `<Video src effects={[colorKey({similarity: 0.45})]} />` over a background layer.
- **Color grade:** `effects={[colorCorrection({exposure: 0.25, contrast: 1.1, temperature: 0.1, vibrance: 0.2}), lut({content: cubeText})]}`.
- **Blur/filters on images:** `<Img effects={[blur({radius: 8})]} />`.
- **Custom pixel effect:** `createEffect` 2d example maps pixels to the nearest palette color (`paletteMap({palette, amount})`).
- **HTML post-processing (glitch, CRT, magnifier, vintage):** `<HtmlInCanvas onPaint>` with 2D filters or WebGL shaders; render with `--gl=angle`.
- **Light leak transition:** `<TransitionSeries.Overlay durationInFrames={20}>` containing `<Solid width height effects={[lightLeak({progress: interpolate(frame, [0, durationInFrames - 1], [0, 1], clamp)})]}/>` between two `TransitionSeries.Sequence`s: the leak peaks at the cut and does not shorten the timeline. Keep the progress expression inline so the Studio can edit it.
- **HDR footage:** tone map (default in OffthreadVideo), try `--gl=angle`, output SDR.
- **HLS source:** `<Video src="https://.../index.m3u8">` (VOD only).

### 4.6 Text and fonts
- Google font: `const {fontFamily} = loadFont('normal', {weights: ['400', '700'], subsets: ['latin']});` at module level, then `style={{fontFamily}}`.
- Local font: `loadFont({family: 'Inter', url: staticFile('Inter-Regular.woff2'), weight: '500'})` from `@remotion/fonts`.
- Wait for fonts before `measureText()`/`fitText()`/`fillTextBox()`.
- Bangla/Bengali and other scripts: `Noto Sans Bengali` and `Hind Siliguri` are in the docs' top-250 Google Fonts list; load the right `subsets` (e.g. `bengali`) explicitly. In Docker install `fonts-noto-color-emoji` / `fonts-noto-cjk`.
- Popular shortlist (docs "top 25"): Inter, Kanit, Lato, Lora, Merriweather, Montserrat, Noto Sans (+JP/KR/TC), Nunito, Nunito Sans, Open Sans, Oswald, PT Sans, Playfair Display, Poppins, Raleway, Roboto (+Condensed/Mono/Slab), Rubik, Ubuntu, Work Sans.

### 4.7 Emitting side files
- Captions file: `frame === 0 ? <Artifact filename="captions.srt" content={srt} /> : null`.
- Thumbnail: `<Artifact filename="thumbnail.jpeg" content={Artifact.Thumbnail} />` on the chosen frame; format follows `imageFormat`.
- Metadata JSON for pipelines: `content={JSON.stringify({...})}`; receive with `onArtifact`.

### 4.8 Render settings by deliverable
- Social/web MP4: `codec h264`, `pixelFormat yuv420p`, `colorSpace 'bt709'` (explicit on 4.0.528), CRF 18 default (lower e.g. 16 for crisper gradients; higher for smaller files), `x264Preset` slower for smaller size at same quality.
- Editor handoff: `prores` (`hq`, or `4444` / `4444-xq` for alpha), audio pcm by default.
- Transparent overlay (lower third): `--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png` (as in the OTIO skill). Not possible client-side.
- Small web loop: `vp9` (slow encode) or GIF (`--codec=gif`, `numberOfGifLoops`, no crf, no audio).
- Audio only: `mp3`, `wav` (16-bit PCM from Remotion), `aac`.
- Faster local encode on Mac: `hardwareAcceleration: 'if-possible'` + `videoBitrate: '8M'` for H.264 Full HD.
- Higher resolution output from a 1080p design: `--scale=2` (vector content re-rendered sharply).

### 4.9 Debugging timeouts and flicker
- Label every `delayRender`, add `retries` for flaky CDNs, raise per-call `timeoutInMilliseconds` for slow loads, `--log=verbose` to see browser logs.
- If an animation flickers only in renders: search for CSS transitions/animations, `Math.random`, `Date`, state across frames, `useEffect` with `frame` deps that fetch, unloaded fonts, CSS `background-image`/`mask-image` assets.
- `--concurrency=1` is a last-resort hack (slower, timing still not guaranteed, blocks Lambda). Legit use: WebGL-heavy maps.

### 4.10 Maps (MapLibre + Turf)
- Container `<div style={{width, height, position: 'absolute'}}>`; `setWorkerUrl` via blob import of the unpkg worker; `new maplibregl.Map({container, style, center, zoom, interactive: false, attributionControl: false, fadeDuration: 0, canvasContextAttributes: {preserveDrawingBuffer: true}})`; `map.on('load', () => { map.jumpTo(...); map.once('idle', () => continueRender(handle)); })`. No `map.remove()` cleanup.
- Route line: GeoJSON `LineString` source + line layer; geodesic arcs via `turf.greatCircle(from, to, {npoints: 100})`; animate with `turf.lineSliceAlong(route, 0, Math.max(0.001, length * progress))` and `source.setData()`.
- Camera: per frame `delayRender`, compute progress with `Easing.inOut(Easing.cubic)`, `map.jumpTo(map.calculateCameraOptionsFromTo(cameraLngLat, altitudeMeters, targetLngLat))`, `map.once('idle', continue)`, `map.triggerRepaint()`. Animate altitude separately for zoom-out/travel/zoom-in.
- Markers: circle layer + symbol layer with `text-field`, halo.
- Render: `--gl=angle --concurrency=1`.

### 4.11 Integrations
- Lottie from AE: Bodymovin (enable "Allow Scripts to Write Files"), export JSON, `fetch(staticFile('animation.json'))` inside delayRender, `<Lottie animationData>`.
- Figma: Copy as SVG -> paste into Studio or convert to JSX.
- GSAP: `@remotion/gsap` (paused timeline seeked per frame). Never let GSAP's own ticker run.
- Local transcription: install whisper.cpp 1.5.5 + `medium.en`, 16 kHz WAV, `tokenLevelTimestamps: true`, `toCaptions()`.

### 4.12 Handing off to an NLE (OpenTimelineIO skill, summarized)
- Read the timeline from code: composition fps/size/duration (after `calculateMetadata`), absolute start of each media element = sum of enclosing `<Sequence from>` (Series/TransitionSeries accumulate durations), `trimBefore`/`trimAfter` for source in-points.
- OTIO `RationalTime` uses composition fps; `source_range.start_time = trimBefore`; gaps via `Gap.1`; overlapping clips need separate tracks.
- Native clips: `<Video>`, `<Audio>`, `<OffthreadVideo>`, `<Img>`. Everything else (text, shapes, springs, effects, transitions, playbackRate, volume curves, canvas/three/lottie/skia) becomes a baked derivative or a rendered fallback: transparent ProRes 4444 overlays, opaque ProRes `light` + `yuv422p10le` intervals, WAV stems. Never keep both a fallback and what it replaces.
- Localize all media next to the `.otio` (download remotes, copy `public/` files, `pathToFileURL()` for `target_url`), probe with `npx remotion ffprobe`, validate JSON. Resolve 18.5+ and Premiere 25.6+ import OTIO directly.

---

## 5. Performance and render stability

- **Concurrency model:** many tabs render frames in parallel (Lambda up to 200x). Anything done in component effects runs in every tab: API calls multiply (rate limits), data must be identical across tabs. Fetch in `calculateMetadata` instead.
- **Determinism breakers:** CSS transitions/animations, `Math.random()` (use `random(seed)`), `Date.now()`, timers, rAF-driven libraries without seeking, state accumulated across renders, relying on frame order, animating while paused, website animations inside `<IFrame>`, Lottie expressions, data that differs per tab.
- **Loading breakers:** native `<img>/<video>/<audio>/<iframe>`, CSS `background-image` and `mask-image` for assets, fonts not awaited, measuring text before fonts load, custom async without `delayRender`.
- **Timeout budget:** 30 s per frame by default (28 s effective). Heavy first-frame work (fonts with all weights, big JSON, map tiles) can exceed it; restrict google-fonts weights/subsets, move work to `calculateMetadata`, raise timeouts deliberately, add `retries`.
- **Premounting:** not automatic on 4.0.528. Without `premountFor`, a heavy asset mounted exactly at its start frame can show a blank/black frame in preview; add `premountFor={fps}` (Sequence and the components listed above).
- **Big props:** huge `defaultProps`/input props are slow (serialized to every tab); pass URLs/IDs and fetch in `calculateMetadata`; warning above 10 MB.
- **Video tags:** many `<Html5Video>` tags stutter; prefer `<Video>` from `@remotion/media` (or `<OffthreadVideo>`). Mute silent videos to skip audio download and FFmpeg inputs (also avoids Windows ENAMETOOLONG).
- **GPU:** headless Chrome disables GPU unless `--gl` is set; `angle` leaks memory on long renders (split into parts with frame ranges); WebGL-heavy scenes may need `--concurrency=1`; Lambda is CPU only (`swangle`).
- **Encoding:** `setDisallowParallelEncoding(true)` lowers memory at the cost of speed; hardware encoding only accelerates encoding (not frame rendering); CRF vs bitrate are exclusive.
- **Machine usage:** one render already saturates the machine: render dataset items sequentially; `setConcurrency(os.cpus().length)` for max speed (system slows down); in Docker grant CPUs and enable multi-process on Linux.
- **Bundling:** bundle once per code change, reuse the serve URL for all renders; Rspack speeds up bundling (4.0.426+); `lazyComponent` reduces Studio startup (not under Bun).
- **Memoized helpers:** `getAudioData`, `getImageDimensions`, `getVideoMetadata` cache by `src` for the page lifetime (a changed file with the same name is not re-read until reload). Always pass a fixed `sampleRate` (default 48000 since 4.0.121) for deterministic waveform data.
- **Limits:** Chrome images max 2^29 pixels; Lambda 10 GB disk, ~5 GB output, 15 min timeout, 1000 concurrency default; Cloud Run 32 GB/8 vCPU/60 min; Vercel functions 800 s; `getStaticFiles` returns the first 10000 files.
- **Platform notes:** Alpine adds >10 s startup (Rust compositor); Windows command line limit 8192 chars (too many audio layers).

---

## 6. Errors and fixes

| Symptom / message | Cause | Fix |
|---|---|---|
| `A delayRender() "label" was called but not cleared after 28000ms` | handle never continued, slow asset, font load, map idle never fired | continue in every path, `cancelRender` on errors, raise `timeoutInMilliseconds` or `--timeout`, add `retries`, label handles, load fewer font variants |
| Other compositions blocked / composition list hangs | `delayRender()` at module top level | move into component with `useState(() => delayRender())` |
| Timeouts after many re-renders | `delayRender()` in component body creates a handle per React render | `useDelayRender()` + `useState` initializer |
| `inputRange must be strictly monotonically increasing but got [...]` | keyframes collide (e.g. fade in/out longer than the composition) | compute keyframes safely, clamp durations |
| `When easing is an array, it must have one entry per segment...` | wrong easing array length | `inputRange.length - 1` entries |
| `Non-numeric strings can only be interpolated using Easing.step1` | interpolating arbitrary strings | use step1 in every segment, or numeric/CSS-unit strings |
| `Cannot interpolate ... values with different units on axis N` | `'0px'` vs `'10%'` in one interpolation | same units per component |
| `extrapolateLeft: "identity" is not supported for non-numeric strings` | identity with strings | use clamp/extend |
| `input can not be undefined` / `Cannot interpolate an input which is not a number` | undefined frame/driver | check driver value |
| `invalid color string ... provided` (interpolateColors) | unsupported color syntax | use supported formats (names, hex, rgb, hsl, oklch, oklab, lab, lch, hwb) |
| Flicker or choppy motion only in renders | multi-tab non-determinism or assets not awaited | see section 5; `--concurrency=1` only as a last resort |
| Render aborted when an image fails | `<Img>` calls `cancelRender` when retries are exhausted (since 4.0) | fix URL/CORS, `maxRetries`, handle `onError`/`onImageError` and unmount or swap `src` |
| CORS errors (`No 'Access-Control-Allow-Origin' header`, preflight, `Method PUT is not allowed`, private network) | server headers | read the second half of Chrome's message; add `Access-Control-Allow-Origin`, answer `OPTIONS` preflight, `Access-Control-Allow-Methods`, `Access-Control-Allow-Private-Network: true`; `application/json` POST triggers preflight; or `--disable-web-security` during renders; disable cache in DevTools |
| `getAudioData` throws | file has no audio track | check `audioCodec` via metadata first |
| Video duration `Infinity` | webm without duration header (`getVideoMetadata`) | re-encode with FFmpeg or use Mediabunny |
| Artifact error | same filename emitted on several frames | render `<Artifact>` on one frame; unique names |
| `Command failed with ENAMETOOLONG: ffmpeg ...` (Windows) | too many audio inputs | mute silent videos, render on macOS/Linux/WSL, or render parts (`--frames`) and concat |
| Type error on `defaultProps` | props typed with `interface` | use `type` |
| Error: component needs `defaultProps` | since 4.0 required when the component has props | add `defaultProps` |
| `import {...} from "remotion"` resolves to your folder | tsconfig `paths` alias without prefix | prefix aliases |
| `staticFile()` path broken with `%25` | manual encoding plus v4 auto-encoding | pass the raw filename |
| Config options ignored in scripts | `remotion.config.ts` not read by SSR APIs / `bundle()` | pass options/overrides directly |
| `getInputProps()` returns `{}` | used in Player / Node / CSR | use component props or `calculateMetadata` |
| Unhandled error in browser render | `cancelRender` throws | wrap in `try/catch` in client-side rendering |
| `Cannot use 'import.meta' outside a module` (browser-bundler in Next App Router) | worker transpiled by Next | host compiler assets statically with `workerUrl` (4.0.529) |
| GitHub Actions render fails with `--gl=angle` | no GPU | use default or `swangle` |
| HDR output overexposed | `--color-space=bt2020-ncl` tags SDR content as HDR | output SDR |
| Lottie flickers | non-deterministic expressions under `goToAndStop()` | avoid those expressions |
| `playbackRate` throws in preview | Chrome range 0.0625..16 | stay in range; reverse unsupported |
| Volume changes ignored on Safari | `useWebAudioApi` combined with `playbackRate` | do not combine on Safari |
| Map render issues | `map.remove()` cleanup, map's own animations | no cleanup; `interactive: false`, `fadeDuration: 0` |
| Turf error at progress 0 | zero-length `lineSliceAlong` | `Math.max(0.001, ...)` |
| Font picker `loadFont` throws | `@remotion/google-fonts` imported as CommonJS | ESM import |
| `<HtmlInCanvas>` throws | nested HtmlInCanvas | merge into one `onPaint` |
| Bun: `lazyComponent` ignored, script does not exit | Bun runtime limitations | use Node for SSR scripts or exit manually |
| Wrong measured sizes in Studio | preview `scale()` transform | divide by `useCurrentScale()` |
| `onError` of Html5Video before 3.3.89 could not catch | old versions | update |

---

## 7. What our skills must teach

### 7.1 Non-negotiable determinism rules
- Every visual value is a function of `useCurrentFrame()`, props and static data. Nothing else.
- Never use CSS `transition`, CSS `animation`/`@keyframes` running on their own (only the paused + negative `animationDelay` scrub trick), `Math.random()` (use `random('seed')` from `remotion`), `Date.now()`/`new Date()` for animation, `setTimeout`/`setInterval`/`requestAnimationFrame` loops, or libraries with internal tickers unless seeked per frame (`@remotion/gsap`, `@remotion/lottie`, MapLibre `jumpTo`).
- Do not keep animation state between frames (no incrementing refs/state per frame); recompute from frame 0 when you need accumulation (time remapping loop).
- Never depend on frame order; never animate while paused.
- Data must be identical in every render tab; fetch in `calculateMetadata`.

### 7.2 Readiness checklist (before calling a composition done)
- [ ] All images/videos/audio/iframes use Remotion components (no native tags, no CSS `background-image`/`mask-image` for assets).
- [ ] All custom async work uses `useDelayRender()` + `useState(() => delayRender('label'))`, with `continueRender` on success and `cancelRender(err)` on failure.
- [ ] Fonts loaded with explicit `weights` and `subsets`; text measurement gated on fonts ready.
- [ ] Heavy media that starts after frame 0 is premounted (`premountFor={fps}`).
- [ ] No `delayRender` at module top level; none created per React render.
- [ ] Silent videos are `muted`.
- [ ] Remote assets are CORS-enabled (or render with `--disable-web-security` knowingly).

### 7.3 Timing math rules
- `frames = Math.round(seconds * fps)`; durations from media: `Math.floor(seconds * fps)` (as the docs do).
- Last frame index is `durationInFrames - 1`; a progress that must reach exactly 1 on the last frame uses `[0, durationInFrames - 1]`.
- CLI and `frameRange` ranges are inclusive.
- Clamp both sides for one-shot animations; leave `extend` only when you want continuing motion.
- Keep `inputRange` strictly increasing; guard for short compositions.
- Offsets and staggers: subtract from `frame` (or `spring({delay})`); nested Sequences/Loops cascade, so compute local time inside the child.
- Size scenes to motion: `measureSpring({fps, config})` or `spring({durationInFrames})`.
- If fps might change later, express timings in seconds times fps, not hardcoded frames.

### 7.4 Motion craft defaults (derived from the docs; adjust per brand)
| Intent | Default |
|---|---|
| Calm UI / corporate entrance | `spring({fps, frame, config: {damping: 200}})` (no bounce, ~23 frames at 30 fps) or `Easing.out(Easing.cubic)` over 15-24 frames |
| Playful pop | default `spring()` (slight overshoot) or `Easing.back()` / `Easing.elastic(1)` |
| Exit | mirror the entrance with an exit spring subtracted (`enter - exit`) or `Easing.in(...)` |
| Camera moves, pans | `Easing.inOut(Easing.cubic)` over the whole move (maps page) |
| Scale changes | `output: 'perceptual-scale'` |
| Sequenced keyframes that should flow | `Easing.spring({damping: 200, allowTail: true, durationRestThreshold: 0.03})` per segment |
| Hard cuts between states | `Easing.step1` |
| Choppy/stop-motion style | `posterize: 2` or `3` |
| Color changes | `interpolateColors` with an explicit mid stop for hue jumps |
| Layering | `<AbsoluteFill>` order instead of `z-index` |
| Transforms | separate `translate`, `scale`, `rotate`, `opacity` style props (Studio-editable) |
| Stagger | 3-6 frames between items (convention, not doc-mandated) via `frame - i * gap` |

### 7.5 Decision tables
**Which timing primitive?**
| Need | Use |
|---|---|
| Start a child later / cut its length | `<Sequence from durationInFrames>` or timing props on `<AbsoluteFill>`/`<Img>`/`Interactive.*` |
| Clips back to back | `<Series>` (D2) |
| Transitions between clips | `<TransitionSeries>` (overlay variant keeps length) |
| Repeat | `<Loop durationInFrames times>` |
| Hold a frame | `<Sequence freeze={n}>` (or `<Freeze frame active>`) |
| Change speed | `playbackRate` on Sequence/Loop/media, or time remapping for ramps |
| Group in sidebar only | `<Folder>` |

**Where does async data load?**
| Data | Place |
|---|---|
| JSON/API data, anything that determines duration/size/fps | `calculateMetadata()` (once, abortable, typed) |
| Binary assets, fonts, WebGL scenes, maps | component with `useDelayRender` (or Remotion asset components) |
| Preview-only buffering | `useBufferState().delayPlayback()` alongside delayRender |

**Which image component?**
| Case | Component |
|---|---|
| Static image, no effects | `<Img>` |
| Static image with effects or canvas | `<Img effects>` / `<CanvasImage>` (needs CORS) |
| Animated GIF/WebP/APNG/AVIF in Chrome/Firefox | `<AnimatedImage>` |
| GIF that must work everywhere incl. Safari | `<Gif>` (`@remotion/gif`) |
| Frame-numbered image sequence | `<Img src={staticFile(`frame${frame}.png`)}>` |

**Which video/audio component?** New code: `<Video>`/`<Audio>` from `@remotion/media` (supports effects, HLS, client-side rendering). `<OffthreadVideo>`: server-side frame extraction, HDR tone mapping, `transparent`. `<Html5Video>`/`<Html5Audio>`: only when native HTML5 behavior is needed (not in client-side rendering).

**Codec by deliverable:** see 4.8. Default H.264 + yuv420p + bt709; ProRes for editing/alpha; VP9/AV1 for small files when encode time is acceptable (AV1 not on Lambda).

**`--gl` by environment (4.0.528):** no WebGL: default; WebGL/Three/shaders/HTML-in-canvas WebGL/maps on a Mac: `angle`; Linux cloud GPU: `angle-egl`; no GPU or Lambda: `swangle`; long `angle` renders: split.

**Where to render:** local CLI/Studio for development and single videos; Node SSR (`bundle` + `selectComposition` + `renderMedia`) for batch/automation; Lambda for scale and speed; client-side (`@remotion/web-renderer`) for in-browser export when the element subset suffices.

### 7.6 Props and schema rules
- Type props with `type`; give every composition `defaultProps`; keep props JSON-serializable (plus Date/Map/Set/staticFile); keep them small (pass URLs, not blobs).
- Add a Zod `schema` whenever validation, enums, optional values or constrained numbers matter; otherwise rely on 4.0.516 inference.
- Use `calculateMetadata` to derive duration from content (text length, media duration, caption count) instead of hardcoding.
- For Studio-editable components use `Interactive.*` / `Interactive.withSchema()` with `Interactive.baseSchema` spread in, forward `controls` to the Sequence, keep values inline.

### 7.7 Asset and font rules
- Everything in `public/`, referenced via `staticFile('name')` (raw name, no manual encoding). No absolute paths, no `fs` in components.
- Use `getStaticFiles()` to enumerate (Studio/render only), pass `src` not `name`.
- Fonts: one `fonts.ts`, explicit weights/subsets, `waitUntilDone()` before measuring; right subsets for non-Latin scripts; Docker emoji/CJK fonts when rendering on Linux.

### 7.8 Version guard for 4.0.528 (write forward-compatible code)
- Available on 4.0.528: everything tagged up to 4.0.528, including interpolate CSS strings (4.0.472), tuples (4.0.473), per-segment easing (4.0.462), `posterize` (4.0.470), `perceptual-scale` (4.0.490), `outputType` (4.0.526), step1 strings (4.0.509), `Easing.spring` (4.0.476, `allowTail` 4.0.483), interpolateColors easing (4.0.475) and oklch family (4.0.439), `<AbsoluteFill>` timing props (4.0.501) and premount props (4.0.528), `<Loop playbackRate>` (4.0.528), effects (4.0.464), `lightLeak` (4.0.500), `<CanvasImage>` (4.0.466), `Interactive` (4.0.475), default-props inference (4.0.516), `@remotion/gsap` (4.0.517), codemods/canvas/browser-bundler (4.0.527).
- NOT on 4.0.528: browser-bundler static `workerUrl` setup (4.0.529); anything marked 5.0.
- 5.0 defaults are inactive, so set them explicitly: `premountFor` on heavy Sequences, `colorSpace: 'bt709'` (or `Config.setColorSpace('bt709')` / `--color-space=bt709`), google-fonts `weights` + `subsets`, `--gl=angle` when WebGL is used, `inputProps` in `selectComposition()`/`getCompositions()` always, options-object `bundle()`, no `measureSpring({from, to})`, no `TransitionSeries layout="none"`, `@remotion/effects` instead of `@remotion/light-leaks`/`@remotion/starburst`, `pauseWhenBuffering`/`pauseWhenLoading` explicit in Player apps.
- Always install all `remotion` and `@remotion/*` packages at the exact same version (`npx remotion add <pkg>`, `--save-exact`, no `^`).

### 7.9 Render pre-flight checklist
- [ ] Studio preview scrubbed at start, middle, end, and at every Sequence boundary.
- [ ] Composition id valid (`a-z A-Z 0-9 -`), fps/size correct for the platform, duration derived from content.
- [ ] `colorSpace` bt709, `pixelFormat` yuv420p for social delivery; ProRes 4444 + `yuva444p10le` + png frames for alpha.
- [ ] CRF chosen per codec table (or bitrate with HW encoding, not both).
- [ ] `--gl` chosen per content; concurrency chosen (1 only for WebGL-heavy scenes).
- [ ] Env vars prefixed `REMOTION_` (CLI) or passed via `envVariables` (SSR).
- [ ] For scripts: bundle once, `selectComposition` with the same `inputProps` as `renderMedia`.
- [ ] Output checked with `npx remotion ffprobe` (duration, fps, color tags) and visually.

### 7.10 Never do
- Call `bundle()` per render or inside a serverless function.
- Render several videos at once on one machine.
- Use `overrideFfmpegCommand` unless unavoidable (discouraged, breaks between versions, not on Lambda).
- Output HDR; nest `<HtmlInCanvas>`; use `interface` for props; ship giant `defaultProps`; leave `delayRender` handles dangling; rely on `--concurrency=1` to fix non-determinism.

---

## 8. Best examples to learn from

Docs pages (mirror paths):
- `mirror/docs/interpolate.md`: every modern option (CSS strings, tuples, step1, perceptual scale, per-segment easing, posterize) in one place.
- `mirror/docs/easing.md`: `Easing.spring` with `allowTail` for flowing multi-keyframe motion.
- `mirror/docs/animation-math.md`: the enter-minus-exit spring pattern.
- `mirror/docs/animating-properties.md`: minimal fade/scale with the "always drive by frame" rule.
- `mirror/docs/flickering.md`: the canonical explanation of multi-tab rendering and the determinism criteria.
- `mirror/docs/data-fetching.md` + `mirror/docs/calculate-metadata.md` + `mirror/docs/dynamic-metadata.md`: data and duration pipeline (abort, debounce, colocated schema + fetcher).
- `mirror/docs/delay-render.md`: correct handle patterns and anti-patterns.
- `mirror/docs/light-leaks.md`: effect as a transition overlay without shortening the timeline.
- `mirror/docs/maps.md`: how to drive an external WebGL renderer frame by frame (per-frame delayRender + idle).
- `mirror/docs/html-in-canvas.md` + `mirror/docs/create-effect.md`: canvas post-processing and custom effect factory.
- `mirror/docs/interactive-with-schema.md` + `mirror/docs/interactivity-schema.md`: building Studio-editable components.
- `mirror/docs/export-opentimeline.md`: a complete, well-structured agent skill written by the Remotion team (useful template for our own skill format and for timeline math).
- `mirror/docs/dataset-render.md`: staggered title reveal + batch rendering script.
- `mirror/docs/distributed-rendering.md`: exact chunking rules (audio alignment).
- `mirror/docs/docker.md`: production Dockerfile.
- `mirror/docs/building-a-timeline.md`: tracks/items data model rendered with Sequences.
- `mirror/docs/audio-buffer-to-data-url.md`: generating audio procedurally.
- `mirror/docs/encoding.md` + `mirror/docs/config.md`: codec/CRF tables and every config option.

Example repos (local copies exist under `examples/`):
- `examples/timing-functions/src/TimeRemapping.tsx`, `remap-speed.tsx`, `CameraApproach.tsx`: speed ramps and perspective push-in done deterministically.
- `examples/css-animation-play-state/src/Composition.tsx`: scrubbing CSS keyframes with paused play state + negative delay.
- `examples/html-in-canvas/` (glitch, burn dissolve, sticker peel, shine, vintage): referenced by html-in-canvas.md.
- `examples/light-leak-example/`: light leak presentation.
- `examples/gpu-scene/`: GPU-heavy scene used in the Azure GPU guide.
- `examples/mapbox-example/`: map animation (maps.md uses MapLibre).
- `examples/library-starter/`: packaging reusable Remotion components.
- `examples/cloudflare-containers-demo/`: container rendering proof of concept.
- `repo/packages/brand/`: Remotion's own motion design system (design-systems.md), source for reusable brand compositions.

URLs referenced by my pages: `github.com/remotion-dev/html-in-canvas`, `remotion.dev/prompts/html-in-canvas-magnifying-glass`, `.../vintage-screen-effect-html-in-canvas`, `.../glitch-effect-html-in-canvas`, `github.com/remotion-dev/measure-item`, `github.com/alexfernandez803/remotion-dataset`, `github.com/remotion-dev/id3-tags` (lazyComponent + sync wasm), `github.com/remotion-dev/angular-starter`, `github.com/remotion-dev/library-starter`, `remotion.dev/templates/electron`.

---

## 9. Open questions

1. `spring()` full reference (defaults, `reverse`, `from/to`, `durationRestThreshold` default value, how `durationInFrames` stretches) is on the D2 spring page; I relied on the Easing.spring defaults (damping 10, mass 1, stiffness 100, overshootClamping false). Confirm with D2.
2. `<Sequence>` details (`premountFor` semantics, `layout="none"`, `crop*`, `freeze`, `outlineRef`, cascading) are D2 material; several of my components inherit them.
3. `useDelayRender()` version: cancel-render.md says "from v3.0.374", which looks like a typo for 4.0.374. Check the use-delay-render page (D2).
4. `setX264Preset` shows `AvailableFrom v="4.2.2"` in config.md (likely a typo); confirm the real version from the renderer docs.
5. measuring.md pre-4.0.110 workaround multiplies by the measured scale; logically it should divide. Irrelevant on 4.0.528 (use `useCurrentScale()`), but do not copy that snippet.
6. freeze.md example titled "From frame 30 on" uses `active={(f) => f < 30}` (freezes before frame 30). Title and code disagree; semantics of `active` are clear (true = frozen).
7. interpolateColors blends in sRGB only. Is there any perceptual (OKLCH) interpolation option planned? Not documented; teach mid-stops for now.
8. HDR page mentions `bt2020-cl`, but 4.0.528's renderer only accepts `default | bt601 | bt709 | bt2020-ncl`.
9. `Config.setColorSpace()` exists in 4.0.528 typings but is not on the config doc page; the render/CLI agent should confirm the exact CLI flag and Studio setting.
10. HTML-in-canvas Studio preview needs Chrome 149+ with a flag; unknown whether the machine's Chrome qualifies (rendering itself is fine).
11. `@remotion/effects` is not installed in the local `remotion-broll` project; effects-based recipes need `npx remotion add @remotion/effects` at 4.0.528 first. Which effects exist at exactly 4.0.528 should be checked by the effects agent (D5).
12. google-fonts subset names for Bengali (`bengali`) should be confirmed via `getInfo()` for Noto Sans Bengali / Hind Siliguri before a skill hardcodes them.
