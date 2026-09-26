# bangla-hisab-short

A 24 s Bangla tip video for shop owners (1080x1920, theme dhaka): a paper ledger hook, one phone as the stage for three rules (typing an entry, the day's total counting up in Bengali digits, the month's best sellers as a bar chart), Bangla TikTok-style captions from the voice's word timings, a recap end card.

## Run it

```bash
python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py new my-bangla-hisab-short --format shorts --seconds 24
cp -R examples/bangla-hisab-short/src/* my-bangla-hisab-short/src/
```

Then make the sound (the files are not in the repository) and put the mastered track at `public/audio/mix.wav`:

1. Voice: `speech.py render vo/script.txt --profile PROFILE --out vo --asr`, then `master vo` and
   `align vo --engine gemini` (nexa-speech); the word timings used by the scenes come from `vo/words.json`. The
   `--asr` gate has Gemini transcribe every take and names a word heard differently: here হিসাব came out as হিসেব
   (the script now steers it with `{হিসাব|হিশাব}`) and ফোনেই as ফনি in 3 of 6 takes; `pick vo c002 3` chose a
   clean one. Never check the Bangla with whisper.

2. Music: a `nexa-sound` brief and `generate`, then `fit` to the length (`fit TRACK --target 24`).
3. Effects: `sound.py sfx place sfx/cues.json --duration 24 --out sfx/sfx.wav --offline`.
4. Mix: `sound.py mix --voice vo/vo_48k.wav --music music/music_fit.wav --sfx sfx/sfx.wav --platform reels --duration 24 --out mix.wav`, then `qc mix.wav`.

Check and render: `nrk.py stills my-bangla-hisab-short --every 1`, `nrk.py render my-bangla-hisab-short --preset web`, `nrk.py qa my-bangla-hisab-short`.
What each fix was for is in `../../references/field-notes.md`.
