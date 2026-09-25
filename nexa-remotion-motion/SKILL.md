---
name: nexa-remotion-motion
description: "Motion design for Remotion videos: timing, easing curves, springs, entrances and exits, staggers, choreography, holds and reading time, pacing, camera moves over a large world, parallax, push-ins, shakes, idle drift, motion blur, stepped (on twos) motion, loops, beat sync and word-locked cues, with the kit's Animate, Stagger, Camera, Parallax, PushIn, Shake, Float and MotionBlur components and measured defaults. Use it whenever a Remotion scene needs to move well or feels stiff, rushed, floaty or like a slideshow, Banglish included ('animation smooth koro', 'motion ta aro professional koro', 'camera move add koro'). Part of the nexa-remotion family."
---

# Motion for Remotion

How things move: when they arrive, how long they stay still, how they leave, and how the camera travels. Part of the
nexa-remotion family (the director skill is `nexa-remotion`; the kit is in `~/.claude/skills/nexa-remotion/kit`,
and a project made with `nrk.py new` imports these parts from `./kit`).

## Fast path

1. Start from the voice: the cue table says which word each element lands on (`nexa-remotion` process step 4).
2. Pick the theme; its `motion` block sets the entrance style, frames, stagger, distance, curve and spring.
3. Wrap each element in `<Animate>` (or a list in `<Stagger>`) inside the `<Sequence>` of its beat; give `delay` in
   frames from the cue table. Add `out` only for things that leave before the cut.
4. Hold: every settled text stays still for at least `readingFrames(text, fps)`; the camera or the ground carries
   the life (`<PushIn>`, a slow `<Camera>` move, `<Float>` on pictures).
5. Check with `nrk.py stills PROJECT --frames` at each cue and 12 frames later, then watch a draft render for speed.

## Components (from `./kit`)

| Component or helper | Use it for | Key props |
|---|---|---|
| `Animate` | an entrance and an optional exit for anything | `in` (19 reveals), `out`, `delay`, `duration`, `outDuration`, `outAt`, `distance`, `ease`, `origin`, `inline` |
| `Stagger` | children arriving one after another | `each`, `delay`, `order` (forward, reverse, center, random), `outEach`, plus Animate's props |
| `Camera` + `Parallax` | a camera travelling over a world larger than the frame, layers at depths | `keys` [{at, x, y, zoom, rotate}], `ease` (one or per segment), `world`; `Parallax depth` |
| `ZoomAt` | a punch-in about a fixed point (the clicked button stays put) | `x`, `y`, `from`, `to`, `at`, `duration`, `backAt` |
| `PushIn` | the slow life of a held shot | `amount` (0.035), `lift`, `origin`, `ease` |
| `Shake` | impacts, drops, bass hits | `from`, `duration`, `amp`, `rotate`, `freq` |
| `Float` | idle drift of pictures and objects after they land (never text being read) | `amp`, `rotate`, `freq` (0.3 to 0.6), `delay`, `lane` |
| `MotionBlur`, `Trail` | blur on fast moves; echo trails | `samples` (5 to 8), `shutter`; `layers`, `lagInFrames`, `trailOpacity` |
| `ramp`, `track`, `inHoldOut` | 0 to 1 progress; keyframe tracks; enter-hold-exit values | frames, curve or curves per segment |
| `springAt` | a spring from a delay with a named config | `delay`, `config`, `durationInFrames` |
| `useLife`, `frameAtProgress` | enter, exit and visible progress of the enclosing Sequence; the frame an eased move reaches a value | `inFrames`, `outFrames`; `target`, `start`, `duration`, `ease` |
| `wiggle`, `pulse`, `inertia`, `onTwos`, `loop`, `pingPong`, `moveFrames` | noise wobble, bounded pulses, damped settles, stepped time, loops, move length from distance | see `references/helpers.md` |
| `curves`, `springs`, `appleSpring`, `springEase` (core) | named easing curves and springs | see `references/easing-and-springs.md` |

Reveals: `fade`, `rise`, `drop`, `left`, `right`, `pop`, `grow`, `zoom`, `blur`, `mask`, `maskDown`, `wipe`,
`wipeLeft`, `wipeUp`, `wipeDown`, `iris`, `flip`, `swing`, `none`. Exits keep travelling the way things move (a
`rise` leaves upwards). The exit ends on the last frame of the enclosing Sequence unless `outAt` says otherwise.

## Craft rules (30 fps; `at30()` scales them)

- **Durations.** Small UI 8 to 11 frames; cards and lines 15 to 20; calm or premium 18 to 28. Exits 12 to 18 with
  ease-in, or none. Bigger or farther moves get more frames, by the square root of the distance ratio
  (`moveFrames`).
- **Curves by role.** Arrivals `curves.out` (`outCubic` for moves under about 60 px: strong curves freeze for several
  frames at the end of short travel); departures `curves.in`; on-screen moves and the camera `curves.inOut`; clocks
  `linear`; pops `outBack`. Never ease-in for an arrival.
- **Springs.** `calm` (no overshoot, settles in 23 frames) by default; `settle` (2.5% overshoot) for a hint of life;
  `pop` or `bouncy` (about 21% overshoot) for one hero per act; Remotion's own default (damping 10) overshoots 16%, so
  always pass a config. Derive custom ones with `appleSpring(duration, bounce)`.
- **Travel.** 10 to 32 px for entrances at 1080; scale from 0.86 to 0.99, never from 0; never opacity alone. No
  element crosses more than a third of the frame without an intermediate change.
- **Stagger.** 2 to 4 frames in one gesture, 5 or 6 for a list, in reading order; the whole run lands before the
  next cue; four or more items: shrink the step or split across cues.
- **Holds.** Settle, then hold 30 to 45 frames before any exit; reading time from `readingFrames`; logos 1 s after
  landing. Text is perfectly still while read.
- **Pacing.** A new beat every 3 to 9 s, something new every 2 to 4 s, nothing fully static over 3 s, one focal
  move at a time. First cuts are too fast: hold longer.
- **Camera.** Moves of 14 to 24 frames with in-out ease; about 3 per chapter; hold on two near-identical keys so an
  editor can cut anywhere; put the zoom origin on what matters; motion blur on fast travel only.
- **Principles.** Anticipation (2 or 3 frames back before a committed move), follow-through (attached parts settle
  2 to 4 frames after the body), arcs (different eases on x and y), staging (dim or blur what has paid off),
  exaggeration only on the hero beat.
- **Beat sync** only for really rhythmic music: cuts on downbeats, small events snapped within 6 frames
  (`snapToBeat`), at most three whole-frame hits per film; motion size never pumps with the beat.

## Recipes

Title that masks in by word, then leaves at the end of its beat:
```tsx
<Sequence from={cue.title} durationInFrames={90}>
	<SafeArea>
		<h1 style={{fontFamily: t.type.display, fontSize: 120 * unit}}>
			<Stagger in="mask" out="mask" each={4} inline>
				{'Invoices in one tap'.split(' ').map((w) => <span key={w} style={{marginRight: '0.25em'}}>{w}</span>)}
			</Stagger>
		</h1>
	</SafeArea>
</Sequence>
```

A camera tour over a board of cards, with a far layer:
```tsx
<Camera world={{width: 3840, height: 2160}} keys={[
	{at: 0, x: 1920, y: 1080, zoom: 0.5}, {at: 30}, {at: 70, x: 800, y: 600, zoom: 1.15}, {at: 110}, {at: 150, x: 3000, y: 1500, zoom: 1},
]}>
	<Parallax depth={0.5}><DotGrid /></Parallax>
	<Cards />
</Camera>
```

A price tag that lands on its word with a small settle (`cue.price` from the transcript):
```tsx
const s = springAt(frame, fps, {delay: cue.price - 8, config: 'settle'});
<div style={{scale: `${0.9 + 0.1 * s}`, opacity: Math.min(1, s * 1.5)}}>$116</div>
```

A hand-animated feel for a whole scene: drive the scene from `onTwos(frame)` (pass it down) or set `posterize: 2`
on its interpolations; keep footage at full rate.

A fast whip with blur (the child must read the frame itself):
```tsx
const Whip: React.FC = () => { const f = useCurrentFrame(); const x = ramp(f, 8, 10, curves.inOutExpo) * 1400; return <Card style={{translate: `${x}px 0px`}} />; };
<MotionBlur samples={6}><Whip /></MotionBlur>
```

## Remotion 4.0.528 facts and traps

- Inside a `<Sequence>`, `useCurrentFrame()` starts at 0 and `useVideoConfig().durationInFrames` is the Sequence's
  length (the kit's exits rely on it). A Sequence without `durationInFrames` is infinite: exits never fire.
- `interpolate` input ranges must be strictly increasing; keyframes computed from a short duration throw. Clamp both
  ends. Per-segment `easing` arrays need one curve per segment (4.0.462).
- `Easing.spring()` (4.0.476) makes a spring into a curve for `interpolate` (measured as if 30 frames long and
  stretched to the segment); `allowTail` lets it settle past the segment.
- `interpolate` accepts CSS strings for `translate`, `scale`, `rotate` (4.0.472) and tuples (4.0.473);
  `output: 'perceptual-scale'` (4.0.490) evens out scale changes; `posterize` (4.0.470) steps values.
- `spring()` without a config bounces (damping 10). `measureSpring()` gives the settle length (calm: 23 frames).
- `@remotion/noise` caches only a few seeds: one seed, many lanes (the kit's `wiggle` does this).
- `CameraMotionBlur` renders its children `samples` times at sub-frame times: the child component must call
  `useCurrentFrame()` itself, or nothing blurs; it costs a full render per sample.
- `Sequence` `playbackRate` (4.0.528) and `freeze` (4.0.476) change time for a whole subtree.
- CSS animations only through the play-state technique; GSAP only as a paused timeline seeked by frame
  (`useGsapTimeline`, 4.0.517, throws on callbacks and random values).

## References

- `references/easing-and-springs.md`: every named curve and spring with numbers, the Apple formula, Easing.spring,
  perceptual scale, posterize.
- `references/choreography.md`: staging, cue tables, reading time, holds and pacing, stagger arithmetic, camera rigs,
  parallax, beat sync, the animation principles, After Effects expressions in Remotion.
- `references/timing-model.md`: Sequence, Series, Loop, Freeze, TransitionSeries, premounting and speed, with the
  arithmetic.
- `references/helpers.md`: every helper in the kit's core and motion modules with its signature.
