# The quality bar

Numbers are for 30 fps and a 1080 px short side; scale with `at30()` and `unit`. They are defaults from measured
productions and the Remotion team's own components: tune them to the brand, but know when you are breaking them.

## Motion

| Thing | Default |
|---|---|
| Entrance, small UI | 8 to 11 frames |
| Entrance, cards, lines of text | 15 to 20 frames |
| Entrance, calm or premium | 18 to 28 frames |
| Exit | none (cut on a settled frame), or 12 to 18 frames with ease-in, faster than the entrance |
| Travel distance on entrances | 10 to 32 px, optionally scale from 0.86 to 0.99; never from 0; never opacity alone |
| Stagger | 2 to 4 frames within a gesture, 5 or 6 for a countable list, 24 to 29 between separate beats |
| Hold before an exit | 30 to 45 frames after settling; 1.5 s for multi-word lines; logos 1 s after landing |
| Reading time | 0.33 s a word + 0.3 s, never under 1.2 s, longer with numbers (`readingFrames`) |
| Camera moves | 14 to 24 frames per move, in-out ease; about 3 moves per chapter |
| Overlay life | about 4 s: in about 20 frames, hold, out 15 to 20 |
| Counters | start on the word that names the number, land before the clause ends, ease out |
| Stillness | nothing fully static over 3 s; but text is perfectly still while read |

Curves by role: arrivals `curves.out` (expo-like; `outCubic` for short travel, because strong curves freeze for
several frames at the end of a short move), departures `curves.in`, moves on screen and camera `curves.inOut`,
clocks `linear`, pops `outBack` (about 10% overshoot). Springs: `calm` (no overshoot) by default, `settle` for a
hint, `pop` or `bouncy` for one hero at a time. Custom: `appleSpring(duration, bounce)`.

Principles in Remotion terms: anticipation is a 2 or 3 frame counter-move; follow-through staggers attached parts 2
to 4 frames after the body; arcs come from different eases on x and y or a path; squash and stretch only on playful
directions (1.06 x 0.95 for 2 or 3 frames); staging means one focal element, and what has paid off dims or blurs
(blur 2.6 px, opacity 0.55). No element travels more than a third of the frame without an intermediate change.

Two failure modes to avoid: the **slideshow** (everything arrives at once, then nothing moves) and the
**screensaver** (everything drifts forever). Movement belongs to entrances, exits and verb-driven actions; during a
hold at most one element is alive, the hero, and background drift is allowed.

## Text

- Load every font with explicit weights (the kit does); a CSS name alone renders a fallback.
- Minimum sizes at 1080: captions for phones about 56 px (5% of the height), other text 32 px; UI inside a mock-up
  may be 12 to 14 px because that is how software looks.
- Two families at most. Weights 500 to 600 for premium heroes; avoid weights under 300 in motion (they shimmer after
  compression). Tracking on display type no tighter than about -0.04 em.
- Titles reveal by word or line behind a mask, not by letter and not with a fade; letters only for a 4 or 5 glyph
  wordmark. Negative tracking on big titles.
- Scale text around its baseline, set `textRendering: 'geometricPrecision'`, never `will-change` on text; grow
  numbers with `scale`, never by animating `fontSize`.
- `tabular-nums` on changing digits; one emphasis word per headline; key words may be huge (200 to 320 px) and one
  giant word plus one small note is a complete composition.
- Bangla: split by words (or graphemes with `Intl.Segmenter`), never by code point; use the theme's Bangla font;
  Bengali digits (০-৯) when the copy is Bangla.

## Composition and taste

- No vacuum: every frame sits on a lit ground (a light with a source, a texture, a horizon, parallax). A flat solid
  behind small floating content fails. Light must touch form; text parked in a glow core loses contrast.
- At least one full-bleed moment per act. A content box under 60% of the frame with dead margins reads as a slide.
  Premium frames keep about 40% negative space.
- One focal point: the hero wins on at least two of size, contrast, position and weight. Hierarchy order: motion,
  size, contrast, saturation, position. Group by proximity (inner gaps clearly smaller than outer gaps).
- One accent with a budget; tinted neutrals; a darker accent for small text on light grounds; no third hue except for
  states. Blend colours with a middle stop (`interpolateColors` blends in sRGB and greys out complementary pairs).
- Anti-slop list (a check, not a design): purple-blue gradients by default, three-column icon grids, cards on
  cards, gradient text, the hero-metric template, glassmorphism by default, glow on everything, emoji as icons,
  eyebrow labels on every section, 01/02/03 scaffolding, expanding ring ripples, heartbeat pulses, decorative
  divider bars, confetti endings, a globe or network as "tech", random particles, a headline over a full-bleed motion
  asset, the same visual formula in two adjacent beats, cream or sand grounds by default.
- Grain as texture re-seeded at about 12 Hz, never per frame (per-frame noise bloats the file and sizzles). Gradients
  band in 8-bit video: add 2 to 4% grain and keep at least two stops.

## Sound

- The voice is the loudest; the bed sits under it (about 0.04 to 0.1 of full volume under speech, up to 1 in scenes
  without speech, with 30-frame ramps); one effect per event, soft, a few dB under the voice.
- Raising a cue's volume in code cannot rescue a quiet file: level the file itself and trim it to its first hit.
- No ducking on hits that are synced to picture. Check each cue's window in the delivered file.
- Master on the delivered file: -14 LUFS integrated, true peak at most -1 dBTP (web and social), a limiter after the
  loudness pass. Two versions when music is used and the client may re-cut: with and without the bed.
- Sound effects: only licensed ones (in `@remotion/sfx`, 7 are CC0: whoosh, whip, uiSwitch, mouseClick, pageTurn,
  shutterModern, shutterOld; the rest are unlicensed meme sounds, never in client work); `nexa-sound` for the rest.

## Checks (measured, not guessed)

- Stills at every cue frame and 12 frames later on a contact sheet; full-size stills for anything detailed.
- Last frame of every shot: settled, nothing half-visible.
- Luminance jumps over 25 levels between adjacent frames only at intended cuts or flashes.
- No shot with stillness over 3 s, no settled hold under 30 frames before an exit.
- Largest object per shot big enough to read on a phone.
- File: codec, size, fps, duration within 5% of the promise, audio present, loudness, colour tags (bt709).
- Transcript of the rendered audio against the script (catches cut-off words).
