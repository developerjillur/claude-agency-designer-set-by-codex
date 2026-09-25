# Kinetic type craft: decisions and numbers

Numbers are at 30 fps and px at 1080 (the kit scales them). They are starting points that read as professional; tune
to the brand and always check stills at full size.

## 1. Which part for which job

| The text is | Use | Default motion |
|---|---|---|
| a headline, a thesis, a scene title | `KineticTitle` | mask rise by word, 3 frames apart, 16 to 18 frames each |
| a two-line punch ("Faster reviews. / Fewer meetings.") | `KineticTitle by="line"` | mask by line, 6 frames apart |
| a supporting line under a title | `SplitText in="rise"` role body | 2 to 3 frames apart, starts as the title settles |
| a wordmark or a single short word | `SplitText` (auto: by character) | pop, 2 frames apart |
| a list or narration beat by beat | `LineStack`, or `Stagger` of `SplitText` | a line per cue, spent lines to 30 % |
| code, a prompt, a search box, a terminal | `Typewriter` (mono, block caret) + `KeySounds` | 25 to 30 characters a second, output lines `instant` |
| a spoken sentence typed as a title | `Typewriter role="display"` | 12 to 20 characters a second |
| a reveal of a secret or a code | `Scramble` | 10 frames of flicker, 24 frames of locking |
| "for X, Y and Z" | `WordRotator` | hold 30 to 40, change 12 to 16 frames |
| one number that matters | `Counter` or `BigStatement` | 45 frames, strong ease-out, a settle |
| a quotation | `Quote` | word by word, attribution after |
| a small label, category or step | `Kicker` / `Label` | bar draws, text rises, 12 to 14 frames |
| speech | `TikTokCaptions` / `BoxedCaptions` | see captions.md |
| a sentence whose size must fit a box | `FitText` | reveal lines by mask |

## 2. Reveal rules

- **By word by default.** "AI Film Director" by letter at a 2-frame stagger needs 30 frames before the last glyph
  moves; by word (3 words, 3-frame stagger, 15-frame rise) it lands at frame 24 and leaves a second of stillness.
- **Masks, never fades, for titles**: each word or line in its own clipping box, rising from below the box. Opacity on
  top of a mask defeats it. The box needs padding for accents and descenders (0.14 em top, 0.22 em bottom for Latin;
  0.34 and 0.3 for Bangla) and the travel must cover the box plus both paddings, or tall letters peek through at the
  start and end (the kit's `MaskUnit`).
- **Order**: reading order. `center` for a symmetric title, `random` only for sparkle-like noise, never for sentences.
- **Stagger budget**: siblings of one gesture 2 to 4 frames; a list 5 to 6; the whole run under about 0.8 s, and done
  before the next cue word.
- **Exits**: faster than entrances (12 to 18 frames), ease-in, all or in a quick reverse stagger (`outEach` 2 to 3);
  the exit ends on the last frame of the Sequence. Text that is still readable at a hard cut is fine; half-visible is
  not.
- **Frame 0 is the poster** for the first scene: when the video autoplays in a feed, start the title already set. The
  kit's reveals accept a negative `delay` (for example `delay={-40}`: every word has landed by frame 0), or place the
  title in a Sequence with a negative `from`.

## 3. Setting headlines

- Size: 100 to 150 px for 16:9 headlines, 90 to 120 in 9:16; key words may be huge (200 to 320 px) and a single giant
  word plus one small note is a complete composition. `BigStatement` fits the word up to 58 % of the safe height.
- Lines: balanced (no orphan), 2 to 3 lines, measured; a manual `\n` where the meaning breaks beats any algorithm.
- Tracking: tight on big type (about -0.035 em at 100 px and up, never tighter than -0.05); caps labels open
  (+0.06 to +0.12 em); body 0.
- Weight: 700 to 900 for kinetic sans, 400 to 500 for premium serif; never under 300 in motion.
- Emphasis: one word, and it must win on at least two of colour, weight, size, a mark. `punch` = accent plus a scale
  from 1.12 to 1 with a small overshoot, pivoting on the baseline (origin x at the word's left for the first word of a
  left-aligned line). `marker`/`block` = a bar that sweeps in once the word has landed.
- Two families at most (display plus body); the theme decides them.

## 4. Typing

- Speed: headlines 12 to 20 cps, interfaces 25 to 30; floor about 0.5 frame a character (above 60 cps at 30 fps
  characters land in batches).
- Rhythm: seeded jitter about 35 % of each interval; pauses after commas 5 frames, sentences 12, line ends 14, spaces
  0 to 2. Budget: `delay + chars / cps * fps + pauses <= shot length`, with a hold after the last key.
- Caret: a bar 0.075 em wide over the line's cap height and descender; solid while typing, blinking (16 frames on,
  16 off) when idle; visible from about 12 frames before the first key, never alone long before. Block caret for
  terminals, underscore for retro.
- Layout: the untyped rest is laid out but hidden, so centred text never drifts and a word never jumps to the next
  line when it grows. Do not fade characters one by one (the caret position breaks).
- Sound: one click per visible key, alternating samples, levels varied by 25 %, keys closer than 2 frames thinned out,
  at 0.25 to 0.35 under the voice.

## 5. Scrambles and rotators

- Scramble: random glyphs change on twos (every 2 frames reads as flicker, every frame as noise); glyph pool from the
  script (Bangla letters for Bangla, digits for numbers, capitals for capitals); unlocked glyphs in the accent at 90 %;
  lock left to right over 20 to 30 frames after 8 to 12 frames of pure flicker. Mono fonts look most "decoded".
- Rotator: hold each word 30 to 40 frames, change in 12 to 16 with an in-out curve (outgoing up, incoming from below,
  moving together); the slot width follows the measured word so a centred line glides; stop on the answer word unless
  it is a loop; give the whole line an entrance.

## 6. Numbers

- Count over 30 to 60 frames with a strong ease-out (`outQuart`), tabular digits (fixed-width slots when the font or
  script lacks them), the final value's width reserved (digits never move), a 4 to 5 % settle on landing pivoting on
  the baseline.
- Formats: currency, percent (write 42 for 42 %), compact (1.2M, `১২.৪ লাখ` in Bangla), decimals fixed. A small
  `%` or unit hangs from the cap height at half size.
- Odometer (`mode="roll"`): the lowest place turns continuously, higher places carry only during the last unit of the
  place below; leading places fade in when reached.
- Start the count on the word that names the number; land before the next clause. Intermediate values must be
  plausible facts, or do not count (fade the number in instead).

## 7. Statements, quotes, line stacks

- Big statement: the word per character from masks (up to 8 graphemes) with a heavy settle (1.05 to 1); a 72 px
  accent rule draws, then a small note (30 to 52 px, muted) rises; note to the right aligned to the word's bottom, or
  below aligned to its left edge.
- Quote: a hanging accent quote mark about 3.4 times the text size; the text 60 to 80 px serif, word by word 2 frames
  apart; the attribution (author strong, role muted, a 44 px rule before it, never a dash) 4 frames after the last word.
- Line stack: each line rises 28 px over 9 frames on its cue; spent lines step back to 30 % over the next arrival; the
  stack lifts 10 px per arrival.

## 8. Reading time and holds

`readingFrames(text, fps)`: about 0.33 s a word plus 0.3 s, never under 1.2 s, more for numbers. Hold settled text at
least that long and at least 30 to 45 frames before an exit; 1.5 s for multi-word lines. The first cut is almost
always too fast: every documented revision asked for longer holds.

## 9. Anti-patterns

- Per-letter staggers on sentences; fades on titles; slow sub-pixel drifts of text being read.
- Animating `fontSize`; `will-change` on text in renders; a 1-frame caret flash at frame 0.
- Two emphasised words in one headline; gradient text; glow on every word; emoji as icons in text.
- Letter spacing or uppercase on Bangla; splitting Bangla by code point.
- A caption page with one orphan word; subtitles that paraphrase the voice; on-screen headlines that repeat the
  voice-over word for word.
- Counting through invented intermediate values; digits that jiggle while counting.
