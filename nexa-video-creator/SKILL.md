---
name: nexa-video-creator
description: "Edits real footage and makes finished videos for every platform, like a professional editor: YouTube long-form, Shorts, Reels, TikTok, Facebook and Instagram feed and Stories, ads, promos, tutorials, talking-head and screen-recording videos, faceless explainers, Vox-style explainers (paper collage, halftone cut-outs with a marker stroke, counters, charts, newspaper highlights, typewriter lines) and day or occasion videos. It syncs a separately recorded camera and screen recording by their sound (offset and clock drift), transcribes with word timings (Bangla included), cuts pauses, fillers and retakes on the frame grid, and places layouts (picture-in-picture, split, stacked 9:16), zooms, punch-ins, designed full-frame scenes (kinetic words, step cards, charts, before and after, end cards), hook titles, lower thirds, b-roll (judged Pixabay stock), burned captions, music, sound effects and platform loudness, then renders with Remotion and checks the result. Use it whenever someone asks to edit, cut or make a video, or to turn raw recordings into a finished one, Banglish included ('video edit kore dao', 'youtube er jonno edit koro', 'reels banao', 'shorts cut koro', 'screen recording ar face cam sync koro', 'vox style video banao')."
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
   `transcribe` (Gemini 3.5 Transcribe for every language but English; English on whisper.cpp with DTW, moved to
   Gemini by itself when whisper looks unsure: low token confidence, a looping phrase, letters outside the Latin
   script; agy without a key). The house rule since 2026-09-26: never rely on whisper for Bangla or other languages.
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
carry the picture with a designed scene per sentence or two (kinetic, step, bigStat, bars, versus, photo, recap,
endCard; the recipe is in `references/plan.md`).

Vox-style explainer (the paper-collage look: `references/vox.md`):
1. Voice with nexa-speech, `nvc.py add JOB vo_48k.wav --role voice`, then `nvc.py brief JOB --style vox`: the look,
   the rules, the job's pictures and a storyboard of the narration as beats with word ids.
2. Pictures per beat: `nvc.py stock JOB "..." --type photo` and `--pick`, then `nvc.py cutout JOB ID...` (people
   become halftone with the red marker stroke, objects keep their colour, a shadow is baked in) and
   `nvc.py key JOB ID` for fire, smoke or sparks shot on black (a transparent WebM).
3. One `vox` overlay per beat (`references/plan.md`, vox beats): an anchor picture, then one new thing about every
   second on the word it shows (cut-outs, clips, a counting `tag`, a `chart`, a `headline`, `bubble`s, a
   `newspaper` with marks, a `typewriter` closer, `scribble`s, a `credit` for the source). `"progress_bar":
   "bottom"`, facts on every number. Then compile, stills, audio, render, qa as usual.

B-roll for a slot (a common, real-world shot: hands typing, a city street, coffee being poured):
1. `nvc.py stock JOB "hands typing laptop" --also "keyboard close up" --also "person working laptop" --judge --slot
   "hands typing on a laptop, close, no logos"` (English keywords; add `--market bangladesh` when people or places
   must fit the client's market, `--no-ai` for real footage only).
2. Look at `media/stock/QUERY/sheet.png`, then `nvc.py stock JOB --pick ID --id broll-typing`: the clip, its licence
   record and a `broll` source in the job.
3. Nothing accepted after two searches: make the shot instead (remotion-broll for explainer scenes, codex-imagegen
   for a still from a text prompt, never from a Pixabay file). Specific places, products and the client's own people
   never come from stock.

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
  `facts` with origin brief, client, web or formula.
- **Scenes: the quality bar.** Where the words carry the video (a faceless explainer, a key point in a talk), use
  the designed full-frame scenes (`references/plan.md`, Scenes), made in the remotion-broll kit's style: `kinetic`
  for the hook and key lines, `step` for each section, `bigStat` and `bars` for numbers, `versus` for before and
  after, `photo` for b-roll and stock, `recap` and `endCard` to close. Colours change from scene to scene, every hold
  moves, sweeps and slides carry the cuts, and every moment has its sound; over a camera the speaker stays in a round
  picture. Judge the stills against the kit's minute cut, not against "clean".
- **Vox beats.** For the explainer look (a paper ground that never changes, pictures and numbers arriving on the
  words), use `vox` overlays instead of scenes: the compiler times every element to its word (landing just before
  it), places it by slot for the frame's shape, keeps text inside the safe area and clear of other text, and gives
  each movement a soft sound. `references/vox.md` has the look, the beat recipes and the rules.
- **2D explainer animation.** For drawn characters and acting, build a remotion-broll kit segment, then
  `nvc.py segment broll KIT_PROJECT --comp NAME --job JOB` and place it as a `segment` overlay. Remotion comes first
  for everything; HyperFrames only where Remotion cannot do the job (`nvc.py segment hf HF_PROJECT --alpha --job JOB`,
  see `references/engines.md`).
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
| `stock JOB "QUERY" [--also W] [--judge] [--pick ID]` | Pixabay videos, photos, illustrations and vectors on a numbered sheet, judged for the slot; a pick downloads it with its licence record |
| `cutout JOB PICTURE... [--style auto\|color\|bw\|halftone] [--stroke]` | cut-outs for vox beats (Apple Vision on this Mac): people halftone with the marker stroke, objects in colour, a baked shadow |
| `key JOB CLIP... [--on auto\|black\|green] [--start S --seconds N]` | a clip shot on black or green made transparent (VP9 WebM with alpha) |
| `brief JOB --style vox` | the brief with the Vox look, rules, the job's pictures and a storyboard of beats |
| `doctor [--setup --link-modules PATH]` | the machine; builds the numpy venv and the shared Remotion renderer |

## Rules

- Never change or delete the user's original files. Proxies, audio and renders live in the job folder.
- A plan with errors does not compile, and a video with open QA items is not delivered without `--force` and a
  reason given to the user. Look at the stills before every full render.
- On-screen copy through natural-copy; thumbnails through codex-design; generated images through codex-imagegen.
- A synthetic voice, a generated person or generated music is disclosed where the platform asks (the delivery notes
  say where). Never present a generated person as a real customer or expert.
- Music must be licensed for the platform (Meta ads: no licensed commercial music; TikTok business: the Commercial
  Music Library). Lyria and ElevenLabs music is not exclusive and never goes to Content ID. `deliver` stops when the
  sound has ElevenLabs items from a free or unknown plan.
- Stock from Pixabay is used inside the edit, never handed over as files; no clip with a visible logo or brand, no
  recognisable person in a health, dating, drug, adult or political context, no Pixabay file fed to an AI tool.
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
| a 43 s Bangla explainer of 11 scenes (voice, music, 17 effects) | compile under 1 s, `audio` 6 s, `stills` 3 s, `render` 24 s (0.55 s a second) |
| a 43 s Vox explainer of 7 beats (8 cut-outs, a keyed fire, 34 soft cues) | `cutout` 6 s for 8 pictures, `key` 11 s for 8 s of fire, compile under 1 s, `render` 34 s (0.8 s a second) |
| "The box that shrank the world", a 59 s Vox explainer made end to end (nexa-speech voice, whisper words, 10 Pixabay files, 8 beats, Lyria music, 44 cues) | voice 2 min with retakes (about $0.05), `transcribe` 3 s, `audio` 33 s with music, `render` 46 s (0.79 s a second), QA clean |

## Licence

Remotion is free for individuals and companies of up to 3 people. Above that, code that runs `remotion render`
counts as an automation (Remotion for Automators: $0.01 a render, at least $100 a month). HyperFrames is Apache-2.0.
The fonts come from Google Fonts (OFL). Pixabay stock: the Pixabay Content License (free for commercial use, no
credit needed, the limits above; `references/cli.md` has the full list), recorded next to every file.

## Files

- `scripts/nvc.py` (the CLI), `nvc_plan.py` (plan checks and compile), `nvc_sync.py` and `nvc_dsp.py` (sync, speech
  activity, word snapping; numpy in the skill venv), `facetrack.swift` (Apple Vision), `presets.json` (targets,
  safe zones, captions, pacing, loudness), `gemini_api.py` and `elevenlabs_api.py` (shared with nexa-speech and
  nexa-sound), `pixabay_api.py` (the stock search: cache, rate limits, the key kept out of every URL shown),
  `sheet.swift` (the numbered contact sheet), `nvc_vox.py` (vox beats: times, slots, checks, cues, the storyboard),
  `cutout.swift` (the cut-outs: Apple Vision and Core Image).
- `template/`: the Remotion renderer (layouts, overlays, the designed scenes in `src/scenes.tsx`, the vox beats,
  paper, grain and light leaks in `src/vox.tsx`, captions, transitions), synced to `~/.nexa-video-creator/renderer`
  on use.
- `references/plan.md` (the plan, with examples per video type), `references/cli.md` (every command and file),
  `references/editing-rules.md` (the craft rules and their sources), `references/engines.md` (Remotion, remotion-broll
  and HyperFrames together), `references/vox.md` (the Vox explainer look and recipes) with its research in
  `references/research/`.
- `tests/`: `python3 -m unittest discover -s ~/.claude/skills/nexa-video-creator/tests`.
