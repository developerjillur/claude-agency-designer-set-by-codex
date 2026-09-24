# R9: Single-prompt pro designs with GPT Image 2 / 2.5 — the design-dossier method

## Summary: 15 rules for single-prompt pro designs

1. **Open with the artifact, not the subject.** Line 1 names the deliverable, platform, aspect in words and "one finished flat design filling the canvas, not a mockup or a sheet of options". A model with no stated structure invents a centred subject on a plain ground. [1][4][15][16]
2. **Decide the idea before writing the prompt.** Write one visual idea ("X shown as Y") that passes a one-jump test (the reader gets it in a single mental step) and a swap-the-logo test (it fails for a competitor). [21][66][67]
3. **Commit every layout decision the model would otherwise make.** Give zones with % bounds, one alignment axis, margins, the largest element, eye path 1→2→3, and what sits nearest the camera. Current models render text well; layout and hierarchy are now the weak point. [15][62][63]
4. **One focal event, one quiet release zone, one deliberate disruption.** Never centre everything, and never let a centred subject and a centred title float apart like "two islands". [18][23][R4]
5. **Make type and image touch.** Set the headline behind the subject, let it cross or lock to the object, or make the type the object; use a scale jump of 5–12× between the largest and smallest text. This is what separates "designed" from "text pasted on a picture". [6][18][23][26]
6. **Describe typography rather than naming fonts.** Give class, weight, width, contrast, case, tracking and size relative to the canvas; use ≤2 families, ≤4 sizes and one axis. Expect a similar feel, never the exact brand face. [1][15][31]
7. **Write an exact-copy contract.** Quote every string once in its final casing and say "only these strings; no paraphrase, re-casing, hyphenation or extra words". Never leave a placeholder unfilled: models fill `[DATE]` with a fabricated date. [1][4][15][6]
8. **Colour in words, by role and share.** State the ground, support and one accent (≈60/30/10), and name the element that carries the accent. Use hex only with a "never print colour codes" guard or inside a text-free swatch image. [16][17][R3]
9. **Light before material.** Give source, direction, quality and temperature, then how each surface responds. Ask for contact shadows that agree with the light, and state a depth-of-field decision. [15][4]
10. **References: 1–4 images, each with one job.** Put a numbered manifest in the first lines, add a conflict rule, and for style references name 2–4 visible mechanisms plus a "must replace" list. [1][15][19][23]
11. **Keep faces, products and logos exact with preservation lists longer than the task.** Plan to composite real pixels (logo PNG, product cut-out) when the check fails; exact logo reproduction is unreliable. [1][6][51][60]
12. **Anti-AI-look by naming the model's strong priors.** Use a short, targeted do-not list (sparkles, badges, glow, gradients, centred stack, invented taglines). Phrase reserved areas positively rather than as bans, delete booster words, and name a style anchor. [15][24][55][R4]
13. **Variety comes from recipes, not re-rolls.** Rotate concept structure × layout archetype × focal type × type mode × palette roles × finish. Keep a ledger and differ from the last 6 on ≥3 axes. There is no seed parameter. [3][17][23][24][44]
14. **Pick the engine per job.** Sunburst for arrangement and text (API, `high`/`xhigh`); Flare for light-led imagery; Codex route = gpt-image-2 at `auto`. Use a fresh session per asset. Spend the prompt on decisions, not QA checklists (median community prompt ≈2.6k characters). [15][16][23][R3]
15. **Verify in a fixed order, then escalate in small steps.** Check text → protected elements → composition → light and material → style. Escalate: point edit (≤2, composite back) → regenerate with one named correction (≤2) → shorten the text → hybrid typesetting. Point edits succeed; restructuring edits break. [10][15][49][R3]

---

**Scope.** One generation of a *finished* social post, story, carousel slide, YouTube thumbnail, banner or cover, poster, flyer, infographic or special-day post, made from a "design dossier" prompt plus attached references, then verified and fixed with targeted edits. It does not repeat R3 (text tiers, route table, text gate, edit mechanics, failure table), R1/R2 (repo catalogues) or R4 §3–5 (craft rules, AI-tell table); it cites them as [R1]–[R7].

**Evidence tags:** OFF = OpenAI or Anthropic docs or code · COM = community repo, forum or blog (not verified by us) · VEN = vendor marketing numbers · DER = our own derivation · **UNVERIFIED** = could not be confirmed; do not hard-code it. All sources were accessed 2026-09-23. Source material is paraphrased; the example prompts in §2.12 are our own, modelled on the cited structures.

---

## 1. Repositories and guides: what each teaches, what to reject

Stars, push dates and licences are in the Repositories table at the end. Only things new since R1/R2, or specific to single-prompt design, are listed here.

### 1.1 Official

- **OpenAI image prompting guide (2.5) [1] + Cookbook guide [4]** (OFF). *Adopt:* labelled sections (scene → subject → details → constraints) plus the intended use; quoted text with position and typography; letter-by-letter spelling of rare words; stated counts and "no extra text"; numbered input images, each with a purpose; "change only X" plus a preserve list repeated every turn; composite back any pixel-critical region; Sunburst when GPT Image 2 falls short, Flare for latency; ads written as a creative brief (brand, audience, vibe, scene, exact tagline) with taste decisions left to the model inside it. *Reject:* the official examples' own tells ("tasteful bokeh lights" on the holiday card; Inter named in the slide example, which [24][38] flag as a default font).
- **API reference [3]** (OFF): `n` 1–10; **no `seed` parameter**; prompts ≤32,000 characters; edits ≤16 images with `input_fidelity`. The Codex skill says gpt-image-2 always uses high input fidelity [5].
- **Codex bundled imagegen skill [5]** (OFF): the Codex agent restates our prompt as a labelled spec (`Use case / Asset type / Primary request / Scene/backdrop / Subject / Style/medium / Composition/framing / Lighting/mood / Color palette / Text (verbatim) / Constraints`). It normalises specific prompts without adding slogans or palettes. *Adopt (DER):* hand Codex the dossier already in these labels.
- **OpenAI `creative-production` plugin [6]** (proprietary; ideas only). A 25-family image-ad archetype pack: UGC offering thumbnail, surreal floating product, luxury editorial still life, direct-response card, problem/solution split, cinematic action hero, UI overlay, exploded benefit diagram, shelf battle card, minimal premium whitespace, collage scrapbook, noir spotlight, cold splash, cozy home ritual, streetwear drop, OOH takeover, e-commerce bundle, testimonial wall, founder desk, retro print classified, sticker-badge native, AI world extension, material proof, launch countdown, hands demo. Each family has copy rules, constraints and an avoid list. Two recurring rules: set the headline *behind the person or subject for depth*; add no subtitles, captions, footers or small text unless exact copy was supplied. Its exact-content contract gives exact text, data and logos to deterministic layers. **OpenAI's own production plugin does not trust single-prompt output for exact content; that is why §6 exists.**
- **`hatch-pet` [7]** (Apache-2.0): layout-guide images are *invisible construction references*, so no boxes, marks, labels or guide colours may appear in the output. Long policy and QA rules stay out of the image prompt.
- **Anthropic `canvas-design` [11]** (R1 §C.1). *Adopt:* philosophy before canvas, a subtle conceptual reference, containment, and a "refine, don't add" pass. *Reject for commercial work:* the 90/10 art-object bias, the thin-type default and its diagrammatic house style, which now reads as an AI tell. **`frontend-design`** (R2 B8): the five AI-default clusters and "spend boldness in one place".

### 1.2 Full-AI poster and ad skills (new since R2)

- **`gc-minimal-zine-poster` [17]** (7.2k★, MIT) — the most complete single-prompt poster compiler found.
  - *Adopt:*
    - the field order canvas → attention geometry (empty-space %, cluster size and position) → photo contract → one metaphor → focal-element form → material → typography → colour (hue, carrier, share) → reproduction and mood → hard avoids, written as four paragraphs;
    - a variation engine: 10 layout families × focal forms × type modes × textures. Each new recipe changes layout, focal form and type mode; a batch of ≥4 uses ≥3 families;
    - photo roles (edit target / reference / supporting insert) with High, Medium or Low preservation;
    - reference analysis split into fixed system, variable system and "sample residue" that is never reused;
    - regenerate once, then report the limitation.
  - *Reject:* the zine look as a default.
- **`mono-color-skill` [18]** (3.3k★, MIT).
  - *Adopt:*
    - a YAML recipe manifest before the prompt;
    - a five-paragraph compiler: canvas and ink → composition → subject → type and words → material and avoids;
    - an **originality firewall**: ≥4 structural changes from any reference;
    - composition rules: one object at 45–80%; the headline crosses or locks to it; paper cuts through the image; one manual gesture; a 5–12× type-scale jump; never centre everything; no safe headline-left / photo-right split;
    - after one failed text retry, fall back to a text-light base.
  - *Reject:* identical inputs → identical recipe when a feed needs variety (use §4.4).
- **`poster-style-transfer` [19]** (47★, MIT). *Adopt:*
  - Hard lock / Soft lock / Must replace;
  - the order intent → reference role → theme → locked layout → type → hero → props → colour → light → exact text → avoids;
  - a weighted fidelity rubric: layout 25, type 20, hero 20, colour 15, graphic language 10, finish 10. Target ≥85; reject any structural score <70;
  - one targeted correction at the lowest high-weight dimension.
- **`guizang-yingzao-skill` [23]** (454★, no licence; method only). *Adopt:*
  - three fixed inputs: Image 1 edit target, Image 2 **one** dominant reference, Image 3 a neutral typeset scaffold (real copy, reading order, occlusion; no final style);
  - name 2–4 mechanisms visible in the reference and forbid only its identity, text, brand and symbols. If only adjectives remain, change the reference;
  - choose the recipe at maximum distance from a stored history;
  - "two islands" layouts are invalid;
  - one art direction per prompt;
  - priority: identity > thesis > reference mechanism > scaffold > original pixels.
- **`fantasy-dongfang-jianyuehaibao` [22]** (108★, no licence). *Adopt:*
  - Mode B: a complete poster *including the title* in one generation;
  - a wrong title is fixed by simplifying it and regenerating;
  - A/B/C modes (archive intervention / single material proof / type-structure experiment), judged as a group.
- **`xiaoma-durex-copywriter` [21]** (577★).
  - *Adopt:*
    - the one-jump rule: draw the association chain; more than one arrow fails;
    - 3–5 genuinely different schemes;
    - subject-type mix from 260 posters: product 30 / prop 40 / pure type 30%;
    - in a set, change skeleton and subject type before colours.
  - Its production route is hybrid, because Chinese text in pixels failed.
  - *Reject:* "enlarge one keyword in brand colour" as a default (an AI tell per R2 B8).
- **`image2-ads-studio` [20]** (48★, Apache-2.0).
  - *Adopt:*
    - a linter that rewrites vague labels ("premium style", "cinematic look", "Apple-like") into explicit composition, material, light, colour and type hierarchy;
    - a check that placement, light direction, materials, text areas and reference policy are all stated;
    - references used only structurally and de-branded.
  - *Reject:* its gallery's generic badges, seals and script accent lines.
- **`30x-image` [24]** (29★, MIT). *Adopt:*
  - one committed option per axis;
  - "taste" dials;
  - an anti-slop block;
  - carousels as N *independent* generations with a shared prefix. It reports that chained edits on slide 1 pulled gpt-image-2 into a "webpage" look (anecdote).
- **`taste-skill` [25]** (89.5k★, MIT). *Adopt:* the creativity-escalation rule (raise ≥3 of composition, type, scale contrast, concept, treatment, rhythm, framing, tension, structure) and its slop lists.

### 1.3 Prompt corpora and libraries

- **callirra atlas [15]** (104★; prompts CC BY 4.0) — the best evidence-bearing 2.5 corpus: 30 briefs of 400–4,500 words, each with the frame it produced and measured pixels.
  - **24 principles, ranked by damage:**
    - canvas before subject; % bands that never overlap; one focal point and a reading order; counts close;
    - light before material; materials by behaviour; two light temperatures; contact shadow and reflection;
    - exact text quoted once; one typographic budget; **fill every variable** (an unfilled template produced a fabricated date and venue);
    - reserve space rather than forbid; preserve list longer than the task; negation only for strong priors;
    - image order is semantic; one reference, one job; a conflict policy; name the miss.
  - **Controlled tier test** (5 prompts, `xhigh`; COM, n=5): Flare wins light-led images, Sunburst wins arrangement. Both rendered 5 HUD strings exactly; Sunburst set them in a tidier block.
- **youart corpus [16]** (111★; mixed rights, so techniques only).
  - 150 prompts, median 2,587 characters. Long prompts add parts, not clauses (≈ one line per decision).
  - 73/150 give an aspect ratio; 74/125 prose prompts quote text; 73 end with exclusions; **0 use hex**.
  - *Adopt:* name the artefact first; lock layout before style; JSON only for many distinct parts; vary one thing in A/B tests.
  - Key observation: failures have moved from garbled glyphs to *text you did not ask for*.
  - Smaller 2.5 corpora [39][40][41] add nothing new for design.
- **freestylefly [26]** (33k★): the **conceptual typography poster** template. The title is the hero; a figure at 40–70% overlaps, emerges from, is framed by or is hidden behind the letters; 4–6 colour roles; "single poster only". *Adopt* the structure; *reject* the case texts copied from X posts.
- **YouMind [27], EvoLink [28], ZeroLu [29]** (10k/17k/2k★): trend signals only.
  - Layered type behind the subject is a mainstream request.
  - Dense 20-string CJK posters are being attempted, with unknown success.
  - *Reject* "8K/ultra-detailed" boilerplate, fake phone numbers and prices, and copying.
  - YouMind's recommender skill [45] reflects the "pick a proven prompt, then remix" habit.
- **wuyoscar [30]**: a new reverse-prompt skill that turns a reference into words (3–5 critical anchors in the first third; brands as shapes and palettes; "reserved text area"). This is our describe-don't-attach path.
- **garden-skills title-safe poster [31]**: headline ≥60% of the area, ≤3 colours, ≤2 families, ≤6 decorative shapes. Defaults for the type-first archetype.
- **higgsfield [32]** (R1 A.1). *Adopt:* the 11-block thumbnail contract, the manifest line, the identity lock, 16 frameworks, single-scope edits. Its 2026-09-11 note keeps GPT Image 2 as the design default. *Reject:* the glossy "vivid" grade as a default for premium brands.
- **Marketplaces:** PromptBase [61] hides prompt text. Its trending ChatGPT-Image posters (retro, "out-of-bounds typography", surreal) are trend signals only.

---

## 2. The single-prompt template: what the evidence supports

### 2.1 Section order

| Source | Order |
|---|---|
| OpenAI guide / cookbook [1][4] | Labelled sections: scene → subject → details → constraints, plus the intended use |
| Codex skill [5] | scene/backdrop → subject → details → constraints → output intent (labelled spec lines) |
| callirra [15], wuyoscar (R2), youart [16] | Artefact, canvas and composition before the subject |
| gc-minimal [17] | canvas → attention geometry → photo contract → metaphor → form → material → type → colour → reproduction → avoids |
| mono-color [18] | canvas and ink → composition → subject → type and words → material and avoids |
| poster-style-transfer [19] | intent → reference role → theme → layout → type → hero → props → colour → light → text → avoids |

**Verdict (DER).** The sources do not conflict once "intended use" is read as the first line.

1. Artifact and format first, which satisfies both camps.
2. Reference manifest.
3. Idea.
4. Layout and reading order.
5. Imagery.
6. Type-image device.
7. Typography.
8. Exact text.
9. Colour.
10. Brand.
11. Style and finish.
12. Safe zones.
13. Constraints last.

Keep the exact-text block next to the typography block, so each string sits with its zone and style. Official and community prompts both put exclusions at the end [1][16].

### 2.2 Layout

- **Zones as proportional bands** ("top 12%", "left 62%"), each saying what it contains and that it never overlaps its neighbour. A vague "title at the top" produces a title somewhere [15].
- **One alignment axis** (e.g. every line of type hangs from the left margin at 7%) and outer margins ≥6–8% [15][R3].
- **Attention geometry.** Give the empty-space % and the focal element's size and position [17]. Typical ranges by genre:

  | Genre | Focal element | Empty space | Source |
  |---|---|---|---|
  | Zine | cluster 8–25% | 70–90% | [17] |
  | Editorial print | object 45–80% | 25–55% | [18] |
  | Thumbnail | subject 40–60% | — | [32] |
  | Type-first poster | headline ≥60% of the area | — | [31] |

- **Reading order.** Largest element, then the second and third stops [15].
- **Counts close.** Numbered modules, labels, leaders and arrows must agree [15].
- **Precision expectations.** Percentages steer the result; they are not pixel-exact. BizGenEval finds that "precise element localisation" still fails even for leading models [62]. OpenAI lists layout-sensitive placement as a limitation [2]. Check zones after generation with a tolerance: ±5% of the canvas is a house heuristic, **UNVERIFIED**.

### 2.3 Typography

- **Describe:**
  - class: grotesque, geometric sans, didone, slab, condensed, extended, mono;
  - weight, width and stroke contrast;
  - case and tracking (tight/normal/wide);
  - line breaks ("Line 1: … / Line 2: …");
  - alignment.

  Official prompts describe type this way ("bold sans-serif, high contrast, clean kerning") [1][4]. Transferring a poster's style means describing its type behaviour, not guessing the font [19].
- **Named fonts.** No test was found showing that GPT Image follows font names (**UNVERIFIED**). Use a well-known name only as a cue ("in the spirit of a 1960s Swiss grotesque"), never a licensed brand face. If the face must be exact, use hybrid [R3].
- **Relative size.** State cap height as % of canvas height (R3 house heuristic: headline ≥6%, other text ≥3%), or as a fraction of the canvas width ("spans about two thirds of the width"). Give secondary text as a fraction of the headline ("one third of its height") [15].
- **Scale jump.** 5–12× between the largest and smallest text [18].
- **Budget.** ≤2 families, a stated number of sizes (often 3–4), one axis [15][31].
- **Case.** Uppercase for public declarations, sentence or lowercase for intimate lines [18].
- **Treatments.** Forbid outline, gradient fill, drop shadow, bevel and glow on type unless the genre needs them [15][18][55]. The exception is the YouTube stack of thick stroke plus hard shadow, a deliberate convention [32].

### 2.4 Exact copy

- **Quote every string once**, in its final casing. Say it appears exactly once and forbid paraphrasing, abbreviation, re-casing, hyphenation and translation [1][15]. Casing errors are real:
  - Sunburst re-cased a word [R3 C7];
  - on PosterBench, Nano Banana Pro's poster-text accuracy fell to about 58% largely because it set requested lowercase in capitals (search-snippet summary of the PosterBench benchmark; not fetched; **UNVERIFIED**).
- **"Include ONLY this text (verbatim)"** is the official pattern [4]. Add the classes of text the model likes to invent: taglines, subtitles, captions, footers, dates, prices, badges, handles [6].
- **No unfilled variables.** Brackets get filled with plausible fiction [15].
- **Data risk.** gpt-image-2 recovered 70.0% of critical entities (numbers, amounts, proper nouns) in text-rich images (TextFake [65]). Keep prices, dates, phone numbers and statistics in hybrid, or verify every one [R3 Tier C].
- **Budgets.** Keep R3's Tier A (≤3 short Latin strings on Codex) and Tier B (4–8 strings via API with retries). The single-prompt route works *inside* these budgets.

### 2.5 Colour

- **Name colours in words with roles and shares:** ground ≈60%, support ≈30%, accent ≈10%. Say what carries the accent: the subject, a cut-out or a type block, not "a touch of" [17][18].
- **Hex codes.** Sources disagree:
  - fal recommends hex [48];
  - the 150-prompt 2.5 corpus uses none [16];
  - hex codes have been printed as labels [R3 C23].

  **Rule:** words by default. Put hex only with a guard line ("colour values are guidance only, never print them"), or in a text-free swatch image (see the Reference sheet recipe).
- **Protect the accent.** Words like "muted", "faded" or "pastel" meant for the paper drain the accent too; restrict them to the surfaces they describe [17].

### 2.6 Brand elements

- **Logo.** Exact reproduction by the model is unreliable. Reviewers report repeated failures, including an outdated logo version (anecdotes [60]). OpenAI's plugin treats logos as a high-risk fidelity area [6].
  - **Default:** reserve a clean, empty rectangle at the logo position ("a plain area about 12% of the width, bottom-right, nothing in it") and composite the real PNG or SVG afterwards.
  - Pass the logo as a reference only when it must live *inside* the scene (a shop sign, a 3D extrusion, a cup print). Then verify it against the source (§6) and fall back to compositing.
- **Brand look.** The distinctive assets (a colour block, a crop shape, a recurring device) matter as much as the logo. That is also what passes the swap test [68].

### 2.7 Imagery

- **Subject:** count, action, scale % of the frame, crop line (mid-limb, not at joints [R4]).
- **Place and people come from the client's market** (house rule: global by default).
- **Camera** as an appearance cue: viewpoint, distance, lens *look*, depth-of-field decision [1][15].
- **Photo mode.** Include "photorealistic" to engage the photo mode [4], plus the natural-photo cues: candid, real light, no retouch (house rule).
- **Light.** Source, direction, quality and colour temperature; a second, separate temperature if wanted; contact shadows at the scene's intensity [15].
- **Materials by behaviour** ("satin aluminium holding one clean specular line"), not by name [15].

### 2.8 Composition devices (the "designed, not pasted" layer)

| Device | How to say it | Evidence |
|---|---|---|
| Type behind the subject | "headline set large behind the person; the head overlaps part of the second word; the first letter and every word stay readable" (R4 rule: subject covers ≤20–30% of the letter area) | OpenAI ad pack [6], community [28], R4 §3.4 |
| Collision or lock | "the headline's last word crosses the object's edge" or "tucks tight against its contour" | [18][23] |
| Type as object | letters built from or carved into the subject matter | [26][31] |
| Scale contrast | a giant crop plus a small figure, or a huge word plus micro text | [18][R4] |
| Negative shape | paper or ground cutting through the image; a shared edge between type and contour | [18][23] |
| Depth | a foreground element cropping into frame | [15] |
| One gesture | a single circled word, arrow or registration mark; one family only | [18] |

Every device must serve the idea. A device with no job is decoration: apply the removal test [R4].

### 2.9 Negative space for platform UI

Say these positively, as calm reserved areas ("the top 14% is plain sky"), not as bans [15].

| Platform | Keep clear |
|---|---|
| Stories | top ≈14% and bottom 20–35% (R2 D3, R5) |
| YouTube thumbnail | the bottom-right ≈21% × 21% (duration badge) |
| YouTube channel banner | text only inside the central 1546×423 of 2560×1440 (≈60% × 29%) |
| Facebook cover | bottom-left avatar area |
| Instagram feed 4:5 | keep the message inside the central 3:4 grid crop |

### 2.10 What to leave to the model

- **Decide:** artifact, idea, layout, scale relations, exact text, type class, palette roles, light direction, subject count, style anchor, exclusions. If you leave these open, the model picks defaults, and "picking creates slop, committing creates intent" [24][16].
- **Delegate explicitly:** micro-texture, prop styling within the named family, glyph detail within the described class, secondary light nuance, background detail within the stated value. The official ad guidance deliberately leaves the model room for taste decisions *inside* a brief [4].
- **Failure sign.** Rich prompt, flat result: the prompt stacked adjectives instead of one structural idea [15].

### 2.11 Length and format

- **Length.** Median 2.6k characters; up to about 4.5k in the craft corpus [15][16]; API limit 32k [3]. Spend it on decisions, one line each, not on adjectives or QA rules [16][23][7].
- **Format.** Labelled lines or CAPS headers (COMPOSITION / TEXT / CONSTRAINTS) as used in [15]. JSON only for many distinct parts; there is no evidence JSON improves accuracy [R3][16].
- **Codex route.** Put the aspect in words in line 1 (the size is `auto`) and keep exact strings byte-identical through the agent [R3 R-T16].
- **Engine.** Arrangement and text → Sunburst; light-led imagery → Flare [15]. A forum user reports that ChatGPT starts routine requests on Flare and escalates to Sunburst for intricate text or heavy edits (**UNVERIFIED**) [12].

### 2.12 Example prompts per deliverable (our own; structures from the cited sources)

Settings in brackets.

- **Codex** = gpt-image-2 `auto`.
- **API-S** = gpt-image-2.5-sunburst at `high`/`xhigh`.

All pass the text gate [R3 §4.4] before delivery.

**Instagram feed post A — type-led announcement** [Codex; Tier A; pattern from [18][31]]

```text
Instagram feed post, vertical 4:5 portrait. One finished flat graphic filling the canvas edge to edge; not a mockup, not a photo of a print, not a set of options.
Idea: "open late" shown as a single croissant photographed so its curve reads as a crescent moon.
Layout: the headline hangs from one left axis at 7% margin and fills the upper-left 55%; the croissant, about 38% of the canvas width, sits lower right and its tip passes behind the last line of the headline; the bottom 10% is a calm band carrying the brand name flush left. Eye path: headline → croissant-moon → brand.
Image: real croissant cut-out with flaky, uneven lamination; soft light from upper left; one small contact shadow on the flat ground.
Typography: heavy condensed grotesque, all capitals, tight tracking, three stacked lines, cap height about 10% of the canvas height; brand name in a regular grotesque about one fifth of that size.
Text — render exactly these strings once each, capitals as written, no other words:
"OPEN UNTIL MIDNIGHT" set as Line 1 "OPEN" / Line 2 "UNTIL" / Line 3 "MIDNIGHT"
"Forno Alto"
Colour: midnight-blue ground (~70%), warm cream type (~20%), the golden croissant as the only warm accent (~10%). Colour names are guidance only; never print them.
Finish: flat screen-print surface with faint paper grain.
Do not add: stars, sparkles or glow around the moon, extra pastries, badges, script lettering, gradients, drop shadows on type.
```

**LinkedIn post B — B2B milestone, photo-led split** [API-S high; Tier A; patterns [6][15]]

```text
LinkedIn feed image, square 1:1. One finished design, not a mockup.
Idea: a warehouse that now runs on its own roof — one worker walking beneath skylights with solar panels visible through them.
Layout: documentary photo fills the right 62%, bleeding off the top, right and bottom edges; left 38% is a solid slate band with 8% inner margins. The headline sits in the band and its last word crosses about 10% into the photo over a calm patch of pale roof. Eye path: headline → worker → brand line at the band's foot.
Image: photorealistic, candid, overcast daylight from the skylights (~6000K) with a warm tungsten work lamp as a second source; worker mid-stride, not posing; the place and people typical of the client's city.
Typography: medium-weight neo-grotesque, sentence case, two lines, cap height about 7% of the height; brand line at one third of that.
Text — exactly, once each: "Powered by our own roof" and "Northfield Logistics". No other text, numbers, percentages, icons or badges.
Colour: slate (~55%), off-white type, the only saturated colour is the worker's safety-orange jacket.
Do not add: lens flare, a glowing sun, infographic icons, a second worker looking at the camera.
```

**Social ad C — minimal premium product** [API-S xhigh; Tier A; OpenAI "minimal premium whitespace" family [6] + callirra light rules [15]]

```text
Square 1:1 social ad for a hand-thrown ceramic pour-over dripper. One finished design, flat to the viewer.
Idea: "slow coffee" — one unbroken thin stream of coffee rising from the dripper as a single diagonal line to the top-right corner.
Layout: product lower left, about 35% of the canvas height, base resting on the lower-third line; the coffee line is the only other element; headline top right on two lines, ragged left edge aligned to an axis at 58% of the width; 65% of the canvas stays calm warm-stone ground.
Light and material: one large soft window source from the left (~4500K), a faint warm bounce from the right; matte glaze with visible pinholes and a slightly uneven rim; the coffee glossy and dark with one bright highlight along its top edge; one soft contact shadow.
Typography: high-contrast serif, regular weight, sentence case, cap height about 6% of the height.
Text — exactly, once: "Take the long pour" (Line 1 "Take the", Line 2 "long pour"); "Kiln & Co." small, bottom right.
Colour: warm stone ground, charcoal type, coffee brown as the only accent.
Do not add: steam curls, scattered beans, a cup, badges, price, "new" flash, gradients.
```

**Story A — event, reserved sticker space** [Codex; Tier A; safe zones R2/R5]

```text
Instagram and Facebook story, vertical 9:16. One finished flat design.
Layout: the top 14% is plain dusk sky; the headline occupies the band from 18% to 50% of the height; a photo of an empty rooftop with rows of deckchairs facing a blank outdoor screen fills 50–100%; the zone from 58% to 76% is calm, low-detail sky and screen for a link sticker; the bottom 25% holds no text and no faces.
Image: photorealistic, just after sunset, violet sky, string of small warm bulbs along one parapet only, nobody in the chairs.
Typography: extended bold grotesque, capitals, three stacked lines, each line spanning about 80% of the width; "Tonight" in the same family at one quarter size under the headline.
Text — exactly, once each: "ROOFTOP" / "FILM" / "NIGHT" and "Tonight".
Colour: violet-to-ink sky, warm white type, the bulbs as the only warm accent.
Do not add: a film title, sponsor strip, popcorn, sparkles, a QR code, any time or date.
```

The start time goes in a native sticker or an HTML layer: R3 puts times in Tier C.

**Story B — product drop** [API-S high; Tier A]

```text
Instagram story, vertical 9:16, finished design.
Idea: a night face oil shown as a single amber bottle standing in shallow, perfectly still dark water, its reflection completing a tall amber shape.
Layout: bottle and reflection centred on the vertical axis between 30% and 80% of the height (the one centred element; the type is not centred); headline flush left in the band 16–28%; the bottom 25% stays dark water with no text.
Light: one narrow warm top-light (~3200K) hitting the glass shoulder; cool ambient ~7000K on the water.
Typography: light-weight wide grotesque, capitals, wide tracking; one line.
Text — exactly, once: "NIGHT OIL". No other words, no volume, no brand claims.
Do not add: ripples, petals, gold flakes, glow, a price, "new".
```

**Carousel — cover, then body slides from the approved cover** [API-S high; method [58] + [24]]

```text
COVER (slide 1 of 7): Instagram carousel cover, vertical 4:5. Flat editorial design. Idea: "5 mistakes when repotting" shown as one cracked terracotta pot, root ball intact, lying on its side.
Layout: headline top-left 45% on a 7% left axis; the pot lower right at 50% of the width, its rim crossing the canvas's right edge (a cue that the story continues); the bottom-left 12% holds a small "1/7" marker.
Typography: bold condensed grotesque, capitals, three lines. Text — exactly, once each: "5 REPOTTING" / "MISTAKES" and "1/7".
Colour: warm bone ground, near-black type, terracotta as the only accent. Finish: flat risograph grain.
Do not add: leaves falling, soil scatter, icons, badges.

BODY (slide k, separate generation; fill every <…> before sending): Image 1 is the approved cover — copy only its type feel, margins, colour roles, grain and axis; do not copy its pot, crack or words. Vertical 4:5, slide k of 7. Headline block in the same top-left zone; one object for this slide's point in the same lower-right zone; marker "k/7" in the same corner.
Text — exactly, once each: "<slide headline, ≤5 words>" and "<k>/7".
```

Carousel notes:

- Generate each slide separately from the approved cover as a *style-only reference*. Never chain edits, and never ask for all slides in one image [24][58].
- A seamless panorama is different: one wide image (≤3:1), sliced, with nothing important within 40 px of the seams [R2 B9].

**YouTube thumbnail A — face + object + three words** [API-S high; higgsfield contract [32] + R3 §5.4.4]

```text
YouTube thumbnail, 16:9 landscape, one finished bold design that must read at 120 px wide.
Layout: the creator (Image 1: identity only; keep face, skin tone, hair, glasses exactly) chest-up in the right 55%, eyes on the upper third, skeptical raised brow, holding a small round robot vacuum toward the lens; the left 40% is a flat saturated cobalt field carrying the words; the bottom-right corner (about 21% × 21%) stays free of text and face.
Light: strong key from front-left, soft fill, a thin cool rim separating hair from the background.
Typography: very heavy condensed sans, capitals, white fill with a thick dark outline and a hard offset shadow, two lines, cap height about 16% of the height.
Text — exactly, once: "TOO" / "SMART?". No other text, no arrows with words, no logos.
Do not add: extra people, emojis, sparkles, a fake play button, a subscribe badge.
```

**YouTube thumbnail B — scale contrast, no person** [Codex; Tier A, one simple number; the creator's own claim, verify it]

```text
YouTube thumbnail, 16:9 landscape. Idea: one worn hiking boot, huge, standing on a miniature mountain range as if it walked it.
Layout: boot fills the left 60%, sole edge crossing the bottom edge; tiny ridgeline and a thin trail under it; the right 40% is a clear pale sky field for the words; bottom-right corner clear.
Light: low late sun from the right, long warm shadows on the miniature ridges; scuffed leather, frayed laces, dried mud.
Text — exactly, once: "WORN 1,000 KM" in two lines ("WORN" / "1,000 KM"), heavy condensed sans, black on the pale sky, cap height about 14% of the height.
Do not add: brand logos on the boot, other text, lens flare, glow.
```

**YouTube thumbnail C — text built into the scene** [API-S xhigh; Tier A; R3 FA thumbnail]

```text
YouTube thumbnail, 16:9. The words "SAVED IT" stand as large three-dimensional letters cut from rusted steel plate, welded seams visible, on a garage floor beside the front of a half-restored 1970s car. Letters occupy the left 50%, cap height about 30% of the height, spelled exactly S-A-V-E-D I-T, each once.
Light: one hanging work lamp (~3000K) from upper right; cool daylight through a side door; oil stains and dust on concrete.
Keep the bottom-right corner clear. No other text, no licence plates with readable characters, no logos.
```

**Banner A — YouTube channel art** [API-S high at 2560×1440; banner safe area R2]

```text
YouTube channel banner, 16:9, 2560×1440 canvas. All text and the main subject sit inside the central 60% width × 29% height; everything outside it is atmosphere that may be cropped.
Idea: a woodworking channel — one long walnut board running edge to edge across the frame, its grain continuous, shavings curling off a plane at the centre.
Typography inside the safe area: channel name in a bold slab serif, capitals, centred on the board's upper edge; cadence line under it in a small grotesque.
Text — exactly, once each: "GRAIN & GLUE" and "New builds every Friday".
Light: warm raking light from the left revealing grain texture; outer areas fall into soft shadow.
Do not add: tools with readable brands, icons, badges, a subscribe button.
```

**Banner B — Facebook Page cover** [API-S high; ≈2.7:1, within the 3:1 limit]

```text
Facebook Page cover, wide 2.7:1 landscape, finished design.
Layout: the bottom-left 25% of width × 40% of height stays plain (avatar overlaps there); message on the right 55%; photo of a sunlit community pool seen from above fills the frame; the text sits over calm, flat water.
Typography: rounded humanist sans, bold, sentence case, one line, spanning about 40% of the width.
Text — exactly, once: "Swim season is open". No other text.
Colour: turquoise water, white type, a single red-and-white lane rope as the accent.
Do not add: swimmers' faces close to camera, logos, sparkles.
```

**Poster A — editorial event poster with a visual metaphor** [API-S xhigh 2:3; Tier A; structure from [15]]

```text
Vertical 2:3 event poster: the flat printed sheet itself, facing the viewer square-on; not a photo of a poster hanging somewhere.
Idea: an open-air lido's night swim — seen from directly above, one swimmer's wake curves across the dark water and the moon's reflection sits at the top of the curve.
COMPOSITION: deep teal-black water fills the frame; the wake enters bottom left and bends up to the right; the moon reflection is a small pale disc at 30% from the top, right of centre. The title occupies the top 28% on one left axis at 8% margin; a single thin rule closes it. The bottom 14% is calm water for the second line. The wake never crosses a letter.
TEXT — render exactly these strings, once each: "NIGHT SWIM" (title, one line, spanning about 70% of the width, tall condensed serif with high contrast, tight tracking) and "Fridays in August · Lido Park" (bottom band, small neutral sans, capitals and lowercase as written).
FINISH: two-colour screen print on heavy uncoated stock: teal-black and pale moon-cream only; visible ink grain in the large flat areas; slight registration offset on the moon.
CONSTRAINTS: no other text, dates, logos, sponsors, QR code; do not rotate, outline or shadow the type; no swimmers' faces; no frame, wall, tape or perspective.
```

**Poster B — conceptual typography (type is the hero)** [API-S xhigh; pattern [26][31]]

```text
One finished conceptual typography poster, vertical 3:4, for a silent-meditation weekend. Single poster only: no board, grid, captions or mockup.
The word "STILL" is the dominant structure: letters about 75% of the canvas width, heavy low-contrast sans with flat terminals, bone white on deep moss green. A seated figure in plain linen, seen from behind, sits in the counter space between the "I" and the first "L"; the figure's shoulder passes behind the "L" (the letters stay fully readable).
Second string, small, bottom left on the same axis as the "S": "A weekend without words". Render both strings exactly once; no other text.
Colour: moss ground (~70%), bone type (~25%), the figure's ochre shawl as the only accent.
Finish: flat lithographic colour areas, fine paper fibre, no gradients.
Do not add: lotus flowers, candles, mandalas, glow, sparkles, a sunrise.
```

**Poster C — flat civic screen print** [Codex; Tier A; pattern [15] travel poster]

```text
City event poster, vertical 2:3, flat three-colour screen print seen straight on.
Composition in three flat bands: river (bottom 30%, dark blue), a long stone bridge of five arches as one flat ochre shape with the arches cut out (middle), and a sky of bare paper (top). Twelve cyclists in profile cross the bridge left to right as tiny flat silhouettes.
Title "RIDE THE RIVER" centred in the sky band, geometric sans, bold capitals, generous tracking, about two thirds of the width; "Bike Week 2026" beneath it at one fifth of the title's height. Exactly these two strings, once each.
Constraints: three inks plus paper only; no gradients, shading or halftones; no people's faces, logos or extra text; no frame or wall.
```

**Flyer A — art-led A5 flyer with a reserved information strip (H5)** [Codex; Tier A + HTML strip [R3]]

```text
Print flyer, vertical A5 (generate 2:3; it will be cropped to 1:1.41). One finished flat design.
Idea: a film-photography workshop — a single 35 mm film strip unrolling across the page, three frames showing the same street corner getting sharper.
Layout: title top 26% on a 7% left axis; film strip diagonally across the middle 45%; the bottom 20% is a flat, empty cream panel with nothing in it (details are added later).
Text — exactly, once each: "SHOOT ON FILM" (bold condensed grotesque, capitals) and "Beginner workshop" (regular grotesque, one third of the title size).
Colour: cream paper, black, and the strip's amber base as the accent. Finish: offset print with fine grain.
Do not add: dates, prices, addresses, QR codes, logos, camera brand names, sparkles.
```

**Flyer B — complete single-sided flyer** [API-S xhigh. R3 puts dates and times in Tier C (hybrid). Run this only as a test of the single-prompt route: best of 3, with a character-level check of every string; otherwise use Flyer A]

```text
Community clean-up flyer, vertical 2:3, finished flat design.
Layout: headline top 30%; hand-drawn illustration of a riverbank with six volunteers carrying bags in the middle 40% (people typical of the client's town); an information block bottom 22% in three left-aligned lines on one axis.
Text — exactly these five strings, once each, casing as written: "CLEAN THE CREEK", "Saturday 11 October", "9:00–12:00", "Meet at Mill Bridge", "Gloves and bags provided".
Typography: headline in a chunky rounded sans; information in a clear grotesque at one quarter of the headline size.
Colour: creek green, sand, and one safety-yellow accent on the bags.
No other text, logos, sponsors, URLs or QR codes.
```

**Infographic A — fixed-zone explainer** [API-S xhigh 4:3; Tier B, 8 strings; structure [15]]

```text
Flat vector explainer infographic, 4:3 landscape, titled "HOW A HEAT PUMP WARMS A HOME".
ZONE 1 (top 12%): title, bold condensed sans, capitals, left aligned; hairline rule closing the band.
ZONE 2 (left 62%, below the title to the bottom strip): cutaway of a two-storey house with an outdoor unit on the left wall and underfloor pipes on the ground floor; five small arrows show the heat path: outside air → outdoor unit → pipe → indoor unit → floor.
ZONE 3 (right 34%): exactly three stacked callouts, each a number badge plus a one-line bold label; one leader line per callout to its part; leaders never cross.
ZONE 4 (bottom 16%, full width): exactly four boxes joined by three chevrons.
TEXT — exactly, once each: the title; callouts "OUTDOOR UNIT", "REFRIGERANT", "UNDERFLOOR LOOP"; boxes "Absorb", "Compress", "Release", "Warm".
STYLE: solid fills, uniform hairlines, no gradients, no shadows, no 3D; white ground; palette of cool blue, warm amber and one accent on the badges and chevrons; one sans in exactly three sizes.
No numbers, units, efficiency figures, logos or other text.
```

**Infographic B — vertical social process card** [API-S high; Tier B, 5 strings: best of 2–4, gated]

```text
Instagram infographic post, vertical 4:5. Four numbered steps in one column on a left axis, each step = a large numeral in a circle, a flat icon and one label of two or three words. Exactly four steps, exactly four icons, top to bottom.
Title band top 18%. Text — exactly, once each: "REPOT IN 4 STEPS", "Loosen the roots", "Pick one size up", "Add fresh mix", "Water, then wait".
Style: flat two-colour illustration (leaf green, soil brown) on warm white; one icon family, same stroke weight.
No other text, no percentages, no logos, no decorative leaves in the margins.
```

**Special-day post A — New Year, typographic** [API-S high; Tier A]

```text
Square 1:1 New Year post for a bookshop, finished flat design.
Idea: the year as a threshold — the "0" in "2027" is drawn as an open door with warm light spilling onto the floor below it.
Layout: "2027" spans 80% of the width across the middle; the light from the open "0" falls as one warm trapezoid toward the bottom; the greeting sits in the bottom 15% on a centred line; the shop's name small, top left.
Text — exactly, once each: "2027", "Happy New Year", "Alder Books".
Typography: tall didone numerals, deep green on warm paper; greeting in a small italic serif.
Do not add: fireworks, confetti, clocks, champagne, sparkles, glitter, bokeh.
```

**Special-day post B — Mother's Day, one-jump metaphor** [Codex; Tier A]

```text
Instagram post, vertical 4:5, for a family bakery on Mother's Day. Photographic, finished design.
Idea: one adult handprint and one small child's handprint pressed side by side in flour on a dark wooden counter (a plain juxtaposition; no people shown).
Layout: handprints centred slightly above the middle, lit by soft window light from the upper left (~5000K) that rakes across the flour; the greeting set small on one line in the bottom 14%; brand name bottom right.
Text — exactly, once each: "For the hands that fed us" and "Bakehouse 19".
Typography: warm humanist serif, sentence case, cream on the dark wood.
Do not add: hearts, flowers, ribbons, script lettering, glow, extra text.
```

### 2.13 Disagreements between sources (and the call we make)

| Topic | Position A | Position B | Our call |
|---|---|---|---|
| First block | Scene first [1][4][5] | Canvas and artefact first [15][16][17] | Artifact and format line first, then layout |
| Colour codes | Hex preferred [48] | 0 hex in 150 prompts [16]; hex printed as labels [R3] | Words by default; hex guarded, or in a swatch image |
| Series consistency | Slide 1 attached as anchor [58], anchor chain (baoyu, R2) | Shared prefix, no chains [24] | Shared prefix always, plus the cover as a style-only reference in *fresh* generations; never edit chains |
| Text failure | Switch to text-light base + overlay [18][R3] | Never auto-switch; simplify the title and regenerate [22][23] | Simplify first (one retry), then hybrid, and tell the user |
| One highlighted word | Keyword enlarged in brand colour [21] | Flagged as an AI tell (R2 B8) | Only when the idea depends on it |
| Official cues | "Tasteful bokeh", "Inter" in official prompts [4][1] | Listed as tells [24][R4] | Our anti-AI rules override |

---

## 3. Reference strategies

### 3.1 How many references

| Route | Limit |
|---|---|
| Codex `image_gen` | ≤5 references [R3] |
| API edits | ≤16 [3] |
| Nano Banana | up to 14 (not our engine) |

**Practice:** 1–4, each with a single job [15][23]. When two inputs can decide the same property, the model averages them and the subject drifts [15].

**Why fewer and simpler (DER).** Inputs are reportedly downsampled to a fixed patch budget of about 1.5k patches (**UNVERIFIED**, R3 S14), so small details in busy references are lost.

### 3.2 Manifest, order and wording

- **Manifest first.** With two or more images, the first lines of the prompt list what each image is [32][1].
- **Order is semantic.**
  - The edit target is always Image 1; the mask applies to the first image [2][23][35].
  - Faces come first and the logo last in higgsfield's thumbnail skill [32].
  - Keep the highest "Image N" equal to the number of images attached [15].
- **Each line says:**
  - what the image supplies;
  - what it must **not** supply;
  - the conflict rule (which input wins on a shared property) [15].

  Example: "Image 1 — identity: face, hair, skin tone; not the lighting or background. Image 2 — style: two-ink print, cropped oversized type, 60% bare paper; not its subject, words or layout."
- **Generation, not edit.** If references are for style or mood, treat the job as generation with references, not an edit of the reference [5][19].

### 3.3 Roles

| Role | Wording core | Source |
|---|---|---|
| Edit target / identity | "keep face, facial structure, skin tone, hairline, glasses exactly; no beautifying; only <expression/pose> may change" | [1][32][17] |
| Product / SKU | "keep silhouette, proportions, cap, label layout, logo, every printed character, material finish, colour" | [51][52] |
| Style | name 2–4 visible mechanisms; "use for visual grammar only; new subject and a clearly different composition" | [23][17][19] |
| Layout guide / sketch | "invisible construction reference: follow positions, sizes, reading order; never draw its boxes, lines, fills or marks" | [7][10][4] |
| Logo | "reproduce Image N exactly: shapes, letters, colours, proportions; small, at <corner>; no effects" — then verify | [32][6] |
| Palette swatch | "take only colour relationships and proportions; do not reproduce swatches" | DER |

### 3.4 Using a style reference without copying it

- **Hard lock, soft lock, must replace [19].**
  - Lock 5–8 high-impact rules: grid family, title footprint, hero-to-canvas ratio, overlap behaviour, palette relationship, type category, image treatment.
  - Adapt 3–6 soft rules.
  - List everything that must be replaced: people, products, props, words, logos, symbols.
  - Keep the spatial grammar, not the coordinates.
- **Name mechanisms, not moods [23].** If the reference can only be described with adjectives ("premium, restrained, editorial"), change the reference.
- **Originality firewall [18].** Change ≥4 of: subject and crop, layout family, headline wording, headline location, image count, grid, type pairing, metadata treatment, ratio, disruption device.
- **Describe instead of attach** when copying risk is high: turn the reference into words (3–5 critical anchors first) and attach nothing [30][32].
  - Higgsfield analyses a style thumbnail with the host's vision and never sends it to the image model [32].
  - Some community carousel builders pick references from outside the target platform, e.g. Pinterest instead of Instagram, to avoid mimicry [58].
- **Checking for leaks.** The fidelity check scores the *system*, not the content [19]. Any surviving reference word, logo or person is a hard fail.

### 3.5 Keeping a client's face, product or logo exact

- **Face**
  1. Supply a photo as Image 1 with an identity-lock paragraph [32]. No other input may supply skin or light [15].
  2. On 2.5, subject preservation is claimed to be better. One hands-on test still showed composited-looking hair edges [10].
  3. Verify with a face-embedding similarity check (DER proposal) plus human review.
  4. If it drifts, regenerate once with tighter invariants. Then cut out the real person and composite them (R3 H2); for High preservation, prefer the original-photo crop over redrawing [17].
- **Product**
  - Write a protection list before the prompt: outline, geometry, proportions, cap, label layout, logo, readable text, colour, finish, count, orientation, light logic [51].
  - Quote the label strings.
  - One failed check sends the image back to the last accepted source [51].
  - If the label must be exact, composite the real product pixels [R3 §7.3].
- **Logo:** see §2.6. Reserve and composite by default.

### 3.6 Layout sketches and typeset scaffolds

- **Evidence.** A rough sketch is an effective layout guide:
  - the official sketch-to-render keeps layout, proportions and perspective [4];
  - ChatGPT's 2.5 **Sketch** exists because spatial relations are "fiddly in words" [10];
  - OpenAI's own skill uses invisible layout guides [7].
- **Typeset scaffold (guizang [23]).** Image 3 is a neutral grey page carrying the confirmed copy in position and at real size, the reading order, and the subject's occlusion contour. It locks structure, not colour or material.
  - This is the strongest known way to hand GPT Image both layout *and* type sizes in one call. COM; **UNVERIFIED** at scale.
- **Rules**
  - Same aspect ratio as the target.
  - No labels or marker text the model could render (hatch-pet rejects outputs that copy the guide [7]).
  - The scaffold's glyph shapes will pull the output toward the scaffold font. Use the real brand font, or only character slots when the display lettering should be reinterpreted [23].

---

## 4. Creative variety while staying on-brand

### 4.1 Concept first: how agencies brief

- **Get / To / By.** Get <audience> to <action or belief> by <organising idea> [69]. Pollard's critique: without a psychological insight and an organising idea, creatives cannot use it. Write the idea as one sentence.
- **Visual metaphor typology** (Phillips & McQuarrie 2004 [66]):
  - three visual structures: **juxtaposition** (side by side), **fusion** (merged), **replacement** (one implies the absent other), in rising complexity;
  - crossed with meaning operations (connection, and comparison for similarity or opposition).
  - Use the grid as a concept generator: fill 3–6 cells per brief.
  - A similar chain from an illustration skill: pick the cognitive anchor → distil the point → invent a fresh metaphor → check it does not read as a slide [43].
- **Filters**
  - **One-jump:** a single mental step from image to meaning [21].
  - **Swap-the-logo:** cover the logo; if a competitor could run it, it is generic [67]. Distinctive assets (colour, character, device) carry recall even under a competitor's logo; the source calls this a "fun experiment" [68].
  - **Three glances:** silhouette → message → detail (R2 B5).
  - **Truthful promise:** exaggeration yes, misrepresentation no [32].
- **Presentation practice.** Agencies commonly show three genuinely different routes ("power of three") [70]. OpenAI's plugin explores 4–6 directions (R2).

### 4.2 Archetype libraries (pick the layout after the idea)

- **Ads:** OpenAI's 25 families [6].
- **Thumbnails:** higgsfield's 16 frameworks (Before/After, Size Difference, Amplified Reality, …) (R1).
- **Posters:**
  - gc-minimal's 10 layout families (center-fragment, lower-left-float, upper-right-block, dual-panel, irregular-cutout, type-led, dot-orbit, single-specimen, diagonal-notes, edge-counterweight) [17];
  - mono-color's 9 families chosen by content (ruled information poster, archival plate, object field, overprint collage, image field, specimen annotation, type-led declaration, editorial journal, editorial cover) [18];
  - fantasy-dongfang's A/B/C (archive intervention / single material proof / type-structure experiment) [22].
- **Ad heroes:** 30x's axes (hero composition × framing × light × text integration) [24].
- **Style packs:** JSON packs with fidelity anchors and "source content to avoid" (R2 A3) [42].
- **Subject type mix:** product / prop / pure type ≈30/40/30 in a mature poster brand [21].

### 4.3 Axes to rotate (one value per axis per design)

concept structure (juxtaposition / fusion / replacement) · archetype or layout family · focal type (person / product / prop / type) · type-image device (§2.8) · type mode (literary serif / civic condensed / wide grotesque / type-as-object) · palette roles (which brand colour is the ground this time) · finish (screen print / photo / flat vector / risograph / 3D) · light (key direction, temperature pair) · scale relation (giant crop / small figure / specimen).

Change the *grammar*, not just positions [17]. Keep the brand constants fixed:

- logo placement;
- 2–3 brand colours;
- type classes;
- one recurring device.

### 4.4 A "never repeat" ledger

Examples exist in the wild:

- guizang stores a recipe history and chooses with maximum distance from it [23];
- gc-minimal compares against the previous visible output [17];
- a small YouTube pipeline keeps a per-video ledger and requires ≥3 axes of difference from the last 6 rows [44]. It was written because YouTube demonetises templated sameness (R2 D1).

**Proposal (DER, house heuristics):**

- **One row per delivered design:** date, client, deliverable, concept structure, archetype, focal type, device, type mode, palette roles, finish, style anchor, prompt hash.
- **Rules**
  - differ from the client's last 6 designs on ≥3 axes;
  - never the same archetype + focal-type pair on adjacent posts;
  - a style anchor at most twice in 10;
  - never the same concept structure three times in a row.
- **A/B variants of one design** deliberately vary *one* axis [16].

### 4.5 Explore, then pick

- **No seed parameter exists** [3]. Repeatability comes from stored prompts and recipes; variety from recipe changes. `n` on the API (1–10) only resamples one recipe.
- **Direction round.** 3–5 different recipes, one image each, in fresh sessions. Chat context leaks style and copy between images [14][R3 C15]. Early Images 2.0 users also saw noise build up within one session and cleared it by starting a new one [13].
  - Codex has no `n`: run parallel calls [R3].
  - Judge as a group [22].
- **Winner round.** 2–3 samples of the chosen recipe; pick; then verify and fix (§6). For a set, approve one representative sample before fanning out [46].
- **Cost on the API.** Explore cheaply: at 1024², going from `low` to `max` costs about 36× more, while going from the smallest size to 4K at a fixed tier costs under 3× more [47].
- **Carousel pace** [58]: about 5 versions of the cover, then about 3 per body slide, each attached to the approved cover.
- **Creativity check** [25]: before generating, raise at least 3 of the escalation levers (composition, type, scale contrast, concept, treatment, framing) versus the safe first idea.

---

## 5. Anti-AI-look rules for full-AI designs

The general tell table is in R4 §5.1. The rows below are the GPT-specific ones for full designs, with prompt counters.

| Tell (full-AI designs) | Where it comes from | Prompt counter |
|---|---|---|
| Centred stack: logo, headline, sub and button on one axis; "two islands" | the default when no layout is given [15][23][24] | give zones and one off-centre axis; one deliberate disruption [18] |
| Glossy gradients, neon glow, orbs, floating blobs, purple/cyan | model priors [24][25][R4] | "flat colour areas; no gradients, glow or blobs"; name a print or photo finish |
| Sparkles, particles, embers, lens flare, bokeh dots | "magic" filler [55][R4] | "no sparkles, particles, flares or bokeh"; light only from named sources |
| Fake badges, seals, stars, "NEW", "BEST", countdowns, certifications | ad completion; e.g. a community ad prompt that asks for a stamp [20][6][15] | "no badges, seals, ratings, awards or flashes" |
| Invented slogans, subtitles, footers, micro-text | ad completion, chat context [6][16][R3 C15] | exact-copy contract; "no small descriptive text" [6]; fresh session |
| Cream + high-contrast serif + terracotta; one word highlighted in the accent | the default "premium" cluster (R2 B8) | choose type from the idea; forbid single-word colour highlights |
| Script or brush flourishes, brush-stroke banners, circle icons, divider lines | template leftovers [57][20] | "no script, brush lettering, swashes, ribbons or banners" |
| Chrome or 3D bevel type; outline plus shadow on every word | [55] | "flat type, no outline, shadow, bevel or gradient" (except the thumbnail genre) |
| Orange-gold cinematic grade, crushed blacks; yellow cast (older models) | [55][24] | name the colour temperature and a neutral balance; documentary cues |
| Everything decorated; every corner busy | [55][57] | give an empty-space % and a release zone [17][18] |
| Mockup instead of artwork (framed, on a wall, a tilted sheet) | "poster" read as an object [R3] | "the flat printed sheet itself, facing the viewer; no frame, wall, tape or tilt" [15] |
| Booster words ("8K, masterpiece, stunning, cinematic, epic") | copied boilerplate [28][55] | delete them; describe the light or finish instead [33][37][20] |

**Wording that works**

- **Short, targeted negation for strong priors only.** Negation works in GPT Image: official prompts use "no extra text, no watermarks". But a long list competes with the description [15][16][1].
- **Reserve space instead of forbidding.** "Leave a clean empty rectangle for X" beats "do not add X" [15].
- **Say the positive state for scene content.** "Calm, flat water" rather than "no waves". Diffusion-era experience shows naming a thing can prime it (COM).
- **Name a style anchor:** a movement, era, print technique or grid [R3 C15][54].
- **Replace vague labels with specifics** (the "premium / cinematic / Apple-like" linter [20]).

**Compact negative bank** (choose 3–8 per prompt):

extra text · subtitles or captions · badges, seals, stars, awards · sparkles, particles, flares, bokeh · gradients, glow, blobs · drop shadow, outline or bevel on type · script or brush lettering, ribbons · centred stacked layout · second focal object, extra props · mockup, frame, wall, perspective · invented logos, handles or QR codes · stock-photo polish, plastic skin.

**Judge questions**

- Would a similar prompt land on the same image? If so, change the recipe (R2 B8).
- Does it pass the swap test [67]?
- Can you name the one bold move? Remove one accessory (R2 B8).
- Is anything confident-looking but meaningless: decoration that says nothing, or text that almost works [56]?

---

## 6. When single-prompt fails: the escalation ladder

### 6.1 Published rates

| Measure | Model | Result | Source | Strength |
|---|---|---|---|---|
| Headline error-free / quoted vs unquoted | gpt-image-2 | 94% / 96% vs 84% | [49] via R3 | VEN |
| Edit rounds: clean after 1 / cumulative after 2 / visible drift after 3 | gpt-image-2 | ~88% / ~72% / ~50% drift | [49] | VEN, **UNVERIFIED** |
| Identity across 8 images, without / with 1 reference | gpt-image-2 | 85% / 94% | [49] | VEN |
| Critical-entity recall in text-rich images | gpt-image-2 | 70.0% (NB2 57.4, Seedream-5-Lite 62.8) | TextFake [65] | research |
| Tricky text-guided edits | 5 models, incl. GPT-Image-1.5 | none above 22%; colour and appearance edits easiest | TECCI [64] | research (via review) |
| Commercial docs, hard mode: text / layout | GPT-Image-1.5 vs Nano Banana Pro | 40.4 / 51.6 vs 86.4 / 72.2 | BizGenEval [62] | research, older GPT |
| Infographics fully correct | NBP / GPT-Image-1.5 | 49% / 12% | IGenBench (R2) | research |
| Point vs structural edits (2.5) | ChatGPT Images 2.5 | point edits strong; moving several objects breaks global consistency | DataCamp [10] | hands-on |
| Tier comparison | 2.5 Flare / Sunburst | both 5/5 HUD strings exact; Sunburst tidier layout | [15] | COM, n=5 |

**No published first-pass acceptance rate exists** for full client designs made by single-prompt (**gap**). R3's arithmetic applies: at P = 0.6 per attempt, three attempts succeed 94% of the time [R3 §3.2].

### 6.2 Classify the miss, then choose the fix

Review in this order [15]: text → protected elements → composition → light and material → style. Check text at 200% for exact characters, counts, dashes, casing and accents [50]. Name the miss in writing before changing anything [15][R2 B5].

| Miss | Fix | Cap |
|---|---|---|
| One string wrong (typo, casing), same length | Point edit on the **original**, change only that string; composite that region back [1][R3 §7.1] | 2 edits |
| Extra or invented text | Regenerate with the exclusion class named; fresh session | 2 regenerations |
| Longer or new text, reflow needed | Shorten or simplify the copy and regenerate [22][18]; then hybrid (R3 H4/H5) | 1 + switch |
| Logo or product drift | Composite the real PNG or cut-out; or regenerate with the protection list [51] | 1 |
| Face drift | Regenerate once with tighter invariants; then composite the real person (R3 H2) | 1 |
| Layout, hierarchy, counts, two islands | **Regenerate** with restated zones, percentages and overlap; do not patch with edits [19][10] | 2 |
| Colour or appearance, local | Point edit (easiest edit class [64]) | 2 |
| Reference leak | Regenerate; name the leaked item under "must replace" [19] | 1 |
| AI look or generic | New recipe or style anchor; add the strong-prior negations | 1 per direction |

### 6.3 Ladder and stop rules (DER, house heuristics)

1. **Generate** from the dossier: best of 1–3 on the API, or parallel calls on Codex.
2. **Point edits.** At most 2 per image, always from the approved original, one change each, repeating the preservation list. Composite the edited region back [1][4].
   - 2.5 claims steadier multi-turn edits [9][10]. Still, measured drift grows with rounds [49].
   - Never chain edits across slides [24].
3. **Regenerate** with one named correction. At most 2 per direction. Rewrite the relevant section only; don't rewrite the whole prompt for a local defect [19].
4. **Reduce the text** to Tier A by shortening the title and moving details to a strip. One try.
5. **Hybrid.** A text-light plate or comp-first (R3 H4), with type, data and logo typeset in HTML. Say so in the delivery note.
6. **Budget.** Stop after about 6 image calls for one deliverable. That is our cap; higgsfield caps a thumbnail job at 16 [R1], and guizang never re-generates automatically [23]. Present the best candidate and name its known defect rather than looping.

---

## 7. Implications for `codex-design` (proposal)

- **Add a "dossier" full-AI route beside Compose.** It is used when:
  - the text fits Tier A/B;
  - there is no data;
  - the design's value is integration of type and image.

  It uses the Master template below, the ledger (§4.4), the ladder (§6.3), and R3's text gate plus the fidelity rubric [19].
- **Compile the dossier into Codex's native labelled lines** [5] and assert passthrough [R3 R-T16]. For Sunburst jobs, use the API engine and pin the snapshot id (e.g. `gpt-image-2.5-sunburst-2026-09-08`) [53].
- **Logo:** reserve-and-composite by default. **References:** manifest plus roles plus conflict rule; ≤4 inputs.
- **Eval before adopting** (extends R3 §11). Compare three conditions: text-only dossier vs dossier + split reference kit vs dossier + composite sheet. Run 6 briefs × 3 samples on Codex and on API Sunburst. Measure:
  - first-pass acceptance and calls per accepted asset;
  - text exactness and zone adherence;
  - logo IoU (overlap with the real logo);
  - palette ΔE (colour difference from the brand swatches);
  - AI-look score.

---

## Master prompt template (fill in every field; delete lines that do not apply)

```text
[0 REFERENCES — only if images are attached; one line each, in attach order]
Image 1 — <role: identity | product | edit target>: use it only for <job>. Keep exactly: <invariants>. Do not take from it: <lighting | background | colours | layout>.
Image 2 — <role: style>: take only these visible mechanisms: <2–4 mechanisms>. Replace its subject, words, logo and composition with a clearly different arrangement.
Image 3 — <role: layout guide>: invisible construction reference — follow its positions, sizes and reading order; never draw its boxes, lines, fills or marks.
Image 4 — <role: logo>: reproduce exactly (shapes, letters, colours, proportions), small, at <corner>, no effects.   (default: omit this line and use the reserve in 10 BRAND)
If images disagree on <property>, Image <n> wins.

[1 ARTIFACT] <deliverable> for <platform>, <aspect in words> <ratio>. One finished flat design filling the canvas edge to edge — not a mockup, not a photo of a print, not a sheet of options.

[2 PURPOSE & IDEA] For <audience> in <client's market/city>; it must make them <one action or feeling> at a glance. Idea: <X shown as Y, one sentence>.

[3 LAYOUT] Axis: <e.g. every text line hangs from one left axis at 7%>. Zones (% of height/width): <zone A bounds — contents>; <zone B …>; zones never overlap except as stated in [6]. Outer margins ≥ <6–8>%. Empty space ≈ <n>%.

[4 FOCUS & ORDER] Largest element: <X>, ≈ <n>% of the canvas. Eye path: 1 <X> → 2 <Y> → 3 <Z>. Quiet zone: <area> stays <calm texture/tone>. Nearest the camera: <foreground crop>, if any. Counts: exactly <n> <things>.

[5 IMAGE] Subject: <who/what, count, action, scale, crop>. People and place: <typical of client's market>. Medium: <photorealistic photo | flat vector | screen print | 3D>. Camera: <viewpoint, distance, lens look, sharp plane>. Light: <source, direction, quality, K>; second source: <…>. Materials: <how each surface behaves>. Contact shadows agree with the light.

[6 TYPE–IMAGE DEVICE] <one: headline behind the subject (first letter and every word readable) | last word crosses the object's edge | letters built from <material> | giant crop + small figure>.

[7 TYPOGRAPHY] ≤2 families. Headline: <class, weight, width, contrast, case, tracking>, cap height ≈ <n>% of height (or spans ≈ <fraction> of width). Secondary: <class>, ≈ <1/3–1/5> of headline. Alignment: <…>. Line breaks as in [8].

[8 EXACT TEXT] Render exactly these strings, each once, casing and punctuation as written; do not paraphrase, translate, abbreviate, re-case or hyphenate:
"<string 1>" — <role>, <zone>, <Line 1 / Line 2>
"<string 2>" — <role>, <zone>
Spell: <B-R-A-N-D> (rare words only).
No other text anywhere: no extra words, subtitles, captions, numbers, dates, prices, labels, handles, signage, badges, UI or watermarks.

[9 COLOUR] <ground colour> ≈<60>%, <support colour> ≈<30>%, one accent <colour> only on <element> ≈<10>%. Colour names and codes are guidance only; never print them.

[10 BRAND] Leave a plain empty area ≈<12>% of the width at <corner> with nothing in it (the logo is added later). Brand device: <recurring shape/colour block/crop>.

[11 STYLE & FINISH] Style anchor: <movement / era / print process / grid>. Surface: <flat printed sheet | screen graphic>, <grain, halftone, ink behaviour>.

[12 PLATFORM SAFE ZONES] Keep <top 14% | bottom 20–35% | bottom-right corner ≈21%×21% | central safe area> free of text and faces.

[13 CONSTRAINTS] Do not add: <3–8 items from the negative bank: second focal object, extra props, badges/seals, sparkles, gradients/glow, drop shadow or outline on type, script lettering, centred stack, invented taglines>.
```

**Kept outside the prompt, in the dossier file:**

- the ledger row and recipe;
- the QA checklist (text gate, fidelity rubric, safe-zone overlay, AI-look questions);
- the rationale;
- hex values, unless guarded.

**Codex mapping (DER; T*n* = template section *n*; labels from [5]).** `Use case` ← T1 · `Asset type` ← the deliverable · `Primary request` ← T2 · `Scene/backdrop` + `Subject` ← T5 · `Style/medium` ← T11 · `Composition/framing` ← T3, T4, T6, T12 · `Lighting/mood` ← T5 · `Color palette` ← T9 · `Text (verbatim)` ← T7, T8 · `Constraints` ← T10, T13.

---

## Reference sheet recipe (composite) — **UNVERIFIED**

**Evidence for a single composite sheet**

- One blogger reports a one-image brand reference sheet (palette with hex, type samples, mascot poses, logo, 3–4 style references) gave on-brand ChatGPT Images 2.0 output on the first try. Anecdotal, with no comparison [59].
- It saves reference slots on Codex (≤5).

**Evidence against**

- One reference, one job: overlapping inputs are averaged [15].
- Labels and hex codes inside images leak into outputs [R3 C23][7].
- Downsampling shrinks a small logo inside a busy sheet (≈1.5k-patch budget, **UNVERIFIED**) [R3].
- A layout sketch needs the target's aspect ratio, which a combined sheet cannot provide (DER).

**Verdict.** Use a **split kit** by default. Test the composite sheet in the §7 eval before adopting it.

### A. Split kit (recommended default; each image has one job)

1. **Logo PNG**, alone.
   - Transparent or on white, filling ≥60% of the image, with clear space.
   - Attach only if the logo must appear inside the scene. Otherwise reserve its area and composite it later.
2. **Palette strip** at 1:1 or 3:2.
   - 3–5 solid colour fields sized by usage (≈60/30/10); one field per brand colour.
   - **No labels, no hex, no text.**
   - Role line: "colour relationships and proportions only".
3. **Layout scaffold** at the **exact target aspect**.
   - Neutral grey blocks for the image zones.
   - The real copy set in position and at real size in the brand font, rendered in HTML with real font files.
   - A thin outline for the reserved logo area.
   - No labels or markers.
   - Role line: the invisible construction reference wording [7][23].
4. Optional: **one style reference** (mechanisms named) and/or **one subject photo**.
   - That totals ≤5 inputs on Codex.

### B. Composite brand sheet (only for testing)

- **Canvas:** 16:9 at ≥2048 px wide, white ground, generous gutters. Nothing smaller than about 10% of the sheet height, because of downsampling.
- **Left 40%:** the logo, large, with clear space.
- **Top right:** colour fields sized by usage. No codes or names.
- **Middle right:** a type specimen.
  - The *actual* headline string at display size in the brand display face.
  - One line in the secondary face.
  - Real fonts rendered via HTML, so the model sees the real letterforms of the words it must write (idea from [23]).
- **Bottom right:** 2–3 unlabelled swatches of brand imagery treatment (grain, crop style, light).
- **Role line:** "Image N is a brand sheet. Take only the logo's shape, the colour relationships and the letterform character. Do not reproduce the sheet, its panels, its layout or any of its words except the quoted strings."
- **Never put** hex values, font names, rules or do/don't text on the sheet.
- **Test protocol:** same briefs × {text-only, split kit, composite} × 3 samples. Metrics: text exactness, logo IoU, palette ΔE, zone adherence, judge score.

---

## Repositories table (checked 2026-09-23 via `gh api`)

| Repo / guide | ★ | Last push | Licence | Adopt | Reject |
|---|---|---|---|---|---|
| OpenAI image prompting guide (2.5) [1] | — | covers 2026-09-08 release | docs | labelled sections, quoted text, image roles, change-only edits, Flare/Sunburst rule | — |
| openai/openai-cookbook (image-gen guide) [4] | 76,137 | 2026-09-23 | MIT | ad-as-brief, "ONLY this text", sketch→render, multi-image indexing | "bokeh" and other cliché cues |
| openai/codex (imagegen skill) [5] | 126,154 | 2026-09-23 | Apache-2.0 | labelled spec lines; no invented slogans; gpt-image-2 always high input fidelity | its "avoid left/right decisions" default for design work |
| openai/plugins (creative-production) [6] | 7,135 | 2026-09-18 | none / proprietary | 25 ad families; headline behind subject; no invented small copy | copying pack text; relying on it for exact content |
| openai/skills (hatch-pet) [7] | 27,582 (deprecated) | 2026-09-08 | Apache per skill | invisible layout guides; QA outside the prompt | — |
| anthropics/skills (canvas-design, frontend-design) [11] | 177,796 | 2026-09-22 | Apache per skill | philosophy first, refine-don't-add, AI-default clusters | 90/10 art bias, thin type, diagram look |
| callirra-ai/gpt-image-2-5-prompt-atlas [15] | 104 | 2026-09-11 | CC BY 4.0 (prompts) | 24 ranked principles, full briefs, tier test, placeholder warning | long craft prompts copied verbatim |
| youart-open-source/awesome-gpt-image-2-5-prompts [16] | 111 | 2026-09-11 | mixed (no grant) | corpus stats, artefact-first, vary one thing | the prompts themselves |
| LiamGvchi/gc-minimal-zine-poster [17] | 7,158 | 2026-08-13 | MIT | field order, variation engine, photo roles, sample residue | zine look as default |
| yanliudesign/mono-color-skill [18] | 3,257 | 2026-09-02 | MIT | manifest, 5-paragraph compiler, originality firewall, collision rules | deterministic sameness for feeds |
| jiemianduan/poster-style-transfer [19] | 47 | 2026-08-07 | MIT | hard/soft/must-replace, fidelity rubric | — |
| kwistzzqq-byte/image2-ads-studio [20] | 48 | 2026-05-06 | Apache-2.0 | vague-label linter, required-field checks | badge, seal and script defaults |
| crawfordxx/xiaoma-durex-copywriter [21] | 577 | 2026-08-08 | NOASSERTION | one-jump rule, 3–5 distinct schemes, subject-type mix | keyword-highlight default |
| dacnay816y62-hub/fantasy-dongfang-jianyuehaibao [22] | 108 | 2026-09-05 | none | full-poster single pass, simplify-and-regenerate, A/B/C | code (no licence) |
| op7418/guizang-yingzao-skill [23] | 454 | 2026-09-03 | none | 3-image contract, scaffold, 2–4 mechanisms, history distance | code (no licence) |
| norahe0304-art/30x-image [24] | 29 | 2026-08-28 | MIT | commit-per-axis, taste dials, anti-slop block, no edit chains | — |
| Leonxlnx/taste-skill [25] | 89,543 | 2026-09-23 | MIT | creativity escalation, slop lists | web-only parts |
| freestylefly/awesome-gpt-image-2 [26] | 33,378 | 2026-09-11 | MIT (cases from X) | conceptual typography template, pitfalls | third-party case texts |
| YouMind-OpenLab/awesome-gpt-image-2 [27] | 9,942 | 2026-09-23 | NOASSERTION (CC-BY per file) | trend and category signals, `{argument}` defaults | copying; fake data in examples |
| EvoLinkAI/awesome-gpt-image-2-API-and-Prompts [28] | 17,237 | 2026-07-18 | CC0 (claimed) | layered-type examples | 8K boilerplate, fake phones and prices |
| ZeroLu/awesome-gpt-image [29] | 2,226 | 2026-09-23 | MIT | dense-copy stress tests | hotlinked third-party images |
| wuyoscar/GPT-Image2-Skill [30] | 5,536 | 2026-09-09 | MIT | reverse-prompt (3–5 anchors first), fixed regions | — |
| ConardLi/garden-skills [31] | 12,594 | 2026-07-12 | MIT | title-safe numbers (≥60%, ≤3 colours, ≤2 families) | stale since July |
| higgsfield-ai/skills [32] | 1,107 | 2026-09-14 | MIT | 11-block thumbnail, manifest, identity lock, frameworks | vivid-gloss default |
| buluslan/gpt-image2-ecommerce [33] | 389 | 2026-09-17 | MIT | style lock, slop-word table (R2) | region stereotypes |
| JimLiu/baoyu-skills [34] | 26,120 | 2026-09-10 | MIT | style × layout × palette dimensions (R2) | edit/anchor chains for carousels |
| AlekseiUL/gpt-image-2-5-agent-kit [35] | 24 | 2026-09-09 | MIT | typed reference order, receipts (R2) | — |
| JuneYaooo/gpt-image2-ppt-skills [36] | 1,306 | 2026-08-22 | Apache-2.0 | corner-tick skeleton (R2) | — |
| pbakaus/impeccable [38] | 70,196 | 2026-09-22 | Apache-2.0 | slop detector rules for the judge (R2) | web-only rules |
| MAYANKSHARMA01010/shorts-factory [44] | 0 | 2026-09-14 | MIT | variation-ledger pattern | — |
| PromptBase (marketplace) [61] | — | live | proprietary | trend signals only | hidden prompts; unusable as rules |

---

## Sources (all accessed 2026-09-23)

1. OpenAI — Image prompting guide (GPT Image 2.5, 2, 1.5): https://developers.openai.com/api/docs/guides/image-prompting
2. OpenAI — Image generation guide (limitations, masks): https://developers.openai.com/api/docs/guides/image-generation
3. OpenAI — Images API reference (`n` 1–10, no seed, 32,000-char prompt, 16 edit images, `input_fidelity`): https://developers.openai.com/api/reference/resources/images
4. OpenAI Cookbook — GPT Image Generation Models Prompting Guide (2026-04-21, updated 2026-08-20): https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide · notebook: https://github.com/openai/openai-cookbook/blob/main/examples/multimodal/image-gen-models-prompting-guide.ipynb
5. openai/codex — bundled imagegen skill, `references/prompting.md`, `sample-prompts.md`: https://github.com/openai/codex/tree/main/codex-rs/skills/src/assets/samples/imagegen
6. openai/plugins — creative-production (image-ad-library pack, exact-content contract, image-building strategy, modes/ads): https://github.com/openai/plugins/tree/main/plugins/creative-production
7. openai/skills — hatch-pet SKILL.md: https://github.com/openai/skills/tree/main/skills/.curated/hatch-pet
8. OpenAI — ChatGPT Images 2.5 System Card (safety only; no capability metrics): https://deploymentsafety.openai.com/chatgpt-images-2-5
9. OpenAI — Introducing ChatGPT Images 2.5 (returned 403; claims taken via [10]): https://openai.com/index/introducing-chatgpt-images-2-5/
10. DataCamp — ChatGPT Images 2.5: Features, Sketch, and API Models (2026-09-09): https://www.datacamp.com/blog/chatgpt-images-2-5
11. anthropics/skills — canvas-design, frontend-design: https://github.com/anthropics/skills
12. OpenAI Developer Community — Introducing GPT Images 2.5 thread: https://community.openai.com/t/introducing-gpt-images-2-5-in-the-api-and-chatgpt/1395897
13. OpenAI Developer Community — GPT-image-generator 2.0 issues and workarounds: https://community.openai.com/t/collection-of-gpt-image-generator-2-0-issues-bugs-and-work-around-tips-check-first-post/1379535
14. OpenAI Developer Community — Image model stuck on the same style: https://community.openai.com/t/image-model-stuck-on-the-same-style/1357399
15. callirra-ai/gpt-image-2-5-prompt-atlas — README, docs/craft.md, docs/how-to-use.md, docs/flare-vs-sunburst.md, cases 01/02/14/25: https://github.com/callirra-ai/gpt-image-2-5-prompt-atlas
16. youart-open-source/awesome-gpt-image-2-5-prompts — README guide and corpus statistics: https://github.com/youart-open-source/awesome-gpt-image-2-5-prompts
17. LiamGvchi/gc-minimal-zine-poster — SKILL.md, references/prompt-compiler.md, variation-engine.md, reference-analysis.md, quality-gate.md, style-system.md: https://github.com/LiamGvchi/gc-minimal-zine-poster
18. yanliudesign/mono-color-skill — SKILL.md, design-system/: https://github.com/yanliudesign/mono-color-skill
19. jiemianduan/poster-style-transfer — SKILL.md, references/: https://github.com/jiemianduan/poster-style-transfer
20. kwistzzqq-byte/image2-ads-studio — README, `packages/ad-image-agent-core/src/deterministic-prompt.ts`, gallery cases: https://github.com/kwistzzqq-byte/image2-ads-studio
21. crawfordxx/xiaoma-durex-copywriter — SKILL.md, references/production.md: https://github.com/crawfordxx/xiaoma-durex-copywriter
22. dacnay816y62-hub/fantasy-dongfang-jianyuehaibao — SKILL.md: https://github.com/dacnay816y62-hub/fantasy-dongfang-jianyuehaibao
23. op7418/guizang-yingzao-skill — SKILL.md, references/image-generation-workflow.md: https://github.com/op7418/guizang-yingzao-skill
24. norahe0304-art/30x-image — references/anti-slop-rules.md, combinatorial-axes.md, SKILL.md: https://github.com/norahe0304-art/30x-image
25. Leonxlnx/taste-skill — skills/imagegen-frontend-web/SKILL.md: https://github.com/Leonxlnx/taste-skill
26. freestylefly/awesome-gpt-image-2 — docs/templates.md, docs/design/gpt-image-2-5/real-cases.md: https://github.com/freestylefly/awesome-gpt-image-2
27. YouMind-OpenLab/awesome-gpt-image-2 — README (17,579 prompts; featured; categories): https://github.com/YouMind-OpenLab/awesome-gpt-image-2
28. EvoLinkAI/awesome-gpt-image-2-API-and-Prompts — cases/ad-creative.md: https://github.com/EvoLinkAI/awesome-gpt-image-2-API-and-Prompts
29. ZeroLu/awesome-gpt-image — README: https://github.com/ZeroLu/awesome-gpt-image
30. wuyoscar/GPT-Image2-Skill — skills/get-prompt-from-image: https://github.com/wuyoscar/GPT-Image2-Skill
31. ConardLi/garden-skills — gpt-image-2 title-safe-poster.md: https://github.com/ConardLi/garden-skills
32. higgsfield-ai/skills — youtube-thumbnail; model-catalog commit 76aa5d4 (2026-09-11): https://github.com/higgsfield-ai/skills
33. buluslan/gpt-image2-ecommerce: https://github.com/buluslan/gpt-image2-ecommerce
34. JimLiu/baoyu-skills: https://github.com/JimLiu/baoyu-skills
35. AlekseiUL/gpt-image-2-5-agent-kit: https://github.com/AlekseiUL/gpt-image-2-5-agent-kit
36. JuneYaooo/gpt-image2-ppt-skills: https://github.com/JuneYaooo/gpt-image2-ppt-skills
37. smixs/visual-skills: https://github.com/smixs/visual-skills
38. pbakaus/impeccable: https://github.com/pbakaus/impeccable
39. wangrunlin/awesome-gpt-image-2-5-prompts: https://github.com/wangrunlin/awesome-gpt-image-2-5-prompts
40. AtlasCloudAI/awesome-gpt-image-2.5-prompts: https://github.com/AtlasCloudAI/awesome-gpt-image-2.5-prompts
41. EvoLinkAI/gpt-image-2.5-for-e-commerce: https://github.com/EvoLinkAI/gpt-image-2.5-for-e-commerce
42. VigoZhao/AI-Visual-Prompt-Cookbook: https://github.com/VigoZhao/AI-Visual-Prompt-Cookbook
43. xiaohuailabs/xiaohu-ip-studio (cognitive anchor → metaphor → self-check): https://github.com/xiaohuailabs/xiaohu-ip-studio
44. MAYANKSHARMA01010/shorts-factory — pipeline/ledgers/variation_ledger.md: https://github.com/MAYANKSHARMA01010/shorts-factory
45. YouMind-OpenLab/ai-image-prompts-skill: https://github.com/YouMind-OpenLab/ai-image-prompts-skill
46. ningzimu/codex-ppt-skill: https://github.com/ningzimu/codex-ppt-skill
47. fal — How to use GPT Image 2.5: https://fal.ai/learn/tools/how-to-use-gpt-image-2-5
48. fal — GPT Image 2 prompting guide: https://fal.ai/learn/tools/prompting-gpt-image-2
49. Oakgen — GPT Image 2 review, 500 generations (2026-04-22; VEN): https://oakgen.ai/blog/gpt-image-2-review-500-generations
50. Atlas Cloud — GPT Image 2.5 text rendering checks: https://www.atlascloud.ai/blog/tips/gpt-image-2.5-text-rendering
51. Atlas Cloud — GPT Image 2.5 product photography (SKU protection list): https://www.atlascloud.ai/blog/tips/gpt-image-2.5-product-photography
52. Masonry — GPT Image 2 guide (single serum-poster test): https://masonry.so/blog/gpt-image-2-guide
53. Vanja Petreski — GPT Image 2.5: Pin Sunburst: https://vanja.io/gpt-image-2-5-sunburst/
54. John Hartnup — AI-generated posters don't have to be horrible (2026-06-07): https://john.hartnup.uk/2026/06/07/ai-event-posters.html
55. Gabos Media — Why AI posters all look the same: https://gabosmedia.substack.com/p/why-ai-posters-all-look-the-same
56. Ken Ashe — AI posters get better when the model stops being the designer (2026-09-19): https://kenashe.ai/blog/2026-09-19-ai-posters-get-better-when-the-model-stops-being-the-designer
57. Venngage — What is AI slop in design (updated 2026-08-12): https://venngage.com/blog/ai-slop-in-design/
58. Artem Novitckii — carousel system (slide-1 anchor): https://novitckii.com/resources/carousel-system/
59. AI Meets Girlboss — visual brand reference sheet (anecdote): https://aimeetsgirlboss.substack.com/p/visual-brand-reference-sheet-ai-prompt
60. Build Fast with AI — ChatGPT Images 2.0 developer breakdown (logo-reproduction anecdotes): https://blog.buildfastwithai.com/chatgpt-images-2-0-gpt-image-2-2026
61. PromptBase — Poster prompts: https://promptbase.com/posters
62. BizGenEval, arXiv 2603.25732: https://arxiv.org/abs/2603.25732 (results: https://arxiv.org/html/2603.25732)
63. PosterIQ, arXiv 2603.24078: https://arxiv.org/abs/2603.24078
64. TECCI, arXiv 2606.01213 (via review): https://pith.science/paper/2606.01213
65. TextFake, arXiv 2606.01050 (Entity OCR Hit Rate, Table 5): https://arxiv.org/html/2606.01050v1
66. Phillips & McQuarrie (2004), Beyond Visual Metaphor, *Marketing Theory*: https://journals.sagepub.com/doi/10.1177/1470593104044089
67. "Can your brand pass the swap-your-logo test?" (LinkedIn, 2014): https://www.linkedin.com/pulse/20140424202258-211880237-can-your-brand-pass-the-swap-your-logo-test
68. Distinctive Bat — Distinctive assets versus logos: https://www.distinctivebat.com/blog/distinctive-assets-versus-logos-who-wins/
69. Mark Pollard on Get/To/By: https://www.linkedin.com/posts/markpollardstrategist_most-uses-of-gettoby-are-useless-activity-7043928445575184385-V0uj
70. Creative Agency Book — power of three in concept presentations: https://www.creativeagencybook.com/blog/successful-concept-presentations-power-of-three

**Local:** companion notes in the scratchpad `design-research/` folder (R1 `R1-skills-higgsfield-local.md`, R2 `R2-community-skills-tools.md`, R3 `R3-gpt-image-design-prompting.md`, R4 `R4-design-craft.md`, R5 `R5-formats-specs-playbooks.md`, R7 `R7-culture-legal-access.md`); skill files read: `~/.claude/skills/codex-design/references/ai-visuals.md` and `genres.md`.
