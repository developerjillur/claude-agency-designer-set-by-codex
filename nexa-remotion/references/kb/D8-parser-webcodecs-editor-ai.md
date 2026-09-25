# D8: AI (agents, skills, plugins, MCP, AI templates), media-parser, webcodecs, Mediabunny, Timeline, Editor Starter, troubleshooting, miscellaneous, terminology

Research agent: `D8-parser-webcodecs-editor-ai`. Target runtime on this machine: Remotion 4.0.528 (React 19).
Coverage log: `kb/D8-parser-webcodecs-editor-ai.coverage.txt` (169 lines, one per assigned file, no gaps, no duplicates).

---

## 1. Scope and coverage

### Assigned docs pages (all 169 read fully, one by one)

| Area | Pages | Path |
|---|---|---|
| AI | 15 | `mirror/docs/ai/*.md` |
| @remotion/media-parser | 28 | `mirror/docs/media-parser/*.md` |
| @remotion/webcodecs | 30 | `mirror/docs/webcodecs/*.md` |
| Mediabunny | 9 | `mirror/docs/mediabunny/*.md` |
| Timeline (paid component) | 5 | `mirror/docs/timeline/*.md` |
| Editor Starter (paid template) | 24 | `mirror/docs/editor-starter/*.md` |
| Troubleshooting | 23 | `mirror/docs/troubleshooting/*.md` |
| Miscellaneous (incl. 3 snippets) | 21 | `mirror/docs/miscellaneous/**.md` |
| Terminology | 14 | `mirror/docs/terminology/*.md` |
| **Total** | **169** | |

### Supplementary material read (not assigned to anyone, read because the AI part "matters most")

- `repo/packages/skills/`: README, package.json (v4.0.529), all 12 `SKILL.md` files, and these reference files in full: `remotion-create/{video-layout,tailwind}.md`, `remotion-markup/{multi-scene-video,connected-compositions,video-editing,timing,voiceover,sequencing,transitions,compositions,parameters,calculate-metadata,sfx}.md`, `remotion-saas/{framework,player,rendering}.md`, `remotion-render/transparent-videos.md`; the first lines of every other reference file (inventory level). Scripts: `prepare-embedded-skills.ts`, `sync-agent-skills.ts` (partial).
- Plugin packages: `repo/packages/claude-code-plugin` (plugin.json, marketplace.json, build.mts, package.json), `kimi-code-plugin/.kimi-plugin/plugin.json`, `agent-plugin` (plugin.json, marketplace.json, `.codex-plugin/plugin.json`, README.cursor.md).
- `repo/packages/mcp` (README, package.json, `src/index.ts`, bundle.ts).
- `repo/packages/template-prompt-to-motion-graphics`: README, `.env.example`, `src/app/api/generate/route.ts` (full), `src/skills/index.ts`, all 8 guidance skills, `src/helpers/sanitize-response.ts`, `src/hooks/useAutoCorrection.ts`, `src/remotion/compiler.ts` (most).
- `repo/packages/template-prompt-to-video`: README, `.env.example`, `cli/cli.ts`, `cli/service.ts`, `cli/timeline.ts`, `src/Root.tsx`, `src/components/AIVideo.tsx`, `src/lib/{types,constants}.ts`.
- `repo/packages/skills-evals`: `scenarios.ts`, `src/run-skill-eval.ts` (most), `src/skill-project.ts` (start).
- Compared the installed skills `~/.claude/skills/remotion-*` (read only) with the repo skills: installed = **v4.0.528**, repo = **v4.0.529** (details in section 3.1).

### Could not read / gaps

- `https://www.remotion.dev/system-prompt.txt` (the reference system prompt that `ai/generate` and `ai/dynamic-compilation` recommend) is not mirrored. The root `llms-full.txt` in the research folder is a 404 HTML page, not content.
- MDX components that render data are not in the Markdown mirror: the list of fields that forbid forward seeking (`DisallowForwardSeekingFields`), the default codec tables (`DefaultAudioCodecs`, `DefaultVideoCodecs`), the readers table of contents, the queueing diagram (`WebCodecsQueueing`), and every twoslash `^?` type popup in `media-parser/types.md` (the types page lists type names but most shapes are only visible in the rendered site).
- Editor Starter and Timeline source code are private repos (paid); only their docs were available.
- Embedded videos (YouTube tutorial on coding agents, Mux demo of the Timeline) were not watched.

---

## 2. Mental model

### 2.1 How the areas relate

- **Making a video yourself with AI** = a coding agent (Claude Code, Codex, Kimi Code, OpenCode, Cursor, Copilot CLI) working inside a real Remotion project, guided by the official **Remotion Agent Skills** (12 skills). This is Remotion's recommended path. It has file system and shell access, runs Studio, renders.
- **Building an AI video product** = either (a) the **prompt-to-motion-graphics** approach: an LLM writes one React component as a string, the browser compiles it just in time (Babel + `new Function`) and plays it in `<Player>`; no filesystem, no OS; or (b) the **prompt-to-video** approach: LLMs produce *data* (script, image prompts, TTS audio with character timestamps) that becomes a `timeline.json`; a fixed, hand-written composition renders any timeline.
- **Steering a running Studio from a browser agent** = **WebMCP** (since 4.0.518). Only ChatGPT Codex supported it at time of writing.
- **The old Remotion MCP server** (`@remotion/mcp`, one docs-search tool) is **deprecated**; `/remotion-docs` replaces it.
- **Media inspection and processing in JS**: the Remotion-owned `@remotion/media-parser` and `@remotion/webcodecs` packages are being **phased out in favor of Mediabunny**. New code should use Mediabunny (and `<Video>`/`<Audio>` from `@remotion/media`, which are built on Mediabunny + WebCodecs). The media-parser/webcodecs docs are still useful for concepts (tracks, samples, timescales, rotation, queueing, codec copy vs re-encode).
- **Building an editor product**: Remotion sells two copy-paste codebases, the **Timeline** component and the **Editor Starter** ($600). Both treat the video as **JSON state** that is passed as `inputProps` to `<Player>` and to the renderer. This differs from normal Remotion work where React code is the source of truth.

### 2.2 Core invariants an agent must hold

1. **The frame number is the only clock.** Frames render independently, in any order, possibly twice, across parallel tabs. All motion must be derived from `useCurrentFrame()` (plus `fps`), never from CSS animations/transitions, `@keyframes`, Tailwind `animate-*`/`transition-*` classes, `setTimeout`, or wall time. Randomness is fine only when it is baked into data before render (the prompt-to-video CLI uses `Math.random()` when writing `timeline.json`, not in the component).
2. **Remotion must know when assets have loaded.** Anything loaded by CSS (`background-image`, `mask-image`) or by third-party image components (`next/image`) is invisible to Remotion and flickers. Use Remotion's media components (`<Img>`, `<Video>`/`<Audio>` from `@remotion/media`, etc.), which call `delayRender()` internally.
3. **Assets live in `public/` and are referenced with `staticFile()`**, or are remote, CORS-enabled URLs. Absolute file paths never work (browser has no filesystem access; bundle only copies `public/`).
4. **Props must be JSON-serializable and slim.** `defaultProps`/`inputProps` travel between Node and the headless browser as strings (256MB hard ceiling, often less). Pass URLs, fetch inside the component or in `calculateMetadata()`.
5. **Duration is never inferred from content.** Set it explicitly, or compute it in `calculateMetadata()` (from audio/video durations, voiceover lengths, data).
6. **Rendering uses a pinned Chrome Headless Shell** (Chrome 149.0.7790.0 from Remotion 4.0.452 on, so also on 4.0.528). Do not swap in a system Chrome.
7. **Studio interactivity is a design goal in current Remotion.** The official skills (v4.0.528/529) require markup that Studio can parse and write back to: `Interactive.*` elements, inline `style` objects, inline `interpolate()` calls with hardcoded ranges, `scale`/`translate`/`rotate` CSS properties instead of `transform` strings, inline `defaultProps` object literals, hardcoded clip timings (no `.map()` for editable clips).

### 2.3 Media data model (from media-parser/webcodecs, still valid conceptually)

- A file (container) holds **tracks**; each track yields **samples** (encoded chunks) with `timestamp` (presentation), `decodingTimestamp`, `duration`, `type` (`key`/`delta`), `data`.
- Remotion normalizes all sample timestamps to **microseconds** (`WEBCODECS_TIMESCALE = 1_000_000`), so samples can be fed straight into `EncodedVideoChunk`/`EncodedAudioChunk`.
- Decoding must start at a keyframe; seeking lands on the best preceding keyframe.
- A video can have three sizes: `codedWidth/codedHeight` (codec buffer), `displayAspectWidth/displayAspectHeight` (aspect-corrected, rotation not applied), `width/height` (what a player shows, rotation applied).
- Rotation metadata is not applied by `VideoDecoder`; you must rotate when drawing.
- Pipelines (read, decode, process, encode, write) run at different speeds; without **backpressure** memory runs away.

### 2.4 Terminology (precise meanings)

- **Bundle**: Webpack output folder (HTML, CSS, JS, `public/` assets). CLI renders bundle automatically; `bundle()` API; `npx remotion bundle`; `npx remotion lambda sites create` bundles and uploads to S3.
- **Serve URL**: a URL where a bundle is hosted (S3, Netlify, Vercel, GitHub Pages, even localhost). You can render locally from a serve URL instead of an entry point.
- **Entry point**: file that calls `registerRoot()` (default `src/index.ts`). Resolution order: CLI argument, `Config.setEntryPoint()`, then `src/index.ts`, `src/index.tsx`, `src/index.js`, `src/index.mjs`, `remotion/index.tsx`, `remotion/index.ts`, `remotion/index.js`, `remotion/index.mjs`, `src/remotion/index.tsx`, `src/remotion/index.ts`, `src/remotion/index.js`, `src/remotion/index.mjs`.
- **Root file**: exports the Root component with `<Composition>`s (usually `src/Root.tsx` or `remotion/Root.tsx`).
- **Remotion Root**: the directory commands run in, found by walking up to the nearest `package.json`; determines `public/`, `.env`, config file. `--log=verbose` prints it.
- **Composition**: component + width + height + fps + durationInFrames + id. A 1-frame composition is a `<Still>`. The Player takes these directly (no `<Composition>`).
- **Sequence**: an absolutely positioned, time-shifted "layer" (like an After Effects layer); `from` delays, `durationInFrames` trims.
- **Input props**: data passed to a render; received as React props and via `getInputProps()`; `defaultProps` are Studio placeholders that input props override.
- **Concurrency**: locally = parallel browser tabs; on Lambda = parallel chunks (`framesPerLambda`), with `concurrencyPerLambda` tabs per function; since v4.0.517 `concurrency: 1` renders on the main Lambda function.
- **Studio**: `npx remotion studio`, in `@remotion/cli`; formerly "Remotion Preview" (renamed in v4.0.0); since v4.0.93 embedded in every bundle (preview only, no rendering). **Player**: `<Player>` from `@remotion/player`, embeddable in any React app.
- **Cloud Run URL / Service name**: address or name of a deployed Cloud Run render service.

---

## 3. API digest

### 3.1 AI tooling

#### Official Agent Skills (12 skills, Agent Skills format from agentskills.io)

Install (three equivalent routes):
- From inside a Remotion project: `npx remotion skills add` (used by the coding-agents, MCP and Editor Starter setup pages; it also updates project-local skills during `npx remotion upgrade`).
- Generic skills CLI: `npx skills add remotion-dev/skills`; update with `npx skills update remotion-best-practices remotion-captions remotion-create remotion-docs remotion-interactivity remotion-maps remotion-markup remotion-multimedia remotion-render remotion-saas remotion-studio remotion-upgrade --yes`.
- Offered interactively by `bun create video` (and `create-video`).
Source: `github.com/remotion-dev/remotion/tree/main/packages/skills` (mirrored to `remotion-dev/skills`).

| Skill | Purpose | Example invocation from docs |
|---|---|---|
| `/remotion-best-practices` | Router over all other skills; use when unsure | `/remotion-best-practices Make a promo video for a record store` |
| `/remotion-create` | New project or new composition | `/remotion-create Make a promo video for a record store` |
| `/remotion-markup` | How to write Remotion React markup: compositions, animation, layout, typography, media, effects, audio, fonts, timing | `/remotion-markup Create an animated title card using Inter.` |
| `/remotion-studio` | Launch Studio preview | `/remotion-studio` |
| `/remotion-render` | Render a video or still | `/remotion-render` |
| `/remotion-maps` | Static maps, animated routes/markers, geo explainers, Mapbox, MapLibre, MapTiler, GeoJSON, CesiumJS 3D flyovers | `/remotion-maps Animate a route from Los Angeles to New York and make the camera follow it.` |
| `/remotion-captions` | Captions and subtitles | |
| `/remotion-saas` | Architecture for Remotion-powered apps and integrations | `/remotion-saas Turn my video into a SaaS.` |
| `/remotion-interactivity` | Make code editable in Studio (when elements are not selectable/editable) | |
| `/remotion-docs` | Search docs, fetch any page as Markdown | `/remotion-docs How to set up Remotion Lambda?` |
| `/remotion-upgrade` | Upgrade Remotion, related packages, compatible Mediabunny packages and installed skills | `/remotion-upgrade` |
| `/remotion-multimedia` | Browser multimedia with Mediabunny (metadata etc.) | |

What the skills actually contain (repo v4.0.529, installed v4.0.528):
- `remotion-best-practices/SKILL.md`: a router. First rule: **preserve user changes** (if code changed surprisingly between turns, assume it was intentional or ask). Then: load `remotion-create` for any "make/create/build a video" request even if a project exists; `remotion-markup` for markup; maps; multimedia; interactivity; render; studio; captions; SaaS; docs; upgrade. In the distributed build (plugin and installed copy) the sub-skills are embedded inside this folder as `REFERENCE.md` copies, because Agent Skills file references must stay inside one skill directory (the build script removes cross-skill links, keeping the link text).
- `remotion-create/SKILL.md`: inspect the folder including hidden files; if empty (only `.DS_Store`-type junk, which may be removed; never treat `.env`/`.git` as junk) scaffold in place with `npx create-video@latest --yes --blank --no-tailwind .` then `npm i`; else scaffold into a subfolder `npx create-video@latest --yes --blank --no-tailwind my-video`. Keep the scaffold and add markup following `remotion-markup` + `video-layout.md`; multi-scene videos follow `multi-scene-video.md`; start preview with `npx remotion studio --no-open` (prints URL; visit `/<composition-id>`; open in the in-harness browser if available); **render only if the user explicitly asks** (`npx remotion render`).
- `remotion-create/video-layout.md` (full rule set): "you are designing a video, not a webpage"; decide what the viewer should notice first in each scene and build the frame around it; safe area for 1080px-wide video: key text at least 80px from the sides and 100px from top and bottom; no redundant elements; minimum sizes for 1080px width: main headline 84px, important supporting text 44px; scale with composition width.
- `remotion-create/tailwind.md`: use Tailwind if installed, never `transition-*`/`animate-*` classes.
- `remotion-markup/SKILL.md` (core conventions, see 7.2): animate with `useCurrentFrame()` + `interpolate()`; customize timing with `Easing.bezier()` and `Easing.spring()`; `Interactive.Div` elements with `name`; inline `interpolate()` in `style`; `scale`/`translate`/`rotate` properties; `output: 'perceptual-scale'` for scale; assets in `public/` via `staticFile()`; media: `<Video>`/`<Audio>` from `@remotion/media`, images via `<CanvasImage>`, animated GIF/APNG/WebP/AVIF via `<AnimatedImage>` (or `@remotion/gif` if not using Chrome); most components (`AbsoluteFill`, `Interactive.*`, `Img`, `AnimatedImage`, `CanvasImage`, `HtmlInCanvas`, `Solid`, `Sequence`, `Video`, `Audio`, `Gif`) accept `from`, `durationInFrames`, `trimBefore`; fallback: wrap in `<Sequence>` (`layout="absolute-fill"` or `layout="none"`); visual effect preference order: HTML/CSS first, then effects on the element or inside `<HtmlInCanvas effects>`, preset effects before `createEffect()`; install packages with `npx remotion add <pkg>` (also for `mediabunny`, `@mediabunny/*`, `zod`, `@huggingface/transformers`); visual checks via Studio or by rendering specific frames. Reference files: `images, embedding-videos, light-leaks, measuring-text, parameters, motion-blur (4.0.529 only), transitions, text-highlights, timing, silence-detection, measuring-dom-nodes, compositions, sequencing, connected-compositions, audio-visualization, multi-scene-video, audio, 3d, voiceover, local-fonts, calculate-metadata, html-in-canvas, effects, cropping, video-editing, ffmpeg, google-fonts, lottie, gifs, sfx`.
- Highlights of the markup reference files (inventory level; the underlying APIs are covered by other agents' docs research): `cropping.md` (prefer `cropLeft/cropRight/cropTop/cropBottom` ratio props, supported on `<Sequence layout="absolute-fill">`, `<CanvasImage>`, `<Img>`, `<AnimatedImage>`, `<HtmlInCanvas>`, `<Solid>`, `@remotion/media` `<Video>`, `<Gif>`, `<RemotionRiveCanvas>`); `measuring-dom-nodes.md` (Remotion scales the container, so correct `getBoundingClientRect()` with `useCurrentScale()`); `measuring-text.md` (`@remotion/layout-utils` `measureText()`, fitting text); `text-highlights.md` (`@remotion/rough-notation`: `<Highlight>`, `<Circle>`, `<Underline>`, `<StrikeThrough>`, `<CrossedOff>`, `<Box>`, `<Bracket>`); `light-leaks.md` (Remotion 4.0.500+, `lightLeak({progress})` from `@remotion/effects/light-leak` on a `<Solid>`, typically inside `<TransitionSeries.Overlay>`); `audio-visualization.md` (`useWindowedAudioData()` from `@remotion/media-utils`); `ffmpeg.md` (`npx remotion ffmpeg` / `npx remotion ffprobe`, no install needed); `silence-detection.md` (measure loudness with `loudnorm` JSON, then `silencedetect`); `html-in-canvas.md` (`<HtmlInCanvas width height>` with `onPaint` and `ctx.drawElementImage()`); `3d.md` (`@remotion/three`); `lottie.md`, `gifs.md` (`<AnimatedImage>`), `google-fonts.md`, `local-fonts.md` (`@remotion/fonts` `loadFont()`), `images.md`, `embedding-videos.md` and `audio.md` (trim, volume, speed, loop, pitch).
- `remotion-interactivity/SKILL.md`: Studio can select, drag, resize, rotate, edit styles and keyframes only if markup is simple: `Interactive.Div` (every HTML/SVG element except `<Img>`, which is already interactive); descriptive hardcoded `name`; inline text for fixed copy; plain inline `style` objects (no constants, no spreading, no math); `interpolate()` inline with hardcoded output range/easing/extrapolation/`output`, input range may use `fps`, `durationInFrames`, `width`, `height` from `useVideoConfig()` with `n * fps`, `fps * n`, `durationInFrames - n`; only the `frame` variable is understood as input; `Interactive.Path`/`Interactive.Svg` + inline `interpolatePaths()` from `@remotion/paths` for editable path morphs (added in the 4.0.529 skill, not in the installed 4.0.528 skill); keep `<Composition>` metadata and `defaultProps` inline, no type assertions, `calculateMetadata` only for the dynamic part; effects arrays inline and stable (no conditional arrays); `Interactive.withSchema()` must include `Interactive.baseSchema`.
- `remotion-render/SKILL.md`: `npx remotion render`, `npx remotion still`; inspect frames as images with `npx remotion render [composition-id] out/frames --frames=0,30,90 --image-format=png`; transparent video recipes (ProRes 4444 `.mov`: `--image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444`; VP9 WebM: `--image-format=png --pixel-format=yuva420p --codec=vp9`; can be set as defaults via `Config` or `calculateMetadata` `defaultCodec`, `defaultVideoImageFormat`, `defaultPixelFormat`, `defaultProResProfile`).
- `remotion-studio/SKILL.md`: `npx remotion studio --no-open` (exits and prints URL if already running); flags `--log=<error|warn|info|verbose>`, `--port=<n>`, `--force-new`.
- `remotion-docs/SKILL.md`: search via Remotion's public Algolia DocSearch index (`indexName: "remotion"`), then fetch the page with a **`.md` suffix** (e.g. `https://www.remotion.dev/docs/sequence.md`) to save tokens; implement from current docs rather than memory.
- `remotion-upgrade/SKILL.md`: prefer `npx remotion upgrade` (also updates skills); manual fallback aligns every `remotion`/`@remotion/*` to one exact version and aligns `zod`, `mediabunny`, `@huggingface/transformers` (and `@mediabunny/*` to the mediabunny version) with `npm view @remotion/studio@<version> dependencies --json`; verify with `npx remotion versions`.
- `remotion-captions/SKILL.md`: captions are JSON `Caption[]` (`text`, `startMs`, `endMs`, `timestampMs|null`, `confidence|null`, `pageBreakAfter?`); references: transcribe (`@remotion/install-whisper-cpp` `transcribe()`), display (TikTok-style pages, word highlighting via `@remotion/captions`), import SRT (`parseSrt()`).
- `remotion-maps/SKILL.md`: pick exactly one technique and load only its `TECHNIQUE.md`: static map (satellite image in `<Img>`), Mapbox (key needed, globe, 3D buildings), MapLibre (free, no 3D buildings), MapTiler (annotate borders/rivers/labels), CesiumJS (terrain flythroughs). Each technique has a `render-stability.md`.
- `remotion-saas/SKILL.md` + refs: templates (Next.js `template-next-app-dir-tailwind` with Lambda; `template-vercel` Vercel Sandbox; `template-react-router` with Lambda; `template-render-server` Express/Node); Player usage; rendering choices (Node SSR, Lambda "fastest and most scalable", Vercel, GitHub Actions, Azure Container Apps, Cloudflare Containers only when asked). Lambda setup coaching steps include: store credentials in `.env` as `REMOTION_AWS_ACCESS_KEY_ID`/`REMOTION_AWS_SECRET_ACCESS_KEY` and **never ask the user to paste secrets into chat**; functions are bound to the Remotion version (redeploy after upgrades); redeploy the site after source changes; check quotas; before production handle rate limiting, auth, cost controls, output privacy, cleanup, progress/error reporting. Vue/Angular/Svelte docs links exist.
- `remotion-multimedia/SKILL.md`: Mediabunny overview at `https://mediabunny.dev/llms.txt`; helper refs `get-audio-duration`, `get-video-duration`, `get-video-dimensions`.
- `sfx.md`: `import {Audio} from "@remotion/sfx"` with ready-made hosted effects at `https://remotion.media/<name>.wav`: whoosh, whip, page-turn, switch, mouse-click, shutter-modern, shutter-old, ding, bruh, vine-boom, windows-xp-error, fah, spongebob-fail, omg-hell-nah, price-is-right-fail, romance-meme, bone-crack, anime-wow, yippee, loading-lag, wilhelm-scream, mac-quack, skedaddle, snapchat-notification, nelly-ahh, sanctuary-guardian-what, minecraft-hurt, oh-my-god-vine, illuminati-confirmed, dramatic-boomer, triggered, record-scratch.
- `voiceover.md`: ElevenLabs TTS per scene (`ELEVENLABS_API_KEY`, model `eleven_multilingual_v2`, voice settings stability 0.5, similarity_boost 0.75, style 0.3), write MP3s to `public/voiceover/<comp>/<scene>.mp3`, run the generator with `node --strip-types generate-voiceover.ts`; ask the user for a key if no provider specified; size the composition in `calculateMetadata` from audio durations; subtract transition overlaps.
- Versions: installed skills in `~/.claude/skills/remotion-*` are v4.0.528 (match our Remotion). The repo v4.0.529 adds `motion-blur.md` (`<HtmlInCanvasMotionBlur>` from `@remotion/motion-blur`, "available from Remotion 4.0.529", `shutterAngle` default 180 (0 to 360), `samples` default 8 (1 to 64)) and the `Interactive.Path` section; the rest of the diff is link rewriting.

#### Plugins (each bundles the same skills, nothing else)

| Agent | Install | Use |
|---|---|---|
| Claude Code | `claude plugin marketplace add remotion-dev/claude-code-plugin` then `claude plugin install remotion@remotion`; restart Claude Code | Claude auto-loads relevant skills; or `/remotion-best-practices <prompt>` |
| Codex (ChatGPT desktop app) | Plugins tab, search "Remotion" (or deep link) | Type `$remotion` in a new project and accept the plugin; default prompts in manifest: "Create an animated chart with 5 bars", "Make a promo video for a record store", "Use Remotion to add captions and audio to a video composition." |
| Cursor | Cursor Marketplace `cursor.com/marketplace/remotion`, or `git clone https://github.com/remotion-dev/cursor-plugin.git ~/.cursor/plugins/local/remotion`; restart or "Developer: Reload Window" | auto-load or `/remotion-best-practices` |
| GitHub Copilot CLI | `copilot plugin install remotion@awesome-copilot` | "Make a promo video for a record store using Remotion" |
| Kimi Code | `/plugins install https://github.com/remotion-dev/kimi-code-plugin`, confirm trust, `/new` or `/reload` | `/skill:remotion-best-practices` |

Manifest facts: Claude Code plugin name `remotion`, marketplace `remotion`, category Design, version tracks Remotion (4.0.529 in repo); the build (`build.mts`) copies `packages/skills/skills/*` (dropping `.tsx`) and runs `prepareEmbeddedSkills()`. There are **no hooks, commands, agents or MCP servers** in the plugin. Our machine already has the skills installed directly, so the plugin adds nothing new for us.

#### MCP (deprecated)

- Package `@remotion/mcp` (bin `remotion-mcp`), one tool `remotion-documentation` with input `{query: string}` that proxies to the hosted `https://mcp.remotion.dev` service.
- Deprecated: hosted service shuts down no earlier than **2026-08-31** (tracking issue #9055). Reasons: less current than docs, Remotion pays the tokens, MCP installs are hard and agents do not call them reliably, it duplicates `/remotion-docs`.
- Migration: remove `remotion-documentation` from the editor's MCP config, run `npx remotion skills add`, ask the agent to use `/remotion-docs`, restart the agent if skills are not detected.

#### WebMCP in Studio (since v4.0.518)

Studio exposes tools to browser agents that support WebMCP (draft web API; at time of writing only ChatGPT Codex among the major harnesses). Shapes are **not stable**. Tools that change timeline, playback or guides need an open composition. Calls affect the open Studio tab immediately.

| Tool | Since | Input | Notes |
|---|---|---|---|
| `install_package` | 4.0.523 | `{packageName, version?}` (exact semver) | Remotion packages pinned to current version; auxiliaries (e.g. `@huggingface/transformers`) at recommended version |
| `transcribe_asset` | 4.0.523 | `{assetPath?, outputPath?, model?, language?, task?: 'transcribe'|'translate', chunkLengthInSeconds?, strideLengthInSeconds?, forceFullSequences?, doSample?, temperature?, topK?, repetitionPenalty?, noRepeatNgramSize?}` | asset from `public/` (default: asset open in Studio); Jobs queue; output `Caption[]` JSON default `<asset>-captions.json`; default model `small.en`; needs `@remotion/whisper-webgpu`, otherwise returns `{success:false, error, installPackage:{tool:'install_package', packageName:'@remotion/whisper-webgpu'}}` |
| `remove_video_background` | 4.0.523 | `{assetPath?, outputPath?, model?, audio?: 'keep'|'none', videoBitrate?: 'very-low'|'low'|'medium'|'high'|'very-high'|number}` | transparent WebM in `public/`, default model `ben2-base`, audio kept, bitrate `very-high`, output `<asset>-no-background.webm`; needs `@remotion/video-matting` |
| `restart_studio` / `shut_down_studio` | 4.0.521 | `{}` | writable Studio with running server; acknowledgment only |
| `get_current_error` | 4.0.520 | `{}` | error overlay content with symbolicated frames (`originalFileName`, `originalLineNumber`, `originalScriptCode` lines), `null` if none |
| `get_compositions` / `select_composition` | | `{}` / `{compositionName}` | folder tree |
| `get_sequences` / `select_sequence` | | `{}` / `{sequenceId}` | id, name, type (`sequence|audio|video|image`), parent, depth, start/end frame, duration, stack, selectable |
| `get_composition` | | `{}` | name, stack, durationInFrames, width, height, fps, currentFrame |
| `get_canvas_html` | | `{}` | rendered HTML at current frame, capped at 100,000 chars; canvas/WebGL pixels not included |
| `get_outlines` | | `{}` | selectable element geometry in composition pixels, with source `{filename, line}` |
| `get_playback_state` | | `{}` | frame, playing, muted, volume, playbackRate, looping, timelineZoom (0 to 1) |
| `get_selection` | | `{}` | source context when exactly one item selected; `selectionType` one of guide, sequence, sequence-prop, sequence-all-effects, sequence-effect, sequence-effect-prop, keyframe, easing |
| `get_guides`, `set_guides_visible`, `add_guide`, `remove_guide` | | `{visible}`, `{orientation, position}`, `{guideId}` | positions in composition pixels |
| `play`, `pause`, `mute`, `unmute` | | `{}` | stills cannot play |
| `set_timeline_zoom` | | `{zoom}` (0 to 1, positive finite) | snapped to supported steps |
| `set_playback_rate` | | `{playbackRate}` one of -4, -2, -1, -0.5, -0.25, 0.25, 0.5, 1, 1.5, 2, 4 | negative plays backwards |
| `seek_to_frame` | | `{frame}` non-negative integer | clamped to last frame |

Example prompts from docs: "What is currently selected in the Studio?", "Fix the error", "Open the `Shapes` composition", "List the sequences and select the `Title` sequence", "Inspect the HTML rendered on the canvas", "Seek to frame 90, set the playback rate to 0.5x and play", "Add a vertical guide at 640 pixels", "Transcribe the audio asset that is currently open", "Remove the background from `product-shot.mp4`".

#### Code generation with an LLM (`ai/generate`)

- Vercel AI SDK: `npm i --save-exact ai @ai-sdk/openai zod`; `generateText({model: openai('gpt-5.2'), system, prompt})` returns `{text, usage}`.
- Example system prompt rules (paraphrased): one named export `MyComposition`; use `useCurrentFrame()` and `useVideoConfig()`; prefer `interpolate()` with `Easing` over `spring()` unless physics is asked for; inline `interpolate()` in style props; prefer `scale`/`translate`/`rotate` over transform strings; output code only.
- Raw text often includes Markdown fences: strip them.
- Structured output: `generateText({..., maxRetries: 3, output: Output.object({schema: z.object({code, title, durationInFrames, fps: z.number().min(1).max(120)})})})` returns `{output}`; AI SDK retries on schema mismatch (default `maxRetries` 2).
- Start from Remotion's `/system-prompt.txt` and tune; beware context rot as context grows.
- Skills instead of one giant prompt: classify the request with a cheap, fast model (the docs example uses `gpt-5-mini`) into categories (`charts`, `typography`, `transitions`, `spring-physics`, `3d`), load only matching Markdown, append to the base system prompt, then generate.

#### Just-in-time compilation (`ai/dynamic-compilation`)

- Transpile with `@babel/standalone`: `Babel.transform(src, {presets: ['react', 'typescript'], filename: 'dynamic.tsx'})`.
- Turn the string into a component with `new Function('React', 'AbsoluteFill', ..., code + '\nreturn DynamicComponent;')` and call it with the real modules. **Every API the code uses must be injected explicitly**; each parameter name becomes a variable in scope.
- Strip import lines (`/^import\s+.*$/gm`), extract the body from `export const X = () => {...};`, rewrap as `const DynamicComponent = () => {...}`.
- Wrap in a `useMemo`-based hook returning `{Component, error}`; show the error or render `<Player component={Component} durationInFrames={150} fps={30} compositionWidth={1920} compositionHeight={1080} controls />`.
- Security: code runs in the page's global scope. For production run it in a sandboxed `<iframe>` with a Content Security Policy.

```tsx
const transpiled = Babel.transform(`const DynamicComponent = () => {\n${body}\n};`, {
  presets: ['react', 'typescript'], filename: 'dynamic.tsx',
});
const create = new Function('React', 'AbsoluteFill', 'useCurrentFrame', 'interpolate',
  `${transpiled.code}\nreturn DynamicComponent;`);
const Component = create(React, AbsoluteFill, useCurrentFrame, interpolate);
```

#### Other AI pages

- Chatbot: CrawlChat-indexed docs; "Ask AI" button, `remotion.ai`, or `Cmd/Ctrl+I` in Studio.
- Bolt.new can prompt Remotion videos (template source `stackblitz/starters/tree/main/bolt-remotion`).

### 3.2 Mediabunny (recommended media layer)

Remotion packages using Mediabunny: `@remotion/media` (`<Video>`, `<Audio>`) and `@remotion/media-utils`. Since 4.0.355 Mediabunny is loaded from `node_modules` (not bundled). Version pairing (docs table): Remotion 4.0.524 uses Mediabunny **1.56.1**; 4.0.520 1.55.5; 4.0.513 1.55.1; 4.0.488 1.50.8; 4.0.487 1.50.7; 4.0.479 1.47.0; 4.0.462 1.45.0; 4.0.454 1.42.0; ... 4.0.342 1.13.0. There is no row for 4.0.525 to 4.0.528, so 4.0.528 should still use 1.56.1 (verify with `npx remotion versions`). Install a matching direct dependency with `npx remotion add mediabunny`; upgrade both with `npx remotion upgrade`.

Key API surface used in the docs recipes:
- `new Input({formats: ALL_FORMATS, source: new UrlSource(url) | new BlobSource(blob)})`; use `using input = ...` for automatic disposal.
- `input.getFormat()` (throws if unsupported), `input.computeDuration()` (seconds), `input.getPrimaryVideoTrack()`, `input.getPrimaryAudioTrack()`.
- Track: `canDecode()`, `displayWidth`/`displayHeight` (also async `getDisplayWidth()`/`getDisplayHeight()`), `computeFrameRateMetrics({targetPacketCount?})` returning `{probedPacketCount, bestGuessFrameRate, frameRateIsConstant, underlyingFrameRate|null, maxFrameRate}` (default probes first 256 packets).
- `new VideoSampleSink(videoTrack)`: `getSample(tSeconds)` returns `VideoSample|null`; `samplesAtTimestamps(timestamps)` async iterable (items may be null); `VideoSample` has `draw(ctx, x, y)`, `displayWidth`, `displayHeight`, `timestamp` (seconds), `close()`. Samples closed by GC print a warning; close explicitly or use `using`.
- Why Mediabunny: dependency-free, fast, works in browser, Node and Bun, supports more containers than the browser, no `<video>` mount needed, exposes fps and codec. When not: the asset is not fetchable due to CORS, then use `getVideoMetadata()` from `@remotion/media-utils` (uses a `<video>` element).

Formats for `@remotion/media` (mirrors Mediabunny):
- Containers: MP4/M4V/M4A (ISOBMFF), MOV, MKV, WebM, Ogg, MP3, WAV, ADTS AAC, FLAC, MPEG-TS, HLS `.m3u8` (VOD only).
- Video codecs: `avc` (H.264), `hevc` (H.265), `vp8`, `vp9`, `av1`, `prores` (4.0.487, opt-in).
- **HEVC cannot be decoded by `<Video>` during server-side rendering, because Chrome Headless Shell does not support HEVC in headless mode.** Transcode HEVC sources (iPhone footage) to H.264 before rendering, or use `<OffthreadVideo>` (FFmpeg based).
- Audio codecs: `aac`, `opus`, `mp3`, `vorbis`, `flac`, `pcm-u8`, `pcm-s8`, `pcm-s16`, `pcm-s16be`, `pcm-s24`, `pcm-s24be`, `pcm-s32`, `pcm-s32be`, `pcm-f32`, `pcm-f32be`, `pcm-f64`, `pcm-f64be`, `ulaw`, `alaw`, `dts` (4.0.520, opt-in), `ac3`/`eac3` (4.0.427, opt-in).
- Opt-in decoders, registered once in `src/Root.tsx`: `npx remotion add @mediabunny/prores` + `registerProresDecoder()` (faster with cross-origin isolation); `npx remotion add @mediabunny/ac3` + `registerAc3Decoder(); registerAc3Encoder();`; `npx remotion add @mediabunny/dts` + `registerDtsDecoder(); registerDtsEncoder();`.
- Codec in container support: avc/hevc in mp4, mov, mkv, ts (not webm); vp8/vp9/av1 in mp4, mov, mkv, webm; prores in mp4, mov, mkv; aac in mp4, mov, mkv, aac, ts; opus in mp4, mov, mkv, webm, ogg; mp3 in mp4, mov, mkv, mp3, ts; vorbis in mp4, mov, mkv, webm, ogg; flac in mp4, mov, mkv, flac; pcm-s16/s24/s32/f32 and pcm-u8 also in wav; ulaw/alaw in mov and wav; ac3/eac3/dts in mp4, mov, mkv, ts.
- All media must be CORS-enabled or served from the bundle via `staticFile()`.

Tag naming (`mediabunny/new-video`): `<Video>` and `<Audio>` from `@remotion/media` are the recommended tags (frame-accurate, fast extraction, minimal fetching). The old `remotion` package tags were renamed: `<Video>` became `<Html5Video>`, `<Audio>` became `<Html5Audio>` (because "users and AIs" reach for `<Video>` first). `<OffthreadVideo>`, `<Html5Video>`, `<Html5Audio>` remain for migration and fallbacks.

Known browser WebCodecs bugs (tracker page, still open at mirror time, relevant to preview and client-side rendering): Chrome software AVC decoder drops initial B-frames; 144 Hz+ monitors throttle `VideoDecoder` 5 to 10x; `VideoEncoder` ignores `visibleRect`; Chrome rejects non-IDR AVC key frames; `VideoEncoder` slows down when the page re-renders; `AudioDecoder` ignores negative timestamps (starts at 0); AMD Windows HEVC encoder marks first chunk as delta; I444AP12 unrecognized; RGBX to RGB `copyTo` garbled; encoder errors after `flush()` swallowed by `close()`; macOS VideoToolbox ignores colorSpace for H.264 (outputs bt709); `bitrateMode: 'quantizer'` initial delay; Firefox `AudioData.copyTo` interleaved f32 frameOffset bug; Safari AAC encoder wrong decoder description.

### 3.3 @remotion/media-parser (legacy, phasing out)

Every page says Media Parser is being phased out for Mediabunny; `parseMedia()` is marked deprecated in favor of Mediabunny metadata. Only use for maintaining old code or for the concepts.

- `parseMedia(options)` (since 4.0.190). Options: `src` (URL, `File`, `Blob`, or local path with `reader: nodeReader`), `fields` (`{name: true}`), `reader`, `controller`, `onVideoTrack({track, container})` and `onAudioTrack(...)` returning `null` or a per-sample callback (sample shape fits `EncodedVideoChunk`/`EncodedAudioChunk`; returning a function from the sample callback runs it after the last sample, since 4.0.307), `selectM3uStream`, `selectM3uAssociatedPlaylists`, `onParseProgress` (async pauses parsing), `progressIntervalInMs` (default 100, 0 = unthrottled), `makeSamplesStartAtZero` (default true), `seekingHints`, `logLevel` (`error|warn|info|debug|trace`, default `info`), `acknowledgeRemotionLicense`, and `on<Field>` callbacks for every field (e.g. `onDurationInSeconds`).
- Fields and cost. Header only: `name`, `size`, `container`, `mimeType` (webReader only). Metadata only: `dimensions` (rotation applied, null for audio), `durationInSeconds` (null if not in metadata), `fps` (null if not stored), `videoCodec` (`h264|h265|vp8|vp9|av1|prores|null`), `audioCodec` (`aac|mp3|aiff|opus|pcm|flac|unknown|null`), `tracks`, `unrotatedDimensions`, `isHdr`, `rotation` (0/90/180/270; **counter-clockwise since 4.0.328**, was clockwise), `location` (`latitude`, `longitude`, `altitude|null`, `horizontalAccuracy|null`), `keyframes|null`, `sampleRate`, `numberOfAudioChannels`, `m3uStreams`, `metadata`, `images` (embedded cover art). Full read: `slowStructure`, `slowKeyframes`, `slowFps`, `slowDurationInSeconds`, `slowNumberOfFrames`, `slowAudioBitrate`, `slowVideoBitrate` (bits per second). Returning a sample callback also forces a full read. Request `internalStats: true` to see `finalCursorOffset` (how many bytes were read), handy to confirm a parse stayed cheap. Remote URLs must support `Range` requests or the whole file is downloaded when metadata sits at the end.
- Readers: `webReader` (default; `@remotion/media-parser/web`), `nodeReader` (`@remotion/media-parser/node`), `universalReader` (`@remotion/media-parser/universal`, not for browsers). Custom readers implement the unstable `MediaParserReaderInterface`.
- Workers: `parseMediaOnWebWorker()` (`@remotion/media-parser/worker`, reader fixed to webReader, browser and Bun), `parseMediaOnServerWorker()` (`@remotion/media-parser/server-worker`, universalReader, only Bun has `Worker`; Deno untested). Same API minus `reader`.
- `downloadAndParseMedia({..., writer: nodeWriter('out.mp4')})` (Node/Bun; `@remotion/media-parser/node-writer`); throw inside a field callback to stop the download; `onError` returns `{action: 'download'}` (keep downloading, error thrown at end) or `{action: 'fail'}` (default: abort, delete, throw).
- `mediaParserController()`: `pause()`, `resume()`, `abort()`, `seek(seconds)` (best keyframe before time; since 4.0.291; may be called before parsing starts), `simulateSeek(seconds)` (4.0.312, returns `SeekResolution` like `{type: 'do-seek', byte, timeInSeconds}`), `getSeekingHints()` (experimental; reuse in later parses or `convertMedia`), `addEventListener('pause'|'resume')`. One controller per parse. Forward seeks throw if any "slow" field is requested. Seek quality: MP4 uses keyframes/`stsd`/`mfra`, WebM uses Cues, WAV computes, TS is not smart.
- `hasBeenAborted(err)` distinguishes deliberate aborts.
- Foreign file errors for upload classification: `IsAnImageError` (`imageType` png/jpeg/bmp/gif/webp, `dimensions`, `fileName`, `sizeInBytes`, `mimeType`), `IsAPdfError`, `IsAnUnsupportedFileTypeError`.
- Formats: MP4/MOV/M4A (H.264, H.265, AV1, AAC; fragmented OK), WebM (VP8, VP9, AV1, Opus, Vorbis), TS (H.264, H.265, AAC), MPEG-2 TS (H.264, AAC), AVI (H.264, AAC), WAV (PCM), AAC, MP3, FLAC, HLS (`.ts`, `.m4s` segments). Not supported: OGG/Opus files, DASH (planned), encrypted media, livestreams.
- HLS: `selectM3uStream({streams})` must return a stream `id` (default: highest width x height; `defaultSelectM3uStreamFn`); stream fields `dimensions`, `bandwidthInBitsPerSec`, `averageBandwidthInBitsPerSec`, `codecs`, `src`, `id`, `associatedPlaylists`; `selectM3uAssociatedPlaylists` filters audio playlists (default: single one, else those with `default: true`; `defaultSelectM3uAssociatedPlaylists`). Two-pass UI: first `fields: {m3uStreams: true}`.
- Metadata entries `{key, trackId|null, value}`; keys can repeat; e.g. `com.apple.quicktime.model`, `com.apple.quicktime.creationdate`, `encoder`, `comment` ("Made with Remotion x.y.z"); MP3 `APIC` goes to `images`.
- `MediaParserVideoTrack`: WebCodecs fields `codec`, `description`, `colorSpace`, `codedWidth`, `codedHeight`, `displayAspectWidth`, `displayAspectHeight`, plus `type`, `trackId`, `codecEnum`, `codecData`, `sampleAspectRatio`, `width`, `height`, `rotation`, `fps`, `timescale` (always 1_000_000), `originalTimescale` (native, e.g. 12800), `advancedColor`, `m3uStreamFormat`, `startInSeconds` (samples already offset). A track object can be passed straight to `VideoDecoder.configure()`.
- Runtime minimums: Node 20, Bun 1.0, Chrome 111, Edge 111, Safari 16.4, Firefox 128; feature test `typeof fetch === 'function' && typeof new ArrayBuffer().resize === 'function'`. WebCodecs decoding: Chrome 94, Edge 94, Firefox 130, Safari (video only as of May 2025).
- License: like Remotion, teams of 4+ need a company license.

### 3.4 @remotion/webcodecs (legacy, phasing out)

Install `npx remotion add @remotion/webcodecs @remotion/media-parser`. All APIs unstable. Does not run in Node for re-encoding (Node has no WebCodecs); Node can only remux (copy).

- `convertMedia(options)` (4.0.229) returns `{save(): Promise<Blob>, remove(): Promise<void>, finalState}`. Options: `src` (CORS URL, `File`/`Blob`, or local path with `reader: nodeReader` for copy only), `container` (`'mp4' | 'webm' | 'wav'`), `videoCodec` (`h264`, `h265`, `vp8`, `vp9`; defaults per container), `audioCodec` (page says only `opus`; the "convert a video" page lists Opus for WebM, AAC for MP4, PCM for WAV; the resample recipe uses `'wav'`), `expectedDurationInSeconds` (sizes the MP4 `moov`; default reserve 2MB, around 1 hour or longer can fail at the end), `expectedFrameRate` (default assumption 60), `controller` (`webcodecsController()`), `reader`, `rotate` (multiples of 90, clockwise, added on top of automatic orientation fix), `resize`, `logLevel`, `onProgress({decodedVideoFrames, decodedAudioFrames, encodedVideoFrames, encodedAudioFrames, bytesWritten, millisecondsWritten, expectedOutputDurationInMs, overallProgress})`, `progressIntervalInMs` (100), `onVideoFrame({frame})` (return same or new `VideoFrame` with identical coded/display size, timestamp, duration; inputs and outputs are closed after return, `clone()` to keep), `onAudioData({audioData})` (same pattern), `writer` (`webFsWriter` default, `bufferWriter`), `onVideoTrack`/`onAudioTrack` (override codec options), `selectM3uStream`, `seekingHints`, parse field callbacks (callback style only).
- Track operations returned by handlers: video `{type: 'copy'}`, `{type: 'reencode', videoCodec}`, `{type: 'drop'}`, `{type: 'fail'}`; audio `{type: 'copy'}`, `{type: 'reencode', audioCodec, bitrate, sampleRate | null}` (suggested bitrate 128000), `drop`, `fail`. Handler params include `track`, `defaultVideoCodec`/`defaultAudioCodec`, `inputContainer`, `outputContainer`, `canCopyTrack`, `rotate`, `resizeOperation`, `logLevel`. Async handlers pause reading.
- Defaults: `defaultOnVideoTrackHandler` copies when possible, drops if no video codec for the container (audio-only output), re-encodes with `rotation: rotate - track.rotation`, else fails. `defaultOnAudioTrackHandler` copies, drops if no audio codec, re-encodes at 128_000 bps, else fails.
- Capability checks: `canCopyAudioTrack({inputCodec, inputContainer, outputContainer, outputAudioCodec | null})` (sync boolean), `canCopyVideoTrack({inputTrack, inputContainer, outputContainer, rotationToApply, resizeOperation, outputVideoCodec | null})` (false whenever rotation must change), `canReencodeAudioTrack({track, audioCodec, bitrate, sampleRate | null})` (Promise), `canReencodeVideoTrack({track, videoCodec, resizeOperation, rotate})` (Promise). `getAvailableContainers()`, `getAvailableVideoCodecs({container})` (webm: `['vp8','vp9']`), `getAvailableAudioCodecs({container})` (webm: `['opus']`), `getDefaultVideoCodec({container})` (webm: `vp8`), `getDefaultAudioCodec({container})` (webm: `opus`).
- `ResizeOperation`: `{mode: 'max-height', maxHeight}`, `{mode: 'max-width', maxWidth}`, `{mode: 'width', width}`, `{mode: 'height', height}`, `{mode: 'max-height-width', maxHeight, maxWidth}`, `{mode: 'scale', scale}` (scale > 0). Rotation always happens before resize. To cancel automatic orientation correction, re-apply `rotate: params.track.rotation` in a custom `onVideoTrack`.
- Writers: `bufferWriter` (`@remotion/webcodecs/buffer`, resizable ArrayBuffer, max 2GB, error text contains "Could not create buffer writer"); `webFsWriter` + `canUseWebFsWriter()` (`@remotion/webcodecs/web-fs`, origin-private file system). `nodeWriter` from media-parser for Node remuxing.
- `webcodecsController()`: `pause()`, `resume()`, `abort()`, events `pause`/`resume`; check aborts with `hasBeenAborted()` from media-parser.
- `createVideoDecoder()` / `createAudioDecoder()` (4.0.307): `{track, onFrame, onError, controller?, logLevel?}`; returns `decode(sample)` (async), `waitForQueueToBeLessThan(n)`, `waitForFinish()`, `flush()`, `reset()`, `close()`, `checkReset()` returning `{wasReset()}` (4.0.312), `getMostRecentSampleInput()` (4.0.312). `onFrame` is awaited and decrements the queue only after resolving; callbacks may overlap. Audio wrapper passes `pcm-s16` through and skips samples under 16 bytes (Chrome bug). `VideoUndecodableError`/`AudioUndecodableError` (4.0.333).
- `extractFrames()` (4.0.311) and `extractFramesOnWebWorker()` (`@remotion/webcodecs/worker`, 4.0.330): `{src, timestampsInSeconds: number[] | async ({track}) => number[], onFrame(VideoFrame), signal?, logLevel?, acknowledgeRemotionLicense?}`. Docs recommend the Mediabunny recipe instead.
- `getPartialAudioData({src, fromSeconds, toSeconds, channelIndex, signal})` (4.0.328): `Promise<Float32Array>` normalized -1..1, one channel, 0.1 s padding; remote needs CORS and range requests.
- `convertAudioData({audioData, newSampleRate?, newFormat?})` (4.0.288): sample rate 3000 to 768000, clones when nothing changes, caller closes both.
- `rotateAndResizeVideoFrame({frame, rotation, resizeOperation, needsToBeMultipleOfTwo?})` (4.0.316): returns the same frame when nothing changes, else a new frame (via `OffscreenCanvas`); set `needsToBeMultipleOfTwo: true` for H.264; close the original only if a new frame came back.
- Reference apps: `remotion.dev/convert`, `remotion.dev/rotate` (source `packages/convert`).
- Debugging: the track-transformation page suggests `logLevel: "verbose"`, but the documented enum is `error | warn | info | debug | trace`; use `trace` or `debug` to see why the default handlers chose copy, re-encode or drop.

### 3.5 Timeline component (paid, copy-paste, repo `remotion-dev/timeline`)

- Setup: copy the `timeline/` folder; `npm install remotion @remotion/player @remotion/media-utils tailwindcss`; Tailwind v4: `@import './timeline/theme/timeline.css';` (customize `@theme`); Tailwind v3: use `timeline/theme/timeline-preset.mjs` in `presets`.
- Composition of providers: `TimelineProvider` (`initialState`, `onChange(newState)`) > `TimelineZoomProvider` (`initialZoom={1}`) > preview (`VideoPreview`, `ActionRow` with `playerRef`) and `TimelineContainer` (`timelineContainerRef`) > `TimelineSizeProvider` (`containerWidth`, only after the width is measured) > `Timeline` (`playerRef`). A `CanvasComposition` renders the timeline state inside the Player.
- Persistence: save from `onChange` (e.g. POST JSON). State shape lives in the provider source.
- Rendering: the sample is a frontend-only Vite app; to render, move to a template with a backend (Next.js or React Router templates include Lambda code), follow the "Player into Remotion project" guide, and pass **exactly the same JSON payload** as `inputProps` to `renderMedia()`/`renderMediaOnLambda()` (must be serializable).
- React 18 compatible (avoids `use()` and ref-as-prop). React Context for state (bring your own store if needed).

### 3.6 Editor Starter (paid template, $600, repo `remotion-dev/editor-starter`)

- Positioning: boilerplate for building your own video editor (end users edit JSON state visually), versus Studio (developers write the video as React code). Start with `npx react-router dev`. Built on React 19, TypeScript, Tailwind v4, React Router 7 (Next.js backend gists provided). Included in the Enterprise License; Timeline buyers get a refund when upgrading; source may not be redistributed or open-sourced; no evaluation license. Company License rules still apply.
- Setup: fork, `npm i`, for coding agents `npx remotion skills add` and prefer `/remotion-saas` + `/remotion-docs` (or `/remotion-best-practices`), `npm run dev`. Existing app: install dependencies, copy `src/editor`, mount `<Editor />`, implement backend routes.
- Pinned dependency set in docs (Remotion 4.0.499 era): `@remotion/{captions,cli,gif,google-fonts,lambda,layout-utils,media,openai-whisper,player,rounded-text-box,shapes,web-renderer}`, `remotion`, `mediabunny` 1.50.8, `openai`, `zod` 4.5.4, `sonner`, `@tanstack/react-virtual`, Radix context-menu/popover/select, `@aws-sdk/s3-request-presigner`, React Router 7.
- Backend routes (unprotected by default): `POST /api/captions` (transcription), `GET /api/fonts/:name` (font metadata; full metadata for all fonts would exceed 10MB), `POST /api/upload` (presigned S3 URL), `POST /api/render` and `POST /api/progress` (Lambda only).
- State (`EditorState`): `undoableState {tracks, assets (Record), items (Record), fps, compositionWidth, compositionHeight, deletedAssets[{remoteUrl, remoteFileKey, assetId, statusAtDeletion}]}`, `selectedItems`, `textItemEditing`, `textItemHoverPreview`, `itemSelectedForCrop`, `renderingTasks`, `captioningTasks`, `initialized`, `itemsBeingTrimmed`, `loop`, `assetStatus` (`pending-upload | uploaded | error | in-progress`). Last tracks render at the back. Deep nesting of context providers isolates re-renders. Return the same object when nothing changed (no re-render, no empty undo step). `useCurrentStateAsRef()` for imperative reads.
- Data model rules: an item refers to at most one asset; many items may share an asset; a track holds items of mixed types; an item belongs to one track; **items in one track may not overlap**. Item union `EditorStarterItem`: ImageItem, TextItem, VideoItem, GifItem, SolidItem, AudioItem, CaptionsItem. Asset union `EditorStarterAsset`: ImageAsset, VideoAsset, GifAsset, AudioAsset, CaptionAsset. To add a type, copy one, extend the union, run `npx tsc -w` and resolve the intentional errors. Each item type has an Inspector component; with nothing selected the composition inspector (dimensions, Render button) shows.
- Undo/redo: in-memory snapshots of `undoableState`, 50 entries; pass `commitToUndoStack` per update; do not commit drags, trims, slider scrubs until mouse release.
- Persistence: `saveState()`/`loadState()` to localStorage under a versioned key like `remotion-editor-starter-state-v1` (bump or migrate when the schema changes); only undoable state persisted; assets cached in IndexedDB (`indexeddb.ts`, `<DownloadRemoteAssets>`, `<UseLocalCachedAssets>` blob URLs, `initialize()` preloads cache); loop setting persisted separately; `#state=<base64 UndoableState>` URL loading behind `FEATURE_LOAD_STATE_FROM_URL`.
- Asset uploads to S3: bucket with public access allowed and **ACLs enabled** (else HTTP 400), CORS `AllowedMethods ["PUT","GET","HEAD"]`, origins `*`, `MaxAgeSeconds 3000`; IAM inline policy `s3:PutObject`, `s3:PutObjectAcl`, `s3:DeleteObject`; `.env`: `REMOTION_AWS_ACCESS_KEY_ID`, `REMOTION_AWS_SECRET_ACCESS_KEY`, `REMOTION_AWS_REGION`, `REMOTION_AWS_BUCKET_NAME`, optional `REMOTION_AWS_TRANSFER_ACCELERATION=true`; `MAX_FILE_UPLOAD_SIZE_IN_MB` default 1000.
- Asset cleanup: never delete while an asset may still be restored by undo; read `deletedAssets`; `deleteCachedAsset(assetId)` for IndexedDB; backend `DeleteObjectCommand` through `getAwsClient({region, service: 's3'})` from `@remotion/lambda/client` for assets whose status was `uploaded`; then `clearDeletedAsset()`.
- Captioning: OpenAI Whisper API (`OPENAI_API_KEY`), audio extracted client-side, uploaded to `/api/captions`, converted to `Caption[]`, added as `CaptionsItem`, paginated with `createTikTokStyleCaptions()`. 25MB request limit (about 13.4 minutes of 16 kHz mono); `MAX_DURATION_ALLOWING_CAPTIONING_IN_SEC`. Alternatives: `@remotion/whisper-web` (in-browser CPU, needs cross-origin isolation), `@remotion/install-whisper-cpp` (Node server), any service mapped to the `Caption` shape.
- Rendering: default Remotion Lambda (`bun deploy.ts` idempotent, or `npm run build` which silently skips deploy without AWS env vars; redeploy when state structure, visuals or Remotion version change; separate prod/dev site names e.g. by `VERCEL_ENV`); client-side rendering via `renderMediaOnWeb()` from `@remotion/web-renderer` when `ENABLE_CLIENT_SIDE_RENDERING = true` in `src/editor/flags.ts` (requires `FEATURE_NEW_MEDIA_TAGS`, on by default). Client-side tradeoffs: user must keep the tab open, no Lambda cost, WebCodecs limits, less responsive page, no ProRes, output is a temporary blob URL.
- Fonts: `@remotion/google-fonts`; top 250 Google Fonts plus TikTok Sans; regenerate with `bun src/scripts/generate-google-font-info.ts`; metadata lazy-loaded; dropdown previews load subset font files; custom fonts need a refactor to `@remotion/fonts`.
- Copy-paste: Clipboard API only supports `text/plain`, `text/html`, `image/png`; items are serialized into a `<div>` placed as `text/html` (Figma/tldraw trick) so plain text is not overwritten; pasted items get new IDs and go on top.
- Cropping: `cropLeft/Right/Top/Bottom` as ratios 0 to 1 (not pixels, to survive resizing), at least 1px left, per-axis sum below 1, images/GIFs/videos only; double-click enters Crop Mode (8 handles, faded full-frame background with opacity forced to 1); negative crops allowed while repositioning, clamped on exit.
- Snapping: magnet toggle for both timeline and canvas; `Shift+M` shortcut; canvas snaps to edges and centers; works for multi-select.
- Not included (you build it): keyframes (replace a property with an array of keyframes and `interpolate()` with `Easing`), transitions (detect adjacent items, render with `<TransitionSeries>`), project management, auto-save (`useFullState()` + `useEffect`), mobile, multiple frame rates (`DEFAULT_FPS` 30; converting means rescaling every item's `from`/`durationInFrames`), auth and rate limits, arbitrary fonts, long-audio captioning, light theme.
- Feature flags (all in `src/editor/flags.ts`): see section 7.8 for the list most relevant to agents.

### 3.7 Miscellaneous APIs and settings

- **Chrome Headless Shell** (auto-installed into `node_modules/.remotion/chrome-headless-shell/<platform>/`, platforms `mac-arm64`, `mac-x64`, `linux64`, `linux-arm64` (headless shell only), `win64`): pre-install with `npx remotion browser ensure` or `ensureBrowser()`. Version file `VERSION` (4.0.415) triggers re-download on mismatch. Chrome versions: from 4.0.452 **149.0.7790.0**; from 4.0.414 144.0.7559.97; from 4.0.315 134.0.6998.35; from 4.0.274 133.0.6943.141; from 4.0.245 123.0.6312.86. Chrome for Testing (GPU-bound work, emulated display, more deps) only for Linux GPU rendering: CLI `--chrome-mode="chrome-for-testing"` (render, benchmark, compositions, still, gpu, browser ensure), API `chromeMode: 'chrome-for-testing'`, Studio Advanced "Chrome Mode", `Config.setChromeMode('chrome-for-testing')`; not on Lambda or Cloud Run. Bring-your-own browser via `setBrowserExecutable()`/`browserExecutable` is discouraged (less deterministic). History: Thorium 4.0.18 to 4.0.135; plain Chromium before 4.0.18 (no H.264/H.265).
- **GPU in the cloud** (Remotion >= 4.0.248): request the "Running On-Demand G and VT instances" quota, launch EC2 `g4dn.xlarge` (about $375/month) from community AMI `ami-06a1f46caddb5669e` (Ubuntu 22.04, us-east-1), upgrade the kernel, install Linux deps, `libvulkan1`, NVIDIA driver 535.104.12 and an `nvidia-smi` startup service, Node 20; verify with `npx remotion gpu --chrome-mode="chrome-for-testing" --gl=vulkan`; render with the same flags. Warnings like `vkCreateInstance() failed: -7` can appear while the render is still GPU accelerated. The Docker variant page is marked outdated (it used `--gl=angle-egl`).
- **Cross-origin isolation**: headers `Cross-Origin-Embedder-Policy: credentialless` (or `require-corp` for Safari or credentialed cross-origin loads) and `Cross-Origin-Opener-Policy: same-origin`; Studio: `Config.setEnableCrossSiteIsolation()` or `--cross-site-isolation`; check `window.crossOriginIsolated`. Needed for `SharedArrayBuffer` (`@remotion/whisper-web`) and fast ProRes decoding; side effect: cross-origin `<Html5Video>`, `<Html5Audio>`, `<OffthreadVideo>`, `<Img>` need CORS (`crossorigin="anonymous"`).
- **Linux multi-process Chrome**: default on since 4.0.137 (`--enable-multi-process-on-linux=false`, `chromiumOptions.enableMultiProcessOnLinux`, `Config.setChromiumMultiProcessInLinux()`); Lambda is forced single-process (prefer more Lambdas over more tabs per Lambda).
- **Temp dir**: `TMPDIR` (macOS/Linux) or `TEMP` (Windows), e.g. `TMPDIR=/var/tmp npx remotion render`.
- **Linux dependencies** (Chrome Headless Shell): Ubuntu 22.04/24.04 `libnss3 libdbus-1-3 libatk1.0-0 libasound2t64 libxrandr2 libxkbcommon-dev libxfixes3 libxcomposite1 libxdamage1 libgbm-dev libcups2 libcairo2 libpango-1.0-0 libatk-bridge2.0-0` (older Ubuntu and Debian use `libasound2`); Amazon Linux 2023 has its own `yum` list; Alpine and NixOS unsupported.
- **Emojis** are OS fonts: install `fonts-noto-color-emoji` (Debian/Ubuntu) or `google-noto-emoji-color-fonts` (AL2023) in Docker; Lambda ships Noto Color Emoji, Apple emoji optional (IP risk), and lacks "facing right" variants and mixed skin-tone couple/family emojis.
- **FFmpeg**: Remotion ships a GPLv2+ FFmpeg (x264/x265 are GPL; uses `fdk-aac-free`); patents are a separate matter. `npx remotion ffmpeg` / `npx remotion ffprobe` exist, so no system FFmpeg is needed.
- **Next.js**: prefer the Vercel template; self-hosted Next needs `serverExternalPackages: ['@remotion/renderer']`, never use `@remotion/bundler` inside an API route, ensure the `remotion` compositor binary ships with the route.
- **Not possible**: embedding Studio as a component (use Player with your own UI, or deploy Studio to a server), live streaming (use OBS browser sources or Software Mansion's Live Compositor; Remotion can make OBS stinger transitions), rendering on edge runtimes (no fs, 30 s Vercel / 10 ms Cloudflare, 4 to 5MB code limits versus ~150MB, 128MB RAM versus 2GB+ recommended), automatic duration from content.
- **Browser rendering** exists via `@remotion/web-renderer` (`renderMediaOnWeb()`, `canRenderMediaOnWeb()`).
- **Video formats**: server-side H.264 MP4, H.265, VP8/VP9 WebM, AV1 (not on Lambda or Linux ARM64 GNU), ProRes, GIF; client-side MP4, WebM, MKV, MOV plus audio-only WAV, MP3, AAC, OGG, FLAC with H.264/H.265/VP8/VP9/AV1 depending on browser. Input decode: `<Video>` per Mediabunny/WebCodecs; `<Html5Video>` per browser (Chrome while rendering); `<OffthreadVideo>` per FFmpeg (most codecs at render time).

---

## 4. Recipes

### 4.1 Prompting a video with a coding agent (Remotion's documented flow)

1. Install Node and an agent (Claude Code, Codex, Kimi Code, OpenCode; most need a paid plan).
2. `npx create-video --yes --blank my-video` (Blank template), `cd my-video`, `npm install`.
3. `npx remotion skills add` (installs the 12 Agent Skills into the project).
4. `npm run dev` (Studio preview) in one terminal.
5. In a second terminal inside the project: `claude` (or `codex`, `kimi`, `opencode`) and prompt the video. Example prompts used by Remotion: "Make a promo video for a record store", "Create an animated title card using Inter.", "Animate a route from Los Angeles to New York and make the camera follow it.", "Create an animated chart with 5 bars", "Use Remotion to add captions and audio to a video composition."

Remotion's own eval prompts (`repo/packages/skills-evals/scenarios.ts`) show the kind of brief that works well: state format and orientation (vertical for Instagram/TikTok, landscape for YouTube pre-roll or a website hero), exact phrases to include as a bullet list, visual vocabulary ("a few animated shapes, simple app-style cards, smooth transitions"), exact size/colors/data values ("1920x1080 dark-themed (#1A1A2E)", revenue values per month, line color #0B84F3), animation feel ("bars animate sequentially with slight overlap", "spring-based timing over 120 frames at 30fps", "ease-out for pressing, then a spring with a slight bounce"), target length ("around 10 seconds"), output ("Render it as a transparent ProRes video"), and even data gathering steps ("use curl to scrape the channel avatar and subscriber count"). The eval harness then sends a second prompt: render the final MP4 to an exact path, do not leave it only in `/tmp`, do not stop at a still.

The prompt-to-motion-graphics README adds prompting tips: be specific about colors, timing and layout ("green sent bubbles on the right, gray received on the left"); put chart data directly in the prompt; describe the motion feel ("bouncy spring entrance", "smooth fade", "staggered timing"); reference images by URL when they should appear in the video.

### 4.2 Writing markup the way the official skills want (Studio-editable)

```tsx
const {fps} = useVideoConfig();
const frame = useCurrentFrame();
<Interactive.Div name="Title" style={{
  fontSize: 88,
  opacity: interpolate(frame, [1 * fps, 2 * fps], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  }),
  scale: interpolate(frame, [0, fps], [0.8, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.spring({damping: 200}), output: 'perceptual-scale',
  }),
}}>Title</Interactive.Div>
```
- Multiple keyframes take an `easing` array with n-1 entries; `posterize: 3` samples every third frame for a stepped look.
- Use `transform` strings only for what the individual properties cannot express (`skew()`, `perspective()`, order-sensitive chains).
- Delay/trim with `from`, `durationInFrames`, `trimBefore` directly on components; always premount sequences (`premountFor={1 * fps}`).

### 4.3 Multi-scene video with connected compositions

- One file and component per substantial scene; parent uses `<TransitionSeries>` (if transitions) or `<Series>` (plain cuts) or `<Sequence>` (free placement), each sequence with a hardcoded `name` and inline `durationInFrames`.
- Register every scene component again in `Root.tsx` inside `<Folder name="MyVideo-Scenes">` with the same component reference, its own id, dimensions, fps and natural duration, plus the parent composition. Studio then shows the scene as a nested, double-clickable timeline (like an After Effects precomp).
- Keep scene `defaultProps` in sync with the props the parent passes (registration does not copy them).
- Duration math: sum of sequences minus each transition's `timing.getDurationInFrames({fps})`; overlays (`<TransitionSeries.Overlay durationInFrames offset>`) do not change the total; an overlay may not sit next to a transition or another overlay.

### 4.4 Voiceover-driven timing

- Generate one audio file per scene into `public/` (ElevenLabs in the official skill; any TTS works). Measure each with Mediabunny (`input.computeDuration()`) inside `calculateMetadata`, set `durationInFrames = Math.ceil(sum * fps)` and pass per-scene frame counts as props; subtract transition overlaps.
- Keep API keys in env vars only.

### 4.5 Prompt-to-motion-graphics (SaaS pattern; `template-prompt-to-motion-graphics`)

Scaffold: `npx create-video@latest --template prompt-to-motion-graphics`; `.env` with `OPENAI_API_KEY`; `npm run dev` (Next.js on port 3000); optional Lambda export with `REMOTION_AWS_ACCESS_KEY_ID`/`REMOTION_AWS_SECRET_ACCESS_KEY` and `npm run deploy`.

Pipeline in `src/app/api/generate/route.ts`:
1. **Validation** (skipped for follow-ups): a classifier call (`generateObject`, schema `{valid: boolean}`) accepts animated text, data viz, UI animations, logo intros, social content, explainers, countdowns, loaders, abstract motion; rejects questions, written-content requests, chat, non-visual tasks. If the classifier errors, the request is let through.
2. **Skill detection**: `generateObject` with `z.array(z.enum(SKILL_NAMES))`. 8 guidance skills (`charts`, `typography`, `social-media`, `messaging`, `3d`, `transitions`, `sequencing`, `spring-physics`) and 9 example skills (`example-histogram`, `example-progress-bar`, `example-text-rotation`, `example-falling-spheres`, `example-animated-shapes`, `example-lottie`, `example-gold-price-chart`, `example-typewriter-highlight`, `example-word-carousel`). Skills already used in the conversation are not re-sent.
3. **Generation**: streamed (`streamText`) with the base system prompt plus "SKILL-SPECIFIC GUIDANCE". Base prompt rules: ES imports then `export const MyAnimation = () => {...}`; body order = short description comment, hooks, UPPER_SNAKE_CASE constants for colors/text/timing/layout **inside the component after hooks** (so users can tweak them), derived values, JSX; use full width with padding, responsive sizes via `Math.max(min, Math.round(width * pct))`; `spring()` for organic motion, `interpolate()` for linear progress, always clamp both sides, stagger multiple elements; allowed imports (remotion core, `@remotion/transitions` + fade/slide, `@remotion/shapes`, `@remotion/three`, React hooks); never shadow API names (`spring`, `interpolate`, ...); inline styles only; `fontFamily: 'Inter, sans-serif'`; 2 to 4 colors; background color set on `AbsoluteFill` from frame 0 (never fade in the background); output only code starting with `import` and ending with `};`; never ask clarifying questions, make a reasonable choice.
4. **Follow-ups**: a second system prompt decides `type: 'edit'` (search/replace list for small changes, under ~30% of code) or `type: 'full'` (over ~50% or "start fresh"); `old_string` must match exactly and uniquely; recent 6 messages of history included; manual user edits flagged and preserved. Edits that are not found or ambiguous return `edit_failed` with the failed edit.
5. **Sanitize**: strip Markdown fences, check for JSX, cut trailing commentary by brace counting from the `export const` line.
6. **Compile** (`src/remotion/compiler.ts`): remove all import forms, extract the body (keeping helper code above the export), Babel transform, `new Function` with a fixed injected set: React hooks, `AbsoluteFill`, `interpolate`, `useCurrentFrame`, `useVideoConfig`, `spring`, `Sequence`, `Img`, all `@remotion/shapes` components and `make*` helpers, `Lottie`, `ThreeCanvas`, `THREE`, `TransitionSeries`, `linearTiming`, `springTiming`, `fade`, `slide`, `wipe`, `flip`, `clockWipe`.
7. **Self-correction** (`useAutoCorrection`): if the last code came from the AI (not a user edit) and compilation or the API fails, automatically send "Fix the compilation error" / "Retry the previous request" with the error, attempt number and max attempts; the prompt tells the model to fix only the error, or to add more context to `old_string`.
- Images: attaching an image makes the model try to **replicate** it in code; giving a URL makes it **embed** the image (e.g. "Create a DVD screensaver animation of this image https://example.com/logo.png"). The route also accepts `frameImages` (base64 captures) as visual context for edits.
- Guidance skill craft notes worth reusing: typewriter by string slicing (not per-character opacity); cursor blink via smooth `interpolate` over `frame % 16`; word carousel width fixed by rendering the longest word invisibly; highlight via two crossfading layers; social: safe zone top 12% / bottom 15% / sides 5% of size, headline `Math.max(48, width * 0.08)`, body `Math.max(28, width * 0.045)`, motion from frame 0, saturated colors, loop-friendly ending; charts: 3 to 5 frame stagger, always a Y axis, value labels inside bars after they grow, pie segments via `strokeDasharray`/`strokeDashoffset` rotated -90 degrees; chat: sent right/received left, `maxWidth: '70%'`, staggered slide+fade, WhatsApp dark and iMessage light palettes; 3D: always `ThreeCanvas` with ambient + directional light, camera `[0, 0, 5]` fov 75; spring presets: snappy `{damping: 20, stiffness: 200}`, bouncy `{damping: 8, stiffness: 100}`, smooth `{damping: 200, stiffness: 100}`, heavy `{damping: 15, stiffness: 80, mass: 2}`.

### 4.6 Prompt-to-video (data pipeline pattern; `template-prompt-to-video`)

- `npm run gen` asks for a title and topic (history, ELI5, fun facts, science work well); needs `OPENAI_API_KEY` and `ELEVENLABS_API_KEY` (prompted if missing).
- Steps: (1) story of 8 to 10 sentences in English via structured JSON output; (2) 5 to 8 detailed image descriptions each mapped to 1 to 2 sentences, in order, "visually appealing, not just characters"; (3) images at 1024x1792 with 3 retries; (4) ElevenLabs `convertWithTimestamps` voice per segment, keeping character start/end times; (5) `timeline.json` with `elements` (background image per segment, `blur` enter/exit, Ken Burns scale alternating 1.5 to 1 and 1 to 1.5), `text` (subtitle chunks of at most 14 characters timed from character timestamps, each with a randomized pop scale baked into data), `audio` (one clip per segment), `shortTitle`.
- Rendering side: `Root.tsx` uses `getStaticFiles()` to find every `public/content/<slug>/timeline.json` and registers one 1080x1920, 30 fps composition per story; `calculateMetadata` loads the timeline, sets `durationInFrames = timelineFrames + 30` (1 s intro title card) and injects it as a prop; the component maps elements to `<Sequence from durationInFrames premountFor={3 * FPS}>`, subtitles to sequences, and audio to `<Audio from durationInFrames premountFor>` from `@remotion/media`; Google Font Bree Serif; yellow boxed intro title.
- For server use: pass a timeline URL as a prop instead of a project name and host generated assets remotely.

### 4.7 Match the composition to a source video (Mediabunny)

```ts
export const calculateMetadata: CalculateMetadataFunction<{src: string}> = async ({props}) => {
  using input = new Input({formats: ALL_FORMATS, source: new UrlSource(props.src)});
  const track = await input.getPrimaryVideoTrack();
  const [m, seconds] = await Promise.all([track?.computeFrameRateMetrics() ?? null, input.computeDuration()]);
  const fps = m === null || m.probedPacketCount < 2 ? 30 : m.bestGuessFrameRate;
  return {fps, durationInFrames: Math.floor(seconds * fps)};
};
```
Remotion timelines are constant frame rate. For variable frame rate footage (screen recordings) never use the average fps (it drops frames); `bestGuessFrameRate` snaps to a detected underlying rate; `maxFrameRate` can explode if two samples are very close.

### 4.8 Editor/QA helpers

- **Can the browser decode this before I mount `<Video>`?** `getFormat()` in try/catch, then `track.canDecode()` for primary video and audio tracks.
- **Thumbnail**: `new VideoSampleSink(track).getSample(t)`, draw to a canvas, `sample.close()`.
- **Filmstrip**: number of frames `n = ceil(canvasWidth / (canvasHeight * aspect))`, timestamps `from + (duration / n) * (i + 0.5)`, iterate `samplesAtTimestamps()` with `using`, abort via `AbortSignal`, timeout via `Promise.race`.
- **Classify an upload in one pass** (legacy): catch `IsAnImageError`/`IsAPdfError`/`IsAnUnsupportedFileTypeError`.
- **Visual self-check for agents**: `npx remotion render <id> out/frames --frames=0,30,90 --image-format=png`, or `npx remotion still`; in Studio via WebMCP: `get_canvas_html`, `get_outlines`, `get_current_error`.

### 4.9 Media fix-ups

- **MediaRecorder WebM** (no duration, slow seek, no Safari): remux `convertMedia({src: blob, container: 'webm'})` (fast, moves cues/metadata to the front) or re-encode to `container: 'mp4', videoCodec: 'h264', audioCodec: 'aac'`; server: `ffmpeg -i in.webm -c copy out.webm` or `-c:v libx264 -c:a aac out.mp4`.
- **16 kHz mono WAV for Whisper**: `npx remotion ffmpeg -i input.mp4 -ar 16000 output.wav -y` (or in-browser `convertMedia` to `wav` with `sampleRate: 16000`).
- **Transparent outputs**: ProRes 4444 `.mov` for editors, VP9 `yuva420p` WebM for browsers (see 3.1 render skill).
- **Background removal / transcription from Studio**: WebMCP `remove_video_background` (needs `@remotion/video-matting`) and `transcribe_asset` (needs `@remotion/whisper-webgpu`).

### 4.10 Composition-level snippets

- **Combine compositions**: a `Main` with `<Series>` of `<Series.Sequence durationInFrames>` scenes; export duration constants; register `Main` with the sum; `<TransitionSeries>` shortens the total by transition lengths; scale up with scene arrays and `calculateMetadata`.
- **Freeze parts of a sequence**: `<Freeze frame={f} active={bool}>` around `<Sequence layout="none" from={offset}>`, with precomputed cumulative freeze offsets so content resumes where it paused.
- **Player in an iframe**: portal `<Player>` into an iframe body (margin/padding 0) and size the iframe with a `ResizeObserver` on the element with class `__player`; isolates global CSS.
- **Serve large local folders instead of copying**: `npx serve --cors <dir>` and pass URLs (or `serve-handler` programmatically).

### 4.11 Rendering an editor's state

- The JSON state is the `inputProps`; render with the exact same payload the `<Player>` receives (`renderMediaOnLambda()`, `renderMedia()`, or `renderMediaOnWeb()`); the composition in the Editor Starter lives in `src/remotion` and also works with `npx remotion studio` / `npx remotion render`.

---

## 5. Performance and render stability

- **Never bundle at runtime.** Bundle once at build time (Lambda: `deploySiteFromBundle()` or `npx remotion lambda sites create`; long-running server: call `bundle()` once and reuse). Parametrize with input props and `calculateMetadata`.
- **Timeouts**: error messages report the elapsed wait (examples in the docs: 28000ms for media/root, 58000ms for a font); the render `--timeout` default is 30 s and also governs page functions (before 4.0.73 page functions had a fixed 5 s). Giant custom timeouts can hang a render silently, especially on Lambda where the function timeout fires first. Always pair `delayRender()` with `continueRender()` and `cancelRender(err)` in the error path.
- **"Timed out evaluating page function"** means the browser is overloaded (CPU/memory), not a missing `continueRender`. Lower `--concurrency`, add resources, raise `--timeout`, look for heavy or infinite loops.
- **Memory**: the OffthreadVideo frame cache grows up to 50% of available memory at render start and halves under pressure; OOM kills show as SIGKILL of the compositor or FFmpeg. Lower `offthreadVideoCacheSizeInBytes`, lower concurrency, upgrade (memory work through 4.0.171), add RAM. Setting the cache too small causes "No frame found at position".
- **`<OffthreadVideo>` downloads the whole file** before extracting a frame; big files cause proxy `<Img>` timeouts. Prefer `<Video>` from `@remotion/media` (partial fetching), split big sources into parts in a `<Series>`, host close to the renderer on a CDN with enough egress. Stock sites like Pexels throttle repeated hotlinked requests from many Lambdas: re-host.
- **HEVC sources fail with `<Video>` during SSR** (no HEVC in Chrome Headless Shell): transcode first.
- **Fonts**: `loadFont()` with no arguments loads every weight and subset (slow, timeouts); from v5 it throws without non-empty `weights` and `subsets`. Load only what you use, e.g. `loadFont('normal', {subsets: ['latin'], weights: ['400', '700']})`, centralized in one module.
- **Props size**: `defaultProps`/composition list must serialize under 256MB (often less). Keep props as URLs and small values.
- **Chrome**: keep the pinned Chrome Headless Shell; pre-download it with `npx remotion browser ensure`; do not install Chrome from a Linux package manager; Remotion >= 4.0.208 ignores system browsers. Multi-process Chrome on Linux is on by default (except Lambda).
- **GPU/WebGL**: WebGL effects need `--gl=angle` (or `chromiumOptions: {gl: 'angle'}`, `Config.setChromiumOpenGlRenderer('angle')`, Studio Advanced "OpenGL render backend"); machines without GPU use `--gl=swangle` (Lambda default). Cloud GPU rendering needs Chrome for Testing + `--gl=vulkan`.
- **Text jitter**: Chrome snaps text to whole pixels; slow text moves oscillate. Add `transform: 'perspective(100px)'` and `willChange: 'transform'`, ideally only while rendering (`getRemotionEnvironment()`), because `will-change` costs resources.
- **Apple Silicon**: run native arm64 Node (Rosetta is up to 2x slower); check `arch` and `node -p process.arch`.
- **Temp disk**: renders write frames and uncompressed audio to the temp dir; redirect with `TMPDIR`/`TEMP` if the disk is small.
- **Player flicker** (preview only, not in renders): premount (`premountFor`, since 4.0.140, most effective), pause when buffering (default on for `@remotion/media` tags; `pauseWhenBuffering` on Html5Video/OffthreadVideo/Html5Audio, `pauseWhenLoading` on `<Img>`), preload hints; prefetch to blob/base64 is memory hungry and rarely worth it.
- **Browser-side pipelines** (WebCodecs): throttle each stage (async callbacks, `waitForQueueToBeLessThan(10)`), close every `VideoFrame`/`AudioData`/`VideoSample` (or `using`), stop feeding a decoder whose `state` is `closed`, handle `reset()` races with `checkReset()`. Buffer writers cap at 2GB; prefer the OPFS writer. Pass `expectedDurationInSeconds` for long MP4 outputs.
- **Edge runtimes cannot render.** AV1 output is not available on Lambda or Linux ARM64 GNU; ProRes output is available on Lambda (the Editor Starter lists it as a Lambda advantage over client-side rendering).
- **Client-side rendering** blocks the tab (user must stay), may reduce responsiveness, and yields only a blob URL.

---

## 6. Errors and fixes

| Error text (or symptom) | Cause | Fix |
|---|---|---|
| Image flickers; `backgroundImage: url(...)` or `maskImage` | CSS loads are invisible to Remotion | Use `<Img>` in stacked `<AbsoluteFill>` layers; if a mask is required, also render a hidden `<Img src={same}>` (opacity 0, `position: absolute`, `left: -100%`) so it is awaited |
| Image flickers with `next/image` `<Image>` | Same | Use Remotion `<Img>` |
| Animation wrong/flickers with `animation: fadeIn 1s`, `transition`, `@keyframes`, `setTimeout`, Tailwind `animate-*` | Frames render out of order and in parallel | Derive from `useCurrentFrame()` + `interpolate()`/`Easing` |
| Studio does not update after saving | Studio process quit, or import casing differs from filename (webpack watchpack bug) | Restart `npx remotion studio`; fix import capitalization |
| `Failed to launch the browser process!` | Missing Linux shared libs, or wrong OS/arch binary | Install Linux deps; use matching binary; debug with `--log=verbose` |
| `Module not found: Can't resolve 'module'` (bundler/webpack) or `Module parse failed: Unexpected character` for `@remotion/compositor-*` | `bundle()`/`deploySite()` itself got bundled (e.g. inside a Next.js function) | Bundle at build time; reuse the bundle or deploy with `deploySiteFromBundle()` / `lambda sites create` |
| `Can't save default props: Could not find or extract defaultProps for composition "<id>".` | No `defaultProps`, `id` not a JSX string literal, `defaultProps` not an inline object literal, root file not found, or root not TypeScript | TS root in a standard path (`src/Root.tsx`, `remotion/Root.tsx`, `app/remotion/Root.tsx`, `src/remotion/Root.tsx`, or `XRoot.tsx` next to `x-entry.tsx`), `id="my-comp"`, inline `defaultProps={{...}}` (`staticFile()` and `new Date('...')` allowed since 4.0.475). Suggested agent prompt: find the root that registers the composition and make the id and defaultProps statically analyzable without changing values or behavior |
| `The source provided ([...]) could not be parsed as a value list.` | FontFace `src` without quotes (old Chrome, e.g. 104 on Lambda) | `url('font.woff2') format('woff2')`; prefer `@remotion/fonts` |
| `npm ERR! could not determine executable to run` | `@remotion/cli` missing (the `remotion` binary lives there) or Corepack `packageManager` is pnpm/yarn/bun | Install `@remotion/cli`; use `pnpm exec`, `yarn`, or `bunx` |
| `defaultProps too big - could not serialize ...` (with or without composition id) | Props or the whole composition list too large to stringify (limit 256MB, sometimes less) | Pass URLs; fetch/derive inside the component or `calculateMetadata` |
| `A delayRender() "Loading <Img> with src=http://localhost:3000/proxy?src=...&time=...&transparent=..." was called but not cleared after 28000ms` | `<OffthreadVideo>` could not extract a frame in time (full download, seek, decode) | Use `<Video>` from `@remotion/media`; raise `delayRenderTimeoutInMilliseconds`; verbose logs; split video into `<Series>` parts; faster/closer hosting |
| `A delayRender() 'Loading <Html5Video> duration with src="https://videos.pexels.com/..."' ... 28000ms` | Pexels throttles repeated requests from many Lambdas | Use `@remotion/media` `<Video>`; re-host media on your own server/S3 |
| `A delayRender() "Fetching Inter font {...}" was called but not cleared after 58000ms` | `loadFont()` without args loads all weights/subsets | `loadFont('normal', {subsets: ['latin'], weights: ['400','700']})`; in v5 args are mandatory |
| `A delayRender() "Loading root component" was called but not cleared after 28000ms` | Entry point does not call `registerRoot()` (you passed `Root.tsx` or a component) | Pass `src/index.ts` (the file calling `registerRoot`) to the CLI or `bundle({entryPoint})` |
| `Compositor error: No frame found at position ... for source ...` | OffthreadVideo cache too small (frames evicted) or the video has gaps (VFR screen recording) | Raise `offthreadVideoCacheSizeInBytes` (below real RAM) or add memory; report gap videos; prefer `<Video>` from `@remotion/media` |
| Blank frames in Player when a later clip starts | Clip starts loading only when it appears | Premount, pause-when-buffering, preload (render output unaffected) |
| `Apple Silicon detected but running under Rosetta ...` | x86 Node on M-series Mac | Install and run arm64 Node (`arch -arm64 zsh`, then install Node) |
| `Compositor quit with signal SIGKILL` / `FFmpeg quit with code null (SIGKILL)` | OOM kill | Lower `offthreadVideoCacheSizeInBytes`, lower concurrency, update Remotion, add RAM |
| Render stuck without error | `delayRender` never cleared with a huge timeout; wrong Chrome (no headless mode); Lambda: errors not read | Smaller timeout + `cancelRender()`; use Chrome Headless Shell (`npx remotion browser ensure`, no `--chrome-executable`); read `errors` from `getRenderProgress()` and stop polling when `fatalErrorEncountered` |
| Text shimmers while moving slowly | Chrome pixel-snaps text | `transform: 'perspective(100px)'` + `willChange: 'transform'` (render-only) |
| `Error: Timed out evaluating page function (f, c) => { window.remotion_setFrame(f, c); }` | Browser overloaded | Lower `--concurrency`, add CPU/RAM, raise `--timeout`, optimize code, check infinite loops |
| Rendered video "has no sound" | VS Code/Cursor preview plays muted; or no audio source, `volume={0}`, or audio not mounted in its `<Sequence>` range | Open in QuickTime/IINA/VLC/mpv; add `<Audio>`/`<Video>` from `@remotion/media`; check volume and sequence timing |
| `Failed to acquire WebGL2 context for blur effect. Pass --gl=angle ...` | No WebGL2 context with default GL backend | `--gl=angle` (CLI), `Config.setChromiumOpenGlRenderer('angle')`, `chromiumOptions: {gl: 'angle'}` in SSR/Lambda/Vercel APIs, Studio Advanced setting; no-GPU machines `--gl=swangle` |
| `'MemorySize' value failed to satisfy constraint: Member must have value less than or equal to 3008` (Editor Starter `deploy.ts`) | AWS account limits (free tier / low concurrency) | Lower `MEM_SIZE_IN_MB` |
| HTTP 400 when uploading assets to S3 (Editor Starter) | Bucket ACLs disabled | Enable ACLs on the bucket |
| Error containing `Could not create buffer writer` | `bufferWriter` output above 2GB | Use `webFsWriter` |
| `Unsupported configuration. Check isConfigSupported() prior to calling configure().` | Chrome reports some configs (e.g. Opus 6 channels at 44100 Hz) as supported but fails | Treat `isConfigSupported()` as unreliable; catch and fall back |
| `AudioUndecodableError` / `VideoUndecodableError` | Browser cannot decode the track | Skip or transcode on the server |
| Error when seeking forward in media-parser | A "slow" field needs every sample | Do not request slow fields when seeking, or use Mediabunny |
| `IsAnImageError` / `IsAPdfError` / `IsAnUnsupportedFileTypeError` | Non-media upload | Branch on the error type (image type and dimensions are provided) |
| `HtmlInCanvas` shows nothing in the browser preview | Per the official skill it needs Chrome 149+ with `chrome://flags/#canvas-draw-element` enabled; nesting is rejected | Tell the user to enable the flag; never nest `<HtmlInCanvas>`; render with `--gl=angle` if WebGL is used (render-side behavior belongs to the effects/canvas research, not this area) |
| HEVC video blank or failing during server render with `<Video>` | Chrome Headless Shell lacks HEVC | Transcode to H.264 or use `<OffthreadVideo>` |
| Emojis look different or missing on Linux/Lambda | OS emoji fonts differ; Lambda removed some emoji sets | Install Noto Color Emoji; avoid "facing right" and mixed skin-tone couple emojis on Lambda |
| Absolute path asset (`C://...`) does not load | Browser has no file access; only `public/` is bundled | Copy to `public/` + `staticFile()`, or serve with `npx serve --cors` |
| `WebMCP transcribe_asset` returns `success: false` with `installPackage` | Optional package missing | Call `install_package` with the returned name, then retry |

Debugging order for any failed render: `--log=verbose` (or `verbose: true`), set `--concurrency=1` to de-duplicate logs, add `console.log`, remove components one by one, search GitHub issues and docs (use `/remotion-docs`), then ask on GitHub/Discord.

---

## 7. What our skills must teach

### 7.1 Agent workflow (autonomous video creation)

- Before creating a project, inspect the folder (including hidden files). Empty: `npx create-video@latest --yes --blank --no-tailwind .` then `npm i`. Non-empty and no project: scaffold into a subfolder. Never delete `.env`, `.git` or user files.
- Ensure Agent Skills are present (`npx remotion skills add`), or rely on our own skills; they are already installed at `~/.claude/skills/remotion-*` (v4.0.528, matching Remotion 4.0.528).
- Look up APIs in current docs instead of memory: fetch `https://www.remotion.dev/docs/<page>.md` (the `.md` suffix returns Markdown), or use the local mirror.
- Preview with `npx remotion studio --no-open` (reuse the running instance; it prints the URL; composition URL is `/<composition-id>`).
- Verify visually before declaring done: render selected frames (`--frames=0,30,90 --image-format=png`) or a still, and inspect them; check the Studio error overlay.
- Render the final video only when the user asks, or when the brief clearly expects a file; write it to an explicit path (not only `/tmp`), and render the video, not just a still.
- Preserve user edits made between turns; if something changed unexpectedly, keep it or ask.
- Never ask the user to paste API keys or AWS secrets into chat; use `.env`.
- Install Remotion-related packages only through `npx remotion add <pkg>` so versions match (`@remotion/*`, `mediabunny`, `@mediabunny/*`, `zod`, `@huggingface/transformers`). Keep every `remotion` and `@remotion/*` package on one exact version; check with `npx remotion versions`.

### 7.2 Markup rules (from the official skills; apply unless the brief says otherwise)

- Frame-driven motion only: `useCurrentFrame()` + `interpolate()`; timing via `Easing.bezier(...)` or `Easing.spring({damping: 200})`; clamp both sides; `output: 'perceptual-scale'` for scale; easing arrays for multi-keyframe; `posterize` for a deliberate choppy look.
- Keep `interpolate()` inline in `style`, with hardcoded ranges (input may use `fps`, `durationInFrames`, `width`, `height` from `useVideoConfig()` in simple forms like `2 * fps` or `durationInFrames - 30`).
- Use `scale`, `translate`, `rotate` CSS properties; use `transform` strings only for skew/perspective/order-sensitive chains.
- Wrap editable elements in `Interactive.Div` (etc.) with a hardcoded descriptive `name`; plain inline `style` objects (no spreading, constants or math); inline fixed text.
- Composition metadata and `defaultProps` inline on `<Composition>`/`<Still>`; `type` not `interface` for props; no `as Props` assertions; use `calculateMetadata()` only for dynamic parts (duration from media or voiceover, fetched data, `defaultOutName`, `defaultCodec`).
- Zod `schema` for parametrizable videos (top level must be `z.object`), `zColor()` from `@remotion/zod-types` for color pickers.
- Assets in `public/` + `staticFile()`, or CORS-enabled URLs. Media: `<Video>`/`<Audio>` from `@remotion/media`; stills via `<Img>`/`<CanvasImage>`; animated images via `<AnimatedImage>`; sound effects via `@remotion/sfx` `<Audio>` with `https://remotion.media/*.wav`.
- Timing props on components (`from`, `durationInFrames`, `trimBefore`); `<Sequence>` fallback with `layout="none"` or `"absolute-fill"`; always premount sequences (`premountFor={1 * fps}`).
- Editable video edits: each clip a separate hardcoded JSX node (no `.map()`), independent clips with `from`/`durationInFrames`/`trimBefore`, or ripple editing with `<TransitionSeries.Sequence name durationInFrames>` (no `from`).
- Multi-scene: one component per scene, connected compositions in a `<Folder>`, `<TransitionSeries>` for transitions; duration arithmetic accounts for transition overlaps.
- Layout: design a video, not a web page; one focal point per scene; for 1080px width, key text 80px from sides, 100px from top/bottom, headline >= 84px, supporting text >= 44px (scale with width); vertical social formats keep content inside roughly 12% top, 15% bottom, 5% side margins.
- Effects: HTML/CSS first, then element `effects` or `<HtmlInCanvas>` (requires Chrome 149+ flag in preview, `--gl=angle` for WebGL renders, no nesting), preset effects before custom `createEffect()`; effects arrays stable and inline.
- Fonts: `@remotion/google-fonts` with explicit weights and subsets; local fonts via `@remotion/fonts` with quoted `src`.

### 7.3 Decision tables

**Which AI architecture?**

| Goal | Use |
|---|---|
| Make videos yourself / for a client with an agent | Coding agent + Agent Skills in a real project (our main path) |
| Product where end users type a prompt and get an animation, no server-side code execution | Prompt-to-motion-graphics pattern: validate, detect skills, generate one component, sanitize, JIT compile, Player preview, auto-correct, Lambda or client-side export; sandbox in an iframe with CSP |
| Product that turns a topic into a narrated story video | Prompt-to-video pattern: LLM script + image prompts + TTS with timestamps into JSON, fixed composition renders the JSON |
| Browser agent helping inside Studio | WebMCP tools |
| Docs lookup for an agent | `/remotion-docs` or `.md` docs URLs (not the deprecated MCP) |

**Which media API?**

| Need | Use |
|---|---|
| Duration, dimensions, fps, codecs in JS | Mediabunny (`Input`, `computeDuration`, `getPrimaryVideoTrack`, `computeFrameRateMetrics`) |
| Asset not fetchable because of CORS | `getVideoMetadata()` from `@remotion/media-utils` |
| Thumbnails/filmstrips in a UI | Mediabunny `VideoSampleSink` |
| Embed video/audio in a composition | `<Video>`/`<Audio>` from `@remotion/media` (fallbacks: `<OffthreadVideo>` for exotic codecs like HEVC during SSR, `<Html5Video>`/`<Html5Audio>` for special cases) |
| Transcode/trim/extract audio on a machine | `npx remotion ffmpeg` / `npx remotion ffprobe` |
| Maintain old code | `@remotion/media-parser`, `@remotion/webcodecs` (phasing out) |

**Which render path?**

| Situation | Use |
|---|---|
| Local agent work | `npx remotion render` / `npx remotion still` |
| Scalable SaaS | Lambda (redeploy function after upgrades, site after source changes) |
| Vercel-hosted app | Vercel Sandbox template |
| Long-running server | Node SSR APIs (`template-render-server`) |
| No server costs, short renders, user keeps tab open | `renderMediaOnWeb()` (`@remotion/web-renderer`) |
| GPU heavy scenes | Linux GPU box with Chrome for Testing + `--gl=vulkan` |

### 7.4 Version gating for our Remotion 4.0.528

| Feature | Available since | On 4.0.528? |
|---|---|---|
| WebMCP in Studio | 4.0.518 (tools up to 4.0.523) | Yes |
| `concurrency: 1` on main Lambda function | 4.0.517 | Yes |
| Light leaks (`@remotion/effects/light-leak`) | 4.0.500 | Yes |
| ProRes decode in `@remotion/media` | 4.0.487 | Yes (opt-in package) |
| `staticFile()`/`new Date()` inside saveable `defaultProps` | 4.0.475 | Yes |
| Chrome 149.0.7790.0 headless shell | 4.0.452 | Yes |
| AC-3/E-AC-3 | 4.0.427 | Yes (opt-in) |
| DTS | 4.0.520 | Yes (opt-in) |
| `<HtmlInCanvasMotionBlur>` | 4.0.529 | **No** |
| `Interactive.Path` guidance in skills | appears only in 4.0.529 skills | **Verify before use** |
| Mediabunny 1.56.1 pairing | 4.0.524 | Expected yes; confirm with `npx remotion versions` |
| Premounting | 4.0.140 | Yes |
| media-parser seeking / webcodecs decoders | 4.0.291 / 4.0.307 | Yes but legacy |

### 7.5 Pre-render checklist

- No CSS animations, transitions, `@keyframes`, Tailwind animation classes, timers, `Math.random()` at render time (use data or `random(seed)`).
- No CSS-loaded images or `next/image`; all media through Remotion components.
- All assets in `public/` or CORS URLs; no absolute paths.
- Fonts loaded with explicit weights/subsets; FontFace URLs quoted.
- Duration set explicitly or via `calculateMetadata`; transitions subtracted.
- Props slim and serializable.
- HEVC inputs transcoded if rendered with `<Video>`.
- WebGL/effects: `--gl=angle` (or swangle without GPU).
- Audio present, volume not zero, mounted during intended range; verify sound in a real player (VS Code preview is muted).
- Output codec matches destination (H.264 MP4 default; ProRes 4444 or VP9 WebM for alpha).

### 7.6 Troubleshooting triage (fast path)

1. Read the exact message; match it against section 6.
2. `--log=verbose`, `--concurrency=1`.
3. Timeouts: which `delayRender` label? Fonts, media proxy, root component, or custom.
4. Kills and hangs: memory (cache size, concurrency), overload (page function timeout), Chrome variant.
5. Studio issues: restart Studio, import casing, `defaultProps` shape.
6. Then docs via `.md` URLs and GitHub issues.

### 7.7 Prompt-writing guidance to give users (and to use when we brief sub-agents)

- Include: purpose and platform (e.g. TikTok vertical, YouTube pre-roll), exact dimensions and fps if known, target length, exact on-screen phrases, brand colors (hex) and font, data values, the motion feel, number and order of scenes, audio (music, voiceover, SFX), output format (MP4, transparent ProRes, WebM), and whether to render.
- Give image URLs when an image must appear; attaching an image (in LLM apps) means "recreate this look".
- Ask for one focal point per scene and readable minimum text sizes.
- For follow-ups, request targeted changes ("make the background #0A0A0A", "slow the entrance to 1 s") so the agent edits instead of rewriting.

### 7.8 If the user wants an editor product

- Recommend the Editor Starter (or Timeline) only when they build an editor for end users; for their own videos use Studio.
- Model the video as JSON (tracks, items, assets) that is fed as `inputProps` to both Player and renderer; keep it serializable and versioned (migrate persisted state).
- Useful Editor Starter flags to know: `FEATURE_NEW_MEDIA_TAGS`, `ENABLE_CLIENT_SIDE_RENDERING`, `FEATURE_RENDERING`, `FEATURE_RENDERING_CODEC_SELECTOR`, `FEATURE_CAPTIONING`, `FEATURE_CROPPING`, `FEATURE_TIMELINE_SNAPPING`, `FEATURE_CANVAS_SNAPPING`, `FEATURE_SPLIT_ITEM`, `FEATURE_ROLLING_EDITS`, `FEATURE_WAVEFORM`, `FEATURE_FILMSTRIP`, `FEATURE_DROP_ASSETS_ON_TIMELINE`, `FEATURE_DROP_ASSETS_ON_CANVAS`, `FEATURE_LOAD_STATE_FROM_URL`, `FEATURE_CACHE_ASSETS_LOCALLY`, `FEATURE_WARN_ON_LONG_RUNNING_PROCESS_IN_PROGRESS`, `FEATURE_PLAYBACKRATE_CONTROL` (0.25x to 5x), `FEATURE_TEXT_LINE_HEIGHT_CONTROL` (0.5 to 5.0), `FEATURE_TEXT_LETTER_SPACING_CONTROL` (-10px to 50px), `FEATURE_TEXT_DIRECTION_CONTROL` (auto LTR/RTL).
- Production checklist: protect all backend routes (auth + rate limits), implement asset cleanup, Lambda checklist and separate prod/dev sites, client-side rendering caveats, disable features you do not want, handle upload-size and caption-duration limits, company license.

---

## 8. Best examples to learn from

- `repo/packages/skills/skills/remotion-markup/SKILL.md`: the canonical current markup conventions (Interactive, inline interpolate, perceptual scale, component timing props).
- `repo/packages/skills/skills/remotion-interactivity/SKILL.md`: exactly what Studio can parse and edit; the do/don't examples are the best spec for editable output.
- `repo/packages/skills/skills/remotion-markup/{multi-scene-video,connected-compositions,video-editing,timing,transitions}.md`: structure for multi-scene videos and editable timelines, with duration math.
- `repo/packages/skills/skills/remotion-create/{SKILL,video-layout}.md`: scaffold rules and video layout minimums.
- `repo/packages/skills/skills/remotion-render/{SKILL,transparent-videos}.md`: frame-sample QA command and alpha export recipes.
- `repo/packages/skills-evals/scenarios.ts`: five realistic, well-specified test prompts (vertical and landscape promo, map trip with 3D Eiffel Tower, bar+line chart, YouTube subscribe lower third as transparent ProRes); reuse as our regression prompts.
- `repo/packages/skills-evals/src/run-skill-eval.ts`: how Remotion evaluates skills (blank template, skills copied into the agent's skill folder, agent run, second "render to exact path" run, collect visual artifacts, compare runs).
- `repo/packages/template-prompt-to-motion-graphics/src/app/api/generate/route.ts`: complete validation, skill routing, streaming generation, search/replace follow-up edits and self-healing prompts.
- `repo/packages/template-prompt-to-motion-graphics/src/skills/*.md`: compact craft rules for typography, charts, chat UIs, social formats, springs, 3D.
- `repo/packages/template-prompt-to-motion-graphics/src/remotion/compiler.ts` and `src/helpers/sanitize-response.ts`: robust import stripping and component extraction for LLM output.
- `repo/packages/template-prompt-to-video/cli/{service,timeline}.ts` and `src/components/AIVideo.tsx`: data-driven story videos synced to TTS character timestamps, Ken Burns backgrounds, subtitle chunking, `getStaticFiles()` + `calculateMetadata` registration.
- `mirror/docs/ai/webmcp.md`: full WebMCP tool contract.
- `mirror/docs/mediabunny/frame-rate.md`: correct fps matching incl. VFR pitfalls; `mirror/docs/mediabunny/formats.md`: codec/container truth table and the HEVC headless limitation.
- `mirror/docs/media-parser/webcodecs.md`: rotation, three dimension sets, queueing and Chrome quirks.
- `mirror/docs/troubleshooting/*.md`: error catalog (section 6).
- `mirror/docs/editor-starter/{state-management,tracks-items-assets,undo-redo,features-not-included}.md`: proven editor architecture decisions.
- `mirror/docs/miscellaneous/chrome-headless-shell.md`: browser pinning and versions.

---

## 9. Open questions

- The reference `/system-prompt.txt` was not available offline; its current content (Remotion's recommended LLM system prompt) should be fetched and reviewed.
- Is `Interactive.Path`/`Interactive.Svg`/`interpolatePaths()` inline editing available in 4.0.528, or only 4.0.529? (The installed 4.0.528 skill does not mention it.)
- Which Mediabunny version does 4.0.528 pin? The docs table jumps from 4.0.524 (1.56.1); run `npx remotion versions` to confirm.
- The exact list of media-parser fields that forbid forward seeking and the default codec tables per container were in MDX components not present in the mirror (low priority, legacy package).
- `convertMedia` audio codec support is documented inconsistently (only `opus` on one page; Opus/AAC/PCM on another). Irrelevant if we stay on Mediabunny, but note it.
- The prompt-to-motion-graphics README says direct image uploads are not supported, while the docs page and the route code accept attached images (`frameImages`). The code suggests attachments work (as style references).
- The official skills now prefer `interpolate()` + `Easing.spring()` (editable), while the SaaS template's guidance prefers raw `spring()`. Our skills should follow the newer, editable style unless physics-accurate springs are needed; confirm this matches the docs owned by other agents (interpolate/Easing pages).
- WebMCP needs a WebMCP-capable browser agent; Claude Code does not drive it today. Could our pipeline use the same Studio APIs (e.g. `restartStudio()`, error overlay) through the Claude Browser tools instead?
- Editor Starter and Timeline internals (state provider shape, flags file) are private; if the user buys them, we should read the source before building editor features.
