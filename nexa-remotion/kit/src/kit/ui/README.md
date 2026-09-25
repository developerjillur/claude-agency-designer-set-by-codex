# ui: product and interface animation

Pointer and touches, controls that react on cue, device and window frames, code and terminals, chat, notifications,
lower thirds, title, chapter and end cards, logo reveals, a subscribe nudge, a chapter bar and countdowns.

Rules that hold for every component here:

- **Sizes and positions are px at 1080** (the short side) and are multiplied by `unit` inside, so a scene written
  for 1920 x 1080 is identical at 1080 x 1920 and at 4K. Never multiply by `unit` yourself when you pass a prop.
- **Frames are local** to the enclosing `<Sequence>`. Temporary things (lower thirds, toasts, tooltips, the
  subscribe card, the chapter bar, countdowns, the cursor) leave by the last frame of that Sequence unless you
  pass `exit={false}` or an `exitAt`.
- **Everything reads the theme.** Interface colours come from `uiPalette(theme, mode)`: `mode="auto"` follows the
  theme, `"light"` or `"dark"` forces a neutral light or dark interface that keeps the theme's accents (a light
  app inside a dark video). Fonts are the theme's stacks, so Bangla works in every text part.
- **Targets come from layout constants.** Put the controls a pointer or finger will hit at absolute positions
  from named constants (`const SHARE = {x, y, w, h}`) and point the cursor at `SHARE.x + SHARE.w / 2`. Never
  estimate a target from padding and flex arithmetic.
- **Nothing here measures text.** Rows that arrive (chat, stacks, list inserts) grow with a CSS grid row going from
  `0fr` to `1fr`, which reaches the natural height without measuring and without font-loading races.
- Assets: `public/ui/click.wav` and `public/ui/tap.wav` (made with ffmpeg, 6 KB each, peak -3 dBFS). A project made
  with `nrk.py new` does not copy the kit's `public/`: copy `kit/public/ui` into the project's `public/` before
  using `staticFile('ui/click.wav')`.

Import from `./kit/ui` (or `../kit/ui` inside the kit).

---

## Pointer and touches (`Cursor.tsx`)

### `Cursor`
A pointer as a stage prop: 44 x 54 px at 1080 (a life-size 32 px pointer disappears on video), white with a dark
outline and a real drop shadow. It travels between keys on a bowed arc (x and y on different curves plus a sideways
bow), pulls back a few px before it goes, switches to the hand just before arriving on a clickable key, blooms on
hover, presses to 0.86, springs back past 1 and leaves a thin ring; it fades in at the first key and fades out
after its last event. The tip, not the corner of the drawing, lands on `(x, y)`.

| Prop | Default | Notes |
|---|---|---|
| `keys` | required | `CursorKey[]`: `{x, y, at, click?, double?, drag?, shape?, duration?, arc?}` |
| `size` | `1` | 1 = 44 x 54 at 1080 |
| `fill`, `stroke` | `#FFFFFF`, `#111317` | |
| `bloom` | theme accent | hover bloom colour; `false` for none |
| `ripple` | white ring with a dark hairline | reads on light, dark and accent controls; `false` for none |
| `lead` | 4 frames at 30 fps | arrival to press when `click: true` |
| `hideAfter` | 22 frames at 30 fps | after the last event; `Infinity` keeps it |
| `appear` | `'fade'` | or `'none'` |
| `debug` | `false` | red cross, index and press frame at every key |

`CursorKey`: `at` is the frame the tip arrives. `click: true` presses `lead` frames later; `click: 45` presses on
frame 45 exactly (sound sync). `drag: true` holds the button from this key's press until just after the next key
(the hand closes). `shape` is `'arrow' | 'hand' | 'grab' | 'text'` (default: hand where it clicks or drags).
`duration` overrides the move length (default grows with the square root of the distance: 14 f for 100 px, 24 f for
900 px at 30 fps). `arc` is the bow as a share of the move (default 0.1, capped at 80 px).

```tsx
const KEYS: CursorKey[] = [
  {x: 1300, y: 640, at: 6},
  {x: SAVE.x + SAVE.w / 2, y: SAVE.y + SAVE.h / 2, at: 40, click: true},
];
const tl = cursorTimeline(KEYS, fps);            // the same plan as data
<UiButton label="Save" pressAt={tl.pressOf(1)} doneLabel="Saved" />
<Cursor keys={KEYS} />                            // last child of the box the keys use
```

Gotchas: put the Cursor last inside the positioned box its coordinates refer to (a page, a window's content, the
whole frame) so it draws on top and moves with any camera that moves that box. Keep keys in time order. If two keys
are packed too tight the move gets shorter, never skipped. Author with `debug` on, then turn it off.

### `cursorTimeline(keys, fps, lead?)` and `cursorPose(tl, frame, fps)`
Pure functions behind the Cursor. `cursorTimeline` returns `clicks` (every press frame in order: put sounds and
control presses here), `releases` (drag drops), `start`, `end`, `pressOf(i)` and `arriveOf(i)` for the key at index
`i` of your list. `cursorPose` returns `{x, y, shape, press, bloom, ripples, moving}` for any frame: use it to carry
a dragged card with the pointer (`card = pose - grabOffset`). `cursorMoveFrames(dist, fps)` is the default move length.

### `TapIndicator`
Touches without a pointer, for phone demos: a translucent finger dot that presses (shrinks onto the screen), holds
and lifts (grows and fades), a long press with a filling ring, and swipes with a short trail.

| Prop | Default | Notes |
|---|---|---|
| `taps` | `[]` | `{x, y, at, hold?, long?}`: `at` = fully down (press the control here) |
| `swipes` | `[]` | `{from: [x, y], to: [x, y], at, frames?}` (14 f default) |
| `size` | `62` | finger dot diameter |
| `color`, `ring` | grey 45%, white | reads on light and dark screens |

```tsx
<PhoneFrame width={700}>
  <App />
  <TapIndicator taps={[{x: 338, y: 1045, at: 60}]} swipes={[{from: [300, 640], to: [300, 520], at: 30}]} />
</PhoneFrame>
```

### `ClickSounds`
Puts a sound on each frame of `frames`, lined up to its transient.

| Prop | Default | Notes |
|---|---|---|
| `frames` | required | e.g. `cursorTimeline(keys, fps).clicks` or `subscribeClicks(...)` |
| `src` | required | `staticFile('ui/click.wav')` after copying `kit/public/ui` |
| `volume` | `0.6` | |
| `offset` | `0` | frames from file start to transient; set `1` to cancel the measured AAC delay below |
| `length` | `12` | frames each sound may play |

Measured on 4.0.528 (MP4, AAC 48 kHz): a click placed on frame 54 decodes at 1.843 s instead of 1.800 s, a
constant +1.3 frames (AAC priming). That is inside a frame of sync; pass `offset={1}` only if you need it exact.

---

## Controls (`Controls.tsx`)

### `Pressable`
Wraps anything that should react to a click or tap: it depresses to `depth` (0.94), darkens slightly and springs
back a little past rest. Children can be a function of the press state to swap content after the press.

| Prop | Default | Notes |
|---|---|---|
| `at` | none | press frame or frames (the bottom of each press) |
| `hoverAt` | none | the pointer arrives: a 2 px lift |
| `depth`, `darken` | `0.94`, `0.08` | |
| `inline`, `style`, `children` | | `children` may be `(s: PressState) => node` with `press`, `after`, `count`, `since`, `hover` |

```tsx
<Pressable at={tl.pressOf(2)}>
  {(s) => <Chip on={s.after} label="Food" />}
</Pressable>
```
`pressStateAt(frame, fps, at, hoverAt)` gives the same state for controls that draw their own pressed look.

### `UiButton`
A themed button (primary, secondary, ghost, danger, dark; sm 44, md 56, lg 72 px tall) that presses on cue and can
roll to a done state ("Save" to "Saved" with a check). The radius follows the theme (pills in playful themes, square
in brutalist ones).

Props: `label`, `variant='primary'`, `size='md'`, `icon`, `iconRight`, `pressAt`, `hoverAt`, `doneLabel`,
`doneIcon`, `doneVariant`, `width` (px at 1080; set it when the label swaps), `radius`, `color`, `mode`, `style`.
```tsx
<UiButton label="Publish" icon="sparkle" width={200} pressAt={150} doneLabel="Published" doneIcon="check" doneVariant="dark" />
```
Gotcha: give a `width` whenever `doneLabel` differs in length, or the button reflows when it swaps.

### `Toggle`
A switch that flips on cue: the knob stretches while it travels (a spring) and the track fills with colour.
Props: `on=true` (the state after `at`; before it the opposite), `at`, `label`, `size=1` (64 x 38), `color`
(default positive), `mode`, `style`.
```tsx
<Toggle on at={tl.pressOf(3)} />
```

### `SearchBar`
A search field that focuses (accent border and ring), types a query at a human rhythm and can open a suggestion
list with the typed part in bold and one row picked.
Props: `text`, `placeholder='Search'`, `typeAt=12`, `cps=14`, `focusAt`, `width=720`, `height=68`, `suggestions`,
`suggestAt` (6 f after typing), `pick`, `pickAt`, `hint` (a key cap shown while empty), `mode`, `style`.
```tsx
<SearchBar text="invoice" typeAt={24} cps={9} suggestions={['Invoice template', 'Invoices from March']} pick={1} pickAt={96} />
```

### `FormField`
A labelled input that focuses, types (passwords as dots, amounts in tabular figures), blurs and can confirm with a
check (border turns positive). Typing splits by grapheme, so Bangla conjuncts never break.
Props: `label`, `value`, `kind='text'|'email'|'password'|'amount'`, `placeholder`, `prefix`, `typeAt=10`, `cps=13`,
`focusAt`, `blurAt`, `validAt`, `hint`, `width=560`, `height=64`, `mode`, `style`.
```tsx
<FormField label="নাম (Name)" value="আরিফ রহমান" typeAt={20} cps={6} blurAt={52} />
<FormField label="Email" value="arif@coinlet.example" typeAt={58} validAt={98} />
```

### `KeyCombo`
Key caps for a shortcut; they pop in one after another and press together. `'cmd'`, `'shift'` and `'enter'` draw
their symbols (no font glyph needed). Props: `keys`, `at=0`, `pressAt`, `size=64`, `mode`, `style`.
```tsx
<KeyCombo keys={['cmd', 'K']} at={4} pressAt={18} />
```

---

## Frames and stages (`Frames.tsx`)

All frames take their screen as `children`, draw no brand marks, and switch materials for light and dark themes.

### `BrowserWindow`
Tabs (with a letter favicon), traffic-light controls (`controls='mono'` for neutral dots), back, forward, reload, an
address bar with a lock and the domain in full colour, a share icon and an avatar. The URL can type itself and a thin
loading bar can run under the toolbar.

Props: `width=1440`, `height=860`, `url`, `typeUrlAt`, `tabs`, `activeTab=0`, `loadAt`, `controls='color'`,
`mode`, `page`, `radius=14`, `shadow=true`, `children`, `style`. `browserChromeHeight(withTabs)` = 98 (58 without
tabs): the page's top inside the window, for placing things from outside.
```tsx
<BrowserWindow url="driftnote.example/launch" typeUrlAt={6} loadAt={44} tabs={['Launch plan', 'Inbox (3)']}>
  <Page />
</BrowserWindow>
```

### `MacWindow`
A desktop window: controls, a centred title, an optional toolbar slot, an optional sidebar. `MAC_TITLE_HEIGHT` = 52.
Props: `width=1280`, `height=800`, `title`, `toolbar`, `sidebar`, `sidebarWidth=280`, `controls`, `mode`,
`radius=14`, `shadow`, `children`, `style`.

### `PhoneFrame`
A modern phone: metal rim (graphite, silver or sand; `auto` picks graphite on light themes, silver on dark), side
buttons, a pill or dot camera, the status bar (time, signal, wifi, battery) whose icon colour follows the screen, a
home indicator and a faint glass reflection. The body is 2.06 times as tall as it is wide.

Props: `width=400`, `finish='auto'`, `camera='pill'|'dot'|'none'`, `statusBar='auto'|'dark'|'light'|'none'`,
`barFill` (a strip behind the status bar for content that scrolls under it), `time='10:24'`, `screen`, `mode`,
`homeIndicator`, `glare`, `shadow`, `children`, `style`.

`phoneScreen(width)` returns `{w, h, top, bottom, radius}` in px at 1080: lay the app out in `w x h`, start content
below `top`. Inside the children, `usePhoneScreen()` returns the same; `useInsidePhone()` returns null outside a
phone (notifications use it to sit under the status bar).
```tsx
const S = phoneScreen(700);
<PhoneFrame width={700} screen="#FFFFFF" barFill>
  <HomeScreen />                         {/* laid out in S.w x S.h */}
  <TapIndicator taps={[{x: S.w / 2, y: 1045, at: 60}]} />
</PhoneFrame>
```
Gotcha: the screen clips its children (rounded corners); put overlays that belong on the screen inside it.

### `LaptopFrame`
A thin black bezel with a camera dot, a hinge, and the base with its thumb scoop (silver or space grey).
Props: `width=1100` (the 16:10 screen), `finish`, `screen`, `mode`, `shadow`, `children`, `style`.
`laptopScreen(width)` = `{w, h}`.

### `StatusBar`
The phone status bar on its own (for full-screen app mock-ups without a device): `width`, `time`, `tone`, `battery`.

### `DeviceRise`
The keynote device entrance: the device rises `distance` px while tipping up from `tilt` degrees (perspective), scale
0.9 to 1, over 30 frames; optional exit. Props: `delay`, `duration`, `tilt=28`, `distance=160`, `exit=false`,
`exitAt`, `ease`, `origin`, `children`, `style`. Pass a small negative `delay` so frame 0 already shows the device.
```tsx
<DeviceRise delay={-8} tilt={22}><LaptopFrame>...</LaptopFrame></DeviceRise>
```

### `ScrollView`
Page content that scrolls between keys (`{at, y}`, y in px at 1080 from the top), ease in-out per move, with a thin
scroll bar that shows while it moves. Fills its parent. Props: `keys`, `ease`, `scrollbar=true`, `mode`,
`children`, `style`. Repeat a `y` on a later frame to hold. Give the content an explicit height.

### `UiBackdrop`
A lit ground for product shots (never a flat vacuum): `variant='glow'|'dots'|'plain'`, `color`, `light`, `style`.

---

## Code and terminal (`Code.tsx`)

### `CodeBlock`
A code window typed by character (with a caret) or by line, coloured by a small tokenizer (ts, tsx, js, jsx, py, json,
bash, text), with line numbers and a walkthrough: `focus` steps move a highlight band and dim the other lines. With a
fixed `height` the view follows the caret.

| Prop | Default | Notes |
|---|---|---|
| `code`, `lang` | required, `'ts'` | |
| `typing` | `'char'` | `'line'` (lines slide in every `lineEvery`), `'none'` (fades in) |
| `startAt`, `cps` | `0`, `45` | code types evenly and fast; leading spaces appear at once |
| `lineEvery` | 5 f at 30 fps | |
| `focus` | `[]` | `[{lines: [5, 6] or '5-8', at}]`, 1-based line numbers |
| `dim` | `0.38` | opacity of lines out of focus |
| `lineNumbers`, `firstLine` | `true`, `1` | |
| `title`, `chrome` | none, `true` | file name in the title bar |
| `width`, `height` | `1100`, fits | |
| `fontSize`, `lineHeight` | `26`, `1.6` | |
| `mode`, `palette`, `radius`, `shadow`, `caret` | | `palette` overrides token colours |

```tsx
<CodeBlock code={SRC} lang="ts" title="ship.ts" startAt={6} cps={50} focus={[{lines: '5-6', at: 150}, {lines: [7], at: 192}]} />
```
Gotchas: budget the typing (`chars / cps * fps` frames plus a little) and put focus steps after it ends. JetBrains
Mono draws `=>` as an arrow ligature. Comments in non-Latin scripts are set upright (italic Bangla is synthesised and
ugly). `tokenizeCode(src, lang)`, `tokenLines(src, lang)` and `codePalette(dark, bg)` are exported for custom views.

### `Terminal`
A shell session: commands type at a human pace with a block caret, output prints two frames apart, `progress` lines
fill a bar with a percentage, `spinner` lines spin and turn into a check with a done text, and the view scrolls up as
it fills. Dark by default in every theme.

| Prop | Default | Notes |
|---|---|---|
| `lines` | required | `{cmd}`, `{out, tone?, icon?}`, `{progress, frames?}`, `{spinner, frames?, done?}`, `{gap}` |
| `startAt`, `cps` | `0`, `24` | |
| `path`, `symbol` | `'~/driftnote'`, `'$'` | the prompt |
| `title`, `idlePrompt` | `'<folder>: zsh'`, `true` | an empty prompt with a blinking caret at the end |
| `width`, `height`, `fontSize` | `1100`, `620`, `24` | |

Tones: `plain`, `muted`, `ok`, `warn`, `err`, `accent`, `info`. `terminalTimeline(lines, fps, startAt, cps)` returns
when each line appears and when the session ends.
```tsx
<Terminal startAt={8} lines={[{cmd: 'npm run deploy'}, {spinner: 'Deploying', frames: 40, done: 'Live'}, {out: 'খসড়া প্রকাশিত হয়েছে', tone: 'info'}]} />
```

---

## Chat and notifications

### `ChatThread` (`Chat.tsx`)
A two-sided chat that plays itself. The other side shows typing dots first (and the header says "typing..."),
bubbles pop from their sender's corner, older messages are pushed up and fade under the top edge, runs of one
sender get tighter spacing and a tail-side corner, group chats show names and initials avatars, reactions pop onto a
bubble, a read receipt appears under your last message, and with `composer` your messages are typed into the input
and sent.

| Prop | Default | Notes |
|---|---|---|
| `messages` | required | `{from: 'me'|'them', text, at?, name?, typing?, react?: {at, icon?}}` |
| `startAt` | `0` | first message when `at` is not given |
| `width`, `height` | `720`, `900` | |
| `header` | `{name: 'Maya Chen', status: 'online'}` | `false` for none |
| `composer`, `cps` | `false`, `20` | |
| `receipt` | none | e.g. `'Read 10:24'` |
| `fontSize` | `30` | 24 in a 440 px phone, 36 in 9:16 |
| `meColor`, `themColor`, `panel`, `radius`, `mode` | | `panel={false}` inside a phone |

Timing: a message without `at` lands a reading beat after the previous one; give `at` when it must hit a word. A
negative `at` puts history on screen from frame 0. `chatTimeline(messages, fps, startAt, composer, cps)` returns
`{land, dots?, compose?}` per message. `TypingDots` is exported on its own.
```tsx
<ChatThread composer receipt="Read 10:24" messages={[
  {from: 'them', text: 'Is the release still on?', at: -60},
  {from: 'them', text: 'Did the new build go out?', at: 40},
  {from: 'me', text: 'Yes, ten minutes ago', at: 104, react: {at: 130}},
]} />
```

### `Notification` (`Notify.tsx`)
One notification in three looks: `phone` (a banner that drops from the top with an app tile, app name, time, title
and two lines of body), `desktop` (a card that slides in from the side with actions and a thin timer line that runs
down until it leaves) and `pill` (a small status pill with a check: "Link copied").

Props: `variant='phone'`, `app='Driftnote'`, `title`, `body`, `time='now'`, `icon`, `iconColor`, `actions`,
`delay=0`, `exit=12`, `exitAt`, `place` (`top`, `top-right`, `top-left`, `bottom`, `bottom-right`, `bottom-left`,
`inline`), `area` (`'parent'` for phone, `'safe'` for the others: the frame's safe area), `inset=20`, `width`,
`timer=true`, `mode`, `style`. Inside a `PhoneFrame` a top banner sits under the status bar and is as wide as the
screen minus the insets, on its own.
```tsx
<Notification variant="desktop" title="Build passed" body="main, 2 min 14 s" icon="check" delay={12} />
<Notification variant="pill" title="Link copied" delay={214} area="parent" place="bottom" inset={36} />
```

### `NotificationStack`
Several notifications; each new one lands on top and pushes the others down (grid-row growth). Props: `items`
(notification props plus `at`), `variant='desktop'`, `place`, `area`, `inset`, `gap=12`, `exit`, `exitAt`, `mode`,
`style`. All leave together at the end.

---

## Overlays (`Overlays.tsx`)

### `LowerThird`
Name and role in four looks, placed at the bottom of the safe area (left or right):

- `bar`: an accent block grows, the name bar wipes out of it, the role bar in the accent follows 5 frames later,
  text slides in behind its bar; last in, first out on the way out.
- `split`: a vertical accent rule grows from its centre and the name and role slide out from behind it.
- `minimal`: the name rises through a mask, a short accent rule draws under it, the role in spaced capitals rises.
- `card`: a rounded card with an initials avatar pops up with a spring.

Props: `name`, `role`, `variant='bar'`, `side='left'`, `delay=0`, `exit=14`, `exitAt`, `accent`, `scrim` (a soft
dark gradient and light text for busy footage; use it with `split` and `minimal`), `size=1` (a 46 px name),
`y` (px above the safe bottom), `inline`, `style`. The exit sub-timings scale with `exit`, so every part is gone on the
last frame.
```tsx
<Sequence from={30} durationInFrames={120}>
  <LowerThird variant="split" name="আরিফ রহমান" role="Founder, Coinlet" scrim />
</Sequence>
```

### `Subscribe` and `subscribeClicks`
A channel card whose Subscribe button is clicked by a pointer (the button turns to "Subscribed" and a check draws),
then the bell is clicked and rings (decaying swing about its top) and fills. Props: `channel`, `handle`, `delay`,
`clickAt` (delay + 44), `bellAt` (click + 22), `exit`, `exitAt`, `color='#E3263A'`, `width=720`,
`place='bottom'|'center'|'inline'`, `cursor=true`, `mode='dark'`, `style`. `subscribeClicks({delay, clickAt, bellAt},
fps)` returns both press frames for sound.
```tsx
<Subscribe delay={10} />
<ClickSounds frames={subscribeClicks({delay: 10}, fps)} src={staticFile('ui/click.wav')} />
```

### `ChapterBar`
A segmented progress bar (one segment per chapter, a playhead) with the current chapter's number and name, which
rolls when the chapter changes. On a rounded panel by default so it reads over footage. Progress is a clock (linear).
Props: `chapters` (`{title, at}[]`), `end` (the Sequence's last frame), `delay`, `exit=12`, `exitAt`,
`place='bottom'|'top'`, `title=true`, `panel=true`, `width` (the safe width), `style`.

### `Countdown`
`variant='ring'` (a number punching in over a disc, the ring depleting each second), `'roll'` (numbers rolling up
in a card) or `'clock'` (an mm:ss timer whose changing digits roll). Centred in its parent. Props: `from=3`, `each`
(one second), `seconds=10` (clock), `go='Go'` (`''` fades the last number out), `delay`, `exit=10`, `exitAt`,
`size=320`, `color`, `plate=true` (a solid disc or card so it reads over footage), `style`.

### `FocusRing`
Dims everything in its parent except a rounded hole with an accent outline. The hole is on each key's rectangle at its
`at`, holds, and glides to the next (`move` frames, 14 at 30 fps, ending on the next key's frame): a guided tour.
Props: `keys` (`{at, x, y, w, h, r?}`), `move`, `dim=0.55`, `ring`, `pad=10`, `delay`, `exit`, `exitAt`.

### `UiTooltip`
A small dark bubble (light in dark interfaces) with a pointer, popping out of the point it explains.
Props: `x`, `y`, `text`, `side='top'|'bottom'|'left'|'right'`, `at`, `exit`, `exitAt`, `size=22`, `mode`.
Time tooltips with a `<Sequence>` each, so each one's exit ends on its Sequence's last frame.

---

## Cards (`Cards.tsx`)

### `TitleCard`
A full-frame title: a kicker that wipes in, words rising through masks (3 frames apart), an optional accent word and
rule, a subtitle that rises after the title lands, a lit ground and a slow push-in (a still card reads as frozen).
Props: `title` (`\n` for your own line breaks), `kicker`, `subtitle`, `align` (left in landscape, centre in portrait),
`size` (124 or 92), `accentWord`, `rule`, `delay`, `exit=false` (a number plays the exit, last word first, ending on
the last frame), `exitAt`, `background='theme'|'none'|colour`, `push=0.03`, `style`.
```tsx
<TitleCard kicker="Product update" title={'Notes that\norganize themselves'} accentWord="organize" rule exit={14} />
```
Gotcha: break two-line titles yourself with `\n`; masks get extra room for Bangla vowel signs automatically.

### `SectionTitle`
A chapter card: a rule draws across, the title rises above it, "Chapter 02 / 05" slides out under it, and (full
variant) a big faint numeral drifts in behind. Props: `title`, `index`, `total`, `label='Chapter'`,
`variant='full'|'inline'`, `align`, `size`, `delay`, `exit` (14), `exitAt`, `push`, `style`.

### `EndCard`
The last card: a logo slot and name, a call to action headline, a subtitle, a button (optionally clicked by a pointer at
`clickAt` and rolling to `doneCta`), the address and handle, and 0 to 2 end-screen video slots on the right in
landscape. Props: `title`, `subtitle`, `cta`, `doneCta`, `url`, `handle`, `name`, `logo`, `slots`, `slotLabels`,
`clickAt`, `delay`, `push`, `background`, `style`. Portrait stacks everything centred.
```tsx
<EndCard slots={2} clickAt={118} doneCta="See you inside" logo={<MyMark />} />
```

---

## Logo reveals (`Logo.tsx`)

### `LogoReveal`
A mark (SVG paths, so it can be drawn), a wordmark and a tagline, brought in five ways:

| Variant | What happens | Timing at 30 fps |
|---|---|---|
| `mask` | the mark rises through a mask with a small turn, the wordmark rises after | mark 0-22, word 10-30, tagline 30 |
| `stroke` | outlines draw (parts staggered), fills fade in, the wordmark wipes from the left | draw 0-36, fill 26-42, word 30-52, tagline 50 |
| `scale` | the mark pops from 0.3 with a spring and a turn, one soft ring pulses, letters (up to 6) or words settle | 0-20, word 12+, tagline 36 |
| `split` | two halves of the mark slide in and meet, then the wordmark opens out from behind it | meet 0-20, open 16-38, tagline 40 |
| `wipe` | an accent block covers the lockup and leaves the other way, revealing it | cover 0-13, uncover 15-29, tagline 34 |

Props: `mark=UI_MARKS.note`, `name='Driftnote'`, `tagline`, `variant='mask'`, `size=170` (mark height), `layout='row'|
'stack'`, `color` (replaces the accent role), `delay`, `exit=false` (a number fades, settles and blurs it out by the
last frame), `exitAt`, `background`, `push=0.03`, `style`.

`LogoMark = {viewBox, parts: {d, fill?, stroke?, strokeWidth?}[]}`; colours may be theme roles (`'accent'`,
`'accent2'`, `'text'`, `'bg'`, `'onAccent'`). `UI_MARKS` holds four invented neutral marks: `note`, `orbit`, `peak`,
`coin`. For a client logo, trace its SVG paths into a `LogoMark` (fills as `fill`, lines as `stroke`).
```tsx
<LogoReveal variant="stroke" mark={UI_MARKS.orbit} name="Orbitly" tagline="Plan the week in one view" exit={16} />
```
Gotchas: `stroke` draws with `pathLength={1}`, so no path measuring is needed, but a mark made of filled shapes only
needs at least an outline worth drawing; a real brand logo needs the client's permission and files.

---

## Helpers

- `UiIcon` (`Icon.tsx`): 62 line icons drawn on a 24 grid: search, bell, bellFilled, check, x, plus, minus, heart,
  heartFilled, star, starFilled, chevronLeft, chevronRight, chevronDown, arrowLeft, arrowRight, arrowUp, refresh,
  lock, home, user, sliders, bolt, copy, play, pause, more, menu, mail, calendar, chart, folder, file, globe, share,
  download, trash, edit, clock, info, warning, terminal, code, sparkle, camera, image, send, mic, cart, wifi, sidebar,
  filter, grid, thumbUp, link, coffee, bag, train, wallet, cmd, enter, shift. Props: `name`, `size=24`, `color`
  (currentColor), `stroke=2`, `style`. `UI_ICONS` holds the drawings.
- `uiPalette(theme, mode)`: the interface colours (`page`, `panel`, `raised`, `chrome`, `bar`, `field`, `text`,
  `muted`, `faint`, `line`, the accents and states) for your own app screens.
- `useUiTyping(text, start, opts)` and `uiTypeSchedule(text, fps, opts)`: the typing engine (grapheme-safe, seeded
  jitter, beats after spaces and punctuation scaled by `pause`, instant indents for code). Returns `shown`, `count`,
  `done`, `endFrame` and a `caret` opacity (solid while typing, a soft blink when idle).
