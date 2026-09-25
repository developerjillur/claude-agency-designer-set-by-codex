# R1-skills-plugins: official Remotion agent skills, plugins, evals and MCP

Author: research agent R1-skills-plugins. Material: the official Remotion Agent Skills (monorepo source and the
published org repos), the agent plugins for Claude Code, Codex, Cursor/Copilot and Kimi, the skills eval harness,
the Remotion MCP server, and the skills installed on this machine (`~/.claude/skills/remotion-*`).

Key facts in one screen:

- 12 official skills: one router (`remotion-best-practices`) that embeds the other 11, four task skills (`create`,
  `studio`, `render`, `upgrade`), one lookup skill (`docs`) and six knowledge skills (`markup`, `interactivity`,
  `captions`, `maps`, `multimedia`, `saas`). About 28k words of Markdown, of which `markup` (~12k) and `maps` (~10k)
  are almost everything.
- Skills are version-locked to Remotion (frontmatter `version`). Monorepo and org repos: 4.0.529. Installed on this
  machine: 4.0.528 (matches the installed Remotion 4.0.528). The 4.0.529 additions are exactly the two APIs that only
  exist from 4.0.529 (`<HtmlInCanvasMotionBlur>`, `interpolatePaths()`), so the installed set is correct for 4.0.528.
- Doctrine: animation is a pure function of `useCurrentFrame()`, and markup is written so Remotion Studio can parse it
  and let a human edit it visually (inline styles, inline `interpolate()` with hardcoded values, `Interactive.*`
  wrappers, CSS `scale`/`translate`/`rotate`, hardcoded clip timings, inline `defaultProps`).
- Evals: 5 prompt scenarios run by the Pi coding agent with `openai-codex/gpt-5.5`; there is no automatic grading at
  all. A human watches the rendered MP4s (before/after a skill change) next to the skill diff.
- MCP: one tool (`remotion-documentation`); officially deprecated in favour of the `/remotion-docs` skill.
- The official skills are thin on craft (design, typography, pacing, story, sound, social specs, data viz, 3D, real
  footage editing, QA). That gap is what our skill family must fill (section 7A).

---

## 1. Scope and coverage

All paths are relative to the R&D root unless absolute. Every file was read one by one. Files that are byte copies of
a file already read were verified with SHA-256 against it; every copy that differed was diffed and the full diff read.

| Area | Files | How covered | Skipped |
|---|---|---|---|
| `repo/packages/skills` (canonical source) | 115 = 8 package files + 107 skill files (12 symlinks that expand to 275 files when followed) | all 115 read fully | none |
| `repo/packages/claude-code-plugin` | 10 | all read | none |
| `repo/packages/agent-plugin` (Codex + portable/Cursor/Copilot) | 17 | 14 text files read | 3 PNG images (`icon.png`, `logo.png`, `logo-dark.png`) |
| `repo/packages/kimi-code-plugin` | 9 | all read | none |
| `repo/packages/codex-plugin` | 251 | 167 identical to canonical (hash), 59 differ (all diffs read) | 25 PNG icons |
| `repo/packages/skills-evals` | 32 | all read | none |
| `repo/packages/mcp` | 6 | all read | none |
| `examples/skills` (org repo remotion-dev/skills) | 313 = 283 working tree + 30 `.git` | 8 package files read (7 identical, `package.json` differs, read); 275 skill files: 257 identical, 18 differ (diffs read); 11 git metadata files read | git `index`, 4 pack files (binary), 14 sample hooks (generic git templates) |
| `examples/claude-code-plugin` (org repo) | 288 = 258 working tree + 30 `.git` | 3 top-level files identical to monorepo; 255 skill files: 237 identical, 18 differ (diffs read); 11 git metadata files read | same 19 git files |
| `~/.claude/skills/remotion-*` official (12 dirs) | 273 | compared with the 4.0.529 distribution: 248 identical, 25 differ (all diffed) | none |
| `~/.claude/skills/remotion-broll` (team kit, symlink) | 48 | 46 read (the 216 KB `package-lock.json` parsed for versions) | 2 PNG stand-in pictures |

Large data files were parsed and every record traversed rather than read line by line: `country-meta.json`
(333 KB: 3 countries, `stop`/`anchor`/`border` with 2029, 3647 and 1833 border points), `yarlung-flow.json` (603
lng/lat points), `cesium-path.json` (297 points), `sample-river.geojson` (1 LineString, 201 points, "Yarlung Tsangpo
(OSM, gorge way)"), `city-path.json` (10 points, lower Manhattan).

Provenance: monorepo mirror at commit `40cf14ba` (2026-09-25 16:47 +0200, main). `remotion-dev/skills` at `cf49eff5`
(2026-09-25, "Update template"). `remotion-dev/claude-code-plugin` at `a39a5019` (2026-09-25, "Update Claude Code
plugin"). Installed official skills written 2026-09-25 08:34.

Supplemental reading (owned by D8, read only to answer the install questions correctly): `mirror/docs/ai/{skills,
plugins,claude-code-plugin,codex-plugin,cursor-plugin,kimi-code-plugin,github-copilot-plugin,mcp,coding-agents}.md`,
`mirror/docs/cli/skills.md`, the flag list of `mirror/docs/cli/studio.md`, and targeted `AvailableFrom` greps across
`mirror/docs` to date every API the skills use.

Nothing was blocked. Coverage list: `kb/R1-skills-plugins.coverage.txt`.

---

## 2. Mental model

1. **Agent Skills format.** Each skill is a folder with `SKILL.md` (YAML frontmatter `name`, `description`, `version`)
   plus rule files that the agent loads only when a link in `SKILL.md` points to them (progressive disclosure). Rule
   files carry their own small frontmatter (`name`, `description`, `metadata.tags`). Each official skill also has
   `agents/openai.yaml` (Codex UI: `display_name: '/<skill>'`, short description, icons, brand colour `#0B84F3`,
   default prompt starting `$<skill>:`) and `assets/remotion-icon.svg`.
2. **Router plus specialists.** `remotion-best-practices` is only a routing table. The other skills are reachable both
   as top-level skills and as embedded copies inside the router (and `remotion-maps` is embedded inside
   `remotion-markup` too). In the monorepo the embedding is done with symlinks; the build materialises them and renames
   embedded `SKILL.md` to `REFERENCE.md` so that agents discover only the top-level skills.
3. **Frontmatter descriptions are terse** ("Router for all Remotion skills", "Content, animation and effects best
   practices"). The official design relies on the router or on explicit slash invocation, not on rich auto-trigger
   descriptions. Our skills should do the opposite (rich trigger descriptions), because Claude Code picks skills from
   the description.
4. **Frame-pure animation.** Everything moves because `useCurrentFrame()` changes. CSS transitions/animations,
   Tailwind `animate-*`/`transition-*`, React Three Fiber `useFrame`, self-animating shaders or browser timers break
   rendering (flicker, wrong frames under parallel rendering).
5. **Studio-editable markup ("interactivity").** Remotion Studio (from 4.0.475) can select, drag, resize, rotate,
   edit CSS and keyframes, but only if the code has a shape it can statically parse: `Interactive.Div` and friends,
   a hardcoded `name`, a plain inline `style` object, inline `interpolate()` calls whose ranges, easing and options are
   literals (input ranges may use `fps`, `durationInFrames`, `width`, `height` from `useVideoConfig()` with simple
   multiplication or subtraction by a number), `scale`/`translate`/`rotate` instead of `transform`, inline
   `defaultProps`, hand-written clip JSX (no `.map()`). Many official rules exist only to preserve this editability.
6. **Canvas-era primitives.** The skills steer towards `<CanvasImage>`, `<Solid>`, `<AnimatedImage>`,
   `<HtmlInCanvas>` and the `effects` prop (WebGL2 effects from `@remotion/effects`), plus `crop*` props and timing
   props (`from`, `durationInFrames`, `trimBefore`) directly on visual components instead of wrapping in `<Sequence>`.
7. **Preview first, render on request.** `remotion-create` says: start `npx remotion studio --no-open`, open the exact
   URL (`/<composition-id>`), and render only when the user asks. Visual checks are Studio or `render --frames`.
8. **Version alignment.** Install everything with `npx remotion add <pkg>` (also for `zod`, `mediabunny`,
   `@mediabunny/*`, `@huggingface/transformers`) so versions match; all `remotion`/`@remotion/*` share one exact version.
9. **Docs over memory.** `remotion-docs` teaches Algolia search plus appending `.md` to any docs URL; the router tells
   agents to read current docs rather than rely on memorised APIs. Our local equivalent is `mirror/docs/**.md`.
10. **Preserve user changes.** Both the router and `remotion-markup` open with: if code changed surprisingly outside the
    conversation, do not overwrite it; assume it was intentional or ask.
11. **Evaluation culture.** Remotion validates skill edits by regenerating fixed prompts and looking at the videos,
    not by assertions. Craft quality is judged by eye.

---

## 2A. Full structure of each official skill

Word counts are for Markdown only. "SKILL" means the entry file. Version 4.0.529 unless noted.

### remotion-best-practices (router, ~300 words)

| File | What it teaches |
|---|---|
| `SKILL.md` | Preserve user edits. Routing: any request to make/create/build a video or composition goes to `remotion-create` even inside an existing project; no project yet goes to `remotion-create`; writing React markup goes to `remotion-markup`; maps, multimedia (Mediabunny), interactivity, rendering beyond a plain render, Studio launch/URL/flags, captions, SaaS/apps, docs lookup and upgrades each go to their skill. |
| `remotion-*/` (11 embedded copies) | Materialised copies of the other skills (entry renamed `REFERENCE.md` in builds). |
| `agents/openai.yaml`, `assets/remotion-icon.svg` | Codex metadata; icon (identical SVG in all 12 skills). |

### remotion-create (~510 words)

| File | What it teaches |
|---|---|
| `SKILL.md` | Scaffold only if no project exists. Check Node and Git. Inspect the folder including hidden files. Empty folder (or only `.DS_Store`-type metadata): delete only that metadata (create-video rejects non-empty folders) and run `npx create-video@latest --yes --blank --no-tailwind .` then `npm i`. Meaningful contents (`.env`, `.git` count): scaffold into a named subfolder. Then write markup per `remotion-markup` and `video-layout.md`; multi-scene goes to `multi-scene-video.md`; structure for interactivity; Tailwind only if requested. Start `npx remotion studio --no-open` (long-running, prints URL, reprints if already running; open `http://localhost:3000/<composition-id>`). Render only if explicitly asked (`npx remotion render`). Follow-ups go back to the router. |
| `video-layout.md` | "You are designing a video, not a webpage": one thing the viewer should notice first per scene; keep key content in a safe area (at 1080 px wide: at least 80 px from the sides, 100 px from top and bottom); no redundant elements; minimum sizes at 1080 px wide: main headline 84 px, important supporting text 44 px; scale these with composition width. This is the only design guidance in the whole official set. |
| `tailwind.md` | Use Tailwind if installed; never `transition-*` or `animate-*` classes; Tailwind must be enabled first (docs link). |

### remotion-markup (~12k words, 30 rule files)

`SKILL.md` is a hub: general rules (drive with `useCurrentFrame()` + `interpolate()`, `Easing.bezier()` and
`Easing.spring()`, CSS/Tailwind animations must be refactored, keep `interpolate()` inline in `style`, prefer
`scale`/`translate`/`rotate`), assets in `public/` via `staticFile()`, media components (`<Video>`/`<Audio>` from
`@remotion/media`, `<CanvasImage>` for images, `<AnimatedImage>` for GIF/APNG/WebP/AVIF), an example scene, the
timing props available on most components (`from`, `durationInFrames`, `trimBefore`; fallback: wrap in
`<Sequence>`, with `layout="absolute-fill"` or `"none"`), `npx remotion add`, and "Visual checks" (Studio, or render
frames). Then an index of the rule files:

| Rule file | What it teaches |
|---|---|
| `timing.md` | Linear `interpolate()` over frame ranges in `fps` units; values are unclamped by default, clamp both sides; Studio-editable inline pattern; `transform` strings only for skew, perspective or order-sensitive chains; `Easing.spring({damping: 200})` = push with no bounce; `Easing.bezier(0.16, 1, 0.3, 1)` like CSS cubic-bezier; `output: 'perceptual-scale'` for scale; multiple keyframes with an `easing` array of n-1 items; `posterize: 3` samples every third frame for a deliberate low-frame-rate look. |
| `sequencing.md` | `<Sequence from durationInFrames layout name>`; default wraps in an absolute fill, `layout="none"` for no wrapper; "always premount any Sequence" with `premountFor={1 * fps}`; `<Series>` for back-to-back scenes; `offset={-15}` overlaps; inside a Sequence `useCurrentFrame()` is local (starts at 0); nesting; `<Sequence width height>` overrides `useVideoConfig()` for a nested composition. |
| `compositions.md` | `<Composition>` metadata; `defaultProps` must be JSON-serialisable (Date, Map, Set, `staticFile()` allowed) and inline (no variable, import, spread, helper or `satisfies`) so Studio can save edits; keep component and registration in one file when scaffolding; use `type` not `interface` for props; `<Folder>` (names: letters, numbers, hyphens; nestable); `<Still>` needs no duration/fps; nesting another composition with `<Sequence width height>`; connected compositions for their own timeline. |
| `connected-compositions.md` | "Precomposition" pattern: put a scene in its own named component, render exactly one direct instance inside a `<Sequence>`/`<Series.Sequence>`/`<TransitionSeries.Sequence>` in the parent, and register the same component reference as its own `<Composition>` (unique id, own natural duration, usually inside a `<Folder>`). Studio then shows the scene as a reference; double-click opens it at the matching frame. Props are not copied: give the standalone registration matching `defaultProps`; keep fps and dimensions aligned. |
| `multi-scene-video.md` | One component and file per substantial scene, registered as connected compositions; `<TransitionSeries>` when transitions may be wanted (install `@remotion/transitions`); inline `durationInFrames` per sequence; the parent duration is the sum (210 in the example) minus transition overlaps; `<Series>` for plain consecutive scenes, `<Sequence>` for independent placement. |
| `transitions.md` | `<TransitionSeries>`: `.Sequence`, `.Transition` (overlaps both scenes, shortens total), `.Overlay` (plays over the cut, does not change total; `durationInFrames`, `offset` default 0; cannot sit next to a transition or another overlay). Presentations `fade`, `slide({direction: from-left/right/top/bottom})`, `wipe`, `flip`, `clockWipe` from their subpaths; `linearTiming({durationInFrames})`, `springTiming({config: {damping: 200}, durationInFrames?})`; `timing.getDurationInFrames({fps})`; total = sum of scenes minus transitions (60+60+60-15-20 = 145). |
| `light-leaks.md` | `lightLeak()` from `@remotion/effects/light-leak` on a `<Solid>` (needs Remotion 4.0.500+); animate `progress` 0 to 1 (reveals in the first half, retracts in the second); options `progress` (default 0.5), `seed` (pattern, default 0), `hueShift` (degrees, default 0 = yellow-orange, 120 green, 240 blue), `disabled`; usually inside `<TransitionSeries.Overlay>`; WebGL2, so enable ANGLE. |
| `effects.md` | The `effects` prop on canvas-based components (`<Video>` from `@remotion/media`, `<Solid>`, `<CanvasImage>`, `<HtmlInCanvas>`); install `@remotion/effects`; import from `@remotion/effects/<slug>` (translate effects from `/translate`); WebGL2, enable `Config.setChromiumOpenGlRenderer('angle')`; the list of 58 effects; `createEffect()` contract for custom effects (2D and WebGL2 skeletons); authoring rules. |
| `html-in-canvas.md` | `<HtmlInCanvas width height onPaint onInit>` renders DOM into a canvas for 2D/WebGL post-processing; Studio preview needs Chrome 149+ with `chrome://flags/#canvas-draw-element` (tell the user); no nesting; enable ANGLE for WebGL; 2D `onPaint` uses `ctx.drawElementImage(elementImage, 0, 0)` and must write the returned transform to `element.style.transform`; WebGL uses `gl.texElementImage2D`; `onPaint` may be async (frame held open). |
| `motion-blur.md` (4.0.529 only) | `<HtmlInCanvasMotionBlur width height samples shutterAngle>` from `@remotion/motion-blur`: samples fractional frames and averages them; `shutterAngle` default 180 (0 to 360, 0 disables), `samples` default 8 (integer 1 to 64, cost grows); call `useCurrentFrame()` inside the child; preview needs the Chrome flag, render needs nothing; no nesting; otherwise see the motion blur guide. |
| `3d.md` | Install `@remotion/three`; wrap 3D in `<ThreeCanvas width height>` (both required) with lights; nothing may animate by itself; `useFrame()` from R3F is forbidden; animate from `useCurrentFrame()`; any `<Sequence>` inside `<ThreeCanvas>` needs `layout="none"`. |
| `audio.md` | `<Audio>` from `@remotion/media`; remote URLs OK; layering; `trimBefore`/`trimAfter` in frames; `from` to delay; `volume` number or callback whose `f` starts at 0 when the audio starts; dynamic `muted`; `playbackRate` (no reverse); `loop` and `loopVolumeCurveBehavior` (`repeat` default, `extend`); `toneFrequency` 0.01 to 2 (server render only, not Studio or Player). |
| `embedding-videos.md` | Same prop set for `<Video>` plus `style` sizing/positioning and `objectFit`, `muted`. (Contains a unit error, see section 6.) |
| `audio-visualization.md` | `@remotion/media-utils`: `useWindowedAudioData({src, frame, fps, windowInSeconds: 30})`; `visualizeAudio({fps, frame, audioData, numberOfSamples, optimizeFor: 'speed', dataOffsetInSeconds})` (power-of-two samples, values 0 to 1, bass on the left); pass `frame` down to children rather than calling `useCurrentFrame()` inside offset sequences; `visualizeAudioWaveform` + `createSmoothSvgPath` for oscilloscope lines; bass = mean of the first 32 of 128 bins; `getWaveformPortion` for volume bars; log (dB) scaling -100 to -30 for balance. |
| `sfx.md` | 32 hosted sound effects at `https://remotion.media/<name>.wav` (whoosh, whip, page-turn, switch, mouse-click, shutter-modern/old, ding, bruh, vine-boom, record-scratch, and meme sounds); more at the soundcn repo. (Import line is wrong, see section 6.) |
| `voiceover.md` | ElevenLabs TTS by default (`ELEVENLABS_API_KEY`, ask the user for a key if no provider named): POST `https://api.elevenlabs.io/v1/text-to-speech/<voiceId>`, `model_id: eleven_multilingual_v2`, `voice_settings {stability 0.5, similarity_boost 0.75, style 0.3}`, write MP3s to `public/voiceover/<comp>/<scene>.mp3`, run with `node --strip-types`; size the composition with `calculateMetadata` summing per-scene audio durations (minus transition overlaps). |
| `calculate-metadata.md` | When metadata depends on props, fetched data or assets: duration from a video, dimensions from a video, sum of several videos, `defaultOutName`, transforming props with `abortSignal`; return fields are all optional and override `<Composition>`. |
| `parameters.md` | Zod schema on a composition (`schema` prop), top level must be `z.object`; install zod by lockfile type; `zColor()` from `@remotion/zod-types` for a colour picker. |
| `images.md` | `<Img>` sizing with `style`/`objectFit`; dynamic `staticFile()` paths (image sequences by frame, per-user avatars, state icons); `getImageDimensions()` also inside `calculateMetadata`. |
| `gifs.md` | `<AnimatedImage src width height fit playbackRate loopBehavior>` (fit `fill` default, `contain`, `cover`; loop `loop` default, `pause-after-finish`, `clear-after-finish`); remote needs CORS; only Chrome and Firefox, else `<Gif>` from `@remotion/gif` (GIF only); `getGifDurationInSeconds()` to size a composition. |
| `lottie.md` | `@remotion/lottie`: fetch JSON inside `delayRender`/`continueRender`, `cancelRender` on error, store in state, render `<Lottie animationData style>`. |
| `google-fonts.md` | `@remotion/google-fonts/<Family>` `loadFont()` (blocks rendering until ready); pass style and `{weights, subsets}` to limit download; call at module top level. |
| `local-fonts.md` | `@remotion/fonts` `loadFont({family, url: staticFile(...), format?, weight?, style?, display?})`; one call per weight with the same family. |
| `measuring-dom-nodes.md` | Divide `getBoundingClientRect()` by `useCurrentScale()` because Studio scales the canvas. |
| `measuring-text.md` | `@remotion/layout-utils`: `measureText` (cached), `fitText({text, withinWidth, fontFamily, fontWeight})` returns `fontSize` (cap it), `fillTextBox({maxBoxWidth, maxLines}).add(...)` returns `exceedsBox`; measure only after fonts load (`waitUntilDone()`), `validateFontIsLoaded: true`, identical font props for measuring and rendering, `outline` instead of `border`. |
| `text-highlights.md` | `@remotion/rough-notation` (4.0.490+): `<Highlight>`, `<Circle>`, `<Underline>`, `<StrikeThrough>`, `<CrossedOff>`, `<Box>`, `<Bracket>` with a frame-driven inline `progress`. |
| `cropping.md` | `cropLeft/Right/Top/Bottom` ratios 0 to 1 on `<Sequence layout="absolute-fill">`, `<CanvasImage>`, `<Img>`, `<AnimatedImage>`, `<HtmlInCanvas>`, `<Solid>`, `<Video>` (media), `<Gif>`, `<RemotionRiveCanvas>`; keyframable inline; never combine with `clipPath`. |
| `video-editing.md` | Two editing models: independent clips (each `<Video>` its own JSX node with hardcoded `from`, `durationInFrames`, `trimBefore` in frames; gaps/overlaps allowed) and ripple editing (`<TransitionSeries>` with named `.Sequence` rows; no `from`; dragging a right edge shifts later clips). Never generate editable clips with `.map()`. |
| `ffmpeg.md` | `npx remotion ffmpeg` / `npx remotion ffprobe` are bundled; prefer non-destructive `trimBefore`/`trimAfter`; if cutting a file, re-encode (`-c:v libx264 -c:a aac`) to avoid frozen first frames. |
| `silence-detection.md` | Adaptive silence detection: `loudnorm=print_format=json` to get `input_thresh`, then `silencedetect=noise=<thresh>dB:d=0.5`; read `silence_start`/`silence_end`; merge near-contiguous (<0.2 s) edge silences; apply as `trimBefore={Math.floor(leadingEnd * fps)}`, `trimAfter={Math.ceil(trailingStart * fps)}`. |
| `remotion-maps/` | Embedded copy of the maps skill. |

### remotion-interactivity (~1.3k words)

| Section | What it teaches |
|---|---|
| `Interactive` | Every HTML/SVG element (not `<Img>`, which is already interactive) can be wrapped as `Interactive.Div` etc. to get selection, drag, resize, rotate, CSS editing and keyframes; do not overdo it or the timeline gets messy. |
| Inline text, names | Fixed text goes inline; `name` is hardcoded and descriptive (also on `<Img>`, `<Video>`, `<Sequence>`). |
| Inline CSS | Plain object literal in `style`; no constants, spreads, `useMemo` styles or math. |
| `interpolate()` | Inline per property; literal output range, easing, extrapolation and `output`; input range may use destructured `fps`, `durationInFrames`, `width`, `height`, `2 * fps`, `durationInFrames - 1`; only the `frame` variable is understood as input. |
| `Interactive.Path` (4.0.529) | `<Interactive.Svg>` + `<Interactive.Path d="...">` with the path string inline; morph with inline `interpolatePaths(frame, inputRange, paths[], options)` from `@remotion/paths`; do not use `interpolatePath()` or extract to a variable; evolve with `strokeDasharray`/`strokeDashoffset`. |
| Transform props | Only `scale`, `rotate`, `translate` are editable; avoid `transform`. |
| Composition metadata | Keep `width`, `height`, `fps`, `durationInFrames`, `defaultProps` inline, no type assertions; use `calculateMetadata` only for the dynamic part. |
| Effects | The `effects` array must be literal and stable; no conditional arrays; render separate elements instead. |
| Custom components | `Interactive.withSchema()` must include `Interactive.baseSchema` (trimming and visibility controls); docs link for making components interactive; video clip structure is in `video-editing.md`. |

### remotion-captions (~1.3k words)

| File | What it teaches |
|---|---|
| `SKILL.md` | All captions are JSON in the `Caption` type `{text, startMs, endMs, timestampMs, confidence, pageBreakAfter?}` from `@remotion/captions`; routes to transcribe, display, import SRT. |
| `transcribe-captions.md` | `@remotion/install-whisper-cpp`: `installWhisperCpp({to, version: '1.5.5'})`, `downloadWhisperModel({model: 'medium.en', folder})`, convert to 16 kHz WAV with ffmpeg, `transcribe({model, whisperPath, whisperCppVersion, inputPath, tokenLevelTimestamps: true})`, `toCaptions({whisperCppOutput})`, write JSON; one JSON per clip. |
| `display-captions.md` | Fetch JSON with `useDelayRender()` (+ `cancelRender` on error); `createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds: 1200})` into pages (`pageBreakAfter` forces a break); one `<Sequence>` per page, start `page.startMs/1000*fps`, end at the next page or the switch interval; text is whitespace-sensitive (leading spaces, `whiteSpace: 'pre'`); captions in a separate component and file; highlight the active token (`fromMs <= t < toMs`, colour `#39E508` in the example); keep captions with their video. |
| `import-srt-captions.md` | `parseSrt({input})` returns `{captions}`; local via `staticFile`, or remote URL. |

### remotion-maps (~10k words, 5 techniques, the deepest skill)

`SKILL.md`: choose exactly one technique from the intended shot, load only that `TECHNIQUE.md`; each technique folder
is self-contained.

| Technique | Files | What it teaches |
|---|---|---|
| static-map | `TECHNIQUE.md` | For location context only: a map image at final aspect and at least render size in `public/`, drawn with `<CanvasImage>`, labels/markers as normal elements. Smallest, fastest, most deterministic. |
| mapbox | `TECHNIQUE.md`, `references/render-stability.md` | Needs a Mapbox token (`REMOTION_MAPBOX_TOKEN`); nicer styles, globe at low zoom, 3D buildings (Eiffel Tower). Rules: Turf for all geodesy; GeoJSON sources and layers (no DOM markers); camera static by default; `interactive: false`, `fadeDuration: 0`, `canvasContextAttributes.preserveDrawingBuffer: true`; drive from the frame; `delayRender` around load and every frame; add sources/layers and apply frame-0 camera before the first `continueRender`, then wait for `idle`; no `map.remove()` cleanup; `mapbox://styles/mapbox/standard`; do not install `@types/mapbox-gl`; keep attribution; record data sources and dates; inspect rendered pixels at every aspect. Full flight-route example (great circle, `lineSliceAlong`, markers, labels, `jumpTo` with centre/zoom/bearing/pitch, `triggerRepaint()` to force `idle`). Render `--gl=angle --concurrency=1`. |
| maplibre | same pair | Free, no key, no 3D buildings; same rules; worker via `setWorkerUrl` blob that imports the unpkg worker of the same version; demo style `https://demotiles.maplibre.org/style.json`; camera with `calculateCameraOptionsFromTo(cameraLngLat, altitudeMeters, targetLngLat)` and separate `targetRoute`/`cameraRoute`, altitude animated separately (e.g. 180 km to 2200 km and back). |
| maptiler | `TECHNIQUE.md`, 4 references, 5 assets + 2 sample data, `scripts/prep-geo.mjs` | Annotation-style explainers (borders, rivers, labels over the map) with `@maptiler/sdk` (`MapStyle.BASIC` or satellite), key `REMOTION_MAPTILER_KEY` (unrestricted). Choose per element: provider vector layer (filter a `source-layer` exactly, animate paint only) vs custom GeoJSON (ordered geometry, draw-on, disputed/historic data) vs hybrid. Never pass `filter: undefined`. Strip symbol layers and "other border" layers on load, hide logo via CSS. Fixed map plate for any camera motion. Time-based beats: each country triggers when the river reaches it, then border draw (2.5 s) then fill bloom with overshoot (1.0 s) then label rise (0.7 s). Labels are React overlays projected per frame. Geo prep: pole-of-inaccessibility label anchors (not centroids), story bounding boxes and nudges, complete (unclipped) borders drawn by cumulative length. |
| cesium | `TECHNIQUE.md`, 3 references, 6 assets, `scripts/prep-cesium-path.mjs` | "Flight simulator" flyovers: `landscape` mode (MapTiler `terrain-quantized-mesh-v2` + `satellite-v2`) or `city` mode (Google Photorealistic 3D Tiles, globe hidden, 30 s promotional limit and "For promotional purposes only" label). CesiumJS 1.143 from CDN; `viewer.useDefaultRenderLoop = false`; per frame call `viewer.render()` (never `scene.render()`) in a settle loop until tiles are loaded; `preserveDrawingBuffer`; long `delayRender` timeouts; Chaikin smoothing (3 passes), arc-length walking, look-ahead heading, bank from turn rate; proven values (13 km over 24 s, 4600 to 4300 m, look-ahead 1.5 km, pitch 76 from nadir, max bank 0.13 rad, exaggeration 1.1); render a middle still first. |

References in maps: `render-stability.md` (identical in the three 2D techniques: fixed map plate recipe, sizing rules),
`map-data-sources.md`, `map-explainer-architecture.md`, `map-geo-prep.md`, `3d-data-sources.md`,
`3d-flyover-architecture.md`, `3d-troubleshooting.md`.

### remotion-multimedia (~630 words)

| File | What it teaches |
|---|---|
| `SKILL.md` | Mediabunny is the browser/Node media library (`https://mediabunny.dev/llms.txt`). |
| `get-audio-duration.md`, `get-video-duration.md` | `new Input({formats: ALL_FORMATS, source: new UrlSource(src)})` then `await input.computeDuration()` (seconds); `staticFile()` for public files; `FileSource` for File objects. |
| `get-video-dimensions.md` | `input.getPrimaryVideoTrack()` then `displayWidth`/`displayHeight` (throw if no video track). |

### remotion-render (~310 words)

| File | What it teaches |
|---|---|
| `SKILL.md` | `npx remotion render` / `npx remotion still` (docs links); several frames in one call: `npx remotion render <id> out/frames --frames=0,30,90 --image-format=png`. |
| `transparent-videos.md` | ProRes 4444 for editing software: `--image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444` (`.mov`); VP9 WebM for browsers: `--image-format=png --pixel-format=yuva420p --codec=vp9`; same as `remotion.config.ts` defaults (restart Studio) or per composition via `calculateMetadata` returning `defaultCodec`, `defaultVideoImageFormat`, `defaultPixelFormat`, `defaultProResProfile`. |

### remotion-studio (~115 words)

`SKILL.md`: run `npx remotion studio --no-open`; if already open it prints the URL and exits; flags `--log`
(error, warn, info default, verbose), `--port`, `--force-new`.

### remotion-saas (~790 words)

| File | What it teaches |
|---|---|
| `SKILL.md` | Apps range from a form hooked to a render to a full editor; links for Vue, Angular, Svelte. |
| `framework.md` | Templates: Next.js App Router + Tailwind (Lambda), Vercel Sandbox template (Vercel), React Router 7 (Lambda), Express render server (Node); brownfield install docs. |
| `player.md` | `<Player component durationInFrames compositionWidth compositionHeight fps controls>`; dynamic metadata must be synced manually or reuse `calculateMetadata`. |
| `rendering.md` | SSR comparison page; plain Node APIs for long-running servers; Lambda is the fastest and most scalable, with a 9-step setup (install, IAM role and user, `.env` keys `REMOTION_AWS_ACCESS_KEY_ID`/`REMOTION_AWS_SECRET_ACCESS_KEY`, never paste secrets in chat, validate policies, deploy function (redeploy after upgrades), deploy site (redeploy after code changes), check quotas, first render); production reminders (rate limits, auth, cost, privacy, cleanup, progress); Vercel Sandbox; GitHub Actions and Azure only when asked; Cloudflare Containers. |

### remotion-docs (~140 words)

Algolia search: POST `https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries` with app id `PLSDUOL1CA`, public
search key in the skill, index `remotion`, `hitsPerPage=10`, retrieving `hierarchy.lvl0..2` and `url`; then fetch the
page with `.md` appended. Workflow: search, pick URLs, fetch `.md`, implement from current docs.

### remotion-upgrade (~240 words)

Inspect manifests and lockfile; if `@remotion/cli` is local run `npx remotion upgrade` (also updates project-local
skills); otherwise upgrade every `remotion`/`@remotion/*` to `npm view remotion version`, align `zod`, `mediabunny`,
`@huggingface/transformers` (and `@mediabunny/*` to the mediabunny version) with `npm view @remotion/studio@<v>
dependencies --json`, update the lockfile, then `npx skills update <all 12 names> --yes`; verify with
`npx remotion versions`; changelog at GitHub releases.

---

## 2B. How the plugins package and install the skills

### Build pipeline (one source, five clients)

1. Canonical source: `packages/skills/skills/<skill>/`. Embedding is by symlink:
   `remotion-best-practices/remotion-<x> -> ../remotion-<x>` for all 11 others, and
   `remotion-markup/remotion-maps -> ../remotion-maps`. `sync-embedded-skills.ts` creates/checks these symlinks and
   rewrites parent links to `./<skill>/...`; `sync-agent-skills.ts` links `.agents/skills/<skill>` to the source and
   `.claude/skills -> ../.agents/skills` for the monorepo's own agents; `sync-readme.ts` generates the README from
   `docs/ai/skills.mdx`; `validate-links.ts` checks every relative Markdown link and the embedding rules.
2. Each plugin's `build.mts` copies every skill folder with `cpSync(..., {dereference: true})` and a filter that
   **drops every `.tsx` file** (so plugins ship without `CesiumFlythrough.tsx`, `RiverReveal.tsx`, `CountryLabel.tsx`
   and the two `example-Root.tsx`), then calls `prepareEmbeddedSkills()`:
   - inside embedded roots (`remotion-best-practices`, `remotion-markup`, `remotion-best-practices/remotion-markup`)
     links `../<parent>/SKILL.md` become `../REFERENCE.md` (or `../SKILL.md`), `../<parent>/` becomes `../`, and
     links to embedded skills point at `REFERENCE.md`;
   - embedded `SKILL.md` files are renamed `REFERENCE.md`, so only top-level skills are discovered;
   - `removeCrossSkillLinks()` turns any relative link that leaves the skill's own folder into plain text (Agent
     Skills rule: file references must stay inside the skill directory). Example: in the top-level `remotion-create`
     the link to the router becomes just the words "Remotion Best Practices".
3. `agent-plugin/build.mts --client=codex|cursor [--output=dir]`:
   - Codex only: appends a "Codex troubleshooting" section to `remotion-best-practices/SKILL.md` (start Studio with
     `--no-open`; on `EMFILE: too many open files, watch` retry with `--webpack-poll 1000`; if still failing ask the
     user to start Studio in their macOS Terminal; Chromium sandbox errors come from the Codex/macOS sandbox).
   - Both: rewrites the top-level `remotion-create/SKILL.md` so the preview server starts by default and the exact URL
     is opened in the agent client's browser (or handed to the user). The embedded copy keeps the generic text.
4. Tests (`bun test`): manifest version equals package version; only top-level folders contain `SKILL.md`; no embedded
   file still links `<skill>/SKILL.md`; maps is reachable from both parents via `(./remotion-maps/REFERENCE.md)`;
   agent-plugin additionally runs `@microsoft/vally` 0.12.0 lint on the Codex and the portable build, checks that no
   link leaves its skill folder, that `openai.yaml` `display_name` is `'/<skill>'`, and that the portable build has no
   Codex section; Kimi checks the generated tree equals the canonical tree after the expected transformations and that
   the manifest has no unsupported fields.

### Per client

| Client | Package / repo | Manifest | Install | Invoke |
|---|---|---|---|---|
| Claude Code | `packages/claude-code-plugin` published to `remotion-dev/claude-code-plugin` | `.claude-plugin/plugin.json` (`name: remotion`, `displayName`, `version` 4.0.529, description, author, homepage, repository, license MIT, keywords); `.claude-plugin/marketplace.json` (marketplace `remotion`, one plugin with GitHub source, category Design, tags video, motion-graphics, react, animation). Skills in `skills/` at the plugin root. | `claude plugin marketplace add remotion-dev/claude-code-plugin` then `claude plugin install remotion@remotion`; restart Claude Code. | Automatic loading, or `/remotion-best-practices ...`. |
| Codex (ChatGPT desktop) | `packages/agent-plugin --client=codex` | `.codex-plugin/plugin.json`: `skills: "./skills/"`, `interface` (displayName Remotion, shortDescription "Make videos agentically", longDescription, category Creativity, capabilities Read and Write, website/privacy/terms URLs, three default prompts, brandColor `#0B84F3`, composer icon SVG, logo and dark logo PNG). `marketplace.json`: local source `./.codex/plugins/remotion`, policy installation AVAILABLE, authentication ON_INSTALL, category Design. | ChatGPT desktop, Plugins tab, search "Remotion" (or the direct plugin link). | Type `$remotion` in a new project and accept the plugin; skills via `$remotion-...` (from `openai.yaml`). |
| Cursor | same package, `--client=cursor`, published to `remotion-dev/cursor-plugin` | portable `plugin.json` with `$schema https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` and exactly 9 keys (name, version, description, author, homepage, repository, license, keywords, $schema). | Cursor Marketplace, or `git clone https://github.com/remotion-dev/cursor-plugin.git ~/.cursor/plugins/local/remotion`, then reload. | Automatic, or `/remotion-best-practices`. |
| GitHub Copilot CLI | `remotion-dev/agent-plugin` (portable build) | same portable manifest | `copilot plugin install remotion@awesome-copilot` | prompt normally. |
| Kimi Code | `packages/kimi-code-plugin` published to `remotion-dev/kimi-code-plugin` | `.kimi-plugin/plugin.json`: `skills: "./skills/"`, `interface` (displayName, shortDescription "Create programmatic videos with React", longDescription, developerName, websiteURL). Forbidden fields: `sessionStart`, `skillInstructions`, `mcpServers`, `hooks`, `commands`, `tools`, `apps`, `inject`, `configFile`. | `/plugins install https://github.com/remotion-dev/kimi-code-plugin`, confirm trust, `/new` or `/reload`. | `/skill:remotion-best-practices`. |
| Any agent, skills only | `remotion-dev/skills` (keeps `.tsx` assets) | none | `npx skills add remotion-dev/skills` (global or project, via the skills CLI); `npx remotion skills add` installs into the project's `.agents/skills` and symlinks `.claude/skills` to it; `bun create video` offers it. | `/remotion-...` |

Updating: `npx remotion skills update` and `npx remotion upgrade` update only project-local `.agents/skills`
("Global skills are not updated"); `--skip-skills` (4.0.503) opts out. Global installs such as
`~/.claude/skills/remotion-*` need `npx skills update remotion-best-practices ... --yes`.

Note: `packages/codex-plugin/skills/` in the monorepo is a tracked but stale build (frontmatter 4.0.519, PNG icons,
older link rewriting). It is legacy; the live Codex build comes from `agent-plugin`. Do not learn from it.

---

## 2C. Installed copies versus the repo (every difference)

`~/.claude/skills/remotion-*` holds 12 official skills in the distribution form of `remotion-dev/skills` (embedded
copies materialised, `REFERENCE.md` names, cross-skill links flattened to text, `.tsx` assets included, SVG icons), so
they were installed with the skills CLI from the org repo, not from the Claude Code plugin. Compared with the 4.0.529
distribution (`examples/skills/skills`): 248 files identical, 25 differ, 2 missing, 0 extra.

| # | Difference | Files |
|---|---|---|
| 1 | Frontmatter `version: 4.0.528` instead of 4.0.529 | all 12 top-level `SKILL.md`, the 12 embedded `REFERENCE.md` under `remotion-best-practices/`, and `remotion-markup/remotion-maps/REFERENCE.md` (25 files; for 21 of them this is the only change) |
| 2 | `motion-blur.md` absent | `remotion-markup/motion-blur.md` and `remotion-best-practices/remotion-markup/motion-blur.md` |
| 3 | No "Motion blur" section (2 lines pointing to `motion-blur.md`) | `remotion-markup/SKILL.md`, `remotion-best-practices/remotion-markup/REFERENCE.md` |
| 4 | No "Keep SVG paths editable with `Interactive.Path`" section (static path, `interpolatePaths()` morph example, `strokeDasharray` note; about 68 lines) | `remotion-interactivity/SKILL.md`, `remotion-best-practices/remotion-interactivity/REFERENCE.md` |

Everything else is byte-identical. Differences 2 to 4 match API availability: `<HtmlInCanvasMotionBlur>` and
`interpolatePaths()` are both "available from 4.0.529" in the docs, so on this machine's Remotion 4.0.528 an agent
must not use them. Upgrading Remotion and the skills together to 4.0.529 would enable both.

Against the monorepo source (rather than the distribution) the only extra differences are the build transformations
(REFERENCE renames, flattened cross-skill links); against the stale `packages/codex-plugin` see the evolution table.

`~/.claude/skills/remotion-broll` is not an official skill (symlink to
the `remotion-broll` skill); see section 7B.

### Evolution signals 4.0.519 to 4.0.529 (what Remotion recently changed in its guidance)

| Area | 4.0.519 (stale codex build) | 4.0.528 (installed) | 4.0.529 (repo) |
|---|---|---|---|
| Scaffolding | always into a subfolder `my-video` | inspect folder; empty folder scaffolds in place | same |
| Multi-scene | scene files + TransitionSeries + optional registration | rewritten around connected compositions | same |
| Connected compositions | absent | new rule file | same |
| Visual checks | "Previewing markup" + optional `npx remotion still <id> --scale=0.25 --frame=30` | "Visual checks": Studio or render frames | same |
| Render | no `--frames` list | `render --frames=0,30,90` for several stills | same |
| Interactivity | no `withSchema` note | `Interactive.withSchema()` needs `Interactive.baseSchema` | plus `Interactive.Path` and `interpolatePaths()` |
| Motion blur | absent | absent | `motion-blur.md` (`<HtmlInCanvasMotionBlur>`) |
| Icons, links | PNG icons; embedded links escaped the skill folder | SVG; cross-skill links flattened | same |

---

## 2D. Skills evals (`packages/skills-evals`)

### How a run works

1. `bun run eval run <scenario-id|--all> [--runs 1-4]` (max 4 runs; up to 8 run in parallel). `compare <id>
   [base-ref]` runs the same scenario with the skills at a git ref (default `origin/main` or
   `REMOTION_SKILLS_EVALS_BASE_REF`) and with the working tree; it is skipped when the skills did not change. `export`
   builds a static site (deployable with `vercel deploy`); `dev` starts a Bun web UI on `127.0.0.1:4321` (`PORT`).
2. For each run: copy `packages/template-blank` into `.runs/<scenario>/<timestamp>--<label>--<model>/project`, pin
   `@remotion/cli`, `@remotion/eslint-config-flat` and `remotion` to the latest published version (`bun pm view
   remotion version`, or `REMOTION_SKILLS_EVALS_REMOTION_VERSION`), copy every skill folder into `.pi/skills/`
   (symlinks are skipped, so the router's embedded subfolders are missing and each skill is discovered on its own;
   the built plugin form is never what is evaluated), hash the skill snapshot, `bun install`.
3. Phase "pi": `pi --extension pi-stream-extension.ts --eval-stream all --model <model> --session-dir <dir> -p
   <scenario prompt>` with the scenario timeout (20 minutes each).
4. Phase "pi-render": the same Pi session continues with a fixed prompt: render the final MP4 to
   `project/out/skills-eval.mp4`, not only to /tmp, and do not stop at a still.
5. Phase "pi-export": `pi --export <session.jsonl> session.html` for a readable transcript.
6. Artifacts: every `.gif .jpeg .jpg .mov .mp4 .png .webm` under the project (videos first); zero artifacts is an
   error. `manifest.json` records prompt, model, times, skill snapshot hash, artifacts and all four command logs;
   output with secret-looking env values is redacted.

### How it is graded

Not automatically. There is no rubric, assertion, score, vision judge or pass/fail. The UI shows each run's video (or
image), how long it took, links to the Pi session export and manifest, the prompt, and for comparisons the before and
after videos side by side with the unified skill diff. A human decides whether a skill change made the videos better.
(Implication for us: our evals should add measurable checks and a model judge, see section 7.)

### The five scenarios (all `openai-codex/gpt-5.5`, timeout 20 min)

| Id | Prompt essentials | What it tests |
|---|---|---|
| `vertical-promo-text-layout-proportions` | ~10 s vertical Instagram/TikTok launch ad for "FlowPilot" (week planning app) with 6 required phrases, animated shapes, app-style cards, smooth transitions | Vertical layout, text sizing and safe areas (the reason `video-layout.md` exists), exact copy inclusion, multi-scene transitions. |
| `landscape-promo-text-layout-proportions` | ~10 s landscape hero/pre-roll for the team version of FlowPilot with 5 required phrases, same visual asks | Landscape proportions, same copy fidelity and scene flow. |
| `map-trip-la-ny-paris-3d` | New composition: start on LA, zoom out while staying centred on LA, draw LA to New York with the camera following, continue to Paris, animate the Eiffel Tower in 3D | Maps skill: technique choice (Mapbox for 3D buildings), camera choreography, multi-leg routes, WebGL render settings. |
| `bar-line-chart-revenue-conversion` | 1920x1080 dark `#1A1A2E` comp `BarLineChart`: revenue bars $8K to $22K Jan to Jun growing from baseline, blue `#0B84F3` conversion line 2.1% to 4.2% drawn progressively with glow, sequential overlapping bars, axis labels, pulsing dot at the line tip, spring timing, 120 frames at 30 fps, "use the remotion-best-practices skill" | Data viz craft without a data-viz skill: exact values, staggered springs, line draw, glow, axis labelling, exact duration. |
| `youtube-subscribe-lower-third` | Scrape the Remotion YouTube channel with curl for avatar and the right subscriber count; white lower third sliding in from bottom centre with name, count, avatar and a fixed-width black Subscribe button that turns "Subscribed"; ease-out press, springy release with slight bounce; fade out; render as transparent ProRes | Data gathering, UI replication, easing vocabulary, and the transparent-video render path. |

---

## 2E. The Remotion MCP server (`packages/mcp`)

- Package `@remotion/mcp` 4.0.529, binary `remotion-mcp`, stdio transport, `McpServer({name: 'remotion-mcp',
  version: '1.0.0'})`, dependencies `@modelcontextprotocol/sdk` 1.26.0 and `zod` 4.1.13.
- One tool: `remotion-documentation` (title "Search the Remotion documentation"), input `{query: string}` ("keep it
  short and concise"). It GETs `https://mcp.remotion.dev/mcp/67cad4626afeae106c6ffb50?query=<query>` and returns the
  response text as one text content item. The query is interpolated without URL encoding.
- Status: deprecated. The docs say the hosted MCP shuts down no earlier than 2026-08-31 (today is 2026-09-25, so it
  may already be gone), because its data lags the docs, Remotion pays the tokens, agents invoke MCPs unreliably, and it
  duplicates `/remotion-docs`. Migration: remove it, run `npx remotion skills add`, use `/remotion-docs`.
- For our skills: do not depend on it. Use the local docs mirror first, then `https://www.remotion.dev/docs/<page>.md`.

---

## 3. API digest

Versions come from `AvailableFrom` notes in `mirror/docs` (the skills themselves rarely state versions). Everything
listed works on 4.0.528 unless marked **4.0.529**.

### 3.1 Timing and animation

| API | What it does, signature | Key options and defaults | Version | Gotchas |
|---|---|---|---|---|
| `useCurrentFrame()` | current frame, local to the enclosing Sequence | | core | Inside a Sequence starting at 60 it returns 0 to 29. |
| `useVideoConfig()` | `{fps, durationInFrames, width, height}` | overridden by `<Sequence width height>` | core | Use for all sizes and timings; do not hardcode 30 fps. |
| `interpolate(input, inRange, outRange, opts)` | map frame to value; out ranges may be numbers or CSS strings (`'0px 0px'`, `'20deg'`) | `extrapolateLeft/Right` default `extend` (unclamped), usually `'clamp'`; `easing` (function or array of n-1); `output: 'perceptual-scale'`; `posterize: n` | core; perceptual-scale 4.0.490 | Keep it inline for Studio editing; clamp by default. |
| `Easing.bezier(x1,y1,x2,y2)` | cubic-bezier easing | skill default `(0.16, 1, 0.3, 1)` (fast out, soft settle); maps use `(0.645, 0.045, 0.355, 1)` | core | |
| `Easing.spring(config)` | spring as an easing for `interpolate` | `damping` default 10, `mass` 1, `stiffness` 100, `overshootClamping` false, `durationRestThreshold` and `allowTail` (both 4.0.483); curve normalised to the interpolation segment, measured as if 30 frames | 4.0.476 | `{damping: 200}` = no-bounce push. Duration is set by the interpolate range. |
| `Easing.linear`, `Easing.in/out/inOut(Easing.quad/cubic/sin)` | classic easings | | core | Used by the team kit. |
| `spring({frame, fps, config, durationInFrames?})` | physics value 0 to 1 | `config.damping/stiffness/mass` | core | Not mentioned in official skills (they prefer `Easing.spring`), heavily used in the team kit. |
| `random(seed)` | deterministic 0 to 1 | | core | Not taught by the official skills; mandatory instead of `Math.random`. |
| `noise2D(seed, x, y)` | `@remotion/noise` smooth noise | | package | Used for wobble/talk pulses in the team kit. |
| `<Freeze frame>` | freezes children at a frame | | 2.2.0 | Team kit uses it to continue a caption from its last frame. |

### 3.2 Structure

| API | What it does | Key props | Version | Gotchas |
|---|---|---|---|---|
| `<Composition>` | registers a renderable video | `id`, `component`, `durationInFrames`, `fps`, `width`, `height`, `defaultProps`, `schema`, `calculateMetadata` | core | Inline `defaultProps`; `type` props; no type assertions. |
| `<Still>` | single image composition | no duration/fps | core | |
| `<Folder name>` | sidebar grouping | letters, numbers, hyphens only | core | (The stale 4.0.519 multi-scene example used `id`; `name` is correct.) |
| `<Sequence>` | place children in time | `from`, `durationInFrames`, `layout` (`absolute-fill` default, `none`), `name`, `premountFor`, `width`/`height`, `trimBefore` (4.0.482), `crop*` (4.0.500, needs absolute-fill), `playbackRate` (4.0.528) | core | Premount everything; `layout="none"` inside `<ThreeCanvas>` and for SFX. |
| `<Series>` / `.Sequence` | back-to-back | `durationInFrames`, negative `offset` to overlap, `layout`, `name` | core | Wraps in absolute fill unless `layout="none"`. |
| `<TransitionSeries>` | series with transitions and overlays | `.Sequence` (`durationInFrames`, `name`, `trimBefore` 4.0.497), `.Transition` (`presentation`, `timing`), `.Overlay` (`durationInFrames`, `offset`) | 4.0.59; Overlay 4.0.415 | Transitions shorten total; overlays do not; overlay not adjacent to a transition or overlay. |
| `<AbsoluteFill>` | full-frame flex container | inherits Sequence timing props (4.0.501), premount props (4.0.528) | core | `name` works on it. |
| `calculateMetadata` | async `({props, abortSignal}) => ({durationInFrames?, width?, height?, fps?, props?, defaultOutName?, defaultCodec?, defaultVideoImageFormat?, defaultPixelFormat?, defaultProResProfile?})` | | 4.0.0+ | `Math.ceil(seconds * fps)`; must be a plain function, not a hook. |
| `staticFile(path)` | URL for `public/` files | | core | Required for fetch of local JSON/SRT/audio. |
| `useDelayRender()` | scoped `{delayRender, continueRender, cancelRender}` | `delayRender(label, {timeoutInMilliseconds})` | 4.0.342; cancelRender 4.0.374 | Create the handle once (`useState(() => delayRender())`). |

### 3.3 Interactivity (Studio editing)

| API | What it does | Notes | Version |
|---|---|---|---|
| `Interactive.Div` (and other HTML/SVG tags: `Svg`, `Path`, `Circle`, `Ellipse`, `G`, `Line`, `Rect`, `Text`) | makes an element selectable, draggable, style and keyframe editable | inherits `durationInFrames`, `from`, `trimBefore`, `playbackRate`, `freeze`, `hidden`, `name`, `showInTimeline`; premount props from 4.0.528; `crop*` from 4.0.506 | 4.0.475 |
| `Interactive.withSchema()`, `Interactive.baseSchema` and other schemas | custom interactive components | include `baseSchema` to keep trimming/visibility | 4.0.479 |
| `interpolatePaths(frame, inRange, paths[], opts)` | editable path morph | **4.0.529** (not on 4.0.528); older `interpolatePath()` exists | 4.0.529 |

### 3.4 Media

| API | What it does | Key props | Version | Gotchas |
|---|---|---|---|---|
| `<Video>` / `<Audio>` from `@remotion/media` | frame-accurate media | `src`, `trimBefore`/`trimAfter` (frames), `from`/`durationInFrames` (4.0.445), `volume` (number or `f => number`, `f` from media start), `muted`, `playbackRate`, `loop`, `loopVolumeCurveBehavior`, `toneFrequency` 0.01 to 2, `style`, `objectFit`, `effects`, `crop*` (4.0.500), `premountFor` (4.0.495), `name` | package | No reverse; pitch only in server render. |
| `<Img>` | image | `style`; inherits timing props (4.0.465) | core | If `effects` is non-empty only CanvasImage props apply. |
| `<CanvasImage>` | canvas-drawn image with effects and crop | `src`, `width`, `height`, `style`, `effects`, `crop*` | 4.0.466 | The skills prefer it for images. |
| `<AnimatedImage>` | GIF/APNG/AVIF/WebP synced to the timeline | `width`, `height`, `fit`, `playbackRate`, `loopBehavior` | 4.0.246 | Chrome and Firefox only; fallback `<Gif>`. |
| `<Gif>`, `getGifDurationInSeconds()` | `@remotion/gif` | same props as AnimatedImage, GIF only | package | |
| `<Solid>` | a coloured canvas layer for effects | `width`, `height`, `effects`, timing props | 4.0.464 | Base for light leaks. |
| `<Lottie animationData style>` | `@remotion/lottie` | load JSON in delayRender | package | |
| `getImageDimensions(src)` | image size | | core | Usable in calculateMetadata. |
| Mediabunny `Input` | metadata in browser/Node/Bun | `formats: ALL_FORMATS`, `source: UrlSource/FileSource`; `computeDuration()`, `getPrimaryVideoTrack().displayWidth/Height` | mediabunny 1.56.1 in the kit | Install via `npx remotion add mediabunny`. |

### 3.5 Effects and canvas

| API | What it does | Options | Version | Gotchas |
|---|---|---|---|---|
| `effects={[...]}` | stack of per-element effects | 58 presets: brightness, contrast, colorKey, duotone, grayscale, hue, invert, saturation, tint, linearGradient, linearGradientTint, thermalVision, blur, linearProgressiveBlur, radialProgressiveBlur, zoomBlur, dropShadow, glow, lightTrail, evolve, venetianBlinds, mirror, scale, uvTranslate, xyTranslate, barrelDistortion, chromaticAberration, fisheye, cornerPin, wave, burlap, emboss, dotGrid, halftone, noise, noiseDisplacement, paper, roughenEdges, pattern, pixelate, pixelDissolve, scanlines, speckle, shine, shrinkwrap, vignette, contourLines, checkerboard, halftoneLinearGradient, gridlines, whiteNoise, tvSignalOff, lines, rings, waves, zigzag, lightLeak, starburst | `@remotion/effects` 4.0.464 | WebGL2: `--gl=angle` or `Config.setChromiumOpenGlRenderer('angle')`; keep the array literal for Studio; every effect accepts `disabled`. |
| `createEffect<Params, State>({...})` | custom effect factory usable in `effects` | `type` (reverse-DNS id), `label`, `documentationLink`, `backend` (`'2d'`, `'webgl2'`, `'webgpu'`), `calculateKey(params)`, `setup(target)`, `apply({source, target, width, height, params, state, flipSourceY})`, `cleanup(state)`, `schema` (InteractivitySchema), `validateParams` | 4.0.479 | `calculateKey` must include every output-changing param; reset 2D state after drawing; preserve alpha; `disabled` is added automatically. |
| `lightLeak({progress, seed, hueShift, disabled})` | light leak overlay | progress default 0.5 | 4.0.500 | Animate progress 0 to 1 across the overlay. |
| `<HtmlInCanvas width height onPaint onInit>` | DOM to canvas post-processing | `HtmlInCanvas.isSupported()` | 4.0.455 | Chrome 149+ flag only for preview; no nesting. |
| `<HtmlInCanvasMotionBlur width height samples shutterAngle>` | frame-sampled motion blur | samples 8, shutterAngle 180 | **4.0.529** | On 4.0.528 use `<CameraMotionBlur>` / `<Trail>` (`@remotion/motion-blur`, 3.2.39) per the docs guide. |

### 3.6 Text, fonts, annotations

| API | Signature | Notes |
|---|---|---|
| `loadFont(style?, {weights, subsets})` from `@remotion/google-fonts/<Family>` | returns `{fontFamily, waitUntilDone}` | Call at module top level; blocks the render until loaded. |
| `loadFont({family, url, format?, weight?, style?, display?})` from `@remotion/fonts` | promise | One call per weight. |
| `measureText({text, fontFamily, fontSize, fontWeight?, letterSpacing?, validateFontIsLoaded?})` | `{width, height}` (cached) | `@remotion/layout-utils` |
| `fitText({text, withinWidth, fontFamily, fontWeight?})` | `{fontSize}` | Cap the result. |
| `fillTextBox({maxBoxWidth, maxLines}).add({text, fontFamily, fontSize})` | `{exceedsBox}` | |
| `useCurrentScale()` | Studio zoom factor | Divide DOM measurements by it. |
| `@remotion/rough-notation` components | `progress`, `color`, `seed`, `roughness`, `strokeWidth`, `iterations`, `padding`, crop, effects | 4.0.490 |

### 3.7 Transitions, audio visualisation, captions, 3D

| API | Notes |
|---|---|
| `fade()`, `slide({direction})`, `wipe()`, `flip()`, `clockWipe()` | subpath imports `@remotion/transitions/<name>` |
| `linearTiming({durationInFrames})`, `springTiming({config, durationInFrames?})`, `.getDurationInFrames({fps})` | spring duration without explicit frames depends on fps |
| `useWindowedAudioData`, `visualizeAudio`, `visualizeAudioWaveform`, `createSmoothSvgPath`, `getWaveformPortion` | `@remotion/media-utils`; samples power of two |
| `Caption`, `createTikTokStyleCaptions`, `parseSrt` | `@remotion/captions` |
| `installWhisperCpp`, `downloadWhisperModel`, `transcribe`, `toCaptions` | `@remotion/install-whisper-cpp`, whisper.cpp 1.5.5, `medium.en`, 16 kHz WAV |
| `<ThreeCanvas width height>` | `@remotion/three`; no `useFrame` |
| `<Player ...>` | `@remotion/player`; `compositionWidth/Height` instead of width/height |

### 3.8 CLI and config

| Command / setting | Notes | Version |
|---|---|---|
| `npx create-video@latest --yes --blank --no-tailwind <dir or .>` | blank project | |
| `npx remotion studio --no-open` | `--port`, `--log`, `--force-new` (4.0.421), `--webpack-poll <ms>` (3.3.11), `--coding-agent=codex` (4.0.506), `--editor=cursor` (4.0.503), `--rspack` (4.0.502), `--allow-html-in-canvas` (4.0.447); press `s` to reopen (4.0.487) | `--no-open` 3.3.19 |
| `npx remotion render <id> <out>` | `--frames=0,30,90` now outputs an image sequence (4.0.502); ranges `0-99,150-199` concatenate; `--image-format`, `--codec`, `--pixel-format`, `--prores-profile`, `--gl=angle`, `--concurrency`, `--timeout` | |
| `npx remotion still <id> <out> --frame=N --scale=0.25` | quick layout check (from the 4.0.519 skill) | |
| `npx remotion add <pkg...>`, `upgrade`, `versions`, `ffmpeg`, `ffprobe`, `skills add/update` | version-aligned install; bundled ffmpeg | |
| `remotion.config.ts` | `Config.setVideoImageFormat`, `setPixelFormat`, `setCodec`, `setProResProfile`, `setChromiumOpenGlRenderer('angle')`; team kit adds `setRspack(true)`, `setOverwriteOutput(true)`, `setColorSpace('bt709')`, `overrideBundlerConfig(enableTailwind)` | |

### 3.9 Maps libraries (from the maps skill)

| API | Notes |
|---|---|
| `new mapboxgl.Map({accessToken, container, style, center, zoom, interactive: false, attributionControl: false, fadeDuration: 0, canvasContextAttributes: {preserveDrawingBuffer: true}})` | same shape for MapLibre and MapTiler |
| `map.on('load')`, `map.once('idle', cb)`, `map.triggerRepaint()`, `map.jumpTo({center, zoom, bearing, pitch})`, `getSource(id).setData()`, `setPaintProperty()`, `project(lngLat)`, `calculateCameraOptionsFromTo()` (MapLibre) | the frame loop primitives |
| Turf: `greatCircle(from, to, {npoints: 100})`, `lineString`, `length`, `lineSliceAlong(line, 0, max(0.001, km))`, `along`, `point`, `featureCollection`, `booleanPointInPolygon`, `bbox`, `bboxClip`, `polygonToLine`, `pointToLineDistance`, `simplify` | coordinates are `[lng, lat]` |
| Cesium: `new Viewer(el, {baseLayer: false, ...widgets off, contextOptions: {webgl: {preserveDrawingBuffer: true}}})`, `UrlTemplateImageryProvider`, `CesiumTerrainProvider.fromUrl(url, {requestVertexNormals: true})`, `Cesium3DTileset.fromUrl(googleRoot, {showCreditsOnScreen: true, maximumScreenSpaceError})`, `camera.setView({destination, orientation: {heading, pitch, roll}})` | heading radians clockwise from north; pitch 0 horizon, negative down |

---

## 4. Recipes

Short snippets show the real API shape; adapt names and values.

**R1. Title entrance that stays editable in Studio.**
```tsx
<Interactive.Div name="Title" style={{
  fontSize: 96,
  opacity: interpolate(frame, [0, 0.6 * fps], [0, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1)}),
  translate: interpolate(frame, [0, 0.6 * fps], ['0px 40px', '0px 0px'], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.bezier(0.16, 1, 0.3, 1)}),
}}>Launch day</Interactive.Div>
```

**R2. In, hold, out with one call:** input `[0, 1*fps, 9*fps, 10*fps]`, output `[0, 1, 1, 0]`, easing array
`[Easing.bezier(0.16,1,0.3,1), Easing.linear, Easing.spring({damping: 200})]` (n-1 easings).

**R3. Scale pop that looks linear:** add `output: 'perceptual-scale'` to any `scale` interpolation (4.0.490+).

**R4. Deliberate "on twos" motion:** `posterize: 2` or `3` in the interpolate options.

**R5. Multi-scene video with editable scene timelines.** One file per scene; parent uses `<TransitionSeries>` with
named `.Sequence` rows and inline `durationInFrames`; register each scene component as its own `<Composition>` inside
`<Folder name="MyVideo-Scenes">`; parent duration = sum of scenes minus each transition's
`timing.getDurationInFrames({fps})`.

**R6. Cut accent without changing timing:** a `<TransitionSeries.Overlay durationInFrames={16..30}>` holding a light
leak on `<Solid>` or a custom wipe (the team kit's `BarSweep`: skewed coloured bars crossing the frame, eased
`bezier(0.45,0,0.55,1)`, covering the cut at the midpoint).

**R7. Voiceover-led duration.** Generate one audio file per scene, then:
```tsx
export const calculateMetadata: CalculateMetadataFunction<Props> = async ({props}) => {
  const secs = await Promise.all(props.files.map((f) => getAudioDuration(staticFile(f))));
  const frames = secs.map((s) => Math.ceil(s * FPS));
  return {durationInFrames: frames.reduce((a, b) => a + b, 0), props: {...props, frames}};
};
```
Return the per-scene frames as props (the official example forgets to), and subtract transition overlaps.

**R8. Match the composition to footage:** `calculateMetadata` with Mediabunny `computeDuration()` and
`getPrimaryVideoTrack()` (`displayWidth`/`displayHeight`).

**R9. Word-highlight captions (TikTok style).** Fetch `captions.json` in `useDelayRender`; `createTikTokStyleCaptions`
with `combineTokensWithinMilliseconds` 1200 (lower = more word-by-word); a `<Sequence>` per page; inside, compare
`page.startMs + frame/fps*1000` with each token's `fromMs`/`toMs`; `whiteSpace: 'pre'`.

**R10. Kinetic sentence (team kit).** Split words; word i starts at `start + i*4` frames; opacity 0 to 1 over 8 frames,
rise 36 px to 0 over 10 frames with `bezier(0.16,1,0.3,1)`, blur 10 px to 0; key words wrapped in rough-notation
`<Underline progress=... strokeWidth={9} iterations={1} seed={7}>`; whole block slowly zooms 1 to 1.05 over the
scene; to continue the sentence in the next scene, render the old line inside `<Freeze frame={last}>` and lift it.

**R11. Silence trim of a talking-head clip:** loudnorm JSON pass for `input_thresh`, `silencedetect` with that
threshold and `d=0.5`, merge edge silences closer than 0.2 s, then `trimBefore`/`trimAfter` in frames.

**R12. Editable edit timeline:** independent clips as separate hardcoded `<Video from durationInFrames trimBefore>`
nodes, or ripple editing with `<TransitionSeries>` rows. Never `.map()` editable clips.

**R13. Transparent overlay export:** ProRes 4444 (`--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le
--image-format=png`, `.mov`) for NLEs; VP9 WebM (`--codec=vp9 --pixel-format=yuva420p --image-format=png`) for web.

**R14. Fast visual check:** `npx remotion render <id> out/frames --frames=0,45,90,135 --image-format=png`, or
`npx remotion still <id> --scale=0.25 --frame=30`. The team kit tiles 16 evenly spaced frames into one contact sheet
with ffmpeg (`scale=480:270,tile=4x4`).

**R15. Audio-reactive visuals:** `useWindowedAudioData` once in the parent, `visualizeAudio` with 128 or 256 samples,
bass = mean of the lowest quarter; drive `scale = 1 + bass*0.5`; pass `frame` to children; log-scale bars.

**R16. Data-true growth chart (team kit `StatScene`).** Precompute the full SVG path from the formula; reveal it with a
clipPath rect whose width follows an eased progress; the counter shows the formula value at the current progress with
`fontVariantNumeric: 'tabular-nums'`; a dot rides the tip; on arrival a 1 to 1.1 to 1 "land" scale and a repeating
pulse ring; axis maximum rounded up to 1, 2, 2.5, 4, 5 or 10 times a power of ten.

**R17. Staggered bar chart (team kit `StatBarsScene`).** Stagger bar starts (e.g. 22, 38, 54, 74 frames) so small bars
are seen growing; ease-out for small bars, ease-in for the hero bar; land-bounce the final value.

**R18. Map route:** Turf great circle, slice with `lineSliceAlong` (never zero length), camera by `jumpTo` only after a
short test render shows no shimmer; otherwise a fixed map plate (render once at max zoom in an oversized container up
to 4096 px per side, then CSS translate + scale <= 1, with overlays transformed the same way).

**R19. River or border reveal explainer:** time-based beats (river 0.3 s to 8 s; each country triggers on river
arrival, then border 2.5 s, fill bloom with 25% overshoot 1.0 s, label 0.7 s), a glowing leading head (last 3% of the
line), labels as React overlays projected each frame.

**R20. 3D terrain or city flyover:** `CesiumFlythrough` pattern; render a middle frame still first; `--gl=angle
--concurrency=1 --timeout=180000`.

**R21. Custom look:** CSS first; then a preset effect; then `createEffect({backend: '2d', ...})`; WebGL2 only when the
math needs it.

**R22. Code-drawn character (team kit).** Limbs as point chains computed from angles that change with the frame; draw
each limb twice (thick outline stroke, then fill stroke) for seamless joints; walk/run cycles from sines (thigh on a
sine, knee flex peaking as the thigh passes vertical, foot flat in stance); unique SVG ids with `useId()`.

**R23. Sound effects on cues:** `<Sequence from={cue} layout="none"><Audio src={whoosh} volume={0.85}/></Sequence>`
with `whoosh` etc. imported from `@remotion/sfx` and `<Audio>` from `@remotion/media`; whoosh 8 frames before a cut,
ding when a value lands, click on UI presses.

**R24. Avoid "frozen" holds:** any hold longer than about 0.7 s gets a slow push-in (scale 1 to 1.04) or drift.

---

## 5. Performance and render stability

- **Determinism:** only frame-driven values; `random(seed)`, never `Math.random()`/`Date.now()`; no CSS
  animations/transitions, Tailwind animation classes, R3F `useFrame`, self-animating shaders, map fades
  (`fadeDuration: 0`) or interactive map handlers.
- **Async gating:** every fetch or load (captions JSON, Lottie, fonts, maps, Cesium tiles) inside `delayRender` with
  `continueRender`/`cancelRender`; per-frame WebGL scenes need a `delayRender` per frame released on `idle` (maps) or
  after a settle loop (Cesium). Increase timeouts for heavy tiles: `timeoutInMilliseconds` 60000 to 120000 and
  `--timeout=180000`.
- **WebGL:** `--gl=angle` (or `Config.setChromiumOpenGlRenderer('angle')`) for effects, HtmlInCanvas WebGL, maps and
  Cesium; `preserveDrawingBuffer: true` or screenshots come out blank; concurrency 1 for maps and Cesium.
- **Map shimmer:** per-frame `jumpTo` on a moving camera resamples tiles and shimmers even on satellite imagery; the
  fix is a static renderer plus a CSS-transformed plate. Keep the plate at most 4096 px per side (Chromium silently
  downsamples bigger WebGL buffers); 3840x2160 for 1920x1080, about 2700x3840 for 1080x1920; never scale the plate
  above 1; split into two plates with an editorial cut if needed.
- **Slow cameras render fast:** at about 18 m per frame Cesium tiles stay cached and each settle returns quickly (720
  frames rendered in one pass).
- **Premount** sequences (`premountFor={fps}`) so media and fonts are ready before they appear.
- **Audio viz:** `optimizeFor: 'speed'`, power-of-two sample counts, windowed loading (30 s windows), one data load in
  the parent.
- **Pitch shift** (`toneFrequency`) only works in server rendering; Studio and Player ignore it.
- **HtmlInCanvas** is experimental: preview needs Chrome 149+ with a flag, rendering is automatic; nesting is rejected;
  `HtmlInCanvasMotionBlur` samples multiply render cost.
- **AnimatedImage** only in Chrome and Firefox; use `<Gif>` elsewhere.
- **Measured on this machine (team kit, 4.0.528, rspack, JPEG frames, 1920x1080 30 fps):** 60 s render in about 45 s,
  16 stills in about 5 s, typecheck about 3 s. Most session time is spent writing scene code and reviewing, not
  rendering.
- **Eval harness limits:** at most 4 runs per scenario, 8 in parallel, 20 minutes per Pi phase.

---

## 6. Errors and fixes

### 6.1 Known problems the skills document

| Symptom | Cause | Fix |
|---|---|---|
| Animation flickers or differs between preview and render | CSS/Tailwind animation, `useFrame`, timers | Drive everything from `useCurrentFrame()`. |
| Frozen first frames after trimming a file | stream copy trim | Re-encode (`-c:v libx264 -c:a aac`) or trim in Remotion with `trimBefore`. |
| Turf error at progress 0 | zero-length `lineSliceAlong` | Use `Math.max(0.001, km)`. |
| Great-circle route becomes MultiLineString | antimeridian crossing | Keep the longest segment (or unwrap longitudes, as `smoothFlightPath` does). |
| Country fills missing, halos without cores (MapTiler) | `filter: undefined` passed to a layer | Spread the filter only when present. |
| Moving 2D map shimmers | per-frame `jumpTo` resampling | Fixed map plate. |
| Plate looks soft during a push | plate underspecified, downsampled or scaled above 1 | Render at the max zoom of any waypoint, keep <= 4096 px, CSS scale <= 1. |
| Black frames with stars (Cesium) | headless Playwright or `scene.render()` | Render through Remotion, `viewer.render()`, `useDefaultRenderLoop = false`. |
| Blank or transparent WebGL frames | no `preserveDrawingBuffer` | Set it in the context options. |
| "delayRender timed out" | cold tiles | `timeoutInMilliseconds: 120000` and `--timeout=180000`. |
| Dark navy globe | imagery layer not attached | `baseLayer: false` then add the imagery provider. |
| Void above horizon | no atmosphere | `skyAtmosphere.show = true`. |
| 403 on MapTiler tiles | domain-locked key | Unrestricted key for headless rendering. |
| 403 on Google 3D Tiles | API disabled, no billing, wrong key or restriction | Enable Map Tiles API and billing; allow the local request. |
| Duplicate surface in city mode | MapTiler or globe still enabled | Hide the globe; do not add MapTiler. |
| Coarse Google mesh | high screen-space error or early capture | Lower `maximumScreenSpaceError` (4 hero, 6 to 8 wide); settle on `tileset.tilesLoaded`. |
| Camera looks at sky | pitch sign | Cesium pitch is negative downwards: `-(90 - pitchFromNadir)`. |
| Look-ahead clamps at the end | path too short | Path length >= travel + 2 x look-ahead. |
| Straight-then-corner camera | Douglas-Peucker simplification | Resample, moving-average smooth, dampen; Chaikin 3 passes. |
| Studio values greyed out | markup too complex to parse | Inline styles and interpolates, hardcoded values, `Interactive.*`. |
| DOM measurements off in Studio | canvas zoom | Divide by `useCurrentScale()`. |
| Text measured wrong | font not loaded yet | `waitUntilDone()` then measure; `validateFontIsLoaded`. |
| Codex: `EMFILE: too many open files, watch` | watcher limits | `npx remotion studio --no-open --webpack-poll 1000`; else user starts Studio in Terminal. |
| Codex: Chromium sandbox errors | Codex/macOS sandbox | Not a project bug; run outside the sandbox. |

### 6.2 Errata in the official skills (do not copy these into our skills)

| File | Problem | Correct |
|---|---|---|
| `remotion-markup/sfx.md` | `import { Audio } from "@remotion/sfx"` | `@remotion/sfx` exports URL constants (`whoosh`, `ding`, `uiSwitch`, ...); `<Audio>` comes from `@remotion/media`. |
| `remotion-markup/embedding-videos.md` | says `trimBefore`/`trimAfter` "values are in seconds" | Frames (the examples use `2 * fps`; `audio.md` and the docs say frames). |
| `remotion-markup/SKILL.md` (FadeIn) | uses `fps` without `useVideoConfig()` | Destructure `fps` first. |
| `remotion-interactivity/SKILL.md` | `calculateMetadata` wrapped in `useMemo` | A plain async function passed to `<Composition>`. |
| `remotion-markup/parameters.md` | component ignores its props (`props.title` undefined), import typo `MycComponent`, only checks `bun.lockb` | Destructure props; also detect `bun.lock`; better: `npx remotion add zod`. |
| `remotion-render/transparent-videos.md` | WebM `calculateMetadata` example sets `defaultCodec: 'vp8'` while the CLI uses vp9 | Use `vp9` consistently (both support alpha). |
| `remotion-markup/voiceover.md` | claims per-scene durations reach the component via a prop, but returns only `durationInFrames` | Return them in `props`. |
| `remotion-markup/effects.md` | mixes `@remotion/effects/<slug>` and root imports; points to monorepo-only files and an internal `add-effect` skill | Follow the effect's docs page for the import path. |
| maps `render-stability.md` (mapbox, maplibre copies) | text says "MapTiler" everywhere | Applies to all GL map libraries. |
| maptiler sample data | borders start exactly on the frame bbox edge (lng 104, lat 33.5), i.e. clipped, contrary to "never clip borders" | Use complete borders in production. |
| MCP `src/index.ts` | query not URL-encoded | Encode with `encodeURIComponent` if ever reused. |
| `packages/codex-plugin` | stale 4.0.519 build tracked in git | Ignore; use `agent-plugin` builds. |
| Evals | copy skills without symlinks, so the router's `./remotion-create/SKILL.md` links are broken in the eval sandbox | Our evals should test the installed (built) form. |

---

## 7. What our skills must teach

### 7.1 Non-negotiable rules

- Every visual change is a function of `useCurrentFrame()`; ban CSS/Tailwind animation, `useFrame`, timers,
  `Math.random`, `Date.now`, and any self-running animation (Lottie is fine: it is frame-synced by `@remotion/lottie`).
- Clamp interpolations by default; express times as `n * fps`; read sizes from `useVideoConfig()`.
- Use `staticFile()` for local assets; remote assets need CORS; gate every async load with `useDelayRender` and
  `cancelRender` on failure.
- Install packages only with `npx remotion add`; keep all `remotion`/`@remotion/*` on one exact version (no caret).
- On this machine the API ceiling is 4.0.528: no `<HtmlInCanvasMotionBlur>`, no `interpolatePaths()`; check any newer
  API against `mirror/docs` `AvailableFrom` before use (`npx remotion versions` confirms the project).
- Preserve user edits made outside the conversation.
- Premount sequences; `layout="none"` for audio-only and 3D-internal sequences.
- WebGL work renders with `--gl=angle`; maps and Cesium also with `--concurrency=1` and long timeouts.
- Media trims are frames; volume callbacks are media-relative; pitch shifting is render-only.

### 7.2 Defaults (when the brief says nothing)

| Decision | Default |
|---|---|
| Entrance easing | `Easing.bezier(0.16, 1, 0.3, 1)`, 0.4 to 0.7 s |
| Soft push without bounce | `Easing.spring({damping: 200})` or `spring({config: {damping: 200}})` |
| Playful pop | `spring` with damping 11 to 14, stiffness 150 to 220 |
| Scale animation | `output: 'perceptual-scale'` |
| Word stagger | 3 to 4 frames per word; 8 to 10 frames per word fade/rise |
| Scene transition | slide or wipe of 8 to 20 frames with `springTiming({config: {damping: 200}})`; avoid fades between two bright scenes (reads as an exposure dip) |
| Holds | never longer than about 0.7 s without slow motion (push-in 1 to 1.04) |
| Safe area | at least 80 px sides and 100 px top/bottom at 1080 px width, scaled; for YouTube also keep clear of the top-left (title) and bottom-right (time) corners; team rule: 5% from every edge |
| Minimum text at 1080 px width | headline 84 px, important supporting text 44 px (scale with width) |
| Fonts | `@remotion/google-fonts` with explicit weights and `subsets: ['latin']` (add the script's subset for Bengali etc.) |
| Numbers that count | `fontVariantNumeric: 'tabular-nums'` |
| Colour space | BT.709 for SDR delivery (`Config.setColorSpace('bt709')`) |
| Preview | `npx remotion studio --no-open`, open `/<composition-id>` |
| Visual check | `render --frames` at key frames or a 16-frame contact sheet |
| Editability | Studio-editable markup for anything a human may tweak; programmatic `.map()` allowed for data-driven elements that nobody hand-edits (charts, particles), because the editability rules forbid loops only for clips meant to be edited |

### 7.3 Decision tables

**Sequencing primitive**

| Need | Use |
|---|---|
| Place layers independently | `<Sequence from durationInFrames>` or timing props directly on the component |
| Back-to-back scenes, no transitions | `<Series>` |
| Transitions between scenes, ripple editing, cut overlays | `<TransitionSeries>` with `.Transition` / `.Overlay` |
| A scene that needs its own editable timeline | connected composition (same component registered as a `<Composition>`) |
| Nested scene at other dimensions | `<Sequence width height>` |

**Image-like source**

| Source | Use |
|---|---|
| Still image, no effects | `<Img>` |
| Still image with effects or crop | `<CanvasImage>` |
| GIF/APNG/WebP/AVIF | `<AnimatedImage>` (Chrome, Firefox) else `<Gif>` |
| Vector animation | `<Lottie>` |
| Flat colour layer for an effect | `<Solid>` |
| Arbitrary DOM post-processing | `<HtmlInCanvas>` (preview needs the Chrome flag) |

**Visual effect route:** CSS or SVG first; then a preset from `@remotion/effects`; then `createEffect()` (reusable,
Studio-editable); `HtmlInCanvas onPaint` only for one-off DOM post-processing.

**Map technique**

| Shot | Technique |
|---|---|
| Location context only, nothing moves | static-map |
| Styled route, globe, 3D landmark buildings, token available | mapbox |
| Free, no key, 2D route | maplibre |
| Borders, rivers, labels drawn as story annotations | maptiler |
| Terrain or city flythrough, banking camera | cesium (landscape or city) |

**Caption source:** existing SRT: `parseSrt`; audio only: whisper.cpp transcription to `Caption` JSON; display:
TikTok pages plus token highlight.

**Transparent output:** editing software: ProRes 4444 MOV; browser: VP9 WebM.

**Rendering for apps:** fastest/scalable: Lambda; app on Vercel: Vercel Sandbox; own server: Node SSR / render
server template; GitHub Actions, Azure only on request; Cloudflare Containers when asked.

### 7.4 Checklists

- **Intake:** platform and aspect (16:9, 9:16, 1:1, 4:5), duration, fps, copy (exact phrases), brand (fonts,
  colours, logo), voiceover or music, assets available, delivery format (MP4, transparent MOV/WebM, GIF), deadline for
  review. Official skills never ask these; our skills should.
- **Before writing code:** Remotion version; packages present; fonts loaded; composition registered with inline
  metadata; scene plan with frame budget per beat.
- **Before rendering:** stills at key frames; text inside safe area and within minimum sizes; no text overflow
  (`fillTextBox`/`fitText`); no hold over 0.7 s without motion; transitions not fading between bright scenes;
  counters and charts judged on their settled frame; drawing order at contact moments; copy spelled exactly.
- **After rendering:** ffprobe duration, fps, resolution, codec, colour space; audio present and levels (YouTube
  about -14 to -16 LUFS integrated); black or frozen frames; a model review of the video against the brief.

---

## 7A. Gap analysis: what the official skills do not cover

The official skills are an API and editability guide. They contain one design file (`video-layout.md`, nine lines)
and no motion design, story, sound or QA doctrine. Gaps, by the kinds of video we must produce:

### Professional motion graphics
- No motion design principles: easing vocabulary per intent (entrance, exit, emphasis, transition), timing tables,
  anticipation, overshoot, follow-through, overlapping action, secondary motion, stagger systems, rhythm.
- No design system: type scales, font pairing, grids, spacing, colour palettes and contrast, hierarchy, brand kits,
  style presets or reference looks. Only the safe-area and minimum-size rule.
- No kinetic typography: per-character or per-word reveals, masks, text on path, typewriter, split/scramble text,
  variable font animation (only rough-notation highlights).
- No shape and path craft: `@remotion/shapes`, `@remotion/paths` draw-on (`evolvePath`), `@remotion/noise`,
  `@remotion/starburst`, `@remotion/rounded-text-box`, `@remotion/animation-utils`, `@remotion/layout-utils` beyond
  measuring, `@remotion/timeline-utils`, `@remotion/svg-3d-engine` are all in the monorepo but untaught.
- No component library: lower thirds, logo reveals, callouts, arrows, progress bars, device mockups, UI animations,
  end cards (the evals ask for a lower third and promo cards, yet no skill teaches them).
- No camera language for 2D scenes (push-ins, parallax layers, whip pans, focus pulls), no depth tricks.
- Motion blur on 4.0.528 is not covered at all (the only guidance is the 4.0.529 component).

### Explainers
- No scripting or storyboard step, no beat sheet, no "one idea per scene" planning beyond one focal element.
- Voiceover is limited to one ElevenLabs call; no voice direction, no timing animation to words or phrases (captions
  have word timestamps but nothing uses them as animation cues), no music bed, no ducking.
- No diagrams, icons, arrows, annotations beyond rough-notation; no reusable illustration or character rigging (the
  team kit covers rigs).

### Social videos
- No platform specs: 1080x1920 / 1080x1080 / 1080x1350, frame rates, maximum lengths, safe zones for TikTok, Reels and
  Shorts UI overlays, cover frames, hook in the first second, loop endings, caption placement above the UI.
- No loudness targets, no file size or bitrate guidance.
- Vertical layout is only tested by an eval prompt, not taught.

### Data videos
- No chart skill, although an eval asks for a combo bar and line chart. Missing: d3 scales and axes, nice ticks,
  number formatting and locale, animated counters, staggered bars, line draw-on, area fills, annotation of key values,
  data-driven composition via `calculateMetadata` and zod schemas, keeping visuals true to the data.

### 3D
- `3d.md` covers only the canvas wrapper, lights and the `useFrame` ban. Missing: camera animation, GLTF/GLB loading
  inside `delayRender`, textures and video textures, PBR materials, environment maps, shadows, post-processing, the
  WebGPU canvas (docs mention `three-webgpu-canvas` inherited props from 4.0.528), performance and GL flags for Three,
  and determinism of loaders.

### Edits from real footage
- `video-editing.md` covers only how to structure clips for Studio. Missing: cutting on action or beat, J and L cuts,
  audio crossfades and ducking, speed ramps (only constant `playbackRate`), reframing 16:9 to 9:16 with subject
  tracking, colour correction and looks (effects like `contrast`, `saturation`, `duotone` exist but are not taught for
  grading), green screen (`colorKey` exists, untaught), video matting (`@remotion/video-matting` exists in the docs),
  stabilisation, jump-cut removal beyond silence trimming, B-roll insertion over A-roll, multicam, subtitles styling
  for burn-in beyond the TikTok example, proxy workflows for heavy footage.

### Audio
- No mix model: levels for voice, music and SFX, ducking, fades at cuts, loudness normalisation, music selection and
  licensing, beat detection for cutting; SFX are a list of URLs.

### Quality assurance and verification
- "Visual checks" is one paragraph. No contact sheets, no automated checks (text overflow, safe area, contrast,
  spelling against the brief, black or frozen frames, audio silence, duration and codec), no model or human review
  rubric. The official evals themselves have no grading.

### Operations
- Rendering outputs beyond transparency: codecs, CRF and bitrate, BT.709, GIF output, audio codecs, image sequences,
  hardware acceleration, concurrency tuning, platform presets. Performance of heavy compositions (memoisation,
  expensive per-frame work, prefetching large media) is not covered.
- Asset sourcing (images, icons, stock footage, AI generation, licensing) is absent apart from the SFX list and
  `remotion.media` samples.
- Localisation: right-to-left scripts, complex scripts (Bengali shaping, font subsets), long translated strings.
- Global skill updates: the upgrade flow does not update `~/.claude/skills`.

### Where the official material is strong (reuse it)
Maps (all five techniques), Studio-editable markup rules, multi-scene structure with connected compositions,
transitions and duration math, captions pipeline, effects API and `createEffect`, transparent rendering, silence
detection, SaaS rendering choices.

## 7B. The team's installed kit `remotion-broll` (not official)

- Purpose: explainer B-roll at 1920x1080, 30 fps with sound effects; version `2026.09.25.1`; Remotion 4.0.528, React
  19.2.3, TypeScript 5.9.3, mediabunny 1.56.1, zod 4.5.4 (from the lockfile); packages include `@remotion/media`,
  `noise`, `paths`, `rough-notation`, `sfx`, `shapes`, `tailwind-v4`, `transitions`, `layout-utils`,
  `google-fonts`.
- Workflow script `scripts/broll.py`: `new` (copy kit, `npm ci`, or link `node_modules` of the same Remotion
  version; never overwrites), `check` (tsc, then every on-screen line from `src/copy.ts` through codex-design's
  copylint via `copy/onscreen.json`), `stills` (16 frames and a contact sheet), `render` (timed, then
  agy-watch-video measured QA), `review` (Gemini review with every copy line checked on screen).
- Structure worth copying: all words in one `copy.ts`, numbers in `GROWTH`, look in `theme.ts`, scenes each their own
  composition inside folders, `BrollDemo` (10 s) + `Part2` (50 s) = `BrollMinute` (60 s) via `<Series>`,
  `TransitionSeries` with `BarSweep` overlays and spring slides, SFX placed with a cue table, presenter PiP with a
  noise-driven "talking" ring.
- Craft rules learned from reviews: 0.7 s hold rule, no fade between bright scenes, check drawing order at contact
  moments, stagger small bars, judge settled frames of counters, feet follow the shin, break two-line titles by hand,
  5% edge margin and YouTube corners, BT.709, Remotion cannot make a photo act (use footage or image-to-video).
- Tests: 10 offline unit tests (kit completeness, pinned versions, copy only in `copy.ts`, charts from `GROWTH`,
  `new` never overwrites, linked modules must match).
- It is one style (warm flat caricature). The new family should generalise its pattern: kit plus scripts plus
  measured QA plus review, per video type.

---

## 8. Best examples to learn from

| Path | Why |
|---|---|
| `repo/packages/skills/skills/remotion-interactivity/SKILL.md` | The exact contract for Studio-editable markup, with good and bad examples. |
| `repo/packages/skills/skills/remotion-markup/transitions.md` | Clear model of transitions versus overlays and duration arithmetic. |
| `repo/packages/skills/skills/remotion-markup/connected-compositions.md` | The precomposition pattern for multi-scene videos. |
| `repo/packages/skills/skills/remotion-markup/effects.md` | Complete `createEffect()` contract with 2D and WebGL2 skeletons and authoring rules. |
| `repo/packages/skills/skills/remotion-maps/techniques/maptiler/assets/RiverReveal.tsx` | Data-triggered, time-based sequencing, fixed map plate, projected React labels, glowing draw head. |
| `repo/packages/skills/skills/remotion-maps/techniques/cesium/assets/CesiumFlythrough.tsx` | Robust `delayRender` gating, settle loop, arc-length camera with look-ahead and bank. |
| `repo/packages/skills/skills/remotion-maps/techniques/cesium/references/3d-troubleshooting.md` | Model symptom, cause, fix table to imitate. |
| `repo/packages/skills/skills/remotion-maps/techniques/mapbox/TECHNIQUE.md` | Per-frame WebGL update loop (`delayRender`, `setData`, `jumpTo`, `once('idle')`, `triggerRepaint`). |
| `repo/packages/skills/skills/remotion-maps/techniques/mapbox/references/render-stability.md` | Diagnosis of render shimmer versus softness and the plate sizing rules. |
| `repo/packages/skills/skills/remotion-captions/display-captions.md` | End-to-end caption display with highlighting. |
| `repo/packages/skills/skills/remotion-markup/silence-detection.md` | Adaptive loudness-based silence detection mapped to trims. |
| `repo/packages/skills/skills/remotion-create/video-layout.md` | The only layout numbers in the official set. |
| `repo/packages/skills-evals/scenarios.ts` | Ready prompt benchmark (promo vertical/landscape, map, chart, lower third) to reuse in our evals. |
| `repo/packages/agent-plugin/build.mts` | How to specialise one skill source per client at build time. |
| `repo/packages/skills/scripts/prepare-embedded-skills.ts` | How to ship embedded sub-skills without duplicate discovery. |
| `~/.claude/skills/remotion-broll/template/src/components/Guitarist.tsx`, `Runner.tsx` | Procedural 2D character rigs and cycles. |
| `~/.claude/skills/remotion-broll/template/src/scenes/StatScene.tsx`, `scenes2/StatBarsScene.tsx` | Data-true chart animation. |
| `~/.claude/skills/remotion-broll/template/src/Part2.tsx` | TransitionSeries with overlays, cue-table SFX, PiP overlay. |
| `~/.claude/skills/remotion-broll/scripts/broll.py` | Stills contact sheet, measured QA and review loop around Remotion. |

---

## 9. Open questions

1. Is upgrading this machine to 4.0.529 worthwhile (gains `HtmlInCanvasMotionBlur` and `interpolatePaths`)? If so,
   the global skills must be updated separately with `npx skills update ... --yes`.
2. How does Claude Code name skills that come from the `remotion` plugin (plain `/remotion-best-practices` as the docs
   show, or plugin-namespaced)? If both the plugin and the global skills are installed, which wins?
3. Pi (pi.dev) version and whether Remotion evaluates with Claude models at all; no eval results are in the repo, so
   there is no public evidence of which skill changes improved videos.
4. Does HTML-in-canvas rendering work headless on this Mac without extra flags (docs say yes)?
5. Should our skills keep the official Studio-editability constraints (inline everything, no `.map()` for clips)
   everywhere, or only when the user plans to edit in Studio? They conflict with reusable component libraries.
6. Is the hosted MCP already shut down (date passed)? Irrelevant if we never use it.
7. The org repo `remotion-dev/skills` ships the `.tsx` map assets but the plugins do not; should our maps guidance
   bundle full components or reference them?
8. Agent Skills limits (Vally lint rules) that our own skills should pass if we ever publish them.
