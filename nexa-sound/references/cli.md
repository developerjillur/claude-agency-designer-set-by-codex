# sound.py reference

`python3 ~/.claude/skills/nexa-sound/scripts/sound.py <command> ...`

Every command prints a short summary. With `--json` it prints one JSON object on stdout instead (other skills parse
it). `sound.py --version` prints the version. Progress notes go to stderr. Exit codes: 0 done, 1 an error (the
message says what happened and what to do), 2 a QC that failed (`qc`) or a RealTime config that is not valid
(`realtime.py`), 130 interrupted.

Audio in can be anything ffmpeg reads (WAV, MP3, AAC, FLAC, the audio of a video). Audio out is always 48 kHz,
24-bit PCM WAV, stereo (a mono voice stays mono in `clean`). Times are seconds.

## Environment

| Variable | Meaning |
|---|---|
| `GEMINI_API_KEY`, `GEMINI_API_KEY_1`, `_2` ... | Gemini keys, in failover order (a refused key moves to the next; a quota error waits on the same key). Without them the macOS keychain entry `GEMINI_API_KEY` is used. Never printed or written anywhere. |
| `FREESOUND_API_KEY` | turns on Freesound for `sfx place` and `sfx fetch` (sent only to freesound.org in an `Authorization` header); without it the keychain entry `FREESOUND_API_KEY` is used |
| `ELEVENLABS_API_KEY`, `ELEVENLABS_API_KEY_1`, `_2` ... | ElevenLabs music, effects, ambience and voice isolation (sent only to api.elevenlabs.io in the `xi-api-key` header); a refused key moves to the next; without them the keychain entry `ELEVENLABS_API_KEY` is used. Give the key the User permission (read) so the plan can be read, plus Sound Effects, Music and Audio Isolation |
| `NEXA_SOUND_HOME` | the skill's own folder, default `~/.nexa-sound` (`library.jsonl`, `venv/`, `bin/`, `capabilities.json`) |
| `NEXA_SFX_DIRS` | your own effect folders, separated by `:`; each may hold a `manifest.json` (below) |
| `NEXA_MEDIA_USE_SFX` | where media-use keeps its effects (default `~/.claude/skills/media-use/audio/assets/sfx`) |
| `FFMPEG`, `FFPROBE` | tool paths when they are not on PATH |
| test hooks | `NEXA_GEMINI_BASE_URL`, `NEXA_GEMINI_SLEEP_SCALE`, `NEXA_NO_KEYCHAIN` (shared module), `NEXA_FREESOUND_BASE_URL`, `NEXA_ELEVENLABS_BASE_URL`, `NEXA_ELEVENLABS_SLEEP_SCALE`, `NEXA_SOUND_VENV_PYTHON` (a Python to run `realtime.py` with), `NEXA_REALTIME_FAKE=1` and `NEXA_REALTIME_FAKE_LOG=FILE` (a local fake stream), `NEXA_SOUND_ISOLATE_BIN` (a voice-isolation binary) |

## Costs and the ledger

Paid calls are estimated first and refused when the estimate is over `--budget` (USD, default 1.00 per command run).
Each call is logged in `ledger.jsonl`: the one in the output folder or up to two folders above it, else a new one in
the output folder; `--project DIR` puts it in `DIR/ledger.jsonl`.

```json
{"time": "2026-09-25T13:41:25+06:00", "skill": "nexa-sound", "command": "generate", "model": "lyria-3-clip-preview",
 "units": 1, "est_usd": 0.04, "key_source": "GEMINI_API_KEY", "status": "ok", "id": "ns_2026-09-25_1341_corporate_a"}
```

`status` is `ok`, `empty` (the call answered without audio; it may still be billed), `blocked` (a finished track
Google blocked, logged at $0 and made once more) or `failed` (logged at $0, except
a timeout, which may have been billed). `key_source` is the variable's name, never the key.

## doctor

`doctor [--live]`

Checks ffmpeg and ffprobe and every filter the skill uses (`filters_missing`), the MP3 encoder (for the listening
judge), the Gemini key sources (names only), the Freesound and ElevenLabs keys (yes or no), uv and the RealTime venv,
swiftc and the voice-isolation helper, the media-use folder, `NEXA_SFX_DIRS` and the library. `--live` (a free call)
lists which of `lyria-3.5`, `lyria-3-clip-preview`, `lyria-realtime-exp` and `gemini-3.8-flash` the key's project
sees and writes `~/.nexa-sound/capabilities.json`; with an ElevenLabs key it also reads the plan (free:
`GET /v1/user/subscription`): tier, paid or not, credits left, or why the key cannot read it. Exit 1 when ffmpeg or a
filter is missing.

## moods

`moods`: the 12 templates in `scripts/moods.json` (id, name, use for, default BPM and key, ending, variants).

| id | for | BPM, key | ending |
|---|---|---|---|
| `corporate` | explainer, about-us, B2B | 104, C major | ring-out |
| `tech` | SaaS, app demo | 112, A minor | final hit |
| `cinematic` | launch reveal, trailer | 92, D minor | final hit |
| `inspirational` | NGO, documentary, founder story | 76, G major | ring-out |
| `lofi` | study, cafe, cosy vlog, B-roll | 82, F major | ring-out |
| `vlog` | travel, lifestyle | 118, D major | final hit |
| `ad` | sale, promo, 15 to 30 s ads | 126, E minor | final hit |
| `luxury` | fashion, real estate, premium | 120, A minor | ring-out |
| `suspense` | problem statement, teaser | 70, C minor | cut to silence |
| `playful` | kids, food, fun explainer | 124, C major | final hit |
| `wellness` | health, spa, meditation | 60, F major | fade |
| `bangla-folk` | Boishakh, Eid, wedding, local brands (`--variant calm`: Baul-inspired acoustic, 88 BPM) | 100, D major | final hit |

## brief

`brief --duration S --mood ID [--variant V] [--cuts FILE] [--speech FILE] [--bpm N] [--key K] [--vocals]
[--notes TEXT] --out brief.json`

Builds the Lyria prompt from a template. `{DUR}` becomes the video length plus 2 s (headroom for `fit`), `{BPM}` and
`{KEY}` the mood's defaults or `--bpm` and `--key`, `{DROP}` the time of the heaviest cut (40 % of the length when
there are no cuts), and `{SECTIONS}` one line per section between cuts:

```
[0:00 - 0:08] Intro: Sparse and supportive under the voice-over, simple chords, no lead melody. Intensity: 2/10
[0:21 - 0:37] Reveal: Lift: fuller drums and a bright lead layer. Intensity: 6/10
[0:51 - 1:00] Call to action: Confident and full, heading for the ending. Intensity: 7/10
```

Sections shorter than 3 s are merged (the weaker cut goes) and there are at most 8. A cut's label only picks the
section's role (intro, tension, build, reveal, call to action, story, outro); the label's own words never go into
the prompt, so product and brand names in an edit list cannot reach Lyria. Sections at least half covered by speech
get intensity 2 or 3 and a sparse arrangement; reveals and calls to action get 6 to 8 (6 when narrated).

The prompt ends with "Instrumental." unless `--vocals` (then every "instrumental" goes, "With lead vocals." is added
and `--notes` follows on its own line, for example `Lyrics: ...`).

Refused, with the reason, when the prompt names or quotes an artist, band, song or album: "in the style of", "in the
vein of", "a la" and a name, "like" followed by a capitalised name, "cover of", "remix of", "tribute to",
"soundalike", "featuring" or "feat.", genres named after a person (Rabindra Sangeet, Nazrul Geeti, Lalon), and any
title in quotes. Lyrics after a `Lyrics:` header get only the phrase checks (a sung line may start "Like Summer").

Cuts file: a list of `{"t": 14.0, "weight": 2.5, "label": "product reveal"}` or of plain seconds, or an EDL:

```json
{"duration_s": 60, "cuts": [{"t": 8.1, "weight": 1, "label": "problem"}, {"t": 20.8, "weight": 2.5, "label": "reveal"}],
 "speech": [{"start": 0.5, "end": 7.6}, {"start": 9.0, "end": 19.8}]}
```

Speech file (`--speech`, also `duck --speech` and `mix --speech`): `[[0.5, 7.6], [9.0, 19.8]]`, or
`[{"start": 0.5, "end": 7.6}]`, or `{"spans": [...]}` / `{"speech": [...]}` (nexa-video-creator), or nexa-speech's
`words.json` (`[{"w": "Hello", "start": 0.52, "end": 0.81}, ...]`; words closer than 0.3 s join into one span).

`brief.json` (schema `nexa-sound/brief-1`) holds `mood`, `variant`, `mood_name`, `duration_s`, `prompt_duration_s`,
`bpm`, `key`, `scale` (the RealTime scale for the key), `vocals`, `notes`, `ending`, `drop_s`, `sections` (`start`,
`end`, `label`, `cut_label`, `kind`, `change`, `intensity`, `narrated`, `speech_share`), `cuts`, `speech`, the
`prompt`, and `realtime`: `weighted_prompts` (`[["Uplifting corporate pop", 1.0], ...]`), `config` (`bpm`, `scale`,
`density`, `brightness`, `guidance`, `mute_drums`) and `automation` (one `{t, density, brightness, mute_drums}` per
section after the first; density and brightness rise with the section's intensity, drums are muted at intensity 2).

## generate

`generate BRIEF --out DIR [--engine auto|elevenlabs|lyria] (--draft N | --final [--takes N] | --realtime [--seed N]
| --takes N [--model M] [--seed N]) [--images A,B] [--budget USD] [--project DIR]`

The engine: `--draft`, `--final` and `--realtime` are Lyria modes. `--engine elevenlabs` makes ElevenLabs takes.
`auto` (the default, with no mode flag) picks ElevenLabs when its key is here and the plan it reads is paid, else a
Lyria final, and says why.

| Mode | Model | What comes back | Price |
|---|---|---|---|
| ElevenLabs (`--takes` 1 to 3) | `music_v2_5` (default) or `music_v2` | exact to the brief's length, 48 kHz 16-bit stereo WAV (the PCM answer wrapped), or MP3 when the plan refuses PCM | $0.15 a minute a take (list price) |
| `--draft N` (1 to 10) | `lyria-3-clip-preview` | about 25 to 30 s, MP3 (25.6 s on 2026-09-25) | $0.04 a take |
| `--final` (`--takes` 1 to 3) | `lyria-3.5` | MP3, 44.1 kHz stereo, 192 kbps; the length is loose (64 s for an 18 s request) | $0.08 a take |
| `--realtime` | `lyria-realtime-exp` | the video length plus 3 s, 48 kHz 16-bit stereo WAV | free for now |

Request (Interactions API, timeout 600 s): `{"model", "input": PROMPT or [text block, image blocks], "store": false}`.
No `response_format`: on 2026-09-25 the live API refused audio/wav and audio/l16 for lyria-3.5 ("Audio MIME type
AUDIO_WAV is not supported"). Takes run in parallel, at most 3 at a time; each id is reserved with a lock file, so a
draft and a final started in the same minute never share a name. A track Google blocks after generating it (seconds
of work, then "Request blocked for an unspecified policy reason") is made once more: the same prompt passed, was
blocked and passed again within 8 minutes on 2026-09-25. A prompt blocked at once, a bad request or a daily quota is
never retried; a per-minute quota or a server error waits and retries up to 3 times on the same key (the shared
`gemini_api` module).

ElevenLabs request (`POST /v1/music`, timeout 600 s, never resent after a timeout since it may be billed): the brief
as a composition plan, `respect_sections_durations`, `sign_with_c2pa` on MP3 (PCM has no C2PA), `seed` when given,
`output_format` `pcm_48000` first, then `mp3_48000_320`, `mp3_44100_192` and `mp3_44100_128` when the plan refuses a
format (only a refusal that names the format, tier or plan steps down; any other error stops). The plan for
`music_v2_5` and `music_v2`:

```json
{"chunks": [
  {"text": "[Intro] {instrumental}", "duration_ms": 13000,
   "positive_styles": ["Minimal electronic tech", "arpeggiated analog synth", "crisp digital plucks", "112 BPM",
     "A minor", "background music under a voice-over",
     "sparse and supportive under the voice-over, simple chords, no lead melody", "intensity 3 of 10",
     "sparse arrangement that leaves room for the voice"],
   "negative_styles": ["vocals", "singing", "choir", "spoken words", "lyrics", "vocal chops", "busy lead melody",
     "loud drum fills"],
   "context_adherence": "high"},
  {"text": "[Ending] {instrumental}", "duration_ms": 3000,
   "positive_styles": ["Minimal electronic tech", "arpeggiated analog synth",
     "one final hit, then a short tail ringing out to silence", "clear resolution"],
   "negative_styles": ["vocals", "singing", "choir", "spoken words", "lyrics", "vocal chops", "fade in",
     "new melody", "abrupt cut"],
   "context_adherence": "high"}]}
```

(The 16 s tech brief of the live test, 2026-09-25: 16.0 s back, 48 kHz stereo, 112.0 BPM, judged 10/10.)

One chunk per brief section at its exact length (3 to 120 s each; longer sections are split, a section under 3 s
joins its neighbour; at most 30 chunks). The first chunk carries the mood's styles, the tempo, the key and the
voice-over note; later chunks repeat the first two styles plus their own. Narrated sections ask for a sparse
arrangement. The mood's ending gets its own chunk (`ring_out` and `fade` 4 s, `final_hit` and `cut` 3 s): styled
only inside the last section, music_v2_5 stopped at the length mid-phrase (the judge called it "abrupt_cut", 7/10);
as its own chunk it resolved (10/10, 2026-09-25). No voice unless the brief allows vocals. The plan is kept in the
sidecar (`request.composition_plan`), and the provider block records the plan tier read at the time and the response
headers that came back (`song-id`; `request-id` and the cost headers when sent). The licence block comes from the
plan: paid means commercial; free means non-commercial with "elevenlabs.io" in the title; unknown (the key cannot
read the plan) means not for client delivery until someone confirms it.

`--images`: up to 10 images (JPEG, PNG, WebP; other formats and files over 1.5 MB are turned into a 1280 px JPEG
first) sent with the prompt to steer the mood (Lyria only).

Per take, in `DIR`:
- `<id>_orig.<wav|mp3>`: the file exactly as it came (ElevenLabs PCM gets a WAV header), made read-only. Never
  edited: every edit is a new file.
- `<id>.json`: the sidecar (below). `<id>.beats.json`: the beat grid.
- a line in `ledger.jsonl` and in `~/.nexa-sound/library.jsonl`.

Ids look like `ns_2026-09-25_1341_corporate_a` (date, time, mood, take letter).

The sidecar (schema `nexa-sound/track-1`), fields that cannot be filled are left out or null:

```json
{"id": "ns_2026-09-25_1341_corporate_d", "created_at": "2026-09-25T13:41:27+06:00",
 "tool": {"skill": "nexa-sound", "version": "2026.09.25.1"},
 "provider": {"api": "gemini-api", "endpoint": "POST /v1beta/interactions", "model": "lyria-3.5", "stage": "GA",
              "interaction_id": "interactions/...", "store": false, "key_var_used": "GEMINI_API_KEY"},
 "request": {"prompt": "Create a 62-second ...", "lyrics": null, "images": [], "realtime": null, "seed": null,
             "response_format": null, "requested_duration_s": 62,
             "brief": {"mood": "corporate", "bpm": 104.0, "key": "C major", "vocals": false, "sections": []}},
 "response": {"text_parts": ["[[A0]] [[B1]] [[C2]]"], "timed_lines": [], "section_labels": ["A0", "B1", "C2"],
              "vocals_suspected": false, "filtered": false, "latency_s": 41.2, "cost_usd_est": 0.08},
 "original": {"file": ".../ns_..._orig.wav", "sha256": "8644...", "format": "wav", "sample_rate": 44100,
              "channels": 2, "duration_s": 62.0, "c2pa_manifest_present": false, "read_only": true,
              "synthid": "SynthID watermark embedded by Google in all Lyria output. Do not remove or alter."},
 "analysis": {"bpm": 104.0, "bar_s": 2.3077, "first_downbeat_s": 0.0, "beat_confidence": 0.98,
              "downbeats_file": ".../ns_....beats.json", "lufs_i": -18.8, "true_peak_dbtp": -2.2, "lra_lu": 1.5},
 "fit": {"target_s": 60.0, "ops": [...], "start_offset_s": 0.0, "file": "...", "report": "...", "earlier": []},
 "qc": {"passed": true, "failed": [], "warnings": [], "listened": false, "vocals_present": null,
        "ending": null, "fit_to_brief": null, "problems": null},
 "licence": {"source": "Google Lyria via the Gemini API (paid tier)", "terms": ["https://ai.google.dev/gemini-api/terms",
             "https://policies.google.com/terms/generative-ai/use-policy"], "ownership": "...", "indemnity": "...",
             "content_id": "Do not register.", "attribution_required": false},
 "usage": {"project": null, "video_edl": ".../edl.json", "approved_by": null}}
```

Every text part the model returns is kept raw. Lines like `[12.0:14.5] words` or `[0.0:] words` are timed lyric
lines: in an instrumental brief they mean the take has vocals (`vocals_suspected`), and QC fails it. `[[A0]]` labels
are section hints only. `c2pa_manifest_present` looks for Google's C2PA credential (a GEOB frame of type
`application/c2pa` in an MP3's ID3 tag, or a C2PA chunk in a WAV).

RealTime: `realtime.py` runs in `~/.nexa-sound/venv` (uv, Python 3.12, `google-genai>=2.9`), created on first use
after a note that it downloads the package once. It records preroll (8 s) plus the video plus 3 s, drops the preroll,
fades both cut points over 5 ms and writes `<id>_orig.wav`. The sidecar's `request.realtime` holds
`weighted_prompts`, `config`, `automation`, `preroll_s`, `recorded_s`, `session_count` and `api_version`;
`response.filtered_prompts` lists prompts the service filtered. A RealTime bed is cut from a stream, so its end is
abrupt until `fit` ends it on a downbeat (QC says so). Sessions stop at about 10 minutes: at most 9 minutes are
recorded.

`realtime.py --config CONFIG.json --out OUT.wav [--json]` (normally called by `generate`):

```json
{"weighted_prompts": [["Lo-Fi Hip Hop", 1.0], ["Rhodes Piano", 0.7]],
 "config": {"bpm": 82, "scale": "F_MAJOR_D_MINOR", "density": 0.4, "brightness": 0.4, "guidance": 4.0},
 "automation": [{"t": 14.0, "density": 0.61, "mute_drums": false}], "seconds": 48, "preroll": 8, "api_version": "v1beta"}
```

Config fields and ranges: `guidance` 0 to 6, `bpm` 60 to 200, `density` and `brightness` 0 to 1, `temperature` 0 to 3,
`top_k` 1 to 1000, `seed` 0 to 2147483647, `mute_bass`, `mute_drums`, `only_bass_and_drums` (true or false),
`music_generation_mode` (`QUALITY`, `DIVERSITY`, `VOCALIZATION`), `scale`: `C_MAJOR_A_MINOR`,
`D_FLAT_MAJOR_B_FLAT_MINOR`, `D_MAJOR_B_MINOR`, `E_FLAT_MAJOR_C_MINOR`, `E_MAJOR_D_FLAT_MINOR`, `F_MAJOR_D_MINOR`,
`G_FLAT_MAJOR_E_FLAT_MINOR`, `G_MAJOR_E_MINOR`, `A_FLAT_MAJOR_F_MINOR`, `A_MAJOR_G_FLAT_MINOR`,
`B_FLAT_MAJOR_G_MINOR`, `B_MAJOR_A_FLAT_MINOR`, `SCALE_UNSPECIFIED`. An unknown field or value is an error (exit 2),
never dropped. Automation events are sent 2 s early (changes take about 2 s to land), with the whole config each
time; they may not change `bpm` or `scale` (that needs a context reset, a hard cut).

## fit

`fit TRACK --target S [--cuts FILE] [--bpm N] [--brief BRIEF] --out FILE`

Fits a track to the picture, to the sample (a result more than 50 ms off stops with an error). BPM comes from
`--bpm`, else the track's sidecar; the ending style from the sidecar's brief or `--brief`.

1. Resample to 48 kHz (`aresample=48000:filter_size=64:phase_shift=10:cutoff=0.97`) in 32-bit float through a 5 Hz
   high-pass (Lyria takes carry a 0.5 to 0.7 % DC offset, which clicks at every cut), with a gain that leaves 1 dB
   of headroom when the source peaks above -1 dBFS (Lyria MP3s decode to +0.8 dBFS, which a 24-bit file would
   clip). The report lists both as `dc_block` and `gain` ops; the output is 24-bit.
2. The beat grid (`beats.py`, with the brief's BPM) and, per beat, the energy in three bands (under 250 Hz, 250 Hz
   to 2 kHz, over 2 kHz).
3. With `--cuts`: the start moves by up to 2 s either way (skip the head, or start the music later) to put the most
   weighted cuts within 80 ms of a downbeat. It stays put unless that lands more cuts or brings them clearly closer.
4. Shorter: remove whole bars from the middle where bar a+m sounds like bar a (and bar a+m-1 like bar a-1), keeping
   the first bar and the last two bars and the ending. Longer: loop whole bars (4, 8 or 16 when the count allows) from
   the steadiest stretch whose end sounds like its start. Every join is a one-beat equal-power crossfade (`acrossfade`
   qsin) starting on a downbeat; a weak grid (confidence under 0.5) gets crossfades of a bar, at most 2 s.
5. The part under a bar: skip a silent lead-in; trim the ring-out after the last hit with a fade (1.5 s at most);
   pad silence after a quiet ending (up to 1.5 s); `atempo` within 3 % (penalised when there are cuts, since it
   slides the downbeats); skip into the intro with a short fade-in; or, last, end on a downbeat 1 to 3 s before the
   target with a fade (0.3 s after the final hit when the brief ends on a hit). Bar counts that are not a multiple of
   4 cost more, since they can break a chord cycle the energy features cannot hear.
6. An abrupt source ending (a Clip draft, a RealTime bed) is never kept: the fit ends on a downbeat with a fade.

`<out>.json` (schema `nexa-sound/fit-1`): `source`, `source_sha256`, `source_sidecar`, `file`, `target_s`,
`result_s`, `source_s`, `bpm`, `bar_s`, `beat_confidence`, `segments` (source seconds, in play order),
`crossfade`, `tempo_factor`, `ops`, `notes`, `considered` (the cheapest plans it compared), `hits_on_cuts`
(`offset_s`, `weighted_hits_before`, `weighted_hits_after`, `soft_before`, `soft_after`, per cut `error_ms`),
`downbeats_out` (downbeats in the result, for placing effects), `tail`, `seconds`.

```json
"ops": [{"op": "resample", "to_hz": 48000, "bits": 24, "from_hz": 44100},
        {"op": "offset", "s": -0.03, "skip_head_s": 0.0, "delay_s": 0.03, "reason": "hits on cuts"},
        {"op": "cut_middle", "from_s": 46.1541, "to_s": 48.4618, "bars": 1, "similarity_db": 0.51, "xfade_s": 0.5769},
        {"op": "pad_tail", "s": 0.2777}]
```

The track's sidecar gets the same in `fit` (older fits move to `fit.earlier`). The original is never touched.

## loop

`loop TRACK --bars 8 [--bpm N] --out FILE [--preview]`

A seamless loop of exactly N bars from the steadiest stretch: the bar after the loop is crossfaded (one beat, qsin)
into the loop's first beat, so the end runs straight into the start. `--preview` also writes
`<out>.preview.wav` (3 repeats). `<out>.json` (schema `nexa-sound/loop-1`): `from_s`, `to_s`, `length_samples`,
`length_s`, `bars`, `bpm`, `bar_s`, `crossfade`, `similarity_db` and `join`: `continuation_db` (the loop's first
50 ms against the source's own continuation; 0 dB means it flows like the original) and `sample_step_vs_source` (the
step across the wrap against the same step in the source; 1.0 is as smooth as the original).

## sfx

`sfx list`: the synthesiser's presets (default length, pitch, brightness, how to align, default gain, description)
and which sources are on.

`sfx make NAME [--dur S] [--seed N] [--pitch HZ] [--brightness 0-1] --out FILE`: one preset to 48 kHz 24-bit stereo
WAV, sample peak -1 dBFS, and `<out>.json` (schema `nexa-sound/sfx-1`) with the parameters and measured numbers:
`duration_s`, `peak_dbfs`, `attack_s` (the first sample within 30 dB of the peak), `peak_s` (the middle of the
loudest 10 ms), `end_s`, `climax_s` (risers), `dc_offset`, `tail_rms_dbfs` (last 20 ms), `true_peak_dbtp`,
`m_max_lufs` (loudest 400 ms), plus `placement` and `licence`. Deterministic: the same inputs give the same bytes.
`sfx make all --out FOLDER` renders every preset with a `manifest.json`, so the folder can join `NEXA_SFX_DIRS`.

Presets: whoosh, whoosh-short, swipe, swoosh-down, pop, bubble, click, tick, key, typing, ding, chime, notify, success,
error, riser, downlifter, impact, boom, sub-drop, glitch, shutter, sparkle (`references/music-craft.md` describes each).
Names also resolve by alias: "ui click", "notification", "swoosh", "bass drop" and the like.

`sfx place CUES --duration S --out FILE [--fps 30] [--offline] [--budget USD] [--project DIR]`

```json
[{"t": 3.2, "name": "whoosh", "gain_db": -10, "align": "peak"},
 {"t": 5.0, "name": "impact"},
 {"t": 7.5, "name": "click", "seed": 3},
 {"t": 9.0, "query": "glass shatter", "allow_cc_by": true},
 {"t": 12.0, "file": "brand/logo-sting.wav", "align": "attack", "licence": "the client's own"}]
```

Cue fields: `t`; one of `name`, `query`, `file`; `align` (`attack`: the attack lands on t, for hits, clicks and pops;
`peak`: the loudest 10 ms lands `lead_s` before t, default 1.5 frames at `--fps`, for whooshes; `end`: a riser's
climax, or a file's loudest moment, lands on t); `gain_db`; `lead_s`; synth parameters `dur`, `seed`, `pitch`,
`brightness`; `source` to use one source only (`file`, `synth`, `library`, `media-use`, `freesound`, `elevenlabs`).
Defaults come from the preset (whooshes and risers -8 to -12 dB, impacts -3 to -6, UI sounds -12 to -22). Without a
seed, repeats of a preset get seeds 1, 2, 3 in order, so they differ.

Sources, in order: the cue's `file`; the synthesiser; `NEXA_SFX_DIRS` folders (by manifest key, file name or all the
query's words in a key or description); media-use's files by path (Pixabay licence: used in place, never copied);
Freesound (CC0 only unless the cue allows CC BY; never NC; the 128 kbps preview); ElevenLabs (budgeted at $0.02 a
clip, within the budget; the plan is recorded, and a free or unknown plan marks the cue not for client delivery).
`--offline` stops at media-use. A cue nothing matches is skipped with the reason. Measured on 2026-09-25 (synthesiser
against ElevenLabs `eleven_text_to_sound_v3`, judged on fit, clean and usable): the synthesiser won or tied on
whoosh, impact (10 against 3), riser, click and ding, ElevenLabs on pop; ElevenLabs is for real-world foley the
presets do not cover (a door, glass, a crowd, rain), so name those cues with `query` and `source: elevenlabs`.

Levels: each effect's loudest 400 ms (momentary loudness, a mono file measured as dual mono) is set to
`-20 LUFS + gain_db`: the stem is made for a dialogue anchor of -20 LUFS, and `mix` moves it with the real dialogue.

Writes the stem (exactly S long), `<stem>_files/` (the synthesised effects and any downloads) and `<stem>_cues.json`
(schema `nexa-sound/sfx-cues-1`): per cue `t`, `name`, `resolved` (`file`, `source`, `preset`, `params`, `licence`,
`licence_url`, `attribution`, and for Freesound `freesound_id`, `title`, `author`, `source_url`, `quality`), `align`,
`lead_s`, `ref_s`, `start_s`, `gain_db`, `applied_gain_db`, `m_max_lufs`, `trimmed_head_s`, `trimmed_tail_s`; then
`skipped`, `licences`, `reference_dialogue_lufs`, `cost`.

A library folder's `manifest.json` (the media-use format, plus optional licence fields):

```json
{"_licence": "CC0", "door-slam": {"file": "door-slam.wav", "duration": 1.2, "description": "heavy door",
                                  "licence": "CC0", "attribution": null}}
```

`sfx fetch QUERY --source freesound|elevenlabs --out DIR [--dur S] [--loop] [--influence 0-1] [--model M]
[--allow-cc-by] [--budget USD] [--project DIR]`: one effect into `DIR`, converted to 48 kHz 24-bit WAV next to the
download (`<name>_48k.wav` when the download is already a WAV), with a sidecar and a `manifest.json` entry (so `DIR`
can join `NEXA_SFX_DIRS`).

- Freesound: `GET /apiv2/search/` (the old `/apiv2/search/text/` was deprecated in November 2025), sorted by
  relevance, CC0 only unless `--allow-cc-by`, never NC or sampling licences, explicit sounds skipped, up to 30 s; the
  HQ preview MP3 is downloaded (the original file needs OAuth2).
- ElevenLabs: `POST /v1/sound-generation` with `text`, `duration_seconds` (0.5 to 30; lengths come back on a 0.04 s
  grid, so 0.5 gives 0.48), `prompt_influence` (0 free to 1 literal; the model's default without it), `loop` and
  `model_id` (`eleven_text_to_sound_v3` by default, `eleven_text_to_sound_v2`; `--loop` always uses v2, the only model
  that loops). With `--dur` it asks for `pcm_48000` (v3 answers 48 kHz stereo; the channel count is read from the
  byte count against the length) and wraps it as WAV; without, 192 kbps MP3. The sidecar (schema
  `nexa-sound/elevenlabs-1`) keeps the prompt, model, length, loop, influence, format, the plan read before the call,
  the licence, the response headers and the SHA-256.

## ambience

`ambience TEXT --duration S --out FILE [--piece S] [--influence 0-1] [--model M] [--fade-in 1.0] [--fade-out 1.5]
[--budget USD] [--project DIR]`

An ambience or room-tone bed of exact length for $0.02: one ElevenLabs seamless loop (`--piece`, 4 to 30 s, default
the length up to 30 s, on `eleven_text_to_sound_v2`), tiled sample-exactly to S with ffmpeg and faded in and out.
Writes FILE (48 kHz 24-bit stereo) and `<stem>.json` (schema `nexa-sound/ambience-1`): the text, length, loop length
and count, fades, loudness, the loop's sidecar, the licence and `seams`: the level jump at each join against the rest
of the file (`joins`, `worst_level_jump_db`, `p95_level_jump_db`, `audible`). An audible join says so: make it again
or use a longer piece. Measured on 2026-09-25 with 8 s loops: an office room tone (20 s) joined at 0.69 dB while the
rest of the file moved 8.36 dB (95th percentile), a busy cafe (15 s) at 1.8 dB against 5.35 dB: no join could be
heard. Describe what is heard, not a scene ("quiet office room tone, distant keyboard, air conditioning hum", not "an
office").

## clean

`clean IN --out FILE [--isolate [auto|elevenlabs|apple]] [--denoiser afftdn|anlmdn|none] [--nr 12] [--hum 50|60]
[--deess 0.4]`

At 48 kHz: `adeclick` and `adeclip` first when astats shows many full-scale peaks; `highpass` 80 Hz; `afftdn` with
`nf` from the measured noise floor (the twenty quietest 50 ms blocks, clamped to -80 to -20 dB) and `nr` 12 (or
`anlmdn`); hum notches at 50 or 60 Hz and 3 harmonics (`--hum`); -2 dB at 250 Hz and +2 dB at 4 kHz; `deesser` only
with `--deess`; `acompressor` (threshold -20 dB, ratio 3, attack 8, release 120, knee 4, makeup 2 dB). The input is
padded so nothing is lost at the end, and the processing delay is removed (afftdn 25 ms, anlmdn 8 ms, Apple isolation
56.3 ms). Then it proves the sync: 1 ms envelopes of input and output are cross-correlated; a leftover over 1 ms is
measured and removed once more, and anything over 2 ms stops the command without writing the file. `--isolate` runs
voice isolation first. `auto` (the default when no engine is named) uses ElevenLabs' voice isolator when its key is
here and the plan is paid, else Apple's (`scripts/voice_isolate.swift`, compiled once with swiftc to
`~/.nexa-sound/bin/voice-isolate`, free). ElevenLabs (`POST /v1/audio-isolation`, $0.12 a minute, in the ledger): the
file goes up as 16-bit WAV and comes back as MP3, decoded to the working length; the sync check then measures and
removes what delay is left. Speech in cafe chatter at 5 dB SNR (2026-09-25, judged 0 to 10): ElevenLabs clarity 9,
noise left 1, natural 8; Apple 7, 2, 5; the words were read equally well after either (CER 0.045). When isolation
cannot run, the chain goes on without it and the report says why. Loudness is not set here.

`<out>.json` (schema `nexa-sound/clean-1`): `chain`, `denoiser`, `nr`, `nf_used_db`, `hum`, `deess`, `isolate`
(`asked`, `ran`, `engine`, and for ElevenLabs the licence and response headers), `noise_floor_db` (`before`, `after`),
`delay` (`removed_ms`, `known_ms`, `extra_measured_ms`, `sync_offset_ms`, `sync_ok`), `clipping_repair`, `notes`.

## duck

`duck --music FILE (--speech FILE | --voice FILE) [--duck -14] --out FILE`

Speech spans come from the file, or from `silencedetect` on the voice (-35 dB, 0.35 s; 12 dB under the voice's
loudness when it is quieter than -30 LUFS). The gain envelope: down `--duck` dB under speech, the fall starting 0.45 s
before a phrase and landing 0.25 s before it, the rise starting 0.15 s after it and lasting 0.6 s, pauses under 0.8 s
held down. When a pause is too short for the rise to finish before the next fall, the two meet in a V (never a jump);
speech in the first 0.45 s starts the music already down. It is computed at 1 kHz, upsampled by ffmpeg, upmixed with
`pan=stereo|c0=c0|c1=c0` (never ffmpeg's own conversion, which applies a -3 dB pan law) and applied with
`amultiply`.

Writes the ducked music, `<out>.keyframes.json` (`[[0.0, 0.0], [0.55, 0.0], [0.75, -14.0], ...]`: seconds and dB,
strictly increasing) and `<out>.json` (schema `nexa-sound/duck-1`). In Remotion:
`volume={(f) => 10 ** (interpolate(f, kf.map(k => k[0] * fps), kf.map(k => k[1])) / 20)}`.

## mix

`mix [--dialogue F] [--voice F] [--music F] [--sfx F] [--ambience F] [--speech F] --platform P [--duck -14]
[--music-under 20] [--ambience-under 24] [--duration S] --out FILE`

The mix is as long as the dialogue or voice-over (else the longest input); give `--duration` with the video's
length when the music runs on after the last word, or its ending is cut (a warning says so).

1. Dialogue and voice-over are the anchor: each is set to -20 LUFS integrated (mono is measured and played as dual
   mono).
2. Speech spans from `--speech`, else `silencedetect` on the speech stems.
3. Music is ducked by the envelope, then set so that under speech it sits `--music-under` dB (default 20) below the
   anchor, measured on its momentary loudness inside the spans. With no speech it sits 2 dB under the anchor.
4. Effects stay at their cue gains (moved by the difference between the anchor and `reference_dialogue_lufs`).
   An ambience or room tone (`--ambience`, from the `ambience` command) is set `--ambience-under` dB (default 24,
   20 to 30 is natural) under the anchor, integrated, and never ducked: a room that dips under every line gives the
   edit away.
5. Summed with `amix ... normalize=0`, then the master: when peaks need it, a 4x-oversampled limiter
   (`alimiter ... level=disabled`) with the gain before it, then two-pass `loudnorm` with `linear=true`. Pass 2's
   JSON must say `linear`; if it says `dynamic` the ceiling drops and it runs again, and after 6 tries the command
   stops. The result is checked with `ebur128` and nudged once when loudnorm's meter and ebur128 differ by more than
   0.1 LU. `-ar 48000` is pinned.

| `--platform` | Integrated | True peak |
|---|---|---|
| youtube, reels, tiktok, facebook, web | -14 LUFS | -1 dBTP |
| podcast | -16 LUFS | -1 dBTP |
| broadcast | -23 LUFS | -1 dBTP |

Then it measures dialogue-only and music-only stretches and the end card (after the last speech) on momentary
loudness, and warns when music-only stretches are over 3 LU louder than the dialogue or the end card is 15 LU under
it. Writes `mix.wav`, `<out>_stems/` (the gain-staged stems as summed, before the master) and `<out>.json`
(schema `nexa-sound/mix-1`): `file`, `platform`, `target` (`I`, `TP`), `measured` (`I`, `TP`, `LRA`),
`normalization`, `master` (the attempts with both loudnorm passes), `stems` (per stem `source`, `file`, `gain_db`,
the rule used), `speech`, `duck` (`keyframes`, `depth_db`), `sections` (`dialogue_lufs`, `music_only_lufs`,
`end_card_lufs`), `warnings`.

## qc

`qc FILE [--brief F] [--kind music|sfx|mix] [--target S] [--listen] [--budget USD] [--project DIR]`

The kind comes from the file's report (`mix.json`, an effect's sidecar), else music. Measured checks (fail unless
marked warn):

| Check | music | sfx | mix |
|---|---|---|---|
| format | stereo, 44.1 kHz or more | 48 kHz stereo | 48 kHz 24-bit stereo |
| duration | +-50 ms of `--target` or the fit's target | same | same |
| clipping | a run of over 10 samples at full scale, or flat tops at the peak level (astats flat factor 20 dB) | same | same |
| loudness | LRA over 8 LU for a bed under speech (warn otherwise) | | -14 (target) +-1 LU, true peak at or under the target +0.1 |
| normalization | | | linear in `mix.json` |
| DC offset | over 0.5 % (on a Lyria original, warn up to 2 %: fit and loop remove it) | same | same |
| mono fold-down | over 3 LU lost when L and R are summed | | same |
| silences | 0.75 s or more under -50 dB inside the body | | warn |
| lead-in | warn over 0.3 s | | warn |
| ending | the last 50 ms above -35 dBFS without 6 dB of decay | | |
| tempo | over 4 % from the brief (half and double allowed; the grid is read with the brief's BPM) | | |
| vocals | timed lyric lines in an instrumental | | |
| peak, tail, attack | | peak over -0.5 dBFS; last 20 ms over -50 dBFS; attack after 0.3 s (warn) | |

`--listen` (music) sends the audio inline (64 kbps mono MP3, or 16 kHz WAV when ffmpeg has no MP3 encoder) to
`gemini-3.8-flash` with the brief and asks for the JSON verdict: `genre`, `mood`, `tempo_feel`, `instruments`,
`vocals_present`, `vocal_spans`, `sections`, `ending` (`ring_out`, `fade`, `final_hit`, `abrupt_cut`),
`fit_to_brief_1_10`, `problems`. About $0.01 (an estimate). Pass rule: every measured check passes, and with the
judge `vocals_present` is false for an instrumental, `fit_to_brief` is 7 or more and the ending is not `abrupt_cut`.
Without a key, run agy-watch-video on the file for a free listening check.

Writes `<file>.qc.json` (schema `nexa-sound/qc-1`: `kind`, `passed`, `summary`, `checks` with `id`, `ok`,
`severity`, `value`, `threshold`, `detail`, `loudness`, `judge`). For an original, the sidecar's `qc` and the library
line are updated. Exit 2 when it fails.

## library

`library [--mood M] [--bpm 100-110 | --bpm 104] [--min S] [--max S] [--passed]`

Searches `~/.nexa-sound/library.jsonl` (one line per take; later lines for the same id update it): `id`, `mood`,
`bpm` (measured), `bpm_requested`, `key`, `duration_s`, `file`, `sidecar`, `model`, `vocals`, `qc_passed`,
`qc_failed`, `created`. One BPM number means +-3. Passed takes come first; `exists` says whether the file is still
there. Reuse a take before paying for a new one.

## credits

`credits DIR --out CREDITS.txt [--strict]`: reads every sidecar, fit report, effect cue file, ElevenLabs effect,
ambience and clean-up report under `DIR` and writes the note for the delivery: a STATUS line first, each track with
its model, date, brief and untouched original (sha256), whether it was edited for the video, what the licence means
in plain words (Lyria's notes, and ElevenLabs' when any item came from it), the effects grouped by source and
licence, and any CC BY credit lines to paste. Anything from ElevenLabs made on a free plan, or on a plan the key
could not read, is listed under "STATUS: NOT FOR CLIENT DELIVERY"; `--strict` then exits 1 (nexa-video-creator's
`deliver` runs it this way).

## cost

`cost [DIR | ledger.jsonl] [--draft N] [--final N] [--listen N] [--elevenlabs N]`: with a folder, the ledger's calls
and spend by model and status; with counts, an estimate. Prices: `lyria-3.5` $0.08, `lyria-3-clip-preview` $0.04,
`lyria-realtime-exp` $0 (free for now), `gemini-3.8-flash` judge about $0.01 (estimate); ElevenLabs at API list
prices (2026-09-25): an effect or ambience loop budgeted at $0.02 (`--elevenlabs N` counts these), music $0.15 a
minute, voice isolation $0.12 a minute. A subscription's credits are what is really spent: the ledger keeps the
response's cost headers where ElevenLabs sends them.

## beats.py

`python3 beats.py TRACK [--bpm N] [--json]`: `{"bpm", "period_s", "bar_s", "beats", "downbeats",
"first_downbeat_s", "confidence", "downbeat_confidence", "fine_shift_ms", "duration_s"}`. 4/4 is assumed. With
`--bpm`, a tempo 3:4 or 2:3 from the autocorrelation's pick that lies within 8 % of the request wins when its
sixteenth grid explains the gaps between the strong onsets at least 0.08 better: dotted-eighth kicks and arpeggios
made a real Lyria take at 110 BPM read as 146.7.
