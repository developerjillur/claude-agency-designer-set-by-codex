# Editing: cuts, speed, layouts and the maths behind them

An edit is data: a list of source ranges with speeds, laid on a timeline. Build that list first, derive the
composition length from it, and move every timed thing (captions, cues, B-roll, ducking windows) through the same
list. The kit's `edl.ts`, `speed.ts` and layout components do this; raw Remotion patterns are shown where the kit has
no component.

## 1. The timing algebra

Five props, applied in this order, turn a file into frames on a timeline:
1. `from`: where the item starts on its parent (frames). Nested Sequences add up.
2. `trimBefore` / `trimAfter`: which source range, in frames at the composition fps, from the file's start.
   `trimAfter` is a position.
3. `playbackRate`: stretches the range; timeline length = `(trimAfter - trimBefore) / playbackRate`.
4. `loop`: repeats the stretched range.
5. `durationInFrames`: cuts the item off last.

At parent frame t the item shows source frame `trimBefore + (t - from) * playbackRate`. Children are mounted only
while `from <= t < from + durationInFrames`; inside, `useVideoConfig().durationInFrames` is the local length.
Since 4.0.528 `<Sequence>` and `<Series.Sequence>` also take a constant `playbackRate` that multiplies down the tree
(media included) and `trimBefore` (4.0.482 / 4.0.497); `freeze` (4.0.476) holds children at a frame.

## 2. Edit lists and jump cuts

```tsx
const ranges = [[1.2, 4.8], [6.1, 9.0], [11.4, 15.2]] as const;   // seconds kept
const edit = buildEdit(ranges, fps);                               // {from, length, trimBefore, rate}[]
// Composition: durationInFrames = editLength(ranges, fps)
<Series>
	{edit.map((p) => (
		<Series.Sequence key={p.index} durationInFrames={p.length} premountFor={fps}>
			<Clip src={src} trimBefore={p.trimBefore} playbackRate={p.rate} />
		</Series.Sequence>
	))}
</Series>
```
That is what `<JumpCuts>` does, plus a punch-in on every second piece. Rules:
- Round source positions once (`buildEdit`) and use those pieces for picture, captions and cues, so all agree to the
  frame.
- Premount each piece 1 to 1.5 s for smooth preview; renders are exact without it.
- The old one-element pattern (a single `<OffthreadVideo>` whose `trimBefore` jumps, with `#t=0,` on the URL) avoids
  remounts but downloads the whole file; the Series pattern is the current advice.

**Ranges from words** (`keepRanges`): merge words closer than 0.45 s, pad 0.12 s before and 0.2 s after, clamp to the
file. Clean whisper output first: drop `[BLANK_AUDIO]`, `[PAUSE]`, `[Silence]`, `[INAUDIBLE]`, `TT_n` and blank tokens.
The Recorder trims a take to the first word minus `ceil(fps / 4)` frames and the last word plus `fps / 2` frames.

**Ranges from silence**: in a Node script, `getSilentParts({src: absolutePath, noiseThresholdInDecibels: -30,
minDurationInSeconds: 0.4})` from `@remotion/renderer` returns `audibleParts`; tune the threshold per recording (the
default -20 dB loses quiet speech). Or `ffmpeg -i talk.wav -af silencedetect=n=-35dB:d=0.4 -f null -`.

**Captions through the cuts**: `remapWords(words, edit, fps)` keeps a word when its middle survived and clamps it
to its piece; `remapTime(sec, edit, fps)` maps one time; `sourceTime(frame, edit, fps)` goes back. Remap after every
cut, trim or speed change.

## 3. Speed

| Need | Do |
|---|---|
| One constant speed | `playbackRate` on the clip (`<Clip playbackRate={1.5}>`). Media engine: pitch rises; `engine="offthread"` keeps the pitch in renders |
| Sections at different constant speeds | edit pieces with a rate: `[[0, 2], [2, 6, 3], [6, 8]]` (the kit), or Series items of `duration / speed` frames with `trimBefore` = source frames used so far |
| A speed that changes smoothly | `<SpeedRamp keys>`: OffthreadVideo re-placed every frame at the integrated position |
| Retime any animation (graphics, not footage) | `<TimeRamp keys>`: children in a `<Freeze>` at the integrated frame; fractional frames keep slow motion smooth |
| A whole animated subtree faster or slower | `<Sequence playbackRate={0.5}>` (4.0.528, constant) |

Integrating speed: `position(t) = start + sum of speed(i + 0.5) for i < t`. Never interpolate `playbackRate` itself:
frames render independently, so the clip would jump to `rate * t`. `rampLength(keys, sourceFrames)` tells how many
output frames a ramp needs, so the ramp never runs past the end of the file. `<TimeRamp>` is limited by `<Freeze>`:
the frame it asks for is clamped to the composition's length (verified), so it cannot run ahead of real time past
the end; use it for slow motion, holds and ramps that stay behind.

Slow motion from 30 fps footage repeats frames (0.25x shows each frame four times): shoot 60 or 120 fps, or accept
the stutter as a style. A ramped clip's own audio is useless (it is chopped every frame): mute it and lay music or a
riser.

## 4. Freeze frames and reverse

- Freeze: `<Clip src trimBefore={n} freeze={0} />` holds source frame n (the `freeze` prop of `@remotion/media`
  `<Video>`, verified). The classic beat: play to the moment, cut to the held frame for 45 to 75 frames with a 4 to 6
  % push-in, a white flash of 6 to 8 frames, a shutter or click, a label; resume from n + 1.
- Reverse playback is not supported by any tag. Pre-render: `ffmpeg -i in.mp4 -vf reverse -af areverse rev.mp4`
  (short clips; reverse loads the whole clip in memory).

## 5. Transitions between clips

- Hard cuts are the default. For a dissolve or a slide use `<TransitionSeries>` from `@remotion/transitions`; it
  overlaps the two clips, so the total shrinks by the transition length.
- Handles: a transition eats footage from both sides. Start the incoming clip earlier in the source (the Recorder
  starts it 15 frames early and lengthens the scene by those frames) so the overlap covers handles, not the first
  words.
- J and L cuts: let the next clip's sound start 6 to 12 frames before its picture (J) or the previous sound run
  under the new picture (L). With the kit: place a `<Voice>` or a muted `<Clip>` plus its audio separately with
  different `from` values.
- Put a whoosh's peak on the cut, a few frames early rather than late.

## 6. B-roll rules (from the Recorder)

- A B-roll clip is muted, starts after the speaker has begun the thought and ends before the scene ends (15 frames
  earlier when the scene transitions out); a later overlapping B-roll stretches the earlier one so the base never
  flashes between them.
- Landscape: fade B-roll in and out with a damped spring (about 10 frames). Square or portrait: shrink the speaker 10
  % while a B-roll card slides in from the side away from the face.
- Vertical footage in a landscape frame: fit it over a blurred, oversized (110 %) copy of itself (`objectFit="blur"`).

## 7. Layouts

- `<SplitScreen>`: rects from `splitRects(n, {width, height, direction, sizes, gap})`; panes slide in from their own
  sides. Keep faces inside narrow panes with `videoStyle.objectPosition`.
- `<PictureInPicture>`: `pipRect()` puts the inset on the safe-area corner; `zoom` + `focus` frame a face in a bubble.
- `<LayoutSwitch>`: the Recorder's idea of computing a box per layout and interpolating boxes between layouts; the
  smaller layer draws on top, so insets never hide behind the full frame. Transitions of 15 to 24 frames, in-out.
- `<Letterbox>`: bars to 2.39 (scope), 2 (univisium), 1.85 (flat); on 9:16 bars leave a wide strip. Put titles in
  the lower bar only where it overlaps the safe area.

## 8. Ken Burns

Rectangles as fractions of the covered picture, zoom interpolated exponentially (equal ratios per frame look like
constant speed), centre linearly. 8 to 25 % over a shot of 4 to 8 s; one direction per shot; alternate directions
between consecutive stills; `curves.sine` for a shot that starts and ends on a cut-away, `linear` when shots cut into
each other mid-move. Faces: end the move on the eyes, not the chin.

## 9. Text behind a person (matting)

`@remotion/video-matting` (4.0.523, needs a GPU; not installed in the kit) splits a clip into an opaque base and a
transparent foreground WebM. Stack: base `<Video>`, the title, foreground `<Video muted>`, all with identical timing.
Without the package, a rough version: a luma or colour key with `@remotion/effects` on a clean background.

## 10. Preparing footage

- Constant frame rate MP4 with faststart: `ffmpeg -i in.webm -r 30 -c:v libx264 -crf 18 -g 30 -c:a aac -b:a 192k
  -movflags +faststart out.mp4` (browser and phone recordings are often variable frame rate).
- Transcode H.265 (iPhone), AV1, AVI and ProRes-without-decoder to H.264/AAC before editing.
- Proxies at output size for 4K sources in a 1080p edit; keyframes every 1 to 2 s for heavy cutting (each frame needs
  its keyframe decoded).
- Level voices before editing (references/sound.md), never inside the edit with big gains.
- Keep the raw transcript; edit copies.
