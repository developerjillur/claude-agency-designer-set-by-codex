# ledgerly-launch

A 27 s SaaS launch promo for a fictional invoicing app (1920x1080, theme midnight), cut to a 110 BPM track. The
poster frame shows the promise and the problem (a receipt waiting to be billed), and two more receipts land on the
beats. The demo drags one receipt photo from the desktop into the app, the app reads it and drafts the invoice by
itself (the same lines and total as the receipt), and one click sends it: the claim is "Invoices in one click", and
the demo shows exactly that. Then reminders that go out over days, three currencies each shown on an invoice, and an
end card where the payment arrives on the last downbeat and the same invoice gets its Paid stamp on the song's last
kick. The invoice's story (made, sent, paid) runs once, in order. One brand mark everywhere (`src/brand.ts`: the
lockup, the end card and the browser tab). The brand, its clients and its `.example` address are invented.

## Run it

```bash
python3 ~/.claude/skills/nexa-remotion/scripts/nrk.py new my-ledgerly-launch --format youtube --seconds 27
cp -R examples/ledgerly-launch/src/* my-ledgerly-launch/src/
```

Then make the sound (the files are not in the repository) and put the mastered track at `public/audio/mix.wav`:

1. Music: a `nexa-sound` brief and `generate`. `fit` cut this track at a random bar with a 0.3 s fade and left 1.9 s of
   silence, so the cut keeps the song's own ending instead: its first 8 bars, then its last 4 (the loud middle goes,
   which also removed a 5 dB jump), joined on a downbeat under a whip with a 0.55 s equal-power crossfade:
   `ffmpeg -i TRACK -filter_complex "[0:a]atrim=0:A+0.27,asetpts=PTS-STARTPTS[a];[0:a]atrim=B-0.27,asetpts=PTS-STARTPTS[b];[a][b]acrossfade=d=0.55:c1=qsin:c2=qsin,atrim=0:27" music_fit.wav`,
   where A and B are the downbeats of bar 8 and bar 24 (`TRACK.beats.json`).
2. Effects: `sound.py sfx place sfx/cues.json --duration 27 --out sfx/sfx.wav --offline`.
3. Mix: `sound.py mix --music music/music_fit.wav --sfx sfx/sfx.wav --platform youtube --duration 27 --out mix.wav`,
   then `qc mix.wav`.

Check and render: `nrk.py stills my-ledgerly-launch --every 1 --guides`, `nrk.py render my-ledgerly-launch --preset web`,
`nrk.py qa my-ledgerly-launch`. What each fix was for is in `../../references/field-notes.md`.
