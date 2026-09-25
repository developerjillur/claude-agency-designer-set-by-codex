# Remotion APIs for interface animation, and their traps (4.0.528)

The kit's ui module is built from a small set of Remotion primitives. This file lists them with the version they
appeared in (checked against the installed 4.0.528 types), how the kit uses them, and the errors people hit.

## 1. Time and value

- `useCurrentFrame()`: the only clock; inside a `<Sequence from={n}>` it starts at 0 on frame n.
- `useVideoConfig()`: `width`, `height`, `fps`, `durationInFrames`. Inside a Sequence `durationInFrames` is that
  Sequence's length (accounting for trims and speed), which is how kit overlays end their exit on the Sequence's last
  frame. The kit reads it through core's `useStage()`, which adds `unit` (short side / 1080) and the `safe` box.
- `interpolate(input, inputRange, outputRange, options)`: options `easing` (one function or one per segment since
  4.0.462), `extrapolateLeft/Right` (`'extend'` default, `'clamp'`, `'wrap'`, `'identity'`), `posterize` (4.0.470: hold
  each value n frames), `output: 'perceptual-scale'` (4.0.490: even perceived growth for scales), CSS string outputs
  such as `'0px 30px'` or `'-8deg'` (4.0.472). Always clamp both ends; an easing may still overshoot inside the range
  (that is how `outBack` presses spring past rest).
- `Easing.bezier(...)`, `Easing.in/out/inOut(...)`, `Easing.spring({damping, mass, stiffness, allowTail,
  durationRestThreshold})` (4.0.476; `allowTail` and the threshold 4.0.483): a spring stretched over a segment.
- `spring({frame, fps, config, delay, durationInFrames, from, to})`: physical progress that may overshoot; the kit uses
  it through motion's `springAt` with named configs (`settle` for bubbles and cards, `pop` for checks and badges,
  `snappy` for toggles).
- `measureSpring({fps, config, threshold})`: frames a spring needs (damping 200 at 30 fps: 23).
- `interpolateColors(input, range, colours)`: RGB interpolation of any CSS colour (`oklch()` accepted since 4.0.439,
  but blended in RGB). The kit uses it to mix and parse colours.
- `random(seed)`: the seeded random; `Math.random()` flickers across render tabs.

## 2. Structure

- `<Sequence from durationInFrames layout name premountFor>`: `layout="none"` keeps children in normal flow (the kit
  uses it for sounds and tooltips); `premountFor` (4.0.140) mounts heavy children early. `<Series>` for back-to-back
  scenes, `<Freeze frame>` to hold a subtree.
- `<AbsoluteFill>` takes Sequence timing props directly since 4.0.501.
- `Interactive.Div` and friends (4.0.475) make layers editable in Studio; `cropLeft/Right/Top/Bottom` on them (4.0.506)
  are an alternative to `clipPath: inset()` wipes.
- `staticFile('ui/click.wav')` for assets in `public/`.

## 3. Media and sound

- `<Audio>` from `@remotion/media`: `src`, `volume` (number or function of the frame), `trimBefore`, `trimAfter`,
  `playbackRate`, `loop`, `muted`, and `from`/`durationInFrames` directly on the tag (4.0.445). The kit wraps it in a
  `Sequence layout="none"` per click.
- Measured on 4.0.528: in an H.264 + AAC MP4 the audio is about 1.3 frames late at 30 fps (2048 samples of AAC
  priming at 48 kHz, the audio stream 56 ms longer than the video). Sync to within a frame needs nothing; frame-exact
  needs `offset={1}` in `ClickSounds` or `from={frame - 1}`.
- `@remotion/sfx` (4.0.429+): 32 URL constants on remotion.media; only `whoosh`, `whip`, `uiSwitch`, `mouseClick`,
  `pageTurn`, `shutterModern`, `shutterOld` are CC0, the rest are meme sounds without a clear licence. Copy files into
  `public/` for offline and Lambda renders.
- `<Video>` from `@remotion/media` or `<OffthreadVideo>` for screen recordings inside a frame; `<Img>` for screenshots
  (they hold the frame until loaded; native `<img>` does not).

## 4. Text

- Fonts only through core (`loadKitFont`, `fontStack`, the theme's `t.type.*`); a family name in CSS alone loads
  nothing and renders a fallback.
- `@remotion/layout-utils` `measureText`, `fitText` (4.0.88), `fitTextOnNLines` (4.0.313): results are cached for the
  page's life and keyed without `fontVariantNumeric`; a measurement taken before the font loaded stays wrong.
  `validateFontIsLoaded: true` turns that into an error. The ui module avoids measuring: it grows rows with CSS grid
  (`gridTemplateRows: minmax(0, p fr)`) and fixes widths it needs (buttons that swap labels).
- `Intl.Segmenter` (grapheme) to split Bangla safely for typing; never `split('')`.
- `textWrap: 'balance'` works in the render browser for subtitles; titles get explicit `\n` breaks.
- `@remotion/rough-notation` (4.0.490) `<Highlight>`, `<Underline>`, `<Circle>` wrap inline text for hand-drawn
  emphasis on UI copy; pass a translucent colour to `<Highlight>` (it draws behind the text but defaults to the
  text colour).

## 5. Transitions and paths

- `@remotion/transitions` (`<TransitionSeries>`, `slide`, `wipe`, `fade`, `iris`...): for scene changes; inside a
  screen box it also changes app screens. Use `springTiming({config: {damping: 200}, durationRestThreshold: 0.001})`
  (the default threshold snaps at the end). `fade()` keeps the old scene opaque unless the new one is opaque.
- `@remotion/paths`: `evolvePath(progress, d)` for draw-on strokes, `getPointAtLength`/`getTangentAtLength` for moving
  a pointer along a drawn path (they return null past the end in 4.0.528: clamp the length). `interpolatePaths` is
  4.0.529 and not available here.
- `@remotion/shapes` `makeRect`, `makeCircle`, `makeCallout` for simple marks and speech shapes.
- `@remotion/mac-cursors` `<MacOSCursor cursor="pointer" />` (4.0.513) draws system cursors with the hotspot at the
  origin; not installed in the shared modules here.

## 6. Rendering

- Stills and contact sheets: `nrk.py demos --module ui` (the kit), `nrk.py stills` and `nrk.py still` (projects). The
  kit's check folder is cleared on every `demos` run, so render all demos in one run before comparing sheets.
- Composition ids: letters, numbers and `-`.
- `--gl=angle` is set by nrk; the ui module needs no WebGL.
- 4K: the ui module scales with `unit`; render 1080p layouts at `--scale=2` or build a 3840 x 2160 composition; both
  give the same composition.

## 7. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| An element visible before it should appear | `interpolate` without clamping | clamp both ends (the kit's `ramp` and `track` do) |
| Values flicker between frames in the render | `Math.random()`, `Date.now()`, CSS animations or transitions | seeded `random()`, frame-pure maths |
| Absolute children collapse to zero height inside a scrolled or scaled wrapper | a CSS transform makes the wrapper their containing block | give the content an explicit height |
| Wrong or fallback font in the first frames | a font named in CSS without loading | load through core |
| A text measurement is wrong forever | measured before the font loaded (cache) | avoid measuring, or measure after `waitUntilDone()` with `validateFontIsLoaded` |
| Render slow for no visible gain | `backdrop-filter`, stacked large blurs | solid 90 to 96% surfaces; small blurs only |
| Held text shimmers between tabs | `will-change` on text | never on text in renders |
| Sound missing in an offline or Lambda render | remote `@remotion/sfx` URL | copy the file into `public/` |
| `Cannot destructure property 'x' of null` | `getPointAtLength` past the end | clamp the length |
| A spring transition snaps at its end | default `durationRestThreshold` 0.005 | 0.001 |
| The composition list hangs | `delayRender()` at module top level | create handles in a `useState` initializer |
| Typecheck error on an unknown API | a docs page describing 4.0.529 or later | check the installed `.d.ts` files first |
