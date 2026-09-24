# GPT Image Mastery: Master Skill Set (Top-1% Playbook)

**Ki:** OpenAI GPT Image (`gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`, `gpt-image-2`) diye **professional, ultra-natural, photoreal** image generate + edit + update korar puro skill set: ekjon AI agent ba manush jeno top-1% level-er output dite pare.
**Date:** 2026-09-23 · **Language:** Banglish explanation + English prompt template (image model English-e best kaj kore) · **Project:** `nexa-media`
**Companion:** `GPT-Image-Generation-Deep-Research-Report.md` (API parameter, pricing, Codex internals-er full reference).

> **Ei doc kivabe banano:** Codex `imagegen` skill-er protita file-er audit + OpenAI-er official prompting guide (24 example) + 4-ta cookbook + `openai/plugins`-er shob image skill + 17-ta community skill deep-read (ranking shoho) + 4-ta prompt library-r 1,150 prompt-er analysis + editing/QA research. Kono paid API call kora hoy nai. ✅ = official, ⚠️ = community/unverified.

## Kivabe use korbe

- **Manush:** Section 0 (rules) → 4 (framework) → 5 (realism) → 8 (genre template) → 12 (loop). Edit korle 9; series-e 10; ship korar age 11.
- **AI agent:** `codex-imagegen` skill-er `SKILL.md`-i operating core (flag/field: `references/cli.md`). §15-er drop-in skill **install korbe na**: seta purono, API-engine-bhittik; §0-er model/quality/size routing shudhu `--engine api`-er jonno.
- **Prompt:** protita template English-e; copy kore `<…>` fill koro.

## Suchipotro

0. Golden Rules (20)
1. Mastery model: 8 pillar
2. Research finding: official skill, `imagegen` audit, community ranking, conflict resolve
3. Model + parameter cheat sheet
4. Master Prompt Framework
5. Photorealism mastery: "AI-generated kintu AI-er moto na"
6. Photography reference
7. Text, typography + layout
8. Genre playbook (15 category)
9. Editing mastery
10. Consistency system
11. QA + evaluation
12. The Director's Loop
13. Production pipeline
14. Cost + latency
15. Agent SOP + drop-in `SKILL.md`
16. Safety, ethics, IP, provenance
17. Ranking: top 25 technique + official resource
18. Mastery path + drill
19. Reference

---

## 0. Golden Rules: top-1% image-er 20 commandment

1. **Brief age, prompt pore.** Intent, deliverable (size/format/kothay), must-have, "done" mane ki: age thik koro.
2. **Model explicitly choose koro:** draft = Flare, final/edit/text/identity = Sunburst, bulk = gpt-image-2 Batch. 1.x kokhono na.
3. **Quality explicit, `auto` na;** `xhigh`/`max` shudhu ekta named gap fix korte.
4. **Size valid rakho** (16-er multiple, ≤3840, ≤3:1, pixel range): 1920×1080 invalid → 1920×1088 + crop.
5. **Labeled brief likho;** Constraints kokhono khali na; specific prompt-e shudhu normalize, generic-e shudhu framing/use/layout add.
6. **Photo = capture condition, adjective na:** device/lens feel + angle + ekta motivated light + texture + located imperfection + exact count.
7. **Hype word delete:** 8K, masterpiece, ultra-detailed, flawless, sharp focus, Unreal/Octane.
8. **Ekta light source-er source + direction + quality + color** bolo: "cinematic lighting" na.
9. **Exact count dao** (manush/object): extra object ar cloned face kome.
10. **Text verbatim quote-e, koto bar, font, placement;** character-by-character proofread; guarantee lagle text/logo/data composite koro.
11. **Edit = "change ONLY X" + preserve list;** ek round-e ek change.
12. **Edit target first input;** face/product first; protita reference-er role + ki nibe/ki nibe na.
13. **Chain ≤2;** tarpor original ba approved composite theke.
14. **Pixel-exact region = composite-back**: prompt-er upor bhorsa na.
15. **Identity lock choto + dridho;** generated image identity reference na.
16. **Transparent = native alpha + backdrop-word-free prompt + code-e alpha verify.**
17. **Explore 3–4 alada direction,** same prompt re-roll na.
18. **Generation-er age acceptance likho; gate first, grade second; verdict code-e.**
19. **200% zoom QA + physics trace + hand-object trace:** hand, text, catchlight, shadow, halo, skin, color cast, na-chawa element; protita pour/splash/reflection/shadow-er source → path → target, ar protita haat → object-er kon ongsho (ashole ache to?) → grip → ojon kothay (5.3d).
20. **Provenance rakho, deceive koro na:** C2PA/SynthID strip na; real person, fake claim, onner brand: na.

---

## 1. Mastery model: 8 pillar

| # | Pillar | Ki jante hobe | Section |
|---|---|---|---|
| 1 | **Model + parameter control** | Sunburst/Flare/2 routing, quality ladder, size rule, format, background, cost | 3, 14 |
| 2 | **Brief + prompt engineering** | Labeled framework, specificity policy, power phrase, bad→good rewrite | 4 |
| 3 | **Photographic direction** | Light setup, lens, aperture, film/device look, composition, color temp, material | 6 |
| 4 | **Realism + anti-AI-look** | AI tell → countermeasure, myth vs reality, realism pattern block | 5 |
| 5 | **Typography + layout** | Exact text protocol, layout contract, text QA | 7 |
| 6 | **Editing + compositing** | Mask polarity, composite-back, identity/product lock, outpaint, upscale | 9 |
| 7 | **Consistency system** | Brand DNA, Campaign Style Lock, character anchor, canonical base | 10 |
| 8 | **QA, pipeline + ethics** | Rubric, judge, OCR diff, best-of-N, regression, post, provenance, legal | 11, 13, 16 |

Level ladder (L1 Operator → L5 Director + QA engineer → Top 1%) ar practice drill: Section 18.

---

## 2. Research finding: official, audit, community

### 2.1 OpenAI-er official skill / asset: ki ache, ki nai

**Direct uttor: OpenAI-er alada kono "image *prompting*" skill nai.** Evidence: `openai/plugins` (full tree + code search: `imagegen` 15 file, `image_gen` 9, `gpt-image` **0**), `openai/skills` (1,030 path; `.system` = imagegen, openai-docs, plugin-creator, skill-creator, skill-installer; `.curated`-e image skill shudhu `hatch-pet`), `openai/codex` bundled sample. Prompting guidance shob somoy **workflow skill-er bhitore embedded**.

Official je jaygay prompting shekhay:
1. Codex `imagegen` skill → `references/prompting.md` + `sample-prompts.md`
2. developers.openai.com **Image prompting guide (GPT Image 2.5)**: 24-ta official example (settings shoho)
3. Cookbook: *GPT Image Generation Models Prompting Guide* (2026-04-21), *gpt-image-1.5 Prompting Guide* (2025-12-16), *Generate Transparent Image Assets* (2026-08-20, 2.5 Flare use kore), *Image Evals* (2026-01-29)
4. Plugin-er bhitore domain scaffold (niche)

#### Official image-related skill inventory (openai/plugins HEAD `1dc1958`, 2026-09-11)

| Plugin / skill | Kaj | Value | Sobcheye boro technique |
|---|---|---|---|
| `creative-production` v0.1.25 (intake, produce, 8 mode ref, 4 contract, 5 JSON prompt pack, MCP review board) | Marketing creative generate/remix/edit | ⭐ Core | **Exact content contract:** image shudhu *treatment* (background, material, light, composition) dey; **text, data, logo, safe zone deterministic-vabe composite** hoy |
| `product-design` v0.1.52 (`ideate`, `image-to-code`, `url-to-code`, `design-qa`) | UI concept, asset, fidelity QA | ⭐ Core | **Exactly 3 independent call**, protita alada axis vary; `design-qa` P0–P3 severity gate (P0–P2 thakle fail) |
| `build-web-apps/frontend-app-builder` + `imagegen-website-concepts.md` | Website/app concept brief + asset pass | ⭐ Core | **Protita section-er jonno fresh, readable image**; purono concept crop kore spec banano nishedh; ≥5-point fidelity ledger |
| `build-web-data-visualization` v0.1.21 (**notun paowa**) | Data-viz concept + substrate | Useful | **"Generic AI atmosphere" reject** (bokeh, orb, wispy ribbon, stock haze); 7-category rubric, ship ≥28/35, kono category <4 na |
| `game-studio/sprite-pipeline` | Sprite strip | Core | **Ek edit call-e puro strip** (frame-by-frame drift kore) → deterministic normalize |
| `openai/skills .curated/hatch-pet` (deprecated repo) | Codex pet atlas | Best consistency pipeline | Canonical base anchor, invisible layout-guide PNG, auto chroma-key, deterministic QA threshold |
| Partner (Adobe, Higgsfield, Canva, Figma…) | Nijer model/tool | Kichu pattern | Adobe: design sobsomoy reference image hishebe; 1 pilot → approval → baki |

**Staleness note:** product-design `image-to-code` bole "Image Gen transparency pare na", sprite-pipeline/hatch-pet chroma-key era-r; egulo 2026-08-10 (Codex native transparency) ar 2.5 launch-er age lekha. Transparent cookbook (2026-08-20) 2.5 Flare/Sunburst-e `background="transparent"` confirm kore.

#### Deep dive: ja shekhar moto

**creative-production**
- 4-ta contract: (1) *Source preservation*: invariant list (identity, silhouette, proportion, material, color, logo placement, approved text), shudhu chawa dimension vary; (2) *Exact content*: text/data/logo deterministic composite; (3) *Image-building*: first-pass visual raster hote hobe (SVG/Pillow/HTML "fake ad" na), base visual → exact layer upore; (4) *Deterministic export*: manifest + provenance.
- **Default 4–6 alada direction**; protita tile ek-ta clean asset (collage/contact sheet/moodboard-er bhitore moodboard na); sparse brief-e safe default, kintu **claim, price, certification, endorsement, readable copy kokhono banano na**.
- **Prompt assembly order** (ek line = ek field): task + family → subject anchor + preserve fact → "stay on this subject, no other brand/category" → scene / format / human presence / rendering mode / channel / subject slot → focus + **"Decision being supported"** → template (placeholder = brief-er pointer, invented value na) → copy rule → route (style/composition/lighting) → constraint + "keep text sparse, use placeholder blocks" → avoid + global avoid (fake endorsement, misspelled large text, watermark, other brand).
- **Shot explorer (13 angle):** overhead, three-quarter, side, wide, tight, pan, zoom, macro, low hero + 1 surprise; protita edit prompt = source image + camera instruction + preserve list + "no new readable text/claim/logo".
- **Remix 6 slot:** style, palette, scene, props, character, format: "change this slot toward X, keep the focus recognizable".
- **Annotation edit:** user image-e point click kore note → normalized 0–1 coordinate (top-left) + preview + source prompt model-e jay.
- **Decision card** protita option-e: rationale, best_for, watch_out, next_step, next_prompt_hints.
- License: Proprietary → idea adapt koro, pack copy na.

**product-design `ideate`**
- Minimum brief (target + user outcome) age play back.
- Reference nam dekhe na, **image khule dekhe**; access na pele thamo; ja attach hoy nai sheta attached bole dabi na.
- Dimension protita prompt-e: mobile 390×844, tablet 834×1194, desktop 1440×1024, landing 1440 wide.
- UI prompt rule: ek hero use case + ek primary action; crammed lagle UI **komao**; separation order spacing/type → divider → tint → border → shadow (sesh-e); card-er bhitore card na; body 14–16px, ≤65 char/line, ≤2 font; mobile-e bezel/status bar na; mock data real date-e anchor.
- `design-qa`: source + implementation **ek combined comparison input**-e, same viewport/state/theme; full view + zoomed region; 5 surface (typography, spacing, color, image/asset fidelity, copy) + "AI shortcut artifact" flag.

**frontend-app-builder**
- Brief: scope, audience, exact visible content (accept-er por copy lock), structure/state, visual system, negative (header-only crop, fake metric, default card grid, hero eyebrow/pill, pasted-looking image na).
- **1 fresh large image per major section**; dense area-r jonno detail image; accepted concept-er por asset pass (logo, product, packaging, signage transparent cutout).

**build-web-data-visualization**
- Asset brief: role (concept / key frame / data mark / substrate / texture), image ki explain korbe vs data layer ki add korbe, label-safe region, mobile crop, transparency, locked vs flexible.
- Raster-e number, axis, logo, source note bake na (explicitly na chaile); misleading scale / invented factual object na.
- Paired large-screen + mobile-portrait concept → approval → semantic design contract.

**sprite-pipeline + hatch-pet (consistency engineering)**
- Ek approved seed/canonical base → protita porer job-e attach.
- Ek edit call-e puro row/strip; layout-guide PNG second input ("do not draw the guide").
- Normalize: equal slot split → alpha bbox → **ek global scale** → bottom-center align → frame-01 lock.
- hatch-pet deterministic QA: key color-er distance-150-er moddhe >800 pixel = error; edge-e >24 pixel = warning; frame area median-er 0.35×–2.75×-er baire = warning; transparent pixel-e **RGB residue flag**.
- Repair smallest scope: frame → row → atlas; max 2 attempt; transport error-e compressed retry prompt.
- Chroma-key auto-select: magenta/cyan/yellow/blue/orange/green theke subject-er color theke sobcheye dure (1st percentile distance) key.

**Partner pattern (Adobe tooling)**
- Design sobsomoy reference image hishebe, text-e describe na.
- 1 pilot mockup → approval → baki (≤5 per turn).
- Reference image thakle ratio prompt wording-e dao.
- Full set-er age 3-ta test crop (protita aspect family theke ekta).
- Generative edit shudhu background-e, **manush-er upor kokhono na**.

### 2.2 Codex `imagegen` skill: pro-level audit (SKILL.md + 5 reference + 2 script)

Tumi je 5-ta supporting doc diyecho (`cli.md`, `image-api.md`, `codex-network.md`, `prompting.md`, `sample-prompts.md`), shobgulo + SKILL.md + `image_gen.py` + `remove_chroma_key.py` line-by-line pora hoyeche. Verdict: **operational dik theke khub strong skill, kintu "craft" (top-1% image quality) dik theke durbol.** Eta ekta bhalo *driver*: kivabe tool chalate hoy shekhay; kintu *art director* na, kivabe world-class image banate hoy shekhay na.

#### Scorecard (0–5)

| Dimension | Score | Kaaron |
|---|---|---|
| Mode architecture (built-in vs CLI) | **5** | Clear separation, cost/API-key guardrail, silent downgrade nishedh |
| Asset handling / save policy | **5** | `$CODEX_HOME`-e project asset rakha nishedh, versioned sibling nam, `--force` chara overwrite na |
| Prompt structure | **4** | Labeled schema + 19-ta use-case slug; kintu Camera / Light / Material alada field nai |
| Augmentation (specificity) policy | **5** | Allowed vs not-allowed list: agent-er "extra jinish add kora" bondho kore |
| Photorealism depth | **2** | Ekta line: "photorealistic + real texture": light, lens, AI-tell, imperfection guide nai |
| Editing depth | **3** | Invariant repeat + image role label bhalo; mask banano, composite-back, first-image rule, chain-degradation nai |
| Text / typography | **3** | Quote + spell basic ache; layout grid, hierarchy, text QA nai |
| QA / evaluation | **1** | "Inspect outputs and validate": kono rubric, zoom check, score, pass/fail nai |
| Variant / exploration strategy | **2** | Single-change iteration ache; explore→converge, best-of-N nai |
| Model currency | **2** | 2.5 (sunburst/flare) nai; transparency info purono; CLI `xhigh`/`max` + 2.5 custom size block kore |
| Production pipeline | **2** | Shudhu downscale; exact deliverable crop, color, compression guide nai |
| Cost / latency awareness | **2** | "draft-e low" chara kichu nai; Codex limit 3–5× khay: bola nai |
| Safety / IP / provenance | **2** | Sample-e "no trademarks"; real-person likeness, disclosure, C2PA guidance nai |
| **Total** | **38 / 65** | Solid operator, weak craftsman |

#### File-by-file

| File | Bhalo dik | Gap / purono |
|---|---|---|
| `SKILL.md` | Decision tree (intent × execution), taxonomy, shared schema, save-path precedence, transparent-first built-in rule | Built-in-e size nai: prompt-e ratio lekhar technique bola nai; `view_image`-first advice `referenced_image_paths` asar age-er; QA step generic |
| `references/prompting.md` | Structure order, specificity policy, invariants, text rule, image role, iterate-deliberately, per-use-case tips | Light/lens vocabulary nai; AI-tell list nai; bad-vs-good example nai; genre depth kom |
| `references/sample-prompts.md` | 11 generate + 8 edit recipe + website/game/wireframe/logo template: coverage bhalo | "Keno kaj kore" annotation nai; recipe-wise model/quality/size recommendation nai; realism-tuned na |
| `references/cli.md` | Complete flag reference, batch JSONL, recipe | 2.5-aware na; retry shudhu batch-e; streaming nai |
| `references/image-api.md` | gpt-image-2 size rule accurate | **Stale:** gpt-image-2 transparency 2026-08-20 theke preview; 2.5 model + `xhigh`/`max` nai |
| `references/codex-network.md` | Approval vs network difference clear | Environment-specific; theek ache |
| `scripts/image_gen.py` | Validation, dry-run, async batch (≤500 job, concurrency 1–25), retry/backoff, downscale, no-overwrite | 2.5 → legacy size + quality reject; single call-e retry nai; `input_fidelity` 2.5-e block kore na |
| `scripts/remove_chroma_key.py` | Soft matte, despill, edge contract/feather, auto key sample: pro-grade alpha tool | Native transparency (2.5)-er cheye edge (chul/glass) durbol hote pare |

#### Ei master doc skill-er kon gap puron kore

| Gap | Puron kore je section |
|---|---|
| Photorealism / AI-look bhanga | 5, 6 |
| Camera/Light/Material field shoho framework | 4 |
| Genre-wise template + parameter | 8 |
| Editing mastery (mask, composite-back, identity) | 9 |
| Consistency (brand DNA, character anchor) | 10 |
| QA rubric + vision-judge | 11 |
| Explore→converge loop | 12 |
| Production (crop/color/format) | 13 |
| Cost/latency | 14 |
| Model currency (2.5) | 3 |
| Safety/IP/provenance | 16 |
| Agent-ready SOP + drop-in skill | 15 |

### 2.3 Community skill ranking: 17-ta deep-read + ~25-ta scan

Star/last-push 2026-09-23-e `gh api` diye. Score 0–5: **Craft** = prompt-craft depth, **Real** = realism guidance, **Edit** = editing support, **2.5** = model currency, **QA** = QA/iteration loop, **Maint** = maintenance/traction, **Safe** = safety/ToS.

| # | Skill | ★ | Last push | Craft | Real | Edit | 2.5 | QA | Maint | Safe | **Total /35** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [wuyoscar/GPT-Image2-Skill](https://github.com/wuyoscar/GPT-Image2-Skill) | 5,518 | 09-09 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | **34** |
| 2 | [buluslan/gpt-image2-ecommerce](https://github.com/buluslan/gpt-image2-ecommerce) | 389 | 09-17 | 4 | 5 | 5 | 5 | 5 | 3 | 4 | **31** |
| 3 | [smixs/visual-skills](https://github.com/smixs/visual-skills) (`image`) | 427 | 09-16 | 5 | 5 | 4 | 5 | 3 | 3 | 5 | **30** |
| 4 | [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | 6,143 | 09-21 | 3 | 1 | 3 | 5 | 5 | 5 | 4 | **26** |
| 5 | [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) `gpt-image-2` | 12,580 | 07-12 | 5 | 3 | 4 | 1 | 2 | 4 | 4 | **23** |
| 6 | [op7418/guizang-yingzao-skill](https://github.com/op7418/guizang-yingzao-skill) | 454 | 09-03 | 4 | 3 | 4 | 1 | 4 | 3 | 4 | **23** |
| 7 | [JimLiu/baoyu-skills](https://github.com/JimLiu/baoyu-skills) | 26,106 | 09-10 | 4 | 2 | 2 | 4 | 3 | 5 | 2 | **22** |
| 8 | [higgsfield-ai/skills](https://github.com/higgsfield-ai/skills) | 1,096 | 09-14 | 3 | 3 | 3 | 1 | 4 | 4 | 3 | **21** |
| 9 | [AlekseiUL/gpt-image-2-5-agent-kit](https://github.com/AlekseiUL/gpt-image-2-5-agent-kit) | 24 | 09-09 | 3 | 2 | 5 | 5 | 4 | 1 | 1 | **21** |
| 10 | [shinpr/mcp-image](https://github.com/shinpr/mcp-image) | 166 | 09-10 | 3 | 2 | 2 | 5 | 1 | 2 | 5 | **20** |
| 11 | [Wangnov/gpt-image-2-skill](https://github.com/Wangnov/gpt-image-2-skill) | 143 | 09-21 | 2 | 1 | 3 | 4 | 5 | 2 | 2 | **19** |
| 12 | jezweb `ai-image-generator` | 1,024 (repo) | 04-22 | 3 | 3 | 2 | 1 | 3 | 2 | 5 | **19** |
| 13 | [JuneYaooo/gpt-image2-ppt-skills](https://github.com/JuneYaooo/gpt-image2-ppt-skills) | 1,304 | 08-22 | 3 | 1 | 4 | 1 | 4 | 3 | 2 | **18** |
| 14 | freestylefly `gpt-image-2-style-library` | 33,304 (repo) | 09-11 | 3 | 2 | 1 | 2 | 1 | 4 | 3 | **16** |
| 15 | feiskyer `gpt-image-skill` | 1,653 (repo) | 07-12 | 1 | 1 | 2 | 1 | 1 | 2 | 5 | **13** |
| 16 | YouMind `ai-image-prompts-skill` | 1,120 | 09-23 | 2 | 1 | 0 | 1 | 1 | 4 | 3 | **12** |
| 17 | UzenUPoZiTiV4ik/gpt-image-2-skill | 440 | 05-01 | 2 | 3 | 0 | 1 | 0 | 2 | 3 | **11** |

#### Top skill gulo theke ki shikhlam

| Skill | Sobcheye mulloban idea | Risk / shaboddhan |
|---|---|---|
| **#1 wuyoscar** | Model-choice gate (Flare/Sunburst/Image 2 ekbar jiggesh; fake `gpt-image-2.5` ID pathay na); "smallest slice" reference load; **acceptance criteria generation-er age**; public evidence ledger (real defect: wrong shadow direction, invented "NO SUGAR" copy, 3-er jaygay 2-tola building); 18-rule craft (canvas/layout subject-er age, 5–12 concrete scene noun, diagram grammar, "three glances" poster test); reverse-prompt skill | CLI default ekhono `gpt-image-2`, `moderation` default `low`; README 227 KB (load koro na) |
| **#2 buluslan** | **Campaign Style Lock** (10 field, verbatim prepend); 5-slot prompt; category "visual key" (beauty = skin texture, electronics = brushed metal + hard light, food = moisture/steam/side light, jewelry = sparkle); slop-word blacklist + positive replacement; **8 AI-tell vision check** + counter-prompt; 3 bar text fail → text-free base + design tool; compliance red line (C2PA strip na, AI disclosure evade na) | Self-promo line; relay-first; "asymmetry"-ke flaw bole (nijer advice-er ulto); Flare > Image 2 claim unofficial |
| **#3 smixs `de-slop.md`** | Model-er "beauty default" table (eye, symmetry, pore-free skin, idealized body, notun-tight clothes, glossy hair, model pose, influencer casting, tidy saturated background) → protita deviation **dui bar** (slot-e + `EYES:`/`SKIN:` labeled Constraint line); ≥3 imperfection with location; capture pipeline "fact" hishebe; `medium` unretouched look-e `high`-er cheye bhalo hote pare; re-roll same prompt = same default | Execution/QA nai; unverified claim (16 ref); CC-BY attribution |
| **#4 codex-ppt** | Gate chain: outline → style (2–3 option) → **1 representative sample approve** → per-slide JSON job, identical method; blocker report kore, quietly quality komay na | Slide text editable na; heavy orchestration |
| **#5 garden-skills** | 80+ JSON template: when to use / not, must-ask vs default vs randomizable field; category auto-fill | 2.5 nai; July theke stale; celebrity/real photo option (likeness risk) |
| **#6 yingzao** | Photo preflight (exposure, sharpness, roll, empty space) → hero/support/reject; **typeset guide image** reference hishebe; deterministic `fit_canvas` crop/pad | Niche; Image 2 only |
| **#7 baoyu** | Reference eka under-weighted → MUST/REQUIRED bullet text-eo; hex = guidance, text na; series-e image 1 = anchor; **short identity lock** (lomba description → lookalike); generated image identity ref na; flawed text-e paint-over na, regenerate | Sensitive/copyright figure refuse na korar instruction; `codex exec --sandbox danger-full-access` provider |
| **#9 AlekseiUL** | Dry-run default (prompt + setting review); typed reference role (identity: pose/clothes/background na nibe); mask validation; **receipt: requested vs actual** (1536×864 chaile 1672×941) | Unofficial ChatGPT/Codex backend token |
| **#11 Wangnov** | Best transparency pipeline: flat matte → **auto-sampled** matte color → local alpha; `dual` black/white for glass/glow; `verify --strict` (alpha range, halo, residue, fake checkerboard, margin) | `~/.codex/auth.json` reuse (ToS gray) |

#### ❌ Adopt koro na

- `basketikun/chatgpt2api`, `yukkcat/chatgpt2api`: reverse-engineered ChatGPT + pooled account.
- `leeguooooo/image-use`: logged-in browser + Cloudflare bot-check bypass driver.
- ChatGPT/Codex login token reuse kora backend (god-tibo-imagen, codex-gpt-image, AlekseiUL/Wangnov-er Codex path): ToS gray zone, shudhu opt-in.

### 2.4 Conflict resolve: community vs official (ei doc-er final decision)

| Conflict | Decision |
|---|---|
| ALL CAPS text (buluslan) vs quote + typography (official) | **Quote verbatim**; caps shudhu jokhon design-e caps chai |
| Positive-only phrasing (shinpr, Higgsfield) vs Constraints/avoid (official, wuyoscar, smixs) | Slot-gulo positive; **choto, targeted exclusion shudhu Constraints-e** |
| Portrait-e `medium` (smixs: kom retouched look) vs `high` (identity fidelity) | OpenAI default dey na → **A/B test**, rubric diye decide |
| Prompt length (Higgsfield <200 token) vs long labeled spec | 2.5-e long labeled spec OK: **adjective kato, fact na** |
| "Flare > Image 2" | ❌ Official: Flare ≈ Image 2; Sunburst > Image 2 |
| "16 reference image" 2.5-e | ⚠️ Undocumented → 2–4 curated reference |
| `input_fidelity` 2.5-e | ⚠️ Param table-e nai → omit |
| "photorealistic" koto bar | Ekbar, medium-er statement hishebe |

---

## 3. Model + parameter control: ek pata-e cheat sheet

> Detail + source: `GPT-Image-Generation-Deep-Research-Report.md` (Section 2–13). Ekhane shudhu decision-er jonno ja lage.

### 3.1 Model choose korar niyom

| Situation | Model | Keno |
|---|---|---|
| Notun workflow, speed priority, everyday asset | `gpt-image-2.5-flare` | Fast; quality ≈ GPT Image 2 |
| Hero asset, dense text, face/identity edit, product label, complex composite | `gpt-image-2.5-sunburst` | Base model, highest quality + edit precision |
| Hazar image, deadline nai, cost-sensitive | `gpt-image-2` + **Batch API** | 50% discount (2.5 Batch-e nai) |
| Codex-e kaj korte korte asset, API key nai | Codex built-in `image_gen` (gpt-image-2) | ChatGPT plan; size/quality control nai |
| `gpt-image-1`, `1.5`, `1-mini`, `chatgpt-image-latest` | ❌ use koro na | 2026-10-23 / 2026-12-01-e shutdown |

**OpenAI-er official decision rule:** age Sunburst diye quality requirement pass koraw → tarpor same prompt/input Flare-e test koro → Flare-o pass korle ar latency komle Flare-e switch. Quality label (`high` etc.) duita model-e same image quality ba same speed mane na.

### 3.2 Quality ladder (draft → final)

| Stage | Quality | Model | Kaj |
|---|---|---|---|
| Explore (3–6 direction) | `low` | flare | Composition, idea, color direction choose |
| Refine | `medium` | flare / sunburst | Selected direction polish |
| Final (normal) | `high` | sunburst ba flare | Deliverable |
| Hero / print / dense text | `xhigh` → `max` | sunburst | Shudhu jokhon `high` fail kore ar latency budget ache |

Rule: **"higher setting ≠ always better"**; `xhigh`/`max` tokhoni jokhon ekta unmet quality requirement fix kore. `auto` production-e na (cost unpredictable).

### 3.3 Size (gpt-image-2 / 2.5)

- `WxH`: duita edge 16-er multiple · max edge 3840 · ratio ≤ 3:1 · 655,360–8,294,400 px · >2560×1440 experimental.
- Common deliverable → valid generation size → crop:

| Deliverable | Generate | Crop/resize to |
|---|---|---|
| Instagram 1:1 | `1024x1024` / `1536x1536` / `1920x1920` | 1080×1080 |
| Instagram 4:5 | `1088x1360` / `1536x1920` | 1080×1350 |
| Story/Reel 9:16 | `1088x1920` / `1440x2560` | 1080×1920 |
| YouTube / web hero 16:9 | `1920x1088` / `2560x1440` | 1920×1080 / 2560×1440 |
| Print-ish 3:2 | `2304x1536` / `3072x2048`* | as needed |
| Banner 21:9 | `2800x1200` / `3360x1440`* | as needed |
| 4K | `3840x2160`* | none |

`*` experimental. Codex built-in-e size nai → prompt-e ratio lekho ("wide 16:9 landscape") → pore crop.

### 3.4 Onno parameter: ek line-e

- `output_format`: master = `png`; web = `webp` (+`output_compression` 80–85); speed = `jpeg`. PNG-e compression na.
- `background`: `transparent` → png/webp + prompt-e "isolated subject… no backdrop/checkerboard/shadow"; **prompt flag-ke override kore**.
- `moderation`: default `auto`; `low` shudhu legit creative need-e.
- `n`: ek prompt-er variant (explore stage-e 2–4); alada asset = alada prompt.
- `partial_images`: shudhu live-preview UI-te (+100 token each).
- `input_fidelity`: 2 / 2.5-e **pathio na**.
- Edit-e face/identity image **prothom** input hishebe dao (first image-e sobcheye rich detail preserve hoy).

---

## 4. Master Prompt Framework: labeled brief system (I-S-S-C-L-M-M-T-X-O)

Top-1% prompt = **art director-er brief**, keyword-er list na. OpenAI-er official guidance (structure + goal, visible details, constraints, iterate) ar community best-practice mile ei framework:

### 4.1 Field order (mnemonic: **I-S-S-C-L-M-M-T-X-O**)

| # | Field | Ki likhbe | Keno lage |
|---|---|---|---|
| 1 | **Intent** (Use case + Asset type) | "Premium e-commerce hero photo for a website banner" | Model-er "mode" ar polish level set kore |
| 2 | **Scene** | Location, time, environment, props, background | Context = realism |
| 3 | **Subject** | Ke/ki, exact count, pose, action, gaze, relative scale | Proportion + action geometry |
| 4 | **Camera** | Shot type, angle, lens feel, DoF, medium ("real photograph", "35mm film", "phone photo") | Photographic look (physically simulate kore na: look steer kore) |
| 5 | **Light** | Source + direction + quality + color temp ("soft window light from left, overcast, 5600K feel") | Realism-er 50% light |
| 6 | **Material/texture** | Skin pores, fabric weave, brushed metal, condensation, wood grain | AI "plastic look" bhange |
| 7 | **Mood/color** | Palette, grade ("natural color balance, muted, not oversaturated") | Tone control |
| 8 | **Text (verbatim)** | Exact copy in quotes + font style + placement + "appears exactly once" | Typography accuracy |
| 9 | **Constraints / Exclusions** | Must keep / must avoid / "no extra text, no watermark, no logos" | Drift + junk bondho |
| 10 | **Output intent** | Aspect/orientation, negative space for copy, safe zones, transparent | Layout-ready asset |

> Motion/action thakle (pour, splash, throw) Subject-er pore **Action mechanics** line dao: source → path → target (Section 5.3c).
> Haat kichu dhorle/tulle/dhalle **Object anatomy** (handle ache ki nei, spout, neck, base, ojon) + **Grip & load** (kon haat kon ongshe, grip type, ojon kothay, load cue) line dao: haat frame position diye bolo (Section 5.3d).

Parameter (`size`, `quality`, `background`, format) **prompt-er baire API-te** dao: OpenAI bole "Set API parameters separately from the prompt".

### 4.2 Universal template (copy-paste, English prompt)

```text
Intent: <what this image is for, e.g. "hero image for a premium skincare landing page">
Scene: <place, time of day, environment, background elements>
Subject: <who/what, exact count, pose, action, gaze, scale relative to scene>
Action mechanics: <only if something moves: what moves, where it starts, its path, where it ends>
Object anatomy: <only if hands hold or use something: handle or "no handle", spout, neck, rim, base, material, weight when full>
Grip & load: <which hand (by frame position) touches which existing part, grip type, which hand or surface carries the weight, visible strain>
Camera: <real photograph | 35mm film photo | phone photo>, <shot type + angle>, <lens feel e.g. 50mm natural perspective>, <depth of field>
Light: <source + direction + quality + color temperature>
Materials & texture: <specific real-world textures and imperfections>
Color & mood: <palette + grading, e.g. "natural color balance, soft contrast, not oversaturated">
Text (verbatim): "<exact copy>", <font style, size, color, placement>; render exactly once
Constraints: <must keep>; no extra text; no watermark; no logos/trademarks unless provided
Output: <orientation/aspect, negative space location, transparent background yes/no>
```

Shudhu je field-e information ache sheta rakho: empty field bad dao (skill-er "specificity policy").

### 4.3 Prompt length + style rule

1. **Specific detail > adjective pile.** "weathered hands with visible knuckle creases" > "ultra detailed hyperrealistic 8k".
2. **Visible jinish describe koro, abstract mood na.** "rain-soaked asphalt reflecting red neon, light mist" > "moody atmosphere".
3. **Ek prompt = ek image-er idea.** Onek alada asset = alada prompt.
4. **Positive description first, exclusion shesh-e.** "No X" list choto + concrete rakho.
5. **Skimmable labeled line** production-e best: debug kora shohoj (OpenAI: "prioritize a skimmable template over clever prompt syntax").
6. **Generic prompt-e tasteful augmentation, specific prompt-e shudhu normalize**: extra character/brand/slogan nijer theke add koro na.

### 4.4 Specificity policy (agent-er jonno: Codex skill theke adopt kora)

- Allowed augmentation: composition/framing cue, intended-use polish level, practical layout guidance, plausible scene concreteness.
- **Not allowed:** unrequested character/object, brand name/slogan/palette/story beat, arbitrary left/right placement (layout support na korle).
- Critical detail missing hole (exact text, brand color, product reference) → **jiggesh koro**; noile reasonable default niye egao.

### 4.5 Bhalo vs kharap prompt: example

❌ Weak:
```text
beautiful woman drinking coffee in cafe, hyperrealistic, 8k, masterpiece, cinematic lighting
```
✅ Pro:
```text
Intent: candid lifestyle photo for a neighborhood café's Instagram feed.
Scene: small café by a rain-streaked window on a grey weekday morning; half-empty tables, a coat over a chair back.
Subject: a woman in her early 30s, oversized knit sweater, holding a ceramic cup with both hands, looking out the window, not at the camera.
Camera: real photograph, eye-level medium shot, 50mm natural perspective, shallow depth of field.
Light: soft overcast daylight from the window on the left, gentle falloff into the room, slightly cool daylight with warm interior practicals.
Materials & texture: visible skin texture and fine flyaway hairs, knit fibers, steam rising from the cup, water droplets on the glass.
Color & mood: natural color balance, muted tones, quiet and unposed.
Constraints: no text, no logos, no watermark, no heavy retouching.
```
Keno bhalo: specific light source, candid gaze, real texture, "unposed", adjective spam nai.

### 4.6 Power phrase library (GPT Image-e kaj kore emon bhasha)

| Goal | Phrase |
|---|---|
| Photoreal mode on | "photorealistic", "real photograph", "taken on a real camera", "professional photography", "iPhone photo" |
| Candid | "candid, unposed, captured in the moment", "not looking at the camera", "mid-action" |
| Real texture | "visible pores and fine skin texture", "fabric weave and wrinkles", "worn edges", "fingerprints on glass", "subtle imperfections" |
| No over-polish | "no glamorization, no heavy retouching", "not overly enhanced or cinematic" |
| Film look | "35mm film photograph, subtle film grain, natural color balance" |
| Grounded realism | "grounded, authentic, unstyled, as if captured in a real moment", "avoid cinematic lighting and dramatic color grading" |
| Layout-ready | "clean negative space on the left for headline", "subject centered with generous padding" |
| Text accuracy | 'Text (EXACT, verbatim, no extra characters): "…"', "render exactly once, perfectly legible" |
| Edit lock | "change only X; keep everything else exactly the same", "preserve identity, pose, lighting, camera angle" |
| Transparent | "isolated on a fully transparent background, clean alpha edges, no backdrop, no checkerboard, no shadow" |

> Note: "8k", "masterpiece", "trending on artstation" type tag GPT Image-e dorkar nai; egulo purono diffusion-model habit; specific visual description beshi kaj kore.

---

## 5. Photorealism mastery: "AI-generated, kintu AI-er moto dekhay na"

> **Boundary:** ei section shudhu *photographic craft*. C2PA/SynthID remove kora, metadata strip kora, AI-detector evade kora: egulo out of scope (policy-violating, deceptive use-e lage). Goal: real camera-r moto *believable* image, manush-ke thokano na (Section 16).

### 5.1 Data ki bole: 1,150-ta popular prompt analysis

Research agent 4-ta top prompt library (freestylefly/awesome-gpt-image-2: 544, EvoLinkAI: 463, YouMind: 120, ZeroLu: ~70) theke **1,150 unique prompt** parse koreche; 634-ta photo-type prompt-e term frequency:

| Term | Photo prompt-e koto % | Realism-e effect |
|---|---|---|
| "cinematic" | 46% | Often AI/poster look aney |
| "editorial" | 31% | Polish barae |
| "photorealistic" | 30% | ✅ Official photo-mode trigger |
| "ultra/hyper-realistic" | 30% | ⚠️ Hype |
| "8K" | 24% | ❌ Myth: fake look-er dike thele |
| "ultra-detailed" | 20% | ❌ Myth / over-sharpen |
| "film grain" | 18% | ✅ Moderate |
| "skin texture" | 18% | ✅ |
| focal length (mm) | 14% | ✅ Look cue |
| "imperfect" | 9% | ✅✅ Rare kintu powerful |
| "candid" | 8% | ✅✅ |
| iPhone/smartphone | 7% | ✅✅ Strong |
| exact counts | 5% | ✅✅ Extra object kome |
| motion blur | 5% | ✅✅ |
| window light | 3.5% | ✅✅ |
| direct flash | 3% | ✅✅ |

**Insight:** popular library-r beshirbhag prompt **hype word** diye bhora. Je minority prompt **"chobi-ta kivabe tola hoyeche"** (device, light source, handheld, imperfection) describe kore: segulo-i sobcheye real dekhay. Top 1% ei minority-r moto likhe.

### 5.2 The Realism Formula: 7 ingredient (+1 minus)

```
REAL = Mode word
     + Capture conditions (device/lens feel, angle, handheld/tripod, framing)
     + ONE motivated light (source + direction + color cast)
     + Material texture scaled to camera distance
     + 1–2 specific imperfections (with a cause)
     + Exact inventory (counts of people/objects)
     + Plain-language exclusions (anti-polish, anti-render, no extras)
     − Hype words (8K, masterpiece, ultra-detailed, flawless, Unreal/Octane)
```

Example (sob ingredient shoho):
```text
Photorealistic candid photo, taken on a phone at arm's length, slightly tilted, subject off-center.
A man in his 50s repairing a bicycle chain on a narrow balcony in the evening, looking down at his greasy hands, not at the camera.
Single warm bulb above the door as the only light, cool blue dusk sky behind him, mixed color temperature.
Grease on his fingertips, frayed cuff on a faded flannel shirt, pores and stubble visible at this distance.
Exactly one person, one bicycle upside down, two tools on the floor.
A strand of hair falling on his forehead, a little motion blur on the spinning wheel, faint noise in the shadows.
Natural, slightly muted color. No retouching, no studio lighting, no cinematic grading, not a 3D render, no text, no watermark.
```

### 5.3 AI tell → countermeasure (master table)

| AI tell | Prompt countermeasure | Workflow / post fix |
|---|---|---|
| Waxy / plastic skin | Pores, peach fuzz, redness nak-gal-e, uneven tone, named light-e subsurface scattering; "no retouching, no beauty filter, no smoothing"; **"flawless", "porcelain", "perfect skin" delete** | Close-up = `high`+, ≥2K, Sunburst; edit-e original face composite back |
| Etched / over-sharpened micro-texture (**2.5-er trait**) | "pores visible only where light rakes across", "soft natural micro-contrast", "no over-sharpening", detail camera distance onujayi | Edit chain koro na; post-e extra sharpen na |
| Perfect symmetry | Head tilt, uneven shoulders, off-center subject | Re-crop |
| HDR glow, halo, over-saturation | "natural dynamic range, a few clipped highlights, shadows allowed to go dark, no HDR; natural slightly muted color" | Gentle curve; clarity/HDR boost na |
| Yellow / sepia cast | "neutral white balance; daylight/overcast"; "golden, vintage, cinematic" shudhu intentionally | Post-e white balance correct (ekmatro reliable fix) |
| Flat uniform studio light | Ekta motivated source + direction + falloff + color cast | n/a |
| Generic creamy bokeh | Moderate DoF; background recognizable; phone deep focus | n/a |
| Too-clean environment | 3-ta specific lived-in detail, wear, clutter | n/a |
| Stock pose, lens-e hashi | Mid-action verb; chokh kono object-e; "unaware of the camera" | n/a |
| Dead / glassy eyes | Named source theke catchlight; eye white-e halka redness; clear gaze target | Close-up-e `high` |
| Malformed hands | Grip + object name koro; hand kom rakho ar kaj-e busy rakho | Inspect; masked local edit-e fix |
| Garbled text | Exact text quote, koto bar, typography; "no other text"; background sign out of focus | `medium`/`high`; proofread |
| Cloned faces, repeated texture | Exact count; "each person different age/build/outfit"; dense crowd eriye cholo (≤5 prominent face) | Fresh session |
| Always centered | Subject rule-of-thirds-e; foreground obstruction; UGC-te halka tilt | Re-crop |
| Subject "pasted in" | "consistent light and shadow between subject and background, same color temperature, contact shadow" | n/a |
| Floating object | Contact shadow; weight dekhao ("cushion compressing") | n/a |
| Uniform CG noise | "photographic noise in the shadows only" | Fresh session; generated image abar reference-e dio na |

### 5.3b "Beauty default" override (smixs `de-slop` method: community-r sobcheye bhalo realism doc)

Model-er ekta **default "sundor" look** ache; tumi ja bolo na, model sheta-i banay. Default theke protita deviation **dui jaygay** bolo, nijer slot-e measurable bhabe, ar Constraints-e labeled line hishebe:

| Model-er default | Override (example) |
|---|---|
| Boro, symmetric, bright eye | `EYES: slightly asymmetric, natural size, one eyelid a bit heavier` |
| Pore-free glossy skin | `SKIN: visible pores, faint acne scar on left cheek, uneven redness` |
| Idealized body / model pose | `BODY: average build, relaxed slouch, weight on one leg` |
| Notun, tight, spotless clothes | `CLOTHES: washed-out cotton tee, slightly stretched collar, lint` |
| Glossy perfect hair | `HAIR: flyaways, a few strands stuck to the forehead` |
| Influencer casting | `CASTING: ordinary office worker, not a model` |
| Tidy saturated background | `BACKGROUND: cluttered desk, muted colors, a coffee ring on the table` |

- **≥3 imperfection, protita-r location shoho.** Capture pipeline "fact" hishebe bolo (frame grab / 35mm scan / phone / mirrorless) + oi pipeline-er artifact.
- "No sharpening, low micro-contrast, natural grading; no HDR, bloom or glow."
- Unretouched look-er jonno `medium` vs `high` A/B koro (`high` kokhono texture beshi sharp kore retouched lagay).
- Miss hole same prompt re-roll na: kon variable under-specified sheta khujo; re-roll default-i ferot dey.

### 5.3c Physics + causality audit: "dekhte thik, logic bhul"

**Real case (ei project-e dhora pora):** `output/imagegen/sample-test-tea-stall.png`-e cha-r dhara steel mug-er **gaa/tola theke beroche**, mug prai shoja dhora, kinara (rim) theke na. Haat, texture, light sob thik chilo, tai prothom QA-te dhora poreni. Model *pattern* aake, *physics* hishab kore na, tai je kono **motion ba cause→effect** (dhala, chitka, pratibimba, chaya) sobcheye beshi bhul hoy.

| Physics tell | Ki check korbe | Prompt countermeasure |
|---|---|---|
| **Liquid pour source bhul** | Dhara spout/rim-er shobcheye nichu bindu theke beroy kina; container heleche kina; dhara top-bottom connected kina | "tilt the <container> ~45°; liquid leaves ONLY over the tilted rim at its lowest point; one continuous stream; ends inside the <target>; nothing flows from the side or bottom" |
| Container-e liquid surface helano | Glass/cup helleo liquid surface **horizontal** thake | "liquid surface stays level with the horizon" |
| Splash direction | Splash impact point theke uporer dike/baire chhoray | "splash rises from the impact point, droplets falling back" |
| Reflection mismatch | Ayna/pani/glass-e object-er sathe mile, ulto thik | "reflection in the water mirrors the boat exactly, inverted" |
| Shadow mismatch | Shob chaya ek light-er dike, length consistent | "all shadows fall away from the <light>, same direction" |
| Gravity / support | Kichu bhashche na; jinish kono surface-e boshe ache | "resting on the table with a contact shadow" |
| Tool use | Tool surface-e contact korche (knife-bread, pen-paper) | "knife blade pressed into the crust" |
| Steam / smoke direction | Shob steam ek hawa-r dike | "steam drifts gently to the right in a light breeze" |
| Rope / cable / chain continuity | Shuru theke shesh connected | "one continuous cable from the plug to the lamp" |
| Mechanical object | Bicycle chain, rickshaw wheel/axle, door hinge plausible | "bicycle chain loops around both sprockets" |
| Fire / flame | Flame fuel/burner-e attached, upore uthche | "flame rises from the burner ring" |
| Scale / perspective | Dure manush choto, vanishing line consistent | "people shrink naturally with distance" |

**Kivabe prompt korbe: "Action mechanics" line** (motion thakle Subject-er pore):
```text
Action mechanics: <source> is <position/tilt>; <substance> leaves from <exact exit point>, travels <path> under gravity,
and ends <target>; the flow is continuous and connected at both ends; nothing comes from <wrong places>.
```

**Strategy:**
1. Action jodi dorkari na hoy → **static moment** bachai (cup already bhora, steam uthche): kinetic moment beshi fail kore.
2. Action dorkar hole → mechanics line + `high` quality + Sunburst-e test (instruction following beshi).
3. **QA-te physics trace:** protita moving element-er source → path → target angul diye follow koro (200% zoom).
4. Fail hole → **T16 PHYSICS FIX** edit (Section 9.15), pour area mask kore, tarpor composite back.

### 5.3d Hand-object affordance, grip + load: "haat ki dhorche, kivabe dhorche, ojon kothay"

**Real case (ei project-e dhora pora):** `output/imagegen/skill-test-pour.png`: handle-chara mati-r kolshi theke glass-e pani dhala. Pour-er physics trace thik chilo, tai physics gate pass korechilo, kintu hand-object logic 3 jaygay bhul:
1. Uporer haat kolshi-r gola-kana (neck + rim) **handle-er moto hook grip-e** dhoreche: kolshi jeno oi haat theke jhulche. Kolshi-te handle nei, tai eta **phantom handle**.
2. Model kolshi-ke pitcher/jug-er sathe mishiye rim-e **pinched spout** banieche: **hybrid object** (rare object common object-er anatomy pay).
3. Nicher haat shudhu angul-er dogay pet chhuye ache; bhora kolshi (~10–15 kg) tar **kono load cue nei**: palm chapa nei, kobji bak nei, forearm-e tension nei, shorir pichone helano nei. Kolshi shorir theke dure dhora (lomba moment arm), ja ei ojone ashombhob.

> Shikkha: **physics gate ≠ hand-object gate.** Pour thik holeo haat bhul hote pare, tai hand-object alada gate (`hand_object`) ar alada trace.

**Skill update-er por same scene:** `output/imagegen/kolshi-retest.png`: handle-chara round kolshi, spout nei. Uporer haat kolshi-r kadhe flat (steer + tilt), nicher haat + forearm pet-er niche (ojon), kolshi komor/hip-e theka, pani rim-er shobcheye nichu bindu theke glass-e. Brief-e shudhu duita line jog kora hoyechilo: **Object anatomy** + **Grip & load**.

**Keno hoy:** Model "pouring" shunle training data-r shobcheye common pattern ane (handle-wala pitcher + handle grip). Haat aake "pose template" hishebe, bol/torque hishab kore na. Rare object (kolshi, lota, boti) common object-er (jug, cup, knife) anatomy ar dhorar dhong pay.

**Research data (2026-09):**
- **Qwen-Image-Bench (May 2026, 18 model):** GPT Image 2 overall #1. Tobu shob model-er best score-o Contact Interaction 43.3/100, Physical Logic 31.9, Anatomical Fidelity 20.9. Flare/Sunburst-er kono published hand-object eval nei. Mane grip prompt-e likhe dite hobe, ar QA-te check korte hobe.
- **Commonsense-T2I:** DALL·E 3 48.92%. GPT diye prompt rewrite korleo thik hoy na: shudhu "bhalo prompt" jothesto na.
- **Vocabulary trap:** Bangladeshi English-e kolshi-ke prai "pitcher" bola hoy. Model-er kache pitcher = handle-wala jug, tai phantom handle ashe. Kolshi-r jonno **"pitcher / jug / jar" kokhono likhbe na**: "kolshi" likho ar anatomy describe koro.
- **Negation priming:** "no X" likhle model kokhono ulto X-i aake (arXiv 2404.15154). Tai age positive description ("round belly, short neck, rolled rim"), negation shudhu ek line-e.
- **Edit persistence:** object bodlale edit model purono grip rekhe dey (HOI-Swap). Tai protita hand edit-e grip abar puro likho.
- **Biomechanics:**
  - Shobcheye shokto grip hoy prai 35° wrist extension-e.
  - Bhora kolshi shudhu gola dhore helale wrist-e ~6–15 N·m torque pore, ar prapto-boyoshko nari-r max wrist-flexion torque ~8 N·m. Tai neck-only pour = shorboshokti-r kaj, relaxed pose na.
  - Thik pose: palm + forearm pet-er niche ojon ney, onno haat shudhu steer kore (angul rim-er pichon dike, dhalar dik-er ulto pashe).
- **Taxonomy gap:** Feix GRASP taxonomy (33 type) bimanual ar gravity-dependent grip (hook, flat hand/platform) baad dey; thik oi grip-gulo-i bhari patro-r jonno lage. Tai prompt-e egulo shobde likhe dite hoy.
- **Reference:** kolshi theke dhalar exact grip kono written source-e nei; ashol kolshi-r reference photo (`--ref`) diye check koro.

#### A. Affordance: haat shudhu ashol, dhorar-jonno-banano ongshe

Object-er shape-i bole kothay dhora jay (Gibson-er *affordance*, Norman-er *Design of Everyday Things*). Rule:
- Haat shudhu oi ongshe jeta **real object-e ache** ar **dhorar jonno baniye**: handle, bail (bucket-er tar), rim, neck, body, base, lid knob.
- Handle na thakle **handle-er moto grip na**: neck-e angul jodiye jhulano na, rim-e hook kora na.
- Object-er anatomy brief-e **nijei likho**; model-ke guess korte dio na: "no handle, no spout" explicitly.
- Tool-er working end target-er dike: chhuri-r dhar niche, kolom-er nib kagoje, chhata-r canopy upore, boti-r blade upore (Section D).

#### B. Grip taxonomy: prompt-er bhasha (Napier 1956; Cutkosky 1989; Feix et al. GRASP 2016)

| Grip | Kokhon | Prompt phrase |
|---|---|---|
| Cylindrical power grip | Handle, bar, tool handle, sturdy bottle | "fingers wrapped fully around the handle, thumb closing over them" |
| Hook grip | Bucket bail, bag strap, suitcase handle | "four fingers hooked through the wire handle, thumb relaxed, arm hanging straight" |
| Spherical grip | Ball, fruit, choto round pot | "fingers spread around the fruit, fingertips on its curve" |
| **Cradle / platform** (palm support) | Handle-chara bhari pot, tray, baby, stack of plates | "palm and spread fingers flat under the base, carrying the weight" |
| Precision pinch / tripod | Cup handle, pen, lobon-er chimti | "handle pinched between thumb and index finger" |
| Lateral pinch | Chabi, card, plate-er kinara | "held between the thumb and the side of the index finger" |
| Hug / two-arm carry | Boro basket, bosta (sack), bhora kolshi | "both arms wrapped around it, pressed against her chest" |
| Hip / head carry (South Asia) | Kolshi, jhuri, bosta | "resting on her hip, her arm wrapped around its neck" / "balanced on her head on a coiled cloth ring, one hand steadying the rim" |

#### C. Load: ojon-er proman chobi-te dekhate hobe

Pani = **1 kg/L**. Majhari kolshi (8–12 L) bhora thakle mati soho **~10–15 kg**. Tai ojon-er class age thik koro, tarpor dhorar dhong:

| Weight class | Example | Kivabe dhore | Visible cue (prompt-e likho) |
|---|---|---|---|
| Light (<0.5 kg) | Cup, phone, kolom, glass | Ek haat, precision ba halka wrap | Relaxed angul, soja kobji |
| Medium (0.5–3 kg) | Kettle, pan, laptop, 2 L bottle | Handle-e ek haat-er power grip, ba dui haat | Firm wrap, forearm engaged, konui bhanga |
| **Heavy (3–15 kg)** | Bhora kolshi, pani-r balti, tel-bhora karahi, 10 kg chal-er bosta | Dui haat **ba** shorir-er support (hip, buk, table); **shorir-er kachhe** | Center of mass-er niche palm chhoranor sathe, angul chepe bosa (pad chapta), kobji pichone bak, forearm-e tendon, kadh shokto, shorir pichone helano / hip baire |
| Very heavy (>15 kg) | Gas cylinder, 25 kg bosta, pani-r drum | Pa + pith diye tola, kadh/matha-y, gorie ba tene | Hantu bhanga, pa chhoriye dara, mukh/gola-y strain |

**Moment arm:** torque = ojon × shorir theke durotto. Manush bhari jinish **shorir-er kachhe** dhore (NIOSH lifting equation-e horizontal distance-i boro multiplier). Bhari jinish haat-lomba durotte, halka angul-e = **WRONG**.

**Two-hand role split:** ek haat **bear** (center of mass-er niche, ojon ney), arek haat **steer** (rim/neck/upor-e, halka chhoa, dik thik kore). Handle-chara patro theke dhala: steer haat upor theke helay, bear haat pet/base-er niche pivot, rim-er shobcheye nichu bindu target-er dike.

**Contact realism:** angul surface-er curve onujayi beke thake; chaper jaygay angul-er pad chapta, chamra halka fyakashe; angul ar surface-er majhe contact shadow; naram jinish (bag, kapor, dough, fol) chape tube jay; faak (bhasa angul) nei, angul object-er bhitore dhuke jay na.

**Handedness:** model left/right prai gulie fele. Frame position diye bolo: "the hand nearer the camera", "the hand on the viewer's right". Anatomical left/right shudhu dorkar holei (jemon South Asia-y dan haate khawa/deya).

#### D. Cultural handling: Bangladesh / South Asia cheat sheet

| Object | Real use | AI-er common bhul |
|---|---|---|
| Kolshi (mati / pitol / aluminium) | Kankhe (hip-e): haat diye gola jodiye; matha-y binni (kapor-er ring)-er upor; dhalar somoy ek haat pet-er niche, arek haat kadh/kana-y, ba kolshi mati/stand-e rekhe helano | Pitcher handle grip, spout jog, ek haate jhulano |
| Lota | Pet ba gola dhore; nol (spout) thakle nol diye dhala | Cup-er moto handle |
| Boti | Mati-te boshe pa diye kather base chepe, blade upor-mukhi; maach/sobji dui haate blade-er dike tene kata | Chhuri-r moto haate tule dhora |
| Karahi | Dui pash-er loop handle, gorom hole kapor/gamchha diye | Pan-er moto ek lomba handle |
| Cha-er kettle (tong dokan) | Handle-e haat, gorom lid kapor diye chapa; dhara nol theke | Gaa theke dhara, handle chara dhora |
| Cycle rickshaw | 3 chaka (samne 1, pichone 2); puller samne seat-e boshe pedal kore, handlebar dhore | 2/4 chaka, puller pichone, sidecar |
| Bhat khawa | Dan haater angul diye | Chamoch, bam haat |
| Shil-pata | Shil (pathor-er slab)-er upor nora (roller) dui haate samne-pichone | Mortar-pestle-er moto thokano |
| Haatpakha | Datu (handle) dhore kobji ghuriye | n/a |
| Bodna (plastic) | Side handle + nol; toilet/wudu-r pani | Drinking glass-e dhala, khabar table-e rakha (**cultural bhul**) |
| Hari / patil (handle-chara ranna-r patro) | Sandashi (chimta) ba kapor diye tola | Khali haate gorom kinara dhora |
| Tubewell | Lever handle upor-niche pump | Handle ghurano, bhul jaygay nol |
| Matha-y kolshi | Bira (khor/doori-r ring)-er upor, ek haat kinara-y | Ring chara, dui haat chara bhasha |

#### E. Pose selection: model je pose bhalo aake sheta bachai

- Bhari jinish **surface-e theka** (table-er kinara, hip, mati): "tilted while its base stays on the table" haate-tola-r cheye beshi reliable.
- Dui haat-i dekha jay ar protita haat-er role sposhto: haat object-er pichone lukano pose-e model gulie fele.
- Haat-lomba durotte bhari jinish, ek haate bhari tola: avoid.
- Close-up hand-object shot-e sobcheye beshi scrutiny: extra detail dao.
- Rare object-er jonno **reference image** dao (`--ref kolshi.jpg=object-anatomy`): shobder cheye anatomy bhalo transfer hoy.

#### F. Prompt template + kolshi example

```text
Object anatomy: <object>, <shape>; <handle: none | one side handle | two loop handles | wire bail>; <spout: none | ...>;
<neck / rim>; <base>; <material>; <size>; <weight when full, about N kg>.
Grip & load: <hand A by frame position> <grip type> on <a part that exists> and <carries the weight | steers | steadies>;
<hand B> ...; the object is held <close to the body | resting on the hip | base on the table>; load cues: <fingers spread and
pressing into the surface, wrist bent back, forearm tense, elbow tucked in, torso leaning back slightly>.
```

```text
Object anatomy: one traditional round-bellied unglazed terracotta kolshi with a short narrow neck and a thick flared rim;
it has NO handle and NO spout; heavy when full.
Grip & load: she holds the kolshi close to her body with both hands; the hand on the viewer's right and its forearm cradle
the round belly from underneath and carry the weight (fingers spread and pressing into the clay, wrist bent back, forearm
tense); the other hand rests flat on the pot's shoulder near the rim to steady and tilt it, not wrapped around the neck;
her upper body leans back slightly to counterbalance.
```

#### G. QA: `hand_object` gate + load-path trace

Protita haat-er jonno ek line, tarpor protita bhari object-er load path:
```text
hand (viewer-right) -> kolshi belly underside (exists) -> cradle/platform -> bears weight; palm flat, fingers pressing = OK
hand (viewer-left)  -> kolshi neck + rim (exists) -> hook grip, pot hangs from it -> WRONG (phantom handle)
load: kolshi ~12 kg -> fingertips only, pot at arm's length, no counter-lean -> WRONG (no load support)
```
**FAIL hobe jodi:** phantom handle / na-thaka ongsho dhora; hybrid object (spout ba handle jog); bhasa angul ba angul object-er bhitore; ojon-er sathe grip type mile na; bhari object-e load cue nei ba shorir theke dure; tool ulto dhora; gorom surface khali haate; cultural mismatch; extra ba missing haat.

**Judge protocol (research theke):**
- Protita check-er jonno item-specific proshno koro. PhyBench-e GPT-4o human-er sathe mileche shudhu specific instruction dile.
- Age protita haat-er contact point ar load path describe koro, **tarpor** angul ek ek kore gono. Vision model count-e prior theke uttor dey: unusual count-e matro 17% (arXiv 2505.23941).
- Haat-er crop 2–4× zoom-e dekho.
- Second signal nao (HandEval ba 21-keypoint hand detector).
- Human-labeled set diye judge calibrate koro.
- Graded 0–5 (≥4 ship): strain cue, counter-lean + shorir-er kachhe dhora, grip-er naturalness, dui haater coordination.

**Fix:** T17 GRIP/LOAD FIX (Section 9.15) ba 12.3-er fix phrase; concept-i bhul hole (pose-tai ashombhob) regenerate with Object anatomy + Grip & load line.

### 5.3e Place, culture + manush: default global, context theke local

**Real case (ei project-e dhora pora, 2026-09-23):** "dental website banao", kono location bola hoyni. Tobu demo-r style lock-e "South Asian adults" ar brief-e "in Dhaka" boshe gechilo, karon requester Banglish-e likhchilen. Fole 5-ta photo-r shob manush South Asian, OG card-e "Family dentistry in Dhaka". Benchmark-er 10-ta brief-o shob Bangladesh-e set chilo. **Requester-er bhasha ≠ client-er audience.**

**Probe (same neutral brief, kono jayga-r naam nei; 2 dental + 2 street, duita timezone-e):** model South Asian dey na; dey **American default**. Dui dental-e white nari, dui street-e New York-er moto English signage ar US bus, ekta-y One World Trade Center-o. Codex protita session-e `<timezone>Asia/Dhaka</timezone>` pathay (rollout-e dekha). Kintu fast mode-e prompt hubohu jay, tai image-e tar prova pore ni (`TZ=UTC` run-o same). Mane bias duita: (1) orchestrator-er anuman, (2) model-er nijer US default. Global korte duitai thamate hoy.

**Decision order (project protite ekbar):**

| # | Signal | Udaharon |
|---|---|---|
| 1 | User-er request ba client-er detail | "Austin, Texas-er clinic" → `Austin, Texas, USA` |
| 2 | Existing site | `locale --root .` / `audit`: schema.org address, phone country code, postcode, currency, site-er nijer domain + email, `<html lang>`, `og:locale`, jayga-r naam |
| 3 | Brief nije jayga ba culture-er naam ney | "a street in Tokyo", "kolshi on her hip" |
| 4 | Kichui na | `global`: internationally neutral setting, varied cast |

**Kokhono signal na:** requester kon bhashay likhche (Bangla, Hindi, Spanish), machine-er timezone/region, agency-r desh, doc-er example scene, ager project-er jayga.

**Script ki kore:**
- `Locale:` line ashe job `"locale"` > jobs-file `"locale"` > `--locale` > style lock `"locale"` theke. Seta hoy rule: "architecture, interiors, vehicles, public signage, clothing and food fit this place today, and the cast reflects its real present-day population (often diverse)".
- Desh jana thakle real-world logic check jog hoy, judge-o verify kore: kon dike gari chole + steering kon pashe, public signage-er script, southern hemisphere-e December = gorom. 22-ta deshe gari bam dike chole: UK, IE, JP, IN, BD, PK, LK, NP, HK, SG, MY, ID, TH, AU, NZ, ZA, KE, TZ, UG, CY, MT, JM. Data: `scripts/locales.json` (77 desh).
- Jayga na thakle: neutral setting, varied cast, shob gari ek dike.
- **Global set-e cast rotation:** ekta image baki set dekhte pay na, tai "varied people" dileo pura batch ek chehara-y gie theme (validation v1-e 5-tar 5-tai ek dhoroner). Tai global batch-e jekhane manush ache, protita job-e main person-er background ghure: African → East Asian → European → Latin American → South Asian → Middle Eastern → Southeast Asian. Brief-e chehara bola thakle ba `"cast": false` dile skip hoy; `--no-auto-cast` puro run-e bondho kore. Ei line judge-er kache jay na: chehara kokhono defect na.
- Shop/street scene-e: "invented, generic names; no real brands" (v1-e London-e "Pret A Manger" ashchilo).
- **Named-place street scene-e manush ar sign "none" na, "distant, defocused, unreadable":** ashol rastay manush ar sign thake, tai "no people, no signs" likhle jayga-r shathe lorai hoy, ar model tobu ane (2026-09-23/24-er review-e 27-ta logged plate candidate-er 8-tay unrequested manush, sign ba prop). Brief-e likho: `People and shop signs only in the far background: distant, defocused, unreadable; no legible text anywhere.` Text-free plate-er jonno (codex-design Compose) eta-i niyom.
- Codex `TZ=UTC`-e chole (`CODEX_IMAGEGEN_TZ=system` dile machine-er timezone thake).

**Casting rule:** manush-ke role, boyosh ar ki korche diye describe koro; chehara tokhoni likho jokhon golpo-r jonno dorkar. Costume ba cliché diye jayga bujhano na. Named jayga-y cast = oi jaygar ashol population (London, Toronto, Dubai → diverse). Real team/doctor/patient photo client-er kach theke ashe.

**Validation v1 (2026-09-23, 13 job, 155 s, plan-er 1%):** 13/13 pass (11 PASS, 2 PASS_WITH_NOTES), shob first-pass. Ek-i hero brief 6 locale-e: Austin (Austin skyline), Munich (Frauenkirche), Tokyo (Skytree, Japanese cast), Lagos (Nigerian cast), Dubai (Burj Khalifa), Dhaka (Bangladeshi cast). London street: route 87 bus ar black cab bam dike, right-hand drive, "STRAND WC2" sign. Neutral street: landmark ar NYC cue chara. Dui dhoroner gap dhora porlo (ek-i chehara-r global set ar real brand signage); dutoi fix kora hoyeche (upore).

### 5.4 Myth vs reality (GPT Image specific)

| Claim | Verdict | Keno |
|---|---|---|
| "photorealistic" / "real photograph" / "iPhone photo" photo mode on kore | ✅ Official | OpenAI cookbook; kintu ekla na: capture condition shoho |
| Focal length + f-stop compression/DoF/framing steer kore | ✅ Loosely | OpenAI: look cue, physics na |
| Exact ISO/shutter number diye physically correct noise/blur | ❌ Myth | Same |
| Pro camera body nam (e.g. "A7R IV") beshi real kore | ⚠️ Weak: polished stock look aney | Hedra, gptimager |
| Everyday device (iPhone, disposable, 2003 digicam, CCD compact) | ✅✅ Strong | Protitar recognizable "look" ache |
| Film stock nam | ⚠️ Loosely palette/grain steer; Portra 400 / CineStill 800T overused → AI-read hote pare | Hedra |
| "8K", "masterpiece", "ultra-detailed" | ❌ Myth: fake look | OpenAI example-e nai |
| "Unreal / Octane / ray-traced" | ❌ Render look aney | n/a |
| Negative-prompt field / `(word:1.3)` weight | ❌ Support nai | Exclusion plain sentence-e lekho |
| JSON prompt prose-er cheye bhalo | ❌ Myth | OpenAI: format matter kore na |
| Higher quality = always better | ❌ Myth | OpenAI; VibeDex: gpt-image-2 `high` `medium`-ke 50-e 22-ta prompt-e hariyeche matro |
| Boro output size fine detail barae | ✅ | 4K `high`-e noticeably better (~$0.40) |
| Exact count extra object kome | ✅ Community | YouMind #109, freestylefly #532 |

### 5.5 Realism pattern library (copy-paste block)

**A. Authentic daily-life portrait chain** (sobcheye strong realism pattern)
```text
<Shot size>, authentic daily-life photo, natural candid moment.
<Specific anatomy: eye shape, nose bridge, skin undertone>.
Skin physics: subsurface scattering under the <named light>, tiny specular highlights on cheekbone and nose ridge, fine pores and faint blemishes.
Wearing <garment named by material: "washed cotton", "worn wool">.
Gaze on <object>, absorbed, unaware of the camera.
<Lived-in environment with one or two specific details at the edge of the frame>.
Two or three stray hairs moved by <cause: "the train's draft">, unplanned and asymmetric.
One motivated light: <source> with its own color cast.
ISO-400-style grain in the shadows only: photo noise, not CG smoothness.
Not a cartoon, painting, illustration or 3D render; no watermark; no text.
```

**B. UGC inventory** (real customer-post feel)
```text
Realistic vertical smartphone photo of a candid <moment> in <place>.
Exactly: <1 shopper, 1 basket, 2 background shoppers out of focus>.
Consumer phone look: imperfect framing, real <fluorescent/tungsten> light with its color cast, mild motion softness, neutral color.
Feels like a customer's social post, not a studio shoot.
No glamour lighting, no exaggerated poses, no artificial skin, no extra people.
```

**C. Raw documentary**
```text
Vertical phone photo, handheld, slightly top-down, raw unedited look.
<Physical state of material: "coffee spreading across the pavement, ice cubes scattered">, natural mess, shadows with a real direction including the photographer's own shadow.
No studio light, no over-clean ground, no over-composed frame, no floating objects, no poster feel.
```

**D. Screen photographed (screenshot na)**
```text
Photo of a laptop screen taken with a phone: visible subpixel grid, faint moiré bands, dust and a fingerprint smudge, uneven reflection of a window, slight perspective skew, handheld noise.
```

**E. Era-device look**
```text
Photo from <2003> shot on a <consumer point-and-shoot digital camera>: pop-up flash in daylight, a few blown highlights, slight chromatic aberration, mild JPEG blockiness, imperfect focus, accidental framing with an object partly blocking the view. Don't keep modern clarity.
```

**F. Anti-plastic block** (je kono portrait-er shesh-e jog koro)
```text
Natural skin: fine pores, faint blemishes, tonal variation, soft natural sheen; no plastic, waxy or over-smoothed skin; no beauty filter; not overly warm or over-filtered.
```

**G. Anti-render block** (product/interior/architecture)
```text
Real photograph, not a 3D render or CGI: physically plausible light falloff, contact shadows, slight dust and wear, real material imperfections.
```

**H. Anti-stock block** (lifestyle/people)
```text
Unposed and candid: relaxed asymmetric posture, gaze away from the lens, mid-action; everyday clutter in the background; no stock-photo smile, no staged look.
```

**I. Grounded-cinematic block** (dramatic scene-eo real rakha)
```text
It should look like a real photo someone could have taken, not an enhanced movie poster. Avoid cinematic lighting, dramatic color grading and stylized composition; keep natural light and realistic colors.
```

### 5.6 Model-wise realism note

| Model | Realism behavior | Tactic |
|---|---|---|
| **2.5 Sunburst** | Texture-heavy photoreal (portrait, product)-e best; edit-e region-er baire kom change; **kintu embellish kore** (na-chawa element add) | Final photoreal + edit-e use; exclusion list strict ("no additional elements, props or branding") |
| **2.5 Flare** | Formatting-e beshi faithful; flat/graphic style-e bhalo; draft-er jonno darun | Explore `medium`-e; final photoreal-e Sunburst-er sathe compare |
| **2.5 (dui-i)** | Close-up face-e fractal-like / etched micro-texture, synthetic eyebrow report; **protita edit pass-e image aro sharp, saturated, artificial** | Chained edit 2–3-er beshi na; original theke edit; composite back |
| **gpt-image-2** | `medium` ≈ `high` (VibeDex 50-prompt test: high jite 22/50); **`low` quality regression 2026-06 theke** (uncanny face, extra limb); tiling "grime" artifact same session-e 3rd–5th image theke barte pare; dense crowd-e fail; product edit-e "plastic face" (OpenAI: fix nai) | Default `medium`; `low` avoid for people; fresh session/stateless call; crowd kom; garment-only mask + face composite |
| **Shob model** | Warm cast "golden/vintage/cinematic" word-e ashe; text >95% accurate (small multilingual) kintu tiny UI glyph/legal copy-te vul | Post-e WB correct; protita text proofread |

### 5.7 Realism QA: 200% zoom checklist

☐ Hand/finger count + grip ☐ Text/sign spelling ☐ Catchlight light source-er sathe mile ☐ Shadow direction consistent ☐ Contact shadow ache ☐ Repeated/cloned face nai ☐ Chul-er edge-e halo nai ☐ Skin-e wax/etched texture nai ☐ Color cast (yellow/green) nai ☐ Background-e melted/garbled object nai ☐ Perspective/vertical line thik (architecture) ☐ Fabric/liquid physics believable ☐ **Physics trace:** protita pour/splash/reflection/shadow-er source → path → target thik (Section 5.3c) ☐ **Hand-object trace:** protita haat real ongsho dhoreche (phantom handle/spout nei), grip ojon-er sathe mile, bhari jinish-er center of mass-er niche haat/hip/surface ar load cue ache (Section 5.3d).

### 5.8 Agent-er jonno 5-ta realism rule

1. **Model:** draft = Flare `medium`; final photoreal + edit = Sunburst `high`; `xhigh`/`max` shudhu close-up face, macro product, dense text (≥2K).
2. **Prompt:** mode word + capture condition + 1 motivated light + texture + 1–2 imperfection (with cause) + exact count + plain exclusion; hype word bad.
3. **Edit:** sobsomoy approved original theke; 2–3 chained edit-er por thamo; unchanged region composite koro; hero image-er jonno fresh session.
4. **Post:** white balance, gentle curve, output size-e subtle grain; heavy sharpening na.
5. **QA:** 200% zoom (5.7 checklist).


### 5.9 Natural look system: "AI feel" komano, measured (2026-09-23)

**Real case:** user bollen chobi-gulo "AI generated feel" dey. 10-brief benchmark-e (dental, fisherman, UGC selfie, family dinner, office, taco stall, mug, living room, park, GP) chokh ar blind reviewer dekhlo je **AI tell mul-e stock-photo polish, skin kom:** shobai ek sathe hashche, catalogue-tidy color-matched set, glow-wala shoman alo + HDR balance, warm/orange grade, dead-centre/postcard framing. Purono judge era-o 4–5 realism dito.

**Research-er shar (source: SKILL review report-e link):**
- **OpenAI docs (GPT Image guide, 1.5 guide, 2.0/2.5 launch prompt):** camera spec "loosely" interpret hoy; kaj kore **chobi kivabe, kothay tola** + tar khut. Device-er dhoron (phone, disposable, point-and-shoot, film format) help kore; body/lens model number, ISO/shutter prai kichu kore na; film stock (Portra 400) look bodlay. "neutral white balance", "no retouching, no beauty filter, no HDR, no cinematic lighting, no colour grading". Mood shobdo (cinematic, dramatic, cozy, golden hour) polish ane.
- **Kamali et al., CHI 2025 (50,444 dorshok):** style artifact = waxy/glossy skin, photoshoot-level perfection, overly soft hair; candid group posed group-er cheye kom dhora pore; manush beshi dhore anatomy (61%), tarpor style (30%).
- **Community (Reddit/X/blog, beshirbhag anecdotal):** accidental snapshot, direct flash camera roll, disposable/early-digicam, film stock + ekta real alo kaj kore; quality booster (8K, masterpiece), **capture-flaw stack** (1–2-er beshi), contradictory spec (phone + 85mm bokeh), generative upscaler: ulto fol.
- **GPT Image quirk:** warm/yellow cast (post-correction shobcheye nirbhorjoggo); 2.5-e grain overdo-r report → grain prompt-e na chaiya post-e controlled.

**Manush ki dekhe AI bole (research, numbers papers theke):**

| Cue | Manush koto use kore | Ashole koto nirbhorjoggo | Prompt-e ki |
|---|---|---|---|
| Anatomy (haat, daant, pupil, kaan) | Shobcheye beshi: 61% comment (Kamali, 34,675) | Dekha gele decisive (finger error 84% dhora pore) | natural grip, irregular ashol daant |
| Skin smooth/waxy/glossy | Style cue 30% | Beshi use hoy kintu real vs AI alada korte pare na (Miller 2023): retouched real photo-o emon | pores, fine lines, uneven tone, matte skin |
| Studio polish (cinematic alo, beshi contrast/saturation) | Ek-i bucket | Ashol tendency: je fake-gulo dhora pore tader contrast/rong beshi; je fake thokay tara "realistic kintu professional na", flatter (Roca/Microsoft 2025, ~12,500 manush) | available light, muted rong, amateur framing |
| Object logic, lekha, logo | 21% | Shobcheye common flaw (Kamali-r annotated fake-er 58.7%) | lekha kom; strap, string, clasp check |
| Alo, shadow, reflection, catchlight | 15% | Mapa gele nirbhorjoggo; "alo odbhut" gut feeling nirbhorjoggo na (Farid) | ek motivated alo, dui chokhe mil-e catchlight |
| Background blur, pasted-on | Kom | Blur cue muche dey: AI portrait 16% "hardest 10%"-e | phone deep focus, real cluttered background |
| Face symmetry/attractive | Common | Symmetry/attractive AI-r dike point kore; average/familiar face "manush" lage | distinctive face, model face na |

- **Kamali et al., CHI 2025:** 50,444 manush, 749,828 judgement; AI chobi 76% dhora pore; portrait shobcheye kothin (72.7%); hand-picked chobi same prompt-er 84% chobir cheye bhalo.
- **Nightingale & Farid 2022:** StyleGAN2 face-e 48.2% accuracy; fake face beshi "trustworthy" (average face).

**Prompt vocabulary, ashol number (Apple spec, datasheet):**
- **iPhone (15/16/17 Pro):** main 24mm-eq f/1.78 (1/1.28" sensor) = full-frame-e prai f/6.3 → **deep DOF, creamy bokeh na**; 1.5 m-e subject 1.0–2.9 m sharp. Ultra-wide 13mm; tele 77mm (15 Pro), 120mm (16 Pro), 100mm (17 Pro). Smart HDR: shadow tola, highlight chapa, halka over-sharpen, kom alo-te watercolour noise reduction, grain nei. Selfie ~30 cm-e nak ~30% chowra. Portrait mode: kata edge, adha-blur chul.
- **Full-frame prime:** 85mm f/1.8 at 2 m → DOF ~5.7 cm; 50mm f/1.8 at 2 m → ~17 cm; 35mm f/8 at 3 m → 1.9–7.2 m. Genre: documentary 35mm f/5.6–8 ISO 800–3200; portrait 85mm f/1.8–2.8 window light; interior 16–24mm f/8–11 tripod; product 100mm macro f/8–16.
- **Film:** Portra 160/400 (smooth natural skin, fine grain), Ektar 100 (saturated, finest grain), Gold 200 (warm snapshot), Superia 400 (disposable-er film, cool green), HP5/Tri-X (B&W, push korle gritty), CineStill 800T (tungsten, lamp/neon-e red halation).
- **Direct flash / disposable:** inverse-square, tai dobol durotte deyal 2 stop kalo; flat uzzol mukh, kopale-nake hotspot, pichone kora shadow, prai kalo background, red-eye; QuickSnap 32mm f/10 fixed focus, flash 1–3 m.
- **Skin/chokh/daant:** ~6% alo skin-er upore colourless reflect; T-zone oil shine; pores 250–500 µm; peach fuzz backlight-e; sclera off-white, halka capillary, boyosh-e holdete; daant ivory, canine beshi holud, kinare translucent.
- **Ghorer alo:** daylight ~6500 K; ghorer bulb 2700–3000 K (warm); office tube/cheap LED-e halka green; "WB lamp-er jonno set → janala-r dik neel".

**System (script, automatic):**

| Layer | Ki kore |
|---|---|
| Capture profile (`look`) | Protita photo-y ekta "Capture:" line: editorial (full-frame, 35mm, f/2.8, available light, background halka soft kintu pora jay), portrait, phone (iPhone main camera, deep focus, phone HDR, halka tilt), phone-flash, film (Portra 400), product (tripod, f/8, shudhu bola props), interior (tilt-shift). Intent dekhe auto; brief-er focal length thake; brief camera bolle brief-i control kore |
| Realism check | People: skin texture, asymmetry, ashol daant, protyeke kichu korche, expression "in between", shobai hashbe na. Scene: keu ekhoni use koreche emon jinish, color-sorted na, unbranded/label ulto, falloff, postcard/landmark na. Product: true texture, chhoto khut, shudhu bola props. Raat: frame mostly dark, lifted shadow na |
| Photo rule | Unretouched, neutral WB, exposure subject-er upor (window clip korte pare), real DOF, muhurte beche neya framing |
| Judge | `ai_tells` list + realism rubric: 5 = unretouched camera photo, 3 = stock polish → FAIL → concrete fix diye regenerate |
| Finish | Judging-er pore, **halka**: shades-of-grey WB (near-neutral pixel, highlight protected, uzzolota ek), 0.3 px soften, luminance grain (bright deyal/akash-e kom), halka vignette, 3% kom saturation; profile natural / portrait (grain na) / phone / film (halation) / clean. Original C2PA soho `-raw.png`-e; finished ar web export-e IPTC `DigitalSourceType=trainedAlgorithmicMedia` (shudhu generated source-e, client photo-te na) |
| Lint | "no text" + menu/sign/screen/label brief-e thakle warning (lekha-wala jinish lekha ane) |

**Brief-er niyom:** emotion na, action ("she is mid-sentence explaining the X-ray; he listens with a small closed-mouth smile"); ashol mixed light; 1–2 lived-in unbranded detail; frame-e kichu kata; capture flaw 1–2; style lock palette photo-te shudhu accent.

**Measured (10 brief, blind reviewer, left/right random):**

| Tulona | Result |
|---|---|
| A (purono skill) vs B1 (shudhu script layer, brief same) | B1 8/10 (confidence-weighted 14 vs 2) |
| A vs B2 (notun brief + layer + finish) | **B2 10/10** (26 vs 0) |
| B2 vs B3 (layer v2: DOF shobdo, exposure/HDR, off-centre, unbranded) | B3 6/10 (10 vs 5) |
| Finish-er alada effect (ek-i image raw vs finish v2) | **Finish 8/10**, 1 tie (13 vs 1) |
| B3 vs B4 (kom detail-er brief + v3 finish: desat 0.94 + beshi grain) | B3 6/10; reviewer: "muted grainy grade looks applied" → finish halka kora holo (grain 4, midtone bias, sat 0.97) |
| Final halka finish (ek-i B4 image, raw vs finish) | **finish 7/10, raw 0, 3 tie** (13 vs 0) |
| Text leak fix (no-text brief-e sign fact bondho + sign/screen hint) | Taco FAIL → PASS; dental monitor-er bodole jaw model → PASS |
| Warm cast (midtone R−B) gor | A 30.3 → B1 24.7 → B2 12.5 → B3 13.4 |
| Saturation gor | 27.7% → 23.4% |

**Ekhono baki (model limit / next):** clutter kokhono "planted" lage; raater shot-e shadow tule dey; lekha-wala jinish-e lekha chole ashe; product-e model nijei styling props jog kore; dental equipment-e brand-er moto chinho.

**Shima:** camera shobdo shudhu prompt style; generated file-e fake EXIF (jemon "iPhone 15 Pro") kokhono na; AI detector ke fakifying adversarial noise na; `-raw.png` master-er C2PA kokhono muche fela na. Finish = dorshok-er jonno shadharon photo finishing.

---

## 6. Photography reference: agent-ke "photographer-er moto bhabte" shekhano

> GPT Image camera spec **physically simulate kore na**: egulo "look cue". Tobuo sothik photographic bhasha dile output real photo-r kachakachi jay, karon model real photo-r context theke shikheche.

### 6.1 Lighting setup

| Setup | Look | Prompt bhasha | Best for |
|---|---|---|---|
| Side window light | Soft directional, dhire dhire shadow | "soft window light from the left, gentle falloff into shadow" | Portrait, food, lifestyle |
| Overcast daylight | Shadow-less, muted, even | "overcast daylight, soft even light, no harsh shadows" | Fashion, street, exterior real estate |
| Golden hour | Warm, low sun, long shadow, rim glow | "late golden-hour sun behind the subject, warm rim light, long shadows" | Outdoor lifestyle, portrait |
| Blue hour | Cool sky + warm practical light | "blue hour, deep blue sky, warm interior lights glowing" | Architecture, city, hospitality |
| Hard midday sun | High contrast, crisp shadow | "harsh midday sun, crisp hard shadows, squinting" | Summer realism, editorial |
| Direct on-camera flash | Flat front light, hard shadow pichone | "direct on-camera flash, hard shadow behind, slightly blown highlights" | Party, candid, fashion editorial "real" feel |
| Softbox key + bounce fill | Clean studio | "large softbox key at 45° left, white bounce fill right" | Product, corporate headshot |
| Rim / backlight | Edge separation, chul-e halo | "subtle rim light outlining hair and shoulders" | Portrait, product edge |
| Rembrandt | Cheek-e triangle light, dramatic | "Rembrandt lighting, single key" | Character portrait |
| Butterfly | Beauty, nak-er niche shadow | "butterfly lighting from above camera" | Beauty, cosmetics |
| Practical / mixed | Lamp, neon, screen | "lit only by a warm desk lamp and the laptop screen glow" | Moody interior, night |
| Tungsten indoor | Warm orange | "warm tungsten lamplight" | Cozy home |
| Fluorescent office | Flat, halka green cast | "flat overhead fluorescent light" | Documentary, office realism |

**Rule:** protita light-er **source + direction + quality + color**, char-tai bolo. "Cinematic lighting" / "dramatic lighting" type vague word AI look aney.

### 6.2 Lens / focal length look

| Lens feel | Look | Use |
|---|---|---|
| 14–24mm ultra-wide | Boro space, edge-e stretch | Interior, architecture ("keep verticals straight") |
| 28–35mm | Environmental, documentary | Street, reportage, UGC |
| 50mm | Chokher moto natural perspective | Lifestyle, general |
| 85mm | Flattering compression, soft background | Portrait, headshot |
| 100mm macro | Extreme close detail | Jewelry, product detail, food texture |
| 135–200mm tele | Strong compression, isolated subject | Fashion, sports, dur theke candid |
| Phone main camera (~26mm) | Deep DoF, shob sharp, phone HDR | UGC authenticity |
| Anamorphic | 2.39:1, oval bokeh, horizontal flare | Cinematic still |

### 6.3 Aperture / shutter / ISO

| Setting | Effect | Prompt bhasha |
|---|---|---|
| f/1.4–2 | Khub shallow DoF | "shallow depth of field, background softly blurred": **overuse korle AI tell** |
| f/4–5.6 | Subject + context readable | "moderate depth of field, background recognizable" |
| f/8–11 | Shob sharp | "deep depth of field, everything in focus" (packshot, landscape, architecture) |
| Fast shutter | Motion freeze | "frozen mid-splash" |
| Slow shutter | Motion blur | "slight motion blur on passing pedestrians": **realism barate darun** |
| High ISO | Shadow-e grain | "slight high-ISO grain in the shadows" (low-light scene) |

### 6.4 Film / medium look (look cue hishebe)

| Look | Character |
|---|---|
| Kodak Portra 400 feel | Warm natural skin, soft contrast |
| Fuji 400H feel | Cool pastel green, airy |
| Kodak Ektar feel | Saturated, fine grain (landscape) |
| Tri-X / HP5 B&W | Visible grain, punchy contrast |
| CineStill 800T feel | Tungsten night, highlight-er chardike red halation |
| Instant / Polaroid | Soft, faded color, instant border |
| Disposable / point-and-shoot flash | Harsh flash, vignette, casual framing |

### 6.5 Composition

- Rule of thirds, leading lines, deliberate negative space (copy-r jonno).
- **Layering:** foreground–midground–background ("shot through a doorway", "blurred plant leaf in the foreground").
- **Natural crop:** frame-er edge-e kichu kata pora, real photo-r lokkhon; sobkichu perfectly centered + fully visible = AI/stock feel.
- Angle: eye-level (natural), high-angle (vulnerable/overview), low-angle (power), overhead flat lay (food/product), 3/4 view (product), over-the-shoulder (story).
- Symmetry shudhu architecture/interior-e intentional; portrait-e halka asymmetry real lage.

### 6.6 Color temperature + grading

| Kelvin | Source | Feel |
|---|---|---|
| 2700–3200K | Tungsten, candle | Warm, cozy |
| ~4000K | Neutral LED | Clean |
| 5500–6500K | Daylight | Natural |
| 7000K+ | Shade, overcast | Cool |

- **Mixed light = realism:** "cool daylight from the window mixing with warm lamp light".
- Grading bhasha: "natural color balance", "true-to-life color", "muted tones", "soft contrast", "lifted blacks" (film). **Eriye cholo:** "vibrant", "HDR", "ultra-saturated", "teal-and-orange grade" (jodi specific style na chao).

### 6.7 Material realism cue

| Material | Real-er lokkhon (prompt-e bolo) |
|---|---|
| Skin | Pores, fine vellus hair, uneven tone, halka redness nak/gal-e, freckle, T-zone-e natural oil sheen, under-eye texture, backlight-e subsurface glow |
| Hair | Individual strand, flyaway, frizz, natural parting |
| Fabric | Weave, pilling, joint-e wrinkle, seam stitching, lint |
| Metal | Brushed anisotropic highlight, fingerprint, micro-scratch, patina |
| Glass | Refraction, caustic, environment reflection, smudge, condensation |
| Liquid | Meniscus, bubble, condensation bead, drip |
| Food | Steam, crumb, glossy sauce, char mark, irregular cut |
| Wood / stone | Grain, knot, chip, dust, edge wear |
| Paper / print | Fiber, halka curl, ink bleed |
| Plastic | Mold line, scuff, sheen variation |

### 6.8 Legit post-processing (generation-er pore)

1. Deliverable size-e crop (Lanczos resize).
2. sRGB-te convert / embed.
3. Web-er jonno halka output sharpening.
4. Series-e same grade/LUT (consistency).
5. Format: master PNG → delivery WebP/JPEG.
6. **Out of scope / korbo na:** C2PA metadata strip kora ba SynthID watermark defeat korar chesta, ja policy-violating ar deceptive (Section 16).

---

## 7. Text, typography + layout mastery (poster, ad, infographic, slide, UI)

### 7.1 Exact text rule (shob somoy)

1. Copy **quote-e** dao; heading-e bolo `Text (EXACT, verbatim, no extra characters):`.
2. **Koto bar** ashbe bolo: "appears exactly once".
3. **Typography spec:** style (bold geometric sans / high-contrast serif / handwritten), weight, size relation ("headline large, subline 40% size"), color, alignment, kerning ("clean kerning").
4. **Placement:** "top third, centered", "bottom-left safe margin".
5. Brand/unusual word → letter-by-letter spell: `"Q-U-I-N-O-A"`.
6. "No extra text, no lorem ipsum, no random letters."
7. Choto/dense text → `high`/`xhigh`/`max`; Sunburst text rendering-e best (Arena text-rendering board #1).
8. **Output-e spelling character-by-character check**; ekta vul hole shudhu text fix-er edit: `Correct the headline to read exactly "…"; change nothing else.`

### 7.2 Layout direction

- Canvas + hierarchy age define: "16:9 slide; title top-left; chart right two-thirds; footnote bottom".
- Grid language: "12-column grid feel, consistent margins, generous whitespace".
- Real data dao (numbers, labels): model real-looking data banay na nijer theke thik moto.
- Infographic: audience + flow direction ("top-to-bottom flow with numbered steps"), label list verbatim.
- UI mockup: "describe the product as if it already exists"; real UI element, spacing, hierarchy; concept-art word na; device frame chaile bolo ("inside an iPhone frame").
- Slide/chart: "clear data hierarchy, readable labels, no clip art, no stock photo, no decorative gradients".

### 7.3 Text QA checklist

☐ Protita word spelling ☐ extra text nai ☐ copy ek bar-i ☐ font style match ☐ legible at target display size ☐ number/data source-er sathe mile ☐ line break/hyphenation thik.

---

## 8. Genre playbook: category-wise template

> Protita template-e `<…>` jaygay nijer detail bosao. Parameter recommendation `model / quality / size` format-e.

### 8.1 Product: studio packshot (e-commerce)
`sunburst / high / 1024x1024 ba 2048x2048`
```text
Intent: e-commerce packshot for <product> on a marketplace listing.
Subject: <exact product description: shape, material, color, label text>, single unit, three-quarter front view.
Scene: seamless light-grey studio sweep, nothing else in frame.
Camera: professional product photography, 85mm-like compression, everything in sharp focus (deep depth of field).
Light: large softbox key from upper left, white bounce fill from right, subtle rim light to separate edges; soft natural contact shadow.
Materials & texture: <e.g. matte frosted glass with crisp refraction, brushed aluminium cap with fine anisotropic highlights>.
Text (verbatim): label reads "<exact label>"; keep it legible and undistorted.
Constraints: preserve exact product geometry and label; no props; no extra text; no watermark.
```
Real product thakle **edit endpoint + product photo first input** (Section 9): generate kore "same product" ashe na.

### 8.2 Product: lifestyle / in-context
`sunburst ba flare / high / 1536x1024`
```text
Intent: lifestyle photo for <brand>'s product page showing <product> in real use.
Scene: <specific real place + time: "sunlit bathroom counter, morning, lived-in but tidy">.
Subject: <product> on <surface>, no other props unless the brief names them; <hand interacting if needed: "a hand reaching for it, natural nails">.
Camera: real photograph, eye-level, 50mm natural perspective, moderate depth of field (product sharp, background softly readable).
Light: <motivated source: "morning window light from the right, soft shadows">.
Materials & texture: <real micro-detail: water droplets, towel fibers, slight countertop scratches>.
Color & mood: neutral white balance, true-to-life colour.
Constraints: product label legible; no extra branding; no text; no watermark.
```

### 8.3 Portrait / people (realistic)
`sunburst / high / 1024x1536`
```text
Intent: <editorial / corporate headshot / lifestyle> portrait.
Subject: <age, look, clothing, expression, all specific and natural>, <pose + gaze>, <hands doing something natural>.
Scene: <real location with depth>.
Camera: real photograph, <85mm portrait look | 35mm environmental>, eye level, shallow depth of field.
Light: <e.g. "large window light 45° left, soft falloff, gentle catchlights">.
Texture: natural skin texture with visible pores, fine lines and slight tonal unevenness; individual hair strands and flyaways; fabric weave.
Mood: honest, relaxed, unposed.
Constraints: no beauty filter, no airbrushed skin, no heavy retouching; no text; no watermark.
```

### 8.4 Food
`sunburst / high / 1024x1280 (4:5)`
```text
Intent: food photo of <dish> for a menu page or social post.
Subject: <dish with exact components and plating>, <garnish>, <one bite taken / sauce drip for realism>.
Scene: <table surface + 1–2 props: linen napkin, cutlery with slight water spots>.
Camera: real food photography, 45° angle (or overhead flat lay), 100mm-like, shallow depth of field.
Light: soft side light from a window behind-left, gentle backlight highlighting steam and gloss.
Texture: crisp crust crumbs, glossy sauce, fresh herb veins, visible steam.
Color: appetizing natural color, not oversaturated.
Constraints: no text; no watermark; no artificial perfection.
```

### 8.5 Interior / real estate / architecture
`sunburst / high / 1536x1024 ba 2560x1440`
```text
Intent: <real-estate listing / architectural visualization> photo of <space>.
Scene: <room type, style, materials, furniture list, time of day>.
Camera: real architectural photograph, wide 24mm-like perspective, eye-level ~1.2 m, vertical lines kept straight (no keystone distortion).
Light: <natural daylight through windows + warm practical lamps>, balanced exposure, soft shadows.
Texture: <oak grain, linen weave, slight wear, a folded throw, a book left open>.
Mood: lived-in, inviting, not a sterile CGI render.
Constraints: no people; no text; no watermark.
```

### 8.6 Fashion / apparel
`sunburst / high / 1024x1536`
```text
Intent: <lookbook / e-commerce on-model> image for <garment>.
Subject: model wearing <garment with exact fabric, color, cut, details>, full body visible, feet included, natural stance.
Scene: <street / studio / location>.
Camera: fashion editorial photograph, 50–85mm look, eye level or slightly low.
Light: <soft daylight / clean studio key + fill>.
Texture: fabric drape, folds at elbows and waist, stitching, realistic fit.
Constraints: garment details exact; no extra logos; no text; no watermark.
```
Try-on (real person + garment photo) → Section 9 identity-lock edit.

### 8.7 UGC / phone-photo look (ad-e "real customer" feel)
`flare / medium–high / 1024x1536`
```text
Intent: user-generated style photo for a social ad.
Subject: <person/product in an everyday moment>.
Camera: casual iPhone photo, handheld, slightly imperfect framing, deep depth of field, natural phone HDR look.
Light: <available light: kitchen ceiling light / afternoon sun>, no studio lighting.
Texture: everyday clutter in background, real skin, slightly messy hair.
Mood: authentic, spontaneous, not staged.
Constraints: no text overlays; no watermark.
```
Ethics: real customer review hishebe present koro na; "fabricated testimonial" deceptive (Section 16).

### 8.8 Cinematic still / moody scene
`sunburst / high–xhigh / 2560x1088 (21:9)`
```text
Intent: cinematic film still for a <genre> concept.
Scene: <scale, weather, atmosphere concretely: "wet cobblestone alley at night, drizzle, steam from a vent">.
Subject: <action + blocking>.
Camera: anamorphic widescreen film still, low angle, subject off-center (rule of thirds).
Light: <motivated sources: "cold sodium streetlight + warm neon sign spill, haze catching light">.
Color: <specific palette>, realistic film grain.
Constraints: keep surface realism (skin, wet textures); don't trade detail for mood; no text; no watermark.
```

### 8.9 Ad / campaign with text
`sunburst / high / 1024x1536`
```text
Intent: campaign ad for <brand> targeting <audience>; brand position: <one line>.
Scene/Subject: <hero moment>.
Style: premium <fashion/tech/food> advertising photography.
Text (EXACT, verbatim): headline "<…>" (bold condensed sans, top third, centered); CTA "<…>" (small, bottom right). Each appears exactly once.
Layout: clean composition with deliberate negative space for text; strong color direction <palette>.
Constraints: no extra text; no unrelated logos; no watermark.
```

### 8.10 Infographic / diagram / slide
`sunburst / high / 1536x1024 ba 1024x1536`
```text
Intent: <infographic | slide | diagram> explaining <topic> for <audience>.
Layout: <flow direction, sections, hierarchy>; <grid/margins>.
Content (verbatim labels): "<label 1>", "<label 2>", …; numbers: <exact data>.
Style: clean flat vector-like graphics, consistent icon style, <palette>, white background.
Constraints: labels exactly as given; no tiny text; no clip art; no decorative clutter; no watermark.
```
Factual relation + label shob verify koro (model plausible but wrong fact banate pare).

### 8.11 Logo / brand mark
`sunburst / high / 1024x1024, background transparent, png, n=3–4`
```text
Intent: original, non-infringing logo for "<Brand>", a <business type>.
Concept: <symbol idea / shapes that define the mark>.
Style: clean vector-like shapes, strong silhouette, balanced negative space, flat colors (<1–2 colors>), minimal strokes, no gradients unless essential.
Output: single centered mark with generous padding, readable at small and large sizes; fully transparent background, clean alpha edges; no backdrop, scenery, checkerboard, mockup, or watermark.
```
Final logo vector (SVG)-e redraw koro: raster logo production-grade na.

### 8.12 Illustration / children's book / comic
`sunburst / high / 1024x1536`
- Character anchor age banao (Section 10), tarpor scene-by-scene edit.
- Comic: "Panel 1: … Panel 2: …"; protita panel-e ekta concrete action beat.
- Style fixed rakho: "hand-painted watercolor look, soft outlines, warm earthy palette".

### 8.13 Game asset (sprite / icon / texture)
- Icon: "centered icon, clear silhouette, generous padding, transparent background, no text".
- Tileable texture: "seamless tileable texture, even lighting, no focal point, no seams" → pore offset-test koro (edge tile hoy kina).
- Sprite sheet: fixed grid bolo ("4×4 grid, equal cells, same character scale and baseline in every frame").

### 8.14 3D / isometric / clay / stylized
```text
Intent: <isometric 3D illustration | claymation still | toy render> of <subject>.
Style: <soft-matte clay with fingerprints | clean isometric low-poly | glossy vinyl toy>, <lighting e.g. soft studio global illumination>.
Camera: <isometric 30° | macro product angle>.
Constraints: consistent material across objects; no text; no watermark.
```

### 8.15 Historical / world-knowledge scene
- Exact place + date dao ("Dhaka, Sadarghat river port, 1965, midday").
- "period-accurate clothing, vehicles, signage; no modern objects".
- Output-e historical accuracy nijei check koro: model plausible-but-wrong detail dite pare.

---

### 8.16 Website, app + brand project (pura image system)

Website ba app banano / improve korar somoy image-er kaj Claude nijei korbe; full playbook: skill-er `references/web-assets.md`. Shongkhepe:

| Dorkar | Kivabe |
|---|---|
| Hero / section / service / interior photo, illustration | Ek `batch`-e sob, shared style lock (`brand/style.json`) + `--export-dir public/images` |
| Layer / cutout / spot illustration | `"transparent": true` (native alpha; edge refine; grey-te judge) ; purono flat-background photo-te `cutout` |
| Logo | Claude SVG likhe (mark + wordmark); concept chaile `--n 4 --explore --transparent` |
| Icon | Project-er SVG icon library ba ekoi style-e hand-written SVG |
| Favicon / app icon / manifest | `favicon` command |
| Social / OG card | `og` command (text typeset, generate na) |
| Brand guideline | `brand/BRAND.md` + `brand/style.json` |
| Existing site | `audit` → keep / re-export / replace / add → abar audit |
| Jayga / audience | request ba `locale --root .` → style lock-e `"locale"` (kichu na thakle `global`), §5.3e |

**Medical / dental ethics:** generated before/after ba "result" image na; generated manush-ke ashol doctor/staff/patient hishebe na; fake testimonial, rating, award, certification ba partner logo na. Clinical accuracy: gloves + mask, bib + protective glasses, real dental chair/light/tray, natural teeth, kono rokto na.

**Demo proof (2026-09-23):** "Hasi Dental Care" landing page: 6 image ekshathe 214 s-e (5/6 first-pass), spot illustration alpha fix-er por PASS_WITH_NOTES, AVIF/WebP/JPEG export, favicon set, OG card, SVG logo, browser-e desktop + mobile verified (mobile-e 768w AVIF load hoy). **Bhul:** ei demo-te Dhaka ami nijei dhore niyechilam, keu bole ni (dekho §5.3e); location chhara request-e ekhon `global` hoy.

## 9. Editing mastery: edit / update / inpaint / composite

### 9.0 Je fact-gulo sob edit workflow-ke niyontron kore

| Fact | Mane |
|---|---|
| Masking **"entirely prompt-based"** (OpenAI) | Mask ekta *hint*; exact shape follow korbe guarantee nai |
| **Puro image regenerate hoy** (community measurement: mask-er baire-o pixel bodlay; ek test-e "preserved" area-r 51.6% pixel >16 value change) | Pixel-identical lagle **composite-back-i ekmatro guarantee** |
| Mask **first image-e** apply hoy; alpha 0 = edit | Edit target sobsomoy `image[0]` |
| Mask-er niche ki ache model **dekhe na** (erase hoye jay) | Recolor/label modify-er moto kaje mask dile content harabe → mask chara edit + nijer mask-e composite |
| Input image-er transparent pixel model **black RGB** hishebe dekhe | RGBA input neutral/edge-extended fill-e flatten koro |
| First image-e sobcheye rich detail | Face/identity image prothome |
| Attach kora reference **eka under-weighted** hoy (community) | Reference-er must-keep element text-eo describe koro |
| Seed nai | Protita output save koro; reproducibility = saved prompt + param + output |
| Responses tool-e main model prompt **rewrite** kore (`revised_prompt`) | Surgical edit-e Images API prefer koro; `revised_prompt` log koro |
| Chained edit **degrade** kore (blur, artifact, contrast/saturation creep, yellow cast; 2 edit-er porei) | Original ba last approved composite theke edit; max 2 chained generation |

### 9.1 Standard edit procedure (protita edit-e)

1. **Input prepare:** EXIF orientation apply → Display P3/Adobe RGB hole sRGB-te convert → RGBA input flatten → valid size (16-er multiple) ba crop window plan → input hash rakho.
2. **Route choose** (9.2 table).
3. **Prompt order:** goal → "change ONLY X" → keep-exactly list → exclusion. Input-ke number + role. Exact text quote-e. Verb "edit"/"draw"; "combine/merge" na; lekho "edit the first image by adding X from the second image".
4. **Request:** `size` = source size (composite-back-er jonno), precision-e Sunburst, `output_format="png"`, precision edit-e `n=2–4`.
5. **Decode + check:** ashol dimension porho (dhore nio na), alignment check, dorkar hole composite-back + color match.
6. **QA** (Section 11).
7. **Iterate:** ek turn = ek change, last approved composite theke; invariant protibar; 2 chained generation-er por original-e fire jao. Protita attempt notun file-e (flawed version-o rakho).

### 9.2 Route table

| Goal | Mask? | Composite back? | Note |
|---|---|---|---|
| Choto local change (recolor, ekta object swap) | optional | **✅** | Prompt-only edit → nijer segmentation mask diye paste back |
| Object replace / insert | ✅ | ✅ | Prompt-e **puro final image** describe koro |
| Relight / style / weather (global) | ❌ | ❌ | Structure QA koro (SSIM on edges) |
| Text swap / localization | ❌ | shudhu text region | Ba live text overlay (best) |
| Background swap | ❌ (cutout) | subject | Pixel-exact subject nije composite |
| Outpaint | ✅ (notun area) | original area | Padded canvas (9.12) |
| 24 MP photo-e choto edit | optional | ✅ | **Crop-edit-paste:** target-er 2–3× context-wala 1024–1536 px window edit → full res-e paste |

### 9.3 Mask inpainting: thik vabe

- **Polarity trap:** shudhu alpha matter kore; **alpha 0 = edit, opaque = keep**. Official B/W→RGBA snippet (`putalpha`) **black pixel-ke editable** kore. Segmentation tool sadharonoto white = object dey → **age invert koro**. "Bhul area edit hocche"-er #1 karon eta.
- **Build:** SAM 2 / Grounded-SAM / face parser → binary threshold → 1024px-e **8–32 px dilate** (blend-er jayga). API mask **binary rakho**: partial alpha-r documented meaning nai. **Feather shudhu composite-er somoy.**
- **Prompt:** official mask example **puro final image** describe kore ("the same sunlit lounge, but the pool contains a flamingo"), shudhu delta na. Hole-e ki boshbe + matching cue (perspective, scale, light direction, shadow/reflection, grain).
- **Object-er shadow/reflection-o mask-e dhoro** (removal-e).
- **Kokhon mask dibe na:** model-ke je jinish *dekhte* hobe (garment recolor, label modify); mask sheta erase kore. Prompt-only edit + nijer mask-e composite back.

```python
from PIL import Image, ImageFilter, ImageOps
seg = Image.open("object_white.png").convert("L")             # white = object (segmentation output)
edit_area = seg.point(lambda v: 255 if v > 127 else 0).filter(ImageFilter.MaxFilter(17))  # binary + ~8px dilate
alpha = ImageOps.invert(edit_area)                             # object -> alpha 0 (editable)
mask = Image.new("RGBA", seg.size, (0, 0, 0, 255)); mask.putalpha(alpha)
mask.save("mask.png")                                          # same size as image[0]
```

### 9.4 Composite-back: pixel-identical region-er ekmatro guarantee

1. Edit **exact source size**-e request (invalid size hole reflection-pad → pore crop).
2. **Align check:** preserved region-e global shift (ECC ba ORB+RANSAC). Residual >~2px hole composite koro na (ghosting): regenerate ba crop-edit.
3. **Color match:** selection-er 16–48px baire ring-e duita image-er Lab mean/std → Reinhard transfer.
4. **Blend:** API mask ~24px grow; composite mask ~6px grow + 4–16px feather (seam model-er coherent redraw-er bhitore pore). Heavy texture → multi-band blend; light different → Poisson (`cv2.seamlessClone`), color shift check.
5. **Verify:** selection-er baire difference = 0 (by construction); seam band-e judge crop check.

```python
from PIL import Image, ImageFilter
orig = Image.open("original.png").convert("RGB")
edit = Image.open("edited.png").convert("RGB").resize(orig.size, Image.Resampling.LANCZOS)
sel = Image.open("selection.png").convert("L")   # white = region to take from the edit
sel = sel.filter(ImageFilter.MaxFilter(13)).filter(ImageFilter.GaussianBlur(8))   # grow ~6px + feather
Image.composite(edit, orig, sel).save("final.png")   # outside selection = original pixels
```

### 9.5 Multi-turn edit (Responses API)

- `previous_response_id` + tool `action: "edit"`; stateless hole `{"type":"image_generation_call","id": ig_id}` + notun instruction.
- `revised_prompt` protita turn-e log koro: main model precise instruction rewrite kore dite pare.
- Chain degradation rule: **max 2 chained generation**, tarpor original / approved composite theke; onek change ek prompt-e combine koro; step-er majhe PNG; protita step-er por composite.
- OpenAI migration advice: single step na, **puro edit sequence test koro**.

### 9.6 Identity (face) lock

- Face image **first input**. Onek manush hole shob face **ek composite image**-e bosiye pathao (first image-e extra richness).
- **Choto, dridho lock bhasha**, karon lomba facial description dile model ekta "lookalike" invent kore (baoyu-skills finding):
  *"Same person as Image 1. Do not redesign, beautify or average the face. Keep skin tone, body shape, pose, expression, hairstyle and proportions. Change only <X>."* + *"Preserve natural skin texture and pores; no retouching."*
- Identity reference: **2–4 curated real photo**; **generated image kokhono identity reference na**. Boyosh dekhate styling bodlao, face na.
- **Plastic face** (gpt-image-2 product edit-e report, OpenAI fix nai): face-e change na lagle **original face+hair face-parsing mask diye composite back**; "studio perfect"/"cinematic" word bad; face-ke beshi pixel dao; Sunburst `high` vs `xhigh` compare.
- QA: facial similarity 0–5 (judge). Face-embedding similarity = biometric data → consent chara na.

### 9.7 Product / logo / label preservation

- Clean high-res packshot **first input**; label text verbatim quote; brand nam letter-by-letter.
- *"Image 1 is the product's source of truth: keep its geometry, proportions, materials, colors, closure and label layout exactly; do not restyle, redraw or re-letter it."*
- **Final logo kokhono model-drawn na:** prompt-e jayga faka rakho ("empty top-right area, no text or logos") → vector master composite (perspective warp + shading match).
- Geometry thik, label bhul → real label art homography (flat) / cylindrical warp (bottle) diye bosao + generated luminance multiply (shading).
- Legal-approved label copy → pixel-exact composite (regenerate-e bhorsa na).
- **Catalog consistency:** ekta background plate generate → protita SKU cutout oi plate-e composite → shob SKU-te identical background.

### 9.8 Multi-reference compositing

- Prompt-er **prothom line-e reference role list**: `Image 1 = edit base (mask applies here); Image 2 = identity; Image 3 = style (palette + materials only, not layout)`. Protita reference theke ki nibe **ar ki nibe na** duitai bolo.
- Ki kothay jabe, relative scale ("the dog's head reaches her knee"), matched lighting/perspective/shadow.
- 1–4-ta relevant, tight-cropped reference ("16 reference" claim 2.5-e undocumented).
- *"Edit image 1 by adding the <object> from image 2 <exact placement>, at <relative scale>. Match image 1's light direction, color temperature, perspective and shadows. Change nothing else in image 1."*

### 9.9 Relight / time of day / weather

- Shudhu environment change: light direction/quality/temperature, sky, shadow, haze/precipitation, wet/snowy surface, practical light. Identity, geometry, camera angle, object position same.
- Chain-e choto follow-up kaj kore ("make it a winter evening with snowfall").
- Composite-back apply hoy na → structure QA (edge-map SSIM) + identity/label check.

### 9.10 Background replacement + transparent cutout

- **Cutout:** `background="transparent"` + PNG/WebP + isolated-subject prompt; return alpha rakho; porer protita edit-e "preserve the transparent background". Painted checkerboard ≠ transparency: **alpha decode kore check**.
- Known alpha defect (gpt-image-2 preview-e report): "opaque" pixel alpha 252–254, alpha-r niche grey RGB rim → halo → Section 13 defringe.
- **Pixel-exact subject + notun background:** subject cutout → matching light direction + subject-er jonno faka jayga shoho background generate → contact shadow diye composite (optional: shudhu background+shadow-e masked harmonize edit, tarpor subject abar composite).
- **Glass/smoke/glow fallback:** subject-e nai emon matte color-e generate → matte color **auto-sample** (prompt-e "#ff00ff" dileo exact ashe na) → local chroma-key + spill suppression; ba black + white duita aligned render → difference matte.

### 9.11 Object removal

- Object + tar **shadow/reflection** mask-e; result describe koro ("hand empty and relaxed; the brick wall continues"); tarpor composite back.

### 9.12 Outpainting (canvas extend)

1. Valid target canvas choose, original offset-e bosao.
2. Notun area **blurred edge extension** diye fill: **black/transparent kokhono na** (black bar ashe).
3. Mask: notun area alpha 0 + original-er edge-e **16–48px overlap band**.
4. `size` = canvas size, canvas = `image[0]`.
5. Prompt: *"The original photo sits at <position>; the masked border areas are empty. Extend the scene naturally: continue the <horizon/floor/wall/sky>, perspective, lighting and color grading. Keep the original area unchanged. No frames, borders, vignettes, text or duplicated objects."*
6. Original feather kore composite back.
7. Boro extension: protita step-e ≤~1.5× (1024² → 2048×1024 → 3072×1024 = 3:1 limit), protita step-er por composite.

### 9.13 Upscaling

| Final size | Strategy |
|---|---|
| ≤ 2560×1440 | Final size-e native generate |
| ≤ 8.29 MP (3840×2160) | Native possible (experimental): 2K + super-resolution-er sathe test set-e compare; 4K `high` ≈ $0.10, `max` ≈ $0.40 |
| > 8.29 MP / print | 2–4K generate → **non-generative** SR (Real-ESRGAN / SwinIR class) product/text/face-e; "creative" diffusion upscaler shudhu texture/background-e; logo/text vector master diye replace; sharpen shesh-e |
| Re-render | Edit: *"Recreate this exact image at higher resolution; preserve composition, shapes, identities, text and colors exactly; add only fine natural detail; add, remove or move nothing."* → full regenerate, tai QA (downscale-e SSIM ≥ ~0.9 vs approved) |

Print note: A4 @300ppi (2480×3508) pixel cap-er upore; valid largest A-series ≈ **2416×3424** (~291 ppi, experimental) → beshi lagle upscale.

### 9.14 Style transfer, sketch-to-render, reverse-prompting

- Reference-er role specific: "use Image 1 only for palette, texture and medium" + notun subject alada describe.
- Sketch: layout, proportion, perspective exactly preserve; sketch-er intent onujayi realistic material + light; "no new elements or text".
- **Reverse-prompt** (reference image theke prompt): subject, composition, perspective, light direction + ratio, palette, material, spatial layer, medium; ei 8 dik break down koro; match-er jonno **sobcheye critical 3–5 detail prompt-er prothom tritiyangshe**; artist/brand/IP nam → visible trait-e translate.

### 9.15 Edit prompt template library (nijer bhashay, copy-paste)

```text
T1 SURGICAL: Edit image 1. Change ONLY <target> to <new state>. Keep EXACTLY unchanged: identity and face, pose,
product geometry and label text "<...>", layout, camera angle, framing, light direction, white balance, exposure,
saturation, contrast, background, and every other object and text. Match the original grain and sharpness in the
edited area. No new objects, text, logos or watermarks.

T2 MASKED: <Full description of the final image>. In the masked region show <content>, matching the perspective,
scale, light direction, shadows/reflections and grain of the surrounding photo. Everything else stays identical.

T3 IDENTITY: Same person as Image 1. Do not redesign, beautify or average the face; keep skin tone, body shape,
pose, expression, hairstyle and proportions. Replace only <clothing/background/...>, fitted naturally to the existing
pose, with lighting and color temperature matched to the original. Preserve natural skin texture and pores; no
retouching. Do not change the camera angle, framing or image quality.

T4 PRODUCT: Image 1 is the product's source of truth. Place this exact product <scene>. Keep geometry, proportions,
materials, colors, closure and label layout exactly; the label reads exactly "<L1>" / "<L2>" (spelled <B-R-A-N-D>).
Do not restyle, redraw or re-letter it. Realistic contact shadow and reflections. No other text.

T5 COMPOSITE: Edit image 1 by adding the <object> from image 2 <exact placement>, at <relative scale>. Match image 1's
light direction, color temperature, perspective and shadows. Change nothing else in image 1.

T6 RELIGHT: Re-stage this photo as <time / weather>. Change only environmental conditions: light direction, quality
and color, sky, shadows, <fog/rain/snow>, wet surfaces, practical lights. Keep composition, camera, geometry, object
positions, identities and signage text. Photorealistic, not stylized.

T7 BACKGROUND: Keep the subject of image 1 exactly (pose, edges, hair strands, clothing, product details). Replace only
the background with <bg>. Match the subject's existing light direction and color temperature; soft plausible contact
shadow; no halos.

T8 CUTOUT: Isolate the product from the input image on a fully transparent background: centered, crisp silhouette,
no halos or fringing. Keep its geometry and label legibility exactly; light polishing only. No backdrop, checkerboard,
scenery or shadow; do not restyle it; keep clean alpha.

T9 REMOVE: Remove <object> together with its shadow and reflection. Fill with the plausible continuation of <surface>,
matching texture, perspective, light and noise. Change nothing else.

T10 TEXT: Replace text only, using this exact case-sensitive mapping: 1) "<src>" -> "<dst>" 2) ... Keep each string's
position, alignment, font style, weight, color and size (shrink to fit if longer). No other text; no other changes.

T11 STYLE: Use image 1 only as the style reference (palette, texture, brushwork, medium), not its layout or people.
Create <new subject/scene> on <background>. No extra elements.

T12 SKETCH: Turn this drawing into a photorealistic image. Keep the exact layout, proportions and perspective; choose
realistic materials and lighting that fit the sketch's intent. Add no new elements or text.

T13 OUTPAINT: (see 9.12 step 5)        T14 RE-RENDER: (see 9.13)

T15 SERIES: Continue the story with the same character. Scene: <...>. Character bible: <verbatim bible block>.
Style: <fixed style block>. Do not redesign the character; no text; no watermarks.

T16 PHYSICS FIX: Fix only the <pour/splash/reflection/shadow>: <source> tilted about <angle> toward <target>; <substance>
leaves only from <exact exit point> in one continuous stream and ends inside <target>; remove any flow from <wrong place>.
Keep hands, objects, lighting, framing and everything else unchanged.

T17 GRIP/LOAD FIX: Fix only the hands and how they hold the <object>. The <object> is <anatomy, e.g. a round terracotta
kolshi with NO handle and NO spout>. The hand on the viewer's <side> spreads flat under the <belly/base> and carries the
weight (fingers pressing into the surface, wrist bent back, forearm tense, elbow tucked in); the other hand rests on the
<shoulder/rim> only to steer and tilt it; the <object> stays close to the body. Keep the object's shape, the pour, the
face, clothing, lighting, framing and everything else unchanged. (Pose-level problem hole edit na: regenerate.)
```

### 9.16 Edit failure mode → fix

| Symptom | Karon | Fix |
|---|---|---|
| **Drift** (na-chawa change) | Puro image regenerate; mask shudhu hint | Invariant list, "change ONLY", composite back, non-target invariance judge |
| **Cumulative degradation** | Chained edit | Original-e re-anchor, change combine, PNG between steps, ≤2 chain |
| **Face change / plastic skin** | Identity drift, beautification | Face first, short lock prompt, skin-texture clause, face composite-back, Sunburst, beshi pixel |
| **Color shift / yellow cast** | Global WB/tone drift; "warm/cinematic/golden" word | Composite back; untouched area-e Lab histogram match; "keep the original white balance, exposure and grading"; ΔE00 QA |
| **Black rectangle / black bar** | Mask polarity ulto / alpha nai; transparent input black dekha; delta-only prompt hole fill kore na; gateway mask drop kore | Debug overlay-e polarity check; official alpha snippet; input flatten; puro final scene describe; mask boro; direct `/v1/images/edits` |
| **Halo / fringe** | Alpha 252–254, grey rim | Alpha clip, 1px choke, color bleed, premultiplied resize, black/white/grey/brand-e preview |
| **Mask-er baire edit** | Prompt-based masking | Composite back (ekmatro guarantee) |
| **Text error / micro-gibberish** | Model limit | Quote, spell, kom + boro word, higher quality, "no other text anywhere", OCR gate, ba live text overlay |
| **Extra finger / anatomy** | Model limit (2.5-eo dekha) | Judge artifact metric; best-of-N |
| **Silent quality regression** | gpt-image-2 (2026-06→09 report) | Snapshot pin; daily canary; request ID rakho |
| **Output dimension bhinno** | Codex backend: 1536×864 chaile 1672×941 | Decoded dimension sobsomoy porho |
| **Physics bhul** (dhara mug-er gaa theke, chaya/pratibimba mile na) | Model pattern aake, physics na | Action mechanics line; static moment; T16 physics-fix edit + composite back; judge-e `physics_plausibility` |
| **Phantom handle / ojon-hin grip** (handle-chara kolshi-r gola handle-er moto dhora, spout jog, bhari patro angul-er dogay) | Common object-er pattern (pitcher) rare object-e boshe; haat pose template, bol-er hishab nei | Object anatomy + Grip & load line; haat frame position diye; hip/surface support pose; T17 fix (local) ba correction soho regenerate (pose); judge-e `hand_object` gate |

---

## 10. Consistency system: brand, character, series

### 10.1 Brand DNA block (OpenAI transparent-asset cookbook pattern)

Ek brand-er shob asset-e ek-i **suffix block** jog koro, tate collection visually consistent hoy:
```text
Brand DNA: <BRAND>, <one-line positioning>. Materials: <signature materials>. Palette: <3–5 named colors or hex>.
Light: <signature lighting>. Mood: <2–3 words>. Rendering: photorealistic micro-detail, premium campaign quality.
Always: full object visible and generously padded; preserve natural transparency and refraction.
Never: other brands' logos, readable text unless specified, watermark.
```
Protita product prompt = *product-specific description* + *same Brand DNA block* (verbatim, change kora na). Hex/color nam shudhu rendering guidance: "don't print color names or hex codes as text" bolo.

### 10.2 Campaign Style Lock (multi-image campaign: buluslan pattern)

2+ image-er campaign-e **10-field lock** banao, protita prompt-er shurute verbatim:

| Field | Example |
|---|---|
| Direction | "clean Scandinavian morning" |
| Palette (hex) | #F4EFE6, #2E3A33, #C9A36B |
| Color temperature | 5200K daylight |
| Type + fallback | "geometric sans, medium weight" |
| Background | "warm off-white plaster" |
| Lighting | "soft window key from left, no hard shadows" |
| Layout | "subject lower-left third, copy space top-right" |
| Icon system | "thin line icons, 2px" |
| Product presentation | "3/4 view, label facing camera" |
| Immutables | "logo never altered, label text exact" |

Per image shudhu vary: purpose, action, local composition, short copy. Batch-er age **ekta representative sample approve** koro, tarpor shob worker-ke *identical method* (model/size/quality/prompt source) dao.

### 10.3 Character bible + anchor sheet

1. **Character sheet** banao: turnaround (front/¾/side/back), 3 expression, palette swatch, outfit callout, plain background. Approve → **Anchor A**; face close-up → **Anchor B**.
2. **Character bible** text block (age, face shape, eye color, hair, signature clothing + colors, proportion, personality): protita prompt-e **verbatim paste**.
3. **Branch from anchors, chain na:** protita scene = `edit(image=[AnchorA, AnchorB, scene_ref…])`, ager scene theke na.
4. Fixed: model snapshot, quality, size, style block, palette hex.
5. Tight consistency lagle **ek image-er bhitore variant** (numbered 4×4 pose sheet, 16-frame orbit) generate kore slice koro.
6. QA: pairwise judge (anchor vs new: feature, proportion, palette, outfit, style) ≥ 4.

### 10.4 Canonical base + layout guide (animation / set)

- Ek approved canonical base → protita porer job-e attach.
- Set/strip **ek call-e** generate (frame-by-frame drift kore); slot count/spacing-er jonno invisible **layout-guide image** second input ("do not draw the guide").
- Post: equal slot split → alpha bbox → ek global scale → bottom-center align → frame-01 lock.

### 10.5 Series production checklist

☐ Model snapshot pin (`-2026-09-08`) ☐ Same quality + size ☐ Same Brand DNA / Style Lock ☐ Palette hex fixed ☐ Same light direction ☐ Anchor image attach ☐ 1 sample approve → batch ☐ Post-e same grade/LUT ☐ Catalog-e shared background plate ☐ Pairwise consistency QA.

---

## 11. QA + evaluation: top-1% ar amateur-er ashol parthokko

Amateur image dekhe "bhalo lagche" bole. Pro **generation-er age acceptance define kore**, tarpor **measure** kore. OpenAI Image Evals cookbook + official plugin + community best practice mile ei system.

### 11.1 Philosophy (5 niyom)

1. **Gate first, grade second:** instruction following, exact text, spec (size/alpha) holo gate (PASS/FAIL); tarpor 0–5 graded metric. **Score average koro na:** ekta gate fail = fail.
2. **Verdict code-e compute koro**, judge-ke free-text verdict likhte dio na (cookbook-er defect).
3. **Uncertain hole kom score** ("if unsure between two scores, pick the lower").
4. **Brand-critical edit-e "near-miss = failure"** (cookbook logo-edit rubric: shob ≥4).
5. **Ek fix per round**: failing element-er nam dao, tarpor ekta change (quality step *ba* prompt change, duita eksathe na).

### 11.2 Acceptance: generation-er AGE likho

Deliverable type onujayi "ki thakle unusable" checklist:
- **Poster/ad:** protita character spelling, copy missing/duplicate na, CTA readable, safe zone faka.
- **Product:** geometry, label text exact, color, contact shadow.
- **Portrait:** identity (edit-e), hands, eyes/catchlight, skin realism.
- **Diagram/infographic:** protita label, relation data-r sathe mile, number exact.
- **Cutout:** alpha present, halo nai, edge-e subject kata na.
- **Series:** anchor-er sathe consistency ≥4.

### 11.3 Three-stage QA loop

```
[1] Deterministic code checks (free, fast)  →  fail? fix/regenerate
        ↓ pass
[2] Vision-LLM judge (rubric, defects list first, JSON)  →  fail tags → targeted fix
        ↓ pass (≥1 candidate)
[3] Pairwise tournament (A/B both orders; inconsistent = tie)  →  winner
        ↓
[4] Human review: shudhu brand-critical, real people, ba check-er majhe disagreement
```

### 11.4 Deterministic check (code)

| Check | Method | Threshold |
|---|---|---|
| Decode + exact dimension + mode | Pillow | Spec-er sathe exact (requested vs actual alada log) |
| Transparency health | RGBA? % fully transparent > 0; core alpha 255 (252–254 clamp); transparent pixel-e RGB residue; checkerboard periodicity na | Gate |
| Drift outside mask | Mean abs diff + % pixel (max channel change >16) | Raw output-e diagnostic; **composite-back-er por = 0** |
| Preserved-region structure | SSIM / LPIPS | Workflow onujayi |
| Preserved-region color | ΔE00 mean / p95 | Mean ≤2 (brand-critical ≤1) |
| Text exact | OCR set-diff (niche 11.7) | 100% required, 0 extra |
| Brand palette | k-means dominant vs brand hex, ΔE00 | ≤5 |
| Duplicate | Perceptual hash | Near-duplicate reject |
| Safety | `omni-moderation-latest` on output | Not flagged |
| Provenance | Archived original-e C2PA present | Present |

```python
from PIL import Image
im = Image.open("cutout.png")
assert im.mode == "RGBA", "no alpha channel"
a = im.getchannel("A"); hist = a.histogram(); n = im.width * im.height
transparent = hist[0] / n; near_opaque = sum(hist[247:255]) / n
print(f"transparent={transparent:.1%} near-opaque(247-254)={near_opaque:.2%}")
assert transparent > 0, "no transparent pixels (painted checkerboard?)"
```

### 11.5 Master rubric (threshold = starting point; nijer human label diye calibrate koro)

> **Script-er judge (codex_image.py) eta-i use kore:** 6-ta gate (instruction_following, text_exact, physics, hand_object, anatomy, no_unrequested_elements) + 5-ta score (realism, artifacts, physics_plausibility, composition, brief_fidelity), `--threshold 4`. Realism: 5 = unretouched camera photo, 4 = halka polish, 3 = stock polish/AI tell → FAIL. PASS / PASS_WITH_NOTES / FAIL / ERROR-er puro rule: `references/cli.md` → Verdicts. Nicher table-er ≥3 threshold shudhu manual review-er jonno.

| Dimension | Type · method | Standard | Brand-critical |
|---|---|---|---|
| Instruction following + deliverable type | gate · judge | PASS | PASS |
| Required text exact, extra text nai | gate · OCR + judge | 100% / 0 extra | + human |
| Edit intent correctness | 0–5 · judge | ≥4 | 5 |
| Non-target invariance | 0–5 · judge + pixel diff | ≥4 | composite-er por 0 drift |
| Identity / facial similarity | 0–5 · judge | ≥4 | ≥4 + human |
| Product / outfit fidelity (label OCR) | 0–5 | ≥4 | 5 |
| Logo character + style integrity | 0–5 | ≥4 | ≥4 + vector overlay |
| Layout + hierarchy | 0–5 | ≥3 | ≥4 |
| Style + brand fit | 0–5 + palette ΔE00 | ≥3 | ≥4, ΔE00 ≤5 |
| **Realism** (light, shadow, perspective, skin) | 0–5 | ≥3 | ≥4 |
| **Artifacts** (hand, melting, seam, sparkle) | 0–5 | ≥3, "major" nai | ≥4, kichui nai |
| Color fidelity (preserved region) | ΔE00 mean | ≤2 | ≤1 |
| Transparency health | gate · alpha stats | present, checkerboard na | + halo score |
| Technical spec | gate · code | exact | exact |
| Safety / policy | gate · moderation | not flagged | + human (real people) |

Data-viz/editorial alternative (OpenAI `build-web-data-visualization`): 7 category × 1–5, ship **≥28/35 ar kono category <4 na**.

### 11.6 Use-case gate (OpenAI Image Evals cookbook)

| Case | Gate | Graded (0–5) | Verdict |
|---|---|---|---|
| UI mockup | instruction_following, in_image_text | layout_hierarchy, ui_affordance | Duita gate PASS + graded ≥3 |
| Marketing flyer | instruction_following, text_rendering (spelling, casing, symbol; extra text = fail) | layout, style_brand_fit, visual_quality | Gate PASS + shob ≥3; "text average kore dhakbe na" |
| Virtual try-on | none | facial_similarity, outfit_fidelity, body_shape | Kono-ta ≤2 hole FAIL (commerce: outfit ≥4) |
| Logo edit | none | edit_intent, non_target_invariance, character_style_integrity | **Shob ≥4**; near-miss = fail |

Cookbook-er published result shikkha: logo edit 5/0/2 → FAIL (text thik kintu background/glow bodleche); **editing-e preservation-i kothin ongsho**.

### 11.7 Judge prompt template (cookbook structure, nijer bhashay)

```text
<core_mission>Evaluate whether the output image satisfies the instruction and criteria below. Judge only against them.</core_mission>
<role>You are a strict senior art director and QA reviewer.</role>
<scope_constraints>Do not reward creativity that violates constraints. Missing or extra elements are serious errors.
List every visible defect (what, where, severity) BEFORE scoring.</scope_constraints>
<metrics>
- instruction_following: PASS | FAIL
- text_exact: PASS | FAIL | NA  (exact spelling, casing, punctuation; any extra text = FAIL)
- realism (0-5): 5 = indistinguishable from a real photo at 100% zoom; 3 = believable at a glance, flaws on zoom; 0-2 = obviously synthetic
- artifacts (0-5): 5 = none; 3 = minor; 0-2 = major (extra fingers, melting, seams)
- non_target_invariance (0-5, edits only): 5 = nothing outside the target changed; 3 = small drift; 0-2 = noticeable changes
- brand_fit (0-5)
- physics_plausibility (0-5): 5 = every flow, force, reflection and shadow has a correct source and target; 0-2 = impossible physics (e.g. liquid emerging from a container wall)
- hand_object: PASS | FAIL | NA  (every hand touches a part that exists and is meant to be held: no phantom handles or added spouts; the grip suits the weight; every heavy object has a hand, forearm, hip or surface under its center of mass with visible load cues; tools held the right way; handling matches the place)
</metrics>
<consistency_rules>If uncertain between two scores, choose the lower one. Base scores on concrete visual observations.
Penalize cumulative degradation across edits.</consistency_rules>
<output_constraints>Return JSON only, matching the schema.</output_constraints>
Input order for edits: instruction + criteria text → input images → mask → OUTPUT IMAGE LAST.
```

JSON schema outline:
```json
{"defects":[{"what":"","where":"","severity":"minor|major|critical"}],
 "instruction_following":"PASS|FAIL","text_exact":"PASS|FAIL|NA",
 "edit_intent":0,"non_target_invariance":0,"identity":0,"product_fidelity":0,
 "realism":0,"artifacts":0,"brand_fit":0,
 "hand_object":"PASS|FAIL|NA","hand_object_trace":["hand (<frame position>) -> <part> (exists: yes/no) -> <grip> -> <role> = OK|WRONG"],
 "fix_mode":"edit|regenerate|none",
 "failure_tags":["drift","text_error","identity_drift","halo","color_shift","extra_text","anatomy","label_error","seam","ai_look","physics","hand_object"],
 "reason":""}
```
Code-e PASS = shob gate PASS/NA + protita applicable metric threshold-e + kono critical defect nai. Output image `detail:"original"`-e pathao; fine detail-er jonno crop/zoom judge (seam, logo, face).

**Verdict policy v2 (quality first, 2026-09-23 benchmark theke):**

| Verdict | Condition | Action |
|---|---|---|
| PASS | Sob gate PASS/NA, sob score ≥ 4, critical defect nei | Deliver |
| PASS_WITH_NOTES | Quality gate (text_exact, physics, hand_object, anatomy, no_unrequested_elements) + realism / artifacts / physics_plausibility ≥ 4, critical nei; shudhu brief precision (instruction_following, composition / brief_fidelity = 3) kom | Deliver, note-e bolo kon brief detail alada; fix round kharach koro na |
| FAIL | Baki sob | Fix route (edit / regenerate); sob candidate ekoi quality rule bhangle fix skip → `model_limit` |

Keno: benchmark-e "fill 4/5 vs 2/3", "haat ulto", "suto ektu jhola" moto brief micro-detail-er jonno brief_fidelity 4↔3 hoy, karon judge-er run-to-run variance. Mean judge score (25-e) agent mode 20.1, fast mode 20.8: quality ek, kintu shudhu threshold-e pass count ulta-palta hoy. Client-er exact spec lagle `--strict`.

### 11.8 OCR set-diff (text gate): cookbook-er bug theke shikkha

- Vision model/OCR diye protita text line list koro → required copy-r sathe **set-diff** (missing + extra).
- **Normalize age:** NFKC + dash (hyphen, en dash, em dash), bullet (`•`), quote (`"` `"` `'`) map; cookbook-e prompt "20% OFF - Mon-Thu" ar expected "20% OFF • Mon–Thu" mile nai bole gate sobsomoy fail korchilo.
- Allow-list-e **shob allowed string** (brand nam-o) rakho.
- Judge ar OCR mile na → human.
- Non-Latin script (Bangla, CJK) → dedicated OCR/human check (vision model durbol); look-alike character (戊/戌/戍) check.

### 11.9 Best-of-N + escalation

- **N = ⌈ln(1−target) / ln(1−p)⌉** (p = measured pass rate). p=0.5, target 95% → N=5; p=0.3 → N=9.
- **Sequential sampling:** k-er batch, first pass-e thamo (cost bachay).
- **Escalation ladder:** quality low → high → xhigh; model Flare → Sunburst; tarpor prompt fix.
- IPM limit mone rakho (Tier 1 = 5 image/min).

### 11.10 Regression suite + prompt versioning + cost

- **Golden set:** 50–200 case (workflow + failure tag onujayi), 3–5-step edit chain shoho; snapshot pin; frozen input/param; case-proti k=3–5 sample (seed nai).
- Report: pass rate (Wilson CI), paired McNemar test, per-dimension delta, p50/p95 latency, **cost per accepted image**.
- **Daily 20-case canary** (silent regression dhorte, gpt-image-2 `low` regression-er moto).
- Judge model pin; judge bodlale frozen artifact abar judge.
- 50–100-item human anchor set; gate-e judge agreement ≥90%.
- Hosted OpenAI Evals platform **2026-11-30-e shutdown** (read-only 10-31 theke) → nijer harness ba Promptfoo.
- **Per-asset log:** template_id, template_version, prompt_sha256, rendered prompt, snapshot, endpoint, params, input+mask hash (ICC + dimension), request_id, revised_prompt, usage, latency, output hash, deterministic metrics, judge model + prompt version, scores, tags, human verdict, cost, C2PA parent hash.
- **Cost per accepted image** = (generation + judge + human review + post) ÷ accepted. Example: Flare `high` 1536×1024 ≈ $0.041 output; 40% pass rate-e ≈ $0.10/accepted (input + judge chara).

### 11.11 Human quick-QA (60 second, 200% zoom)

☐ Hand/finger ☐ Text spelling (character-by-character) ☐ Catchlight = light source ☐ Shadow direction + contact shadow ☐ Cloned face/texture nai ☐ Hair edge halo nai ☐ Skin wax/etched nai ☐ Color cast nai ☐ Background-e melted object nai ☐ Verticals thik (architecture) ☐ Product/label exact ☐ Alpha real (transparent) ☐ Brand palette ☐ Na-chawa element (Sunburst embellishment) nai ☐ Deliverable size/format exact ☐ **Physics trace** (pour/splash/reflection/shadow: source → path → target) ☐ **Hand-object** (phantom handle nei, grip + ojon-er support + load cue thik, tool shoja dhora).

---

## 12. The Director's Loop: iteration protocol (top-1% workflow)

Pro-ra ek shot-e perfect image asha kore na: **explore → select → refine → finalize → QA** loop chalay. GPT Image-e **seed nai**, tai reproducibility ashe prompt/param/output save kore.

### 12.1 Nine steps

| # | Step | Ki korbe | Output |
|---|---|---|---|
| 1 | **BRIEF** | Intent, deliverable (size/format/kothay use), must-have (exact text, brand, product reference), constraint, "done" mane ki | 5–8 line brief |
| 2 | **PLAN** | Surface (Codex built-in / Images API / Responses), model, quality ladder, size, `n` | Plan line |
| 3 | **EXPLORE** | 3–4 *alada* direction (composition/light/angle alada): `low` quality, Flare | 3–8 draft |
| 4 | **SELECT** | Quick score (concept, composition, light) → 1–2 winner | Winner + keno |
| 5 | **REFINE** | Single-change follow-up; invariant list protibar repeat; change log rakho | Refined draft |
| 6 | **FINALIZE** | Winning prompt `high`/`xhigh`-e (Sunburst); seed nai bole final quality-te best-of-2/3 | Final candidate |
| 7 | **QA** | Section 11 rubric + 100% zoom + text + alpha check | Pass / fail + fix list |
| 8 | **POST** | Crop, sRGB, format, alt text, naming | Deliverable |
| 9 | **LOG** | Prompt, param, model, `revised_prompt`, `usage`, cost, QA score → manifest | Reproducible record |

### 12.2 Explore stage-e "diversity" ano

Same prompt 4 bar chalano = 4-ta prai same image. Pro-ra **direction vary kore**:
- A: eye-level, window light, candid
- B: overhead / flat lay, soft daylight
- C: low angle, overcast side light
- D: tight detail crop, macro texture

### 12.3 Fix-phrase library (surgical follow-up, copy-paste)

| Problem | Follow-up prompt |
|---|---|
| Skin plastic/waxy | "Keep everything the same; restore natural skin texture with visible pores, fine lines and slight tonal variation; no smoothing." |
| Too polished / stock-photo feel | "Keep the scene; make it feel candid and unposed: relaxed posture, natural gaze away from camera, everyday imperfections." |
| Over-saturated / HDR | "Keep all content; reduce saturation and contrast to natural, true-to-life levels; no HDR glow." |
| Light fake/flat | "Keep composition; relight with a single soft window light from the left and natural falloff; realistic shadows." |
| Background too clean | "Add one subtle lived-in detail at the edge of the background (a coat on a chair) without changing the subject." |
| Extra object | "Remove the <object> on the right; change nothing else." |
| Hand/finger vul | "Fix the hands: natural anatomy, five fingers each, relaxed grip on the <object>; keep everything else unchanged." |
| Text vul | 'Correct the text to read exactly "<…>"; same font, size and position; change nothing else.' |
| Drift in edit | "Restore the <element> exactly as in the first image; keep the rest of this edit." |
| Product/label change | "Keep the product exactly as in Image 1: same shape, proportions, label text and colors." |
| Too much bokeh | "Keep framing; use a deeper depth of field so the background stays recognizable." |
| Phone-real look | "Same scene as a casual phone photo: deeper depth of field, slightly imperfect framing, natural phone HDR." |
| Pour/flow source bhul | "Fix only the pour: tilt the mug about 45° toward the cup so the tea leaves only over its lowest rim point in one continuous stream into the cup; nothing flows from its side or bottom; change nothing else." |
| Phantom handle / ojon-hin grip | "Fix only the hands: the kolshi has no handle; the hand on the viewer's right spreads flat under its belly and carries the weight (fingers pressing into the clay, wrist bent back, forearm tense); the other hand rests on its shoulder only to steer; keep the pot close to her hip; change nothing else." |

### 12.4 Kokhon regenerate, kokhon edit

- **Composition/concept bhul** → regenerate (prompt thik kore).
- **Composition thik, choto detail bhul** → edit (change only X).
- **Onek bar edit-er por quality nemeche / drift** → **original image theke** abar edit koro, chain theke na.
- **Pixel-identical region lagbe** → approved edit-ta original-er upor **composite** koro (mask diye layer), prompt-er upor bhorsa na.

---

## 13. Production pipeline: generation theke delivery

### 13.1 Deliverable spec (age thik koro)

| Field | Example |
|---|---|
| Final size | 1080×1350 (IG 4:5) |
| Generation size | `1088x1360` (valid) → center crop |
| Format | Master PNG; delivery WebP q85 |
| Color | sRGB |
| Background | opaque / transparent |
| Safe zone | Top 15% text-free (platform UI) |
| Alt text | Required |

### 13.2 Post-processing command (macOS / Python)

```bash
# 1920x1088 -> 1920x1080 center crop (macOS sips)
sips --cropToHeightWidth 1080 1920 hero-master.png --out hero-1920x1080.png
# alpha ache kina
sips -g hasAlpha cutout.png
```

```python
from PIL import Image, ImageOps
img = Image.open("hero-master.png")
img = ImageOps.fit(img, (1920, 1080), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))  # exact crop
img.convert("RGB").save("hero-1920x1080.webp", "WEBP", quality=85, method=6)
```

Alpha defringe (transparent asset-e halo thakle): alpha 250–254 → 255 clamp; edge 1px contract; dark/green fringe thakle despill (`remove_chroma_key.py --spill-cleanup` logic).

### 13.3 Naming + manifest (reproducibility)

`assets/<campaign>/<asset>/<asset>-v03-sunburst-high-1536x1024.png`

```json
{
  "asset": "spring-hero",
  "version": 3,
  "model": "gpt-image-2.5-sunburst",
  "params": {"size": "1536x1024", "quality": "high", "output_format": "png", "background": "opaque"},
  "prompt": "Intent: ... (full prompt)",
  "inputs": ["refs/product-front.png"],
  "revised_prompt": null,
  "usage": {"input_tokens": 0, "output_tokens": 0},
  "qa": {"score": 0.0, "pass": false, "notes": ""},
  "created": "2026-09-23"
}
```

Generation size calculator (tested):
```python
import math
def c16(x): return math.ceil(x / 16) * 16
def gen_size(tw, th):
    s = max(1.0, math.sqrt(655_360 / (tw * th)))      # minimum pixel rule
    w, h = c16(tw * s), c16(th * s)
    if w * h > 8_294_400 or max(w, h) > 3840:
        return "too big: generate largest valid same-aspect size, then upscale"
    return w, h          # e.g. (1920,1080)->(1920,1088), (800,800)->(816,816), (1200,630)->(1200,640)
```

### 13.4 Provenance + accessibility

- **Untouched API PNG + SHA-256** provenance parent hishebe rakho. Re-encode korle C2PA harate pare → **re-sign koro, harao na**: XMP-e `DigitalSourceType` (`trainedAlgorithmicMedia` / AI edit-e `compositeWithTrainedAlgorithmicMedia`) + alt text → tarpor `c2patool final.webp -m manifest.json -p original_openai.png -o final_signed.webp` (actions: cropped, resized, color_adjustments, transcoded, placed) → `c2patool --info` diye verify. CDN-e "Preserve Content Credentials" on.
- 2.5 output-er C2PA `softwareAgent gpt-image 2.0` dekhay: model version nijer log theke nao.
- **Alt text final image theke** (prompt theke na), human review; decorative = `alt=""`; chart = short alt + long description; text-over-image contrast ≥4.5:1; image-of-text-er bodole live text prefer (WCAG 1.1.1 / 1.4.3 / 1.4.5).

### 13.5 Legal + platform note (legal advice na; research-e paowa)

- **Likeness:** consent chara real manush-er authenticity-confusing image OpenAI policy-te nishedh; AI alteration cover kore emon model release nao.
- **Biometric:** QA-te face embedding = biometric data (GDPR Art. 9, Illinois BIPA) → consent ba judge-based QA.
- **EU AI Act Art. 50** (2026-08-02 theke apply): deepfake disclose; machine-readable marking → mark kokhono strip na.
- **Marketplace:** Google Merchant Center AI image-e IPTC `TrainedAlgorithmicMedia` tag chay; main image / real-estate staging truthful hote hobe; AI persona diye fake testimonial (FTC 16 CFR 465) nishedh.
- **Copyright:** shudhu AI output (human authorship chara) US-e register hoy na (Copyright Office report 2025; *Thaler v. Perlmutter*) → human-authored layer (vector logo, typography, arrangement) rakho + document koro.

---

## 14. Cost + latency strategy

### 14.1 Cost formula (verified, 12/12 published data point match)

`output_tokens = ceil(G × round(G × short/long) × (2,000,000 + W×H) / 4,000,000)` · price $30 / 1M image output token.
G: gpt-image-2 → low 16 / medium 48 / high 96 · 2.5 → low 16 / medium 24 / high 48 / xhigh 64 / max 96.

| 2.5 size | low | medium | high | xhigh | max |
|---|---|---|---|---|---|
| 1024×1024 | $0.006 | $0.013 | $0.053 | $0.094 | $0.211 |
| 1536×1024 | $0.005 | $0.010 | $0.041 | $0.074 | $0.165 |
| 2560×1440 | $0.006 | $0.014 | $0.055 | $0.098 | $0.221 |
| 3840×2160 | $0.011 | $0.026 | $0.100 | $0.178 | $0.400 |

(+ input text token $5/1M, input image token $8/1M: edit-e reference image thakle beshi; partial image +100 token each.)

### 14.2 Strategy

1. **Explore cheap:** 4 draft × `low` ≈ $0.02–0.03 total.
2. **Final expensive, ekbar:** winner-ke `high`/`xhigh`-e.
3. **Metric = cost per accepted image** (total spend ÷ QA-pass image), per-request cost na.
4. `auto` quality production-e na.
5. Bulk + deadline nai → **gpt-image-2 Batch (50% off)**.
6. Codex built-in → ChatGPT plan-er limit **3–5× druto** khay: boro batch-e API key path.
7. Latency: Flare < Sunburst; jpeg fastest; square fastest; >2560×1440 slow + unreliable.

### 14.3 Speed architecture: measured (2026-09-23, 10 complex brief, Codex built-in image tool)

**Shomoy kothay jay:**

| Step | Shomoy | Notes |
|---|---|---|
| Image tool (`image_gen`) | 30–230 s per image | Backend variance. Median ~48 s; kichu call 120–230 s |
| Codex agent overhead (per image, agent mode) | ~140 s | Skill pora, xhigh reasoning-e prompt rewrite, self-QA view, retry, copy |
| Self-QA retry (agent mode) | Prai protita run-e 2nd image call | Image shomoy prai 2 gun |
| Independent judge | high ~65 s, medium ~44 s | 12-ta judge ekshathe 81 s: concurrency kono problem na |

**Tai design (fast mode, skill-er default):**
1. **Prompt-time judge:** brief + failure-mode library-er check (judge ja check korbe tai) prompt-ei. Photo rule shudhu photo brief-e; illustration / infographic-e na (negation/conditional priming edate).
2. **Parallel generation:** protita image nijer lean Codex session-e (low effort, skill pora nei, self-QA nei, copy nei). Shob job ekshathe → 10 image ≈ shobcheye slow image-er shomoy.
3. **Parallel candidate:** complex brief (≥6 check ba known risk) → 2 candidate ekshathe. Sequential retry-er cheye druto, same best-of-2 benefit.
4. **Parallel judge (medium):** protita candidate-er alada fresh session; medium ar high 6/6 same pass/fail.
5. **Verdict policy:** quality gate (physics, hand-object, anatomy, text, extras) + sob score ≥ 4 → pass; shudhu brief-detail mismatch → `PASS_WITH_NOTES` (fix round kharach hoy na).
6. **Fix only what can be fixed:** protiti candidate ekoi quality rule bhangle fix round skip → `model_limit` report (retry-te 0/6 thik hoyechilo).

| Run (same 10 brief) | Wall time | Pass (PASS / PASS_WITH_NOTES, calibrated judge) |
|---|---|---|
| Agent mode (baseline) | 36.8 min | 5/10 |
| Fast, compiled prompt (v1) | 5.9 min | 4/10 |
| Fast, Codex art-director prompt (lite A/B) | 9.2 min | 3/10: prompt rewrite quality barayni, shudhu slow |
| Fast v3 (complex brief-e 2 candidate) | 7.7 min | 2/10 (verdict v1): brief_fidelity 4↔3 variance |
| Fast v4 (verdict v2 + fix-skip rule) | 3.9 min | 7/10, first-pass 6/10, mean score 20.7 vs 20.1, plan usage 1% vs 4% |
| Fast v5 (installed skill, lean sessions) | 4.4 min | 5/10, mean 20.2 |
| **Final v6 (+ early exit: prothom usable candidate jite, baki session cancel)** | **3.5 min (10.4×)** | **6/10**, mean **21.1** (sob run-er moddhe best), plan usage 1%, image call 16 vs 36 |

**Lean session flags:** automated session-e `-c features.memories=false`, `memories.generate_memories=false`, `features.chronicle=false`, `features.apps=false`, browser/computer use off → Codex start-up 14.5 s → 9.1 s, ar user-er Codex memory-te shoto shoto automated job jome na.

**Codex code-mode pitfall (fast mode-e shikha):** image_gen result `generatedImage(v)` diye na dekhale low-effort agent kokhono code chalate refuse kore ("image-generation instructions require returning results with generatedImage"). Reference image thakle age `view_image` (shudhu `detail` high/original chole). Prompt verbatim file theke pore: agent-ke prompt abar type korte dile output token-e shomoy jay.

**Loop-er shikkha (failure library nijeo over-strict hote pare):**
- "Suto/chain-er pura path dekha jabe" check dile judge natural occlusion-keo fail korto. Thik niyom holo: haat ba object-er pichone gele line-ta ekoi line-e abar ber hoy, bhanga, doubling ba bhasa end na thakle OK.
- "Wrench-er open jaw" check-e ring spanner-o fail hochhilo. Thik niyom: open jaw duti flat-e ba ring end nut ghire, dutoi thik.
- "Tilted" risk shudhu cup / glass / bowl nije helano thakle. Dhalar pitcher helano thakle risk na.
- Domain physics jog holo: latte art-e heart toirir somoy spout crema-r prai gaye lage.
- Simplified brief (risk element bad) diye ager 5-ta constant FAIL-er 3-ta sathe sathe pass (rickshaw, bicycle, boatman).

**Model-limit list** (perfect prompt-eo prai fail; dorkar na hole brief theke bad dao): helano cup/glass-e level liquid; ulto object nijer contact point-e balance; wrench-er jaw nut-e; haater bhitor diye suto-r continuity; 3+ exact text string; "shudhu ei 2-ta alo" type light restriction.

---

## 15. Agent operating procedure (SOP) + drop-in skill

> **Superseded:** ei section-er drop-in skill ar SOP `codex-imagegen` skill-er ager version. Ekhon `SKILL.md` + `references/cli.md` follow koro; nicher model/quality/size routing shudhu `--engine api`-er jonno.

### 15.1 SOP: AI agent ei order-e kaj korbe

| Step | Agent ki korbe | Reference |
|---|---|---|
| 0. Classify | Generate na edit? Asset type (genre)? Ekta na series? → use-case slug | 8, 14.7 (report) |
| 1. Brief check | Must-have: exact text, product/brand reference, deliverable size/format/destination. **Essential missing hole shudhu tokhon jiggesh**; noile safe default | 12.1 |
| 2. Surface | Codex built-in (key nai, size control nai) · Images API (full control) · Responses (multi-turn) · Batch (bulk gpt-image-2) | 3 |
| 3. Model | Draft = Flare · Final/edit/text/identity = Sunburst · Bulk = gpt-image-2 Batch · 1.x kokhono na | 3.1 |
| 4. Params | Valid explicit `size`, quality ladder, format, background; `input_fidelity` na | 3.2–3.4, 10 |
| 5. Prompt | I-S-S-C-L-M-M-T-X-O framework + (photo hole) Realism Formula + exact-text protocol + Constraints kokhono khali na; series-e Brand DNA / Style Lock / character bible verbatim | 4, 5, 7, 10 |
| 6. Generate | Explore 3–4 *alada* direction (`low`/`medium`) → select → refine (single change) → final (`high`+). **Shob image ekshathe (parallel)**: sequential loop na; complex brief-e 2 candidate parallel-e | 12, 14.3 |
| 7. QA | Deterministic check → judge rubric (protita image-er judge parallel-e) → 200% zoom; verdict v2 (PASS / PASS_WITH_NOTES / FAIL); fix shudhu quality fail-e, sob candidate ekoi rule bhangle `model_limit` report; ≤2 chained edit; pixel-exact = composite-back | 9, 11, 14.3 |
| 8. Post | Exact deliverable crop, sRGB, format, alt text; C2PA master rakho | 13 |
| 9. Report + log | Final path(s), final prompt, model/params, QA result, cost; manifest save | 13.3 |

**Hard rules (kokhono na):**
1. Chupchap model switch / downgrade.
2. Claim, price, certification, endorsement, testimonial, ba copy nijer theke banano.
3. Generated image-ke identity reference hishebe use.
4. Provenance (C2PA/SynthID) strip / detector evade.
5. Real, identifiable manush-er deceptive/non-consensual image; onner trademark/logo.
6. Final logo/legal text model-er upor chhere dewa (vector/live text composite koro).
7. "HTTP 200" ke success dhora: file khule QA na kore deliver.

### 15.2 Drop-in `SKILL.md` (Codex / Claude Code)

Install (tumi chaile ami kore dite pari):
- Codex: `~/.agents/skills/gpt-image-mastery/SKILL.md` (`.system/imagegen` edit koro na; update-e wipe hoy)
- Claude Code: `~/.claude/skills/gpt-image-mastery/SKILL.md`
- Ei master doc-ta pashe `references/master.md` hishebe rakho (progressive disclosure: SKILL.md choto, detail reference-e).

````markdown
---
name: gpt-image-mastery
description: Professional-grade image generation and editing with OpenAI GPT Image (gpt-image-2.5-sunburst, gpt-image-2.5-flare, gpt-image-2). Use for photoreal, natural-looking product, lifestyle, portrait, food, interior, fashion, UGC, ad, poster, infographic, UI mockup, logo and series/character work, and for precise edits (inpainting, identity/product preservation, background swap, relight, text localization, outpaint, transparent cutouts). Covers model/quality/size routing, a structured brief, a realism formula, exact-text protocol, edit contracts, composite-back, QA rubric and delivery.
---

# GPT Image Mastery

Read `references/master.md` sections as needed; this file is the operating core.

## 1. Route
- Draft/explore: gpt-image-2.5-flare, quality low|medium.
- Final photoreal, edits, identity/product/label fidelity, dense text: gpt-image-2.5-sunburst, quality high (xhigh|max only to fix a named gap).
- Bulk without deadline: gpt-image-2 via Batch (50% off; 2.5 has no Batch).
- Never use gpt-image-1 / 1.5 / 1-mini (shutting down). Never silently switch models.
- In Codex without an API key, use the built-in image tool (no size/quality control): state aspect ratio in the prompt, then crop.

## 2. Parameters
- size: auto or WxH with both edges multiples of 16, max edge 3840, ratio <= 3:1, 655,360–8,294,400 px; > 2560x1440 is experimental. 1920x1080 is invalid: generate 1920x1088 and crop.
- quality explicit (never auto in production). output_format png (master) / webp or jpeg (delivery). output_compression only for jpeg/webp.
- background transparent => png/webp + isolated-subject prompt with no backdrop words (prompt overrides the flag); verify alpha in code.
- Do not send input_fidelity to gpt-image-2 or 2.5. partial_images only for live previews (+100 tokens each).

## 3. Brief (labeled lines; omit empty ones; Constraints never empty)
Intent / Scene / Subject (exact counts, pose, gaze) / Action mechanics (anything moving: source -> path -> target) / Object anatomy + Grip & load (anything held, carried, lifted or poured: handle or "no handle", spout, neck, base, weight; which hand, named by frame position, touches which existing part, grip type, what carries the weight) / Camera (medium, shot, angle, lens feel, DoF) / Light (source, direction, quality, color cast) / Materials & texture / Color & mood / Text (verbatim, count, font, placement) / Constraints (keep + exclude) / Output (aspect, negative space, transparency).
Specificity: if the request is detailed, only normalize it; if generic, add only framing/use/layout detail. Never add people, props, brands, slogans, claims or copy the user did not imply.

## 4. Realism formula (photographic work)
mode word ("photorealistic" / "real photograph" / "phone photo") + capture conditions (device or lens feel, angle, handheld) + ONE motivated light with color cast + texture scaled to distance + 1–3 located imperfections with causes + exact inventory counts + plain exclusions (no retouching, no studio polish, not a 3D render, no extra text/logos). For any motion add an Action mechanics line: source -> path -> target (e.g. liquid leaves only over the tilted rim and lands inside the cup). For anything held add Object anatomy + Grip & load: hands touch only parts that exist (no phantom handles), heavy objects rest on a hand, forearm, hip or surface under their center of mass, close to the body, with visible load cues (spread fingers pressing in, wrist bent back, forearm tension, counter-lean).
Delete hype words: 8K, masterpiece, ultra-detailed, flawless, sharp focus, Unreal/Octane. Avoid "cinematic/golden/vintage" unless intended (warm cast). Keep <= 5 prominent faces.

## 5. Exact text
Quote copy verbatim, say how many times it appears, give font style + placement, spell rare words letter by letter, "no other text". Proofread character by character. For guaranteed copy/logos/data: generate a text-free base and composite live text/vector marks.

## 6. Edit contract
First input = edit target (mask applies to it; alpha 0 = edit). Faces/products first; role-list every reference (what to take, what not to take).
"Change ONLY X. Keep exactly: <identity, geometry, label text, layout, camera, light, white balance, background>." Describe the full final image for masked edits.
One change per round, from the original or last approved composite; max 2 chained generations. Pixel-identical regions: composite back. Short identity lock ("same person, do not redesign, beautify or average"); never use generated images as identity references.

## 7. Workflow
Brief -> explore 3–4 distinct directions (low/medium) -> select -> refine (single change) -> final (high+) -> QA -> post -> log.
Speed: generate every image of a request concurrently (never one by one), judge them in parallel, fix only quality failures, and stop retrying a rule every candidate broke (report it as a model limit and simplify the brief).

## 8. QA (gate, then grade; verdict computed, never averaged)
Gates: instruction following, exact text (OCR set-diff, normalized dashes/quotes), spec (size, alpha), safety.
Graded 0–5: realism, artifacts, edit intent, non-target invariance, identity, product fidelity, brand fit (ship >= 4 for brand-critical; if unsure, score lower).
200% zoom: hands, text, catchlights vs light source, shadow direction + contact shadows, cloned faces, halos, waxy/etched skin, color cast, unrequested elements, physics trace (every pour/splash/reflection/shadow has a correct source and target), hand-object trace (each hand -> an existing part -> grip -> role; each heavy object's load path).
Fix routing: a local defect -> one "change only" edit; a pose, grip, anatomy, camera or composition defect -> regenerate with the correction added to the brief.
Fix one named failure per round; record requested vs actual output dimensions.

## 9. Deliver
Crop to exact deliverable, sRGB, webp/jpeg delivery + png master, alt text from the final image, keep provenance (never strip C2PA/SynthID). Report final paths, final prompt, model/params, QA result and cost.

## 10. Never
Invent claims/prices/endorsements/testimonials; deceptive or non-consensual images of real people; other brands' logos or copyrighted characters; provenance removal or detector evasion; delivering without opening and checking the file.
````

---

## 16. Safety, ethics, IP, provenance

### 16.1 Korbe na (hard line)

- Real, identifiable manush-er **deceptive / non-consensual** image (fake event, fake endorsement, intimate content).
- Minor-der kono sexualized content: absolute na.
- **Fake review / testimonial / "real customer" claim**: UGC-style image ad-e "actual customer" hishebe present kora deceptive.
- Onner **trademark/logo, copyrighted character**, ba artist-er signature style "same copy": "original, non-infringing" bolo.
- **C2PA metadata strip, SynthID watermark defeat, AI-detector evade**: ei doc-e eta include kora hoy nai; eta policy-violating ar misinformation-e use hoy.

### 16.2 Korbe (professional practice)

- Real person-er identity-preserve edit → **consent** nao.
- Brand asset → client-er dewa logo/product image reference hishebe (generate kore brand logo banaio na).
- Platform-er AI-disclosure rule follow koro (ad/social platform policy).
- `moderation_blocked` hole prompt legit kina dekho, rephrase koro: filter "trick" korar chesta na.
- Historical/news-like scene-e "illustrative / AI-generated" context dao.

### 16.3 Realism ≠ deception

Ei doc-er "ultra-natural, not-AI-looking" technique **photographic craft**: product, lifestyle, editorial, architecture-e real camera-r moto quality anar jonno. Target holo *believable craft*, *manush-ke thokano* na.

---

## 17. Ranking: ki shobcheye beshi kaje lage

### 17.1 Top 25 technique (output quality-te impact onujayi)

Source: 4-ta research track (OpenAI official plugin + cookbook, 17 community skill, 1,150-prompt corpus, editing/QA research) cross-rank kora.

| # | Technique | Keno top | Kotha theke |
|---|---|---|---|
| 1 | **Exact content pixel-er baire rakho**: text/logo/data/safe zone deterministic composite; image = treatment | Text rendering #1 production failure | OpenAI creative-production, Higgsfield, yingzao |
| 2 | **Labeled brief, Constraints kokhono khali na** + specificity policy | Drift + invented element bondho | Official guide, Codex imagegen, wuyoscar, smixs |
| 3 | **Realism = capture condition, adjective na** (de-slop; hype word bad; ≥3 located imperfection) | Corpus data: real-looking prompt-gulo capture describe kore | Cookbook, smixs, buluslan, corpus analysis |
| 4 | **Edit contract**: "change ONLY X" + preserve list + ek change/round + original-e anchor | Edit-er ashol kothin ongsho = preservation | Official, buluslan, cookbook evals |
| 5 | **Composite-back** pixel-exact region-e | Ekmatro guarantee | Official guide |
| 6 | **Reference role list + short identity lock**; generated image identity ref na | Identity drift + lookalike bondho | Official, baoyu, AlekseiUL |
| 7 | **Acceptance age + gate-then-grade, verdict code-e** | "Bhalo lagche" theke measurable | wuyoscar, Image Evals cookbook |
| 8 | **Explicit model/quality routing** (Flare draft, Sunburst final; `auto` na) | Quality + cost duitai control | Official, buluslan, shinpr |
| 9 | **Diversity by construction**: 3–4 alada axis-e direction | Same prompt re-roll = same default | product-design `ideate`, creative-production |
| 10 | **Anchor-locked consistency** (canonical base, character sheet, Style Lock) | Series-e drift bondho | hatch-pet, buluslan, cookbook |
| 11 | **OCR set-diff** (normalized) text gate | Judge "exact match" bole bhul korte pare | Image Evals cookbook |
| 12 | **Transparency protocol**: native alpha + backdrop-word-free prompt + code-e alpha verify | Painted checkerboard/halo dhora pore | Transparent cookbook, Wangnov |
| 13 | **Exact inventory count** | Extra object/cloned face kome | YouMind, freestylefly |
| 14 | **Chain limit ≤2 + fresh session** | Degradation + tiling artifact bondho | Community (forum, apipass) |
| 15 | **One motivated light (source+direction+color cast)** | Flat AI light bhange | Photography craft, corpus |
| 16 | **AI-tell audit + counter-prompt** (8–17 tell) | Systematic realism fix | buluslan, research |
| 17 | **Deterministic post**: crop/pad (stretch na), sRGB, format | Exact deliverable, color thik | yingzao, editing research |
| 18 | **Pilot before batch** (1 sample approve → identical method) | Batch-wide failure bondho | codex-ppt, Adobe pattern |
| 19 | **Best-of-N sequential + escalation ladder** | Cost-efficient quality | Editing/QA research |
| 20 | **Brand DNA / Campaign Style Lock block** | Collection-wide consistency | Transparent cookbook, buluslan |
| 21 | **Receipt: requested vs actual** (dimension, model, hash) | Codex backend size ignore kore | AlekseiUL, baoyu |
| 22 | **Reverse-prompting** (critical 3–5 detail prothom tritiyangshe) | Reference match | wuyoscar, smixs |
| 23 | **"Decision being supported" line** | Asset-er purpose-e focus | creative-production |
| 24 | **Negative catalog** ("generic AI atmosphere": bokeh orb, wispy ribbon, stock haze) | Cliché bondho | build-web-data-visualization |
| 25 | **Real date-e mock data anchor** (UI) | Believable UI | product-design |

### 17.2 Official resource ranking (mastery-r jonno kon-ta age porbe)

| # | Resource | Keno |
|---|---|---|
| 1 | [Image prompting guide (GPT Image 2.5)](https://developers.openai.com/api/docs/guides/image-prompting) | Model choice, migration, 24 official example |
| 2 | [Image generation guide](https://developers.openai.com/api/docs/guides/image-generation) | Parameter, mask, limit, error |
| 3 | [Cookbook: GPT Image models prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide) | Fundamentals + photoreal "natural" section |
| 4 | [Cookbook: Image evals](https://developers.openai.com/cookbook/examples/multimodal/image_evals) | QA rubric + judge structure |
| 5 | [Cookbook: Transparent image assets](https://developers.openai.com/cookbook/examples/multimodal/transparent-image-assets-for-campaigns-and-presentations) | Brand DNA suffix, alpha QA |
| 6 | [openai/plugins → creative-production](https://github.com/openai/plugins/tree/main/plugins/creative-production) | Contracts, prompt packs, board |
| 7 | [openai/plugins → product-design](https://github.com/openai/plugins/tree/main/plugins/product-design) | Ideate + design-qa gate |
| 8 | Codex `imagegen` skill (`~/.codex/skills/.system/imagegen/`) | Operational workflow, taxonomy |
| 9 | [openai/skills → hatch-pet](https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet) | Consistency engineering + deterministic QA |
| 10 | [Cookbook: High input fidelity](https://developers.openai.com/cookbook/examples/generate_images_with_high_input_fidelity) | Face/brand preservation concept (purono model) |

---

## 18. Mastery path: level + practice drill

### 18.1 Level ladder

| Level | Nam | Parbe | Proof |
|---|---|---|---|
| L1 | Operator | Tool/API chalate pare | Valid request, file save |
| L2 | Prompter | Labeled brief, exact text, constraint | Text-exact poster first try-e ≥70% |
| L3 | Photographer | Light, lens, material, composition direct korte pare | Blind test-e manush real photo theke alada korte pare na (≥50%) |
| L4 | Retoucher | Mask, composite-back, identity/product lock, outpaint | Edit chain-e non-target drift 0 (composite-er por) |
| L5 | Director + QA engineer | Rubric, judge, regression, cost, series system | Cost per accepted image track; ≥90% judge-human agreement |
| **Top 1%** | L5 + taste | Protita output-er "keno" bolte pare | Portfolio + measurable pass rate |

### 18.2 Practice drill (protita 30–60 min)

1. **Light study:** same subject, 5 light setup (Section 6.1) → realism score compare.
2. **Hype vs capture A/B:** "8K masterpiece" prompt vs Realism Formula prompt → judge realism score + human blind pick.
3. **Exact-text poster:** English + Bangla + number/punctuation → OCR set-diff; fail hole text-free base + composite.
4. **Packshot from reference:** real product photo → Sunburst edit → label OCR exact → logo vector composite.
5. **Identity edit chain:** 3-step edit → drift measure → composite-back diye 0 drift.
6. **Glass cutout:** transparent glass bottle → alpha health check (Section 11.4) → defringe.
7. **Character series:** anchor sheet → 4 scene (branch, chain na) → pairwise consistency ≥4.
8. **UGC vs studio:** same product duita style-e → AI-tell audit (Section 5.3).
9. **Outpaint:** 1024² → 2048×1024 → 3072×1024 step-e, seam check.
10. **Regression mini-suite:** 20 golden prompt × Flare/Sunburst × k=3 → pass rate, latency, cost/accepted table.
11. **Physics drill:** pour / splash / reflection scene 3-ta model-e → protita output-e physics trace → fail hole T16 fix.
12. **Hand-object drill:** 5-ta object (handle-chara kolshi, balti, karahi, boti, cha-er kettle) → Object anatomy + Grip & load line soho generate → hand-object trace + load path → fail hole T17 ba regenerate; haat frame position diye likhe left/right swap bondho koro.

---

## 19. Reference list

**OpenAI official**
- Image prompting guide: https://developers.openai.com/api/docs/guides/image-prompting
- Image generation guide: https://developers.openai.com/api/docs/guides/image-generation
- Responses image tool: https://developers.openai.com/api/docs/guides/tools-image-generation
- Model pages: https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst · …/gpt-image-2.5-flare · …/gpt-image-2
- Pricing: https://developers.openai.com/api/docs/pricing · Deprecations: https://developers.openai.com/api/docs/deprecations
- Content provenance: https://developers.openai.com/api/docs/guides/content-provenance
- Images & vision (detail levels): https://developers.openai.com/api/docs/guides/images-vision
- System card (Images 2.5): https://deploymentsafety.openai.com/chatgpt-images-2-5

**OpenAI Cookbook**
- GPT Image models prompting guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- gpt-image-1.5 prompting guide: https://developers.openai.com/cookbook/examples/multimodal/image-gen-1.5-prompting_guide
- Transparent image assets: https://developers.openai.com/cookbook/examples/multimodal/transparent-image-assets-for-campaigns-and-presentations
- Image evals: https://developers.openai.com/cookbook/examples/multimodal/image_evals · harness: https://github.com/openai/openai-cookbook/tree/main/examples/evals/imagegen_evals
- High input fidelity: https://developers.openai.com/cookbook/examples/generate_images_with_high_input_fidelity

**OpenAI skill / plugin**
- openai/plugins: https://github.com/openai/plugins (creative-production, product-design, build-web-apps, build-web-data-visualization, game-studio)
- openai/skills (deprecated; hatch-pet): https://github.com/openai/skills
- Codex imagegen (live): https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen

**Community skill** (Section 2.3 table-e shob link)
- wuyoscar/GPT-Image2-Skill · buluslan/gpt-image2-ecommerce · smixs/visual-skills · ningzimu/codex-ppt-skill · ConardLi/garden-skills · op7418/guizang-yingzao-skill · JimLiu/baoyu-skills · higgsfield-ai/skills · AlekseiUL/gpt-image-2-5-agent-kit · shinpr/mcp-image · Wangnov/gpt-image-2-skill

**Prompt library**
- https://github.com/freestylefly/awesome-gpt-image-2 · https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts · https://github.com/YouMind-OpenLab/awesome-gpt-image-2 · https://github.com/ZeroLu/awesome-gpt-image

**Realism / community finding**
- Hedra (real-photo prompting): https://www.hedra.com/blog/make-ai-images-look-like-real-photos-prompting
- getimg (fake skin): https://getimg.ai/blog/why-ai-skin-looks-fake-how-to-make-it-real
- VibeDex quality tiers: https://vibedex.ai/blog/gpt-image-2-quality-tier-comparison-2026
- Everypixel GPT Image 2 test: https://research.everypixel.com/gpt-image-2-0/
- apipass tiling artifact: https://apipass.dev/blogs/gpt-image-2-launch-tiling-texture-artifact
- Curious Refuge review: https://curiousrefuge.com/blog/open-ai-gpt-image-model-review
- Arena leaderboard: https://arena.ai/leaderboard/text-to-image · Artificial Analysis: https://artificialanalysis.ai/image/leaderboard/text-to-image
- OpenAI forum, plastic faces: https://community.openai.com/t/gpt-image-2-produces-plastic-looking-faces-in-product-edit/1394653 · quality regression: https://community.openai.com/t/drastically-worse-gpt-image-2-quality-over-the-last-24-hours/1383092 · mask/transparency: https://community.openai.com/t/understanding-how-gpt-image-models-on-edits-see-mask-and-transparency/1381752 · edit degradation: https://community.openai.com/t/bug-edited-images-significantly-degrade-in-quality/1395704
- Vercel mask-drift measurement: https://github.com/vercel/ai/issues/14360

**Hand-object / grasp / load (Section 5.3d)**
- Qwen-Image-Bench (2026): https://arxiv.org/html/2605.28091v1
- Cutkosky 1989, grasp choice: https://bdml.stanford.edu/twiki/pub/Seabed/LiteratureReview/Cutkosky_-_1989_-_On_Grasp_Choice_Grasp_Models_and_the_Design_of_Hands_for_Manufacturing_Tasks.pdf
- Feix et al. GRASP taxonomy: https://www.csc.kth.se/grasp/taxonomyGRASP.pdf
- Guiard 1987, bimanual roles: https://www.lri.fr/~mbl/ENS/FONDIHM/2013/papers/Guiard-JMB87.pdf
- Wrist posture vs grip strength: https://pubmed.ncbi.nlm.nih.gov/1538102/ · wrist torque norms: https://pmc.ncbi.nlm.nih.gov/articles/PMC4322806/
- Commonsense-T2I: https://arxiv.org/abs/2406.07546 · PhyBench (T2I physics judge): https://arxiv.org/abs/2406.11802
- Hand-object generation survey (2026): https://arxiv.org/html/2607.28394 · HOI-Swap: https://vision.cs.utexas.edu/projects/HOI-Swap/ · HandEval: https://arxiv.org/abs/2510.08978
- Negation in T2I prompts: https://arxiv.org/abs/2404.15154 · VLM counting bias: https://arxiv.org/abs/2505.23941
- Water culture in Bangladesh (kolshi, bodna): https://www.farhanasultana.com/wp-content/uploads/2019/07/Sultana-Water-Culture-and-Gender-Analysis-from-Bangladesh-2012.pdf · Bira: https://www.ebanglalibrary.com/167019/%E0%A6%AC%E0%A6%BF%E0%A6%A1%E0%A6%BC%E0%A6%BE/ · Boti: https://gastronomica.org/2013/04/16/the-bengali-bonti/

**Provenance / legal / platform** (legal advice na)
- c2patool: https://github.com/contentauth/c2patool
- Cloudflare Preserve Content Credentials: https://developers.cloudflare.com/images/optimization/transformations/preserve-content-credentials/
- Google Merchant Center AI image: https://support.google.com/merchants/answer/14743464
- EU AI Act Art. 50 guideline: https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-transparency-obligations

**Companion doc (ei folder-e):** `GPT-Image-Generation-Deep-Research-Report.md`: API parameter, model, pricing, Codex internals-er full reference.
