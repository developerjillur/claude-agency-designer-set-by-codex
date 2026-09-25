# Easing curves and springs

## Named curves (`curves` in the kit's core)

| Name | cubic-bezier | Role |
|---|---|---|
| `out` | 0.16, 1, 0.3, 1 | the default arrival (expo-like), the Remotion Elements' most used entrance |
| `outCubic` | 0.33, 1, 0.68, 1 | arrivals over short distances (under about 60 px), where `out` would freeze at the end |
| `outQuart` | 0.25, 1, 0.5, 1 | calm premium arrivals |
| `outQuint` | 0.22, 1, 0.36, 1 | long confident arrivals |
| `outBack` | 0.34, 1.56, 0.64, 1 | pops with about 10% overshoot: badges, dots, stickers |
| `decelerate` | 0, 0, 0, 1 | Material standard decelerate |
| `emphasized` | 0.05, 0.7, 0.1, 1 | Material emphasized decelerate: hero arrivals |
| `in` | 0.7, 0, 0.84, 0 | departures |
| `inCubic` | 0.32, 0, 0.67, 0 | gentler departures |
| `accelerate` | 0.3, 0, 0.8, 0.15 | Material emphasized accelerate |
| `anticipate` | 0.36, 0, 0.66, -0.56 | pulls back before it goes |
| `inOut` | 0.65, 0, 0.35, 1 | moves on screen, wipes, panel moves |
| `inOutQuart` | 0.76, 0, 0.24, 1 | decisive moves |
| `inOutExpo` | 0.87, 0, 0.13, 1 | whips and snaps between positions |
| `standard` | 0.2, 0, 0, 1 | Material standard (UI-like) |
| `sine` | 0.37, 0, 0.63, 1 | camera drifts, push-ins, breathing |
| `snap` | 0.2, 0.9, 0.1, 1 | quick settle, kinetic type, brutalist cuts |
| `linear` | | clocks: typewriters, tickers, rotations, progress bars tied to time |

Material durations for reference: short 50 to 200 ms, medium 250 to 400, long 450 to 600, extra long 700 to 1000
(frames at 30 fps = ms x 0.03).

## Named springs (`springs` in the kit's core), measured at 30 fps

| Name | damping, stiffness, mass | Settles in | Overshoot | Half-way at | Use |
|---|---|---|---|---|---|
| `calm` | 200, 100, 1 | 23 frames | 0% | frame 6 | the safe default |
| `smooth` | `appleSpring(0.5, 0)` = 25.1, 158, 1 | 18 | 0% | 5 | brisk without bounce |
| `settle` | 18, 140, 1 | 19 | 2.5% | 4 | a hint of life on landing |
| `snappy` | 20, 200, 1 | 15 | 4.2% | 4 | UI, kinetic type |
| `pop` | 12, 180, 1 | 27 | 20.7% | 3 | one hero per act |
| `bouncy` | 9, 150, 0.7 | 25 | 21.5% | 3 | playful styles |
| `heavy` | 22, 90, 2 | 32 | 1.1% | 7 | big, weighty objects |
| Remotion's default | 10, 100, 1 | 28 | 16.3% | 4 | never by accident: always pass a config |

Facts measured in the solver (4.0.528):
- **Damping above critical changes nothing.** Remotion treats any spring with a damping ratio of 1 or more (ratio =
  damping / (2 * sqrt(stiffness * mass))) as critically damped: `{damping: 20}` with the default stiffness 100 and
  `{damping: 200}` or `{damping: 2000}` all give the same 23-frame curve at 30 fps. Only `stiffness`, `mass` or
  `durationInFrames` change the speed of a no-bounce spring.
- Springs play about 1.56 times slower at 10 fps (each solver step is capped at 64 ms); keep springs at 24 fps and up.
- `Easing.ease` is CSS **ease-in** (0.42, 0, 1, 1), not CSS `ease`; use a named curve instead.

`springAt(frame, fps, {delay, config: 'settle'})` uses them. `measureSpring({fps, config})` gives the settle length
of any config, for sizing a Sequence to a spring.

## The Apple model: duration and bounce

`appleSpring(duration, bounce)`: `duration` is the perceived length in seconds; `bounce` 0 is critically damped (no
overshoot), about 0.15 subtle, 0.3 playful, above 0.4 exaggerated; negative values are over-damped. With mass 1:
stiffness = (2 pi / duration)^2; damping = (1 - bounce) 4 pi / duration (bounce >= 0) or 4 pi / (duration (1 +
bounce)). Remotion's spring solver works in seconds, so the numbers carry over exactly.

## Springs as curves

- `Easing.spring({damping, mass, stiffness, overshootClamping, allowTail, durationRestThreshold})` (4.0.476; the last
  two 4.0.483) turns a spring into an easing curve for `interpolate`, measured as if it lasted 30 frames and stretched
  to the segment. `allowTail: true` lets the tail keep settling into the next segment.
- The kit's `springEase('settle')` wraps it with a named config.
- The Remotion team's own default keyframe easing in recent videos is
  `Easing.spring({damping: 200, allowTail: true, durationRestThreshold: 0.02})`: a calm settle whose last 2% flows into
  the next segment.
- `spring({durationInFrames: n})` stretches a spring to exactly n frames; `delay` starts it later; `reverse` plays it
  backwards; values can be added and subtracted (enter minus exit).
- In transitions, `springTiming({config})` uses a rest threshold of 0.005 by default, which snaps visibly at the end;
  pass `durationRestThreshold: 0.001`.

## interpolate options that change the feel

- `easing` per segment (4.0.462): `[inCurve, Easing.linear, outCurve]` for enter, hold, exit in one call.
- `posterize: n` (4.0.470): hold each value n frames: stop-motion, boiling lines (`posterize: 4` on a line seed),
  textures (`posterize: 30`).
- `output: 'perceptual-scale'` (4.0.490): scale changes look even (area grows linearly); use it on scale keyframes.
- Clamp both ends. `extrapolateRight: 'extend'` only for values that must keep going (a rotation, a phase).

## Choosing

| The thing | Curve or spring |
|---|---|
| Text arriving | `out` over 15 to 20 frames (`outCubic` for small travel) |
| A card or photo arriving | `out` or `settle` spring |
| A badge or a number landing | `outBack` or `pop` (one hero) |
| Something leaving | `in` over 12 to 18 frames |
| A panel sliding across, a wipe | `inOut` over 20 to 35 frames |
| The camera | `inOut` or `sine`, 14 to 24 frames per move; `sine` for slow drifts |
| A whip between states | `inOutExpo` over 8 to 12 frames, with motion blur |
| A typewriter, a ticker, a clock | `linear` |
| Luxury, keynote | `outQuart` with long durations (24 to 36) and blur-in |
| Playful, kids, consumer apps | `outBack` and `bouncy` |
