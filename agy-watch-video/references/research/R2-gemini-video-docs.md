# R2: Gemini video and audio understanding, official docs (checked 2026-09-24)

Research date: 2026-09-24. Every page below was fetched that day. "Updated" is the page's own
"Last updated" stamp when it shows one.

How this was gathered:

- Google developer pages (ai.google.dev, docs.cloud.google.com, firebase.google.com, geminicli.com,
  antigravity.google) were rendered in a browser and read as full page text, so numbers are exact.
  Items marked **(summary)** came through a summarizing fetch only and deserve a second look.
- Caution: the `.md.txt` mirrors on ai.google.dev can lag the live page. Example: the mirror of the
  Interactions overview still says "Beta" and "video metadata not supported", while the live page
  (updated 2026-09-23) says the Interactions API has been Generally Available since June 2026.
  Numbers here come from live pages unless flagged.
- Licensing: ai.google.dev, docs.cloud.google.com and firebase.google.com pages state CC BY 4.0
  (code Apache 2.0), so short verbatim quotes are used with attribution. Antigravity docs and blogs,
  DeepMind PDFs, GitHub threads and forum posts are paraphrased, with only very short phrases quoted.
- Nothing was installed, run, signed into or posted.

---

## 0. What matters for the skill (short version)

1. **Native Gemini video input (API)**: static mode samples **1 FPS** by default, adds a timestamp
   every second, and carries the audio track ("processed at 1Kbps (single channel)"). Custom fps
   exists only in static mode; the v1beta API schema allows **fps in (0.0, 24.0]**, default 1.0.
2. **Tokens (Gemini 3)**: video frames cost **70 tokens/frame** at default/low/medium and
   **280 at high**; audio **25 tokens/s** (media-resolution page). Older docs text still says
   66/258 per frame and 32 tokens/s. Rule of thumb: about **100 tokens/s** at default, about
   **300 tokens/s** at high. A 1M-context model fits about 3 h (default) or 1 h (high) of video.
3. **Agentic video mode** (Gemini 3.8/3.7/3.6 Flash and 3.5 Flash-Lite only, not 3.1 Pro): the model
   pulls transcript, frames at adaptive fps and audio on demand; Google claims up to 88% fewer tokens,
   up to 66% lower cost, up to 7% higher accuracy. It is an API feature; nothing in the Antigravity
   docs says agy uses it.
4. **Timestamps**: ask for `MM:SS` (Gemini API). Vertex/GEAP adds `H:MM:SS` over one hour and
   `MM:SS.sss` when sampling above 1 FPS.
5. **Prompt rules from Google**: one video per prompt; video part first, text after; be specific;
   ask for the output format (or use a JSON schema); ask it to describe before reasoning; slow down
   or raise fps for fast action; use `high` media resolution only for on-screen text.
6. **Audio**: Gemini transcribes with MM:SS timestamps, diarizes speakers, detects emotion and
   understands non-speech sounds (birdsong, sirens), but GEAP lists non-speech recognition as a
   known weak spot. Bengali (`bn`) is in the official Gemini language list; the dedicated
   Gemini 3.5 Transcribe model lists `bn-BD` and `bn-IN`.
7. **Gemini CLI is no longer an option on a consumer login**: since **2026-06-18** it stopped serving
   free, Google AI Pro and Ultra individual accounts; only API keys, Vertex and Code Assist
   Standard/Enterprise remain. With a key, `@video.mp4` is sent as native `inlineData`
   (video plus audio at default 1 FPS, no fps control), capped at 20 MB by the CLI.
8. **Antigravity (agy)** is the only official consumer-login path. Docs cover headless mode,
   `--json-schema`, model slugs and quotas, but say nothing about how `view_file` turns a video into
   frames. Changelog items show agy can read audio files natively (.wav fix, audio attachments),
   rejects files over 100 MB in `view_file`, and (desktop app 2.11.0) added a `MediaResolution`
   option to `view_file`.
9. **Your 20k-token observation fits a fixed image budget**: agy headless has about 10.4k tokens of
   built-in overhead (docs example: `input_tokens` 10,415 for a one-line question). The remaining
   ~9k matches 8 frames x 1,120 tokens (Gemini 3 default image) and also 32 frames x 280 tokens
   (Gemini 3 low image) = 8,960 in both cases. Hypothesis, not documented: agy sends frames as
   images under a fixed budget, so more frames means lower resolution per frame.
10. **Your "no audio" result is inconclusive**: the clip was silent, so the model would report no
    audio either way. Retest with a clip that has speech or a clear sound.
11. **Quota**: Antigravity Gemini models share one pool "drawn down as per API pricing" (May 2026),
    Pro refreshes every five hours until a weekly cap, free tier refreshes weekly. Video tokens
    therefore eat quota at API-price weight, and Flash is cheaper than Pro per token.
12. **Terms of Service risk**: the Antigravity FAQ says using third-party software (it names
    Claude Code) with an Antigravity login violates its ToS and recommends a Gemini Enterprise or
    AI Studio API key for third-party agents. Calling the official `agy` binary in documented
    headless mode is not the same as reusing its tokens in another client, but the wording is broad.
    Keep an API-key path in the design.

---

## 1. Gemini API video understanding

Main source: https://ai.google.dev/gemini-api/docs/video-understanding (Updated 2026-09-23).
Legacy generateContent version: https://ai.google.dev/gemini-api/docs/generate-content/video-understanding
(Updated 2026-09-16). Vertex, now called Gemini Enterprise Agent Platform (GEAP):
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/video-understanding
(Updated 2026-09-22).

### 1.1 Input paths and size limits

Table on the Gemini API video page (2026-09-23):

| Input method | Max size | Recommended use (quoted) |
|---|---|---|
| File API | 20GB (paid) / 2GB (free) | "Large files (100MB+), long videos (10min+), reusable files." |
| Cloud Storage Registration | 2GB (per file, no storage limits) | "Large files (100MB+), long videos (10min+), persistent, reusable files." |
| Inline Data | < 100MB | "Small files (<100MB), short duration (<1min), one-off inputs." |
| YouTube URLs | N/A | "Public YouTube videos." |

Conflicting inline limits (all official, all current):

- Same video page: "Always use the Files API when the total request size (including the file, text
  prompt, system instructions, etc.) is larger than 20 MB" and inline is "suitable for shorter videos
  under 20MB total request size."
- Files API page (https://ai.google.dev/gemini-api/docs/files, Updated 2026-09-23): "Always use the
  Files API when the total request size ... is larger than 100 MB. For PDF files, the limit is 50 MB."
- Audio page (Updated 2026-09-23): "Maximum request size is 20 MB total (including prompts and all files)".
- Safe design rule: inline only below 20 MB total request.

Files API facts (Files API page, 2026-09-23): "store up to 20 GB of files per project, with a per-file
maximum size of 2 GB. Files are stored for 48 hours." and "The Files API is available at no cost in all
regions where the Gemini API is available." (The video page's "20GB (paid)" per-file figure conflicts
with the Files API page's 2 GB per file.)

Videos per request: "For Gemini 2.5 and later models, you can upload a maximum of 10 videos per
request." (video page). GEAP table: "Maximum number of videos per prompt: 10". Firebase AI Logic
(https://firebase.google.com/docs/ai-logic/input-file-requirements, Updated 2026-09-24): 10 video files,
1 audio file per request.

### 1.2 Formats

Gemini API: `video/mp4`, `video/mpeg`, `video/mov`, `video/avi`, `video/x-flv`, `video/mpg`, `video/webm`,
`video/wmv`, `video/3gpp`. GEAP list: `video/x-flv`, `video/quicktime`, `video/mpeg`, `video/mpegs`,
`video/mpg`, `video/mp4`, `video/webm`, `video/wmv`, `video/3gpp`.

### 1.3 Static vs agentic processing

Static (default, all models), video page "Technical details":
> "Frames are extracted at 1 FPS and placed into context (default for all models). Audio is processed
> at 1Kbps (single channel). Timestamps are added every second."

Agentic (Gemini 3.8 Flash, 3.7 Flash, 3.6 Flash, 3.5 Flash Lite only):
> "The model dynamically navigates the video timeline, loading only the content it needs based on the
> prompt. Up to 88% more token-efficient and ~7% higher quality on long-form content."

Google's guidance on the same page: "As a general guideline, start with agentic mode"; use static for
"Latency-sensitive queries on short clips (under 5 minutes), or cases where frame-level precision
across the entire clip is needed." Agentic "may slightly increase Time to First Token (TTFT) on short
clips (<5 minutes)".

How to enable:

- Interactions API (now the recommended API): on the video input item, `"processing": "agentic"`.
  Verify via `interaction.steps` containing `processing_call` and `processing_result`.
- generateContent (legacy): `media_processing="AGENTIC"` on the Part (REST: `"media_processing": "AGENTIC"`
  next to `file_data`). Verify via `tool_call`/`tool_response` parts "with the MEDIA_PROCESSING tool type".
- GEAP: `media_processing="agentic"` (options "agentic", "static"); "Agentic video understanding is set to
  STATIC or disabled by default for all supported models." GEAP marks it Preview.
- Modes can be mixed per video in one request.

Billing: "Navigation reasoning tokens ... are accounted as thought tokens (`total_thought_tokens`), while
frames, audio, and transcript loaded on demand are accounted as tool use tokens (`total_tool_use_tokens`)."
Tokens page (https://ai.google.dev/gemini-api/docs/tokens, Updated 2026-09-23): "a 1-hour lecture that
would use ~1.08M tokens in static mode might use ~108K tokens". Pricing page note (Updated 2026-09-24):
agentic sampling depth "may exceed 1 FPS for detailed visual segments".

How it works (AI Studio developer guide by Patrick Loeber and Maarten Grootendorst,
https://aistudio.google.com/learn/agentic-video-understanding-with-gemini, no date shown; paraphrased):
the API passes a pointer to the video, the model plans, then fetches transcript first, then only the
needed time window at an adaptive frame rate (the guide gives 5 to 10 FPS for fast motion and 0.1 FPS
for skimming), and pulls the audio track when tone or sound matters. Billing covers only the media
slices it actually loads; Batch API works at 50% cost. Recommended for videos over about 5 minutes and
for "fine-grained temporal tasks"; static for clips under 5 minutes.

Launch blog (https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/,
2026-09-01, Rohan Doshi and Mario Lucic, paraphrased): launched on 3.7 Flash, 3.6 Flash, 3.5 Flash-Lite;
up to 88% fewer tokens, up to 66% lower cost, up to 7% better accuracy (measured with 3.7 Flash); no
extra fee; listed uses include sub-second moment retrieval, needle-in-haystack search over multi-hour
video, and "counting of actions and objects over time"; also rolling out in the Gemini app.

Long requests: use streaming or background execution, because synchronous calls "can exceed connection
or authentication token validity windows, which may surface as unexpected 401 Unauthorized or timeout
errors." Multi-turn: stateful mode (`previous_interaction_id`) keeps video context; stateless mode needs
the returned steps sent back.

### 1.4 Custom frame rate and clipping

- Only in static mode: "These customization options are only supported when processing the video in
  "static" mode."
- Allowed fps range, from the v1beta API schema (https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta,
  `VideoMetadata.fps`): "Optional. The frame rate of the video sent to the model. If not specified, the
  default value will be 1.0. The fps range is (0.0, 24.0]."
- generateContent (legacy page, 2026-09-16): `videoMetadata` / `video_metadata` with `fps`,
  `start_offset`, `end_offset`. Example values in the page code **(summary)**: `VideoMetadata(fps=5)` and
  `start_offset='1250s', end_offset='1570s'`. Guidance: "You might want to set low FPS (< 1) for long
  videos. This is especially useful for mostly static videos (e.g. lectures). Use a higher FPS for videos
  requiring granular temporal analysis, such as fast-action understanding or high-speed motion tracking."
- Interactions API (current video page code): `"processing": {"type": "static", "fps": 0.5}` and
  `"processing": {"type": "static", "start_offset": 1200, "end_offset": 1500}`. The page does not state
  the units; the legacy API uses duration strings in seconds, so 1200/1500 most likely means seconds
  20:00 to 25:00 (unverified).
- Cost scales with fps: "If you set a custom frame rate in the GenerateContent API, token usage scales
  proportionally with the configured FPS." (tokens page)
- GEAP tip (2026-09-22, looks stale): "Video clipping and frames per second (FPS) are supported by all
  models, but the quality is significantly higher with 2.5-series models."
- Older forum advice (Google staff, 2025-06-06, https://discuss.ai.google.dev/t/optimal-video-pre-processing-parameters-fps-resolution-for-file-api/87440,
  paraphrased): since the API samples 1 FPS, pre-transcoding to 1 FPS and about 720p saves upload size
  without losing quality; the model may downscale frames internally. Do not do this if you plan fps > 1.

### 1.5 Media resolution and token math

Media resolution page (https://ai.google.dev/gemini-api/docs/media-resolution, Updated 2026-09-23),
Gemini 3 models:

| media_resolution | Image | Video (per frame) | Audio | PDF |
|---|---|---|---|---|
| unspecified (Default) | 1120 | 70 | 25 (per second) | 560 |
| low | 280 | 70 | 25 (per second) | 280 + Native Text |
| medium | 560 | 70 | 25 (per second) | 560 + Native Text |
| high | 1120 | 280 | 25 (per second) | 1120 + Native Text |
| ultra_high (per item only) | 2240 | N/A | N/A | N/A |

Recommended settings on that page:
- Video (General): `low` (or `medium`), 70 per frame: "For video, low and medium settings are treated
  identically (70 tokens) to optimize context usage."
- Video (Text-heavy): `high`, 280 per frame: "Required only when the use case involves reading dense
  text (OCR) or small details within video frames."
- Audio: "Audio is tokenized at a fixed rate of 25 tokens per second across all supported resolution
  settings".
- Per-item resolution is Gemini 3 only; `media_resolution` and `processing` are independent and can both
  be set on one video.

GEAP (2026-09-22): "With Gemini 3, video tokenization uses a variable sequence length, which replaces the
Pan and Scan method used in previous models". "The default resolution for videos is 70 tokens per frame."
HIGH 280, MEDIUM 70, LOW 70, UNSPECIFIED 70. "For models earlier than Gemini 3, each frame is tokenized at
258 tokens per frame for default resolution, or 66 tokens per frame for low resolution."

Older numbers still printed on the Gemini API video page (static token calculation): low = 66
tokens/frame, otherwise 258; audio 32 tokens/s; "Total: Approximately 100 tokens per second of video at
default (low) media resolution, or approximately 300 tokens per second of video at high media
resolution." The tokens page adds a third figure: "Video: 263 tokens per second (applies to static
processing)."

Working estimates for Gemini 3, static, 1 FPS (70 + 25 + metadata):

| Clip | Default (~100 tok/s) | High (~305 tok/s) |
|---|---|---|
| 8 s | ~0.8k | ~2.4k |
| 1 min | ~6k | ~18k |
| 10 min | ~60k | ~180k |
| 1 h | ~360k | ~1.1M (context limit) |

At fps = 5 and default resolution: about 5 x 70 + 25 = ~375 tokens/s. A single image at Gemini 3 default
costs 1,120 tokens, so sending frames as separate images is far more expensive than a native video part.

### 1.6 Maximum length

- Gemini API: "Models with a 1M context window can process videos up to 3 hours long by default (at low
  media resolution), or up to 1 hour long at high media resolution."
- GEAP model table (2026-09-22) for 3.8 Flash, 3.7 Flash, 3.6 Flash, 3.5 Flash-Lite, 3.5 Flash,
  3.1 Flash-Lite, 2.5 models, and also 3.1 Pro preview and 3 Flash preview: "Maximum video length (with
  audio): Approximately 45 minutes", "Maximum video length (without audio): Approximately 1 hour",
  "Maximum number of videos per prompt: 10".
- Context windows (GEAP 3.8 Flash guide, 2026-09-22): 3.8 Flash, 3.7 Flash and 3.1 Pro all 1,048,576
  input and 65,536 output tokens.

### 1.7 Timestamps

- Gemini API: "When referring to specific moments in a video within your prompt, use the MM:SS format
  (e.g., 01:15 for 1 minute and 15 seconds)." Also: "You can ask questions about specific points in time
  within the video using timestamps of the form MM:SS."
- GEAP, more detailed: "For sampling rates at 1 FPS or below: Use the MM:SS format ... If you have offsets
  that are greater than 1 hour, use the H:MM:SS format." "For sampling rates above 1 FPS: Use the
  MM:SS.sss format, or, if you have offsets that are greater than 1 hour, use the H:MM:SS.sss format".
- GEAP best practice: "If you require timestamp localization in a video with audio, ask the model to
  generate timestamps that follow the format as described in "Timestamp format"."
- Example prompts from Google: audio page code "Provide a transcript from 02:30 to 03:29." **(summary)**; cookbook
  (https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb, no date)
  **(summary)**: "For each scene in this video, generate captions that describe the scene along with any
  spoken text placed in quotation marks. Place each caption into an object with the timecode of the
  caption in the video."

### 1.8 YouTube URLs

Video page: "The YouTube URL feature is in preview and is available at no charge. Pricing and rate limits
are likely to change." Limits: "For the free tier, you can't upload more than 8 hours of YouTube video per
day."; "For the paid tier, there is no limit based on video length."; "You can only upload public videos
(not private or unlisted videos)."; max 10 videos per request on 2.5 and later. Agentic mode works with
YouTube URLs (AI Studio guide). All of this needs an API key.

### 1.9 Context caching (many questions on one video)

- Interactions API: "only supports implicit caching. Explicit caching ... is not supported in the
  Interactions API. To use explicit caching, switch to the generateContent API."
  (https://ai.google.dev/gemini-api/docs/caching, Updated 2026-09-02)
- Implicit caching: on by default for Gemini 2.5 and newer. Minimum input tokens: Gemini 3.8, 3.7, 3.6,
  3.5 Flash and 3.1 Pro Preview **4,096**; Gemini 2.5 Flash and 2.5 Pro **2,048**. Tips: "Try putting
  large and common contents at the beginning of your prompt" and "Try to send requests with similar
  prefix in a short amount of time". Hits appear in `usage.total_cached_tokens`.
- Explicit caching (https://ai.google.dev/gemini-api/docs/generate-content/caching, Updated 2026-09-11,
  marked Beta, v1beta): "If not set, the TTL defaults to 1 hour."; "There are no minimum or maximum bounds
  on the TTL."; billed on cached tokens at a reduced rate plus storage time. Listed use: "Repetitive
  analysis of lengthy video files".
- Legacy video page: "For videos longer than 10 minutes, or when you plan to make multiple requests against
  the same video file, use context caching".
- Prices (pricing page, Updated 2026-09-24, paid tier per 1M tokens):
  - 3.8 Flash and 3.7 Flash: caching $0.075 through 2026-12-31, $0.15 from 2027-01-01; storage $0.50 per
    1M tokens per hour (then $1.00). Free tier: caching "Free of charge".
  - 3.1 Pro Preview: $0.20 (prompts up to 200k) / $0.40; storage $4.50 per 1M tokens per hour; no free tier.
  - 3.5 Flash-Lite: $0.03; storage $1.00 per 1M per hour; caching not available on free tier.
- In agy there is no explicit cache control, but reusing one conversation keeps context: the headless docs
  show a second turn in a `--input-format stream-json` session reporting `cache_read_tokens` 30,214.
  `--continue` and `--conversation <id>` also resume context.

### 1.10 Structured output

https://ai.google.dev/gemini-api/docs/structured-output (Updated 2026-09-23):
- Interactions API: "configure response_format with an object (or an array containing an object) of type
  text and set its mime_type to application/json. The schema should be provided in the schema field."
- Supported subset: types string, number, integer, boolean, object, array, null (via a type array);
  `title`, `description`; `properties`, `required`, `additionalProperties`; string `enum`, `format`
  (date-time, date, time); numeric `enum`, `minimum`, `maximum`; array `items`, `prefixItems`,
  `minItems`, `maxItems`. Examples on the page use `anyOf` and recursive schemas. Pydantic and Zod work
  through the SDKs.
- Limits: "Not all JSON Schema features are supported." "Very large or deeply nested schemas may be
  rejected." Best practice: "While output is syntactically correct JSON, always validate values in your
  application."
- The audio page's transcription example uses structured output (see 2.1).
- GEAP 3.8 Flash guide (2026-09-22): temperature, top_k and top_p "are ignored by the backend. Instead,
  you can control determinism using thinking_level (LOW, MEDIUM, HIGH) and response_schema or json_schema."

### 1.11 Google's prompting practices for video

From the Gemini API video page, the GEAP video page and the file prompting guide
(https://ai.google.dev/gemini-api/docs/files, section "File prompting strategies", Updated 2026-09-23):

- "Use only one video per prompt request for optimal results." (GEAP; also on the Interactions video page)
- Order: "If combining text and a single video, place the text prompt after the video part" (Gemini API);
  "If your prompt contains a single video, place the video before the text prompt." (GEAP). File guide:
  a single image "(or video)" before the text "might perform better".
- "Be specific in your instructions", "Add a few examples", "Break it down step-by-step", "Specify the
  output format" (file guide).
- If output is too generic: "try asking the model to describe the image(s) or video before providing the
  task instruction" (file guide).
- To find what failed: ask the model to describe the input or explain its reasoning.
- Hallucination: "Try dialing down the temperature setting or asking the model for shorter descriptions"
  (file guide). Note 3.8 Flash ignores temperature, so use shorter outputs, schemas and thinking level.
- Fast action: "Consider slowing down such clips if necessary." (GEAP best practices) and use a higher
  FPS on Gemini 3 (GEAP).
- Text in frames: `media_resolution` high (280 tokens/frame).
- Thinking level for video on 3.8 Flash (GEAP 3.8 Flash guide): HIGH "Recommended for dense visual QA,
  split-second movement detection (sports, editing), or multi-step reasoning across 60+ minute videos";
  MEDIUM (default) for "general video Q&A, lecture summarization, and clip retrieval"; LOW for "fast
  transcript-focused searches or basic metadata extraction". MINIMAL is rejected on 3.8 Flash.
- GEAP multimodal prompt page (2026-09-22) also suggests starting at temperature 0.4 for older models;
  not applicable to 3.8 Flash.

### 1.12 Documented limitations

- Fast motion: "fast action sequences might lose detail due to the 1 FPS sampling rate" (video pages);
  the default rate "may miss details in videos with rapid motion or quick scene changes".
- Small text: only readable reliably at `high` media resolution (see 1.5).
- Non-speech audio: "The models that support audio might make mistakes recognizing sound that's not
  speech." (GEAP video and audio pages)
- Content moderation: "The models refuse to provide answers on videos that violate our safety policies." (GEAP)
- Counting: not listed as a limitation in current docs; the agentic launch blog lists better counting of
  actions and objects over time as an agentic benefit, which implies static 1 FPS counting is weaker.
- Hallucination: Gemini 3.8 Flash model card (https://deepmind.google/models/model-cards/gemini-3-8-flash/,
  published 2026-09-02) lists hallucinations, occasional slowness or timeouts, and extra token use at
  higher effort as known limitations **(summary)**.
- Rates may change: GEAP says the 1 FPS / 1Kbps rates "are subject to change in the future".

### 1.13 Which model for video, and published benchmarks

Model notes:
- GEAP 3.8 Flash guide: 3.8 Flash is GA and its "Primary focus" includes "interactive video understanding";
  3.1 Pro is still Preview (`gemini-3.1-pro-preview`) with focus on deep reasoning.
- Agentic video is only on the Flash family (3.8/3.7/3.6 Flash, 3.5 Flash-Lite), not on 3.1 Pro.
- Models page (https://ai.google.dev/gemini-api/docs/models, Updated 2026-09-23) **(summary)**: stable
  3.8 Flash, 3.7 Flash, 3.6 Flash, 3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite; preview 3.1 Pro and 3 Flash.
- Firebase models page (Updated 2026-09-24): Gemini 3.x Pro, Flash and Flash-Lite accept video and audio.

Google-published video benchmarks (numbers from the official evaluation PDFs, read directly):

| Eval doc (date) | Benchmark | Gemini numbers | Others | Method note |
|---|---|---|---|---|
| Gemini 3 Pro (Nov 2025) | Video-MMMU | 3 Pro 87.6%, 2.5 Pro 83.6% | Claude Sonnet 4.5 77.8%, GPT-5.1 80.4% | Gemini run with media_resolution=HIGH (280 tokens/frame), temperature 0 |
| Gemini 3 Flash (Dec 2025) | Video-MMMU | 3 Flash 86.9%, 3 Pro 87.6%, 2.5 Flash 79.2%, 2.5 Pro 83.6% | Sonnet 4.5 77.8%, GPT-5.2 85.9% | same HIGH setting |
| Gemini 3.1 Pro (Feb 2026) | none for video | MMMU-Pro 80.5% (3 Pro 81.0%) | | no video row |
| Gemini 3.6 Flash (Jul 2026) | none for video | CharXiv only | | |
| Gemini 3.7 Flash (Aug 2026) | LVBench (long video) | 3.7 Flash 85.4%, 3.6 Flash 84.2% | Sonnet 5 68.5%, GPT-5.6 Terra 78.9% | 1024 frames for Gemini and GPT, 300 for Sonnet, no tools |
| Gemini 3.8 Flash (Sep 2026) | LVBench | 3.8 Flash 87.8% (agentic), 87.1% (static); 3.7 Flash 85.4% | Opus 5 75.4%, Sonnet 5 68.5%, GPT-5.6 Sol 82.1%, Terra 78.9% | 1024 frames Gemini and GPT-5.6, 300 for Claude "due to API limitations" |

PDF URLs: storage.googleapis.com/deepmind-media/gemini/ gemini_3_pro_model_evaluation.pdf,
gemini_3_flash_model_evaluation.pdf, gemini_3-1_pro_model_evaluation.pdf, gemini_3-6_flash_model_evaluation.pdf,
gemini_3-7_flash_model_evaluation.pdf, gemini_3-8_flash_model_evaluation.pdf (reached via
deepmind.google/models/evals-methodology/...).

Video-MME: no Gemini 3.x Video-MME number appears in any of these official eval PDFs. A search snippet of the
Gemini 2.5 technical report (arXiv 2507.06261) cites Video-MME 84.3 for 2.5 Pro and 75.5 for 2.5 Flash; I did
not open that PDF.

Takeaway: for video, Google's own evidence favours the current Flash line (3.8 Flash) over 3.1 Pro; Pro has no
published video score newer than Gemini 3 Pro, and 3 Pro vs 3 Flash on Video-MMMU was 87.6 vs 86.9.

### 1.14 Price snapshot (Gemini API, paid tier, per 1M tokens, pricing page 2026-09-24)

| Model | Input (text/image/video) | Output | Free tier |
|---|---|---|---|
| 3.8 Flash, 3.7 Flash, 3.6 Flash | $0.75 through 2026-12-31, $1.50 from 2027-01-01 | $3.75, then $7.50 | "Free of charge" |
| 3.5 Flash-Lite | $0.30 (text/image/video/audio) | $2.50 | "Free of charge" |
| 3.1 Pro Preview | $2.00 (up to 200k), $4.00 above | $12.00 / $18.00 | Not available |
| 3.5 Transcribe | $2.00 audio, or about $0.003/min | $12.00 | "Free of charge" |

Free-tier rows say "Used to improve our products: Yes"; paid rows "No". Free-tier rate limits are not published
on the rate-limits page; they are shown in AI Studio (https://ai.google.dev/gemini-api/docs/rate-limits)
**(summary)**. "Google AI Studio usage is free of charge in all available regions."

---

## 2. Audio understanding

### 2.1 Gemini API audio page

https://ai.google.dev/gemini-api/docs/audio (Updated 2026-09-23).

- Capabilities: "Describe, summarize, or answer questions about audio content", "Transcription and translation
  (speech to text)", "Speaker diarization (identifying different speakers)", "Emotion detection in speech and
  music", "Analyzing specific segments with timestamps".
- Technical details: "Tokens: 32 tokens per second of audio (1 minute = 1,920 tokens)"; "Non-speech: Gemini
  understands non-speech sounds (birdsong, sirens, etc.)"; "Max length: 9.5 hours of audio per prompt";
  "Resolution: Downsampled to 16 Kbps"; "Channels: Multi-channel audio combined to single channel".
- Formats: WAV audio/wav, MP3 audio/mp3, AIFF audio/aiff, AAC audio/aac, OGG audio/ogg, FLAC audio/flac,
  MPEG audio/mpeg, M4A audio/m4a, L16 audio/l16, Opus audio/opus, ALAW audio/alaw, MULAW audio/mulaw,
  WebM audio/webm.
- Inline: under 20 MB total request; Files API above that.
- Timestamps: "Use MM:SS format to reference specific sections". Plain transcript prompt:
  "Generate a transcript of the speech." **(summary)**
- The full transcription example **(summary of the code)** uses `gemini-3.8-flash`, structured output, and a
  prompt with six numbered requirements: identify distinct speakers, timestamps per segment in MM:SS, detect the
  language of each segment, give an English translation when not English, pick one emotion from Happy, Sad,
  Angry, Neutral, and give a short summary first. Schema: `summary` (string) and `segments[]` with `speaker`,
  `timestamp`, `content`, `language`, `emotion` (enum happy/sad/angry/neutral). Reusable as-is for a Bangla
  transcript skill (swap the translation target).

### 2.2 GEAP (Vertex) audio page

https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/audio-understanding
(Updated 2026-09-22):

- 3.8/3.7/3.6/3.5 Flash, 3.5 Flash-Lite, 3.1 Flash-Lite, 3.1 Pro preview, 3 Flash preview, 2.5 models:
  "Maximum audio length per prompt: Approximately 8.4 hours, or up to 1 million tokens"; "Maximum number of
  audio files per prompt: 1".
- Limitations: non-speech sound recognition mistakes; "Audio-only timestamps: To accurately generate timestamps
  for audio-only files, you must configure the audio_timestamp parameter in generation_config." (Vertex
  `audioTimestamp`; there is no such switch in agy.)

### 2.3 Gemini 3.5 Transcribe (dedicated speech-to-text)

https://ai.google.dev/gemini-api/docs/transcribe (Updated 2026-09-23):

- Model `gemini-3.5-transcribe`: "automatic language identification, speaker diarization, word-level timestamps,
  and custom vocabulary hints", plus a "smart" mode that removes disfluencies.
- "Automatically detects languages across 85+ locales" with code-switching support.
- Bengali is listed: "Bengali (Bangladesh) bn-BD" and "Bengali (India) bn-IN".
- Diarization: "Up to 8 speakers are supported (attribution for 3 or more speakers is experimental)."
- Word timestamps: "Enabling word-level timestamps may degrade overall transcription accuracy."
- Length: "Standard unary requests support audio files up to 1 hour. Audio processing is limited to 30 minutes
  when features like speaker diarization or word-level timestamps are enabled."
- Custom vocabulary up to 1,000 terms (best around 100), not combinable with diarization or word timestamps.
- Pricing (pricing page): input $2.00 per 1M audio tokens or about $0.003/min; free tier "Free of charge";
  pricing note uses "25 audio tokens per second". API-key only; not in agy's model list.
- DeepMind page (https://deepmind.google/models/gemini-audio/ai-transcription/, no date) **(summary)**: 85+
  languages, FLEURS WER 5.04% non-streaming, 5.50% streaming.

### 2.4 Languages (Bengali)

Firebase AI Logic models page (https://firebase.google.com/docs/ai-logic/models, Updated 2026-09-24): "All the
Gemini models can understand and respond in the following languages:" and the list includes "Bengali (bn)".
GEAP pages point to the "Google models" page for the language list. Transcription quality for Bengali is not
benchmarked in any doc I found.

### 2.5 Audio inside a video, and the token-rate conflict

- In a native video part, the audio track is "processed at 1Kbps (single channel)" and counted separately
  from frames.
- Audio token rate: 32/s on the audio page and the video page; 25/s for Gemini 3 on the media-resolution page
  ("fixed rate of 25 tokens per second"), and 25/s in pricing notes for Live, Transcribe and TTS models.
  Budget with 32/s to be safe: 10 minutes = 19.2k tokens (15k at 25/s).

---

## 3. Gemini CLI (github.com/google-gemini/gemini-cli, geminicli.com)

### 3.1 Consumer login ended on 2026-06-18

- Google Developers Blog, "An important update: Transitioning Gemini CLI to Antigravity CLI"
  (https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/,
  2026-05-19, Dmitry Lyalin and Taylor Mullen, paraphrased): on 2026-06-18 Gemini CLI and Code Assist IDE
  extensions stop serving Google AI Pro, Ultra and free Code Assist for individuals users; Code Assist
  Standard/Enterprise continue; the CLI stays usable with "paid Gemini and Gemini Enterprise Agent Platform
  API keys"; no 1:1 feature parity promised for Antigravity CLI at first.
- GitHub discussion #28017 (https://github.com/google-gemini/gemini-cli/discussions/28017, 2026-06-18,
  maintainer) confirms the stop for Pro, Ultra and free individual accounts; API key users unaffected.
- Auth doc (https://geminicli.com/docs/get-started/authentication/, Updated 2026-09-18), banner: "Unpaid tier
  and Google One users: Gemini CLI was replaced by Antigravity CLI on June 18th, 2026." The same page's table
  recommends "Use Gemini API Key or Vertex AI" for headless mode.
- Quotas page (https://geminicli.com/docs/resources/quota-and-pricing/, Updated 2026-06-18) still shows the
  old table: Google login 1,000 (Code Assist Individual), 1,500 (AI Pro), 2,000 (AI Ultra) requests/day;
  Gemini API key free tier "250 maximum model requests / user / day" and "Model requests to Flash model only";
  Vertex Express "90 days before you need to enable billing". The README (undated) still advertises "60
  requests/min and 1,000 requests/day" for Google sign-in **(summary)**. Treat the Google-login rows as dead
  for personal accounts.
- Latest release: v0.61.0 on 2026-09-23 (https://geminicli.com/docs/changelogs/) **(summary)**.

### 3.2 Headless flags

https://geminicli.com/docs/cli/headless/ (Updated 2026-03-10) **(summary)**: `-p/--prompt` or positional
prompt or stdin; `--output-format text|json|stream-json`; `-m/--model`; `-y/--yolo`; `--approval-mode`;
`--include-directories`; `--debug`. JSON output has `response`, `stats`, `error`. stream-json events: `init`,
`message`, `tool_use`, `tool_result`, `error`, `result`. Exit codes 0, 1, 42 (input error), 53 (turn limit).
No JSON-schema or structured-output flag is documented (only `--output-format json`, added via issue #8022
in 2025).

### 3.3 How Gemini CLI sends video and audio

- `@path` in the prompt: content "is fetched and then inserted into your query before being sent" via the
  internal `read_many_files` tool (https://geminicli.com/docs/reference/commands/, Updated 2026-08-17)
  **(summary)**. The model-facing `read_many_files` tool was deprecated around v0.15 to v0.16 (discussion
  #12970, search summary only), but the `@` processor still uses `ReadManyFilesTool` in source.
- Source code (main branch, Apache 2.0, read 2026-09-24):
  - `packages/core/src/utils/fileUtils.ts`: `detectFileType` returns `'text' | 'image' | 'pdf' | 'audio' |
    'video' | 'binary' | 'svg'`; for `'image'`, `'pdf'` and `'video'` it reads the file and returns
    `inlineData: { data: base64Data, mimeType }` with display text "Read video file: ...". So an mp4 is sent
    as native inline video (the model gets frames plus the audio track at the API default 1 FPS). There is no
    way to pass `videoMetadata.fps` or `media_resolution` from the CLI.
  - `packages/core/src/utils/constants.ts`: `export const MAX_FILE_SIZE_MB = 20;`
  - `packages/core/src/tools/read-many-files.ts`: image, pdf and audio files are skipped unless "explicitly
    requested by name or extension"; video is not in that check.
- `read_file` tool doc (https://geminicli.com/docs/tools/file-system/, Updated 2026-04-10): "Supports text,
  images, audio, and PDF." (video not listed).
- Known failure when the model itself calls `read_file` on media: issue #16741
  (https://github.com/google-gemini/gemini-cli/issues/16741, 2026-01-15) reports a 400 error because
  audio/video mime types are "not supported in function_response.parts", and the session keeps resending the
  bad part. So only the `@path` route (user turn) is reliable for video.
- Audio support in tool descriptions was made explicit by PR #14658 (merged 2025-12-08).

Net: Gemini CLI would give native video with audio, but not on a consumer login any more, and with no fps,
resolution or schema control.

---

## 4. Google Antigravity (agy)

### 4.1 Headless mode

https://antigravity.google/docs/cli/headless/ (no date shown; paraphrased except flag names):

- `-p` / `--print` / `--prompt` runs once; response on stdout, diagnostics on stderr. Needs a prior interactive
  sign-in (cached credentials).
- `--output-format text|json|stream-json`. JSON envelope: `conversation_id`, `status` (SUCCESS, ERROR,
  CANCELED, INTERRUPTED, INVALID, WAITING, RUNNING), `response`, `error`, `duration_seconds`, `num_turns`,
  `structured_output` and `json_schema` (with `--json-schema`), `usage` (`input_tokens`, `output_tokens`,
  `thinking_tokens`, `cache_read_tokens`, `total_tokens`).
- `--json-schema` takes an inline schema string, a path to a .json file, or a primitive type name; for
  stream-json it applies to the final `result` event.
- `--input-format stream-json` keeps one process for many turns; content blocks: "text is the only supported
  block type" and any other block type ends the session with an error. So media cannot be passed as prompt
  parts in headless mode; the agent must open files with its tools.
- `--model <slug>` (list with `agy models`; examples `gemini-3.8-flash-high`, `gemini-3.8-flash-medium`,
  `gemini-3.7-flash-high`, `gemini-3.6-flash-high`, `gemini-3.1-pro-high`, `claude-sonnet-4-6`); unknown slug
  exits non-zero instead of falling back. `--effort low|medium|high`, `--agent`.
- `--continue/-c`, `--conversation <id>`; `--dangerously-skip-permissions`; `--sandbox`; `--print-timeout`
  (docs table says default 5m).
- Permissions: reads and writes inside the workspace are auto-allowed; tools needing approval are soft-denied
  in headless mode (run exits 0 with a stderr notice); allow rules go in `permissions.allow` in
  `~/.gemini/antigravity-cli/settings.json`.
- Baseline cost: the docs' own examples show `input_tokens` 10,415 and 10,522 (with about 8.1k
  `cache_read_tokens`) for one-line questions, and 30,384 for the first turn of a stream-json session.
- `--add-dir` is not in the documented headless flag table; the CLI reference lists the `/add-dir <path>`
  slash command (https://antigravity.google/docs/cli/reference/). Since it works for you, it is presumably an
  undocumented flag; confirm with `agy --help`.

CLI changelog items that change this picture (https://antigravity.google/changelog, CLI tab, read 2026-09-24;
latest listed CLI version is 1.2.9 of 2026-09-23, so your 1.2.10 is newer than the public list; releases roll
out gradually):
- 1.1.8 (2026-07-28): added `--output-format` and `--json-schema`.
- 1.1.13 (2026-08-14): `GEMINI_API_KEY` support (`modelProvider: "gemini"`, optional `GOOGLE_GEMINI_BASE_URL`).
- 1.1.27 (2026-09-05): refused tool actions are reported as `denied_actions` in the JSON output.
- 1.1.28 (2026-09-09): `--print-timeout` expiry now returns partial output with exit 0 and a warning.
- 1.2.6 (2026-09-18): default headless timeout changed from 5 minutes to unlimited; failures print a
  structured `AGY_ERROR: {...}` line on stderr and exit with code 3.
- 1.2.9 (2026-09-23): headless runs wait for background tasks until `--print-timeout`, capped at 30 minutes.

### 4.2 Models

https://antigravity.google/docs/models/ (no date): Gemini 3.8 Flash, 3.7 Flash, 3.6 Flash, 3.1 Pro on every
plan including Free and Google AI Plus; Claude Sonnet 4.6 (thinking), Claude Opus 4.6 (thinking) and
GPT-OSS-120b on Free, Plus, Pro and Ultra but not Enterprise. Nano Banana 2 handles image generation.

### 4.3 Media handling (what is documented)

- Prompting doc (https://antigravity.google/docs/cli/prompting/, no date): in the interactive TUI you can paste
  media with Ctrl+V; supported types are images (PNG, JPEG, GIF, WebP, BMP, TIFF, SVG) and videos (MP4, MOV,
  WebM, AVI). Whether a pasted video is sent natively (with audio) or as frames is not stated. Not usable in
  headless mode (see the text-only rule above).
- `view_file` is a built-in tool described only as reading file contents (SDK tools page,
  https://antigravity.google/docs/sdk/tools/). No doc explains video-to-frame conversion, frame rate, audio
  handling or token budget for videos. Our test (1 FPS frames, 8 frames for 8 s) is the only evidence.
- Changelog items about media (paraphrased):
  - CLI 1.1.15 (2026-08-19): reading a .wav file failed as an unsupported media type; fixed by normalizing mime
    types "before they reach the model". This implies audio files read by the agent reach Gemini as audio.
  - CLI 1.1.17 (2026-08-20): Ogg audio and video attachments (.ogg, .opus, .ogv) were sent as generic
    application/ogg and rejected; fixed.
  - CLI 1.1.18 (2026-08-22): audio attachments recognize .wav, .mp3, .m4a, .aac, .flac, .opus.
  - CLI 1.2.2 (2026-09-12): `view_file` now rejects unsupported binary formats and files larger than 100 MB.
  - CLI 1.2.8 (2026-09-22): custom models honour `modelFeatures` media flags for images, video, PDF and audio.
  - Desktop app 2.10.0 (2026-08-24): audio attachments (MP3, WAV, M4A, AAC, OGG, FLAC, OPUS) up to 20 MB.
  - Desktop app 2.11.0 (2026-08-26): `view_file` gained page ranges (StartPage, EndPage) for PDFs and an image
    resolution option (`MediaResolution`). The CLI shares the agent harness (CLI 1.1.17 "consolidated agent
    execution harness"), so the option probably exists in agy too; untested.
- GitHub issue #762 (https://github.com/google-antigravity/antigravity-cli/issues/762, opened 2026-08-06,
  closed): in the Antigravity IDE 2.1.1 the Media picker accepted images and PDFs but not MP4; no maintainer
  answer about frames or audio.
- Antigravity SDK (https://antigravity.google/docs/sdk/overview/ and the Python SDK README): accepts image,
  video, audio and document attachments (`from_file`), but authenticates with a Gemini API key or Vertex, not
  the consumer login.

### 4.4 Plans, quotas, AI credits

Plans page (https://antigravity.google/docs/plans/, no date; paraphrased with short quotes):
- All plans: Gemini models including 3.1 Pro and 3.8 Flash, unlimited tab completions, all features including
  the CLI.
- Google AI Ultra: highest quota "refreshed every five hours", highest weekly limits, third-party models.
- Google AI Pro: quota "refreshed every five hours until weekly limit reached", higher weekly limit.
- Everyone else: quota "refreshed weekly" with a weekly limit.
- Limits track "the amount of work done by the agent" and may change.
- Overages: Pro and Ultra can spend purchased AI credits at Gemini Enterprise consumption pricing; the "AI
  Credit Overages" setting is Never or Always. No bring-your-own-key for extra rate limits.

"Changes to Antigravity Plans" blog (https://antigravity.google/blog/changes-to-antigravity-plans, 2026-05-19):
- Gemini Flash and Pro now share one limit "drawn down as per API pricing"; non-Gemini models keep a separate
  fixed limit.
- New $100/month Ultra tier with 5x the tokens of the $20 Pro plan; top Ultra cut from $250 to $200 with 20x.
- AI credits removed from base plans and kept only as an overage mechanism.

Earlier blog (https://blog.google/feed/new-antigravity-rate-limits-pro-ultra-subsribers/, 2025-12-05): Pro and
Ultra got five-hour refresh; free users moved to a larger weekly limit.

CLI controls: `/usage` (alias `/quota`) shows per-model quota; `/credits` shows credits; setting
`useG1Credits` (default false, "External builds only") spends personal credits once plan quota is exhausted
(https://antigravity.google/docs/cli/reference/, https://antigravity.google/docs/cli/credits/).

No official numbers exist for the five-hour or weekly caps. A community post (sanj.dev, Aug 2026) claims a
250-unit five-hour and 2,800-unit weekly structure; a forum thread (discuss.ai.google.dev, 2026-03-10) shows
users disputing weekly lockouts with no Google explanation. Treat both as unofficial.

### 4.5 Auth and Terms of Service

- Install and auth (https://antigravity.google/docs/cli/install/): Google sign-in stored in the OS keyring;
  SSH sessions get a URL plus one-time code; `GEMINI_API_KEY` with `modelProvider: "gemini"` bypasses sign-in.
- FAQ (https://antigravity.google/docs/faq/): personal Google accounts in approved regions, 18+ only. On
  third-party tools it says using third-party software (named examples: Claude Code, OpenClaw, OpenCode) with an
  Antigravity login is "a violation of our Terms of Service" that can lead to suspension, and it recommends "a
  Gemini Enterprise or Google AI Studio API key" for third-party coding agents.
- Community projects that reuse the Antigravity login to send native video/audio `inlineData` exist (for
  example a September 2026 PR in chaos-03x/dsh-agy); they fall under that ToS warning.

---

## 5. Getting higher frame rates or audio without an API key

| Route | Frames | Audio | Headless | Status and evidence |
|---|---|---|---|---|
| agy `view_file` on the mp4 (current) | 1 FPS, images | unknown (test clip was silent) | yes | Undocumented; our test only |
| agy + ffmpeg frame extraction at N fps, images read by `view_file` | any fps you choose | no | yes | Images are documented media; costs up to 1,120 tokens per image at Gemini 3 default |
| agy + ffmpeg contact sheets (grid of frames per image) | many frames per image | no | yes | Design idea; trades detail for coverage |
| agy + time-stretched copy (setpts) | effective N x 1 FPS | no (or pitch-shifted) | yes | Google itself suggests slowing fast clips; must rescale timestamps |
| agy + extracted audio file (.wav/.mp3/.m4a/.flac/.opus) | n/a | likely native audio | yes | Changelog 1.1.15/1.1.18 imply audio reaches the model; needs a test |
| agy TUI paste (Ctrl+V) of a video | unknown | unknown | no | Documented for MP4/MOV/WebM/AVI, interactive only |
| Gemini CLI `@video.mp4` | API default 1 FPS | yes (native) | yes | Consumer login gone since 2026-06-18; key needed; 20 MB cap |
| Free AI Studio API key, direct API | fps (0, 24], clipping, media_resolution, agentic | yes (native) | yes | Needs a key (free tier: data used to improve products) |
| agy with `GEMINI_API_KEY` | same as agy (view_file) | as above | yes | Uses API quota, not plan quota |
| Third-party clients on the Antigravity login | native | native | yes | Against Antigravity ToS; avoid |

Reading your measurements:
- 8 frames for 8 s matches 1 FPS static sampling.
- About 20k input tokens = agy baseline (about 10.4k in the docs examples) + about 9k for the video. 8 x 1,120
  and 32 x 280 are both 8,960, which matches Gemini 3 image tiers (default and low). That points to frames sent
  as images inside a fixed budget, with resolution dropping as frame count rises. A 16-frame test should then
  land near 560 tokens per frame.
- Suggested checks: (1) a clip with clear speech and a distinct sound, asking for a transcript with MM:SS;
  (2) the same clip plus its audio extracted to .wav, asking the agent to `view_file` both; (3) ask the agent to
  call `view_file` with MediaResolution HIGH and compare `usage.input_tokens`; (4) burn a timecode into frames
  (ffmpeg drawtext) or name frame files by time so the model can cite real timestamps, since agy's image path
  does not carry the API's per-second timestamps.
- Local fallback that needs no quota at all: transcribe audio locally and pass the timed transcript as text
  next to the frames. Not a Google feature, just a complement.

---

## 6. Conflicts and open questions

1. Per-frame tokens: 66/258 (video page static calc) vs 70/280 (Gemini 3 media-resolution page and GEAP) vs
   "263 tokens per second" (tokens page).
2. Audio tokens: 32/s (audio and video pages) vs 25/s (Gemini 3 media-resolution page, pricing notes).
3. Max audio per prompt: 9.5 h (Gemini API) vs about 8.4 h or 1M tokens (GEAP).
4. Max video: 3 h default / 1 h high (Gemini API) vs about 45 min with audio / 1 h without (GEAP).
5. Inline size: < 100MB (video table) vs 20 MB (video text, audio page) vs 100 MB (Files API page).
6. File API per-file size: "20GB (paid) / 2GB (free)" (video page) vs "per-file maximum size of 2 GB" (Files page).
7. Interactions API: live page says GA since June 2026 and shows `processing.fps`; the `.md.txt` mirror and the
   cookbook still say custom fps and clipping need generateContent. Clipping units in the Interactions example
   (1200/1500) are not stated.
8. Prompt order wording differs (text after video vs video before text) but means the same thing.
9. agy headless timeout: docs table says 5m default; changelog 1.2.6 says unlimited by default.
10. Gemini CLI quota page still lists Google-login tiers although personal Google logins stopped on 2026-06-18.
11. GEAP tip that fps/clipping quality is "significantly higher with 2.5-series models" looks stale.
12. Nothing official describes agy `view_file` video handling (fps, audio, token budget, MediaResolution).

---

## 7. Sources (fetched 2026-09-24)

Gemini API (ai.google.dev, CC BY 4.0):
- Video understanding: https://ai.google.dev/gemini-api/docs/video-understanding (Updated 2026-09-23)
- Video understanding, generateContent (legacy): https://ai.google.dev/gemini-api/docs/generate-content/video-understanding (Updated 2026-09-16)
- Media resolution: https://ai.google.dev/gemini-api/docs/media-resolution (Updated 2026-09-23)
- Tokens: https://ai.google.dev/gemini-api/docs/tokens (Updated 2026-09-23)
- Audio: https://ai.google.dev/gemini-api/docs/audio (Updated 2026-09-23)
- Transcribe: https://ai.google.dev/gemini-api/docs/transcribe (Updated 2026-09-23)
- Files API and file prompting strategies: https://ai.google.dev/gemini-api/docs/files (Updated 2026-09-23)
- Caching (Interactions): https://ai.google.dev/gemini-api/docs/caching (Updated 2026-09-02)
- Caching (generateContent): https://ai.google.dev/gemini-api/docs/generate-content/caching (Updated 2026-09-11)
- Structured outputs: https://ai.google.dev/gemini-api/docs/structured-output (Updated 2026-09-23)
- Interactions API overview: https://ai.google.dev/gemini-api/docs/interactions (Updated 2026-09-23)
- Pricing: https://ai.google.dev/gemini-api/docs/pricing (Updated 2026-09-24)
- Models: https://ai.google.dev/gemini-api/docs/models (Updated 2026-09-23) (summary)
- Gemini 3.8 Flash model page: https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash (summary)
- Rate limits: https://ai.google.dev/gemini-api/docs/rate-limits (summary)
- API schema, VideoMetadata.fps: https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta

Google Cloud, Gemini Enterprise Agent Platform (formerly Vertex AI, CC BY 4.0):
- Video understanding: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/video-understanding (Updated 2026-09-22)
- Audio understanding: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/audio-understanding (Updated 2026-09-22)
- Gemini 3.8 Flash developer guide: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/guides/gemini-3-8-flash (Updated 2026-09-22)
- Design multimodal prompts: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/design-multimodal-prompts (Updated 2026-09-22)

Firebase AI Logic (CC BY 4.0):
- Models and languages: https://firebase.google.com/docs/ai-logic/models (Updated 2026-09-24)
- Input file requirements: https://firebase.google.com/docs/ai-logic/input-file-requirements (Updated 2026-09-24)

Google AI Studio and blogs:
- Agentic video developer guide: https://aistudio.google.com/learn/agentic-video-understanding-with-gemini (no date)
- Agentic video launch: https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/ (2026-09-01)
- Gemini CLI to Antigravity CLI: https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ (2026-05-19)
- Antigravity rate limits: https://blog.google/feed/new-antigravity-rate-limits-pro-ultra-subsribers/ (2025-12-05)

DeepMind evals and model cards:
- Gemini 3 Pro eval PDF (Nov 2025), Gemini 3 Flash eval PDF (Dec 2025), Gemini 3.1 Pro eval PDF (Feb 2026),
  Gemini 3.6 Flash (Jul 2026), 3.7 Flash (Aug 2026), 3.8 Flash (Sep 2026): https://storage.googleapis.com/deepmind-media/gemini/
- Gemini 3.8 Flash model card: https://deepmind.google/models/model-cards/gemini-3-8-flash/ (2026-09-02)
- Gemini 3.1 Pro model card: https://deepmind.google/models/model-cards/gemini-3-1-pro/ (2026-02-19)
- Gemini transcription page: https://deepmind.google/models/gemini-audio/ai-transcription/ (no date)

Cookbook:
- https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb (no date, summary)

Gemini CLI:
- Repo and README: https://github.com/google-gemini/gemini-cli (summary)
- Headless: https://geminicli.com/docs/cli/headless/ (Updated 2026-03-10, summary)
- Authentication: https://geminicli.com/docs/get-started/authentication/ (Updated 2026-09-18)
- Quotas: https://geminicli.com/docs/resources/quota-and-pricing/ (Updated 2026-06-18)
- Commands reference (@): https://geminicli.com/docs/reference/commands/ (Updated 2026-08-17, summary)
- File system tools: https://geminicli.com/docs/tools/file-system/ (Updated 2026-04-10)
- Changelog: https://geminicli.com/docs/changelogs/ (v0.61.0, 2026-09-23, summary)
- Source: packages/core/src/utils/fileUtils.ts, packages/core/src/utils/constants.ts, packages/core/src/tools/read-many-files.ts (main, read 2026-09-24)
- Discussion #28017 (2026-06-18), issue #16741 (2026-01-15), PR #14658 (2025-12-08), issue #1556 (2025-06-25), issue #3379 (2025-07-06)

Antigravity:
- Headless: https://antigravity.google/docs/cli/headless/
- Prompting and media paste: https://antigravity.google/docs/cli/prompting/
- CLI reference: https://antigravity.google/docs/cli/reference/
- Using AGY CLI: https://antigravity.google/docs/cli/using/
- Install and auth: https://antigravity.google/docs/cli/install/
- Models: https://antigravity.google/docs/models/
- Plans and credits: https://antigravity.google/docs/plans/ , https://antigravity.google/docs/cli/credits/ , https://antigravity.google/docs/cli/commands/usage/
- FAQ: https://antigravity.google/docs/faq/
- SDK: https://antigravity.google/docs/sdk/overview/ , https://antigravity.google/docs/sdk/tools/ , https://github.com/google-antigravity/antigravity-sdk-python
- Changelog (CLI 1.2.9 of 2026-09-23 latest listed): https://antigravity.google/changelog
- Plans blog: https://antigravity.google/blog/changes-to-antigravity-plans (2026-05-19)
- Issue #762: https://github.com/google-antigravity/antigravity-cli/issues/762 (2026-08-06)

Unofficial, for context only:
- Forum, video pre-processing (Google staff reply): https://discuss.ai.google.dev/t/optimal-video-pre-processing-parameters-fps-resolution-for-file-api/87440 (2025-06-06)
- Forum, Antigravity Pro quota: https://discuss.ai.google.dev/t/navigating-antigravity-pro-quota-limits/130212 (2026-03-10)
- sanj.dev quota post (Aug 2026), chaos-03x/dsh-agy PR #30 (Sep 2026)
