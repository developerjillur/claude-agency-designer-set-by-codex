# The workflow, gate by gate

Each gate produces evidence (a file, a sheet, a measurement) before the next starts. The order matters: a flow
problem found after the build costs a rebuild; found in the storyboard it costs a line.

## 1. Intake

Fill the intake sheet in `storyboard.md`. Read it from the brief and the client's material first: their site,
product, brand files, earlier videos, the platform. A pre-filled plan the user can correct beats an interview.

Defaults when nothing says otherwise:

| Question | Default |
|---|---|
| Platform | YouTube 16:9 1920x1080 at 30 fps; add a 9:16 variant when the brief mentions social |
| Length | explainer 60 to 120 s; promo 20 to 40 s; short 15 to 45 s; logo sting 4 to 6 s |
| Voice | a voice-over when the message needs sentences; none for a loop, a sting or a UI feature loop |
| Music | a quiet bed under a voice; the driver for a promo or lyric video without a voice |
| Language | the audience's (global by default; Bangla only when the audience is Bangladeshi or the brief says so) |
| Look | the style closest to the brand and the audience (`nexa-remotion-styles`) |

Never invent facts, prices, results, testimonials, customer names or UI the client does not have. Placeholders are
visible and listed in the delivery note.

## 2. Treatment

- A physical scene sentence decides light or dark ("a clean desk in daylight", "a stage in a dark hall"); never
  default silently to dark.
- **Three directions** for client work. Each is a paragraph plus its dials: energy, density, ground, depth, camera,
  type, texture, colour, product presence, sound. They differ on at least four dials. If one matches a stock example
  (a template's look), drop it first. Keep the one that fits the audience and the message; say why in one line.
- **One signature move** that expresses the product's verb (a card that snaps into a stack for "organise", a route
  that draws for "deliver"), used two or three times, never in every scene.
- **Composition systems**: adjacent beats use different ones (full-bleed image with scrim, oversized type, horizon
  world, asymmetric offset hero, split with a hard seam, rising surface, full-screen singles), with one palette, one
  type voice and one light language across the film.

## 3. Words

On-screen copy and the script go through `natural-copy` (copylint at least; copyjudge for client finals). For the
ear: 8 to 14 words a breath, about 2.5 words a second, numbers as they are said, the brand and the ask said twice.
On screen: key words and numbers, never the sentence being said (captions are the exception).

## 4. Voice, timing and music

1. Voice: `nexa-speech` (TTS, Bangla included) or the client's recording. One file per line or one take per
   argument.
2. Word timings: `python3 ~/.claude/skills/nexa-video-creator/scripts/nvc.py transcribe JOB --engine whisper`, or
   the TTS engine's own timestamps. Convert to frames once and keep the table in the scene file as constants.
3. Scene lengths = measured voice + 0.2 to 0.5 s tail hold (+ transition overlap).
4. Cue the meaning (the verb or the emphasis word): readable elements land 1 or 2 frames before their word, hits
   land exactly on it. One beat carries at most two cues; weight reveals to the back half of a shot.
5. Music: `nexa-sound` (a bed, or a track to cut to). Beat sync only when the track is really rhythmic: cuts on
   downbeats, small events snapped to the nearest beat within 6 frames (`snapToBeat`), at most three whole-frame hits
   per film. Motion size never follows the beat.

## 5. Storyboard

The shot list in `storyboard.md`: scene, start frame, length, what the viewer sees (the hero element), the copy
verbatim, cue words, composition system, motion, transition, sound. Show the sums. Get the flow right here: it is the
one defect the edit cannot fix.

## 6. Build

1. `nrk.py new PROJECT --format youtube --seconds 75 --title "..."`.
2. Theme: `makeTheme('studio', {colors: {accent: '#...'}, fonts: {display: 'Manrope'}})` from the brand, in one
   `theme.ts`, given to `<ThemeProvider>` in `Main.tsx`.
3. One scene per file in `src/scenes/`, each a component that fills the frame and assumes frame 0 is its start.
   Compose in `Main.tsx` with `<Series>` (hard cuts) or the fx module's `Scenes` (transitions).
4. Probe shared systems first (the camera rig, a layout grid, a custom component) with one small scene and its
   stills, before building everything on them.
5. Build act by act: stills of each act, look, fix, then the next act.

## 7. Look

- `nrk.py stills PROJECT --every 1 --guides` for an act (the safe area drawn on every frame), `--frames` for exact beats (the frame a cue lands and 12 frames
  later). Read the sheet. Contact sheets misjudge scale: render dense or detailed frames full size with
  `nrk.py still` and look again.
- `nrk.py render PROJECT --preset draft` and watch it with agy-watch-video: `watch VIDEO --goal motion --depth
  quick` for flow, `ask VIDEO "..." --at T` for a moment, `verify` for a claim that matters.
- Check what stills cannot show: speed, smoothness, rhythm, sound against picture.

## 8. Independent review

Use the `remotion-reviewer` agent (or any fresh agent) with only the rendered file or stills and the brief's
audience and platform, never the design notes or the code (a reviewer who knows the intent sees the intent, not the
frame). It reads held frames at full size, treats mid-motion frames as motion only, crops at least three dense areas
per round, and reports findings with a severity (high, medium, low). The builder fixes, or rebuts with pixel
evidence. Same reviewer across rounds; stop when no high or medium finding remains, or after three rounds (then
change the material, not the cut).

After the look converges, a **tempo pass**: a fresh agent rebuilds the beat timetable from the code and fixes dwell
times (reading time, holds, pacing) inside the promised length, without touching the design.

Model judges are advice: never let one waive a failed measurement.

## 9. Deliver

1. `nrk.py render PROJECT --preset web` for each deliverable (and `master` or `alpha` when an editor needs them).
2. `nrk.py qa PROJECT --platform ...`; loudness measured on the file (ffmpeg ebur128): -14 LUFS integrated, true peak
   at most -1 dBTP for web platforms.
3. The delivery note:
   - the files (path, format, size, length);
   - what was verified, with counts ("38 stills of 2,250 frames looked at, QA passed for YouTube, loudness -14.1 LUFS");
   - what was not verified (audio by ear, full-rate motion on a phone, platform compression, a fact the client must
     confirm);
   - disclosures: a synthetic voice or AI images where the platform or the law asks for it;
   - licences: music and sound effect sources, stock, fonts (Google Fonts are OFL), and the Remotion licence
     (free for individuals and companies of up to 3 people; above that a Company License is needed).
4. Keep the project and every render; never overwrite the only copy of a delivered file.
