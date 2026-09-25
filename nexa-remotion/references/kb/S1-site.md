# S1-site: remotion.dev outside the docs

Elements (ready-made components with source), Prompt Showcase, Templates, blog, showcase, success stories, learn, experts and product pages.

- Agent: S1-site. Source: `mirror/site/**` (182 files). Coverage list: `kb/S1-site.coverage.txt`.
- Target runtime on this machine: Remotion 4.0.528, React 19. Every version below was checked against the `<AvailableFrom>` tags in `mirror/docs` (the monorepo snapshot in `repo/` is 4.0.529). Everything the Elements use exists on 4.0.528, with one unverified item (`type: 'text-content'` schema fields, see section 9).
- Paths in this file are relative to the `remotion-rd/` folder.

---

## 1. Scope and coverage

All 182 assigned files were read fully, one by one, and logged (182 lines, no duplicates, none missing when diffed against `assign-S1-site.txt`).

| Section | Files | What it contains |
|---|---|---|
| Elements | 56 | 41 Element pages with complete TSX source, 11 category index pages, overview, Element Guidelines, Contributing guide, Third-party libraries |
| Prompts | 30 | 25 prompt pages (prompt text, author, tool, model), 3 gallery pages with like counts, `show.md` (redirect stub), `submit.md` (submissions disabled) |
| Blog | 29 | 17 release posts (1.1 to 4.0), 9 feature or company posts, archive, 2 pagination pages |
| Experts | 23 | index plus 22 freelancer profiles |
| Templates | 21 | index plus 20 template pages |
| Success stories | 7 | index, archive, 5 stories |
| Learn | 3 | Apple fireworks tutorial (twice) and the archive |
| Showcase | 2 | `showcase.md` (empty), `showcase/add.md` (submission rules) |
| Product pages | 11 | home, about, automate (pricing), lambda, player, design, explore, contact, search, ai, ai-embed |

Limits and caveats:
- Empty or stub pages: `ai.md` (navigation only), `ai-embed.md` (title only), `showcase.md` (client-rendered, empty in the mirror, so no showcase entries could be read), `templates/editor-starter.md` (title only), `prompts/show.md` (redirect), `search.md` (search widget only).
- Duplicates: `blog.md` equals the Mediabunny post; `blog/page/2.md` equals the 3.0 post; `blog/page/3.md` equals the 1.4 post; `learn.md` and `learn/apple-wow.md` have byte-identical bodies; `success-stories.md` equals `a-million-dollars.md`.
- Blog and Learn code blocks are mangled by Twoslash hover text in the mirror (for example ``import Html5Video'>Html5Video``). I reconstructed the intended code. Old posts were partly retro-edited to current names (`<Html5Video>` instead of `<Video>`, `<AbsoluteFill from>` instead of `<Sequence from>`), while the prose still describes historic behaviour.
- Expert, template and prompt pages share a site header and footer; a script confirmed that nothing outside each page's unique block differs.
- Prompt pages hold only the prompt (no resulting code or video). Quality can be judged only from the text and the like count.
- Element metadata (`element-definitions.ts`: durations, dimensions, dependency lists, `installationMode`) is not in the mirror. I inferred the mode from the code: a component exported through `Interactive.withSchema()` is a component-owned sequence; the rest are wrapped.

---

## 2. Mental model

### 2.1 How remotion.dev positions Remotion in 2026
- Three interchangeable workflows (home page): agentic (a coding agent plus Remotion Agent Skills and Plugins), interactive (Studio drag and drop plus Elements, edits saved back to code) and programmatic (data, parameterization, batch rendering). "Code is always the source of truth": whatever the workflow, the TSX file is the master.
- Products: Player (embed a live, prop-driven video in React), Lambda (distributed rendering on AWS), Studio (can be deployed as a static site or a server), Editor Starter (paid editor boilerplate), Timeline (paid copy-paste timeline component), Recorder (webcam and screen production tool), Convert (browser video converter, now built on Mediabunny).
- Scale claims: more than 2M videos rendered per month, 60k GitHub stars, 5M+ installs per month, 300 to 400+ paying companies, about 1000 docs pages, 35 templates and examples.
- Licensing (home and automate pages): free for individuals and organisations of up to 3 people (all features, unlimited commercial use). A Company License is required from 4 people: "Remotion for Automators" costs $0.01 per render with a $100/month minimum (batch rendering, video apps, Player embeds; no seats needed) and "Remotion for Creators" costs $25/month per seat (manual video creation and motion design systems in Studio, explicitly including work done with AI agents). Enterprise starts at $500/month and includes Editor Starter. For agency work this matters: a company of 4+ people making client videos with agents in Studio needs Creator seats.

### 2.2 The frame-function model (blog, Learn, Elements)
- A video is a React tree rendered once per frame. `useCurrentFrame()` is the only clock, so every visual value must be a pure function of the frame number and props.
- Rendering opens several browser tabs; each frame can be produced in a different tab and components mount directly at the requested frame (since 2.4 a component never passes through frame 0 when a frame range is rendered). Consequences: no `Math.random()` (use `random(seed)`), no values accumulated in state across frames, no wall-clock time, no reliance on mount order.
- Timing primitives: `interpolate()`, `spring()`, `Easing`, and the layout-in-time components `<Sequence>`, `<Series>`, `<Loop>`, `<Freeze>`. Since 4.0.46x many visual components accept Sequence timing props directly (section 2.3).
- Anything asynchronous (fonts, images, map tiles, data) must block rendering with `delayRender()` and `continueRender()` (or the `useDelayRender()` hook) and block Player playback with `useBufferState().delayPlayback()`. A handle that is never released fails the render (hard failure since 1.5) with a stack trace of where it was created (2.1).

### 2.3 The interactive layer model used by every Element (2026 code style)
- `Interactive.Div`, `Interactive.Span`, `Interactive.Svg`, `Interactive.Path` and so on (4.0.475) render ordinary DOM or SVG, but are selectable, draggable and keyframable in Studio.
- Core visual components accept Sequence timing props: `AbsoluteFill` (4.0.501: `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`), `Img` (4.0.465), `CanvasImage`, `Solid`, `@remotion/media` `<Audio>` (`from` and `durationInFrames` since 4.0.445) and every `Interactive.*` element (plus `cropLeft`, `cropRight`, `cropTop`, `cropBottom` since 4.0.506). A stagger is therefore written as `<Interactive.Div from={8 + i * 6}>` or `<AbsoluteFill from={i * 3}>` instead of wrapping in `<Sequence>`. `premountFor` and `postmountFor` arrived on `Img` in 4.0.497 and on `CanvasImage` in 4.0.495, but on `AbsoluteFill`, `Solid`, `Interactive.*` and rough-notation components only in 4.0.528 (exactly our version).
- Studio-editable code style, identical across all 41 Elements: values stay inline; animation is written as hardcoded keyframe arrays `interpolate(frame, [k...], [v...], {easing: [...], extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`; transforms use the individual CSS properties `translate`, `scale`, `rotate`, `opacity` (string values such as `'0px 30px'`, `'10deg'`, `'y -10deg'` are interpolated directly) rather than `transform` strings or animated `top`/`left`.
- An Element is copied source, not an npm dependency. "Install one into your codebase and see it appear on your active Studio canvas", then remix it in Studio or with an agent. Two installation modes (guidelines):
  - `wrapped` (default): Studio wraps the component in a `<Sequence>` for placement and duration; its internal `Interactive.*` layers stay separately editable.
  - `component-owned-sequence`: the component is exported through `Interactive.withSchema()`, owns its `<Sequence layout="none">`, appears as one timeline layer, and exposes schema-driven Inspector controls. Used for generative effects, canvas content, audio visualizers, captions, maps.
- Effects: GPU effect factories imported per subpath from `@remotion/effects/<name>` are passed as an ordered array to `effects` on `<Solid>`, `<HtmlInCanvas>`, `<Img>` and `<CanvasImage>` (the Shine Element runs `scale()` then `shine()`).
- HTML-in-canvas (4.0.455) paints live DOM into a canvas for post-processing (shaders, glitch, CRT, lens). Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element` enabled; renders need no setup according to the guide. Check support with `HtmlInCanvas.isSupported()`.

### 2.4 Captions model
`Caption[]` JSON (`text`, `startMs`, `endMs`, `timestampMs`, `confidence`) goes through `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds})` (4.0.216), which returns `pages`, each with `text`, `startMs`, `durationMs` and `tokens` (`text`, `fromMs`, `toMs`). Render the page whose half-open interval `[startMs, startMs + durationMs)` contains the current time, and style the token whose `[fromMs, toMs)` contains it. `combineTokensWithinMilliseconds` of 800 gives short punchy pages for word-level styles; 2000 gives subtitle-like lines. Studio (4.0.521) imports caption JSON into a caption layer (select the layer, Captions inspector, Import).

### 2.5 Prompt-to-video model (Prompt Showcase)
The gallery collects videos "built using Remotion Skills and coding agents like Claude Code, Codex, or OpenCode". The best prompts trigger the skill ("use remotion best practices"), fix the canvas (size, fps, duration), describe a timeline, give numeric style tokens (hex colours, fonts, px, degrees), specify camera and easing, name assets and data sources, and then iterate with precise deltas. Appendix B has the full catalogue and a style guide.

---

## 3. API digest

In this material the APIs appear as usage inside Elements, template commands and the history told by the blog. Versions come from `mirror/docs`.

### 3.1 Interactive and Studio authoring (`remotion`)
- `Interactive.<Tag>` (4.0.475). HTML: A, Article, Aside, Button, Code, Div, Em, Footer, H1 to H6, Header, Label, Li, Main, Nav, Ol, P, Pre, Section, Small, Span, Strong, Ul. SVG: Circle, Ellipse, G, Line, Path, Rect, Svg, Text. Props: all native props plus `name`, Sequence timing props (`from`, `durationInFrames`, `showInTimeline`, `hidden`...) and `cropLeft`/`cropRight`/`cropTop`/`cropBottom` as 0 to 1 fractions (4.0.506). SVG elements expose `stroke`, `strokeWidth` and (if paintable) `fill` controls; on `Svg` and `G` these become inherited defaults.
- `Interactive.withSchema({Component, componentName, schema, supportsEffects})` (4.0.479) returns a Studio-editable component. `Component` is a `forwardRef` that receives the schema props plus `controls: SequenceControls | undefined`. Every Element passes `supportsEffects: false` and casts the result `as React.FC<Props>`.
- Schema spreads: `Interactive.baseSchema` (always first), `Interactive.transformSchema` (always last), `Interactive.captionsSchema` (4.0.500, adds the `captions` field), `Interactive.textSchema` (4.0.481; `style.fontFamily` 4.0.486). Also available: crop (4.0.500), background and border (4.0.497), borderRadius (4.0.501), svgPaint and svgStroke (4.0.499), premount, sequence.
- Field types seen in Elements:
  - `{type: 'asset', assetType: 'audio', default: url, description}` (`assetType` 4.0.521)
  - `{type: 'color', default: '#2563eb', description}`
  - `{type: 'number', min, max, step, default, description, hiddenFromList: false, keyframable: false}`
  - `{type: 'enum', default: 'instagram', variants: {instagram: {}, tiktok: {}}, keyframable: false}` (enum keyframes possible from 4.0.509 via hold keyframes)
  - `{type: 'array', item: {type: 'number', step: 0.0001}, default: [-0.1276, 51.5072], minLength: 2, maxLength: 2, newItemDefault: 0}`
  - `{type: 'hidden'}` for internal props such as `index`, `count`, `callerStyle`
  - `{type: 'text-content', default: 'London'}` for editable strings (used by 4 Elements: Rotating Cards, both maps, Spinning Text Wheel; not documented in the docs mirror)
- Types: `InteractiveBaseProps`, `InteractiveTransformProps`, `InteractivitySchema`, `SequenceControls`, `SequenceProps` (`Pick<SequenceProps, 'width' | 'height'>` for caption area size).
- Wiring rules for a component-owned sequence (Element Guidelines): spread `baseSchema`; pass `controls` unchanged to the `<Sequence>`; forward `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`; use `layout="none"` and pass `outlineRef` (4.0.479) to the box that should show the selection outline; forward `style` and the ref to that same box; set dimensions inside the component (metadata does not pass them); put every `useCurrentFrame()` call in a child component below the Sequence so the clock respects `from`, `trimBefore`, `playbackRate` and `freeze`.

Condensed shape of a component-owned Element (my rewrite of the audio Elements):
```tsx
const schema = {...Interactive.baseSchema, color: {type: 'color', default: '#2563eb', description: 'Color'}, ...Interactive.transformSchema} as const satisfies InteractivitySchema;
const Inner = forwardRef<HTMLDivElement, Props & {readonly controls: SequenceControls | undefined}>(
  ({controls, name, style, color = '#2563eb', ...sequenceProps}, ref) => {
    const outlineRef = useRef<HTMLDivElement>(null);
    useImperativeHandle(ref, () => outlineRef.current as HTMLDivElement, []);
    return (
      <Sequence layout="none" {...sequenceProps} controls={controls} name={name ?? 'My layer'} outlineRef={outlineRef}>
        <Content outlineRef={outlineRef} style={style} color={color} />{/* useCurrentFrame() lives in Content */}
      </Sequence>
    );
  });
export const MyLayer = Interactive.withSchema({Component: Inner, componentName: '<MyLayer>', schema, supportsEffects: false}) as React.FC<Props>;
```

### 3.2 `<Sequence>` props used by Elements
`layout="none"` (1.4, opts out of the absolute full-size wrapper), `controls` (4.0.501), `outlineRef` (4.0.479), `name`, `from` (optional since 3.3), `durationInFrames` (defaults to Infinity since 2.5), `trimBefore` (4.0.482 on Sequence), `playbackRate` (4.0.528 on Sequence), `freeze` (4.0.476), `hidden` (4.0.462), `showInTimeline`, `premountFor` (4.0.140), `style` and `ref` (3.3; `style` only without `layout="none"`).

### 3.3 `interpolate()` and `Easing` as used by Elements
- Multi-keyframe (2.0): `interpolate(frame, [0, 24, 104, 119], [0, 1, 1, 0], ...)` expresses enter, hold and exit in one call.
- Per-segment easing array (4.0.462): `easing: [inCurve, Easing.linear, outCurve]`, one entry per segment. A single function (or one-element array) applies to all segments.
- CSS value outputs (4.0.472): `['0px 30px', '0px 0px']`, `['-20deg', '-8deg']`, axis rotations `['y -10deg', 'y 5deg']`; transform-origin keywords (4.0.475); numeric tuples (4.0.473); discrete string steps (4.0.509); single-value ranges (4.0.469).
- `posterize: n` (4.0.470): hold each value for n frames, for stop-motion stepping, boiling hand-drawn lines and texture seeds.
- `output: 'perceptual-scale'` (4.0.490): makes the visible area change linearly after easing; Elements use it on most keyframed scale animations (containers, cards, buttons, the pie).
- `outputType` (4.0.526) exists but is not used by Elements.
- `Easing.spring({damping, mass, stiffness, overshootClamping, allowTail, durationRestThreshold})` (4.0.476; `allowTail` and `durationRestThreshold` 4.0.483) turns a spring into an easing curve, measured as if it lasted 30 frames and stretched to the segment. `allowTail: true` lets the settling tail continue past the segment end. `Easing.out(Easing.spring(...))` is used for exits.
- Curves that recur in Elements: `Easing.bezier(0.16, 1, 0.3, 1)` (expo-out style entrance, the most common), `Easing.bezier(0.65, 0, 0.35, 1)` (in-out for wipes and moves), `Easing.bezier(0.7, 0, 0.84, 0)` (ease-in for exits), `Easing.bezier(0.34, 1.56, 0.64, 1)` (overshoot pop), `Easing.bezier(0, 0, 0.58, 1)` (ease-out), `Easing.bezier(0.42, 0, 0.58, 1)` (ease-in-out), `Easing.bezier(0.4, 0, 1, 1)` (press in), `Easing.inOut(Easing.cubic)`, `Easing.inOut(Easing.quad)`, `Easing.inOut(Easing.sin)`, `Easing.out(Easing.cubic)`, `Easing.out(Easing.exp)`, `Easing.in(Easing.cubic)`.
- `spring({fps, frame, config: {damping, mass, stiffness}, durationInFrames, delay, durationRestThreshold})`: with `durationInFrames` (3.1) the curve is stretched to that exact length; `damping: 200` removes bounce. Spring outputs can be summed (Moving Pill captions) or remapped with `interpolate`. `measureSpring()` (2.1) returns a spring's natural length.

### 3.4 Visual primitives
- `<Solid color width height effects>` (4.0.464): a solid-colour layer that effects draw on (all background Elements).
- `@remotion/effects/<name>` factories used by Elements (option names as used):
  - `waves` (4.0.471): `colors`, `direction`, `thickness`, `gap`, `angle`, `offset`, `amplitude`, `wavelength`, `phase` (and `maskToSourceAlpha` 4.0.474)
  - `zigzag` (4.0.471): same as waves without `phase`
  - `liquidContours` (4.0.491): `firstColor`, `secondColor`, `phase`
  - `paper` (4.0.486): `amount`, `colorFront`, `colorBack`, `contrast`, `roughness`, `fiber`, `crumples`, `folds`, `seed`, `scale`, `drops`
  - `gridlines` (4.0.476): `gridSize`, `lineWidth`, `lineColor`
  - `starburst` (4.0.500): `rays`, `colors`, `rotation`, `origin: [x, y]` in 0 to 1
  - `shine` (4.0.468): `progress`, `angle`, `haloSigma`, `coreSigma`, `haloIntensity`, `coreIntensity`
  - `tear` (4.0.523): `jaggedness`, `progress`, `rotation`
  - `scale` (4.0.466): `scale`
  - The docs list about 70 more (blur, glow, halftone, chromatic aberration, light leak, LUT, vignette, scanlines, pixelate, noise, duotone, tv-signal-off...); see the effects agent's file.
- `<HtmlInCanvas width height name effects onPaint>` (4.0.455) and `<CanvasImage src width height fit name showInTimeline style>` (4.0.466; `fit` is `'cover'` or `'contain'`; `crossOrigin` 4.0.526).
- `<Img src name showInTimeline pauseWhenLoading style>` (Sequence props 4.0.465, `pauseWhenLoading` 4.0.111, `effects` 4.0.469, `onImageError` and `crossOrigin` 4.0.526).
- `@remotion/shapes` `makeCallout({width, height, pointerLength, pointerBaseWidth, pointerPosition, pointerDirection, cornerRadius})` returns `{path, width, height, transformOrigin}`.
- `@remotion/rough-notation` (4.0.490, install with `npx remotion add @remotion/rough-notation`): `<Highlight>`, `<Circle>`, `<StrikeThrough>`, `<CrossedOff>`, `<Box>`, `<Bracket>`, `<Underline>` wrap inline children. Props seen: `progress` (0 to 1), `seed`, `roughness`, `strokeWidth`, `color`, `padding: {left, right, top, bottom}`, `box: 'inside'`, `iterations`, `maxRandomnessOffset`, `bowing`, `name`.
- `@remotion/rounded-text-box` (4.0.360) `createRoundedTextBox({textMeasurements, textAlign, horizontalPadding, borderRadius})` returns `{d, boundingBox: {width, height, viewBox}}`: one SVG path that hugs multi-line text with rounded corners.

### 3.5 Text and fonts
- `@remotion/google-fonts/<Family>`: `const {fontFamily, waitUntilDone} = loadFont('normal', {weights: ['700'], subsets: ['latin']})`. Modules also export `fontFamily` directly. Families used by Elements: Inter, Montserrat, Figtree, Lora, Caveat, CormorantGaramond, MonaSans. Loading only the needed weights and subsets keeps loads small.
- `@remotion/layout-utils`: `fitText({text, withinWidth, fontFamily, fontWeight, validateFontIsLoaded})` (4.0.88) returns `{fontSize}`; `fitTextOnNLines({text, maxLines, maxBoxWidth, maxFontSize, fontFamily, fontWeight, validateFontIsLoaded})` (4.0.313) returns `{fontSize, lines}`; `measureText({text, fontFamily, fontSize, fontWeight, additionalStyles, validateFontIsLoaded})` returns `{width, height}`. `validateFontIsLoaded` exists since 4.0.136 (default true only from 5.0, which is unreleased).

### 3.6 Audio
- `@remotion/media` `<Audio src showInTimeline from durationInFrames trimBefore volume name>`: Sequence-style timing directly on the tag.
- `@remotion/sfx` (4.0.429) exports hosted sound-effect URLs: `mouseClick`, `ding`, `whoosh`, `whip`, `pageTurn`, `shutterModern`, `shutterOld`, `recordScratch`, `uiSwitch`, `vineBoom`, `snapchatNotification`, `windowsXpError`, `yippee` and meme sounds (bruh, fah, animeWow, wilhelmScream, and more). The Subscribe Nudge uses `mouseClick` and `ding`.
- `@remotion/media-utils`: `useWindowedAudioData({src, frame, fps, windowInSeconds})` (4.0.240) returns `{audioData, dataOffsetInSeconds}` and only decodes a window around the frame; `visualizeAudio({audioData, dataOffsetInSeconds, fps, frame, numberOfSamples, optimizeFor: 'speed'})` (`dataOffsetInSeconds` 4.0.268, `optimizeFor` 4.0.83) returns frequency magnitudes from low to high, 0 to 1; `getWaveformPortion({audioData, dataOffsetInSeconds, startTimeInSeconds, durationInSeconds, numberOfSamples, channel, normalize, outputRange: 'minus-one-to-one'})` (`normalize` 4.0.280) returns `{index, amplitude}[]`; `createSmoothSvgPath({points})` returns a smooth SVG path.

### 3.7 Captions
`createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds, breakOnSilenceAfterMilliseconds})` (4.0.216; last option 4.0.514) returns `{pages}`; types `Caption`, `TikTokPage`, `TikTokToken` from `@remotion/captions`.

### 3.8 Async and lifecycle
`useDelayRender()` (4.0.342) returns `{delayRender, continueRender}`; `useBufferState()` (4.0.111) returns `{delayPlayback}`, whose result has `unblock()`; `cancelRender(error)` aborts the render with a real error (Elements call it when a font fails to load).

### 3.9 Template CLI
`npx create-video@latest --<template>` (also `bun create video --<template>` and `pnpm create video --<template>`); `--yes` skips questions (`npx create-video@latest --yes --blank my-video` appears in a prompt); `--tailwind` since 3.1. Template flags are listed in Appendix C.

### 3.10 Historic APIs from the blog and their names today
| Introduced | API or behaviour | Today (4.0.528) |
|---|---|---|
| 1.1 | `remotion.config.ts`, `overrideWebpackConfig()` reducer | still the pattern; config can import files (3.0) |
| 1.1 | `<Img>`, `<IFrame>` wait for load; ESLint warns on native tags | still; prefer `Img` and `CanvasImage` |
| 1.2 | JPEG frames by default (2x faster than PNG) | PNG only when alpha is needed |
| 1.4 | `random(seed)`; ESLint rule against `Math.random()` | still mandatory |
| 1.4 | `<Sequence layout="none">` | still |
| 1.4 | H.265, WebM VP8/VP9, transparent video with `yuva420p` | see encoding and transparent-videos docs |
| 2.0 | audio support; `@remotion/media-utils` (`getAudioData`, `visualizeAudio`, `useAudioData`, `getAudioDuration`, `getVideoMetadata`, `getWaveformPortion`) | `useWindowedAudioData` preferred for long files |
| 2.0 | `startFrom` and `endAt` on Video and Audio | renamed `trimBefore` and `trimAfter` in 4.0.319 |
| 2.0 | `<Video>` and `<Audio>` from `remotion` | now `<Html5Video>` and `<Html5Audio>`; new code should use `<Video>` and `<Audio>` from `@remotion/media` |
| 2.0 | `--frames=0-9` or `--frames=50`, `@remotion/gif`, esbuild loader, Webpack cache | still |
| 2.1 | `interpolateColors()`, `measureSpring()`, first `@remotion/player` release (alpha; stable in 2.6) | still |
| 2.2 | `<Freeze>`, `playbackRate` on media, `.env` support, `@remotion/three`, ProRes and MKV, fonts awaited with `document.fonts.ready` | still |
| 2.3 | `<Still>`, `npx remotion still`, `renderStill()` | still (WebP and PDF stills since 4.0) |
| 2.3.2 and 2.5 | `<Series>`, `<Loop>`, In/Out markers, J K L shortcuts | still |
| 2.6 | `public/` folder and `staticFile()`; data URLs as media sources; `audioBufferToDataUrl()` | still |
| 3.0 | Lambda, `renderMedia()`, `openBrowser()`, parallel render and encode | still |
| 3.1 | `--codec=gif`, `--every-nth-frame`, `--number-of-gif-loops`; Tailwind; `spring({durationInFrames})`; `<OffthreadVideo>`; `@remotion/preload` | still (`@remotion/media` Video is the newest recommendation) |
| 3.2 | `@remotion/lottie`, `@remotion/skia`, `--muted`, `--enforce-audio-track`, default output `out/{id}.{ext}` | still |
| 3.3 | FFmpeg auto-install, `ensureFfmpeg()` | obsolete: FFmpeg is baked in since 4.0 |
| 3.3 | `@remotion/google-fonts`, `@remotion/motion-blur` (`<Trail>`, `<CameraMotionBlur>`), `@remotion/noise`, `@remotion/paths`, `<Thumbnail>`, `prefetch()`, `frameupdate`, `inFrame`/`outFrame`, negative still frames, `--height`/`--width`, `onSlowestFrames`, `npx remotion benchmark`, `src/Root.tsx` naming | still |
| 4.0 | Studio (renamed from Preview), Zod schema props editing and saving, Render button, Rust binary, `calculateMetadata()`, `@remotion/rive`, `@remotion/shapes`, `@remotion/tailwind`, `getStaticFiles()`, `cancelRender()` | still |
| 4.0.130 | seamless AAC chunk concatenation on Lambda | automatic |
| 2024 | `npx remotion bundle` deploys Studio as a static site; every render API accepts a URL as `serveUrl` | still |
| 2025 | Media Parser and `@remotion/webcodecs` | deprecated since 1 February 2026 in favour of Mediabunny |

---

## 4. Recipes

Each recipe comes from an Element, a template, the Learn tutorial or a prompt. Frame numbers assume 30 fps.

**R1. Overlay life cycle in one call (enter, hold, exit).** Share one keyframe array and one easing array across properties (Subscribe Nudge):
```tsx
const t = [0, 24, 104, 119];
const easing = [Easing.bezier(0.65, 0, 0.35, 1), Easing.linear, Easing.bezier(0.7, 0, 0.84, 0)];
const o = {easing, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const style = {
  opacity: interpolate(frame, t, [0, 1, 1, 0], o),
  translate: interpolate(frame, t, ['0px 14px', '0px 0px', '0px 0px', '0px 20px'], o),
  scale: interpolate(frame, t, [0.98, 1, 1, 0.97], {...o, output: 'perceptual-scale'}),
};
```

**R2. Wipe a bar or a line of text in and out.** `<Interactive.Div cropRight={interpolate(frame, [0, 20, 96, 116], [1, 0, 0, 1], {easing: [inOut, Easing.linear, inOut]})}>` with `inOut = Easing.bezier(0.65, 0, 0.35, 1)`. Stack a second bar 4 frames later on the way in and 4 frames earlier on the way out (last in, first out). Name Lower Third and Location Lower Third use this; Location swaps the in and out curves for `Easing.spring({damping: 200, allowTail: true, durationRestThreshold: 0.02})`.

**R3. Mask slide-up label.** Wrap the label in a box with `overflow: 'hidden'` and animate the inner `` translate: `0 ${(1 - p) * 100}%` ``. Switch the wrapper to `overflow: 'visible'` once the move is done so shadows and descenders are not clipped (Vertical Bar Chart: `overflow: frame < end ? 'hidden' : 'visible'`). Keep the text `visibility: 'hidden'` until its start frame.

**R4. Draw any path without measuring it.** `pathLength={1}`, `strokeDasharray={1}` (or `"1 1"`), `strokeDashoffset={1 - progress}`. Used for the chart trend line, map routes and the map pin outline. For a route with a casing, draw the same path twice: white at `width + 24` underneath, colour on top (Watercolor Map).

**R5. Staggered pop of data points.** `r = interpolate(frame, [14 + i * 7, 22 + i * 7], [0, 11], {easing: Easing.bezier(0.34, 1.56, 0.64, 1), ...clamp})` gives an overshoot pop per point (Line Chart).

**R6. Counting number.** `Math.round(interpolate(frame, [0, 90], [0, 1], {easing: Easing.out(Easing.exp), ...clamp}) * 24813).toLocaleString('en-US')` with `fontVariantNumeric: 'tabular-nums'` so digits do not jitter (Number Counter).

**R7. Pie reveal.** Sweep a global `revealAngle` from 0 to 360 over frames 8 to 60 (`Easing.inOut(Easing.cubic)`); draw each slice from its start angle to `min(endAngle, revealAngle)` with an SVG arc (`largeArcFlag = end - start > 180 ? 1 : 0`, angles offset by -90 degrees so 0 is 12 o'clock).

**R8. Bars that feel physical.** Vertical bars grow with `easing: [Easing.spring({damping: 14.5, mass: 0.8, stiffness: 100})]` over `16 + round(value / max * 8)` frames (taller bars take slightly longer), stagger 24 frames; the value label rises out of a mask ending 2 frames after the bar; force progress to exactly 1 after the end frame (`frame >= end ? 1 : interpolate(...)`) so the spring tail never leaves a bar at 0.998. Horizontal bars reveal with `cropRight` and ease-out, stagger 6 frames via `from`. Highlight one bar in the accent colour and keep the others grey; label values directly on the bars instead of using legends.

**R9. Caption timing that survives trimming and speed changes.** Inside the Sequence: `currentTimeMs = ((trimBefore + (frame - trimBefore) * playbackRate) / fps) * 1000`. Build pages once with `useMemo(() => createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds}).pages, [...])`, pick the active page with a half-open interval, and key the page component by page index and start so per-page state resets. Keep leading and trailing whitespace of each token outside the styled `inline-block` span so spacing stays natural.

**R10. Legible bold captions.** White Montserrat 700, `` WebkitTextStroke: `${fontSize / 7}px #000` ``, `paintOrder: 'stroke fill'` (stroke sits behind the fill), `lineHeight: 1.5`, font size = min(80, fit of the whole page, fit of every single word) via `fitText` with `validateFontIsLoaded: true`. Render nothing until `waitUntilDone()` resolved; call `cancelRender(error)` if it rejects.

**R11. Moving pill highlight between words.** Measure every token span after layout (`useLayoutEffect`, `offsetLeft`, `offsetTop`, `offsetWidth`, `offsetHeight`, plus a `ResizeObserver`). Compute a fractional word index as a sum of springs: for each token after the first add `spring({frame: pageLocalFrame, fps, config: {damping: 100}, durationInFrames: 5, delay: tokenStartFrame - 2.5})`. Interpolate the pill's left, top and width across the measured layouts at that fractional index. The pill glides between words instead of jumping.

**R12. Word pop and word highlight.** Popping Word: the active word gets `color: '#2563eb'` and `scale: 1 + min(enter, exit) * 0.03` with `transformOrigin: 'center bottom'`, where `enter` is a damping-200 spring over `min(4, tokenFrames / 2)` frames and `exit` a linear ramp over the same length at the token end; fit the font with the width divided by 1.03 so the scaled word never overflows. Word Highlight: only the colour changes.

**R13. Rounded multi-line caption box.** `fitTextOnNLines` (max 2 lines, max 64 px, limited by `height / (lines * 1.5)`), `measureText` per line with `additionalStyles: {lineHeight: 1.5}`, then `createRoundedTextBox({textMeasurements, textAlign: 'center', horizontalPadding: 22, borderRadius: 20})`; render the path in an SVG behind absolutely positioned lines (Rounded Captions, Figtree 700, white box, black text).

**R14. Audio visualizers.**
- Spectrum: `useWindowedAudioData({src, frame, fps, windowInSeconds: 10})`, `visualizeAudio({..., numberOfSamples: 256, optimizeFor: 'speed'})`, keep the first `ceil(bars / 2)` bins, mirror them (reverse plus original), bar height `clamp(4, 300, 300 * sqrt(v) * sensitivity)`. The square root lifts quiet bins.
- Oscilloscope: `getWaveformPortion` over a 0.35 s window centred on the current time (`startTimeInSeconds: t - window / 2`), 64 samples, `normalize: false`, `outputRange: 'minus-one-to-one'`, turned into a curve with `createSmoothSvgPath`.
- Static voice note with progress: read the whole clip once (`frame: 0`, `windowInSeconds: duration`), bars from `getWaveformPortion` inside `useMemo`, colour played versus unplayed with one SVG `linearGradient` whose two middle stops sit at `progress * 100%` (a hard edge).
- "React to the bass only" (Music CD prompt): use only the lowest bins of `visualizeAudio` for scale or glow.
- Always mount the `<Audio>` (with `showInTimeline={false}`) inside the visualizer so sound and picture share the clock.

**R15. Seamless moving pattern background.** `<Solid color width height effects={[waves({colors: [a, b], direction: 'horizontal', thickness: 56, gap: 0, angle: 0, amplitude: 24, wavelength: 160, phase: 0, offset: (frame / durationInFrames) * 448})]} />`. The offset reached at the last frame is a whole multiple of the pattern period (448 = 4 x 56 x 2 colours; the zigzag Element uses thickness 40 and 480 = 6 x 40 x 2), which is how the loop stays seamless (my reading of the numbers).

**R16. Boiling textures and hand-drawn lines.** `interpolate(frame, [0, 120], [0, 1000], {posterize: 30})` as the `paper()` seed changes the paper grain every 30 frames (Paper Texture). `posterize: 4` on both `progress` and `seed` of a rough-notation `<Circle>` gives a 7.5 fps hand-drawn look with a jittering outline (Circle Marker).

**R17. Multi-word highlighter.** Split a phrase into one `<Highlight>` per word, each with its own `seed`; drive them from one phrase progress, word i covering `[i / n, (i + 1) / n]`. Start phrases 29 frames apart, 24 frames each, spring-eased (News Article Highlight). Yellow `rgba(255, 224, 76, 0.62)` with `bowing: 0` reads like a real marker; the highlight sits behind the text.

**R18. Shine sweep or tear on any content.** `<HtmlInCanvas width={1280} height={720} effects={[scale({scale: 0.75}), shine({progress, angle: 30, haloSigma: 200, coreSigma: 65, haloIntensity: 0.3, coreIntensity: 0.4})]}>` with children such as `<CanvasImage fit="cover" ...>`; progress 0 to 1 over 44 frames. The tear uses `tear({jaggedness: 24, progress, rotation})` over frames 15 to 25 with a damping-200 spring easing.

**R19. Picture-in-picture from full screen.** On the foreground scene animate over the same 35 frames with one damping-200 spring easing: `cropLeft` and `cropRight` 0 to 0.302, `cropTop` and `cropBottom` 0 to 0.06, `scale` 1 to 0.38 with `transformOrigin: 'top left'`, `translate` to `'1363px 23px'`, `borderRadius` 0 to 48. Cropping (instead of shrinking the content) keeps the subject framed as the box shrinks.

**R20. Slide into a 60/40 split screen and back.** One `splitProgress = interpolate(frame, [20, 52, 98, 130], [0, 1, 1, 0], {easing: [Easing.bezier(0.65, 0, 0.35, 1), Easing.linear, Easing.bezier(0.65, 0, 0.35, 1)]})`. Scene A sits in a wrapper whose `width` shrinks from full to 60% minus the divider (`overflow: 'hidden'`), and its content shifts left by `aShift * progress` so it stays centred in the narrower panel. Scene B plus a 15 px white divider slides in from the right.

**R21. Rotating card carousel.** A scroll position runs from 0 to `count - 1` between frames 24 and `duration - 28`, eased per step only in the middle 64% of each step (`[0.18, 0.82]` with `Easing.inOut(Easing.cubic)`) so each card rests before moving. Each card's slot is `index - scroll`, wrapped to `[-count/2, count/2)`; x = slot x 270 px, rotate = slot x 5.5 deg, scale from 1.02 at the centre to 0.84, fade out beyond distance 1.02 to 1.18, `zIndex = 100 - round(distance * 20)`.

**R22. Chat bubbles.** iMessage colours `#e5e5ea` (them, black text, left) and `#248bf5` (me, white text, right), radius 37, 40 px Inter, max width 75%. Tails are `::after` pseudo-elements (32 x 32) shaped with CSS `clip-path: path(...)` inside an inline `<style>`. Reveal each bubble in 8 frames (opacity plus 32 px rise, `Easing.bezier(0.16, 1, 0.3, 1)`), 25 frames apart.

**R23. Polaroid montage.** Cards (off-white `#fffdfa`, 22 px frame, bigger bottom margin, layered shadows plus a 1 px inset border, a translucent tape strip `#d9c58f` at 0.68 opacity) fly in from off screen with rotation (for example `'-620px 260px'` and -20 deg to 0 and -8 deg) over 26 frames, 12 frames apart, with `[expo-out, spring hold, expo-out]` easing arrays. The whole group pushes in slowly during the hold (scale 1 to 1.035 perceptual, 18 px lift), then each card flies out in a different direction while scaling up. Handwritten captions in Caveat 600.

**R24. Lower thirds.** Name bar (accent `#2563eb`) over title bar (`#18181b`), white 34 px bold, 66 px tall, crop wipes. Location: a map pin that draws its outline (dash offset), fills (fill-opacity), grows an inner dot, drops 10 px and scales 0.88 to 1, then the place name wipes in; everything reverses on exit; about 120 frames. Use `dir="auto"` and `textOverflow: 'ellipsis'` for international names.

**R25. Button micro-interaction with sound (YouTube Subscribe Nudge).** Cursor glides in (frames 40 to 60, expo-out), press scale 1 to 0.94 in 3 frames with `Easing.bezier(0.4, 0, 1, 1)`, release with a bouncy `Easing.spring({damping: 9, mass: 0.45, stiffness: 180})`, swap Subscribe (`#ff1744`) to Subscribed (`#2a2b31` plus checkmark) in one frame (63 to 64), press the bell at frames 78 to 81 (scale 1 to 0.9, then a spring with damping 7 back to 1 by frame 93) and its background lightens, then ring it with rotation keyframes 0, -18, 16, -11, 7, 0 deg every 4 frames around `transformOrigin: '50% 20%'` and swap the outline icon for the filled one. Sync SFX on the same frames: `<Audio from={61} durationInFrames={12} trimBefore={3} volume={0.5} src={mouseClick} />` and `<Audio from={81} durationInFrames={39} trimBefore={4} volume={0.24} src={ding} />` (trimBefore removes each sample's silent lead-in).

**R26. Card with a living 3D sway.** Parent `perspective: 1500`; the card slides up 760 px with a bouncy spring easing (damping 14, mass 0.8, stiffness 110, `allowTail`), sways with `rotate: interpolate(frame, [0, 90, 180, 270], ['y -10deg', 'y 5deg', 'y -5deg', 'y 5deg'], {easing: Easing.inOut(Easing.sin)})`, and exits down with `Easing.out(Easing.spring(...))` (YouTube Comment Highlight).

**R27. Maps.**
- Watercolor Map (no map library): project longitude and latitude to Web Mercator pixels yourself (`x = (lng + 180) / 360 * 256 * 2^z`, clamp latitude to 85.05112), pick the zoom where the route spans about 7.5 tiles (1920 / 256), move the camera centre from origin to destination with `interpolate`, lay out 256 px `<Img pauseWhenLoading>` tiles (drawn 257 px to hide seams) for the visible viewport, and draw a quadratic curve route raised by `min(400, 0.37 * height, 0.35 * distance)`. Tiles: Cooper Hewitt watercolor tiles (Stamen Watercolor, CC BY 3.0, data OSM CC BY-SA); keep the attribution.
- A-to-B Map Flyover (MapLibre plus Turf): render the map once as a large "plate" (up to 4096 px on the long side, zoom chosen to fit the whole great-circle route with detail margin) and move the camera by CSS-translating the plate so the current route point stays centred. Never move the MapLibre camera per frame. Details in Appendix A and section 5.

**R28. Spinning word wheel (slot-machine selection).** Items sit on a drum of radius 100 px: `translateZ(cos(a) * 100px) translateY(sin(a) * 100px) rotateX(a)` with the text counter-rotated and `backfaceVisibility: 'hidden'`. A heavy spring (mass 10, damping 200, stiffness 200, `durationInFrames: 90`, `durationRestThreshold: 0.0001`) turns the drum through one revolution and lands on item 0; a vertical `maskImage` gradient fades the top and bottom; the selected item's opacity rises from 0.28 to 1 during the last 12% of the spring.

**R29. Wiggle for attention.** Rotate keyframes `[0, 7, 14, 20, 26]` to `['0deg', '10deg', '-7deg', '3deg', '0deg']` with `Easing.inOut(Easing.quad)` and `transformOrigin: '50% 100%'` (pivot at the callout pointer) (Wiggling Callout, shape from `makeCallout`).

**R30. Particle burst by composition (Learn: Apple fireworks).** Small single-purpose wrappers composed from the inside out: `<Dot>` (a 14 px circle), `<Shrinking>` (scale 1 to 0 at frames 60 to 90), `<Move>` (spring with damping 200 and `durationInFrames: 120` mapped to -400 px of `translate`, with a `delay`), `<Trail amount>` (copies delayed by `from={i * 3}` and scaled `1 - i / amount`), `<Explosion>` (10 copies rotated by `i / 10 * 2 * PI rad`). Hearts and stars reuse the same wrappers with different radii, delays and a 0.3 rad offset. Order of wrappers matters: scale, then move, then delay.

**R31. Speed ramp for a subtree.** Accumulate per-frame speed and freeze children at the remapped frame:
```tsx
const remap = (frame: number, speed: (f: number) => number) => {
  let passed = 0;
  for (let i = 0; i <= frame; i++) passed += speed(i);
  return passed;
};
const Slowed: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const f = remap(frame, (i) => interpolate(i, [0, 20, 21], [1.5, 1.5, 0.5], {extrapolateRight: 'clamp'}));
  return <Freeze frame={f}>{children}</Freeze>;
};
```
The loop is O(frame) per frame; for long clips precompute a cumulative table or use a closed form.

**R32. Image-sequence playback (transparent character, Learn).** Export a ProRes 4444 clip with alpha (macOS: Encode Selected Video Files, Apple ProRes, Preserve Transparency), convert with `ffmpeg -i animoji.mov -pix_fmt rgba -start_number 0 frame%03d.png` into `public/`, then show `` staticFile(`frame${String(frame * 2).padStart(3, '0')}.png`) `` in `<Img>` (frame x 2 plays 60 fps frames in a 30 fps comp).

**R33. Typewriter title cards and screen-recording zoom (Cursor prompt).** 1 character per frame, hold 3 s after each card, line 1 then line 2; recording full screen and top-aligned for 2 s, then one continuous eased zoom of about 125% towards the top-left; reuse an existing end-card MP4.

**R34. Transparent overlay for editors.** Render as ProRes with alpha (the Transparent CTA prompt asks for "a transparent prores video"; the 3D logo prompt's first attempt failed until the agent followed the transparent-videos docs). Background must stay transparent (no full-frame fills), frames must be PNG, and the codec must keep alpha (ProRes 4444 in `.mov`, or VP8/VP9 WebM with `yuva420p` as introduced in 1.4). Template `--overlay` exists for this.

**R35. Social safe zones check.** Drop the Social Safe Zones Element (1080 x 1920, `platform: 'instagram' | 'tiktok'`) on top while designing a vertical video, then hide or delete it before the final render. Its first layer, named "Background", is sample artwork that covers the frame: delete it or you will hide your own content.

---

## 5. Performance and render stability

- **Parallel tabs, no shared state.** Random values in `useState(() => Math.random())` differ per tab and flicker between frames; use `` random(`x-${i}`) `` (1.4). Components mount directly at their frame (2.4), so nothing may depend on having run earlier frames. The Solar System prompt asks for deterministic stars via `Math.sin(i * 127.1 + 42)`; Remotion's `random(seed)` is the idiomatic equivalent.
- **Wait for assets.** `<Img>` and `<IFrame>` block the frame until loaded (1.1); fonts are awaited through `document.fonts.ready` (2.2) and `@remotion/google-fonts` `loadFont()`; map tiles use `<Img pauseWhenLoading>` (the Player pauses while they load). Never measure text before `waitUntilDone()` resolved; `validateFontIsLoaded: true` turns a silent fallback-font measurement into an error.
- **Third-party renderers (MapLibre pattern).** Create the handle once (`const [handle] = useState(() => delayRender('Loading MapLibre flyover'))`), create the map with `interactive: false`, `fadeDuration: 0`, raster `'raster-fade-duration': 0`, `pixelRatio: 1`, `attributionControl: false` and `canvasContextAttributes: {preserveDrawingBuffer: true}`, wait for `'load'`, `jumpTo()` the final view, then release the handle on the first `'idle'` event after `triggerRepaint()`. Any later reframe takes a new handle and waits for `'idle'` again. In the Player, return `delayPlayback().unblock` from a `useLayoutEffect` until the map exists. Keep the per-frame work to a CSS transform of the pre-rendered plate.
- **Webpack and workers.** MapLibre's worker URL gets rewritten by Webpack; the Element sets `` maplibregl.setWorkerUrl(URL.createObjectURL(new Blob([`import "https://unpkg.com/maplibre-gl@${maplibregl.getVersion()}/dist/maplibre-gl-worker.mjs";`], {type: 'text/javascript'}))) ``. This makes the render depend on unpkg being reachable.
- **Heavy computations in `useMemo`.** Caption pagination, `fitText`, waveform extraction and map projections are memoised on their inputs; a `key` that includes the source (`` key={`${audioSrc}-${durationInFrames}`} ``) resets state when the input changes.
- **Audio data windows.** `useWindowedAudioData` with a 10 s window decodes only what is needed around the current frame; loading a whole song for every frame is the slow alternative. The static waveform reads the full clip once at frame 0 instead.
- **Frame format.** JPEG frames render about twice as fast as PNG (1.2); use PNG only for alpha.
- **Encoding pipeline.** Rendering and encoding overlap since 3.0 (10 to 15% faster); parallel encoding switches off on low memory (`disallowParallelEncoding` forces it off). Video without audio skips the silent track (faster; `--enforce-audio-track` restores it); audio-only renders do not seek video; `--muted` drops audio.
- **Diagnostics.** `--log=verbose` lists the slowest frames (also `onSlowestFrames` in `renderMedia()`); `npx remotion benchmark` compares codecs, compositions and concurrency with repeated runs; a crashed frame ("Target closed") is retried once (3.3).
- **Embedding video.** `<OffthreadVideo>` (3.1) extracts frames with FFmpeg outside the browser, and since 4.0 through the FFmpeg C API with the file kept open (up to 2x faster). For new code the docs prefer `<Video>` from `@remotion/media` (Mediabunny-based, and the only one supported in client-side rendering).
- **Lambda economics.** Distributed rendering: 80 s video in 15 s, 2 h video in 12 min, concurrency up to 200x, from about $0.01 per minute of video (ARM, 2048 MB, warm, us-east-1, excluding S3). Audio is the slow part: 4.0.130 concatenates AAC chunks without a final re-encode (segments padded to multiples of 1024 samples with overlapping keyframe packets, 48 kHz resampling, trimming before `atempo` because `atempo` is imprecise, a negative container offset for AAC's 512-sample priming). Upgrade to at least 4.0.130 for long renders (4.0.528 is fine).
- **Even dimensions.** MP4 (H.264) needs an even composition width and height; 999 x 999 fails (2.4). Element boxes inside the composition can have any size.
- **Compositing hints.** Elements put `willChange: 'transform'` (or `'opacity, transform'`) on moving layers, and several add `transform: 'perspective(100px)'` next to the individual `translate`/`scale` properties. Treat the second as an observed habit, probably to force a composited layer and smooth sub-pixel motion; it is not documented on these pages.
- **HTML-in-canvas and effects.** Studio preview of HTML-in-canvas needs Chrome 149+ with a flag; renders work without it. GPU effects rely on WebGL or WebGPU in the render browser; performance and GPU flags are for the effects agent.
- **Remote assets.** Element defaults load from `remotion.media`, Unsplash, unpkg, NASA GIBS and Cooper Hewitt at render time. For client work copy assets into `public/` and use `staticFile()` (the guidelines' installed-asset path is `staticFileRef()` in `installationProps`) so renders are reproducible offline.

---

## 6. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Particles or positions jump between frames only in the final render | `Math.random()` or state-based randomness differs per render tab | `random(seed)`; derive everything from frame and index |
| Images, iframes or map tiles pop in or flicker | render did not wait for loading | `<Img>`, `<CanvasImage>`, `<IFrame>`; `pauseWhenLoading` for tiles; `delayRender()` for custom loaders |
| Wrong font in first frames or text overflow | text measured or shown before the web font loaded | `loadFont()` and `waitUntilDone()` before rendering or measuring; `validateFontIsLoaded: true`; `cancelRender(err)` on failure |
| Render fails with a delayRender timeout | a handle was never continued | release on every path (success, error); `cancelRender(error)` on failure; the error shows where the handle was created (2.1) |
| Child visuals start at the wrong time inside an Element | `useCurrentFrame()` was called in the component that returns the `<Sequence>` (it reads the parent clock) | move frame-dependent code into a child below the Sequence (guideline). The Spinning Text Wheel Element itself breaks this rule |
| Children are forced to full size and absolutely positioned | default `<Sequence>` layout | `layout="none"` (and pass `outlineRef` for Studio outlines) |
| Captions drift after trimming or speeding up the layer | caption time taken straight from frame | `currentTimeMs = ((trimBefore + (frame - trimBefore) * playbackRate) / fps) * 1000` |
| MP4 render refuses odd sizes | H.264 needs even dimensions | even width and height |
| "Transparent" export is black or opaque | wrong codec, pixel format or image format | ProRes 4444 or VP8/VP9 with `yuva420p`, PNG frames, no background fill; follow the transparent-videos docs |
| 3D logo shows its mirrored back | full 360 degree rotation of a flat extruded shape | rotate only from -90 to 90 degrees and restart (3D logo prompt) |
| Postprocessing glitch differs per frame or per tab | effect library uses its own random or time | ask for (and implement) deterministic seeds driven by frame (3D logo prompt) |
| MapLibre worker fails under Webpack | worker URL rewritten by the bundler | `maplibregl.setWorkerUrl()` with a same-origin Blob that imports the worker module |
| Map render is blank or partly loaded | frame captured before tiles finished | wait for the `'idle'` event after `jumpTo()` and `triggerRepaint()`; fade durations 0; `preserveDrawingBuffer: true` |
| HTML-in-canvas preview shows nothing in Studio | browser flag missing | Chrome 149+ with `chrome://flags/#canvas-draw-element` enabled; `HtmlInCanvas.isSupported()` |
| Social safe zone preview hides the video | Element includes a full-frame sample "Background" image | delete that layer; hide the guide before the final render |
| Video cannot be seeked or errors on load | host without HTTP range support, or unsupported codec | serve with range requests (2.2 warning); transcode |
| Multiple Remotion versions warning | mismatched `remotion` and `@remotion/*` versions (for example after adding an Element) | pin all Remotion packages to the project's version; non-Remotion Element deps use exact versions |
| Old blog snippet does not compile | historic APIs, and the 1.3 post's `interpolate(frame, [0, 100], {...})` omits the output range | use today's names (section 3.10) and full `interpolate(input, inputRange, outputRange, options)` |
| Lambda: missing `s3:ListBucket`, ACL errors, credential conflicts inside another function | IAM or bucket settings | messages and help pages added in 3.2; `privacy: 'no-acl'` for buckets without ACLs |

---

## 7. What our skills must teach

### 7.1 Non-negotiable rules
- Every animated value is a pure function of `useCurrentFrame()`; no `Math.random()`, `Date.now()`, timers, CSS transitions or state that accumulates across frames. CSS animations only through the play-state technique (`examples/css-animation-play-state`), and the Remotion team does not recommend them by default.
- Clamp every `interpolate()` (`extrapolateLeft` and `extrapolateRight: 'clamp'`) unless a value must keep moving (unclamped `rotation` and `phase` in the background Elements are intentional).
- Temporary elements (overlays, lower thirds, labels, callouts) get an entrance and an exit. Backgrounds, loops and full scenes do not need them. Two Elements break this (Wiggling Callout and On-Screen Messages have no exit); our skills should add one when using them as overlays.
- Stagger with `from` on `Interactive.*`, `AbsoluteFill`, `Img`, `@remotion/media` media (4.0.528 supports it), or with `<Sequence>`/`<Series>` for scene structure.
- Write transforms with the individual `translate`, `scale`, `rotate` properties and hardcoded keyframe arrays so Studio can edit them; `output: 'perceptual-scale'` on scale animations.
- Fonts come from `@remotion/google-fonts` (only needed weights and subsets) or local files; numbers use `fontVariantNumeric: 'tabular-nums'`; set explicit text colours on the root of every reusable piece (guideline) so it survives light and dark hosts.
- Media: `<Img>`/`<CanvasImage>` for images, `@remotion/media` `<Video>`/`<Audio>` for new video and audio, `staticFile()` for local assets, `trimBefore`/`trimAfter` (not `startFrom`/`endAt`).
- Before using an Element or template on 4.0.528, check each import against the docs version tags (all Elements pass; `text-content` fields need a compile test).
- Licensing: flag Company License needs for teams of 4+ (Creator seats for Studio and agent work, Automator plan for apps and batch renders).

### 7.2 Default motion vocabulary (distilled from all 41 Elements)
| Purpose | Default | Typical length at 30 fps |
|---|---|---|
| Entrance of cards, bubbles, photos | `Easing.bezier(0.16, 1, 0.3, 1)` plus opacity 0 to 1 and a 14 to 32 px rise, often with a scale up to 1 (from 0.86 for cards, from 0.97 or 0.98 for whole overlays) | 8 to 26 frames |
| Wipes and panel moves | `Easing.bezier(0.65, 0, 0.35, 1)` | 20 to 35 frames |
| Exits | `Easing.bezier(0.7, 0, 0.84, 0)`, `Easing.in(Easing.cubic)` or `Easing.out(Easing.spring(...))` for drops | 12 to 25 frames, a little shorter than the entrance |
| Calm physical settle | `spring` or `Easing.spring` with `damping: 200` (no bounce), `allowTail: true` | 20 to 35 frames |
| Playful bounce (buttons, badges, cards) | `Easing.spring({damping: 7 to 14.5, mass: 0.45 to 0.8, stiffness: 100 to 180})` | 7 to 48 frames |
| Small pops (dots, badges) | `Easing.bezier(0.34, 1.56, 0.64, 1)` | 8 frames |
| Counters | `Easing.out(Easing.exp)` | 90 frames |
| Continuous life during holds | slow push (scale 1 to 1.035, 18 px lift), 3D sway (plus or minus 5 to 10 deg on y with `Easing.inOut(Easing.sin)`) | whole hold |
| Hand-drawn feel | `posterize: 4` (lines), `posterize: 30` (textures) | always on |
| Stagger between siblings | 4 to 12 frames for related items, 24 to 29 frames for separate beats | |
| Overlay total | about 120 frames (4 s): in about 20, hold, out about 15 to 20 | |

### 7.3 Default visual language of Elements
- One accent `#2563eb` (Tailwind blue-600); near-black text `#111827`, `#171717`, `#18181b`; grey data `#d1d5db`, `#b9c0ca`, `#9ca3af`, `#6b7280`; off-white stage `#f5f6f7`; dark UI cards `#15161a` with a 1 px `rgba(255,255,255,0.09)` border, 26 px radius and `0 18px 40px rgba(0,0,0,0.26)` shadow.
- Heavy weights (700 to 900) with negative tracking on big type (-1.6 at 48 px, -2.8 at 70 px, -7 to -8 at 160 to 180 px); `lineHeight: 1` for single-line labels.
- Direct labels instead of legends and axes; one highlighted data point; generous padding (56 to 160 px).
- Elements are sized to their smallest useful box (audio 900 x 300, captions 682 x 252 or 900 x 220, lower third 534 x 132 or 680 x 138, subscribe nudge 760 x 240) and placed by the wrapper; backgrounds read `useVideoConfig()` width and height.

### 7.4 Decision tables
Goal to Element (copy the TSX from `mirror/site/elements/...`):
| Goal | Element | Notes |
|---|---|---|
| Speech visual for a podcast or voice-over | Oscilloscope, Mirrored Spectrum | spectrum also suits music |
| Voice message look with progress | Voice Note (waveform-progress) | static bars, played colour sweep |
| Plain accessible subtitles | Basic Captions | grey translucent box, 2-line clamp |
| Clean boxed subtitles | Rounded Captions | white rounded box, Figtree |
| Energetic short-form captions | Moving Pill, Popping Word, Word Highlight | 800 ms pages, Montserrat with outline |
| Quick animated background | Moving Waves, Moving Zigzags, Liquid Contours, Rotating Starburst | `Solid` plus effect, change colours |
| Paper or notebook look | Paper Texture, Notebook Paper | pair with Caveat or hand-drawn annotations |
| Emphasise a word | Text Marker, Circle Marker, Strike Through, Crossed Off | rough-notation |
| Quote a news headline | News Article Highlight | code-built article; for a real screenshot see the prompt version (OCR positions) |
| Pick one of several options | Spinning Text Wheel | edit `items`, first line wins |
| Numbers and charts | Number Counter, Horizontal Bar, Vertical Bar, Line, Pie | swap the data arrays |
| Show product variants or cards | Rotating Cards | 150 frames |
| Discount or attention sticker | Wiggling Callout | add an exit |
| Premium reveal of an image or card | Shine | HTML-in-canvas |
| Destructive reveal | Tear apart | HTML-in-canvas, 4.0.523 |
| Presenter to picture-in-picture | Picture in Picture Transition | crop-based |
| Compare two things | Slide to Split Screen | 60/40 with divider |
| Travel route | Watercolor Map (illustrated, no library), A-to-B Map Flyover (satellite, MapLibre) | keep attribution |
| Speaker or place intro | Name Lower Third, Location Lower Third | |
| Vertical video safety | Social Safe Zones | guide only, delete its Background layer |
| Story beat with texts | On-Screen Messages | |
| Memories or before/after | Polaroid Pictures | |
| YouTube engagement | Subscribe Nudge (with SFX), Comment Highlight, End Card | end card is 16:9 full frame with two 631 x 361 slots |

Template choice (`npx create-video@latest --flag`):
| Project | Flag |
|---|---|
| Agent writes everything | `--blank` (recommended when writing code with AI) |
| Learning playground with lint and format | `--hello-world` |
| SaaS app with Player plus Lambda | `--next` (recommended) or `--react-router` |
| Render on demand on Vercel | `--vercel` (Vercel Sandbox VMs, Vercel Blob output) |
| Self-hosted render API | `--render-server` (Express: start, track, cancel) |
| Desktop app | `--electron` |
| AI prompt to motion graphics product | `--prompt-to-motion-graphics` (generates Remotion code, streams it, compiles and previews in the browser) |
| AI prompt to narrated story video | `--prompt-to-video` (OpenAI script and images, ElevenLabs voice) |
| Captioned talking video | `--tiktok` (installs Whisper.cpp, word-by-word captions) |
| Podcast clip | `--audiogram`; music clip `--music-visualization` |
| Screen plus webcam productions | `--recorder` |
| Overlays for Premiere, Resolve, Final Cut | `--overlay` |
| Code walkthrough | `--code-hike` |
| 3D | `--three` (React Three Fiber) or `--skia` |
| OG images and thumbnails | `--still` (includes an HTTP server) |
| GitHub star milestone | `--stargazer` |

### 7.5 Agent workflow lessons from the Prompt Showcase
- Load the Remotion skill explicitly (the community phrase is "use remotion best practices"; name sub-areas such as "html in canvas" or "maps"), and link a docs page as `.md` when a feature matters (Music CD, Vintage screen and 3D logo prompts did this).
- For product demos, interview the user first ("Really grill me with questions"), take feature priorities from the marketing page, and rebuild the UI with React components instead of screen recordings.
- For open-ended data art, produce 3 short variants first, then refine the chosen one (Rocket Launches prompt).
- Source data and assets with tools: scrape a channel page with curl for the avatar and subscriber count (warn about duplicates), OCR a screenshot with tesseract to find word positions, parse GPX files, fetch a product site for logo and copy.
- When installing packages, detect the existing lockfile and use its package manager (News highlight prompt).
- After rendering, open or show the file (Cursor prompt) and check it; the 3D logo prompt shows the loop of art-direction feedback ("too dark", "completely white, find a middle ground").
- Keep text legible for the platform (Strava prompt: story-sized fonts) and keep content inside social safe zones.
- Split big videos into scene components with explicit frame counts that add up to the total, share one app-window or card component, and define the palette and fonts once (Launch Video prompt).
- Never render a real person's likeness or a brand's identity without rights (Cinematic Tech Intro uses a public figure's photo and a company's colours); our skills should ask.

### 7.6 Quality checklist before render
1. Canvas even-sized; fps and duration match the brief; composition id meaningful.
2. Every overlay has an exit; every stagger reads in order; nothing pops without easing.
3. Fonts loaded and awaited; text measured after load; numbers tabular; explicit colours.
4. All async work behind `delayRender`; no remote asset that can disappear (copy to `public/`).
5. Deterministic: seeds, no time or random APIs; scrub the Studio timeline backwards and forwards and compare frames.
6. Audio: SFX aligned to the visual frame, sample lead-in trimmed, music faded (the Launch prompt: 1 s in, 2 s out, 40% volume).
7. Output format matches the use: MP4 H.264 for social, ProRes 4444 or WebM alpha for overlays, 1080 x 1920 for Reels/TikTok/Shorts with safe zones checked.

---

## 8. Best examples to learn from

Elements (complete source in the mirror):
- `mirror/site/elements/guidelines.md`: the authoring contract for reusable video pieces (focus, portability, installation modes, entrance and exit rule).
- `mirror/site/elements/captions/moving-pill-captions.md`: DOM measurement plus spring-summed fractional index; the most advanced motion logic on the site.
- `mirror/site/elements/captions/rounded-captions.md`: `fitTextOnNLines` plus `measureText` plus `createRoundedTextBox`.
- `mirror/site/elements/maps/map-flyover.md`: integrating an async third-party renderer (delayRender, useBufferState, idle events, worker URL, high-resolution plate).
- `mirror/site/elements/maps/watercolor-map.md`: a map without a map library (Mercator maths, tiles, arc route).
- `mirror/site/elements/youtube/youtube-subscribe-nudge.md`: frame-exact micro-interaction choreography with SFX.
- `mirror/site/elements/storytelling/polaroid-pictures.md`: fly-in, settle, push-in and fly-out with per-segment easing arrays.
- `mirror/site/elements/layouts/picture-in-picture-transition.md` and `slide-to-split-screen.md`: crop and width based layout transitions.
- `mirror/site/elements/data/vertical-bar-chart.md` and `line-chart.md`: mask reveals, spring growth, path drawing, staggered pops.
- `mirror/site/elements/text/spinning-text-wheel.md`: CSS 3D drum with a heavy spring and a mask gradient.
- `mirror/site/elements/audio/oscilloscope.md`, `mirrored-spectrum.md`, `waveform-progress.md`: the three audio data patterns.
- `mirror/site/elements/backgrounds/*.md`: shortest possible effect-driven backgrounds.

Prompts:
- `mirror/site/prompts/launch-video-on-x.md`: best multi-scene production spec (scene list with frames, palette tokens, fonts per role, music, shared components).
- `mirror/site/prompts/apple-style-device-rise-animation.md`: exact numbers and a pre-emptive fix for transform order and centring.
- `mirror/site/prompts/solar-system-orbit-animation.md`: acceptance criteria ("Expected Result"), determinism, Canvas plus HTML overlay split, second composition.
- `mirror/site/prompts/news-article-headline-highlight.md`: tool-assisted positioning (OCR) and subtle camera values.
- `mirror/site/prompts/spinning-glitching-svg-logo-turned-3d.md`: iterative art direction ending in a transparent export.
- `mirror/site/prompts/transparent-call-to-action-overlay.md`: data scraping plus micro-interaction easing plus alpha output in one paragraph.

Tutorial and blog:
- `mirror/site/learn.md`: composition by small wrappers, polar duplication, speed remapping with `<Freeze>`, image-sequence playback.
- `mirror/site/blog/faster-lambda.md`: why audio is the hard part of distributed rendering.
- `mirror/site/blog/1-4.md`: the randomness rule; `mirror/site/blog/3-3.md`: CLI defaults and diagnostics; `mirror/site/blog/4-0.md`: Studio, calculateMetadata and the v4 architecture.

Code outside my assignment worth pairing (for the templates and examples agent):
- `repo/packages/template-*/src` (tiktok `CaptionedVideo`, audiogram, music-visualization `Visualizer`, prompt-to-motion-graphics with its own `skills/` and `examples/` folders, code-hike, three, still, overlay); `repo/packages/template-vibe-code` exists but is not on the site.
- `examples/`: `typewriter`, `d3-example`, `3d-text`, `three-particles`, `morph-text`, `text-warping`, `glb-example`, `remotion-three-gltf-example`, `gl-transitions`, `light-leak-example`, `anime-example`, `video-with-jump-cuts`, `css-animation-play-state`, `tone-js-example`, `animated-captions`, `html-in-canvas`, `mapbox-example`, `motion-blur-example`, `apple-wow-tutorial` (the Learn tutorial source). The 2024 Studio blog lists many of these as deployed Studios.

---

## 9. Open questions

1. `type: 'text-content'` schema fields (Rotating Cards, both map Elements, Spinning Text Wheel) do not appear in `mirror/docs/interactivity-schema.md`; they are used in repo 4.0.529 code. Confirm with a TypeScript compile on 4.0.528 before shipping these Elements.
2. Element metadata (duration, dimensions, dependency versions, installation mode, initial props) lives in `element-definitions.ts`, which is not mirrored. Durations had to be inferred from the code (for example Voice Note defaults to 271 frames, Rotating Cards exports 150, the map flyover needs about 240).
3. Do GPU effects and HTML-in-canvas render identically on Lambda and on the local headless browser shipped with 4.0.528? The site only says rendering "just works"; the effects agent should confirm GL settings.
4. Remote default assets (remotion.media, Unsplash, unpkg for the MapLibre worker, NASA GIBS, Cooper Hewitt tiles): availability, rate limits and licences for client deliverables. Our skills should localise them.
5. The purpose of `transform: 'perspective(100px)'` beside individual transform properties in several Elements is undocumented.
6. The Polaroid page promises "developing-photo accents" that the code does not implement; the Music Visualization card on the templates index reuses the Audiogram description.
7. The Mediabunny post says both "As of February 1st 2026, Media Parser is now deprecated" and "Media Parser is not yet deprecated" (stale sentence). Treat it as deprecated.
8. The showcase page is empty in the mirror; its videos and source links could be a useful quality bar if fetched separately.
9. Prompt pages do not include outputs, so the like count (popularity) is the only quality signal; short prompts by the Remotion team rank highest, likely because of reach rather than prompt quality.

---

## Appendix A. Elements catalogue (41 Elements)

Legend: mode "owned" = exported through `Interactive.withSchema()` (one Studio layer with Inspector controls); "wrapped" = plain component with internal `Interactive.*` layers. All defaults are from the source. Accent colour is `#2563eb` unless stated.

### A.1 Audio (all owned, default audio `https://remotion.media/elements/remotion-made-this-picture-move.mp3`)
1. **Oscilloscope** (`audio/oscilloscope`, export `AudioOscilloscope`). Live waveform line for speech. Props: `audioSrc` (asset, audio), `lineColor` `#2563eb`, `lineWidth` 6 (1 to 16), `amplitude` 2 (0.25 to 4), `windowInSeconds` 0.35 (0.05 to 1) plus base and transform props. Look: 900 x 300 box, smooth rounded stroke over a faint centre line (stroke opacity 0.18). Technique: `useWindowedAudioData` (10 s window) plus `getWaveformPortion` (64 samples centred on now, not normalised, range -1 to 1) plus `createSmoothSvgPath`; renders its own `<Audio showInTimeline={false}>`. Deps: `@remotion/media`, `@remotion/media-utils`.
2. **Voice Note** (`audio/waveform-progress`, export `AudioWaveformProgress`). Messenger-style static waveform whose bars fill with colour as audio plays. Props: `audioSrc`, `playedColor` `#2563eb`, `unplayedColor` `#cbd5e1`, `numberOfBars` 64 (12 to 96, not keyframable), `barGap` 5 (0 to 8), `amplitude` 1 (0.25 to 2); default `durationInFrames` 271. Look: 900 x 300, rounded vertical bars (height 10 to 210 px, square-root scaled) centred on a midline. Technique: whole-clip `getWaveformPortion` at frame 0, one gradient with a hard stop at `progress = frame / (duration - 1)`, `useId()` for a unique gradient id, keyed remount when the source or duration changes.
3. **Mirrored Spectrum** (`audio/mirrored-spectrum`, export `MirroredAudioSpectrum`). Symmetric frequency bars for music or speech. Props: `audioSrc`, `barColor` `#2563eb`, `numberOfBars` 65 (3 to 127, odd steps, not keyframable), `sensitivity` 1.5 (0.25 to 3). Look: 900 x 300 flex row, gap 8, pill bars (radius 999), minimum 4 px, low frequencies in the centre. Technique: `visualizeAudio` with 256 samples and `optimizeFor: 'speed'`, first `ceil(n / 2)` bins mirrored, height `300 * sqrt(v) * sensitivity`.

### A.2 Backgrounds (wrapped, full frame via `useVideoConfig()`; all use `<Solid>` plus `@remotion/effects`; default palette `#dff4ff` and `#7cc6ff`)
4. **Liquid Contours**: two-colour flowing contour bands; `liquidContours({firstColor, secondColor, phase: interpolate(frame, [0, 240], [3.23, 4.23])})` (unclamped, keeps flowing). 4.0.491.
5. **Moving Waves**: horizontal bands that flow upward seamlessly; `waves({colors, direction: 'horizontal', thickness: 56, gap: 0, angle: 0, offset: frame / duration * 448, amplitude: 24, wavelength: 160, phase: 0})`. 4.0.471.
6. **Moving Zigzags**: same idea with sharp zigzags; `zigzag({thickness: 40, offset: frame / duration * 480, amplitude: 40, wavelength: 160, ...})`. 4.0.471.
7. **Notebook Paper**: white paper grain plus blue-grey grid; `paper({amount: 0.38, contrast: 0.18, roughness: 0.18, fiber: 0.28, crumples: 0.1, folds: 0.12, seed: 24, scale: 0.8, drops: 0})` then `gridlines({gridSize: 54, lineWidth: 3.4, lineColor: 'rgba(76, 101, 128, 0.16)'})`. Static.
8. **Paper Texture**: white paper whose grain re-rolls every 30 frames: `paper({seed: interpolate(frame, [0, 120], [0, 1000], {posterize: 30, clamp})})` (after frame 120 it stays still).
9. **Rotating Starburst**: 28 alternating rays slowly rotating: `starburst({rays: 28, colors, rotation: interpolate(frame, [0, 2000], [0, 360]), origin: [0.5, 0.5]})`. 4.0.500.

### A.3 Captions (all owned; props `captions: Caption[]`, `playbackRate`, `combineTokensWithinMilliseconds`, `width`, `height`, `trimBefore`, base and transform; schema includes `Interactive.captionsSchema` so Studio can import caption JSON)
10. **Basic Captions**: white Arial 64 px on `rgba(64, 64, 64, 0.75)`, padding 14 x 22, `textWrap: 'balance'`, clamp to 2 lines; pages of 2000 ms; area 900 x 220. No web font needed.
11. **Rounded Captions**: black Figtree 700 on a white box whose outline follows each line with 20 px rounded corners (`@remotion/rounded-text-box`), max 64 px, 2 lines, 2000 ms pages, 900 x 220; `playbackRate` and `combineTokensWithinMilliseconds` typed nullable.
12. **Moving Pill Captions**: white Montserrat 700 up to 80 px with a black outline (`fontSize / 7`), a blue pill (radius 10, padding 12) that glides to each newly spoken word in 5 frames; 800 ms pages; 682 x 252.
13. **Popping Word Captions**: same base; the active word turns blue and scales to 1.03 from the bottom centre with a 4-frame spring in and linear out.
14. **Word Highlight Captions**: same base; the active word turns blue, no motion. Most readable karaoke style.

### A.4 Commerce / effects
15. **Rotating Cards** (`commerce/product-collection`, listed under Layouts; wrapped, inner `ProductCard` owned with `label` text-content). Three photo cards (A, B, C over blue and pink stock backgrounds, card C hue-rotated -65 deg) arranged in an arc; each takes the centre once. 150 frames (exported constant). Container 900 x 660 fades and scales in over 10 to 16 frames and out over the last 8. See recipe R21 for the maths.
16. **Wiggling Callout** (`commerce/product-discount-callout`, wrapped). Blue speech bubble (`makeCallout` 600 x 300, pointer down, 70 long, 130 wide, radius 45) with "-20%" in Inter 800 at 180 px, letter spacing -7; wiggles 0, 10, -7, 3, 0 deg over 26 frames around its pointer. No exit.
17. **Shine** (`commerce/shine`, wrapped). Diagonal light sweep across an image inside `<HtmlInCanvas>` 1280 x 720 (`scale` 0.75 then `shine`, angle 30, halo sigma 200, core sigma 65, intensities 0.3 and 0.4), 44 frames. 4.0.468.
18. **Tear apart** (`commerce/tear`, wrapped). The graphic rips with a jagged edge (jaggedness 24) and a 5 deg rotation between frames 15 and 25, spring-eased. Needs 4.0.523.

### A.5 Charts and data (wrapped, background `#f5f6f7`, Inter 700 and 800, tabular numbers)
19. **Horizontal Bar Chart**: three bars (Jonny 18 highlighted, Igor 17, Mehmet 10), width proportional to value, radius 12, label left and value right inside the bar; bars wipe in from the left (frames 14 to 47 of each bar, ease-out), 6-frame stagger via `from={8 + i * 6}`, label fades at 26 to 32, value at 32 to 38.
20. **Line Chart**: seven months (Mar to Sep, 24 to 74) on a 1600 x 640 plot with four grey gridlines; 12 px blue line draws over frames 14 to 58; white dots with blue 8 px rings pop one by one; a blue "74K" badge springs up above the last point at frame 58 (forced to scale 1 from frame 70); every second month labelled.
21. **Number Counter**: 0 to 24,813 in 90 frames with exponential ease-out; Inter 800, 150 px, `#171717`, tracking -0.03em, `en-US` separators.
22. **Pie Chart**: four slices (Focused work 42, Meetings 26, Planning 18, Admin 14) in blue and three greys, radius 284 in a 600 viewBox drawn at 680 px; clockwise sweep over frames 8 to 60; legend rows (104 px, radius 12, same colours) wipe in with `cropLeft`, values fade before labels.
23. **Vertical Bar Chart**: three bars (34, 89, 163 highlighted) 280 px wide on a 1080 px baseline; bars grow with a bouncy spring easing, 24-frame stagger, value labels rise out of a mask at the bar tip, names slide up under the baseline.

### A.6 Layouts
24. **Picture in Picture Transition** (wrapped): scene A (blue photo with a giant "A") shrinks into a rounded box at the top right over frames 15 to 50 while scene B stays full frame (recipe R19).
25. **Slide to Split Screen** (wrapped): full-screen A opens into A 60% | white 15 px divider | B 40%, holds and closes (frames 20 to 130; recipe R20).

### A.7 Maps (owned)
26. **A-to-B Map Flyover** (`MapFlyover`): NASA Blue Marble satellite basemap (GIBS, max zoom 8, no key), great-circle route between `origin` (default London `[-0.1276, 51.5072]`) and `destination` (Tokyo `[139.6917, 35.6895]`) with its bend halved in Mercator space; red-coral route (`routeColor` `#ff5c4d`, `lineWidth` 24, range 2 to 24) draws over frames 0 to 205 (`Easing.inOut(Easing.quad)`) while the camera follows; origin label fades at start; destination marker grows from route width to full size, then a white centre dot and the label appear (frames 210 to 240); labels 26 px white with drop shadow; soft vignette; attribution badge. Props: `origin`, `destination` (arrays of 2 numbers), `originLabel`, `destinationLabel` (text-content), `routeColor`, `lineWidth`. Deps: `maplibre-gl`, `@turf/turf` (plus CSS import `maplibre-gl/dist/maplibre-gl.css`).
27. **Watercolor Map** (`WatercolorMap`): hand-painted watercolor tiles, arc route with a white casing, round markers (60 px, 12 px white border), white pill labels in Lora 700 40 px with a white glow, label above or below depending on screen space. Defaults Los Angeles to Zurich, `routeColor` `#ff0041`, `routeWidth` 18 (4 to 30); travel frames 40 to 130 (`Easing.inOut(Easing.ease)`), labels and marker springs (damping 200, 20 frames) at 40, 130 and 133. No map library. Also sold as a paid template.

### A.8 Overlays
28. **Location Lower Third** (wrapped, 680 x 138): blue map pin that draws, fills and pops its inner dot, plus "Berlin, Germany" (54 px bold `#18181b`) wiping in; full exit by frame 119.
29. **Name Lower Third** (wrapped, 534 x 132): "Alex Morgan" on a blue bar over "Creative Developer" on a near-black bar, both white Inter 700 34 px; crop wipes in 20 frames, staggered 4, out in reverse; about 116 frames.
30. **Social Safe Zones** (owned, fixed 1080 x 1920): transparent PNG captures of the Instagram Reels or TikTok interface (`platform` enum) laid over a sample background; `zIndex` max, no pointer events. Captures were measured from iOS on full-green videos; treat as a reference, not a guarantee.

### A.9 Storytelling
31. **News Article Highlight** (`text/news-article-highlight`, listed under Storytelling; wrapped): a newspaper-style article (category "Politics" in rust `#a0432d`, Georgia 70 px headline with `textWrap: 'balance'`, Georgia 25 px summary) where "government shutdown" and then "funding lapses" get yellow marker strokes word by word from frame 31; fades out at 125 to 149.
32. **On-Screen Messages** (wrapped, 1260 x 680): three iMessage bubbles ("I just saw you at the station." / "I'm still in Berlin." / "Then who waved back?") appear at frames 2, 27 and 52.
33. **Polaroid Pictures** (wrapped, 1480 x 640): three taped instant photos with handwritten captions fly in (frames 8, 20, 32), settle at alternating angles, the group slowly pushes in, and the photos fly out at the end (recipe R23).

### A.10 Text effects (wrapped unless noted; serif demos use Cormorant Garamond 700 at 80 px, `#171717`)
34. **Circle Marker**: blue rough circle (stroke 12, roughness 1.8, padding 10, `box: 'inside'`) drawn around "circular" over 43 frames with 4-frame posterized progress and seed (boiling line).
35. **Crossed Off**: red `#eb2525` scribbled cross (10 iterations, roughness 2, stroke 6) over "remove", frames 18 to 39.
36. **Strike Through**: thick red `#f11515` hand-drawn line (stroke 14) through "forbidden", frames 10 to 25.
37. **Text Marker**: translucent yellow `rgba(255, 236, 79, 0.62)` highlighter behind "remarkable" (roughness 2.3, random offset 10, bowing 0, 20 px side padding), 25 frames, spring-eased.
38. **Spinning Text Wheel** (owned; props `items` newline-separated text-content, first line is the winner, plus `Interactive.textSchema`): weekday names spin on a 3D drum inside a 400 x 200 masked window and decelerate onto "Friday" over 90 frames; Mona Sans 700 65 px `#182033`; non-selected items at 0.28 opacity.

### A.11 YouTube (wrapped, Inter)
39. **YouTube Comment Highlight** (1120 x 360 stage): dark comment card with round avatar (Unsplash photo via `CanvasImage`), handle, two-line comment, like count and thumbs icons; bounces up from below, sways in 3D, drops out (about 180 frames).
40. **YouTube End Card** (full 16:9 frame, `#FAFAFA`): avatar plus black pill "Subscribe" button rising from below (frames 35 to 65), then website, X, LinkedIn and Instagram rows fading in bottom-up, and two empty 631 x 361 black-bordered frames on the right for YouTube's end-screen video slots.
41. **YouTube Subscribe Nudge** (760 x 240, props `clickSrc`, `dingSrc`, `avatarSrc`): dark channel card with avatar, name, handle, red Subscribe button, bell; an arrow cursor clicks Subscribe (state flips to Subscribed with a checkmark), then the bell; click and ding SFX; about 120 frames (recipe R25). Deps: `@remotion/media`, `@remotion/sfx`.

### A.12 Element authoring notes (guidelines and contributing pages)
- Start from a technique seen in a real published video (keep the link and timestamp); AI ideas or web components are not evidence that it works in video; do not copy branding or footage.
- One coherent treatment per Element; works with zero configuration; no Elements for presets or tiny CSS variations (the three word-level caption styles are separate because users would pick them separately).
- Portable: HTML, CSS and React; no global styles or fullscreen assumptions (except backgrounds); explicit text colours; Google Fonts for non-web-safe fonts; few dependencies (Remotion Effects are acceptable); every non-Remotion dependency with an exact version; Remotion packages use `version: null` (installed at the project's Remotion version).
- Animate properties inside the Element (translate, scale, opacity) and leave placement to the wrapper or owned Sequence.
- Controls must meaningfully edit the treatment, never switch between unrelated styles; name editable objects clearly ("Container" for the root).
- Choose a representative poster frame; the preview video covers the full duration including entrance and exit.
- Contributing: copy `packages/docs/elements-template`, register in `element-definitions.ts` and `elements-sidebars.ts`, preview with `cd packages/docs && bun remotion`, render previews with `bun run render-element-previews --element=<category>/<slug>`, test with `bun test src/test/elements.test.ts`; a "scaffold-element" Agent Skill automates setup. Starter props go in `initial-props.ts` (`satisfies ComponentProps<typeof X>`), installed assets are declared with `staticFileRef()` in `installationProps`.
- Third-party Element libraries that can be added to Studio: Remocn (`https://remocn.dev/docs/typography`) and Lexington Themes (`https://lexingtonthemes.com/remotion/free-templates`).

---

## Appendix B. Prompt Showcase catalogue and prompt style guide

25 prompts across 3 gallery pages (likes at mirror time). Tool and model as shown on the page (two pages swap the fields).

| # | Prompt (author, likes) | Tool, model | Video type | Length and structure |
|---|---|---|---|---|
| 1 | Travel Route on Map with 3D landmarks (@JNYBGR, 347) | Claude Code, Opus 4.5 | map travel with camera follow and 3D landmark | 2 short turns, iterative |
| 2 | News article headline highlight (@Remotion, 347) | Claude Code, Opus 4.5 | news B-roll from a screenshot | 1 paragraph of ordered steps |
| 3 | Product Demo for Presscut (@Shpigford, 242) | Claude Code, Opus 4.5 | SaaS demo with UI rebuilt in React | short goal plus an interview request |
| 4 | Launch Video on X (@ghumare64, 198) | Claude Code, Opus 4.6 | 37 s, 8-scene product launch | long spec: globals plus 8 scene blocks |
| 5 | Cinematic Tech Intro (@tiw_ari_ayu, 191) | Gemini, k2.5 | CEO intro, kinetic title, HUD | 1 dense paragraph |
| 6 | Transparent Call-To-Action overlay (@Remotion, 172) | Claude Code, Opus 4.5 | YouTube subscribe lower third with alpha | 1 paragraph |
| 7 | Rocket Launches Timeline (@crispynotfound, 126) | not stated | data art timeline | 2 sentences plus a variants request |
| 8 | Real Estate Investing (HarisShah2345, 108) | Claude Code, Opus 4.5 | vertical edit of raw footage | role plus 7 staged sub-prompts |
| 9 | Three.js "Top 20 Games Sold" Ranking (@DilumSanjaya, 92) | Claude Code | 3D ranking tower with camera path | medium: steps plus pasted data |
| 10 | Promotion video for VVTerm (@wiedymi, 80) | Claude Code, Opus 4.5 | Apple-keynote-style promo | 2 sentences |
| 11 | Music CD store promo (samohovets, 65) | OpenCode, Kimi K2.5 | 30 s promo, audio reactive | section list plus 3 refinement turns |
| 12 | Bar + Line Chart (combined) (samohovets, 62) | OpenCode, Opus 4.5 | combo chart | 1 dense sentence |
| 13 | Cursor Agent Skills Announcement (@edwinarbus, 45) | Cursor | announcement with typewriter cards and recording zoom | medium: cards, shots, notes |
| 14 | Shape to words transformation (@tiw_ari_ayu, 42) | Gemini, k2.5 | logo intro with morphing shapes | medium: 4 scenes plus tech requirements |
| 15 | Spinning, glitching SVG Logo turned 3D (@Remotion, 41) | Claude Code, Opus 4.5 | 3D metallic logo, glitch, alpha | pasted SVG plus 8 short refinement turns |
| 16 | 3D Retro Pixel Font (@GogHeng, 35) | Claude Code, Opus 4.6 | square brand animation with pixel text | medium: effect, timeline, variant |
| 17 | Apple-Style Device Rise Animation (@gaucho_booleano, 33) | Claude Code, Opus 4.5 | device mockup reveal | long numeric spec with an IMPORTANT block |
| 18 | Strava Run visualized (@JNYBGR, 31) | Claude Code, Opus 4.5 | GPX data story | 2 sentences plus a data file |
| 19 | HTML-in-canvas magnifying glass (@JNYBGR, 27) | Claude Code, Opus 4.7 xhigh | lens refraction effect | 1 sentence |
| 20 | The Kinetic Marketing (@tiw_ari_ayu, 26) | Gemini, k2.5 | kinetic typography promo | 1 dense paragraph (style only) |
| 21 | Audio Spectrum Visualizer (samohovets, 23) | OpenCode, Opus 4.5 | music visualizer | 1 dense sentence |
| 22 | Vintage screen effect (HTML-in-canvas) (@JNYBGR, 21) | Claude Code, Opus 4.7 | CRT terminal | short: docs link plus scripted content |
| 23 | BMS Active Cell Balancing Animation (pasrom, 18) | Claude Code, Opus 4.6 | engineering explainer | long engineering spec |
| 24 | Glitch effect (HTML-in-canvas) (@remotion, 17) | Claude Code, Opus 4.7 xhigh | effect demo | 2 sentences |
| 25 | Solar System Orbit Animation (@GogHeng, 10) | Claude Code, Opus 4.6 | science explainer | long Markdown spec with acceptance criteria |

### B.1 Per-prompt notes (what it asks, why it works, what is missing)
1. **Travel Route**: two short turns: map, zoom out of LA "while staying focused on it", line LA to NY "and make the camera follow it"; then "add another stop... paris... animate the eiffel tower and show it in 3D". Works because it opens with the skill trigger and describes camera behaviour in plain verbs; scope grows turn by turn. Missing: size, duration, style (left to the skill).
2. **News article headline highlight**: import a local screenshot, OCR with tesseract to find text positions, pad the article generously on a white Full HD background, 5 s, very subtle zoom and 3D rotation (about 15 deg per axis) from left to right, blur to sharp over the first second, then a rough.js highlighter left to right over two named phrases, marker behind the text, and use the project's package manager. Works: tool chain for positions, exact timing and magnitudes, explicit layering, hygiene.
3. **Presscut demo**: build a demo with React components replicating the app UI "as closely as possible"; pick features from the marketing homepage; keep language simple; "Really grill me with questions"; goal: what the founder would show a customer. Works: states purpose and audience, forces a requirements interview. Missing: format and length (the interview fills them).
4. **Launch Video on X**: canvas (1080 x 700, 30 fps, about 37 s), theme tokens (`#0c0a09` background, `#fbbf24` accent, surface, border and three text greys), music track with 1 s fade in, 2 s fade out at 40% volume, then 8 scenes each with frames and seconds (120, 150, 160, 130, 140, 120, 180, 120), detailed UI copy, motion per scene (typing at 1 char per frame, 3D terminal slide with rotateX 20 deg, staggered spring reveals, word-by-word reveal, logo rotating in from -180 deg), one global transition rule (spring fade plus scale 0.95 to 1 and back) and one shared `AppWindow` component; fonts by role (Inter UI, SF Mono code, Georgia brand). The strongest production spec in the gallery.
5. **Cinematic Tech Intro**: one dense paragraph: 1920 x 1080 30 fps, "Cyberpunk/Tech-Corporate", white background with radial noise, huge name in Knewave `#76B900` popping from 3x to 1x, cutout photo at frame 40 with spring entrance, float and occasional glitch (skew, hue-rotate), rotating dashed rings, falling data streams, glassmorphism HUD with cut-corner clip-path sliding from -600 px, scanner line, corner brackets, geometric particles, "spring and interpolate for all". Works: rich named effects with numbers and one key beat time. Risks: real person and brand identity.
6. **Transparent CTA overlay**: scrape the channel page with curl for avatar and subscriber count (pick the right one of several), white lower third sliding up from bottom centre with name, count and avatar, fixed-width black Subscribe button switching to Subscribed, ease-out for the press, spring with slight bounce on release, fade out, render as transparent ProRes. Works: data source plus micro-interaction curves plus output format in five sentences.
7. **Rocket Launches Timeline**: every SpaceX launch 2015 to 2025 in order, launch parabolas with fading trajectories, abstract minimalist; "Give me three versions first, then I'll pick one". Works: exploration step; aesthetic keyword; data scope. Missing: data source, format.
8. **Real Estate Investing**: role prompt ("high-end real estate video editor...") and seven staged sub-prompts: analyse the raw video (highlights, weak parts, 1 to 3 s micro-scenes, ideal 15 to 30 s length with timestamps), second-by-second edit plan (motion, transition, text, text animation), motion graphics package (price reveal, location lower third with animated pin, bed/bath/sqft counters, "Just Listed" titles, blueprint grid, corner brackets; black and gold or white and navy), typography (modern serif or bold sans headline, clean sans body, fade and slide, mask reveal, word-by-word hooks), cinematic touches (subtle light leaks, warm grade, grain, slow zooms, luxury music with beat drop), retention (hook in 2 s, pattern interrupt at 5 to 7 s, speed ramp, loop cut or CTA) and export (9:16 1080 x 1920, loud clean audio). Works as a checklist; weak on numbers, and it assumes the agent can watch video (pair with a video-analysis tool).
9. **Three.js ranking**: starts from the React Three Fiber template, removes the example, 1920 x 1080 at 60 fps, one box tower per game with height by copies sold, camera from the last rank to the first stopping briefly at each; data pasted as JSON. Works: known starting point, inline data, camera choreography.
10. **VVTerm promo**: Apple presentation style, fetch details and logo from the product site, Nerd Fonts and Inter, about 20 s. Works: a strong style reference in few words; everything else sourced from the web.
11. **Music CD store promo**: section by section: hook text on black (fade in, hold 2 s, fade out), logo from `public/` on a warm orange gradient with tagline, counter to 12,000+ ("Happy customers"), five abstract gradient album covers sliding in one by one with artist and song names, CTA with URL, fade to black; then refinements: smoother transitions (interpolate the background from black to orange), make the logo audio reactive (links the `use-windowed-audio-data.md` doc), make all scenes react, react to low frequencies only. Shows iterative prompting and doc-linking.
12. **Bar + Line Chart**: single sentence: 1920 x 1080, dark `#1A1A2E`, composition id `BarLineChart`, revenue bars for Jan to Jun with values, blue `#0B84F3` conversion line with values drawing with glow, bars sequential with slight overlap, line following, axis labels, pulsing dot at the line tip, spring timing over 120 frames at 30 fps, skill named. Complete and testable.
13. **Cursor announcement**: 1920 x 1080 at 60 fps, typewriter at about 1 character per frame, hold 3 s after typing, line 1 then line 2, exact copy for each card, recording full screen top-aligned for 2 s then continuous eased zoom to the top-left by about 125%, final card, end with an existing `end.mp4`, "Render and open the file inside Cursor's browser tool"; brand rules lived in a separate rules file. Works: timing units the agent can compute, reuse of assets, verification step.
14. **Shape to words**: 10 s, white canvas with light grid; scene 1 eight coloured shapes in a row (90 px spacing) breathing; scene 2 shapes jump, spin 180 deg and morph with flubber into R-E-M-O-T-I-O-N with a ghost trail; scene 3 logo flies in, snaps with a spring and spins 360 deg; scene 4 logo slides across and erases each letter as it passes ("Wipe Logic"); springs damping 14 for jumps and 300 for the wipe; filled shapes, no strokes. Works: scene mechanics, named library, physics numbers.
15. **3D logo**: paste the SVG, make it 3D with a metallic material, then a feedback loop: smaller and more silver, brighter, "completely white, find a middle ground", rotate only -90 to 90 deg to hide the back, add the react-postprocessing glitch (link), "make everything deterministic", export transparent for After Effects, "did not work, check the docs: transparent-videos". Teaches art-direction deltas and pointing the agent at docs when it fails.
16. **3D Retro Pixel Font**: 1080 x 1080, 8 s, black; four coloured cursors fly in, scatter, line up and "build" pixel text (two lines) block by block like collaborative editing; 20 px blocks with layered emboss; second-by-second timeline (0 to 0.4, 0.4 to 0.9, 0.9 to 1.6, 1.6 to 5.0, 5.0 to 5.8 typed subtitle, 5.5 to 8.0 cursors float away); plus a red colour variant. Works: metaphor, mechanics, timeline, variant.
17. **Apple device rise**: 1280 x 720, 30 fps, 4 s; phone rises from 400 px below with ease-out cubic, rotateX 35 to 8 deg, scale 0.8 to 1 over 1.5 s; exact device spec (320 x 650, bezel `#1a1a1a`, radii 45 and 35, Dynamic Island 90 x 28, 9:41 status bar, green gradient wallpaper, shadow strings); an IMPORTANT block on centring (`bottom: -250px`, `left: 50%`, transform origin centre bottom, and the transform order translateX(-50%), translateY, rotateX, scale); then notification cards sliding down 0.3 s apart with backdrop blur; background `#f5f5f7`. Works: numbers everywhere and a pre-emptive fix for the classic centring bug.
18. **Strava run**: attach a GPX file, "turn my run today into an animated instagram story", map, route and live metrics, font sizes legible in a story. Works: real data plus a platform constraint.
19. **Magnifying glass**: HTML-in-canvas, one line of text, round magnifier moving left to right with slight glass refraction. Minimal effect demo relying on the skill.
20. **Kinetic Marketing**: style words ("Aurora Glassmorphism", breathing pastel pink, lavender, soft blue gradients, 3D floating React logos with depth-of-field blur, radar rings, pulse circles), accent `#0b84f3`, Poppins Black, elastic layout where new words push old ones, exits rotating -15 deg and shrinking, blue iris wipes and ring tunnels, 140 BPM. Works: vocabulary and a tempo; missing size and duration.
21. **Audio Spectrum**: 1920 x 1080 dark, id `AudioSpectrum`, `funk.mp3` from `public/`, 32 bars reacting to bass, mids and highs, magenta to cyan gradient, glow, rounded tops, faint reflection on a glossy floor, fade-in, duration equal to the audio at 30 fps, expose bar count, gradient colours, bar width and glow as props, skill named. Works: parameterization request and data-driven duration (calculateMetadata).
22. **Vintage screen**: link to the HTML-in-canvas docs, subtle convex CRT shader over an HTML terminal showing `npx create-video@latest --yes --blank my-video` and its output, then `claude` launching with a prompt. Works: doc link as the first line, scripted terminal content.
23. **BMS cell balancing**: 10 s, 30 fps, 1280 x 720 MP4; manual setup commands, tsconfig, file structure; eight cells with unbalanced voltages 3.3 to 4.05 V, phases by frame (0 to 60 idle, 60 to 90 measuring with yellow dot, 90 to 240 balancing with voltages converging by smoothstep and green pulsing dot, 240 to 300 balanced in blue); per-cell SOC fill colours, terminals, bus bars, three-decimal voltages, labels, temperature, charge and discharge borders and arrows, energy particles, shimmer; spring info panel (pack voltage, colour-coded max delta, average, config, SOC, method); legend; render command. Works: engineering-grade state machine by frame ranges. Improvement: use `npx create-video@latest --blank` rather than hand setup.
24. **Glitch effect**: "use remotion html-in-canvas best practices... apply a glitch effect". Minimal; shows the skill carries the know-how.
25. **Solar system**: Markdown spec with headings: 1920 x 1080, 30 fps, 30 s simulating one year from 2025-01-01; near-black background with 500 deterministic stars; sun radial gradient and halo; 8 planets with real periods (J2000 mean longitude), gradient spheres with glow, Saturn rings, Earth's moon (27.32 days), labels; orbit radius formula (linear to 1.6 AU, then log2 compression); no fade-in, title always visible, frosted date pill; Canvas 2D for the scene redrawn in a `useEffect` keyed on the frame, HTML overlays for crisp text; a second composition `InnerPlanets` (zoom 2.5, 3 months); clean file structure; an "Expected Result" checklist. Works: acceptance criteria and architecture decisions stated up front.

### B.2 Patterns across effective prompts
- **Two workable detail levels.** (1) Short prompt plus a strong skill plus iteration, for exploratory or effect-driven pieces (Travel Route, Glitch, Magnifying glass, 3D logo); (2) a long, numeric spec for production pieces with fixed content and brand (Launch Video, Device Rise, BMS, Solar System). Likes do not track length: the two top prompts are short, the best-specified ones sit mid-table.
- **Skill trigger first.** "use remotion best practices" (or naming a skill or a docs URL) appears in the two most-liked prompts and in most Remotion-team prompts.
- **Canvas numbers.** Width x height, fps, duration in seconds or frames, often a composition id.
- **Timeline.** Scene lists with frame counts, second ranges or "at frame 40" beats; totals add up.
- **Numbers over adjectives.** px offsets, degrees, scale ranges, spring damping, stagger seconds, hex colours, font names; adjectives only as style anchors ("Apple presentation style", "Cyberpunk/Tech-Corporate", "abstract, minimalist").
- **Named techniques and libraries.** rough.js highlighter, flubber morph, react-postprocessing glitch, tesseract OCR, typewriter at 1 char per frame, iris wipe, Ken Burns, word-by-word reveal.
- **Assets and data made explicit.** Paths in `public/`, pasted SVG or JSON, GPX files, URLs to scrape, existing recordings and end cards to reuse.
- **Layering and camera.** "marker behind the text", "camera follows the line", "zoom out while staying focused", "stop at each rank".
- **Output contract.** Codec and alpha (transparent ProRes), vertical 1080 x 1920, "render and open".
- **Process instructions.** Ask questions first; produce three versions; iterate with relative feedback; demand determinism; link docs when it fails.
- **Acceptance criteria.** "Expected Result" lists, "title must remain visible", "no fade-in on the first frame".

### B.3 Anti-patterns seen
- No canvas numbers (Kinetic Marketing, Rocket Timeline) leaves the agent guessing format and length.
- Adjective piles without values (Real Estate) produce generic results.
- Asking the agent to "analyse the uploaded video" without a video tool.
- Hand-rolled pseudo-random hashes instead of `random(seed)`; manual project scaffolding instead of `create-video`.
- Real people and brands without permission.

### B.4 Prompt skeleton for our skills (fill every line, delete what does not apply)
```text
use remotion best practices [+ skill area or docs .md link]
Canvas: <W>x<H>, <fps> fps, <seconds> s (<frames> frames), composition id "<Id>", background <hex/texture>
Story: Scene 1 (<frames> f): <what appears, copy text verbatim> / Scene 2 ... (frames add up to total)
Style: palette <hex list with roles>; fonts <family weight per role>; look <1 to 3 anchors>
Motion: entrances <easing + distance + duration>; exits <...>; stagger <frames>; transitions <type + length>; camera <path>
Assets/data: <public/ paths, URLs to fetch, pasted JSON/SVG, captions JSON>
Audio: <music file, volume, fades, SFX on which beats>
Props to expose: <list> (Zod schema, editable in Studio)
Constraints: deterministic; fonts loaded; safe zones for <platform>; <layering rules>
Output: <codec/container, alpha?, path>; render, then show me the file
Process: ask me questions first | give 3 variants | stop after scene 1 for review
Done when: <checklist of observable results>
```

---

## Appendix C. Templates catalogue

Create with `npx create-video@latest --<flag>` (or `bun create video --<flag>`, `pnpm create video --<flag>`). "Preview" = deployed Studio preview, "StackBlitz" = try online, "Tailwind" = supports Tailwind. Repo sources are in `repo/packages/template-<name>` (covered by the templates agent).

| Template | Flag | Purpose (site text, in my words) | Extras |
|---|---|---|---|
| Blank | `--blank` | only an empty canvas; recommended for experienced users and for writing the code with AI | Preview, StackBlitz, Tailwind |
| Hello World | `--hello-world` | playground with a simple animation; TypeScript, Prettier and ESLint preconfigured | Preview, StackBlitz, Tailwind |
| Next.js | `--next` | SaaS starter with Player and Lambda rendering built in; the recommended base for video-generating apps | Live demo, StackBlitz |
| Next.js (Vercel Sandbox) | `--vercel` | on-demand renders in ephemeral Linux VMs (Vercel Sandbox), output stored in Vercel Blob | Live demo |
| Recorder | `--recorder` | record webcam and screen, generate captions, add music, all in JavaScript | StackBlitz |
| Prompt to Motion Graphics SaaS Starter Kit | `--prompt-to-motion-graphics` | AI generates Remotion code, streams it to the frontend, compiles and previews it in the browser (contributed by ASchwad) | source includes `skills/` and `examples/` |
| Render Server (Express.js) | `--render-server` | Express server that starts, tracks and cancels renders | StackBlitz |
| Electron | `--electron` | Electron Forge plus Vite app rendering from the main process | |
| React Router 7 | `--react-router` | SaaS starter with Player and Lambda on React Router 7 | StackBlitz |
| React Three Fiber (3D) | `--three` | R3F scene starter | Preview, StackBlitz |
| Still images | `--still` | dynamic PNG or JPEG (social cards) with an HTTP server deployable to Heroku | Preview, StackBlitz |
| Audiogram | `--audiogram` | podcast snippets into social videos (text plus waveform) | Preview, StackBlitz, Tailwind |
| Music Visualization | `--music-visualization` | music snippets into social videos | StackBlitz, Tailwind |
| Prompt to Video | `--prompt-to-video` | story video from a prompt: script, images, voice-over via OpenAI and ElevenLabs (contributed by webmonch) | StackBlitz, Tailwind |
| Skia | `--skia` | React Native Skia preconfigured | StackBlitz |
| Overlay | `--overlay` | overlays for conventional editing software (transparent output) | StackBlitz, Tailwind |
| Code Hike | `--code-hike` | animated transitions between code snippets, many languages, TypeScript error annotations, themes | Preview, StackBlitz |
| Stargazer | `--stargazer` | celebration video of a repo's stargazers (contributed by pomber) | StackBlitz, Tailwind |
| TikTok | `--tiktok` | word-by-word animated captions for a local video; installs Whisper.cpp automatically; customisable style | StackBlitz, Tailwind |
| Editor Starter (paid) | not a flag | boilerplate for building a video editor (tracks, items, assets, undo and redo, copy and paste, cropping, fonts, uploads, cleanup, persistence, captioning, Lambda and client-side rendering, backend routes) | page empty in mirror; blog lists the docs |
| Watercolor Map (paid) | not a flag | 2D watercolor travel map; the free Element covers the core look | |
| `<Timeline />` (paid) | not a flag | copy-pasteable timeline editing component | |

Historic templates mentioned in the blog: text-to-speech and plain JavaScript (2.3), Tailwind (`--tailwind`, 3.1), Remix SaaS template (3.3). The repo also holds `template-vibe-code`, which the site does not list.

---

## Appendix D. Technical lessons from the blog (2021 to 2025)

### D.1 Determinism and parallelism
- 1.4: frames render in several browser instances, so random values must be seeded (`random(seed)`); ESLint flags `Math.random()`.
- 1.3: Puppeteer pipeline optimisations, mainly no longer reloading the page for every frame, gave a 5.5x speed-up (98 s to 18 s for a 19 s 720p video at concurrency 16); the render ran faster than real time.
- 2.4: rendering a range mounts components directly at the first frame of that range.
- 3.3: `--log=verbose` shows slowest frames; frames that crash are retried once.

### D.2 Loading and flicker
- 1.1: `<Img>` and `<IFrame>` wait for their network loads; ESLint warns about native `img`, `iframe`, `video`, `audio`; import assets instead of string paths (1.4).
- 1.5: a frame that fails (for example a delayRender never released) stops the render; renders are served from `http://localhost:3000` (next free port), so APIs can whitelist localhost for CORS.
- 2.1 and 2.2: timeouts print where the handle was created; fonts are awaited via `document.fonts.ready`; helpful errors for multiple Remotion versions, non-seekable videos (for example some cloud storage), unsupported codecs, uncleared handles.
- 3.3 and 3.1: `prefetch()` and `@remotion/preload` (`preloadVideo`, `preloadAudio`, `resolveRedirect`) make Player assets ready before they appear; media tags reuse prefetched blobs.

### D.3 Timing primitives
- 1.3: Easing works inside `interpolate()` (for example `Easing.bezier(...)`).
- 2.0: `interpolate()` accepts more than two keyframes (one-line fade in and out).
- 2.1: `interpolateColors()`; `measureSpring()` to know a spring's length.
- 3.1: `spring({durationInFrames})` stretches the curve to an exact duration without changing its character.
- 2.2: `<Freeze frame>` pauses any subtree; combine with Sequences for play, pause, continue.
- 2.3.2 and 2.5: `<Series>` lays sequences back to back; `<Loop>` repeats (shown cleanly in the timeline); `durationInFrames` on Sequence defaults to Infinity.
- 3.3: `from` on Sequence is optional; Sequence accepts `style` (when `layout` is not `"none"`) and a `ref`; AbsoluteFill accepts a `ref`.

### D.4 Media
- 2.0: audio support with per-frame volume curves mixed by FFmpeg to match the preview; `mp3`, `aac`, `wav` audio-only outputs; `@remotion/gif`.
- 2.2: `playbackRate` on video and audio (FFmpeg handles any tempo when rendering).
- 2.6: `staticFile()` and `public/`; data URLs for generated tones (`audioBufferToDataUrl()`, see the Tone.js example).
- 3.1: `<OffthreadVideo>` for reliable frame-exact video; 3.3: `loop` on video and audio.
- 3.2: `@remotion/lottie` (thousands of LottieFiles animations, After Effects export guide; `direction` prop in 3.3), `@remotion/skia`; 4.0: `@remotion/rive` (smaller and faster than Lottie), `@remotion/shapes`.
- 2.5: `@remotion/three` wraps the canvas in `<Suspense>` and delays rendering until loaded (drei `<Environment>` works); Chrome uses the ANGLE OpenGL backend for best Three.js support.

### D.5 Rendering and encoding
- 1.2: JPEG frames halve render time without visible loss; PNG remains available.
- 1.4: codecs H.264, H.265, VP8, VP9; `setCrf`, `setQuality` (JPEG), `setImageSequence`, `setImageFormat`, `setPixelFormat('yuva420p')` for transparency.
- 2.2: ProRes (with alpha, for editors) and MKV; CRF 0 disallowed for H.264 (unplayable on many platforms).
- 2.4: MP4 needs even dimensions.
- 3.1: GIF output (`--codec=gif`, `--every-nth-frame` to reach 10 to 15 fps, `--number-of-gif-loops`), `renderMedia()` can return a Buffer.
- 3.3: `--audio-bitrate`/`--video-bitrate` exist but CRF is recommended; `--height`/`--width` change layout while `--scale` only resizes; negative still frames count from the end; FFmpeg command can be overridden reducer-style; `npx remotion benchmark`.
- 4.0: Rust binary; FFmpeg 6.0 custom build baked in (no install); audio codec chosen independently of video; WebP and PDF stills.

### D.6 Data-driven videos
- 1.4: `delayRender()` in the root allowed async composition metadata (now `calculateMetadata()`, 4.0: adjust duration and size from props, fetch data before render, precompute props).
- 2.2: environment variables via `.env`, CLI and Node APIs; input props for the preview (2.2) and auto-reloading `--props` files (3.1).
- 4.0: Zod schemas make `defaultProps` type-safe and editable in Studio; edits can be saved back to code; the Render button renders a parameterised video from a form.

### D.7 Studio and developer experience
- 2.4: New Composition dialog (N), shortcut sheet (?), keyboard-only navigation, no extra dependencies.
- 2.5: In and Out markers, J K L playback, playback rates from -4x to 4x.
- 3.2 and 3.3: zoomable timeline with second and frame ticks; Cmd+K quick switcher (compositions, menu actions, docs search); pinch zoom of the canvas; `npx remotion render` needs no arguments (asks for the composition; output `out/<id>.<ext>`).
- 3.1: A and E jump to start and end; Enter returns to where playback started; built-in colour picker.
- 2024: `npx remotion bundle` exports Studio as a static site (deploy to Vercel or Netlify); share the URL with clients to tweak props; every render API and CLI command accepts that URL; clicking a sequence in the deployed Studio jumps to its source on GitHub; deploy Studio as a server (Fly.io, Render.com) to keep the Render button.

### D.8 Scale and cloud
- 3.0: Lambda splits a render into chunks rendered in parallel by the function invoking itself; ARM functions; Chromium and FFmpeg preinstalled.
- 3.2 and 3.3: ProRes on Lambda, `privacy: 'no-acl'`, `downloadBehavior`, webhooks on completion or failure, input props over 256 KB stored in S3 automatically, output to S3-compatible storage (DigitalOcean Spaces, Cloudflare R2), `deleteRender()`, defaults `imageFormat: 'jpeg'`, `privacy: 'public'`, `maxRetries: 1`.
- 4.0: 20 regions, `speculateFunctionName()`, VP9, `getCompositionsOnLambda()`, PHP and Go SDKs, Cloud Run alpha.
- 4.0.130: AAC concatenation without re-encoding (details in section 5).

### D.9 Direction of the ecosystem
- 2025: Media Parser (metadata and WebCodecs decoding) and the web converter launched, then Remotion joined forces with Mediabunny (sponsoring $1000/month). Media Parser is deprecated since 1 February 2026; `extractFrames()` and `getPartialAudioData()` move to Mediabunny; a faster `<Video>` tag and in-browser rendering are built on it.
- Seed round 2022 (CHF 180k from users): the plan was higher-level components, templates and UI elements for non-experts, which the 2026 Elements gallery now delivers.

### D.10 Renames to remember
`src/Video.tsx` to `src/Root.tsx` and `RemotionVideo` to `RemotionRoot` (3.3); Preview to Studio (4.0); `<Video>`/`<Audio>` from `remotion` to `<Html5Video>`/`<Html5Audio>` (with `@remotion/media` as the new default); `startFrom`/`endAt` to `trimBefore`/`trimAfter` (4.0.319); `npm init video` or `yarn create video` to `npx create-video@latest`; `npm run build` to `npx remotion render`; FFmpeg install steps and `ensureFfmpeg()` to nothing (baked in).

---

## Appendix E. Community signals (experts, success stories, showcase, product pages)

- Typical commercial uses: AI short-form tools (Submagic reached $1M ARR three months after launch in 2023; Revid.ai $1M ARR in 15 months; Crayo about $6M per year with story videos; AIVideo.com $1M per year), product intro videos from text (Typeframes: Player for live preview, Lambda for rendering, watermark on a free plan), web stories to MP4 (MakeStories: up to ten slides rendered within a minute), event and conference assets (Shortvid.io: open-source templates, also used on venue screens), personalised sports finisher videos (YARX: C# backend launching many VMs that call Remotion, replacing FFmpeg-only overlays), GitHub Unwrapped (personalised year in review with the Player).
- Expert profiles describe pipelines close to ours: TTS (self-hosted viXTTS) plus Gemini image generation plus SRT-driven subtitle timing plus Ken Burns presets plus cross-dissolves plus a spectrum, turning a book into a video in about an hour (Hai Nguyen); AI editors with Gemini highlight detection and Deepgram captions (Pablito Silva); custom explainer pipelines with brand-guided component systems (Amir Tadrisi); `remotion-sst` for deploying Lambda with SST (Karel Nagel); `remotion-animate-text` (Pramod Kumar); `@remotion/cloudrun` author (Matt McGillivray); `@remotion/player` and Lambda co-author (Shankhadeep Dey).
- Showcase submission rules (useful as a quality bar): title up to 80 characters without emojis or caps, description up to 280 characters about how Remotion was used, optional links (video, source, website, tutorial), no overly simple or duplicate videos, only your best work.
- `@remotion/design` (the `/design` page) is Remotion's own React UI kit (Button variants, Counter, Switch, Slider, Card, Select, Tabs, Input, Textarea, InlineCode, Link) used for its web properties; source in `repo/packages/design`. Useful if we build Remotion-branded editor UIs, not for video frames.
- `/explore_section` lists the capability map the site promotes: video, audio, captions, AI, parameterization, rendering, effects, transitions, Elements, colour correction, keyframes, background removal, fonts, integrations, Editor Starter, Convert.
