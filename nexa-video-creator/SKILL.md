---
name: nexa-video-creator
description: "Edits real footage and makes finished videos for every platform, like a professional editor: YouTube long-form, Shorts, Reels, TikTok, Facebook and Instagram feed and Stories, ads, promos, tutorials, talking-head and screen-recording videos, faceless explainers and day or occasion videos. It syncs a separately recorded camera and screen recording by their sound (offset and clock drift), transcribes with word timings (Bangla included), cuts pauses, fillers and retakes on the frame grid, and places layouts (picture-in-picture, split, stacked 9:16), zooms, punch-ins, hook titles, stat and list cards, keyword pops, lower thirds, b-roll, 2D explainer animation from remotion-broll, HyperFrames segments, burned captions, music, sound effects and platform loudness, then renders with Remotion and checks the result. Use it whenever someone asks to edit, cut or make a video, or to turn raw recordings into a finished one, Banglish included ('video edit kore dao', 'youtube er jonno edit koro', 'reels banao', 'shorts cut koro', 'screen recording ar face cam sync koro')."
---

# nexa-video-creator

Claude is the editor; the tool is the engine. The tool measures (sync, word timings, pauses, loudness), compiles and
checks every decision against the transcript and the editing rules, renders with Remotion and runs the QA. Claude
reads the brief and writes the edit as a plan grounded to word ids and exact quotes, so no time is ever guessed.
Command prefix: `python3 ~/.claude/skills/nexa-video-creator/scripts/nvc.py`.

## Fast path (do exactly this)

1. **Job:** `nvc.py new JOB --target youtube --title "..." [--lang bn]`. Keep jobs with long footage on the T7.
   Targets: youtube, shorts, reels, tiktok, story, feed (4:5), square.
2. **Media:** `nvc.py add JOB cam.mov --role camera`, `add JOB screen.mov --role screen`, and b-roll, images,
   music, logos with their roles. Files are linked, never changed.
3. **Measure:** `ingest` (proxies, audio, the best microphone as the master clock, face position), `sync` (every
   other recording against the dialogue: offset and drift), optional `clean` (nexa-sound voice clean-up), then
   `transcribe` (whisper.cpp with DTW for English, Gemini 3.5 Transcribe for Bangla with a key, agy otherwise).
4. **Read** `nvc.py brief JOB` → `edit-brief.md`: the transcript with word ids, fillers, retakes, numbers said, long
   pauses, the target's rules and a plan example.
5. **Edit:** write `JOB/plan.json` (below and `references/plan.md`). All on-screen words go through natural-copy
   first. Then `nvc.py compile JOB`. Errors come back with the transcript's real words: fix and compile again.
   Confirm every `?` review item (a number on screen the speaker did not say) or add its source.
6. **Sound and picture:** `nvc.py audio JOB` (dialogue cut on the frame grid, music fitted and ducked, effects,
   mixed to the platform: nexa-sound), `nvc.py stills JOB` (look at the sheet, fix, look again only where it
   changed), `nvc.py render JOB`.
7. **Check and hand over:** `nvc.py qa JOB` (for client finals `--review`: the Gemini watch with every on-screen
   line expected), then `nvc.py deliver JOB` (video, SRT, VTT, chapters, credits, disclosure notes, report).

Another format from the same footage: write `plan.shorts.json`, then `compile`, `audio`, `render` with
`--target shorts`. Faceless explainer: make the voice with nexa-speech, `add JOB vo_48k.wav --role voice`, and
carry the picture with b-roll, images, segments and graphics.

## How to edit (the plan)

- **Hook first.** Open on the strongest line, never on a greeting ("Hi everyone"), a logo or silence. First word by
  0.5 s, the promise said or shown by 3 s (short-form, ads) or 5 s (long-form). A 3 to 7 word hook title from frame 0
  (`"at": "start"`). Reordering for a cold open is allowed; the tool warns when a segment repeats earlier material.
- **Structure.** Segments are the kept spans in output order, each with a beat (hook, problem, step, proof, payoff,
  close) and a layout. Long-form: re-engage near 3:00 and 6:00, never signal the end early, end on the payoff.
  Short-form: a visual change every 1.5 to 3 s, a re-hook near the middle, a loop or a call to action of 2 s or less.
- **Cuts.** The tool keeps 50 ms before and 80 ms after each kept word, never cuts inside a pause under 150 ms, trims
  long pauses to the target's length, and cuts bounded filled pauses (um, uh, উম, হুম) by itself. You remove
  retakes and false starts (`remove`), keep discourse markers that carry meaning (মানে, আসলে), and hold a pause after
  a punchline with `holds`.
- **Picture.** Screen for doing, face for explaining, feelings and credibility. Layouts: camFull, screenFull,
  screenPip, split, stack (9:16), brollFull, voiceOnly. Jump cuts inside a camFull segment get an automatic punch-in
  when the source has the pixels; add `punches` on emphasis. Zoom on the screen where something small happens
  (1.5 to 2x, held 2 s or more).
- **Graphics.** A number said becomes a stat card, steps become a list, a claim against another a compare card, a
  quote a quote card, a name a lower third, one stressed word a keyword pop, a chapter a chapter card, the ask a CTA.
  B-roll (1.5 to 6 s) starts on the word it shows. Every shown number must be in the grounded quote, or carry
  `facts` with origin brief, client or web.
- **2D explainer animation.** Build it with remotion-broll (the kit's rigged characters, charts and scenes), then
  `nvc.py segment broll KIT_PROJECT --comp NAME --job JOB` and place it as a `segment` overlay. HyperFrames for a
  short design-led unit (kinetic title, logo sting, website capture): `nvc.py segment hf HF_PROJECT --alpha --job JOB`
  (see `references/engines.md`). Remotion stays the master timeline.
- **Captions.** Word style (1 to 3 words, the spoken word lit) for vertical and short-form; sentence subtitles as an
  SRT for YouTube (burn them only when asked). Emphasise one word per phrase at most. Bangla: whole-word styling, no
  letter-spacing, the danda never starts a line (the tool enforces these).
- **Sound.** Music under speech about 20 dB down and ducked by an envelope, effects on visual events and rarely (at
  most one every 1 to 2 s in short videos, every 4 to 10 s in long ones). Music: a licensed file, a library track,
  or Lyria through nexa-sound (`"music": {"generate": "final", "mood": "corporate"}` costs about $0.08).

## Commands

| Command | Does |
|---|---|
| `new`, `add`, `status` | the job folder, media (linked), what is done and next |
| `ingest` | probe, classify, H.264 BT.709 CFR proxies (VFR fixed), 48 kHz audio, best microphone, face position |
| `sync [--set SRC=SECONDS]` | offset, drift and steps of every recording against the dialogue (confidence high, medium, low) |
| `clean [--isolate] [--hum 50]` | dialogue clean-up by nexa-sound, delay removed and checked |
| `transcribe [--engine auto\|whisper\|gemini\|agy]` | words with ids on the master clock, edges measured |
| `brief` | `edit-brief.md` for writing the plan |
| `compile [--target T]` | the plan verified and compiled: `out/T/edl.json`, `edl.md`, captions, chapters, cues |
| `audio [--music FILE] [--no-music] [--no-sfx]` | the mix at the platform's loudness (nexa-sound; dialogue only without it) |
| `stills`, `render [--draft]` | the contact sheet; the video |
| `qa [--review]`, `deliver [--force]` | the checks; the final files |
| `segment broll\|hf PROJECT --job JOB` | remotion-broll or HyperFrames renders added as media |
| `doctor [--setup --link-modules PATH]` | the machine; builds the numpy venv and the shared Remotion renderer |

## Rules

- Never change or delete the user's original files. Proxies, audio and renders live in the job folder.
- A plan with errors does not compile, and a video with open QA items is not delivered without `--force` and a
  reason given to the user. Look at the stills before every full render.
- On-screen copy through natural-copy; thumbnails through codex-design; generated images through codex-imagegen.
- A synthetic voice, a generated person or generated music is disclosed where the platform asks (the delivery notes
  say where). Never present a generated person as a real customer or expert.
- Music must be licensed for the platform (Meta ads: no licensed commercial music; TikTok business: the Commercial
  Music Library). Lyria music is not exclusive and never goes to Content ID.
- Private data in screen recordings (e-mails, keys, customer records, notifications) gets a `redact` overlay.

## Measured on this machine (Mac Studio M4 Max, 2026-09-25)

| Step | Test media (a 21.7 s camera clip and a 24.2 s 60 fps screen recording) |
|---|---|
| `ingest` (2 proxies, audio, mic choice) | 6.5 s |
| `sync` | 0.4 s: +2.3700 s found (true offset 2.37 s), confidence high |
| `transcribe` (whisper large-v3-turbo q5_0, DTW) | 1.7 s for 45 words; plain segment offsets had put a word 1.5 s late, DTW matched the speech |
| `compile`, `audio` | under 1 s each; the mix -14.2 LUFS, true peak -4.0 dBTP |
| `stills` (5 to 11 frames) | 2.8 to 5.5 s |
| `render` 1080p | 13.4 s of video in 11.5 s (0.86 s a second); research measured 50 to 60 s a minute for 1080p edits |

## Licence

Remotion is free for individuals and companies of up to 3 people. Above that, code that runs `remotion render`
counts as an automation (Remotion for Automators: $0.01 a render, at least $100 a month). HyperFrames is Apache-2.0.
The fonts come from Google Fonts (OFL).

## Files

- `scripts/nvc.py` (the CLI), `nvc_plan.py` (plan checks and compile), `nvc_sync.py` and `nvc_dsp.py` (sync, speech
  activity, word snapping; numpy in the skill venv), `facetrack.swift` (Apple Vision), `presets.json` (targets,
  safe zones, captions, pacing, loudness), `gemini_api.py` (shared with nexa-speech and nexa-sound).
- `template/`: the Remotion renderer (layouts, overlays, captions, transitions), synced to
  `~/.nexa-video-creator/renderer` on use.
- `references/plan.md` (the plan, with examples per video type), `references/cli.md` (every command and file),
  `references/editing-rules.md` (the craft rules and their sources), `references/engines.md` (Remotion, remotion-broll
  and HyperFrames together).
- `tests/`: `python3 -m unittest discover -s ~/.claude/skills/nexa-video-creator/tests`.
