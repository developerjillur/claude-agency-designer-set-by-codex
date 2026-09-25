# Changelog: nexa-speech

The version is `SKILL_VERSION` in `scripts/speech.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/nexa-speech/tests`, and run `plan`, `render`, `master` and `align`
once by hand (against the real API only when a key and a budget are agreed).

## 2026.09.25.2 · the first live run

An English line (`say`), a Bangla voice-over (`render`, `master`) and `align --engine gemini` on the live API
(2026-09-25), with gemini-3.8-flash-tts (Iapetus, Sadaltager) and gemini-3.5-transcribe. Every word was spoken
(checked by whisper and by Gemini); the numbers read as দশ and পাঁচশো. What the real answers changed:

- **32 audio tokens a second, not 25.** The usage the API reported (77 tokens for 2.4 s, 214 for 6.7 s) makes every
  estimate 28 % higher: 10 minutes on 3.8 Flash is $0.173, not $0.135. The "likely bill" factor drops from 1.5 to
  1.2, since the old 1.5 was mostly this rate.
- **Gate 2 before the pace is measured.** 3.8 Flash spoke 2 to 39 % faster than the presets guess, in English and
  Bangla, with every word present; one Bangla chunk (ratio 0.72) failed and was paid for twice. Until a voice's pace
  is measured (3 chunks of the project, calibration.json or the profile), the window is 0.65 to 1.50, which still
  catches a missing sentence; after that it stays 0.80 to 1.25. `takes.json` records the window used.
- **Align matches what Gemini writes.** It joined আসসালামু আলাইকুম into one word, wrote 10 and 500 for দশ and
  পাঁচশো, and কিভাবে for কীভাবে: 86 % of the script matched. Digits are now read in the language around them,
  ী and ি, ূ and ু and a final ো are folded for matching, joined or split words share the heard time by length, and
  alike words between two matches pair up: 100 %.
- **The ledger before the file.** A paid take is logged as soon as the answer arrives, so a save that fails
  (a full disk) cannot hide it.
- **What the live answers look like:** raw 16-bit PCM (`audio/l16; rate=24000; channels=1`, with `sample_rate`
  and `channels` fields), `status: completed`, no finish reason at all, no interaction id with `store: false`;
  word timings as `word_info` annotations in 0.1 s steps (`"3s"`, `"0.100s"`); transcription bills audio input
  at 25 tokens a second and reports no output tokens. The fake server in the tests now answers the same way.
- **Tests:** 72 (a failed save still in the ledger, the gate 2 windows, the live Bangla transcript's joins, digits and spellings, the new prices).

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
