# Story: the engine, the skeleton, scenes and endings

A story is a caused change: a before state, one event that flips it, an after state, chained by "but" and
"therefore". Everything here serves that. Evidence: `research/R3-storytelling.md` (the science and the structures),
`V2-script-and-story-part1.md` (the LEVELS ladder), `V3-story-part2.md` (plot points and attention tools),
`V4-story-part3.md` (a viral vlog taken apart), `V5-humm-storytelling.md` (scenes), `V6-kallaway-vishen.md`
(sentence-level devices and the HSTSS story shape).

## 1. Find the story before drafting

Answer five questions (R3 §4.4). No answer to 1 or 3 means you have a list of facts: go find a person or a wrong
belief in the research, never invent one.

1. **Character:** who or what wants something? A person is best; a group, a place, an object or the researcher can
   stand in.
2. **Question:** the single question the viewer wants answered by the end.
3. **Conflict:** what is in the way: nature, a rival, a wrong belief, time, money.
4. **Turning point:** where expectation breaks (McKee's gap between the expected and the actual result).
5. **Reveal:** what the viewer learns at the end that changes how they see the start.

Then write the **change line** (from → to, with a direction) and name **PP1**, the one event that flips the before
state (V3 SR1). If you cannot, list the events start to end with no gaps and find the flip.

Worked example (illustrative, R3 §4.4): a bakery that sells out by 9 a.m. Character: the owner. Question: why not
bake more? Conflict: one oven. Turning point: doubling the batch made the bread worse. Reveal: the small batch is
the product. The and-then version ("she opened, then it got busy, then she baked more") has no reason to keep
listening.

## 2. The engine: but and therefore

- Join beats with **but** (a complication) or **therefore/so** (a consequence), never "and then" (Parker and Stone,
  R1 §2.11; R3 §3). The lint flags more than one and-then in three marked transitions and two in a row.
- Split main claims into expectation, reversal, consequence (V6-R10). Aim for one to four contrast turns per spoken
  minute; at most one "not X, it's Y" frame per script.
- Short-form story is a chain of expectation breaks: each "but" opens a gap, each "so" cashes it (Kallaway, R3 §4.1).

## 3. The skeleton and its two anchors

**Hook, Identity, Conflict, Choice, Change, Value** (V3 SR4): identity and choice may be reordered or skipped;
conflict and change may not. Tag beats with `roles` in `script.json` and the lint checks the skeleton.

| Anchor | Where | Rule |
|---|---|---|
| PP1 | 10 to 25 % of long-form; by about a third of a short | Never beat 1: the viewer must know what it changes (V3 §3.1) |
| Setup before PP1 | 10 % of long-form, 5 s in a short | Only who, what normal looks like, what is missing (V3 SR3, ST2) |
| Midpoint turn | 40 to 55 % | Reframes the question; the counter to the mid-video sag (R1 §4) |
| PP2 | 75 to 85 % (anything over 3 minutes) | Failure, discovery, a person, a reveal (V3 SR2) |
| Main payoff | late, then leave | At most 30 s or 5 % of runtime after it, whichever is shorter (V4-L22) |

Two script modes (V4): **Mode A, explainer or teaching** (the unit is the point; open on the topic; engine =
questions, promises, weak-to-strong contrasts; the best point promised early, delivered in rising order). **Mode B,
story, vlog or documentary** (the unit is the scene; open on the place, then a belief break; engine = goals,
obstacles, threats, relief; the biggest payoff in the last 15 %).

## 4. Stakes

- Stakes = root + risk + urgency, and one big question stated early (V2 LEVELS level 4).
- A concrete, true loss (a number, an object, a place) plus a named feeling; for a narrator the audience does not
  know, one proof line (10 s or less) comes before the low point (V6-R2, V6-R3).
- A stakes pair in the first 20 %: what can be lost (`stakes_loss`) and what the viewer gains (`stakes_gain`)
  (V3 SL9). Concrete stakes before the midpoint (R3 R5).
- Honest stakes only: no invented stakes in factual or client work (V3 SR9); "this changes everything" with nothing
  specific at risk is fake stakes (R3 §7).

## 5. Loops, bridges and promises

- Keep a **loop ledger** (`loops` + `loops_open`/`loops_close` on beats). Every loop closes, the main one last; a
  loop may run into the next video only when declared (`{"question": "...", "cross_video": true}`) (R3 R4, V3 SR6).
- A new question, tease or turn keeps pulling: V3's creators claim one every 15 to 30 s; the lint warns at a 60 s gap
  in long-form and 12 s in a short. The references sagged exactly where they went 112 to 272 s without one (V2 E5).
- Close small loops fast while the title's question runs to the end (R1 §4). Bigger teases need bigger payoffs
  (V4 F6); a tease repeated twice must pay big.
- **Bridge line** at every section end (V6 T-V6d): acknowledge what landed + a contrast word + tease what is
  different about the next part. "That fixes the opening, but it does nothing for the middle, which is where most
  viewers leave." The teased part must pay.
- **Chapter ends** before a time jump, a chapter break or an ad hold an unresolved threat or a pending test (V4 F5,
  T9): "The pizza is due at Siliguri at 2:30. I haven't paid for it."
- Time-boxed promises ("in two minutes", "the third point") are kept on time (V4-L07).
- A sponsor or plug sits after a loop opens and before it pays off, never before the first payoff (V3 SR15, V2 E15).

## 6. The tension map (R3 §6.1)

Score every beat 0 to 3 on four rows and store them as `tension: {"q", "s", "u", "p"}`:

- **q** open question: does the viewer want to know something right now?
- **s** stakes: do they know what someone they care about could lose?
- **u** uncertainty: could the next beat plausibly go more than one way?
- **p** payoff: did this beat change something (a reveal, a reversal, a decision, a fact that matters)?

T = q + s + u. The lint reads the shape: a **flat zone** (T under 4 for more than two beats in a short or about 45 s
in long-form: cut, or add a but), an **orphan payoff** (p of 2 or more with no T of 5 before it: set it up), **unpaid
tension** (T of 6 or more for long with no payoff: pay a smaller loop), a **section end** with q under 2 (end on a
re-hook), and a **peak** that belongs just before the biggest payoff, around 75 to 90 %. Surprises: at least one in a
short, one every 2 to 3 minutes in long-form, each fair (set up earlier) (R3 §6.2).

After publishing, lay the retention graph over the map: a dip at a high-T beat usually means an unclear question or a
broken promise.

## 7. Scenes: zoom into the moment (V5)

PAST is scene texture, used after the structure is set: **Place, Action, Speech, Thoughts**.

- **Find the moment:** zoom into the turn (the line or act that changes things); summarize the rest in short lines.
  One zoomed scene per short story, one or two per long story; never zoom every sentence (V5 H1, HL9).
- **Anchor opener:** a time marker, one place, an action verb and the disruption in the first sentence or two; no
  weather, scenery or job history first; context comes after the first action, in one or two lines (V5 H2, H3).
- **The rewrite ladder** for any flat line: a summary (worst) → a named emotion → the exact words, thought or body cue
  of that second (best). One rung per sentence (V5 T3).
- **Show at the peak, label in the reflection:** no "I was so nervous" inside the key moment (V5 H5; lint HL4).
- **Direct speech:** "she told me that she was upset" becomes her exact words (V5 HL5); quoted lines are short (15
  words or fewer), colloquial and in character, with no report words ("regarding", "opportunity") inside quotes (HL7).
- **Stage the key line:** the sentence before it sets the expectation (usually a thought); the key line stands alone;
  a pause follows (`[beat]` in the narration or `pause_s` of 0.7 to 1.2 on its beat); then the reaction (V5 H7).
  Name it in `story.key_line`; mark the scene beat in `story.key_moment`.
- **Let the picture carry what it can:** in video, place and body cues move to the visual column; narration keeps
  speech and thought (V5 H8).
- **Reaction then reason:** the visible feeling comes one beat before its explanation (V4 F10).
- **One scene the viewer can see** in long-form, with three or more concrete details; slow the delivery there
  (V6-R12).

The six-slot zoom (V5 T2): anchor (place and action) → expectation (a thought) → trigger (the exact words or event,
the key line) → `[beat]` → reaction (a raw thought or one body cue) → consequence or punchline, then optionally one
line of reflection.

## 8. Emotion: a wave, not a line

- Emotion rises and falls; a flat tone and a constant peak both bore (V2 ERCRT). At least four distinct feelings in a
  long story; troughs set up peaks (V4 J06).
- Tag beats with `emotion` (a free word; the navarasa set in V4 T5 gives a shared vocabulary: love, laughter, sorrow,
  anger, courage, fear, disgust, wonder, peace). The lint flags three identical tags in a row.
- Place the point that must be remembered inside or right after the biggest emotional or surprise peak (R3 R7).
- Keep statistics out of the emotional peak; bring them in afterwards as proof (R3 §2.7).

## 9. Devices (use when they serve the content)

| Device | Use | Source |
|---|---|---|
| Foreshadowing | plant early what pays off later; cut anything planted and never used | R3 §5 |
| Callback and bookend | return to the opening image or line with a new meaning; opening state = closing state, changed | R3 §5, V4 F9 |
| Motif | introduce, use privately, pay off as shared or transformed | V4 F8 |
| Progress markers | ordinal signposts that each promise the next reward, mirrored on screen; the last framed as the biggest | V3 SR8 |
| Escalation | only in formats with attempts: each attempt bigger or riskier, announced before it starts | V3 SR10, ST7 |
| Thought narration | 2 to 4 times in long-form, once in a short: the viewer's likely objection in their words, answered at once; take it from real comments | V6-R7 |
| Term brand | 1 to 3 per long video: defined within two sentences, reused twice, never presented as a psychological principle | V6-R9 |
| Demonstrate, then reveal | teaching videos use the technique on the viewer, then name it | V6-R13 |
| Perspective | replace a label with a habitual detail; set a big number against something the viewer knows | V3 SR12 |
| Rule of three | two items set a pattern, the third breaks it; a reflexive triplet in every sentence is a machine tell | R3 §5, §7 |
| Dialogue and sound | quote a real line; pair key images with a sound cue | R3 §5, V2 B17 |

## 10. Endings

- End on the payoff and shown change; a callback beats a summary; no stated moral (R3 R10).
- One earned **shatter line** is allowed in teaching and keynote formats: 25 words or fewer, reversing a belief named
  earlier, true, placed before the evidence; ads and fiction use a callback instead (V6-R11).
- No vague payoffs ("and the rest is history", "বাকিটা তো জানোই"): they fail the lint (V2 E13).
- No ending signals before the end ("in conclusion", "before we end") (R1 §4).
- One CTA tied to the next video in the last 5 to 20 s (the end-screen window) (R1 §4).

## 11. Truth modes (set `story.mode` or `meta.mode`)

| Mode | Quotes | Reconstruction | Dates and places |
|---|---|---|---|
| `nonfiction` | only from the research ledger or approved words, with a claim id on the beat | label composites and reconstructions on screen | only from facts given or the pack |
| `personal` | the teller's own anecdote; reconstructed lines allowed, listed in `story.reconstructed`, gist approved by the teller | allowed, marked | the teller's own |
| `testimonial`, `case_study` | the customer's real, approved words only | none | the client's facts |
| `ad` | real, approved words; no invented reviews or results | none | the client's facts |
| `fiction` | anything, labelled as fiction where it could be mistaken for real | free | free |

Never add specifics to make a story feel true (V5 H10), never claim "nothing staged" over staged scenes (V4-L23), and
never invent people, quotes, events, customers or numbers in factual work (R3 R12).

## 12. How stories fail, and the AI tells to hunt

- **Story as decoration:** an anecdote you could delete without changing the argument. The turning point must be the
  evidence for the claim or the reason for the ask (R3 §7).
- **Melodrama:** emotion bigger than its cause; adjectives and music doing the work.
- **AI tells** (R3 §7): a predictable arc (problem, effort, quick success, lesson); generic characters; the moral at
  the end; stock phrases ("little did they know", "a testament to"); exposition explaining what the scene just
  showed; emotions named instead of shown; reflexive triplets and "not X, it's Y"; every thread tied with a bow.
- **Pop science** never enters a script: "22 times more memorable", goldfish attention, oxytocin, "dopamine hits",
  "your brain is wired", "subconscious", "cheat code" (R3 §2.9, V6-R16). Keep the behavioural lesson: tension plus a
  person to care about moves people.
