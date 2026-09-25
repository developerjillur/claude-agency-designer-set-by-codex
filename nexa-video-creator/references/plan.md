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
- Transitions go into a segment: cut (default), zoom, whip, dip, flash. One kind per video, used at section changes.

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

- `box` for callouts and redactions: `{"x": 0.62, "y": 0.08, "w": 0.3, "h": 0.06}` as fractions of the source frame
  (take them from a still of the proxy). `layer: "frame"` puts them in output coordinates instead.
- Text overlays stay on screen at least `clamp(0.35 x words + 0.5, 0.83, 7)` s (stat, list and compare 1 s more);
  the compiler lengthens them and warns when a type's maximum is too short for its text.
- Two overlays of the same slot (title, centre, card, full, lower) may not overlap.
- `sfx: null` silences an overlay's default sound; `sfx: "ding"` changes it.
- `facts`: `[{"text": "62%", "origin": "brief"}]` when a number on screen comes from the client, not the speaker.

### captions, chapters, music, sound effects, theme

```json
"captions": {"style": "word", "emphasis": ["w0044"]},
"chapters": [{"words": ["w0001", "w0004"], "quote": "why your audio drifts", "title": "Why it drifts"}],
"music": {"generate": "final", "mood": "tech"},
"sfx": [{"at": "word:w0044", "name": "impact"}, {"at": "overlay:2", "name": "pop"}, {"at": "time:12.4", "name": "riser"}],
"theme": {"accent": "#00C2A8", "display": "Montserrat", "body": "Inter"}
```

- Caption style `word` (vertical default), `sentence` (YouTube default, as SRT; `"burn": true` to burn in), `none`.
- Chapters: the first moves to 00:00; YouTube needs 3 or more, each 10 s or longer.
- Music: `source` (an ingested music id), `file` (a path), or `generate` (draft, final, realtime) with a `mood` from
  `nexa-sound moods`. The music is fitted to the edit's length, hits land near the weighted cuts, and it ducks under
  speech.
- Sound-effect cues: `overlay:<index or id>`, `word:<id>`, `clip:<index or id>`, `time:<seconds>`. Names come from
  `nexa-sound sfx list`. Default cues too close to another cue are dropped.

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
3. Segments in `voiceOnly` (the themed backdrop) or `brollFull`; the picture comes from b-roll, images
   (codex-imagegen), remotion-broll segments (2D characters, charts) and graphics. Keep a visual change every 3 to
   8 s (long) or 1.5 to 3 s (short).

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
