# Rendering sound and checking the delivered file

A mix is done when the delivered file measures right, not when the preview sounds right.

## 1. Render flags that touch sound

| Goal | Flags (CLI) | Node `renderMedia()` |
|---|---|---|
| Social or web MP4 | `--codec=h264 --crf=18 --pixel-format=yuv420p --color-space=bt709 --audio-codec=aac --audio-bitrate=320k` | `codec: 'h264', audioCodec: 'aac', audioBitrate: '320k'` |
| Sample rate | `--sample-rate=48000` (default) or 44100 when every source is 44.1 kHz | `sampleRate` (4.0.448) |
| No audio track | `--muted` | `muted: true` |
| Silent track when there is none (chunks you will join) | `--enforce-audio-track` | `enforceAudioTrack: true` |
| A stem next to the video | `--separate-audio-to=out/mix.wav` (the extension picks the codec) | `separateAudioTo` |
| Audio only | `out/mix.mp3 --codec=mp3` (or aac, wav) | `codec: 'mp3', imageFormat: 'none'` |
| Uncompressed audio in the video | `--audio-codec=pcm-16` (h264 goes to .mkv or .mov) | `audioCodec: 'pcm-16'` |
| ProRes master | `--codec=prores --prores-profile=hq` (PCM audio) | |
| A section only | `--frames=120-359` | `frameRange: [120, 359]` |
| Highlights from one timeline | `--frames=0-149,600-749` (4.0.502; audio of the gaps is dropped) | `frameRange: [[0, 149], [600, 749]]` |

With `nrk.py render PROJECT --preset web` the kit passes the web row for you. The Node APIs ignore
`remotion.config.ts`: pass every option explicitly.

## 2. Measure the delivered file

```bash
# streams: is there audio, at what rate, how long
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,sample_rate,channels -of compact=p=0 out.mp4
# peak and mean
ffmpeg -hide_banner -nostats -i out.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
# integrated loudness, range and true peak
ffmpeg -hide_banner -nostats -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -A 14 "Summary:"
# silences (gaps, cut points, a missing track)
ffmpeg -hide_banner -nostats -i out.mp4 -af silencedetect=n=-45dB:d=0.3 -f null - 2>&1 | grep silence_
```
Targets: an audio stream at 48 kHz; about -14 LUFS integrated for social video (-16 podcasts, -23 broadcast); true
peak at or under -1 dBTP; no unexpected silence.

## 3. Prove the bed ducks (band-split method)

A full-mix meter cannot separate the music from the voice. Measure a band only one of them occupies, per 0.25 s:
```bash
# music band: below 90 Hz (kick and bass); the voice has almost nothing there
ffmpeg -i out.mp4 -af "pan=mono|c0=0.5*c0+0.5*c1,lowpass=f=90,lowpass=f=90,lowpass=f=90,asetnsamples=n=12000,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=music.txt" -f null -
# voice band: above 1.2 kHz (the voice's formants and consonants)
ffmpeg -i out.mp4 -af "pan=mono|c0=0.5*c0+0.5*c1,highpass=f=1200,highpass=f=1200,asetnsamples=n=12000,astats=metadata=1:reset=1,ametadata=mode=print:key=lavfi.astats.Overall.RMS_level:file=voice.txt" -f null -
```
`n=12000` is 0.25 s at 48 kHz. Read `pts_time` and `RMS_level` pairs from the files and compare windows inside the
voice with windows in gaps. The kit's DemoEditDucking measured: the music band at -37 to -41 dB under the voice and
-18 to -19 dB in the long gap (the 18.4 dB duck it was set to), staying down through a 1.9 s pause (bridged),
integrated -14.2 LUFS, peak -3.3 dBFS. When the voice and the music share a band, render once with the voice muted
(a boolean prop) and measure the bed alone.

## 4. Other checks

- A/V sync at cuts: spot-check the first frames after each cut; a sync pip (a 1 kHz tone on a flash frame) in test
  footage makes drift visible in `silencedetect` and stills.
- Offsets: AAC encoding adds a short delay at the start (about 2048 samples at 48 kHz on one pipeline); for
  frame-exact hits, cross-correlate the delivered audio with the source once and correct in a constant.
- Loop points: render the last and first seconds of a looping bed; listen for a click.
- Stills at cuts and 12 frames later before the full render: `nrk.py stills PROJECT --frames 0,59,60,72`.
- The render log: grep for "falling back" (codec or CORS problems) and for delayRender timeouts.

## 5. Pre-render checklist for footage and sound

1. Every source through `staticFile()` or a CORS-enabled URL; SFX copied into `public/` for offline renders.
2. H.264/VP8/VP9 video, AAC/Opus/MP3/FLAC audio, constant frame rate, faststart; no H.265 or AV1 unless the offthread
   engine is intended; the ProRes decoder registered if ProRes is used; a plan for alpha.
3. The composition length is an integer from `calculateMetadata()` or `editLength()`; Series lengths match trims and
   speeds; ramps end before the file does (`rampLength`).
4. Volume curves clamped on both sides, nothing at 100, the bed ducked under speech, B-roll muted.
5. Caption JSON and fonts gated by `delayRender`; captions remapped through the cuts.
6. A short range rendered first (`--frames`), the log read, then the full render and the measurements above.

## 6. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| No audio stream in the MP4 | `--muted`, every track muted, or no audio tags | check props; `--enforce-audio-track` if silence is intended |
| Music louder than the voice | an unleveled voice, `duckTo` too high, a hot master | level the voice to -16 LUFS; `duckTo` 0.04 to 0.06 |
| Music swells between sentences | pauses longer than `bridge` or ramps too fast | raise `bridge`, lengthen `release` |
| Clicks at cuts inside sound | hard cuts mid-waveform | `declick={2}` on JumpCuts, or cut in pauses |
| Distortion | gains above 1 on a hot file, several loud tracks | lower gains; keep peaks under -1 dBTP |
| Audible steps in a fade | a fade shorter than 6 frames | lengthen it |
| SFX late on the hit | the file has silence at its head, or `hit` not set | trim the file; set `hit` to its peak frame |
| Remote SFX missing in an offline render | `@remotion/sfx` URLs are remote | copy into `public/sfx/` |
| "Volume was set to 100" | an unclamped `interpolate()` as volume | clamp both sides or use `volumeCurve()` |
| A visualiser shows the wrong part of the song | frame not offset to the audio position | pass `from` (and `trimBefore`) to the kit hooks |
| `windowInSeconds cannot be changed dynamically` | a prop that changes after mount | keep it constant (remount with a new key to change it) |
