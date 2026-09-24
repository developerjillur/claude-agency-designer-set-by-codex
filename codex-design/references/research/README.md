# Research notes behind the references

Dated research notes, copied verbatim from the research runs. They are the evidence behind the reference files,
not rules: where a note and a reference disagree, the reference wins, because the references were updated after
measured runs. The notes keep their original punctuation, dashes included, so never copy their style into a design.

| File | Covers | Date |
|---|---|---|
| `R1-skills-higgsfield-local.md` | survey of design skills: higgsfield-ai/skills and the design skills installed locally | 2026-09-23 |
| `R2-community-skills-tools.md` | community skills, prompt libraries and open-source tools for design deliverables | 2026-09-23 |
| `R3-gpt-image-design-prompting.md` | designing with GPT Image: text, typography, and choosing full-AI or hybrid | 2026-09-23 |
| `R4-design-craft.md` | design craft: numeric rules, pairings, composition, colour, AI tells, logos, brand kits, critique | 2026-09-23 |
| `R5-formats-specs-playbooks.md` | format and print specs, and the playbook for each deliverable | 2026-09-23 |
| `R6-rendering-tooling.md` | rendering, fonts, PDF and image tooling on macOS (headless Chrome, Vision, font embedding) | 2026-09-23 |
| `R7-culture-legal-access.md` | occasions and culture, legal safety, accessibility and AI labelling | 2026-09-23 |
| `R8-gpt-image-2.5-edit-access.md` | GPT Image 2.5: region editing, references, typography, sizes and access paths | 2026-09-23 |
| `R9-single-prompt-pro-design.md` | single-prompt designs: the dossier method, recipes and variety | 2026-09-23 |
| `R10-trends-preferences-2026.md` | what looks current in late 2026, audience preferences and industry playbooks | 2026-09-23 |
| `R11-multi-agent-verification.md` | multi-agent generation, OCR verification and region repair for full-AI graphics | 2026-09-23 |
| `copy-ai-tells.md` | AI-writing tells in English: punctuation, structures, vocabulary, ad copy, humanizer repos, sources | 2026-09-24 |
| `copy-hooks-ctas-platforms.md` | hook patterns, platform limits, CTAs, captions, attention and copy frameworks, with sources | 2026-09-24 |
| `copy-transcreation.md` | transcreation principles, a table for 12 languages, local skills reviewed, gaps found | 2026-09-24 |
| `formats-social.md` | social formats: what was missing, what changed, measured overlays, retired formats, corrections | 2026-09-24 |
| `formats-creator.md` | creator, community, messaging, regional, blog, portfolio and music formats | 2026-09-24 |
| `formats-commerce.md` | the product image stack, text-on-image rules by marketplace, A+ content, store banners, app store screenshots, course and event covers | 2026-09-24 |
| `formats-unknown-protocol.md` | the method for an unknown size, platform or kind of design: spec ladder, first principles, archetypes, web and email formats | 2026-09-24 |
| `formats-canva-catalog.md` | the design types Canva and similar tools offer, used to find gaps in the catalogue | 2026-09-24 |
| `formats-print.md` | print, publishing, merch and signage playbook: e-book and book covers, magazines, reports, certificates, invitations, stationery, tickets, badges, tags, stickers, packaging, merch, yard signs, banners, roll-ups, billboards, transit, trade shows, digital signage, calendars, CVs; Bangladesh print market notes | 2026-09-24 |
| `formats-print-formulas.md` | the maths: book spines and wraps (KDP, IngramSpark, Lulu, BookBaby), barcodes, text size and resolution versus distance, bleed by printer, colour, labels on round containers, merch pixels, folds, billboard scale files, LED walls | 2026-09-24 |
| `voice-evidence.md` | why natural copy decides results: reader trust and purchase data, platform demotion of templated copy, detection studies, AI-disclosure law, Bangladesh reader opinion | 2026-09-24 |
| `voice-casual-en.md` | casual English craft: brand voice guides, the register ladder, what casual is not, purple prose, 2026 model templates, writing for the ear, replies; 179 lint candidates tested on 1,658 brand posts | 2026-09-24 |
| `voice-bangla.md` | Bangla and Banglish for Bangladesh: 724 brand texts and 3,322 human and ChatGPT passage pairs measured, register ladder, poetic stack, sadhu forms, Dhaka slang, Banglish, spelling slips, reader opinion | 2026-09-24 |
| `voice-languages.md` | casual versus bookish copy in 18 languages: calques, translated structure, spoken particles, template lines, address and code-mixing, swaps, AI and translation tells | 2026-09-24 |
| `voice-humanizer-skills.md` | 89 humanizer and anti-slop projects and the data lists (Wikipedia, GPTZero, Pangram, Kobak, slop-score): what they catch, where they disagree, 377 tested rules in 26 language codes | 2026-09-24 |
| `voice-data/` | the machine-readable candidates of the four voice notes, `build_voice_rules.py` (merges them into `scripts/voice_rules.json`, with the calibration overrides) and `evaluate.py` (checks a rebuild) | 2026-09-24 |

Not copied: the raw downloads the copy and voice research read (other projects' word lists, scanners and skill files,
a Wikipedia dump, the Bangla Academy rulebook, journal articles, and the brand posts and ads used to measure false
positives). They are third-party texts, not notes. Where a voice note says its JSON is "next to this file", it is in
`voice-data/`. The first Bengali research is in `copy.md` §3; the voice research on Bangla is `voice-bangla.md`.
