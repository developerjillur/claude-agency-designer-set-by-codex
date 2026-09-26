# V5: Philipp Humm on storytelling (two English videos)

Two videos by Philipp Humm that the owner picked as teaching material on storytelling. Written 2026-09-26 as input for nexa-script (rules and templates), its lint and its judge. It also settles the "[content unverified]" note on Humm in R3 section 4.2: his content is now checked against the transcripts and the frames.

Short tags used in this file:

- **HUMM9**: "Give me 9min, and I'll improve your storytelling skills by 176%", Philipp Humm, 8:58, id `hNuAv-42jzY`. A talking head at home with dense motion graphics. Five techniques.
- **HUMM18**: "Give me 18min & I'll improve your storytelling skills by 183%", Philipp Humm, 18:34, id `YtkrIaONxu0`. A filmed workshop with a live audience, a whiteboard and volunteers. The PAST framework: Place, Action, Speech, Thoughts.

## Sources and how they were checked

- Both `.txt` transcripts were read in full. The `.json` logs (sounds, music, uncertain spots) were used for timing and delivery notes.
- About 150 frames were sampled from the cached downloads (HUMM9 every 10 s, HUMM18 every 20 s, both hooks every 3 s, two timing checks and one whiteboard crop) to read technique cards, name cards, overlays and end screens.
- **HUMM9 timing fault.** One transcript line runs from [0:58] to [1:40]. That is the transcription model's clock jumping, not a silent gap (the V2 file found the same fault in four other transcripts of this batch, this one included). Lines shown between [1:40] and [5:40] that come from the first five-minute chunk are about 40 s late: the LOCATION card is on screen at about [1:32], while the `.txt` puts the line that introduces it at [2:12]. Because those late lines spill past [5:00], the `.txt` from [5:00] to [5:40] interleaves two streams: the end of the thoughts section and the start of the emotions section (late) mixed with the rest of the emotions section (on time). The order used below was rebuilt from content and frames. HUMM9 times in this file are real video times, and `~` marks a corrected one. From [5:00] on, the `.txt` times are right.
- **HUMM18 timing is right.** Checked against the P and A cards (about [2:48]), the place-and-date icons ([6:20]), the S card ([9:49]), the T card ([13:28]) and the start of the last clip ([16:34]).
- **HUMM18 speaker labels reset every five minutes.** After [15:00] the presenter is S2, not S1, and the line at [15:00] labelled S1 still belongs to the volunteer.
- **Bleep.** HUMM18 has a censor bleep at about [16:14] inside the raw-thought example; the `.txt` renders the line without the bleeped word.
- **Names.** HUMM9 names its two storytellers aloud: John Krasinski, and Sarah Willingham, introduced as a British entrepreneur, investor and CEO of Nightcap (her clip carries a BBC logo). HUMM18 never names its storytellers aloud; on-screen cards name them as Anne Hathaway and Leonardo DiCaprio, and both clips carry the ellentube logo. The HUMM18 hook also shows cut-out photos of well-known speakers, not identified here.
- HUMM18's volunteers are private people telling personal stories. They are described, not named.
- Quotes are kept to one. Concept names (PAST, zoom into the moment, helicopter view) are used as labels; everything else, his examples and the clips included, is paraphrased.
- Counts (words, questions, sentence length) come from machine transcripts and are approximate.

## Top findings

1. **One principle, several tools.** Both videos teach a single idea: stop summarizing from the helicopter and zoom into one moment of the story. Every technique is a way of doing that zoom.
2. **The tools.** HUMM9 has five: location, actions, thoughts, emotions shown on the body, and dialogue. HUMM18 compresses them into PAST (place, action, speech, thoughts); emotion now travels through thoughts, and body language drops out.
3. **A ready-made story opener.** Almost every example of his own has the same shape: a time marker, "I'm" in a place doing something, and (in HUMM18) a "when" that brings the disruption. It becomes a template (T1) and a lint check (HL1).
4. **A three-rung ladder for any flat line** (HUMM18 [12:42]): a summary is worst, a named emotion is better, the exact words or thoughts of that second are best. It works as a revision pass and as a judge scale.
5. **Raw, not polished.** Quoted lines and thoughts must sound like a person in that second, not like a report. Formal wording inside quotes is the mistake he names most often, in both videos. It is countable.
6. **Stage the key line** (HUMM18 [11:14] to [12:23]): find the one line the story turns on, build anticipation right before it with a thought, and pause after it so the contrast lands.
7. **Two tips that clash with our truth rules.** If you can't remember the words, use words that could have been said; and naming the date and place makes listeners accept a story as true. Both are fine for a teller's own anecdote and wrong for nonfiction, testimonials and client case stories. Our skill needs declared story modes.
8. **The headline numbers are unsupported.** Neither 176% nor 183% is said, shown or measured anywhere in either video. The 78-speaker analysis, the top-1% promise and the better-than-99% promise come with no method.
9. **Scope limit.** PAST renders a scene. It does not choose the story, the stakes, the turn or the ending. Every demo he picks has a strong reversal, which does much of the work he credits to zooming in. Pair PAST with R3's structure tools.
10. **The videos are built the way they teach**: a demo story first, then the principle with a picture (helicopter against trenches), then numbered steps with black-and-white "before" and color "after" rewrites, then a second story as a spot-the-elements test.

---

## Video 1: HUMM9, "Give me 9min, and I'll improve your storytelling skills by 176%"

### 1. What it teaches, as a method

1. **The principle: zoom into the moment [0:58 to ~1:27].** After the Krasinski clip he asks whether the viewer noticed what the actor did, then performs the same events himself as a flat recap (shot in black and white): the actor did not summarize, he zoomed in. Good stories do not stay at helicopter level; they take the listener into the trenches and into the physical moment. He says this is easy and that five techniques work in every story.
2. **Location: say where you are [~1:32 to ~2:29].**
   - Rule: open by stating where you physically are.
   - His examples: two weeks ago on the couch in his living room, taking a deep breath; a named month and year, standing at the door of a conference room, about to walk in.
   - Why: as soon as a listener hears conference room or living room, they picture their own version of it.
   - Mistake: listing the room's contents (a big table, a TV, a wooden floor). Beginners over-describe; the listener supplies the details.
3. **Actions: what are you doing in that moment [~2:29 to ~3:16].**
   - Rule: skip the context that doesn't matter and state the verbs (walking, biking, shouting, reading, waiting).
   - His examples: in his office, opening the laptop and starting to read a message from his manager; at the airport, waiting in the security line.
   - Why: verbs give forward momentum, put the listener in the moment, and signal that you won't waste their time.
4. **Thoughts: what are you thinking [~3:16 to ~4:29].**
   - Rule: people have thousands of thoughts a day (hopes, plans, fears, worries, odd ones). Share the ones from the crucial moment.
   - His rewrites: instead of saying he was excited to meet his crush, give the happy thought about finally seeing her after so long; instead of saying a presentation disappointed him, give the panicked thought that everyone now thinks he is stupid and he can never show his face there again.
   - Mistake: thoughts that sound professional, like a line from a performance review. Nobody thinks like that. Give the raw, unfiltered version, a bit juicy and a bit neurotic.
5. **Emotions: what are you feeling [~4:29 to 5:38].**
   - Frame: the best stories take the listener on an emotional journey. Thoughts are one route; this is the second.
   - Weak rung: stating the emotion (relieved, disappointed, happy). It is what most people do, and the listener cannot see it.
   - Strong rung: show what the emotion does to the body and the face. His rewrites: relief becomes leaning back and letting out a long sigh; another person's anxiety becomes tapping a pen on the table and glancing at the clock every few seconds.
   - Why: showing is visual and places the listener in the specific moment.
6. **Dialogue: what are you hearing [5:38 to 6:54].**
   - Rule: most stories have more than one character (a manager, a friend, a coworker, even a dog). Give their exact words at the crucial moment.
   - His rewrites: a friend's disappointment becomes the friend turning to him, using his name, and asking what on earth that was; a manager's approval becomes the manager telling him it was the best presentation he has ever given.
   - He calls dialogue the tool he uses most.
   - Mistake: dull, formal dialogue (a manager complaining in boardroom language about the poor execution of a project). Pick short, catchy, juicy lines.
7. **Practice test [6:54 to 8:31].** A recap wheel of the five, then a BBC clip of about a minute with Sarah Willingham. Early in her career, running acquisitions for Pizza Express, she arrives two minutes late to a meeting, and the lawyer across the table, assuming she is there to serve drinks, gives her his coffee order. She makes the coffee, serves it, offers coffee to the room, sits down opposite him, and watches the color drain from his face. She reflects that being misjudged turned into a superpower and ends by pointing out who left with the deal. The viewer is asked to spot the location, actions, thoughts, dialogue and feelings. He never walks through the answers.

### 2. Mechanics that can become checks or templates

- **Opener formula** (every location and action example): [time marker] + "I'm" + [place] + [action verb]. The time marker is always there although he only teaches place and action. HUMM18 adds "when" plus a disruption.
- **Historical present.** All his own examples pair a past time marker with a present-tense verb (two weeks ago, I'm sitting...). He never states it as a rule, and two of his four model stories use the past tense (Willingham, DiCaprio). Tense is a style choice, not the mechanism.
- **Place is one noun phrase.** No furniture lists. Check: at most one descriptive clause about the setting before the first action.
- **Emotion ladder, HUMM9 version:** label < body or face cue. Body cues are small, visible, often repeated physical acts (tapping, glancing, leaning back, a sigh).
- **Thought line format:** I thought, '...', in the first person, present tense inside the quote, informal, often a question or an exclamation.
- **Dialogue line format:** in that moment, [person] looked at me and said, '...': a look, then a short line. The line uses a name or a strong reaction and no formal words.
- **Swap operator, used six times:** instead of saying [label], say [scene]. For our revision pass: find the label and replace it with a thought, a body cue or a line.
- **Five questions as a scene checklist:** where are you, what are you doing, what are you thinking, what are you feeling (shown), what are you hearing.

### 3. How the video itself is built

**Hook, first 30 seconds.**
- [0:00] A brief greeting over a title card (a speaker on a stage before an audience, with the words storytelling and hook your listeners).
- [0:01 to 0:16] A general claim about the power of stories, a vague enemy (the advice out there makes it complicated) and a reframe (it is simple once you know what matters).
- [0:16] The promise with a time cost and a count: nine minutes, five techniques. A card shows a brain inside a ring with five nodes; the ring returns later as the recap wheel.
- [0:24 to 0:37] A named demo (John Krasinski, with a nod to The Office), sized as a 20-second story, plus an outcome promise: by the end the viewer will tell stories like him.
- [0:37] The clip starts. First story content at 7% of runtime.
- Weakness: the first 16 s are generic (greeting, truism, vague enemy); the V2 file's lint check 1 would flag the greeting. The specific promise and the famous name do the hooking.

**Sections (real times).**

| Time | Section | Device |
|---|---|---|
| 0:00-0:37 | Hook and promise | Title card, nine-minutes card, name card |
| 0:37-0:58 | Krasinski clip: a customs officer cannot believe who his wife is | Clip in a branded frame; laughter and a desk slap in the log |
| 0:58-~1:32 | Principle: zoom in, not helicopter | Black-and-white recap as the wrong way |
| ~1:32-~2:29 | 1 Location | Numbered card with its question; a cut to a different living-room set; black-and-white furniture icons for the mistake; a question card on why it matters |
| ~2:29-~3:16 | 2 Actions | Action icons; a cut to an office set |
| ~3:16-~4:29 | 3 Thoughts | Thought-bubble graphic; black-and-white BEFORE inserts |
| ~4:29-5:38 | 4 Emotions | Teal AFTER inserts; an eye-and-faces card on showing emotion |
| 5:38-6:54 | 5 Dialogue | AFTER inserts; a pop sound; a check-mark card; black and white for the dull version |
| 6:54-7:18 | Recap and set-up | Five-technique wheel; Willingham name card; the list to spot |
| 7:18-8:31 | Willingham clip | BBC clip with burned-in captions |
| 8:31-8:52 | Wrap and CTA | Tease of advanced techniques; pointer to the next video |
| 8:52-8:58 | End screen | Subscribe plus a next-video slot |

Proportions: hook and first demo 17%, the five techniques 60% (between 47 and 76 s each), second demo and close 23%.

**Open loops and payoffs.**
- Five techniques promised [0:16] → paid in order, each with a numbered card → recap wheel [~6:55]. The count is on screen, so the viewer always knows how much is left.
- The Krasinski demo [0:24] → shown [0:37] → decoded [0:58] → the principle.
- The spot-the-elements test [7:12] → never debriefed. The viewer checks alone; HUMM18 fixes this.
- Advanced techniques teased [8:38] → left open on purpose and pointed at the next video.

**Stories used.** Two borrowed celebrity stories (one comic, one business), each chosen for a strong reversal, and about a dozen one-line micro-examples in his own voice (couch, conference room, laptop and a message from the manager, airport security, a crush, a failed presentation, relief, anxiety, a friend's reaction, a manager's praise). No full story from his own life.

**Pacing.** About 1,300 words in his own voice at roughly 180 words per minute; sentences average 12 words and 14% run past 20; 2.7 questions per minute, several of them the tag "right?"; about 6 second-person forms per minute. In the frames sampled every 10 s, just over half show a graphic, a set change, a before or after insert, or a clip. The longest run of plain talking head in those frames is about 80 s, from roughly [3:50] to [5:10] (the end of thoughts into emotions). Music runs under his talk and stops for the clips.

**Ending and CTA.** A two-line recap (the viewer now has the foundations), a tease that more advanced techniques exist, a spoken pointer to a next video that promises to make the viewer a better storyteller than 99% of people, a sign-off, and an end screen (subscribe, next video, and a line promising more juicy tips).

### 4. Weak, unproven or questionable advice

1. **Where the 176% comes from: nowhere the viewer can see.** The number is not said, did not appear in any frame we sampled, and nothing in the video measures anything: no before and after, no audience test, no scale, no sample. An odd, precise figure reads as measured (precise numbers are taken as a sign of the speaker's confidence: Jerez-Fernandez, Angulo and Oppenheimer, Psychological Science 2014, cited from memory and not re-checked here). HUMM18 uses the same title formula with 183%, and this batch also holds a Kallaway title promising 10x. Treat it as title copy.
2. **The 99% and like-him promises** (the CTA and [0:33]) are status claims no one can measure.
3. **The demo doesn't show the method.** The Krasinski clip starts mid-story; it has no place or action line (Humm supplies the customs setting in his own recap) and is almost pure back-and-forth dialogue. Its punch comes from delivery (acting out the officer, the double take, the desk slap, the laughter) and from a built-in surprise. None of the five techniques teaches those.
4. **Details as irrelevant.** Right about set dressing, too strong as a rule. One telling detail can carry a scene: the lawyer's precise coffee order does much of the work in the Willingham story. Better: one place noun, plus at most one detail that serves the point.
5. **Stating an emotion as second best.** Right at the peak, too strong elsewhere. Willingham names her feelings in her closing reflection and he calls her an incredible storyteller. Our rule: show at the peak, labels allowed in the reflection.
6. **Juicy, neurotic thoughts** carry a register risk: fine on a personal channel, wrong for many brands and for audiences that expect clean speech.
7. **The five overlap.** Thoughts are introduced as a way to make a story emotional, then emotions follow as a separate technique; HUMM18 merges them. The count is partly packaging.
8. **Silent on structure.** Nothing on which moment deserves the zoom, on stakes, on the turn, on endings or on length. Zooming every sentence would give a slow, bloated story; the implied rule (zoom into the crucial moment only) is never stated.
9. **The thousands-of-thoughts line** is harmless as a figure of speech. If a script turns it into a number (the popular 60,000 a day), our pop-science check should flag it: that figure has no traceable study behind it.
10. **Dialogue as his most-used tool** is a preference, not evidence.

---

## Video 2: HUMM18, "Give me 18min & I'll improve your storytelling skills by 183%"

### 1. What it teaches, as a method

1. **Diagnosis and principle [0:17 to 2:37].** He asks the room for the single most important element of a great story. The guesses (hook, conflict, authenticity, emotion) go on the whiteboard. A clip follows (on-screen card: Anne Hathaway): at the gym, a man she catches staring turns out to be a trainer looking for clients, and when she mentions she had a baby seven weeks earlier he asks whether she is trying to lose the baby weight; she answers with as much dignity as she can manage and cries a little afterwards. The room adds details to the list. He says every answer is right but they share a theme, and explains it with a war film: an aerial shot of tanks and soldiers holds you for two seconds, then you want to be down in the mud with the soldiers. Stories stuck in helicopter view summarize (a hard problem, it was tough, I overcame it); the best storytellers zoom into the trenches. Zooming in has four steps: PAST.
2. **P, place [2:51 to 4:08].**
   - Mistake: opening with description (a warm Sunday afternoon, birdsong, a scent in the air). He says you have lost the room before you begin.
   - Fix: open with where you are, already in motion: two weeks ago, in his apartment in Amsterdam, looking at his laptop; last July, in front of a conference room, taking a deep breath. The picture starts forming at once.
   - Answering a question he raises himself: no need to describe the room; any conference room in the listener's head will do.
3. **A, action [4:08 to 5:19].**
   - Mistake: the most common one he hears (he says he has listened to thousands of stories) is too much context first: years at a company, a nice company, a manager he liked, and the listener still wondering where the story is.
   - Fix: start in the action with forward momentum, often with an interruption: in his Amsterdam apartment when a notification pops up; at airport security, putting his bag on the belt, when someone calls his name.
   - Use action verbs (walk, shout, bike, open or close a door). Each adds a frame to the movie in the listener's head.
4. **Exercise 1: rewrite the first 20 seconds of your story with place and action [5:19 to 7:40].**
   - Volunteer 1 opens on a woman walking toward her with open arms, her own heart sinking because she can't remember the woman's name, the woman greeting her by name, and her wish that the floor would swallow her. He praises the action unfolding and adds a tip [6:20]: **give the date as well as the place**, because time plus location makes listeners accept a story as true, while without them some start to doubt it.
   - Volunteer 2 tells of accidentally inviting the wrong one of two men with nearly identical names to a beach club. Straight into action, he says, and asks for **the words said in that moment**. On the retry she gives the exact exchange (her casual see-you-Sunday, his puzzled reply) and he says that's it.
5. **S, speech [7:40 to 9:51].**
   - The technique he uses most. Stories have several characters; give their exact words at the crucial moment.
   - His rewrite: a manager being upset becomes the manager phoning and telling him, with a swear word he swallows on stage, that he was all over the place in the presentation.
   - Whiteboard exercise [8:24]: three flat lines to turn into speech (an upset customer, a happy mum, a proud coworker). He does the customer: a furious call saying the technology he sold broke their whole production system. A volunteer tries the mum (a surprise visit on her birthday); he first describes two smiling faces, and when asked for the mother's words, offers one. Philipp asks whether his mother really talks like that and suggests an excited, disbelieving shout as the kind of line to look for. The proud coworker is never done.
6. **Objection: what if you don't remember the words? [9:51 to 10:07].** Use words that could have been said in that moment. He calls it creative freedom.
7. **Exercise 2: find and stage the key line [10:07 to 12:25].** A volunteer tells of ending a five-year relationship in the kitchen one Sunday evening; her partner's first reply is a practical question about the house. His coaching: find the most important line in the story, here that reply. The one quote in this file: "That's the moment that you want to milk." [11:19]. Pause longer around it, and before it build anticipation by sharing the thoughts that set up an expectation (is he going to try to win me back?), so the contrast is bigger. On the retry she voices her expectation first; he says the anticipation made the story much stronger and that she could pause even longer after the line.
8. **T, thoughts [12:25 to 13:31].**
   - The technique that makes any story emotional and connects the teller with the listeners.
   - **Three-rung ladder:** bad storytellers summarize (a difficult situation with the manager); amateurs name the emotion (the manager was frustrated); great ones share the exact thought of that moment (a fear that the manager will hate him for this).
   - People have thousands of thoughts a day, many of them odd or anxious; share some.
9. **Exercise 3: three flat lines to turn into thoughts [13:31 to 15:58].** Nerves before a meeting, excitement about a date, embarrassment about money.
   - He does the first: a spiral of dread (this will be terrible, they will tear the presentation apart, he will end up crying in the meeting).
   - The date volunteer first summarizes (trying outfits, anxious, wanting it perfect). He pushes twice: you are standing at the wardrobe, what exactly is in your head right now, and don't summarize it. She lands on a run of short questions to herself (will he be funny, will I laugh at his jokes, are we a match).
   - The money volunteer, rejected by his crush over dinner, gives the thought he had when the bill came (should he still pay for her?) and what he did (paid only for himself and left). Philipp says that thought made it interesting and real.
10. **Mistake: the polished thought [15:58 to 16:16].** People report thoughts in a tidy, career-minded form. His own thoughts are short and blunt (a bleeped one-liner about being doomed).
11. **Recap and test [16:16 to 18:25].** PAST cards, then a clip (on-screen card: Leonardo DiCaprio): on a plane to Russia he sees an engine turn into a fireball, seems to be the only one who notices, feels he has already died, and screams; a flight attendant calmly reports a small problem, a passenger asks what it is, and the answer is that the plane had two engines and now has one. The room finds each element: the place (the plane), the action (looking out of the window, the explosion), the speech (the passenger and the attendant, which DiCaprio acts out) and the thought (feeling he had already died). He closes: any ordinary moment can become a great story if you zoom in with PAST.

### 2. Mechanics that can become checks or templates

- **Opener template with disruption:** [time], I'm [place] [action], when [event]. Both his action examples follow it, and so does volunteer 2's opening.
- **Truth anchor:** time plus place in the opening [6:20]. For us: present in personal stories, always true, always taken from the brief.
- **Context after motion:** backstory follows the first action. Volunteer 2's necessary backstory (a separate plan with the other man) comes after her opening scene, and it works.
- **Three-rung ladder as a line score:** summary 0, named emotion 1, exact words (speech or thought) 2.
- **Rewrite operators:** flat line → speech (a person calls or looks at me and says '...'); flat line → thought (I'm standing there thinking '...'). He insists the thought is framed inside the moment (at the wardrobe, now), not reported afterwards.
- **Voice-match test for dialogue** [9:25]: would this person really say it like that?
- **Key-line staging:** the key line is the line the story turns on; an expectation thought just before; the key line alone; a pause after. The contrast is the gap between the voiced expectation and the line.
- **Stacked questions as a thought:** a run of short questions shows anxiety without naming it.
- **Spot-the-elements debrief:** after a model story, label where each element appears. A judge can do the same to our drafts.

### 3. How the video itself is built

**Hook, first 30 seconds.**
- [0:00 to 0:17] Cold open, no greeting. He says he studied 78 of the world's most successful speakers and hundreds of their videos (cut-out photos of famous speakers, then a card asking how they tell stories), that it all comes down to one thing most people don't use (a shattering ONE THING title), and that knowing it puts you among the top 1% of storytellers (a gold TOP 1% title). Music under all of it.
- [0:17] A question to the room: what is the single most important element? Four guesses appear as on-screen labels.
- [0:33] The loop is extended: watch this clip, then say which one it is.
- Devices: proof of effort, a single secret, exclusivity, a status outcome, a question the viewer answers in their head, and a demo that delays the answer.

**Sections.**

| Time | Section | Device |
|---|---|---|
| 0:00-0:17 | Claim: 78 speakers, one thing, top 1% | Cut-outs, kinetic titles, music |
| 0:17-0:43 | Guess the one element | Guesses as labels; whiteboard list |
| 0:43-1:41 | Gym clip, about 58 s (announced as 30) | Name card, ellentube logo |
| 1:41-2:37 | Debrief, war-film analogy, the answer | War footage from above; black and white for the helicopter summary |
| 2:37-2:51 | PAST named | Letter cards |
| 2:51-4:08 | P, place | Office overlay for the good opener; black and white for the over-description he rebuts |
| 4:08-5:19 | A, action | Numbered verb list overlay |
| 5:19-7:40 | Exercise 1, two volunteers | Place and date icons at 6:20 |
| 7:40-9:51 | S, speech, whiteboard exercise | S card; list overlay; conference-room overlay |
| 9:51-10:07 | Objection: memory | |
| 10:07-12:25 | Exercise 2, break-up story with retry | Pause and anticipation icons; applause |
| 12:25-16:16 | T, thoughts, exercise 3, the polished-thought mistake | T card; captions on volunteer lines; a bleep |
| 16:16-16:34 | Recap | P A S T cards |
| 16:34-17:15 | Plane clip | Name card, ellentube logo |
| 17:15-18:25 | The room finds each element; close | |
| ~18:27-18:34 | End screen | The same card as HUMM9 |

Proportions: hook to answer 14%; the four letters with their exercises 74%; test and close 12%. Exercises take about 9 of the 18 minutes (about 2.4, 1.6, 2.4 and 2.5 minutes), plus a one-minute debrief at the end.

**Open loops and payoffs.**
- The one thing [0:10] → answered at ~[2:31], 14% into the video. The main loop pays early; from then on the four PAST letters work as a visible progress bar (cards and whiteboard).
- Which guess is right [0:33] → all right but incomplete [1:56] → zoom in [2:31].
- Two superlative teasers pay at once: the technique he uses most [7:42] → speech; the one that makes stories most emotional [12:27] → thoughts.
- The memory objection [9:51] → answered in 15 s.
- Three whiteboard lines for speech [8:24] → only two done; the proud coworker never gets a turn.
- The final clip [16:27] → debriefed with the room, element by element.

**Stories used.** Two celebrity clips (gym, plane), a war-film analogy, his own one-line examples (Amsterdam apartment, conference room, a notification, airport security, a manager, a customer) and five volunteer stories that become live before-and-after demonstrations. The live rewrites are the best proof the method teaches: the viewer hears a flat version and a better one from the same person minutes apart.

**Pacing.** About 2,650 words from him; sentences average 11 words (14% over 20); 3.2 questions per minute, 20 of them the tag "right?"; about 6 second-person forms per minute. Clips take about 9% of runtime and audience or volunteer speech about 19%. A new segment (clip, letter, exercise or objection) starts every 1 to 2.5 minutes, and a card or icon marks each one. Laughter and applause logged through the exercises act as social proof.

**Ending and CTA.** A one-line promise that any ordinary moment can become an incredible story by zooming in with PAST, and that the viewer's stories will be unrecognizable. No spoken CTA and no subscribe ask; the end screen (the same card as HUMM9) does the CTA. The last spoken line comes right after the last payoff, so nothing sags.

### 4. Weak, unproven or questionable advice

1. **The 183% in the title**, as in HUMM9: never said, never shown, nothing measured. A video that teaches a subset of HUMM9's techniques claims a bigger gain, which suggests the numbers are title copy.
2. **78 speakers, hundreds of videos, thousands of stories.** No list, no selection criteria, no coding method, no result. The finding (render a scene instead of summarizing) is an old craft rule (show, don't tell; scene against summary) that needed no 78-speaker study. The famous faces in the hook imply they were among those studied; nothing in the video says so.
3. **One thing most people don't use; the top 1%.** Unsupported and unmeasurable.
4. **The single most important element.** He grants that hook, conflict, authenticity and emotion are all true, then calls zooming the theme beneath them. Zooming does not create conflict. Every demo (the trainer's assumption, the engine count, the lawyer's coffee order, the customs double take) carries a reversal; a vivid scene with nothing at stake stays flat. The framework takes credit for the structure of well-chosen stories.
5. **Words that could have been said.** Normal in oral anecdote, where the gist is true and the teller owns the memory. Wrong in nonfiction, testimonials, case studies and ads, where invented quotes from real people mislead viewers and can break advertising rules on endorsements. Our skill needs a mode: reconstructed speech only in the teller's own anecdote, with the gist confirmed by the teller.
6. **Date and place as proof of truth.** No evidence offered, and the trick works as well for invented stories. Our rule: dates and places must be real and come from the brief; never add specifics to make a story feel true.
7. **No description of the place, yet he wants to see the mud on the soldiers' faces.** His own analogy asks for a vivid sensory detail. The consistent rule: no set dressing, but one telling detail when it serves the point.
8. **Body cues dropped.** HUMM18's ladder puts exact thoughts at the top and leaves out the body language HUMM9 taught. In video the picture often carries emotion better than a narrated thought, and in audio one body cue is sometimes cleaner than inner monologue. Keep both.
9. **No dose.** Thoughts and speech are praised without a limit. A story where every beat has inner monologue turns slow and self-absorbed; a story is not a transcript of every line said.
10. **Clip timing.** The gym clip is announced as 30 seconds and runs about a minute. Minor, but the kind of slip a fact check should catch.
11. **Register.** Swearing from him and from volunteers is presented as raw and good. Raw should mean honest and colloquial.

---

## Where the two videos differ

| | HUMM9 | HUMM18 |
|---|---|---|
| Format | Talking head at home, dense motion graphics | Workshop with an audience, whiteboard, letter cards |
| Tools | Five: location, actions, thoughts, emotions, dialogue | Four: place, action, speech, thoughts |
| Emotion | Shown on the body and face, and through thoughts | Through thoughts only |
| Only here | Body and face cues | Date plus place; the "when" disruption; key-line staging; the memory license; the voice-match test; the three-rung ladder |
| Model stories | Krasinski (pure dialogue), Willingham (business) | Hathaway (gym), DiCaprio (plane) |
| Test story | Not debriefed | Debriefed with the room |
| Hook | Greeting, general claim, promise with time and count, celebrity demo | Cold research claim, one secret, top 1%, a question to the room |
| CTA | Spoken, plus end screen | End screen only |

---

## Synthesis for our skills

PAST is scene craft. It decides how a moment is told, not which story to tell or why it matters. In nexa-script it belongs to the drafting and revision of story beats, after R3's structure pass (character, question, conflict, turning point, reveal; R3 4.4) and the LEVELS questions in the V2 file, as the concrete form of their final line pass. Its research backing sits in R3, not in Humm: concreteness (R3 2.7) and narrative transportation (R3 2.1). Thought narration also appears among Kallaway's tactics (R3 4.1), so two independent creators converge on it.

### A. Rules the script skill should adopt

- **H1 Find the moment first.** Every story names its turn: the line, act or reveal that changes things. Zoom there and summarize the rest in short lines. Short form: one zoomed scene. Long form: one per story, at most two.
- **H2 Open on an anchor.** In the first sentence or two: a real time marker, one place noun, an action verb, and usually the disruption ("when..."). No weather, scenery or job history first.
- **H3 Context after motion.** Backstory comes after the first action, in one or two lines, or folded into the action.
- **H4 Render the key moment.** At least one direct line of speech or thought in the key moment; speech is preferred for the turn when another character is present.
- **H5 Show at the peak, label in the reflection.** No "I was nervous" inside the key moment; use a thought, a line or a body cue. Naming the feeling afterwards, in one line, is fine.
- **H6 Sound like the person.** Quoted lines and thoughts are short, colloquial and in character, and pass the voice-match test (would this person really say it that way?). No corporate words inside quotes. Raw means honest, not rude: no profanity unless the brief's voice allows it.
- **H7 Stage the key line.** The sentence before it sets up the expectation (usually a thought); the key line stands alone; a pause follows (`[beat]` in the script, a TTS break of about 0.7 to 1.2 s as our starting value); the reaction or punchline comes after.
- **H8 Let the picture carry what it can.** In video scripts the place and the body cues can move to the visual column; narration keeps speech and thought. In audio-only work, keep one body cue in the narration.
- **H9 One tense per story in English.** Historical present suits spoken anecdotes; the past is fine. Switch only with a time jump. Not applied to Bangla (see E).
- **H10 Declared truth modes.** `personal` (the teller's own anecdote): reconstructed dialogue allowed, marked in `script.json`, gist approved by the teller. `nonfiction`, `testimonial`, `case_study`, `ad`: no invented quotes from real people; every quote maps to the ledger or to client-approved words; dates and places only from facts given. Never add specifics to make a story feel true. (Matches R3 rule R12.)
- **H11 No invented numbers in titles or hooks.** No improve-by-N%, top-1% or better-than-99% claims without a measurement we can show.
- **H12 Teaching videos may use his build** (tutorials, explainers, skill videos): demo first, the principle in one line with a picture, numbered steps with the count visible on screen as a progress bar, a before-and-after rewrite in every step, a second demo as a test, then a debrief. Pay every listed or promised item.

### B. Templates

**T1, anchor opener.** `[time], I'm [place] [action], when [disruption].`
- English (ours): "Last Thursday, I'm third in line at the bank when my phone buzzes: payment failed."
- Bangla (ours): "গত বৃহস্পতিবার, ব্যাংকের লাইনে টোকেন হাতে দাঁড়িয়ে আছি, ঠিক তখনই ফোনে মেসেজ এল: Payment failed."

**T2, the zoomed key moment (six slots, one or two short sentences each).**
1. Anchor: place and action (T1).
2. Expectation: the thought that sets up what the teller expects or hopes.
3. Trigger: the other person's exact words, or the event, as the key line.
4. `[beat]`: a pause.
5. Reaction: a raw thought or one body cue.
6. Consequence or punchline; then, optionally, one line of reflection (labels allowed there).

The Willingham story maps onto it: she walks into the meeting room late (1); the lawyer's coffee order is the trigger (3); her thought that this is a moment fuses expectation and reaction (2 and 5); she makes and serves the coffee and sits down opposite him (6); his face drains of color (5, a body cue on the other person); then the reflection and the punchline.

**T3, the rewrite ladder (a revision pass).** For every summary or label line in a story, climb one rung: summary (0) → named emotion (1) → exact words: a line, a thought or a body cue (2). One per sentence; don't stack all three.

**T4, teaching-video skeleton.**
1. Hook: either a promise with a time cost and a count, or proof of effort plus one secret plus a question to the viewer.
2. A demo story under 60 s.
3. A did-you-notice question and the principle in one line with a picture.
4. N steps, each with a name card, a guiding question, the common mistake (the before, in black and white), the fix (the after, in color) and why it works.
5. A recap card.
6. A second demo; the viewer spots the elements; a debrief.
7. A one-line takeaway and one CTA.

**T5, `script.json` fields for story beats** (an addition to the beat schema in DESIGN.md section 3): `story.mode` (personal, nonfiction, testimonial, case_study, ad), `story.time`, `story.place`, `story.action`, `story.disruption`, `story.key_moment` (a beat id), `story.key_line`, `story.expectation_line`, `story.pause_ms`, `story.speech[]`, `story.thoughts[]`, `story.body_cues[]`, `story.reflection`, `story.reconstructed[]` (quote ids) and `story.approved_by`.

### C. What the lint should measure

Starting thresholds are ours, to be calibrated on our own scripts. Reference values follow the table.

| # | Check | How to measure | Starting threshold | Source |
|---|---|---|---|---|
| HL1 | Story anchor | First two sentences of a story's opening beat: a time marker, a place phrase and a finite action verb (lists per language) | All three; warn if time or place is missing, fail if there is no action | HUMM9 ~1:32-~3:16; HUMM18 2:51-5:19 |
| HL2 | Context before action | Words before the first action verb of a story; backstory markers (used to, for about N years, I had been working at) | Short form ≤ 20 words, long form ≤ 40 | HUMM18 4:12 |
| HL3 | Set dressing | Setting clauses before the first action: weather, time-of-day openers, smells and sounds, adjective stacks; a ban list per language | Warn at 2 or more | HUMM18 2:51; HUMM9 ~2:05 |
| HL4 | Named emotion at the peak | I was/felt (very/so) + emotion, and he/she was + emotion, inside the `key_moment` beat; an emotion lexicon per language | 0 in the key moment; allowed in `reflection` | HUMM9 ~4:29-5:38; HUMM18 12:42 |
| HL5 | Reported speech | told me that, said that, asked me whether, was very upset with me, inside story beats | Warn each; suggest a direct line | HUMM9 5:38; HUMM18 8:07 |
| HL6 | Speech or thought in the key moment | Quoted lines and thought frames (I thought, I'm like, in my head) in `key_moment` | ≥ 1 of either; ≥ 1 speech line when another character is present | Model stories below |
| HL7 | Spoken-sounding quotes | Words per quoted sentence; sentences per quoted turn; formal words inside quotes (represents, opportunity, inadequate, execution, dissatisfied, regarding, furthermore); passive voice | ≤ 15 words per quoted sentence, ≤ 2 sentences per turn, no formal words | HUMM9 ~3:57, 6:28; HUMM18 15:58 |
| HL8 | Key-line staging | A thought or expectation line within the two sentences before `key_line`; a pause mark after it | Both present | HUMM18 11:14-12:23 |
| HL9 | Zoom balance | Share of a story's words inside the zoomed scene; number of zoomed scenes | Scene ≥ 50% of the story's words; 1 zoomed scene per short story, ≤ 2 per long one | Model stories; H1 |
| HL10 | Tense drift (English only) | Past against present finite verbs per story beat | Warn on a mid-beat switch without a time jump | Ours |
| HL11 | Register of raw lines | Profanity and bleep-worthy words in quotes and thoughts, against the brief's voice | Fail if the brief is clean, warn otherwise | HUMM18 15:30, ~16:14 |
| HL12 | Truth of quotes, dates and places | Nonfiction modes: every quote attributed to a named person maps to a ledger quote or approved client words; every date and place in a story is in `facts_given`. Personal mode: reconstructed quotes are marked | 100% | HUMM18 6:20, 9:51 |
| HL13 | Unsupported improvement claims | improve ... by N%, N% better, Nx, top 1%, better than 99%, without a ledger source | Fail in client finals, warn in drafts | Both titles; HUMM18 0:13; HUMM9 8:42 |
| HL14 | Promised items paid | Counted or listed items (N steps, three examples, a spot-the-elements test) each covered, and each test debriefed | All paid | HUMM9 7:12; HUMM18 8:24 |

**Reference values from the four model stories.**

| Story | Runtime | Place and action in the first sentence | Lines with direct speech or thought | Tense |
|---|---|---|---|---|
| Krasinski, customs (HUMM9) | ~21 s | No: the clip starts mid-story and Humm supplies the setting | nearly all 15 | mixed, mostly present (he goes, I go) |
| Willingham, meeting room (HUMM9) | ~72 s | Yes: age, job, place, lateness and the lawyer's line all in sentence one | 3 of 8 | past |
| Hathaway, gym (HUMM18) | ~58 s | Yes: on a machine, being stared at | about 12 of 18 | present |
| DiCaprio, plane (HUMM18) | ~41 s | Yes: a plane to Russia and an exploding engine in ten words | about 7 of 10 | past |

So the model stories carry direct speech or thought in between about 40% and nearly 100% of their lines, and only half of them use the present tense.

**Reference values for his own delivery** (English, to camera or to a room).

| Metric | HUMM9 | HUMM18 |
|---|---|---|
| Words in his own voice | ~1,300 | ~2,650 |
| Speech rate | ~180 wpm across his screen time | roughly 180 to 200 wpm (an estimate; workshop pauses blur it) |
| Mean words per sentence | 12.3 | 10.9 |
| Sentences over 20 words | 14% | 14% |
| Questions per minute | 2.7 | 3.2 |
| "right?" tags | 7 | 20 |
| Second-person forms per minute | 5.8 | 5.6 |
| First story starts | 0:37 (7%) | 0:43 (4%) |
| Main principle stated | ~1:10 (13%) | ~2:31 (14%) |
| Clips as a share of runtime | ~17% | ~9% (plus ~19% audience and volunteers) |

These sit inside the V2 file's general thresholds (mean sentence length ≤ 16, direct address ≥ 3 per minute), so they need no new general check.

### D. What the judge should score

Give the judge only the script, the brief and the ledger. These seven dimensions cover scene craft. They sit beside R3's J1 to J10 and the V2 file's J1 to J10, and refine R3's J7 (specificity) and J10 (truth).

| # | Dimension | 1 | 3 | 5 |
|---|---|---|---|---|
| HJ1 | Moment choice | No moment: the story is a summary | A scene exists, but not at the turn | The zoom lands on the turn: the line or act that changes things |
| HJ2 | Anchor | Opens on backstory, scenery or weather | Place or action, but late or vague | Time, place and action in the first sentence or two, plus a disruption |
| HJ3 | Speech | Reported (she told me she was upset) | Direct but stiff, long or out of character | Short, in-character words that carry the turn |
| HJ4 | Inner life | Feelings named at the peak | Some thought or body cue, mixed with labels | A specific, raw thought or body cue at the peak; labels only in the reflection |
| HJ5 | Economy | Set dressing, a context dump, or every beat zoomed | Some filler | Summary where speed helps, scene where it matters, at most one telling detail |
| HJ6 | Key-line delivery | The key line is buried mid-sentence | Clear but unstaged | Expectation set just before, the line alone, a pause after, the contrast felt |
| HJ7 | Truth of reconstruction | Invented quotes or specifics presented as fact, or a real person misquoted | A personal anecdote with plausible but unmarked reconstructions | Every quote, date and place sourced or approved; reconstructions marked |

Hard fail regardless of score: HJ7 at 1 in any nonfiction mode.

For teaching videos, add one line to the judge: every listed item is paid, every step has at least one before-and-after rewrite, and every test example is debriefed.

**Three judge tests taken from his teaching.**
- *Picture test:* after the first two sentences of a story, the judge writes where we are, who is there and what they are doing. A blank in any slot fails the anchor.
- *Zoom-point test:* the judge picks the one sentence it would zoom into. If it differs from `story.key_moment`, the zoom is misplaced or the turn is unclear.
- *Summary test:* the judge rewrites the story as one line. If the line loses nothing that matters, the story was never zoomed in.

**Panel questions for the audience personas:** at which line could you first picture the scene; which line would you repeat to a friend (it should be the key line); where did you feel what the teller felt; where did your attention drop.

### E. Bangla and South Asian notes

- Time markers for HL1: গত সপ্তাহে, দুই সপ্তাহ আগে, সেদিন রাতে, ২০১৯ সালের সেপ্টেম্বরে. The "when" of T1: ঠিক তখনই, হঠাৎ.
- Thought frames for HL6: মনে মনে ভাবছি, মাথায় একটাই কথা ঘুরছে. A run of short questions works in Bangla just as in English.
- Reported-speech markers for HL5: বলল যে, জানাল যে, জিজ্ঞেস করল যে.
- Emotion labels for HL4 (inside the key moment only): খুব নার্ভাস ছিলাম, খুব খুশি হলাম, লজ্জা পেলাম, ভয় পেয়ে গেলাম, মন খারাপ হয়ে গেল.
- Tense: spoken Bangla anecdotes move between present and past freely (দাঁড়িয়ে আছি, হঠাৎ দেখি...), so HL10 stays off for Bangla.
- Raw register: everyday cholito lines, clean by default. Rawness comes from honesty and specificity, not swearing. Religion-tied exclamations only when they match the teller.
- Places, prices and moments come from the client's market (a bank queue, a bus counter, a cousin's wedding for a Bangladeshi brand), never from the writer's defaults.

### F. What not to adopt

- Precise improvement percentages and top-1% or better-than-99% promises in titles or hooks without data.
- Effort-and-authority hooks (N speakers analysed) unless we can show the list and the method.
- Invented could-have-been-said dialogue outside the teller's own anecdote.
- Date and place used as a credibility trick.
- Swearing as the meaning of raw.
- Dropping body cues (HUMM18's ladder): keep them for audio and hand them to the visual column in video.
- PAST as a whole-story method: it is scene texture; pair it with R3's structure (4.4, 6.1) and the V2 file's LEVELS questions.
- Zooming every sentence: one moment per story gets the full treatment.
