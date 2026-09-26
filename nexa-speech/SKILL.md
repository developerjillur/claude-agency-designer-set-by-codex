---
name: nexa-speech
description: "Voice-overs, narration and character voices with Google Gemini text-to-speech (3.8 Flash TTS by default) that keep one voice and one delivery from the first second of a video to the last: a pinned voice profile, sentence-safe chunks, a cache so nothing is paid for twice, measured QA gates with one automatic re-roll, a 48 kHz master at -16 LUFS with an exact timeline, word and sentence timings, SRT and VTT captions, and fitting to scene lengths. English and Bangla (numbers read as Bangla words with lakh and crore, a lexicon for names). Use it whenever a request asks for a voice-over, VO, narration, dialogue or character voices for a video, reel, ad, explainer, tutorial, documentary or story, Banglish asks included ('voice over banao', 'VO lagbe', 'script ta voice e porao', 'Bangla narration koro'). It feeds nexa-video-creator; write or fix the script itself with natural-text."
---

# nexa-speech

Gemini text-to-speech for paid client videos, with the cost known before a call, every call logged, and the quality
measured instead of assumed. Command prefix: `python3 ~/.claude/skills/nexa-speech/scripts/speech.py`. Every command,
flag and file format is in `references/cli.md`; writing for the ear, the tags, pronunciation, drift and platform rules
are in `references/craft.md`; the sourced facts are in `references/research-notes.md`.

Checked on the live API (2026-09-25): `say`, `render`, `master` and `align --engine gemini` in English and Bangla
with gemini-3.8-flash-tts and gemini-3.5-transcribe (every word spoken, the numbers read right, 100 % of the words
aligned). Not yet run live: `design` (it stores voices in the key's project), `voices --library`, the 3.1 and 2.5
models, `send_language_code` and `align --engine elevenlabs`; watch their first real run
(`references/research-notes.md` lists what is unverified).

Measured against ElevenLabs the same day (the same lines, a Gemini listening judge, 0 to 10, and the character error
rate of a transcript): English, Gemini Iapetus natural 8, ElevenLabs v3 and Multilingual v2 (Eric) 9, all accent 10,
no errors; Bangla, Gemini Sadaltager natural 9 and accent 10, ElevenLabs v3 River 8 and 9, Sia 9 and 9, the same
error rate. So Gemini stays the voice for English and Bangla here (cheaper, native Bangla, the gates and cache built
around it); ElevenLabs is worth it only for a cloned or brand voice or a scene with 3 or more speakers, which this
skill does not make.

## Fast path (do exactly this)

1. **Voice (once per voice):** `profile new NAME --preset ID` (`presets` lists 15). The profile pins the model, the
   voice, the style and the pace; editing it later bumps its version by itself. For a Dhaka accent on 3.8, design a
   voice once (`design ...` with the preset's prompt, then `design keep ID --profile NAME`).
2. **Script:** plain text with `# Scene` headings and blank lines between paragraphs (format: `references/cli.md`).
   Write it for the ear (`references/craft.md`); numbers may stay as digits, the tool reads them out.
3. **Plan (free):** `plan SCRIPT --profile NAME --out DIR`. Read the chunks, the warnings and the cost. Fix every
   warning in the script or the lexicon; `render` refuses warnings unless `--force`.
4. **Render:** `render SCRIPT --profile NAME --out DIR` (run it in the background for long scripts). Only what is not
   cached is paid for; the gates run on every take and a failing chunk gets one automatic re-roll.
5. **Master:** `master DIR` gives `vo_48k.wav` (48 kHz, 24-bit, -16 LUFS, -1.5 dBTP) and `vo.manifest.json`.
6. **Captions:** `align DIR` gives `words.json`, `sentences.json`, `vo.srt` and `vo.vtt` (free from the pauses; with
   a key, `--engine gemini` adds word timestamps for about $0.005 a minute; `--engine elevenlabs` times the known
   script instead, $0.22 an hour, and flags words the voice may not have said).
7. **Client final:** `qa DIR --asr` (Gemini transcribes every chunk; a Bangla word heard differently is named), listen
   to anything flagged, then `pick DIR CHUNK TAKE` (the gates run again on the pick) or
   `render ... --only c007 --takes 3`, and `master` again.
8. **Scene lengths from the edit:** `fit DIR --scenes scenes.json`, then `--apply`.

A single line (a hook, an outro, a sting): `say "TEXT" --profile NAME --out line.wav`, cached and mastered.

## Commands

| Command | What it does | Paid |
|---|---|---|
| `doctor [--live]` | key sources (names only), ffmpeg and its filters, the cache, voices near expiry; `--live` lists the models the key's project sees | `--live` is a free call |
| `voices [--gender f\|m] [--find WORD]` | the 30 prebuilt voices; `--library [--lang bn-BD] [--search W]` searches Google's 3.8 voice library | library: free call |
| `presets` | the 15 presets (voice, style, pace, Bangla design prompts) | no |
| `profile new\|show\|list` | make, read and list voice profiles | no |
| `design --desc ... --gender G --lang L --takes 3 --out DIR`, `design keep ID --profile NAME` | 3.8 voice design: samples to audition, then pin one | yes |
| `audition --voices A,B,C --text FILE --profile NAME --out DIR` | one text of 15 s or less in several voices, loudness-matched, cost first | yes |
| `plan SCRIPT --profile NAME` | parse, normalise, chunk; seconds, requests, tokens, USD | no |
| `render SCRIPT --profile NAME --out DIR` | synthesise what is not cached, gates, one re-roll, ledger (`--takes`, `--only`, `--budget`, `--force`, `--asr`) | yes |
| `pick DIR CHUNK TAKE` | choose a take by hand | no |
| `say "TEXT" --profile NAME --out FILE` | one line, cached and mastered | yes |
| `qa DIR [--asr]` | the gates again, `qa.json` and a table; `--asr` adds the transcript gate | `--asr` |
| `master DIR` | the finished voice-over and its manifest | no |
| `align DIR [--engine auto\|gemini\|elevenlabs\|pauses]` | word and sentence timings, SRT and VTT | gemini, elevenlabs |
| `fit DIR --scenes FILE [--ad] [--apply]` | gaps first, then one tempo per scene, else what to cut | no |
| `cost [DIR] [--minutes 10] [--model M]` | an estimate, or the actual numbers from `ledger.jsonl` | no |

`--json` on any command prints one JSON object on stdout (for nexa-video-creator and other skills).

## How one voice is kept

- **One model per video.** A voice name sounds different on another model; switching models means re-rendering all.
- **One voice:** a prebuilt name, or a designed `voice_...` id with its `expire_time` (warned 30 days ahead).
- **One short style**, sent byte for byte in `speech_metadata.style` on 3.8 (never in the text: 3.8 reads the text
  aloud word for word) or in `### PERFORMANCE` on 3.1 and 2.5. Delivery changes only through the profile's named modes
  (`@mode story`). No temperature, ever; no language code unless the profile asks for it.
- **Chunks:** 1 to 4 whole sentences of one scene, speaker and mode, 12 to 35 s, never over 45 s (and 124 words or
  1,488 characters in Bangla); one request per chunk and per dialogue turn; fragments under six words ride with a
  neighbour; ads and tutorials go one sentence per chunk. Gaps between chunks are exact silences laid in post.
- **Post:** every chunk trimmed, faded and gain-matched to the median; one room tone under the whole track; one
  two-pass loudness step in linear mode, never shipped in dynamic mode.

## QA gates (every take, `references/cli.md` has the numbers)

1. Audio present, finish reason fine (truncated audio is billed and fails), WAV header handled.
2. Voiced duration against the words at the voice's pace: outside 0.80 to 1.25 fails once the pace is measured (3
   chunks), outside 0.65 to 1.50 before (3.8 Flash speaks up to 39 % faster than a preset guesses).
3. Lead-in under 20 ms, a click at the start, noise after the last word: flagged and fixed in `master`.
4. `--asr`: WER over 3% (English) or CER over 5% (Bangla, compared by sound, not spelling), words missing or extra at
   the end, direction words heard, a lexicon term or `{display|spoken}` respelling not heard: fails. A Bangla word
   heard differently under the 5% (one wrong vowel) is named as a flag.
5. Drift, from 5 chunks: speaking rate beyond 12% of the median, loudness beyond 4 LU, spectral centroid beyond 2 SD:
   fails. Speaker similarity needs a speaker-embedding model and is not measured: listen to the hero chunks.
6. Clipping: flagged.

Gates 1, 2, 4 and 5 earn one automatic re-roll (a new take, in the ledger). Safety refusals, quota, billing and bad
requests go to the user and are never retried in a loop. `@takes N` chunks keep every take and the best score wins.

## Money

Prices as of 2026-09-25 (USD per 1M tokens, audio out and text in; 32 audio tokens a second, as the live API's usage
showed):

| Model | Audio out | Text in | 10 min, one take each |
|---|---|---|---|
| `gemini-3.8-flash-tts` (default) | $9.00 to 2026-12-31, then $18.00 | $0.50, then $1.00 | about $0.17 |
| `gemini-3.8-flash-lite-tts` | $6.00, then $12.00 | $0.50, then $1.00 | about $0.12 |
| `gemini-3.1-flash-tts-preview` (legacy) | $20.00 | $1.00 | about $0.38 |
| `gemini-2.5-flash-preview-tts` (legacy) | $10.00 | $0.50 | about $0.19 |
| `gemini-2.5-pro-preview-tts` (legacy) | $20.00 | $1.00 | about $0.38 |

Word timings (`gemini-3.5-transcribe`) cost about $0.005 a minute. One public test was billed about 1.5x the token
arithmetic at 25 tokens a second; at the measured 32 about 1.2x is left, so `cost` shows a likely bill at 1.2x, and
`ledger.jsonl` keeps the `usage` of every answer to check against. Every
paid command has `--budget USD` (default 1.00) and refuses work whose estimate is higher.

## Policy

- Use a key from a Google Cloud project with billing on: on the free tier Google may use what you send to improve its
  products. Never send a client's script on a free-tier key.
- Label realistic synthetic voices where the platform asks: YouTube (realistic synthetic content, and any clone of
  someone else's voice), Facebook and Instagram (realistic audio made or altered digitally), TikTok (AI audio that
  imitates a real person). Details and sources: `references/craft.md`.
- No voice cloning here. Replicating a voice needs the owner's recorded consent, verified by the API, and is not
  offered in some regions; for client work also get written permission and never replicate a public figure.
- Never present a synthetic voice as a real customer, expert or presenter.
- The Bangla number words still wait for a native reader's check (`CHANGELOG.md`): until then, read the spoken text
  in `plan.json` of a Bangla script before its client render.

## Time, measured on this machine (2026-09-25, Mac Studio, M4 Max)

Local work only, against a stand-in server that answers at once; the real API time comes on top and is not measured
here (see the research notes: one public test made 78 s of speech in about 20 s).

| Step | Time |
|---|---|
| `plan` of a 3.5-minute script | 0.07 s |
| `render` local work, 17 takes (3.5 min) | 0.7 s, and 0.1 s when all is cached |
| `master` of 3.5 minutes / 10.8 minutes | 3.4 s / 9.6 s (peak memory 241 MB) |
| `align --engine pauses`, 3.5 / 10.8 minutes | 0.2 s / 0.6 s |
| `fit --apply` (includes a new master), 3.5 minutes | 3.4 s |
| `say` of a 4 s line / `audition` of 3 voices | 0.4 s / 0.8 s |
| Offline test suite (73 tests) | about 15 s |

Measured on the 3.5-minute master: integrated -16.0 LUFS, true peak -4.0 dBTP, sentence starts within 4.1 ms of the
measured onsets (mean 1.1 ms), an `@pause 1.5` measured at 1.500 s.

## Files

- `scripts/speech.py`: the CLI (Python 3.9 standard library, ffmpeg). `scripts/gemini_api.py` and
  `scripts/elevenlabs_api.py`: the shared clients (keys, calls, errors), identical in every nexa skill.
  `scripts/voices.json`, `scripts/presets.json`: data.
- `~/.nexa-speech/`: `profiles/`, `cache/` (paid masters and their sidecars, never deleted), `designs.jsonl`.
- In a project folder: `plan.json`, `takes.json`, `masters/`, `analysis/`, `qa.json`, `calibration.json`,
  `ledger.jsonl`, `vo_48k.wav`, `vo.manifest.json`, `words.json`, `sentences.json`, `vo.srt`, `vo.vtt`, `align.json`,
  `fit.json`.
- `tests/`: offline tests with a fake Gemini server (`python3 -m unittest discover -s ~/.claude/skills/nexa-speech/tests`).
