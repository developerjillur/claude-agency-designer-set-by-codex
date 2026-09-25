# D6-graphics-text: transitions, paths, shapes, hand-drawn notation, text layout, fonts, vector animation players, styling

Knowledge file for the Remotion skill family. Target runtime: Remotion 4.0.528 (React 19). The docs mirror and the monorepo
snapshot track 4.0.529, so every API below carries its "since" version and a note when it is newer than 4.0.528 or changes in v5.

---

## 1. Scope and coverage

### Docs pages read in full: 121 of 121 (list in `kb/D6-graphics-text.coverage.txt`)

| Package / area | Pages |
|---|---|
| `@remotion/transitions` (TransitionSeries, timings, 23 presentation pages, custom + HTML-in-canvas presentations, audio, progress hook) | 32 |
| `@remotion/paths` | 22 |
| `@remotion/shapes` (11 components + 11 `make*()` functions) | 22 |
| `@remotion/rough-notation` | 8 |
| `@remotion/layout-utils` | 6 |
| `@remotion/lottie` | 5 |
| `@remotion/google-fonts` | 6 |
| `@remotion/gif` | 3 |
| `@remotion/animated-emoji` | 2 |
| `@remotion/rive`, `@remotion/rounded-text-box`, `@remotion/fonts`, `@remotion/gsap`, `@remotion/mac-cursors` | 1 each (5) |
| Tailwind v3 (2), Tailwind v4 (2), enable-scss (2), zod-types (4) | 10 |

### Source folders read (to confirm props, defaults, behaviour)

- `repo/packages/transitions/src`: `TransitionSeries.tsx`, `context.tsx`, `flatten-children.ts`, `html-in-canvas-presentation.tsx`,
  `index.ts`, `types.ts`, `use-transition-progress.ts`, `validate.ts`, `timings/linear-timing.ts`, `timings/spring-timing.ts`, and
  in full the CSS presentations `fade`, `slide`, `none`, `wipe`, `flip`, `clock-wipe`, `iris`, `push-cut`, plus `blur-slide.tsx`
  and `upload-element-image.ts`. For `book-flip`, `cross-zoom`, `crosswarp`, `dissolve`, `dreamy-zoom`, `film-burn`,
  `linear-blur`, `ripple`, `swap`, `zoom-blur`, `zoom-in-out` I read the props types, defaults, time convention and wiring
  (GLSL bodies skimmed). Tests: `with-premounting.test.tsx` (partly), file list of the rest.
- `repo/packages/paths/src`: `index.ts`, `evolve-path`, `get-length`, `get-point-at-length`, `get-tangent-at-length`, `cut-path`,
  `center-path`, `reset-path`, `reduce-instructions`, `get-subpaths`, `extend-viewbox`, `interpolate-path/interpolate-path.ts`,
  `interpolate-path/interpolate-instructions.ts`, `interpolate-paths.ts`, `scale-path.ts`, `warp-path/index.ts`, `debug-path.ts`,
  `get-bounding-box.ts` (result shape), `get-instruction-index-at-length.ts`, `serialize-instructions.ts` (head),
  `parse-path.ts` (error paths), `helpers/types.ts`, `translate-path.ts` (head), `test/scale-path.test.ts`. The math helpers
  (`construct`, `bezier*`, `arc`) are ports of svg-path-properties and were not read line by line.
- `repo/packages/shapes/src`: `index.ts`, `components/render-svg.tsx`, `components/star.tsx`, `components/schema.ts`,
  `utils/shape-info.ts`, `make-rect`, `make-circle`, `make-ellipse`, `make-arrow`, `make-callout`, `make-pie`, `make-heart`
  (full), `make-polygon`, `make-star`, `make-triangle`, `make-spark` (options, defaults, validation), `join-points` (validation).
- `repo/packages/rough-notation/src`: all 7 non-test files in full.
- `repo/packages/layout-utils/src`: all 4 layout files plus the tests and both fixtures.
- `repo/packages/rounded-text-box/src`: both files in full.

### Verified against the installed 4.0.528 packages (read only)

the shared modules (`remotion-broll/node_modules`)/@remotion/*` (paths, shapes,
transitions, rough-notation, layout-utils, google-fonts, tailwind-v4, zod-types all at 4.0.528) and `remotion` core 4.0.528:
- `@remotion/paths` 4.0.528 has NO `interpolatePaths` (docs: since 4.0.529) and `getPointAtLength()` already returns `null`
  past the end (docs claim that only happens from v5).
- `@remotion/transitions` 4.0.528 exports every presentation listed in section 3.1 (subpaths `./fade` ... `./blur-slide`) and
  `TransitionSeries.Sequence` has an `offset` prop.
- Shapes components in 4.0.528 accept `effects`, `pathStyle`, `debug`, `pixelDensity` and Sequence timing props.
- `remotion` 4.0.528 has `Interactive.Div/Span/Svg/Path`, `Easing.spring()`, `useDelayRender()`, `HtmlInCanvas`, and
  `AbsoluteFill` accepts `from`, `durationInFrames`, `premountFor` etc. directly.
- `@remotion/google-fonts` 4.0.528 has `loadVariableFont` for variable families (Inter, NotoSans) and `/from-info`.

### Also consulted for context (not in the assignment)

`mirror/docs/html-in-canvas.md` (Limitations and Rendering sections), version/install lines of `mirror/docs/rounded-text-box.md`,
`gsap.md`, `lottie.md`, `rive.md`; example repos `examples/text-warping`, `examples/morph-text`, `examples/typewriter`,
`examples/transitions-video/src/TextMask.tsx`, `examples/light-leak-example/src/presentation.tsx`; monorepo examples
`repo/packages/example/src/{TikTokTextbox,Title,VariableGoogleFont,GoogleFontsCjk,Paths,TransitionRounding.tsx,PremountOnTransitionSeries.tsx}`
and `repo/packages/brand/src/effects/RoughNotationShowcase.tsx`; installed skill rules
`~/.claude/skills/remotion-markup/{transitions,text-highlights,measuring-text,google-fonts,lottie}.md` (to spot gaps).

### Not readable

Several doc pages render their prop tables through MDX components that carry no text in the mirror: `<ShapeOptions>`,
`<MakeShapeReturnType>`, `<ShapeSeeAlso>` (all shapes pages), `<Presentations>`, `<Timings>`, `<TableOfContents>`,
`<AvailableEmoji>`, `<AvailableFonts>`, `<MacOSCursorTable>` and every `<Demo>`. Shape props and defaults were recovered from
source instead. The names of the 39 macOS cursors and the animated emoji list are not in the mirror (use
`getAvailableEmojis()` at runtime; cursor names are CSS cursor keywords).

---

## 2. Mental model

1. **Everything is a pure function of the frame.** Every package here either takes a progress/frame input (paths, shapes,
   rough-notation `progress`, `interpolate`-driven styles) or seeks a third-party player to the current frame (Lottie, Rive, GIF,
   GSAP, animated emoji). Nothing may run on wall-clock time, callbacks or `Math.random()`. `useGsapTimeline()` enforces this with
   runtime errors; the other packages assume it.
2. **A transition = timing x presentation.** `<TransitionSeries>` is `<Series>` whose neighbouring scenes can overlap. The timing
   (`linearTiming`, `springTiming`, custom) decides the overlap length (`getDurationInFrames({fps})`) and a 0 to 1 progress
   curve; the presentation is a wrapper component that receives `presentationProgress` and `presentationDirection`
   (`'entering' | 'exiting'`) and styles its children. Total length = sum of sequences minus sum of transitions. Overlays
   (`<TransitionSeries.Overlay>`, 4.0.415) sit on the cut without shortening anything.
3. **Two engines for presentations.** CSS presentations (`fade`, `slide`, `wipe`, `flip`, `clockWipe`, `iris`, `none`,
   `pushCut`, custom CSS/SVG) work everywhere. Shader presentations (`zoomBlur`, `zoomInOut`, `dissolve`, `ripple`, `bookFlip`,
   `crosswarp`, `dreamyZoom`, `linearBlur`, `swap`, `crossZoom`, `filmBurn`, `blurSlide`, custom via
   `makeHtmlInCanvasPresentation`) rasterize both scenes with the experimental HTML-in-canvas API and blend them in WebGL2:
   Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element`; renders work from 4.0.455 with Remotion's bundled
   Chrome but need `--gl=angle` (or `swangle` without GPU). Prefer CSS; use shaders for looks CSS cannot do.
4. **Nesting order of presentations.** When a sequence has a transition on both sides, the presentation of the NEXT transition
   (direction `exiting`) wraps the presentation of the PREVIOUS transition (direction `entering`), which wraps the scene. Only
   the entering scene is clipped in mask presentations (`clockWipe`, `iris`, custom star); the exiting scene is left untouched
   underneath. `fade()` only fades the incoming scene in, so a semi-transparent incoming scene shows the old one through.
5. **SVG path pipeline.** Create a `d` string (`@remotion/shapes` `make*()`, a design tool, or glyphs via opentype.js) ->
   normalise (`parsePath`, `normalizePath`, `reduceInstructions` gives only `M L C Z`) -> place (`resetPath`, `centerPath`,
   `translatePath`, `scalePath`, `warpPath`, `getBoundingBox` for the viewBox) -> animate (`evolvePath` for draw-on,
   `cutPath`, `interpolatePath` morph, `getPointAtLength`/`getTangentAtLength` for motion along a path) -> render as `<path>`,
   as a CSS `clip-path: path("...")` mask, or as an SVG `<clipPath>`.
6. **Shapes are SVG components with timeline powers.** Each `<Rect>`, `<Star>` etc. renders `<svg width height viewBox="0 0 w h"
   style="overflow: visible">` with one `<path>`; extra props go to the `<path>` (fill, stroke, strokeDasharray...), `style`
   goes to the `<svg>`, `pathStyle` to the `<path>`. In 4.0.528 they are also Studio-editable and accept Sequence props (`from`,
   `durationInFrames`, `premountFor`...) and GPU `effects` (renders through `<HtmlInCanvas>`).
7. **Text layout is measured, not guessed.** `@remotion/layout-utils` measures text in the browser DOM (a hidden
   `inline-block`, `white-space: pre` span). It is only correct after the font has loaded and when every font property matches
   the rendered text. Measurements are cached for the page lifetime. The winning pattern: load font -> `fitTextOnNLines()` ->
   render the returned `lines` explicitly with `white-space: pre` -> optionally `measureText()` each line ->
   `createRoundedTextBox()` for TikTok/Instagram-style caption plates.
8. **Fonts block the render.** `@remotion/google-fonts` `loadFont()` and `@remotion/fonts` `loadFont()` wrap loading in
   `delayRender()`. Load only the weights, styles and subsets you use (in 4.0 a bare `loadFont()` loads everything and can time
   out; in v5 it throws). Variable fonts (4.0.525) let you animate `fontWeight` (and other axes) continuously.
9. **Hand-drawn annotations are measured overlays.** `@remotion/rough-notation` (4.0.490) wraps text in an inline-block span,
   measures it with `offsetLeft/offsetWidth`, generates seeded Rough.js strokes and reveals them with `evolvePath()` driven by
   your `progress` prop. `<Highlight>` sits behind the text; all others draw on top.
10. **Version gates matter.** On 4.0.528: no `interpolatePaths()` (4.0.529); everything else in this file exists. `blurSlide`
    (4.0.523), variable fonts (4.0.525), GSAP (4.0.517), mac cursors (4.0.513), push cut (4.0.500), rough-notation (4.0.490),
    Sequence props on `<Lottie>` and premount props on rough-notation, Rive and `<MacOSCursor>` (all 4.0.528) are recent: do
    not assume older projects have them.

---

## 3. API digest

### 3.1 `@remotion/transitions` (package 4.0.53, `<TransitionSeries>` 4.0.59)

Install: `npx remotion add @remotion/transitions`. Presentations are subpath imports (`@remotion/transitions/fade` ...);
`blurSlide`, `crossZoom`, `dreamyZoom`, `filmBurn`, `linearBlur`, `pushCut` are also exported from the root in 4.0.528.

#### `<TransitionSeries>`
- Inherits `from`, `playbackRate`, `name`, `className`, `style` from `<Sequence>` (source also passes `freeze`, `hidden`,
  `showInTimeline`). Default `layout` is `absolute-fill`; `layout="none"` is deprecated and throws in v5. Default name
  `<TransitionSeries>`.
- Children may only be `.Sequence`, `.Transition`, `.Overlay` (React Fragments are flattened, whitespace strings ignored). A
  custom wrapper component around `.Sequence` is NOT recognised and throws; map arrays directly inside the series.

#### `<TransitionSeries.Sequence>`
- Props: `durationInFrames` (floats allowed), `offset?` (integer, shifts like `Series.Sequence` offset; undocumented but typed in
  4.0.528), `name`, `className`, `style`, `layout`, `showInTimeline`, `freeze`, `hidden`, `playbackRate`, `premountFor`,
  `postmountFor`, `trimBefore` (4.0.497).
- Must be at least as long as the transition before it and the transition after it (checked separately, so a sequence can be
  shorter than in+out combined; then both presentations overlap inside it).

#### `<TransitionSeries.Transition>`
- `timing: TransitionTiming` (required), `presentation?: TransitionPresentation` (default `slide()` = from-left).
- Both scenes render during the transition; total duration shrinks by the transition length.
- Put one first or last in the series to animate a single scene in or out (enter/exit animation without a second scene).

#### `<TransitionSeries.Overlay>` (4.0.415)
- `durationInFrames` (positive integer), `offset?` (integer, default 0, positive = later). Centred on the cut: half before, half
  after. Does not change timing. Children get no progress context (drive them with `useCurrentFrame()`, which starts at 0 at
  overlay start). Rendered in a `<Sequence>` named `<TS.Overlay>`.
- Must not start before frame 0 or reach beyond the previous/next sequence.

#### Rules (thrown as errors)
1. A transition must not be longer than the previous or the next sequence.
2. No two transitions adjacent. 3. No two overlays adjacent. 4. A transition and an overlay cannot be adjacent (same slot).
5. At least one sequence before or after every transition/overlay.

#### Duration math
`total = sum(sequence durations) - sum(transition durations)`; overlays add 0. Example 40 + 60 + 90 with transitions 30 and 45 =
115. `timing.getDurationInFrames({fps})` gives the overlap; `springTiming({config: {damping: 200}}).getDurationInFrames({fps: 30})`
is 23.

#### Timings
| Timing | Signature | Notes |
|---|---|---|
| `linearTiming()` | `{durationInFrames: number, easing?: (t) => number}` | `interpolate(frame, [0, d], [0, 1], {easing, clamp both})`. Pass `Easing.bezier(...)`, `Easing.inOut(Easing.cubic)` etc. |
| `springTiming()` | `{config?: Partial<SpringConfig>, durationInFrames?, durationRestThreshold? = 0.005, reverse? (4.0.144)}` | Duration = `durationInFrames` if set, else `measureSpring({config, threshold, fps})` (so it depends on fps). Default threshold cuts the last 0.5 percent visibly: use `durationRestThreshold: 0.001` (the custom-presentation doc even uses `0.0001`). `reverse: true` still goes 0 to 1 but with the time-reversed curve (slow start, fast finish). |
| custom | `{getDurationInFrames: ({fps}) => number, getProgress: ({frame, fps}) => number}` | Duration must be deterministic. Springs go 0 to 1 so they can be added (for example two half springs with a pause). |

#### `useTransitionProgress()` (4.0.177)
Returns `{entering, exiting, isInTransitionSeries}`. Inside a sequence that is entering: `entering` goes 0 to 1; exiting scene:
`exiting` goes 0 to 1; outside any transition: `entering = 1`, `exiting = 0`, `isInTransitionSeries = false`. Designed for
`none()` so you can animate individual elements of each scene (stagger titles out, fly cards in) instead of the whole frame.

#### Presentations

CSS presentations (work in Chrome, Firefox, Safari, Player, SSR):

| Function (import) | Since | Options and defaults | Behaviour |
|---|---|---|---|
| `fade()` (`/fade`) | 4.0.53 | `enterStyle?`, `exitStyle?` (4.0.84), `shouldFadeOutExitingScene? = false` (4.0.166) | Incoming opacity = progress; outgoing stays at 1 unless the flag is set. Styles are spread after opacity, so they can override it. Needs an opaque incoming scene. |
| `slide()` (`/slide`) | 4.0.53 | `direction? = 'from-left'` (`from-left`, `from-right`, `from-top`, `from-bottom`), `enterStyle?`, `exitStyle?` (4.0.84) | Incoming pushes the outgoing out with `translateX/Y(%)`; 0.01 percent overlap hides the seam. Default presentation of every Transition. |
| `wipe()` (`/wipe`) | 4.0.53 | `direction? = 'from-left'` (adds `from-top-left`, `from-top-right`, `from-bottom-right`, `from-bottom-left`), `outerEnterStyle?`, `outerExitStyle?`, `innerEnterStyle?`, `innerExitStyle?` (4.0.84) | `clip-path: polygon()` reveal of the incoming, matching hide of the outgoing; diagonals move at 2x. |
| `flip()` (`/flip`) | 4.0.54 | `direction? = 'from-left'`, `perspective? = 1000`, outer/inner enter/exit styles | `rotateY` (or `rotateX` for top/bottom) 180 degrees with `backface-visibility: hidden`, `transform-style: preserve-3d`. Not supported in client-side rendering. |
| `clockWipe()` (`/clock-wipe`) | 4.0.74 | `width`, `height` (required: pass `useVideoConfig()` values), outer/inner styles | Incoming clipped by `clip-path: path()` of `makePie()` sized to the frame diagonal, sweeping clockwise from 12 o'clock. |
| `iris()` (`/iris`) | 4.0.316 | `width`, `height` (required), outer/inner styles | Circle mask from the centre (radius 0 to half diagonal). |
| `none()` (`/none`) | 4.0.177 | docs: no options; source also accepts `enterStyle?`, `exitStyle?` | No visual; use `useTransitionProgress()`. |
| `pushCut()` (`/push-cut`) | 4.0.500 | `cutProgress? = 5/11` (0 < x < 1), `outgoingScale? = 1.04`, `incomingStartScale? = 1.04`, `incomingEndScale? = 1.07` (all > 0), `transformOrigin? = '50% 50%'`, `flashColor? = '#f5f2ed'`, `flashOpacity? = 0.2` (0..1), `flashFrames? = 2` (>= 0), outer/inner enter/exit styles | Editorial hard cut: outgoing punches in (ease-in quad) until the cut, incoming is invisible until `cutProgress`, then eases out (quad) from 1.04 to 1.07; a flash peaks at the cut. Use a monotonic timing (linear). The incoming scene's clock already runs while hidden: delay its content by the pre-cut frames (`<AbsoluteFill from={5}>` or `<Sequence from={5}>`) and lengthen that sequence by the same amount. Docs example: 11-frame transition, 5 pre-cut frames. |
| `cube()` (`@remotion-dev/cube-presentation`, paid at remotion.pro) | n/a | `direction`, `perspective? = 1000` | 3D cube rotation of both scenes. No client-side rendering. |

Shader presentations (HTML-in-canvas + WebGL2; Chrome only; `firefox`/`safari` false in compat tables). Every one also accepts
an undocumented `effects?: EffectsProp` (applied to the shader output by `makeHtmlInCanvasPresentation`). The TypeScript
signature of all except `blurSlide` requires an options object: write `dissolve({})`, not `dissolve()` (at runtime
`TransitionSeries` falls back to `{}`, so only the type check fails).

| Function (import) | Since | Options and defaults | Look |
|---|---|---|---|
| `zoomBlur()` (`/zoom-blur`) | 4.0.456 | `rotation? = Math.PI / 6` (radians; out: 0 to -rotation, in: +rotation to 0) | Outgoing zooms out and rotates, incoming zooms in from the opposite angle, radial blur. |
| `zoomInOut()` (`/zoom-in-out`) | 4.0.457 | none (pass `{}`) | Zoom toward the viewer, crossfade, zoom back out. |
| `dissolve()` (`/dissolve`) | 4.0.465 | `lineWidth? = 0.1`, `spreadColor? = '#ff0000'`, `hotColor? = '#e6e633'` (hex `#rrggbb`), `pow? = 5.0`, `intensity? = 1.0` | Luminance-threshold burn with a glowing edge. |
| `ripple()` (`/ripple`) | 4.0.465 | `amplitude? = 100` (ring frequency), `speed? = 50` | Sine ripple from the centre while crossfading. |
| `bookFlip()` (`/book-flip`) | 4.0.466 | `direction? = 'from-right'` (4 directions) | Shaded page turn. |
| `crosswarp()` (`/crosswarp`) | 4.0.466 | none (pass `{}`) | Scenes warp against each other along x. |
| `dreamyZoom()` (`/dreamy-zoom`) | 4.0.466 | `rotation? = 6` (DEGREES), `scale? = 1.2` | Zoom + rotate through a white flash. |
| `linearBlur()` (`/linear-blur`) | 4.0.466 | `intensity? = 0.1` | Directional 6x6-sample blur while blending. |
| `swap()` (`/swap`) | 4.0.466 | `reflection? = 0.4`, `perspective? = 0.2`, `depth? = 3` | Scenes swap in perspective with a floor reflection. |
| `crossZoom()` (`/cross-zoom`) | 4.0.467 | `strength? = 0.4` | Zoom across a moving centre with weighted blur. |
| `filmBurn()` (`/film-burn`) | 4.0.467 | `seed? = 2.31` | Procedural film-burn glow + radial blur. |
| `blurSlide()` (`/blur-slide`) | 4.0.523 | `direction? = 'from-left'`, `blur? = 0.5` (max motion-blur length as a fraction of the frame along the slide axis, >= 0) | Whip pan: both scenes travel with a two-pass 32x32-tap box blur; slide eased internally with a quintic smootherstep, so use `linearTiming()`; blur peaks at mid-transition. Validates direction and blur. |

Credits: most shaders are MIT ports from gl-transitions.com.

Exported types worth knowing: `TransitionPresentation`, `TransitionPresentationComponentProps`, `TransitionTiming`,
`TransitionSeriesOverlayProps`, `TransitionState` (root), `SlideDirection` (`/slide`), `WipeDirection` (`/wipe`),
`FlipDirection` (`/flip`), `BlurSlideDirection`/`BlurSlideProps`, `PushCutProps`, `CrossZoomProps`, `DreamyZoomProps`,
`FilmBurnProps`, `LinearBlurProps` (root), `CubeDirection` (paid package), `HtmlInCanvasShader`, `HtmlInCanvasShaderDraw`,
`HtmlInCanvasShaderDrawParams` (root).

#### Custom presentations (CSS/SVG path)
`TransitionPresentation<P> = {component, props}`. The component receives `TransitionPresentationComponentProps<P>`:
`children`, `presentationDirection`, `presentationProgress` (0..1 after timing), `presentationDurationInFrames` (4.0.153),
`passedProps: P`, plus internal `onElementImage`, `onUnmount`, `bothEnteringAndExiting` (used by the HTML-in-canvas machinery;
ignore them in CSS presentations). Return `<AbsoluteFill>` wrappers. Pattern from the docs: star mask =
`makeStar()` sized to the frame diagonal * progress, centred with `getBoundingBox()` + `translatePath()`, applied as a
`clipPath` only when entering.

```tsx
const Circle: React.FC<TransitionPresentationComponentProps<{w: number; h: number}>> = ({children, presentationDirection, presentationProgress: p, passedProps: {w, h}}) => {
  const r = (Math.hypot(w, h) / 2) * p;
  const d = translatePath(makeCircle({radius: r}).path, w / 2 - r, h / 2 - r);
  return <AbsoluteFill style={{clipPath: presentationDirection === 'entering' ? `path("${d}")` : undefined}}>{children}</AbsoluteFill>;
};
export const circleReveal = (props: {w: number; h: number}): TransitionPresentation<{w: number; h: number}> => ({component: Circle, props});
```

#### `makeHtmlInCanvasPresentation(shader)` (4.0.456)
- `shader: HtmlInCanvasShader<Props> = (canvas: OffscreenCanvas) => {clear(), cleanup(), draw(params)}`. Create the WebGL2
  context once (`canvas.getContext('webgl2', {premultipliedAlpha: true})`), compile programs and textures up front.
- `draw({prevImage, nextImage, width, height, time, passedProps})`: `prevImage`/`nextImage` are `OffscreenCanvas | null`
  (upload with `gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image)`). `time = 1` means show the
  exiting scene fully (start), `time = 0` the entering scene (end). If `!prevImage` force `time = 0`, if `!nextImage` force
  `time = 1`. `clear()` runs when nothing is mounted; `cleanup()` once on unmount (delete programs, textures, buffers).
- Returns `(props: Props & {effects?}) => TransitionPresentation`. Each paint is wrapped in `delayRender('onPaint')`, and the
  shader output goes through the effect chain. It throws `HTML_IN_CANVAS_UNSUPPORTED_MESSAGE` where the API is missing.
- Porting a gl-transitions shader: replace `getFromColor(uv)` with `texture(u_prev, uv)` and `getToColor(uv)` with
  `texture(u_next, uv)`; add `float progress = 1.0 - u_time;`; wrap as `void main() { outColor = transition(v_uv); }` with
  `out vec4 outColor;`. Standard vertex shader flips v: `v_uv = vec2(a_pos.x * 0.5 + 0.5, 0.5 - a_pos.y * 0.5)`.
- Use `CLAMP_TO_EDGE` texture wrap unless the effect needs wrap-around (blur-slide uses `REPEAT`).

#### Sound on transitions (works from 4.0.58)
Wrap any presentation: clone `{component, ...rest}`, render `<Audio src={...} />` (from `@remotion/media`) only when
`presentationDirection === 'entering'`, then the original component. Result is used like any presentation
(`addSound(slide(), staticFile('whoosh.mp3'))`). Adjust volume/offset on the `<Audio>`.

### 3.2 `@remotion/paths` (pure functions, all environments incl. Node)

Install `npx remotion add @remotion/paths`. All functions throw `Malformed path data` (or similar) on invalid input.

| Function | Signature -> return | Since | Notes and gotchas |
|---|---|---|---|
| `getLength(d)` | -> `number` | 3.x | svg-path-properties port. Parses on every call: memoize. |
| `getPointAtLength(d, len)` | -> `{x, y} \| null` | 3.x | Returns `null` if `len > getLength(d)`. Docs say this is v5 behaviour and 4.0 returned the end point, but the installed 4.0.528 already returns `null`: always clamp `Math.min(len, total)` and handle `null`. |
| `getTangentAtLength(d, len)` | -> `{x, y} \| null` | 3.x | Unit tangent; same `null` rule. Rotation angle = `Math.atan2(t.y, t.x)`. |
| `getInstructionIndexAtLength(d, len)` | -> `{index, lengthIntoInstruction}` | 4.0.84 | Throws if `len` > total length. Pair with `parsePath(d)[index]`. |
| `evolvePath(progress, d)` | -> `{strokeDasharray: string, strokeDashoffset: number}` | 3.x | Draw-on effect: spread onto `<path>`. At `progress = 0` it uses 1.5x length to avoid a rounding dot. >1 starts erasing from the start; <0 draws from the end. Needs a stroke (not fill). |
| `cutPath(d, length)` | -> `string` | 4.0.x (no marker) | Portion from the start to `length`; > total returns the whole path; 0 returns only the `M`. Output is reduced (M/L/C/Z). Use to grow filled shapes or to attach an arrowhead at the tip. |
| `interpolatePath(t, a, b)` | -> `string` | 3.x | Morph (d3-interpolate-path port). `t = 0` returns `a`, `t = 1` returns `b` verbatim. Both reduced to M/L/C; the shorter one is extended; `Z` kept only if both end with `Z`. Values outside 0..1 extrapolate. Best with single closed subpaths of similar winding. |
| `interpolatePaths(input, inputRange, outputRange, options?)` | -> `string` | 4.0.529 (NOT in 4.0.528) | Multi-keyframe morph with `interpolate()` semantics: `easing` (one fn or one per segment, supports `Easing.spring()`), `extrapolateLeft/Right` = `'extend'` (default) / `'clamp'` / `'wrap'`, `posterize` (step every n frames). Throws `Cannot interpolate SVG paths with different subpath structures`. Pairs with `<Interactive.Path d={...}>` for Studio keyframe editing. |
| `getBoundingBox(d)` | -> `{x1, y1, x2, y2, width, height, viewBox}` | 3.3.40 (`width/height/viewBox` 3.3.97) | Tight box including curve extrema. `viewBox` string ready for `<svg viewBox>`. Type `BoundingBox`. |
| `resetPath(d)` | -> `string` | 3.3.40 | Moves bbox top-left to 0,0. |
| `centerPath(d, target? = {x: 0, y: 0})` | -> `string` | 4.0.486 | Moves the bbox centre to `target`. Type `CenterPathTarget`. |
| `translatePath(d, x, y)` | -> `string` | 3.x | Docs example 1 shows unchanged output: a docs typo (it really moves). Relative commands are left as is (they move with their anchor). |
| `scalePath(d, xScale, yScale)` | -> `string` | 3.3.43 | Scales around the bbox TOP-LEFT (it zeroes, scales, moves back). Output is reduced. For centre scaling: `centerPath` to 0,0, scale, `centerPath` back. |
| `warpPath(d, fn, {interpolationThreshold?})` | -> `string` | 3.3.43 | Subdivides the path until segments are shorter than the threshold (default `max(bboxW, bboxH) * 0.01`) and maps every point through `fn: WarpPathFn = ({x, y}) => ({x, y})`. Output is much longer. WarpJS port. |
| `getSubpaths(d)` | -> `string[]` | 3.3.6 | Splits at each `M`/`m` (relative `m` converted to `M`). `getParts()` was removed in v4. |
| `normalizePath(d)` | -> `string` | 3.x | Relative -> absolute. |
| `reversePath(d)` | -> `string` | 3.x | Swaps start and end (draw a stroke from the other end with `evolvePath`). |
| `parsePath(d)` | -> `Instruction[]` | 3.3.40 | Typed union of `M L H V C S Q T A m l h v c s q t a Z z` objects (fields `x, y, cp1x...`, relative ones `dx, dy...`). |
| `serializeInstructions(instructions)` | -> `string` | 3.3.40 | Inverse of `parsePath`; does not validate. |
| `reduceInstructions(instructions)` | -> `ReducedInstruction[]` | 3.3.40 | Only `M`, `L`, `C`, `Z` (Q converted to C; the pre-4.0.168 note in the docs is about Q handling). |
| `extendViewBox(viewBox, scale)` | -> `string` | 3.2.25 | `"0 0 1000 1000", 2` -> `"-500 -500 2000 2000"`; usually `style={{overflow: 'visible'}}` on the `<svg>` is simpler. |
| `PathInternals.debugPath(d)` | -> `{d, color}[]` | internal | Small squares at every vertex (blue = M, green = others, red = last) for debugging morphs. |

### 3.3 `@remotion/shapes`

Install `npx remotion add @remotion/shapes`. Every shape has a component `<X />` and a pure `makeX()` returning
`ShapeInfo = {path, width, height, transformOrigin: 'x y', instructions: Instruction[]}`.

Props common to all components (`AllShapesProps`, 4.0.528):
- Any SVG `<path>` attribute except `width`, `height`, `d`, `hidden`, `name` (`fill`, `stroke`, `strokeWidth`, `strokeLinecap`,
  `strokeLinejoin`, `strokeDasharray`, `strokeDashoffset`, `opacity`, `filter`...). No fill set = SVG default black.
- `style` -> applied to the `<svg>` (merged with `overflow: visible`). `pathStyle` -> applied to the `<path>` (merged after
  `transformBox: 'fill-box'`; the path's `transform-origin` is the shape's centre, so `pathStyle={{transform: 'rotate(20deg)'}}`
  rotates around the centre).
- `debug?: boolean`: draws Bezier control handles.
- `effects?: EffectsProp` + `pixelDensity?`: renders the SVG inside `<HtmlInCanvas>` with GPU effects (Chrome flag in preview).
- Sequence/timeline props: `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`,
  `showInTimeline`, `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted` (outside a composition,
  e.g. in a plain React app, the bare `<svg>` is returned).
- The Studio schema default `fill: '#0b84ff'` only seeds the visual editor; it is not a runtime default.

| Shape | Options (defaults) | Size / transformOrigin | Notes |
|---|---|---|---|
| `Rect` / `makeRect` | `width`, `height`, `edgeRoundness? = null`, `cornerRadius? = 0` | w x h, centre | `cornerRadius` = arc rounding like `border-radius`; `edgeRoundness` = Bezier bulge of edges (squircle-ish). Using both throws. |
| `Circle` / `makeCircle` | `radius` | 2r x 2r | Two relative arcs, starts at the top. |
| `Ellipse` / `makeEllipse` | `rx`, `ry` | 2rx x 2ry | |
| `Triangle` / `makeTriangle` | `length`, `direction = 'right'` (`right`, `left`, `up`, `down`), `edgeRoundness? = null`, `cornerRadius? = 0` | equilateral; for right: 86.6 x 100 with length 100 | transformOrigin is the centroid ('28.87 50' for right). |
| `Star` / `makeStar` | `points`, `innerRadius`, `outerRadius`, `edgeRoundness? = null`, `cornerRadius? = 0` | 2 * max radius | Studio defaults 5 / 50 / 100. |
| `Polygon` / `makePolygon` | `points` (>= 3, else throws), `radius`, `edgeRoundness? = null`, `cornerRadius? = 0` | 2r | cornerRadius uses Bezier strategy for polygons. |
| `Pie` / `makePie` | `radius`, `progress` (clamped 0..1), `closePath? = true`, `counterClockwise? = false`, `rotation? = 0` (radians) | 2r | Starts at 12 o'clock, clockwise. `closePath: false` = open arc (progress rings with `stroke`, `fill="none"`). |
| `Arrow` / `makeArrow` | `length? = 300`, `headWidth? = 185`, `headLength? = 120`, `shaftWidth? = 80`, `direction? = 'right'` (`left`, `up`, `down`), `cornerRadius? = 0` | length x headWidth (swapped for up/down) | Throws unless all > 0, `headWidth >= shaftWidth`, `headLength <= length`. A filled block arrow, not a line. |
| `Callout` / `makeCallout` | `width? = 500`, `height? = 200`, `pointerLength? = 40`, `pointerBaseWidth? = 60`, `pointerPosition? = 0.5` (0..1 along the side), `pointerDirection? = 'down'` (`up`, `left`, `right`), `edgeRoundness? = null`, `cornerRadius? = 0` | returned size includes the pointer (500 x 240 for down); transformOrigin = body centre | Speech bubble. |
| `Heart` / `makeHeart` (4.0.315) | `height`, `aspectRatio? = 1.1`, `bottomRoundnessAdjustment? = 0`, `depthAdjustment? = 0` | width = height * aspectRatio | Docs example output (200 x 160) is stale. |
| `Spark` / `makeSpark` | `width`, `height`, `edgeRoundness? = 1`, `cornerRadius? = 0` | w x h | Four-point sparkle; `edgeRoundness` controls how concave the sides are. |

`Arrow` `cornerRadius` rounds the back corners and the head tips, not the shaft/head junctions; `Callout` rounds the body
corners, not the pointer. `makeX()` output is plain data: combine it with any `@remotion/paths` function.

### 3.4 `@remotion/rough-notation` (4.0.490)

Install `npx remotion add @remotion/rough-notation`. Components: `Highlight` (drawn behind), `Underline`, `StrikeThrough`,
`CrossedOff`, `Box`, `Bracket`, `Circle` (drawn on top). Type `Padding = {left, right, top, bottom}` (partial allowed).
Name clash: `Circle` and `Box` collide with `@remotion/shapes` `Circle` and other `Box` components; alias on import.

Common props: `children`, `progress` (0..1, required; drive with `interpolate`), `style?` (applied to the text span; note that
`display: inline-block`, `position: relative`, `white-space: pre` are forced), `disabled? = false`, `seed? = 1` (integer;
change it every few frames for a "boiling" hand-drawn line), `color? = 'currentColor'`, `roughness?` (3 for Highlight, 1.5 for
the rest), `maxRandomnessOffset? = 5`, `bowing? = 1`, `disableMultiStroke?` (docs: default false; source: every type is built
with Rough.js `disableMultiStroke: true`, so pass `disableMultiStroke={false}` to get the classic doubled sketch stroke),
`preserveVertices? = false`. Sequence props: `from`, `durationInFrames`, `trimBefore`, `playbackRate`, `freeze`, `hidden`,
`name`, `showInTimeline` (default true); from 4.0.528 also `premountFor`, `postmountFor`, `styleWhilePremounted`,
`styleWhilePostmounted`. Studio-editable (text and font controls).

| Component | strokeWidth default | iterations default | Other options |
|---|---|---|---|
| `Highlight` | n/a (stroke = text height + top + bottom padding) | 2 | `padding`, `rtl? = false`. Default colour `currentColor` would paint over the text colour: always pass a translucent colour such as `rgba(255, 236, 79, 0.62)`. |
| `Underline` | 20 | 2 | `padding` accepts only `top` (moves the line down), `rtl` |
| `StrikeThrough` | 20 | 1 | `rtl` |
| `CrossedOff` | 20 | 1 (per diagonal) | `rtl` |
| `Box` | 7 | 2 | `padding` |
| `Bracket` | 20 | n/a | `padding`, `bracketLeft? = false`, `bracketRight? = true`, `bracketTop? = false`, `bracketBottom? = false` |
| `Circle` | 20 | 2 (each gets seed + i) | `padding`, `box? = 'around'` (ellipse scaled by sqrt 2 to enclose the box) or `'inside'` (ellipse fits the padded box), `curveFitting? = 0.95`, `curveTightness? = 0`, `curveStepCount? = 9` |

Behaviour from source: `iterations` must be an integer >= 1 (TypeError). Strokes are revealed one after another: with n paths,
path i draws while `progress * n - i` goes 0 to 1 (so 2 iterations = first stroke in the first half). For Highlight,
Underline, StrikeThrough and CrossedOff every second stroke runs back the other way (`rtl` flips the first one), which gives
the back-and-forth marker look. Measurement uses `offsetLeft/Top/Width/Height` of the span (layout pixels, so parent CSS
`scale` transforms are fine) and a `ResizeObserver`; the first render is held with `delayRender()` until a size is known. The
annotated text never wraps (`white-space: pre`): keep annotated phrases short or split per line.

### 3.5 `@remotion/layout-utils` (package 4.0.50; browser only)

| Function | Since | Input | Output |
|---|---|---|---|
| `measureText(word)` | 4.0.50 (package) | `text`, `fontFamily`, `fontSize` (number, string since 4.0.125), `fontWeight?`, `letterSpacing?`, `fontVariantNumeric?` (4.0.57), `textTransform?` (4.0.140), `validateFontIsLoaded?` (4.0.136; default false in 4.0, true in v5), `additionalStyles?` (4.0.140, e.g. `{lineHeight: 1.5}`) | `{width, height}` (`Dimensions`) |
| `fitText(opts)` | 4.0.88 | `text`, `withinWidth`, `fontFamily`, `fontWeight?`, `letterSpacing?`, `fontVariantNumeric?`, `textTransform?`, `validateFontIsLoaded?`, `additionalStyles?` | `{fontSize}` for a single line; cap it yourself (`Math.min(80, ...)`) |
| `fitTextOnNLines(opts)` | 4.0.313 | `text`, `maxBoxWidth`, `maxLines`, `fontFamily`, `fontWeight?`, `letterSpacing?`, `fontVariantNumeric?`, `textTransform?`, `validateFontIsLoaded?`, `additionalStyles?`, `maxFontSize? = 2000` | `{fontSize, lines: string[]}` |
| `fillTextBox({maxBoxWidth, maxLines})` | 4.0.57 | `.add({text, fontFamily, fontSize (number px), fontWeight?, letterSpacing?, fontVariantNumeric?, textTransform?, validateFontIsLoaded?, additionalStyles?})` | `{exceedsBox, newLine}` per word |

Internals that matter:
- `measureText` appends a hidden span (`display: inline-block; position: absolute; top: -10000px; white-space: pre`) to
  `document.body`, reads `getBoundingClientRect()`, removes it. Global CSS (Tailwind preflight, resets) applies to it too.
- Cache key = text, family, weight, size, letterSpacing, textTransform, additionalStyles. It EXCLUDES `fontVariantNumeric` and
  it is never invalidated: a measurement taken before the font loaded stays wrong for the page lifetime.
- `validateFontIsLoaded` measures again with the fallback font and throws only if both sizes match, the computed families
  differ and the text has more than 4 unique characters.
- `fitText` measures at 100 px and scales linearly. Letter spacing in `px` does not scale linearly: express it in `em`.
- `fitTextOnNLines` binary-searches font size between 0.1 and `maxFontSize` in 0.01 px steps, splitting on single spaces and
  greedily filling lines with `fillTextBox` (which trims leading spaces, and reports `exceedsBox` if a single word is wider
  than the box, the fix for issue 7359). The browser may wrap differently: render the returned `lines` yourself, one block
  per line with `white-space: pre`. Scripts without spaces (CJK) are one word and only shrink.
- Throws `measureText() can only be called in a browser.` in Node/SSR contexts: call inside components, `useMemo` or
  `useEffect`, never in `calculateMetadata`.
- Exported types: `Dimensions` (`{width, height}`), `TextTransform`.
- Debugging wrong measurements (docs debug page): open the composition in Studio at 100 percent zoom, render at the bottom a
  `<div id="remotion-measurer" style={{display: 'inline-block', whiteSpace: 'pre', fontSize, fontWeight, fontFamily,
  letterSpacing, fontVariantNumeric, textTransform}}>` with the same text, select it in Chrome DevTools and compare its box and
  its Computed styles with the real node until they match. Typical culprits: whitespace (`.trim()` or keep `white-space: pre`
  on the whole container), CSS resets/Tailwind, padding/border, font not loaded, multiplying sizes by `useCurrentScale()`.

### 3.6 `@remotion/rounded-text-box` (4.0.360)

`createRoundedTextBox({textMeasurements: Dimensions[], textAlign: 'left' | 'center' | 'right', horizontalPadding: number,
borderRadius: number})` -> `{d, boundingBox: BoundingBox, instructions: ReducedInstruction[]}`. Builds one outline around
stacked lines of different widths with rounded outer corners and inverse-rounded inner corners (the TikTok/Instagram caption
plate). Corner radius is clamped to half of each line's height; inner corner radii follow half (left/right align) or a quarter
(centre) of the width difference. Lines stack with no gap, so measure every line with the same `lineHeight` (via
`additionalStyles`) that you render with, and render each line with `paddingLeft/Right = horizontalPadding`. Draw it as
`<svg viewBox={boundingBox.viewBox} style={{position: 'absolute', width: boundingBox.width, height: boundingBox.height,
overflow: 'visible'}}><path d={d} fill="white"/></svg>` behind a `position: relative` text stack.

### 3.7 `@remotion/google-fonts`

- `loadFont(style?, {weights?, subsets?, document?, ignoreTooManyRequestsWarning? (4.0.283)})` from
  `@remotion/google-fonts/<ImportName>` -> `{fontFamily, fonts, unicodeRanges, waitUntilDone() (4.0.135)}`. Blocks the render
  until loaded. In 4.0 omitting args loads all styles/weights/subsets (many requests, warnings above 20 requests, timeouts);
  from v5 `weights` and `subsets` must be non-empty. Call at module top level (once), one call per style. The module also
  exports `fontFamily` directly.
- `getAvailableFonts()` (root import) -> `[{fontFamily, importName, load: () => import(...) (3.3.64)}]`. Dynamic `load()` needs
  ESM (not `require()`).
- `getInfo()` from each font module -> `{fontFamily, importName, version, url, unicodeRanges, fonts, subsets, variable?
  (4.0.525: {axes: {wght: {min, max}, ...}, fontFaces, url})}`. Pure JSON, can be served from a backend.
- `loadFontFromInfo(info, style, options?)` from `@remotion/google-fonts/from-info` (4.0.279): same as `loadFont` without
  per-font autocomplete, keeps big font modules out of the client bundle (font pickers).
- `loadVariableFont(style, {subsets (required, >= 1), document?, ignoreTooManyRequestsWarning?})` (4.0.525; only on variable
  families) -> `{fontFamily, axes, waitUntilDone()}`. Then animate `fontWeight` between `axes.wght.min` and `axes.wght.max`.
  No client-side rendering support. `loadVariableFontFromInfo(info, style, options)` (4.0.525) is the metadata version.
- CJK: named subsets such as `'chinese-simplified'` resolve to many numbered chunk files (use
  `ignoreTooManyRequestsWarning: true` knowingly, fixed in issue 7258).

### 3.8 `@remotion/fonts` (4.0.165)

`loadFont({family, url, format?, ascentOverride?, descentOverride?, display?, featureSettings?, lineGapOverride?, stretch?,
style?, weight?, unicodeRange?})` -> `Promise<void>`; blocks the render until the FontFace is ready. `url` is
`staticFile('brand.woff2')` or a URL; `format` is derived from the extension (`woff2`, `woff`, `opentype`, `truetype`). Then use
`fontFamily: family` in CSS. Call once per weight/style file with matching `weight`/`style`.

### 3.9 `@remotion/lottie` (needs peer `lottie-web`)

- `<Lottie animationData ... />` props: `animationData` (Lottie JSON; identity change re-initializes, so memoize or keep in
  state), `className`, `style` (on the wrapping `<div>`), `direction? = 'forward' | 'backward'`, `loop? = false`,
  `playbackRate? = 1`, `renderer? = 'svg'` (`'canvas'`, `'html'`; 4.0.105), `preserveAspectRatio?` (4.0.105, lottie-web
  string), `onAnimationLoaded?(item: AnimationItem)` (3.2.29), `assetsPath?` (4.0.138; assets with `e: 0` are prefixed by it,
  e.g. `staticFile('lottie')` -> `public/lottie/`; `e: 1` = absolute/embedded). From 4.0.528 it inherits `from`,
  `durationInFrames`, `trimBefore`, `freeze`, `hidden`, `name` (default `"<Lottie>"`), `showInTimeline` (default false),
  `premountFor`, `postmountFor`, `styleWhilePremounted`, `styleWhilePostmounted`.
- `getLottieMetadata(json)` -> `null | {width, height, fps, durationInSeconds, durationInFrames (floored)}`. Use in
  `calculateMetadata()` to size and time the composition from the file.
- Loading: import JSON directly, or `fetch(staticFile('x.json'))` / remote URL (CORS) inside `useEffect` guarded by
  `delayRender()` + `continueRender()` / `cancelRender()` and render `<Lottie>` only when data exists. Type
  `LottieAnimationData`. Find files on LottieFiles (download "Lottie JSON").

### 3.10 `@remotion/rive` `<RemotionRiveCanvas>` (3.3.75)

Props: `src` (URL or `staticFile()`), `fit? = 'contain'` (`cover`, `fill`, `fit-height`, `none`, `scale-down`, `fit-width`),
`alignment? = 'center'` (9 positions like `top-left`), `artboard?` / `animation?` (name or index; otherwise the file's
default artboard/animation),
`onLoad?(file: File)` (4.0.58; memoize), `enableRiveAssetCdn? = true` (4.0.181), `assetLoader?(asset, bytes)` (4.0.181;
memoize; return true when you handle the asset), `effects?`, `className?`, `style?` on the `<canvas>` (4.0.464),
`cropLeft/Right/Top/Bottom?` (0..1, 4.0.500). Inherits `from`, `durationInFrames`, `trimBefore` (4.0.482), `playbackRate`,
`name`, `showInTimeline`, `hidden` (4.0.464) and premount props (4.0.528). Ref (4.0.180): `getAnimationInstance()`,
`getArtboard()`, `getRenderer()`, `getCanvas()`. Dynamic text: in `onLoad`, `file.defaultArtboard().textRun('city').text =
'Tokyo'` (the docs snippet calls `useCallback` outside a component: move it inside).

### 3.11 `@remotion/gif`

- `<Gif>`: `src` (import, `staticFile()` or CORS URL), `width`, `height` (use these, not `style.width/height`),
  `fit? = 'fill'` (`contain`, `cover`), `playbackRate? = 1` (4.0.44), `loopBehavior? = 'loop'` (`pause-after-finish`,
  `unmount-after-finish`; 3.3.4), `onLoad?({width, height, delays, frames})`, `style`, `ref` (`HTMLCanvasElement`, 3.3.88),
  `effects?` (4.0.464), `cropLeft/Right/Top/Bottom?` (4.0.500), `premountFor?`, `postmountFor?`, `styleWhilePremounted?`,
  `styleWhilePostmounted?` (4.0.497; premounting lets it decode before it shows), `delayRenderTimeoutInMilliseconds? = 30000`
  (4.0.403), `requestInit?` (4.0.471, fetch options; `signal` ignored). JS decoder: works in Safari; no animated AVIF/WebP
  (use `<AnimatedImage>` for those).
- `getGifDurationInSeconds(src, {requestInit?})` (3.2.22) -> `Promise<number>` (one loop).
- `preloadGif(src, {requestInit?})` (3.3.38) -> `{waitUntilDone(), free()}` for the Player.

### 3.12 `@remotion/animated-emoji` (4.0.187)

`<AnimatedEmoji emoji="blush" scale? calculateSrc? />`: plays Google Noto animated emoji videos (via `<OffthreadVideo>`, so no
client-side rendering). `scale` 0.5 (512 px), 1 (1024 px, default), 2 (2048 px). Assets are NOT bundled: copy the videos from
the `public` folder of github.com/remotion-dev/animated-emoji into your `public/`. The default `calculateSrc({emoji, scale,
format})` returns `staticFile(emoji + '-' + scale + 'x.' + ext)` where `ext` is `mp4` for `format === 'hevc'`, else `webm`
(for example `blush-1x.webm`). `getAvailableEmojis()` (the docs page title says `getAvailableEmoji`) ->
`[{name, categories, tags, durationInSeconds, codepoint}]`.

### 3.13 `@remotion/gsap` `useGsapTimeline()` (4.0.517; peer `gsap`)

`const scope = useGsapTimeline<HTMLDivElement>(({timeline, scope, selector}) => {...}, {dependencies?: []})` returns a ref for
the scoping HTML/SVG element. The builder runs once per mount (and when dependencies change, after reverting); the hook
seeks the paused timeline to the current frame by replaying from 0 every frame. Allowed: `to`, `from`, `fromTo`, `set`, `add`,
labels, position parameters, staggers, keyframes, repeat, yoyo, nested timelines, zero-duration `gsap.set()`. Throws on:
`play/resume/restart/reverse/paused(false)/seek/time/progress/tweenTo`; callbacks (`onStart`, `onUpdate`, `onComplete`,
`timeline.call`, `eventCallback`, `then`); async builders; tweening plain objects (freezes in renders); `"random(...)"`,
`stagger: {from: 'random'}`, `repeatRefresh: true`; freestanding `gsap.to()` / `gsap.delayedCall()`. No GSAP plugins.

### 3.14 Styling toolchains

- Tailwind v3: `@remotion/tailwind` `enableTailwind(config, {configLocation?})` (3.3.95; `configLocation` 4.0.187 fixes
  running the CLI from another directory) inside `Config.overrideBundlerConfig()` in `remotion.config.ts`.
- Tailwind v4: `@remotion/tailwind-v4` `enableTailwind(config)` (4.0.256). Both are build-time only (Studio/CLI bundling).
- SCSS: `@remotion/enable-scss` `enableScss(config)` (4.0.162); pin `sass@1.77.2 sass-loader@14.2.1 css-loader@5.2.7` exactly
  (newer may break). Compose overrides reducer style: `enableScss(enableTailwind(config))`.

### 3.15 `@remotion/zod-types`

`zColor()` (color picker in Studio props editor), `zTextarea()` (multiline string; render with `white-space: pre-line`),
`zMatrix()` (flat square matrix, 2x2 = 4 numbers). Since 4.0.426 the package builds Zod v4 schemas; use
`@remotion/zod-types-v3` (4.0.426) with Zod 3.22.3. Validation works everywhere; the editors only in Studio.

### 3.16 `@remotion/mac-cursors` `<MacOSCursor>` (4.0.513)

`cursor? = 'default'` (CSS cursor keyword: `pointer`, `text`, ...; unknown -> arrow; `'none'` renders nothing; `'custom'` uses
`customCursor`), `customCursor?` (CSS value like `url("...") 12 8, pointer`, quoted or not, optional hotspot), `className?`,
`style?` (position with `left`/`top`; the hotspot correction is kept), 39 bundled SVG cursors with the hotspot at the component
origin. Inherits Sequence props (premount ones from 4.0.528).

---

## 4. Recipes

Values marked "house default" are recommendations distilled from the docs examples and the showcase code, not documented
defaults. Frames assume 30 fps unless stated.

### 4.1 Scene transitions

**R1. The safe professional default.** `slide()` or `wipe()` with
`springTiming({config: {damping: 200}, durationInFrames: 20, durationRestThreshold: 0.001})`, or
`linearTiming({durationInFrames: 18, easing: Easing.bezier(0.65, 0, 0.35, 1)})`. House default lengths: 15 to 24 frames
(0.5 to 0.8 s) for slide/wipe/flip, 10 to 20 for `fade()`, 8 to 12 for fast social cuts, 11 for `pushCut()`, 20 to 30 for
shader looks. Never leave `durationRestThreshold` at 0.005 with springs (visible snap at the end).

**R2. Duration bookkeeping.** Keep scene lengths and timings in one array and derive the composition length (also in
`calculateMetadata()`):
```ts
const scenes = [90, 120, 75];
const timings = [linearTiming({durationInFrames: 20}), springTiming({config: {damping: 200}, durationRestThreshold: 0.001})];
const total = scenes.reduce((a, b) => a + b, 0) - timings.reduce((a, t) => a + t.getDurationInFrames({fps: 30}), 0);
```
Extend each scene by the overlap you want to preserve: a 3 s scene followed by a 20-frame transition should be 110 frames if the
content must be fully visible for 3 s.

**R3. Entry and exit of a single scene.** Put a `<TransitionSeries.Transition>` as the first child (enter) or last child (exit);
the other side is empty. Good for lower thirds and end cards (`slide({direction: 'from-bottom'})`, `iris({width, height})`).

**R4. Per-element choreography instead of whole-frame moves.** Use `none()` plus `useTransitionProgress()` in both scenes:
```tsx
const Headline: React.FC<{text: string}> = ({text}) => {
  const {entering, exiting} = useTransitionProgress();
  const y = interpolate(entering, [0, 1], [60, 0]) + interpolate(exiting, [0, 1], [0, -60]);
  return <h1 style={{transform: `translateY(${y}px)`, opacity: entering * (1 - exiting)}}>{text}</h1>;
};
```
Offset child elements with sub-ranges (`interpolate(entering, [0.3, 1], ...)`) for a stagger. `entering`/`exiting` are already
eased by the timing.

**R5. Accent on a hard cut without shortening the edit.** `<TransitionSeries.Overlay durationInFrames={16}>` with a flash
(`<AbsoluteFill style={{backgroundColor: '#fff', opacity: interpolate(frame, [0, 8, 16], [0, 0.8, 0])}}/>`) or
`<LightLeak />` from `@remotion/light-leaks` (docs example; D5 covers light leaks/effects). Not adjacent to a transition.

**R6. Whoosh on every transition.** Wrap presentations with the `addSound()` helper (section 3.1). The sound starts when the
entering scene's presentation mounts, i.e. at the start of the overlap. Alternative: compute cut frames from the array in R2
and place `<Sequence from={cut - 6}><Audio .../></Sequence>` outside the series.

**R7. Branded mask reveal.** Custom presentation that clips the entering scene with `clip-path: path("...")` built from
`@remotion/shapes` or a logo path: size = frame diagonal * progress, centred with `centerPath(d, {x: w / 2, y: h / 2})` (4.0.486)
or `translatePath()`. Reveal from a point (a button, a pin): radius = distance from that point to the farthest corner. Only
clip when `presentationDirection === 'entering'` so the old scene stays underneath. Prefer CSS `clip-path: path()` over an
SVG `<clipPath id>`; if you use ids, generate them with `React.useId()` (the docs' `random(null)` works but is not
reproducible) so two instances never collide.

**R8. Editorial punch cut.** 11-frame `pushCut({cutProgress: 5 / 11})` with `linearTiming({durationInFrames: 11})`; lengthen the
next sequence by 5 frames and wrap its content in `<AbsoluteFill from={5}>` (valid in 4.0.528) or `<Sequence from={5}>` so its
first visible frame is its local frame 0. Tint the flash with `flashColor` (brand off-white) and keep `flashOpacity` 0.15 to
0.3.

**R9. Zoom-through, whip, burn, page turn.** For CSS: write a custom presentation (outgoing
`scale(interpolate(p, [0, 1], [1, 2.5]))` + `opacity 1 - p`, incoming `scale(0.8 -> 1)`). For shader looks: `blurSlide({})`
whip pan, `zoomBlur({})`, `crossZoom({strength: 0.4})`, `filmBurn({})`, `bookFlip({})`, `dissolve({hotColor, spreadColor})`
with brand colours. Always set `Config.setChromiumOpenGlRenderer('angle')` in `remotion.config.ts` (or `--gl=angle`,
`swangle` on GPU-less machines) and tell the user that Studio preview needs Chrome with `chrome://flags/#canvas-draw-element`.

**R10. Static enter/exit styles pop.** `enterStyle`, `exitStyle`, `outer*/inner*` styles are applied only while the transition
runs and do not animate: `slide({exitStyle: {filter: 'brightness(0.6)'}})` darkens the old slide abruptly at the first
overlap frame. Use them for things that should hold during the whole overlap (box-shadow on the incoming card, `zIndex`,
`borderRadius`); for animated depth write a custom presentation.

**R11. Transitions inside a shape or text.** Put a whole `<TransitionSeries>` of colour/image scenes inside an `<AbsoluteFill>`
that has `WebkitMaskImage: url(staticFile('word.png'))` (examples/transitions-video `TextMask.tsx`): scenes change inside the
letters while the mask scales with a spring.

### 4.2 Paths, drawings and illustration

**R12. Draw-on line art (logo, signature, diagram).**
```tsx
const parts = useMemo(() => getSubpaths(logoD), []);
{parts.map((d, i) => {
  const p = interpolate(frame, [i * 5, i * 5 + 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  return <path key={i} d={d} fill="none" stroke="#111" strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" {...evolvePath(p, d)} />;
})}
```
Then fade the fill in (`fillOpacity`) after the last stroke finishes. `reversePath(d)` draws from the other end. Keep the stroke
on a separate `<path>` from the fill so the fill does not wait for the dash animation.

**R13. Object travelling along a route (plane, map pin, data packet).**
```tsx
const len = useMemo(() => getLength(route), [route]);
const at = Math.min(len * progress, len);
const pt = getPointAtLength(route, at) ?? {x: 0, y: 0};
const t = getTangentAtLength(route, at) ?? {x: 1, y: 0};
<g transform={`translate(${pt.x} ${pt.y}) rotate(${(Math.atan2(t.y, t.x) * 180) / Math.PI})`}><Plane /></g>
```
Draw the trail behind it with `evolvePath(progress, route)`, or, for a dashed trail, `<path d={cutPath(route, at)}
strokeDasharray="10 14"/>` (evolvePath owns `strokeDasharray`, so it cannot also make dashes).

**R14. Shape and icon morphs.** `interpolatePath(t, a, b)` with an eased `t`. Works best when both paths are single, closed
subpaths with similar starting points and winding; otherwise split with `getSubpaths()` and morph pairs, or add dummy points.
Inspect with `PathInternals.debugPath()`. Multi-keyframe morphs on 4.0.528 (no `interpolatePaths`):
```ts
const morph = (f: number, times: number[], paths: string[], easing = Easing.inOut(Easing.cubic)) => {
  let i = 0;
  while (i < times.length - 2 && f >= times[i + 1]) i++;
  const t = interpolate(f, [times[i], times[i + 1]], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing});
  return interpolatePath(t, paths[i], paths[i + 1]);
};
```
From 4.0.529 replace it with `interpolatePaths(frame, times, paths, {easing, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})`.

**R15. Text as vector outlines (warp, outline draw-on, glyph morph).** Load a font file with opentype.js inside
`delayRender()`: `font.getPath(text, 0, fontSize, fontSize).toPathData(2)` -> `resetPath()` -> transform -> `getBoundingBox()`
for the `viewBox` (examples/text-warping). Extra dependency (`opentype.js`); the font file must be in `public/`. Use HTML text
whenever you do not need path operations (sharper hinting, selectable, cheaper).

**R16. Warps.** `warpPath(d, ({x, y}) => ({x, y: y + Math.sin(x / 40 + frame / 6) * 12}), {interpolationThreshold: 1})` for a
flag wave; bulge: scale points by distance from a centre. The output grows a lot: memoize on inputs, keep thresholds around
1 to 3 units for smooth curves, and precompute static warps once.

**R17. Progress rings, pie and donut charts.**
`<Pie radius={120} progress={p} closePath={false} fill="none" stroke="#0b84f3" strokeWidth={18} strokeLinecap="round" />` gives an
open arc from 12 o'clock; `counterClockwise` flips it; `rotation` (radians) moves the start. Donut chart: one `<Pie>` per slice
with `rotation = cumulativeFraction * 2 * Math.PI` and `progress = slice * growProgress`. Keep strokes inside the viewBox or rely
on the shapes' `overflow: visible`.

**R18. Speech bubbles and callouts.** Size `makeCallout({width: textW + 2 * pad, height: textH + 2 * pad, pointerDirection:
'down', pointerPosition: 0.2, cornerRadius: 24})` from `measureText()`; place text absolutely over the body (body height =
`height` option, pointer adds `pointerLength`). Pop in with a spring `scale` whose `transformOrigin` is the pointer tip
(`width * pointerPosition`, `height + pointerLength` for down) so the bubble grows out of the speaker.

**R19. Arrows.** Line arrow: draw the shaft with `evolvePath`, then place a small head (`makeTriangle({length: 28, direction:
'right'})` path) at the current tip from `getPointAtLength` and rotate it by the tangent. Block arrow: `<Arrow>` revealed with a
`clip-path: inset(0 X% 0 0)` or scaled from its back end (`pathStyle={{transformOrigin: '0% 50%'}}` plus `transform`), with
`cornerRadius` 8 to 16 for a friendly UI look.

**R20. Rounded UI primitives.** `makeRect({width, height, cornerRadius: 24})` for cards/buttons that need path tricks (draw-on
border with `evolvePath`, morph to a circle). `edgeRoundness` (0 to about 1) gives squircle-like, organic sides; the two options
cannot be combined. Use `pathStyle` for rotation around the centre and `debug` to check Bezier handles.

**R21. Sparkles, stars, badges.** `<Spark width={40} height={56} fill="#fff"/>` scaled with a spring (overshoot) and rotated
15 to 45 degrees, several with `random('spark-' + i)` positions and 3 to 6 frame staggers; `<Star points={12} innerRadius={70}
outerRadius={90} cornerRadius={6}/>` for price badges; hearts via `<Heart height={80} />` for social overlays.

### 4.3 Hand-drawn emphasis (`@remotion/rough-notation`)

**R22. Marker sweep on a keyword.** Showcase values: `color="rgba(255, 221, 64, 0.72)"`, `roughness={2.3}`,
`maxRandomnessOffset={10}`, `padding={{left: 18, right: 18}}`, progress `interpolate(frame, [8, 30], [0, 1], {clamp,
easing: Easing.bezier(0.22, 1, 0.36, 1)})`. Docs example adds `bowing={0}` for a straighter marker and
`Easing.spring({damping: 200, ...})` as easing.

**R23. Circle a number or word.** `<Circle box="inside" padding={{left: 42, right: 51, top: 16, bottom: 26}} strokeWidth={12}
roughness={1.8} color="#2563eb">`. Add `disableMultiStroke={false}` for the doubled pencil look.

**R24. Underline, box, bracket, cross-out.** Underline `strokeWidth` about fontSize / 12 with `padding={{top: -4}}`; Box
`strokeWidth={10}` with small padding; Bracket `bracketLeft bracketRight`; CrossedOff `iterations={3}` for an angry scribble.

**R25. Boiling line (cartoon jitter).** After the stroke has drawn, set `seed={1 + Math.floor(frame / 4)}` (new shape every 4
frames at 30 fps); faster than every 3 frames looks noisy.

**R26. Sequencing.** Stagger several annotations 10 to 20 frames apart, after the text itself has landed (6 to 8 frames). Wrap
each slide's text in an `opacity` fade (0 to 1 over 6 frames) and a `scale` 0.97 -> 1 over 8 frames `Easing.out(Easing.cubic)`
(brand showcase). For paper texture backgrounds see D5 (`@remotion/effects` paper, gridlines, vignette).

### 4.4 Typography

**R27. One font module per project.**
```ts
// fonts.ts
import {loadFont as loadInter} from '@remotion/google-fonts/Inter';
export const inter = loadInter('normal', {weights: ['400', '700', '900'], subsets: ['latin']});
export const waitForFonts = () => Promise.all([inter.waitUntilDone()]);
```
Import `inter.fontFamily` everywhere. Components that measure text render inside a `WaitForFonts` wrapper
(`useDelayRender()` handle + `waitForFonts()` then `continueRender`; docs "best practices" HOC) or measure in `useEffect` after
`waitUntilDone()`.

**R28. Titles that always fit.** Single line: `Math.min(maxSize, fitText({text, withinWidth, fontFamily, fontWeight,
validateFontIsLoaded: true}).fontSize)`. Up to N lines:
```tsx
const {fontSize, lines} = useMemo(() => fitTextOnNLines({text, maxBoxWidth: 900, maxLines: 2, maxFontSize: 120, fontFamily, fontWeight: 800, validateFontIsLoaded: true}), [text]);
return <div style={{fontFamily, fontWeight: 800, fontSize, lineHeight: 1.1}}>
  {lines.map((l, i) => <div key={i} style={{whiteSpace: 'pre'}}>{l}</div>)}
</div>;
```
Use `outline` (not `border`/`padding`) for debug frames, and the same `textTransform`/`letterSpacing` in both measurement and
markup.

**R29. TikTok/Instagram caption plate.** `fitTextOnNLines` -> `measureText` each line with `additionalStyles: {lineHeight}` ->
`createRoundedTextBox({textMeasurements, textAlign: 'center', horizontalPadding: 30, borderRadius: 20})` -> SVG path behind the
lines (section 3.6). Animate the plate with a spring scale from the centre, or draw its outline with `evolvePath(p, d)`.

**R30. Paginating captions.** Feed words to `fillTextBox({maxBoxWidth, maxLines: 2})`; when `exceedsBox` is true start a new page
with that word. Deterministic, so the same pages come out in every render worker.

**R31. Variable font animation (4.0.525).** `const {fontFamily, axes} = loadVariableFont('normal', {subsets: ['latin']})` from a
variable family (Inter, NotoSans...), then `fontWeight: interpolate(frame, [0, 30], [axes.wght.min, axes.wght.max])`. Width
changes with weight: centre the text or give it a fixed box. Other axes (if present in `axes`) via
`fontVariationSettings: "'wdth' 80"`. Not for client-side rendering.

**R32. Numbers that do not jiggle.** Counters and timers: `fontVariantNumeric: 'tabular-nums'` in the style and in
`measureText()` (remember the cache ignores `fontVariantNumeric`, so do not measure the same text twice with different values).

**R33. Typewriter and reveal.** `text.slice(0, Math.floor(frame / 3))` plus a blinking caret (`Math.floor(frame / 10) % 2`) as in
examples/typewriter. Reserve the final width (measure the full string, fix the container width) so centred text does not drift
while typing.

**R34. Gooey blur morph between words.** Two stacked spans cross-fading with `blur(8 / f - 8 px)` and opacity `f ** 0.4`, parent
`filter: url(#threshold) blur(0.6px)` with an `feColorMatrix` alpha row `0 0 0 255 -140` (examples/morph-text). Drive `f` from
the frame, not from DOM mutations, and load the font through `@remotion/google-fonts` (the example's CSS `@import` does not
block rendering).

**R35. Non-Latin scripts (Bengali, Devanagari, CJK).** Load a family that has the subset (`subsets: ['bengali', 'latin']` on a
Bengali-capable family, `'chinese-simplified'` etc. for CJK) and nothing more. Never animate complex scripts character by
character with `split('')`: it breaks conjuncts and shaping; animate by words or by grapheme clusters
(`Intl.Segmenter`) instead (general web knowledge, not from these docs). `fitTextOnNLines` splits on spaces only.

**R36. Brand fonts.** `loadFont({family: 'Brand', url: staticFile('Brand-Bold.woff2'), weight: '700'})` from `@remotion/fonts`,
one call per file, then `fontFamily: 'Brand'`. Prefer `woff2`.

### 4.5 Vector animation players and assets

**R37. Lottie that fits the timeline.** Keep the JSON in `public/`, fetch it once in `calculateMetadata()` (or in a component
with `delayRender`), read `getLottieMetadata(json)` to set `durationInFrames` / `fps` / size, then `<Lottie animationData={json}
loop={false} playbackRate={1} style={{width, height}} />`. Use `renderer="canvas"` for heavy files, `assetsPath={staticFile('lottie')}`
for external images. Memoize `animationData`.

**R38. Rive with live data.** `<RemotionRiveCanvas src={staticFile('card.riv')} artboard="Main" animation="Intro" fit="cover"
onLoad={onLoad}/>` with `onLoad` (memoized) setting text runs from props.

**R39. GIF stickers and memes.** `<Gif src={staticFile('cat.gif')} width={400} height={400} fit="cover"
loopBehavior="pause-after-finish" premountFor={30}/>`; get its length with `getGifDurationInSeconds()`.

**R40. Emoji reactions.** `<AnimatedEmoji emoji="fire" scale={0.5}/>` (512 px is enough for stickers) inside a `<Sequence>`,
with a spring scale-in. Copy the assets first.

**R41. GSAP-authored motion.** Port GSAP timelines with `useGsapTimeline()`: element selectors (`data-*` attributes +
`selector()`), numeric eases (`power3.out`), staggers with fixed order, `{dependencies: [prop]}` when props change the tweens.

**R42. Product-demo cursor.** `<MacOSCursor cursor={overButton ? 'pointer' : 'default'} style={{left: x, top: y, scale: 1.5}}/>`
with `x, y` from a spring or from `getPointAtLength()` on a curved path; click = `scale` 1 -> 0.85 -> 1 over 6 frames plus a
`<Circle>` ripple (scale up, fade out) at the hotspot.

### 4.6 Editable templates and styling

**R43.** Expose brand colours with `zColor()`, multi-line copy with `zTextarea()` (render with `white-space: pre-line`), in a
Zod v4 schema (`@remotion/zod-types`), or `@remotion/zod-types-v3` for Zod 3.22.3 projects.

**R44.** Tailwind: v4 projects use `@remotion/tailwind-v4` `enableTailwind`; v3 uses `@remotion/tailwind` with
`configLocation: path.join(__dirname, 'tailwind.config.js')`. Tailwind preflight also styles the `measureText()` probe span,
so measurements stay consistent only if the rendered text gets the same computed styles.

---

## 5. Performance and render stability

- **Two scenes per frame.** During a transition both scenes render (and both keep their own `useCurrentFrame()`); heavy scenes
  double the cost in the overlap. Use `premountFor` on `TransitionSeries.Sequence` for video/Lottie/GIF scenes so they load
  before they appear.
- **Shader presentations** (HTML-in-canvas): each paint is a `delayRender('onPaint')`, a WebGL2 draw and an effect-chain pass at
  device pixel size. They need `--gl=angle` (or `swangle`) in renders, throw in browsers without the API
  (`HTML_IN_CANVAS_UNSUPPORTED_MESSAGE`), and nesting `<HtmlInCanvas>` is unsupported: avoid shader transitions around scenes
  that themselves use `effects` on shapes/Gif/Rive (which render through `<HtmlInCanvas>`) unless tested.
- **springTiming duration depends on fps.** Recompute totals with the composition fps; pass `durationInFrames` to lock it.
- **Fonts**: load only needed weights/subsets. A bare `loadFont()` in 4.0 can fire dozens of requests (warning above 20) and time
  out; large CJK subsets are many files. Raise the delayRender timeout only after narrowing. Local fonts: `woff2`.
- **measureText** touches the DOM (append, measure, remove) per uncached call; `fitTextOnNLines` runs a binary search (about 10 to 18
  iterations depending on `maxFontSize`) and measures every word each time (cached per word and size). Wrap in `useMemo` keyed on text and style; never
  call per frame with changing sizes. The cache is global and never invalidated.
- **Paths**: every call re-parses the string. Memoize `getLength`, `getSubpaths`, `warpPath`, `interpolatePath` inputs;
  `warpPath` output can be thousands of segments (tune `interpolationThreshold`). Avoid recomputing static geometry each frame.
- **rough-notation**: measures with a `ResizeObserver`, holds the first render with an unlabeled `delayRender()` until the
  wrapped span has a size (hidden or empty children can stall until the timeout), and recomputes strokes in a layout effect
  every frame. Use few annotations per frame and keep `seed` stable unless you want jitter.
- **Lottie**: a new `animationData` object identity re-initialises lottie-web (costly, may flash): memoize. SVG renderer is the
  default; canvas can be faster for complex files. Remote JSON needs CORS and `delayRender`.
- **GIF**: decoded in JavaScript into `ImageData` frames (memory heavy for long/large GIFs); `preloadGif().free()` releases
  memory in the Player; default load timeout 30 s (`delayRenderTimeoutInMilliseconds`).
- **GSAP**: every frame replays the timeline from 0 (deterministic but O(tweens)); hundreds of tweens cost on every frame.
- **Animated emoji** uses `<OffthreadVideo>`: fine for server renders, not supported in client-side rendering.
- **Determinism**: rough-notation seeds (default 1), `filmBurn` seed, and `random('key')` are deterministic; `Math.random()`,
  GSAP `random(...)` strings and time-based callbacks are not. The docs' `random(null)` for clip ids is not reproducible between
  workers (harmless for ids, never for visuals).
- `getPointAtLength` / `getTangentAtLength` return `null` past the end in 4.0.528: floating-point overshoot (`len * 1.0000001`)
  crashes a destructure; clamp first.

---

## 6. Errors and fixes

| Symptom / message | Cause | Fix |
|---|---|---|
| `The duration of a <TransitionSeries.Sequence /> must not be shorter than the duration of the next/previous <TransitionSeries.Transition />...` | Scene shorter than an adjacent transition | Lengthen the scene or shorten the timing (springs without `durationInFrames` can be longer than expected: check `getDurationInFrames({fps})`). |
| `A <TransitionSeries.Transition /> component must not be followed by another <TransitionSeries.Transition />` | Two transitions in a row | Put a sequence between them. |
| `A <TransitionSeries.Overlay /> component must not be followed by ...Overlay / ...Transition`, or `A <TransitionSeries.Transition /> component must not be followed by a <TransitionSeries.Overlay />` | Overlay and transition share a slot | Choose one per cut. |
| `A <TransitionSeries.Overlay /> extends before frame 0` / `extends beyond the previous sequence` / `beyond the next sequence` | Overlay too long or offset too big | Reduce `durationInFrames` or `offset`; overlay needs `durationInFrames / 2 - offset` frames before the cut and `durationInFrames / 2 + offset` after. |
| `The "offset" property of a <TransitionSeries.Overlay /> must be finite/an integer` | Float offset | Round it. |
| `The <TransitionSeries /> component only accepts a list of <TransitionSeries.Sequence />, ...` | A custom wrapper component, text or `<Sequence>` inside the series | Map sequences directly; whitespace strings are fine, other text is not. |
| `layout` prop error in v5 | `layout="none"` on the series or a sequence | Remove it (absolute-fill only). |
| Studio throws the HTML-in-canvas unsupported message on a shader transition | Browser lacks the API | Chrome 149+ with `chrome://flags/#canvas-draw-element`, or preview a CSS presentation. |
| Blank or failing shader transition in `npx remotion render` | No WebGL2 context | `--gl=angle` / `Config.setChromiumOpenGlRenderer('angle')`, `swangle` without GPU. |
| TypeScript `Expected 1 arguments, but got 0` on `dissolve()` / `zoomInOut()` / `crosswarp()` etc. | Shader presentation factories type their options object as required | Call `dissolve({})`. |
| `cutProgress passed to pushCut() must be greater than 0 and less than 1`, `... must be finite`, `flashOpacity ... between 0 and 1` | Invalid pushCut option | Use values in range. |
| `direction passed to blurSlide() must be one of ...`, `blur ... must be greater than or equal to 0` | Invalid blurSlide option | Fix the option. |
| Slight snap at the end of a spring transition | `durationRestThreshold` 0.005 cuts the tail | `durationRestThreshold: 0.001`. |
| Old scene shows through a `fade()` | Incoming scene is not opaque | Give the scene a background, or `shouldFadeOutExitingScene: true` for overlays. |
| `Malformed path data: ...` | Invalid `d` string (often a missing `M`, or a CSS `path()` string with quotes) | Validate with `parsePath()`; strip quotes. |
| `A length of X was passed to getInstructionIndexAtLength() but the total length of the path is only Y` | Length beyond the end | Clamp to `getLength()`. |
| `TypeError: Cannot destructure property 'x' of null` after `getPointAtLength` | Length past the end (returns `null`) | Clamp and null-check. |
| `Cannot interpolate SVG paths with different subpath structures` (4.0.529 `interpolatePaths`) | Different `M`/`Z` layout | Same number of subpaths, all closed or all open. |
| `SVG Path "..." is not valid` from `interpolatePath` | Empty path after parsing | Check inputs. |
| `"headWidth" must be greater than or equal to "shaftWidth"`, `"headLength" must be less than or equal to "length"`, `"pointerPosition" must be a number between 0 and 1`, `"width" must be a positive number`, `"points" should be minimum 3` | Invalid shape options | Respect the constraints in section 3.3. |
| `"cornerRadius" and "edgeRoundness" cannot be specified at the same time.` | Both rounding modes | Pick one. |
| `iterations must be an integer of at least 1` | rough-notation option | Use integers >= 1. |
| Highlight hides the text | `color` defaults to `currentColor` | Use a translucent colour. |
| Annotation misplaced after font swap / render timeout with annotations | Measured before the font loaded, or wrapped span has no size | Load fonts first (module-level `loadFont`), avoid `display: none` parents, give children content. |
| `measureText() can only be called in a browser.` | Called in Node (`calculateMetadata`, SSR) | Call in a component or `useEffect`. |
| `Called measureText() with "fontFamily": ... but it looks like the font is not loaded` | `validateFontIsLoaded: true` caught a fallback measurement | Await `waitUntilDone()` / wrap in `WaitForFonts`. |
| Text overflows although `fitText` said it fits | Different CSS between measure and render (padding, border with `box-sizing: border-box`, letter spacing in px, Tailwind classes, `useCurrentScale()` multiplication) | Match styles exactly, use `outline`, letter spacing in em, never multiply by `useCurrentScale()`; debug with the `remotion-measurer` div method (layout-utils debug page). |
| Font render timeout / "too many requests" warning | Loading every weight/subset | Pass `weights` and `subsets`; `ignoreTooManyRequestsWarning` only for intentional CJK loads. |
| Lottie restarts or flickers | New `animationData` object each render | Memoize / keep in state. |
| Remote Lottie/GIF fails in render | CORS | Put the file in `public/` and use `staticFile()`, or serve with CORS headers. |
| Rive component re-renders endlessly | Inline `onLoad`/`assetLoader` | `useCallback`. |
| GSAP hook throws about playback, callbacks, random, plain objects or stray tweens | Non-deterministic GSAP usage | Follow the builder rules (section 3.13). |
| Tailwind classes missing when CLI runs from another folder (v3) | `tailwind.config.js` resolved from cwd | `enableTailwind(config, {configLocation})` (4.0.187). |
| SCSS build breaks | Unpinned sass toolchain | `sass@1.77.2 sass-loader@14.2.1 css-loader@5.2.7`. |
| Zod type errors with `zColor()` | Zod major version mismatch | `@remotion/zod-types` for Zod 4, `@remotion/zod-types-v3` for Zod 3.22.3. |

---

## 7. What our skills must teach

### 7.1 Hard rules (always)

- Every visual value must derive from `useCurrentFrame()` (directly or through `progress`, timings, springs). No `Math.random()`,
  `Date.now()`, GSAP callbacks or wall-clock timers. Seeded randomness only (`random('key')`, rough-notation `seed`).
- Transitions: import presentations from their subpaths; give `clockWipe()` and `iris()` `{width, height}` from
  `useVideoConfig()`; springs always get `durationRestThreshold: 0.001`; compute the composition length as
  sum(scenes) - sum(transitions) with `timing.getDurationInFrames({fps})`; a scene must be >= each adjacent transition; never two
  transitions/overlays side by side; overlays are for accents that must not shorten the edit.
- Before choosing a shader presentation, check: is the output rendered on a machine with `--gl=angle`/`swangle` configured, and
  does the user preview in Chrome with the canvas-draw-element flag? If not, pick a CSS presentation. Pass `{}` to option-less
  shader factories.
- Fonts: load at module top level with explicit `weights`, `subsets` (and `style`); never a bare `loadFont()`; one font module
  per project; local brand fonts through `@remotion/fonts` `loadFont()` with `staticFile()`. Never CSS `@import`/`<link>` for
  fonts (does not block rendering).
- Text measuring: only in the browser, only after `waitUntilDone()` (or inside a WaitForFonts wrapper), with
  `validateFontIsLoaded: true` passed explicitly (default false on 4.0.528), with exactly the same `fontFamily`, `fontSize`,
  `fontWeight`, `letterSpacing`, `textTransform`, `fontVariantNumeric`, `lineHeight` as the markup; no `padding`/`border` on
  measured text (use `outline`); render measured text with `white-space: pre`; wrap calls in `useMemo`.
- Multi-line fitted text: render the `lines` returned by `fitTextOnNLines()` one per block; do not let the browser re-wrap.
- Paths: memoize parsing-heavy calls; clamp lengths before `getPointAtLength`/`getTangentAtLength` and handle `null`; compute the
  `viewBox` with `getBoundingBox()` (or use `overflow: visible`); `evolvePath` needs a stroke and no user `strokeDasharray`.
- `interpolatePaths()` does not exist on 4.0.528: use the segment helper (R14) or upgrade to 4.0.529+.
- rough-notation: `progress` from a clamped `interpolate()`; translucent colour for `<Highlight>`; alias `Circle`/`Box` imports;
  keep annotated phrases short (no wrapping); pass `disableMultiStroke={false}` for the double-stroke sketch look.
- Shapes: set `fill` explicitly (default black); `style` positions the `<svg>`, `pathStyle` transforms the `<path>`; use
  `cornerRadius` or `edgeRoundness`, not both.
- Lottie: memoize `animationData`; derive duration/size from `getLottieMetadata()`; remote files need CORS or `public/`.
- GIF/remote assets: CORS or `staticFile()`; `premountFor` for heavy stickers.
- GSAP: only via `useGsapTimeline()` and only element targets; follow its rule list.

### 7.2 Defaults the agent should reach for

House defaults (recommendations distilled from docs examples and showcase code, not API defaults):

| Situation | Default |
|---|---|
| Scene change, generic | `slide()` from the reading direction, spring damping 200, 20 frames, threshold 0.001 |
| Same subject, softer | `fade()` 15 frames (opaque scenes) or `none()` + per-element choreography |
| Reveal / result | `wipe({direction: 'from-left'})` or `iris({width, height})`, `linearTiming` 20 frames with `Easing.inOut(Easing.cubic)` |
| Punchy social edit | `pushCut()` 11 frames (+ delayed incoming content) |
| Whip pan / energy | `blurSlide({})` 16 to 20 frames linear (shader) |
| Accent on a cut | `<TransitionSeries.Overlay durationInFrames={16}>` flash or light leak |
| Keyword emphasis | `<Highlight color="rgba(255,221,64,0.72)" roughness={2.3} padding={{left: 18, right: 18}}>` drawn over 20 to 25 frames, eased `Easing.bezier(0.22, 1, 0.36, 1)` |
| Title | `fitTextOnNLines` maxLines 2, `maxFontSize` about 10 to 12 percent of frame width, `lineHeight` 1.05 to 1.15 for display type |
| Caption plate | `createRoundedTextBox` with `horizontalPadding` 20 to 30, `borderRadius` 16 to 20, `lineHeight` 1.4 to 1.5 |
| Line drawing | `evolvePath` + `strokeLinecap="round"` + `Easing.inOut(Easing.cubic)` over 20 to 40 frames per stroke, 4 to 6 frame stagger |
| Counters | `fontVariantNumeric: 'tabular-nums'` |

### 7.3 Decision tables

Transition by intent:

| Intent | Presentation | Engine |
|---|---|---|
| Continuity, calm | `fade`, `none` + `useTransitionProgress` | CSS |
| Next step, spatial flow | `slide` (4 dirs), `wipe` (8 dirs) | CSS |
| Reveal from a point / radial | `iris`, `clockWipe`, custom mask (shapes path, logo path) | CSS |
| Two sides of a thing | `flip`, (`cube`, paid) | CSS 3D |
| Editorial hard cut | `pushCut`, or a plain cut + Overlay flash | CSS |
| Speed, music, trailers | `blurSlide`, `zoomBlur`, `crossZoom`, `linearBlur`, `zoomInOut` | shader |
| Retro, film, fire | `filmBurn`, `dissolve` | shader |
| Storybook, magazine | `bookFlip` | shader |
| Playful, dreamy | `ripple`, `dreamyZoom`, `swap`, `crosswarp` | shader |

Text sizing:

| Need | API |
|---|---|
| Exact width/height of a string | `measureText` |
| One line, biggest size that fits a width | `fitText` (+ `Math.min` cap) |
| Up to N lines, biggest size, and the line breaks | `fitTextOnNLines` (+ `maxFontSize`) |
| Will these words overflow N lines? pagination | `fillTextBox().add()` |
| Background plate following ragged lines | `createRoundedTextBox` |

Animated illustration source:

| Asset / need | Tool |
|---|---|
| After Effects / LottieFiles JSON | `@remotion/lottie` |
| Rive file, runtime text runs, artboards | `@remotion/rive` |
| GIF (Safari-safe, onLoad metadata) | `@remotion/gif` (`<AnimatedImage>` for AVIF/WebP) |
| Emoji reactions | `@remotion/animated-emoji` |
| Code-drawn shapes, charts, diagrams | `@remotion/shapes` + `@remotion/paths` + SVG |
| Existing GSAP choreography | `@remotion/gsap` |
| UI demo pointer | `@remotion/mac-cursors` |
| Sketchy emphasis on text | `@remotion/rough-notation` |

### 7.4 Checklists

Before writing a scene with text:
1. Font module exists, weights/subsets narrowed, script subsets included (Bengali, CJK...).
2. Longest realistic copy tested with `fitTextOnNLines`/`fillTextBox`; `maxFontSize` set; lines rendered explicitly.
3. Same style object used for measurement and markup (spread one `const style`).
4. Complex scripts animated by words or grapheme clusters, not `split('')`.
5. Numbers use tabular figures.

Before render with transitions/graphics:
1. Durations: scene >= adjacent transitions; total length recomputed; springs measured at the composition fps.
2. Shader presentation present? `Config.setChromiumOpenGlRenderer('angle')` set; no nested HtmlInCanvas.
3. No `Math.random`, `Date.now`, `setTimeout`, GSAP callbacks; seeds fixed.
4. Heavy scenes have `premountFor`; remote assets are CORS-safe or local.
5. Path lengths clamped; `null` handled; geometry memoized.
6. Version gate: nothing newer than the project's Remotion version (check the "since" column; `interpolatePaths` needs 4.0.529).

### 7.5 Version gate list (relative to 4.0.528)

Available: TransitionSeries 4.0.59, Overlay 4.0.415, `trimBefore` on TS.Sequence 4.0.497, `useTransitionProgress`/`none` 4.0.177,
`flip` 4.0.54, `clockWipe` 4.0.74, `iris` 4.0.316, enter/exit styles 4.0.84, `shouldFadeOutExitingScene` 4.0.166, spring
`reverse` 4.0.144, `presentationDurationInFrames` 4.0.153, HTML-in-canvas presentations 4.0.456 to 4.0.467, `pushCut` 4.0.500,
`blurSlide` 4.0.523, `centerPath` 4.0.486, `getInstructionIndexAtLength` 4.0.84, `Heart` 4.0.315, rough-notation 4.0.490 (premount
props 4.0.528), `fitText` 4.0.88, `fitTextOnNLines` 4.0.313, `fillTextBox` 4.0.57, `validateFontIsLoaded` 4.0.136,
`textTransform`/`additionalStyles` 4.0.140, rounded-text-box 4.0.360, `loadFontFromInfo` 4.0.279, `loadVariableFont` 4.0.525,
`ignoreTooManyRequestsWarning` 4.0.283, `@remotion/fonts` 4.0.165, Lottie `renderer` 4.0.105 / `assetsPath` 4.0.138 / Sequence props
4.0.528, Rive `effects/className/style` 4.0.464 / crop 4.0.500 / premount 4.0.528, GIF premount 4.0.497 / crop 4.0.500 /
`requestInit` 4.0.471 / timeout 4.0.403, animated emoji 4.0.187, GSAP 4.0.517, mac cursors 4.0.513, Tailwind v4 4.0.256, SCSS
4.0.162, zod-types v4 + v3 package 4.0.426.
Not available: `interpolatePaths` (4.0.529). v5 changes to anticipate: `layout="none"` throws on TransitionSeries,
`loadFont()` requires weights and subsets, `validateFontIsLoaded` defaults to true, `getPointAtLength`/`getTangentAtLength` return
`null` past the end (already the case in 4.0.528).

---

## 8. Best examples to learn from

- `mirror/docs/transitions/presentations/custom.md`: complete mask presentation (makeStar + getBoundingBox + translatePath +
  clipPath, entering-only) and a spring timing with a very low rest threshold.
- `repo/packages/transitions/src/presentations/push-cut.tsx`: model CSS presentation (validated options, eased sub-ranges of
  progress, flash layer, outer/inner style hooks).
- `repo/packages/transitions/src/presentations/clock-wipe.tsx` and `iris.tsx`: the `clip-path: path()` + shapes idiom in 60 lines.
- `repo/packages/transitions/src/presentations/blur-slide.tsx`: production-grade two-pass WebGL2 shader (framebuffer, anti-moire
  sampling, internal easing, prop validation).
- `mirror/docs/transitions/make-html-in-canvas-presentation.md`: minimal working shader boilerplate to start custom GPU
  transitions, plus the gl-transitions porting steps in `presentations/custom-html-in-canvas.md`.
- `repo/packages/transitions/src/TransitionSeries.tsx`: the exact timing math, validation messages and presentation nesting.
- `examples/transitions-video/src/TextMask.tsx`: a TransitionSeries playing inside a text mask with a spring scale.
- `examples/light-leak-example/src/presentation.tsx`: hiding a hard switch behind a screen-blended light-leak video, timed to the
  transition length (now simpler with `TransitionSeries.Overlay`).
- `examples/text-warping/src/Warp.tsx` and `src/helpers/get-path.ts`: text to SVG path with opentype.js, reset, warp, viewBox.
- `repo/packages/example/src/Paths/PathEvolve.tsx`: spring-driven `evolvePath` on thick gradient strokes with drop shadows.
- `repo/packages/example/src/Paths/ShapesMorph.tsx`: polygon to circle morph with `PathInternals.debugPath` vertex overlay.
- `repo/packages/brand/src/effects/RoughNotationShowcase.tsx`: tuned colours, stroke widths, paddings and easing for all seven
  annotations on a paper background.
- `mirror/docs/rough-notation/highlight.md`: `Easing.spring()` inside `interpolate` easing and `Interactive.*` elements for Studio
  editing.
- `repo/packages/example/src/Title/FitTextOnNLines.tsx`: fitTextOnNLines -> measureText -> createRoundedTextBox end to end.
- `repo/packages/layout-utils/src/test/fixtures/long-unbreakable-token-fit-text.tsx`: correct rendering of returned `lines`
  (`white-space: pre`, one block per line).
- `mirror/docs/layout-utils/best-practices.md`: the fonts module + `WaitForFonts` wrapper pattern (from the Recorder).
- `repo/packages/example/src/VariableGoogleFont/VariableGoogleFont.tsx` and `GoogleFontsCjk/GoogleFontsCjk.tsx`: variable axes
  and CJK subset loading.
- `examples/morph-text/src/Composition.tsx`: gooey blur-threshold word morph (copy the filter, fix the font loading).
- `examples/typewriter/src/Composition.tsx`: minimal frame-based typewriter with caret blink.
- `mirror/docs/gsap/use-gsap-timeline.md`: the clearest statement of determinism rules; reuse its reasoning for any third-party
  animation library.
- `repo/packages/shapes/src/components/render-svg.tsx` and `repo/packages/rough-notation/src/render-annotation.tsx`: how
  shape props are routed and how annotation strokes are sequenced.

---

## 9. Open questions

1. Shader presentations on Lambda / other servers at 4.0.528: docs say supported since 4.0.455 with `swangle` default on Lambda;
   not render-tested here. Performance per frame is unknown.
2. Nesting: can a shape/Gif/Rive with `effects` (rendered through `<HtmlInCanvas>`) live inside a scene transitioned by a shader
   presentation (itself a layout-subtree canvas)? The docs forbid nested `<HtmlInCanvas>`; this combination needs a test.
3. `getPointAtLength` returns `null` past the end in 4.0.528, contradicting the docs ("from v5"). Since which 4.0.x? Treat as
   nullable everywhere.
4. rough-notation `disableMultiStroke` documented default `false` vs effective `true` in the renderer: confirm visually and tell
   the Remotion team if it is a docs bug.
5. `measureText` cache key omits `fontVariantNumeric`: likely a bug; workaround documented (R32).
6. `TransitionSeries.Sequence` `offset` is typed and implemented but undocumented: safe to use? (Series-like gaps/overlaps.)
7. `<AbsoluteFill from={n}>` (used by the pushCut docs) time-shifts children in 4.0.528 per the types; confirm with a render.
8. Upgrade policy: `interpolatePaths()` and Studio path keyframe editing need 4.0.529+. Pin 4.0.528 or move all `@remotion/*`
   packages together?
9. `@remotion/lottie`, `@remotion/rive`, `@remotion/gif`, `@remotion/animated-emoji`, `@remotion/gsap`, `@remotion/mac-cursors`,
   `@remotion/rounded-text-box`, `@remotion/fonts` and `@remotion/light-leaks`/`@remotion/effects` are not installed in
   `nexa-media/remotion-broll`; add them with `npx remotion add <pkg>` so versions match exactly.
10. The emoji name list and the 39 cursor names are only in docs components; generate the lists at runtime
    (`getAvailableEmojis()`) or from the package assets when a skill needs them.
11. `cube()` is a paid remotion.pro item: licence terms for client work not reviewed.
