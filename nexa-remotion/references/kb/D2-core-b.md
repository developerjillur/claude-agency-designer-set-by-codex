# D2-core-b: Remotion core docs, second half (media-parser to zod-types)

Research agent: D2-core-b. Source: `mirror/docs/*.md` (132 pages). Target install: Remotion 4.0.528, React 19.

---

## 1. Scope and coverage

- Assigned: 132 pages listed in `assign-D2-core-b.txt`, from `media-parser.md` to `zod-types.md` (about 14,200 lines, 529 KB).
- Read: all 132, each one fully, in assignment order. Every path is logged in `kb/D2-core-b.coverage.txt` (132 lines, checked with `diff` against the assignment: identical set, no duplicates).
- Could not read: none.
- Companion file: `kb/D2-core-b.worknotes.txt` holds my raw per-page notes (one heading per page, same order as the assignment). Use it to look up a single page's details; this file is the synthesis.
- Quality notes on the sources:
  - Six pages are HTML conversions with TypeScript hover noise inside code blocks (`null.md`, `preload.md`, `skia.md`, `studio.md`, `use-offthread-video-texture.md`, `use-video-texture.md`). I rebuilt the code from the noise; the meaning is clear.
  - About 20 pages are package overviews whose function lists live in sub-pages owned by other agents (`media-utils`, `paths`, `shapes`, `noise`, `rive`, `rounded-text-box`, `sfx`, `transitions`, `three`, `zod-types`, `using-audio`, `terminology`, `web-renderer`, `renderer`, `player`, `studio-protocol`, `timeline`, `remotion`). I recorded what the overview says and the sub-page names, and did not invent sub-page details.
  - `terms.md` and `privacy.md` are the upcoming **v5.0** legal texts (they take effect when Remotion 5.0 ships). `spline.md` is flagged by the docs themselves as possibly out of date.
- Cross-checks I did beyond the assignment (read-only):
  - Version markers on neighbouring pages that my pages depend on: `interpolate.md`, `easing.md`, `absolute-fill.md`, `interactive.md`, `bundlers.md`, `bundle.md`, `rough-notation/api.md`, `media/video.md`, `videos/as-threejs-texture.md`.
  - The installed package at `nexa-media/remotion-broll/node_modules/remotion` is 4.0.528. Its type definitions confirm `Sequence` has `playbackRate`, `trimBefore`, `freeze`, `cropLeft`, `hidden`, `controls` and `outlineRef`, and that `Easing.spring`, the `posterize` option, `Interactive`, `Solid`, `HtmlInCanvas`, `usePixelDensity`, `useDelayRender` and `Freeze` are all exported.
  - Installed `@remotion/*` packages there: bundler, canvas, captions, cli, codemods, compositor-darwin-arm64, eslint-config-flat, google-fonts, layout-utils, licensing, media, media-parser, media-utils, noise, paths, player, renderer, rough-notation, sfx, shapes, streaming, studio, studio-protocol, studio-server, studio-shared, tailwind-v4, timeline-utils, transitions, web-renderer, zod-types. **Not installed**: three, motion-blur, effects, skia, rive, gif, lottie, light-leaks, animation-utils, preload, rounded-text-box, video-matting, whisper-webgpu, openai-whisper.
- Version reality check: the docs are at 4.0.529 (install snippets pin `@4.0.529`). The newest "available from" marker in my 132 pages is **4.0.528**, the installed version. So every API in this file exists on our install, but the ones marked 4.0.528 are brand new (see Open questions). Behaviours described as "Remotion 5.0" are not active on 4.0.528.

---

## 2. Mental model

1. **A frame is a pure function.** Remotion gives a component a frame number and a blank canvas. The renderer opens several browser tabs in parallel and asks each for arbitrary frames, often out of order. Anything that depends on wall-clock time, on the order frames are drawn, or on per-tab state (timers, `Math.random()`, R3F `useFrame`, free-running CSS animations, physics simulations stepped per render) gives different pixels in different tabs and breaks the video. Derive everything from `useCurrentFrame()`, `useVideoConfig()` and props.
2. **Frames are the unit, seconds are the language.** First frame is `0`, last is `durationInFrames - 1`. Write timings as `seconds * fps` so a composition can switch between 30 and 60 fps without changing speed.
3. **Timelines nest.** Every timing container creates a child timeline. For a child at parent frame `t`: `childFrame = trimBefore + (t - from) * playbackRate`. The child is mounted only while `from <= t < from + durationInFrames` (parent frames); outside that window it is **unmounted**, not hidden. Inside, `useVideoConfig().durationInFrames` is the local end of that window. Nesting cascades (a `from={60}` inside a `from={30}` starts at 90). Timing containers include `<Sequence>`, `<Series.Sequence>`, `<AbsoluteFill>` (timing props since 4.0.501), `Interactive.*` elements, `<Img>`, `<Solid>`, `<HtmlInCanvas>`, `<Video>`/`<Audio>` from `@remotion/media`, `<ThreeCanvas>` (4.0.528), rough-notation and shapes components.
4. **Media order of operations**: (1) `from`, `trimBefore`, `trimAfter` choose the source range, (2) `playbackRate` stretches it, (3) `loop` repeats it, (4) `durationInFrames` cuts the timeline length last.
5. **Composition = component + metadata** (`width`, `height`, `fps`, `durationInFrames`, `id`), registered in the root. Never nest `<Composition>`. `<Still>` is a one-frame composition. `calculateMetadata()` runs once per render (not per tab), may be async, may fetch data, may even use true randomness, and can set fps, duration, size, default codec, sample rate, pixel format and props.
6. **Props pipeline**: `defaultProps` (shape and fallback) -> input props (CLI `--props`, `inputProps` in SSR, Studio render dialog; must be JSON) -> `calculateMetadata()` -> component. Since 4.0.516 the Studio infers editing controls from `defaultProps`; a Zod schema is optional.
7. **Nothing may be missing at screenshot time.** Remotion's own tags (`<Img>`, `<Video>`, `<Audio>`, `<IFrame>`, `<OffthreadVideo>`...) hold the frame via `delayRender()` until loaded. Your own async work must do the same with `useDelayRender()` (preferred, 4.0.342) or the global `delayRender()`. Default limit: 30 s, then the render fails.
8. **Three video tag families.** `<Video>`/`<Audio>` from `@remotion/media` (Mediabunny + WebCodecs, frame-perfect, fastest, default for new work), `<OffthreadVideo>` (Rust + FFmpeg extractor, render only, downloads whole file), `<Html5Video>`/`<Html5Audio>` (native elements, not frame-perfect; `<Html5Video>` was called `<Video>` in older code). `@remotion/media` falls back to the older tags in SSR for unsupported media.
9. **Four runtimes, different rules.** Studio (preview + editor), Player (embedded in apps), server-side render (headless Chrome + FFmpeg: CLI, Node, Lambda, Vercel Sandbox, Cloud Run), client-side render (`@remotion/web-renderer`, WebCodecs, subset of tags/CSS). Use `useRemotionEnvironment()` to branch.
10. **Output pipeline**: screenshot each frame (JPEG quality 80 by default, or PNG) -> encode (H.264 by default; ProRes, VP8/VP9, GIF, etc.) -> mix all audio resampled to one rate (48 kHz by default).
11. **The Studio is an editor now.** `Interactive` elements (4.0.475), visual props editing, keyframe settings, crop, `hidden` (eye icon) and schema controls write back to source. Code stays editable only if it follows the conventions: inline `defaultProps` object literal, inline `interpolate()` keyframe arrays, individual CSS `translate`/`scale`/`rotate`/`opacity` properties instead of `transform` strings.
12. **The GPU is not a given.** Headless renders run on CPU by default. WebGL/WebGPU content needs `--gl=angle` on Remotion 4 (or `swangle` without a GPU). GPU-heavy CSS (`box-shadow`, gradients, `filter: blur()`) is slow on cloud machines.
13. **One version for everything.** `remotion` and every `@remotion/*` package must be the exact same version (no `^`).

---

## 3. API digest

### 3.1 Hooks and core functions (package `remotion`)

**`useCurrentFrame()`**
- Returns the frame relative to the nearest timing parent (0-indexed). Inside `<AbsoluteFill from={10}>` at timeline frame 25 it returns 15.
- For the absolute frame inside a timed child: read it at the top level and pass it down as a prop.
- With `playbackRate`, only `useCurrentFrame()` calls *inside* the sped-up subtree change speed; values computed in the parent and passed down keep the parent clock.

**`useVideoConfig()`** returns `{width, height, fps, durationInFrames, id, defaultProps, props (4.0.0), defaultCodec (4.0.54), defaultSampleRate (4.0.448)}`.
- `width`/`height` are overridden by a parent `<Sequence width height>` (4.0.80).
- `durationInFrames` inside a sequence is the local end: visible 40 parent frames with `playbackRate={2}` and `trimBefore={10}` gives `40 * 2 + 10 = 90`.

**`useCurrentScale(options?)`** (4.0.125): Studio zoom or Player fit scale; use to convert measured DOM sizes. Throws outside Remotion unless `{dontThrowIfOutsideOfRemotion: true}` (then 1). Returns 1 in render environments.

**`usePixelDensity(options?)`** (4.0.472): `window.devicePixelRatio` in preview, the render `scale` when rendering. Same `dontThrowIfOutsideOfRemotion` option. Feed it to `pixelDensity` props of canvas-based components.

**`useRemotionEnvironment()`** (4.0.342): `{isStudio, isRendering, isPlayer, isReadOnlyStudio, isClientSideRendering (4.0.344)}`. Preferred over `getRemotionEnvironment()` because it is scoped to the calling tree.

**`useDelayRender()`** (4.0.342): returns scoped `{delayRender, continueRender, cancelRender}` (`cancelRender` from 4.0.374). Recommended over the global functions (future-proof for browser rendering). No-op in Player and Studio.

**`useBufferState()`** (4.0.111): `buffer.delayPlayback()` returns a handle with `unblock()`. Puts the Player into buffering. Create it inside `useEffect`, never in a `useState` initializer (Strict Mode double call leaves a handle that never clears), and always unblock in the cleanup. Pair with `delayRender` if the same load must also block rendering. No-op in SSR and client-side rendering.

**`random(seed)`**: deterministic value in `[0, 1)` from a number or string seed (`random(1)` is always `0.07301638228818774`). `random()` with no argument throws. `random(null)` gives true randomness without the ESLint warning that `Math.random()` triggers. Works in every environment.

**`spring({frame, fps, from?, to?, reverse?, config?, durationInFrames?, durationRestThreshold?, delay?})`**
- Defaults: `from 0`, `to 1`, `reverse false` (3.3.92), `config: {mass: 1, damping: 10, stiffness: 100, overshootClamping: false}`.
- `durationInFrames` (3.0.27) stretches the curve to an exact length; `durationRestThreshold` (3.0.27, only with `durationInFrames`) sets how close to the end counts as done (0.001 means 99.9%).
- `delay` (3.3.90): frames before the start (returns the initial value until then).
- Order: stretch, then reverse, then delay.
- Default config bounces. `damping: 200` gives a smooth, non-overshooting move. Lower `mass` is faster. `measureSpring()` gives the natural length. Playground: remotion.dev/timing-editor.

**`interpolate()` extras relevant to my pages** (details belong to another agent's `interpolate.md`):
- `posterize: n` (4.0.470) quantizes the input: frames 0-2 use the frame 0 value, 3-5 the frame 3 value. Also on `interpolateColors()` and `interpolateStyles()` (`@remotion/animation-utils`). Studio keyframe previews respect it; edit via right-click on a keyframed prop, "Keyframe settings...".
- Per-segment `easing` array (4.0.462), `Easing.spring({damping, mass, stiffness, overshootClamping, durationRestThreshold (4.0.483), allowTail (4.0.483)})` (4.0.476; measured as if it lasted 30 frames), CSS-unit outputs like `['-200px', '200px']` (CSS transform values 4.0.472).

**`registerRoot(Root)`**: call once, in its own file (usually `src/index.ts`), separate from `src/Root.tsx`, because Fast Refresh re-executes the edited file. May be deferred (for example after loading WASM) without `delayRender()`. Studio and SSR only.

**`VERSION`**: from `remotion` or `remotion/version` (the latter avoids importing React). Only reports the `remotion` package.

### 3.2 Timeline components

**`<Sequence>`** (props, defaults, versions)

| Prop | Default | Since | Notes |
|---|---|---|---|
| `from` | `0` | optional since 3.2.36 | Negative values trim the start of the content. |
| `durationInFrames` | `Infinity` | | Children unmounted outside the window. |
| `trimBefore` | `0` | 4.0.482 | Sequence still starts at `from`; children see frames advanced by `trimBefore`. |
| `playbackRate` | `1` | **4.0.528** | Positive, finite, constant over time. Mount window unchanged; `trimBefore` counts in child frames after the speed change; nested rates multiply; a media tag's own rate multiplies too. |
| `freeze` | `null` | 4.0.476 | Holds children at a frame without remounting (like `<Freeze>`). |
| `width` / `height` | | 4.0.80 | Sets the container size and overrides `useVideoConfig()` size for children. |
| `name` | | | Studio timeline label. |
| `layout` | `'absolute-fill'` | 1.4 | `'none'` removes the wrapper div (required inside `<ThreeCanvas>`). |
| `cropLeft/Right/Top/Bottom` | | 4.0.500 | Ratio 0..1, animatable, only with `absolute-fill`; overlapping crops meet in the middle; inline `borderRadius` is applied to the crop, class radii are not. |
| `style` / `className` | | 3.0.27 / 3.3.45 | Not allowed with `layout="none"`. |
| `premountFor` | `0` | 4.0.140 | Mount early to avoid flicker. Remotion 5 default becomes `fps` (1 s). |
| `postmountFor` | | 4.0.340 | Keep mounted after the end (for backwards seeking). |
| `styleWhilePremounted` / `styleWhilePostmounted` | | 4.0.252 / 4.0.340 | Override styles in those phases. |
| `showInTimeline` | `true` | 4.0.110 | Children still show unless they also opt out. |
| `hidden` | `false` | 4.0.462 | Not rendered; Studio eye icon writes it to source. |
| `outlineRef` | | 4.0.479 | Element the Studio outlines; needed with `layout="none"`. |
| `controls` | | 4.0.501 | Pass through the object from `Interactive.withSchema()`; never build by hand. |
| `ref` | | 3.2.13 | `HTMLDivElement`. |

Minimal example of the speed maths (4.0.528):

```tsx
// At comp frame 30 the child sees 10; at 40 it sees (40 - 30) * 2 + 10 = 30.
// The sequence is still visible until comp frame 89.
<Sequence from={30} durationInFrames={60} trimBefore={10} playbackRate={2}>
  <Child />
</Sequence>
```

**`<Series>`** (2.3.1) and **`<Series.Sequence>`**
- Since 4.0.443 `<Series>` is itself a `<Sequence>` and takes all its props; its `layout` defaults to `'none'`.
- `<Series.Sequence>`: `durationInFrames` (only the last one may be `Infinity`), `offset` (positive adds a gap, negative starts early and overlaps the previous scene; shifts all following scenes), `trimBefore` (4.0.497), `playbackRate` (4.0.528: scene length and next start unchanged; on `<Series>` itself it speeds the whole series), `freeze` (4.0.476), `layout` (`'absolute-fill'` default), `style` (3.3.4), `className` (3.3.45), `showInTimeline`, `premountFor` (4.0.140), `ref` (3.3.4).

**Shared timing props** (`timing.md`): `from`, `durationInFrames`, `trimBefore`, `playbackRate` on Interactive elements and `<AbsoluteFill>`, `<Img>`, `<CanvasImage>`, `<AnimatedImage>`, `<Solid>`, `<HtmlInCanvas>`, `<HtmlInCanvasMotionBlur>`, `<Gif>`, `<Lottie>`, `<ThreeCanvas>`, `<RemotionRiveCanvas>`, `@remotion/shapes`, `@remotion/rough-notation`, `<MacOSCursor>`, and `<Video>`/`<Audio>` from `@remotion/media` (which add `trimAfter` and `loop`). Components built with `Interactive.withSchema()` can expose them too.

**`<Still>`**: `<Composition>` without `durationInFrames` and `fps`. The Studio hides the timeline. Studio and SSR only.

**`<Solid>`** (4.0.464): a solid rectangle painted on a `<canvas>`, mainly as a base for effects.
- Required: `width`, `height` (positive integers, logical px). Optional: `color` (default transparent), `effects` (4.0.464), `pixelDensity` (4.0.472, default 1), `className`, `style`, crop props (4.0.500).
- Inherits `from`, `durationInFrames`, `trimBefore` (4.0.482), `playbackRate`, `name`, `showInTimeline`, `hidden`; premount and postmount props since 4.0.528. Ref type `HTMLCanvasElement`.

### 3.3 Assets and loading

**`staticFile(name)`** (2.5.7): turns a file in `public/` into a URL with a hashed prefix (`/static-32e8nd/my-image.png`).
- Pass the bare name: `staticFile('image.png')` (a leading slash is tolerated). Wrong: `'../public/x'`, `'./x'`, absolute paths, `'public/x'` (error "does not support relative paths"), and remote URLs (error "does not support remote URLs"; pass URLs directly).
- `public/` must sit next to the `package.json` that lists `remotion`.
- Since 4.0.0 it URI-encodes the name (`#` becomes `%23`), so do not pre-encode.
- Works with `<Img>`, `<Video>`, `<Audio>`, `<OffthreadVideo>`, `<Html5*>`, `fetch()`, `FontFace()`.
- Related: `getStaticFiles()` lists files; `watchStaticFile(name, cb)` (4.0.61, Studio only, moving to `@remotion/studio`) calls `cb(StaticFile | null)` on change and returns `{cancel}`.

**`prefetch(src, options?)`** (3.2.23): downloads a whole asset into memory for smooth Player playback. Not recommended for most cases (the docs point to premounting instead).
- Options: `method` `'blob-url'` or `'base64'` (3.2.35), `contentType` (4.0.40), `credentials` (4.0.229), `onProgress` (4.0.85, `{loadedBytes, totalBytes | null}`), `logLevel` (4.0.250).
- Returns `{free(), waitUntilDone(): Promise<string>}`. Media tags given the original URL switch to the blob automatically. Use the resolved URL yourself for CSS such as `mask-image`.
- Needs CORS. No-op in every render environment.

**`@remotion/preload`**: `preloadVideo()`, `preloadAudio()`, `preloadImage()`, `preloadFont()`, `resolveRedirect()`. Player/Studio smoothness only; not needed for rendering.

**Use Remotion tags, not native ones** (`use-img-and-iframe.md`): `<Img>`/`<Gif>` instead of `<img>`, Next `<Image>` or CSS `background-image`; `<Video>`/`<OffthreadVideo>`/`<Html5Video>` instead of `<video>`; `<Audio>`/`<Html5Audio>` instead of `<audio>`; `<IFrame>` instead of `<iframe>`. They wait for loading and stay in sync with the timeline.

### 3.4 Video and audio

**Which video tag** (`video-tags.md`, the key decision table)

| | `<Video>` / `<Audio>` (`@remotion/media`) | `<OffthreadVideo>` (`remotion`) | `<Html5Video>` / `<Html5Audio>` (`remotion`) |
|---|---|---|---|
| Engine | Mediabunny + WebCodecs | Rust + FFmpeg binary | HTML5 media element |
| Frame-perfect | yes | yes | not guaranteed |
| Partial download | yes | no (whole file first) | only with `muted` |
| Render speed | fastest | fast | medium |
| Containers | aac flac m3u8 mkv mov mp3 mp4 ogg wav webm (else fallback) | aac avi caf flac flv m4a mkv mp3 mp4 ogg wav webm | aac flac m4a mkv mp3 mp4 ogg wav webm |
| Codecs | AAC FLAC H.264 MP3 Opus VP8 VP9 Vorbis (else fallback) | adds AC3 AV1 H.265 M4A PCM | AAC FLAC H.264 MP3 Opus VP8 VP9 Vorbis |
| ProRes | preview (decoder must be enabled) + render | render only | no |
| HLS | yes | Chrome 142+ preview only | preview only |
| CORS needed | **yes** | no | no |
| `loop` | yes | **no** | yes |
| `playbackRate` pitch | **pitch changes with speed** | pitch preserved | pitch preserved |
| `toneFrequency` | yes | SSR only | SSR only |
| Three.js texture | `onVideoFrame` snippet (best) | `useOffthreadVideoTexture()` | `useVideoTexture()` |
| Client-side rendering | yes | no | no |

- `@remotion/media` falls back during SSR: `<Video>` to `<OffthreadVideo>`, `<Audio>` to `<Html5Audio>` for unsupported media. H.265 plays in the browser but falls back to `<OffthreadVideo>` when rendering. ProRes decoding in `@remotion/media` is off by default (`/docs/videos/prores`).
- Performance page: `<Html5Video>` and `<OffthreadVideo>` are "not optimized"; migrate to `@remotion/media`.
- Per-environment switch: `useRemotionEnvironment().isRendering ? <Video .../> : <OffthreadVideo .../>` (types `VideoProps`, `RemotionOffthreadVideoProps`, `AudioProps`, `RemotionAudioProps`).

**`<Video>` from `@remotion/media`, as used on my pages** (`videos.md`, `timing.md`, `video-uploads.md`)
- `src` (URL or `staticFile()`), `from`, `durationInFrames`, `trimBefore`, `trimAfter`, `playbackRate` (constant only; speed ramps need the accelerated-video technique), `loop` (loops the trimmed range), `volume` (number or per-frame callback), `muted`, `style` (`width`, `height`, `position`, `objectFit`...), `onVideoFrame`, `headless` (4.0.387, no canvas mounted, for Three.js textures; from `media/video.md`).
- Example: `trimBefore={45} trimAfter={105}` at 30 fps plays source 1.5 s to 3.5 s; with `playbackRate={2} loop durationInFrames={90}` those 60 source frames repeat three times in 90 frames.

**`<OffthreadVideo>`** (3.0.11): during render the frame is extracted outside the browser and shown in an `<img>`; in preview it is a `<video>`. Not supported by `@remotion/web-renderer`.

| Prop | Default | Since | Notes |
|---|---|---|---|
| `src` | | | URL or `staticFile()`. |
| `trimBefore` / `trimAfter` | | 4.0.319 | Frames. Old names `startFrom`/`endAt` still work but cannot be mixed with the new ones. |
| `transparent` | `false` | 4.0.0 | `true` extracts PNG (alpha, slower); `false` extracts BMP. |
| `volume` | `1` | | Number or `(f) => number`; above 1 allowed now; iOS Safari forces 1 unless `useWebAudioApi`. |
| `useWebAudioApi` | | 4.0.306 | Volume above 1 and iOS volume; needs `crossOrigin="anonymous"` + CORS; on Safari not combinable with `playbackRate`. |
| `loopVolumeCurveBehavior` | `'repeat'` | 4.0.142 | `'extend'` keeps counting frames inside `<Loop>`. |
| `playbackRate` | `1` | 2.2.0 | Reverse not supported; Chrome preview throws below 0.0625 or above 16. |
| `preservePitch` | `true` | 4.0.463 | Preview only; SSR always preserves pitch. |
| `toneFrequency` | `1` | 4.0.47 | 0.01 to 2, SSR only. |
| `muted` | `false` | | |
| `acceptableTimeShiftInSeconds` | `0.45` | 3.2.42 | Resync threshold in Studio/Player. |
| `pauseWhenBuffering` | `false` | 4.0.111 | Becomes `true` in Remotion 5. |
| `toneMapped` | `true` | 4.0.117 | HDR to sRGB correction; `false` is faster but duller. |
| `audioStreamIndex` | `0` | 4.0.340 | Render only; streams are not channels. |
| `name` / `showInTimeline` | / `true` | 4.0.71 / 4.0.122 | Studio timeline. |
| `delayRenderTimeoutInMilliseconds` / `delayRenderRetries` | | 4.0.150 / 4.0.178 | |
| `onError` | | | Since 3.3.89 passing it suppresses the thrown error. |
| `onAutoPlayError` | | 4.0.187 | Default behaviour: mute and retry once. |
| `onVideoFrame` | | 4.0.190 | Receives a `CanvasImageSource` (preview `HTMLVideoElement`, render `HTMLImageElement`); from 4.0.472 preview also passes rVFC timestamp and metadata. |
| `crossOrigin` | `'anonymous'` if `onVideoFrame`, else unset | 4.0.190 | |
| `imageFormat` | removed | 4.0.0 | |
| `allowAmplificationDuringRender` | deprecated | 4.0.279 | |

- No `loop` prop; the last frame stays on screen after the file ends. Codecs: H.264, H.265, VP8, VP9, AV1 (4.0.6), ProRes.
- Perf tips: `transparent` only when needed; `toneMapped={false}` when colour accuracy does not matter.

**Audio data and visualization** (`@remotion/media-utils`, MIT; all functions work outside Remotion except `useAudioData()`)
- `useAudioData(src, options?)`: loads and decodes the whole file into state, with delayRender handling. Options (4.0.458): `sampleRate` (AudioContext, default 48000), `requestInit` (only the first render's value is used). Returns `AudioData | null`. Throws if the file has no audio track (4.0.75+). Needs CORS for remote files.
- `useWindowedAudioData({src, frame, fps, windowInSeconds, requestInit?})` (4.0.240): loads only the windows around the current frame via Range requests (current, previous and next window, so `windowInSeconds: 10` holds up to 30 s). All Mediabunny formats since 4.0.383 (WAV only before). Returns `{audioData, dataOffsetInSeconds}`. Use it for long audio.
- `visualizeAudio({audioData, frame, fps, numberOfSamples, smoothing?, optimizeFor?, dataOffsetInSeconds?})` returns `numberOfSamples` values in 0..1, bass on the left.
  - `numberOfSamples`: power of two.
  - `smoothing`: default `true` (averages previous, current and next frame).
  - `optimizeFor` (4.0.83): default `'accuracy'`, `'speed'` for Lambda or many samples (default in v5).
  - `dataOffsetInSeconds` (4.0.268): pass through from the windowed hook.
  - `frame` means the position **in the audio file**; correct it if the audio is shifted or trimmed.
- Other exports named on my pages (`standalone.md`) or in the media-utils sub-page list: `getAudioData()`, `getAudioDurationInSeconds()` (no CORS needed), `getVideoMetadata()`, `getWaveformPortion()`, `audioBufferToDataUrl()`, `createSmoothSvgPath()`, `visualizeAudioWaveform()`.

**Sample rate** (`sample-rate.md`): output is 48 kHz by default and every source is resampled to it. Override since 4.0.448 with `renderMedia({sampleRate})`, `renderMediaOnWeb({sampleRate})`, `--sample-rate`, `Config.setSampleRate()` (CLI/Studio default only), or the Studio "Audio" tab. `calculateMetadata` can return `defaultSampleRate` (lower priority than the flag or the dialog). Preview AudioContext: `Config.setPreviewSampleRate()` or `--preview-sample-rate`. With mixed sources, pick the majority rate or the highest.

**Other media packages**
- **Mediabunny** (MPL 2.0, by Vanilagy) powers `@remotion/media`, `@remotion/media-utils`, the Studio and remotion.dev/convert. Install with `npm i --save-exact mediabunny` at the version Remotion uses; `npx remotion upgrade` keeps them aligned. Metadata snippet: `new Input({formats: ALL_FORMATS, source: new UrlSource(src)})`, then `computeDuration()`, `getPrimaryVideoTrack()` (`displayWidth`, `displayHeight`), `getPrimaryAudioTrack()` (`sampleRate`).
- **`@remotion/media-parser`** and **`@remotion/webcodecs`** (4.0.229) are deprecated in favour of Mediabunny. For reference: `parseMedia({src, fields: {durationInSeconds: true, videoCodec: true}})` and `onVideoTrack: ({track}) => (sample) => {...}`; webcodecs converts, rotates, extracts frames and fixes `MediaRecorder` files.
- **`@remotion/sfx`** (4.0.429): royalty-free sound effect URLs, peak-normalized to -3 dB, no attribution required (package MIT, per-sound licences). Sounds include whoosh, whip, ding, mouse-click, page-turn, shutter-modern, shutter-old, record-scratch, ui-switch, vine-boom, windows-xp-error, yippee and meme sounds.
- **`@remotion/video-matting`** (4.0.523, MIT; models keep their own licences): splits a video into an opaque base and a transparent foreground in the browser or Node with WebGPU. `separateVideoLayers()`, `canUseVideoMatting()`, `getAvailableModels()`. Needs a GPU and WebCodecs VP9-alpha encoding. Studio "Remove background" replaces a video's source with a transparent WebM (duplicate the layer first to keep the original). Install with `@huggingface/transformers`.
- **Transcription**:
  - `@remotion/whisper-webgpu` (4.0.518, MIT) is the preferred local path, in the browser or Node: `clearStaleModels()`, `downloadWhisperModel({model})`, `resampleTo16Khz({file})`, `transcribe({channelWaveform, model, language})`, `toCaptions({whisperWebGpuOutput})`. Check `canUseWhisperWebGpu()`.
  - `@remotion/whisper-web` (unstable, WASM) needs COOP `same-origin` + COEP `require-corp` headers and `optimizeDeps.exclude` in Vite.
  - `@remotion/openai-whisper` (4.0.217) converts OpenAI Whisper API output to `Caption[]`.
  - `@remotion/install-whisper-cpp` offers `installWhisperCpp()`, `downloadWhisperModel()`, `transcribe()`, `toCaptions()` on the server.

### 3.5 Visual effects, graphics and 3D

**Shaders and effects** (`shaders.md`, `starburst.md`, `solid.md`)
- `@remotion/effects` presets go in the `effects` array of canvas-based components (`<Solid>`, `<HtmlInCanvas>`). Import each preset from its own path, for example `@remotion/effects/halftone-linear-gradient`, `@remotion/effects/fisheye`, `@remotion/effects/starburst`. Custom effects come from `createEffect()`.
- `halftoneLinearGradient({firstStopDotSize, secondStopDotSize, firstStopPosition: [x, y], secondStopPosition: [x, y], gridSize, dotColor})` on a black `<Solid>` gives a halftone background.
- `<HtmlInCanvas width height effects={[fisheye({fieldOfView: 2.5})]}>` captures DOM children to pixels and runs shaders on them. It has a `pixelDensity` prop. The installed 4.0.528 package also exports `isHtmlInCanvasSupported` and `HTML_IN_CANVAS_UNSUPPORTED_MESSAGE` (useful to gate preview when the Chrome flag is off; the API itself is documented on another agent's page).
- `starburst({rays: 16, colors: ['#ffdd00', '#ff8800'], rotation})` (4.0.500) is a WebGL2 retro ray background. Keep `interpolate()` inline in the effect params so the Studio can edit the keyframes.
- Render any WebGL content with `--gl=angle` (Remotion 4).

**Motion blur** (`@remotion/motion-blur`, 3.2.31, MIT): three components.
- `<HtmlInCanvasMotionBlur>` is the recommended, most realistic one. It needs the HTML-in-canvas Chrome flag during **preview** only; rendering needs no setup.
- `<CameraMotionBlur>` works everywhere but its layered blending can shift colour and opacity. Props: `shutterAngle` (exposure length), `samples` (smoothness).
- `<Trail>` repeats earlier positions behind the element (a stylised look, not a camera exposure).

**Noise** (`@remotion/noise`, 3.2.32, MIT): `noise2D/3D/4D(seed, ...coords)` returns values in -1..1. Use two dimensions for space and one for time (`frame * speed`).

**SVG helpers**
- `@remotion/paths` (MIT): `getLength`, `getPointAtLength`, `getTangentAtLength`, `evolvePath`, `interpolatePath`, `cutPath`, `warpPath`, `scalePath`, `translatePath`, `reversePath`, `normalizePath`, `getBoundingBox`, `extendViewBox`, `parsePath`, `serializeInstructions`, `reduceInstructions`, `getSubpaths`, `getParts`, `resetPath`, `getInstructionIndexAtLength`.
- `@remotion/shapes` (MIT): `<Rect>`, `<Circle>`, `<Ellipse>`, `<Triangle>`, `<Star>`, `<Pie>`, `<Polygon>`, `<Callout>`, `<Heart>`, `<Arrow>`, `<Spark>` plus `make*()` path builders.
- `@remotion/rounded-text-box` (4.0.360, MIT): TikTok-style multi-line text box path with rounded corners (`createRoundedTextBox()`).

**Hand-drawn text annotations** (`@remotion/rough-notation`, 4.0.490)
- Components: `<Highlight>`, `<Underline>`, `<StrikeThrough>`, `<CrossedOff>`, `<Box>`, `<Bracket>` (with `bracketLeft`, `bracketRight`, `bracketTop`, `bracketBottom`), `<Circle>` (`box="inside"` option).
- Props seen: `progress` (0..1, drive it with `interpolate`), `color`, `strokeWidth`, `iterations`, `roughness`, `bowing`, `maxRandomnessOffset`, `padding` (`{left, right, top, bottom}`, negative allowed), `seed`, `name`.
- The docs wrap the surrounding text in `<Interactive.Div>` / `<Interactive.Span>` so it stays editable.

**Transforms** (`transforms.md`)
- Use the individual CSS properties `opacity`, `scale`, `translate` (`'100px 0px'`), `rotate` (`'45deg'`). They do not reflow layout, unlike `width` or `margin`, and the Studio can edit them.
- Use a `transform` string only for `skew()`, `perspective()` or order-dependent chains. `makeTransform([rotate(45), translate(50, 50)])` from `@remotion/animation-utils` builds one type-safely.
- Rotating in 3D needs `perspective` on the parent. SVG elements pivot around the top-left corner unless you set `transformBox: 'fill-box', transformOrigin: 'center center'`.

**Transitions** (`@remotion/transitions`, 4.0.53; `<TransitionSeries>` guide since 4.0.59; Remotion License)
- `<TransitionSeries.Sequence durationInFrames>`, then `<TransitionSeries.Transition presentation={slide()} timing={linearTiming({durationInFrames: 30})} />` or `springTiming({config: {damping: 200}})`.
- Both scenes render during a transition, so the total length shrinks: 40 + 60 - 30 = 70. `timing.getDurationInFrames({fps})` returns the length (a damping-200 spring at 30 fps is 23 frames).
- `<TransitionSeries.Overlay durationInFrames>` (4.0.415) draws on top of a cut without shortening anything, centred on the cut (for example `<LightLeak/>` from `@remotion/light-leaks`).
- A transition placed first or last gives an enter or exit animation.
- Rules: a transition may not be longer than either neighbour; no two transitions, two overlays, or a transition plus an overlay next to each other; there must be a sequence before or after each one.

**Three.js** (`@remotion/three`; install `three @react-three/fiber @remotion/three @types/three`)
- `<ThreeCanvas width height ...R3F Canvas props>`: re-provides Remotion contexts inside R3F. `width` and `height` are required.
  - Animate from `useCurrentFrame()`, never R3F `useFrame()`.
  - Since 4.0.528 it inherits the Sequence timing and premount props, with `showInTimeline` defaulting to `false` and `name` to `"<ThreeCanvas>"`.
  - During render `frameloop` is forced to `'never'`: after an async texture update call `advance(performance.now())`, not `invalidate()`.
  - Any `<Sequence>` inside it needs `layout="none"`.
- `<ThreeWebGPUCanvas>` (4.0.503, experimental in Three.js): import from `@remotion/three/webgpu`; needs three 0.167+, @react-three/fiber 9+ and React 19. Same props minus `gl`. Falls back to WebGL 2. TSL comes from `three/tsl`. In Remotion 4 render with `--gl=angle` (or `swangle` without a GPU), otherwise the canvas may come out empty.
- `useVideoTexture(videoRef)` (needs a hidden `<Html5Video>`) and `useOffthreadVideoTexture({src, playbackRate, transparent, toneMapped, delayRenderTimeoutInMilliseconds, delayRenderRetries})` (4.0.83, render only) are both **deprecated**; use `@remotion/media` `<Video headless onVideoFrame>` into a `CanvasTexture`.
- SSR: the config file does not apply, so pass `chromiumOptions: {gl: 'angle'}` to `renderMedia()`, `renderFrames()`, `getCompositions()`, `renderMediaOnLambda()` and `renderMediaOnVercel()`.

**Other integrations**
- **Skia** (`@remotion/skia` + `@shopify/react-native-skia`):
  - Enable in the config with `Config.overrideWebpackConfig((c) => enableSkia(c))` (`@remotion/skia/enable`).
  - The entry point must `await LoadSkia()` (from `@shopify/react-native-skia/src/web`), then dynamically import the Root and call `registerRoot`.
  - Draw with `<SkiaCanvas>`; render with `--gl=angle`. Template: `npx create-video --skia`.
  - The React 19 page says React Native Skia does not support React 19 yet (see Open questions).
- **Rive**: `@remotion/rive` provides `<RemotionRiveCanvas>`.
- **Spline**: the "Code (Experimental)" react-three-fiber export plus `@splinetool/r3f-spline`, placed in `<ThreeCanvas>`; drive the camera with `useThree` and animate with `interpolate`/`spring`. The tutorial is marked out of date.
- **Third-party animation libraries** (`third-party.md`): everything must be driven by `useCurrentFrame()`.
  - Supported through packages or examples: GSAP (`@remotion/gsap`), Lottie (`@remotion/lottie`, also the After Effects route), GIFs (`@remotion/gif`), Anime.js (example repo), CSS animations (paused and driven by a negative `animation-delay`).
  - Matter.js: no integration; bake the simulation to data first.
  - Not supported: Framer Motion, react-spring (use `spring()`). Reanimated shares code with `interpolate`, `spring` and `Easing`.

### 3.6 Props, schemas and visual editing

- Type the component as `React.FC<Props>`. A `<Composition>` whose component takes props **must** have `defaultProps`.
- Input props must be a JSON-serialisable object.
  - CLI: `--props='{"a":1}'` or `--props=./props.json`.
  - SSR: pass the same `inputProps` to **both** `selectComposition()` and `renderMedia()`.
  - Root component: read them with `getInputProps()`.
- Resolution: `defaultProps`, then input props (they win), then `calculateMetadata()` may transform both props and metadata. In the Studio, edits in the sidebar change the defaults (invalid edits get a red outline and are not applied). The Render button pre-fills its form with them. Starting the Studio with `--props` makes those values win over the defaults and the sidebar edits (`calculateMetadata()` still runs on them); the docs advise against it.
- Schemas: `npx remotion add zod`. The top level must be `z.object()`. Pass `schema` to `<Composition>` with matching `defaultProps`; the component type is `z.infer<typeof schema>`. `@remotion/zod-types` adds `zColor()`, `zTextarea()`, `zMatrix()`. It is based on Zod v4 since 4.0.426; `@remotion/zod-types-v3` stays on Zod 3.22.3.
- Studio controls (sidebar "Props" tab, Cmd/Ctrl+J):
  - Inferred from `defaultProps` since 4.0.516.
  - An explicit schema wins. Schema controls exist for object, string, date, number, boolean, array, union of two types where one is null/undefined, optional, nullable, enum, `zColor`, `zTextarea`, `zMatrix`, `staticFile` paths as strings, `.min()`, `.max()`, `.step()`.
  - JSON editing mode is available.
  - **Saving to code only works if `defaultProps` is an inline object literal inside `<Composition>`.**
  - Selecting a `<Sequence>` in the timeline gives offset, scale, rotation, transform-origin (draggable pivot) and opacity controls.
- The schemas page includes an agent prompt for making a composition parameterisable. In short: define a TypeScript prop type, add inline `defaultProps` that reproduce the current output, and add Zod only when validation, choices or special controls are needed.

### 3.7 Rendering and output

**Ways to render** (`render.md`, `ssr.md`)
- Studio "Render" button; the Studio can also be deployed to a server.
- CLI: `npx remotion render <id> [out]` (an interactive picker if `id` is omitted); `npx remotion still`.
- Node/Bun (`@remotion/renderer`), Lambda (fastest in the cloud), Vercel Sandbox (simplest), GitHub Actions, Docker, Azure Container Apps, Cloudflare Containers.
- Cloud Run is alpha and not actively developed.
- In the browser: `@remotion/web-renderer`, API stable since 4.0.491. WebCodecs via Mediabunny, no bundling step, a subset of tags and CSS, telemetry always on.

**`@remotion/renderer`** (the **config file has no effect** here; pass every option explicitly)

```ts
const serveUrl = await bundle({entryPoint: path.resolve('./src/index.ts')}); // once, reuse
const composition = await selectComposition({serveUrl, id: 'MyComp', inputProps});
await renderMedia({composition, serveUrl, codec: 'h264',
  outputLocation: 'out/MyComp.mp4', inputProps,
  chromiumOptions: {gl: 'angle'},   // only if WebGL content
  licenseKey: 'free-license'});     // see telemetry
```

- Other functions: `getCompositions()`, `renderStill()`, `renderFrames()` + `stitchFramesToVideo()` (the old two-step flow; `renderMedia()` is faster), `openBrowser()` (reuse one browser), `makeCancelSignal()`, `getVideoMetadata()`, `getSilentParts()`, `extractAudio()`, `getCanExtractFramesFast()`.
- Bundler overrides: pass `bundlerOverride` to `bundle()` (4.0.498), or the older `webpackOverride`. Rspack exists since 4.0.426.
- Linux needs Chrome Headless Shell libraries. `@remotion/bundler` cannot run inside Next.js (use Lambda).

**Output options**
- **GIF** (3.1): `--codec=gif` / `codec: 'gif'`.
  - `everyNthFrame` (default 1; 2 turns 30 fps into 15 fps; the first frame is always included; with `frameRange` it counts from the range start).
  - `numberOfGifLoops` (`null` means forever, `0` plays once, `1` plays twice).
  - Transparent GIF needs `imageFormat: 'png'`. Use 4.0.138+ for better colours; GIFs are limited to 256 colours.
- **ProRes** (2.1.7): `.mov` output, `--codec=prores`, `--prores-profile`, `proResProfile`, `Config.setProResProfile()`, or `defaultProResProfile` from `calculateMetadata`.
  - Profiles: `proxy` (~45 Mbps), `light` (~102), `standard` (~147), `hq` (default, ~220), `4444` (~330, alpha), `4444-xq` (~500, alpha).
  - `crf` is unsupported and `videoBitrate` is ignored. Only for editing workflows, never web delivery.
- **Transparency**:
  - WebM (Chrome/Firefox playback): `--image-format=png --pixel-format=yuva420p --codec=vp8` (or vp9).
  - ProRes for editing software: `--codec=prores --prores-profile=4444 --image-format=png --pixel-format=yuva444p10le`.
  - Either set can be returned from `calculateMetadata` as `defaultCodec`, `defaultVideoImageFormat`, `defaultPixelFormat`, `defaultProResProfile`.
  - The composition must have no opaque background (check with the Studio checkerboard).
- **Stills** (2.3): `<Still>` + `npx remotion still --props=... id out.png`; `--image-format` png (default), jpeg, webp, pdf; `--frame` picks the frame. Also `renderStill()`, `renderStillOnWeb()`, `renderStillOnLambda()`, `renderStillOnCloudRun()`. Preview in an app with `<Thumbnail>` from `@remotion/player`.
- **Other outputs**: image sequence (`--sequence`), audio-only export.
- **Scaling** (2.6.7):
  - `--scale`, the `scale` option (renderStill, renderFrames, the Lambda, Vercel and Cloud Run functions, renderMediaOnWeb, renderStillOnWeb), or `Config.setScale()`.
  - Maximum 16. Values below 1 shrink. Since 4.0.328 odd or fractional sizes are rounded automatically.
  - Text, SVG and large-enough images get sharper. Canvas and WebGL need `pixelDensity`. Videos cannot be upscaled.
- **Quality**:
  - CRF is the main knob (range depends on the codec; with hardware acceleration you cannot set it, so use `--video-bitrate`). `--crf` and `--video-bitrate` exclude each other.
  - `--jpeg-quality` (default 80) or `--image-format=png`. `--x264-preset` for H.264.
  - `--color-space=bt709` for accurate colours (the default in v5).
  - Render at `--scale=2` for text that stays crisp on HiDPI screens.
- **Metadata** (4.0.216):
  - Set with `--metadata` (CLI, Lambda, Cloud Run), or the `metadata` option of `renderMedia`, `renderMediaOnWeb` (4.0.517), `renderMediaOnLambda` and `renderMediaOnCloudrun`.
  - MP4/MOV accept only a fixed key list: title, artist, album_artist, composer, album, date, genre, copyright, grouping, lyrics, description, synopsis, show, episode_id, network, keywords, plus the int8 keys episode_sort, season_number, media_type, hd_video, gapless_playback, compilation.
  - WebM/MKV accept any keys. Keys are case-insensitive.
  - Remotion writes `comment: Made with Remotion <version>` (custom comments are merged). Inspect with `npx remotion ffprobe`.
- **Batch**:
  - CLI: `npx remotion compositions src/index.ts -q` in a shell loop.
  - Node: `bundle()` once, `getCompositions()`, then `renderMedia()` for each composition.
- **GitHub Actions**: a `workflow_dispatch` job runs `npm i` and `npx remotion render`, then uploads the file with `actions/upload-artifact@v4`. For props, write `${{ toJson(github.event.inputs) }}` to `input-props.json` and pass `--props`.

**Vercel** (`vercel.md`, `vercel-sandbox.md`)
- Deploy the Studio: build command `bunx remotion bundle`, output folder `build`. Any deployed bundle URL can be a serve URL: `npx remotion render https://site HelloWorld`.
- Sandbox template: `npx create-video@latest --template vercel`, plus a Blob store.
- `@remotion/vercel` flow: `createSandbox()`, `addBundleToSandbox({sandbox, bundleDir})`, `renderMediaOnVercel({sandbox, compositionId, inputProps, detached: true, vercelBlob: {blobToken, access: 'public'}})` returns `{sandboxId, cmdId}`. Poll `getRenderProgress({sandboxId, cmdId})` and stop the sandbox when finished.
- Limits: sandbox 45 min (Hobby) or 5 h (Pro/Enterprise); 10 or 2000 concurrent; functions run at most 800 s, so use detached mode for long renders.
- Renders happen on one machine, slower than Lambda. Add rate limiting, caching and spend limits, and clean up Blob data (it persists indefinitely).
- Lambda can also be triggered from a Vercel function (`renderMediaOnLambda` + `speculateFunctionName({diskSizeInMb: 10240, memorySizeInMb: 2048, timeoutInSeconds: 120})`).

**Telemetry and licence keys** (`telemetry.md`)
- SSR sends a telemetry event only when `licenseKey` is set, and only for successful renders.
- `renderMediaOnWeb()` / `renderStillOnWeb()` **always** send one (success or failure, not on abort), including `window.location.origin`, and the end user's IP reaches Remotion (mention it in the app's privacy policy).
- `licenseKey: 'free-license'` declares free eligibility (it also silences the browser warning). Companies use their private key for SSR (for example `process.env.REMOTION_PRIVATE_LICENSE_KEY`) and a public `rm_pub_...` key for client-side rendering.
- Telemetry never blocks, slows or fails a render. `getUsage()` from `@remotion/licensing` supports spend controls.

### 3.8 Tooling and integration

- **Tailwind v4** (from 4.0.256):
  1. `npm i -D @remotion/tailwind-v4 tailwindcss`.
  2. `Config.overrideBundlerConfig((c) => enableTailwind(c))`, and pass the same override to `bundle()`.
  3. `src/index.css` with `@import 'tailwindcss';`, imported at the top of `Root.tsx`.
  4. `package.json` must not say `"sideEffects": false` (use `["*.css"]`).
  - v3 (3.3.95): `@remotion/tailwind`, `@tailwind` directives, `tailwind.config.js` with content `./src/**/*.{ts,tsx}`. v2 is legacy (manual postcss-loader rule, and the `node_modules/.cache` caching bug).
- **TypeScript path aliases** are not resolved. Add each alias through `Config.overrideBundlerConfig` (and `bundlerOverride` for `bundle()`), or use `tsconfig-paths-webpack-plugin` (Webpack only, not Rspack). The docs advise against aliases because they can hijack `import ... from 'remotion'` when a local `remotion/` folder exists.
- **Dynamic imports**: `require(variable)` fails ("Cannot find module"). Prefer `staticFile()` with computed names, or put the expression inside `require('./assets/' + name)` so Webpack bundles the whole folder.
- **Testing**: wrap components in `<Thumbnail component compositionWidth compositionHeight durationInFrames fps frameToDisplay noSuspense/>` (`noSuspense` since 4.0.271) and use `renderToString`, React Testing Library, Bun + Happy DOM, or Playwright.
- **Player in other frameworks**:
  - Svelte and Vue: mount React with `createRoot` inside a wrapper component, pass data as `inputProps`, re-render on change, unmount on destroy. Vue also needs `@vitejs/plugin-react` with `include: /\.(jsx|tsx)$/` and `"jsx": "react", "jsxImportSource": ""`.
  - Starters: remotion-dev/svelte-starter, remotion-dev/vue-starter.
- **Player app to Remotion project**: `npm i --save-exact @remotion/cli@<version>`, then a `remotion/Root.tsx` with `<Composition>` and a `remotion/index.ts` calling `registerRoot`. Run `npx remotion studio` or `npx remotion render remotion/index.ts`. A Player cannot "download" a video; render it on a server.
- **Studio project to app**: scaffold the Next.js, Next.js (Vercel Sandbox) or React Router 7 template, copy the Root and components until `npx tsc -w` passes, copy `public/`, put the `<Player>` in `app/page.tsx` (Next) or `app/home.tsx` (RR7), and share constants such as fps and duration.
- **Starting the Studio**: `npm run dev` (newer templates), `npm start` (older), `npm run remotion` (Next/RR7 templates); all are `npx remotion studio`, on port 3000 or the next free port. The Studio also shows "Browse Elements" (first-party Remotion Elements plus added third-party libraries).
- **`@remotion/studio-protocol`** (4.0.502): lets a website hand Elements to a running Studio: `createElementPayload()`, `setStudioDragData()` (drag and drop, shown as unverified), `installInStudio()` (confirmation dialog), `addElementLibraryToStudio()`, `buildOpenInRemotionNewUrl()`.
- **React versions**: React 18 needs Remotion 3.0+ (`React.FC` no longer includes `children`). React 19 needs 4.0+ (ref type fixes in 4.0.236); pair it with @react-three/fiber 9.1.2 + three 0.171.0, styled-components v6, Next.js 15.
- **Versions**: pin every Remotion package to the same exact version (no `^`). Check with `npx remotion versions`; upgrade with `npx remotion upgrade`. Libraries declare `remotion` as a peer dependency plus a dev dependency, never a direct dependency. Same-major upgrades are safe except for APIs marked experimental. `<Experimental.Null>` was removed in 4.0.228. React Native is not supported.
- **Paid and template products**:
  - `<Timeline>` (remotion.pro): multi-track drag and drop, keyboard shortcuts, a `CanvasComposition` that renders the timeline state in the Player, a zoomable timeline with `<ZoomSlider>`, theming through Tailwind variables.
  - Remotion Recorder template: see recipes.
  - Editor Starter.
- **Security**:
  - Environment variables prefixed `REMOTION_`, and those in `.env`, are exposed to the headless browser.
  - Never call `@remotion/lambda` from a frontend (it would expose AWS credentials).
  - `disableWebSecurity` turns off the same-origin policy.
  - Put auth and rate limits on endpoints that trigger renders.
  - Report vulnerabilities to security@remotion.dev (terms) or hi@remotion.dev (security page).

---

## 4. Recipes

### 4.1 Timeline and editing

**R1. Scene list with overlaps and gaps.** Use `<Series>` with `offset`: a negative offset overlaps the previous scene (a cross-fade window if both scenes animate opacity); a positive offset leaves a gap. For real transitions use `<TransitionSeries>`, and remember the total length shrinks by each transition's length.

```tsx
<Series>
  <Series.Sequence durationInFrames={3 * fps} premountFor={fps}><Intro /></Series.Sequence>
  <Series.Sequence durationInFrames={4 * fps} offset={-10}><Demo /></Series.Sequence>
  <Series.Sequence durationInFrames={2 * fps}><Outro /></Series.Sequence>
</Series>
```

**R2. Trim, delay, trim plus delay.** Delay: `<Sequence from={30}>`. Cut the end: `durationInFrames={45}`. Start part-way into an animation: `trimBefore={15}` (4.0.482), or the classic nesting `<Sequence from={30}><Sequence from={-15}>...` (outer delays, inner negative `from` trims).

**R3. Slow motion or fast forward of any animated subtree (4.0.528).** `<Sequence playbackRate={0.5}>` halves the speed of everything inside that uses `useCurrentFrame()`, including media. The rate must stay constant, and animations computed in the parent keep the parent speed. For a changing speed (a ramp), split into consecutive sequences with different constant rates and matching `trimBefore` values, or use the accelerated-video technique for media.

**R4. Freeze frame / hold.** `<Sequence freeze={20}>` holds the children at local frame 20 without remounting (4.0.476). Combine it with a `<Series>` scene to hold on a key moment, then continue.

**R5. Wipe reveal without masks.** Animate the crop props (4.0.500) on `<Sequence>` or `<Solid>`:

```tsx
const reveal = interpolate(frame, [0, 30], [1, 0], {extrapolateRight: 'clamp'});
<Sequence cropRight={reveal} style={{borderRadius: 24}}>
  <Card />   {/* revealed left to right; inline borderRadius is kept on the crop */}
</Sequence>
```

**R6. Drop in a component designed for another size.** `<Sequence width={1080} height={1920}>` gives the child its own `useVideoConfig()` dimensions (4.0.80). Scale the sequence with CSS `scale` to fit.

**R7. Jump cuts from one long take without remounting** (`examples/video-with-jump-cuts`): keep one video element mounted and compute its start offset for the current output frame from a list of kept sections; set `durationInFrames` in `calculateMetadata` as the sum of the section lengths. The example uses `<OffthreadVideo startFrom>` (now `trimBefore`), `pauseWhenBuffering`, and a `#t=0,` suffix on the URL to opt out of the automatic time fragment. For silence detection feed `getSilentParts()` (`@remotion/renderer`) into the sections list. The Recorder template also trims silence at the start and end of each take.

**R8. Loop a clip.** `@remotion/media` `<Video loop>` loops the `[trimBefore, trimAfter)` range. For `<OffthreadVideo>` (no `loop`): read the duration with Mediabunny inside `delayRender`/`continueRender` and wrap it in `<Loop durationInFrames={Math.floor(duration * fps)}>` during render; use `<Html5Video loop>` in preview (the docs' `LoopableOffthreadVideo`).

**R9. Different tag in preview and in render.** `const {isRendering} = useRemotionEnvironment()`, then return the render-grade tag (`@remotion/media` `<Video>`) when rendering and a lighter or more compatible one in preview.

### 4.2 Motion and look

**R10. Frame-rate-independent timing.** `interpolate(frame, [1 * fps, 2 * fps], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`; `spring({frame, fps, durationInFrames: 2 * fps, delay: 1 * fps})`; `<Interactive.Div durationInFrames={3 * fps}>`. To let users pick 30 or 60 fps, have `calculateMetadata` return `{fps: props.frameRate === '60fps' ? 60 : 30}`. Never use an "FPS converter" wrapper: it breaks media tags.

**R11. Smooth entrance and timed exit** (`template-overlay/src/Overlay.tsx`): entrance `spring({frame, fps, config: {mass: 0.5}})` for a slight pop. The exit starts 20 frames before the end: `spring({frame: frame - durationInFrames + 20, fps, config: {damping: 200}, durationInFrames: 20})`, mapped to `translate` and `rotate`. The styles use the individual `scale`, `translate` and `rotate` properties.

**R12. Stop-motion / on-twos / choppy style.** Add `posterize: 2` or `3` to `interpolate()` or `interpolateColors()` (4.0.470). For a "boiling" hand-drawn line, keep `progress={1}` and animate `seed` with `interpolate(frame, [0, 89], [1, 90], {posterize: 10})`.

**R13. Hand-drawn emphasis on a word.** `<Highlight progress={interpolate(frame, [0, 25], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} color="rgba(255,236,79,0.62)" roughness={2.3} padding={{left: 20, right: 20}} bowing={0}>word</Highlight>`. Timings used on the docs page: underline 14-35, strike-through 10-25, crossed-off 18-39 (10 iterations), box 0-23, bracket 0-60, circle 0-43 with `Easing.bezier(0.42, 0, 0.58, 1)`. A highlight with `easing: [Easing.spring({damping: 200, allowTail: true, durationRestThreshold: 0.02})]` feels natural.

**R14. Deterministic particles or scatter.** Positions from `random(`x-${i}`)` and `random(`y-${i}`)`; motion from `noise3D('x', i / COLS, j / ROWS, frame * speed) * maxOffset`; opacity from `interpolate(noise3D('opacity', i, j, frame * speed), [-1, 1], [0, 1])`. Overscan the grid by about 100 px so edges stay covered. For one random pick per render (a random theme, say), use `Math.random()` inside `calculateMetadata()` and pass the result as a prop.

**R15. Shader backgrounds.** `<Solid width={width} height={height} color="black" effects={[halftoneLinearGradient({...})]}/>`; retro rays with `starburst({rays, colors, rotation: interpolate(frame, [0, durationInFrames], [0, 360])})`. Warp live DOM (a title card, a UI mock) by wrapping it in `<HtmlInCanvas effects={[fisheye({fieldOfView: 2.5})]}>`. Always render with `--gl=angle` on Remotion 4, and pass `pixelDensity={usePixelDensity()}` when rendering with `--scale`.

**R16. Motion blur.** Wrap a fast-moving layer in `<HtmlInCanvasMotionBlur>` (best quality; needs the Chrome flag only for preview). If colours must stay exact and the flag is not available, use `<CameraMotionBlur shutterAngle samples>` and check the colours. `<Trail>` gives a stylised echo.

**R17. Keep CSS keyframe animations frame-accurate** (`examples/css-animation-play-state`): set `animationPlayState: 'paused'` and `animationDelay: -(progress * durationSeconds) + 's'`, with `progress = interpolate(frame, [0, fps * durationSeconds], [0, 1], {extrapolateRight: 'clamp'})`.

**R18. 3D product spin with an inset video** (`repo/packages/template-three/src/Phone.tsx`):
- Camera: in `useEffect`, set the camera via `useThree`.
- Rotation: `interpolate(frame, [0, durationInFrames], [0, Math.PI * 6])` plus an entrance `spring({config: {damping: 200, mass: 3}})` driving scale, a one-turn spin and a lift from y = -4.
- Screen: `<Video src headless muted onVideoFrame>` draws each frame into an `OffscreenCanvas` behind a `CanvasTexture`.
- Per the docs, while rendering call `advance(performance.now())` after updating the texture (the template calls `invalidate()`).

### 4.3 Audio

**R19. Spectrum bars that look good.**
- Get `numberOfSamples` 64 or 128 from `visualizeAudio()`. Keep the lower part of the spectrum (the template's `highFreqCutoff` is 0.5), pick log-spaced bins, boost the highs, normalise to the maximum, then apply a slight power of 0.9 (`template-music-visualization/src/helpers/process-frequency-data.ts`).
- Simpler alternative that matches WebAudio's analyser: `db = 20 * Math.log10(v)`, then `(db + 100) / 70`, clamped to 0..1.

**R20. Bass-reactive flash** (`template-music-visualization/src/Visualizer/BassOverlay.tsx`): `useWindowedAudioData({src, frame, fps, windowInSeconds: 30})`, `visualizeAudio({..., numberOfSamples: 128, optimizeFor: 'speed', dataOffsetInSeconds})`, average the first 32 bins times 3, then `opacity = Math.min(0.5, avg * 0.8)` on a full-frame colour layer.

**R21. Keep the visualisation in sync with an offset audio.** Wrap the `<Audio>` and all visualisers in one `<Sequence from={-audioOffsetInFrames}>` (template-music-visualization `Main.tsx`). The visualiser's `useCurrentFrame()` then equals the position in the audio file, which is what `visualizeAudio` expects.

**R22. Long podcasts.** Use `useWindowedAudioData` (Range requests, a few windows in memory) instead of `useAudioData` (whole file decoded). Pass `dataOffsetInSeconds` through.

**R23. Match the source sample rate.** In `calculateMetadata`: `const track = await new Input({formats: ALL_FORMATS, source: new UrlSource(props.src)}).getPrimaryAudioTrack(); return {props, defaultSampleRate: track?.sampleRate};`.

**R24. Sound design.** `@remotion/sfx` URLs (whoosh on transitions, mouse-click on UI demos, shutter on photo reveals, page-turn, ding, ui-switch), peak-normalised to -3 dB, no attribution required. Lower the level with `volume`.

**R25. Speed-changed video with natural audio.** `@remotion/media` changes pitch with `playbackRate`. If the pitch must not change, mute the sped-up video and lay the audio separately, or accept the fallback tags' pitch-preserving behaviour (`<OffthreadVideo>` / `<Html5Audio>` preserve pitch in preview and SSR).

**R26. Local captions pipeline.** `@remotion/whisper-webgpu` (browser or Node; needs a GPU) produces captions through `toCaptions()`. `@remotion/install-whisper-cpp` is the server option. Recorder-style caption craft: word-level timings, balanced lines with no orphan words, backtick terms set in monospace, an autocorrect function for common misspellings, captions stored as editable JSON.

### 4.4 Output formats and delivery

**R27. Transparent overlay for an editor (FCP, Premiere, Resolve).** Give the component a `transparent` prop that drops the background, and set:

```ts
// remotion.config.ts (CLI / Studio only; SSR needs the same values passed explicitly)
Config.setVideoImageFormat('png');
Config.setPixelFormat('yuva444p10le');
Config.setCodec('prores');
Config.setProResProfile('4444');
Config.setMuted(true); // template-overlay also mutes
```

**R28. Transparent video for the web.** VP8/VP9 + `yuva420p` + PNG frames. Also render an opaque MP4 fallback (two npm scripts), and choose between them with `<source>` or `canplay`. On Lambda prefer ProRes for alpha (WebM alpha flickers at chunk seams), or render WebM locally in one pass.

**R29. Social formats** (from the Recorder page; the last bullet is my suggestion):
- X / LinkedIn: 1:1, muted autoplay, so captions must be burned in (square gets more views on X per the Buffer study the page cites).
- YouTube: 16:9, audio on, captions as `.srt`, an end card with related-video cut-outs and a "Subscribe" call to action.
- TikTok / Reels / Shorts: 9:16, keep the bottom clear (the UI covers it), word-by-word captions.
- Make one composition take the aspect ratio as a prop and set `width`/`height` in `calculateMetadata`.

**R30. Crisp text for HiDPI screens.** Render 1080p compositions with `--scale=2` (and `pixelDensity={usePixelDensity()}` on canvas layers). Use `--color-space=bt709` for accurate colours.

**R31. GIF for docs or chat.** `--codec=gif --every-nth-frame=2 --number-of-gif-loops=0` (0 plays once) or leave loops unset for an infinite loop. Keep the palette simple (256 colours).

**R32. Thumbnails and OG images.** A `<Still>` next to the video `<Composition>`, rendered with `npx remotion still --frame=N` or `renderStill()`. Formats png, jpeg, webp, pdf.

**R33. Embed metadata.** `--metadata title="..." --metadata artist="..."` (MP4 accepts only the fixed key list).

**R34. Render every composition.** Shell loop over `npx remotion compositions src/index.ts -q`, or Node: `bundle()`, `getCompositions()`, then `renderMedia()` each.

**R35. A small render server** (`repo/packages/template-render-server/server/render-queue.ts`): a job map plus a promise chain as a sequential queue. Per job: `makeCancelSignal()`, `selectComposition()`, `renderMedia({cancelSignal, onProgress})`, and a state of queued, in-progress (with progress), completed (with URL) or failed (with error).

### 4.5 Video apps (Player, uploads)

**R36. Upload flow.** Check `canDecode(file)` (Mediabunny snippet). Show the file at once through `URL.createObjectURL(file)` passed as an input prop to `<Player>`. Upload directly to S3 with a presigned PUT URL (server: `getSignedUrl`, `PutObjectCommand`, a size limit such as 200 MB, a UUID key). Then switch the prop to the cloud URL and `URL.revokeObjectURL()` the blob (blob URLs cannot seek efficiently). Track progress with `XMLHttpRequest` `upload.onprogress`.

**R37. Smooth Player playback.** Premount upcoming sequences. Use `useBufferState().delayPlayback()` while your own data loads, and `prefetch()` / `@remotion/preload` only when really needed (`free()` afterwards). If the audio source changes during playback, `prefetch(url).waitUntilDone()` before swapping it in (this avoids the non-seekable error).

**R38. Parameterise a composition for non-coders.** Inline `defaultProps`, then either rely on inferred controls or add `schema` with `zColor()` / `zTextarea()`. Teammates edit in the Studio sidebar and press Render; the Studio can be deployed as a URL.

---

## 5. Performance and render stability

### 5.1 What breaks deterministic parallel rendering

- `Math.random()` anywhere in render code, including `useState(() => Math.random())`: each tab gets different values, so elements jump between frames rendered by different tabs. Use `random(seed)`. True randomness is fine inside `calculateMetadata()` (it runs once).
- Animation driven by anything other than the frame: R3F `useFrame()`, `requestAnimationFrame`, timers, running CSS animations or transitions, Framer Motion, react-spring, un-baked physics engines. Every value must come from `useCurrentFrame()`.
- Changing React `key`s every frame (for example `key={uuid()}`) remounts media on every frame ("error creating media player").
- `invalidate()` after an async texture update inside `<ThreeCanvas>` while rendering: the scene re-renders asynchronously and the screenshot can show the previous frame, especially with concurrency above 1. Use `advance(performance.now())`.
- Transparent WebM rendered in chunks (Lambda): alpha flickers at chunk boundaries.
- `<Html5Video>` is not frame-perfect. Use `@remotion/media` `<Video>` or `<OffthreadVideo>` for final renders.
- Assets that are not loaded when the screenshot is taken: always go through Remotion tags or `useDelayRender()`.

### 5.2 Speed

- **Video tags**: `@remotion/media` `<Video>` is fastest and downloads only what it needs. `<OffthreadVideo>` must download the whole file first (this can exceed the 30 s timeout for big files). `<Html5Video>` is medium.
- `<OffthreadVideo transparent>` extracts PNG instead of BMP (slower). `toneMapped={false}` skips colour conversion.
- **Concurrency**: both too high and too low slow things down. Find the value with `npx remotion benchmark`. Too high also causes crashes ("Target closed"), timeouts, and Chrome refusing to load `<Html5Video>`s.
- **GPU-bound content on CPU-only cloud machines** is slow: WebGL (Three, Skia, P5, Mapbox), 2D canvas, `box-shadow`, `text-shadow`, `linear-gradient()`, `radial-gradient()`, `filter: blur()`, `filter: drop-shadow()`. Precompute such layers as images when possible.
  - Remotion 4: `--gl=angle` for WebGL/WebGPU; `swangle` when there is no GPU (the default on Lambda and Cloud Run); `vulkan` with Chrome for Testing on GPU Linux servers. `npx remotion gpu` shows what is available.
  - Remotion 5 picks automatically.
- **Image format**: `jpeg` (default, quality 80) is faster than `png`; PNG is only needed for transparency.
- **Codecs**: VP8/VP9 encode slowly. ProRes files are huge.
- **Resolution**: output scaling costs time. Only scale up for text crispness when it matters.
- **JavaScript cost**: memoise heavy calculations (`useMemo`, `useCallback`). Measure data fetching and cache results. Add `console.time` around suspects.
- **Audio visualisation**: `optimizeFor: 'speed'` for large `numberOfSamples` or Lambda.
- **Measure**: `--log=verbose` lists the slowest frames (the first frames of each tab are slow because of start-up).

### 5.3 Memory

- `useAudioData()` decodes the whole file into memory; `useWindowedAudioData()` keeps about three windows.
- `prefetch()` holds whole files in memory until `free()`.
- High concurrency means more Chrome tabs, which leads to out-of-memory crashes ("Target closed"). On Lambda, raise the memory size.

### 5.4 Timeouts and loading

- Each `delayRender()` must be cleared within 30 s by default (the message mentions 28000 ms).
- Raise the limit:
  - Studio: render dialog, "Advanced".
  - CLI: `--timeout`; config: `Config.setDelayRenderTimeoutInMilliseconds()`.
  - SSR, Lambda and Vercel APIs: `timeoutInMilliseconds` (Cloud Run: `delayRenderTimeoutInMilliseconds`).
  - One call: `delayRender(label, {timeoutInMilliseconds})` (4.0.140).
  - Media and image tags: the `delayRenderTimeoutInMilliseconds` prop (4.0.140).
- Label your `delayRender('Fetching data...')` calls (2.6.13) so a timeout names the culprit.
- Check network reach in the render environment (a VPC or firewall may block font, image or media URLs).

### 5.5 Preview smoothness (Player and Studio)

- Premount (`premountFor`); postmount for backwards scrubbing (`postmountFor`); `styleWhilePremounted` to hide premounted content.
- Buffer state: media tags can pause the Player while loading (`pauseWhenBuffering`, default `true` in v5). Use `useBufferState()` for custom loaders.
- Media must be served with status 200, a proper `Content-Type`, `Content-Range` and `Content-Length`, and ideally faststart. Blob URLs cannot range-request, so swap them for real URLs soon.

### 5.6 Other stability notes

- Put `registerRoot()` in its own file (Fast Refresh).
- Pin all Remotion packages to one exact version. A mismatch gives subtle bugs or total breakage.
- The config file does not apply to Node APIs. Every setting that matters (gl, codec, pixel format, image format, scale, timeout, sample rate) must be passed explicitly in SSR code.
- Telemetry never fails a render.
- Audio is always resampled to one output rate (48 kHz default). Mixed sources cannot keep their own rates.

---

## 6. Errors and fixes

| Symptom / message | Cause | Fix |
|---|---|---|
| `Could not play video with src ... [object MediaError]` (or audio) | Codec Chrome cannot play (HEVC on Linux, AVI, FLV); 404; missing `staticFile()`; bad headers; Internet Download Manager | Convert the file; use `staticFile('name.mp4')` for `public/` files; serve status 200 with `Content-Type` and `Content-Range`; use `onError` (3.3.89+) to swap in a fallback. |
| `error creating media player` | Too many video elements, often a `key` that changes every frame | Stable keys; switch to `@remotion/media` `<Video>` (no native element). |
| `The media [src] cannot be seeked` | Media swapped during playback without preload; server lacks `Content-Range`/`Content-Length`; no faststart; blocking headers (`X-Frame-Options`, CSP `frame-ancestors`, `Cross-Origin-Resource-Policy: same-origin`) | `prefetch(url).waitUntilDone()` before swapping; host with Range support; import locally; use `@remotion/media` `<Video>` (renders fine); check with `getVideoMetadata()`. |
| `A delayRender() was called but not cleared after 28000ms` | Missing `continueRender()`; network blocked; memory pressure; big `<OffthreadVideo>` download; old Remotion | Clear every handle; check network; lower concurrency; raise the timeout; use `@remotion/media`; label handles. |
| `Target closed` | Chrome tab crashed: missing Linux libraries, out of memory or CPU, broken Chrome binary | Install the libraries; lower `--concurrency` (more Lambda memory); reinstall the browser; `--log=verbose` shows which binary is used. |
| `staticFile() does not support relative paths` | Passed `../public/x`, `./x`, an absolute path or `public/x` | Pass only the name inside `public/`. |
| `staticFile() does not support remote URLs` | Wrapped an https URL | Pass the URL directly. |
| `<Composition> mounted inside another composition` / `...inside the component that was passed to the <Player>` | Nested compositions, or a composition returned from the Player component | Render components directly or use `<Sequence>`; give the Player `component`, `durationInFrames`, `fps`, `compositionWidth`, `compositionHeight`. |
| `Error: Cannot find module './image0.png'` | `require(variable)` | Use `staticFile()`, or put the expression inside `require('./assets/' + x)`. |
| `random() argument must be a number or a string` | `random()` called without a seed | Pass a seed; `random(null)` for real randomness. |
| ESLint warning on `Math.random()` | Nondeterminism risk | `random(seed)`; `random(null)` if intentional. |
| `Using a slow method to extract the frame` | Remotion 3 only (gone since v4): corrupt H.264 timestamps or VP8 + PNG | Re-encode with `npx remotion ffmpeg -i in.mp4 out.mp4`; prefer VP9 or JPEG. |
| `useAudioData` throws | File has no audio track (4.0.75+) | Check first with `getVideoMetadata()` (`audioCodec === null`), or copy the hook inline to catch it. |
| Preview throws on `playbackRate` | Chrome limits 0.0625 to 16 in preview | Keep rates inside the range; reverse playback is not supported. |
| Empty or black WebGL canvas in render | No GL context in headless Chrome | `--gl=angle` / `Config.setChromiumOpenGlRenderer('angle')` / `chromiumOptions: {gl: 'angle'}` in SSR; `swangle` without a GPU. |
| Error with `<Sequence>` inside `<ThreeCanvas>` | Sequence renders a `<div>` | `layout="none"`. |
| Stale video texture frames in a Three.js render | `invalidate()` is async while `frameloop` is `'never'` | `advance(performance.now())` while rendering. |
| `import from 'remotion'` resolves to a local folder | TS aliases plus a `remotion/` folder | Avoid aliases or rename the folder. |
| Tailwind classes have no effect | Override missing in `bundle()`; `"sideEffects": false`; CSS not imported | Pass the override to `bundle()`; `"sideEffects": ["*.css"]`; import the CSS in `Root.tsx`. |
| Tailwind v2 config ignored | Cache bug | Delete `node_modules/.cache`. |
| TS errors about `children` on `React.FC` | React 18 types | Declare `children: React.ReactNode` explicitly. |
| Ref type errors with React 19 | Old types | Remotion 4.0.236 or newer. |
| Subtle breakage after installing a package | Version mismatch across `@remotion/*` | Pin exact versions; `npx remotion versions`; `npx remotion upgrade`. |
| Transparent WebM flickers at intervals on Lambda | Chunks encoded independently | ProRes 4444, a single local pass, or a larger `framesPerLambda`. |
| Soft text on Retina displays | 1x render viewed at 2x | `--scale=2`; `pixelDensity` for canvas layers. |
| Washed-out GIF colours | Old version / 256 colours | 4.0.138+; simplify the palette. |
| `crf` rejected | Hardware acceleration, or ProRes | Hardware encoding: use `--video-bitrate` instead. ProRes: `crf` is not supported and `videoBitrate` is ignored, so choose a `--prores-profile`. |
| Player buffers forever | `delayPlayback()` created in a `useState` initializer (Strict Mode) or never unblocked | Create it in `useEffect`, unblock in the cleanup. |
| Audio hiccups in Safari after `prefetch` | Safari and blob URLs | `method: 'base64'`; set `contentType` because blob URLs lose the file extension. |
| Settings in `remotion.config.ts` ignored in the Node script | The config file does not apply to Node APIs | Pass the options to `bundle()`, `renderMedia()` and so on. |
| `<OffthreadVideo>` fails in the browser renderer | Not supported in `@remotion/web-renderer` | Use `@remotion/media` `<Video>`. |
| whisper-web fails with `SharedArrayBuffer` | No cross-origin isolation | Send COOP `same-origin` and COEP `require-corp`; better, use whisper-webgpu. |
| Studio cannot save edited props | `defaultProps` not inline, or in another file | Inline the object literal in `<Composition>`. |

---

## 7. What our skills must teach

### 7.1 Hard rules (determinism and correctness)

- Every visual value is a function of `useCurrentFrame()`, `useVideoConfig()` and props. No `Math.random()`, timers, `useFrame`, or free-running CSS or JS animation. Randomness comes from `random('seed-' + i)`, or from `calculateMetadata()` passed down as props.
- Express time as `seconds * fps`; never hard-code frame numbers that assume 30 fps.
- Clamp `interpolate()` (`extrapolateLeft/Right: 'clamp'`) unless overshoot is intended.
- One `registerRoot()` in `src/index.ts`; compositions in `src/Root.tsx`; never nest `<Composition>`.
- Use Remotion tags only (`<Img>`, `<Video>`, `<Audio>`, `<IFrame>`, `<Gif>`), never raw `<img>`, `<video>`, `<audio>`, `<iframe>` or CSS `background-image` for assets.
- Files in `public/` always go through `staticFile('name.ext')` (no `./`, no `public/`, no URL encoding). Remote URLs are passed as they are.
- Wrap all custom async work in `useDelayRender()` and always continue or cancel. Label each handle.
- Inside `<ThreeCanvas>`: `width`/`height` are required, `<Sequence layout="none">`, and `advance(performance.now())` after async texture updates during render.
- All `remotion` and `@remotion/*` packages on the same exact version. For our install that is 4.0.528, and new packages are added with `npx remotion add <pkg>` so they match.
- In SSR code, remember that `remotion.config.ts` is ignored: pass `chromiumOptions.gl`, codec, pixel format, image format, scale and timeouts explicitly, and pass `inputProps` to both `selectComposition` and `renderMedia`.

### 7.2 Defaults an autonomous agent should pick

- Video and audio: `@remotion/media` `<Video>` / `<Audio>`. Use `<OffthreadVideo>` only for codecs Mediabunny lacks (the fallback already does this). Use `<Html5Video>` only for special preview needs.
- Sequencing: `<Series>` for back-to-back scenes, `<TransitionSeries>` for transitions, `<Sequence>` for layering and offsets. Add `premountFor={fps}` on scenes containing media (what v5 will do by default).
- Transforms: individual CSS `translate` / `scale` / `rotate` / `opacity` properties with inline `interpolate()` keyframes (Studio-editable).
- Easing: `spring({frame, fps, config: {damping: 200}})` for UI-grade motion without bounce; the default config when a bounce is wanted. `Easing.spring` for springs inside `interpolate()`.
- Output: H.264 MP4, JPEG frames, `--color-space=bt709`. ProRes 4444 for alpha deliverables to editors; VP9 + `yuva420p` for alpha on the web.
- Sample rate: 48 kHz unless the source is 44.1 kHz only and fidelity matters (then return `defaultSampleRate` from `calculateMetadata`).
- WebGL/WebGPU content on Remotion 4: always `--gl=angle`, or `swangle` on machines without a GPU.
- Props: inline `defaultProps`, a typed `React.FC<Props>`, and a Zod schema only when constraints or pickers are needed.
- Licence key for SSR: `licenseKey: 'free-license'` if eligible, otherwise the company's private key (see 7.6).

### 7.3 Decision tables

**Which renderer**

| Situation | Choose |
|---|---|
| Local one-off or agent pipeline on this Mac | `npx remotion render` / `npx remotion still` |
| Programmatic batch, custom server | `@remotion/renderer` (`bundle` once, `selectComposition`, `renderMedia`), a queue with `makeCancelSignal` |
| Fast, parallel cloud renders | Lambda (beware transparent WebM) |
| Simplest cloud on Vercel, long renders OK | Vercel Sandbox (`renderMediaOnVercel` detached + poll) |
| No server at all, user's browser | `@remotion/web-renderer` (subset of tags/CSS, `@remotion/media` only, telemetry always on) |
| Manual trigger with inputs | GitHub Actions `workflow_dispatch` + `--props=input-props.json` |

**Which transparency format**

| Destination | Settings |
|---|---|
| NLE (FCP, Premiere, Resolve) | `prores`, profile `4444` (or `4444-xq`), `png`, `yuva444p10le` |
| Web (Chrome, Firefox) | `vp8`/`vp9`, `yuva420p`, `png`, plus an opaque MP4 fallback |
| GIF | `gif`, `imageFormat: 'png'` |
| Lambda + alpha | ProRes (WebM alpha flickers at chunk seams) |

**Which audio-data hook**

| Case | Use |
|---|---|
| Short music bed, need the whole waveform | `useAudioData` |
| Long audio (podcast, full song) or Lambda | `useWindowedAudioData` + `dataOffsetInSeconds` + `optimizeFor: 'speed'` |
| Only the duration | `getAudioDurationInSeconds()` (no CORS needed) |

**Which motion blur**

| Case | Use |
|---|---|
| Best realism, render or preview with the flag | `<HtmlInCanvasMotionBlur>` |
| Preview without the flag, colour shifts acceptable | `<CameraMotionBlur shutterAngle samples>` |
| Stylised echo | `<Trail>` |

### 7.4 Checklists

**Before any render**
- [ ] `npx remotion versions` shows one version everywhere.
- [ ] No `Math.random`, `useFrame` or CSS animation without frame control (grep for them).
- [ ] Every asset is local via `staticFile`, or remote with correct headers (`Content-Range`, CORS if `@remotion/media`).
- [ ] WebGL/WebGPU present, so `--gl=angle` (or `chromiumOptions`).
- [ ] Transparent deliverable, so PNG frames and an alpha pixel format, and no background.
- [ ] Concurrency tuned (`npx remotion benchmark` once per machine).
- [ ] Long assets or slow APIs, so the timeout is raised and `delayRender` handles are labelled.
- [ ] Output checked: duration, fps, audio present, colour space (`npx remotion ffprobe out.mp4`).

**Making a composition editable in the Studio**
- [ ] `defaultProps` is an inline literal in `<Composition>`.
- [ ] `interpolate()` keyframe arrays written inline where they are used.
- [ ] Individual transform properties, not `transform` strings.
- [ ] `name` props on important sequences; `showInTimeline={false}` for helpers.
- [ ] Optional: `Interactive.*` elements for draggable layers (4.0.475+).

**Video app (Player + uploads)**
- [ ] Validate with `canDecode()` before upload; reject or re-encode on failure.
- [ ] Presigned PUT uploads with size limits; auth and rate limits on render endpoints.
- [ ] Blob URL for instant preview, replaced by the cloud URL, then revoked.
- [ ] Never expose Lambda or AWS credentials to the client.
- [ ] Licence: embedding `<Player>` in a company product counts as automation (see 7.6).

### 7.5 Version gates relevant to 4.0.528 (all available)

| Feature | Since |
|---|---|
| `Sequence` / `Series.Sequence` `playbackRate`; `<ThreeCanvas>` timing props; premount props on `<Solid>` / `<AbsoluteFill>` | 4.0.528 |
| `@remotion/video-matting` | 4.0.523 |
| `@remotion/whisper-webgpu` | 4.0.518 |
| Inferred Studio controls from `defaultProps` | 4.0.516 |
| `<ThreeWebGPUCanvas>` | 4.0.503 |
| `@remotion/studio-protocol` | 4.0.502 |
| `AbsoluteFill` timing props; `Sequence` `controls` | 4.0.501 |
| Crop props; `starburst()` | 4.0.500 |
| `bundlerOverride` / `overrideBundlerConfig` | 4.0.498 |
| `Series.Sequence` `trimBefore` | 4.0.497 |
| Web renderer API stable | 4.0.491 |
| `@remotion/rough-notation` | 4.0.490 |
| `Sequence` `trimBefore` | 4.0.482 |
| `outlineRef` | 4.0.479 |
| `freeze`; `Easing.spring` | 4.0.476 |
| `Interactive` | 4.0.475 |
| `usePixelDensity`; `Solid` `pixelDensity` | 4.0.472 |
| `posterize` | 4.0.470 |
| `<Solid>` and `effects` | 4.0.464 |
| `hidden`; per-segment easing array | 4.0.462 |
| Audio `requestInit` / `sampleRate` options | 4.0.458 |
| Output `sampleRate` | 4.0.448 |
| `<Series>` is a `<Sequence>` | 4.0.443 |
| `@remotion/sfx` | 4.0.429 |
| Zod v4 types; Rspack | 4.0.426 |
| `TransitionSeries.Overlay` | 4.0.415 |

Remotion 5.0 behaviour changes to be aware of (not active on 4.0.528): `premountFor` default becomes `fps`; `pauseWhenBuffering` default `true`; `visualizeAudio` `optimizeFor` default `'speed'`; `bt709` default; automatic GL selection; new Terms, Privacy Policy and mandatory licence keys for "Automators".

### 7.6 Licensing facts the skills should surface (from the v5.0 terms; v4 terms apply today)

- Free: individuals (including commercial work), teams of up to 3 people, genuine non-profits, evaluation.
- Company: "Creators" $25 per seat per month (one person writing Remotion code, including through agentic tools such as Claude Code), or "Automators" $0.01 per render with a $100 monthly minimum (any code that calls render APIs or CLI render commands, or embeds `<Player>`).
- A studio that renders in-house and delivers only MP4s does not count the client's headcount. A client that owns the Remotion code must hold the licence.
- Prompt-to-video services that generate the Remotion code with AI are allowed. Letting end users upload their own Remotion code is not allowed without approval.
- Exported project code must say it is built with Remotion and link to remotion.pro/license.
- Users own the rendered media. Codec, font and royalty rights are the user's own responsibility.

---

## 8. Best examples to learn from

| Path / URL | Why |
|---|---|
| `repo/packages/template-overlay/src/Overlay.tsx` + `remotion.config.ts` | Clean entrance and timed-exit springs using individual CSS transform properties; the complete ProRes 4444 alpha config (PNG, `yuva444p10le`, muted, Rspack). |
| `repo/packages/template-music-visualization/src/Visualizer/Main.tsx` | Aligning offset audio and visualisers with one negative-`from` Sequence; composable spectrum, waveform and bass layers from a Zod schema. |
| `repo/packages/template-music-visualization/src/Visualizer/BassOverlay.tsx` | Bass-reactive flash with `useWindowedAudioData`, `optimizeFor: 'speed'`, 128 samples. |
| `repo/packages/template-music-visualization/src/helpers/process-frequency-data.ts` | Production-grade spectrum shaping (log bins, high-frequency boost, normalisation). |
| `repo/packages/template-audiogram/src/Audiogram/` (`Spectrum.tsx`, `Oscilloscope.tsx`, `Captions.tsx`) | Podcast audiogram: visualisers plus captions in one composition. |
| `repo/packages/template-three/src/Phone.tsx` | 3D device with a video screen: `@remotion/media` `<Video headless onVideoFrame>` into a `CanvasTexture`, spring entrance, camera setup (add the `advance()` fix). |
| `repo/packages/template-three/remotion.config.ts` | Minimal 3D config: `setChromiumOpenGlRenderer('angle')`, JPEG frames. |
| `repo/packages/template-still/src/Root.tsx`, `src/server/` | `<Still>` compositions plus an image-rendering server with caching and S3. |
| `repo/packages/template-render-server/server/render-queue.ts` | A minimal, correct SSR job queue with cancel signals and progress. |
| `repo/packages/template-recorder/config/*.ts` | Recorder design system as config: layouts, scenes, transitions, sounds, end cards, captions autocorrect, themes, fps. |
| `repo/packages/template-vercel` | Reference for Vercel Sandbox rendering (`@remotion/vercel`). |
| `examples/video-with-jump-cuts/src/JumpCuts.tsx` | Jump cuts from one mounted video, `calculateMetadata` summing sections. |
| `examples/css-animation-play-state/src/Composition.tsx` | The exact trick for syncing CSS keyframes to the frame. |
| `examples/transitions-video`, `examples/light-leak-example` | Transitions and light-leak overlays in practice. |
| `examples/three-particles`, `examples/remotion-three-gltf-example`, `examples/glb-example` | Frame-driven 3D particles and model animation. |
| `examples/motion-blur-example`, `examples/html-in-canvas`, `examples/gpu-scene` | Motion blur and HTML-in-canvas / GPU effects. |
| `examples/tone-js-example` | Generated music synced to the timeline. |
| `mirror/docs/text-highlights.md` | Seven annotation styles with tuned timings, colours and roughness values. |
| `mirror/docs/video-tags.md` | The single most useful decision table for media. |
| `mirror/docs/timing.md` | The timing model and formula every agent needs. |
| `mirror/docs/sequence.md` | Full, current prop list including 4.0.5xx additions. |
| `mirror/docs/recorder.md` | Platform-native format rules (1:1, 16:9, 9:16) and caption craft. |
| `mirror/docs/resources.md` | Pointers to community component libraries (Remocn, Remotion Bits, Onda, RemotionUI, snapcn, clippkit) and agent tooling (video-shotcraft skill, Aeon). |

---

## 9. Open questions

1. **Skia and React 19**: `react-19.md` says React Native Skia has no React 19 support, while our stack is React 19. Is `@remotion/skia` usable on 4.0.528 with current `@shopify/react-native-skia`, or must Skia work be avoided or run in a React 18 side project? Needs a test.
2. **template-three uses `invalidate()`** in `onVideoFrame`, while `three-canvas.md` and `videos/as-threejs-texture.md` require `advance(performance.now())` when rendering. Does the template produce stale frames at concurrency above 1? Our skills should use the docs pattern.
3. **`Sequence playbackRate` is brand new** (4.0.528, the installed version). Edge cases (media inside, `<Series>` with `playbackRate`, the note that it speeds up "transitions" in a series) should be tested before the skills rely on it.
4. **`@remotion/media` pitch change**: speed-changed audio shifts pitch in preview, SSR and client-side rendering. Is `toneFrequency` able to compensate (for example `toneFrequency = 1 / playbackRate`)? Not stated.
5. **HTML-in-canvas flag**: `<HtmlInCanvasMotionBlur>` and `<HtmlInCanvas>` need a Chrome flag during preview. Does headless rendering on Lambda or Vercel need anything? The page says "rendering needs no configuration" but does not name environments.
6. **`@remotion/effects` package status and licence**: not installed locally and not covered in my pages beyond the preset names; check with the effects agent (D5).
7. **CORS for `@remotion/sfx` URLs** with `@remotion/media` `<Audio>` (which requires CORS): presumably served with CORS headers from remotion.media; confirm.
8. **Studio start command drift**: `preview.md` says `npm run dev`, `studio.md` says `npm start` for regular templates. Skills should just call `npx remotion studio`.
9. **Licensing for the agency**: the v5 terms (seats for people coding "through agentic tools", Automators for pipelines) apply once 5.0 ships; the current v4 terms at remotion.pro/terms-4-0 were not in my material. Team size and deliverable model decide free or paid; worth a human decision.
10. **`bundlerOverride` vs `webpackOverride`**: `ssr-node.md` and `render-all.md` still show `webpackOverride`, while the aliases page says `bundlerOverride` (4.0.498). Both probably work on 4.0.528; confirm which one to teach (probably `bundlerOverride` for Rspack compatibility).
11. **`Config.setRspack(true)`** appears in the local templates (overlay, three) but the Rspack pages were outside my set; confirm whether our remotion-broll project should enable it (faster bundling) and whether the Tailwind v4 and Skia overrides are Rspack-compatible.
