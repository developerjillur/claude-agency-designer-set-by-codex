# The edit plan (nvc-plan/1)

The plan is the edit, written by Claude after reading `edit-brief.md`. It names what to keep, in what order and how
it looks, and points every choice at the words that justify it. `nvc.py compile` checks it and turns it into frames.
Times are never written by hand when words exist: a word id cannot land in the wrong place, and the quote check
catches a wrong id.

## Grounding

Most items take one of three anchors:

| Anchor | Meaning |
|---|---|
| `"words": ["w0012", "w0021"], "quote": "the exact words"` | the span of the transcript; the quote must match the words (case, punctuation and Bengali or ASCII digits are ignored) |
| `"at": "start"` or `"at": "end"` with `"seconds": 3` | the first or last seconds of the output |
| `"from": 12.0, "to": 15.5` | seconds: master clock for segments, output timeline for overlays; only when there are no words (music-only promos) |

A compile error quotes the transcript's real words, so a wrong quote is fixed by copying them.

## Fields

```json
{
  "schema": "nvc-plan/1",
  "target": "youtube",
  "title": "What the video is called",
  "language": "en",
  "segments": [],
  "remove": [],
  "holds": [],
  "punches": [],
  "zooms": [],
  "transitions": [],
  "overlays": [],
  "chapters": [],
  "captions": {"style": "word", "emphasis": [], "burn": true, "case": "upper"},
  "music": {"source": "music1"},
  "sfx": [],
  "theme": {"accent": "#FFD23F"},
  "auto_fillers": true,
  "trim_pauses_above_ms": 550,
  "pause_target_ms": 300,
  "progress_bar": false
}
```

### segments (required)

The kept spans in output order. Each: `words` + `quote` (or `from`/`to` in master seconds), and optionally:
- `layout`: camFull, screenFull, screenPip, split, stack, brollFull, voiceOnly. Default: screenPip (stack on 9:16)
  when there is a camera and a screen, else camFull, screenFull or voiceOnly. Vertical targets turn screenPip and
  split into stack.
- `beat`: a label for the report (hook, problem, step 1, proof, payoff, close).
- `cam`, `screen`: which source fills the camera or screen role (default: the first of each).
- `pip`: `{"corner": "br", "shape": "circle" | "rounded", "size": 0.17}` (size is a share of the frame width).
- `punch`: a scale for the whole segment (1.08 to 1.2); `auto_punch: false` stops the automatic punch-in that every
  second jump cut inside a camFull segment gets.
- `broll` + `in`: for brollFull, the source id and the second to start from.

Pauses inside a segment are trimmed to `pause_target_ms` when longer than `trim_pauses_above_ms` (the target sets
both: YouTube 550 to 300 ms, vertical 300 to 150 ms). Bounded filled pauses are cut unless `auto_fillers` is false.

### remove, holds, punches

```json
"remove": [{"words": ["w0031", "w0036"], "quote": "so the the first thing", "kind": "retake"}],
"holds": [{"words": ["w0050", "w0050"], "quote": "free.", "seconds": 0.8}],
"punches": [{"words": ["w0071", "w0073"], "quote": "this changes everything", "scale": 1.15}]
```

`kind` is filler, retake, tangent or other (for the report). A hold keeps the pause after the span's last word.

### zooms and transitions

```json
"zooms": [{"words": ["w0060", "w0064"], "quote": "click the export button", "layer": "screen", "x": 0.82, "y": 0.12, "scale": 1.8}],
"transitions": [{"segment": 3, "type": "zoom", "frames": 9}]
```

- A zoom starts 0.3 s before its words, eases in and out over half a second and holds at least 2 s. `x`, `y` are the
  point to bring to the centre (0 to 1 of the source frame). Layers: screen or cam. Read the point from a still.
- Transitions go into a segment: cut (default), zoom, whip, dip, flash, slide (the new clip slides over the last
  one), sweep (colour bars cross the frame and hide the cut). One kind per video, used at section changes.

### overlays

| Type | Props | Placement | Default sound |
|---|---|---|---|
| hook | text, highlight?, box? | title band | whoosh-short |
| keyword | text, emoji?, position? (top, center, bottom), color? | centre (over the screen panel of a split) | pop |
| stat | value, label, source? | card: side away from the face or the camera panel; title band on 9:16 | impact |
| list | items[], title? | card; items appear one by one | pop |
| compare | left, right, title? | centre | whoosh-short |
| quote | text, by?, highlight? | full frame | whoosh |
| chapter | title, label? | title band | whoosh |
| lowerThird | name, role? | lower band, left | swipe |
| callout | label?, spotlight?, layer? + `box` | on the recording (moves with its zoom) | click |
| redact | style? (blur, solid), layer? + `box` | on the recording, from its first frame | none |
| broll, image, segment | `source` (+ `in` seconds), fit (full, box), box?, motion? (push, pull, pan-left, pan-right, none), enter? (cut) | full frame or an inset card | whoosh |
| cta | text, sub? | lower band, centred | ding |
| label | text, corner? (tl, tr, bl, br), tone? (dark, light, accent) | a location-style chip in a corner of the safe area | pop |

- `box` for callouts and redactions: `{"x": 0.62, "y": 0.08, "w": 0.3, "h": 0.06}` as fractions of the source frame
  (take them from a still of the proxy). `layer: "frame"` puts them in output coordinates instead.
- Text overlays stay on screen at least `clamp(0.35 x words + 0.5, 0.83, 7)` s (stat, list and compare 1 s more);
  the compiler lengthens them and warns when a type's maximum is too short for its text.
- Two overlays of the same slot (title, centre, card, full, lower) may not overlap.
- `sfx: null` silences an overlay's default sound; `sfx: "ding"` changes it.
- `facts`: `[{"text": "62%", "origin": "brief"}]` when a number on screen comes from the client, not the speaker. A
  fact vouches for the numbers written in its text (list them all: "1 week 1.07x 6 months 6.1x"); a fact with no text
  covers the whole overlay. Origins: brief, client, web, formula.

### scenes (designed full-frame moments)

A scene fills the whole frame with a designed composition in the remotion-broll kit's style: bright palette colours,
warm dotted paper, white cards with soft shadows, words that rise out of a blur, hand-drawn underlines on key words,
drifting bubbles, count-ups that land with a bounce, and a slow push-in on every hold. A faceless video is carried by
them (one every 3 to 8 s); over a camera the speaker stays on in a round picture with a ring that moves while they
talk (`"pip": false` turns it off). Ground each scene on the sentence it shows, like any overlay.

| Type | Props | What it shows | Comes in | Sound |
|---|---|---|---|---|
| kinetic | text (or lines[]), highlight?, bg? (dusk, paper, color), color? | the words said, large, rising one by one; highlight words in the key colour with a hand-drawn underline | cut | whoosh-short |
| step | n, title (or lines[]), label?, color? | a numbered chapter card on a palette colour: the badge spins in, "Step n" (ধাপ n in Bangla), the title word by word, an accent bar | sweep | whoosh, then pop on the badge |
| bigStat | value, title?, label?, series[]?, xLabels?, source?, color? | a big number counting up on a white card on paper; with `series` a curve drawn with it, the tip pulsing once it lands | slide | whoosh-short, ding on landing |
| bars | rows[{label, value, text?}] (2 to 6), title?, note?, focus?, color? | bars that grow one after another, linear in value; the focus row (default the largest) grows last and lands with a bounce | slide | whoosh-short, ding on landing |
| versus | left, right: {label?, text?, value?, source?, color?} or a string | a split: two panels, a label chip on each, a hand-drawn seam that boils; a picture or clip in a panel when `source` is given | sweep | whoosh-short |
| recap | items[{label, text?, source?}] (2 to 4), title?, color? | cards on a dark board, popping in turn and floating; a picture in a card, else its number | slideUp | whoosh-short |
| endCard | text (or lines[]), button?, pressed?, icon? (bell, none), color? | the call to action rising in, a cursor that clicks the button, the button turning into its pressed state, the bell ringing | slideUp | whoosh, click and ding on the click |
| photo | `source` (+ `in`), label?, caption?, style? (card, full), bg?, motion? (push, pull) | a picture or clip in a tilted white card on paper with a label chip, or full frame with a slow push | slide | whoosh-short |

- `enter` and `exit` on any full-frame overlay: slide, slideUp, pop, fade, sweep or cut. A scene that slides, pops
  or fades in lands over the one before it (that one stays underneath for its first frames); a sweep hides the cut
  with colour bars.
- Titles are broken into even lines by the compiler (a number stays with its word); `lines` keeps a hand break,
  which is broken again when it is far too long for the frame (a 16:9 break used on 9:16).
- Scenes in a row touch: a gap under a second between two full-frame overlays is closed. A scene next to another
  ends where the next begins, down to its type's minimum (the compile warns when that leaves its words too little
  time).
- Numbers on a scene follow the overlay rule: said in the grounded words, or `facts` with origin brief, client, web
  or formula (a value computed from others, such as 1.01 to the power of 365). A `series` always asks for its
  source.
- kinetic, step, endCard and quote hide burned captions while they show (the words are on screen already);
  `"captions": true` in props keeps them. Other scenes keep their cards above the caption box.
- In Bangla, labels and buttons come in Bangla (ধাপ ১, সাবস্ক্রাইব করুন), numbers in Bengali digits, titles in
  Anek Bangla. The end card's button defaults to Subscribe on YouTube and Shorts and Follow elsewhere; `"button":
  null` leaves it out.
- The palette, paper, key colour and backdrop come from the theme (below). A faceless edit gets the paper backdrop
  between scenes, a filmed one the dark light pools.

### vox beats (the Vox explainer look)

A `vox` overlay is one composition on a locked paper ground (warm grey, a faint grid, printed grain), grounded to
the sentence or sentences it shows. Its `elements` come in on the words they show and may leave on others; beats in
a row share the paper, so a cut between them swaps the pictures while the paper stays. The look, the rules and a
beat-by-beat recipe are in `vox.md`; `nvc.py brief JOB --style vox` writes a storyboard of the narration as beats.

```json
{"type": "vox", "words": ["w0034", "w0047"], "quote": "Oil prices skyrocketed to $116 a barrel, pushing American inflation to a three-year high,",
 "exit": "cut", "facts": [{"origin": "web", "text": "CPI-U, annual average change 2016-2024: 1.3 2.1 2.4 1.8 1.2 4.7 8.0 4.1 2.9",
                            "url": "https://www.bls.gov/cpi/"}],
 "elements": [
   {"id": "sea", "kind": "clip", "source": "sea", "slot": "floor", "layer": "fore", "feather": {"top": 0.3}, "at": "start"},
   {"id": "ship", "kind": "cutout", "source": "tanker-cut", "x": 0.36, "y": 0.86, "anchor": "bottom", "w": 0.62,
    "enter": "slideRight", "drift": {"x": 0.008}, "at": "start", "out": "w0041"},
   {"id": "price", "kind": "tag", "value": "$116", "from": 25, "unit": "per barrel", "icon": "barrel",
    "at": "w0034", "land": "w0038", "follow": "ship", "dx": 0.3, "dy": -0.5},
   {"id": "chart", "kind": "chart", "title": "U.S. inflation rate", "at": "w0042", "drawAt": "w0043", "drawEnd": "w0047",
    "series": [{"name": "CPI", "values": [1.3, 2.1, 2.4, 1.8, 1.2, 4.7, 8.0, 4.1, 2.9]}],
    "xLabels": ["2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"], "yPrefix": "+", "ySuffix": "%",
    "callout": {"text": ["2022 peak", "+8.0%"], "index": 6, "at": "w0046"}},
   {"id": "src", "kind": "credit", "text": "Source: BLS", "at": "w0043"}]}
```

| Kind | Fields | What it is | Comes in |
|---|---|---|---|
| cutout | source, h? or w?, drift?{x,y}, shadow? (none, soft, ground), flip?, bw? | a cut-out picture (`nvc.py cutout`): halftone people with the marker stroke, colour objects; `bw` gives a colour cut-out the archival look | rise (grounded) or pop |
| clip | source, w?, h?, feather?{top,bottom,left,right}, blend?, bw?, trimBefore? | a clip or picture in the collage: a band of sea (`slot: floor`), a keyed fire (`nvc.py key`) | fade |
| card | source, caption?, bw? | a photo as a print with a white border and a typed caption | pop |
| headline | text or lines, highlight?, mark?, markAt?, count?, land?, size?, color? | heavy caps; `highlight` words in the accent, `mark` words get a highlighter band at `markAt`, `count` counts the number up to `land` | wipe |
| label | text, caps?, box?, size?, weight?, accent? | a small line: a place, a quantity, a caption | fade |
| credit | text | the source line, bottom left, small caps | fade |
| tag | value, from?, unit?, icon? (barrel, coin, dollar, taka, up, down, pin, warning, check, cross), land?, follow?, dx?, dy? | a number that counts from `from` and lands on `land` with a bump; `follow` rides on a moving element | pop |
| bubble | text or lines, highlight?, tail? (right, down-right, down, down-left, left, up-left, up, up-right, or degrees) | a comic speech bubble, key words in the marker colour | pop |
| newspaper | masthead, headline, marks?[{text, at}], deck?, byline?, section?, kicker?, corner?, left?[], right?[], body?, source?, photoCaption?, tilt?, illustrative? | a tilted page; each mark's words get the highlighter as they are said. `"illustrative": true` says the masthead is made up; a real paper's headline needs its source in facts (else it goes to the review list) | rise |
| chart | title, series[{name?, values[], color?}] (1 to 3), xLabels?, xValues?, yPrefix?, ySuffix?, note?, drawAt?, drawEnd?, callout?{text[], at, index?, series?} | a cream card: gridlines, the lines drawn left to right, dots popping as the line reaches them, a pulsing call-out; `xValues` (rising numbers, like years) places uneven steps truly | rise |
| typewriter | text or lines | typed word by word on the spoken frames, block cursor | none |
| scribble | shape (circle, underline, arrow, cross, box), w?, h?, thick?, color? | a marker mark drawn on | none |
| icon | icon, size?, color? | one of the tag icons on its own | pop |

- Every element: `id` (for `follow`), `at` (in), `out?` (leaves, by its nearest side edge; without it, it stays to
  the beat's end), `enter?` (rise, pop, slideLeft, slideRight, drop, wipe, fade, none), `exit?` (drop, fade, pop,
  slideLeft, slideRight, rise, cut), `moves?[{at, x?, y?, slot?, scale?, rotate?, frames?}]`, `layer?` (back, mid,
  fore, text), `slot?` or `x`/`y` (shares of the frame) with `anchor?`, `rotate?`, `scale?`, `float?` (false stops
  the idle float), `sfx?` (a nexa-sound name, or false).
- Times: a word id (`w0012`: the entrance lands just before the word), `w0012.end`, `w0012+0.3` or `w0012-0.2`
  (exactly, no lead), seconds from the beat's start (`1.5`), `start`, `end`. A word outside the beat is an error.
- Slots (landscape; vertical frames keep text in the top half and stand pictures on the bottom edge): center, left,
  right, top, bottom, top-left, top-right, bottom-left, bottom-right, sky, stage, stage-left, stage-right, far-left,
  far-right, floor. Defaults by kind: cut-outs on `stage`, clips on `floor`, headlines `top`, labels `bottom`, tags
  `top-right`, bubbles `top-left`, the typewriter on the left, the credit bottom left.
- Cut-outs are sized by height unless `w` is given: on the bottom edge 0.8 of the frame in `mid` (people), 0.5 to
  0.62 in `fore` (a band wide enough to hide the people behind it), 0.9 in `back`; 0.46 floating. They stand a
  little under the bottom edge so a cut-off bottom never shows.
- The beat: `exit` cut (default: the pictures vanish at the cut, the next beat's rise in), drop, fade, slide or pop
  (played under the next beat's first 12 frames), leak (warm light over the cut); `push` (0.035) is its slow push-in;
  `step: 2` draws its motion on twos. `sfx: false` silences its cues.
- The compiler moves a text that pokes out of the safe area back in (and records it), warns on text over text, on
  too little time to read, on a full spoken sentence on screen (except the typewriter), on more than 5 s with
  nothing new, and on more than 7 things at once; a newspaper and a chart always go to the review list.
- A vox beat brings the Vox theme (paper, orange accent, marker, highlighter, cream cards, Montserrat) unless the
  job or plan sets its own; a faceless edit gets the grid paper between beats. `"progress_bar": "bottom"` draws the
  explainer's thick bar.

### captions, chapters, music, sound effects, theme

```json
"captions": {"style": "word", "emphasis": ["w0044"]},
"chapters": [{"words": ["w0001", "w0004"], "quote": "why your audio drifts", "title": "Why it drifts"}],
"music": {"generate": "final", "mood": "tech"},
"sfx": [{"at": "word:w0044", "name": "impact"}, {"at": "overlay:2", "name": "pop"}, {"at": "time:12.4", "name": "riser"}],
"theme": {"accent": "#00C2A8", "display": "Poppins", "body": "Inter",
          "palette": ["#FF7A2F", "#6D3AF0", "#1F5C63", "#E8521A", "#2A6FDB"], "paper": "#F4EEE5", "highlight": "#FFC43D",
          "backdrop": "paper"}
```

- Caption style `word` (vertical default), `sentence` (YouTube default, as SRT; `"burn": true` to burn in), `none`.
- Chapters: the first moves to 00:00; YouTube needs 3 or more, each 10 s or longer.
- Music: `source` (an ingested music id), `file` (a path), or `generate` (draft, final, realtime) with a `mood` from
  `nexa-sound moods`. The music is fitted to the edit's length, hits land near the weighted cuts, and it ducks under
  speech.
- Sound-effect cues: `overlay:<index or id>`, `word:<id>`, `clip:<index or id>`, `time:<seconds>`. Names come from
  `nexa-sound sfx list`. Default cues too close to another cue are dropped (4 s apart in long videos, 1 s in short
  ones); a scene's own moments (a landing, a click) are always kept, and a scene that comes in with a sweep or a
  slide keeps its whoosh unless another transition is under 1.5 s away.
- Theme: `palette` gives the scene colours in order (step 1 takes the first), `paper` and `paperText` the data
  cards' ground and ink, `highlight` the key-word and ring colour, `backdrop` (paper, dusk, pools) what shows between
  scenes, `displayBn` and `bodyBn` the Bangla fonts (Anek Bangla and Hind Siliguri).

## Recipes

### YouTube tutorial: face camera and screen recording (the most common job)

1. Hook: the result or the promise, camFull, a hook title from frame 0.
2. Steps: screenPip with the face in the corner, a zoom wherever something small is clicked, a callout on the button,
   a list card for the steps, redactions on private data.
3. Explanations and opinions: camFull or split. Payoff and close on the face; CTA at the end; chapters per step.

```json
{
  "schema": "nvc-plan/1", "target": "youtube", "title": "Sync a screen recording with your camera",
  "segments": [
    {"words": ["w0004", "w0017"], "quote": "...", "beat": "hook", "layout": "camFull"},
    {"words": ["w0018", "w0090"], "quote": "...", "beat": "step 1", "layout": "screenPip"},
    {"words": ["w0091", "w0140"], "quote": "...", "beat": "why it works", "layout": "split"},
    {"words": ["w0141", "w0160"], "quote": "...", "beat": "close", "layout": "camFull", "punch": 1.12}
  ],
  "overlays": [
    {"type": "hook", "at": "start", "seconds": 3, "props": {"text": "Sync in 10 seconds", "highlight": "10 seconds"},
     "facts": [{"text": "10 seconds", "origin": "brief"}]},
    {"type": "callout", "words": ["w0060", "w0064"], "quote": "...", "box": {"x": 0.78, "y": 0.06, "w": 0.12, "h": 0.05},
     "props": {"label": "Export"}},
    {"type": "cta", "at": "end", "seconds": 4, "props": {"text": "Subscribe", "sub": "Part 2 on Friday"}}
  ],
  "zooms": [{"words": ["w0060", "w0064"], "quote": "...", "layer": "screen", "x": 0.84, "y": 0.09, "scale": 1.8}],
  "chapters": [{"words": ["w0004", "w0006"], "quote": "...", "title": "The problem"},
               {"words": ["w0018", "w0020"], "quote": "...", "title": "Step 1"},
               {"words": ["w0091", "w0093"], "quote": "...", "title": "Why it works"}],
  "captions": {"style": "sentence"},
  "music": {"generate": "final", "mood": "tech"}
}
```

### Shorts, Reels, TikTok cut-down from a long video

`plan.shorts.json` with `"target": "shorts"`: one idea in 20 to 60 s, the strongest line first (a cold open from the
middle is fine), stack layout for screen parts, word captions with one emphasis per phrase, a visual change every
1.5 to 3 s (punches, keyword pops, b-roll), a loop or a CTA of 2 s or less. Then `compile`, `audio`, `render` with
`--target shorts`.

### Faceless explainer (nexa-speech voice-over)

1. Script with natural-copy; voice with nexa-speech (`render`, `master`, `align`).
2. `nvc.py add JOB vo_48k.wav --role voice`: the `words.json` that nexa-speech's `align` wrote next to it becomes
   the transcript (ids w0001...), so no transcription is needed. Without it, run `transcribe`.
3. Segments in `voiceOnly` (the paper backdrop) or `brollFull`; the picture is carried by scenes, one per sentence
   or two: kinetic for the hook and key lines, step cards for sections, bigStat and bars for numbers, versus for
   before and after, photo for b-roll and stock (nvc.py stock), recap, and an end card. remotion-broll segments add
   drawn characters where the story needs acting. Keep a visual change every 3 to 8 s (long) or 1.5 to 3 s (short).

```json
"overlays": [
  {"type": "kinetic", "words": ["w0001", "w0008"], "quote": "...", "props": {"text": "Most people quit learning to edit halfway through", "highlight": "halfway"}},
  {"type": "step", "words": ["w0017", "w0023"], "quote": "...", "props": {"n": 1, "title": "Practise ten minutes a day"}},
  {"type": "photo", "words": ["w0024", "w0029"], "quote": "...", "source": "px-43559", "props": {"label": "Every day"}},
  {"type": "bigStat", "words": ["w0045", "w0058"], "quote": "...", "props": {"title": "Get 1% better every day", "value": "37.8x",
   "label": "after one year", "series": [1, 1.35, 1.82, 2.45, 3.3, 4.45, 6.0, 8.1, 10.9, 14.7, 19.8, 26.7, 36.0, 37.8],
   "xLabels": ["Today", "1 year"]}, "facts": [{"text": "37.8x", "origin": "formula"}]},
  {"type": "endCard", "words": ["w0092", "w0103"], "quote": "...", "props": {"text": "Start today"}}
]
```

### Vox-style explainer (faceless, pictures on paper)

1. Script with natural-copy (one idea per sentence, lines that point at what is shown); voice with nexa-speech;
   `nvc.py add JOB vo_48k.wav --role voice`.
2. `nvc.py brief JOB --style vox`: the storyboard of beats. For each beat pick the anchor picture and what follows
   on which words; find the pictures with `nvc.py stock`, then `nvc.py cutout` (people halftone with the marker
   stroke, objects in colour) and `nvc.py key` (fire, smoke on black).
3. One `vox` overlay per beat, segments in `voiceOnly`, `"progress_bar": "bottom"`, facts on every number.
4. `compile`, `stills` (look at every beat once its pictures have landed), `audio` (music low, the beat's soft
   cues), `render`, `qa`, `deliver`.

### Ads (15 to 30 s)

0 to 3 s hook with the product visible; 3 to 8 s the product working; 8 to 12 s proof (a number, a result); last 3 s
the offer and the CTA spoken and shown. At least 3 distinct scenes. Captions on (most feeds play muted at first).
Claims only with proof; no fake testimonials; Meta ads use no licensed commercial music.

### Promo from product assets, no speech

Add the music with `--role music` (it becomes the master clock), images and clips as broll or image. Segments are
`from`/`to` ranges of the music; overlays use `from`/`to` output seconds; hits go on the music's downbeats
(nexa-sound fit reports them).

### Day and occasion videos

5 to 15 s story or 15 to 30 s reel: the occasion visual and greeting in the first second, the brand message, a 2 s
sign-off. Dates and customs from the client's market; natural-copy's occasion rules for the words.

## What the compiler checks

Quotes and ids, removed words used by an overlay, slot overlaps, zoom overlaps, reading times, numbers not said,
the hook (first word by 0.5 s), the target's length limit (Shorts and Reels 180 s), static stretches longer than the
target allows, chapters, sources that do not cover a segment (the layout falls back and says so), and repeated
recording time across segments.
