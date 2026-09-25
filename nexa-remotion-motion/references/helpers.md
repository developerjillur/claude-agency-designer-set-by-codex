# Kit helpers: core and motion

## core

| Helper | Signature | Notes |
|---|---|---|
| `useStage()` | `() => {width, height, fps, durationInFrames, unit, safe, vertical, aspect, sec(s), u(px)}` | `unit` = short side / 1080; `safe` is the platform safe area |
| `Stage` | `<Stage format="shorts" or safe={{x, y, w, h}}>` | names the target when the size alone is ambiguous |
| `SafeArea` | `<SafeArea justify align gap row style>` | a flex column exactly on the safe area |
| `SafeGuides` | `<SafeGuides />` | authoring overlay; leave out of deliveries |
| `FORMATS`, `safeAreaFor` | `safeAreaFor(width, height, format?)` | the same numbers as nrk.py |
| `ThemeProvider`, `useTheme`, `makeTheme`, `THEMES`, `THEME_NAMES` | `makeTheme('studio', {colors: {...}, fonts: {...}})` | 20 themes; `t.type.*` are resolved font stacks |
| `loadKitFont`, `fontStack`, `FONTS` | `fontStack('Manrope', [800], 'AnekBangla')` | 45 families with their real weights; returns the CSS family |
| `curves`, `springs`, `appleSpring`, `springEase` | see `easing-and-springs.md` | |
| `clamp`, `lerp`, `invLerp`, `remap` | numbers | |
| `rand`, `randBetween`, `shuffle` | seeded | the same in every tab |
| `toFrames`, `at30` | `at30(18, 60) = 36` | theme timings are written for 30 fps |
| `beatGrid`, `snapToBeat` | `beatGrid(bpm, fps, total, offsetSeconds)` | for rhythmic music only |
| `readingFrames` | `readingFrames(text, fps)` | how long text must hold |

## motion

| Helper | Signature | Notes |
|---|---|---|
| `ramp` | `ramp(frame, start, duration, ease = curves.out)` | 0 to 1, clamped |
| `track` | `track(frame, frames[], values[], ease or ease[])` | keyframes, clamped; repeat a value to hold |
| `inHoldOut` | `inHoldOut(frame, start, inFrames, end, outFrames, easeIn, easeOut)` | 0 to 1 to 0 |
| `springAt` | `springAt(frame, fps, {delay, config, durationInFrames, from, to})` | named or custom config |
| `stagger` | `stagger(index, each, start)` | a start frame |
| `onTwos` | `onTwos(frame, step = 2)` | stepped time |
| `loop`, `pingPong` | `loop(frame, period)`, `pingPong(frame, period)` | cycles |
| `pulse` | `pulse(frame, start, duration)` | half a sine, 0 outside: one emphasis |
| `wiggle` | `wiggle(frame, fps, freq = 0.5, lane = 0, seed = 'kit')` | about -1 to 1; one seed, many lanes |
| `inertia` | `inertia(frame, from, fps, amp, freq, decay)` | a damped settle after an impact |
| `moveFrames` | `moveFrames(distance, baseDistance = 200, baseFrames = 16)` | longer moves take longer |
| `frameAtProgress` | `frameAtProgress(target, start, duration, ease)` | the (fractional) frame an eased move reaches `target`: time labels to a drawing line |
| `useLife` | `useLife(inFrames, outFrames, easeIn, easeOut)` | `{enter, exit, visible}` of the enclosing Sequence |
| `Animate`, `Stagger`, `Camera`, `Parallax`, `useCamera`, `ZoomAt`, `PushIn`, `Shake`, `Float`, `MotionBlur`, `Trail` | components | see SKILL.md |
