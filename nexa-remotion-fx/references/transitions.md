# Transitions between scenes

`@remotion/transitions` (TransitionSeries since 4.0.59) plus the kit's `Scenes` and `tr.*`. Every fact below was
checked against the installed 4.0.528 package and on renders.

## The model

A transition is a **timing** (how long, and a 0 to 1 progress curve) times a **presentation** (a component that
styles the entering and the exiting scene from that progress). `<TransitionSeries>` is a `<Series>` whose
neighbouring scenes overlap by the transition's length. An **overlay** sits on a cut without overlapping anything.

```tsx
<TransitionSeries>
  <TransitionSeries.Sequence durationInFrames={90}><A /></TransitionSeries.Sequence>
  <TransitionSeries.Transition timing={linearTiming({durationInFrames: 20})} presentation={slide()} />
  <TransitionSeries.Sequence durationInFrames={120}><B /></TransitionSeries.Sequence>
  <TransitionSeries.Overlay durationInFrames={16}><Flash /></TransitionSeries.Overlay>
  <TransitionSeries.Sequence durationInFrames={90}><C /></TransitionSeries.Sequence>
</TransitionSeries>
```

- **Length** = sum of sequences minus sum of transitions; overlays add nothing. 90 + 120 + 90 with one 20-frame
  transition = 280. Compute it in one place (the kit's `scenesLength`) and use it for the Composition.
- **Rules (thrown as errors):** a sequence must be at least as long as the transition before it and the one after it
  (checked separately: a scene can be shorter than both together, then both overlaps share it); no two transitions in
  a row; no two overlays in a row; a transition and an overlay cannot share a cut; an overlay needs half its length
  on each side of the cut (`durationInFrames / 2 - offset` before, `durationInFrames / 2 + offset` after) and must
  not start before frame 0; `offset` must be an integer.
- **Children** may only be `.Sequence`, `.Transition` and `.Overlay` (fragments are flattened, whitespace ignored). A
  custom component wrapping a `.Sequence` throws: map arrays directly inside the series.
- **A transition first or last** animates a single scene in or out (enter or exit with nothing on the other side).
- **Nesting of presentations:** a scene with transitions on both sides is wrapped by the next transition's
  presentation (exiting) around the previous one's (entering). Mask presentations clip only the entering scene;
  the exiting one stays underneath.
- `TransitionSeries.Sequence` props on 4.0.528: `durationInFrames` (floats allowed), `offset` (integer, like
  Series.Sequence; typed but undocumented), `name`, `className`, `style`, `layout`, `showInTimeline`, `freeze`,
  `hidden`, `trimBefore` (4.0.497), `playbackRate`. `premountFor` is not in the types; it is passed through at
  runtime and premounting only acts in the Studio and Player preview (renders wait for `delayRender` anyway).
- `<TransitionSeries>` takes Sequence props (`from`, `name`, `style`...); `layout="none"` is deprecated (throws in
  v5).

## Timings

| Timing | Signature | Notes |
|---|---|---|
| `linearTiming` | `{durationInFrames, easing?}` | clamped interpolate from 0 to 1 with the easing (`Easing.bezier(...)`) |
| `springTiming` | `{config?, durationInFrames?, durationRestThreshold? (0.005), reverse?}` | length = `durationInFrames` if set, else the measured spring (depends on fps). ALWAYS pass `durationRestThreshold: 0.001` or the end snaps. `damping: 200` = no overshoot. `reverse` plays the time-reversed curve |
| custom | `{getDurationInFrames({fps}), getProgress({frame, fps})}` | deterministic; springs can be added (two half springs with a pause) |

`timing.getDurationInFrames({fps})` gives the overlap. `springTiming({config: {damping: 200}})` measures 23 frames at
30 fps.

## Presentations: CSS (any browser)

| Presentation (import) | Since | Options (defaults) | What it does |
|---|---|---|---|
| `fade()` (`/fade`) | 4.0.53 | `enterStyle`, `exitStyle`, `shouldFadeOutExitingScene` false | the incoming scene fades in over the outgoing one, which stays opaque: transparent scenes show both, so set the flag |
| `slide()` (`/slide`) | 4.0.53 | `direction` from-left (from-right, from-top, from-bottom), `enterStyle`, `exitStyle` | the incoming pushes the outgoing out; the default of every Transition |
| `wipe()` (`/wipe`) | 4.0.53 | `direction` from-left (+ 4 diagonals), outer and inner enter and exit styles | a polygon reveal; diagonals move twice as far |
| `flip()` (`/flip`) | 4.0.54 | `direction`, `perspective` 1000 | a 3D card turn; not in client-side rendering |
| `clockWipe({width, height})` (`/clock-wipe`) | 4.0.74 | width and height required | a pie sweep from 12 o'clock |
| `iris({width, height})` (`/iris`) | 4.0.316 | width and height required | a circle from the centre |
| `none()` (`/none`) | 4.0.177 | `enterStyle`, `exitStyle` | nothing: animate elements with `useTransitionProgress()` |
| `pushCut()` (`/push-cut`) | 4.0.500 | `cutProgress` 5/11 (0..1 exclusive), `outgoingScale` 1.04, `incomingStartScale` 1.04, `incomingEndScale` 1.07, `transformOrigin`, `flashColor` #f5f2ed, `flashOpacity` 0.2, `flashFrames` 2, styles | editorial hard cut with a punch-in and a faint flash; use linear timing (11 frames); the incoming scene is invisible until the cut but its clock runs: delay its content by the hidden frames and lengthen it by the same |

Enter and exit styles are static for the whole overlap (they do not animate): use them for things that hold, like a
shadow or z-index; for animated depth write a custom presentation.

## Presentations: shaders (HTML-in-canvas plus WebGL2)

All twelve render on 4.0.528 with `--gl=angle` (verified). They need Chrome 148+ with the canvas-draw-element flag to
preview. Every factory except `blurSlide` requires an options object in its type (`dissolve({})`), and every one
also takes `effects` (run on the shader output).

| Presentation | Since | Options (defaults) | Look | Length |
|---|---|---|---|---|
| `blurSlide` (also root export) | 4.0.523 | `direction` from-left, `blur` 0.5 (fraction of the frame) | whip pan with real blur; eases itself: linear timing | 16 to 20 |
| `zoomBlur` | 4.0.456 | `rotation` PI/6 (radians) | zoom out with a turn, zoom in from the other angle | 20 to 24 |
| `zoomInOut` | 4.0.457 | none | zoom to the viewer, crossfade, zoom back | 24 to 28 |
| `crossZoom` (root) | 4.0.467 | `strength` 0.4 | zoom across a moving centre with blur | 22 to 26 |
| `dreamyZoom` (root) | 4.0.466 | `rotation` 6 (DEGREES), `scale` 1.2 | zoom and turn through a white bloom | 24 to 28 |
| `linearBlur` (root) | 4.0.466 | `intensity` 0.1 | directional blur crossfade | 18 to 22 |
| `filmBurn` (root) | 4.0.467 | `seed` 2.31 | film burn glow through white | 28 to 32 |
| `dissolve` | 4.0.465 | `lineWidth` 0.1, `spreadColor` #ff0000, `hotColor` #e6e633 (6-digit hex only), `pow` 5, `intensity` 1 | luminance burn with a glowing edge | 28 to 32 |
| `ripple` | 4.0.465 | `amplitude` 100, `speed` 50 | water rings while crossfading | 28 to 32 |
| `crosswarp` | 4.0.466 | none | the scenes warp against each other | 24 to 28 |
| `swap` | 4.0.466 | `reflection` 0.4, `perspective` 0.2, `depth` 3 | the scenes swap in perspective over a floor | 28 to 32 |
| `bookFlip` | 4.0.466 | `direction` from-right | a shaded page turn | 30 to 34 |

Traps, measured on 4.0.528:

- **CSS in, shader out:** a shader transition gets no picture of a scene that entered with a CSS transition (the
  entering CSS presentation wraps the scene but never captures it for the exiting shader), so the shader plays as a
  hard cut. Shader in then CSS out works; shader to shader works. Fix by hand: split the scene into two sequences,
  the first the whole scene hiding itself at `duration - L`, the second `L` frames long with `offset={-L}` holding
  the same scene with `<Sequence from={-(duration - L)}>` so its clock continues. The kit's `Scenes` does this.
- **No HTML-in-canvas inside:** a scene next to a shader transition must not contain `<HtmlInCanvas>` (or effects on
  shapes, Gif and Rive, which render through it): it waits for "first paint after canvas resize" until the render
  times out. Effects on `Img`, `Video` and `Solid` are fine there (their own canvas is captured like any DOM).
- A canvas look wrapped around a whole TransitionSeries works with CSS transitions inside, never with shader ones.

### Your own shader transition: `makeHtmlInCanvasPresentation(shader)` (4.0.456)

`shader(canvas: OffscreenCanvas)` returns `{draw, clear, cleanup}`. Create the WebGL2 context once
(`{premultipliedAlpha: true}`), compile, make textures. `draw({prevImage, nextImage, width, height, time,
passedProps})`: the images are OffscreenCanvas or null (upload with `texImage2D`); `time` 1 = the exiting scene,
0 = the entering one (use `progress = 1 - time`); with no prevImage force time 0, with no nextImage force time 1.
`clear()` runs when nothing is mounted, `cleanup()` once. The result is a factory `(props & {effects?}) =>
TransitionPresentation`. Porting a gl-transitions.com shader: `getFromColor(uv)` becomes `texture(u_prev, uv)`,
`getToColor(uv)` becomes `texture(u_next, uv)`, add `float progress = 1.0 - u_time;`, output from `main()`. The
standard quad flips v (`v_uv = vec2(x * 0.5 + 0.5, 0.5 - y * 0.5)`); use CLAMP_TO_EDGE unless the effect wraps.

## Custom CSS presentations

`TransitionPresentation<P> = {component, props}`; the component receives `children`, `presentationDirection`
('entering' | 'exiting'), `presentationProgress` (0 to 1 after the timing), `presentationDurationInFrames`,
`passedProps`, and internal HTML-in-canvas callbacks to ignore. Return `<AbsoluteFill>` wrappers.

```tsx
const Circle: React.FC<TransitionPresentationComponentProps<{w: number; h: number}>> = ({children, presentationDirection, presentationProgress: p, passedProps: {w, h}}) => {
  const r = Math.hypot(w, h) / 2 * p;
  const d = translatePath(makeCircle({radius: r}).path, w / 2 - r, h / 2 - r);
  return <AbsoluteFill style={{clipPath: presentationDirection === 'entering' ? `path('${d}')` : undefined}}>{children}</AbsoluteFill>;
};
export const circle = (props: {w: number; h: number}): TransitionPresentation<{w: number; h: number}> => ({component: Circle, props});
```

Ideas and their numbers: zoom-through (outgoing `scale = 1 / distance` with distance from 1 toward 0.2, mostly linear
with a little ease-in so it moves from the first frame; the incoming scene waits until about 40 percent, then grows
from 0.8 to 1 as its blur clears, landing by 90 percent),
whip pan (both scenes translate together, directional blur from the speed), wheel spin (rotate about a pivot far
outside the frame, `transform-origin: -400% 50%`), CSS cube (`perspective` on the parent, faces turned 90 degrees
about the shared edge, `backface-visibility: hidden`), light-leak cut (the switch hides at the leak's brightest
moment). Clip ids: generate them with `useId()`, or use `clip-path: path()` and no ids at all.

## Overlays and per-element choreography

- `<TransitionSeries.Overlay durationInFrames offset?>` (4.0.415): centred on the cut; `useCurrentFrame()` inside
  starts at 0 at the overlay's start and `useVideoConfig().durationInFrames` is its length. For flashes, light leaks,
  glitch hits and sound on a hard cut.
- `none()` plus `useTransitionProgress()` (4.0.177) gives `{entering, exiting, isInTransitionSeries}` inside each
  scene (`entering` 0 to 1 on the entering scene, `exiting` 0 to 1 on the exiting one, 1 and 0 outside a
  transition), already eased by the timing. Stagger elements with sub-ranges (`interpolate(entering, [0.3, 1], ...)`).
  The kit's `tr.choreo()` is this.

## Sound on a cut

Either wrap the presentation so the entering side also renders an `<Audio>` (it starts when the transition starts),
or place `<Sequence from={cut - lead}><Audio src /></Sequence>` outside the series. The kit's `sound: {src, volume,
lead}` on any `tr.*` does the second, with `lead` = frames before the cut (default: from the start of the
transition). A whoosh peaks a few frames after it starts: set `lead` so the peak lands on the cut.

## The kit: `Scenes` and `tr`

`Scenes` builds the series from `[{node, duration, transition, name, premountFor}]` with optional `enter` and `exit`,
runs `planScenes` first and throws a readable error, fills in the frame size for iris and clock wipe, uses springs
with a 0.001 rest threshold, delays the content of scenes that follow a hard-cut style (pushCut 5 of 11 frames,
glitchCut half, lightLeakCross 42 percent) so their first visible frame is their own frame 0, marks scenes next to
shader transitions (looks there use their css engine), splits CSS-in/shader-out scenes, and places transition
sounds. `planScenes(scenes, fps, {enter, exit})` returns `total`, `starts`, `durations`, `delays`, `joints` (with the
cut frame of each), `problems` and `warnings`.

Presets (frames at 30 fps, scaled for other rates): css `fade` 15, `slide` 20, `wipe` 20, `flip` 26, `clockWipe` 26,
`iris` 24, `pushCut` 11, `choreo` 20; kit css `zoomThrough` 22, `whipPan` 12, `glitchCut` 12, `lightLeakCross` 36,
`blurDissolve` 24, `maskReveal` 26 (circle or any mask shape from a point, or a 'diagonal' edge with an accent bar);
shaders `blurSlide` 18, `zoomBlur` 22, `crossZoom` 24, `filmBurn` 30, `dissolve` 30 (theme colours), `linearBlur` 20,
`dreamyZoom` 26, `swap` 30, `ripple` 30, `crosswarp` 26, `bookFlip` 32, `zoomInOut` 26; overlays `flash` 10, `leak`
40; `cut`.

## Choosing a transition

| Intent | Choose | Length at 30 fps |
|---|---|---|
| Same subject, calm continuity | `fade`, `blurDissolve`, `choreo` with per-element moves | 15 to 24 |
| Next step, spatial flow | `slide` or `wipe` in the reading direction | 18 to 22 |
| Reveal from a point, a result | `iris`, `maskReveal` from the element that caused it, `clockWipe` for time | 22 to 28 |
| Two sides of one thing | `flip` | 24 to 28 |
| Editorial punch, social | `pushCut`, or a hard cut plus a `flash` overlay | 8 to 12 |
| Energy, music, trailers | `whipPan`, `blurSlide`, `zoomThrough`, `zoomBlur`, `crossZoom` | 12 to 24 |
| Tech, error, a drop | `glitchCut` | 10 to 14 |
| Warm, nostalgic, film | `lightLeakCross`, `leak` overlay, `filmBurn` | 30 to 40 |
| Storybook, magazine | `bookFlip` | 30 to 34 |
| Playful, dreamy | `ripple`, `dreamyZoom`, `swap`, `crosswarp` | 26 to 32 |

House rules: one family per film plus one signature transition used two or three times; carry the direction of
motion across the cut; hard cuts between kinetic-type beats; never leave a spring at the default rest threshold;
a scene holds its reading time outside its overlaps; two heavy scenes overlapping double the render cost of those
frames.
