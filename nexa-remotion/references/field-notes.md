# Field notes: what three real builds taught (2026-09-26)

Three finished videos were made with the kit end to end (voice, music, effects, build, stills, QA, review): a 24 s
Bangla vertical tip video, a 33 s English map story and a 27 s SaaS launch promo. Their sources are in `examples/`.
Everything below was measured on those renders; each item cost a render cycle to find.

## Layout

- **9:16: words in a top band, the stage below it.** Captions and titles sit at the top of the safe area (y 280 to
  470); the phone, card or object sits under them and may run past the safe area's bottom as decoration. Every word
  stays inside the safe area: QA flagged a day-total card and a chart's last label that sat below 65% of the height,
  where Reels puts its caption. Compute it: frame y of anything inside a phone = phone top + bezel + screen y.
- **A light interface inside a dark look needs its own theme.** Components read the theme, so a dark theme's cream
  text vanishes on a white phone screen or browser page: wrap the screen in `<ThemeProvider theme={makeTheme('studio',
  ...)}>`.
- **Full-frame components need a box of their own.** `LogoReveal` (and other `AbsoluteFill` components) fill their
  parent: put them in an absolutely positioned box with a height, and pass `background="none"` over a Ground.
- **Glyphs overhang their box.** A headline placed at `left: safe.x` put the ink of G and O 1 px outside the safe
  area; place text at `safe.x + 8` (the kit's `SafeArea` has a 4 px inset for this).
- **Push-ins move edges.** A 3% push around the frame centre moves text at the safe edge about 26 px outward; the
  kit's cards now anchor their push on their text edge.

## Time and motion

- **Frame 0 is the poster.** Captions pop in, so the first page is not on frame 0: open with a big title for the first
  sentence and start captions with the second. A logo lockup can be fully present on frame 0 (`delay` negative).
- **Voice first, cuts a few frames early.** Cut to a scene 3 frames before the phrase that opens it; land readable
  elements 2 to 4 frames before their word.
- **Music cuts:** make each transition's midpoint land on a downbeat (`music_fit.json` has `downbeats_out`): for a
  12-frame transition, the next scene starts 6 frames before the downbeat, and each scene's duration adds the overlap.
- **"Frozen picture" QA is strict (0.5 s).** A slow camera drift under about 10% over a hold is not seen as motion.
  Fix it with story beats (a click, a toast, a highlight that follows the voice), a camera move of 10% or more, or a
  drifting light (`Ground drift={0.25}`), never by moving text that is being read.
- **Hand-offs:** the object leaving must be gone before the next title lands on its word (the phone left at "চলে",
  the title rose on "আজই"); a title and captions that share a band must not overlap for even a frame.
- **Form typing:** focus, type, blur, then focus the next field; two fields focused at once reads as a bug.

## Sound

- **Pre-mix with nexa-sound, then play one track.** `mix --voice --music --sfx --platform P --duration S` gives a
  mastered file (-14 LUFS for social); Remotion plays it with one `<Audio>`.
- **`--duration`:** without it the mix is as long as the voice and cuts the music's ending.
- **The bed stays low after the voice ends.** The mix keeps music 20 dB under the voice, so an end card after the
  last word can sit near -32 LUFS (feels broken). Lift the tail: `ffmpeg -af "volume='if(lt(t,T),1,min(4,1+(t-T)/0.6*3))':eval=frame"` from the last word,
  then measure (the map story's end card went from -31.6 to -19.5 LUFS, the file stayed at -14.0).
- **Effects on actions only:** a pop per arrival, a click per press, a whoosh per whip, a ding when a number lands;
  -15 to -20 dB under the voice.

## Bangla

- `Counter` in `bn-BD` puts ৳ after the number; for Bangladeshi price style use `prefix="৳"` with `digits="bangla"`.
- Split Bangla by words or graphemes only; the kit's type module does, and every conjunct rendered correctly.
- Gemini word timings come in steps of about 0.1 s: fine for captions and cuts. When a hit must land on a syllable,
  snap the word edges to the measured speech (nvc's transcribe does); never switch Bangla to whisper for it: on this
  short's 22 s voice whisper garbled correct words all through (সহোজ, তিন্টা, আখনো), and its reading of a real slip
  (ফোনেই said "ফনিই") was lost among them: two reviews read past it. Gemini's clean transcript showed both slips at
  once (হিসাব said "হিসেব" too). nexa-speech's `qa --asr` now names such a word; fix it with another take or a
  `{হিসাব|হিশাব}` respelling.
- **After a voice fix, re-time from the new words:** each cue is its word's start, each cut 3 frames before its
  phrase, and every effect moves by exactly the frames of the picture event it belongs to (a pop with its card, a
  click with its press), not by the audio's shift.
- **Hind Siliguri draws the digit ১ as a small hook** that reads as ৲ ("তেল, ১ লিটার ৳১৯০" read as ৳৯০). The dhaka
  and corporate themes now use Noto Sans Bengali for text; Anek Bangla, Noto Serif Bengali, Tiro Bangla, Baloo Da
  2, Atma and Galada draw it right. Never set prices or dates in Hind Siliguri.
- Default caption pages split phrases ("তিনটা | সহজ নিয়মে।"): use `sentenceMs` (the type module's captions doc).

## Maps

- On a light theme, give the sea a pale colour (`colors={{ocean, stage}}`): white sea and grey land read as a blank.
- A sea route needs waypoints on water (round Sri Lanka's south cape into Colombo, Bab-el-Mandeb, the canal, round
  Iberia) and `lift={0}` (ships do not fly arcs).
- The Route's marker fades at each leg's end; for a many-waypoint voyage draw your own marker on the same schedule.
- Sea labels you place with `useMap().project` must fade near the safe-area edge, or a pan leaves "Bay of Be" cut at
  the frame edge.

## What a first-watch review caught after QA passed

QA measures the file; it cannot tell whether the video works. A fresh reviewer (the `remotion-reviewer` agent, given
only the render) found these in videos whose QA was clean. Each is now a rule:

- **The hook must show the problem and move within the first second.** A neat ledger held still for 1.5 s said
  nothing about "still in a notebook?"; the fix was a ledger with a corrected price and a total that is struck and
  rewritten in red in frames 6 to 30, a slow float, and the circle on the spoken word.
- **One red thing at a time.** Caption pill, step badge, input focus and button were all red at once; the app went
  green and the badge marigold, so the eye had one target.
- **Say how.** A call to action with no tool, place or link fizzles; one line of "where" is enough (no brand needed).
- **Recaps use the voice's words.** An end-card rule that paraphrased the voice ("তুলনা করুন" against "দেখুন কোনটা
  বেশি চলে") read as a different rule.
- **Marks never touch numbers.** A check drawn beside a total ran into its last digit and out of the card; marks go in
  a label row inside the card's padding.
- **End captions with the scene.** The last caption hung alone for 0.3 s after the phone left; end the captions with
  the phone's exit and start the close while it leaves.
- **Audience details.** An iPhone with a Dynamic Island for a Bangladeshi shopkeeper audience read as foreign
  (`PhoneFrame camera="dot"`); "(example)" glued to a date read as part of it (a separate tag).
- **App screens change like apps.** A hard cut between screens inside a phone reads as a glitch; slide the next screen
  in over the last (the Bangla short's `Screen` wrapper).

- **Claims match the demo.** "Invoices in one tap" over a two-click desktop flow, and "Snap a receipt" with the
  receipt already on screen, read as false. Both changed: the claim is "one click", and the demo drags a receipt photo
  in, the app drafts the invoice by itself, and one click sends it.
- **One brand mark.** A disc with a C cut out read as a copyright sign next to the name, and the browser tab showed a
  different tile. One mark in `brand.ts`, the same shape as the tab's letter tile, everywhere.
- **States follow the story.** "Draft ready" after "Sent", and "Paid" above "Total due", read as bugs in an invoicing
  demo: the invoice card takes its status per frame.
- **Music ends, it does not stop.** `fit` cut the track at a bar with a 0.3 s fade and left 1.9 s of silence. The cut
  that works keeps the song's own ending: its first 8 bars, then its last 4, joined on a downbeat under a whip. That
  also removed a 5 dB jump, and the video grew to 27 s so the song's final stop lands 0.9 s before the end, with the
  Paid stamp on its last downbeat.
- **A click that changes nothing is a dead button.** The end card lost its pointer; its last beat is the stamp.
- **The traveller never leaves the frame.** The camera held on Suez while the ship sailed out of shot for 2 s: key the
  camera to the ship's legs, and give a slow leg (the canal) to the close shot.
- **The picture moves with the first words.** The ship left 5 s in, on "crosses"; it now leaves on "leaves", and the
  poster frame has its pin and the ship.
- **Labels sit beside the route, never across it.** Move sea names off the line, turn a narrow sea's name along the
  sea, and fade them for the whole-trip view, where they collide with everything.
- **Land and sea must separate.** Grey land on a pale sea measured 1.34:1 and read as washed out: paper land on a clear
  blue sea with a drawn coast.
- **QA's frozen picture sees eased cameras.** A move that eases in (the first 0.5 s) or an eased push through a hold
  (1.3 s at Colombo, the last 0.6 s of an end card) was flagged: open on a linear move, push 20% or more through a
  hold, end on a linear push.
- **OCR boxes run past the ink.** A card sliding in from the right, clipped exactly at the safe edge, still flagged:
  clip 14 px inside it.
- **A dark app in a dark film.** A white browser window swiping in and out made six brightness-jump flags; the dark
  app UI made none.

A second review of the fixed videos found no broken moments but a new layer of problems, all fixed:

- **A story runs once.** The hook took the invoice from Draft to Paid, then the demo made the same invoice again as a
  Draft: "paid before it is made". The hook now shows the problem (receipts landing on the beats), and the invoice
  first appears in the demo.
- **Numbers on screen must add up.** An invoice made "from the receipt" totalled $648 next to a $108 receipt (a work
  line the receipt did not have); the invoice now carries exactly the receipt's lines.
- **Show every claim on the product.** "Get paid in USD, EUR, GBP" over three chips read as a slide; an invoice in each
  currency now lands under the word.
- **A see-through stamp shows what is under it.** The status pill read through a translucent PAID stamp: make it opaque.
- **The phone's lower screen sits under the platform's white caption.** On Reels the username and caption sit over the
  bottom third; a cream screen there makes them unreadable. Fade the device into the ground below the safe area.
- **Show the habit, not a tick.** "Reconcile the day's total" needs the thing it is matched against (the cash counted),
  then the check.
- **Every caption line keeps its phrase.** "মোট / বিক্রি" and "কোন / জিনিস" split determiners from their nouns; the
  kit's captions now never end a line on such a word, and a spoken "এক," joins its sentence (`silenceMs`).
- **Circle the mistake, not the page.** The hook's circle went round the whole ledger; it now goes round the wrong total.
- **A label that cannot sit by its point must go.** A pin label clamped to the safe edge stayed put while its pin slid
  away, then vanished in place; labels now fade as the edge pushes them off their point. Sea names fade by their width,
  not their centre ("Mediterranean Sea" crossed the edge while its centre was inside).
- **End on a beat that shows why.** The payment notification lands on the last downbeat and the stamp on the song's last
  kick, so the ending has a cause and a hit.

Two QA findings came from the kit and are fixed there: a bright device leaving on an ease-in fade made a one-frame
luma jump (DeviceRise now fades on a sine curve), and icons in the platform's caption zone were read as text by the
OCR (a house as "h", a person as "OK", a bar chart as "ılı", even a faint calendar as a CJK letter). Keep the
platform's caption zone plain: on the phone that zone is under the app's own caption and buttons, and a plain
background there is what keeps them readable, so a phone's lower screen stays empty on purpose.

## Tooling

- Write TSX through a quoted heredoc (`<<'EOF'`) or a Python file: an unquoted heredoc lets the shell eat `${...}` in
  template strings and leaves broken code.
- `nrk.py stills --frames` at every cue and 12 frames later catches most problems before a render (`--guides` draws
  the safe area on each frame); `nrk.py qa` then finds what stills cannot (safe-zone OCR, frozen stretches,
  loudness), and a first-watch review finds what QA cannot.
