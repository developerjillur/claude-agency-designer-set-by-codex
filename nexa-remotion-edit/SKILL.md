---
name: nexa-remotion-edit
description: "Editing footage and sound in Remotion: clips with trims, speed and framing, jump cuts that remove pauses (captions remapped through the cuts), speed ramps, freeze frames, Ken Burns stills, split screens, picture in picture, layouts that morph between full, split and inset, letterbox bars, voice tracks, music beds that duck under the voice, sound effects on cuts, spectrum and waveform visualisers, audiograms and cutting on the beat, with the kit's Clip, JumpCuts, SpeedRamp, Music, AudioBars and Audiogram components and measured mix levels. Use it for any Remotion job with video files or audio, Banglish asks included ('video edit koro', 'jump cut dao', 'music ta voice er niche nama', 'audiogram banao'). Part of the nexa-remotion family."
---

# Editing footage and sound in Remotion

How footage and sound become an edit: which clip plays when, from where, how fast and how framed, and how voice,
music and effects sit together. Part of the nexa-remotion family (the director skill is `nexa-remotion`; the kit
lives in `~/.claude/skills/nexa-remotion/kit`, and a project made with `nrk.py new` imports these parts from
`./kit/edit`). Remotion is pinned at 4.0.528.

## Fast path

1. **Voice first.** Get the narration or dialogue as a file, level it (`loudnorm`, references/sound.md), and get word
   timings (Gemini 3.5 Transcribe for every language but English, whisper.cpp with `tokenLevelTimestamps` for
   English, ElevenLabs, or forced alignment) as `{text, startMs, endMs}[]`.
   Every other timing hangs off these words.
2. **Prepare footage once.** H.264/AAC MP4, constant frame rate, faststart, keyframe every second, at output size
   (`ffmpeg -i in.mov -r 30 -c:v libx264 -crf 18 -g 30 -c:a aac -movflags +faststart out.mp4`). Put files in
   `public/` and load them with `staticFile()`.
3. **Cut.** A talking head: `keepRanges(words)` then `<JumpCuts ranges punchIn={0.08}>`; set the composition length
   to `editLength(ranges, fps)`; remap captions with `remapWords(words, buildEdit(ranges, fps), fps)`. Everything
   else: `<Clip trimBefore trimAfter>` inside `<Series>` or `<Sequence>`.
4. **Frame.** `objectFit="cover"` for full bleed, `"blur"` for vertical footage in a wide frame (and the reverse),
   `<SplitScreen>`, `<PictureInPicture>` or `<LayoutSwitch>` for two sources, `<KenBurns>` for stills.
5. **Mix.** `<Voice>` at 1; `<Music duck={speechWindows(words, fps, {offset})}>` (bed 0.5, 0.06 under the voice,
   30-frame ramps, short pauses bridged); `<Sfx at={cutFrame}>` at 0.2 to 0.4 on a few chosen events; mute B-roll.
6. **Check.** `nrk.py stills` at cuts and 12 frames later; render a draft; then measure the delivered file:
   `ffprobe` (audio stream, 48 kHz), `ebur128` (about -14 LUFS for social, peaks under -1 dBTP), and the bed under
   the voice (references/render-and-check.md has the band-split method).

## Components (from `./kit/edit`)

| Component or helper | Use it for | Key props |
|---|---|---|
| `Clip` | any footage: trim, speed, fit, fades, loop, freeze | `trimBefore`, `trimAfter`, `playbackRate`, `objectFit` (cover, contain, blur), `volume`, `fadeIn`, `fadeOut`, `loop`, `freeze`, `engine` |
| `JumpCuts` + `keepRanges`, `buildEdit`, `editLength`, `remapWords`, `remapTime`, `sourceTime` | cutting pauses out of one take, captions that follow | `ranges` (seconds), `punchIn`, `punchOrigin`, `declick` |
| `SpeedRamp`, `TimeRamp`, `speedAt`, `rampLength` | speed changing over time (footage / any animation) | `keys: [{at, speed}]`, `ease`, `trimBefore` |
| `KenBurns` | stills (or a clip) pushed and panned | `move`, `amount`, `focus`, `from`, `to` |
| `SplitScreen` | two to four sources side by side or stacked | `gap`, `divider`, `labels`, `enter` |
| `PictureInPicture` | a webcam or screen inset | `shape` (rect, round, circle), `corner`, `width`, `zoom`, `focus`, `label`, `enter`, `exit` |
| `LayoutSwitch` | host and B-roll morphing between full, inset and split | `a`, `b`, `keys: [{at, shot}]`, `transition` |
| `Letterbox` | scope bars, pillar bars | `aspect` (2.39), `delay`, `out` |
| `Voice`, `Music`, `Sfx`, `SFX` | the mix | `Music`: `duck`, `level`, `duckTo`, `attack`, `release`, `bridge`; `Sfx`: `at`, `hit`, `volume` |
| `musicGain`, `duckGain`, `speechWindows`, `volumeCurve`, `fadeGain`, `dbToGain` | gains as pure functions (draw them, reuse them) | |
| `AudioBars`, `AudioWave`, `AudioCircle`, `useAudioSpectrum`, `useAudioLevel` | visualisers from the real sound | `src`, `from`, `bars`, `mirror`, `variant` |
| `Audiogram` | a podcast clip as a 9:16, square or 16:9 video | `src`, `title`, `show`, `episode`, `cover`, `captions` |
| `OnBeats`, `BeatPulse`, `useBeatGrid`, `beatAt`, `beatPulse`, `snapCuts`, `beatCuts` | cutting and pulsing on the music | `bpm`, `offset`, `beats`, `every` |

Every prop, default and gotcha: `kit/edit/README.md`. Demos: `nrk.py demos --module edit`.

## Craft rules

**Timing**
- A clip at parent frame t shows source frame `trimBefore + (t - from) * playbackRate`. Trims are source frames at the
  composition fps; `trimAfter` is a position, not a length. A trimmed clip ends by itself; an untrimmed one freezes
  on its last frame.
- Cut in pauses: a word's end plus about 0.3 s, never mid-word. Keep ranges pad 0.12 s before and 0.2 s after
  speech, and merge words closer than 0.45 s.
- Jump cuts read as intended with a punch-in of 6 to 12 % on every second piece, centred on the face.
- Lead readable elements 1 to 2 frames before the word they illustrate; land hits exactly on it.
- Speed: ramps ease in-out over 20 to 30 frames; real slow motion needs 60 or 120 fps footage (30 fps at 0.25x
  repeats frames). Keep speed changes under about 3x for footage people watch, not skim.
- Freeze frames hold 1.5 to 2.5 s with a slow push (4 to 6 %), a flash of 6 to 8 frames and a shutter or click.

**Framing**
- Full bleed is `objectFit="cover"`; vertical footage in 16:9 (or 16:9 in 9:16) is `"blur"` with `dim` 0.35, 0.5
  when text sits on the fill.
- Split screens: 10 to 16 px gutters, or a hard split with a 6 to 8 px accent line; two panes read, four is the most.
- Insets: 28 % of the frame width for a rect, 300 to 340 px circles at 1080, a 6 px ring and a soft shadow, pushed
  in on the face (`zoom` 1.5 to 1.9). They sit on the safe-area corner, away from captions.
- Ken Burns: 8 to 25 % over the shot, one direction, a gentle sine ease; stills at 1.5x the frame size.

**Mix (gain = 10^(dB / 20))**
- Voice at 1 (-14 to -16 LUFS after levelling). Music bed at 0.5 (-6 dB) alone and 0.04 to 0.1 (-28 to -20 dB)
  under the voice: the kit's 0.06 puts a mastered track about 18 dB under the voice. SFX 0.2 to 0.4, 10 to 20 dB
  under the voice.
- Duck ramps of about 30 frames that finish before the voice starts and wait 8 frames after it; pauses shorter than
  about 2.3 s stay down (a bed that swells for a second between sentences pumps).
- Fades of 6 frames or more (volume steps once per frame). Every volume `interpolate()` clamps both sides.
- One SFX per event, nothing repeated more than twice in 45 s, foley (shutter, click, whoosh) over synthetic bleeps
  in product films. Only the 7 CC0 sounds of `@remotion/sfx`, or a licensed library; copy them into `public/sfx/`.
- Deliver around -14 LUFS integrated, true peak under -1 dBTP for social; -23 for broadcast.

**Beat**
- Only when the track is rhythmic. Measure BPM and the first downbeat; cut every 2 or 4 beats; snap internal
  events within 6 frames; pulse elements, not the frame; at most 3 whole-frame hits per film; narration wins.

## Recipes

**Talking head, pauses cut, captions in sync**
```tsx
const ranges = keepRanges(words, {duration: 12});                // compose length: editLength(ranges, fps)
const edit = buildEdit(ranges, fps);
<JumpCuts src={staticFile('talk.mp4')} ranges={ranges} punchIn={0.08} punchOrigin="60% 38%" />
<MyCaptions words={remapWords(words, edit, fps)} />
```

**Voice-over explainer mix**
```tsx
<Voice src={staticFile('vo.m4a')} from={15} />
<Music src={staticFile('bed.m4a')} duck={speechWindows(words, fps, {offset: 15})} />
<Sfx src="whoosh" at={sceneCut} volume={0.3} />
```

**Podcast clip for Reels** (the slot takes any inline caption line; plain text is styled at 46 px)
```tsx
<Audiogram src={staticFile('ep12.m4a')} title="Why every edit starts with the voice" show="The Cut" episode="EP 12"
	cover={staticFile('cover.jpg')} captions={<PhraseLine words={words} ms={(frame / fps) * 1000} />} />
```

**Screen recording with a host**
```tsx
<LayoutSwitch a={<Clip src={host} />} b={<Clip src={screen} muted />}
	keys={[{at: 0, shot: 'a'}, {at: 90, shot: 'b+a'}, {at: 300, shot: 'split'}, {at: 420, shot: 'a'}]} />
```

**Speed ramp into a freeze**
```tsx
const keys = [{at: 0, speed: 1}, {at: 40, speed: 3}, {at: 90, speed: 0.3}];
const hold = Math.round(rampPositions(keys, 120)[119]); // the source frame the ramp ends on
<Series>
	<Series.Sequence durationInFrames={120}><SpeedRamp src={surf} keys={keys} /></Series.Sequence>
	<Series.Sequence durationInFrames={60}><PushIn amount={0.05}><Clip src={surf} trimBefore={hold} freeze={0} /></PushIn></Series.Sequence>
</Series>
<Sfx src="shutterModern" at={120} volume={0.35} />
```

**Montage on the beat**
```tsx
<Music src={staticFile('track.m4a')} level={0.8} />
<OnBeats bpm={120} beats={4}>{shots.map((s) => <Clip key={s} src={s} muted />)}</OnBeats>
```

## Remotion 4.0.528 facts and traps

- Use `<Video>` and `<Audio>` from `@remotion/media` (frame exact, partial downloads, fastest). `objectFit` must be
  the prop (`style.objectFit` is ignored with a warning); `objectPosition` in the style works.
- The media `<Video>` cannot change speed over time and never loops in `<OffthreadVideo>`: ramps use the
  OffthreadVideo trick (`SpeedRamp`), loops on the offthread engine are wrapped in `<Loop>` (Clip does this).
- Verified on this install: `trimBefore/trimAfter` are frame exact and self-limit; the media and offthread engines
  pick the same source frame at 1.5x; `<Video freeze={n}>` holds clip frame n; `<Freeze>` clamps to the
  composition's length (a Freeze remap cannot fast-forward past the end); remote `@remotion/sfx` URLs load in
  renders (peak -3 dB files).
- `volume` callbacks get frames since that media started (not the composition frame); `loop` with
  `loopVolumeCurveBehavior="extend"` keeps counting. Gains of 100 or more throw; NaN throws. `playbackRate` on the
  media path changes pitch; `toneFrequency` (0.01 to 2) shifts pitch without speed; Chrome preview limits rates to
  0.0625 to 16; reverse playback does not exist (pre-render with `ffmpeg -vf reverse -af areverse`).
- Fallback: the media tags fall back to `<OffthreadVideo>` / `<Html5Audio>` in preview and server renders for
  codecs WebCodecs cannot decode (H.265, AV1), CORS failures and alpha without WebGL2; never in client-side
  rendering. Grep the render log for "falling back".
- Visualisers: `useWindowedAudioData` keeps three windows around the playhead, holds a delayRender while loading,
  its `windowInSeconds` cannot change after mount, Matroska/WebM audio decodes from the start; pass
  `dataOffsetInSeconds` on. `frame` means the position in the audio file: subtract where the audio starts.
- Renders mix all audio at 48 kHz; `--muted` drops the track; audio-only export with `--codec=mp3|aac|wav`.
- New in 4.0.528: `<Sequence playbackRate>` (constant, multiplies down the tree, media included). Test before
  relying on it with media.

## References

- `references/media-tags.md`: `<Video>`, `<Audio>`, `<OffthreadVideo>`, Html5 tags: every prop with defaults and
  versions, the decision table, fallback, codecs and containers, alpha, ProRes, caching, errors.
- `references/editing.md`: the timing algebra, edit lists, jump cuts, speed segments and ramps, freeze, reverse,
  transitions with handles, B-roll rules, layouts, Ken Burns, captions through an edit, preparing footage.
- `references/sound.md`: gain and dB, levels, ducking design, fades and crossfades, loops, SFX (CC0 list, hits,
  palette), voice-first timing, loudness and mastering commands, pitch, generated audio.
- `references/visualizers.md`: `@remotion/media-utils` API, the offset rule, spectrum shaping, waveforms,
  audiogram layout, performance.
- `references/beat-sync.md`: beat grids, measuring tempo and downbeat, snapping, montage and pulse rules, checks.
- `references/render-and-check.md`: render flags for sound, measuring the delivered file (ffprobe, ebur128, band
  levels), the pre-render checklist, errors and fixes.
