# Platform specs used by `qa --platform` and `watch --platform`

The values come from official pages read on 2026-09-24 (`research/R3-video-qa-techniques.md` §3.5 to §3.7). Values marked
*approx* are not published in text by the platform. They are a conservative box derived from third-party templates:
treat a hit there as a warning. Specs change: re-read the source before relying on a number for a client.

| Platform (`--platform`) | Aspect | Size | Frame rate | Length | Safe zone (top / bottom / left / right) | Source |
|---|---|---|---|---|---|---|
| Instagram Reels (`reels`) | 9:16 for full screen (1.91:1 to 9:16 allowed) | at least 720 px, 1080 best, 1440x2560 for ads | at least 30 fps | up to 20 min; over 3 min is not recommended to new audiences | 14% / 35% / 6% / 6% (Meta ads guide) | facebook.com/help/instagram/1038071743007909, facebook.com/business/ads-guide/update/video/instagram-reels |
| TikTok (`tiktok`) | 9:16 | 360 to 4096 px; ads at least 540x960 | 23 to 60 fps | 3 min for everyone, 10 min for some | *approx* 7.8% / 25.2% / 5.6% / 13% | developers.tiktok.com/doc/content-posting-api-media-transfer-guide, ads.tiktok.com/help/article/tiktok-auction-in-feed-ads |
| YouTube Shorts (`shorts`) | 9:16 or square | 1080 best | 23 to 60 fps | up to 3 min | *approx* 8% / 25% / 6% / 13% | support.google.com/youtube/answer/15424877 |
| YouTube (`youtube`) | 16:9 | 1080p recommends 8 Mbps at 24 to 30 fps, 12 Mbps at 48 to 60 fps | 23 to 60 fps | | EBU R 95 graphics safe 5% each edge | support.google.com/youtube/answer/1722171, tech.ebu.ch/docs/r/r095.pdf |
| Facebook (`facebook`) | 9:16 reels, 4:5 feed | up to 4000 px wide, sides divisible by 16 | 30 fps or lower recommended | no limit for organic reels | 14% / 35% / 6% / 6% | facebook.com/help/1041366099316573, facebook.com/business/ads-guide/update/video/facebook-facebook-reels |
| anything (`generic`) | | at least 480 px | 15 to 120 fps | | 5% each edge | |

More from the same sources:
- **Meta** (Reels and Stories ads): "H.264 compression, square pixels, fixed frame rate, progressive scan and stereo AAC
  audio compression at 128 kbps+". Stories ads also state the safe zone as 14% top and 20% bottom in pixels. Those
  pixel figures disagree with the percentages; use the percentages, which are stricter.
- **TikTok**: "Introduce your content proposition in the first 3 seconds" and "Prioritize your hook in the first 6
  seconds" (creative best practices, June 2025).
- **YouTube Shorts ads**: only "the first 60 seconds will play on the Shorts feed"; the call-to-action button appears
  at 3 s or 10 s depending on the campaign.
- **YouTube uploads**: MP4 with the moov atom at the front, AAC-LC or Opus at 48 kHz, H.264 High Profile, progressive,
  4:2:0, closed GOP of half the frame rate, BT.709 for SDR.

## Loudness

No social platform publishes a loudness target. The skill aims for -16 to -12 LUFS integrated (common practice around
-14). It notes anything between -20 and -10 and fails anything outside that range. True peak must be at most
-1 dBTP. Reference points:

| Standard | Integrated | True peak |
|---|---|---|
| EBU R 128 (broadcast) | -23 LUFS | -1 dBTP |
| EBU R 128 s2 (streaming, interim) | -20 to -16 LUFS | |
| Spotify | -14 LUFS | below -1 dBTP |
| YouTube, TikTok, Instagram | not published; about -14 in practice | about -1 dBTP |

## Captions and legibility

- Subtitles written by `transcribe`: at most 2 lines of 42 characters, each cue shown for 5/6 s to 7 s, with a gap
  of at least 2 frames between cues (Netflix Timed Text Style Guide). Adults read up to 20 characters a second.
- On-screen text should stay up for at least 1.5 s for a 30-character line (20 characters a second).
- Contrast: 4.5:1 for normal text, 3:1 for large text (WCAG 2.2, used as a proxy for burned-in text).
- Flashing: at most three flashes in any second (WCAG 2.3.1). The skill counts a flash as a pair of opposite
  whole-frame brightness jumps of 20 or more (on 0 to 255) within half a second, and flags any second with more than
  three. It is a warning, not a certification: small flashing areas can pass the screen.

## How the checks are made

- `aspect`, `resolution`, `frame rate`, `duration`, `codec`, `4:2:0 colour`, `fast start`: from ffprobe and the MP4
  box order.
- `constant frame rate`: the average and nominal frame rates differ by more than 0.5 fps.
- `loudness` and `true peak`: ffmpeg `ebur128=peak=true`.
- `black bars`: ffmpeg `cropdetect` on the measurement pass (median crop smaller than 95% of the frame).
- `text inside safe zones`: Apple Vision text boxes on 8 frames (or on the watched frames). Boxes are found for
  every script, Bengali included, even where Vision cannot read the letters.
- `reach` and `bitrate`: notes, never failures.
