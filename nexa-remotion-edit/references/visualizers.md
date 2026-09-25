# Audio visualisers and audiograms

Everything here reads the real samples with `@remotion/media-utils` (4.0.528) and draws them as a pure function of
the frame. The kit's `AudioBars`, `AudioWave`, `AudioCircle`, `Audiogram` and hooks wrap these calls.

## 1. Loading audio for analysis

| Function | Returns | Use it for |
|---|---|---|
| `useAudioData(src, {sampleRate?, requestInit?})` | `MediaUtilsAudioData \| null` (whole file decoded) | short files (under about a minute) |
| `useWindowedAudioData({src, frame, fps, windowInSeconds, channelIndex?, requestInit?})` | `{audioData, dataOffsetInSeconds}` | anything long; 4.0.240, every Mediabunny format since 4.0.383 |
| `getAudioData(src)` | promise of the same | outside components (`calculateMetadata`) |
| `getAudioDurationInSeconds(src)` | seconds | length without CORS |
| `getWaveformPortion({audioData, startTimeInSeconds, durationInSeconds, numberOfSamples, channel?, outputRange?, dataOffsetInSeconds?, normalize?})` | `{index, amplitude}[]` | a static waveform of a section |
| `audioBufferToDataUrl(buffer)` | a WAV data URL | generated audio |
| `createSmoothSvgPath({points})` | an SVG path with curves | lines through samples |

`MediaUtilsAudioData`: `{channelWaveforms: Float32Array[], sampleRate, durationInSeconds, numberOfChannels, resultId,
isRemote}`; samples are -1 to 1.

How `useWindowedAudioData` behaves (read in the bundle):
- It keeps the previous, current and next window around the playhead (`windowInSeconds: 10` holds up to 30 s) and
  returns them as one array; pass `dataOffsetInSeconds` to the visualise functions.
- It holds a `delayRender` while metadata or the current window loads (renders wait; the Studio does not).
- `windowInSeconds` cannot change after mount (it throws). Past the end of the file it returns null.
- Matroska and WebM audio must be decoded from the start of the file to reach a window (a warning is logged): use
  MP3, AAC/M4A or WAV for long audio.

## 2. The offset rule

Every visualise function takes `frame` as *the position in the audio file*. The kit's hooks compute
`frame - from + trimBefore`, where `from` is where the audio starts on the component's timeline. Two cases catch
people:
- The visualiser sits in a Sequence that starts at frame S while the audio plays from the composition start: its
  `useCurrentFrame()` is S frames behind, so pass `from={-S}` (or add S to the frame).
- The audio starts at frame F (`<Audio from={F}>`): pass `from={F}`; before F the visualiser shows silence.
The music-visualisation template's trick: put the `<Audio>` and all visualisers in one `<Sequence from={-offset}>`,
so their frames match the file.

## 3. Spectrum (`visualizeAudio`)

`visualizeAudio({audioData, frame, fps, numberOfSamples, smoothing = true, optimizeFor = 'accuracy',
dataOffsetInSeconds})` -> `numberOfSamples` magnitudes 0 to 1, bass first. Facts from the source:
- It runs an FFT of `2 * numberOfSamples` samples centred on the frame; bin k is `k * sampleRate / (2 *
  numberOfSamples)` Hz (1024 samples at 48 kHz: 23 Hz bins over a 43 ms window).
- `numberOfSamples` must be a power of two; `optimizeFor: 'speed'` for many samples or Lambda (the v5 default).
- `smoothing` averages the frames before and after (three FFTs per call).
- Magnitudes are divided by the loudest sample in the loaded data, so levels can shift slightly when a much louder
  window loads.

Raw FFT bars are bass-heavy and flicker. What the kit's `useAudioSpectrum` does, and what the templates do:
1. Log-spaced bands: bar i covers `minHz * (maxHz / minHz)^(i / bars)` to the next edge (40 Hz to 12 kHz); take the
   RMS of the bins inside.
2. Decibels with a tilt: `20 * log10(v) + tilt * log2(centre / 1000)` for bands above 1 kHz (3 dB per octave), so the
   highs are not always flat.
3. Map a dB range to 0 to 1 (-62 to -12 by default), clamp; shape with a power of 1.1 to 1.2 at draw time.
4. Fall-off without state: `bar(t) = max over j of value(t - j) * decay^j` for j up to 4 (decay 0.7), so bars drop
   like a meter, deterministically.
Template variants worth knowing: the music-visualisation template keeps the lower half of the bins, picks bar i at
log index `round(maxIndex ^ (i / bars))`, multiplies by a gain that grows with frequency, compresses with a power of
0.8 to 0.6, normalises and applies `^ 0.9`; the audiogram template keeps the low bins from a start index, mirrors them
and draws `300 * sqrt(v)` px bars; a bass flash averages the first 32 of 128 bins times 3 into a full-frame colour
at `min(0.5, avg * 0.8)` opacity.

## 4. Waveforms

- `visualizeAudioWaveform({audioData, frame, fps, windowInSeconds, numberOfSamples, channel, dataOffsetInSeconds,
  normalize = false})` averages absolute samples in `numberOfSamples` blocks across a window centred on the frame and
  flips the sign of every other block: an envelope zig-zag, not the true wave. It throws when
  `windowInSeconds * sampleRate < numberOfSamples`. Looks: `windowInSeconds` 1/fps (live), 10/fps (sliding); a
  stepped look by passing `frame: Math.round(frame / 3) * 3`.
- The kit's `AudioWave variant="line"` draws the true samples over 40 to 100 ms (a short average against aliasing,
  `tanh` to round off peaks) through `createSmoothSvgPath`: an oscilloscope.
- `AudioWave variant="scroll"`: RMS per time slice on a fixed grid (so bars do not flicker), sliding past a centre
  playhead, played part in the accent, the rest faint, fading at both ends. Good under a podcast title.
- A static full waveform with progress: `getWaveformPortion` over the whole file with `useAudioData` (short files).

## 5. Radial rings and reactive layers

- `AudioCircle`: spectrum bars around a circle, mirrored so bass sits at the top, a slow spin (4 to 8 degrees per
  second), the inner content scaled by the bass (`pulse` 0.03 to 0.05).
- `useAudioLevel({src, band: [30, 150]})` gives one 0 to 1 bass level: drive a glow (opacity 0.12 + 0.1 * level), a
  logo scale (1 + 0.04 * level) or a light. Keep the reaction small: big whole-frame throbs tire the eye.

## 6. Audiogram layout

A podcast clip for social: cover, title, captions, waveform, progress.
- 9:16 (Reels, Shorts, TikTok): everything between y 270 and 1248 and x 65 to 940 at 1080x1920 (the kit's safe
  area); below is platform UI. Order: show line, title (2 lines, about 60 px), the cover in a ring (340 px), the
  caption line (46 px, 2 lines), the scrolling strip and progress with times.
- 1:1: the same order, smaller cover. 16:9: cover ring on the left, the text column on the right.
- Captions: 2 to 4 words per page for punchy clips, a sentence per page for calm ones; the spoken word in the accent,
  spoken words in the text colour, upcoming words dimmed (not invisible); keep leading spaces and `white-space: pre`.
- One accent colour for the ring, the played strip and the active word. A soft radial glow behind the cover that
  breathes a little with the bass.
- Mount the `<Audio>` once (the Audiogram does it unless `playAudio={false}`); a quiet music bed under a podcast is
  optional and ducks like any voice-over.

## 7. Performance

- Each visualiser runs its own analysis per frame; share one `useAudioSpectrum` result between elements when you
  draw several from the same file.
- Fall-off costs one extra FFT per lookback frame; 1024-sample FFTs are cheap.
- `useAudioData` decodes the whole file in every render tab: fine for 20 s, wasteful for an hour.
- `optimizeFor: 'speed'` on Lambda and for 1024 or more samples.
