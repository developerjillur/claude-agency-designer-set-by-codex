# Overlays and cards

Lower thirds, subscribe nudges, chapter bars, countdowns, tours and tooltips sit on top of a video for a while and then
leave; title, chapter and end cards own the whole frame; logo reveals open and close a film. This file gives their
anatomy, timings and the raw techniques behind them.

## 1. Lower thirds

| Look | Anatomy | In (30 fps) | Out |
|---|---|---|---|
| `bar` | a 12 px accent block, the name on a solid bar in the theme's text colour, the role on an accent bar | block grows 0-9, name bar wipes out of the block 4-18 (in-out), role bar 9-22, text slides 14 to 18 px behind its bar | last in, first out: role bar, then name bar, then block |
| `split` | a 5 px accent rule the height of both lines, name and role to its side | rule grows from its centre 0-11, name slides out from behind the rule 6-23, role 10-27 | text slides back into the rule, the rule collapses |
| `minimal` | the name in the display face, a short accent rule, the role in spaced capitals | name rises through a mask 0-18, rule draws 8-22, role rises 11-27 | down through the masks, rule retracts |
| `card` | a rounded card with an initials avatar, name and role | pops up on a settle spring, avatar and text 2 to 3 frames later | drops 20 px and fades |

- Placement: the bottom of the safe area on the left (or `side="right"`), `y` to lift it; in 9:16 the bottom of the
  platform-safe band (y 1248 at 1080 x 1920).
- Legibility: `bar` and `card` carry their own ground. `split` and `minimal` need a calm area or `scrim` (a soft dark
  radial gradient behind, light text, a faint text shadow).
- Length: names up to about 24 characters at `size={1}`; long roles wrap nothing (they stay on one line), so shorten
  them.
- Timing: arrive after the speaker's first words (about 1 s in), stay 4 to 6 s, leave before a cut; one lower third per
  person per film.
- The exit sub-timings scale with the `exit` length, so a shorter exit still ends every part on the Sequence's last
  frame.

Raw technique for bar wipes: animate `clipPath: inset(0 ${(1 - p) * 100}% 0 0)` (or `cropRight` on
`Interactive.Div`, 4.0.506) with `Easing.bezier(0.65, 0, 0.35, 1)`, and stack a second bar 4 frames later on the way in
and 4 frames earlier on the way out.

## 2. Title cards (`TitleCard`)

- Words, not letters: each word rises through its own mask (translate from 112% to 0), 3 frames apart, 17 frames each
  (expo-like ease out). A four-word title has landed by frame 26. Letters only for a 4 to 5 glyph wordmark.
- A kicker (spaced capitals, accent) wipes in first; the title starts 5 frames later; a subtitle rises 18 px as the
  last word lands; an accent `rule` draws under the title.
- One emphasis: `accentWord` colours one word in the accent.
- Break lines yourself with `\n` (balanced two-line titles read better than the browser's wrap).
- Sizes: 124 px in 16:9, 92 px in 9:16; the subtitle 40 or 36 px; left-aligned in landscape, centred in portrait.
- Hold at least the reading time of title plus subtitle; a slow push-in (3% over the card) keeps it alive (a still
  card reads as frozen on review).
- Exit (`exit={14}`): words go up through their masks last word first, all gone on the Sequence's last frame. Without
  an exit, cut on a settled frame.
- Bangla: the masks get more room above and below (vowel signs), and the line height grows to 1.34.

## 3. Chapter cards (`SectionTitle`)

A rule draws across (18 frames, in-out), the title rises above it (words, from frame 10), "Chapter 02 / 05" slides out
under it, and in the `full` variant a numeral at 460 px (300 in 9:16) in 6% of the text colour drifts in behind at the
top right. Use `inline` over content without its own ground. Chapters are numbered from the real structure of the
video; do not decorate every card with numbers when there is no sequence.

## 4. End cards (`EndCard`)

- Order of arrival: logo slot and name (0), the call-to-action headline (words from 8), subtitle, the button (a settle
  spring), then the address and handle, each 18 frames with a 24 px rise.
- One call to action, one button. A pointer may click it (`clickAt`); the label rolls to `doneCta`.
- YouTube end screens: the platform draws its own video and subscribe elements over the last 5 to 20 s, so `slots`
  reserve empty 16:9 frames on the right (up to two, 36% of the safe width each) with small labels. Keep your own
  content out of them.
- A 3% push-in over the card; no exit (it is the last thing).
- Portrait: everything centred and stacked, larger type (title 104 px).

## 5. Logo reveals (`LogoReveal`)

| Variant | Reads as | Use for |
|---|---|---|
| `mask` | calm, editorial | corporate, product updates |
| `stroke` | crafted, drawn | studios, design brands, marks with clear outlines |
| `scale` | energetic, playful | apps, consumer brands (one ring pulse, not a loop) |
| `split` | precise, technical | tools, fintech, two-part marks |
| `wipe` | fast, graphic | promos, social cut-downs |

A sting of 3 to 5 s: mark in 0 to 0.8 s, wordmark 0.6 to 1.8 s, tagline 2 to 3.5 s, a 1 s hold, exit in the last
0.5 s (`exit={16}`: a small scale-down, fade and blur, done on the last frame).

Making a mark: take the client's SVG, keep its `viewBox`, and list its paths as `parts`: filled shapes with `fill`
(theme roles like `'accent'` or real hex values), lines with `stroke` and `strokeWidth`. The `stroke` variant draws
every part with `pathLength={1}` and `strokeDasharray={1}` (no measuring), then fades the fills in. Real brand logos
only with the client's files and permission; drafts use `UI_MARKS` (note, orbit, peak, coin).

Raw techniques: draw-on with `@remotion/paths` `evolvePath(progress, d)` (needs a stroke and no dash of your own);
a logo cannot fill the frame by scaling (holes scale too), so reveal with a mask or flood a colour from inside the mark.

## 6. Subscribe nudge (`Subscribe`)

The card rises (18 frames, in-out, from 18 px); a pointer enters from the lower right and reaches the button 4 frames
before `clickAt` (delay + 44); the button presses, turns from red to a neutral tone with "Subscribed" and a check that
draws; 22 frames later the pointer presses the bell, whose icon fills and swings about its top (0, -18, 16, -11, 7, 0
degrees, 4 frames apart); the pointer fades; the card leaves on the last frame. `subscribeClicks({delay}, fps)` returns
both press frames for `ClickSounds`.

## 7. Chapter bar and countdowns

- `ChapterBar`: one segment per chapter, proportional to its length, 6 px gaps, a playhead dot; the current chapter's
  number and name roll up when the chapter changes; the fill is a clock (linear). On a rounded panel by default so it
  reads over footage; `panel={false}` over a calm ground.
- `Countdown`: `ring` (numbers punch in from 0.6 on a pop spring over a solid disc while the ring depletes each
  second), `roll` (numbers roll up in a card over 10 frames), `clock` (mm:ss, the digits that change roll). `go` is
  shown after the last number (`''` fades the last number out instead). Keep `plate` on over footage.

## 8. Tours and tooltips

- `FocusRing`: a veil at 55% with a rounded hole and a 3 px accent outline; the hole holds on each key's rectangle from
  its `at` and glides to the next over 14 frames (in-out), arriving on that key's frame. Give each stop at least 1.5 s.
- `UiTooltip`: dark on light interfaces, light on dark, 22 px text, a 9 px pointer; pops from the point on a pop
  spring. Put each tooltip in its own `<Sequence>` so it leaves before the ring moves on.
- A tour of more than four stops is a tutorial: split it into chapters.

## 9. Faults and fixes

| Fault | Cause | Fix |
|---|---|---|
| Part of a lower third still visible on the last frame | offsets add up past the exit | the kit scales sub-timings; in custom code end every part by the Sequence's last frame |
| Title exit cut off at the cut | a stagger longer than the exit | the kit compresses the stagger; in custom code start the last word's exit early enough |
| Countdown blinks between numbers | the new number starts at opacity 0 | punch in at full opacity from a smaller scale |
| Chapter bar unreadable over footage | bare text in the theme colour | the panel, or a scrim |
| End-screen slots cover the call to action | slots too big | at most 36% of the safe width each, CTA on the left |
| Logo looks cheap when it pops | overshoot on a serious brand | `mask` or `stroke` for calm brands, `scale` only for playful ones |
