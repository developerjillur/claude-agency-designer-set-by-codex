# The pointer and the finger

A system cursor recorded from a screen is 16 to 32 px, moves in straight jerks and disappears on a phone screen.
In a product video the pointer is a stage prop: bigger, shaded, moving like a hand, and every click it makes is an
event the rest of the scene reacts to. This file covers the kit's `Cursor`, its timeline, touches, sound, and how to
build a pointer in raw Remotion when the kit is not available.

## 1. The drawing

- Size: 44 x 54 px at 1080 (`size={1}`). Go to 1.2 for 4K masters shown small, never under 0.9.
- Look: white fill, a 1.6 px near-black outline, a real drop shadow (about 2.5 px down, 3.5 px blur, 32% black).
  It reads on white pages, dark apps and footage alike. One design for the whole film.
- Shapes: `arrow` (default), `hand` (pointing finger, over anything clickable), `grab` (closed hand while
  dragging), `text` (I-beam over fields). The hotspot is the tip of the arrow, the tip of the index finger, the
  palm of the closed hand, the middle of the I-beam; the kit positions the drawing so the hotspot lands on `(x, y)`.

## 2. The plan: `CursorKey` and `cursorTimeline`

```ts
type CursorKey = {x: number; y: number; at: number; click?: boolean | number; double?: boolean;
  drag?: boolean; shape?: 'arrow' | 'hand' | 'grab' | 'text'; duration?: number; arc?: number};
```

Rules the timeline applies (numbers at 30 fps, scaled for other rates):

| Moment | Rule |
|---|---|
| appear | at the first key's `at`, fading in over 6 frames at that key's position |
| arrive | a key's `at` is the frame the tip reaches `(x, y)` |
| press | `click: true` presses `lead` (4) frames after arriving; `click: 52` presses on frame 52 (clamped to the arrival) |
| double | a second press 5 frames after the first |
| leave | the next move may start 5 frames after the last press (the pointer never leaves while clicking) |
| drag | `drag: true` presses on arrival + lead, holds the button during the move to the next key and lets go 2 frames after arriving there; the move to the key after that waits for the release |
| move length | `duration` or `cursorMoveFrames(distance)` = 9 + 0.5 x sqrt(px), clamped to 10..30 frames at 30 fps (14 f for 100 px, 19 f for 400 px, 24 f for 900 px) |
| packed keys | if a move has no room, it starts right after the previous key and becomes short; it is never skipped |
| hide | fades out over 8 frames starting `hideAfter` (22) frames after the last event, or earlier so it is gone by the Sequence's last frame |

`cursorTimeline(keys, fps, lead?)` returns:

- `clicks`: every press frame in time order (sound and control presses go here),
- `releases`: drag drops, `start`, `end`,
- `pressOf(i)`, `arriveOf(i)`: for the key at index `i` of the list you gave.

Keep the keys in time order; indexes refer to your list. Keep the keys in a module constant so the same array feeds
both the `Cursor` and the timeline (the Cursor memoises on the array's identity).

## 3. How it moves (`cursorPose`)

For a move from A to B over T frames:

1. **Pull-back.** During the first 3 frames the pointer eases back by `min(8 px, 5% of the distance)` against the
   direction of travel (half a sine), and the forward travel starts half-way through that, so the anticipation is
   visible but tiny.
2. **Two curves.** x follows `bezier(0.5, 0, 0.18, 1)` and y follows `bezier(0.38, 0, 0.24, 1)`: a quick start and a
   long settle, with y leading slightly, like a wrist.
3. **Bow.** A sideways offset of `min(arc x distance, 80 px) x sin(pi x progress)` perpendicular to the straight line,
   always sagging downwards (or to the right on vertical moves). `arc: 0` gives a straight line.
4. **Shape.** The arrow travels; 3 frames before arriving it switches to the target key's shape (hand where it
   clicks), as a real pointer does over a link. During a drag it is the closed hand.
5. **Press.** Scale to 0.86 about the hotspot over 2 frames (ease in), hold 1 frame, back over 9 frames with a small
   overshoot (`outBack`), so the pointer springs past its size before settling.
6. **Bloom.** A soft accent glow (radial, about 60 px across) grows over 4 frames from the arrival, stays through the
   press and fades 10 frames after; it leads the press by the lead time, which reads as hover.
7. **Ring.** At the press a thin ring (white with a dark hairline) grows from 12 to 42 px and fades over 14 frames.

`cursorPose(tl, frame, fps)` returns `{x, y, shape, press, bloom, ripples, moving}` at any frame. Use it to attach
things to the pointer: a dragged card follows `pose - grabOffset` between the drag press and release, then snaps to
its drop slot (see `DemoUiCursor` in `kit/src/demos/ui.tsx`).

## 4. Targets without guessing

The classic failure: a click that lands 20 px beside the button because its position was estimated from padding.
Rules:

- Put every control that will be clicked, typed into or dragged at an absolute position from a named constant, and
  compute the key from it: `{x: SAVE.x + SAVE.w / 2, y: SAVE.y + SAVE.h / 2}`. Everything else may use flex.
- The keys are px at 1080 in the box the Cursor sits in. Put the Cursor as the last child of that box (the page inside
  a `BrowserWindow`, the screen inside a `PhoneFrame`, or the whole frame). Then any camera, scale or scroll applied to
  the box moves the pointer with the content.
- If the content scrolls (`ScrollView`), subtract the scroll offset that holds at the click frame.
- Author with `<Cursor debug>`: a red cross, the key index, its arrival and its press frame are drawn at every key.
  Render a still at each press frame and look. Turn `debug` off for delivery.
- To prove the path shape, render every second frame of a move and darken-blend them into one image: you should see a
  small backward step, a bowed line with growing spacing, then tight spacing into the target.

## 5. Making the interface answer

- `UiButton pressAt={tl.pressOf(i)} hoverAt={tl.arriveOf(i)}` depresses 6% on the press frame and lifts 2 px on
  hover; `doneLabel` rolls the label to a new state 1 frame after the press.
- `Toggle at={tl.pressOf(i)}` flips on the press frame; `Pressable at=...` works around anything; its function child
  receives `{press, after, count, since, hover}` to swap content (`after` is true from the press on).
- A menu, dialog or page change should start 6 to 10 frames after the press, not on it: the viewer needs to see the
  press land first.
- Locking a click to a word of the voice: give that key `click: wordFrame` and put its arrival 4 or more frames before;
  the move starts `cursorMoveFrames` earlier on its own.

## 6. Touch (`TapIndicator`)

For phones and tablets the pointer is replaced by a finger dot:

- 60 to 80 px at 1080 (`size`), a translucent grey fill with a white rim and a soft shadow, visible on light and dark
  screens.
- A tap: the dot appears 3 frames before `at` shrinking from 1.35 to 1 (the finger lands), holds `hold` frames (5),
  then grows to 1.55 and fades over 10 frames (the finger lifts). Press the control on `at`.
- A long press (`long: true`): holds 24 frames while a ring around the dot fills; start the long-press action when the
  ring closes.
- A swipe: `{from, to, at, frames}`; the dot lands, travels with ease in-out (14 frames default) with three fading
  ghosts behind it, and lifts. Drive the content with a `ScrollView` whose keys match: scroll from `at` to
  `at + frames` by the same distance (`to - from` in y) in the opposite direction.
- Taps are frame numbers you choose; reuse the same numbers for `Pressable`, screen transitions and sounds
  (`<ClickSounds frames={Object.values(TAPS)} src={staticFile('ui/tap.wav')} />`).

## 7. Sound

- `ClickSounds` places `<Audio>` (from `@remotion/media`) in a `<Sequence>` at each frame, `length` frames long.
- The kit's `public/ui/click.wav` (a short filtered transient with a low thump, 60 ms, peak -3 dBFS) and
  `public/ui/tap.wav` (softer, 70 ms) were made with ffmpeg, so there is no licence question. Copy `kit/public/ui` into
  the project's `public/ui`: `nrk.py new` does not copy the kit's public folder.
- Measured on 4.0.528 (MP4, AAC 48 kHz): a click placed on frame 54 decodes at 1.843 s instead of 1.800 s, a constant
  +1.3 frames of AAC priming. Within a frame is in sync to the eye; pass `offset={1}` for frame-exact.
- Levels: UI sounds 10 to 20 dB under the voice (`volume` 0.3 to 0.6 with the kit files). One sound per event; never
  more than about 3 clicks a second; alternate two samples or step volumes down when clicks come in quick runs.
- `@remotion/sfx` exports hosted URLs; only `mouseClick`, `uiSwitch`, `whoosh`, `whip`, `pageTurn`, `shutterModern`
  and `shutterOld` are CC0. For client work copy the file into `public/` and use `staticFile()`, so renders do not
  depend on the network.

## 8. A pointer in raw Remotion

When the kit is not in the project, the same ideas in a few lines:

```tsx
const f = useCurrentFrame();
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const t0 = 40, t1 = 62, press = 66; // move 40..62, click on 66
const px = interpolate(f, [t0, t1], [0, 1], {...clamp, easing: Easing.bezier(0.5, 0, 0.18, 1)});
const py = interpolate(f, [t0, t1], [0, 1], {...clamp, easing: Easing.bezier(0.38, 0, 0.24, 1)});
const bow = 60 * Math.sin(Math.PI * px); // sideways sag in px
const x = A.x + (B.x - A.x) * px, y = A.y + (B.y - A.y) * py + bow;
const s = interpolate(f, [press - 2, press, press + 1, press + 10], [1, 0.86, 0.86, 1],
  {...clamp, easing: [Easing.in(Easing.cubic), Easing.linear, Easing.bezier(0.34, 1.56, 0.64, 1)]});
// an SVG arrow whose tip is at (4, 2) of a 44 x 54 box:
<svg width={44} height={54} viewBox="0 0 44 54" style={{position: 'absolute', left: x - 4, top: y - 2, scale: `${s}`,
  transformOrigin: '4px 2px', filter: 'drop-shadow(0 2.5px 3.5px rgba(0,0,0,.32))'}}>
  <path d="M4 2 L4 44.6 L14.1 35 L21.4 51.8 L28.6 48.8 L21.5 32.6 L35.4 32.2 Z" fill="#fff" stroke="#111317" strokeWidth={1.6} strokeLinejoin="round" />
</svg>
```

(The bow above is always downward; for moves in other directions offset along the perpendicular of the move.)

`@remotion/mac-cursors` (4.0.513+) ships 39 macOS cursor drawings with the hotspot at the component's origin:
`<MacOSCursor cursor="pointer" style={{left: x, top: y, scale: 1.5}} />` (`cursor` takes CSS cursor keywords, `'none'`
draws nothing, `'custom'` uses `customCursor`). It is not in the shared node_modules on this machine; add it with
`npx remotion add @remotion/mac-cursors` in a project that needs the system look. It still needs your own path, press
and ripple.

## 9. Faults and fixes

| Fault | Cause | Fix |
|---|---|---|
| Pointer behind a dialog | rendered before it | make the Cursor the last child (it has `zIndex: 40` inside its box) |
| Pointer does not follow the camera or the scroll | it sits outside the moved box | move it inside the same box as the controls |
| Click lands beside the button | target estimated | absolute layout constants, `debug`, a still at the press frame |
| Pointer starts leaving while clicking | no hold after the press | the kit enforces 5 frames; with raw code add a hold key |
| It teleports | two keys on the same frame or out of order | keep keys in time order with room for the move |
| Visible after the scene | `hideAfter={Infinity}` in a short Sequence | keep the default, or end the Sequence after it fades |
| Tiny at 4K | px values multiplied by `unit` twice | pass px at 1080; the kit multiplies once |
| Rings everywhere | a ring on every hover | rings only on presses; `ripple={false}` for calm films |
