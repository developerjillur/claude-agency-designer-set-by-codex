---
name: nexa-remotion-render
description: "Rendering Remotion videos right: codec, quality and colour settings for YouTube, social, editors and the web, transparent video (ProRes 4444, WebM alpha), GIFs, stills and thumbnails, image sequences, audio-only, draft and final quality ladders, speed and concurrency, the Node render APIs, Studio and Player, AWS Lambda, Vercel and Cloud Run (with cost and safety rules), the Remotion licence, and a table of render errors with fixes. Use it whenever a Remotion render is needed, fails, is slow, looks soft or banded, has wrong colours, or must run in the cloud, Banglish included ('render koro', 'transparent video lagbe', 'render slow keno', 'lambda te render'). Part of the nexa-remotion family."
---

# Rendering Remotion videos

Settings that make the file right the first time, and fixes when it is not. Part of the nexa-remotion family (the
director skill is `nexa-remotion`; `nrk.py render` applies these presets to a kit project).

## Fast path

1. Check before rendering: `nrk.py stills PROJECT` looked at; `npx tsc --noEmit` clean; even width and height;
   every asset local (`public/`) or reachable; fonts loaded through the kit.
2. Draft: `nrk.py render PROJECT --preset draft` (half size, CRF 28), watch it.
3. Final: `nrk.py render PROJECT --preset web` (H.264, CRF 18, bt709, AAC 320k, `--gl=angle`). For a file that a
   platform will re-encode (YouTube, Vimeo), `--preset upload` (CRF 12): flat graphics at CRF 18 came out near 2 Mbps,
   and thin lines and small labels soften first in YouTube's encode (it asks about 8 Mbps for 1080p).
4. Other deliverables from the same project: `--preset master` (ProRes HQ for an editor), `alpha` (ProRes 4444 with
   transparency), `webm-alpha` (VP9 with transparency), `gif`; `nrk.py still PROJECT --frame N` for a thumbnail.
5. Verify the file: `nrk.py qa PROJECT` (platform checks), `ffprobe` (codec, pix_fmt, colour tags, size, fps,
   duration, audio), loudness (`ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`).

## Decisions

| Goal | Codec | Pixel format | Frames | Audio | Notes |
|---|---|---|---|---|---|
| YouTube, social, client MP4 | h264 | yuv420p | jpeg (q 95) | aac 320k | `--color-space=bt709`, CRF 18 (14 to 16 for gradients or thin type) |
| Smaller file for modern players | h265 | yuv420p | jpeg | aac | CRF 23 default |
| Web page with transparency | vp9 (or vp8) | yuva420p | png | opus | `.webm`; offer an opaque MP4 fallback for Safari |
| Editor overlay with transparency | prores 4444 | yuva444p10le | png | pcm-16 | `.mov`, large; the composition must not paint a background |
| Editor master | prores hq | default | png | pcm-16 | `.mov` |
| Best compression, time to spare | av1 | yuv420p | jpeg | aac or opus | much slower; not on Lambda |
| A preview in chat or a README | gif | | jpeg | none | `--every-nth-frame=2`, small size |
| Sound only | mp3, aac or wav | | none | | `--image-format=none` |
| Frames for review | any, `--sequence --frames=0,45,90` | | png or jpeg | | the output folder path must contain no dot |
| A still, a thumbnail | `npx remotion still --frame=N` | | png (graphics), jpeg (photos), webp, pdf | | `--frame=-1` is the last frame |

**Where to render**: the local Mac for client deliverables (full codec set, fonts, GPU, no bill); Lambda for many
personalised videos, batches or a SaaS feature; Vercel Sandbox only when the client's app lives there
(experimental); Cloud Run only when a client mandates GCP (alpha, unmaintained). Details: `references/cloud.md`.

## Craft rules

- **Always `--color-space=bt709`** for video deliverables: the default writes no colour tags and players guess
  (washed-out or shifted colours). nrk does it.
- **`--gl=angle`** for anything WebGL (effects, 3D, shader transitions, maps plates drawn with WebGL); `swangle`
  without a GPU; check with `npx remotion gpu`. Blank canvases are the symptom.
- **Opaque ground** on every H.264 composition (fuzzy edges otherwise); transparency only with PNG frames and an
  alpha pixel format.
- **Sharp text**: CRF 14 to 18, PNG or JPEG 95+ frames; for phone-sharp text after platform re-encoding render at
  `--scale=2`. Gradients band in 8-bit: add 2 to 4% grain, keep two stops, CRF 16.
- **Even dimensions** for h264, h265 and av1 (odd sizes are silently cut by a pixel).
- **Concurrency** defaults to half the threads, at most 8. Measure once per machine:
  `npx remotion benchmark src/index.ts Main --concurrencies=4,8,12 --runs=3`; lower it when several renders share
  the machine; `--concurrency=1` to diagnose flicker and for heavy WebGL maps.
- **Speed**: JPEG frames are fastest; parallel encoding only for h264 and h265; `--scale=0.5` for drafts; heavy
  footage is the usual bottleneck (re-encode sources with dense keyframes and `-movflags +faststart`).
- **Audio** renders at 48 kHz; master loudness is measured on the file (see `nexa-remotion-edit`).
- **Node APIs ignore `remotion.config.ts`**: pass codec, CRF, pixel format, colour space, GL and every other option
  explicitly; pass `inputProps` to both `selectComposition` and `renderMedia`.
- **Versions**: `remotion` and every `@remotion/*` package exactly the same (4.0.528 here); add packages with
  `npx remotion add`.

## Recipes

Transparent lower third for an editor (in the project):
```bash
python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py render PROJECT --comp LowerThird --preset alpha
```

Only some frames, as PNGs, for a review sheet (the folder is relative, so no dot in the path):
```bash
npx remotion render src/index.ts Main out/review --sequence --frames=0,45,90,300 --image-format=png --gl=angle
```

A render from Node with the same settings as the CLI:
```ts
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const composition = await selectComposition({serveUrl, id: 'Main', inputProps});
await renderMedia({composition, serveUrl, codec: 'h264', crf: 18, colorSpace: 'bt709', imageFormat: 'jpeg',
	jpegQuality: 95, audioBitrate: '320k', chromiumOptions: {gl: 'angle'}, outputLocation: 'out/main.mp4', inputProps});
```

A fast final on the Mac's hardware encoder (bitrate, not CRF):
```bash
npx remotion render src/index.ts Main out/main.mp4 --hardware-acceleration=if-possible --video-bitrate=16M --color-space=bt709 --gl=angle
```

## Remotion 4.0.528 facts and traps

- `--frames=0,30,90` renders just those frames; `--frames=0-99,150-199` joins ranges into one video (4.0.502).
- Default CRF: h264 18 (1 to 51, 0 rejected), h265 23, vp8 9, vp9 28, av1 30; no CRF for ProRes and GIF; CRF and
  video bitrate cannot both be set; hardware encoding refuses CRF.
- `yuva420p` only with vp8/vp9; `yuva444p10le` with ProRes 4444; any alpha format needs PNG frames. The ProRes
  profile option is `--prores-profile` (a typo silently drops the alpha).
- Image sequences refuse an output folder whose path contains a dot anywhere ("cannot have an extension"): render
  into a relative folder inside the project.
- `remotion compositions --log=error` hides the table; one-frame compositions are listed as `Still`.
- The v5 defaults (bt709, premounting, required font weights, Lambda disk 10240 MB) are not active on 4.0.528: set
  them explicitly.
- Current Remotion needs macOS 15 or later; Linux needs glibc 2.35+.
- Licence: free for individuals and companies of up to 3 people. A company of 4 or more needs a Company License:
  seats for people (and agents) making videos in Studio; per-render pricing ($0.01 a render, $100 a month minimum)
  for automation such as render pipelines or an embedded Player. An agency delivering only video files counts only
  its own headcount. State the facts; do not give legal advice.

## References

- `references/encoding.md`: every codec, pixel format, colour space, audio codec, preset and the quality ladder.
- `references/errors.md`: render and Studio errors with causes and fixes.
- `references/cloud.md`: Lambda, Vercel Sandbox and Cloud Run: decisions, defaults, costs, safety, debugging.
- `references/studio-player.md`: the Studio as an editor, the Player in apps, client-side rendering, codemods.
- Depth: `~/.claude/skills/nexa-remotion/references/kb/D4-render-studio-player.md` and `D3-lambda-cloud.md`.
