# How MoSidd built the 47-second Vox-style explainer (Claude Code + Remotion)

Research notes written 2026-09-25. Every source below was accessed on 2026-09-25.
Tags in square brackets name the source. `V@m:ss` means the moment in the YouTube video [S1]
where the fact is visible on screen or spoken. Values marked "eyeballed" were judged from video
frames, not read from text.

Copyright note: the author's prompts, script lines and article text are paraphrased here with every
instruction and number kept. The exact wording can be checked at the listed timestamps.

---

## 0. Sources and what could be read

| ID | Source | URL | Status |
|---|---|---|---|
| S1 | YouTube: "I Made Vox-Style Motion Graphics Using Only Claude Code & Remotion", channel MoSidd (@mo-sidd), 13:11 long, uploaded 2026-06-28, about 194k views when accessed | https://www.youtube.com/watch?v=7wuYBfE131U | Read: description, chapters, full auto-caption transcript (word-level timings), and 1080p frames viewed in a browser at chosen timestamps |
| S2 | The write-up "How I Built a Fully VO-Synced Motion-Graphics Explainer in Remotion" (byline MoSidd, AI Made Easy, about 12 min read) | Not public. It is a local HTML page, `localhost:8099/website/how-to-remotion-broll.html` (URL bar visible at V@4:37), that he scrolls through on screen | Read section by section from 1080p frames of S1. Not on Medium or anywhere else I could find |
| S3 | Skool community "AI Visual Production Lab" (owner Mo Siddique), about page | https://www.skool.com/ai-visual-production-lab-4976/about | Read. Holds "full project files from every video: skill files, storyboards, scripts, assets" plus build guides, free, about 5.8k members. Content needs an account, so not read |
| S4 | MoSidd: "I Built a Vox Explainer Using Claude Code & Remotion (No Plugins)", 2026-07-05 | https://www.youtube.com/watch?v=Y6mOBK5peDU | Description and auto-captions read |
| S5 | MoSidd: "Vox-Style Animated Charts With ONE PROMPT (Remotion + Claude Code)", 2026-07-18 | https://www.youtube.com/watch?v=dv3ADYu74DE | Description and auto-captions read |
| S6 | MoSidd: "Full Remotion Tutorial to Create Insane Motion Graphics", 2026-09-11 | https://www.youtube.com/watch?v=f393grXJn9E | Description and captions 3:00 to 15:00 read |
| S7 | MoSidd channel video list (plus descriptions of xOhh274Ayac, aSNYHAzPEKc, GvC9zXk4l7s, b7KlsXNQobs, dBakc0BdHjY) | https://www.youtube.com/@mo-sidd/videos | Read |
| S8 | Remotion docs: halftone(), OffthreadVideo, visual editing | https://www.remotion.dev/docs/effects/halftone , https://www.remotion.dev/docs/offthreadvideo , https://www.remotion.dev/docs/visual-editing | Read, for rebuild context only |
| S9 | Third-party summaries | https://learningatlas.us/learning/video/7wuYBfE131U , https://vidaspect.com/v/i-made-vox-style-motion-graphics-using-only-claude-code-and-remotion-2637af | Read. Built from the transcript, nothing new |

Not found: a Medium post with this title (checked Medium story, people and tag searches, tag RSS,
and more than 20 candidate handles through a reader proxy), any GitHub repo, any X or LinkedIn
thread by this author. X @MoSidd is an unrelated account. The S1 description links only to Skool,
remotion.dev and claude.com/claude-code.

---

## 1. The piece at a glance

- Subject: a US-Iran peace deal framed as the start of American decline. Hormuz blockade, oil at
  $116 a barrel, inflation at a three-year high, a debt of nearly $39 trillion that is larger than
  the economy, interest that costs more than the military, the world moving off the dollar, and a
  closing line that empires end with an unpaid bill rather than a war. [S1 V@0:05 to 0:52; S2]
- Specs from the stats card that ends S2 [V@12:32]: 47.3 s runtime, 1080p at 30 fps, 1,419 frames,
  7 scenes, 10 VO beats, 100% in code. Scene compositions in Studio show 1920x1080, 30 FPS
  [V@8:19, V@10:04].
- Toolchain: the Claude desktop app, Code tab, on Windows (model label "Opus 4.8", effort High,
  "Bypass permissions" mode) [V@7:13, V@7:36]; Remotion Studio; Magnific and Higgsfield connected as
  MCP servers; an OpenAI image model shown as "GPT-2" on a card (he says "GPT 2.0", most likely GPT
  Image 2) [V@2:01]; ElevenLabs for the voice; Whisper for timestamps; Higgsfield for music [S2].
- The video's own 10-step outline (title card V@0:55): storyboard and script, lock a visual system,
  open Claude Code, project architecture, set up Remotion, animate with intent, fine adjustments,
  assemble master sequence, voiceover generation, music and final render.
- S2's own outline, "What we'll cover" [V@1:10]: storyboard and script; setup and building each
  scene (source, layers, keying, animation); previewing and tuning in Remotion Studio; assembling
  the master sequence; voiceover and timing the cuts to the word; music, polish and final render.

---

## 2. Script, beats and timing

S2 treats the narration as the timeline: short beats, one idea per line, and the script doubles as
the shot list. Its storyboard figure shows a list labelled "10 beats" wired to scene cards, with a
ruler labelled one beat per scene [V@1:21].

### 2.1 The 10 VO beats and where they start

Start times come from the YouTube auto-captions of S1 (word level). The explainer's first word is at
5.28 s and the empty paper frame is on screen at 5.34 s, so composition time = YouTube time minus
5.28 s. Frames are my arithmetic at 30 fps.

| Beat | Content (paraphrased) | YouTube start (s) | Comp start (s) | Comp frame |
|---|---|---|---|---|
| L1 | US and Iran are signing a peace deal | 5.28 | 0.00 | 0 |
| L2 | the fall of the American empire has already begun | 8.88 | 3.60 | 108 |
| L3 | it started when a much weaker nation held the Strait of Hormuz hostage | 12.84 | 7.56 | 227 |
| L4 | oil prices jumped to $116 a barrel | 19.20 | 13.92 | 418 |
| L5 | pushing US inflation to a three-year high | 24.80 | 19.52 | 586 |
| L6 | hitting a nation already owing nearly $39 trillion | 28.16 | 22.88 | 686 |
| L7 | a debt now bigger than the whole economy | 33.48 | 28.20 | 846 |
| L8 | where interest alone costs more than the whole military | 36.88 | 31.60 | 948 |
| L9 | and the world is quietly leaving the dollar | 41.08 | 35.80 | 1074 |
| L10 | empires end not with war but with a bill they cannot pay (two sentences, one beat) | 46.00 | 40.72 | 1222 (last word about 46.3 s) |

The auto-captions drop "nearly $39" in L6. The ElevenLabs text box [V@11:38] and the on-screen
"$39 TRILLION" confirm the figure.

### 2.2 Scene windows (S2 figure "VO-driven timing", V@11:55)

The figure shows the VO waveform (47.3 s) with tick marks and seven scene blocks sized to their VO
windows. Its caption says each block's width is its frame count and that the audio decides the edit.

| Scene | Window (s) | Frames at 30 fps | Beats | Label in figure |
|---|---|---|---|---|
| 01 | 0.0 to 3.4 | 102 | L1 | (none) |
| 02 | 3.4 to 7.2 | 114 | L2 | (none) |
| 03 | 7.2 to 19.3 | 363 | L3, L4 | Ocean / oil |
| 04 | 19.3 to 31.2 | 357 | L5, L6, L7 | Inflation / debt |
| 05 | 31.2 to 35.3 | 123 | L8 | (none) |
| 06 | 35.3 to 40.3 | 150 | L9 | (none) |
| 07 | 40.3 to 47.3 | 210 | L10 | Empire bill |

The frames sum to 1,419, which matches the stats card.

Observation (my comparison of 2.1 and 2.2): every cut sits about 0.2 to 0.5 s (6 to 15 frames)
before the first word of its line, in the breath between lines. The video frames agree: each scene
change in the YouTube cut happens at the window start computed with the 5.28 s offset.

---

## 3. The full scene breakdown table (S2, V@1:30 to 1:39)

Header as shown: `#`, VOICEOVER LINE, BACKGROUND, MIDGROUND ASSET, FOREGROUND ASSET, MIDGROUND PROMPT,
FOREGROUND PROMPT, TRANSITION. (The brief called the first text column VOICELINE and did not list
MIDGROUND ASSET. The page has both asset columns.) The table's subtitle presents each beat as a
layer-and-prompt sheet.

BACKGROUND is one merged cell for all seven rows: a locked paper / Photoshop texture, file
`mo-photoshop-background.png`.

Asset descriptions are paraphrased. Prompts are given as their descriptor lists, in order.

| # | Beats | Midground asset | Foreground asset | Midground prompt | Foreground prompt | Transition |
|---|---|---|---|---|---|---|
| 01 | L1 | Halftone cut-out portraits, Trump on the left and Khamenei on the right, with red marker stroke | White House facade cut-out, front-on, settles in front | high-contrast B&W halftone cut-out portrait of [leader]; chest-up; bold newsprint dot texture; transparent background; sharp edges | flat front-on illustration of the White House facade; clean vector; warm soft shadow; transparent background | Hard cut |
| 02 | L2 | An op-ed page of "The Nation" built in code (masthead, headline, columns) | none (typographic) | none: vector layout, real article text, amber highlighter sweep | none | Hard cut |
| 03 | L3, L4 | Oil tanker cut-out plus a keyed ocean video; the ship sails over looping waves | Oil price counter plus oil-barrel icon, rising on the foreground band | side-profile flat editorial illustration of a large black oil tanker / cargo ship; transparent background; plus a looping ocean-wave clip with alpha | flat isometric oil-barrel icon; marigold and warm-black; bold outline; transparent background | Slide-out |
| 04 | L5, L6, L7 | Self-drawing CPI line chart plus isometric US map | "$39 TRILLION" headline that pops to the front | isometric United States map; subtle stars-and-stripes texture; warm shadow; transparent background (the chart itself is drawn in code) | none: heavy display type, code-driven | Closer move |
| 05 | L8 | US map (debt) plus a worker cut-out (labour) against a soldier and tank cut-outs (military) | "Interest: $1 trillion" label | cut-out of a US construction worker; half-body; transparent background; red offset marker outline. Plus a cut-out US soldier. Plus a flat military tank illustration | none: text label, code-driven | Hard cut |
| 06 | L9 | B&W cut-out of Xi and Putin shaking hands, plus comic speech bubbles | Tiananmen gate cut-out spanning the foreground base | black-and-white cut-out photo of two world leaders shaking hands; transparent background; red offset marker outline | flat illustration of the Tiananmen gate / Chinese government building; transparent background; warm shadow | Hard cut |
| 07 | L10 | Burning $100 bill, a transparent video floating above | Typewriter punchline plus a closing vignette | a single US $100 bill burning at one edge; flames and smoke curling up; alpha / transparent background; 4K; slow motion | none: typewriter text reveal, code-driven | Fade to black |

Project folders on disk (Windows Explorer, V@3:42 to 3:55): `F:\Mo Sidd\Remotion Video\scenes\` holds
`Result`, `scene-01-peace-deal`, `scene-02-downfall-newspaper`, `scene-03-ocean-tanker`,
`scene-04-inflation-debt`, `scene-05-debt-military`, `scene-06-dollar-yuan`, `scene-07-empire-bill`.
Scene 01 contains `background.png`, `iran-halftone.png`, `trump-halftone.png`,
`white-house-foreground.png`. Scene 03 contains `background.png`, `keyed-ocean.webm`,
`oil-barrel.png`, `tanker-ship.png`. Each scene folder carries its own copy of the shared background.

---

## 4. Visual system

S2 "Lock a visual system" [V@2:14], in my words: one background, one font stack and one accent
palette, so the separate beats feel like one film. Its three rules: the same paper-textured
background in every scene; heavy display type for headlines with an orange/red accent for emphasis;
a signature marker-stroke outline on every cut-out character. Its reason: settle the look once, up
front, so every later scene is a variation rather than a new design problem.

Spoken reason for the locked background [V@4:37 to 4:52]: the static background with elements
moving in reads as one continuous shot instead of many cuts.

Observed in the frames (eyeballed unless a value was read from text):

- Background: light warm-grey paper with a faint white graph-paper grid (cells very roughly 65 to
  100 px at 1080p) and fine grain. Identical in every scene.
- Midground people: black-and-white halftone photo cut-outs (fine dot screen). Behind each one sits
  a flat red-orange copy of its silhouette, offset up and to the left, which is the "offset red marker
  stroke". Studio props read `strokeColor: #E04329` (text, V@8:26 and the S2 tuning figure at
  V@11:05), plus `shadow: true`, `zOffset: 1` and a `strokeOpacity` field [V@8:26].
- Foreground objects are in full colour (White House, Tiananmen gate with red flags, work gear, oil
  barrel) with warm soft shadows. The foreground band hides the characters' lower bodies.
- Type classes: a heavy geometric sans in near-black for figures and headlines ($116, $39 TRILLION,
  the interest label); a bold high-contrast serif for the newspaper; uppercase monospace typewriter
  type for the ending; comic hand lettering in the speech bubbles. No font names are given in any
  readable source.
- Accents: red-orange stroke (#E04329, read); amber highlighter on the newspaper headline; marigold
  oil barrel; orange chart line against a grey comparison line; an orange-outlined callout box.
- A thin orange progress bar grows along the bottom edge of the YouTube cut over the 47 s. It does
  not appear in the per-scene Studio views, so it may be an edit overlay (unverified).
- In S6 (about 13:30) he explains the halftone purpose: stock images of mixed colour and lighting
  look like one printed magazine layout once they share a halftone pass.

---

## 5. Setup: Claude Code and the MCP connectors

- He works in the Claude desktop app's Code tab, project "Remotion Tutorial". He first selects the
  `scenes` folder as the working folder. Running the setup prompt before choosing a folder did not
  work, so he picked the folder and ran it again [V@4:19 to 4:33].
- Connectors enabled in the "+" menu: Adobe for creativity, Higgsfield, Magnific, vidIQ for Claude,
  Claude in Chrome [about V@2:36 to 2:41]. To add one: Settings, Connectors, Customize, then "Add
  custom connector" with a name and the remote MCP server URL [V@2:42 to 2:57 spoken; connector
  settings page at V@2:49; dialog at V@2:54].
- Magnific connector URL on screen: `https://mcp.magnific.com`, with 10 interactive tools such as
  `creations_list`, `images_models_show`, `library_show`, `stock_show` [V@3:17]. A caption card
  says this lets Claude Code fetch images directly, with no manual downloads from Magnific [about
  V@3:08].
- The green-screen ocean clip came from Magnific, background removed [V@10:08 to 10:23].

---

## 6. Remotion architecture

### 6.1 The pattern S2 describes ("Set up Remotion & a reusable scene pattern", V@3:33)

- Each scene lives in its own folder.
- Each scene is prop-driven: a schema defines every position, size, timing and colour.
- Each scene renders the shared background first, so beats stay visually continuous.
- He writes none of the code. He describes what he wants and Claude Code writes it.
- Callout "Everything is a prop" [V@6:59]: no magic numbers in JSX. Positions, sizes and timings are
  exposed so tuning happens without touching code.
- Tuning figure [V@11:05]: a mock Studio panel for a scene named `EmpireBill` with a `strokeColor`
  field set to #E04329 and a "Save props" button. Caption: every slider writes back into the code.

### 6.2 What Claude Code actually built (its on-screen summary, V@7:36)

- `SceneAsset.tsx`: one reusable component that drives every asset, plus an `assetSchema({...})`
  factory that declares a scene's assets. Every field is editable live in the Studio props panel:
  - Position: `left` / `bottom` as % of canvas (resolution-independent), plus `x` / `y` pixel nudges
  - Size: `width`, `height`, `scale`, `rotate`, `opacity`
  - Entrance: `rise` / `fade` / `pop` / `none`, with `startFrame`, `durationInFrames`, `riseFrom`
  - Idle life: `floatAmp` / `floatSpeed` (a subtle bob)
  - Look: drop shadow plus the red marker-stroke outline (`strokeColor`, `strokeOpacity`, `strokeX`,
    `strokeY`)
- `Scene.tsx`: a wrapper that renders the locked background and the layered children. Each scene is
  its own component wrapping it.
- `Root.tsx` registers two compositions: `Scene01PeaceDeal` (worked example: two halftone portraits
  in the midground with red strokes, White House in the foreground) and `SceneTemplate` (blank start
  that renders labelled placeholders).
- Recipe for each new scene, also written to `README.md`: copy `SceneTemplate.tsx` to
  `SceneNN_Name.tsx`; add one `assetSchema({ src, ... })` per cut-out and drop the file in `public/`;
  render one `<SceneAsset layer="midground|foreground">` per asset; register a `<Composition>` in
  `Root.tsx`. Scripts: `npm run dev` for Studio, `npm run render:scene01`.
- It then offered to scaffold scenes 02 to 07 from their asset folders.
- Self-check before handing over [V@7:13]: clean typecheck, then it rendered a still (frame 150 of
  scene 01), opened the PNG, confirmed the three layers composite correctly, and checked that the
  template renders its placeholders.
- Studio for the rebuilt scene: `Scene01PeaceDeal`, 1920x1080, 30 FPS, 9.00 s [V@8:19]. Example asset
  props: `src: scene-01-peace-deal/trump-halftone.png`, an `alt` text, `bottom: 30`, `x: 0`, `y: 0`,
  `width: 520`, `height: 580` [V@7:59 to 8:41].

### 6.3 His production project (scene tour, V@10:00 to 10:52)

- The shipped scenes live in a separate Remotion project called "my-video" with many `Broll...`
  compositions, among them `BrollPeaceDealScene`, `BrollOceanTankerScene`, `BrollInflationDebtScene`
  and `BrollDebtTransitionNextScene` (1920x1080, 30 FPS, 10.00 s), next to b-roll from other videos
  [V@10:04]. A browser tab shows a composition named `EmpireDownfallSequence`, probably the master
  [V@4:37].
- Props hold asset paths under `public/broll-<scene>/`, for example
  `broll-ocean-tanker/mo-photoshop-background.png`, `broll-ocean-tanker/tanker-ship.png`,
  `broll-ocean-tanker/keyed-ocean.webm`, `broll-inflation-debt/us-map.png`,
  `broll-debt-transition-next/work-gear.png`; layout numbers such as `shipX`; and the on-screen words
  as string props (`debtAmountText`, `interestLabelText`) [V@10:04, V@10:13, V@10:52].

### 6.4 Master sequence (S2 section 04, V@11:07)

All beats are chained into one composition with Remotion's `<Series>`. Each plays for a set number
of frames and receives its tuned props. The frame counts are the VO windows in section 2.2.

### 6.5 Zod and Studio problems met on camera

- `schema.parse({})` failed because the nested asset objects had no default. Claude gave each asset
  group a `{}` default [V@7:13].
- Studio refused to save default props for `Scene01PeaceDeal`. Claude's explanation [V@8:16]: Studio
  writes `defaultProps` back into the source by static analysis, so they must be a hard-coded object
  literal inside `<Composition>`, not a computed expression such as `schema.parse({})`. It rewrote
  `Root.tsx` for both compositions. The Remotion docs agree: default props must be inlined for
  visual editing [S8].

---

## 7. Prompts he gave Claude Code (paraphrased, all instructions kept)

1. Kickoff [S2 V@3:33; run at V@4:14]: set up a new Remotion project, then build a reusable scene
   pattern to repeat for every scene. Each scene gets its own component with a locked background and
   an animated midground and foreground. The background stays the same across all scenes. Give full
   scale and prop control for every asset in the scene.
2. Halftone [S2 V@5:24; card at V@5:47]: turn the Trump image in the folder into black and white and
   finish it with a half-tone pattern, then do the same for the Khamenei image.
3. Animate scene 1 [S2 V@6:37; read aloud V@6:41]: the White House springs up first, Trump and
   Khamenei right after; stagger them so they do not all move at once; put an offset red marker
   stroke behind each midground cut-out.
4. Start Remotion Studio for me, please [V@8:09; the captions mishear it as "stop" at V@7:43].
5. Fix this error, please, with the Studio default-props error pasted in [spoken V@8:06; visible in
   the chat at V@8:16].
6. Spoken advice: if the props panel shows no controls, ask Claude Code for a prop control on every
   element on screen [V@8:24].
7. Master [S2 V@11:07]: stitch all scenes into one video, in order, each lasting as long as its part
   of the voiceover, back to back as one film.
8. VO sync [S2 V@11:55; spoken V@11:54]: embed the voiceover in the composition and sequence the
   scenes to it, so that each scene starts and ends on its own line of narration and every cut lands
   on the word.
9. Render [S2 V@12:32]: render everything as a 1080p MP4 with music and voiceover mixed in. Spoken
   alternative: export picture only and mix music and VO in Premiere Pro [V@12:38 to 12:48].

The exact prompt files are in the Skool practice kit [S3], which needs an account.

---

## 8. Asset preparation: cut-outs, keying, halftone

- S2 "Cut the assets out (keying)" [V@5:24]: every asset must be transparent. Stills are keyed to a
  transparent PNG by flood-filling the background from the image edges and then keeping only the
  largest connected shape, so fills inside the subject survive. Footage is transcoded to a
  transparent VP9 WebM and played with `<OffthreadVideo transparent>`. The portraits then get the
  newsprint look (black and white with halftone dots) through prompt 2 in section 7.
- Figure "Keying to compositing" [V@5:58]: the keyed transparent PNG next to the composited scene.
- Remotion docs [S8]: `transparent` makes OffthreadVideo extract PNG frames; alpha works with VP8,
  VP9 and ProRes; it is about 40% slower, so use it only where needed.
- Remotion also ships a native `halftone()` effect (`@remotion/effects/halftone`, from v4.0.467, for
  `<Video>`, `<HtmlInCanvas>` and `<Solid>`; options include shape, dotSize, dotSpacing, rotation,
  colorMode, dotColor, invert) [S8]. The video does not show which method produced his halftone PNGs;
  Claude Code processed the image files on request.
- Image prompts for every midground and foreground asset are in the table in section 3.

---

## 9. Animation, scene by scene

General rule from S2 [V@6:37]: `spring()` for pop-ins, `interpolate()` for moves, draws and fades.
Reused signatures: the offset marker stroke, a typewriter reveal, comic speech bubbles. S2's gallery
of beats [V@6:59] shows the newspaper (built in code), the tanker with counter, the speech bubbles
and the burning bill. No spring configs or stagger numbers are given for this piece. In S5 his dot
pop is a "small crisp spring" with damping about 19 and stiffness about 280.

Times below are YouTube-cut seconds from frames I viewed; composition time is 5.28 s less.

- 01 Peace deal (5.3 to 8.7): the paper frame is empty for a moment; the White House rises into
  place by about 5.6; Trump rises from behind it around 6.3 to 6.9; Khamenei is up by 7.9. The
  elements arrive roughly 1 s apart (eyeballed). In Studio he raised the White House scale 1.5, then
  1.6, then 1.8, set Trump to 1.4 and moved Y down, saving after each change [V@8:42 to 9:36].
- 02 Newspaper (8.7 to 12.5): a code-built op-ed page, slightly rotated, with a drop shadow, drifting
  slowly. It has a masthead, date line, section label, bold serif headline, italic dek, byline, drop
  cap, text columns and a grey image block. An amber highlighter sweeps across the two key headline
  words between about 9.5 and 10.6, finishing on the spoken word "Empire" (10.6).
- 03 Tanker and counter (12.5 to 24.6): the tanker cut-out sails slowly left to right across the
  looping keyed ocean band. On "Oil prices" (about 19.2) the counter fades in beside an orange barrel
  icon with a small caption and counts up fast, slowing at the end: $25 at 19.2, $67 at 19.9, $99 at
  20.4, $116 by about 20.7. S2 says the counter hits $116 exactly as it is spoken, but in the YouTube
  cut the word "$116" is at 21.84 in the captions, so the count lands about 1 s early.
- 04 Inflation and debt (24.6 to 36.5): a cream chart card appears with a title, legend, y axis +2
  to +8 and x axis 2016 to 2026. The orange series with white dot markers draws itself left to right
  (about 25.0 to 28.7) over a grey comparison line, and a callout for the 2026 high (+4.2%) pops at
  the last point. The chart then shrinks and slides left while the isometric US flag map, floating
  over a soft shadow, and the "$39 TRILLION" headline enter from the right (about 30.7 to 31.8).
  The chart then leaves and the map moves to the centre (about 35.3): the "closer move" into 05.
- 05 Debt against military (36.5 to 40.6): map and headline move up. The worker cut-out rises and
  fades in at bottom left with full-colour work gear in front (about 37.2 to 38.0). The interest label
  is on screen by about 38.1, shortly after the VO says "interest" (37.2). The soldier with tank and
  US flag rises at bottom
  right (about 39.1, just before "military" at 39.8). Red strokes on both figures.
- 06 Dollar and yuan (40.6 to 45.6): the Tiananmen gate with red flags is the foreground; the Xi and
  Putin handshake cut-out rises and fades in behind it (about 41.1 to 42.0). The left comic bubble
  pops around 43.3 (an offer to trade in yuan, yen sign, key word in red); the right bubble answers
  with a short agreement around 44.9. Bubbles are cream, tilted, with a thick dark outline.
- 07 Empire bill (45.6 to 52.6): an uppercase monospace line types out character by character with a
  block cursor, then a second line, keeping pace with the voice (first word at about 46.0 to 46.2,
  last word typed about 0.3 s after it is spoken). A $100 bill sits at the bottom centre, partly
  cropped by the frame edge, and burns in from its left edge. S2's table says "fade to black"; the
  YouTube edit instead flashes warm and white into the presenter shot.

Camera: apart from the newspaper drift and the chart/map move, no global camera moves appear in this
piece. In S6 his camera method is to animate the scale and position of a container (for example
scale 1 to 2.8, with about 1.5 s holds), since Remotion has no camera.

---

## 10. Sound

- Voice [V@11:20 to 11:45]: ElevenLabs Text to Speech; voice listed as "Cate - Cinematic British RP
  Narrator" (he says "Kate"); model Eleven Multilingual v2; sliders near the defaults (speed about
  1.0, stability about 50%, similarity about 75%, eyeballed). The script is typed as 10 uppercase
  lines, 568 characters, with money written as a number plus the word dollars and "three-year" in
  words. He uses ElevenLabs directly rather than through Claude Code because his saved voices are
  there. He downloads the audio and puts it in the same project folder [V@11:44].
- Timing [S2 V@11:55]: generate the VO; transcribe it with Whisper for exact start and end times per
  line; fit each beat to its line window and retime the scene internals so key moments land on the
  word; then embed the audio (prompt 8).
- Music [S2 V@12:07]: Higgsfield, connected as an MCP, generates a tense documentary track. It sits
  under the narration at low volume with a fade in and out so the voice stays on top. S2's intro
  caption also calls it a tense documentary track [V@1:09].
- Foley: he says a piece may need some foley and background sounds, but lists none for this one
  [V@12:10]. S4 lists risers, blips, sonar pings and whooshes on camera moves.
- Mix and render: Remotion renders the final MP4 with music and VO mixed; the alternative is to mix
  in Premiere Pro [V@12:30 to 12:48].

---

## 11. What went wrong and how he fixed it

1. The setup prompt ran before a working folder was chosen. Fix: select the folder, run it again
   [V@4:19].
2. The first render of scene 1 looked off. Fix: scale and position in the Studio props panel, not
   code [V@7:52 to 9:43].
3. Zod default parsing failed on nested asset objects. Fix: `{}` defaults per asset group [V@7:13].
4. Studio could not save default props. Fix: hard-coded literal `defaultProps` in `<Composition>`
   [V@7:59 to 8:16].
5. Missing props panel: ask for prop controls. Unsaved slider values are lost, so save after each
   change [V@8:24, V@8:51].
6. Jerky audio while previewing. S2's "Optimise for smooth playback" [V@12:07]: one 28 MB background
   asset was stuttering the preview and dragging the audio with it; cropping and optimising it to the
   visible area (about 4 MB) fixed the preview and sped up renders with no visible difference. Its
   debug tip: jerky preview audio on heavy scenes usually means dropped frames from a giant asset,
   and the exported file is normally fine [spoken V@12:13 to 12:28].
7. In the narration he twice says "Kamala Harris" where the frames show Khamenei [V@8:36, V@9:29].

---

## 12. Related techniques from his other videos

- S4, map explainer (2026-07-05): real country shapes from world-atlas, TopoJSON and d3-geo; six
  plain-English prompts; each scene starts on the exact last frame of the one before, so the film
  reads as one continuous shot; built scene by scene so a fix in one chunk cannot break another;
  ease-out preferred (linear looks mechanical, back easing bounces); an explosion clip on black keyed
  with a screen blend; a film-grain overlay at the end; narrator picked from ElevenLabs through an
  MCP or API (he chose "Sterling" over "Gideon" and "Maya"); music by Magnific; foley list with
  riser, blip and sonar; one audio prompt covering a slow-building tension bed, one VO line per scene
  and whooshes on camera moves.
- S5, charts (2026-07-18): one prompt sets up Remotion, the texture style, the animation and the
  data; the printed-paper look is a paper/grain overlay, jagged marker edges on the shapes and grain
  over the whole frame; a parliament chart laid out on a grid, not concentric rings, revealed as one
  left-to-right wave; a racing line chart with a hand-drawn "boil" from fractal noise, kept subtle
  because too much becomes "buzz".
- S6, masterclass (2026-09-11): write prompts as specs in blocks (build, copy, data, colours,
  motion); 30 fps; bars start a few frames apart; ease-out for documentary work, since a spring pop
  looks cartoonish; camera by scaling a container; yellow marker highlights; a halftone pass to
  unify mismatched images; an offset drop shadow so cut-outs sit slightly above the paper.
- Other videos on the same stack [S7]: a Netflix vs Blockbuster collage reel (xOhh274Ayac); a collage
  animation built with Claude Fable 5, "GPT2 Image" via Replicate, Lyria 2 and ElevenLabs
  (aSNYHAzPEKc); a minimal reel at 15 fps with a halftone finish (GvC9zXk4l7s).

---

## 13. What to carry into our Remotion skill

1. A storyboard sheet with his exact columns: #, VO line, background, midground asset, foreground
   asset, midground prompt, foreground prompt, transition. Group beats into scenes (10 beats became
   7 scenes).
2. One locked paper background shared by every scene, cropped to 1920x1080 and kept under about
   5 MB (his 28 MB file caused preview stutter).
3. A `SceneAsset` primitive with an `assetSchema()` Zod factory covering the prop groups in 6.2.
   Default every field, give nested groups `{}` defaults, and write `defaultProps` as inline literals
   in `<Composition>` so Studio's save works.
4. Three layers in fixed order: paper background, then halftone cut-outs with the offset stroke
   (#E04329, offset up and left, plus a drop shadow), then full-colour foreground objects that hide
   lower bodies.
5. Keying: edge flood-fill plus largest connected component for stills; VP9 alpha WebM with
   `<OffthreadVideo transparent>` for footage, budgeting for the slowdown.
6. A halftone pass on every photo cut-out (preprocessed, or `halftone()` on canvas layers).
7. VO first: TTS, then Whisper line and word timestamps, then scene windows that cut 6 to 15 frames
   before each line's first word, then `<Series>`. Key beats inside scenes (counter end value,
   highlighter, bubbles, typewriter) are keyed to word times. Check that the counter really lands on
   its word; his lands about 1 s early.
8. Code-built beats worth turning into templates: newspaper page with highlighter sweep; count-up
   counter with icon; self-drawing line chart with callout; comic bubbles; typewriter with cursor;
   floating transparent prop video (the burning bill).
9. A verification loop: typecheck, render a still at a mid frame, look at it, then open Studio.
10. Do not imitate a real publication's masthead over invented copy (his scene 02 does this). Use a
    fictional masthead.

---

## 14. Gaps

- S2 section 03 (previewing and tuning in Studio) was only visible as its figure; its text was not
  shown. The rest of the "Gather the source material" paragraph and anything after the stats card
  were not shown either.
- No spring configs, stagger frame counts or font names for this piece in any readable source.
- The exact prompt wording is visible at the listed timestamps and is paraphrased here.
- The Skool project files (skill files, storyboards, scripts, assets) need an account and were not
  read.
