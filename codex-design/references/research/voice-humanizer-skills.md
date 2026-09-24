# Humanizer skills and anti-slop projects, 2024 to 2026

Research note for the codex-design copy system. Every source below was read on 2026-09-24.

**Scope.** Existing skills, rule files, linters and word lists that teach or enforce natural, human-sounding writing:
- Claude Code, Agent Skills, Codex and Cursor rule sets on GitHub;
- data-backed word and phrase lists;
- the skills installed on this machine;
- what these projects say about casual, social and non-English writing.

**Baseline.** "Already covered" means covered by one of these files:
- `references/copy.md` (as of 10:39 on 2026-09-24);
- `scripts/copyrules.py` (as of 14:27 the same day, 637 lines; it changed while this research ran, and the later additions were counted as covered);
- `references/research/copy-ai-tells.md`.

**Method.**
1. GitHub search found about 250 candidate repositories.
2. 74 of them were cloned or fetched and their SKILL.md, reference and rule files read. Four reader agents read the social, East Asian, Romance and Slavic, and Arabic, Turkish, Indonesian and South Asian projects (sections 2 and 5).
3. The data sources were read directly:
   - the current revision of Wikipedia's "Signs of AI writing";
   - the GPTZero and Pangram pages;
   - the Kobak et al. data repository, from which 2024 excess ratios were recomputed;
   - sam-paech's slop-score leaderboard.
4. Every candidate lint entry was tested three ways:
   - its regex must match the bad example and miss the good one;
   - the live `copyrules.lint_string` must miss the bad example (so the entry is really new);
   - false positives were counted on real copy.

**Corpora for the false-positive counts** (all collected by sibling research in this session):
- 1,671 brand posts from Bluesky, 2024 to 2026: Patagonia, Xbox, Substack, PlayStation, Netflix and others;
- 144 Bangladeshi big-brand ads from the Meta Ad Library: bKash, Grameenphone, Robi, Nagad, Pathao, Shwapno, foodpanda, Daraz;
- 1,544 Bangladeshi small-business ads from the same library (1,464 of them mainly in Bengali script);
- the parent's small natural and robotic test sets.

In total the note draws on 89 repositories and 7 single skill files. The readers' findings are merged below, and their candidate entries are in the JSON after deduplication.

## Key findings

1. **The loudest tell is only half covered.** The "not X but Y" family is:
   - the one tell every project lists;
   - the one tell measured in every language: 2 to 18 times the human rate in English (slop-score), 9.2 to 12.1 times in Korean (im-not-ai), 3 times per 10,000 words (Pangram).

   The lint only catches the "not just / not only" form. These all pass today:
   - "It's not about X, it's about Y."
   - "This isn't X. It's Y."
   - "The problem isn't X. It's Y."
   - "X isn't the problem. Y is."
   - "No X, no Y, just Z."
   - "doesn't just A, it Bs"
   - "It wasn't X. It wasn't Y. It was Z."
2. **The word lists match exact forms only.** "bolstered", "garnered", "showcased", "delved", "leveraging" and "unveiled" pass today. In PubMed abstracts they ran 2.4 to 12.3 times their expected 2024 frequency (Kobak data, recomputed).
3. **New phrase data.** GPTZero's AI Vocabulary page (updated September 2026, 3.3 million texts) ranks lemmatized n-grams by AI-to-human ratio. Marketing lines at 20 to 111 times the human rate are missing from the lint:
   - "an unwavering commitment", "a unique blend", "the relentless pursuit";
   - "left an indelible mark", "continue to inspire", "a significant milestone";
   - "the journey begins", "a delicate balance".
4. **Social-post formulas are the biggest gap for this skill.** Several projects now catalogue them:
   - launch intros: "Meet X, your new favorite", "Think X meets Y";
   - curatorial sign-offs: "Thank me later", "Save this for later.";
   - generic closing questions: "What do you think?";
   - the fake-casual costume: "Pro tip:", "*chef's kiss*", "(yes, really)", the self-QA volley "Is it X? Yes.";
   - the reply "validation tail": "so this one hits".

   Two authors measured their own posts. In sergebulaev/x-skills (445 top tweets), tweets with AI vocabulary earned 0.58 times the median and tweets with an em dash 0.52 times. In kirupa/KONVO (809 forum replies), the median reply was 139 characters, 57% opened straight on the content, and 78% of emoji sat at the very end.
5. **Humanizing is not slang.** A cluster of findings says over-correcting into casual register is its own tell:
   - Russell et al.: adding casual language did not hide AI text from expert readers;
   - badmuriss/unslop: more human does not mean more slang;
   - ardha27/humanizer-id: it controls "over-gaul", overdone slang;
   - harshaneel/humanize: a Slack message keeps its AI shape even with "fwiw" sprinkled in.
6. **Rewrites leave their own fingerprint.**
   - Machine editing adds filler (Shan et al. 2026).
   - A stress test of blader/humanizer found a new "humanizer voice" of fragments and staccato.
   - Pangram's study of commercial humanizers found hyphens stripped, date ranges broken and facts invented.
   - Korean rewrites injected fresh tells (im-not-ai).

   So: re-lint every rewrite; never pass client copy through third-party humanizers; never invent first-person experience.
7. **Banning the em dash displaces the rhythm.** The same punchy aside moves into colons and paired commas (kjmagnan1s/anti-slop, June 2026). Claude Opus 4.5 already uses colons 4.1 times the human rate. The lint checks colon reveals only in headlines.
8. **The judge needs guarding too.**
   - LLM judges prefer their own model family's writing (Panickssery et al., NeurIPS 2024).
   - They also prefer longer answers (length-controlled AlpacaEval).
   - Human raters agree poorly on naturalness (ICC .23 to .41 in im-not-ai).

   For `copyjudge`: use a judge from a different model family than the writer, control for length, and re-lint the judge's rewrites.
9. **Bengali now has one skill and 28 tested entries.**
   - opuu/bangla-writer (MIT, created 2026-08-25, not yet evaluated) is the only Bengali natural-writing skill found on GitHub, so copy.md section 3's "no Bengali humanizer" line is out of date.
   - No Hindi, Hinglish or Urdu humanizer exists.
   - The 14 entries transferred from other languages match 1 of 144 big-brand ads and 4.0% of 1,464 Bengali small-business ads; those ads use the em dash more often than the rest (39.0% against 31.0%).
   - Big-brand ads used an em dash in 2.8% of cases; small-business ads in 31.4%.
10. **Several classic "tells" are human in measured data. Do not lint them:**
    - "in order to", "very", "perhaps" (Wikipedia's "Signs of human writing");
    - discourse particles "just", "really", "actually" (instruction-tuned models use them at 13 to 80% of the human rate);
    - questions and metaphors in Chinese;
    - Korean 통해 and 에 대해;
    - a single em dash;
    - perfect grammar.

    stop-slop's "kill all adverbs" contradicts the data.

## 1. English skills and linters

### conorbronsdon/avoid-ai-writing
https://github.com/conorbronsdon/avoid-ai-writing · MIT · 4,702 stars · v3.36.0, pushed 2026-09-23 · read 2026-09-24

**What it is.** The most complete English audit-and-rewrite skill:
- modes: detect, rewrite, edit;
- a Node detector;
- a preservation validator;
- a hash-only human-control corpus;
- context profiles: linkedin, blog, technical-blog, investor-email, docs, casual;
- voice profiles: casual, professional, technical, warm, blunt.

**Rules.**
- **Tier 1A:** AI markers. Their "5 to 20 times" ratio is inherited from brandonwise/humanizer; the repo says it did not measure it.
- **Tier 1B:** clarity edits, explicitly not authorship evidence: utilize, in order to, due to the fact that, serves as, features, commence, ascertain, endeavor. These fired on 257 pre-2023 human paragraphs.
- **Tier 2:** flag at 2+ per paragraph.
- **Tier 3:** flag by density, about 3% of words.
- **Tier 3 phrase clusters:** 3+ distinct stock phrases in one piece. Examples: the intersection of, community-driven, user engagement.
- **An explicit instruction to match inflected forms.**
- **About 60 structural patterns.** The ones useful for social copy:
  - social endorsement closers;
  - lingering-attention claims ("the line I keep coming back to");
  - narrated candor ("to be fully transparent");
  - launch-copy introductions (Meet X, your new favorite; Think X meets Y);
  - the fake-casual register (verdict closers, six stage directions, wink asides, label prefixes, the self-QA volley);
  - negation chains;
  - performed-insight phrases, taken from Simon Willison's LLM cliché highlighter;
  - dramatized contrast against an invented crowd;
  - wall-of-text replies;
  - hashtag stuffing (6+ tags);
  - unfilled placeholders;
  - AI-tool URL parameters.
- **A "never inject" list** for the rewrite side:
  - fabricated perspective;
  - manufactured stakes ("now more than ever");
  - forced contrarianism;
  - performed candor;
  - em-dash theatrics;
  - staccato conversion;
  - invented specifics.
- **Tolerance matrix, linkedin profile.** It accepts:
  - fragments;
  - one rhetorical question as a hook;
  - bold hooks;
  - 1 or 2 end-of-line emoji;
  - "some sell".

  It skips copula avoidance, uniform paragraph length and generic-conclusion checks in short social copy.

**Evidence.**
- Human-control corpus of 376 documents from 38 sources, mostly blogs. A zero-findings rule rejected 31.4% of human documents; a budget of 6 findings rejected 1.9%.
- Cited on detector unreliability:
  - Liang et al. 2023: over 60% false positives on non-native English;
  - Jabarian and Imas 2025: over 70% misclassification by open-source detectors;
  - arXiv 2506.07001: paraphrase cuts detection by about 88%.

**New for us.**
- The whole social-closer and fake-casual set.
- Inflected forms.
- The 1A/1B split, so clarity words are not scored as AI evidence.
- A per-piece findings budget instead of zero tolerance.
- Profile-specific relaxations for short social copy.

### Nanako0129/sepia
https://github.com/Nanako0129/sepia · MIT · 2,816 stars · v0.12.2, pushed 2026-09-23 · read 2026-09-24

**What it is.** A de-AI skill with separate fiction and professional routes, and four operations: write, review, refactor, recreate. It keeps a ledger of measured sources, each with its limits stated.

**Rules.**
- **The seven edit types professional editors actually made**, from LAMP, Chakrabarty et al. (18 MFA writers, 1,057 paragraphs):

  | Edit | Share |
  |---|---|
  | awkward word choice | 28% |
  | poor structure | 20% |
  | redundant exposition | 18% |
  | cliché | 17% |

  Their edit mix was replace 74%, delete 18%, insert 8%.
- **Syntax templates** 2 to 5 times over-represented:
  - "a/the [abstract noun] of [noun]": a sense of wonder, the weight of expectation;
  - trailing participles;
  - nominalization;
  - paired abstractions.
- **An "add back" list**, because instruction-tuned models under-use these at 13 to 80% of the human rate (Reinhart et al., PNAS 2025): contractions, discourse particles, "because", "so", hedges, negation, first and second person.
- **A deletion test and a reversion test** after every refactor. Shan et al. 2026: machine editing lowers lexical density, d = -3.10, so an editor's fingerprint is the filler it adds.
- **Per-model prose layers taken from vendor prompting guides:**
  - Claude Fable 5.1: "mannered prose", a metaphor where a literal phrase exists;
  - Claude Opus 5: long written files and narrated intent;
  - GPT-6 Astra: OpenAI's own slop list, below;
  - Gemini 3 and 3.1: less verbose by default;
  - GPT-5.6: generic reassurance, praise and sign-offs.
- **The GPT-6 Astra list** names: "Bottom Line:", delve, foster, leverage, "it's worth noting", "importantly", "Question? Answer.", "This isn't about X. It's about Y.", "genuinely", hyphenated compound descriptors, "In short:", unprompted "X, not Y" contrasts, invented compound labels.
- **A false-positive whitelist:**
  - a single em dash or semicolon;
  - formal tone in a formal venue;
  - punctuation density (the measured directions contradict each other);
  - average paragraph length.

**Evidence** (ledger):
- **SlopShape** (Madler, arXiv 2609.15369, September 2026). 2,250 pre-ChatGPT company blog posts from 268 domains against 11,250 mirrors written by five frontier models. 187 structural features reached 98.0 macro-F1 on held-out companies, and 98.1 after each model reworded its own posts. The AI shape is "tidy, self-announcing".
- **Gude et al. 2026.** Sentences of 1 to 15 tokens are 32 to 33% of human news-lead sentences, against 1 to 4% for 2025 instruction-tuned models.
- **Freeburg 2026**, em dashes per 1,000 words:

  | Writer | Em dashes |
  |---|---|
  | GPT-4.1 | 10.62 |
  | Claude Opus 4.6 | 9.09 |
  | GPT-5.4 | 1.43 |
  | Human baseline (eight essays) | 3.23 |
- **Saad and Ting 2026.** A fixed 72-word marker list fell from 3.5 to 1.5 times background between 2023 and 2026. "delve" retreated after mid-2024, while "underscore" and "notably" kept rising.
- **Pangram 4 technical report.** Self-reported AUROC 0.9916.

**New for us.**
- The GPT-6 Astra slop list.
- Mannered prose as a Claude-specific tell.
- The deletion and reversion tests.
- The rule that the absence of old tells (no em dash, no delve) is not evidence of a human.

### tbhb/vale-ai-tells
https://github.com/tbhb/vale-ai-tells · MIT · 110 stars · v1.37.0, pushed 2026-09-23 · read 2026-09-24

**What it is.** A Vale style package with 137 prose rules and 15 commit-message rules. It is built for technical documentation; its own README says it is less suited to marketing.

**Rules that apply to marketing:**
- AICompoundPhrases: rich tapestry, delicate balance, paradigm shift, tipping point, sets the stage, takes center stage, a cornerstone of, the transformative power of, deeply rooted in, the hallmark of, move the needle;
- PromotionalPuffery: a hub of, a beacon of, a treasure trove of, a shining example, widely regarded as, has established itself as, continues to inspire, left an indelible mark, a lasting legacy, vibrant community;
- MarketingHeadings: The Ultimate Guide, Everything You Need to Know, The Power of, Why Choose;
- UrgencyInflation: more important than ever, the stakes have never been higher, at a crossroads;
- OpeningCliches: in this day and age, have you ever wondered, picture this;
- ClosingPleasantries: don't hesitate to reach out;
- MicDrop: "It matters.", "And it shows.", "Everything is intentional.";
- FalseExclusivity: what most people miss, the dirty little secret;
- ContrastiveFormulas, including the two-sentence "It's not about X. It's about Y.";
- PseudoCleft: "What you get is";
- IncompleteComparison: "significantly faster" with no "than".

**Evidence.** Every token is counted against pre-2022 human prose before it ships: Go and Python standard library comments, PEPs, Rust RFCs, the Go blog, Pro Git. The counts are kept in the rule comments.

**New for us.**
- The token families above.
- Its method: count a candidate against pinned pre-LLM human text before shipping it.
- A warning: its docs rules flag badge copy such as "No signup required", which is normal and useful in SaaS ads.

### eric-tramel/slop-guard
https://github.com/eric-tramel/slop-guard · MIT · 164 stars · pushed 2026-07-09 · read 2026-09-24

**What it is.** A programmatic 0 to 100 prose linter, used as an MCP server or the `sg` command. It has 24 rules and about 200 literal and structural heuristics. `sg-fit` fits the rule weights to your own corpus. A benchmark on public-domain US newspapers checks the score distribution.

**Rules.**
- **Words:** invaluable, noteworthy, pioneering, visionary, unparalleled, stunning, captivating, impactful, foundational, pinnacle, odyssey, authenticity, perseverance.
- **98 phrases**, including "can feel overwhelming", "make an informed decision", "specific needs", "great starting point", "the results will follow", "don't hesitate to".
- **Closing-aphorism rule** on the last sentence: Sometimes…, The real…, In the end…, It all comes down to….
- **Contrast pairs:** ", not X" at 2+.
- **Densities:** colons over 1.5 per 150 words; em dashes over 1 per 150 words; sentence-length variation under 0.3 across 5+ sentences.

**New for us.**
- The closing-aphorism position rule.
- Colon density.
- Fitting rule weights to a client's own corpus.

### miqdadbadjuber/anti-slop
https://github.com/miqdadbadjuber/anti-slop · MIT · 3,633 stars · pushed 2026-09-23 · read 2026-09-24

**What it is.** Rules for coding agents covering UI, code and copy. It includes a dedicated `antislop-copywriting` skill.

**Rules.**
- Em dash banned in agent-written text; a user's own sample that uses dashes goes through a "name it and ask" protocol.
- Default buttons banned: Get Started, Learn More, Try Now, Explore, Discover.
- Buzzwords banned: AI Powered, Next Generation, Intelligent, Ultimate, Powerful, Effortless.
- **Copy patterns:**
  - "Trusted by thousands" with no number;
  - persuasive-authority tropes ("the heart of the matter");
  - fake-candid openers;
  - an all-caps clause used for emphasis;
  - an actorless passive;
  - a product given a mind verb ("the dashboard understands");
  - tailing negations (", no guessing.");
  - "and everything in between";
  - fabricated testimonials;
  - dense scare quotes.
- **A "what not to flag" list.**
- **Signs of human writing to preserve:**
  - hard-to-fake specifics;
  - mixed feelings;
  - era-bound slang;
  - self-corrections.

**Evidence.** None measured; it cites Wikipedia and blader/humanizer.

**New for us.**
- Bare "Try Now", "Explore" and "Discover" as buttons.
- Mind verbs.
- "Everything in between".
- Scare quotes.
- The preserve list.

### MohamedAbdallah-14/unslop
https://github.com/MohamedAbdallah-14/unslop · MIT · 146 stars · pushed 2026-09-21 · read 2026-09-24

**What it is.** A deterministic regex rewriter plus an LLM mode, backed by 80 detector-research memos written in August 2026.

**Rules.** New phrases:
- "steeped in rich tradition", "What a wonderful…", "a leading voice on", "internationally recognized as";
- ", being a reliable platform,";
- "No X, no Y, no Z.";
- "It's not X. It's Y." across two sentences.

Its SYNTH-91 memo sorts human cues into three bins:
- **Preserve:** stance, disagreement, calibrated uncertainty, concrete specifics, uneven paragraphs.
- **Inject:** only distribution shape (sentence-length spread, contractions).
- **Never inject:** sycophancy, performative empathy, hedge stacks, performative balance.

**Evidence cited.**
- Abdulhai et al., arXiv 2603.18161: LLM edits neutralized about 70% of for-and-against stances.
- Ibrahim et al., arXiv 2507.21919: warmth-trained models made 7 to 12 points more errors.
- Liang et al. 2023: detectors flagged over half of TOEFL essays.
- EU AI Act Article 50: its transparency obligations have applied since 2 August 2026, and the Code of Practice was published on 10 June 2026.

**New for us.**
- The preserve, inject and never-inject rule.
- Blandification as a named risk for brand voice.
- The regulatory note that humanizers sold as "100% undetectable" face compliance exposure.

### adenaufal/anti-slop-writing
https://github.com/adenaufal/anti-slop-writing · MIT · 134 stars · pushed 2026-07-06 · read 2026-09-24

**What it is.** A universal system prompt with English and Indonesian versions.

**Rules.**
- Model dialects:
  - GPT-5.x, the "motivator": the negated contrast about once per paragraph; symmetric two-clause hooks ("Most people think X. The reality is Y.", "Forget X. Focus on Y."); "one thing is clear" closers.
  - Claude, the "philosopher": hedge-and-reassure stacks; an essay arc in every format.
  - Gemini: moralizing and explicit theme statements.
- Formulaic pairs: challenges and opportunities, pros and cons, risks and rewards.
- The Indonesian anti-translationese rules: over-use of "oleh" passives, "yang" relative chains, the copula "adalah", topic-comment order, pro-drop. They are summarized under section 5.

**Evidence.** Its figures (em dash 16.9 times, colon 4.1 times and semicolon 3.1 times the human rate in Claude Opus 4.5; "comprehensive" 24.5 times) trace to shandley/claude-style-guide (below). Other figures ("ensuring" 4.3 times; 82% of AI text following a four-part cadence) have no source that could be found.

**New for us.**
- The two-clause hook pattern as a fingerprint when repeated across posts.
- Formulaic pairs.
- The translationese framework, which transfers to Bengali (section 5).

**Caution.** Its "inject discourse markers" list ("Look,", "Honestly,", "The thing is") collides with other projects' fake-candid rules.

### gabelul/slopbuster
https://github.com/gabelul/slopbuster · MIT · 38 stars · pushed 2026-07-21 · read 2026-09-24

**What it is.** 152 patterns for text, code and academic writing, applied in two passes: remove the patterns, then add voice.

**Evidence.** It claims 1,000+ AI and human samples but publishes none. It notes itself that sentence-length variation did not separate its slop example (CV 0.59).

**New for us.**
- Phrases: "It goes without saying", "Needless to say", "The fact of the matter is", "For all intents and purposes", "exciting times lie ahead", "poised for growth".

**Caution.** Its voice guide tells writers to inject "I genuinely don't know how to feel about this" and "I keep coming back to…". That is the fabricated-perspective failure other projects ban.

### ehmo/slopkit (slopbeth)
https://github.com/ehmo/slopkit · MIT · 101 stars · pushed 2026-07-22 · read 2026-09-24

**Rules.**
- **Evidence-bound mode.** Vague benefits become proof gaps, never polished claims: "faster decisions", "reduced friction", "momentum", "confidence".
- **Support copy.** No added promises such as "we will follow up" unless the source makes them.
- **"Bland-clean failure".** A sentence that could move to another topic with only the nouns swapped.
- **A false-positive tracker** of plain human lines that must be left alone.

**Evidence.** On 25 real cases, five de-slop tools landed within 0.45 points of each other (23 exact ties). An earlier win rate of 0.92 was withdrawn after the authors found it counted ties as wins. Good de-slop output converges, so adding a sixth rule set has diminishing returns.

### harshaneel/humanize
https://github.com/harshaneel/humanize · MIT · 495 stars · pushed 2026-09-22 · read 2026-09-24

**Rules.**
- **Strip the RLHF "helpful assistant" register:**
  - balanced "on one hand" tradeoffs;
  - unrequested options;
  - a caveat on every claim;
  - "While I understand the appeal of X".
- **Casual (Slack) calibration:**
  - fwiw, lmk, ~60%, "~3-4 days" rather than "approximately three to four days";
  - fragments and self-corrections;
  - the report shape of accomplishment, caveat, next steps must itself break.

**Evidence cited.**
- "Base Models Look Human" (arXiv 2605.19516): detectors flag the instruction-tuned register rather than AI text as such.
- DivEye (arXiv 2509.18880): AI text keeps a uniform surprisal that survives surface rewriting.
- arXiv 2412.12710: controlled disfluencies raise perceived spontaneity in casual registers.

**New for us.**
- The spelled-out-approximation rule.
- "The shape must break", not only the words.

**Out of scope.** Its detector-evasion "advanced techniques".

### kjmagnan1s/anti-slop
https://github.com/kjmagnan1s/anti-slop · MIT · 3 stars · pushed 2026-09-18 · read 2026-09-24

**What it is.** A merge of avoid-ai-writing, humanizer and stop-slop. It keeps a dated "living corpus" of tells caught in the wild, each tagged with the mechanism that produced it, and runs weekly self-play with fresh-eyes detectors.

**Entries.**
- Anti-em-dash displacement (2026-06-21).
- The concession reflex: "To be fair, X. That said, Y."
- The validation tail in replies (2026-07-24): "[fact], so this one lands / hits / tracks".
- Mannered prose (2026-09-02).

**New for us.** Displacement as a concept: over-constraining creates new tells, so audit the output after every rule change.

### jman4162/slopscore
https://github.com/jman4162/slopscore · MIT · 2 stars · pushed 2026-09-17 · read 2026-09-24

**Rules.** Genre profiles, set by hand rather than tuned:
- **Marketing:** down-weights lexical markers and significance inflation. Its note: marketing "naturally resembles slop, so only flag severe cases".
- **Social:** down-weights formatting tells and "TL;DR". Up-weights insight signalling.

**Evidence.** False-positive rates reported for simple-English and non-native subgroups.

**New for us.** Per-genre weighting and ESL fairness reporting.

### Claude-ism projects
- **shandley/claude-style-guide** (MIT, 3 stars, results dated 2026-01-21).
  - Corpus: 201 Opus 4.5 samples (47,104 words) plus Haiku 3, Sonnet 3.7 and Sonnet 4; human baseline from Wikipedia, OpenWebText and C4; technical-writing prompts.
  - Em dashes per 1,000 characters: human 0.28, Opus 4.5 4.78 (16.8 times), Sonnet 4 0.25.
  - Opus 4.5 against the human rate: colon 4.1 times; comprehensive 24.4 times; fundamentally 17 times; nuanced 17 times (56 times in Sonnet 4); paradigm 15.1 times.
  - robust fell from 43 times (Haiku 3) to 3.1 times (Opus 4.5).
- **lavallee/claude-bingo** (MIT). A phrase bank scored against your own transcripts:
  - honesty performance: "Let me be direct", "To be clear", "I should be upfront";
  - therapy register: "I hear you", "that's a real…", "the tension here";
  - load-bearing vocabulary: "does the heavy lifting", "surface area";
  - engineering theater: "surgical", "battle-tested".
- **morganrivers/claude-wordswap** (licence unstated). A joke display hook listing 219 Claude-isms. Marketing entries: bespoke, iconic, must-see, unforgettable, rest assured, peace of mind.
- **SeanL128/deslop** (MIT). Claude-isms: "one honest caveat", "one thing worth flagging", "the shape of the problem", "your instinct was right".

**New for us.** Honesty performance and the therapy register in replies and captions. "iconic" was dropped after it hit 10 genuine brand posts.

### Unchanged since the earlier pass
**blader/humanizer** (51,731 stars; last push 2026-09-06, wording only), **hardikpandya/stop-slop** and **petergyang/no-ai-slop**: their skill files are byte-identical to the copies read that morning.

stop-slop items still absent from copyrules:
- "The uncomfortable truth is", "Let me be clear", "Make no mistake", "Full stop.";
- "[X] isn't the problem. [Y] is.";
- "The answer isn't X. It's Y.";
- "It feels like X. It's actually Y.";
- "stops being X and starts being Y";
- "Not because X. Because Y.";
- jargon: "lean into", "double down", "circle back".

### Smaller English projects (new items only)
- **apurvrdx1/tagore** (MIT, 53 stars): "blazing fast", "I'm pleased to share", "is a catalyst for".
- **Aboudjem/humanizer-skill** (MIT, 255 stars, 55 patterns): "X is the new Y", "the brutal truth", "what makes X unique".
- **kdgbalmer/ai-tells** (MIT, 35 stars): "I'm here to help", "to wrap up".
- **crimeacs/ai-tells-validator** (MIT, 21 stars; reads the live Wikipedia catalog at run time): "just checking in", "circling back", "looking forward to hearing".
- **eugeniughelbur/clearmode** (MIT, 2 stars): "crystal clear", "as we all know", "and that's a wrap".
- **woerndl/unsloppify** (licence unstated, 24 stars): "No config. No setup. No hassle.", "everything from X to Y", "Apple didn't build Uber" analogy stacking.
- **msdanyg/humanize-pro** (MIT, 13 stars): "That's the whole game", "Not the LinkedIn answer. The honest one.", "curious how others are handling this".
- **adewale/anti-slop-writing** (MIT, 18 stars): "That's not incidental. It's the design."
  - Its lessons file lists judge biases: self-preference (Panickssery, Bowman and Feng, NeurIPS 2024), length bias (Dubois et al.), style over substance (Wu and Aji), criteria drift (Shankar et al.).
  - It now requires a cross-family judge ensemble.
- **badmuriss/unslop** (licence unstated, 19 stars): a register gate. Its narrative layer was measured on fiction, so it never runs on marketing copy. Its Portuguese layer is covered under section 5.
- **Chaosman-One/Stop-Slop-v2**, **bpweber1/ai-pattern-killer**, **Hainrixz/humanizalo**: nothing new beyond the above.

## 2. Social, casual and marketing projects

A reader agent read 19 repositories for X, Instagram, LinkedIn, Reddit, short video and UGC scripts, all read on 2026-09-24. It checked them against copy.md (sections 1, 2, 5, 6 and 7), copyrules.py (the 14:27 version), copy-ai-tells.md and copy-hooks-ctas-platforms.md. 31 of its 35 candidate entries are in the JSON; the other four were folded into overlapping entries of mine. Its conflicts are listed in section 6.

### sergebulaev/x-skills
https://github.com/sergebulaev/x-skills · MIT · 99 stars · pushed 2026-09-23 · read 2026-09-24

**What it is.** Nine skills for X: post writer, thread builder, humanizer with an audit mode, reply drafter, hook extractor, repurposer, profile, planner and audience insights.

**Rules.**
- AI vocabulary is scored by density per tweet: one marker passes, two are flagged, three force a rewrite.
- 2026 model idioms: quietly, "X matters." on its own line, load-bearing, doing the heavy lifting, a signal, the work, built different.
- Removed on a single hit:
  - reveal bridges (The result?, Here's why, Stop X start Y, plot twist:);
  - every "not X, but Y";
  - sincerity announcements (real talk, full transparency, ngl, I'll say the quiet part, can I be vulnerable);
  - dead closers (Thoughts?, Let me know in the replies, Tag someone who needs this).
- Staged rhythm is banned: "No X. No Y. Just Z.", "All the X. None of the Y.", three one-word beats, a three-word punch tweet added for rhythm.
- A hollow triad (all abstract words, no name or number) is rewritten; one concrete triad per tweet may stay.
- The em dash is capped at one per tweet, not banned.
- Over-correction guard: never add fragments, hedges or confessions; keep the author's own lowercase.
- Replies: no canned "great point!", no hard sell under someone else's post, and five reply shapes (answer plus one detail, concede then sharpen, extend, lived experience, a quote that adds value).

**Evidence.** The author's own corpus of 445 top tweets (July 2026, length-controlled):
- tweets with AI vocabulary earned 0.58 times the median, tweets with an em dash 0.52 times;
- uniform rhythm earned 1.7 times the median in posts of about 75 words; varied rhythm only helped threads of about 430 words;
- 26% of top human tweets hold exactly one triad.

**New in the JSON.** Sincerity openers, reply openers (This., 100%, Couldn't agree more), the hollow-triad warning, and "All the X. None of the Y." (merged into the "No X, no Y, just Z" entry).

### sergebulaev/instagram-skills
https://github.com/sergebulaev/instagram-skills · MIT · 158 stars · pushed 2026-09-23 · read 2026-09-24

**What it is.** The same bundle rebuilt for Instagram: captions, carousels, a humanizer, hashtags, hooks and repurposing.

**Rules.**
- Emoji storms: four or more in a caption, or one on every line; the rocket, sparkles, fire and 100 run is removed as a set.
- "POV:" on something that is not a point of view; "link in bio" as filler; bait such as Double tap if you agree and Tag 3 friends who need this.
- The first 125 characters must stand alone; a save or send ask must name a reason.

**Evidence.** 284 human captions, prevalence only: 29% had an em dash, 23% a triad, 10% some AI vocabulary, and none a "not X, but Y" construction. Its hashtag file still allows 30 per post, which is out of date against copy.md's cap of 5.

**New in the JSON.** Two different "energy" emoji side by side, conditional bait, and reach-bait hashtags (#fyp, #viral).

### kirupa/KONVO
https://github.com/kirupa/KONVO · no licence · 6 stars · pushed 2026-09-16 · read 2026-09-24

**What it is.** A skill for warm technical explainers, with short-form rules for X, LinkedIn, forums, Slack, texts and email. It is the only social source measured on a real human corpus.

**Rules.**
- Short replies: match the size of the input; no headings or bullets; open by answering or by asking; one ask.
- Keep contrast inside the sentence; a run of sentences opening with But, So or However is a model habit.
- One emoji at the end, or none; never make people comment or DM to get a link.
- Email and chat: the answer or the ask goes in line 1, with no "Hope you're well" and no "I wanted to reach out".
- Applause lines: telling the reader to admire ("Sit with that for a second"), rating your own example ("deceptively powerful"), ending on a verbless slogan.
- What to add back: textured numbers (4:30am, $43), a named thing instead of a category, one aside with attitude. Never add typos.

**Evidence.** 809 of the author's forum replies, 2006 to 2026, about 27,000 words:
- median reply 139 characters, 82% under 280; median sentence 10 words;
- 57% open on the content, 22% with a question, 5% with a greeting;
- in about 1,700 sentences, "But" starts one and "However" none;
- emoji in 49% of replies, 78% of them at the very end; em dashes 0;
- 27 of the 29 words on its ban list never appear.

**New in the JSON.** The email, DM and SMS opener entry, applause lines, and the one-dense-block reply structure.

### skyf0xx/hedgehog-core-copywriting-prose-engineering
https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering · MIT · 12 stars · pushed 2026-09-22 · read 2026-09-24

**What it is.** A Node copy gate (retext, write-good, Flesch) with format rules for Meta ads, landing pages, direct response and X, looping until the script exits 0. Its tweet rules come from x-skills (MIT); its ad rules from robpalmer99's copywriting skills (CC BY 4.0).

**Rules.**
- X: 280 characters, counting each URL as 23 and each wide character as 2; more than one hashtag is an error; a link in the body is a warning.
- Meta ads: primary text 125 characters visible and 2,200 maximum, headline 27 and 40, description 30; a headline that is really a button label (Learn more, Shop now); unqualified claims (100% risk-free, results are typical).
- Vague benefits: take your X to the next level, reach new heights, of all sizes.

**Evidence.** Wikipedia, avoid-ai-writing and Meta's field specs; no engagement data.

**Caveats.** Its ad skill still teaches bucket brigades, a "Stop scrolling" hook and a "Sarah lost 23 lbs" proof line. Its age callout hook (men over 50) may break Meta's personal-attributes ad policy; that is the reader's note, not the repo's.

**New in the JSON.** X length as an error (copyrules defines PLATFORM['x']['max_chars'] but lint_caption does not enforce it), and keycap numbers, arrows and check marks used as bullets.

### wpgaurav/claude-code-skills
https://github.com/wpgaurav/claude-code-skills · MIT (red-pen has no upstream licence; the UX skills derived from impeccable are Apache-2.0) · 3 stars · pushed 2026-09-12 · read 2026-09-24

**What it is.** stop-slop, a four-tier slop-detector with a caption linter and regression tests, and red-pen, a line editor.

**Rules.**
- Production commentary in alt text and captions is a hard fail: "AI-generated", "captured with" a named tool, "not a generic mockup".
- Review slop: what sets X apart, comes packed with, won't break the bank, a go-to tool for.
- Audience hedges: for businesses of all sizes, no matter your skill level, perfect for everyone.
- Conclusion clichés: So there you have it, Final thoughts, Thanks for reading!
- Repeat thresholds: "No X. Just Y." warns at three uses; mirrored contrasts warn at two.
- Never add fragments, emotion or asymmetry just to pass a metric.

**Evidence.** The production-commentary rule was validated on 8,226 real alt and caption strings with 0 false positives. Nothing else is measured.

**New in the JSON.** The alt-text error, review slop and dead business metaphors, audience hedges and false ranges.

### vyralcontent/content-skills
https://github.com/vyralcontent/content-skills · MIT · 118 stars · pushed 2026-06-22 · read 2026-09-24

**What it is.** Hooks, captions and CTAs for TikTok, Reels and Shorts.

**Rules.**
- The bait test: does the ask want the content of the engagement, or only the act?
- Caption anti-patterns: stacked CTAs (like, save, share, follow); the CTA before the payoff; repeating the on-screen hook word for word; generic tags (#fyp, #foryou, #viral); a caption that argues the opposite of the voiceover.
- Hooks that fail: welcome and logo intros, "Hi everyone, today we're going to talk about", "You won't believe what happened next", a brand-first opener.
- CTAs that work: send to a named person, save for a named moment, comment with a stance, one ask per video.

**Evidence.** It claims a study of 200,000 viral videos but publishes no data; it cites Mosseri on sends.

**New in the JSON.** Stacked engagement verbs, channel intros and outros in scripts, vague teases.

### vstorm-co/content-skills (social skills only)
https://github.com/vstorm-co/content-skills · MIT · 24 stars · pushed 2026-04-16 · read 2026-09-24

- LinkedIn never: "I'm humbled to announce", Agree?, "I don't usually post about this, but", fake dialogue posts, "Day 1 vs Day 365" with nothing in it.
- Reddit: no fake grassroots ("Has anyone tried X? It's amazing!"); titles name the value, not the launch; disclose affiliation.
- Hacker News: no superlatives and no marketing lines such as "Join thousands of developers who" or "Built by developers, for developers".
- Its own templates recommend "Here's what nobody tells you about" and "Unpopular opinion:" hooks (see section 6).
- No evidence.

### Smaller social projects
- **marian-kamenistak/linkedin-post-writing-skill** (MIT, 40 stars). New items: "I recently had the opportunity to", "There's a common misconception about", "Here's to [outcome]!", "The journey continues", alliterative three-pillar lists. Its algorithm claims are unsourced, and its own house style uses the keycap bullets it bans.
- **kvsdileep/linkedin-writer** (no licence detected, README says MIT; 19 stars). Emphasis crutches: Let that sink in., Read that again., Full stop., Period., Make no mistake. Its "signature transitions" break its own ban list.
- **allanta8/slop-check** (MIT, 19 stars). Reply openers (Great point, Excellent take, 100%); 2026 patterns (tidy moral endings, fake specificity, a forced persona, copy that is too smooth); hollow emotion words (powerful, profound, deeply human); a gate asking whether the post takes a position someone could disagree with.
- **Varnan-Tech/reddit-post-engine** (no licence, 1 star). No product link in the body; 90/10 self-promotion; no "I came across this great tool" fake discovery; three reviewer personas (a skeptic, a moderator, a target reader).
- **yotamgutman/ai-free-writing-checklist** (no licence, 4 stars). A marketer's list: whispering, reverberate, gossamer, bustling, metropolis, "Designed to enhance", conductor and music analogies. No data.
- **willcheung/no-ai-slop-writing-skill** (MIT, 0 stars). The clearest list of fake casual: "Okay, but hear me out" as a default opener, "Plot twist" before an unsurprising fact, random lowercase, forced slang, fragments posing as personality. Its final test is whether the last sentence can be deleted.
- **Hiro-Inagawa/write-like-me** (MIT, 18 stars). Measures a writer's corpus (about 50 features per register) and enforces the profile with a checker. It blocks stance adverbs as openers (Honestly, Frankly, Interestingly, Notably). Transferable idea: block only what the brand's real posts never do, which fits copy.md section 11.
- **yamz8/x-thread-skill** (MIT, 4 stars). Four-post threads: a human moment, numbers, the link, then a behind-the-scenes reply to yourself; it flags overly clean three-word punchlines.
- **flazedude/humanized-writer** (no licence, 1 star). A long never-use list, but its templates ship "[Topic] is not about X. It's about Y." and "Stop X. Start Y.", and it suggests 2 to 3 hashtags per tweet.
- **alekhomenok/brand-voice-skill** (MIT, 0 stars). A formality score from 1 to 10 per channel (website 5, LinkedIn 7, PR 4.5), which would fit brand.json's formal_casual axis if set per platform.
- **tenfoldmarc/brand-voice-skill** (no licence, 6 stars). Transcribes a creator's reels with Whisper and writes the voice document from real transcript lines. It auto-installs ffmpeg, yt-dlp and Whisper, so run it with care.
- **R3LAMP4GO/ugc-scripts** (no licence, 0 stars; rules folder only). A scene test, doubt before the endorsement, and 150 words a minute (75 words for 30 seconds). It requires lowkey, literally, honestly, dash asides and a friend called Sarah, all of which clash with the house rules.

**Not read** (found late): rediumvex/social-media-caption-generator-claude (127 stars), realkimbarrett/advertising-skills (756 stars), Yuzzyuk/marketing-os (526 stars).

## 3. Data-backed lists

### Wikipedia, "Signs of AI writing"
Current revision 1376434705, 2026-09-24 03:34 UTC.

**New since the earlier pass:**
- **"Vague expression of connection or association"**, with examples up to August 2026: "in connection with", "associated with", "particularly associated".
- **"Y rather than X"**, noted as common in Grok output.
- **"no …, no …, just …"** as a form of "Not X, but Y".
- **"deep dive"** added to the vocabulary box, citing the Economist, July 2026.
- **Vocabulary by era:**
  - mid-2024 to mid-2025, GPT-4o: align with, bolstered, crucial, emphasizing, enhance, enduring, fostering, highlighting, pivotal, showcasing, underscore, vibrant;
  - from mid-2025, GPT-5: emphasizing, enhance, highlighting, showcasing;
  - Grok still overuses "underscore" and pseudo-scientific words: causal, empirical, correlate.
- **Em dash.** A September 2026 banner proposes moving it to "historical indicators". A July 2026 study found only Claude above professional writers.
- **Leaks:**
  - Gemini: [cite: 1];
  - Grok: grok_card;
  - DeepSeek: 【85†L261-269】;
  - Perplexity: [attached_file:1], [web:1];
  - unattributed: ":::writing{variant…}", seen from 1 June 2026.
- **A "Signs of human writing" section.** People write:
  - plain is and has;
  - wrote, moved, used, tried, died, rather than authored, relocated, utilized, attempted, passed away;
  - superlatives such as "one of the best";
  - hedges and intensifiers such as very, perhaps, tends to;
  - "in order to", "the fact that".
- **"Ineffective indicators":** perfect grammar, mixed registers, fancy prose in general, transition words on their own.

### GPTZero, AI Vocabulary
https://gptzero.me/ai-vocabulary, "Updated September 2026".

**Method.** 3.3 million texts; AI and human documents matched by subject and length. The table loads client-side; its 100 rows were read from the page's script bundle.

**Top rows (AI-to-human ratio):**

| N-gram | Ratio |
|---|---|
| provide a valuable insight | 181.5 |
| left an indelible mark | 111.2 |
| a stark reminder | 88.3 |
| a nuanced understanding | 77.3 |
| significant role in shaping | 70.2 |
| an unwavering commitment | 59.0 |
| play a pivotal role | 48.6 |
| continue to inspire | 43.5 |
| the transformative power | 42.8 |
| the relentless pursuit | 41.4 |
| serves as a reminder | 39.0 |
| a significant milestone | 37.3 |
| leave a lasting | 35.5 |
| add a layer | 35.3 |
| pave the way for the future | 32.3 |
| make an informed decision | 29.4 |
| a unique blend | 28.6 |
| the journey begins | 27.0 |
| a delicate balance | 26.2 |
| the path ahead | 26.2 |
| a new avenue | 22.1 |
| ready to embrace | 21.9 |

**Caveat.** A vendor page. No per-model or per-genre breakdown, and no published method beyond the matching.

### Pangram Labs
- **"Walking through AI's most overused phrases"** (Elyas Masrour, 21 February 2025). Multipliers against human text:

  | Phrase | Multiplier |
  |---|---|
  | as a poignant | 49,000 |
  | As a powerful reminder | 43,000 |
  | reminder of the enduring | 31,000 |
  | faced numerous challenges | 30,000 |
  | vibrant tapestry | 17,000 |
  | In the ever-evolving | 11,000 |
  | serves as a powerful | 10,000 |
  | newfound sense of purpose | 4,000 |
  | even in the face of unimaginable | 3,000 |
  | important to note | 3,000 |

- **"9 signs of AI writing"** (undated page). Per 10,000 words, AI against human:

  | Sign | AI | Human | Ratio |
  |---|---|---|---|
  | Markdown | 90 | 8 | 12x |
  | AI phrases | 30 | 3 | 12x |
  | em dashes | 17 | 2 | 10x |
  | bullet lists | 28 | 3 | 9x |
  | triads | 19 | 5 | 4x |
  | not just X but Y | 3 | 1 | 3x |
  | unusual Unicode | 71 | 28 | 3x |

  Overall emoji use is similar, but ✅ is 167 times more frequent in AI text and people favor face emoji.
- **"AI humanizers: the (slop)² problem"** (Destiny Akinode, 27 February 2026). Humanizer output:
  - removed every hyphen (194 texts with 164 hyphens produced zero);
  - broke ranges: 1861-1867 became "1861, 1867";
  - added random capitals, tense drift and invented facts.
- **AI Amazon reviews** (Max Spero, 4 May 2026).
  - 30,000 front-page reviews of 500 best-sellers; 3% (909) were AI-written.
  - 74% of AI reviews gave 5 stars, against 59% of human reviews; 10% gave 1 star, against 22%.
  - 93% of the AI reviews carried the Verified Purchase badge.
- **"How to spot AI reviews"** (Max Spero, 5 December 2023):
  - "I can't speak highly enough", "the first thing that struck me", "Highly recommend!";
  - the full product name restated;
  - an intro, then one paragraph per aspect, then a conclusion.

### Kobak et al., Science Advances 11(27), 2025
**Source.** Data repository berenslab/llm-excess-vocab (MIT; 900 excess words, 407 of them style words; PubMed yearly counts 2010 to 2024).

**Method.** Excess ratios for 2024 recomputed from the published counts: observed frequency divided by a counterfactual extrapolated from 2021 and 2022.

**2024 ratios, style words:**

| Word | Ratio | Word | Ratio |
|---|---|---|---|
| delves | 28.2 | underscores | 13.8 |
| delved | 12.3 | showcasing | 10.7 |
| meticulously | 10.5 | intricacies | 7.6 |
| surpassing | 7.1 | delving | 7.0 |
| commendable | 6.8 | excels | 5.9 |
| garnered | 5.3 | underscored | 5.1 |
| encompassing | 4.4 | offering | 4.3 |
| revolutionizing | 4.1 | formidable | 3.9 |
| showcased | 3.8 | bolstering | 3.8 |
| endeavors | 3.7 | unveiled | 3.4 |
| leveraging | 3.1 | dependable | 3.0 |
| crafting | 2.9 | seamless | 2.2 |
| impressive | 2.1 | elevate | 1.8 |
| unparalleled | 1.8 | | |

**Caveat.** Biomedical abstracts, not ads. The ratios show model preference, not marketing-copy rates.

### sam-paech: slop-score, antislop and FTPO
**slop-score** (https://github.com/sam-paech/slop-score, dual licence; live at eqbench.com/slop-score.html).
- **Score:** 60% slop-word rate, 25% "not X but Y" rate, 15% slop-trigram rate.
- **Samples:** 150 creative and 150 essay outputs per model.
- **Leaderboard** (7 November 2025):

  | Writer | Slop words per 1,000 words | "Not X but Y" per 1,000 characters |
  |---|---|---|
  | human baseline | 6.90 | 0.044 |
  | Claude Sonnet 4.5 | 9.72 | 0.171 |
  | GPT-5-mini | 15.44 | not recorded here |
  | chatgpt-4o-latest | 23.26 | 0.245 |
  | Gemini 2.5 Flash | 40.16 | not recorded here |
  | DeepSeek V3.2 | not recorded here | 0.569 |
  | Gemma 3 4B | not recorded here | 0.811 |

- **The contrast detector:** 10 surface regexes plus 35 part-of-speech patterns. They include the two-sentence "… isn't …. It's …" and the same-verb "didn't V. It V-ed".

**antislop-sampler.** Its lists are still dated 2025-04-07.

**Antislop paper** (Paech, Roush, Goldfeder, Shwartz-Ziv, arXiv 2510.15061, October 2025):
- some patterns appear over 1,000 times more often in LLM output than in human text;
- the sampler suppresses 8,000+ patterns, while token banning breaks down at about 2,000;
- FTPO fine-tuning cuts slop by 90% without hurting benchmark scores.

## 4. Skills installed on this machine

All read-only. The ECC plugin is at `~/.claude/plugins/cache/ecc/ecc/2.2.0`.

- **brand-voice (ECC).**
  - Builds a VOICE PROFILE from 5 to 20 real samples, in source-priority order.
  - Profile fields: rhythm, compression, capitalization, parentheticals, question use, claim style, preferred and banned moves, CTA rules, channel notes.
  - Hard bans: fake curiosity hooks, "not X, just Y", "no fluff", forced lowercase, LinkedIn thought-leader cadence, bait questions, "Excited to share", founder-journey filler.
  - Canonical for the other ECC writing skills. Close to copy.md §11, which already has avoid and prefer lists.
- **article-writing (ECC).**
  - Lead with the concrete thing; explain after the example.
  - Bans: "here's why this matters" as a bridge, fake vulnerability arcs, closing questions added only for engagement, biography padding.
- **content-engine (ECC).**
  - Per-platform adaptation for X, LinkedIn, short video, YouTube and newsletters.
  - Bans: forced casualness on LinkedIn; ending with a LinkedIn-style question to farm replies.
- **crosspost (ECC).**
  - Never post identical copy across platforms.
  - Threads: no fake hyper-casual creator copy. Bluesky: no feed-gaming language.
  - Bans: "Here's what I learned", "What do you think?", "link in bio" unless true, generic takeaway paragraphs.
- **marketing-campaign (ECC)** and **marketing-agent (ECC).**
  - A 5-second test for hero copy; one CTA per piece.
  - Ad claims must match landing-page claims; email subject must match body.
  - Bans: hollow social proof ("thousands trust us", "loved by students everywhere"), bait-and-switch subject lines, copy that would work for any competitor.
  - The agent sets hero headlines at 8 to 12 words, longer than copy.md's 6 to 8.
- **investor-outreach and lead-intelligence (ECC).**
  - "I'd love to connect", begging language, soft closing questions, generic admiration.
  - Visible merge fields; the same copy reused across email, LinkedIn and X.
- **brand-discovery module 50 (ECC).**
  - A 5-axis voice spectrum: adds distant to warm, conventional to irreverent, minimal to expressive.
  - A tone matrix by content type (homepage, case study, proposal, error, social).
- **design:ux-copy.** Microcopy rules:
  - errors: what happened, why, and how to fix it;
  - confirmation buttons named for the action ("Delete files", not "OK");
  - localization notes.
- **social-publisher, x-api (ECC).** Publishing only; they defer voice to brand-voice.
- **doc-coauthoring (Anthropic example skills).** A final read for "slop or generic filler".
- **bangla-voice-script** (user skill, not a plugin). Listenability rules for Bengali narration:
  - no screen-dependent words ("উপরে", "পাশে", "এই তালিকায়");
  - "would a person say this?";
  - put the key word last, where the stress falls;
  - never add facts.

  These fit the new `lint_spoken` path in copyrules.

**None of these local skills has:**
- a word list tied to measured data;
- inflected-form matching;
- a non-English rule;
- a social-reply rule beyond "no bait".

The strongest ideas to reuse are the brand-voice profile schema (source priority, split voices rather than averaging, observable banned moves) and crosspost's no-identical-copy rule.

## 5. Non-English projects

### Korean, Chinese and Japanese (from the East Asian reader)
- **epoko77-ai/im-not-ai** (Korean; MIT; 5,693 stars; pushed 2026-09-23). The best-evidenced project in the whole set.
  - Corpus: 60 AI and 60 pre-2022 human texts from 40 outlets, tested with log-likelihood G².
  - Antithesis ("A가 아니라 B"): 5.8 against 0.6 per 1,000 eojeol, 9.2 times; 11.8 times when the AI and human texts had the same task.
  - AI text lacks long sentences.
  - Comma after a connective ending: 4.84 times (KatFish).
  - "단순한 X를 넘어" ("beyond a mere X"): 0 of 60 human texts against 12 of 12 AI texts.
  - **Rules the data killed:** Korean 통해 and 에 대해, which humans use more; sentence-initial connectives; hype words.
  - A Pebblous teardown flagged 285 of 532 clean human texts until two independent signals were required.
  - Rewriting injected new tells.
  - Human agreement on naturalness was low (ICC .231 to .405).
  - Of blader/humanizer's English list translated into Korean, only "challenges remain" survived.
- **limleesol/stop-slop-ko** (MIT).
  - Its register table treats short hooks and exclamations as fine on social media while hype adjectives remain slop.
  - It exempts comment or share calls and hook questions on social platforms.
  - It deliberately does not replace Sino-Korean words with native ones.
- **LifelongLazyLearner/qu-ai-wei** (Simplified Chinese; MIT; 601 stars).
  - Reversal skeletons: 不是…而是, 不仅是…更是.
  - Era openers: 在当今, 随着…发展.
  - Jargon: 赋能, 闭环, 底层逻辑.
  - A platform file for Xiaohongshu stacked calls (点赞收藏关注), Bilibili and brand copy. Brand copy protects slogans, fragments and parallelism.
  - Never add typos, emoji, slang or feelings to seem human.
- **baibanbao/qu-ai-wei** (MIT). Merges three rule sets and settles their contradictions with the lieflat corpus (300 AI samples, 1.179 million characters, 5 models).
  - AI rates: reversal 0.70 per 1,000 characters; colon lead-ins 0.29 against 0.08.
  - Role metaphors: 12.6 times with praise words.
  - Humans use 2.6 times more numbers.
  - Measured as human, so not to be edited out: passives, questions, metaphor (2.4 times more human), and the particles 就, 很, 了.
- **tentenco/shuorenhua-zh-tw** (Traditional Chinese, Taiwan; MIT).
  - AI flavour and regional vocabulary are two separate checks; 150+ Mainland-to-Taiwan terms.
  - Taiwanese influencer phrases pass on their own and are a tell only when stacked.
  - Leftovers from script conversion; Ministry of Education punctuation.
  - This is the closest model for copy.md's Bangladesh against West Bengal axis.
- **kyaukyuai/stop-slop-ja** (MIT) and **matsuikentaro1/humanizer-japanese** (no licence file).
  - Chatbot frames: ご質問ありがとうございます, 参考になれば幸いです.
  - False agency: 数字が物語る.
  - "することができる" padding; the ではない。Yだ reversal; katakana jargon.
  - A box-drawing rule (U+2500) used as a dash.

**Gaps found in copyrules for these languages:**
- no word checks run on Hangul, Han or kana;
- the U+2500 dash passes;
- the full-width ！ is not counted;
- headline and CTA limits count spaces, so CJK needs character limits;
- the chatbot-leftover error exists for English only.

### Spanish, Portuguese, French, German, Russian and Finnish (from the Romance and Slavic reader)
**Evidence is thin.** Ten of the thirteen repositories cite no data. The only measurement is dripips/plain-prose's dash study:
- the same 14 articles in Russian, German and English;
- an English dash rule flagged all 28 Russian and German originals, none a real finding;
- dashes per 1,000 words: Russian 39.7, German 25.0.

**Findings on the lint:**
- copylint runs no word or structure checks for these languages, only punctuation, so "not just X" passes in es, pt, fr, ru and fi today.
- Two English-only notes misfire on other Latin-script languages: the CTA-verb note fires on "Pide tu cupón" and "Bestellen Sie jetzt", and the question-headline note on "¿Hambre de algo rico?". Scope both to `en`.
- The dash rule collides with grammar. The Russian dash between a noun subject and a noun predicate is grammatical, so deleting it breaks the sentence; the fix is to recast with a verb, never to swap in a spaced hyphen.

**The repositories:**
- **sohantanna/stop-slop-spanish** (MIT text, 3 stars). The richest variety layer in the batch:
  - address forms and voseo verb forms by region;
  - a word table (ordenador or computadora, móvil or celular);
  - loaded words (coger is vulgar in Mexico and the Southern Cone);
  - quote marks and decimal separators by country: Mexico, Central America and the Caribbean write decimal points, Spain and most of South America write commas;
  - the model's "neutral Spanish" is itself a tell.
- **madebydiego/humanizador** (MIT).
  - Declares a route first: text type, country, domain.
  - Country packs: Bolivia, written by a native; Mexico, researched.
  - WhatsApp replies stay messages, never sales copy. Missing data becomes "[dato por confirmar]".
  - Diminutives (cafecito, ahorita) are warmth, not errors.
  - New packs need a native author and a "do not correct" list.
- **AndreAlmeidaDC/humanizador** (licence file missing, README says MIT) and **profdorly/humanizador** (MIT), both pt-BR.
  - "Não é X, é Y" called the number-one Brazilian tell.
  - Bait transitions: "O segredo?", "o pulo do gato?".
  - Gerundismo: "vamos estar enviando".
  - One mechanical rule: remove invisible characters but keep ZWJ and ZWNJ, which Indic scripts need.
  - "através de" declared not a tell.
- **opaulomarcondes/humanizador-pt** (MIT). Its one contradiction: it swaps "crucial" for "fundamental", which other repos list as tells.
- **badmuriss/unslop**, Portuguese layer:
  - gerundismo marked critical;
  - ceremonial openings: "no cenário atual", "vale destacar que";
  - crutch words: alavancar, potencializar, jornada, ecossistema;
  - empty FOMO punchlines: "o futuro é agora", "saia na frente";
  - its warning that "more human does not mean more slang": the usual over-correction turns institutional text into WhatsApp talk.
- **captain-marketing/anti-slop-fr** and **JulienSnsnCode/anti-slop-fr** (MIT).
  - Openers: "Dans un monde en constante évolution", "On ne va pas se mentir".
  - "Que vous soyez X ou Y".
  - The CTA question "Alors, prêt à…?".
  - Calques: "plonger dans" (delve), "débloquer le potentiel".
  - The comma before "et" as an English serial-comma calque.
  - A VOICE.md field for signature expressions the model must never correct. brand.json has avoid and prefer lists but no keep list, which would protect brand slang such as জোস.
- **dripips/plain-prose** (MIT; English, Russian, German).
  - Russian officialese: данный, в рамках, в кратчайшие сроки.
  - Russian calques: мощный инструмент (powerful tool), бесшовный (seamless).
  - German Substantivstil; German loan-translations: nahtlos, ganzheitlich, Mehrwert schaffen.
  - Its note that models leave out the Russian particles ну, вот, же.
- **thevseprod/humanizer-ru** (MIT).
  - Announcing instead of saying: "Давайте разберёмся", "Погнали".
  - Keep claim words such as "first" and "record" when cutting hype.
  - A synonym swap is not a fix.
  - Never cut the CTA, price, deadline or contact line.
  - Count distinct rule families rather than total hits.
- **ormeilu/avoid-ai-writing-russian** (MIT).
  - The Russian social costume: "Сюжетный поворот:", "Встречайте:", "Сохраняйте, пригодится", "(да, серьёзно)".
  - Curly English quotes as a strong machine-translation sign.
  - Latin letters inside Russian words as the most serious tell.
- **Hakku/finnish-humanizer** (MIT).
  - Dropped pronouns and particles (-han, -pa, kyllä); officialese (kyseinen, mikäli); imported politeness.
  - "Enthusiasm is suspect": "ihan hyvä" is praise.
  - The closest structural match to Bengali in the batch.
- **jlwin/unslop_ai** (MIT). Unchanged since the earlier skim. Still unused from it:
  - "Ob Startup oder Konzern";
  - "Ich hoffe, diese E-Mail erreicht Sie wohlbehalten";
  - German number formats;
  - rotating structural moves across a series.
- **Hainrixz/humanizalo** (MIT, 90 stars). English patterns with a Spanish README; nothing new.

**Coverage gaps.** None of these covers pt-PT or fr-CA. The one pt-PT port, mariorabeloneto/evitar-escrita-ia, is covered in the next subsection; nothing covers fr-CA. copy.md §4 has no Russian or Finnish row, which the notes above could fill.

### Arabic, Hebrew, Turkish, Indonesian and multi-language ports (from the multilingual reader)
All read on 2026-09-24. Measured evidence is rare: only turkish-humanify ran blind comparisons, and only hazemshan1 tested its checks on real human text.

- **OthmanAdi/humanizer-semitic** (MIT, 7 stars, pushed 2026-08-03). Four skills on blader/humanizer's layout: MSA (28 patterns), Egyptian (25), Levantine (25) and Hebrew (35).
  - MSA: the hedges تجدر الإشارة إلى and من المهم الإشارة; the openers في الآونة الأخيرة and في ظل التطورات المتسارعة; the closer وفي الختام; تم or يتم passives above 3 per 300 words.
  - Egyptian and Levantine: the fix is grammar, not only vocabulary (the هـ future, ما...ش negation, the demonstrative after the noun). The same holds for Bengali, where the fix for bookish copy is চলিত grammar such as -নি negation.
  - Hebrew: בעולם של היום, חשוב לציין, לסיכום, and a masculine default in gender agreement.
  - Caution: it prescribes quotas (a dialect particle in every paragraph, three French words per 100 in Lebanese, stretched letters, even a curse). In brand copy that is forced casualness. Its "human" MSA and Hebrew examples contain em dashes, and its headline figures have no citation.
- **hazemshan1-rgb/humanizer-ar** (MIT, 0 stars, pushed 2026-08-17). A 27-pattern MSA catalogue with a scanner, and the most honest about evidence.
  - Inflation: نقلة نوعية, حجر الزاوية, يفتح آفاقًا; trailing مما يسلط الضوء على; the light verb قام بـ plus a verbal noun.
  - It tested its own checks on human Arabic and changed them: partial diacritics appeared on 8 to 9% of words in both AI and human samples, so that check is now informational; the tatweel check wrongly flagged the Hijri هـ.
  - It cites Almohaimeed et al. 2025: a leading detector fell from 96% to 12% accuracy on lightly polished human Arabic.
  - Lesson for Bengali: test every check on real Bangladeshi human text before it ships, as the ad corpora here do.
- **batuhan-bas/trilingua** (MIT, 2 stars, pushed 2026-09-16). Turkish, English and Arabic with a lint that only counts.
  - Turkish: the -maktadır ending on more than 20% of sentences; işlev görmektedir for "serves as"; Gelin birlikte inceleyelim; Günümüzde and Dijital çağda openers; "bir" inflation carried over from English "a".
  - Over-correction guard: forced fragments and typos are a signature too, and real grammar slips are human, so copyjudge should not count them as AI tells.
- **durmazoguzhan/turkish-humanify** (MIT, 5 stars, pushed 2026-09-04). The most rigorously tested non-English repo.
  - Blind, pre-registered comparisons: repair mode won 16 to 5 over 21 files (p = 0.027); write mode won 11 to 1 (p = 0.0032); unaided model Turkish was never ranked first in 12 tries.
  - Corporate register lost 2 to 3 until the skill stopped turning lists into prose; then it won 4 to 1. Keep offer lists as lists.
  - Sentence-length spread did not separate model from human Turkish (about 5.6 in both). Em dashes, the -DIr ending, bold, bullets and en-dash ranges did.
  - Blind judges named an added sentence-final "ama" (4 times in 400 words, none in the source) as fake. Its rule: delete every added device, and keep it only if something is lost.
  - Judges also picked a text because of three invented sentences, so fidelity must be scored before human-likeness.
- **ardha27/humanizer-id** (MIT, 0 stars, pushed 2026-08-21). Indonesian, first written for TTS narration. The clearest anti-over-slang rule in the set: heavy slang at most 1 to 2 times per paragraph, no Gen Alpha slang (skibidi, sigma) in paid copy, never mixing gue and lo with aku and kamu. Its "data-backed" claim is thin: the lexicon is a slang dictionary with formality labels, and its 20 sample dialogues come from a chatbot persona.
- **konten-studio/jekardah-writer** (MIT, 28 stars, pushed 2026-09-09). An eight-skill Indonesian desk with a truth contract: no invented proof, urgency or experience. "Don't miss out" (jangan sampai ketinggalan) without a real deadline counts as a truth violation. Never sprinkle literally, jujurly or bestie; brand captions must read clearly outside the in-group; no neighbourhood or class stereotypes. By analogy, district jokes (Noakhali, Barishal, Sylhet) should stay out of Bangladeshi brand humour; that is the reader's inference.
- **finestructure-ai/humanizer-multilingual** (MIT, 2 stars, pushed 2026-08-05). One method for ten languages: find the literal rendering of English stock units (al final del día, Découvrez, ermöglicht es Ihnen, يتيح لك, 使您能够). One stock phrase is normal; three, or one in the opening sentence, is the signal. Two cautions: all ten of its "native" rewrites end on the same "That's it" kicker, and it tells the agent to append a vendor attribution line after every pass. Import neither.
- **MADEVAL/HumanAI** (MIT, 37 stars, pushed 2026-07-12). A single prompt pipeline for nine languages. Useful: CTA pairs (Empieza ya rather than No esperes más; Jetzt starten rather than Starten Sie noch heute) and "trust killers" (nos complace, nous sommes ravis, wir freuen uns, рады предложить). Accuracy problems: its README example invents numbers, it calls « » English quotes, and its delete-on-sight lists (Además, Hoy en día) would flag ordinary human text.
- **jurigis/avoid-ai-writing-multilingual** (MIT in the LICENSE file, NOASSERTION on GitHub; 16 stars; pushed 2026-08-05). German, Romanian, Italian, French and Swedish ports of avoid-ai-writing in which every Tier 1 word needs a source. Examples: French réinventé (a practitioner count put it at 1,033 times the human rate, with no published method), German Mehrwert and Tauchen Sie ein, Italian Nel mondo odierno and Barnum lines such as ogni azienda è unica, Swedish Det handlar inte om X, utan om Y. Its method is how the Bengali lists should grow.
- **mariorabeloneto/evitar-escrita-ia** (MIT in its README and SKILL.md, NOASSERTION on GitHub; 0 stars; pushed 2026-09-03; I read it directly). The only European Portuguese port, adapted from avoid-ai-writing v3.28.0.
  - Brazilian interference in copy meant for Portugal: the gerund progressive (estamos trabalhando), sentence-initial pronouns (Me diga, Se trata de), você everywhere, Brazilian words (usuário, celular, cadastro, aplicativo, engajamento) and spellings (econômico, contato).
  - The Portuguese social costume: O detalhe?, E a melhor parte?, Reviravolta:, Guarda este post., Agradeces-me depois.
  - A false-positive section: public funding applications (FCT, Portugal 2030), legal text and academic prose legitimately use promover, dinamizar, transversal and no âmbito de.
  - Human Portuguese sentences run longer than English ones (it suggests 20 to 30 words in ordinary prose), so an English length ruler should not be imported; the variation is what matters.
  - Evidence: none measured; the avoid-ai-writing README calls its tables editorial hypotheses.
  - New in the JSON: five pt-PT entries (Brazilian words, Brazilian spelling, Brazilian grammar, the social costume, stock lines). They apply only when the target market is Portugal. fato and recepção were left out on purpose: fato means a suit in Portugal, and older pt-PT text still writes recepção.

### Bengali, Hindi and Urdu
**A Bengali natural-writing skill now exists.** My own searches missed it; the multilingual reader found it with a code search for চলিত in SKILL.md files.
- **opuu/bangla-writer** (https://github.com/opuu/bangla-writer · MIT · 0 stars · created and last pushed 2026-08-25 · read 2026-09-24). Writing, translation and review in Bengali for Bangladesh and West Bengal. Its own rubric says no evaluation has been run, so it is unscored.
  - Grammar: past negation with -নি (করিনি, not করেছিলাম না); matching honorifics (never তিনি with বলল); no mixing of সাধু and চলিত; no দ্বারা passive calques; plurals by animacy; no ষ or ণ in loanwords (পোস্ট, not পোষ্ট).
  - Cut empty framing: বর্তমান প্রেক্ষাপটে, উল্লেখ্য যে, গুরুত্বপূর্ণ ভূমিকা পালন করে, নতুন দিগন্ত উন্মোচন. Calibrate অভূতপূর্ব and বৈপ্লবিক.
  - Never manufacture naturalness: no slang, echo words (কাজটাজ) or fillers added only to sound human.
  - Orthography: no space before দাঁড়ি, never a pipe for it, লাখ and কোটি grouping (২,৪৭,৮০০), no purist coinages.
  - So copy.md section 3's line that a GitHub search found no Bengali humanizer is out of date.
- Single skill files with some Bengali guidance:
  - **timothy-agent/timothy** `skills/writing/SKILL.md` (AGPL-3.0, 58 stars): চলিত only, one form of address throughout, Bangla Academy spelling, and it flags এটি গুরুত্বপূর্ণ যে openers. It allows one em dash per short piece, which is weaker than the house rule.
  - **Ross-cripto/goza** `skills/nationalities/bangladesi/SKILL.md` (MIT, 3 stars): no forced Banglish; never infer religion, so use আসসালামু আলাইকুম only when the user sets that register. It is marked as pending native review.
  - **roy-avik/drkyana** and **bhittu21/dlas-digital-legal-aid**: no natural-Bengali rules; the legal UI register in the second is too stiff for consumer copy.

**No Hindi, Hinglish or Urdu humanizer or anti-slop skill exists** (repository and code searches on 2026-09-24, plus the top 100 humanizer and top 100 anti-slop repositories created since 2025, filtered for Indic languages). What exists:
- **Muvon/octomind-tap** (Apache-2.0, 4 stars): a short Hindi note on over-Sanskritisation and missing Hinglish, sourced only to a detector product page. Its Spanish example advises rotating synonyms, which other repos call a tell.
- **salehrifai42/roman-urdu-book** (NOASSERTION, 0 stars): a one-spelling Roman Urdu canon (mein, nahi, yeh, woh) with a linter that flags Hindi-leaning words such as prem for Urdu readers. Not a humanizer.
- **gethamster/horde** `writer-responsible-prose` (Apache-2.0, 8 stars): Indian-English rules (kindly, revert for "reply", do the needful, prepone) that also suit Bangladeshi English copy.
- **harshitj183/ai-skills** `roles/hinglish_native.md` (2 stars): a 50/50 Hinglish quota and a mandatory signature line, both anti-patterns. One useful rule: use the loanword "computer", not the coinage संगणक.
- **SahilFruitwala/content-skills** x-post-writer voice (0 stars): Hinglish only where it lands, never in a brand-trying-to-be-funny voice.
- **ajaitech/model-skills** `india-regional-slang` and **mahanteshimath/corpify**: register mirroring and profanity stripping only; nothing about AI tells.

**The Bengali entries in the JSON (28).**
- 14 transferred from other languages' measured tells: chatbot frames, শুধু X নয় without একটি, নয় বরং, the busy-age opener, the cleft আসল কথা হলো, গুরুত্বপূর্ণ ভূমিকা পালন, ", যা … নিশ্চিত করে", দ্বারা and কর্তৃক passives, "এটি একটি", অনন্য সমন্বয় and নতুন মাত্রা, FOMO calques, delve calques, the generic closing question, and উন্মোচন and আলিঙ্গন করুন.
- 3 from the Romance reader: চলুন জেনে নিই, সদয় অবগতির জন্য, and a serial comma before এবং or ও.
- 11 from the multilingual reader, mostly from bangla-writer: উল্লেখ্য যে, এটি মনে রাখা গুরুত্বপূর্ণ যে, perfect plus না, ষ or ণ in loanwords, অনুগ্রহ করে on every line, তিনি with a non-honorific verb, অভূতপূর্ব and বৈপ্লবিক, the missing hyphen before a Bengali suffix on a Latin word (Daraz এর), a space before দাঁড়ি, a pipe typed as দাঁড়ি, and Western grouping of lakh figures.

**How they behave on real ads** (144 big-brand and 1,464 small-business Bengali ads from the Meta Ad Library, collected 2026-09-24):
- the AI-shaped entries fire on 0 or 1 big-brand ad each. The 14 transferred ones match 1 big-brand ad (a foodpanda partner-recruitment line built on নতুন দিগন্ত) and 59 small-business ads (4.0%), for example "শাড়ি শুধু পোশাক নয়, এটি…", "আজকের ব্যস্ত জীবনে…" and "নতুন দিগন্ত উন্মোচন করুন";
- the small-business ads they match use the em dash more often than the rest (39.0% against 31.0%); big-brand ads use it in 2.8% of cases;
- the typographic entries also fire on human copy: a space before দাঁড়ি in 6 big-brand and 97 small-business ads, the pipe in 46 small-business ads, Western lakh grouping in 4 big-brand ads, the missing suffix hyphen in 3 big-brand and 64 small-business ads. They are house-style checks, not AI tells, so they sit at note level, except the hyphen, which copy.md section 3.3 already requires.

**Cautions from the Korean data:**
- measure before banning;
- AI tells in a language are English-shaped translationese: word order, inserted pronouns, passive করা হয়, noun chains;
- the current lexical tell is convergence on generic verbs (নিশ্চিত করা, বৃদ্ধি করা, উন্নত করা), not rare formal words;
- never strip zero-width characters, because ZWJ and ZWNJ carry meaning in Bengali (র‍্যা).

## 6. Where the sources disagree

- **Adverbs and particles.**
  - Against: stop-slop removes "really", "just", "actually".
  - For: Reinhart et al. show instruction-tuned models under-use them; baibanbao shows the same for Chinese 就 and 很.
  - Keep them, especially in casual copy.
- **Injecting voice.**
  - For: slopbuster and adenaufal advise adding first-person reactions and markers such as "Look," and "Honestly,".
  - Against: avoid-ai-writing, unslop, qu-ai-wei and im-not-ai forbid it, and a stress test showed it creates a new fingerprint.
  - For brand copy: never invent experience or feeling. Keep only the voice the source or client supplies.
- **"Unpopular opinion" and "Forget X. Focus on Y."**
  - copy.md lists these hook patterns.
  - avoid-ai-writing flags the literal "Unpopular opinion:" label; adenaufal flags the two-clause hook when it opens most pieces.
  - The pattern is fine; the literal label and repetition are the tell. The copy ledger should catch the repetition.
- **Save and send requests.**
  - A bare "Save this for later." is an AI closer (avoid-ai-writing).
  - A save request with a reason is the best-performing Instagram CTA (copy.md §6).
  - Lint only the bare form.
- **Em dash as evidence.**
  - Its value as evidence is fading: GPT-5.x rarely uses it; only Claude still exceeds professional writers.
  - Readers still notice it, and small Bangladeshi f-commerce ads use it in about 31% of cases against 2.8% for big brands.
  - The house rule stands for reader reasons, not detection reasons.
- **Sentence-length variation.**
  - For: several projects score it.
  - Against: slopbuster, lieflat (Chinese) and im-not-ai (Korean, where the signal is missing long sentences) found it weak or absent.
  - Also against: x-skills' corpus (uniform rhythm earned 1.7 times the median in short X posts) and turkish-humanify (no separation in Turkish, about 5.6 in both).
  - Keep it as a low-weight note, and skip it on X posts and threads.
- **Marketing copy "naturally resembles slop"** (slopscore). The marketing profiles in slopscore and avoid-ai-writing relax promotional rules. This skill should not relax them, because its purpose is copy that does not read like ads, but it should keep puffery at warning level, not error.

- **Em dash in social copy.**
  - x-skills and instagram-skills cap it at one rather than banning it; their corpora show dashes in 11% of top human tweets and 29% of human captions.
  - KONVO calls a blanket ban wrong, and R3LAMP4GO requires dash asides in UGC scripts.
  - These numbers only show that people use the dash too. The house ban stays for the reader reasons above.
- **Lowercase.** Native on X and Instagram for x-skills, instagram-skills and yamz8; "random lowercase" is fake casual for willcheung. Fine when the brand already writes that way, never as a humanizing trick.
- **"Not X. Y." contrast.** Recommended by alekhomenok, flazedude's templates and hedgehog's ad skill; kvsdileep allows it as a hook only. Nearly every other source bans it, and it is measured in every language, so keep it linted.
- **"Here's what nobody tells you".**
  - Recommended by vstorm and used by marian; retired by wpgaurav; KONVO and willcheung call crowd claims fake insight.
  - copy-hooks-ctas-platforms.md itself lists a "Nobody tells you..." hook, so the new false-exclusivity entry contradicts the house hooks note.
  - Decide which wins before shipping it. My suggestion: allow the hook only when the post then gives a fact that really is little known, and leave that call to the judge.
- **Comment-keyword CTAs.**
  - vyral's TikTok file endorses "Comment X if you want the rest", while its own bait check fails "Comment YES for the link".
  - KONVO says never make people comment or DM to get a link; the house hooks note lists comment-to-DM as a CTA.
  - The bait entry catches "comment YES", "me" or "1" below; "Comment GUIDE" is left to the judge.
- **Hashtags and lengths.**
  - instagram-skills still allows 30 hashtags and flazedude 2 to 3 per tweet, against copy.md's caps (5 on Instagram, 0 to 1 on X).
  - vyral says YouTube ignores every tag once a video has more than 15; the house note cites 60 from YouTube Help.
  - LinkedIn length: 150 to 300 words (vstorm), 1,800 to 2,800 characters (kvsdileep), about 1,300 (marian), 1,301 to 2,500 in copy.md. No repository cites data for any of these.
- **UGC voice.** R3LAMP4GO requires lowkey, literally, honestly and a persona called Sarah; x-skills treats added sincerity markers as tells; copyrules already warns on quotes from default names such as Sarah and Emily.
- **Meta personal attributes.** hedgehog's callout hook aimed at men over 50 may conflict with Meta's rule against ad copy that asserts or implies personal attributes such as age or health. Check that policy before adding any callout-hook rule.
- **Forced casualness in other languages.**
  - Quotas: OthmanAdi (dialect particles in every paragraph, French words in Lebanese, stretched letters), HumanAI (a fragment every 2 to 3 sentences in social copy), a 50/50 Hinglish persona.
  - Against: humanizer-id, jekardah-writer, turkish-humanify, bangla-writer, goza and SahilFruitwala.
  - The only measured evidence, turkish-humanify's blind judges, supports "against". So copy.md section 3.1's advice to add কিন্তু to a flat statement should be softened: add a particle only where it does real work.
- **Word-level disputes between languages.** None of these was linted.
  - علاوة على ذلك is wrong (OthmanAdi) or correct but overused (hazemshan1).
  - نقلة نوعية is an inflation tell (hazemshan1) or the native fix (finestructure).
  - au cœur de is flagged by jurigis and called native by finestructure; so is the "cutting-edge" family (de pointe, de ponta, all'avanguardia) between HumanAI and finestructure.
  - Formal address defaults to usted and Lei in HumanAI; finestructure and copy.md say consumer copy uses tú.
- **Synonym cycling.** Several repositories (trilingua, wpgaurav's stop-slop and the pt-PT port among them) call rotating synonyms a tell, and octomind's Spanish example recommends it. copyrules' deck `repeat` note says "vary or cut", which pushes toward cycling; change it to "cut, or keep the same word".

## 7. New rules worth adding

Every item is new against copy.md and copyrules.py as of 14:27. Items 1 to 9 and 13 to 15 have tested entries in `humanizer-skills.json`; items 10 to 12 and 16 are process and wording changes. Items 1 to 12 are ordered by expected value for short marketing and social copy; 13 to 16 came from the reader agents' batches.

**What is in the JSON.** 377 entries in 26 language codes:
- English 100 (69 of mine, 31 from the social reader), Bengali 28, cross-language (mul) 11;
- 238 in 23 other codes: fr 19, ru 19, es 18, de 18, ja 18, ko 14, zh-CN 14, pt-BR 12, tr 11, zh-TW 11, it 10, fi 10, ar 10, id 10, pt 9, he 9, zh 7, ar-EG 6, pt-PT 5, hi 2, ur 2, es-419 2, apc 2;
- levels: 11 error, 271 warning, 95 note; kinds: 347 regex, 26 structure, 3 phrase, 1 word.

**How it was checked.**
- Every regex, phrase and word entry matches its bad example and misses its good example (Python `re`; English with IGNORECASE and MULTILINE, the rest with MULTILINE and inline flags).
- Each English regex entry's evidence ends with its hit count in the 1,671 Bluesky brand posts, and each Bengali entry's with its counts in the 144 big-brand and 1,464 small-business ads.
- Duplicates were merged: when two entries in one language matched each other's bad examples, the broader one was kept; one-way overlaps were merged or trimmed by hand.
- The examples in languages other than English and Bengali were written by non-native readers. Have a native reader approve them before they ship.

1. **Close the contrast family** (§2.2, warning). Add:
   - "It's not about X, it's about Y" and "This isn't X. It's Y." without "just";
   - "The problem / answer / question isn't X. It's Y.";
   - "X isn't the problem. Y is.";
   - "It feels like X. It's actually Y.";
   - "stops being X and starts being Y";
   - "Not because X. Because Y.";
   - "It wasn't X. It wasn't Y. It was Z.";
   - "No X, no Y, just Z" and three-item "no" chains;
   - "X doesn't just A, it Bs";
   - "Don't call it X. Call it Y.";
   - a note at two or more ", not X" tails.

   Zero hits in the 1,671 brand posts.
2. **Match inflected forms of the tier-1 verbs** (bolstered, garnered, showcased, delved, leveraging, unveiled). 6 hits in the brand posts, all PlayStation and Substack product copy of the same register.
3. **Add the GPTZero and Pangram n-grams with ratios above 20** (warning). Also the heritage and tourism set: steeped in tradition, deeply rooted in, a beacon of, a treasure trove of, widely regarded as.
4. **Add a social-closer family** (warning):
   - endorsement closers;
   - generic closing questions at the end of a caption;
   - launch intros ("Meet X, your new favorite", "Think X meets Y", "Excited to share" without "we're");
   - the reply validation tail;
   - lingering-attention claims;
   - the social reader's set: conditional and keyword bait, stacked engagement verbs, reach-bait hashtags, canned reply openers, generic prompts (Thoughts?, Agree?), channel intros and outros, vague teases, applause lines.
5. **Add the fake-casual costume** (note to warning):
   - label prefixes;
   - stage directions;
   - wink asides;
   - the self-QA volley;
   - one-word verdict closers.

   Also state in copy.md §2: more human does not mean more slang; never add slang, typos, emoji or feelings to seem human.
6. **Extend chatbot and leftover checks** (error for leaks and placeholders):
   - citation markup ([cite: n], :::writing, grok_card, 【n†…】, [web:n]);
   - tool UTM parameters;
   - placeholders ([Your City], XX%, {{name}});
   - Bengali, Korean, Chinese and Japanese chatbot frames.
   - Assistant and corporate leftovers at warning level: "Don't hesitate to reach out", "Would you like me to", "Here is a revised version", "as of my last update".
7. **Add a colon-density note for body copy.** More than one colon reveal per piece, or more than 1.5 colons per 150 words. This covers the displacement that the em-dash ban causes.
8. **Add the Bengali set** (28 entries; listed in section 5): the 14 transferred calques, the 3 from the Romance reader and the 11 from bangla-writer and the multilingual reader. The typographic ones (space before দাঁড়ি, pipe for দাঁড়ি, Western lakh grouping) stay at note level because real brand ads do them too.
9. **Fix the CJK gaps and add the East Asian entries:**
   - word checks for Hangul, Han and kana;
   - the U+2500 dash;
   - the full-width ！;
   - character-based headline and CTA limits.
10. **Guard copyjudge:**
    - a judge from a different model family than the writer;
    - length normalization;
    - re-lint every judge rewrite, because rewrites inject tells;
    - report the judge's rating as a range, which copy.md already asks.
11. **Pipeline rules for copy.md §9:**
    - never pass copy through third-party humanizer tools (they strip hyphens and corrupt ranges such as ১০-১২);
    - run a deletion test on every word a rewrite adds and a reversion test on every replacement;
    - keep a per-piece findings budget for long captions rather than zero tolerance (avoid-ai-writing: zero tolerance rejected 31% of human documents).
12. **Keep these human signals unlinted:**
    - "in order to" and the other Tier 1B clarity words stay note level;
    - discourse particles;
    - single em dashes in quoted client samples (still banned in our output);
    - one short fragment;
    - one rhetorical hook question;
    - ✨, which appeared in real brand posts.
13. **Scope the English-only notes, then add the other languages.**
    - copyrules runs no word or structure checks for es, pt, fr, de, it, ru, fi, ar, he, tr, id, ko, zh or ja.
    - Its CTA-verb and question-headline notes fire on "Pide tu cupón", "Bestellen Sie jetzt" and "¿Hambre de algo rico?". Scope both to `en`.
    - Then add the 238 entries in 23 language codes. The pt-PT entries apply only when the market is Portugal; the pt-BR ones only for Brazil.
14. **Enforce the platform mechanics the lint skips** (social reader):
    - X length as an error: PLATFORM['x']['max_chars'] exists, but lint_caption does not enforce it;
    - markdown in captions, which Instagram, LinkedIn, Facebook and X do not render (warning);
    - "link in bio" on X, LinkedIn, Facebook or Threads (warning);
    - production commentary in alt text and image captions (error; 0 false positives in 8,226 real strings);
    - a hashtag inside a sentence (note only: 21 of the 1,671 brand posts do it).
15. **Add the cross-language notes** (mul): over-slanging, props that sound human from a friend but fake from a brand, performed hesitation, the "That's it" kicker, synonym cycling, explicit "we" in every sentence, stacked connectors, generic engagement questions, and lists melted into prose. Invisible characters and mixed-script look-alike letters go in at warning level.
16. **Edit copy.md, copyrules and copyjudge:**
    - copy.md section 3: replace the "no Bengali humanizer" line with a pointer to opuu/bangla-writer, noting that it is unscored;
    - copy.md section 3.1: change "add কিন্তু to a flat statement" to "add a particle only where it does real work";
    - copyrules `lint_deck`: change the repeat note's "vary or cut" to "cut, or keep the same word";
    - copyrules: skip the flat-rhythm note on X posts and threads;
    - copyjudge: score fidelity to the brief before human-likeness, because blind judges reward invented experience (turkish-humanify);
    - brand.json: add a "keep" list of signature expressions the model must never correct (from anti-slop-fr's VOICE.md), and consider a formality number per channel (alekhomenok).

## Sources
All read on 2026-09-24.

**Projects**
- https://github.com/conorbronsdon/avoid-ai-writing
- https://github.com/Nanako0129/sepia
- https://github.com/tbhb/vale-ai-tells
- https://github.com/eric-tramel/slop-guard
- https://github.com/miqdadbadjuber/anti-slop
- https://github.com/MohamedAbdallah-14/unslop
- https://github.com/adenaufal/anti-slop-writing
- https://github.com/gabelul/slopbuster
- https://github.com/ehmo/slopkit
- https://github.com/harshaneel/humanize
- https://github.com/kjmagnan1s/anti-slop
- https://github.com/jman4162/slopscore
- https://github.com/shandley/claude-style-guide
- https://github.com/lavallee/claude-bingo
- https://github.com/morganrivers/claude-wordswap
- https://github.com/SeanL128/deslop
- https://github.com/blader/humanizer
- https://github.com/hardikpandya/stop-slop
- https://github.com/petergyang/no-ai-slop
- https://github.com/apurvrdx1/tagore
- https://github.com/Aboudjem/humanizer-skill
- https://github.com/kdgbalmer/ai-tells
- https://github.com/crimeacs/ai-tells-validator
- https://github.com/eugeniughelbur/clearmode
- https://github.com/woerndl/unsloppify
- https://github.com/msdanyg/humanize-pro
- https://github.com/adewale/anti-slop-writing
- https://github.com/badmuriss/unslop
- https://github.com/Chaosman-One/Stop-Slop-v2
- https://github.com/bpweber1/ai-pattern-killer
- https://github.com/epoko77-ai/im-not-ai
- https://github.com/limleesol/stop-slop-ko
- https://github.com/LifelongLazyLearner/qu-ai-wei
- https://github.com/baibanbao/qu-ai-wei
- https://github.com/tentenco/shuorenhua-zh-tw
- https://github.com/kyaukyuai/stop-slop-ja
- https://github.com/matsuikentaro1/humanizer-japanese
**Social and casual projects** (read by the social reader)
- https://github.com/sergebulaev/x-skills
- https://github.com/sergebulaev/instagram-skills
- https://github.com/marian-kamenistak/linkedin-post-writing-skill
- https://github.com/kvsdileep/linkedin-writer
- https://github.com/allanta8/slop-check
- https://github.com/Varnan-Tech/reddit-post-engine
- https://github.com/kirupa/KONVO
- https://github.com/skyf0xx/hedgehog-core-copywriting-prose-engineering
- https://github.com/yotamgutman/ai-free-writing-checklist
- https://github.com/willcheung/no-ai-slop-writing-skill
- https://github.com/wpgaurav/claude-code-skills
- https://github.com/Hiro-Inagawa/write-like-me
- https://github.com/vstorm-co/content-skills
- https://github.com/yamz8/x-thread-skill
- https://github.com/flazedude/humanized-writer
- https://github.com/alekhomenok/brand-voice-skill
- https://github.com/tenfoldmarc/brand-voice-skill
- https://github.com/vyralcontent/content-skills
- https://github.com/R3LAMP4GO/ugc-scripts

**Spanish, Portuguese, French, German, Russian and Finnish** (read by the Romance and Slavic reader, plus evitar-escrita-ia read by me)
- https://github.com/sohantanna/stop-slop-spanish
- https://github.com/madebydiego/humanizador
- https://github.com/AndreAlmeidaDC/humanizador
- https://github.com/profdorly/humanizador
- https://github.com/opaulomarcondes/humanizador-pt
- https://github.com/mariorabeloneto/evitar-escrita-ia
- https://github.com/captain-marketing/anti-slop-fr
- https://github.com/JulienSnsnCode/anti-slop-fr
- https://github.com/dripips/plain-prose
- https://github.com/thevseprod/humanizer-ru
- https://github.com/ormeilu/avoid-ai-writing-russian
- https://github.com/Hakku/finnish-humanizer
- https://github.com/jlwin/unslop_ai
- https://github.com/Hainrixz/humanizalo

**Arabic, Hebrew, Turkish, Indonesian and multi-language ports** (read by the multilingual reader)
- https://github.com/OthmanAdi/humanizer-semitic
- https://github.com/hazemshan1-rgb/humanizer-ar
- https://github.com/batuhan-bas/trilingua
- https://github.com/durmazoguzhan/turkish-humanify
- https://github.com/ardha27/humanizer-id
- https://github.com/konten-studio/jekardah-writer
- https://github.com/finestructure-ai/humanizer-multilingual
- https://github.com/MADEVAL/HumanAI
- https://github.com/jurigis/avoid-ai-writing-multilingual

**Bengali, Hindi and Urdu**
- https://github.com/opuu/bangla-writer
- https://github.com/Muvon/octomind-tap
- https://github.com/salehrifai42/roman-urdu-book
- https://github.com/harshitj183/ai-skills (`roles/hinglish_native.md`)
- https://github.com/SahilFruitwala/content-skills (x-post-writer voice file)

**Single skill files**
- https://github.com/timothy-agent/timothy (`skills/writing/SKILL.md`)
- https://github.com/roy-avik/drkyana (`.skills/voice-and-tone/SKILL.md`)
- https://github.com/bhittu21/dlas-digital-legal-aid (`Skills/bilingual-bangla-english-ui/SKILL.md`)
- https://github.com/Ross-cripto/goza (`skills/nationalities/bangladesi/SKILL.md`)
- https://github.com/ajaitech/model-skills (`skills/india-regional-slang/SKILL.md`)
- https://github.com/gethamster/horde (`.agents/skills/writer-responsible-prose/SKILL.md`)
- https://github.com/mahanteshimath/corpify (`SKILL.md`)

**Data**
- https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing (revision 1376434705)
- https://gptzero.me/ai-vocabulary
- https://www.pangram.com/blog/walking-through-ai-phrases
- https://www.pangram.com/blog/pangram-ai-phrases
- https://www.pangram.com/signs-of-ai-writing
- https://www.pangram.com/blog/ai-humanizers-the-slop-2-problem
- https://www.pangram.com/blog/ai-amazon-reviews
- https://www.pangram.com/blog/how-to-spot-ai-reviews
- https://github.com/berenslab/llm-excess-vocab
- https://www.science.org/doi/full/10.1126/sciadv.adt3813
- https://github.com/sam-paech/slop-score
- https://eqbench.com/slop-score.html
- https://github.com/sam-paech/antislop-sampler
- https://github.com/sam-paech/auto-antislop
- https://arxiv.org/abs/2510.15061
- https://github.com/sam-paech/slop-forensics

**Papers cited through the projects** (not re-read here)
- SlopShape, arXiv 2609.15369
- StoryScope, arXiv 2604.03136
- LAMP, arXiv 2409.14509
- Reinhart et al., arXiv 2410.16107
- Russell et al., arXiv 2501.15654
- Shan et al., arXiv 2608.27855
- Gude et al., arXiv 2605.06030
- Saad and Ting, arXiv 2609.10664
- Freeburg, arXiv 2603.27006
- Pangram 4 technical report, arXiv 2607.27183
- Panickssery et al., arXiv 2404.13076
- Dubois et al., arXiv 2404.04475
- Abdulhai et al., arXiv 2603.18161
- Ibrahim et al., arXiv 2507.21919
- "Base Models Look Human", arXiv 2605.19516
- DivEye, arXiv 2509.18880
- Liang et al., arXiv 2304.02819
- Al-Shaibani and Ahmed 2025, arXiv 2505.23276
- Almohaimeed et al. 2025, arXiv 2511.16690
- Schaaff, Schlippe and Mindner 2023, arXiv 2312.04882
- Jabarian and Imas, BFI working paper 2025-116

**Local skills** (read-only)
- `~/.claude/plugins/cache/ecc/ecc/2.2.0/skills/{brand-voice,article-writing,content-engine,crosspost,marketing-campaign,investor-outreach,lead-intelligence,brand-discovery}`
- `~/.claude/plugins/cache/ecc/ecc/2.2.0/agents/marketing-agent.md`
- the synced design plugin's `ux-copy` skill
- `~/.claude/plugins/cache/anthropic-agent-skills/example-skills/34040c9c5685/skills/doc-coauthoring`
- `~/.claude/skills/bangla-voice-script`
