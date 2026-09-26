# Sound: levels, ducking, effects and loudness

Sound is arithmetic, not taste. Voice decides the timing, music sits under it at measured levels, effects mark a
few chosen events, and the delivered file is measured before it ships.

## 1. How Remotion mixes

- Every mounted, unmuted `<Audio>`, `<Video>` (and legacy tag) is a track; tracks add. Renders resample everything
  to one rate (48 kHz by default; `--sample-rate`, `Config.setSampleRate()`, or `defaultSampleRate` from
  `calculateMetadata`) and hard-clip the sum.
- `volume` is a linear gain: 1 = as recorded, 0.5 = -6 dB, above 1 amplifies. A callback `(f) => gain` gets frames
  since *that media* started playing (0 at its first frame), not the composition frame. It is evaluated once per
  video frame and applied to all of that frame's samples: fades shorter than about 6 frames step audibly.
- `loop` with `loopVolumeCurveBehavior="extend"` keeps `f` counting across repeats (a whole-length fade-out works);
  `'repeat'` restarts the curve every loop.
- Gains of 100 or more throw; NaN or Infinity from a callback throws. `interpolate()` extends past its last key by
  default, so an unclamped fade-in keeps climbing until it throws: clamp both sides, always. The kit's `volumeCurve`,
  `fadeGain`, `duckGain` and `musicGain` clamp and sanitise.
- Memoise volume callbacks (`useCallback`/`useMemo`): the Studio draws them as curves and it is faster.

## 2. Gain and dB

`gain = 10^(dB / 20)`, `dB = 20 * log10(gain)`.

| Gain | dB | Use |
|---|---|---|
| 1 | 0 | voice after levelling |
| 0.7 | -3 | |
| 0.5 | -6 | music bed alone (the kit's `level`) |
| 0.3 | -10.5 | a whoosh on a cut |
| 0.2 | -14 | subtle SFX, Recorder shrink/grow sounds |
| 0.1 | -20 | bed under a quiet voice; Recorder whip |
| 0.06 | -24.4 | bed under the voice (the kit's `duckTo`) |
| 0.04 | -28 | Recorder bed under speech |

## 3. Levels that work

- **Voice** loudest: level recordings to a common loudness before editing (section 7); keep `volume` at 1.
- **Music bed**: 0.5 alone; 0.04 to 0.1 under the voice (mastered music is often 5 to 8 LU louder than a normalised
  voice, so the bed ends up 15 to 25 dB under it). Measured on the kit's demo: -11 LUFS music and a -16 LUFS voice,
  bed 0.5 to 0.06, the music band dropped 18 to 19 dB under speech.
- **SFX**: 0.2 to 0.4, individually placed, 10 to 20 dB under the voice. A cue fully under continuous speech is felt,
  not heard: cut it or move it to a gap.
- A cue's `volume` cannot rescue a quiet file (raising 0.35 to 0.85 moved one mix 0.1 dB against a -17 dB voice):
  level the file itself, trim silence off its head so the transient sits at its start.

## 4. Ducking

The kit's `<Music duck>` and `musicGain()`:
- Windows come from word timings: `speechWindows(words, fps, {gap: 0.5, pad: 0.05, offset})` merges words closer
  than 0.5 s and shifts by where the voice starts on the timeline.
- The ramp down (`attack`, 30 frames) ends when the voice starts, so the first word never fights the music; the ramp
  up (`release`, 30) waits `hold` (8) frames after the last word.
- Pauses shorter than `bridge` (attack + hold + release, about 2.3 s at 30 fps) stay down: a bed that swells for a
  second between two sentences pumps. Longer gaps get a real swell (a musical breath).
- Ramps move in dB (gain interpolated geometrically), so the middle of a ramp sounds half way.
- Do not duck on a beat-synced hit: let the hit through, duck after it.

Manual version in raw Remotion (clamped both sides):
```tsx
const bed = (f: number) => {
	const fades = interpolate(f, [0, 30, len - 60, len - 1], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	const duck = interpolate(f, [s - 30, s, e + 8, e + 38], [1, 0, 0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
	return fades * Math.pow(0.06 / 0.5, 1 - duck) * 0.5; // 0.5 alone, 0.06 under the voice
};
<Audio src={staticFile('bed.mp3')} loop loopVolumeCurveBehavior="extend" volume={bed} />
```
Recorder policy: music at 0.04 under talking scenes, 1.0 in title and end-card scenes, 30-frame ramps, one track
across consecutive scenes, a crossfade when the track changes.

## 5. Fades, crossfades, music length

- Fade music in over about 1 s (30 frames) and out over 1 to 2 s on its last frame (`fadeGain` spreads the steps so
  the first and last frames are never silent).
- Crossfade two tracks with equal power: A = cos(p * pi / 2), B = sin(p * pi / 2) over the overlap; linear
  crossfades dip in the middle.
- Match music to the video: start on a downbeat, end on a phrase. Either fade the tail, or pre-cut the track into
  versions in 2 s steps and pick the one within 1 s of the video length (github-unwrapped). A loop must be seamless
  (a whole number of bars; wrap reverb tails to the start).
- Make two finals when music is used, with and without it, from the same timeline (a boolean prop).

## 6. Voice first (word-locked timing)

1. Script, then record or synthesise the voice (one file per line or per argument).
2. Word timestamps: Gemini 3.5 Transcribe for every language but English (`watch_video.py transcribe FILE --words`
   or `nvc.py transcribe`); whisper.cpp for English only (`tokenLevelTimestamps: true`, `splitOnWord: true`, an
   explicit `language`), with Gemini as soon as it looks unsure; ElevenLabs with `timestamps_granularity: 'word'`,
   or forced alignment. Store `{text, startMs, endMs}` JSON in `public/`.
3. Scene lengths = measured voice + 0.2 to 0.5 s of tail hold (+ transition overlap). Only then build.
4. Write the cue table (word at seconds) above the scene. Cue the meaning word; lead readable elements by 1 to 2
   frames; fire hits exactly on the word; at most two cues per beat.
5. Cuts sit in sentence gaps (a word end + about 0.3 s); confirm with `silencedetect`.
6. Fix brand words in caption text only, never in the timestamps. A new voice or model means new timestamps. Some TTS
   engines ignore speed settings: measure the file length, stretch with `atempo` if needed.

## 7. Loudness and mastering

- Measure each voice file: `ffmpeg -i vo.wav -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -`, then
  apply the second pass with the measured values (`measured_I`, `measured_TP`, `measured_LRA`, `measured_thresh`,
  `offset`, `linear=true`).
- Deliver: about -14 LUFS integrated and true peak at or under -1 dBTP for YouTube, Reels, TikTok; -16 for
  podcasts; -23 for EBU broadcast. Pick one target per platform.
- Master a render: two-pass `loudnorm` to the target, then a peak limiter without makeup gain
  (`alimiter=limit=0.891:level=disabled`), `-c:v copy`, `+faststart`. Verify on the shipped file with
  `ebur128=peak=true` (references/render-and-check.md).
- The Recorder normalises every take to the average loudness of all takes (at least -20 LUFS) with `loudnorm
  I=<target>:LRA=7:TP=-2.0` before editing.

## 8. Sound effects

The seven CC0 sounds in `@remotion/sfx` (safe for client work, no credit needed):

| Export (kit `SFX` name) | File | Length | Since |
|---|---|---|---|
| `whoosh` | whoosh.wav | 0.15 s | 4.0.429 |
| `whip` | whip.wav | 0.17 s (96 kHz, 24-bit) | 4.0.429 |
| `uiSwitch` | switch.wav | 0.33 s | 4.0.429 |
| `mouseClick` | mouse-click.wav | 0.40 s | 4.0.429 |
| `pageTurn` | page-turn.wav | 0.40 s | 4.0.429 |
| `shutterModern` | shutter-modern.wav | 0.49 s | 4.0.429 |
| `shutterOld` | shutter-old.wav | 0.31 s | 4.0.429 |

- They are URLs on remotion.media (CORS works, files peak at -3 dB). For offline, Lambda and reproducible renders
  copy them into the project once (`curl -o public/sfx/whoosh.wav https://remotion.media/whoosh.wav`) and use
  `staticFile('sfx/whoosh.wav')`.
- The other 25 exports (ding, bruh, vineBoom, windowsXpError, recordScratch, animeWow and the rest) are internet
  meme sounds with no stated licence: never in client work, and in the user's own work only when that tone is asked
  for.
- Other sources: kenney.nl (all CC0), freesound.org (check each licence), a licensed library, or synthesis (the kit's
  demo whoosh and click are filtered noise and a sine burst made in Node).
- Land the transient on the event: `<Sfx at={frame} hit={framesToPeak}>`. A whoosh peaks in its middle, a click or a
  shutter at its start. Place cues relative to shot starts or beats, never as bare absolute frames, and re-pin them
  after any timing change; sound is done after picture lock.
- Palette by film type: product promos use whoosh, impact, riser, shutter, switch and real foley; synthetic bleeps read
  as a mobile game. One cue per event, nothing repeated more than twice in 45 s; alternate two samples and step
  volumes down (0.4 then 0.25) when events repeat. A signature phrase: a riser into the build, the impact on the
  landing about 35 frames later, a sparkle 25 frames after that. Sub-bass only on the thesis and the call to action.
- Render output adds a small AAC encoder delay (about 2048 samples at 48 kHz, 1.3 frames at 30 fps, on one measured
  pipeline): if hits must be frame-exact, measure the delivered file and offset once.

## 9. Pitch, tempo, tone

- `playbackRate` on the media tags changes pitch with speed. For speech sped up without chipmunk voice: `engine=
  "offthread"` on `<Clip>` (pitch kept in renders), or pre-process with `ffmpeg -af atempo=1.25`.
- `toneFrequency` (0.01 to 2, constant) shifts pitch without speed: 0.8 lowers 20 %.
- Pre-rendered audio is the most predictable: stretch, pitch or reverse in ffmpeg, then place the file.

## 10. Generated audio

- Synthesise offline (Node, Python, a DAW) and save to `public/`: deterministic, cached, cheap in every tab. The kit's
  demo music (120 BPM, Am F C G, seamless 20 s loop) and voice-like track were made this way.
- In-browser generation (Tone.js `Offline()` rendered to an AudioBuffer, `audioBufferToDataUrl()` from
  `@remotion/media-utils`, fed to an audio tag inside a delayRender) works for short sounds but runs in every render
  tab and holds the whole file in memory.

## 11. Export and stems

- Audio only: `npx remotion render src/index.ts Main out/mix.mp3 --codec=mp3` (or `aac`, `wav`); with the Node API add
  `imageFormat: 'none'`.
- A stem next to the video: `--separate-audio-to=out/mix.wav`. No audio at all: `--muted`. A silent track when there
  is none (for concatenating chunks): `--enforce-audio-track`.
- Web delivery: `--audio-codec=aac --audio-bitrate=320k`; ProRes masters carry PCM.
