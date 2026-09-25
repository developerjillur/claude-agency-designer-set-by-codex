# Scenes and components

All scenes are 1920x1080 at 30 fps (30 frames = one second). Each is its own composition in the Studio sidebar, so
it can be checked alone; `BrollDemo` (10 s), `Part2` (50 s) and `BrollMinute` (60 s) put them in order.

## Scenes

| File | Composition | Frames | What it shows | Words from `copy.ts` |
|---|---|---|---|---|
| `scenes/SplitScreenScene.tsx` | `SplitScreen` | 70 | guitarist (left) and runner (right), a hand-drawn orange divider that grows and boils, label chips | `split.left`, `split.right` |
| `scenes/CreatorScene.tsx` | `Creator` | 66 | the creator cutout with camera and tripod, viewfinder corners, blinking REC and a running timecode, engagement icons flying out of the lens, a camera push-in | `creator.rec` |
| `scenes/TimelineScene.tsx` | `Timeline` | 58 | an editing timeline built from divs: clips grow in, waveforms rise, the playhead scrubs across | none (timecodes are computed) |
| `scenes/StatScene.tsx` | `StatCard` | 64 | growth card: title, a counter to the final value, the curve drawn from `GROWTH`, axis labels, legend, the formula | `stat.*`, `GROWTH` |
| `scenes/CaptionScene.tsx` | `Caption` | 60 | kinetic caption: words rise one by one, key words get a hand-drawn underline | `caption.first`, `caption.firstKey` |
| `scenes2/ContinueCaption.tsx` | in `Part2` | 75 | picks up the frozen first caption, lifts it and finishes the sentence | `caption.next`, `caption.nextKey` |
| `scenes2/StepCard.tsx` | in `Part2` | 60 each | numbered chapter card: the badge spins in, the title rises word by word, an accent bar grows | `steps[0..2]` |
| `scenes2/HabitScene.tsx` | `Habit` | 165 | the guitarist practising in a card while a 30-day streak fills | `habit.title` |
| `scenes2/ShareScene.tsx` | `Share` | 165 | the creator (mirrored) next to a post that uploads, then reactions fly out | `share.uploading`, `share.posted` |
| `scenes2/FeedbackScene.tsx` | `Feedback` | 165 | the edit gets tighter: a marked section is cut, the gap closes, reactions rise at the playhead | none |
| `scenes2/StatBarsScene.tsx` | `StatBars` | 180 | four bars that grow to `(1 + rate)^days` for each period | `bars.*`, `GROWTH` |
| `scenes2/PayoffSplit.tsx` | `Payoff` | 180 | the same guitarist on day 1 (alone at home) and day 365 (small stage, spotlight, crowd) | `payoff.before`, `payoff.after` |
| `scenes2/FinishLineScene.tsx` | `FinishLine` | 150 | the runner breaks the finish tape, confetti falls | `finish` |
| `scenes2/StoryCards.tsx` | `RecapCards` | 150 | the three characters as live cards on a dark board | `recap[0..2]` |
| `scenes2/EndCard.tsx` | `EndCard` | 150 | the call to action rises in, a cursor clicks Subscribe, the bell rings | `end.words`, `end.button`, `end.pressed` |

## Components

| File | What it does |
|---|---|
| `components/draw.tsx` | the drawing helpers: unit vectors from angles, and limbs drawn as an outline pass then a fill pass so joints stay seamless |
| `components/Guitarist.tsx` | the guitarist rig: fast downstroke and slower upstroke (two strums a second), head bob, foot tap, notes rising; home and stage versions |
| `components/Runner.tsx` | the runner rig: a procedural run cycle (thigh on a sine, knee folding as it passes vertical, the foot flat while it carries the weight), a moving background, the finish tape |
| `components/RoundPip.tsx` | the round presenter picture-in-picture (swap the photo for the talking-head clip in production) |
| `components/LabelChip.tsx` | a dark location-style label that pops in (`text`, `delay`, `x`, `y`, `tone`) |
| `components/AppIcons.tsx` | engagement icons (chat, heart, bell) that fly out of the camera lens and keep floating |
| `components/BarSweep.tsx` | orange and yellow bars that sweep across and hide a cut (a TransitionSeries overlay) |
| `components/MiniScene.tsx` | a 960x1080 panel (the guitar room, the running track) scaled into a card and still animating |

## Adding a scene

Copy the closest scene, give it a composition in `src/Root.tsx`, and put its words in `src/copy.ts`. Draw new
characters with `draw.tsx` the way `Guitarist.tsx` does: a hip or shoulder point, then limbs as chains of angles that
change with the frame. Check it alone in the Studio, then as stills (`broll.py stills DIR --comp YourScene`).
