# Changelog: nexa-sound

The version is `SKILL_VERSION` in `scripts/sound.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests` (about 55 s, no network, no keys), and run the
changed command once by hand on a synthetic file and measure the result.

## 2026.09.25.3 · ElevenLabs, measured against what was here

ElevenLabs joins as a music, effects, ambience and voice-isolation engine, each run head to head on the live API
against the engine it would replace (2026-09-25) and made the default only where it won:

- **`generate --engine auto|elevenlabs|lyria`.** ElevenLabs `music_v2_5` (or `music_v2`) takes the brief as a
  composition plan: one chunk per section at its exact length, sparse where the voice talks, no voices, and the
  mood's ending as a chunk of its own. With the ending only styled inside the last section, the 16 s take stopped
  mid-phrase (judged "abrupt_cut", 7/10); as its own chunk it resolved (10/10). 16.0 s exact, 112.0 BPM, 5.3 s to
  make. `auto` uses it when the key reads a paid plan, else a Lyria final.
- **`ambience`:** one ElevenLabs seamless loop tiled sample-exactly to the length, with fades and a report on each
  join (office room tone: 0.69 dB at the joins against 8.36 dB elsewhere; nothing audible).
- **`mix --ambience`:** a room tone or ambience stem 24 dB under the dialogue anchor, never ducked.
- **`clean --isolate [auto|elevenlabs|apple]`:** ElevenLabs' isolator on a paid plan (cafe chatter at 5 dB SNR:
  clarity 9, noise left 1, natural 8, against Apple's 7, 2, 5), else Apple's.
- **Effects stay on the synthesiser.** It won or tied 5 of the 6 presets tried against `eleven_text_to_sound_v3`
  (impact 10 against 3); ElevenLabs is for real-world foley. `sfx fetch` gains `--loop`, `--influence` and `--model`;
  a loop always uses v2 (the only model that loops) and the sidecar says so. A WAV download no longer converts onto
  itself (`_48k.wav`).
- **PCM is read, not assumed.** ElevenLabs PCM has no header; the channel count is the one whose implied length is
  nearest the asked length (within 25 %), which also holds for a 0.5 s click that comes back as 0.48 s.
- **Formats step down only on a format refusal.** PCM, then 320, 192 and 128 kbps MP3, only when the error names the
  format, the tier or the plan: an error about the composition plan no longer looked like one.
- **Licence from the plan, and `credits --strict`.** Every ElevenLabs file records the plan read at the time; free
  means non-commercial, unknown (a key without User access cannot read it) means not for delivery. `credits` now
  opens with a STATUS line and ElevenLabs' notes (individual plans, no film, TV or games, barred industries, no
  Content ID, effects only inside the mix); `--strict` exits 1, and nexa-video-creator's `deliver` runs it.
- **Freesound's new search.** `/apiv2/search/` (the text search was deprecated in November 2025), sorted by score,
  explicit sounds skipped; the key can come from the keychain too.
- The shared `elevenlabs_api.py` module (keys from the environment or the keychain, errors scrubbed of keys, busy
  and server errors retried, a timeout never resent) is identical in nexa-sound, nexa-speech and
  nexa-video-creator.

## 2026.09.25.2 · the first live run

A Clip draft, two Lyria 3.5 finals and a listening-judge call on the live API (2026-09-25), then fit, mix and QC
on what came back. What the real answers changed:

- **No format request.** Lyria 3.5 refuses `response_format` audio/wav and audio/l16 ("Audio MIME type AUDIO_WAV
  is not supported for models/lyria-3.5"): both models answer in MP3, 44.1 kHz stereo, 192 kbps, with the C2PA
  manifest in the ID3 tag. Finals no longer ask for WAV and wait on a refusal first.
- **A paid take is never lost to a name clash.** A draft and a final started in the same minute took the same id;
  the final's paid audio could not be written over the draft's read-only original and the run crashed. Every id
  is now reserved at once with a lock file, and a take never saves over another's original.
- **The ledger before the file.** The lost take above never reached the ledger either, since the line was written
  after the file; a paid call is now logged as soon as the answer arrives.
- **A track blocked after generation is made once more.** The same prompt passed at 17:26, came back as "Request
  blocked for an unspecified policy reason" after 22 s of generation at 17:33, and passed at 17:34. A block that
  arrives after seconds of work is retried once (logged at $0); a prompt blocked at once is still never retried.
- **3:4 tempo mistakes.** A take at 110 BPM with dotted-eighth kicks and arpeggios read as 146.7 BPM and failed QC.
  With the brief's BPM, a tempo 3:4 or 2:3 away that fits the gaps between strong onsets on a sixteenth grid
  clearly better now wins; QC reads the grid with the brief's BPM too.
- **DC and overs in fit and loop.** Lyria takes carry a 0.5 to 0.7 % DC offset and decode to +0.8 dBFS. The working
  copy is now 32-bit float through a 5 Hz high-pass, with a gain for 1 dB of headroom when needed, so cuts do not
  click and the 24-bit output does not clip. QC on a Lyria original warns about DC up to 2 % instead of failing.
- **Measured on the live answers:** the Clip draft was 25.6 s (not 30 s) and the final 64.0 s for an 18 s request;
  Lyria answered in 13.7 s (Clip) and 24.5 s (3.5); the judge heard no vocals and scored the fitted bed 10/10.
- **Docs:** `mix` follows the dialogue's length unless `--duration` says otherwise (the help said the longest input).
- **Tests:** 57 (a race between two runs, a failed save still in the ledger, blocked tracks, the DC warning and fit, dotted eighths, the fake answering
  as the live API does).

## 2026.09.25.1 · first release

- **Music from Google Lyria:** `brief` turns the video's length, cuts and speech into a Lyria prompt from 12 mood
  templates (sections with intensities, the drop on the heaviest cut, "Instrumental." last) and refuses artist, song
  and album names, quoted titles and person-named genres, saying why. `generate` makes drafts on Lyria 3 Clip ($0.04,
  at most 3 at a time), finals on Lyria 3.5 ($0.08, WAV asked for) and exact-length beds on Lyria RealTime (free for
  now, recorded with an 8 s preroll dropped). Originals are kept read-only with a sidecar (provider, prompt, every
  text part, SHA-256, C2PA, analysis, QC, licence), and every call goes into the project's ledger and the library.
- **Beat grid without numpy:** onset strength on 10 ms frames smoothed against bass ripple, autocorrelation weighted
  toward the asked tempo, a comb and a least-squares fit, downbeats from the kick band, a 1 ms refinement. On click
  tracks at 82, 104 and 126 BPM: tempo exact, downbeats within 1.2 ms.
- **Fitting to the picture:** `fit` lands on the target to the sample with whole-bar cuts or loops where bars match,
  one-beat equal-power crossfades on downbeats, phrase-sized edits preferred, the real ending kept (an abrupt one is
  replaced by a fade on a downbeat), the start moved up to 2 s to land cuts on downbeats, and every choice in
  `fit.json`. `loop` makes seamless whole-bar loops.
- **A synthesiser the skill owns:** 23 presets (whoosh, whoosh-short, swipe, swoosh-down, pop, bubble, click, tick, key,
  typing, ding, chime, notify, success, error, riser, downlifter, impact, boom, sub-drop, glitch, shutter, sparkle)
  from sine and FM partials and swept state-variable filters in plain Python: 48 kHz 24-bit stereo, peak -1 dBFS, no
  DC, no clicks at either end, the last 20 ms below -64 dBFS (below -60 at every allowed length, pitch and
  brightness), deterministic by seed.
- **Effects on the timeline:** `sfx place` resolves each cue (a file, the synthesiser, your folders, media-use in place,
  Freesound CC0, ElevenLabs on paid plans), aligns attacks, peaks or climaxes to the frame sample-exactly, levels each
  effect against a -20 LUFS dialogue anchor and records sources and licences. `sfx fetch` adds single online effects.
- **Dialogue clean-up:** `clean` runs the measured chain at 48 kHz (high-pass, afftdn from the measured noise floor,
  hum notches, EQ, optional de-esser, compressor, optional Apple voice isolation) and proves the result is in sync by
  cross-correlating 1 ms envelopes (within 2 ms, or nothing is written).
- **Ducking and mixing:** `duck` applies a gain envelope from the speech spans (no jump when a pause is short, no -3 dB
  pan law) and writes keyframes for Remotion. `mix` sets the speech anchor, the music 20 dB under speech, the effects
  at their gains, and masters linearly to -14, -16 or -23 LUFS with the limiter-first rule, checked with ebur128, with
  warnings for loud music-only stretches and quiet end cards.
- **QC and licences:** `qc` measures format, clipping (including clipped-then-lowered audio), loudness, silences, an
  abrupt ending, tempo, DC, the mono fold-down and vocals in an instrumental, and can ask a Gemini listening judge.
  `credits` writes the licence and provenance note for a client.
- **Review fixes before release:** a mix whose master falls back to dynamic mode never reaches `--out` (every try
  renders to a scratch file; only a linear result is moved into place); a steady signal whose loudness range measures
  0 (loudnorm then refuses linear mode) is brought to the target by one static gain instead; the mix is as long as
  the speech, with a warning for any stem of another length; "like a Rihanna song", "like the Beatles" and similar
  phrasings are refused; a `Lyrics:` section needs `--vocals` and its lines are checked for names too (a line may
  still open with "Like" and a capital); a refused WAV request is written in the ledger (at no cost); `fit` moves
  its file into place only after the length check.
- **Tests:** 51 offline tests with a fake Gemini server (Lyria 3.5, Clip, timed lyrics, a safety block, the judge, the
  models list), fake Freesound and ElevenLabs endpoints and a fake RealTime stream; they check that the fake keys
  appear in no file and no output.
- **Untested against the real services:** Lyria 3.5's WAV answer and text parts, image input, every part of Lyria
  RealTime, the judge's JSON answer, Freesound's and ElevenLabs' endpoints (see SKILL.md).
