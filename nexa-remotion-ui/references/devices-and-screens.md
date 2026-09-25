# Devices, windows and the screens inside them

The frame tells the viewer where the product lives; the screen inside it carries the story. This file covers the
kit's frames, their geometry, how to build app screens that animate well, transitions between screens, scrolling,
device entrances, and working with real product footage.

## 1. Which frame

| The product is | Use | Notes |
|---|---|---|
| a web app or site | `BrowserWindow` | tabs for context, the URL can type itself and a loading bar can run |
| a desktop app | `MacWindow` | title, optional sidebar and toolbar |
| a phone app, 16:9 video | `PhoneFrame` (400 to 460 px wide) beside a headline | tilt a second phone behind for depth |
| a phone app, 9:16 video | `PhoneFrame` 650 to 720 px wide, or a full-screen app with `StatusBar` | key UI inside the platform safe area |
| a hero or launch shot | `LaptopFrame` rising with `DeviceRise` | 1000 to 1150 px screen width |
| a feature close-up | the screen content alone, cropped, with a `Camera` punch-in | no frame at all |

All frames draw no brand marks (generic window controls, a neutral phone, a plain laptop) and take their screen as
children.

## 2. Geometry (px at 1080)

| Frame | Numbers |
|---|---|
| `BrowserWindow` | default 1440 x 860, radius 14; tab strip 44 + toolbar 54 = page top at 98 (`browserChromeHeight(true)`); without tabs one 58 px row |
| `MacWindow` | default 1280 x 800, title bar 52 (`MAC_TITLE_HEIGHT`), sidebar 280 |
| `PhoneFrame` | body `width` x 2.06 width; rim 0.9%, bezel 3%, body radius 15.5%; screen = width - 6%; status bar 13.5% of the body width tall; home area 7.5% |
| `LaptopFrame` | screen `width` x 0.625 (16:10); bezel 2% sides, 3% top (camera), 3% chin; base 1.16 x the lid, 2.4% of the width tall |

`phoneScreen(width)` returns `{w, h, top, bottom, radius}`, `laptopScreen(width)` returns `{w, h}`. Lay screens out in
those sizes. Inside a phone's children `usePhoneScreen()` gives the same numbers and `useInsidePhone()` returns null
outside a phone.

## 3. Materials, light and dark

`uiPalette(theme, mode)` gives the interface colours: `page` (inside the window), `panel` (cards, sidebars), `raised`
(menus, toasts), `chrome` (title and tab bars), `bar` (toolbar, active tab), `field` (inputs, address bar), `text`,
`muted`, `faint`, `line`, and the theme's accents and states.

- `mode="auto"`: follows the theme. Light themes get a white page with 3 to 7% tints of the text colour for chrome and
  fields; dark themes use the theme's `bg2` and `surface` with a brighter raised layer and a darker field.
- `mode="light"` or `"dark"` against the theme: a neutral interface in that mode that keeps the theme's accents (a
  light app shown in a dark keynote, or the other way round).
- Shadows are layered (a hairline, a short contact shadow and a long soft one); in dark mode they add a 1 px light
  inner edge so windows separate from a dark ground.
- `PhoneFrame finish="auto"`: graphite on light themes (contrast), silver on dark ones; also `sand`.
  `LaptopFrame finish="auto"`: space grey on light, silver on dark.
- The phone's status bar picks dark or light icons from the screen colour; pass `statusBar` to force it.

## 4. Building a screen that animates well

- **Absolute where it moves or gets hit.** Buttons, fields, chips, rows that get tapped, anything the pointer or a
  finger touches: absolute positions from named constants. Static text blocks, lists and grids may use flex.
- **Real content.** Real button labels and names from the client; tabular figures (`fontVariantNumeric:
  'tabular-nums'`) for any number that changes; `UiIcon` instead of emoji; the theme's fonts only.
- **No measuring.** Things that appear in a list (a new row, a message, a toast) grow with a grid row, which reaches the
  natural height without measuring text:

  ```tsx
  <div style={{display: 'grid', gridTemplateRows: `minmax(0, ${p}fr)`}}>
    <div style={{minHeight: 0, overflow: p < 0.999 ? 'hidden' : 'visible', opacity: p}}>{row}</div>
  </div>
  ```
  `p` from 0 to 1 over 8 to 10 frames (ease out). A row that leaves runs the same backwards. The rows around it slide
  by themselves.
- **Numbers that change** count with `interpolate` and `toFixed`, over 15 to 25 frames with ease in-out, and hold.
  Intermediate values are visible, so count only between true values.
- **Charts inside screens** grow from the baseline once (bars 20 to 30 frames, ease out); the data module draws
  richer charts.

## 5. Moving between screens

| Change | Motion (30 fps) |
|---|---|
| push (open a detail) | new screen from `translate: 100%` to 0 over 20 frames ease in-out, old screen to -28% with a 25% dark veil; back does the reverse |
| modal dialog | veil 0 to 28% over 8 frames; the dialog from scale 0.94 and opacity 0 with a settle spring |
| bottom sheet | from `translateY(100%)` with a settle spring, veil behind |
| tab switch | cross-fade 6 frames, no movement |
| a toast after an action | a pill rises 26 px and pops (see chat-and-notifications.md) 6 frames after the action |

Start any change 6 to 10 frames after the press that causes it. Only mount the incoming screen from the frame its
transition starts, and unmount the old one after it is covered, so two heavy screens do not render longer than needed.
`@remotion/transitions` `TransitionSeries` also works inside a screen box (its sequences must be direct children;
`slide({direction: 'from-right'})` with `springTiming({config: {damping: 200}, durationRestThreshold: 0.001})`), but
the push above is simpler when the old screen stays partly visible.

## 6. Scrolling

`ScrollView keys={[{at: 30, y: 0}, {at: 48, y: 120}]}` translates its content by `-y` with ease in-out between keys
and shows a thin scroll bar while it moves. Give the content an explicit height (a translated wrapper becomes the
containing block of absolute children). Match a swipe (`TapIndicator swipes`) to the same frames. When content
scrolls under a phone's status bar, pass `barFill` to the `PhoneFrame` so the time and icons keep a solid strip.
Targets below a scroll: subtract the offset that holds at the tap frame.

## 7. Entrances, depth and the camera

- `DeviceRise`: rises 160 px while tipping up from 28 degrees with perspective and scaling from 0.9, over 30 frames
  (expo-like ease out), optional exit. Give it a small negative `delay` (-6 to -12) so frame 0 already shows the device
  on its way in.
- `Float` (motion module) after the landing adds 4 px of drift; never on a screen whose text is being read closely.
- Two phones: the back one smaller (360 vs 400), rotated -7 degrees, lower and behind, a dark screen against the light
  one; enter them 6 frames apart.
- Camera punch-ins (motion's `Camera`): 1.2 to 1.35x, 20 to 30 frames in, hold through the action, 25 to 30 frames
  out; the focus point near the control so it stays on screen. Rules from production work: never two moves on one
  transform (keep the camera as the outer node), never a lasting scale on the node that holds the whole UI when a
  sharp still matters (move content instead, or keep the zoom short), keep pointer and UI inside the camera so
  coordinates stay valid.

## 8. Real product footage

When the client has screen recordings or screenshots:

- Put them in the frame's children: `<Video src={staticFile('rec.mp4')} style={{width: '100%', height: '100%',
  objectFit: 'cover'}} />` from `@remotion/media` (or `<OffthreadVideo>`), `<Img>` for screenshots; `trimBefore` to
  start later, `playbackRate` to speed through waiting, `premountFor={30}` on the Sequence that holds them.
- Record without the system cursor and add the kit's pointer on top; take target coordinates from the recording's pixel
  grid: `x_1080 = x_recording x (frame box width / recording width) / unit`.
- Zoom with the Camera, not by cropping the file; keep 1.3x or less on 1080p recordings so text stays sharp (record at
  2x for deeper zooms).
- Blur or replace personal data (names, emails, tokens) before it reaches the video.

## 9. Faults and fixes

| Fault | Cause | Fix |
|---|---|---|
| A small window looks crude | chrome is sized in px, so a 500 px window has the chrome of a big one | render it at full size inside a wrapper with CSS `scale` and `transformOrigin: 0 0` |
| Content hides under the status bar or camera | laid out from y 0 | start below `phoneScreen(w).top` |
| The status bar collides with scrolled content | no strip behind it | `barFill` |
| An overlay meant for the screen spills out | placed outside the frame's children | put it inside the frame (the screen clips) |
| Light app looks grey in a dark video | `mode="auto"` in a dark theme | `mode="light"` on the frame and the controls |
| Text blurs during a zoom | a composited layer scaled up | keep zooms short and at most 1.35x, no `will-change` |
| A real OS or browser brand is visible | recorded chrome | use the kit's neutral frames; crop recordings to the page |
