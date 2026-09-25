---
name: nexa-remotion
description: "Makes any video in code with Remotion, start to finish, like a motion design studio: explainers, product launches and SaaS promos, app demos, kinetic typography, data stories and charts, map and route stories, social shorts and reels with captions, ads, trailers, lyric videos, audiograms, logo stings, 3D product scenes and Vox-style collages, in any look (20 ready themes and a catalogue of named styles). It plans the treatment and a storyboard timed to the voice or the beat, builds scenes from a tested kit of components, checks stills and renders, measures the file and delivers. Use it for any request for a video, animation, motion graphics or explainer made with Remotion or in code, Banglish included ('remotion diye video banao', 'motion graphics banao', 'promo video lagbe', 'explainer animation koro'). It directs the nexa-remotion-* sub-skills."
---

# nexa-remotion

The director of the nexa-remotion family. Claude is the motion designer, editor and producer; the **kit** is a
tested component library for Remotion 4.0.528 (themes, motion, type, design, graphics, UI, maps, 3D, effects,
transitions, editing); **nrk.py** makes projects, renders stills and videos, and checks them. Everything is decided
from the brief and measured, so the user is involved only where a decision is really theirs.

Command prefix: `python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py`

## Fast path (every video request)

1. **Intake: decide, do not interrogate.** Platform and format, length, audience, the one message, voice (who, which
   language), music, brand (colours, fonts, logo), facts and assets. Take what the brief and the client's material
   give; pick sensible defaults for the rest and state them in one line. Ask only what nobody can decide for the
   user (for example the product's real price).
2. **Treatment.** Pick the look from `nexa-remotion-styles` (a theme plus grounds, type, motion character and sound)
   and name one signature move that repeats two or three times. For client work write three directions that differ
   on at least four dials (energy, density, ground, depth, camera, type, texture, colour), then keep one.
3. **Words.** On-screen text and the voice-over script with the `natural-copy` skill (for the ear: one idea per
   breath, numbers as people say them). Only the client's facts; every number on screen is said or sourced.
4. **Voice first.** Record or synthesise the voice (`nexa-speech`), get word timings (`nexa-video-creator`'s
   `nvc.py transcribe --engine whisper`), and write the cue table: which word triggers which element. Music from
   `nexa-sound`; a beat grid only when the track is really rhythmic. Durations come from the audio, not guesses.
5. **Storyboard.** A shot list with frame arithmetic (`references/storyboard.md`): each scene's start frame, length,
   hero element, cue words, composition system and transition; the sum checked against the promised length.
6. **Build.** `nrk.py new PROJECT --format youtube --seconds 30`, then one file per scene in `src/scenes/`, composed
   in `src/Main.tsx` with `<Series>` or the fx `Scenes` helper. Use kit components first, raw Remotion where the kit
   has nothing. Brand with `makeTheme()`.
7. **Look, act by act.** `nrk.py stills PROJECT` after each act; read every contact sheet, render dense frames full
   size with `nrk.py still`, fix, repeat. Then `nrk.py render PROJECT --preset draft` and watch it with the
   `agy-watch-video` skill (`watch --goal motion`), fix.
8. **Independent review.** A fresh reviewer (the `remotion-reviewer` agent) that never saw the plan judges held
   frames and motion frames and lists problems by severity; fix every high and medium one.
9. **Deliver.** `nrk.py render PROJECT --preset web` (plus the 9:16 or other variants), `nrk.py qa PROJECT`,
   loudness on the file, and a delivery note: files, what was verified (with counts), what was not.

## Who does what (routing)

| The job needs | Skill |
|---|---|
| Timing, easing, springs, choreography, stagger, camera moves, parallax, motion blur, holds and pacing | `nexa-remotion-motion` |
| Kinetic text, titles, typewriters, counters, fitting text, highlights, captions and subtitles, Bangla type | `nexa-remotion-type` |
| Grounds, gradients, grain, paper, patterns, cards, glass, layout grids, colour, safe zones, brand kits | `nexa-remotion-design` |
| Charts, numbers, diagrams, timelines, path drawing and morphing, icons, hand-drawn marks | `nexa-remotion-graphics` |
| App and web demos, cursor, devices, code, terminal, chat, toasts, lower thirds, title and end cards, logo reveals | `nexa-remotion-ui` |
| World and country maps, highlights, zooms, routes and flights, pins, globes, choropleths | `nexa-remotion-maps` |
| 3D scenes, product turntables, 3D text, particles, camera paths | `nexa-remotion-3d` |
| Effects, film and retro looks, glitch, masks, keying, light leaks, transitions between scenes | `nexa-remotion-fx` |
| Footage and sound: clips, trims, speed, jump cuts, split screens, picture in picture, music ducking, sound effects, visualisers | `nexa-remotion-edit` |
| Render settings, formats, transparency, GIFs, speed, Lambda and cloud, licences, render errors | `nexa-remotion-render` |
| Choosing a look: named styles with their theme, components, motion and sound | `nexa-remotion-styles` |
| Editing real recordings (sync, transcript cuts, b-roll, Vox beats over footage) | `nexa-video-creator` |
| Caricature character B-roll | `remotion-broll` |
| Voice-over (TTS, Bangla included), music and sound effects | `nexa-speech`, `nexa-sound` |
| Images to animate (products, scenes, cut-outs) | `codex-imagegen` |
| Words on screen and scripts | `natural-copy` |
| Watching and measuring the render | `agy-watch-video` |
| Raw Remotion API detail beyond our references | the official `remotion-best-practices` family, then `references/kb/` |

## The kit

A project made with `nrk.py new` gets its own copy in `src/kit/` (update it later with `nrk.py sync`). Import the
light modules from `./kit` and the special ones by path: `./kit/fx` (looks and transitions), `./kit/maps`,
`./kit/three`. Every module has a README with every prop and a demo per component (`nrk.py demos --module NAME`).

| Module | Main parts |
|---|---|
| `core` | `useStage()` (size, fps, `unit`, safe area), `SafeArea`, `SafeGuides`, `Stage`, 20 themes, `ThemeProvider`, `makeTheme`, `useTheme` (colours incl. `accentText`/`onAccent` at 4.5:1, resolved font stacks), 45 fonts (`loadKitFont`, `fontStack`, `useFontsReady`), `curves`, `springs`, `appleSpring`, `rand`, `shuffle`, `beatGrid`, `snapToBeat`, `readingFrames`, `at30` |
| `motion` | `Animate` (19 reveals, exits end on the Sequence's last frame), `Stagger`, `Camera` + `Parallax`, `ZoomAt`, `PushIn`, `Shake`, `Float`, `MotionBlur`, `Trail`; `ramp`, `track`, `inHoldOut`, `springAt`, `useLife`, `frameAtProgress`, `wiggle`, `pulse`, `inertia`, `onTwos`, `moveFrames` |
| `type` | `KineticTitle`, `SplitText`, `Typewriter` (+ `KeySounds`), `Scramble`, `WordRotator`, `Counter` (Bengali digits, lakh grouping, odometer), `FitText`, `Marker`, `Annotate`, `TextPlate`, `BigStatement`, `Quote`, `Kicker`, `Label`, `LineStack`, `TikTokCaptions`, `BoxedCaptions`, `SubtitleFile`, `toCaptions`, `remapCaptions` |
| `design` | `Ground`, `Gradient`, `Mesh`, `EffectGround`, `Paper`, `Finish`, `Grain`, `Vignette`, `Pattern`, `Spotlight`, `LightSweep`, `Card`, `Pill`, `Badge`, `Scrim`, `Frame`, `Panel`, `Grid`/`Cell`, `Stack`, `Center`, `Split`, `StatSplit`, `FullBleed`, `Blob`, `Ring`, `Squiggle`, colour helpers (`mix`, `contrast`, `readableOn`, `ensureContrast`, `brandTheme`) |
| `graphics` | `BarChart`, `LineChart`, `Donut`, `BarRace`, `Sparkline`, `Stat`, `ProgressRing`, `ProgressBar`, `Comparison`, `ChartFrame`, `Timeline`, `FlowDiagram`, `OrgChart`, `DrawPath`, `PathFollow`, `Morph`, `Arrow`, `HandMark`, `Marked`, `Callout`, `Icon` (49), `IconBadge`, number formatting |
| `ui` | `Cursor`, `TapIndicator`, `ClickSounds`, `Pressable`, `UiButton`, `Toggle`, `SearchBar`, `FormField`, `BrowserWindow`, `MacWindow`, `PhoneFrame`, `LaptopFrame`, `DeviceRise`, `ScrollView`, `CodeBlock`, `Terminal`, `ChatThread`, `Notification`, `LowerThird`, `TitleCard`, `SectionTitle`, `EndCard`, `LogoReveal`, `Subscribe`, `ChapterBar`, `Countdown`, `FocusRing`, `UiIcon` (62) |
| `edit` | `Clip`, `KenBurns`, `JumpCuts` (+ `keepRanges`, `remapWords`), `SpeedRamp`, `TimeRamp`, `SplitScreen`, `PictureInPicture`, `LayoutSwitch`, `Letterbox`, `Voice`, `Music` (ducking), `Sfx`, `AudioBars`, `AudioWave`, `AudioCircle`, `Audiogram`, `OnBeats`, `BeatPulse` |
| `fx` (by path) | `fx.*` (36 clamped effect presets), `FilmLook`, `VhsLook`, `CrtLook`, `NewsprintLook`, `NoirLook`, `DreamyLook`, `GlitchLook`, `StopMotionLook`, `TextMask`, `ShapeMask`, `WipeMask`, `ChromaKey`, `BlendVideo`, `LightLeak`, `Starburst`, `Shine`, `Scenes` + `tr.*` (fade, slide, wipe, iris, pushCut, 12 shaders, zoomThrough, whipPan, glitchCut, lightLeakCross, blurDissolve, maskReveal) |
| `maps` (by path) | `WorldMap` (camera keys, auto projection, always sharp), `MapZoom`, `Globe`, `CountryShape`, `Route`, `Pin`, `CountryLabels`, `Choropleth`, `Legend`, `GeoLayer`, `useMap` |
| `three` (by path) | `Scene3D`, `CameraPath`, `Turntable`, `ProductSpin`, `Phone3D`, `Card3D`, `Text3D` (Bangla too), `Particles`, `FloatingCards`, `Model`, `VideoPlane`, `Bloom`, `Floor`, `Svg3D` (no WebGL) |

## Project anatomy and code rules

- `src/Root.tsx`: one `<Composition>` per deliverable (a 16:9 master and a 9:16 variant share scenes and timing);
  size, fps and length inline; props with inline `defaultProps` (and a Zod schema when a client will edit them).
- `src/Main.tsx` composes `src/scenes/*.tsx`; one scene per file; constants for the cue table at the top.
- Assets in `public/`, loaded with `staticFile()`; never absolute paths, never remote files at render time (copy
  them in).
- Deterministic: everything from `useCurrentFrame()`, seeded randomness, no CSS animations or timers; clamp every
  interpolation; `delayRender` for async work; `premountFor` on Sequences with media.
- Sizes are px at 1080 times `unit`; text inside `safe`; colours and fonts from the theme.
- Keep scene timing literal and inline where a person may fine-tune it in Studio.

## Timing that reads as professional (30 fps)

- Entrances 8 to 11 frames for small UI, 15 to 20 for cards and lines, 18 to 28 for calm or premium looks; exits
  shorter (12 to 18) with ease-in, or none (cut on a settled frame). Never scale from 0; never opacity alone.
- Stagger 2 to 4 frames within one gesture, 5 or 6 for a list; the whole run lands before the next cue word.
- Hold settled text at least `readingFrames(text)` (about 0.33 s a word plus 0.3 s, never under 1.2 s), and 30 to
  45 frames before any exit. Text is perfectly still while read; the camera or the ground may drift.
- A new beat every 3 to 9 s, something new inside a beat every 2 to 4 s, nothing fully static over 3 s, one focal
  move at a time. First cuts are nearly always too fast: when unsure, hold longer.
- Frame 0 is the poster: open composed and legible (no fade from black on social).
- With transitions, total length = sum of scenes minus sum of transitions; each scene lasts at least as long as the
  transitions touching it.

## Quality gates (all before delivery)

1. `npx tsc --noEmit` is clean; every scene renders its stills; no font falls back (look at the letterforms).
2. Every text and logo inside the safe area of every delivered format; minimum text 32 px at 1080 (captions about
   56 px for phones); contrast at least 4.5:1 for small text.
3. No slideshow (everything arrives at once, then nothing moves) and no screensaver (everything drifts forever).
4. Nothing half-visible at a cut or on the last frame; no jumps between frames (check stills 1 frame apart at cuts).
5. Every number said or sourced; no invented people, reviews, logos or UI a client does not have.
6. Sound: voice loudest, bed quiet, one effect per event, -14 LUFS and true peak at most -1 dBTP on the file (web).
7. `nrk.py qa` passes for the platform; the reviewer has no high or medium findings left.

## Commands

| Command | Does |
|---|---|
| `doctor [--link-modules PATH]` | checks node, ffmpeg, the shared Remotion 4.0.528 modules and extras |
| `setup` | installs the kit's modules once into `~/.nexa-remotion/modules` (a new machine) |
| `new PROJECT --format F --fps 30 --seconds N` | a project: the kit library, a starter scene, linked modules; formats youtube, 4k, shorts, reels, tiktok, story, feed, square |
| `stills PROJECT [--comp Main] [--every 1.5 or --frames 0,45,90] [--guides]` | frames on one labelled contact sheet (`--guides` draws the format's safe area on each) |
| `still PROJECT --frame N` | one full-size PNG (thumbnails, close looks) |
| `render PROJECT --preset web|upload|draft|master|alpha|webm-alpha|gif` | renders with the right codec, colour space and GL settings (`upload`: CRF 12 for YouTube and Vimeo, so flat graphics survive the re-encode) |
| `qa PROJECT` | measured checks of the last render (agy-watch-video) |
| `demos [--module M] [--only X]` | typechecks the kit and renders its demos (the kit's own test) |
| `sync PROJECT` | updates the project's copy of the kit (the old copy is kept) |

`npx remotion studio` inside a project opens the Studio for hand tweaks.

## When things break

| Symptom | Fix |
|---|---|
| Text in a fallback font | load it through the kit (`loadKitFont`, `fontStack` or the theme); a CSS name alone loads nothing |
| Blank WebGL, effects or 3D | render with `--gl=angle` (nrk does); `swangle` on a machine without a GPU |
| Flicker or values that differ between frames | something reads the clock or `Math.random`, or state builds up across frames |
| `inputRange must be strictly monotonically increasing` | keyframes computed from a duration shorter than the fades; guard short lengths |
| Render fails on an effect parameter | an unclamped interpolation pushed it out of range; clamp |
| Image-sequence render refuses the folder | the output path has a dot somewhere; use a relative path inside the project (nrk does) |
| Video letterboxed despite `objectFit` in CSS | use the `objectFit` prop of `@remotion/media` `<Video>` |
| A timeout in `delayRender` | a loader never finished; check the asset path and CORS, raise the timeout only after that |

More in `nexa-remotion-render` and `references/kb/`.

## References

- `references/process.md`: the full workflow with its gates, the three directions, the reviewer loop and the
  delivery note.
- `references/storyboard.md`: intake sheet, treatment, shot list with frame arithmetic, cue table.
- `references/quality.md`: the quality bar: motion, text, composition, anti-slop list, sound, checks.
- `references/platforms.md`: sizes, safe zones, lengths, loudness and codecs per platform.
- `references/remotion-core.md`: how Remotion works and the core API on 4.0.528, in one place.
- `references/prompting.md`: writing a precise video brief for yourself or for a sub-agent.
- `references/field-notes.md`: what three real builds taught (layout, frozen-picture QA, sound tails, Bangla,
  maps, tooling), measured on their renders.
- `examples/`: the sources of those three videos (a Bangla vertical tip video, an English map story, a SaaS launch):
  real, tested scene code to start from.
- `references/kb/`: the research behind the family (every docs page, the source, the examples, the community),
  one file per area, with an index.
- `kit/CONVENTIONS.md`: the rules for writing new kit components.
- `agents/`: the `remotion-director` and `remotion-reviewer` agent definitions.
