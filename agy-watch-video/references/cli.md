# watch_video.py reference

`python3 ~/.claude/skills/agy-watch-video/scripts/watch_video.py <command> ...`

Every command prints one JSON object on stdout. Progress goes to stderr. Exit code 0 means success; a result with
`"ok": false` (an error, or nothing produced) exits 1, `qa --strict` exits 2 on a failed check, and an interruption
exits 130. Times accept seconds (`12.5`, `12.5s`)
or clock form (`0:12.5`, `1:02:03`). A path can be any video or audio file ffmpeg reads; URLs go through `fetch`.

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `AGY_WATCH_CACHE` | `~/.cache/agy-watch-video` | the cache |
| `AWV_MODEL_FAST` | `gemini-3.8-flash-high` | overview, audio, second opinions |
| `AWV_MODEL_LIGHT` | `gemini-3.8-flash-medium` | quick overview, subject boxes, smoke test |
| `AWV_MODEL_DEEP` | `gemini-3.1-pro-high` | frame batches, text reading, review, careful answers |
| `AWV_TIME_BARS` | off | `1` writes each frame's time in a bar above the frames sent to Gemini (the research favours plain text times, which the prompts always give) |
| `AGY_BIN`, `FFMPEG`, `FFPROBE` | found on PATH (`~/.local/bin/agy` for agy) | tool paths |

## Cache layout

`<cache>/v/<first 16 hex of the file's SHA-256>/`:
`source.json`, `probe.json`, `measure.json` (+ `measure/frames.meta`), `media/` (proxy video, WAV and audio parts),
`frames/` (clean sharp frames `f_<ms>.jpg`), `frames_g/` (with a time bar, only with `AWV_TIME_BARS=1`), `zoom/`,
`sheets/`, `passes/` (every Gemini result, keyed by model, prompt, schema and media), `reports/`, `onsets-*.json`.
`<cache>/stage/` holds, for the length of one call, hardlinks to that call's media: the only folder agy may read.
A file is recognised again by path, size and modification time (`index.json`), then by content hash.

## doctor

`doctor [--setup] [--smoke] [--quota]`

Checks ffmpeg (and the filters scdet, blackdetect, freezedetect, signalstats, blurdetect, blockdetect, silencedetect,
ebur128, astats, ssim, tile, volumedetect), ffprobe, agy, sign-in (via `agy models`), the three models, OCR (Apple
Vision helper compiled from `scripts/ocr.swift` with swiftc), Pillow for time labels, and yt-dlp.
- `--setup` creates the skill's `.venv` and installs Pillow (pinned to 11.3.0).
- `--smoke` makes a 4 s test clip (test pattern plus the spoken words "Seven blue boxes" on macOS) and runs one real
  call that must describe the picture and hear the words: `smoke: {ok, heard, image, seconds}`.
- `--quota` adds the agy quota.
Output: `ready` (bool) and one field per check. Exit 1 when not ready.

## watch

`watch VIDEO [--goal G] [--depth D] [--focus TEXT] [--lang CODE] [--from T] [--to T] [--platform P] [--no-audio]
[--parallel N] [--out DIR] [--fresh] [--dry-run]`

| Flag | Meaning |
|---|---|
| `--goal` | `general` (default), `promo`, `ai-video`, `motion`, `screen`, `footage`, `tutorial`: sets what each pass looks for and the review checklist |
| `--depth` | `quick` (overview and audio), `standard` (default: plus 1 sharp frame a second, at most 36, and a review), `deep` (2 a second, at most 96, plus a text check by two models), `forensic` (4 a second, at most 192, every batch also read by the second model) |
| `--focus` | what the user wants to know; added to every prompt |
| `--lang` | speech language hint (`bn` writes Bengali in Bengali script) |
| `--from`, `--to` | watch only this part; times in the report stay absolute |
| `--platform` | `reels`, `tiktok`, `shorts`, `youtube`, `facebook`, `generic`: adds the spec and safe-zone checks |
| `--no-audio` | skip the audio pass |
| `--parallel` | frame batches in flight at once (1 to 8, default 4) |
| `--max-frames` | at most this many sharp frames: a budget below the depth's cap |
| `--expect` | a text file of approved on-screen lines (one per line); each is reported `found`, `different` (with what was seen) or `not found`; runs the text check at any depth |
| `--out` | where the report goes (default `<cache>/v/<id>/reports/`) |
| `--fresh` | ignore every cached pass |
| `--dry-run` | print the plan (frames, batches, models, estimated calls) and stop |

Passes: measurements (ffmpeg) → in parallel the overview (proxy video; 20-minute parts for long videos), audio (WAV
parts) and frame batches (12 sharp frames per call, each listed with its time) → the second-model cross-check
(forensic) → the text check (deep, forensic, or with `--expect`) → the review (Pro, facts only, trimmed to 150 KB in
bytes, with the failed passes listed so it marks what they would have answered as unclear).

The text check reads one frame per distinct text on screen (Apple Vision boxes find where the text changes; up to 24
frames), by two models, and checks each reading against Apple Vision (Latin, CJK, Cyrillic and more) or Tesseract's
Bengali data when installed. A reading counts as `verified` only when a second reader agrees.

Sampling always covers the whole range, the first and the last frame included. When the frames fit the depth's cap:
uniform plus the first frame of every shot. Otherwise: the first frames of shots spread over the range (40% of the
budget), the middle of long shots (10%), the goal's extras, and the rest filling the biggest gaps, weighted towards
motion. Promos add the first 3 s and the last 3 s every 0.5 s; motion and ai-video add frames around flicker. At
standard and deep, frames of an unchanged picture are skipped (at least one every 4 s or 2 s is kept; screen recordings
keep smaller changes). `plan.largest_gap_s` and the coverage header give the biggest gap. Model observations with times
outside the watched range are dropped and counted.

Output: `report_md`, `report_json`, `verdict` (`ready`, `fix first`, `not usable`, `insufficient data`; none for
quick), `summary`,
`contact_sheet`, `cost` (`calls`, `cached`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `model_seconds`),
`wall_seconds`, `errors` (failed passes; the rest still count).

`report_json` holds `coverage` (what was watched, how, and what was not seen), `probe`, `measure`, `plan`, `overview`, `audio` (with `transcript` items `start`, `start_model`,
`end`, `speaker`, `text`, and `time_shifts`), `detail_frames` (per frame: `t`, `what`, `people`, `objects`, `text`,
`change`, `frame`), `detail_people`, `cross_check`, `text` (`items`: `t`, `text`, `text_alt`, `ocr`, `unreadable`,
`verified`, `how`), `platform`, `review` (`summary`, `timeline`, `people`, `goal_review`, `issues`, `conflicts`,
`verdict`, `top_fixes`, `uncertain`), `evidence`, `calls`, `cost`, `errors`.

## ask

`ask VIDEO "QUESTION" [--at T [--span S]] [--from T --to T] [--region R] [--no-zoom] [--fps F] [--audio] [--quick]
[--model M] [--max-windows N] [--fresh]`

- The window: `--at` looks at `--span` seconds around a moment (default 2); `--from/--to` a range; with neither, a
  clip of 12 s or less is taken whole, and a longer one is searched by a locate pass (Flash on the proxy, plus the
  cached transcript), which returns up to `--max-windows` ranges (default 2). Once a window is answered with both
  models agreeing, the later windows are skipped unless `--all-windows`.
- Frames: 8 a second for windows up to 1.5 s, 4 up to 4 s, 2 up to 10 s, then 16 across the window; 2 to 24 frames.
- Zoom: `--region auto`, a word (`left`, `right`, `top`, `bottom`, `center`, `top-left`, `top-right`, `bottom-left`,
  `bottom-right`, `upper-third`, `middle-third`, `lower-third`) or `x,y,w,h` in pixels or fractions. Questions about
  hands, objects, text, numbers, logos and screens zoom automatically unless `--no-zoom`: a quick model boxes the
  subject in three frames, and the union of the boxes plus a margin is enlarged up to 2x.
- Audio: added for questions about speech or sound, or with `--audio`.
- Models: Pro and Flash in parallel, compared (`--quick` for one; `--model` sets the first).

Agreement, in three steps:
1. Hard conflicts mean `disagree`: one answer finds the thing and the other does not; both give numbers that differ (in
   any script, or spelled out); only one gives the number a how-many, phone, price or code question asks for; both
   give times more than 0.6 s apart; both name colours that differ; or one says nothing is there ("holding nothing",
   "unreadable"; "a hose, nothing else" is not a nothing answer).
2. `agree` when the shorter answer's words, lightly stemmed (carries = carrying), mostly appear in the longer one.
3. Otherwise a light model compares the two answers' facts in one text-only call (different wording or detail is
   fine, a conflicting fact is not); if that call fails, the result is `disagree`.

`agreement_how` says which step decided. When both runs ended up on the same model (a fallback), the result says so.

Output: `answers[]`, one per window, each with `answer`, `short_answer`, `found`, `moments[]` (`t`, `what`, `file`,
`frame`), `confidence`, `unclear`, `agreement` (`agree`, `disagree`, `single model`), `second_opinion`,
`check_frames` (when the models disagree), `window`, `model`, `frames`, `zoom`, `zoom_region`, `audio_included`.
Also `locate` (the ranges found) and `cost`.

## verify

`verify VIDEO "CLAIM" [--question Q] [--at T [--span S]] [--from T --to T] [--region R] [--no-zoom] [--fps F] [--audio]
[--fresh]`

1. A light model rewrites the claim as an open, neutral question that does not reveal it ("the mechanic walks off
   with a hose" becomes "What, if anything, is the mechanic holding?"). `--question` sets it yourself.
2. The same window inspection as `ask`: dense sharp frames, auto zoom, audio when it matters, Pro and Flash compared.
3. Pro judges the two answers against the claim. It returns `unclear` whenever the viewers disagree or could not see it.

For claims about order (before, after, first, then, enters, leaves and the like) the second viewer gets the frames in
reverse order, labelled with their true times: a viewer that reads the order from the file list instead of the times
disagrees, and the verdict becomes `unclear` (`order_check` says it ran).

When the rewrite fails, a broad question that still hides the claim is used instead (what happens, in order, for order
claims), without a zoom on a guessed subject.

Output: `claim`, `neutral_question`, `question_source` (`model`, `given`, or `generic` with the reason), `verdict`
(`supported`, `contradicted`, `unclear`), `reason`, `agreement_how`, `confidence`,
`window`, `agreement`, `answers` (what each model saw, with times), `check_frames`, `zoom_region`, `cost`. Calls: 1
neutral question, 1 subject box when zooming, 2 viewers, 1 judge, and 1 fact check only when the viewers' wording
cannot settle their agreement.

## transcribe

`transcribe VIDEO_OR_AUDIO [--lang CODE] [--model M] [--out DIR] [--fresh]`

The soundtrack as 16 kHz mono WAV, cut into parts of about 5 minutes at pauses, transcribed in parallel. Each part's
sentence starts are aligned to measured speech onsets: a global shift first, then each sentence to the nearest later
onset within 0.8 s. Writes `transcript-*.json`, `.txt`, `.srt` and `.vtt`; subtitle cues have at most 2 lines of 42
characters and last 5/6 s to 7 s (a short cue is stretched to 5/6 s when the next one leaves room). Output: `language`, `segments`, the four
paths, `preview` (the first 12 lines) and `cost`.

## frames

`frames VIDEO [--fps F | --at T1,T2 | --scenes] [--from T] [--to T] [--zoom R] [--sheet] [--cols N] [--max N]
[--out DIR]`

Sharp JPEG frames at exact times, full resolution up to 1920 px, with optional zoom crops and a labelled contact sheet
(times on each cell; plain grid without Pillow). `--scenes` takes one frame per shot from the measured cuts. `--out`
copies the files. Output: `frames[]` and `zoom[]` (`t`, `path`), `sheet`.

## qa

`qa VIDEO [--platform P] [--strict] [--fresh]`

No model. Output: `probe`, `measure` (`video`: cuts, shots, average shot length, black, freeze, flicker events,
flash risk (more than 3 flashes in a second), letterbox bars, luma, saturation, blur, blockiness; `audio`: integrated loudness, true peak, loudness range, peak, RMS, flat factor, silence,
silent share), `platform` (checks for aspect, resolution, frame rate, duration, loudness, true peak, codec, fast start,
and text inside the safe zones from Apple Vision text boxes on 8 frames), `measurement_errors`, and `flags`
(plain-language problems, including HDR input). A flash is a pair of opposite brightness jumps within half a second;
more than three in a second is flagged. `ok` is false when nothing could be measured. `--strict` exits 2 when any flag
or platform check fails.

## compare

`compare A B [--threshold 0.95] [--fresh]`

SSIM at 4 frames a second over the shared duration, per channel (the lowest of Y, U and V, so colour changes count).
A frame changed when it falls below the clip's own baseline (the median less 4 median absolute deviations, at least
0.005) or below the threshold; when most of the clip is below the threshold (a heavier re-encode), only the baseline
counts. Identical pictures stop early with `identical: true` and no model call. Otherwise frames of both, at up to 12
of the most changed moments (or 5 even ones when nothing changed), go to Pro in pairs. Output: `identical`,
`ssim_mean`, `changed_windows` (`start`, `end`, `lowest_ssim`, most changed first), `compared_times`, `result`
(`summary`, `differences[]` with `t`, `a`, `b`, `kind`; `same`; `uncertain`), `cost`.

## probe, usage, fetch, cache

- `probe VIDEO [--fresh]`: duration, container, size, bit rate, video (codec, size after rotation, fps, VFR suspicion,
  pixel format, colour, `hdr`, field order, sample aspect), audio (codec, rate, channels), `faststart` for MP4, and
  `c2pa` (whether a Content Credentials manifest is present, when `c2patool` is installed; the skill never strips one).
- `usage`: `limits[]` with `group`, `limit`, `remaining_pct`, `resets`.
- `fetch URL --confirmed`: downloads with yt-dlp (at most 1080p, MP4) into `<cache>/downloads/`. Without
  `--confirmed` it refuses: ask the user first.
- `cache [--clear VIDEO|ID] [--older-than DAYS]`: lists the cached videos, their ids and sizes; deletes one video's
  cache folder by path or by the 16-character id (useful when the source file is gone); or deletes every video cache
  not used for DAYS days. It never touches anything outside the cache.
