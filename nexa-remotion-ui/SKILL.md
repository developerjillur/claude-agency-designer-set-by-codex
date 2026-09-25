---
name: nexa-remotion-ui
description: "Product and interface animation for Remotion 4.0.528 from the nexa-remotion kit: a lifelike pointer with bowed paths, a click stack and click frames for sound, touch indicators, buttons, toggles, search bars and form fields that press and type on cue, browser, desktop, phone and laptop frames, typed code and terminals, chat threads, phone and desktop notifications, lower thirds, title, chapter and end cards, logo reveals, a subscribe nudge, chapter bars and countdowns. Use it for SaaS and app demos, launches, tutorials, YouTube overlays and 9:16 app promos, Banglish asks included ('app demo video banao', 'cursor click animation', 'lower third lagbe', 'logo reveal koro'). Part of the nexa-remotion family."
---

# Interface animation for Remotion

Everything a product or tutorial video needs to show software working: a pointer that moves like a hand, controls
that react, device and window frames, code, terminals, chat, notifications, and the overlays and cards around them.
Part of the nexa-remotion family (the director skill is `nexa-remotion`; the kit lives in
`~/.claude/skills/nexa-remotion/kit`, and a project made with `nrk.py new` imports these parts from `./kit/ui`).
Motion timing comes from `nexa-remotion-motion`; themes and brand colours from `nexa-remotion-styles`.

## Fast path

1. **Intake.** Format (16:9 `youtube` or 9:16 `shorts`), length, voice or music, and the product's truth: real
   screens or screenshots, real button labels, real colours and logo files. Never invent the client's metrics or
   UI copy; for drafts use the kit's neutral names (Driftnote, Coinlet, Orbitly, Taskwell) and `.example` domains.
2. **Project.** `python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py new PROJECT --format youtube --seconds 20`.
   Pick the theme closest to the product (`studio`, `midnight`, `keynoteLight`, `fresh`, `corporate`...) or
   `makeTheme(base, {colors, fonts})` from the brand. Copy `kit/public/ui` into the project's `public/ui` if you
   will use the click sounds.
3. **Storyboard in frames.** Hook with the product on screen within 3 s; one focal action per beat (click, type,
   toggle, scroll); after every action a settled hold of 30 to 45 frames (dense screens 90 to 120) before the next.
   Write the beat table as constants at the top of the scene.
4. **Build the screens** as React components inside a frame (`BrowserWindow`, `MacWindow`, `PhoneFrame`,
   `LaptopFrame`) on a `UiBackdrop`. Every control that will be clicked, tapped or typed into sits at an absolute
   position from a named layout constant (`const SAVE = {x, y, w, h}`).
5. **Choreograph from one plan.** Write `CURSOR_KEYS` (or `taps`), get `const tl = cursorTimeline(KEYS, fps)`, and
   feed `tl.pressOf(i)` to the controls (`UiButton pressAt`, `Toggle at`, `Pressable at`). Typing gets its start
   frame (`FormField typeAt`, `SearchBar typeAt`, `CodeBlock startAt`). A camera punch-in (motion's `Camera`) goes
   before or after a pointer move, never during it.
6. **Overlays and ends.** `LowerThird` for people, `Notification` pills for confirmations, `ChapterBar` for
   tutorials, `EndCard` or `LogoReveal` to finish. Each one is wrapped in the `<Sequence>` of its beat so its exit
   ends on that Sequence's last frame.
7. **Sound.** `<ClickSounds frames={tl.clicks} src={staticFile('ui/click.wav')} />`, taps with `ui/tap.wav`; keep
   UI sounds 10 to 20 dB under the voice.
8. **Check.** `nrk.py stills PROJECT --comp Main --every 0.5` and read the sheet; render full-size stills at every
   press frame and every text hold (`nrk.py still PROJECT --frame N`); author with `<Cursor debug>`; then
   `nrk.py render` and `nrk.py qa`.

## Components

| Component | Use it for | Key props |
|---|---|---|
| `Cursor` | a pointer that travels, hovers, clicks, drags and leaves | `keys` [{x, y, at, click, double, drag, shape, duration, arc}], `size`, `bloom`, `ripple`, `hideAfter`, `debug` |
| `cursorTimeline`, `cursorPose` | the same plan as data: press frames, drags, the pose at any frame | `(keys, fps)`: `clicks`, `pressOf(i)`, `arriveOf(i)`; `(tl, frame, fps)` |
| `TapIndicator` | cursor-free touches for phones: tap, long press, swipe | `taps` [{x, y, at, hold, long}], `swipes` [{from, to, at, frames}] |
| `ClickSounds` | a sound on every press frame | `frames`, `src`, `volume`, `offset` |
| `Pressable` | any control that depresses 6% and springs back | `at`, `hoverAt`, `depth`, children as a function of the press state |
| `UiButton` | themed buttons that press and roll to a done state | `label`, `variant`, `size`, `icon`, `pressAt`, `doneLabel`, `width` |
| `Toggle` | a switch flipping on cue | `on`, `at`, `label` |
| `SearchBar`, `FormField` | fields that focus, type (grapheme-safe) and confirm | `text`/`value`, `typeAt`, `cps`, `suggestions`, `pick`, `kind`, `validAt` |
| `KeyCombo` | shortcut key caps | `keys` (`'cmd'`, `'shift'`, `'enter'` drawn), `at`, `pressAt` |
| `BrowserWindow` | web apps and sites | `url`, `typeUrlAt`, `tabs`, `loadAt`, `mode`; `browserChromeHeight()` |
| `MacWindow` | desktop apps | `title`, `sidebar`, `toolbar` |
| `PhoneFrame` | phone apps | `width`, `finish`, `camera`, `statusBar`, `barFill`; `phoneScreen(width)` |
| `LaptopFrame` | a laptop hero shot | `width`, `finish`; `laptopScreen(width)` |
| `DeviceRise`, `ScrollView`, `UiBackdrop` | the keynote device entrance, scrolling pages, a lit ground | `tilt`, `distance`; `keys` [{at, y}]; `variant` |
| `CodeBlock` | typed, coloured code with a walkthrough | `code`, `lang` (ts, tsx, js, jsx, py, json, bash), `typing`, `cps`, `focus` [{lines, at}] |
| `Terminal` | shell sessions with output, progress bars, spinners | `lines` [{cmd} / {out, tone} / {progress} / {spinner, done} / {gap}] |
| `ChatThread` | two-sided chats with typing dots, a composer, reactions | `messages` [{from, text, at, name, react}], `composer`, `receipt` |
| `Notification`, `NotificationStack` | phone banners, desktop toasts, status pills | `variant`, `title`, `body`, `delay`, `place`, `area`, `actions` |
| `LowerThird` | names and roles | `variant` (bar, split, minimal, card), `side`, `scrim` |
| `TitleCard`, `SectionTitle`, `EndCard` | opening, chapter and closing cards | `title`, `kicker`, `accentWord`; `index`, `total`; `cta`, `slots`, `clickAt` |
| `LogoReveal` | logo stings | `variant` (mask, stroke, scale, split, wipe), `mark`, `name`, `tagline` |
| `Subscribe`, `ChapterBar`, `Countdown` | a clicked subscribe card, tutorial progress, 3-2-1 or mm:ss | `clickAt`, `bellAt`; `chapters`; `variant`, `from`, `seconds` |
| `FocusRing`, `UiTooltip` | a guided tour: dim all but one control, explain it | `keys` [{at, x, y, w, h}]; `x`, `y`, `text`, `side` |
| `UiIcon`, `uiPalette`, `useUiTyping` | 62 drawn icons, interface colours for your own screens, the typing engine | |

Sizes and positions are px at 1080 (the kit multiplies by `unit`), frames are local to the enclosing Sequence.
The module README (`kit/src/kit/ui/README.md`) lists every prop and default.

## Craft rules

- **The pointer is a prop, not a system cursor.** 44 x 54 px at 1080; one design for the whole film. Moves take
  14 to 24 frames by distance, with a pull-back of up to 8 px first and a bow of about a tenth of the distance. It
  arrives 4 frames before it presses; the press takes 2 frames down to 0.86 and 9 frames back with a small overshoot;
  it stays at least 5 frames after the press before leaving. It fades out about 0.7 s after its last action.
- **The control answers the pointer.** Depress about 6%, then change state (label roll, colour, check) within
  7 frames. One ripple ring, thin and short; never rings on every element.
- **Taps on phones, pointers on desktops.** A finger dot 60 to 80 px, down 3 frames before the tap frame, holds 5,
  lifts over 10. Swipes with a short trail.
- **Typing speeds.** Prose 12 to 16 characters a second with jitter and beats after punctuation; commands 20 to 26;
  code 40 to 60, even, indents instantly. Budget it: characters / cps x fps, plus 10%. Caret solid while typing,
  a soft blink about once a second when idle.
- **Hold what the viewer reads.** At least `readingFrames(text, fps)`; 30 to 45 frames after each UI action;
  90 to 120 frames for a dense screen. Walkthrough highlights come after typing ends, never during.
- **One focal move at a time.** Camera punch-ins of 1.2 to 1.35x, 20 to 30 frames, ease in-out, toward the control;
  the pointer rests while the camera moves and the other way round.
- **Legible on a phone.** Anything the viewer must read: at least 24 px at 1080 in 16:9 and 32 px in 9:16;
  code 26 to 30 px; chat 24 px inside a 440 px phone, 36 px full screen in 9:16; lower-third names 46 to 56 px.
  Window chrome may stay small (16 to 20 px) because that is how software looks.
- **Safe areas.** 16:9: 5% margins. Shorts, Reels, TikTok: text and every tapped control inside (65, 270) to
  (940, 1248); a large phone may reach beyond, its key UI may not.
- **Frame 0 is a poster.** Give entrances a small negative `delay` (devices, history in a chat) so the first
  frame is composed; never open on an empty ground.
- **Temporary things leave cleanly.** Overlays enter in 18 to 22 frames and leave in 12 to 14, last in first out,
  ending on the last frame of their Sequence; nothing half-visible at a cut.
- **No vacuum, no slop.** Devices stand on a lit ground with a real shadow; one accent; icons drawn (`UiIcon`), never
  emoji; no glow on everything, no confetti endings, no brand logos you were not given.

## Recipes

**1. A click-through in a browser with a punch-in**
```tsx
const SHARE = {x: 1234, y: 50, w: 150, h: 56};
const KEYS: CursorKey[] = [{x: 1100, y: 330, at: 84}, {x: SHARE.x + 96, y: SHARE.y + 30, at: 110, click: true}];
const tl = cursorTimeline(KEYS, fps);
<Camera keys={[{at: 0, x: 960, y: 540, zoom: 1}, {at: 66}, {at: 94, x: 1330, y: 390, zoom: 1.3}, {at: 124}, {at: 152, x: 960, y: 540, zoom: 1}]}>
  <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
    <BrowserWindow url="driftnote.example/launch-plan" typeUrlAt={6} loadAt={44} tabs={['Launch plan']}>
      <Page />
      <div style={{position: 'absolute', left: SHARE.x * unit, top: SHARE.y * unit}}><UiButton label="Share" variant="secondary" width={150} pressAt={tl.pressOf(1)} /></div>
      <Cursor keys={KEYS} />
    </BrowserWindow>
  </AbsoluteFill>
</Camera>
```

**2. A 9:16 app demo with taps**
```tsx
const S = phoneScreen(700);
<PhoneFrame width={700} screen="#FFFFFF">
  <AbsoluteFill style={{translate: `${-28 * push}% 0px`}}><HomeScreen /></AbsoluteFill>
  {frame >= 60 ? <AbsoluteFill style={{translate: `${(1 - push) * 100}%`}}><AddScreen /></AbsoluteFill> : null}
  <TapIndicator size={78} taps={[{x: S.w / 2, y: 1046, at: 60}, {x: 108, y: 479, at: 132}]} />
  <Notification variant="pill" title="Expense saved" delay={256} area="parent" place="bottom" inset={176} />
</PhoneFrame>
```
(`push` = `ramp(frame, 66, 20, curves.inOut)`: the new screen pushes in from the right.)

**3. Code walkthrough, then a deploy**
```tsx
<Sequence durationInFrames={240}><CodeBlock code={SRC} lang="ts" title="ship.ts" cps={50} focus={[{lines: '5-6', at: 150}, {lines: [7], at: 192}]} /></Sequence>
<Sequence from={240}><Terminal lines={[{cmd: 'npm run deploy'}, {spinner: 'Deploying', frames: 40, done: 'Live at app.example'}]} /></Sequence>
```

**4. Talking-head overlays with sound**
```tsx
<Sequence from={30} durationInFrames={120}><LowerThird variant="split" name="আরিফ রহমান" role="Founder, Coinlet" scrim /></Sequence>
<ChapterBar chapters={[{title: 'Why offline matters', at: 0}, {title: 'Setting it up', at: 60}]} />
<Sequence from={400} durationInFrames={150}>
  <Subscribe delay={10} />
  <ClickSounds frames={subscribeClicks({delay: 10}, fps)} src={staticFile('ui/click.wav')} />
</Sequence>
```

**5. Chat story in a phone**
```tsx
<PhoneFrame width={440}>
  <div style={{position: 'absolute', top: phoneScreen(440).top * unit}}>
    <ChatThread panel={false} width={phoneScreen(440).w} height={760} fontSize={24} composer receipt="Read 10:24"
      messages={[{from: 'them', text: 'Is the release still on?', at: -60}, {from: 'them', text: 'Did it go out?', at: 40}, {from: 'me', text: 'Ten minutes ago', at: 104, react: {at: 130}}]} />
  </div>
</PhoneFrame>
```

**6. Sting and end card**
```tsx
<Sequence durationInFrames={150}><LogoReveal variant="stroke" mark={UI_MARKS.orbit} name="Orbitly" tagline="Plan the week in one view" exit={16} /></Sequence>
<Sequence from={150} durationInFrames={180}><EndCard slots={2} clickAt={118} doneCta="See you inside" /></Sequence>
```

## Remotion 4.0.528 facts and traps

- Inside a `<Sequence>`, `useVideoConfig().durationInFrames` is that Sequence's length: the kit's exits key off it,
  so wrap every temporary element in the Sequence of its beat.
- `interpolate` takes per-segment easing arrays (4.0.462), `posterize` (4.0.470), CSS string outputs (4.0.472) and
  `output: 'perceptual-scale'` (4.0.490); `Easing.spring` turns a spring into a curve (4.0.476, `allowTail` 4.0.483).
- `@remotion/media` `<Audio>` takes `from` and `durationInFrames` (4.0.445). Measured here: an MP4's AAC audio lands
  about 1.3 frames late (priming); pass `offset={1}` to `ClickSounds` only if you need it frame-exact.
- `@remotion/sfx` constants are remote URLs and only 7 are CC0 (mouseClick, uiSwitch, whoosh, whip, pageTurn,
  shutterModern, shutterOld); copy what you use into `public/`. The kit ships its own `ui/click.wav` and `ui/tap.wav`.
- `@remotion/mac-cursors` exists from 4.0.513 but is not in the shared modules; the kit's `Cursor` draws its own.
- `measureText`/`fitText` cache results for the page's life, even if measured before the font loaded; the kit never
  measures (rows grow with a CSS grid row from `0fr` to `1fr`).
- A CSS `translate`/`scale` on a wrapper makes it the containing block of absolute children: give content inside a
  scrolled or scaled wrapper an explicit height.
- `backdrop-filter` makes renders several times slower; the kit uses 94% solid surfaces instead. No `will-change` on
  text in renders.
- JetBrains Mono draws `=>` as an arrow ligature; synthetic italics ruin Bangla, so the kit sets non-Latin comments
  upright. Split Bangla by grapheme (`Intl.Segmenter`), never by code unit.
- Composition ids: letters, numbers and `-` only.

## References

- `references/pointer-and-touch.md`: the pointer and finger in depth, the timeline API, drags, targets, debugging, sound sync, a raw Remotion pointer.
- `references/devices-and-screens.md`: frames, screen geometry, building app screens, screen transitions, scrolling, light and dark palettes, footage of real apps.
- `references/code-and-terminal.md`: the tokenizer, colours, typing budgets, walkthroughs, terminals, alternatives.
- `references/chat-and-notifications.md`: chat timing, composer, reactions, notification looks, stacks and placement.
- `references/overlays-and-cards.md`: lower thirds, title, chapter and end cards, logo reveals, subscribe, chapter bar, countdown, focus tours.
- `references/craft-and-qa.md`: product-demo story grammar, numbers, legibility, safe areas, the review checklist.
- `references/remotion-api-and-traps.md`: the Remotion APIs this area uses with version tags, and errors with fixes.
