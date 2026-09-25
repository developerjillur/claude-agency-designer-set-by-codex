# D7: Media, audio, captions, SFX, transcription, matting, Recorder

Agent: D7-media-audio-captions. Written 2026-09-25. Target: Remotion 4.0.528 (React 19) as installed on this machine.

---

## 1. Scope and coverage

### Assigned material: 137 of 137 pages read fully, one by one

| Area (mirror/docs/...) | Pages | Notes |
|---|---|---|
| `media/` (@remotion/media) | 5 | audio, video, cache, fallback, support |
| `videos/` | 10 | speed over time, align duration, Three.js texture, speed segments, jump cuts, media fragments, ProRes, sequence, transparency, pixel manipulation |
| `audio/` | 11 | delaying, exporting, from-video, importing, muting, pitch, sfx, speed, trimming, visualization, volume |
| `captions/` | 10 | api, Caption type, createTikTokStyleCaptions, displaying, ensureMaxCharactersPerLine, exporting, importing, parseSrt, serializeSrt, transcribing |
| `sfx/` | 32 | one page per sound |
| `media-utils/` | 2 | createSmoothSvgPath, visualizeAudioWaveform |
| `elevenlabs/`, `openai-whisper/` | 1 + 1 | transcript converters |
| `install-whisper-cpp/` | 5 | install, download model, transcribe, toCaptions, deprecated convertToCaptions |
| `whisper-web/` | 7 | WASM transcription in browser |
| `whisper-webgpu/` | 12 | WebGPU transcription (browser and Node) |
| `video-matting/` | 9 | foreground/background separation |
| `recorder/` | 32 | the Remotion Recorder template |

Also read (as requested): `repo/packages/captions/src` (index, caption, create-tiktok-style-captions, ensure-max-characters-per-line, parse-srt, serialize-srt, plus the 3 test files). All paths are in `kb/D7-media-audio-captions.coverage.txt`.

### Supplementary reading (read-only), to verify behaviour on 4.0.528 and extract craft
- Installed packages in `remotion-broll` (all at 4.0.528): `@remotion/media` type definitions and `dist/esm/index.mjs` (volume, objectFit, trim, fallback, cache code paths), `remotion` core bundle (`evaluateVolume`, `warnAboutTooHighVolume`, `interpolate` defaults, `<Sequence>` validation, Freeze muting, `calculateMediaDuration`), `@remotion/sfx` exports, `@remotion/captions` dist. Wherever this file says "verified in bundle", it comes from these.
- `repo/packages/template-recorder` (41 files: config, calculate-metadata, scenes, B-roll, audio track, SFX, captions processing, SRT, scripts), `repo/packages/template-tiktok` (8 files).
- `examples/animated-captions` (8 files), `examples/video-with-jump-cuts` (2), `examples/tone-js-example` (1).
- Cross-check only (owned by D2): `mirror/docs/timing.md`, `using-audio.md`, `video-tags.md`.
- Skimmed the installed skills `~/.claude/skills/remotion-captions` and `remotion-multimedia` to see what they already teach (they are thin: Caption type, whisper.cpp script, display snippet, Mediabunny duration helpers).

### Could not read
- Interactive MDX components embedded in pages (sound PlayButtons, the speed-ramp demo player, waveform demos, greenscreen canvas demos, Recorder layout diagrams and the Recorder demo video): not present in the Markdown mirror.
- External sources linked from pages (GitHub sources of `@remotion/media`, `@remotion/elevenlabs`, `@remotion/openai-whisper`, `@remotion/whisper-web`, `@remotion/whisper-webgpu`, `@remotion/video-matting`; mediabunny.dev format table). These packages are also not installed in the project, so their exact output shapes (for example whether their `toCaptions()` puts a leading space before every word) are unverified. See Open questions.

---

## 2. Mental model

1. **Three generations of media tags; one default.** For new code use `<Video>` and `<Audio>` from `@remotion/media`. They are built on Mediabunny + WebCodecs, decode exactly the frame (and exactly the audio slice) needed for each Remotion frame, and draw video into a `<canvas>`. Legacy tags from `remotion`: `<OffthreadVideo>` (Rust + FFmpeg frame extractor, server-side only, full download), `<Html5Video>` / `<Html5Audio>` (plain HTML5 elements, not frame-exact). `@remotion/media` automatically falls back to `<OffthreadVideo>` (video) or `<Html5Audio>` (audio) when it cannot decode, but only in preview and server-side rendering, never in client-side rendering.

2. **Timeline algebra.** Every editing operation reduces to five props that apply in this order:
   1. `from`: position on the parent timeline (frames).
   2. `trimBefore` / `trimAfter`: which source range to use, in frames at the *composition* fps, measured from the start of the file. `trimAfter` is an absolute source position, not a length.
   3. `playbackRate`: stretches the selected range. Timeline length = `(trimAfter - trimBefore) / playbackRate`.
   4. `loop`: repeats the stretched range.
   5. `durationInFrames`: cuts the item off last.
   Children see frame `trimBefore + (t - from) * playbackRate` at parent frame `t`.

3. **Trimmed clips self-limit; untrimmed clips freeze.** Verified in bundle: when `trimAfter` is set and `loop` is not, `<Video>` wraps itself in a Sequence lasting exactly `(trimAfter - trimBefore) / playbackRate` frames and disappears afterwards. Without `trimAfter`, the last frame stays visible until the parent sequence ends.

4. **Frames are independent.** Rendering splits frames across parallel browser tabs. Every time-dependent value must be a pure function of the frame. That is why interpolating `playbackRate` does not make a speed ramp: you must integrate speed from frame 0 to the current frame.

5. **Audio is a mix of tracks.** Every mounted, unmuted `<Audio>` or `<Video>` (and legacy tags) is a track; adding tags mixes them. `volume` is a linear gain (1 = unity, above 1 amplifies), static or `(f) => number` where `f` is 0 when that media starts playing (not `useCurrentFrame()` of the composition). Verified in bundle: render mixes at 48 kHz stereo, evaluates the volume once per video frame, multiplies 16-bit samples and hard-clips.

6. **Preview is not render.** In the Studio and Player, media must buffer, so you premount clips (`premountFor`) and the Player pauses while buffering. During render, frames are selected exactly and premounting does nothing for correctness. A choppy preview is usually not a render bug.

7. **The browser decides what is possible.** Remote files need CORS. WebCodecs decodes H.264, VP8, VP9, AAC, Opus, MP3, FLAC, Vorbis; H.265 and AV1 go to fallback during render. ProRes needs `@mediabunny/prores`. Alpha needs WebGL2 (off by default in the headless browser). Matroska audio (`.webm`, `.mkv`) must be decoded from the beginning.

8. **Captions are data in milliseconds; display is in frames.** Pipeline: transcribe once, offline, to word-level `Caption[]` JSON (ms, whitespace-sensitive) -> group into pages (`createTikTokStyleCaptions`) or subtitle lines (SRT) -> mount each page in a `<Sequence>` (ms to frames) -> style tokens by comparing the current time with token times.

9. **An edit is an EDL.** An edit decision list is an ordered list of source ranges with speeds. Compute clip durations in `calculateMetadata()` (Mediabunny), render with `<Series>`/`<Sequence>`, and remap every other timed thing (captions, SFX cues, B-roll, music ducking) through the same list: `outputMs = clipStartMs + (sourceMs - trimBeforeMs) / playbackRate`.

10. **The Recorder is the reference editor.** Scenes live in composition props (zod schema), edited in the Studio props panel. `calculateMetadata()` derives trims from captions, layout, transition overlaps with handles, B-roll constraints and SRT; an audio track ducks music under speech; SFX mark transitions; captions are burned in (square) or exported as SRT (landscape).

---

## 3. API digest

### 3.1 `<Video>` from `@remotion/media`

Recommended video component. Draws frames into a `<canvas>` via Mediabunny; native buffering in the Player is on by default. Compatible with Chrome, Firefox, Safari, SSR, client-side rendering (supported codecs only), Player, Studio.

| Prop | Type / default | Since | Notes and gotchas |
|---|---|---|---|
| `src` | string, required | | `staticFile()` path, CORS-enabled URL, or HLS `.m3u8` |
| `from` | number, 0 | 4.0.445 | Same as `<Sequence from>`; cascades with outer sequences |
| `durationInFrames` | number, Infinity | 4.0.445 | Same as Sequence |
| `premountFor` | frames | 4.0.495 | Mounted early with `display: none`, frozen at first frame, to buffer |
| `postmountFor` | frames | 4.0.495 | Kept mounted after end, invisible, frozen on last frame |
| `styleWhilePremounted` / `styleWhilePostmounted` | CSS | 4.0.495 | Override the default `display: none; pointer-events: none` |
| `trimBefore` / `trimAfter` | frames at comp fps | | Source range; see mental model |
| `volume` | number or `(f) => number`, 1 | | `f` starts at 0 when the media starts. Negative values are clamped to 0; NaN or non-finite from a callback throws; 100 or more throws (verified) |
| `loopVolumeCurveBehavior` | `'repeat'` or `'extend'`, `'repeat'` | 4.0.354 | With `loop`: restart `f` each iteration or keep counting |
| `playbackRate` | number, 1 | 4.0.354 | Changes pitch too (no pitch preservation on this path). Reverse not supported. Cannot be animated (see recipes) |
| `muted` | boolean | | May change over time |
| `loop` | boolean | | Loops the trimmed range |
| `style` | CSS for the `<canvas>` | | **`style.objectFit` is ignored**: the `objectFit` prop (default `contain`) overrides it and a warning is logged (verified) |
| `objectFit` | `'contain'` default, `'cover'`, `'fill'`, `'none'`, `'scale-down'` | 4.0.442 | Use this for full-bleed video. Also warns on `object-*` class names |
| `cropLeft` / `cropRight` / `cropTop` / `cropBottom` | ratio 0 to 1 | 4.0.500 | Same semantics as Sequence crop |
| `effects` | effect chain | 4.0.464 | `@remotion/effects` applied after the frame is drawn (for example `colorKey()` for greenscreen) |
| `name` | string | | Studio timeline label |
| `showInTimeline` | boolean, true | | |
| `onError` | `(err) => 'fallback' or 'fail'` | 4.0.404 | Default behaviour is fallback. In client-side rendering it always fails |
| `onVideoFrame` | `(frame: CanvasImageSource) => void` | | Receives an `ImageBitmap` or `VideoFrame` whenever a frame is drawn |
| `headless` | boolean | 4.0.387 | No canvas mounted; `onVideoFrame` still fires (Three.js textures) |
| `audioStreamIndex` | number, 0 | | Pick an audio stream in multi-stream files |
| `requestInit` | `RequestInit` | 4.0.465 | Captured on mount (inline object is safe). `{cache: 'no-store'}` when a CDN returns bad range responses; `{credentials: 'include'}` for cookies |
| `credentials` | deprecated | 4.0.437 | Use `requestInit.credentials` (wins if both given) |
| `toneFrequency` | 0.01 to 2, constant | SSR 4.0.357, preview 4.0.520, client 4.0.523 | Pitch shift without speed change. Not keyframable. Not applied when falling back in preview |
| `delayRenderTimeoutInMilliseconds`, `delayRenderRetries` | | | For the internal `delayRender()` |
| `fallbackOffthreadVideoProps` | object | | Only used on fallback: `acceptableTimeShiftInSeconds`, `transparent` (bundle default true), `toneMapped` (default true), `onError`, `crossOrigin`, `useWebAudioApi`, `pauseWhenBuffering`, `onAutoPlayError`, `preservePitch` (4.0.463) |
| `disallowFallbackToOffthreadVideo` | boolean | | Fail instead of falling back |
| `debugOverlay` | boolean | | Playback debug overlay |

Also accepted by the 4.0.528 types but not documented on the page: `logLevel`, `className`, `data-*` attributes, `freeze` (number or null) and `hidden` (boolean) inherited from the Sequence-like base props. Verified in bundle: the canvas is sized to the source's intrinsic display size (rotation applied) and scaled by CSS, so a 4K source costs 4K decoding even in a 1080p composition.

```tsx
import {Video} from '@remotion/media';
import {AbsoluteFill, staticFile} from 'remotion';

export const Bg: React.FC = () => (
  <AbsoluteFill>
    <Video src={staticFile('broll.mp4')} objectFit="cover" style={{width: '100%', height: '100%'}} muted />
  </AbsoluteFill>
);
```

### 3.2 `<Audio>` from `@remotion/media`

Same timing and loading model as `<Video>`, audio only.

| Prop | Default | Since | Notes |
|---|---|---|---|
| `src` | required | | file or URL |
| `from`, `durationInFrames` | 0, Infinity | 4.0.445 | |
| `premountFor`, `postmountFor` | | 4.0.495 | Buffering in the Player |
| `trimBefore`, `trimAfter` | | | Audio still starts at the beginning of its sequence; use `from` to delay |
| `volume`, `loopVolumeCurveBehavior` | 1, `'repeat'` | | As for Video |
| `playbackRate` | 1 | | Pitch changes with speed. Chrome supports 0.0625 to 16 |
| `loop` | false | 3.2.29 (page) | |
| `muted` | false | | Can change over time (mute a section) |
| `name`, `showInTimeline` | | | |
| `onError` | fallback | 4.0.404 | Fallback target is `<Html5Audio>` |
| `audioStreamIndex` | 0 | | |
| `requestInit` | | 4.0.465 | `credentials` deprecated (4.0.437) |
| `toneFrequency` | 1 | as Video | |
| `fallbackHtml5AudioProps` | | | `onError`, `useWebAudioApi`, `acceptableTimeShiftInSeconds`, `pauseWhenBuffering`, `crossOrigin`, `preservePitch` (4.0.463) |
| `disallowFallbackToHtml5Audio` | false | | |
| `delayRenderTimeoutInMilliseconds`, `delayRenderRetries`, `logLevel` | | | |

### 3.3 Fallback behaviour
- Triggers: CORS failure, container not supported by Mediabunny, codec WebCodecs cannot decode (H.265 during render is the classic), alpha channel without browser WebGL2 (the default headless browser has no WebGL).
- Log line to watch for: `Cannot decode /public/video-h265.mp4, falling back to <OffthreadVideo>`. On Lambda, check CloudWatch.
- `loop` during fallback: in preview, `<Html5Video>` loops natively. During render, `<OffthreadVideo>` cannot loop, so `@remotion/media` reads the duration and wraps it in `<Loop>`; if the duration cannot be read (CORS, broken container) the render fails.
- Client-side rendering (`@remotion/web-renderer`): no fallback exists, the render fails with a descriptive error.
- Fallback changes behaviour: OffthreadVideo and Html5 tags preserve pitch when `playbackRate` changes (the Mediabunny path does not).

### 3.4 Decoded media cache
- Shared by all `<Video>`/`<Audio>` in a render (per render, not per tag). Needed because decoding a delta frame requires its keyframe and all frames in between, and parallel rendering asks for frames out of order.
- Default budget: 50% of available memory, minimum 500 MB, maximum 20 GB (docs). Verified in bundle: explicit values must be 240 MB to 20 GB or the render is cancelled; if memory is unknown the default is 1 GB; each source's read cache is budget/16 clamped to 8 to 64 MB.
- Set with `mediaCacheSizeInBytes` on `renderMedia()`, `renderStill()`, `selectComposition()`, `renderFrames()`, `getCompositions()`, Lambda and Cloud Run APIs, or `--media-cache-size-in-bytes` on the CLI (`render`, `still`, `compositions`, `benchmark`, lambda and cloudrun variants), or in the Studio "Advanced" tab.

### 3.5 Supported media (the @remotion/media path)
- Containers: `.aac .flac .m3u8 .mkv .mov .mp3 .mp4 .ogg .wav .webm` (and MP4-family `.m4a`). Codecs: AAC, FLAC, H.264, MP3, Opus, VP8, VP9, Vorbis. Anything else falls back (video-tags comparison).
- Matroska limitation: to extract audio at minute 3, minutes 0 to 2 must be decoded too (millisecond timestamps in the container are not precise enough). Prefer `.mp4`, `.mov`, `.m4a` for distributed rendering (Lambda).
- CORS: every asset must be CORS-enabled or served via `staticFile()`.

### 3.6 ProRes (since 4.0.487)
- `npx remotion add @mediabunny/prores`, then in the entry file call `registerProresDecoder()` from `@mediabunny/prores` before `registerRoot()`.
- Multithreaded decoding only when the page is cross-origin isolated; otherwise a slower algorithm.
- ProRes 4444 `.mov` with alpha from VideoHive or Motion Array works as an overlay.

### 3.7 Media fragments (`#t=`), legacy tags only
- `<OffthreadVideo>` and `<Html5Video>` get `#t=start,end` appended automatically from the Sequence and trims (`<Video>`/`<Audio>` do not). Good for bandwidth, important on Safari mobile.
- Any change of the fragment makes the browser reload the source. Disable with your own hash (`src + '#disable'`) when you change `from`/`durationInFrames`, trims or `playbackRate` dynamically (the speed-ramp recipe does this).

### 3.8 Getting media metadata (Mediabunny)
```ts
import {ALL_FORMATS, Input, UrlSource} from 'mediabunny';
const input = new Input({formats: ALL_FORMATS, source: new UrlSource(src)});
const [seconds, track] = await Promise.all([input.computeDuration(), input.getPrimaryVideoTrack()]);
if (!track) throw new Error('Not a video file');
const [width, height] = await Promise.all([track.getDisplayWidth(), track.getDisplayHeight()]);
return {durationInFrames: Math.ceil(seconds * fps), fps, width, height};
```
- Uses `fetch()`: remote URLs need CORS. For audio, skip the track check and the size fields. Composition `durationInFrames` must be an integer (verified: only `<Composition>` rejects floats; `<Sequence>`, `<Series.Sequence>` and `<Loop>` accept fractional durations).

### 3.9 Exporting audio
- Audio-only: `npx remotion render src/index.ts my-comp out/audio.mp3` or `--codec=mp3`. Supported: `mp3`, `aac`, `wav`. `renderMedia({codec: 'mp3'})`. Lambda and Vercel: `codec: 'mp3'` plus `imageFormat: 'none'`.
- No audio: `--muted` or `muted: true` (renderMedia, renderMediaOnLambda, renderMediaOnVercel, `npx remotion lambda render --muted`).
- Audio from all video tags is included automatically.

### 3.10 `@remotion/captions` (since 4.0.216, MIT, works in browser, Node, Bun)

**`Caption`**: `{text: string; startMs: number; endMs: number; timestampMs: number | null; confidence: number | null; pageBreakAfter?: boolean}`. `timestampMs` is whisper.cpp's `t_dtw` (null or a midpoint elsewhere). `confidence` 0 to 1 or null. `pageBreakAfter` since 4.0.517 forces a page or cue break without changing timing. **Whitespace-sensitive**: put a space before each word; render with `white-space: pre`.

**`createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds, breakOnSilenceAfterMilliseconds?})`** -> `{pages: TikTokPage[]}`
- `TikTokPage = {text, startMs, durationMs, tokens: TikTokToken[]}` (`durationMs` since 4.0.261); `TikTokToken = {text, fromMs, toMs, pageBreakAfter?}` (token flag since 4.0.517). Token times are absolute ms.
- Source-verified algorithm: a new page can only start at a caption whose `text` begins with a space, and only if the current page already spans more than `combineTokensWithinMilliseconds` (`currentTo - currentFrom > limit`) or the gap to the previous caption is at least `breakOnSilenceAfterMilliseconds` (since 4.0.514; `0` means a page per word). Captions without a leading space are always glued to the previous word (so Whisper sub-word tokens like `Dr.` + `Strange` merge). If no caption has a leading space, everything becomes one page.
- `pageBreakAfter: true` ends the page after that caption.
- A page's `durationMs` runs until the next page starts (so text stays up through pauses); the last page ends at its last token's `toMs`. Page `text` is left-trimmed; the first token's text is trimmed, later tokens keep their leading space. Whitespace-only captions create no token but extend the page end.

**`parseSrt({input})`** -> `{captions}`: strips a BOM, accepts CRLF, CR, and `,` or `.` millisecond separators; a cue is a line of only digits followed by a line containing ` --> ` (spaces required). Multi-line cue text is joined with `\n`. `confidence` = 1, `timestampMs` = midpoint. Arrow text inside a cue is preserved.

**`serializeSrt({lines: Caption[][]})`** -> string: each inner array is one cue; texts are concatenated with no added spaces; start = first `startMs`, end = last `endMs` (floored to ms); `pageBreakAfter` splits a cue; empty arrays are skipped; cues are separated by a blank line, no trailing newline.

**`CaptionsInternals.ensureMaxCharactersPerLine({captions, maxCharsPerLine})`** -> `{segments: Caption[][]}` (internal, undocumented): splits every caption's text on spaces into `" word"` captions that inherit the parent's times, packs greedily by character count, and breaks early to avoid an orphan (when 2 or 3 words remain and the line is more than half full). Honors `pageBreakAfter`.

### 3.11 `@remotion/sfx`: 32 URL constants (all present in 4.0.528)

Each export is a string URL on `https://remotion.media/...wav`; use it as `<Audio src={whoosh} />`. Only 7 are CC0 and safe for client work; the other 25 are internet meme sounds from myinstants.com with **no explicit licence** (the docs disclaim responsibility).

| Export | File | Length (s) | Since | Licence |
|---|---|---|---|---|
| `whoosh` | whoosh.wav | 0.15 | 4.0.429 | CC0 (freesound) |
| `whip` | whip.wav | 0.17 (96 kHz, 24-bit) | 4.0.429 | CC0 (freesound) |
| `uiSwitch` | **switch.wav** | 0.33 | 4.0.429 | CC0 (kenney.nl) |
| `mouseClick` | mouse-click.wav | 0.40 | 4.0.429 | CC0 (freesound) |
| `pageTurn` | page-turn.wav | 0.40 | 4.0.429 | CC0 (kenney.nl) |
| `shutterModern` | shutter-modern.wav | 0.49 | 4.0.429 | CC0 (freesound) |
| `shutterOld` | shutter-old.wav | 0.31 | 4.0.429 | CC0 (freesound) |
| `ding` | ding.wav | 1.40 | 4.0.433 | meme |
| `bruh` | bruh.wav | 0.63 | 4.0.433 | meme |
| `vineBoom` | vine-boom.wav | 1.26 | 4.0.433 | meme |
| `windowsXpError` | windows-xp-error.wav | 0.99 | 4.0.433 | meme |
| `recordScratch` | record-scratch.wav | 1.26 | 4.0.465 | meme |
| `animeWow` | anime-wow.wav | 4.18 | 4.0.464 | meme |
| `boneCrack` | bone-crack.wav | 1.07 | 4.0.464 | meme |
| `dramaticBoomer` | dramatic-boomer.wav | 1.33 | 4.0.464 | meme |
| `fah` | fah.wav | 1.93 | 4.0.464 | meme |
| `illuminatiConfirmed` | illuminati-confirmed.wav | 7.84 | 4.0.464 | meme |
| `loadingLag` | loading-lag.wav | 2.69 | 4.0.464 | meme |
| `macQuack` | mac-quack.wav | 0.35 | 4.0.464 | meme |
| `minecraftHurt` | minecraft-hurt.wav | 0.37 | 4.0.464 | meme |
| `nellyAhh` | nelly-ahh.wav | 1.46 | 4.0.464 | meme |
| `ohMyGodVine` | oh-my-god-vine.wav | 1.62 | 4.0.464 | meme |
| `omgHellNah` | omg-hell-nah.wav | 4.40 | 4.0.464 | meme |
| `priceIsRightFail` | price-is-right-fail.wav | 4.52 | 4.0.464 | meme |
| `romanceMeme` | romance-meme.wav | 5.81 | 4.0.464 | meme |
| `sanctuaryGuardianWhat` | sanctuary-guardian-what.wav | 9.01 | 4.0.464 | meme |
| `skedaddle` | skedaddle.wav | 6.55 | 4.0.464 | meme |
| `snapchatNotification` | snapchat-notification.wav | 0.22 | 4.0.464 | meme |
| `spongebobFail` | spongebob-fail.wav | 3.38 | 4.0.464 | meme |
| `triggered` | triggered.wav | 0.70 | 4.0.464 | meme |
| `wilhelmScream` | wilhelm-scream.wav | 2.09 | 4.0.464 | meme |
| `yippee` | yippee.wav | 2.65 | 4.0.464 | meme |

Other sources the docs recommend: freesound.org (many CC0), kenney.nl (all CC0), soundcn.xyz (UI sounds), ElevenLabs sound-effect generation. Each page links `remotion.dev/convert?url=...` for format conversion.

### 3.12 `@remotion/media-utils` (visualization part)
- `visualizeAudioWaveform({audioData, frame, fps, numberOfSamples, windowInSeconds, dataOffsetInSeconds?, normalize?})` -> `number[]` of length `numberOfSamples` (power of two), values -1 to 1. Suited to voice. `windowInSeconds` is centred on `frame/fps`. `dataOffsetInSeconds` (4.0.268) is needed with `useWindowedAudioData()`. `normalize` (4.0.280, default false) scales the peak to 1. `frame` is a position in the audio track: subtract the audio's `from`/trim yourself.
- `createSmoothSvgPath({points: {x, y}[]})` -> SVG path string with `C` curves between points.
- From the visualization page: `useAudioData(src)` loads the whole file (memory-heavy for long files); `useWindowedAudioData()` loads a window around the current frame but only for `.wav`; `visualizeAudio({fps, frame, audioData, numberOfSamples})` gives a frequency spectrum for music bars; `getAudioData()` is the non-hook loader.
- Waveform looks: `windowInSeconds: 1/fps` (live oscilloscope), `10/fps` (sliding), and posterize by passing `frame: Math.round(frame / 3) * 3`.

### 3.13 Transcription packages

| Package | Runs | Speed | Cost | Offline | Converter | Notes |
|---|---|---|---|---|---|---|
| `@remotion/install-whisper-cpp` | Node/Bun server | fast (hardware) | free | yes | `toCaptions()` | Most accurate word timing with `tokenLevelTimestamps` (DTW) |
| `@remotion/whisper-webgpu` | browser or Node with GPU | fast | free | yes | `toCaptions()` | New (4.0.518+); language required for multilingual models |
| `@remotion/whisper-web` | browser (WASM) | slow | free | yes | `toCaptions()` | Experimental; needs cross-origin isolation |
| `@remotion/openai-whisper` | cloud API | fast | paid | no | `openAiWhisperApiToCaptions()` | Keep the API key server-side |
| `@remotion/elevenlabs` | cloud API | fast | paid | no | `elevenLabsTranscriptToCaptions()` | Keep the API key server-side |

**whisper.cpp (`@remotion/install-whisper-cpp`)**
- `installWhisperCpp({to, version, printOutput = true, signal?})` (4.0.115; `signal` 4.0.156) -> `{alreadyExisted}`. Clones and builds from source except on Windows (binary download, release tags only, none newer than 1.6.0). From 1.7.3 `cmake` is required. If the folder exists without the executable, delete it manually. Add the folder to `.gitignore`.
- `downloadWhisperModel({model, folder, onProgress?(downloaded, total), printOutput = true, signal?})` (4.0.115) -> `{alreadyDownloaded}`; saves `ggml-${model}.bin`. Models: `tiny`, `tiny.en`, `base`, `base.en`, `small`, `small.en`, `medium`, `medium.en`, `large-v1`, `large-v2`, `large-v3`, `large-v3-turbo`.
- Model footprint (TikTok template comments): tiny 75 MB disk / ~390 MB RAM, base 142 MB / ~500 MB, small 466 MB / ~1.0 GB, medium 1.5 GB / ~2.6 GB, large 2.9 GB / ~4.7 GB, large-v3-turbo 1.5 GB / ~4.7 GB (whisper.cpp 1.7.2+; the transcribe page says builds from Nov 2024 and Remotion 4.0.229+).
- `transcribe({inputPath, whisperPath, whisperCppVersion, model = 'base.en', modelFolder?, tokenLevelTimestamps, translateToEnglish = false, printOutput = true, tokensPerItem = 1, splitOnWord?, language = null, signal?, onProgress?, flashAttention?, additionalArgs?})` (4.0.131). Input must be a **16-bit 16 kHz WAV**. `tokenLevelTimestamps: true` passes `--dtw` and fills `t_dtw` (needs whisper.cpp 1.5.5+). `tokensPerItem` only when `tokenLevelTimestamps` is false (`null` = whisper's own grouping, movie-style). `splitOnWord` (4.0.208) adds `--split-on-word`. `language` (4.0.142) passes `-l`, accepts names or ISO codes including `bn`/`Bengali`, or `auto`; do not use a `.en` model for other languages or translation (use at least `medium` to translate). `onProgress` 0 to 1 and `signal` (4.0.156). `flashAttention` and `additionalArgs` such as `['-tdrz', ['--max-len', '1']]` (4.0.324). Returns `TranscriptionJson` (`systeminfo`, `model`, `params`, `result.language`, `transcription[]` with `tokens[]` holding `t_dtw`, `text`, `timestamps`, `offsets`, `id`, `p`). Prefer `t_dtw` over `offsets`.
- `toCaptions({whisperCppOutput})` (4.0.216) -> `{captions}` with leading spaces before words (example: `"William"`, `" just"`, `" hit"`) and `confidence` set. `convertToCaptions()` (4.0.131) is deprecated since 4.0.216.

**whisper-web (`@remotion/whisper-web`, unstable)**
- Requires cross-origin isolation (`Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy: require-corp`), IndexedDB and storage estimation.
- `canUseWhisperWeb(model)` -> `{supported, reason?, detailedReason?}`; reasons: `window-undefined`, `not-cross-origin-isolated`, `indexed-db-unavailable`, `navigator-storage-unavailable`, `quota-undefined`, `usage-undefined`, `not-enough-space`, `error-estimating-storage`.
- `downloadWhisperModel({model, onProgress?({progress, totalBytes, downloadedBytes})})` -> `{alreadyDownloaded}` into IndexedDB. `getAvailableModels()` sizes: tiny 77.7 MB, tiny.en 77.7 MB, base 148.0 MB, base.en 148.0 MB, small 487.6 MB, small.en 487.6 MB. `getLoadedModels()` -> downloaded models.
- `resampleTo16Khz({file, onProgress?, logLevel = 'info'})` -> mono 16 kHz `Float32Array` (Web Audio decode).
- `transcribe({channelWaveform, model, language = 'auto', onProgress?, onTranscriptionChunk?, threads = 4 (max 16), logLevel})`. Cannot run twice concurrently (second call rejects).
- `toCaptions({whisperWebOutput})`.

**whisper-webgpu (`@remotion/whisper-webgpu`)**
- `canUseWhisperWebGpu()` (4.0.518) -> reasons `window-undefined`, `webgpu-unavailable`, `webgpu-requires-secure-context`.
- `getAvailableModels()` (4.0.518): `{name, modelId, parameters, multilingual, supportsTranslation (4.0.523), webGpuDownloadSize}`; sizes `tiny`, `base`, `small`, `medium`, `large-v3-turbo`, `.en` variants up to `medium`. Models are mirrored byte-identical on `remotion.media` (faster than Hugging Face).
- `downloadWhisperModel({model, onProgress?({file, progress, loadedBytes, totalBytes}), signal? (4.0.528)})` (4.0.528) -> `{alreadyDownloaded}`; Cache API in browser, Transformers.js filesystem cache in Node.
- `isWhisperModelCached({model})` (4.0.518): models cached from Hugging Face before 4.0.522 do not count. `clearStaleModels()` (4.0.518): run at page load after upgrades. `loadWhisperModel({model, onProgress?, signal? (4.0.528)})` (4.0.518) -> `{alreadyLoaded, [Symbol.asyncDispose]}` (use `await using`). `disposeWhisperModel({model?})` frees memory, keeps files. `removeWhisperModel({model})` (4.0.523) deletes files, waits for running work.
- `resampleTo16Khz({file, onProgress?})` (4.0.518, browser). `WHISPER_WEBGPU_SAMPLE_RATE` constant for Node.
- `transcribe({channelWaveform, model, language?, task = 'transcribe', chunkLengthInSeconds = 30, strideLengthInSeconds = 5, forceFullSequences = false, doSample = false, temperature = 1, topK = 50, repetitionPenalty = 1, noRepeatNgramSize = 0, onModelLoadProgress?, signal?})` (4.0.518; `task` and sampling options 4.0.523; `signal` 4.0.528) -> `{text, words, model}`. Recommended model `small` or `small.en`. `language` is **required for multilingual models** (no auto-detection). `translate` (to English) only on multilingual non-turbo models. Word timestamps arrive only at the end (no streaming). `stride` must be below half the chunk.
- `toCaptions({whisperWebGpuOutput})` (4.0.518): word boundaries as start/end, `timestampMs` midpoint, `confidence: null`.
- Node (4.0.528): install `@remotion/whisper-webgpu @huggingface/transformers mediabunny @mediabunny/server` (docs pin 4.0.529; on this machine pin 4.0.528 to match), call `registerMediabunnyServer()`, decode with a Mediabunny `Conversion` to mono f32 at `WHISPER_WEBGPU_SAMPLE_RATE`, then download, load, transcribe, `toCaptions`. Needs a compatible GPU; Node uses `onnxruntime-node` with Dawn WebGPU; not on Linux arm64.

**OpenAI**: `openAiWhisperApiToCaptions({transcription})` (4.0.217) for `openai.audio.transcriptions.create({file, model: 'whisper-1', response_format: 'verbose_json', timestamp_granularities: ['word'], prompt?})`; it re-inserts punctuation into words.

**ElevenLabs**: `elevenLabsTranscriptToCaptions({transcript})` (4.0.443) for `POST https://api.elevenlabs.io/v1/speech-to-text` with header `xi-api-key`, form fields `file`, `model_id` (example `scribe_v2`), and **`timestamps_granularity: 'word'`** (required). Only `words[]` entries of `type: 'word'` are used (`spacing` and `audio_event` are dropped); times are seconds in the input.

### 3.14 `@remotion/video-matting` (4.0.523+)
- Purpose: split a video into an opaque **base** WebM (original, including the subject) and a **foreground** WebM with alpha (subject only), so you can put content between them ("text behind the person").
- `getAvailableModels()`: `modnet` (people, 25.9 MB, default, Apache-2.0) and `ben2-base` (general subjects, 219.1 MB, experimental, more memory, needs `shader-f16`, MIT). Mirrored on `remotion.media`.
- `canUseVideoMatting({model = 'modnet'})` -> reasons `window-undefined`, `webgpu-unavailable`, `webgpu-requires-secure-context`, `shader-f16-unavailable` (Node: failed probe returns `webgpu-unavailable` with the ONNX error). Does not check codecs.
- `downloadVideoMattingModel({model, onProgress?, signal?})` (4.0.528), `isVideoMattingModelCached({model})`, `loadVideoMattingModel({model, onProgress?, signal? (4.0.528)})` -> `{alreadyLoaded, [Symbol.asyncDispose] (4.0.528)}`, `disposeVideoMattingModel({model?})` (waits for active separations), `removeVideoMattingModel({model})`.
- `separateVideoLayers({src, model = 'modnet', audio = 'base', outputs?, videoBitrate = 'very-high', audioBitrate?, keyframeIntervalInSeconds = 1, signal?, onModelLoadProgress?, onProgress?})`:
  - `src`: string, URL or Blob (Node also local paths and `file:` URLs).
  - `audio`: `'base'` | `'foreground'` | `'both'` (duplicate audio if both play unmuted) | `'none'`.
  - `outputs.base` / `outputs.foreground`: `outputTarget: 'arraybuffer' | 'web-fs'` (default `web-fs` when available, else `arraybuffer`) or `outputWritable` (a `WritableStream<StreamTargetChunk>`; writes can be at arbitrary positions); the two options are exclusive.
  - `videoBitrate`: bits per second or `very-low` to `very-high` (higher keeps alpha edges cleaner). `audioBitrate` omitted = copy compatible Opus, else encode at `medium`.
  - `onProgress({stage: 'processing' | 'finalizing', progress, processedFrames, processedDurationInSeconds, durationInSeconds})`.
  - Returns `{base, foreground, model, width, height, durationInSeconds, processedFrames, [Symbol.asyncDispose]}`; each output has `getBlob()`, `dispose()` (call after `getBlob()` resolves) and `[Symbol.asyncDispose]` (4.0.528).
  - Output: VP9 WebM, foreground with alpha, Opus audio.
- Node (4.0.528): `registerMediabunnyServer()`; set `env.cacheDir` from `@huggingface/transformers` to choose the model cache; GPU required; no Linux arm64; typical serverless has no GPU.

### 3.15 Other APIs touched in this area
- `<Artifact filename content />` (from `remotion`): emit a file during render; the SRT recipe renders it only at frame 0; it lands in `out/[composition-id]/<filename>`.
- `useDelayRender()` -> `{delayRender, continueRender, cancelRender}`: hold rendering until captions or fonts load.
- `useRemotionEnvironment()` -> `{isRendering, isStudio, ...}`: branch between preview and render (for example, to use `<OffthreadVideo>` in preview and `<Video>` in render, or the Three.js `advance()` fix).
- `<Series>` / `<Series.Sequence durationInFrames premountFor>`: back-to-back clips; only the last may be `Infinity`; fractional durations allowed.
- In 4.0.528, `<Sequence>` itself also takes `trimBefore`, `playbackRate` (multiplies down the tree), `freeze` and `hidden` (core, see D1/D2 notes). Media inside a freeze is muted (verified).

---

## 4. Recipes

### 4.1 Full-bleed background or B-roll clip
Use the prop, not CSS: `objectFit="cover"` plus 100% size. Mute B-roll unless its sound is wanted (audio from every video tag is mixed in).
```tsx
<AbsoluteFill>
  <Video src={staticFile('city.mp4')} objectFit="cover" style={{width: '100%', height: '100%'}} muted loop />
</AbsoluteFill>
```

### 4.2 Trim and place one clip
At 30 fps: use source 12.0 s to 17.5 s, starting 3 s into the timeline. The clip then lasts 165 frames and disappears after (self-limiting).
```tsx
const {fps} = useVideoConfig();
<Video src={staticFile('interview.mp4')} from={3 * fps} trimBefore={12 * fps} trimAfter={Math.round(17.5 * fps)} />
```
The audio of a trimmed clip starts immediately at its `from`; to start sound later, move `from`, do not trim.

### 4.3 EDL: clips back to back (jump cuts, montages, multi-file edits)
```tsx
type Clip = {src: string; inF: number; outF: number; rate?: number};
const len = (c: Clip) => (c.outF - c.inF) / (c.rate ?? 1);
export const Edit: React.FC<{clips: Clip[]}> = ({clips}) => {
  const {fps} = useVideoConfig();
  return (
    <Series>
      {clips.map((c, i) => (
        <Series.Sequence key={i} durationInFrames={len(c)} premountFor={Math.round(1.5 * fps)}>
          <Video src={c.src} trimBefore={c.inF} trimAfter={c.outF} playbackRate={c.rate ?? 1} />
        </Series.Sequence>
      ))}
    </Series>
  );
};
```
- `calculateMetadata()` returns `durationInFrames: Math.ceil(sum of len)` and, for files of unknown length, Mediabunny durations (`Math.floor(seconds * fps)` per file as in the docs).
- `premountFor` of 1 to 1.5 s is only for smooth preview; renders are exact anyway.
- The old example `examples/video-with-jump-cuts` (4.0.212) instead moves one `<OffthreadVideo startFrom>` and adds `#t=0,` to avoid fragment reloads; the docs now recommend the Series + premount approach above.

### 4.4 Different sections at different speeds
Accumulate: each segment `{duration (source frames), speed}` becomes a Series item of `duration / speed` frames with `trimBefore = sum of previous source durations` and `playbackRate = speed`; the composition length is `Math.ceil(last end)`. Works with `@remotion/media`. Remember pitch rises with speed on this path.

### 4.5 Smooth speed ramp (speed changing every frame)
Not supported by `@remotion/media` `<Video>` yet. Use `<OffthreadVideo>` and integrate the speed curve: at frame `t`, start the clip at `trimBefore = round(sum of speed(i) for i = 0..t)`, set `playbackRate = speed(t)`, and move it with `<Sequence from={t}>`. Add `#disable` to the URL so the changing media fragment does not reload the file.
```tsx
const speed = (f: number) => interpolate(f, [0, 500], [1, 5], {extrapolateRight: 'clamp'});
const cum = useMemo(() => {
  const a: number[] = [];
  for (let i = 0, s = 0; i <= durationInFrames; i++) { s += speed(i); a.push(s); }
  return a;
}, [durationInFrames]);
return (
  <Sequence from={frame}>
    <OffthreadVideo src={`${src}#disable`} trimBefore={Math.round(cum[frame])} playbackRate={speed(frame)} muted />
  </Sequence>
);
```
The docs' version loops from 0 to `frame` on every frame (quadratic over a long render); precomputing as above is my optimisation. Muting and laying music separately is my recommendation (audio of a remapped clip is not discussed in the docs). The Studio timeline item moves while playing; that is expected.

### 4.6 Freeze frame (experimental, 4.0.528)
The installed types expose `freeze?: number | null` on `<Video>` (from the Sequence base props), and media inside a freeze is muted (verified). `<Video src={src} trimBefore={inF} freeze={30} />` should hold the clip's frame 30. Test with a short render before relying on it; pair it with a `shutterModern` or `whoosh` SFX and a punch-in scale for the classic "freeze + title" beat. Reverse playback is not supported by any tag; pre-render a reversed file with ffmpeg (`-vf reverse -af areverse`) instead.

### 4.7 Transparent overlays
| Source | How |
|---|---|
| WebM VP8/VP9 with alpha | `<Video src={staticFile('overlay.webm')} />` natively |
| ProRes 4444 `.mov` with alpha | register `@mediabunny/prores` (4.0.487+), then `<Video>` |
| Footage on pure black (light leaks, fire, particles) | `<Video style={{mixBlendMode: 'screen'}} />` |
| Greenscreen footage | `effects` with `colorKey()` from `@remotion/effects` (see Greenscreen page, D1) |
| Legacy | `<OffthreadVideo transparent />` |
Alpha decoding needs WebGL2; without it `@remotion/media` falls back to `<OffthreadVideo>`, whose fallback props default to `transparent: true` (verified), so alpha still works but slower. Watch the logs for the fallback warning. To export a transparent video, see D4's "Transparent videos" notes.

### 4.8 Text or graphics behind a person (video matting)
1. Offline (browser page or Node with GPU): `separateVideoLayers({src, model: 'modnet', audio: 'base'})`, then save `base.getBlob()` and `foreground.getBlob()` as `public/talk-base.webm` and `public/talk-fg.webm`.
2. Composition, bottom to top:
```tsx
<AbsoluteFill>
  <Video src={staticFile('talk-base.webm')} />
  <BigTitle />
  <Video src={staticFile('talk-fg.webm')} muted />
</AbsoluteFill>
```
Keep both layers on identical `from`/trim values. Use `ben2-base` only for non-human subjects and when `shader-f16` exists. Alpha WebM needs WebGL2 in the renderer or it falls back (still correct, slower).

### 4.9 Video as a Three.js texture
Mount `<Video headless muted onVideoFrame={...}>` inside `<ThreeCanvas>`; draw each frame into an `OffscreenCanvas`, wrap it in a `CanvasTexture`, set `texture.needsUpdate = true`, then call `advance(performance.now())` from `useThree()` while rendering (frame extraction resolves after ThreeCanvas already advanced) or `invalidate()` in preview. Using `invalidate()` during render leaves stale textures, especially with concurrency above 1. `useOffthreadVideoTexture()` and `useVideoTexture()` are deprecated for this.

### 4.10 Per-pixel manipulation
Hide the `<Video>` (`style={{opacity: 0}}`) and draw each `onVideoFrame` frame into your own `<canvas>` (for example `ctx.filter = 'grayscale(100%)'`). Preview relies on `requestVideoFrameCallback` (Chrome 83, Safari 15.4, Firefox 130). Prefer `effects` for standard looks.

### 4.11 Music bed with fades and ducking under speech
Gain in dB = 20 x log10(volume): 1 = 0 dB, 0.5 = -6 dB, 0.25 = -12 dB, 0.2 = -14 dB, 0.1 = -20 dB, 0.04 = -28 dB.
```tsx
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
// speech: [startFrame, endFrame][] relative to the music's own start
const musicVolume = (f: number, len: number, speech: [number, number][]) => {
  const fades = interpolate(f, [0, 30, len - 30, len], [0, 1, 1, 0], clamp);
  let level = 0.5;
  for (const [s, e] of speech) {
    level = Math.min(level, interpolate(f, [s - 12, s, e, e + 12], [0.5, 0.08, 0.08, 0.5], clamp));
  }
  return fades * level;
};
<Audio src={staticFile('music.mp3')} loop loopVolumeCurveBehavior="extend" volume={(f) => musicVolume(f, len, speech)} />
```
- `interpolate()` input ranges must be strictly increasing: the fade needs `len > 60` and each speech range `e > s`; guard short clips.
- Clamp **both** sides of every volume `interpolate()`. The docs' fade-in examples (`audio/volume.md`, `media/audio.md`) clamp only the left side; `interpolate()` extends to the right by default (verified), so the gain keeps climbing after the fade (2x at twice the fade time, clipping; 100x throws "Volume was set to 100 ... Did you forget to divide by 100?").
- With `loop`, use `loopVolumeCurveBehavior="extend"` so `f` keeps counting across loop iterations (the Recorder does this); `'repeat'` restarts the curve on each loop.
- Derive `speech` from caption words (merge words closer than ~0.5 s). The Recorder's own levels: music at 0.04 under talking scenes, 1.0 during title and end card scenes, 30-frame ramps.
- Crossfade two tracks: overlap two `<Audio>` for N frames; fade A out and B in. Equal-power curves (A = cos(p x pi/2), B = sin(p x pi/2)) avoid the dip of linear crossfades (general audio practice).
- Keep volume functions memoized (`useMemo`/`useCallback`) and prefer callbacks over re-rendered numbers: the Studio draws a volume curve and it is faster.

### 4.12 Sound effects on cuts and motion
- Place SFX with `from`: `<Audio src={whoosh} from={cutFrame - 3} volume={0.3} />` (a whoosh reads best when its peak lands on the cut; nudge by a few frames).
- Recorder levels: `whip` at 0.1 on scene transitions, custom shrink/grow sounds at 0.2 when the webcam changes size. SFX are sweeteners: keep them 10 to 20 dB under the voice.
- For renders that must work offline or on Lambda, copy the WAVs from `remotion.media` into `public/sfx/` and use `staticFile()`; the `@remotion/sfx` constants are remote URLs.
- Client deliverables: only the 7 CC0 sounds (whoosh, whip, uiSwitch, mouseClick, pageTurn, shutterModern, shutterOld) or your own licensed library.

### 4.13 Pitch and tone
`toneFrequency={0.8}` lowers pitch 20% without changing speed (constant per asset). Experimental idea to test by ear: counteract the pitch rise of a speed-up with `playbackRate={1.25} toneFrequency={0.8}`; otherwise use `<OffthreadVideo playbackRate>` (pitch preserved in SSR) or pre-process the audio with ffmpeg `atempo`.

### 4.14 Composition as long as a media file
Make `src` a prop, read its duration with Mediabunny in `calculateMetadata()` (section 3.8), return `durationInFrames`, `fps`, and for video also `width`/`height`. The TikTok template uses `getVideoMetadata()` from `@remotion/media-utils` for the same job (older helper).

### 4.15 Captions end to end (local whisper.cpp)
```ts
// scripts/transcribe.ts (Node or Bun), run once before editing
await installWhisperCpp({to: WHISPER, version: '1.7.2'});
await downloadWhisperModel({folder: WHISPER, model: 'medium'});
execSync(`npx remotion ffmpeg -i "${input}" -ar 16000 -ac 1 -y "${wav}"`);
const out = await transcribe({inputPath: wav, whisperPath: WHISPER, whisperCppVersion: '1.7.2',
  model: 'medium', tokenLevelTimestamps: true, splitOnWord: true, language: 'bn'});
const {captions} = toCaptions({whisperCppOutput: out});
writeFileSync('public/captions/talk.json', JSON.stringify(captions, null, 2));
```
- `npx remotion ffmpeg` is the ffmpeg bundled with Remotion (both templates use it for 16 kHz extraction and conversion). Use a non-`.en`, larger model for Bengali or any non-English speech.
- In the composition: fetch the JSON under `useDelayRender()`, `cancelRender(e)` on failure, `useMemo` the pages, then one `<Sequence>` per page:
```tsx
{pages.map((page, i) => {
  const start = (page.startMs / 1000) * fps;
  const next = pages[i + 1];
  const end = Math.min(next ? (next.startMs / 1000) * fps : Infinity, start + (MAX_PAGE_MS / 1000) * fps);
  return end - start <= 0 ? null : (
    <Sequence key={i} from={start} durationInFrames={end - start} layout="none">
      <CaptionPage page={page} />
    </Sequence>
  );
})}
```
- Inside a page: `absoluteMs = page.startMs + (frame / fps) * 1000`; a token is active when `fromMs <= absoluteMs < toMs`. Tip: to avoid the highlight blinking off in gaps between words, treat the last token with `fromMs <= absoluteMs` as active.
- Captions are whitespace-sensitive: render tokens in `<span style={{whiteSpace: 'pre'}}>` (not trimmed).

### 4.16 Caption styles that ship well
| Style | Recipe (values from official code) |
|---|---|
| TikTok bold (template-tiktok) | Pages of 1200 ms; uppercase bold display font; `fontSize = min(120, fitText({text: page.text, withinWidth: width * 0.9}).fontSize)`; white fill, `WebkitTextStroke: '20px black'` + `paintOrder: 'stroke'`; active word `#39E508`; block at `bottom: 350`, height 150 on 1080x1920; page enter spring (damping 200, 5 frames) scaling 0.8 to 1 and translating 50 px up |
| Colored words (animated-captions) | Pages of 800 ms; max width 800, max font 80, bold Montserrat; stroke width `fontSize / 7`, `paintOrder: 'stroke fill'`; active word `#18ff0e` |
| Scaling words | As colored words, plus the active word scales 1 to 1.2 with a spring over `min(4, wordFrames)` frames; `display: inline-block`, `transform: 'perspective(100px)'`, `willChange: 'transform'` to avoid subpixel jitter |
| Moving highlight pill | Measure each token with `measureText()` (with and without its leading space); a fractional word index from summed springs (damping 100, 5 frames centred on each word boundary) interpolates the pill's `left` and `width`; pill `#0B84F3`, radius 10, padding 12; pill appears scaling 0.6 to 1 |
| Boxed read-along (Recorder square) | Box with 3 px border and theme background; font 56; lines = floor((boxHeight - 50) / (56 x lineHeight)); pages paginated by real pixel width with `fillTextBox()` from `@remotion/layout-utils` (with `validateFontIsLoaded`), balanced to avoid hanging words and to break after `,` or `.`; words grey until 100 ms before `startMs`, then colour; backtick-marked words become accent-coloured monospace pills that pop 0.95 to 1; each page fades 5 frames in and out; first page appears 1 s early, last lingers 1 s |
| Classic subtitles (SRT-like) | Max 42 characters per line with orphan prevention (Recorder `calculate-srt.ts`, same logic as `ensureMaxCharactersPerLine`) |
- Always load fonts before measuring (`fitText`, `measureText`, `fillTextBox`): wrap in a `WaitForFonts` component that holds a `delayRender()` until `loadFont().waitUntilDone()` resolves.
- For Bengali, pick a font with full Bengali shaping (for example Noto Sans Bengali or Hind Siliguri from `@remotion/google-fonts`), skip `uppercase`, and check that sub-word tokens without leading spaces are glued into words before styling.

### 4.17 Captions through an edit (jump cuts, trims, speed)
Transcribe the raw file once, then map words into output time per clip:
```ts
type Cut = {inMs: number; outMs: number; startMs: number; rate: number};
const remap = (words: Caption[], cuts: Cut[]): Caption[] =>
  cuts.flatMap((c) => words
    .filter((w) => w.startMs >= c.inMs && w.endMs <= c.outMs)
    .map((w) => ({...w,
      startMs: c.startMs + (w.startMs - c.inMs) / c.rate,
      endMs: c.startMs + (w.endMs - c.inMs) / c.rate,
      timestampMs: w.timestampMs === null ? null : c.startMs + (w.timestampMs - c.inMs) / c.rate})));
```
The Recorder does the same for its SRT: each scene subtracts its trim (`startFrame / FPS * 1000`) and adds the scene's timeline offset (`scene.from * 1000 / FPS`).

### 4.18 Subtitles as files
- Export: render `<Artifact filename="subtitles.srt" content={serializeSrt({lines})} />` only when `frame === 0`; output goes to `out/[composition-id]/subtitles.srt`. Group word captions into lines with `createTikTokStyleCaptions({combineTokensWithinMilliseconds: 3000})` and map tokens back to `Caption` (`startMs = fromMs`, `endMs = toMs`, keep `pageBreakAfter`).
- Import: `fetch(staticFile('subtitles.srt'))` -> `parseSrt({input: text})` inside `useDelayRender()`. Cue-level captions have no leading spaces and whole sentences per item; do not feed them to TikTok pagination expecting word animation.
- YouTube: upload the SRT next to the video (viewers can toggle and resize). Feed platforms (X, LinkedIn): burn captions in, big, because feeds autoplay muted (Recorder policy).

### 4.19 Audiogram and music visualizers
Voice: `useAudioData(src)` + `visualizeAudioWaveform({numberOfSamples: 32, windowInSeconds: 1/fps})` -> `createSmoothSvgPath()` -> `<path strokeWidth={10} fill="none" />`, with the same audio mounted as `<Audio>`. Music: `visualizeAudio({numberOfSamples: 16 or more})` -> bars. Long files: `useWindowedAudioData()` (WAV only) and pass `dataOffsetInSeconds`. Remember to subtract the audio's `from`/trim from `frame`.

### 4.20 Silence trimming and "tightening" talking heads
- Recorder rule (from captions): start = first word's time minus 0.25 s (`ceil(fps / 4)` frames), end = last word's time plus 0.5 s (`fps / 2` frames), plus user `startOffset`/`endOffset` in frames, clamped to the file. It uses `timestampMs` (DTW) and first removes whisper filler tokens (`[PAUSE]`, `[BLANK_AUDIO]`, `[Silence]`, `[silence]`, `[INAUDIBLE]`, and `TT_<n>` tokens) and blank tokens.
- Inner jump cuts (my extension of the same idea): build keep ranges from the words, merge words separated by less than about 0.35 to 0.5 s, pad each range by about 0.1 s, then feed ranges to recipe 4.3 and captions to 4.17.

### 4.21 Loudness normalization of recordings (Recorder script)
`ffmpeg -i in -af loudnorm=I=-23:LRA=7:print_format=json -f null -` to measure each file's integrated loudness, average them, target `max(average, -20)` LUFS, then `ffmpeg -i in -af loudnorm=I=<target>:LRA=7:TP=-2.0 -c:v copy out`. It overwrites sources (commit first). The ai|coustics experiment targets -14 LUFS with a -1 dB peak limit, the usual level for social platforms.

### 4.22 Blurred background fill (vertical footage in a landscape frame)
Recorder `VideoWithBlur`: behind the fitted video, the same source at 110% size, offset -5%, `filter: blur(20px)` (oversized to hide Chrome's unblurred edges), `muted`. Both `<Video>` share one decode through the media cache. Note: the template sets `objectFit: 'cover'` through `style`, which `@remotion/media` 4.0.528 ignores; pass `objectFit="cover"` as a prop in our code.

### 4.23 B-roll overlays with rules (Recorder)
- Each B-roll: `{source, from, durationInFrames}` relative to its scene; defaults 30 and 90.
- Rule 1: it must end before the scene ends, and 15 frames earlier if the scene transitions out. Rule 2: if a later B-roll overlaps, the earlier one extends until the later one ends (no gaps showing the base).
- Landscape: opacity fade via springs (damping 200, 10 frames in and out, `opacity = appear - disappear`). Square: the base video scales down by 10% while a B-roll is shown. Video B-rolls are muted.

### 4.24 Transitions with handles
The Recorder overlaps scenes by 15 frames for a transition and, when a scene transitions in, starts its video 15 frames earlier in the source (clamped at 0) and lengthens the scene by those frames, so the transition eats extra footage (handles), not the first words. Scene enter and exit use `spring({damping: 200, durationInFrames: 15, durationRestThreshold: 0.001})`, and progress above 0.999 is rounded to 1.

### 4.25 Preparing footage (before editing)
- Convert browser or phone recordings to constant frame rate MP4 with fast start, as the Recorder does: `npx remotion ffmpeg -i in.webm -movflags +faststart -r 30 out.mp4`.
- Transcode H.265 (iPhone), AV1, AVI and other unsupported sources to H.264/AAC MP4 before use, or accept a slower fallback (never possible in client-side rendering).
- Make proxies at output resolution for 4K sources when rendering 1080p, and keep keyframes frequent for heavy-cut timelines (the decoder must start at a keyframe).
- Keep WebM/MKV audio out of Lambda renders (see 3.5).

### 4.26 The Recorder, end to end
1. `npx create-video@latest --recorder` (or `bun create video --recorder`), install Bun 1.2+, `bun i`, optionally `bun sub.ts` (installs whisper.cpp plus a 1.5 GB model), `bun run dev` (Studio on localhost:3000, recording UI on localhost:4000; hosted UI on record.remotion.dev saves to Downloads, then `bun copy.ts && bun sub.ts`).
2. Folder per composition: `public/<composition-id>/`; files `webcam<N>`, `display<N>`, `alternative1<N>`, `alternative2<N>` (`.mp4 .webm .mkv .mov`), captions `subs<N>.json`. Order = numeric suffix. `display` is used only with a matching `webcam` (the webcam then becomes a miniature); a display-only recording must be named `webcam`.
3. Edit scenes in the right sidebar props editor, save with the disk icon or Cmd/Ctrl+S. Scene types: `videoscene` (webcamPosition, startOffset, endOffset, transitionToNextScene, newChapter, stopChapteringAfterThis, music, bRolls), `title` (title, subtitle, 50 frames), `endcard` (channel, links, 200), `tableofcontents` (200), `recorder` (90).
4. Layouts `landscape` 1920x1080 and `square` 1080x1080 (9:16 is on the roadmap); FPS 30.
5. Music: `none`, `previous` (continue), `soft`, `euphoric`, `epic` (Utope tracks cleared only for Recorder videos); custom tracks go in `public/sounds` and `config/sounds.ts`; changing track crossfades.
6. Captions: edit by clicking a caption in the Studio, editing the JSON, or `config/autocorrect.ts`; mark words as monospace highlights; colour in `config/themes.ts`.
7. Render in the Studio (to `out/`), or on Lambda per platform: `bunx remotion lambda functions deploy --memory=3009` (3 vCPUs), `bunx remotion lambda sites create --site-name=remotion-recorder --enable-folder-expiry`, `bunx remotion lambda render remotion-recorder <id> --props='{"platform":"x","canvasLayout":"square"}' --delete-after="7-days"`.

---

## 5. Performance and render stability

**Decoding path**
- `@remotion/media` is the fastest path (partial downloads, WebCodecs, frame-exact). Any fallback to `<OffthreadVideo>` downloads the whole file and uses FFmpeg: slower. Grep the render log for "falling back".
- Random access costs: each frame needs its GOP decoded from the last keyframe; parallel tabs request frames out of order. Long-GOP sources (screen recordings, phone footage) and many short cuts multiply decode work; the per-render cache (50% of memory by default) absorbs repeats.
- Resolution: the canvas matches the source's intrinsic size (verified), so 4K sources in a 1080p comp cost 4K decode, memory and compositing. Use proxies.
- Several tags on the same file (blur background, matting layers, repeated B-roll) share decoded frames through the per-render cache.
- Matroska audio must be decoded from the start of the file to reach any point: prefer MP4/MOV/M4A for Lambda and long files.
- ProRes decodes faster when the page is cross-origin isolated.
- Alpha needs WebGL2 in the headless browser; without it, fallback (correct but slower).

**Memory**
- Cache budget: default 50% of available memory (500 MB to 20 GB); explicit values 240 MB to 20 GB. Lower it (`--media-cache-size-in-bytes`) when high concurrency with many or large sources runs out of memory.
- `useAudioData()` decodes the whole file into memory; use `useWindowedAudioData()` for long WAVs.
- Audio built as a data URL (Tone.js example with `audioBufferToDataUrl`) lives in memory in every tab; generate once and keep it short.

**Network**
- Remote media need CORS and stable range requests; use `requestInit={{cache: 'no-store'}}` for CDNs that break range responses. `@remotion/sfx` and HLS sources are remote: renders need network, and each render tab fetches.
- `staticFile()` assets are same-origin and safest.

**Determinism**
- Anything time-based must be a pure function of the frame (speed ramps integrate speed; no `useState` counters across frames).
- Media fragments: changing `from`/durations/trims/`playbackRate` of `<OffthreadVideo>` or `<Html5Video>` reloads the source unless the URL carries its own hash (`#disable`).
- Three.js: call `advance()` inside `onVideoFrame` during render; `invalidate()` gives stale frames with concurrency above 1.
- Volume is evaluated once per frame and applied to that frame's samples (verified): very fast fades (1 to 2 frames) can step audibly; use 6 frames or more.
- Captions and fonts: hold with `delayRender()` until the JSON and fonts are loaded; `fitText`/`measureText` on an unloaded font give wrong layouts (and `validateFontIsLoaded: true` throws instead of silently mis-measuring).

**Preview smoothness (Studio and Player)**
- `premountFor` 1 to 1.5 s before each clip (Series items, captions pages do not need it). Native buffering pauses the Player while media loads.
- Mobile browsers may block media that starts after frame 0 (autoplay policies; see the Player autoplay page, D4).
- Safari mobile depends on media fragment hints for legacy tags.

**Transcription and ML**
- Transcribe offline before rendering and store JSON; never transcribe inside a composition.
- whisper-web: one transcription at a time; `threads` up to 16. whisper-webgpu and video-matting: need a GPU; Node uses ONNX Runtime (no Linux arm64); typical serverless has no GPU; release models with `await using` or `dispose*()`.
- Video matting `videoBitrate` trades alpha edge quality against file size; `keyframeIntervalInSeconds` default 1 keeps the outputs seek-friendly.

---

## 6. Errors and fixes

| Symptom or message | Cause | Fix |
|---|---|---|
| `Cannot decode <src>, falling back to <OffthreadVideo>` (or `<Html5Audio>`) | Unsupported codec (H.265, AV1), unsupported container, CORS, alpha without WebGL2 | Transcode to H.264/AAC MP4 or VP9 WebM; serve via `staticFile()`; enable WebGL for alpha; or accept the fallback. Force failure with `disallowFallbackTo...` to catch it in CI |
| Render fails in client-side rendering with a media error | No fallback in `@remotion/web-renderer` | Use a decodable source |
| Looped video fails to render after fallback | Duration unreadable (CORS or broken container) | Fix CORS, re-mux the file |
| `Use the objectFit prop instead of the style prop.` and letterboxed video | `style.objectFit` is overridden by the prop default `contain` | `objectFit="cover"` prop |
| `Volume was set to 100, but regular volume is 1, not 100. Did you forget to divide by 100?` | Volume of 100 or more (for example a fade-in without right clamp that kept extending) | Clamp both sides; volumes are 0 to 1 (above 1 is amplification) |
| `You passed in a function to the volume prop but it returned NaN / a non-finite number / not a number` | Bad volume callback | Guard divisions and inputs |
| Distorted, clipping audio | Gain above 1 on a hot source; several loud tracks summed | Lower volumes, duck music, normalize voices |
| `The "durationInFrames" prop of the "<Composition />" ... must be an integer` | Fractional duration from seconds x fps | `Math.ceil` or `Math.floor` in `calculateMetadata()` |
| `The minimum value for the "mediaCacheSizeInBytes" prop is 240MB` / maximum 20GB | Out-of-range cache setting | Stay within 240 MB to 20 GB |
| Whole transcript shows as one caption page | Captions lack leading spaces | Prefix `" "` before each word (except glued sub-word tokens) |
| Caption spaces collapse | Missing `white-space: pre` | Add it to token spans |
| Page flashes or overlaps | Page end not limited by next page start | Use `min(nextStart, start + max)` in frames (not ms) |
| Captions out of sync after cutting | Caption times still in source time | Remap through the EDL (4.17) |
| whisper.cpp fails on input | Not a 16-bit 16 kHz WAV | `npx remotion ffmpeg -i in -ar 16000 -ac 1 out.wav` |
| `tokenLevelTimestamps` errors | whisper.cpp older than 1.5.5 | Upgrade, or set false (then `tokensPerItem` is allowed) |
| `large-v3-turbo` misbehaves | whisper.cpp build before Nov 2024 or Remotion before 4.0.229 | Use 1.7.2+ |
| Build fails for whisper.cpp 1.7.3+ | `cmake` missing | Install cmake or use 1.7.2 |
| `installWhisperCpp` returns `alreadyExisted` but nothing works | Folder exists without the executable | Delete the folder and reinstall |
| Wrong language or garbage for non-English speech | `.en` model or no `language` | Multilingual model (medium or larger) plus `language` |
| whisper-web `not-cross-origin-isolated` | Missing COOP/COEP headers | Serve with `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp` |
| whisper-web second `transcribe()` rejects | Concurrency not allowed | Queue transcriptions |
| whisper-webgpu multilingual model errors on missing language | No auto-detection | Pass `language` |
| `isWhisperModelCached` false for an already downloaded model | Hugging Face cache from before 4.0.522 | `downloadWhisperModel()` again; `clearStaleModels()` at load |
| `shader-f16-unavailable` | GPU lacks 16-bit shaders | Use `modnet` |
| `webgpu-unavailable` in Node | No GPU, driver issue, or Linux arm64 | Run on a GPU host (macOS arm64 is not excluded) |
| ElevenLabs captions empty or coarse | `timestamps_granularity` not set to `word` | Set it |
| OpenAI captions lack word timing | Missing `verbose_json` / `timestamp_granularities: ['word']` | Set both |
| Recorder: `Cannot read properties of undefined (reading 'decode') at new URLStateMachine` | Bun issue after upgrading Remotion | `rm -rf node_modules && bun i` |
| Recorder: "The file ... is a Whisper.cpp output. The file format has changed" | Old raw whisper JSON as captions | Convert with `toCaptions()` (migration gist linked in the error) |
| Three.js texture lags one frame in render | `invalidate()` only schedules | `advance(performance.now())` in `onVideoFrame` when rendering |
| Speed ramp jumps to the wrong part of the clip | `playbackRate` interpolated per frame | Integrate speed (4.5) |
| Video reloads constantly in preview (legacy tags) | Changing media fragments | Append `#disable` |

**Documentation and template drift found while reading (do not copy blindly)**
- `audio/volume.md` and `media/audio.md` fade-in examples clamp only `extrapolateLeft`; the gain then keeps growing (see 4.11).
- `recorder/editing/captions.md` shows an autocorrect using `word.word` (the old type); the current template uses `caption.text`, and both examples replace `" github"` with `" " + " GitHub"`, producing a double space.
- `recorder/external-recordings.md` shows files named `camera10.mov` while the text says the prefix must be `webcam`.
- `template-recorder` (Display, VideoWithBlur) and `template-tiktok` (OffthreadVideo) set `objectFit` via `style`; with `@remotion/media` that is ignored.
- `template-tiktok` computes the page end as `start + SWITCH_CAPTIONS_EVERY_MS` (ms added to frames); the docs version converts to frames.
- `whisper-webgpu/node.md` and `video-matting/node.md` install `@4.0.529`; this machine runs 4.0.528, and all Remotion packages must share one exact version.
- `recorder/lambda-rendering.md` passes `--props='{"platform": "youtube", "layout": "landscape"}'` in its first example, but the composition schema field is `canvasLayout` (the page's own "Our script" example uses `canvasLayout`).
- `install-whisper-cpp/transcribe.md` says `tokenLevelTimestamps` needs whisper.cpp "later than 1.0.55" in one place and 1.5.5 or later in the note; treat 1.5.5 as the minimum.

---

## 7. What our skills must teach

### 7.1 Tag choice (decision table)
| Situation | Use |
|---|---|
| Any new video or audio | `<Video>` / `<Audio>` from `@remotion/media` |
| Full-bleed or cropped framing | `objectFit` prop (`cover`), never `style.objectFit`; crop props (4.0.500+) for ratio crops |
| Speech sped up without chipmunk voice | `<OffthreadVideo playbackRate>` (server render only), or pre-process with ffmpeg `atempo`; experimental: `toneFrequency = 1 / rate` |
| Speed changing every frame | `<OffthreadVideo>` + integration recipe (4.5) |
| H.265/AV1/odd codecs you cannot transcode | Allow fallback (server render only); better: transcode |
| Client-side rendering | Only decodable sources; no fallback |
| Three.js | `<Video headless onVideoFrame>` + `advance()` |
| Alpha overlays | VP9 alpha WebM first; ProRes 4444 with the decoder; `mixBlendMode: 'screen'` for black backgrounds |

### 7.2 Timing rules
- Trims are source frames at composition fps; `trimAfter` is a position, not a length.
- Clip timeline length = `(trimAfter - trimBefore) / playbackRate`; set Series durations to exactly that; comp duration = `Math.ceil(sum)`.
- A trimmed clip disappears after its range; an untrimmed clip freezes on its last frame.
- Delay audio with `from`, not `trimBefore`.
- Children see `trimBefore + (t - from) * playbackRate`.
- Use `premountFor` of about 1 to 1.5 s on clips that start later (preview only).
- Do not animate `playbackRate` or `toneFrequency`.
- Reverse playback: pre-render a reversed file.

### 7.3 Audio mixing rules
- Volume is linear gain. Starting points: speech at 1.0; music 0.04 to 0.1 under speech and 0.5 to 1.0 when nothing is said (the Recorder uses 0.04 and 1.0; adjust to the track's mastering); SFX 0.1 to 0.3 (the Recorder uses 0.1 to 0.2).
- Every `interpolate()` used for volume clamps **both** sides.
- Use callbacks for changing volume (Studio curve, faster), memoized.
- Fade music in and out (about 1 s); duck under speech with 10 to 15 frame ramps; loop music with `loopVolumeCurveBehavior="extend"`.
- Mute B-roll and duplicate layers (blur fill, matting foreground).
- Never set volume to 100 or more; above 1 only on purpose, and check for clipping.
- Normalize voice recordings to a common loudness before mixing; aim around -14 LUFS integrated with peaks under -1 dB for social (general practice; Recorder normalizes to the average, at least -20 LUFS).

### 7.4 Captions rules
- Transcribe once, offline, into `Caption[]` JSON in `public/`; keep raw transcripts, edit copies.
- Model choice: whisper.cpp for local and multilingual work (`medium` or `large-v3-turbo` for Bengali and other non-English; `tokenLevelTimestamps: true`, `splitOnWord: true`, explicit `language`); whisper-webgpu for in-browser apps (explicit `language` for multilingual); cloud APIs only with server-side keys.
- Strip whisper filler tokens (`[BLANK_AUDIO]`, `[PAUSE]`, `[Silence]`, `[INAUDIBLE]`, `TT_n`) and blank tokens; apply a word autocorrect map for brand names.
- Keep leading spaces; render with `white-space: pre`.
- Page size: 200 to 800 ms for punchy word-by-word shorts, about 1200 ms for TikTok-style groups, 3000 ms for SRT lines; `breakOnSilenceAfterMilliseconds` about 500 to 800 ms to avoid pages spanning pauses; `pageBreakAfter` at sentence ends when needed.
- Convert ms to frames at display time; clamp each page to the next page's start.
- Fit text by measurement (`fitText`, `fillTextBox`) after fonts load; cap the font size.
- Vertical video: keep captions out of the bottom ~18% (TikTok template sits 350 px above the bottom of 1920) and away from the right-side button rail.
- After any cut, trim or speed change, remap captions through the EDL.
- Deliverables: burn in for feeds; also emit an SRT via `<Artifact>` for YouTube.

### 7.5 SFX rules
- Prefer the 7 CC0 sounds or a licensed library for client work; avoid meme sounds unless the client asks for that tone.
- Copy SFX to `public/` for offline, Lambda and reproducible renders.
- Land the transient on the visual event (cut, impact, text slam); one SFX per event; low levels.

### 7.6 Render-safety checklist (run before every media render)
1. All sources are `staticFile()` or CORS-enabled URLs; SFX local.
2. Codecs: H.264/VP8/VP9 video, AAC/Opus/MP3/FLAC audio; no H.265/AV1; ProRes decoder registered if used; alpha plan (WebGL or accepted fallback).
3. Constant frame rate footage; proxies for 4K; MP4/MOV/M4A for Lambda.
4. Composition duration is an integer from `calculateMetadata()`; Series durations match trims and rates.
5. Volume curves clamped, no value 100 or more, music ducked under speech.
6. Caption JSON and fonts gated with `delayRender()`; `white-space: pre`.
7. Render a short range first (`--frames`) and read the log for "falling back" warnings.
8. After render, check loudness and spot-check A/V sync at cuts (ideally with a video QA step).

### 7.7 Editing-model rules (from the Recorder)
- Represent an edit as data (scenes or clips in zod-validated props); derive everything else in `calculateMetadata()`.
- Transitions overlap clips; borrow handles from before the in-point so words are not covered.
- B-roll must end before the scene ends (earlier by the transition length) and earlier B-rolls stretch to cover later overlapping ones.
- Keep SFX and music decisions as functions of the scene list, not hand-placed frames.

---

## 8. Best examples to learn from

- `repo/packages/template-recorder/remotion/audio/AudioTrack.tsx`: music clips across scenes, 0.04 bed under speech, loud parts at 1.0, 30-frame ramps, loop with `extend`.
- `repo/packages/template-recorder/remotion/calculate-metadata/add-durations-to-scenes.ts`: transition overlap with handles and B-roll rules in one pass.
- `repo/packages/template-recorder/remotion/calculate-metadata/get-start-end-frame.ts`: caption-driven silence trimming with padding and offsets.
- `repo/packages/template-recorder/remotion/captions/processing/postprocess-subs.ts`: cleaning whisper output (filler tokens, blanks, autocorrect).
- `repo/packages/template-recorder/remotion/captions/processing/layout-captions.ts`: pixel-accurate caption pagination with `fillTextBox` and balanced breaks.
- `repo/packages/template-recorder/remotion/captions/boxed/components/SingleCaption.tsx`: read-along word colouring and highlighted-word pills.
- `repo/packages/template-recorder/remotion/captions/srt/helpers/calculate-srt.ts` and `EmitSrtFile.tsx`: SRT lines (42 chars) offset per scene, emitted as an artifact.
- `repo/packages/template-recorder/remotion/scenes/BRoll/*.tsx` and `layout/blur.ts`: B-roll fades, scale-down, blurred background fill.
- `repo/packages/template-recorder/scripts/convert-video.ts` and `scripts/captions/caption-file.ts`: footage normalization (CFR 30, faststart) and 16 kHz extraction plus transcription.
- `repo/packages/template-tiktok/src/CaptionedVideo/Page.tsx`: the canonical bold TikTok caption look.
- `repo/packages/template-tiktok/sub.mjs`: batch transcription of a public folder with whisper.cpp.
- `examples/animated-captions/src/AnimatedCaptions/styles/AnimatedBackground.tsx`: moving highlight pill driven by `measureText()` and summed springs.
- `examples/animated-captions/src/AnimatedCaptions/styles/ScalingWords.tsx`: per-word pop with subpixel-safe transforms.
- `repo/packages/captions/src/create-tiktok-style-captions.ts` and `src/test/tiktok.test.ts`: exact pagination semantics (leading spaces, silence breaks, forced breaks).
- `mirror/docs/videos/jumpcuts.md`: Series plus premount jump cuts with `calculateMetadata()`.
- `mirror/docs/videos/different-segments-at-different-speeds.md`: segment speed accumulation.
- `mirror/docs/videos/accelerated-video.md`: the only correct speed-ramp method (with `<OffthreadVideo>`).
- `mirror/docs/videos/as-threejs-texture.md`: headless video texture with the `advance()` render fix.
- `mirror/docs/video-matting/separate-video-layers.md`: complete options for text-behind-subject layers.
- `mirror/docs/captions/displaying.md`: minimal correct fetch, paginate, sequence and highlight flow.
- `examples/tone-js-example/src/ToneJS/index.tsx`: synthesizing audio in the browser (Tone.Offline) and feeding it to an audio tag (old API; the idea still applies).

---

## 9. Open questions

1. Do `toCaptions()` of `@remotion/whisper-webgpu` and `@remotion/whisper-web`, and `elevenLabsTranscriptToCaptions()`, emit a leading space before each word (required by `createTikTokStyleCaptions()`)? Packages not installed locally; test and normalize if not.
2. Does `<Video freeze={n}>` (present in the 4.0.528 types) hold the expected frame in both preview and render, and can a per-frame changing `freeze` value act as a time remap (reverse, ramps) for the picture? Needs a test render.
3. Does `playbackRate` plus `toneFrequency = 1 / rate` give acceptable speech on the `@remotion/media` path, and what artefacts does the pitch shifter produce?
4. Which Chromium GL setting makes alpha WebM and ProRes decode without fallback on this Mac and on Lambda (the fallback page only says WebGL is off by default)? Coordinate with D4 (chromium flags `--gl`).
5. Is the default media cache budget computed per browser tab or divided by concurrency? The bundle computes it inside each page from `remotion_initialMemoryAvailable`; high concurrency with 4K sources may need an explicit lower value.
6. Are fractional `trimBefore`/`trimAfter` values safe for `@remotion/media` (Sequence validation only requires finite numbers and non-negative `trimBefore`)? Recipes round them to be safe.
7. Does `@remotion/media` `<Audio>` accept `data:` URLs (the Tone.js pattern) as well as the legacy tag did?
8. Quality and speed of whisper.cpp versus whisper-webgpu for Bengali on this Mac Studio (M-series GPU via Dawn in Node), and which model size is the best default for Bangla client work.
9. Is `@remotion/sfx` usable offline in the Studio (remote URLs), and is there an official way to vendor the files? Current advice: copy them into `public/`.
10. The accelerated-video note says per-frame speed changes do not work with `@remotion/media` "yet": watch for a native speed-ramp API in versions after 4.0.528.
