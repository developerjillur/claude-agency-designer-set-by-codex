# Where to look: programmatic sources, tools and Bangladeshi starting points

Evidence: `research/R8-deep-research-methods.md` §7 (every API checked on 2026-09-26) and §11.2. Rate limits and
terms change: respect them, and send an honest User-Agent.

## 1. The fetch ladder (R8 §11.2)

1. Claude's WebSearch (with `allowed_domains`) for finding; count it with `research.py budget`.
2. WebFetch for a quick look (a lead, never evidence: its summaries misreported numbers in our tests).
3. `research.py fetch URL` for the raw text used in checks (it caches, reads the title, author and dates, and reports
   blocked pages).
4. The in-app browser or Chrome for a public page that refuses scripts (low volume, reading only).
5. `research.py wayback URL` when a page is gone.

## 2. Built into the tool

| Command | Source | Good for | Notes |
|---|---|---|---|
| `youtube search "q" [--details] [--bank DIR]` | yt-dlp | competitor videos, views, outliers, chapters | `x_median_views` over 3 marks an outlier |
| `youtube comments VIDEO [--bank DIR]` | yt-dlp | the audience's words | usernames are never stored |
| `youtube captions VIDEO --lang en` | yt-dlp | what competitors say, their hooks | for Bangla audio use agy-watch-video (Gemini) |
| `academic "q" --source openalex|crossref|arxiv|semantic` | scholarly APIs | papers, DOIs, citations | Crossref wants a `mailto`; unauthenticated Semantic Scholar often returns 429 |
| `wiki "q" [--lang bn]` | Wikipedia | a map of citations, entities, dates | cite the underlying sources |
| `hn "q"` | Hacker News (Algolia) | tech audience, launch dates | 10,000 requests an hour |
| `fetch URL [--meta]` | the page | raw text and metadata | a blocked page says so |
| `wayback URL` | the Internet Archive | dead links, page history | |

## 3. Other free sources (R8 §7)

| Source | Good for | Access |
|---|---|---|
| PubMed E-utilities, Europe PMC | biomedical literature | 3 requests a second without a key |
| World Bank API | development indicators, with a last-updated date | no key |
| Our World in Data | harmonized indicators with the source chain and update dates (`.csv`, `.metadata.json`) | no key |
| Wikidata | structured facts | SPARQL, 60 s timeout |
| SEC EDGAR | company filings | a declared User-Agent with a contact email |
| Google Fact Check Tools | existing fact checks | API key |
| Google Trends | relative search interest | a sample rescaled 0 to 100 per request; compare against a stable term |
| Wikipedia pageviews | absolute attention over time | no key |
| Reddit | community language | OAuth by request; anonymous JSON is blocked |
| YouTube Data API | videos, stats, comments | quota-limited; terms forbid harvesting identifying data |
| Gemini with YouTube URLs (agy-watch-video) | transcripts and analysis of public videos | public videos only |

## 4. Bangladesh: starting points

Official and primary (grade A when the page holds the figure or the text itself; check each page's date):

- Bangladesh Bureau of Statistics (bbs.gov.bd): population, household income and expenditure, labour force, prices.
- Bangladesh Bank (bb.org.bd): exchange rates, remittances, inflation, monetary data.
- Laws of Bangladesh (bdlaws.minlaw.gov.bd): the text of acts (for example the Consumer Rights Protection Act 2009).
- Ministries and agencies under gov.bd: health (dghs.gov.bd), telecom (btrc.gov.bd, subscriber data), exports
  (epb.gov.bd).
- The World Bank and other intergovernmental series for comparisons (with their release dates).

News (grade B with a corrections policy; attribute and trace load-bearing claims): The Daily Star, Prothom Alo,
bdnews24.com, Dhaka Tribune, The Business Standard, New Age. Search them in Bangla and English: the same story often
carries different details in each language.

Audience words (grade D): Facebook pages and groups (Bangladesh is Facebook first), YouTube comments, Daraz and Google
Maps reviews. Read by hand where scraping is not allowed; aggregate; drop names.

Notes: our WebSearch is US-only, so search in Bangla script and Banglish with `allowed_domains` set to the outlets
above and `gov.bd`; convert numbers with care (lakh, crore, taka) and record the exchange rate and its date for every
conversion.
