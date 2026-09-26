# V1 method videos, part 1: how three Hindi creators teach research and scripting

Prepared 2026-09-26 as input for our research skill and our script skill. Three Hindi (Hinglish) YouTube tutorials, chosen by the owner as teaching material, are broken down into method, tools, checkable rules, construction, and weak spots, then combined into one workflow with checks and templates.

| # | Video | Channel | Length | Format |
|---|---|---|---|---|
| V1.1 | "How to Research Any Topic and Monetize It? \| Modern Tools Used By Creators?" (`N6RDear_xFE`) | HimanshuG | 10:51 | Presenter on camera, keyed over animated backgrounds, very fast cutting |
| V1.2 | "How to Research and Script Any Topic for YouTube (STEP BY STEP)" (`q2bOMglypxg`) | DecodingYT | 10:49 | Faceless voice-over, motion graphics, screen recordings |
| V1.3 | "How to Research Like @dhruvrathee \| Script Like Dhruv Rathee" (`7hdwmTagRSk`) | Tube Sensei | 10:47 | Faceless voice-over with an animated avatar, diagrams, Dhruv Rathee clips |

## How the sources were read (read this before trusting a timestamp)

- All three `.txt` transcripts were read end to end. Everything below is translated and paraphrased. There is one short quote (in V1.3).
- **DecodingYT transcript fault.** In `q2bOMglypxg/transcript-*.txt`, the timestamps from about 1:02 to 4:57 run about 40 s late, and roughly 35 s of speech (about 4:24 to 5:00: where to find answers, and why not to take answers from ChatGPT) is missing. The segment that starts at 0:58 is stretched to 1:42 to cover the jump. I re-transcribed 0:55 to 5:05 from the cached video (Gemini, via the agy-watch-video skill) and checked 9:30 to 10:00. **All DecodingYT times below use the corrected timing.** The transcript files themselves were not changed; that transcript should be regenerated.
- The other two transcripts were spot-checked at 4:30 to 5:00 and 9:30 to 10:00 against fresh transcriptions: they are within about 3 s.
- Speaker labels are unreliable. `S2` and `S3` are usually inserted clips (Dhruv Rathee's narration, film or meme audio), but after each 5-minute chunk boundary the labels can swap.
- To describe how each video is built, I ran a visual-only overview of each video (about 1 frame per second) and checked key frames myself. On-screen text quoted here comes from frames I looked at. Details marked "(visual pass)" are a model's reading and were not checked frame by frame.
- Sound effects and music changes come from the transcript JSON (`sounds`, `music`). Shot counts are ffmpeg measurements.
- Anything flagged as wrong is checked against well-established facts only; items marked "verify" need a source check before we reuse them.

## At a glance

| | V1.1 HimanshuG | V1.2 DecodingYT | V1.3 Tube Sensei |
|---|---|---|---|
| Core method | Basics first, then chain question after question (4W1H) on one running example | 5W1H grid, then find and verify answers, then horizontal and vertical logic, then script | Classify topic as What (news) or Why (explainer), pick horizontal or vertical logic, 4W1H at every node, Dhruv's script pattern |
| Best single idea | Prior-coverage template: check what videos, documentaries, books, journalism, papers and shorts already exist before researching | AI may write the questions, never the answers; use only cited AI answers and open the citations | Background, then jump to the present, so the viewer asks "how did we get here?", then a mid-video contradiction to re-wake interest |
| Best structure device | One running case (Project Cheetah) threads every step; bookend ending | On-screen checklist that is ticked at every section change | Teach a pattern, then build it on a fresh topic |
| Biggest weakness | Unsourced numbers, including a "scientifically proven" claim whose on-screen citation says something else | Blunt source rules; an intuitive breadth list that misses the main factor | The demo script contains factual and chronological errors; opinion-steering advice for news |

---

## V1.1 HimanshuG: "How to Research Any Topic and Monetize It?" (`N6RDear_xFE`, 10:51)

### 1. What it teaches, step by step

1. **Research sits under every format people love.** Films, Netflix series, YouTube videos, reels, college papers, broadcast analysis and a Money Heist style plan all run on research. He promises "four things" to keep in mind before researching [0:00].
2. **Adopt the nosy relative's mindset.** Imagine being 45 and grilling a young person: what do you do, how do you do it, is that right, what's your salary. He asks viewers to hold on to these 20 seconds for later [0:16 to 0:31]. The callback comes at [4:19]: research is that same relentless questioning.
3. **Find the topic idea when relaxed.** Ideas arrive in the shower because the mind is relaxed and the subconscious passes an insight to the conscious mind [0:31 to 1:08]. (The science he attaches is wrong; see section 5.)
4. **Study a pro example.** He uses Dhruv Rathee's Project Cheetah video, whose opening is all dates and numbers: September 2022, eight African cheetahs from Namibia; February 2023, twelve more from South Africa [1:08 to 1:33].
5. **Rule 1, basics first.** Collect the general facts that appear on the first page of search results: dates, numbers, the stated reason for the thing [1:33 to 1:57].
6. **Apply 4W1H.** Spoken as why, when, where, how and "for what purpose"; the on-screen card reads `4W 1H: Why, When, Where, Who, How`. In his examples the first question is always "what is it" [1:57 to 2:14]. Answering the basics takes you one level deeper [2:14].
7. **Every heading becomes a question, every answer a new question.** Project Cheetah (heading), why was it started (sub-heading or question), because cheetahs declined, so why did they decline, where did they decline, how many were there before we started calling them few [2:31 to 3:30]. On screen the questions stack up as cards.
8. **Count and deepen.** One minute of chaining gave six researchable questions [3:39]. To go deeper, write more questions and read further down the results, more pages [3:47 to 4:03]. How deep is your choice [3:55].
9. **Copy how the pro goes deep.** Dhruv turns "reasons" into the next layer (hunting, habitat loss) and then asks why, how, since when and what followed for each [4:03 to 4:19].
10. **Don't fear the volume.** He claims 80 percent of what you need is on the first results page [4:21].
11. **Build a prior-coverage template before researching.** For the topic, is there already a video, a documentary, a book or e-book, a journalist's piece, published research (and when), reels or shorts? It cuts research time and surfaces angles nobody has taken. He says the template later "matches your story" and that this is how research gets monetized [4:30 to 5:21].
12. **Know 4W1H and half the research is done** [5:21].
13. **Research the audience.** For every video his team first studies retention: what this audience likes to watch, read from competitors' videos [5:26 to 5:38].
14. **Check demand with keywords.** vidIQ gives AI topic ideas for your channel and a keyword tool with search volume. He jokes about drifting into SEO, then justifies it: these tools show whether the research is useful to people [5:38 to 6:12].
15. **Harvest the questions people actually ask.** AlsoAsked and AnswerThePublic, both run on "Project Cheetah"; the output becomes his research question list [6:12 to 7:01].
16. **Upgrade to primary data when you can.** Everything so far is secondary data; first-hand data makes research "10 to 100 times" more valuable. Models: Hindenburg (spends most on primary research), Vox (mixes primary with secondary), Monkey Magic (documentaries that look like vlogs) [7:01 to 8:07].
17. **Build field knowledge.** Knowing the field cuts research time and improves quality [8:07 to 8:17].
18. **Monetize research.** (a) Sell research as data (firms only, Hindenburg again), (b) content: video, audio, blogs, and above all paid newsletters (Creator Hooks as the example), (c) publish books, (d) run your own research firm (Ram Setu film clip) [8:17 to 10:04].
19. **Add storytelling.** It is the skill that turns research into money; he closes by calling back the opening list of formats [10:04 to 10:23].

### 2. Tools and sources named

| Tool or source | What he uses it for | Note |
|---|---|---|
| Google search, first results page | Basics: dates, numbers, reasons | Orientation only (see section 5) |
| News articles and a journal paper, highlighted on screen (visual pass: ThePrint, Deccan Herald, The New York Times, a Scientific Reports paper) | Cheetah history | He shows the exact supporting line highlighted, a good habit |
| Jenni AI | Paste article links and get bullet-point summaries | "If you don't want to read" (see section 5) |
| vidIQ | AI topic ideas for your channel; keyword tool with search volume and competition | Demand research, not fact research |
| AlsoAsked | Branching tree of "People also ask" questions for a keyword | Visual pass: region set to India, 3 free searches a day |
| AnswerThePublic | The most-asked questions around a keyword | 3 free searches a day, renews daily |
| Competitors' videos; YouTube Studio audience data (visual pass) | What this audience watches and keeps watching | |
| Dhruv Rathee, Project Cheetah video | Worked example for every research step | |
| Hindenburg Research | Example of primary research and of selling research | Business model described wrongly (section 5) |
| Vox | Example of combining primary and secondary research | |
| Monkey Magic (YouTube channel) | Documentary content in vlog form | |
| Creator Hooks | Example of a paid newsletter (titles, thumbnails, hooks) | Revenue claim unsourced |
| Ram Setu (film) | Clip for the "own research firm" idea | |

### 3. Rules and heuristics worth turning into checks

- **Basics before angle:** no angle work until the topic's dates, numbers, actors and stated reasons are logged.
- **Question chaining:** every heading is rewritten as a question; every answer produces at least one follow-up question; keep the chain as heading, sub-heading, sub-sub-heading.
- **Question count floor:** he gets six questions from one minute of chaining. Our suggestion: at least 12 logged questions for a 10-minute video before searching.
- **Depth is a decision:** record the planned depth per branch; stop when the video's need is met, not when the internet runs out.
- **Prior-coverage scan is mandatory:** videos, documentaries, books and e-books, journalism, published research with dates, reels and shorts. Output: what exists, what is missing, our angle.
- **Demand check:** collect real audience questions (People Also Ask tools) and search volume before committing to a topic.
- **Tag data type:** mark each fact primary or secondary; aim for at least one piece of primary material per video when the budget allows.
- **Construction rules from his own video:** open a loop in the first 30 s and close it later; end on a bookend that calls back the opening.
- **Negative rule (from his mistake):** a numbered promise in the hook ("four things") must be delivered and visibly counted.

### 4. How the video itself is built

- **Format.** Presenter on camera with a lapel mic, keyed over grid backgrounds with B-roll layered behind and around him. Measured 197 shots, about 3.3 s per shot: the fastest of the three.
- **First 30 seconds.**
  - [0:00 to 0:16] A spoken list with a matching montage (visual pass: streaming interface, creator thumbnails, a reel, a chalkboard, a cricket broadcast, the Money Heist "Professor"), ending on the "four things" promise and a cinematic sound sting [0:12].
  - A one-second channel logo [0:16].
  - [0:16 to 0:31] The relative thought experiment, visualised (visual pass) with cutout figures that gain a degree, a tie and then a wedding turban: studies, job, marriage, the classic interrogation. An audience-groan sound lands on "what's your salary" [0:26]. Then the open loop: remember these 20 seconds.
- **Promise.** Research method, modern tools and monetization (title), plus four pre-research rules that are never counted.
- **Structure.**

| Time | Section |
|---|---|
| [0:00] | Hook montage and promise |
| [0:16] | Thought experiment, open loop |
| [0:31] | Where ideas come from (shower) |
| [1:08] | Two examples announced: Dhruv's Project Cheetah and "our own" |
| [1:20] | Dhruv clip 1, then basics first and 4W1H |
| [2:19] | Dhruv clip 2, then question chaining |
| [3:39] | Six questions in a minute; going deeper |
| [4:03] | Dhruv clip 3: reasons become questions |
| [4:19] | Callback to the 20 seconds; the 80 percent claim |
| [4:30] | Prior-coverage template |
| [5:26] | His own routine: audience, competitors, vidIQ |
| [6:12] | Audience questions: AlsoAsked, AnswerThePublic |
| [7:01] | Primary data (Hindenburg, Vox, Monkey Magic); field knowledge |
| [8:17] | Four ways to monetize research |
| [10:04] | Storytelling; bookend |
| [10:23] | End screen |

- **Time budget.** Hook and idea 1:08; research method 4:18; tools 1:35; primary data and knowledge 1:16; monetization 1:47; ending 0:47.
- **Open loops and payoffs.** (1) "Remember these 20 seconds" [0:28], paid at [4:19], but the lesson stays implicit. (2) "The template will match your story; we'll see how" [5:14], paid only loosely at [10:04]. (3) "Research is confusing, but watch to the end and it will be clear" [3:30], a generic retention line. (4) The opening list of formats, paid as a bookend [10:16] with a quick visual recap (visual pass). (5) "Four things" [0:00], never paid.
- **Teaching device.** Clip first, rule second: each Dhruv clip shows the move, then he names the method behind it. One case study threads the whole video; even the tool demos run on the same keyword.
- **Pattern interrupts.** A sound effect every 20 to 60 s (boom, groan, chimes, whooshes); a meme insert that completes his 4W1H list for him and jokes that viewers are fed up with all the questions [2:07]; a self-aside ("weren't we talking about research, where did SEO come from?") with a record scratch [6:00]; an off-screen voice cutting him off ("easy, bro") with a record stop when he rattles off YouTube hacks [9:34]; film clips (Ram Setu [9:56]); on-screen question cards that build up as he speaks.
- **Ending and call to action.** Storytelling as the final multiplier, a recap montage (visual pass), then two end-screen videos, one baited with "how 15-year-olds are becoming crorepatis" [10:31], and his sign-off.

### 5. Weak or questionable advice

1. **The shower science does not hold up, and his own citation shows it.** He says water drops make the brain "blink" for 1 to 4 seconds and calls it scientifically proven [0:52]. The card he flashes on screen [0:59] summarises a Vanderbilt finding that the brain "blinks" (brief unconscious gaps in visual perception) when attention shifts. That finding is about visual attention. It says nothing about water, a 1 to 4 second window, or subconscious insight. There is real research on incubation and mind-wandering, but it does not describe this mechanism. **Lesson for our fact-check:** "a source exists" is not enough; the source must say what the sentence says.
2. **"80 percent is on the first page"** [4:21] is an unsourced number. First-page results favour SEO-optimised and aggregator pages; primary documents (gazettes, datasets, papers, court records) often sit deeper. Use the first page to get oriented, never as the source of record.
3. **"Don't want to read? Paste links into Jenni AI"** [2:57]. Summaries drop caveats, numbers and dates. Anything that goes into a script must be read in the source. V1.2 says the opposite, and V1.2 is right.
4. **Demand research is mixed into fact research.** vidIQ volume and competitor retention answer "will people watch?", not "is it true?". Both matter; keep them as separate steps with separate outputs.
5. **Hindenburg is the wrong example for selling research.** Hindenburg Research was an activist short seller that made money from positions against the companies it exposed, not by selling reports to media companies; it shut down in January 2025. The "after 2017, research moved into content" line is never explained.
6. **Unsourced numbers throughout:** India "number one in online reading", Creator Hooks making "millions of dollars", primary data "10 to 100 times" more valuable. A research tutorial that states numbers without sources teaches the wrong habit.
7. **Unpaid promise.** The "four things" are never delivered as four.
8. **Primary research is praised, not taught.** No word on interviews, surveys, datasets, consent or cost. The monetization routes (sell data, found a firm) are out of reach for the beginners he addresses.

---

## V1.2 DecodingYT: "How to Research and Script Any Topic for YouTube (STEP BY STEP)" (`q2bOMglypxg`, 10:49)

Timestamps from [1:03] to [5:05] use the corrected timing (see the note at the top).

### 1. What it teaches, step by step

1. **Know your starting state.** You have a topic, but you are either flooded with points or blank [0:45 to 1:03].
2. **Run the Kipling method (5W1H: who, what, when, where, why, how)** to list the points to cover [1:03 to 1:24]. Worked example, "The Hidden World of Dark Web" [1:24]:
   - What: what exactly it is, how it differs from the surface web, what content is on it [1:35].
   - When: when it emerged, a timeline, when it became popular, major events [1:47].
   - Where: where it was created, where it is used most [1:59].
   - Who: who controls it, who uses it, who its victims are; everyone involved in it or affected by it [2:03].
   - Why: why it exists [2:17]. How: how it works technically [2:22].
   - On screen the questions build up line by line (visual pass) into a nine-question list.
3. **Reverse-engineer a top video with the same grid.** Dhruv Rathee's metaverse video maps to what (definition, origin of the name, uses), who (companies and founders), when (when it becomes part of daily life), where (where the idea came from), why (why it is popular), how (VR and AR), plus an impact question: how will it affect our lives, good and bad [2:40 to 3:27].
4. **Weight the Ws per topic.** "Where" matters a lot for a World War video and hardly at all for "how MrBeast became the biggest YouTuber" [3:33 to 3:54].
5. **Know a little first.** Some prior knowledge is needed to ask intelligent questions [3:54].
6. **Stuck? Ask ChatGPT to apply 5W1H to your topic.** The prompt on screen says, in effect: I'm making a YouTube video on this topic; how can I apply 5W1H to research it? [4:02 to 4:18].
7. **Find answers and verify sources** [4:18]. Google each question for articles [4:29], read the topic's Wikipedia page [4:35], related books [4:38], documentaries and interviews on YouTube [4:41].
8. **Do not take answers from ChatGPT-style chat sites; he strongly recommends against it** [4:44 to 4:53]. Two reasons: every article, study, report or interview you take in builds your own knowledge, so you research wider and with more confidence [4:53]; and reading yourself shows you points your 5W1H grid missed, which you add to the list [5:05].
9. **If you use AI, use Perplexity, because answers come with citations.** Read the cited articles for more detail and judge whether each source is reliable [5:16 to 5:42]. On screen he opens the list of five cited sources, then the cited article itself (visual pass).
10. **Check every source.** Trustworthy website and credible author [5:42]; Quora and Reddit are likely biased, therefore unreliable [5:49]; verification is always needed and is a must for medicine, science, finance, news and politics, and controversial topics [5:57 to 6:10].
11. **Use academic search.** Google Scholar for papers and studies [6:10]; Consensus, an AI search engine that answers from scientific papers, for science topics [6:20 to 6:32].
12. **Go in depth with two logics** [6:32]. Horizontal logic lists the parallel answers to a question: why do people smoke, peer pressure, stress relief, advertising [6:56 to 7:17]. Vertical logic takes one answer and keeps asking why until the root cause: peer pressure, the need to fit in, belonging as a basic human need, tribe membership mattered for protection, sharing resources and reproduction [7:17 to 7:47]. Do this for every important question; then research is complete [7:47 to 7:59].
13. **Script, step 1: a killer intro** [8:07]. There is no single format [8:11]. Three models: open with the most attention-grabbing statements from later in the video (Nitish Rajput) [8:18]; open with a shocking number (Mohak Mangal's business videos, shown opening on a big rupee-crore figure) [8:28]; open with a story that plants questions, then start answering them (Dhruv Rathee's history videos, shown with his Bhopal gas tragedy opening: a date, the railway station, two named railway officials) [8:40]. The common rule: make the viewer curious about the rest [8:54].
14. **Main content.** Answer your 5W1H points: basic questions first (Mona Lisa: who painted it, when), then the more interesting ones (why is it so valuable) [9:01 to 9:25].
15. **Relevance filter.** Go deep only where the viewer came for depth: a long detour into Leonardo's education and family loses viewers; "who is the woman in the painting?" keeps them [9:25 to 9:52].
16. **Link every point to the next** [9:52]. Never jump abruptly. End a point by raising a question the next point answers, or by saying something that contradicts the current point. On screen it becomes a flowchart (visual pass): current point, raise question, next point; or contradict current point [10:00 to 10:32]. Done well, a point-heavy video feels like a movie and the viewer never notices the technique.

### 2. Tools and sources named

| Tool or source | What it is used for | Note |
|---|---|---|
| Kipling method (5W1H) | Generating the points to cover | Named after Kipling's "six honest serving men" verse |
| ChatGPT | Generating 5W1H questions for a topic | Questions only, never answers |
| Google search | Articles for each question | |
| Wikipedia | Topic overview | Best used for its reference list |
| Books; YouTube documentaries and interviews | Depth and first-person accounts | |
| Perplexity | AI answers with citations; open the sources to read more and judge reliability | On screen: opens the list of cited sources |
| Google Scholar | Academic papers and studies | |
| Consensus | AI search engine that answers from scientific papers; for science topics | Visual pass: shows its agreement meter |
| Quora, Reddit | Named as biased and unreliable | Too blunt (section 5) |
| Dhruv Rathee, Mohak Mangal, Nitish Rajput | Models for the three intro types and for linking points | |

### 3. Rules and heuristics worth turning into checks

- **Every video starts with a 5W1H grid:** at least one question per W; each W marked high, medium or low for this topic.
- **Add an impact question** (how will it affect us?) to every grid.
- **AI writes questions, humans read sources:** an AI answer only counts once its cited source has been opened and read.
- **Source gate:** reputable site plus a credible, named author.
- **Hard-verify categories:** medicine, science, finance, news and politics, controversial topics.
- **Depth rule:** each core question gets a breadth list and at least one why-chain down to a root cause.
- **Intro rule:** the intro must create curiosity; pick one of three types (teaser, statistic, story).
- **Order rule:** basic questions before interesting ones.
- **Relevance rule:** cut any branch the viewer did not come for.
- **Transition rule:** every point ends with a question the next point answers, or with a contradiction.

### 4. How the video itself is built

- **Format.** Faceless voice-over. Motion graphics on a green grid, a 3D animated character, stock footage, big kinetic words spelling out the Hinglish narration (visual pass), creator clips, and screen recordings (Google, Perplexity, a news site, Google Scholar, Consensus). Measured 80 shots, about 8 s per shot, but the graphics inside each shot change every 1 to 3 s.
- **Signature device.** A `RESEARCH FULL GUIDE` notepad checklist (Kipling method; finding answers and verifying source; going in depth; important tools; how to script) appears with the roadmap [0:28] and returns with ticks at the section changes (visual pass: about [4:18], [6:33] and [7:45]). It works as a visible progress bar and an open loop.
- **First 30 seconds.**
  - [0:00] Cutouts of three famous creators, a view counter racing into the millions and falling cash (visual pass), with a cash-register sound: they earn lakhs from ads.
  - [0:08] The viewer's own problems as a run of questions: where do I start, what do I cover, what do I read out of everything on Google, how do I turn it into a script.
  - [0:26] "All of it is answered here", then the roadmap [0:28] and "let's begin" [0:44].
- **Promise.** Four deliverables (Kipling method, going deep, free tools, how your favourite creators script), shown as the five-item checklist. All are paid off.
- **Structure.**

| Time | Section |
|---|---|
| [0:00] | Hook: social proof and money |
| [0:08] | Pain questions |
| [0:28] | Roadmap checklist |
| [0:45] | Problem: flooded or blank |
| [1:03] | Kipling method with the dark web example |
| [2:40] | Reverse-engineering Dhruv's metaverse video |
| [3:33] | Weighting the Ws; prior knowledge; the ChatGPT prompt |
| [4:18] | Finding answers and verifying sources (Google, Wikipedia, books, interviews; not chat answers; Perplexity; source checks; must-verify categories) |
| [6:10] | Google Scholar and Consensus |
| [6:32] | Horizontal and vertical logic (smoking) |
| [7:59] | Script: the killer intro, three models |
| [9:01] | Main content: order and relevance (Mona Lisa) |
| [9:52] | "But wait": linking points |
| [10:32] | Call to action |

- **Time budget.** Hook and roadmap 0:45; question grid 3:15; answers, verification and tools 2:14; depth 1:27; scripting 2:33; call to action 0:17.
- **Open loops and payoffs.** The checklist is the main loop: five boxes, ticked in turn. At [9:52], just as the lesson seems finished, "but wait, this is not enough" (with a record scratch and the music cut) opens a final loop for the most valuable tip.
- **Pattern interrupts.** A whoosh on every section change; pop sounds as each W appears; questions building up on screen line by line; a short clip of another creator's voice introducing "two kinds of logic" [6:47]; the record scratch [9:52].
- **Examples.** Exactly one example per concept, each from a different domain: dark web, metaverse, World War versus MrBeast, smoking, Mona Lisa, the Bhopal story intro.
- **Pacing.** 60 to 90 s per concept, clear signposting, no digressions.
- **Ending and call to action.** "If you made it this far, comment 'Research is fun'" [10:32]: a completion check that also seeds comments. Then a playlist and a goodbye.
- **Irony.** The video's own intro uses the promise-and-roadmap format (right for a tutorial), not the story hook it praises.

### 5. Weak or questionable advice

1. **The Quora and Reddit rule is too blunt** [5:49]. Forums are weak evidence for facts but useful for leads, lived experience and links to primary material. And "biased" is not the same as "unreliable".
2. **The smoking breadth list misses the main factor.** Peer pressure, stress relief and advertising leave out nicotine dependence, the main reason people keep smoking. An intuitive breadth list needs checking against a domain authority and should be ranked by evidence.
3. **The why-chain ends in an unsourced evolutionary story** (tribes, protection, reproduction) presented as the root cause. Each link in a chain needs its own evidence, or the "root cause" is a guess. The chain has also drifted away from the video's topic.
4. **The Mona Lisa question has a shaky premise.** The painting has never been sold. Its "most expensive" status rests on a record insurance valuation (1962); the highest price actually paid for a painting went to another Leonardo work, Salvator Mundi (2017). Every grid question needs a premise check.
5. **Cited AI is treated as safe.** Perplexity citations can point to pages that do not say what the answer says, and Consensus's agreement meter flattens study quality. Open, read, and match each claim to its source.
6. **Verification stops at reputation.** No cross-checking between independent sources, no tracing to the original document, no dates or recency, no number hygiene.
7. **"Every YouTuber you watch uses this method"** [2:35] is an overclaim.
8. **Scripting is thin.** Intro, order and transitions only: nothing on endings, showing evidence on screen, or fact density.

---

## V1.3 Tube Sensei: "How to Research Like @dhruvrathee | Script Like Dhruv Rathee" (`7hdwmTagRSk`, 10:47)

### 1. What it teaches, step by step

1. **Interest and background first.** Work in a field you care about. Dhruv has made political and social videos for about a decade, so he can talk for an hour on a topic and tie it to past events. Without that background, method has to make up for it [0:24 to 0:59].
2. **Classify the video before researching** [0:59]:
   - A **What topic** is current news: what is happening, how people react, where leaders stand, what could happen next (Dhruv's Gaza crisis video) [1:08].
   - A **Why topic** covers history and context, an explainer: what the conflict is, why, when it began, what is happening now (Dhruv's Israel-Palestine explainer) [1:22 to 1:36].
   - He adds that What videos can steer viewers toward your view, while neutral Why videos let viewers form their own [1:36] (see section 5).
3. **Pick the research pattern from the class** [1:50]:
   - What topic, **horizontal logic**: move through the sequence, event one, event two, event three [2:01].
   - Why topic, **vertical logic**: drill into one event, its reason, that reason's reason, and so on, "जब तक आप पॉइंट ज़ीरो पे ना पहुँच जाओ" ("until you reach point zero") [2:09].
   - Or mix both to explain a concept [2:17]. On screen: a chain labelled `REASON 1, REASON 2, REASON 3, SO ON, POINT 0`.
4. **Fill the content with 4W1H at every node:** what, when, where, why, how (his list has no "who") [2:25 to 3:06]. Dhruv does not know everything, but runs every topic through this and puts the data in sequence, so the video explains itself [2:48].
5. **Know your data type.** Primary data you collect yourself (surveys); secondary data comes from news, books and documents. Vox leans on primary, Dhruv on secondary [3:06 to 3:31].
6. **Track news daily.** Google News, Dainik Jagran, Economic Times, Mint; he says most of Dhruv's data comes from sites like these [3:31 to 3:43].
7. **Read widely and go to the origin.** Search the topic, read as many top articles as possible, and follow each one to its original source [3:43 to 3:56].
8. **Because many outlets are compromised, add primary data.** Reach people where the story is happening through social media and collect their accounts [3:56 to 4:17]; he pitches this as the one gap where a small creator can beat Dhruv [4:17 to 4:28].
9. **Hook within the first 15 seconds, with a story or a question** [4:51 to 6:01]. Examples played in full: Dhruv's Mona Lisa theft opening (a Monday morning in Paris, 21 August 1911, three men walk out of the Louvre) and a riddle-style Ramayana opening that gives only the letters of the names. Both leave the viewer "in a state of question". He supports the 15-second window with a YouTube Creator Playbook post shown on screen, dated 2011 [5:45].
10. **No preview after the hook.** Some creators announce what the viewer will learn (he names Nitish Rajput and Abhi and Niyu). Dhruv goes straight into content, so the viewer has no time to drift [6:02 to 6:19].
11. **Body pattern: past, then present, then the question.** Tell the background story (history), jump straight to the current situation, skip the middle. Viewers now ask themselves how it got from there to here, and the video answers with 4W1H and both logics [6:19 to 6:54]. On screen: `BG STORY | CURRENT SITUATION`.
12. **The twist.** When viewers feel they understand everything, show something that contradicts it (an opposition leader's tweet, a clip). Curiosity comes back. Then re-explain, covering the opposing side with the same logics [6:54 to 7:21].
13. **Ending: an opinion that doesn't simply pick a side.** Viewers stay to the end to learn where the creator stands; Dhruv closes like a diplomat (the Israel-Palestine video ends with him on the side of humanity), which keeps his reputation for being unbiased [7:21 to 7:59].
14. **Demo: "Why China is Dangerous"** [7:59 to 10:05]:
    - Hook: a stack of five questions over strong visuals: was COVID an accident, what if China becomes a superpower, why does China influence Canada's elections, why does China help Pakistan, is China playing a long game [8:14 to 8:31].
    - Background by contrast: China in 1983 (poor, farming, famine) against China today (largest economy, skyline, nobody picks a fight), ending on "what happened between 1983 and 2023?" [8:31 to 9:03].
    - Horizontal chapters: rise of Mao (when, why, what happened, how it turned out), then after Mao's death the rise of Xi Jinping, and so on until every reason for the growth is covered [9:03 to 9:41].
    - Play the card: flip from growth to danger, against everything shown so far, then continue with both logics. On screen the danger splits into four pillars: economic dominance, military power, human rights, technology, each with what, when, where, why, how [9:41 to 9:55].
    - End with future possibilities rather than your own opinion, because a small channel's opinion carries no weight yet [9:55 to 10:05].

### 2. Tools and sources named

| Tool or source | What it is used for | Note |
|---|---|---|
| 4W1H (what, when, where, why, how) | Content checklist at every node | No "who" |
| Horizontal and vertical logic | Research patterns (sequence; reason chain to point zero) | Different meaning of "horizontal" from V1.2 |
| Google News, Dainik Jagran, Economic Times, Mint | Daily news tracking | Indian sources; Bangladesh equivalents in the synthesis |
| Google search: top articles and their original sources | Building a solid fact base | |
| Surveys; social media contacts | Primary data | Representativeness and safety issues (section 5) |
| Vox; Dhruv Rathee | Models of primary and secondary research | |
| YouTube Creator Playbook post on the first 15 seconds (2011, on screen) | Support for the 15-second hook window | Old; use your own retention graph |
| Dhruv Rathee videos: Gaza crisis, Israel-Palestine explainer, Mona Lisa and Ramayana openings | Case studies | Visual pass: his clips show news headlines with the key line highlighted |

### 3. Rules and heuristics worth turning into checks

- **Classify first:** every video is labelled What (news) or Why (explainer) before research; the label picks the research pattern and the outline.
- **Point-zero rule:** in a Why video, every causal chain continues until a documented origin, not until the researcher gets tired.
- **4W1H at every node** of the sequence or chain.
- **Origin rule:** every article used is traced to its original source.
- **Hook rule:** the first 15 seconds carry a story or a question.
- **Preview rule:** no "in this video you will learn" for story explainers.
- **Body rule:** past, jump to present, "how did we get here?", then answer.
- **Twist rule:** once the main explanation is done, bring in credible counter-evidence, then give the opposing view the same rigour.
- **Ending rule:** a balanced judgement, or future scenarios; new channels should prefer scenarios.

### 4. How the video itself is built

- **Format.** Faceless voice-over with an anime-style avatar at a neon desk, stock B-roll, many Dhruv Rathee clips (two of his cold opens played in full), news screenshots, and diagrams: `WHAT / WHY`, the event chain, the reason chain to `POINT 0`, the 4W1H list, `BG STORY | CURRENT SITUATION`, a notepad script page and tree diagrams. There is also a `YOU` versus `DHRUV` standoff meme [4:18]. Measured 90 shots, about 7 s per shot, with animated graphics in between.
- **First 30 seconds.**
  - Authority [0:00]: Dhruv got into TIME because of his research (the graphic shows a TIME article about him using YouTube to fact-check Indian media), and he is the biggest influencer on YouTube because of his scripts.
  - Pain [0:07]: you run the same kind of channel and can't grow, because your script and research are weak (visual pass: thumbs-down and crumpled-paper shots).
  - Promise [0:14]: how he researches, how he knows every news story, how he writes scripts that people finish at 20 to 25 minutes.
  - The prerequisite (interest) starts at [0:24].
- **Promise.** A three-part promise, plus a second promise at [4:42] to build the pattern on a fresh topic (paid at [7:59]).
- **Structure.**

| Time | Section |
|---|---|
| [0:00] | Hook: authority, pain, promise |
| [0:24] | Interest and knowledge |
| [0:59] | What versus Why topics |
| [1:50] | Horizontal versus vertical logic |
| [2:25] | 4W1H |
| [3:06] | Primary versus secondary data, news sources, original sources, primary data via social media |
| [4:28] | Script pattern announced ("I watched 100+ Dhruv videos") |
| [4:51] | Intro and hook: Dhruv's openings, the 15-second window |
| [6:02] | No preview |
| [6:19] | Background, present, question |
| [6:54] | Twist: contradictory evidence |
| [7:21] | Diplomatic ending |
| [7:59] | Demo: "Why China is Dangerous" |
| [10:05] | Summary diagram, series wrap, call to action |

- **Time budget.** Hook 0:24; interest 0:35; research 3:29; script pattern 3:31; demo 2:06; wrap 0:42.
- **Open loops and payoffs.** "I'll show the pattern, then build it on a new topic" [4:42], paid at [7:59]. "This is how you beat Dhruv" [4:17] is an aspiration loop. He also describes Dhruv's ending as a loop: viewers wait to learn his side.
- **Teaching device.** Pattern first, then transfer to a fresh topic. It is the strongest teaching move of the three, although the demo's content is wrong (section 5).
- **Pattern interrupts.** Dhruv's cold opens with a switch to suspense music [5:00]; typing sounds as 4W1H appears [2:32]; the standoff meme; big title cards (visual pass: `HOOK`, `INTRO`, `PROMPT`).
- **Ending and call to action.** A one-screen summary diagram (research branches into What topic with horizontal logic and Why topic with vertical logic, 4W1H under both) [10:05]; the end of his series; a request for 1,000 comments before he starts a new series [10:20]; a pointer to his SEO video [10:33].

### 5. Weak or questionable advice

1. **"What (news) videos can push viewers to one side"** [1:36]. Blending facts with steering in news coverage is a trust and ethics problem, and it contradicts his own praise of Dhruv's balanced ending. Our rule: separate what happened from interpretation, label opinion, present each side's strongest case.
2. **Neutrality presented as a tactic.** He frames Dhruv's balanced ending as a way to protect status and to "influence the whole audience". Balance should come from the evidence, not be performed.
3. **4W1H without "who".** In news and politics, the actors (who decided, who gains, who is hurt) are often the heart of the story.
4. **Claims about Dhruv's process are inferred, not sourced:** which sites he reads, that he never uses primary data, that 100 videos follow one pattern. Treat them as a hypothesis from watching the output.
5. **"Primary data is easy through social media."** Messages and comments are self-selected, hard to verify, and in conflict zones can put people at risk. Disclose sample and method, verify identity, get consent. "The one loophole to beat Dhruv" overpromises.
6. **"Media houses are sold, so prefer primary data."** The better fix is triangulation across outlets with different leanings, plus primary documents. First-hand data is not automatically truer.
7. **The China demo is a cautionary example: a good structure filled with wrong facts.**
   - It places over a million hunger deaths in the 1983 background. China's great famine was 1959 to 1961 and killed tens of millions by most estimates, two decades earlier.
   - "World's largest economy" is true only by purchasing-power parity; by nominal GDP the US is larger.
   - "The world industrialised while China only farmed" ignores Mao-era heavy industry and the market reforms that began in 1978.
   - The sequence goes 1983, then the rise of Mao (in power from 1949), then straight from Mao to Xi Jinping. It skips Deng Xiaoping and the reform era that actually explains the growth. The "horizontal" chronology breaks its own order.
   - "60% poverty in 1983" has no source and no poverty line; estimates for that period vary enormously by definition.
   - The hook questions presuppose contested or specific claims: the origin of COVID is unresolved, and interference in Canada's elections was examined by a public inquiry whose findings should be cited, not hinted at. The danger is also framed from India's side ("helping Pakistan").
   - Lesson: the template does not make the content true. Every number and date in the hook and background needs a ledger entry.
8. **The 15-second rule rests on a 2011 blog post** [5:45]. Still sensible, but the channel's own retention graph should set the window.
9. **Overclaims in his own hook.** The TIME point is vague rather than false: the graphic shows an undated TIME article about Dhruv's fact-checking, not an award or a list. "Biggest influencer on YouTube" is an unsourced superlative. He also promises a "prompt" but shows an outline.

---

## Synthesis for our skills

### If we adopt only ten things

1. **Classify first.** Every video is What (news), Why (explainer) or How-to (tutorial) before any research. The class sets the research mode and the outline. (V1.3)
2. **Build a question grid:** who, what, when, where, why, how, plus impact and what-next. Chain every answer into the next question, weight each W for the topic, and premise-check every question. (V1.2, V1.1, our additions)
3. **Scan prior coverage and demand before researching:** existing videos, documentaries, books, journalism, papers and shorts, plus the questions people actually search. (V1.1)
4. **AI writes questions; people read sources.** An AI answer counts only once its citation has been opened and the claim found in it. (V1.2)
5. **Trace every claim to its origin and keep a claim ledger** with the supporting excerpt. Check that the source says what the script says. (V1.2, V1.3; V1.1's citation card shows why)
6. **Map depth three ways:** sequence (timeline), breadth (parallel factors ranked by evidence), chains (why after why, to a documented point zero). (V1.2, V1.3)
7. **Collect counter-evidence during research.** It powers the mid-video twist and keeps the video fair. (V1.3)
8. **Hook within 15 seconds** with a story, question stack, number or teaser. Explainers skip the preview; tutorials show a roadmap and tick it off. (V1.2, V1.3)
9. **End every chapter with a hand-off,** a question the next chapter answers or a contradiction. (V1.2, V1.3)
10. **End on evidence:** a balanced judgement or future scenarios, with opinion labelled. New channels should lean on scenarios. (V1.3)

### The shared research-to-script workflow

1. **Topic and type.** Pick the topic, classify it (What, Why, How-to), and check demand: audience questions, search volume, how competitors' videos hold viewers. (V1.3; V1.1)
2. **Coverage and gap.** List what already exists and find the angle nobody has taken. (V1.1)
3. **Question grid.** 5W1H plus impact, chained into sub-questions, weighted per topic. (V1.2; V1.1)
4. **Basics.** First-page results, Wikipedia, news sites, a first timeline. (All three)
5. **Answers from real sources.** Read them yourself and trace each to the original; use AI only through citations. (V1.2; V1.3)
6. **Verification.** Site and author credibility, extra care for high-risk categories, triangulation against media bias. (V1.2; V1.3)
7. **Depth.** Sequence, breadth, why-chains to point zero. (V1.2; V1.3; V1.1)
8. **Primary material** where possible. (V1.1; V1.3)
9. **Ordering.** Basics first, then the interesting questions; cut what the viewer didn't come for. (V1.2)
10. **Script.** Hook, background, present, the natural question, answer chapters with hand-offs, twist, balanced ending, with storytelling throughout. (V1.3; V1.2; V1.1)

### Where they differ

| Aspect | V1.1 HimanshuG | V1.2 DecodingYT | V1.3 Tube Sensei |
|---|---|---|---|
| Question formula | "4W1H": spoken why, when, where, how, for-what; card shows Why, When, Where, Who, How; examples start with what | 5W1H: who, what, when, where, why, how, plus an impact question | 4W1H: what, when, where, why, how (no who) |
| Going deep | Chain questions to the depth you need | Horizontal = parallel reasons (breadth); vertical = why-chain to root cause | Horizontal = event sequence; vertical = reason chain to point zero; What topics go horizontal, Why topics go vertical |
| Where facts come from | First results page, prior coverage, question tools; primary data praised | Google, Wikipedia, books, documentaries and interviews; Perplexity, Scholar, Consensus | News sites; top Google articles traced to their originals; primary data through social media |
| Stance on AI | Link summaries fine (Jenni AI); AI topic ideas (vidIQ) | Questions yes, answers no unless cited (Perplexity) | Not discussed ("prompt" means outline) |
| Verification | Not taught | Site and author credibility; must-verify categories; forums unreliable | Trace to the original; distrust compromised media; add primary data |
| Hook | Own video: relatable list plus a thought experiment | Teaser, statistic or story; must spark curiosity | Story or question in the first 15 s; no preview |
| Body | Not taught (storytelling mentioned) | Basics first; relevance cut; hand-offs by question or contradiction | Past, present, question, answer; twist with counter-evidence; re-explain |
| Ending | Storytelling as the multiplier | Not taught | Diplomatic opinion (big channels) or scenarios (small channels) |
| Demand research | Yes: vidIQ, AlsoAsked, AnswerThePublic, competitors | No | No |
| The video's own form | Face on camera, 3.3 s shots | Faceless motion graphics, progress checklist | Faceless avatar, diagrams, borrowed clips |

**The terminology clash matters.** "Horizontal logic" means breadth (parallel factors) in V1.2 and sequence (a timeline of events) in V1.3. Our skills should drop the word and use three explicit modes: **sequence**, **breadth** and **chain**.

### What none of them covers (our skills must add)

- **Number hygiene:** units, base year, definition (which poverty line?), nominal versus PPP, totals versus per capita, currency conversion (1 million = 10 lakh; 1 billion = 100 crore).
- **Dates and recency:** when each source was published, whether it still holds, and an "as of" date in the script for anything that changes.
- **Claim-to-source matching:** the excerpt has to state the claim, not just sit near it.
- **Independent corroboration:** two independent sources for key claims, and the original rather than the aggregator.
- **A deliberate counter-evidence search** (V1.3's twist needs it, but nobody says where it comes from).
- **Legal risk** (defamation, accusations against named people or institutions) and privacy for private individuals.
- **Visual rights.** All three lean on film, TV and other creators' clips; Content ID claims and copyright are real risks.
- **Labelling dramatized footage.** Dhruv's Bhopal reconstruction carries a small "representational" label on screen; we should do the same.
- **Audience-relative stakes:** "dangerous for whom?", "why does this matter to a viewer here?"
- **Showing and publishing sources:** highlighted headlines and documents on screen for key claims, and a source list in the description.

### Research skill: steps to adopt

1. **R0 Brief.** Topic; type (What, Why, How-to); audience (country, language mix, prior knowledge); the viewer's question; the promise; the stakes for this audience; target length.
2. **R1 Demand and coverage.** People-also-ask questions and autocomplete in English, Bangla script and Banglish; competitor videos (angle, length, date, questions in their comments); the coverage template; a one-line gap statement.
3. **R2 Question grid.** Who, what, when, where, why, how, impact, what-next. AI may draft it. Weight each W, chain each answer into follow-ups, and premise-check every question.
4. **R3 Orientation.** First-page results, Wikipedia and its references, a first timeline, a list of key actors.
5. **R4 Sources per question.** Read them. Trace each to the original. Log type (primary, secondary, tertiary), publisher, author, date and leaning. Get two independent sources for key claims.
6. **R5 Depth map.** Sequence (dated events), breadth (factors ranked by evidence), chains (each link sourced, ending at a documented point zero or marked "hypothesis"). What videos need sequence, reactions, stakes and scenarios; Why videos need all three modes.
7. **R6 Counter-evidence.** The strongest opposing claim and its best sources.
8. **R7 Primary material,** cheapest first: official statistics and datasets, documents (gazettes, court orders, right-to-information replies), expert interviews, on-ground interviews, surveys with the method disclosed.
9. **R8 Claim ledger freeze.** Every claim with its excerpt, confidence, "as of" date and flags.
10. **R9 Handoff to the script.** Questions ordered basics first; a relevance cut list; key numbers; the counterpoint; what we could not verify.

### Research skill: checks

| ID | Check | Pass condition |
|---|---|---|
| RC-01 | Grid coverage | Every W, plus impact and what-next, has at least one question or an explicit "not relevant" note |
| RC-02 | Premise | No question assumes something unverified or false |
| RC-03 | Claim-source match | Every claim has an excerpt from its source that states it |
| RC-04 | Corroboration | Numbers, accusations and causal claims have two independent sources or a primary document |
| RC-05 | Origin | Aggregator and news citations are traced to the original report or data where one exists |
| RC-06 | Forum and AI | Reddit, Quora, Facebook or X posts and AI answers are never the only source for a fact |
| RC-07 | High-risk categories | Medicine, science, finance, law, elections and politics, religion, communal and cross-border topics have a primary or expert source plus a second source |
| RC-08 | Numbers | Each number has unit, date, place, definition and source; conversions are recomputed |
| RC-09 | Red-flag words | "Scientifically proven", "biggest", "first", "only", "everyone", round percentages: each needs a qualifier and a source, or is cut |
| RC-10 | Chronology | Timeline in order; key actors and turning points present (checked against two overviews) |
| RC-11 | Chains | Every link in a why-chain is sourced; a speculative end is labelled "hypothesis" |
| RC-12 | Breadth | At least three parallel factors, ranked by evidence, including the main factor named by the domain authority |
| RC-13 | Recency | Time-sensitive facts carry an "as of" date; old sources on fast-moving topics are flagged |
| RC-14 | Counterview | Contested topics have the strongest opposing case with sources |
| RC-15 | Stakes | "Why this matters to a viewer in [country]" is answered with evidence |

### Script skill: steps to adopt

1. **S1 Pick the outline from the type:** Why explainer, What news, How-to tutorial, or research story (one running case).
2. **S2 Hook (0 to 15 s).** Story cold open, question stack, sourced number, teaser, or withheld-name riddle. It must carry stakes and a curiosity gap. Every fact in it must have a ledger ID.
3. **S3 Promise.** Explainers go straight into content; tutorials show a roadmap and tick it off on screen.
4. **S4 Background, jump to the present, then the natural question** "how did we get here?"
5. **S5 Chapters.** One grid question each, basics before the interesting ones, relevance cut applied, each ending on a hand-off.
6. **S6 Twist at about two-thirds:** real counter-evidence, then a fair re-examination.
7. **S7 Ending:** what the evidence supports, then a balanced judgement or scenarios; a call to action tied to the topic.
8. **S8 Visual proof plan:** a highlighted headline or document for each key claim; dramatized footage labelled.
9. **S9 Loop ledger:** every loop opened and every promise made is listed with the time it opens and the time it closes.

### Script skill: checks

| ID | Check | Pass condition |
|---|---|---|
| SC-01 | Hook timing | Story, question or number plus stakes within 15 s (about 35 to 45 spoken words) |
| SC-02 | No warm-up | Greeting or channel sting under 2 s before the hook |
| SC-03 | Preview by format | No preview in story explainers; a roadmap in tutorials |
| SC-04 | Hand-offs | Every chapter ends with a question, contradiction or callback; no abrupt switches |
| SC-05 | Promises | Every item promised in the intro is delivered and, if numbered, counted on screen |
| SC-06 | Loops | Every open loop is closed by the end |
| SC-07 | Counterpoint | Contested topics include an opposing section built on sources of similar quality |
| SC-08 | Opinion | Opinion is labelled; facts and interpretation are separated in news videos |
| SC-09 | Relevance | No tangent over about 20 s that doesn't serve the viewer's question |
| SC-10 | Ledger coverage | Every factual sentence maps to a claim ID |
| SC-11 | Loaded questions | Hook questions don't presuppose unproven claims, or are answered with evidence in the video |
| SC-12 | Interrupt density | A visual or audio change every 3 to 8 s in fast formats (V1.1 cuts every 3.3 s; V1.2 and V1.3 every 7 to 8 s, with motion graphics in between) |
| SC-13 | Call to action | Tied to the video's content (V1.2's comment keyword is the model) |

### Templates

**A. Research brief**

```
TOPIC:
TYPE: What (news) | Why (explainer) | How-to (tutorial)
AUDIENCE: country, language mix, what they already know
VIEWER QUESTION (why they click):
PROMISE (what they can explain after watching):
STAKES FOR THIS AUDIENCE:
LENGTH TARGET:
```

**B. Question grid (AI may draft it; a person checks the premises)**

```
| # | W | Question | Weight H/M/L | Premise OK? | Mode: sequence / breadth / chain | Status |
W = who, what, when, where, why, how, impact (so what), next (what could happen)
```

Prompt to draft it (our wording): "I am researching a [length]-minute [type] video for [audience] on [topic]. List research questions under who, what, when, where, why, how, impact and what-next. Mark how much each matters for this topic, and flag any question that assumes something that may be false."

**C. Coverage scan (from V1.1)**

```
EXISTS: top videos (views, date, angle) | documentaries | books and e-books |
        journalism (investigations, explainers) | papers and reports (date) | shorts and reels
GAP: unanswered questions | outdated coverage | voices not heard
OUR ANGLE:
```

**D. Claim ledger row**

```
ID | claim as it will be spoken | number, unit, date, place | source 1 (title, publisher,
author, date, URL, type) | supporting excerpt | source 2 (independent) | confidence |
as-of date | script section | flags
```

**E. Depth map**

```
CORE QUESTION:
SEQUENCE: date | event | source
BREADTH: factor | evidence strength | source   (ranked)
CHAIN: claim | because | source  ...until point zero (or labelled hypothesis)
COUNTER: strongest opposing claim | source
```

**F. Why explainer outline (the Dhruv pattern as V1.2 and V1.3 describe it)**

```
0:00  Hook, 15 s max: story cold open (date, place, named people) or question stack
      (no preview)
      Background: the past
      Jump: the present situation, as a contrast
      The natural question: how did we get from there to here?
      Chapters 1..n: one grid question each, basics first; each ends on a hand-off
~2/3  Twist: the strongest counter-evidence, fairly presented
      Re-examination with the counterpoint
      Ending: what the evidence supports, then a balanced judgement or scenarios
      Call to action tied to the topic
```

**G. What (news) outline**

```
Hook: the newest development and why it matters here
What happened: dated sequence
Who is involved: actors and their stated positions, sourced
Reactions: people, leaders, each side
What we don't know yet
What could happen next: scenarios with conditions
As-of line
```

**H. How-to tutorial outline (the V1.2 pattern)**

```
Hook: the aspiration, then the viewer's exact problems as questions
Roadmap checklist on screen, ticked at every section
Each step: rule, one example, common mistake
"But wait": the non-obvious final tip
Completion call to action: a comment keyword tied to the lesson
```

**I. Hook bank**

```
1 Story cold open: [date], [place], [named person] does [something unexpected]; cut before the outcome
2 Question stack: 3 to 5 questions, each answered in the video, none loaded
3 Number: one sourced figure, plus a comparison that makes it felt
4 Teaser: the 1 to 3 strongest lines from later in the video
5 Riddle: withhold a well-known name (initials only) until the reveal
Rule: stakes plus a curiosity gap inside 15 s
```

**J. Transition bank**

```
Question hand-off: end the chapter on the question the next chapter answers
Contradiction: "but", then a sourced fact that complicates what was just said
Callback: return to the opening image or an open loop
Sequence: "then", with a date
```

### South Asian audience notes that matter for Bangladesh

- **Code-mixed speech is normal.** All three videos are Hinglish: English terms inside Hindi sentences, and V1.2 even flashes Romanised Hindi words on screen. Bangladeshi explainer audiences accept the same Bangla and English mix. Keep English technical terms, and decide per channel whether on-screen text is Bangla script or English.
- **Shared cultural hooks.** The nosy-relative interrogation (studies, job, salary, marriage) lands just as well in Bangladesh. Bollywood films and Indian TV memes are widely recognised there too, but Bangladeshi references land closer to home and avoid an India-centred frame.
- **Lakh and crore.** These videos count money in lakh and crore, as Bangladeshi viewers do. Convert international figures carefully (1 million = 10 lakh; 1 billion = 100 crore), give the BDT figure, and check the conversion (RC-08).
- **Media distrust is high in both countries.** V1.3's "sold media" remark reflects a real audience belief. Answer it with transparency: show headlines and documents on screen, triangulate across outlets with different leanings, and publish sources. Bangladeshi equivalents of V1.3's news list:
  - Newspapers: Prothom Alo, The Daily Star, bdnews24.com, Dhaka Tribune, and the state agency BSS.
  - Official data: Bangladesh Bureau of Statistics, Bangladesh Bank, ministries, the Election Commission, gazettes and the laws database.
  - International Bangla services: BBC Bangla, DW Bangla.
  - Fact-checkers: Rumor Scanner, Dismislab, FactWatch.
- **Primary data routes.** Bangladesh's Right to Information Act 2009 allows document requests. Facebook, the dominant platform, is useful for finding people and leads, but anything collected there is self-selected (see V1.3's section 5).
- **Demand tools are thin in Bangla.** AlsoAsked and AnswerThePublic draw on Google's question data, which is sparse for Bangla queries. Run each query in English, Bangla script and Banglish, and add YouTube autocomplete plus the comments on Bangladeshi channels and pages.
- **Sensitive areas need the high-risk gate (RC-07) and neutral framing:** religion, communal issues, India-Bangladesh relations, elections, and 1971 history. V1.3's Ramayana riddle opening works for a Hindu-majority Indian audience; religious references need more care for a mixed Bangladeshi audience.
- **Legal exposure.** Online speech laws have changed several times (Digital Security Act 2018, Cyber Security Act 2023, further changes after 2024). Check the current law before making accusatory claims about named people or institutions.
- **Re-ground the stakes.** V1.3's China demo is written from India's security frame ("helping Pakistan"). For Bangladeshi viewers, China and India are both major partners, and the stakes differ (trade, loans, infrastructure, water). The research skill should ask "for whom?" (RC-15).
- **Scenarios over opinions.** V1.3's advice for small channels (give scenarios, not verdicts) fits Bangladesh's polarised climate and lowers risk.
- **Long videos work when the story pulls.** V1.3 credits Dhruv with holding viewers through 20 to 25 minute videos. Don't cut depth for length; keep the hand-offs and the mid-video twist instead.
- **The greeting is part of the brand.** Dhruv's fixed opening greeting is part of his identity. For Bangladesh, choose a signature opener that suits both religious and secular viewers, and keep it under 2 s (SC-02).
- **Money and aspiration hooks work in both markets** ("lakhs from ads", "crorepati teenagers") but read as clickbait fast. Only use them when the video delivers on them.
