# claude-agency-designer-set-by-codex

Four Claude Code skills that work as a small design agency: they design finished graphics at each platform's exact
size with real typography, write copy that sounds like the audience instead of a machine, make and check the images
with the Codex CLI on a ChatGPT plan, and watch, transcribe and check videos with Gemini through the Antigravity CLI
(no API keys needed).

| Skill | What it does |
|---|---|
| [`codex-design`](codex-design/SKILL.md) | Designs social posts, stories, carousels, thumbnails, covers, banners, ads, posters, flyers, brochures, book covers, certificates, invitations, signs and more: 526 researched formats, and a method for any size or kind it has never seen. Real type in HTML and CSS over generated plates, rendered by headless Chrome and measured (contrast on real pixels, safe zones, text sizes, folds), then judged by an independent senior-art-director review and gated before delivery. |
| [`natural-copy`](natural-copy/SKILL.md) | Writes and fixes any text an audience reads or hears (captions, ads, banner lines, product and web text, emails, WhatsApp and SMS, scripts, replies) so it sounds like a person from that audience: casual everyday words, no AI tone, no bookish, poetic or translated feel. English, Bangla and Banglish for Bangladesh first-class, and 18 more languages. Song lyrics, jingles and poems get their own rules and a lyricist's judge. |
| [`agy-watch-video`](agy-watch-video/SKILL.md) | Gives Claude eyes and ears for video: summaries, shot lists, frame-by-frame reports at full resolution, timestamped transcripts and subtitles (Bengali included), on-screen text, zoomed answers about any moment or detail, measured QA (cuts, black and frozen frames, flicker, loudness, platform specs and safe zones) and version comparisons. ffmpeg prepares and measures; Gemini 3.1 Pro and 3.8 Flash look and listen through the Antigravity CLI; two models are compared and Claude checks the evidence frames. |
| [`codex-imagegen`](codex-imagegen/SKILL.md) | Generates and edits the images a project needs through the logged-in Codex CLI: photos, illustrations, cutouts, logo concepts, favicons, OG cards and web exports, in parallel with a style lock, each one judged independently. Photos look like unretouched camera photos, and place and people come from the client, never the requester. |

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
- Any copy people will read, in any language: load `natural-copy` first and follow its fast path.
- Any graphic with text or layout: load `codex-design` first and follow its fast path.
- Any image to generate or edit: `codex-imagegen`. Any video or audio: `agy-watch-video`.
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
- [Claude Code](https://docs.claude.com/en/docs/claude-code).

## Install

```bash
git clone https://github.com/developerjillur/claude-agency-designer-set-by-codex.git
cd claude-agency-designer-set-by-codex
./install.sh
```

`install.sh` links the four skills into `~/.claude/skills` (so `git pull` updates them; `--copy` copies them
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
```

Every command, flag and output is documented in the `references/cli.md` of each skill.

## Tests

```bash
python3 -m unittest discover -s ~/.claude/skills/codex-design/tests
python3 -m unittest discover -s ~/.claude/skills/codex-imagegen/tests
python3 -m unittest discover -s ~/.claude/skills/agy-watch-video/tests
CODEX_DESIGN_PATTERNS=1 python3 -m unittest discover -s ~/.claude/skills/codex-design/tests -p "test_patterns.py"
```

The video skill also checks itself against synthetic clips with known answers: `watch_video.py selftest` (seconds, no
model) and `watch_video.py selftest --live` (about 20 real calls; run it after installing or updating agy).

The last one renders the whole pattern library (26 patterns on their presets) and fails on any error or warning.

## Layout

```
codex-design/     the design skill: scripts/ (design.py, copyrules.py, presets.json, voice_rules.json), templates/
                  (26 patterns, the kit, a sample brand), references/ (craft, copy, formats, research notes), tests/
natural-copy/     the voice skill: SKILL.md and references/ (English, Bangla, 18 more languages)
codex-imagegen/   the image skill: scripts/codex_image.py, references/, tests/
agy-watch-video/  the video skill: scripts/watch_video.py (and ocr.swift), references/ (engine, cli, playbooks,
                  platforms, research notes), tests/
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

## License

MIT, see [LICENSE](LICENSE).
