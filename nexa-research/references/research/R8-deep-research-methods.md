# R8. Deep research methods: deeper and more reliable than one web search

Prepared 2026-09-26 for the nexa-media skill lab, to design a research skill that feeds the script and copy skills.

**Method.** Web search until the session's shared cap ran out, then direct fetches (curl), a headless browser for public pages that refuse scripts, and live API calls. Numbers were checked in raw source text (HTML, PDF text, API JSON), never only in a tool summary. Tags: **[V]** verified in the original source; **[O]** our own test on 2026-09-26; **[R]** secondary report only; **[U]** unverified. [S#] keys point to the source list.

---

## 1. Key findings

1. Depth comes from structure: clarify, plan, split into sub-questions, run isolated parallel workers, loop on gaps, verify, write once [S1, S6, S13].
2. Effort must scale with the question, from 1 agent with 3 to 10 tool calls to 10+ subagents [S1].
3. Tokens are the main lever: token usage explained 80% of BrowseComp variance, and sampling several attempts added 15 to 25% [S1, S15].
4. The best products still mis-cite: 78 to 90% citation accuracy on DeepResearch Bench, 40 to 80% in DeepTRACE, 31% of news answers with significant sourcing problems [S16, S19, S25].
5. Recurring failures: unsupported citations, broken links, syndicated copies, content farms, stale facts, altered quotes, one-sidedness, overconfidence [S1, S15, S19, S24, S25].
6. Forgetting found information best predicted failed tasks: write findings to a ledger as you go [S18].
7. Fact-checkers read laterally and trace claims to their origin; checklists alone invite surface judgments [S36, S37].
8. Summaries are not evidence: our fetch summarizer misreported two benchmark tables [O].
9. Scholarly and statistics APIs are open; social platforms are gated (Reddit OAuth by request, YouTube captions only with edit rights) [S59, S60].
10. Content research has two extra jobs: find the story and collect the audience's own words, within privacy and copyright limits.

---

## 2. How the leading systems work and what they learned

### 2.1 Anthropic Research (multi-agent) [S1, S2, S3]
- **Architecture [V].** A lead agent saves its plan to memory (context is truncated past 200,000 tokens), spawns subagents that search in parallel with interleaved thinking, loops while gaps remain, then a separate CitationAgent maps each claim to a source location.
- **Result [V].** Opus 4 lead plus Sonnet 4 subagents beat single-agent Opus 4 by 90.2% on the internal research eval. Token usage (80%), tool-call count and model choice explained 95% of BrowseComp variance. Agents used about 4x chat tokens, multi-agent systems about 15x.
- **Lessons [V].** Give each subagent an objective, output format, tool guidance and boundaries, or work is duplicated. Scale effort: a fact takes 1 agent and 3 to 10 calls; a comparison 2 to 4 subagents with 10 to 15 calls each; complex research 10+ subagents. Start short and broad, then narrow. 3 to 5 parallel subagents, each running 3+ tools at once, cut time up to 90%. Tested, rewritten tool descriptions cut task time 40%. Subagents write to files to avoid a "game of telephone".
- **Failures [V].** 50 subagents for simple queries, endless hunts for nonexistent sources, agents distracting each other, and SEO content farms chosen over academic PDFs until source-quality heuristics were added.
- **Evaluation [V].** About 20 real queries suffice early. One LLM-judge call scores factual accuracy, citation accuracy, completeness, source quality and tool efficiency (0.0 to 1.0, pass/fail); humans still catch edge cases.
- Claude Research launched 2025-04-15 with inline citations [S2]. The Citations API cites exact sentence chunks; Endex went from 10% source hallucinations and formatting issues to 0% [S3, V].

### 2.2 OpenAI deep research [S4, S15]
- Launched 2025-02-02 on an o3 variant tuned for browsing; 5 to 30 minutes per task; 26.6% on Humanity's Last Exam; top of GAIA at launch [V].
- Stated limits: hallucinated facts and wrong inferences, it "may struggle with distinguishing authoritative information from rumors", weak calibration, citation formatting errors [V].
- Updates: o4-mini version (2025-04-24), visual browser via ChatGPT agent (2025-07-17), and on 2026-02-10 MCP connections, search restricted to trusted sites, and live interruption [V].
- BrowseComp: 51.5% against 1.9% for GPT-4o with browsing, but the worst calibration error (91%); browsing raised confidence in wrong answers [S15, V].

### 2.3 Google Gemini Deep Research [S5, S6, S7]
- December 2024: shows a multi-step plan the user can revise or approve, then runs searches that build on what it learned [V].
- December 2025 (Gemini 3 Pro, API): plans, reads, identifies knowledge gaps, searches again; 46.4% HLE, 66.1% DeepSearchQA, 59.2% BrowseComp. DeepSearchQA has 900 "causal chain" tasks in 17 fields and scores exhaustive answer sets, so recall counts [V].
- April 2026: Deep Research Max on Gemini 3.1 Pro with MCP and charts, reported at 93.3% DeepSearchQA and 54.6% HLE; vendor-run, partly on its own benchmark [S7, V].

### 2.4 Perplexity Deep Research [S8, S16, S18, S62]
- Launched 2025-02-14: dozens of searches, hundreds of sources, a plan refined as it learns, most tasks under 3 minutes; 21.1% HLE, 93.9% SimpleQA [V].
- Independent results are mixed: best citation accuracy on DeepResearch Bench (90.24%) but fewer supported citations [S16]; its standard Pro mode beat its Deep Research mode in FutureSearch tests [S18]. Cloudflare reported it using undeclared crawlers to evade no-crawl directives [S62].

### 2.5 Stanford STORM and Co-STORM [S9, S10]
- STORM (NAACL 2024) researches before writing: it finds perspectives, simulates writers with those perspectives questioning a source-grounded expert, then builds an outline. Against a RAG baseline, articles were judged better organized (+25% absolute) and broader (+10%). Editors flagged source bias transfer and over-association of unrelated facts [V].
- Co-STORM (EMNLP 2024): the user joins a discourse among expert agents and a moderator, with a mind map to surface "unknown unknowns"; 70% preferred it to a search engine, 78% to a RAG chatbot [V].

### 2.6 Open-source pipelines [S11 to S14]
- **GPT Researcher**: planner writes questions, execution agents scrape and summarize with source tracking; 20+ sources, about 3 minutes and $0.10. Deep mode explores a tree (breadth 4, depth 2, concurrency 4), about 5 minutes and $0.40 [V].
- **LangChain open_deep_research** (2025-07-16): scope (clarify, write a brief), research (supervisor plus sub-agents that clean findings), write (one shot). Parallel section writing gave disjoint reports, so multi-agent is for research only [V]. It ranked 6th on DeepResearch Bench (RACE 0.4344); the 100-task run cost $87.83 and 207 million tokens [S14, V].

### 2.7 The shared pattern

| Stage | What the strong systems do | Evidence |
|---|---|---|
| Clarify | Ask, then write a research brief | S4, S13 |
| Plan visibly | Editable multi-step plan | S5 |
| Decompose | Sub-questions and perspectives | S1, S9 |
| Breadth then depth | Short broad queries, then narrow | S1 |
| Parallel isolated workers | Separate contexts, file outputs | S1, S13 |
| Reflect and loop | Find gaps, search again | S6, S8 |
| Separate citation pass | Map claims to source locations | S1, S3 |
| Single writer | One-shot synthesis from findings | S13 |
| More compute | More tokens and sampling raise accuracy | S1, S15 |

---

## 3. What evaluations show

| Benchmark | What it tests | Key result [V] |
|---|---|---|
| GAIA, 2023 [S17] | 466 real-world assistant questions | Humans 92%, GPT-4 with plugins 15% |
| BrowseComp, 2025-04 [S15] | 1,266 hard-to-find, easy-to-verify questions | Deep Research 51.5%, o1 9.9%, GPT-4o with browsing 1.9%. Human trainers solved 29.2% and gave up on 70.8% after two hours. Voting and best-of-N added 15 to 25% |
| BrowseComp-Plus, 2025-08 [S23] | Same task style on a fixed corpus | GPT-5 55.9%; 70.1% with a better retriever and fewer searches |
| DeepResearch Bench, 2025-06 [S16] | 100 PhD-level tasks, 22 fields; report quality (RACE) and citations (FACT) | Gemini-2.5-Pro Deep Research: RACE 48.88, 111.21 supported citations per task, 81.44% citation accuracy; OpenAI 46.98, 40.79, 77.96%; Perplexity 42.25, 31.26, 90.24% |
| Deep Research Bench (FutureSearch), 2025-05 [S18] | 89 tasks on a frozen web copy | Best agent (o3) 0.51 against an estimated ceiling near 0.8 |
| Mind2Web 2, 2025-06 [S21] | 130 long tasks, agent-as-judge | Best system reached 50 to 70% of human performance in half the time |
| DeepTRACE, 2025-09 [S19] | 8 audit dimensions | One-sided, confident answers on debate questions; citation accuracy 40 to 80% |
| Search Arena, 2025-06 [S20] | 24,000+ paired conversations, about 12,000 votes | Users prefer answers with more citations even when the citations do not support the claims |
| DeepHalluBench, 2026-01 [S22] | Hallucination across plan, search, summarize | All six systems showed reliability gaps, traced mainly to hallucinations propagating through the trajectory |

**Failure modes and their evidence.**
1. **Unsupported citations.** 50 to 90% of LLM answers to medical questions were not fully supported by their cited sources; GPT-4o with web search left about 30% of statements unsupported [S26]. Across 3,113 news answers from ChatGPT, Copilot, Gemini and Perplexity (22 broadcasters, 18 countries, 14 languages), 45% had a significant issue and 31% significant sourcing problems; Gemini 76% and 72% [S25].
2. **Broken links and syndicated copies.** In 1,600 Tow Center queries asking 8 tools to identify an excerpt's headline, publisher, date and URL, over 60% of answers were wrong (Perplexity 37%, Grok 3 94%); 154 of Grok 3's 200 citations hit error pages; tools cited Yahoo or AOL copies and seemed to bypass some publishers' crawler blocks [S24].
3. **Confident wrongness.** Premium tools were more confidently wrong than free ones; all but Copilot preferred a wrong answer to admitting a limit [S24]. Deep Research had 91% calibration error [S15].
4. **Shallow sources.** Content farms over primary sources [S1]; an agent reporting a wrong number from the first leaderboard it found [S18].
5. **Outdated facts.** A top EBU error, for example naming Francis as Pope in May 2025 after his death [S25]; commentators also said OpenAI's tool missed major legal rulings and scientific updates [S44].
6. **Altered quotes.** 12% of the 1,053 EBU answers containing direct quotes had significant quote errors [S25].
7. **One-sidedness** on contested questions [S19], and **source bias transfer** [S9].
8. **Forgetting and loops.** Forgetting found information had the largest negative effect on task scores (coefficient -0.843, p=0.014), then hallucination (-0.653, p=0.055), then repeated tool calls [S18].
9. **Real costs.** Deloitte repaid the final instalment of an AU$440,000 government contract after fake citations and a made-up court quote were found; the revised report disclosed a GPT-4o tool chain [S28]. A public database lists 2,079 court decisions on hallucinated material as of 2026-09-25 [S27].

**Observed in this session [O].**
- **F1.** The fetch tool's summarizer misreported numbers twice: it gave GPT-4o 54% on BrowseComp (the paper says 0.6%) and gave Gemini's RACE overall as 49.44 (that is the readability column; overall is 48.88). Raw-text checks caught both.
- **F2.** Scripted fetches got HTTP 403 from openai.com, perplexity.ai, help.openai.com, bls.gov, loc.gov, unesdoc.unesco.org, quora.com, Reddit Help and sec.gov (sec.gov worked with a declared User-Agent); NCBI Bookshelf returned a near-empty page. A headless browser read OpenAI, Perplexity, Reddit Help, VentureBeat and the HN docs normally. Unauthenticated Semantic Scholar and GDELT returned 429.
- **F3.** The WebSearch tool has a per-session cap shared by all parallel agents: this session hit 200 of 200 after about twenty searches by this agent, because sibling research agents were searching too. The tool is also US-only.
- **F4.** Anonymous Reddit `.json` requests returned 403 or a login redirect.
- **F5.** arXiv API abstracts carry LaTeX escapes (`92\%`), which break naive exact-match quote checks.

---

## 4. Research protocol

### 4.1 Stages
| Stage | Who | Output |
|---|---|---|
| 0. Intake | Lead | `brief.yaml`: question, purpose, audience, market and languages, "as of" date, must-answer sub-questions, exclusions, tier. Ask the user only if the answer changes the plan. |
| 1. Plan | Lead | `plan.md`: 4 to 12 sub-questions; 3 to 6 perspectives (skeptic, practitioner, affected person, regulator, historian, local voice); story hypotheses; target sources per sub-question; search budget per worker. |
| 2. Breadth sweep | Lead | 5 to 10 short queries; landscape note: entities, dates, terms per language, candidate primary sources, contested points. |
| 3. Depth | One subagent per sub-question | Wide then narrow; one or more disconfirming queries; citations followed to the origin; atomic claims written to the ledger with quote, locator and date; returns a short summary and the file path. |
| 4. Collectors | Scripts in parallel | Scholarly, statistics, YouTube, voice-of-customer and trend data straight into the ledger. |
| 5. Verify | Verifier agent plus scripts | URLs fetched; quotes and numbers matched in raw text; sources graded; same-origin clusters flagged; conflicts, confidence and dates set. |
| 6. Gap and red-team pass | Lead | Hunts for weak load-bearing claims, counter-evidence, and anything newer than time-sensitive sources. |
| 7. Synthesis | One writer | Brief, fact-check table and banks built only from ledger rows. No new facts at this stage. |
| 8. Audit | Script | Every factual sentence maps to a verified ledger row, or delivery is blocked. |

### 4.2 Budgets
| Tier | Use | Subagents | Tool calls | WebSearch calls | Sources read | Time |
|---|---|---|---|---|---|---|
| Quick | One fact, a short check | 0 to 1 | 3 to 10 | up to 10 | 3 to 8 | 2 to 5 min |
| Standard | A script or article | 2 to 4 | 10 to 15 each | up to 40 | 15 to 40 | 10 to 20 min |
| Deep | Flagship video, client report | 5 to 10 | 15 to 30 each | up to 120, plus APIs | 40 to 100 | 30 to 90 min |

Bands follow Anthropic's scaling rules [S1]; times are anchored on Perplexity (under 3 minutes), GPT Researcher (3 to 5) and OpenAI (5 to 30) [S8, S11, S12, S4], with Deep longer for verification. Reserve a quarter of the search share for stages 5 and 6, and count searches centrally because parallel agents share one cap [O].

### 4.3 Stopping rules
1. **Coverage:** each must-answer sub-question has a primary source or two independent reliable ones, or is logged as a gap.
2. **Saturation:** stop a thread when three new sources in a row add nothing new.
3. **Hard caps:** per-tier limits on calls, searches, tokens and time; at a cap, stop and report gaps.
4. **Origin rule:** a load-bearing number or quote gets three targeted attempts to reach its origin, then is labeled "not traced" and never stated as fact.
5. **No ghost hunts:** a source with no trace in search, scholarly APIs or archives is reported as not found [S1].
6. **Recency:** before stopping, search for anything newer than each time-sensitive source.

---

## 5. Search playbook

**Decompose** into facts (who, what, when, where, how many), mechanisms (why, how), disagreements, people and stories, and audience questions. Perspectives surface questions one viewpoint misses [S9].

**Vary queries.** Short and broad first [S1], then synonyms, jargon and lay words, question and keyword forms, the other side ("criticism", "debunked", "myth"), document types ("report", "dataset", "transcript", `filetype:pdf`), time, place and language. Log every query and its yield.

**Operators.** Google documents `""`, `site:`, `-`, `before:`, `after:` (combinable into a date range) and `filetype:` [S29]; `intitle:` or `OR` are not on that page, so treat them as best-effort [U]. The cached-page link was retired in 2024; "About this result" now links the Wayback Machine [S33, S34]. Bing documents `site:`, `filetype:`, `ext:`, `contains:`, `intitle:`, `inbody:`, `inanchor:`, `language:`, `loc:`, `prefer:`, `feed:`, `hasfeed:`, `url:` and `ip:` [S30]. Our WebSearch tool's `allowed_domains` and `blocked_domains` are the most reliable site filter. Never scrape Google result pages: robots.txt disallows `/search` and the terms forbid automated access against robots.txt [S35]. Google's Custom Search JSON API is closed to new customers and ends 2027-01-01; Bing's Search APIs were retired 2025-08-11 [S31, S32].

**Recency.** Use `before:`/`after:` [S29], month and year in queries, and "updated" stamps; for fast topics start from the newest material.

**Multilingual.** Search in the language of the place and people involved; translate names and key terms both ways, including transliterations; target local domains with `site:` or `allowed_domains`. Bing has `language:` and `loc:` [S30]; Google has a Language filter and `lr`, `hl`, `gl` API parameters [S29, S31]. Our WebSearch is US-only [O], so native-language queries plus local site targeting are the workaround. EBU found errors in all 14 languages [S25]: verify every language equally. Transcribe Bangla with Gemini (house rule).

**Site-specific.** Official (`site:gov`, `site:gov.bd`, `site:who.int`), academic (`site:edu`, arxiv.org), communities (reddit.com, news.ycombinator.com), video. Wikipedia is a map of citations, not the citation [S47].

**Follow the citation** backward to the origin and forward to later citing work (OpenAlex, Semantic Scholar), with a Crossref retraction check [S51 to S54]; dead links go to Wayback [S58].

**Primary source behind the news.** (1) Pull identifiers: study title, DOI, report name, bill or case number, dataset, speech date. (2) Search the exact title in quotes and with `filetype:pdf`. (3) Go to the issuer: journal, agency, court, filing. (4) Compare sample, period and caveats with the news claim. (5) Cite the original publisher, never a syndicated copy [S24]. (6) For quotes, find the full transcript or video and timestamp: SIFT's "trace" step [S36].

**Finding numbers.** Ladder: official statistics release; intergovernmental databases (World Bank, UN, IMF, OECD); compilations that expose their source chain (Our World in Data metadata lists sources, last and next update); associations and filings; commercial aggregators; news mentions [S65, S66]. For Statista, trace the original source on the page; Market Insights figures are Statista's own modeled estimates whose scope differs from other publishers' and which shift when inputs change [S71]. Record value, unit, geography, period, definition, release and retrieval dates, and source chain. Never average conflicting figures.

**Query templates.**

| Goal | Templates |
|---|---|
| Landscape | `[topic] explained`; `[topic] statistics [year]`; `[topic] report filetype:pdf` |
| Origin | `"[exact study or report title]"`; `"[key phrase of claim]" site:gov`; `[org] annual report [year] filetype:pdf`; `[person] transcript [event]` |
| Disconfirm | `[claim] false`; `[claim] debunked`; `[topic] criticism`; `[topic] limitations study` |
| Recency | `[topic] after:2026-01-01`; `[topic] [month year] update` |
| Numbers | `[indicator] [country] site:worldbank.org`; `[indicator] our world in data`; `[indicator] [country] bureau of statistics` |
| Story | `[topic] oral history`; `[person] interview [year]`; `[event] court filing`; `[company] founder first customers`; `[topic] archive photo` |
| Audience | `[problem] site:reddit.com "I wish"`; `[product] "does anyone else"`; `[topic] "how do I"` |
| Local | Query in the local language plus `allowed_domains` set to national outlets and `gov.[cc]` |

---

## 6. Source evaluation and fact-checking

### 6.1 What professionals do
- **SIFT** (Mike Caulfield, 2019): Stop; Investigate the source; Find better coverage; Trace claims, quotes and media to the original context [S36].
- **Lateral reading.** Among 45 skilled users (10 PhD historians, 10 fact-checkers, 25 Stanford undergraduates), historians and students read vertically and were fooled by logos and domain names; fact-checkers left the site, opened new tabs to learn who was behind it, and reached better conclusions in a fraction of the time [S37]. The group now runs as the Digital Inquiry Group with free Civic Online Reasoning lessons [S38].
- **CRAAP** (Currency, Relevance, Authority, Accuracy, Purpose; CSU Chico) helps with currency and purpose, but judging a site by its .org or .edu domain is the vertical reading that failed above. Use it after lateral reading [S39, S37].
- **Full Fact:** where is it from, what is missing, how does it make you feel; its AI tools serve 40+ fact-checking organisations in 30 countries [S43].
- **IFCN Code:** five commitments, 31 criteria: nonpartisanship and fairness; sources detailed enough for readers to replicate the work; transparent funding and organisation; transparent methodology; open corrections [S40].
- **PolitiFact:** burden of proof on the speaker; ratings use what was known when the claim was made; the claimant is contacted and sources listed; three editors vote after asking whether it is literally true, open to other readings, evidenced, and consistent with past rulings [S41].
- **Snopes** ratings include True, Mostly True, Mixture, Mostly False, False, Miscaptioned, Correct and Incorrect Attribution, Outdated and Labeled Satire; "Unproven" was retired in favor of stating what is unknown [S42].

### 6.2 Source reliability ladder

| Tier | Type | Use |
|---|---|---|
| T1 Primary record | Law, court filing, official statistics, company filing, original dataset, peer-reviewed paper (retraction-checked), full recording | Cite for facts |
| T2 Expert synthesis | Systematic reviews, intergovernmental reports, agency explainers, compilations that show their sources | Cite; follow to T1 for key numbers |
| T3 Quality journalism | Named sources, corrections policy, IFCN signatories; reference works as maps | Cite with attribution; trace load-bearing claims |
| T4 Interested or aggregated | Press releases, company blogs, trade press, commercial aggregators | Leads; attribute ("the company says") |
| T5 Community | Reddit, HN, YouTube comments, reviews, Quora | Audience language and leads only, never facts |
| T6 Unreliable | Content farms, anonymous SEO pages, unsourced AI pages, deprecated sources, satire | Never cite; only a lead to the origin |

Grade source and claim separately, as the Admiralty code does: reliability A (completely reliable) to F (cannot be judged); credibility 1 (confirmed by independent sources) to 6 (cannot be judged). A good source can carry a weak claim [S46]. Wikipedia's perennial-sources list (generally reliable, no consensus, generally unreliable, deprecated, blacklisted) also stresses that reliability depends on the claim [S47].

### 6.3 Confidence levels
- **High:** a T1 source, or two independent T2/T3 sources agree, and no credible dispute. Copy states it plainly.
- **Medium:** one reliable secondary source, or sources agree with small differences. Copy attributes it.
- **Low:** a single weak or indirect source, or conflicting evidence. Copy leaves it out or frames it as a claim.
- **Unverified:** not traced. Never used.

For probabilities, borrow the IPCC scale: virtually certain 99 to 100%, very likely 90 to 100%, likely 66 to 100%, about as likely as not 33 to 66%, unlikely 0 to 33%, very unlikely 0 to 10%, exceptionally unlikely 0 to 1%. Keep confidence (type, amount, quality and consistency of evidence, plus agreement) separate from probability [S45].

### 6.4 Primary, secondary and independence
Primary sources are the record; secondary sources report on it. Two outlets repeating one wire story are one source; apparent confirmation from a single origin is circular reporting [S48]. The ledger clusters rows by origin: "two independent sources" means two clusters.

### 6.5 Conflicting sources
1. Check both measure the same thing (definition, place, period, method, unit).
2. Prefer the primary and latest revision; look for corrections.
3. Check independence and incentives.
4. If the conflict is real, give the range, attribute each side, explain the difference. Do not average.
5. Log it in the conflicts table.

### 6.6 Dating claims
Record event, data period, publication, last-update and retrieval dates; write "as of" in copy; re-search for newer material. PolitiFact rates claims on what was known at the time [S41], Snopes rates some "Outdated" [S42], and stale facts were a top AI error [S25].

### 6.7 Per-claim verification steps
1. Split into atomic claims. 2. Find the origin. 3. Fetch raw text. 4. Match quote or number after normalizing whitespace, quote marks and escapes. 5. Read laterally on publisher and author. 6. Seek independent confirmation. 7. Record dates. 8. Grade source, claim, confidence. 9. Archive. 10. Log it, failures included.

---

## 7. Free programmatic sources (checked 2026-09-26)

| Source | Good for | Access and limits | Terms and notes |
|---|---|---|---|
| OpenAlex [S51] | Works, authors, citations | Free account key with $1 of usage per day [V]; unauthenticated headers showed a $0.10 daily limit and $0.001 per search [O] | Data free; paid tiers for volume |
| Crossref [S52] | DOI metadata, references, retractions | No signup. Documented pools: public 5 req/s (1 concurrent), polite with `mailto` 10 req/s (3), Plus 150 [V]. List queries got 1 req/s public and 3 polite [O]. Retractions via `filter=update-type:retraction`; Retraction Watch data added 2023 [V] | 429 when exceeded; always send `mailto` |
| Semantic Scholar [S53] | Papers, citation graph | Unauthenticated calls share one pool of 1,000 req/s across all users; a key starts at 1 req/s [V]; our unauthenticated calls got 429 [O] | Get a free key |
| arXiv API [S54] | Preprints | One request every 3 seconds, one connection [V] | Metadata reuse allowed |
| PubMed E-utilities [S55] | Biomedical literature | 3 req/s without key, 10 with key [V] | Send tool and email |
| Europe PMC [S50] | Abstracts by DOI | Worked without key [O] | |
| Wikipedia and Wikidata [S56] | Facts, citation maps, pageviews | Descriptive User-Agent with contact, serial requests; Wikidata SPARQL 60 s timeout, 60 s processing per minute, 5 parallel queries per IP [V]; pageviews API worked [S70, O] | Cite underlying sources |
| Wayback Machine [S58] | Dead links, page history | Availability and CDX APIs worked [O] | |
| HN Algolia [S57] | Tech audience, launch dates | 10,000 req/hour per IP; `search_by_date`; filters on date, points, comments [V] | |
| Reddit [S59] | Community language | OAuth required, access by request under the Responsible Builder Policy; free tier 100 queries per minute per client [V]; anonymous JSON blocked [O] | Unidentified clients throttled |
| YouTube Data API [S60] | Videos, stats, comments | Default 100 `search.list` calls per day plus 10,000 units for other methods; `commentThreads.list` costs 1 unit, up to 100 per page, with a `searchTerms` filter; `captions.download` costs 200 units and needs edit permission on the video [V] | Terms forbid automated scraping without permission and harvesting identifying data such as usernames [V] |
| Gemini API with YouTube URLs [S61] | Transcripts and analysis of public videos | Preview, no charge; free tier 8 hours of YouTube video per day; public videos only [V] | Route for the agy-watch-video skill |
| Google Trends [S63, S64] | Relative search interest | Website data is a sample, normalized and rescaled 0 to 100 per request, low-volume terms show 0, not a poll [V]. Official API in alpha since 2025-07-24: 1,800 days, consistent scaling, application-gated [V]. pytrends repo archived [O] | Compare against a stable reference term |
| Google Fact Check Tools [S49] | Existing fact checks | `claims:search` with language, publisher and max-age filters [V] | ClaimReview snippets left Google Search in 2025 [S49] |
| Our World in Data [S65] | Harmonized indicators | Chart API: `.csv` (full or filtered by country and time) and `.metadata.json` with citation and update dates [V, O] | Keep the original source chain |
| World Bank API [S66] | Development indicators | Worked without key; returns a last-updated date [O] | |
| SEC EDGAR [S67] | Company filings | 10 req/s; declared User-Agent with contact email [V] | Generic agents get 403 [O] |
| GDELT DOC API [S68] | News volume | Returned 429 asking for one request every 5 seconds [O] | |

---

## 8. Research for content creation

### 8.1 Finding the story
Hunt for a **character** with a want (public or consenting), the **obstacle** and stakes, a dated **turning point** with a before-and-after number, the **surprising fact** that breaks an audience assumption (check it hardest; it spreads most), **texture** (a verbatim line, a place, an object) and **primary documents** (filings, patents, letters, archive footage). Method: a dated timeline from T1 sources, the turns marked, the people each turn affected, a document or clip per beat. Routes: Wikipedia references, Wayback CDX for how a page changed, SEC filings, HN launch threads, and agy-watch-video for timestamped quotes re-checked against the audio.

### 8.2 Audience research (voice of customer)
Copyhackers' review mining asks what the audience uses today to solve the problem and where those solutions live online, then mines those reviews and forums, not only your own product's; in its words, "Review mining data should write your copy" [S69]. Sources: YouTube comments (API), Reddit (approved OAuth or manual), HN (API), review sites and Quora (manual; Quora blocked our fetcher [O]). Extract verbatim pains, desired outcomes, objections, triggers, questions and misconceptions; count them; keep links; drop usernames. Misconceptions become myth-busting angles; repeated phrases feed natural-copy.

### 8.3 Competitor and content-gap analysis
1. Collect the top 20 to 50 videos or articles for the query set: title, angle, hook, structure, length, date, views, channel size.
2. **Outlier score** = views / median views of the channel's last 20 uploads; high scores show demand beyond channel size.
3. Mine comments with `searchTerms` for gap signals ("you didn't", "what about", "missed", "part 2", "wrong") and questions [S60].
4. Send the top 3 to 5 to agy-watch-video for hook, structure and timestamped claims, then fact-check them: competitor errors are angles, never sources.
5. Build a gap matrix: sub-topics by competitor (covered, shallow, missing, wrong) plus unanswered audience questions.

### 8.4 Trend and topic selection
Signals: Google Trends for relative interest and seasonality (5-year view, rising queries, a stable comparison term) [S63]; Wikipedia pageviews for absolute attention [S70]; YouTube Trending Charts for selected categories, not personalized, refreshed about every 30 minutes [S72]; HN activity for tech topics [S57]; GDELT news volume at a polite pace [S68]. Score topics on demand, gap, fit, timeliness and **evidence availability**; drop topics we cannot source well.

---

## 9. Output formats for writers

**Research brief** (`brief.md`)
```
# Research brief: <topic>   As of <date> | Tier <tier> | Market <country, language>
## Answer in five lines
## Key facts (each: sentence [C-id] confidence)
## Contested points (each side, sources, why they differ)
## Story angles (3), best evidence for each
## Audience words (top phrases with counts)
## Gaps in existing content
## Do not say (failed verification)
## Say carefully (medium or low confidence)
## Open questions and what could not be verified
```

**Claim ledger** (`claims.jsonl`, exported to CSV). Columns: `claim_id, claim (atomic), type (number, quote, event, definition, causal, opinion), value, unit, geography, period, source_id, url, archived_url, locator (page, section, paragraph or timestamp), verbatim (<=40 words, internal only), match (exact, fuzzy, none), published, updated, retrieved, tier, reliability (A-F), credibility (1-6), origin_cluster, confirmations, confidence, checked_by, notes, used_in`.
Example row, built from a live call [O]:
```
{"claim_id":"C014","claim":"Bangladesh's population was 173,562,364 in 2024","type":"number",
 "value":173562364,"unit":"people","geography":"BGD","period":"2024","source_id":"S66",
 "url":"https://api.worldbank.org/v2/country/BGD/indicator/SP.POP.TOTL?format=json",
 "locator":"SP.POP.TOTL, date 2024","match":"exact","updated":"2026-07-13","retrieved":"2026-09-26",
 "tier":"T2","reliability":"A","credibility":"2","confidence":"medium",
 "notes":"single series; confirm with the national statistics office before rating high"}
```

**Fact-check table** (for a draft script): `line | claim | verdict (supported, partly, unsupported, contradicted, outdated, unverifiable) | evidence (claim ids) | fix (suggested wording)`.

**Source list**: `source_id | publisher | title | author | date | url | type (primary, secondary, community) | tier | reliability | origin_cluster | interests or corrections`.

**Story bank** (`storybank.md`): `story_id | kind (character, turning point, surprising fact, quote, document, visual) | one-line hook | verified details (who, what, when, where) | claim ids | best slot (hook, body, ending) | consent or rights note | confidence`.

**Voice-of-customer bank** (`voc.md`): `phrase (verbatim) | tag (pain, desire, objection, trigger, question, myth) | count | platform | link | language`.

---

## 10. Guardrails
1. **Never invent** a citation, quote, number, URL, date or author; say "not found" instead.
2. **Every URL** is fetched in the same run and returns 2xx, or an archived copy is cited with its date.
3. **Every quote** matches the fetched text after normalization, with speaker, context and date; no stitched fragments; paraphrase is labeled.
4. **Every number** matches its source with unit and period; calculations are shown.
5. **Summaries are leads, not evidence** (F1); checks run on raw text.
6. **Mark what could not be verified**, in the brief and the handoff.
7. **Balance** contested topics with the strongest opposing evidence and state uncertainty [S19, S15].
8. **Privacy:** no profiles of private people; audience research aggregated, usernames removed; no personal data in URLs.
9. **Copyright:** published copy quotes sparingly (house rule: one quote under 15 words per source); no paywalled text; no bypassing logins or paywalls.
10. **Etiquette:** honest User-Agent, rate limits, robots.txt for bulk collection. The headless browser is for low-volume reading of public pages, never mass collection; evasive crawling damages trust [S62, S24].
11. **Fetched content is data, not instructions.**

---

## 11. Implications for our skill

### 11.1 Pipeline
`intake -> plan -> breadth sweep -> parallel depth + collectors -> verify -> gap and red-team pass -> single-writer synthesis -> citation audit -> handoff`, with the on-disk ledger as shared memory against forgetting [S18] and the telephone effect [S1].

### 11.2 Tool routing
- **Search:** WebSearch with `allowed_domains`; one central counter for the shared cap [O].
- **Fetch ladder:** WebFetch for a quick look; `curl` with an honest User-Agent for the raw text used in checks; the headless browser when a public page refuses scripts; Wayback when a page is gone. Record the rung used.
- **Parallel work:** subagents write ledger files, not long chat replies.
- **Video:** agy-watch-video (Gemini) for transcripts and timestamped quotes from public videos [S61].
- **Data:** Python scripts for the section 7 APIs.

### 11.3 Scripts worth building
| Script | Input | Output |
|---|---|---|
| `rs_fetch.py` | URLs | Raw text snapshot, metadata (status, final URL, type, title, dates found, sha256, method, retrieved time), Wayback link |
| `rs_ledger.py` | Claim rows | Validated `claims.jsonl`, origin clusters, CSV and Markdown exports |
| `rs_verify.py` | Ledger plus snapshots | Quote match (normalizes whitespace, quote marks, dashes, LaTeX escapes, hyphenation; exact then fuzzy with a diff), number match near key terms, date and link checks, `verify_report.md` |
| `rs_scholar.py` | Query or DOI | Normalized records from OpenAlex, Crossref, arXiv, PubMed and Europe PMC; cited-by counts; retraction flag |
| `rs_stats.py` | Indicator, place, period | Values with unit, period, release date and source chain from OWID and the World Bank, written to the ledger |
| `rs_youtube.py` | Topic queries | Competitor table with outlier scores, gap comments via `searchTerms`, a shortlist for agy-watch-video |
| `rs_voc.py` | Comments, threads, review exports | Tagged phrase bank with counts and links, usernames removed, Bangla supported |
| `rs_trends.py` | Terms | Wikipedia pageviews, HN activity by month, optional Trends CSV import; seasonality and momentum table with caveats |
| `rs_audit.py` | Final brief or script plus ledger | Sentence-to-claim map; fails on unsupported sentences, uncited numbers, long quotes, low or unverified claims stated as fact, dead links |
| `rs_budget.py` | Calls by agent | Shared counter with a warning at 75% and fallback routing to APIs and direct fetches |

### 11.4 Quality gates
- **G1 Plan** on disk before searching. **G2 Coverage:** each must-answer sub-question answered or logged as a gap.
- **G3 Citations:** 100% of cited claims pass quote or number matching; the best products sit at 78 to 90% [S16], so this is where we beat them.
- **G4 Independence:** each key claim has a T1 source or two origin clusters. **G5 Recency:** time-sensitive claims carry "as of" and a later-update search.
- **G6 Balance:** contested topics include the strongest counter-evidence. **G7 Links:** none dead; each archived.
- **G8 Privacy and copyright** as in section 10.
- **G9 Judge:** Anthropic's rubric (factual accuracy, citation accuracy, completeness, source quality, tool efficiency; 0.0 to 1.0 with pass or fail) per run, plus about 20 real requests rerun on every skill change [S1].
- **G10 Handoff:** writers get only high and medium claims with wording guidance, plus the do-not-say list.

### 11.5 Starting defaults
Standard for a normal script: 3 subagents, about 12 calls each, 30 searches, 20 minutes, one verification pass. Deep for flagship or client work: 6 to 8 subagents, a separate verifier, a red-team pass, a second audit. Quick for single facts inside other skills.

---

## Sources
All accessed 2026-09-26. [V] unless marked.

- S1. Anthropic Engineering, "How we built our multi-agent research system", https://www.anthropic.com/engineering/multi-agent-research-system, 2025-06-13.
- S2. Anthropic, "Claude takes research to new places", https://claude.com/blog/research, 2025-04-15.
- S3. Anthropic, "Introducing Citations on the Anthropic API", https://claude.com/blog/introducing-citations-api, January 2025 (launch covered by Simon Willison on 2025-01-24; the page now shows 2025-06-23).
- S4. OpenAI, "Introducing deep research", https://openai.com/index/introducing-deep-research/, 2025-02-02, updated 2026-02-10 (read in browser).
- S5. Google, "Gemini: Try Deep Research and Gemini 2.0 Flash Experimental", https://blog.google/products/gemini/google-gemini-deep-research/, 2024-12-11.
- S6. Google (L. Haas, S. Basu Mallick), "Build with Gemini Deep Research", https://blog.google/innovation-and-ai/technology/developers-tools/deep-research-agent-gemini-api/, 2025-12-11.
- S7. VentureBeat (M. Nuñez), "Google's new Deep Research and Deep Research Max agents can search the web and your private data", https://venturebeat.com/technology/googles-new-deep-research-and-deep-research-max-agents-can-search-the-web-and-your-private-data, 2026-04-21 (read in browser).
- S8. Perplexity, "Introducing Perplexity Deep Research", https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research, 2025-02-14 (read in browser).
- S9. Shao et al., "Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models" (STORM), NAACL 2024, https://arxiv.org/abs/2402.14207.
- S10. Jiang et al., "Into the Unknown Unknowns" (Co-STORM), EMNLP 2024, https://arxiv.org/abs/2408.15232.
- S11. GPT Researcher docs, "Introduction", https://docs.gptr.dev/docs/gpt-researcher/getting-started/introduction.
- S12. GPT Researcher docs, "Deep Research", https://docs.gptr.dev/docs/gpt-researcher/gptr/deep_research.
- S13. LangChain, "Open Deep Research", https://www.langchain.com/blog/open-deep-research, 2025-07-16.
- S14. langchain-ai, open_deep_research README, https://github.com/langchain-ai/open_deep_research, updates of 2025-08-02 and 2025-08-07.
- S15. Wei et al. (OpenAI), "BrowseComp", https://arxiv.org/abs/2504.12516, 2025-04-16.
- S16. Du et al., "DeepResearch Bench", https://arxiv.org/abs/2506.11763, 2025-06-13 (Table 1 read in HTML).
- S17. Mialon et al., "GAIA: a benchmark for General AI Assistants", https://arxiv.org/abs/2311.12983, 2023-11-21.
- S18. Bosse et al. (FutureSearch), "Deep Research Bench: Evaluating AI Web Research Agents", https://arxiv.org/abs/2506.06287, 2025-05-06.
- S19. Venkit et al., "DeepTRACE", https://arxiv.org/abs/2509.04499, 2025-09-02.
- S20. Miroyan et al., "Search Arena: Analyzing Search-Augmented LLMs", https://arxiv.org/abs/2506.05334, 2025-06-05.
- S21. "Mind2Web 2: Evaluating Agentic Search with Agent-as-a-Judge", https://arxiv.org/abs/2506.21506, 2025-06-26.
- S22. "Why Your Deep Research Agent Fails? On Hallucination Evaluation in Full Research Trajectory", https://arxiv.org/abs/2601.22984, 2026-01-30.
- S23. "BrowseComp-Plus", https://arxiv.org/abs/2508.06600, 2025-08-08.
- S24. Columbia Journalism Review, Tow Center (K. Jaźwińska, A. Chandrasekar), "AI Search Has a Citation Problem", https://www.cjr.org/tow_center/we-compared-eight-ai-search-engines-theyre-all-bad-at-citing-news.php, 2025-03-06.
- S25. EBU and BBC, "News Integrity in AI Assistants", https://www.ebu.ch/Report/MIS-BBC/NI_AI_2025.pdf, October 2025.
- S26. Wu et al., "An automated framework for assessing how well LLMs cite relevant medical references", Nature Communications, DOI 10.1038/s41467-025-58551-6, 2025-04-16 (abstract via Europe PMC API).
- S27. D. Charlotin, "AI Hallucination Cases Database", https://www.damiencharlotin.com/hallucinations/, updated 2026-09-25.
- S28. The Register, "Deloitte refunds Australian government over AI in report", https://www.theregister.com/2025/10/06/deloitte_ai_report_australia/, 2025-10-06.
- S29. Google Search Help, "Refine Google searches", https://support.google.com/websearch/answer/2466433.
- S30. Microsoft Support, "Advanced search keywords" (Bing), https://support.microsoft.com/en-us/bing/advanced-search-keywords.
- S31. Google for Developers, Custom Search JSON API overview and `cse.list`, https://developers.google.com/custom-search/v1/overview.
- S32. Microsoft Learn, "Bing Search APIs retiring on August 11, 2025", https://learn.microsoft.com/en-us/lifecycle/announcements/bing-search-api-retirement.
- S33. 9to5Google, "Google Search 'cached' link is officially dead", https://9to5google.com/2024/02/02/google-search-cached-link/, 2024-02-02.
- S34. Internet Archive Blogs, "New Feature Alert: Access Archived Webpages Directly Through Google Search", https://blog.archive.org/2024/09/11/new-feature-alert-access-archived-webpages-directly-through-google-search/, 2024-09-11.
- S35. Google, robots.txt (https://www.google.com/robots.txt) and Terms of Service (https://policies.google.com/terms), effective 2026-07-30.
- S36. M. Caulfield, "SIFT (The Four Moves)", Hapgood, https://hapgood.us/2019/06/19/sift-the-four-moves/, 2019-06-19.
- S37. S. Wineburg, S. McGrew, "Lateral Reading and the Nature of Expertise", Teachers College Record 121(11), DOI 10.1177/016146811912101102, 2019 (abstract via Crossref API).
- S38. Digital Inquiry Group (formerly Stanford History Education Group), https://www.inquirygroup.org/ and https://cor.inquirygroup.org/.
- S39. Meriam Library, CSU Chico, "Evaluating Information: Applying the CRAAP Test", https://library.csuchico.edu/sites/default/files/craap-test.pdf (undated).
- S40. IFCN, "The commitments of the Code of Principles", https://ifcncodeofprinciples.poynter.org/the-commitments.
- S41. PolitiFact, "The Principles of the Truth-O-Meter", https://www.politifact.com/article/2018/feb/12/principles-truth-o-meter-politifacts-methodology-i/ (living page).
- S42. Snopes, "Fact Check Ratings", https://www.snopes.com/fact-check-ratings/, updated 2026-05-07.
- S43. Full Fact, "Misinformation Toolkit", https://fullfact.org/toolkit/ (2026-05-28), and "Full Fact AI", https://fullfact.org/ai/.
- S44. The Conversation (University of Sydney authors), "OpenAI's new 'deep research' agent is still just a fallible tool, not a human-level expert", https://theconversation.com/openais-new-deep-research-agent-is-still-just-a-fallible-tool-not-a-human-level-expert-249496, 2025-02-12 (commentary).
- S45. IPCC (Mastrandrea et al.), "Guidance Note for Lead Authors of the IPCC Fifth Assessment Report on Consistent Treatment of Uncertainties", https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf, July 2010.
- S46. Wikipedia, "Admiralty code", https://en.wikipedia.org/wiki/Admiralty_code, revision of 2026-03-10.
- S47. Wikipedia, "Reliable sources/Perennial sources", https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources.
- S48. Wikipedia, "Circular reporting", https://en.wikipedia.org/wiki/Circular_reporting.
- S49. Poynter (A. D. Holan), "Google backs away from search result snippets that address falsehoods", https://www.poynter.org/ifcn/2025/google-claimreview-fact-checks-snippets-removed/, 2025-07-21; Google Fact Check Tools API `claims:search`, https://developers.google.com/fact-check/tools/api/reference/rest/v1alpha1/claims/search.
- S50. Europe PMC REST API, query used: https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41467-025-58551-6&resultType=core&format=json [O].
- S51. OpenAlex Help Center, "Pricing", https://help.openalex.org/access/pricing/, plus API response headers [O].
- S52. Crossref, "Access and authentication", https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/; "Retraction Watch", https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/; blog of 2023-09-12, https://www.crossref.org/blog/news-crossref-and-retraction-watch/.
- S53. Semantic Scholar, "Academic Graph API", https://www.semanticscholar.org/product/api.
- S54. arXiv, "Terms of Use for arXiv APIs", https://info.arxiv.org/help/api/tou.html.
- S55. NCBI Insights, "New API Keys for the E-utilities", https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/.
- S56. Wikimedia Foundation, "User-Agent policy", https://foundation.wikimedia.org/wiki/Policy:User-Agent_policy; MediaWiki, "API:Etiquette", https://www.mediawiki.org/wiki/API:Etiquette; "Wikidata Query Service/User Manual", https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual.
- S57. Hacker News Search API (Algolia), https://hn.algolia.com/api (read in browser).
- S58. Internet Archive, "Wayback Machine APIs", https://archive.org/help/wayback_api.php.
- S59. Reddit Help, "Reddit Data API Wiki", https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki, updated about May 2026 (read in browser).
- S60. YouTube Data API docs: https://developers.google.com/youtube/v3/getting-started, https://developers.google.com/youtube/v3/docs/commentThreads/list, https://developers.google.com/youtube/v3/docs/captions/download; YouTube Terms of Service, https://www.youtube.com/static?template=terms.
- S61. Google AI for Developers, "Video understanding" (YouTube URLs), https://ai.google.dev/gemini-api/docs/video-understanding.
- S62. Cloudflare Blog, "Perplexity is using stealth, undeclared crawlers to evade website no-crawl directives", https://blog.cloudflare.com/perplexity-is-using-stealth-undeclared-crawlers-to-evade-website-no-crawl-directives/, 2025-08-04.
- S63. Google Trends Help, "FAQ about Google Trends data", https://support.google.com/trends/answer/4365533; pytrends repository status via GitHub API (archived) [O].
- S64. Google Search Central Blog, "Introducing the Google Trends API (alpha)", https://developers.google.com/search/blog/2025/07/trends-api, 2025-07-24.
- S65. Our World in Data, "Charts API", https://docs.owid.io/projects/etl/api/chart-api/.
- S66. World Bank Indicators API, https://api.worldbank.org/v2/country/BGD/indicator/SP.POP.TOTL?format=json [O].
- S67. U.S. SEC, "Accessing EDGAR Data", https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data (needs a declared User-Agent).
- S68. GDELT DOC 2.0 API, https://api.gdeltproject.org/api/v2/doc/doc [O].
- S69. Copyhackers (J. Wiebe), "Amazon review mining for copywriting", https://copyhackers.com/2014/10/amazon-review-mining/.
- S70. Wikimedia REST API, pageviews per article, query used: https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Deep_research/monthly/20250101/20260831 [O].
- S71. Statista, "Market Insights methodology", https://www.statista.com/outlook/methodology/.
- S72. YouTube Help, "Trending Charts on YouTube", https://support.google.com/youtube/answer/7239739.

## Not verified in this session
- Google operators beyond the official list (`intitle:`, `OR`, `AROUND`) and how reliably they work today [U].
- The status of the Google Trends API after mid-2026: secondary reports in August 2026 said it was still alpha [R].
- Reverse image search tools (Google Lens, TinEye), the Library of Congress and UNESCO pages, and Quora's and Amazon's terms: the relevant pages refused our fetcher or were not checked [U].
- Current Reddit approval rules beyond the Data API Wiki, and BLS API quotas (page returned 403) [U].
