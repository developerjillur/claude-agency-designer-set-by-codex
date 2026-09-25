# Choreography: what moves, when, and for how long

## Voice first, then cues

1. The voice-over (or the music) sets the clock. Scene length = measured speech + 0.2 to 0.5 s tail (+ transition
   overlap).
2. Cue the meaning: the verb or the emphasis word. Readable elements land 1 or 2 frames before their word; hits
   (a stamp, a count landing, a flash) land exactly on it.
3. One beat carries at most two cues. Put reveals in the back half of a shot; the first half establishes.
4. Keep the cue table as constants at the top of the scene; time everything from it.

## Staging

- One focal element per moment; it wins on at least two of size, contrast, position and weight.
- What has paid off steps back: dim it (opacity 0.55) or blur it (2 to 3 px), or move it aside with a `moves` key.
- Hierarchy of attention: motion first, then size, contrast, saturation, position. A moving thing always wins, so
  move only what should be looked at.
- At most one or two things moving or being read at once.

## Reading time and holds

- `readingFrames(text, fps)`: about 0.33 s a word plus 0.3 s, never under 1.2 s, longer for numbers.
- After an element settles, hold 30 to 45 frames before it leaves (1.5 s for multi-word lines, 1 s for a logo).
- Text holds perfectly still while it is read. Slow sub-pixel drift of text looks choppy after encoding: drift the
  camera or the ground instead.
- Dense UI or a chart needs 90 to 120 frames on screen.

## Pacing

- A new beat every 3 to 9 s; something new inside a beat every 2 to 4 s; nothing fully static for more than 3 s.
- Shot lengths regular (for example 36 or 48 frames in kinetic pieces), broken once on purpose for the line that
  matters.
- Avoid the **slideshow** (all at once, then nothing) and the **screensaver** (everything drifting forever). During a
  hold, at most the hero is alive; background drift is allowed.
- First cuts are almost always too fast: every documented revision loop asked for longer holds, never shorter.

## The Remotion team's house numbers (measured in their own videos)

- Text and UI enter over 15 to 21 frames on `bezier(0.16, 1, 0.3, 1)`.
- Staggers: 1 or 2 frames between letters (wordmarks only), 8 between primary items, 10 between list rows.
- Data grows over 34 frames, with count-ups on the same window and curve.
- At most one bouncy accent per element; exits faster than entrances.
- Beats overlap by 2 to 4 frames; in data pieces everything settles by about 55% of the video, then holds.
- Short-form scene changes are 6 to 8 frame pushes.
- Product videos: shots of 0.9 to 1.7 s with one gesture each; boring parts sped up (about 2.3x), key moments slowed
  (about 0.7x); one eased value drives the cursor, the number shown and the effect together.

## Stagger arithmetic

- The run takes `(n - 1) * each + duration` frames; keep a gesture under about 0.8 s.
- 2 to 4 frames within one gesture (words of a title, bars of a chart), 5 or 6 for countable lists, 24 to 29
  between separate beats.
- Order: reading order by default; `center` for symmetric groups; `random` (seeded) only for scattered objects.
- Four or more items that must land before a cue: shrink the step or split the list across two cues.
- Exits usually leave together (or not at all); a reverse stagger (`outEach`) for lists that clear the stage.

## Titles

- Per word or per line behind a mask (`in="mask"`): per letter only for a 4 or 5 glyph wordmark. Letter staggers
  destroy kerning and take too long (a 16-letter title at 2 frames each needs 30 frames before the last letter
  moves; three words at 3 frames land by frame 24).
- A mask means no fade on top (the fade defeats the mask).
- Kinetic paragraphs: each line enters on its word (about 0.3 s, 28 px rise); spent lines drop to 0.3 opacity and
  the stack nudges up about 10 px per arrival.

## The camera

- Build a world 2 to 2.5 times the frame; drive focus x, y and zoom from one keyframe table (`<Camera keys>`).
- Moves 14 to 24 frames with `inOut`; repeat a key to hold; end on two near-identical keys so an editor can cut
  anywhere; about three moves per chapter.
- Two nodes for complex rigs: an outer one for the dolly (scale), an inner one for the turn; never two tweens on one
  transform.
- Put the zoom origin exactly on what matters (a clicked button stays put while the frame zooms around it).
- Never keep a lasting transform on a container that holds a whole UI with small text (it resamples every glyph);
  move what is inside instead, or accept the softness.
- Before scaling, compute where the bottom lands: `bottom_after = bottom + (bottom - origin_y) * (scale - 1)`.
- Motion blur on fast travel only (`<MotionBlur>` or `<Trail>`).

## Parallax

Layers at depths: under 1 is farther (moves slower), over 1 nearer (moves faster). Three layers are plenty: a far
texture (0.3 to 0.6), the subject plane (1), a near foreground band (1.2 to 1.5) that hides the lower edge of cut-out
people or objects. Parallax moves are small: a few percent of the frame per move.

## Continuous life (without a screensaver)

- `PushIn` of 2 to 4% over a held shot, with an 18 px lift at most.
- `Float` on pictures: 4 to 10 px at 0.3 to 0.6 Hz, only on things that are not being read.
- A bounded pulse (`pulse(frame, start, 6)`) for a single emphasis, instead of an endless heartbeat.
- Envelope any idle motion that runs into a cut so the cut does not chop it mid-swing.

## Beat sync

Only when the music is rhythmic (measure it: a click track, a drum loop). Cuts on downbeats; small events snapped to
the nearest beat within about 6 frames (`snapToBeat(frame, beatGrid(bpm, fps, total, offset))`); at most three
whole-frame hits (a flash, a punch-in) per film. The size of motion does not follow the beat.

## Animation principles in Remotion terms

| Principle | In code |
|---|---|
| Timing | frames from fps; farther or bigger moves get more frames (square root of the distance ratio) |
| Slow in and out | the curve by role; linear only for clocks |
| Anticipation | a 2 or 3 frame counter-move (8 px back, a 0.95 dip) before a committed move |
| Follow-through | attached parts settle 2 to 4 frames after the body (shadow, label, badge) |
| Arcs | different curves or durations on x and y, or a path (`getPointAtLength`) |
| Secondary action | one supporting reaction per hit (a clicked control depresses) |
| Squash and stretch | 1.06 x 0.95 for 2 or 3 frames on impact, playful styles only |
| Staging | one focal element; the rest dims or blurs |
| Exaggeration | only on the hero beat and the signature move |
| Straight ahead or pose to pose | keyframe tables (pose to pose); seeded simulations computed from the frame (straight ahead) |

## After Effects expressions in Remotion

| After Effects | Remotion |
|---|---|
| `wiggle(f, a)` | `wiggle(frame, fps, f, lane) * a` (the kit) or `noise2D(seed, frame / fps * f, lane) * a` |
| `seedRandom(i, true); random()` | `random('seed-' + i)` |
| `loopOut('cycle')`, `'pingpong'` | `loop(frame, period)`, `pingPong(frame, period)` |
| inertial bounce after the last key | `inertia(frame, landedAt, fps, amp, freq, decay)` or a spring with bounce |
| `valueAtTime(time - delay)` | call the same function with `frame - delay * fps` |
| `time * 90` | `frame / fps * 90` |
| time remap | `<Sequence playbackRate>`, `trimBefore`, `freeze` |
| a null with sliders | component props (and a Zod schema for Studio controls) |
| essential properties of a template | `defaultProps` plus `schema`; `calculateMetadata` for data-driven length |
