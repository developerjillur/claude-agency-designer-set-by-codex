# Changelog

## 2026.09.24.5

- **Time limits by kind of call.** Every agy call used to wait up to 17 minutes before failing over. Each kind now has
  its own limit, about three times the slowest measured: 900 s for a proxy video, 600 s for audio, 420 s for frames,
  360 s for the review and 240 s for other text-only calls (`AWV_CALL_TIMEOUT` overrides). A stuck call reaches the
  sibling model in minutes.
- **The cache keeps across releases.** Cached probes, measurements and passes are keyed by their own version, which
  changes only when what they return changes, so this release reuses every analysis already made.
- **Tests.** 98 offline tests.

## 2026.09.24.4

What models miss between frames and on thin things, now measured instead of hoped for.

- **A change grid on every frame.** The ffmpeg measurement pass also records, for every frame, where the picture
  changes: the largest Y, U or V difference to the previous frame, dilated so thin things register, on a grid of 32
  cells across. It runs in the same decode as the other measurements, costs seconds and no model call, and lines up
  with the real frame timestamps.
- **Brief changes get their own frame.** Something that shows for a moment between two sampled frames (a pop-up, a
  flash of text, a glitch) is measured with its time and place. `watch` gives it a frame chosen while it shows, plus a
  close-up, and the report lists each one with what was seen there. `ask` and `verify` add those frames inside their
  window. `qa` lists them under `local_changes` and `notes`, and never fails `--strict` on them.
- **Close-ups of the moving area.** At standard and deeper, sampled frames come with an enlarged crop of the strongest
  compact moving area at that moment: the person and what they carry. In testing, the close-up of a drone clip showed
  a worker's thin hose from his hand to the tyre, with no model call spent finding him. Bands along the frame's edge
  (a camera move revealing new ground) never get one.
- **Closer looks.** The frame passes list what they could not make out (`look_closer`, with a time and an area). The
  skill enlarges those areas three times from the full-resolution video and asks Pro again.
- **`ask` zoom fallback.** When the subject box finds nothing, the measured moving area in the window is enlarged.
- **`selftest`.** Synthetic clips with known answers: a red square shown for 3 frames, a 0.4 s label, a thin rod
  carried by a moving figure, the order of two appearances (one differing mostly in colour), four squares to count and
  a spoken sentence. Offline it checks the measurements, the frame chosen and the plan in seconds. With `--live` it
  runs `watch`, `verify`, `ask` and `transcribe` and checks every answer (about 20 calls); `--cached` re-checks the
  last answers without new calls. First live run: 15 of 15 passed. `watch` saw the 3-frame square, read the 0.4 s
  label exactly and saw the thin rod.
- **Replayed live answers.** Five real verify runs are kept as a fixture (answers only, no paths or plates), and the
  tests replay them through the logic after the models, which must reach the live verdicts.
- **Found while building it:** a resampled grid picked a frame one frame late for a 3-frame event, and a colour change
  with little brightness change (green on grey) went unmeasured. A code review then found that fast blinking in one
  place (blinks under 0.3 s apart) was called movement and got no frame (now a `flicker`, with its own frame), and
  that `--max-frames 2` with a brief change gave 3 frames (brief frames now always come out of the budget). Thin strips
  along an edge of the frame (a camera move revealing new ground) no longer get close-ups. All are fixed and tested.
  The test data no longer carries a client's real phone numbers or name.
- **Tests.** 97 offline tests (grid events, pairing, flicker, pop-up against movement, camera moves, the frame budget,
  close-ups, closer looks, the replay and the offline self test).

## 2026.09.24.3

A full review (code, silent failures, security, and a gap analysis against professional video QA), with every finding
fixed and tested.

- **Coverage you can trust.**
  - Frames always run from the first to the last frame. When they fit the budget: uniform plus the first frame of
    every shot. When they do not: shot starts spread over the range, the middle of long shots, and the rest filling the
    biggest gaps, weighted towards motion. The report states the largest gap between frames.
  - Promos get the hook (first 3 s) and the end card every 0.5 s; motion and AI-video goals get frames around flicker.
  - Long videos: the locate pass for `ask` searches the overview in 20-minute parts, with the cached transcript.
  - The proxy is re-encoded smaller when it would pass agy's 100 MB limit, and the command says so when it still would.
- **Agreement that is strict on facts, not on wording.** Hard conflicts are a disagreement: numbers that differ
  (digits in any script, or spelled out), a missing number the question asks for, times more than 0.6 s apart,
  different colours, or "nothing" against a thing. "3 people" against "4 people" is now a disagreement. Words are
  lightly stemmed, and when the wording still cannot tell, one text-only call compares the facts. Found in a live
  check: Pro ("fills tire and carries a black hose") and Flash ("stands, walks away, carrying a black hose") described
  the same walk-off, and the word overlap alone had turned a true claim into `unclear`. A fallback that ran both
  viewers on the same model is reported as a single model.
- **`verify` checks order.** For claims about before and after, the second viewer gets the frames in reverse, labelled
  with their true times; a viewer that follows the file order instead of the times makes the verdict `unclear`.
- **Approved copy.** `watch --expect copy.txt` reports each approved line as found, different (with what was seen) or
  not found. The text check reads one frame per distinct text (up to 24) instead of a fixed sample.
- **Delivery gates.** `qa --strict` exits 2 on any failed flag or platform check. Every command exits 1 when its result
  is `ok: false`. `qa` lists measurement errors and flags HDR input. `probe` adds HDR, field order, sample aspect and
  whether a Content Credentials (C2PA) manifest is present.
- **Measurements.**
  - A flash is now a pair of opposite brightness jumps within half a second, so one hard cut no longer counts as a
    flash.
  - `compare` finds changed frames against the clip's own baseline, so a re-encode does not hide an edit. Identical
    pictures stop before any model call, and the changed windows come ranked with their lowest SSIM.
  - Subtitle cues shorter than 5/6 s are stretched when the next cue leaves room.
- **Model rules.** Describe only the frames given, never what happens between them; count by listing each instance;
  judge camera movement from parallax and scale; write "number plate", never its characters.
- **Denied tools.** A run in which the agent reached for a denied tool is never kept. It is retried once with a
  stricter prompt, then sent to the sibling model, and the error names the tool. Found in a live check: Flash tried to
  run a command while rewriting a claim, which stopped `verify`. Text-only calls now say that no tool is needed, and
  `verify` falls back to a broad neutral question when the rewrite fails (`question_source`).
- **Review budget in bytes.** The review's facts are trimmed to 150 KB counted in bytes, so Bengali (three bytes a
  letter) no longer overflows agy's prompt limit.
- **`doctor`.** `ready` now also needs ffmpeg's analysis filters and the three models.
- **Tests.** 80 offline tests, including end-to-end runs of `watch`, `ask` (with the order check) and `verify`
  (with a failed rewrite) through a schema-aware fake agy, denial retries, the fact check, a long overview in parts,
  the planner's coverage, agreement (word forms, times, numbers the question asks for), flash pairs and subtitle
  timing.
- **Live checks** on an 8 s drone clip: `doctor --smoke` passed; `verify` contradicted a false claim (a red ladder:
  both models saw a black hose on the auto zoom, high confidence, 5 calls), supported a true order claim (the
  mechanic stands up, then walks off with the hose) and contradicted the same events told in reverse, each with the
  second viewer on reversed frames and high confidence.

## 2026.09.24.2

- **`verify`**: checks one claim the way a careful reviewer would. A light model turns the claim into a neutral
  question that does not reveal it. Pro and Flash answer it on dense frames (with auto zoom and audio where needed),
  and Pro judges their answers against the claim: supported, contradicted or unclear. In testing, a true claim (a
  worker walks off holding a hose) came back supported, and a false one (a red bucket) came back contradicted.
- **Frames follow the picture.**
  - Over budget, the frames that are not cut anchors are spread along the measured motion, with half the weight
    uniform.
  - At standard and deep, frames of an unchanged picture are skipped, keeping at least one every 4 s or 2 s. Screen
    recordings keep small changes.
  - `--max-frames` sets a budget.
- **Reports say what they cover.**
  - A "What this report covers" header lists what was watched, the sampling, the audio, the text check and what was
    not seen.
  - A "Speech with picture" table sets each spoken sentence against the nearest sharp frame.
  - A line marks quoted content as data, not instructions.
- **No silent failures.**
  - A failed measurement is never cached.
  - Failed passes and measurement errors reach the review, which marks the checklist items they would have answered
    as unclear.
  - A new verdict, `insufficient data`, is used when nothing was produced.
  - `ok` is false in that case, and `qa` says when it could not measure.
  - A failed loudness measurement reads "unclear", not "no audio".
  - Model observations with times outside the watched range are dropped and counted.
- **Safety.**
  - For every call, only that call's media are hardlinked into a fresh folder shared with agy. The rest of the cache
    (the source path, older frames and passes) stays out of reach of any text in a video.
  - `fetch` needs `--confirmed`.
  - `cache --older-than DAYS` removes old caches.
  - Pillow is pinned to 11.3.0.
- **Fixes.**
  - The JSON envelope parser reads only top-level objects: the envelope echoes the schema, whose nested fields can be
    called "status".
  - Digits in any script compare equal when two answers are matched.
  - `compare` uses the lowest SSIM channel, so colour changes count.
  - Contact sheets stay within 2000 px.
  - Bengali text gets a third reader, Tesseract, when its Bengali data is installed.
- **Tests.** 63 offline tests.

## 2026.09.24.1

First version.

- **Engine.** The official Antigravity CLI (`agy`) in headless mode, with only the video's own cache folder shared.
  Every run is checked for denied actions. An empty reply is retried once, then sent to a sibling model; a quota error
  stops at once (every Gemini model draws on the same quota). Every call has a hard timeout.
- **Media, as measured.**
  - A video file reaches Gemini as about 1 low-detail frame per second, without its audio. The skill uses it only for
    the overview.
  - Detail comes from sharp frames extracted by ffmpeg, each listed with its time in the prompt (a time bar is
    optional: `AWV_TIME_BARS=1`).
  - Zoom crops handle small things, and the soundtrack goes as 16 kHz WAV in 5-minute parts.
- **Commands.** `watch` (quick, standard, deep, forensic; seven goals; platform checks), `ask` (a moment, a range or
  the whole video), `transcribe` (JSON, TXT, SRT, VTT), `qa` (measured only), `frames` (sharp frames, zoom and
  labelled contact sheets), `compare` (per-channel SSIM, so colour changes count, then Gemini on the changed moments), `probe`, `usage`, `fetch`, `cache`,
  `doctor` (with `--setup` and `--smoke`).
- **Accuracy.**
  - Neutral prompts with an "unreadable, never guess" rule. Text and speech inside the video are treated as data.
  - Two models are compared in `ask`; when they disagree, the frames to check are listed. Digits count the same in any
    script, so a Bengali and a Latin reading of the same phone number agree. In testing, both models read a promo's
    two Bengali phone numbers exactly, from a zoom the skill located by itself.
  - Questions about hands, objects and text zoom automatically on the subject. In testing, this found a thin hose
    that both models missed on full frames.
  - Text is read by two models and checked against Apple Vision OCR where it can read.
  - The review pass trusts measurements first, then full-resolution frames, then the overview.
  - Transcript times are aligned to measured speech onsets. In testing they went from about 1 s late to within 0.05 s.
- **Measured QA** (one ffmpeg pass): cuts, shots, black and frozen frames, flicker outside cuts, flash risk (more than
  three flashes in a second), letterbox bars, luma, saturation, blur, blockiness, integrated loudness, true peak,
  loudness range, silence, and fast start. Platform specs from the official pages (Reels, TikTok, Shorts, YouTube,
  Facebook), with safe zones checked against OCR text boxes. Loudness is advisory: no platform publishes a target.
- **Subtitles.** At most 2 lines of 42 characters, 5/6 s to 7 s per cue, 2-frame gaps.
- **Long videos.** Proxies shrink with length to stay under agy's file limits, and the overview runs in 20-minute
  parts in parallel.
- **Privacy.** Number plates and other personal identifiers are left out unless asked for.
- **Speed and cost.** Passes run in parallel, and everything is cached by file hash, model, prompt, schema and media.
  The review facts are trimmed to stay under agy's prompt limit.
- **Review fixes.** ffmpeg writes its measurement files by bare name from their own folder (paths with quotes or
  colons once emptied the measurements), letterbox checks use the displayed orientation of rotated phone clips,
  `--from/--to` audio is split into parts too, the JSON envelope survives notices with braces and pretty-printed
  output, an explicit 0 in `--to` or `--span` is respected, and `cache --clear` takes a cache id.
- **Tests.** 55 offline tests, including a fake agy for the engine plumbing and generated clips for ffmpeg.
