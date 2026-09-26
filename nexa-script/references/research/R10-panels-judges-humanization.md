# R10: Judges, synthetic panels and humanization for script and copy review loops

Prepared 2026-09-26 for the skill-lab. Question: what makes a loop of draft, rubric judges, a 100-persona audience panel, fixes and rescoring reliable and useful for video scripts, ads, articles and emails, rather than theatre.

Sources are cited as [n] and listed in section 6. Tags: **V** = checked against the paper or page during this review; **S** = known through a secondary summary only; **VC** = the vendor's own claim; **U** = could not be retrieved, unverified. The web search budget ran out midway, so later sources were checked by opening paper pages directly; some relevant work may be missing. Thresholds in sections 5 and 7 are our starting values, to be tuned on the calibration set, unless a source is cited.

---

## 0. The short version

1. Judges are reliable for checkable criteria and for comparing two versions, and weak on taste: about 80% agreement with people on chat tasks [2], near chance on writing quality [31], and no positive correlation with experts on a creative-writing test [30].
2. Their biases (order, length, their own style, low-perplexity text, AI text over human text) all push a loop toward longer, smoother, blander prose [1][2][7][10][13].
3. Loops overfit their judges: scores rise while human-rated quality stays flat or falls [36]. Most gains come in the first rounds [39].
4. Personas get direction right more often than size: spread too narrow, subgroups wrong, groups flattened [44][45][59].
5. Grounding beats labels: interview-based agents reached 83 to 86% of people's own test-retest consistency, demographic labels 74% [51].
6. Ask for behaviour and choices: direct 1 to 5 ratings collapse to the middle, while free text mapped to a scale matched real purchase-intent distributions [56].
7. LLMs predict message effects well in survey experiments (r = .85) but only modestly in the field (r = .34, about expert level) [57]. We found no validated text-only predictor of a script's retention curve.
8. Script signals with evidence: fast early movement of meaning, emotional volatility, entertainment after the brand, brief brand pulses, shorter videos, intros that keep the title's promise [67][68][70][71][72][74].
9. AI prose shows in structure and rhythm more than in single words: participial clauses at 2 to 5 times the human rate, noun density, recycled templates, low surprise [79][82][35]. Heavy LLM users catch it with 1 error in 300, even after humanizer tools [85].
10. Humanizers that add errors or slang backfire: worse fluency and meaning [89], typos cost the writer [90], suspected AI use lowers trust [91].

---

## 1. LLM-as-a-judge

### 1.1 How close judges get to people

Strong judges agreed with human preferences in over 80% of MT-Bench and Chatbot Arena comparisons, about the rate at which humans agree with each other [2]. Chatbot Arena ranks models from more than 240,000 crowdsourced pairwise votes that agree well with expert raters [3]. G-Eval (chain of thought plus form filling) reached a Spearman correlation of 0.514 with human ratings of summaries [1]. With a rubric that describes every score level plus a reference answer, Prometheus correlated 0.897 with human scores, near GPT-4 (0.882) and far above ChatGPT (0.392) [16].

Two cautions. High percent agreement can hide score gaps of up to 5 points, so report Cohen's kappa, and expect leniency [27]. Outside English, GPT-4 judges drift toward higher scores and need calibration against native speakers, especially in non-Latin scripts [28]. That covers Bangla.

### 1.2 The biases that matter inside a rewrite loop

| Bias | Evidence | Effect in our loop |
|---|---|---|
| Position | Order alone let Vicuna-13B beat ChatGPT on 66 of 80 queries with ChatGPT judging [5]. GPT-4 kept its verdict after a swap 65% of the time, Claude-v1 23.8% [2]. The bias is worst when candidates are close in quality [6]. | Consecutive drafts are close, so order can decide. |
| Length | GPT-4 prefers longer answers more than people do [7]. A repetitive-list padding attack fooled GPT-3.5 and Claude-v1 in 91.3% of cases, GPT-4 in 8.7% [2]. Length control raised AlpacaEval's correlation with Arena from 0.94 to 0.98 [8]. Length is the top style factor even in human votes [4]. | Drafts grow each round. |
| Self-preference | Models recognise and favour their own text; more self-recognition, more bias [9]. GPT-4 gave itself about a 10% higher win rate, Claude-v1 about 25% [2]. | A same-family writer and judge inflate scores. |
| Familiarity | Judges rate low-perplexity text higher than humans do, whoever wrote it [10][11]. | Pulls toward predictable wording. |
| AI over human | G-Eval-4 always scored GPT-3.5 summaries above human ones, even where people preferred the human ones [1]. LLMs chose products with GPT-4-written descriptions 89% of the time, human raters 36% [13]. Judges did worst on AI-versus-human pairs [31]. | The human voice loses to AI polish. |
| Skew, anchoring, noise | Ratings bunch on few values, one attribute anchors the next, runs disagree, trivial prompt edits move scores [11]. On 1 to 5 scales one digit, often 3, dominates [1]. | Noise looks like progress. |
| Leniency, sycophancy | Judges are lenient [27]. Assistants tilt feedback toward the user's apparent views [29]. | Everything passes. |

One framework catalogues 12 bias types and finds serious ones persist in strong models on specific tasks [12].

### 1.3 Pairwise or absolute

Pairwise preferences align better with humans than direct scores on long-form output, and a ranking search over pairwise calls (PairS) beat direct scoring [15]. EQ-Bench's creative-writing test switched to pairwise matches with a Glicko rating for better separation, and truncates both texts to equal length before judging [33]. But pairwise judges are easier to fool: adding a spurious feature the judge likes flipped about 35% of pairwise preferences against 9% of absolute scores [14]. For order, MT-Bench asks twice with positions swapped and counts a win only when both agree, otherwise a tie [2]; Wang et al. also average across orders and ask for evidence before the verdict [5].

Rule for us: absolute yes/no criteria as gates; pairwise only to choose between versions, always in both orders, with length held to the brief.

### 1.4 Rubrics with anchors

- **Checklists beat scales.** Yes/no sub-questions raised average agreement between evaluator models by 0.45 and cut variance [17]. Husain's practitioner guide recommends pass/fail with a written critique, built from one domain expert's labels, with agreement checked on held-out cases [18].
- **Anchor every level.** Prometheus's gains came from rubrics that describe each score [16], the idea behind behaviourally anchored rating scales in 1963 [20]. Our best anchors are the client's own past pieces with known results.
- **Expect drift.** People refine criteria while grading real outputs [19]; criteria drafted from a few human labels and then refined improved agreement with experts [21].
- **Separate attributes.** Judge each alone, or gather evidence for all before scoring any, because one attribute anchors the next [11].

### 1.5 Several judges

A jury of three small models from different families (Command R, Claude 3 Haiku, GPT-3.5) beat one GPT-4 judge: kappa 0.763 against 0.627 on Natural Questions, Pearson 0.917 against 0.817 on Arena scores, at seven to eight times lower cost, with majority votes for binary calls and averages for scores [22]. The median of 12 LLMs forecast as well as 925 human forecasters, though the models leaned toward "yes" [23].

### 1.6 Reducing variance

- **Sample more than once** and measure run-to-run reliability [25]; a majority over samples (self-consistency) is the standard fix [24].
- **Reason from evidence.** Asking the judge to explain its rating raised correlation with humans, number-only output was worse, and G-Eval's automatic chain of thought did not always help [26]. On MT-Bench math items, chain of thought cut GPT-4's judging failures from 14 of 20 to 6, and a reference answer cut them to 3 [2].
- **Weight by probability** where log-probs exist: G-Eval's score is the probability-weighted sum over score tokens, which removes ties and the pull toward one value [1].

### 1.7 Where judges fail: creative and persuasive writing

- On the Torrance Test of Creative Writing, LLM stories passed 3 to 10 times fewer of its 14 tests than professional stories, and no LLM assessor correlated positively with the experts [30].
- On a 4,729-judgment writing-quality benchmark, zero-shot LLMs, reasoning models included, scored below or only a few points above the 50% chance line and did worst on AI-versus-human pairs. A reward model trained on expert edits reached 74%, and experienced writers preferred its picks 66% of the time (72.2% when its reward gap exceeded 1 point) [31].
- On LitBench (2,480 debiased Reddit story pairs), the best off-the-shelf judge, Claude 3.7 Sonnet, matched readers 73% of the time; trained reward models reached 78% [32].
- Locating flawed spans in LLM paragraphs, the best LLMs had precision 0.46 against expert-to-expert agreement of 0.57 [34].
- EQ-Bench lists biases it cannot control, including self-bias and a "slop" bias toward overused tropes [33].
- Professional fiction is 2 to 4 times less predictable to models than LLM fiction, instruction tuning widens the gap, and rated quality peaks at fairly high, not extreme, unpredictability [35]. With the familiarity bias [10][11], a judge-driven loop drags drafts away from that peak.

### 1.8 What happens inside loops

- When one model generates and evaluates, its scores rise over iterations while quality judged by real users stays flat or falls; larger models and shared context make it worse [36].
- An agent optimising tweet engagement made posts more controversial, raising engagement and toxicity together [37].
- Over-optimising a proxy reward eventually hurts the true goal [38].
- Self-Refine gained about 20% absolute on average, with most gains in the early iterations where tracked. Of its failures, 61% came from feedback proposing the wrong fix and 33% from feedback pointing at the wrong place [39].
- Without outside feedback, self-correction can make answers worse [40].

---

## 2. Simulated audiences and personas

### 2.1 What the evidence supports

- Conditioned on thousands of backstories taken from real survey respondents, GPT-3 reproduced subgroup response patterns in detail; the authors call this *algorithmic fidelity* and the result *silicon samples* [41].
- Agents for 1,052 Americans built from two-hour interviews, surveys or both reached 83%, 82% and 86% of the people's own two-week test-retest consistency on held-out General Social Survey items, against 74% from demographics alone, with smaller accuracy gaps across racial and ideological groups [51]. Nielsen Norman Group reports effect sizes from interview-based twins correlating r = 0.98 with human data [59].
- Naturalistic backstories improved the match to Pew survey distributions by up to 18% and consistency by 27% [52].
- In 57 real concept tests run with Colgate-Palmolive (9,300 human answers), direct Likert ratings from GPT-4o and Gemini 2.0 Flash collapsed toward 3 (distribution similarity 0.26 to 0.39). A short free-text reaction mapped to the scale by embedding similarity to fixed anchor statements (Semantic Similarity Rating, SSR) reached similarity 0.80 to 0.88 and 85 to 90% of human test-retest correlation. Without demographic markers it fell to about 50% and turned uniformly positive [56].
- LLM predictions of text-based survey experiments correlated r = .85 with the actual effects; for field megastudies r = .34, close to expert forecasters (r = .26) [57].

### 2.2 Where synthetic samples break

- **Too little spread.** Persona answers matched survey averages, but with much less variation, wrong regression coefficients, sensitivity to wording, and different results from the same prompt three months later [44]. In a marketing study, synthetic users got the direction of effects but not their size, with smaller standard deviations [59][60].
- **The wrong people.** Model opinions differed from US demographic groups by about the Democrat-Republican gap on climate change, and steering toward a group did not close it; people aged 65 and over and widowed people were among the poorly reflected groups [43]. Across 3,200 participants, 16 identities and 4 models, identity prompts misportrayed groups (closer to outsiders' views than members' own), flattened their variety and essentialised identity; mitigations reduced but did not remove this [45]. Political and marginalised groups, and bland general topics, were most prone to caricature [47]; generated personas carried more racial stereotypes than human-written portrayals [46].
- **A weak persona effect.** Persona variables explained under 10% of annotation variance in existing subjective datasets [48].
- **Survey artefacts.** Models favour the option labelled A and drift to near-uniform answers once order is randomised [49], react to wording that does not move humans [50], and can be unnaturally accurate ("hyper-accuracy distortion") [42].
- **Generated details drift.** Persona details written by an LLM produced significant deviations from real election and opinion results [53].
- **Hidden confounds.** Changing one attribute in the prompt, such as price, shifts others the model infers; describing the design to the model helped [54].
- **Pleasing the researcher.** In Nielsen Norman Group's test, synthetic learners claimed to finish every course and praised forums that real users found contrived; the authors treat such output as hypotheses only [58]. Models also lean toward "yes" [23] and toward the user's views [29].

### 2.3 What makes a synthetic panel informative

1. **Ground personas in real audience texts** (comments, reviews, questions, interviews) in the audience's own words, not a label or an LLM-invented biography [51][52][53].
2. **Engineer diversity:** weighted segment quotas that include sceptics, two or more model families, temperature near 1, and prompts that ask for a spread. Verbalized sampling (asking for several responses with their probabilities) raised creative diversity 1.6 to 2.1 times [61].
3. **Ask for behaviour in context.** "Which of these eight posts would you stop for?" beats "rate this hook"; stated intentions are where synthetic users idealise [58].
4. **Find drop-off by revealing the script in stages,** so a persona does not already know the payoff is coming (our inference; untested in the literature we found).
5. **Rank alternatives** and map free text to scales; relative results are more trustworthy than levels [44][56][57], keeping the pairwise caveat in mind [14].
6. **Use it to locate problems and pick versions, never to forecast levels.** Pin model versions and re-baseline when they change [44].

### 2.4 How companies use them, and what validation exists

- **System1** tests ads with real viewers (FaceTrace emotion measurement; Star rating for long-term growth, Spike for short-term sales, Fluency for branding). Its AI "Test Your Ad Screen" is described as trained on 18 million human emotional responses and matching human testing "9 times out of 10"; no method or error metric is on the page [62] (VC).
- **Kantar LINK AI** is marketed as AI prediction of ad pre-test results; its product pages returned 404 during this review, so no validation figure is given here [66] (U).
- **Evidenza** sells synthetic B2B buyers and claims 88% average similarity over 100+ head-to-head validations, citing client correlations such as r = 0.81 [63] (VC).
- **Artificial Societies** claims 3 million personas built from real behaviour and 86% distribution accuracy across 1,000 panels [64] (VC).
- **Colgate-Palmolive and PyMC Labs** published the most transparent validation we found: the SSR paper above, with open code [56].
- **Google's ABCDs Detector** has Gemini check an ad for creative features (dynamic start, early brand and product, faces, supers, pacing, call to action), warns of false positives, and publishes no accuracy figures [65].

The pattern: credible tools are trained on or calibrated against large banks of real human responses; uncalibrated LLM personas are hypothesis generators [58].

---

## 3. Predicting retention and ad results from a script

- **Story shape.** Across nearly 50,000 texts, films and TV were liked more when meaning advanced quickly, TV shows that covered a lot of ground scored lower, and academic papers showed the opposite speed pattern [67]. Speed is genre-specific, not universal.
- **Emotional volatility.** Bigger period-to-period sentiment swings raised ratings of 4,000+ movies and made readers of 30,000+ online articles more likely to keep reading, confirmed by experiment [68]. Six basic arcs dominate 1,327 Project Gutenberg stories, and some arcs earn more downloads [69].
- **Ad structure.** For 82 ads watched by 178 consumers under webcam tracking, entertainment had an inverted-U relation with purchase intent, and entertainment after the brand appeared helped while entertainment before it did not [70]. Brief, repeated brand appearances ("pulsing") reduce avoidance of TV ads [71] (title-level claim; abstract not retrieved).
- **Length and transitions.** Across 6.9 million edX sessions, shorter videos and informal talking heads held attention better [72]. In 862 videos, longer ones had more dropout, and 61% of sampled interaction peaks coincided with visual transitions [73].
- **Platform definitions.** YouTube's intro metric is the share still watching at 30 seconds, and strong intros match what the title and thumbnail promised; the report also marks top moments, spikes and dips [74]. Meta found mobile feed content can be recalled after 0.25 seconds of exposure, and a piece of mobile content gets about 1.7 seconds on average [75].
- **Message tests.** LLMs predict survey-experiment effects well and field effects weakly [57]. In a 54-intervention megastudy, impartial human forecasters also failed to pick the winners [76]. The Upworthy archive of 32,487 real headline A/B tests is a public check for any predictor [77].

Not found: peer-reviewed evidence that any model predicts a specific script's retention curve or CTR from text alone at useful accuracy. So the panel locates likely drop points and ranks versions, and the skill never prints a predicted retention percentage.

---

## 4. AI-text tells and humanization

### 4.1 What distinguishes AI prose

- **Grammar.** Instruction-tuned models use present participial clauses at 2 to 5 times the human rate (GPT-4o 5.3 times), nominalisations at 1.5 to 2 times, "that" clauses as subjects 2.6 times and phrasal coordination 1.9 times, but agentless passives at about half the human rate. The style is dense, noun-heavy and the same across genres, and instruction tuning widens the gap [79]. So Orwell's advice to prefer the active voice [98] does not fix AI prose, which is already active; the tells are "-ing" tails and noun stacks.
- **Vocabulary.** Words such as "delve", "intricate" and "underscore" are overrepresented, with evidence consistent with preference tuning as one cause [81]; at least 13.5% of 2024 PubMed abstracts were processed with an LLM [80]. Clusters, not single words, are the signal [86].
- **Templates.** 76% of the part-of-speech templates in model output appear in pre-training data against 35% for human text, and fine-tuning leaves them in place [82]. Some phrase patterns are over 1,000 times more frequent in LLM output than in human text [88]. Wikipedia's editors add negative parallelisms ("not just X, but Y"), inflated significance, promotional tone, vague attributions, "despite its challenges" endings, "serves as" where "is" would do, title-case headings, heavy bold and dash overuse [86].
- **Rhythm and surprise.** Human news text has more scattered sentence lengths, richer vocabulary, shorter constituents and more negative emotion, while LLM text uses more numbers, symbols and auxiliaries [83]. Humans and models spread information differently through a text [84], and professional fiction is far less predictable than model fiction [35].
- **What trained readers notice.** Five heavy ChatGPT users voting together misclassified 1 of 300 articles, beat automatic detectors, and stayed accurate on paraphrased and humanized text, using vocabulary plus formality, originality and clarity [85].

### 4.2 Why readers care

Smart replies made chats faster and warmer, but partners suspected of using AI were rated more negatively [91]. Hosts thought to have AI-written profiles were distrusted when readers saw a mix of AI and human profiles [92]. With the source hidden, AI ad copy was rated higher than experts' copy; learning a human wrote it raised ratings, while learning AI helped did not lower them [93]. Tells cost most where readers expect a person: emails, replies, founder posts, personal scripts.

### 4.3 Why humanizer tools backfire

- Across 19 humanizer and paraphrasing tools, the worst tier added nonsense phrases and invented citations. Judged for fluency against the original, humanized text won only 26% of the time for the best tier, 14.67% for the middle, 2.67% for the worst [89].
- Errors cost the writer: in housemate-search emails, three typos lowered ratings by about 0.47 points on a 7-point scale and grammar errors by about 0.22 [90].
- Trained readers see through humanizers [85], and scrubbing surface signs while keeping the substance only hides the problem [86].
- Random slang is a register error. The target is the audience's own register, learned from their texts (2.3, point 1).

### 4.4 What editors actually change

Professional writers editing 1,057 LLM paragraphs made about 8 edits each: awkward word choice 28% of edits, poor sentence structure 20%, unnecessary exposition 18%, cliche 17%, plus purple prose, missing specificity and tense slips. 70% of non-deletion edits kept the meaning, and readers ranked writer-edited text above LLM-edited text above raw LLM text [34]. Suppressing listed patterns during generation scaled to 8,000+ patterns, and a targeted fine-tune cut slop by 90% without hurting benchmarks [88].

- **Scripts:** open on the concrete thing (object, number, conflict), not a greeting or a rhetorical question; one idea; every beat adds information; lines that fit one breath, mixed with short punches; no summary lines; the creator's own words.
- **Articles:** a claim-first lead; specifics in every paragraph; uneven lengths where the content calls for it; no section-ending summaries or default lists of three; little bold, few headings; plain opinions and plain doubts.
- **Emails:** the reason in the first line; the reader's context; one ask; no padding openers, and no headings or bullets in a personal note; never injected typos.

---

## 5. Recommended protocol

### 5.1 Rubric judging

**Judge inputs:** the brief (audience, platform, goal, must-say facts), the draft with numbered lines (L1 to Ln), the rubric with anchors, and 3 to 5 of the client's past pieces with known results. Never the writer's notes, project files, earlier scores, authorship, or which version is newer: shared context feeds reward hacking and sycophancy [29][36].

**Roster:** three judges from at least two model families; taste and pairwise calls go to families other than the writer's [9][22]. Two runs each, with criterion order shuffled.

**Layers:**

1. *Hard gates*, deterministic where possible: length or duration, must-say facts present, nothing invented, one call to action, lint clean, platform specs.
2. *Binary checklist with evidence.* Example for a short video: B1 L1 states a specific tension, promise or visual action; B2 the first 30 seconds keep the title's promise [74]; B3 one idea; B4 at least 3 concrete details per 100 words; B5 no beat restates an earlier one; B6 a turn before the midpoint [67][68]; B7 brand early and brief, then short pulses [70][71]; B8 speakable rhythm; B9 matches the voice samples; B10 claims supported and inside the brief.
3. *Two anchored 1 to 5 scales only,* "Would the target viewer stop for L1?" and "Publishable?": 1 harms the brand; 2 generic, reads as AI; 3 publishable but forgettable; 4 good, with one line people would repeat; 5 as good as the client's best past piece (attached).

**Prompt order:** for each criterion, quote the evidence lines, give one or two sentences of reasoning, then the verdict [26]. State that length is not quality, that the judge must not rewrite, and that it did not write the draft.

```json
{"judge": "family/model-id", "run": 1,
 "criteria": [{"id": "B1_hook", "lines": ["L1"], "evidence": "L1: 'Hi everyone, welcome back'",
   "reason": "Greeting; no tension or promise.", "verdict": "fail", "severity": "major",
   "problem": "Opening gives no reason to stay."}],
 "scales": {"stop_for_L1": {"evidence": "...", "score": 2},
            "publishable": {"evidence": "...", "score": 3}},
 "best_lines": ["L7"], "tells": [{"line": "L4", "pattern": "not X but Y"}]}
```

**Aggregation:** majority of 6 votes (3 judges by 2 runs) per binary criterion; a 3 to 3 split is marked unstable and goes to a human, not into the fix list. Scales take the median; an interquartile range above 1 marks the scale unreliable for that draft.

**Calibration, per client and format, before first use:** 20 to 40 past pieces labelled pass or fail by the user, with outcomes where available (30-second retention, average view duration, CTR, replies). Keep a criterion at a judge-to-user kappa of 0.6 or more, rewrite it below that, drop it below 0.4 [18][27]. If "publishable" correlates below 0.2 with real outcomes, report it but never gate on it. Recalibrate whenever a judge model changes [44].

**Version check:** each judge compares old and new in both orders under neutral labels; a win counts only when both orders agree [2].

### 5.2 The 100-persona panel

**Build once per client and format, and reuse it across drafts,** so rounds stay comparable and prompt drift stays out [44][50].

- *Evidence pack:* hundreds to a few thousand real audience texts (comments on the client's and competitors' posts, reviews, DMs, FAQs, survey answers, search terms), channel analytics, and any interviews.
- *Segments:* 6 to 10, weighted from analytics, always including sceptics, newcomers and a price- or time-pressed group; for example core fans 30, newcomers 25, sceptics 15, price hunters 15, lapsed 10, adjacent 5.
- *Persona card (120 to 200 words):* segment; demographics as context only; a first-person backstory in the audience's register built from real texts [52]; habits (platform, time of day, what they skip, recent purchases or videos); one or two real quotes with source ids; viewing context (sound off, on a bus).
- *Validation:* the panel must rank 5 to 10 past posts roughly in order of their real performance (Spearman 0.4 or more) before its output counts.

**Tasks, behaviour first:**

- **T1 Feed stop test:** the draft's hook (first line plus title or thumbnail text) among 6 to 8 real niche hooks with known performance, positions rotated: "pick up to two you would stop for".
- **T2 Staged watch:** the script in chunks (hook, 0 to 15 s, 15 to 30 s, 30 to 60 s, the rest) in separate calls; continue or leave, with the line and a reason tag (slow, confusing, salesy, irrelevant, repetitive, fake, other). Only those who continue see the next chunk. The cheap single-call version asks for the first line where they would leave and accepts lookahead bias.
- **T3 After-view:** like, comment (write it), share (with whom), save, click, follow or nothing; the line remembered; the line that felt fake; any confusing line.
- **T4 Intent (ads, emails):** free text mapped to a 5-point distribution by similarity to fixed anchor statements [56], never a direct number.
- **T5 Pairwise (later rounds):** both versions, random order, neutral labels: "which would you rather watch, and the one reason".

**Batching:** 10 calls of 10 personas split across two model families, with the instructions and draft in a cached prefix and the persona cards after it. Tell the model each persona reacts alone and that it is fine if most or none like it. Shuffle persona order every round. Repeat 5 personas in a second batch as a noise probe: if their continue-or-leave answers disagree more than 30% of the time, do not act on the panel. Fast models suffice: Gemini 2.0 Flash reached 90% correlation attainment with SSR [56]. Expect 20 to 40 calls per pass.

```json
{"persona_id": "P037", "segment": "sceptic",
 "t1": {"stopped_for": ["H3", "H6"], "why": "H3 shows the price"},
 "t2": {"left_at": "L9", "reason_tag": "salesy", "why": "sounds like every ad"},
 "t3": {"actions": ["save"], "comment": "does it work on gas stoves?",
        "remember": "L5", "fake": "L11", "confusing": null},
 "t4_text": "I'd check the price first, maybe next month"}
```

### 5.3 From reactions to a fix list

**Metrics:**

- *Hook index:* the draft's T1 stop rate divided by the median stop rate of the real hooks in the lineup.
- *Survival:* S(k) = share still watching after chunk or line k; hazard h(k) = (S(k-1) minus S(k)) / S(k-1). Flag a spike where h(k) is at least twice the median hazard and 5 or more personas leave.
- *Proportions with Wilson 95% intervals:* at n = 100, p = 0.5 is about plus or minus 9.6 points, and p = 0.1 spans 5.5% to 17.4%.
- *Per-line shares* (remembered, fake, confusing) and T4 top-two-box, all split by segment and weighted.

**Issues** come from panel flags (line, tag, reason) and failed judge criteria (lines, severity). Cluster by line and tag, then merge near-duplicates. Priority = weighted support x severity (major 3, moderate 2, minor 1) x 1.5 when a judge failed the same lines. An issue enters the fix list only with at least 10% support overall or 20% in a priority segment, seen in both model families; others go to a watch list.

**Keep list:** lines remembered by 15% or more, or named best by two judges, are frozen next round. A line that fans remember and sceptics call fake is a polarising asset, not a bug; a human decides.

**Output:** at most 5 fixes, each with line ids, the problem as the reader experiences it, 1 or 2 persona quotes plus the judge's evidence, and constraints ("keep L5 wording"). Name the problem and let the writer choose the fix: wrong prescriptions and wrong locations caused most Self-Refine failures [39].

### 5.4 Stopping rules

- **Cap:** 2 revision rounds, 3 for flagship pieces. Gains come early [39] and scores inflate with iteration [36].
- **Continue only if** a gate fails, a judge criterion fails by majority, or a fix has at least 20% support in the core segment.
- **Accept a revision only if** it wins the paired panel comparison with at least 61 of 100 personas (the two-sided p < .05 threshold under independence; 39 of 60, 21 of 30), wins within each model family, is not preferred against by the judges' both-orders check, breaks no gate, and passes 5.5. Personas from one model are not independent, so treat 61% as a floor.
- **Noise band:** run the unchanged draft through the panel twice at the start, and ignore later changes smaller than that difference.
- **Stop when** gates pass and the latest pairwise result sits between 40% and 60%, at the cap, or on oscillation (a fixed issue returns, or one line tops the fix list twice).
- **Ship the best version, not the last:** a both-orders pairwise tournament among the survivors, then a blind human read of the top two for client work.

### 5.5 Keeping the writing alive

The pressure toward blandness is documented: judges favour familiar [10][11], AI-written [13][31] and longer [7][8] text; loops reward-hack [36]; RLHF cuts output diversity [97]; LLM rewriting shrank writing-complexity variance by 21 to 50% [94]; co-writing homogenised essays [95], and AI story ideas made stories more alike [96]. Counter-measures:

1. **Edit budget:** at most 25% of tokens change per round, only on fix-list lines and their neighbours; keep-list lines stay frozen.
2. **Generic-baseline test:** a fresh model writes three versions from the brief alone. The draft must not move closer to them (embedding cosine, shared 4-grams), and must win "which could only have been written for this creator?" against the closest one.
3. **Specificity:** concrete details per 100 words must not fall.
4. **Tells:** lint findings must not rise, and the template ledger must not show a repeat.
5. **Rhythm:** the spread of sentence lengths stays within the creator's own range [83].
6. **Love and hate, not the mean:** track top-box (share, save, remember a line) and bottom-box. Trimming hate by 3 points while losing 10 points of love is a regression.
7. **Voice judge:** pairwise against the creator's real samples.
8. **Explore before polishing:** when a hook fails, generate 5 hooks with verbalized sampling, including unlikely ones [61], and test them all in T1 instead of asking for one "improved" hook.

---

## 6. Sources

**LLM judges**

- [1] Liu et al. G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment. EMNLP 2023. https://arxiv.org/abs/2303.16634 (V)
- [2] Zheng et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS 2023. https://arxiv.org/abs/2306.05685 (V)
- [3] Chiang et al. Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference. arXiv, Mar 2024. https://arxiv.org/abs/2403.04132 (V)
- [4] Li, Angelopoulos, Chiang. Does style matter? Disentangling style and substance in Chatbot Arena. LMSYS blog, 29 Aug 2024. https://lmsys.org/blog/2024-08-28-style-control/ (V)
- [5] Wang et al. Large Language Models are not Fair Evaluators. arXiv, May 2023. https://arxiv.org/abs/2305.17926 (V)
- [6] Shi et al. Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. AACL-IJCNLP 2025. https://arxiv.org/abs/2406.07791 (V)
- [7] Saito et al. Verbosity Bias in Preference Labeling by Large Language Models. arXiv, Oct 2023. https://arxiv.org/abs/2310.10076 (V)
- [8] Dubois et al. Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators. COLM 2024. https://arxiv.org/abs/2404.04475 (V)
- [9] Panickssery, Bowman, Feng. LLM Evaluators Recognize and Favor Their Own Generations. arXiv, Apr 2024. https://arxiv.org/abs/2404.13076 (V)
- [10] Wataoka, Takahashi, Ri. Self-Preference Bias in LLM-as-a-Judge. NeurIPS 2024 workshop, Oct 2024. https://arxiv.org/abs/2410.21819 (V)
- [11] Stureborg, Alikaniotis, Suhara. Large Language Models are Inconsistent and Biased Evaluators. arXiv, May 2024. https://arxiv.org/abs/2405.01724 (V)
- [12] Ye et al. Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge. arXiv, Oct 2024. https://arxiv.org/abs/2410.02736 (V)
- [13] Laurito et al. AI-AI bias: Large language models favor communications generated by large language models. PNAS 122(31), 2025. https://pmc.ncbi.nlm.nih.gov/articles/PMC12337326/ (V)
- [14] Tripathi, Wadhwa, Durrett, Niekum. Pairwise or Pointwise? Evaluating Feedback Protocols for Bias in LLM-Based Evaluation. COLM 2025. https://arxiv.org/abs/2504.14716 (V)
- [15] Liu et al. Aligning with Human Judgement: The Role of Pairwise Preference in Large Language Model Evaluators. COLM 2024. https://arxiv.org/abs/2403.16950 (V)
- [16] Kim et al. Prometheus: Inducing Fine-grained Evaluation Capability in Language Models. ICLR 2024. https://arxiv.org/abs/2310.08491 (V)
- [17] Lee et al. CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists. EMNLP 2025. https://arxiv.org/abs/2403.18771 (V)
- [18] Husain. Using LLM-as-a-Judge For Evaluation: A Complete Guide. hamel.dev, 29 Oct 2024. https://hamel.dev/blog/posts/llm-judge/ (V)
- [19] Shankar et al. Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences. arXiv, Apr 2024. https://arxiv.org/abs/2404.12272 (V)
- [20] Smith, Kendall. Retranslation of expectations: An approach to the construction of unambiguous anchors for rating scales. Journal of Applied Psychology, 1963. https://doi.org/10.1037/h0047060 (V, metadata only)
- [21] Liu et al. Calibrating LLM-Based Evaluator. arXiv, Sep 2023. https://arxiv.org/abs/2309.13308 (V)
- [22] Verga et al. Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models. arXiv, Apr 2024. https://arxiv.org/abs/2404.18796 (V)
- [23] Schoenegger et al. Wisdom of the Silicon Crowd: LLM Ensemble Prediction Capabilities Rival Human Crowd Accuracy. arXiv, 2024. https://arxiv.org/abs/2402.19379 (V)
- [24] Wang et al. Self-Consistency Improves Chain of Thought Reasoning in Language Models. ICLR 2023. https://arxiv.org/abs/2203.11171 (V)
- [25] Schroeder, Wood-Doughty. Can You Trust LLM Judgments? Reliability of LLM-as-a-Judge. arXiv, Dec 2024. https://arxiv.org/abs/2412.12509 (V)
- [26] Chiang, Lee. A Closer Look into Automatic Evaluation Using Large Language Models. Findings of EMNLP 2023. https://arxiv.org/abs/2310.05657 (V)
- [27] Thakur et al. Judging the Judges: Evaluating Alignment and Vulnerabilities in LLMs-as-Judges. GEM 2025. https://arxiv.org/abs/2406.12624 (V)
- [28] Hada et al. Are Large Language Model-based Evaluators the Solution to Scaling Up Multilingual Evaluation? Findings of EACL 2024. https://arxiv.org/abs/2309.07462 (V)
- [29] Sharma et al. Towards Understanding Sycophancy in Language Models. arXiv, Oct 2023. https://arxiv.org/abs/2310.13548 (V)

**Judging creative writing**

- [30] Chakrabarty et al. Art or Artifice? Large Language Models and the False Promise of Creativity. CHI 2024. https://arxiv.org/abs/2309.14556 (V)
- [31] Chakrabarty, Laban, Wu. AI-Slop to AI-Polish? Aligning Language Models through Edit-Based Writing Rewards and Test-time Computation. arXiv, Apr 2025. https://arxiv.org/abs/2504.07532 (V)
- [32] Fein et al. LitBench: A Benchmark and Dataset for Reliable Evaluation of Creative Writing. arXiv, Jul 2025. https://arxiv.org/abs/2507.00769 (V)
- [33] Paech. EQ-Bench Creative Writing Benchmark v3, README. GitHub, 2025. https://github.com/EQ-bench/creative-writing-bench (S)
- [34] Chakrabarty, Laban, Wu. Can AI writing be salvaged? Mitigating Idiosyncrasies and Improving Human-AI Alignment in the Writing Process through Edits. CHI 2025. https://arxiv.org/abs/2409.14509 (V)
- [35] Sui. LLMs Exhibit Significantly Lower Uncertainty in Creative Writing Than Professional Writers. arXiv, Feb 2026. https://arxiv.org/abs/2602.16162 (V)

**Loops and optimisation**

- [36] Pan, He, Bowman, Feng. Spontaneous Reward Hacking in Iterative Self-Refinement. arXiv, Jul 2024. https://arxiv.org/abs/2407.04549 (V)
- [37] Pan, Jones, Jagadeesan, Steinhardt. Feedback Loops With Language Models Drive In-Context Reward Hacking. ICML 2024. https://arxiv.org/abs/2402.06627 (V)
- [38] Gao, Schulman, Hilton. Scaling Laws for Reward Model Overoptimization. arXiv, Oct 2022. https://arxiv.org/abs/2210.10760 (V)
- [39] Madaan et al. Self-Refine: Iterative Refinement with Self-Feedback. NeurIPS 2023. https://arxiv.org/abs/2303.17651 (V)
- [40] Huang et al. Large Language Models Cannot Self-Correct Reasoning Yet. ICLR 2024. https://arxiv.org/abs/2310.01798 (V)

**Personas and synthetic samples**

- [41] Argyle et al. Out of One, Many: Using Language Models to Simulate Human Samples. Political Analysis, 2023. https://arxiv.org/abs/2209.06899 (V)
- [42] Aher, Arriaga, Kalai. Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies. ICML 2023. https://arxiv.org/abs/2208.10264 (V)
- [43] Santurkar et al. Whose Opinions Do Language Models Reflect? ICML 2023. https://arxiv.org/abs/2303.17548 (V)
- [44] Bisbee et al. Synthetic Replacements for Human Survey Data? The Perils of Large Language Models. Political Analysis 32(4), 2024. https://www.cambridge.org/core/journals/political-analysis/article/synthetic-replacements-for-human-survey-data-the-perils-of-large-language-models/B92267DC26195C7F36E63EA04A47D2FE (S)
- [45] Wang, Morgenstern, Dickerson. Large language models that replace human participants can harmfully misportray and flatten identity groups. Nature Machine Intelligence 7, 2025. https://arxiv.org/abs/2402.01908 (V)
- [46] Cheng, Durmus, Jurafsky. Marked Personas: Using Natural Language Prompts to Measure Stereotypes in Language Models. ACL 2023. https://arxiv.org/abs/2305.18189 (V)
- [47] Cheng, Piccardi, Yang. CoMPosT: Characterizing and Evaluating Caricature in LLM Simulations. EMNLP 2023. https://arxiv.org/abs/2310.11501 (V)
- [48] Hu, Collier. Quantifying the Persona Effect in LLM Simulations. ACL 2024. https://arxiv.org/abs/2402.10811 (V)
- [49] Dominguez-Olmedo, Hardt, Mendler-Dünner. Questioning the Survey Responses of Large Language Models. NeurIPS 2024. https://arxiv.org/abs/2306.07951 (V)
- [50] Tjuatja et al. Do LLMs exhibit human-like response biases? A case study in survey design. arXiv, Nov 2023. https://arxiv.org/abs/2311.04076 (V)
- [51] Park et al. Generative Agent Simulations of 1,000 People (2024), revised 2026 as LLM Agents Grounded in Self-Reports Enable General-Purpose Simulation of Individuals. https://arxiv.org/abs/2411.10109 (V)
- [52] Moon et al. Virtual Personas for Language Models via an Anthology of Backstories. EMNLP 2024. https://arxiv.org/abs/2407.06576 (V)
- [53] Li, Chen, Namkoong, Peng. LLM Generated Persona is a Promise with a Catch. arXiv, Mar 2025. https://arxiv.org/abs/2503.16527 (V)
- [54] Gui, Toubia. The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective. arXiv, Dec 2023. https://arxiv.org/abs/2312.15524 (V)
- [56] Maier et al. (PyMC Labs, Colgate-Palmolive). LLMs Reproduce Human Purchase Intent via Semantic Similarity Elicitation of Likert Ratings. arXiv, Oct 2025. https://arxiv.org/abs/2510.08338 (V)
- [57] Hewitt, Ashokkumar, Ghezae, Willer. Large language models can predict the results of social science experiments. Nature, 2026, per the authors' site. https://www.treatmenteffect.app/ (V for the site's figures)
- [58] Rosala, Moran. Synthetic Users: If, When, and How to Use AI-Generated "Research". Nielsen Norman Group, 21 Jun 2024. https://www.nngroup.com/articles/synthetic-users/ (V)
- [59] Budiu. Evaluating AI-Simulated Behavior: Insights from Three Studies on Digital Twins and Synthetic Users. Nielsen Norman Group, 15 Aug 2025. https://www.nngroup.com/articles/ai-simulations-studies/ (V)
- [60] Arora, Chakraborty, Nishimura. AI-Human Hybrids for Marketing Research: Leveraging LLMs as Collaborators. Journal of Marketing, 2025. https://journals.sagepub.com/doi/10.1177/00222429241276529 (S, via [59])
- [61] Zhang et al. Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity. arXiv, Oct 2025. https://arxiv.org/abs/2510.01171 (V)

**Tools and vendors** (accessed 26 Sep 2026)

- [62] System1. Test Your Ad, including Test Your Ad Screen. https://system1group.com/test-your-ad (VC)
- [63] Evidenza. Home page validation claims. https://www.evidenza.ai/ (VC)
- [64] Artificial Societies. Home page. https://societies.ai/ (VC)
- [65] Google Marketing Solutions. ABCDs Detector. GitHub. https://github.com/google-marketing-solutions/abcds-detector (V)
- [66] Kantar. LINK AI product pages; kantar.com/campaigns/link-ai and three similar URLs returned 404. (U)

**Retention and ad performance**

- [67] Toubia, Berger, Eliashberg. How quantifying the shape of stories predicts their success. PNAS, Jun 2021. https://doi.org/10.1073/pnas.2011695118 (V, abstract)
- [68] Berger, Kim, Meyer. What Makes Content Engaging? How Emotional Dynamics Shape Success. Journal of Consumer Research, 2021. https://doi.org/10.1093/jcr/ucab010 (V, abstract)
- [69] Reagan et al. The emotional arcs of stories are dominated by six basic shapes. EPJ Data Science, 2016. https://doi.org/10.1140/epjds/s13688-016-0093-1 (V, abstract)
- [70] Teixeira, Picard, el Kaliouby. Why, When, and How Much to Entertain Consumers in Advertisements? A Web-Based Facial Tracking Field Study. Marketing Science, 2014. https://doi.org/10.1287/mksc.2014.0854 (V, abstract)
- [71] Teixeira, Wedel, Pieters. Moment-to-Moment Optimal Branding in TV Commercials: Preventing Avoidance by Pulsing. Marketing Science, 2010. https://doi.org/10.1287/mksc.1100.0567 (U, title only)
- [72] Guo, Kim, Rubin. How video production affects student engagement: an empirical study of MOOC videos. ACM Learning at Scale, 2014. https://doi.org/10.1145/2556325.2566239 (V, abstract)
- [73] Kim et al. Understanding in-video dropouts and interaction peaks in online lecture videos. ACM Learning at Scale, 2014. https://doi.org/10.1145/2556325.2566237 (V, abstract)
- [74] YouTube Help. Measure key moments for audience retention. Accessed 26 Sep 2026. https://support.google.com/youtube/answer/9314415 (V)
- [75] Facebook IQ (Meta). Capturing Attention in Feed: The Science Behind Effective Video Creative. 20 Apr 2016. https://www.facebook.com/business/news/insights/capturing-attention-feed-video-creative (V)
- [76] Milkman et al. Megastudies improve the impact of applied behavioural science. Nature 600, 2021. https://doi.org/10.1038/s41586-021-04128-4 (V, abstract)
- [77] Matias et al. The Upworthy Research Archive, a time series of 32,487 experiments in U.S. media. Scientific Data, 2021. https://doi.org/10.1038/s41597-021-00934-7 (V, abstract)

**AI text and humanization**

- [79] Reinhart et al. Do LLMs write like humans? Variation in grammatical and rhetorical styles. PNAS 122, e2422455122, 2025. https://arxiv.org/abs/2410.16107 (V)
- [80] Kobak et al. Delving into LLM-assisted writing in biomedical publications through excess vocabulary. Science Advances 11(27), 2 Jul 2025. https://arxiv.org/abs/2406.07016 (V)
- [81] Juzek, Ward. Why Does ChatGPT "Delve" So Much? Exploring the Sources of Lexical Overrepresentation in Large Language Models. COLING 2025. https://arxiv.org/abs/2412.11385 (V)
- [82] Shaib, Elazar, Li, Wallace. Detection and Measurement of Syntactic Templates in Generated Text. EMNLP 2024. https://arxiv.org/abs/2407.00211 (V)
- [83] Muñoz-Ortiz, Gómez-Rodríguez, Vilares. Contrasting Linguistic Patterns in Human and LLM-Generated News Text. Artificial Intelligence Review 57, 2024. https://arxiv.org/abs/2308.09067 (V)
- [84] Venkatraman, Uchendu, Lee. GPT-who: An Information Density-based Machine-Generated Text Detector. Findings of NAACL 2024. https://arxiv.org/abs/2310.06202 (V)
- [85] Russell, Karpinska, Iyyer. People who frequently use ChatGPT for writing tasks are accurate and robust detectors of AI-generated text. ACL 2025. https://arxiv.org/abs/2501.15654 (V)
- [86] Wikipedia editors (WikiProject AI Cleanup). Wikipedia:Signs of AI writing. Accessed 26 Sep 2026. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (V)
- [88] Paech, Roush, Goldfeder, Shwartz-Ziv. Antislop: A Comprehensive Framework for Identifying and Eliminating Repetitive Patterns in Language Models. arXiv, Oct 2025. https://arxiv.org/abs/2510.15061 (V)
- [89] Masrour, Emi, Spero. DAMAGE: Detecting Adversarially Modified AI Generated Text. arXiv, Jan 2025. https://arxiv.org/abs/2501.03437 (V)
- [90] Boland, Queen. If You're House Is Still Available, Send Me an Email: Personality Influences Reactions to Written Errors in Email Messages. PLOS ONE, 9 Mar 2016. https://doi.org/10.1371/journal.pone.0149885 (V)
- [91] Hohenstein et al. Artificial intelligence in communication impacts language and social relationships. Scientific Reports 13, 2023. https://doi.org/10.1038/s41598-023-30938-9 (V, abstract)
- [92] Jakesch et al. AI-Mediated Communication: How the Perception that Profile Text was Written by AI Affects Trustworthiness. CHI 2019. https://doi.org/10.1145/3290605.3300469 (V, abstract)
- [93] Zhang, Gosline. Human favoritism, not AI aversion: People's perceptions (and bias) toward generative AI, human experts, and human-GAI collaboration in persuasive content generation. Judgment and Decision Making, 2023. https://doi.org/10.1017/jdm.2023.37 (V, abstract)
- [94] Sourati et al. The Shrinking Landscape of Linguistic Diversity in the Age of Large Language Models. Nature Human Behaviour, 2026. https://arxiv.org/abs/2502.11266 (V)
- [95] Padmakumar, He. Does Writing with Language Models Reduce Content Diversity? ICLR 2024. https://arxiv.org/abs/2309.05196 (V)
- [96] Doshi, Hauser. Generative AI enhances individual creativity but reduces the collective diversity of novel content. Science Advances, 2024. https://doi.org/10.1126/sciadv.adn5290 (V, abstract)
- [97] Kirk et al. Understanding the Effects of RLHF on LLM Generalisation and Diversity. ICLR 2024. https://arxiv.org/abs/2310.06452 (V)
- [98] Orwell. Politics and the English Language. 1946. The Orwell Foundation. https://www.orwellfoundation.com/the-orwell-foundation/orwell/essays-and-other-works/politics-and-the-english-language/ (V)

---

## 7. Implications for our skills

1. **Pipeline for every script and copy job:** `copylint` gates, then judges (5.1), the panel (5.2), a deterministic aggregator (5.3) that writes `fixlist.json` and `keep.json`, a bounded rewrite (5.5), rescoring, the stop rules (5.4), a best-of tournament, and a human read for client work. The native-reader `copyjudge` stays the language gate.
2. **Judges:** 3 per run from at least 2 families. With Claude as writer, taste and pairwise calls go to GPT (via Codex) and Gemini (via agy); a fresh Claude session may take checklist items only. 2 runs, shuffled criteria, blind to authorship, version order and project files. Checklist plus two anchored scales, evidence before verdict, the JSON in 5.1, majority of 6.
3. **`calibration.json` per client and format:** 20 to 40 labelled past pieces with outcomes, kappa per criterion, the publishable scale's correlation with results, and the panel's rank correlation on past posts; recomputed whenever a model changes. Bangla thresholds come from native-reader labels, because judges inflate scores in non-Latin scripts [28].
4. **`panel.json` per client and format:** 100 persona cards across 6 to 10 weighted segments, sceptics included, each card citing the real audience texts behind it; no invented biographies [51][52][53].
5. **Panel run:** T1 to T5, 10 batches of 10, two families, fast models, cached prefix, 5 repeated personas as a noise probe.
6. **Aggregator in code, not a model:** Wilson intervals, survival and hazard, segment splits, clustering, priority, entry rules, keep list, conflict flags, at most 5 fixes. Every number it reports is labelled "synthetic, directional".
7. **Acceptance:** paired wins of at least 61 of 100 in both families, beyond the noise band, and a clean blandness gate. A blandness regression blocks acceptance even when the panel prefers the new draft.
8. **Honest reporting:** never state predicted retention, CTR or conversion; never call personas people or a focus group; never publish persona quotes as testimonials. After 5 to 10 published pieces, compare hazard spikes and the hook index with real retention dips and CTR, and down-weight any task that does not track reality.
9. **Humanization policy:** no humanizer tools and no injected typos or slang [85][89][90]. Fix the structural tells (participial tails, nominalisations, templates, uniform rhythm, summary lines) through the edit taxonomy in 4.4, in the audience's own register from the evidence pack.
