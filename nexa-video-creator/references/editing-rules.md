# Editing rules

The craft rules nexa-video-creator applies, from research done on 2026-09-25 (official platform documentation, published standards, peer-reviewed studies and practitioner sources). Every number carries a source tag `[S#]` (list at the end) and a confidence tag: **[H]** official or peer-reviewed, **[M]** reputable secondary or several agreeing practitioners, **[L]** a single practitioner source, **[D]** derived here (a tunable default). The compiler enforces the rules it can measure; the rest guide the plan.

### 1.1 Master spec table

| Format | Aspect and canvas | Frame rate | Max length | Deliver loudness | Sources |
|---|---|---|---|---|---|
| YouTube long-form | 16:9. 1920x1080 minimum; upload 2560x1440 or 3840x2160 when the source allows | Native: 24, 25, 30, 48, 50 or 60. Never conform | 12 h or 256 GB, whichever is less (15 min until the account is verified) [H] | -14 LUFS integrated, true peak at most -1 dBTP [M] | S1, S3, S42, S43 |
| YouTube Shorts | 9:16 or 1:1, 1080x1920 | Native, usually 30 or 60 | 3 min for uploads after 2024-10-15 [H] | as above | S2 |
| Instagram Reels | 9:16, 1080x1920. Meta's ads guide now recommends 1440x2560 for Reels ads [H] | At least 30 fps (Instagram Help, via secondary) [M] | 3 min in app since January 2025 [H]; Reels ads 0 s to 15 min [H] | as above; Meta publishes no target [M] | S18, S25, S30 |
| Instagram and Facebook Stories | 9:16, 1080x1920 (ads 1440x2560) | 30 typical | 60 s per story card since 2023 [M]; ads 1 s to 60 min, and ads under 16 s play on one card [H] | as above | S19, S28 |
| Instagram feed posts | 4:5 1080x1350, or 3:4 1080x1440; the profile grid shows a 3:4 crop [M] | - | Treat video posts as Reels for spec purposes [D] | - | S29 |
| Facebook feed | 4:5, 1440x1800 recommended for feed video ads [H] | Fixed | Ads 1 s to 241 min [H]. Since June 2025 every Facebook video is a Reel, with no length or orientation limit [H] | as above | S20, S22 |
| Facebook Reels | 9:16, 1080x1920 (1440x2560 for ads) | Fixed | as above | as above | S18, S22 |
| TikTok | 9:16, 1080x1920 | 30; 60 for fast motion [M] | 10 min recorded in app; up to 60 min upload in a limited test [M] | as above; no published target | S40 |
| TikTok In-Feed ads | 9:16 preferred (1:1 and 16:9 accepted), minimum 540x960 | - | 5 to 60 s; bitrate at least 516 kbps; file up to 500 MB; ad text 12 to 100 characters [M] | as above | S31 |
| YouTube ads | Any; vertical for Shorts | - | Skip button at 5 s, under 3 min recommended; non-skippable 15 to 60 s by campaign subtype; bumpers 5 to 6 s; Shorts ads under 60 s recommended [H] | as above | S11 |

### 1.2 Export presets

**Master encode (all platforms), from YouTube's upload recommendations [S1][H]:** MP4 container with the moov atom at the front (fast start) and no edit lists; H.264 High profile, progressive, 2 consecutive B-frames, closed GOP of half the frame rate, CABAC on, variable bitrate, 4:2:0 chroma. SDR colour tagged BT.709 for primaries, transfer and matrix (YouTube converts unsupported spaces to 8-bit BT.709). Audio AAC-LC at 48 kHz; mono 128 kbps, stereo 384 kbps, 5.1 at 512 kbps. Meta requires stereo AAC at 128 kbps or more, square pixels, fixed frame rate, progressive scan [S18][H].

**YouTube SDR bitrates [S1][H]**

| Resolution | 24, 25, 30 fps | 48, 50, 60 fps |
|---|---|---|
| 2160p | 35 to 45 Mbps | 53 to 68 Mbps |
| 1440p | 16 Mbps | 24 Mbps |
| 1080p | 8 Mbps | 12 Mbps |
| 720p | 5 Mbps | 7.5 Mbps |

HDR 1080p is 10 and 15 Mbps; HDR 2160p is 44 to 56 and 66 to 85 Mbps [S1][H].

**Vertical social preset [D]:** 1080x1920, native frame rate, H.264 High, 2-pass VBR at 10 to 16 Mbps (above YouTube's 8 and 12 Mbps figures because every platform re-encodes), AAC 48 kHz at 320 kbps or more. Deliver 1440x2560 for Meta ads when the source allows [S18].

**Frame rate rules:** encode at the recorded rate and deinterlace first (for example 1080i60 becomes 1080p30) [S1][H]. Mixed-rate footage goes into a timeline at the dominant camera rate. Lighting flicker note (general engineering knowledge, not sourced here): footage shot at 30 or 60 fps under 50 Hz mains lighting can flicker; the QC pass should flag banding or flicker rather than assume a region.

### 1.3 Safe zones in pixels

| Platform, placement | Top | Bottom | Left | Right | Source, confidence |
|---|---|---|---|---|---|
| Instagram and Facebook Reels, and Stories (Meta ads guide) | 14% = 269 px | 35% = 672 px | 6% = 65 px | 6% = 65 px | S18, S19 [H] |
| Same rule at 1440x2560 | 358 px | 896 px | 86 px | 86 px | [D] |
| TikTok (In-Feed) | 130 px | 484 px | 44 px | 140 px | S35 [M]. TikTok states the safe area shrinks as the ad caption gets longer [M] |
| YouTube Shorts ads (Google) | 10% = 192 px | 25% = 480 px | not stated | 10% = 108 px | S9 [H] |
| YouTube Shorts organic, measured | about 170 px | about 330 px (about 400 px with the description expanded) | about 50 px | about 120 px | S95 [L] |
| **Universal 9:16 safe rectangle** (intersection of all rows) | **270 px** | **672 px** | **65 px** | **140 px** | [D] |

The universal rectangle is **x 65 to 940, y 270 to 1248 (875 x 978 px)** on 1080x1920. Anything that must be read (hook text, captions, prices, CTA, logo) goes inside it when a video will be cross-posted. Meta also consolidated Stories and Reels safe zones into one standard in March 2026 per a secondary source [S24][M]; the Meta ads guide pages fetched on 2026-09-25 show the same 14% / 35% / 6% for both, which is consistent.

**16:9:** EBU R95 action-safe is 3.5% per side and graphics-safe 5% per side [S80][H], so graphics sit inside x 96 to 1824, y 54 to 1026 on 1920x1080 [D]. Keep lower thirds and burned-in text above y 918 (the bottom 15%) so player controls and viewer-enabled closed captions do not cover them [D].

**4:5 feed:** use a 5% inset (54 px) [D from S80]. For Instagram, the grid preview crops a 4:5 post to 3:4, trimming about 67 px of width in total, so logos and faces stay near the centre [S29][M].

### 1.4 Caption and text placement per format

- **9:16, cross-posted:** caption block centred horizontally; top edge at or below y 960, bottom edge at or above y 1248; nominal caption centre y 1100 to 1150 (57% to 60% of height) [D from 1.3]. TikTok-only exports may sit lower, with the bottom edge up to y 1436 [D].
- **9:16 hook or title text:** band y 270 to 520 [D].
- **Faces:** never put text over the eyes or mouth. If the face occupies the caption band, move captions to the top band [D]. BBC guidance for vertical video: subtitles sit a little higher than in landscape, still in the lower third, because faces usually fill the upper half [S58][H].
- **16:9 long-form:** sentence subtitles bottom-centred inside graphics-safe; at most 2 lines; line length at most 68% of frame width (1306 px); line height 8% of frame height (86 px) [S58][H]. Upload an SRT or VTT caption track as well (see 4.3).
- **4:5 feed:** captions in the lower third inside the 5% inset; do not cover the product [D].
- The practitioner "Hormozi" spec places captions at y 1150 to 1350 [S63][L]. That overlaps Meta's bottom 35% (y above 1248), so for anything that runs on Reels or Stories keep the caption's bottom edge at or above y 1248 [D].

### 1.5 Loudness targets

| Destination | Integrated loudness | True peak | Notes | Source |
|---|---|---|---|---|
| YouTube (long-form and Shorts) | -14 LUFS | at most -1 dBTP | YouTube turns content louder than its reference down and does not turn quieter content up; the reference is widely measured at about -14 LUFS | S42 [H for the behaviour], S43 [M for the number] |
| TikTok, Instagram, Facebook | -14 LUFS default | at most -1 dBTP | Normalisation exists but targets are not published | [M] |
| Podcast-style video also going to Apple Podcasts | -16 LKFS, plus or minus 1 dB | at most -1 dBFS | Measured to ITU-R BS.1770-5 | S46 [H] |
| Audio streaming (AES TD1008) | speech -18 LUFS (dialog-gated), music -16 LUFS; keep above -20 LUFS | at most -1 dBTP at the codec input | Explicitly not intended for sound-with-picture | S41 [H] |
| Broadcast deliverables | EBU R128 -23 LUFS; ATSC A/85 -24 LKFS | per spec | iZotope quotes broadcast -23 to -25 LKFS | S44, S50 [H] |
| Netflix-style long-form | -27 LKFS dialog-gated, plus or minus 2 LU | at most -2 dBTP | | S47 [H] |

Default rule: every social or YouTube master is **-14 LUFS integrated (plus or minus 1 LU) with true peak at most -1.0 dBTP**, measured per BS.1770 on the final mix [S43][M] [S41][H]. Mastering louder gains nothing on YouTube because loud content is turned down [S42]. Speech-heavy tutorials may sit at -14 to -16 LUFS.
### 1.6 Platform rules that change editing decisions

- **Shorts classification:** 3 min or less and square or vertical; use 16:9 to avoid Shorts classification [S2][H].
- **Shorts views:** since 2025-03-31 a view counts every time a Short starts or replays; the older threshold-based count survives as "engaged views" and still drives YouTube Partner Program revenue [S14][M]. Loops therefore raise views.
- **Shorts music:** most YouTube audio library songs may be used for up to 90 s in a Short, some only 60 or 30 s [S2][H]. From 2026-09-24, Shorts between 1 and 3 min with an active Content ID claim are no longer auto-blocked and may stay playable [S2][H].
- **Mid-rolls:** available on monetised videos of 8 min or more; slots at natural breakpoints (a pause in audio or a visual transition) are more likely to serve, mid-sentence slots less likely [S4][H]. The editor should create clean breakpoints.
- **Chapters:** the first timestamp is 00:00; at least 3 timestamps in ascending order; each chapter at least 10 s [S5][H].
- **End screens:** only in the last 5 to 20 s; video must be at least 25 s; up to 4 elements on 16:9; viewers can hide them [S6][H].
- **Audience retention "intro" metric:** the share of viewers still watching after 30 s; key moments need a video of at least 60 s and 100 views [S7][H].
- **AI disclosure:** YouTube requires disclosure of realistic altered or synthetic content (since March 2024) [S16][H]; TikTok requires labels on realistic AI-generated content [S37][H]; Meta requires disclosure of photorealistic digitally created or altered content in social issue, electoral or political ads (announced 2023-11-08, effective 2024-01-11; label renamed "AI info" on 2026-02-19) [S23][H]; the EU AI Act Article 50 deepfake disclosure applies from 2026-08-02, with lighter disclosure for evidently artistic, creative, satirical or fictional works [S86][H].
- **Originality:** YouTube's "inauthentic content" rule (renamed 2025-07-15) keeps templated, mass-produced content with minimal variation out of monetisation [S17][M]; TikTok's For You feed excludes unoriginal re-uploads without new creative edits, content carrying other platforms' watermarks or logos, QR codes, and very short clips or static images [S36][H]; Instagram replaces identical reposts with the original in recommendations and stops recommending aggregator accounts to non-followers [S27][M]. The skill must vary templates per client, add real authorial input, and never leave another app's watermark in frame.
- **Instagram ranking:** watch time, likes per reach and sends per reach are the three most important signals (Mosseri, January 2025) [S26][M].
- **Music rights:** Meta Reels ads cannot use licensed music (original audio or Meta Sound Collection only) [S18][H]; TikTok business accounts must use the Commercial Music Library [S38][M].
- **TikTok monetisation:** only videos of at least 1 minute earn Creator Rewards [S39][H].

### 1.7 Length guidance (what to aim for, not the maximum)

| Format | Guidance | Evidence |
|---|---|---|
| YouTube long-form | Let content decide. At least 8:00 unlocks mid-rolls [S4][H]. MrBeast's last-100-video average was 818 s (13:37) [S67][M] | S4, S67 |
| Tutorials | Segment into chunks under 6 min; tutorial viewers engaged for only 2 to 3 min regardless of length, so chapter every step [S65][H] | S65 |
| YouTube Shorts | 15 to 60 s default; up to 3 min allowed [S2][H]; Shorts ads under 60 s [S9][H] | [D] default |
| Instagram Reels | 15 to 60 s default; industry analyses suggest 7 to 15 s for trend formats and 30 to 90 s for value content [L] | S25, [L] |
| TikTok | 21 to 60 s default; 60 s or more when the creator monetises through Creator Rewards [S39][H] | [D] default |
| Stories | 5 to 15 s per card [L] | [L] |
| Ads | See 6.3 | |

---
### 2.2 The first 1 to 3 seconds

**Evidence**

- TikTok: more than 63% of the highest-CTR videos show their key message or product in the first 3 s [S34][M]; 90% of an ad's recall impact is captured in the first 6 s [S33][M]; secondary sources add that about 50% lands in the first 2 s [L].
- TikTok 2021 conversion analysis: on-screen text appearing within the first 7 s gave a 43% conversion lift in gaming ads [S32][M].
- YouTube's own hook advice: ask a question, brand with energy, tell viewers within 5 s what they will get, or cold-open into the action [S8][H, dated 2014].
- MrBeast: the first minute loses the most viewers (one video lost 21 million of 60 million viewers in minute one, which the team considered good); front-load the interesting material and match the thumbnail's promise [S67][M].
- 1of10 (2025): 0 to 5 s grab attention, 5 to 15 s clarify the promised value, 15 to 30 s set context or start the story; above 70% retention at 30 s is solid, above 80% exceptional, below 50% at 10 to 15 s means the hook failed [S94][L].
- Curiosity is driven by a perceived gap in knowledge (information-gap theory), strongest when the viewer knows a little but not the answer [S70][H].

**Hook production rules (applied automatically)**

| ID | Rule | Number | Source |
|---|---|---|---|
| H1 | Frame 0 shows the subject (face, product, result). Never open on black, a logo sting, or a slow establishing shot | 0 s | S67 [M], [D] |
| H2 | Trim pre-roll so the first spoken word or key action starts by 0.5 s | at most 0.5 s | [D] |
| H3 | Put a 3 to 7 word text hook on screen from frame 0, held at least 0.35 s per word plus 0.5 s | 7 words: at least 2.95 s | S58 [H], [D] |
| H4 | State or show the payoff promised by the title or thumbnail within 5 s (long-form) or 3 s (short-form and ads) | 5 s / 3 s | S8 [H], S34 [M] |
| H5 | Add an audio hook in the first 0.3 s: a voice line, SFX hit or music downbeat. TikTok treats itself as sound-on | 0.3 s | S33 [M], [D] |
| H6 | Ads: product or brand visible in the first 3 s; value proposition inside 6 s | 3 s / 6 s | S12 [H], S33 [M] |
| H7 | If the title promises X, the first 30 s must visibly move toward X (no unrelated intro, no channel trailer) | 30 s | S7 [H] |

**Hook types**

| # | Type | Template | Generic example | Edit treatment | Best for | Source |
|---|---|---|---|---|---|---|
| 1 | Result first | "Here is [result]. Here is how." | Finished room on screen: "This took $300 and one weekend." | Open on the final frame, text hook, then cut to the start | Tutorials, transformations, product | S8, S94 |
| 2 | Cold open | Most intense moment first, then rewind | The car will not start; card "3 days earlier" | 2 to 5 s best-moment clip, rewind SFX, title card | Vlogs, stories, challenges | S8, S94 |
| 3 | Curiosity question | "Why does X happen?" | "Why do most short videos lose people at second 3?" | Question as text, punch-in on the key word | Education, explainers | S8, S70 |
| 4 | Problem call-out | "If you [problem], watch this." | "If your videos sound quiet on phones, this is why." | Tight face, highlight the problem word | Tutorials, problem-solution ads | S94 |
| 5 | Contrarian or mistake | "Stop doing X." | "Stop exporting talking heads at 60 fps." | Red cross graphic, record-scratch SFX | Education, ads | S94 |
| 6 | Stakes or challenge | "If I lose, ..." | "24 hours to edit 10 videos." | Countdown overlay, fast progression | Entertainment | S67, S94 |
| 7 | Visual pattern interrupt | Unexpected motion in frame 0 | Phone dropped into water in the first frame | No intro, splash SFX, 0.5 s slow motion | Ads, product | S33 |
| 8 | Demonstration first | Product working in frame 0 | One wipe removes a stain | Macro close-up, "watch" text | Ads, product promos | S33, S12 |
| 9 | Audience call-out | "[Audience], this is for you." | "Freelance editors: copy this caption setup." | Name the audience in text | Niche content | [L] |
| 10 | Proof or authority | "After [credential], ..." | "After editing 1,000 ads, three hooks win." | Big number emphasis | Education, ads | [L] |
| 11 | Sound hook | A distinctive sound first | A crisp crunch, or a licensed trending audio drop | Audio leads, caption follows | TikTok, Reels | S33 |
| 12 | In the middle of the story | "So I just ..." | "So I just locked myself out of my car, on camera." | Selfie framing, jump cuts | UGC, vlogs | [L] |
### 4.7 Bengali (and other Indic scripts)

| ID | Rule | Source |
|---|---|---|
| BN1 | Render only with HarfBuzz shaping: FFmpeg drawtext from version 6.1 needs libharfbuzz (built with libfreetype, libharfbuzz, libfribidi; `text_shaping=1` is the default when supported); libass 0.15.0 or later (HarfBuzz mandatory); browser-based renderers (Chrome, Remotion, HyperFrames) shape correctly | S83, S84 [H] |
| BN2 | QC: render a conjunct test line such as "ক্ষ ত্র জ্ঞ স্ত্র ন্দ্র রূপ হৃদয় শ্রী" and fail the render if dotted circles (◌) or detached vowel signs appear | [D] |
| BN3 | Fonts with full conjunct coverage: Noto Sans Bengali (variable weights and widths, 695 glyphs), Hind Siliguri (5 weights), Anek Bangla (variable), Baloo Da 2 (variable), Tiro Bangla, Noto Serif Bengali; Galada and Atma for display only. Netflix specifies Vrinda for Bangla subtitles | S85 [M], S55 [H] |
| BN4 | No uppercase exists: emphasis by colour, weight and a pop of at most 105%, never by case | S82 [H], [D] |
| BN5 | Style whole words only. Styling part of a syllable (for example half of বি) breaks vowel-sign positioning, so karaoke wipes must advance word by word | S81 [H] |
| BN6 | No letter-spacing (tracking) on Bengali: it splits conjuncts and breaks the headline (matra) | S81, S82 [H] |
| BN7 | Line height larger than for Latin (vowel signs sit above and below); start at 1.3x to 1.5x the Latin line height | S82 [H qualitative], numbers [D] |
| BN8 | Thinner stroke than Latin (about 5% to 7% of font size instead of about 10%) or a soft shadow or box, because thick outlines fill the counters of conjuncts; check visually | [D] |
| BN9 | Break lines only at spaces; a danda (।) or closing bracket never starts a line; no space before punctuation; use the single ellipsis character (U+2026) | S82, S55 [H] |
| BN10 | Reading speed at most 22 cps (adult) or 18 cps (children); at most 42 characters per line; at most 2 lines | S55 [H] |
| BN11 | Numerals: follow the client's convention. Netflix spells out 1 to 10 in Bangla and uses numerals from 11 | S55 [H] |
| BN12 | No italics in Bangla subtitles; use quotation marks for titles | S55 [H] |
| BN13 | Mixed Bengali and English words (Banglish): pick a family with matching Latin glyphs, or pair fonts with matched x-height; align visually because Bengali hangs from its headline | S81 [H], [D] |
| BN14 | Word-by-word captions: Bengali words are often long after inflection, so allow 1 to 2 words per caption and keep a caption at or under about 18 to 22 characters | [D] |
| BN15 | Size: many Bengali fonts look smaller than Latin caps at the same em size; start about 10% to 15% larger than the Latin caption size and check on a phone | [D, uncertain] |
| BN16 | ASR word timestamps for Bengali are less reliable than for English: verify alignment on a sample and re-time so each word appears within 1 to 2 frames of its audio | S57 [H], [D] |

---
## 10. Master rules table

One row per rule. Numbers are defaults the skill applies automatically; confidence per the legend.

| ID | Applies to | Rule | Number(s) | Source | Conf. |
|---|---|---|---|---|---|
| FMT-01 | YouTube long-form | 16:9; upload 1440p or 2160p when the source allows | 1080p SDR 8 / 12 Mbps; 2160p 35-45 / 53-68 Mbps | S1 | H |
| FMT-02 | All | Keep native frame rate; never conform; deinterlace | 24/25/30/48/50/60 fps | S1 | H |
| FMT-03 | All | H.264 High, 2 B-frames, closed GOP = fps/2, CABAC, 4:2:0, MP4 fast start, BT.709 tags | - | S1 | H |
| FMT-04 | All | AAC-LC 48 kHz; stereo 384 kbps (YouTube), at least 128 kbps (Meta) | 48 kHz | S1, S18 | H |
| FMT-05 | Shorts | 9:16 or 1:1 and at most 180 s is a Short | 180 s | S2 | H |
| FMT-06 | Shorts | YouTube audio library music at most 90 s per Short | 90 s | S2 | H |
| FMT-07 | Reels | 9:16; organic at most 3 min; Reels ads up to 15 min; 1440x2560 for ads | 180 s | S25, S18 | H |
| FMT-08 | Stories ads | Keep under 16 s so the ad plays on one card | 16 s | S19 | H |
| FMT-09 | Facebook feed ads | 4:5 at 1440x1800 | - | S20 | H |
| FMT-10 | TikTok | At least 60 s when the creator earns through Creator Rewards | 60 s | S39 | H |
| FMT-11 | TikTok ads | 5 to 60 s; at least 540x960; at least 516 kbps; at most 500 MB | - | S31 | M |
| FMT-12 | Instagram feed | Keep key content inside the centre 3:4 of a 4:5 post | about 67 px trimmed | S29 | M |
| SAFE-01 | Meta Reels and Stories | Clear top 14%, bottom 35%, sides 6% | 269 / 672 / 65 px | S18, S19 | H |
| SAFE-02 | TikTok | Clear top 130, bottom 484, left 44, right 140 px | - | S35 | M |
| SAFE-03 | Shorts | Clear top 10%, bottom 25%, right 10% | 192 / 480 / 108 px | S9 | H |
| SAFE-04 | Any 9:16 cross-post | Critical text inside x 65-940, y 270-1248 | 875 x 978 px | SAFE-01 to 03 | D |
| SAFE-05 | 16:9 | Graphics inside a 5% inset (action-safe 3.5%) | x 96-1824, y 54-1026 | S80 | H |
| LOUD-01 | YouTube and social | Master -14 LUFS plus or minus 1 LU, true peak at most -1 dBTP | -14 / -1 | S43, S41 | M |
| LOUD-02 | YouTube | Never master louder than the target; loud content is only turned down | - | S42 | H |
| LOUD-03 | Podcast-style | -16 LKFS plus or minus 1, true peak at most -1 dBFS | - | S46 | H |
| LOUD-04 | Broadcast, streaming TV | EBU -23 LUFS, ATSC -24 LKFS, Netflix -27 dialog-gated with true peak at most -2 | - | S44, S50, S47 | H |
| HOOK-01 | Short-form, ads | Key message or product visible by 3 s | 3 s | S34 | M |
| HOOK-02 | Ads | Value proposition inside 6 s | 6 s | S33 | M |
| HOOK-03 | Long-form | Show or say what the video delivers within 5 s; match title and thumbnail | 5 s | S8, S7 | H |
| HOOK-04 | All | Frame 0 shows the subject; first word or action by 0.5 s | 0.5 s | S67, [D] | D |
| HOOK-05 | All | Text hook of 3 to 7 words held for at least 0.35 s per word plus 0.5 s | e.g. 2.95 s for 7 words | S58, [D] | D |
| HOOK-06 | Long-form | Target retention at 30 s | 70% or more (80% exceptional) | S94 | L |
| HOOK-07 | Shorts | Target "viewed vs swiped away" | 50% or more; 70% strong | S15 | L |
| PACE-01 | Short-form entertainment | Median gap between visual events | 1.5 to 3 s | S96 | L |
| PACE-02 | Short-form education | Median gap between visual events | 2 to 4 s | S96, [D] | L |
| PACE-03 | Long-form talking head | Visual event every 3 to 8 s; no unchanged shot longer than 15 s | 3-8 s; 15 s | S68, S64, [D] | D |
| PACE-04 | Dense or emotional content | Slow the cut rate | 4 to 6 s or more | S69 | M (direction), D (number) |
| PACE-05 | Ads | Distinct scenes per ad | 3 or more (5 or more for gaming) | S32 | M |
| PACE-06 | All except beat montages | Vary shot lengths around the target | plus or minus 30% | S68, [D] | D |
| PACE-07 | Long-form | Re-engagement beats | about 3:00 and 6:00 | S67 | M |
| PACE-08 | Long-form | Never signal the end; end within 5 to 20 s of the payoff, end screen over live content | 5-20 s | S67, S6 | M |
| PACE-09 | Long-form of 8 min or more | Clean audio pause or visual transition at each intended mid-roll | 8 min | S4 | H |
| PACE-10 | Long-form | Chapters: 00:00 first, at least 3, each at least 10 s; tutorials one per step | 3; 10 s | S5, S65 | H |
| ZOOM-01 | Jump cuts | Punch at least 20% so the size change reads as intentional | 120% or more | S75 | M |
| ZOOM-02 | Punch ceiling | At most source/output ratio; HD to HD at most 115% | 200% for UHD in HD | S76, [D] | M |
| ZOOM-03 | Emphasis | Punch 110% to 125%; close-up punch 140% to 150% | - | [L] | L |
| ZOOM-04 | Serious beats | Slow push 100% to 105-110% over 3 to 8 s | - | [L] | L |
| ZOOM-05 | Frequency | Punch at most 1 of every 2 to 3 jump cuts | - | [L] | L |
| JUMP-01 | Silences | Short-form: over 300 ms to 100-200 ms; long-form: over 500-600 ms to 250-350 ms | - | S71, S72, S74 | D |
| JUMP-02 | All cuts | About 200 ms padding; never clip the first syllable | 0.2 s | S73, S97 | M |
| JUMP-03 | Filler | Remove um, uh, er, false starts, repeats unless meaningful | - | S97 | M |
| JUMP-04 | Deliberate pause | Keep after punchlines and key claims | 0.5 to 1.0 s | S71, [D] | D |
| BROLL-01 | Showable noun, number, process | B-roll or graphic starts within 0.5 s of the word | 0.5 s | S99, [D] | D |
| BROLL-02 | B-roll | General 2-5 s; establishing 2-4 s; detail 1.5-3 s; reaction 1-2 s | - | S93 | M |
| BROLL-03 | Talking head | About 60% A-roll, 40% b-roll | 60/40 | S93 | L |
| BROLL-04 | Screen segments | Keep the presenter visible (PiP); return to the face for credibility and emotion | 41% of gaze on face | S64, S65 | H |
| BROLL-05 | Jarring cuts | Cutaway spanning the cut | - | [M] | M |
| CAP-01 | Short-form | 1 to 3 words per caption, 1 line | - | S63, S62 | M |
| CAP-02 | Short-form | Font 80 to 120 px; line height never below 4.5% of height | 86 px minimum line height | S63, S58 | M |
| CAP-03 | Short-form | White fill, 8 to 12 px black stroke or soft shadow | about 10% of size | S63 | L |
| CAP-04 | Short-form | One highlighted word per phrase | #FFD93D or #39FF14 | S63 | L |
| CAP-05 | All captions | Word or event on screen at audio onset | within 1-2 frames | S57 | H |
| CAP-06 | Subtitles | At most 42 chars per line, 2 lines, 20 cps English or 22 cps Bangla | - | S54, S55 | H |
| CAP-07 | Subtitles | Event 0.83 to 7 s; gaps 2 frames or at least 0.5 s | - | S56, S57 | H |
| CAP-08 | Any reading | 160 to 180 wpm; at least about 0.3 s per word | - | S58 | H |
| CAP-09 | 16:9 subtitles | Line height 8% of height; width at most 68% | 86 px; 1306 px | S58 | H |
| CAP-10 | All text | Contrast at least 4.5:1 (3:1 large) | - | S105 | H |
| TYPE-01 | Lower thirds | Inside 5% safe; hold 4 to 7 s; name at least 36 pt equivalent at 1080p | - | S80, S98 | M/L |
| TYPE-02 | All on-screen text | t = clamp(0.35 x words + 0.5, 0.83, 7.0) s | - | S58, S56, [D] | D |
| TYPE-03 | Data cards | One key number; number at 8% to 10% of height or more; hold reading time plus 1 s | - | S99, [D] | D |
| BN-01 | Bengali text | HarfBuzz renderer only (FFmpeg 6.1 or later, libass 0.15 or later, or browser) | - | S83, S84 | H |
| BN-02 | Bengali text | No tracking; style whole words only | - | S81, S82 | H |
| BN-03 | Bengali text | Danda never starts a line; no space before punctuation | - | S82, S55 | H |
| BN-04 | Bengali subtitles | At most 22 cps adult, 42 chars per line | - | S55 | H |
| BN-05 | Bengali text | Line height 1.3x to 1.5x Latin; stroke 5% to 7% of size | - | S82, [D] | D |
| AUD-01 | Voice | De-reverb, de-noise, HPF 80-100 Hz, de-ess 4-9 kHz, compress 2:1 (at most 6 dB), limit -1 dBTP | - | S44, S45 | M |
| AUD-02 | Music under speech | 15 LU below dialogue by default; 20 dB for accessible content; never closer than 8 LU | - | S48, S50, S51, [D] | M/D |
| AUD-03 | Ducking | -12 to -18 dB (vlogs up to -25); fades at least 200 ms | - | S53 | M |
| AUD-04 | Music under speech | Carve 1 to 4 kHz, or multiband duck 1.5 to 4 kHz | - | S44 | M |
| AUD-05 | Cut gaps | Fill with room tone at -45 to -50 dB under dialogue | - | S51 | L |
| AUD-06 | SFX | May exceed the 20 dB background rule only for sounds of 1 to 2 s | 1-2 s | S48 | H |
| SFX-01 | SFX placement | Whoosh peak on the cut; pop on the text's first frame; riser of 1 to 2 s ending on the reveal; impact under key stats | - | S51 | L |
| SFX-02 | SFX density | At most one prominent SFX per 1-2 s (short) or 5-10 s (long); rotate samples | - | [L], [D] | L |
| MUS-01 | Beat edits | Cut points on multiples of 60/BPM s | 120 BPM = 0.5 s = 15 f at 30 fps | S100 | H |
| MUS-02 | Licensing | Meta ads: no licensed music; TikTok business: Commercial Music Library | - | S18, S38 | H |
| AD-01 | Ads | Hook, body, close with CTA; product on screen; CTA card | +65% affinity, +45% recall | S33 | M |
| AD-02 | Ads | ABCD: brand from the start, people, one message, voiced CTA | +30% short-term sales likelihood | S12 | H |
| AD-03 | TikTok ads | 21 to 34 s for conversion tests; 9 to 15 s for awareness | - | S32, [L] | M/L |
| AD-04 | YouTube ads | Hook and brand before the 5 s skip; bumper at most 6 s; Shorts ads under 60 s | 5 s; 6 s; 60 s | S11 | H |
| AD-05 | Meta Reels ads | 9:16 plus audio plus safe zone | -34.5% cost per result vs images | S21 | H |
| AD-06 | Ads | Offer or CTA as text plus captions; voiceover plus written offer | +80%, +87% conversion (2021) | S32 | M |
| COMP-01 | Health, beauty | No negative self-image framing; no weight-loss before and after; verify current policy | - | S90 | M/L |
| COMP-02 | Beauty ads | No filters that exaggerate the product's effect | - | S89 | H |
| COMP-03 | Testimonials | No fake or AI testimonials; disclose connections | up to $51,744 per violation | S87 | H |
| COMP-04 | Health claims | Competent and reliable scientific evidence; typical results | - | S88 | H |
| COMP-05 | Synthetic media | Label realistic AI or altered content | EU from 2026-08-02 | S16, S37, S23, S86 | H |
| COMP-06 | All | No other-platform watermarks or QR codes; transform reused clips | - | S36, S27, S17 | H |
| COMP-07 | Disclosures | Clear and conspicuous, same mode as the claim, readable duration | - | S88 | H |
| TUT-01 | Screen capture | 1440p or 4K capture; editor font at least 16-18 px | - | S92 | L |
| TUT-02 | Screen zoom | Auto-zoom on clicks to 1.5x to 2x; eased 500 ms or more; hold 2 s | - | S91, [D] | L |
| TUT-03 | Code | Code text height at least 3% of output height after zoom | about 32 px at 1080p | [D] | D |
| TUT-04 | Tutorials | Chunks under 6 min; chapter per step (viewers engage 2 to 3 min) | 6 min | S65 | H |
| TUT-05 | Tutorials | Do not slow narration; energetic delivery engages | mean 156 wpm observed | S65 | H |
| TUT-06 | Screen content | Solid-box or heavy blur on secrets; track moving areas | - | [M] | M |
| TH-01 | Talking head | Eyes on upper third, camera at eye height, look into lens | - | [M] | M |
| TH-02 | 9:16 talking head | Eyes at 28% to 35% of height | y 540-670 | [D] | D |
| TH-03 | Skin | Hue near the skin-tone line; exposure 60-70 IRE light, 48-52 medium, 40-48 dark | about 123 degrees | S78, S77 | M |
| END-01 | YouTube | End-screen space in the last 5 to 20 s; video at least 25 s; at most 4 elements | - | S6 | H |
| END-02 | Shorts, Reels, TikTok | Loop the last frame or line into the first | - | S14 | M |

### 10.1 Machine-readable presets

```yaml
safe_zones_1080x1920:          # SAFE-01..04
  meta_reels_stories: {top: 269, bottom: 672, left: 65, right: 65}      # S18, S19 [H]
  tiktok:             {top: 130, bottom: 484, left: 44, right: 140}     # S35 [M]
  youtube_shorts_ads: {top: 192, bottom: 480, left: 54, right: 108}     # S9 [H]; left = 5% [D]
  universal:          {x_min: 65, x_max: 940, y_min: 270, y_max: 1248}  # [D]
safe_zone_1920x1080: {x_min: 96, x_max: 1824, y_min: 54, y_max: 1026}   # EBU R95 5% [H]
loudness:
  social_default: {integrated_lufs: -14, tolerance_lu: 1, true_peak_dbtp: -1.0}  # S43 [M], S41 [H]
  podcast_apple:  {integrated_lufs: -16, tolerance_lu: 1, true_peak_dbtp: -1.0}  # S46 [H]
  broadcast_ebu:  {integrated_lufs: -23, true_peak_dbtp: -1.0}
captions_social_9x16:
  words_per_caption: [1, 3]
  lines: 1
  font_px: [80, 120]
  min_line_height_px: 86
  stroke_px: [8, 12]
  fill: "#FFFFFF"
  stroke: "#000000"
  highlight: ["#FFD93D", "#39FF14"]
  pop_scale_max: 1.05
  caption_center_y_px: [1100, 1150]   # cross-post; TikTok-only may go lower
  max_width_px: 875
subtitles:
  max_chars_per_line: 42
  max_lines: 2
  max_cps: {en_adult: 20, en_child: 17, bn_adult: 22, bn_child: 18}
  min_duration_s: 0.83
  max_duration_s: 7.0
  min_gap_frames: 2
  line_height_pct: {landscape: 8.0, vertical_9x16: 4.5}
reading_time_s: "clamp(0.35 * words + 0.5, 0.83, 7.0)"
silence:
  short_form: {trim_above_ms: 300, target_ms: [100, 200]}
  long_form:  {trim_above_ms: 550, target_ms: [250, 350]}
  deliberate_pause_ms: [500, 1000]
  speech_padding_ms: 200
music_under_speech_lu_below_dialogue: {default: 15, accessible: 20, floor: 8}
ducking: {depth_db: [-12, -18], fade_down_ms: [250, 400], fade_up_ms: [400, 800], hold_through_gaps_under_ms: 1000}
voice_chain: [dereverb_light, denoise_light, hpf_80_100hz, deess_4_9khz, comp_2to1_max6db_gr, limiter_minus1dbtp]
pacing_median_gap_s:
  short_entertainment: [1.5, 3.0]
  short_education: [2.0, 4.0]
  ads_first_6s: [1.5, 3.0]
  longform_talking_head: [3.0, 8.0]
  emotional_occasion: [3.0, 6.0]
punch_in:
  min_change_pct: 20
  emphasis_pct: [110, 125]
  closeup_pct: [140, 150]
  max_hd_source_pct: 115
  slow_push: {to_pct: [105, 110], over_s: [3, 8]}
```

---

## 11. Quality checklist before export (30 items)

1. **Spec:** resolution, aspect ratio and frame rate match the preset; no unintended letterboxing or pillarboxing.
2. **Encode:** H.264 High, preset bitrate, fast start, no edit lists; SDR tagged BT.709.
3. **Frame 0:** a strong subject frame (it often becomes the cover on Reels and TikTok) that matches the title or thumbnail promise.
4. **Hook:** key message by 3 s (short-form, ads) or within 5 s (long-form); hook text passes the reading-time check.
5. **Dead air:** no unintended silence longer than about 0.6 s; no black or frozen frames except intentional ones.
6. **Jump cuts:** no clipped syllables, no clicks or pops at edits, room tone continuous under cuts.
7. **Pacing:** visual-event gaps within the format's target; no static shot beyond its limit; rhythm varies.
8. **Structure:** long-form re-engagements present; the end is not signalled early; short-form loop or CTA works.
9. **B-roll:** matches what is being said at that moment; no contradicting or unrelated stock; no watermarks; licences logged.
10. **Captions accuracy:** names, brands, numbers and technical terms 100% correct; sync within 1 to 2 frames.
11. **Captions layout:** words per caption, lines and size per spec; nothing over eyes, mouth, product or logo.
12. **Safe zones:** every critical text element, price and CTA passes a safe-zone overlay check for each target platform.
13. **Reading time:** every text element meets `t_min`; subtitles within cps limits.
14. **Contrast:** at least 4.5:1, or stroke, shadow or box present.
15. **Typography:** at most 2 families plus the caption font; weights consistent; font licences allow video use.
16. **Bengali or other Indic text:** shaping test passes (no dotted circles, no detached vowel signs); no tracking; whole-word styling only.
17. **Copy:** on-screen text spelled correctly and written in natural, human language for the audience; no em dashes.
18. **Loudness:** -14 LUFS integrated plus or minus 1 LU (or the job's target); true peak at most -1 dBTP.
19. **Intelligibility:** music at least 15 LU under speech (20 dB for educational); no SFX masking words; checked on a phone speaker.
20. **Clean audio:** no hum, hiss, clipping, harsh sibilance or pumping; voice centred.
21. **Music:** licensed for this platform and this account type; edits on bar lines; the ending resolves or loops.
22. **SFX:** density within limits, samples varied, each one synced to its visual.
23. **Ending:** ads close with a spoken and shown CTA; YouTube leaves 5 to 20 s for end-screen elements; Shorts loop cleanly.
24. **Chapters and mid-rolls:** 00:00 first, at least 3, each at least 10 s; clean breakpoints at mid-roll slots for videos of 8 min or more.
25. **Claims and compliance:** claims substantiated; testimonials genuine and disclosed; no prohibited before-and-after framing; no exaggerating filters.
26. **AI and disclosure:** realistic synthetic or altered content flagged for the platform's label and, in the EU, Article 50 disclosure; paid-partnership labels set.
27. **Privacy:** no personal data, keys, notifications or bystander faces visible; redactions burned in.
28. **Originality:** no other-platform watermarks or QR codes; reused clips transformed; template varied for this client.
29. **Deliverables:** SRT or VTT captions for long-form; 9:16, 4:5 and 16:9 versions reframed around faces rather than blindly cropped; Instagram cover safe inside the 3:4 grid crop.
30. **Final watch:** one full watch on a phone with sound, and one muted watch to confirm the story still reads with sound off.

---
## 12. Uncertain items and things to verify live

- **TikTok official safe-zone files** could not be fetched; the 130 / 484 / 44 / 140 px values come from 2026 secondary guides, and TikTok itself says the safe area shrinks as ad captions grow. Re-check against TikTok's downloadable safe-zone templates when possible.
- **Social loudness targets** for TikTok, Instagram and Facebook are not published; -14 LUFS is a convention. YouTube's -14 LUFS reference is measured, not officially documented.
- **Cut-frequency numbers** for short-form (1.5 to 3 s and similar) come from practitioner guides, not controlled studies. Research supports the direction (faster cutting holds attention; fast pace plus arousing content hurts recall) but not exact seconds.
- **Punch-in percentages** beyond the 20% rule and the resolution ceiling are practitioner conventions.
- **Caption styling numbers** (80 to 120 px, stroke 8 to 12 px, highlight colours) come from one detailed practitioner spec; BBC's 4.5% line height for vertical video is the only standards-body anchor.
- **Meta before-and-after change of 2026-07-22** is reported by an agency blog without a Meta link. Treat before-and-after health and beauty imagery as restricted until confirmed in Meta's live Advertising Standards.
- **TikTok "50% of ad impact in the first 2 s"** is reported by secondary sources only; the 90%-within-6-s figure appears on TikTok's Creative Codes page.
- **TikTok 280% lift for 21 to 34 s ads** is quoted by secondary sources; TikTok's 2021 guidance as reported by Social Media Today states only that 21 to 34 s performed best.
- **Screen Studio's 2x default zoom** comes from a competitor's blog; Screen Studio's own guide confirms click-based auto-zoom only.
- **Instagram's 30 fps minimum** comes from secondary summaries of an Instagram Help page that did not render here.
- **EU AI Act Article 50** applies from 2026-08-02; the EU "Digital Omnibus" process may change timelines or details for some obligations. Check before advising on EU campaigns.
- **Music tempo table (5.4)** is an editor heuristic with no authoritative source.
- **Bengali size and stroke adjustments (BN8, BN15)** are derived and need a visual check on real renders.
- **Meta "3-second video plays" and ThruPlay definitions** were not re-fetched in this session.

---
## 13. Sources

Dates are publication or last-updated dates where the page shows one; "accessed" means the live page was read on 2026-09-25 and shows no date.

| ID | Source | Date | URL |
|---|---|---|---|
| S1 | YouTube Help: Recommended upload encoding settings | accessed 2026-09-25 | https://support.google.com/youtube/answer/1722171 |
| S2 | YouTube Help: Understand three-minute YouTube Shorts | rules dated 2024-10-15, 2025-12-08, 2026-09-24 | https://support.google.com/youtube/answer/15424877 |
| S3 | YouTube Help: Upload videos longer than 15 minutes | accessed 2026-09-25 | https://support.google.com/youtube/answer/71673 |
| S4 | YouTube Help: Manage mid-roll ad breaks | accessed 2026-09-25 | https://support.google.com/youtube/answer/6175006 |
| S5 | YouTube Help: Video chapters | accessed 2026-09-25 (via search) | https://support.google.com/youtube/answer/9884579 |
| S6 | YouTube Help: Add end screens | accessed 2026-09-25 | https://support.google.com/youtube/answer/6388789 |
| S7 | YouTube Help: Measure key moments for audience retention | accessed 2026-09-25 | https://support.google.com/youtube/answer/9314415 |
| S8 | YouTube Official Blog: Four tips to hook your viewers | 2014-06-24 | https://blog.youtube/creator-and-artist-stories/four-tips-to-hook-your-viewers-on/ |
| S9 | Google Business: YouTube Shorts ads | accessed 2026-09-25 | https://business.google.com/us/ad-solutions/youtube-ads/shorts-ads/ |
| S10 | Google Ads Help: Use square and vertical video | accessed 2026-09-25 | https://support.google.com/google-ads/answer/9128498 |
| S11 | Google Ads Help: About video ad formats | accessed 2026-09-25 | https://support.google.com/google-ads/answer/2375464 |
| S12 | Google Ads Help: About the ABCDs of effective video ads (study: Google and Kantar, April 2021) | accessed 2026-09-25 | https://support.google.com/google-ads/answer/14783551 |
| S13 | Think with Google: YouTube ABCDs | 2022-04 | https://business.google.com/us/think/future-of-marketing/youtube-video-ad-creative/ |
| S14 | PPC Land: YouTube changes how Shorts views are counted (effective 2025-03-31) | 2025-03 | https://ppc.land/youtube-changes-how-shorts-views-are-counted-from-march-31/ |
| S15 | YouTube Community: Viewed vs swiped away metric; benchmarks from third-party explainers | 2024 to 2026 | https://support.google.com/youtube/community-video/273390203 |
| S16 | TechCrunch: YouTube requires disclosure of realistic AI content; YouTube Help 14328491 | 2024-03-18 | https://techcrunch.com/2024/03/18/youtube-requires-creatorsdisclose-realistic-content-made-ai/ |
| S17 | Social Media Today: YouTube clarifies inauthentic content monetisation update | 2025-07 | https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/ |
| S18 | Meta Ads Guide: Instagram Reels video | accessed 2026-09-25 | https://www.facebook.com/business/ads-guide/update/video/instagram-reels |
| S19 | Meta Ads Guide: Instagram Stories video | accessed 2026-09-25 | https://www.facebook.com/business/ads-guide/update/video/instagram-story |
| S20 | Meta Ads Guide: Facebook Feed video | accessed 2026-09-25 | https://www.facebook.com/business/ads-guide/update/video/facebook-feed |
| S21 | Meta for Business: Instagram and Facebook Reels ads (stats footnoted to Meta analyses, incl. May 2022 to April 2023) | accessed 2026-09-25 | https://www.facebook.com/business/ads/facebook-instagram-reels-ads |
| S22 | Meta Newsroom: Making it easier to create videos on Facebook | 2025-06 | https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/ |
| S23 | Meta: AI disclosure policy for political and social issue ads | 2023-11-08 (effective 2024-01-11; label update 2026-02-19) | https://www.facebook.com/government-nonprofits/blog/political-ads-ai-disclosure-policy |
| S24 | Billo: Meta ads safe zones, 2026 unified creative update (secondary) | 2026 | https://billo.app/blog/meta-ads-safe-zones/ |
| S25 | Social Media Today: Instagram expands Reels to 3 minutes | 2025-01 | https://www.socialmediatoday.com/news/instagram-officially-expands-reels-length-3-minutes/737766/ |
| S26 | Hootsuite: Instagram algorithm (Mosseri's January 2025 signals) | 2026 | https://blog.hootsuite.com/instagram-algorithm/ |
| S27 | Engadget: Instagram rewards original content, penalises aggregators; PetaPixel on the 2026 expansion | 2024; 2026-04-30 | https://www.engadget.com/instagrams-algorithm-overhaul-will-reward-original-content-and-penalize-aggregators-130018977.html |
| S28 | Social Media Today: Instagram Stories under 60 s no longer split | 2023 | https://www.socialmediatoday.com/news/Instagram-Announces-Videos-Under-60-Seconds-Stories-No-Longer-Split-Segments/632598/ |
| S29 | Buffer: Instagram grid changes (3:4) | 2025 | https://buffer.com/resources/instagram-grid/ |
| S30 | Instagram Help: Reel size and aspect ratios (content via secondary summaries) | accessed 2026-09-25 | https://help.instagram.com/1038071743007909 |
| S31 | Udonis: TikTok ad specs (citing TikTok Business Help Center) | 2026 | https://www.blog.udonis.co/advertising/tiktok-ad-specs |
| S32 | Social Media Today: TikTok best-practice tips for conversion (TikTok data) | 2021-12-03 | https://www.socialmediatoday.com/news/tiktok-shares-best-practice-tips-for-driving-conversion-with-your-ads/610952/ |
| S33 | TikTok for Business: Creative Codes (figures via search snippets; page not fetchable here) | accessed 2026-09-25 | https://ads.tiktok.com/business/en-US/creative-codes |
| S34 | Lebesgue and others quoting TikTok Creative Center (63% key message in 3 s; 93% use audio) | 2024 to 2026 | https://lebesgue.io/tiktok-ads/how-to-increase-tiktok-ctr-9-creative-tips |
| S35 | EzUGC: TikTok safe zones (also Koro, 2026-02-03) | 2026-06-21, updated 2026-08-01 | https://www.ezugc.ai/blog/tiktok-safe-zones-guide |
| S36 | TikTok Community Guidelines: For You feed eligibility standards | accessed 2026-09-25 (via search) | https://www.tiktok.com/community-guidelines/en/fyf-standards |
| S37 | TikTok Newsroom: New labels for disclosing AI-generated content | 2023 onward | https://newsroom.tiktok.com/en-us/new-labels-for-disclosing-ai-generated-content |
| S38 | TikTok Ads Help: About the Commercial Music Library (via secondary summaries) | accessed 2026-09-25 | https://ads.tiktok.com/help/article/commercial-music-library |
| S39 | TikTok: Creator Rewards Program terms | accessed 2026-09-25 | https://www.tiktok.com/legal/page/global/creator-rewards-program-us/en |
| S40 | Metricool: TikTok video length limits | 2025 | https://metricool.com/tiktok-video-length/ |
| S41 | AES TD1008.1.21-9: Loudness of internet audio streaming and on-demand distribution | 2021-09-24 | https://aes.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf |
| S42 | Ian Shepherd, Production Advice: YouTube stats for nerds and normalisation | 2017-09-29 | https://productionadvice.co.uk/stats-for-nerds/ |
| S43 | iZotope: Your mastering questions answered (YouTube -14 LUFS) | accessed 2026-09-25 (via search) | https://www.izotope.com/en/learn/we-are-listening-your-mastering-questions-answered |
| S44 | iZotope: Mixing audio for video, part 4 | 2018-10-22 | https://www.izotope.com/en/learn/mixing-audio-for-video-part-4-mixing-techniques.html |
| S45 | iZotope: Ultimate guide to podcast production, part 2 | 2025-07-24 | https://www.izotope.com/en/learn/podcast-production-guide-part2 |
| S46 | Apple Podcasts for Creators: Audio requirements | accessed 2026-09-25 (via search) | https://podcasters.apple.com/support/893-audio-requirements |
| S47 | Netflix Partner Help: Sound mix specifications and best practices v1.6 | accessed 2026-09-25 (via search) | https://partnerhelp.netflixstudios.com/hc/en-us/articles/360001794307 |
| S48 | W3C: Understanding WCAG 2.2 SC 1.4.7 Low or no background audio | updated 2025-09-16 | https://www.w3.org/WAI/WCAG22/Understanding/low-or-no-background-audio.html |
| S49 | WeVideo: How to set volume levels | 2025-11-26 | https://www.wevideo.com/blog/how-to-set-audio-levels |
| S50 | Zatta: Guidelines for adjusting audio level | 2020-12-19 | https://zatta.link/en/video/adjustment-audio-level-in-decibel-and-loudness.html |
| S51 | Mark Studios: Sound design and music selection for video | 2026-04-09 | https://www.markstudios.com/blog/sound-design-music-selection-for-video-2026 |
| S52 | Larry Jordan: Automatically duck background music under dialog in DaVinci Resolve | 2024-08-31 | https://larryjordan.com/articles/automatically-duck-background-music-under-dialog-in-davinci-resolve/ |
| S53 | Freepik blog: Auto ducking in Premiere Pro | undated, accessed 2026-09-25 | https://www.freepik.com/blog/how-to-use-auto-ducking-in-premiere-pro-for-clean-professional-audio/ |
| S54 | Netflix: English (USA) Timed Text Style Guide | updated 2025-12-19 | https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977 |
| S55 | Netflix: Bangla Timed Text Style Guide | updated 2025-07-04 | https://partnerhelp.netflixstudios.com/hc/en-us/articles/4483351778963 |
| S56 | Netflix: Timed Text Style Guide, general requirements | updated 2022-10-07 | https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617 |
| S57 | Netflix: Subtitle timing guidelines | updated 2025-07-04 | https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394 |
| S58 | BBC Subtitle Guidelines v1.2.3 (via Broadcast Writer, 2024-12-12, and Clevercast, 2023-09-06) | 2024-06 | https://broadcastwriter.com/2024/12/12/bbc-subtitle-style-guide-2024/ |
| S59 | Ofcom subtitling speed guidance and 2023 consultation (secondary) | 2023-07-15 | https://liamodell.com/2023/07/15/ofcom-tv-access-services-code-guidelines-consultation-subtitles-sign-language-audio-description/ |
| S60 | Forbes: Verizon Media and Publicis Media captions study | 2019-07-31 | https://www.forbes.com/sites/tjmccue/2019/07/31/verizon-media-says-69-percent-of-consumers-watching-video-with-sound-off/ |
| S61 | 3Play Media: Captions increase Facebook video ad view time 12% (Facebook internal, 2016) | 2016 | https://www.3playmedia.com/blog/captions-increase-viewership-for-facebook-video-ads/ |
| S62 | Li, Applied Cognitive Psychology: One-line vs two-line subtitles in vertical videos (eye tracking, n = 211) | 2026 | https://onlinelibrary.wiley.com/doi/10.1002/acp.70262 |
| S63 | Ascynd: Hormozi captions, exact font, colour and specs | 2026-04-23 | https://ascynd.io/en/blog/hormozi-captions |
| S64 | Kizilcec, Papadopoulos, Sritanyaratana, CHI: Showing face in video instruction | 2014 | https://rene.kizilcec.com/wp-content/uploads/2014/01/final_version2.pdf |
| S65 | Guo, Kim, Rubin, L@S: How video production affects student engagement | 2014-03 | https://dl.acm.org/doi/10.1145/2556325.2566239 |
| S66 | TechSmith: Video Viewer Trends 2024 | 2024-09-11 | https://www.techsmith.com/resources/research/video-viewer-report/ |
| S67 | MrBeast Productions internal guide (publicised September 2024; summary by Simon Willison, 2024-09-15) | 2024-09 | https://simonwillison.net/2024/Sep/15/how-to-succeed-in-mrbeast-production/ |
| S68 | Cutting et al., i-Perception: Quicker, faster, darker (160 films, 1935 to 2010) | 2011 | https://journals.sagepub.com/doi/10.1068/i0441aap |
| S69 | Lang, Bolls, Potter, Kawahara, Journal of Broadcasting and Electronic Media: Production pacing and arousing content | 1999 | https://www.tandfonline.com/doi/abs/10.1080/08838159909364504 |
| S70 | Loewenstein, Psychological Bulletin: The psychology of curiosity | 1994 | (journal article) |
| S71 | Campione and Veronis, Speech Prosody: Multilingual study of silent pause duration | 2002 | https://www.isca-archive.org/speechprosody_2002/campione02_speechprosody.html |
| S72 | Stivers et al., PNAS: Universals and cultural variation in turn-taking | 2009 | https://www.pnas.org/doi/10.1073/pnas.0903616106 |
| S73 | auto-editor README (default margin and threshold) | accessed 2026-09-25 | https://github.com/WyattBlue/auto-editor |
| S74 | Descript Help: Shorten word gaps | undated, accessed 2026-09-25 | https://help.descript.com/hc/en-us/articles/10164807277453 |
| S75 | Story Envelope: 180-degree, 30-degree and 20% rules | 2020-05-01 | https://storyenvelope.com/three-basic-rules-of-filmmaking-explained/ |
| S76 | Creative COW and Adobe community: punching into UHD in an HD timeline (200%) | forum threads | https://creativecow.net/forums/thread/how-much-can-you-zoom-in-on-4k-footage-in-a-1080p/ |
| S77 | Videomaker: How to use false colour (skin IRE ranges) | about 2025-02 | https://www.videomaker.com/how-to/shooting/composition/how-to-use-false-color-in-your-next-project/ |
| S78 | Pixel Valley Studio: The skin tone line | accessed 2026-09-25 (via search) | https://pixelvalleystudio.com/pmf-articles/the-skin-tone-line |
| S79 | Frame.io Insider, Cullen Kelly: 5 tips for perfect skin tones in DaVinci Resolve | 2020-10-05, updated 2023-12-18 | https://blog.frame.io/2020/10/05/skin-tones-in-davinci-resolve/ |
| S80 | EBU R95: Safe areas for 16:9 television production | R95 (revised 2016) | https://tech.ebu.ch/publications/r095 |
| S81 | W3C: Bengali Gap Analysis | 2021-05-25 | https://www.w3.org/TR/2021/WD-beng-gap-20210525/ |
| S82 | r12a: Bengali orthography notes | accessed 2026-09-25 | https://r12a.github.io/scripts/beng/bn.html |
| S83 | FFmpeg drawtext documentation (7.1); FFmpeg 6.1 drawtext requires HarfBuzz (void-linux issue 52730) | 2023 to 2025 | https://ayosec.github.io/ffmpeg-filters-docs/7.1/Filters/Video/drawtext.html |
| S84 | libass Changelog (0.15.0: HarfBuzz required) | accessed 2026-09-25 | https://github.com/libass/libass/blob/master/Changelog |
| S85 | Fontsource and Google Fonts: Bengali families | accessed 2026-09-25 | https://fontsource.org/languages/bengali |
| S86 | EU AI Act, Article 50 (applies 2026-08-02) | accessed 2026-09-25 | https://artificialintelligenceact.eu/article/50/ |
| S87 | FTC: Final rule banning fake reviews and testimonials | 2024-08-14 (effective 2024-10-21) | https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials |
| S88 | FTC: Health Products Compliance Guidance | 2022-12 | https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance |
| S89 | ASA: The (mis)use of social media beauty filters when advertising cosmetic products | 2021-02 | https://www.asa.org.uk/news/the-mis-use-of-social-media-beauty-filters-when-advertising-cosmetic-products.html |
| S90 | Accelerated Digital Media: 2026 health advertising policies; Clikim on the reported 2026-07-22 Meta update (unverified) | 2026 | https://www.accelerateddigitalmedia.com/insights/guide-to-social-media-health-ad-restrictions-2026/ |
| S91 | Screen Studio guide: Adding and editing zooms; Screenify blog on auto-zoom defaults (2026-04-10) | accessed 2026-09-25 | https://screen.studio/guide/adding-editing-zooms |
| S92 | Screenify: How to record VS Code for coding tutorials | 2026-04-19 | https://www.screenify.studio/blog/2026-04-19-record-vscode-tutorial |
| S93 | Captions.ai: A practical guide to b-roll | 2025-11-25, updated 2026-06-15 | https://captions.ai/blog/practical-guide-b-roll-video |
| S94 | 1of10: How to hook viewers in the first 30 seconds | 2025-09-01 | https://1of10.com/blog/how-to-hook-viewers-in-the-first-30-seconds-of-a-youtube-video/ |
| S95 | Pod2Reels: YouTube Shorts safe zone guide (organic, measured) | 2026-07-10 | https://www.pod2reels.com/blog/youtube-shorts-safe-zone-guide |
| S96 | Shortzly: Short-form video pacing guide | 2026 | https://shortzly.com/blog/short-form-video-pacing-editing-guide |
| S97 | RouteNote: How to create effective jump cuts | 2026-03-09 | https://licensing.routenote.com/blog/how-to-create-effective-jump-cuts-when-video-editing/ |
| S98 | ANFX: Lower thirds design rules | accessed 2026-09-25 (via search) | https://anfx.co/blog/lower-thirds-design-rules-free-templates/ |
| S99 | Mayer, Multimedia Learning, 3rd edition, Cambridge University Press (coherence, signalling, contiguity, segmenting principles) | 2020 | https://www.cambridge.org/highereducation/books/multimedia-learning/FB7E79A165D24D47CEACEB4D2C426ECD |
| S100 | ClipMusic: BPM for video editors | accessed 2026-09-25 (via search) | https://clipmusic.ai/blog/bpm-video-editing-guide |
| S101 | Jon Loomer: Meta Andromeda and creative diversification | 2025 | https://www.jonloomer.com/meta-andromeda-creative-diversification/ |
| S102 | Jon Loomer: Meta video ad length requirements | 2025 to 2026 | https://www.jonloomer.com/meta-video-ad-length-requirements/ |
| S103 | iZotope: Tips to repair a compressed or noisy interview (de-reverb before de-noise; via search snippet) | accessed 2026-09-25 | https://www.izotope.com/en/learn/tips-to-repair-a-compressed-or-noisy-interview.html |
| S105 | W3C: WCAG 2.2 (SC 1.4.3 contrast minimum) | W3C Recommendation 2023-10-05 | https://www.w3.org/TR/WCAG22/ |
