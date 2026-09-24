# R3: Designing with GPT Image — text, typography, and choosing full-AI or hybrid

Prepared 2026-09-23 for the NexaLance design-deliverables extension of `codex-imagegen`.

**Scope.** GPT Image 1.5, 2 and 2.5 (Flare and Sunburst) used for social posts, stories, carousels, YouTube thumbnails, banners, posters, flyers, brochures, infographics, info cards, special-day posts, logos, brand kits, ads and image-to-banner edits.

**Companion notes.** Notes on higgsfield and the local skills, including the thumbnail text-overlay recipe, are in `design-research/R1-skills-higgsfield-local.md`. This file does not repeat them. General edit mechanics are in `~/.claude/skills/codex-imagegen/references/master.md` §9: mask polarity, composite-back code and outpaint steps.

**Evidence tags.** Every claim carries a source key that resolves in §13, which gives the URL and date. All web sources were accessed on 2026-09-23 unless noted.

| Tag | Meaning |
|---|---|
| OFF | Official OpenAI or vendor documentation, or an announcement by an OpenAI employee. |
| SRC | Source code we read ourselves (file cited). |
| LOC | Measured on this machine, recorded in the skill docs or project memory. |
| COM | Community report: forum, HN, blog or GitHub skill. Anecdotal; we have not verified it. |
| VEN | Vendor or marketing blog. We could not reproduce its numbers; treat them as unverified. |
| DER | Our own derivation from the cited inputs. |
| **UNVERIFIED** | We could not confirm it. Do not base a hard rule on it. |

---

## 0. Summary — the ten findings that drive the design

1. **The Codex route has no quality or size control.**
   - Codex's built-in tool always requests `gpt-image-2` with `quality=auto` and `size=auto`, and takes at most 5 reference images [S15 SRC].
   - Native outputs are about 1.57 MP [L1 LOC]: 1536×1024, 1024×1536, 1254×1254, 1122×1402 and 1672×941.
   - OpenAI's advice for small or dense text is to compare `medium` or `high` [S3 OFF], which this route cannot request. Small and dense text is therefore structurally riskier on our default engine.
2. **OpenAI's own docs make the case for hybrid.** Four official statements:
   - text placement and clarity can still fail, layouts that depend on exact placement can be imprecise, and brand elements can drift across generations [S2];
   - production-critical typography should be proof-read word by word and finished in a design tool [S10];
   - charts that must be numerically exact should be rendered deterministically [S6];
   - pixel-identical regions need compositing [S1].
3. **Short Latin headlines are usable in full-AI behind a gate.**
   - One vendor measured gpt-image-2 on 500 generations [C12 VEN, unverified]:
     - one-line headlines ~94% correct;
     - two-line subheads ~87%;
     - quoted text 96% versus 84% unquoted.
   - Across several strings the odds compound quickly. Eight strings at 94% each are all correct only about 61% of the time [DER].
4. **Invented copy is a bigger practical risk than misspelling.**
   - Models add taglines, claims ("NO SUGAR"), specs and extra event copy [C20 COM, C15 COM].
   - Casing drifted in one Sunburst test [C7 COM].
   - The official eval method is an OCR set-diff: required strings against extracted strings [S5 OFF].
5. **Bengali is claimed, not yet proven.**
   - OpenAI said Images 2.0 renders Bengali and Hindi at high fidelity, as quoted in launch coverage [C9].
   - Independent evidence for Bengali on gpt-image-2 and 2.5 is thin.
   - A cross-lingual editing benchmark on the previous model generation ranks Bengali among the hardest scripts, 0.70 below English on a 0–5 scale. Typical errors were broken or missing vowel signs and malformed conjuncts [C16].
   - Vision-model OCR also misreads Indic conjuncts [C18], so automated QA for Bengali is weak.
6. **Non-Latin type needs a browser, not Pillow.** Headless Chrome shapes complex scripts with HarfBuzz [P4]. Pillow needs the Raqm engine for them [P5]. The W3C documents Bengali bugs: letter-spacing splits conjuncts, and `::first-letter` fails on conjuncts [P3]. **Never letter-space Bengali.**
7. **The route decision in one line:**
   - hybrid is the default for final, text-bearing client deliverables;
   - full-AI is for concepts, art-led lettering, and simple posts with at most three short Latin strings that pass the OCR gate;
   - these are **always hybrid**: print, aspect ratios beyond 3:1 (a LinkedIn Page cover is 1512×256 [P2]), multi-size sets, series and brand templates.
8. **Editing text inside a generated image works only for short strings.**
   - Each edit re-renders the image and quality degrades with every pass [C1 COM, C24 COM].
   - Always edit from the original, make one change per pass, and composite the changed region back [S1 OFF].
9. **Brand consistency does not come from the model.** It comes from an HTML template, the real SVG logo, a fixed style lock and one approved anchor image. OpenAI itself lists brand-element consistency as a limitation [S2 OFF].
10. **Measure before hard-coding.** Build our own English and Bengali design-text eval (§11) before fixing any threshold. Every number marked "house heuristic" below must be calibrated.

---

## 1. Ground truth: engines, models, sizes, settings

### 1.1 The two engines we actually have

| Item | Codex built-in `image_gen` (default route) | OpenAI API engine (optional, needs key) |
|---|---|---|
| Model | Hard-coded `gpt-image-2` (`IMAGE_MODEL`) in `codex-rs/ext/image-generation/src/tool.rs` on main and in v0.149.1 [S15 SRC]. The installed CLI 0.156.1 still requests gpt-image-2 [L2 LOC]. | `gpt-image-2` (snapshot 2026-04-21), `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` (snapshots 2026-09-08) [S7 OFF, S8 OFF] |
| Model proof | C2PA metadata says gpt-image "2.0" even for images the API returned for 2.5 requests [S14 COM], so metadata cannot prove which model ran. Report "requested gpt-image-2" [L1]. | The requested model id |
| `quality` | Always `auto` [S15 SRC] | gpt-image-2: low / medium / high / auto. 2.5: adds `xhigh` and `max` [S1 OFF, S2 OFF] |
| `size` | Always `auto`; the aspect follows the prompt wording [S15 SRC, L2 LOC]. Native sizes in §1.2. | Any W×H with both edges multiples of 16, max edge 3840, ratio ≤ 3:1, total 655,360–8,294,400 px. Above 2560×1440 (3,686,400 px) is experimental [S1 OFF, S2 OFF] |
| Reference images | ≤ 5 (`MAX_EDIT_IMAGES`) [S15 SRC] | ≤ 16 on `/images/edits` [S9 OFF] |
| Mask | None [S15 SRC] | Alpha mask applied to the first image. It is prompt-based guidance, not a hard boundary [S2 OFF] |
| Transparency | A prompt asking for a transparent background returned real alpha in local tests [L2 LOC]. Main added an explicit `transparent_background` argument on 2026-09-23 (PR #47484); **not yet in 0.156.1 (UNVERIFIED which release)** [S15 SRC] | `background="transparent"` with png or webp. Preview for gpt-image-2 since 2026-08-20; supported on 2.5 [S8 OFF] |
| Prompt path | The Codex *agent* writes the `prompt` argument, and the tool forwards it as-is [S15 SRC]. Our copy therefore passes through an LLM. Our `~/.codex/AGENTS.md` makes Codex answer in Banglish [L2], a risk for exact strings (§4.3 R-T16). | The Image API sends the prompt as given. The Responses tool auto-revises prompts (`revised_prompt`) [S2 OFF] |
| Cost | ChatGPT plan usage. Image turns use limits 3–5× faster [S10 OFF] | $30 per 1M image-output tokens for all three models; per-image numbers in §1.3 [S7 OFF, S18 DER]. Batch at −50% for gpt-image-2 only [S8 OFF] |
| Latency | About 77 s for the first run. Fast mode: 10 complex images in about 3.5 min, run in parallel [L2 LOC] | gpt-image-2: about 104 s on average over roughly 50k API images (one user) [C5 COM]. At 1920×1088, `high`, n=6: 2.5 Flare about 29 s, Sunburst about 41 s [S14 COM] |

### 1.2 Sizes: generation aspect → final deliverable

Codex native sizes were measured locally [L1 LOC]:

| Aspect | Native size |
|---|---|
| 3:2 | 1536×1024 |
| 2:3 | 1024×1536 |
| 4:5 | 1122×1402 |
| 1:1 | 1254×1254 |
| 16:9 | 1672×941 |

9:16, 21:9 and 3:1 were **not measured (UNVERIFIED)**.

| Deliverable | Final size | Codex: generate at | API size (explicit) | Post step |
|---|---|---|---|---|
| Feed portrait | 1080×1350 (common spec, **UNVERIFIED this session**) | 4:5 → 1122×1402 | 1088×1360 or 1536×1920 | Downscale or crop |
| Square | 1080×1080 | 1:1 → 1254×1254 | 1024×1024 / 2048×2048 | Downscale |
| Story / Reel | 1080×1920 | 9:16 (native size unmeasured) | 1088×1920 / 2160×3840 (experimental) | Crop or pad |
| YouTube thumbnail | YouTube now recommends 3840×2160, 16:9, minimum width 640 [P1] | 16:9 → 1672×941 | 1920×1088; 3840×2160 is experimental | Accept 1280×720, or upscale the *plate* only |
| Web hero | 1920×1080 / 2560×1440 | 16:9 → 1672×941 | 2560×1440 (reliability ceiling) | Crop |
| LinkedIn Page cover | 1512×256 ≈ 5.9:1 [P2] | 3:1 plate (native size unmeasured) | 3072×1024 | **Extend in CSS**; beyond the 3:1 limit [S1] |
| IAB leaderboard / skyscraper | 728×90 / 160×600 (IAB standard, **UNVERIFIED this session**) | n/a | n/a | Hybrid only (8:1 and 1:3.75) |
| A4 flyer or poster, print | 2480×3508 at 300 ppi | 2:3 → 1024×1536 ≈ 124 ppi at A4 | Largest valid A-ratio ≈ 2416×3424 ≈ 291 ppi, experimental [L1 master §9.13] | Vector type; upscale the plate |

**Rules**

- Always state the aspect in words at the top of the prompt, for example "vertical 4:5 portrait". The Codex route has no other way to set it [L2].
- Read the decoded output dimensions; never assume them. The same backend returned 1672×941 for a request of 1536×864 [C26 COM].

### 1.3 Quality ladders and per-image cost (API route)

The token counts come from the official image-token calculator formula [S18 DER]. The quality ladders map onto each other: 2.5 `max` equals gpt-image-2 `high`, and 2.5 `high` equals gpt-image-2 `medium`. One user confirmed this remap from billing [S14 COM].

Cells show image-output tokens / cost at $30 per 1M; input tokens are excluded.

| Model · quality | 1024×1024 | 1024×1536 | 2048×2048 | 3840×2160 |
|---|---|---|---|---|
| gpt-image-2 low | 196 / $0.006 | 158 / $0.005 | 397 / $0.012 | 371 / $0.011 |
| gpt-image-2 medium = 2.5 high | 1,756 / $0.053 | 1,372 / $0.041 | 3,568 / $0.107 | 3,336 / $0.100 |
| gpt-image-2 high = 2.5 max | 7,024 / $0.211 | 5,488 / $0.165 | 14,272 / $0.428 | 13,342 / $0.400 |
| 2.5 medium | 439 / $0.013 | 343 / $0.010 | 892 / $0.027 | 865 / $0.026 |
| 2.5 xhigh | 3,122 / $0.094 | 2,459 / $0.074 | 6,343 / $0.190 | 5,930 / $0.178 |

Official guidance on choosing quality:

- Start low for drafts [S2].
- For small or dense text, detailed infographics and multiple fonts, compare `medium` and `high` [S3].
- For 2.5, raise quality only while a requirement is still unmet; use `xhigh` or `max` only when they fix it [S1].
- The same quality label does not mean the same quality or latency across models [S1].

### 1.4 What OpenAI officially says about text, layout and consistency

All points are paraphrased.

**Exact text**

- Put literal text in quotes (or ALL CAPS) and give its typography: style, size, colour and placement [S1, S3, S4].
- Spell unusual words letter by letter [S1, S3, S4].
- Say how many times the text appears, ask for no other text, then check the spelling [S1].
- Keep in-image text short, keep the capitalization you want, and say whether any other text is allowed [S10].
- For dense copy or production-critical typography, review every word and finish the asset in a design tool [S10].

**Quality**

- Use `medium` or `high` for small text, dense information panels and multi-font layouts; use `high` for dense labels [S1, S3].

**Structured visuals**

- Infographics and diagrams: name the audience, the flow and the required labels, and say what to leave out. Verify labels and the relationships between them [S1, S16].
- Slides and charts: write the prompt as an artifact spec with the real numbers and labels; use a landscape canvas and `high` for small text [S1, S3].
- UI: describe the product as if it already exists; avoid concept-art language [S1, S3].
- Ads: write the prompt like a creative brief with brand, audience, concept, composition and exact copy, and let the model make taste decisions inside those limits [S3].
- Logos: an original, simple mark with a strong silhouette, balanced negative space and scalability. Use a transparent background and `n` variations [S1, S3].

**Layout and negative space**

- Name placements when layout matters, for example "logo top-right" or "negative space on the left" [S3, S4].
- Reserve room for later copy explicitly. One official example leaves the upper-right corner clear [S10].

**Documented limitations** [S2]

- Complex prompts can take up to 2 minutes.
- Text placement and clarity can still fail.
- Recurring characters and brand elements can drift across generations.
- Precise placement in layout-sensitive compositions can fail.

**Editing and preservation**

- Masking is prompt-based; the model may not follow the mask's exact shape [S2].
- Repeated edits can change details you meant to keep; composite a region that must stay pixel-identical [S1].
- Instructions in the prompt override `background="transparent"` [S6].
- Charts that must be numerically exact should be rendered deterministically; image generation is for the illustration [S6].

**System cards**

- Images 2.0 improved instruction following and dense text [S11].
- Images 2.5 improved edit consistency and infographic accuracy and layout, and added Sketch, templates and shared prompts [S12].

**Announcements**

- gpt-image-2 targets production visuals that are readable, on-brand, localized and sized for their destination. It added more aspect ratios and resolutions up to 2K, stronger structured generation (diagrams, infographics, charts, posters, comics) and better multilingual text [S13].
- Images 2.5: faster generation, templates for posters and merch, Sketch, and comment-based edits. Flare is the fast model; Sunburst adds precision and takes longer [S14].

### 1.5 Design use cases OpenAI demonstrates

| Use case | Where | Pattern that matters for us |
|---|---|---|
| Process infographic (coffee machine) | [S1, S3] | Short prompt naming the audience and the flow; 1024×1536, `medium` |
| Translate an infographic to Spanish (edit) | [S1, S3] | "Translate the text; change nothing else"; then check for words left untranslated |
| Bakery logo, transparent, n=4 | [S1, S3] | Brand personality, simplicity, silhouette, padding, alpha |
| Streetwear ad with tagline | [S1, S3] | Creative-brief framing; tagline rendered exactly once; no extra text |
| Classroom biology diagram | [S1, S3] | Audience, required components, 8 exact labels; 1536×1024, `high` |
| Pitch-deck slide with numbers | [S1, S3] | Artifact spec: the exact figures and footnotes; 1536×864, `high` |
| Billboard mockup from a product photo | [S1, S3] | `Billboard text (EXACT, verbatim, no extra characters)`; typography named |
| Holiday card; collectible packaging | [S1, S3] | "Include ONLY this text (verbatim)"; no trademarks or logos |
| Transparent charts, icons, stickers, print designs | [S6] | The prompt must not describe any background. Charts carry the exact values but must be verified. |
| Eval cases: mobile checkout UI; coffee flyer with 5 exact strings; logo year edit 2024→2026 | [S5] | Text rendering is a hard pass/fail gate; OCR set-diff |
| Launch showcase: menus, infographic posters, scientific diagrams, slides, maps, manga, multi-image sets (thinking mode) | [C9] | ChatGPT only. Thinking mode, web search and self-check are not in our routes. |

### 1.6 Independent rankings (overall preference, not text-specific)

**LMArena, 2026-09-21 [C28]**

| Model | Text-to-image | Image edit |
|---|---|---|
| gpt-image-2.5-sunburst | 1423 (preliminary) | 1526 |
| gpt-image-2.5-flare | 1401 (preliminary) | 1482 |
| gpt-image-2 (medium) | 1381 | 1461 |
| seedream-5.0-pro | 1256 | 1394 |
| nano-banana-pro (2k) | 1246 | 1390 |
| gpt-image-1.5-hf | 1239 | — |
| ideogram-4.0-quality | 1204 | — |
| recraft-v4.1-utility-pro | 1169 | — |
| flux-2-max | 1162 | — |

Arena has a "Text Rendering" category, but our capture only held the overall table. Which model leads on text alone is **UNVERIFIED**.

**Artificial Analysis, captured 2026-09-23 [C29]**

| Model | Text-to-image Elo | Price per 1k images |
|---|---|---|
| GPT Image 2.5 Sunburst (max) | 1196 | $210.7 |
| GPT Image 2.5 Flare (max) | 1189 | $210.7 |
| GPT Image 2 (high) | 1171 | $211.0 |
| Nano Banana 2 | 1121 | $67 |
| Nano Banana Pro | 1099 | $134 |
| Seedream 5.0 Pro | 1078 | $90 |
| FLUX.2 [flex] | 1025 | — |
| Recraft V4.1 Utility | 1020 | — |
| Ideogram 4.0 (Quality) | 1011 | — |

Midjourney does not appear in either capture.

---

## 2. Community evidence 2025–2026: design with text

### 2.1 Text-accuracy numbers (all unverified; ranked by credibility)

| Source | What was measured | Result |
|---|---|---|
| Oakgen, 2026-04-22 [C12 VEN] | 500 gpt-image-2 generations across 10 categories, 5 raters, medians | Headline error-free 94%; two-line subhead 87%; quoted text 96% versus unquoted 84%; single-line headlines above 85% in 10 languages (Arabic, Hindi, Japanese, Korean, Mandarin, Cyrillic scripts and others). **Bengali not tested.** |
| Puter, 2026-09-11 [C7 COM] | One poster prompt at `xhigh`, Flare versus Sunburst | Flare exact. Sunburst spelled correctly but capitalized "FERRY" and added unrequested scene elements. |
| wuyoscar Sunburst runs, 2026-09-09 [C20 COM] | 5 live 2.5 Sunburst runs at `high` | Required strings were readable. The model **added** specs (watch plate) and **invented** "NO SUGAR" ad copy (product), and one shadow pointed the wrong way (poster). |
| JuneYaooo PPT edit guide, repo pushed 2026-08-22 [C24 COM] | Text edits on generated slides | Short titles, dates and places: high stability. Several short edits at once: high. Numbers on data cards: medium-high, each must be checked. Dense tables, financials and contract text: low. |
| India e-commerce Hindi eval, undated [C19 COM] | GPT Image 1 against Gemini 2.5/3.1 Flash; 5 prompts × 8 raters | GPT Image 1 text 4.58/5; Gemini 3.1 Flash 3.90; Gemini 2.5 Flash 3.25, with errors in every prompt. Small sample, older models. |
| DataCamp, 2026-09-09 [C8 COM] | Hands-on test of Images 2.5 | Dense small text "still" hits limits; the poster "has that AI-generated vibe". |
| Atlas Cloud, 2026-06-12 [C14 VEN] | One magazine-layout prompt | gpt-image-2 got everything right, including small print. NB2's small text came out wavy; Seedream 5.0's body text was gibberish. n=1. |
| Neurohive, 2026-04-21 [C10] | Launch explainer | "Long text blocks … break down after a few hundred characters." **UNVERIFIED**; no method given. |
| invideo [C13 VEN] | Marketing page | 99% English, above 90% for CJK/Hindi/Bengali/Arabic. No method given; ignore for rules. |

### 2.2 Long copy, small text, numbers and prices — what the evidence supports

- **Headlines** (one line, a few words, large): reliable enough for full-AI behind an OCR gate [C12, C7, C20].
- **Two-line subheads and short labels** (≤3 words): usable, but expect roughly one failure in eight per string [C12]. Official infographic examples carry about 6–8 labels [S1, S3].
- **Paragraphs, fine print, dense tables:** not production-safe. Every source that mentions them reports failure or advises a design tool [S10, C8, C10 UNVERIFIED, C22, C24].
- **Numbers, prices, specs:** the risk is *invented* or *wrong* data as much as glyph shape.
  - Models add specs and claims [C20].
  - Chart labels must be checked against the source data [S6].
  - Symbols need care. The official eval prompt wrote "20% OFF - Mon-Thu", but its expected set used "20% OFF • Mon–Thu", so dashes and bullets must be normalized before comparing [S5].
- **Small text quality depends on the quality setting** [S1, S3]. The Codex route cannot raise it (§1.1).

### 2.3 Prompt structures that work

| # | Technique | Evidence | Verdict for us |
|---|---|---|---|
| 1 | Quote every literal string; say verbatim, **exactly once**, and **no other text** | OFF [S1, S3, S4, S10]; quoted 96% vs unquoted 84% [C12] | **Adopt, always** |
| 2 | Letter-by-letter spelling for rare words and brand names | OFF [S1, S3]; used as a retry fallback [C21] | Adopt for brand names, or after a misspelling |
| 3 | ALL CAPS | OFF allows quotes *or* caps [S3]; community says short caps words are the most reliable [C21, UNVERIFIED] | Use only when the design wants caps; **always state the casing** |
| 4 | Describe fonts rather than name them | OFF example "sans-serif like Inter" [S3]; Ideogram cannot take font names [M3]; Google allows them [M2] | Describe category, weight, width and era, optionally "similar to X" as a cue. An exact font means hybrid. |
| 5 | Canvas and aspect first, then layout, then subject | Community atlas of 162 prompts [C20]; OFF "define the canvas and hierarchy" [S1] | Adopt |
| 6 | Layout zones or fixed-region schema; control the number of modules | [C20, C22] | Adopt, especially for infographics and posters |
| 7 | Promotional hierarchy plus a distance test ("three glances") | [C20] | Adopt |
| 8 | JSON or config-style prompts | OFF: any maintainable format works [S1, S3]; community uses JSON for complex product renders [C20]; FLUX.2 and Ideogram 4 are JSON-native [M7, M3] | Labeled lines by default. JSON is optional; there is **no evidence it improves GPT text accuracy**. |
| 9 | Creative-brief framing for ads | OFF [S3] | Adopt for full-AI concepts |
| 10 | Named style anchors (movement, era, print technique) | [C15, C20] | Adopt, to escape the identikit look (§6 row 13) |
| 11 | Reference images with explicit roles | OFF [S1, S3, S10]; typed roles [C26]; references alone are under-weighted, so restate must-keeps in text [C23 via L1 master §9.0] | Adopt |
| 12 | Layout-guide image as an invisible construction reference | OpenAI's own `hatch-pet` skill [S17] | Adopt for full-AI layout control; the guide must carry **no labels** |
| 13 | Short, targeted exclusions | OFF uses exclusions [S1]; "negation is for strong priors" [C20]. FLUX.2 does *not* support negatives [M7]. | Keep avoid-lines short. Do not import FLUX's "positive only" rule. |
| 14 | Hex guard | Community saw hex codes and colour names printed as labels [C23] | Adopt: add one line saying colour values are guidance only |
| 15 | One change per iteration; restate what must not change | OFF [S1, S3] | Adopt |
| 16 | Finalize the copy before the image prompt | [C27] | Adopt (`copy.json`) |
| 17 | Fresh context per asset | Earlier chat copy leaked onto a poster [C15] | Adopt; one `codex exec` per job already does this |

---

## 3. Route decision guide

### 3.1 Definitions

- **Full-AI.** GPT Image renders the whole design, text included. We only crop or resize, then run the text gate (§4.4).
- **Hybrid.** GPT Image renders text-free layers only:
  - a plate with a reserved zone;
  - cutouts, textures, 3D objects and illustrations;
  - optionally, a lettering-art layer of 1–3 words.

  HTML/CSS sets all informational text, SVG logos, SVG charts and QR codes, and headless Chrome renders the PNG or PDF at the exact size.
- **Hybrid variants**
  - **H1 plate + type** is the default.
  - **H2 cutout layers + type** covers products, people and 3D objects on transparent backgrounds [S6].
  - **H3 AI lettering layer + HTML info** uses a transparent PNG of 1–3 words (chrome "SALE", neon title) with the information typeset in HTML.
  - **H4 comp-first:** approve a full-AI comp, then make a text-free plate by regenerating the same brief with "no text", or by a "remove all text" edit. Typeset the real copy where the comp had it. This is our proposal; **UNVERIFIED** until tested.
  - **H5 hybrid-lite:** a full-AI art-led design with an HTML strip for date, price, CTA and logo.

### 3.2 Decision procedure — apply in order; the first match wins

1. **Client-critical data in the image** → hybrid for that element.
   - This covers price, date or time, phone, address, URL, promo code, QR or barcode, statistic, legal, medical or nutrition claim, and brand wordmark or logo.
   - Evidence: [S6, S10, C20, C21].
2. **Non-Latin copy** (Bengali, Indic, Arabic, Hebrew) beyond one headline of three words or fewer → hybrid.
   - A headline of three words or fewer may be AI-lettered, but only with native-reader sign-off.
   - Evidence: [C16, C18, M3].
3. **Print, or high resolution, or exact dimensions, or an extreme ratio** → hybrid (AI plate plus upscale or extension).
   - High resolution means more than about 1.6 MP on Codex, or more than 3.7 MP on the reliable API range.
   - An extreme ratio is anything beyond 3:1.
   - Evidence: [S1, S2, L1, P2].
4. **Series, template, multi-size or multi-language set, or the client needs editable source** → hybrid.
   - Evidence: the consistency limitation [S2].
5. **Copy exceeds Tier A** (§4.1) → hybrid, or the API route under Tier B with retries.
6. **The typography is the artwork** (lettering integrated with the image, three short Latin strings or fewer) → full-AI through the API at `high` or `xhigh` where possible, plus the OCR gate. Put any information block in HTML (H5).
7. **Concepts, moodboards, internal drafts** → full-AI.
8. **Anything else** (a simple social post, three short Latin strings or fewer, no data) → full-AI with the OCR gate. **Fall back to hybrid automatically after two failed regenerations.**

Why two regenerations [DER]: with *P* = the chance that all strings come out right, three attempts succeed with probability 1 − (1 − P)³.

| P | Success within 3 attempts |
|---|---|
| 0.8 | 99% |
| 0.6 | 94% |
| 0.33 | 70% |

Below about 0.6, full-AI becomes a slot machine.

### 3.3 Per-deliverable routing

| Deliverable | Default route | Full-AI is fine when… | Why | Generate (Codex) → final | Must-pass QA |
|---|---|---|---|---|---|
| Social post (1:1 / 4:5) | Full-AI if Tier A, otherwise H1 | ≤3 short Latin strings, no data, one-off | Headlines ~94% [C12]; compounding [DER] | 4:5 → 1122×1402 → 1080×1350 | OCR set-diff; read at phone size |
| Story (9:16) | H1 | Art-only background, or one huge word | App UI covers the top and bottom bands; common advice is ~14% / 250 px top and bottom (**UNVERIFIED**) | 9:16 (native unmeasured) → 1080×1920 | Safe-zone overlay; OCR |
| Carousel | H1 template plus a plate per slide from one anchor | The cover slide, if art-led | Consistency limitation [S2]; one-approved-sample pattern [C25] | 4:5 or 1:1 | Contact sheet across slides; OCR per slide |
| YouTube thumbnail | H1 headline overlay; full-AI if the text *is* the illustration | 1–3 words of 3D or integrated lettering | Overlay recipe in R1; spec [P1] | 16:9 → 1672×941 → 1280×720 (API 3840×2160 for 4K) | Legible at 120–168 px wide (R1); keep the bottom-right clear for the duration badge (common practice, **UNVERIFIED**) |
| Banners: web hero, ad sizes, social covers | H1 | Never, for final multi-size sets | 3:1 generation limit [S1]; LinkedIn 1512×256 [P2] | 16:9 / 3:1 plate; extend in CSS | Per-size overflow; contrast; crops |
| Poster (event or promo) | H5 (AI art or title, HTML info), or H1 | Typographic or art poster, ≤3 strings, no dates | Event facts must be exact [C20]; print resolution | 2:3 / 3:4 | OCR; proof at print size |
| Flyer (print) | H1 → vector PDF | Digital-only and Tier A | Resolution; dense information [S10] | 2:3 plate → A5/A4 PDF | Vector text; bleed; overflow |
| Brochure | H1 (HTML→PDF) | Cover art only | Body text unreliable [C22, C24] | A plate per panel | Pagination; overflow |
| Infographic | Hybrid (SVG charts and labels with AI illustrations) | Illustrative explainer, ≤12 short English labels, no numbers | Better infographics in 2.5 [S12]; deterministic charts [S6] | 2:3 / 16:9 | Every label and relation against the source |
| Info card (quote, stat, tip) | H1 | A one-line English quote | The text *is* the content | 1:1 / 4:5 | Exact text and attribution |
| Special-day post | H1 (greeting in HTML) plus AI illustration | A short English greeting | Bengali/Arabic risk [C16]; religious text must be exact (policy, §8.3) | 1:1 / 4:5 | Native and cultural review |
| Logo | Full-AI concepts → final **SVG** (hybrid) | Never as the final raster | Brand consistency [S2]; official logo guidance [S1]; Codex skill prefers native vector for logo systems [S16] | 1:1, transparent | Vector rebuild; 16 px favicon test |
| Brand kit | Hybrid: tokens, SVG logo, AI imagery and mockups | Moodboards | [S2]; brand manuals need "don'ts" [C22] | Varies | Logo pixel-exact in every mockup |
| Ads (Meta, Google) | Full-AI for concepts, H1 for the delivered sets | A single-size Tier A creative | Creative-brief pattern [S3]; exact copy and claims; many sizes | Per placement | Claims check; OCR; per-size render |
| Image-to-banner (client photo) | H2: AI extends or restyles the background, the original subject is composited back, text in HTML | Re-rendering the subject is acceptable | Identity and label drift in edits [S1, C4] | Target aspect | Pixel diff of subject and labels |
| Menu *(extra)* | H1 | — | Prices must be exact. Generated food photos may misrepresent the product [C5]. | 2:3 | Price check against the POS list |
| Packaging mock *(extra)* | Full-AI mock; label from real artwork | Concept only | "Include ONLY this text" pattern [S1] | 1:1 | Label text |
| App or UI screen *(extra)* | Real screenshot composited in a device frame | Concepts only | Generated UI is not the client's product [S1 UI guidance] | Per device | Never present as the real app |

### 3.4 Cost and time trade-off [DER]

- **Full-AI:** 1 call plus retries, and each retry costs a full call. On Codex, image turns use plan limits 3–5× faster [S10].
- **Hybrid:**
  - one plate call per aspect, plus a render of a few seconds;
  - copy variants (A/B, languages, sizes) only need a re-render, so they cost almost nothing;
  - consistency across a series is free.
- Hybrid carries a one-time template-engineering cost. Full-AI carries a per-asset QA cost.

---

## 4. Text-in-image rulebook (full-AI route)

### 4.1 Text budget tiers

Numbers marked **house heuristic** come from the cited evidence but have not been measured by us. Calibrate them with §11.

**Tier A — full-AI with the OCR gate**

- At most 3 strings: headline, subline, CTA. House heuristic, from [C12] and [DER], and from the local finding that three or more exact strings is a known failure trigger [L1].
- Headline ≤ 6 words / 35 characters; subline ≤ 10 words / 60 characters; CTA ≤ 3 words. House heuristic.
- Latin script only. Digits only as one simple token, such as "2026" or "50%". House heuristic, from [C20, C21].
- Rendered cap height: headline ≥ 6% of canvas height, all other text ≥ 3% (about 31 px at 1024). House heuristic; OFF advises against tiny text [S1].
- Engine: Codex is acceptable. Through the API, use gpt-image-2 `high` or 2.5 `high`/`xhigh` [S1, S3].

**Tier B — full-AI only through the API, with best-of-2–4 and retries; otherwise hybrid**

- 4–8 strings, at most 150 characters in total, labels of 3 words or fewer (callouts, diagram steps). House heuristic; the official diagram carries 8 labels [S1].
- A single non-Latin headline of 3 words or fewer, with native sign-off. House heuristic, from [C12, C16].
- Quality: 2.5 `xhigh` or `max`, or gpt-image-2 `high` [S1].

**Tier C — hybrid only**

- More than 8 strings, or more than 150 characters.
- Any sentence-length body text (more than about 20 words).
- Any price, date or time, phone, URL, code, statistic, address, or legal, medical or nutrition claim.
- QR codes and barcodes.
- Brand wordmarks.
- Exact brand typefaces.
- Fine print below 3% cap height.
- Bengali, Indic or RTL text beyond one short headline.
- Print, multi-size, multi-language or editable-source deliverables.

### 4.2 Why budgets matter: compounding [DER]

*P*(all strings correct) = *p*ⁿ, assuming independence. In practice errors correlate: all small text fails together.

| Per-string p | n=1 | n=3 | n=5 | n=8 | n=12 |
|---|---|---|---|---|---|
| 0.97 | 97% | 91% | 86% | 78% | 69% |
| 0.94 (headline, [C12]) | 94% | 83% | 73% | 61% | 48% |
| 0.87 (two-line subhead, [C12]) | 87% | 66% | 50% | 33% | 19% |

### 4.3 The rules

Each rule applies to every full-AI prompt.

- **R-T1 — freeze the copy first.** Keep copy in `copy.json`: role, text, language, casing, max_lines, must_exact [C27].
- **R-T2 — one labeled text block.**
  - Heading line: "Text — render exactly as written".
  - One string per line, each with its role and zone. Every string in straight double quotes [S1, S3, S16, C20].
- **R-T3 — count.** State "each string appears exactly once" [S1].
- **R-T4 — exclusivity.**
  - State "No other text anywhere", and list the classes that tend to leak in: extra words, numbers, labels, signage, logos, watermarks, UI, captions [S1, S3, S10].
  - If a prop must carry text, give that text exactly. Otherwise leave text-bearing props out entirely [L1 lint].
- **R-T5 — casing.** Write each string in its final casing and add "preserve capitalization and punctuation exactly". Sunburst changed casing once [S10, C7].
- **R-T6 — line breaks.** State "on one line", or give "Line 1: … / Line 2: …" [S10 example].
- **R-T7 — hierarchy and placement.**
  - Give relative sizes, for example "headline ≈ 9% of image height; subline ≈ 40% of headline".
  - Give zones, for example "top 30%, left-aligned, 8% side margins" [S1, S3, C20].
- **R-T8 — typography.** Describe category, weight, width, contrast, colour and treatment. Add a named font only as a cue ("similar to Inter"); matching an exact font requires hybrid [S3, M3].
- **R-T9 — rare words.** Letter-by-letter spelling for brand names and uncommon words, proactively or on the first failure [S1, C21].
- **R-T10 — digits.** Tier A allows simple numerals only. Everything else goes to hybrid [S6, C20].
- **R-T11 — hex guard.** When the prompt carries colour codes, add a line saying colour values are guidance only and must not be printed [C23].
- **R-T12 — one artifact.** Ask for "one finished flat design filling the canvas; not a mockup, not a photo of a print, not a board of options" [C22, C20].
- **R-T13 — anti-default style.** Name a style anchor and keep a short avoid-list. One real forum prompt excluded generic gradients, stock icons, fake logos, mascots, glossy 3D blobs and empty decorative space [S14 COM example; C15].
- **R-T14 — engine and quality (API).**
  - Text work: `high`/`xhigh` on 2.5, or `high` on gpt-image-2.
  - Compare Flare and Sunburst on our own eval. In one test, Flare followed the formatting more literally [C7, n=1].
- **R-T15 — fresh session.** One asset per session, with no earlier copy in context [C15].
- **R-T16 — verbatim passthrough on Codex.**
  - The Codex agent authors the `image_gen` prompt [S15], and our Codex runs in Banglish [L2].
  - Assert that the prompt actually sent contains every exact string, compared byte-for-byte after NFC normalization, so a string is never paraphrased, translated or transliterated. The check reads the session rollout.
  - Keep briefs in files or quoted heredocs; in double quotes the shell expands `$imagegen` [L2].
- **R-T17 — hybrid-lite.** When an HTML strip will be added (H5), reserve and describe its zone as empty.

### 4.4 Text QA gate (applies to full-AI outputs and to hybrid plates)

1. **Extract.**
   - Have a vision model list every visible text item, one per line, keeping casing and punctuation — the official cookbook method [S5].
   - For non-Latin text, add Tesseract with the matching model: `eng`, `ben`, `hin`, `ara`… `tessdata_best` ships `ben` and `script/Bengali` [P7].
2. **Normalize both sides.**
   - Unicode NFC (Bengali specifics in §8.6).
   - Map dash variants, bullets and quote styles.
   - Collapse whitespace [S5 lesson].
3. **Set-diff.** Compare required against extracted and record four things: missing, extra, case mismatch, and count (each string exactly once).
4. **Placement.** Check each string sits in its zone, using the OCR box against the zone.
5. **Verdict rules** (as in the cookbook, never averaged [S5]):
   - any missing, extra or misspelled string → **FAIL**;
   - layout, style or artifact score below 3/5 → **FAIL**.
6. **Humans.**
   - A native reader for any non-Latin string.
   - A human 200%-zoom pass for client-facing assets [L1 master §11].
7. **Escalation.** Regenerate at most twice with one targeted correction each time, then switch to hybrid (§3.2 rule 8).
8. **Hybrid plates.** Extraction must return **nothing**, because text leaks onto plates through props [L2].

```python
import re
import unicodedata

DASH = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")
QUOTES = {ord("“"): '"', ord("”"): '"', ord("‘"): "'", ord("’"): "'"}

def norm(s):
    s = unicodedata.normalize("NFC", s).translate(DASH).translate(QUOTES)
    return re.sub(r"\s+", " ", s.replace("•", "·")).strip()

def gate(required, extracted):
    req = [norm(r) for r in required]
    got = [norm(e) for e in extracted]
    missing = [r for r in req if r not in got]
    extra = [g for g in got if g not in req]
    dup = [r for r in req if got.count(r) > 1]
    case = [r for r in missing if r.casefold() in {g.casefold() for g in got}]
    ok = not (missing or extra or dup)
    return ok, {"missing": missing, "extra": extra, "duplicated": dup, "case_only": case}
```

---

## 5. Prompt templates

**Conventions**

- Prompts are written in English; the exact strings are inserted verbatim from `copy.json`.
- `<…>` marks a slot to fill. Delete lines that do not apply.
- On the Codex route, the aspect goes in words in the first line (§1.2).
- These are our own templates, built from the patterns in §2.3; they are not copies of the official prompts.

### 5.1 Full-AI master skeleton

```text
Deliverable: <type> — <aspect in words and ratio, e.g. "vertical 4:5 portrait">. One finished flat design filling the whole canvas edge to edge; not a mockup, not a photo of a printed piece, not a board of options.
Purpose & audience: <who sees it, where, and the single action or feeling it must produce>.
Layout (zones): <zone list with approximate % of canvas, top→bottom / left→right>; outer margins at least <6–8>% on every side; nothing important within the margins.
Visual: <subject/scene/illustration>, <medium: photograph / flat vector / risograph print / 3D render>, <light>, <materials>.
Style anchor: <named movement, era, print technique or grid>; palette <2–4 colours in words>. Colour values are rendering guidance only — never print colour names or codes.
Typography: <category, weight, width, case, colour, treatment>; headline ≈ <X>% of image height; secondary text ≈ <40–50>% of headline size; crisp, evenly kerned letterforms; strong contrast with the background.
Text — render exactly as written, preserve capitalization and punctuation, each string exactly once, in these positions:
1) [headline · <zone>] "<…>"
2) [subline · <zone>] "<…>"
3) [cta · <zone>] "<…>"
No other text anywhere: no extra words, numbers, labels, signage, logos, watermarks, UI or captions.
Avoid: <2–5 targeted exclusions for strong defaults, e.g. generic gradients, glossy 3D blobs, stock icons, fake logos, pastel bunting and florals>.
```

### 5.2 Hybrid plate skeleton (a text-free visual with reserved space)

```text
Deliverable: text-free background plate for a <type>, <aspect in words and ratio>. Typography will be added later in a separate layer, so the plate must work without any text.
Reserved zone: <area, e.g. "left 45% of the frame" / "top 30%"> stays calm and low-detail — <tone: dark|light> <texture: soft paper grain / out-of-focus wall / smooth gradient> — with no objects, faces, edges or bright highlights crossing into it.
Subject & placement: <subject>, occupying <zone>, <facing or leading the eye toward the reserved zone>.
Visual: <medium>, <light direction and quality>, <materials>; style anchor <…>; palette <…> (guidance only, not text).
Crop safety: keep everything important inside the central <80>% so the plate also survives a <other aspect> crop.
Hard exclusions: no text, letters, numbers, logos, signage, labels, packaging text, screens, books with titles, price tags or watermarks anywhere.
```

**Cutout layer variant** (H2), following OFF guidance [S1, S6]:

```text
Isolated <object/person/product> on a fully transparent background. Centered with generous padding; crisp silhouette with no halos. No backdrop, floor, checkerboard or cast shadow (a shadow will be added later). <For an existing product: preserve its geometry and label exactly; do not restyle it.>
```

On the API, set `background="transparent"` with png/webp. On Codex, rely on the prompt, and use `transparent_background` once it ships [S15].

**Lettering layer variant** (H3), 1–3 Latin words; spell-check it like full-AI:

```text
The word "<WORD>" as <treatment: chrome 3D letters / hand-painted sign lettering / neon tube lettering>, spelled exactly <W-O-R-D>, alone on a fully transparent background; no other text or objects; letterforms fully visible with padding.
```

### 5.3 Hybrid typesetting contract (JSON spec rendered by headless Chrome)

```json
{
  "canvas": {"w": 1080, "h": 1350, "dpr": 2, "bleed_mm": 0},
  "plate": "plates/post-01.png",
  "safe": {"top": 0.06, "bottom": 0.08, "left": 0.08, "right": 0.08},
  "tokens": {"head": "Anek Bangla", "body": "Hind Siliguri", "latin": "Inter", "ink": "#101418", "accent": "#E4572E"},
  "layers": [
    {"role": "headline", "lang": "bn", "text": "বিজ্ঞান উৎসব ২০২৬", "box": [0.08, 0.07, 0.84, 0.22],
     "font": ["latin", "head"], "weight": 700, "size_max": 112, "size_min": 72, "max_lines": 2, "align": "start", "color": "ink"},
    {"role": "cta", "lang": "en", "text": "Register free", "box": [0.08, 0.86, 0.40, 0.06], "style": "pill"}
  ],
  "logo": {"src": "brand/logo.svg", "box": [0.78, 0.88, 0.14, 0.06]},
  "checks": ["fonts_loaded", "no_overflow", "contrast_aa", "zone_clear", "dom_text_equals_copy"]
}
```

**Renderer contract** (proposed)

- **Fonts:** use local OFL font files, never runtime web fonts. Wait for `document.fonts.ready` and `document.fonts.check()` for every family and string.
- **Language and direction:** set `lang` and `dir` on every text node.
- **Fitting:** shrink-to-fit between `size_max` and `size_min`. Fail on overflow or line clamp.
- **Contrast:** measure the plate luminance behind each box. Pick the ink colour, or add a CSS scrim, to reach WCAG contrast of 4.5:1 for normal text and 3:1 for large text [P9].
- **Screen output:** screenshot at DPR 2, then downsample to the exact pixel size.
- **Print output:** `page.pdf()` keeps text as vector. Chrome's PDF output is RGB-only (believed; **UNVERIFIED**), so check the print shop's CMYK needs.

### 5.4 Per-deliverable templates

Each block gives the full-AI version (FA) and the hybrid version (HY). Hybrid always means the §5.2 plate plus the §5.3 spec. Only what differs is shown.

#### 5.4.1 Social post (1:1 or 4:5)

**FA** (Tier A only):

```text
Deliverable: single Instagram feed post — vertical 4:5 portrait. One finished flat design filling the canvas; not a mockup or a board of options.
Purpose & audience: <e.g. announce a weekend workshop to local hobby painters; make them tap "Book now">.
Layout: top 28% headline zone; middle 52% hero visual; bottom 20% CTA strip; 8% side margins.
Visual: <hero subject>, <medium>, <light>.
Style anchor: <e.g. Swiss International Style, strict left-aligned grid, generous white space>; palette <off-white, ink black, one vermilion accent> (guidance only, not text).
Typography: heavy condensed grotesque for the headline (≈9% of height), regular grotesque for the subline (≈40% of headline), medium grotesque in a pill button for the CTA.
Text — render exactly as written, preserve capitalization, each exactly once:
1) [headline · top zone, left-aligned, one line] "<HEADLINE>"
2) [subline · under headline, left-aligned] "<Subline>"
3) [cta · bottom strip, pill button] "<CTA>"
No other text anywhere. Avoid generic gradients, stock icons, glossy 3D blobs, fake logos.
```

**HY plate:** use the §5.2 skeleton.

- Reserved zone: the top 30% plus the bottom 18%.
- Subject: the middle band, leaving room on both sides.
- Type in HTML: headline, subline, CTA, logo.

**QA:** OCR gate; view at 1080×1350 and at 360 px wide.

#### 5.4.2 Story or Reel cover (9:16)

**FA** only for an art background with at most one big word. **Default HY:**

```text
Deliverable: text-free vertical 9:16 story background plate. Keep the top 14% and bottom 20% free of important detail (app UI will cover them).
Reserved zone: centre-left band from 30% to 60% of height, calm and <dark> for a headline set later.
Subject: <subject> in the lower-middle, eye-line toward the reserved band.
Visual / style / exclusions: as in 5.2.
```

- The 14% and 20% bands are a heuristic based on the common ~250 px advice (**UNVERIFIED**; confirm with Meta's current spec).
- HTML: headline inside the safe band, link-sticker space kept empty, CTA above the bottom band.

#### 5.4.3 Carousel (N slides)

**HY:** one HTML template (cover, body and final-CTA variants) with one plate per slide.

1. Generate the **anchor** plate for slide 1 and approve it.
2. Generate every other plate from the anchor with this prompt:

```text
Image 1 is the approved anchor plate for this carousel — style reference only: copy its palette, lighting, texture, grain and illustration/photo treatment; do not copy its subject, layout or any marks.
Deliverable: text-free plate for slide <k> of <N>, vertical 4:5 portrait.
Reserved zone: <top 35%> calm and <light> for text added later.
Subject: <slide-specific visual>.
Hard exclusions: no text, letters, numbers, logos or watermarks.
```

- Always generate from the **anchor**, never chained from the previous slide [C1, S1]. This is the same approve-one-sample-first gate the PPT skill uses [C25].
- **FA** fits the cover slide only, when it is art-led.
- **QA:** a contact sheet of all slides side by side; OCR on every slide.

#### 5.4.4 YouTube thumbnail (16:9)

**HY** is the default. The plate follows the full recipe and the overlay type system in R1, section A.1.

```text
Deliverable: text-free 16:9 landscape YouTube thumbnail plate, bold and high-contrast, one focal subject.
Subject: <person/object> large in the right 55% (chest-up, face sharp, <emotion>), clean rim light separating them from the background.
Reserved zone: left 40% is a simple high-contrast color field / soft background for a 2–4 word headline added later; keep the bottom-right corner clear.
Hard exclusions: no text, letters, numbers, logos, UI or watermarks.
```

**FA** when the words are part of the illustration:

```text
Deliverable: 16:9 landscape YouTube thumbnail, one finished design.
Visual: <scene>; the words are part of the scene as <3D extruded letters / letters built from <objects>> in the left 45%, cap height about 16% of image height.
Text — exactly as written, one line, all caps as shown, exactly once: "<TWO OR THREE WORDS>".
No other text anywhere. Keep faces unobstructed; bottom-right corner clear.
```

**QA:** OCR; downscale to 168×94 and 120 px wide, and confirm the subject and the words still read.

#### 5.4.5 Banners (web hero, ad sets, social covers)

**HY** always for final sets.

1. Generate one plate per *aspect family* rather than cropping everything from one image:
   - 16:9 for the hero;
   - 3:1 for covers;
   - 1:1 and 4:5 for ads.
2. Extend ratios beyond 3:1 in CSS. For example, a 3:1 plate is placed right-aligned in a 1512×256 LinkedIn cover [P2], and the remaining left area is filled by one of:
   - a gradient sampled from the plate edge;
   - `object-fit: cover` with a blurred, mirrored copy of the plate behind it.

Plate prompt (3:1):

```text
Deliverable: text-free wide 3:1 banner plate.
Subject: <product/scene> in the right third; left two-thirds is a continuous, low-detail <texture/gradient/soft environment> that can be extended sideways without seams.
Hard exclusions: no text, logos, UI, signage, watermarks.
```

**FA** only for concept exploration.

#### 5.4.6 Poster (event or promo)

**FA** (art or typographic poster, no dates or venues in pixels) plus an HTML info strip (H5):

```text
Deliverable: vertical 2:3 poster, one finished flat artwork filling the canvas (not a framed print, not a mockup).
Concept: <one visual idea>; the title is the hero: letters <interact with the image — e.g. partly hidden behind / built from / carved into> <element>.
Style anchor: <e.g. 1960s Swiss jazz poster, two-colour screenprint, visible registration offset>.
Layout: title across the upper 40%; image in the middle; bottom 18% left completely empty and flat <colour> for an information strip added later.
Text — exactly as written, each once: [title] "<TITLE>"   (optional) [subtitle] "<Subtitle>"
No other text, dates, logos, sponsor strips or watermarks anywhere.
```

**HY** puts the date, time, venue, price, QR code and sponsor logos in HTML.

**Print:** use the API at 2:3, about 2048×3072 (**experimental** above 3.69 MP), or upscale a Codex plate. Text stays vector in the PDF.

#### 5.4.7 Flyer (print A5 or A4)

**HY → PDF.**

```text
Deliverable: text-free vertical A-series flyer plate (ratio ≈ 1:1.41 — generate 2:3 and crop), print-oriented, clean.
Reserved zones: top 35% flat and quiet for the title block; right column 40% (from 35% to 85% of height) quiet for details; bottom 12% plain for contact/QR.
Subject: <illustration/photo> in the lower-left, bleeding off the left edge.
Hard exclusions: no text, logos, prices, QR codes, watermarks.
```

- Headless Chrome builds an A4/A5 page: `@page` size plus a 3 mm bleed box and vector text.
- The plate is upscaled non-generatively (master §9.13).

#### 5.4.8 Brochure (tri-fold or multi-page)

**HY → PDF.** Use one plate per panel or spread, with a shared style lock, and make the cover plate the anchor.

- AI supplies covers, section illustrations and textures. HTML supplies all body copy, tables, maps and contact blocks.
- Do not ask GPT Image for body text. The community advice is to fill body areas with *simulated text blocks* only for comps [C22].

#### 5.4.9 Infographic

**FA** for an illustrative explainer (Tier B via the API, English, labels only, no numbers):

```text
Deliverable: vertical 2:3 educational infographic for <audience>, one finished flat design.
Structure: title band (top 12%); <5> numbered modules flowing top-to-bottom, each = icon + short label; thin arrows between modules; generous white space; consistent flat icon style.
Style: <clean flat vector, two-tone>, white background.
Text — exactly as written, each once:
[title] "<Title>"
[module 1 label] "<≤3 words>" … [module 5 label] "<≤3 words>"
No other text, numbers, footnotes, logos or watermarks. Avoid tiny text.
```

**HY** whenever there is data. Charts go in SVG (D3, Vega or hand SVG) with HTML labels [S6]. GPT Image supplies the hero illustration and the icon set as transparent PNGs:

```text
Set of <6> matching flat icons for <topic>, each isolated on a fully transparent background, same stroke weight and palette <…>, no text, no numbers.
```

**QA:** every label and every relationship against the source, not only the spelling [S1]. The official Images 2.5 system card claims better infographic accuracy [S12]; verify anyway.

#### 5.4.10 Info card (quote, stat, tip)

**HY.** A plate with a large reserved centre block and a calm texture. The quote, attribution, statistic (with source) and logo go in HTML.

**FA** only for a short English quote (Tier A) set as the design itself:

```text
Deliverable: square 1:1 quote card, one finished flat design. Background: <texture>; quote centered in a <serif> at ≈7% of height, attribution below at ≈40% size.
Text — exactly as written, each once: [quote] "<…>"  [attribution] "— <Name>"
No other text anywhere.
```

#### 5.4.11 Special-day post (Pohela Boishakh, Eid, Victory Day, Christmas…)

**HY** is the default: the greeting in HTML with a Bengali or Arabic font, and a festive illustration plate from AI.

```text
Deliverable: text-free square 1:1 festive illustration plate for <occasion> for <audience/brand>.
Motifs: <client-approved motifs, e.g. alpana patterns, clay pots, marigolds for Pohela Boishakh>; avoid stereotypes and costume clichés.
Reserved zone: centre 40% calm <cream> area for a greeting typeset later.
Hard exclusions: no text in any script, no calligraphy, no numbers, no logos, no watermarks.
```

- **FA** only for a short English greeting such as "Happy New Year". A short Bengali greeting of three words or fewer is allowed only under §8.4, with native sign-off.
- **Policy:** never let the model render religious text (Qur'anic verses, du'a, mantras). Use verified typeset or vector calligraphy supplied by the client (§8.3).

#### 5.4.12 Logo (concepts → vector)

**FA concepts:** 4–8 independent calls (API `n=4`), each on a transparent background [S1, S3]:

```text
Original, non-infringing logo concept for "<Brand>", a <what it is> for <audience>; personality <3 adjectives>.
Mark only (no lettering) — <idea: e.g. geometric monogram / abstract symbol built from <motif>>; flat, vector-like shapes, strong silhouette, balanced negative space; reads at 16 px; 1–2 colours <…>.
Centered with generous padding on a fully transparent background; no mockups, no 3D, no gradients, no text, no watermark.
```

**Final (hybrid):**

1. Rebuild the chosen mark as SVG, hand-written or traced and cleaned.
2. Set the wordmark in a licensed font with manual kerning.
3. Produce mono, reversed and favicon versions, and test at 16, 32 and 64 px.

Never ship the raster AI logo as the logo. The Codex skill itself says logo systems are better built as native vector [S16], and brand elements drift across generations [S2]. Check for trademark conflicts.

#### 5.4.13 Brand kit

**HY**

- **Deterministic assets:** `brand.json` tokens (colours, type scale, spacing), the SVG logo set, the type specimen, and the colour and "don't" pages. These are rendered as HTML to PDF.
- **AI-generated assets:**
  - mood imagery;
  - texture and pattern tiles;
  - scene plates for mockups: blank tote bag, storefront, business-card desk scene, all "blank surface, no marks".
- **Applying the logo to mockups:** either composite the real SVG in perspective in CSS, which is exact, or edit with the logo as a reference and then verify that the shapes match. Composite back if needed [S1, C26 logo role].

Mockup plate:

```text
Photorealistic <tote bag on a café chair>, the bag face is completely blank and flat-lit, <light>, no logos, no text, no prints anywhere in frame.
```

#### 5.4.14 Ads (Meta, Google, display)

**FA concept** — creative brief [S3]:

```text
Ad concept for <brand> — <positioning>; audience <…>; the single message: <…>.
Deliverable: square 1:1 social ad, one finished design; polished campaign look, <style anchor>.
Scene: <concept>; composition leaves the top-left third calm for the headline.
Text — exactly as written, each once: [headline] "<≤6 words>"  [cta] "<≤3 words>"
No other text, prices, claims, badges or logos anywhere.
```

**HY delivery set:** one plate per aspect (1:1, 4:5, 9:16, 1.91:1). HTML templates for each size carry the headline, offer, price, CTA, logo and legal line. Render every size. Run a claims check with no invented discounts, certifications or ratings [L1 rules].

#### 5.4.15 Image-to-banner edit (client photo → banner)

**H2**

1. Cut the subject or product out of the client photo (API edit with `background="transparent"`, or the existing `cutout` for clean backgrounds) [S1].
2. Generate a matching plate at the target aspect, using the photo as a *style and lighting reference*:

```text
Image 1 is the client's photo — reference for lighting direction, colour temperature and camera height only; do not copy the subject.
Deliverable: text-free wide 16:9 banner plate: <environment continuing the photo's setting>, an empty <surface/area> on the right third where the product will be placed, matching perspective and light from <direction>.
Reserved zone: left 40% calm for text.
Hard exclusions: no people, products, text, logos or watermarks.
```

3. Composite the *original* subject pixels in HTML with CSS drop-shadows and a colour match. Optionally run one "harmonize" edit, then composite the subject back so it stays pixel-exact [S1].
4. Typeset in HTML.

**Full-AI edit alternative:** only when re-rendering the subject is acceptable. Lock identity, product geometry and label text in the prompt [S1], then diff the result against the original.

---

## 6. Failure → mitigation table

| # | Failure | Typical trigger | Prevention (prompt/route) | Detection | Repair | Sources |
|---|---|---|---|---|---|---|
| 1 | Misspelled or garbled letters | Long or rare words, small text, many strings, `auto` quality | Tier A budget; quotes; letter-by-letter; larger type; API `high`/`xhigh` | OCR set-diff | One targeted edit or regenerate (≤2), then hybrid | S1, S3, C12, C21 |
| 2 | Extra or invented text (taglines, claims, specs, sponsor strips) | Promo-style scenes; chat context; the model "completing" an ad | "Render only these strings; no other text"; fresh session; no promo-y props | Extra set in the diff | Regenerate; hybrid | C20, C15, S5 |
| 3 | Duplicated text | Headline mentioned twice in the prompt; repeated layout motifs | "Each string exactly once"; mention each string once | Count check | Regenerate | S1, S3 |
| 4 | Casing or punctuation drift | Model style defaults | Write the final casing; "preserve capitalization and punctuation" | Case-sensitive diff | Edit or regenerate | C7, S10 |
| 5 | Hex codes or colour names printed as labels | Colour codes inside a text-heavy prompt | Hex guard line (R-T11); prefer colour words | Extra set in the diff | Regenerate | C23 |
| 6 | Small text wavy or illegible | Fine print below about 3% height; Codex `auto` quality | Tier C to hybrid; API `high` or above | Zoomed OCR | Hybrid | S1, S3, C14 |
| 7 | Wrong numbers, prices, dates; chart shapes that disagree with the values | Any numeric content | Hybrid; deterministic SVG charts | Diff against the source data | Rebuild in HTML/SVG | S6, C24, C20 |
| 8 | Fake logos, brand marks, maker marks on products or clothes | Real-brand-adjacent scenes; sportswear; packaging | "No logos or trademarks"; plain items; supply the real logo and composite it | Vision check for marks | Local edit, then composite; or regenerate | S1, L2, C20 |
| 9 | Cluttered layout, flat hierarchy | "Make an infographic about X"; too many modules | Zones; module count; size ratios; three-glances test | Layout score below 3 | Simplify; hybrid | C20, C22, S5 |
| 10 | Mockup or moodboard instead of a flat design (framed print, wall, several variants) | "Poster" read as an object | R-T12 wording | Vision check | Regenerate | C22 |
| 11 | Text placed off-zone or overlapping the subject | Composition control is imprecise | Zones plus a layout-guide image; reserve empty areas | OCR box against the zone | Hybrid | S2, S17 |
| 12 | Text clipped by the edge or the platform UI | No margins; wrong aspect | Margins; generate at the target aspect; safe zones | Safe-zone overlay | Re-render (hybrid) | L1, P1 |
| 13 | "AI poster look": identikit pastel florals and bunting, glossy 3D, bokeh or orbs, generic gradients, warm cast | Generic prompts; default taste | Named style anchor; restrained palette; avoid-list; real typography (hybrid) | Human or judge taste check | Restyle | C15, C5, C8, S14 |
| 14 | Unrequested embellishment (extra props or elements, more "detail") | Sunburst tends to embellish | "No additional elements"; exact counts; compare with Flare | Diff against the brief | Regenerate | C7, C20 |
| 15 | Edit drift: unrequested changes, blur, contrast creep, plastic faces | Chained edits; repeated passes | Edit from the original; one change per pass; restate what must not change; at most 2 chained edits | Pixel or SSIM diff outside the target | Composite the region back | S1, C1, C4 |
| 16 | Mask not respected (the edit spills outside it) | Masks are guidance only | Mask plus composite back | Diff outside the mask | Composite | S2, C2 |
| 17 | Wrong output size or aspect | Codex has no size control; the backend rounds sizes | Aspect in words; plan the crop or pad | Read the decoded size | Crop, pad or extend (hybrid) | L1, C26 |
| 18 | Too low-resolution for print | ~1.57 MP on Codex; the API cap | Hybrid vector type; API 2K plate plus non-generative upscale | ppi check | Rebuild | S1, L1 |
| 19 | Broken Indic or RTL shaping (reversed order, missing vowel signs, split conjuncts) | Non-Latin text in pixels | Hybrid with proper fonts; ≤3-word rule plus a native reader | Native review; Tesseract | Hybrid | C16, C18, M3 |
| 20 | Painted checkerboard instead of real alpha | The prompt describes a background; unsupported path | `background="transparent"`; the prompt describes an isolated subject only | Check the alpha channel | Regenerate | S1, S6 |
| 21 | Brand drift across a series (palette, style, logo) | Each image generated independently | Style lock; anchor reference; HTML template; SVG logo | Contact sheet | Regenerate from the anchor | S2, C25 |
| 22 | Style reference leaks content (its text, people, layout copied) | Reference with no stated role | Role line: "palette and texture only; do not copy subjects, layout or text" | Vision check | Regenerate | C26, S1 |
| 23 | Text-bearing props in a no-text plate (menus, screens, books, signs) | Scene realism | Leave them out or turn them away (lint) | OCR must find nothing | Regenerate | L2 |
| 24 | Exact copy altered before it reaches the image model (paraphrased, translated, transliterated) | The Codex agent writes the tool prompt; Banglish AGENTS.md | R-T16 passthrough check; English meta-instructions; copy passed from a file | Compare the rollout prompt with `copy.json` | Re-issue | S15, L2 |
| 25 | Quality regression days (sudden worse output) | Backend changes reported by users | Keep an eval canary; pin API snapshots where possible | Canary score drop | Switch engine or model | C3 |

---

## 7. Editing workflows

### 7.1 Replace or correct text in a generated design

**Decision:** if the design is hybrid, edit `copy.json` and re-render; there is no generative step and no risk. If it is full-AI:

1. **Is the change short and the same length?** A typo, a date or a name → one targeted edit. The community rates short edits high-stability and number edits medium-high [C24].
2. **Does the change reflow the layout?** A longer string, a new line or a new block → do not edit. Regenerate, or switch to hybrid.
3. Always edit the **original approved image**, never an already-edited copy. Quality drops with every edit pass [C1].

Edit prompt, modelled on the official localization sample [S16] and the FLUX Kontext replacement convention [M8]:

```text
Image 1 is the approved design. Change only the text "<wrong string>" so it reads exactly "<correct string>" — same typeface style, weight, size, colour, alignment, position and line breaks. Keep everything else exactly as it is, including all other text, the layout, colours, imagery and margins. Do not add any text.
```

**API route**

- Send the original at the same size.
- Add a mask with an alpha hole over the text box plus 12–24 px [S2; mask polarity in L1 master §9.3].
- Use Sunburst for edit precision [S7], at `high`.

**Codex route**

- Load the file with `view_image`, then run a built-in edit with `referenced_image_paths` [S15, S16]. No mask is available.

**Then**

- **Composite back** only the text box region, feathered 6–12 px, onto the original. The official line is that pixel-identical regions need compositing [S1].
- Run the OCR gate on the whole image.
- **Stop rule:** after 2 failed edits, rebuild that text in HTML over a text-free patch.

**Edited images are downsampled first.** One user measured about a 1,536-patch vision budget for input images (e.g., 1248×1248), so small text in a dense source image loses detail when edited [S14 COM, **UNVERIFIED**]. Another reason to prefer hybrid for dense layouts.

**Translation of a whole design:** the official edit-translate pattern works, and the result must be checked for words left in the original language [S1]. For Bengali, Hindi and Arabic, rebuild the design in hybrid instead (§8).

### 7.2 Extend or outpaint to another aspect ratio

Options, best first:

1. **Generate natively at each aspect** with the same style lock plus the approved image as a *style reference*. This is the best quality and needs no seams.
2. **Crop from a wider master.** Codex 16:9 comes out at 1672×941, so each crop loses resolution.
3. **Extend in CSS for flat or abstract backgrounds.** Use gradients sampled from the edges, a blurred mirror behind the image, or a pattern tile. This is deterministic, ideal for banners, and handles ratios beyond 3:1 (§5.4.5).
4. **Generative extension of an approved plate (API):**
   - pad the canvas;
   - fill the new area with a blurred edge extension, never black or transparent;
   - mask the new area plus a 16–48 px overlap;
   - prompt "extend the scene naturally; keep the original area unchanged";
   - composite the original back.

   Full procedure and code: L1 master §9.12.

   **Caveats:**
   - The API says edits can produce an "extended" image [S9].
   - A community test on gpt-image-2 found transparent input regions are not read as transparency, and the model wrote outside the mask [C2].
   - Treat this option as best-effort and always composite back.

Recompose prompt for option 1 or 4:

```text
Image 1 is the approved <4:5> text-free plate. Create the same scene as a <16:9> landscape frame: extend the <sky/wall/floor/table> naturally to the left and right, continuing perspective, light and texture. Keep the subject identical in shape, colour, scale and position within the scene. Add no new objects, no text, no frames or borders.
```

### 7.3 Place a product photo into a designed layout

Preferred route, H2 (pixel-exact product):

1. **Cutout.** Use the API edit with `background="transparent"` and the official extract-product wording: preserve geometry and label legibility, no restyling, no shadow [S1]. For clean studio shots, the existing `cutout` command does the same.
2. **Scene plate.** Generate an "empty surface at <camera height/angle>, light from <direction>, no products, no text" plate at the target aspect (§5.4.15).
3. **Composite in HTML.** Place the product with a CSS contact shadow (a blurred ellipse), a drop shadow, and a slight colour match (CSS filters) to the plate's white balance.
4. **Optional harmonize pass** (API edit on the flattened composite):

   ```text
   Add a natural contact shadow and matching ambient light on the product; do not change the product, its label or any text; change nothing else.
   ```

   Then composite the product pixels back.

Full-AI alternative: an edit with the product photo as Image 1 and a layout or style reference as Image 2 [S1, S3].

- Risk: the label text is re-rendered and can warp [S1 caveats; C4].
- Accept this only for concepts, or check the label word by word and composite it back.

### 7.4 Keep brand consistency across a series

1. **Style lock.** A fixed text block pasted verbatim into every prompt: medium, palette words, light, texture and grain, illustration or photo treatment, "don'ts". This pattern appears as a campaign style lock in the community and as a brand-DNA block in OpenAI's transparent-assets cookbook [C21, S6].
2. **Anchor image.** The first approved asset is passed as a *style-only* reference with an explicit role to every later job. Codex allows at most 5 references [S15]; restate the must-keeps in text [C23].
3. **Generate each asset from the anchor, not in a chain.** Chaining accumulates drift [S1, C1]. The PPT skills use the same approve-one-sample-first gate [C25].
4. **Deterministic brand layer.** The logo SVG, fonts, colours, spacing and the text template stay in HTML, so they cannot drift.
5. **QA.** A contact sheet of the series side by side. Reject outliers in palette, grain, light direction or illustration style, and regenerate them from the anchor.

---

## 8. Multilingual, with Bengali first

### 8.1 Evidence

| Claim | Source | Strength |
|---|---|---|
| Images 2.0 supports high-fidelity text in Japanese, Korean, Chinese, Hindi and Bengali | OpenAI launch, as quoted by VentureBeat on 2026-04-21 [C9]; echoed on 2026-04-22 [C11]. The OpenAI post itself returned 403 to our fetcher. | Official claim; no data |
| gpt-image-2 "improved multilingual text rendering" | OpenAI staff forum post, 2026-04-21 [S13] | Official claim; no data |
| Single-line headlines above 85% in 10 languages; Arabic, Devanagari and kanji above 90% | Oakgen [C12 VEN] | Unverified; **Bengali not included** |
| Editing text across scripts: Bengali average 2.285 against English 2.982 on a 0–5 scale (−0.697). Errors: missing or corrupted diacritics, unnatural direction, distorted script structure. RTL scripts show reversed order. | MultiTextEdit, arXiv 2605.08163, May 2026. 12 models including GPT-image-1.5 and Nano Banana 2 — **not gpt-image-2 or 2.5** [C16] | Peer-review-style benchmark; older models |
| Arabic, Hindi and Korean lag badly in multilingual text rendering (Qwen-Image, Nano Banana and others; no GPT model tested) | LingT2I, arXiv 2608.11002, 2026-08 [C17] | Benchmark; different models |
| Non-Latin scripts "often produce unpredictable results"; add text afterwards in an editor | Ideogram official docs [M3] | Official, for Ideogram |
| Multilingual output can contain grammar mistakes; small text and spelling can fail | Google, Nano Banana Pro tips, 2025-11-20 [M2] | Official, for Google |
| Frontier VLM OCR errs on Devanagari conjuncts, vowel signs and nukta; the best reach chrF++ 82–86 on real scans | arXiv 2606.29213, 2026-06-28 [C18] | Benchmark: our automated QA readers are imperfect for Indic scripts |

**Bottom line.** No independent, per-string Bengali accuracy figure exists for gpt-image-2 or 2.5. We must measure it (§11) and treat Bengali as high-risk until we have.

### 8.2 Bengali: where AI rendering breaks

A native reviewer must check these features, and QA must diff them:

- **Conjuncts (যুক্তাক্ষর).** Examples: ক্ষ, জ্ঞ in বিজ্ঞান, ন্ত্র in মন্ত্র, ষ্ণ in কৃষ্ণ. Expect them to be dropped, split with a visible hasanta, or replaced by a lookalike [C16 error types].
- **Vowel signs (কার)** above, below and on both sides (ো, ৌ, ি before the consonant). Expect a missing or misplaced sign [C16].
- **Reph and ra-/ya-phala.** Examples: কর্ম, প্রিয়, ব্যবসা. The special case র‍্যা needs a zero-width joiner (U+200D), which a model cannot be told about reliably.
- **Nukta letters য় ড় ঢ় and khanda ta ৎ** (উৎসব).
- **The headline stroke (মাত্রা).** A broken stroke makes words look foreign. Letter-spacing in CSS breaks it too [P3].
- **Bengali digits ০–৯ and the taka sign ৳.** Models may silently switch to Latin digits.

### 8.3 Policy

- **All Bengali copy is typeset in HTML (hybrid)** by default.
- The model may render **at most one Bengali headline of three words or fewer**, and only when the lettering *is* the art (for example, festive hand lettering of "শুভ নববর্ষ"). It needs native-reader sign-off. The HTML fallback must be ready.
- **Never AI-render** religious text (Qur'anic Arabic, du'a, mantras), names of people, legal text, prices, or any Bengali longer than a headline. This is a risk policy, not a measured rule.
- Mixed Bengali-English posts: the English display word may be AI art under Tier A; the Bengali lines go in HTML.

### 8.4 If AI must render a short Bengali headline (Tier B)

```text
Text — render exactly these Bengali characters, as written, once; do not translate, transliterate or add Latin letters: "শুভ নববর্ষ"
Script: Bengali (Bangla) script, standard modern spelling; keep every conjunct, vowel sign and the continuous headline stroke intact; Bengali digits only if digits appear.
Lettering style: <hand-painted festive lettering / bold modern Bengali display letters>, ≈12% of image height, centered in the top third, on one line.
No other text in any script anywhere.
```

- Put the Bengali string in `copy.json` and pass it by file.
- Verify the prompt that was sent, byte for byte after NFC (R-T16). Our Codex instance writes Banglish by default [L2]; that must never touch the copy.
- Accept only after (a) Tesseract `ben` plus a vision reader agree with the string, and (b) a native reader approves.

### 8.5 Hybrid Bengali typesetting: the practical rules

**Fonts.** All are OFL on Google Fonts and ship the Bengali subset; checked in the google/fonts repo on 2026-09-23 [P6].

| Font | Coverage |
|---|---|
| Noto Sans Bengali | Variable; weight 100–900, width 62.5–100 |
| Noto Serif Bengali | Variable; weight 100–900, width 62.5–100 |
| Hind Siliguri | Weights 300–700 |
| Anek Bangla | Variable; weight 100–800, width 75–125 |
| Baloo Da 2 | Variable; weight 400–800 |
| Tiro Bangla | Regular and italic |
| Atma | Weights 300–700 |
| Mina | Weights 400 and 700 |
| Galada | Weight 400; display only |

Bundle the files locally. Do not load fonts at render time.

**CSS rules**

| Rule | Reason |
|---|---|
| Set `lang="bn"` on Bengali nodes | Correct shaping and line breaking. Chrome shapes through HarfBuzz and falls back font by font [P4]. |
| **Never** set `letter-spacing` or `word-spacing` hacks on Bengali | The W3C gap analysis lists letter-spacing splitting conjuncts and adding stray spaces [P3]. |
| No `::first-letter` drop caps; avoid `text-decoration: underline` | Conjuncts are not selected as one unit; underlines must clear the vowel signs [P3]. |
| Set `font-synthesis: none` | Prevents faux bold or italic on single-weight fonts such as Galada. |
| Line-height ≥ 1.4–1.6 | Vowel signs above and below need room (house heuristic). |
| Mixed script: `font-family: "Inter", "Hind Siliguri", sans-serif` | Latin characters use Inter; Bengali characters fall through to Hind Siliguri. |
| Digits: follow the copy | Use ০–৯ and ৳ where the copy is Bengali; the W3C notes users need script-specific numerals [P3]. |
| Never render Bengali with Pillow unless Raqm is present | The Pillow docs call Raqm the recommended engine for all non-English text [P5]. The skill's current `og` command is Latin-only [L1]. |

### 8.6 Bengali QA

- **Normalize both sides to NFC before comparing.**
  - য় (U+09DF), ড় (U+09DC) and ঢ় (U+09DD) are *composition exclusions*: NFC turns them into base + nukta (U+09BC).
  - ো (U+09CB) and ৌ (U+09CC) compose in NFC.
  - Checked with Python `unicodedata` and the Unicode CompositionExclusions.txt on 2026-09-23 [P8].
- **Hybrid output:** compare the *DOM text* against `copy.json`, which is exact by construction. OCR is only a sanity check that the font rendered (no tofu, i.e. no empty boxes for missing glyphs).
- **AI-rendered Bengali:** run Tesseract `ben` or `script/Bengali` [P7] alongside a vision-model reader. Disagreement between the two means a human decides. Automated readers themselves err on Indic conjuncts [C18], so a **native reader is mandatory** for client-facing Bengali.
- **Diff by grapheme cluster, not code point.** Cluster boundaries do not always match syllabic conjuncts [P3 issue #87], so show the reviewer both strings side by side, enlarged.

### 8.7 Other scripts

- **Hindi / Devanagari.** Same pattern as Bengali: headline stroke, conjuncts, matras. Fonts: Noto Sans Devanagari, Mukta, Hind, Tiro Devanagari Hindi [P6].
  - Launch coverage claims Hindi works in 2.0 [C9].
  - A small e-commerce Hindi eval favoured GPT Image 1 over Gemini Flash [C19].
  - Hybrid by default.
- **Arabic / Urdu (RTL).**
  - Editing benchmarks show the largest drops, with reversed order and wrong joining [C16].
  - Hybrid always, with `dir="rtl"` and `lang="ar"`, and no letter-spacing on connected script.
  - Fonts: Noto Naskh Arabic, Noto Kufi Arabic, Cairo, Tajawal, Amiri, IBM Plex Sans Arabic [P6].
  - Use client-supplied, verified calligraphy for religious phrases.
- **CJK.**
  - Community reports gpt-image-2 does well on Chinese headlines [C12, C20]. CJK errors tend to be plausible-looking wrong characters [C16], so check lookalike characters (L1 master §11.8).
  - Fonts: Noto Sans SC, JP, KR and Noto Serif TC [P6].
  - `lang` drives line-breaking rules. Use `word-break: keep-all` for Korean.

---

## 9. Other models: where each is better or worse, and what carries over

### 9.1 Comparison

| Model (latest seen) | Text and design strengths | Weaknesses and limits | Unique features | Evidence |
|---|---|---|---|---|
| **GPT Image 2 / 2.5** (ours) | Top overall on Arena and AA as of Sep 2026. Strong instruction following, dense layouts and multilingual claims. Edit arena #1 is 2.5 Sunburst. | Edits lose fine detail versus Nano Banana and FLUX (one user). "Plastic" faces in product edits. About $0.21 per 1024² at max. Codex route has no size or quality control. | Transparent output; 3:1 to 1:3 at custom sizes up to 3840 px; Flare and Sunburst tiers | C28, C29, C5, C4, S1, S15 |
| **Nano Banana Pro** (Gemini 3 Pro Image), 2025-11-20; NB2 in 2026 | Legible text from taglines to paragraphs (claim). Localization and translation. 2K and 4K output. Up to 14 references and 5 people. Search-grounded infographics. | Google itself lists small-text and spelling errors and grammar mistakes in multilingual output. Below GPT on the overall arenas. | Google Search grounding; SynthID watermark | M1, M2, C28, C29 |
| **Ideogram 3.0 → 4.0** (4.0 open weights, 2026-06) | Text-first design tool. 4.0 is JSON-native with bounding boxes for placement (secondary sources). Style references (3.0: up to 3, **UNVERIFIED**). | Official docs: non-Latin text unpredictable; long text raises error rates; cannot name typefaces; not for text-heavy layouts. | Magic Prompt; per-element boxes in 4.0 | M3, C28, C29 |
| **Recraft V3 → V4 / V4.1** | V3 (2024-10-30): long text, and exact text size and position. V4 (2026-02): short to mid-length phrases; the only model with real editable SVG output. | V4 has no style creation (custom brand styles are V2/V3 only). Mid-table on the arenas. | Vector (SVG) output; brand styles in V3 | M4, M5, C29 |
| **Seedream 4.0 / 4.5 → 5.0** | 4.5 claims small, dense text for posters and brand visuals. 4K. Multi-image references. Cheaper. | One vendor test saw gibberish body text on 5.0 [C14]. No official limits stated. | Unified generate and edit | M10, M11, C14, C29 |
| **FLUX.2 / Kontext** | Claims reliable fine text for typography, infographics and UI. Up to 10 references (8 on pro). 4 MP. Kontext replaces text in place ("Replace 'A' with 'B'" plus keep font and colour). | No negative prompts; lower on the arenas. | JSON prompt schema; hex bound to objects | M6, M7, M8, C28, C29 |
| **Midjourney v7 → v8** | The v8 alpha note (2026-03-17) says text is much better "when in quotes"; native 2K `--hd`. A V8.1 release in April 2026 appears only in secondary sources (**UNVERIFIED**). | v7 text generally weak (community consensus, **UNVERIFIED**). No arena presence in our captures. | Style references (`--sref`); strong aesthetics | M9 |

### 9.2 Conventions that transfer to GPT Image

**Transfer as-is**

- **Quotes around exact text.** Universal: OpenAI, Google, Ideogram, BFL and Midjourney all use them [S1, M2, M3, M7, M9].
- **Numbered references with roles** ("Image A for pose, B for style") [M2, S1].
- **Describe typography** by class, weight and era. Ideogram cannot take font names; GPT treats names as loose cues [M3, S3].

**Transfer with adaptation**

- **Kontext text-replacement wording.** "Replace 'X' with 'Y' while keeping the same font style and colour" is the same shape as our §7.1 edit prompt [M8].
- **Hex bound to objects** (FLUX.2) → put colours in words, or bind hex to a named element *and* add the hex guard [M7, C23].
- **JSON schemas** (FLUX.2, Ideogram 4) are usable as labeled lines for GPT. There is no evidence they improve GPT's accuracy [S1].
- **Bounding boxes** (Recraft, Ideogram 4) → GPT has none; use zone percentages plus a layout-guide image [S17], or go hybrid.
- **Midjourney `--sref`** → attach a style reference with a "style only" role [S1, C26].

**Do not transfer**

- FLUX's "no negative prompts" rule. GPT follows short exclusions, and OpenAI recommends them [S1].
- Google's search grounding. It is not available in our routes; verify facts ourselves.

### 9.3 When another engine would be the better tool (outside today's pipeline)

- **Recraft V4:** a true SVG draft of an icon or logo.
- **Nano Banana Pro:** 4K photographic mockups with up to 14 references.
- **FLUX Kontext:** a surgical local text swap on a photo.

None of these change the core recommendation. The *text* in client deliverables belongs in HTML.

---

## 10. Recommendations for our skill

Numbered by priority. The target is `codex-imagegen`, or a sibling `design` skill that calls it.

1. **Add a `design` pipeline with an explicit route.**
   - Command: `design --type <social|story|carousel|thumbnail|banner|poster|flyer|brochure|infographic|infocard|special-day|logo|brandkit|ad|image-to-banner> --route auto|full-ai|hybrid --copy copy.json --brand brand.json`.
   - `auto` implements §3.2, uses the defaults in §3.3, and prints the chosen route with the reason.
2. **Make `copy.json` the single source of truth for text.**
   - Fields per string: `role`, `text`, `lang`, `script`, `case`, `max_lines`, `must_exact`, `kind` (plain, price, date, phone, url, claim, legal, brand).
   - A **text-budget linter** classifies Tier A, B or C (§4.1). It detects digits, currency, URLs, phone numbers and scripts by Unicode range, and **forces hybrid** for any `kind` other than `plain` and for non-Latin text beyond a ≤3-word art headline.
3. **Full-AI prompt compiler** (§5.1) with every rule from §4.3:
   - quotes, "exactly once", "no other text", casing, line breaks, zones and size ratios;
   - the hex guard, the one-artifact line, the style anchor and a short avoid-list.
4. **Verbatim passthrough check on the Codex route** (R-T16).
   - Read the actual `image_gen` prompt from the session rollout and assert that every `must_exact` string appears byte for byte after NFC.
   - Also keep Codex's meta-instructions in English and state "do not translate or transliterate quoted strings". Our Codex AGENTS.md answers in Banglish [L2].
5. **Text gate** (§4.4) as a subcommand: `textgate --image X --copy copy.json`.
   - A vision-model reader plus Tesseract for the scripts present (`eng`, `ben`, `hin`, `ara`…).
   - NFC plus punctuation normalization; missing, extra, count and case diffs; zone checks.
   - **FAIL on any text error, never averaged away.** Regenerate at most twice, then fall back to hybrid automatically.
   - Log everything to `.meta.json`.
6. **Hybrid renderer** (`typeset`): headless Chrome through Playwright or CDP.
   - Bundled OFL fonts, including the Bengali set in §8.5.
   - HTML templates per deliverable with the §5.3 contract: auto-fit, overflow fail, WCAG contrast with an automatic scrim, safe-zone overlays, DPR 2 then exact-pixel PNG, and vector PDF for print.
   - This replaces the Pillow path for any non-Latin text; today's `og` command is Latin-only [L1].
7. **Plate generator with zone QA.** The §5.2 prompt plus three deterministic checks on the reserved zone:
   - edge density or variance below a threshold;
   - OCR finds nothing;
   - a luminance measurement that chooses the ink colour.

   Failure means regenerate once, then add a CSS scrim.
8. **Aspect and size planner.**
   - Map each deliverable to its Codex generation aspect (native table), then to a crop, pad or CSS extension.
   - Ratios beyond 3:1 are extended in CSS. Print gets a 2K API plate or a non-generative upscale.
   - Record requested and actual dimensions, like the alek receipts [C26].
   - Measure the Codex 9:16, 21:9 and 3:1 native sizes that are still missing.
9. **Engine policy.** Report the model exactly as requested; C2PA cannot tell 2.0 from 2.5 [S14].

   | Job | Engine |
   |---|---|
   | Plates and Tier A full-AI | Codex (gpt-image-2, `auto`) |
   | Tier B text, print plates, masks, exact sizes | API engine (when a key exists) |
   | Precise edits | Sunburst at `high` |
   | Literal text layouts | Flare; to be validated [C7] |

10. **Series and brand system.**
    - `brand.json` tokens and an SVG logo set that is **never regenerated**.
    - One anchor image per campaign; every asset generated *from the anchor*, never chained.
    - A contact-sheet QA across the series (§7.4).
11. **Edit policy.**
    - Text change on a hybrid design → edit `copy.json` and re-render.
    - Text change on a full-AI design → one masked or edited pass from the original, composite the region back, OCR check, at most 2 tries, else hybrid (§7.1).
    - Never chain more than 2 generative edits.
12. **Logo workflow.**
    - AI concept marks, 4–8 independent transparent calls (§5.4.12).
    - The user picks one; it is rebuilt as SVG and the wordmark is set in a licensed font.
    - Test favicon, mono and reversed versions.
    - A raster AI logo is never delivered as final; flag trademark checks.
13. **Anti-"AI look" design library.**
    - Named style presets: Swiss/International, Bauhaus, risograph, letterpress, editorial magazine, brutalist, Japanese minimal, Memphis, 1960s screenprint, and so on [C15, C20].
    - Each preset carries a type scale, a palette rule and a default avoid-list (generic gradients, glossy blobs, bokeh or orbs, stock icons, fake logos, bunting and florals) [S14 COM example, C15].
    - The judge scores "AI-look" as part of taste.
14. **Bengali module.**
    - The fonts and CSS rules in §8.5; digit and taka formatting helpers; NFC-aware QA; a mandatory native-review checkpoint for any client-facing Bengali.
    - AI-rendered Bengali limited to ≤3-word art headlines with sign-off.
15. **Compliance.**
    - No invented prices, claims, certifications, ratings or testimonials. No generated UI presented as the client's app. No AI-rendered religious text.
    - Keep C2PA on raw masters and IPTC tags on exports, as today.
16. **Deliverable package.** Final PNG, JPG or PDF plus the source HTML, `copy.json` and `brand.json`, the plates, and a QA report (route, model, text-gate diff, checks, native sign-off). This lets any later text edit happen deterministically.
17. **Eval first, then thresholds** (§11). Re-run the eval canary after every `codex update` or model change; users reported silent quality shifts [C3].
18. **Adopt Codex's new `transparent_background` argument** once a release ships it (merged to main 2026-09-23) [S15]. Until then, keep the prompt-based transparency and the alpha checks.
19. **Keep briefs in files** (quoted heredocs) so Unicode, quotes and `$imagegen` survive the shell [L2].
20. **Cross-link R1** for the thumbnail headline-overlay system and the higgsfield brand-kit patterns, rather than re-deriving them.

---

## 11. Eval plan: measure before locking thresholds

- **Cases (about 48).**
  - 5 deliverables: social 4:5, story 9:16, thumbnail 16:9, poster 2:3, infographic with 6 labels.
  - 6 copy sets:

    | Set | Example |
    |---|---|
    | EN short | 2 words |
    | EN mid | 8 words, two lines |
    | EN with data | "$19.99", "12 Oct 2026", phone |
    | BN short | "শুভ নববর্ষ" |
    | BN mid with conjuncts and nukta | "বিজ্ঞান উৎসব ২০২৬", "২০% ছাড়, সীমিত সময়ের জন্য" |
    | Mixed BN+EN | — |

  - 2 routes (full-AI and hybrid). Some combinations are skipped.
- **Engines.** Codex (gpt-image-2 `auto`), 3 samples per case. API, if a key is available: 2.5 Flare `high` and Sunburst `high`/`xhigh`, 2 samples each.
- **Metrics.**
  - Per-string exact match (NFC); extra-text count; casing errors; zone adherence from the OCR box.
  - A plate-zone cleanliness pass rate (hybrid).
  - A taste and "AI-look" score from the judge plus a human.
  - Time and cost per *accepted* asset.
- **Readers.** Vision judge plus Tesseract (`eng` and `ben`) plus a native Bengali reviewer for every Bengali output.
- **Outputs.**
  - Replace the Tier A/B/C heuristics with measured per-string accuracy.
  - Set the fallback threshold of §3.2 rule 8.
  - Decide Flare against Sunburst for text.
- **Canary.** Keep 6 fixed cases and re-run them after any Codex or model update.

---

## 12. Open questions and unverified items

- Codex native sizes for 9:16, 21:9 and 3:1 (unmeasured).
- Whether Codex's backend ever serves 2.5 while requesting gpt-image-2. C2PA cannot tell [S14].
- Per-string Bengali accuracy on gpt-image-2 (Codex) and 2.5 (API) — **no public data**.
- Whether the H4 comp-first route (full-AI comp → text-free plate) keeps style and layout well enough to be worth it.
- Whether stating cap height as a percentage is honoured proportionally by the model.
- Flare as more literal than Sunburst for text rests on n=1 [C7].
- Reliability of generative outpainting through API masks on gpt-image-2 and 2.5. The community test was negative [C2].
- The input-image downsampling budget of about 1,536 patches [S14 COM].
- Story safe-zone percentages; Instagram, X and IAB sizes (not re-verified this session).
- Chrome PDF colour space for print (RGB-only is believed).

---

## 13. Sources

Access date is 2026-09-23 unless marked. Publication dates are given where known.

### OpenAI (official)

| Key | Source | URL | Date |
|---|---|---|---|
| S1 | Image prompting guide (GPT Image 2.5, with tabs for 2, 1.5 and 1) | https://developers.openai.com/api/docs/guides/image-prompting | Covers the 2026-09-08 release |
| S2 | Image generation guide (limitations, sizes, masks, costs) | https://developers.openai.com/api/docs/guides/image-generation | Captured 2026-09-23 |
| S3 | Cookbook: GPT Image Generation Models Prompting Guide | https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide | 2026-04-21 |
| S4 | Cookbook: gpt-image-1.5 Prompting Guide | https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide | 2025-12-16 |
| S5 | Cookbook: Image Evals for Image Generation and Editing | https://developers.openai.com/cookbook/examples/multimodal/image_evals | 2026-01-29 |
| S6 | Cookbook: Generate Transparent Image Assets for Campaigns and Presentations | https://developers.openai.com/cookbook/examples/multimodal/transparent-image-assets-for-campaigns-and-presentations | 2026-08-20 |
| S7 | Model pages: gpt-image-2 (snapshot 2026-04-21), gpt-image-2.5-sunburst and gpt-image-2.5-flare (snapshots 2026-09-08) | https://developers.openai.com/api/docs/models/gpt-image-2 (and /gpt-image-2.5-sunburst, /gpt-image-2.5-flare) | Captured 2026-09-23 |
| S8 | API changelog (gpt-image-2 2026-04-21; transparency preview 2026-08-20; 2.5 on 2026-09-08) | https://developers.openai.com/api/docs/changelog | — |
| S9 | Images API reference (edits take up to 16 images; "edited or extended image") | https://developers.openai.com/api/reference/resources/images | Captured 2026-09-23 |
| S10 | ChatGPT/Codex "Image generation" doc (text rules; Codex uses gpt-image-2; usage 3–5×) | https://learn.chatgpt.com/docs/image-generation | Captured 2026-09-23 |
| S11 | ChatGPT Images 2.0 System Card | https://deploymentsafety.openai.com/chatgpt-images-2-0 | 2026-04-21 |
| S12 | ChatGPT Images 2.5 System Card | https://deploymentsafety.openai.com/chatgpt-images-2-5 | 2026-09-08 |
| S13 | OpenAI forum: "Introducing gpt-image-2 — available today in the API and Codex" (staff post and replies) | https://community.openai.com/t/introducing-gpt-image-2-available-today-in-the-api-and-codex/1379479 | 2026-04-21 → 2026-06-24 |
| S14 | OpenAI forum: "Introducing GPT Images 2.5 in the API and ChatGPT" (announcement; replies with latency tests, C2PA "2.0" observations, token remap, input-downsampling test, and an anti-slop prompt example) | https://community.openai.com/t/introducing-gpt-images-2-5-in-the-api-and-chatgpt/1395897 | 2026-09-08 → 2026-09-22 |
| S15 | openai/codex `codex-rs/ext/image-generation/src/tool.rs`: model constant, `auto` quality and size, ≤5 references; PR #47484 adds `transparent_background` | https://github.com/openai/codex/blob/main/codex-rs/ext/image-generation/src/tool.rs | Main checked 2026-09-23; v0.149.1 capture |
| S16 | openai/codex imagegen skill (SKILL.md, references/prompting.md, sample-prompts.md) | https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen | Captured 2026-09-23 |
| S17 | openai/skills `hatch-pet` (layout guides as invisible construction references) | https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet | Checked 2026-09-23 |
| S18 | Image-token calculator formula, from the calculator script on the image generation guide; used for §1.3 | https://developers.openai.com/api/docs/guides/image-generation | Captured 2026-09-23 |

### Local (this machine)

| Key | Source | Date |
|---|---|---|
| L1 | `~/.claude/skills/codex-imagegen/` — SKILL.md; `references/cli.md` (native sizes table: 3:2 → 1536×1024, 2:3 → 1024×1536, 4:5 → 1122×1402, 1:1 → 1254×1254, 16:9 → 1672×941; `og` Latin-only); `references/master.md` (§9 editing, §9.12 outpaint, §9.13 upscale and A4 sizing, §11 QA) | 2026-09-23 |
| L2 | Project memory `codex-exec-imagegen.md`: Codex 0.156.1 still gpt-image-2; arguments; ~1.57 MP; latency; Banglish AGENTS.md; text-bearing props as a top failure; prompt-based transparency returns alpha | 2026-09-23 |

### Community and independent

| Key | Source | URL | Date |
|---|---|---|---|
| C1 | OpenAI forum: "Edited Images significantly degrade in quality" | https://community.openai.com/t/bug-edited-images-significantly-degrade-in-quality/1395704 | 2026-09-08 |
| C2 | OpenAI forum: how gpt-image models see masks and transparency (gpt-image-2 test) | https://community.openai.com/t/understanding-how-gpt-image-models-on-edits-see-mask-and-transparency/1381752 | 2026-05-25 |
| C3 | OpenAI forum: GPT Image 2 quality regression thread (OpenAI Support reply 2026-09-09) | https://community.openai.com/t/drastically-worse-gpt-image-2-quality-over-the-last-24-hours/1383092 | 2026-06-08 → 2026-09-09 |
| C4 | OpenAI forum: plastic-looking faces in product edits | https://community.openai.com/t/gpt-image-2-produces-plastic-looking-faces-in-product-edit/1394653 | 2026-09-03 → 2026-09-10 |
| C5 | Hacker News: ChatGPT Images 2.5 (AI menu "slop", edit detail loss, ~104 s → 35–40 s latency) | https://news.ycombinator.com/item?id=49614720 | 2026-09-08 → 2026-09-10 |
| C7 | Puter: GPT Image 2.5 review (poster test; casing drift) | https://developer.puter.com/blog/gpt-image-2-5-review/ | 2026-09-11 |
| C8 | DataCamp: ChatGPT Images 2.5 | https://www.datacamp.com/blog/chatgpt-images-2-5 | 2026-09-09 |
| C9 | VentureBeat (Carl Franzen): ChatGPT Images 2.0 launch coverage, quoting OpenAI on multilingual text | https://venturebeat.com/technology/openais-chatgpt-images-2-0-is-here-and-it-does-multilingual-text-full-infographics-slides-maps-even-manga-seemingly-flawlessly | 2026-04-21 |
| C10 | Neurohive: ChatGPT Images 2.0 explainer (paragraph-length claim unverified) | https://neurohive.io/en/news/chatgpt-images-2-0-openai-launches-image-generation-model-with-reasoning-2k-resolution-and-multilingual-text/ | 2026-04-21 |
| C11 | T2 Online (Mathures Paul): Bengali and Hindi text in Images 2.0 | https://t2online.in/tech/tech-news/openai-s-chatgpt-images-2-0-brings-clearer-bengali-and-hindi-text-to-ai-generated-visuals/2004757 | 2026-04-22 |
| C12 | Oakgen: GPT Image 2 review, 500 generations (VEN) | https://oakgen.ai/blog/gpt-image-2-review-500-generations | 2026-04-22 |
| C13 | invideo: ChatGPT Images 2.0 explained (VEN; percentages unsupported) | https://invideo.io/blog/chatgpt-images-2-0-explained/ | ~2026-04 |
| C14 | Atlas Cloud: 2026 image API benchmark (VEN, n=1 typography prompt) | https://www.atlascloud.ai/blog/tips/2026-ai-image-api-benchmark-gpt-image-2-vs-nano-banana-2-pro-vs-seedream-5-0 | 2026-06-12 |
| C15 | John Hartnup: "AI-generated posters don't have to be horrible" (identikit default look; extra text from chat context) | https://john.hartnup.uk/2026/06/07/ai-event-posters.html | 2026-06-07 |
| C16 | MultiTextEdit: cross-lingual text-in-image editing benchmark (arXiv 2605.08163) | https://arxiv.org/abs/2605.08163 | v2 2026-05-18 |
| C17 | LingT2I: cross-lingual consistency in multilingual T2I (arXiv 2608.11002) | https://arxiv.org/abs/2608.11002 | 2026-08-11 |
| C18 | "Can OCR-VLMs Read Devanagari?" (arXiv 2606.29213) | https://arxiv.org/abs/2606.29213 | 2026-06-28 |
| C19 | india-text-to-image-eval (Hindi e-commerce creatives; GPT Image 1 against Gemini Flash) | https://github.com/AAAaMMbbaarr/india-text-to-image-eval | Undated; accessed 2026-09-23 |
| C20 | wuyoscar/GPT-Image2-Skill: `references/craft.md` (162-prompt atlas rules), `docs/sunburst-samples.md` | https://github.com/wuyoscar/GPT-Image2-Skill | Last push 2026-09-09 |
| C21 | buluslan/gpt-image2-ecommerce: `references/craft.md` (text tricks, fallback to text-free base), campaign style lock, platform constraints | https://github.com/buluslan/gpt-image2-ecommerce | Last push 2026-09-17 |
| C22 | freestylefly/awesome-gpt-image-2: templates and pitfall guides (posters, infographics, documents, logos) | https://github.com/freestylefly/awesome-gpt-image-2 | Last push 2026-09-11 |
| C23 | JimLiu/baoyu-skills (hex codes rendered as labels; reference weighting; anchors) | https://github.com/JimLiu/baoyu-skills | Last push 2026-09-10 |
| C24 | JuneYaooo/gpt-image2-ppt-skills: `docs/edit_guide.md` (text-edit stability table) | https://github.com/JuneYaooo/gpt-image2-ppt-skills | Last push 2026-08-22 |
| C25 | ningzimu/codex-ppt-skill (approve one sample, then per-slide jobs using the same method) | https://github.com/ningzimu/codex-ppt-skill | Last push 2026-09-21 |
| C26 | AlekseiUL/gpt-image-2-5-agent-kit (reference roles; 1536×864 requested → 1672×941 returned; receipts) | https://github.com/AlekseiUL/gpt-image-2-5-agent-kit | Last push 2026-09-09 |
| C27 | smixs/visual-skills: `references/text-rendering.md` (write the text first, then the image) | https://github.com/smixs/visual-skills | Last push 2026-09-16 |
| C28 | LMArena leaderboards, text-to-image and image-edit | https://arena.ai/leaderboard/text-to-image · https://arena.ai/leaderboard/image-edit | Snapshot 2026-09-21 |
| C29 | Artificial Analysis leaderboards, text-to-image and editing | https://artificialanalysis.ai/image/leaderboard/text-to-image · https://artificialanalysis.ai/image/leaderboard/editing | Captured 2026-09-23 |

### Other models (official)

| Key | Source | URL | Date |
|---|---|---|---|
| M1 | Google: Nano Banana Pro announcement | https://blog.google/innovation-and-ai/products/nano-banana-pro/ | 2025-11-20 |
| M2 | Google: Nano Banana Pro prompting tips (text, localization, references, limitations) | https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/ | 2025-11-20 |
| M3 | Ideogram docs: Text and Typography (page references 4.0) | https://docs.ideogram.ai/using-ideogram/getting-started/prompting-guide/2-prompting-fundamentals/text-and-typography | Accessed 2026-09-23 |
| M4 | Recraft V3 announcement | https://www.recraft.ai/blog/recraft-introduces-a-revolutionary-ai-model-that-thinks-in-design-language | 2024-10-30 |
| M5 | Recraft V4 docs (SVG; no style creation) | https://www.recraft.ai/docs/recraft-models/recraft-V4 | V4 released 2026-02 |
| M6 | Black Forest Labs: FLUX.2 launch | https://bfl.ai/blog/flux-2 | 2025-11-25 |
| M7 | BFL: FLUX.2 prompting guide (quotes, hex, JSON, no negatives, reference limits) | https://docs.bfl.ai/guides/prompting_guide_flux2 | Accessed 2026-09-23 |
| M8 | BFL: Kontext image editing (text replacement syntax) | https://docs.bfl.ai/kontext/kontext_image_editing | Known through search results only; not fetched directly |
| M9 | Midjourney V8 alpha notes | https://updates.midjourney.com/v8-alpha/ | 2026-03-17 |
| M10 | ByteDance Seed: Seedream 4.0 | https://seed.bytedance.com/en/seedream4_0 | 2025-09 |
| M11 | ByteDance Seed: Seedream 4.5 | https://seed.bytedance.com/en/seedream4_5 | ~2025-12, per secondary sources |

### Platforms and typography technology

| Key | Source | URL | Date |
|---|---|---|---|
| P1 | YouTube Help: custom thumbnails (16:9, 3840×2160 recommended, minimum width 640, JPG/PNG, 2 MB on mobile) | https://support.google.com/youtube/answer/72431 | Accessed 2026-09-23 |
| P2 | LinkedIn Help: Page cover image 1512×256, PNG/JPEG ≤ 3 MB | https://www.linkedin.com/help/linkedin/answer/a563309 | Accessed 2026-09-23 |
| P3 | W3C Bengali Gap Analysis (letter-spacing splits conjuncts #117; stray spaces #118; `::first-letter` #94; underline clearance #90; grapheme clusters #87; numerals #91) | https://www.w3.org/TR/beng-gap/ | Draft note 2025-05-31 |
| P4 | Chromium Blink fonts README (HarfBuzz shaping; per-character fallback) | https://chromium.googlesource.com/chromium/src/+/main/third_party/blink/renderer/platform/fonts/README.md | Accessed 2026-09-23 |
| P5 | Pillow ImageFont docs (Raqm needed for complex scripts) | https://pillow.readthedocs.io/en/stable/reference/ImageFont.html | Accessed 2026-09-23 |
| P6 | google/fonts repository `METADATA.pb` for each family (subsets, weights, axes) | https://github.com/google/fonts/tree/main/ofl | Checked via `gh api` 2026-09-23 |
| P7 | Tesseract `tessdata_best` (`ben.traineddata`, `script/Bengali.traineddata`) | https://github.com/tesseract-ocr/tessdata_best | Checked 2026-09-23 |
| P8 | Unicode CompositionExclusions.txt (09DC, 09DD, 09DF) and Python `unicodedata` check | https://www.unicode.org/Public/UCD/latest/ucd/CompositionExclusions.txt | Checked 2026-09-23 |
| P9 | WCAG 2.2 SC 1.4.3 Contrast (Minimum): 4.5:1, or 3:1 for large text | https://www.w3.org/TR/WCAG22/#contrast-minimum | W3C Recommendation 2023-10-05 (not re-fetched) |
