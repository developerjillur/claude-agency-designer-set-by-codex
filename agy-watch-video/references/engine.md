# The engine: Gemini through the Antigravity CLI

Everything here was measured on 2026-09-24 with agy 1.2.10 on macOS, signed in with a Google AI Pro account, unless a
source is named. agy updates itself in the background, so re-run `doctor --smoke` after a version change and re-check
the numbers that matter.

## 1. How the skill calls agy

```bash
agy -p "<prompt with absolute file paths>" --output-format json --json-schema <schema.json> \
    --model <model> --print-timeout <seconds>s --add-dir <a fresh folder with this call's media only>
```

- Each call is a fresh conversation, run from an empty work folder inside the cache.
- Only a fresh staging folder is shared (`--add-dir`), holding hardlinks to that call's media and nothing else, and
  it is removed after the call. Text in a video that tells the agent to read other files finds nothing to read. In headless mode the
  current folder is **not** readable by the agent: reads need `--add-dir`, and writes are denied unless a
  `permissions.allow` rule exists (the skill never needs writes).
- A denied tool still exits 0 with `status: SUCCESS`. The skill reads `denied_actions` and never keeps a run with a
  denial, even one with an answer: the agent may not have seen the media. It retries once with a stricter prompt (no
  tool except `view_file`; for text-only calls, no tool at all), then the sibling model. In a live test, Flash tried
  to run a command while rewriting a claim into a question, a text-only task; the stricter retry fixed it.
- The answer is read from `structured_output`. Every schema field has a description: without one the extraction turn
  returns wrong or null values. `response` repeats the JSON with extra keys and is used only as a fallback.
- Notices can come before the JSON envelope on stdout, and the envelope echoes the schema; the skill takes the last
  top-level JSON object that looks like an envelope.
- Never `--dangerously-skip-permissions`. In an early test, when a file read failed, the agent went looking in its own
  transcript and tried to read `~/.zsh_history` (denied).

## 2. What each kind of file becomes

| File given to `view_file` | What the model receives | Measured |
|---|---|---|
| mp4 (H.264) | about 1 frame per second as separate low-detail images, plus a speech transcript the tool makes itself, **no audio signal** | 8 s gave 8 frames, 14 s gave 14, 60 s gave 61; about 70 to 100 tokens a frame |
| JPEG or PNG frame | one full-detail image | up to about 1,100 tokens (Gemini 3 documents 1,120 at the default resolution) |
| WAV (16 kHz mono PCM) | real audio | exact transcript; sentence starts within 0.3 s |
| MP3 | real audio | exact transcript; starts about 1 s late |
| m4a / AAC | refused: `unsupported mime type audio/mp4a-latm` | |
| a file over 100 MB | refused (agy changelog 1.2.2) | the skill sends a proxy |

The transcript the tool attaches to a video has compressed times: sentences at 0, 3.0, 5.8 and 9.0 s came back as
0, 2, 4 and 6 s. The skill never uses it and always sends the soundtrack as WAV.

A prompt can list several files. The agent opens them in parallel in one step, which keeps the number of turns (and the
per-turn overhead) down. One call with the video frames and the WAV together gives a timeline that joins speech and
picture, but its speech times were about 1 s off, so the skill keeps audio in its own pass.

## 3. Tokens and time

- Agent overhead: about 17.7k input tokens per turn (system prompt and tools). Opening files adds a turn, so a call
  that views media costs about 2 × 17.7k plus the media, minus cached reads.
- An 8 s clip as video: about 1k to 4k tokens of frames. The same clip as 16 full frames: about 45k input plus 60k
  cached.
- Timing per call (wall clock, including about 10 s of CLI start-up):

| Model | Typical call |
|---|---|
| gemini-3.8-flash-medium | 15 to 35 s |
| gemini-3.8-flash-high | 25 to 60 s |
| gemini-3.1-pro-high | 35 to 130 s |

- Five or more agy processes run in parallel without trouble.

## 4. Models and routing

`agy models` lists Gemini 3.8, 3.7 and 3.6 Flash (high, medium, low), Gemini 3.1 Pro (high, low), Claude Sonnet 4.6,
Claude Opus 4.6 Thinking and GPT-OSS 120B. The skill uses:

| Role | Default model | Why |
|---|---|---|
| overview of the proxy video | gemini-3.8-flash-high (medium for `--depth quick`) | the frames are low detail anyway; speed |
| audio | gemini-3.8-flash-high | accurate, fast; handles Bengali |
| full-resolution frame batches | gemini-3.1-pro-high | invents least: on 16 sharp frames it tracked every person, a child, a crouching mechanic standing up and leaving with a hose, and invented no text |
| second opinion (`ask`, forensic) | gemini-3.8-flash-high | more detail, but calls a push-in static and misreads digits with confidence |
| subject boxes for auto zoom | gemini-3.8-flash-medium | a quick, easy task |
| text check, second reader | gemini-3.8-flash-low | reading needs eyes, not reasoning: on 12 frames of a render it read the same words as Flash on high in 27 s instead of 187 s (56k thinking tokens) |
| review | gemini-3.1-pro-high | careful merging of the passes |

Override with `AWV_MODEL_FAST`, `AWV_MODEL_LIGHT`, `AWV_MODEL_READ` (the text check's second reader) and
`AWV_MODEL_DEEP`. Fallbacks: Pro to Flash 3.8, Flash 3.8 to
Flash 3.7.

## 5. What the tests showed (8 s drone clip of a workshop, checked frame by frame)

| Setup | Result |
|---|---|
| Flash, video file, "note every glitch" prompt | the story right; a signboard slogan invented; a green window read as a hi-vis vest; a Toyota wagon called a Prius |
| Pro, same | reported heavy AI morphing on real footage and rejected it |
| Pro, video file, neutral deep schema with the unreadable rule | useful editing advice, no invented text, but an invented door-opening action |
| Pro, 4x slow-motion copy (32 low-detail frames) | the slogan invented again; vehicles mixed up |
| Pro, 16 sharp frames (2 per second) as images | the best: every person including a child, the crouching mechanic standing up and leaving with a hose, the SUV's open bonnet on a ramp, the silver car on the lift; no invented text |
| Flash, the same 16 frames | the most detail (a likely drone pilot, a spare-wheel SUV, the car model), but called the push-in a static hover and misread the phone digits |
| `ask` about the hose, full frames | both models said his hands were empty |
| `ask` about the hose, zoomed on the subject | both models found the hose |

Lessons built into the skill: detail comes from sharp frames and zoom, never from the video file; prompts stay
neutral; two models are compared; small text is read twice and checked; Claude verifies with its own eyes.

## 5a. Between the frames: the change grid

No model sees every frame, so ffmpeg does. In the same pass as the other measurements, every frame is compared with
the previous one at up to 640 px (the largest of the Y, U and V differences), dilated 3x3 so a thin line registers,
and averaged into a grid of 32 cells on the long side. A cell counts when it rises above its own frame's level by more
than 6 (of 255) and by more than six times its usual spread, so a camera move or a cut, which lifts every cell, does
not count. Grid frames are matched to the real frame timestamps (`-fps_mode passthrough`): with a resampled grid the
frame chosen for a 3-frame event was once one frame late, after the event had ended.

Measured calibration (2026-09-24):

| Clip | What the grid saw |
|---|---|
| a red 48 px square for 3 frames on grey noise | one brief change, 2.333 to 2.433 s, top right, strength 38 to 70; the frame chosen (2.366 s) shows it |
| a white-on-black label for 0.43 s next to a moving figure | appear and disappear 0.43 s apart, paired into one brief change (strength 95); kept apart from the figure because it is more than 3 times stronger |
| a green square appearing on grey (similar brightness) | missed on brightness alone; found once the colour planes counted |
| an 8 s drone push-in over a workshop | a worker walking: strength 7 to 100, one moving area tracked from the bottom left towards the left edge; 58 short flickers of movement before the rules below, 0 brief changes after |
| a flat dark block moving slowly | only its two edges change (strength about 13): merged into one moving area |

Rules that came from these: a brief change needs a strength of at least 18 (ordinary movement of a person measured 7
to 16) and must not sit at the same place and time as movement at least half as strong; appear and disappear pairs up
to 1.5 s apart are one event; parts of similar strength within 3 cells in one frame are one object; changes that
keep coming and going in one place, in at most half of the frames, are a flicker (a blinking icon), not movement. The close-up of
the drone clip's moving area at 4 s showed the worker and the thin hose from his hand to the tyre, found without a
model call.

Limits: a change filling well under one cell (about 3% of the width), or fainter than the threshold, is not measured;
videos over 20 minutes are measured about 10 times a second, which still catches 0.1 s but can miss a single frame.

## 6. Limits and failure modes

- `view_file` refuses files over 100 MB (the skill sends a proxy of at most 1280 px).
- agy hung for about 42 minutes on a file whose audio and video were out of sync (reported in the community): the
  proxy has no audio, and every call has a hard timeout.
- About 10% of long runs end with `SUCCESS` and an empty reply (reported): the skill retries once, then falls back.
- Prompts are cut at about 192 KB (reported): the review pass trims its facts to 150 KB, counted in bytes (Bengali
  letters take three).
- There has been no default print timeout since 1.2.6: the skill always passes `--print-timeout`, set by the kind of
  call at about three times the slowest measured: 900 s for a proxy video (overview, locate), 600 s for five minutes
  of audio, 420 s for frames, 360 s for the review and 240 s for other text-only calls. A call that hits it goes
  to the sibling model once. `AWV_CALL_TIMEOUT` sets one limit for every call.
- The agent can reach for tools on its own: in a live run, Flash tried to run a command while rewriting a claim (a
  text-only task). A denied run is never kept; it is retried with a stricter prompt, then the sibling model.
- Gemini's audio times drift on long files (a report of -157 s over 11:49): audio goes in 5-minute parts, and each part
  is aligned to measured speech onsets.

## 7. Quota

`agy -p "/usage"` (the skill's `usage` command) prints the remaining share of the Gemini five-hour and weekly limits
and, separately, of the Claude and GPT limits. On the Pro plan the Gemini quota refreshes every five hours until the
weekly limit is reached. A standard watch of an 8 s clip used well under 1% of the five-hour limit. Five Pro runs on
16 frames used about 6%.

## 8. Terms, and the API-key route

Google's Antigravity FAQ (https://antigravity.google/docs/faq, read 2026-09-24): "Using third party software, tools,
or services to access Antigravity is a violation of our Terms of Service, and severely degrades the experience for
legitimate product users." "Such actions may be grounds for suspension or termination of your account." "If you would
like to use a third party coding agent with Gemini, we recommend using a Gemini Enterprise or Google AI Studio API key."

This skill calls the official `agy` binary in the headless mode Google documents for scripts and CI. It does not reuse
the login in another client. Claude Code still orchestrates it, so the account owner decides whether that is
acceptable. The safer route for heavy or commercial use is an API key:
- agy can run on a Gemini API key instead of the sign-in (the install docs describe `GEMINI_API_KEY` with the Gemini
  model provider). The user sets this up in agy themselves, and the skill works unchanged. Never ask for a key in chat.
- The Gemini API itself (not used by the skill yet) accepts native video with its audio. It supports a custom frame
  rate up to 24 fps, clipping by offsets, high media resolution (280 tokens a frame), and, since 2026-09-01, an
  "agentic" video mode for long videos. That would be the next engine to add.

## 9. Things not to rely on

- Gemini CLI (`gemini`) no longer serves personal Google accounts (since 2026-06-18); it needs an API key.
- Pasting a video with Ctrl+V works only in the interactive agy screen, not in headless mode.
- `stream-json` input accepts text blocks only: media must go through `view_file`.
