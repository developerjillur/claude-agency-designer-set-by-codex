# Searching deep: the grid, three modes, the playbook, content research

Evidence: `research/R8-deep-research-methods.md` §5 and §8, `research/V1-method-videos-part1.md` (HimanshuG,
DecodingYT and Tube Sensei on researching like Dhruv Rathee).

## 1. Classify, then build the question grid (V1)

- **Classify the piece first:** a What (news), a Why (explainer) or a How-to (tutorial). The class sets the depth mode
  and the outline.
- **The grid:** who, what, when, where, why, how, plus impact and what next. Chain every answer into the next question;
  weight each W for the topic; premise-check every question (no question assumes something unverified). AI may draft
  the grid; answers come only from sources opened and read.
- **Decompose** into facts (who, what, when, where, how many), mechanisms (why, how), disagreements, people and
  stories, and the audience's questions. Perspectives (sceptic, practitioner, affected person, regulator, historian,
  local voice) surface questions one viewpoint misses (STORM).

## 2. Three depth modes (V1)

| Mode | What it builds | Used for |
|---|---|---|
| **Sequence** | dated events in order, a timeline | What videos; the "how did we get here" of any piece |
| **Breadth** | parallel factors, ranked by evidence, including the main factor named by the domain authority | Why videos: at least three factors |
| **Chain** | why after why, each link sourced, down to a documented point zero, or the end labelled "hypothesis" | Why videos: the root cause |

Collect **counter-evidence** during research, never after: it powers the midpoint twist and keeps the piece fair
(V1.3). Number hygiene for every figure: the unit, the base year, the definition (which poverty line?), nominal or
PPP, total or per capita, currency conversion recomputed (1 million = 10 lakh; 1 billion = 100 crore).

## 3. The playbook (R8 §5)

- **Vary queries:** short and broad first, then synonyms, jargon and lay words, question and keyword forms, the other
  side ("criticism", "debunked", "myth"), document types ("report", "dataset", "transcript", `filetype:pdf`), time,
  place and language. Log every query and its yield.
- **Operators:** Google documents `""`, `site:`, `-`, `before:`, `after:` and `filetype:`; Bing adds `language:`,
  `loc:`, `intitle:`, `inbody:`. Our WebSearch tool's `allowed_domains` and `blocked_domains` are the most reliable site
  filter. Never scrape Google result pages.
- **Recency:** `before:`/`after:`, the month and year in the query, "updated" stamps; for fast topics start from the
  newest material.
- **Multilingual:** search in the language of the place and people involved; translate names and key terms both ways,
  transliterations included (Bangla script, Banglish, English); target local domains (`site:gov.bd`, national
  outlets). Our WebSearch is US-only, so native-language queries plus local site targeting are the workaround. Verify
  every language equally; transcribe Bangla audio with Gemini (agy-watch-video), never whisper.
- **Follow the citation** backward to the origin and forward to later citing work (OpenAlex), with a Crossref retraction
  check; dead links go to the Wayback Machine (`research.py wayback URL`).
- **The primary source behind the news:** pull the identifiers (study title, DOI, report, bill or case number,
  dataset, speech date); search the exact title in quotes and with `filetype:pdf`; go to the issuer; compare the
  sample, period and caveats with the news claim; cite the original publisher, never a syndicated copy; for quotes,
  find the full transcript or video and timestamp.
- **The numbers ladder:** an official statistics release; intergovernmental databases (World Bank, UN, IMF, OECD);
  compilations that show their source chain (Our World in Data); associations and filings; commercial aggregators;
  news mentions. For Statista, trace the original on the page; its Market Insights figures are its own modelled
  estimates. Record the value, unit, place, period, definition, release and retrieval dates. Never average conflicting
  figures.
- **Wikipedia** is a map of citations, not the citation.

**Query templates:**

| Goal | Templates |
|---|---|
| Landscape | `[topic] explained`; `[topic] statistics [year]`; `[topic] report filetype:pdf` |
| Origin | `"[exact study or report title]"`; `"[key phrase]" site:gov`; `[org] annual report [year] filetype:pdf`; `[person] transcript [event]` |
| Disconfirm | `[claim] false`; `[claim] debunked`; `[topic] criticism`; `[topic] limitations study` |
| Recency | `[topic] after:2026-01-01`; `[topic] [month year] update` |
| Numbers | `[indicator] [country] site:worldbank.org`; `[indicator] our world in data`; `[indicator] [country] bureau of statistics` |
| Story | `[topic] oral history`; `[person] interview [year]`; `[event] court filing`; `[company] founder first customers` |
| Audience | `[problem] site:reddit.com "I wish"`; `[product] "does anyone else"`; `[topic] "how do I"` |
| Local | the query in the local language, with `allowed_domains` set to national outlets and `gov.[cc]` |

## 4. Research for content (R8 §8, V1)

**Finding the story:** a character with a want (public or consenting); the obstacle and the stakes; a dated turning
point with a before-and-after number; the surprising fact that breaks an audience assumption (check it hardest: it
spreads most); texture (a verbatim line, a place, an object); primary documents (filings, patents, letters, archive
footage). Build a dated timeline from primary sources, mark the turns and the people each turn affected, find a
document or clip per beat. Store stories with `research.py note add DIR --bank story --text "..." --set turn=...
--set claims=c3,c7`.

**The audience's own words (voice of customer):** ask what the audience uses today to solve the problem and where
those solutions live online, then mine those reviews and forums, not only your own product's. Sources: YouTube comments
(`research.py youtube comments VIDEO --bank DIR`), Hacker News (`hn`), review sites, Facebook groups, Google Maps and
Daraz reviews (read by hand), forums. Extract verbatim pains, desired outcomes, objections, triggers, questions and
misconceptions; count them; keep links; drop usernames. Misconceptions become myth-busting angles; repeated phrases
feed natural-text, the hooks and the persona panel. Community sources are grade D: opinion and the audience's words,
never a fact on their own.

**Competitors and the gap:**
1. Collect the top 20 to 50 videos or articles for the query set: title, angle, hook, structure, length, date, views,
   channel size (`research.py youtube search "..." --details --bank DIR`).
2. The outlier score: views against the median of the set (`x_median_views` over 3 marks an outlier worth studying).
3. Mine their comments for gap signals ("you didn't", "what about", "missed", "part 2", "wrong") and questions.
4. Send the top 3 to 5 to agy-watch-video for the hook, the structure and timestamped claims, then fact-check them:
   competitor errors are angles, never sources.
5. A gap matrix: sub-topics by competitor (covered, shallow, missing, wrong) plus the unanswered audience questions.

**Trend and topic selection:** Google Trends for relative interest and seasonality (a sample, rescaled 0 to 100 per
request, compared against a stable reference term); Wikipedia pageviews for absolute attention; YouTube's trending
charts for selected categories; Hacker News activity for tech topics. Score topics on demand, gap, fit, timeliness and
**evidence availability**: drop topics we cannot source well.

**Show the sources:** key claims get a highlighted headline or document on screen; the source list goes in the
description (the research documents of Dhruv Rathee's channel are the model for high-trust explainer markets).
