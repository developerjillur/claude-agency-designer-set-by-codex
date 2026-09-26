# claude-agency-designer-set-by-codex

Twenty Claude Code skills and two agents that work as a small design and video agency: they design finished graphics
at each platform's exact size with real typography, write copy that sounds like the audience instead of a machine,
make and check the images with the Codex CLI on a ChatGPT plan, edit real footage into finished videos for every
platform with Remotion, make any motion graphics video in code with a Remotion skill family (a director, eleven craft
skills and a tested component kit), voice scripts with Gemini text-to-speech, score them with Google Lyria, animate
explainer B-roll from a ready kit, and watch, transcribe and check videos with Gemini through the Antigravity CLI.

| Skill | What it does |
|---|---|
| [`codex-design`](codex-design/SKILL.md) | Designs social posts, stories, carousels, thumbnails, covers, banners, ads, posters, flyers, brochures, book covers, certificates, invitations, signs and more: 526 researched formats, and a method for any size or kind it has never seen. Real type in HTML and CSS over generated plates, rendered by headless Chrome and measured (contrast on real pixels, safe zones, text sizes, folds), then judged by an independent senior-art-director review and gated before delivery. |
| [`natural-text`](natural-text/SKILL.md) | Writes and fixes any text an audience reads or hears (captions, ads, banner lines, product and web text, emails, WhatsApp and SMS, scripts, replies) so it sounds like a person from that audience: casual everyday words, no AI tone, no bookish, poetic or translated feel. English, Bangla and Banglish for Bangladesh first-class, and 18 more languages. Song lyrics, jingles and poems get their own rules and a lyricist's judge. |
| [`agy-watch-video`](agy-watch-video/SKILL.md) | Gives Claude eyes and ears for video: summaries, shot lists, frame-by-frame reports at full resolution, timestamped transcripts and subtitles (Bengali included), on-screen text, zoomed answers about any moment or detail, measured QA (cuts, black and frozen frames, flicker, loudness, platform specs and safe zones) and version comparisons. ffmpeg prepares and measures; Gemini 3.1 Pro and 3.8 Flash look and listen through the Antigravity CLI; two models are compared and Claude checks the evidence frames. |
| [`remotion-broll`](remotion-broll/SKILL.md) | Explainer-video B-roll in Remotion from a ready kit: code-drawn 2D caricature characters (a guitarist and a runner, rigged), split screens, a round presenter picture-in-picture, a timeline editor, a stat card and bar chart that compute from one growth rate, kinetic captions, step cards, a finish line and a subscribe end card, with sound effects. Every word on screen lives in one file; a minute renders in about 45 s and is checked by the video skill. |
| [`nexa-video-creator`](nexa-video-creator/SKILL.md) | Edits real footage and makes finished videos like a professional editor: YouTube long-form, Shorts, Reels, TikTok, feed and Stories, ads, promos, tutorials, talking-head and faceless explainers. Syncs a separately recorded camera and screen by their sound (offset and drift), transcribes with word timings (Bangla included), cuts pauses, fillers and retakes on the frame grid, and places layouts, zooms, punch-ins, hook titles, stat and list cards, b-roll, 2D explainer animation, captions, music and effects. Claude writes the edit as a plan grounded to the transcript's words; a compiler checks it against the editing rules; Remotion renders it; the video skill checks the result. |
| [`nexa-sound`](nexa-sound/SKILL.md) | Music, sound effects and the final mix: Google Lyria scores (cheap drafts, structured finals, exact-length beds), a built-in synthesiser for effects the skill owns outright, music fitted to the edit on whole bars with hits on cuts, dialogue clean-up, ducking under speech with a gain envelope, mastering to each platform's loudness, measured QC and licence notes for clients. |
| [`nexa-speech`](nexa-speech/SKILL.md) | Human-sounding voice-overs and character voices with Gemini text-to-speech, one consistent voice from the first line to the last: voice profiles, Bangla and English number handling, chunking, a cache so no line is paid for twice, measured QA of every take, a mastered 48 kHz track with sentence and word timings and subtitles, and scenes fitted to a length. |
| [`codex-imagegen`](codex-imagegen/SKILL.md) | Generates and edits the images a project needs through the logged-in Codex CLI: photos, illustrations, cutouts, logo concepts, favicons, OG cards and web exports, in parallel with a style lock, each one judged independently. Photos look like unretouched camera photos, and place and people come from the client, never the requester. |
| [`nexa-remotion`](nexa-remotion/SKILL.md) | The director of a Remotion skill family that makes any video in code like a motion design studio: explainers, product launches, app demos, kinetic type, data and map stories, social shorts with captions, ads, trailers, lyric videos, audiograms, logo stings and 3D product shots, in 20 ready themes and 27 named looks. It plans the treatment and a storyboard timed to the voice or the beat, builds from a tested kit for Remotion 4.0.528 (about 600 components across motion, type, design, charts and diagrams, interfaces and devices, maps, 3D, effects and transitions, editing and sound), checks stills and renders, measures the file and hands the review to an independent critic agent. Built on a full read of the Remotion docs, source, templates, examples and community (`nexa-remotion/references/kb/`). |
| `nexa-remotion-motion`, `-type`, `-design`, `-graphics`, `-ui`, `-maps`, `-3d`, `-fx`, `-edit`, `-render`, `-styles` | The craft skills the director calls: timing, springs and camera; kinetic text and captions (Bangla included); grounds, texture, layout and colour; charts, diagrams and icons; interfaces, devices, lower thirds and logo reveals; maps, routes and globes; 3D; effects, looks, keying and transitions; footage and sound; render settings and the cloud; a catalogue of looks. Each has its kit module with a README and a demo per component. |

## Fast for everyday work, strict for client finals

Every skill opens with a fast path for drafts (a caption, a post, a placeholder image, a quick look at a video): a
few tool calls, offline checks only, no judges. Client finals take each skill's client level: the independent judges,
`--runs 3` and the delivery gate. Measured on two everyday tasks: a Bangla caption in 15 s and an Instagram post in
39 s, down from 202 s and 447 s. A design's final check is one command, `deliver --judge`, which runs the design judge
and the copy judge at the same time before the gates (43 s for a Bengali post, 3 runs each).

At a low effort setting Claude Code may not load a skill unless told to. A few lines in your global `CLAUDE.md` fix
that:

```markdown
## Our skills: use them for these jobs, every time
- Any copy people will read, in any language: load `natural-text` first and follow its fast path.
- Any graphic with text or layout: load `codex-design` first and follow its fast path.
- Any image to generate or edit: `codex-imagegen`. Any video or audio: `agy-watch-video`.
- Animated explainer B-roll or motion graphics: `remotion-broll`.
- Editing or making a video from footage, a voice-over or assets: `nexa-video-creator`.
- Any video, motion graphics or animation made in code with Remotion: `nexa-remotion` first.
- Music, sound effects, voice clean-up or a mix: `nexa-sound`. A voice-over or character voice: `nexa-speech`.
```

## Why it holds up

- **Measured, not eyeballed.** Every render writes a report (`.qa.json`) with contrast, safe-zone, keep-out, fold and
  text-size checks. A delivery gate refuses a design without a clean render, an independent judge's pass on that exact
  file and copy that passed its own checks.
- **Copy that reads human.** A copy lint (`copylint`) with 932 tested rules in 24 languages catches AI templates ("it's
  not X, it's Y", "elevate your", launch clichés), translated structure, bookish or sadhu Bangla and fake casual. It was
  calibrated so that 287 natural lines draw no finding while 232 of 234 robotic lines are caught. A native-reader judge
  (`copyjudge`) scores fidelity to the brief before anything else and lints its own rewrites.
- **Never two designs alike.** A design ledger rejects a layout recipe too close to a client's recent work.
- **Video claims are checked, not trusted.** Detail comes from sharp full-resolution frames and zoom, never from the
  low-detail video stream; two Gemini models answer every question and must agree on every number and colour; a claim
  is verified with a neutral question that hides it, then judged. ffmpeg measures every frame on a change grid, so a
  pop-up that shows between two sampled frames still gets a frame and a close-up, and the moving person gets a
  close-up of what they carry. Measured QA (cuts, black and frozen frames, flashes, loudness, platform specs and safe
  zones) needs no model at all.
- **Global by default.** Place, people, language, digits and currency come from the client's market.

## Requirements

- macOS with the Xcode Command Line Tools (`xcode-select --install`), for on-device OCR.
- Python 3.9 or newer (`python3`).
- Google Chrome (the Compose route renders with headless Chrome).
- The [Codex CLI](https://github.com/openai/codex), logged in with a ChatGPT plan that includes image generation
  (`codex login`). It generates the images and runs the judges; the offline tools and the lint work without it.
- For `agy-watch-video`: [ffmpeg](https://ffmpeg.org) (`brew install ffmpeg`) and the
  [Antigravity CLI](https://antigravity.google/download#antigravity-cli), signed in once with `agy`. See the note on
  Antigravity's terms below.
- For `remotion-broll` and `nexa-video-creator`: [Node.js](https://nodejs.org) 22.6 or newer (npm installs Remotion
  4.0.528; `nvc.py doctor --setup --link-modules PATH` reuses an installed kit's packages instead).
- For `nexa-video-creator`: [whisper.cpp](https://github.com/ggml-org/whisper.cpp) (`brew install whisper-cpp`) and a
  large-v3-turbo model, for English transcripts only: every other language is transcribed with Gemini 3.5 Transcribe
  on the API key, and English moves to Gemini too when whisper looks unsure. numpy is installed into the skill's own
  environment by `doctor --setup`.
- For `nexa-speech`, `nexa-sound` and Bangla transcripts: a Gemini API key from a Google Cloud project with billing
  turned on, in `GEMINI_API_KEY` or in the macOS keychain (`security add-generic-password -a "$USER" -s GEMINI_API_KEY -w`
  asks for it at a prompt). The skills never ask for a key, print it or write it to a file.
- Optional keys, the same way (environment variable or keychain item of the same name):
  - `ELEVENLABS_API_KEY` for ElevenLabs music, ambience loops, realistic effects, voice isolation, Scribe
    transcripts and forced alignment. Give the key User access (the tools read the plan: free-plan output is
    marked for evaluation and never delivered to a client) and the endpoints you use. Client work needs a paid
    plan.
  - `PIXABAY_API_KEY` for stock video, photos, illustrations and vectors (`nvc.py stock`). Pixabay's API has no
    music, sound effects, GIFs or 3D; without full API access, pictures stop at 1280 px.
  - `FREESOUND_API_KEY` for CC0 sound effects.
- [Claude Code](https://docs.claude.com/en/docs/claude-code).

## Install

```bash
git clone https://github.com/developerjillur/claude-agency-designer-set-by-codex.git
cd claude-agency-designer-set-by-codex
./install.sh
```

`install.sh` links the eight skills into `~/.claude/skills` (so `git pull` updates them; `--copy` copies them
instead), sets up each skill's Python environment and checks the machine. It never overwrites an existing folder.
Restart Claude Code afterwards. `./install.sh --test` also runs the offline test suites.

## Use

Ask Claude Code in plain words, in any language; the skills load by themselves:

- "Design an Instagram carousel for our Saturday open day, 5 slides."
- "YouTube thumbnail for this video, and a matching community post."
- "biye card design kore dao" or "post er caption likhe dao" (Banglish works).
- "Make a KDP paperback cover, 6x9, 240 pages, cream paper."
- "What happens in this video?", "Check this reel before I post it", "Transcribe this and give me subtitles",
  "Why does the app crash at 0:12 in this recording?"
- "Explainer B-roll for our course launch, one minute" or "remotion diye 2D caricature video banao"
- "Edit my face cam and screen recording for YouTube", "ei video theke 3 ta reels cut koro"
- "Bangla voice over banao ei script diye", "corporate background music lagbe 45 second"

Or call the tools directly:

```bash
python3 ~/.claude/skills/codex-design/scripts/design.py presets --find "youtube thumbnail"
python3 ~/.claude/skills/codex-design/scripts/design.py render --html post.html --preset ig-portrait --out post.png
python3 ~/.claude/skills/codex-design/scripts/design.py copylint --caption caption.txt --platform instagram --locale BD
python3 ~/.claude/skills/codex-design/scripts/design.py copyjudge --caption caption.txt --brief brief.md --runs 3
python3 ~/.claude/skills/codex-imagegen/scripts/codex_image.py doctor --smoke
python3 ~/.claude/skills/agy-watch-video/scripts/watch_video.py watch clip.mp4 --goal promo --platform reels
python3 ~/.claude/skills/agy-watch-video/scripts/watch_video.py ask clip.mp4 "What is on the sign?" --at 0:12
python3 ~/.claude/skills/agy-watch-video/scripts/watch_video.py verify clip.mp4 "the logo appears before the title" --from 0 --to 5
python3 ~/.claude/skills/remotion-broll/scripts/broll.py new ~/videos/launch-broll
python3 ~/.claude/skills/remotion-broll/scripts/broll.py render ~/videos/launch-broll
python3 ~/.claude/skills/nexa-video-creator/scripts/nvc.py new ~/videos/launch --target youtube
python3 ~/.claude/skills/nexa-speech/scripts/speech.py profile new bn-yt --preset bn-yt-explainer-m
python3 ~/.claude/skills/nexa-speech/scripts/speech.py plan script.md --profile bn-yt --out vo
python3 ~/.claude/skills/nexa-sound/scripts/sound.py sfx list
```

Every command, flag and output is documented in the `references/cli.md` of each skill.

## Tests

```bash
python3 -m unittest discover -s ~/.claude/skills/codex-design/tests
python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests
python3 -m unittest discover -s ~/.claude/skills/agy-watch-video/tests
python3 -m unittest discover -s ~/.claude/skills/remotion-broll/tests
python3 -m unittest discover -s ~/.claude/skills/nexa-video-creator/tests
python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests
python3 -m unittest discover -s ~/.claude/skills/nexa-speech/tests
python3 -m unittest discover -s ~/.claude/skills/nexa-remotion/tests
CODEX_DESIGN_PATTERNS=1 python3 -m unittest discover -s ~/.claude/skills/codex-design/tests -p "test_patterns.py"
```

The video skill also checks itself against synthetic clips with known answers: `watch_video.py selftest` (seconds, no
model) and `watch_video.py selftest --live` (about 20 real calls; run it after installing or updating agy).

The Remotion kit checks itself by typechecking every module and rendering every demo to a labelled contact sheet:
`python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py demos` (the whole kit, a few minutes) or `--module NAME`.

The last one renders the whole pattern library (26 patterns on their presets) and fails on any error or warning.

## Layout

```
codex-design/     the design skill: scripts/ (design.py, copyrules.py, presets.json, voice_rules.json), templates/
                  (26 patterns, the kit, a sample brand), references/ (craft, copy, formats, research notes), tests/
natural-text/     the voice skill: SKILL.md and references/ (English, Bangla, 18 more languages)
codex-imagegen/   the image skill: scripts/codex_image.py, references/, tests/
agy-watch-video/  the video skill: scripts/watch_video.py (and ocr.swift), references/ (engine, cli, playbooks,
                  platforms, research notes), tests/
remotion-broll/   the B-roll kit: template/ (the Remotion project), scripts/broll.py, references/ (scenes, picture
                  briefs), tests/
nexa-video-creator/ the editor: scripts/nvc.py (pipeline), nvc_plan.py (plan checks and compile), template/ (the
                  Remotion renderer), references/ (plan, cli, editing rules, engines), tests/
nexa-sound/       music, effects and mix: scripts/sound.py, sfx_synth.py, beats.py, references/, tests/
nexa-speech/      voice-overs: scripts/speech.py, voices and presets, references/, tests/
nexa-remotion/    the Remotion director: scripts/nrk.py, kit/ (the component library: src/kit/<module>/ with a
                  README each, src/demos/, generated demo media in public/), agents/ (director and reviewer),
                  references/ (process, quality, platforms, core, prompting, kb/ research), evals/, tests/
nexa-remotion-*/  the eleven craft skills: SKILL.md and references/ each
```

## Notes

- Tidewater, Northloaf, Tokjhal, Sutokotha and Vela Cycles are fictional sample brands used in the templates, tests and
  case studies. Their URLs use the reserved `.example` domain.
- `codex-design/references/research/` holds dated research notes with their sources. They are evidence, not rules:
  where a note and a reference file disagree, the reference file wins.
- Generated images keep their provenance metadata (C2PA); the tools never strip or fake it.
- `agy-watch-video` sends the video's frames and audio to Google through your Antigravity account. Google's
  Antigravity FAQ says "using third party software, tools, or services to access Antigravity is a violation of our
  Terms of Service" and recommends a Gemini Enterprise or Google AI Studio API key for third-party coding agents. The
  skill calls the official `agy` binary in its documented headless mode; whether that fits your account is your call.
  agy can also run on a Gemini API key, and the skill works the same way (see `agy-watch-video/references/engine.md`).
- The sample photos in `codex-design/templates/patterns/assets/photos/` were generated with `codex-imagegen` for the
  fictional sample brand and say so in their metadata (IPTC DigitalSourceType trainedAlgorithmicMedia).
- The sample brand's fonts are open-licensed (SIL OFL 1.1); see `codex-design/templates/sample-brand/fonts/`.
- `nexa-speech` and `nexa-sound` call the Gemini API with your key and cost money per call (a 10-minute voice-over is
  about $0.17 to $0.25 on Gemini 3.8 Flash TTS, a Lyria 3.5 track $0.08; September 2026 prices). Every call is
  estimated first, logged in the job's `ledger.jsonl`, and stopped by a budget guard. Use a key from a project with
  billing turned on: on the free tier Google may use what you send to improve its products.
- Lyria music and Gemini voices carry Google's SynthID watermark; the tools keep it and never try to remove it. Lyria
  music is not exclusive, so it is never registered with Content ID.
- Remotion is free for individuals and companies of up to 3 people; above that, code that renders counts as an
  automation under Remotion's company licence.
- `nexa-remotion/references/kb/` holds research notes written in our own words from the Remotion docs, source,
  templates and examples (with version tags for 4.0.528); no official text or code is copied. The kit's demo media
  (clips, photos, sounds, a GLB model) were made locally with ffmpeg and code.

## License

MIT, see [LICENSE](LICENSE).
