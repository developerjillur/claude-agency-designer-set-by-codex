# D4: rendering, CLI, Studio, Player, web rendering, codemods (knowledge file)

Agent: D4-render-studio-player. Target runtime: Remotion 4.0.528 (React 19) on macOS (Mac Studio, 36 GB RAM).
Everything below is written from the assigned docs; where the docs were silent or contradictory I checked the
installed `@remotion/*` 4.0.528 packages in `nexa-media/remotion-broll/node_modules` (read only) and say so.

---

## 1. Scope and coverage

- Assigned: 158 docs pages. Read fully: 158. Coverage list: `kb/D4-render-studio-player.coverage.txt` (158 lines, no
  duplicates, no missing entries; verified with `comm` against the assignment file).
- Breakdown: `@remotion/renderer` 17, CLI 18, Studio 27, Studio protocol 9, Player 16, `@remotion/preload` 5,
  browser bundler 5, client-side rendering 6, web renderer 6, licensing/license 4, accessibility 2,
  `<HtmlInCanvas>` 1, codemods 34, contributing 8.
- Placeholders that the mirror does not resolve: many pages embed `<Options id="..."/>` (option text generated from
  source) and twoslash `^?` type popups. I resolved all option texts and defaults by loading the installed
  `@remotion/renderer/dist/options/*.js` 4.0.528 definitions with a throwaway script (rendered their JSX descriptions
  to text and called `getValue()` for defaults). I also read the installed codec/CRF/pixel-format/audio-codec tables
  (`dist/crf.js`, `codec.js`, `file-extensions.js`, `pixel-format.js`, `image-format.js`, `options/audio-codec.js`,
  `get-codec-name.js`, `get-concurrency.js`, `can-use-parallel-encoding.js`,
  `validate-even-dimensions-with-codec.js`), the web renderer type unions, and the `@remotion/codemods` type exports.
  These are marked "(installed code)".
- Pages that are not what their path suggests:
  - `mirror/docs/contributing/docs.md` contains the Getting Started / Installation page, not "Writing documentation".
  - `mirror/docs/license/pricing.md` is only a `<Pricing>` React component; no prices in the mirror. Prices are in
    `license/faq.md`.
  - `player/drag-and-drop.md` and `preload/resolve-redirect.md` are HTML conversions with twoslash noise; readable.
  - `renderer/types.md` and `web-renderer/types.md` show only type names (twoslash); unions taken from installed code.
- Supplementary reads for context (not in the assignment): `repo/packages/template-render-server/server/render-queue.ts`,
  its `remotion.config.ts`, and the official skills `repo/packages/skills/skills/remotion-render` (plus
  `transparent-videos.md`), `remotion-studio`, `remotion-interactivity`.
- Nothing was unreadable.

---

## 2. Mental model

1. **Pipeline (server-side rendering, SSR).** Source -> `bundle()` / `npx remotion bundle` (Webpack, or Rspack with
   `--rspack` since 4.0.502) -> a *serve URL* (folder or hosted URL) -> `selectComposition()` runs that composition's
   `calculateMetadata()` with your `inputProps` -> `renderMedia()` starts Chrome Headless Shell, opens
   `concurrency` tabs, each tab seeks to a frame and takes a screenshot (JPEG by default, PNG for alpha) -> frames go to
   FFmpeg (bundled 7.1 build) -> audio is mixed separately -> muxed into the container. Every frame is rendered
   independently, possibly in a different tab, so a frame must be a pure function of (frame, props).
2. **One option, four places.** Resolution order for any render option: value passed to the Node API > value set in the
   Studio render dialog > CLI flag > `remotion.config.ts` > default. The config file does NOT apply to Node APIs
   (`renderMedia()` etc.); pass options directly there. CLI flags are kebab-case, Node options camelCase, numeric
   options carry their unit (`timeoutInMilliseconds`, `durationInFrames`).
3. **Codec decides almost everything else.** Container/extension, allowed audio codecs, default audio codec, CRF range
   and default, whether video bitrate is allowed, whether parallel encoding is used, whether dimensions are forced
   even, whether hardware encoding exists. Pick the codec from the delivery target first, then the rest follows
   (decision table in section 7).
4. **Quality knobs are mutually exclusive.** Either `crf` (constant quality) or `videoBitrate` (target bitrate), never
   both. Hardware encoders (VideoToolbox on macOS, NVENC on Linux/Windows) refuse `crf`, `bufferSize`, `maxRate`.
5. **Studio = preview + visual editor that writes code.** Since 4.0.475 the Studio edits your source files
   (drag, scale, rotate, keyframes, easing, props, effects) with undo/redo. It can only edit code written in a
   statically analysable way (inline styles, inline `interpolate()`, inline `defaultProps`, named `Interactive.*`
   elements). Code style therefore decides whether a human can fine-tune an agent's video.
6. **Player = composition inside any React app.** No `<Composition>`: you pass the component, fps, size and duration.
   It is the preview surface for web apps, Element libraries and editors. Performance hinges on not re-rendering it.
   Premounting and the buffer state only matter in Player/Studio playback, never in rendering.
7. **Client-side rendering (web renderer) is an emulation.** `renderMediaOnWeb()` does not screenshot the page; it
   walks the DOM and redraws a supported subset of CSS onto a canvas, then encodes with WebCodecs/Mediabunny. It is
   single-threaded, needs CORS-clean assets, and only supports `@remotion/media` `<Video>`/`<Audio>`.
8. **Codemods (4.0.528, draft) = the Studio's editing engine as a library.** Pure functions over an in-memory
   `{rootDir, files}` project that return file diffs (`previousContents`/`nextContents`), never touching disk. An agent
   can use them for safe, structured edits (add media, split sequences, set keyframes) with trivial undo.
9. **Version discipline.** Many features in this area are brand new (4.0.4xx to 4.0.528). The docs track 4.0.529+;
   one feature here (browser-bundler JSX source locations) is 4.0.529 and NOT available on 4.0.528. Everything tagged
   "Draft API" or experimental may change.
10. **Licensing is part of the render API surface.** Remotion is source-available; organisations above 3 people need a
    Company License, and anything that calls render APIs or embeds `<Player>` counts as an "automation"
    (per-render pricing). `licenseKey` / `isProduction` options exist on the render APIs.

---

## 3. API digest

### 3.1 `@remotion/renderer` (Node.js and Bun only; not browsers, not serverless functions)

#### `renderMedia()` (since v3.0): render video or audio
Required: `serveUrl`, `composition` (a `VideoConfig` from `selectComposition()`/`getCompositions()`), `codec`.

| Option | Type / values | Default | Since | Notes |
|---|---|---|---|---|
| `outputLocation` | path | `null` -> returns `buffer` | | absolute or cwd-relative file path, not a folder |
| `inputProps` | JSON object | | | pass the SAME object to `selectComposition()` |
| `frameRange` | `number` / `[a,b]` / `[a,null]` / `[[a,b],[c,d]]` | all frames | `[a,null]` 4.0.421; arrays 4.0.502 | inclusive; ranges ordered, non-overlapping, open end only last; gaps dropped from video and audio |
| `concurrency` | number, `"50%"`, `null` | `null` | | installed code: `null` -> `round(min(8, max(1, cpus/2)))`; > cpus or < 1 throws |
| `imageFormat` | `jpeg` / `png` / `none` | `jpeg` | | png for alpha; none for audio-only |
| `jpegQuality` | 0-100 | 80 (Chrome) | renamed from `quality` in 4.0 | only with jpeg |
| `crf` | number | per codec (table 3.3) | | not with `videoBitrate`, not with HW accel |
| `videoBitrate` | FFmpeg `-b:v` string e.g. `"8M"` | `null` | 3.2.32 | ignored for prores and audio codecs |
| `bufferSize` / `maxRate` | FFmpeg `-bufsize` / `-maxrate` | `null` | 4.0.78 | `maxRate` requires `bufferSize` |
| `audioCodec` | `pcm-16` / `aac` / `mp3` / `opus` | per codec | | overrides codec-implied audio |
| `audioBitrate` | `-b:a` string | `320k` | 3.2.32 | |
| `sampleRate` | Hz | 48000 | 4.0.448 | match the source to avoid resampling |
| `muted` | boolean | false | 3.2.1 | no audio track at all |
| `enforceAudioTrack` | boolean | false | 3.2.1 | adds a silent track when there is no audio; needed for chunks that get concatenated; `muted` wins |
| `separateAudioTo` | path | `null` | 4.0.123 | audio written to its own file; extension picks the audio codec; silent file even with no audio |
| `pixelFormat` | see 3.3 | `yuv420p` | | alpha formats need png |
| `colorSpace` | `default`, `bt601`, `bt709`, `bt2020-ncl` | `default` | 4.0.28 | see 3.3 |
| `proResProfile` | `4444-xq`, `4444`, `hq`, `standard`, `light`, `proxy` | `hq` | | prores only, else TypeError |
| `x264Preset` | `ultrafast` ... `placebo` | `medium` | | h264 / h264-mkv / h264-ts only, else TypeError |
| `gopSize` | int (`-g`) | encoder decides | 4.0.466 | keyframe interval |
| `hardwareAcceleration` | `disable` / `if-possible` / `required` | `disable` | 4.0.228 | see 3.3 |
| `scale` | 0 < s <= 16 | 1 | | multiplies output pixels; vectors and text re-rasterise sharply |
| `everyNthFrame` | int | 1 | 3.1.0 | GIF only |
| `numberOfGifLoops` | `null` / 0 / n | `null` (infinite) | 3.1.0 | 0 = play once, 1 = play twice |
| `metadata` | `Record<string,string>` | `{}` | 4.0.216 | embedded container tags |
| `envVariables` | `Record<string,string>` | | | readable as `process.env` in the bundle |
| `timeoutInMilliseconds` | ms | 30000 | | max wait for `delayRender()` per frame |
| `puppeteerInstance` | from `openBrowser()` | new browser per call | | you must close it; its launch flags win over `chromiumOptions` |
| `browserExecutable` | path | auto-detect / download | 3.0.11 | |
| `chromeMode` | `headless-shell` / `chrome-for-testing` | `headless-shell` | 4.0.248 | chrome-for-testing to use GPU drivers on Linux |
| `chromiumOptions` | `{disableWebSecurity:false, ignoreCertificateErrors:false, headless:true, gl, userAgent (3.3.83), darkMode:false (4.0.381), enableMultiProcessOnLinux:true (4.0.42)}` | | 2.6.5 | set at browser launch |
| `offthreadVideoCacheSizeInBytes` | bytes | `null` = half of system RAM | 4.0.23 | bigger = faster, more RAM |
| `offthreadVideoThreads` | int | 2 | 4.0.261 | "increase carefully" |
| `mediaCacheSizeInBytes` | bytes | half of system RAM | 4.0.352 | `@remotion/media` decoded-frame budget and per-source read cache; not a total-memory cap |
| `disallowParallelEncoding` | boolean | false | 3.2.29 | less memory, maybe slower |
| `ffmpegOverride` | `({type:'pre-stitcher'/'stitcher', args}) => args` | | 3.2.22 | discouraged; may be called several times; not on Lambda |
| `onStart` | `({frameCount, parallelEncoding (4.0.52), resolvedConcurrency (4.0.180)})` | | | |
| `onProgress` | `({progress, renderedFrames, encodedFrames, renderedDoneIn, encodedDoneIn, stitchStage:'encoding'/'muxing'})` | | `progress` 3.2.17 | |
| `onDownload` | `(src) => ({percent, downloaded, totalSize}) => void` | | | remote audio/video downloads for the audio mix |
| `onBrowserLog` | `({type, text, stackTrace})` | | | forward page console |
| `onArtifact` | `(artifact)` | | 4.0.176 | for `<Artifact>` |
| `cancelSignal` | from `makeCancelSignal()` | | 3.0.15 | |
| `logLevel` | `trace`/`verbose`/`info`/`warn`/`error` | `info` | 4.0.0 | |
| `binariesDirectory` | path | `node_modules/@remotion/compositor-*` | 4.0.120 | ffmpeg, ffprobe, Rust compositor |
| `forSeamlessAacConcatenation` | boolean | false | 4.0.123 | trims audio to AAC frames (internal, for chunking) |
| `compositionStart` | int | | 4.0.279 | distributed rendering only |
| `repro` | boolean | false | 4.0.88 | writes a reproduction ZIP for bug reports |
| `licenseKey` / `isProduction` | string / boolean (default true) | | 4.0.409 | `isProduction:false` = non-billable dev render |
| `onBrowserDownload` | callback | | 4.0.137 | |

Removed or renamed: `parallelism` (-> `concurrency`, removed v4), `quality` (-> `jpegQuality`), `dumpBrowserLogs` and
`verbose` (-> `logLevel`), `onSlowestFrames` (-> return value), `ffmpegExecutable`/`ffprobeExecutable` (v4 bundles
FFmpeg), `apiKey` (-> `licenseKey`).

Return (v4): `{buffer, slowestFrames: [{frame, time}] (10 slowest), contentType (4.0.426, e.g. "video/mp4")}`.

```ts
const composition = await selectComposition({serveUrl, id: 'Main', inputProps});
const {slowestFrames} = await renderMedia({
  serveUrl, composition, inputProps, codec: 'h264',
  outputLocation: 'out/main.mp4', colorSpace: 'bt709',
  onProgress: ({progress}) => console.log(Math.round(progress * 100) + '%'),
});
```

#### `renderStill()` (since v2.3)
`composition`, `serveUrl`, `output` (absolute path; omit to get `buffer`, 3.3.9), `inputProps`, `frame` (default 0;
negative counts from the end since 3.2.27, `-1` = last), `imageFormat` `png` (default) / `jpeg` / `webp` / `pdf`,
`jpegQuality`, `scale`, `overwrite` (default true), `envVariables` (default `{}`), `timeoutInMilliseconds` (30000),
same browser/cache/license options as `renderMedia()`. Returns `{buffer, contentType (4.0.426)}`. For several stills
in one browser session use `renderFrames({frames: [...]})` (4.0.502).

#### `renderFrames()` (low level; prefer `renderMedia()`)
Required besides `composition`, `serveUrl`, `inputProps`: `onStart(data)`, `onFrameUpdate(framesRendered, frame,
timeToRenderInMilliseconds)` (required per installed types) and `outputDir` (or `null` + `onFrameBuffer(buffer)`,
which may return a Promise for backpressure since 4.0.515). Other options: `imageSequencePattern` (4.0.313,
`[frame]` zero-padded and `[ext]`, default `element-[frame].[ext]`), `frames` (4.0.502: list of frame numbers, any
order, rendered ascending, filename keeps the source number; cannot combine with `frameRange`/`everyNthFrame`, output
cannot go to `stitchFramesToVideo()`), `imageFormat` default `jpeg`. Returns `{frameCount, assetsInfo}`
(`assetsInfo` is internal and unstable).

#### `stitchFramesToVideo()`
Encodes `renderFrames()` output: `fps`, `width`, `height`, `assetsInfo`, `outputLocation` (or buffer), `force`
(overwrite, default true), `pixelFormat` (yuv420p), `codec` (h264), plus the same encoding options as
`renderMedia()`. `muted` must be passed to both `renderFrames()` and here. Returns nothing.

#### `combineChunks()` (4.0.279, advanced; Lambda uses it)
`{outputLocation, videoFiles[], audioFiles[], codec, fps, framesPerChunk (equal except last), preferLossless,
compositionDurationInFrames (the full duration even with frameRange), audioCodec?, frameRange?, everyNthFrame?,
audioBitrate?, numberOfGifLoops?, metadata?, onProgress({totalProgress, frames}), logLevel, binariesDirectory,
cancelSignal}`. Chunk renders must share settings and use `enforceAudioTrack` + `forSeamlessAacConcatenation`.

#### Composition discovery
- `selectComposition({serveUrl, id, inputProps, ...browserOptions})` (4.0.0): evaluates only that composition's
  `calculateMetadata()`; throws if the id does not exist. `inputProps` becomes required in v5.
- `getCompositions({serveUrl, inputProps, ...})`: evaluates `calculateMetadata()` for every composition (slower).
  The options-object form is available from 4.0.497 (so it works on 4.0.528); the legacy positional form
  `getCompositions(serveUrl, {inputProps})` works through v4 and is removed in v5.
- A `VideoConfig` carries `id, width, height, fps, durationInFrames, defaultProps, props` plus render defaults returned
  by `calculateMetadata()`: `defaultCodec, defaultOutName, defaultVideoImageFormat, defaultPixelFormat,
  defaultProResProfile, defaultSampleRate`.

#### Browser management
- `openBrowser('chrome', {logLevel (4.0.189; replaces deprecated shouldDumpIo), browserExecutable, chromiumOptions,
  forceDeviceScaleFactor, onBrowserDownload, chromeMode})`. Reuse the instance across `selectComposition`,
  `renderMedia`, `renderStill`. If you will render with `scale`, set `forceDeviceScaleFactor` at launch.
  Close with `browser.close({silent: true})`.
- `ensureBrowser({chromeMode, browserExecutable, logLevel, onBrowserDownload})` (4.0.137): pre-download Chrome
  Headless Shell; `onBrowserDownload` may return `{version: '149.0.7790.0' | null, onProgress({percent,
  downloadedBytes, totalSizeInBytes})}`. CLI: `npx remotion browser ensure`.

#### Media utilities (absolute local paths only; URLs are not supported)
- `extractAudio({videoSource, audioOutput, logLevel, binariesDirectory})` (4.0.49): copies the audio stream without
  converting; the output extension must match the source audio codec.
- `getSilentParts({src, noiseThresholdInDecibels = -20 (must be < 30), minDurationInSeconds = 1})` (4.0.18) ->
  `{silentParts, audibleParts, durationInSeconds}` with `{startInSeconds, endInSeconds}` items. The docs header says
  `source`, but the installed type (and the docs example) use `src`.
- `getVideoMetadata(path)` (4.0.6, deprecated in favour of Mediabunny): fps, width, height, durationInSeconds, codec,
  `supportsSeeking` (unknown codec: no; under 5 s: yes; non-h264: yes; h264: only if faststart, moov before mdat),
  colorSpace, audioCodec, audioFileExtension, pixelFormat.
- `makeCancelSignal()` (3.0.15) -> `{cancelSignal, cancel}`; a cancelled render rejects with
  "renderMedia() got cancelled".
- Removed in v4 (archival pages): `ensureFfmpeg()`, `ensureFfprobe()`, `getCanExtractFramesFast()`,
  `npx remotion install`. FFmpeg ships inside `@remotion/compositor-*`.

### 3.2 CLI (`@remotion/cli`)

`npx remotion render <entry|serve-url>? <composition-id> <output>`: without an id you get a picker; without an output
the file goes to `out/`. The entry point is auto-detected if omitted.

Render flags (version where the docs give one): `--props` (JSON string or path to a .json file; inline JSON breaks on
Windows shells), `--width`/`--height` (3.2.40), `--fps`/`--duration` (4.0.424), `--concurrency`,
`--pixel-format`, `--image-format`, `--image-sequence-pattern` (4.0.313), `--config`, `--env-file` (default `.env`),
`--jpeg-quality`, `--output`, `--overwrite` (on; `--overwrite=false`), `--sequence` (image sequence, JPEG default),
`--codec`, `--audio-codec`, `--audio-bitrate`, `--video-bitrate`, `--buffer-size`, `--max-rate`,
`--prores-profile`, `--x264-preset`, `--gop` (4.0.466), `--crf`, `--browser-executable`, `--chrome-mode`,
`--scale`, `--frames`, `--every-nth-frame`, `--muted`, `--enforce-audio-track`, `--disallow-parallel-encoding`
(4.0.315), `--number-of-gif-loops`, `--color-space`, `--hardware-acceleration`, `--bundle-cache`
(default true; `=false`), `--log`, `--port`, `--public-dir`, `--timeout` (30000), `--ignore-certificate-errors`,
`--disable-web-security`, `--disable-headless`, `--dark-mode`, `--gl`, `--user-agent`,
`--media-cache-size-in-bytes`, `--offthreadvideo-cache-size-in-bytes`, `--offthreadvideo-video-threads`,
`--enable-multiprocess-on-linux`, `--repro`, `--binaries-directory`, `--rspack` (4.0.502), `--sample-rate`
(4.0.448), `--for-seamless-aac-concatenation`, `--separate-audio-to`, `--metadata key=value` (repeatable).

`--frames` grammar: `--frames=42` (one frame, a still), `--frames=0-99` (range), `--frames=100-` (to the end);
since 4.0.502 `--frames=0,30,60` renders those frames as an image sequence (implies `--sequence`),
`--frames=0-99,150-199` concatenates ranges into one video (inclusive, gaps omitted), mixes like `--frames=0,30-59,90-`
work, and adding `--sequence` outputs the ranges as images.

Other commands:
- `npx remotion still <serve-url|entry>? [id] [output]`: `--image-format` png/jpeg/pdf/webp (png default), `--frame`
  (negative allowed), `--scale`, browser flags. Several stills: `npx remotion render MyComp out/frames
  --frames=0,30,90 --image-format=png`.
- `npx remotion studio <entry>?` (alias `preview`): press `s` in the terminal to reopen (4.0.487). Flags:
  `--props`, `--config`, `--env-file`, `--log`, `--port`, `--public-dir`, `--disable-keyboard-shortcuts`,
  `--disable-interactivity` (4.0.487), `--allow-html-in-canvas` (4.0.447), `--editor` (4.0.503: vscode, cursor,
  windsurf, zed, vscodium, webstorm, sublime-text), `--coding-agent` (4.0.506: codex, cursor, copilot, claude-code),
  `--rspack`, `--webpack-poll <ms>`, `--no-open`, `--browser <path|chrome>` (env `BROWSER`, `BROWSER_ARGS`,
  `BROWSER=none`), `--browser-args`, `--beep-on-finish`, `--ipv4`, `--number-of-shared-audio-tags` (default 0),
  `--experimental-keep-audio-context-alive` (4.0.508), `--preview-sample-rate` (default 48000),
  `--cross-site-isolation` (4.0.364; COOP/COEP headers, needed for `@remotion/whisper-web`; the docs example wrongly
  shows `--enable-cross-site-isolation`), `--disable-ask-ai` (4.0.407), `--force-new` (4.0.421), `--public-license-key`
  (4.0.398; `"free-license"` if eligible).
- `npx remotion compositions <serve-url|entry>?`: lists IDs; `--quiet`/`--q` prints IDs only (space separated).
- `npx remotion bundle` (4.0.89): relocatable by default since 4.0.497; `--out-dir` (default `build/` next to the
  Remotion root), `--public-path` (4.0.127), `--public-dir`, `--disable-git-source` (4.0.182), `--rspack`.
- `npx remotion benchmark src/index.ts Main,Canvas --codec=h264` (3.2.28): `--runs` (default 3), `--concurrencies=2,4,8`;
  inherits render flags.
- `npx create-video --yes --blank my-video` (non-interactive since 4.0.439; needs a template flag and a directory;
  installs Tailwind unless `--no-tailwind`; does not install agent skills or open an editor; fails inside an existing
  git repo); `--tmp` (4.0.214); `--help`/`-h` (4.0.488).
- `npx remotion add <pkgs...>` installs `@remotion/*` (and zod, mediabunny, `@huggingface/transformers`) at the
  project's Remotion version; `--package-manager` (4.0.367); extra args forwarded.
- `npx remotion upgrade` (all Remotion packages + recommended aux versions + `.agents/skills`), `--version <v>`
  (4.0.15, also downgrades), `--skip-skills` (4.0.503), `--package-manager` (npm, yarn, pnpm, bun, nub). Do not use
  `npm update`.
- `npx remotion versions`: checks that all Remotion packages share one version.
- `npx remotion skills add | update`: installs `remotion-dev/skills` into `.agents/skills` (symlinked from
  `.claude/skills`).
- `npx remotion ffmpeg ...` / `npx remotion ffprobe ...` (4.0): bundled 7.1 binaries that only know H.264, H.265,
  VP8, VP9 and ProRes.
- `npx remotion gpu --gl=angle` (4.0.52): prints Chrome's GPU feature status (not for parsing).
- `npx remotion browser ensure`, `npx remotion help`.

`remotion.config.ts` methods that appear in this material (import `{Config}` from `@remotion/cli/config`; restart the
Studio after changes): `setRspack(true)`, `setVideoImageFormat('jpeg' | 'png')`, `setOverwriteOutput(true)`,
`setCodec`, `setPixelFormat`, `setProResProfile`, `setChromiumOpenGlRenderer` (read by `npx remotion gpu` too),
`setKeyboardShortcuts({...})`, `setKeyboardShortcutsEnabled(false)`, `setDefaultEditor(...)`,
`setBufferStateDelayInMilliseconds(ms)`, `setAllowHtmlInCanvasEnabled(true)`, `addElementLibrary({...})` (written by
the Studio protocol). Doc-link anchors also name `setDefaultCodingAgent`, `setEnableCrossSiteIsolation`,
`setAskAiEnabled`, `setInteractivityEnabled`, `setNumberOfSharedAudioTags`, `setPreviewSampleRate`,
`setExperimentalKeepAudioContextAlive`, `setForceNewStudioEnabled`, `setBeepOnFinish` (exact casing: check the config
page owned by another agent).

### 3.3 Encoding matrix (docs + installed code)

**Codecs** (installed `validCodecs`): `h264` (default), `h265`, `vp8`, `vp9`, `av1`, `prores`, `h264-mkv`, `h264-ts`,
`gif`, `mp3`, `aac`, `wav`. The CLI page still lists `png` as a codec; that is outdated (use `--sequence` or
`--frames` lists for PNG sequences). `av1` is unavailable on Linux ARM64 GNU.

| Codec | Default ext (other) | Audio allowed (default first) | CRF range / default | Parallel encoding | Even dims forced | HW encoder |
|---|---|---|---|---|---|---|
| h264 | mp4 (mkv, mov) | aac, mp3, pcm-16 (pcm -> mkv) | 1-51 / 18 (0 rejected) | yes | yes | macOS `h264_videotoolbox`, Linux/Win `h264_nvenc` |
| h265 | mp4 (mkv, hevc) | aac, pcm-16 | 0-51 / 23 | yes | yes | `hevc_videotoolbox` / `hevc_nvenc` |
| av1 | mp4 (webm with opus, mkv) | aac, opus, pcm-16 | 0-63 / 30 | no | yes | none (libaom, "significantly slower") |
| vp8 | webm (mkv with pcm) | opus, pcm-16 | 4-63 / 9 | no | no | none |
| vp9 | webm (mkv with pcm) | opus, pcm-16 | 0-63 / 28 | no | no | none |
| prores | mov (mkv, mxf) | pcm-16, aac | no CRF | no | no | macOS `prores_videotoolbox` |
| h264-mkv | mkv | pcm-16, mp3 | 1-51 / 18 | yes | yes | none (`required` throws) |
| h264-ts | ts | aac, pcm-16 | 1-51 / 18 | no | yes | none (`required` throws) |
| gif | gif | none | no CRF | no | no | none |
| mp3 / aac / wav | mp3 / aac (m4a, 3gp, m4b, mpg, mpeg) / wav | mp3 / aac / pcm-16 (+ pcm-16 -> wav) | none | no | n/a | n/a |

- Audio codec to FFmpeg encoder: aac -> `libfdk_aac`, mp3 -> `libmp3lame`, opus -> `libopus`, pcm-16 -> `pcm_s16le`.
  `preferLossless: true` picks pcm-16 for every codec (an explicit `audioCodec` wins).
- **Pixel formats** (installed `validPixelFormats`): `yuv420p` (default), `yuva420p` (alpha; vp8/vp9 only), `yuv422p`,
  `yuv444p`, `yuv420p10le`, `yuv422p10le`, `yuv444p10le`, `yuva444p10le` (alpha; use with ProRes 4444). Any `yuva*`
  format requires `imageFormat: 'png'`.
- **Transparency recipes** (official skill + docs): ProRes for editing software:
  `--image-format=png --pixel-format=yuva444p10le --codec=prores --prores-profile=4444` (.mov). WebM for browsers:
  `--image-format=png --pixel-format=yuva420p --codec=vp9` (or vp8) (.webm). The composition must not paint an opaque
  background.
- **Color space**: v4 accepts `default`, `bt601` (identical to `default` since 4.0.424), `bt709` (4.0.28), `bt2020-ncl`
  (4.0.88). The option text also lists `bt2020-cl`, but the installed v4 validator does not accept it. Real color
  conversion happens since 4.0.83 (before it only tagged metadata). Docs: use `png` frames for the most accurate color.
  v5 will default to `bt709`. What the installed `ffmpeg-args.js` actually does: `default`/`bt601` add no color tags
  at all (players must guess); `bt709` adds `-colorspace/-color_primaries/-color_trc bt709`, `-color_range tv` and a
  `zscale` filter to limited-range BT.709; `bt2020-ncl` tags BT.2020 with the `arib-std-b67` (HLG) transfer; GIF is
  always bt601. This is the strongest reason to pass `bt709` for every video deliverable.
- **Container details (installed code)**: every encode uses `-video_track_timescale 90000`; `.mp4` and `.mov` outputs
  are finalised with `-movflags faststart` (moov atom first, seekable in browsers). `yuva420p` automatically adds
  `-auto-alt-ref 0` for VP8/VP9 alpha.
- **CRF semantics**: lower = better and bigger. **x264 presets**: ultrafast, superfast, veryfast, faster, fast, medium
  (default), slow, slower, veryslow, placebo (the docs list starts at superfast; the installed validator also accepts
  ultrafast).
- **Hardware acceleration** (`disable` default): with `if-possible`, Remotion silently falls back to software (with a
  warning) when `crf`, `bufferSize` or `maxRate` are set; with `required` those options throw. Quality then comes from
  `videoBitrate`.
- **Image formats**: video frames `jpeg` (default, fastest, no alpha) / `png` / `none`; stills `png` (default) /
  `jpeg` / `webp` / `pdf`.
- **GL backends** (`--gl`, `chromiumOptions.gl`): `angle`, `egl`, `swiftshader`, `swangle`, `vulkan` (4.0.41),
  `angle-egl` (4.0.51). Default `null` (Chrome decides), except Lambda (`swangle`); v5 plans `angle` with SwiftShader
  fallback. Historical note in the option text: `angle` once had a small memory leak that could crash very long
  renders (2.4.3 to 2.6.6). Check with `npx remotion gpu`.
- **Concurrency**: see 3.1; `"50%"` = floor(0.5 x cpus).
- **Log levels**: `trace`, `verbose`, `info` (default), `warn`, `error`. `--log=verbose` shows whether parallel encoding
  is on, cache sizes, and even-dimension rounding.

### 3.4 Remotion Studio: features an agent can use

**Starting it**: `npx remotion studio --no-open` (agent friendly; if a Studio already runs for this project and port it
prints the URL and exits; `--force-new` starts another). Press `s` in the terminal to reopen the browser tab.

**Interactivity (4.0.475)**: visual edits written back to source; undo `Cmd/Ctrl+Z`, redo `Cmd/Ctrl+Y` (shortcut table
lists `Cmd/Ctrl+Shift+Z`, and `Ctrl+Y` outside macOS).
- Select sequences, sequence props, effects, effect props, keyframes and easing segments; Shift = range, Cmd/Ctrl =
  toggle, drag on the timeline = marquee, `Cmd/Ctrl+A` = all rows.
- Canvas: drag outlines -> `style.translate`; Shift locks an axis; edges -> `style.scale`; corners -> `style.rotate`;
  transform-origin handle (translate is compensated). Dragging a keyframed value creates/updates a keyframe at the
  current frame.
- Effects: drop onto outlined sequences, drag UV handles, copy/paste effects and single effect values.
- Keyframes: drag horizontally, multi-move, delete. Easing segments: context menu Linear / presets / custom editor.
- Editable easings (must be inline in `interpolate()` / `interpolateColors()`): `Easing.linear`, `Easing.step1`
  (4.0.509), `Easing.bezier(numbers)`, `Easing.spring({static config})`, and since 4.0.487 `Easing.ease`, `quad`,
  `cubic`, `back()`, `back(n)`, `poly(1..3)` (written back as `Easing.bezier(...)`), `Easing.in(supported)`,
  `Easing.out(bezier or linear)`, `Easing.inOut(Easing.linear)`. `sin`, `circle`, `exp`, `bounce`, `elastic`,
  `poly(4)` and non-linear `inOut` are shown read-only.
- Delete/Backspace deletes or resets to defaults; `Cmd/Ctrl+D` duplicates sequences; `Cmd/Ctrl+Shift+D` splits at the
  playhead (4.0.527).
- `--disable-interactivity` (config anchor `setinteractivityenabled` per the option's doc link) keeps preview and
  source navigation but disables outlines, the sequence inspector, visual controls, timeline selection and editing.

**Code rules that keep things editable** (interactivity best practices):
- Use `Interactive.Div` (any HTML/SVG element: `Interactive.Svg`, `Interactive.Path`, ...) with a hardcoded `name`.
  `<Img name>` and `@remotion/media` `<Video name>` are interactive already.
- `style` = one inline object literal: no constants, no spread, no arithmetic, no memoised style objects.
- Animate with inline `interpolate(frame, [in], [out], {easing, output, extrapolateLeft, extrapolateRight})` on the
  property itself. Output range, easing, extrapolation and `output` must be literals. The input range may use
  `fps`, `durationInFrames`, `width`, `height` destructured from `useVideoConfig()`, `2 * fps`, `fps * 2`,
  `durationInFrames - 1`. Only the `frame` variable is understood as input.
- Prefer the individual `scale`, `rotate`, `translate` CSS properties over `transform`.
- Keep `<Composition>` / `<Still>` `width`, `height`, `fps`, `durationInFrames`, `defaultProps` inline, no `as Props`
  casts, no extracted `defaultProps` constant; use `calculateMetadata()` only for truly dynamic metadata. Since 4.0.516
  the Props editor infers basic controls from inline `defaultProps` (no Zod schema needed).
- Effects arrays inline with a stable shape; no conditional arrays; render two elements instead.

```tsx
const {fps} = useVideoConfig();
<Interactive.Div name="Headline" style={{fontSize: 96, color: 'white',
  translate: interpolate(frame, [0, fps], ['0px 80px', '0px 0px'],
    {easing: Easing.bezier(0.2, 0, 0, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}),
  opacity: interpolate(frame, [0, 0.5 * fps], [0, 1], {extrapolateRight: 'clamp'})}}>
  Launch day
</Interactive.Div>
```
(`0.5 * fps` is my extrapolation of the "number times fps" rule; the docs show `2 * fps` / `1 * fps`.)

**Make a custom component interactive (4.0.479)**: `Interactive.withSchema({Component, componentName: '<Badge>',
schema, supportsEffects})`. The schema (`InteractivitySchema`, e.g. `{color: {type: 'color', default: '#0b84ff',
description: 'Color'}, padding: {type: 'number', min: 0, step: 1, default: 16, description, hiddenFromList}}`) should
always spread `Interactive.baseSchema` (from, trimBefore, playbackRate, durationInFrames, freeze, hidden, name,
showInTimeline); add `Interactive.transformSchema` if the component applies `style`, `Interactive.cropSchema`
(4.0.500, with `InteractiveCropProps`), `Interactive.premountSchema` (premountFor/postmountFor),
`Interactive.captionsSchema` (4.0.500; caption text editable only when passed as a direct JSX array literal). The inner
component receives `controls`: forward it unchanged to its `<Sequence controls={controls}>`; with
`<Sequence layout="none">` pass `outlineRef` so the Studio can draw the outline. Do not expose `controls` publicly.

**`@remotion/studio` functions** (Studio only unless noted; install with `npx remotion add @remotion/studio`):

| API | Since | Signature / behavior |
|---|---|---|
| `getStaticFiles()` | 4.0.144 | `[{name, src, sizeInBytes, lastModified}]`; use `src` or `staticFile(name)`; prefix in `src` changes on restart; first 10000 files; empty array in Player and plain Node; works in SSR |
| `watchPublicFolder(cb)` | 4.0.154 | `cb(StaticFile[])`, returns `{cancel}` |
| `watchStaticFile(name, cb)` | 4.0.144 | `cb(StaticFile | null)` (null = deleted), returns `{cancel}` |
| `writeStaticFile({filePath, contents})` | 4.0.147 | string or ArrayBuffer into `public/`; forward slashes; cannot escape `public/` |
| `deleteStaticFile(path)` | 4.0.154 | returns `{existed}` |
| `saveDefaultProps({compositionId, defaultProps: ({schema, savedDefaultProps}) => props})` | 4.0.147 | writes Root file; needs a running (non-static) Studio and `zod`; since 4.0.437 all edits save immediately (`unsavedDefaultProps` equals saved) |
| `updateDefaultProps()` | 4.0.154 | deprecated alias |
| `restartStudio()` | 4.0.162 | new CLI process on same port (package upgrades apply) |
| `shutDownStudio()` | 4.0.521 | writable Studio with server only |
| `play(e?)`, `pause()`, `toggle(e?)` | 4.0.287 | pass the click event for audio autoplay |
| `seek(frame)` | 4.0.259 | clamped to `0 .. durationInFrames-1` |
| `goToComposition(id)` | 4.0.287 | throws if missing |
| `focusDefaultPropsPath({path: ['items', 0, 'title'], scrollBehavior})` | 4.0.165 | scrolls the props editor |
| `reevaluateComposition()` | 4.0.167 | re-runs `calculateMetadata()` (public folder, network, randomness, time) |
| `visualControl(name, default, zodSchema?)` | 4.0.292 | deprecated in favour of interactivity; name must be a static string; returns the original value outside Studio |

**Keyboard shortcuts** (defaults, customizable since 4.0.523 via `Config.setKeyboardShortcuts({playPause: {key: 'q'},
quickSwitcher: {key: 'p', commandOrControl: true}, render: null})`): Space play/pause, M mute, Shift+L loop, A start,
E end, J/K/L reverse/pause/forward (repeat L = faster), G go to frame, Enter pause and return, Cmd+B/J/G sidebars,
F fullscreen, Shift+O outlines, Shift+R rulers and guides, Shift+M snapping, PageUp/PageDown previous/next
composition, `?` shortcuts, Cmd+K quick switcher (`>` menu items, `?` docs search), R render dialog, T checkerboard
(transparency check), I/O/X in, out, clear points, `+`/`-`/`0` zoom, P/T/R/S select translate/opacity/rotate/scale
prop, Cmd+D duplicate, Cmd+Shift+D split, Cmd+C/X/V effects and values, Cmd+I Ask AI, Shift+C color picker (4.0.525).
Arrows = 1 frame or nudge, Shift+arrows = 1 second.

**Open in editor (4.0.503)**: `Config.setDefaultEditor('cursor')` (vscode, cursor, windsurf, zed, vscodium, webstorm,
sublime-text) or a custom `{type: 'custom', name, executable, arguments: ['--goto',
'%TARGET_PATH%:%LINE_NUMBER%:%COLUMN_NUMBER%']}`; `--editor` wins.

**Deploying the Studio**:
- VPS/Docker (4.0.46): `node:22-bookworm-slim` + Chrome libs (libnss3, libdbus-1-3, libatk1.0-0, libgbm-dev,
  libasound2, libxrandr2, libxkbcommon-dev, libxfixes3, libxcomposite1, libxdamage1, libatk-bridge2.0-0,
  libpango-1.0-0, libcairo2, libcups2), `npm i`, `npx remotion browser ensure`, `CMD npx remotion studio`, port 3000.
  Fly.io needs `--ipv4` and >= performance-2x (2 CPU, 4 GB); Render.com Standard (2 GB)+; DigitalOcean App Platform
  fails (its proxy blocks server-sent events), a plain droplet works.
- Static (4.0.97): `npx remotion bundle` -> `build/`; host on Vercel (`bunx remotion bundle`), Netlify, GitHub Pages
  (before 4.0.497 add `--public-path="./"`). No SSR in a static Studio (client-side rendering can work); the URL is a
  valid serve URL for `npx remotion render <url> <id>`, `renderMedia()`, Lambda and Cloud Run. The read-only Studio's
  render modal has "Copy command".
- remotion.dev/new: a browser-only Studio (virtual FS, Rspack in the browser): add solids, effects, media, captures,
  elements, keyframes, packages, transcription, video matting, download the project; cannot edit code, run an agent
  or save. Free to use; downloaded projects fall under the Remotion License.

### 3.5 Studio protocol (`@remotion/studio-protocol`): delivering Elements into a user's Studio

- `createElementPayload({displayName (< 120 chars), slug (lowercase; last segment names the .element.tsx file),
  sourceCode (exactly one named exported component), dependencies: [{name, version}] (@remotion/* -> version null;
  others exact semver; never react/react-dom/remotion), dimensions: {width, height} | null, durationInFrames (int),
  initialProps? (4.0.524), installationMode? ('wrapped' default: Studio adds a <Sequence>; or
  'component-owned-sequence' (4.0.506)), assets? (4.0.528: [{path, type: 'url', url} | {path, type: 'base64',
  data}], max 100 assets, 50 MB total, payload max 250,000 JSON characters)})` (4.0.502) -> versioned payload
  (v1, or v2 with assets); throws `TypeError` on invalid input.
- `staticFileRef('my-element/logo.png')` (4.0.528) inside `initialProps`: Studio downloads the asset to `public/` and
  writes `staticFile('...')` on the invocation. Give the Player preview the plain hosted URL instead.
- `installInStudio({payload})` (4.0.502): probes local ports 3000 to 3009 (or the containing Studio) and targets the
  most recently focused one; success = `{status: 'awaiting-confirmation', target}`; failure codes include
  `no-compatible-studio`, `studio-upgrade-required`, `loopback-network-permission-denied` (4.0.521),
  `request-timed-out`, `network-error`.
- `setStudioDragData({dataTransfer, payload})` (4.0.502): drag-and-drop from a website (labelled "unverified").
- `addElementLibraryToStudio({url, displayName?})` (4.0.518): after confirmation persists
  `Config.addElementLibrary()` in `remotion.config.ts` (`no-config-file` if none).
- `isInsideStudio()` (4.0.518): UI hint only. `buildOpenInRemotionNewUrl({payload})` (4.0.527): link to remotion.dev/new.
- Security: HTTPS origins only (HTTP only for localhost/127.0.0.1); every install shows a confirmation with source,
  code and packages; dependency lifecycle scripts are disabled.
- Recommended library pattern: show the component in `<Player>` with the same size/duration as the payload, and get
  the source string with Vite `import src from './X.tsx?raw'`.

### 3.6 `@remotion/player`

`npx remotion add @remotion/player`. `<Player component={C} | lazyComponent={useCallback(() => import('./C'), [])}
durationInFrames fps compositionWidth compositionHeight inputProps />` (never wrap in `<Composition>`).

Props (default; since): `loop` (false), `autoPlay` (false; avoid with audio), `controls` (false), `showVolumeControls`
(true), `allowFullscreen` (true), `clickToPlay` (true if controls), `doubleClickToFullscreen` (false; delays pause by
200 ms), `spaceKeyToPlayOrPause` (true), `moveToBeginningWhenEnded` (true; 3.1.3), `style`, `className`, `initialFrame`
(0; fixed after mount; 3.1.14), `numberOfSharedAudioTags` (5 in v4, 0 in v5; fixed), `sampleRate` (48000; fixed;
4.0.470), `playbackRate` (-10..10, not 0; media cannot play in reverse), `errorFallback({error})`,
`renderLoading({width, height})`, `renderPoster({width, height, isBuffering})` + `showPosterWhenUnplayed` /
`Paused` / `Ended` (3.2.14) / `Buffering` (4.0.111) / `BufferingAndPaused` (4.0.290), `inFrame`/`outFrame` (3.2.15),
`initiallyShowControls` (true or ms), `initiallyMuted` (3.3.81), `renderPlayPauseButton({playing, isBuffering})`,
`renderFullscreenButton({isFullscreen})`, `renderMuteButton({muted, volume})` (4.0.188),
`renderVolumeSlider({isVertical, volume, onBlur, inputRef, setVolume})` (4.0.188), `renderCustomControls()` (4.0.418),
`alwaysShowControls` (false), `hideControlsWhenPointerDoesntMove` (true / 3000 ms), `showPlaybackRateControl` (true =
[0.5, 0.8, 1, 1.2, 1.5, 1.8, 2, 2.5, 3] or an array), `posterFillMode` ('player-size' | 'composition-size'),
`bufferStateDelayInMilliseconds` (300), `overflowVisible` (4.0.173), `browserMediaControlsBehavior` ({mode:
'prevent-media-session' default | 'register-media-session' | 'do-nothing'}; 4.0.221), `overrideInternalClassName`,
`logLevel` ('trace' logs media mounting, seeking, buffering; 4.0.250), `noSuspense` (tests; 4.0.271),
`acknowledgeRemotionLicense` (4.0.253), `volumePersistenceKey` ("remotion.volumePreference"; 4.0.305),
`initialVolume` (0..1, disables localStorage; 4.0.453), `_experimentalKeepAudioContextAlive` (4.0.508, editors).

`PlayerRef`: `play(e?)`, `pause()`, `toggle(e?)`, `pauseAndReturnToPlayStart()` (4.0.67), `seekTo(frame)`,
`getCurrentFrame()`, `isPlaying()`, `mute()`, `unmute()`, `isMuted()`, `getVolume()`, `setVolume(0..1)`,
`requestFullscreen()` (throws if disallowed/unsupported; no iOS Safari), `exitFullscreen()`, `isFullscreen()`,
`getScale()`, `getContainerNode()`, `addEventListener` / `removeEventListener`.
Events (`CallbackListener<'x'>`, payload in `e.detail`): `play`, `pause`, `ended`, `seeked` {frame} (seeking only),
`timeupdate` {frame} (at most every 250 ms while playing), `frameupdate` {frame} (every frame, playing and seeking),
`ratechange`, `volumechange`, `mutechange`, `scalechange`, `fullscreenchange`, `error` {error}, `waiting` / `resume`
(buffering, 4.0.111). Render errors are caught by an error boundary (remount via `key`); async errors are not.

`<Thumbnail>` (3.2.41): one frame (`frameToDisplay`) of a component; same sizing props plus `durationInFrames`,
`fps`, `inputProps`, `errorFallback`, `renderLoading`, `overflowVisible`, `logLevel`, `noSuspense`;
`ThumbnailRef` has `getContainerNode()`, `getScale()`, `error`/`waiting`/`resume` events.

Sizing: default = composition size; `style={{width: '100%'}}` keeps the aspect ratio; to fit a box use an absolutely
positioned wrapper with `aspectRatio: W / H`, `maxWidth/maxHeight: '100%'`, `margin: 'auto'`, Player width 100%.

Buffer state (4.0.111): `@remotion/media` `<Video>`/`<Audio>` buffer by default; add `pauseWhenBuffering` to
`<Html5Video>`, `<Html5Audio>`, `<OffthreadVideo>` and `pauseWhenLoading` to `<Img>`. Custom:
`const h = useBufferState().delayPlayback(); ... h.unblock()` inside `useEffect` with cleanup. It is independent from
`delayRender()` (which only affects rendering); use both when loading data.

Premounting (4.0.140): mount early (opacity 0, pointer-events none, frame frozen at the start) so media can load. v4
`premountFor` defaults to 0 (opt in); v5 defaults to `fps`. Available on `<Sequence>`, `Series.Sequence`,
`TransitionSeries.Sequence`, `@remotion/media` `<Video>`/`<Audio>` (4.0.495, display none), and since 4.0.528 on
`<AbsoluteFill>`, `Interactive.*`, `<HtmlInCanvas>`, `<Solid>`, shapes, `<MacOSCursor>`, rough-notation, `<Lottie>`,
`<RemotionRiveCanvas>`, `<ThreeCanvas>`, `<ThreeWebGPUCanvas>` (plus `<Img>`, `<AnimatedImage>`, `<Gif>`).
`styleWhilePremounted` overrides the hiding style. Not possible with `<Sequence layout="none">`. Only Player/Studio.

Media keys (4.0.221): Studio registers the Media Session; the Player prevents it by default. With several Players, let
only one use `register-media-session`.

### 3.7 `@remotion/preload` and `prefetch()`

- `preloadVideo(url)`, `preloadAudio(url)` (hidden `<video|audio preload="auto">`, or `<link rel=preload>` on Firefox),
  `preloadImage(url)`, `preloadFont(url)` each return an un-preload function. Video/audio preloading affects only
  HTML5 elements (`<Html5Video>`, `<Html5Audio>`, `<OffthreadVideo>` in preview), not `@remotion/media`.
- `resolveRedirect(url)` follows redirects (needs CORS, else throws); resolve at module load, fall back to the
  original URL, then preload.
- `prefetch(url)` (in `remotion`, 3.2.23): downloads fully into a blob URL that media components with the same `src`
  use automatically; `{free, waitUntilDone}`; reliable but needs CORS and full download; not recommended in most cases
  and never while the Player is already mounted.

### 3.8 `@remotion/browser-bundler` (4.0.527, Draft API, Chrome only, needs cross-origin isolation)

- `createBrowserBundler({dependencyVersions?, enableFastRefresh? = false, onProgress?({asset: 'rspack-wasm',
  loadedBytes, totalBytes}), workerUrl?})` -> `{bundle({project}), dispose()}`. `project` = `{entryPoint:
  'src/index.ts', files: {'src/Root.tsx': '...'}}` (complete snapshot each call; no binary or `public/` files).
  Unpinned npm imports resolve to latest on esm.sh; React/ReactDOM/Remotion are shared with the host. Errors:
  `BrowserBundlerError.diagnostics`.
- From `@remotion/browser-bundler/runtime`: `loadBrowserBundle({bundle})` -> root FC (entry must call
  `registerRoot()` synchronously once; evaluated with `Function`, CSP must allow eval; trusted code only);
  `getBrowserComposition({root, compositionId, inputProps, signal?})` -> `{component, props, width, height, fps,
  durationInFrames, default*}` for a `<Player>`; `createBrowserBundleRuntime()` (Fast Refresh: dev React,
  `react-refresh@0.18.0`, isolated iframe, apply every bundle in order) and `createBrowserCompositionObserver({onChange,
  onError})` (keeps the Player component stable across edits).
- JSX source locations for editors: 4.0.529 (not on 4.0.528). Package is not installed in `remotion-broll`.

### 3.9 Client-side rendering (`@remotion/web-renderer`, since 4.0.397)

`renderMediaOnWeb({composition: {id, component, durationInFrames, fps, width, height, defaultProps?,
calculateMetadata?}, inputProps?, container? ('mp4'), videoCodec? (mp4 -> h264, webm -> vp8), audioCodec?
(mp4 -> aac, webm -> opus), frameRange? (number, [a,b], [a,null]; no multi-range), scale?, videoBitrate? /
audioBitrate? (bps or 'very-low'|'low'|'medium' (default)|'high'|'very-high'), hardwareAcceleration?
('no-preference'|'prefer-hardware'|'prefer-software'), keyframeIntervalInSeconds? (5), transparent? (false; webm or
mkv + vp8/vp9 only), muted?, sampleRate? (48000; 4.0.448), metadata? (4.0.517, Mediabunny tags; "Made with Remotion
<version>" is prepended to comment), pageResponsiveness? ('disabled'|'low' 100 ms|'medium' 33 ms (default)|'high'
16 ms|number; 4.0.487), delayRenderTimeoutInMilliseconds? (30000), onProgress?({progress, encodedFrames,
renderEstimatedTime, doneIn}), onFrame?(VideoFrame => VideoFrame), outputTarget? ('web-fs' OPFS or 'arraybuffer';
auto), outputWritable? (WritableStream, e.g. `showSaveFilePicker().createWritable()`; 4.0.508), signal?, schema? (Zod
v4), licenseKey?, isProduction?, allowHtmlInCanvas? (false; 4.0.447), mediaCacheSizeInBytes?, onArtifact?, logLevel?})`
-> `{getBlob()}` (rejects when `outputWritable` is used).

`renderStillOnWeb({composition, frame, ...})` -> `{canvas(), blob({format: 'png'|'jpeg'|'webp', quality}), url()}`.
`canRenderMediaOnWeb({width, height, container, videoCodec, audioCodec, transparent, muted, bitrates, outputTarget})`
-> `{canRender, issues[{type, message, severity}], resolvedVideoCodec, resolvedAudioCodec, resolvedOutputTarget}`;
issue types: `webcodecs-unavailable`, `container-codec-mismatch`, `invalid-dimensions` (H.264/H.265 need even
sizes), `video-codec-unsupported`, `audio-codec-unsupported`, `transparent-video-unsupported`, `webgl-unsupported`
(3D CSS transforms), `output-target-unsupported`. `getEncodableVideoCodecs(container)` / `getEncodableAudioCodecs(...)`
list what the browser can encode. Installed 4.0.528 unions are wider than the docs: containers mp4, webm, mkv, mov,
wav, mp3, aac, ogg, flac; audio codecs aac, opus, mp3, vorbis, pcm-s16, flac; video codecs h264, h265, vp8, vp9, av1.

How it works: mounts the component off-screen; per frame walks the DOM, neutralises transforms up the tree,
measures with `getBoundingClientRect()`, draws `<img>`/`<svg>`/`<canvas>`/`<video>` natively and other boxes with
Canvas 2D (text re-laid out word by word via `Intl.Segmenter`), mixes `@remotion/media` audio, encodes with
Mediabunny. Supported and unsupported CSS: section 5. HTML-in-canvas capture (`allowHtmlInCanvas`, needs
`chrome://flags/#canvas-draw-element`) takes true screenshots instead and falls back automatically.

Migration rules: `useRemotionEnvironment()` instead of `getRemotionEnvironment()`, `useDelayRender()` instead of
`delayRender()`/`continueRender()`/`cancelRender()`, CORS-enabled assets, only `@remotion/media` `<Video>`/`<Audio>`,
no `getInputProps()`. Cancellation via `AbortController`; check `signal.aborted` in `catch`.

### 3.10 `<HtmlInCanvas>` (in `remotion`, 4.0.455)

Renders children into a canvas via the WICG HTML-in-canvas API so you can post-process real DOM with Canvas 2D, WebGL2
or WebGPU. Needs Chrome 149+ with `chrome://flags/#canvas-draw-element`; `HtmlInCanvas.isSupported()` (Chrome 147's
buggy build counts as unsupported); unsupported browsers get a fatal error.
Props: `width`, `height` (positive ints), `pixelDensity` (1; 4.0.472; pass `usePixelDensity()` to follow render
`scale`), `effects` (4.0.464; applied after `onPaint`), `onPaint({canvas: OffscreenCanvas, element, elementImage,
pixelDensity})` (default paints with 2D; may be async and holds the frame via `delayRender()`), `onInit(...)` (create
GL/GPU resources once; must return a cleanup), `cropLeft/Right/Top/Bottom` (0..1; 4.0.500), inherited Sequence props
`from`, `durationInFrames`, `trimBefore` (4.0.482), `playbackRate`, `premountFor`, `postmountFor`,
`styleWhilePremounted`, `styleWhilePostmounted` (4.0.528), `ref` (HTMLCanvasElement). 2D: `ctx.reset();
ctx.filter = ...; const t = ctx.drawElementImage(elementImage, 0, 0); element.style.transform = t.toString()`.
WebGL2: `gl.texElementImage2D(...)`. WebGPU: `device.queue.copyElementImageToTexture(...)`. Never nest two
`<HtmlInCanvas>`. If WebGL2 is unavailable while rendering, try `--gl=angle`.

### 3.11 `@remotion/codemods` (4.0.528 unless noted; Draft API; installed in `remotion-broll`)

Model: `CodemodProject = {rootDir: string, files: Record<path, source>}`; results carry `changes:
[{filePath, previousContents | null (new file), nextContents | null (deleted)}]`; node addressing via
`JsxNodeReference = {filePath, nodePath}` and `EffectReference = {...node, effectIndex}`; node-editing results also
return `nodePathRemappings: [{filePath, oldNodePath | null, newNodePath | null}]` (apply them to any references you
hold). The input project is never mutated; failed edits leave it unchanged. Nothing is installed, downloaded or
executed.

| Group | Functions |
|---|---|
| Apply / undo | `applyCodemodChanges(project, changes)` (throws if a file's current contents differ from `previousContents` or a file appears twice; undo = swap previous/next) |
| Inspect | `getJsxNodes({project, filePath})` -> `[{filePath, nodePath, tagName, componentIdentity, location}]`; `getJsxNodeProps({project, node, keys: ['children', 'style.opacity'], effectKeys?, assetKeys?, componentIdentity?, videoConfig?})` -> props with `status: 'static' | 'keyframed' | 'computed'` and effect descriptions; `resolveCompositionComponent({project, compositionFile, compositionId})` -> `{filePath, exportName, location, canAddContent}` |
| Registration tree | `addComposition({compositionFile, compositionId, component: {importName, importPath}, metadata, folder?})`, `addCanvasCaptureComposition(...)` (creates component + registration from a screen capture + cursor data; needs `@remotion/media` and `@remotion/mac-cursors`), `duplicateComposition({newId, metadata?, tag?})`, `renameComposition`, `deleteComposition`, `moveComposition({destination})`, `updateCompositionMetadata({metadata})` (does not touch `calculateMetadata()`), `setCompositionDefaultProps({defaultProps, enumPaths?})` (replaces, not merges), `addFolder`, `renameFolder`, `moveFolder`, `unwrapFolder` |
| Content | `addSolid({width, height, from?, position?})` (4.0.527), `addMedia({type: image|video|audio|gif|animated-image, src, srcType: static|remote, dimensions?, from?, durationInFrames?, position?})`, `addComponent({importName, importPath, props, from?, durationInFrames?, position?})`, `deleteJsxNodes({nodes})` (4.0.527), `duplicateJsxNodes`, `reorderJsxNode({node, target, position: before|after})` (stacking order), `splitSequences({splits: [{node, frame}]})` (adjusts from/durationInFrames/trimBefore), `detachAudio({node})` (mutes video, adds matching audio element) |
| Props and keyframes | `updateJsxNodeProps({node, props: {'style.opacity': 0.5, children: 'Text'}} or updates[] with defaultValue, googleFont, clipboardParam)`, `updateMultipleJsxNodeProps({changes})`, `updateJsxNodeKeyframes({node, updates: [{key, operation}]})` with operations `add {frame, value}`, `remove {frame, valueWhenLastKeyframeDeleted}`, `move {moves}`, `easing {segmentIndex, easing}`, `settings {clamping, posterize, output}` |
| Effects | `addEffect({node, importName, importPath (@remotion/effects/*, @remotion/light-leaks, @remotion/starburst), props})`, `updateEffectProps`, `updateEffectKeyframes`, `deleteEffects` (`effectIndex: null` removes all), `duplicateEffects`, `reorderEffect({effect, toIndex})` |
| Legacy | `updateVisualControls({filePath, changes: [{id, newValueSerialized, newValueIsUndefined, enumPaths}]})` |

Undocumented exports also present: `wrapJsxNode`, `canWrapJsxNode`. Codemods reject computed values, spreads that
may override a prop, dynamic timing, conditional/computed effect arrays: the same static-code rules as Studio
interactivity.

### 3.12 Licensing (`@remotion/licensing`) and license facts

- `registerUsageEvent({licenseKey: 'rm_pub_...', event: 'web-render' | 'cloud-render', host, succeeded})` ->
  `{billable, classification: 'billable' | 'development' | 'failed'}`; localhost hosts and failed events are free.
- `getUsage({licenseKey: 'rm_sec_...' (backend only), since?})` -> `{webRenders, cloudRenders}` each `{billable,
  development, failed}` (since defaults to month start UTC, max 90 days back; `webRenders` since 4.0.428).
- Render APIs accept `licenseKey` + `isProduction` (4.0.409); Studio accepts `--public-license-key`.
- Free License: individuals, organisations up to 3 people, non-profits, evaluation. Company License: "Creators"
  $25/month per person writing Remotion code (including via agents) or "Automators" $0.01 per render, $100/month
  minimum; Enterprise $500/month minimum. Automation = owning code that calls `renderMedia`, `renderStill`,
  `renderFrames`, Lambda/Cloud Run/Vercel/web render functions, `npx remotion render|still`, or embedding `<Player>`.
  A render = one successful video, audio, GIF, still or PDF; Studio and Player previews do not count.
- Agencies: if only finished files are delivered, only the agency headcount counts (Free up to 3 people); if the
  client owns or operates the project, headcounts aggregate and the IP owner buys the license. LLM-generated-code
  services are allowed; letting users upload their own Remotion code for rendering is not. Client-side rendering has
  non-optional telemetry; SSR telemetry becomes mandatory for Automators in v5. Codec patent fees (H.264, HEVC, AAC)
  are not covered by the license.

### 3.13 Contributing and meta pages (useful facts only)

- System requirements (from the getting-started page mirrored at `contributing/docs.md`): Node or Bun, macOS 15
  (Sequoia) or later, Linux glibc >= 2.35; Alpine and NixOS unsupported. Starter: `npx create-video@latest --yes
  --blank my-video && cd my-video && npm i && npx remotion skills add && npm run dev`.
- New options follow: Node API > Studio render UI > CLI > config > default; camelCase for Node, kebab-case for CLI,
  units in numeric names.
- Rust compositor is maintenance-only (new media tags replace it); FFmpeg shared libs live in each
  `@remotion/compositor-*` package.
- Sound effects for `@remotion/sfx`: WAV, CC0, peak normalised to -3 dB.
- Custom HTML-in-canvas transition presentations: `u_time = 0` shows the entering scene, `1` the exiting one
  (`progress = 1.0 - u_time` when porting gl-transitions), handle null prev/next images in `draw()`.
- Web renderer contributions are screenshot-tested in Chromium, Firefox and WebKit via Vitest browser mode.
- Accessibility statements cover the websites only; noteworthy: brand blue `#0B84F3` fails 4.5:1 contrast on white,
  and autoplaying videos without captions/pause controls were flagged (a reminder for our own video deliverables).

---

## 4. Recipes

**R1. Standard social/web MP4 (the default deliverable).**
```bash
npx remotion render src/index.ts Main out/main.mp4 \
  --codec=h264 --crf=18 --pixel-format=yuv420p --color-space=bt709 \
  --audio-codec=aac --audio-bitrate=320k --props=./props.json
```
h264 + yuv420p plays everywhere. `--crf=18` is also the h264 default; lower means bigger/better. Keep the composition
width and height even. Verify with `npx remotion ffprobe out/main.mp4`.

**R2. Fast draft while iterating.** Render a subset and a smaller frame: `--frames=0-89` (or `--frames=120-`),
`--scale=0.5`, `--x264-preset=veryfast`, JPEG frames (default). Or skip video entirely and check stills (R3).

**R3. QA stills at key moments before the full render.** One browser session, several PNGs:
```bash
npx remotion render src/index.ts Main out/qa --frames=0,45,90,135,179 --image-format=png
```
Node: `renderFrames({composition, serveUrl, inputProps, outputDir, frames: [0, 45, 90], imageFormat: 'png',
onStart: () => {}, onFrameUpdate: () => {}})` (`onStart` and `onFrameUpdate` are required in the installed types).
Single still: `npx remotion still src/index.ts Main out/last.png --frame=-1`.

**R4. Transparent overlay.** For editors (Premiere, Resolve, Final Cut):
`--codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --image-format=png` -> `.mov`.
For the web: `--codec=vp9 --pixel-format=yuva420p --image-format=png` -> `.webm`. Studio: press T for the
checkerboard to confirm the background is really transparent. Can be made the composition default via
`calculateMetadata()` returning `{defaultCodec, defaultVideoImageFormat, defaultPixelFormat, defaultProResProfile}`.

**R5. Master / intermediate for further editing.** `--codec=prores --prores-profile=hq` (default profile) with PCM
audio (the ProRes default) -> large `.mov`; or `--prores-profile=4444-xq` for the highest quality.

**R6. Hardware-accelerated fast export on this Mac.** `--hardware-acceleration=if-possible --video-bitrate=12M`
(no `--crf`, no `--buffer-size`/`--max-rate`, or it silently falls back to software). Uses `h264_videotoolbox`,
`hevc_videotoolbox` or `prores_videotoolbox`. Use `required` only when you want a hard failure instead of fallback.

**R7. Variants from one composition.** CLI overrides `--width=1080 --height=1920` (3.2.40) and `--fps`/`--duration`
(4.0.424) change metadata at render time; the component must lay out from `useVideoConfig()`. For a permanent variant
registration use `duplicateComposition({newId: 'Portrait', metadata: {width: 1080, height: 1920}})` or
`calculateMetadata()` driven by input props.

**R8. GIF.** `--codec=gif --every-nth-frame=2` (30 fps -> 15 fps GIF) and `--number-of-gif-loops` omitted for infinite
looping (`0` = play once, `1` = play twice). Keep dimensions small; GIF has no CRF.

**R9. Audio deliverables.** Audio only: `--codec=mp3` (or `aac`, `wav`) with `--image-format=none` (Node:
`imageFormat: 'none'`). Stem next to the video: `--separate-audio-to=out/voice.wav` (extension picks the codec; must
be allowed for the video codec). Uncompressed audio inside the video: `--audio-codec=pcm-16` (h264 -> `.mkv`/`.mov`).
Match `--sample-rate` to the source (default 48000).

**R10. Cut a highlight reel from one timeline without new code (4.0.502).**
`npx remotion render src/index.ts Main out/reel.mp4 --frames=0-149,600-749,1200-` concatenates the ranges (video and
audio of gaps dropped). Node: `frameRange: [[0, 149], [600, 749], [1200, null]]`.

**R11. Remove silence from talking-head footage.** In a Node script (local absolute paths only):
`getSilentParts({src: absPath, noiseThresholdInDecibels: -30, minDurationInSeconds: 0.4})` -> `audibleParts`. Pass
the kept ranges as props and lay them back to back; `trimBefore`/`trimAfter` are source positions in frames at the
composition fps (`trimAfter` is absolute, not a length; cross-checked with the D7 file):
```tsx
<Series>
  {parts.map((p, i) => (
    <Series.Sequence key={i} durationInFrames={Math.round(p.endInSeconds * fps) - Math.round(p.startInSeconds * fps)}>
      <Video src={staticFile('talk.mp4')} trimBefore={Math.round(p.startInSeconds * fps)}
        trimAfter={Math.round(p.endInSeconds * fps)} />
    </Series.Sequence>
  ))}
</Series>
```
Set the composition duration to the sum of the parts in `calculateMetadata()`. Audio below the threshold counts as
silent (default -20 dB): a lower value such as -30 keeps quieter speech; tune it per source and listen to the result.

**R12. Batch or personalised renders with one browser.**
```ts
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome');
for (const job of jobs) {
  const composition = await selectComposition({serveUrl, id: 'Main', inputProps: job.props, puppeteerInstance: browser});
  await renderMedia({serveUrl, composition, inputProps: job.props, codec: 'h264',
    outputLocation: `out/${job.id}.mp4`, puppeteerInstance: browser});
}
await browser.close({silent: true});
```
Set Chromium flags (and `forceDeviceScaleFactor` if you use `scale`) on `openBrowser()`, not per render.

**R13. Render queue service.** Pattern from `repo/packages/template-render-server/server/render-queue.ts`: a
`Map<jobId, state>` (queued, in-progress with `progress`, completed with URL, failed with error), a promise chain as a
serial queue, `makeCancelSignal()` per job with `cancel` stored in the state, `onProgress` updating the map,
`selectComposition()` per job with that job's input props.

**R14. Player preview in a web app.** Memoise `inputProps`; keep `<Player>` in its own component; put time displays,
seek bars and buttons in sibling components that receive `playerRef`; drive a frame display with a
`useSyncExternalStore` hook subscribed to `frameupdate`; pass the click event into `play(e)` / `toggle(e)` (use
`onClickCapture` for Safari); `style={{width: '100%'}}` for responsive sizing.

**R15. Smooth preview playback of heavy media.** Use `@remotion/media` `<Video>`/`<Audio>` (buffer state on by
default), add `premountFor={fps}` (or more) on upcoming `<Sequence>`s or directly on the media/visual components
(4.0.495 / 4.0.528), show a spinner via `renderPoster` + `showPosterWhenBuffering`, and debug with
`logLevel="trace"`. Avoid `prefetch()` once the Player is mounted.

**R16. Poster / thumbnail.** In an app: `<Thumbnail component frameToDisplay={30} ... />`. As a file:
`npx remotion still ... --frame=45 --image-format=jpeg --jpeg-quality=90`. A Player poster that is a freeze frame:
`renderPoster` + `posterFillMode="composition-size"` + `showPosterWhenUnplayed`.

**R17. Hand the video to a human for fine-tuning in Studio.** Write interactive-friendly markup (section 3.4 rules),
run `npx remotion studio --no-open`, tell the human which named layers exist. Their drags, keyframes and easing edits
land in the source files; read the diff afterwards instead of assuming the old code.

**R18. Structured code edits from an agent (codemods, 4.0.528 draft).**
```ts
const project = {rootDir, files: {'src/Video.tsx': await fs.readFile(p, 'utf8')}};
const [title] = getJsxNodes({project, filePath: 'src/Video.tsx'}).filter((n) => n.tagName === 'Interactive.Div');
const {changes} = await updateJsxNodeKeyframes({project, node: title, updates: [
  {key: 'style.opacity', operation: {type: 'add', frame: 0, value: 0}},
  {key: 'style.opacity', operation: {type: 'add', frame: 30, value: 1}}]});
const next = applyCodemodChanges(project, changes); // then write changed files to disk
```
Keep `changes` as the undo record (swap previous/next to undo).

**R19. Export button inside a web app (client-side).** Check first with `canRenderMediaOnWeb({width, height,
container: 'mp4', videoCodec: 'h264'})`; then `renderMediaOnWeb({composition, inputProps, outputWritable:
await (await window.showSaveFilePicker({suggestedName: 'video.mp4'})).createWritable()})` to stream to disk, or
`getBlob()` for small videos. Only for compositions using the supported CSS/element subset (section 5).

**R20. Shader effect over live DOM (Chrome 149+ with flag).** `<HtmlInCanvas width height pixelDensity={usePixelDensity()}
onInit={createGlResources} onPaint={drawWithShader}>...</HtmlInCanvas>`; guard with `HtmlInCanvas.isSupported()` and
keep a non-shader fallback component for unsupported environments.

**R21. Chunked / distributed render (advanced).** Render each chunk with the same codec and settings plus
`frameRange`, `enforceAudioTrack: true`, `forSeamlessAacConcatenation: true`, `separateAudioTo`; then
`combineChunks({videoFiles, audioFiles, codec, fps, framesPerChunk, compositionDurationInFrames, preferLossless})`.
Prefer plain `renderMedia()` (already multi-threaded) unless you really distribute across machines.

**R22. Team review server.** Dockerised Studio (section 3.4) or a static `npx remotion bundle` deployment that doubles
as a serve URL: `npx remotion render https://host/ Main out.mp4 --props '{"title":"x"}'`.

---

## 5. Performance and render stability

**What makes SSR renders fast**
- Concurrency: default `round(min(8, max(1, cpus/2)))` (installed code), so a many-core Mac never uses more than 8
  tabs unless told to. Measure with `npx remotion benchmark src/index.ts Main --concurrencies=4,8,12 --runs=3` and pick
  the knee of the curve; `resolvedConcurrency` is reported in `onStart`.
- JPEG frames (default) are the fastest; PNG costs time and is only needed for alpha or maximum color accuracy.
- Parallel encoding (frames captured while FFmpeg encodes) only happens for h264, h264-mkv and h265 (not h264-ts,
  vp8, vp9, av1, prores, gif); `--log=verbose` confirms it. `disallowParallelEncoding` trades speed for memory.
- Codec cost: AV1 (libaom) is flagged by Remotion as significantly slower; VP8/VP9 compress better but render slower;
  x264 presets trade encode time for size (default `medium`); ProRes encodes fast but produces huge files.
- Hardware encoders (`if-possible`: VideoToolbox for h264/h265/prores on macOS) are the typical speed-up for the
  encode stage, but they disable CRF (bitrate mode only). The docs make no speed claim; benchmark before relying on it.
- `scale` multiplies pixel count by scale squared; use `0.5` for drafts, `2` only for final sharp text/vector output.
- Reuse work: one `bundle()` per code version (bundle cache on by default, Rspack via `--rspack` or
  `Config.setRspack(true)` since 4.0.502), one browser via `openBrowser()`, `selectComposition()` rather than
  `getCompositions()` (the latter runs every composition's `calculateMetadata()`).
- Find hot frames: `slowestFrames` (return of `renderMedia()`), `onFrameUpdate` timing in `renderFrames()`.
- Video-heavy compositions: `offthreadVideoCacheSizeInBytes` / `mediaCacheSizeInBytes` default to half of system RAM
  each; `offthreadVideoThreads` default 2. Raise for speed, lower when several renders share one machine.
- H.264 sources without faststart are not seekable in the browser (Html5 media fails, OffthreadVideo slow); re-encode
  once (`npx remotion ffmpeg -i in.mp4 -movflags +faststart out.mp4`) before using them.
- GPU content (WebGL, Three, shaders): default GL backend is Chrome's choice; check `npx remotion gpu`; if WebGL2 is
  unavailable during a render the docs suggest `--gl=angle`; on Linux GPUs need `--chrome-mode=chrome-for-testing`.
  `enableMultiProcessOnLinux` is on by default since 4.0.137 (faster; newer Chrome refuses single-process).

**What breaks deterministic parallel rendering (from this material)**
- A frame must not depend on what previous frames did: tabs render arbitrary frames out of order, and `--frames`
  lists or ranges render isolated frames. State, timers and one-time effects that "build up" across frames will differ
  between Studio playback and renders.
- Premounting and the buffer state exist only in Player/Studio; do not rely on them to "wait" in renders. Use
  `delayRender()` (or `useDelayRender()` for client-side renders) to hold a frame until data or media is ready; it
  times out after `timeoutInMilliseconds` (30000) per frame.
- Anything network-dependent inside `calculateMetadata()` runs again for every `selectComposition()`; in Studio use
  `reevaluateComposition()` to refresh it.
- Async `onPaint` in `<HtmlInCanvas>` keeps the frame open through `delayRender()`; long GPU work there is paid per
  frame.
- Chromium flags passed per call are ignored when you pass `puppeteerInstance`.
- Even-dimension rounding (h264/h265/av1/h264-mkv/h264-ts) silently shrinks odd sizes by 1 px (only logged in
  verbose mode).

**Memory**
- Each concurrent tab holds a full page; parallel encoding adds an FFmpeg process; OffthreadVideo and `@remotion/media`
  caches can each take up to half the RAM by default. On a 36 GB machine running several renders at once, set explicit
  cache sizes and a lower concurrency.
- `outputLocation: null` returns the whole video as a Buffer in memory; write to disk for anything large.
- Client-side: `outputTarget: 'web-fs'` (OPFS, default when available) or `outputWritable` avoids holding the file in
  memory.

**Player performance**
- Re-rendering the component that renders `<Player>` re-renders the video; keep frequently changing state elsewhere.
- Memoise `inputProps` (and `lazyComponent`, render callbacks with `useCallback`).
- `timeupdate` (<= 4 per second) for coarse UI, `frameupdate` only where every frame matters.
- Over-aggressive `prefetch()` and premounting consume memory and bandwidth; `logLevel="trace"` is not for
  production.

**Client-side renderer**
- Single-threaded (no concurrency), but no IPC and usually GPU-accelerated.
- `pageResponsiveness` default `'medium'` (yield every 33 ms) slows renders; `'disabled'` is fastest when the page
  need not stay interactive.
- Background tabs are throttled; a Worker timer keeps the render going but slower. Keep the tab visible.
- Supported CSS: layout, overflow, `object-fit` (not `object-position`), `transform` (3D transforms need WebGL),
  `transform-origin`, `opacity`, `scale`/`rotate`/`translate`, `backface-visibility`, `background-color`,
  linear-gradient backgrounds (+ size/position, `background-clip`), borders, `border-radius`, `outline`, most text
  properties (color, fill color, font-*, line-height, letter/word spacing, text-transform, text-decoration styles,
  `text-shadow`, `-webkit-text-stroke`, `paint-order`), basic `box-shadow`, linear-gradient `mask-image` and simple
  raster masks (4.0.501), `filter` functions (not on Safari), `clip-path` polygon/path/circle/ellipse/inset.
  Unsupported: `z-index` (order the DOM back to front), `mix-blend-mode`, `background-blend-mode`,
  `backdrop-filter`, `perspective`, `transform-style`, `writing-mode`, `corner-shape`, inset/spread shadows, SVG
  `url()` filters, clip paths and masks, `<OffthreadVideo>`, `<Html5Video>`, `<Html5Audio>`, `<AnimatedEmoji>`.
  SVG `<text>` fonts from `@remotion/fonts` / `@remotion/google-fonts` are embedded (4.0.525) when the font is set
  inside the SVG markup.

---

## 6. Errors and fixes

| Symptom / message | Cause | Fix |
|---|---|---|
| `"crf" and "videoBitrate" can not both be set` | both quality modes | keep one |
| `"crf" option is not supported with hardware acceleration` | `crf` + `hardwareAcceleration: 'required'` (or HW encoder in use) | use `videoBitrate`, or `if-possible` (falls back to software) |
| `"encodingMaxRate" can not be set without also setting "encodingBufferSize"` | `maxRate` alone | add `bufferSize` |
| `Setting the CRF to 0 with a H264 codec is not supported anymore` | CRF 0 | use >= 1 (18 is default) |
| `CRF must be between X and Y for codec Z` / `codec does not support the --crf option` | out of range / prores, gif, audio | see table 3.3 |
| `You have set a x264 preset but the codec is ...` | preset with non-h264 | drop preset or use h264 |
| `You have set a ProRes profile but the codec is ...` | profile without prores | set `--codec=prores` |
| `Pixel format was set to 'yuva420p' but codec ... does not support it` | yuva420p outside vp8/vp9 | use vp8/vp9, or yuva444p10le + prores |
| `...to render transparent videos, you need to set PNG as the image format` | alpha pixel format with JPEG frames | `--image-format=png` |
| Output is 1 px smaller than the composition | odd width/height with h264/h265/av1 | use even dimensions |
| `"scale" must be ...` | scale <= 0 or > 16 | stay in (0, 16] |
| `Maximum for --concurrency is N` / `Minimum for concurrency is 1` | concurrency out of range | lower it or use a percentage |
| Render times out waiting for `delayRender()` | asset or data slower than 30 s per frame | fix the handle, preload, or raise `timeoutInMilliseconds` / `--timeout` |
| Chromium options have no effect | browser passed via `puppeteerInstance` | set them on `openBrowser()` |
| Scaled render looks wrong with a reused browser | device scale factor fixed at launch | `openBrowser(..., {forceDeviceScaleFactor})` |
| `--props` JSON ignored on Windows | shell strips quotes | pass a `.json` file path |
| `getSilentParts` complains about the argument | docs header says `source` | the real key is `src`; absolute local path only |
| `extractAudio` output unusable | extension does not match the source audio codec | inspect the codec first (Mediabunny / ffprobe) |
| "Non-seekable media" / slow OffthreadVideo | h264 without faststart | re-encode with `-movflags +faststart` |
| AV1 unavailable | Linux ARM64 GNU | pick another codec |
| WebGL2 unavailable during render | GL backend | `--gl=angle` (also check `npx remotion gpu`) |
| `saveDefaultProps()` / `restartStudio()` / `shutDownStudio()` throw | static or read-only Studio, not in Studio, or `zod` missing | run the local Studio server; install zod |
| `visualControl()` value not saved | dynamic control name | use a static string literal |
| Studio shows values greyed out / cannot drag | non-inline styles, spreads, math, extracted constants, `transform` | follow the interactivity rules (3.4) |
| Easing shown read-only | helper not representable as one cubic Bezier | use `Easing.bezier`, `linear`, `spring({...})` or listed helpers |
| `--enable-cross-site-isolation` unknown | docs example typo | use `--cross-site-isolation` |
| Studio on DigitalOcean App Platform does not work | proxy blocks server-sent events | use a droplet or another host |
| Studio unreachable on Fly.io | IPv6 binding | `npx remotion studio --ipv4` |
| Static Studio on GitHub Pages cannot load `public/` files | pre-4.0.497 bundle | `--public-path="./"` or upgrade |
| Player throws after changing `numberOfSharedAudioTags` or `_experimentalKeepAudioContextAlive`; changes to `initialFrame` / `sampleRate` have no effect | these are mount-only | remount with a new `key` |
| Player error: more audio tags than shared tags | too many `<Html5Audio>` at once | raise `numberOfSharedAudioTags` (v4 default 5) |
| Audio does not start / video muted in Player | autoplay policy | start from a user gesture and pass the event to `play(e)`; `onClickCapture` on Safari; handle `onAutoPlayError` (4.0.187) |
| `requestFullscreen()` throws | `allowFullscreen={false}` or iOS Safari | feature-detect after mount |
| Player crashed and stays on error UI | render error caught by boundary | remount via `key`; custom `errorFallback` |
| Buffer never clears in dev | `delayPlayback()` called inside `useState` (strict mode double call) | call it in `useEffect` and `unblock()` in cleanup |
| Client render: "image is tainted due to CORS restrictions" / "image is in a broken state" | no CORS header / 404 | serve with `Access-Control-Allow-Origin` / fix URL |
| Client render ignores stacking or blend modes | unsupported CSS | reorder DOM; avoid blend/backdrop filters |
| `canRenderMediaOnWeb` issue `invalid-dimensions` / `transparent-video-unsupported` | odd size with h264/h265 / alpha without vp8/vp9 + webm/mkv | fix size / codec |
| `getBlob()` rejects | `outputWritable` used | the file is already in the stream |
| `<HtmlInCanvas>` fatal error | Chrome < 149 or flag off | guard with `HtmlInCanvas.isSupported()` |
| Error when nesting `<HtmlInCanvas>` | nesting unsupported | merge effects into one |
| `applyCodemodChanges` throws | file changed since the codemod ran, or duplicate file entries | re-read files and re-run the codemod |
| Codemod rejects the edit | computed props, spreads, dynamic timing, conditional effects arrays, default exports for `addComponent` | make the source static/inline first |
| `installInStudio` codes `no-compatible-studio`, `studio-upgrade-required`, `loopback-network-permission-denied` | no Studio on ports 3000 to 3009 / old Studio / browser blocked local network | start or upgrade Studio; use drag-and-drop instead |
| `loadBrowserBundle` throws | entry did not call `registerRoot()` synchronously once, or CSP blocks eval | fix entry / CSP |

---

## 7. What our skills must teach

**Version and environment guard**
- Target 4.0.528. Do not use: browser-bundler source locations (4.0.529). Treat as draft/experimental: codemods,
  browser bundler, `_experimentalKeepAudioContextAlive`, `--experimental-keep-audio-context-alive`, HTML-in-canvas.
- Recent-but-available features worth using: multi-range `--frames` and `renderFrames({frames})` (4.0.502), Rspack
  (4.0.502), `premountFor` on visual components (4.0.528), default-props inference (4.0.516), shortcut customisation
  (4.0.523), `getCompositions({...})` object form (4.0.497), relocatable bundles (4.0.497).
- Keep all `@remotion/*` versions identical (`npx remotion versions`); add packages with `npx remotion add`.
- macOS 15+ is required by current Remotion; Linux needs glibc 2.35+.

**Render option placement**
- Project-wide defaults (codec, pixel format, image format, Rspack, overwrite, shortcuts, editor) go in
  `remotion.config.ts`; per-composition export defaults go in `calculateMetadata()` (`defaultCodec`,
  `defaultPixelFormat`, `defaultVideoImageFormat`, `defaultProResProfile`, `defaultOutName`, `defaultSampleRate`);
  one-off choices go on the CLI; Node scripts must pass options explicitly (config file is ignored there).

**Codec decision table**

| Goal | codec | pixel format | image format | audio | notes |
|---|---|---|---|---|---|
| Social / web / client MP4 (default) | h264 | yuv420p | jpeg | aac 320k | `--color-space=bt709`, CRF 18 (the h264 default; go lower only for banding-prone gradients) |
| Smaller file, modern players | h265 | yuv420p | jpeg | aac | CRF default 23 |
| Browser playback with alpha | vp9 (or vp8) | yuva420p | png | opus | .webm |
| NLE overlay with alpha | prores 4444 | yuva444p10le | png | pcm-16 | .mov, large |
| Edit master | prores hq (or 4444-xq) | default for now (see open question 12) | png for color | pcm-16 | .mov |
| Web delivery with best compression, time available | av1 | yuv420p | jpeg | aac or opus | much slower |
| Animated preview | gif | n/a | jpeg | none | `--every-nth-frame=2`, small size |
| Voice / music only | mp3, aac or wav | n/a | none | same | `--image-format=none` |
| Image sequence | any + `--sequence` or `--frames=list` | | png/jpeg | | filenames via `--image-sequence-pattern` |
| Still / thumbnail | `remotion still` | | png (text/graphics), jpeg (photo), webp, pdf (print) | | `--frame=-1` = last frame |

**Quality ladder**
- Draft: `--scale=0.5 --x264-preset=veryfast --frames=<range>`; or stills only.
- Review: full size, defaults, `--crf=23`.
- Final: `--crf=18` (or 16 for fine gradients), `--color-space=bt709`, audio 320k, 48 kHz.
- Fast final on Mac: `--hardware-acceleration=if-possible --video-bitrate=<n>M` (no CRF).
- Master: ProRes.

**Pre-render checklist**
1. `npx remotion compositions src/index.ts` shows the expected IDs; `selectComposition()` resolves metadata with the
   exact props you will render.
2. Width and height are even (for h264/h265/av1) and match the platform spec.
3. All assets load within 30 s per frame, remote media is CORS/seekable (faststart), fonts load via
   `delayRender`-aware loaders.
4. Render QA stills (`--frames=a,b,c --image-format=png`) and look at them before the full render.
5. Choose codec/pixel format/image format from the table; transparency needs PNG frames and an alpha pixel format.
6. Decide concurrency (benchmark once per machine) and cache sizes if rendering several jobs in parallel.
7. Render with `--log=verbose` the first time; keep `slowestFrames` for optimisation.
8. Verify output with `npx remotion ffprobe out.mp4` (codec, pix_fmt, color primaries/transfer, size, fps,
   duration, audio stream presence and sample rate); run visual QA on the file.

**Studio-editable code (always, unless the user opts out)**
- Named `Interactive.*` elements for every visible layer; inline `style` literals; inline `interpolate()` per
  property with literal ranges/easing; `scale`/`rotate`/`translate` instead of `transform`; inline
  `<Composition>` metadata and `defaultProps` without casts; inline stable effects arrays; custom components via
  `Interactive.withSchema()` with `Interactive.baseSchema` and forwarded `controls` + `outlineRef`.
- After a human edits in Studio, re-read the source before making further changes.
- Launch Studio with `--no-open` from an agent and report the URL; `--force-new` only when a second instance is needed.

**Player checklist**
- `component` directly (no `<Composition>`), memoised `inputProps`, controls in siblings via `playerRef`,
  `useSyncExternalStore` + `frameupdate` for synced UI, events passed to `play(e)`, `@remotion/media` media with
  `premountFor`, spinner via `renderPoster`/`showPosterWhenBuffering`, `acknowledgeRemotionLicense` only when the
  license question is settled.

**SSR vs client-side rendering decision**
- Use SSR (`renderMedia`/CLI) for anything using blend modes, backdrop filters, z-index, perspective, OffthreadVideo,
  Html5 media, complex CSS, or where pixel-exact output matters.
- Use `renderMediaOnWeb()` only for simple layouts built from the supported subset, when rendering must happen in the
  user's browser; run `canRenderMediaOnWeb()` first; stream large outputs with `outputWritable`.

**Licensing awareness (state facts, do not give legal advice)**
- Rendering programmatically or embedding `<Player>` counts as automation for organisations that need a Company
  License; the Free License covers individuals and teams up to 3 people. Agencies delivering only video files count
  only their own headcount. Surface this when building render pipelines or Player apps for a client.

---

## 8. Best examples to learn from

- `repo/packages/template-render-server/server/render-queue.ts`: minimal production render queue (select, render,
  progress, cancel, job states).
- `repo/packages/template-render-server/remotion.config.ts`: Rspack + JPEG + overwrite defaults, and the reminder that
  Node APIs ignore the config file.
- `repo/packages/skills/skills/remotion-render/transparent-videos.md`: exact ProRes/WebM alpha settings and the
  `calculateMetadata()` default-export trick.
- `repo/packages/skills/skills/remotion-interactivity/SKILL.md`: interactivity rules plus `Interactive.Path` and inline
  `interpolatePaths()` for editable SVG morphs.
- `mirror/docs/studio/make-component-interactive.md`: complete `Interactive.withSchema()` component with forwarded
  `controls` and `outlineRef`.
- `mirror/docs/studio/interactivity-best-practices.md`: good vs bad markup side by side.
- `mirror/docs/player/custom-controls.md`: full SeekBar, time display (hh:mm:ss.ff), volume, mute, fullscreen, loop.
- `mirror/docs/player/drag-and-drop.md`: canvas editing inside the Player with `useCurrentScale()`, selection
  outlines and resize handles (a mini editor).
- `mirror/docs/player/current-time.md`: the `useSyncExternalStore` frame hook.
- `mirror/docs/player/premounting.md`: custom `PremountedSequence` with `Freeze` and `useRemotionEnvironment()`.
- `mirror/docs/remotion/html-in-canvas.md`: three complete effect implementations (2D animated blur, WebGL2 wave
  distortion, WebGPU pixelate/posterize).
- `mirror/docs/client-side-rendering/limitations.md`: the authoritative CSS support matrix for web rendering.
- `mirror/docs/web-renderer/render-media-on-web.md`: `outputWritable` + `showSaveFilePicker` streaming export.
- `mirror/docs/studio-protocol/component-library-integration.md`: Player preview + Vite `?raw` source for Element
  libraries.
- `mirror/docs/studio/deploy-server.md`: working Dockerfile for a hosted Studio.
- `examples/shorts-customizer`: the docs' reference project for deploying the Studio: Dockerfile plus a Zod-schema
  driven "goal" short (score, minute, team, player as `defaultProps`) edited through the Props editor; pinned to the
  old Remotion 4.0.48, so read it for the pattern, not the versions.
- `examples/html-in-canvas`: example project for HTML-in-canvas effects.
- URL: https://github.com/remotion-dev/remotion/blob/main/packages/player-example/src/App.tsx (large Player example
  referenced by the best-practices page).

---

## 9. Open questions

1. Color: the v4 default `colorSpace` is `"default"` (= bt601 since 4.0.424) and writes no color tags; `bt709` tags
   and converts (section 3.3). Recommendation stands (always `bt709`), but confirm with one A/B test render + ffprobe
   on this machine, and check whether JPEG vs PNG frames visibly change the result (docs prefer PNG for accuracy).
2. `bt2020-cl` appears in the option text but the installed v4 validator rejects it; confirm and avoid.
3. Does the CLI switch to `--image-format=none` automatically for audio-only codecs, or must we always pass it?
4. Best concurrency on this Mac Studio (default caps at 8): run `npx remotion benchmark` once and store the result.
5. VideoToolbox quality per bitrate versus libx264 CRF 18 on Apple Silicon, and whether HW encodes are bit-identical
   across runs (matters for reproducible deliverables).
6. `--x264-preset` shows "AvailableFrom 4.2.2" in the docs (typo); exact introduction version unknown (works on 4.0.528
   per installed code).
7. Web renderer docs vs installed types disagree (containers/audio codecs; `resolvedVideoCodec` vs `videoCodec` field
   names in the types page). Which containers actually encode in Chrome today?
8. Codemods and browser bundler are draft APIs; do we build skill features on them now or wait? They are installed
   (codemods) / not installed (browser bundler) in `remotion-broll`.
9. `premountFor` on visual components (4.0.528) and on `@remotion/media` (4.0.495): confirm the Studio timeline and
   Player behave as documented in our projects.
10. R11 uses `trimBefore`/`trimAfter` as described in the D7 file; render one silence-cut test to confirm there are
    no audio clicks at the joins before shipping it as a skill recipe.
11. License position of the agency (agency headcount, client-owned projects, Player use) is a business decision for the
    user; the skills should surface the rule, not decide it.
12. ProRes pixel format: Remotion passes `-pix_fmt yuv420p` (the default) to `prores_ks` unless told otherwise; FFmpeg
    normally substitutes a ProRes-compatible format, but the docs never say which pixel format to use for opaque
    ProRes masters (`yuv422p10le` is the natural candidate). Test before recommending.
13. `h264-ts` is a valid codec in the installed code but has no docs page in this material; its use cases
    (broadcast/HLS segments?) are undocumented here.
14. `shutDownStudio()` links to a "WebMCP" page (`/docs/ai/webmcp`, not in this assignment). If the Studio exposes
    WebMCP tools, an agent could drive play/seek/render in the Studio directly; whoever owns the AI docs should check.
15. The pricing page in the mirror is an unrendered component; prices above come from the FAQ text (Creators $25 per
    person per month, Automators $0.01 per render with $100 minimum, Enterprise from $500). Re-check before quoting
    them to a client.
