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
