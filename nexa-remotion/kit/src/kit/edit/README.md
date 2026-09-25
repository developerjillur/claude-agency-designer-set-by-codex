# edit: footage and sound

Clips, trims and speed, jump cuts, speed ramps, freeze frames, Ken Burns stills, split screens, picture in picture,
layouts that morph between full, split and inset, letterbox bars, a voice, a music bed that ducks under it, sound
effects, audio visualisers, audiograms and cutting on the beat. Import from `./kit/edit` in a project. Built on
`@remotion/media` (`<Video>`, `<Audio>`), `OffthreadVideo`, `@remotion/media-utils` and `@remotion/sfx`, all 4.0.528.

Timing model in one line: a clip at parent frame `t` shows source frame `trimBefore + (t - from) * playbackRate`;
`trimBefore` and `trimAfter` are source positions in frames at the composition's fps (`trimAfter` is a position,
not a length); a clip with `trimAfter` ends by itself after `(trimAfter - trimBefore) / playbackRate` frames.

Demos: `src/demos/edit.tsx` (`nrk.py demos --module edit`). Demo media: see the end of this file.

---

## Clip

One piece of footage placed, trimmed, framed and mixed. The media engine (`@remotion/media` `<Video>`) by default;
the offthread engine (`<OffthreadVideo>`) on request.

| Prop | Default | Notes |
|---|---|---|
| `src` | required | `staticFile('clips/a.mp4')` or a CORS-enabled URL |
| `from` | 0 | frame on the parent timeline where it starts |
| `durationInFrames` | rest of the parent | cuts it off |
| `trimBefore` / `trimAfter` | none | source frames at the composition fps; `trimAfter` is a position |
| `playbackRate` | 1 | constant. Media engine: the pitch moves with it; offthread engine keeps the pitch |
| `objectFit` | `'cover'` | `'contain'`, `'fill'`, `'none'`, `'scale-down'`, or `'blur'` (fitted over a blurred cover copy) |
| `volume` | 1 | a gain, or `(f) => gain` with `f` = frames since the clip started |
| `fadeIn` / `fadeOut` | 0 | sound fades in frames (use 6 or more: gain is applied once per frame) |
| `fadePicture` | false | also dip the picture with the same frames |
| `muted`, `loop` | false | `loop` repeats `[trimBefore, trimAfter)`; the volume curve keeps counting across loops |
| `freeze` | none | hold the frame at this clip frame (after `trimBefore`); a frozen clip is silent |
| `engine` | `'media'` | `'offthread'`: pitch-preserving speed, or a source you want decoded by FFmpeg |
| `transparent` | false | offthread engine: keep alpha (PNG extraction, slower) |
| `premountFor` | fps (1 s) | preview buffering only |
| `blur`, `dim` | 40, 0.35 | the `'blur'` fill: radius (px at 1080) and darkening (0.5 when text sits on it) |
| `style` / `videoStyle` | | the box (position it here) / the picture (`objectPosition`, a filter) |

```tsx
<Clip src={staticFile('interview.mp4')} trimBefore={12 * fps} trimAfter={Math.round(17.5 * fps)} fadeIn={8} fadeOut={12} />
<Clip src={staticFile('phone.mp4')} objectFit="blur" muted />                 // vertical footage in a 16:9 frame
<Clip src={staticFile('city.mp4')} objectFit="cover" muted loop />            // full-bleed B-roll
<Clip src={staticFile('talk.mp4')} playbackRate={1.25} engine="offthread" />   // faster, voice pitch kept
<Clip src={staticFile('shot.mp4')} trimBefore={30} freeze={44} />            // holds source frame 74
```

Gotchas
- `objectFit` must be the prop: `@remotion/media` ignores `style.objectFit` and logs a warning. `objectPosition`
  in `videoStyle` works (frame a face: `'60% 40%'`).
- Without `trimAfter` a clip does not end by itself: it freezes on its last frame until the parent ends.
- Audio of a trimmed clip starts at its `from`. To start the sound later, move `from`, never `trimBefore`.
- Mute B-roll and every duplicate layer (the blur copy is muted for you): every unmuted video adds to the mix.
- When to use the offthread engine: pitch-preserving speed changes; H.265 (iPhone), AV1 or odd codecs you cannot
  transcode (the media engine already falls back to OffthreadVideo by itself in server renders, with a log line
  "falling back to <OffthreadVideo>", but never in client-side rendering); alpha sources when the render browser
  has no WebGL2 (`transparent`). Better still: transcode to H.264/AAC MP4 or VP9 WebM with alpha.
- A 4K source costs 4K decoding even in a 1080p frame: make proxies.
- `clipLength({trimBefore, trimAfter, playbackRate})` returns the frames a clip lasts (Infinity without `trimAfter`).

## KenBurns

A slow push and pan over a still (or any full-frame content) from one framing rectangle to another. The picture is
laid out to cover the frame, so rectangles are fractions of what fills the frame (no image size needed). Zoom moves
exponentially, the centre in a straight line.

| Prop | Default | Notes |
|---|---|---|
| `src` or `children` | | an image, or a scene/clip to move |
| `move` | `'in'` | preset: `'in'`, `'out'`, `'left'`, `'right'`, `'up'`, `'down'` |
| `amount` | 0.15 | how much closer the tight end is (0.08 to 0.25) |
| `focus` | `[0.5, 0.5]` | where a preset pushes to or pans across |
| `from` / `to` | preset | `{x, y, w}`: top-left and width as fractions; height follows the frame |
| `delay`, `duration` | 0, rest of the Sequence | |
| `ease` | `curves.sine` | `curves.linear` when shots cut into each other mid-move |
| `imgStyle`, `style` | | |

```tsx
<KenBurns src={staticFile('lake.jpg')} move="in" amount={0.2} focus={[0.64, 0.45]} />
<KenBurns src={staticFile('map.png')} from={{x: 0, y: 0, w: 1}} to={{x: 0.55, y: 0.2, w: 0.4}} />
<KenBurns move="right" amount={0.1}><Clip src={staticFile('city.mp4')} muted /></KenBurns>
```

Gotchas: give stills at least `1 + amount` times the frame size (2880x1620 for a 25 % push at 1080p) or the tight
end goes soft. Rectangles are clamped inside the picture, so a far focus point slows the move near the edge.
`kenBurnsPreset(move, amount, focus)` and `kenBurnsAt(a, b, t)` give the same framings for overlays (a minimap).

## JumpCuts and the edit maths

`<JumpCuts>` plays only the kept ranges of one source, back to back, one premounted clip per piece in a `<Series>`.

| Prop | Default | Notes |
|---|---|---|
| `src`, `ranges` | required | `ranges`: `[start, end]` or `[start, end, speed]` in source seconds |
| `objectFit`, `volume`, `muted` | `'cover'`, 1, false | |
| `punchIn` | 0 | every second piece this much closer (0.06 to 0.12): the cut reads as a second camera |
| `punchOrigin` | `'50% 40%'` | the face |
| `declick` | 0 | sound fade frames at each join (2 to 3 for cuts inside continuous sound) |
| `premountFor` | fps | |
| `overlay` | none | `(piece) => node` drawn over each piece |

```tsx
const ranges = keepRanges(words, {gap: 0.45, padBefore: 0.12, padAfter: 0.2, duration: 12});
// composition durationInFrames = editLength(ranges, fps)
<JumpCuts src={staticFile('talk.mp4')} ranges={ranges} punchIn={0.08} punchOrigin="60% 38%" />
const captions = remapWords(words, buildEdit(ranges, fps), fps); // captions follow the cuts
```

Helpers (`edl.ts`), all frame-exact because source positions are rounded once in `buildEdit`:
- `buildEdit(ranges, fps)` -> `EditPiece[]` `{index, from, length, trimBefore, rate, start, end}`; `editLength()`.
- `remapTime(sec, edit, fps)` source to output seconds (null when cut); `sourceTime(frame, edit, fps)` the inverse.
- `pieceAt(frame, edit)`, `pieceAtSource(sourceFrame, edit)`.
- `remapWords(words, edit, fps)`: any `{startMs, endMs, timestampMs?}` (a `Caption[]`) moved into output time; a
  word is kept when its middle survived; start and end are clamped to its piece.
- `keepRanges(words, {gap, padBefore, padAfter, duration})`: ranges from word timings. From silence detection
  instead, map `getSilentParts()` `audibleParts` to `[start, end]`.

Gotchas: set the composition length from `editLength` (an integer). Cut in pauses (a word end plus about 0.3 s),
never mid-word. Speed pieces (`[s, e, 2]`) change pitch on the media engine.

## SpeedRamp and TimeRamp

A speed that changes over time. The media `<Video>` cannot change speed while it plays, so `<SpeedRamp>` uses
`<OffthreadVideo>` placed at every frame at the source position found by summing the speed so far.
`<TimeRamp>` retimes any animated children through `<Freeze>` (fractional frames, so slow motion stays smooth).

| Prop | Default | Notes |
|---|---|---|
| `keys` | required | `[{at, speed}]` on the output timeline; 1 normal, 0 hold |
| `ease` | `curves.inOut` | between keys |
| `trimBefore` (SpeedRamp) / `start` (TimeRamp) | 0 | source frame at output frame 0 |
| `objectFit` | `'cover'` | SpeedRamp |
| `muted` | true | SpeedRamp: the ramped clip's own sound is chopped every frame; lay music instead |
| `transparent`, `style` | | SpeedRamp |

```tsx
const keys = [{at: 0, speed: 1}, {at: 30, speed: 1}, {at: 55, speed: 2.8}, {at: 80, speed: 2.8}, {at: 105, speed: 0.25}, {at: 140, speed: 0.25}, {at: 179, speed: 1}];
<SpeedRamp src={staticFile('surf.mp4')} keys={keys} />
<TimeRamp keys={[{at: 0, speed: 1}, {at: 50, speed: 0.2}, {at: 120, speed: 1}]}><Explosion /></TimeRamp>
```

Helpers: `speedAt(frame, keys)`, `rampPositions(keys, frames, start)` (the table), `rampLength(keys, sourceFrames)`
(output frames a ramp needs; check it against the file length). Gotchas: a ramp can run past the end of the file,
so check `rampLength`. `TimeRamp` is clamped to the composition's length: speed-ups need frames that exist, so use
it for slow motion and holds (it cannot fast-forward past the end). A 30 fps source at 0.25x repeats frames: shoot
60 or 120 fps for real slow motion.

## Layouts: SplitScreen, PictureInPicture, LayoutSwitch, Letterbox

`<SplitScreen>`: one pane per child, side by side in landscape, stacked in portrait.

| Prop | Default | Notes |
|---|---|---|
| `direction` | `'auto'` | `'row'`, `'column'` |
| `sizes` | equal | `[2, 1]` gives the first pane two thirds |
| `gap` | 0 | px at 1080; the ground shows through |
| `divider`, `dividerColor` | 0, accent | a line on each seam |
| `labels`, `labelPosition` | none, `'bottom'` | chips inside the safe area |
| `enter` | `'slide'` | `'wipe'`, `'none'`; panes arrive from their own sides |
| `delay`, `duration`, `stagger`, `ease` | 0, 24 f, 5 f, `curves.out` | |
| `background`, `style` | theme `bg` | |

`<PictureInPicture>`: an inset in a corner of the safe area.

| Prop | Default | Notes |
|---|---|---|
| `corner` | `'bottomRight'` | |
| `shape` | `'round'` | `'rect'`, `'circle'` |
| `width`, `aspect` | 520 (300 circle), 16/9 | px at 1080 |
| `margin` | 0 | from the safe-area edges |
| `border`, `borderColor` | 6, light | ring (near-white on dark themes) |
| `shadow` | 1 | 0 to 1 |
| `label` | none | a name chip on the lower edge |
| `zoom`, `focus` | 1, `[0.5, 0.5]` | push in on the content with `focus` centred (a face in a webcam bubble) |
| `enter` / `exit` | `'pop'` / `'none'` | `'slide'`, `'fade'`; the exit ends on the last frame of the Sequence |

`<LayoutSwitch>`: two sources whose layout morphs over time: `'a'`, `'b'` (full), `'a+b'` (A full, B inset),
`'b+a'` (B full, A inset), `'split'`. Props: `a`, `b`, `keys: [{at, shot}]`, `transition` (20 f), `ease`, `pip`
(PipOptions), `gap` (16), `border`, `borderColor`, `background`. The smaller layer is always drawn on top.

`<Letterbox>`: bars to a picture aspect (2.39 scope, 1.85 flat, 4/3 pillar bars on 16:9). Props: `aspect` (2.39),
`color` (#000), `delay`, `duration` (24 f, 0 = already in), `out` (bars leave on the last frame), `ease`, children.

```tsx
<SplitScreen gap={14} labels={['Before', 'After']}><Clip src={a} muted /><Clip src={b} muted /></SplitScreen>
<PictureInPicture shape="circle" width={320} label="Nadia Karim, host" zoom={1.8} focus={[0.66, 0.4]} exit="pop">
	<Clip src={staticFile('webcam.mp4')} />
</PictureInPicture>
<LayoutSwitch a={<Clip src={host} />} b={<Clip src={screen} muted />} keys={[{at: 0, shot: 'a'}, {at: 90, shot: 'b+a'}, {at: 200, shot: 'split'}]} />
<Letterbox aspect={2.39} delay={8}><Clip src={city} muted /></Letterbox>
```

Gotchas: children are usually `<Clip>`s (they fill any box with `objectFit: 'cover'`); use `videoStyle.objectPosition`
to keep a face in a narrow pane. Chips and insets stay inside the safe area; in 9:16 that is the upper middle of
the frame (y 270 to 1248 at 1080x1920). `splitRects`, `pipRect` and `letterboxBars` return the geometry.
`LayoutLabel` is the chip itself.

## Sound: Voice, Music, Sfx

`<Voice src from trimBefore trimAfter volume=1 fadeIn fadeOut playbackRate>`: a narration or dialogue track.

`<Music>`: a bed that fades in, sits at `level`, ducks under voice windows, and fades out on its last frame.

| Prop | Default | Notes |
|---|---|---|
| `src` | required | |
| `from`, `durationInFrames`, `trimBefore` | 0, rest of the parent | the fade-out ends at the end |
| `duck` | [] | voice windows `[start, end]` in frames on the parent timeline (`speechWindows()` makes them) |
| `level` | 0.5 | gain with no voice (-6 dB) |
| `duckTo` | 0.06 | gain under the voice (-24 dB); 0.04 to 0.1 for a mastered track under a normalised voice |
| `attack` / `release` / `hold` | 30 / 30 / 8 | the ramp down ends as the voice starts; the ramp up waits `hold` frames |
| `bridge` | attack + hold + release | pauses shorter than this stay down (no pumping between sentences) |
| `fadeIn` / `fadeOut` | 30 / 60 | |
| `loop` | true | the curve keeps counting across repeats (`loopVolumeCurveBehavior="extend"`) |

`<Sfx src at hit volume=0.25 playbackRate>`: a sound whose hit lands on frame `at`. `src` is a file or one of the
seven CC0 names in `SFX` (`whoosh`, `whip`, `uiSwitch`, `mouseClick`, `pageTurn`, `shutterModern`, `shutterOld`);
`hit` is the frames from the file's start to its peak (`SFX_HIT` holds estimates for the built-ins; check by ear).
A hit before frame 0 starts the file part-way.

```tsx
const windows = speechWindows(words, fps, {offset: voiceFrom});
<Voice src={staticFile('vo.m4a')} from={voiceFrom} />
<Music src={staticFile('bed.m4a')} duck={windows} />
<Sfx src="whoosh" at={cutFrame} volume={0.3} />
<Sfx src={staticFile('sfx/shutter.wav')} at={freezeFrame} volume={0.4} />
```

Gain helpers (`gain.ts`): `dbToGain`, `gainToDb`, `safeGain` (finite, 0 to 4), `fadeGain(f, length, in, out)`,
`volumeCurve(frames, gains, ease)` (clamped both sides, NaN-safe: pass it as `volume`), `duckDepth`, `duckGain`,
`bridgeWindows`, `musicGain(f, opts)` (the exact curve `<Music>` plays, for drawing it), `speechWindows(words, fps,
{gap: 0.5, pad: 0.05, offset})`.

Gotchas
- Every `interpolate()` used as a volume must clamp both sides: an unclamped fade-in keeps climbing and throws at
  100 ("Did you forget to divide by 100?"). The helpers here all clamp.
- Volume is linear gain applied once per video frame: fades under 6 frames step audibly.
- The `@remotion/sfx` URLs are remote (remotion.media, CORS works): the render machine needs the network. For
  offline, Lambda and reproducible renders copy the files into `public/sfx/` and use `staticFile()`. The other 25
  exports of `@remotion/sfx` are internet meme sounds with no stated licence: never in client work.
- Renders mix at 48 kHz; mixed sources are resampled.

## Visualisers and Audiogram

All read the real sound through `useWindowedAudioData` (three windows of `windowSeconds`, default 10, around the
playhead), so long files work.

Shared props (`AudioSourceOptions`): `src`, `from` (frame on this timeline where the audio starts playing),
`trimBefore`, `windowSeconds`. The file is read at `frame - from + trimBefore`. **Inside a Sequence that starts at
S while the audio plays from the composition start, pass `from={-S}`.**

| Component | Use it for | Key props (defaults) |
|---|---|---|
| `AudioBars` | spectrum bars | `bars` 32, `minHz` 40, `maxHz` 12000, `floorDb` -62, `ceilDb` -12, `tilt` 3 dB/oct, `decay` 0.7, `lookback` 4, `width` 1200, `height` 320, `gap` 0.38, `color`, `color2`, `align` bottom/center, `mirror`, `minHeight` 6 |
| `AudioWave` | `'line'`: live waveform; `'scroll'`: level bars sliding past a centre playhead | `variant`, `width` 1200, `height` 240, `seconds` (0.06 line, 6 scroll), `points` (96 / 64), `gain` 1.6, `strokeWidth` 6, `color`, `color2`, `glow`, `floorDb`, `ceilDb` |
| `AudioCircle` | a ring of bars around a cover or logo | `size` 380, `length` 110, `barWidth` 7, `bars` 36, `mirror` true, `spin` 6 deg/s, `pulse` 0.04, `color`, children |
| `Audiogram` | a podcast clip as a video | `src`, `from`, `trimBefore`, `length`, `title`, `show`, `episode`, `cover` (src or node), `captions` (slot), `playAudio` true, `volume`, `accent` |

Hooks: `useAudioAt(opts)` -> `{data, offset, position, fps}`; `useAudioSpectrum(opts)` -> `number[]` 0 to 1 (bass
first); `useAudioLevel({...opts, band: [30, 150]})` -> one 0 to 1 level for pulses and flashes.

```tsx
<AudioBars src={music} bars={36} mirror align="center" width={1500} height={380} />
<AudioWave src={voice} variant="scroll" width={875} height={80} />
<Audiogram src={staticFile('ep12.m4a')} title="Why every edit starts with the voice" show="The Cut" episode="EP 12"
	cover={staticFile('cover.jpg')} captions={<MyCaptions />} />
```

Gotchas: the spectrum is normalised to the loudest sample in the loaded windows, so levels can shift slightly
when a much louder window loads. `Audiogram` lays out portrait (9:16), square and landscape inside the safe area;
in 9:16 everything sits between y 270 and 1248. The captions slot takes any node (the type module's caption
components, or plain text, styled at 46 px). Visualisers show silence before the audio starts and after it ends.

## Beat: BeatPulse, OnBeats and helpers

`useBeatGrid(bpm, offset)` -> beat frames over the Sequence (core's `beatGrid`); `beatFrame(k, bpm, fps, offset)`.
`beatAt(frame, grid)` -> `{index, beatFrame, since, phase, bar, beatInBar}`. `beatPulse(frame, grid, {decay 8,
every 1, phase 0})` -> 1 on the beat, falling to 0. `snapCuts(cuts, grid, window 6)`, `beatCuts(grid, every 4)`.

`<BeatPulse bpm offset every phase amount=0.06 decay=9 glow origin>`: a small hit on an element.
`<OnBeats bpm offset beats=4 premountFor>`: children back to back, each lasting a whole number of beats (the first
also covers the lead-in before the first downbeat); `onBeatLengths()` gives the lengths.

```tsx
<Music src={track} />
<OnBeats bpm={120} beats={4}>{shots}</OnBeats>
<BeatPulse bpm={120} every={4}><Logo /></BeatPulse>
```

Gotchas: measure the tempo and the first downbeat (offset) from the file; do not guess. Pulse elements, not the
whole frame: at most a few whole-frame hits per film, on the strongest beats. Narration wins over music: cut on the
beat nearest the sentence gap.

---

## Demo media (`public/edit/`, 2.2 MB, all generated for the kit)

| File | What | How it was made |
|---|---|---|
| `cam-a.mp4` | 8 s, 1280x720, 30 fps: dusk skyline with bokeh; slate `CAM A mm:ss.ff` and `f###`, white dot on each whole second; 440 Hz tone at -20 dBFS with a 1 kHz pip each second (mono AAC) | a Remotion composition (SVG, noise, seeded random) rendered muted, muxed with a Node-synthesised WAV; x264 CRF 27, keyframe every second |
| `cam-b.mp4` | 8 s: ocean swell at sunrise, slate top right; surf noise (stereo AAC) | same |
| `talk.mp4` | 12 s: a presenter whose mouth and level meter follow the voice; same voice as `voice.m4a` | same (mouth from the voice's RMS) |
| `still.jpg` | 2880x1620 layered mountains at dawn | a Remotion still (noise ridges) |
| `music.m4a` | 20 s seamless loop, 120 BPM, Am F C G, first downbeat at 0 s (kick, snare, hats, bass, pad, arp), -11 LUFS | synthesised in Node, AAC 128k |
| `voice.m4a` | 12 s voice-like speech with pauses (formant synthesis, energy above 180 Hz), -16 LUFS | synthesised in Node, AAC 64k mono |
| `whoosh.wav`, `click.wav` | 0.7 s filtered-noise whoosh (peak at 0.35 s), 0.12 s click | synthesised in Node |

Voice phrases (seconds in `voice.m4a` and `talk.mp4`): 0.62 to 2.51, 4.25 to 6.17, 8.15 to 10.10. Word timings
are in `src/demos/edit.tsx` (`WORDS`, @remotion/captions shape).
