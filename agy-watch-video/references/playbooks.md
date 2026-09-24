# Playbooks: what to look for, and what to ask

Each goal sets what the passes look for and the checklist the review goes through (`GOAL_FOCUS` and `GOAL_CHECKLIST`
in `scripts/watch_video.py`). After the report, Claude asks the follow-up questions below with `ask`, one moment at a
time, and opens the evidence frames for anything the answer depends on.

The rule for every playbook: ask neutral questions. "What is in his hand?" beats "Is he holding a hose?". "Describe
any defect you can see; if there is none, say so" beats "Find the glitches". A leading question gets the answer it
leads to.

## promo: ads, reels, shorts, promos

Run `watch VIDEO --goal promo --platform reels` (or `tiktok`, `shorts`, `youtube`, `facebook`) at `standard`, or at
`deep` for a final check.

Look for:
- **Hook (0 to 3 s):** what is on screen, whether the product, person or promise is visible, and whether there is
  motion or text in the first second. A slow logo reveal or an empty establishing shot loses the scroll.
- **Brand:** the first time the brand or logo appears, and how long it stays on screen in total.
- **Message and offer:** one clear message. The price, date or offer is readable as a fact.
- **Text:** size (at least about 4.5% of the frame height for body text on a phone), contrast, and time on screen.
  Reading time is about 3 words a second, plus half a second.
- **Call to action:** present, specific (the action and the thing), on screen long enough, and inside the safe zone.
- **Contact details:** the phone number, address or link is readable. Check the digits with your own eyes; models
  misread them.
- **Pacing:** the average shot length from the measured cuts. Short-form usually cuts every 1 to 3 s.
- **Audio:** music against voice, loudness near the platform target, and nothing clipped.
- **End:** the last frame holds long enough to read.

Ask:
- `ask V "What exactly is on screen in the first 3 seconds, and when does the brand first appear?" --from 0 --to 3`
- `ask V "Read the phone number and address shown here." --at 55`: auto zoom, two models; then look at the frame.
- `ask V "Is any text cut off, covered or too small to read on a phone?" --from 48 --to 60`

## ai-video: generated clips

Run `watch VIDEO --goal ai-video --depth deep`. Use `forensic` for a hero clip.

Look for, and report only with a frame that shows it:
- identity drift (face, hair, clothes change between frames);
- hands and fingers (count, merging, a grip that does not hold the object);
- text that changes or melts from frame to frame;
- physics: contact without support, objects passing through each other, liquids, gravity, shadows that disagree with
  the light;
- object permanence: things that appear or vanish without cause;
- flicker and popping, measured (`flicker_events` in the report).

False positives: real footage has motion blur, compression and rolling shutter. None of these is a generation
artefact. In testing, a prompt that said "note every glitch" made Gemini 3.1 Pro report "extreme AI morphing" on real
drone footage and reject it. The skill's prompts are neutral. Confirm every defect with
`verify V "<the defect>" --at T --span 1` (the models never see the claim) and look at the frames yourself before
reporting it.

## motion: motion graphics, renders, HyperFrames and Remotion output

Run `qa VIDEO --platform ... --strict` first (seconds: black and frozen frames, flicker, loudness, specs), then
`watch VIDEO --goal motion --depth deep --expect copy.txt` (every approved line is looked for on screen).

Look for:
- when each element enters and leaves, and whether its easing is smooth (no jumps between frames);
- overlaps and collisions, and text cut off by the frame or by other elements;
- text size and legibility on a phone, and time on screen long enough to read;
- safe zones on social platforms;
- the final hold;
- typos: compare the on-screen text with the script. Use `ask` on each title card; for Bengali, two models must agree
  and Claude checks the frame.
- audio sync: a hit on the beat, voice against captions.

Ask:
- `ask V "When does each piece of text appear and disappear?" --from 0 --to 8`
- `ask V "Does any element overlap another or leave the frame?" --at 4.2 --span 1`

## screen: screen recordings and bug reproductions

Run `watch VIDEO --goal screen --depth deep`. Screens carry small text, so the text check and zoom matter most.

Look for:
- every step with its time: app and screen, what is clicked (look for the cursor and pressed states), what is typed,
  what changes;
- every message, toast, dialog or error, with its exact text (Apple Vision OCR confirms Latin text);
- the moment the behaviour goes wrong, and the state just before it;
- the environment: app, version, OS, browser, URL bar;
- steps to reproduce, written from the steps.

Ask:
- `ask V "What error or message appears, word for word?" --at 12 --region auto`
- `ask V "What did the user click or type just before the error?" --from 9 --to 12`

Screens change in small areas, so the measured cuts are few. Use `--depth deep` (2 frames a second) or `forensic`
around the moment of the bug. A recording longer than a few minutes: run `watch --depth quick` to find the moment, then
`deep` with `--from/--to`.

## footage: camera and drone footage

Run `watch VIDEO --goal footage` (standard).

Look for: shots and takes with in and out points, usable ranges, the best moments, exposure (measured luma and
clipping), focus and blur (measured), stability and horizon, distractions (wires, passers-by, reflections, a crew
member in the frame), the camera move, and the people and what they do.

Ask:
- `ask V "Which 3-second stretch is the cleanest to use as an opener, and why?"`
- `ask V "Is anyone from the crew, or the drone pilot, visible?"` (look at the frame yourself before saying yes)

## tutorial: lessons, talks, demos

Run `watch VIDEO --goal tutorial --lang <code>`; add `transcribe` for subtitles.

Look for chapters and steps with times, what is on screen at each step (code, commands, slides; OCR for Latin
text), key points, and anything skipped or unclear.

Ask:
- `ask V "What command is typed here, exactly?" --at 3:12 --region auto`
- `ask V "Where does the speaker explain X?"` (the locate pass searches the transcript and the proxy)

## general

Run `watch VIDEO` for what happens, who and what appears, text, speech and sound, and the measured quality.

## Checking a claim before reporting it

1. Find the time (the report's evidence, `moments`, or the frame table).
2. `verify V "<the claim>" --at T --span 1`: the claim becomes a neutral question the models answer without seeing
   the claim, on 8 frames a second with auto zoom; a judge then compares their answers to the claim.
3. `supported` or `contradicted`: report it with the time. `unclear`: open `check_frames` and decide yourself, or
   report it as unverified.
