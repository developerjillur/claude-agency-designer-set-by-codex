# Hooks, packaging and the first 30 seconds

The package (title, thumbnail, first line, first frame) makes one promise; the opening confirms it and the body pays
it, bigger than promised. Evidence and sources: `research/R1-youtube-longform.md` §1 and §3, `R2-shortform-and-ads.md`
§2, `V4-story-part3.md` (formulas F1 to F3, T1, T10), `V6-kallaway-vishen.md` (V6-R4, V6-R8, T-V6h),
`V2-script-and-story-part1.md` §C, `V5-humm-storytelling.md` (T1).

## 1. The promise contract (fill it before the script)

| Field | What goes in |
|---|---|
| Viewer | who, where they meet it (feed, search, home page), sound on or off |
| Title | 3 options; specific, honest, complements the thumbnail instead of repeating it |
| Thumbnail concept | 3 options; one idea readable in a glance |
| Promise | one sentence the viewer would repeat |
| First spoken line | the hook line itself |
| First visual | what is on screen in frame 1 (an action, not a logo) |
| Tension | the misconception, contradiction or open question it breaks |
| Payoff at | where the main promise is paid (a time or a beat id) |
| Bigger than the package | the line or visual that already gives more than the title by 0:30 (V4 F1) |

Why: YouTube's own title and thumbnail test picks the winner by watch time share, not clicks, and its Intro metric is
the share still watching at 0:30 (R1 §1). A package the video does not pay loses on both. The MrBeast production
guide (leaked 2024) makes the first minute match the thumbnail and then escalate; Paddy Galloway's line is that the
best intro does not feel like an intro (R1 §2).

Store it in `script.json` under `promise` (`promise`, `titles`, `thumbnails`, `first_line`, `first_visual`,
`tension`, `payoff_at`).

## 2. Three layers, one idea

A hook is a first frame, a first spoken line and an overlay, all saying the same thing (R2 §2).

- **Short and ad:** something happens in frame 1; speech starts by about 0.5 s; the promise is clear by 3 s; the
  overlay is 7 words or fewer and restates the promise for sound-off viewers; the product or brand cue shows by 3 to
  5 s as part of the action, never as a logo slate (R2 §1.4, §8).
- **Long-form:** the topic is confirmed within about 25 words; a turn (but, except, yet) or a hard stake lands within
  20 s; no greeting, logo, subscribe ask or sponsor in the first 30 s (R1 §9.1).

**The 30-second intro (long-form), about 75 to 85 words at 150 to 170 wpm (R1 §3):**

| Time | Beat | Job |
|---|---|---|
| 0 to 5 s | Confirm | Show or say exactly what the title and thumbnail promised |
| 5 to 12 s | Stakes | Why it matters, what is at risk, or what is strange |
| 12 to 20 s | Turn | A "but" that breaks the obvious answer or names the misconception |
| 20 to 30 s | Plan or proof | The roadmap, or the first piece of evidence, plus one line of credibility |

Explainers skip the preview and go straight into content; tutorials show a roadmap and tick it off on screen (V1
SC-03). Stories may open on the place for up to 15 s with ambient sound, then the belief-break line (V4 T2).

## 3. Formulas

Every slot must be filled with something true from the brief or the research pack. A formula is a draft shape; the
lint and the judges decide.

| Formula | Shape | Source |
|---|---|---|
| Break + stakes + gap (+ clock) | a true correction or an unexpected result; what it costs or gives this viewer; the answer held back; when it arrives | V4 F2 |
| Belief break | "If you think [common belief], [the verified correction]" + why it matters now | V4 F3 |
| Context lean, contrast, snapback | make the topic clear, one contrast word, a turn against expectation that points at the payoff | Kallaway (R1 §2.8) |
| Collision line | two ideas that clash in 8 to 10 words, literally true to the body | V6 T-V6h |
| Pain, gap, relief | the pain in the viewer's words with a number; "but actually" a small number of steps is enough; here they are | V2 T2 |
| Anchor opener (stories) | [time], I'm [place] [action], when [disruption] | V5 T1 |
| In medias res | start at the most charged moment and backfill | R3 §3 |
| Result first | show the finished result in frame 1, then how | R2 §2 |

**Hook types for shorts and ads (R2 §2; the examples are ours):**

| Type | Strong | Weak |
|---|---|---|
| Result first | "Five lunches, 40 minutes, one Sunday." (pan across the packed fridge) | "Meal prep can be hard, but it doesn't have to be!" |
| Value promise | "Three settings that get your phone to bedtime on one charge." | "Some useful phone tips." |
| Statement of intent | "I'm fixing this wobbly table with one thing from the kitchen drawer." | "In this video I'll talk about furniture." |
| Question | "Guess what this whole outfit cost." | "Have you ever thought about fashion?" |
| Proof shot | the phone dropped in a fish tank at frame 1, text: Waterproof? | a slow logo reveal |
| Mistake or warning | "Stop rinsing rice like this." | "Rice is eaten by billions of people." |
| In medias res | "11 pm, my landlord texts: is that your car?" | "Let me tell you a story." |
| Comparison | split screen, same water, one powder clumps | "Unlike other brands, we're better." |
| Recognition | text: POV: black couch, golden retriever | "Everyone deals with pet hair." |
| Objection first | "Yes, it's $60 for socks. Here's why I bought four pairs." | "Premium socks for everyone." |
| Offer | "Two for one ends Sunday. Here's what's in the box." | "Amazing deals now!" |

**Hook menu from the Hindi reference videos (V2 §C):** the viewer's own questions; demand proof ("X people asked",
only when true); a result despite constraints; before and after with the one lever; a paradox fact (huge today,
nearly gone before); a sensory moment then a flash-forward; the viewer's feed contradicted; a journey graph with the
answer hidden.

## 4. Weak openers and their stronger pattern

| Weak | Why | Stronger |
|---|---|---|
| A greeting, then "today I'll teach you X" | no break, no gap | correct a belief the viewer holds about X |
| "Here are N tips" | a list with no gap | hold back the most surprising item and say when it comes |
| "You must learn X" | no proof, no stake | a sourced number about people like the viewer, or their own loss |
| "Have you ever wondered why prices keep rising?" | a question anyone could ask | "Ten years ago this basket cost 40 dollars. Today it's 62. The shop's profit barely moved. So who took the 22?" (R1 §3, illustrative) |
| "Hey guys, welcome back! Today: pivot tables." | throat-clearing | "40,000 rows, a 3 pm meeting, and your boss wants totals by region. It takes three clicks." |
| "There's been a lot of drama lately." | vague | "Monday they promised every customer a refund. Thursday the post was gone." |
| "This bakery turns people away." | an interpretation of the facts the viewer cannot check, and a claim the brief never made | the scene the facts give, with their own times: "The line starts at 7 a.m. By 9, it's sold out." (2026-09-26 benchmark: judges from two model families preferred the scene, and one called the interpretation unsupported) |

The lint flags greetings (error), announcing openers (warning), hedges in the hook ("might", "maybe", "হয়তো"; V6-L1),
first sentences over 12 words in shorts or 20 in long-form (V2 E2), and a hook line with no number, time, contrast or
question (a note). "You might think..." voicing the viewer's belief before breaking it is thought narration, not a
hedge.

## 5. Rules that keep hooks honest

1. The hook's key claim (who did what, how much) reappears accurately in the body (V6-R4). A hook the body
   contradicts is a hard fail.
2. Pay the hook: a short pays it within 5 to 8 s and keeps one idea (R2 §8); long-form pays small debts early and the
   main one late (R1 §4).
3. Never call out a sensitive trait of the viewer ("Struggling with your weight?"): Meta's personal-attribute rules
   reject it (R2 §6). Describe the situation instead ("What I eat on a 12-hour shift so I'm not starving at 4 pm").
4. At most one negative hook per piece; every warning names a real, common, checkable mistake; no fear hooks on
   health, money or religion without a sourced risk (V6-R8).
5. No fake loops ("stay till the end", "bonus at the end") unless the payoff is real and named (V3 SL15).
6. No improvement numbers you cannot show ("improve by 176%", "top 1%"): V5 HL13 found the reference videos never
   measured theirs.
7. No hedging where the evidence is firm, and one plain caveat where it is not (V6-R6).
8. In South Asian markets, "your teachers were wrong" style breaks can read as disrespect; prefer "what we were taught
   about X is incomplete", and never break a religious belief (V4 SA 7).

## 6. Hook packs (shorts and ads)

An ad ships 5 hooks of at least 4 types and 3 different first frames on one body, with 2 bodies and 2 CTAs, each
block ending on a clean cut so any hook joins any body (R2 §5, §8). Variants differ in concept or hook type, never
just wording; Meta's Andromeda retrieval rewards distinct assets and weakens small iterations (R2 §1.2, §5).

In `script.json`: `promise.hook_variants` = `[{"type", "visual", "spoken", "caption"}]`. The lint checks the count,
the types and the first frames.

When a hook fails, explore before polishing: write 5 hooks including unlikely ones and test them all in the panel's
feed-stop test (T1) instead of asking for one "improved" hook (R10 §5.5).

**The feed-stop test:** put the draft hooks among 6 to 8 real hooks from the niche with known results (the research
pack's competitor list), in `hooks.json` as `[{"id": "H1", "text": "...", "draft": true}, {"id": "R1", "text": "...",
"result": "1.2M views"}]`, then `script.py panel run FILE --panel panel.json --hooks hooks.json`. The review reports a
hook index: the draft's stop rate against the median of the real hooks. It is synthetic and directional.

## 7. Titles and thumbnails

- Plan them before the script; complement, never duplicate; pass the glance test (Galloway, R1 §2.2).
- Concrete beats abstract: Veritasium's retitle of a Magnus-effect video around one concrete scene added about
  10 million views, and dropping the word "surprising" lifted a title test about 10% (R1 §2.4).
- More extreme framing wins clicks in MrBeast's notes, and a thumbnail detail the video does not match makes viewers
  feel lied to (R1 §2.1). Honesty is part of packaging (V6-R14).
- YouTube's Test & Compare runs up to 3 titles or thumbnails for up to 2 weeks and picks by watch time share (R1 §1).

## 8. Bangla hook lines (drafts)

Slot patterns from V3 ST4, to be filled with true claims and passed through natural-text before use:

| Device | Pattern |
|---|---|
| But pivot | ভেবেছিলাম [X] কাজে দেবে, কিন্তু উল্টো [ক্ষতি] হয়ে গেল |
| Contrarian claim | [দামি জিনিস] আসলে কোনো কাজেরই না, [N]টা কারণ বলি |
| X-Y rule | আপনি যদি [X] হন, তাহলে [Y] করবেন না |
| X-Y rule, form 2 | আপনি [X] করছেন, তাই [Y] হচ্ছে না |
| Markers | এটাই ছিল আপনার প্রথম ভুল / দ্বিতীয়টা কেউ বলে না / আসল চমক এখনো বাকি |
| Anchor opener | গত বৃহস্পতিবার, ব্যাংকের লাইনে টোকেন হাতে দাঁড়িয়ে আছি, ঠিক তখনই ফোনে মেসেজ এল |

A salam or greeting, when the creator always uses one, goes right after the first hook line and lasts a second
(V4 SA 15); it never opens the video.
