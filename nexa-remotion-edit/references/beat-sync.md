# Cutting and moving on the beat

Beat sync times cuts, not amplitude. Use it only when the track is rhythmic, and let narration win when the two
disagree.

## 1. The grid

- A beat grid is the list of beat frames: `beatGrid(bpm, fps, durationInFrames, offsetSeconds)` from core (frames
  rounded once). At 120 BPM and 30 fps a beat is exactly 15 frames; at 128 BPM 14.0625 frames, so round from the
  formula `round((offset + k * 60 / bpm) * fps)`, never by adding a rounded step (drift).
- `offset` is the time of the first downbeat in the file (seconds). The kit's demo track has it at 0.
- The kit: `useBeatGrid(bpm, offset)` over the Sequence, `beatFrame(k, bpm, fps, offset)`, `beatAt(frame, grid)` ->
  `{index, beatFrame, since, phase, bar, beatInBar}`, `snapCuts(cuts, grid, window)`, `beatCuts(grid, every)`,
  `beatPulse(frame, grid, {decay, every, phase})`, `<OnBeats>`, `<BeatPulse>`.

## 2. Measuring tempo and downbeat (before building)

- Offline, in Python: `librosa.beat.beat_track(y, sr)` gives a tempo and beat times; fit a uniform grid
  `t_i = t0 + i * T` to the beat list by least squares (the reported tempo can be 2 % off) and accept it when the
  residuals stay within +-15 ms. Test half and double tempo: pick the one where kicks land on whole beats.
- Dense mixes: separate the drums first (HPSS or Demucs) and detect on the drum stem.
- Without Python: tap the tempo in a DAW or read it from the track's metadata, then find the first kick with
  `ffmpeg -i track.wav -af silencedetect=n=-40dB:d=0.05 -f null -` or by looking at a waveform.
- If the analyser says the track is not rhythmic, do not cut to its grid: transition on energy changes (RMS with a
  hop of 256 samples finds the climax) and use silences as holds.
- Store `BEAT0` (the analysis) and any measured output offset as two separate constants.

## 3. Cutting

- Scene cuts on strong beats (bar starts, snares); a shot every 2 or 4 beats for a montage (`<OnBeats beats={4}>`),
  faster only for a short build.
- Internal events (a text slam, a zoom, a light) snapped to the nearest beat within 6 frames (`snapCuts`);
  realigning drifting internal events is often the single biggest improvement to a music video.
- Narration wins: when a sentence gap and a beat disagree, cut on the beat nearest the gap.
- A transient and the swell 9 to 15 frames later are two events: impact first, reveal second.
- Do not duck the music on a synced hit.

## 4. Pulsing

- Pulse elements, not the frame: a dot, a logo, a line, a light (`<BeatPulse amount={0.06} decay={9}>`, or
  `beatPulse()` into any property).
- Whole-frame or camera hits: at most 3 per film, at least 16 beats apart, on the strongest measured hits. A frame
  that scales on every beat reads as a cheap template.
- Pulse on the element's own rhythm: `every={4}` once a bar for a logo, `every={1}` only for small UI such as beat
  dots or meters.
- A pulse is an attack and a decay: full on the beat, back to rest within 8 to 10 frames (ease out). Never a
  continuous sine throb.

## 5. Checking

- Stills at each cut and 12 frames later (`nrk.py stills --frames`) to see what lands.
- After the render: extract the audio, re-detect beats, compare with the cut frames; within 3 frames passes, within
  1.5 is ideal. 30 fps cannot be more precise than +-16.7 ms.
- AAC adds a small start delay in the delivered file (about 1.3 frames at 30 fps on one measured pipeline): measure
  once and put the correction in its own constant if hits must be frame exact.
