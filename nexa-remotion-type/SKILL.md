---
name: nexa-remotion-type
description: "Typography and captions for Remotion videos: kinetic titles and words that rise from masks, typewriters with key sounds, scramble decodes, word rotators, counters and odometers (currency, percent, compact, Bangla digits), text fitted to a box, marker sweeps and hand-drawn circles, underlines and strikes, caption plates, big statements, quotes and labels, and burned-in captions (TikTok pages with a gliding pill, karaoke or word pop; boxed YouTube subtitles; SRT files) from Gemini (whisper only for English) or ElevenLabs word timings, with Bangla that never breaks. Use it for any text on screen in a Remotion video, Banglish included ('caption add koro', 'title animation banao', 'counter animation lagbe'). Part of the nexa-remotion family."
---

# Type for Remotion

Words on screen, set and timed like a motion designer would: measured lines, masks instead of fades, one emphasis per
headline, numbers that never jiggle, captions that sit clear of the phone interface. Part of the nexa-remotion family:
the director skill is `nexa-remotion`, the kit lives in `~/.claude/skills/nexa-remotion/kit`, and a project made with
`nrk.py new` imports these parts from `./kit` (or `./kit/type`). Full props and gotchas per component:
`kit/src/kit/type/README.md`.

## Fast path

1. **Say what the text does**, then pick the part (table below): a title (`KineticTitle`), a line that arrives
   (`SplitText`), a number (`Counter`, `BigStatement`), emphasis inside a sentence (`Marker`, `Annotate`), speech on
   screen (`TikTokCaptions`, `BoxedCaptions`), a quotation (`Quote`), a label (`Kicker`, `Label`).
2. **Write the words with the `natural-copy` skill** and lint them (`copylint --copy onscreen.json`). One idea per
   line, one emphasised word per headline, every number said or sourced.
3. **Place it in the theme**: inside `<SafeArea>`, sizes in px at 1080, fonts through the theme roles (`display`,
   `body`, `mono`, `serif`, `hand`, `bangla`). Never name a font in CSS alone.
4. **Time it to the voice**: `delay` on the frame of the cue word, entrance done before the next cue, then a hold of
   at least `readingFrames(text, fps)`. Temporary text gets `out` so it is gone by the Sequence end.
5. **Captions**: transcribe once with word timings: Gemini 3.5 Transcribe for every language but English
   (`watch_video.py transcribe FILE --words --lang bn`, or `nvc.py transcribe`), whisper for English with Gemini as
   soon as it looks unsure (never whisper for Bangla: on a 22 s voice-over it misheard four correct words and passed
   a real slip). Then `toCaptions(json)`, `remapCaptions()` if the clip was cut or sped, `<TikTokCaptions>` for
   shorts or `<BoxedCaptions>` for YouTube, plus `<SubtitleFile>` to emit the SRT.
6. **Look**: `nrk.py stills PROJECT --frames` at each entrance, mid-hold and the last frame; a full-size
   `nrk.py still` for masks, Bangla shaping and caption position; `copylint` again after any text change.

## Components

| Component | Use it for | Key props |
|---|---|---|
| `SplitText` | a line or paragraph arriving by word (default), character (short words) or line | `text`, `by`, `in`/`out`, `each`, `maxWidth`, `lines`, TypeProps |
| `KineticTitle` | headlines: masks by word or line, balanced lines, tight tracking, emphasis | `text`, `by`, `emphasis`, `emphasisStyle` (punch, color, marker, block), `maxLines`, `align` |
| `Typewriter` + `typewriterSchedule` + `KeySounds` | typed text with caret, human rhythm, terminal output lines, key clicks on the landing frames | `cps`, `jitter`, `pauses`, `instant`, `caret`, `delay` |
| `Scramble` | a seeded decode that locks letter by letter | `duration`, `hold`, `charset`, `rate`, `order` |
| `WordRotator` | one word of a line cycling through options, the line gliding to the new width | `words`, `prefix`, `suffix`, `hold`, `transition`, `reveal`, `width` |
| `Counter` + `formatCount` | counts and odometers with Intl formats, Bangla digits, tabular slots, a landing settle | `to`, `format`, `currency`, `decimals`, `digits`, `mode`, `suffix`, `affixScale` |
| `FitText` + `useFitText` | the biggest size that fits a width on 1 or N lines | `maxWidth`, `maxLines`, `maxSize`, `in` |
| `Marker` | a marker sweep behind words that follows line wraps | `delay`, `duration`, `shape`, `color` |
| `Annotate` | hand-drawn circle, highlight, underline, box, strike, cross, bracket (rough-notation) | `kind`, `delay`, `color`, `boil`, `role` |
| `TextPlate` | the rounded caption plate that hugs each line | `text`, `tone`, `plateIn`, `maxLines`, `align` |
| `BigStatement` | one giant word or number plus a small note | `word`, `note`, `notePosition` |
| `Quote` | a quotation with a hanging mark and attribution | `text`, `author`, `title` |
| `Kicker`, `Label` | small caps label above a title; pill tags | `text`, `rule`, `variant`, `dot` |
| `LineStack` | lines arriving on cues while spent lines step back (narration, lyrics) | `lines`, `at` or `each`, `dim`, `nudge` |
| `TikTokCaptions` | burned-in short-form captions: pill, colour, scale, karaoke, word pop, plate | `captions`, `highlight`, `reveal`, `position`, `plate`, `sentenceMs` (pages by phrase, never mid-phrase), `trimBefore`, `playbackRate` |
| `BoxedCaptions`, `SubtitleFile` | YouTube-style boxed subtitles; an .srt next to the render | `maxChars` (42), `maxLines` (2), `readAlong` |
| data helpers | `toCaptions`, `remapCaptions`, `cutsFromFrames`, `captionTimeAt`, `captionPages`, `subtitleCues`, `toSrt` | pure, Node or browser |
| layout helpers | `useTypeFontsReady`, `WaitForFonts`, `layoutText`, `measureTextWidth`, `typeStyle`, `trackingFor`, `leadingFor`, `graphemes`, `baselineRatio` | for your own measured text |

## Craft rules

- **Words, not letters.** Reveal by word (3 frames apart at 30 fps, 14 to 20 frames each) or by line (6 apart).
  Per character only for a wordmark of up to 6 graphemes: letters in boxes lose their kerning and take too long to
  land. The whole line should have arrived within about 0.8 s.
- **Masks, not fades, for titles.** A word rises from its own clipping box; fading on top of a mask defeats it. Arrivals
  ease out, departures ease in and run faster (12 to 18 frames), and nothing is left half visible on the last frame.
- **Hold still while it is read**: at least 0.33 s a word plus 0.3 s (never under 1.2 s), 30 to 45 frames minimum
  before any exit. The camera or the ground may drift; the text does not.
- **Set it tight when it is big.** Tracking about -0.035 em from 100 px (never tighter than -0.05 em), 0 for body
  sizes, +0.06 to +0.12 em for small capitals, always 0 for Bangla. Leading 0.98 to 1.1 for display, 1.2 to 1.4 for
  body, at least 1.28 for Bangla display and 1.5 for Bangla body. Grow type with `scale` from the baseline, never by
  animating `fontSize`.
- **One emphasis per headline**, and make it win on colour plus one other thing (a punch, a marker, a circle). A
  marker sits behind the text; on a dark ground it becomes a block and the covered letters turn to the ground colour.
- **Sizes that survive a phone** (px at 1080): captions 56 to 80 (Bangla about 10 % more), supporting text at least
  32, labels 24 to 30; weights of 500 and up in motion (thin weights flicker after compression). Contrast 4.5 : 1 for
  small text; over footage use white with a dark outline (about 1/7 of the size) or a plate.
- **Numbers**: tabular digits, count over 30 to 60 frames with a strong ease-out, start on the word that names the
  number, land before the next clause with a small settle. Do not count through values that are not facts.
- **Typing**: 12 to 20 characters a second for headlines, 25 to 30 for interfaces; pauses after commas (5 frames),
  sentences (12) and lines (14); caret solid while typing, blinking when idle, never alone long before the first key.
  Budget: `delay + characters / cps * fps + pauses` must fit the shot.
- **Captions for shorts**: 2 to 4 words a page (pages of 800 to 1200 ms), at most 2 lines, never across a sentence end,
  no one-word orphan page, the spoken word marked. On 9:16 keep them inside the safe area (clear of the bottom 18 to
  20 % and the right rail); the kit puts the block's bottom at 95 % of the safe height.
- **Subtitles**: at most 42 characters a line (32 on 9:16), 2 lines, about 20 characters a second, each cue 5/6 s to
  7 s, balanced lines broken after punctuation and never after "a", "the", "to" or "of". Subtitles match the speech
  word for word; on-screen headlines never restate the voice-over.
- **Bangla**: split by grapheme with conjuncts kept whole (`graphemes()`), never by code point; no letter spacing,
  no uppercase, taller leading and deeper mask padding; Bengali digits with lakh grouping (১২,৩৪,৫৬৭).

## Recipes

**Title card** (kicker, title with one emphasis, supporting line, all leaving at the cut):
```tsx
<SafeArea justify="center" gap={34}>
  <Kicker text="Release 4.2" out />
  <KineticTitle text="Ship the update your users actually asked for" emphasis="actually" out="mask" delay={8} />
  <SplitText text="Written from 1,200 support tickets" role="body" size={40} in="rise" delay={40} out="fade" />
</SafeArea>
```

**A number beat**:
```tsx
<Counter to={24813} format="currency" size={140} delay={cue} />
<SplitText text="revenue this month" role="body" size={34} in="rise" delay={cue + 30} />
<BigStatement word="3x" note="faster code reviews since the team moved to written updates" notePosition="right" />
```

**Captions for a short from a whisper JSON in `public/`**:
```tsx
const [words, setWords] = useState<Caption[] | null>(null);
const {delayRender, continueRender, cancelRender} = useDelayRender();
const [handle] = useState(() => delayRender('captions'));
useEffect(() => {
  fetch(staticFile('talk.json')).then((r) => r.json())
    .then((j) => { setWords(toCaptions(j)); continueRender(handle); }, cancelRender);
}, []);
return words ? <AbsoluteFill><TikTokCaptions captions={words} highlight="pill" /><SubtitleFile captions={words} /></AbsoluteFill> : null;
```

**Captions after jump cuts and a speed change** (source ms to output ms):
```tsx
const cuts = [{inMs: 1200, outMs: 5400}, {inMs: 7000, outMs: 9800, rate: 1.25}];
<TikTokCaptions captions={remapCaptions(words, cuts)} />
// or over one trimmed clip in the same Sequence: <TikTokCaptions captions={words} trimBefore={90} playbackRate={1.5} />
```

**Typing with key sounds** (copy `kit/public/type/` into the project's `public/type/`):
```tsx
const timing = {delay: 10, cps: 16, seed: 'intro'};
const sched = typewriterSchedule(lines, fps, timing);
<Typewriter text={lines.join('\n')} role="display" size={88} align="center" {...timing} />
<KeySounds frames={sched.keys} volume={0.3} />
```

**Emphasis inside a paragraph**:
```tsx
<p style={{fontFamily: t.type.serif, fontSize: 76 * unit}}>
  Most teams lose <Annotate kind="circle" delay={34} role="serif">four hours</Annotate> every week to{' '}
  <Marker delay={10}>status meetings that could have been an update.</Marker>
</p>
```

**Bangla title, counter and captions** (theme `dhaka`):
```tsx
<KineticTitle text="মিটিং কম, কাজ বেশি" emphasis="বেশি" size={150} />
<Counter to={12450} digits="bangla" size={170} align="center" />
<TikTokCaptions captions={toCaptions(bnWords)} highlight="pill" />
```

## Remotion 4.0.528 facts and traps

- `@remotion/layout-utils` measures in a hidden `inline-block`, `white-space: pre` span and caches every result for the
  page (the key ignores `fontVariantNumeric`). Measure only after the fonts load (`useTypeFontsReady()`; the kit passes
  `validateFontIsLoaded: true`, whose default is false before v5) with the exact family, weight, size, tracking in em
  and transform you render; no padding or border on measured text. `fitTextOnNLines` (4.0.313) fills lines greedily
  and splits on spaces only; `fitText` (4.0.88) measures at 100 px and scales.
- Google Fonts through core only (explicit weights and subsets); `loadFont()` returns `waitUntilDone()`, which the
  kit's `waitForTypeFont()` uses. Local brand fonts: `@remotion/fonts` `loadFont({family, url: staticFile(...), weight})`.
  Variable fonts (`loadVariableFont`, 4.0.525) allow animating `fontWeight`.
- `createTikTokStyleCaptions` (4.0.216) only starts a page at a caption whose text begins with a space: without leading
  spaces the whole transcript is one page. `breakOnSilenceAfterMilliseconds` is 4.0.514+, `pageBreakAfter` 4.0.517+,
  page `durationMs` 4.0.261+ (it runs until the next page starts, through pauses). The official TikTok template adds
  milliseconds to a frame number: always `Math.round(ms / 1000 * fps)`.
- `serializeSrt` joins a cue's texts without spaces and floors times; `parseSrt` gives sentence-level captions without
  leading spaces (not for word animation). `<Artifact>` writes files on the frame it renders on (render it at 0).
- `@remotion/rough-notation` (4.0.490): `color` defaults to `currentColor` (a highlight then paints over the text),
  every type is built with a single stroke unless `disableMultiStroke={false}`, `Circle` and `Box` clash with other
  names (alias them), the annotated text never wraps, the first render waits for a measured size, and its `from`
  prop hides the text itself before `from` (drive `progress` instead).
- `@remotion/rounded-text-box` (4.0.360): measure every line with the same line height you render; lines stack with no
  gap; render each line with the same horizontal padding.
- The motion module's `Animate` mask travels 110 % of the box, so tall letters can peek through its padding at the
  start and end: text parts use `MaskUnit` (full travel) instead.
- `interpolatePaths` does not exist before 4.0.529; clamp every `interpolate()`; no `Math.random()`: scrambles and
  jitter use seeded `rand()`.

## References

- `references/layout-and-fonts.md`: loading and waiting for fonts, measuring, fitting and balancing lines, baselines,
  tracking and leading tables, the rounded text box.
- `references/captions.md`: the Caption type, transcription options and their output shapes, paging, remapping
  through edits, caption styles with numbers, subtitle rules, SRT, safe zones, errors.
- `references/annotations.md`: marker sweeps (the inline background technique), rough-notation in full with
  defaults and traps, hand-drawn looks and sequencing.
- `references/kinetic-craft.md`: decision tables and numbers for titles, typing, scrambles, rotators, counters,
  statements, quotes and line stacks; anti-patterns.
- `references/bangla.md`: Bangla and other complex scripts: fonts, clusters and conjuncts, spacing, digits, captions.
- `references/raw-remotion.md`: the same effects in plain Remotion without the kit, plus errors and fixes.
