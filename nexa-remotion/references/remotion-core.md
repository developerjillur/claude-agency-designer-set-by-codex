# How Remotion works (4.0.528), in one place

The essentials an agent needs before writing any scene. Every area has a deeper file in `kb/` (the research); the
version tags say when an API arrived, so anything tagged above 4.0.528 is not available here.

## The model

1. **A video is a pure function of (frame, props).** A render opens several headless Chrome tabs; each renders any
   frame in any order with no shared state. Anything that reads wall-clock time (CSS animations and transitions,
   timers, `requestAnimationFrame`, `Date.now()`, `Math.random()`, GSAP or Lottie tickers) desynchronises across tabs
   and flickers. Compute every visual from `useCurrentFrame()`, props and static data.
2. **Time is frames.** `seconds = frames / fps`; a composition of N frames has frames 0 to N-1 (the last frame is
   N-1). CLI ranges `--frames=S-E` include both ends.
3. **Two layers.** The Root (called by `registerRoot()`) registers `<Composition>`s (`id`, `width`, `height`, `fps`,
   `durationInFrames`, `component`, `defaultProps`, `schema`, `calculateMetadata`); components render one frame.
4. **Props.** `defaultProps` (or Studio edits) merged with input props (`--props` file or JSON, `inputProps` in Node),
   optionally transformed by `calculateMetadata`, reach the component. JSON-serialisable only (plus `Date`, `Map`,
   `Set`, `staticFile()`); type props with `type`, not `interface`.
5. **Time transforms nest.** `<Sequence from durationInFrames>` shifts and trims time for its children (inside, frame
   0 is the Sequence's start, and `useVideoConfig().durationInFrames` is the Sequence's length); `<Series>` stacks
   sequences; `<Loop>` repeats; `<Freeze>` or `<Sequence freeze>` holds. Since 4.0.501 `AbsoluteFill`, `Img`,
   `Interactive.*`, `CanvasImage`, `Solid` and the media tags take `from` and `durationInFrames` directly.
6. **Readiness.** A frame is captured when no `delayRender` handle is pending. Remotion's asset components handle
   their own; your async work creates a handle in a `useState` initializer and clears it (default timeout 30 s).
7. **Assets** live in `public/` and are referenced with `staticFile('name.png')` (it URL-encodes; never encode
   yourself). No `fs`, no absolute paths.
8. **Layers are DOM order**: later siblings paint on top; `AbsoluteFill` is the layer primitive.
9. **Canvas pipeline** (4.0.455+): `Solid`, `HtmlInCanvas`, `Img` with `effects`, `CanvasImage`, `AnimatedImage`,
   `Gif`, `@remotion/media` `Video` and `@remotion/shapes` take an `effects` array (`@remotion/effects/<name>`), most
   of them WebGL2 (render with `--gl=angle`).
10. **Environments.** Studio (preview and editing), Player (embedded in apps), server render (CLI, Node, Lambda),
    client-side render (`@remotion/web-renderer`, a subset of HTML). `getRemotionEnvironment()` tells them apart.
11. **Version landscape.** Installed 4.0.528; the docs describe 4.0.529+ in places; 5.0 will change defaults
    (premounting, font weights required, bt709). Write explicit values so code behaves the same on both.

## Animation primitives

- `interpolate(input, inputRange, outputRange, options)`: input range strictly increasing; extrapolate `'extend'`
  (default), `'clamp'`, `'wrap'`, `'identity'`: **clamp both ends** for one-shot animation. `easing` is one function
  or (4.0.462) one per segment. Output may be CSS strings for `scale`, `translate`, `rotate`, `transform-origin`
  (4.0.472), numeric tuples (4.0.473), discrete strings with `Easing.step1` (4.0.509). `posterize: n` (4.0.470)
  steps values every n frames. `output: 'perceptual-scale'` (4.0.490) makes scale changes feel even.
  Guard short durations: keyframes computed from a duration throw when fades overlap.
- `Easing`: `linear`, `ease`, `quad`, `cubic`, `sin`, `circle`, `exp`, `bounce`, `step0`, `step1`, `poly(n)`,
  `elastic(b)`, `back(s)`, `bezier(x1, y1, x2, y2)`, `spring(config)` (4.0.476; `allowTail`,
  `durationRestThreshold` 4.0.483), modifiers `in`, `out`, `inOut`.
- `spring({frame, fps, config, delay, durationInFrames, from, to})`: physical 0 to 1 (defaults damping 10, mass 1,
  stiffness 100: a visible bounce; `damping: 200` settles without one). `measureSpring({fps, config})` gives its
  length in frames (30 fps, damping 200: 23 frames). Springs are numbers: add, subtract, map with interpolate.
- `interpolateColors(input, range, colors)`: blends in sRGB whatever the input space (oklch included), so add a
  middle stop between complementary colours.
- `random(seed)`: deterministic 0 to 1. `@remotion/noise` `noise2D/3D/4D(seed, ...)`: smooth noise (few seeds are
  cached: vary a coordinate, not the seed).

## Structure

- `<Composition>`: `id` of letters, digits and `-`; `defaultProps` required when the component takes props; a Zod
  `schema` for Studio controls (since 4.0.516 plain `defaultProps` also produce controls).
- `calculateMetadata({props, defaultProps, abortSignal, compositionId, isRendering})`: runs once per render before
  frames (fetch data, set `durationInFrames`, `width`, `height`, `fps`, default codec, pixel format and more).
  Returned values beat the Composition's; CLI flags beat both.
- `<Sequence>`: `from`, `durationInFrames`, `name`, `layout="none"` (no wrapper), `premountFor` (mount early for
  preview smoothness; renders are unaffected), `trimBefore` (4.0.482), `playbackRate` (4.0.528), `freeze`
  (4.0.476), `hidden` (4.0.462).
- `<Series>` of `<Series.Sequence durationInFrames offset>`; `<TransitionSeries>` (in `@remotion/transitions`) with
  `<TransitionSeries.Transition presentation timing>`: total = sum of sequences minus sum of transitions; each
  sequence must be at least as long as the transitions next to it.
- `<Loop durationInFrames times>`; `Loop.useLoop()` gives the iteration.
- `<Folder>` groups compositions in the Studio sidebar.
- `<Still>` registers a single-frame composition (thumbnails, posters).

## Async work

```tsx
const {delayRender, continueRender, cancelRender} = useDelayRender();
const [handle] = useState(() => delayRender('Loading data'));
useEffect(() => {
	fetch(staticFile('data.json'))
		.then((r) => r.json())
		.then((d) => {
			setData(d);
			continueRender(handle);
		})
		.catch((e) => cancelRender(e));
}, [continueRender, cancelRender, handle]);
```

Never call `delayRender` at module top level (it blocks every composition) or in the render body (a new handle every
render). Label handles; raise `timeoutInMilliseconds` only after fixing slow assets. For data that decides the
length, use `calculateMetadata` instead.

## Media and images

- `<Img>` for images (waits for load, retries twice, `effects` turn it into a canvas); `<CanvasImage>` for canvas
  images with `fit`; `<AnimatedImage>` for GIF, APNG, AVIF, WebP; `@remotion/gif` for GIFs with more control.
- Video and audio: `<Video>` and `<Audio>` from `@remotion/media` for new code (frame exact, fetch only what they
  need, loop, `trimBefore`/`trimAfter` in source frames at the composition fps, `volume` number or per-frame
  function, the `objectFit` **prop**). They fall back to `<OffthreadVideo>` for H.265 or AV1 and alpha in some
  setups. `<OffthreadVideo>` extracts exact frames with FFmpeg (downloads the whole file first; `transparent` prop
  for alpha). `Html5Video`/`Html5Audio` are the old tags.
- `@remotion/media-utils`: `useAudioData`, `useWindowedAudioData`, `visualizeAudio`, `getWaveformPortion`,
  `getImageDimensions`. For metadata use Mediabunny (the old parser is being retired).
- Fonts: `@remotion/google-fonts/<Family>` `loadFont(style, {weights, subsets})` (always name weights and subsets on
  4.x, or every file loads); `@remotion/fonts` `loadFont({family, url: staticFile(...), weight})` for brand files.
  Measure text (layout-utils) only after fonts load.

## Studio-editable code (when a person will fine-tune)

Values inline in JSX; animation as hardcoded `interpolate()` keyframe arrays; the separate `translate`, `scale`,
`rotate` and `opacity` style properties instead of `transform` strings or animated `top`/`left`; `Interactive.*`
elements (4.0.475) or `Interactive.withSchema()` components; `defaultProps` inline. The Studio then writes drags,
keyframes and easing back into the source.

## Rendering, in short

- CLI: `npx remotion render src/index.ts Main out.mp4 [flags]`, `npx remotion still ... --frame=N`,
  `npx remotion compositions`, `npx remotion studio`, `npx remotion benchmark`.
- `remotion.config.ts` applies to the CLI and Studio only; the Node APIs (`bundle`, `selectComposition`,
  `renderMedia`, `renderStill`) need every option passed explicitly, `inputProps` to both `selectComposition` and
  `renderMedia`.
- Codecs: h264 (CRF 18 default, 1 to 51), h265 (23), vp8 (9), vp9 (28), av1 (30), prores (profiles proxy to
  4444-xq), gif. Transparency: PNG frames with ProRes 4444 `yuva444p10le` or VP8/VP9 `yuva420p`. Odd sizes are
  rounded down by one pixel for h264, h265 and av1.
- `--color-space=bt709` tags and converts colour (the default writes no tags, players guess). `--gl=angle` for any
  WebGL. `--concurrency` defaults to half the threads, at most 8; measure with `benchmark`. `--frames=0,30,90`
  renders only those frames (4.0.502).
- Licence: free for individuals and companies of up to 3 people; above that a Company License (seats for people and
  agents making videos in Studio; per-render pricing for automation).

## Where to go deeper

| Area | File in `kb/` |
|---|---|
| interpolate, Easing, spring, compositions, props, Studio, delayRender, assets, config, codecs, CLI | `D1-core-a.md` |
| Sequence, Series, Loop, Freeze, media tags, audio, three, the timing model, licence | `D2-core-b.md` |
| Lambda, Cloud Run, Vercel | `D3-lambda-cloud.md` |
| Rendering APIs, Studio, Player, codemods, browser rendering | `D4-render-studio-player.md` |
| @remotion/effects (74), canvas, HtmlInCanvas, light leaks, starburst, motion blur, noise | `D5-effects-canvas.md` |
| Paths, shapes, transitions, fonts, layout-utils, rough-notation, Lottie, GSAP, emoji | `D6-graphics-text.md` |
| Video and audio tags, captions, sfx, Whisper, recorder | `D7-media-audio-captions.md` |
| Media parser, WebCodecs, Mediabunny, the editor starter, AI and MCP | `D8-parser-webcodecs-editor-ai.md` |
| remotion.dev site: Elements, prompts, templates, blog lessons | `S1-site.md` |
| The official skills and plugins, evals, MCP | `R1-skills-plugins.md` |
| The Remotion team's own videos and code | `R2-team-videos.md` |
| Templates and example repositories | `R3-templates-examples.md` |
| The community, motion craft, competing tools | `C1-community.md` |
