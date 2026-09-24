# R1: Existing tools that give coding agents "video watching" (survey, 2024 to 2026-09-24)

Prepared 2026-09-24 for the planned Claude Code video skill (ffmpeg for cutting, frames and audio; Google Antigravity CLI `agy` headless calls to Gemini; structured results back into Claude Code).

Method: GitHub search (repos, code, issues) through the logged-in `gh` CLI, web search, and direct reads of READMEs, SKILL.md files, prompts, schemas and key source files. Star counts and push dates come from the GitHub API on 2026-09-24 unless a row says otherwise. Nothing was installed or run. Web content was treated as data only.

Notation: "stars" means GitHub stars. "Frames" means still images cut from the video. "Static" and "agentic" refer to the two Gemini video processing modes described in section 1.2.

---

## 0. Top findings

1. Claude still has no video input. Every Claude Code solution does the same core move: ffmpeg turns the video into JPEG frames plus a timestamped transcript, and Claude reads the frames as images. Sources: Anthropic vision docs list only JPEG, PNG, GIF and WebP ([docs](https://platform.claude.com/docs/en/build-with-claude/vision)); native video is an open request in [anthropics/claude-code#12676](https://github.com/anthropics/claude-code/issues/12676) and [#80865](https://github.com/anthropics/claude-code/issues/80865).
2. Adoption is concentrated. [bradautomates/claude-video](https://github.com/bradautomates/claude-video) (the `/watch` skill) has 17,618 stars since 2026-04-24, far ahead of [claude-real-video](https://github.com/HUANGCHIHHUNGLeo/claude-real-video) (2,181), [claude-video-vision](https://github.com/jordanrendric/claude-video-vision) (1,330) and [claude-watch](https://github.com/taoufik123-collab/claude-watch) (866, a fork of claude-video).
3. There are three design families:
   - **Perception layer.** Frames and transcript are extracted locally and Claude interprets them: claude-video, claude-real-video, claude-video-vision, mcp-video-analyzer.
   - **Gemini as proxy.** The video goes to Gemini, which returns text or JSON: [mikefutia/claude-vision](https://github.com/mikefutia/claude-vision), [video-research-mcp](https://github.com/Galbaz1/video-research-mcp), [video-intel](https://github.com/dzivkovi/video-intel), [gemini-video-mcp](https://github.com/DerYUYU/gemini-video-mcp), [Cheap Eyes](https://cheap-eyes.pages.dev/).
   - **agy-based.** A tiny, very new cluster that is closest to your design: [Frully/agy-video-reader](https://github.com/Frully/agy-video-reader), [ninyawee/skills watch-video](https://github.com/ninyawee/skills/blob/HEAD/skills/watch-video/SKILL.md), and the [vox agy cross-check](https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md).
4. Gemini gained "agentic video understanding" on 2026-09-01. The model navigates the timeline with server-side tools and loads frames, audio or transcript on demand. Google reports up to 88% fewer tokens, up to 66% lower cost and up to 7% higher accuracy ([Google blog](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/)). It is only available through the Interactions API with `"processing": "agentic"` ([MarkTechPost](https://www.marktechpost.com/2026/09/04/google-agentic-video-understanding-gemini-flash-models/)). One user measured 85,480 versus 7,416 tokens on the same 15-minute video ([gemini-video-mcp](https://github.com/DerYUYU/gemini-video-mcp)). Nothing documents this mode as reachable through `agy`.
5. Claude image pricing changed. Cost is now per 28x28 patch: `ceil(w/28) x ceil(h/28)` visual tokens. Claude 4.7 and later run a high-resolution tier with a 2576 px long edge and up to 4784 tokens per image. When a request holds more than 20 images, every image must be at most 2000 px ([Anthropic vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)). Most skills still estimate cost with the old `(w x h)/750` rule. Oversized images have broken whole Claude Code sessions ([#66141](https://github.com/anthropics/claude-code/issues/66141), [#65636](https://github.com/anthropics/claude-code/issues/65636)).
6. The failures that recur across shipped tools are silent ones:
   - ffmpeg `-vsync` removal breaks extraction; claude-video has 15+ duplicate issues, for example [#99](https://github.com/bradautomates/claude-video/issues/99).
   - Whisper invents dialogue on silence ([#222](https://github.com/bradautomates/claude-video/issues/222)).
   - Dedup drops text-only UI changes ([crv benchmark](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/benchmark/benchmark.md)).
   - Gemini timestamps drift ([python-genai#1359](https://github.com/googleapis/python-genai/issues/1359), [Google forum](https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501)).
   - Timestamps come back relative when they should be absolute after clipping ([claude-video-vision CHANGELOG](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/CHANGELOG.md), [video-intel#141](https://github.com/dzivkovi/video-intel/issues/141)).
   - `agy` reports success on empty or error output ([vox guards](https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md), [antigravity-cli#902](https://github.com/google-antigravity/antigravity-cli/issues/902)).
7. Things nobody does well:
   - Zooming into a region of the frame at a given time, for arbitrary videos.
   - Checking each claim against the frames at its timestamp.
   - Getting audio through `agy`.
   - Screen-recording specifics: text-fill states, clicks, and alignment with logs.
   - QA of motion and timing in rendered videos.
   - Sub-second precision.
   - Measuring answer accuracy (as opposed to frame counts).

---

## 1. Platform facts that constrain the design

### 1.1 Claude (Anthropic)

Formats and video:
- Supported formats are JPEG, PNG, GIF and WebP ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)).
- For an animated GIF only the first frame is used, so a GIF is not a video workaround. Issue [#80865](https://github.com/anthropics/claude-code/issues/80865) confirms this in Claude Code and adds that GIF palette quantization tinted a dark dashboard green.
- Anthropic's docs contain no video recipe; the community recipe is ffmpeg frames plus a contact sheet ([#80865](https://github.com/anthropics/claude-code/issues/80865)).
- [anthropics/skills](https://github.com/anthropics/skills) ships no video-understanding skill (checked its README on 2026-09-24).

Token math ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)):
- Cost is `ceil(w/28) x ceil(h/28)` visual tokens.
- Standard tier: 1568 px long edge, 1568 tokens maximum.
- High-resolution tier (Claude 4.7 and later): 2576 px long edge, 4784 tokens maximum.
- A 1920x1080 frame costs 1560 tokens on the standard tier (after downscaling to 1456x819) and 2691 tokens on the high-resolution tier.
- High resolution can cost roughly 3x more.

My own arithmetic from that formula:

| Frame size | Tokens |
|---|---|
| 512x288 | 209 |
| 768x432 | 448 |
| 1024x576 | 777 |
| 1280x720 | 1196 |

- A 3x3 contact sheet of 640x360 cells (1920x1080) costs exactly the same as nine separate 640x360 frames on the high-resolution tier (2691 tokens). Sheets save image count and aid comparison, not tokens per pixel.
- On the standard tier the same sheet is downscaled, so each cell shrinks to about 485x273.

Request limits ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)):
- 100 images per API request for 200k-context models, 600 for others, 20 per message on claude.ai.
- More than 20 image blocks in one request, including images from earlier turns and images inside `tool_result`, triggers a stricter limit: each image must be at most 2000 px, or the API returns an `invalid_request_error` that mentions "many-image requests".
- Maximum image size is 10 MB on the direct API and 5 MB on Bedrock and Vertex.

Placement guidance ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)):
- Images before text works best.
- Label each image ("Image 1:", and so on).
- On the API, the Files API avoids resending base64 on every turn.

Stated limitations ([vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)):
- Images under 200 px or low-quality images cause mistakes.
- Counting is approximate.
- Claude cannot tell whether an image is AI-generated.

Claude Code specifics:
- **MCP images arrive as text.** MCP `ImageContent` reaches the model as base64 text, costing about 15k to 25k tokens per image instead of about 1.6k, and the model cannot see it. Closed as not planned: [#31208](https://github.com/anthropics/claude-code/issues/31208). The practical fix is to return file paths and let Claude `Read` them, as analysed in the [vidtheque survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md).
- **One oversized image breaks later images.** A single image over 2000 px can make later valid images fail for the rest of the session ([#66141](https://github.com/anthropics/claude-code/issues/66141)).
- **The resulting retry loop is expensive.** It invalidated the prompt cache and inflated cost about 35x in one session ([#65636](https://github.com/anthropics/claude-code/issues/65636)). See also [#34566](https://github.com/anthropics/claude-code/issues/34566) and [#45543](https://github.com/anthropics/claude-code/issues/45543).
- **Reading too many frames at once fails.** A shipped frame-analyzer agent caps parallel frame reads at 8 because of multi-image limits ([emdashcodes video-frame-analyzer](https://github.com/emdashcodes/claude-code-plugins/blob/HEAD/plugins/video-toolkit/agents/video-frame-analyzer.md)).

### 1.2 Gemini API (what `agy` sits on top of)

Static processing ([video docs](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding)):
- The default is 1 frame per second.
- Frame cost is 66 tokens at low resolution and 258 at default.
- Audio costs 32 tokens per second.
- Totals come to roughly 100 tokens per second (low) or 300 (high).
- With 1M context that is up to 3 hours at low resolution or 1 hour at high.
- "Timestamps are added every second"; prompts should reference `MM:SS`.
- The docs warn that fast action can lose detail at 1 fps.

Gemini 3 media resolution ([docs](https://ai.google.dev/gemini-api/docs/media-resolution)):
- Video frames cost 70 tokens at `low` and `medium` and 280 at `high`.
- Audio costs 25 tokens per second.
- Resolution can be set per media part.
- Use `high` only for dense on-screen text.

Inputs:
- Files API: up to 2 GB (free) or 20 GB (paid).
- Inline: under 100 MB (Interactions doc, [md](https://ai.google.dev/gemini-api/docs/video-understanding.md.txt)) or under 20 MB total request (generateContent doc, [page](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding)).
- YouTube URLs work for public videos only, with 8 hours per day on the free tier.
- Up to 10 videos per request on 2.5 and later.

Clipping and fps:
- `videoMetadata` (`fps`, `start_offset`, `end_offset`) works only with `generate_content`. The Interactions API does not yet support fps or clipping ([Gemini cookbook, Video_understanding.ipynb](https://github.com/google-gemini/cookbook/blob/HEAD/quickstarts/Video_understanding.ipynb)).

Agentic mode:
- Enabled with `"processing": "agentic"` on the video part (Interactions API).
- Models: Gemini 3.8, 3.7 and 3.6 Flash, and 3.5 Flash-Lite ([docs](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding)).
- Responses expose `processing_call` and `processing_result` steps. Video context persists across turns ([cookbook](https://github.com/google-gemini/cookbook/blob/HEAD/quickstarts/Video_understanding.ipynb)).
- Static mode is still preferred for clips under 5 minutes and for frame-precise work. Custom fps is static only ([VP Land](https://www.vp-land.com/stories/gemini-apis-agentic-video-mode-navigates-long-footage-instead-of-sampling-the-whole-clip)).

Reported problems:
- **YouTube-URL transcript drift.** Timestamps drifted by 5 to 10 minutes over a 30-minute video. Downloading and uploading the file fixed it, and an explicit structured time format helped ([python-genai#1359](https://github.com/googleapis/python-genai/issues/1359)).
- **Audio transcript drift in Gemini 3.** Gemini 3 Flash drifted to -157 s over 11:49, and 3.1 Pro to -16 s. Flash Lite held sub-second alignment. Workarounds were 5-minute chunks or a two-pass pipeline ([forum](https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501)).
- **Clipping ignored.** On `gemini-3.7-flash`, `start_offset` did not clip a YouTube video; the model returned the whole video with shifted stamps ([video-intel#141](https://github.com/dzivkovi/video-intel/issues/141)).
- **Premature calls fail.** Calling before the uploaded file reaches `ACTIVE` returns `FAILED_PRECONDITION` ([claude-video-vision#19 fix in CHANGELOG](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/CHANGELOG.md)).

### 1.3 Antigravity CLI (`agy`)

Gemini CLI retirement:
- Gemini CLI stopped serving free, AI Pro and Ultra users on 2026-06-18. `agy` replaces it ([Google Developers blog](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/), [discussion #27274](https://github.com/google-gemini/gemini-cli/discussions/27274)).
- Every Gemini-CLI-based video path from 2025 to mid-2026 is therefore dead for consumer accounts. That includes [jamubc/gemini-mcp-tool](https://github.com/jamubc/gemini-mcp-tool) (2,283 stars), the [eiei114 gemini-video-analysis skill](https://skills.lc/eiei114/skills/eiei114-skills-skills-gemini-video-analysis-skill-md) and the [note.com /dougamite skill](https://note.com/sagyo_eggi/n/nf36652aef2f3?hl=en). Some repos are already marked deprecated, for example [guibarscevicius/gemini-cli-mcp](https://github.com/guibarscevicius/gemini-cli-mcp).

Media in `agy`:
- Official docs: in the prompt panel, `ctrl+v` attaches images and "video recordings" (MP4, MOV, WebM, AVI) ([docs](https://antigravity.google/docs/cli/prompting)).
- An issue states that `@image.png` and `@video.mp4` attach visual media, and asks for the same for audio ([#244](https://github.com/google-antigravity/antigravity-cli/issues/244), open).
- Changelog 1.1.18: audio attachments now recognise wav, mp3, m4a, aac, flac and opus.
- Changelog 1.2.2: `view_file` now rejects files over 100 MB and unsupported binaries ([CHANGELOG](https://github.com/google-antigravity/antigravity-cli/blob/HEAD/CHANGELOG.md)).

Headless behaviour ([CHANGELOG](https://github.com/google-antigravity/antigravity-cli/blob/HEAD/CHANGELOG.md) unless noted):
- 1.2.6 changed the default `-p` timeout from 5 minutes to unlimited.
- 1.2.10 makes a partial response that ends in an error exit with code 3 and print an `AGY_ERROR` line.
- 1.1.18 fixed empty-success in `-p`. The `stream-json` path still ends about 10% of long turns as `SUCCESS` with an empty response ([#902](https://github.com/google-antigravity/antigravity-cli/issues/902)).
- A 452 KB headless prompt was truncated to about 192 KB in the generation context ([#979](https://github.com/google-antigravity/antigravity-cli/issues/979)).
- A 19-minute 720p mp4 deadlocked a conversation and poisoned all later turns in it ([#560](https://github.com/google-antigravity/antigravity-cli/issues/560), open).
- Headless turns abort on a transient 500 or EOF ([#1014](https://github.com/google-antigravity/antigravity-cli/issues/1014)).

Your own test notes (local file `the author's local notes on agy (not published)`, 2026-09-24):
- `view_file` opens an mp4 only when its folder is granted with `--add-dir`.
- Gemini saw about 1 fps (8 of 240 frames), no audio, about 20k tokens per video, plus 18k to 27k tokens of agent overhead per call.
- It invented small sign text until told to write "unreadable".
- A denied tool still exits 0 with SUCCESS, so check `denied_actions`.
- Read `structured_output`, and give every schema field a description.
- The best result was 16 full-resolution frames (2 fps) passed as images, with a deep JSON schema and a "never guess" rule.
- Gemini 3.1 Pro falsely flagged real drone footage as AI morphing.

---

## 2. Project-by-project notes

Each entry uses the fields you asked for. "Not found" means the project does not document it.

### A. Claude Code skills and plugins (local frames plus transcript)

#### A1. bradautomates/claude-video (`/watch`)

- **URL and activity:** https://github.com/bradautomates/claude-video. 17,618 stars, created 2026-04-24, last push 2026-07-01. Many open issues and a community fork ([frinsen/claude-video](https://github.com/frinsen/claude-video)) that carries the fixes.
- **What it does:** a single `/watch <url|path> [question]` command. It fetches captions first, downloads only what it needs, extracts frames, builds a timestamped transcript, and prints frame paths with `t=MM:SS`. Claude then `Read`s every frame in one parallel message ([SKILL.md](https://github.com/bradautomates/claude-video/blob/HEAD/skills/watch/SKILL.md)).
- **Frame sampling:** a `--detail` dial ([README](https://github.com/bradautomates/claude-video/blob/HEAD/README.md)):
  - `transcript`: no frames.
  - `efficient`: keyframes only via `-skip_frame nokey`, capped at 50.
  - `balanced`: ffmpeg `select=gt(scene,0.20)` with `showinfo` to get real PTS, capped at 100.
  - `token-burner`: scene frames, uncapped.
  - Scene modes fall back to a uniform sampler when fewer than 8 cuts are found.
  - The budget is set by duration: about 30 frames for 30 s or less, up to 100 beyond 10 minutes, with a hard cap of 2 fps.
  - Focus mode (`--start/--end`) gets denser budgets.
  - `--timestamps T1,T2` forces extra frames at moments Claude picks after reading the transcript (deictic cues such as "look here"). These frames are pinned against the cap.
  - Dedup: each frame becomes a 16x16 grayscale thumbnail, and a frame is dropped when its mean absolute difference from the last kept frame is 2.0 or less (source: [frames.py](https://github.com/bradautomates/claude-video/blob/HEAD/skills/watch/scripts/frames.py)).
- **Model path:** Claude only, reading JPEGs at 512 px wide by default (1024 for text), clamped to 1998 px tall.
- **Audio:** native captions through yt-dlp first; otherwise mono 16 kHz 64 kbps mp3 sent to Groq `whisper-large-v3` or OpenAI `whisper-1`. Audio over 25 MB is chunked.
- **Prompts and schema:** none. Claude synthesises the answer, and the skill says to summarise rather than paste the transcript.
- **Caching:** none beyond telling Claude not to re-run for follow-ups ("you already have the frames in context"). The work directory is deleted after use.
- **Cost controls:** detail modes and caps. Measured on a 49:08 video: `efficient` 50 frames at about 9.8k image tokens, `balanced` 100 frames at about 19.7k, `transcript` about 26.6k text tokens ([README](https://github.com/bradautomates/claude-video/blob/HEAD/README.md)).
- **Long video:** a "sparse scan" warning past 10 minutes, with advice to re-run focused on a range.
- **Output:** a markdown report on stdout with a header, frame list and transcript.
- **Follow-ups:** re-run with `--start/--end` or `--timestamps`, pointing at the downloaded local file.
- **Verification:** none built in. The upstream has no Whisper confidence flag; the fork's 0.3.0 marks a transcript LOW CONFIDENCE from `no_speech_prob` and `avg_logprob`, or when a phrase loops at regular intervals ([#222 comment](https://github.com/bradautomates/claude-video/issues/222)).
- **Weaknesses** (from issues):
  - `-vsync` was removed in ffmpeg 8/9, which breaks extraction: [#99](https://github.com/bradautomates/claude-video/issues/99), [#117](https://github.com/bradautomates/claude-video/issues/117) and many duplicates.
  - `--fps` combined with the frame cap spends the whole budget on the opening seconds ([#178](https://github.com/bradautomates/claude-video/issues/178)).
  - The 2 fps cap leaves 1 or 2 frames on sub-second clips ([#37](https://github.com/bradautomates/claude-video/issues/37)).
  - Captions are hardcoded to English, so non-English videos get auto-translated tracks ([#153](https://github.com/bradautomates/claude-video/issues/153), [#240](https://github.com/bradautomates/claude-video/issues/240)).
  - Whisper hallucinates on silent videos ([#222](https://github.com/bradautomates/claude-video/issues/222)).
  - Windows encoding crashes ([#61](https://github.com/bradautomates/claude-video/issues/61)).
  - A local whisper.cpp fallback was requested; its timestamped mode loses punctuation unless primed with `--prompt` ([#137](https://github.com/bradautomates/claude-video/issues/137)).

#### A2. HUANGCHIHHUNGLeo/claude-real-video (`crv`)

- **URL and activity:** https://github.com/HUANGCHIHHUNGLeo/claude-real-video. 2,181 stars, last push 2026-09-19. Reached the Hacker News front page ([thread](https://news.ycombinator.com/item?id=48766005)). The CLI, skill and MCP server are free; a paid "Pro" add-on exists.
- **What it does:** extracts scene-aware, deduplicated frames plus a transcript from a URL or file into a folder: `frames/`, `frames.json` (per-frame `timestamp_sec` and `selection_reason`), `transcript.txt/.json` and `MANIFEST.txt` ([README](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/README.md)).
- **Frame sampling:**
  - One chronological `select` pass takes scene changes (`--scene 0.30`) plus a density floor (`--fps-floor 1.0`, at least one frame per N seconds).
  - `--adaptive` compares each frame with a rolling neighbourhood to catch slow morphs.
  - `--text-anchors` forces frames at subtitle cues.
  - `--from/--to` makes ffmpeg seek instead of decoding the whole file.
  - `--frame-width 640` by default.
  - `--max-frames` defaults to `clamp(150, window*1.5, 600)`.
  - Dedup runs three channels against a sliding window of the last 4 kept frames:
    - a global pixel-difference channel (8% threshold);
    - a "settled-local" channel that catches thin strokes, caption swaps and small UI updates once they stop changing;
    - an "action" channel for small fast subjects.
  - `--report` writes `report.html` showing every keep or drop decision ([README](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/README.md)).
- **Model path:** model-agnostic output. The agent skill says to read `MANIFEST.txt` first, then 3x3 contact sheets (`--grid`), and single frames only for close-ups ([skill](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/skills/claude-real-video-for-agents/SKILL.md)).
- **Audio:**
  - Sidecar or embedded subtitles are used when present.
  - Otherwise Whisper; the `[fast]` extra uses faster-whisper gated by Silero VAD, so music or silence yields a "no speech" note instead of invented captions.
  - The `[mlx]` extra runs on the Apple GPU: a 21-minute talk took about 1 minute on an M4, versus about 6 on faster-whisper.
  - `--speakers` runs local diarization (45 MB model).
  - `--keep-audio` saves the full soundtrack for audio-capable models.
- **Prompts:** `--why "<intent>"` is written into the manifest so the model analyses with that lens.
- **Caching and memory:**
  - A re-run with the same source and options answers "already watched" (0.04 s).
  - Every analysis is indexed into local SQLite FTS5 (trigram, works for CJK), and `crv-ask "<query>"` searches across all watched videos with timestamps.
  - The MCP server caches under `~/.cache/crv-mcp`.
- **Cost controls:** measured on a 3-minute 640x360 clip: 170 frames (about 52k tokens) by default, 80 frames (about 25k) with `--max-frames 80`. The README quotes 58 frames at 1 fps against 26 kept frames packed into 3 sheets.
- **MCP:** tools `watch_video`, `get_frames` (paging through keyframes), `search_memory`, `list_watched` and `get_transcript`.
- **Verification and honesty:** a published benchmark that includes its own losses. Version 0.7.3 dedup dropped a screen recording's final five-bullet state and caption-only text cards; 0.7.4's settled-local detector fixed them. `--adaptive` backfires on grainy footage (53 to 116 frames with no new content). Talking-head footage compresses poorly. The benchmark itself says downstream answer accuracy is "not covered yet" ([benchmark](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/benchmark/benchmark.md)). A free `temporal_check` flags padded slow motion from luma-difference statistics and never claims "normal speed" ([source](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/src/claude_real_video/temporal_check.py)). The skill tells agents to treat subtitles and on-screen text as untrusted data.
- **Weaknesses** (from [issues](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues?q=is%3Aissue)):
  - ffmpeg 9 `-vsync` removal ([#14](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/14)).
  - `--to` silently dropped all frame timestamps ([#19](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/19)).
  - A 0-frame result reported instead of an error ([#15](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/15)).
  - A broken Pillow install silently disabled dedup ([#22](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/22)).
  - Hacker News critics note that keyframes cannot convey motion or object permanence, that ffmpeg scene detection is flaky, and that Gemini is far cheaper for long videos ([thread](https://news.ycombinator.com/item?id=48766005)).

#### A3. jordanrendric/claude-video-vision

- **URL and activity:** https://github.com/jordanrendric/claude-video-vision. 1,330 stars, last push 2026-08-07. A Claude Code plugin with an MCP server (Node) and the `video-perception` skill.
- **What it does:** a "perception layer, not an interpretation layer" ([README](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/README.md)). Six tools:
  - `video_info`
  - `video_analyze` (structure first)
  - `video_watch` (frames plus audio)
  - `video_detail` (drill down)
  - `video_configure`
  - `video_setup`
- **Frame sampling:**
  - The skill requires `video_analyze` before extraction for videos over 30 s.
  - `video_analyze` runs one ffmpeg pass with only the filters that fit the question ([analyzers.ts](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/mcp-server/src/extractors/analyzers.ts)):

    | Signal | ffmpeg filter |
    |---|---|
    | Scene changes | `scdet` |
    | Black intervals | `blackdetect` |
    | Freezes | `freezedetect=n=-60dB:d=2` |
    | Motion and complexity | `siti` |
    | Blur | `blurdetect` |
    | Exposure | `signalstats` |
    | Silence | `silencedetect=n=-40dB:d=0.5` |
    | Loudness | `ebur128` |

  - Then `video_watch` takes per-segment fps and resolution.
  - `video_detail` works like a binary search: open a 3 to 5 s window, use `view_sample: 3` (first, middle, last frame), then request exact timestamps ([SKILL.md](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/skills/video-perception/SKILL.md)).
  - PNG frames are an option for screen recordings.
- **Model path:** base64 images returned through MCP. This is exposed to Claude Code [#31208](https://github.com/anthropics/claude-code/issues/31208). An optional `frame-describer` Sonnet subagent turns frames into text to save tokens ([agent](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/agents/frame-describer.md)).
- **Audio:**
  - Backends are the Gemini API, local whisper.cpp or openai-whisper, and the OpenAI API.
  - The Gemini backend uploads a wav, polls until `ACTIVE`, and asks for strict JSON with `transcription[{start,end,text}]` and `audio_tags[{start,end,tag}]` for music and effects. It uses thinking budget 0 and deletes the file afterwards ([gemini-api.ts](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/mcp-server/src/backends/gemini-api.ts)).
  - Long audio is cut at chunk boundaries snapped to the nearest silence midpoint within ±30 s, with overlap ([audio-chunker.ts](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/mcp-server/src/extractors/audio-chunker.ts)).
  - YouTube transcripts prefer manual subtitles, then auto captions, then the backend, and label the provenance as `transcription_source`.
- **Caching:** when `enable_index` is on, sessions are keyed by SHA-256 of the first 64 KB plus the file size. `manifest.json` stores frames by resolution and timestamp, so a changed fps does not re-extract existing timestamps ([design spec](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/docs/superpowers/specs/2026-04-25-smart-video-analysis-design.md)). Sessions expire after 7 days.
- **Cost controls:** `view_sample`, per-segment fps, and resolution guidance (256 to 512 for scans, 1024 and up for text).
- **Output:** JSON (analysis, frames, transcription, tags).
- **Follow-ups:** `video_detail` plus the manifest, so Claude avoids re-requesting frames it already has.
- **Weaknesses:**
  - `video_analyze` hit a 600 s ffmpeg timeout and silently returned empty; decode cost is unbounded at native resolution ([#58](https://github.com/jordanrendric/claude-video-vision/issues/58)).
  - The scenes array truncates around 01:09 on long films ([#47](https://github.com/jordanrendric/claude-video-vision/issues/47)).
  - The `scdet` default surfaces motion noise ([#45](https://github.com/jordanrendric/claude-video-vision/issues/45)).
  - LLMs misuse `end_time` as a duration ([#35](https://github.com/jordanrendric/claude-video-vision/issues/35)).
  - whisper.cpp hallucinates on music-only audio and collapses timestamps to 00:00:00 ([#40](https://github.com/jordanrendric/claude-video-vision/issues/40)).
  - An earlier bug mixed relative audio timestamps with absolute frame timestamps ([CHANGELOG](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/CHANGELOG.md)).
  - The vidtheque survey adds that nothing persists between sessions beyond the 7-day cache ([survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md)).

#### A4. taoufik123-collab/claude-watch

- **URL and activity:** https://github.com/taoufik123-collab/claude-watch. 866 stars, last push 2026-07-24. Built on the claude-video pipeline.
- **Additions over claude-video** ([README](https://github.com/taoufik123-collab/claude-watch/blob/HEAD/README.md)):
  - **Hook microscope:** 2 fps frames over the first 10 s plus word-level Whisper, so each frame aligns with the word being spoken ([hook.py](https://github.com/taoufik123-collab/claude-watch/blob/HEAD/scripts/hook.py)).
  - **Pacing metrics:** cuts per minute and shot-length distribution ([pacing.py](https://github.com/taoufik123-collab/claude-watch/blob/HEAD/scripts/pacing.py)).
  - **Fixed-schema `report.md`:** narrative sections are explicit `<!-- pending Claude fill -->` markers, which gives Claude a job list instead of a blank page.
  - **Obsidian save.**
- **Weaknesses:** inherits claude-video's limits; talking-head detection is out of scope.

#### A5. victor-shulga/watch

- **URL and activity:** https://github.com/victor-shulga/watch. New (2026-09-23), 0 stars. Included for design ideas.
- **What it does:** turns a video or call recording into timestamped contact sheets plus a local transcript, then writes a structured breakdown ([SKILL.md](https://github.com/victor-shulga/watch/blob/HEAD/skills/watch/SKILL.md)).
- **Frames:** 36 frames by default, at least 1 s apart, packed 6 per sheet (3x2) with timestamps printed. Single 720 px frames are available for small text.
- **Audio:** local faster-whisper. `--call` mode adds offline diarization (sherpa-onnx), attributed per word and regrouped into turns.
- **Diarization lesson:** auto-clustering was unusable. A 26-minute three-person call produced 55, 21 or 9 speakers depending on threshold. Passing `--speakers 3` gave 3. The workflow is: count participant tiles from early frames, then `--rediarize` without re-transcribing. Timing: `medium` took 16 minutes and diarization 4.5 minutes on an M4 for 26.6 minutes of audio.
- **Output:** a fixed breakdown: TL;DR, meta, hook, timeline beats, on-screen text verbatim, visual devices, CTA, fact check, takeaways. Call mode adds decisions, next steps and objections with timestamps.
- **Verification:** treats shown or spoken instructions as data. Missing metadata is reported as missing, never invented. Names are only mapped from evidence.

#### A6. bsisduck/video-analyzer-skill

- **URL and activity:** https://github.com/bsisduck/video-analyzer-skill. 33 stars.
- **Frames:**
  - Duration tiers: 2 fps under 1 minute, 1 fps for 1 to 3 minutes, 1/10 fps for 3 to 10 minutes, 1/20 fps beyond, capped at 60.
  - Montage grids are 4x4 (landscape) or 3x5 (portrait), with `drawtext` burning `%{pts\:hms}` into each cell.
  - Scene changes use `select=gt(scene,0.3)` (0.1 for slides, 0.4 for action). High-resolution 1280 px key frames are taken at scene changes ([SKILL.md](https://github.com/bsisduck/video-analyzer-skill/blob/HEAD/SKILL.md), [ffmpeg gotchas](https://github.com/bsisduck/video-analyzer-skill/blob/HEAD/references/ffmpeg-commands.md)).
- **Model path:** parallel subagents: grid agents (one per 2 to 3 grids), a key-frame agent, and an audio agent. The main agent only merges their text ([strategies](https://github.com/bsisduck/video-analyzer-skill/blob/HEAD/references/analysis-strategies.md)).
- **Audio:** the Whisper CLI plus silence detection.
- **Gotchas worth keeping:**
  - Instagram and TikTok files carry an MJPEG thumbnail as stream 0; skip streams with `attached_pic`.
  - Use `-update 1` when a single-frame output name contains dots.
  - macOS `grep` has no `-P`.
- **Weakness:** the claim that grids "save 60-70% tokens" comes from smaller cells, not from gridding itself (see 1.1 math).

#### A7. fabriqaai/ffmpeg-analyse-video-skill

- **URL:** https://github.com/fabriqaai/ffmpeg-analyse-video-skill. 31 stars.
- **Idea:** images live only in disposable subagent contexts, and the main agent reads text reports. The authors claim this saves about 90% of context.
- **Frames by duration** ([SKILL.md](https://github.com/fabriqaai/ffmpeg-analyse-video-skill/blob/HEAD/SKILL.md)):
  - Under 60 s: 1 frame per 2 s.
  - 1 to 10 minutes: scene detection at 0.3.
  - 10 to 30 minutes: keyframes.
  - Over 30 minutes: the ffmpeg `thumbnail` filter, capped at about 60 frames.
- **Weaknesses:** uses the deprecated `-vsync vfr`. Scene and keyframe outputs are numbered files with no timestamps unless PTS is captured separately.

#### A8. mugnimaestra/video-frames-skill

- **URL:** https://github.com/mugnimaestra/video-frames-skill. 11 stars.
- **Idea:** presets are `efficient` (768 px), `balanced` (1024), `detailed` (1568) and `ocr` (1568 with grayscale, contrast 1.3 and an unsharp mask). `--target-model` sizing is available, along with `--min-scene-interval` ([SKILL.md](https://github.com/mugnimaestra/video-frames-skill/blob/HEAD/skills/video-frames/SKILL.md)). A cross-provider token spec sheet is included ([llm-image-specs.md](https://github.com/mugnimaestra/video-frames-skill/blob/HEAD/skills/video-frames/references/llm-image-specs.md)).
- **Weakness:** the Claude figures still use the `/750` formula and the 1568 px ceiling, which is outdated for Claude 4.7 and later (section 1.1).

#### A9. emdashcodes video-toolkit (plugin)

- **URL:** https://github.com/emdashcodes/claude-code-plugins/tree/HEAD/plugins/video-toolkit. The repo has 13 stars.
- **Ideas:**
  - A Gemini audio pass returns music segments as JSON (`has_music`, `music_segments[start,end]`), which then feed Shazam identification ([analyze_audio_gemini.py](https://github.com/emdashcodes/claude-code-plugins/blob/HEAD/plugins/video-toolkit/skills/video-toolkit/scripts/analyze_audio_gemini.py)).
  - A frame-analyzer agent batches reads and never loads more than 8 frames in parallel. It always reads the first and last frame, and cites frames as `frame_0015 @ 45.2s` ([agent](https://github.com/emdashcodes/claude-code-plugins/blob/HEAD/plugins/video-toolkit/agents/video-frame-analyzer.md)).

#### A10. Newuxtreme/watch-video-skill

- **URL:** https://github.com/Newuxtreme/watch-video-skill. 69 stars. It vendors claude-video.
- **Ideas:** triggers only on the literal slash command, to avoid accidental token burn. A plain YouTube question should be answered from the transcript alone. Output is a notes file (TL;DR, timeline, key quotes, visual notes) ([SKILL.md](https://github.com/Newuxtreme/watch-video-skill/blob/HEAD/SKILL.md)).

### B. Gemini-as-proxy skills and MCP servers

#### B1. mikefutia/claude-vision (`video-analyzer` skill)

- **URL:** https://github.com/mikefutia/claude-vision. 102 stars.
- **Model path:** Gemini (default `gemini-3-flash-preview`). Files up to 18 MB go inline; larger files go through the Files API, polling up to 300 s for `ACTIVE`. `--fps` is passed as `VideoMetadata` ([analyze_video.py](https://github.com/mikefutia/claude-vision/blob/HEAD/scripts/analyze_video.py)).
- **Prompt:** a structured markdown report (summary, scene-by-scene `MM:SS`, audio, visual details, key moments) with anti-hallucination rules:
  - Report only what is present.
  - Never invent a narrator, speaker or voiceover.
  - Say "No speech detected" or "Audio track is silent" when true.
  - Label inferences "(inferred)".
  - Treat silent screen recordings as normal.
- **Weaknesses:** free-text markdown, no schema, no caching, no chunking. `disable-model-invocation: true` means it runs only when invoked explicitly ([SKILL.md](https://github.com/mikefutia/claude-vision/blob/HEAD/SKILL.md)).

#### B2. DerYUYU/gemini-video-mcp

- **URL:** https://github.com/DerYUYU/gemini-video-mcp. 1 star, created 2026-09-20. Included for its measurements.
- **Findings** ([README](https://github.com/DerYUYU/gemini-video-mcp/blob/HEAD/README.md)):
  - Sending `processing` to `generateContent` returns 400.
  - Same question on the same 15-minute video: 85,480 tokens static versus 7,416 agentic, with better coverage.
  - A 2-minute range cost 11,293 tokens at static `low` and 35,922 at `high`. `low` still read an on-screen repository name.
  - On a 51-second reel, agentic and static cost about the same, but the agentic answer was richer.
  - Token usage is reported on every call.

#### B3. Galbaz1/video-research-mcp

- **URL:** https://github.com/Galbaz1/video-research-mcp. 23 stars, last push 2026-07-22. A 51-tool plugin.
- **Ideas:**
  - Files over 20 MB are uploaded and context-cached, so follow-up turns reuse the cache ([README](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/README.md), [context_cache.py](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/src/video_research_mcp/context_cache.py)).
  - Multi-turn `video_create_session` and `video_continue_session`. When an answer cites a moment, Claude extracts that exact frame with ffmpeg and embeds it in the notes ([video-chat.md](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/commands/video-chat.md)).
  - A metadata-optimizer step writes a video-specific extraction prompt from title and tags ([prompts/video.py](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/src/video_research_mcp/prompts/video.py)).
  - Structured output via Pydantic models; timestamps are described as "precise, not rounded" ([models/video.py](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/src/video_research_mcp/models/video.py)).
  - Deterministic quality gates after the model: timestamp format, monotonic order, at least 90% coverage of the video's duration, and a minimum length for key points ([validation.py](https://github.com/Galbaz1/video-research-mcp/blob/HEAD/src/video_research_mcp/validation.py)).
- **Weakness:** API key only. Context caching depends on a minimum-token check.

#### B4. dzivkovi/video-intel

- **URL:** https://github.com/dzivkovi/video-intel. 6 stars. Its README reports daily use since March 2026 on 2,400+ videos.
- **Ideas:**
  - **Fused transcript:** speech lines interleaved with `SCREEN [01:09-01:31] [diagram]: ...` blocks. Speakers are identified with an evidence field (for example, a name card at 00:15) ([README](https://github.com/dzivkovi/video-intel/blob/HEAD/README.md)).
  - **One Gemini call** returns `transcripts`, `screen_content` (typed as slide, diagram, code, terminal, ui_demo, chart, table, whiteboard, text_overlay or other; verbatim text; a `code` field) and `speakers` ([prompts/transcript.md](https://github.com/dzivkovi/video-intel/blob/HEAD/prompts/transcript.md)).
  - **Absolute-timestamp invariant:** every timestamp must be absolute even for clipped chunks, and chunk-relative stamps are rejected downstream.
  - **Single model:** an ADR replaced Whisper, pyannote, Claude and Gemini with one Gemini Flash call ([ADR-0003](https://github.com/dzivkovi/video-intel/blob/HEAD/docs/adr/ADR-0003-single-model-replaces-pipeline.md)).
  - **Chunking plan:** merge with offsets, deduplicate speakers, add a coverage table, and keep partial results with a visible warning ([plan](https://github.com/dzivkovi/video-intel/blob/HEAD/docs/brainstorms/2026-04-26-lex-fridman-feasibility-and-chunking-plan.md)).
- **Costs:** about $0.15 to $0.25 per 15-minute video for mind maps, and about $0.33 per video-hour for fused transcripts.
- **Pitfall found here:** `start_offset` did not clip YouTube input on 3.7 Flash ([#141](https://github.com/dzivkovi/video-intel/issues/141)).

#### B5. Cheap Eyes

- **URL:** https://cheap-eyes.pages.dev/. A local script plus a skill.
- **Ideas:** Gemini 3.5 Flash or Flash-Lite describes the video (inline under 19 MB, else the Files API). Claude reasons over the text only. An `--opus` escalation sends 6 evenly spaced frames, or exact seconds via `--at 12,41.5,88`, scaled to a 1568 px long edge.
- **Cost:** a 3-minute recording costs "low single-digit cents" on Flash.

#### B6. Gemini CLI era (now retired for consumer accounts)

- [note.com /dougamite](https://note.com/sagyo_eggi/n/nf36652aef2f3?hl=en) (2026-05-16): Claude Code calls `gemini -p` for a timestamped analysis, then extracts frames with ffmpeg at the moments Gemini named and reads them.
- The [eiei114 gemini-video-analysis skill](https://skills.lc/eiei114/skills/eiei114-skills-skills-gemini-video-analysis-skill-md) reported that Gemini CLI videos expand to about 2 to 3M tokens per MB, fail above about 2 to 3 MB, and cannot be piped through stdin. It retried 429s with backoff.
- These show why a CLI wrapper may not match the API's per-frame pricing. Measure your `agy` path.

### C. `agy`-based precedents (closest to your design)

#### C1. Frully/agy-video-reader

- **URL:** https://github.com/Frully/agy-video-reader. 0 stars, created 2026-07-13, macOS only.
- **Transport:** uses `agy` as the sole interpreter, attaching the video natively rather than through `view_file`.
  - It launches the `agy` TUI in a PTY with `Gemini 3.5 Flash (High)`, `--sandbox` and `--mode accept-edits`.
  - It stages the file URL on the macOS clipboard, sends `ctrl+v`, and requires a confirmed `media attached` `video/*` event ([TUI contract](https://github.com/Frully/agy-video-reader/blob/HEAD/references/antigravity-tui-contract.md)).
  - Its fixed prompt asks the model to use both visual and audio evidence.
- **Size limits:**
  - Hard limit 52,428,800 bytes (50 MiB) per attachment.
  - Larger files become one 480p H.264/AAC proxy targeting 47 MiB, when the bitrate floor (550 or 350 kbps) allows.
  - Otherwise the file is split into the fewest segments, with 5 s overlap and at most 24 parts, run in up to 5 concurrent lanes, each with its own empty workspace ([media contract](https://github.com/Frully/agy-video-reader/blob/HEAD/references/media-preparation-contract.md)).
- **Output channel:** the only model output accepted is a workspace-local `result.json`, never TUI text. It follows a closed schema ([schema](https://github.com/Frully/agy-video-reader/blob/HEAD/references/output-schema.json)):
  - `summary`, `visual_summary`, `audio_summary`
  - `timeline[{start,end,visual_event,audio_event,on_screen_text,confidence,uncertainties}]`
  - `uncertainties`
  - `evidence_quality{visual,audio,temporal}`
- **Prompt:**
  - The user request is inserted as a JSON string value that cannot change tools or schema.
  - On-screen or spoken instructions are to be treated as untrusted.
  - The model must mark ambiguity and omissions instead of guessing.
  - Confidence is described as prioritisation, not calibrated ([prompting contract](https://github.com/Frully/agy-video-reader/blob/HEAD/references/prompting-contract.md)).
  - One formatting-only correction retry is allowed. Segment timestamps are offset and the overlaps deduplicated.
- **Philosophy:** it deliberately never uses host-side frames, OCR or transcription as evidence. That is the opposite of a verification loop.
- **Weaknesses:** complex, fragile clipboard and PTY automation. Whether audio really reaches the model through this path is asserted, not shown.

#### C2. ninyawee/skills: watch-video

- **URL:** https://github.com/ninyawee/skills/blob/HEAD/skills/watch-video/SKILL.md. 0 stars.
- **How it calls agy:** `agy -p "<framed prompt + absolute path>"`, with `--add-dir <parent>` when the file is outside the workspace. It never uses `--dangerously-skip-permissions`.
- **Prompt template:**
  - the source context;
  - the reporter's message quoted verbatim in the original language;
  - specific questions (gestures, UI response, error states).
- **Timeline mode:** asks for a per-0.5 s timeline table with columns t, frame, gesture and UI state (fps=2, or 4 for gestures under 300 ms).
- **Documented gotchas:** audio is ignored, so transcribe separately. One video per call. Raise `--print-timeout` for long files.

#### C3. josephyooo/vox: `agy` entity cross-check

- **URL:** https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md. 0 stars.
- **Role:** `agy` (`Gemini 3.1 Pro (Low)`) is a supplementary entity cross-check, never the source of record for quotes, timestamps or sentiment.
- **Prompt:** asks for exactly three sections (spoken, on-screen, entities), each with an explicit empty marker such as `(no speech)`.
- **Guards learned in live runs:**
  1. A hard external timeout of about 150 s, because `agy` hung for about 42 minutes on an audio/video desync, past its own `--print-timeout`.
  2. Success judged by output, not exit code: `agy` returned exit 0 with an error body about a timeout, and truncated outputs lost sections.
  3. Retry once, because about a third of clean runs flaked.
- **Reconciliation rules:**
  - Name-spelling precedence runs: on-screen name card read by vision, then `agy`, then the ASR transcript.
  - `agy`-only entities are added at lower confidence and must be corroborated.
  - `agy` never creates a quote and never deletes a claim.
  - Unavailability is recorded as a note and never halts the run.

### D. MCP servers that expose frames and transcripts

#### D1. guimatheus92/mcp-video-analyzer

- **URL:** https://github.com/guimatheus92/mcp-video-analyzer. 76 stars, last push 2026-09-20.
- **Tools** ([README](https://github.com/guimatheus92/mcp-video-analyzer/blob/HEAD/README.md)):
  - `analyze_video`
  - `analyze_videos` (batch, resumable through sidecars)
  - `get_transcript`
  - `get_metadata`
  - `get_frames` (scene or dense 1 fps)
  - `analyze_moment` (burst frames, filtered transcript and OCR for a range)
  - `get_frame_at`
  - `get_frame_burst` (N frames in a narrow window for motion)
- **Ideas:**
  - Perceptual dedup (dHash plus Hamming distance).
  - Scene detection falls back to uniform sampling when only an overlay changes.
  - OCR through tesseract.js, with grayscale, 2x upscale, contrast normalisation and sharpening, run on the full-resolution frame while the emitted copy is capped (800 px by default).
  - An annotated timeline merges transcript, frames and OCR.
  - A disk cache keyed by `mtime:size` plus parameters.
  - A `fields` filter and `brief|standard|detailed` levels.
  - Downloads capped at 1080p.
- **Weaknesses:** Tesseract is the weakest OCR option for video frames (per the [vidtheque survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md)), and there is no cross-video index.

#### D2. kwacky1/video-understanding-mcp

- **URL:** https://github.com/kwacky1/video-understanding-mcp. 0 stars, 2026-09-10. Included for its design.
- **Ideas** ([README](https://github.com/kwacky1/video-understanding-mcp/blob/HEAD/README.md)):
  - Evidence is "bounded and reproducible".
  - The sampler combines the first frame, source-time cadence, scene changes and `mpdecimate` near-duplicate removal. It never uses the `fps` filter, which rewrites timestamps.
  - `provenance.json` records each frame's source PTS, timebase, duration, selection reason and SHA-256.
  - At most 24 frames; inline images are off by default (at most four at 512 px).
  - The transcript cache key includes the input SHA-256, parameters, the whisper binary fingerprint and the model SHA-256.
  - Content-addressed caches with an age and size LRU (14 days, 5 GB).
  - Allowed-root path policy and symlink-escape protection; a doctor command.

#### D3. YouTube transcript and yt-dlp MCPs

- [jkawamoto/mcp-youtube-transcript](https://github.com/jkawamoto/mcp-youtube-transcript) (484 stars): `get_timed_transcript` with a `next_cursor` pagination and `--response-limit` so long transcripts do not blow the context.
- [anaisbetts/mcp-youtube](https://github.com/anaisbetts/mcp-youtube) (546 stars): a single yt-dlp subtitle tool.
- [kevinwatt/yt-dlp-mcp](https://github.com/kevinwatt/yt-dlp-mcp) (281 stars): read-only and idempotent tool annotations plus hard output truncation, which the vidtheque survey recommends copying ([survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md)).
- All of these are text only; none looks at pixels.

#### D4. Knowledge-base style video MCPs

- [0xchamin/mcptube](https://github.com/0xchamin/mcptube) (158 stars): scene-change frames are captioned by a vision LLM and compiled into a "wiki" with SQLite FTS5. Keyword search only, and no license.
- [woosal1337/media-mcp](https://github.com/woosal1337/media-mcp) (8 stars): returns absolute frame paths instead of base64, which suits Claude Code (summary from the [vidtheque survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md)).

### E. Hosted platforms with agent connectors

#### E1. Twelve Labs

- **Links:** [MCP blog](https://www.twelvelabs.io/blog/twelve-labs-mcp-server) and [Claude Code plugin docs](https://docs.twelvelabs.io/docs/advanced/claude-code-plugin).
- **How it works:** videos are indexed first (`/twelvelabs:index-video`). Search is backed by the Marengo embeddings and returns timestamps; analysis, summaries and Q&A are backed by Pegasus.
- **Pattern:** chain search, then analysis on the returned clips.
- **Weaknesses:** hosted, paid, an index step before any answer, and a closed model.

#### E2. VideoDB

- **Links:** [Director](https://github.com/video-db/Director) (1,540 stars), [agent-toolkit and MCP](https://github.com/video-db/agent-toolkit), [MCP docs](https://docs.videodb.io/pages/mcp).
- **How it works** (per the ECC `videodb` skill in your plugin cache, `~/.claude/plugins/cache/ecc/ecc/2.2.0/skills/videodb/SKILL.md`, and its upstream docs):
  - `index_spoken_words`, then `index_scenes` (shot-based extraction plus a describe prompt).
  - Semantic search with `score_threshold`.
  - `results.compile()` returns a playable stream as evidence.
- **Pattern:** "playable evidence links" for each hit.
- **Weaknesses:** hosted, needs an API key, cloud upload.

#### E3. Jam (bug recordings)

- **Link:** [MCP docs](https://jam.dev/docs/debug-a-jam/mcp).
- **Tools:**
  - `analyzeVideo`
  - `getVideoTranscript` (WebVTT)
  - `getVideoChapters`
  - `getFrames` (specific moments, ranges, or an overview grid)
  - `getUserEvents` (clicks, inputs and navigation in plain language)
  - `getConsoleLogs`
  - `getNetworkRequests`
- **Lesson:** reliable repro steps come from captured browser telemetry, not from pixels alone.
- **Weakness:** needs Jam's Chrome extension at recording time.

#### E4. screenpipe

- **Link:** https://github.com/screenpipe/screenpipe (21,683 stars).
- **How it works:**
  - Event-driven capture: a screenshot on app switch, click, typing pause or scroll, paired with the accessibility tree, with OCR only as a fallback.
  - Local Whisper with diarization.
  - SQLite FTS5 search.
  - An MCP server (`npx screenpipe-mcp`) ([README](https://github.com/screenpipe/screenpipe/blob/HEAD/README.md)).
- **Lesson:** event-driven capture beats fixed-interval capture for screen work.

#### E5. Builder.io Agent-Native Clips

- **Link:** [blog](https://www.builder.io/blog/agent-native-clips-captures-browser-errors) (2026-09-01).
- **What it does:** a Chrome-extension screen recorder that attaches console errors, failed requests and status codes as JSON beside the video, so an agent can write repro steps with expected and actual behaviour. A related [dev.to post](https://dev.to/infracore/turn-screen-recordings-into-bug-reports-agents-can-act-on-1o5m) shows that without such tooling, people do this by hand and skip it under pressure.

### F. General packages and notebooks

#### F1. byjlw/video-analyzer

- **URL:** https://github.com/byjlw/video-analyzer. 1,592 stars, created 2024-11.
- **Pipeline:**
  - OpenCV grayscale `absdiff` scoring (threshold 10) on an adaptive sample.
  - Keep the top-N most different frames (default 60 per minute, at most 30).
  - Caption each frame with a local vision LLM (Llama 3.2 Vision via Ollama, or any OpenAI-compatible API), passing the previous frame's analysis as context.
  - Reconstruct the video description from the captions plus the Whisper transcript ([DESIGN.md](https://github.com/byjlw/video-analyzer/blob/HEAD/docs/DESIGN.md)).
- **Honesty:** the design doc lists its own limitations: frames between samples are missed, rapid sequences get one frame, and even sampling can skip significant changes.
- **Extra:** a `video-analyzer-tune` package tunes the prompts.

#### F2. simonw/llm-video-frames and Simon Willison's video scraping

- **Links:** [llm-video-frames](https://github.com/simonw/llm-video-frames) (52 stars) and its [blog post](https://simonwillison.net/2025/May/5/llm-video-frames/).
- **What it does:** turns a video into frame attachments at `fps=N`. With `timestamps=1` it overlays the filename and time on each frame, so the model can cite times. Example cost: GPT-4.1-mini, 3 frames, 7,072 input tokens.
- **Video scraping** ([post](https://simonwillison.net/2024/Oct/17/video-scraping/)): a 35-second screen recording was turned into JSON through Gemini 1.5 Flash for 11,018 tokens, under 0.1 cent. Simon spot-checked the output by eye because LLM extraction cannot be trusted at 100%.

#### F3. Gemini cookbook

- **Link:** [quickstarts/Video_understanding.ipynb](https://github.com/google-gemini/cookbook/blob/HEAD/quickstarts/Video_understanding.ipynb).
- **Contents:**
  - Example prompts for scene captions with timecodes, text extraction into tables, screen-recording summaries with timestamps, and "find all instances with timestamps" on YouTube.
  - An agentic mode section.
  - Custom fps only through `generate_content`.

#### F4. OpenAI cookbook

- **Link:** [GPT_with_vision_for_video_understanding.ipynb](https://github.com/openai/openai-cookbook/blob/HEAD/examples/GPT_with_vision_for_video_understanding.ipynb).
- **Method:** OpenCV reads every frame and a strided subset is sent as base64 images with no timestamps. This is the naive baseline.

### G. Render-QA helpers (motion graphics)

#### G1. HeyGen HyperFrames

- **Link:** https://github.com/heygen-com/hyperframes (52,796 stars).
- **What it does:** `npx hyperframes check --snapshots` writes annotated overview frames plus a crop for every finding that has a bounding box. `snapshot --zoom "#selector"` or `--zoom "x,y,w,h" --zoom-scale 2` crops a region to verify a defect, and `snapshot --at t1,t2` captures proof frames ([reference](https://github.com/heygen-com/hyperframes/blob/HEAD/skills/hyperframes-cli/references/lint-validate-inspect.md)).
- **Significance:** this is the only region zoom in the survey, and it works only for HyperFrames' own compositions.

#### G2. Remotion

- The official [remotion-dev/skills](https://github.com/remotion-dev/skills) (4,702 stars) cover code patterns and show how to render stills and specific frames (`npx remotion still`, `render --frames=0,30,90`) ([render reference](https://github.com/remotion-dev/skills/blob/HEAD/skills/remotion-best-practices/remotion-render/REFERENCE.md)). They include no verification loop.
- The third-party [haidrrrry/claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill) (189 stars) makes a render, inspect frames, fix, re-render loop mandatory ([README](https://github.com/haidrrrry/claude-remotion-skill/blob/HEAD/README.md)).
- Failure evidence from real sessions:
  - All automated checks (lint, contrast, motion, frame snapshots, silence and clipping detection) passed while TTS inserted a garbled word in about 13 of 15 clips. The defect was found only by listening, and Whisper word confidence could isolate it ([#86973](https://github.com/anthropics/claude-code/issues/86973)).
  - Static screenshots of an animated hero caught dark mid-animation frames and led to a confident false defect report ([#67279](https://github.com/anthropics/claude-code/issues/67279)).

### H. Research patterns worth borrowing

- **[VideoAgent](https://arxiv.org/abs/2403.10517)** (2024): an LLM agent iteratively picks which frames to look at. It reached 54.1% on EgoSchema and 71.3% on NExT-QA using about 8 frames on average. The lesson is to search, not to sample densely.
- **[Deep Video Discovery](https://arxiv.org/abs/2505.18079)** (Microsoft, 2025, [code](https://github.com/microsoft/DeepVideoDiscovery)): agentic search tools over a multi-granular clip database for hour-long videos, state of the art on LVBench.
- **Gemini agentic video** (1.2) is the productised version of the same idea.
- The **[vidtheque landscape survey](https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md)** (2026-08-08) is a useful secondary source for OCR, shot detection and ASR choices:
  - PySceneDetect, with TransNetV2 for gradual transitions.
  - The Katna idea of choosing the sharpest frame by Laplacian variance, because frames at a cut are often blurry.
  - RapidOCR or PaddleOCR over Tesseract.
  - whisperX for word-level alignment.

---

## 3. Synthesis

### 3.1 Techniques worth copying

| # | Technique | Who does it | Why it matters for your skill |
|---|---|---|---|
| 1 | Plan with cheap ffmpeg analysis before choosing frames: scene, black, freeze, silence, loudness, blur | claude-video-vision (`video_analyze`) | Freeze, black and silence intervals are QA findings in themselves, and they tell you where to look. |
| 2 | Hybrid candidate frames: scene cuts, a density floor, transcript-cue frames, and pinned user or model timestamps | claude-real-video (scene plus floor), claude-video (`--timestamps` cues), crv `--text-anchors` | No single sampler covers fast cuts, static slides and spoken "look here" moments. |
| 3 | Dedup against the last kept frame (not the previous frame), with a sliding window and a local "settled change" detector | claude-video (MAD vs last kept), crv 0.7.4 (settled-local, action channel) | Keeps budget for distinct content while keeping text-fill and small UI changes, the classic screen-recording loss. |
| 4 | Source-PTS timestamps and provenance per frame: `select` plus `showinfo`, no timestamp-rewriting `fps` filter, frames.json or provenance.json with reason and hash | kwacky1, claude-video, crv | Every claim can be traced to an exact source time and re-extracted. |
| 5 | Burned-in timecode on frames or clips | bsisduck (`drawtext %{pts\:hms}`), llm-video-frames (`timestamps=1`) | Gemini and Claude can read the time instead of guessing it, which counters timestamp drift. |
| 6 | Focused re-runs: clip a window and sample denser inside it, keeping timestamps absolute | claude-video (`--start/--end`), crv (`--from/--to`), mcp-video-analyzer (`analyze_moment`, `get_frame_burst`) | Answers "what happens at 2:30" without re-watching everything. |
| 7 | Binary-search drill-down: view 3 frames of a window, then exact timestamps | claude-video-vision (`video_detail`, `view_sample`) | Keeps Claude's image count low. |
| 8 | Frame and resolution manifest reused across calls | claude-video-vision (timestamp plus resolution keys), crv ("already watched") | Follow-ups cost nothing, and you never re-read a frame already in context. |
| 9 | Content-addressed caches keyed by input hash, parameters, tool version and model hash, with LRU retention | kwacky1 | Safe reuse, with no stale answers after the model or version changes. |
| 10 | Captions first, local ASR second, VAD gate and `no_speech_prob` flags | claude-video (captions first), crv (Silero VAD), claude-video fork (LOW CONFIDENCE) | Stops invented dialogue on silent screen recordings and music. |
| 11 | Pin diarization speaker count from visual evidence (count tiles), then re-diarize without re-transcribing | victor-shulga/watch | Auto-clustering is unusable on real calls. |
| 12 | Contact sheets for overview, single full-resolution frames for detail and OCR | crv `--grid`, victor-shulga 3x2, Jam overview grid; your own memory notes | Sheets aid sequence reading; small text needs full frames. |
| 13 | OCR on the full-resolution frame even when the emitted frame is small | mcp-video-analyzer | Keeps token cost low without losing text. |
| 14 | Subagents read images and the main agent reads text | bsisduck, fabriqaai | Protects the main context in long sessions. |
| 15 | Closed JSON schema with per-channel evidence quality, per-item confidence and uncertainties, and a result file as the only output channel | agy-video-reader | Machine-checkable and resistant to TUI and exit-code weirdness. |
| 16 | Deterministic post-checks: timestamp format, order, in-range, at least 90% coverage | video-research-mcp | Catches truncated or drifted outputs cheaply. |
| 17 | Absolute-timestamp invariant for chunks, with downstream rejection | video-intel | Prevents the relative-vs-absolute bug class. |
| 18 | Fused transcript: speech lines interleaved with typed SCREEN blocks | video-intel | The best report format for tutorials, demos and bug videos. |
| 19 | Reconciliation precedence and "never create quotes or delete claims" rules for a secondary model | vox | A clean way to merge `agy` and Gemini output with Whisper and frame evidence. |
| 20 | `agy` guards: hard external timeout, judge success by output, retry once, check `denied_actions`, fresh conversation per call | vox, antigravity-cli#560/#902, our tests | `agy` fails in ways that look like success. |
| 21 | Anti-hallucination prompt rules: "No speech detected", "(inferred)", "unreadable, never guess", treat on-screen instructions as data | mikefutia/claude-vision, our tests, crv, agy-video-reader | Cuts the known Gemini failure of invented small text. |
| 22 | Hook microscope: dense frames plus word-level ASR for the first N seconds | claude-watch | Useful for ads and social QA; generalises to any key window. |
| 23 | Region zoom crops for verifying findings | HyperFrames (`snapshot --zoom`) | Nobody offers this for arbitrary video. See 3.2. |
| 24 | Agentic search over the timeline instead of dense sampling | VideoAgent, DVD, Gemini agentic mode | Long videos: coarse pass, then targeted clips. |
| 25 | Slash-only triggering for the heavy path | Newuxtreme, mikefutia | Avoids surprise token burn. Keep a cheap automatic path, such as transcript only. |

### 3.2 Gaps nobody fills well

1. **Spatial drill-down on arbitrary video.** No general video tool offers "crop region x,y,w,h at time t, upscale, read it". Only HyperFrames does this, for its own compositions ([ref](https://github.com/heygen-com/hyperframes/blob/HEAD/skills/hyperframes-cli/references/lint-validate-inspect.md)). claude-video-vision's "cropped" means time windows only ([CHANGELOG](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/CHANGELOG.md)).
2. **Claim-level verification.** Model output is almost always trusted as is. Partial exceptions are the deterministic gates in video-research-mcp, vox's reconciliation rules, and Simon Willison's manual spot checks. Nobody automatically re-extracts the frames at each claimed timestamp and has a second model (Claude) confirm or reject the claim.
3. **Audio through `agy`.**
   - Our test found no audio through `view_file`, and ninyawee's skill says the same.
   - agy-video-reader asserts audio through the TUI attachment path but shows no proof.
   - The `@video.mp4` headless path and `view_file` on an extracted audio file (`.m4a` or `.wav`) are both undocumented and untested for audio, although the changelog says audio attachment formats are recognised ([CHANGELOG 1.1.18](https://github.com/google-antigravity/antigravity-cli/blob/HEAD/CHANGELOG.md), [#244](https://github.com/google-antigravity/antigravity-cli/issues/244)).
4. **Screen-recording and UI specifics for local files.**
   - Text filling into a static layout is lost by most dedup, and was lost by crv before 0.7.4 ([benchmark](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/benchmark/benchmark.md)).
   - Cursor position, click moments and hover states are not detected by any local tool.
   - Aligning with logs (console, network, Playwright traces) exists only in hosted recorders that capture telemetry: Jam, Builder Clips and screenpipe.
5. **Motion and timing QA for rendered or generated video.** No tool detects:
   - easing and timing mistakes;
   - elements appearing a frame late;
   - audio/video sync errors;
   - garbled TTS words ([#86973](https://github.com/anthropics/claude-code/issues/86973));
   - false "defects" from frames captured mid-animation ([#67279](https://github.com/anthropics/claude-code/issues/67279)).

   Gemini can also falsely flag real footage as AI-generated (our tests), and Anthropic says Claude cannot detect AI-generated images ([docs](https://platform.claude.com/docs/en/build-with-claude/vision)).
6. **Sub-second and frame-exact questions.** The defaults are 1 fps (Gemini) and a 2 fps cap (claude-video, [#37](https://github.com/bradautomates/claude-video/issues/37)). Burst tools exist only in mcp-video-analyzer and your `ffmpeg fps=N` scripts.
7. **Evaluation.** Nobody publishes answer accuracy. crv measures frame counts and says accuracy is "not covered yet"; everyone else shows demos.
8. **Cost telemetry in the agent loop.** Only gemini-video-mcp reports tokens per call. With `agy` adding 18k to 27k tokens of agent overhead per call (our tests), budgeting per call matters.
9. **Timestamp truth across chunks.** Bugs appeared in claude-video-vision (fixed), crv [#19](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/19) and video-intel [#141](https://github.com/dzivkovi/video-intel/issues/141). No shared convention exists.

### 3.3 Pitfalls and failure modes reported in issues and discussions

ffmpeg and extraction:
- **`-vsync` removal.** `-vsync` has been removed in newer ffmpeg (issues cite 8.x and 9.x); use `-fps_mode`. See claude-video [#99](https://github.com/bradautomates/claude-video/issues/99) and [#163](https://github.com/bradautomates/claude-video/issues/163) plus about 15 duplicates, and crv [#14](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/14).
- **fps plus frame cap stops early.** `fps=` combined with `-frames:v N` stops after `N/fps` seconds, silently covering only the head of the video ([#178](https://github.com/bradautomates/claude-video/issues/178)).
- **The `fps` filter rewrites timestamps.** Take PTS from `select` plus `showinfo`, or record the source PTS ([kwacky1 README](https://github.com/kwacky1/video-understanding-mcp/blob/HEAD/README.md)).
- **Full-resolution analysis passes hit timeouts** and silently return nothing ([claude-video-vision#58](https://github.com/jordanrendric/claude-video-vision/issues/58)). Downscale for analysis and treat a timeout as an error.
- **Scene thresholds are content-dependent.** Suggested values are 0.1 for slides, 0.3 in general and 0.4 for action ([bsisduck](https://github.com/bsisduck/video-analyzer-skill/blob/HEAD/references/ffmpeg-commands.md)). A low `scdet` value surfaces motion noise ([#45](https://github.com/jordanrendric/claude-video-vision/issues/45)), and scene detection is called flaky on Hacker News ([thread](https://news.ycombinator.com/item?id=48766005)).
- **Social media downloads carry a thumbnail stream.** An MJPEG `attached_pic` sits at stream 0 ([bsisduck](https://github.com/bsisduck/video-analyzer-skill/blob/HEAD/references/ffmpeg-commands.md)).
- **Silent zero-frame or zero-timestamp results.** Seen in crv [#15](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/15) and [#19](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/issues/19). Always assert counts and ranges.

Frames and dedup:
- **Dedup misses small or local changes.** It drops text-card swaps, text filling into a screen, and thin strokes. A 16x16 signature is blind to them ([crv benchmark](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/benchmark/benchmark.md)).
- **Tiny fast subjects vanish.** A subject covering under 1% of the frame disappears under percentage-based dedup (crv 0.7.16 note in the [README](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/README.md)).
- **Adaptive detection backfires on noise.** On grainy footage it fires on grain (+119% tokens), and a gesturing speaker defeats dedup ([benchmark](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/benchmark/benchmark.md)).
- **Keyframes do not show motion.** Keyframes cannot convey motion or object permanence. One Hacker News commenter found plain descriptions beat grids for animations ([thread](https://news.ycombinator.com/item?id=48766005)).
- **Slow motion trades detail for frames.** A 4x slow-motion copy passed more frames but less detail per frame, and tracking got worse (our tests).

Audio and ASR:
- **Whisper invents speech on silence and music.** The fixes are VAD gating and per-segment confidence ([claude-video#222](https://github.com/bradautomates/claude-video/issues/222), [claude-video-vision#40](https://github.com/jordanrendric/claude-video-vision/issues/40), [crv README](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/README.md)).
- **Wrong caption language.** English-only caption selection returns machine-translated tracks ([#153](https://github.com/bradautomates/claude-video/issues/153)).
- **Punctuation loss.** whisper.cpp in timestamped mode may drop punctuation; prime it with `--prompt` ([#137](https://github.com/bradautomates/claude-video/issues/137)).
- **Diarization needs the speaker count.** Pass N ([victor-shulga](https://github.com/victor-shulga/watch/blob/HEAD/skills/watch/SKILL.md)).
- **Gemini transcript timestamps drift** on long audio (see 1.2).

Claude side:
- **Image size limits.** Stay at or under 2000 px and never let an oversized image into the session ([#66141](https://github.com/anthropics/claude-code/issues/66141), [#65636](https://github.com/anthropics/claude-code/issues/65636)).
- **MCP images become text.** Return paths, not MCP images ([#31208](https://github.com/anthropics/claude-code/issues/31208)).
- **Too many images in one go.** Do not flood 100 frames in one turn. Batch the reads and prefer subagents.
- **Outdated cost estimates.** The high-resolution tier costs up to about 3x the old estimates ([docs](https://platform.claude.com/docs/en/build-with-claude/vision)).

Gemini side:
- **1 fps loses fast action** ([docs](https://ai.google.dev/gemini-api/docs/generate-content/video-understanding)).
- **Timestamp drift** in YouTube-URL input and in long audio ([#1359](https://github.com/googleapis/python-genai/issues/1359), [forum](https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501)).
- **Offsets are unreliable** on YouTube input ([video-intel#141](https://github.com/dzivkovi/video-intel/issues/141)). Cut the file yourself instead.
- **Files API state polling is required** ([claude-video-vision CHANGELOG](https://github.com/jordanrendric/claude-video-vision/blob/HEAD/CHANGELOG.md)).
- **Output truncation on long transcripts.** video-intel skips transcripts over 2 hours unless chunked ([plan](https://github.com/dzivkovi/video-intel/blob/HEAD/docs/brainstorms/2026-04-26-lex-fridman-feasibility-and-chunking-plan.md)).

`agy` side:
- **Hangs and poisoned conversations.** `agy` has hung for about 42 minutes on audio/video-desynced media ([vox](https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md)), and a large mp4 deadlocked and poisoned a conversation ([#560](https://github.com/google-antigravity/antigravity-cli/issues/560)).
- **Failure disguised as success.** Exit 0 with an error body ([vox](https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md)); SUCCESS with an empty response in about 10% of long `stream-json` turns ([#902](https://github.com/google-antigravity/antigravity-cli/issues/902)); a denied tool reported as SUCCESS (our tests).
- **Input truncation.** Headless input was cut from 452 KB to about 192 KB ([#979](https://github.com/google-antigravity/antigravity-cli/issues/979)). Do not inline big transcripts; pass files.
- **Size limits.** `view_file` limit is 100 MB ([CHANGELOG 1.2.2](https://github.com/google-antigravity/antigravity-cli/blob/HEAD/CHANGELOG.md)). Attachments are limited to 50 MiB in the TUI path ([agy-video-reader](https://github.com/Frully/agy-video-reader/blob/HEAD/references/antigravity-tui-contract.md)).
- **No default timeout.** `-p` is unlimited since 1.2.6, so set `--print-timeout` and an outer kill ([CHANGELOG](https://github.com/google-antigravity/antigravity-cli/blob/HEAD/CHANGELOG.md)).
- **Workspace access.** Needs `--add-dir`. Avoid `--dangerously-skip-permissions`; under it the agent went looking through shell history (our tests).
- **Invented text.** Gemini invents small on-screen text unless told to write "unreadable" (our tests).

Agent behaviour:
- **LLMs misuse range parameters.** They confuse `end` as an absolute time versus a duration ([#35](https://github.com/jordanrendric/claude-video-vision/issues/35)). Make APIs explicit, as in `--start 12.0 --end 18.0`, and validate.
- **The easy path wins over written rules.** The model picks screenshots over recordings despite rules; one team had to add a PreToolUse hook to enforce it ([#67279](https://github.com/anthropics/claude-code/issues/67279)).
- **The model may skip frames entirely.** It can answer from title or transcript alone. Newuxtreme's skill forbids writing the summary before reading frames ([SKILL.md](https://github.com/Newuxtreme/watch-video-skill/blob/HEAD/SKILL.md)).

### 3.4 Concrete recommendations for your skill

#### Architecture

Build a hybrid of the perception layer and a Gemini proxy with verification:
1. ffmpeg does all cutting, sampling and measuring.
2. `agy` (Gemini) is the first-pass watcher, run on small, prepared inputs.
3. Claude is the judge that verifies claims against extracted frames.

No surveyed project closes this loop. Keep everything file-based: return paths, never MCP images.

#### Command set

Expose these as one script with subcommands, and have SKILL.md route to them.

| Command | What it does | Borrowed from |
|---|---|---|
| `probe <file>` | ffprobe JSON (duration, fps, VFR flag, rotation, streams, `attached_pic`, audio present), SHA-256, and a cache directory | kwacky1, bsisduck |
| `scan <file>` | One downscaled ffmpeg pass (for example 640 px): scene cuts, `blackdetect`, `freezedetect`, `silencedetect`, `ebur128`, optional `blurdetect`. Writes `analysis.json`. Hard timeout; a timeout counts as an error | claude-video-vision |
| `frames <file> --mode scene\|uniform\|keyframe\|burst\|at` with `--start --end --max --res --times` | Source-PTS timestamps and `frames.json` with reason and hash. Dedup against last kept frames plus a local-change check for UI. Chooses the sharpest frame within about 0.5 s after each cut. Allows more than 2 fps in bursts under about 5 s | crv, claude-video, kwacky1, Katna idea |
| `sheet --grid 3x3 [--range]` | Labelled contact sheets for overview only | crv, victor-shulga |
| `zoom --t 12.40 --region x,y,w,h [--scale 2]` | Crop and upscale for text or detail verification. Fills gap 1 | HyperFrames, as a pattern |
| `clip --start --end [--timecode]` | Accurate re-encoded cut with burned absolute timecode, ready for `agy` | bsisduck, llm-video-frames |
| `transcribe [--engine local\|gemini] [--words] [--speakers N]` | Local whisper (mlx-whisper, whisper.cpp or faster-whisper) with VAD; per-segment `no_speech_prob` and `avg_logprob` flags; word-level timestamps optional; Gemini audio only as a cross-check | crv, claude-video fork, victor-shulga, vox |
| `ask <file> "<question>" [--start --end] [--model]` | Prepares a window (clip plus frames) and runs a single `agy` call against a Q&A schema. The answer must cite timestamps and evidence | Cheap Eyes, video-research-mcp |
| `analyze <file> --profile summary\|bug-repro\|ui-qa\|motion-qa\|meeting` | Full pipeline: probe, scan, chunk plan, per-chunk `agy` JSON, merge, verify, report | agy-video-reader, video-intel |
| `verify <report.json>` | Deterministic gates first, then evidence checks on sampled or all findings: extract frames at t±0.5 s (and a zoom for text claims) for Claude to confirm | video-research-mcp, vox |
| `cache ls\|prune` | Inspect and prune the cache | kwacky1 |

#### Frame strategy defaults

- **Candidate set:**
  - scene cuts (0.25 to 0.3 on a downscaled pass);
  - a density floor (one frame per 2 to 5 s, depending on duration);
  - freeze-end and black-end boundaries;
  - transcript-cue times;
  - user or model-pinned times.

  Dedup against the last 4 kept frames with a local-change detector. Always keep the first and last frames. Budget by purpose, not only by duration.
- **Resolution for Claude:** 768 to 1024 px long edge for general reading and 1568 px for text (zoom crops are better). Never exceed 2000 px. At most 20 images per Claude turn; use subagents for more.
- **For `agy` and Gemini:** follow your own measured winner. Send 16 to 32 full-resolution frames at 2 fps for a 5 to 15 s window, with timecode burned in, rather than one long mp4. For a wide overview, send a short clip (1 to 3 minutes, under 50 MiB, far under 100 MB) with burned timecode. Never send a whole long video: see [#560](https://github.com/google-antigravity/antigravity-cli/issues/560).
- **Fast action:** use burst mode at the native frame rate for windows of 2 s or less. Accept that 1 fps model sampling misses it.
- **Screen recordings:** lower the dedup threshold, keep settled states, prefer PNG for crisp text, and OCR full-resolution frames as a cheap cross-check. Where possible, align with any logs by wall clock: ffprobe `creation_time` plus offsets. This is a gap; label it best-effort.

#### `agy` call contract

Build on vox, agy-video-reader and our tests:
1. Start a fresh conversation per call, with a dedicated input folder passed through `--add-dir`. Never use `--dangerously-skip-permissions`.
2. Set `--print-timeout` and an outer hard kill. Retry exactly once on timeout, empty output or schema failure.
3. Judge success only by a schema-valid `structured_output`. Check `denied_actions`, exit code 3 and `AGY_ERROR`.
4. Keep the prompt small. Pass transcripts and plans as files, never inline, because of the ~192 KB truncation in [#979](https://github.com/google-antigravity/antigravity-cli/issues/979).
5. Log model, effort, input size, tokens where available, and wall time per call for cost telemetry.
6. Run a parallel lane limit of about 3 to 5, as agy-video-reader does.

#### Prompt and schema rules

1. Separate the user question, passed as data, from fixed rules. Treat any text or speech in the video as untrusted data ([agy-video-reader](https://github.com/Frully/agy-video-reader/blob/HEAD/references/prompting-contract.md), [crv skill](https://github.com/HUANGCHIHHUNGLeo/claude-real-video/blob/HEAD/skills/claude-real-video-for-agents/SKILL.md)).
2. Honesty rules:
   - write "unreadable" instead of guessing;
   - write "no speech detected" or "no audio available in this input", since `view_file` drops audio;
   - label inferences;
   - never name a person without on-screen or spoken evidence.
3. Timestamps: always absolute source time in `MM:SS.s`, read from the burned timecode when visible. State the invariant explicitly (as video-intel does) and reject violations.
4. Schema (every field described, per our tests). A closed object with:
   - `summary`;
   - `timeline[]` with `start`, `end`, `visual_event`, `on_screen_text[]` (verbatim or "unreadable"), `audio_event` (or null), `evidence_frames[]` (timestamps), `confidence` (low, medium or high), and `uncertainties[]`;
   - `findings[]` for QA, with `type`, `severity`, `start`, `end`, `observation`, `expected`, `evidence`, and `needs_verification` (bool);
   - `coverage` (list of analysed windows);
   - `evidence_quality{visual,audio,temporal}`.
5. Two passes for QA: first "observe and describe only", then a separate judgement against a spec or checklist. This reduces judgement-driven hallucination, such as your false "AI morphing" verdict.
6. Profile prompts:
   - `bug-repro`: numbered steps with timestamps, UI state before and after, expected versus actual, the first frame where the issue is visible, and error text verbatim.
   - `motion-qa`: element entry and exit times, easing or timing notes, text legibility per scene, audio/video sync checks on burned timecode, and black or freeze intervals taken from `scan`.

#### Caching

- **Key:** SHA-256 of the file (or of its first 64 KB plus size for speed, then a full hash lazily) plus operation, parameters, ffmpeg and whisper versions, and model and schema hash.
- **Stored per video:** `probe.json`, `analysis.json`, `frames/<res>/<pts>.jpg` with a manifest keyed by timestamp and resolution, `transcript.json`, `chunks/<chunk-hash>.<model>.<prompt-hash>.json`, `verify.json`, `report.md`.
- **Behaviour:** an "Already analysed" short-circuit for identical requests. Retention by age and size (for example 14 days and 5 GB, as in kwacky1).
- **Safety:** never delete the user's source file (claude-video [#80](https://github.com/bradautomates/claude-video/issues/80) wiped a source that sat inside `--out-dir`).
- **Gemini context caching:** API only (video-research-mcp); it does not apply to `agy`.

#### Report format

Write `report.json` for machines and `report.md` for people:
1. **Header:** file, duration, hash, analysed windows and coverage %, models and versions, what the input lacked (for example "agy input had no audio; transcript from local whisper"), and warnings.
2. **Fused timeline:** `[mm:ss.s]` speech lines (with transcript source and confidence) interleaved with `SCREEN [a-b] [type]` blocks and scan events (black, freeze, silence).
3. **Findings table:** severity, time range, claim, evidence frame paths or zoom paths, and verification status (verified, unverified or contradicted).
4. **Uncertainties and coverage gaps.**
5. **Appendix:** frames index and cost log.

Follow-ups reuse the cache: `ask` and `zoom` against the same hash.

#### Verification loop

1. Run deterministic gates: timestamps parse, fall within the duration, are ordered, and meet the coverage threshold.
2. For each finding or timeline item flagged `needs_verification`, plus a random 10 to 20% sample of the rest, extract frames at t-0.5, t and t+0.5 s (and a `zoom` for text claims). Claude reads them and marks each claim verified or contradicted.
3. Reconcile sources with fixed precedence:
   - on-screen text read from zoomed frames beats Gemini text;
   - the local transcript beats Gemini for quotes;
   - Gemini-only claims stay lower confidence.

   Nothing is deleted silently.
4. Flag the Whisper transcript LOW CONFIDENCE when most segments exceed the `no_speech_prob` threshold or a phrase repeats at regular intervals.

#### Tests to run before committing to the design

These are open questions the survey could not answer:
1. Does `agy -p "@/abs/clip.mp4 ..."` (the `@` syntax) attach the video natively in headless mode, and does Gemini then hear the audio? Compare against `view_file`.
2. Does `view_file` on an extracted `.m4a` or `.wav` give a timestamped transcript through `agy` (changelog 1.1.18 suggests audio attachments work)?
3. Is burned-in timecode read reliably by Gemini 3.8 Flash in `view_file` video mode versus frames-as-images mode? Measure timestamp error in seconds.
4. What are token and overhead costs per call for clip versus frames, so the budget table is based on measurements? Our tests already give about 20k tokens per video plus 18k to 27k tokens of overhead.
5. Screen-recording fixture set (text fill-in, dropdown revert, toast, spinner, sub-second click): measure recall of each frame strategy against a hand-labelled truth. crv's benchmark is the template, but add answer accuracy.

---

## 4. Source index (primary reads)

Skills and plugins:
- https://github.com/bradautomates/claude-video (README, skills/watch/SKILL.md, scripts/frames.py, issues #37 #61 #99 #137 #178 #222)
- https://github.com/HUANGCHIHHUNGLeo/claude-real-video (README, benchmark/benchmark.md, skills/claude-real-video-for-agents/SKILL.md, src/claude_real_video/temporal_check.py, issues)
- https://github.com/jordanrendric/claude-video-vision (README, skills/video-perception/SKILL.md, agents/frame-describer.md, mcp-server/src/extractors/analyzers.ts, audio-chunker.ts, backends/gemini-api.ts, design spec, issues)
- https://github.com/taoufik123-collab/claude-watch
- https://github.com/victor-shulga/watch
- https://github.com/bsisduck/video-analyzer-skill
- https://github.com/fabriqaai/ffmpeg-analyse-video-skill
- https://github.com/mugnimaestra/video-frames-skill
- https://github.com/emdashcodes/claude-code-plugins/tree/HEAD/plugins/video-toolkit
- https://github.com/Newuxtreme/watch-video-skill

Gemini-proxy tools:
- https://github.com/mikefutia/claude-vision
- https://github.com/DerYUYU/gemini-video-mcp
- https://github.com/Galbaz1/video-research-mcp
- https://github.com/dzivkovi/video-intel
- https://cheap-eyes.pages.dev/

`agy` precedents:
- https://github.com/Frully/agy-video-reader
- https://github.com/ninyawee/skills/blob/HEAD/skills/watch-video/SKILL.md
- https://github.com/josephyooo/vox/blob/HEAD/skills/vox-video/references/agy-crosscheck.md
- https://github.com/google-antigravity/antigravity-cli (CHANGELOG, issues #244 #560 #902 #979 #1014)
- https://antigravity.google/docs/cli/prompting

MCP servers:
- https://github.com/guimatheus92/mcp-video-analyzer
- https://github.com/kwacky1/video-understanding-mcp
- https://github.com/jkawamoto/mcp-youtube-transcript
- https://github.com/anaisbetts/mcp-youtube
- https://github.com/kevinwatt/yt-dlp-mcp
- https://github.com/0xchamin/mcptube
- https://github.com/T0mSIlver/vidtheque/blob/HEAD/research/landscape-survey-video-mcp.md

Hosted platforms:
- https://www.twelvelabs.io/blog/twelve-labs-mcp-server
- https://docs.twelvelabs.io/docs/advanced/claude-code-plugin
- https://github.com/video-db/Director
- https://github.com/video-db/agent-toolkit
- https://jam.dev/docs/debug-a-jam/mcp
- https://github.com/screenpipe/screenpipe
- https://www.builder.io/blog/agent-native-clips-captures-browser-errors

Packages, notebooks and render QA:
- https://github.com/byjlw/video-analyzer
- https://github.com/simonw/llm-video-frames
- https://simonwillison.net/2025/May/5/llm-video-frames/
- https://simonwillison.net/2024/Oct/17/video-scraping/
- https://github.com/google-gemini/cookbook/blob/HEAD/quickstarts/Video_understanding.ipynb
- https://github.com/openai/openai-cookbook/blob/HEAD/examples/GPT_with_vision_for_video_understanding.ipynb
- https://github.com/heygen-com/hyperframes/blob/HEAD/skills/hyperframes-cli/references/lint-validate-inspect.md
- https://github.com/remotion-dev/skills
- https://github.com/haidrrrry/claude-remotion-skill

Platform docs:
- https://platform.claude.com/docs/en/build-with-claude/vision
- https://ai.google.dev/gemini-api/docs/generate-content/video-understanding
- https://ai.google.dev/gemini-api/docs/video-understanding.md.txt
- https://ai.google.dev/gemini-api/docs/media-resolution
- https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/
- https://www.marktechpost.com/2026/09/04/google-agentic-video-understanding-gemini-flash-models/
- https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/

Issues:
- https://github.com/anthropics/claude-code/issues/12676
- https://github.com/anthropics/claude-code/issues/80865
- https://github.com/anthropics/claude-code/issues/31208
- https://github.com/anthropics/claude-code/issues/66141
- https://github.com/anthropics/claude-code/issues/65636
- https://github.com/anthropics/claude-code/issues/86973
- https://github.com/anthropics/claude-code/issues/67279
- https://github.com/googleapis/python-genai/issues/1359
- https://discuss.ai.google.dev/t/bug-gemini-3-flash-and-3-1-pro-progressive-timestamp-drift-in-audio-transcription/129501

Research:
- https://arxiv.org/abs/2403.10517
- https://arxiv.org/abs/2505.18079
- https://news.ycombinator.com/item?id=48766005

Local:
- `the author's local notes on agy (not published)` (your `agy` test notes, 2026-09-24)
- `~/.claude/plugins/cache/ecc/ecc/2.2.0/skills/videodb/SKILL.md`
