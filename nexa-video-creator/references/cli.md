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
`~/.local/share/*/models`), `CLAUDE_SKILLS_DIR`. Keys (the environment first, then the macOS keychain item of the same
name; names only are ever shown): `GEMINI_API_KEY` (Bangla transcription, the stock judge, `qa --review`),
`PIXABAY_API_KEY` (`stock`), `ELEVENLABS_API_KEY` (passed on to nexa-sound). Test hooks: `NEXA_PIXABAY_BASE_URL`,
`NEXA_PIXABAY_CACHE`, `NEXA_PIXABAY_SLEEP_SCALE`, plus the Gemini and ElevenLabs ones of the shared modules.

## Job

| Command | Flags | Writes |
|---|---|---|
| `new JOB` | `--target youtube\|shorts\|reels\|tiktok\|story\|feed\|square`, `--title`, `--id`, `--lang en\|bn\|auto`, `--fps 30`, `--brand #RRGGBB\|theme.json` | `job.json`, folders |
| `add JOB FILE...` | `--role camera\|screen\|broll\|image\|voice\|music\|dialogue\|segment\|logo`, `--id NAME` | a link in `media/originals/`, the probe in `job.json`; a voice-over's nexa-speech `words.json` becomes `analysis/words.json` |
| `ingest JOB` | `--force` (rebuild), `--no-faces` | `media/proxies/ID.mp4` (H.264 High, CFR at the job fps, BT.709 tagged, 1 s GOP, AAC 48 kHz, faststart; scaled down only to 2x the output for screens and 1.25x for cameras), `media/audio/ID.wav` (48 kHz mono 24-bit), `analysis/ID.faces.json`; `job.json`: `dialogue` (the master clock) and each source's `levels` |
| `sync JOB` | `--set SOURCE=SECONDS` (by hand) | `job.json` `sources.ID.sync`: `offset_s`, `drift_ppm`, `segments`, `steps`, `confidence` |
| `clean JOB` | `--isolate`, `--hum 50\|60` | `media/audio/DIALOGUE.clean.wav` (nexa-sound) |
| `transcribe JOB` | `--engine auto\|whisper\|gemini\|agy`, `--lang`, `--model` | `analysis/words.json`, `analysis/transcript.txt`; Gemini cost in `ledger.jsonl` |
| `brief JOB` | `--target`, `--style vox` (the Vox look, rules, the job's pictures and a storyboard of beats; remembered in `job.json` `style`) | `edit-brief.md` (or `edit-brief.TARGET.md`) |
| `compile JOB` | `--plan FILE`, `--target` | `out/TARGET/`: `edl.json`, `edl.md`, `report.json`, `pieces.json`, `speech.json`, `sfx_cues.json`, `words.out.json`, `captions.srt`, `captions.vtt`, `chapters.txt` |
| `audio JOB` | `--target`, `--music FILE`, `--no-music`, `--no-sfx`, `--budget USD` | `audio/TARGET/`: `dialogue.wav`, `music.wav`, `sfx.wav`, `mix.wav`, `audio.json`; sets `edl.json` `audio` |
| `stills JOB` | `--target`, `--frames 0,45,300` | `out/TARGET/stills/`, `out/TARGET/stills.png` |
| `render JOB` | `--target`, `--draft` (half size), `--out FILE` | `out/TARGET/JOB-TARGET.mp4`, `render.json` |
| `qa JOB` | `--target`, `--review` | `out/TARGET/qa.json` |
| `deliver JOB` | `--target`, `--force`, `--allow-noncommercial` | `final/`: `NAME-TARGET.mp4`, `.srt`, `.vtt`, `.chapters.txt`, `.notes.md`, `.CREDITS.txt`, `.report.md`; stops when nexa-sound's `credits --strict` finds ElevenLabs sound from a free or unknown plan (`--allow-noncommercial` only for an internal test) |
| `stock JOB "QUERY"` | `--type video\|animation\|photo\|illustration\|vector`, `--also "WORDS"` (repeatable), `--n 12`, `--orientation auto`, `--min-seconds S`, `--order popular\|latest`, `--lang`, `--editors-choice`, `--no-ai`, `--judge`, `--slot`, `--use broll\|ad\|background`, `--market`, `--auto-pick`, `--json` | `media/stock/QUERY/`: `candidates.json`, `sheet.png` (numbered), `thumbs/` |
| `stock JOB --pick ID` | `--id NAME` | `media/stock/pixabay-ID.mp4` (or `.jpg`, `.png`) and its `.json` record, added as `broll` or `image`; `job.json` `stock` |
| `segment broll PROJECT --job JOB` | `--comp NAME`, `--id` | `media/segments/ID.mp4` from a remotion-broll project, added as a `segment` source |
| `segment hf PROJECT --job JOB` | `--alpha`, `--id` | `media/segments/ID.webm` (VP9 with alpha) or `.mp4` from a HyperFrames project |
| `cutout JOB PICTURE...` | a file or a job source id; `--style auto\|color\|bw\|halftone` (auto: people halftone, the rest in colour), `--stroke auto\|none\|#RRGGBB`, `--stroke-width PX`, `--offset DX,DY`, `--shadow soft\|none`, `--no-lift`, `--id` | `media/cutouts/ID.png` (transparent, padded, at most 2000 px) and its `.json` record (from, style, people found, a stock licence carried over), added as an `image` source with `alpha` |
| `key JOB CLIP...` | a file or a job source id; `--on auto\|black\|green`, `--start S`, `--seconds N` (default 20), `--max PX` (default 1280), `--id` | `media/keyed/ID.webm` (VP9, alpha: on black the brightness is the alpha and the colour is un-premultiplied; on green a chroma key with despill) and its `.json` record, added as a `broll` source with `alpha` |
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

## Stock (Pixabay)

Search once with up to three wordings of the same need (`--also`), look at the numbered sheet, pick by id. Pixabay's
tags are English: search in English keywords whatever the video's language.

- The search: `GET /api/` (pictures) or `/api/videos/` with `safesearch=true`, `per_page` 3 times `--n`, the
  orientation from the frame (`auto`: landscape, portrait or square from the target), and for videos a minimum width
  or height so a clip can fill the frame. Answers are cached 24 hours (`~/.nexa-video-creator/pixabay-cache`),
  Pixabay's rate headers are read and a 429 waits for the reset (100 requests a minute by default). The key travels
  in the URL, so no URL is ever printed or stored with it.
- Skipped before the sheet: hits Pixabay marks `isLowQuality`, AI-made ones with `--no-ai`, videos under
  `--min-seconds`. Candidates that fill the frame without enlarging come first, then Pixabay's order.
- The sheet: 480x270 cells with a red number, the id, size, length and author (Swift, `scripts/sheet.swift`; an ffmpeg
  grid when swiftc is missing).
- `--judge` (Gemini 3.8 Flash on the sheet, about a cent): per candidate 0 to 5 for subject (weight 0.30), action
  (0.15), setting (0.10), people and market (0.15, left out when nobody is visible), quality (0.15) and framing
  (0.15), plus gates. A watermark, burned-in text, a logo or brand, unsafe content or the wrong place (with
  `--market`) rejects it outright, as does an AI look with `--no-ai` and a recognisable person in a sensitive context.
  Accept: a score of 0.70 for b-roll, 0.75 for ads, 0.65 for backgrounds, with subject 4 or more and quality and
  framing 3 or more; within 0.15 of that is "near". An ad candidate with a recognisable person comes back "human"
  (a person decides). `--auto-pick` adds the best accepted candidate that fills the frame; when none is accepted the
  tool says to search another way or make the shot (codex-imagegen from a text prompt, never a Pixabay file as the
  reference; remotion-broll for an explainer scene).
- `--pick ID`: videos download the largest rendition there is (large, up to 3840x2160; else medium, small, tiny); pictures the
  largest the key may fetch (`imageURL` or `fullHDURL` with full API access, otherwise `largeImageURL`, 1280 px at
  most on the long side). A picture that cannot fill the frame is flagged: use it as a card or pick another. The
  record next to the file: `{"schema": "nvc-stock/1", "source": "pixabay", "id", "type", "page_url", "user",
  "user_id", "tags", "query", "width", "height", "duration", "rendition", "ai_generated", "fills_frame", "downloaded",
  "sha256", "licence"}`.
- What Pixabay's API does not have: music, sound effects, GIFs and 3D (use nexa-sound for sound); scraping the site
  for them breaks its terms.

Pixabay's licence in short (the record carries it): free for commercial use and editing, no credit needed; never
sold or handed over as the file itself, alone or as stock, and never in a trademark or logo; no visible logo or
brand used to promote something; recognisable people not in health, dating, drug, adult or political contexts
(Pixabay has no model releases); no political use; do not feed the file to AI tools (img2img, outpainting, AI
upscaling, training). The delivery notes list every stock file with its Pixabay page and author, so a claim can be
traced and the file taken out.

Measured on the live API (2026-09-25, a 1920x1080 job, "laptop typing" and two more wordings): 1,491 hits, 3 skipped
as low quality, 12 on the sheet, all filling the frame; the judge rejected the two clips with a visible laptop logo
and scored the best 0.72, "near", not accepted: the tool asked for another search or a made shot.

## Exit codes

0 done; 1 an error (the message says what to do). `compile` prints every plan error with the transcript's real words
and writes nothing else.
