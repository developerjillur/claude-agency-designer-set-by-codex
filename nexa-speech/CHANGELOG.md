# Changelog: nexa-speech

The version is `SKILL_VERSION` in `scripts/speech.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/nexa-speech/tests`, and run `plan`, `render`, `master` and `align`
once by hand (against the real API only when a key and a budget are agreed).

## 2026.09.25.1 · first release

Built from the Gemini TTS research of 2026-09-25 (`references/research-notes.md`), offline, with no key.

- **Before a client release:** a native Bangla reader must check the number words: the 0 to 99 table in
  `scripts/speech.py` (`BN_0_99`, copied from the build spec), the hundreds, the years before সাল, the ordinals 1 to
  10, the times and the taka and percent readings.
- **Voice profiles:** everything that shapes the voice pinned in one JSON file (model, prompt family, voice with its
  expiry, language, style, modes, tags, pace, gaps, chunk limits, numbers, lexicon, loudness, post, takes). A change to
  the model, voice, style, modes or lexicon content bumps the version, also after a hand edit. 30 prebuilt voices and
  15 presets (with the four Bangla voice-design prompts) in `scripts/voices.json` and `scripts/presets.json`.
- **Script format:** scenes, `@cast` dialogue, `@profile`, `@mode`, `@takes`, `@pause`, comments,
  `{display|spoken}` pairs and 3.8 tags (turned into square-bracket tags for 3.1 and 2.5).
- **Text:** captions keep what is written, the voice gets it spoken: a lexicon, English numbers (money, percentages,
  ordinals, years, times, decimals), Bangla numbers with lakh and crore and years before সাল, and warnings for
  Latin words inside Bangla, addresses, symbols, leftover digits and page-only words (`render` refuses them without
  `--force`).
- **Chunking:** 1 to 4 whole sentences of one scene, speaker and mode, 12 to 35 s, never over 45 s (and 124 words or
  1,488 characters in Bangla), fragments merged, lone lines with no style and two takes, one sentence per chunk for
  ads and tutorials, exact gaps stored after each chunk.
- **Requests:** 3.8 with the transcript in `text` and the style in `speech_metadata`; 3.1 and 2.5 with the director
  block; 16-bit PCM requested, a RIFF answer never wrapped twice; three at a time; no temperature.
- **Cache:** every paid take in `~/.nexa-speech/cache/KEY.wav` with a sidecar, linked into the project; never deleted;
  a second render of the same script makes no call.
- **Gates:** audio and finish reason, the duration ratio against the calibrated pace, edges (lead-in, click, noise
  after the last word), a transcript check with `--asr`, drift from 5 chunks (rate, loudness, spectral centroid) and
  clipping; one automatic re-roll for a failing chunk, best of N for `@takes`, `pick` by hand. Speaker similarity is
  not measured (it needs a model).
- **Master:** trim, fades, gain matching, exact gaps over one room tone, a gentle clean-up chain, two-pass `loudnorm`
  in linear mode with a limiter first when needed (never shipped dynamic), 48 kHz 24-bit, checked with `ebur128`;
  `vo.manifest.json` with scenes, chunks and sentences timed to the millisecond.
- **Timings and captions:** `align` from the pauses (free) or `gemini-3.5-transcribe` (word timestamps matched to the
  script); `words.json`, `sentences.json`, SRT and VTT with balanced cues, 2 lines of 42 graphemes, no line starting
  with a danda.
- **Fit:** gaps first, then one tempo per scene within 6% (10% for ads, neighbours within 3%), else the seconds and
  words to cut; `--apply` keeps the old master.
- **Money:** a dated price table, an estimate before every paid call, `ledger.jsonl` after it (with the API's `usage`
  and the key's source name, never the key), and `--budget` (1.00 USD by default) on every paid command.
- **Measured (2026-09-25, Mac Studio, M4 Max, local work against a stand-in server):** a 3.5-minute master in 3.4 s
  and a 10.8-minute one in 9.6 s; -16.0 LUFS and -4.0 dBTP measured; sentence starts within 4.1 ms of the measured
  onsets; an `@pause 1.5` measured at 1.500 s.
- **Review fixes before release:** the language-code setting is part of the cache key and the profile's version (a
  changed setting no longer reuses audio made without it); subtitle cues of short sentences with no gap no longer
  overlap; `render --asr` transcribes only the takes the run asked for, so the budget check counts what is spent;
  `fit --apply` puts the old master back when the new one fails.
- **Tests:** 67 offline tests with a fake Gemini server (speech whose length follows the words, scripted daily-quota,
  safety, server-error, truncation, refusal and two-part answers, voices, models and transcripts), about 13 s on
  Python 3.9 and 3.12.
- **Untested against the real service:** every API call (see "Unverified" in `references/research-notes.md`).
