# Changelog: nexa-video-creator

The version is `SKILL_VERSION` in `scripts/nvc.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/nexa-video-creator/tests` (and with `NVC_RENDER_TESTS=1` once the
renderer is set up).

## 2026.09.25.2 · the first live run

A Bangla job on the live API (2026-09-25): Gemini 3.5 Transcribe with `bn-BD`, then a 10 s faceless edit from the
nexa-speech voice-over and a Lyria 3.5 bed (compile, audio, stills, render, qa: all clean). What it changed:

- **A breath is never a word.** The snap let each pause claim the nearest free word boundary; a breath between two
  sentences split one pause into two, and আজ landed on the breath (0.4 s early) while the next word took আজ. Each
  pause now goes to the boundary nearest to it, measured to the span between the two words' heard edges, and a
  boundary with two pauses ends the first word at the first and starts the next after the last. The first and last
  words take the nearest speech edge, so a breath before the first word is skipped too.
- **Bangla numbers in Bengali digits.** Gemini writes 10 and 500 where the speaker said দশ and পাঁচশো; Bangla
  transcripts now show ১০ and ৫০০ (the house rule for Bangla copy), except after a Latin word (iPhone 15).
- **A nexa-speech voice-over keeps its language.** The manifest keeps the language per profile (bn-BD); the import
  looked for a top-level field, labelled a Bangla voice-over "en", and the edit brief said English.
- **Numbers on a time-placed overlay.** A hook at the start that shows a number the speaker says later in the edit
  (১০ at 3.2 s) is no longer sent for review; one said nowhere in the edit still is.
- **The compare card** sits in the middle with headline-sized text when nothing is behind it (voiceOnly, brollFull);
  it was small and high on the frame.
- **Measured:** the 10.45 s edit rendered in 8.2 s (0.76 s a second of video), mixed at -14.0 LUFS, -2.7 dBTP.
- **Tests:** 30 (snapping with a breath, Bengali digits, the voice-over's language, time-placed numbers).

## 2026.09.25.1 · first release

Built from six research reports written on 2026-09-25 (editing craft, Remotion for real footage, HyperFrames, audio
post and footage, Lyria, Gemini TTS) and tested on a synthetic camera and screen-recording pair.

- **The pipeline:** `new`, `add`, `ingest`, `sync`, `clean`, `transcribe`, `brief`, `compile`, `audio`, `stills`,
  `render`, `qa`, `deliver`, plus `segment` for remotion-broll and HyperFrames clips, `status` and `doctor`.
- **Sync:** onset-envelope cross-correlation, then GCC-PHAT windows and a Theil-Sen drift fit per segment
  (`nvc_sync.py`). On the test pair: +2.3700 s found for a true 2.37 s in 0.4 s. In the research it found a 24.6 min
  pair to 0.04 ms with 62.5 ppm drift, and split recordings that paused or dropped samples into segments.
- **Words:** whisper.cpp with DTW token times (`-dtw`, and `-nfa` because flash attention turns DTW off), then every
  measured pause claims the nearest word boundary. On the test pair the plain segment offsets put a word 1.5 s late
  inside a pause; DTW matched the speech. Bangla: Gemini 3.5 Transcribe with word timings when a key exists, agy
  sentences otherwise. A nexa-speech voice-over brings its own word timings.
- **The plan and the compiler:** Claude writes `plan.json` grounded to word ids and exact quotes; the compiler checks
  quotes, ids, overlaps, reading times, numbers not said, the hook, the length limit, static stretches, chapters and
  source coverage, then lays every cut on the frame grid (50 ms before and 80 ms after kept words, no cut in a pause
  under 150 ms, long pauses trimmed per target, bounded filled pauses cut by themselves).
- **The renderer:** a Remotion 4.0.528 project (shared, synced from `template/`) with layouts camFull, screenFull,
  screenPip, split (sized to the recording's shape), stack, brollFull and voiceOnly; face-centred crops and
  automatic punch-ins within the source's resolution; zooms that clamp at the edges; hook, keyword, stat (count-up),
  list, compare, quote, chapter, lower-third, CTA, b-roll, image and segment overlays; callouts and redactions that
  move with the recording's zoom; word and sentence captions (Bangla rules built in); zoom, whip, dip and flash
  transitions.
- **Sound:** the dialogue is cut sample-accurately on the same frame grid (30 ms fades), music is fitted and ducked,
  effects are placed, and the mix is mastered to the platform by nexa-sound; without nexa-sound the dialogue is
  normalised on its own.
- **Measured on the test pair:** ingest 6.5 s, sync 0.4 s, transcribe 1.7 s, stills 2.8 to 5.5 s, a 13.4 s 1080p
  render in 11.5 s; the mix at -14.2 LUFS and -4.0 dBTP.
- **Review fixes before release:** a source added but not ingested is now an error instead of a blank stretch; zoom
  overlaps are checked per layer; subtitle cues can no longer overlap; word captions no longer double punctuation
  in the subtitle files; a hold on a segment's last word now keeps its pause; transparent cutouts respect a box;
  subtitle files follow the target's line length (42 characters on 16:9, 32 on narrower frames).
- **ffmpeg 7 and later:** the dialogue cut reads its filter graph with `-/filter_complex FILE`; newer builds removed
  `-filter_complex_script` (deprecated in 7.0), and the old option is used only on ffmpeg 6 and earlier.
- **Tests:** 25 offline tests (the compiler's rules, the review fixes, and the pipeline on synthetic media with a
  known 1.25 s offset).
