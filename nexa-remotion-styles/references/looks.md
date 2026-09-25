# The looks, as recipes

Each recipe: when to use it, the theme, ground, type, motion, composition, signature moves and the kit parts,
transitions, sound, and what to avoid. Durations are at 30 fps. Kit parts are exact component names: the light
modules come from `./kit`, and parts marked fx, maps or three come from `./kit/fx`, `./kit/maps` or `./kit/three`.

## Keynote minimal
- **Use** premium tech, product reveals, design-led brands, investor or keynote-style statements.
- **Theme** `keynote` (dark) or `keynoteLight`; the brand accent on one word or one line only.
- **Ground** near-black #0A0A0B or near-white; a soft radial light behind the object; no texture.
- **Type** Inter 700 at 120 to 200 px for single statements, tracking -0.045 em, sentence case; body 400.
- **Motion** blur-in over 24 frames with `outQuart`, 16 px rise; fades out over 18; stagger 6; holds of 2 to 3 s; a 2%
  push-in on held shots; camera moves of 24 to 36 frames.
- **Composition** one sentence or one object per shot, centred or on thirds, about 40% empty space; full-bleed product
  moments.
- **Signature** a statement resolves word by word, then the product appears in the space it leaves.
- **Kit parts** `KineticTitle` (blur or mask), `Ground` (spot) with `Spotlight`, `ProductSpin` (three) or `DeviceRise` and `PhoneFrame`, `PushIn`.
- **Transitions** cuts and soft dissolves only.
- **Sound** piano or pad bed; soft whooshes on reveals; silence is allowed.
- **Avoid** bouncy springs, more than two colours, glow, particles, busy grids.

## SaaS launch, dark
- **Use** B2B software, developer tools, AI products, dashboards.
- **Theme** `midnight`; the brand accent; `accent2` for success states.
- **Ground** blue-black with a lit radial source, grain 0.03, vignette 0.25; an optional faint grid for depth.
- **Type** Manrope 800 headlines at 96 to 140 px; Inter body; realistic small UI text inside frames.
- **Motion** rises of 16 frames; `settle` springs on cards; the camera travels over the product UI (moves of 18 to 24
  frames); the cursor with its click stack; whips with motion blur between features.
- **Composition** the UI in a browser or window, the camera pushing to the feature, a short headline beside it; each
  feature shown as an action, never a bullet list.
- **Signature** the product's verb acted out in the interface (a card dragged, a report generated, a toast arriving).
- **Kit parts** `BrowserWindow`, `MacWindow`, `Cursor`, `Pressable`, `UiButton`, `Notification`, `Camera` or `ZoomAt`, `ProgressRing`, `Stat`, fx `Scenes` with `tr.whipPan` or `tr.slide`.
- **Transitions** slide or whip between features; a hard cut to the logo.
- **Sound** electronic bed at 110 to 125 BPM; clicks on presses; a whoosh on whips; a small riser into the call to action.
- **Avoid** purple-blue gradients by default, glass everywhere, invented metrics, three-column icon grids.

## Clean product explainer
- **Use** explaining a process or product to a broad audience; onboarding; help and support videos.
- **Theme** `studio`.
- **Ground** off-white #F5F6F7, white cards with elevation 2 to 3 shadows.
- **Type** Inter 800 headlines at 84 to 120 px; 500 body at 36 to 44 px.
- **Motion** 18-frame rises, stagger 5, calm springs, no bounce, holds by reading time.
- **Composition** split (text and visual), step cards, icons that draw on, a stat card; a different system every beat.
- **Signature** a step list whose each step becomes the next scene's hero.
- **Kit parts** `Card`, `Split`, `StatSplit`, `Icon`, `IconBadge`, `FlowDiagram`, `Stat`, `KineticTitle`, `Marker`.
- **Transitions** cuts; slides between steps.
- **Sound** light acoustic or corporate pop; soft pops on arrivals; a chime on completion.
- **Avoid** clip-art people, many colours, emoji as icons.

## Bright consumer app
- **Use** consumer apps, shopping, delivery, fintech for young people, app store previews.
- **Theme** `fresh`.
- **Ground** white or a pale mint band; colour blocks behind the phone.
- **Type** Outfit 800 headlines; Figtree body; short lines.
- **Motion** 14-frame pops with `outBack`; `settle` springs; the phone slides in on a spring; tap indicators; lists at
  4-frame staggers.
- **Composition** the phone centred or offset with a headline; native 9:16 versions.
- **Signature** the screen changes with a tap for every benefit.
- **Kit parts** `PhoneFrame`, `TapIndicator`, `Notification`, `Counter`, `Marker`, `Blob`, fx `tr.iris` into the call to action.
- **Transitions** push or slide; an iris into the call to action.
- **Sound** upbeat pop; taps and pops; a success chime.
- **Avoid** fake ratings, real brand logos, invented reviews.

## Kinetic typography
- **Use** event promos, manifestos, talk trailers, social teasers.
- **Theme** `kinetic`.
- **Ground** flat black; a few full-bleed accent frames (acid yellow) on the strongest words.
- **Type** Anton capitals at 160 to 320 px; one or two words a beat; tracking 0.
- **Motion** 10-frame mask reveals on `snap`; punch-ins (scale 0.33 to 1 in 5 frames) on the key word; hard cuts every
  12 to 24 frames on the beat; a shake on bass hits.
- **Composition** one giant word plus a small note; words may bleed off the frame when still legible; alignment
  alternates.
- **Signature** a colour flip (type and ground swap) on the strongest word.
- **Kit parts** `KineticTitle`, `BigStatement`, `WordRotator`, `Shake`, `beatGrid` and `snapToBeat`, fx `tr.glitchCut` once.
- **Transitions** hard cuts; one glitch.
- **Sound** a rhythmic track that the cuts follow; no voice or a short one.
- **Avoid** letter-by-letter staggers, fades, lines shorter than their reading time.

## Swiss grid
- **Use** architecture, design studios, museums and culture, annual reports.
- **Theme** `swiss`.
- **Ground** white with a visible 12-column grid (thin rules), red blocks.
- **Type** Archivo 800 display flush left; 500 body; big numerals.
- **Motion** 16-frame wipes on `inOut`; things move along grid lines; no rotation, no bounce.
- **Composition** asymmetric layouts on the grid; large numbers; a red rectangle as the anchor.
- **Signature** the grid draws itself and content snaps into its cells.
- **Kit parts** `Grid`/`Cell`, `Pattern` (grid lines), `Animate` with wipes, `BarChart` in black and red.
- **Transitions** wipes and hard cuts.
- **Sound** minimal techno, or silence with clicks.
- **Avoid** centring everything, drop shadows, gradients.

## Editorial magazine
- **Use** media brands, long reads, culture, founder stories.
- **Theme** `editorial`.
- **Ground** a white page; full-bleed photos with captions; hairline rules.
- **Type** Instrument Serif at 110 to 180 px (italic for emphasis); Inter body; spaced small capitals for kickers.
- **Motion** mask reveals by line over 20 frames; photos revealed by wipes; slow pushes on photos.
- **Composition** headline, deck and photo; pull quotes; a large number with a short caption.
- **Signature** a pull quote that arrives line by line, then its credit.
- **Kit parts** `KineticTitle` (mask by line), `Quote`, `Kicker`, `Label`, `KenBurns`, `Scrim`.
- **Transitions** cuts and wipes.
- **Sound** piano, acoustic or ambient; page turns sparingly.
- **Avoid** invented quotes, real mastheads, fake bylines.

## Data journalism
- **Use** reports, numbers that matter, finance and civic explainers.
- **Theme** `data`.
- **Ground** white; light grey panels.
- **Type** Source Serif 4 700 headlines; Inter body; IBM Plex Mono for data labels; tabular numbers.
- **Motion** charts draw while they are described; callouts land on their words; counters ease out; 18-frame rises.
- **Composition** one chart per beat, direct labels, one highlighted series, the source line always visible.
- **Signature** a chart that rescales when the story turns.
- **Kit parts** `ChartFrame`, `LineChart`, `BarChart`, `Donut`, `Stat`, `Callout`, `Counter`, maps `Choropleth`.
- **Transitions** cuts; morphs between charts.
- **Sound** an understated bed; soft ticks on data points.
- **Avoid** 3D charts, bar axes that do not start at zero, unsourced numbers, rainbow palettes.

## Vox collage
- **Use** explainers about places, money, history and politics-free current affairs, built from narration.
- **Theme** `vox`; with footage and cut-outs, use `nexa-video-creator` (its `vox` overlays) and its recipe
  (`references/vox.md` there).
- **Ground** warm grey paper #D9D7D1 with a light grid and printed grain; an orange progress bar.
- **Type** Montserrat 900 numbers and headlines; Merriweather newspapers; Bangers bubbles; Special Elite typewriter.
- **Motion** cut-outs rise and pop 2 to 4 frames before their words; counters land on their numbers; highlights sweep
  as words are said; a 3.5% push per beat with parallax.
- **Composition** one anchor picture per beat, then one new thing about every second; a foreground band hides the lower
  edge of people.
- **Signature** halftone people with an offset red marker stroke.
- **Kit parts** `Paper`, `Grain`, `Callout`, `HandMark`, `Counter`, `Marker`, `onTwos`; for footage beats, nexa-video-creator's vox overlays.
- **Transitions** hard cuts on one locked ground; a light leak at the end.
- **Sound** soft effects on the main motion only, a few dB under the voice.
- **Avoid** stock people in sensitive contexts, logos, a newspaper that puts words in a real outlet's mouth.

## Flat illustrated explainer
- **Use** children, education, NGOs, simple product stories, broad consumer audiences (Bangladesh included).
- **Theme** `playful` (Baloo Da 2 covers Bangla and Latin).
- **Ground** sky blue with soft shapes; white cards.
- **Type** Baloo Da 2 800 headlines; Nunito body.
- **Motion** 14-frame pops with `outBack`; `bouncy` springs for heroes; float on objects; a little squash on landings.
- **Composition** big simple shapes, characters or icons, one idea a frame.
- **Signature** an object bounces in and speaks through a bubble.
- **Kit parts** `Blob`, `Card`, `Icon`, `HandMark`, `Float`; characters from remotion-broll.
- **Transitions** iris and slide.
- **Sound** ukulele or marimba; pops; a boing only once in a while.
- **Avoid** meme sounds, many bounces at once.

## Whiteboard sketch
- **Use** training, processes, strategy and how-it-works videos.
- **Theme** `whiteboard`.
- **Ground** white with a faint paper grain.
- **Type** Permanent Marker headings; Patrick Hand body; Caveat notes.
- **Motion** everything draws on (paths, arrows, circles); text writes on; `posterize` 2 or 3 for a hand-made feel;
  the camera travels across a board larger than the frame.
- **Composition** clusters of drawings on one big board.
- **Signature** an arrow draws from the problem to the answer.
- **Kit parts** `DrawPath`, `HandMark`, `Icon`, `Arrow`, `Camera` over a large board, `Typewriter`.
- **Transitions** camera moves instead of cuts.
- **Sound** a light bed; marker sounds only if subtle.
- **Avoid** gradients, glossy shadows.

## Corporate and finance
- **Use** banks, insurance, B2B services, investor updates, internal communication.
- **Theme** `corporate`.
- **Ground** cool grey with white panels and thin lines.
- **Type** IBM Plex Sans 700 and 400; tabular numbers or Plex Mono.
- **Motion** 20-frame rises on `outCubic`; calm springs; charts; slow camera moves.
- **Composition** clear margins, split panels, figure cards.
- **Signature** a key figure that counts up and anchors the scene.
- **Kit parts** `Card`, `Grid`, `BarChart`, `LineChart`, `Stat`, `ProgressRing`, `LowerThird`, `Counter`.
- **Transitions** slides and dissolves.
- **Sound** a corporate bed; subtle clicks.
- **Avoid** invented figures, stock handshakes, neon.

## Luxury and fashion
- **Use** fashion, jewellery, hotels, perfume, premium real estate.
- **Theme** `luxury`.
- **Ground** warm black, vignette 0.5, grain 0.06; gold hairlines.
- **Type** Cormorant Garamond 500 capitals with 0.18 em tracking; Manrope body, small.
- **Motion** 30-frame blur-ins on `outQuart`; holds of 3 s or more; slow push-ins; no bounce; rack focus between layers.
- **Composition** one product, much space, symmetry; full-bleed imagery with little type.
- **Signature** the name resolves out of a blur as the light reaches it.
- **Kit parts** `KineticTitle` (blur), `Vignette`, `Grain`, fx `FilmLook` or `DreamyLook`, `KenBurns`.
- **Transitions** slow dissolves; dips to black.
- **Sound** strings or ambient; a single soft shimmer.
- **Avoid** fast cuts, bright colours, glitch.

## Cinematic trailer
- **Use** documentaries, films, series, events with drama.
- **Theme** `trailer`.
- **Ground** black; 2.39:1 letterbox; grain 0.1; vignette 0.55; light leaks.
- **Type** Cinzel 700 capitals with 0.12 em tracking; title cards held 2 s or more.
- **Motion** 36-frame fades on `sine`; push-ins on stills and footage; flash cuts on hits; a riser into the title.
- **Composition** image shots alternating with title cards; the big title and the date at the end.
- **Signature** a line of copy that splits the trailer into before and after, on a hit.
- **Kit parts** fx `LightLeak`, `FilmLook`, `tr.lightLeakCross`; `Letterbox`, `KenBurns`, `TitleCard`, `PushIn`, `Shake` on hits.
- **Transitions** dips to black, light-leak crosses, flash cuts.
- **Sound** drone, hits, riser, silence before the title.
- **Avoid** bouncy motion, UI, too much text.

## Neon night
- **Use** music, gaming, nightlife, tech events.
- **Theme** `neon`.
- **Ground** ink blue with a glowing horizon or grid; vignette 0.4.
- **Type** Unbounded 700; Space Grotesk body.
- **Motion** 16-frame blur-ins; bounded glow pulses; light sweeps; camera drift.
- **Signature** one line of light that draws the path of the story.
- **Kit parts** fx `fx.glow` and `fx.chromaticAberration`, `Gradient`, `Mesh`, `EffectGround` (synthwave floor), `DrawPath`.
- **Transitions** zoom-through; one glitch cut.
- **Sound** synthwave.
- **Avoid** glow on everything (one glowing element per shot), thin text on dark.

## Eighties retro and VHS
- **Use** nostalgia campaigns, music, gaming, playful brands.
- **Theme** `retro`, with the `fx` VHS or CRT look.
- **Ground** a purple gradient with a sun or a grid horizon; scanlines; tape noise.
- **Type** Rubik Mono One capitals; VT323 for timecodes and UI.
- **Motion** pops with `outBack`; motion on twos; tracking glitches at transitions.
- **Kit parts** fx `VhsLook`, `CrtLook`, `GlitchLook`; `Gradient`, `Pattern`, `onTwos`.
- **Sound** synth-pop; tape stops.
- **Avoid** artefacts over text that must be read.

## Terminal and developer
- **Use** developer tools, APIs, open source, technical tutorials.
- **Theme** `terminal`.
- **Ground** GitHub-dark with windows.
- **Type** JetBrains Mono; the focus line at least 28 px at 1080.
- **Motion** commands type in linearly; output lines appear; code lines highlight; the caret blinks as a stepped value.
- **Kit parts** `Terminal`, `CodeBlock`, `MacWindow`, `Typewriter`.
- **Transitions** hard cuts; window slides.
- **Sound** light typing (sparingly); soft blips.
- **Avoid** fake outputs that claim real results, unreadable code.

## Brutalist
- **Use** fashion streetwear, art and culture, bold startups.
- **Theme** `brutalist`.
- **Ground** flat grey, black rules 4 to 8 px, colour blocks.
- **Type** Archivo Black capitals; Space Grotesk body.
- **Motion** 10-frame snap slides; hard cuts; deliberate overlaps.
- **Kit parts** `Grid`, `Card` (outline), `Animate` with `left`/`right` slides, `BigStatement`.
- **Sound** punchy beats; hard stops.
- **Avoid** soft shadows, gradients, rounded corners.

## Bangla-first
- **Use** Bangladeshi audiences, local brands, Bangla voice-overs.
- **Theme** `dhaka` (or any theme with its Bangla font).
- **Type** Anek Bangla 800 headlines; Hind Siliguri 500 body; Bengali digits (০ to ৯) in Bangla copy.
- **Motion** 16-frame rises; words (never letters) reveal; counters in Bengali digits.
- **Copy** `natural-copy` with the BD locale; voice from `nexa-speech`.
- **Kit parts** `KineticTitle` (word split), `Counter` with Bengali digits and lakh grouping, `TikTokCaptions` in Bangla.
- **Avoid** splitting Bangla into characters, West Bengal spellings in Bangladeshi copy, flag clichés.

## Lyric video
- **Theme** `kinetic` for energy, `editorial` for ballads.
- **Motion** each line enters on its sung word; one emphasised word per line; cuts on the beat; the ground changes per
  section (verse, chorus).
- **Kit parts** `KineticTitle`, `TikTokCaptions` (karaoke) timed from the song's word timings, `OnBeats`, `BeatPulse`, `Shake` on drops.
- **Sound** the song only.
- **Avoid** the whole lyric at once; lines shorter than their reading time.

## Audiogram
- **Theme** `midnight` or `studio`.
- **Layout** 1080x1920 or 1080x1080: title at the top, the speaker's photo, a waveform, captions.
- **Kit parts** `Audiogram`, `AudioWave`, `AudioBars`, `TikTokCaptions`, `Card`.
- **Sound** the clip at -16 LUFS; no music under speech unless the show has it.
- **Avoid** a waveform that does not come from the real audio.

## Captioned talking-head short
- **Theme** any, for captions and accents; the footage stays the hero (cut it with `nexa-video-creator`).
- **Captions** 2 to 4 words a page, the active word highlighted, inside the safe area at about 60 to 65% height, clear
  of the face.
- **Motion** punch-ins on key words (scale 1.08 in 5 frames); b-roll cutaways on nouns; one lower third.
- **Kit parts** `TikTokCaptions`, `Clip`, `PictureInPicture`, `JumpCuts` (+ `remapCaptions`), `LowerThird`.
- **Avoid** engagement-bait endings; captions over the face or the platform's buttons.

## Documentary and news
- **Theme** `corporate` or `trailer`; `data` for explainer segments.
- **Kit parts** `LowerThird` (minimal), maps `WorldMap` and `Pin`, `KenBurns` with sources, `Quote`.
- **Motion** calm; no bounce; long holds on quotes.
- **Avoid** dramatised real people, unsourced claims, fake mastheads.

## Map story
- **Theme** `data` (day), `neon` (night flights) or `studio`.
- **Kit parts** maps `WorldMap` (camera keys), `MapZoom`, `Route`, `Pin`, `Globe`, `Choropleth`; `Label`.
- **Motion** zooms of 30 to 45 frames in-out; routes draw at an even speed; the vessel or plane turns along its path.
- **Avoid** borders that are disputed without context; city positions not taken from a source.

## 3D product hero
- **Theme** `keynote`.
- **Kit parts** three `Scene3D`, `ProductSpin`, `CameraPath`, `Text3D` or a CSS title over calm space.
- **Motion** a slow turn that eases in and out; a camera move of 60 frames or more.
- **Render** with `--gl=angle`; check for blank frames; keep geometry light.

## Paper stop-motion
- **Theme** `vox` or `playful`.
- **Kit parts** `Paper`, `Grain`, fx `StopMotionLook`, `onTwos`; cut-outs from nexa-video-creator.
- **Avoid** smooth 60 fps movement on paper elements (it breaks the illusion).

## Glitch and cyber
- **Theme** `neon` or `kinetic`.
- **Kit parts** fx `GlitchLook`, `tr.glitchCut`, `fx.scanlines`, `tr` pixel dissolve; hard cuts.
- **Avoid** glitching text that must be read; more than three flashes a second (a seizure risk).
