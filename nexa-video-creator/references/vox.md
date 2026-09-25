# Vox-style explainers

The look of Vox, Johnny Harris and the Claude Code + Remotion explainers that copied them: a locked paper ground,
cut-out photos and objects that rise and pop on the narration's words, halftone people with a red marker stroke,
bold numbers, charts that draw themselves, a newspaper with a highlighter, comic bubbles, a typewriter closer. This
page is the recipe. The research behind it (sources, measurements, the reference video frame by frame) is in
`research/vox-01-mosidd-workflow.md`, `research/vox-02-style-bible.md` and `research/vox-03-remotion-toolkit.md`.

## What makes it work

1. **The story is visual.** Every claim has a picture that shows it: a place, a document, a price, a chart, the
   people involved. Narration over generic stock is not this style.
2. **One anchor picture per beat,** then one new thing at a time, about a second apart, each landing just before
   the word it shows. Picture and voice arrive together; a viewer follows 3 to 5 things at once.
3. **One locked ground.** The same paper behind every beat, so hard cuts between beats read as one continuous shot.
   Transitions carry no information: cut, and spend the time on evidence.
4. **Imperfect on purpose.** Paper grain, halftone dots, a marker stroke, hand-drawn circles. A polished, glossy
   finish reads as an ad.
5. **Key words and numbers on screen, never the sentence being said.** The typewriter closer is the one exception.
6. **Accuracy is part of the look.** Every number on screen is said or sourced (a `credit` line shows the source);
   a newspaper never puts words in a real outlet's mouth.

## The look (measured on the reference, 1080p)

| Part | Value |
|---|---|
| Paper | #D9D7D1 warm grey, a light grid every ~106 px (lines about 2 px, #FAF8F2 at 62%), printed grain (luma spread about 7.5 levels), a soft vignette |
| Accent | #FF8900 orange: the progress bar (38 px along the bottom), the chart line, tag icons, call-outs |
| Marker | #E04329 red-orange: the stroke behind halftone people (offset up and to the left), key words in bubbles, scribbles |
| Highlighter | #F4B41A amber, swept left to right behind marked words as they are said |
| Cards | #F9F5ED cream chart card, radius 24 px, soft shadow |
| Type | Montserrat 900 for numbers and headlines, Inter 700 to 800 for labels and charts, Merriweather for the newspaper, Bangers for bubbles, Special Elite for the typewriter; Anek Bangla and Hind Siliguri for Bangla |
| People | black and white halftone cut-outs with the offset marker stroke and a soft baked shadow |
| Objects and places | colour cut-outs; a foreground band (a building, a desk, a gate) hides the people's lower halves |

## Making the pictures (all local, nothing generated unless you choose to)

1. Find them: `nvc.py stock JOB "oil tanker ship" --type photo`, look at the sheet, `--pick ID --id tanker`.
   Portraits and objects with a clear subject cut out best. Stock people never go in political, health, dating,
   drug or adult contexts (Pixabay has no model releases), and no visible logos.
2. Cut them out: `nvc.py cutout JOB tanker capitol man1`. People become halftone with the marker stroke, anything
   else keeps its colour (`--style halftone|bw|color`, `--stroke none`). Apple Vision lifts the subject on this Mac;
   a soft shadow is baked in so the render stays fast. A stock picture's licence travels with its cut-out.
3. Clips shot on black (fire, smoke, sparks, light) or a green screen: `nvc.py key JOB fire --start 2 --seconds 8`.
   The result is a transparent WebM that lies over the paper as it is (a screen blend washes out on light paper).
   A clip that should fill a band (the sea under a ship) needs no key: use it as a `clip` with `slot: floor` and a
   feathered top.
4. A picture nothing in stock shows (a map with the client's route, an isometric object): make it with
   codex-imagegen on a plain background, then `cutout`. Never an AI picture of a real, identifiable person.

## Planning (the brief does most of it)

`nvc.py brief JOB --style vox` adds the look, the rules, the job's cut-outs and keyed clips, the element kinds and a
storyboard: the narration grouped into beats of 3 to 9 s with their word ids. For each beat decide the anchor
picture, what follows on which words, and the facts for any number. Then write one `vox` overlay per beat
(`plan.md`, Vox beats). Typical beats:

| The line says | The beat |
|---|---|
| who and where ("The US and Iran are signing a deal") | a colour foreground band (`layer: fore`, stage) with halftone people rising behind it (`stage-left`, `stage-right`), one on each name |
| a claim from the press | a `newspaper` with a made-up masthead, the key words `marks`ed as they are said |
| a price or a quantity ("oil at $116 a barrel") | the thing itself (a ship on a `floor` clip of sea, drifting) and a `tag` that counts from a start value and lands on the spoken number, riding on it with `follow` |
| a trend | a `chart` card that draws while the trend is described, a `callout` on the point that is named; later `moves` shrink it aside for the next picture |
| a big number | a `headline` with `count` that lands on the number's word, next to the object it measures |
| a comparison | two cut-outs or labels on `left` and `right`, a `scribble` circle or underline on the one that wins |
| a conversation or a stance | halftone people with `bubble`s, key words in the marker colour |
| the closing line | a `typewriter` that types the line as it is said, and one image that sums it up (a bill burning with a keyed fire clip) |

Pacing: a new beat every 3 to 9 s, something new inside a beat every 2 to 4 s (the compiler warns after 5 s).
Most beats end on a cut; `exit: drop|fade|slide|pop` plays the old pictures out under the new beat, and `leak`
washes warm light over the last cut (out to a camera, or at the end).

## Motion and sound (defaults, all tunable)

- Entrances ease out, no cartoon bounce: `rise` (from under the frame for grounded pictures), `pop` (about 6%
  overshoot), `slideLeft`/`slideRight`, `wipe` for headlines, `fade` for labels. Pictures float a few pixels once
  landed, and each beat pushes in about 3.5% with a little parallax (nearer layers move more).
- A bare word id lands the entrance 2 to 4 frames before the word (rise starts 13 frames early, pop 8); a counter
  lands 2 frames before its number; a highlight sweep starts 4 frames before its word; moves start 12 frames early.
- An element leaving mid-beat slides off by its nearest side edge; at a cut everything leaves with the beat.
- `step: 2` on a beat (or `voxStep` in the theme) draws the graphics "on twos", like hand animation; clips keep
  their own time.
- Sound: soft effects only on the main motion (a flick for a rise, a pop, a ding when a counter lands, a key per
  typed word, a swipe for a highlight), a few dB under nexa-sound's own levels. Music low under the voice; change
  it at topic turns.

## Checks the compiler makes

Every time is a real word in the beat; every shown number said or sourced (chart values ask for facts); text inside
the safe area (a label or a following tag is moved in, and the move is recorded); no two texts on top of each other;
enough time to read each text; no full spoken sentence on screen except the typewriter; nothing static for more than
5 s inside a beat; at most 7 things on screen; every newspaper and every chart goes to the review list.

## What still needs a person

- Choosing the anchor picture when stock has nothing close enough: look at the sheet before picking.
- The facts: the compiler asks for sources, it cannot check them. Put the source on screen with a `credit`.
- Maps drawn from real geography (country shapes, routes) are not built in yet; use a picture of the map as a
  cut-out (research 03 lists the d3-geo + Natural Earth route when it is needed).
