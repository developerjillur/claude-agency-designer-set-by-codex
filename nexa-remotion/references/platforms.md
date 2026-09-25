# Platforms

Sizes, safe areas and settings the kit uses (`FORMATS` in `core/format.tsx`, the same numbers in `nrk.py` and in
nexa-video-creator). Safe areas are `[x, y, w, h]` in px: text and logos stay inside them.

| Format | Size | Safe area | Notes |
|---|---|---|---|
| youtube | 1920x1080 | 96, 54, 1728, 972 | 16:9; 5% margins; 30 or 60 fps (60 for screen recordings and fast motion) |
| 4k | 3840x2160 | 192, 108, 3456, 1944 | render a 1080 layout at `--scale=2`, or build at 4K with `unit` 2 |
| shorts | 1080x1920 | 65, 270, 875, 978 | clear of the title, channel row, buttons (right) and description |
| reels | 1080x1920 | 65, 270, 875, 978 | clear of the profile row, caption and buttons |
| tiktok | 1080x1920 | 65, 270, 875, 978 | clear of the caption and the right rail |
| story | 1080x1920 | 65, 270, 950, 978 | clear of the top bar and the reply box |
| feed | 1080x1350 | 54, 68, 972, 1215 | 4:5, the tallest feed shape on Facebook and Instagram |
| square | 1080x1080 | 54, 54, 972, 972 | 1:1 |

Vertical versions: build parallel compositions that share tokens and timing; restack rows into columns instead of
cropping; recompute cursor paths (horizontal sweeps become vertical scrolls); zoom punches grow downward inside the
safe area; captions sit around 60 to 65% of the height, above the platform's caption bar.

## Lengths that work

| Use | Length |
|---|---|
| Social short, reel, TikTok | 15 to 45 s; the hook in the first second; the product or payoff by 3 s |
| Ad | 6, 15 or 30 s |
| Product launch, SaaS promo | 20 to 45 s |
| Explainer | 60 to 120 s for a single idea; 2 to 8 min with chapters |
| Logo sting | 4 to 6 s: mark 0 to 0.8 s, wordmark 0.6 to 1.8 s, tagline 2 to 3.5 s, breathe, exit in the last 0.5 s |
| Web feature loop | 6 to 15 s, muted, seamless loop, frame 0 as the poster |

## Render settings (the nrk presets)

| Preset | Settings | For |
|---|---|---|
| web | H.264, CRF 18, yuv420p, bt709, JPEG frames q95, AAC 320k | YouTube and social delivery |
| draft | H.264, CRF 28, half size | a fast look |
| master | ProRes 422 HQ, PNG frames, bt709 | an editor's master |
| alpha | ProRes 4444, yuva444p10le, PNG frames | a transparent overlay for Premiere, Final Cut, Resolve |
| webm-alpha | VP9, yuva420p, PNG frames | a transparent overlay for the web or another Remotion project |
| gif | GIF, every second frame | a README or chat preview |

Every preset adds `--gl=angle` (WebGL effects, 3D and shader transitions draw nothing without it). For thin type or
flat gradients, lower the CRF (14 to 16) or use PNG frames; for text that must stay sharp after a platform
re-encodes it, render at `--scale=2`. Give every H.264 composition an opaque background.

## Loudness and audio

| Target | Integrated | True peak |
|---|---|---|
| YouTube, Instagram, TikTok, Facebook | -14 LUFS | -1 dBTP |
| Broadcast (EBU R128) | -23 LUFS | -1 dBTP |
| Podcast audiogram | -16 LUFS | -1 dBTP |

Audio renders at 48 kHz. Measure on the delivered file:
`ffmpeg -i out.mp4 -af ebur128=peak=true -f null -`.

## Captions

Burned captions for social (most people watch muted); an SRT or VTT next to the file for YouTube. At most 42
characters a line and two lines for boxed captions; 2 to 4 words a page for TikTok-style captions; about 56 px at
1080 for phones; inside the safe area, above the platform's caption bar.
