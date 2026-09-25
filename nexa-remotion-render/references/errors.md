# Render and Studio errors, with fixes

| Symptom or message | Cause | Fix |
|---|---|---|
| Blank canvas, missing effect, black 3D scene | WebGL without a GL backend | `--gl=angle` (`swangle` without a GPU); `npx remotion gpu` |
| Text in the wrong font | font never loaded (a CSS name alone), or measured before it loaded | load through `@remotion/google-fonts`/`@remotion/fonts` (the kit does); measure after `waitUntilDone()` |
| Flicker between frames | wall-clock animation, `Math.random`, state across frames, CSS transitions | compute from the frame; `random(seed)`; render with `--concurrency=1` to confirm |
| `delayRender` timeout | an asset or data slower than 30 s per frame, or a handle never cleared | fix the path or CORS, preload, clear the handle in every branch; then `--timeout` |
| `inputRange must be strictly monotonically increasing` | keyframes from a duration shorter than the fades | guard short durations |
| Effect parameter out of range during render | an unclamped interpolation | clamp inputs to the effect's range |
| `The output directory of the image sequence cannot have an extension` | a dot anywhere in the output folder's path | a relative folder inside the project |
| Output 1 px smaller than the composition | odd size with h264, h265 or av1 | even dimensions |
| `crf and videoBitrate can not both be set` | two quality modes | keep one |
| `crf option is not supported with hardware acceleration` | CRF with a hardware encoder | video bitrate, or `if-possible` |
| `Setting the CRF to 0 with a H264 codec is not supported` | CRF 0 | 1 or more (18 is the default) |
| `yuva420p but codec ... does not support it` | alpha pixel format with h264 or ProRes | vp8/vp9 with yuva420p, or ProRes 4444 with yuva444p10le |
| `you need to set PNG as the image format` | alpha with JPEG frames | `--image-format=png` |
| Transparent ProRes is opaque | the profile flag was misspelled or the composition paints a background | `--prores-profile=4444`, no background |
| Video letterboxed | `style.objectFit` on the new `<Video>` is ignored | the `objectFit` prop |
| Audio fade keeps getting louder | a volume curve clamped only at the start | clamp both sides |
| Silent or cut-off audio | wrong trims (source frames at the composition fps), or `muted` | check `trimBefore`/`trimAfter` maths |
| Slow render with footage | sources without faststart or sparse keyframes; OffthreadVideo downloads whole files | re-encode sources: `-movflags +faststart -g 30` |
| Non-seekable media | H.264 without faststart | `npx remotion ffmpeg -i in.mp4 -movflags +faststart out.mp4` |
| Compositions list is empty in a script | `--log=error` hides the table | read it at the info level |
| `--props` ignored | shell quoting | pass a `.json` file |
| Studio values greyed out, cannot drag | non-inline styles, spreads, maths, `transform` strings | follow the editable-code rules (`studio-player.md`) |
| Easing shown read-only in Studio | a curve Studio cannot represent | `Easing.bezier`, `linear`, `spring({...})` |
| `saveDefaultProps` throws | static Studio or `zod` missing | run the local Studio; install zod |
| Player audio will not start | autoplay policy | start from a click and pass the event to `play(e)` |
| `HtmlInCanvas` error in Studio | Chrome under 149 or the flag off (preview only) | `HtmlInCanvas.isSupported()`; renders do not need the flag |
| Lambda render differs from local | fonts (no Bengali), emoji, GPU, config file ignored, unreachable assets | see `cloud.md` pre-flight |
