# Intake, treatment and storyboard templates

Copy these into the project folder as `brief.md` and `storyboard.md` and fill them. Delete lines that do not apply.

## Intake sheet

```text
Client / product:
Audience (one reader: who, where they see it, what they know):
The one message (one sentence):
What the viewer should do or feel after it:
Platform(s) and formats: youtube 1920x1080 | shorts 1080x1920 | feed 1080x1350 | square 1080x1080
Length (promised):            fps: 30
Voice: none | TTS (voice, language) | client recording (file)
Music: none | bed | drives the cut (file or nexa-sound brief)
Brand: colours (hex with roles), fonts, logo files, words they use and avoid
Facts and sources (every number that may appear):
Assets (screens, footage, photos, data files) and their licences:
Must include / must avoid:
Deadline and deliverables (masters, variants, captions files):
Defaults I chose (state them):
```

## Treatment

```text
Scene sentence (light and place):
Direction A / B / C: one paragraph each + dials (energy, density, ground, depth, camera, type, texture, colour, sound)
Kept: X, because ...
Style: nexa-remotion-styles entry + theme (makeTheme overrides)
Signature move (the product's verb), where it appears (2 or 3 scenes):
Composition systems per act (adjacent beats differ):
Sound: voice, bed, effects vocabulary (one per event)
```

## Shot list with frame arithmetic

Write frames, not seconds. At 30 fps, 1 s = 30 frames.

```text
fps 30, total promised 2250 f (75 s)

#  start  len  scene            hero element                 copy (verbatim)            cues (word -> frame)        system          transition out
1      0   150  Hook             product shot rises           "Invoices in one tap"       "one" -> 38, "tap" -> 52    full-bleed      cut
2    150   240  Problem          stack of paper falls         "Month-end takes 3 days"    "3" -> 212                  oversized type  cut
3    390   300  Feature 1        cursor drags a card          ...                         ...                         UI + camera     slide 15
...
sum of len = 2280, transitions = 30 (2 x 15) -> total 2250  OK
```

Checks before building:
- The hero is on screen within the first 3 s (1 s for shorts), and frame 0 is composed.
- Every scene has one hero; readable text holds at least `readingFrames`.
- Pacing: a new beat every 3 to 9 s; nothing static over 3 s.
- Adjacent scenes use different composition systems.
- The sums match the promised length (with transitions subtracted).

## Cue table (top of each scene file)

```ts
// Scene 3, starts at 390 (global). Frames are local to the scene.
const CUE = {
	cardLands: 18, // "drag" at 0:13.6
	stackSnaps: 44, // "snaps" at 0:14.5
	counterStarts: 60, // "three" at 0:15.0
	counterLands: 82,
	hold: 150, // reading time of the caption
} as const;
```

Word times come from the transcript in seconds: `local = Math.round(seconds * fps) - sceneStart`. Readable
elements land 1 or 2 frames before their word; hits land on the word.
