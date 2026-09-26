# Writing for the ear: rhythm, numbers, pace and delivery

A script is heard once, at speed, with no rewind. Evidence: `research/R1-youtube-longform.md` §5.2,
`V2-script-and-story-part1.md` (the YASH delivery lesson, the lint values), `V5-humm-storytelling.md` (key-line
staging), `V6-kallaway-vishen.md` (calibrated commitment, thought narration), and natural-text for the words
themselves.

## 1. Ten rules (R1 §5.2)

1. One idea per sentence; the subject and verb in the first five words.
2. Average 10 to 16 words with real variety: short punches, a few longer runs, nothing a narrator cannot say in one
   breath (about 25 words; 30 is the hard ceiling, V2 E9). In shorts and ads, 18 words at most per spoken sentence
   and a hook line of 12 or fewer (R2 §8, V2 E2).
3. Numbers the way people say them ("about one in five", "nearly double"), one number per sentence, the comparison
   right next to it.
4. Nothing the ear cannot rewind: no brackets, no "the former" or "respectively", no "as shown above".
5. Repeat the key noun instead of a distant pronoun.
6. Put the surprising word last in the sentence, where the voice lands.
7. Contractions and spoken connectors ("so", "but"), never "furthermore" or "moreover".
8. Signpost: "Three reasons. First..." (Blackman: a few seconds of signposting buys attention).
9. Show it, then name it: discovery before the label.
10. Read it aloud at the target speed; wherever the narrator stumbles or runs out of breath, rewrite.

## 2. Rhythm

- Vary sentence length. Across the 14 reference transcripts, the spread of sentence length (sd divided by the mean)
  ran 0.54 to 1.01, and no stretch of 12 sentences fell under 0.25. The lint calls anything under 0.25 over eight
  sentences a monotone rhythm, a machine tell.
- At least 15 % of sentences at 8 words or fewer (R1 §9.2).
- Slow down at the key line: an expectation just before it, the line alone, a pause after it (`[beat]`, 0.7 to 1.2
  s), then the reaction (V5 H7). Vishen drops to about 151 wpm at his key line (V6).
- One tense per story in English (historical present suits spoken anecdotes); Bangla anecdotes move between tenses
  freely, so the rule stays off for Bangla (V5 H9, E).

## 3. Numbers, money and units

- Lakh and crore in Hindi and Bangla narration; taka (৳) for Bangladesh, rupees for India; Bangla numerals in Bangla
  on-screen text (V4 SA 8). One reference video said "47 million" and then "4.5 crore" for the same figure: the
  second is the one that lands (V2 G2).
- Convert dollar figures and set them against a local scale (a salary, a rickshaw fare, a bag of rice) (V3 SR12).
- Recompute every conversion: 1 million = 10 lakh, 1 billion = 100 crore (V1).
- Every number carries its unit, date, place and definition in the research pack (V1 RC-08); the script says it the
  way a person would.

## 4. Commit, talk to the viewer, voice their doubts

- **Calibrated commitment** (V6-R6): no hedges in the hook, an instruction or the CTA; firm where the claim is
  sourced, one plain caveat where it is not, cut where it is unsourced. Instructions use "when", not "if" ("when you
  post", not "if you try posting"); "if" is for audience qualifiers ("if you run a shop").
- **Direct address:** the reference creators say "you" 3.5 to 8 times a minute (V2 E10). Talk to one viewer.
- **Thought narration** (V6-R7): voice the viewer's likely objection in their own words, then answer it at once:
  "You're probably thinking this only works for big channels. It worked for a channel with 300 subscribers." Take the
  objection from real comments and searches (the research pack's voice bank), never from a guess. Two to four times
  in long-form, once in a short.
- **One address form** in Bangla: আপনি by default for broad and client work, তুমি only for a young niche that talks
  that way, তুই only inside character dialogue; never mix them in the narration (V4-L27, the lint checks it).

## 5. Delivery: two outputs, two tests

- **Voice-over or TTS:** `narration.txt` from `script.py render`, with stage marks removed. Voice it with the
  nexa-speech skill; time the real read, set `meta.wpm` to it and re-run `timing`.
- **On camera:** a script read word for word sounds robotic; a creator who tells it from a roadmap, rehearsed aloud
  several times, sounds human (V2, the YASH lesson). `render` writes `roadmap.md`: the hook line, the structure, the
  facts to get exactly right, the close line.
- **Read-aloud test:** read at the target speed, or through TTS, with two or three people if you can; mark stumbles,
  drift and lines nobody would say (R3 §6.2).
- **Retell and first-time-learner tests** (V2 F): `script.py understand FILE --brief brief.json` has a fresh model
  read the plain narration once, retell it to a friend in five sentences and explain the main idea as a first-time
  learner; a second model maps the retelling onto the numbered lines. Beats that drop out or change order point at
  an unclear structure; an explanation that misses the mechanism points at a missing comparison.
- **The dinner test:** would you say it this way to a friend at dinner? If not, rewrite (R3 §6.2).

## 6. The words themselves

natural-text is the backbone for every word: casual, specific, in the audience's own words, never bookish or
translated. `script.py lint --voice` runs its lint (codex-design copylint, role voiceover) on the narration and adds
its findings to the script's. For Bangla it applies the Bangladesh rules (চলিত, everyday words, no সাধু forms, no
Kolkata words in a Bangladeshi script).
