# Formats, beat maps, budgets and the script file

Pick the format, take its beat map as the skeleton (`script.py new` writes it with the roles filled), then write.
Evidence: `research/R1-youtube-longform.md` §5 and §6, `R2-shortform-and-ads.md` §3 and §4, `R3-storytelling.md`
§3.1, `V3-story-part2.md` ST1 to ST3, `V4-story-part3.md` T1 to T7, `V5-humm-storytelling.md` T4,
`V6-kallaway-vishen.md` T-V6a to T-V6c.

## 1. Formats and pace

| Format (aliases) | Medium | wpm (English) | Notes |
|---|---|---|---|
| `youtube-long` (video-essay) | video | 160 | explainer default |
| `explainer` | video | 160 | Mode A |
| `documentary` | video | 150 | Mode B |
| `tutorial` | video | 150 | roadmap first, steps as chapters |
| `commentary` | video | 170 | evidence first |
| `short` (reel, tiktok, shorts) | video | 165 | up to 180 s |
| `ad` (ugc-ad, vsl) | video | 150 | modular pack |
| `talk` | listen | 140 | nested loops |
| `podcast` | listen | 155 | |
| `blog` (article, newsletter) | read | n/a | see `blog.md` |

Pace measured on real channels (words per minute of runtime, R1 §5.1): Kurzgesagt 157 to 167, Johnny Harris 158 to
171, Veritasium 185 to 190, Mark Rober 192 to 197. Hindi creators in our reference videos ran 173 to 252 (median about
205). Language factors in `script_core.py`: Hindi 1.25, Bangla 0.84, Banglish 0.9 against English. Bangla has no
measured creator sample yet: time a Bangla script with the real TTS voice (nexa-speech) before the edit, and set
`meta.wpm` to the measured rate.

**Word budgets for shorts and ads** (R2 §4.1, at 2.3 to 2.8 words a second):

| Length | Spoken words |
|---|---|
| 6 s bumper | 12 to 15 |
| 15 s | 30 to 40 |
| 30 s | 65 to 80 |
| 45 s | 100 to 120 |
| 60 s | 135 to 160 |
| 90 s | 200 to 240 |

Long-form: runtime minutes = words / wpm; a 12-minute explainer at 160 wpm is about 1,900 words. Length follows the
story; YouTube publishes no ideal length (R1 §5.1).

## 2. Short-form (20 to 60 s)

**Story short** (R3 T1, V3 ST2): 0 to 2 s the hook (the most surprising moment or the contradiction, shown first);
2 to 5 s only the context needed to see the gap; BUT, the first complication (PP1 by about a third); SO, what it
forces; one more BUT and SO, 5 to 10 s each; the payoff answers the hook exactly; the last line closes the hook's loop.

**Organic templates** (R2 §3.1):

| Template | Plan |
|---|---|
| Loop (7 to 15 s) | open mid-sentence on the payoff image; end on a line that runs into the first one; no end card |
| List, "3 things" (20 to 35 s) | number plus stakes at 0 to 2 s; each item 6 to 8 s (name on screen, one line of why, one visual proof); best last; an open question |
| Story (30 to 60 s) | cold open at the tensest moment; one line of context; two escalations; a turn; the payoff; a last line people want to send |
| Tutorial (20 to 45 s) | the result in the first 2 s; numbered steps of 6 s at most; the common mistake; the result again; a save prompt |
| POV (7 to 20 s) | the setup in on-screen text; an acted reaction; little voice-over; licensed audio |
| Green screen (20 to 45 s) | a screenshot, review or chart behind the creator; the hook reacts to it; two or three points; a clear opinion |

Pace in shorts: a new shot, angle, zoom or text change every 1.5 to 3 s in the first 6 s, then every 2 to 4 s; 6 or
more distinct shots in 30 s (R2 §4.2, heuristic). Captions follow the voice in chunks of 1 to 4 words at 20
characters a second or fewer; one text zone at a time; keep critical text between 14 % and 65 % of the height and
8 % to 86 % of the width to clear every platform's buttons (R2 §4.3, §4.4).

## 3. Ads

**30-second ad** (R3 T3): normal, a person and a want (0 to 5 s); explosion, the problem (5 to 15 s); guide and plan,
the product as the tool, never the hero (15 to 24 s); new normal, a specific result and one CTA (24 to 30 s).

**UGC and performance structures** (R2 §3.2, 30 s unless noted):

| Structure | Beats |
|---|---|
| Problem, agitate, solution | 0 to 3 the problem shown; 3 to 8 its specific cost; 8 to 20 the product solving it on camera; 20 to 26 proof; 26 to 30 CTA with the offer |
| Testimonial | 0 to 3 the result in the creator's words; 3 to 10 life before; 10 to 20 the product in use plus one surprising detail; 20 to 26 one doubt answered; 26 to 30 recommendation and CTA |
| Founder story (30 to 45 s) | the moment it started; the problem; what they built and the one insight; proof; an invitation |
| Before and after (15 to 20 s) | the after; the dated before; the process with the product; CTA. Check the platform's policy first |
| Demo | a test that looks impossible; one unbroken take; the one mechanism behind it; CTA |
| Reasons why | "3 reasons I switched"; three reasons of about 7 s, each with its own shot; CTA |
| Objection handling | the objection, bluntly; the answer with proof; CTA with risk reversal |
| Us vs them | a side-by-side test; two or three substantiated differences; the verdict; CTA (comparative claims must be true and backed) |

**Long direct response** (90 to 160 s, the Harmon Brothers approach, R2 §3.3): a funny cold open on the problem;
character and product; education (why the problem exists); demonstration; proof; objections; offer, guarantee, CTA;
a callback joke and the CTA again. Cut 6, 15 and 30 s versions from the same footage. The ad runs as long as the sale
needs.

**Brand story** (30 to 60 s, R2 §3.4): a human moment; tension; the brand as enabler, not hero; the emotional payoff; a
sign-off with a sonic or visual brand asset.

**The pack:** 5 hooks of at least 4 types, 2 bodies, 2 CTAs, and which combinations to test first (R2 §8 rule 7).
The ask names what the audience wants, in the brief's words, and calls back the objection it answered: "Follow for
the story behind the food, not the hype" for viewers who want "the story behind a food spot" and fear "another hype
video". In the 2026-09-26 benchmark both Gemini judges preferred that ask to "Follow for the numbers behind the next
spot", which answered the objection but offered the viewer something they never asked for.
The CTA is a verb plus an object plus a reason, spoken and shown, matching the button: "Tap Shop Now, the starter kit
is 20 % off until Sunday" (R2 §4.5). Urgency needs a real date or count.

**UGC creator brief** (R2 §5): an outcome-based brief beats a word-for-word script, which comes out looking like a
testimonial and sounding like an ad. Give the objective, a mindset persona, the intent being resolved, 2 or 3 story
directions, a visual hook direction, value props in plain speech, energy references, must-say claims with proof,
forbidden claims, the disclosure rule, specs and the usage rights needed.

**Compliance** (R2 §6): claims need evidence before they run; no personal-attribute callouts; no cure, guaranteed
result or quick-money claims; paid creators disclose early, spoken and on screen; fake and AI-generated testimonials
are banned (FTC 2024); licensed music only; realistic synthetic people, voices or events carry the platform's AI label.
Set `meta.brand`, `meta.paid` and `meta.mode = "ad"`; the lint checks them.

## 4. Long-form video

**Explainer, 6 to 15 min** (R3 T2, R1 §6, V3 ST1; percent of runtime):

| % | Beat | Roles |
|---|---|---|
| 0 to 5 | cold open in medias res; the question in one sentence; the stakes | hook |
| 5 to 20 | the common belief or normal world, what can be lost and gained, then the anomaly | identity, stakes |
| 10 to 35 | PP1 and the investigation; a BUT turn; each section ends on a re-hook | pp1, conflict |
| 40 to 55 | the midpoint reversal that reframes the question | surprise |
| 50 to 75 | complications, the best counter-argument, the cost | conflict, choice |
| 75 to 85 | PP2: the favourite explanation fails or the stakes land | pp2 |
| 85 to 97 | the answer, then what it means for the viewer | change, value |
| last 5 to 20 s | callback to the cold open; one CTA to the next video | cta |

Explainers state the common misconception and refute it: Muller's study of 364 physics students found versions that
confronted misconceptions taught more (effect sizes 0.79 and 0.83) than a clear straight lecture that students rated
clearer (R1 §2.4).

**Documentary or video essay, 15 to 30 min** (R1 §6): cold open in a scene; the thesis question by about 1:00; the
world before; the inciting event; complications joined by but and therefore; a re-engagement every few minutes
(MrBeast's notes plan them near 3:00 and 6:00); the midpoint reversal; the climax and answer; what it means now.

**Story, vlog or challenge (Mode B)**, the beat sheet taken from the analysed train vlog (V4 T3; act percentages are
ours): Act 1 (10 to 20 %) place, belief break, why it is rare, a departure marker. Act 2 (60 to 70 %) the first goal
stated, a quick win with a catch, a near miss then relief, a cliffhanger at the time jump, a progress stamp, a planned
set piece as a test, a loss plus a social complication, warm relief carrying the theme, a threat planted then
reframed, the build-up paid. Act 3 (15 to 20 %) the real high and the theme line, the motif payoff, the bookend, the
arrival with the title's number, a completion image, a short reflective close, the CTA. Script the beat plan and key
lines before the shoot, keep an event log during it, and write the voice-over in the edit (V4 T8).

**Tutorial, 6 to 15 min** (R1 §6, V5 T4): the finished result on screen, who it is for, the time needed; the trap
most people fall into; steps (goal, action, check), one chapter each, with the count visible; a before-and-after in
every step; the mistakes section; a second example as a test; the result plus the next tutorial. Each point as a CVF
block (V4 T6): **C**ontext in the simplest words, a **V**isual cue (example, demo, graphic), **F**raming (why it
matters to the whole); the next point's first words link back.

**Commentary, 8 to 20 min** (R1 §6): the strongest piece of evidence first; your claim in one sentence; 60 s of
context; the evidence ladder with receipts; the best version of the other side; the verdict and what to watch next.
Label opinion; separate fact from interpretation (V1 SC-08).

**List video, 10 to 15 min** (R1 §6, V3 ST3, V6 T-V6a): the hook with the ranking logic and stakes; items in rising
order with number one held as the open loop; each item: a name, a claim, proof, a twist, a micro-payoff, and a bridge;
vary item length and format; plant the last item inside the one before it; number one pays the title. A count in the
title is delivered with the same count.

**Running story inside a teaching video** (V6 T-V6c): split one true story at cliffhanger points so each teaching
section is one chapter; debrief each ("notice what I just did") and teach the move; resolve the story before the final
lesson.

## 5. Talks and audio

**Talk, 10 to 20 min** (R3 T4): open a personal story at its peak (loop A); set what is against what could be;
alternate them with evidence and a second story (loop B); deliver the core idea and one moment people will repeat;
close B, then A; end on the new normal and the ask. Nested loops close in reverse order.

For audio-only work keep one body cue in the narration (there is no picture to carry it), and signpost more often.

## 6. The A/V script and the roadmap

The two-column script is the standard for documentaries, explainers and ads (R1 §5.3): narration, dialogue and sound
on the left; the matching picture on the right. Write both at once. Right-column rules: concrete and shootable
("close-up: the receipt, total circled", never "b-roll of shopping"); a visual idea every 1 to 3 sentences; every
number gets an on-screen form; every abstract idea gets a metaphor or a demo. `script.py render` writes it as
`script.md`, with the loop ledger and the claim ids.

On-camera creators talk from a **roadmap**, not a read-out script: the hook line, the structure, the hard facts with
sources, one or two examples, the close line, rehearsed aloud several times (V2, the YASH video). `render` writes
`roadmap.md` next to the script.

**Chapters** (YouTube): the first timestamp 00:00, at least 3 in ascending order, each at least 10 s; write chapter
titles as mini-promises ("Why the fix made it worse"), never labels ("Part 3"). **End screens** only in the last 5 to
20 s (R1 §1, §4).

## 7. The script file (`nexa.script/1`)

```json
{"schema": "nexa.script/1",
 "meta": {"title": "", "format": "explainer", "lang": "bn", "target_seconds": 600, "wpm": null,
          "mode": "nonfiction", "captions": true, "brand": "", "paid": false},
 "promise": {"promise": "", "titles": [], "thumbnails": [], "first_line": "", "first_visual": "", "tension": "",
             "payoff_at": "", "hook_variants": [{"type": "", "visual": "", "spoken": "", "caption": ""}]},
 "loops": {"Q1": "the question", "Q2": {"question": "...", "cross_video": true}},
 "story": {"mode": "nonfiction", "key_moment": "b7", "key_line": "", "reconstructed": []},
 "beats": [{"id": "b1", "section": "cold-open", "roles": ["hook"], "narration": "", "visual": "",
            "visual_type": "", "on_screen": "", "sound": "", "emotion": "", "seconds": null, "pause_s": 0,
            "loops_open": ["Q1"], "loops_close": [], "claims": ["c3", "brief"],
            "tension": {"q": 0, "s": 0, "u": 0, "p": 0}}],
 "cta": {"text": "", "beat": ""}, "sources": "research/pack.json"}
```

- `roles`: hook, identity, setup, conflict, choice, pp1, pp2, change, value, marker, stakes_loss, stakes_gain,
  surprise, bridge, sponsor, cta, key_moment.
- `claims`: claim ids from `research/pack.json`, or `brief` for a fact the client gave (`facts_given`).
- `seconds`: a planned duration (shorts and ads); the lint checks words per second against it.
- `pause_s`: a held pause after the beat; `[beat]` inside the narration marks a pause after the key line. Both are
  stripped from `narration.txt` so a voice never reads them.
- `visual_type`: a-roll, talking head, b-roll, graphic, map, archive, screen, demo; the lint flags a talking head over
  20 s in long-form.
