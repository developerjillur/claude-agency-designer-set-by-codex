# Layout for video, safe zones and frame shapes

How to arrange a frame so it reads on a phone and survives every platform's UI and every aspect ratio.

## 1. Safe areas

The kit's core knows the formats (`FORMATS`, `useStage().safe`, `<SafeArea>`, `<SafeGuides>`, `<Stage format>`);
nrk.py and nexa-video-creator use the same numbers:

| Format | Frame | Safe rect (x, y, w, h) | Why |
|---|---|---|---|
| youtube | 1920 x 1080 | 96, 54, 1728, 972 | 5% margins |
| 4k | 3840 x 2160 | 192, 108, 3456, 1944 | the same, doubled |
| shorts, reels, tiktok | 1080 x 1920 | 65, 270, 875, 978 | clear of the title, the caption, the buttons and the right rail |
| story | 1080 x 1920 | 65, 270, 950, 978 | clear of the top bar and the reply box |
| feed | 1080 x 1350 | 54, 68, 972, 1215 | 4:5, 5% margins |
| square | 1080 x 1080 | 54, 54, 972, 972 | 5% margins |

`useStage()` picks the safe area from the frame size (or `<Stage format>` when a size is ambiguous, for example
1080 x 1920 story against shorts). Other sizes get 5% margins.

Reference numbers behind them:
- Broadcast: SMPTE's legacy guides put action safe at 90% and title safe at 80% of the frame; the HD update is 93%
  action and 90% title; EBU R95 for 16:9 HD uses 3.5% action and 5% graphics margins. For web video, an 80% title
  area survives phones that zoom to fill.
- Vertical platforms: reserve roughly the top 12 to 14% and the bottom 18 to 20%, plus a right strip on TikTok for
  the buttons (community tokens: TikTok top 100, bottom 180, right 80 px at 1080 x 1920; Instagram Stories top 100,
  bottom 120). Captions sit around 65% of the height, or 20% up from the bottom. The kit's safe rect is stricter
  than these (top 270, bottom 672, right 140): it keeps text clear of every platform at once.
- Platform UIs change: treat any capture (Remotion's Social Safe Zones Element uses iOS PNG captures) as a reference,
  not a guarantee, and hide the guide before the final render.

What must be inside the safe area: all text, logos, key numbers, faces that carry the story and anything clickable
looking. Grounds, pictures, patterns and decoration bleed to the edges. In 9:16 the lower third of the frame is
usually picture or ground only: let the picture (a `FullBleed`), a floor band or a `Split` ground fill it.

## 2. Frame shapes and responsive props

The kit classifies the frame: wide (aspect 1.3 and up, 16:9), square (0.9 to 1.3), portrait (0.68 to 0.9, 4:5),
tall (below 0.68, 9:16). Any `Responsive<T>` prop takes one value or one per shape; a missing shape falls back to
the nearest given one by aspect (`useLayout().pick`).

```tsx
const {pick, tall, shape} = useLayout();
const headline = pick({wide: 120, square: 104, portrait: 100, tall: 96});
<Grid columns={{wide: 3, square: 3, portrait: 1, tall: 1}} gap={{wide: 36, square: 22, tall: 24}} />
```

Rules for vertical versions (from teams that ship both):
- Build parallel compositions that share tokens and timing; the horizontal cut is the source of truth.
- Restack rows into columns instead of cropping the wide layout; recompute paths that sweep horizontally (a cursor
  crossing becomes a vertical scroll).
- Zoom punches grow downward from `transform-origin: center top`, and keep at least 5% of a card's height free
  around anything that punches.
- Test what fits: three stacked plan cards plus a title overflowed a 1:1 safe area (972 px tall) in the kit's tests,
  three columns fitted; on 4:5 (1215 px) stacking fitted and filled the frame better. The kit does not shrink
  content: check the stacked height on every shape.

## 3. Composition systems

Adjacent beats use different systems, one palette, one type voice and one light language across the film:

| System | Kit | Good for |
|---|---|---|
| Oversized type stack | `Center` or `SafeArea` with big type | a claim, a quote, a title |
| Full-bleed picture with a scrim | `FullBleed` | places, products, people |
| Split with a hard seam | `Split area="full" seam="hard"` | before and after, two options, a reveal |
| Asymmetric hero | `Split ratio={0.58}` | a picture and its point |
| One big number | `StatSplit` | the number that carries the story (once) |
| Grid of equals | `Grid` + `Card` | plans, steps, a gallery (not three identical icon cards) |
| Horizon world | `Ground kind="band"` or `EffectGround kind="floor"` | products standing on something, journeys |
| Bottom-rising surface | a `Card` or `Panel` rising from the lower edge | app screens, lists |
| Sequenced full-screen singles | one element per frame, hard cuts | kinetic promos |

Proportions that separate designed frames from slides:
- A content box under 60% of the frame with dead margins on all sides reads as a slide: at least one full-bleed
  moment per act.
- Premium frames keep about 40% negative space; headlines about 80% (big type, little else).
- One focal point; the hero wins on at least two of size, contrast, position and weight. Hierarchy order: motion,
  then size, contrast, saturation, position.
- Proximity: gaps inside a group clearly smaller than the gaps between groups (the kit's `SPACE`: 8, 16, 24, 40,
  64, 96, 144 px at 1080; one step inside a group, two or three between groups).

## 4. Type sizes and measure on video

- Minimum effective sizes at 1080p for phone viewing: narrative captions about 56 px (5.2% of the frame height),
  auxiliary text 32 px; UI inside mockups may go down to 12 to 14 px because that is how software looks. Chips and
  pills: 30 px (the kit's default), badges 28.
- Headlines 96 to 140 px on 16:9, 90 to 110 px in 9:16 (the frame is narrower); one giant word (200 to 320 px) with a
  small annotation is a complete composition.
- Measure: body lines of 28 to 45 characters on screen (shorter than print); `Center` defaults to 72% of the safe
  width on 16:9 and 96% in 9:16. Balance headline lines with `textWrap: 'balance'` (the kit's Center, FullBleed and
  StatSplit label do): no single orphan word on the last line.
- Optical centre: the eye puts the middle a little above the geometric one; `Center` lifts content by 3% of the
  area's height.
- Two type families at most; weights 500 and up in motion (thin weights flicker after compression); display tracking
  no tighter than about -0.04em; `fontVariantNumeric: 'tabular-nums'` for numbers that change.

## 5. Fitting text to a box

Measure, do not guess, and only after the font has loaded. The kit's fonts come from `@remotion/google-fonts`, which
adds each font face to `document.fonts` only once it has loaded, so `document.fonts.ready` resolves too early and a
measurement on the first render of a tab uses the fallback font. The kit's `useTextEm(text, style)` waits for the
face, measures a hidden span at 100 px, caches the result for the tab and holds the render meanwhile
(`StatSplit` uses it; sized from a digit-width guess, "87%" in Manrope ran past the edge of a 4:5 frame, because a
% is about 1.6 digits wide). For multi-line fitting and captions use the type module (`fitText`, `fitTextOnNLines` from
@remotion/layout-utils with `validateFontIsLoaded: true`).

## 6. Grids and gutters

- Columns: 16:9 takes 3 or 4 columns (12-column thinking: spans of 4 or 3), 1:1 and 4:5 take 2 or 3, 9:16 takes 1
  (sometimes 2 for small tiles).
- Gutters 32 to 40 px at 1080 on 16:9, 22 to 24 on narrow frames; margins are the safe area.
- A single-column tall layout needs fewer, bigger items; cut items rather than shrink them below the size floors.
- Align to the grid, then break it once on purpose for the thing that matters.

## 7. Showing several frame shapes in one frame

`<Sequence width height>` overrides `useVideoConfig()` width and height for its subtree (the Sequence's absolute
fill gets that size), so `useStage()` inside reports a real 1080 x 1920 frame with its own safe area and unit. Scale
the Sequence down with CSS `scale` and `transformOrigin: '0 0'` inside a clipped box to lay out tiles of different
shapes side by side (the kit's demos do this; also useful to show a vertical cut inside a 16:9 explainer). Give the
Sequence a `durationInFrames` so the inner duration stays finite.

## 8. Layout transitions (raw Remotion; the kit has no component yet)

- Picture in picture from full screen: over about 35 frames with one calm spring easing, crop the foreground scene
  (`cropLeft`, `cropRight` 0 to 0.3 and `cropTop`, `cropBottom` 0 to 0.06), scale it 1 to 0.38 from the top left, move
  it into a corner and round it (radius 0 to 48). Cropping keeps the subject framed as the box shrinks.
- Slide to a split screen: one progress value `interpolate(frame, [20, 52, 98, 130], [0, 1, 1, 0], {easing: [inOut,
  linear, inOut]})`; scene A's wrapper narrows from full to 60% minus a divider (overflow hidden) and its content
  shifts to stay centred; scene B and a 15 px divider slide in from the right.
- `Interactive.*` elements, `AbsoluteFill`, `Solid` and `Img` take `cropLeft/Right/Top/Bottom` (4.0.506) and Sequence
  timing props on 4.0.528, so these are a few inline keyframes.

## 9. Checks

- Every text and logo inside the safe outline on every shape you deliver (render stills of each composition).
- Nothing half visible on the last frame; nothing overflowing on 1:1 (the tightest height).
- No content box under 60% of the frame in more than one beat in a row.
- Each beat's system differs from the one before; one palette and light language throughout.
