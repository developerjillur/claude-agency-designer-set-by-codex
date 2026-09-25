# Encoding reference (installed 4.0.528)

## Codecs

| Codec | Extension (others) | Audio (default first) | CRF range / default | Parallel encode | Even size forced | Hardware encoder |
|---|---|---|---|---|---|---|
| h264 (default) | mp4 (mkv, mov) | aac, mp3, pcm-16 | 1 to 51 / 18 (0 rejected) | yes | yes | macOS h264_videotoolbox |
| h265 | mp4 (mkv, hevc) | aac, pcm-16 | 0 to 51 / 23 | yes | yes | hevc_videotoolbox |
| av1 | mp4 (webm, mkv) | aac, opus, pcm-16 | 0 to 63 / 30 | no | yes | none (slow) |
| vp8 | webm (mkv) | opus, pcm-16 | 4 to 63 / 9 | no | no | none |
| vp9 | webm (mkv) | opus, pcm-16 | 0 to 63 / 28 | no | no | none |
| prores | mov (mkv, mxf) | pcm-16, aac | none | no | no | prores_videotoolbox |
| h264-mkv, h264-ts | mkv, ts | pcm-16, mp3 / aac, pcm-16 | 1 to 51 / 18 | mkv only | yes | none |
| gif | gif | none | none | no | no | none |
| mp3, aac, wav | audio files | | none | | | |

`png` is not a codec any more: use `--sequence` or a `--frames` list for PNG sequences. AV1 is not available on
Linux ARM64 GNU or on Lambda.

## Pixel formats and transparency

`yuv420p` (default), `yuva420p` (alpha, vp8/vp9 only), `yuv422p`, `yuv444p`, `yuv420p10le`, `yuv422p10le`,
`yuv444p10le`, `yuva444p10le` (alpha, with ProRes 4444). Any `yuva*` needs PNG frames. VP8/VP9 alpha automatically
adds `-auto-alt-ref 0`. The composition must not paint an opaque background; check transparency in Studio with `T`
(checkerboard). Transparent WebM can flicker at Lambda chunk boundaries.

ProRes profiles: `proxy`, `light`, `standard`, `hq`, `4444`, `4444-xq`.

## Colour space

`default` and `bt601` write no colour tags (players guess); `bt709` (4.0.28) tags BT.709 and converts to
limited-range BT.709 (real conversion since 4.0.83); `bt2020-ncl` tags BT.2020 with an HLG transfer. GIF is always
bt601. Pass `--color-space=bt709` for every video deliverable; 5.0 will make it the default. PNG frames give the most
accurate colour.

## Audio

aac (libfdk_aac), mp3 (libmp3lame), opus (libopus), pcm-16. `--audio-bitrate=320k` for finals. Everything is mixed
at 48 kHz by default (`--sample-rate`, 4.0.448). `preferLossless` picks pcm-16.

## Frames

Video frames: `jpeg` (default, fastest, no alpha; `--jpeg-quality` default 80, use 92 to 95 for finals), `png`,
`none` (audio only). Stills: `png` (default), `jpeg`, `webp`, `pdf`.

## Other flags that matter

| Flag | Default | Use |
|---|---|---|
| `--crf` | per codec | lower = better and bigger; 14 to 16 for gradients and thin type |
| `--video-bitrate`, `--max-rate` + `--buffer-size` | | instead of CRF (hardware encoders need it) |
| `--x264-preset` | medium | ultrafast to placebo; `slow` for smaller finals, `veryfast` for drafts |
| `--scale` | 1 | 0.5 drafts; 2 for sharp text or 4K from a 1080 layout (pixel count x scale squared) |
| `--every-nth-frame` | 1 | GIFs |
| `--number-of-gif-loops` | infinite | |
| `--concurrency` | half the threads, max 8 | measure with `npx remotion benchmark` |
| `--gl` | Chrome decides | `angle` for WebGL; `swangle` without a GPU; check `npx remotion gpu` |
| `--frames` | all | `0-99`, `0,30,90` (4.0.502), `0-99,150-199` joins ranges |
| `--sequence` | | image sequence into a folder (no dot anywhere in its path) |
| `--image-sequence-pattern` | `element-[frame].[ext]` | frames are zero-padded to the widest number |
| `--muted`, `--enforce-audio-track` | | drop audio, or add silence so every file has a track |
| `--log=verbose` | info | shows parallel encoding, rounding, cache sizes |
| `--timeout` | 30000 ms | per delayRender; fix slow assets first |
| `--hardware-acceleration` | disable | `if-possible` falls back to software when CRF is set |

Container details: every encode uses a 90000 timescale; MP4 and MOV are written with `faststart` (seekable in
browsers).

## Quality ladder

| Stage | Settings |
|---|---|
| Stills | `nrk.py stills` (JPEG 88 at half size) and full-size `nrk.py still` |
| Draft | `--scale=0.5 --crf=28 --x264-preset=veryfast`, or a `--frames` range |
| Review | full size, CRF 23 |
| Final | CRF 18 (16 for gradients), bt709, JPEG 95 or PNG frames, AAC 320k, 48 kHz |
| Fast final on the Mac | `--hardware-acceleration=if-possible --video-bitrate=16M` (no CRF) |
| Master | ProRes HQ (or 4444-xq), PNG frames |

## Verify the file

```bash
npx remotion ffprobe out.mp4
ffprobe -v error -show_entries stream=codec_name,pix_fmt,width,height,r_frame_rate,color_space,color_primaries,color_transfer,sample_rate -of compact out.mp4
ffmpeg -i out.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
```
