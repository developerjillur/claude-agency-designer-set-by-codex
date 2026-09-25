# The timing model (4.0.528)

## One rule for every timing container

For a child at parent frame `t`: `childFrame = trimBefore + (t - from) * playbackRate`, and the child is mounted only
while `from <= t < from + durationInFrames` (parent frames). Outside that window it is unmounted, not hidden. Inside,
`useVideoConfig().durationInFrames` is the local end of the window (including trims and speed: 40 visible frames at
`playbackRate={2}` with `trimBefore={10}` report 90). Nesting cascades: `from={60}` inside `from={30}` starts at 90.

Timing containers: `Sequence`, `Series.Sequence`, `AbsoluteFill` (4.0.501), `Interactive.*`, `Img`, `CanvasImage`,
`AnimatedImage`, `Solid`, `HtmlInCanvas`, `Gif`, `Lottie`, `ThreeCanvas` (4.0.528), `@remotion/shapes`,
`@remotion/rough-notation`, and `Video`/`Audio` from `@remotion/media` (plus `trimAfter` and `loop`).

## Sequence

| Prop | Default | Since | Notes |
|---|---|---|---|
| `from` | 0 | | negative values trim the start of the content |
| `durationInFrames` | Infinity | | an infinite Sequence never ends, so exits timed to its end never play |
| `trimBefore` | 0 | 4.0.482 | children start part-way in |
| `playbackRate` | 1 | 4.0.528 | constant; nested rates multiply; the window in the parent does not change |
| `freeze` | | 4.0.476 | holds the children at a local frame without remounting |
| `premountFor` | 0 | 4.0.140 | mounts early for smooth preview (renders are not affected); 5.0 makes it `fps` by default |
| `postmountFor` | | 4.0.340 | stays mounted after the end (backwards seeking) |
| `layout` | 'absolute-fill' | | `'none'` removes the wrapper (needed inside ThreeCanvas) |
| `width`, `height` | | 4.0.80 | the children see this size in `useVideoConfig()` |
| `cropLeft/Right/Top/Bottom` | | 4.0.500 | 0 to 1, animatable: wipes without masks |
| `hidden` | false | 4.0.462 | not rendered |
| `name`, `showInTimeline` | | | Studio timeline |

Nested clocks, in practice:
- `durationInFrames` stays in parent frames, so a slowed Sequence (`playbackRate` below 1) cuts off its last keyframes
  unless its length is extended by the same factor.
- A frame read in the parent is not retimed by the child: pass values down, or read the frame inside the child.
- `trimBefore` equal to `from` keeps a late-mounted child on the master clock (useful for global audio analysis).
- A Sequence with `width` and `height` works as a movable sub-canvas: move or scale it like a camera over a panel.

Media order of operations: `from`, `trimBefore` and `trimAfter` choose the source range; `playbackRate` stretches
it; `loop` repeats it; `durationInFrames` cuts the timeline length last.

## Series

`<Series>` is a Sequence (4.0.443) stacking `<Series.Sequence durationInFrames offset>`: a positive `offset` leaves a
gap, a negative one overlaps the previous scene and shifts everything after it. Only the last scene may be infinite.
`playbackRate` on a scene changes its speed, not its length.

## TransitionSeries (`@remotion/transitions`)

- Total length = sum of the sequences minus the sum of the transitions.
- Each sequence must be at least as long as each transition touching it.
- `linearTiming({durationInFrames, easing})` or `springTiming({config, durationInFrames, durationRestThreshold})`;
  pass `durationRestThreshold: 0.001` to springs (the default 0.005 snaps at the end); spring lengths depend on fps.
- Lengths must be whole frames: fractional lengths break the series (round every computed duration).
- `<TransitionSeries.Overlay>` puts something over a cut without shortening the total (a light leak, a flash).
- Wrapping `TransitionSeries.Sequence` in your own component throws: use it directly.
- `pushCut` (4.0.500): the incoming scene's clock runs while hidden, so delay its content by the pre-cut frames.
- Details and the shader transitions: `nexa-remotion-fx`.

## Loop and Freeze

- `<Loop durationInFrames times>`; nested loops cascade; `Loop.useLoop()` gives `{durationInFrames, iteration}` to
  vary each repeat deterministically; `playbackRate` (4.0.528) speeds up each iteration.
- `<Freeze frame active>`: children see that frame; videos pause, audio mutes. Prefer `<Sequence freeze>`.

## Arithmetic worth knowing

- Last frame = `durationInFrames - 1`. An exit of `n` frames that must finish on the last frame starts at
  `durationInFrames - 1 - n` (the kit's default).
- Frames from seconds: `Math.round(seconds * fps)`; write timings as seconds times fps so a composition can switch
  between 30 and 60 fps.
- Keyframes computed from a duration (`[0, 20, d - 20, d]`) throw when `d < 40`: guard short beats.
- A speed ramp on media needs `OffthreadVideo` and the sum of speeds up to each frame (the new Video's rate cannot
  change over time): see `nexa-remotion-edit`.
