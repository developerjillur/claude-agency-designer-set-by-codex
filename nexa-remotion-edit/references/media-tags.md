# Media tags in Remotion 4.0.528

Which tag plays a file, every prop that matters, how they fail and what to do. Checked against the installed type
definitions and bundles of 4.0.528; "verified" means we rendered it on this machine.

## 1. The three families

| | `<Video>` / `<Audio>` (`@remotion/media`) | `<OffthreadVideo>` (`remotion`) | `<Html5Video>` / `<Html5Audio>` (`remotion`) |
|---|---|---|---|
| Engine | Mediabunny + WebCodecs, draws into a `<canvas>` | FFmpeg frame extractor outside the browser, shown as `<img>` in renders, `<video>` in preview | the browser's media element |
| Frame exact | yes | yes | no (preview grade) |
| Download | partial (range requests) | the whole file first | whole (partial only when muted) |
| Speed of render | fastest | fast | medium |
| Containers | mp4 mov m4a webm mkv mp3 aac wav flac ogg m3u8 | adds avi caf flv and more | the browser's |
| Codecs | H.264 VP8 VP9, AAC Opus MP3 FLAC Vorbis (others fall back) | adds H.265 AV1 ProRes AC3 PCM | the browser's |
| CORS needed | yes (or `staticFile()`) | no | no |
| `loop` | yes | no (wrap in `<Loop>`) | yes |
| `from`, `durationInFrames` props | yes (4.0.445) | no (wrap in `<Sequence>`) | yes |
| Pitch with `playbackRate` | changes | kept in renders | kept |
| `toneFrequency` | yes (render 4.0.357, preview 4.0.520) | render only | render only |
| Client-side rendering | yes | no | no |

Default for new work: `@remotion/media`. Use `<OffthreadVideo>` for speed ramps (the only way), pitch-kept speed
changes, codecs the browser cannot decode when you cannot transcode, and alpha when the render browser has no
WebGL2. `<Html5*>` only for special preview needs.

## 2. `<Video>` from `@remotion/media`

| Prop | Default | Since | Notes |
|---|---|---|---|
| `src` | required | | `staticFile()`, CORS URL, HLS `.m3u8` |
| `from`, `durationInFrames` | 0, Infinity | 4.0.445 | like a Sequence; nests |
| `trimBefore`, `trimAfter` | none | | source frames at the composition fps; `trimAfter` is a position |
| `playbackRate` | 1 | 4.0.354 | constant; pitch follows; no reverse |
| `volume` | 1 | | number or `(f) => number`, f = frames since the media started playing |
| `loop`, `loopVolumeCurveBehavior` | false, `'repeat'` | 4.0.354 | `'extend'` keeps f counting across loops |
| `muted` | false | | may change over time |
| `objectFit` | `'contain'` | 4.0.442 | `'cover'`, `'fill'`, `'none'`, `'scale-down'`. `style.objectFit` is ignored and warns |
| `style`, `className` | | | on the canvas; `objectPosition` works |
| `cropLeft/Right/Top/Bottom` | | 4.0.500 | ratios 0 to 1 |
| `premountFor`, `postmountFor`, `styleWhilePremounted` | | 4.0.495 | preview buffering; frozen on the first frame while premounted |
| `freeze` | null | | hold at a local frame (verified: `trimBefore={45} freeze={30}` shows source frame 75); media in a freeze is silent |
| `hidden`, `name`, `showInTimeline` | | | Studio |
| `effects` | | 4.0.464 | `@remotion/effects` chain (a colour key for green screen) |
| `onVideoFrame`, `headless` | | headless 4.0.387 | a `CanvasImageSource` per frame; headless mounts no canvas (Three.js textures) |
| `toneFrequency` | 1 | | 0.01 to 2, constant |
| `audioStreamIndex` | 0 | | multi-stream files |
| `requestInit` | | 4.0.465 | `{cache: 'no-store'}` for CDNs with bad range answers; `{credentials: 'include'}` |
| `onError` | fallback | 4.0.404 | return `'fallback'` or `'fail'` |
| `disallowFallbackToOffthreadVideo` | false | | fail instead (catch unsupported files in CI) |
| `fallbackOffthreadVideoProps` | {} | | used only on fallback: `transparent` (true), `toneMapped`, `preservePitch`, `acceptableTimeShiftInSeconds`, `pauseWhenBuffering`, `useWebAudioApi`, `crossOrigin`, `onError` |
| `delayRenderTimeoutInMilliseconds`, `delayRenderRetries`, `logLevel`, `debugOverlay` | | | |

Behaviour worth knowing (read in the bundle, some verified by render):
- With `trimAfter` and no `loop`, the Video wraps itself in a Sequence of `(trimAfter - trimBefore) / playbackRate`
  frames and disappears afterwards (verified). Without `trimAfter` it holds the last frame to the parent's end.
- The canvas has the source's own size, scaled by CSS: a 4K file costs 4K decoding in a 1080p frame.
- Several tags on one file (a blurred fill and the picture) share decoded frames through the per-render cache.
- The render mixes audio at 48 kHz, evaluates `volume` once per frame, multiplies 16-bit samples and hard-clips.
  A gain of 100 or more throws ("Did you forget to divide by 100?"); a callback returning NaN or Infinity throws.

## 3. `<Audio>` from `@remotion/media`

Same timing model: `src`, `from`, `durationInFrames`, `trimBefore`, `trimAfter`, `volume`, `loop`,
`loopVolumeCurveBehavior`, `playbackRate` (Chrome 0.0625 to 16), `muted`, `toneFrequency`, `audioStreamIndex`,
`premountFor`, `postmountFor`, `name`, `showInTimeline`, `freeze`, `hidden`, `requestInit`, `onError`,
`fallbackHtml5AudioProps` (`useWebAudioApi`, `preservePitch`, `crossOrigin`, `acceptableTimeShiftInSeconds`,
`pauseWhenBuffering`, `onError`), `disallowFallbackToHtml5Audio`, `delayRender*`, `logLevel`. A trimmed audio still
starts at its `from`: delay sound with `from`, never with `trimBefore`. Remote `@remotion/sfx` files load in renders
(verified; they are peak-normalised to -3 dB).

## 4. `<OffthreadVideo>`

Props: `src`, `trimBefore`/`trimAfter` (4.0.319; the old `startFrom`/`endAt` still work but cannot be mixed),
`playbackRate`, `volume`, `muted`, `loopVolumeCurveBehavior`, `transparent` (PNG extraction for alpha, slower),
`toneMapped` (true; false is faster, duller HDR), `toneFrequency` (render only), `style`, `onVideoFrame`,
`audioStreamIndex`, `pauseWhenBuffering`, `acceptableTimeShiftInSeconds` (0.45), `useWebAudioApi`, `crossOrigin`,
`preservePitch` (preview), `delayRender*`, `onError`, `onAutoPlayError`, `name`, `showInTimeline`.
- No `from`, `durationInFrames` or `loop`: place it in a `<Sequence>`; loop with `<Loop durationInFrames>`.
- It appends a media fragment (`#t=start,end`) to the URL from its trims; when trims or `from` change every frame
  (speed ramps), add your own hash (`src + '#disable'`) or the preview reloads the file.
- It downloads the whole file before the first frame: very large files can hit the 30 s delayRender timeout.
- Verified: at 1.5x it picks the same source frame as the media `<Video>` (both floor the fractional position).

## 5. Fallback

- The media tags fall back to `<OffthreadVideo>` (video) or `<Html5Audio>` (audio) in preview and server renders
  when: the codec cannot be decoded by WebCodecs (H.265 during renders is the classic), the container is not
  supported, CORS fails, or a file has alpha and the render browser has no WebGL2.
- The log line to look for: `Cannot decode <src>, falling back to <OffthreadVideo>`. In client-side rendering there
  is no fallback: the render fails.
- A looped Video that falls back is wrapped in `<Loop>`; if the duration cannot be read, the render fails.
- Fallback changes behaviour: pitch is kept on speed changes, and the whole file downloads first.

## 6. Formats, alpha, ProRes, HLS

- Prefer MP4 (H.264 + AAC) at output size, constant frame rate, faststart, a keyframe every 1 to 2 s. Matroska
  (`.webm`, `.mkv`) audio must be decoded from the start of the file to reach any point: avoid it for long files
  and Lambda.
- Alpha: VP9 WebM with alpha plays in `<Video>` (needs WebGL2 in the renderer, else it falls back, still correct
  because the fallback defaults to `transparent`); ProRes 4444 `.mov` needs `@mediabunny/prores` registered before
  `registerRoot()` (4.0.487; faster when the page is cross-origin isolated). Footage on black (light leaks, fire):
  `mixBlendMode: 'screen'` on the tag. Green screen: an `effects` colour key.
- HLS (`.m3u8`) plays in `<Video>`; `<OffthreadVideo>` HLS is Chrome 142+ preview only.
- Remote files need CORS for `@remotion/media`; `staticFile()` files are same-origin.

## 7. The decoded-media cache

One per render (not per tag): 50 % of available memory by default, 500 MB to 20 GB; explicit values 240 MB to 20 GB
(`--media-cache-size-in-bytes`, `mediaCacheSizeInBytes` in the Node and Lambda APIs). Lower it when several renders
share a machine or concurrency is high with 4K sources.

## 8. Metadata for `calculateMetadata()`

Read duration and size with Mediabunny before the render, never inside a frame. It comes with `@remotion/media`
(1.56.1 on this install); list it in `package.json` at exactly that version if a project imports it directly.
`calculateMetadata()` runs once per render, so this is the place:
```ts
import {ALL_FORMATS, Input, UrlSource} from 'mediabunny';
export const probe = async (src: string, fps: number) => {
	const input = new Input({formats: ALL_FORMATS, source: new UrlSource(src)});
	const seconds = await input.computeDuration();
	const video = await input.getPrimaryVideoTrack();
	return {
		durationInFrames: Math.floor(seconds * fps),
		width: video ? await video.getDisplayWidth() : undefined,
		height: video ? await video.getDisplayHeight() : undefined,
	};
};
```
The composition's `durationInFrames` must be an integer; Sequences accept fractions. `getAudioDurationInSeconds()`
from `@remotion/media-utils` reads audio length without CORS.

## 9. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Letterboxed video and "Use the objectFit prop instead of the style prop" | `style.objectFit` | `objectFit="cover"` prop |
| "falling back to <OffthreadVideo>" in the log, slow render | H.265/AV1, odd container, CORS, alpha without WebGL2 | transcode to H.264/AAC MP4 (or VP9 WebM for alpha), serve via `staticFile()` |
| Render fails in the browser renderer | no fallback there | decodable sources only |
| "Volume was set to 100 ..." | an unclamped fade that kept climbing, or a 0 to 100 scale | clamp both sides; gains are 0 to 1 (above 1 amplifies) |
| "returned NaN" from `volume` | a division by 0 in the callback | guard inputs (`safeGain()`) |
| Speed ramp jumps to the wrong part | `playbackRate` interpolated per frame | integrate the speed (`SpeedRamp`) |
| Preview reloads the file every frame | changing media fragments on OffthreadVideo | `#disable` on the URL |
| Clip shows its last frame for a long time | no `trimAfter` | add `trimAfter`, or cut with `durationInFrames` |
| Sound starts late or early | used `trimBefore` to delay | use `from` |
| delayRender timeout on a big OffthreadVideo | whole-file download | the media `<Video>`, a proxy, or a longer `--timeout` |
| Stale Three.js video texture | `invalidate()` during render | call `advance(performance.now())` in `onVideoFrame` |
| Looped fallback video fails | duration unreadable | fix CORS, remux the file |
