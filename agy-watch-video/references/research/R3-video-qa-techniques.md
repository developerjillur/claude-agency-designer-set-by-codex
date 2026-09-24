# R3: Video QA techniques for an ffmpeg + Gemini video skill

Research date: 2026-09-24. Scope: frame sampling, deterministic ffmpeg/ffprobe QA, hallucination control, use-case playbooks.

How this was checked:
- Four parallel research passes, plus direct reading of the FFmpeg docs and FFmpeg source, the Gemini API docs, and Anthropic's vision docs.
- Every claim carries the URL it came from.
- **Unverified** marks anything that could not be confirmed on a primary page.
- Numbers from papers were read through a page summarizer, so a table cell can be mistyped. The findings the recommendations lean on hardest were re-opened and confirmed; they are marked **(re-checked)**.
- No fetched page contained instructions addressed to an AI.

---

## 0. Summary: the twelve findings that matter most

1. **Why the native mp4 run invented details.**
   - Gemini's default ("static") video path samples 1 frame per second (https://ai.google.dev/gemini-api/docs/video-understanding).
   - On Gemini 3 each video frame gets 70 tokens at the default, low or medium media resolution, and 280 at high. A still image gets 1,120 tokens by default, and 2,240 at `ultra_high` (https://ai.google.dev/gemini-api/docs/media-resolution).
   - So each of your 16 extracted frames had about 16x the detail budget of a native video frame, and you sent twice as many frames.
   - Google's own doc warns that fast action "might lose detail due to the 1 FPS sampling rate" (https://ai.google.dev/gemini-api/docs/video-understanding).
2. **Sample 2 to 5 fps for short clips; go denser only in short bursts.**
   - The only Gemini frame-rate study found is Moment-Video (https://arxiv.org/html/2606.02522, re-checked). Gemini-3.1-Pro scored 26.9% at 1 fps, 38.3% at 5 fps, 36.3% at 8 fps and 36.6% at 16 fps. Gemini-3-Flash followed the same pattern.
   - The authors' reading: denser sampling helps, but "not strictly monotonic".
3. **Put a text label line before every frame image.** For example `Frame 07/16 | t=00:03.50`.
   - TimeLens tested timestamp formats (https://arxiv.org/html/2512.14698, re-checked). Plain text timestamps placed before each frame scored best: Charades-STA mIoU 48.3. Burned-in overlay timestamps scored 46.3 and position embeddings 36.6.
4. **Always keep a uniform coverage floor, then add frames at scene cuts, motion peaks and events.**
   - Picking frames only by relevance to the question can score below uniform sampling on general questions. In the AKS ablation, Video-MME fell from 64.4 (uniform) to 63.7 (relevance-only) (https://arxiv.org/html/2502.21271).
5. **Small text needs native-resolution crops, plus OCR.**
   - Cropping has the strongest evidence of any fix for small detail. ViCrop took TextVQA from 47.80 to 56.06 (https://arxiv.org/html/2502.17422).
   - Frame-level text reading is still weak in video. On VidText, humans score 89.5% and Gemini 1.5 Pro 46.8% (https://arxiv.org/html/2505.22810v1).
   - So send OCR output (Apple Vision or Tesseract) alongside the frames.
6. **Contact sheets are for overview, order and pacing only.**
   - IG-VLM found a 3x2 grid of 6 frames works well for video QA (https://arxiv.org/html/2403.18406v1).
   - Each cell gets only a fraction of the pixels, so never use a grid to read small text.
7. **Measure what can be measured; never ask the model.** This covers:
   - cuts, black frames, freezes and silence;
   - loudness, true peak and clipping;
   - letterboxing and interlacing;
   - variable frame rate, rotation and codec.

   ffmpeg and ffprobe give exact values (section 3). Hand these to the model as authoritative facts.
8. **Neutral prompts only.**
   - "Find the glitches" puts a false premise in the question. False-premise questions are the hardest hallucination category: about 22% average accuracy in HAVEN (https://arxiv.org/abs/2503.19622).
   - Models also go along with how the user frames things (ViSE, https://arxiv.org/html/2506.07180v3).
   - Always allow "none observed" as an answer.
9. **Every claim must cite evidence**: frame ID, timestamp and region. "Unreadable" or "not visible" is the correct answer when evidence is missing.
   - Evidence grounding is the hardest part even for the best models. On VideoZeroBench, "No model exceeds 1% accuracy when both correct answering and accurate spatio-temporal localization are required", and Gemini-3-Pro answers "fewer than 17%" correctly end to end (https://arxiv.org/abs/2604.01569, re-checked).
10. **Verify separately from the first answer.**
    - Chain-of-Verification works best in its factored form, where the verifier never sees the draft claim (https://arxiv.org/abs/2309.11495).
    - Re-check each flagged claim in a fresh call, on dense frames and crops, with a neutral question.
    - Cross-check text with OCR.
    - Claude, the host model in Claude Code, can read the same frames as an independent second opinion.
11. **AI-generation verdicts need provenance first, then artifact evidence that rules out ordinary camera causes.**
    - The best zero-shot model on RA-Bench (Gemini-3.1-Pro-Preview) reached 63.4 balanced accuracy (https://arxiv.org/html/2608.14391; this number comes from the paper body).
    - Anthropic states that Claude "cannot determine whether an image is AI-generated" (https://platform.claude.com/docs/en/build-with-claude/vision).
12. **Keep Gemini 3 temperature at its default of 1.0**, as Google recommends (https://ai.google.dev/gemini-api/docs/gemini-3).
    - Treat disagreement between repeated runs as a warning flag, not as a vote. Majority voting did not fix sycophancy in ViSE (https://arxiv.org/html/2506.07180v3).

---

## 1. Gemini facts that shape the design

All from Google's docs as fetched on 2026-09-24; the pages show "Last updated 2026-09-23".

**Video sampling and processing** (https://ai.google.dev/gemini-api/docs/video-understanding and https://ai.google.dev/gemini-api/docs/video-understanding.md.txt)
- Default static mode takes 1 frame per second. "Timestamps are added every second."
- Custom rate and clipping: `processing: {type: "static", fps: 0.5, start_offset: ..., end_offset: ...}`, shown in the Interactions API examples.
- No maximum fps is documented.
- Agentic mode is `"processing": "agentic"`. It is supported on "Gemini 3.8 Flash, 3.7 Flash, 3.6 Flash, 3.5 Flash Lite, and later models".
- In agentic mode the model loads frames, audio or transcript on demand. Google claims "up to 88% more token-efficient and ~7% higher quality on long-form content", with somewhat more latency on short clips.

**Audio**
- "Audio is processed at 1Kbps (single channel)."
- 32 tokens per second on the video page; 25 tokens per second in the Gemini 3 media-resolution table.

**Tokens per video frame**
- Video page: 66 tokens per frame at low resolution and 258 at high. Roughly 100 tokens per second of video at default (low) resolution, and 300 at high, including audio.
- Gemini 3 table on the media-resolution page: 70 tokens at unspecified, low or medium, and 280 at high.
- The Gemini 3 table recommends `high` only for "reading dense text (OCR) or small details" (https://ai.google.dev/gemini-api/docs/media-resolution).

**Tokens per image, Gemini 3**
- Unspecified (default) 1,120; low 280; medium 560; high 1,120; `ultra_high` 2,240.
- Resolution can be set per media item, but only on Gemini 3 (https://ai.google.dev/gemini-api/docs/media-resolution).
- The older rule still printed on the image page and the tokens page: 258 tokens for an image up to 384 px, and 768x768 tiles at 258 tokens each (https://ai.google.dev/gemini-api/docs/image-understanding, https://ai.google.dev/gemini-api/docs/tokens).

**Limits** (https://ai.google.dev/gemini-api/docs/video-understanding, https://ai.google.dev/gemini-api/docs/image-understanding)
- Inline data under 100 MB. Files API 2 GB (free tier) or 20 GB (paid).
- With a 1M-token context, about 3 hours of video at low resolution or 1 hour at high.
- Up to 3,600 images per request.

**Prompt order: Google's own pages conflict**
- Video page: put the text after the video.
- Image page: "place the text prompt *before* the image" for a single image (re-checked).
- File prompt guide: image before text (https://ai.google.dev/gemini-api/docs/files).
- The Gemini 3 guide says to put specific questions "at the end" for large inputs (https://ai.google.dev/gemini-api/docs/gemini-3).
- **Our resolution:** a short label text before each frame (TimeLens), and the task and rules at the end.

**Gemini 3 guidance** (https://ai.google.dev/gemini-api/docs/gemini-3)
- Keep temperature at 1.0; lower values "may degrade performance" or cause looping.
- Keep instructions concise.
- Thinking levels: minimal, low, medium, high.
- **Conflict:** the general file prompt guide says that for hallucinated content you should try "dialing down the temperature setting or asking the model for shorter descriptions" (https://ai.google.dev/gemini-api/docs/files). Follow the model-specific Gemini 3 advice. "Shorter descriptions" is compatible with it.

**Frame rate claims**
- The Gemini 3 Pro vision blog (Dec 5, 2025) says the model was optimized for fast actions "when sampling at >1 frames-per-second", and gives a 10 fps golf-swing example (https://blog.google/technology/developers/gemini-3-pro-vision/).

**Current models, 2026-09-23** (https://ai.google.dev/gemini-api/docs/models)
- `gemini-3.8-flash` is stable. `gemini-3.1-pro-preview` is still in preview. `gemini-3-pro-preview` is shut down.
- Which model, media resolution and fps the Antigravity CLI uses is **unknown**.

**Prices, paid tier, input** (https://ai.google.dev/gemini-api/docs/pricing)

| Model | Input price per 1M tokens |
|---|---|
| 3 Flash Preview | $0.50 (text, image, video) |
| 3.8 Flash | $0.75 until 2026-12-31, then $1.50 |
| 3.1 Pro Preview | $2.00 (prompts up to 200k tokens) |
| 3.5 Flash-Lite | $0.30 |

**Existing local contract** (`<local scratch file>`)
- Inputs over 50 MiB are transcoded to proxies of at most 854x480 and 30 fps.
- That is fine for general gist, but it removes exactly the small text and fine detail the drone test got wrong.
- For detail work, extract frames from the original file, never from the proxy.

### 1.1 Token budget: native video vs frames as images (Gemini 3 defaults)

Assumptions (from the docs above): native static video costs about 100 tokens/s at default and about 300 tokens/s at high, audio included. An image at default costs 1,120 tokens.

| Case | Native video, default | Native video, high | Frames as images | Hybrid (recommended) |
|---|---|---|---|---|
| 8 s drone clip | about 800 | about 2,400 | 16 frames: 17,920 (+8 crops: 26,880) | 16 frames + 4 to 8 crops: 22k to 27k |
| 60 s ad | about 6,000 | about 18,000 | 2 fps, 120 frames: 134,400 | native default + 30 shot frames + 10 crops: about 50,800 |
| 10 min tutorial | about 60,000 | about 180,000 | not sensible | native low + 80 scene keyframes + 20 crops: about 172,000 |

What this costs in money: 17,920 tokens is about $0.009 on 3 Flash Preview, and 134,400 is about $0.067 (https://ai.google.dev/gemini-api/docs/pricing). Money is not the constraint. Context size, latency and the CLI quota are.

**Claude as the second reader**
- Claude 4.7 and later reads a 1920x1080 frame without downscaling, at about 2,691 visual tokens. The long edge limit is 2,576 px.
- If a request carries more than 20 images, each image must be 2,000 px or less.
- Source: https://platform.claude.com/docs/en/build-with-claude/vision

---

## 2. Frame sampling strategies

### 2.1 Strategy comparison

| Strategy | Catches | Misses | Starting settings | Use for |
|---|---|---|---|---|
| Uniform fps | Everything at the sampling rate; unbiased coverage | Events shorter than the interval; wastes budget on static shots | 2 fps for clips of 30 s or less; 0.5 to 1 fps as a floor on long videos | Default floor, "review the whole thing" |
| Scene change (`select` scene score, `scdet`, PySceneDetect) | One frame per shot; edit rhythm | Continuous camera moves (drone pans rarely register as cuts), events inside a shot | `gt(scene,0.3)` to `0.4`; `scdet` 8 to 14; `detect-adaptive` 3.0 | Ads, promos, edited content |
| Keyframes / I-frames | Cheap: no full decode | Encoder chooses placement (GOP or encoder scene-cut), so the choice is not about content | `-skip_frame nokey` | Quick look only |
| Motion-adaptive (sample along a frame-difference CDF) | Fast action, gestures, glitches | Important static moments, unless a uniform floor is kept | YDIF or `mafd` weights plus a floor | Sport, drone, AI clips |
| Duplicate removal (`mpdecimate`) | Every visual change in mostly static video | Changes below the thresholds | defaults `hi=768:lo=320:frac=0.33` | Screen recordings, slides |
| Dense burst | Sub-second events; verifying a claim | Anything outside the window | all native frames, ±0.5 to 1 s | Verification pass |
| Contact sheet | Order, pacing, overview, very cheap | Small detail | 3x2 to 4x4 | First look, pacing |
| Native-resolution crop | Small text, logos, hands, UI | Context | 2x Lanczos upscale | Text, detail |
| Model-chosen frames (coarse, then fine) | Long videos, specific questions | Global summary, if used alone | coarse grid, model returns frame IDs, then dense frames | Long tutorials, bug hunts |

### 2.2 Commands

**Build notes**
- Homebrew's core `ffmpeg` is 9.0.2. Its dependencies include `libvmaf`, but not `freetype`, `fontconfig`, `libass`, `harfbuzz` or `whisper-cpp` (https://formulae.brew.sh/formula/ffmpeg). So `drawtext`, the subtitle filters and the `whisper` filter are missing there. That is an inference from the dependency list; check with `ffmpeg -hide_banner -filters | grep -wE 'drawtext|whisper|libvmaf'`.
- The third-party tap `homebrew-ffmpeg/ffmpeg` installs `fontconfig`, `freetype` and `libass` by default: `brew tap homebrew-ffmpeg/ffmpeg && brew install homebrew-ffmpeg/ffmpeg/ffmpeg` (https://github.com/homebrew-ffmpeg/homebrew-ffmpeg).
- The per-filter pages below are an unofficial mirror of the 9.0 docs (https://ayosec.github.io/ffmpeg-filters-docs/9.0/). The official single page is https://ffmpeg.org/ffmpeg-filters.html, with `#filtername` anchors.

**Probe first.** Every later step needs duration, fps, rotation and colour.
```bash
ffprobe -v error -show_format -show_streams -of json in.mp4 > probe.json
```

**Uniform sampling at full resolution, logging each frame's timestamp**
```bash
ffmpeg -hide_banner -i in.mp4 -vf "fps=2,showinfo" -q:v 2 frames/f_%04d.jpg 2> frames.log
# pts_time per saved frame:
grep -oE "n: *[0-9]+ .*pts_time:[0-9.]+" frames.log
```
- `fps` "Convert[s] the video to specified constant frame rate by duplicating or dropping frames". The default `round=near` picks the nearest source frame for each tick (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/fps.html).
- `showinfo` prints `n`, `pts_time`, `iskey`, `type` and more for every frame (https://ffmpeg.org/ffmpeg-all.html#showinfo).
- Use PNG for screen recordings and anything with text. Anthropic warns that "heavy JPEG compression can make text difficult to read" (https://platform.claude.com/docs/en/build-with-claude/vision).
- ffmpeg applies the rotation stored in the file by default, so extracted stills come out upright.

**Exactly N evenly spaced frames, each taken with an accurate seek**
```bash
D=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 in.mp4); N=16
for i in $(seq 0 $((N-1))); do
  t=$(awk -v i=$i -v d=$D -v n=$N 'BEGIN{printf "%.3f", (i+0.5)*d/n}')
  ffmpeg -v error -ss "$t" -i in.mp4 -frames:v 1 "frames/f_$(printf %02d $i)_t${t}.png"
done
```
With `-ss` before `-i`, ffmpeg seeks to the nearest earlier seek point. When transcoding with `-accurate_seek` (the default), "this extra segment between the seek point and position will be decoded and discarded", so the frame is exact (https://ffmpeg.org/ffmpeg-all.html, the `-ss` and `-accurate_seek` entries).

**Minimum spacing between selected frames.** This is the official example, with a 10 s gap:
```bash
-vf "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,10)'"
```

**Scene-change frames, keeping their scores**
```bash
ffmpeg -hide_banner -i in.mp4 \
  -vf "select='gt(scene,0.3)',metadata=mode=print:file=scenes.txt" \
  -fps_mode passthrough scenes/s_%04d.png
```
- `scene` is a "Value between 0 and 1 to indicate a new scene". The official mosaic example is `select='gt(scene,0.4)',scale=160:120,tile` (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Multimedia/select.html).
- How the score is computed, from the source (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/f_select.c):
  - `mafd` is the mean absolute difference between this frame and the previous one;
  - `diff` is `|mafd - prev_mafd|`;
  - `score = clip(min(mafd, diff)/100, 0, 1)`.
- Consequence: a steady pan (high but constant `mafd`) scores low, while flashes and hard cuts score high. That is why drone footage yields few "scenes".
- The score is written to frame metadata as `lavfi.scene_score`.
- In `print` mode, each frame's block starts with a `frame:N pts:X pts_time:T` line, followed by `key=value` lines.
- `-fps_mode passthrough` passes "each frame... with its timestamp from the demuxer to the muxer", so no frames get duplicated (https://ffmpeg.org/ffmpeg-all.html).

**`scdet`, an alternative that exports `mafd` and a score for every frame**
```bash
ffmpeg -hide_banner -i in.mp4 \
  -vf "scdet=threshold=10:sc_pass=1,metadata=mode=print:file=scdet.txt" \
  -fps_mode passthrough cuts/c_%04d.png
```
- Threshold is a percentage. "Good values are in the `[8.0, 14.0]` range", default 10.
- `sc_pass=1` passes only the frames at a scene change.
- Metadata keys: `lavfi.scd.mafd`, `lavfi.scd.score`, and `lavfi.scd.time` (the last only on frames where a change was detected).
- Source: https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/scdet.html

**PySceneDetect v0.7.1** (released 2026-07-21; https://www.scenedetect.com/, https://www.scenedetect.com/docs/latest/cli.html)
```bash
scenedetect -i in.mp4 detect-adaptive list-scenes save-images -n 3
scenedetect -i in.mp4 --stats in.stats.csv detect-adaptive   # per-frame scores
```
- Detector defaults (https://www.scenedetect.com/docs/latest/api/detectors.html):

  | Detector | What it measures | Defaults |
  |---|---|---|
  | `AdaptiveDetector` | Rolling-average ratio, which "suppresses false cuts from camera motion" | `adaptive_threshold=3.0`, `min_content_val=15` |
  | `ContentDetector` | HSV/HSL delta | `threshold=27` |
  | `ThresholdDetector` | Fades | `threshold=12` |
  | `HashDetector` | Perceptual-hash distance | `threshold=0.395` |
  | `HistogramDetector` | Y-histogram difference | `threshold=0.05` |

- The CLI minimum scene length is 0.6 s.
- `save-images -n` saves 3 images per scene by default, including the start and end frames.
- v0.7 moved to PTS-based timestamps, which fixes variable-frame-rate files, and made frame numbers 1-based (https://www.scenedetect.com/changelog/).
- Python: `from scenedetect import detect, AdaptiveDetector; detect("in.mp4", AdaptiveDetector())` (https://www.scenedetect.com/docs/latest/api.html).
- Official benchmark, F1 on the BBC set: Adaptive 91.59, Content 86.69, Hash 83.10, Histogram 79.96 (https://github.com/Breakthrough/PySceneDetect/blob/main/benchmark/README.md).
- TransNetV2 (neural) reports F1 96.2 on BBC (https://github.com/soCzech/TransNetV2). Consider it for gradual transitions and AI morph cuts.

**Keyframes (I-frames)**
```bash
ffmpeg -skip_frame nokey -i in.mp4 -vf showinfo -fps_mode passthrough key/k_%04d.png 2> key.log
# keyframe times without decoding (packet flags contain K):
ffprobe -v error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=p=0 in.mp4 | awk -F, '$2 ~ /K/ {print $1}'
```
- The first command follows the official `tile` example, `ffmpeg -skip_frame nokey -i file.avi -vf 'scale=128:72,tile=8x8' -an -fps_mode passthrough keyframes%03d.png` (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/tile.html).
- Alternative: `select='eq(pict_type,I)'` (select docs above).

**Motion-adaptive sampling.** Build a per-frame motion score, then sample along its cumulative distribution with a uniform floor.
```bash
ffmpeg -hide_banner -i in.mp4 -vf "scale=320:-2,signalstats,metadata=mode=print:key=lavfi.signalstats.YDIF:file=ydif.txt" -an -f null -
```
```python
import re, numpy as np
t, m, cur = [], [], 0.0
for line in open("ydif.txt"):
    if line.startswith("frame:"):
        cur = float(re.search(r"pts_time:(\S+)", line).group(1))
    elif "YDIF=" in line:
        t.append(cur); m.append(float(line.split("=", 1)[1]))
t, m = np.array(t), np.array(m)
w = m + 0.25 * m.mean()            # floor keeps coverage of static parts
cdf = np.cumsum(w) / w.sum()
N = 24
picks = sorted({float(t[np.searchsorted(cdf, (k + 0.5) / N)]) for k in range(N)})
```
- `YDIF` is "the average of sample value difference between all values of the Y plane in the current frame and corresponding values of the previous input frame" (https://ffmpeg.org/ffmpeg-all.html#signalstats).
- The method is our adaptation of two papers:
  - BOLT's inverse-transform sampling (https://arxiv.org/html/2503.21483). With LLaVA-OneVision at 8 frames it improved Video-MME 53.8 to 56.1 and MLVU 58.9 to 63.4.
  - MGSampler's sampling along the cumulative motion distribution (https://arxiv.org/abs/2104.09952).
- The floor term is ours. AKS showed that relevance-only selection can lose to uniform sampling (https://arxiv.org/html/2502.21271).

**Screen recordings: keep only frames where something changed**
```bash
ffmpeg -hide_banner -i rec.mp4 -vf "mpdecimate,showinfo" -fps_mode vfr changes/c_%05d.png 2> changes.log
```
- A frame is dropped when no 8x8 block differs by more than `hi`, and no more than `frac` of blocks differ by more than `lo`.
- Defaults: `hi` 64x12, `lo` 64x5, `frac` 0.33 (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/mpdecimate.html).

**Dense burst around a moment** (every native frame in a 1 s window)
```bash
ffmpeg -hide_banner -ss 00:00:04.500 -i in.mp4 -t 1.0 -vf showinfo -fps_mode passthrough burst/b_%03d.png 2> burst.log
```

**Contact sheet**
```bash
# 16 frames over an 8 s clip (fps = N / duration) into one 4x4 sheet
ffmpeg -hide_banner -i in.mp4 -vf "fps=16/8,scale=480:-2,tile=4x4:padding=8:margin=8:color=white" -frames:v 1 sheet.png
```
`tile` defaults to `layout=6x5`. It has `margin`, `padding`, `color`, `nb_frames` and `overlap` options (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/tile.html).

**Labelling frames without `drawtext`.** Add a label band above the frame so no content is covered.
```python
from PIL import Image, ImageDraw, ImageFont
def label(src, dst, text):
    im = Image.open(src).convert("RGB")
    band = max(28, im.height // 20)
    out = Image.new("RGB", (im.width, im.height + band), "black")
    out.paste(im, (0, band))
    font = ImageFont.load_default(size=int(band * 0.7))   # Pillow >= 10.1, needs FreeType
    ImageDraw.Draw(out).text((8, int(band * 0.12)), text, fill="yellow", font=font)
    out.save(dst)
label("f_07.png", "f_07_lbl.png", "F07  t=00:03.50")
```
- `load_default(size=...)` was "Added in version 10.1.0" and loads Aileron Regular when FreeType is available (https://pillow.readthedocs.io/en/stable/reference/ImageFont.html; current Pillow is 12.3.0).
- ImageMagick alternative, with the file name as the label: `magick montage -label '%t' -pointsize 22 -geometry 480x+6+6 -tile 4x frames/*.png sheet.png`. The official example is `magick montage -label %f -frame 5 ... rose.jpg red-ball.png frame.jpg` (https://imagemagick.org/montage/).
- If your ffmpeg has `drawtext` (it needs `--enable-libfreetype`; see https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/drawtext.html):
  ```bash
  -vf "fps=2,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='%{pts\:hms}  #%{n}':x=10:y=10:fontsize=36:fontcolor=yellow:box=1:boxcolor=black@0.6"
  ```
- NumPro (CVPR 2025) burned red frame numbers, 40 px, in the bottom-right corner (https://arxiv.org/html/2411.10332). It gave big gains for weak open models, and GPT-4o improved by +2.2 mIoU.
- Rule: burn labels only into overview or contact-sheet copies. Never burn them into the stills or crops used for detail or OCR. Always add the text label line before each image (TimeLens, above).

**Zoom and crop tiles for small detail**
```bash
# top-right third of the frame, 2x upscaled
ffmpeg -v error -i f_07.png -vf "crop=iw/3:ih/3:iw*2/3:0,scale=iw*2:-1:flags=lanczos" f_07_c_tr.png
# split into a 3x3 grid of tiles (tiles are written as separate images)
ffmpeg -v error -i f_07.png -vf "untile=3x3" f_07_tile_%d.png
```
- `untile` does the reverse of `tile` (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/untile.html).
- Prefer overlapping crops, computed in a script, so no object is cut exactly at a tile boundary.
- Better still, crop around OCR boxes or regions the model named, and scale so the text x-height is 20 to 30 px. Tesseract notes that x-heights "about 20 pixels" work, and below 10 px "you have very little chance" (https://tesseract-ocr.github.io/tessdoc/tess3/FAQ-Old.html).
- **Why a crop helps (our inference):** on Gemini 3, `media_resolution` sets "the maximum number of tokens allocated per input image". So a crop gets the same budget as a full frame, spent on a smaller area, which means more detail per pixel of the source (https://ai.google.dev/gemini-api/docs/media-resolution).
- **Research support:**
  - ViCrop: TextVQA 47.80 to 56.06 (https://arxiv.org/html/2502.17422).
  - DeepEyes, which crops with a tool: V* 71.2 to 90.1 (https://arxiv.org/html/2505.14362).
  - LENS, a video version: Video-MME 53.3 to 60.7 (https://arxiv.org/abs/2607.25125).

**HDR and anamorphic sources**
- If `color_transfer` is `smpte2084` or `arib-std-b67`, stills extracted without tone mapping look flat and washed out. Do not let the model judge exposure or colour from them.
- If `sample_aspect_ratio` is not 1:1, apply `scale=iw*sar:ih,setsar=1` before extracting stills.
- Both are practical notes, not taken from a single source.

### 2.3 What the research says: frames, sampling and native video

**Denser vs sparser sampling**
- **Short events are missed under sparse sampling.** VideoNIAH (ICLR 2025, 1 s needles) showed "bar-shaped" results: a needle is found only if its frame happened to be sampled (https://arxiv.org/html/2406.09367v3).
- **Gemini 1.5 found a single-frame needle anywhere in 10.5 hours of video.** But that needle was a full frame of large text, guaranteed to be sampled, which says little about small or sub-second details (https://arxiv.org/html/2403.05530v5).
- **The Gemini fps curve (Moment-Video, re-checked):** accuracy jumps from 1 to 5 fps, then plateaus. Human accuracy is 84.33%; the best model (Seed-2.0-Pro) reached 39.6% (https://arxiv.org/html/2606.02522).
- **High frame rate helps motion.** F-16 samples at 16 fps: gymnastics accuracy went from 48.5 to 64.1 moving from 1 to 16 fps (https://arxiv.org/html/2503.13956v2).
- **More frames do not always help.**
  - TOMATO: models plateau after about 8 frames, while humans reach 95.2% with the full video (https://arxiv.org/html/2410.23266).
  - Temporal Chain of Thought: long context "can saturate or degrade accuracy" (https://arxiv.org/html/2507.02001).
  - LongVideoBench: open models degraded at 64 frames, while GPT-4o and Gemini kept improving up to 256 (https://arxiv.org/abs/2407.15754).
- **Uniform 2 fps sampling was the best strategy on Video-MME** for four small VLMs, capped at 96 frames (https://arxiv.org/abs/2509.14769, from the paper body; the abstract stresses task-specific behaviour).

**Resolution vs frame choice**
- Resolution matters for detail, not gist. Gemini 2.5 scored Video-MME 84.7 at low resolution vs 85.2 at default (https://developers.googleblog.com/en/gemini-2-5-video-understanding/).
- Raising VidText resolution from 448² to 896² added 3.2 to 5.0 points (https://arxiv.org/html/2505.22810v1).

**Choosing frames with the model**
- **Two-pass, model-selected frames work with Gemini (re-checked).** Temporal Chain of Thought had Gemini choose frame IDs itself:
  - with a 32K context it beat the 700K-context baseline by 2.8 points on LVBench videos over 1 hour;
  - LVBench overall went from 50.3 to 61.7.

  Source: https://arxiv.org/abs/2507.02001.
- **Coverage still matters for summary-style questions.**
  - Frame-Voyager: CLIP-based retrieval did worse than uniform sampling on "synopsis" tasks (https://arxiv.org/html/2410.03226v4).
  - MaxInfo: selecting for diversity alone, with no question, still added +3.28 on LongVideoBench (https://arxiv.org/abs/2502.03183).
- **A stop rule for adding frames.** Video-RTS doubles the frame count until 5 sampled answers agree (https://arxiv.org/html/2507.06485).

**Mixing resolutions**
- A few high-resolution frames plus many low-resolution ones is token-efficient. Q-Frame's best split was 4 high, 8 medium and 32 low (https://arxiv.org/html/2506.22139v1).
- On Gemini 3 this maps to per-item `resolution` (API only).

**Grids and contact sheets**
- IG-VLM found 6 frames in a 3x2 grid best among 4 to 20 frames. Its authors name "loss of spatial detail" as the limitation (https://arxiv.org/html/2403.18406v1).
- TS-LLaVA pairs one thumbnail grid with tokens sampled from all frames (https://arxiv.org/abs/2411.11066).

**Ads and multi-scene content**
- DistractionBench: all 11 VideoLLMs tested credited actions from inserted ad segments to the main subject (https://arxiv.org/abs/2605.27101).
- Analyse scene by scene, with explicit shot boundaries.

**No head-to-head study of "Gemini native video vs the same frames as images" was found.** The recommendation above rests on:
- the documented token budgets;
- the frame-rate ablation;
- the crop and resolution studies;
- your own drone test.

### 2.4 Sampling recipes by content type

These are recommendations built from the evidence above.

| Content | Floor | Extra frames | Crops | Also send |
|---|---|---|---|---|
| Drone or camera clip, 30 s or less | 2 fps, full resolution | 5 to 8 fps bursts where YDIF peaks | Any signage, text or people region, at native resolution | Measured facts; no "glitch" framing |
| Ad or promo, 60 s or less | 1 frame per shot (start and middle) + 2 fps floor | 0 to 3 s at 6 to 10 fps (hook); end card at 2 fps | Logo, super, CTA and legal text | Shot list, loudness, OCR, ASR |
| AI-generated clip | 4 to 8 fps | Native-fps pairs at every YDIF spike | Hands, faces, text, edges of moving objects | Difference images (section 5.3) |
| Motion graphics | Native fps around every transition; 2 fps elsewhere | Every frame where OCR text appears or disappears | Each text element | Burned frame numbers (overview copies only) |
| Screen recording | Every `mpdecimate`-kept change | ±0.5 s at native fps around clicks and errors | Cursor area, dialogs, console | OCR of every kept frame |
| Tutorial, 10 min or more | Scene or slide changes + 0.2 fps floor | Model-selected segments at 2 to 4 fps | Code and terminal text | ASR with word timestamps |

---

## 3. Deterministic measured QA (ffmpeg / ffprobe)

**The rule:** these numbers go to the model as MEASURED FACTS. The model never estimates them.

**How to run the checks**
- Run each command with `-hide_banner -nostats`, and use `-f null -` when no output file is needed.
- Send stderr to a log and parse it with the regexes in 3.4.
- Or use `metadata=mode=print:file=...` (video) or `ametadata` (audio) for per-frame values.
- Print mode is documented as: "Print key and its value if metadata was found. If key is not set print all metadata values available in frame." Its official examples are `signalstats,metadata=print:key=lavfi.signalstats.YDIF:value=0:function=expr:expr='between(VALUE1,0,1)'` and `silencedetect,ametadata=mode=print:file=metadata.txt` (https://ffmpeg.org/ffmpeg-all.html#metadata_002c-ametadata).

### 3.1 ffprobe container and stream checks

```bash
ffprobe -v error -show_format -show_streams -of json in.mp4 > probe.json
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=nb_read_frames -of default=nw=1:nk=1 in.mp4
ffprobe -v error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=p=0 in.mp4 | awk -F, '$2 ~ /K/ {print $1}'   # keyframe times -> GOP
ffprobe -v trace -i in.mp4 2>&1 | grep -m1 -oE "type:'(moov|mdat)'"   # moov first = fast start (trace format: verify on your build)
```
- ffprobe syntax for `-show_entries`, `-select_streams`, `-read_intervals` and the `json`/`csv`/`flat` writers is documented at https://ffmpeg.org/ffprobe.html.
- Rotation lives in stream side data as a display matrix with a `rotation` value. ffprobe prints it with `print_int("rotation", ...)` (https://github.com/FFmpeg/FFmpeg/blob/master/fftools/ffprobe.c). Parse `streams[].side_data_list[].rotation` from the JSON, and also check the legacy `tags.rotate`.

| Field (from `probe.json`) | Check | Pass rule, where a source exists |
|---|---|---|
| `codec_name`, `profile` | h264 High for YouTube; H.264 for Meta | YouTube recommends H.264 High Profile (https://support.google.com/youtube/answer/1722171); Meta lists "H.264 compression, square pixels, fixed frame rate, progressive scan" (https://www.facebook.com/business/ads-guide/update/video/instagram-reels) |
| `pix_fmt` | `yuv420p` | YouTube wants 4:2:0 chroma (https://support.google.com/youtube/answer/1722171) |
| `color_primaries`, `color_transfer`, `color_space` | bt709 for SDR | YouTube: BT.709 for primaries, transfer and matrix |
| `field_order` + `idet` | progressive | YouTube "Progressive scan (no interlacing)"; Meta progressive |
| `r_frame_rate` vs `avg_frame_rate` + `vfrdet` | constant | Meta: "fixed frame rate" |
| `sample_aspect_ratio` | 1:1 | Meta: "square pixels" |
| `width`, `height`, aspect | platform tables (3.5) | |
| audio `codec_name`, `sample_rate`, `channels`, `bit_rate` | AAC, 48 kHz (YouTube) or 44.1 kHz (FB Reels export), stereo, 128 kbps or more (Meta) | 3.5 |
| keyframe gap | YouTube: "Closed GOP. GOP of half the frame rate" | https://support.google.com/youtube/answer/1722171 |
| moov position | "moov atom at the front of the file (Fast Start)", "No Edit Lists" | same |
| HDR | `smpte2084` or `arib-std-b67` means HDR: use the HDR bitrate table; tone-map before judging stills | same |
| duration: video vs audio vs format | differ by more than 1 frame means A/V length mismatch | practice |

### 3.2 Video detectors

**blackdetect** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/blackdetect.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf "blackdetect=d=0.1:pic_th=0.98:pix_th=0.10" -an -f null - 2>&1 | grep -oE "black_start:[0-9.]+ black_end:[0-9.]+ black_duration:[0-9.]+"
```
- Defaults: `d` (`black_min_duration`) = 2.0 s; `pic_th` = 0.98; `pix_th` = 0.10.
- `d=0.1` catches short black flashes that the 2 s default would ignore.
- Log line format, from the source: `"black_start:%s black_end:%s black_duration:%s"` at INFO level (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_blackdetect.c).

**freezedetect** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/freezedetect.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf "freezedetect=n=-60dB:d=0.5" -an -f null - 2>&1 | grep -oE "freeze_(start|duration|end): [0-9.]+"
```
- Defaults: `n` = -60 dB (0.001), `d` = 2 s.
- Keys: `lavfi.freezedetect.freeze_start`, `freeze_duration`, `freeze_end`. Logged as `"%s: %s"` at INFO level (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_freezedetect.c).
- In motion graphics, a held frame may be intentional. Report it as a flag, not a failure.

**signalstats**: exposure, flicker, legal range, saturation (https://ffmpeg.org/ffmpeg-all.html#signalstats)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf "signalstats,metadata=mode=print:file=sig.txt" -an -f null -
```
- Per frame:
  - `YMIN`, `YLOW` (10th percentile), `YAVG`, `YHIGH` (90th percentile), `YMAX`, each 0 to 255;
  - `SATMIN` to `SATMAX`, 0 to about 181.02;
  - `HUEMED`, `HUEAVG`;
  - `YDIF`, `UDIF`, `VDIF` (difference from the previous frame).
- `out=brng` highlights pixels outside the broadcast range.
- Our heuristics, not from a standard:
  - `YAVG` below about 30 or above about 220 in 8-bit: under- or over-exposed;
  - `YAVG` oscillating in sign several times a second with no cut: flicker or exposure pumping;
  - a `YDIF` spike with no scene cut: a flash or glitch candidate, worth a dense burst.

**Flash screening (photosensitivity).** This is a screen only; certify with Harding or PEAT, the tools WCAG lists (https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html).
- Thresholds from ITU-R BT.1702-3 (https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1702-3-202311-I!!PDF-E.pdf):
  - A harmful flash is a change of 20 cd/m² or more where the darker image is below 160 cd/m².
  - It is not permitted when concurrent flashes cover more than 25% of the screen AND there are more than 3 flashes (6 transitions) in any 1 s.
  - Saturated red transitions count on their own.
  - Patterns: more than 5 light-dark stripe pairs covering more than 40% of the screen (static) or more than 25% (moving).
- SDR luminance model:
  - L = 200 x V^2.4 cd/m².
  - V = (D-64)/876 for 10-bit, per the research pass. For 8-bit limited range, V = (Y-16)/219 is our adaptation.
- Grid approximation: `ffmpeg -i in.mp4 -vf "scale=4:4:flags=area,format=gray" -f rawvideo -` gives 16 cell means per frame. Each cell is 6.25% of the screen, so 4 cells equal 25%. Count opposing changes of 20 cd/m² or more per cell within 1 s windows.
- WCAG 2.3.1 limit: no more than three flashes per second, unless below the general and red flash thresholds. The WCAG area proxy is 341x256 px at 1024x768 (https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html).
- The ffmpeg `photosensitivity` filter is a mitigation filter: `frames` default 30, `threshold` default 1 (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/photosensitivity.html).
  - It measures badness as per-cell luminance differences on an 8x8 grid. It logs `"badness: %6d -> %6d / %6d (%3d%% - %s)"` at VERBOSE level (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_photosensitivity.c).
  - Whether `bypass=1` still logs is **unverified**.

**blurdetect** (https://ffmpeg.org/ffmpeg-all.html#blurdetect)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf "blurdetect=block_width=32:block_height=32:block_pct=80,metadata=mode=print:key=lavfi.blur:file=blur.txt" -an -f null - 2>&1 | grep "blur mean"
```
- Uses the Marziliano perceptual blur metric. Higher means blurrier.
- Per-frame key is `lavfi.blur`. The summary line is `"blur mean: %.7f"` at INFO level (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_blurdetect.c).
- No absolute standard exists. Compare within the video, or against the reference version.

**blockdetect**, the same pattern:
- `blockdetect=period_min=3:period_max=24`
- Key `lavfi.block`; summary `"block mean: %.7f"` (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_blockdetect.c, https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/blockdetect.html).

**idet**: interlacing and field order (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/idet.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf idet -frames:v 600 -an -f null - 2>&1 | grep -E "detection:|Repeated Fields"
```
- Final lines, from the source (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_idet.c):
  - `Single frame detection: TFF:%6d BFF:%6d Progressive:%6d Undetermined:%6d`
  - `Multi frame detection: ...` in the same format
- If TFF plus BFF outweighs Progressive, the source is interlaced and fails the YouTube and Meta progressive requirement.

**cropdetect**: letterbox and pillarbox (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/cropdetect.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf "cropdetect=limit=24:round=2:reset=0" -an -f null - 2>&1 | grep -oE "crop=[0-9]+:[0-9]+:[0-9]+:[0-9]+" | sort | uniq -c | sort -rn | head -1
```
- Defaults: `limit` 24, `round` 16, `skip` 2, `mode` `black` (or `mvedges`). The filter prints `crop=w:h:x:y`.
- A detected height smaller than `ih` means a letterbox; a smaller width means a pillarbox. Example: a 16:9 video boxed inside a 9:16 frame.
- Dark scenes can fool the black mode, so take the most frequent value over the whole video.

**mpdecimate**: duplicate or held frames
```bash
ffmpeg -hide_banner -nostats -loglevel debug -i in.mp4 -vf mpdecimate -an -f null - 2>&1 | grep -c " drop pts:"
```
- The debug line format is `"%s pts:%s pts_time:%s drop_count:%d keep_count:%d"`, where `%s` is `drop` or `keep` (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_mpdecimate.c).
- A regular drop pattern usually means frame-rate conversion.
- Runs of drops where motion is expected mean dropped or held frames in a render.

**vfrdet**: variable frame rate
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vf vfrdet -an -f null - 2>&1 | grep -E "VFR:|min:"
```
- Output lines: `"VFR:%f (%d/%d)"` (the ratio of variable to constant deltas), then `"min: %d max: %d avg: %d"` (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/vf_vfrdet.c).
- Screen and phone recordings are often VFR. Always use `pts_time`, never frame index times fps.

**thumbnail**: "select[s] the most representative frame" per batch; `n` defaults to 100 (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/thumbnail.html). A cheap "best still per shot" picker.

### 3.3 Audio detectors

**Loudness: loudnorm JSON (easiest to parse)**
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -map 0:a:0 -af "loudnorm=I=-14:TP=-1:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p'
```
- The measured fields are `input_i`, `input_tp`, `input_lra` and `input_thresh`.
- `print_format` accepts `summary`, `json` or `none`. `I` defaults to -24, `TP` to -2, `LRA` to 7 (https://ffmpeg.org/ffmpeg-all.html#loudnorm).
- "In dynamic mode, to accurately detect true peaks, the audio stream will be upsampled to 192 kHz."

**Loudness: ebur128 with true peak** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Multimedia/ebur128.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -map 0:a:0 -af "ebur128=peak=true" -f null - 2>&1 | sed -n '/Summary:/,$p'
# short-term maximum (EBU R 128 s1 for ads):
ffmpeg -hide_banner -nostats -i in.mp4 -map 0:a:0 -af "ebur128=metadata=1,ametadata=mode=print:key=lavfi.r128.S:file=r128_S.txt" -f null -
```
- `peak` accepts `none`, `sample` or `true`. `target` defaults to -23 LUFS. Metadata keys are `lavfi.r128.*`.
- The per-frame log line is `"t: %-10s TARGET:%d LUFS M:%6.1f S:%6.1f I:%6.1f LUFS LRA:%6.1f LU"` (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/f_ebur128.c).
- The official analysis example is `ffmpeg -nostats -i input.mp3 -filter_complex ebur128 -f null -` (https://ffmpeg.org/ffmpeg-all.html#ebur128).
- The summary block format was not confirmed from source. Prefer the loudnorm JSON for parsing.
- EBU does not recommend LRA for programmes under 1 minute (https://tech.ebu.ch/docs/r/r128.pdf).

**astats: clipping, DC offset, noise floor** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Audio/astats.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -map 0:a:0 -af "astats=measure_perchannel=none" -f null - 2>&1 | grep -E "DC offset|Peak level dB|RMS level dB|Flat factor|Peak count|Noise floor dB"
```
- Definitions from the docs:
  - DC offset: "mean amplitude displacement from zero".
  - Flat factor: "flatness (i.e. consecutive samples with the same value) of the signal at its peak levels".
  - Peak count: "number of occasions (not the number of samples) that the signal attained either Min_level or Max_level".
- Metadata keys look like `lavfi.astats.Overall.Peak_count`.
- Our heuristics:
  - Peak level of -0.1 dBFS or higher with Flat factor above 0: probable clipping.
  - True peak above -1 dBTP (from ebur128 or loudnorm): delivery fail against EBU, Spotify and AES.
  - A clearly non-zero DC offset, for example above 0.005: flag.

**volumedetect** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Audio/volumedetect.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -map 0:a:0 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume|histogram_0db"
```
- Prints `mean_volume`, `max_volume` and `histogram_XdB`.
- Doc example reading: "raising it by +5 dB causes clipping for 6 samples".
- `max_volume: 0.0 dB` with a non-trivial `histogram_0db` count suggests clipped samples.

**silencedetect** (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Audio/silencedetect.html)
```bash
ffmpeg -hide_banner -nostats -i in.mp4 -vn -af "silencedetect=n=-50dB:d=0.5" -f null - 2>&1 | grep -oE "silence_(start|end): [-0-9.]+( \| silence_duration: [0-9.]+)?"
```
- Defaults: `n` = -60 dB, `d` = 2 s. `mono=1` checks each channel separately.
- Log formats: `"silence_start: %s"`, and `"silence_end: %s | silence_duration: %s"` (https://github.com/FFmpeg/FFmpeg/blob/master/libavfilter/af_silencedetect.c).

### 3.4 One decode pass, and a parse table

```bash
ffmpeg -hide_banner -nostats -i in.mp4 -filter_complex \
"[0:v]blackdetect=d=0.1,freezedetect=n=-60dB:d=0.5,cropdetect=round=2,idet,vfrdet,signalstats,metadata=mode=print:file=v_meta.txt[v];\
 [0:a]ebur128=peak=true,astats=measure_perchannel=none,silencedetect=n=-50dB:d=0.5,volumedetect[a]" \
-map "[v]" -map "[a]" -f null - 2> qa.log
```
- Check that an audio stream exists first (ffprobe). Without one, the `[0:a]` branch fails.
- cropdetect and ebur128 log one line per frame, so `qa.log` gets large. Separate passes are cleaner if time allows.

| Source | Regex |
|---|---|
| blackdetect | `black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)` |
| freezedetect | `lavfi\.freezedetect\.freeze_(start\|duration\|end): ([\d.]+)` |
| silencedetect | `silence_start: (-?[\d.]+)` and `silence_end: ([\d.]+) \| silence_duration: ([\d.]+)` |
| idet | `(Single\|Multi) frame detection: TFF:\s*(\d+) BFF:\s*(\d+) Progressive:\s*(\d+) Undetermined:\s*(\d+)` |
| vfrdet | `VFR:([\d.]+) \((\d+)/(\d+)\)` |
| cropdetect | `crop=(\d+):(\d+):(\d+):(\d+)` (take the mode) |
| blurdetect / blockdetect | `blur mean: ([\d.]+)` and `block mean: ([\d.]+)` |
| volumedetect | `max_volume: (-?[\d.]+) dB`, `histogram_(\d+)db: (\d+)` |
| astats | `Peak level dB: (\S+)`, `Flat factor: ([\d.]+)`, `Peak count: (\d+)`, `DC offset: (-?[\d.]+)` |
| loudnorm | JSON block: `input_i`, `input_tp`, `input_lra`, `input_thresh` |
| metadata print files | `^frame:(\d+)\s+pts:(\S+)\s+pts_time:(\S+)`, then `^(lavfi\.[\w.]+)=(\S+)` |
| showinfo | `n:\s*(\d+).*?pts_time:([\d.]+)` |

### 3.5 Platform delivery specs, checked 2026-09-24

**Instagram Reels, organic** (https://www.facebook.com/help/instagram/1038071743007909/, https://www.facebook.com/help/instagram/2720958398006062/)
- Aspect ratio "between 1.91:1 and 9:16". Minimum frame rate 30 fps. Minimum resolution 720 px.
- Up to 20 minutes, but "Reels over 3 minutes won't be recommended to new audiences".

**Instagram Reels ads** (https://www.facebook.com/business/ads-guide/update/video/instagram-reels)
- 9:16, 1440x2560 recommended. MP4 or MOV.
- "H.264 compression, square pixels, fixed frame rate, progressive scan and stereo AAC audio compression at 128 kbps+".
- Minimum width 250 px for ads under 30 s, 500 px for 30 s or longer. Duration 0 s to 15 min. Up to 4 GB.
- **Safe zone:** "Consider leaving at least 14% of the top, 35% of the bottom and 6% on each side of your asset free from text, logos or other important creative elements."
- On 1080x1920 that is a safe box of x 65 to 1015, y 269 to 1248 (our arithmetic).

**Instagram Stories ads** (https://www.facebook.com/business/ads-guide/update/video/instagram-story)
- 9:16, 1440x2560, duration 1 s to 60 min, up to 4 GB, aspect tolerance 1%.
- Same 14% / 35% / 6% safe zone.
- Videos of 16 s or longer "may be split" into cards.

**Instagram Feed ads** (https://www.facebook.com/business/ads-guide/update/video/instagram-feed)
- The page lists 9:16 at 1080x1920, duration 1 s to 60 min. Facebook Feed recommends 4:5 instead.
- How Instagram masks 9:16 in the feed is **unverified**. Treat "key content survives a centred 1080x1350 crop" as a warning, not a hard fail.

**Facebook, organic reels**
- About Meta, 2025-06-17: "all videos on Facebook will be shared as reels", with no "length or format restrictions" (https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/).
- Recommended export (https://www.facebook.com/help/1041366099316573):
  - H.264 with AAC, in MP4 or MOV;
  - "Maximum width of 4,000 pixels, with dimensions divisible by 16";
  - "30 frames per second (fps) or lower";
  - stereo at 44,100 Hz;
  - under 10 GB.

**Facebook ads**
- Reels ads: 9:16, 1440x2560, "No maximum limit" on duration, same 14/35/6 safe zone (https://www.facebook.com/business/ads-guide/update/video/facebook-facebook-reels).
- Feed ads: 4:5, 1440x1800, 1 s to 241 min (https://www.facebook.com/business/ads-guide/update/video).
- Stories ads: 1 s to 3 min. "roughly 14% (250 pixels) of the top and 20% (340 pixels) of the bottom" (https://www.facebook.com/business/ads-guide/update/video/facebook-story).
  - The pixel values and the percentages disagree on a 1920 px frame. Use the percentages; they are stricter.

**TikTok**
- **Organic** (developer media guide, updated 2026-08-04; https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide):
  - MP4 (recommended), WebM or MOV; H.264 recommended, also H.265, VP8, VP9;
  - 23 to 60 fps; 360 to 4096 px; up to 4 GB;
  - "All TikTok creators can post 3-minute videos, while some have access to post 5-minute or 10-minute videos."
- **In-Feed auction ads** (https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en):
  - 9:16 at least 540x960, 16:9 at least 960x540, 1:1 at least 640x640;
  - up to 10 min; up to 500 MB; bitrate at least 516 kbps.
- **Reservation In-Feed and TopView ads** (https://ads.tiktok.com/help/article/tiktok-reservation-topview): 5 to 60 s (9 to 15 s recommended), bitrate at least 2,500 kbps.
- **Safe zone:** no official pixel values appear in page text; they exist only in downloadable templates. Third-party values conflict, so they are **unverified**.
  - A conservative box that covers all published third-party values on 1080x1920: top 150, bottom 484, left 60, right 140 (a derivation, not a spec).
- **Hook guidance** (https://ads.tiktok.com/help/article/creative-best-practices?lang=en, updated June 2025):
  - "Introduce your content proposition in the first 3 seconds".
  - "Prioritize your hook in the first 6 seconds".
  - "5-10 words per second" for on-screen text. That is quoted as written but far above subtitle reading norms, so don't use it as a limit.

**YouTube Shorts**
- Organic (https://support.google.com/youtube/answer/15424877): up to 3 minutes, square or vertical, for uploads after October 15, 2024.
- Shorts ads (https://support.google.com/google-ads/answer/16041697):
  - only "the first 60 seconds will play on the Shorts feed";
  - the CTA button appears at 3 s (Performance Max, App, Demand Gen) or at 10 s (Video View campaigns).
- **Conflict:** another Google Ads page lists Shorts ads as "6-60 seconds" (https://support.google.com/google-ads/answer/17091270).
- A Shorts text safe area is not published in text: **unverified**.

**YouTube long-form: recommended upload encoding** (https://support.google.com/youtube/answer/1722171)
- **Container:** MP4, "No Edit Lists", moov atom at the front.
- **Audio:** AAC-LC or Opus, 48 kHz. Stereo 384 kbps, mono 128 kbps, 5.1 512 kbps.
- **Video:** H.264 High Profile, progressive, 2 consecutive B-frames, "Closed GOP. GOP of half the frame rate", CABAC, variable bitrate, 4:2:0.
- **Colour:** BT.709 for SDR.

YouTube SDR bitrate (Mbps):

| Resolution | 24 to 30 fps | 48 to 60 fps |
|---|---|---|
| 2160p | 35 to 45 | 53 to 68 |
| 1440p | 16 | 24 |
| 1080p | 8 | 12 |
| 720p | 5 | 7.5 |

YouTube HDR bitrate (Mbps):

| Resolution | 24 to 30 fps | 48 to 60 fps |
|---|---|---|
| 2160p | 44 to 56 | 66 to 85 |
| 1080p | 10 | 15 |

**Google Ads**
- Sizes (https://support.google.com/google-ads/answer/13547298): recommended 1920x1080, 1080x1920 or 1080x1080; minimum 1280x720, 720x1280 or 480x480.
- Durations (https://support.google.com/google-ads/answer/2375464): bumper 6 s; non-skippable in-stream 15 to 60 s.

**LinkedIn video ads** (https://www.linkedin.com/help/lms/answer/a424737)
- MP4, 75 KB to 500 MB, 3 s to 30 min. Frame rate "Less than 30 FPS". Captions as SRT only.

**X**: official pages returned HTTP 402, so **unverified**.

### 3.6 Loudness targets

| Standard or service | Integrated | True peak | Source |
|---|---|---|---|
| EBU R 128 (broadcast) | -23.0 LUFS, ±0.2 LU in QC | ≤ -1 dBTP | https://tech.ebu.ch/docs/r/r128.pdf |
| EBU R 128 s1 (ads and promos) | -23.0 LUFS; maximum short-term -18.0 LUFS; LRA not applicable | -1 dBTP | https://tech.ebu.ch/docs/r/r128s1.pdf |
| EBU R 128 s2 (streaming) | interim distribution -20 to -16 LUFS | | https://tech.ebu.ch/docs/r/r128s2.pdf |
| ATSC A/85:2026-07 | -24 LKFS; streaming services -23 to -27 LKFS | -2 dBTP | https://www.atsc.org/wp-content/uploads/2026/07/A85-2026-07-Annex-M.pdf |
| AES TD1008 (not intended for sound with picture) | speech -18 LUFS; music -16 or -14; interstitials -18 | ≤ -1 dBTP | https://aes.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf |
| Spotify | -14 LUFS default | below -1 dBTP (below -2 if louder than -14) | https://support.spotify.com/us/artists/article/loudness-normalization/ |
| YouTube | **no official target**; -14 LUFS is widely quoted by third parties | | https://www.meterplugs.com/blog/2022/03/23/apple-switch-to-lufs.html |
| Apple Podcasts | about -16 LKFS ±1 | ≤ -1 dBFS | https://podcasters.apple.com/support/893-audio-requirements |
| Netflix (partially verified; the page is now behind a sign-in) | -27 LKFS ±2, dialogue-gated | ≤ -2 dBTP | https://partnerhelp.netflixstudios.com/hc/en-us/articles/360001794307-Netflix-Sound-Mix-Specifications-Best-Practices-v1-6 |
| TikTok, Instagram | **no published target**; practice is about -14 LUFS and -1 dBTP (**unverified**) | | |

**Measurement definitions**
- Momentary loudness uses a 0.4 s window, short-term a 3 s window. Integrated loudness is gated at -70 LUFS absolute and -10 LU relative (https://tech.ebu.ch/docs/tech/tech3341.pdf).
- LRA is the 95th minus the 10th percentile of short-term loudness (https://tech.ebu.ch/docs/tech/tech3342.pdf).

**House rule for social deliverables** (a recommendation, not any platform's spec)
- Aim for -14 to -16 LUFS integrated.
- Fail if true peak is above -1 dBTP.
- Flag integrated loudness below -20 or above -10 LUFS.

### 3.7 Captions, legibility, safe areas

**Netflix captions**
- General requirements (https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements): minimum duration "5/6 (five-sixths) of a second", maximum 7 s, at most 2 lines.
- English (USA) guide (https://partnerhelp.netflixstudios.com/hc/en-us/articles/217350977-English-USA-Timed-Text-Style-Guide): 42 characters per line; up to 20 characters per second for adults and 17 for children.
- Timing guidelines (https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines): gaps of at least 2 frames.

**WCAG 2.2** (https://www.w3.org/TR/WCAG22/)
- 1.2.2 Captions (Prerecorded), Level A.
- 2.3.1 Three Flashes or Below Threshold.
- Contrast: 4.5:1 for normal text and 3:1 for large text; this also applies to images of text (https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- WCAG is a web standard. Use it as a proxy for burned-in text.

**Safe areas**
- EBU R 95 (https://tech.ebu.ch/docs/r/r095.pdf): action safe 3.5% and graphics safe 5% on each edge.
- At 1920x1080 that is 67/38 px and 96/54 px.

**Examples of derived checks**
- A 30-character super needs at least 1.5 s on screen at 20 characters per second.
- An OCR box that intersects a platform's unsafe zone is flagged.

**BBC words-per-minute figures**: the site was blocked, so **unverified**.

---

## 4. Reducing hallucination in video-LLM answers

### 4.1 What the research shows

**How the drone errors map to known categories** (taxonomy from https://arxiv.org/abs/2503.19622, https://arxiv.org/abs/2305.10355)
- The invented sign text is an OCR or detail hallucination at low resolution.
- The hi-vis vest is a co-occurrence prior. POPE found that hallucinated objects are the frequent ones, and the ones that co-occur with real objects in the scene.
- "AI morphing" on real footage is an in-context conflict: the question itself asserted a false premise. That is HAVEN's worst category, with about 22% average accuracy against about 48% for prior conflict.

**Yes-bias**
- VideoHallucer: "Most models exhibit a strong bias toward answering 'yes'" (https://arxiv.org/abs/2406.16338).
- Gemini-1.5-Pro scored 83.6% on basic questions but 42.3% on the paired hallucination questions.

**False premises and sycophancy**
- MAD-Bench (https://arxiv.org/abs/2402.13220): adding a "think twice" paragraph lifted GPT-4V from 82.82 to 92.23. Its exact wording is **unverified**, because the paper shows it only as an image.
- ViSE (https://arxiv.org/html/2506.07180v3):
  - polite "suggestive" bias can cause more sycophancy than strong bias;
  - a contradiction-checking prompt made it worse;
  - majority vote left it unchanged, at 44.71 vs 44.92.
- "Caved or Convinced" (https://arxiv.org/html/2608.03160): when events fall between sampled frames, all nine tested models accepted true and false claims equally often.
- "Looking Again", a single source (https://arxiv.org/html/2608.28623): share of reasoning chains that gave in under user pressure was Gemini-3-Flash-Preview 30.84%, Claude-Sonnet-4.6 60.35%, GPT-5.4-Mini 78.88%.

**Language priors**
- 31.15% of Video-MME questions can be answered without the video (https://arxiv.org/abs/2505.14321).
- VideoHallu (https://arxiv.org/abs/2505.01481): models "rely on their embedded commonsense and physics priors ... even when prompted to rely on video content".

**Thinking can drift away from the pixels**
- Video-VER (https://arxiv.org/html/2510.06077): chain of thought lowered Qwen2.5-VL-7B on Video-MME from 59.2 to 54.7.
- Video-MME-v2 found thinking "sometimes degrading" results on purely visual questions (https://arxiv.org/html/2604.05015v1).
- So ground any reasoning in an explicit list of observations.

### 4.2 Known failure modes and what to do about each

| Failure mode | Evidence (best model vs human) | What the skill does |
|---|---|---|
| Small text / OCR | VidText: Gemini 1.5 Pro 46.8% vs human 89.5% (https://arxiv.org/html/2505.22810v1); MME-VideoOCR best 73.7% (https://arxiv.org/abs/2505.21333) | OCR plus native-resolution crops; "unreadable" rule; OCR is authoritative for strings |
| Counting | VNBench counting 36.7% for Gemini 1.5 Pro (https://arxiv.org/html/2406.09367v3); EC-Bench 23.74% vs human 82.97% (https://arxiv.org/html/2603.29943v2) | List each instance with frame and position, then count; listing first "consistently improves Counting accuracy" (EC-Bench) |
| Fast or fine motion | MotionBench under 60% (https://arxiv.org/html/2501.02955); FAVOR-Bench 49.87% (https://arxiv.org/html/2503.14935) | Dense bursts at 5 to 10 fps; measured YDIF |
| Temporal order | TOMATO 37.9% vs 95.2% (https://arxiv.org/html/2410.23266); Vinoground best 56.6 vs 90.0 (https://vinoground.github.io/) | Labelled consecutive frames; reversal probe (4.4) |
| Object permanence / consistency | TOC-Bench 47.1% vs 89.3% (https://arxiv.org/html/2605.09904) | Ask per frame range ("what is visible in F10 to F14"), not "what happened next" (MoHallBench, https://arxiv.org/abs/2607.01117) |
| Camera motion read as static, or as object motion | CameraBench: standard VLMs "at or below chance" on camera-motion questions; zoom vs dolly confused (https://arxiv.org/html/2504.15376) | Claim camera motion only with parallax or scale evidence across cited frames |
| Brief events | Moment-Video best 39.6% vs 84.33% (https://arxiv.org/html/2606.02522) | Motion-adaptive sampling; 5 fps floor in windows of interest |
| Single-frame bias | Strong scores are possible with no temporal understanding (https://arxiv.org/abs/2206.03428) | Shuffled-frame control for temporal claims |
| Cross-scene misattribution | DistractionBench, 11 of 11 models (https://arxiv.org/abs/2605.27101) | Scene-by-scene analysis with explicit cut list |

### 4.3 Current benchmark results

| Model | Result | Setting / source |
|---|---|---|
| Gemini 3 Pro | Video-MMMU 87.6% | media_resolution HIGH, temperature 0; GDM eval PDF (https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_model_evaluation.pdf) |
| Gemini 3 Flash | Video-MMMU 86.9% | same method (https://storage.googleapis.com/deepmind-media/gemini/gemini_3_flash_model_evaluation.pdf) |
| GPT-5.2 (xhigh) / Claude Sonnet 4.5 | Video-MMMU 85.9% / 77.8% | computed by GDM (same PDFs) |
| Gemini 3.7 Flash; Claude Sonnet 5; GPT-5.6 Terra | LVBench 85.4 / 68.5 / 78.9 | 1,024 frames; Claude 300 "due to API limitations" (https://storage.googleapis.com/deepmind-media/gemini/gemini_3-7_flash_model_evaluation.pdf) |
| Gemini 3.8 Flash; Claude Opus 5; GPT-5.6 Sol | LVBench 87.8 (agentic) or 87.1 (static); 75.4; 82.1 | https://storage.googleapis.com/deepmind-media/gemini/gemini_3-8_flash_model_evaluation.pdf |
| Gemini 3 Pro / 3 Flash / GPT-5 | Video-MME-v2 average accuracy 66.1 / 61.1 / 55.6; grouped score 49.4 / 42.5 / 37.0; human expert 90.7 / 94.9 | https://arxiv.org/html/2604.05015v1 |
| Gemini 3 Pro High (reported by ByteDance) | VideoMME 88.4, MotionBench 70.3, TOMATO 55.8, LongVideoBench 78.2 | https://seed.bytedance.com/en/seed2 |
| Seed2.0 Pro (reported by ByteDance) | VideoMME 89.5, MotionBench 75.2, TOMATO 59.9 | same |
| InternVL3.5-241B | Video-MME 72.9 (no subtitles), MVBench 76.5, LongVideoBench 67.1 | https://arxiv.org/html/2508.18265v1 |

**Gaps**
- No official Gemini 3.x numbers were found for MVBench, TemporalBench, MLVU, EgoSchema or Perception Test.
- The Video-MME and LongVideoBench leaderboards are stale (https://video-mme.github.io/home_page.html, https://longvideobench.github.io/).
- GPT-5's VideoMMMU 84.6% is **unverified** (openai.com returned 403).

**Reading of the numbers:** knowledge-style video QA sits in the high 80s. Motion, temporal and grounded-evidence scores are far lower, and those are exactly what QA work needs.

### 4.4 The anti-hallucination contract

Each rule, with its evidence:

1. **Neutral task framing.** State no presumed defect. Offer "none observed" explicitly.
   - Evidence: HAVEN's in-context conflict category (https://arxiv.org/abs/2503.19622); MAD-Bench; ViSE.
2. **Describe, then analyse.** First pass: a neutral per-frame inventory. Second pass: the task.
   - Google's own troubleshooting advice is to "try asking the model to describe the image(s) or video before providing the task instruction" (https://ai.google.dev/gemini-api/docs/files).
   - LLoVi's caption-then-reason approach added 18.1 points on EgoSchema (https://arxiv.org/abs/2312.17235).
3. **Evidence on every claim.** Frame ID(s), MM:SS.ss timestamp, region (for example top-right), and evidence type: measured, OCR, visual, audio or inferred.
   - Claims without evidence are dropped.
   - Evidence: VideoZeroBench (above).
4. **Unreadable beats a guess.** Quote text only when every character is legible in a frame or crop. Otherwise write `[unreadable]`, or quote the legible part with `?` for unclear characters. Say whether you agree with the OCR.
   - VirtueBench's instruction "If the frames do not provide enough information, DO NOT guess..." increased refusals where they were warranted, and removing it made refusal "drop notably" (https://arxiv.org/abs/2603.07071).
5. **No claims about what happens between frames.** Write "not observable at this sampling".
   - Evidence: Caved or Convinced; VideoNIAH.
6. **Counts only by listing instances** (EC-Bench above).
7. **Camera motion only with visible parallax or scale change** (CameraBench).
8. **Observed and inferred stay separate.** Measured facts override visual impressions for timing, loudness, black or frozen frames, and resolution.
9. **Confidence is categorical, tied to evidence.**
   - High: visible in 2 or more frames, or measured.
   - Medium: visible in 1 frame.
   - Low: partial or ambiguous.

   Verbalized confidence is better calibrated than token probabilities for RLHF models (https://arxiv.org/abs/2305.14975), but LLMs "tend to be overconfident" (https://arxiv.org/abs/2306.13063), and so do VLMs (https://arxiv.org/abs/2405.02917). Use it to prioritise review only.
10. **Factored verification.** Each defect, text or count claim is re-asked in a fresh call, on dense frames and crops, as a neutral question that does not reveal the claim.
    - Chain-of-Verification's factored variant works better because models that see their earlier output "tend to repeat" its hallucinations (https://arxiv.org/abs/2309.11495).
11. **Reversal and shuffle probes for motion and order claims.** Ask the direction or order question on reversed or shuffled frames. If the answer does not change, the claim is not coming from the visual evidence.
    - MotionCD, contrasting original and reversed playback, improved results by up to 15.1% (https://ojs.aaai.org/index.php/AAAI/article/view/32463).
    - The reversal test in https://arxiv.org/html/2608.03160 reached 0.92 to 1.00 accuracy on models that can read order.
12. **Repeated runs are a flag, not a vote.** Run the task 2 to 3 times at temperature 1.0. A claim that appears in only one run gets low confidence and goes to verification.
    - Self-consistency helps reasoning (https://arxiv.org/abs/2203.11171), but did not fix sycophancy (ViSE).
13. **A second model, reading the pixels independently.** Claude, in the host session, reads the same frames and crops and answers the same neutral verification questions.
    - Evidence on multi-agent approaches is mixed. Debate does "not reliably outperform" self-consistency (https://arxiv.org/abs/2311.17371), while cross-examination catches inconsistencies (https://arxiv.org/abs/2305.13281).
    - Keep it independent and neutral: in "Looking Again", Claude-Sonnet-4.6 gave in under pressure 60.35% of the time.

**Rewriting prompts to be neutral**

| Leading prompt | Neutral replacement |
|---|---|
| "Find the glitches." | "List any frame-to-frame inconsistencies you can point to (frame and region), or write none observed. For each, name the most likely ordinary cause and whether the frames rule it out." |
| "Is the logo visible in the first 3 seconds?" (invites yes-bias) | "In F01 to F06 (00:00 to 00:03), list every logo or brand name with frame and region; if none, write none." |
| "What does the sign say?" | "Transcribe crop C3 character by character; mark unclear characters with ?; if fewer than half are legible, write unreadable." |
| "Count the people." | "List each person with frame and position; then give the count." |

### 4.5 OCR as ground truth for text

**Tesseract** (https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html, https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html)
```bash
tesseract crop.png stdout --psm 11 -l eng tsv   # per-word 'conf' column; --psm 6 = block, 7 = single line
```
- Scale crops so the text x-height is 20 to 30 px (https://tesseract-ocr.github.io/tessdoc/tess3/FAQ-Old.html). The docs also recommend at least 300 DPI and about a 10 px border.
- Bengali is available as `ben` (https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html).

**Apple Vision**
- `VNRecognizeTextRequest` exposes `recognitionLevel` (accurate or fast), `usesLanguageCorrection`, `recognitionLanguages`, `customWords` and `minimumTextHeight` (https://developer.apple.com/tutorials/data/documentation/vision/vnrecognizetextrequest.json).
- `minimumTextHeight` defaults to 1/32 of the image height, about 34 px on a 1080p frame (https://developer.apple.com/tutorials/data/documentation/vision/vnrecognizetextrequest/minimumtextheight.json). Lower it, or crop.
- Minimal script, run with `swift ocr.swift frame.png`:
```swift
import Foundation; import Vision; import AppKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let img = NSImage(contentsOf: url),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else { exit(1) }
let req = VNRecognizeTextRequest { r, _ in
  for case let o as VNRecognizedTextObservation in r.results ?? [] {
    if let c = o.topCandidates(1).first {
      let b = o.boundingBox   // normalized, origin bottom-left
      print(String(format: "%.3f\t%.4f\t%.4f\t%.4f\t%.4f\t%@", c.confidence, b.minX, b.minY, b.width, b.height, c.string))
    }
  }
}
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false   // keep raw strings so real typos in supers are not auto-"fixed" (our inference)
req.minimumTextHeight = 0.01
try VNImageRequestHandler(cgImage: cg).perform([req])
```
- Wrappers:
  - ocrit (https://github.com/insidegui/ocrit)
  - macOCR, with `--json` output (https://github.com/schappim/macOCR)
  - ocrmac, a Python library that returns confidence and boxes (https://github.com/straussmaximilian/ocrmac)
- **Bengali:** not in the lists found for Vision or Live Text, so treat it as unsupported (**unverified for macOS 26**). Check `supportedRecognitionLanguages()` on the machine.
- For Bangla use Tesseract `ben` or EasyOCR `bn` (https://github.com/JaidedAI/EasyOCR).

**Using OCR in the skill**
- Text below a confidence threshold, for example 0.5, becomes "unreadable" in the facts given to the LLM.
- Text that the LLM and OCR disagree on becomes a verification item.

---

## 5. Use-case playbooks

Every playbook uses the same pattern: measure, then sample, then describe, then analyse, then verify. Prompts follow the section 4.4 contract, with the task and rules at the end of the packet.

### 5.1 Debugging a screen recording of a software bug

**Evidence**
- Frame rate and indicators decide success:
  - V2S needs at least 30 fps, full device resolution and Android "Show Touches" (https://arxiv.org/abs/2005.09057).
  - In CAPdroid's sample, 89% of GitHub bug recordings showed a touch indicator.
- CAPdroid segments actions with luma SSIM between consecutive frames (https://arxiv.org/abs/2302.00886):
  - a sharp drop is a tap or navigation;
  - a drop followed by a gradual rise is a scroll;
  - repeated drops with a keyboard on screen is typing;
  - a plateau is loading.

  It reached 0.84 video-F1 and made reproduction 59.8% faster.
- ViBR (https://arxiv.org/html/2604.19905) lists the failure causes:
  - masked input fields;
  - loading delays that cause over-segmentation;
  - dynamic ads and video playback.
- Keyframes cover the bug moment well. FFmpeg keyframes kept a median 1.90% of frames and still caught the bug frame 98.79% of the time (https://arxiv.org/abs/2508.04895).
- Models still struggle with dynamic GUIs:
  - GUI-World (https://arxiv.org/abs/2406.10819);
  - VideoWebArena, where the best agent scored 13.3% vs 73.9% for humans on factual retention (https://arxiv.org/abs/2410.19100).

**Commercial reference fields**
- Jam captures URL, timestamp, device, browser, OS, console logs, network requests, clicks, navigation and typed input (https://jam.dev/docs).
- Loom's AI workflow produces steps to reproduce from the transcript (https://support.atlassian.com/loom/docs/use-ai-workflows/).

**Recording advice to give users**
- Android "Show taps" and "Pointer location" (https://developer.android.com/studio/debug/dev-options).
- macOS Screenshot app, "Show Mouse Clicks" (https://support.apple.com/en-us/102618).
- 30 fps or more, native resolution.
- A visible clock and DevTools open are our suggestions (**unverified**).

**Measure**
- ffprobe: fps, VFR, resolution.
- `mpdecimate` change frames.
- A per-frame SSIM or YDIF series to find action boundaries.
- OCR on every kept frame: error strings, URLs, versions.

**Sample**
- Every changed frame, plus ±0.5 s at native fps around each boundary.
- A 2x crop around the cursor or touch dot and around any dialog.

**Prompt pattern** (after the inventory pass)
```
You are reproducing a software bug from stills of a screen recording. Use only what is visible (frames, crops, OCR, measured boundaries).
1. List user actions in order: t_start/t_end (MM:SS.ss), action (tap|click|long_press|swipe|scroll|type|shortcut|navigate|wait), target (visible label), region, typed_text (verbatim | "masked" | "not visible"), evidence (touch dot, click ring, focus change, keyboard), inferred (true if the input itself is not visible), confidence.
2. Loading waits with durations (from measured boundaries).
3. First frame where the failure is visible; verbatim error text from OCR.
4. Environment clues visible on screen (OS, browser, app version, clock).
5. Title, summary, numbered repro steps, expected vs actual, open questions.
Never invent clicks or typed text; write "touch not visible" when there is no indicator.
```

**Verify**
- Re-extract every step's frames and confirm the target label with OCR.
- Error text is always taken from OCR.

### 5.2 Reviewing an ad or promo

**Evidence**
- Google ABCD reports a 30% lift in short-term sales likelihood and a 17% lift in long-term brand contribution (https://support.google.com/google-ads/answer/14783551).
- ABCD playbook (https://www.thinkwithgoogle.com/_qs/documents/8472/ABCD_Complete_V7b_HR_1.pdf):
  - "Introduce your brand or product in the first 5 seconds";
  - "Aim for 2+ shots in the first 5 seconds";
  - tight framing, supers, and CTAs by text and voice;
  - brand mentions by people on screen beat voiceover.
- Google's open-source ABCD Detector (https://github.com/google-marketing-solutions/abcds-detector):
  - Checks include Quick Pacing, Dynamic Start, Supers, Supers with Audio, Brand Visuals, Brand Mention (Speech), Product Visuals and Mentions, Visible Face (Close Up), Presence of People, Overall Pacing, and Call To Action (Text and Speech).
  - A May 2026 update added 20 YouTube Shorts attributes.
  - It trims an actual 0 to 5 s clip for the early checks, rather than telling the model to focus on the first 5 seconds.
  - Pacing and Dynamic Start come from shot annotations, not from the LLM.
  - Config: `early_time_seconds=5`, `avg_shot_duration_seconds=2`, `dynamic_cutoff_ms=3000`, `confidence_threshold=0.5`.
  - Score is passed checks ÷ total. 80 or above is "Excellent"; 65 to 79 is "Might Improve".
  - Its README warns the tool is "prone to hallucinations".
- TikTok: proposition in the first 3 s, hook in the first 6 s (https://ads.tiktok.com/help/article/creative-best-practices?lang=en). "90% of ad recall impact is captured within the first six seconds" (https://ads.tiktok.com/business/en/blog/creative-best-practices-top-performing-ads).
- Meta:
  - "Over 75% of Reels views on Instagram are sound on"; keep the hook and CTA inside the safe zone (https://developers.facebook.com/blog/post/2024/11/07/unlock-the-power-of-reel-ads/).
  - Recall after "0.25 seconds of exposure" (https://www.facebook.com/iq/articles/capturing-attention-feed-video-creative).
  - Meta's own wording for "hook in the first 3 s" is **unverified**.

**Measure**
- Shot list (`scdet` or PySceneDetect). From it compute:
  - Dynamic Start: first cut under 3 s;
  - Quick Pacing: 5 or more shots in any 5 s window;
  - mean shot length.
- Loudness and true peak.
- Black or frozen frames.
- OCR every shot, and test each box against the platform safe zones (3.5).
- ASR with word timestamps for brand, product and CTA mentions.
- Muted-viewing check: can brand, offer and CTA be read with the sound off?

**Sample**
- 0 to 3 s at 6 to 10 fps (the hook).
- One frame at the start and middle of every shot.
- The end card at 2 fps.
- Crops of logo, supers and legal text.
- Analyse scene by scene (DistractionBench).

**Prompt pattern:** one call per feature group, detector-style.
```
For each feature return {id, detected, confidence, rationale, evidence:[{frame, t, region, what}]}. Brand <name + variations>; products <list>; valid CTAs <list>.
Early window (F01-F12 = 00:00-00:03, labelled): brand name/logo visible; product visible; person/face visible; on-screen text (quote OCR).
Whole ad: supers present and whether they match speech (use transcript); CTA as text; CTA spoken; logo placement type (in story / on product / super / watermark).
Muted pass: can brand, offer and CTA be understood without audio? Cite frames.
Do not score pacing, cuts, loudness or safe zones; they are measured and given below.
```

### 5.3 Detecting AI-generated artifacts without false positives

**Evidence**
- **Artifact taxonomies**
  - BrokenVideos, with pixel-level masks: "temporally inconsistent motion, physically implausible trajectories, unnatural object deformations, and local blurring" (https://arxiv.org/abs/2506.20103).
  - Spotlight's six error types: Physics, Appearance/Disappearance, Logical, Motion, Anatomy (including "unrealistic morphing"), Adherence. Asking about each type in a separate query took a small VLM from 0.148 to 0.254 (https://arxiv.org/html/2511.18102).
  - VBench-2.0 dimensions include Human Anatomy, Identity, Mechanics and Material (https://arxiv.org/html/2503.21755v2).
- **How well models detect AI video**
  - RA-Bench: Gemini-3.1-Pro-Preview had the best zero-shot score, 63.4 balanced accuracy, and social-media sharing makes detection harder (https://arxiv.org/html/2608.14391; the number is from the paper body).
  - VideoASMR-Bench: asked neutrally, VLMs show "a strong bias toward classifying videos as real". Gemini-3-Pro fails to reliably detect AI ASMR clips (https://arxiv.org/abs/2512.13281).
  - LOKI video judgment: GPT-4o 71.3%, humans 83.5% (https://arxiv.org/html/2410.09732v2).
  - Physics-IQ: Gemini 1.5 Pro told Sora clips from real ones at 55.6%, close to chance (https://arxiv.org/html/2501.09038).
  - VidAudit: a detector's AUC fell from 0.998 to 0.529 under audited evaluation, because it was learning format shortcuts (https://arxiv.org/abs/2606.31004).
  - Anthropic: Claude "cannot determine whether an image is AI-generated" (https://platform.claude.com/docs/en/build-with-claude/vision).
- **Benign causes on real footage**
  - Rolling-shutter "Jello effect" (https://www.adobe.com/creativecloud/video/discover/rolling-shutter-effect.html).
  - Re-encoding and platform compression (RA-Bench).
  - Also, as domain knowledge (**unverified**): stabilisation warping, motion blur, lens distortion, beauty filters, frame interpolation ghosting, low-light denoiser smearing, macroblocking in dark gradients.
- **Provenance**
  - `c2patool video.mp4` prints the C2PA manifest; `-d` gives a detailed report, and `trust --trust_anchors` checks trust (https://raw.githubusercontent.com/contentauth/c2patool/main/docs/usage.md). MP4, MOV and AVI are supported.
  - A missing manifest proves nothing.
  - SynthID: the Gemini app checks uploads up to 100 MB and 90 s (https://blog.google/technology/ai/verify-google-ai-videos-gemini-app/), and "can currently only recognize content created by Google AI tools" (https://support.google.com/gemini/answer/16722517). No public CLI or API for SynthID in video was found.

**Measure**
- `c2patool` and ffprobe tags.
- YDIF and `scdet` spikes with no cut: candidate glitch frames.
- `freezedetect`.
- Difference images between adjacent frames, which show morphing or boiling as structured changes on static background:
  ```bash
  ffmpeg -i a.png -i b.png -filter_complex "blend=all_mode=difference" diff.png
  ```
  `blend` and `tblend` modes are documented at https://ffmpeg.org/ffmpeg-all.html#blend.

**Sample:** native-fps pairs and triplets at every spike, plus crops of hands, faces, text, and edges of moving objects.

**Prompt pattern:** one query per artifact family; never "is this AI?".
```
Frames F21-F26 (00:05.20-00:05.40, native fps) and crops are consecutive. Family: <anatomy/hands | identity/texture drift | text changing | object appears/disappears | physics | background geometry warp | temporal flicker>.
Describe the <region> in each frame. Report a change only if you can point to it (frames + region). For each change, check these ordinary camera causes: compression blocking, motion blur, rolling-shutter wobble, stabilisation warp, lens distortion, beauty filter, frame interpolation, low-light noise, VFX. If one fits, label it "explained". Otherwise label it "unexplained". "No change" is a valid answer.
```

**Verdict scale**
- `provenance-confirmed`: C2PA or SynthID says AI.
- `likely-generated`: two or more unexplained families, confirmed by verification.
- `unclear`.
- `no generation artifacts observed`: this is not proof of authenticity.
- A bare "AI" verdict from visuals alone is never issued.

### 5.4 Motion-graphics QA

**Evidence and thresholds**
- Text timing: minimum 5/6 s on screen; 20 characters per second for adults, 17 for children; at most 2 lines (Netflix, 3.7).
- Safe areas (EBU R 95): action 3.5%, graphics 5%.
- Contrast 4.5:1, or 3:1 for large text (WCAG 1.4.3).
- Flashing: WCAG 2.3.1 and BT.1702 (3.2).
- Render-error detectors: `freezedetect`, `blackdetect`, `idet` (field order), `mpdecimate` (held or dropped frames), `scdet`, and `blurdetect` or `blockdetect` for banding and softness proxies (section 3).
- Missing sources: Adobe's pages on alpha fringes, gamma shift and field order returned 403, and no source was found for a minimum text size as a fraction of frame height. Both are **unverified**.

**Measure**
- Run OCR at 10 fps over the whole video. For each text element record its first and last frame, bounding box and character count.
- From that compute: on-screen duration against characters per second; bounding box inside the graphics-safe area or platform safe zone; sampled contrast ratio.
- Collect held-frame runs and flash counts.

**Easing and collision method** (ours; no standard exists)
- Extract every native frame across each transition.
- Track each element's box per frame, from OCR boxes or a model-returned box.
- Compute per-frame displacement. A velocity jump between adjacent frames means a keyframe or easing problem. Overlapping boxes mean a collision.

**Prompt pattern**
```
Frames are consecutive at native fps (labels carry frame numbers). Measured: text elements with first/last frame, cps, safe-area status; held-frame runs; flash windows.
For each flagged window report: frame range, issue class (timing, easing/velocity jump, overlap, clipped or off-safe text, legibility, typo vs script <script text>, glyph/font substitution, banding, alpha halo, colour shift vs reference still, combing, held/dropped frame), severity (blocker/issue/FYI), evidence frames, suggested fix. Describe each element's motion as linear / ease-in / ease-out / overshoot from the frame-to-frame displacement you can see.
```

### 5.5 Tutorial step extraction

**Evidence**
- HowTo100M narration is only loosely aligned with the visuals (https://arxiv.org/abs/1906.03327). HTM-Align annotates that alignment (https://arxiv.org/abs/2204.02968).
- MPTVA (ECCV 2024) has an LLM filter "task-irrelevant information" and summarize steps, then aligns them via narration timestamps and similarity. It gained +5.9% in step grounding (https://arxiv.org/abs/2409.16145).
- VidChapters-7M is precedent for "segment plus title" output (https://arxiv.org/abs/2309.13952).
- VideoTree's coarse-to-fine tree works well on long videos (https://arxiv.org/abs/2405.19209).

**Measure**
- ASR with word timestamps (5.6).
- Scene or slide changes: `detect-adaptive`, plus `mpdecimate` for screencasts.
- OCR on every keyframe, covering code, terminal and menu text.

**Sample**
- 1 to 3 keyframes per scene, plus a 0.2 fps floor.
- Model-selected segments at 2 to 4 fps.

**Prompt pattern**
```
Inputs: transcript [{start,end,text}], scenes [{id,start,end,frame}], OCR per frame, keyframes.
1. Drop narration unrelated to the task (intro, sponsor, banter).
2. Numbered steps: imperative title; start/end MM:SS snapped to the nearest scene change within 2 s; screenshot frame id; exact on-screen text or code copied from OCR; spoken tip (quote); "you should now see ...".
3. Tag each step seen+heard | seen-only | heard-only; flag narration vs screen disagreements.
```

### 5.6 Transcript-visual alignment

**Tools**
- **WhisperX** gives word timestamps by forced alignment with wav2vec2. It exists because Whisper over sliding windows is prone to "drifting, hallucination & repetition". Limits: numbers such as "£13.60" can't be aligned, and overlapping speech is weak (https://arxiv.org/abs/2303.00747, https://github.com/m-bain/whisperX).
- **whisper.cpp** (https://raw.githubusercontent.com/ggml-org/whisper.cpp/master/README.md)
  - `whisper-cli -ml 1` for word-level timestamps; `-osrt`, `-ovtt` and `-oj`/`-ojf` for output formats.
  - Input must be 16 kHz mono WAV: `ffmpeg -i in.mp4 -ar 16000 -ac 1 -c:a pcm_s16le out.wav`.
- **faster-whisper** with `word_timestamps=True` (https://github.com/SYSTRAN/faster-whisper).
- **FFmpeg `whisper` filter**
  - Shipped in FFmpeg 8.0 on 2025-08-22 (https://ffmpeg.org/index.html#news). Needs `--enable-whisper` plus whisper.cpp.
  - Options: `model` (required), `language` (default auto), `queue` (3 s), `destination`, `format` (text, srt or json), `vad_model`, `max_len`, `translate`.
  - Example:
    ```bash
    ffmpeg -i input.mp4 -vn -af "whisper=model=../whisper.cpp/models/ggml-base.en.bin:language=en:queue=3:destination=output.srt:format=srt" -f null -
    ```
    (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Audio/whisper.html)
  - Homebrew core ffmpeg does not list whisper-cpp, so the filter is probably not present there (inference).

**Sync tolerances**
- Gemini's own audio timestamps are per second (1), so it cannot judge sub-second sync.
- EBU R37: sound may lead picture by at most 40 ms and lag by at most 60 ms, end to end (https://tech.ebu.ch/docs/r/r037.pdf).
- SyncNet reports the audio-video offset in frames, with a confidence value (https://github.com/joonson/syncnet_python).

**Alignment rule**
- Snap segment edges to cuts, following Netflix practice: in-time on the first frame of the shot, out-time 2 frames before a cut (3.7).

**Prompt pattern**
```
For each segment [id, MM:SS.ss-MM:SS.ss, text] you get the frames inside it: match | partial | mismatch between speech and visuals (quote both). For a visible speaker: lips moving during speech, speech with mouth closed. Do not estimate milliseconds; the measured SyncNet offset is given.
```

### 5.7 Comparing two versions of a video

**Exact identity**
```bash
ffmpeg -v error -i A.mp4 -map 0:v -f framemd5 A.md5
ffmpeg -v error -i B.mp4 -map 0:v -f framemd5 B.md5
# compare hash columns
```
Documented usage: `ffmpeg -i INPUT -f framemd5 out.md5` (https://ffmpeg.org/ffmpeg-all.html#framemd5).

**Matching segments across edits** (MPEG-7 signature)
```bash
ffmpeg -i A.mp4 -i B.mp4 -filter_complex "[0:v][1:v]signature=nb_inputs=2:detectmode=full:format=xml:filename=sig%d.xml" -map :v -f null -
```
(https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/signature.html)

**Quality metrics on aligned ranges**
```bash
ffmpeg -i B.mp4 -i A.mp4 -lavfi "[0:v]settb=AVTB,setpts=PTS-STARTPTS[b];[1:v]settb=AVTB,setpts=PTS-STARTPTS[a];[b][a]ssim=stats_file=ssim.log" -f null -
ffmpeg -i B.mp4 -i A.mp4 -lavfi "[0:v]setpts=PTS-STARTPTS[d];[1:v]setpts=PTS-STARTPTS[r];[d][r]libvmaf=log_path=vmaf.json:log_fmt=json" -f null -
```
- SSIM needs identical size and pixel format. The docs' own combined example is `ffmpeg -i main.mpg -i ref.mpg -lavfi "ssim;[0:v][1:v]psnr" -f null -` (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/ssim.html).
- For `libvmaf`, "The first input is the distorted video, and the second input is the reference video" (https://ayosec.github.io/ffmpeg-filters-docs/9.0/Filters/Video/libvmaf.html). Homebrew core ffmpeg includes libvmaf.

**Reading the numbers**
- VMAF (https://raw.githubusercontent.com/Netflix/vmaf/master/resource/doc/faq.md):
  - the default model assumes 1080p viewed from 3 screen heights;
  - don't compare absolute scores across resolutions;
  - mean pooling hides the worst frames.
- A difference of about 6 VMAF points is a common "just noticeable difference" convention (https://arxiv.org/abs/2401.15343).
- SSIM in dB is 10·log10(1/(1-SSIM)). Universal SSIM thresholds are **unverified**.

**Aligning versions of different lengths**
- Audio first: `audio-offset-finder`. Trust a score above 10 (https://github.com/bbc/audio-offset-finder).
- Then DTW over per-frame pHash at 2 to 5 fps (https://github.com/JohannesBuchner/imagehash, https://dtaidistance.readthedocs.io/en/latest/usage/dtw.html). This finds inserted, deleted and retimed ranges.

**LLM pass**
- VidDiff found GPT-4o weak at "fine-grained frame comparison". Its fix is three stages: propose, localize, compare (https://arxiv.org/abs/2503.07860).
- Build matched pairs: `ffmpeg -i a_t.png -i b_t.png -filter_complex hstack pair.png`, labelled `A 01:23.40 | B 01:25.10`, plus the difference image.
- Only report a quality change as visible if the VMAF drop is 6 or more, or you can point to it in a pair.

---

## 6. Proposed pipeline and frame packet

1. **Probe** (3.1): duration, fps, VFR, rotation, SAR, HDR, audio presence.
2. **Measure** (3.2 and 3.3): cuts, black, freeze, silence, loudness, true peak, clipping, crop, interlace, duplicates, flashes. Output a `facts.json`.
3. **Plan frames** (2.4): uniform floor, plus shot frames, plus motion-CDF frames, plus event bursts. Deduplicate near-identical frames. Cap by token budget.
4. **Extract** full-resolution stills with accurate seeks; PNG for text.
5. **Build** label bands (overview copies only), one contact sheet, and native-resolution crops (OCR boxes, regions of interest).
6. **OCR** every still and crop. Text below the confidence threshold is marked "unreadable".
7. **Pass A**, neutral inventory: per frame, what is visible and what text is visible, with legibility.
8. **Pass B**, the task (a playbook from section 5): gets facts, OCR, inventory and frames. Every claim carries evidence and a confidence level.
9. **Pass C**, factored verification: for each defect, text or count claim, dense frames and crops go to a fresh Gemini call and to Claude, with a neutral question. Motion and order claims also get the reversal or shuffle probe. Claims that fail are dropped or downgraded.
10. **Report**: claims tagged `measured | ocr | visual | audio | inferred`, each with `verified | unverified | failed`, frame IDs and timestamps.

**Frame packet layout** (text before each image, task at the end):
```
[text] VIDEO: 1080x1920, 29.97 fps, 00:30.03. Stills below are full-resolution frames extracted with ffmpeg; each is preceded by its label.
[text] Frame 01/24 | t=00:00.00 | shot 1 start
[image] f01.png
[text] Frame 02/24 | t=00:00.50
[image] f02.png
...
[text] Crop C1 of Frame 07 | x 1280-1920, y 0-360 (top-right) | 2x upscale
[image] f07_c1.png
[text] MEASURED FACTS (authoritative): cuts 00:03.20, 00:07.85, ...; black 00:29.60-00:30.03; integrated -18.2 LUFS; true peak -0.4 dBTP; ...
[text] OCR (Apple Vision, conf >= 0.5): F07 "SALE 50% OFF" (0.98); F12 [unreadable] ...
[text] TASK: ...  RULES: (section 4.4 contract, short form)
```

**Claim schema**
```json
{"id":"C3","t_start":"00:05.20","t_end":"00:05.40","frames":["F21","F22"],"region":"top-left",
 "claim":"logo edge shape changes between F21 and F22","evidence_type":"visual",
 "confidence":"medium","alt_explanations_checked":["compression","motion blur"],
 "verification":"passed|failed|not_run"}
```

---

## 7. Open or unverified items

**Platform specs**
- TikTok safe-zone pixel values; the TikTok 10-minute in-app and 60-minute web limits.
- A YouTube Shorts text safe area.
- Meta's own wording for "hook in first 3 s" and "bottom 40% with disclaimers".
- All X specs.

**Loudness**
- YouTube -14 LUFS and Apple Sound Check -16 LUFS: third-party figures only.
- No published Instagram or TikTok loudness target.
- Netflix values could only be partly confirmed; the page is now behind a sign-in.

**Captions and legibility**
- BBC words-per-minute figures.
- Minimum text height as a fraction of frame height.
- Universal thresholds for SSIM and pHash.

**Tools and Gemini specifics**
- Whether the Antigravity CLI exposes fps, `media_resolution`, per-item resolution or agentic mode, and which model it uses.
- Apple Vision support for Bengali on macOS 26.
- Whether `photosensitivity=bypass=1` still logs badness.
- The exact `ebur128` summary text and the `ffprobe -v trace` atom line format. Check both on the installed 9.0.2 build.

**Conflicts to handle in code**
- Facebook Stories safe zone: the pixel values and percentages disagree; use the percentages.
- Instagram Feed: the ads guide lists 9:16 only, while Facebook Feed recommends 4:5.
- Shorts ad length: "up to 3 min" on one Google page, "6-60 s" on another.
- Netflix minimum subtitle duration: "5/6 s" in one guide, "20 frames" in another.
- Gemini prompt-order advice differs between Google's pages (section 1).

---

## 8. Source index

**Gemini and Google**
- https://ai.google.dev/gemini-api/docs/video-understanding
- https://ai.google.dev/gemini-api/docs/video-understanding.md.txt
- https://ai.google.dev/gemini-api/docs/media-resolution
- https://ai.google.dev/gemini-api/docs/gemini-3
- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/tokens
- https://ai.google.dev/gemini-api/docs/image-understanding
- https://ai.google.dev/gemini-api/docs/files
- https://ai.google.dev/gemini-api/docs/pricing
- https://blog.google/technology/developers/gemini-3-pro-vision/
- https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/
- https://developers.googleblog.com/en/gemini-2-5-video-understanding/

**Anthropic**
- https://platform.claude.com/docs/en/build-with-claude/vision

**FFmpeg**
- https://ffmpeg.org/ffmpeg-filters.html
- https://ffmpeg.org/ffmpeg-all.html
- https://ffmpeg.org/ffprobe.html
- https://ayosec.github.io/ffmpeg-filters-docs/9.0/ (per-filter mirror of the 9.0 docs)
- Source files in https://github.com/FFmpeg/FFmpeg/tree/master/libavfilter: `f_select.c`, `vf_blackdetect.c`, `vf_freezedetect.c`, `af_silencedetect.c`, `vf_blurdetect.c`, `vf_blockdetect.c`, `vf_idet.c`, `vf_vfrdet.c`, `vf_mpdecimate.c`, `vf_photosensitivity.c`, `f_ebur128.c`
- https://github.com/FFmpeg/FFmpeg/blob/master/fftools/ffprobe.c
- https://formulae.brew.sh/formula/ffmpeg
- https://github.com/homebrew-ffmpeg/homebrew-ffmpeg

**Imaging tools**
- https://pillow.readthedocs.io/en/stable/reference/ImageFont.html
- https://imagemagick.org/montage/

**PySceneDetect**
- https://www.scenedetect.com/docs/latest/cli.html
- https://www.scenedetect.com/docs/latest/api/detectors.html
- https://www.scenedetect.com/changelog/
- https://github.com/Breakthrough/PySceneDetect/blob/main/benchmark/README.md

**Frame selection and sampling**
- AKS 2502.21271; BOLT 2503.21483; Frame-Voyager 2410.03226; Q-Frame 2506.22139
- VideoAgent 2403.10517; VideoTree 2405.19209; TCoT 2507.02001; MaxInfo 2502.03183
- Frame Sampling Strategies Matter 2509.14769; DistractionBench 2605.27101
- IG-VLM 2403.18406; TS-LLaVA 2411.11066
- NumPro 2411.10332; TimeLens 2512.14698; TimeMarker 2411.18211

**Long video, needles and motion**
- VideoNIAH 2406.09367; LongVA 2406.16852; Gemini 1.5 report 2403.05530
- LongVideoBench 2407.15754; MLVU 2406.04264; VideoZeroBench 2604.01569
- Moment-Video 2606.02522; F-16 2503.13956; MotionBench 2501.02955
- FAVOR-Bench 2503.14935; TOMATO 2410.23266
- MGSampler 2104.09952; Video-RTS 2507.06485

**Crops and zoom**
- ViCrop 2502.17422; DeepEyes 2505.14362; LENS 2607.25125

(All arXiv IDs resolve at https://arxiv.org/abs/<id>.)

**Hallucination**
- VideoHallucer 2406.16338; HAVEN 2503.19622; VideoHallu 2505.01481
- MAD-Bench 2402.13220; ViSE 2506.07180; Caved or Convinced 2608.03160; Looking Again 2608.28623
- VBenchComp 2505.14321; POPE 2305.10355; VirtueBench 2603.07071; VideoASMR-Bench 2512.13281
- VidText 2505.22810; MME-VideoOCR 2505.21333; EC-Bench 2603.29943; TOC-Bench 2605.09904
- CameraBench 2504.15376; MoHallBench 2607.01117; Video-VER 2510.06077; Video-MME-v2 2604.05015

**Verification methods**
- CoVe 2309.11495; self-consistency 2203.11171
- Calibration: 2305.14975, 2306.13063, 2405.02917
- Debate and cross-examination: 2305.14325, 2311.17371, 2305.13281
- LLoVi 2312.17235
- MHBench: https://ojs.aaai.org/index.php/AAAI/article/view/32463

**Benchmark results**
- GDM evaluation PDFs: https://storage.googleapis.com/deepmind-media/gemini/ (3 Pro, 3 Flash, 3.7 Flash, 3.8 Flash)
- https://seed.bytedance.com/en/seed2
- InternVL3.5 2508.18265

**Platforms**
- Meta: https://www.facebook.com/business/ads-guide/update/video (and the instagram-reels, instagram-story, instagram-feed, facebook-facebook-reels and facebook-story pages); https://www.facebook.com/help/instagram/1038071743007909/; https://www.facebook.com/help/1041366099316573
- TikTok: https://developers.tiktok.com/doc/content-posting-api-media-transfer-guide; https://ads.tiktok.com/help/article/tiktok-auction-in-feed-ads?lang=en; https://ads.tiktok.com/help/article/creative-best-practices?lang=en
- YouTube and Google Ads: https://support.google.com/youtube/answer/1722171; https://support.google.com/youtube/answer/15424877; https://support.google.com/google-ads/answer/16041697
- LinkedIn: https://www.linkedin.com/help/lms/answer/a424737

**Standards**
- https://tech.ebu.ch/docs/r/r128.pdf; r128s1.pdf; r128s2.pdf; tech3341.pdf; tech3342.pdf; r095.pdf; r037.pdf
- ATSC A/85 Annex M; AES TD1008
- ITU-R BT.1702-3
- https://www.w3.org/TR/WCAG22/
- Netflix Timed Text Style Guide pages (URLs in 3.7)

**Playbook sources**
- Screen recordings: V2S 2005.09057; CAPdroid 2302.00886; ViBR 2604.19905; GUI-World 2406.10819; VideoWebArena 2410.19100; 2508.04895
- Ads: ABCD pages and https://github.com/google-marketing-solutions/abcds-detector
- AI artifacts: BrokenVideos 2506.20103; Spotlight 2511.18102; VBench-2.0 2503.21755; RA-Bench 2608.14391; LOKI 2410.09732; Physics-IQ 2501.09038; VidAudit 2606.31004; c2patool usage doc; SynthID pages
- Tutorials: HowTo100M 1906.03327; MPTVA 2409.16145; VidChapters 2309.13952
- Transcription and sync: WhisperX 2303.00747; whisper.cpp; faster-whisper; SyncNet
- Version comparison: VMAF FAQ; audio-offset-finder; ImageHash; dtaidistance; VidDiff 2503.07860
- OCR: Tesseract tessdoc pages; Apple Vision doc JSON pages; ocrit; macOCR; ocrmac; EasyOCR
