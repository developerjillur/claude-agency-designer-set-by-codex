# nvc.py reference

`python3 ~/.claude/skills/nexa-video-creator/scripts/nvc.py COMMAND ...`. Every command reads and writes the job
folder; any step can run again. Paths below are inside the job folder.

## Setup

| Command | Does |
|---|---|
| `doctor` | ffmpeg and its filters, Node, numpy, whisper-cli and a model, swiftc, a Gemini key (names only), the other nexa skills, the renderer, the T7, free disk |
| `doctor --setup` | builds `.venv` (numpy) in the skill folder, and the shared renderer at `~/.nexa-video-creator/renderer` |
| `doctor --setup --link-modules PATH` | uses an installed Remotion 4.0.528 project's `node_modules` (for example a remotion-broll kit project) instead of installing |
| `doctor --setup --npm` | installs the renderer's packages with npm (about 600 MB, downloaded) |

Environment: `NVC_HOME` (default `~/.nexa-video-creator`), `NVC_RENDERER`, `NVC_WHISPER_MODEL` (a ggml model file;
otherwise found in `NVC_HOME/models`, `/Volumes/T7 Shield/nexa-video-creator/models`, Homebrew's share folder and
`~/.local/share/*/models`), `CLAUDE_SKILLS_DIR`.

## Job

| Command | Flags | Writes |
|---|---|---|
| `new JOB` | `--target youtube\|shorts\|reels\|tiktok\|story\|feed\|square`, `--title`, `--id`, `--lang en\|bn\|auto`, `--fps 30`, `--brand #RRGGBB\|theme.json` | `job.json`, folders |
| `add JOB FILE...` | `--role camera\|screen\|broll\|image\|voice\|music\|dialogue\|segment\|logo`, `--id NAME` | a link in `media/originals/`, the probe in `job.json`; a voice-over's nexa-speech `words.json` becomes `analysis/words.json` |
| `ingest JOB` | `--force` (rebuild), `--no-faces` | `media/proxies/ID.mp4` (H.264 High, CFR at the job fps, BT.709 tagged, 1 s GOP, AAC 48 kHz, faststart; scaled down only to 2x the output for screens and 1.25x for cameras), `media/audio/ID.wav` (48 kHz mono 24-bit), `analysis/ID.faces.json`; `job.json`: `dialogue` (the master clock) and each source's `levels` |
| `sync JOB` | `--set SOURCE=SECONDS` (by hand) | `job.json` `sources.ID.sync`: `offset_s`, `drift_ppm`, `segments`, `steps`, `confidence` |
| `clean JOB` | `--isolate`, `--hum 50\|60` | `media/audio/DIALOGUE.clean.wav` (nexa-sound) |
| `transcribe JOB` | `--engine auto\|whisper\|gemini\|agy`, `--lang`, `--model` | `analysis/words.json`, `analysis/transcript.txt`; Gemini cost in `ledger.jsonl` |
| `brief JOB` | `--target` | `edit-brief.md` (or `edit-brief.TARGET.md`) |
| `compile JOB` | `--plan FILE`, `--target` | `out/TARGET/`: `edl.json`, `edl.md`, `report.json`, `pieces.json`, `speech.json`, `sfx_cues.json`, `words.out.json`, `captions.srt`, `captions.vtt`, `chapters.txt` |
| `audio JOB` | `--target`, `--music FILE`, `--no-music`, `--no-sfx`, `--budget USD` | `audio/TARGET/`: `dialogue.wav`, `music.wav`, `sfx.wav`, `mix.wav`, `audio.json`; sets `edl.json` `audio` |
| `stills JOB` | `--target`, `--frames 0,45,300` | `out/TARGET/stills/`, `out/TARGET/stills.png` |
| `render JOB` | `--target`, `--draft` (half size), `--out FILE` | `out/TARGET/JOB-TARGET.mp4`, `render.json` |
| `qa JOB` | `--target`, `--review` | `out/TARGET/qa.json` |
| `deliver JOB` | `--target`, `--force` | `final/`: `NAME-TARGET.mp4`, `.srt`, `.vtt`, `.chapters.txt`, `.notes.md`, `.CREDITS.txt`, `.report.md` |
| `segment broll PROJECT --job JOB` | `--comp NAME`, `--id` | `media/segments/ID.mp4` from a remotion-broll project, added as a `segment` source |
| `segment hf PROJECT --job JOB` | `--alpha`, `--id` | `media/segments/ID.webm` (VP9 with alpha) or `.mp4` from a HyperFrames project |
| `status JOB` | | what is done and the next step |

## Files

`job.json`:

```json
{"schema": "nvc-job/1", "id": "launch", "title": "...", "target": "youtube", "language": "en", "fps": 30,
 "dialogue": "cam",
 "sources": {"cam": {"role": "camera", "kind": "camera", "original": "/abs/cam.mov", "link": "media/originals/cam.mov",
                     "proxy": "media/proxies/cam.mp4", "audio": "media/audio/cam.wav", "duration": 612.4,
                     "width": 3840, "height": 2160, "face": {"x": 0.48, "y": 0.37, "found": 0.97},
                     "levels": {"snr_db": 41.2, "hf_share": 0.09}},
             "screen": {"role": "screen", "kind": "screen_recording", "sync": {"offset_s": 2.3700, "drift_ppm": 12.5,
                        "confidence": "high", "segments": [{"t_ref_from": 8.0, "t_ref_to": 600.0,
                        "offset_s": 2.37, "drift_ppm": 12.5}]}}},
 "steps": {"ingest": {"at": "2026-09-25T13:02:11+06:00", "seconds": 6.5}}}
```

`analysis/words.json`: `{"schema": "nvc-words/1", "source": "cam", "language": "en", "engine": "whisper",
"words": [{"id": "w0001", "text": "Today", "start": 3.12, "end": 3.54, "pause_after": 0.21}]}`. Times are seconds
on the master clock (the dialogue source's own time).

`out/TARGET/edl.json` (nvc-edl/1, read by the renderer): `width`, `height`, `fps`, `durationInFrames`, `safe`,
`bands`, `theme`, `base` (`jobs/ID/`), `audio`, `sources` (proxy paths, sizes, face), `clips` (`from`,
`durationInFrames`, `layout`, `cam` and `screen` placements with `trimBefore` in frames, `punch`, `pip`,
`transitionIn`, `masterIn`, `masterOut`), `overlays` (`type`, `from`, `durationInFrames`, `props`), `zooms`,
`captions` (`style`, `burn`, `fontPx`, `band`, `pages` or `cues`, `case`), `chapters`, `progress`, `meta`
(warnings, review). Every value is resolved: the renderer computes nothing but positions.

`out/TARGET/pieces.json`: `[{"masterIn": 3.0667, "masterOut": 7.8333, "outFrom": 0, "frames": 143}]`: the kept ranges
on the frame grid; `audio` cuts the dialogue from exactly these.

`out/TARGET/speech.json`: `{"spans": [[0.067, 4.61], ...]}` (output seconds; ducking). `sfx_cues.json`:
`[{"t": 4.067, "name": "whoosh-short", "align": "peak", "why": "transition into c002"}]`.

## Exit codes

0 done; 1 an error (the message says what to do). `compile` prints every plan error with the transcript's real words
and writes nothing else.
