---
name: nexa-sound
description: "Everything a video needs from sound: music from Google Lyria (cheap 30 s drafts, structured finals, exact-length RealTime beds), sound effects from a built-in synthesiser the skill owns outright (whoosh, riser, impact, click, typing, chime and 17 more) plus your own, media-use, Freesound CC0 and ElevenLabs sources, fitting music to the picture (whole-bar edits, a real ending, hits on cuts), dialogue clean-up proved in sync, ducking under speech, a final mix mastered to each platform's loudness, measured QC with an optional listening judge, and licence notes a client can be given. Use it whenever a video, reel, ad, explainer or podcast needs music, a bed, a jingle, sound effects, a cleaner voice, ducking, a mix or loudness for YouTube, Reels, TikTok, podcast or broadcast, Banglish asks included ('music banao', 'background music lagbe', 'bgm add koro', 'sound effect dao', 'whoosh lagao', 'voice clean koro', 'noise komao', 'audio mix koro', 'loudness thik koro'). nexa-video-creator calls these commands; nexa-speech makes the voice-over stems."
allowed-tools: Bash(python3 ~/.claude/skills/nexa-sound/scripts/sound.py:*), Read
---

# nexa-sound

Music, effects, clean-up, ducking, mixing and QC for videos, with every step measured. The command prefix is
`python3 ~/.claude/skills/nexa-sound/scripts/sound.py`. Every flag and file format is in `references/cli.md`; prompt
craft, fitting, levels and effect timing in `references/music-craft.md`; licences in `references/licence.md`.

## Fast path (do exactly this)

A draft (a first cut, a placeholder bed):
1. `library --mood corporate --bpm 100-110 --passed`: reuse a take that passed QC before paying for a new one.
2. `brief --duration 45 --mood corporate --cuts edl.json --out music/brief.json` (free; `moods` lists the 12 moods).
3. `generate music/brief.json --out music --draft 2` ($0.08: two 30 s MP3s to choose a style from).
4. `fit music/<id>_orig.mp3 --target 45 --cuts edl.json --out music/music_fit.wav`.
5. `sfx place cues.json --duration 45 --out sfx/sfx.wav --offline` (the synthesiser: no cost, no licence risk).
6. `mix --voice vo_48k.wav --music music/music_fit.wav --sfx sfx/sfx.wav --platform youtube --out mix.wav`.
7. `qc mix.wav`: exit 0 means every measured check passed.

A client final adds: `generate --final` (Lyria 3.5, $0.08) or `--realtime` for an exact-length bed, then
`qc music/music_fit.wav --listen` (a Gemini listening judge, about $0.01) or agy-watch-video on the file for a free
listen, `clean` on any camera or microphone dialogue before the mix, and `credits . --out CREDITS.txt` in the delivery.
Pass rule: measured checks pass, no vocals in an instrumental, fit to the brief 7/10 or more, no abrupt ending. If a
take fails, change the brief and generate again at most twice, then show the user the judge's notes and the two best
takes. Run anything that calls Lyria with Bash `run_in_background: true`: a final can take minutes.

## Commands

| Command | What it does |
|---|---|
| `doctor [--live]` | ffmpeg filters, key sources (names only), uv and the RealTime venv, swiftc, media-use and `NEXA_SFX_DIRS`; `--live` (free): which Lyria models the key's project sees |
| `moods` | the 12 mood templates (corporate, tech, cinematic, inspirational, lofi, vlog, ad, luxury, suspense, playful, wellness, bangla-folk) |
| `brief --duration S --mood ID [--cuts F] [--speech F] [--bpm N] [--key K] [--vocals] [--notes T] --out F` | the Lyria prompt: length plus 2 s, sections from the cuts with intensities (narrated 2 to 4, reveals and calls to action 6 to 8), the drop on the heaviest cut, "Instrumental." last; refuses artist, song and album names and says why |
| `generate BRIEF --out DIR (--draft N \| --final \| --realtime) [--images A,B] [--budget USD]` | drafts on Lyria 3 Clip (at most 3 at a time), finals on Lyria 3.5, beds on Lyria RealTime; read-only originals, sidecars, ledger, library |
| `fit TRACK --target S [--cuts F] [--bpm N] --out F` | to the sample: whole-bar cuts or loops with one-beat crossfades on downbeats, the real ending kept, cuts landed on downbeats; every step in `fit.json` |
| `loop TRACK --bars 8 --out F [--preview]` | a seamless loop of whole bars, and 3 repeats to check the join |
| `sfx list` / `make NAME --out F` / `place CUES --duration S --out F` / `fetch QUERY --source freesound\|elevenlabs --out DIR` | the 23 presets; one effect; a stem with every cue aligned (attack, peak or end) and levelled; one online effect |
| `clean IN --out F [--isolate] [--nr 12] [--hum 50\|60] [--deess 0.4]` | dialogue clean-up at 48 kHz, delay removed and the sync proved within 2 ms |
| `duck --music F (--speech F \| --voice F) --out F [--duck -14]` | a gain envelope under speech, plus keyframes for Remotion |
| `mix [--dialogue F] [--voice F] [--music F] [--sfx F] [--speech F] --platform P --out F` | the anchor, music 20 dB under speech and ducked, effects at their gains, mastered linearly to the platform |
| `qc FILE [--brief F] [--kind music\|sfx\|mix] [--listen]` | measured checks; `--listen` adds the Gemini judge; exit 2 on a fail |
| `library [--mood M] [--bpm 100-110] [--min S] [--max S]` | search kept takes |
| `credits DIR --out CREDITS.txt` | the licence and provenance note for a client |
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
- **Clean-up** never sets loudness (the mix does). Voice isolation is optional: when it cannot run, the chain goes on
  and the report says so.
- **Never** use MusicGen, AudioGen, MMAudio, AudioLDM 2, TangoFlux, ThinkSound, BBC Sound Effects, Freesound NC
  sounds or ElevenLabs on a free plan for client work (non-commercial terms). Never copy media-use's Pixabay files
  into a project or a repo: they are used in place.
- Never try to remove or hide SynthID or C2PA, and never present the music as made only by people.

## Costs

| What | Price |
|---|---|
| Draft, `lyria-3-clip-preview` (30 s MP3) | $0.04 |
| Final, `lyria-3.5` | $0.08 |
| RealTime bed, `lyria-realtime-exp` | free for now (experimental; may change) |
| `qc --listen`, `gemini-3.8-flash` | about $0.01 (estimate) |
| ElevenLabs effect | about $0.05 (estimate; paid plans only) |
| Synthesiser, clean, duck, fit, loop, mix, qc, Freesound | $0 |

A 60 s promo with 3 drafts and 1 final: about $0.20. Lyria 3.5 has no free tier: the key's project needs billing.

## Licence in brief

Google claims no ownership of Lyria output, but it is not exclusive, carries SynthID, is not indemnified through the
Gemini API and should never be registered with Content ID. The synthesiser's effects have no third-party rights;
Freesound is CC0 unless a cue allows CC BY (then `CREDITS.txt` has the credit line). Details and sources:
`references/licence.md`.

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

Untested against the real services (no live call was made): Lyria 3.5's WAV answer and text parts, `store: false`,
images as input, the Clip MP3's C2PA tag, every part of Lyria RealTime (SDK names, the scale values, v1beta, filtered
prompts, automation timing), the listening judge's JSON answer, Freesound's search and ElevenLabs' endpoints. The
uv venv for RealTime was not created (it downloads packages). Apple's voice isolation ran only on tone-burst speech,
which it partly removes; it is tuned for real voices. Run `doctor --live` and one cheap draft before a client job.

## Files

- `scripts/sound.py`: the CLI. `scripts/sfx_synth.py`: the synthesiser (plain Python). `scripts/beats.py`: the beat
  grid. `scripts/realtime.py`: the Lyria RealTime recorder (runs in `~/.nexa-sound/venv`).
  `scripts/voice_isolate.swift`: Apple's voice isolation, compiled once to `~/.nexa-sound/bin/voice-isolate`.
  `scripts/moods.json`: the 12 templates. `scripts/gemini_api.py`: the shared Gemini module (do not edit here).
- `references/cli.md`, `references/music-craft.md`, `references/licence.md`, `CHANGELOG.md`.
- `tests/test_sound.py`: offline tests with fake servers
  (`python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests`, about 35 s).
