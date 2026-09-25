# container-route

A 33 s English map story (1920x1080, theme data): a container's typical sea route from Chattogram to Rotterdam through
the Suez Canal. The ship is at its pin on the poster frame and leaves on "leaves"; each leg starts on its word and
lands on the place's name, and the camera follows the ship so it never leaves the frame. Paper land on a clear blue
sea, sea names set beside the route (the Red Sea's turned along the sea), pins that stay to the last frame, opening
and closing title cards.

## Run it

```bash
python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py new my-container-route --format youtube --seconds 33
cp -R examples/container-route/src/* my-container-route/src/
```

Then make the sound (the files are not in the repository) and put the mastered track at `public/audio/mix.wav`:

1. Voice: `speech.py render vo/script.txt --profile PROFILE --out vo`, `master vo`, `align vo --engine gemini`
   (nexa-speech); the word timings used by the scenes come from `vo/words.json`.

2. Music: a `nexa-sound` brief and `generate`, then `fit` to the length (`fit TRACK --target 33`).
3. Effects: `sound.py sfx place sfx/cues.json --duration 33 --out sfx/sfx.wav --offline`.
4. Mix: `sound.py mix --voice vo/vo_48k.wav --music music/music_fit.wav --sfx sfx/sfx.wav --platform youtube --duration 33 --out mix.wav`, then `qc mix.wav`.
5. The mix keeps the music 20 dB under the voice after the last word, so lift the end card:
   `ffmpeg -i mix.wav -af "volume='if(lt(t,29.95),1,min(4,1+(t-29.95)/0.6*3))':eval=frame" mix_tail.wav`, and measure.

Check and render: `nrk.py stills my-container-route --every 1 --guides`, `nrk.py render my-container-route --preset upload`
(CRF 12: thin route lines and small labels survive YouTube's encode), `nrk.py qa my-container-route`.
What each fix was for is in `../../references/field-notes.md`.
