# Changelog: nexa-sound

The version is `SKILL_VERSION` in `scripts/sound.py`. Run the offline tests after every change:
`python3 -m unittest discover -s ~/.claude/skills/nexa-sound/tests` (about 35 s, no network, no keys), and run the
changed command once by hand on a synthetic file and measure the result.

## 2026.09.25.2 · the first live run

A Clip draft, two Lyria 3.5 finals and a listening-judge call on the live API (2026-09-25), then fit, mix and QC
on what came back. What the real answers changed:

- **No format request.** Lyria 3.5 refuses `response_format` audio/wav and audio/l16 ("Audio MIME type AUDIO_WAV
  is not supported for models/lyria-3.5"): both models answer in MP3, 44.1 kHz stereo, 192 kbps, with the C2PA
  manifest in the ID3 tag. Finals no longer ask for WAV and wait on a refusal first.
- **A paid take is never lost to a name clash.** A draft and a final started in the same minute took the same id;
  the final's paid audio could not be written over the draft's read-only original and the run crashed. Every id
  is now reserved at once with a lock file, and a take never saves over another's original.
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
- **Tests:** 56 (a race between two runs, blocked tracks, the DC warning and fit, dotted eighths, the fake answering
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
