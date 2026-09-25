# Craft and review for interface videos

What separates a designed product film from a template: a story built on the product's real behaviour, one readable
action at a time, honest content, and checks made on rendered pixels. The numbers below are at 30 fps and 1080 px
(the kit scales both).

## 1. Story grammar

**Product demo or launch (15 to 45 s)**
1. Hook, 0 to 3 s: the product on screen doing its most visual thing (a result, not a login screen).
2. The problem, optional, one line.
3. Three to five features, each as an action: a click, a typed query, a toggle, a swipe, and its visible result.
4. Proof: the real outcome (a published page, a saved expense, a deployed site), not an invented metric.
5. One call to action on an end card; a logo sting if the brand wants one.

**Tutorial (1 to 10 min)**: chapters with a `SectionTitle` or a `ChapterBar`; every step is shown, then held, then
explained; a pointer that rests while the voice explains; a focus ring or tooltip for the one control that matters.

**9:16 app promo (8 to 20 s)**: a big phone, taps not pointers, one flow from start to finish, the key UI inside the
platform-safe band, captions or short on-screen lines that do not repeat the voice.

## 2. Timing table

| Thing | Value |
|---|---|
| pointer move | 14 to 24 frames by distance; arrive 4 frames before the press |
| press | 2 frames down to 0.86, 9 back with overshoot; the control depresses 6% |
| state change after a press | 1 to 7 frames (label roll, colour) |
| screen change after a press | starts 6 to 10 frames after, lasts 18 to 22 |
| toast after an action | 6 frames after; about 1.5 s on screen |
| hold after an action | 30 to 45 frames; dense screens 90 to 120 |
| text hold | at least `readingFrames(text, fps)` (0.3 s + 0.33 s a word, never under 1.2 s) |
| overlay in / out | 18 to 22 / 12 to 14 frames, last in first out, ending on the Sequence's last frame |
| typing | prose 12 to 16 cps, commands 20 to 26, code 40 to 60 |
| camera punch-in | 1.2 to 1.35x, 20 to 30 frames in, hold through the action, 25 to 30 out |
| stagger | 2 to 4 frames for parts of one gesture, 5 to 6 for a list |

One focal move at a time: the camera rests while the pointer moves and the other way round; text is still while it is
read.

## 3. Composition

- A lit ground (`UiBackdrop` glow or dots) and real shadows; devices never float on a flat colour.
- 16:9: a window 70 to 80% of the frame width, or a phone 75 to 85% of the frame height beside a headline block of
  40 to 46% of the safe width; a second device behind at 90% size, rotated a few degrees.
- 9:16: a phone 650 to 720 px wide centred on the platform-safe band; the band holds the key UI.
- Frame 0 composed (small negative delays on entrances, chat history, a loading skeleton instead of an empty page).
- Fill containers with real content or shrink them: an empty half of a board or window reads as unfinished.
- One accent colour with a budget; states (positive, negative) only where they mean something.

## 4. Legibility

| Text | 16:9 | 9:16 |
|---|---|---|
| anything the viewer must read | 24 px or more | 32 px or more |
| on-screen headline | 88 to 124 px | 84 to 104 px |
| code | 26 to 30 px | 30 to 34 px, fewer characters a line |
| chat | 24 px in a 440 px phone, 30 in a panel | 36 px |
| lower-third name / role | 46 to 56 / 22 to 26 px | 50 to 60 / 26 to 30 px |
| window chrome (tabs, URL, menus) | 15 to 18 px (it is decoration) | same |

Over footage: solid bars, cards, plates or a scrim; never thin text straight on a busy picture.

## 5. Safe areas

- 16:9 (`youtube`): 5% margins, safe box (96, 54) to (1824, 1026).
- Shorts, Reels, TikTok (`shorts`): text and tapped controls inside (65, 270) to (940, 1248): the top 14% and the
  bottom 35% carry platform buttons and captions; a right strip carries the action rail.
- Story: (65, 270) to (1015, 1248). Feed 4:5 and square: 5% margins.
- The kit's overlays place themselves in `useStage().safe`; frames and blocks you position yourself must stay inside it.

## 6. Truth and content

- The client's real UI copy, product names, colours and logo files. Ask for them; do not invent them.
- For drafts and demos: neutral invented names (Driftnote, Coinlet, Orbitly, Taskwell, Studio Loop), people named in a
  plausible mix (Maya Chen, Arif Rahman, Lena Ortiz, Tanvir Hasan), `.example` domains and handles.
- No real brand chrome (no browser or OS brand), no copied messenger looks, no brand logos without files and
  permission, no personal data from real accounts in recordings.
- Numbers on screen must be true for the client or clearly illustrative; a counter shows every value it passes.
- Bangla and English both work in every text part; test with Bangla names and messages.

## 7. Sound for interfaces

Clicks and taps on the press frames (`ClickSounds`), a soft whoosh on screen pushes, nothing on every hover. Real foley
beats synthetic bleeps. Voice loudest; UI sounds 10 to 20 dB under it; the same click at the same level all film;
check the delivered file, not the preview.

## 8. Review checklist (before delivery)

1. `nrk.py stills PROJECT --every 0.5`: read the whole sheet. Frame 0 composed? The last frame clean (no overlay half
   gone)?
2. A full-size still at every press frame and 12 frames later: the tip on the target, the control reacting, the next
   state readable.
3. A trail image of one long pointer move (every second frame, darken-blended): pull-back, bow, settle.
4. Every text hold at full size: no fallback font, Bangla shaped (conjuncts whole), no clipped descenders in masks.
5. Contrast: fields visible in dark mode, overlays readable over the actual footage.
6. Safe areas: turn on `SafeGuides` from core for one still in each format.
7. Render, then `nrk.py qa PROJECT` (loudness, black and frozen frames, platform checks).
8. Write what you did not verify (audio by ear, full-rate motion, platform compression).

## 9. Failure patterns seen in our own review, with fixes

| Seen | Fix |
|---|---|
| a board whose columns were half empty | shorter containers, content that fills them |
| form fields invisible on a dark card | the kit's dark field colour and a stronger border |
| a walkthrough highlight while code was still typing | budget the typing; steps after it ends |
| title words still leaving on the cut frame | exits that end on the last frame (the kit compresses staggers) |
| a countdown that blinked between numbers | punch in at full opacity |
| chapter bar and countdown lost over footage | panels and plates |
| a focus ring drifting between stops | hold, then glide in the last 14 frames |
| scrolled content colliding with the phone clock | `barFill` |
| a click ring invisible on a blue button | a white ring with a dark hairline |
