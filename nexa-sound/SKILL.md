---
name: nexa-sound
description: "Everything a video needs from sound: music from ElevenLabs (composition plans exact to the length, with a real ending) or Google Lyria (cheap drafts, finals, RealTime beds), ambience and room tone as seamless loops, sound effects from a built-in synthesiser (whoosh, riser, impact, click, typing and 18 more) plus ElevenLabs foley, Freesound CC0 and your own, fitting music to the picture (whole-bar edits, hits on cuts), voice isolation and dialogue clean-up proved in sync, ducking, a mix mastered to each platform's loudness, measured QC with a listening judge, and licence notes that keep free-plan output out of client work. Use it whenever a video, reel, ad, explainer or podcast needs music, a bed, ambience, sound effects, a cleaner voice, ducking, a mix or loudness, Banglish asks included ('music banao', 'background music lagbe', 'bgm add koro', 'sound effect dao', 'whoosh lagao', 'voice clean koro', 'noise komao', 'audio mix koro', 'loudness thik koro'). nexa-video-creator calls these commands; nexa-speech makes the voice-over stems."
allowed-tools: Bash(python3 ~/.claude/skills/nexa-sound/scripts/sound.py:*), Read
---

# nexa-sound

Music, effects, clean-up, ducking, mixing and QC for videos, with every step measured. The command prefix is
`python3 ~/.claude/skills/nexa-sound/scripts/sound.py`. Every flag and file format is in `references/cli.md`; prompt
craft, fitting, levels and effect timing in `references/music-craft.md`; licences in `references/licence.md`.

## Fast path (do exactly this)

Which engine does what (measured head to head on 2026-09-25, `references/cli.md` has the numbers):
- **Music:** ElevenLabs `music_v2_5` when the key reads a paid plan (exact to the length, a real ending, 16 s made
  in 5.3 s, judged 10/10); otherwise Lyria 3.5 (also 10/10 after `fit`). `generate` picks this on its own.
- **Ambience and room tone:** ElevenLabs loops (`ambience`, $0.02): the joins could not be heard.
- **UI sounds, whooshes, hits, risers:** the synthesiser (free, won or tied 5 of 6 against ElevenLabs).
- **Real-world foley** (a door, glass, rain, a crowd): ElevenLabs, as a cue with `query` and `source: elevenlabs`.
- **Voice isolation:** ElevenLabs on a paid plan (clarity 9, natural 8), else Apple's (7, 5).

A draft (a first cut, a placeholder bed):
1. `library --mood corporate --bpm 100-110 --passed`: reuse a take that passed QC before paying for a new one.
2. `brief --duration 45 --mood corporate --cuts edl.json --out music/brief.json` (free; `moods` lists the 12 moods).
3. `generate music/brief.json --out music` (ElevenLabs on a paid plan, $0.11 for 45 s; else a Lyria final, $0.08).
   For cheap style sketches first: `--engine lyria --draft 2` ($0.08, two 30 s MP3s).
4. `fit music/<id>_orig.<wav|mp3> --target 45 --cuts edl.json --out music/music_fit.wav`.
5. `sfx place cues.json --duration 45 --out sfx/sfx.wav --offline` (the synthesiser: no cost, no licence risk).
6. When the scene has a room: `ambience "quiet office room tone, distant keyboard" --duration 45 --out sfx/room.wav`.
7. `mix --voice vo_48k.wav --music music/music_fit.wav --sfx sfx/sfx.wav [--ambience sfx/room.wav] --platform youtube
   --out mix.wav`.
8. `qc mix.wav`: exit 0 means every measured check passed.

A client final adds: `qc music/music_fit.wav --listen` (a Gemini listening judge, about $0.01) or agy-watch-video on
the file for a free listen, `clean --isolate` on any camera or microphone dialogue before the mix, and
`credits . --out CREDITS.txt --strict` in the delivery (exit 1 when anything came from a free or unknown ElevenLabs
plan). Pass rule: measured checks pass, no vocals in an instrumental, fit to the brief 7/10 or more, no abrupt
ending. If a take fails, change the brief and generate again at most twice (or switch engine with `--engine`), then
show the user the judge's notes and the two best takes. Run anything that calls Lyria or ElevenLabs music with Bash
`run_in_background: true`: a Lyria final can take minutes.

## Commands

| Command | What it does |
|---|---|
| `doctor [--live]` | ffmpeg filters, key sources (names only), uv and the RealTime venv, swiftc, media-use and `NEXA_SFX_DIRS`; `--live` (free): which Lyria models the key's project sees, and the ElevenLabs plan |
| `moods` | the 12 mood templates (corporate, tech, cinematic, inspirational, lofi, vlog, ad, luxury, suspense, playful, wellness, bangla-folk) |
| `brief --duration S --mood ID [--cuts F] [--speech F] [--bpm N] [--key K] [--vocals] [--notes T] --out F` | the Lyria prompt: length plus 2 s, sections from the cuts with intensities (narrated 2 to 4, reveals and calls to action 6 to 8), the drop on the heaviest cut, "Instrumental." last; refuses artist, song and album names and says why |
| `generate BRIEF --out DIR [--engine auto\|elevenlabs\|lyria] [--draft N \| --final \| --realtime \| --takes N] [--budget USD]` | ElevenLabs takes from a composition plan (sections at their exact lengths, an ending of its own), drafts on Lyria 3 Clip, finals on Lyria 3.5, beds on Lyria RealTime; read-only originals, sidecars, ledger, library |
| `ambience TEXT --duration S --out F [--piece S]` | an ElevenLabs seamless loop tiled to the exact length, with fades and a report on every join |
| `fit TRACK --target S [--cuts F] [--bpm N] --out F` | to the sample: whole-bar cuts or loops with one-beat crossfades on downbeats, the real ending kept, cuts landed on downbeats; every step in `fit.json` |
| `loop TRACK --bars 8 --out F [--preview]` | a seamless loop of whole bars, and 3 repeats to check the join |
| `sfx list` / `make NAME --out F` / `place CUES --duration S --out F` / `fetch QUERY --source freesound\|elevenlabs --out DIR [--dur S] [--loop]` | the 23 presets; one effect; a stem with every cue aligned (attack, peak or end) and levelled; one online effect |
| `clean IN --out F [--isolate [auto\|elevenlabs\|apple]] [--nr 12] [--hum 50\|60] [--deess 0.4]` | dialogue clean-up at 48 kHz, voice isolation first when asked, delay removed and the sync proved within 2 ms |
| `duck --music F (--speech F \| --voice F) --out F [--duck -14]` | a gain envelope under speech, plus keyframes for Remotion |
| `mix [--dialogue F] [--voice F] [--music F] [--sfx F] [--ambience F] [--speech F] --platform P --out F` | the anchor, music 20 dB under speech and ducked, effects at their gains, ambience 24 dB under and steady, mastered linearly to the platform |
| `qc FILE [--brief F] [--kind music\|sfx\|mix] [--listen]` | measured checks; `--listen` adds the Gemini judge; exit 2 on a fail |
| `library [--mood M] [--bpm 100-110] [--min S] [--max S]` | search kept takes |
| `credits DIR --out CREDITS.txt [--strict]` | the licence and provenance note for a client; `--strict` exits 1 when anything is not for client delivery |
| `cost [DIR]` | spend from the ledger, or an estimate with `--draft N --final N` |

## Rules

- **Never name an artist, band, song or album** in a brief, and never use real song lyrics. Describe the sound:
  genre and era, 3 to 5 instruments, tempo, key, mood. `brief` refuses otherwise. No negative prompts on Lyria 3 or
  3.5: say what you want.
- **Originals stay untouched.** `<id>_orig.*` is read-only; every edit (fit, loop, mix) is a new file with a JSON
  report. Keep the sidecars with the delivery.
- **Money:** paid calls are estimated first and refused over `--budget` (1.00 USD a run by default); every call goes
  into the project's `ledger.jsonl` with the key's variable name, never the key. A safety block or a bad request is
  explained and never retried. Never ask anyone for a key in chat; `doctor` shows which variables are set.
- **Levels:** dialogue and voice-over are the anchor at -20 LUFS before the mix; music sits 20 dB under speech (18 to
  25) and ducks 14 dB; whooshes and risers 6 to 12 dB under the dialogue, UI clicks 18 dB or more under. The master is
  -14 LUFS / -1 dBTP for YouTube, Reels, TikTok, Facebook and the web, -16 for podcasts, -23 for broadcast, always
  linear (a limiter first when needed, two-pass loudnorm, checked with ebur128).
- **Effects:** few, and each on a visible event. Hits, clicks and pops land their attack on the frame; a whoosh's
  peak lands 1.5 frames before the cut (`--fps`); a riser's climax lands on the cut. Prefer the synthesiser.
- **RealTime beds and Clip drafts end abruptly** (a stream, a 30 s cut): always `fit` them before use.
- **Lengths are loose.** Lyria 3.5 made 64 s for an 18 s request and the Clip 25.6 s (2026-09-25): ask for what the
  video needs and let `fit` cut it; both come as MP3 only (44.1 kHz, 192 kbps, a C2PA manifest in the ID3 tag).
- **Clean-up** never sets loudness (the mix does). Voice isolation is optional: when it cannot run, the chain goes on
  and the report says so.
- **Never** use MusicGen, AudioGen, MMAudio, AudioLDM 2, TangoFlux, ThinkSound, BBC Sound Effects, Freesound NC
  sounds or ElevenLabs on a free plan for client work (non-commercial terms). Never copy media-use's Pixabay files
  into a project or a repo: they are used in place.
- **ElevenLabs:** the plan is read before every paid call (the key needs the User permission to read it; without it
  the output is "plan unknown" and blocked from delivery). Eleven Music on a self-serve plan is for online and
  offline commercial use, not film, TV, radio or multi-platform games; Free to Pro are for individuals, a company
  needs Scale or Business; some industries may not use it at all (`references/licence.md`). Effects go to a client
  mixed into the video, never as separate files. Switch off effect sharing ("Disable" on the Sound Effects page)
  before the first client effect. A timed-out music call is never resent: it may already be billed.
- Never try to remove or hide SynthID or C2PA, and never present the music as made only by people.

## Costs

| What | Price |
|---|---|
| Draft, `lyria-3-clip-preview` (30 s MP3) | $0.04 |
| Final, `lyria-3.5` | $0.08 |
| RealTime bed, `lyria-realtime-exp` | free for now (experimental; may change) |
| `qc --listen`, `gemini-3.8-flash` | about $0.01 (estimate) |
| ElevenLabs music, `music_v2_5` | $0.15 a minute (API list price; 45 s is $0.11) |
| ElevenLabs effect or ambience loop | budgeted at $0.02 a clip ($0.12 a minute list) |
| ElevenLabs voice isolation | $0.12 a minute |
| Synthesiser, Apple isolation, clean, duck, fit, loop, mix, qc, Freesound | $0 |

A 60 s promo with 3 Lyria drafts and 1 final: about $0.20; with one ElevenLabs take instead of the final, $0.27.
Lyria 3.5 has no free tier: the key's project needs billing. On a subscription, ElevenLabs spends credits: the
ledger keeps the cost headers it sends.

## Licence in brief

Google claims no ownership of Lyria output, but it is not exclusive, carries SynthID, is not indemnified through the
Gemini API and should never be registered with Content ID. ElevenLabs output is commercial only from a paid plan,
not exclusive either (no Content ID), and Eleven Music excludes film, TV, radio and multi-platform games on
self-serve plans. The synthesiser's effects have no third-party rights; Freesound is CC0 unless a cue allows CC BY
(then `CREDITS.txt` has the credit line). Details and sources: `references/licence.md`.

## Measured on this machine (2026-09-25, Mac Studio, M4 Max)

On synthetic material (a groove at 104 BPM, tone-burst speech, noise and hum); the API commands ran against a local
fake server, so Lyria's own generation time is not included.

| Step | Time |
|---|---|
| `brief`, `moods`, `library`, `credits`, `cost` | under 0.1 s |
| `generate`, local work per take (save, analyse, measured QC) | about 1 to 2 s |
| `fit` 62 s to 45 s, or to 90 s | 0.85 s |
| `loop` 8 bars with a preview | 0.9 s |
| `sfx make` one preset / all 23 | 0.3 s / 5 s |
| `sfx place` 23 cues on a 60 s stem | 4.9 s |
| `clean` 60 s / with voice isolation (first run compiles the helper) | 0.8 s / 3.5 to 3.9 s |
| `duck` 60 s | 0.45 s |
| `mix` 60 s (voice, music, effects) | 3.2 to 3.4 s |
| `qc` 60 s music / mix / effect | 0.9 to 1.0 s / 0.7 s / 0.2 s |

| Result | Measured |
|---|---|
| Beat grid, click tracks at 82, 104 and 126 BPM | tempo exact to 0.01 BPM, every downbeat within 1.2 ms |
| `fit` | exact to the sample; after a cut or a loop the downbeats stay on one grid within 1.4 ms |
| `loop` | 8 bars exact to 0.06 ms; the wrap as smooth as the source (step ratio 1.0, +0.4 dB) |
| Synthesiser, 23 presets | peak -1.0 dBFS; last 20 ms at -64 dBFS or lower (-60 at every allowed length, pitch and brightness); DC under 0.04 %; under 1 dB lost in mono; all 23 in 3 s |
| `sfx place` | attacks sample-exact on the cue; whoosh peaks exactly 1.5 frames early |
| `clean`, noisy speech | pauses 14 dB quieter; in sync to 0.1 ms after removing 25 ms of delay |
| `duck` | -14.00 dB under speech, 0.00 dB in long gaps, on both channels |
| `mix` | -14.0, -16.0 and -23.0 LUFS on target, true peak -1.8 dBTP or lower, linear; music 20.3 dB under the voice |

Checked on the live API (2026-09-25): a Clip draft and a Lyria 3.5 final with `store: false` (MP3 with C2PA, text
parts `<instrumental>` and `[[A0]]` section labels, no finish reason), a final blocked after generation and made
again, the listening judge's JSON answer (vocals false, fit 10/10), and fit, mix and QC on the result. Lyria 3.5
refuses `response_format` audio/wav and audio/l16.

ElevenLabs, head to head on the live API the same day (judged by Gemini listening, 0 to 10):

| Test | Result |
|---|---|
| Music, 16 s tech bed, `music_v2_5` | 16.0 s exact, 48 kHz stereo PCM, 112.0 BPM, -15.6 LUFS, -1.0 dBTP, made in 5.3 s; 7/10 with the ending inside the last section ("abrupt_cut"), 10/10 with an Ending chunk of its own. Lyria 3.5 + `fit`: 10/10, 24.5 s to make |
| Effects, synthesiser against `eleven_text_to_sound_v3` (fit, clean, usable) | whoosh 10/9/9 against 9/9/8, pop 9/9/9 against 10/9/9, click 7/8/6 against 4/8/7, impact 10/9/9 against 3/3/2, riser 9/8/8 against 5/7/6, ding 10/10/9 against 10/9/9 |
| Ambience, 8 s loops tiled | office room tone to 20 s: worst join 0.69 dB, level changes elsewhere 8.36 dB (95th percentile); a busy cafe to 15 s: 1.8 dB against 5.35 dB; no join heard |
| Voice isolation, speech in cafe chatter at 5 dB SNR (clarity, noise left, natural) | ElevenLabs 9/1/8, Apple 7/2/5; the words read equally well after either (CER 0.045) |

v3 effects come as 48 kHz stereo PCM on a 0.04 s length grid (0.5 s asked, 0.48 s back). The test key could not
read its plan (no User permission), so every ElevenLabs file from it is marked "plan unknown". Still untested:
images as input, every part of Lyria RealTime (SDK names, the scale values, v1beta, filtered prompts, automation
timing; its venv downloads packages), Freesound's search, ElevenLabs on a known paid plan (format refusals, credit
headers). Run `doctor --live` and one cheap draft before a client job.

## Files

- `scripts/sound.py`: the CLI. `scripts/sfx_synth.py`: the synthesiser (plain Python). `scripts/beats.py`: the beat
  grid. `scripts/realtime.py`: the Lyria RealTime recorder (runs in `~/.nexa-sound/venv`).
  `scripts/voice_isolate.swift`: Apple's voice isolation, compiled once to `~/.nexa-sound/bin/voice-isolate`.
  `scripts/moods.json`: the 12 templates. `scripts/gemini_api.py` and `scripts/elevenlabs_api.py`: the shared Gemini
  and ElevenLabs modules (identical in every nexa skill; edit all copies together, a test checks).
- `references/cli.md`, `references/music-craft.md`, `references/licence.md`, `CHANGELOG.md`.
- `tests/test_sound.py`: offline tests with fake servers
  (`python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests`, about 35 s).
