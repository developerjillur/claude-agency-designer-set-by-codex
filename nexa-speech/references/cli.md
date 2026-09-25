# speech.py reference

`python3 ~/.claude/skills/nexa-speech/scripts/speech.py <command> ...`

Every command prints a short plain summary on stdout; with `--json` it prints one JSON object instead. Progress goes to
stderr. Exit code 0 means success; 1 means an error, plan errors, refused warnings, a stopped or incomplete render, a
budget refusal, or `doctor` not ready; 130 means interrupted. Paths may use `~`.

## Environment

| Variable | Meaning |
|---|---|
| `GEMINI_API_KEY`, `GEMINI_API_KEY_1`, `_2` ... | the key, then failover keys; with none set, the macOS keychain item `GEMINI_API_KEY` is used. Keys are never printed or written; the ledger records only the source name (`GEMINI_API_KEY_1`). |
| `NEXA_SPEECH_HOME` | the home folder (default `~/.nexa-speech`): `profiles/`, `cache/`, `designs.jsonl`, `say/` |
| `FFMPEG` | the ffmpeg binary (default: the one on `PATH`) |
| `NEXA_GEMINI_BASE_URL`, `NEXA_GEMINI_SLEEP_SCALE`, `NEXA_NO_KEYCHAIN` | test hooks of `gemini_api.py`: a fake server, waits scaled (0 in tests), no keychain |

## Voice profiles

`~/.nexa-speech/profiles/NAME.json`, or `--profiles DIR` for a project's own. `profile new` writes one from a preset;
edit the file by hand for anything else: a change to model, voice, style, modes or the lexicon's content bumps
`version` the next time the profile is read (logged, with a `history` line).

```json
{"schema": "nexa-speech/profile-1", "name": "bn-yt-m", "version": 2, "preset": "bn-yt-explainer-m",
 "engine": "gemini-api", "model": "gemini-3.8-flash-tts", "prompt_family": "speech_metadata",
 "voice": {"id": "voice_abc123", "type": "designed", "expire_time": "2027-09-25T00:00:00Z", "sample": "design/design-1.wav"},
 "language": "bn-BD", "send_language_code": false,
 "style": "friendly Bangla explainer, conversational and clear",
 "modes": {"story": "calm and visual storytelling"},
 "tags_allowed": ["<short pause>", "<long pause>", "<breath>"],
 "wpm": {"target": 132, "min": 125, "max": 140, "measured_wps": null},
 "gaps_ms": {"sentence": 320, "paragraph": 750, "scene": 1100, "min": 180, "max": 900},
 "chunk": {"max_s": 45, "target_s": [12, 35], "max_words": 110, "max_chars_bn": 1488},
 "numbers": "words", "lexicon": "bn-brand.tsv",
 "loudness": {"stem_I": -16.0, "TP": -1.5, "LRA": 11.0},
 "post": {"highpass_hz": 70, "deess": 0, "room_tone": "pink", "room_tone_dbfs": -65.0},
 "takes": {"default": 1, "hero": 3, "max_auto_reroll": 1}, "precise": false,
 "design_prompt": "Native Bangladeshi Bangla-speaking man ...", "identity": {"...": "..."}, "history": ["..."]}
```

- `model`: one of the five in the price table; `prompt_family` must match it (`speech_metadata` for 3.8,
  `director_text` for 3.1 and 2.5).
- `voice.type`: `prebuilt` (a name from `voices`), `designed` (pinned by `design keep`, with `expire_time`),
  `library` (an id from `voices --library`) or `replicated` (a `voicekey_...`). The cache key uses the name, or
  `id@expire_time` for designed and replicated voices.
- `send_language_code`: `true` adds `language` to the request (untested; off by default).
- `style` and `modes`: sent byte for byte. A mode's style replaces the base style while it is on.
- `tags_allowed`: the inline tags a script may use; any other tag is a plan error.
- `wpm`: the preset's pace, a starting guess. The pace used for estimates and gate 2 is, in order: the median of this
  project's chunks (from 3), `calibration.json`, `wpm.measured_wps`, or `wpm.target` less a 10% pause share.
- `numbers`: `words` (spell numbers out) or `keep` (send digits; no digit warning).
- `lexicon`: a TSV file, relative to the profiles folder or absolute.
- `post.room_tone`: `pink` (seeded pink noise), `none`, or a file path (looped), set so that its RMS after the
  chain's high-pass is `room_tone_dbfs` (the loudness step then moves it with the voice). It lies under the whole
  track, so the noise floor never switches on and off. `post.deess` above 0 adds ffmpeg `deesser` at that intensity
  (0 to 1); it stays off unless you ask.
- `takes.hero`: the takes for `@takes` without a number. `max_auto_reroll`: 1, or 0 to switch the re-roll off.
- `precise`: one sentence per chunk (set by the ad and tutorial presets).

## Lexicon (TSV)

One `display<TAB>spoken` pair a line; `#` starts a comment. Whole words only. An all-capitals entry (an acronym)
matches only in capitals; other entries ignore case. The lexicon runs before `{display|spoken}` pairs and numbers,
and a pair written in the script wins over the lexicon.

```text
# display	spoken
NexaLance	Nexa-Lance
AI	এআই
SaaS	sass
```

## Script format

```text
@cast Rafi=bn-yt-m, Nadia=bn-yt-f     optional, top of file: speaker names to profiles (dialogue)
# Hook                                 a scene; the heading is not spoken; scenes get ids s1, s2 ... in order
@profile bn-yt-m                       who speaks from here on (overrides --profile)
@mode story                            a delivery mode from the profile's modes; @mode off goes back to the base style
@takes 3                               the next chunk gets 3 takes (hooks, calls to action, emotional peaks)
@pause 1.2                             exactly 1.2 s of silence here in the master
// a comment                           ignored
Rafi: So the launch is Thursday.       a dialogue line (needs @cast); each turn is its own chunk and request
{NexaLance|Nexa-Lance}                 captions show the left side, the voice says the right side
<short pause> <breath> <sigh> ...      3.8 inline tags pass through; for 3.1 and 2.5 they become [short pause] etc.
(blank line)                           a paragraph break
```

- Text before the first heading is scene `s1` (untitled).
- A line after a dialogue line, with no blank line between, continues that turn. After a blank line, text is
  narration again. A `Name:` line whose name is not in `@cast` is read as narration, with a warning.
- `@mode` stays on across scenes until `@mode off` or another `@mode`. `@takes` alone uses the profile's
  `takes.hero`; `@takes N` allows 1 to 5. `@pause` takes 0.05 to 30 s; pauses in a row add up; a pause before the first
  line becomes lead-in silence and one after the last line becomes silence at the end.
- Tags: `<name>` with a name from `tags_allowed`. Tags are removed from the captions.
- Unknown directives, `@cast` after the first spoken line, unknown modes and tags not allowed are plan errors.

## Text normalisation

For every sentence the plan keeps `display` (captions) and `spoken` (the voice), in this order:

1. Tags are set aside (spoken only).
2. `{display|spoken}` pairs, then the lexicon.
3. Bangla abbreviations `খ্রি.` and `হি.` are said in full.
4. Numbers, unless the profile says `keep`. A sentence with Bengali letters, and any Bengali digit, reads in Bangla;
   the rest reads in English.

English: integers to the trillions (`1,250,000` one million two hundred fifty thousand), decimals (`3.5` three point
five), percentages (`40%` forty percent), money (`$5` five dollars, `$4.99` four dollars ninety-nine cents, `$1.5
million` one point five million dollars; also £, € and ৳), ordinals (`21st` twenty-first), years (a bare 4-digit
number from 1100 to 2099: `1971` nineteen seventy-one, `2005` two thousand five, `2026` twenty twenty-six; write
`1,500` with a comma for a count), decades (`1990s`), en-dash ranges (`1990` to `2000`), times (`10:30` ten thirty,
`10:00` ten o'clock), negatives, and numbers with a leading zero digit by digit.

Bangla: the lakh and crore system (`১৫০০০০` এক লাখ পঞ্চাশ হাজার, `১২৫০০০০০০` বারো কোটি পঞ্চাশ লাখ, `২৫০` দুইশো
পঞ্চাশ), years before সাল or খ্রিস্টাব্দ from 1100 to 1999 (`১৯৭১ সালে` উনিশশো একাত্তর সালে; other numbers are
cardinal: `২০২৬ সালে` দুই হাজার ছাব্বিশ সালে), `%` as শতাংশ, `৳` or `Tk` as টাকা after the amount, decimals with
দশমিক, a suffix kept on (`৫টি` পাঁচটি), ordinals 1 to 10 (`২য়` দ্বিতীয়), times (`১০:৩০` দশটা ত্রিশ মিনিট).

Warnings (`plan` prints them, `render` and `say` refuse them unless `--force`): Latin words inside Bangla that are
not in the lexicon and not in a short list of words people say in English; web and e-mail addresses; the symbols
`& / # @ + =`; digits left over (`4K`, `MP3`); square brackets on 3.8 (read aloud); words that only work on a page
("see below", "this list", "নিচে দেখুন").

## Chunking

Scene, then paragraph, then sentence. Sentences end at `. ! ? । ॥ …` and at every line end, never on decimals,
abbreviations (Mr. Dr. e.g. i.e. etc. vs. and more), initials or web addresses. A chunk is 1 to 4 whole sentences of
one paragraph, speaker and mode, aimed at 12 to 35 s at the profile pace, never over `chunk.max_s`, `chunk.max_words`
or, in Bangla, 124 words and `chunk.max_chars_bn` characters. A sentence too long for one request is a plan error.
Fragments under 6 words ride with a neighbour; a line under 6 words that stands alone (its own paragraph, or a whole
dialogue turn) gets 2 takes and no style (an explicit `@mode` still applies). Narration chunks in one scene are kept
within 2x of each other where the paragraphs allow, otherwise the plan says so in a note; dialogue turns, `@takes`
lines and lone lines are short by design and do not count. The same words twice in a script share one cache key and
are paid for once. Precise mode (`--precise`,
or a profile with `precise`) gives 1 sentence per chunk. After each chunk the plan stores the gap: `sentence`,
`paragraph`, `scene`, `pause` (from `@pause`) or `end`. A gap is the silence from the last sound of one chunk to the
first sound of the next.

## Commands

### doctor

`doctor [--live] [--profiles DIR]`. Key sources (names only), ffmpeg and every filter the tool uses, the cache
(masters, size), designed voices that expire within 30 days. `--live` (a free call): the models the key's project
sees, and whether the five TTS models and `gemini-3.5-transcribe` are among them. JSON: `ready`, `keys`, `ffmpeg`,
`filters`, `cache`, `voices_expiring`, `live`. Exit 1 when not ready.

### voices, presets

`voices [--gender f|m] [--find WORD]`: name, gender and character of the 30 prebuilt voices.
`voices --library [--lang bn-BD] [--gender f|m] [--search WORD]`: `GET /v1beta/voices` with those filters, up to 10
pages of 100 (3.8 voices; a free call; the field names are untested). `presets`: the 15 presets.

### profile

`profile new NAME --preset ID [--voice V] [--style S] [--model M] [--lang L] [--mode NAME=STYLE]... [--lexicon FILE]`
never overwrites a profile. On 3.1 and 2.5, the Bangla presets add their accent line to the style unless `--style`
is given. `profile show NAME`, `profile list`.

### design

`design --desc TEXT [--gender male] [--lang bn-BD] [--takes 3] [--model M] [--name PREFIX] --out DIR [--budget USD]`:
one `POST /v1beta/voices` per take with
`{"store": true, "voice": {"model", "type": "prompted", "display_name", "gender", "language_code", "prompted": {"input"}}}`.
Each call gives a different voice, even with the same words. Saves each `sample_audio` as `design-N-ID.wav`, writes
`DIR/design.json` and adds every voice to `~/.nexa-speech/designs.jsonl`. The cost has no separate price in the
research: it is estimated as 10 s of audio a take. 3.8 models only. Untested against the real API.

`design keep VOICE_ID --profile NAME [--out DIR]` pins the voice (id, `expire_time`, sample) to the profile, sets
the profile's model to the design's model, and bumps the version.

### audition

`audition --voices A,B,C --text FILE --profile NAME --out DIR [--budget USD]`: the same text (15 s or less at the
profile pace) in each voice, with the profile's model, style and language, cost logged first. Each take is trimmed and
normalised to the profile's loudness: `audition-VOICE.wav`, all of them 1 s apart in `audition-all.wav`, and
`audition.json`. Takes are cached like chunks.

### plan

`plan SCRIPT [--profile NAME] [--out DIR] [--precise] [--profiles DIR]` (free). Writes `plan.json` to `--out`
(default: the script's folder); it never replaces a `plan.json` that nexa-speech did not write. Prints each chunk
(scene, speaker or profile, mode, words, seconds, takes), the totals, the cost (interactive, batch or flex for
reference, from 2027-01-01), errors, warnings and notes. Exit 1 on errors.

### render

`render SCRIPT [--profile NAME] --out DIR [--takes N] [--only c003,c007] [--budget USD] [--force] [--precise] [--asr]`

1. Plans the script (as `plan`) into `DIR/plan.json`; errors stop it, warnings stop it unless `--force`.
2. Finds every take already paid for (the cache or `DIR/masters/`), estimates the rest, and refuses when the estimate
   is over `--budget` (default 1.00 USD). A designed voice that has expired stops it when new takes need that voice.
3. Calls the API for the missing takes, three at a time: each master goes to the cache and to `DIR/masters/`, with a
   sidecar and a ledger line.
4. Runs the gates on every take, picks each chunk's best, and gives a failing chunk one automatic re-roll (within the
   budget). A chunk is then decided: later renders never re-roll it again by themselves.
5. Writes `takes.json`, `qa.json` and `calibration.json` and prints the table.

`--takes N`: at least N takes of each chunk (the best score wins). `--only`: these chunks only (new takes with
`--takes`). `--asr`: gate 4 on every take, inside the re-roll (paid, about $0.005 a minute). Stops at once on a
missing key, billing, auth, a daily or per-minute quota and a bad request; a refused line is reported and the rest go
on. Exit 1 when a chunk has no audio or the run stopped; finished chunks stay cached, so running it again pays only for
what is missing.

### pick

`pick DIR CHUNK TAKE`: chooses that take (it stays chosen until the chunk's text or voice changes). Run `master`
again.

### say

`say "TEXT" --profile NAME --out FILE.wav [--budget USD] [--force]`: the text as a one-paragraph script (directives
are ignored), rendered with the gates, mastered to the profile's loudness at 48 kHz, 24-bit. Writes `FILE.wav`, the
manifest as `FILE.json` (schema `nexa-speech/say-1`), and the ledger next to it. The work folder is
`~/.nexa-speech/say/<hash>/`. It replaces `FILE.wav` only when `FILE.json` shows that `say` made it.

### qa

`qa DIR [--asr] [--budget USD]`: runs the gates again on the chosen takes (with `--asr`, transcribes each chosen take
once; transcripts are cached) and writes `qa.json`. It never calls the TTS API; to act on a failure, `pick` or
`render --only`.

### master

`master DIR`: every chunk's chosen take is trimmed to 60 ms before its first sound and 150 ms after its last (a
click at the start and noise after the last word are cut), faded in (8 ms) and out (40 ms), gain-matched to the median
chunk loudness (at most 12 dB), stretched by the scene's tempo from `fit.json` if there is one, and placed at 24 kHz
so that each gap is exact. The room tone goes under the whole track. Then: `highpass` (70 Hz), `equalizer` (250 Hz,
-1.5 dB), `deesser` only when asked, `acompressor` (threshold -20 dB, ratio 2), two-pass `loudnorm` in linear mode to
the profile target, `aresample=48000:filter_size=64:phase_shift=10:cutoff=0.97`, `pcm_s24le`.

The loudness rule: pass 1 measures; when the gain would push the true peak over the target, `alimiter`
(`level=disabled`, `latency=1`) goes in first and pass 1 runs again with it; pass 2's report must say `linear`, else
the limiter ceiling goes down and it runs again; a loudness range above the target LRA is kept as it is (linear gain
only). The result is checked with `ebur128=peak=true`: integrated within 0.5 LU of the target and the true peak at or
under the target, or it runs again (8 tries at most, then an error: nothing is shipped in dynamic mode). The float
files in `DIR/work/` are removed afterwards.

### align

`align DIR [--engine auto|gemini|pauses] [--budget USD]`. `auto` uses `gemini` when a key exists, else `pauses`.

- `pauses` (free): sentence times from the manifest; words spread over each sentence's voiced time by the length of
  what is said (graphemes plus 2 a word), and moved to a pause (`silencedetect` at the target loudness less 20 dB,
  150 ms) within 150 ms.
- `gemini`: one `gemini-3.5-transcribe` call on a 16 kHz copy of `vo_48k.wav` with word timestamps; the recognised
  words are matched to the spoken words with `difflib.SequenceMatcher` on normalised tokens (lower case, punctuation
  stripped, Bengali digits folded, numbers spelled out), the display words carried over, and unmatched words placed
  between their matched neighbours in the same sentence.

Writes `words.json`, `sentences.json`, `vo.srt`, `vo.vtt` and `align.json`. Captions: one sentence at a time, split
into the fewest cues that fit, of even length, breaking after punctuation where it helps, never a one-word cue left
over; at most 2 lines of 42 graphemes (Bengali conjuncts count as one), 1 to 7 s a cue, held longer to stay under 20
characters a second where the next cue allows, at least 80 ms between cues, and no line starts with a danda.

### fit

`fit DIR --scenes scenes.json [--ad] [--apply]`. For each scene with a target: the sentence and paragraph gaps inside
it change first (180 to 900 ms, the profile's `gaps_ms.min` and `max`), then one `atempo` factor for the scene
(0.94 to 1.06, or 0.90 to 1.10 with `--ad`), with neighbouring scenes never more than 0.03 apart (a scene without a
target stays at 1.0); what is left is reported as seconds and words to cut or add. A scene's length runs from its
first word to the next scene's first word (to its last word for the last scene). `--apply` renames `vo_48k.wav`,
`vo.manifest.json` and the caption files to `NAME.before-fit-YYYYmmdd-HHMMSS.EXT`, writes `fit.json` and masters
again. `master` keeps applying `fit.json` while the script is unchanged; delete `fit.json` to master without it.

### cost

`cost [--minutes 10] [--model M]`: the estimate for that many minutes on each model (or one): interactive, batch or
flex (for reference), from 2027-01-01, with 1.4x takes, with word timings, and a likely bill at 1.5x.
`cost DIR`: the ledger's calls by model, their estimates, dollars from the `usage` the API reported where it gave
token counts, and requests per day (Pacific, when the daily quota resets).

## Gates (per take)

| Gate | Check | On failure |
|---|---|---|
| 1 | audio present; finish reason STOP or none and status completed or none (`OTHER`, `MAX_TOKENS` and the like count as truncated); no WAV inside the WAV | re-roll (a refusal: reported, no re-roll) |
| 2 | voiced seconds (between the first and last sound, less pauses of 150 ms or more) against words at the reference pace: 0.80 to 1.25 passes; skipped under 4 words | re-roll |
| 3 | lead-in under 20 ms; a click (the first 5 ms peak over 4x the next 50 ms); noise after the last word (the last 300 ms steady, above -50 dBFS, median spectral flatness 0.4 or more) | flag, fixed in `master` |
| 4 | `--asr` only: WER over 3% (English) or CER over 5% (Bangla); words missing or extra at the end; style or tag words heard that the script does not have; a lexicon term not heard | re-roll |
| 5 | from 5 chunks of the same profile with 3 s or more of voice: speaking rate beyond 12% of the median, loudness beyond 4 LU of the median (up to that it is only gain-matched), spectral centroid beyond 2 SD of the mean (the SD taken as at least 5% of the mean) | re-roll |
| 6 | clipping: peak at -0.1 dBFS or above, reached 3 times or more (astats peak count) | flag |

The best take has the lowest score: 1,000 for a gate 1 failure, 100 for each other failure, small amounts for flags
and for distance from the project norms. A take chosen with `pick` stays chosen.

## Project files

`plan.json` (schema `nexa-speech/plan-1`): the script, its hash, the profiles and lexicons as used, scenes, the lead
pause, chunks, errors, warnings, notes and totals. A chunk:

```json
{"id": "c003", "scene": "s1", "para": 2, "profile": "doc", "speaker": null, "mode": "story",
 "style": "calm and visual storytelling", "standalone": false, "hero": false, "takes": 1,
 "sentences": [{"display": "In 1971 the ferry cost $4.99.", "spoken": "In nineteen seventy-one the ferry cost four dollars ninety-nine cents.",
                "words": [{"w": "1971", "sp": "nineteen seventy-one"}, {"w": "$4.99.", "sp": "four dollars ninety-nine cents."}],
                "n_words": 11, "graphemes": 60, "line": 12}],
 "display": "...", "spoken": "...", "request_text": "...", "n_words": 38, "chars": 201, "est_s": 14.2, "tags": [],
 "lexicon_terms": [["NexaLance", "Nexa-Lance"]], "model": "gemini-3.8-flash-tts", "family": "speech_metadata",
 "voice": "Charon", "voice_type": "prebuilt", "voice_key": "Charon", "language": "en-US",
 "send_language_code": false, "base_key": "adcf958aef6a49e3", "gap_after": {"kind": "paragraph", "s": 0.75}}
```

`takes.json` (`nexa-speech/takes-1`): per chunk (keyed by `base_key`, the cache key without the take): the takes,
the chosen one and why, the gate results and measures, `auto_reroll` and `decided`.

```json
{"id": "c006", "chosen": 2, "chosen_by": "best of 2 takes", "result": "pass", "fails": [], "flags": [],
 "gates": {"1": "pass", "2": "pass", "3": "pass", "4": "skip (run with --asr)", "5": "pass", "6": "pass"},
 "measures": {"ratio": 1.0, "rate_dev": 0.0, "loudness_dev": 0.0, "centroid_z": 0.002, "wps_ref": 2.654,
              "wps_source": "this project (median of 11 chunks)"},
 "auto_reroll": true, "decided": true,
 "takes": {"1": {"take": 1, "key": "5d1acfffb63d2eac", "finish": "OTHER", "finish_class": "truncated",
                 "riff": false, "source": "api", "usage": {"...": 0}, "key_source": "GEMINI_API_KEY",
                 "file": "masters/5d1acfffb63d2eac.wav"}, "2": {"...": "..."}}}
```

`masters/KEY.wav`: the paid audio as it came (24 kHz, 16-bit mono), a hard link to (or copy of)
`~/.nexa-speech/cache/KEY.wav`. Its sidecar `KEY.json`, kept in both places, holds the model, voice, style, family,
the exact text, the take, the request body, the finish reason, `usage`, the key source name and the estimate. `KEY` is
the first 16 hex of the SHA-256 of the canonical JSON of `{engine, endpoint, model, voice, language, style,
prompt_family, text, format: "audio/l16@24000", take}`. A project moved to another machine refills that machine's
cache from its `masters/` and pays for nothing again. Transcripts are cached as `KEY.asr.json`. Nothing in the cache
is ever deleted by the tool.

`analysis/KEY.json`: what the gates measured on one take (derived; rebuilt when the analysis version changes).

`qa.json` (`nexa-speech/qa-1`): `references` (per profile: the pace and its source, the drift medians), a note that
speaker similarity is not measured, a row per chunk (take, result, fails, flags, gates, measures, words, voiced
seconds, loudness, centroid, the transcript with `--asr`) and a summary.

`calibration.json`: `{"schema": "nexa-speech/calibration-1", "profiles": {"doc": {"measured_wps": 2.654, "chunks": 11,
"updated": "..."}}}`, the median words per voiced second of the accepted chunks, once there are 3.

`ledger.jsonl`: one line per call (paid or refused):

```json
{"time": "2026-09-25T07:21:39Z", "command": "render", "project": "/path/to/DIR", "chunk": "c001", "take": 1,
 "master_key": "0c8cc6e95399761d", "model": "gemini-3.8-flash-tts", "voice": "Charon",
 "units": {"audio_s_est": 4.94, "audio_tokens_est": 124, "text_tokens_est": 37}, "est_usd": 0.00113,
 "key_source": "GEMINI_API_KEY", "usage": {"total_input_tokens": 20, "total_output_tokens": 131},
 "status": "completed", "finish": "STOP", "result": "ok", "attempts": 1, "seconds": 0.05}
```

(A line from a test run against the fake server, so `seconds` is tiny; `result` is `ok`, `truncated`, `blocked`,
`empty`, `failed` or `error:KIND`, and a refused call is logged with `est_usd` 0.)

`vo.manifest.json` (`nexa-speech/manifest-1`), read by nexa-video-creator; every time is in seconds in
`vo_48k.wav`, rounded to milliseconds; a chunk's `start` and `end` are its first and last sound, and the next chunk
starts exactly `gap_after.s` after the end:

```json
{"schema": "nexa-speech/manifest-1", "skill_version": "2026.09.25.1", "created": "...", "file": "vo_48k.wav",
 "sample_rate": 48000, "duration_s": 212.808,
 "loudness": {"I": -16.0, "TP": -4.0, "LRA": 1.2, "normalization": "linear", "target": {"stem_I": -16.0, "TP": -1.5, "LRA": 11.0},
              "limiter_db": null, "passes": 1},
 "post": {"chain": "highpass=f=70,...", "room_tone": {"room_tone": "pink", "room_tone_dbfs": -65.0}, "trim": {"...": 0}},
 "profiles": {"doc": {"model": "gemini-3.8-flash-tts", "voice": "Charon", "voice_type": "prebuilt",
                      "style": "calm documentary narration, measured and grounded", "version": 1, "language": "en-US"}},
 "main_profile": "doc", "script": "/path/script.md", "script_sha": "1b36c4b234d52560",
 "scenes": [{"id": "s2", "title": "Middle", "start": 65.295, "end": 121.936}],
 "chunks": [{"id": "c003", "scene": "s1", "profile": "doc", "speaker": null, "mode": null, "display": "...", "spoken": "...",
             "start": 25.17, "end": 43.885, "master": "masters/adcf958aef6a49e3.wav", "take": 1,
             "gap_after": {"kind": "paragraph", "s": 0.75}, "gain_db": 0.0, "tempo": 1.0}],
 "sentences": [{"scene": "s1", "chunk": "c002", "text": "By noon the river is loud and busy, ...", "start": 18.647, "end": 24.728}],
 "fit": null, "qa": {"flagged": []}, "cost": {"est_usd": 0.08584, "calls": 32, "ledger": "ledger.jsonl", "prices_as_of": "2026-09-25"},
 "versions": {"skill": "2026.09.25.1", "ffmpeg": "8.1.1"}}
```

`words.json`: `[{"w": "and", "start": 2.032, "end": 2.372, "sentence": 0, "chunk": "c001", "scene": "s1"}]`; `w` is
the display word (`1971`, `$4.99`), punctuation attached.
`sentences.json`: `[{"index": 1, "scene": "s1", "chunk": "c002", "text": "...", "start": 5.705, "end": 11.357}]`.

`vo.srt` and `vo.vtt`:

```text
1
00:00:00,060 --> 00:00:04,955
Every place has a voice,
and today we listen to ten of them.
```

`align.json`: the engine, its numbers (for `gemini`: recognised words, matched share, the estimate) and the caption
rules used.

`scenes.json` (input to `fit`): `[{"scene": "s1", "target_s": 12.0}, {"scene": "s2", "target_s": 8.5}]`.
`fit.json`: `{"schema": "nexa-speech/fit-1", "script_sha": "...", "targets": {...}, "ad": false, "tempo": {"s4": 1.03},
"gaps": {"c012": 0.18}, "plan": {...}}`.

`design.json`: the model, description, gender, language and each voice (`id`, `expire_time`, `sample`).
`audition.json`: the text, the estimate, and per voice the file, master key, duration and loudness.

## Requests (exact, from the Gemini docs of 2026-09-24; untested against the real API)

3.8 (`speech_metadata`), `POST /v1beta/interactions`:

```json
{"model": "gemini-3.8-flash-tts", "store": false,
 "input": [{"type": "text", "text": "SPOKEN TEXT <short pause> MORE",
            "annotations": [{"type": "speech_metadata", "style": "STYLE"}]}],
 "response_format": {"type": "audio", "mime_type": "audio/l16", "sample_rate": 24000},
 "generation_config": {"speech_config": [{"voice": "Charon"}]}}
```

No `annotations` when the style is empty; `"language"` in the `speech_config` item only with `send_language_code`.

3.1 and 2.5 (`director_text`): `input` is one string, `response_format` is `{"type": "audio"}` (the answer is
headerless 16-bit PCM; a RIFF answer is written as it came, never wrapped twice):

```text
Synthesize speech for the performance defined below. Speak ONLY the lines under #### TRANSCRIPT.
### PERFORMANCE
STYLE
#### TRANSCRIPT
SPOKEN TEXT [short pause] MORE
```

## Errors

| Kind (from `gemini_api`) | What happens |
|---|---|
| `no_key` | prints how to set a key (environment or keychain); nothing else runs |
| `billing` | the key's project needs billing turned on |
| `auth` | the key was refused; the next key is tried, if there is one |
| `quota_day` | stops: wait until midnight Pacific, or use another model for the whole project |
| `quota_minute` | already waited on inside `gemini_api` (the server's delay, else 15, 30, 60 s); stops: try again in a minute |
| `safety` | that line is reported (rephrase or shorten it, or try the other voice once); the other chunks go on |
| `bad_request` | stops and shows the message |
| `server`, `network` | waited on inside `gemini_api`, then reported |
| `timeout` | never retried (the call may still be billed); run again later |
