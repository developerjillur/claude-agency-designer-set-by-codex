# The same effects in plain Remotion (no kit), and errors and fixes

For a project that does not use the kit, or an effect the kit has no part for. Everything is a pure function of
`useCurrentFrame()`; every `interpolate()` is clamped on both sides.

```tsx
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const out = Easing.bezier(0.16, 1, 0.3, 1);
```

## 1. Words rising from masks

```tsx
const Word: React.FC<{text: string; at: number}> = ({text, at}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + 16], [0, 1], {...clamp, easing: out});
  // box padding for accents and descenders; travel = line box + both paddings
  return (
    <span style={{display: 'inline-block', overflow: 'hidden', verticalAlign: 'top',
      padding: '0.14em 0', margin: '-0.14em 0'}}>
      <span style={{display: 'inline-block', translate: `0 ${(1 - p) * 1.4}em`}}>{text}</span>
    </span>
  );
};
// words.map((w, i) => <React.Fragment key={i}>{i ? ' ' : null}<Word text={w} at={i * 3} /></React.Fragment>)
```
Put the words in a block with `white-space: pre` when the lines are given, or `normal` to let it wrap at spaces.

## 2. Typewriter with a caret

```tsx
const chars = graphemes(text); // Intl.Segmenter, conjuncts merged (never text.split(''))
const shown = Math.min(chars.length, Math.max(0, Math.floor((frame - start) / framesPerChar)));
const typing = shown < chars.length;
const caretOn = typing || Math.floor(frame / 16) % 2 === 0;
return (
  <div style={{whiteSpace: 'pre'}}>
    {chars.slice(0, shown).join('')}
    <span style={{display: 'inline-block', width: 0, position: 'relative'}}>
      <span style={{position: 'absolute', left: '0.03em', bottom: '-0.2em', width: '0.075em', height: '1.08em',
        background: accent, visibility: caretOn ? 'visible' : 'hidden'}} />
    </span>
    <span style={{visibility: 'hidden'}}>{chars.slice(shown).join('')}</span>
  </div>
);
```
The hidden rest keeps the layout of the finished line (no drift, no reflow).

## 3. A counter

```tsx
const p = interpolate(frame, [start, start + 45], [0, 1], {...clamp, easing: Easing.bezier(0.25, 1, 0.5, 1)});
const text = new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD', maximumFractionDigits: 0}).format(to * p);
<span style={{fontVariantNumeric: 'tabular-nums'}}>{text}</span>
```
`new Intl.NumberFormat('bn-BD')` gives Bengali digits and lakh grouping. Reserve the final width (a hidden copy in the
same grid cell) so a growing number does not shift.

## 4. Fitting a title

```tsx
const {fontSize, lines} = useMemo(() => ready
  ? fitTextOnNLines({text, maxBoxWidth: 900, maxLines: 2, maxFontSize: 140, fontFamily, fontWeight: 800,
      letterSpacing: '-0.03em', validateFontIsLoaded: true})
  : {fontSize: 0, lines: []}, [ready, text]);
return <div style={{fontFamily, fontWeight: 800, fontSize, letterSpacing: '-0.03em', lineHeight: 1.05}}>
  {lines.map((l, i) => <div key={i} style={{whiteSpace: 'pre'}}>{l}</div>)}
</div>;
```
`ready` comes from the font loader's `waitUntilDone()` (see layout-and-fonts.md).

## 5. Captions from a JSON file

```tsx
const [captions, setCaptions] = useState<Caption[] | null>(null);
const {delayRender, continueRender, cancelRender} = useDelayRender();
const [handle] = useState(() => delayRender('Loading captions'));
useEffect(() => {
  fetch(staticFile('captions.json')).then((r) => r.json())
    .then((c) => { setCaptions(c); continueRender(handle); })
    .catch((e) => cancelRender(e));
}, [cancelRender, continueRender, handle]);
const pages = useMemo(() => createTikTokStyleCaptions({captions: captions ?? [], combineTokensWithinMilliseconds: 1200}).pages, [captions]);
// one Sequence per page, frames converted explicitly and clamped to the next page
pages.map((page, i) => {
  const from = Math.round((page.startMs / 1000) * fps);
  const next = pages[i + 1];
  const to = next ? Math.round((next.startMs / 1000) * fps) : from + Math.round((page.durationMs / 1000) * fps);
  return to > from ? <Sequence key={i} from={from} durationInFrames={to - from} layout="none"><Page page={page} /></Sequence> : null;
});
// inside Page: const now = page.startMs + (frame / fps) * 1000; active when token.fromMs <= now < token.toMs
```

## 6. An SRT next to the render

```tsx
const srt = serializeSrt({lines: cues.map((c) => [{text: c.lines.join('\n'), startMs: c.startMs, endMs: c.endMs, timestampMs: null, confidence: null}])});
{frame === 0 ? <Artifact filename="subtitles.srt" content={srt} /> : null}
```

## 7. A hand-drawn highlight

```tsx
import {Highlight as RoughHighlight} from '@remotion/rough-notation';
const progress = interpolate(frame, [20, 45], [0, 1], {...clamp, easing: out});
<RoughHighlight progress={progress} color="rgba(255, 221, 64, 0.62)" roughness={2.3} bowing={0}
  padding={{left: 18, right: 18}} disableMultiStroke={false}>remarkable</RoughHighlight>
```

## 8. A caption plate

```tsx
const measurements = lines.map((l) => measureText({text: l, fontFamily, fontSize, fontWeight: 700,
  additionalStyles: {lineHeight: '1.35'}, validateFontIsLoaded: true}));
const {d, boundingBox} = createRoundedTextBox({textMeasurements: measurements, textAlign: 'center', horizontalPadding: 24, borderRadius: 20});
<div style={{position: 'relative', width: boundingBox.width, height: boundingBox.height}}>
  <svg viewBox={boundingBox.viewBox} style={{position: 'absolute', width: boundingBox.width, height: boundingBox.height, overflow: 'visible'}}>
    <path d={d} fill="#fff" />
  </svg>
  <div style={{position: 'relative'}}>
    {lines.map((l, i) => <div key={i} style={{fontFamily, fontSize, fontWeight: 700, lineHeight: 1.35, textAlign: 'center', padding: '0 24px', whiteSpace: 'pre'}}>{l}</div>)}
  </div>
</div>
```

## 9. Other text effects

- **Variable weight**: `const {fontFamily} = loadVariableFont('normal', {subsets: ['latin']})` from a variable family
  (4.0.525), then `fontWeight: interpolate(frame, [0, 30], [300, 800], clamp)`; centre it (width changes).
- **Gooey morph between words**: two stacked spans cross-fading with a growing and shrinking blur, the parent filtered
  by an SVG `feColorMatrix` alpha threshold (`0 0 0 255 -140` on the alpha row) plus a slight blur; drive it from the
  frame and load the font properly (the example's CSS import does not block rendering).
- **Text as vector outlines** (warp, draw-on of letters): load the font file with opentype.js inside `delayRender`,
  `font.getPath(text, 0, size, size).toPathData(2)`, then `@remotion/paths` (`resetPath`, `warpPath`,
  `evolvePath`); an extra dependency, only when path operations are needed.
- **Text behind a person**: split the footage with `@remotion/video-matting` (base and foreground WebMs), then stack
  base video, the title, foreground video (see the edit sub-skill).
- **Animated emoji** next to text: `<AnimatedEmoji emoji="fire" />` from `@remotion/animated-emoji` plays Noto
  animated emoji videos from `public/` (copy the assets from the package's repository first).

## 10. Errors and fixes

| Symptom or message | Cause | Fix |
|---|---|---|
| Text in a fallback font, widths off | font named in CSS only, or measured before it loaded | load through `@remotion/google-fonts`/`@remotion/fonts` (the kit: theme roles), wait with `waitUntilDone()` |
| `Called measureText() ... but it looks like the font is not loaded` | `validateFontIsLoaded` caught a fallback measurement | wait for the font; check the family string |
| `measureText() can only be called in a browser.` | called in Node (`calculateMetadata`) | call inside a component, `useMemo` or `useEffect` |
| Text overflows although `fitText` said it fits | different CSS (padding, px tracking, resets, transform) | one style object, tracking in em, no padding, `outline` for debug |
| Lines break differently from the measurement | the browser re-wraps | render the measured lines with `white-space: pre` |
| Counter digits jiggle | proportional digits | `fontVariantNumeric: 'tabular-nums'`, or fixed-width digit slots |
| Scaled title shimmers or sticks | centre pivot, hinting, `will-change` | pivot on the baseline, `textRendering: 'geometricPrecision'`, no `will-change` in renders |
| Letters peek at the edge of a mask before or after a reveal | travel shorter than box plus padding | move by the line height plus both paddings |
| Highlight hides the text | rough-notation colour defaults to `currentColor` | a translucent colour |
| Single thin rough stroke instead of the pencil look | `disableMultiStroke` is effectively true by default | `disableMultiStroke={false}` |
| Annotation missing before its start | its `from` prop hides the text too | drive `progress`; do not pass `from` |
| Render timeout with annotations | annotated span has no size (hidden, empty) | give it content; no `display: none` parents |
| Bangla shows dotted circles or broken conjuncts | split by code point | split by word or by grapheme cluster with conjuncts merged |
| Captions on one giant page | no leading spaces | add a space before every word |
| Captions late or early after trimming | source times | remap through the cuts, or offset by `trimBefore` and `playbackRate` |
| SRT has words run together | `serializeSrt` joins texts without spaces | keep leading spaces, or pass one caption per cue with the full text |
| `Volume was set to 100 ...` on key sounds | a volume curve not clamped | clamp both sides; volumes are 0 to 1 |
