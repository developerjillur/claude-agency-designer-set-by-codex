# R2: Community skills, prompt libraries and open-source tools for pro graphic-design deliverables

- **Snapshot date:** 2026-09-23. Stars, licence (SPDX id) and last push were taken with `gh api repos/...` on that day. Numbers were re-checked in one consolidated pass, so they may differ from the agent reports by 1–5 stars.
- **Scope:** social posts, stories and carousels (including seamless "chain" carousels); YouTube thumbnails, banners and covers; posters, flyers and brochures; infographics and info, quote and tip cards; special-day posts; logos, brand kits and guidelines; ads and e-commerce banners; image-to-banner edits and multi-format resizing.
- **Method:**
  - Eight parallel read-only research passes. Three extracted the earlier local captures, and five did GitHub and web research.
  - I then personally re-verified the load-bearing facts: star counts, the frontend-design "AI default clusters" text, the app-store-screenshots seam rules, and the impeccable detector rule list.
  - Nothing was installed, cloned, posted or signed up for.
- **Licence legend:**
  - "none" means there is no licence, so the ideas can be used but not the code or text.
  - AGPL/GPL means reimplement the method instead of copying.
  - CC-BY means attribution is required.
  - "Proprietary" means read-only inspiration.
- **Copyright:** everything is paraphrased. No prompt text was copied beyond a few words.

## TL;DR (the 12 findings that matter)

1. **Our planned architecture is now the consensus of the best sources.**
   - OpenAI's `creative-production`: generate the raster visual base first, then add exact text, logos, charts and safe zones as deterministic layers.
   - Higgsfield brandkit: posters and banners are deterministic; image models never bake the logo or exact copy.
   - Canva AI 2.0 (layered output) and Shopify's docs (no baked text) point the same way.
   - The full-AI route stays as a gated option.
2. **Nobody ships seamless "chain" carousels end to end.** Only slicers exist.
   - The one formal rulebook is ParthJadhav/app-store-screenshots (MIT): crops of one connected canvas; one cross-seam moment per 5+ slides; 10–30 % overlap; never split text, prices or faces; each crop passes a one-second standalone test.
   - Build it as a master canvas with per-slide `clip` captures and a seam/text collision check.
3. **The best carousel engine is op7418/guizang-social-card-skill** (7.2k★, **AGPL, method only**). It uses seed HTML templates plus 28 layout recipes, and a Playwright validator with 9 rules (overflow, 22 px floor, ≥75 % fill, no blank band over 15 %, title gap). It fixes overflow with a ladder keyed to measured pixels.
4. **The best thumbnail and brand-kit processes are higgsfield-ai/skills** (MIT, *already installed here*).
   - Thumbnails: at least 5 concepts from 16 frameworks, a text-free plate, an HTML overlay baked at native resolution, a 120 px legibility gate.
   - Brand kits: a Brand Lock with evidence labels, approvals kept in a state file, dependency invalidation, and code (not vision) checking hex values, fonts and spacing.
5. **The best full-AI grammar is JimLiu/baoyu-skills** (26k★, MIT): style × layout × palette dimensions, presets, compatibility and auto-select tables, a prompt file before each render, an image-1 anchor chain, and a hardened `codex exec` wrapper. **The best e-commerce set logic is buluslan** (MIT): a 10-field Campaign Style Lock prepended byte-identical, a 9-slot funnel, a slop-word → replacement table and 8 AI-tell checks. Full lists are in Part C.
6. **In 2026 the most-starred design repos are about *taste and anti-slop*, not prompts:** gstack 134k, ui-ux-pro-max 130k, awesome-design-md 117k, open-design 98k, taste-skill 90k, impeccable 70k.
   - Anthropic's `frontend-design` (rewritten 2026-09-03) names five AI-default clusters, for example cream + serif + terracotta, near-black + one acid accent, and eyebrow/"A · B · C" template chrome.
   - impeccable ships a 61-rule deterministic detector. **Use both.**
7. **Prompt libraries are large but mostly third-party content.** freestylefly has 33k★ and 541 cases, 511 of them taken from X; YouMind has about 17k prompts. Mine their *techniques*: single-artifact guard, exact-copy contract, fixed-region infographic layouts, the three-glances test, a style-pack schema. Never copy prompts or images.
8. **Headless Chrome is the right engine.** Satori is flex-only. Takumi is the best browser-free option (grid, `text-fit`, paged PDF) but has untested Indic support. Chrome can't do CMYK or PDF/X; use WeasyPrint (PDF/X-4), Vivliostyle `--press-ready` (PDF/X-1a, AGPL) or Typst only when a printer demands it.
9. **Code the data, not the picture.** On IGenBench (ACL 2026), even Nano Banana Pro gets only 49 % of infographics fully correct, and GPT-Image-1.5 only 12 %. Charts come from AntV Infographic, ECharts SSR or Vega-Lite; image models supply illustration only.
10. **The Codex image path ignores size, quality and background.** Measured outputs: 1672×941 when asking for 16:9; 1122×1402; fake checkerboards. So always measure, then crop or pad, and verify alpha. Check that `image_gen` really ran in *this* thread (baoyu v2.5.2). **GPT Image 2.5** (Sunburst/Flare, snapshot 2026-09-08) exists in the API; it is unconfirmed whether Codex's built-in tool uses it.
11. **Licensing traps:**
    - rembg's default model is non-commercial; use `birefnet-general` or Apple Vision.
    - Remotion needs a company licence.
    - guizang is AGPL.
    - yingzao and inference-sh have no licence.
    - baoyu-design, huashu-design and claude-design-skill are derived from Claude Design prompts, so don't vendor them.
    - wzj177's code disables TLS verification.
12. **Audience data explains the pro-vs-slop gap.**
    - Carousels are the top-engaging format: Instagram 0.55 % vs 0.37 % for images; LinkedIn documents at 7 %.
    - 78 % of consumers prefer human-made ads.
    - Holiday AI ads drew backlash (Coca-Cola, McDonald's NL).
    - YouTube demonetizes templated "inauthentic" channels (2025-07-15), so series need real variation.
    - EU AI Act Art. 50 applies from 2026-08-02.
    - Pros win with a brand system, editable real type, one bold move, human sign-off and legibility tests at thumbnail size.

---

## Part A: Catalog

### A1. Community agent skills that make design deliverables

| Repo (github.com/…) | ★ | Licence | Last push | What it does | Technique worth adopting |
|---|---|---|---|---|---|
| JimLiu/baoyu-skills | 26,118 | MIT | 2026-09-10 | 21 skills. The design ones: `xhs-images` (a 1–10 card 3:4 series), `cover-image`, `infographic` (21 layouts × 22 styles), `slide-deck` (17 presets → PNG + PPTX + PDF), `article-illustrator`, `comic`, and a multi-provider `image-gen` with a `codex exec` backend | Independent dimensions (style × layout × palette), named presets and a table that auto-picks them from content signals; a prompt file written before every render; an image-1 anchor chain; a `STYLE_INSTRUCTIONS` block pasted word for word into every slide; a Codex wrapper with a JSON error taxonomy and proof that `image_gen` ran in the current thread (v2.5.2) |
| op7418/guizang-social-card-skill | 7,212 | AGPL-3.0 (commercial licence sold) | 2026-07-01 | Article → Xiaohongshu 3:4 carousels (1080×1440) and WeChat 21:9 + 1:1 cover pairs. Two style systems, 28 layout recipes, 10 themes; seed HTML → Playwright PNG | A 9-rule Playwright DOM validator (overflow, footer collision, 22 px body floor, ≥75 % filled, no blank band >15 %, title caps, title gap); an overflow-fix ladder keyed to measured pixels; a "subject map" plus a 360 px thumbnail test for text on photos; each ratio recomposed instead of cropped. **Use the method only (AGPL).** |
| higgsfield-ai/skills | 1,104 | MIT | 2026-09-14 | `youtube-thumbnail`, `brandkit`, `marketplace-cards`, `product-photoshoot` (Higgsfield CLI, paid credits). **Already installed locally**, v0.12.0 | Thumbnail: at least 5 concepts drawn from 16 frameworks; a truthful information gap; an 11-block prompt contract; a text-free render plus an HTML/CSS overlay baked at native resolution; a 120 px legibility gate; at most 16 generations. Brandkit: a Brand Lock whose fields are fixed, proposed, n/a or unknown, each with evidence; approvals in `state.json`; a change re-does only what depends on it; a set-level consistency matrix; vision is never trusted for hex values, fonts or spacing |
| op7418/guizang-yingzao-skill | 454 | none | 2026-09-03 | Real place photo → art-directed editorial poster through one GPT Image edit call | A three-image input contract (corrected source, one dominant reference, a neutral grey **typeset scaffold** with S1/B1/T1/I1 markers); a fontTools glyph-coverage check; alignment to real ink boxes; the "two islands" layout is rejected; 8 gates before generating; a READY manifest. Ideas only |
| buluslan/gpt-image2-ecommerce | 389 | MIT | 2026-09-17 | 39 e-commerce scenario templates, funnel sets, a compliance pre-check (`compliance_check.py`) | A **10-field Campaign Style Lock** prepended byte-identical to every prompt; a 9-slot funnel set; a 5-slot prompt; a category × style blacklist; a slop-word → replacement table; 8 AI-tell vision checks; edge-ring background detection plus a fill-ratio measure plus OCR |
| wzj177/ecommerce-image-suite | 415 | Apache-2.0 | 2026-08-27 | Product photos → an 8-type listing set, plus copy, detail-page HTML and video, for CN and global marketplaces | An analysis JSON with a `print_design_lock` product-fidelity sentence; layout chosen by *selling-point type* (material → magnifier bubbles; function → icons; detail → callouts; premium → split panels); a two-stage model/identity lock. **Avoid the code:** TLS verification is disabled, every output is forced to 1:1, and specs are invented |
| wuyoscar/GPT-Image2-Skill | 5,528 | MIT | 2026-09-09 | GPT Image 2/2.5 CLI, craft guide, 30 galleries, reverse-prompt skill | Canvas, ratio and layout before the subject; fixed-region layout contracts for infographics; a promotional hierarchy plus a "three glances" test; a table of what to freeze and what to check per artifact; name the failing string or region before retrying |
| smixs/visual-skills (`image/`) | 429 | CC-BY-4.0 | 2026-09-16 | Prompt writer for GPT Image 2.5 and Nano Banana; de-slop guide | 5 labelled slots; bans on booster words; each default the model beautifies is stated twice; Style DNA plus a Reject Checklist; edits written as Change / Preserve / Constraints (attribution required) |
| ningzimu/codex-ppt-skill | 6,156 | MIT | 2026-09-21 | Decks with one image per slide through Codex | Gates: outline → style (2–3 options) → backend → **one representative sample** → one subagent per slide. The sample becomes a style-only reference and its generation method is recorded; density caps by slide role; one metaphor per slide |
| JuneYaooo/gpt-image2-ppt-skills | 1,306 | Apache-2.0 | 2026-08-22 | Clone a template → deck; turn an AI page into an editable PPTX | A layout-bank sidecar JSON with per-slot length caps; a **corner-tick skeleton** for real-image slots (no coordinates in the prompt, real image pasted by code); a clean plate plus layers plus native text; an A1/A2/B extraction ladder; edges checked on black and on white; stop when a round brings no visible gain |
| alchaincyf/huashu-slide-codex | 22 | MIT | 2026-09-22 | Covers, thumbnails and slides through Codex `image_gen` | A platform size and safe-area table (YouTube banner safe area 1546×423); cover text at most 2 lines × 12 characters; title and cover must say different things; render 3 directions and regenerate anything under 7/10 |
| norahe0304-art/30x-image | 29 | MIT | 2026-08-28 | Brand DESIGN.md → 8 templates (ad, logo, slide, carousel …) through Codex | "Taste" dials drive deterministic variation axes, logged in `manifest.json`; an anti-slop block in every prompt; carousel axes (pattern, cover, body rhythm, continuity, tension curve) |
| dean9703111/ig-card-generator | 13 | MIT | 2026-07-26 | Markdown DSL → lint → Puppeteer, 1080×1350 cards | A component DSL (`[hero] [stat] [vs] [flow] [timeline]`); a character-cap lint; `invert` light/dark rhythm; a contact sheet, alt text and `deck.json` |
| johnnyang0612/bearcarousel | 3 | Apache-2.0 | 2026-07-23 | JSON content × template × brand → render → audit | Text placed from measured ink boxes; WCAG contrast measured on the real pixels behind the text; any red finding means not done |
| ZJU-REAL/Easel (`skills/openclaw/card-*`, `poster-hero`) | 1,310 | Apache-2.0 | 2026-09-23 | HTML social, quote and data cards on 9 locked styles | `card_audit.py` flags dead space, poor span and top-heavy layouts; the bigger the type, the lighter the weight; bans blue-purple gradients, gradient text and emoji used as icons |
| lijigang/ljg-skills (`ljg-card`) | 7,391 | MIT | 2026-09-16 | Reading, quote, whiteboard and comic cards | The generated image carries the idea; HTML carries the exact words; body text at least 40 px at 1080 px wide |
| itchernetski/threads-carousel-claude-skill | 102 | MIT | 2026-04-19 | Text posts → carousels (6 formats, 12 slide types) | A 3-axis style composer (font × colour × purpose); serve assets from the same origin so html-to-image exports aren't blank |
| charlesdove977/carousel-builder | 41 | MIT | 2026-06-08 | Instagram carousel via Higgsfield plus the Canva MCP | The cover becomes the theme anchor for every slide; character budgets are measured from the template |
| ParthJadhav/app-store-screenshots | 6,953 | MIT | 2026-09-05 | App-store screenshot decks | **Connected-canvas crops and cross-seam rules**, the only formal seam rules found (see B9) |
| motiful/product-shots | 78 | MIT | 2026-06-08 | A router plus 6 sub-skills: main image, A+, multi-angle, social, ads | A safe-zone pixel table (8 platforms × 21 formats) used as assertions; a filter for UI words in prompts, paired with "keep packaging text"; the user's copy is protected |
| rmichak/collateral-kit | 0 | MIT | 2026-08-19 | YAML → brochure or one-pager PDF, per-page proofs, `verify.py` | A page-order recipe; QR codes and URLs checked live; a 0.4 in trim margin |
| dabodamjan/poster-maker | 8 | MIT | 2026-08-28 | HTML/CSS → Playwright PNG/PDF: flyers, IG, OG, A4, business cards | 2× scale for pixel posters, 4× (≈384 dpi) for physical sizes; PDFs at true physical size |
| recombyn/zuoge (`festival_poster`) | 52 | Apache-2.0 | 2026-09-11 | Festival poster artboard agent | One memory point (the mood *or* the title); AI atmosphere plus native text nodes; no invented prices or QR codes |
| arome3/evidence-based-brand-systems | 3 | MIT | 2026-08-13 | Brand book, tokens, style tile, `brandcheck.py` | Contrast computed for every declared colour pair; font facts read with fontTools; one token source; no invented proof |
| durmazoguzhan/svg-logo-maker | 2 | MIT | 2026-09-04 | Hand-written SVG logos, variants, favicons, print handoff | A one-colour structure score; contrast of 3:1 for marks and 4.5:1 for wordmarks; a CMYK gamut check; a 16 px test |
| rampstackco/claude-skills | 898 | MIT | 2026-09-15 | 59 skills including `logo-design`, `brand-identity`, `brand-style-guide` | Each logo is tested at a 16 px favicon, a 28 px app icon, 1.5 in embroidery, one colour and reversed; any candidate failing more than 2 of these is dropped |
| Leonxlnx/taste-skill | 89,510 | MIT | 2026-09-23 | 15 "taste" skills, including `brandkit` (a brand board as one image) | A slop taxonomy (layout, visual, type, content, fake KPIs); strategy → core metaphor → board; bans generic lightning bolts, crests and sparkles |
| nextlevelbuilder/ui-ux-pro-max-skill | 130,045 | MIT | 2026-09-21 | Searchable style, palette and font data plus banner, brand and logo sub-skills | Banners: an HTML/CSS overlay on a text-free background, critical content in the central 70–80 %, at most 2 typefaces, contrast ≥4.5:1, 3 options |
| coreyhaines31/marketingskills | 51,279 | MIT | 2026-09-05 | `ad-creative`, `social` (carousel frameworks), `marketing-psychology` | Platform character limits; 5 carousel narrative structures |
| garrytan/gstack | 133,993 | MIT | 2026-09-23 | `design-review`, `design-shotgun`, `design-consultation` | A 0–10 score per dimension with "what would make it a 10"; a rating board writing `feedback.json`; a decaying `taste-profile.json` |
| cathrynlavery/diagram-design | 42,133 | MIT | 2026-09-19 | 41 diagram and chart types as HTML + SVG | A style-guide gate before first use; density 4/10; the accent on 1–2 focal nodes only |
| google-labs-code/design.md | 28,055 | Apache-2.0 | 2026-09-14 | The DESIGN.md spec: a visual identity written for agents | Use it as the brand-lock file format |
| VoltAgent/awesome-design-md | 117,453 | MIT | 2026-09-21 | DESIGN.md files distilled from real sites | Structural examples only; never clone a real brand for a client |
| nexu-io/open-design | 97,767 | Apache-2.0 | 2026-09-23 | Local "Claude Design" alternative with a `critique` template | 5 dimensions scored 0–10 → an HTML report with Keep / Fix (P0/P1) / Quick-wins. **Its poster and carousel templates produce the AI look; avoid them** |
| pbakaus/impeccable | 70,118 | Apache-2.0 | 2026-09-22 | Design language plus a **deterministic anti-pattern detector (61 rules)**. Installed locally | Slop rules (overused fonts, AI purple/cyan palette, the default cream palette, gradient text, a type hierarchy flatter than 1.25×, glow and halo) plus quality rules (overflow, text occlusion, contrast, tight leading, tiny text) plus DESIGN.md conformance. The critique runs the design review blind *before* detector evidence enters |
| jau123/MeiGen-AI-Design-MCP | 1,772 | MIT | 2026-09-17 | MCP to the paid MeiGen API plus a library of 1,400+ prompts | Variant axes of photoreal / illustration / type-led; a headline zone kept clear |
| Jakeschincariol/youtube-agent-skill (`yt-package`) | 108 | MIT | 2026-09-16 | Lints a title and its thumbnail as a pair | Thumbnail at most 3 words; no word overlap with the title; truncation checks at 60 and 40 characters |
| AgriciDaniel/claude-youtube | 390 | MIT | 2026-04-10 | YouTube strategy, including a thumbnail CTR guide | Test at mobile size; 3–5 words at most |
| SupercmoHQ/superCMO-skills | 48 | Apache-2.0 | 2026-08-28 | `generating-image-ads` | Pick the model by how much text there is; don't make the model redraw label text; the CTA is a filled button |
| antvis/Infographic (skills) | 6,853 | MIT | 2026-08-21 | Declarative infographic DSL, its renderer, and agent skills | The LLM writes the DSL, so numbers and labels stay exact |
| alchaincyf/huashu-design | 24,414 | MIT | 2026-09-22 | Design skill distilled from Claude Design prompts | **Caution:** provenance, and a watermark added by default. Take the ideas only: the three-directions gate and the critique bands |
| nexu-io/html-anything | 8,934 | Apache-2.0 | 2026-09-15 | 75 HTML templates | Useful as a taxonomy only; its poster spec prescribes the violet gradient and emoji AI look |
| HisMax/RedInk | 5,578 | NOASSERTION | 2026-06-30 | One sentence → a Xiaohongshu post (Nano Banana Pro) | A signal of volume demand for Xiaohongshu cards |

### A2. Official skills and plugins (Anthropic, OpenAI)

| Repo / path | ★ | Licence | Last push | What it does | Technique worth adopting |
|---|---|---|---|---|---|
| anthropics/skills: `frontend-design` | 177,768 | Apache-2.0 (per skill) | rewritten 2026-09-03 (#1713) | Distinctive visual direction | Names **5 clusters that AI design defaults to** (B8); a "similar prompt" self-check, where you revise if a similar prompt would land in the same place; spend boldness in one place only |
| anthropics/skills: `canvas-design` | same | Apache-2.0 | 2025-12 | A design-philosophy .md, then one PNG/PDF made in code | Philosophy first; about 90 % visual; bundled OFL fonts (`canvas-fonts/`); nothing overlaps; a forced "refine, don't add" pass |
| anthropics/skills: `theme-factory`, `brand-guidelines`, `algorithmic-art`, `slack-gif-creator`, `web-artifacts-builder` | same | Apache-2.0 | 2025-12 | Theme presets, a brand application, generative art, budgeted GIFs | A theme showcase PDF → the user picks; a template for a per-client brand skill; seeded generative backgrounds; validators for output budgets |
| anthropics/skills: `pptx`, `pdf`, `docx` | same | **Proprietary** | 2026-07 | Document skills | A list of AI tells (underlines under titles, edge stripes, cream default backgrounds, centred body text); **render every page and inspect it with fresh context (a subagent)**; fonts the QA renderer can reproduce exactly |
| anthropics/knowledge-work-plugins | 25,474 | Apache-2.0 | 2026-09-23 | `design-critique`, `brand-review`, `brand-style`, `canva-creator` | Brand captured from a URL or plain words and previewed before saving; a generation budget shown before spending (rows × candidates) |
| openai/codex: `codex-rs/skills/src/assets/samples/imagegen` | 126,135 | Apache-2.0 | skill changed 2026-08-10 | The bundled Codex imagegen skill (native transparency) | 16 use-case slugs; a labelled spec (Use case, Asset type, …, Text (verbatim), Constraints, Avoid); invariants repeated on every edit; never overwrite, use versioned names |
| openai/plugins: `creative-production` | 7,133 | **Proprietary** | 2026-09-18 | Ads, social, logos, charts on a review board | **Generate the raster visual base first, then add exact text, logos, charts, safe zones and dimensions as deterministic layers.** 4–6 directions; ≤4 parallel workers; ≤2 attempts; every returned path checked |
| openai/plugins: `build-web-apps/frontend-app-builder` | same | MIT | same | ImageGen concept → faithful HTML → fidelity QA | Tokens, an allowed-copy list and a colour lock extracted before coding; a **fidelity ledger** of at least 5 comparison points between concept and render |
| openai/plugins: `product-design/design-qa` | same | Proprietary | same | Side-by-side design-vs-build QA | Source and render in one image; P0–P3 findings; blocked until no P0–P2 remains; the build fails if real imagery was replaced with CSS, SVG or emoji |
| openai/plugins: `build-web-data-visualization` | same | MIT | same | Editorial infographic system plus a rubric | A 7 × 5 rubric (clarity, storytelling, hierarchy, restraint, annotation, accessibility, originality); ship at 28/35 or higher with no score below 4 |
| openai/plugins: `canva`, `adobe` | same | none / Apache-2.0 (Adobe skill) | same | Canva MCP resize, bulk create, brand check and feedback; Adobe social variations | Canva feedback per page with High/Med/Low severity and one fix each; Adobe does subject-aware crops plus generative expansion and **previews 3 crops before the full run** |
| openai/skills | 27,577 | Apache-2.0 (per skill) | 2026-09-08 | **Deprecated** (PR #496, 2026-06-22) in favour of openai/plugins | `hatch-pet`: invisible layout-guide images, contact-sheet QA, repair the smallest failing scope |

### A3. Prompt libraries ("awesome GPT image" and similar)

| Repo | ★ | Licence | Last push | What it does | Technique worth adopting |
|---|---|---|---|---|---|
| freestylefly/awesome-gpt-image-2 | 33,366 | MIT (but **511 of 541 cases come from X posts**) | 2026-09-11 | 541 cases in 13 categories; 47 template blocks; a 22-entry style library; a skill (`gpt-image-2-style-library`); a paid web app | Routing goes category → style tag → scene tag → nearest cases; every category has a plain template, an agent JSON template and pitfalls; a single-artifact guard (no moodboard, grid or mockup) |
| YouMind-OpenLab/awesome-gpt-image-2 | 9,939 | CC-BY-4.0 in its LICENSE file (GitHub shows NOASSERTION) | 2026-09-23 | ~17.5k prompts; categories include YouTube Thumbnail, Social Media Post, Poster/Flyer, E-commerce Main Image, Infographic | `{argument name="…" default="…"}` slots; author, source and date recorded for every entry |
| YouMind-OpenLab/awesome-nano-banana-pro-prompts | 13,473 | CC-BY-4.0 | 2026-09-23 | ~15.7k prompts | A bento infographic "system instruction" (hero card 28–30 % of area; icon, label, value and unit per metric); a 2×2 puzzle that stays continuous across panels |
| YouMind-OpenLab/ai-image-prompts-skill | ~1.1k | MIT | 2026-09-23 | Recommends at most 3 proven prompts, then remixes the chosen one | Pick first, then remix; the category sizes signal demand (Social 9,746 · Product marketing 5,716 · Poster/flyer 1,023 · Infographic 605 · E-com main image 577 · YouTube thumbnail 224) |
| EvoLinkAI/awesome-gpt-image-2-API-and-Prompts | 17,236 | CC0 (claimed over X content) | 2026-07-18 | 462 cases in 7 categories | Storyboards that say "exactly N scenes" and number them; JSON lighting split into key, fill, specular and shadow |
| ZeroLu/awesome-gpt-image | 2,226 | MIT (images hotlinked from X) | 2026-09-23 | About 72 prompts, including typography and posters | Dense-text stress tests; always supply the exact copy |
| PicoTrex/Awesome-Nano-Banana-images | 23,778 | Apache-2.0 (images third-party) | 2026-09-03 | About 140 edit recipes | Document → flowchart; article → slide |
| jamez-bondos/awesome-gpt4o-images | 8,151 | CC-BY-4.0 + NOTICE | 2025-05-26 | 100 cases | A per-case `ATTRIBUTION.yml` that separates the prompt author from the image author |
| VigoZhao/AI-Visual-Prompt-Cookbook | 611 | MIT (code) / CC-BY-4.0 (packs) | 2026-09-23 | 147 JSON style packs, a schema and CI | A style pack holds fidelity anchors, source content to avoid, and variables; the prompt is rendered at runtime, so stored prompts never drift |
| QIYU-JACKMAN/codexQIYU-image-workflow | 83 | root none (MIT in a subfolder) | 2026-08-19 | Codex e-commerce workflows, including batch resize | A manifest that retries only failed IDs; a resize QA gate (no stretching, no bars, no cropped copy) |
| FANzR-arch/Phil-design-skills | 82 | none | 2026-08-15 | 19 style "compile contracts" | The template body is locked and only fields are open; a blank field beats an invented one; a series varies at least 2 fields |
| songguoxs/gpt4o-image-prompts · ZHO-ZHO-ZHO/ZHO-nano-banana-Creation · ImgEdify/Awesome-GPT4o-Image-Prompts | 3.8k / 3.7k / 586 | none / GPL-3.0 / MIT | 2026-01 / 2025-09 / 2025-05 | Older or copyleft collections | Reference only |

### A4. Curated lists and directories (for discovery)

| List | ★ | Licence | Last push | Design coverage |
|---|---|---|---|---|
| ComposioHQ/awesome-claude-skills | 75,528 | none | 2026-09-18 | Creative & Media and Business & Marketing sections, mostly copies of the Anthropic skills |
| hesreallyhim/awesome-claude-code | 54,485 | NOASSERTION | 2026-09-23 | Curated "Design & UI/UX" and "Creative Media" sections |
| VoltAgent/awesome-agent-skills | 34,772 | MIT | 2026-09-23 | The largest (1000+), including official Figma, Stitch, fal and MiniMax sets |
| travisvn/awesome-claude-skills | 15,140 | none | 2026-04-28 | Stale |
| BehiSecc/awesome-claude-skills | 10,171 | none | 2026-09-21 | Media, marketing, a design auditor |
| heilcheng/awesome-agent-skills | 6,226 | MIT | 2026-04-05 | Mirrors of the above |
| PatrickJS/awesome-cursorrules | 40,826 | CC0-1.0 | 2026-05-30 | Only `toss-style-design-system.mdc` (one accent; greys carry the structure; weight and colour before size; no nested cards) and `landing-page-image-quality.mdc` (never put essential text *only* inside an image) are relevant |
| skills.sh / claude-plugins.dev | — | — | live | Install counts are **not** a quality signal: one repo shows 379k installs but has 6 stars |

### A5. Open-source render engines and tools

The quality ceiling is judged by rendering engine, CSS coverage, text shaping (HarfBuzz and complex scripts), OpenType and variable-font support, colour, PDF and print capability, and speed.

**HTML/JSX → image or PDF**

| Tool | ★ | Licence | Last push | What it does | Quality ceiling and why | Technique to adopt |
|---|---|---|---|---|---|---|
| microsoft/playwright | 96,557 | Apache-2.0 | 2026-09-23 | Drives Chromium, WebKit and Firefox; screenshots; PDF in Chromium only | **Full Chrome ceiling** (Blink + Skia + HarfBuzz + ICU): grid, `text-wrap` balance/pretty, `hyphens` (Bengali since Chrome 87), variable and COLRv1 fonts, bidi text | Context `deviceScaleFactor`; `locator.screenshot`; `clip`; `omitBackground`; `animations:'disabled'`; `caret:'hide'`; `style:` to hide guides |
| puppeteer/puppeteer | 95,616 | Apache-2.0 | 2026-09-23 | Chrome driver; PNG, JPEG, WebP; PDF | Same as Chrome | `page.pdf` waits for fonts and tags the PDF by default |
| Raw CDP (what in-progress `codex-design` uses) | — | — | — | `Page.captureScreenshot` / `printToPDF` | Same | `CSS.getPlatformFontsForNode` reveals **silent font fallback**; `Emulation.setEmulatedVisionDeficiency` gives blurred and greyscale judge views |
| gotenberg/gotenberg | 13,150 | MIT | 2026-09-18 | Docker API: Chromium → PDF or screenshots; PDF/A and PDF/UA | Chrome, RGB only; only fonts baked into the image | Treat `failOnConsoleExceptions` and `failOnResourceLoadingFailed` as hard gates |
| node-html-to-image | 887 | Apache-2.0 | 2026-09-11 | Puppeteer + Handlebars | Chrome | Template kept separate from data; a page pool |
| vercel/satori (+ @vercel/og) | 13,969 | MPL-2.0 | 2026-09-22 (0.33.5) | JSX subset → SVG, laid out with Yoga | **Flat OG cards only.** Flex/block only (no grid, `z-index` or `calc`); HarfBuzz shaping only since 0.33.0 (2026-08-20); no mixed LTR/RTL; TTF/OTF/WOFF but no WOFF2; `balance` but no `pretty` | Not for designed pieces |
| kane50613/takumi | 3,021 | MIT or Apache-2.0 | 2026-09-23 | Rust: JSX/HTML/CSS → PNG, JPEG, WebP, SVG, GIF/APNG, **paged PDF** | **The best ceiling without a browser.** Taffy flex, grid and float; `calc`; `@media`; `text-fit`; balance/pretty; variable fonts; WOFF2; Arabic/bidi; tagged PDF and PDF/A. **Indic scripts untested.** Warm PDF in 26 ms vs Puppeteer's 198 ms | An optional bulk path for hundreds of variants of a template already approved in Chrome; its `text-fit` is a reference for our fitter |
| html2canvas · bubkoo/html-to-image · modern-screenshot · zumerlab/snapdom | 31.9k · 7.2k · 2.1k · 8.2k | MIT | 2024-07 · 2026-05 · 2026-04 · 2026-09 | Capture a DOM element from inside a page | html2canvas repaints the page itself (lowest quality: no filters or blend modes); the others use a foreignObject approach (fonts must be inlined; raster only) | Only for a "download" button inside an editor |

**Print and PDF engines** (Chrome can't produce CMYK, spot colours, PDF/X, `bleed` or `marks`)

| Tool | ★ | Licence | Last push | Quality ceiling and why | Use |
|---|---|---|---|---|---|
| Kozea/WeasyPrint | 9,627 | BSD-3-Clause | 2026-09-22 (v70) | Its own layout engine (Pango/HarfBuzz). @page margin boxes, **`bleed`, `marks`, PDF/X-1a/-3/-4/-5g, `device-cmyk()`**, hyphenation, OpenType features. Weak on modern CSS: no `text-wrap`, basic grid and flex. Needs Python ≥3.10 (this Mac's system Python is 3.9) | CMYK or PDF/X for text-led print (menus, flyers) in restricted CSS |
| pagedjs/pagedjs | 1,514 | MIT | 2026-09-15 | Paged Media polyfill running inside Chrome: running headers, page counters, bleed and crop marks | Multi-page brochures, still in Chrome |
| vivliostyle.js / vivliostyle-cli | 793 / 235 | **AGPL-3.0** | 2026-09-23 | Chromium typesetting; `--crop-marks`, `--bleed 3mm`, **`--press-ready`** → PDF/X-1a through Ghostscript | One-command press-ready PDF from our HTML; run it as a separate CLI because of AGPL |
| typst/typst | 56,193 | Apache-2.0 | 2026-09-23 (v0.15.1) | **Best paragraph typography** (optimized justification); `cmyk()`, spot colours, `page(bleed:)`, variable fonts (all 0.15); PDF/A and UA; PNG at a chosen `--ppi`; Indic hyphenation fixed in 2026-04; **no PDF/X**, no CSS effects | Brochures, menus, catalogues, reports |
| Ghostscript (`pdfwrite`) | — | AGPL or commercial | 2026-09 | Chrome's RGB PDF → CMYK PDF/X-1 or X-3 with an ICC output intent; **no X-4**; flattens transparency | Last-step CMYK conversion |
| pdf-lib / qpdf / pikepdf | 8.6k / 5.4k / 2.8k | MIT / Apache-2.0 / MPL-2.0 | 2024-07 / 2026-09 / 2026-09 | PDF structure editing | Set TrimBox and BleedBox; inspect embedded fonts |

**Raster, canvas and image libraries**

| Tool | ★ | Licence | Last push | Use |
|---|---|---|---|---|
| lovell/sharp | 32,709 | Apache-2.0 | 2026-09-22 (0.35) | `extract` (carousel slicing), `attention` smart crop (luminance, saturation, skin), `withIccProfile('srgb')`, `withDensity(300)`, CMYK TIFF/JPEG, AVIF/WebP |
| linebender/resvg | 4,092 | Apache-2.0 | 2026-09-16 | The most accurate static-SVG rasterizer (about 1,600 regression tests). Use it for logo and icon PNG sizes. It has no HTML, so `foreignObject` labels are lost |
| skia-canvas · @napi-rs/canvas | 2.6k · 2.3k | MIT | 2026-09 | Canvas on Skia with vector PDF/SVG; generative textures |
| jwagner/smartcrop.js | 12,957 | MIT | 2024-03 (stale, works) | Content-aware crop; can boost detected faces |
| danielgatis/rembg | 24,853 | MIT (code only) | 2026-09-20 | **Its default model `bria-rmbg` (RMBG-2.0) is CC BY-NC 4.0, i.e. non-commercial.** Use `-m birefnet-general` (MIT), with `-dc` and `-vm` for hair. Apple Vision foreground masks avoid the licence question entirely |
| ZhengPeng7/BiRefNet · transformers.js | 4.2k · 16.3k | MIT · Apache-2.0 | 2026-09 | High-resolution segmentation; a JavaScript background-removal pipeline |

**Video engines that can also make stills (animated variants)**

| Tool | ★ | Licence | Note |
|---|---|---|---|
| heygen-com/hyperframes | 52,575 | Apache-2.0 | HTML → deterministic MP4 through Chrome; `snapshot --at` for stills. **Its skills are already installed here**, so it can turn an approved static design into a story or reel version |
| remotion-dev/remotion | 60,120 | Remotion License | `renderStill()`. **Needs a paid company licence above 3 employees**, so avoid it unless licensed |

**Carousel, social and OG generators**

| Project | ★ | Licence | Renders with | Takeaway |
|---|---|---|---|---|
| Hainrixz/open-carrusel | 467 | MIT | Puppeteer + sharp; Claude writes each slide's HTML | The closest to our plan, but with no QA and no PDF |
| FranciscoMoretti/carousel-generator | 211 | MIT | html-to-image → jsPDF | Its LinkedIn PDF is **raster**, with no selectable text. Don't copy this |
| wei/socialify · shadcn-labs/ogimagecn · pi0/shiki-image | 2.2k · 233 · 165 | MIT | Satori / Takumi | Parametric OG cards |
| FUTC-Coding/panosplitter · alexejwaser/ZeroSeams | 45 · 1 | GPL-3.0 · MIT | Slicers only | Seamless carousel = one master cut into N frames |

**Template-image APIs** (their layer models are worth copying)

| API / format | What its layer model teaches |
|---|---|
| Bannerbear | Named layers; **`text-fit: auto_fit / resize_overflow`**; layers anchored to other layers so a layout survives resizing; `ai-detect: face / subject` for focus crops, with a fallback |
| Placid | `color_mode: rgb / cmyk` and dpi 72–300 per output |
| Templated | `autofit` with `min_font_size` and `max_font_size`; `object_fit` and `object_position` |
| Polotno JSON | `{pages[{children[], bleed}]}`, where stacking order is array order; crop fractions; `${photo:query}` placeholders; `custom` data for bulk variants |

Self-hosted open-source clones (canolite, openbanner, beeroniza) are all immature. **Takeaway: design our own slot schema** (see E3):
- named slots;
- fit modes `off / shrink / grow-shrink` with a minimum size;
- an overflow policy (ellipsis vs. rewrite the copy);
- relative anchors;
- image fit and focus, with focus from faces or saliency;
- a background-removal flag;
- `dpi`, `scale` and `color_mode` per output.

**Design engines and editors**

| Engine | ★ | Licence | Headless template engine? | Note |
|---|---|---|---|---|
| Polotno (SDK, polotno-node, `@polotno/pdf-export`, desktop app) | — | Commercial ($249/mo and up); the desktop app is free | Yes | Built on Konva. The app runs a local MCP server with 19 tools and bundles a `polotno-design` skill. Its QA rubric is **pass/block per check** (content, visual intent, reading path, typography, spacing, colour, media, editability, output), followed by a fixed repair order. pdf-export does PDF/X-4 and X-1a, CMYK, spot colours, bleed and crop marks |
| penpot/penpot | 60,289 | MPL-2.0 | Partly (it has an exporter; the MCP needs the plugin tab open) | Heavy to self-host |
| open-pencil/open-pencil | 8.6k | MIT | Yes (early): `openpencil export` to PNG, PDF, SVG, PPTX and `.fig` | Reads and writes Figma `.fig`; its MCP has 100+ tools; created 2026-02; rough edges |
| fabricjs/fabric.js · konvajs/konva | 31,454 · 14,815 | MIT | Yes (node canvas backends) | Canvas text only; most Bannerbear clones use Fabric |
| excalidraw/excalidraw | 132,717 | MIT | Browser only | Hand-drawn diagrams (Rough.js) |
| tldraw/tldraw | 50,535 | Custom (production use needs a key) | No | — |
| GraphiteEditor/Graphite | 27.3k | Apache-2.0 + MIT | Experimental | Node-based and procedural; alpha |
| layerhub-io/react-design-editor | — | — | Repo removed (404) | Dead |
| IMG.LY CE.SDK · Pintura | — | Proprietary | CE.SDK yes; Pintura browser only | Commercial references |

**Charts and infographics for social posts**

| Tool | ★ | Licence | Server-side output | Fit |
|---|---|---|---|---|
| antvis/Infographic | 6,853 | MIT | SVG; a community CLI | **The best text-to-infographic layout engine.** LLM-friendly syntax that tolerates streamed output; about 200 templates; a hand-drawn theme; ships Claude skills |
| apache/echarts | 67,380 | Apache-2.0 | `renderToSVGString()` (SSR) | Polished defaults, many chart types |
| vega/vega-lite + vl-convert | 5,495 | BSD-3-Clause | SVG/PNG/PDF without a browser | A JSON grammar that LLMs write reliably |
| observablehq/plot · d3 | 5,386 · 113.8k | ISC | SVG | Editorial defaults · unlimited but all custom |
| mermaid · d2lang/d2 | 90,379 · 25,491 | MIT · MPL-2.0 | CLI | Technical diagrams only; D2 looks cleaner and has a sketch mode |
| rough.js / roughViz | 21.2k / 7.2k | MIT | SVG | Hand-drawn accents |
| Datawrapper, Flourish | — | Commercial | — | Quality reference: headline plus subtitle, labels on the data, a source line |
| MisterBrookT/IGenBench (ACL 2026) | 17 | MIT | Benchmark | **Whole-infographic fully correct: GPT-Image-1.5 0.12, Nano Banana Pro 0.49** (question-level 0.55 / 0.90). This justifies composing infographics in code |

**Typography and colour support**

| Tool | Licence | Use |
|---|---|---|
| fontsource/fontsource (6.1k) | MIT (fonts keep their own licences, mostly OFL) | Pinned, offline, self-hosted fonts, including variable ones |
| fonttools (`pyftsubset`) · glyphhanger | MIT | Subset while keeping `--layout-features='*'`; WOFF2; glyph coverage |
| culori (4.0) · chroma.js | MIT · BSD/Apache | OKLCH palettes, gamut mapping, WCAG contrast, ΔE |
| Myndex/apca-w3 | "Limited W3 licence", patent pending | Advisory only; keep the WCAG 2 ratio as the actual gate |
| STRML/textFit · fitty | MIT | References for a binary-search text fitter |
| Emoji fonts: noto-emoji (OFL) · twemoji (MIT + CC-BY) · fluentui-emoji (MIT) | — | Pin an emoji font instead of the operating system's Apple Color Emoji |

### A6. Design-tool MCPs (for when a client needs editable files)

| Item | Status 2026-09-23 | Use |
|---|---|---|
| Canva MCP (`mcp.canva.com/mcp`, OAuth; docs canva.dev/docs/mcp) | Live. OpenAI ships an official Codex Canva plugin | Editable Canva output: resize, brand kits, export. Bulk Create needs Enterprise. Colours and fonts are not reliably readable, so the thumbnail is the source of truth |
| Figma remote MCP (figma/mcp-server-guide) | Write-to-canvas in beta: free now, billed by usage later | Figma frames for clients who need Figma |
| penpot/penpot `mcp/` (60,289★, MPL-2.0) | Active; the old penpot/penpot-mcp repo was archived 2026-02-03 | Self-hostable editable vector output. The plugin tab must stay open |
| Kittl | No MCP or API (kittl.com, checked 2026-09-23) | Don't plan around it |

---

## Part B: Deep notes on the best 10

### B1. op7418/guizang-social-card-skill: the most mature carousel and social-card engine (AGPL, method only)

- **Outputs:**
  - Xiaohongshu 3:4 sets at 1080×1440.
  - WeChat cover pairs at 2100×900 (21:9) and 1080×1080, both built in one HTML file with a side-by-side preview.
  - Live Photo cards.
- **Intake:**
  - It asks only what changes the result: the platform, the source text and the content category.
  - A cookbook routes each category, and **openly declines** categories it can't do well, such as OOTD body shots.
  - The image source is asked once: the user's own photos (recommended, as the least AI-looking), stock with every URL logged in `SOURCES.md`, or AI.
- **Planning:**
  - The cover is the hook, then one idea per page, usually 5–9 pages.
  - Each set gets one style system (Editorial Magazine / E-ink, or Swiss International) and one theme.
  - Every page uses a layout recipe (M01–M16, S01–S12), each with a minimum density.
  - HTML is **never written from scratch**; each set starts from a seed template.
- **Quality rules:**
  - A component spec fixes the type scale, minimum readable sizes, title length bands, spacing tokens and the icon set (Lucide).
  - Swiss style: the bigger the type, the lighter the weight.
  - Editorial pages need an atmosphere layer (paper grain or ink), never flat beige.
  - Banned: decorative blobs, nested SaaS cards, fake data, cropping one ratio out of another.
- **Text on photos:**
  - Pick the photo first.
  - Write a *subject map* (where the focal point is) as an HTML comment.
  - Set `object-position` on every image.
  - Add a local tint only if the text fails a **360 px thumbnail test**.
- **QA (`validate-social-deck.mjs`, Playwright on the computed DOM):**
  - R1 overflow
  - R2 footer collision
  - R3 heavy Swiss display type
  - R4 minimum font size (22 px body floor)
  - R5 density: at least 75 % filled, and no blank band taller than 216 px of 1440
  - R6 title line caps
  - R7 figure margin drift
  - R8 visual bounds
  - R9 a 28 px gap under display titles
- **Overflow is fixed by a ladder keyed to measured pixels.** Afterwards it checks that the fix didn't overcorrect into a big empty band.

  | Measured overflow | Fix |
  |---|---|
  | 1–40 px | Nudge |
  | 40–90 px | Compact the gaps |
  | 90–160 px | Shrink the title or one paragraph |
  | >160 px | Switch to another layout recipe |

- **Why it reaches pro quality:**
  - Curated seed templates plus recipes mean the model arranges content instead of inventing layout.
  - Density and hierarchy are checked with code rather than by eye.
- **Adopt:**
  - R1–R9 as our DOM QA.
  - The overflow ladder.
  - Recomposing each ratio with a title shortener, never cropping.
  - The subject map and the 360 px test.
- **Licence:** AGPL-3.0, so reimplement rather than copy.

### B2. higgsfield-ai/skills: YouTube thumbnail and brandkit processes (MIT, already installed at `~/.agents/skills`, symlinked into `~/.claude/skills`)

**Thumbnail skill**

- **Intake:**
  - The video's truthful promise.
  - 0–3 people, and it never picks a face silently.
  - An optional style-reference thumbnail. It is analysed by vision but **never sent as an image input**, so the output can't copy it.
  - An optional logo.
  - An optional 2–4-word headline.
  - Ratio: 16:9, 9:16 or 4:5.
  - A hard cap of 16 generations.
- **Concept gate:**
  - At least 5 concepts drawn internally from 16 frameworks (before/after, size difference, map, news clip, day-N badge …).
  - Keep the strongest *truthful* information gap that reads in under 1 second at about 120 px wide.
- **Prompt contract:** 11 blocks in a fixed order, with:
  - an explicit no-text frame;
  - subjects filling 40–60 % of the frame;
  - an identity lock per face;
  - a power-third composition;
  - a three-light portrait rig where only the rim light may be coloured;
  - a colour grade.
- **Text:**
  - The default is no text in the pixels.
  - Headlines are an HTML/CSS overlay with 5 presets, previewed live and then **baked on canvas at native resolution**.
  - Rules: cap height 12–18 % of the frame; never over a face; the stroke drawn under the fill (`paint-order`); fonts must finish loading before the bake.
- **QA and edits:**
  - After rendering, it checks identity match, stray text, exact baked text, 120 px legibility and truthfulness.
  - At most 2 retries.
  - Edits are limited to four narrow scopes (expression, background replace, background recolour, rim-light recolour), with everything else locked.

**Brandkit skill**

- **Classification:** it first decides whether the job is to apply existing assets, extend them, or create something new.
- **Brand Lock:** records each field as fixed, proposed, n/a or unknown, with an evidence label (supplied, measured, seen, inferred).
- **Approval state** lives in `state.json`.
- **New identity flow:**
  - 2–3 palettes rendered as deterministic HTML.
  - Exactly 3 vector logo marks (Recraft).
  - 2–3 font pairs rendered with the real brand name.
  - Each step needs explicit approval; silence is never taken as approval.
- **Dependency tracking:** a palette change invalidates a generated logo; a typography change doesn't.
- **Rendering split:**
  - Social graphics are GPT Image renders that take the approved logo PNG and a type specimen as references.
  - Posters and banners are deterministic SVG/PPTX/HTML, and **never** carry an AI-baked logo or exact copy.
  - 4:5 is generated at 3:4, then centre-cropped to 93.75 % height.
- **QA:**
  - A set-level matrix (asset × logo, palette, type, grid, shape, format).
  - Scripts verify hex values, fonts, positions, SVG attributes and PPTX structure.
  - **Vision is explicitly not accepted as proof of those.**
- **Caveats:**
  - Generation needs paid Higgsfield credits.
  - Its bootstrap pipes an install script into `sh`.
  - The marketplace-cards and product-photoshoot skills keep their prompts on Higgsfield's server; only the module taxonomy is reusable.
- **Adopt:** the concept frameworks, the canvas-baked overlay, the 120 px gate, the Brand Lock with evidence labels, dependency invalidation, and the rule that measurable things are checked by code.

### B3. JimLiu/baoyu-skills: full-AI prompt grammar plus a Codex backend (MIT)

The full preset lists are in Part C1. What makes it work:

- **Independent dimensions:**
  - Style (rendering rules) × layout (information structure) × palette (colours only).
  - The palette replaces background and colours but keeps the style's texture and line rules, so a client brand palette can sit on any style.
  - Named **presets** resolve to full dimension sets.
  - Precedence runs: explicit flag > preset > the style's default > none.
- **Auto-selection:** a content-signal table where the first match wins and there is an explicit fallback.
- **Compatibility matrix:** a style × layout table (✓✓ / ✓ / ✗) that warns before a render is wasted.
- **Density budgets:**
  - Points per layout (sparse 1–2, balanced 3–4, dense 5–8 with 20–30 % whitespace).
  - Cover text levels mapped to how much of the canvas stays visual: 85 % (title only), 75 % (title + subtitle), 60 % (text-rich).
- **Prompt-file discipline:**
  - Every final prompt is saved as `prompts/NN-{type}-{slug}.md` *before* the render.
  - Edits change the file first.
  - Nothing is overwritten; old versions are renamed with a timestamp.
- **Consistency:**
  - xhs: the **image-1 anchor chain**. Render the cover first, then pass it as a reference to every later card. The user's reference goes on image 1 only.
  - slide-deck: a `STYLE_INSTRUCTIONS` block is resolved once and pasted verbatim into every slide.
  - comic: a **character sheet first** (front, 3/4 and an expression strip, with a hex palette per character), compressed to JPEG q80, then passed with every page.
- **Colour guard:** hex codes and colour names are rendering guidance and must never appear as visible text.
- **References:** "passing `--ref` alone is not enough". Each reference also gets MUST/REQUIRED bullets naming what to reproduce, plus an explicit spatial split.
- **Codex backend** (`packages/baoyu-codex-imagegen`):
  - Runs `codex exec --json --sandbox danger-full-access`.
  - Validates that `image_gen` actually ran in the current thread (a stream event or a PNG in `generated_images/{thread}`), checks the PNG magic bytes and size, caches on `sha256(prompt + aspect + refs)`, and uses a cross-process lock.
  - Logs JSONL.
  - Error kinds: `timeout`, `no_image_gen_tool_use`, `invalid_png`, `agent_refused`, `lock_busy`, and more.
  - Measured cost: 50–90 s and about 110k input tokens per call. It is serialized, one call at a time.
  - Size and quality flags are ignored; the output at 16:9 was 1672×941.
- **Weaknesses:**
  - No vision judge or OCR.
  - A ban on any HTML text overlay (fine for a full-AI route, wrong for hybrid).
  - A cartoon and Chinese-market bias; a leftover "nano banana pro" line in prompts.
  - `danger-full-access` exposes the host to prompt injection from client text.
- **Adopt:** the dimension grammar, presets and compatibility matrix; the prompt file as source of truth; the anchor chain; the character sheet; the colour guard; the backend hardening checks. Use a narrow sandbox.

### B4. buluslan/gpt-image2-ecommerce: campaign lock, funnel, platform constraints, slop control (MIT)

Details are in Part C2. The core ideas:

- **A 10-field Campaign Style Lock**, prepended **byte-identical** to every prompt in a set of two or more images.
  - Fields: visual direction; palette with hex values and roles; colour temperature in kelvin; typography; background system; lighting system; layout system; icon system; product presentation; `locked_immutable`.
  - Only four things may vary per image: its purpose, the subject's action, the local composition, and short copy.
- **Funnel set:** 9 slots, generated anchor-first (the main image fixes the product anchor; drift is checked between images 1 and 2), with default set sizes of 3, 5 and 7.
- **A category × style conflict matrix**, plus a table of slop words and positive replacements.
- **8 AI tells as a vision rubric**, with a fixed severity order and one fix per round. After three failures, switch approach.
- **A text-rendering ladder** for the full-AI route: quote → spell out → "no extra words" → state count and position. After three failures, **make a text-free base and typeset it in a design tool**. That is exactly our hybrid route.
- **`compliance_check.py`:** background detected from the outer 2-px ring (quantized mode), a fill ratio, and OCR, graded pass/warn/fail with a strict mode.
- **Weaknesses:**
  - It covers e-commerce only.
  - The flattener has bugs (arrays silently empty a slot).
  - Fill is measured as pixel *area*, not extent.
  - Its own templates break its multiple-of-16 size validator.
  - It inserts a mandatory self-promotion line.

### B5. freestylefly/awesome-gpt-image-2 + wuyoscar/GPT-Image2-Skill: the full-AI template library and its QA (MIT; the cases are third-party)

- **freestylefly (33.4k★):**
  - 13 categories with case counts: Posters & Typography 90, Photography 78, UI 73, Illustration 59, Charts & Infographics 53, Products & E-commerce 42, Characters 31, Brand & Logos 27, and others.
  - 47 template blocks, each with a plain version, a JSON "for agents" version and a pitfall list.
  - A 22-entry style library listing use-when, guidance and pitfalls.
- **Routing:** category → style tag → scene tag → nearest cases; offer 2–3 options only when genuinely ambiguous.
- **Six-block prompt:** subject/task · composition/layout · style/materials · text/labels · ratio/format · constraints.
- **Pitfalls worth keeping:**
  - Hard-code all copy, or the model invents text.
  - Lock the structure before the details.
  - Imagery must physically interact with the letters.
  - Ban moodboard or grid output.
  - Lock only headlines exactly; simulate body copy.
- **Real re-runs through Codex's built-in tool** (4 cases): output was 1024×1536, 1122×1402 or 1254×1254 in 61–156 s. One case gained **unrequested branding**, and another had its colour and lettering changed.
- **Gaps:** no templates for carousels, thumbnails, quote cards or special days; the JSON variants carry "8K/UE5" boilerplate.
- **wuyoscar** is the closest thing to a full-AI QA method:
  - Canvas, ratio and layout come before the subject.
  - Fixed-region layout contracts for infographics.
  - Promotional hierarchy: name > claim > SKU > price/date > CTA > fine print.
  - The **three-glances test** (silhouette → message → detail).
  - Material, light and palette as separate controls.
  - 5–12 concrete nouns rather than adjectives.
  - A per-artifact table of what to freeze and what to check:
    - Poster: every character, repeated or missing copy, clipping, reading order.
    - UI: labels and alignment.
    - Diagram: relations and values.
    - Panel sheet: count, order, identity.
  - Always **name the failing string or region before proposing one targeted fix**.

### B6. The hybrid scaffold: guizang-yingzao (ideas only) + JuneYaooo (Apache-2.0)

These solve the core problem of our plan: making AI imagery and real typography look like **one** design, not "type pasted on a picture".

- **guizang-yingzao** gives GPT Image exactly three inputs:
  1. The corrected source photo.
  2. **One** dominant real reference.
  3. A **neutral grey typeset scaffold**. `typeset_compose.py` renders the real copy at real sizes with region markers, checks glyph coverage with fontTools (no missing-glyph boxes), aligns to real ink boxes within 0.25 % of canvas width, checks collisions, overflow and an occlusion contract, and draws a subject footprint when text sits behind the subject.
- **Thesis before references:** four sentences covering subject treatment, the background's role, how the text interacts with the subject's real contour, and one layout move that breaks double-centring.
  - The "two islands" layout (a centred subject plus a centred title that never touch) is invalid by default.
- **Text modes:**
  - Literal.
  - Reinterpreted lettering.
  - "Layered final type": a text-free AI base, then real fonts composited with a subject mask. Chosen only up front.
- **Gates and review:**
  - 8 hard gates before any paid call.
  - One readback listing 0–3 issues, with no automatic re-roll.
  - Local fixes are edits; structural fixes go back to the source.
- **JuneYaooo, real-image slots:**
  - Plan each slot from candidate regions, text volume and aspect ratio.
  - Pass a **transparent skeleton reference with only corner ticks**, and tell the model it is a positioning map, not a style reference: keep the background continuous and never draw boxes or frames.
  - Never write coordinates in the prompt; paste the real image by code.
- **JuneYaooo, editable mode:**
  - Clean plate + layers + native text.
  - Extraction ladder: A1 (original pixels) → A2 (pixels + inpaint) → B (regenerate on chroma key).
  - Edits only inside a mask.
  - Layers checked on white and on black.
  - Keep the best version; stop when a round shows no visible gain.
- **Adopt:**
  - The typeset scaffold as "image 3" on the full-AI route.
  - The corner-tick skeleton to reserve text zones on the hybrid route.
  - Layer decomposition for image-to-banner edits and for re-laying-out one design across ratios.

### B7. OpenAI's creative stack: the blueprint that matches our architecture

- **`creative-production`** (proprietary, ideas only):
  - The first pass must be generated raster imagery; SVG, Pillow or HTML "fake ads" are not allowed as finished first-pass visuals.
  - **Deterministic layers own exact text, claims, labels, charts, logos, safe zones, dimensions and filenames.**
  - "Generate the visual base first, then add the exact layers."
  - Contracts: `exact-content` (the model supplies treatment only); `deterministic-exports` (manifest plus provenance); `source-preservation`.
  - Runtime limits: 4–6 distinct directions, each a single clean asset (never a collage); ≤4 workers; ≤2 attempts; every path checked for existence and non-zero size.
  - It **bans `codex exec` inside that plugin**, which signals that `codex exec` batching isn't first-class, so our wrapper must stay defensive.
- **`frontend-app-builder`** (MIT):
  - One fresh concept per section.
  - Extract tokens, an allowed-copy list, an icon inventory and a **colour lock** (true white vs off-white; never "warm it up").
  - Build faithfully.
  - Before handoff, `view_image` both concept and render, then write a **fidelity ledger of at least 5 comparison points**.
  - Hard stops: invented eyebrows, pills or badges; an added hero tint; white turned into cream; placeholder art.
- **`design-qa`** (proprietary):
  - Source and render go into one side-by-side image, normalized first.
  - Full view, then crops.
  - Five areas: fonts, spacing, colour tokens, image quality, copy.
  - P0–P3 findings, each with evidence and a fix. Blocked until no P0–P2 remains.
- **Bundled Codex `imagegen` skill** (Apache-2.0, in openai/codex):
  - One `image_gen` call per asset.
  - Label the role of every input image.
  - A labelled spec with a verbatim `Text` field.
  - Don't invent brands, slogans or palettes; add only composition hints to a generic prompt.
  - Repeat the invariants on every edit.
  - Copy finals out of `$CODEX_HOME/generated_images`, never overwrite, and version the names.

### B8. The anti-slop canon: Anthropic `frontend-design` + `pptx` + pbakaus/impeccable (Apache-2.0 detector, installed locally)

- **The five clusters AI design defaults to** (Anthropic `frontend-design`, rewritten 2026-09-03, verified):
  1. A warm cream background (near #F4F1EA) with a high-contrast serif and a terracotta accent (near #D97757).
  2. Near-black with one acid-green or vermilion accent.
  3. Broadsheet hairlines, zero radius and dense columns.
  4. The SaaS card kit: identical rounded cards, one radius, a soft grey shadow, gradient washes.
  5. Template chrome: a tracked ALL-CAPS eyebrow above every heading, "A · B · C" meta strings, "WORD — fragment" labels, tinted near-black instead of black, monospace micro-labels.
- **Other tells:** accenting one word in a headline; 01/02/03 numbering on content that isn't a sequence.
- **The rule is conditional:** use one of these looks only when the brief asks for it.
- **Process:**
  1. Plan tokens.
  2. Ask whether a similar prompt would land in the same place; if so, revise and say what changed.
  3. Build.
  4. Screenshot and critique.
  5. Remove one accessory.
  6. **Spend boldness in one place.**
- **`pptx` (proprietary):**
  - One colour at 60–70 % visual weight plus a sharp accent.
  - One repeated motif, which may never be a colour bar.
  - Bans underlines under titles, edge stripes, cream defaults and centred body text.
  - Use fonts the QA renderer reproduces exactly, so overflow checks are real.
  - Render every page and inspect each **with fresh context (a subagent)**, because the author "sees what they expect".
- **impeccable detector** (`scripts/detector/registry/antipatterns.mjs`, 61 rules):
  - Slop rules:
    - `overused-font`: Inter, Roboto, Fraunces, Geist, Plus Jakarta Sans, Space Grotesk.
    - `ai-color-palette`: purple/violet gradients, cyan on dark.
    - `cream-palette`, `gradient-text`.
    - `flat-type-hierarchy`: every step under 1.25×.
    - `dark-glow`, `radial-halo`, `radial-spotlight-glow`.
    - `icon-tile-stack`, `hero-eyebrow-chip`, `kicker-above-heading`.
    - `italic-serif-display`, `extreme-negative-tracking`.
    - `em-dash-overuse`, `marketing-buzzword`, `aphoristic-cadence`.
    - `repeating-stripes-gradient`, `codex-grid-background`.
  - Quality rules:
    - `text-overflow`, `text-occlusion`.
    - `low-contrast`, `gray-on-color`.
    - `tight-leading`, `line-length`.
    - `tiny-text`, `undersized-ui-text` (11 px floor).
    - `all-caps-body`, `wide-tracking`, `justified-text`, `cramped-padding`.
  - DESIGN.md conformance: `design-system-font`, `-color`, `-radius`, `-font-size`.
  - Its critique mode runs **two isolated assessments**: a design review by a subagent, and detector/browser evidence. The review must finish before detector findings enter, because deterministic output anchors judgment. That is a good pattern for our vision judge.
- **Adopt:** run the detector (or a port of the static-graphics subset) on every HTML design before screenshotting; add the five clusters and the pptx list to the vision-judge checklist; judge blind first, then merge in the deterministic results.

### B9. ParthJadhav/app-store-screenshots: the only formal seam rules for chain carousels (MIT, verified)

- **Connected canvas:** exports are **crops of one connected canvas**, not separate renders. A mock-up placed across screens 2 and 3 appears as a left crop and a right crop.
- **How many cross-screen moments:**
  - Decks of 5 or more slides: one by default.
  - Decks of 8–10 slides: at most two.
  - Formal or compliance-heavy decks: zero is fine.
  - The goal is that the slides belong together, not one poster chopped up.
- **What may cross a seam:**
  - A non-critical visual may overlap the seam by **10–30 % of its width**.
  - Go beyond 40 % only for backgrounds, paths or abstract decoration (horizon, gradient, route, waveform).
  - The seam should pass through negative space, a soft shadow or a simple object body.
- **What must never cross a seam:** headlines, names, prices, legal text, ratings, CTAs, faces or critical UI. Never centre a giant object on the seam.
- **Checks:**
  - Every exported crop must pass a **one-second standalone test**.
  - Inspect the strip zoomed out, then each crop.
  - A 160 px thumbnail squint test.
- **Composition:** the headline takes the top 30–40 %; never repeat a layout on adjacent slides; invert 1–2 slides for rhythm.
- **Adopt** as the rulebook for our panoramic and chain carousel module (see E6).

### B10. The rendering stack: headless Chrome as the one visual engine, with print back-ends only where needed

**Why Chrome wins for our quality bar.** Everything else is either a CSS subset (Satori, and Takumi to a lesser degree), not CSS at all (Typst), or behind on modern CSS (WeasyPrint). Chrome is the only engine with all of these at once:
- HarfBuzz shaping, which matters for Bengali, Arabic and Devanagari;
- variable and colour fonts;
- `text-wrap: balance` (up to 6 lines) and `pretty` (last 4 lines only);
- `hyphens: auto` with a `lang` attribute;
- `text-box` trim (optically centred badges);
- `initial-letter`;
- grid, container queries, blend modes and filters.

**What Chrome lacks:** CMYK, spot colours, PDF/X, `bleed`/`marks` and `hanging-punctuation`.

**Settings** (from the Playwright/Puppeteer defaults, Chrome issues and the CDP docs):
- **Launch flags:** `--force-color-profile=srgb` (Playwright and Puppeteer add it by default), `--font-render-hinting=none`, `--hide-scrollbars`.
- **Viewport and scale:** make the viewport exactly the artboard. Device scale factor: 1 for exact social pixels, 2 for masters, **3.125 (= 300/96) for 300-dpi print rasters**.
- **Readiness:** call `document.fonts.load()` for each declared face (fonts load lazily), then wait for `document.fonts.ready`, `img.decode()` and two animation frames. Then assert `document.fonts.check()`, **and use `CSS.getPlatformFontsForNode` to fail on silent fallback** (for example, Bengali text quietly set in a system font).
- **Capture size limit:** keep every capture ≤16,384 px per side. Playwright issue #13496 reports failures above that, and an empty WebP above 16,383. Per-slide `clip` captures avoid this.
- **PDF:** `@page {size; margin:0}`, `preferCSSPageSize`, `printBackground`, `tagged`. For print, make the page trim + 2 × bleed, then set TrimBox and BleedBox with pdf-lib or qpdf.
- **Performance:** keep one warm browser. A cold start is 0.7–2.8 s; a warm PDF is about 0.2 s.

**Print CMYK routes** (use them only when the printer requires CMYK; many accept RGB with a proof):
- (a) **Vivliostyle CLI** `--press-ready --bleed 3mm --crop-marks` → PDF/X-1a via Ghostscript. Run it as a separate CLI because it's AGPL. It flattens transparency, so rasterize shadows on purpose.
- (b) **WeasyPrint** `pdf/x-4` with `device-cmyk()`, for templates written in its CSS subset. It needs Python 3.10 or newer.
- (c) **Typst** for long documents with spot colours.
- (d) **Ghostscript** RGB → CMYK conversion as the last step.
- Always embed the printer's ICC profile (FOGRA39 or US Web Coated SWOP).

**Resizing:**
- Never crop a finished design; **re-lay it out** from the same content and tokens. A few layout patterns (stacked, split, overlay, text band) are chosen by aspect ratio with container or aspect-ratio queries.
- Compute each photo's focal point **once**, then apply it as `object-position` in every format. Sources, in order of preference: Apple Vision saliency, face detection, smartcrop with a face boost, sharp `attention` as the last resort.
- **Text fitting** is an in-page binary search on `font-size` with a minimum and maximum per role. At the minimum, the LLM shortens the copy instead of shrinking further (Bannerbear `auto_fit`, Templated min/max, Takumi `text-fit`).

**Slicing a seamless carousel:**
1. One master artboard, N·W × H, with a seam-guide overlay that is hidden during capture.
2. Check every text node's `getBoundingClientRect` against x = k·W ± 60–80 px.
3. Capture each slide with `clip {x: i·W, …}` from the same layout. This gives pixel-exact seams and never exceeds the 16,384 px limit.
4. For LinkedIn, each PDF page is a W×H window onto the master (`overflow:hidden; translateX(-i·W)`), which keeps the text vector.
5. Compare the edge columns of adjacent slices to catch 1 px gaps from fractional scaling.

**Infographics:** compose in code. IGenBench shows the best image model is fully correct on only about half of infographics.
- **Layout:** AntV Infographic syntax (lists, timelines, comparisons, hierarchies).
- **Charts:** ECharts SSR or Vega-Lite (vl-convert) inside the same page, so the brand fonts apply.
- **Sketchy diagrams:** D2 sketch mode or Rough.js.

**Optional speed path:** Takumi, once a template has passed in Chrome. Verify pixel parity on samples first; its Indic support is untested.

**Animated versions:** HyperFrames (Apache-2.0, installed) renders the same HTML to MP4 for Stories and Reels.

**Gaps observed in the in-progress `~/.claude/skills/codex-design`** (read-only):
- `--force-color-profile=srgb` is not in its Chrome launch.
- No `getPlatformFontsForNode` fallback check.
- No 16,384 px capture guard or per-slide `clip`.
- No CMYK route; Ghostscript, Vivliostyle and WeasyPrint are not installed, and WeasyPrint needs Python ≥3.10.
- No pinned emoji font.

**Already in place there:** `printToPDF` with box fixing, `fonts.ready`, vision-deficiency views, balance/pretty wrapping, 4:4:4 JPEG at quality ≥90, sRGB tagging, and Apple Vision saliency and masks.

---

## Part C: What the earlier local captures contain (`scratchpad/{baoyu,bulu,free,conard,fei,alek}` plus the other capture folders)

**Folder → source repo:**

| Folder | Source repo | Files read | Notes |
|---|---|---|---|
| `baoyu` | JimLiu/baoyu-skills | 26, all | |
| `bulu` | buluslan/gpt-image2-ecommerce | 17, all | |
| `free` | freestylefly/awesome-gpt-image-2 (`gpt-image-2-style-library`) | 4 | Byte-identical to the live repo |
| `conard` | ConardLi/garden-skills (`gpt-image-2`) | 9 | 12,591★, MIT, last push 2026-07-12, stale |
| `fei` | feiskyer/claude-code-settings (`gpt-image-skill`) | — | 1,653★, MIT |
| `alek` | AlekseiUL/gpt-image-2-5-agent-kit | — | 24★, MIT |

The other capture folders were skimmed for design-specific rules: smixs, wuyo, you, ning, june, shin, sk, jez, misc, wang, uzen, cb.

**Caveat:** several referenced files were never captured. These include the baoyu per-style spec files, 35 of bulu's 39 templates, and 89 of conard's ~93 templates. The name lists below are complete; the full rendering specs exist only for the files that were captured.

### C1. baoyu (MIT): style, layout and preset libraries

**Shared scaffolding (all six design skills)**

- **Backend order:** Codex-native `imagegen` → `codex-imagegen` through `codex exec` → Cursor `GenerateImage` (ratio stated in the prompt) → any other native tool → ask the user.
- **Hard bans:**
  - Never replace a raster image with SVG/HTML.
  - Never repair text inside a generated bitmap; regenerate, use a layout with less text, or let the user choose.
  - A text-fix regeneration writes a **new** prompt file and a **new** output path, so the flawed candidate is kept.
- **Confirmation:** the default is to confirm before generating. It is skipped only on explicit wording (`--yes`, `--quick`, "generate directly"), and the skipped choices are stated afterwards.
- **Files:** `<skill>/<slug>/` holds `source-*`, `analysis.md`, `outline.md`, `prompts/NN-{type}-{slug}.md` and `NN-{type}-{slug}.png`. There is a backup-before-overwrite rule, and slugs never change when items are renumbered.
- **References:** `direct` (sent as an image), `style` (traits appended to the text) or `palette` (hex values appended). They are recorded in frontmatter and each file's existence is checked.
- **Batching:** prompts are written before any batch; dependencies go first (the anchor image, the character sheet); batch size defaults to 4 (1–8); one retry.
- **Preferences:** an `EXTEND.md` lookup order of project → XDG → home.

**xhs-images: 3:4 card series, 1–10 cards, `2k` quality**

- **Roles:**
  - Cover: a hook, sparse.
  - Content cards: balanced, dense, list, comparison or flow.
  - Ending: a CTA or summary.
- **Styles (12):**
  - `cute` (the default)
  - `fresh`
  - `warm`
  - `bold`
  - `minimal`
  - `retro`
  - `pop`
  - `notion`: line-art knowledge cards
  - `chalkboard`
  - `study-notes`: a photo of handwritten notes
  - `screen-print`: halftone, 2–5 flat colours, a duotone pair, misregistration, figure-ground inversion, stencil type, one conceptual focal point
  - `sketch-notes`: macaron pastels on cream, wobbly lines
- **Layouts (8):**

  | Layout | Content |
  |---|---|
  | sparse | 1–2 points |
  | balanced | 3–4 |
  | dense | 5–8 points, 20–30 % whitespace |
  | list | 4–7 |
  | comparison | — |
  | flow | 3–6 |
  | mindmap | 4–8 |
  | quadrant | — |

- **Palettes (3; they replace colours only):**

  | Palette | Background | Zones | Accent |
  |---|---|---|---|
  | macaron | #F5F0E8 | #A8D8EA, #D5C6E0, #B5E5CF, #F8D5C4 | coral #E8655A |
  | warm | #FFECD2 | #ED8936, #C05621, #F6AD55, #D4A09A | #A0522D |
  | neon | #1A1025 | cyan, magenta, green, pink | yellow |

- **Presets (26), grouped:**

  | Group | Presets |
  |---|---|
  | Knowledge | `knowledge-card`, `checklist`, `concept-map`, `swot`, `tutorial`, `classroom`, `study-guide`, `hand-drawn-edu`, `sketch-card`, `sketch-summary` |
  | Lifestyle | `cute-share` (fallback), `girly`, `cozy-story`, `product-review`, `nature-flow` |
  | Impact | `warning`, `versus`, `clean-quote`, `pro-summary` |
  | Trend | `retro-ranking`, `throwback`, `pop-facts`, `hype` |
  | Poster | `poster`, `editorial`, `cinematic` |

- **Outline strategies:**

  | Strategy | Sequence | Typical cards |
  |---|---|---|
  | A Story-driven | hook → problem → discovery → experience → conclusion | 4–6 |
  | B Information-dense | conclusion → info card → pros/cons → recommendation | 3–5 |
  | C Visual-first | hero → details → lifestyle → CTA | 3–4 |

- **Smart Confirm:** Path A (quick), Path B (5 pre-filled questions) or Path C (three alternative outlines, each with a `style_reason`).
- **Auto-selection:** keyword table → style/layout/preset, first match wins. For example, warning/important → `bold` + `list`; knowledge/SaaS → `notion` + `dense`.
- **Style × layout matrix (✓✓/✓/✗):** `study-notes` + `sparse` is ✗; `screen-print` + `dense`/`mindmap` is ✗.
- **Text:** hand-lettered, in the content's language, capped by layout density.
- **Prompt skeleton:** Specs → Core principles → Text style → Language → STYLE (palette hex, elements, typography) → LAYOUT (density, whitespace %, structure) → CONTENT (position "page 3 of 6", message, text, visual concept) → watermark.

**cover-image: one cover, 16:9 (default), 2.35:1, 4:3, 3:2, 1:1 or 3:4**

- **Six dimensions:**

  | Dimension | Values |
  |---|---|
  | Type | `hero` (focal visual 60–70 %) · `conceptual` · `typography` (title ≥40 % of area) · `metaphor` · `scene` · `minimal` (≥60 % whitespace) |
  | Palette | warm, elegant, cool, dark, earth, vivid, pastel, mono, retro, duotone, macaron |
  | Rendering | flat-vector, hand-drawn, painterly, digital, pixel, chalk, screen-print |
  | Text level | none · title-only (85 % visual) · title-subtitle (75 %) · text-rich (60 %; 2–4 tags) |
  | Mood | subtle (contrast/saturation −20–30 %) · balanced · bold (+20–30 %) |
  | Font | clean (geometric sans) · handwritten · serif · display |

- **Composition:** 40–60 % whitespace; the visual at centre or left, with the right side free for the title; one focal element plus 1–2 supporting.
- **Icon vocabulary** by theme: tech, ideas, growth, security.
- **References:** each reference yields MUST bullets (exact hex, letterforms, "bottom 30 % dark banner") plus an integration split (e.g. a 65 % illustration area over a 35 % banner).
- **The only post-render check anywhere in baoyu:** confirm the required reference elements are visible; if not, strengthen the prompt and regenerate.
- **Title fidelity:** never invent or modify the title.

**infographic: one image, 16:9, 9:16, 1:1 or a custom ratio**

- **Layouts (21):** linear-progression, binary-comparison, comparison-matrix, hierarchical-layers, tree-branching, hub-spoke, structural-breakdown, bento-grid (the default), iceberg, bridge, funnel, isometric-map, dashboard, periodic-table, comic-strip, story-mountain, jigsaw, venn-diagram, winding-roadmap, circular-flow, dense-modules.
- **Styles (22):** craft-handmade (the default), claymation, kawaii, storybook-watercolor, chalkboard, cyberpunk-neon, bold-graphic, aged-academia, corporate-memphis, technical-schematic, origami, pixel-art, ui-wireframe, subway-map, ikea-manual, knolling, lego-brick, pop-laboratory, morandi-journal, retro-pop-grid, hand-drawn-edu, retro-popup-pop.
- **18 recommended pairs**, for example:
  - timeline → linear-progression + craft-handmade
  - metrics → dashboard + corporate-memphis
  - technical → structural-breakdown + technical-schematic
  - product guide → dense-modules + morandi-journal
- **Structured-content step first:** learning objectives; for each section, the key concept, the content **verbatim**, a visual and labels; data and quotes kept exact; nothing added.
- **Base prompt:** a separate "Text labels (in {LANGUAGE})" list, which is useful as the OCR diff target.

**slide-deck: 16:9 "reading" decks → PNG + PPTX + PDF**

- **Slide count by source length:** <1k words → 5–10; 1–3k → 10–18; 3–5k → 15–25; >5k → 20–30.
- **Presets (17), each a texture × mood × typography × density combination:**

  | Preset | Note |
  |---|---|
  | blueprint | the default |
  | chalkboard, corporate, minimal, sketch-notes, hand-drawn-edu, watercolor | |
  | dark-atmospheric, notion, bold-editorial, editorial-infographic | |
  | fantasy-animation, intuition-machine, pixel-art, scientific | |
  | vector-illustration, vintage | |

- **Base prompt rules:**
  - One message per slide, at most 3–4 text elements.
  - No page numbers or logos in the image.
  - AI copy words are banned ("dive into", "explore", "journey").
  - Z-pattern and rule of thirds.
  - `STYLE_INSTRUCTIONS` is pasted verbatim into every slide.

**article-illustrator**

- **Types:** infographic, scene, flowchart, comparison, framework, timeline.
- **Per-type templates** built from ZONES / LABELS / COLORS / STYLE / ASPECT. **LABELS must carry the article's real numbers and terms.**
- **Palettes:** mono-ink is #FFFFFF / #1A1A1A with semantic accents (coral = risk, teal = solution, lavender = neutral) kept **under 10 % of the canvas**.

**comic**

- **Character sheet first:** front, 3/4 and an expression strip, with hex values per character.
- **Panel specs:** 1–2 px black borders, 8–12 px gutters, varied camera angles.
- **Bubble and caption conventions.**
- **Concept → metaphor table:** data flow → particles; proof → puzzle pieces.

### C2. bulu (MIT): Campaign Style Lock, funnel, platform constraints, slop and AI-tell control

**Campaign Style Lock**

Built for any set of 2 or more images, and **prepended byte-identical**:

| # | Field | Default when no brand is supplied |
|---|---|---|
| 1 | `visual_direction` (exactly one: photo, 3D/CGI or editorial illustration) | commercial product photography |
| 2 | `color_palette` (2–3 main + 1 accent, hex with roles) | #FFFFFF bg / #F5F5F5 surface / #2C2C2C text / #0066CC accent |
| 3 | `color_temperature` (K) | ≈5500 K |
| 4 | `typography` (heading, body, emphasis, fallbacks) | Inter Bold/Regular/SemiBold; Helvetica; CJK Source Han / Noto |
| 5 | `background_system` | light-grey sweep #F5F5F5→#E8E8E8 |
| 6 | `lighting_system` (the same direction across the set) | soft top-left daylight + subtle right rim |
| 7 | `layout_system` | rule of thirds, left-aligned text, generous whitespace |
| 8 | `icon_system` (**never mix line and filled**) | thin line, 2 px stroke, 4 px radius, accent colour |
| 9 | `product_presentation` | front 3/4, 60–70 % of frame, no edge crop |
| 10 | `locked_immutable` (the most important field) | palette hex, fonts, background hue, light direction, icon style, angle |

- **Per-image freedoms (only four):** purpose, action, local composition, short copy.
- **Category overrides** change only the palette and temperature, for example:
  - electronics: #0066CC, 6500 K
  - beauty: #C97B63, 4500 K
  - food: #D4351C, 4000 K
  - jewellery: #D4AF37 on white or near-black, 5500 K
- **Region tables** cover US, EU, SEA, CN and ME: aesthetics, a minimum of 2 skin tones per set for US/EU, taboos (e.g. ME: no pork, alcohol or religious symbols) and holidays. **Holiday sets get a temporary lock with its own `campaign_id`**, archived afterwards.
- **Caution:** treat the region tables as hints; they contain stereotypes.

**Funnel set: 9 slots, generated anchor-first**

| # | Slot | Role |
|---|---|---|
| 1 | Main | wins the click; Amazon: white, no text, ≥85 % fill |
| 2 | Lifestyle | the buyer imagines owning it |
| 3 | Selling-point infographic | 3–6 points; icons + short copy |
| 4 | Macro detail | proves quality |
| 5 | Comparison / before-after | **the competitor rendered in neutral grey** |
| 6 | Size / spec | cuts returns |
| 7 | Packaging / gift | |
| 8 | UGC / trust (optional) | |
| 9 | Brand story (optional) | |

- **Default set sizes:** 7 by default; "3" means slots 1–3; "5" means 1, 2, 3, 5, 7.
- **The driver decides which slots get the investment:**
  - visual → 1, 2, 4
  - pain point → 1, 3, 5
  - emotional → 1, 2, 9
- **Fast track:** one prompt for the whole set, then redo the weak images with a lock distilled from the good ones.

**Platform constraints (L1)**

| Platform | Rules |
|---|---|
| Amazon main | pure RGB 255 white; no text, logo or border; 1:1; ≥1000 px (1600+ for zoom); ≥85 % fill |
| TikTok Shop | 1:1 or 3:4; ≥540 px short side (1080 advised); an AIGC toggle (since 2026-02-11) |
| Shopify | 2048² advised; strips EXIF, IPTC and C2PA on upload |
| AliExpress / Temu | pure white; 1:1; ≥800 px; CN implicit-watermark rules |

- **L2, AI disclosure:**
  - Image type A (no people), B (retouch), C (realistic AI people: highest risk), D (real-person replica: refuse).
  - Disclosure copy is provided in 6 languages.
- **L3, violations:**
  - Invented certifications (UL, CE, FCC), inflated specs, medical claims.
  - Main-image bans.
  - Refusals: real-person replicas, stripping provenance, coaching disclosure evasion.

**Craft**

- **Five-element brief:** subject + material + explicit light + lens/framing + finish.
- **Light:**
  - Formula: quality + direction + position + intensity.
  - Category light: electronics hard side or top; food warm side or 45° back; jewellery spot + soft.
  - Material pairing: metal under soft light reads as grey plastic.
- **Composition:** eye order is contrast → brightness → faces/gaze → leading lines; three layout types (hero, lifestyle, infographic); callouts go around the product, never over it.
- **Text ladder:**
  1. Quote the text (caps where the design allows).
  2. Spell it out letter by letter.
  3. Say "no extra words".
  4. State the count and position.
  - After three failures, **generate a text-free base and typeset it in a design tool.**
- **Category visual keys:**
  - beauty = believable skin
  - electronics = material feel
  - food = moisture and steam
  - jewellery = fire and lustre

**Style blacklist**

- **Category × style matrix.** For example:
  - electronics: no florals or script type; backgrounds no darker than #2A2A2A
  - food: no neon blue or dark moody
  - jewellery: background at an extreme, never mid-grey
- **Slop word → replacement:**

  | Slop | Replacement |
  |---|---|
  | perfect / flawless | natural texture, even surface |
  | stunning, gorgeous, breathtaking | the concrete quality |
  | 8K / masterpiece / award-winning / Octane | delete |
  | hyper-realistic | delete, or "natural photographic look" |
  | cinematic | concrete light + depth of field |
  | epic, magical, dreamy | the concrete atmosphere |
  | polished, retouched (UGC) | candid, unedited |

  "Photorealistic" is allowed **once**, as a statement of the medium.
- **8 AI tells**, each with a counter-prompt:
  1. plastic skin
  2. symmetry
  3. fused edges (max 4 callout boxes)
  4. extra fingers (hide or crop hands first)
  5. dead eyes
  6. flat light
  7. impossible background
  8. gibberish text or phantom watermarks
- **Rules:** one fix per round, in severity order; after 3 failures, change approach; the test is "would a buyer call it fake at first glance?"

**`compliance_check.py`**

- **Background detection:** background colour = the 16-level quantized mode of the outer 2-px ring, on an image downscaled to ≤300 px.
- **White ratio:** pass ≥0.95, warn ≥0.80.
- **Foreground fill:** measured against the background distance threshold.
- **OCR:** English only; any text fails under a "forbid" policy.
- **Thresholds (normal/strict):**

  | Platform | White tolerance | Fill |
  |---|---|---|
  | Amazon | 12 / 6 | 0.85 / 0.90 |
  | TikTok | 25 / 12 | 0.70 / 0.80 |
  | Shopify | 40 / 20 | n/a |

- **Output:** a JSON envelope; exit 0 = pass, 1 = warn/fail, 2 = bad input.
- **Bug:** fill is measured as pixel *area*, but Amazon means *extent*. An 85 % extent is about a 72 % area.

**Evals, routing, motion, sizes**

- **Evals:** 11 cases tagged [auto] or [human], covering exact text via OCR (≥0.85 confidence), set drift, 8 colourways with silhouette similarity ≥0.9, UGC realism, a category conflict and translation. There is no runner.
- **Routing:** Sunburst for anything that must survive edits and for finals; Flare for drafts. Draft tier → final tier.
- **Motion GIF:**
  - 16 frames in one 4×4 grid (consistency comes from a single generation).
  - A 60° orbit with slow-in/fast-out easing, played forward then reversed.
  - 500–640 px wide, ≤3 MB; WebP for semi-transparency.
- **Size validator (`imagegen.sh`):** both sides multiples of 16; ≤3840 px per edge; ratio ≤3:1; 655,360–8,294,400 px.
- **Legal render sizes** for common targets (render at the legal size, then downscale):

  | Target | Render at |
  |---|---|
  | 1080×1350 | 1088×1360 |
  | 1080×1920 | 1152×2048 |
  | 1080² | 1088² |
  | 3-slide 4:5 panorama | 3264×1360 (2.4:1) |
  | 3-slide square panorama | 3072×1024 (3:1) |

  **Four or more 1:1 or 4:5 slides can't be one generation**; chain overlapping extend-canvas edits instead.

### C3. free: freestylefly `gpt-image-2-style-library` (MIT; cases third-party)

- **Templates** (`templates.md`): 13 categories, 47 blocks. Most categories have a plain template, an agent JSON template (`structure`, `style`, `content`, `constraints`) and a pitfall list.
  - Posters & Typography (10 blocks): a general poster; a sports campaign where a hero prop is the compositional anchor; a conceptual typography poster where the title is the hero and the letterforms are spelled out by weight, width, contrast, spacing, distortion, edge and ink; a 4–6 colour role system; single-artifact guards; a movie-poster JSON; and more.
  - Charts & Infographics (3): 3–5 modules; a scientific scale diagram with 6–8 frames plus units.
  - UI (4), including a social-screenshot template (platform, mode, exact body text, engagement numbers, UI layers).
  - Products (3), Brand & Logos (6): a full identity package; a touchpoint board; a brand-persona comic; a "don't" rules list.
  - Documents (3): a brochure system with a whole-book preview; lock headlines exactly and simulate body copy.
- **Style library, 22 entries** (id → key guidance → pitfall):

  | Entry | Key guidance | Pitfall |
  |---|---|---|
  | `ui-screenshot-system` | lock platform, ratio, exact text | — |
  | `infographic-engine` | 3–5 modules, short labels | long paragraphs |
  | `poster-layout-system` | lock subject, headline, palette, ratio | moodboard output |
  | `conceptual-typography-poster` | type as hero, exact spelling | — |
  | `product-commerce-visual` | selling points, material, light | random props |
  | `brand-identity-package` | palette, type, touchpoints | inconsistent logo variants |
  | `brand-touchpoint-board` | — | — |
  | `document-publishing` | columns | tiny dense text |
  | `concept-product-breakdown` | — | — |

  The other entries cover photo, character, history and architecture.
- **Routing:** detect language → classify the output type → match category → style tag → scene tag → cases. If one template clearly wins, use it; otherwise offer 2–3.
- **Six-block prompt:** subject · composition · style/materials · text/labels · ratio · constraints.
- **Real cases** (4 re-runs through Codex): hashes, dimensions and time were recorded. Unrequested branding and lettering changes appeared, which is proof that QA must detect **unrequested text**.

### C4. conard: ConardLi/garden-skills `gpt-image-2` (MIT, stale since July)

- **About 93 templates in 18 categories.** Captured: premium-studio-product, professional-portrait, product-retouching, portrait-local-edit.

  | Category | Templates |
  |---|---|
  | Posters & campaigns | brand-poster, campaign-kv, banner-hero, editorial-cover, character-catalog-poster, lineup-comparison-poster, … |
  | Typography | title-safe-poster, bilingual-layout-visual |
  | Branding & packaging | brand-identity-board, mascot-brand-kit, full-mascot-brand-doc (18–24 modules), cosmetic-packaging, beverage-label-design |
  | Infographics | legend-heavy, hand-drawn, bento-grid, comparison, step-by-step, kpi-dashboard |
  | Grids | banner-grid-2x2 (four unified banners in one image), ad-banner-multi-grid |
  | UI mockups | short-video-cover-ui (YouTube and Douyin covers), social-interface-mockup |
  | Others | academic figures (no invented numbers, ≤3 colours), technical diagrams ("use Mermaid when it must be editable") |

- **Template file anatomy:** scope; when to use and when not; question order; a master JSON (`type`, `goal`, `subject`, `scene`, `layout`, `style`, `details`, `constraints{must_keep, avoid}`); parameter and auto-fill strategy; variants; an avoid list.
- **Fields have three classes:**
  - **Must-ask** changes the result materially: subject, product, platform.
  - **Defaultable:** background, secondary copy, lighting.
  - **Randomizable:** plausible filler.
  - Placeholder syntax: `{argument name="…" default="…"}`.
- **Premium studio product rules:**
  - The product is the only hero, at about 45 % of the frame.
  - At most two props, in its own colour family.
  - A slogan of ≤8 characters that never covers the product.
  - One light direction.
  - Category auto-fill: perfume dark with top light; cosmetics cream with soft front light; jewellery black with a rim; electronics deep space with cool blue.

### C5. fei and alek

- **fei:** a thin OpenAI Images wrapper with legacy sizes. Its documented edit command fails because of a parser bug. Not useful.
- **alek (AlekseiUL):**
  - **Composable presets:** `thumbnail` (one focal point, strong contrast, readable hierarchy, text sized for export), `product`, `no-text`, `brand-style`, `edit`, and a script-specific text preset. Conflicting presets are rejected.
  - **Typed reference roles in a fixed order:** `edit_base` → identity → style → logo → layout → general, ≤5 in total.
    - Identity: don't copy pose, clothes or background.
    - Style: palette, materials, light and density only; no people or lettering.
    - Logo: exact shape, colours and letters.
    - Layout: arrangement and scale only.
  - **Dry run by default.**
  - **Receipts** record *requested vs actual*. A request for 1536×864 came back **1672×941** on both runs, so always measure before an exact-size layout.
  - **Local size policy:** multiples of 16, ≤3840, ≤3:1.

### C6. Other capture folders: design-specific rules

- **smixs (CC-BY):**
  - Booster words banned (4K, 8K, masterpiece, flawless, stunning).
  - Replace style tags with facts ("cream background, heavy black sans, asymmetric type block, one hero object").
  - Quality ladder: medium by default; high for dense text, infographics and brand assets; xhigh for print.
  - Layout taxonomy for text visuals: linear, comparison, hierarchical, radial, grid, spatial.
  - Viral-thumbnail recipe: face kept, expression changed, subject pointing to one side, a bold arrow, a huge outlined headline, a blurred background.
- **wuyo:** covered in B5. Its size shortcuts: 1k square for social, portrait for posters, 2k for print; sizes above 2560×1440 are experimental.
- **you (YouMind skill):** the 15,678-prompt category sizes signal demand (see A3). It recommends at most 3 prompts verbatim, each with its sample image, then remixes.
- **ning (codex-ppt):**
  - The McKinsey style file is a model house-style brief: a hex palette plus rules for it; banned elements (orange accents, neon, gradients); a metaphor library (funnel = conversion, ladder = maturity, flywheel = growth).
  - **Density caps by role:** title slides have 1 giant title, 2–4 tags and 1 metaphor, and ≥5 modules is forbidden; analysis slides have 3–6 modules, and ≥8 is forbidden.
  - It treats HTML overlays as failures, which is the opposite of our hybrid route.
- **june:**
  - A layout-bank `.layouts.json` sidecar per style: `visual_signature`, `content_capacity`, `best_for`/`avoid_for`, `variation_tags`, and a **JSON Schema with length caps per slot** (Swiss: cover title ≤24, metrics 2–5 with labels ≤16, quote 6–56 characters).
  - Swiss-grid rules: 12 columns; ≤6 elements; ≥50 % whitespace; one solid colour block; big numbers ≥30 % on data slides; no rounded corners, shadows, gradients or emoji; no centred body text.
  - Regex routing by content shape: metrics, timeline, comparison, process, table, list.
  - It reads the PNG header, and if the ratio is off by >15 % it regenerates (at most 2 times).
- **misc/liang (e-commerce detail images):**
  - Numeric product occupancy: 35–40 % white-background main image; 25–30 % benefit image; 20–25 % lifestyle; 40 % feed ad; 45 % search ad.
  - Whitespace ≥45–50 %.
  - Copy in three layers: a promise of ≤15 characters, 2–3 proof icons, a CTA of ≤8 characters.
  - Set rhythm: alternate 2–3 background tones; ≥3 angles across 5 hero images; never three identical angles in a row; full shots ≤40 %.
  - Type 28–48 / 16–20 / 10–14 pt.
  - Zoom to 200 % to check strokes.
  - Never invent certifications.
- **misc/yingzao:** see B6.
- **misc/image-use:** reports that the Codex subscription backend **rewrites** the image tool request: the model becomes `gpt-image-2-codex`, and quality, size and background become auto. This confirms that we must measure and post-process for exact sizes.
- **wang:**
  - Codex `size` is not guaranteed, although writing the size and ratio into the prompt helped.
  - `background=opaque` plus a transparency prompt produced a **fake checkerboard**.
  - Complex CJK glyphs failed.
  - Transparency pipeline: chroma matte with an auto-sampled key colour → two-background (black/white) extraction for glass and glow → strict verification (halo, residue, fake checkerboard).
- **cb (OpenAI cookbook image evals):**
  - Judge rubrics:
    - UI mockup: instruction and text are gates; layout and affordance are scored 0–5 and must be ≥3.
    - Marketing flyer: instruction and text gates; hierarchy, brand fit and visual quality ≥3.
    - Logo edit: every criterion ≥4.
  - **Never average; when unsure, choose the lower score.**
  - Strict JSON output; a crop tool for zoom.
  - OCR set-diff with a **known bug**: " - " vs "•"/"–". Always normalize punctuation before diffing.
- **sk (openai/skills `hatch-pet`):**
  - A brand-discovery worker returns name, a ≤45-word brief, a visual seed, an avoid list and sources.
  - Layout-guide images are invisible construction references, and any output that copies the guide is rejected.
  - Contact-sheet QA by a lightweight worker; repair the smallest failing scope.
- **shin:** a size mapper (ratio + 1K/2K/4K → multiples of 16 under the pixel cap); a purpose table (book and album covers get space for type).
- **jez:** platform ratios (OG and LinkedIn 1.91:1, Pinterest 2:3, FB cover 2.63:1); a vision critique that returns PASS or issues, which are appended as negatives.

---

## Part D: Trends and use cases, 2025–2026

**How to read this part:**
- Every claim carries a URL and date.
- The grades are OFFICIAL (platform documentation), DATA (large post analyses), SURVEY (a named sample), and VENDOR (tool or agency blogs; treat these as hypotheses).
- The session's web-search quota ran out partway through. Some official pages also returned 403, so a few specs rest on 2026 third-party guides. Those are marked.

### D1. What people and agencies actually make at volume

**Carousels have the highest engagement; video has the highest reach.**
- Instagram (DATA):
  - Socialinsider, 35M posts in 2025: carousels 0.55 %, Reels 0.52 %, images 0.37 % (Q2-2026: 0.50 / 0.48 / 0.33) (socialinsider.io/social-media-benchmarks/instagram).
  - Buffer, 52M posts: median engagement 6.90 % for carousels vs 4.44 % for images vs 3.31 % for Reels, although Reels reach more people (buffer.com/resources/state-of-social-media-engagement-2026, 2026-03-05).
- LinkedIn document (PDF) carousels are the top-engaging format (Socialinsider, 7.00 % across 1.3M posts).
- TikTok photo mode: the evidence conflicts (Fanpage Karma, June 2025 vs Buffer), so test it for step-by-step content.
- Instagram has allowed 20 slides since August 2024 (Mosseri).

**Xiaohongshu image-text notes (VENDOR)**
- Format: 1080×1440 (3:4), with 1242×1660 for dense cards and one ratio per note.
- Structure: 6–9 images (cover → core → steps → summary/CTA).
- Cover: a 3–7-character title at ≥80 px in the upper third; text under ~40 pt is unreadable in the feed.
- Series: 2–3 fixed colours per account and one filter (huasheng.ai 2026-02-01; linkbloom.ai 2026-09-03).
- Demand signal: HisMax/RedInk (sentence → Xiaohongshu post) has 5.6k★ since Nov 2025.

**Faceless YouTube and thumbnails**
- YouTube's **"inauthentic content" update (2025-07-15)** demonetizes mass-produced or templated work, naming image slideshows and AI content made from generic templates (support.google.com/youtube/answer/1311392). **A series template must still produce real variation for each video.**
- AI-made thumbnails and infographics count as production help and **need no disclosure** (support.google.com/youtube/answer/14328491).
- **Test & Compare** (support.google.com/youtube/answer/16391400):
  - up to 3 thumbnails and/or titles;
  - the winner is chosen by *watch-time share*, not CTR;
  - title testing went global in Dec 2025.
  - So deliver 2–3 **genuinely different** variants.

**Posters and infographics: image models now render text**
- OpenAI (OFFICIAL / press):
  - gpt-image-2 reached the API on 2026-04-21, pitched for "structured" posters and infographics.
  - ChatGPT Images 2.0 launched 2026-04-22 with better non-Latin text; Bengali and Hindi are claimed and **must be verified per job**.
  - **GPT Image 2.5 (`sunburst` / `flare`, snapshot 2026-09-08)** was added to openai-python on 2026-09-08. It supports native transparency, `xhigh`/`max` quality, sizes in multiples of 16, ratios from 1:3 to 3:1, and up to 3840×2160 (above 2560×1440 is experimental). **It is not confirmed whether Codex's built-in `image_gen` uses 2.5.**
- Google (OFFICIAL / press):
  - Nano Banana Pro (2025-11-20): legible multilingual text, Search-grounded infographics, 4K, and up to 14 inputs / 5 consistent people.
  - Nano Banana 2 (2026-02-26).
- Others:
  - FLUX.2 (2025-11-25; 10 references).
  - Qwen-Image-2.0 (2026-02-11; slides and posters in one pass; the original model is Apache-2.0 with 8.4k★).
  - Seedream 4.5 (dense text).
  - Ideogram 4.0 (2026-06-03; open weights with JSON layout and bounding boxes, VENDOR; non-commercial without a licence).
  - Recraft V4 (Feb 2026; native SVG).
- Even Google's launch post says to verify facts in generated infographics.

**Special-day posts**
- AI holiday ads draw the most backlash: Coca-Cola's AI Christmas ad was criticized again (Forbes, 2025-11-04), and McDonald's NL pulled its AI Christmas ad within days (NBC, 2025-12-11).
- Canva's 2026 trends report shows local typography searches rising ("Hindi typography" +17 %, "Desi" +26 %) and an "Imperfect by Design" theme (campaignbrief, 2025-12-15).
- Dates and greetings vary: Eid depends on moon sighting and differs by country; Diwali runs 5–6 days and is centred on Kali Puja in Bangladesh and eastern India. **Keep dates "pending" until confirmed for each country.**

**E-commerce**
- **Amazon main image** (sellerlabs 2026 guide; Seller Central blocked the fetch): a real photo of the actual product; RGB 255 white; ≥85 % fill; no text or insets; ≥1000 px (2000+ recommended); up to 9 images.
- **A+ modules:** 970×600, 970×300, 300×300; Premium 1464×600 plus a 600×450 mobile version; ≤2 MB; RGB. Use the modules' editable text fields for searchable text.
- **Taobao:** 800×800; the fifth image on white with ≥60 % product and no text; absolute claims such as "the best" are banned.
- **Shopify (OFFICIAL):** keep text out of slideshow and banner images, put it in the theme editor, and set focal points.
- **Volume signals:** Google Pomelli Photoshoot (2026-02-19) and Pomelli's "millions" of assets; Higgsfield at a $700M run-rate (PRN, 2026-08-17).

**Brand kits**
- Google Pomelli (2025-10-28) builds a **"Business DNA"** (tone, fonts, images, palette) from a URL, and added agent features and brand books on 2026-05-19.
- Canva's Brand Kit is available through a Claude connector.
- Adobe Firefly Custom Models entered public beta on 2026-03-19.
- Lovart (a design agent) launched publicly on 2025-07-28.

### D2. Professional results vs "AI slop"

**Audience evidence (SURVEY)**
- IAB (2026-01-15):
  - 82 % of ad executives believe young consumers like AI ads; only 45 % actually do.
  - 83 % of executives use AI in creative work.
  - Over half of consumers want disclosure.
- Harris / 4As (2026-06-24): 78 % say AI ads feel less authentic, 73 % trust them less and 63 % are less likely to buy.
- Canva report (2026-05-14):
  - 97 % of marketing leaders use AI daily, yet 78 % of consumers prefer human-made ads.
  - Media mentions of "AI slop" are up 9×.
- NIM: an "AI-generated" label on its own lowers purchase intent.
- Figma (2025-04-24): only 32 % of designers say they can rely on AI output.

**Concrete tells (for the judge checklist)**
- **Type:** uneven kerning or baselines, varying letterforms, gradient text, too many families.
- **Colour:** purple→blue gradients, AI cyan-on-dark, the default cream + serif + terracotta look, tinted near-black.
- **Layout:** centred everything, identical rounded cards and one radius everywhere, eyebrow chips, 01/02/03 labels on non-sequences, clutter, "could belong to any company".
- **Imagery:** plastic or waxy skin, symmetry, beauty-filter softness, glow and halos, 3D blobs, emoji used as icons.
- **Photo realism:** light that doesn't match its source.
- **Text:** garbled text, invented extra copy ("NEW", "NO SUGAR"), phantom watermarks.
- **Series:** sameness across a series (template repetition, which YouTube now penalizes).
- **Emotion:** holiday and emotional pieces made with photoreal AI people read as "creepy".
- Sources: venngage.com/blog/ai-slop-in-design (2026-08-12); 925studios (2026-03-19); getimg.ai skin (2026-09-04); plus Anthropic `frontend-design` and the impeccable rules in B8.

**What pros do instead**
- A brand system first: kits, custom models, Business DNA.
- AI output treated as a draft, with a human edit of type, layout and colour.
- **Real type in editable layers, never baked** (Shopify, Canva AI 2.0's layered output).
- One memorable move ("spend boldness in one place"); texture and grain; deliberate asymmetry.
- Fixed series palettes and filters.
- Legibility tests at thumbnail size.
- Real or art-directed photos with a named light source.
- No AI for logos, heroes or emotionally sensitive campaigns without a human finish.
- A human sign-off gate.

### D3. Platform spec registry (seed data for our skill; confirm before shipping)

| Destination | Canvas | Safe zone / crop | Limits | Source |
|---|---|---|---|---|
| Instagram feed | 1080×1350 (4:5) default; 1080×1440 (3:4) accepted | Profile grid previews at 3:4 since Jan 2025 (≈1012×1350 centre of a 4:5 post) | 3:4 to 1.91:1; ≤20 slides | Buffer 2026-03-17; Kapwing 2025-12-30 |
| Stories (Meta) | 1080×1920 | top 14 % (~270 px), bottom 20 % (~380 px), sides ~6 % | — | 1clickreport 2026-09-02 (VENDOR, based on Meta help) |
| Reels (Meta) | 1080×1920 | top 14 %, **bottom 35 %** | — | same |
| LinkedIn document | 1080×1350 recommended (1:1 and 16:9 also fine) | ~50 px margins; body ≥24 pt | PDF, ≤100 MB, ≤300 pages; 5–15 slides typical | linkedin.com/help a523054; oktopost 2026-06-11 |
| LinkedIn image / OG | 1200×627 (1.91:1) | — | — | Hootsuite 2026-09 |
| X | 1280×720, 1080×1080, 720×1280 | — | ≤5 MB mobile / 15 MB web | Hootsuite |
| Pinterest | 1000×1500 (2:3) | taller gets cut off | ≤20 MB, sRGB | help.pinterest.com (OFFICIAL) |
| TikTok photo mode | 1080×1920 (1:1 and 4:5 allowed) | right rail ~64 px, bottom ~18 % (motiful table) | 4–35 images; don't mix ratios | postfa.st 2026-01-09 (VENDOR) |
| YouTube thumbnail | 16:9; 1280×720 standard, up to 3840×2160 | keep clear of the bottom-right timestamp | JPG/PNG; ≤2 MB (mobile upload) / ≤50 MB (desktop, per the current help page) | support.google.com/youtube/answer/72431 |
| YouTube banner | 2560×1440 (min 2048×1152) | **text-and-logo safe area 1546×423** (1235×338 on the minimum canvas) | ≤6 MB | answer/10456525 |
| Xiaohongshu | 1080×1440 (3:4); 1242×1660 for dense cards | ~10 % top and bottom | one ratio per note | VENDOR guides 2026 |
| Amazon main / A+ | ≥1000 px (2000 recommended), white RGB 255, ≥85 % fill / 970×600, 970×300, 300×300, 1464×600 + 600×450 | — | A+ ≤2 MB | sellerlabs 2025-08-19; greenonion 2026-04-22 |
| Taobao / Tmall | 800×800; details 750 wide | the white-background fifth image, product ≥60 % | ≤3 MB | focalflow 2026-04-03 |
| Shopee | 1:1 or 3:4 (3:4 helps visibility) | — | — | seller.shopee (OFFICIAL, 2023) |
| Shopify | depends on the theme; set a focal point | no text baked into banners | ≤20 MB | help.shopify.com (OFFICIAL) |
| Daraz | square product images; banner size **not verified** | — | — | — |
| Print (poster, flyer, brochure) | A-series / Letter at 300 dpi; 3 mm (0.125 in) bleed; keep type 0.4 in (~10 mm) from the trim | CMYK proofing | PDF | poster-maker, collateral-kit, general print practice |

### D4. Market signals and launch timeline

| Date | Event |
|---|---|
| 2025-07-15 | YouTube inauthentic-content policy |
| 2025-07-28 | Lovart public launch |
| 2025-09-01 | China AIGC labelling measures take effect |
| 2025-10 | Adobe MAX: Firefly Image 5 plus partner models; Canva design model; **Pomelli launch (10-28)** |
| 2025-11-20 | **Nano Banana Pro** |
| 2025-11-25 | FLUX.2 |
| 2025-12 | Canva "Imperfect by Design" trends; McDonald's NL pulls its AI ad; YouTube title testing goes global |
| 2026-01-15 | IAB "AI gap" report |
| 2026-02 | Recraft V4 (SVG); Qwen-Image-2.0; Pomelli Photoshoot; Nano Banana 2 |
| 2026-03-19 | Firefly Custom Models (public beta) |
| 2026-04 | Canva AI 2.0 with layered, editable output (04-16); **gpt-image-2 API (04-21)**; ChatGPT Images 2.0 (04-22) |
| 2026-05 | Canva marketing report (78 % of consumers prefer human-made ads); Pomelli agent and brand books |
| 2026-06 | Ideogram 4.0; EU Code of Practice on AI-generated content finalized (06-10); Harris/4As survey |
| 2026-08-02 | EU AI Act Art. 50 applies |
| 2026-08-17 | Higgsfield raises $400M ($700M run-rate) |
| 2026-09-03 | Anthropic `frontend-design` rewritten around AI-default clusters |
| 2026-09-08 | **GPT Image 2.5 Sunburst / Flare** (openai-python) |

### D5. Disclosure and labelling that affect deliverables

- **Meta:** "AI info" labels appear when it detects C2PA or IPTC metadata or the user self-declares; AI-*generated* content is labelled more prominently than AI-*edited*. Political and social-issue ads must disclose (about.fb.com, updated 2024-09-12).
- **TikTok:** realistic AI content must be labelled, and C2PA metadata is auto-labelled (newsroom.tiktok.com, 2024-05-09).
- **YouTube:** realistic altered or synthetic content must be disclosed; thumbnails and infographics are exempt.
- **EU AI Act Art. 50:** applies from **2026-08-02**. Providers must mark outputs in machine-readable form, and deployers must disclose deepfakes. The Code of Practice was finalized 2026-06-10 and includes EU label icons.
- **China (CAC measures, in force 2025-09-01):** visible labels plus metadata labels, and removing them is banned. This matters for Xiaohongshu, Douyin and Taobao work.
- **C2PA** (spec v2.3; members include OpenAI, Google, Meta, TikTok): **a headless-Chrome composite drops the model's C2PA manifest.** Keep the raw master with its C2PA, write IPTC `trainedAlgorithmicMedia` on finals (as our codex-imagegen skill already does), and record the models used in each asset's manifest.

### D6. Repo momentum: where the stars are (2026-09-23)

| Cluster | Repos (★) | Reading |
|---|---|---|
| "Taste" and anti-slop design skills | garrytan/gstack 134k · nextlevelbuilder/ui-ux-pro-max-skill 130k · VoltAgent/awesome-design-md 117k · nexu-io/open-design 98k · Leonxlnx/taste-skill 90k · pbakaus/impeccable 70k · cathrynlavery/diagram-design 42k · google-labs-code/design.md 28k | **The most-starred design work in 2026 is about taste, anti-slop and design-system files**, not image prompts |
| Official skills | anthropics/skills 178k · openai/codex 126k · openai/skills 28k (deprecated) · anthropics/knowledge-work-plugins 25k | Both vendors now ship render-and-inspect QA and visual-base + exact-layer patterns |
| Prompt libraries | freestylefly 33k · PicoTrex 24k · EvoLinkAI 17k · YouMind 10k + 13k · ZeroLu 2k | Large but full of third-party content and "8K" boilerplate; mine them for techniques only |
| Design deliverable skills | baoyu-skills 26k · guizang-ppt 27k · guizang-social-card 7k · ljg-skills 7k · codex-ppt 6k · wuyoscar 6k · Easel 1.3k · higgsfield 1.1k | The deliverable-specific skills that matter are mid-sized and very active (pushed in the last 1–3 months) |
| Small but technically the best | bearcarousel (3) · evidence-based-brand-systems (3) · svg-logo-maker (2) · ig-card-generator (13) · 30x-image (29) · collateral-kit (0) | Measured-QA ideas worth reimplementing; stars are not a quality signal |

---

## Part E: Recommendations for our skill

**What the best sources agree on**
- Professional-looking output comes from **constraint, not from prompting harder**:
  - curated layout recipes and seed templates instead of free-form layout;
  - one brand lock that feeds both the image prompts and the CSS;
  - real typography in layers;
  - code checks for everything measurable;
  - a fresh-context vision judge only for what can't be measured;
  - a human gate for hero pieces.
- OpenAI's `creative-production` (visual base first, then deterministic exact layers) and Higgsfield brandkit (posters are deterministic; image models never bake the logo or exact copy) have independently arrived at the architecture we planned. Keep it.

### E1. Three routes, one brief, one brand lock

| Route | Use for | How |
|---|---|---|
| **H: hybrid (default)** | Posts, stories, carousels, thumbnails, ads, banners, posters, special-day posts | Text-free AI plate with reserved zones → HTML/CSS layout from brand tokens → headless Chrome → PNG/PDF → QA → judge |
| **A: full-AI (gated)** | Stylized typographic posters, conceptual title art, short Latin-script greetings, mood or brand boards, "hand-lettered" Xiaohongshu-style cards | GPT Image renders the text. OCR-diff gate; after 1–2 misses, switch to H. **Never patch AI-rendered text**; regenerate or switch route |
| **D: deterministic** | Data infographics, charts, quote/tip cards, brand guidelines, brochures, logo finals | HTML/SVG plus a chart engine; AI only for optional spot illustration |

**Making H not look "pasted on".** Each of these comes from a source above:
- Reserve text zones in the plate with a **corner-tick skeleton** or a **neutral typeset scaffold** as a reference image, worded "positioning map, not style; don't draw boxes" (JuneYaooo, yingzao, hatch-pet).
- Let the type **interact with the subject**: a subject mask (rembg or BiRefNet) allows text behind the subject, and wrapping follows the subject's contour. Reject "two islands" layouts.
- Unify the layers: one grain or texture layer over everything, a matched shadow direction, and a palette taken from the plate (culori) mapped to brand tokens.
- **Spend boldness in one place:** one memorable move per piece, with everything else quiet.

### E2. Brand lock: one source of truth, three consumers

Extend the existing `brand/style.json` of codex-imagegen into:
- **`brand/DESIGN.md`** in the google-labs-code/design.md format, so it is readable by any agent.
- **`brand/lock.json`:**
  - the 10 buluslan fields, plus type roles, spacing scale, radius set and motif;
  - `locked_immutable`;
  - a per-field status of fixed / proposed / unknown with an evidence label (higgsfield);
  - banned pairings;
  - a `do_not` list.
- **Generated from `lock.json`:**
  1. CSS custom properties for the HTML templates.
  2. A verbatim prompt prefix for GPT Image, with a colour-guard line so hex codes never appear as text.
  3. QA thresholds: allowed fonts, the palette with a ΔE tolerance, minimum contrast.
- **Brand discovery:** when a client has none, do it from a URL or plain words, like Pomelli's "Business DNA" or knowledge-work `brand-style`, then preview it on a sample card and get a human yes.
- **Market data:** per-market hints on taboos, holidays and scripts are advisory only, not stereotypes (bulu §6).

### E3. Deliverable registry (JSON, one file per deliverable type)

- **Fields:**
  - platform sizes;
  - **safe zones in %**;
  - text slots with **JSON-Schema length caps** (june layout bank);
  - allowed routes;
  - layout recipes;
  - QA profile (which checks, minimum font px, density band, contrast floor);
  - export (format, JPEG quality, max bytes, PDF bleed).
- **Seed data:** D3.
- **Render at legal model sizes, then crop or pad to exact pixels.** The Codex path ignores size; alek measured 1536×864 → 1672×941. Record requested vs actual in the manifest.

### E4. Template system

Take the pattern from guizang, baoyu, visual-style-presets and Easel.

- **Layout recipes:** seed HTML per deliverable family, never free-form. Start with about 12–16 recipes for each of carousel, thumbnail, poster and card.
- **Style presets:** a token block plus **one signature structural motif** (the local visual-style-presets skill's rule). Never blend two presets.
- **Palettes:** the brand palette overrides colours only.
- **Selection:**
  - a **style × layout compatibility matrix**;
  - **content-signal auto-select** (first match wins, explicit fallback);
  - presets that resolve to full dimension sets with precedence: flag > preset > default.
- **Default blocklist:** Anthropic's five AI-default clusters and the impeccable slop rules. Use one of those looks only when the brief asks for it.
- **Fonts:** a curated OFL set with verified coverage for Latin, Bengali (Hind Siliguri, Noto Sans/Serif Bengali, Tiro Bangla), Arabic, Devanagari and CJK. Check glyph coverage with fontTools before rendering (yingzao). Rotate away from Inter, Roboto and Space Grotesk as defaults.

### E5. Workflow gates (all skippable with `--yes` for overnight runs)

1. **Intake:** the platform or deliverable, and a verbatim **allowed-copy list**. Facts are graded verified / user-confirmed / unconfirmed, and unconfirmed facts never render.
2. **Structure:** for carousels, one idea per slide; for infographics, data taken verbatim.
3. **Show 3 directions as real renders** (safe / bold / wildcard) and **approve one sample** (a representative content slide, not the cover). Record its method. It becomes the style-only reference and anchor for the batch (codex-ppt, baoyu anchor chain, huashu).
4. **Show the budget** (N AI images) before the batch, then run the batch in parallel.
5. **QA (E14) → judge → at most 2 fix rounds →** export with `manifest.json` (prompt hash, models, requested vs actual size, C2PA/IPTC status, disclosure flags), a contact sheet and alt text.

### E6. Carousel and seamless "chain" carousel module (the gap nobody fills)

**Standard carousel**
- Hook slide with a swipe cue → one idea per slide → final CTA or save slide.
- 5–10 slides (LinkedIn 5–15).
- 1080×1350. LinkedIn export is one uniform PDF.
- Invert 1–2 slides for rhythm, and never repeat a layout on adjacent slides.

**Chain carousel**
1. **Master canvas:** N × 1080 by 1350.
2. **AI plate, one generation if possible:**
   - N=3 at 4:5 is 2.4:1: generate at 21:9 or 3:1 and crop.
   - N=3 at 1:1 is exactly 3:1.
   - N=2 fits 16:9 or 3:2 with a crop.
   - For N≥4, either chain overlapping extend-canvas edits (the previous segment's edge as the edit input), or carry the continuity in **HTML layers**: lines, shapes, a cut-out photo crossing a seam. This is cheaper and exact.
3. **HTML typesetting on the master with a per-slide grid.**
4. **Seam rules** (ParthJadhav, verified):
   - No text, prices, CTAs or faces across a seam.
   - A 60–80 px gutter each side of a seam (an assumption; tune it).
   - One cross-seam moment per 5 slides, at most 2 per 8–10.
   - A crossing object overlaps 10–30 % of its width; only backgrounds may cross more than 40 %.
5. **Slice** with Playwright `clip` or sharp `extract`.
6. **Automatic checks:**
   - text boxes are clear of x = k·1080;
   - adjacent edge columns are pixel-continuous;
   - each slice passes a standalone check;
   - the 3:4 grid-crop centre of slide 1 still reads.
7. **Deliver** the slices plus a stitched preview.

### E7. YouTube thumbnail and banner

**Thumbnail** (the higgsfield process)
- At least 5 concepts from frameworks; a truthful information gap.
- A text-free plate plus an HTML overlay baked at native resolution:
  - cap height 12–18 %;
  - stroke drawn under the fill;
  - never over a face;
  - the bottom-right timestamp area kept clear.
- A **120 px legibility gate** and OCR at that size.
- Thumbnail text of 3–5 words at most, sharing no words with the title (yt-package lint).
- **3 genuinely different variants** for Test & Compare.
- Exports: a 3840×2160 master plus a 1280×720 JPG under 2 MB.
- Faces come only from the client, with an identity lock. Never invent a fake creator face.

**Banner:** 2560×1440 with all text and logos inside 1546×423. Check it at TV, desktop and mobile crops.

### E8. Posters, flyers, brochures

- **Posters and flyers:**
  - a promotional hierarchy (name > claim > details > CTA > fine print);
  - the three-glances test;
  - one memory point for special-day pieces.
- **Print:**
  - page size plus 3 mm bleed;
  - type ≥10 mm (0.4 in) from the trim;
  - 300 dpi rasters (render at 4× for physical sizes);
  - QR codes and URLs checked live (collateral-kit);
  - a true-size PDF.
- **Brochures:** a page-order recipe (cover → what you get → how → proof → price → close) and per-page proofs.
- **CMYK:** the default is an RGB vector PDF from Chrome with TrimBox and BleedBox set, and the manifest says so.
  - When the printer requires CMYK or PDF/X, use Vivliostyle `--press-ready` (PDF/X-1a; AGPL, so run it as a separate CLI), WeasyPrint `pdf/x-4` with `device-cmyk()`, or Typst for long documents, always with the printer's ICC profile.
  - None of these is installed yet, so ask before installing.

### E9. Infographics and data cards

- **Numbers come from a source table through a chart engine, inside the same HTML page so the brand fonts apply.** Never have an image model draw a chart: on IGenBench, even Nano Banana Pro gets only 49 % of infographics fully right.
  - AntV Infographic syntax for list, timeline, comparison and hierarchy layouts.
  - ECharts `renderToSVGString` or Vega-Lite for charts.
- AI is only for spot illustration or icons in one consistent icon style (the bulu icon-system field: never mix line and filled).
- Fixed-region layout contract; 3–5 modules; a source line on every card.
- The judge uses OpenAI's 7 × 5 editorial rubric (ship at ≥28/35 with no score below 4).
- A full-AI variant is allowed only when the data is trivial, and it must carry a separate verbatim label list for the OCR diff (baoyu).

### E10. Quote, tip and info cards; special-day posts

- **Cards:** typographic recipes (quote plus author; big-number stat; tip list; myth/fact). Body ≥28–40 px at 1080 wide (Easel, ljg). The bigger the type, the lighter the weight.
- **Special-day calendar per market:**
  - dates stay **pending until confirmed per country**;
  - a greeting and imagery table per faith and region;
  - **human review for religious content**;
  - no photoreal AI people in emotional holiday pieces;
  - AI for atmosphere and texture only; real text in HTML.
  - Holiday sets get a **temporary style lock** with its own campaign id (bulu).

### E11. Logos, brand kits and guidelines

- **Concepts:** 3–4 genuinely different AI concept marks (existing codex-imagegen transparent jobs). **The final mark is hand-built SVG.**
- **Logo tests:**
  - 16 px favicon and 28 px app icon;
  - one colour and reversed;
  - contrast of 3:1 for the mark and 4.5:1 for a wordmark;
  - CMYK gamut;
  - a one-colour structure score (rampstack, svg-logo-maker).
- **Guideline PDF generated from `lock.json`:**
  - palette with usage rules and **banned pairings** (every declared pair's contrast computed, brandcheck-style);
  - type system with licences;
  - clear space and minimum sizes;
  - do/don't;
  - application mockups, labelled as presentation only.
- **Brand board:** the full-AI route is fine as a moodboard (taste-skill brandkit), never as the source files.

### E12. Ads and e-commerce

- **Amazon main image:**
  - **a real product photo only**;
  - a pixel check for RGB 255 at the edge ring;
  - **fill measured as extent, not pixel area** (bulu's bug).
- **Secondary and A+ images:** the hybrid route with bulu's funnel slots and category visual keys and light.
- **Fidelity:** a product-fidelity lock sentence (wzj177 `print_design_lock`). **Composite the real packshot or label; never regenerate label text.**
- **Copy:** a claims linter (certifications, medical claims, inflated specs, "best"); ad copy character limits (marketingskills); the CTA drawn as a button.
- **Placements:** Reels and Stories safe zones enforced (bottom 35 % / top 14 %).

### E13. Resize, reformat and image-to-banner

- **Never blindly crop across ratios.** Text re-flows per ratio from the HTML layers; recompose with a title shortener (guizang).
  - Layout patterns (stacked, split, overlay, text band) are chosen by aspect ratio.
  - Each photo's focal point is computed **once**, preferring Apple Vision saliency or faces, with sharp `attention` as the fallback, and applied as `object-position` in every format.
  - A text fitter binary-searches font size between a minimum and maximum per role; at the minimum it asks for shorter copy.
- **Art:** a subject-aware crop, then a generative extend (Codex edit, extend-canvas) only where needed. **Preview 3 crops before the full run** (Adobe pattern).
- **Client photos:** preflight exposure, sharpness and roll → hero / support / reject (yingzao).
- **Old design → new banner:** decompose into a clean plate plus layers first (JuneYaooo), then re-lay out.

### E14. QA pipeline, in order (the cheapest and most objective checks first)

1. **Pre-render lint:**
   - copy against slot caps, banned words and claims;
   - fonts in the lock, with glyph coverage; after rendering, CDP `CSS.getPlatformFontsForNode` must show no silent fallback;
   - every capture ≤16,384 px per side;
   - model sizes legal;
   - platform words kept out of image prompts, paired with "keep packaging text" (product-shots).
2. **DOM checks (Playwright):**
   - overflow and text occlusion;
   - minimum font px for the deliverable;
   - **text boxes vs platform safe zones and seams**;
   - density bands (≥75 % filled; no blank band >15 %);
   - title gap;
   - computed-style contrast;
   - a port of the impeccable slop and quality rules that apply to static graphics.
3. **Pixel checks:**
   - contrast measured on the real pixels behind text (bearcarousel);
   - dead space and top-heaviness (Easel);
   - palette ΔE against the lock;
   - dimensions, bytes and format;
   - Amazon edge ring and extent;
   - **downscaled legibility at 120, 160 and 360 px with OCR at that size.**
4. **OCR diff** on any AI-rendered text, after normalizing punctuation (the cookbook bug) and with Unicode normalization for Bengali.
5. **Vision judge** (a fresh-context subagent, blind to the detector output at first; impeccable pattern):
   - **gates:** instruction, exact text, brand lock, claims and safety;
   - **0–5 scores:** hierarchy, composition, typographic craft, brand fit, originality / not slop, legibility at size, series consistency;
   - never averaged; the lower score when unsure;
   - P0–P3 findings, each with **one** targeted fix and the failing region named;
   - checklists: the 5 AI-default clusters, the 8 AI tells, "two islands", "could belong to any company";
   - side by side with the approved sample, with a contact sheet for sets.
6. **Stop rules and human gate:**
   - at most 2 fix rounds per asset;
   - keep the best version;
   - stop when a round shows no visible gain;
   - human sign-off for hero and client-facing pieces.

### E15. Harden the Codex path (in the existing codex-imagegen skill)

- **Prove the image is new:** `image_gen` ran in *this* thread (a stream event, or a new PNG in `generated_images/<thread>`); check the PNG magic bytes and a minimum size; never accept images from earlier sessions (baoyu 2.5.2).
- **Treat size, quality and background as advisory** on the Codex path:
  - always measure and then crop or pad;
  - check the alpha channel really exists (not a fake checkerboard);
  - keep the chroma-key fallback.
- **Protect the machine:** do not use `--sandbox danger-full-access`; copy files out of `generated_images` ourselves. Client text is untrusted prompt input.
- **Make runs traceable:** a JSON error taxonomy with retryable flags; a cache on sha256(prompt + aspect + refs); a lock; JSONL logs.
- **Plan for the throughput limits:** about 50–90 s per image when serialized. Our parallel batch already beats that, but still budget carousel runs (10 plates plus fixes).

### E16. Licensing and provenance rules for what we build

- **Can adapt, keeping the notice:**
  - MIT: baoyu, bulu, higgsfield, wuyoscar, ParthJadhav, ig-card-generator, evidence-based-brand-systems, svg-logo-maker, rampstack, taste-skill, 30x-image, OpenAI `frontend-app-builder` and data-viz rubric.
  - Apache-2.0: Easel, bearcarousel, impeccable, Anthropic example skills, the Codex imagegen skill, JuneYaooo, zuoge.
- **CC-BY (attribution required):** smixs, YouMind.
- **Ideas only:**
  - AGPL: guizang.
  - No licence: yingzao, inference-sh, Phil-design-skills.
  - Proprietary: Anthropic `pptx`/`pdf`/`docx`; OpenAI `creative-production` and `design-qa`.
- **Do not vendor:**
  - baoyu-design, jiji262/claude-design-skill and huashu-design (their provenance is Claude Design prompts; huashu also watermarks by default);
  - wzj177's code (TLS verification disabled);
  - any prompt-library prompt text or example image (third-party X content).
- **Output provenance:**
  - keep the C2PA master;
  - write IPTC on finals;
  - record the models used and the disclosure needs per platform (EU Art. 50, China, Meta/TikTok auto-labels);
  - no tool or brand names in delivered files (the global attribution rule).

### E17. Suggested build order

1. **MVP:**
   - `lock.json` → CSS + prompt prefix; the deliverable registry (D3).
   - About 12 seed recipes: 4:5 post, 9:16 story, 1:1 post, LinkedIn PDF carousel, YouTube thumbnail, YouTube banner, quote card, tip or stat card, A-series poster, special-day post, e-commerce banner, simple infographic.
   - Playwright renderer; DOM and pixel QA; vision judge; manifest.
   - Plates from the existing codex-imagegen batch.
2. **v1.1:** chain carousels (E6); the full-AI route with the OCR gate and typeset scaffold; the resize module; the thumbnail concept process.
3. **v1.2:** brand-kit and guideline PDF; logo test suite; print PDF with bleed and CMYK; chart and infographic engine; e-commerce funnel sets and claims linter; optional Canva/Figma/Penpot export adapters.

### E18. Fit with the in-progress `~/.claude/skills/codex-design`

It appeared during this research and was read only, never modified. It already covers much of E1, E10 and E14 (Chrome rendering, safe zones, contrast, an art-director judge). The highest-value additions from this research, in priority order:

1. **Chain carousel:** master-canvas slicing via `clip`, the seam rules (B9), and edge-continuity checks.
2. **Font-fallback check:** CDP `getPlatformFontsForNode`. Also add `--force-color-profile=srgb` and the 16,384 px guard.
3. **Brand-lock-driven tokens, style × layout presets with compatibility and auto-select, and the 5-cluster anti-default list** (E2, E4, B8).
4. **Judge protocol:** blind first, then detector evidence; gates plus scores, never averaged; P0–P3 with one fix each; a contact sheet for sets (E14).
5. **Full-AI route with an OCR gate and typeset scaffold,** falling back to hybrid (E1, B6).
6. **Thumbnail concept frameworks, 3 variants for Test & Compare, and the title/thumbnail word-overlap lint** (E7).
7. **Print CMYK route and logo test suite** (E8, E11).
8. **Marketplace rules:** Amazon main image is a real photo, fill measured as extent; claims linter (E12).

---

## Process notes and evidence caveats

- **Web-search quota:** the session's web-search limit (200 calls) ran out during this research. Later passes used `gh api`, raw files, npm and direct page fetches instead.
- **Blocked sources:** Amazon Seller Central, the Meta Ads Guide, Ideogram, Midjourney and OpenAI help all returned 403 or needed JavaScript. Those specs rest on 2026 third-party guides and are marked VENDOR.
- **Still to confirm before shipping:**
  - Daraz and Shopee banner sizes;
  - India, NY, CA and Korea AI-label rules;
  - whether Codex's built-in `image_gen` uses GPT Image 2.5;
  - whether gpt-image-2 or 2.5 really renders Bengali reliably (claimed by OpenAI, not tested here).
- **One conflict between research passes:** one pass reported "no GPT Image 2.5 found", but openai-python's 2026-09-08 commit, baoyu's 2026-09-09 update and our earlier captures all confirm 2.5 Sunburst and Flare exist. The later evidence wins.
- **Files created outside this notes file:**
  - One research pass wrote freestylefly's `cases.json` (1.3 MB) into the session scratchpad for analysis and deleted it straight after.
  - A WebFetch of a Shopee PDF was saved automatically by the tool to the session's tool-results cache. It is a harness cache file; it was left in place and not deleted.
  - Some slow `curl` calls left harness output files in the session `tasks/` folder.
  - Nothing else was installed, cloned or modified.
