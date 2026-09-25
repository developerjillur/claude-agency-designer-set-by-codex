# Chat and notifications

Messages and alerts are small events with a big narrative load: someone replies, a payment lands, a build passes.
They must arrive at a readable pace, one at a time, in the product's own look. This file covers `ChatThread`,
`TypingDots`, `Notification` and `NotificationStack`, their timing, and raw recipes.

## 1. Chat anatomy (px at 1080, `fontSize` = 30)

| Part | Value |
|---|---|
| bubble | padding 0.42em x 0.66em, corner radius 0.8em, max width 82% of the thread, line height 1.34 |
| runs | 18 px above the first bubble of a sender's run, 6 px between bubbles of one run |
| corners | inside a run the sender-side corners are 8 px; the last bubble of a run has a 6 px corner at its tail side |
| colours | yours: the accent with its `onAccent` text (or `meColor` with black or white picked for contrast); theirs: a 7.5% tint of the text colour on light, a lighter panel on dark (`themColor` to override) |
| group chats | the sender's name (62% size, muted) above their first bubble, an initials avatar (36 px) beside their last |
| header | 96 px: back chevron, avatar, name, status that reads "typing..." while dots show |
| composer | 100 px: plus, a pill input ("Message"), a send button that lights when there is a draft |
| edge | older messages fade under a 60 px mask at the top of the thread |

Sizes that stay readable: 24 px inside a 440 px phone in a 16:9 video, 30 px in a 720 px panel, 36 px full width in
9:16.

## 2. Timing

`chatTimeline(messages, fps, startAt, composer, cps)` decides when each message lands:

- A message with `at` lands on that frame. Negative `at` puts history on screen from frame 0 (a lived-in thread is a
  better poster than an empty one).
- Without `at`, it lands a reading beat after the previous one: 10 frames plus half of `readingFrames(previous text)`.
- A message from the other side shows typing dots for `typing` frames first (26 at 30 fps; `false` for none). Their
  landing frame is the `at` you give; the dots start before it.
- With `composer`, your message is typed into the input at `cps` (20) and sent 8 frames after the last character:
  its landing frame is the send, and typing starts before it.
- Word-locked chat: set `at` of each message to the word that introduces it; keep at least `readingFrames(text)` before
  the next one.

Motion (30 fps): the row grows to its height over 8 frames (ease out) and pushes the older rows up; the bubble pops
from its tail corner (scale 0.72 to 1 on a settle spring) and fades in over 4 frames with a 12 px lift; dots collapse
while the message arrives; a reaction (`react: {at, icon}`, a heart or a thumb) pops onto the top corner with a pop
spring; `receipt` text appears under your last message 24 frames after it lands.

## 3. Look, not brand

Messaging apps have strong brand identities (a particular green, a particular blue, particular bubble tails). Do not
copy them for client work unless the video is about that app with permission. The kit's look is neutral and takes
the theme's accent. For a light app inside a dark video pass `mode="light"`.

## 4. Notifications

| Variant | Anatomy | Motion |
|---|---|---|
| `phone` | a banner as wide as the screen minus the insets (360 px elsewhere), radius 7.5% of its width, app tile 12% with a glyph, app name in capitals and the time, a bold title, two lines of body | drops from above on a settle spring (140 px) with scale 0.94 to 1, leaves upwards (160 px) faster |
| `desktop` | a 440 px card, round tinted icon, title and time, body, optional actions (first is primary), a thin timer line at the bottom that runs down until the card leaves | slides in from its side on a settle spring, slides out the same way |
| `pill` | a 64 px pill, a round check in the positive colour, one short line | rises 26 px and pops (0.9 to 1), falls away 14 px |

Placement: `place` is `top`, `top-right`, `top-left`, `bottom`, `bottom-right`, `bottom-left` or `inline`; `area` is
`'parent'` (inside the box it sits in: a phone screen, a window page) or `'safe'` (the frame's safe area; the default
for desktop and pill). Inside a `PhoneFrame` a top banner sits under the status bar and fits the screen on its own.
`inset` is the margin (20 px).

Timing: arrive 6 to 10 frames after the event that causes it; enter over 18 frames; stay at least
`readingFrames(title + body)`; leave over 12 frames by the end of its Sequence (`exitAt` to leave earlier). A pill that
confirms an action: 6 frames after the press, about 1.5 s on screen.

`NotificationStack items={[{at, title, ...}]}` stacks up to about three; each new card lands on top and pushes the
others down with the grid-row growth; all leave together at the end. Newest first reads naturally for both phones and
desktops.

## 5. Raw recipes

Row growth without measuring (the trick every list in the kit uses):
```tsx
const p = interpolate(frame, [land, land + 8], [0, 1], {easing: Easing.bezier(0.16, 1, 0.3, 1), extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
<div style={{display: 'grid', gridTemplateRows: `minmax(0, ${p}fr)`}}>
  <div style={{minHeight: 0, overflow: p < 0.999 ? 'hidden' : 'visible'}}>{bubble}</div>
</div>
```
A grid row of `p fr` in an auto-height container resolves to `p` times its content height, so the row reaches its
natural height without anyone measuring text (no font-loading race, no `measureText` cache trap).

Typing dots: three dots, each lifted by `max(0, sin(2 pi (t - i x 0.16)))` with `t = frame / (0.9 s x fps)`: a
wave that runs through the dots about once a second.

A queue of toasts with explicit exits: give each its own `<Sequence from={at} durationInFrames={life}>` and a
`Notification place="inline"` inside a column; the Sequence end is its exit.

## 6. Faults and fixes

| Fault | Cause | Fix |
|---|---|---|
| The thread looks empty at the start | no history | two or three messages with negative `at` |
| Messages arrive faster than they can be read | fixed short gaps | leave `at` empty (reading beats) or space by `readingFrames` |
| A reaction covers the first letters | placed inside the bubble | the kit puts it outside the corner; keep custom ones out too |
| A banner sits on the clock | positioned from the screen top | inside `PhoneFrame` the kit offsets it; elsewhere pass `style={{top}}` |
| Emoji in messages render as boxes on a server | no colour emoji font | draw reactions and icons (`UiIcon`) instead |
| Five toasts at once | every event notifies | at most three on screen; merge or drop the rest |
