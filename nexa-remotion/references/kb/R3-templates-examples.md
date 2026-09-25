# R3: Official templates and org example repos

Agent: R3-templates-examples. Target runtime: Remotion 4.0.528 with React 19. Material: the 20 official templates in
`repo/packages/template-*` and 30 org example repos in `examples/` (all except `examples/skills` and
`examples/claude-code-plugin`). Versions were cross-checked against `mirror/docs` (`AvailableFrom` markers and
`5-0-migration.md`) and a few package sources. All paths below are relative to the R&D root.

Layout of this file: sections 1 to 9 follow the brief. Appendix A describes every template, Appendix B every example
repo (what it produces, how it is built, what to copy, reusable techniques), Appendix C is a technique index that
points from a goal to the file that shows it best.

## 1. Scope and coverage

- Read in full, file by file, and logged in `kb/R3-templates-examples.coverage.txt`: **1984 text files** (1984
  unique paths; the coverage list equals the scope list, verified with `comm`).
  - **Templates: 798 files** in 20 packages: recorder 238, prompt-to-motion-graphics 91, vibe-code 73, react-router 44,
    next-app-tailwind 43, vercel 42, electron 29, code-hike 27, audiogram 25, still 24, prompt-to-video 22,
    stargazer 20, render-server 20, music-visualization 18, tiktok 17, three 16, helloworld 16, skia 13, overlay 10,
    blank 10.
  - **Example repos: 1186 files** in 30 repos: github-unwrapped 360, template-prompt-to-motion-graphics-saas 91,
    trailer-2-0 82, 4-0-trailer 77, html-in-canvas 67, trailer 59, shorts-customizer 46, transitions-video 36,
    apple-wow-tutorial 28, gpu-scene 24, library-starter 23, gl-transitions 22, cloudflare-containers-demo 22,
    3d-text 20, text-warping 19, timing-functions 18, remotion-three-gltf-example 18, glb-example 18,
    animated-captions 17, tone-js-example 15, three-particles 14, motion-blur-example 14, morph-text 13,
    mapbox-example 13, typewriter 12, light-leak-example 12, d3-example 12, css-animation-play-state 12,
    video-with-jump-cuts 11, anime-example 11.
- Not read, by rule: 48 binaries in the templates (png, mp3, mp4, ico, wav, ttf, m4a, jpeg, woff2, jpg, gif); in
  the examples 544 binaries (images, audio, video, fonts), 29 lockfiles (24 `package-lock.json`, 4 `bun.lockb`,
  1 `pnpm-lock.yaml`), 2 generated source maps (shorts-customizer `sw.js.map`, `workbox-*.js.map`) and 942 files of
  `.git/` metadata (each example is a shallow clone).
- Read structurally (head, element counts and every logic line; the bulk is machine-generated vector or glyph data):
  3d-text `public/Bold.json` and `Rubik.json` (facetype typeface JSON, about 450 KB each); tone-js-example
  `EndCard.tsx` (79 KB Figma SVG with an embedded base64 PNG); mapbox-example `routes.ts` (412 + 204 coordinates);
  shorts-customizer `workbox-1ffba242.js` (93 KB, generated) and an Illustrator logo SVG; 4-0-trailer
  `ProductLineup.tsx` (111 KB of outlined text) and `public/zod.svg` (118 KB); github-unwrapped: 21 SVG-to-TSX
  artwork files (orbs, sky, the 228 KB Sponsorships background, the 354 KB Earth, home backgrounds, octocats, the
  Poof and Box sprite sheets, StarSprite frames, StandardPlanet) and its 28 `.svg` assets.
- Duplicates: the shared example boilerplate (182 files in 54 distinct variants: eslint, prettier, tsconfig,
  `remotion.config.ts`, GitHub workflow) was checked with md5 and read once per variant.
  `examples/template-prompt-to-motion-graphics-saas` is byte-identical to `repo/packages/template-prompt-to-motion-graphics`
  except for `package.json`. `examples/html-in-canvas/.agents/skills/remotion-best-practices` (SKILL.md, 34 rules,
  3 assets) was read in full; its copies under `.agent`, `.claude`, `.cline`, `.codex`, `.cursor`, `.gemini`, `.github`
  and `.opencode` are symlinks to it.
- Gaps: `repo/packages/core/src` is partial in our copy (easing, interpolate, spring only), so one question about
  `Sequence` (fractional `from`) stays open; `repo/packages/three/package.json` is missing (the docs were used).
- Licensing flags: `examples/animated-captions` is a paid remotion.pro component whose README forbids redistribution:
  this file records ideas only, no code. `examples/4-0-trailer` has no licence; its music, the GT Planar font and brand
  assets are reference only. github-unwrapped music is licensed from SmartSound (a derivative must re-license).
  Sample tokens and account ids that ship in some READMEs and configs are deliberately not reproduced.

Remotion versions pinned by the examples (their age explains renamed APIs such as `startFrom`):

| Remotion | Repos |
|---|---|
| ^3.0.0 | motion-blur-example, trailer, trailer-2-0 |
| 4.0.4 | apple-wow-tutorial |
| ^4.0.46 / 4.0.48 | library-starter / shorts-customizer |
| 4.0.60 | transitions-video |
| 4.0.118 | timing-functions, tone-js-example |
| 4.0.119 | 3d-text, glb-example, typewriter |
| 4.0.120 | morph-text, css-animation-play-state, text-warping, three-particles, remotion-three-gltf-example |
| 4.0.150 | gl-transitions, light-leak-example |
| 4.0.169 | 4-0-trailer |
| 4.0.177 | d3-example |
| 4.0.212 | video-with-jump-cuts |
| 4.0.240 | github-unwrapped (the 2025 edition: `YEAR_TO_REVIEW = 2025`, site `unwrapped2025`) |
| 4.0.248 | gpu-scene |
| 4.0.298 | anime-example |
| 4.0.321 | cloudflare-containers-demo |
| 4.0.390 | animated-captions |
| 4.0.409 | mapbox-example |
| 4.0.455 | html-in-canvas |
| ^4.0.0 | template-prompt-to-motion-graphics-saas |

Templates follow the monorepo (react 19.2.3, zod 4.5.4, TypeScript 5.9.3). Their `package.json` version fields:
vibe-code "4.0.529" (one release ahead of our 4.0.528), prompt-to-motion-graphics "4.0.379", recorder "4.0.277".

## 2. Mental model

The templates and examples are the closest thing Remotion has to a "house style guide". Read together they teach
the following model.

1. **Project shape.** `src/index.ts` calls `registerRoot(Root)`. `Root` registers `<Composition>` and `<Still>` items
   (grouped in `<Folder>`), each = component + `width/height/fps/durationInFrames` + `defaultProps` + optional zod
   `schema` + optional `calculateMetadata`. Big projects register every scene as its own composition with realistic
   and edge-case props (github-unwrapped registers `Issues0-0`, `Issues20-15`, `Issues500-500` and so on) so each
   scene can be developed and checked alone. `remotion.config.ts` only affects the CLI and Studio; Node APIs
   (`renderMedia`, `bundle`, Lambda) need the same options passed explicitly (every template says so in a comment).
2. **A frame is a pure function of `(frame, props)`.** Everything visual derives from `useCurrentFrame()` and
   props. Randomness comes from `random(seed)`; anything random that must be designed (pop animations, delays,
   scatter tables) is pre-computed once and frozen into data (prompt-to-video timeline, github-unwrapped position
   tables). Anything asynchronous (fonts, JSON, images, WebGL init, map tiles, DOM measurement) holds the frame with
   `delayRender`/`useDelayRender` and must release it on failure with `cancelRender`. Web-only motion (CSS
   transitions and keyframes, `requestAnimationFrame`, react-spring) never goes inside a composition.
3. **Data first, then layout, then motion.** The strongest templates do all data work in `calculateMetadata`:
   durations from media (mediabunny), captions, API data, even complete element layouts (recorder). The component
   then only renders. `calculateMetadata({props, defaultProps, abortSignal, isRendering, compositionId})` returns any
   of `{durationInFrames, fps, width, height, props, defaultCodec, ...}`. Studio edits re-run it, so debounce network
   calls with the `abortSignal` (stargazer) and read `props`, not `defaultProps`.
4. **Time structure.** `<Sequence>` resets local time (children see frame 0 at `from`); negative `from` starts
   media or animation part-way; `<Series>` chains scenes and a negative `offset` overlaps them;
   `<TransitionSeries>` overlaps neighbours by the transition length (total duration shrinks by it); captions are
   one Sequence per page; heavy media gets `premountFor`. Overlaps are computed in `calculateMetadata` so audio and
   music line up (recorder subtracts 15 frames per transition).
5. **Motion vocabulary.** `spring({config: {damping: 200}})` is the default no-bounce ease; bouncy accents use
   damping 8 to 15; heavy objects use mass 2 to 10. Stagger lists by 2 to 5 frames (captions 1 frame per letter, bars
   3 to 10). Exits use a delayed spring (`delay: duration - n`) or `reverse: true`; "enter minus exit" of two springs
   gives an in/out envelope. `interpolate` is always clamped. Zooms through objects use `scale = 1 / distance`. Speed
   ramps integrate a speed curve (`remapSpeed`). Loops use modulo arithmetic.
6. **Assets.** Everything used at render time belongs in `public/` and is referenced with `staticFile()`. Remote URLs
   (GLB on S3, HDR environments, avatars, fonts from a CDN) are the most common fragility in the examples.
7. **Three surfaces.** Studio (development; Studio-only APIs such as `writeStaticFile` turn a composition into an app),
   Player (web preview with its own constraints: mobile audio tag limits, prefetching, user-gesture play) and renderers
   (CLI, Node SSR, Lambda, Vercel Sandbox, Cloudflare Containers, Electron, the in-browser web renderer).
8. **GPU axis.** WebGL, Three, Skia, HtmlInCanvas and Mapbox need a GL backend: `--gl=angle` locally in v4 (default
   is `null`), `swangle` on Lambda/Cloud Run (no GPU), `angle-egl` on Linux GPU hosts. v5 makes `angle` the default
   with a `swangle` fallback. HtmlInCanvas needs Chrome 149+ with a flag only for preview; renders use Remotion's
   Chrome build.
9. **Generative pipelines separate generation from a deterministic renderer.** prompt-to-video: LLM story, image
   model, TTS with character timestamps, then a validated `timeline.json` that a generic composition plays.
   prompt-to-motion-graphics: LLM writes a component, the browser compiles it with Babel into an injected scope,
   the Player previews it, errors are fed back for up to 3 automatic fixes, follow-ups are exact string edits. Both
   constrain the model (JSON schema, import whitelist) and keep the renderer dumb.
10. **Studio as an editor.** zod schemas (`zColor()`, enums, discriminated unions, `.step(1)`) become a props form;
    `Interactive.*` elements plus codemods (vibe-code) write visual edits back to source; the recorder uses Studio
    APIs for drag-and-drop b-roll, caption editing and follow-the-playhead props.

## 3. API digest

Scope: the APIs that the templates and examples actually exercise, with the values they use. Versions are from the
docs mirror ("since" = first version with the feature). Deeper reference material lives in the D-series kb files;
this digest records how the official code uses each API and what goes wrong.

### 3.1 Core timing and motion (`remotion`)

- **`spring({frame, fps, config, from, to, delay, reverse, durationInFrames, durationRestThreshold})`**. Physics curve
  from `from` (0) to `to` (1). `durationInFrames`/`durationRestThreshold` since 3.0.27, `delay` since 3.3.90,
  `reverse` since 3.3.92. Config defaults: mass 1, damping 10, stiffness 100, overshootClamping false. Values used in
  the official code: `damping: 200` (no overshoot, the default look), `mass: 0.5` (quick pop), `damping: 100` (logo),
  `damping: 12..15` with `stiffness: 100..170` (bouncy accents, chat bubbles), `mass: 3..10` (heavy spins and slot
  wheels), `durationRestThreshold: 0.001..0.00001` when a stretched spring must not visibly "stop early".
  Gotchas: spring overshoots above 1 unless damped or clamped; `durationInFrames` stretches the curve to end at that
  frame; `delay` is cleaner than `frame - n`. The function is pure, so it also works outside compositions
  (github-unwrapped animates a website button with `spring({fps: 1000, frame: msElapsed, reverse: true})`).
  Example: `const out = spring({frame, fps, config: {damping: 200}, durationInFrames: 15, delay: dur - 15});`
- **`interpolate(input, inputRange, outputRange, {easing, extrapolateLeft, extrapolateRight})`**. Output ranges may be
  CSS strings since 4.0.472 (`["0px 60px", "0px 0px"]`, `["-12deg", "0deg"]`), per-segment easing since 4.0.462,
  single-value ranges since 4.0.469, numeric tuples 4.0.473, perceptual scale output 4.0.490, discrete strings
  4.0.509. Gotcha: without `clamp` values keep going (helloworld's subtitle opacity exceeds 1; harmless there, a bug
  elsewhere). Three-point ranges give "fast in, slow read, fast out" (`[0, 25, 250] -> [1500, 300, -3000]`).
- **`interpolateColors(value, inputRange, colors)`**. Colour lerp. Used for caption word states, planet tinting
  (mix a user colour toward white at graded stops) and blending a palette into a background.
- **`Easing`**. Values seen: `Easing.bezier(0.17, 0.67, 0.76, 0.91)` (code-hike token moves),
  `Easing.bezier(0.16, 1, 0.3, 1)` (html-in-canvas slide), `Easing.bezier(0.2, -0.02, 0.32, 1)` (github-unwrapped
  sweep), `Easing.out(Easing.quad | Easing.cubic)`, `Easing.out(Easing.back(1.2..1.5))`, `Easing.inOut(Easing.sin)`.
- **`random(seed)`**. Deterministic 0..1 from a string or number. `random(null)` is truly random: only acceptable for
  unique SVG ids (helloworld, StandardPlanet use `useState(() => random(null))`; `useId()` is the modern choice).
  Server code imports it from `remotion/no-react` (github-unwrapped picks per-user variations with
  `random(lowercasedUsername + key)`).
- **`<Sequence>`**. `from` (default 0, may be negative), `durationInFrames` (default Infinity), `name`,
  `layout="none"` (no AbsoluteFill wrapper), `style` (3.0.27), `width`/`height` (4.0.80), `showInTimeline`
  (4.0.110), `premountFor` (4.0.140), `styleWhilePremounted` (4.0.252), `postmountFor` (4.0.340), `hidden` (4.0.462),
  `freeze` (4.0.476), `trimBefore` (4.0.482), `controls` (4.0.501), `crop*` (4.0.500), `playbackRate` (4.0.528,
  must stay constant across frames). Gotchas: children see local time; audio inside a Sequence also restarts, so
  global audio analysis needs `frame + sequenceStart` (trailer-2-0); hundreds of tiny Sequences clutter the Studio
  timeline, hide them with `showInTimeline={false}` (github-unwrapped Issues). v5 premounts every Sequence for 1 s
  automatically.
- **`<Series>` / `<Series.Sequence durationInFrames offset layout>`**. Negative `offset` overlaps the previous scene.
  Since 4.0.443 Series is a Sequence and accepts its props; `premountFor` on Series.Sequence since 4.0.140. Only the
  last item may be `Infinity`.
- **`<Freeze frame>`** (2.2.0). Pins the subtree to a frame. Used for OG stills from an animation frame, frame-sampled
  motion-blur trails and speed ramps (`<Freeze frame={remapSpeed(frame, fn)}>`). `Sequence freeze` (4.0.476) is the
  prop form.
- **`<Folder name>`** (3.0.1), **`<Still>`**, **`<Composition>`**, **`calculateMetadata`** (4.0.0): see mental model
  item 3. Metadata may also set `defaultCodec`, `defaultPixelFormat`, `defaultProResProfile` (vendored skill uses
  this for transparent output).
- **`<AbsoluteFill>`**. Accepts Sequence props since 4.0.501 (`<AbsoluteFill durationInFrames={30}>` is a timed layer
  in prompt-to-video), premount props since 4.0.528.

### 3.2 Async safety and environment

- **`delayRender(label?)` / `continueRender(handle)`** (2.6.13), **`cancelRender(error)`** (3.3.44),
  **`useDelayRender()`** (4.0.342, returns scoped `{delayRender, continueRender, cancelRender}`). Pattern used by the
  better templates: `const [handle] = useState(() => delayRender("Loading captions"))`, fetch, `continueRender`,
  `cancelRender(err)` in `catch`. Labels show up in timeout errors. `Config.setDelayRenderTimeoutInMilliseconds()`
  (2.6.3; stargazer sets 1200000 to survive GitHub rate-limit waits).
- **`staticFile(path)`**, **`getStaticFiles()`** (moved to `@remotion/studio`, since 4.0.144; prefer it over the old
  `remotion` export). Templates list `public/` to discover inputs: code-hike reads every `code*` file, recorder groups
  `webcam<ts>`/`display<ts>`/`subs<ts>` files, prompt-to-video registers one composition per `timeline.json`.
- **`getRemotionEnvironment()`** (4.0.25) and **`useRemotionEnvironment()`** (4.0.342): `{isStudio, isRendering,
  isPlayer, isReadOnlyStudio}`. Uses: show a PNG instead of a slow CSS gradient while rendering (github-unwrapped),
  hide on-canvas SRT previews and editor overlays while rendering (recorder), skip network debounce when rendering
  (stargazer `isRendering` from calculateMetadata).
- **`prefetch(src)`** (3.2.35): `.waitUntilDone()` promise; github-unwrapped prefetches every asset of a user's video
  and enables the Play button only at 100 %.
- **`getInputProps()`** (2.0): prompt-to-motion-graphics reads the generated code this way inside the component.
- **`useCurrentScale()`** (4.0.125): convert `getBoundingClientRect()` sizes back to composition pixels (recorder end
  card measures its content inside a delayRender).
- **`<Artifact content filename>`** (4.0.176): emits a file next to the render; recorder renders it at frame 0 to
  produce `captions.srt`.
- **`Interactive`** (4.0.475; `baseSchema`/`transformSchema` 4.0.479): `Interactive.Div/H1/P name="..."` makes elements
  selectable and editable in Studio; `Config.setInteractivityEnabled(false)` (4.0.487) and
  `Config.setAskAIEnabled(false)` (4.0.407) switch these Studio features off (recorder does both).
- **`<HtmlInCanvas width height onInit onPaint>`** (4.0.455): captures its DOM children as an `elementImage` for 2D
  (`ctx.drawElementImage`) or WebGL2 (`gl.texElementImage2D`). `onInit({canvas, element, elementImage})` runs once
  and returns a cleanup (or a Promise of one); `onPaint(...)` runs when children change. Extra props: `pixelDensity`
  (4.0.472), `effects` (4.0.464), `cropLeft/Right/Top/Bottom` (4.0.500), Sequence timing props (`trimBefore` 4.0.482,
  `playbackRate`, premount/postmount 4.0.528). `HtmlInCanvas.isSupported()`. Cannot be nested.

### 3.3 Media (`@remotion/media`, core video, mediabunny)

- **`<Video>` / `<Audio>` from `@remotion/media`**: `src`, `trimBefore`/`trimAfter` (in frames), `volume` (number or
  `(f) => number`), `loop` + `loopVolumeCurveBehavior="extend"` (4.0.354), `playbackRate` (4.0.354), `objectFit`
  (4.0.442), `from`/`durationInFrames` (4.0.445), `premountFor`/`postmountFor` (4.0.495), `effects` (4.0.464),
  `crop*` (4.0.500), `headless` + `onVideoFrame` (4.0.387; draws frames into your own canvas, e.g. a three.js
  texture), `onError` (4.0.404). They pause the Player while loading.
- **`<OffthreadVideo>`**: `trimBefore`/`trimAfter` since 4.0.319 (renamed from `startFrom`/`endAt`, which still work
  but cannot be mixed with the new names), `transparent` for alpha video, `pauseWhenBuffering`, `playbackRate`,
  `muted`. The core `<Video>`/`<Audio>` of older examples are now `Html5Video`/`Html5Audio`.
- **mediabunny** (templates prefer it for metadata): `new Input({formats: ALL_FORMATS, source: new UrlSource(url)})`,
  `computeDuration()`, `getPrimaryVideoTrack()` with `displayWidth/displayHeight`, `computePacketStats(50).averagePacketRate`
  (fps estimate), always `input.dispose()`. In the browser `Conversion.init({input, output, video})` converts
  recordings (recorder). `getVideoMetadata()` from `@remotion/media-utils` is deprecated (fails on H.265 on Linux),
  and v5 removes the `@remotion/renderer` one.

### 3.4 Transitions (`@remotion/transitions`, TransitionSeries since 4.0.59)

- `<TransitionSeries>` with `.Sequence durationInFrames` and `.Transition presentation timing`; `.Overlay` (4.0.415)
  for effects that sit across a cut without shortening it.
- Timings: `linearTiming({durationInFrames, easing})`, `springTiming({config: {damping: 200}, durationInFrames})`;
  both expose `getDurationInFrames({fps})`, which github-unwrapped uses to compute the total length in
  calculateMetadata.
- Presentations: `fade()`, `slide({direction: "from-left" | "from-right" | "from-top" | "from-bottom"})`,
  `wipe({direction})` (8 directions), `flip({direction, perspective})` (4.0.54), `clockWipe({width, height})`
  (4.0.74), `none()` (4.0.177), `iris({width, height})` (4.0.316); shader presentations on HtmlInCanvas: `zoomBlur`
  (4.0.456), `zoomInOut` (4.0.457), `dissolve`/`ripple` (4.0.465), `crosswarp`/`dreamyZoom`/`linearBlur`/`swap`/
  `bookFlip` (4.0.466), `crossZoom`/`filmBurn` (4.0.467), `pushCut` (4.0.500), `blurSlide` (4.0.523);
  `makeHtmlInCanvasPresentation()` (4.0.456) wraps a custom WebGL2 shader; `cube()` is a paid remotion.pro item.
  `useTransitionProgress()` (4.0.177); enter/exit style options (4.0.84); `shouldFadeOutExitingScene` (4.0.166).
- Custom presentation contract: a factory returns `{component, props}`; the component receives `{children,
  presentationDirection: "entering" | "exiting", presentationProgress, passedProps}` and styles its children.
  Wrapping a presentation so the entering side also renders `<Audio src>` locks a whoosh to the cut (`addSound`
  in transitions-video). v5 removes `layout="none"` on TransitionSeries.

### 3.5 Captions and transcription

- **`Caption`** (`@remotion/captions`, 4.0.216): `{text, startMs, endMs, timestampMs, confidence,
  pageBreakAfter? (4.0.517)}`. Whisper tokens are sub-words; a leading space marks a new word.
- **`createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds, breakOnSilenceAfterMilliseconds?})`**
  (4.0.216; silence breaks 4.0.514) returns `{pages}`; a page has `text`, `startMs`, `durationMs` (4.0.261) and
  `tokens[{text, fromMs, toMs, pageBreakAfter}]`. Values used: 1200 ms (tiktok, several words), 800 ms
  (animated-captions), 200 ms or less gives single words.
- **`parseSrt({input})`** -> `{captions}` (4.0.216), `serializeSrt`, `ensureMaxCharactersPerLine` (4.0.216).
- **`@remotion/install-whisper-cpp`**: `installWhisperCpp({to, version})` (tiktok 1.6.0, audiogram 1.7.4, recorder
  1.7.2; Windows 1.6.0), `downloadWhisperModel({model, folder, onProgress})`, `transcribe({inputPath, whisperPath,
  whisperCppVersion, model, tokenLevelTimestamps: true, language, splitOnWord, translateToEnglish: false,
  printOutput, onProgress, signal})` (4.0.131), `toCaptions({whisperCppOutput})` -> `{captions}` (4.0.216). Input
  must be 16 kHz WAV: `npx remotion ffmpeg -i in.mp4 -ar 16000 out.wav -y` (add `-ac 1`, and `-ss` to skip intro
  music). Models: `medium.en` in tiktok/recorder (1.5 GB, about 2.6 GB RAM); non-English needs a model without
  `.en`; `large-v3-turbo` needs whisper.cpp 1.7.2 or later.

### 3.6 Text layout (`@remotion/layout-utils`)

- **`measureText({text, fontFamily, fontSize, fontWeight, letterSpacing, validateFontIsLoaded})`** (4.0.57) ->
  `{width, height}`; code-hike measures "A" to get the monospace advance.
- **`fitText({text, withinWidth, fontFamily, fontWeight, textTransform})`** (4.0.88) -> `{fontSize}`; templates cap it
  (`Math.min(120, fitted)` in tiktok, 80 in animated-captions).
- **`fillTextBox({maxBoxWidth, maxLines})`** (4.0.57) -> `{add({text, fontFamily, fontSize, ...}) => {exceedsBox,
  newLine}}`; audiogram and recorder use it to paginate captions. `fitTextOnNLines` since 4.0.313.
- Gotcha: measure only after the font is loaded (`validateFontIsLoaded: true`; default becomes true in v5).

### 3.7 Audio analysis (`@remotion/media-utils`)

- **`useWindowedAudioData({src, frame, fps, windowInSeconds})`** (4.0.240; WAV only before 4.0.383, every mediabunny format since) ->
  `{audioData, dataOffsetInSeconds}`; loads only a window with HTTP range requests (audiogram 10 s, music-visualization
  30 s). **`useAudioData(src)`** loads the whole file (options since 4.0.458).
- **`visualizeAudio({fps, frame, audioData, numberOfSamples, optimizeFor, dataOffsetInSeconds})`**
  (`optimizeFor` 4.0.83, `dataOffsetInSeconds` 4.0.268) -> array of frequency magnitudes (power-of-two sample
  counts). v5 makes `optimizeFor: "speed"` the default.
- **`visualizeAudioWaveform({fps, frame, audioData, numberOfSamples, windowInSeconds, channel, dataOffsetInSeconds})`**
  (4.0.268) -> amplitudes in [-1, 1]; **`createSmoothSvgPath({points})`** turns points into a smooth path.
- **`getWaveformPortion({audioData, startTimeInSeconds, durationInSeconds, numberOfSamples, normalize})`**
  (`normalize` default restored in 4.0.280); **`audioBufferToDataUrl(buffer)`** (2.5.7) makes a WAV data URL from a
  generated AudioBuffer.

### 3.8 Vector helpers (`@remotion/paths`, `@remotion/shapes`, `@remotion/noise`, `@remotion/animation-utils`)

- `evolvePath(progress, d)` -> `{strokeDasharray, strokeDashoffset}` (draw-on). `getLength(d)`,
  `getPointAtLength(d, len)`, `getTangentAtLength(d, len)`: in v5 both return `null` beyond the end (v4 returned
  the end point), so clamp `len` (github-unwrapped samples the tangent at `len + 0.0001`). `warpPath(d, fn,
  {interpolationThreshold})` (3.3.43), `resetPath` (3.3.40), `scalePath` (3.3.43), `translatePath`, `reversePath`,
  `getBoundingBox` -> `{x1, y1, x2, y2, width, height, viewBox}` (3.3.40, size fields 3.3.97), `parsePath`,
  `reduceInstructions`/`serializeInstructions` (3.3.40; edit bezier control points then re-serialise).
  `interpolatePaths` is 4.0.529 (not on 4.0.528).
- `@remotion/shapes`: `makeRect({width, height, cornerRadius})`, `makeCircle({radius})`, `makePie({radius, progress,
  closePath, rotation})`, `makeTriangle({length, direction, edgeRoundness})` (0.71 gives the rounded Remotion
  triangle), each returning `{path, width, height, instructions, transformOrigin}`; components `<Rect>`, `<Circle>`,
  `<Pie progress closePath={false}>`, `<Star>`, `<Triangle>`, `<Ellipse>`, `<Heart>`, `<Polygon>`.
- `noise2D(seed, x, y)` (package since 3.2.32) -> -1..1, deterministic per seed string; used for shake, wander,
  flicker, glitch bands and starfields.
- `makeTransform([scale(0.8), translateY(50)])` and `interpolateStyles(value, inputRange, styles)`
  (`@remotion/animation-utils`, 4.0.92).

### 3.9 3D and GPU

- **`<ThreeCanvas width height ...R3F props>`** (`@remotion/three`): `width`/`height` are required; passes `linear`,
  `orthographic`, `camera`, `shadows`, `dpr` to R3F. While rendering it sets `frameloop="never"` and calls
  `advance()` once per Remotion frame behind its own delayRender; its Suspense fallback holds a delayRender, so
  `useGLTF` and other suspending loaders are render-safe. Inherits Sequence props since 4.0.528.
  `useVideoTexture`/`useOffthreadVideoTexture` are deprecated in favour of `<Video headless onVideoFrame>`.
  **`<ThreeWebGPUCanvas>`** from `@remotion/three/webgpu` since 4.0.503 (experimental; three >= 0.167, R3F 9).
- **Skia**: entry must `await LoadSkia()` (from `@shopify/react-native-skia/src/web`) before importing the Root;
  bundler override `enableSkia` from `@remotion/skia/enable` (pass as `webpackOverride` to `bundle()`/`deploySite()`
  too); draw inside `<SkiaCanvas width height>`.
- **Config GL**: `Config.setChromiumOpenGlRenderer("angle")` (three, skia, 3d-text, gl-transitions, mapbox),
  `"angle-egl"` (Linux GPU, 4.0.52), `"swangle"` (Lambda default, no GPU), `"vulkan"` (4.0.41). v4 default is `null`.

### 3.10 Studio APIs (`@remotion/studio`, Studio only)

`watchStaticFile(name, cb)` (4.0.144, returns `{cancel}`), `writeStaticFile({filePath, contents})` (4.0.147),
`saveDefaultProps` (4.0.147), `deleteStaticFile` (4.0.154), `updateDefaultProps({compositionId, defaultProps: ({unsavedDefaultProps}) => next})`
(4.0.154), `watchPublicFolder(cb)` (4.0.154), `focusDefaultPropsPath({path, scrollBehavior})` (4.0.165),
`reevaluateComposition()` (4.0.167, re-runs calculateMetadata). Guard every use with `isStudio && !isReadOnlyStudio`.

### 3.11 Rendering and deployment

- **`@remotion/bundler` `bundle({entryPoint, onProgress, webpackOverride})`** once per process (v5 removes the
  positional signature). **`@remotion/renderer`**: `selectComposition({serveUrl, id, inputProps})` (v5 requires
  `inputProps`), `renderMedia({composition, serveUrl, codec, outputLocation, inputProps, onProgress, cancelSignal,
  chromiumOptions: {enableMultiProcessOnLinux}, binariesDirectory, browserExecutable})`, `renderStill({composition,
  serveUrl, output, inputProps, imageFormat, scale})`, `ensureBrowser()` (4.0.137), `makeCancelSignal()` (3.0.15)
  -> `{cancel, cancelSignal}`.
- **`@remotion/lambda`**: `deployFunction({memorySizeInMb, timeoutInSeconds, diskSizeInMb, region,
  createCloudWatchLogGroup, enableV5Runtime})`, `getOrCreateBucket({region, enableFolderExpiry})`, `deploySite({bucketName,
  entryPoint, siteName, region, options: {webpackOverride}})`, `getRegions()`, `speculateFunctionName({diskSizeInMb,
  memorySizeInMb, timeoutInSeconds})` (3.3.75); from `@remotion/lambda/client`: `renderMediaOnLambda({functionName,
  region, serveUrl, composition, inputProps, codec, framesPerLambda, downloadBehavior: {type: "download", fileName},
  deleteAfter, metadata})`, `renderStillOnLambda({imageFormat, jpegQuality, privacy})`, `getRenderProgress({renderId,
  bucketName, functionName, region})` -> `{overallProgress, done, outputFile, outputSizeInBytes,
  fatalErrorEncountered, errors, costs}`. Values used: RAM 3009 MB, disk 10240 MB, timeout 240 s, framesPerLambda 10
  or 60 (templates); RAM 1200 MB and timeout 120 s (github-unwrapped). v5 defaults: disk 10240, `overwrite: true`,
  x264 preset `veryfast`.
- **`@remotion/vercel`** (4.0.426): `createSandbox({onProgress})`, `addBundleToSandbox({sandbox, bundleDir})`,
  `renderMediaOnVercel({sandbox, compositionId, inputProps, onProgress})`, `uploadToVercelBlob({sandbox,
  sandboxFilePath, contentType, blobToken, access})`, then `sandbox.stop()`.
- **`@remotion/web-renderer`** (4.0.397): `renderStillOnWeb({composition, frame, scale, inputProps})` ->
  `.blob({format})`, `renderMediaOnWeb({composition, inputProps, container, videoCodec, videoBitrate, frameRange,
  signal, onProgress})` -> `{getBlob}`, `canRenderMediaOnWeb(...)` -> `{canRender, issues}`.
- **`<Player>`** (`@remotion/player`): props used `component`, `inputProps`, `durationInFrames`, `fps`,
  `compositionWidth/Height`, `controls`, `autoPlay`, `loop`, `clickToPlay`, `spaceKeyToPlayOrPause`,
  `errorFallback`, `initiallyMuted`, `numberOfSharedAudioTags` (2.3.1; default 5 in v4, 0 in v5); ref methods
  `play(event)`, `pause()`, events `play`, `pause`, `error`, `frameupdate`. Size it with inline style (Tailwind
  classes lose to the Player's own styles).
- **Config**: `setRspack(true)`, `setVideoImageFormat("jpeg" | "png")`, `setOverwriteOutput(true)`,
  `setPixelFormat("yuva444p10le")` + `setCodec("prores")` + `setProResProfile("4444")` (alpha), `setMuted`,
  `setConcurrency(2)` (skia), `setChromeMode("chrome-for-testing")` (4.0.248), `overrideBundlerConfig(fn)` /
  `overrideRspackConfig(fn)`, `setEntryPoint(path)`.
- **Experimental, 4.0.527 and later**: `@remotion/browser-bundler`, `@remotion/canvas`, `@remotion/codemods` (vibe-code;
  several calls need 4.0.529). `HtmlInCanvasMotionBlur` is 4.0.529. `@remotion/light-leaks` (4.0.415) is deprecated in
  favour of `lightLeak()` from `@remotion/effects/light-leak` (4.0.500), and v5 stops publishing it.

## 4. Recipes

Each recipe names the source that shows it best. Snippets are paraphrased, not copied.

### 4.1 Derive duration, size and props from media and data (every data-driven template)
Do media and data work in `calculateMetadata`, put the results into `props`, and let the component throw if they are
missing (three, audiogram and prompt-to-video set `null` placeholders in `defaultProps`).
```tsx
export const calculateMetadata: CalculateMetadataFunction<Props> = async ({props, abortSignal}) => {
  const input = new Input({formats: ALL_FORMATS, source: new UrlSource(props.src)});
  try {
    const seconds = await input.computeDuration();
    const captions = await fetch(props.captionsUrl, {signal: abortSignal}).then((r) => r.json());
    return {fps: 30, durationInFrames: Math.ceil(seconds * 30), props: {...props, captions}};
  } finally {
    input.dispose();
  }
};
```
Variants: subtract an intro offset (music-visualization plays from `audioOffsetInSeconds` via
`<Sequence from={-offsetFrames}>`); width from content (code-hike: longest line x monospace advance, rounded up to an
even number because H.264 needs even dimensions, minimum 1080); dimensions from a layout enum (github-unwrapped
promo: `short` 1080x1920, `landscape` 1200x630); duration = sum of scene lengths minus overlaps (github-unwrapped,
recorder); debounce Studio edits with `abortSignal` before calling an API (stargazer waits 500 ms of no input).

### 4.2 Word-highlight captions, TikTok style (template-tiktok, animated-captions ideas)
1. Transcribe: extract 16 kHz WAV (`npx remotion ffmpeg -i in.mp4 -ar 16000 out.wav -y`), `installWhisperCpp` +
   `downloadWhisperModel` once, `transcribe({tokenLevelTimestamps: true, splitOnWord: true, language: "en"})`,
   `toCaptions()`, write `public/<name>.json`.
2. Load the JSON in the component under `useDelayRender()` (`cancelRender` on failure); in Studio re-load on change
   with `watchStaticFile`.
3. Page it: `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 1200})`; each page is a Sequence
   that lasts until the next page starts (no flicker between pages).
```tsx
return pages.map((page, i) => {
  const from = Math.round((page.startMs / 1000) * fps);
  const nextMs = pages[i + 1]?.startMs ?? page.startMs + page.durationMs;
  const to = Math.round((nextMs / 1000) * fps);
  return (
    <Sequence key={page.startMs} from={from} durationInFrames={Math.max(1, to - from)} layout="none">
      <CaptionPage page={page} />
    </Sequence>
  );
});
```
4. Style: `fitText({text: page.text, withinWidth: width * 0.9, fontFamily, textTransform: "uppercase"})` capped at
   120 px; white uppercase with `WebkitTextStroke: "20px black"` + `paintOrder: "stroke"` (or stroke width
   `fontSize / 7` with `paintOrder: "stroke fill"`); tokens are `whiteSpace: "pre"` spans because the space belongs
   to the token; active token when `page.startMs + frame / fps * 1000` lies in `[fromMs, toMs)`, coloured `#39E508`
   (tiktok) or `#18ff0e` (animated-captions).
5. Page entrance: `spring({frame, fps, config: {damping: 200}, durationInFrames: 5})` into
   `makeTransform([scale(0.8 -> 1), translateY(50 -> 0)])`. Place the block about 350 px above the bottom on
   1080x1920.
6. Variants (ideas from the paid animated-captions, re-implement yourself): scale the active word up 20 % with a
   4-frame spring inside a fixed-height flex row so the line does not jump, add `perspective(100px)` +
   `willChange: transform` against subpixel jitter; a coloured pill that glides between words (see 4.4).

### 4.3 Transcript-style paginated captions (template-audiogram, template-recorder)
- Convert all times with one helper (`msToFrame = Math.floor(ms / 1000 * fps)`).
- Lay words into lines with `fillTextBox({maxBoxWidth, maxLines})`: `box.add({text, fontFamily, fontSize})` returns
  `{newLine, exceedsBox}`; trim leading spaces at line starts; `pageBreakAfter` (4.0.517) forces a new page.
- Show only lines whose first word has started, from the last page break, last 5 lines (audiogram) = a scrolling
  transcript. Word entrance: opacity 0 to 1 over 15 frames, `translate: 0 0.25em -> 0` over 10 frames with
  `Easing.out(Easing.quad)`, `display: inline-block; white-space: pre`. Base 48, font 72, weight 600, line height 96.
- Recorder's box karaoke: grey words (30 % alpha) turn to full colour with `interpolateColors(timeMs, [startMs - 100,
  startMs], [grey, full])`; pages start 1 s early and end 1 s late at scene edges; 5-frame page fades; font 56, line
  height 1.2, border 3, `boxDecorationBreak: "clone"`; when a page overflows, cut 5 words early if more than 90 %
  fit, prefer cuts after "," or "." within 3 words, never after a code word, then recurse.
- Post-process whisper output first: drop `TT_` tokens and bracketed fillers (`[BLANK_AUDIO]`, `[PAUSE]`, `[INAUDIBLE]`),
  merge sub-word tokens that do not start with a space, apply a find/replace autocorrect list (brand names).

### 4.4 A highlight pill that glides between words (idea from animated-captions)
Measure each token with `measureText({validateFontIsLoaded: true})` (with and without its leading space). Build a
fractional word index as the sum over words of a short spring (about 5 frames, damping 100) that starts 2.5 frames
before each word. Interpolate the pill's left offset and width over the integer indices with that fractional value,
so the pill slides and resizes smoothly; pop it in with a spring mapped 0.6 to 1 on CSS `scale`; padding 12 px,
radius 10. The same fractional-index idea works for tab underlines and list selectors.

### 4.5 Audiogram: oscilloscope or spectrum (template-audiogram)
```tsx
const {audioData, dataOffsetInSeconds} = useWindowedAudioData({src, frame, fps, windowInSeconds: 10});
if (!audioData) return null;
const f = Math.round(frame / 3) * 3; // update every 3 frames for a stepped look
const ys = visualizeAudioWaveform({fps, frame: f, audioData, numberOfSamples: 64,
  windowInSeconds: 0.1, channel: 0, dataOffsetInSeconds});
const points = ys.map((y, i) => ({x: (i / (ys.length - 1)) * width, y: h / 2 + y * (h / 2) * 4}));
return <path d={createSmoothSvgPath({points})} stroke={color} strokeWidth={10} strokeLinecap="round" fill="none" />;
```
Spectrum: `visualizeAudio({..., numberOfSamples: n * 4, optimizeFor: "speed"})`, keep the low bins from a start index,
optionally mirror (`[...bins.slice(1).reverse(), ...bins]`), bar height `300 * Math.sqrt(v)` (square root lifts quiet
bins). Pass a WAV for long audio so only a window is fetched. Layout: 1080x1080 black, cover 250 px high radius 6,
IBM Plex Sans 500/600 behind a font gate.

### 4.6 Balanced music spectrum and beat flash (template-music-visualization)
Raw FFT is bass-heavy. Keep the lower half of the bins, pick bar i at log index `round(maxIndex ** (i / bars))`,
multiply by a gain that rises with frequency (`(0.3 + (i/n) ** (3 + 3i/n) * 3.5) * max(0.8, 1 - 0.3i/n)`), compress
with a power of about 0.8 to 0.6, normalise by the max, apply `** 0.9`. Bars: flex items, height `min(100, 80 * v)%`,
radius 8. Waveform mode: samples = 2048 per second of window, clamped to 2048..8192. Bass flash: average of the
first 32 of 128 bins times 3, full-frame colour layer with `opacity = min(0.5, avg * 0.8)`. Other scalings seen:
decibels `20 * log10(v)` mapped from -100..0 (4-0-trailer), or -100..-30 (vendored skill).

### 4.7 Meters, fake editors and waveform timelines (trailer-2-0, 4-0-trailer)
- LED meter: `visualizeAudio({numberOfSamples: 8, frame: frame + sequenceStart})` (add the Sequence start so the
  analysis stays on the global clock), 20 segments per column, segment j lit when `(20 - j) / 50 - 0.05 < volume`.
- Waveform bars for a timeline mock: `getWaveformPortion({audioData, startTimeInSeconds, durationInSeconds,
  numberOfSamples: 200})`; bars near a moving playhead grow with `visualizeAudio({numberOfSamples: 1})`.
- Volume envelopes drawn on a 2D canvas that morph by interpolating two functions with a spring.

### 4.8 Code walkthrough with token-level moves (template-code-hike)
Files `public/code1.tsx`, `code2.tsx`, ... become steps. `calculateMetadata` reads them with `getStaticFiles()`, runs
twoslash for type callouts (`// ^?`) and expected errors (`// @errors: 2339`), highlights with a lighter theme, and
returns `{steps, themeColors, codeWidth}`; each step lasts 90 frames. A `<Series>` renders one transition per step:
render the old code, snapshot token positions (`getStartingSnapshot`), render the new code, compute token moves in a
`useLayoutEffect` (`calculateTransitions`), then on each frame set every token's translate, colour and opacity from
`interpolate(frame, [delay * 30, (delay + duration) * 30], [0, 1], clamp)` eased with
`Easing.bezier(0.17, 0.67, 0.76, 0.91)`. Tokens must be `inline-block`. Callout bubbles and error messages fade in at
frames 25..35. Font 40 px, tab size 3, padding 60/84, line height 1.5. A story-style progress bar on top shows the
step. In Studio, `watchPublicFolder` + `reevaluateComposition()` reload when code files change.

### 4.9 Growing code lines and typed terminals (trailer, 4-0-trailer, html-in-canvas Crt)
- Line reveal: for lines listed in a timing array, drive opacity, line-height (0 to 1.53) and font-size (0 to 1em)
  with one spring (stiffness 200, damping 100, mass 0.5, overshootClamping) so lines grow in and push the code apart.
- Terminal: type the command with `slice(0, frame * speed)`, draw an ASCII progress bar, script outputs at fixed
  frames in a timing table, blink a block cursor every 15 frames, and compute the total duration from the last line
  plus a 60-frame hold.

### 4.10 Typewriter, caret, word carousel, highlighter (prompt-to-motion-graphics skills, typewriter)
```tsx
const chars = Math.min(text.length, Math.floor(frame / CHAR_FRAMES)); // CHAR_FRAMES = 3
const typing = chars < text.length;
const caret = typing ? 1 : interpolate(frame % 16, [0, 8, 16], [1, 0, 1]);
return (<span>{text.slice(0, chars)}<span style={{opacity: caret}}>{"▌"}</span></span>);
```
Rules: slice the string, never fade characters individually (breaks caret position); keep the caret solid while
typing and blink it after; a word carousel keeps width stable by rendering the longest word with
`visibility: hidden` and overlaying the current word absolutely (hold 32 frames, flip 18 frames, blur 6 px
crossfade); a highlighter is a bar behind the word that grows with a spring on `scaleX` from the left (0.12 em
bleed, 0.2 em radius), drawn in a separate layer that crossfades in after typing ends. The bare-bones example uses a
hard blink `Math.floor(frame / 10) % 2`.

### 4.11 Liquid text morph (morph-text)
Stack two words. Outgoing: `filter: blur(min(8 / (1 - f) - 8, 100)px)`, opacity `(1 - f) ** 0.4`; incoming:
`blur(min(8 / f - 8, 100)px)`, opacity `f ** 0.4`. Wrap both in a container with `filter: url(#threshold)
blur(0.6px)` where the SVG filter is an `feColorMatrix` whose alpha row is `0 0 0 255 -140`: the alpha threshold turns
blurred edges into gooey, fused shapes. Re-simulate the word timeline from frame 0 (morph 1 s, cooldown 0.25 s) so any
frame renders alone.

### 4.12 Warped text (text-warping)
Load a TTF with opentype.js under delayRender, `font.getPath(text, 0, 150, 72).toPathData(2)`, `resetPath`, optionally
`scalePath(d, 1, 5)`, then `warpPath(d, ({x, y}) => ({x: x + Math.sin(y / 4 + frame / 20) * 3, y}),
{interpolationThreshold: 1})` (lower threshold = finer subdivision). Size the SVG with `getBoundingBox(d).viewBox`.
Recipes: travelling bulge `x + 100 * normalPdf((y - start) / len)` with `start` sweeping -0.2h..1.2h; glitch bands
shifted by `noise2D("band" + i, frame / 100, 0) * 10`; hard offset shadow with `translatePath(d, 4, 4)`. Load the
font once, not in an effect keyed on `frame`.

### 4.13 Variable-font punches (transitions-video, github-unwrapped)
Register the font with `new FontFace("Mona Sans", "url(...) format('woff2 supports variations'),
url(...) format('woff2-variations')", {weight: "200 900", stretch: "75% 125%"})` under delayRender, then animate
`fontVariationSettings: '"wght" 600 -> 900, "wdth" 100 -> 125'` with a 20-frame spring. Pair with 20 to 25 frame
shots, `springTiming({config: {damping: 200}, durationInFrames: 10})` transitions and flat saturated colour fields.

### 4.14 Graphic 3D text and extruded SVG worlds (3d-text, 4-0-trailer)
- Three.js "long shadow" type: per character two `TextGeometry` meshes from a typeface JSON (`new FontLoader().parse(json)`):
  a deep extrusion (`height: 60`, flat `meshBasicMaterial` in the accent colour) and a flat face (`height: 0`, white)
  just in front (z + 0.01). Use `<ThreeCanvas linear orthographic camera={{zoom: 90, near: -40}}>`, lay characters
  out from `geometry.computeBoundingBox()` widths with 0.1 spacing, rotate the scene `[-PI/10, PI/10, 0.1]`, and
  spring each word forward in z (damping 15, 5 frames apart). No lights needed.
- SVG pseudo-3D (no WebGL): turn 2D path points into 3D points, apply 4x4 matrices (rotate, translate, scale around the
  element centre), extrude = front face + back face + one side quad per segment (subdivide curves 3 times at t = 0.5
  so sides follow the curve), sort faces by centre z, draw each face as an SVG path; orthographic only, no lighting.
  The monorepo now carries this as `@remotion/svg-3d-engine` (undocumented, treat as unstable). Scene ideas: logo
  triangles fanning out in depth, a 3D timeline with depth-flying tracks, a "Render" button pressed by a 3D cursor,
  a 9x9 grid rippling out by distance from centre (spring delay = distance / 20), extruded circles whose depth follows
  the spectrum in dB, and flying through the front face of an extruded "4" by using its serialised path as
  `clipPath: path(...)` on an HTML layer while `scale = 1 / distance`.

### 4.15 Product turntable from a GLB (glb-example)
`<ThreeCanvas shadows dpr={[1, 2]} camera={{fov: 70}}>` then a Stage that centres the model with a Box3 but uses a
**fixed radius** (8) so the framing does not drift while it spins: camera at `(0, r * 0.5, r * 2.5)` looking at
`(0, r / 2.5, 0)`, a spot key light (penumbra 1, castShadow), point fill, ambient at a third, `<ContactShadows blur={2}
opacity={0.5}>` and `<Environment preset="city">`. Rotate the mesh `interpolate(frame, [0, 90], [0, 2 * PI])`.
Bundle the GLB and HDR locally; drei's `Environment` preset downloads from a CDN at render time.

### 4.16 A video playing on a 3D device (template-three)
Get the clip's size and fps in `calculateMetadata` (mediabunny), build a rounded phone from an extruded `THREE.Shape`
(thickness 0.15, bevel 0.04, screen radius 0.07 of the base scale, outer radius = inner radius + bezel, screen plane
0.001 in front to avoid z-fighting), and feed the video into a canvas texture:
```tsx
const [canvas] = useState(() => new OffscreenCanvas(vw, vh));
const texture = useMemo(() => new THREE.CanvasTexture(canvas), [canvas]);
const invalidate = useThree((s) => s.invalidate);
const onVideoFrame = useCallback((img: CanvasImageSource) => {
  canvas.getContext("2d")!.drawImage(img, 0, 0, vw, vh);
  texture.needsUpdate = true;
  invalidate();
}, [canvas, texture, invalidate]);
// <Video src={src} headless muted onVideoFrame={onVideoFrame} />  (@remotion/media)
```
Screen material `meshBasicMaterial toneMapped={false} map={texture}` with `texture.repeat` = 1 / screen size (shape
UVs are in world units). Motion: entrance spring (damping 200, mass 3) with an extra full spin and rise from y = -4,
plus a constant 3 turns over the composition. Config `setChromiumOpenGlRenderer("angle")`.

### 4.17 Thousands of particles (three-particles)
One `<instancedMesh args={[undefined, undefined, 10000]}>` with a tiny dodecahedron and a Phong material around a
coloured point light. Per particle seed base values with `random("x" + i)` etc.; per frame compute a position and scale
from `t = frame * speed` with sin/cos wobble, write them through one reusable `Object3D` (`updateMatrix()`,
`setMatrixAt(i, dummy.matrix)`), then `instanceMatrix.needsUpdate = true`. Do this in `useFrame` or
`useLayoutEffect`: the example uses `useEffect`, which can lag the canvas by one frame under ThreeCanvas.

### 4.18 Map fly-along (mapbox-example)
Token from `process.env.REMOTION_MAPBOX_TOKEN` (the `REMOTION_` prefix exposes `.env` values to the bundle). Create
the map with `interactive: false, fadeDuration: 0`, pitch 65, add the route as a GeoJSON line layer on `style.load`,
and hold the first frame until `load`. Per frame: take a new delayRender, compute progress, place the free camera
along a separate camera path at a fixed altitude (4000 m) with `MercatorCoordinate.fromLngLat(point, altitude)`, call
`camera.lookAtPoint(pointOnRoute)` and `map.setFreeCameraOptions(camera)`, then release on `map.once("idle")`.
Advance both paths by the same fraction of their own length (`turf.along`). Rules: each render tab initialises and
bills its own map, so keep concurrency low (`--concurrency=1`); disable self-animating layers (label fades, POI,
terrain); do not call `map.remove()` in cleanup; give the container explicit size and absolute position; linear
lng/lat interpolation draws straight lines in Mercator (turf geodesics look curved); labels at least 40 px at 1080p;
`--gl=angle` locally, `swangle` on Lambda.

### 4.19 Transitions with character (transitions-video, light-leak-example, github-unwrapped)
- Defaults: `springTiming({config: {damping: 200}, durationInFrames: 10})` between short shots, `linearTiming` for
  crossfades, slide directions chosen so motion continues across the cut (github-unwrapped maps a per-user corner to
  matching exit and enter directions).
- Custom presentation:
```tsx
const WheelSpin: React.FC<TransitionPresentationComponentProps<Record<string, never>>> = ({
  children, presentationDirection, presentationProgress,
}) => {
  const deg = presentationDirection === "entering" ? (1 - presentationProgress) * 15 : -presentationProgress * 15;
  return <AbsoluteFill style={{transformOrigin: "-400% 50%", rotate: `${deg}deg`}}>{children}</AbsoluteFill>;
};
export const wheelSpin = (): TransitionPresentation<Record<string, never>> => ({component: WheelSpin, props: {}});
```
- Other hand-made presentations: CSS cube (parent `perspective`, `transformStyle: preserve-3d`, faces rotated 90 deg
  about the shared edge, `backfaceVisibility: hidden`); clock wipe (`makePie({radius: halfDiagonal, progress})` as an
  SVG clipPath on the entering scene); circle wipe (`makeCircle` scaled by progress); light-leak cut (entering side
  overlays a light-leak video with `mixBlendMode: "screen"` and the hard cut happens at the brightest moment,
  `progress > 0.3625`). Today prefer built-ins: `clockWipe`, `iris`, shader presentations, and
  `lightLeak()` from `@remotion/effects/light-leak` (4.0.500) over the deprecated `@remotion/light-leaks`.
- Sound on the cut: wrap a presentation so the entering side also mounts `<Audio src={whoosh}>` (the audio starts
  exactly when the transition starts).
- Mosaic transitions: 2x2 or 3x3 grids of independent TransitionSeries with staggered delays and a very long final
  sequence to hold; text-shaped masks (`WebkitMaskImage: url(...)`) over a TransitionSeries of colour fields.

### 4.20 Image-to-image GL transitions (gl-transitions)
The gl-transitions contract: fragment shader defines `vec4 transition(vec2 uv)` and uses `getFromColor(uv)`,
`getToColor(uv)`, `progress` (0..1), `ratio`; the harness adds `uniform sampler2D from, to` and aspect-correct lookup
(cover/contain/stretch), draws one oversized triangle `[-1,-1, -1,4, 4,-1]`, flips Y on upload, and binds extra
uniforms from `paramsTypes` with `defaultParams`. Integrate with Remotion by holding a delayRender through image load,
shader fetch and compile, then draw in `useLayoutEffect` on every frame with `progress = frame / (durationInFrames - 1)`
(the example's `frame / fps` is a bug). Use a per-instance canvas ref and `cancelRender` on init failure. For scene
transitions of live content use the HtmlInCanvas shader presentations or `makeHtmlInCanvasPresentation()` instead.

### 4.21 Shader effects on live DOM (html-in-canvas)
House template: `gl.ts` with `#version 300 es` shaders, a `linkProgram` that throws with the info log, `initGl(canvas)`
(WebGL2 `{alpha: true, premultipliedAlpha: true, antialias: false}`, `UNPACK_FLIP_Y_WEBGL`, one LINEAR/CLAMP texture,
a 6-vertex quad VAO, `blendFunc(ONE, ONE_MINUS_SRC_ALPHA)`), and `paintGl(gpu, elementImage, uniforms)`.
```tsx
const gpu = useRef<Gpu | null>(null);
const onInit: HtmlInCanvasOnInit = useCallback(({canvas}) => {
  gpu.current = initGl(canvas);
  return () => disposeGl(gpu.current!);
}, []);
const onPaint: HtmlInCanvasOnPaint = useCallback(({elementImage}) => {
  paintGl(gpu.current!, elementImage, {time: frame / fps, amount});
}, [frame, fps, amount]); // frame-derived deps trigger a repaint
return <HtmlInCanvas width={width} height={height} onInit={onInit} onPaint={onPaint}><Card /></HtmlInCanvas>;
```
Hash all randomness from frame numbers (sin-hash, value noise, fBm). If `onInit` needs an image, return a Promise and
await it there. Nesting is not allowed, so combine effects in one shader. Effect parameter sets worth reusing:
magnifier (radius 0.2, magnify 2.4, fBm wander, refraction `0.015 r^3`, chromatic split `0.004 r^2.5`); CRT (barrel
curvature (6, 5.5), scanlines 8 %, aperture mask 0.18, vignette 0.4, 1.2 % 60 Hz flicker); vintage film (grain 0.126
re-rolled at 24 fps, vignette 0.6, warmth 0.28, fade 0.385, gate weave, 3 scratches, dust); tilt-shift article
highlight (fixed 3D tilt, `mixBlendMode: multiply` highlighter, progressive Gaussian blur up to 4.25 px); glitch (40
bands, rare block tears per 60-frame window, un-premultiply before RGB split); burn dissolve (fBm threshold with
ember palette); sticker peel (cylinder curl, back face in paper colour, 2x oversampled canvas); "on threes" timing
(`Math.floor(frame / 3) * 3`) for a hand-made feel.

### 4.22 Motion blur (motion-blur-example)
Render N copies of the scene, copy i inside `<Freeze frame={frame - frameDelay * i}>` with opacity
`opacity - ((i + 1) / N) * opacity`, then the live scene on top (50 copies, delay 0.1 frame in the demo). Children must
fill an AbsoluteFill. Today use `@remotion/motion-blur` (`<CameraMotionBlur>`, `<Trail>`, since 3.2.39).

### 4.23 Speed ramps and time remapping (timing-functions, apple-wow, github-unwrapped)
```tsx
const remapSpeed = (frame: number, speed: (f: number) => number) => {
  let t = 0;
  for (let i = 0; i <= frame; i++) t += speed(i);
  return t;
};
const launch = remapSpeed(frame, (f) => 10 ** interpolate(f, [0, 60], [-1, 4])); // exponential take-off
const slowMo = remapSpeed(frame, (f) => (f < 20 ? 1.5 : 0.5)); // burst, then slow motion
return <Freeze frame={slowMo}><Burst /></Freeze>;
```
Landing = the same maths backwards (`remapSpeed(75 - frame, takeOff)`). A constant speed change can use
`<Sequence playbackRate>` (4.0.528, constant only); variable ramps still need this technique.

### 4.24 Camera moves: fly-through and zoom-through (timing-functions, github-unwrapped, 4-0-trailer)
`scale = 1 / distance` with distance interpolated from 1 toward 0.000005: the approach accelerates like a real dolly
and ends by rushing through. Drive distance with a reversed spring for exits. Mix an eased jump with a small linear term
(0.8 eased + 0.2 linear) so a zoom never looks stopped. Camera shake: `noise2D` on x/y (10 px) and rotation
(0.02 rad) times a decaying factor. Parallax: foreground scales from the bottom edge while background layers slide.

### 4.25 Particle bursts from composable wrappers (apple-wow-tutorial)
Small wrappers that each transform their children: `Explosion` (render children 10 times rotated `i / 10 * 2PI`),
`Move` (spring, damping 200, 120 frames, 0 to -400 px), `Shrinking` (scale 1 to 0 over frames 60..90), `Trail` (N
copies in `<Sequence from={i * 3}>` scaled `1 - i / N`), `Slowed` (remapped Freeze). Nest them: Slowed(Explosion(Move(
Trail(Shrinking(dot))))) and rotate groups by 0.3 rad to offset them.

### 4.26 Driving imperative libraries (anime-example, d3-example, css-animation-play-state)
- anime.js/GSAP-like: create with `autoplay: false` in an effect, then every frame `animation.seek(frame / fps * 1000)`
  (modulo duration for loops). Hold a delayRender until it exists if frame 0 matters.
- d3: let d3 build scales and axes once, and update the data join synchronously in an effect keyed on the
  Remotion-driven progress (`spring({frame: frame - 10, fps, config: {mass: 5, damping: 200}})`).
- Legacy CSS keyframes: `animationPlayState: "paused"` and `animationDelay: -(progress * duration)s`.

### 4.27 Jump cuts without remounting (video-with-jump-cuts)
```tsx
const SECTIONS = [{start: 0, end: 150}, {start: 210, end: 300}, {start: 390, end: 540}]; // source frames
let kept = 0;
const section = SECTIONS.find((s) => (kept += s.end - s.start) > frame) ?? SECTIONS[SECTIONS.length - 1];
const trimBefore = section.end - kept; // source frame = frame + trimBefore
return <OffthreadVideo src={staticFile("talk.mp4") + "#t=0,"} trimBefore={trimBefore} pauseWhenBuffering />;
```
One element for the whole timeline avoids a black flash at each cut; `calculateMetadata` sums the kept lengths. The
`#t=0,` suffix stops Remotion from appending its own time fragment. The example predates the rename, so it uses
`startFrom`.

### 4.28 Music generated in code (tone-js-example)
Inside a delayRender, `Tone.Offline(() => { schedule synth notes }, seconds)` renders an AudioBuffer faster than real
time; `audioBufferToDataUrl()` turns it into a WAV data URL for `<Audio src>`. Show the current note by accumulating
`Tone.Time("8n").toSeconds() * fps` per note and wrapping the note label in `<Sequence from={noteFrame} layout="none">`.
For long audio generate once in Node and save to `public/` (every render tab regenerates the data URL otherwise).

### 4.29 Transparent overlays and alpha video (template-overlay, github-unwrapped)
```ts
Config.setVideoImageFormat("png");
Config.setPixelFormat("yuva444p10le");
Config.setCodec("prores");
Config.setProResProfile("4444");
Config.setMuted(true);
```
This produces an alpha `.mov` for Premiere, Final Cut and DaVinci (WebM alternative: VP9 with `yuva420p`). Overlay
design: card top-right (90 px margins), spring in with mass 0.5 on `scale`, out with a 20-frame damped spring on
`rotate` and `translate`. To play alpha video in the browser Player ship two encodings: HEVC with alpha for Safari and
VP9 WebM with alpha for Chrome, choose by user agent, and use `<OffthreadVideo transparent muted>`.

### 4.30 Counters and number displays
Count-up: `Math.round(value * progress)` with a spring; odometer: old digit moves 0 to -200 px while the new one moves
200 to 0 inside an overflow-hidden box (shorts-customizer); slot wheel: digits on a 3D cylinder (`translateZ`,
`rotateX` per item, perspective 5000 to 10000, gradient mask top and bottom) stopped by a heavy spring (mass 10,
stiffness 200, damping 200, 100 frames, rest threshold 0.0001) plus a small pre-roll so it moves from frame 0
(github-unwrapped); seven-segment: digit images over a faint "8" (opacity 0.05), noise flicker 0.7..1.0, leading zeros
hidden, fixed width from the maximum digit count; stargazer-style: chase an eased target with a damped spring
simulated from frame 0 (k 170, c 26, m 1) and virtualise the list (render only rows within 3 of the current index).

### 4.31 Moving along paths, orbits and drawn lines (github-unwrapped, next-app-tailwind, helloworld)
```tsx
const len = getLength(d);
const at = Math.min(len, progress * len);
const p = getPointAtLength(d, at);
const tan = getTangentAtLength(d, Math.min(len, at + 0.0001)); // v5 returns null past the end
const angle = (Math.atan2(tan.y, tan.x) * 180) / Math.PI + 90; // sprite drawn pointing up
```
Paths to travel on come from `@remotion/shapes`: an arc from `makePie({closePath: false, rotation})`, an orbit from
`makeCircle` + `reversePath` (mirror with `scalePath(d, -1, 1)` for the other direction), loop with
`progress % 1` while the radius grows, then leave along the tangent. Draw-on strokes: `evolvePath(progress, d)`
(logos in next-app-tailwind: three strokes staggered 0/15/30 frames) or `strokeDasharray = length`,
`strokeDashoffset = length * (1 - progress)` (helloworld arcs, ellipse length approximated by
`2PI * sqrt((rx^2 + ry^2) / 2)`). Travelling border shine: stroke a `makeRect` outline with a linear gradient whose
`gradientTransform` rotates `frame * 7` degrees, or race a 250 px dash around the perimeter
(`strokeDasharray = "250 (perimeter - 250)"`, animated offset). Organic lines: perturb bezier control points with
`noise2D` via `reduceInstructions`/`serializeInstructions`, reveal with `evolvePath`, and ride a blurred dot on the
tip with `getPointAtLength`.

### 4.32 Sprite-sheet bursts (github-unwrapped Poof, StarSprite, Box)
Draw 6 to 8 explosion frames as separate inline SVG components and pick one per frame (`Math.round(useCurrentFrame())`
inside a `<Sequence from={hitFrame} layout="none">`), or hold each for 3 frames and play the set in reverse for an
implode. Position the sprite container at `x - w / 2, y - h / 2` and scale it with the object it replaces.

### 4.33 Formats and layout variants (shorts-customizer, github-unwrapped, prompt-to-motion-graphics skills)
- Design at 1080x1920 and render smaller by wrapping the scene in `scale(targetWidth / 1080)` (shorts-customizer
  renders 720x1280); stargazer designs at 512x288 and scales to the output with `transformOrigin: "top left"`.
- One component tree with a `layout: "short" | "landscape"` enum; `calculateMetadata` switches dimensions and the
  component switches sizes and slide directions.
- Social safe zones (prompt-to-motion-graphics social skill): top 12 %, bottom 15 %, sides 5 %; headline at least
  `max(48, 8 % of width)`, body at least `max(28, 4.5 % of width)`; hook motion from frame 0; loop-friendly endings.
- Stills from the same code: `<Still>` for OG images (1200x630), Instagram stories (1036x1973), and
  `<Freeze frame={175}>` of the logo animation for a 4K poster (4-0-trailer).

### 4.34 Talking-head auto edit (template-recorder)
1. Record: browser app captures webcam, screen and up to two extra cameras with exact `deviceId` constraints, writes
   MediaRecorder chunks (mp4 `avc1,mp4a.40.2` or webm `vp8,opus`, 32 Mbit/s, 2 s keyframes) to OPFS every 10 s,
   converts with mediabunny (max 1080p), uploads into `public/<compositionId>/webcam<ts>.mp4`, and transcribes with
   whisper.cpp to `subs<ts>.json`. Re-encode browser recordings to constant 30 fps with faststart before editing.
2. `calculateMetadata`: match the n-th `videoscene` to the n-th recording, read metadata and captions, auto-trim dead
   air (start = first word minus `ceil(fps / 4)`, end = last word plus `fps / 2`, plus user offsets), resolve webcam
   positions, compute every element's layout (`{left, top, width, height, borderRadius, opacity}`), overlap scenes by
   15 frames where a transition happens, and assign chapters.
3. Render: each scene is `<Sequence premountFor={30}>`; `<Video trimBefore trimAfter>` inside absolutely positioned
   layout boxes; transitions interpolate between the previous and next layouts (webcam corner moves are a "magic
   move"; if the path would cross the screen share, exit through the nearest edge and re-enter from the opposite one);
   enter/exit springs of 15 frames with `durationRestThreshold: 0.001`; SFX: shrink 0.2, grow 0.2, whip 0.1 volume.
4. B-roll: fade in landscape without display, otherwise a card that slides in from the edge away from the webcam while
   the scene behind scales down 10 % per active b-roll; clamp b-rolls to end before the scene transition.
5. Letterboxed media get a blurred cover copy behind them (110 % size, -5 % offset, blur 20 px).
6. Captions: see 4.3; landscape emits an SRT (at most 42 characters per line) through `<Artifact>`.

### 4.35 Music bed and loud parts (template-recorder, github-unwrapped)
```tsx
<Audio src={staticFile("music.mp3")} loop loopVolumeCurveBehavior="extend"
  volume={(f) => interpolate(f, [0, 30, dur - 30, dur], [0, 0.04, 0.04, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp"})} />
```
Keep music at 0.04 under speech and ramp to 1.0 over 30 frames in "loud parts" (titles, end cards); consecutive scenes
marked `music: "previous"` share one clip. github-unwrapped pre-cuts each track in 2 s steps (24 to 56 s) and picks the
one within 1 s of the video length so the music ends with the video; SFX start part-way with a negative `from` or
`trimBefore`.

### 4.36 Personalised videos at scale (github-unwrapped)
- One pure function `computeCompositionParameters(stats, theme)` produces input props on both the website (Player
  preview) and the server (Lambda render), so preview and render cannot diverge. Seeds per user make "random" choices
  stable.
- Render key `(username, theme)`; a Mongo record stores `{renderId, region, bucketName, functionName, account,
  finality}`; repeated requests return the stored URL or poll `getRenderProgress`; an in-memory pool dedupes
  concurrent clicks.
- Spread load: deploy the function and the site in every region of several AWS accounts, pick a random account and
  region per render, switch credentials with env vars; `deleteAfter: "30-days"`; `downloadBehavior: {type:
  "download", fileName}`; `getOrCreateBucket({enableFolderExpiry: true})`; `deployFunction({enableV5Runtime: true})`.
- Stills (OG 1200x630, Instagram story) render with `renderStillOnLambda({imageFormat: "jpeg", jpegQuality: 100,
  privacy: "public"})` in parallel with the video and are cached; the site proxies them with a 7-day Cache-Control.
- Player side: `numberOfSharedAudioTags={11}`, skip SFX on mobile, prefetch every asset before enabling Play, call
  `play(event)` inside the click handler.

### 4.37 Prompt to video (template-prompt-to-video)
1. Story: structured completion (`gpt-4.1`, `response_format: {type: "json_schema", strict: true}` from
   `z.toJSONSchema(schema)`) for an 8 to 10 sentence story in one paragraph.
2. Segmentation: second structured call splits the story into 5 to 8 segments of 1 to 2 sentences, each with a very
   detailed image description.
3. Assets per segment: an image (`dall-e-3`, `1024x1792`, 3 retries 1 s apart) and a voice clip with character
   timestamps (ElevenLabs `convertWithTimestamps`).
4. Timeline JSON validated by zod: `elements` (background images with startMs/endMs, enter/exit transition, scale
   animations alternating 1.5 -> 1 and 1 -> 1.5), `text` (caption chunks of at most 14 characters built from the
   character end times), `audio` (clip per segment). Random choices are made here, once, and frozen into the JSON.
5. Render: Root registers one composition per `public/content/<slug>/timeline.json`; calculateMetadata loads it;
   duration = last end + a 30-frame intro title card; backgrounds and voice clips are Sequences with
   `premountFor={3 * fps}`; captions use `fitText` (80 % width, max 120 px) with a stacked stroke layer. Note: the
   renderer ignores the per-caption animation data it generates, so do not rely on those fields.

### 4.38 Prompt to motion graphics: the generation loop (template-prompt-to-motion-graphics)
1. Validate the first prompt with a cheap structured classifier (motion-graphics request or not; fail open).
2. Detect which guidance skills apply (multi-label enum) and append only those not already used in the conversation.
3. Generate with a strict system prompt: ES imports, one `export const MyAnimation = () => {...};`, a short comment,
   hooks, then UPPER_SNAKE_CASE constants for colours, text, timing and layout inside the component, full-frame layout
   with padding, background colour set from frame 0, springs for organic motion and clamped interpolates for linear
   progress, a whitelist of imports, never shadow `spring`/`interpolate`/`useCurrentFrame`, code only.
4. Stream to the editor, strip fences, cut trailing prose by brace counting, check that it contains JSX.
5. Compile in the browser: strip imports, wrap the body, Babel `react` + `typescript` presets, `new Function` with an
   explicit scope (React, remotion subset, shapes, transitions, three, lottie). Preview in `<Player>` keyed by the
   component source; catch runtime errors with `errorFallback` and the `error` event.
6. On compile or runtime error, silently send a follow-up with the error text (up to 3 attempts, only while the last
   change came from the model). Follow-ups use structured output `{type: "edit" | "full", summary, edits:
   [{description, old_string, new_string}], code}`; the server applies edits only if each `old_string` matches exactly
   once, otherwise it returns the failed edit so the next attempt adds context. Manual user edits are flagged so the
   model preserves them.
7. Visual feedback: capture the current frame with `renderStillOnWeb({... scale: 0.5})` as JPEG and attach it to the
   next prompt for the vision model.
8. Render: Lambda with `framesPerLambda: 60`, or the web renderer. Key lesson: the prompt whitelist, the editor type
   stubs and the injected runtime scope must list the same names (the template teaches `Series`, but does not inject
   `Series`, `Easing`, `interpolateColors`, `staticFile` or `random`).

### 4.39 Render services (template-still, template-render-server, cloudflare-containers-demo, template-vercel, template-electron)
- Still server: bundle once at startup, `selectComposition` + `renderStill` per request, key the cache by
  `md5(JSON.stringify({composition, format, inputProps}))`, cache on disk or S3, one render at a time (`p-limit(1)`),
  rate limit 20 requests per minute, `ensureBrowser()` before listening.
- Job queue: in-memory map of jobs (`queued | in-progress | completed | failed`), a serial promise chain, per-job
  `makeCancelSignal()`, `DELETE` to cancel, outputs served statically.
- Containers: Docker image installs Chrome shared libraries, runs `npx remotion browser ensure` and `npx remotion
  bundle` at build time, sets the serve URL to the prebuilt bundle, renders one video per request and deletes it in
  `finally` (Cloudflare adds a Worker that stores the MP4 in R2).
- Vercel Sandbox: snapshot a sandbox with the bundle at build time, restore it per request, stream progress as SSE,
  keep working after the response with `waitUntil`, upload to Blob. Electron: render in the main process, ship the
  compositor binary for each platform unpacked from asar, report progress to the dock/taskbar.

### 4.40 The Studio as an editor (template-recorder, template-vibe-code, shorts-customizer)
Expose the video as a zod schema (discriminated unions for scene types, enums for positions and themes, `zColor()`
for colours, `.step(1)` for integers) so the Studio props panel is the editing UI. Add Studio-only helpers:
`writeStaticFile` + `updateDefaultProps` for drag-and-drop assets, `watchStaticFile` for live captions,
`focusDefaultPropsPath` to scroll the props panel to the current scene, `deleteStaticFile` + `saveDefaultProps` for
cleanup, all guarded by `isStudio && !isReadOnlyStudio`. Write compositions in the "editable" style: named
`Interactive.*` elements, named Sequences, individual transform properties whose values are inline `interpolate`
calls with literal keyframe arrays (vibe-code's samples), so visual edits can round-trip into code.

## 5. Performance and render stability

**Why frames must stand alone.** Renders split the frame range across browser tabs (and Lambda functions); a tab may
start in the middle and see frames in any order. The examples that survive this derive everything from the frame:
- No state carried from frame to frame. When a value depends on history (stargazer's spring chase, morph-text's word
  timeline, recorder's music clips), re-simulate from frame 0 or precompute a table in `calculateMetadata`; the
  re-simulation is O(frame) per frame, so memoise it for long videos.
- `random(seed)` or pre-baked tables only; `Math.random()` only in generation scripts whose output is frozen to JSON.
- Every tab repeats async initialisation: fonts, map instances, WebGL contexts, Tone.js synthesis, twoslash type
  checks. Keep init cheap, cache what can be cached (module-level promises), and remember external costs (Mapbox
  bills each map load, so concurrency multiplies cost).
- Effects that draw must finish before capture: imperative drawing belongs in `useLayoutEffect` or, for three.js,
  in `useFrame`; a passive `useEffect` may run after ThreeCanvas has already advanced (three-particles).
- CSS `transition`, CSS keyframes, `requestAnimationFrame`, react-spring and autoplaying libraries are not
  frame-controlled. The examples convert them (anime.js `seek`, CSS `animationPlayState: paused` + negative delay) or
  keep them on the website only (github-unwrapped `ShineEffect` vs `RemotionShineEffect`).

**delayRender hygiene.** Default timeout is 30 s. Every `delayRender` needs a success path (`continueRender`) and a
failure path (`cancelRender(error)`); several examples omit the failure path (react-router `load-fonts.ts`,
github-unwrapped `injectFont`, transitions-video font loader, gl-transitions init) and would hang to the timeout
with an unhelpful message, and trailer-2-0 ships a `delayRender` that is never continued. Give each handle a label.
Gate text layout behind a font gate component that renders nothing until fonts load (audiogram `WaitForFonts`,
recorder fonts module). Raise the timeout only when waiting is intended (stargazer: 1200000 ms for rate-limit waits).

**Heavy content.**
- Remote assets at render time (GLB on S3, drei `Environment` HDR from a CDN, avatars, fonts, logos) add latency and
  failure modes per tab; copy them to `public/`.
- Premount heavy media (`premountFor={3 * fps}` in prompt-to-video, `premountFor={30}` per recorder scene); v5
  premounts 1 s by default.
- Bake expensive visuals: github-unwrapped renders its CSS gradients to PNG stills at `scale: 2` and shows the PNG while
  rendering (CSS gradients can be slow or banded); it also cuts finished PR paths short so later frames draw less.
- Virtualise long lists (stargazer renders only cards within 3 rows of the current index); use instancing for
  thousands of meshes (three-particles: 10,000 instances).
- Hide hundreds of tiny Sequences from the Studio timeline (`showInTimeline={false}`) to keep the Studio responsive.
- Long audio: `useWindowedAudioData` fetches only a window with range requests (WAV only before 4.0.383);
  `useAudioData` decodes the whole file. Generated audio as a data URL is recomputed per tab and grows with length.
- Image sequences work (apple-wow draws a Memoji PNG sequence at twice the composition rate), but keep them in
  `public/` and prefetch in the Player.

**GPU and Chrome.** WebGL content needs `--gl=angle` locally on v4 (default `null` has no WebGL); Lambda and Cloud Run
use `swangle` (CPU, slower); Linux GPU servers use `angle-egl` with `setChromeMode("chrome-for-testing")` (gpu-scene);
`angle` leaks memory on long renders, so split very long GPU renders; GitHub Actions has no GPU. Skia sets
`setConcurrency(2)`. `chromiumOptions.enableMultiProcessOnLinux` (4.0.42) defaults to true. HtmlInCanvas WebGL effects
still need a GL backend even though the flag for `drawElementImage` is on in Remotion's Chrome.

**Lambda and servers.** Template defaults: 3009 MB RAM, 10240 MB disk, 240 s timeout, `framesPerLambda` 10
(next-app-tailwind) or 60 (prompt-to-motion-graphics): more frames per function means fewer invocations but less
parallelism. github-unwrapped uses 1200 MB and 120 s and spreads renders over several accounts and every region to
escape concurrency limits. Version the site name (`"...-" + VERSION` from `remotion`) so an upgrade deploys a new
site instead of breaking a live one, and redeploy function and site whenever Remotion, the template or the config
changes. Node servers: bundle once at startup, call `ensureBrowser()` before accepting work, render one job at a time
on small machines (`p-limit(1)` or a serial promise chain), support cancellation with `makeCancelSignal()`, and delete
outputs in `finally`. Buffering the whole MP4 in memory twice (cloudflare-containers-demo) caps video size.

**Player.** Mobile browsers limit simultaneous audio tags: set `numberOfSharedAudioTags` to the maximum number of
concurrent `<Audio>` (github-unwrapped: 11) and skip decorative SFX on mobile; v5 changes the default from 5 to 0.
Prefetch assets and only then enable Play; call `playerRef.play(event)` synchronously inside the click handler so audio
may start. Remount the Player when the component changes (`key={Component.toString()}` in prompt-to-motion-graphics).

**Inputs.** Browser recordings are variable frame rate: re-encode to constant 30 fps with `-movflags +faststart`
before editing (recorder). whisper.cpp needs 16 kHz WAV. Measure text only after the font is loaded.

## 6. Errors and fixes

| Symptom | Cause (where seen) | Fix |
|---|---|---|
| Render waits 30 s then fails with a delayRender timeout | async work without a failure path, or a handle never released (react-router `load-fonts.ts`, trailer-2-0 `HelloWorld.tsx`, github-unwrapped `injectFont`) | always `cancelRender(err)` in `catch`; label handles; use `useDelayRender()` |
| Captions linger or cut early | milliseconds added to a frame number (template-tiktok `startFrame + SWITCH_CAPTIONS_EVERY_MS`) | convert once: `frames = ms / 1000 * fps`; end a page at the next page's start |
| A stray ";" appears on screen | a semicolon after a JSX element inside `<Sequence>` (template-tiktok) | lint JSX children; never leave text nodes between elements |
| Generated code compiles but throws `ReferenceError` | the injected Babel scope lacks names the prompt allows (prompt-to-motion-graphics: `Series`, `Easing`, `interpolateColors`, `staticFile`, `random`) | keep prompt whitelist, editor stubs and runtime scope identical; feed runtime errors back |
| Three.js scene lags one frame or shows stale positions | per-frame mutations in `useEffect` under ThreeCanvas (three-particles) | mutate in `useFrame` or `useLayoutEffect` |
| Black or missing WebGL output in renders | default GL backend `null` in v4 (and no GPU in CI) | `--gl=angle` locally, `swangle` on Lambda, `angle-egl` on Linux GPU |
| `HtmlInCanvas` throws | unsupported browser in preview, or nested HtmlInCanvas | preview in Chrome 149+ with `chrome://flags/#canvas-draw-element`; render with Remotion's Chrome; merge effects into one shader |
| Early frames paint a black texture | image loaded inside `onInit` without waiting (html-in-canvas CenteredWhitePaper) | return a Promise from `onInit` and await the image |
| Encoder rejects odd width | computed widths (code-hike) | round dimensions up to even numbers |
| Player plays silently or drops audio on phones | too many audio tags, autoplay policy | `numberOfSharedAudioTags`, skip SFX on mobile, call `play(event)` in the click handler |
| Alpha video is opaque in Safari or Chrome | wrong codec per browser | HEVC with alpha for Safari, VP9 WebM with alpha for Chrome, `<OffthreadVideo transparent>` |
| Progress bar or caret animates in preview but not in render | CSS `transition` (prompt-to-motion-graphics progress-bar example) | compute the value from the frame |
| Path follower jumps or crashes at the end on v5 | `getPointAtLength`/`getTangentAtLength` return `null` past the end in v5 | clamp the length to `getLength(d)` |
| Tailwind width on `<Player>` ignored | Player's inline styles win | inline `style={{width: "100%"}}` |
| Hooks or context break in a shared component library | two copies of `remotion` bundled | make `remotion` (and react) peer dependencies (library-starter) |
| fitText/measureText returns wrong sizes | font not loaded yet | load first, `validateFontIsLoaded: true` (v5 default) |
| Chrome records from the wrong camera | `deviceId` passed as a plain string is only a preference | `deviceId: {exact: id}` (recorder) |
| Audio drifts or edits jitter on browser recordings | variable frame rate input | re-encode to constant fps with faststart |
| Old examples fail on 4.0.528 | renamed APIs: `startFrom`/`endAt` -> `trimBefore`/`trimAfter` (4.0.319); v3 `Config.Rendering.*`, `Config.Output.*`; `useVideoTexture`; `*BufferGeometry` JSX names; `turf.lineDistance` | use current names (`Config.setVideoImageFormat`, `<Video headless onVideoFrame>`, `dodecahedronGeometry`, `turf.length`) |
| vibe-code does not start on 4.0.528 | needs 4.0.529 features | pin the whole template to its own version or wait |
| Map style fails to load when copied from the vendored skill | invisible U+2060 word joiner inside the style URL in `maps.md` | retype the URL (the installed skill has a clean one) |
| Trim values off by a factor of fps | vendored `videos.md` calls `trimBefore`/`trimAfter` "seconds" | they are frames |
| Transparent WebM renders opaque | vendored skill sets `defaultCodec: "vp8"` after a VP9 example | use `vp9` with `yuva420p` |
| Input props ignored for a scene length | `calculateMetadata` reads `defaultProps` (github-unwrapped `calculateIssueDuration`) | read `props` |
| Cannot pass props from CLI or Lambda | `defaultProps` contain functions (github-unwrapped `renderLabel`) | keep props JSON-serialisable; pass keys, not callbacks |
| Lottie frames render "Loading..." | JSON fetched in `useEffect` without delayRender (prompt-to-motion-graphics example) | hold the frame or import the JSON |
| gl transition never completes | `progress = frame / fps` (gl-transitions) | `frame / (durationInFrames - 1)` |
| Two effect instances fight over one canvas | module-level `React.createRef()` (gl-transitions) | `useRef` per instance |
| Studio preview of Skia is empty or crashes | Root imported before CanvasKit loaded | `await LoadSkia()` then dynamic `import("./Root")` |
| Dockerfile fails to build | `apt install` without `apt-get update`, non-existent `USER pptruser` (template-still) | follow the render-server or cloudflare Dockerfile |
| `getVideoMetadata` fails on some files | deprecated helper, H.265 on Linux | mediabunny metadata |
| Light leak package warns deprecated | `@remotion/light-leaks` | `lightLeak()` from `@remotion/effects/light-leak` (4.0.500) |

## 7. What our skills must teach

### 7.1 Project rules (scaffold like the official templates)
- Start from the helloworld or blank shape: `registerRoot`, a `Root` with `<Folder>` groups, one composition per
  scene plus the full video, a `calculateMetadata` (even a stub) and a zod schema for every user-facing prop.
- Register edge-case variants of data-driven scenes (empty, small, huge values) as extra compositions and check them
  with stills before a full render.
- Keep constants shared between Player, API routes and compositions in one module (`COMP_NAME`, size, fps, duration).
- Put every render-time asset in `public/` and reference it with `staticFile()`; forbid remote URLs at render time
  unless the user insists (and then prefetch and hold a delayRender).
- `remotion.config.ts` does not apply to Node APIs: pass `webpackOverride`, GL, codec and similar options to
  `bundle()`, `renderMedia()` and `deploySite()` explicitly.
- Props must be JSON-serialisable (no functions); read `props`, not `defaultProps`, in `calculateMetadata`.

### 7.2 Determinism checklist (run before every render)
1. No `Math.random()`, `Date.now()`, `requestAnimationFrame`, CSS transitions or keyframes, autoplaying libraries.
2. Every async task holds a labelled delayRender and releases it on success and failure.
3. Fonts are loaded (and awaited) before any `measureText`/`fitText`/`fillTextBox` call.
4. Imperative drawing runs in `useLayoutEffect` or `useFrame`, keyed on frame-derived values.
5. State that depends on history is recomputed from frame 0 or precomputed in `calculateMetadata`.
6. SVG ids are unique per instance (`useId()`).
7. Media inside Sequences: remember local time; add the Sequence start when analysing global audio.

### 7.3 Motion defaults (decision table)

| Goal | Default |
|---|---|
| Clean entrance, no bounce | `spring({config: {damping: 200}})`, 15 to 30 frames |
| Playful pop | damping 12 to 15, stiffness 100 to 170, or `mass: 0.5` |
| Heavy object, slot wheel | mass 3 to 10, `durationRestThreshold` 0.001 or lower |
| Exit | same spring with `delay: duration - n` or `reverse: true`; envelope = in minus out |
| Stagger | 2 to 5 frames per item (1 frame per letter, 38 frames per chat message) |
| Linear progress bars, wipes | `interpolate` with both sides clamped, optional `Easing.out(Easing.cubic)` |
| Fly through or zoom into something | `scale = 1 / distance`, distance 1 toward 0.000005 |
| Speed ramp | integrate a speed function (`remapSpeed`) and render under `<Freeze>`; constant speed: `Sequence playbackRate` |
| Organic wander, shake, flicker | `noise2D(seed, t, 0)` with amplitude falling off over time |
| Loop | modulo of the frame with exact tile sizes (`frame % 28` over 28 px rows) |
| Hand-made or retro feel | quantise time "on threes" (`Math.floor(frame / 3) * 3`) |
| Transition between shots | `springTiming({config: {damping: 200}, durationInFrames: 10..20})`; motion direction continuous across the cut |

### 7.4 Text and captions
- Captions pipeline: 16 kHz WAV -> whisper.cpp (`tokenLevelTimestamps: true`) -> `toCaptions` -> clean-up (fillers,
  sub-word merge, autocorrect list) -> `createTikTokStyleCaptions` or `fillTextBox` paging -> one Sequence per page that
  lasts until the next page -> active-word highlight from page-relative milliseconds.
- Short-form default: uppercase bold, `fitText` within 90 % width capped at 120 px (80 px for mixed case), outline with
  `paintOrder: "stroke"`, highlight colour for the active word, bottom third but inside the safe zone, 5-frame spring
  pop per page.
- Long-form default: box karaoke (grey to full colour 100 ms before each word), 5 lines per page, balanced page breaks.
- Typewriters slice strings; carets blink only after typing; carousels reserve the longest word's width.
- Fit to box, never overflow: always measure with the real font.

### 7.5 Audio
- Music under speech at about 0.04 volume with 30-frame ramps; raise to 1.0 in sections without speech; match music
  length to the video (pre-cut variants or fade the tail); SFX at 0.1 to 0.2 locked to transitions.
- Visualisers: `useWindowedAudioData` for anything longer than a minute; log-spaced bins and a rising gain for
  spectra; `Math.sqrt` or dB mapping for perceived loudness; posterise the frame for a stepped look.
- Generated audio (Tone.js) and TTS are produced before rendering and saved to `public/` when long.

### 7.6 3D, GPU and effects (decision table)

| Need | Use |
|---|---|
| Real 3D models, lighting, particles | `@remotion/three` `<ThreeCanvas width height>`, `--gl=angle` |
| Flat graphic 3D (logos, type, UI) without WebGL | CSS 3D (`perspective`, `preserve-3d`) or SVG extrusion |
| Video on a 3D surface | `<Video headless onVideoFrame>` into a `CanvasTexture` |
| Vector glow, path trims, neon | Skia (`LoadSkia`, `enableSkia`) or SVG strokes with `evolvePath` |
| Post effects on live DOM (CRT, film, glitch, peel) | `<HtmlInCanvas>` with one WebGL2 shader, or built-in `effects` |
| Shader scene transitions | built-in HtmlInCanvas presentations, `makeHtmlInCanvasPresentation()` |
| Maps | Mapbox free camera with turf paths, low concurrency, no self-animating layers |

### 7.7 Data-driven and personalised video architecture
- Pure `computeProps(data)` shared by preview and render; seeds from a stable user key.
- `calculateMetadata` computes durations and layouts; scenes appear only if their data exists (nullable scenes in a
  TransitionSeries); music variant chosen by length.
- Cache renders by `(user, variant)`; store render ids and poll progress; dedupe concurrent requests; set
  `deleteAfter`; generate social stills alongside the video.

### 7.8 Our own generation loop (lessons from prompt-to-motion-graphics and prompt-to-video)
- Separate planning (structured JSON: timeline, scenes, assets) from rendering (a stable component library).
- When the model writes code: a strict system prompt (structure, constants block, whitelist, full-frame layout,
  background from frame 0), skill snippets injected by detected intent, a compile step, a Player or still-frame check,
  and an automatic repair loop capped at 3 attempts that sends the exact error text.
- Edits as exact `old_string`/`new_string` pairs that must match once; fall back to full replacement for large
  changes; preserve user edits.
- Visual self-check: render stills of chosen frames (`renderStillOnWeb` or `npx remotion still`) and look at them
  before rendering the full video.

### 7.9 Where to render (decision table)

| Situation | Choice (template to copy) |
|---|---|
| Local one-off | CLI `npx remotion render` (helloworld) |
| Dynamic OG images | Express still server with md5 cache (template-still) |
| Background jobs on one machine | queue + `renderMedia` + cancel (template-render-server) |
| Web app, bursty load | Lambda with progress polling (next-app-tailwind, react-router) |
| Vercel stack | Vercel Sandbox + Blob with a build-time snapshot (template-vercel) |
| Cloudflare stack | Container with pre-bundled site + R2 (cloudflare-containers-demo) |
| Desktop app | Electron main-process rendering (template-electron) |
| No server, small outputs | `renderMediaOnWeb` / `renderStillOnWeb` (vibe-code, prompt-to-motion-graphics) |
| CI | GitHub Actions `workflow_dispatch` inputs -> `--props` file (stargazer); no GPU there |

### 7.10 Version gates for 4.0.528
- Available: `useDelayRender` (4.0.342), HtmlInCanvas (4.0.455) with `effects`/`pixelDensity`/crop, shader
  presentations up to `blurSlide` (4.0.523), `lightLeak()` in `@remotion/effects` (4.0.500), `Sequence trimBefore`
  (4.0.482), `freeze` (4.0.476), `playbackRate` (4.0.528), `AbsoluteFill` Sequence props (4.0.501), media
  `from/durationInFrames` (4.0.445) and premount props (4.0.495), `Interactive` (4.0.475), captions `pageBreakAfter`
  (4.0.517) and `breakOnSilenceAfterMilliseconds` (4.0.514), ThreeWebGPUCanvas (4.0.503, experimental).
- Not available: anything the vibe-code template needs from 4.0.529, `interpolatePaths()` and `HtmlInCanvasMotionBlur`
  (4.0.529).
- Renamed or deprecated: `startFrom`/`endAt` -> `trimBefore`/`trimAfter` (4.0.319); `getVideoMetadata()` ->
  mediabunny; `@remotion/light-leaks` -> `@remotion/effects`; `useVideoTexture` -> headless video; `getStaticFiles`
  -> `@remotion/studio` export.
- Prepare for v5: GL default `angle`, premount by default, `numberOfSharedAudioTags` default 0, `validateFontIsLoaded`
  default true, Google Fonts need explicit weights and subsets, `selectComposition` needs `inputProps`, path sampling
  returns `null` past the end, no `layout="none"` on TransitionSeries, bt709 default colour space.

### 7.11 Licensing and hygiene
- Do not reuse music, fonts or brand assets from 4-0-trailer, github-unwrapped (SmartSound music), or the paid
  animated-captions code; learn the techniques.
- Never commit tokens: Mapbox and GitHub tokens go in `.env` as `REMOTION_*` variables; Lambda keys as
  `REMOTION_AWS_ACCESS_KEY_ID`/`REMOTION_AWS_SECRET_ACCESS_KEY`.
- Remotion needs a company licence for companies (github-unwrapped's About page states it).

### 7.12 Suggested skill modules and their best sources
captions (tiktok, audiogram, recorder); audio-viz (audiogram, music-visualization, trailer-2-0); code-animation
(code-hike, trailer); text-fx (morph-text, text-warping, prompt-to-motion-graphics typography skill); 3d (three,
3d-text, glb-example, three-particles, 4-0-trailer); gl-and-effects (html-in-canvas, gl-transitions); transitions
(transitions-video, light-leak-example, github-unwrapped TopLanguages); maps (mapbox-example); data-video
(github-unwrapped, stargazer); talking-head-edit (recorder, video-with-jump-cuts); ai-pipelines (prompt-to-video,
prompt-to-motion-graphics); render-infra (still, render-server, next-app-tailwind, vercel, cloudflare, electron).

## 8. Best examples to learn from

Templates (`repo/packages/...`):
- `template-recorder/remotion/calculate-metadata/calc-metadata.ts`: the model for data-driven editing; every scene's
  media, captions, trims, layouts and chapters are resolved before rendering.
- `template-recorder/remotion/animations/interpolate-layout.ts` and `remotion/layout/*`: layouts as plain objects
  interpolated between scenes, the cleanest "magic move" implementation in the material.
- `template-recorder/remotion/captions/processing/layout-captions.ts` and `postprocess-subs.ts`: production caption
  clean-up and balanced page breaking.
- `template-recorder/remotion/audio/AudioTrack.tsx`: music bed with ducking, loud parts and overlap compensation.
- `template-recorder/remotion/scenes/BRoll/apply-b-roll-rules.ts`: rule-based clamping of overlays to scene bounds.
- `template-prompt-to-motion-graphics/src/app/api/generate/route.ts`: validation, skill detection, streaming and
  structured edit follow-ups in one route.
- `template-prompt-to-motion-graphics/src/remotion/compiler.ts`: in-browser compile with an explicit injected scope.
- `template-prompt-to-motion-graphics/src/hooks/useAutoCorrection.ts`: capped automatic repair loop.
- `template-prompt-to-motion-graphics/src/skills/*.md`: compact motion-design guidance per topic (charts, typography,
  messaging, transitions, sequencing, spring physics, social media, 3D).
- `template-prompt-to-video/cli/timeline.ts`: turning TTS character timestamps into captions and a timeline JSON.
- `template-code-hike/src/CodeTransition.tsx`: token-level code morphing driven by frames.
- `template-tiktok/src/CaptionedVideo/index.tsx` and `Page.tsx`: minimal caption paging and styling (note its ms/frame bug).
- `template-audiogram/src/Audiogram/Captions.tsx` and `Oscilloscope.tsx`: `fillTextBox` paging and windowed audio.
- `template-music-visualization/src/helpers/process-frequency-data.ts`: perceptually balanced spectrum.
- `template-three/src/Phone.tsx`: headless video to three.js texture.
- `template-overlay/remotion.config.ts`: transparent ProRes 4444 in five lines.
- `template-still/src/server/index.ts` (with `cache.ts`, `make-hash.ts`): cached image server.
- `template-render-server/server/render-queue.ts` and `Dockerfile`: job queue with cancellation and a correct image.
- `template-next-app-tailwind/deploy.mjs` and `src/app/api/lambda/*/route.ts`: Lambda deploy and progress polling.
- `template-vercel/src/app/api/render/route.ts` and `create-snapshot.ts`: SSE progress and snapshot cold starts.
- `template-electron/src/render-video.ts` and `forge.config.ts`: shipping the renderer in a desktop app.
- `template-stargazer/src/Root.tsx`, `wait-for-no-input.ts`, `Content.tsx`: abortable data fetching and a list
  virtualised by a simulated spring.
- `template-vibe-code/src/editor/hooks/use-compiler.ts` and `src/remotion/*.tsx`: browser bundling loop and the
  "editable" composition style.
- `template-skia/src/SkiaNeon.tsx`: neon write-on with stacked blurred strokes.

Examples (`examples/...`):
- `github-unwrapped/remotion/Main.tsx` and `Root.tsx`: data-driven Series with overlaps, music chosen by length, every
  scene registered with edge-case props.
- `github-unwrapped/remotion/TopLanguages/PlanetScaleSpiral.tsx`, `PlanetScaleOut.tsx`, `PlaneScaleWiggle.tsx`,
  `AllPlanets.tsx` and `remotion/move-along-line.ts`: path travel, orbits and direction-aware transitions.
- `github-unwrapped/remotion/Issues/get-shots-to-fire.ts` and `index.tsx`: a data-driven shoot-'em-up with SFX caps.
- `github-unwrapped/remotion/StarsGiven/*`: fly-through stars, cockpit screens via `matrix3d`, noise camera shake.
- `github-unwrapped/remotion/Productivity/Wheel.tsx`: slot-machine wheel with a heavy spring.
- `github-unwrapped/remotion/Opening/TakeOff.tsx` and `EndScene/LandingRocket.tsx`: exponential speed ramps.
- `github-unwrapped/src/server/render.ts` and `deploy.ts`: multi-account, multi-region Lambda with caching.
- `github-unwrapped/vite/VideoPage/Player/Player.tsx`: Player tuned for mobile audio and prefetch.
- `github-unwrapped/vite/VideoPage/Background/octocat-line.tsx`: one animation function for website (rAF) and video.
- `html-in-canvas/src/Crt/*`, `src/Vintage/*`, `src/MagnifyingGlass/*`, `src/Bonus/GlitchComposition.tsx`: the WebGL2
  effect template with tuned parameters.
- `transitions-video/src/presentations/*.tsx` and `src/add-sound.tsx`: custom presentations and SFX on cuts.
- `light-leak-example/src/presentation.tsx`: a cut hidden in a light leak.
- `apple-wow-tutorial/src/*.tsx`: composable motion wrappers and a slowed trail.
- `timing-functions/src/remap-speed.tsx`, `TimeRemapping.tsx`, `CameraApproach.tsx`: speed ramps and 1/distance zoom.
- `4-0-trailer/src/3d-svg.ts`, `element.ts`, `Faces.tsx`, `matrix.ts`: SVG extrusion engine; `DigitWheel.tsx`,
  `AudioViz.tsx`, `NameTag.tsx`, `NumberedChapter.tsx` for scene ideas.
- `trailer/src/CodeFrame.tsx` and `GlowingStroke.tsx`: growing code lines and a racing border.
- `trailer-2-0/src/AudioVisualization.tsx`, `AudioDemo.tsx`, `Showcase.tsx`: meters, fake editors, 3-point scroll.
- `morph-text/src/Composition.tsx`: gooey morph with an SVG alpha threshold.
- `text-warping/src/Api.tsx`, `Blocks.tsx`, `helpers/get-path.ts`: `warpPath` recipes.
- `3d-text/src/TextMesh.tsx`: extruded long-shadow type in orthographic three.js.
- `glb-example/src/Stage.tsx`: fixed-radius stage for turntables.
- `three-particles/src/Dust.tsx`: instanced particles.
- `mapbox-example/src/Composition.tsx`: free camera per frame with delayRender per frame.
- `tone-js-example/src/ToneJS/index.tsx`: offline synthesis to a data URL.
- `video-with-jump-cuts/src/JumpCuts.tsx`: cuts without remounting.
- `anime-example/src/Composition.tsx`, `d3-example/src/Composition.tsx`, `css-animation-play-state/src/Composition.tsx`:
  taming imperative libraries.
- `shorts-customizer/src/videos/Whirl.tsx`, `Score.tsx`, `SlidingText.tsx`, `NewScore.tsx`, `1080pScaler.tsx`:
  sports-highlight motion and design-at-1080 scaling.
- `cloudflare-containers-demo/Dockerfile` and `src/server.ts`: modern container render image.
- `gpu-scene/remotion.config.ts` and `render.mjs`: GPU flags for Linux servers.
- `library-starter/packages/library/package.json`: `remotion` as a peer dependency.
- `animated-captions/src/AnimatedCaptions/styles/*`: study the ideas only (paid, not redistributable).

## 9. Open questions

1. Is a fractional `Sequence from` officially supported? tiktok and github-unwrapped (`from={i * 1.5}`) use fractional
   values; the docs do not say, and our core source copy is partial. Our skills round to integers until confirmed.
2. Under `ThreeCanvas`, do passive `useEffect` mutations in children always lag one frame, or only sometimes? Inferred
   from `repo/packages/three/src/ThreeCanvas.tsx`; needs a render test.
3. Do WebGL canvases inside compositions need `preserveDrawingBuffer: true` to be captured reliably? None of the
   examples set it; html-in-canvas works through `onPaint`.
4. Is `@remotion/svg-3d-engine` meant to be public? It has sources and is used by `packages/example`, but no docs page
   and no `package.json` in our copy.
5. How should `numberOfSharedAudioTags` be sized in general: github-unwrapped sets 11 and also caps SFX in code;
   v5 defaults to 0. A rule of thumb for our Player skill is needed.
6. HtmlInCanvas performance on `swangle` (Lambda, no GPU): heavy shaders (9x9 blur, fBm) may be slow; no numbers in
   the material.
7. `@remotion/light-leaks` versus `@remotion/effects/light-leak`: the effect needs canvas-based components (`<Video>`,
   `<CanvasImage>`, `<Solid>`); is there a drop-in replacement for a light leak laid over a whole transition
   (`TransitionSeries.Overlay`)?
8. vibe-code needs 4.0.529 features (`controller.setSequenceNodePaths`, `controller.overrides`, sequence controls):
   which of `@remotion/browser-bundler`, `@remotion/canvas` and `@remotion/codemods` work on 4.0.528 alone?
9. The prompt-to-motion-graphics validation classifier fails open; is that the right default for an autonomous agent
   that pays per render?
10. Whisper model choice for non-English projects: which model and whisper.cpp version give usable token timestamps
    per language, and how does `splitOnWord` behave for scripts that do not separate words with spaces?

## Appendix A. Template catalogue (`repo/packages/template-*`)

Common scaffolding: `src/index.ts` registers the root; `remotion.config.ts` usually sets `Config.setRspack(true)`,
`setVideoImageFormat("jpeg")`, `setOverwriteOutput(true)` with a comment that the file does not apply to Node APIs;
scripts `dev: remotion studio`, `build: remotion bundle`, `upgrade: remotion upgrade`, `lint: eslint src && tsc`;
eslint 9 flat config from `@remotion/eslint-config-flat`; tsconfig ES2018, module Preserve, bundler resolution,
strict; `out/` ignored.

### A.1 template-blank
- Produces: an empty 1280x720, 30 fps, 60-frame composition.
- Build: the component file registers its own `<Composition>` and exports a typed `CalculateMetadataFunction` stub.
- Copy: co-locate registration with the component and add `calculateMetadata` from day one.

### A.2 template-helloworld (the canonical starter)
- Produces: 1920x1080, 30 fps, 150 frames: a React-style atom logo draws on and lifts, a title appears word by word, a
  subtitle fades in, everything fades out at the end; plus an `OnlyLogo` composition to iterate on the logo alone.
- Build: logo lift = `spring({frame: frame - 25, fps, config: {damping: 100}})` mapped to translateY 0..-150; title
  in `<Sequence from={35}>`, subtitle `<Sequence from={75}>`; words staggered 5 frames with `spring({damping: 200})`
  on `scale` (words are inline-block); three ellipse arcs drawn with dash offsets and rotated by spring progress; the
  whole logo rotates 0..360 over the video; global fade `interpolate(frame, [dur - 25, dur - 15], [1, 0], clamp)`.
- Copy: the timing skeleton (enter, hold, fade), per-word stagger, SVG draw-on arcs, unique gradient ids per instance.
- Techniques: ellipse perimeter approximation for dash lengths; `zColor()` props.

### A.3 template-still (dynamic OG images plus a render server)
- Produces: a 1200x627 `<Still>` card (gradient title, 2-line clamped description, a sine-wave dotted swirl on canvas)
  and an Express server that renders it on demand.
- Build: schema `{title, description, color: zColor()}`; route `/:composition.:format(png|jpe?g)` with the query
  string as input props; md5 cache key; filesystem, S3 or no cache; `p-limit(1)`; 20 requests per minute;
  `bundle()` once, `selectComposition` + `renderStill` per request; `ensureBrowser()` at startup.
- Copy: the cache-keyed still server, `whiteSpace: "pre-wrap"` so `%0A` in URLs becomes a line break, canvas drawing
  in an effect keyed on props and frame.
- Caveat: its Dockerfile is illustrative (missing `apt-get update`, non-existent user); use the render-server one.

### A.4 template-overlay
- Produces: a 75-frame 1920x1080 transparent lower-third style card for editing software.
- Build: ProRes 4444 config (4.29); card top-right, `loadFont("normal", {subsets: ["latin"], weights: ["400", "700"]})`
  from `@remotion/google-fonts/Roboto`; enter `spring({config: {mass: 0.5}})` on `scale`; exit spring (damping 200,
  20 frames before the end) on `rotate` 0..-PI/20 rad and `translate` 0..-500 px, as separate CSS properties.
- Copy: the alpha export config and the separate `scale`/`translate`/`rotate` properties.

### A.5 template-three
- Produces: a 300-frame 1280x720 phone or tablet (schema enum) spinning in 3D with a video playing on its screen.
- Build: `calculateMetadata` picks the clip and reads its size and fps with mediabunny; `ThreeCanvas linear`,
  ambient 1.5 + point light; rounded device from an extruded shape; video texture via headless `<Video>` (4.16);
  camera set once (position z 2.5, near 0.2); spin `interpolate(frame, [0, dur], [0, 6PI])` plus an entrance spring.
  Config `setChromiumOpenGlRenderer("angle")`. Deps: three 0.178, R3F 9.2, mediabunny 1.56.
- Copy: headless video textures, derive layout from media, z-offset against z-fighting.

### A.6 template-skia
- Produces: a neon signature writing itself (SkiaNeon) and a Skia hello-world.
- Build: `await LoadSkia()` before importing the Root; `enableSkia` bundler override; `setConcurrency(2)`; paths from
  SVG strings fitted with `fitbox("contain")`; each of 7 segments trims in over 15 frames (`<Path end={progress}>`);
  glow = the same path stroked 4 times (15 px + animated blur, 4 px + blur 1.75, 1 px, white 2.5 px core) with a
  linear gradient over the tight bounds; interior fill clipped to the path.
- Copy: stacked-stroke neon, path trim write-on. Add delayRender around async Skia font/image loading (the template
  does not).

### A.7 template-tiktok
- Produces: vertical 1080x1920 video with word-highlighted captions; fps 30 and duration from the source video.
- Build: `sub.mjs` transcribes every video in `public/` with whisper.cpp 1.6.0 `medium.en`; the composition loads
  captions under `useDelayRender`, pages them at 1200 ms, sizes with `fitText`, strokes with `paintOrder`, highlights
  the active token `#39E508`, pops pages with a 5-frame spring; background `<OffthreadVideo objectFit: cover>`.
- Copy: the whole pipeline (4.2). Avoid its bugs: ms added to frames, a stray ";" text node, unrounded `from`.
  It still uses the deprecated `getVideoMetadata()`.

### A.8 template-audiogram
- Produces: a 1080x1080 podcast clip: cover, episode title (an `Interactive.Div`), oscilloscope or spectrum, and
  scrolling word captions.
- Build: `calculateMetadata` loads captions (`.json` or `.srt` via `parseSrt`) and audio duration (mediabunny); schema
  is a discriminated union for the visualiser with sensible defaults (spectrum 65 lines, oscilloscope window 0.1 s,
  posterisation 3, amplitude 4); `WaitForFonts` gate; `transcribe.ts` asks for the speech start second to skip intro
  music and shifts all timestamps.
- Copy: 4.3 and 4.5; visualiser options as a discriminated union so Studio shows only relevant fields.

### A.9 template-music-visualization
- Produces: a 1080x1080 song preview with a spectrum or waveform, an optional bass flash, and a cover card.
- Build: duration = audio length minus the chosen offset; the whole piece sits in `<Sequence from={-offsetFrames}>`;
  windowed audio (30 s); log-spaced balanced bins (4.6); glassy song card (cover 280 px, radius 20, name 5.5rem,
  artist 3.5rem).
- Copy: the frequency processing function and the negative-from offset trick.

### A.10 template-code-hike
- Produces: an animated code walkthrough: each `public/code*` file becomes a step with token-level morphs, type
  callouts and error squiggles, plus a story-style progress bar.
- Build: see 4.8. Config aliases `@code-hike/lighter` to its ESM build and ignores a dynamic-require warning; twoslash
  runs in the browser from a CDN; width computed from the longest line and forced even.
- Copy: snapshot/transition token morphs, even-dimension rule, Studio auto-reload on public file changes.

### A.11 template-stargazer
- Produces: a 960x540 video of a repository's GitHub stars counting up while stargazer cards scroll past (15 s by
  default, props `repoOrg`, `repoName`, `starCount`, `duration`).
- Build: `calculateMetadata` fetches stargazers via GraphQL (token from `REMOTION_GITHUB_TOKEN`) or REST without dates,
  debounces Studio edits with `waitForNoInput(abortSignal, 500)` unless `isRendering`, waits 60 s on rate limits
  (timeout raised to 20 min), caches pages in localStorage; progress = a damped spring (k 170, c 26, m 1) chasing an
  ease-in-out-cubic target, re-simulated from frame 0; the scene is designed at 512x288 and scaled up; only cards
  near the current index render; the last second holds. A GitHub workflow renders from `workflow_dispatch` inputs
  and installs Noto fonts (CJK and emoji in user names).
- Copy: abortable, debounced data loading; virtualised lists; CI rendering with fallback fonts.

### A.12 template-prompt-to-video
- Produces: a 9:16 narrated story slideshow from a title and topic (demo: 54 s, 8 images, 78 caption chunks).
- Build: CLI (`bun cli/cli.ts`) runs 4.37; renderer registers one composition per timeline; intro card 30 frames
  (yellow box, 10 px black border, Bree Serif 120 px); backgrounds with Ken Burns and 1 s blur transitions (up to
  25 px); voice clips as `<Audio from durationInFrames premountFor>`.
- Copy: planning JSON + dumb renderer; caption chunking from TTS character timestamps; structured outputs from a zod
  schema with `strict: true`. Note: the README suggests passing a timeline URL as a prop to turn it into a service.

### A.13 template-prompt-to-motion-graphics (and examples/template-prompt-to-motion-graphics-saas)
- Produces: a Next.js 16 SaaS where a prompt becomes a Remotion component that previews live and renders on Lambda.
- Build: 4.38. Models offered: gpt-5.2 with reasoning none/low/medium/high (default low) and gpt-5.2-pro. Guidance
  skills are Markdown files imported as strings (raw-loader for Turbopack, `asset/source` for webpack). Composition
  `DynamicComp` 1920x1080 takes `{code, durationInFrames, fps}`; it compiles the code under delayRender and shows a
  red error slate if compilation fails. Lambda: 3009 MB, 240 s, `framesPerLambda: 60`; `deploy.mjs` exits cleanly when
  credentials are missing so Vercel builds pass.
- Copy: the loop design, structured edits, error feedback, still-frame feedback for vision models, skill snippet
  injection. Fix its scope gap; do not copy the progress-bar example's CSS transition or the Lottie example's
  unheld fetch.
- Guidance values worth keeping: charts (bars staggered 3 to 5 frames, spring damping 18 stiffness 80, labels inside
  bars only above 30 px, pie via circle dash array), messaging (38-frame stagger, 18-frame fade, pop spring damping 12
  stiffness 170 from the tail corner, WhatsApp dark and iMessage palettes), spring presets (snappy 20/200, bouncy
  8/100, smooth 200/100, heavy 15/80 mass 2), 3D defaults (camera `[0, 0, 5]` fov 75, ambient + directional light).

### A.14 template-vibe-code
- Produces: a browser-only motion-graphics editor: Monaco code tabs, a canvas preview, a timeline and an inspector
  that write edits back into the source, plus in-browser MP4/WebM rendering.
- Build: `@remotion/browser-bundler` (rspack WASM in a worker, needs COOP/COEP headers), React Fast Refresh inside a
  same-origin iframe, `@remotion/canvas` as the preview surface, `@remotion/codemods` for every visual edit (update
  props, split, wrap in Sequence, reorder, add media, add or rename compositions) followed by Prettier, live overrides
  while dragging, `renderMediaOnWeb`/`renderStillOnWeb` for export. Needs 4.0.529.
- Copy: the "editable composition" authoring style (named `Interactive.*` elements, literal keyframe arrays, CSS
  string interpolation) and Studio-compatible shortcuts (Space, J/K/L, I/O, cmd+D, R, G).

### A.15 template-next-app-tailwind
- Produces: a Next.js 16 page with a Player preview of a 200-frame 1280x720 title animation and a Lambda render
  button with progress and download.
- Build: shared constants module; Tailwind v4 in compositions via `enableTailwind` (also passed to `deploySite`);
  rings zooming out with `scale(1 / (1 - outProgress))`, logo strokes drawn with `evolvePath`, a diagonal mask wipe
  for the title (`maskImage: linear-gradient(-45deg, transparent L%, black R%)`, R from 200 to 0, L = R - 60);
  API routes `renderMediaOnLambda` (`framesPerLambda: 10`) and `getRenderProgress`, polled every second.
- Copy: the full Lambda flow and the soft diagonal text wipe; size the Player with inline styles.

### A.16 template-vercel
- Produces: the same app rendering in Vercel Sandbox and storing results in Vercel Blob.
- Build: `@remotion/vercel` (4.0.426); a build step creates a sandbox with the bundle and snapshots it; requests
  restore the snapshot (5-minute timeout), render with progress streamed over SSE, upload to Blob, stop the sandbox.
- Copy: snapshot-based cold starts and SSE progress; add rate limiting and spend limits yourself (README warns).

### A.17 template-react-router
- Produces: the same Lambda flow on React Router 8 (SSR) with a 7 s 1920x1080 logo animation.
- Build: actions for render and progress; site name suffixed with Remotion's `VERSION`; dots scale in with springs
  (delays 0/4/8), connector fades in over frames 25..55.
- Copy: versioned site names. Avoid: `load-fonts.ts` never releases its delayRender on error.

### A.18 template-render-server
- Produces: an Express 5 API that queues renders of a HelloWorld composition and serves the MP4s.
- Build: 4.39 job queue; prebuilt bundle via `REMOTION_SERVE_URL` or bundling at startup; Dockerfile on
  `node:lts-bookworm` installs Chrome libraries, runs `npx remotion browser ensure` and `npx remotion bundle`.
- Copy: the queue, cancellation and Dockerfile as the default self-hosted setup.

### A.19 template-electron
- Produces: a desktop app (Electron 40, Forge 7.11, Vite) that renders a video locally with a save dialog, progress in
  the dock or taskbar, cancellation and "show in folder".
- Build: renderer process sandboxed (contextIsolation, no nodeIntegration, CSP, sender checks on IPC); main process
  calls `ensureBrowser`, `selectComposition` and `renderMedia` with `binariesDirectory` pointing at the unpacked
  compositor package for the current platform (musl vs glibc detected); optional bundled Chrome Headless Shell.
- Copy: the packaging rules (unpack `@remotion/compositor-*` from asar, keep compositor binaries out of lipo merges).

### A.20 template-recorder
- Produces: a recording app plus an automatic editor for talking-head videos with screen share, captions, b-roll,
  chapters, music, title cards, table of contents and platform-specific end cards (landscape 1920x1080 or square
  1080x1080, 30 fps).
- Build: 4.34 and 4.35; scenes configured through a zod discriminated union (`videoscene`, `title`, `endcard`,
  `tableofcontents`, `recorder`) with webcam position, offsets, music mode and b-rolls; a layout engine of plain
  rectangles; interpolated layout transitions with SFX; Studio tooling for captions and b-roll; `bun sub.ts` batch
  transcription; codemods create new projects in `Root.tsx`. `Config.setAskAIEnabled(false)`,
  `Config.setInteractivityEnabled(false)`.
- Copy: nearly everything; it is the most complete editing engine in the material. Brand intro idea: letters rotating
  in around an off-screen pivot with 1-frame stagger, triangle logo morphing into rounded squares via `edgeRoundness`.

## Appendix B. Example repo catalogue (`examples/*`)

Shared boilerplate in older repos: `.eslintrc` extending `@remotion`, prettier with tabs and single quotes,
`remotion.config.ts` with jpeg frames and overwrite, and a GitHub workflow that renders on `workflow_dispatch` with the
inputs written to `input-props.json` (the old ones still `apt install ffmpeg`, which Remotion no longer needs).

### B.1 apple-wow-tutorial (4.0.4; source of the remotion.dev "Apple Wow" course)
- Produces: 130 frames at 1920x1080: dots, hearts and stars burst radially behind a Memoji image sequence on a dark
  gradient (`#000021` to `#110024`).
- Build: composable wrappers Explosion, Move, Shrinking, Trail, Slowed (4.25); Memoji frames via
  `staticFile("frame" + pad(frame * 2, 3) + ".png")`.
- Copy: effects as nestable wrappers; slow motion by remapped `<Freeze>`. Minor: mapped Sequences lack keys.

### B.2 morph-text (4.0.120)
- Produces: a 900-frame "liquid" morph cycling through 7 words (Raleway 900, 80 px, `#0b84f3`).
- Build and copy: 4.11. Caveat: font loaded by CSS `@import` without delayRender.

### B.3 text-warping (4.0.120)
- Produces: warped-text stills and animations (wave, glitch blocks, travelling bulge, "So Good" cover, spring stretch)
  and a Promo Series of three 200-frame clips at 1080x1080.
- Build and copy: 4.12 (opentype.js paths plus `warpPath`, `getBoundingBox`, `translatePath` shadows).

### B.4 animated-captions (4.0.390; paid remotion.pro component, ideas only)
- Produces: three short-form caption styles at 1000x1000: coloured active word, scaling active word, and a pill that
  slides behind the active word.
- Build (ideas): pages from `createTikTokStyleCaptions` at 800 ms, each page a Sequence lasting until the next page,
  page-relative token timing, Montserrat behind a font gate, `fitText` capped at 80 px within 800 px, stroke width
  `fontSize / 7` with `paintOrder: "stroke fill"`, fractional-index highlight (4.4).
- Copy: the ideas only; the README forbids redistribution.

### B.5 3d-text (4.0.119)
- Produces: "Text in 3D": three words springing forward in z with a blue long-shadow extrusion, 1080x1080, 60 frames.
- Build and copy: 4.14. Today ThreeCanvas already handles delayRender and per-frame `advance()`, so the manual
  delayRender in the example is redundant.

### B.6 timing-functions (4.0.118; tutorial playground, 540x540)
- Produces: separate 540x540 demo compositions for linear easing, spring (`mass: 4.7`, `from: -150`, `to: 150`),
  time remapping and a camera approach.
- Copy: `remapSpeed` (4.23) and `scale = 1 / distance` (4.24).

### B.7 d3-example (4.0.177)
- Produces: a 60-frame 1280x720 horizontal bar chart of letter frequencies growing in.
- Build: d3 scales and axes appended once; bars joined each frame with width multiplied by a spring
  (`mass: 5, damping: 200`, starting at frame 10).
- Copy: 4.26 (d3 computes, Remotion drives).

### B.8 anime-example (4.0.298, animejs 4.0.2)
- Produces: a box sliding 270 px back and forth.
- Copy: `autoplay: false` + `seek(frame / fps * 1000)` for any imperative timeline library.

### B.9 gl-transitions (4.0.150)
- Produces: five 1920x1080 shader transitions between two photos (cube, polka-dot curtain, leaf, butterfly wave
  scrawler, zoom blur).
- Build and copy: 4.20 (uniform contract, oversized triangle, delayRender through init). Fix: progress formula,
  per-instance refs, `cancelRender` on failure.

### B.10 transitions-video (4.0.60; the @remotion/transitions launch video)
- Produces: a 28 s 1080x1080 kinetic music-video promo built only from transitions, with 2x2 and 3x3 mosaics, a text
  mask and a lottery of flipping tiles.
- Build: 20 to 25 frame shots, `springTiming({config: {damping: 200}, durationInFrames: 10})`, tiles inset at
  `scale: 0.8` with radius 50, flat palette (`#1B9CFC`, `#FC427B`, `#58B19F`, `#F97F51`), variable-font punches,
  custom presentations (cube, wheelspin, clock wipe, circle wipe) and `addSound`.
- Copy: 4.13 and 4.19. Caveats: unused and unloaded fonts, remote logo URL, a missing `i ===` in one condition.

### B.11 light-leak-example (4.0.150)
- Produces: two photos joined by an 80-frame light-leak transition.
- Build and copy: a custom presentation that overlays a light-leak video (`mixBlendMode: "screen"`,
  `playbackRate = 80 / presentationDuration`) and cuts at 36 % progress. Today: `lightLeak()` from
  `@remotion/effects/light-leak` (4.0.500) on canvas-based components.

### B.12 motion-blur-example (Remotion 3)
- Produces: a square flying up and rotating with a heavy motion trail.
- Build and copy: 4.22. Uses v3 config names; use `@remotion/motion-blur` now.

### B.13 three-particles (4.0.120)
- Produces: 10 s of 10,000 drifting dark particles around a light-blue point light.
- Build and copy: 4.17. Caveats: `useEffect` mutations, removed `*BufferGeometry` JSX names.

### B.14 remotion-three-gltf-example (4.0.120)
- Produces: the Suzanne GLB rotating on a gold background (its README describes a phone scene that the code no longer
  renders).
- Build: `useGLTF(url, true)` (Draco) inside a `Setup` with `ThreeCanvas shadows`, camera `(-5, 5, 5)` fov 75.
- Copy: suspense loaders are render-safe because ThreeCanvas's Suspense fallback holds a delayRender. Caveat: the
  model comes from a remote S3 URL.

### B.15 glb-example (4.0.119)
- Produces: a 3 s cassette-tape product turntable with studio light and a contact shadow.
- Build and copy: 4.15 (fixed-radius Stage).

### B.16 typewriter (4.0.119)
- Produces: 120 frames at 1280x720 typing one sentence with a black bar cursor.
- Build: `text.slice(0, Math.floor(frame / 3))`; cursor solid while typing, then blinks every 10 frames.
- Copy: the minimal baseline; prefer the smoother caret in 4.10.

### B.17 mapbox-example (4.0.409)
- Produces: a 50 s 1280x720 3D fly-along of a hiking route in the Alps.
- Build and copy: 4.18. The README's sample token is not reproduced here; use your own in `.env`.

### B.18 trailer (Remotion 3; the original launch trailer)
- Produces: a 97.8 s voice-over-driven 1920x1080 trailer plus a 315-frame teaser and one composition per scene.
- Build: absolute Sequences overlapping 8 to 10 frames, home-made push and fade transitions, the Remotion house style
  (white background, bold sans, gradient text via `background-clip`, damping-200 springs, 2 to 4 frame staggers,
  zoom-in logo triangles, a CPU grid, a fake terminal, a racing `GlowingStroke`, growing code lines).
- Copy: the motion language and CodeFrame (4.9). Obsolete: webpack asset imports, styled-components, old config names,
  muxing the voice-over with ffmpeg after render.

### B.19 trailer-2-0 (Remotion 3; the 2.0 launch trailer)
- Produces: voice-over length plus a 250-frame end card, with scenes on audio features (fake editor, volume curves,
  LED meter), a scrolling showcase, bento feature grids and live contributor avatars.
- Build: the Root awaits `getAudioDuration` under delayRender before registering compositions (today:
  `calculateMetadata`); `useAudioData` + `visualizeAudio` with the Sequence offset added; modulo scrolling; CSS cube.
- Copy: 4.7 and the 3-point scroll interpolation. Avoid: `HelloWorld.tsx` never continues its delayRender; the
  `SpeechSynthesisRecorder.ts` leftover; copyrighted outro music was removed for a reason.

### B.20 4-0-trailer (4.0.169; the Remotion 4.0 launch; unlicensed assets)
- Produces: a 1900-frame intro made of extruded SVG 3D scenes (triangles, a 3D terminal, a 3D timeline, a render
  button, flipping progress cards, a Studio mock), plus keynote overlays at 3840x2160 and 25 fps, social assets and a
  transparent in-frame logo.
- Build: a home-made SVG 3D engine (4.14), opentype.js text paths, `getWaveformPortion` bars, spectrum in dB,
  odometer wheels, `<Folder>` organisation, mixed 25 and 30 fps.
- Copy: scene ideas and the extrusion approach. Avoid: deep imports from `@remotion/paths/dist`, float durations
  without rounding, a font loader that never caches or handles errors, reusing the assets.

### B.21 github-unwrapped (4.0.240; the 2025 edition of githubunwrapped.com)
- Produces: a personalised 1080x1080 30 fps "year in review" video per GitHub user (opening take-off, top languages as
  planets, issues as a UFO shoot-out, stars flying at a cockpit, productivity wheels, contribution grid, landing),
  plus OG images, Instagram stories and promo videos.
- Build: data layer (GitHub GraphQL and REST, token rotation, Mongo cache), composition parameters computed by a pure
  shared function, `Main` as a Series with negative offsets and data-dependent scene lengths, music chosen by length,
  per-scene compositions with edge cases, Lambda across accounts and regions, stills in parallel, Vite website with a
  tuned Player (4.36).
- Copy: architecture (4.36), speed ramps (4.23), fly-throughs (4.24), path travel and orbits (4.31), slot wheels and
  seven-segment counters (4.30), sprite bursts (4.32), pre-rendered gradients, alpha flame video per browser,
  `showInTimeline={false}` for hundreds of Sequences.
- Caveats: `calculateMetadata` reading `defaultProps`, functions in `defaultProps`, `startFrom` names, font loader
  without error handling, remote avatars, a streak counter that misses a streak running to the last day, stale About
  text, licensed music.

### B.22 video-with-jump-cuts (4.0.212)
- Produces: one clip with three kept sections played back to back.
- Build and copy: 4.27.

### B.23 css-animation-play-state (4.0.120)
- Produces: a CSS keyframe scale animation made scrubbable.
- Copy: paused play state plus negative `animationDelay`; only for porting legacy CSS.

### B.24 tone-js-example (4.0.118)
- Produces: an 18 s holiday card that synthesises "Jingle Bells", shows the current note and flips into an end card
  at frame 440.
- Build and copy: 4.28. Add `perspective` to the flip parent (without it the flip reads as a squash).

### B.25 html-in-canvas (4.0.455)
- Produces: six 1080x1080 effect showcases (magnifying glass, CRT terminal, vintage film, glowing bar chart, store
  peel, article highlight) and six 1280x720 bonus experiments (chromatic aberration, glitch, sticker peel, burn
  dissolve, sale sticker, shine sticker).
- Build and copy: 4.21. Caveats: no `setChromiumOpenGlRenderer("angle")` in its config, an async texture load without
  holding the render, an unloaded font. The vendored agent skill is an older flat copy of the official best-practices
  skill with three known errors (trim units, VP8 vs VP9, an invisible character in the Mapbox style URL).

### B.26 template-prompt-to-motion-graphics-saas
- Identical to A.13 except `package.json` (Remotion `^4.0.0` ranges). Same lessons.

### B.27 shorts-customizer (4.0.48; a football club hackathon project)
- Produces: a 265-frame 720x1280 goal highlight (minute, "GOOOOOAL!!", scorer, new score) customised through a zod
  schema (player enum, season goal, minute 1..90, scores, opponent).
- Build: designed at 1080x1920 and scaled down; background texture and crowd in `soft-light`; score slam from scale
  10 with per-letter font-size waves; `Whirl` of 1000 light streaks at simplex-noise angles; player cut-out drawn
  twice (colour-dodge copy with drop shadow plus a 40 % normal copy); `SlidingText` reveals in overflow-hidden boxes;
  odometer score.
- Copy: sports-highlight vocabulary and design-at-1080 scaling. Avoid: internal `Internals.CompositionManager`, remote
  fonts and images, PWA leftovers in `public/`.

### B.28 library-starter (^4.0.46; Turborepo + pnpm)
- Produces: a publishable Remotion hook library (`useCurrentSecond()`) with a Studio testbed package.
- Copy: tsup `--format cjs,esm --dts`, `remotion` and react as peer dependencies.

### B.29 cloudflare-containers-demo (4.0.321)
- Produces: a Worker that forwards `POST /render` to a Durable-Object-backed container, stores the MP4 in R2 and returns
  its key.
- Build: 4.39 container recipe (`node:24-bookworm-slim`, Chrome libraries, `npx remotion browser ensure`,
  `npx remotion bundle`, `node --experimental-strip-types src/server.ts`), `sleepAfter: "10m"`, max 10 instances.
- Copy: the Dockerfile. Replace the sample account id and bucket names that ship with it; add progress and limits.

### B.30 gpu-scene (4.0.248)
- Produces: a 10 s 1280x720 GPU benchmark in four quadrants (video texture phone, distorted orb with contact shadow,
  stacked box shadows, heavy CSS blur).
- Build: `setChromiumOpenGlRenderer("angle-egl")`, `setChromeMode("chrome-for-testing")`, render script with
  `chromiumOptions: {enableMultiProcessOnLinux: true}`.
- Copy: use it to check whether a render host really uses the GPU.

## Appendix C. Technique index, motion language and prompt essentials

### C.1 Goal to technique

| Goal | Recipe | Best source |
|---|---|---|
| Word-highlight short-form captions | 4.2 | template-tiktok, animated-captions (ideas) |
| Transcript or karaoke captions, SRT export | 4.3 | template-audiogram, template-recorder |
| Gliding highlight behind words | 4.4 | animated-captions (ideas) |
| Waveform or spectrum for podcasts | 4.5 | template-audiogram |
| Music visualiser, beat flash | 4.6 | template-music-visualization |
| Meters, fake audio editors, waveform timelines | 4.7 | trailer-2-0, 4-0-trailer |
| Code walkthrough with morphing tokens | 4.8 | template-code-hike |
| Code lines growing in, typed terminal | 4.9 | trailer, html-in-canvas Crt |
| Typewriter, caret, carousel, highlighter | 4.10 | prompt-to-motion-graphics skills, typewriter |
| Morphing text | 4.11 | morph-text |
| Warped text | 4.12 | text-warping |
| Variable-font animation | 4.13 | transitions-video, github-unwrapped |
| 3D type and extruded vector worlds | 4.14 | 3d-text, 4-0-trailer |
| Product turntable | 4.15 | glb-example |
| Video on a 3D device | 4.16 | template-three |
| Particles | 4.17 | three-particles |
| Map fly-along | 4.18 | mapbox-example |
| Custom transitions, sound on cuts | 4.19 | transitions-video, light-leak-example |
| GL image transitions | 4.20 | gl-transitions |
| Shader effects on live content | 4.21 | html-in-canvas |
| Motion blur | 4.22 | motion-blur-example, `@remotion/motion-blur` |
| Speed ramps and slow motion | 4.23 | timing-functions, apple-wow-tutorial, github-unwrapped |
| Camera moves and fly-throughs | 4.24 | timing-functions, github-unwrapped, 4-0-trailer |
| Particle bursts | 4.25 | apple-wow-tutorial |
| anime.js, d3, legacy CSS | 4.26 | anime-example, d3-example, css-animation-play-state |
| Jump cuts | 4.27 | video-with-jump-cuts |
| Generated music | 4.28 | tone-js-example |
| Transparent overlays, alpha video | 4.29 | template-overlay, github-unwrapped |
| Counters, odometers, slot wheels | 4.30 | github-unwrapped, shorts-customizer, template-stargazer |
| Path travel, orbits, draw-on lines | 4.31 | github-unwrapped, next-app-tailwind, helloworld |
| Sprite bursts | 4.32 | github-unwrapped |
| Social formats and safe zones | 4.33 | shorts-customizer, github-unwrapped, prompt-to-motion-graphics |
| Talking-head auto edit | 4.34 | template-recorder |
| Music bed and SFX | 4.35 | template-recorder, github-unwrapped |
| Personalised video at scale | 4.36 | github-unwrapped |
| Prompt to narrated video | 4.37 | template-prompt-to-video |
| Prompt to motion graphics | 4.38 | template-prompt-to-motion-graphics |
| Render services | 4.39 | still, render-server, cloudflare, vercel, electron |
| Studio as editor | 4.40 | template-recorder, template-vibe-code |

### C.2 The trailers' motion language (trailer, trailer-2-0, 4-0-trailer, transitions-video, github-unwrapped)

- **Pace**: shots of 20 to 25 frames in music-driven promos, 2 to 8 s scenes in narrated trailers; cut points follow
  the voice-over or the beat; scenes overlap by 8 to 15 frames so the next move starts before the last one settles.
- **Entrances**: damping-200 springs almost everywhere; bouncier springs (damping 15 to 20, mass 2) only for accents
  such as name tags, end-card panels and logo pops; lists and grids staggered 2 to 4 frames per item (or by distance
  from the centre for grids).
- **Exits**: a second spring that starts 10 to 20 frames before the end, or a zoom-through (`1 / distance`) that also
  works as the transition into the next scene.
- **Type**: large bold sans on white (launch trailers) or dark gradients (github-unwrapped); gradient text via
  `background-clip: text` (blue `#4290f5 -> #42e9f5`, orange `#f5ad43 -> #fd764a`, magenta `#e01d67 -> #79367a`);
  per-letter font-size springs for emphasis words; variable-font weight and width punches on beats; text swaps on a
  beat inside a shot (`frame < 10 ? "" : "NA"`).
- **Product UI as motion graphics**: recreate the UI in React (terminal, editor timeline, Studio panels, cards,
  pricing columns) rather than screen-recording it, then animate its parts; bento grids of white rounded cards that
  slide in with staggered springs; a showcase column that scrolls fast, slows to read, then leaves (3-point interpolate).
- **Depth**: "inspect" push-outs (scale 3.7 to 1 with translate), CSS 3D cubes and wheels, SVG extrusions, parallax
  layers, glass panes with soft glow PNGs behind content.
- **Accents**: racing gradient strokes around panels, travelling border shines, light streaks, sprite bursts, noise
  shake on impacts, SFX (whoosh on cuts, "wham" on impacts, glockenspiel on hits, fireball on chapter numbers) at
  0.1 to 0.2 volume.
- **Endings**: end cards with three or four panels springing in 10 frames apart, call-to-action pills zooming in,
  music and video fading together over the last 100 frames.

### C.3 Prompt essentials for our own generators (paraphrased from the two AI templates)

For a model that writes **timeline JSON** (prompt-to-video style):
- Ask for structured output against a strict JSON schema derived from zod; forbid prose.
- Split generation into small calls: story, then segmentation with detailed visual descriptions, then assets.
- Keep all randomness in the planner and store it; the renderer must be deterministic.
- Derive caption timing from TTS character timestamps, not from estimated reading speed.

For a model that writes **Remotion code** (prompt-to-motion-graphics style):
- Fix the output shape: imports, one exported component, a 2 to 3 sentence comment, hooks, an UPPER_SNAKE_CASE
  constants block (colours, text, timing, layout) inside the component, derived values, JSX; code only, no questions.
- Fix the design defaults: full-frame layout with padding, sizes relative to the frame (`Math.max(min, width * pct)`),
  2 to 4 colours, background colour on the root from frame 0, Inter or another loaded font.
- Fix the motion defaults: springs for organic motion, clamped interpolates for linear progress, staggered
  entrances, Sequences instead of `frame >= n &&` conditions, no CSS animation.
- Whitelist imports and inject exactly those names at runtime; list reserved names that must not be shadowed.
- Inject topic guidance only when the request needs it (charts, typography, messaging, transitions, sequencing,
  spring physics, social, 3D) and include one complete example component per topic.
- For follow-ups prefer exact search-and-replace edits; require enough context for a unique match; tell the model
  when the user edited the code by hand; send compile and runtime errors back verbatim with an attempt counter.
- Validate intent first (is this a motion-graphics request) so obvious non-video requests fail fast.
