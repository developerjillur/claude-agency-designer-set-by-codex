# Captions and subtitles (Remotion 4.0.528)

Captions are data in milliseconds; drawing is in frames. Transcribe once, offline, to word timings; convert them to
`Caption[]`; group them into pages (burned-in short-form captions) or cues (subtitles); draw the page or cue whose
time range contains the current time; mark the spoken word.

## 1. The data type

`Caption` (`@remotion/captions`, 4.0.216): `{text, startMs, endMs, timestampMs: number | null, confidence: number |
null, pageBreakAfter?: boolean}`.
- `text` is whitespace sensitive: a space **before** each word (`"Most"`, `" teams"`, `" lose"`). Tokens without a
  leading space are glued to the previous word (sub-word pieces, punctuation).
- `timestampMs` is whisper.cpp's DTW time (null or a midpoint elsewhere); `confidence` 0 to 1 or null.
- `pageBreakAfter` (4.0.517) ends a page or an SRT cue after this caption without changing any time.

## 2. Getting word timings

| Source | Runs | Converter | Notes |
|---|---|---|---|
| whisper.cpp (`@remotion/install-whisper-cpp`) | Node or Bun, local | `toCaptions({whisperCppOutput})` | most accurate word times with `tokenLevelTimestamps: true` (DTW, whisper.cpp 1.5.5+) and `splitOnWord: true`; input a 16 kHz 16-bit WAV (`npx remotion ffmpeg -i in.mp4 -ar 16000 -ac 1 out.wav`); models `tiny` to `large-v3-turbo` (1.7.2+) |
| whisper-webgpu (`@remotion/whisper-webgpu`, 4.0.518+) | browser or Node with a GPU | `toCaptions({whisperWebGpuOutput})` | `language` required for multilingual models; word times arrive at the end |
| whisper-web (WASM) | browser, cross-origin isolated | `toCaptions({whisperWebOutput})` | slow, experimental, one job at a time |
| OpenAI | cloud | `openAiWhisperApiToCaptions({transcription})` | `response_format: 'verbose_json'` and `timestamp_granularities: ['word']` |
| ElevenLabs | cloud | `elevenLabsTranscriptToCaptions({transcript})` | `timestamps_granularity: 'word'`; only `type: 'word'` items are words |
| Any JSON of words | anywhere | the kit's `toCaptions(json)` | see section 3 |

For Bangla or any non-English speech use a multilingual model of at least `medium` (or `large-v3-turbo`) with
`language: 'bn'`; never a `.en` model. Keep the raw transcript; fix brand names in the caption text, never in the
times. Drop fillers: `[BLANK_AUDIO]`, `[PAUSE]`, `[Silence]`, `[INAUDIBLE]`, `TT_<n>` and blank tokens.

## 3. The kit's converters (`captionData.ts`, pure)

- `toCaptions(input, {unit, offsetMs})` accepts an array of words, `{words}` or `{segments: [{words}]}`; keys `text`,
  `word` or `punctuated_word`; times `start`/`end` (seconds or ms) or `startMs`/`endMs`. `unit: 'auto'` reads seconds
  unless every time is a whole number and some exceed 30. If the input already marks word starts with spaces
  (token-level whisper), spacing is kept; otherwise every word gets a leading space except the first and pure
  punctuation. ElevenLabs `spacing` and `audio_event` items and fillers are dropped; the result is sorted.
- `remapCaptions(captions, cuts)` maps source times into an edit. `CaptionCut = {inMs, outMs, atMs?, rate?}`: a kept
  source range placed at `atMs` (default: right after the previous cut) and sped by `rate`. A word is kept when its
  middle falls inside a cut; its start and end are clipped to the cut: `out = at + (clamp(t, in, out) - in) / rate`.
  `cutsFromFrames(cuts, fps)` takes frame cuts. `shiftCaptions(captions, ms)` moves everything.
- `captionTimeAt(frame, fps, {trimBefore, playbackRate, offsetMs})` is the time to use when the captions sit over one
  trimmed or sped clip in the same Sequence: `((trimBefore + frame * playbackRate) / fps) * 1000 + offsetMs`.

## 4. Pages for short-form captions

`createTikTokStyleCaptions({captions, combineTokensWithinMilliseconds, breakOnSilenceAfterMilliseconds?})` returns
`{pages}`; a page is `{text, startMs, durationMs, tokens: [{text, fromMs, toMs, pageBreakAfter?}]}` with absolute
token times. The algorithm (source-verified): a new page can start only at a caption whose text begins with a space,
and only when the current page already spans more than `combineTokensWithinMilliseconds`, or the gap before this
caption is at least `breakOnSilenceAfterMilliseconds` (4.0.514; `0` makes one page per word). A page lasts until the
next page starts (text stays up through a pause); the last one ends at its last token. The first token of a page is
trimmed; the others keep their leading space. Without leading spaces everything becomes one page.

The kit's `captionPages(captions, {pageMs 1200, silenceMs 600, maxHoldMs 900, maxWords 8})` adds three craft rules:
pages never cross a sentence end (it sets `pageBreakAfter` on sentence ends), a one-word page joins its neighbour when
there is no real pause (no "it." orphan), and a page leaves at most `maxHoldMs` after its last word. It returns whole
words (`{text, fromMs, toMs}`), glued and split correctly. `captionPageAt(pages, ms)` finds the page on screen.

Time-based pages split phrases wherever the clock says: "ফোনেই রাখুন, তিনটা | সহজ নিয়মে।" left a number dangling
from its noun. `sentenceMs` (also a `TikTokCaptions` prop) pages by phrase instead: a pause of `silenceMs` or a
sentence end always ends a page, a sentence spoken within `sentenceMs` (and at most `maxWords` words) stays whole,
a longer one splits after its commas (joining neighbouring phrases while they fit), and a phrase still too long
splits into even runs, never leaving one word alone. `sentenceMs={3000}` suits voice-overs of short sentences.
Whole sentences make two-line pages: give the captions an explicit `size` and a numeric `position` so both lines
fit their band (a 9:16 top band above a phone took `size={64} position={0.115}`). Inside a page, `TikTokCaptions`
never ends a line on a word that belongs with the next (`bindsToNext`: English small words, Bangla determiners,
quantifiers, genitives and numbers, so no "মোট / বিক্রি"); a spoken list number ("এক,") joins its sentence when
`silenceMs` is longer than the pause after it.

Page length guide: 200 to 800 ms for punchy word-by-word styles, about 1200 ms for 2 to 4 word pages, 2000 to 3000 ms
for subtitle-like lines.

## 5. Drawing pages

Two correct ways: one `<Sequence from={Math.round(page.startMs / 1000 * fps)} durationInFrames={...}>` per page
(shows in the Studio timeline; clamp each page's end to the next page's start, in frames), or compute the page from
the current time (what the kit does). Either way:
- `nowMs = page.startMs + frame / fps * 1000` inside a page Sequence, or `captionTimeAt(frame, fps, timing)`.
- A token is active when `fromMs <= nowMs < toMs`; to stop the mark blinking off in gaps, keep the last started word
  active until the next one starts.
- Render tokens in `white-space: pre` spans; keep leading spaces outside styled inline-blocks so spacing stays natural.
- Convert milliseconds to frames explicitly, `Math.round(ms / 1000 * fps)`. The official TikTok template adds
  milliseconds to a frame number (a bug): never copy that line.

## 6. Styles that ship (numbers)

| Style | How |
|---|---|
| Bold white | white, weight 700 to 800, size 70 to 90 px on 1080x1920 (about 60 on 16:9); outline `WebkitTextStroke: size/7 px black` with `paintOrder: 'stroke fill'`; a soft shadow; active word in a bright colour (yellow, green or the brand accent) |
| Gliding pill | a rounded rectangle (radius about 0.24 em, padding about 0.17 em by 0.06 em) behind the active word that glides: fractional index = sum over words after the first of an eased 0 to 1 step of about 5 frames centred on each word start; interpolate left, width and top between word boxes; pop the pill in (scale 0.6 to 1); the text on the pill is a second layer clipped to the pill so colours switch exactly at its edge |
| Word pop | each word appears on its start: scale 0.7 to 1 with a small overshoot over 4 frames, opacity with it |
| Scale | the active word grows about 10 % from its baseline centre with a 4-frame overshoot and shrinks as the next starts; add about 0.1 em of extra word spacing so it never touches neighbours |
| Karaoke | a second copy of each word in the active colour, clipped from the left by the word's progress `(now - from) / (to - from)`; spoken words fully filled |
| Plate | one rounded plate (`createRoundedTextBox`) behind the page lines; dark text on white or the brand colour; no outline |
| Boxed subtitles | each line in its own box (near-black at 75 to 80 %, padding 0.08 em by 0.42 em, radius 0.14 em), white text, body weight, 44 to 48 px at 1080; optional read-along (unspoken words at 50 %) |

Page entrance: a 5-frame pop (scale 0.9 to 1, 10 px rise, opacity). Page exit only when a pause follows (a 5-frame
fade); consecutive pages switch on a cut. Bangla: outline thinner (0.1 of the size), size about 10 % larger, line
height 1.4 and up, never uppercase.

## 7. Where captions go

- 9:16 (Shorts, Reels, TikTok): inside the safe area (kit `shorts`: x 65 to 940, y 270 to 1248 on 1080x1920), clear of
  the bottom 18 to 20 % and the right button rail; about 60 to 65 % of the frame height works. The kit puts the
  block's bottom at 95 % of the safe height and keeps lines 40 px short of the safe width so the pill and outline stay
  inside.
- 16:9: bottom of the safe area for subtitles (YouTube's own controls cover the lowest band); short-form styles can
  sit lower middle.
- Never cover the speaker's face; move captions to `top` or a fraction position for that shot.

## 8. Subtitles and SRT

- Rules (Netflix-style English): at most 42 characters a line (about 32 on 9:16), 2 lines, up to 20 characters a
  second for adults (17 for children), each cue between 5/6 s and 7 s, a new cue at sentence ends and pauses, line
  breaks balanced and after punctuation, never after "a", "the", "to", "of", "and". Captions match the speech exactly.
- `subtitleCues(captions, {maxChars, maxLines, maxMs, minMs, gapMs, cps})` builds such cues; each cue's end is
  extended for reading speed and minimum duration but never into the next cue (40 ms gap).
- `toSrt(captions | cues)` uses `serializeSrt({lines: Caption[][]})`: each inner array is a cue, texts joined with
  no added spaces (the kit passes one caption per cue with `\n` between lines), times floored to ms, cues separated by
  a blank line. `parseSrt({input})` reads SRT (BOM, CRLF, comma or dot milliseconds) into sentence-level captions
  without leading spaces.
- `CaptionsInternals.ensureMaxCharactersPerLine({captions, maxCharsPerLine})` (internal) splits captions into words and
  packs lines greedily; its orphan rule only acts at the very end of the transcript.
- Export with `<Artifact filename="subtitles.srt" content={srt} />` rendered on frame 0 (the kit's `<SubtitleFile>`);
  it lands in `out/<composition-id>/subtitles.srt`. Upload it next to the YouTube video; burn captions in for muted
  feeds (X, LinkedIn, Reels).

## 9. Errors and fixes

| Symptom | Cause | Fix |
|---|---|---|
| The whole transcript is one page | no leading spaces | `toCaptions()` (adds them) or prefix `" "` to each word |
| Spaces collapse between words | no `white-space: pre` | render tokens with it |
| Captions drift after an edit | source times | `remapCaptions()` with the edit's cuts, or `trimBefore`/`playbackRate` on the component |
| Pages flash or overlap | page end not limited by the next start, or ms added to frames | clamp in frames, convert with `Math.round(ms / 1000 * fps)` |
| A lone word gets its own page | time-based paging | the kit merges orphans; raw: merge pages of one word into the previous one |
| Wrong font or overflow in the first frame | measured before the font loaded | `useTypeFontsReady()` / `waitUntilDone()` before `fitText`/`measureText` |
| Garbage for Bangla speech | `.en` model or no language | multilingual `medium`+ with `language: 'bn'` |
| ElevenLabs captions empty | granularity not `word` | `timestamps_granularity: 'word'` |
| OpenAI captions without word times | wrong format | `verbose_json` plus `timestamp_granularities: ['word']` |
| whisper.cpp refuses the input | not 16 kHz 16-bit WAV | convert with the bundled ffmpeg |
