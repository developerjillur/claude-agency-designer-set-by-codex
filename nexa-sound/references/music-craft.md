# Music craft for video

How to ask Lyria for music that works under picture, how the fit works, where levels sit, and how to time effects.
Sources are listed at the end with their dates. Anything not tried against the live service is marked untested.

## 1. Writing the prompt

Google's structure for Lyria prompts: genre and era, mood, instruments, tempo and rhythm, vocals and language,
lyrics; optionally structure, soundscape and production words ("clean mix"). The templates in `scripts/moods.json`
follow it, and `brief` fills them from the edit.

| Works | Weak or ignored |
|---|---|
| A genre with its era, 3 to 5 named instruments, BPM, key, mood words | Negative prompts ("no drums"): not supported on Lyria 3 and 3.5. Say what you want instead, and end with "Instrumental." |
| Timestamped sections with an intensity: `[0:21 - 0:37] Reveal: fuller drums. Intensity: 6/10` | Artist, band, song or album names: blocked or diluted, and against Google's policy. Describe the sound. |
| "Instrumental." as the last word | Sample-accurate timing: expect a few hundred ms of slack; `fit` measures the real beats |
| Steady-energy words for beds: "one steady groove, consistent energy, no build-up" | Mixing words (EQ, LUFS, sidechain): do them in post (`mix`) |
| An explicit ending: "a final chord that rings out by 47 seconds", or "one final hit at 44 seconds" | Output loudness: not controllable; `mix` sets it |
| RealTime: short keyword prompts with weights | Lyrics in Bengali: not among the 8 supported lyric languages (EN, DE, ES, FR, HI, JA, KO, PT); try a draft first |

Recipes:
- **No vocals:** keep the "Instrumental." ending, and QC anyway: timed lyric lines in the answer fail the take,
  and `qc --listen` asks a judge. RealTime is instrumental by design.
- **A loopable bed:** RealTime (no song arc, exact length), or ask Lyria 3.5 for "one steady groove from start to
  finish, consistent energy, no build-up, no breakdown", then `loop` or `fit` from the steady middle.
- **A clean ending:** "End on a single sustained final chord that rings out naturally by {DUR} seconds." For ads:
  "a final punchy hit at {DUR-1} seconds, then a short natural tail". Clip drafts always stop at 30 s: treat that end
  as abrupt; `fit` ends it on a downbeat with a fade.
- **A riser into a drop on a cut:** "A rising synth sweep and snare roll from 0:10 to 0:14; the beat drops at exactly
  0:14", with 0:14 on the reveal cut. Then measure: `fit --cuts` lines the downbeats up with the cuts.
- **Under dense voice-over:** "sparse, supportive arrangement, simple chords, no prominent lead melody", intensity 2
  to 4 in narrated spans (`brief` does this from the speech spans). Duck in post anyway.
- **Transitions:** section boundaries on scene changes ("[0:18 - 0:30] Lift: drums get fuller, add strings.
  Intensity: 7/10"). For a hard change of genre, crossfade two tracks at a cut and hide the seam with a whoosh.
- **Images:** 1 to 3 key frames with `--images`: Lyria 3.5 reads mood and colour from them (untested here).
- **Logo sting:** a Clip draft with "[0:00 - 0:04] one bold brass and timpani sting, final hit at 0:02, natural
  reverb tail. [0:04 - 0:30] a quiet sustained pad.", then cut 0:00 to 0:04 on the decay (untested; the synthesiser's
  impact, boom or chime is the dependable fallback).

Bangladeshi and South Asian colour: Google's own keywords include "Bengal Baul", "Bhangra", "Indian Classical",
"Tabla" and "Sitar". Instruments by name work too: ektara, dotara, bansuri, harmonium, dhol, dhak, khol, mandira,
esraj, shehnai. Describe genres named after a person instead of naming them (they may trip the artist filter;
`brief` refuses them): "an early 20th century Bengali art-song feel with harmonium, esraj and tabla".

Lyria RealTime: short keyword prompts with weights ("Lo-Fi Hip Hop" 1.0, "Rhodes Piano" 0.7); changes take about
2 s to land; the first 5 to 10 s after start are unsettled (the recorder drops 8 s); BPM and key cannot change
mid-stream without a hard reset. `brief` writes automation from the sections (denser and brighter at reveals, drums
muted under dense narration); those values are starting points, untested against the live service.

## 2. Drafts, finals and reuse

1. `library --mood M --bpm 100-110` first: a take that passed QC costs nothing to reuse.
2. Drafts on Clip ($0.04, 30 s MP3) to choose the style; listen with agy-watch-video or `qc --listen`.
3. The final on Lyria 3.5 ($0.08) with the same brief, or a RealTime bed for exact length and no arc.
4. Pass rule: measured checks pass, no vocals in an instrumental, fit to the brief 7/10 or more, no abrupt ending
   after `fit`. Otherwise change the prompt and generate again, at most twice, then show the user the judge's notes
   and the two best takes.

A 60 s promo with 3 drafts and 1 final costs about $0.20. RealTime is free for now (an experimental model).

## 3. Fitting music to the picture

Editors keep the music's real ending and cut in the middle, on bar lines, where two bars sound alike; they loop a
steady stretch to make music longer; and they slide the start so the strongest cuts land on downbeats. `fit` does
the same with measurements instead of ears:

- the beat grid comes from onset strength (`beats.py`): on synthetic tracks at 82, 104 and 126 BPM it found the tempo
  exactly and every downbeat within 1.2 ms;
- bars are compared on their energy per beat in three bands; a cut or loop happens only where the bars match
  (within 3 dB), and whole phrases (4, 8, 16 bars) are preferred, because the energy cannot hear a broken chord cycle;
- every join is a one-beat equal-power crossfade starting on a downbeat, so the downbeats stay on one grid across
  the join (measured: within 1.4 ms);
- the last part under a bar is absorbed where it is least heard: a silent lead-in, the ring-out after the last hit,
  silence after a quiet ending, a tempo change of 3 % or less, a skip into the intro, or a fade on a downbeat;
- with cuts, the start moves up to 2 s to land the most weighted cuts within 80 ms of a downbeat.

Read `fit.json`'s `considered` to see the alternatives and their cost. When the result is not what the edit needs,
change the target by a bar, give `--cuts`, or generate with a length closer to the video.

## 4. Levels

Starting points, not standards (sources at the end):

| Element | Level |
|---|---|
| Dialogue and voice-over | the anchor: each set to -20 LUFS before the mix |
| Music under speech | 18 to 25 dB below the speech; `mix` sets 20 (`--music-under`). WCAG 2.x SC 1.4.7 asks for background sound at least 20 dB under speech, a good benchmark for video too |
| Music ducking depth | 12 to 15 dB below its music-only level (`--duck -14`) |
| Music alone (intro, outro, long gaps) | close to the dialogue level, a few dB under |
| Whooshes and risers | 6 to 12 dB under the dialogue (editing practice; OpenMontage puts effects between dialogue and music) |
| Impacts | briefly near the dialogue level |
| UI clicks and ticks in screen demos | 18 dB or more under |

The effect levels are each preset's default `gain_db`, applied to the effect's loudest 400 ms against the -20 LUFS
anchor. Change a cue's `gain_db` to taste; keep effects under the voice.

Ducking with a gain envelope from the speech spans, not a sidechain compressor: the envelope looks ahead (the music
is already down when the first word lands), holds steady through short pauses and is exact in dB, while a compressor
follows the voice's level, so the bed breathes with every word and swells between sentences. The same keyframes drive
Remotion's `volume` callback.

Loudness targets (integrated, true peak):

| Where | Target | Status |
|---|---|---|
| YouTube | -14 LUFS, -1 dBTP | YouTube turns loud content down to about -14; no official spec (Fora Soft, 2026-06-05) |
| TikTok, Instagram, Facebook | -14 LUFS is common practice, -1 dBTP | no published target |
| Spotify and podcasts there | -14 LUFS, -1 dBTP | first-party |
| Apple Podcasts | -16 LUFS, -1 dBTP | first-party recommendation |
| EBU R 128 broadcast | -23 LUFS, -1 dBTP | standard |

The master is always linear: a limiter first when the peaks need it, then two-pass `loudnorm` with `linear=true`,
verified with `ebur128`. A dynamic-mode result is never shipped silently.

## 5. Sound effects

Keep them few and tied to something on screen: about 8 designed effects in 18 s reads as designed, about 20 as
generic (browser-use's video-use notes). Every effect lands on a frame, measured from the file, not guessed:

| Kind | Align | Where it lands |
|---|---|---|
| hits, clicks, pops, UI tones | `attack` | its first sample within 30 dB of its peak on the frame |
| whooshes and swipes | `peak` | its loudest 10 ms 1 to 2 frames before the cut (default 1.5 frames at `--fps`) |
| risers | `end` | its climax on the cut (the synthesiser's riser peaks 0.25 s before its own end, then releases) |
| downlifters, booms, sub drops | `attack` | on the cut or the landing |

The synthesiser's presets (48 kHz stereo, 24-bit, peak -1 dBFS, deterministic by seed):

| Preset | Length | Sound |
|---|---|---|
| whoosh | 0.9 s | air rushing past: a swept pink-noise band, peak at 58 %, moving left to right |
| whoosh-short | 0.45 s | a quick bright whoosh for fast moves |
| swipe | 0.28 s | an airy upward flick with a faint rising tone |
| swoosh-down | 0.8 s | a band sweeping down with a sinking body, settling in the centre |
| pop | 0.16 s | a round pop: a sine dropping an octave in 30 ms |
| bubble | 0.3 s | a soft water bloop with a rising pitch |
| click | 0.05 s | a crisp interface click |
| tick | 0.045 s | a small dry tick for counters and steppers |
| key | 0.14 s | one keyboard key with its release |
| typing | 1.6 s | 8 to 10 keys a second with human timing and a lower spacebar |
| ding | 1.3 s | a clean glassy ding (bell partials that die faster than the fundamental) |
| chime | 2.2 s | a soft rising three-note chime |
| notify | 0.8 s | a friendly two-note notification |
| success | 0.95 s | a bright rising four-note arpeggio |
| error | 0.55 s | a soft descending two-note "uh-oh" |
| riser | 3.0 s | noise sweep, rising saw and speeding tremolo, widening, climax 0.25 s before the end |
| downlifter | 2.2 s | bright on the hit, then falling and narrowing |
| impact | 1.6 s | kick-like body, bright crack, low thump and a wide tail |
| boom | 2.6 s | a deep long boom with a wide low rumble |
| sub-drop | 2.0 s | a sine gliding down about two octaves |
| glitch | 0.5 s | a short digital stutter of blips, noise and held tones |
| shutter | 0.32 s | a camera shutter: open click, curtain, close click |
| sparkle | 1.5 s | tiny glassy grains on a pentatonic scale across the stereo field |

How they are made: sine and FM partials (every partial kept under 18 kHz, FM sidebands kept under Carson's bound),
noise through state-variable filters that stay clean while their cutoff sweeps, exponential envelopes, raised-cosine
starts and ends (no clicks), a DC-blocking high-pass, a gentle ceiling at 16 kHz on noise-based sounds, and stereo
movement that loses under 1 dB in mono. `--dur`, `--pitch` and `--brightness` change each one; `--seed` gives a
different take of the same sound.

## 6. Dialogue clean-up

The order matters: a high-pass first (rumble would drive everything after it), then noise reduction (a compressor
raises the noise floor, so reduce noise before it), then corrective EQ (less mud at 250 Hz, more presence at 4 kHz),
then de-essing if asked, then gentle compression. Loudness is set on the final mix, not per clip.

- `afftdn`'s noise floor is set from the recording; `nr` 10 to 15 dB sounds natural, 24 dB starts to smear.
- Hum: notches at the mains frequency and 3 harmonics (`--hum 50` in Bangladesh, Europe and most of Asia; 60 in the
  Americas).
- Every processor delays the audio: afftdn 25 ms, anlmdn 8 ms, Apple's voice isolation 56.3 ms (measured on an M4
  Max; EQ, high-pass, de-esser and compressor add none). The output length does not change, so the delay is invisible
  unless measured. `clean` removes it and proves the sync by cross-correlation (within 2 ms).
- Apple's voice isolation (the Audio Unit behind the Voice Isolation mic mode) is optional and undocumented by Apple
  for this use: re-check it after macOS updates. It is tuned for real speech.

## 7. QC

Measured checks come first and cannot be argued with: format, clipping (including flat tops from audio that clipped
and was turned down), loudness, silences inside the body, an abrupt ending, the tempo against the brief, DC offset and
the mono fold-down. A listening judge adds what measurements cannot hear: vocals in an instrumental, the mood, the
genre, how the sections and the ending feel. Gemini hears a 16 kbps mono downmix, so it cannot judge fidelity, the
stereo image or clipping. For client finals, run `qc --listen` (about a cent) or agy-watch-video on the fitted file.

## Sources

- Google, Generate music with Lyria 3.5 (updated 2026-09-23): https://ai.google.dev/gemini-api/docs/music-generation
- Google, Lyria prompt guide (updated 2026-09-17): https://ai.google.dev/gemini-api/docs/lyria-prompt-guide
- Google, Real-time music generation with Lyria RealTime (updated 2026-09-17):
  https://ai.google.dev/gemini-api/docs/realtime-music-generation
- Google Cloud, Ultimate prompting guide for Lyria 3 models (2026-04-08):
  https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-lyria-3-pro
- Google Cloud, Lyria 3 model page (capability table, updated 2026-09-24):
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3
- G. Vernade, Lyria RealTime: the developer's guide (2025-12-08):
  https://dev.to/googleai/lyria-realtime-the-developers-guide-to-infinite-music-streaming-4m1h
- Google, Audio understanding (updated 2026-09-23): https://ai.google.dev/gemini-api/docs/audio
- W3C, Understanding SC 1.4.7 Low or No Background Audio:
  https://www.w3.org/WAI/WCAG22/Understanding/low-or-no-background-audio.html
- browser-use, video-use SKILL.md (read 2026-09-25): https://github.com/browser-use/video-use
- OpenMontage, skills/creative/sound-design.md (read 2026-09-25): https://github.com/calesthio/OpenMontage
- Pure Audio Insight, background music level:
  https://pureaudioinsight.com/blogs/content-production/background-music-volume-how-loud-should-it-be
- Fora Soft, LUFS targets per platform in 2026 (2026-06-05):
  https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026
- EBU R 128 s2, Loudness in streaming (November 2023): https://tech.ebu.ch/docs/r/r128s2.pdf
- FFmpeg filter documentation (loudnorm, alimiter, acrossfade, afftdn, silencedetect): https://ffmpeg.org/ffmpeg-filters.html
