# type: kinetic text, numbers, highlights and captions

Everything that puts words on screen: words and lines that arrive, kinetic titles, typewriters, scrambles, word
rotators, counters, fitted text, marker sweeps and hand-drawn annotations, caption plates, big statements, quotes,
labels, and burned-in captions (TikTok pages and boxed subtitles) with the data helpers behind them.

Import from `./kit` (or `./kit/type`). Every component reads the theme (`useTheme()`), sizes in px at 1080 times
`unit`, and waits for the fonts before it measures anything. Bangla works everywhere: text is split by grapheme
cluster with conjuncts kept whole, and complex scripts get zero tracking, taller leading and deeper mask padding.

Demos: `nrk.py demos --module type` (DemoTypeWords, Title, Typewriter, Scramble, Counter, Fit, Highlight, Plate,
Statement, Quote, Captions, CaptionsPop, CaptionsWide, Bangla, BanglaKit).

## Shared ideas

- **Measured, never guessed.** Components that need line breaks or widths call `useTypeFontsReady()` (it holds the render
  with `delayRender` until the theme fonts have loaded), then measure with `@remotion/layout-utils` and render the
  measured lines explicitly with `white-space: pre`, so the browser never re-wraps them.
- **TypeProps** (on most components): `role` (`display` default for titles, `body` for captions and plates, `mono`,
  `serif`, `hand`, `bangla`), `size` (px at 1080), `weight`, `strong`, `caps` (default: the theme's caps for display),
  `tracking` (em; default `trackingFor()`), `lineHeight` (default `leadingFor()`), `fontFamily` (a stack loaded
  through core), `color`.
- **RevealTiming** (SplitText, KineticTitle): `in` / `out` (the motion module's reveals), `delay`, `each`,
  `duration`, `outDuration`, `outEach`, `order` (`forward`, `reverse`, `center`, `random`), `seed`, `distance`.
  Exits end on the last frame of the enclosing Sequence unless `outEach` spreads them.
- **Masks** use `MaskUnit`: padding sized for the script and a travel of the full box plus both paddings, so no
  ascender, descender or vowel sign peeks through the mask before the entrance or after the exit.

## SplitText

Text that arrives by word (default), by character (only for one short word), or by line.

| Prop | Default | Notes |
|---|---|---|
| `text` | required | `\n` gives lines |
| `by` | `'auto'` | `'word'`, `'char'`, `'line'`; auto = characters for one word of up to 6 graphemes, else words |
| `lines` | none | given lines |
| `maxWidth` | none | px at 1080: measure and wrap (needed for `by="line"` without lines; default the safe width then) |
| `maxLines` | none | with `maxWidth`: shrink until it fits |
| `align` | `'left'` | |
| `in` / `out` | theme entrance / `'none'` | any motion `Reveal` |
| `each` | 3 (word), 2 (char), 6 (line) at 30 fps | |
| `duration` | theme `enterFrames` (12 for chars) | |
| TypeProps | size 72, role display | |

```tsx
<SplitText text="Every frame is a pure function of time" size={84} in="rise" out="fade" outEach={2} />
<SplitText text="Launch" size={150} in="pop" />               {/* one short word: by character */}
<SplitText text={copy} by="line" in="mask" maxWidth={1100} role="body" size={52} />
```

Gotchas: per character only for wordmarks (letters in boxes lose kerning and take long to land); Bangla splits by
grapheme, never by code point. Without `maxWidth` or lines, word mode wraps naturally at spaces.

## KineticTitle

A headline rising out of masks word by word or line by line, balanced lines, tracking that tightens with size, and an
emphasised word.

| Prop | Default | Notes |
|---|---|---|
| `text` | required | `\n` forces a break |
| `by` | `'word'` | `'line'` |
| `size` | 124 (104 in 9:16) | shrinks to fit `maxLines` |
| `maxWidth` / `maxLines` | safe width / 3 | |
| `align` | `'left'` | |
| `emphasis` | none | word text (case and punctuation ignored) or index, or a list |
| `emphasisStyle` | `'punch'` | `'punch'` (accent colour, scale 1.12 to 1 with a settle from the baseline), `'color'`, `'marker'` (lower-half bar on light themes, a block on dark ones), `'block'` (full bar; the text is repainted in the ground colour exactly where the bar is) |
| `emphasisColor` | accent (bar: highlight) | |
| `in` / `out` | `'mask'` / `'none'` | |
| `each` / `duration` | 3 (6 by line) / max(14, theme enter) | |

```tsx
<Kicker text="Release 4.2" />
<KineticTitle text="Ship the update your users actually asked for" emphasis="actually" out="mask" />
<KineticTitle text={'Faster reviews.\nFewer meetings.'} by="line" align="center" emphasis="Fewer" emphasisStyle="color" />
```

Gotchas: one emphasised word per headline; the marker and block sweep in after the word lands and clear when it leaves.

## Typewriter, typewriterSchedule, KeySounds

Typing grapheme by grapheme with a caret. The rest of each line is laid out but hidden, so typed text never reflows
and centred text never drifts. `typewriterSchedule()` gives the landing frame of every character.

| Prop | Default | Notes |
|---|---|---|
| `text` / `lines` | required | `\n` for lines, typed line by line |
| `delay` | 0 | frames before the first key |
| `cps` | 18 | characters per second (10 slow human, 30 fast UI) |
| `jitter` | 0.35 | seeded variation of each interval |
| `pauses` | comma 5, sentence 12, line 14, word 0 | extra frames at 30 fps after punctuation and at line ends |
| `instant` | none | line indexes that appear whole (terminal output) |
| `caret` | `'bar'` | `'block'`, `'underscore'`, `'none'` |
| `caretColor` / `caretAfter` / `caretLead` | accent / `'blink'` / 12 | caret solid while typing, blinks when idle, shows 12 frames before typing |
| `maxWidth` | none | px at 1080: wrap into measured lines first |
| TypeProps | size 56, role mono | |

```tsx
const timing = {delay: 10, cps: 16, seed: 'hello'};
const sched = typewriterSchedule(lines, fps, timing); // sched.keys: frames of visible keystrokes
<Typewriter text={lines.join('\n')} role="display" size={88} align="center" {...timing} />
<KeySounds frames={sched.keys} volume={0.3} />
```

`KeySounds` plays one of three generated clicks (`kit/public/type/key-1..3.wav`, 65 ms, peak -3 dBFS) on each frame,
thinning keys closer than `minGap` (2) frames and varying sample and level by seed. A project made with `nrk.py new`
does not copy `kit/public`: copy `kit/public/type/` into the project's `public/type/`, or pass your own `src`.

## Scramble

A seeded decode: every glyph flickers through random characters (in `scrambleColor`, default accent), then locks in
order. The final text is laid out from the start, so nothing jitters.

Props: `text`, `delay` (0), `duration` (24 frames from first to last lock), `hold` (10 frames of pure flicker),
`order` (`'forward'`), `charset` (auto: Bangla letters for Bangla, digits for numbers, capitals for capitals, or
`latin`, `upper`, `digits`, `symbols`, `binary`, `hex`, `bangla`, or your own string), `rate` (2: changes on twos),
`seed`, `scrambleColor`, `align`, TypeProps (size 96).

```tsx
<Scramble text="ACCESS GRANTED" role="mono" size={112} delay={6} />
```

## WordRotator

One word of a line cycles through options with a mask slide (or `blur`, `flip`); the slot's width follows the
measured word so the rest of the line glides instead of jumping.

Props: `words`, `prefix`, `suffix`, `delay` (0), `hold` (34), `transition` (14), `loop` (false: stops on the last
word), `reveal` (`'mask'`), `width` (`'animate'` or `'max'` for a fixed slot), `wordColor` (accent), `align`,
TypeProps (size 96).

```tsx
<WordRotator prefix="Built for " words={['designers', 'developers', 'founders']} size={76} delay={40} align="center" />
```

Gotcha: it has no entrance of its own; wrap it in `<Animate>` when the line should arrive.

## Counter, formatCount

A number that counts (or rolls like an odometer) with Intl formatting, fixed-width digit slots (any font, Bangla
digits too), a small settle on landing and an entrance.

| Prop | Default | Notes |
|---|---|---|
| `to` / `from` | required / 0 | |
| `delay` / `duration` | 0 / 45 at 30 fps | |
| `ease` | `curves.outQuart` | fast, then settles |
| `format` | `'plain'` | `'decimal'`, `'currency'`, `'percent'` (42 means 42 %), `'compact'`, or `Intl.NumberFormatOptions` |
| `locale` | `'en-US'` (`'bn-BD'` with Bangla digits) | |
| `currency` | `'USD'` | `'BDT'` gives ৳ |
| `decimals` | 0 (1 for compact) | |
| `digits` | `'latin'` | `'bangla'`: ০১২৩৪৫৬৭৮৯ with lakh grouping (১২,৩৪,৫৬৭; compact ১২.৪ লাখ) |
| `mode` | `'count'` | `'roll'`: every digit a wheel; leading places fade in |
| `prefix` / `suffix` / `affixScale` | none / none / 1 | `affixScale` 0.5 hangs a small % from the cap height |
| `settle` | true | a 4.5 % scale bump on landing, pivoting on the baseline |
| `enter` | `'rise'` | `'fade'`, `'none'` (shows `from` before `delay`) |
| `align` | `'right'` | digits inside the reserved final width (right: digits never move) |
| TypeProps | size 160, role display | tabular numbers always |

```tsx
<Counter to={24813} format="currency" size={112} delay={6} />
<Counter to={99.98} decimals={2} suffix="%" affixScale={0.5} />
<Counter to={12450} digits="bangla" size={170} align="center" />
formatCount(1240000, {format: 'compact'}); // "1.2M"
```

Gotchas: counts show every intermediate value; if those are not facts, do not count (or use `mode="roll"` quickly).
Start the count on the word that names the number and land before the next clause.

## FitText, useFitText

The biggest size at which a text fits a width on one line (`fitText`) or N lines (`fitTextOnNLines`), measured after
the fonts load, tracking in em re-derived for the size found.

Props: `text`, `maxWidth` (safe width), `maxLines` (1), `maxSize` (280), `minSize` (24), `align`, `in` / `out`
(reveal the lines; default none), `delay`, `each` (5), `fonts` (extra kit fonts to wait for), TypeProps,
`children` (a render function receiving `{fontSize, lines, style, width}`).

```tsx
<FitText text="Revenue up 38%" maxWidth={830} maxSize={260} in="mask" />
const fit = useFitText(title, {maxWidth: 900, maxLines: 2}); // null until the fonts are ready
```

Gotcha: `fitTextOnNLines` fills lines greedily (use KineticTitle for balanced lines); it splits on spaces only.

## Marker

A clean marker sweep behind inline text that follows line wraps in reading order (one background on the inline box).

Props: `children`, `delay` (0), `duration` (18), `shape` (`'marker'` lower half, `'block'`, `'underline'`,
`'strike'`), `color` (theme highlight; translucent on dark themes), `thickness` (em), `textColor`, `ease`
(`curves.inOut`), `out` (false: true wipes it off at the end of the Sequence), `style`.

```tsx
<p>Most teams lose four hours a week to <Marker delay={10}>status meetings that could have been an update.</Marker></p>
```

## Annotate

Hand-drawn marks over `@remotion/rough-notation` (imported under aliases, so `Circle` and `Box` never collide), with
defaults that look right: translucent highlight, the doubled pencil stroke (`disableMultiStroke={false}`), sizes in
em of the annotated text (read from the page), a circle sized to enclose the words' corners, and room on each side
of circles, boxes and brackets so they do not run into the next word.

Props: `kind` (`'circle'` default, `'highlight'`, `'underline'`, `'box'`, `'strike'`, `'cross'`, `'bracket'`),
`children` (a short phrase: it never wraps), `delay` (0), `duration` (22; 26 for circles), `color` (highlight at
62 % or 40 % on dark; accent for marks; negative for strike and cross), `strokeWidth` / `padding` (px at 1080; default
from the text size), `iterations`, `roughness`, `bowing`, `seed` (1), `multiStroke` (true), `boil` (false: true
redraws every 4 frames once drawn), `brackets`, `role` (the text's font, waited for before measuring), `fonts`,
`ease` (`curves.outQuart`), `style`.

```tsx
Most teams lose <Annotate kind="circle" delay={34} role="serif">four hours</Annotate> every week.
<Annotate kind="highlight" delay={60} role="body">highlight</Annotate>
```

Gotchas: annotations measure their own box, so keep them out of parents with `display: none`; stagger several by 10
to 20 frames after the text has landed.

## TextPlate

The TikTok and Instagram caption plate: measured lines with one rounded outline around all of them
(`@remotion/rounded-text-box`), text revealed line by line.

Props: `text` / `lines`, `maxWidth` (86 % of the safe width), `maxLines` (3), `align` (`'center'`), `padding`
(0.45 of the size), `radius` (0.36 of the size), `tone` (`'invert'` default: text colour plate and ground colour
text; `'accent'`, `'surface'`, `'light'` white and black, `'dark'`), `plateColor`, `textColor`, `delay`, `plateIn`
(`'pop'`, `'wipe'`, `'draw'`, `'none'`), `textIn` (`'mask'`), `out` (true: shrinks and fades at the end of the
Sequence), TypeProps (size 60, role body, strong, line height 1.34, 1.55 for Bangla).

```tsx
<TextPlate text="The quiet part of every launch nobody films" size={66} />
<TextPlate text="Watch till the end" tone="accent" size={46} delay={40} plateIn="wipe" />
```

## BigStatement, Quote, Kicker, Label, LineStack

- **BigStatement**: one giant word or number (`word`) fitted to the width up to 58 % of the safe height, revealed
  per character from masks with a heavy settle, plus a small `note` (below or `notePosition="right"`) after an accent
  rule. Props: `word`, `note`, `notePosition`, `maxSize`, `maxWidth`, `align`, `color`, `accent`, `noteColor`,
  `delay`, `role`.
- **Quote**: a hanging accent quote mark, the quotation by word (serif role), an attribution with a short rule (never
  a dash). Props: `text`, `author`, `title`, `size` (76; 60 in 9:16), `maxWidth` (1450), `align`, `role`, `mark`,
  `delay`, `reveal`, `color`, `accent`.
- **Kicker**: a small spaced-capitals label above a title; a bar draws, then the words rise from a mask. Props:
  `text`, `size` (26), `color` (accent), `rule` (true), `delay`, `out` (false).
- **Label**: a pill tag that pops in. Props: `text`, `variant` (`'soft'`, `'solid'`, `'outline'`), `dot`, `size`
  (26), `color`, `delay`.
- **LineStack**: lines arriving on their cues (a narration, a lyric); spent lines step back to `dim` (0.3) and the
  stack nudges up `nudge` (10) px per arrival. Props: `lines`, `at` (frames) or `each` (36) and `delay`, `dim`,
  `nudge`, `align`, TypeProps (size 64).

```tsx
<BigStatement word="3x" note="faster code reviews since the team moved to written updates" notePosition="right" />
<Quote text={quote} author="Maya Chen" title="Head of Product, Northwind" />
<LineStack lines={['Some things are made slowly.', 'By hand, in small batches.']} each={36} role="serif" align="center" />
```

## Captions

### Data (`captionData.ts`, pure, Node or browser)

- `toCaptions(input, {unit, offsetMs})`: words from any transcriber (an array, `{words}`, or `{segments: [{words}]}`;
  keys `text`/`word`/`punctuated_word`, `start`/`end` in s or `startMs`/`endMs`) to `Caption[]` with a space before
  every word, none before punctuation, sub-word tokens kept as sent; ElevenLabs `spacing` and `audio_event` items and
  fillers (`[BLANK_AUDIO]`, `(music)`, `TT_12`) dropped. `unit: 'auto'` reads seconds unless every time is whole and
  some exceed 30.
- `remapCaptions(captions, cuts)`: through an edit; `CaptionCut = {inMs, outMs, atMs?, rate?}` (cuts without `atMs`
  follow each other); a word is kept when its middle is inside a cut. `cutsFromFrames(cuts, fps)` converts frame cuts.
  `shiftCaptions(captions, ms)`.
- `captionTimeAt(frame, fps, {trimBefore, playbackRate, offsetMs})`: the caption time under a trimmed or sped clip.
- `captionPages(captions, {pageMs 1200, silenceMs 600, maxHoldMs 900, maxWords 8})`: `createTikTokStyleCaptions`
  pages with whole words, never across a sentence end, no one-word orphan pages, a bounded hold after the last word.
  `captionPageAt(pages, ms)`.
- `subtitleCues(captions, {maxChars 42, maxLines 2, maxMs 7000, minMs 833, gapMs 700, cps 20})`: subtitle cues with
  balanced two-line breaks (after punctuation, never after a small word), new cues at sentence ends and pauses.
- `toSrt(captions | cues)`: an SRT string (`serializeSrt`).

### TikTokCaptions

Short pages with the spoken word marked. Place it in a full-frame layer (an `AbsoluteFill` or a Sequence).

| Prop | Default | Notes |
|---|---|---|
| `captions` | required | `Caption[]` |
| `highlight` | `'pill'` | `'color'`, `'scale'` (active word grows 10 %, words get extra space), `'karaoke'` (fill sweeps each word), `'plain'` |
| `reveal` | `'page'` | `'word'`: each word pops in as it is spoken |
| `pageMs`, `silenceMs`, `maxHoldMs` | 1200, 600, 900 | paging |
| `maxLines` / `maxWidth` | 2 / safe width less 40 | |
| `position` | `'bottom'` | `'center'`, `'top'`, or the block centre as a fraction of the safe height |
| `tone` | `'light'` | white text, dark outline (0.14 of the size, 0.1 for Bangla) and shadow for footage; `'theme'` |
| `activeColor` | highlight (accent for the pill) | |
| `plate` | false | a `PlateTone`: one rounded plate behind each page |
| `enter` | `'pop'` | `'rise'`, `'none'` |
| `trimBefore`, `playbackRate`, `offsetMs` | 0, 1, 0 | follow a trimmed or sped clip |
| TypeProps | size 76 in 9:16, 58 in 16:9 (10 % more for Bangla), role body, strong | |

The pill glides between words (a fractional word index from short eased steps) and the text on it is a second layer
clipped to the pill, so letters change colour exactly where the pill is, even mid-glide.

```tsx
const captions = toCaptions(whisperJson);
<AbsoluteFill>
  <TikTokCaptions captions={captions} highlight="pill" />
</AbsoluteFill>
```

### BoxedCaptions

Classic boxed subtitles (YouTube look), each line in its own box, low in the safe area. Props: `captions`,
`maxChars` (42; 32 in 9:16), `maxLines` (2), `maxMs`, `minMs`, `gapMs`, `cps`, `position` (`'bottom'`, `'top'`),
`box` (near-black 78 %), `textColor` (white), `readAlong` (false: true dims words not yet spoken), timing props,
TypeProps (size 46; 50 in 9:16). A cue wider than the safe area is set smaller, never cut.

### SubtitleFile

`<SubtitleFile captions={captions} filename="subtitles.srt" />` writes the SRT next to a render
(`out/<composition>/subtitles.srt`) through Remotion's `<Artifact>` on frame 0.

## Helpers

- Text: `graphemes`, `splitWords`, `splitLines`, `isBangla`, `isComplexScript`, `toBanglaDigits`, `toLatinDigits`,
  `isPunctuation`, `endsSentence`, `endsClause`.
- Fonts: `useTypeFontsReady(roles, extra)`, `WaitForFonts`, `waitForTypeFont`, `fontNeeds`, `roleFamily`, `roleWeight`,
  `trackingFor`, `leadingFor`, `maskPad`, `typeStyle`.
- Layout: `layoutText(text, style, {maxWidth, maxLines, balance, shrink, minSize})`, `measureTextWidth`, `typeCss`,
  `textAlignOffset`, `fontMetrics`, `baselineRatio`.
- Reveals: `RevealUnit`, `MaskUnit`, `staggerRank`, `isMaskReveal`.

```tsx
const ready = useTypeFontsReady('display');
const layout = useMemo(() => (ready ? layoutText(title, style, {maxWidth: 900, maxLines: 2}) : null), [ready, title]);
```

## Gotchas

- Measure only after `useTypeFontsReady()`; `@remotion/layout-utils` caches every measurement for the page, so a width
  taken with a fallback font stays wrong. Pass the same family, weight, size, tracking (em) and transform you render.
- A font named in CSS alone loads nothing: use the theme roles or core's `loadKitFont` / `fontStack`, and pass
  `fonts` (FitText, Annotate) so the component waits for them.
- Captions are whitespace sensitive: a space before each word, rendered with `white-space: pre` (the components do
  it). Words without leading spaces all merge into one page.
- Convert milliseconds to frames explicitly (`Math.round(ms / 1000 * fps)`); never add milliseconds to frames.
- Complex scripts: no letter spacing, no uppercase, more leading (Bangla 1.28 and up), never split by code point.
- The `Animate` mask of the motion module travels 110 % of the box, which lets tall letters peek through its padding;
  text components here use `MaskUnit` instead.
