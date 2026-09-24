## A. Punctuation tells (WP = Wikipedia's Signs of AI writing; clay = theclaymethod/unslop)

- **Em dash (—)** ★. Used where people put commas, parentheses or colons (WP). Per 1,000 words, unprompted: GPT-4.1 10.62, Claude Opus 4.6 9.09, human essays 3.23 (Freeburg 2026). In July 2026 only Claude exceeded professional writers; ChatGPT now falls below them (Economist, via WP). *Fix:* period, comma, colon, parentheses, or recast; none in short copy (no-ai-slop). An explicit ban works on Claude: 0.00 per 1,000 words (Freeburg).
- **Spaced en dash " – " and " -- "**: humanizer treats them as the same tell; snifftest flags any en or em dash outside number ranges (5–10). *Fix:* same; a glyph swap fixes nothing.
- **Dash spacing**: WP says AI em dashes are usually spaced; Czuma 2026 found unspaced word—word doubled in 2025 congressional press releases. *Fix:* count both.
- **Colon reveal** ("The best part: it learns."): no-ai-slop, maxgoff, clay; snifftest flags 3+ colons per paragraph. *Fix:* a full sentence.
- **Emoji bullets** (WP): by July 2025, 70% of GPT-4o messages had emoji; ✅ ran 11× the human rate, 🧠 and 🔹 10× (WaPo). *Fix:* 0–2 per post, never as bullets (jalaalrd).
- **Arrows (→)** (tropes.fyi, humanizer). *Fix:* "to", "then".
- **"!"**: clay calls several per paragraph a hard tell; jalaalrd caps it at 1 per 1,000 words. *Fix:* period.
- **Ellipsis as a transition**: jalaalrd allows it only for a real trail-off, once per piece. *Fix:* period.
- **Curly quotes**: ChatGPT and DeepSeek use them, Claude and Gemini usually don't; weak alone (WP). *Fix:* keep them in typeset graphics; flag only mixed styles (inference).
- **Commas, semicolons, parentheses**: the Economist found LLMs use fewer than humans, write longer sentences and overuse "and"; SlopMonster and harshaneel flag semicolons in web copy. *Fix:* no semicolons in ads.

**Why:** markdown structure leaking into prose, with resistance to suppression tracking RLHF method (Freeburg). Goedecke's hypothesis is digitized 19th-century books; GPT-4o used about 10× GPT-3.5's rate. **Instead**, some writers now drop the dash entirely (McGill 2026). GPT-5.1 obeys a "no em dashes" instruction, but not by default (TechCrunch).

## B. Structural and phrasing tells (before → after)

1. ★ **Not X but Y / "not just X, it's Y"** (WP, Economist; SlopMonster's "loudest tell"; in 6% of ChatGPT chats in July 2025, WaPo): "Not just a roof, but peace of mind." → "A written scope and a fixed number before anyone climbs a ladder." (SlopMonster)
2. **Negative countdown** (tropes.fyi, stop-slop): "Not a bug. Not a feature. A fundamental design flaw." → "It's a design flaw."
3. ★ **Rule of three** (WP, Economist): "Trusted, reliable and built to last." → "Six nails per shingle, every shingle." (SlopMonster)
4. **"Whether you're X or Y"** (SlopMonster, Stockton): "Whether you're a beginner or a pro…" → "Built for your first 10K."
5. **Self-answered question** (tropes.fyi): "The result? Faster shipping." → "Orders ship the same day."
6. **Signposting** (humanizer, stop-slop): "Here's the thing: our bread is fresh." → "Baked at 5 a.m."
7. **Era openers** (jlwin, Stockton): "In today's fast-paced world, you need speed." → "Delivered in two hours."
8. ★ **Inflated significance** (WP): "The launch marks a pivotal moment for the company." → "The launch is the company's first paid product." (no-ai-slop)
9. ★ **-ing rider** (WP; GPT-4o uses participial clauses at 5.3× the human rate, Reinhart): "adds file search, highlighting the team's commitment to better workflows" → "adds file search, so users can find old drafts without leaving the editor" (no-ai-slop)
10. **Avoiding "is/has"** (WP): "The café boasts 40 seats." → "The café has 40 seats."
11. **Kickers and dramatic fragments** (humanizer): "Let that sink in." "Game. Changer." → cut them; end on the last concrete fact.
12. **Staccato overcorrection** (clay: the signature of de-slopped text): "Real dough. Real fire. Real fast." → "Out of the oven in 90 seconds." One fragment headline is fine; flag the cadence when it repeats.
13. **Stacked compounds:** "our industry-leading, context-aware, best-in-class platform" → one specification (SlopMonster).
14. **False range** (tropes.fyi): "From innovation to implementation to cultural transformation" → name the two real items.
15. **Hedge stacks:** "It may potentially help." → "It may help." Single hedges ("perhaps", "tends to") are more common in human text (WP).
16. **Borrowed authority:** "Experts agree", "featured in [outlets]" → name the source or cut it (WP, humanizer).
17. **Chatbot residue:** "I hope this helps", "Here's a caption:" → delete (humanizer's surest tell).
18. **Formatting** (bold-label bullets, emoji bullets, Title Case): "🚀 **Launch Phase:** The product launches in Q3" → "The product launches in Q3." (humanizer)
19. **Formula ending:** "Despite challenges… continues to thrive", "The future looks bright" → end on the last fact (WP, humanizer).

Passive voice is a weak tell: GPT-4o uses agentless passives at about half the human rate (Reinhart). WP's categories: content (significance, notability, -ing analysis, promotion, vague attribution, "challenges" sections), language (vocabulary, copulas, parallelisms, triads), style (title case, bold, list headers, dashes, emoji, quotes), chatbot residue, markup leaks.

## C. Vocabulary, roughly strongest first (★ = WP-listed and corpus-measured; the rest come from other WP lists or repo lists)

★delve: look at, dig into ("delves" ran 28× its expected 2024 rate in PubMed abstracts, Kobak; rare by 2025); ★underscores: shows (13.8×); ★showcasing: shows, has (10.7×); ★testament to: proof of; ★tapestry: mix; ★boasts: has; ★intricate: detailed; ★garner: get, win; ★emphasizing: says; ★highlighting: shows; ★enhance: improve; ★pivotal: key; ★crucial: important, needed; ★vibrant: lively, busy; ★robust: strong; ★groundbreaking: new, first; ★align with: fit, match; ★foster: build, encourage; ★meticulous: careful; ★landscape (abstract): market, field; ★interplay: mix; ★enduring: lasting; ★bolster: back, strengthen; ★valuable: useful; ★additionally: also; realm: field, area; key (adjective): main; seamless: smooth, easy; leverage: use; comprehensive: full; multifaceted: varied; harness: use; streamline: simplify; unveil: show, launch; revolutionize: change; elevate: improve, raise; unlock: get, open; unleash: release; embark: start; journey: process; game-changer: name the change; cutting-edge: new, latest; transformative: big; nestled: sits; in the heart of: in, central; bustling: busy; rich heritage: long history; renowned: known for; breathtaking: describe it; diverse array: range; profound: deep; navigate (figurative): handle; ever-evolving: changing; paramount: most important; holistic: whole; nuanced: subtle; empower: let, help; supercharge: speed up; curated: chosen; quietly: cut; resonate with: appeal to; moreover: also; core: main (ChatGPT used it 5× more in 2025 than a year earlier, WaPo).

WP: one or two may be chance, but a cluster is "one of the strongest tells." Lists age; WP's GPT-5 set is emphasizing, enhance, highlighting, showcasing. Literal uses are fine (robust steel).

## D. Marketing and ad-copy tells

- **Hype verb + "your X"** (unlock, elevate, supercharge, revolutionize): "We leverage industry-leading materials to deliver unparalleled protection." → "We source materials from manufacturers who test for wind, hail and sun." (SlopMonster; Jenny Lucas calls "elevate" one of ChatGPT's go-tos.)
- **Empty superlatives** (most trusted, world-class, best-in-class, award-winning): "The area's most trusted roofing experts." → "Roofing, and only roofing, since 2001." WP says newer models are "more subtly positive," so watch words like vibrant and seamless too.
- **Invented proof:** "Loved by 10,000+ happy homeowners" → a real, evidenced number or a visible placeholder (SlopMonster's one hard rule).
- **Stock constructions:** "Look no further", "Say goodbye to", "That's where we come in", "Imagine a…", "More than just", "[Problem]? Meet [solution]." Fix: say what the product does (SlopMonster, Stockton).
- **Launch hype:** "Big news! 🎉 We're thrilled to announce… Ready to experience the future of work?" → "New feature: Smart Templates. 14-day free trial, no card required." (clay)
- **Social bait:** "Hot take:", "Drop it in the comments 👇", 🧵, hashtag stacks → cut them; use 0–2 hashtags (clay, jalaalrd).
- **Urgency:** "Upgrade now and receive 20% off!" → "Upgrade before March 1 for 20% off the first year." (clay). "Don't miss out" and "Act now" are unmeasured; require a real date or quantity (inference).
- **Boilerplate CTA:** "Get started" → "Book a free inspection": the button says what it does (SlopMonster).
- **Tourism puffery:** nestled, must-visit, hidden gem → location plus one concrete detail (WP, humanizer, clay).
- **"Discover…"/"Experience the…" openers:** unmeasured by any source; treat as tier 2 (inference).

## E. Repos and skills

- **github.com/blader/humanizer** (51.7k★): Wikipedia-based rewrite skill, 25 patterns. *Borrow:* strength order (§1–5 act on one sighting; "weak alone" tells need company) and a no-new-facts check.
- **github.com/hardikpandya/stop-slop** (17.5k★): rules plus phrase and structure lists. *Borrow:* score directness, rhythm, trust, authenticity and density 1–10; revise below 35/50.
- **github.com/petergyang/no-ai-slop** (11.1k★): edit or detect mode. *Borrow:* the portability test (a line that fits any brand gets cut or made specific).
- **github.com/theclaymethod/unslop**: skill with Python scanners. *Borrow:* hard/soft regex catalogue, structure metrics, staccato exemption for social copy, quote and code masking.
- **github.com/ItsssssJack/SlopMonster**: copy linter for built HTML. *Borrow:* five pass/fail groups, ship only at 5/5, rival-model cleanup then re-lint.
- **github.com/sam-paech/antislop-sampler**: backtracking sampler with slop phrase lists. *Borrow:* resample when a banned phrase matches.
- **github.com/sam-paech/slop-forensics**: per-model over-represented words and n-grams. *Borrow:* build your own list from your outputs.
- **github.com/mshumer/unslop**: samples a domain N times with Claude Code and distills the defaults. *Borrow:* run it on "banner headlines".
- **github.com/jlwin/unslop_ai**: German/English skill. *Borrow:* three tiers (always replace / flag at 2+ per paragraph / flag when piled up).
- **github.com/jalaalrd/anti-ai-slop-writing**: writing directive. *Borrow:* numeric caps on dashes, "!" and hashtags.
- **github.com/harshaneel/humanize**: research-based humanizer and checker. *Borrow:* burstiness rules, best-of-N selection.
- **github.com/stephenturner/skill-deslop**: scientific deslop skill. *Borrow:* the tropes.fyi catalogue.
- **github.com/DanRWilloughby/snifftest**: prose linter. *Borrow:* marketing rules (unsupported "first" claims, verbless pull-quotes).
- **github.com/Aboudjem/humanizer-skill**: local detector. *Borrow:* 0–100 score (lexical 0.4, burstiness 0.28, diversity 0.18, repetition 0.14).
- Also read: maxgoff/unslop, realrossmanngroup/no_ai_slop_writing_rules. A GitHub search found no Bengali humanizer.

## F. Heuristics a script can run

1. **Dashes:** `—|\s--\s|–(?!\s?\d)`, which exempts number and time ranges (inference). None in short copy. In longer copy, at most 1 per 500 words (jalaalrd) and never 2 in one sentence (SlopMonster).
2. **Not X but Y:** `(?:\bnot|n't)\s+(?:just|only|merely|simply)\b[^.!?]{0,80}\bbut\b` (SlopMonster) and `(?i)not [^.!?]{3,60} but` (antislop). One hit fails.
3. **Triads:** `\b[A-Za-z][A-Za-z-]+,\s+[A-Za-z][A-Za-z-]+,\s+and\s+[A-Za-z][A-Za-z-]+\b` (clay), plus SlopMonster's version without the Oxford comma. Count them across a set of outputs (inference).
4. **Burstiness** (8+ sentences): flag a sentence-length CV under 0.55 or a max–min spread under 5 (clay), or 3 sentences in a row within 5 words of each other (harshaneel).
5. **Staccato:** 3+ sentences in a row of 5 words or fewer. Per document, flag 3+ lines built from 2–4 short sentences (clay).
6. **Openers:** unique first-word ratio under 0.55, or 4 identical openers in a row (clay).
7. **-ing riders:** `,\s+(ensuring|highlighting|reflecting|showcasing|emphasizing|fostering|underscoring|contributing to)\b[^.!?]*[.!?]$`. Flag a share of 0.15 or more (clay).
8. **Vocabulary:** stem-match, but exact-match words with literal senses (landscape, journey). A tier-1 word fails on one hit; tier-2 words fail at 2+ per paragraph.
9. **Invented proof:** `\d[\d,]*\+?\s*(?:happy|trusted|satisfied)?\s*(?:users|customers|clients|teams)` (simplified from SlopMonster). Fails unless the brief supplies the number.
10. **Counts:** 4+ hyphenated compounds in one sentence, 3+ bold-colon lines, emoji at line start, more than 2 hashtags, 3+ colons in one paragraph.
11. **Leaks (zero tolerance):** `oaicite|contentReference|turn0search0|utm_source=chatgpt|\[(Name|INSERT)`.
12. **Mask first:** quotes, brand names and code.
13. **Write for readers, not detectors:** heavy ChatGPT users still caught humanized AI text (100% by majority vote, Russell 2025).

## Sources

https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing, https://en.wikipedia.org/wiki/Wikipedia:Marketing_buzzspeak, the repos in E, https://tropes.fyi, https://arxiv.org/html/2603.27006v1 (Freeburg), https://arxiv.org/abs/2608.05889 (Czuma), https://arxiv.org/html/2406.07016 (Kobak), https://arxiv.org/html/2412.11385 (Juzek & Ward), https://arxiv.org/html/2410.16107 (Reinhart), https://arxiv.org/html/2501.15654 (Russell), https://www.seangoedecke.com/em-dashes/, https://www.mcgill.ca/oss/article/critical-thinking-student-contributors-technology/why-did-llms-steal-our-em-dashes, https://www.yahoo.com/news/articles/clues-chatgpt-wrote-something-analyzed-214947550.html (WaPo), https://www.techcrunch.com/2025/11/14/openai-says-its-fixed-chatgpts-em-dash-problem/, https://gustavonewsletter.substack.com/p/everything-you-know-about-spotting and https://aiadventureclub.substack.com/p/how-to-spot-ai-writing-in-2026 (Economist summaries; original paywalled), https://www.blakestockton.com/p/red-flag-phrases (Stockton), https://www.jennylucascopywriting.co.uk/2025/01/annoying-words-and-phrases-that-are-killing-your-marketing-copy/

Local copies of the scanners and word lists were kept in the research session's scratch folder, not in this repository.
